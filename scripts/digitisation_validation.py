"""Digitisation error on real figures with numeric source data (extends PREREG_P3A.md 3.5).

scripts/digitisation_error.py measures the error on one figure (Mg-SU-102 Fig. 4a). This
script adds published figures whose authors also deposited the plotted numbers, and
digitises them with the unmodified library (src/p3a/digitise.py) and the same per-source
procedure as scripts/digitise_sources.py:

  raster: `raster_source` steps (frame line, tick snapping, template from one marker,
          `raster_markers` with the default gates: fill >= 0.6, colour tol 0.18, white-core
          check, open-marker veto). No legend markers exist in these panels (the legends are
          coloured text), so each template is cut from an isolated data marker, as for the
          Tan 2021 figures in digitise_sources.py.
  vector: `legend_mapped` steps (axes from tick labels snapped to tick marks, series colour
          from the legend marker on the label's line, markers by colour, size and shape).

Per-figure inputs (tick, frame and template pixel positions) were read by eye from grid
images made with scripts/raster_inspect.py; they are listed below and in the output. The
numeric truth is opened only for the comparison, after detection.

Figures (all Nat. Commun., CC BY; files under data/raw/validation/, not redistributed):
  hkust1_si21a  HKUST-1 F3@HK_30, 10.1038/s41467-024-53853-7, SI Fig. 21a (298, 318 K), raster
  hkust1_fig1a  same paper, main Fig. 1a (pristine HKUST-1, F3@HK_30, 298 K), raster
  emm8_fig3a    EMM-8, 10.1038/s41467-021-27883-4, Fig. 3a (25, 40, 50 C), vector

Matching (as digitisation_error.py): each detection is paired with the nearest unused truth
point of its series in axis-normalised coordinates (value / axis span), within MATCH_TOL.
Here MATCH_TOL is one marker radius, converted to normalised units with the figure's
geometric-mean pixels (or points) per axis span; it is reported per figure.

Visible-point recall (raster only). Some truth points cannot be seen in a figure: repeated
measurements at one pressure plot on top of each other, and markers of one series are
covered by another's. A truth point is called visible when (1) it is the first of the
truth points of its series that lie within the detector's own peak-merging distance
(0.9 x marker radius, in pixels) of each other (a cluster of coincident points counts once,
and is matched if any member is), and (2) at its pixel position (truth mapped through the
fitted axis) the template footprint is at least 60 % covered by the series colour (the
detector's own min_fill gate, colour tolerance 0.18). Recall over visible points is the
fraction of such clusters matched.

Usage: python scripts/digitisation_validation.py [requires the validation PDFs and the
EMM-8 source-data .xls extracted from its zip; pass the extracted folder with --emm8-dir and
a folder holding xlrd with --pylib if xlrd is not installed].
Outputs: logs/digitisation_validation.json, logs/digitisation_validation/<figure>.png.
"""
import argparse
import json
import sys
from pathlib import Path

import fitz
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from p3a import digitise  # noqa: E402
from digitise_sources import (legend_marker_colour, markers_outside,  # noqa: E402
                              refine_legend_marker)

VAL = ROOT / "data/raw/validation"
OUT_JSON = ROOT / "logs/digitisation_validation.json"
OUT_DIR = ROOT / "logs/digitisation_validation"

# ----------------------------------------------------------------- per-figure inputs

