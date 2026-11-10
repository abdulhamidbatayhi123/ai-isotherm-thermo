"""Figure: example extrapolations at the held-out temperature, from the exact refits of the reported seeds
(results/refit_diagnostics.shard*.jsonl, scripts/refit_diagnostics.py; descriptive, ledger X-4) and, for P-sign,
the exploratory variant (results/explore_p_signs.shard*.jsonl; ledger X-6, refitted here with its reported seed).

a  a typical material: the material whose P-vs-V-pen ratio in E-high is closest to the median over materials;
b  COF-SO3H in E-high, P's largest error;
c  the V-pen fit whose held-out isotherm falls most below its running maximum (a violation visible at T_out).
Observed held-out points in black; model curves in the fixed cell colours. Uptake in mol/kg.

  python paper/fig_examples.py [out_stem]     default: paper/figures/fig_examples
"""
import glob
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "paper"))
import figstyle as fs  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402

CELLS = ("P", "V-pen", "A-hard", "C1", "F-none")
PSIGN = dict(color=fs.OI["black"], ls="--", marker="", label="P-sign (exploratory)")


def load(pattern):
    return [json.loads(x) for f in sorted(glob.glob(str(ROOT / pattern))) for x in open(f) if x.strip()]


def drop(c):
    q = np.array(c["q"])
    x = np.array(c["x"])
    q = q[x <= 0.90]
    return float(np.max(np.maximum.accumulate(q) - q))


def panel(ax, recs, mat, task, title, psign=None, ymax=None):
    rs = {r["cell"]: r for r in recs if r["material"] == mat and r["task"] == task}
    c0 = rs["P"]["curve"]
    ax.plot(c0["x_obs"], c0["q_obs"], "o", ms=2.6, mfc=fs.OI["black"], mec="none", zorder=5, label="data")
    for cell in CELLS:
        if cell in rs:
            st = fs.CELL[cell]
            c = rs[cell]["curve"]
            ax.plot(c["x"], c["q"], color=st["color"], ls=st["ls"], lw=1.0, label=f"{cell} (E {rs[cell]['E_refit']:.2g})")
    if psign is not None:
        ax.plot(psign["x"], psign["q"], color=PSIGN["color"], ls=PSIGN["ls"], lw=1.0,
                label=f"P-sign (E {psign['E']:.2g})")
    ax.set_xlim(0, 0.95)
    top = ymax if ymax else 1.25 * max(c0["q_obs"])
    ax.set_ylim(0, top)
    ax.set_xlabel(r"$p/p_\mathrm{sat}$")
    ax.set_title(title, loc="left")
    ax.legend(loc="upper left", fontsize=5.0, handlelength=1.8, borderaxespad=0.2)


def psign_curve(mat, task):
    """Refit P-sign's reported seed for one fit and return its held-out curve (exploratory)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT / "src"))
    import torch
    import explore_p_signs as X
    from p3a import study
    from refit_diagnostics import curve
    from run_dev import load_materials
    rec = [r for r in load("results/explore_p_signs.shard*.jsonl") if r["material"] == mat and r["task"] == task]
    if not rec:
        return None
    rec = rec[0]
    m = [x for x in load_materials("confirmatory") if x.name == mat][0]
    best = json.loads((ROOT / "results/dev_best_configs.json").read_text())
    cfg = study.Config(**best["P"]["config"])
    torch.set_num_threads(1)
    loss, seed, model = X.fit_psign(cfg, m, rec["train_T"], seeds=(int(rec["best_seed"]),))[0]
    E = study.error_E(model, m, rec["T_out"])
    assert abs(E - rec["E"]) <= 1e-12 * max(1, rec["E"]), (E, rec["E"])
    c = curve(model, m, rec["T_out"])
    c["E"] = E
    return c


def main():
    stem = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "paper/figures/fig_examples")
    recs = load("results/refit_diagnostics.shard*.jsonl")
    assert max(r["E_rel_diff"] for r in recs) == 0.0
    # a: typical material for P vs V-pen in E-high
    eh = {}
    for r in recs:
        if r["task"] == "E-high" and r["cell"] in ("P", "V-pen"):
            eh.setdefault(r["material"], {})[r["cell"]] = r["E_refit"]
    ratios = {m: math.log10(v["P"] / v["V-pen"]) for m, v in eh.items() if len(v) == 2}
    med = float(np.median(list(ratios.values())))
    typ = min(ratios, key=lambda m: abs(ratios[m] - med))
    sulfo = [m for m in eh if m.startswith("COF-SO3H")][0]
    vp = [r for r in recs if r["cell"] == "V-pen"]
    worst = max(vp, key=lambda r: drop(r["curve"]) / max(r["curve"]["q_obs"]))
    fs.apply()
    fig, axes = plt.subplots(1, 3, figsize=(fs.W2, 62 * fs.MM))
    panel(axes[0], recs, typ, "E-high", f"{typ.split(' |')[0]}, E-high (typical)")
    sp = psign_curve(sulfo, "E-high")
    panel(axes[1], recs, sulfo, "E-high", "COF-SO$_3$H, E-high", psign=sp)
    panel(axes[2], recs, worst["material"], worst["task"],
          f"{worst['material'].split(' |')[0]}, {worst['task']}")
    axes[0].set_ylabel(r"Uptake (mol kg$^{-1}$)")
    for k, ax in enumerate(axes):
        fs.letter(ax, "abc"[k], x=-0.2)
    fig.tight_layout(pad=0.5, w_pad=1.2)
    inputs = sorted(glob.glob(str(ROOT / "results/refit_diagnostics.shard*.jsonl")))
    inputs += sorted(glob.glob(str(ROOT / "results/explore_p_signs.shard*.jsonl")))
    print(fs.save(fig, stem, inputs=inputs))
    print("typical:", typ, "violation example:", worst["material"], worst["task"],
          "drop/q_obs_max:", round(drop(worst["curve"]) / max(worst["curve"]["q_obs"]), 3))


if __name__ == "__main__":
    main()
