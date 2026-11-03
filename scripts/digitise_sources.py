"""Digitise the confirmatory and development isotherm figures (PREREG_P3A.md section 3.5).

One function per source. Each returns a table of adsorption-branch points and a provenance
record. Outputs:
  data/raw/digitised/<key>.csv           points (local only: source licences, INVENTORY s5)
  data/raw/digitised/<key>_overlay.png   detections drawn on the source image (local only)
  data/digitised_provenance/<key>.json   method, calibration, counts, checks (committed)

Usage: python scripts/digitise_sources.py [key ...]   (no key: all sources)
Every source is digitised before any model sees it (blind to model outputs).
"""
import json
import sys
from pathlib import Path

import fitz
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from p3a import digitise  # noqa: E402

RAW = ROOT / "data/raw/primary"
OUT = ROOT / "data/raw/digitised"
PROV = ROOT / "data/digitised_provenance"


def overlay(page, clip, pts_by_label, path, dpi=200):
    """Draw detected points (PDF coordinates) as small crosses on the rendered clip."""
    from PIL import Image, ImageDraw

    OUT.mkdir(parents=True, exist_ok=True)

    pix = page.get_pixmap(dpi=dpi, clip=clip)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    dr = ImageDraw.Draw(im)
    s = dpi / 72.0
    for pts in pts_by_label.values():
        for x, y in pts:
            u, v = (x - clip.x0) * s, (y - clip.y0) * s
            dr.line((u - 4, v, u + 4, v), fill=(255, 0, 255), width=1)
            dr.line((u, v - 4, u, v + 4), fill=(255, 0, 255), width=1)
    im.save(path)


def save(key, rows, prov):
    OUT.mkdir(parents=True, exist_ok=True)
    PROV.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / f"{key}.csv", index=False)
    prov["n_points_by_T"] = {str(k): int(v) for k, v in df.groupby("T_C").size().items()}
    (PROV / f"{key}.json").write_text(json.dumps(prov, indent=2, default=float))
    print(key, prov["n_points_by_T"], "axis residuals (pt):",
          [round(prov["axis_x"]["residual"], 4), round(prov["axis_y"]["residual"], 4)])


# ------------------------------------------------------------------ COF-432 (vector)


def cof432():
    """Nguyen et al., JACS 2020, 142, 2218 (10.1021/jacs.9b13094), Fig. 4a, page 3.
    Vector figure. Markers: outer 4.2 pt disc in the series colour plus a 3.7 pt inner disc,
    white for desorption (open) and coloured for adsorption (filled). Tick labels are glyph
    outlines, so tick values are read from the figure: x (P/Psat) 0, 0.2, ..., 1.0 at the
    six x tick marks; y (g/g) 0, 0.1, 0.2, 0.3 at the four y tick marks. Legend (read by
    eye, top to bottom): black 10 C, red 25 C, blue 40 C."""
    key = "nguyen2020_cof432"
    page = fitz.open(RAW / key / "20COFWater.pdf")[2]
    x_ticks = [(100.55, 0.0), (131.33, 0.2), (162.12, 0.4), (192.90, 0.6), (223.69, 0.8), (254.47, 1.0)]
    y_ticks = [(159.28, 0.0), (128.35, 0.1), (97.35, 0.2), (66.42, 0.3)]
    # tick centres above are the vector tick marks' centres (see provenance check below)
    xa = digitise.fit_axis([c for c, _ in x_ticks], [v for _, v in x_ticks])
    ya = digitise.fit_axis([c for c, _ in y_ticks], [v for _, v in y_ticks])
    plot = fitz.Rect(100.8, 61.9, 264.8, 162.7)
    legend = fitz.Rect(178.0, 98.0, 242.0, 131.0)
    items = [i for i in digitise.vector_items(page, plot)
             if not legend.contains(fitz.Point(i["x"], i["y"]))]
    marks = digitise.concentric_markers(items, outer_size=4.2, inner_size=3.7)
    colour_T = {(0.0, 0.0, 0.0): 10, (1.0, 0.0, 0.0): 25, (0.0, 0.0, 1.0): 40}
    rows, pts = [], {}
    for col, tc in colour_T.items():
        f = marks[col]["filled"]
        f = f[np.argsort(f[:, 0])]
        pts[tc] = f
        for x, y in f:
            rows.append({"source": key, "material": "COF-432", "T_C": tc, "branch": "ads",
                         "x_quantity": "p/psat", "x": float(xa(x)), "q_unit": "g/g", "q": float(ya(y))})
    # check: the tick centres used match the vector tick marks
    ticks_x = digitise._tick_positions(page, fitz.Rect(95, 160, 270, 168), "x")
    ticks_y = digitise._tick_positions(page, fitz.Rect(98, 55, 106, 165), "y")
    prov = {"key": key, "figure": "Fig. 4a, page 3", "method": "vector, concentric markers",
            "doi": "10.1021/jacs.9b13094", "axis_x": vars(xa), "axis_y": vars(ya),
            "x_ticks": x_ticks, "y_ticks": y_ticks,
            "vector_tick_marks_x": ticks_x.tolist(), "vector_tick_marks_y": ticks_y.tolist(),
            "n_open_markers_by_T": {tc: int(len(marks[c]["open"])) for c, tc in colour_T.items()},
            "legend_excluded": list(legend)}
    overlay(page, fitz.Rect(90, 55, 270, 172), pts, OUT / f"{key}_overlay.png")
    save(key, rows, prov)


