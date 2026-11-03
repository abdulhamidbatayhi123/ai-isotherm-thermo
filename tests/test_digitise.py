"""The digitiser on a synthetic vector PDF with known points."""
import fitz
import numpy as np
import pytest

from p3a import digitise


def _make_pdf(tmp_path, xs, ys, colour=(0.8, 0.1, 0.1)):
    """A 'plot' with x axis 0..10 over 100..300 pt and y axis 0..1 over 400..200 pt."""
    doc = fitz.open()
    page = doc.new_page(width=400, height=500)
    for v in (0, 2, 4, 6, 8, 10):
        x = 100 + 20 * v
        page.draw_line((x, 400), (x, 403), width=0.2)
        page.insert_text((x - 2.5, 415), str(v), fontsize=7)
    for v in ("0", "0.5", "1"):
        y = 400 - 200 * float(v)
        page.draw_line((97, y), (100, y), width=0.2)
        page.insert_text((80, y + 2.5), v, fontsize=7)
    for x, y in zip(xs, ys):
        cx, cy = 100 + 20 * x, 400 - 200 * y
        page.draw_rect(fitz.Rect(cx - 1.5, cy - 1.5, cx + 1.5, cy + 1.5), color=colour, fill=colour)
    path = tmp_path / "plot.pdf"
    doc.save(path)
    return fitz.open(path)[0]


def test_vector_digitiser_recovers_known_points(tmp_path):
    xs = np.array([0.5, 1.7, 3.3, 5.0, 7.25, 9.9])
    ys = np.array([0.05, 0.2, 0.41, 0.66, 0.83, 0.97])
    page = _make_pdf(tmp_path, xs, ys)
    xa = digitise.vector_axis(page, fitz.Rect(90, 404, 320, 420), "x", tick_clip=fitz.Rect(90, 399, 320, 404))
    ya = digitise.vector_axis(page, fitz.Rect(70, 190, 96, 410), "y", tick_clip=fitz.Rect(95, 190, 101, 410))
    m = digitise.vector_markers(page, fitz.Rect(101, 150, 320, 399))
    assert len(m) == 1
    pts = next(iter(m.values()))
    assert len(pts) == len(xs)
    assert np.allclose(xa(pts[:, 0]), xs, atol=1e-3)
    assert np.allclose(ya(pts[:, 1]), ys, atol=1e-3)
    assert xa.residual < 0.05 and ya.residual < 0.05


def test_fit_axis_needs_two_ticks_and_reports_residual():
    with pytest.raises(ValueError):
        digitise.fit_axis([1.0], [0.0])
    ax = digitise.fit_axis([0, 10, 20], [0, 1, 2.2])
    assert ax.residual > 0
    lg = digitise.fit_axis([0, 10, 20], [1, 10, 100], log=True)
    assert np.isclose(lg(10), 10.0)


def test_a_corner_label_of_the_other_axis_is_not_taken(tmp_path):
    """The y axis's '0' label sits at the corner and its text box touches the x-label strip."""
    xs = np.array([1.0, 5.0, 9.0])
    ys = np.array([0.1, 0.5, 0.9])
    page = _make_pdf(tmp_path, xs, ys)
    page.insert_text((88, 409), "0", fontsize=7)  # an extra corner label, as in many plots
    xa = digitise.vector_axis(page, fitz.Rect(95, 405, 320, 420), "x", tick_clip=fitz.Rect(90, 399, 320, 404))
    assert xa.n_ticks == 6 and xa.residual < 0.05


@pytest.mark.parametrize("frame_width", [1, 4])
@pytest.mark.parametrize("width", [1, 3, 7])
@pytest.mark.parametrize("side", ["out", "in"])
def test_snap_ticks_centres_thick_and_thin_ticks_on_either_side(width, side, frame_width):
    """A tick of any width, inside or outside a thin or thick frame line, is centred between
    its edges, even when the reading by eye is off by several pixels."""
    img = np.ones((120, 300, 3))
    frame = 60
    img[frame - frame_width // 2: frame - frame_width // 2 + frame_width, :, :] = 0.0  # axis line
    f_lo, f_hi = frame - frame_width // 2, frame - frame_width // 2 + frame_width - 1
    true_centres = [50.0, 150.0, 250.0]
    for c in true_centres:
        lo = int(c - (width - 1) / 2)
        rows = slice(f_hi + 1, f_hi + 9) if side == "out" else slice(f_lo - 8, f_lo)
        img[rows, lo: lo + width, :] = 0.0
    got = digitise.snap_ticks(img, [c + 3 for c in true_centres], "x", frame, search=6)
    expected = [int(c - (width - 1) / 2) + (width - 1) / 2 for c in true_centres]
    assert np.allclose(got, expected, atol=0.05)