HK = VAL / "hkust1_f3_ncomms2024"
RASTER = {
    "hkust1_si21a": dict(
        pdf=HK / "41467_2024_53853_MOESM1_ESM.pdf", page=27, xref=125,
        doi="10.1038/s41467-024-53853-7", figure="Supplementary Fig. 21a, SI page 27",
        # x-axis line row 395, y-axis line column 91, frame top row 58, right column 544
        frame_row=395, frame_col=91, frame_top=58, frame_right=544,
        # major ticks (labelled) read from 3x zooms of the 1229 x 499 px image
        x_ticks=[(104, 0.0), (189, 0.2), (275, 0.4), (360, 0.6), (445, 0.8), (531, 1.0)],
        y_ticks=[(381, 0.0), (304, 0.1), (227, 0.2), (151, 0.3), (74, 0.4)],
        # (series label, isolated data marker (row, col)) -- black 298 K, red 318 K
        series=[("298K", (176, 258)), ("318K", (205, 291))],
        truth=(HK / "41467_2024_53853_MOESM5_ESM.xlsx", "Supplementary Fig. 21. a",
               {"298K": (0, 1), "318K": (2, 3)}),
        x_span=1.0, y_span=0.4),
    "hkust1_fig1a": dict(
        pdf=HK / "s41467-024-53853-7.pdf", page=3, xref=71,
        doi="10.1038/s41467-024-53853-7", figure="main Fig. 1a, page 3",
        frame_row=442, frame_col=47, frame_top=10, frame_right=581,
        # y ticks 0.0 and 0.7 coincide with the frame lines and are not used
        x_ticks=[(72, 0.0), (169, 0.2), (267, 0.4), (364, 0.6), (461, 0.8), (558, 1.0)],
        y_ticks=[(380, 0.1), (318, 0.2), (257, 0.3), (195, 0.4), (134, 0.5), (72, 0.6)],
        # black = pristine HKUST-1, red = F3@HK_30 (identified from the curve shapes in the
        # figure: the red curve ends at 0.39 g/g as in SI Fig. 21a's 298 K curve)
        series=[("Pristine-HK", (39, 512)), ("F3@HK_30", (271, 322))],
        truth=(HK / "41467_2024_53853_MOESM5_ESM.xlsx", "Figure 1a",
               {"Pristine-HK": (0, 1), "F3@HK_30": (2, 3)}),
        x_span=1.0, y_span=0.7),
}
# raster_source defaults used by every confirmatory raster source
TPL_HALF, OPEN_PX, COLOUR_TOL, TICK_SEARCH = 14, 2, 0.18, 8

VECTOR = {
    "emm8_fig3a": dict(
        pdf=VAL / "emm8_ncomms2021/s41467-021-27883-4.pdf", page=5,
        doi="10.1038/s41467-021-27883-4", figure="main Fig. 3a, page 5",
        # clips in PDF points, read from the page's text spans and drawing items
        xlab=fitz.Rect(86, 230, 295, 240), xtick=fitz.Rect(86, 222, 300, 232),
        ylab=fitz.Rect(69, 50, 86, 225), ytick=fitz.Rect(84, 50, 95, 228),
        plot=fitz.Rect(87, 50, 298, 226), legend=fitz.Rect(95, 57, 135, 90),
        label_clip=fitz.Rect(112, 57, 135, 90),
        labels=((" 25", "25C"), (" 40", "40C"), (" 50", "50C")),
        # data markers are 4.0 x 4.1 pt discs (legend markers 3.8 x 3.9 pt, highlights 2.2 pt)
        size_range=(3.95, 4.3), shape_tol=0.45,
        truth=("Source Data/Manuscript-Figure3.xls", "Figure3a ",
               {"25C": (0, 1), "40C": (2, 3), "50C": (4, 5)}, 2),
        x_span=1.0, y_span=0.4),
}

BNN = VAL / "bnn1_ncomms2026"
for _p, _mat, _y0, _y1, _ylab, _leg in (
        ("a", "bnn-1-Co", 55.0, 146.3, fitz.Rect(76, 55, 85.5, 149.8), fitz.Rect(118, 94, 186, 122)),
        ("b", "bnn-1-Ni", 165.0, 257.5, fitz.Rect(76, 165, 85.5, 261), fitz.Rect(118, 196, 188, 226))):
    _xl = 148.5 if _p == "a" else 259.5
    VECTOR[f"bnn1_fig3{_p}"] = dict(
        pdf=BNN / "s41467-026-76301-0.pdf", page=4, doi="10.1038/s41467-026-76301-0",
        figure=f"main Fig. 3{_p}, page 4 ({_mat})",
        xlab=fitz.Rect(85, _xl, 212, _xl + 7), xtick=fitz.Rect(85, _y1 - 0.5, 212, _y1 + 2.5),
        ylab=_ylab, ytick=fitz.Rect(85.5, _y0, 88.0, _y1 + 1),
        plot=fitz.Rect(87.8, _y0, 215, _y1 + 0.5), legend=_leg,
        label_clip=fitz.Rect(_leg.x0 + 18, _leg.y0, _leg.x1, _leg.y1),
        labels=(("Adsorption at 27", "27C"), ("Adsorption at 60", "60C")),
        # filled adsorption discs 1.9 x 1.8 pt; desorption discs are white-filled
        size_range=(1.7, 2.05), shape_tol=0.45,
        truth=(BNN / "41467_2026_76301_MOESM3_ESM.xlsx", f"Fig 3{_p}", {"27C": (0, 1), "60C": (3, 4)}, 2),
        x_span=100.0, y_span=30.0)


