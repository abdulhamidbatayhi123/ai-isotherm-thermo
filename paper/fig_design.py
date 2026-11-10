"""Figure 1: the design (schematic, drawn in code; no data, no fit).

a  the idea: one potential psi(s, T), s = ln p, gives the isotherm q* = d psi / d s and the
   isosteric heat from the same function; curves are illustrative (one Langmuir and one
   cooperative Sips term with van't Hoff affinities, not fitted to anything);
b  the 3 x 3 factorial of PREREG_P3A.md section 4, the extra comparators C1 and F-rel, and
   the comparisons of section 7.1: H1b (primary, non-inferiority) to H1e confirmatory under
   Holm, H1a descriptive since P3A-21;
c  the tasks E-high and E-low (section 5.1) and what is scored (sections 6.1 to 6.3).

An automatic layout check runs before saving: no two texts overlap, every text owned by a box
lies inside it, no other text touches a box, and no arrow or curve passes through a text.

  python paper/fig_design.py      -> paper/figures/fig_design.{pdf,png,prov.json}
"""
import sys
from itertools import combinations
from pathlib import Path

import warnings

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "paper"))
import figstyle as fs  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402
from matplotlib.text import Text  # noqa: E402
from matplotlib.transforms import Bbox  # noqa: E402

W_MM, H_MM = 183.0, 110.0   # layout units (mm at 183 mm width); drawn at fs.W2 wide (ACS 7.0 in), same aspect
R = 8.314
INK = fs.OI["dark"]
T_COLD, T_HOT = 283.0, 318.0
TXT = 6.0       # body text in the schematic
SM = 5.5        # small text
SUB_PT = 6.0    # smallest size of a text with a sub- or superscript (script at 0.85 x 6.0 = 5.1 pt)

# ---------------------------------------------------------------- illustrative potential
TERMS = [  # (capacity, exponent g, K at 283 K in 1/Pa, Q in J/mol)
    (0.30, 1.0, 1 / 120.0, 60e3),
    (0.70, 2.0, 1 / 500.0, 46e3),
]


def _K(K283, Q, T):
    return K283 * np.exp(Q / R * (1 / T - 1 / 283.0))


def psi(s, T):
    return sum(qm / g * np.log1p((_K(K, Q, T) * np.exp(s)) ** g) for qm, g, K, Q in TERMS)


def qstar(s, T):
    out = 0.0
    for qm, g, K, Q in TERMS:
        y = (_K(K, Q, T) * np.exp(s)) ** g
        out = out + qm * y / (1 + y)
    return out


def qst_curve(T, s):
    h_s, h_T = 1e-4, 1e-3
    dq_ds = (qstar(s + h_s, T) - qstar(s - h_s, T)) / (2 * h_s)
    dq_dT = (qstar(s, T + h_T) - qstar(s, T - h_T)) / (2 * h_T)
    return qstar(s, T), -R * T ** 2 * dq_dT / dq_ds / 1e3


