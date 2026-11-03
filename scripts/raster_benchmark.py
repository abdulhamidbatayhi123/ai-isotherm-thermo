"""Synthetic raster benchmark for the raster digitiser (PREREG_P3A.md section 3.5).

Figures are drawn in the styles of the confirmatory raster figures:
  sparse  like the hydrazide-COF SI figures (Nguyen et al. 2022): about 28 adsorption
          points per isotherm, filled adsorption and white-filled open desorption markers
          of one colour per temperature, joined by lines, a steep step;
  dense   like MOF-303 (Hanikel et al. 2019, SI Fig. S18): about 80 adsorption points per
          isotherm, so markers overlap into chains along the step.
Marker shapes: circle, square, triangle (filled), as in CAU-23 (Lenzen et al. 2019).
Two drawing orders (desorption on top is the harder case) and two image widths.

The pixel position of every true point is known from matplotlib's transform. Reported:
  recall_visible  one-to-one recall over true markers with >= 30 % of their area visible
                  (a fully hidden marker cannot be recovered by any method);
  recall          one-to-one recall over all true markers;
  false           detections farther than one marker radius from every true point;
  curve_rms/max   distance of each detection from the true polyline, as a fraction of the
                  axis span (the metric that matters for fitting, and the right one for
                  dense figures where one-to-one pairing is ambiguous);
  rms_dx/dy       paired position error, fractions of the axis spans.

Output: logs/raster_benchmark.json and a printed summary.
"""
import io
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.signal import fftconvolve  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from p3a import digitise  # noqa: E402

COLOURS = {"T1": (0.0, 0.0, 0.0), "T2": (0.0, 0.0, 1.0), "T3": (0.0, 0.5, 0.0)}
X_SPAN, Y_SPAN = 1.0, 0.5
TEMPLATE = True  # template-by-example matching (the method used on real figures)


def isotherm(x, step, width, cap=0.45, low=0.02):
    return low + (cap - low) / (1 + np.exp(-(x - step) / width)) + 0.08 * x


def make_figure(style, marker, px_width, des_on_top, rng):
    dpi = 100
    fig = plt.figure(figsize=(px_width / dpi, px_width * 0.96 / dpi), dpi=dpi)
    ax = fig.add_axes([0.15, 0.12, 0.8, 0.83])
    truth = {}
    for k, (name, col) in enumerate(COLOURS.items()):
        step = 0.22 + 0.02 * k
        if style == "sparse":
            x_ads = np.concatenate([np.linspace(0.03, step - 0.03, 5),
                                    np.linspace(step - 0.02, step + 0.03, 9),
                                    np.linspace(step + 0.06, 0.95, 14)])
        else:
            x_ads = np.concatenate([np.linspace(0.01, step - 0.03, 15),
                                    np.linspace(step - 0.025, step + 0.03, 35),
                                    np.linspace(step + 0.04, 0.95, 30)])
        x_ads = np.clip(np.sort(x_ads + rng.normal(0, 0.002, x_ads.size)), 0.005, 0.97)
        cap = 0.45 - 0.015 * k
        y_ads = isotherm(x_ads, step, 0.008, cap=cap)
        x_des = x_ads[::-1] - 0.015
        y_des = isotherm(x_des, step - 0.02, 0.008, cap=cap) + 0.01
        z_ads, z_des = (2, 3) if des_on_top else (3, 2)
        ax.plot(x_ads, y_ads, "-" + marker, color=col, ms=5, mfc=col, mec=col, lw=0.8, zorder=z_ads)
        ax.plot(x_des, y_des, "-" + marker, color=col, ms=5, mfc="white", mec=col, lw=0.8, zorder=z_des)
        truth[name] = np.column_stack([x_ads, y_ads])
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 0.5)
    ax.set_xticks(np.arange(0, 1.01, 0.2))
    ax.set_yticks(np.arange(0, 0.51, 0.1))
    ax.tick_params(direction="in", length=4)
    fig.canvas.draw()
    to_px = ax.transData.transform
    H = fig.canvas.get_width_height()[1]
    xt_px = [to_px((v, 0))[0] for v in np.arange(0, 1.01, 0.2)]
    yt_px = [H - to_px((0, v))[1] for v in np.arange(0, 0.51, 0.1)]
    frame_row = int(round(H - to_px((0, 0))[1]))
    frame_col = int(round(to_px((0, 0))[0]))
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi)
    plt.close(fig)
    buf.seek(0)
    img = plt.imread(buf)[..., :3].astype(float)
    half_size_px = 5 / 2 * dpi / 72
    return img, truth, xt_px, yt_px, frame_row, frame_col, half_size_px


def marker_footprint(marker, px_width):
    """The marker's own footprint at the figure's scale, as a human would cut it from the
    legend: one filled marker drawn alone, then digitise.marker_template."""
    dpi = 100
    fig = plt.figure(figsize=(0.4, 0.4), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.plot([0.5], [0.5], marker, color=(0, 0, 1), ms=5, mfc=(0, 0, 1), mec=(0, 0, 1))
    ax.set_xlim(0, 1), ax.set_ylim(0, 1), ax.axis("off")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi)
    plt.close(fig)
    buf.seek(0)
    im = plt.imread(buf)[..., :3].astype(float)
    return digitise.marker_template(im, (0, 0, 1), (0, im.shape[0], 0, im.shape[1]))