# ----------------------------------------------------------------------- truth tables


def read_truth(path, sheet, cols, first_row):
    s = pd.read_excel(path, sheet_name=sheet, header=None)
    out = {}
    for lab, (cx, cy) in cols.items():
        x = pd.to_numeric(s.iloc[first_row:, cx], errors="coerce").to_numpy()
        y = pd.to_numeric(s.iloc[first_row:, cy], errors="coerce").to_numpy()
        ok = np.isfinite(x) & np.isfinite(y)
        out[lab] = np.column_stack([x[ok], y[ok]])
    return out


# ------------------------------------------------------------------------- matching


def compare(dig, truth, xs, ys, tol):
    """One-to-one nearest pairing in normalised units within tol (digitisation_error.compare).
    Returns matched (det index, truth index) pairs and the number of false detections."""
    dn, tn = dig / [xs, ys], truth / [xs, ys]
    used, pairs, false = set(), [], 0
    for i, p in enumerate(dn):
        d = np.hypot(*(tn - p).T)
        order = np.argsort(d)
        j = next((int(k) for k in order if int(k) not in used), None)
        if j is not None and d[j] <= tol:
            used.add(j)
            pairs.append((i, j))
        elif d[order[0]] > tol:
            false += 1
    return pairs, false


def metrics(dig, truth, xs, ys, tol):
    pairs, false = compare(dig, truth, xs, ys, tol)
    r = {"n_truth": int(len(truth)), "n_detected": int(len(dig)), "n_matched": len(pairs),
         "recall": len(pairs) / len(truth), "false_detections": int(false),
         "unmatched_detections": int(len(dig) - len(pairs))}
    if pairs:
        ex = np.array([dig[i, 0] - truth[j, 0] for i, j in pairs])
        ey = np.array([dig[i, 1] - truth[j, 1] for i, j in pairs])
        for ax, e, span in (("x", ex, xs), ("y", ey, ys)):
            r[f"rms_{ax}"] = float(np.sqrt(np.mean(e**2)))
            r[f"max_abs_{ax}"] = float(np.max(np.abs(e)))
            r[f"mean_signed_{ax}"] = float(np.mean(e))
            r[f"rms_{ax}_pct_span"] = 100 * r[f"rms_{ax}"] / span
            r[f"max_abs_{ax}_pct_span"] = 100 * r[f"max_abs_{ax}"] / span
            r[f"mean_signed_{ax}_pct_span"] = 100 * r[f"mean_signed_{ax}"] / span
    return r, pairs


def pooled(per, figs_dig, figs_truth, xs, ys, pairs_by):
    ex, ey = [], []
    for lab, pairs in pairs_by.items():
        d, t = figs_dig[lab], figs_truth[lab]
        ex += [d[i, 0] - t[j, 0] for i, j in pairs]
        ey += [d[i, 1] - t[j, 1] for i, j in pairs]
    ex, ey = np.array(ex), np.array(ey)
    n_t = sum(v["n_truth"] for v in per.values())
    out = {"n_truth": n_t, "n_matched": int(ex.size), "recall": ex.size / n_t,
           "false_detections": int(sum(v["false_detections"] for v in per.values()))}
    if ex.size:
        out.update({"rms_y_pct_span": float(100 * np.sqrt(np.mean(ey**2)) / ys),
                    "max_abs_y_pct_span": float(100 * np.max(np.abs(ey)) / ys),
                    "rms_x_pct_span": float(100 * np.sqrt(np.mean(ex**2)) / xs),
                    "max_abs_x_pct_span": float(100 * np.max(np.abs(ex)) / xs)})
    return out


# --------------------------------------------------------------------------- raster


