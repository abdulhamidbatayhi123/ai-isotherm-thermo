"""Measured digitisation error (PREREG_P3A.md section 3.5).

Mg-SU-102 (Nat. Commun. 2025, 10.1038/s41467-025-59551-2) publishes its Fig. 4a isotherms
both as a vector figure and as numeric source data (MOESM3, sheet Figure4). We digitise
the figure without looking at the numbers, then compare:

  1. vector extraction (markers from the PDF drawing commands, axes from the tick labels
     snapped to tick marks, series assigned to temperatures by the legend's text colour);
  2. raster digitisation of the same panel rendered at 150, 300 and 600 dpi (markers found
     by colour segmentation after a morphological opening that removes the interpolation
     lines; axes from tick marks detected in the image and the tick values read by eye).

Pairing for the comparison: each digitised point is matched to the nearest numeric point of
the same temperature (in axis-normalised units); unmatched points count against recall.

Inputs (local, not redistributed): data/raw/primary/mgsu102_2025_natcommun/.
Output: logs/digitisation_error.json and a printed summary.
"""
import json
import sys
from pathlib import Path

import fitz
import numpy as np
import pandas as pd
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from p3a import digitise  # noqa: E402

RAW = ROOT / "data/raw/primary/mgsu102_2025_natcommun"
PDF = RAW / "s41467-025-59551-2.pdf"
XLSX = RAW / "41467_2025_59551_MOESM3_ESM.xlsx"
TEMPS_C = [15, 20, 25, 30, 35, 40, 45, 50, 55]

# Panel A geometry on page 4 (PDF points), read from the page once; see the log.
PAGE = 3
PLOT = fitz.Rect(166.0, 55.0, 305.0, 205.0)  # marker search area (inside the frame)
XLAB = fitz.Rect(160.0, 208.5, 295.0, 219.0)
XTICK = fitz.Rect(160.0, 205.0, 310.0, 208.0)
YLAB = fitz.Rect(148.0, 50.0, 164.5, 212.0)
YTICK = fitz.Rect(160.0, 50.0, 166.0, 210.0)
LEGEND = fitz.Rect(300.0, 58.0, 320.0, 132.0)
X_SPAN, Y_SPAN = 16.0, 0.4  # axis spans (mbar, g/g) used to normalise errors


def numeric_truth():
    """Numeric isotherms: {T_C: array of (p_mbar, q_g_per_g)}; p from p/p0 x p_sat(T)."""
    import torch

    from p3a import water

    s = pd.read_excel(XLSX, sheet_name="Figure4", header=None)
    out = {}
    for i, tc in enumerate(TEMPS_C):
        rh = pd.to_numeric(s.iloc[3:, 2 * i], errors="coerce").to_numpy()
        q = pd.to_numeric(s.iloc[3:, 2 * i + 1], errors="coerce").to_numpy()
        ok = np.isfinite(rh) & np.isfinite(q)
        psat = water.p_sat(torch.tensor([tc + 273.15])).item()  # Pa
        out[tc] = np.column_stack([rh[ok] * psat / 100.0, q[ok]])  # mbar = Pa / 100
    return out


def legend_colours(page):
    cols = {}
    for b in page.get_text("dict", clip=LEGEND)["blocks"]:
        for line in b.get("lines", []):
            for sp in line["spans"]:
                t = sp["text"].strip()
                if t.isdigit() and int(t) in TEMPS_C:
                    c = sp["color"]
                    cols[int(t)] = np.array([(c >> 16) & 255, (c >> 8) & 255, c & 255]) / 255.0
    return cols


def assign_series(series_colours, legend):
    """Map each legend temperature to the nearest series colour (blind to the numbers)."""
    out = {}
    for tc, lc in legend.items():
        keys = list(series_colours)
        d = [np.linalg.norm(np.array(k) - lc) for k in keys]
        out[tc] = keys[int(np.argmin(d))]
    return out


# a digitised point is matched only within MATCH_TOL (axis-normalised units, about one
# marker half-size: 1.5 pt of a 137 pt wide panel); farther points are false detections
MATCH_TOL = 0.012


def compare(dig, truth):
    """One-to-one nearest pairing in normalised units within MATCH_TOL.
    Returns (dx errors, dy errors, recall, number of false detections)."""
    dn = dig / [X_SPAN, Y_SPAN]
    tn = truth / [X_SPAN, Y_SPAN]
    used, ex, ey, false = set(), [], [], 0
    for p in dn:
        d = np.hypot(*(tn - p).T)
        order = np.argsort(d)
        j = next((int(k) for k in order if int(k) not in used), None)
        if j is not None and d[j] <= MATCH_TOL:
            used.add(j)
            ex.append((p[0] - tn[j][0]) * X_SPAN)
            ey.append((p[1] - tn[j][1]) * Y_SPAN)
        elif d[order[0]] > MATCH_TOL:
            false += 1
    return np.array(ex), np.array(ey), len(used) / len(truth), false


def summarise(errs_x, errs_y, recalls):
    ex, ey = np.concatenate(errs_x), np.concatenate(errs_y)
    return {
        "n_matched": int(ex.size),
        "recall_mean": float(np.mean(recalls)),
        "recall_min": float(np.min(recalls)),
        "rms_dq_g_per_g": float(np.sqrt(np.mean(ey**2))),
        "max_abs_dq_g_per_g": float(np.max(np.abs(ey))),
        "rms_dq_frac_of_axis": float(np.sqrt(np.mean(ey**2)) / Y_SPAN),
        "rms_dp_mbar": float(np.sqrt(np.mean(ex**2))),
        "max_abs_dp_mbar": float(np.max(np.abs(ex))),
        "rms_dp_frac_of_axis": float(np.sqrt(np.mean(ex**2)) / X_SPAN),
    }