# ------------------------------------------------- helpers for legend-mapped vector figures


def legend_marker_colour(page, label_text, label_clip, marker_clip):
    """Colour of the legend marker on the same line as label_text (a text span inside
    label_clip); the marker is the small filled item in marker_clip nearest in y."""
    ys = []
    for b in page.get_text("dict", clip=label_clip)["blocks"]:
        for line in b.get("lines", []):
            for sp in line["spans"]:
                if sp["text"].strip().startswith(label_text.strip()):
                    ys.append(0.5 * (sp["bbox"][1] + sp["bbox"][3]))
    if len(ys) != 1:
        raise ValueError(f"legend label {label_text!r} found {len(ys)} times")
    items = [i for i in digitise.vector_items(page, marker_clip, 1.5, 8.0) if i["fill"]]
    return min(items, key=lambda i: abs(i["y"] - ys[0]))["fill"]


def markers_outside(page, plot, exclude, colour, size_range, shape_tol=0.45):
    """Centres of filled marker items of one colour in plot, outside the legend box;
    an item drawn twice at one place is kept once."""
    # markers are square-ish (width = height within 0.3 pt for circles and squares; a little
    # more for triangles): this rejects arrow heads and other annotation items
    pts = [(i["x"], i["y"]) for i in digitise.vector_items(page, plot, *size_range)
           if (i["fill"] == colour or (i["fill"] is None and i["stroke"] == colour))
           and abs(i["w"] - i["h"]) <= shape_tol
           and not exclude.contains(fitz.Point(i["x"], i["y"]))]
    out = []
    for p_ in sorted(pts):
        if not out or np.hypot(p_[0] - out[-1][0], p_[1] - out[-1][1]) > 0.3:
            out.append(p_)
    return np.array(out).reshape(-1, 2)


def legend_mapped(key, pdf, page_no, xlab, xtick, ylab, ytick, plot, legend, label_clip,
                  labels, size_range, material, branch, x_quantity, q_unit, figure, doi, note,
                  overlay_clip, shape_tol=0.45):
    """Shared body of the legend-mapped vector extractions."""
    page = fitz.open(RAW / key / pdf)[page_no - 1]
    xa = digitise.vector_axis(page, xlab, "x", tick_clip=xtick)
    ya = digitise.vector_axis(page, ylab, "y", tick_clip=ytick)
    colour_T = {}
    for lab, tc in labels:
        colour_T[legend_marker_colour(page, lab, label_clip, legend)] = tc
    if len(colour_T) != len(labels):
        raise ValueError("two legend labels mapped to one colour")
    rows, pts = [], {}
    for c, tc in colour_T.items():
        m = markers_outside(page, plot, legend, c, size_range, shape_tol)
        pts[tc] = m
        for x, y in m:
            rows.append({"source": key, "material": material, "T_C": tc, "branch": branch,
                         "x_quantity": x_quantity, "x": float(xa(x)), "q_unit": q_unit,
                         "q": float(ya(y))})
    prov = {"key": key, "figure": figure, "method": "vector markers, legend-mapped", "doi": doi,
            "axis_x": vars(xa), "axis_y": vars(ya),
            "legend_colours": {str(v): k for k, v in colour_T.items()}, "note": note,
            "marker_size_range_pt": list(size_range), "marker_shape_tol_pt": shape_tol}
    overlay(page, overlay_clip, pts, OUT / f"{key}_overlay.png")
    save(key, rows, prov)