def raster_run(key, cfg):
    """Body of digitise_sources.raster_source, without writing into data/."""
    page = fitz.open(cfg["pdf"])[cfg["page"] - 1]
    img = digitise.load_page_image(page, xref=cfg["xref"])
    frow = digitise.find_frame_line(img, cfg["frame_row"], "x")
    fcol = digitise.find_frame_line(img, cfg["frame_col"], "y")
    xs_px = digitise.snap_ticks(img, [c for c, _ in cfg["x_ticks"]], "x", frow, search=TICK_SEARCH)
    ys_px = digitise.snap_ticks(img, [c for c, _ in cfg["y_ticks"]], "y", fcol, search=TICK_SEARCH)
    xa = digitise.fit_axis(xs_px, [v for _, v in cfg["x_ticks"]])
    ya = digitise.fit_axis(ys_px, [v for _, v in cfg["y_ticks"]])
    region = (cfg["frame_top"] + 2, frow - 1, fcol + 2, cfg["frame_right"] - 2)
    dig, info = {}, {}
    for lab, (lr, lc) in cfg["series"]:
        lr, lc = refine_legend_marker(img, lr, lc)
        col = np.median(img[lr - 1: lr + 2, lc - 1: lc + 2].reshape(-1, 3), axis=0)
        tpl = digitise.marker_template(img, col, (lr - TPL_HALF, lr + TPL_HALF + 1, lc - TPL_HALF,
                                                  lc + TPL_HALF + 1), tol=COLOUR_TOL, open_px=OPEN_PX)
        cents = digitise.raster_markers(img, col, 0.5 * min(tpl.shape), tol=COLOUR_TOL,
                                        region=region, exclude=[(0, 0, 0, 0)], template=tpl)
        dig[lab] = np.column_stack([xa(cents[:, 1]), ya(cents[:, 0])]) if len(cents) else np.zeros((0, 2))
        info[lab] = {"colour": [round(float(v), 3) for v in col], "template_px": list(tpl.shape),
                     "template_centre_px": [int(lr), int(lc)], "tpl": tpl, "cents": cents}
    return img, xa, ya, dig, info, region, (frow, fcol, xs_px, ys_px)


def visible_clusters(img, truth, xa, ya, col, tpl):
    """Indices of truth clusters (lists) that are visible by the rule in the docstring."""
    from scipy.signal import fftconvolve

    r = 0.5 * float(min(tpl.shape))
    u = (truth[:, 0] - xa.a) / xa.b
    v = (truth[:, 1] - ya.a) / ya.b
    clusters, assigned = [], np.full(len(truth), -1)
    for i in range(len(truth)):
        if assigned[i] >= 0:
            continue
        near = [j for j in range(len(truth)) if assigned[j] < 0 and np.hypot(u[j] - u[i], v[j] - v[i]) <= 0.9 * r]
        assigned[near] = len(clusters)
        clusters.append(near)
    mask = (np.linalg.norm(img - np.asarray(col, float), axis=-1) < COLOUR_TOL).astype(float)
    ker = np.asarray(tpl, float)
    fill = fftconvolve(mask, ker[::-1, ::-1] / ker.sum(), mode="same")
    h, w = ker.shape
    vis = []
    for cl in clusters:
        i = cl[0]
        # index convention of raster_markers: an even footprint's centre is half a pixel
        # before the output index
        rr = int(round(v[i] + 0.5 * (h % 2 == 0)))
        cc = int(round(u[i] + 0.5 * (w % 2 == 0)))
        f = fill[rr, cc] if 0 <= rr < fill.shape[0] and 0 <= cc < fill.shape[1] else 0.0
        vis.append((cl, float(f)))
    return vis


def raster_overlay(img, xa, ya, dig, truth, region, path):
    """Plot area (search region + 20 px) enlarged 3x: truth = green circles, detections =
    magenta crosses, search region = blue box."""
    from PIL import Image, ImageDraw

    r0, r1, c0, c1 = region
    m, k = 20, 3
    R0, C0 = max(0, r0 - m), max(0, c0 - m)
    crop = img[R0: r1 + m, C0: c1 + m]
    im = Image.fromarray((crop * 255).round().astype(np.uint8))
    im = im.resize((im.width * k, im.height * k), Image.NEAREST)
    dr = ImageDraw.Draw(im)

    def px(x, y):
        return ((x - xa.a) / xa.b - C0 + 0.5) * k, ((y - ya.a) / ya.b - R0 + 0.5) * k

    for lab in truth:
        for x, y in truth[lab]:
            u, v = px(x, y)
            dr.ellipse((u - 6, v - 6, u + 6, v + 6), outline=(0, 200, 0), width=2)
        for x, y in dig[lab]:
            u, v = px(x, y)
            dr.line((u - 8, v, u + 8, v), fill=(255, 0, 255), width=2)
            dr.line((u, v - 8, u, v + 8), fill=(255, 0, 255), width=2)
    dr.rectangle(((c0 - C0) * k, (r0 - R0) * k, (c1 - C0) * k, (r1 - R0) * k), outline=(0, 160, 255))
    im.save(path)


