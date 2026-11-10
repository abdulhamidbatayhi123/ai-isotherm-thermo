"""Summary of the step-position error (PREREG 6.4, descriptive; ledger X-2) from the refit records of
scripts/step_position.py: per model, over the E-high and E-low fits, the median absolute and median
signed error of the step position in p/p_sat (model minus data), the number of fits whose step could
not be located, and the largest relative difference between refitted and recorded E (reproduction).

    python scripts/step_summary.py   -> results/step_position_summary.json
"""
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CELLS = ("P", "V-pen", "A-hard", "F-none", "C1", "F-hard")


def main():
    rows = [json.loads(x) for f in sorted((ROOT / "results").glob("step_position.shard*.jsonl"))
            for x in f.read_text().splitlines() if x.strip()]
    keys = {(r["cell"], r["material"], r["task"]) for r in rows}
    assert len(keys) == len(rows), "duplicate refit records"
    out = {"n_records": len(rows), "max_E_rel_diff": max(r["E_rel_diff"] for r in rows), "cells": {}}
    for c in CELLS:
        g = [r for r in rows if r["cell"] == c]
        e = [r["step_error"] for r in g if math.isfinite(r["step_error"])]
        out["cells"][c] = {"fits": len(g), "located": len(e),
                           "median_abs": statistics.median(abs(x) for x in e) if e else None,
                           "median_signed": statistics.median(e) if e else None}
    (ROOT / "results/step_position_summary.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