# ---------------------------------------------------------------- canvas with checks
class Canvas:
    def __init__(self):
        fs.apply()
        self.fig = plt.figure(figsize=(fs.W2, fs.W2 * H_MM / W_MM))
        ax = self.fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, W_MM)
        ax.set_ylim(0, H_MM)
        ax.axis("off")
        self.ax = ax
        self.boxes = []          # (x, y, w, h, [texts])
        self.paths = []          # (transform, Nx2 points) for arrows and curves
        self.owned = set()

    def box(self, x, y, w, h, fc="white", ec=INK, lw=0.6, ls="-"):
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.8",
                                         fc=fc, ec=ec, lw=lw, ls=ls, zorder=2))
        self.boxes.append((x, y, w, h, []))
        return len(self.boxes) - 1

    def text(self, x, y, s, size=TXT, owner=None, ha="center", va="center", **kw):
        # a text with a sub- or superscript is drawn at SUB_PT or larger, so that its script
        # (fs.SCRIPT_SHRINK of the text) prints at 5 pt or more; figstyle.save measures it
        if "$" in s and ("_" in s or "^" in s):
            size = max(size, SUB_PT)
        t = self.ax.text(x, y, s, fontsize=size, ha=ha, va=va, color="#000000", zorder=5, **kw)
        if owner is not None:
            self.boxes[owner][4].append(t)
            self.owned.add(t)
        return t

    def arrow(self, p0, p1, rad=0.0, lw=0.7, color=INK, style="-|>", ms=5, ls="-"):
        a = FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=ms, lw=lw, color=color,
                            connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0, ls=ls,
                            zorder=4)
        self.ax.add_patch(a)
        (x1, y1), (x2, y2) = p0, p1
        cx, cy = (x1 + x2) / 2 + rad * (y2 - y1), (y1 + y2) / 2 - rad * (x2 - x1)
        t = np.linspace(0, 1, 60)[:, None]
        pts = (1 - t) ** 2 * np.array(p0) + 2 * t * (1 - t) * np.array([cx, cy]) + t ** 2 * np.array(p1)
        self.paths.append((self.ax.transData, pts))
        return pts[30]           # apex of the curve, for its label

    def curve(self, ax, x, y, **kw):
        ax.plot(x, y, **kw)
        self.paths.append((ax.transData, np.column_stack([x, y])))

    def check(self):
        """Assert the layout rules; returns the number of texts checked."""
        fig = self.fig
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        texts = [t for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()]
        bb = {t: t.get_window_extent(r) for t in texts}
        fb = fig.bbox
        errors = []
        for t in texts:
            b = bb[t]
            if b.x0 < fb.x0 or b.y0 < fb.y0 or b.x1 > fb.x1 or b.y1 > fb.y1:
                errors.append(f"outside figure: {t.get_text()!r}")
        for a, b in combinations(texts, 2):
            if bb[a].overlaps(bb[b]):
                errors.append(f"overlap: {a.get_text()!r} / {b.get_text()!r}")
        pad = 0.5 * fs.MM * fig.dpi   # 0.5 mm clearance inside a box
        to_px = self.ax.transData
        for x, y, w, h, own in self.boxes:
            (X0, Y0), (X1, Y1) = to_px.transform([(x, y), (x + w, y + h)])
            inner = Bbox([[X0 + pad, Y0 + pad], [X1 - pad, Y1 - pad]])
            outer = Bbox([[X0, Y0], [X1, Y1]])
            for t in own:
                b = bb[t]
                if not (b.x0 >= inner.x0 and b.x1 <= inner.x1 and b.y0 >= inner.y0 and b.y1 <= inner.y1):
                    errors.append(f"leaves its box: {t.get_text()!r}")
            for t in texts:
                if t not in own and bb[t].overlaps(outer):
                    errors.append(f"touches a box it does not belong to: {t.get_text()!r}")
        shrink = 0.3 * fig.dpi / 72
        for tr, pts in self.paths:
            P = tr.transform(pts)
            for t in texts:
                b = bb[t]
                inside = ((P[:, 0] > b.x0 + shrink) & (P[:, 0] < b.x1 - shrink)
                          & (P[:, 1] > b.y0 + shrink) & (P[:, 1] < b.y1 - shrink))
                if inside.any():
                    errors.append(f"line through text: {t.get_text()!r}")
        assert not errors, "layout check failed:\n  " + "\n  ".join(errors)
        return len(texts)


def letter(cv, s, x_mm, y_mm):
    fs.letter(cv.ax, s, x=x_mm / W_MM, y=y_mm / H_MM)