def co2cl2btdd():
    """Rieth et al., ACS Cent. Sci. 2017, 3, 668 (10.1021/acscentsci.7b00186), SI Fig. S8,
    page 13: characteristic curves W (cm3 STP/g) against A (kJ/mol) from the isotherms at
    298, 293 and 283 K. p/psat = exp(-1000 A / (R T)) recovers the relative pressure exactly,
    whatever saturation pressure the authors used."""
    legend_mapped(
        "rieth2017_co2cl2btdd", "oc7b00186_si_001.pdf", 13,
        xlab=fitz.Rect(150, 372, 520, 395), xtick=fitz.Rect(150, 362, 520, 375),
        ylab=fitz.Rect(120, 105, 158, 375), ytick=fitz.Rect(155, 100, 170, 375),
        plot=fitz.Rect(160, 100, 490, 368), legend=fitz.Rect(345, 200, 440, 255),
        label_clip=fitz.Rect(395, 200, 440, 255),
        labels=(("298", 24.85), ("293", 19.85), ("283", 9.85)), size_range=(2.0, 5.0),
        material="Co2Cl2(BTDD)", branch="ads (characteristic curve)", x_quantity="A_kJ_per_mol",
        q_unit="cm3STP/g", figure="SI Fig. S8, page 13", doi="10.1021/acscentsci.7b00186",
        note="characteristic curve; p/psat = exp(-1000 A/(R T)), T the isotherm temperature",
        overlay_clip=fitz.Rect(120, 95, 500, 395))


def kmf1():
    """Cho et al., Nat. Commun. 2020 (10.1038/s41467-020-18968-7), SI Fig. 18, page 17:
    characteristic curves W (mL/g) against A (kJ/mol) at 20, 30 and 40 C. W is converted to
    g/g in the dataset builder with a stated liquid-density assumption."""
    legend_mapped(
        "cho2020_kmf1", "41467_2020_18968_MOESM1_ESM.pdf", 17,
        xlab=fitz.Rect(195, 281, 450, 294), xtick=fitz.Rect(195, 270, 450, 282),
        ylab=fitz.Rect(184, 95, 199, 284), ytick=fitz.Rect(196, 95, 206, 284),
        plot=fitz.Rect(199, 98, 450, 279), legend=fitz.Rect(395, 105, 412, 150),
        label_clip=fitz.Rect(405, 105, 440, 150),
        labels=((" 20", 20.0), (" 30", 30.0), (" 40", 40.0)), size_range=(3.0, 8.0),
        material="KMF-1", branch="ads (characteristic curve)", x_quantity="A_kJ_per_mol",
        q_unit="mL/g", figure="SI Fig. 18, page 17", doi="10.1038/s41467-020-18968-7",
        note="characteristic curve in adsorbed liquid volume; density assumption in the builder",
        overlay_clip=fitz.Rect(180, 90, 455, 300), shape_tol=1.2)  # triangles are 6.6 x 5.6 pt


def kim2018_mof801():
    """Kim et al., Nat. Commun. 2018, 9, 1191 (10.1038/s41467-018-03162-7), Fig. 1b, page 3:
    MOF-801 adsorption isotherms at 15, 25, 45, 65 and 85 C (TGA), 0 to 40 % RH. The 105 C
    curve is a characteristic-curve prediction, not a measurement, and is excluded."""
    legend_mapped(
        "kim2018_natcommun", "s41467-018-03162-7.pdf", 3,
        xlab=fitz.Rect(345, 227, 515, 237), xtick=fitz.Rect(345, 218, 515, 229),
        ylab=fitz.Rect(338, 60, 351, 232), ytick=fitz.Rect(349, 60, 360, 232),
        plot=fitz.Rect(352, 58, 515, 227), legend=fitz.Rect(462, 160, 480, 220),
        label_clip=fitz.Rect(478, 160, 505, 220),
        labels=(("15", 15.0), ("25", 25.0), ("45", 45.0), ("65", 65.0), ("85", 85.0)),
        size_range=(4.4, 4.9), material="MOF-801", branch="ads", x_quantity="RH_percent",
        q_unit="g/g", figure="Fig. 1b, page 3", doi="10.1038/s41467-018-03162-7",
        note="105 C curve excluded (a prediction from the characteristic curve, per the caption)",
        overlay_clip=fitz.Rect(335, 50, 520, 245))


