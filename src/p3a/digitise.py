"""Digitising isotherm figures from PDFs.

Vector figures: markers are read from the PDF drawing commands (PyMuPDF), and the axes are
calibrated from the PDF's own tick labels, snapped to the tick marks where they are found.
Raster figures: see `raster_*` functions; the axis calibration there needs tick pixel
positions and their values, supplied per figure in the digitisation script and recorded.

Every function is deterministic. The measured digitisation error (PREREG_P3A.md section 3.5)
comes from `scripts/digitisation_error.py`, which compares these functions with numeric data.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np

_NUM = re.compile(r"^[−\-]?\d+(\.\d+)?$")


@dataclass
class AxisMap:
    """value = a + b * coordinate (linear axes) or log10(value) = a + b * coordinate."""

    a: float
    b: float
    log: bool = False
    residual: float = 0.0  # RMS calibration residual, in coordinate units
    n_ticks: int = 0

    def __call__(self, c):
        v = self.a + self.b * np.asarray(c, dtype=float)
        return 10.0**v if self.log else v


def fit_axis(coords, values, log=False):
    """Least-squares axis map through (coordinate, value) tick pairs; residual in coordinates."""
    coords = np.asarray(coords, float)
    values = np.asarray(values, float)
    y = np.log10(values) if log else values
    if len(coords) < 2:
        raise ValueError("an axis needs at least two calibrated ticks")
    b, a = np.polyfit(coords, y, 1)
    pred_c = (y - a) / b
    res = float(np.sqrt(np.mean((pred_c - coords) ** 2)))
    return AxisMap(a=float(a), b=float(b), log=log, residual=res, n_ticks=len(coords))


def numeric_labels(page, clip):
    """Numeric text spans inside clip: list of (value, x_centre, y_centre)."""
    out = []
    for block in page.get_text("dict", clip=clip)["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                t = span["text"].strip().replace("−", "-")
                if _NUM.match(t):
                    x0, y0, x1, y1 = span["bbox"]
                    xc, yc = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
                    # get_text(clip=) returns spans that merely touch the clip; a label of the
                    # other axis at the corner would otherwise be taken (CORRECTIONS P3A-6)
                    if clip.x0 <= xc <= clip.x1 and clip.y0 <= yc <= clip.y1:
                        out.append((float(t), xc, yc))
    return out


def _tick_positions(page, clip, axis):
    """Centres of short thin line-like drawing items in clip (candidate tick marks).

    axis="x": vertical ticks (thin in x), returns their x. axis="y": horizontal ticks, their y.
    """
    pos = []
    for d in page.get_drawings():
        r = d["rect"]
        # a tick line has zero width or height; fitz treats such a rect as empty, so
        # Rect.intersects would reject it. Test the coordinates directly.
        if not (r.x1 >= clip.x0 and r.x0 <= clip.x1 and r.y1 >= clip.y0 and r.y0 <= clip.y1):
            continue
        w, h = r.width, r.height
        if axis == "x" and w < 0.6 and 1.0 < h < 8.0:
            pos.append(0.5 * (r.x0 + r.x1))
        if axis == "y" and h < 0.6 and 1.0 < w < 8.0:
            pos.append(0.5 * (r.y0 + r.y1))
    return np.array(sorted(pos))


def vector_axis(page, label_clip, axis, tick_clip=None, snap_tol=1.5, log=False):
    """Calibrate an axis from its numeric tick labels; snap each label to the nearest tick mark
    within snap_tol points if tick_clip is given and a tick is found.

    If no label snaps to a tick mark, label centres are used, and then only the labels of
    the most common text length: a centred label's box centre depends on glyph widths, so
    '10' and '1' are not centred alike (CORRECTIONS P3A-6)."""
    labels = numeric_labels(page, label_clip)
    if not labels:
        raise ValueError("no numeric tick labels found")
    coords = np.array([lx if axis == "x" else ly for _, lx, ly in labels])
    values = np.array([v for v, _, _ in labels])
    snapped = np.zeros(len(coords), bool)
    if tick_clip is not None:
        ticks = _tick_positions(page, tick_clip, axis)
        if len(ticks):
            for i, c in enumerate(coords):
                j = np.argmin(np.abs(ticks - c))
                if abs(ticks[j] - c) <= snap_tol:
                    coords[i] = ticks[j]
                    snapped[i] = True
    if not snapped.any() and axis == "x":
        widths = np.array([len(f"{v:g}") for v in values])
        modal = np.bincount(widths).argmax()
        keep = widths == modal
        if keep.sum() >= 2:
            coords, values = coords[keep], values[keep]
    return fit_axis(coords, values, log=log)


def vector_markers(page, clip, min_size=1.2, max_size=6.0, merge_tol=0.4):
    """Marker centres inside clip, grouped by colour.

    A marker is a drawing item whose bounding box is between min_size and max_size points on
    both sides. Filled and stroked copies of one marker are merged when their centres are
    within merge_tol points. Returns {colour_key: array of (x, y)} in PDF coordinates.
    """
    groups: dict[tuple, list] = {}
    for d in page.get_drawings():
        r = d["rect"]
        if not clip.contains(r):
            continue
        if not (min_size <= r.width <= max_size and min_size <= r.height <= max_size):
            continue
        col = d.get("fill") or d.get("color")
        if col is None:
            continue
        key = tuple(round(v, 2) for v in col)
        groups.setdefault(key, []).append((0.5 * (r.x0 + r.x1), 0.5 * (r.y0 + r.y1)))
    out = {}
    for key, pts in groups.items():
        pts = np.array(pts)
        keep = []
        for p in pts:
            if not any(np.hypot(*(p - q)) <= merge_tol for q in keep):
                keep.append(p)
        out[key] = np.array(sorted(keep, key=lambda t: t[0]))
    return out



def vector_items(page, clip, min_size=1.0, max_size=8.0):
    """Small drawing items (marker parts) inside clip, as dicts with centre, size and
    colours, for figures whose markers are built from several items (e.g. a coloured disc
    with a white inner disc for an open marker)."""
    out = []
    for d in page.get_drawings():
        r = d["rect"]
        if not clip.contains(r):
            continue
        if not (min_size <= r.width <= max_size and min_size <= r.height <= max_size):
            continue
        out.append({"x": 0.5 * (r.x0 + r.x1), "y": 0.5 * (r.y0 + r.y1),
                    "w": r.width, "h": r.height,
                    "fill": tuple(round(v, 3) for v in d["fill"]) if d.get("fill") else None,
                    "stroke": tuple(round(v, 3) for v in d["color"]) if d.get("color") else None})
    return out


def concentric_markers(items, outer_size, inner_size, size_tol=0.25, centre_tol=0.3):
    """Markers drawn as an outer disc in the series colour plus an inner disc that is white
    (open marker) or the series colour (filled marker). Returns
    {colour: {"filled": array (x, y), "open": array (x, y)}}."""
    outer = [i for i in items if i["fill"] and abs(i["w"] - outer_size) <= size_tol
             and abs(i["h"] - outer_size) <= size_tol]
    inner = [i for i in items if i["fill"] and abs(i["w"] - inner_size) <= size_tol
             and abs(i["h"] - inner_size) <= size_tol]
    out: dict = {}
    for o in outer:
        if o["fill"] == (1.0, 1.0, 1.0):
            continue
        match = [i for i in inner if abs(i["x"] - o["x"]) <= centre_tol and abs(i["y"] - o["y"]) <= centre_tol]
        kind = "open" if any(m["fill"] == (1.0, 1.0, 1.0) for m in match) else "filled"
        out.setdefault(o["fill"], {"filled": [], "open": []})[kind].append((o["x"], o["y"]))
    return {c: {k: np.array(v).reshape(-1, 2) for k, v in d.items()} for c, d in out.items()}

# ---------------------------------------------------------------- raster figures


def load_page_image(page, xref=None, clip=None, dpi=300):
    """RGB float image in [0, 1]. With xref, the embedded image at its native resolution
    (preferred: no resampling); otherwise the page (or clip) rendered at dpi."""
    import fitz

    if xref is not None:
        pix = fitz.Pixmap(page.parent, xref)
        if pix.n - pix.alpha != 3:
            pix = fitz.Pixmap(fitz.csRGB, pix)
    else:
        pix = page.get_pixmap(dpi=dpi, clip=clip)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    return a[..., :3].astype(np.float64) / 255.0


def snap_ticks(img, approx, axis, frame, search=4, dark=0.75, length=(2, 12)):
    """Refine approximate tick pixel positions to the centre of the nearest tick mark.

    approx: approximate positions (columns for axis="x", rows for axis="y"), e.g. read by
    eye from the image. frame: the pixel row (x) or column (y) of the axis line. A tick is a
    run of dark pixels perpendicular to the axis line, starting next to it, inside or
    outside the frame. Raises if a tick is not found within +-search pixels, so a wrong
    reading fails loudly instead of biasing the calibration.
    """
    g = img.mean(-1) < dark
    out = []
    for c in approx:
        best = None
        for d in range(-search, search + 1):
            k = int(round(c)) + d
            if axis == "x":
                strip_out = g[frame + 1: frame + 1 + length[1], k]
                strip_in = g[max(0, frame - length[1]): frame, k][::-1]
            else:
                strip_out = g[k, max(0, frame - length[1]): frame][::-1]
                strip_in = g[k, frame + 1: frame + 1 + length[1]]
            run = max(_leading_run(strip_out), _leading_run(strip_in))
            if run >= length[0] and (best is None or run > best[1] or
                                     (run == best[1] and abs(d) < abs(best[0] - c))):
                best = (k, run)
        if best is None:
            raise ValueError(f"no tick near {c} on the {axis} axis")
        # subpixel: darkness-weighted centre over the tick's width
        k = best[0]
        lo, hi = k - 2, k + 3
        if axis == "x":
            prof = 1.0 - img[frame + 1: frame + 1 + length[0], lo:hi].mean(-1).mean(0)
        else:
            prof = 1.0 - img[lo:hi, frame - length[0]: frame].mean(-1).mean(1)
        prof = np.clip(prof - prof.min(), 0, None)
        out.append(lo + float((prof * np.arange(len(prof))).sum() / prof.sum()) if prof.sum() > 0 else float(k))
    return np.array(out)


def _leading_run(v):
    n = 0
    for x in v:
        if not x:
            break
        n += 1
    return n


def find_frame_line(img, approx, axis, search=6, dark=0.75):
    """Row (axis="x": horizontal axis line) or column (axis="y") with the most dark pixels
    within +-search of approx."""
    g = img.mean(-1) < dark
    idx = range(int(approx) - search, int(approx) + search + 1)
    counts = [g[i, :].sum() if axis == "x" else g[:, i].sum() for i in idx]
    return list(idx)[int(np.argmax(counts))]


def marker_template(img, colour, box, tol=0.18, open_px=0):
    """Binary footprint of one isolated marker (e.g. the legend's), cut from box =
    (r0, r1, c0, c1): the pixels of the marker colour, cropped to their bounding box.
    open_px > 0 removes thinner structures first (a legend line through the marker) by a
    morphological opening with a disc of that radius, then keeps the blob nearest the
    box centre."""
    from scipy import ndimage

    r0, r1, c0, c1 = box
    m = np.linalg.norm(img[r0:r1, c0:c1] - np.asarray(colour, float), axis=-1) < tol
    if open_px > 0:
        yy, xx = np.mgrid[-open_px:open_px + 1, -open_px:open_px + 1]
        m = ndimage.binary_opening(m, structure=np.hypot(yy, xx) <= open_px)
        lab, n = ndimage.label(m)
        if n > 1:
            cy, cx = (m.shape[0] - 1) / 2, (m.shape[1] - 1) / 2
            cents = ndimage.center_of_mass(m, lab, range(1, n + 1))
            k = int(np.argmin([np.hypot(a - cy, b_ - cx) for a, b_ in cents])) + 1
            m = lab == k
    rows, cols = np.nonzero(m)
    if rows.size == 0:
        raise ValueError("no marker pixels of that colour in the template box")
    return m[rows.min(): rows.max() + 1, cols.min(): cols.max() + 1]


def raster_markers(img, colour, radius, mode="filled", tol=0.18, min_fill=0.6,
                   region=None, exclude=(), max_white_core=0.08, template=None, veto_open=True):
    """Centres (row, col) of circular-ish markers of one colour.

    The colour mask is convolved with a disc (mode="filled") or a ring (mode="ring") of the
    marker radius; peaks of the fill fraction above min_fill are markers. Thin lines and
    markers of the other mode give low fill and are rejected; partly covered markers keep
    a peak. region=(r0, r1, c0, c1) limits the search to the plot area; exclude is a list
    of such boxes (legend). Subpixel centres from the fill-weighted mean around each peak.
    """
    from scipy import ndimage
    from scipy.signal import fftconvolve

    mask = (np.linalg.norm(img - np.asarray(colour, float), axis=-1) < tol).astype(float)
    r = float(radius)
    R = int(np.ceil(r)) + 1
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
    dist = np.hypot(yy, xx)
    core = (dist <= max(1.0, 0.6 * r)).astype(float)
    if template is not None:
        # template matching with the figure's own marker footprint (any shape); the core
        # for the white check is the footprint eroded by about a third of its size
        if mode != "filled":
            raise ValueError("templates are for filled markers")
        ker = np.asarray(template, float)
        k = max(1, int(round(min(ker.shape) / 3)))
        core = ndimage.binary_erosion(ker > 0, iterations=k).astype(float)
        if core.sum() == 0:
            core = ker.copy()
        r = 0.5 * float(min(ker.shape))
    elif mode == "filled":
        ker = (dist <= r).astype(float)
    elif mode == "ring":
        ker = ((dist <= r) & (dist >= r - max(1.0, 0.35 * r))).astype(float)
        hole = (dist < max(0.5, r - max(1.0, 0.35 * r) - 1.0)).astype(float)
    else:
        raise ValueError(mode)
    fill = fftconvolve(mask, ker[::-1, ::-1] / ker.sum(), mode="same")  # correlation
    ok = fill >= min_fill
    if mode == "filled":
        # a filled marker has no white in its core; crowded open (white-faced) markers whose
        # coloured outlines merge into solid patches do (CORRECTIONS P3A-7)
        white = (img.min(-1) > 0.9).astype(float)
        ok &= fftconvolve(white, core[::-1, ::-1] / core.sum(), mode="same") <= max_white_core
    if mode == "ring":
        inner = fftconvolve(mask, hole / max(hole.sum(), 1.0), mode="same")
        ok &= inner <= 0.35
    if region is not None:
        r0, r1, c0, c1 = region
        lim = np.zeros_like(ok)
        lim[r0:r1, c0:c1] = True
        ok &= lim
    for r0, r1, c0, c1 in exclude:
        ok[r0:r1, c0:c1] = False
    peak = (fill == ndimage.maximum_filter(fill, size=max(3, int(round(1.2 * r))))) & ok
    rows, cols = np.nonzero(peak)
    # merge plateaus (several equal maxima of one marker)
    pts = []
    for y, x in sorted(zip(rows, cols), key=lambda t: -fill[t]):
        if all(np.hypot(y - py, x - px) > 0.9 * r for py, px in pts):
            pts.append((y, x))
    out = []
    w = max(1, int(round(0.6 * r)))
    for y, x in pts:
        sl = fill[max(0, y - w): y + w + 1, max(0, x - w): x + w + 1]
        sy, sx = np.mgrid[max(0, y - w): y + w + 1, max(0, x - w): x + w + 1]
        wgt = np.clip(sl - min_fill * 0.9, 0, None)
        out.append((float((wgt * sy).sum() / wgt.sum()), float((wgt * sx).sum() / wgt.sum())))
    if template is not None and veto_open and out:
        # open-marker veto: an open marker of this colour (outline in the colour, white core)
        # centred at a detection makes that detection ambiguous; drop it (CORRECTIONS P3A-7)
        ring = np.clip(ker - core, 0, 1)
        ring_fill = fftconvolve(mask, ring[::-1, ::-1] / max(ring.sum(), 1.0), mode="same")
        white = (img.min(-1) > 0.9).astype(float)
        core_white = fftconvolve(white, core[::-1, ::-1] / core.sum(), mode="same")
        open_c = np.argwhere((ring_fill >= 0.5) & (core_white >= 0.5))
        if len(open_c):
            keep = []
            for y, x in out:
                d = np.hypot(open_c[:, 0] - y, open_c[:, 1] - x)
                if d.min() > 0.5 * r:
                    keep.append((y, x))
            out = keep
    if template is not None:
        # with mode="same", an even-sized footprint's centre lies half a pixel before the
        # output index: same[i] aligns template pixel m with image pixel i - ceil((h-1)/2) + m
        h_t, w_t = np.asarray(template).shape
        out = [(y - 0.5 * (h_t % 2 == 0), x - 0.5 * (w_t % 2 == 0)) for y, x in out]
    return np.array(sorted(out, key=lambda t: t[1])).reshape(-1, 2)
