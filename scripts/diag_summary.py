"""Summary of the refit diagnostics (scripts/refit_diagnostics.py; descriptive, ledger X-4/X-5) and of the
exploratory P-sign variant (scripts/explore_p_signs.py; ledger X-6).

Per cell, over the E-high and E-low fits: the number of fits with any grid point where the isosteric heat is
negative, above 150 kJ/mol, or undefined, inside the penalty domain ("in") and in the rest of the grid ("out"),
and the median fraction of grid points out of 0..150 kJ/mol among the fits that have any. For P and V-none/V-pen:
how many fits have a term with Q_k < 0 or alpha_k < 0, and the E of the fits with and without such a term. For
P-sign: H1-type ratios against P and V-pen (Hodges-Lehmann over materials, exploratory), its violations and heat
counts, and the COF-SO3H E-high seeds.

    python scripts/diag_summary.py   -> results/diag_summary.json
"""
import glob
import json
import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import analyse as A  # noqa: E402


def load(pattern):
    return [json.loads(x) for f in sorted(glob.glob(str(ROOT / pattern))) for x in open(f) if x.strip()]


def main():
    R = load("results/refit_diagnostics.shard*.jsonl")
    keys = {(r["cell"], r["material"], r["task"]) for r in R}
    assert len(keys) == len(R)
    out = {"n_refits": len(R), "max_E_rel_diff": max(r["E_rel_diff"] for r in R), "cells": {}}
    for c in sorted({r["cell"] for r in R}):
        g = [r for r in R if r["cell"] == c]
        h = [r["heat"] for r in g]
        d = {"fits": len(g)}
        for k in ("neg_in", "neg_out", "high_in", "high_out", "undef_in", "undef_out"):
            d[k] = sum(x[k] > 0 for x in h)
        frac = [(x["neg_in"] + x["neg_out"] + x["high_in"] + x["high_out"]) / x["points"] for x in h]
        d["any_out_of_range"] = sum(f > 0 for f in frac)
        d["median_frac_if_any"] = statistics.median([f for f in frac if f > 0]) if any(f > 0 for f in frac) else 0.0
        d["neg_any"] = sum((x["neg_in"] + x["neg_out"]) > 0 for x in h)
        d["high_any"] = sum((x["high_in"] + x["high_out"]) > 0 for x in h)
        d["undef_any"] = sum((x["undef_in"] + x["undef_out"]) > 0 for x in h)
        if g[0]["terms"] is not None:
            negQ = [any(q < 0 for q in r["terms"]["Q_kJ"]) for r in g]
            nega = [any(a < 0 for a in r["terms"]["alpha_per_K"]) for r in g]
            d["fits_with_negative_Q"] = sum(negQ)
            d["fits_with_negative_alpha"] = sum(nega)
            either = [a or b for a, b in zip(negQ, nega)]
            d["fits_with_either"] = sum(either)
            e1 = [r["E_refit"] for r, x in zip(g, either) if x]
            e0 = [r["E_refit"] for r, x in zip(g, either) if not x]
            d["median_E_with_either"] = statistics.median(e1) if e1 else None
            d["median_E_without"] = statistics.median(e0) if e0 else None
        out["cells"][c] = d
    so3h = [r for r in R if r["cell"] == "P" and r["material"].startswith("COF-SO3H") and r["task"] == "E-high"][0]
    out["P_COF-SO3H_E-high"] = {"selected": so3h["seed"], "seeds": so3h["all_seeds"]}
    # exploratory P-sign
    S = load("results/explore_p_signs.shard*.jsonl")
    if S:
        ps = {}
        for r in S:
            ps[(r["material"], r["task"])] = r
        out["P-sign"] = {"n": len(S), "failed": sum(r.get("error") is not None for r in S)}
        v = json.loads((ROOT / "results/verdicts.json").read_text())
        runs = load("results/confirmatory_runs.shard*.jsonl")
        E = {}
        for r in runs:
            E[(r["cell"], r["material"], r["task"])] = r["E"]
        mats = sorted({r["material"] for r in S})
        complete = [m for m in mats if all((m, t) in ps for t in A.E_TASKS)]
        out["P-sign"]["materials_complete"] = len(complete)
        for X in ("P", "V-pen", "A-hard", "C1"):
            d = []
            for m in complete:
                eS = np.mean([np.log10(ps[(m, t)]["E"]) for t in A.E_TASKS])
                eX = np.mean([np.log10(E[(X, m, t)]) for t in A.E_TASKS])
                d.append(eS - eX)
            d = np.array(d)
            lo, hi = A.hl_ci_exact(d, 0.95) if len(d) >= 6 else (float("nan"), float("nan"))
            out["P-sign"][f"vs_{X}"] = {"n": len(d), "R": float(10 ** A.hodges_lehmann(d)),
                                       "R_ci95": [float(10 ** lo), float(10 ** hi)],
                                       "n_better": int((d < 0).sum())}
        ev = [r for r in S if r["task"] in A.E_TASKS and r.get("error") is None]
        out["P-sign"]["violating_in"] = sum(A._violates(r["violations"], "in") for r in ev)
        out["P-sign"]["fits_E"] = len(ev)
        out["P-sign"]["heat_neg_any"] = sum((r["heat"]["neg_in"] + r["heat"]["neg_out"]) > 0 for r in ev)
        out["P-sign"]["heat_any_out"] = sum((r["heat"]["neg_in"] + r["heat"]["neg_out"] + r["heat"]["high_in"]
                                             + r["heat"]["high_out"]) > 0 for r in ev)
        out["P-sign"]["median_E"] = statistics.median([r["E"] for r in ev])
        so = ps.get((so3h["material"], "E-high"))
        if so:
            out["P-sign"]["COF-SO3H_E-high"] = {"E": so["E"], "E_all_seeds": so["E_all_seeds"],
                                               "train_loss_all_seeds": so["train_loss_all_seeds"]}
    (ROOT / "results/diag_summary.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
