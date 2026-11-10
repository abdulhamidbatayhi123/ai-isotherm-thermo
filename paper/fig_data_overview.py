"""Figure: the confirmatory data (descriptive; no model). One panel per material, uptake against
relative pressure at every temperature, points joined by thin lines (no fitted curve), with
the source type (numeric, vector-, raster- or ISODB-digitised) in each panel.

  python paper/fig_data_overview.py [out_stem]   default -> paper/figures/fig_data_overview.{pdf,png,prov.json}
  (the manuscript uses paper/figures/fig_s1, Supplementary Fig. S1)
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "paper"))
sys.path.insert(0, str(ROOT / "src"))
import figstyle as fs  # noqa: E402
from p3a import water  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import torch  # noqa: E402

M_W = 18.01528e-3  # kg/mol
SOURCE_WORD = {"numeric": "numeric data", "vector-digitised": "vector", "raster-digitised": "raster",
               "isodb-digitised": "ISODB"}


def main():
    fs.apply()
    d = pd.read_csv(ROOT / "data/raw/dataset/isotherms.csv")
    summ = json.loads((ROOT / "data/dataset_summary.json").read_text())
    d = d[d["set"] == "confirmatory"]
    keys = sorted(summ, key=lambda k: (summ[k]["class"] != "MOF", k.lower()))
    keys = [k for k in keys if summ[k]["set"] == "confirmatory"]
    fig, axes = plt.subplots(4, 4, figsize=(fs.W2, 150 * fs.MM))
    for ax, k in zip(axes.flat, keys):
        mat, src = [s.strip() for s in k.split("|")]
        g = d[(d.material == mat) & (d.source == src)]
        for T, h in g.groupby("T_K"):
            h = h.sort_values("p_Pa")
            rh = h.p_Pa / water.p_sat(torch.as_tensor(h.T_K.to_numpy(float))).numpy()
            c = fs.temp_colour(T)
            ax.plot(rh, h.q_molkg * M_W, "-", lw=0.5, color=c)
            ax.plot(rh, h.q_molkg * M_W, "o", ms=1.8, mfc=c, mec="none")
        ax.set_xlim(0, 0.92)
        ax.set_ylim(0, None)
        ax.set_title(f"{mat.replace(' (Lin 2006)', '')} ({summ[k]['class']})", fontsize=fs.SMALL_PT, pad=2)
        ax.text(0.97, 0.04, SOURCE_WORD.get(summ[k]["provenance"], summ[k]["provenance"]),
                transform=ax.transAxes, ha="right", va="bottom", fontsize=5.5, color=fs.ROLE["muted"])
    for ax in axes.flat[len(keys):]:
        ax.axis("off")
    # one shared temperature scale instead of per-panel legends (a legend covered data)
    import matplotlib as mpl
    spare = axes.flat[len(keys)]
    cax = spare.inset_axes([0.08, 0.42, 0.84, 0.09])
    T_lo, T_hi = 278.0, 333.0
    sm = mpl.cm.ScalarMappable(norm=mpl.colors.Normalize(T_lo - 273.15, T_hi - 273.15),
                               cmap=mpl.colors.ListedColormap([fs.temp_colour(T, T_lo, T_hi)
                                                               for T in np.linspace(T_lo, T_hi, 256)]))
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal")
    cb.set_label("Temperature (°C)", fontsize=fs.SMALL_PT)
    cb.outline.set_linewidth(0.5)
    cb.set_ticks([10, 20, 30, 40, 50])
    spare.text(0.5, 0.78, "Points: adsorption branch as published;\nlines join points (no fit).",
               transform=spare.transAxes, ha="center", va="center", fontsize=fs.SMALL_PT)
    for i, ax in enumerate(axes.flat[:len(keys)]):
        if i + 4 >= len(keys):  # no panel below: label the x axis here
            ax.set_xlabel(r"$p/p_\mathrm{sat}$")
    for ax in axes[:, 0]:
        ax.set_ylabel("Uptake (g g$^{-1}$)")
    fig.tight_layout(pad=0.4, h_pad=0.6, w_pad=0.5)
    stem = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "paper/figures/fig_data_overview")
    fs.save(fig, stem,
            inputs=[str(ROOT / "data/raw/dataset/isotherms.csv"), str(ROOT / "data/dataset_summary.json")])


if __name__ == "__main__":
    main()
