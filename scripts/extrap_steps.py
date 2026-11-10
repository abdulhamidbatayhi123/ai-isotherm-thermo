"""Descriptive (review R3 M6): how far each extrapolation reaches beyond the nearest training temperature.

E-high holds out T_k, so its step is T_k - T_(k-1); E-low holds out T_1, step T_2 - T_1. Also the span T_k - T_1.
Reads data/dataset_summary.json (confirmatory materials); writes results/extrap_steps.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    d = json.loads((ROOT / "data/dataset_summary.json").read_text())
    rows = {}
    for name, m in d.items():
        if m["set"] != "confirmatory":
            continue
        T = sorted(m["temperatures_K"])
        rows[name] = {"E-high_K": round(T[-1] - T[-2], 2), "E-low_K": round(T[1] - T[0], 2),
                      "span_K": round(T[-1] - T[0], 2), "n_T": len(T)}
    steps = [v[k] for v in rows.values() for k in ("E-high_K", "E-low_K")]
    out = {"n_materials": len(rows), "n_extrapolations": len(steps), "step_min_K": min(steps),
           "step_max_K": max(steps), "step_median_K": sorted(steps)[len(steps) // 2 - 1:len(steps) // 2 + 1],
           "per_material": rows}
    (ROOT / "results/extrap_steps.json").write_text(json.dumps(out, indent=1))
    print({k: v for k, v in out.items() if k != "per_material"})


if __name__ == "__main__":
    main()
