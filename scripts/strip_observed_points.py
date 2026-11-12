"""Remove the measured held-out points from the refit records (written 2026-11-12; ledger, data availability).

results/refit_diagnostics.shard*.jsonl stored, for the example figure, the measured held-out isotherm of every fit
(curve.x_obs = p/p_sat, curve.q_obs = uptake in mol/kg). Those are third-party data whose sources do not all allow
redistribution (data/open/README.md). This script replaces them by their count and a SHA-256 of the exact values,
so a reader with the data set can check that the figure used the same points (paper/fig_examples.py recomputes them
from data/raw/dataset/isotherms.csv and checks the hash). Model curves, errors and every other field are unchanged.

    python scripts/strip_observed_points.py
"""
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent


def obs_hash(x, q):
    """SHA-256 of the observed points as float64 little-endian bytes, x then q."""
    a = np.concatenate([np.asarray(x, "<f8"), np.asarray(q, "<f8")])
    return hashlib.sha256(a.tobytes()).hexdigest()


def main():
    n = 0
    for f in sorted((ROOT / "results").glob("refit_diagnostics.shard*.jsonl")):
        out = []
        for line in f.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            c = r.get("curve", {})
            if "x_obs" in c:
                c["n_obs"] = len(c["x_obs"])
                c["obs_sha256"] = obs_hash(c.pop("x_obs"), c.pop("q_obs"))
                n += 1
            out.append(json.dumps(r))
        f.write_text("\n".join(out) + "\n")
    print(f"stripped the observed points from {n} records")


if __name__ == "__main__":
    main()
