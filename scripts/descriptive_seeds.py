"""Seed spread of the held-out error (PREREG 5.3: "The seed spread of the held-out error is
reported") and two EXPLORATORY checks that are not in the pre-registration (written after the
confirmatory verdicts were known, 2026-11-10, and labelled as such wherever they are reported).

1. Seed spread (pre-registered as a report, form not fixed): for every record, the range of
   log10 E over the five seeds, and the rank of the selected seed (lowest training loss) among
   the five held-out errors; summarised per cell over the E-high and E-low records.
2. Exploratory: the H1 comparisons recomputed with E replaced, in every record of every cell, by
   the median over the five seeds of E (selection-free; it uses no held-out information to pick
   a seed, it averages over all of them). Same code as the confirmatory analysis
   (scripts/analyse.py analyse_h1), so only the per-record value changes.
3. Exploratory: the H1 comparisons with the material of largest |d| in H1b left out.

    python scripts/descriptive_seeds.py [results/confirmatory_runs.jsonl] -> results/descriptive_seeds.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import analyse as A  # noqa: E402

SEED = 20261013   # the analysis seed of scripts/analyse.py (bootstrap only)


def seed_table(df):
    rows = []
    for r in df.itertuples():
        es = {int(k): float(v) for k, v in r.E_all_seeds.items()}
        le = np.log10(np.array([es[k] for k in sorted(es)]))
        sel = np.log10(es[int(r.best_seed)])
        rows.append({"cell": r.cell, "material": r.material, "task": r.task, "n_seeds": len(es),
                     "range_decades": float(le.max() - le.min()),
                     "rank_selected": int((le < sel - 1e-12).sum()) + 1,       # 1 = best held-out error
                     "median_E": float(10 ** np.median(le)), "selected_E": float(es[int(r.best_seed)])})
    return pd.DataFrame(rows)


def main(argv):
    src = Path(argv[0]) if argv else ROOT / "results/confirmatory_runs.jsonl"
    df = A.load(src)
    st = seed_table(df)
    et = st[st.task.isin(A.E_TASKS)]
    spread = {}
    for c, g in et.groupby("cell"):
        spread[c] = {"records": int(len(g)),
                     "median_range_decades": float(g.range_decades.median()),
                     "max_range_decades": float(g.range_decades.max()),
                     "records_range_over_1_decade": int((g.range_decades > 1).sum()),
                     "selected_was_best_heldout": int((g.rank_selected == 1).sum()),
                     "selected_was_worst_heldout": int((g.rank_selected == g.n_seeds).sum())}
    out = {"source": src.name,
           "note": "Section 1 reports the pre-registered seed spread (PREREG 5.3). Sections 2 and 3 are "
                   "EXPLORATORY, not pre-registered, written after the confirmatory verdicts were known.",
           "seed_spread_E_tasks": spread,
           "largest_selected_E": st.sort_values("selected_E", ascending=False).head(5).to_dict("records")}
    # 2. exploratory: median over seeds
    dm = df.copy()
    med = st.set_index(["cell", "material", "task"]).median_E
    dm["E"] = [med[(r.cell, r.material, r.task)] for r in dm.itertuples()]
    dm["log10E"] = np.log10(dm.E)
    h = A.analyse_h1(dm, np.random.default_rng(SEED))
    out["exploratory_median_over_seeds"] = {
        k: {kk: v[kk] for kk in ("X", "R", "R_ci95", "p", "p_adj", "class")} for k, v in h["H1"].items()}
    out["exploratory_median_over_seeds"]["H1b_upper95_below_1.25"] = h["H1b_prediction"]["met"]
    out["exploratory_median_over_seeds"]["H1a"] = {kk: h["descriptive"]["H1a"][kk]
                                                   for kk in ("X", "R", "R_ci95", "p", "class")}
    # 3. exploratory: leave out the material with the largest |d| in H1b (confirmatory values)
    full = A.analyse_h1(df, np.random.default_rng(SEED))
    db = full["H1"]["H1b"]["d_by_material"]
    drop = max(db, key=lambda m: abs(db[m]))
    h3 = A.analyse_h1(df[df.material != drop], np.random.default_rng(SEED))
    out["exploratory_leave_one_out"] = {"left_out": drop, "n_materials": h3["H1"]["H1b"]["n_materials"]}
    out["exploratory_leave_one_out"].update(
        {k: {kk: v[kk] for kk in ("X", "R", "R_ci95", "p", "p_adj", "class")} for k, v in h3["H1"].items()})
    out["exploratory_leave_one_out"]["H1b_upper95_below_1.25"] = h3["H1b_prediction"]["met"]
    dst = ROOT / "results/descriptive_seeds.json"
    dst.write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    for c, s in spread.items():
        print(f"{c:7s} median range {s['median_range_decades']:.2f} dec, >1 dec {s['records_range_over_1_decade']:2d}/"
              f"{s['records']}, selected best {s['selected_was_best_heldout']:2d}, worst {s['selected_was_worst_heldout']:2d}")
    for name in ("exploratory_median_over_seeds", "exploratory_leave_one_out"):
        print(name)
        for k, v in out[name].items():
            if isinstance(v, dict) and "R" in v:
                print(f"  {k} {v['X']:7s} R={v['R']:.3f} [{v['R_ci95'][0]:.3f}, {v['R_ci95'][1]:.3f}] "
                      f"p_adj={v.get('p_adj', v['p']):.4f} {v['class']}")
        print("  H1b upper95 < 1.25:", out[name]["H1b_upper95_below_1.25"])
    print("written", dst)


if __name__ == "__main__":
    main(sys.argv[1:])