def raster_figure(key, cfg):
    img, xa, ya, dig, info, region, (frow, fcol, xs_px, ys_px) = raster_run(key, cfg)
    path, sheet, cols = cfg["truth"]
    truth = read_truth(path, sheet, cols, 4)
    xs, ys = cfg["x_span"], cfg["y_span"]
    px_x, px_y = abs(xs / xa.b), abs(ys / ya.b)  # pixels per axis span
    per, pairs_by = {}, {}
    for lab in truth:
        tpl = info[lab]["tpl"]
        r_px = 0.5 * float(min(tpl.shape))
        tol = r_px / np.sqrt(px_x * px_y)
        m, pairs = metrics(dig[lab], truth[lab], xs, ys, tol)
        matched_truth = {j for _, j in pairs}
        vis = visible_clusters(img, truth[lab], xa, ya, info[lab]["colour"], tpl)
        vis_ok = [cl for cl, f in vis if f >= 0.6]
        m.update({"match_tol_normalised": float(tol), "marker_radius_px": r_px,
                  "n_truth_clusters": len(vis), "n_visible": len(vis_ok),
                  "n_visible_matched": int(sum(any(j in matched_truth for j in cl) for cl in vis_ok)),
                  "colour": info[lab]["colour"], "template_px": info[lab]["template_px"],
                  "template_centre_px": info[lab]["template_centre_px"]})
        m["recall_visible"] = m["n_visible_matched"] / m["n_visible"] if vis_ok else None
        per[lab], pairs_by[lab] = m, pairs
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raster_overlay(img, xa, ya, dig, truth, region, OUT_DIR / f"{key}.png")
    return {"method": "raster (digitise_sources.raster_source steps; template from an isolated data marker)",
            "doi": cfg["doi"], "figure": cfg["figure"], "image_px": list(img.shape[:2]),
            "xref": cfg["xref"], "x_ticks": cfg["x_ticks"], "y_ticks": cfg["y_ticks"],
            "snapped_x_px": xs_px.tolist(), "snapped_y_px": ys_px.tolist(),
            "frame_row": int(frow), "frame_col": int(fcol), "search_region": list(region),
            "axis_x": vars(xa), "axis_y": vars(ya),
            "axis_x_residual_pct_tick_span": 100 * xa.residual / abs(xs_px[-1] - xs_px[0]),
            "axis_y_residual_pct_tick_span": 100 * ya.residual / abs(ys_px[-1] - ys_px[0]),
            "x_span": xs, "y_span": ys, "series": per,
            "pooled": pooled(per, dig, truth, xs, ys, pairs_by),
            "overlay": str((OUT_DIR / f"{key}.png").relative_to(ROOT)).replace("\\", "/")}


# --------------------------------------------------------------------------- vector