# ---------------------------------------------------------------- panel a
def panel_a(cv):
    letter(cv, "a", 1.0, 104.5)
    cv.text(6.0, 106.2, "One potential gives the isotherm and the heat (curves illustrative)",
            size=TXT, ha="left")
    s = np.linspace(np.log(1.0), np.log(2.0e4), 300)
    cols = {T: fs.temp_colour(T) for T in (T_COLD, T_HOT)}
    W, Hh, y0 = 17.0, 17.0, 78.0
    xs = [7.0, 34.5, 62.0]
    axs = []
    for x in xs:
        a = cv.fig.add_axes([x / W_MM, y0 / H_MM, W / W_MM, Hh / H_MM])
        a.set_xticks([])
        a.set_yticks([])
        axs.append(a)
    # potential
    for T in (T_COLD, T_HOT):
        cv.curve(axs[0], s, psi(s, T), color=cols[T], lw=1.1)
    axs[0].set_title("potential ψ(s, T)", fontsize=TXT, loc="center", pad=3)
    axs[0].set_xlabel("s = ln p", fontsize=SM, labelpad=2)
    axs[0].set_xlim(s[0], s[-1])
    axs[0].set_ylim(0, None)
    # isotherm
    for T in (T_COLD, T_HOT):
        cv.curve(axs[1], s, qstar(s, T), color=cols[T], lw=1.1)
    axs[1].set_title("isotherm q* = ∂ψ/∂s", fontsize=TXT, loc="center", pad=3)
    axs[1].set_xlabel("s = ln p", fontsize=SM, labelpad=2)
    axs[1].set_xlim(s[0], s[-1])
    axs[1].set_ylim(0, 1.08)
    # temperature key under the plots (labels inside the small axes collided with the curves)
    xk = 22.0
    for T in (T_COLD, T_HOT):
        cv.ax.plot([xk, xk + 4.0], [71.0, 71.0], color=cols[T], lw=1.1)
        cv.text(xk + 5.0, 71.0, f"{T:.0f} K", size=SM, ha="left")
        xk += 14.0
    cv.text(xk, 71.0, "(heat shown at 283 K)", size=SM, ha="left")
    # heat
    sd = np.linspace(np.log(0.5), np.log(3.0e3), 400)
    q, Q = qst_curve(T_COLD, sd)
    m = (q > 0.03) & (q < 0.85)
    cv.curve(axs[2], q[m], Q[m], color=cols[T_COLD], lw=1.1)
    axs[2].set_title("heat $Q_{st}$(q)", fontsize=TXT, loc="center", pad=3)
    axs[2].set_xlabel("uptake q", fontsize=SM, labelpad=2)
    axs[2].set_xlim(0, 1.0)
    axs[2].set_ylim(Q[m].min() - 4, Q[m].max() + 5)
    # arrows between the plots
    ym = y0 + Hh / 2
    cv.arrow((xs[0] + W + 1.5, ym), (xs[1] - 1.5, ym))
    cv.text((xs[0] + W + xs[1]) / 2, ym + 1.4, "∂/∂s", size=SM, va="bottom")
    cv.arrow((xs[1] + W + 1.5, ym), (xs[2] - 1.5, ym))
    cv.text((xs[1] + W + xs[2]) / 2, ym + 1.4, "∂/∂T", size=SM, va="bottom")
    cv.text((xs[1] + W + xs[2]) / 2, ym - 1.4, "at fixed q", size=SM, va="top")
    # what holds by construction
    bx = cv.box(4.0, 42.0, 76.0, 25.0, fc="#F4F4F4", ec=INK, lw=0.5)
    x0 = 6.0
    cv.text(x0, 64.0, "Holds by construction, for every parameter value", owner=bx,
            ha="left", va="center", fontweight="bold")
    lines = [
        "•  monotone in p:  ∂q*/∂s = ∂²ψ/∂s² > 0, because ψ is convex in s",
        "•  Henry limit:  q* grows in proportion to p as p → 0",
        "•  heat always finite:  $Q_{st}$ = −RT² (∂q*/∂T) / (∂q*/∂s),",
        "    denominator never zero; sign and size not constrained",
        "In P each term has a van't Hoff affinity $K_0$ exp(Q / RT), Q free in sign.",
        "Every model's heat is computed from its own isotherm by the same code.",
    ]
    for i, ln in enumerate(lines):
        cv.text(x0, 60.2 - 3.0 * i, ln, size=SM, owner=bx, ha="left")


# ---------------------------------------------------------------- panel b
def marker(cv, x, y, name):
    st = fs.CELL[name]
    cv.ax.plot([x], [y], marker=st["marker"], ms=3.6, mfc=st["color"], mec=INK, mew=0.4,
               zorder=6, ls="none")


