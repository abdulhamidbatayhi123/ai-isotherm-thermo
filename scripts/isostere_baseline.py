"""EXPLORATORY, descriptive (written 2026-11-11 after the confirmatory verdicts, review R4; correction ledger X-8 b).

A classical baseline with no fitted model: isostere extrapolation (Clausius-Clapeyron at constant loading). For a
task with training temperatures T_1..T_j and held-out temperature T_out:

  1. Each training isotherm is made monotone (running maximum of q over increasing p) and read as ln p(q) by linear
     interpolation in ln p.
  2. On 200 loadings spanning the range common to all training isotherms, ln p is fitted as a + b/T by least squares
     over the training temperatures (exactly through the two points when j = 2) and evaluated at T_out.
  3. The held-out uptake at each measured pressure is read from this extrapolated isotherm by linear interpolation in
     ln p. Below its lowest pressure the uptake falls linearly in p to zero at p = 0 (a Henry segment through the
     origin); above its highest pressure it is held at the largest common loading (the method cannot say more).

The error E = RMSE / q_ref is the confirmatory error (scripts/analyse.py, PREREG 6.1); the per-material summary and
the Hodges-Lehmann ratio against P use the frozen analysis code (exploratory: unadjusted, no verdict class). The
extrapolated isotherm is checked for monotonicity (an isostere crossing makes it decrease).

    python scripts/isostere_baseline.py   -> results/isostere_baseline.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from p3a import study  # noqa: E402
from run_dev import load_materials  # noqa: E402
import analyse as A  # noqa: E402

N_Q = 200


def lnp_of_q(s, q):
    """Monotone (running maximum) training isotherm as an interpolant ln p(q) on its distinct loadings."""
    o = np.argsort(s)
    s, q = s[o], np.maximum.accumulate(q[o])
    qu, idx = np.unique(q, return_index=True)       # first pressure at which each loading is reached
    return qu, s[idx]


def predict(m, train_T, T_out):
    curves = [lnp_of_q(m.s[m.T == T], m.q[m.T == T]) for T in train_T]
    q_lo = max(c[0][0] for c in curves)
    q_hi = min(c[0][-1] for c in curves)
    qg = np.linspace(q_lo, q_hi, N_Q)
    X = np.column_stack([np.ones(len(train_T)), 1.0 / np.asarray(train_T)])
    S = np.stack([np.interp(qg, qu, su) for qu, su in curves])           # (j, N_Q) ln p at each loading
    coef, *_ = np.linalg.lstsq(X, S, rcond=None)
    s_out = coef[0] + coef[1] / T_out                                     # extrapolated isotherm ln p(q)
    monotone = bool(np.all(np.diff(s_out) > 0))
    # size of the fold: the loading span over which ln p(q) lies below its running maximum, as a fraction of
    # q_ref; a fold above 0.02 q_ref is a violation by the tolerance of the H3 count (PREREG 6.2)
    folded = s_out < np.maximum.accumulate(s_out) - 1e-12
    fold_frac = float(np.sum(np.diff(qg)[folded[1:]]) / m.q_ref)
    s_mono = np.maximum.accumulate(s_out)                                 # read q(p) from the monotone envelope
    s_obs = m.s[m.T == T_out]
    qp = np.interp(s_obs, s_mono, qg)
    p_obs, p_min = np.exp(s_obs), np.exp(s_mono[0])
    below = s_obs < s_mono[0]
    qp[below] = qg[0] * p_obs[below] / p_min
    qp[s_obs > s_mono[-1]] = qg[-1]
    E = float(np.sqrt(np.mean((qp - m.q[m.T == T_out]) ** 2)) / m.q_ref)
    return {"E": E, "monotone_isotherm": monotone, "fold_frac_qref": fold_frac, "fold_violation": fold_frac > 0.02, "q_common": [float(q_lo), float(q_hi)],
            "frac_above_range": float(np.mean(s_obs > s_mono[-1])), "frac_below_range": float(below.mean())}


def main():
    rows, out_fits = [], []
    for m in load_materials("confirmatory"):
        for task, (train_T, T_out) in study.tasks(m).items():
            if task not in A.E_TASKS:
                continue
            r = predict(m, [float(t) for t in train_T], float(T_out))
            out_fits.append({"material": m.name, "task": task, **r})
            rows.append({"cell": "ISO", "material": m.name, "task": task, "E": r["E"], "error": None})
    iso = pd.DataFrame(rows)
    iso["log10E"] = np.log10(iso.E)
    conf = A.load(ROOT / "results/confirmatory_runs.jsonl")
    eP = A.e_by_material(conf, "P")
    eX = A.e_by_material(iso, "ISO")
    d, mats, fails = A.paired_d(eP, eX)
    summary = {"note": "exploratory, post hoc (ledger X-8 b); p unadjusted, no verdict class",
               "R_P_over_ISO": 10 ** A.hodges_lehmann(d),
               "R_ci95": [10 ** x for x in A.hl_ci_exact(d, 0.95)],
               "p_unadjusted": A.wilcoxon_exact(d), "n_material_P_better": int((d < 0).sum()),
               "n_materials": len(mats), "median_E_iso": float(np.median(iso.E)),
               "median_E_iso_pct": float(100 * np.median(iso.E)),
               "median_E_iso_pct_log": float(100 * 10 ** np.median(np.log10(iso.E))),   # as descriptive_seeds.py
               "fits_fold_above_tolerance": int(sum(f["fold_violation"] for f in out_fits)),
               "median_fold_frac_if_any": float(np.median([f["fold_frac_qref"] for f in out_fits
                                                           if not f["monotone_isotherm"]] or [0.0])),
               "fits_nonmonotone": int(sum(not f["monotone_isotherm"] for f in out_fits)),
               "median_frac_above_range": float(np.median([f["frac_above_range"] for f in out_fits])),
               "fits": out_fits}
    summary["n_fits"] = len(out_fits)
    for cell in ("A-hard", "C1", "V-pen"):
        dd, _, _ = A.paired_d(A.e_by_material(conf, cell), eX)
        summary[f"R_{cell}_over_ISO"] = 10 ** A.hodges_lehmann(dd)
        summary[f"R_{cell}_over_ISO_ci95"] = [10 ** x for x in A.hl_ci_exact(dd, 0.95)]
    (ROOT / "results/isostere_baseline.json").write_text(json.dumps(summary, indent=1))
    print({k: v for k, v in summary.items() if k != "fits"})


if __name__ == "__main__":
    main()