def vector_figure(key, cfg, emm8_dir):
    page = fitz.open(cfg["pdf"])[cfg["page"] - 1]
    xa = digitise.vector_axis(page, cfg["xlab"], "x", tick_clip=cfg["xtick"])
    ya = digitise.vector_axis(page, cfg["ylab"], "y", tick_clip=cfg["ytick"])
    colour_lab = {}
    for txt, lab in cfg["labels"]:
        colour_lab[legend_marker_colour(page, txt, cfg["label_clip"], cfg["legend"])] = lab
    if len(colour_lab) != len(cfg["labels"]):
        raise ValueError("two legend labels mapped to one colour")
    dig, pts_pt = {}, {}
    for c, lab in colour_lab.items():
        m = markers_outside(page, cfg["plot"], cfg["legend"], c, cfg["size_range"], cfg["shape_tol"])
        pts_pt[lab] = m
        dig[lab] = np.column_stack([xa(m[:, 0]), ya(m[:, 1])]) if len(m) else np.zeros((0, 2))
    rel, sheet, cols, first = cfg["truth"]
    path = rel if Path(rel).is_absolute() else Path(emm8_dir) / rel
    truth = read_truth(path, sheet, cols, first)
    xs, ys = cfg["x_span"], cfg["y_span"]
    pt_x, pt_y = abs(xs / xa.b), abs(ys / ya.b)
    r_pt = 0.5 * float(np.mean(cfg["size_range"]))
    tol = r_pt / np.sqrt(pt_x * pt_y)
    per, pairs_by = {}, {}
    for lab in truth:
        m, pairs = metrics(dig[lab], truth[lab], xs, ys, tol)
        m["match_tol_normalised"] = float(tol)
        per[lab], pairs_by[lab] = m, pairs
    # overlay: page render with truth (green circles) and detections (magenta crosses)
    from PIL import Image, ImageDraw

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    clip = fitz.Rect(cfg["plot"].x0 - 25, cfg["plot"].y0 - 5, cfg["plot"].x1 + 5, cfg["plot"].y1 + 20)
    dpi = 300 if clip.width > 180 else 600
    pix = page.get_pixmap(dpi=dpi, clip=clip)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    dr = ImageDraw.Draw(im)
    s = dpi / 72.0
    for lab in truth:
        for x, y in truth[lab]:
            u, v = ((x - xa.a) / xa.b - clip.x0) * s, ((y - ya.a) / ya.b - clip.y0) * s
            dr.ellipse((u - 5, v - 5, u + 5, v + 5), outline=(0, 190, 0), width=2)
        for x, y in pts_pt[lab]:
            u, v = (x - clip.x0) * s, (y - clip.y0) * s
            dr.line((u - 7, v, u + 7, v), fill=(255, 0, 255), width=2)
            dr.line((u, v - 7, u, v + 7), fill=(255, 0, 255), width=2)
    im.save(OUT_DIR / f"{key}.png")
    return {"method": "vector (digitise_sources.legend_mapped steps)", "doi": cfg["doi"],
            "figure": cfg["figure"], "axis_x": vars(xa), "axis_y": vars(ya),
            "legend_colours": {lab: list(c) for c, lab in colour_lab.items()},
            "marker_size_range_pt": list(cfg["size_range"]), "marker_shape_tol_pt": cfg["shape_tol"],
            "clips_pt": {k: list(cfg[k]) for k in ("xlab", "xtick", "ylab", "ytick", "plot", "legend", "label_clip")},
            "x_span": xs, "y_span": ys, "series": per,
            "pooled": pooled(per, dig, truth, xs, ys, pairs_by),
            "overlay": str((OUT_DIR / f"{key}.png").relative_to(ROOT)).replace("\\", "/")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emm8-dir", required=True, help="folder with the extracted EMM-8 MOESM3 zip")
    ap.add_argument("--pylib", default=None, help="extra folder on sys.path (xlrd for .xls)")
    ap.add_argument("only", nargs="*")
    a = ap.parse_args()
    if a.pylib:
        sys.path.insert(0, a.pylib)
    res = {"note": "digitisation error on real figures with numeric source data; see the "
                   "docstring of scripts/digitisation_validation.py for the matching and "
                   "visibility rules", "figures": {}}
    for key, cfg in RASTER.items():
        if not a.only or key in a.only:
            res["figures"][key] = raster_figure(key, cfg)
    for key, cfg in VECTOR.items():
        if not a.only or key in a.only:
            res["figures"][key] = vector_figure(key, cfg, a.emm8_dir)
    OUT_JSON.write_text(json.dumps(res, indent=2, default=float))
    for key, f in res["figures"].items():
        print(key, "axis residuals:", round(f["axis_x"]["residual"], 4), round(f["axis_y"]["residual"], 4))
        for lab, m in f["series"].items():
            print(f"  {lab:12s} n={m['n_truth']:3d} det={m['n_detected']:3d} rec={m['recall']:.3f} "
                  f"vis={m.get('n_visible_matched', '-')}/{m.get('n_visible', '-')} false={m['false_detections']} "
                  f"rms_y={m.get('rms_y_pct_span', float('nan')):.3f}% max_y={m.get('max_abs_y_pct_span', float('nan')):.3f}% "
                  f"bias_y={m.get('mean_signed_y_pct_span', float('nan')):+.3f}% "
                  f"rms_x={m.get('rms_x_pct_span', float('nan')):.3f}% max_x={m.get('max_abs_x_pct_span', float('nan')):.3f}% "
                  f"bias_x={m.get('mean_signed_x_pct_span', float('nan')):+.3f}%")
        print("  pooled", {k: round(v, 4) if isinstance(v, float) else v for k, v in f["pooled"].items()})


if __name__ == "__main__":
    main()