# ------------------------------------------------- raster figures (template matching)


def raster_overlay(img, pts_by_T, path, region):
    from PIL import Image, ImageDraw

    OUT.mkdir(parents=True, exist_ok=True)
    im = Image.fromarray((img * 255).astype(np.uint8))
    dr = ImageDraw.Draw(im)
    for pts in pts_by_T.values():
        for y, x in pts:
            dr.line((x - 5, y, x + 5, y), fill=(255, 0, 255), width=1)
            dr.line((x, y - 5, x, y + 5), fill=(255, 0, 255), width=1)
    r0, r1, c0, c1 = region
    dr.rectangle((c0, r0, c1, r1), outline=(0, 200, 0))
    im.save(path)


def refine_legend_marker(img, r, c, win=12, min_px=20):
    """Centre of the solid (non-white) blob nearest (r, c) within +-win px: the legend
    marker position read by eye is refined to the marker's centroid, so the colour sample
    and the template do not depend on reading error."""
    from scipy import ndimage

    r0, c0 = max(0, r - win), max(0, c - win)
    sub = img[r0: r + win + 1, c0: c + win + 1]
    solid = sub.min(-1) < 0.8
    # a legend line is thin: an opening keeps the marker disc and drops the line
    solid = ndimage.binary_opening(solid, structure=np.ones((3, 3)))
    lab, n = ndimage.label(solid)
    best, bd = None, 1e9
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        if ys.size < min_px:
            continue
        d = np.hypot(ys.mean() + r0 - r, xs.mean() + c0 - c)
        if d < bd:
            best, bd = (int(round(ys.mean() + r0)), int(round(xs.mean() + c0))), d
    if best is None:
        raise ValueError(f"no legend marker near {(r, c)}")
    return best


def raster_source(key, pdf, page_no, xref, frame_row, frame_col, x_ticks, y_ticks, series,
                  legend_box, material, x_quantity, q_unit, figure, doi, note,
                  tpl_half=14, open_px=2, colour_tol=0.18, plot_region=None, tick_search=8, src_dir=None,
                  frame_top=None, frame_right=None):
    """Raster figure digitised with the validated method (scripts/digitisation_error.py,
    scripts/raster_benchmark.py).

    frame_row/frame_col: approximate pixel row of the x-axis line and column of the y-axis
      line, read from the grid image (scripts/raster_inspect.py); refined by find_frame_line.
    x_ticks/y_ticks: [(approximate pixel, value)] read by eye; refined by snap_ticks.
    series: [(T_C, (row, col) of the legend's adsorption marker)]: the series colour is the
      median colour at the legend marker centre and the template is cut from it.
    legend_box: (r0, r1, c0, c1) excluded from the search.
    """
    page = fitz.open(RAW / (src_dir or key) / pdf)[page_no - 1]
    img = digitise.load_page_image(page, xref=xref)
    frow = digitise.find_frame_line(img, frame_row, "x")
    fcol = digitise.find_frame_line(img, frame_col, "y")
    xs = digitise.snap_ticks(img, [c for c, _ in x_ticks], "x", frow, search=tick_search)
    ys = digitise.snap_ticks(img, [c for c, _ in y_ticks], "y", fcol, search=tick_search)
    xa = digitise.fit_axis(xs, [v for _, v in x_ticks])
    ya = digitise.fit_axis(ys, [v for _, v in y_ticks])
    # search region: inside the frame (top and right edges given per figure, else 40 px
    # beyond the outermost ticks)
    top = frame_top + 2 if frame_top is not None else max(0, int(min(c for c, _ in y_ticks)) - 40)
    right = frame_right - 2 if frame_right is not None else int(max(c for c, _ in x_ticks)) + 40
    region = plot_region or (top, frow - 1, fcol + 2, right)
    rows, pts, prov_series = [], {}, {}
    for item in series:
        tc, (lr, lc) = item[0], item[1]
        lr, lc = refine_legend_marker(img, lr, lc)
        legend_col = np.median(img[lr - 1: lr + 2, lc - 1: lc + 2].reshape(-1, 3), axis=0)
        # the data markers' colour may differ from the legend symbol's (Nguyen 2022: legend
        # blue (0,0,255), data blue (4,51,255)); then it is given, read from the histogram
        col = np.asarray(item[2], float) / 255.0 if len(item) > 2 and item[2] else legend_col
        tpl = digitise.marker_template(img, legend_col, (lr - tpl_half, lr + tpl_half + 1, lc - tpl_half,
                                                         lc + tpl_half + 1), tol=colour_tol, open_px=open_px)
        cents = digitise.raster_markers(img, col, 0.5 * min(tpl.shape), tol=colour_tol,
                                        region=region, exclude=[legend_box], template=tpl)
        pts[tc] = cents
        prov_series[str(tc)] = {"colour": [round(float(v), 3) for v in col],
                                "template_px": list(tpl.shape), "n_detected": int(len(cents))}
        for y, x in cents:
            rows.append({"source": key, "material": material, "T_C": tc, "branch": "ads",
                         "x_quantity": x_quantity, "x": float(xa(x)), "q_unit": q_unit,
                         "q": float(ya(y))})
    prov = {"key": key, "figure": figure, "method": "raster template matching (open-marker veto)",
            "doi": doi, "image_px": list(img.shape[:2]), "xref": xref,
            "axis_x": vars(xa), "axis_y": vars(ya), "x_ticks": x_ticks, "y_ticks": y_ticks,
            "snapped_x_px": xs.tolist(), "snapped_y_px": ys.tolist(),
            "frame_row": int(frow), "frame_col": int(fcol), "search_region": list(region),
            "legend_box": list(legend_box), "series": prov_series, "note": note}
    raster_overlay(img, pts, OUT / f"{key}_overlay.png", region)
    save(key, rows, prov)


