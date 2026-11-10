"""Further descriptive numbers asked for by the fresh-eyes review R1 (2026-11-10, after the verdicts; ledger X-4).
Nothing here is a test; every number is an estimate or a recount from existing result files with the frozen
analysis functions (scripts/analyse.py).

1. MOF/COF split of H1b-e and H1a (PREREG 6.4 subgroup; estimates only, n = 5 and 8).
2. H1a on the materials with at least three training temperatures (PREREG 6.4; n = 2, per-material ratios).
3. Same-source check of H1b (review M11): the per-material d averaged within each source paper, then the
   Hodges-Lehmann estimate and exact 95 % interval over the sources (exploratory).
4. H2 against F-none over the materials on which both P and F-none gave a defined heat (review M7), per family:
   Hodges-Lehmann ratio without the imputation of failures (exploratory).
5. The E floor set by digitisation (PREREG 3.5: about 0.003) next to the smallest observed E per cell.

    python scripts/descriptive_extra.py   -> results/descriptive_extra.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import analyse as A  # noqa: E402


def hl_with_ci(d):
    d = np.asarray(d, float)
    lo, hi = A.hl_ci_exact(d, 0.95)
    return {"n": int(d.size), "R": float(10 ** A.hodges_lehmann(d)),
            "R_ci95": [float(10 ** lo), float(10 ** hi)] if np.isfinite(lo) and np.isfinite(hi) else None}


def main():
    v = json.loads((ROOT / "results/verdicts.json").read_text())
    cls = A.material_class()
    out = {"note": "Descriptive and exploratory, computed after the verdicts (ledger X-4). No tests."}
    comps = {h: v["H1"][h] for h in ("H1b", "H1c", "H1d", "H1e")}
    comps["H1a"] = v["descriptive"]["H1a"]
    split = {}
    for h, r in comps.items():
        dd = r["d_by_material"]
        split[h] = {"X": r["X"]}
        for k in ("MOF", "COF"):
            d = [x for m, x in dd.items() if cls.get(m) == k]
            split[h][k] = {"n": len(d), "R": float(10 ** A.hodges_lehmann(np.array(d)))}
    out["by_class"] = split
    df = A.load(ROOT / "results/confirmatory_runs.jsonl")
    ntrain = {}
    for r in df[(df.cell == "P") & df.task.isin(A.E_TASKS)].itertuples():
        ntrain[r.material] = min(ntrain.get(r.material, 99), len(r.train_T))
    three = sorted(m for m, n in ntrain.items() if n >= 3)
    out["H1a_3plus_training_T"] = {m: float(10 ** comps["H1a"]["d_by_material"][m]) for m in three}
    # 3. same-source check of H1b
    dd = pd.Series(comps["H1b"]["d_by_material"])
    src = dd.index.map(lambda m: m.split("|")[1].strip().split("_")[0])
    by_src = dd.groupby(src).mean()
    out["H1b_by_source"] = {"sources": {k: float(x) for k, x in by_src.items()}, **hl_with_ci(by_src.values)}
    # 4. H2 vs F-none over materials where both succeeded
    h2 = A.load(ROOT / "results/synthetic_h2.jsonl", value_col="qst_rmse_kJ")
    both = {}
    for fam in A.H2_FAMILIES:
        sub = h2[h2.family == fam]
        eP, eX = A.e_by_material(sub, "P"), A.e_by_material(sub, "F-none")
        ok = eP.notna() & eX.notna()
        both[fam] = hl_with_ci((eP[ok] - eX[ok]).to_numpy())
    out["H2_F-none_both_defined"] = both
    # 5. E floor
    out["E_floor_digitisation"] = 0.003
    out["E_min_by_cell"] = {c: float(g.E.min()) for c, g in df[df.task.isin(A.E_TASKS)].groupby("cell")}
    (ROOT / "results/descriptive_extra.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
