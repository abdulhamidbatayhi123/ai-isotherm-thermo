"""Table of Contents / abstract graphic for J. Chem. Inf. Model. (ACS TOC guidelines, updated 2024-02-28, read
2026-11-11): at most 3.25 x 1.75 in at final size, sans serif, 8 pt preferred and never below 6 pt, original, not
a figure from the text, the essence of the paper without specific results.

Schematic only (no data): a framework pore with water; isotherms at training temperatures (viridis, solid) and the
prediction at a held-out temperature (dashed) for a model whose shape conditions are built in (always rising) and
for one trained with a penalty (free to dip).

  python paper/fig_toc.py [out_stem]     default: paper/figures/fig_toc
"""
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "paper"))
import figstyle as fs  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, RegularPolygon  # noqa: E402

W_IN, H_IN = 3.25, 1.75
PT = 8.0          # labels (ACS: 8 pt preferred, >= 6 pt)
T_TRAIN = (288.0, 298.0, 308.0)
T_OUT = 323.0
NEW = fs.OI["vermilion"]   # held-out temperature; contrast with white about 3.9:1 (ACS: WCAG >= 3:1 for marks)


def step(x, T, dip=0.0):
    """A schematic water isotherm: a small Langmuir part plus a cooperative step that moves right as T rises."""
    x0 = 0.22 + 0.004 * (T - 288.0)
    q = 0.12 * x / (0.05 + x) + 0.80 / (1.0 + np.exp(-(x - x0) / 0.025))
    if dip:
        q = q - dip * np.exp(-((x - (x0 + 0.17)) / 0.06) ** 2)
    return q


def pore(ax):
    ax.set_xlim(-1.32, 1.32)
    ax.set_ylim(-1.32, 1.32)
    ax.set_aspect("equal")
    ax.axis("off")
    for k in range(6):
        a = math.pi / 3 * k
        ax.add_patch(RegularPolygon((0.95 * math.cos(a), 0.95 * math.sin(a)), 6, radius=0.30,
                                    orientation=math.pi / 6, fc=fs.OI["light"], ec=fs.OI["dark"], lw=0.6))
    ax.add_patch(RegularPolygon((0, 0), 6, radius=0.62, orientation=math.pi / 6, fc="white", ec=fs.OI["dark"],
                                lw=0.8))
    rng = np.random.default_rng(3)
    for (x, y) in [(-0.25, 0.18), (0.2, 0.25), (0.02, -0.22), (-0.3, -0.18), (0.3, -0.12), (0.0, 0.05)]:
        x += 0.03 * rng.standard_normal()
        ax.add_patch(Circle((x, y), 0.085, fc=fs.OI["blue"], ec=fs.OI["dark"], lw=0.4))
        for s in (-1, 1):
            ax.add_patch(Circle((x + s * 0.085, y + 0.075), 0.042, fc="white", ec=fs.OI["dark"], lw=0.4))


def isotherms(ax, title, dip):
    x = np.linspace(0.0, 0.9, 400)
    for T in T_TRAIN:
        ax.plot(x, step(x, T), color=fs.temp_colour(T), lw=1.1)
    ax.plot(x, step(x, T_OUT, dip=dip), color=NEW, lw=1.3, ls=(0, (3, 1.6)))
    ax.set_xlim(0, 0.9)
    ax.set_ylim(0, 1.05)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel(r"$p/p_\mathrm{sat}$", fontsize=PT, labelpad=1.5)
    ax.set_title(title, fontsize=PT, loc="center", pad=2.5)


def main():
    stem = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "paper/figures/fig_toc")
    fs.apply()
    fig = plt.figure(figsize=(W_IN, H_IN))
    pore(fig.add_axes([0.01, 0.20, 0.28, 0.72]))
    fig.text(0.15, 0.02, "MOF or COF + water", ha="center", va="bottom", fontsize=7.0)
    a1 = fig.add_axes([0.38, 0.27, 0.28, 0.60])
    a2 = fig.add_axes([0.71, 0.27, 0.28, 0.60])
    isotherms(a1, "shape built in", 0.0)
    isotherms(a2, "shape as penalty", 0.22)
    a1.set_ylabel("uptake", fontsize=PT, labelpad=1.5)
    from matplotlib.lines import Line2D
    hs = [Line2D([], [], color=fs.temp_colour(T_TRAIN[1]), lw=1.1),
          Line2D([], [], color=NEW, lw=1.3, ls=(0, (3, 1.6)))]
    fig.legend(hs, ["training T", "new T"], loc="lower center", bbox_to_anchor=(0.685, -0.015),
               ncol=2, fontsize=7.0, handlelength=2.0, columnspacing=1.2, borderaxespad=0.0)
    print(fs.save(fig, stem))


if __name__ == "__main__":
    main()