def hanikel2019_mof303():
    """Hanikel et al., ACS Cent. Sci. 2019, 5, 1699 (10.1021/acscentsci.9b00745), SI Fig. S17,
    page 15 (embedded image xref 254, 1343 x 1028 px): MOF-303 against P/Psat at 10, 25, 35
    and 50 C; filled adsorption and open desorption circles of one colour per temperature.
    Tick and legend pixel positions read from the grid image (x 1.5 of the 2/3-size view)."""
    raster_source(
        "hanikel2019_mof303", "oc9b00745_si_001.pdf", 15, 254, frame_row=855, frame_col=245,
        x_ticks=[(312, 0.0), (465, 0.2), (620, 0.4), (773, 0.6), (927, 0.8), (1080, 1.0)],
        y_ticks=[(802, 0), (698, 100), (593, 200), (488, 300), (383, 400), (278, 500), (172, 600)],
        series=[(10, (450, 725)), (25, (546, 725)), (35, (642, 725)), (50, (738, 725))],
        legend_box=(420, 800, 670, 1110), material="MOF-303", x_quantity="p/psat",
        q_unit="cm3STP/g", figure="SI Fig. S17, page 15", doi="10.1021/acscentsci.9b00745",
        note="many adsorption markers in the steps are covered by desorption markers; only "
             "visible markers are detected (coverage per T in n_points_by_T)")


def _hcof(fig, page_no, xref, material, x_ticks, y_ticks, legend_rows, legend_col, legend_box,
          frame_row, frame_col):
    raster_source(
        f"nguyen2022_hcof_{fig}", "oc2c00398_si_001.pdf", page_no, xref, frame_row, frame_col,
        x_ticks=x_ticks, y_ticks=y_ticks,
        series=[(tc, (r, legend_col), dc) for tc, r, dc in
                zip((15, 25, 35), legend_rows, (None, (4, 51, 255), None))],
        legend_box=legend_box, material=material, x_quantity="p/psat", q_unit="g/g",
        figure=f"SI Fig. {fig}, page {page_no}", doi="10.1021/acscentsci.2c00398",
        note="Nguyen et al., ACS Cent. Sci. 2022; filled adsorption and open desorption "
             "circles; ticks and legend read from the grid image",
        src_dir="nguyen2022_hcof")


XT6 = lambda c: list(zip(c, (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)))  # noqa: E731


def hcof_s43():
    _hcof("S43", 36, 225, "AB-COF", XT6((97, 234, 370, 506, 641, 776)),
          list(zip((693, 555, 419, 283, 146, 10), (0, 0.1, 0.2, 0.3, 0.4, 0.5))),
          (356, 403, 451), 372, (335, 470, 350, 700), 693, 97)