def panel_b(cv):
    letter(cv, "b", 85.0, 104.5)
    cv.text(90.0, 106.2, "Factorial: shape constraint × temperature structure", ha="left")
    gx, cw, cg = 100.0, 18.0, 4.0          # grid left, cell width, gap
    rh, rg = 8.0, 4.0                      # row height, gap
    y_hard = 62.0
    rows = {"hard": y_hard, "penalty": y_hard + rh + rg, "none": y_hard + 2 * (rh + rg)}
    cols = {"F": gx, "V": gx + cw + cg, "A": gx + 2 * (cw + cg)}
    head = {"F": "F: free\nin 1/T", "V": "V: van't Hoff\nper term", "A": "A: characteristic\ncurve in A"}
    y_head = rows["none"] + rh + 4.6
    for c, x in cols.items():
        cv.text(x + cw / 2, y_head, head[c], size=SM, linespacing=1.1)
    cv.text(92.0, y_head, "shape\nconstraint", size=SM, linespacing=1.1)
    for r, y in rows.items():
        cv.text(92.0, y + rh / 2, r, size=SM)
    names = {("F", "none"): "F-none", ("F", "penalty"): "F-pen", ("F", "hard"): "F-hard",
             ("V", "none"): "V-none", ("V", "penalty"): "V-pen", ("V", "hard"): "P",
             ("A", "none"): "A-none", ("A", "penalty"): "A-pen", ("A", "hard"): "A-hard"}
    centre = {}
    for (c, r), nm in names.items():
        x, y = cols[c], rows[r]
        if nm == "P":
            b = cv.box(x, y, cw, rh, fc="#D9EAF6", ec=fs.CELL["P"]["color"], lw=1.3)
            cv.text(x + cw / 2 + 1.6, y + rh / 2 + 1.3, "P", owner=b, size=7, fontweight="bold")
            cv.text(x + cw / 2 + 1.6, y + rh / 2 - 1.7, "(= V-hard)", owner=b, size=SM)
        else:
            b = cv.box(x, y, cw, rh)
            cv.text(x + cw / 2 + 1.6, y + rh / 2, nm, owner=b)
        if nm in fs.CELL:
            marker(cv, x + 2.6, y + rh / 2, nm)
        centre[nm] = (x + cw / 2, y + rh / 2)
    # other comparators
    cx, cwid = 167.0, 15.0
    cv.text(cx + cwid / 2, y_head, "other\ncomparators", size=SM, linespacing=1.1)
    b = cv.box(cx, rows["none"] - 1.5, cwid, rh + 1.5, ls=(0, (2, 1.2)))
    cv.text(cx + cwid / 2 + 1.4, rows["none"] + rh - 1.6, "F-rel", owner=b)
    cv.text(cx + cwid / 2, rows["none"] + 2.4, "MLP on\nln(p/$p_{sat}$)", owner=b, size=5.0,
            linespacing=1.15)
    marker(cv, cx + 2.0, rows["none"] + rh - 1.6, "F-rel")
    cv.text(cx + cwid / 2, rows["none"] - 3.6, "descriptive", size=5.0)
    b = cv.box(cx, y_hard - 1.5, cwid, rh + 1.5)
    cv.text(cx + cwid / 2 + 1.4, y_hard + rh - 1.6, "C1", owner=b)
    cv.text(cx + cwid / 2, y_hard + 2.4, "dual-site Sips,\nvan't Hoff", owner=b, size=5.0, linespacing=1.15)
    marker(cv, cx + 2.0, y_hard + rh - 1.6, "C1")
    # confirmatory comparisons from P
    px, py = centre["P"]
    xV = cols["V"]
    # H1b: straight up to V-pen
    cv.arrow((px, y_hard + rh), (px, rows["penalty"]))
    cv.text(px + 1.0, y_hard + rh + rg / 2, "H1b", size=SM, ha="left")
    # H1d: a straight line up the F/V column gap, corner of P to corner of F-none
    cv.arrow((xV + 0.6, y_hard + rh), (cols["F"] + cw - 0.6, rows["none"]))
    cv.text(cols["F"] + cw - 2.6, rows["penalty"] + rh + rg / 2, "H1d", size=SM, ha="right")
    # H1a, H1c, H1e: arcs below the grid
    a = cv.arrow((px - 3.0, y_hard), (centre["F-hard"][0], y_hard), rad=-0.45, ls=(0, (3, 2)))  # descriptive: dashed
    cv.text(a[0], a[1] - 0.6, "H1a", size=SM, va="top")
    a = cv.arrow((px + 3.0, y_hard), (centre["A-hard"][0], y_hard), rad=0.35)
    cv.text(a[0], a[1] - 0.6, "H1c", size=SM, va="top")
    a = cv.arrow((px, y_hard), (cx + cwid / 2, y_hard - 1.5), rad=0.5)
    cv.text(a[0], a[1] - 0.6, "H1e", size=SM, va="top")
    # key
    ky = 44.0
    cv.text(88.0, ky + 3.0, "Comparisons of P (H1b primary; H1c-H1e confirmatory, Holm over H1b-H1e; H1a descriptive):", size=SM,
            ha="left", fontweight="bold")
    key = [("H1a", "against F-hard: temperature structure"),
           ("H1b", "against V-pen: hard against penalty"),
           ("H1c", "against A-hard: characteristic curve"),
           ("H1d", "against F-none: generic network"),
           ("H1e", "against C1: classical dual-site Sips")]
    for i, (h, s) in enumerate(key):
        col, row = divmod(i, 3)
        x = 88.0 + 47.5 * col
        y = ky - 2.6 * row
        cv.text(x, y, h, size=SM, ha="left", fontweight="bold")
        cv.text(x + 5.0, y, s, size=SM, ha="left")


