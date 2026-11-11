"""Descriptive summary of every model over the extrapolation tasks (written 2026-11-11 after the confirmatory verdicts,
review R4; correction ledger X-8 c). No new fit: it reads the confirmatory run records, the X-6 (P-sign), X-7/X-8
(V-pen at a heavier monotonicity weight) and X-8 b (isostere) results.

For each model over its E-high and E-low fits: the median error E (% of q_ref); the ratio R = E_P / E_X with its exact
95 % interval and unadjusted p (frozen analysis code; for the confirmatory comparators these equal the verdict
file); the number of fits violating inside the domain (H3 rule) and the number with any heat outside 0 to 150 kJ/mol
and the number with an undefined heat on the grid (PREREG 6.2 strict counts).

    python scripts/cell_summary.py   -> results/cell_summary.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import analyse as A  # noqa: E402

ORDER = ("F-none", "F-pen", "F-hard", "V-none", "V-pen", "P", "A-none", "A-pen", "A-hard", "F-rel", "C1")


def jsonl(pattern):
    return pd.DataFrame([json.loads(x) for f in sorted((ROOT / "results").glob(pattern))
                         for x in f.read_text().splitlines() if x.strip()])


def summarise(df, cell, eP):
    g = df[(df.cell == cell) & df.task.isin(A.E_TASKS)]
    v = list(g["violations"]) if "violations" in g else []
    out = {"fits": len(g),   # median as in scripts/descriptive_seeds.py: 10 ** median(log10 E)
           "median_E_pct": float(100 * 10 ** np.median(np.log10(g.E.astype(float))))}
    if cell != "P":
        d, mats, _ = A.paired_d(eP, A.e_by_material(df, cell))
        out.update({"R": 10 ** A.hodges_lehmann(d), "R_ci95": [10 ** x for x in A.hl_ci_exact(d, 0.95)],
                    "p_unadjusted": A.wilcoxon_exact(d), "n_P_better": int((d < 0).sum()), "n": len(mats)})
    if v and all(isinstance(x, dict) for x in v):
        out["violating_in_domain"] = int(sum(A._violates(x, "in") for x in v))
        out["heat_out_of_range"] = int(sum(x["qst_out_of_range"] > 0 for x in v))
        out["heat_undefined"] = int(sum(x["undefined_qst"] > 0 for x in v))
    return out


def main():
    conf = A.load(ROOT / "results/confirmatory_runs.jsonl")
    eP = A.e_by_material(conf, "P")
    rows = {c: summarise(conf, c, eP) for c in ORDER}
    ps = jsonl("explore_p_signs.shard*.jsonl")
    ps["log10E"] = np.log10(ps.E.astype(float))
    rows["P-sign"] = summarise(ps, "P-sign", eP)
    sel = json.loads((ROOT / "results/vpen_weight_summary.json").read_text())
    w = sel.get("selected_on_development", {}).get("w_mono")
    if w is not None:
        sw = jsonl("explore_vpen_weight.shard*.jsonl")
        sw = sw[np.isclose(sw.w_mono.astype(float), float(w))].copy()
        sw["log10E"] = np.log10(sw.E.astype(float))
        rows["V-pen-heavy"] = summarise(sw, "V-pen", eP) | {"w_mono": float(w)}
    iso = json.loads((ROOT / "results/isostere_baseline.json").read_text())
    rows["Isostere"] = {"fits": iso["n_fits"], "median_E_pct": iso["median_E_iso_pct_log"], "R": iso["R_P_over_ISO"],
                        "R_ci95": iso["R_ci95"], "p_unadjusted": iso["p_unadjusted"],
                        "n_P_better": iso["n_material_P_better"], "n": iso["n_materials"],
                        "fold_above_tolerance": iso["fits_fold_above_tolerance"]}
    out = {"note": "descriptive; R = E_P / E_X (below one: P more accurate), exact 95 % interval, p unadjusted",
           "rows": rows}
    # X-8 (c): heat at the held-out temperature inside the H2 window (refits, scripts/heat_window_real.py)
    hw = jsonl("heat_window_real.shard*.jsonl")
    if len(hw):
        if hw.duplicated(["cell", "material", "task"]).any() or hw.E_rel_diff.max() > 1e-12:
            raise ValueError("heat_window_real: duplicate records or a refit that does not reproduce E")
        win = {}
        for c, g in hw.groupby("cell"):
            w = list(g["window"])
            win[c] = {"fits": len(g),
                      "fits_any_out_of_range_or_undefined": int(sum((x["neg"] + x["high"] + x["undef"]) > 0 for x in w)),
                      "fits_negative": int(sum(x["neg"] > 0 for x in w)),
                      "fits_above_150": int(sum(x["high"] > 0 for x in w)),
                      "fits_undefined": int(sum(x["undef"] > 0 for x in w)),
                      "fits_window_lt3": int(sum(x["n_window"] < 3 for x in w)),
                      "states_in_window": int(sum(x["n_window"] for x in w)),
                      "states_out_of_range_or_undefined": int(sum(x["neg"] + x["high"] + x["undef"] for x in w))}
        out["heat_window_held_out"] = {"complete": len(hw) == 130, "cells": win}
    dg = json.loads((ROOT / "results/diag_summary.json").read_text())
    out["P_median_grid_fraction_out_of_range_if_any"] = dg["cells"]["P"]["median_frac_if_any"]
    (ROOT / "results/cell_summary.json").write_text(json.dumps(out, indent=1))
    for k, r in rows.items():
        print(f"{k:12s} medE {r['median_E_pct']:5.1f}%  R {r.get('R', float('nan')):.2f} "
              f"{[round(x, 2) for x in r.get('R_ci95', [])]}  viol {r.get('violating_in_domain')}  "
              f"heat {r.get('heat_out_of_range')} undef {r.get('heat_undefined')}")


if __name__ == "__main__":
    main()