def polyline_distance(p, line):
    """Distance from point p to a polyline, both in normalised units."""
    a, b = line[:-1], line[1:]
    ab = b - a
    t = np.clip(((p - a) * ab).sum(1) / np.maximum((ab**2).sum(1), 1e-30), 0, 1)
    proj = a + t[:, None] * ab
    return float(np.min(np.hypot(*(proj - p).T)))


def run_case(style, marker, px_width, des_on_top, seed):
    rng = np.random.default_rng(seed)
    img, truth, xt, yt, frow, fcol, h = make_figure(style, marker, px_width, des_on_top, rng)
    xt_eye = np.array(xt) + rng.uniform(-2, 2, len(xt))
    yt_eye = np.array(yt) + rng.uniform(-2, 2, len(yt))
    frow = digitise.find_frame_line(img, frow + rng.integers(-2, 3), "x")
    fcol = digitise.find_frame_line(img, fcol + rng.integers(-2, 3), "y")
    xa = digitise.fit_axis(digitise.snap_ticks(img, xt_eye, "x", frow), np.arange(0, 1.01, 0.2))
    ya = digitise.fit_axis(digitise.snap_ticks(img, yt_eye, "y", fcol), np.arange(0, 0.51, 0.1))
    # the template radius a human would choose: inside the marker for every shape
    r = {"o": 0.85, "s": 0.85, "^": 0.6}[marker] * h
    tol_norm = h / (max(xt) - min(xt))  # one marker half-size, in normalised x units
    region = (int(min(yt)) - 2, frow - 1, fcol + 2, int(max(xt)) + 2)
    n_true = n_found = n_false = n_vis = n_vis_found = 0
    ex, ey, curve = [], [], []
    for name, col in COLOURS.items():
        tr = truth[name]
        trn = tr / [X_SPAN, Y_SPAN]
        mask = (np.linalg.norm(img - np.array(col), axis=-1) < 0.18).astype(float)
        R = int(np.ceil(r)) + 1
        yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
        ker = (np.hypot(yy, xx) <= r).astype(float)
        vis_map = fftconvolve(mask, ker / ker.sum(), mode="same")
        tr_px = [((p_[1] - ya.a) / ya.b, (p_[0] - xa.a) / xa.b) for p_ in tr]
        visible = np.array([vis_map[int(round(a)), int(round(b))] >= 0.3 for a, b in tr_px])
        cents = digitise.raster_markers(img, col, r, mode="filled", region=region,
                                        template=marker_footprint(marker, px_width) if TEMPLATE else None)
        dig = np.column_stack([xa(cents[:, 1]), ya(cents[:, 0])]) if len(cents) else np.zeros((0, 2))
        used = set()
        for p in dig:
            pn = p / [X_SPAN, Y_SPAN]
            curve.append(polyline_distance(pn, trn))
            d = np.hypot(*(trn - pn).T)
            order = np.argsort(d)
            j = next((int(k) for k in order if int(k) not in used), None)
            if j is not None and d[j] <= tol_norm:
                used.add(j)
                ex.append(p[0] - tr[j, 0])
                ey.append(p[1] - tr[j, 1])
            elif d[order[0]] > tol_norm:
                n_false += 1
        n_true += len(tr)
        n_found += len(used)
        n_vis += int(visible.sum())
        n_vis_found += len([j for j in used if visible[j]])
    ex, ey, curve = np.array(ex), np.array(ey), np.array(curve)
    return {"style": style, "marker": marker, "px_width": px_width, "des_on_top": des_on_top,
            "seed": seed, "axis_residual_px": [xa.residual, ya.residual],
            "recall": n_found / n_true, "recall_visible": n_vis_found / max(n_vis, 1),
            "visible_fraction": n_vis / n_true, "false_detections": n_false,
            "curve_rms": float(np.sqrt(np.mean(curve**2))), "curve_max": float(curve.max()),
            "rms_dx": float(np.sqrt(np.mean(ex**2)) / X_SPAN),
            "rms_dy": float(np.sqrt(np.mean(ey**2)) / Y_SPAN),
            "max_dx": float(np.max(np.abs(ex)) / X_SPAN), "max_dy": float(np.max(np.abs(ey)) / Y_SPAN)}


def main():
    out = [run_case(st, mk, w, top, s)
           for st in ("sparse", "dense") for mk in ("o", "s", "^")
           for w in (800, 1400) for top in (False, True) for s in (0, 1)]
    (ROOT / "logs/raster_benchmark.json").write_text(json.dumps(out, indent=2))
    for r in out:
        print(f"{r['style']:6s} {r['marker']} w={r['px_width']} top={'des' if r['des_on_top'] else 'ads'} "
              f"s={r['seed']} recall={r['recall']:.2f} vis={r['visible_fraction']:.2f} "
              f"recall_vis={r['recall_visible']:.2f} false={r['false_detections']} "
              f"curve rms={r['curve_rms']:.4f} max={r['curve_max']:.4f} "
              f"pair rms dx={r['rms_dx']:.4f} dy={r['rms_dy']:.4f}")
    print("WORST over all cases: recall_visible min", min(r["recall_visible"] for r in out),
          "| false max", max(r["false_detections"] for r in out),
          "| curve_rms max", max(r["curve_rms"] for r in out),
          "| curve_max max", max(r["curve_max"] for r in out))


if __name__ == "__main__":
    main()
