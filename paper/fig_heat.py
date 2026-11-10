"""Figure: the isosteric-heat verdicts (H2) on the synthetic truths, drawn only from a verdicts file
written by scripts/analyse.py (no argument: H1, H2 and H3).

One panel per comparator (V-pen, A-hard, F-none). In each, one row per truth family (KS, DA, FG, HS,
TC): the Hodges-Lehmann ratio R = RMSE(Qst)_P / RMSE(Qst)_X (log axis; R < 1 means P's heat is
closer to the exact heat) with its exact 95 % interval (thin) and 90 % interval (thick), the
per-material ratios 10**d_m as small points, the 25 % band (0.8 to 1.25), and at the right the class
word from the file and the number of materials on which X failed (P failed on none, checked here).

  python paper/fig_heat.py results/verdicts.json [out_stem]     default out_stem: paper/figures/fig_heat
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "paper"))
import figstyle as fs  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator  # noqa: E402

FAMILIES = ("KS", "DA", "FG", "HS", "TC")
COMPARATORS = ("V-pen", "A-hard", "F-none")
WORDS = {"P_better": "P better", "X_better": "X better", "equivalent": "equivalent",
         "differ_small": "differ < 25 %", "differ_uncertain": "differ", "inconclusive": "inconclusive"}


def panel(ax, v, X, show_labels):
    ax.axvspan(0.8, 1.25, color=fs.OI["light"], lw=0, zorder=0)
    ax.axvline(1.0, color=fs.ROLE["muted"], lw=0.6, zorder=1)
    rng = np.random.default_rng(0)  # fixed jitter of the material points only
    allv = []
    for i, fam in enumerate(FAMILIES):
        r = v["H2"][f"H2-{fam}-{X}"]
        assert r["X"] == X and r["failures"]["P"] == 0, (fam, X, r["failures"])
        y = len(FAMILIES) - 1 - i
        d = np.array(list(r["d_by_material"].values()), float)
        pts = 10**d
        allv += list(pts) + list(r["R_ci95"])
        ax.scatter(pts, y + 0.28 + rng.uniform(-0.06, 0.06, d.size), s=3, color=fs.ROLE["muted"], lw=0, zorder=2)
        lo95, hi95 = r["R_ci95"]
        lo90, hi90 = r["R_ci90"]
        ax.plot([lo95, hi95], [y, y], color=fs.OI["dark"], lw=0.6, zorder=3)
        ax.plot([lo90, hi90], [y, y], color=fs.OI["dark"], lw=1.8, zorder=3, solid_capstyle="butt")
        st = fs.CELL[X]
        ax.plot([r["R"]], [y], marker=st["marker"], ms=4, zorder=4, mec=fs.OI["dark"], mew=0.6, color=st["color"])
        word = f"{X} better" if r["class"] == "X_better" else WORDS.get(r["class"], r["class"])
        nf = r["failures"]["X"]
        ax.text(1.02, y, word + (f"\n{X} failed: {nf}" if nf else ""), transform=ax.get_yaxis_transform(),
                va="center", ha="left", fontsize=fs.SMALL_PT)
    lo, hi = min(allv + [0.5]), max(allv + [2.0])
    ax.set_xscale("log")
    ax.set_xlim(lo / 1.3, hi * 1.3)
    if hi / lo > 300:   # wide range: decades only, so that the labels do not collide
        cand = (0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0)
    else:
        cand = (0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0)
    ticks = [x for x in cand if lo / 1.3 <= x <= hi * 1.3]
    ax.xaxis.set_major_locator(FixedLocator(ticks))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:g}"))
    ax.set_yticks(range(len(FAMILIES)))
    ax.set_yticklabels(list(reversed(FAMILIES)) if show_labels else [])
    ax.set_ylim(-0.6, len(FAMILIES) - 0.3)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_title(f"P vs {X}", loc="left")
    ax.set_xlabel("R = RMSE(Q$_{st}$)$_P$ / RMSE(Q$_{st}$)$_X$")


def main():
    src = Path(sys.argv[1])
    stem = sys.argv[2] if len(sys.argv) > 2 else str(ROOT / "paper/figures/fig_heat")
    v = json.loads(src.read_text())
    fs.apply()
    fig = plt.figure(figsize=(fs.W2, 62 * fs.MM))
    axes = [fig.add_axes([0.05 + 0.325 * k, 0.21, 0.205, 0.68]) for k in range(3)]
    for k, (ax, X) in enumerate(zip(axes, COMPARATORS)):
        panel(ax, v, X, show_labels=(k == 0))
        fs.letter(ax, "abc"[k], x=-0.16 if k == 0 else -0.08)
    print(fs.save(fig, stem, inputs=[str(src)]))


if __name__ == "__main__":
    main()
