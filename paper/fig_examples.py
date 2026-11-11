"""Figure: example extrapolations at the held-out temperature, from the exact refits of the reported seeds
(results/refit_diagnostics.shard*.jsonl, scripts/refit_diagnostics.py; descriptive, ledger X-4) and, for P-sign,
the exploratory variant (results/explore_p_signs.shard*.jsonl; ledger X-6, refitted here with its reported seed).

a  a typical material: the material whose P error in E-high is closest to P's median E-high error;
b  COF-SO3H in E-high, P's largest error;
c  the V-pen fit whose held-out isotherm falls most below its running maximum (a violation visible at T_out);
d  (review R4) the isosteric heat against uptake at the held-out temperature for the fit of panel b, from the refits
   of results/heat_window_real.shard*.jsonl (scripts/heat_window_real.py; ledger X-8 c), with the 0 to 150 kJ/mol
   range of the pre-registered count shaded and the H2 window (0.1 to 0.9 q_ref) marked.
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
            ax.plot(c["x"], c["q"], color=st["color"], ls=st["ls"], lw=1.0, label=f"{cell} (E {rs[cell]['E_refit']:#.2g})")
    if psign is not None:
        ax.plot(psign["x"], psign["q"], color=PSIGN["color"], ls=PSIGN["ls"], lw=1.0,
                label=f"P-sign (E {psign['E']:#.2g})")
    ax.set_xlim(0, 0.90)  # the measured range (p/p_sat <= 0.90)
    top = ymax if ymax else 1.25 * max(c0["q_obs"])
    ax.set_ylim(0, top)
    ax.set_xlabel(r"$p/p_\mathrm{sat}$")
    ax.set_title(title, loc="left")
    ax.legend(loc="upper left", fontsize=6.0, handlelength=1.6, borderaxespad=0.2)


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


def panel_heat(ax, mat, task):
    hw = [r for r in load("results/heat_window_real.shard*.jsonl") if r["material"] == mat and r["task"] == task]
    assert hw and max(r["E_rel_diff"] for r in hw) <= 1e-12
    qref = hw[0]["q_ref"]
    ax.axhspan(0.0, 150.0, color=fs.OI["light"], lw=0, zorder=0)
    ax.axvline(0.1 * qref, color=fs.ROLE["muted"], lw=0.5, ls=":", zorder=1)
    ax.axvline(0.9 * qref, color=fs.ROLE["muted"], lw=0.5, ls=":", zorder=1)
    for r in sorted(hw, key=lambda r: ("P-sign", "A-hard", "C1", "V-pen", "P").index(r["cell"])):
        st = PSIGN if r["cell"] == "P-sign" else fs.CELL[r["cell"]]
        q = np.array(r["curve"]["q"], float)
        h = np.array([np.nan if v is None else v for v in r["curve"]["qst_kJ"]], float)
        keep = (q > 0.02 * qref) & (q < 1.05 * qref)
        ax.plot(q[keep], h[keep], color=st["color"], ls=st["ls"], lw=1.0,
                label="P-sign (exploratory)" if r["cell"] == "P-sign" else r["cell"])
    ax.set_xlim(0, 1.05 * qref)
    ax.set_ylim(-150, 250)
    ax.axhline(0.0, color=fs.ROLE["muted"], lw=0.5, zorder=1)
    ax.set_xlabel(r"Uptake (mol kg$^{-1}$)")
    ax.set_ylabel(r"$Q_\mathrm{st}$ (kJ mol$^{-1}$)")
    ax.set_title("COF-SO$_3$H, E-high: heat at the held-out T", loc="left")
    ax.legend(loc="upper center", fontsize=6.0, handlelength=1.6, borderaxespad=0.2, ncol=3)


def main():
    stem = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "paper/figures/fig_examples")
    recs = load("results/refit_diagnostics.shard*.jsonl")
    assert max(r["E_rel_diff"] for r in recs) == 0.0
    # a: typical material: P's E-high error closest to P's median E-high error (in log10)
    eh = {r["material"]: r["E_refit"] for r in recs if r["task"] == "E-high" and r["cell"] == "P"}
    med = float(np.median([math.log10(e) for e in eh.values()]))
    typ = min(eh, key=lambda m: abs(math.log10(eh[m]) - med))
    sulfo = [m for m in eh if m.startswith("COF-SO3H")][0]
    vp = [r for r in recs if r["cell"] == "V-pen"]
    worst = max(vp, key=lambda r: drop(r["curve"]) / max(r["curve"]["q_obs"]))
    fs.apply()
    fig, axs = plt.subplots(2, 2, figsize=(fs.W2, 118 * fs.MM))
    axes = axs.flatten()
    panel(axes[0], recs, typ, "E-high", f"{typ.split(' |')[0]}, E-high (typical)")
    sp = psign_curve(sulfo, "E-high")
    panel(axes[1], recs, sulfo, "E-high", "COF-SO$_3$H, E-high", psign=sp)
    axes[1].legend(loc="lower right", fontsize=6.0, handlelength=1.6, borderaxespad=0.2)  # P's steep curve crosses upper left
    panel(axes[2], recs, worst["material"], worst["task"],
          f"{worst['material'].split(' |')[0]}, {worst['task']}: V-pen dip (zoom)")
    # zoom on the largest fall of V-pen's held-out isotherm below its running maximum
    c = worst["curve"]
    x, q = np.array(c["x"]), np.array(c["q"])
    k = int(np.argmax(np.where(x <= 0.90, np.maximum.accumulate(q) - q, -1)))
    lo, hi = max(0.0, x[k] - 0.08), min(0.95, x[k] + 0.08)
    win = (x >= lo) & (x <= hi)
    axes[2].set_xlim(lo, hi)
    axes[2].set_ylim(min(0.0, 1.3 * float(np.min(q[win]))), 1.6 * float(np.max(q[win])))
    axes[2].axhline(0.0, color=fs.ROLE["muted"], lw=0.5, zorder=0)
    axes[2].legend(loc="lower right", fontsize=6.0, handlelength=1.6, borderaxespad=0.2)
    panel_heat(axes[3], sulfo, "E-high")
    for ax in axes[:3]:
        ax.set_ylabel(r"Uptake (mol kg$^{-1}$)")
    for k, ax in enumerate(axes):
        fs.letter(ax, "abcd"[k], x=-0.14)
    fig.tight_layout(pad=0.5, w_pad=1.6, h_pad=1.2)
    inputs = sorted(glob.glob(str(ROOT / "results/refit_diagnostics.shard*.jsonl")))
    inputs += sorted(glob.glob(str(ROOT / "results/explore_p_signs.shard*.jsonl")))
    inputs += sorted(glob.glob(str(ROOT / "results/heat_window_real.shard*.jsonl")))
    print(fs.save(fig, stem, inputs=inputs))
    print("typical:", typ, "violation example:", worst["material"], worst["task"],
          "drop/q_obs_max:", round(drop(worst["curve"]) / max(worst["curve"]["q_obs"]), 3))


if __name__ == "__main__":
    main()