def hcof_s44():
    _hcof("S44", 36, 226, "COF-480-hydrazide", XT6((98, 233, 369, 503, 638, 773)),
          list(zip((685, 550, 415, 280, 145, 12), (0, 0.1, 0.2, 0.3, 0.4, 0.5))),
          (313, 361, 409), 355, (295, 430, 330, 690), 685, 98)


def hcof_s45():
    _hcof("S45", 37, 230, "Py-COF-2D", XT6((92, 229, 365, 501, 637, 773)),
          list(zip((695, 597, 499, 401, 303, 205, 107, 12), (0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7))),
          (76, 124, 172), 152, (55, 195, 130, 500), 695, 92)


def hcof_s46():
    _hcof("S46", 37, 231, "COF-482-hydrazide", XT6((94, 230, 366, 502, 637, 773)),
          list(zip((692, 522, 352, 182, 12), (0, 0.2, 0.4, 0.6, 0.8))),
          (80, 130, 178), 152, (60, 200, 130, 500), 692, 94)


def nguyen2025_hcof2():
    """Nguyen et al., ACS Cent. Sci. 2025 (10.1021/acscentsci.4c01878), SI Fig. S8, page 10
    (xref 93, 827 x 727 px): HCOF-2 at 25, 35, 45 C; left axis cm3(STP)/g."""
    raster_source(
        "nguyen2025_hcof2", "oc4c01878_si_001.pdf", 10, 93, frame_row=647, frame_col=93,
        x_ticks=XT6((93, 222, 350, 480, 608, 737)),
        y_ticks=list(zip((647, 505, 363, 221, 80), (0, 100, 200, 300, 400))),
        series=[(25, (306, 438)), (35, (357, 438)), (45, (425, 438))],
        legend_box=(290, 470, 420, 590), frame_top=10, frame_right=778, material="HCOF-2", x_quantity="p/psat",
        q_unit="cm3STP/g", figure="SI Fig. S8, page 10", doi="10.1021/acscentsci.4c01878",
        note="filled adsorption, open desorption circles", src_dir="nguyen2025_onset")


def nguyen2025_cof309():
    """Nguyen et al., ACS Cent. Sci. 2025 (10.1021/acscentsci.4c01878), SI Fig. S23, page 24
    (xref 130, 865 x 765 px): COF-309 at 25, 35, 45 C; left axis cm3(STP)/g."""
    raster_source(
        "nguyen2025_cof309", "oc4c01878_si_001.pdf", 24, 130, frame_row=683, frame_col=93,
        x_ticks=XT6((93, 228, 362, 497, 631, 765)),
        y_ticks=list(zip((683, 548, 413, 279, 145, 10), (0, 200, 400, 600, 800, 1000))),
        series=[(25, (326, 464)), (35, (386, 464)), (45, (452, 464))],
        legend_box=(310, 495, 445, 615), frame_top=10, frame_right=780, material="COF-309", x_quantity="p/psat",
        q_unit="cm3STP/g", figure="SI Fig. S23, page 24", doi="10.1021/acscentsci.4c01878",
        note="filled adsorption, open desorption circles", src_dir="nguyen2025_onset")


TAN_MATERIALS = {"red": "HFPTP-PDA-COF", "blue": "HFPTP-DMePDA-COF", "black": "HFPTP-BPDA-COF"}
# Tan et al., Nat. Commun. 2021, 12, 6747 (10.1038/s41467-021-27128-4), main Fig. 3, page 5
# (xref 204, 1285 x 2500 px). One panel per temperature, one colour per COF (caption):
# a 25 C circles, b 15 C triangles, c 10 C squares; filled = adsorption. No legend in the
# panels: each template is cut from the series' last (highest-pressure) filled marker.
TAN_PANELS = {
    "a": dict(T=25, x=(140, 227, 313, 400, 486, 572), y=(474, 367, 260, 153, 46),
              frame=(37, 488, 127, 578), tpl={"black": (95, 522), "red": (150, 523), "blue": (347, 522)}),
    "b": dict(T=15, x=(792, 878, 964, 1050, 1136, 1222), y=(474, 367, 260, 153, 46),
              frame=(37, 487, 780, 1232), tpl={"black": (112, 1178), "red": (157, 1180), "blue": (315, 1178)}),
    "c": dict(T=10, x=(148, 234, 320, 406, 492, 576), y=(1072, 965, 858, 751, 644),
              frame=(635, 1086, 135, 584), tpl={"black": (733, 535), "red": (783, 535), "blue": (960, 535)}),
}