def vector_run(page, truth):
    xa = digitise.vector_axis(page, XLAB, "x", tick_clip=XTICK)
    ya = digitise.vector_axis(page, YLAB, "y", tick_clip=YTICK)
    series = digitise.vector_markers(page, PLOT)
    series = {k: v for k, v in series.items() if len(v) >= 5}
    mapping = assign_series(series, legend_colours(page))
    ex, ey, rec, per_T = [], [], [], {}
    for tc in TEMPS_C:
        pts = series[mapping[tc]]
        dig = np.column_stack([xa(pts[:, 0]), ya(pts[:, 1])])
        a, b, r, f = compare(dig, truth[tc])
        ex.append(a), ey.append(b), rec.append(r)
        per_T[tc] = {"n_digitised": int(len(dig)), "n_truth": int(len(truth[tc])), "recall": r, "false": f}
    return {"axis_x": vars(xa), "axis_y": vars(ya), "per_T": per_T, **summarise(ex, ey, rec)}, xa, ya, mapping


def raster_run(page, truth, dpi, mapping, xa_vec, ya_vec, seed=0):
    """Raster pipeline on the panel rendered at dpi, using only what a human digitiser has:
    the image, the series colours and marker styles seen in it (filled for 15 to 35 C,
    hollow for 40 to 55 C), and the tick values printed on the axes. Tick positions are
    'read by eye' as the true positions plus +-2 px noise and then snapped to the tick marks
    in the image (`digitise.snap_ticks`). The vector maps give the approximate tick and
    frame positions only; no point position comes from them."""
    rng = np.random.default_rng(seed)
    clip = fitz.Rect(160.0, 50.0, 320.0, 212.0)
    img = digitise.load_page_image(page, clip=clip, dpi=dpi)
    scale = dpi / 72.0
    xticks_v = np.arange(0, 15, 2.0)
    yticks_v = np.arange(0, 0.41, 0.1)
    x_pt = (xticks_v - xa_vec.a) / xa_vec.b
    y_pt = (yticks_v - ya_vec.a) / ya_vec.b
    x_eye = (x_pt - clip.x0) * scale + rng.uniform(-2, 2, x_pt.size)
    y_eye = (y_pt - clip.y0) * scale + rng.uniform(-2, 2, y_pt.size)
    frow = digitise.find_frame_line(img, (205.63 - clip.y0) * scale + rng.integers(-2, 3), "x")
    fcol = digitise.find_frame_line(img, (165.22 - clip.x0) * scale + rng.integers(-2, 3), "y")
    xs = digitise.snap_ticks(img, x_eye, "x", frow)
    ys = digitise.snap_ticks(img, y_eye, "y", fcol)
    xa = digitise.fit_axis(xs, xticks_v)
    ya = digitise.fit_axis(ys, yticks_v)
    radius = 1.4 * scale  # markers are about 2.5 to 3.4 pt across
    region = (int((PLOT.y0 - clip.y0) * scale), frow - 1, fcol + 2, int((PLOT.x1 - clip.x0) * scale))
    ex, ey, rec, per_T = [], [], [], {}
    for tc in TEMPS_C:
        mode = "filled" if tc <= 35 else "ring"
        cents = digitise.raster_markers(img, mapping[tc], radius, mode=mode, region=region,
                                        min_fill=0.5 if mode == "filled" else 0.45)
        if len(cents) == 0:
            rec.append(0.0)
            per_T[tc] = {"n_digitised": 0, "recall": 0.0}
            continue
        dig = np.column_stack([xa(cents[:, 1]), ya(cents[:, 0])])
        a, b, r, f = compare(dig, truth[tc])
        ex.append(a), ey.append(b), rec.append(r)
        per_T[tc] = {"n_digitised": int(len(dig)), "recall": r, "false": f, "mode": mode}
    return {"dpi": dpi, "axis_x_residual_px": xa.residual, "axis_y_residual_px": ya.residual,
            "n_xticks": xa.n_ticks, "n_yticks": ya.n_ticks, "per_T": per_T, **summarise(ex, ey, rec)}


def main():
    truth = numeric_truth()
    page = fitz.open(PDF)[PAGE]
    vec, xa, ya, mapping = vector_run(page, truth)
    result = {"source": "Mg-SU-102 Fig. 4a vs MOESM3 sheet Figure4", "vector": vec,
              "raster": [raster_run(page, truth, d, mapping, xa, ya) for d in (150, 300, 600)]}
    out = ROOT / "logs/digitisation_error.json"
    out.write_text(json.dumps(result, indent=2, default=float))
    v = result["vector"]
    print(f"vector: n={v['n_matched']} recall={v['recall_mean']:.3f} (min {v['recall_min']:.3f}) "
          f"rms dq={v['rms_dq_g_per_g']:.5f} g/g (max {v['max_abs_dq_g_per_g']:.5f}) "
          f"rms dp={v['rms_dp_mbar']:.4f} mbar (max {v['max_abs_dp_mbar']:.4f})")
    for r in result["raster"]:
        print(f"raster {r['dpi']} dpi: n={r['n_matched']} recall={r['recall_mean']:.3f} (min {r['recall_min']:.3f}) "
              f"rms dq={r['rms_dq_g_per_g']:.5f} g/g (max {r['max_abs_dq_g_per_g']:.5f}) "
              f"rms dp={r['rms_dp_mbar']:.4f} mbar (max {r['max_abs_dp_mbar']:.4f}) "
              f"ticks x/y={r['n_xticks']}/{r['n_yticks']}")


if __name__ == "__main__":
    main()
