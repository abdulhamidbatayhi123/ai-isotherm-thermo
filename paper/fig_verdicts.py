"""Figure: the confirmatory verdicts, drawn only from a verdicts file written by scripts/analyse.py.

a  H1: for each comparison, the Hodges-Lehmann ratio R = E_P / E_X (log axis; R < 1 means P
   extrapolates better) with its exact 95 % interval (thin) and 90 % interval (thick), the
   per-material ratios 10**d_m as small points, and the 25 % band (0.8 to 1.25) of the smallest
   effect of interest. H1a is descriptive (PREREG 7.1) and drawn open; the class words printed
   at the right are the ones in the file, not re-derived here.
   Review R4: the primary H1b is drawn first and the descriptive H1a last, below a rule; for H1b the
   post hoc check with every error replaced by its median over the seeds (results/descriptive_seeds.json,
   ledger X-1) is drawn as an open diamond below the confirmatory estimate.
b  H3: fraction of the extrapolation fits (E-high, E-low) with a thermodynamic violation inside
   the measured domain, per model cell, with its Wilson 95 % interval and the counts; below a rule,
   post hoc, V-pen with the monotonicity weight chosen on the development materials
   (results/vpen_weight_summary.json, ledger X-8 a).

Nothing is computed from fits here: every number comes from the verdicts and summary files (the Wilson
interval of the post hoc row is computed from its count with the formula of scripts/analyse.py).

  python paper/fig_verdicts.py results/verdicts_confirmatory.json [out_stem]
      default out_stem: paper/figures/fig_verdicts
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "paper"))
import figstyle as fs  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402

WORDS = {"P_better": "P better", "X_better": "X better", "equivalent": "equivalent",
         "differ_small": "differ < 25 %", "inconclusive": "inconclusive"}
H3_ORDER = ("P", "V-pen", "V-none", "F-hard", "F-pen", "F-none", "A-hard", "A-pen", "C1")
DSD = ROOT / "results/descriptive_seeds.json"
VW = ROOT / "results/vpen_weight_summary.json"


def rows(v):
    out = []
    for h in ("H1b", "H1c", "H1d", "H1e"):
        if h in v.get("H1", {}):
            out.append((h, v["H1"][h], False))
    if "H1a" in v.get("descriptive", {}):
        out.append(("H1a", v["descriptive"]["H1a"], True))
    return out


def panel_h1(ax, v):
    rs = rows(v)
    ax.axvspan(0.8, 1.25, color=fs.OI["light"], lw=0, zorder=0)
    ax.axvline(1.0, color=fs.ROLE["muted"], lw=0.6, zorder=1)
    rng = np.random.default_rng(0)  # fixed jitter of the material points only
    for i, (h, r, desc) in enumerate(rs):
        y = len(rs) - 1 - i
        d = np.array(list(r["d_by_material"].values()), float)
        jit = rng.uniform(-0.06, 0.06, d.size)
        ax.scatter(10**d, y + 0.28 + jit, s=3, color=fs.ROLE["muted"], lw=0, zorder=2)
        # review R3 m11: mark COF-SO3H, which drives the spread, with one symbol in every row
        names = list(r["d_by_material"])
        k = [j for j, n in enumerate(names) if n.startswith("COF-SO3H")][0]
        ax.scatter([10 ** d[k]], [y + 0.28 + jit[k]], s=14, marker="^", facecolors="none",
                   edgecolors=fs.OI["dark"], lw=0.6, zorder=3, label="COF-SO$_3$H" if i == 0 else None)
        lo95, hi95 = r["R_ci95"]
        lo90, hi90 = r["R_ci90"]
        ax.plot([lo95, hi95], [y, y], color=fs.OI["dark"], lw=0.6, zorder=3)
        ax.plot([lo90, hi90], [y, y], color=fs.OI["dark"], lw=1.8, zorder=3, solid_capstyle="butt")
        ax.plot([r["R"]], [y], marker="o", ms=4, zorder=4, mec=fs.OI["dark"], mew=0.8,
                mfc="white" if desc else fs.OI["blue"])
        if h == "H1b":   # post hoc: every error replaced by its median over the seeds (ledger X-1)
            xm = json.loads(DSD.read_text())["exploratory_median_over_seeds"]["H1b"]
            yx = y - 0.30
            ax.plot(xm["R_ci95"], [yx, yx], color=fs.ROLE["muted"], lw=0.6, zorder=3)
            ax.plot([xm["R"]], [yx], marker="D", ms=3, zorder=4, mec=fs.OI["dark"], mew=0.6, mfc="white",
                    label="seed median (post hoc)")
        if desc:
            ax.axhline(y + 0.5, color=fs.ROLE["muted"], lw=0.5, ls="--", zorder=1)
        word = "descriptive" if desc else WORDS.get(r["class"], r["class"])
        ax.text(1.02, y, f"{word}\nR {r['R']:.2f} [{lo95:.2f}, {hi95:.2f}]", transform=ax.get_yaxis_transform(),
                va="center", ha="left", fontsize=fs.SMALL_PT)
    ax.set_xscale("log")
    from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator
    allv = [x for _, r, _ in rs for x in (*r["R_ci95"], *(10**np.array(list(r["d_by_material"].values()))))]
    lo, hi = min(allv + [0.5]), max(allv + [2.0])
    ax.set_xlim(lo / 1.15, hi * 1.15)
    ticks = [x for x in (0.05, 0.1, 0.2, 0.5, 0.8, 1.0, 1.25, 2.0, 5.0, 10.0, 20.0) if lo / 1.15 <= x <= hi * 1.15]
    ax.xaxis.set_major_locator(FixedLocator(ticks))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:g}"))
    ax.set_yticks(range(len(rs)))
    ax.set_yticklabels([f"{h}  P vs {r['X']}" for h, r, _ in reversed(rs)])  # comparator from the file
    ax.set_ylim(-0.6, len(rs) - 0.3)
    ax.set_xlabel("Error ratio R = E$_P$ / E$_X$ (log; < 1: P better)")
    ax.tick_params(axis="y", length=0)
    ax.legend(loc="lower right", fontsize=fs.SMALL_PT, handletextpad=0.3, borderaxespad=0.1)
    ax.spines["left"].set_visible(False)


def wilson(k, n, z=1.959964):   # as scripts/analyse.py
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [max(0.0, c - h), min(1.0, c + h)]


def panel_h3(ax, v):
    cells = dict(v["H3"]["cells"])
    names = [c for c in H3_ORDER if c in cells]
    vw = json.loads(VW.read_text()).get("selected_on_development") if VW.exists() else None
    if vw:
        k, n = vw["violating_in_domain"], vw["fits"]
        cells["V-pen, heavy"] = {"fraction": k / n, "wilson95": wilson(k, n), "violating_in_domain": k, "fits": n}
        names.append("V-pen, heavy")
    for i, c in enumerate(names):
        y = len(names) - 1 - i
        r = cells[c]
        st = fs.CELL["V-pen"] if c == "V-pen, heavy" else fs.CELL[c]
        if c == "V-pen, heavy":
            ax.axhline(y + 0.5, color=fs.ROLE["muted"], lw=0.5, ls="--")
        lo, hi = r["wilson95"]
        ax.plot([lo, hi], [y, y], color=st["color"], lw=1.2)
        ax.plot([r["fraction"]], [y], marker=st["marker"], color="white" if c == "V-pen, heavy" else st["color"],
                ms=4, mec=fs.OI["dark"], mew=0.4)
        ax.text(1.08, y, f"{r['violating_in_domain']}/{r['fits']}", ha="left", va="center",
                fontsize=fs.SMALL_PT, transform=ax.get_yaxis_transform())
    ax.axvline(0.2, color=fs.ROLE["muted"], lw=0.6, ls=":")
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels([n.replace("V-pen, heavy", "V-pen, heavier
weight (post hoc)") for n in reversed(names)])
    ax.tick_params(axis="y", length=0)
    ax.set_ylim(-0.6, len(names) - 0.4)
    ax.set_xlim(-0.02, 1.02)
    ax.set_xlabel("Extrapolation fits with a violation")


def main():
    src = Path(sys.argv[1])
    stem = sys.argv[2] if len(sys.argv) > 2 else str(ROOT / "paper/figures/fig_verdicts")
    v = json.loads(src.read_text())
    fs.apply()
    fig = plt.figure(figsize=(fs.W2, 70 * fs.MM))
    ax1 = fig.add_axes([0.12, 0.17, 0.40, 0.76])
    ax2 = fig.add_axes([0.76, 0.17, 0.19, 0.76])
    panel_h1(ax1, v)
    panel_h3(ax2, v)
    fs.letter(ax1, "a", x=-0.27)
    fs.letter(ax2, "b", x=-0.30)
    print(fs.save(fig, stem, inputs=[str(src), str(DSD), str(VW)]))


if __name__ == "__main__":
    main()