def tan2021_fig3():
    for panel, cfg in TAN_PANELS.items():
        top, bottom, left, right = cfg["frame"]
        for colour, material in TAN_MATERIALS.items():
            raster_source(
                f"tan2021_fig3{panel}_{material}", "s41467-021-27128-4.pdf", 5, 204,
                frame_row=bottom, frame_col=left, x_ticks=XT6(cfg["x"]),
                y_ticks=list(zip(cfg["y"], (0.0, 0.1, 0.2, 0.3, 0.4))),
                series=[(cfg["T"], cfg["tpl"][colour])], legend_box=(0, 0, 0, 0),
                frame_top=top, frame_right=right, material=material, x_quantity="p/psat",
                q_unit="g/g", figure=f"main Fig. 3{panel}, page 5", doi="10.1038/s41467-021-27128-4",
                note="template from the series' last filled marker (no legend in the panel)",
                src_dir="tan2021_watercluster")


TAN4_MATERIALS = {"red": "TFBCz-PDA-COF", "blue": "TTA-TFB-COF", "green": "TFPPy-PDA-COF",
                  "black": "TPB-DMTP-COF"}
# main Fig. 4i-k, page 6 (xref 213, 2000 x 2223 px): i 25 C circles, j 15 C triangles,
# k 10 C squares (caption). Positions read from 1.5x crops with a 20 px grid; templates from
# isolated filled markers (the last point, or a step point where last points crowd).
_Y4 = (1478, 1370, 1262, 1153)
TAN4_PANELS = {
    "i": dict(T=25, x=(149, 237, 325, 413, 500, 587), frame=(1040, 1485, 141, 593),
              tpl={"red": (1221, 541), "blue": (1189, 541), "green": (1455, 389), "black": (1330, 475)}),
    "j": dict(T=15, x=(840, 928, 1016, 1103, 1190, 1277), frame=(1040, 1485, 831, 1285),
              tpl={"red": (1213, 1231), "blue": (1198, 1231), "green": (1440, 1091), "black": (1292, 1189)}),
    "k": dict(T=10, x=(1527, 1615, 1703, 1790, 1877, 1965), frame=(1040, 1485, 1517, 1971),
              tpl={"red": (1219, 1919), "blue": (1203, 1919), "green": (1431, 1775), "black": (1389, 1853)}),
}


def tan2021_fig4():
    for panel, cfg in TAN4_PANELS.items():
        top, bottom, left, right = cfg["frame"]
        for colour, material in TAN4_MATERIALS.items():
            raster_source(
                f"tan2021_fig4{panel}_{material}", "s41467-021-27128-4.pdf", 6, 213,
                frame_row=bottom, frame_col=left, x_ticks=XT6(cfg["x"]),
                y_ticks=list(zip(_Y4, (0.0, 0.2, 0.4, 0.6))),
                series=[(cfg["T"], cfg["tpl"][colour])], legend_box=(0, 0, 0, 0),
                frame_top=top, frame_right=right, material=material, x_quantity="p/psat",
                q_unit="g/g", figure=f"main Fig. 4{panel}, page 6", doi="10.1038/s41467-021-27128-4",
                note="template from an isolated filled marker (no legend in the panel)",
                src_dir="tan2021_watercluster")


SOURCES = {"nguyen2020_cof432": cof432, "hanikel2019_mof303": hanikel2019_mof303,
           "tan2021_fig3": tan2021_fig3, "tan2021_fig4": tan2021_fig4,
           "nguyen2025_hcof2": nguyen2025_hcof2, "nguyen2025_cof309": nguyen2025_cof309,
           "nguyen2022_hcof_S43": hcof_s43, "nguyen2022_hcof_S44": hcof_s44,
           "nguyen2022_hcof_S45": hcof_s45, "nguyen2022_hcof_S46": hcof_s46, "rieth2017_co2cl2btdd": co2cl2btdd, "cho2020_kmf1": kmf1,
           "kim2018_natcommun": kim2018_mof801}

if __name__ == "__main__":
    keys = sys.argv[1:] or list(SOURCES)
    for k in keys:
        SOURCES[k]()