# ---------------------------------------------------------------- panel c
def panel_c(cv):
    letter(cv, "c", 1.0, 33.0)
    cv.text(6.0, 34.7, "Tasks and scores (per material, temperatures $T_1$ < ... < $T_k$)", ha="left")
    xT = [26.0, 34.0, 42.0, 50.0]
    labs = ["$T_1$", "$T_2$", "...", "$T_k$"]
    c_train = fs.CELL["P"]["color"]
    for y, held, name, words in [(25.0, 3, "E-high", "predict the highest"),
                                 (13.0, 0, "E-low", "predict the lowest")]:
        cv.text(5.0, y, name, ha="left", fontweight="bold")
        cv.ax.plot([xT[0] - 3, xT[-1] + 3], [y, y], color=fs.ROLE["muted"], lw=0.5, zorder=3)
        cv.paths.append((cv.ax.transData, np.array([[xT[0] - 3, y], [xT[-1] + 3, y]])))
        for i, (x, lb) in enumerate(zip(xT, labs)):
            if lb == "...":
                cv.text(x, y + 0.6, "...", size=SM, va="center",
                        bbox=dict(fc="white", ec="none", pad=0.2))
                continue
            filled = i != held
            cv.ax.plot([x], [y], "o", ms=4.2, mfc=c_train if filled else "white",
                       mec=c_train, mew=0.9, zorder=6)
            cv.text(x, y - 2.0, lb, size=SM, va="top")
        cv.text(xT[-1] + 5.0, y, words, size=SM, ha="left")
    cv.ax.plot([6.0], [4.0], "o", ms=4.2, mfc=c_train, mec=c_train, mew=0.9)
    cv.text(8.0, 4.0, "training temperature", size=SM, ha="left")
    cv.ax.plot([34.0], [4.0], "o", ms=4.2, mfc="white", mec=c_train, mew=0.9)
    cv.text(36.0, 4.0, "held out", size=SM, ha="left")
    # what is scored
    cards = [
        ("Accuracy (H1, primary)",
         ["E = RMSE / $q_{ref}$ on the", "held-out isotherm;", "per material, the mean of",
          "log$_{10}$ E over E-high and", "E-low"]),
        ("Violations (H3)",
         ["grid to ±15 K, p ≤ 0.9 $p_{sat}$:", "uptake falling by more than",
          "0.02 $q_{ref}$ as p rises, or", "below −0.02 $q_{ref}$ (band to", "±20 K reported apart)"]),
        ("Heat (H2, synthetic)",
         ["$Q_{st}$ against the exact", "heat of five synthetic truths,", "at matched loading in",
          "0.1 to 0.9 $q_{ref}$, on the", "same tasks"]),
    ]
    x0, wc, gap = 93.0, 28.0, 2.0
    cv.text(x0 - 4.0, 21.0, "scored", size=SM, rotation=90)
    for i, (title, lines) in enumerate(cards):
        x = x0 + i * (wc + gap)
        b = cv.box(x, 8.5, wc, 24.5)
        cv.text(x + 1.5, 30.2, title, owner=b, ha="left", fontweight="bold", size=SM)
        for j, ln in enumerate(lines):
            cv.text(x + 1.5, 26.4 - 3.2 * j, ln, owner=b, ha="left", size=SM)


def main():
    warnings.filterwarnings("error", message="Glyph")  # a missing glyph is an error
    cv = Canvas()
    panel_a(cv)
    panel_b(cv)
    panel_c(cv)
    try:
        n = cv.check()
    except AssertionError:
        import os
        if os.environ.get("FIG_DEBUG_PNG"):   # look at a failing layout without saving it
            cv.fig.savefig(os.environ["FIG_DEBUG_PNG"], dpi=300)
        raise
    print(f"layout check passed: {n} texts, {len(cv.boxes)} boxes, {len(cv.paths)} lines")
    out = fs.save(cv.fig, str(ROOT / "paper/figures/fig_design"))
    print("wrote", *out)


if __name__ == "__main__":
    main()
