"""Exploratory, post hoc (ledger X-7; review R3 M1): does a heavier monotonicity penalty change V-pen's comparison
with P?

Reads results/explore_vpen_weight.shard*.jsonl (V-pen refitted with the monotonicity term weighted w_mono, the
Henry-slope term kept at the tuned lambda = 0.001) and the confirmatory runs (P, and V-pen at w_mono = lambda).
For each weight it reports, with the frozen analysis code of scripts/analyse.py (the same per-material mean of log10 E
over E-high and E-low, the Hodges-Lehmann ratio R = E_P / E_X with exact intervals and the exact Wilcoxon p-value):
  * R against P, its 95 % and 90 % intervals and p (unadjusted: exploratory, no verdict class);
  * the in-domain violation count of scripts/analyse.py (H3 rule) over the 26 extrapolation fits, and the strict
    count (any non-monotone or negative point on the grid);
  * the median monotonicity and Henry terms at the selected seed.
Writes results/vpen_weight_summary.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import analyse as A  # noqa: E402


def summarise(df, eP, label):
    eX = A.e_by_material(df, "V-pen")
    d, mats, fails = A.paired_d(eP, eX)
    R = 10 ** A.hodges_lehmann(d)
    lo95, hi95 = (10 ** x for x in A.hl_ci_exact(d, 0.95))
    lo90, hi90 = (10 ** x for x in A.hl_ci_exact(d, 0.90))
    g = df[(df.cell == "V-pen") & df.task.isin(A.E_TASKS)]
    v = [x for x in g["violations"] if isinstance(x, dict)]
    out = {"weight": label, "n_materials": len(mats), "fails": fails, "R": R, "R_ci95": [lo95, hi95],
           "R_ci90": [lo90, hi90], "p_unadjusted": A.wilcoxon_exact(d),
           "n_material_P_better": int((d < 0).sum()),
           "fits": len(v), "violating_in_domain": int(sum(A._violates(x, "in") for x in v)),
           "violating_extrapolated_band": int(sum(A._violates(x, "out") for x in v)),
           "violating_strict": int(sum(any(x[c] > 0 for c in ("nonmonotone", "negative_q")) for x in v)),
           "median_log10E_vpen": float(np.median(eX.to_numpy(float)))}
    for col in ("mono_term", "henry_term"):
        if col in g:
            out[f"median_{col}"] = float(np.median(g[col].to_numpy(float)))
    if "mono_term" in g:
        strict = [any(x[c] > 0 for c in ("nonmonotone", "negative_q")) for x in g["violations"]]
        mono = g["mono_term"].to_numpy(float)
        out["fits_mono_term_nonzero"] = int((mono > 0).sum())
        out["strict_fits_with_mono_term_zero"] = int(sum(s and m == 0 for s, m in zip(strict, mono)))
        out["strict_fits_nonmonotone_with_mono_term_zero"] = int(sum(
            x["nonmonotone"] > 0 and m == 0 for x, m in zip(g["violations"], mono)))
    return out


def main():
    conf = A.load(ROOT / "results/confirmatory_runs.jsonl")
    eP = A.e_by_material(conf, "P")
    # A.load keys duplicates on (cell, material, task); here the weight is part of the key
    files = sorted((ROOT / "results").glob("explore_vpen_weight.shard*.jsonl"))
    sweep = pd.DataFrame([json.loads(x) for f in files for x in f.read_text().splitlines() if x.strip()])
    if sweep.duplicated(["w_mono", "material", "task"]).any():
        raise ValueError("duplicate X-7 records")
    if sweep["error"].notna().any() or not (sweep.E > 0).all():
        raise ValueError("failed or non-positive X-7 fits: " + str(sweep[sweep["error"].notna()][["material", "task"]]))
    sweep["log10E"] = np.log10(sweep.E.astype(float))
    lam = float(sweep.lam.iloc[0])
    rows = [summarise(conf, eP, {"w_mono": lam, "multiple_of_lambda": 1.0, "source": "confirmatory"})]
    for w, g in sweep.groupby("w_mono"):
        rows.append(summarise(g, eP, {"w_mono": float(w), "multiple_of_lambda": float(w) / lam, "source": "X-7"}))
    out = {"note": "exploratory, post hoc (ledger X-7); p unadjusted, no verdict class", "lambda": lam,
           "tasks": list(A.E_TASKS), "rows": rows}
    (ROOT / "results/vpen_weight_summary.json").write_text(json.dumps(out, indent=1))
    for r in rows:
        print(r["weight"]["multiple_of_lambda"], f"R={r['R']:.3f}", [round(x, 3) for x in r["R_ci95"]],
              f"p={r['p_unadjusted']:.4f}", f"Pbetter={r['n_material_P_better']}/{r['n_materials']}",
              f"viol_in={r['violating_in_domain']}/{r['fits']}", f"strict={r['violating_strict']}",
              f"mono={r.get('median_mono_term')}", f"henry={r.get('median_henry_term')}")


if __name__ == "__main__":
    main()
