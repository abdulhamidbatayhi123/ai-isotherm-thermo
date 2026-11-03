"""Minimum detectable effect of the H1 comparisons (PREREG_P3A.md section 7.3).

The spread of d = e_m(P) - e_m(X) across materials is estimated on the development set
(results/devcheck_runs.jsonl, the tuned configurations run on the development materials;
material-task values pooled, because only 3 development materials exist). Because that
estimate is weak, the SD used is the larger of the estimate and a pre-stated floor of
0.15 decades. The Wilcoxon signed-rank test (two-sided) is simulated at the confirmatory
sample size with normal d; the MDE is the smallest |mean d| with power >= 0.80, at alpha
0.05 / 4 (Holm's strictest step) and at 0.05. Reported as error ratios R = 10^-MDE.

  python scripts/mde.py <n_confirmatory>
Output: results/mde.json
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
SD_FLOOR = 0.15
N_SIM = 4000
SEED = 20261013
H1 = {"H1a": "F-hard", "H1b": "V-pen", "H1c": "A-hard", "H1d": "F-none"}


def power(delta, sd, n, alpha, rng):
    hits = 0
    for _ in range(N_SIM):
        d = rng.normal(delta, sd, n)
        if stats.wilcoxon(d, alternative="two-sided").pvalue < alpha:
            hits += 1
    return hits / N_SIM


def mde(sd, n, alpha, rng):
    lo, hi = 0.0, 1.5
    for _ in range(14):
        mid = 0.5 * (lo + hi)
        if power(mid, sd, n, alpha, rng) >= 0.80:
            hi = mid
        else:
            lo = mid
    return hi


def main():
    n = int(sys.argv[1])
    df = pd.DataFrame([json.loads(x) for x in (ROOT / "results/devcheck_runs.jsonl").read_text().splitlines()])
    df = df[df.task.isin(["E-high", "E-low"])]
    df["log10E"] = np.log10(df.E.where(np.isfinite(df.E) & (df.E > 0)))
    piv = df.pivot_table(index=["material", "task"], columns="cell", values="log10E")
    rng = np.random.default_rng(SEED)
    out = {"n_confirmatory": n, "sd_floor": SD_FLOOR, "comparisons": {}}
    for h, X in H1.items():
        d = (piv["P"] - piv[X]).dropna().to_numpy()
        sd_est = float(np.std(d, ddof=1)) if len(d) > 1 else float("nan")
        sd = max(sd_est if np.isfinite(sd_est) else 0.0, SD_FLOOR)
        m_strict = mde(sd, n, 0.05 / 4, rng)
        m_plain = mde(sd, n, 0.05, rng)
        out["comparisons"][h] = {"X": X, "n_dev_values": int(len(d)), "sd_estimate": sd_est, "sd_used": sd,
                                 "mde_decades_alpha_0.0125": m_strict, "mde_R_alpha_0.0125": 10**-m_strict,
                                 "mde_decades_alpha_0.05": m_plain, "mde_R_alpha_0.05": 10**-m_plain}
        print(f"{h} P vs {X:7s} sd_est={sd_est:.3f} sd_used={sd:.3f}  MDE: R <= {10**-m_strict:.3f} "
              f"(alpha 0.0125), R <= {10**-m_plain:.3f} (alpha 0.05)")
    (ROOT / "results/mde.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
