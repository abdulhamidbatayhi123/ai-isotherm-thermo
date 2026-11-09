"""Power of the H1 verdicts at the confirmatory sample size (PREREG_P3A.md section 7.3).

Rewritten before the freeze (review D1): the verdict itself is simulated with the frozen
analysis code (exact Wilcoxon test, exact Hodges-Lehmann intervals, the words of section 8),
not a normal approximation of the test alone.

For each spread sigma of d_m across materials in SIGMAS and two shapes of its distribution
(normal; Student t with 3 degrees of freedom scaled to the same SD, for outliers such as
ranked failures), with n materials:
  - P(equivalent | true d = 0): the probability of the words "equivalent within 25 %";
  - the minimum detectable effect: the smallest true |d| at which "P extrapolates better
    than X" is reached with probability >= 0.80 (the verdict MDE), and the smallest at which
    the test alone is significant with probability >= 0.80 (the test MDE).
Both at Holm's strictest step (p x 4 < 0.05, i.e. alpha 0.0125, for the four confirmatory H1
tests) and at alpha 0.05 (Holm's last step). Common random numbers across effect sizes make the power curves monotone.

The spread expected in the confirmatory data is estimated from the development-set pipeline
check (results/devcheck_runs.jsonl) and from the synthetic worlds
(results/verdicts_worlds_*.json) when present; both are reported next to the table.

  python scripts/mde.py [n]          default n = 14; writes results/mde.json
  python scripts/mde.py --spread-only   refreshes only the spread estimates in results/mde.json
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import analyse  # noqa: E402

SIGMAS = (0.10, 0.15, 0.20, 0.30, 0.50)
N_SIM = 2000
SEED = 20261013
N_H1 = len(analyse.H1)            # confirmatory H1 tests under Holm (4 since P3A-21)
STRICT = f"alpha_{0.05 / N_H1:g}"  # Holm's strictest step


def draws(shape, n, rng):
    if shape == "normal":
        return rng.standard_normal((N_SIM, n))
    return rng.standard_t(3, (N_SIM, n)) / math.sqrt(3.0)  # unit SD


def classify(d, holm_factor):
    p = analyse.wilcoxon_exact(d)
    p_adj = min(1.0, holm_factor * p)
    hl = analyse.hodges_lehmann(d)
    lo95, hi95 = analyse.hl_ci_exact(d, 0.95)
    lo90, hi90 = analyse.hl_ci_exact(d, 0.90)
    cls, _ = analyse.verdict(p_adj, 10**hl, 10**lo95, 10**hi95, 10**lo90, 10**hi90, "X")
    return cls, p_adj < 0.05


def rates(z, delta, sigma, holm_factor):
    out = [classify(delta + sigma * row, holm_factor) for row in z]
    return (np.mean([c == "P_better" for c, _ in out]), np.mean([s for _, s in out]),
            np.mean([c == "equivalent" for c, _ in out]))


def mde(z, sigma, holm_factor, which):
    """Smallest |d| (decades, P better) with power >= 0.80; inf if not reached by 2 decades."""
    k = 0 if which == "verdict" else 1
    if rates(z, -2.0, sigma, holm_factor)[k] < 0.80:
        return math.inf
    lo, hi = 0.0, 2.0
    for _ in range(12):
        mid = 0.5 * (lo + hi)
        if rates(z, -mid, sigma, holm_factor)[k] >= 0.80:
            hi = mid
        else:
            lo = mid
    return hi


def spread_estimates():
    est = {}
    f = ROOT / "results/devcheck_runs.jsonl"
    if f.exists():
        df = analyse.load(f)
        eP = analyse.e_by_material(df, "P")
        for h, X in analyse.H1.items():
            if X in set(df.cell):
                d, _, _ = analyse.paired_d(eP, analyse.e_by_material(df, X))
                est[f"dev {h}"] = {"n": len(d), "sd": float(np.std(d, ddof=1)) if len(d) > 1 else None}
    for f in sorted((ROOT / "results").glob("verdicts_worlds_*.json")):
        w = json.loads(f.read_text())
        for h, r in w.get("H1", {}).items():
            d = np.array(list(r["d_by_material"].values()))
            est[f"{f.stem.replace('verdicts_', '')} {h}"] = {"n": len(d), "sd": float(np.std(d, ddof=1))}
    return est


SPREAD_FLOOR = 0.15


def per_comparison(est):
    """Section 7.3 second table: per H1 comparison, the spread used is the largest of the
    development estimate, the largest world estimate and SPREAD_FLOOR; the verdict is then
    simulated at that spread (normal shape, Holm's strictest step, same seed)."""
    out = {}
    for h in analyse.H1:
        dev = (est.get(f"dev {h}") or {}).get("sd")
        worlds = [v["sd"] for k, v in est.items() if k.startswith("worlds_") and k.endswith(f" {h}")]
        wmax = max(worlds) if worlds else None
        used = max(x for x in (dev, wmax, SPREAD_FLOOR) if x is not None)
        z = draws("normal", 13, np.random.default_rng(SEED))
        v = mde(z, used, N_H1, "verdict")
        out[h] = {"X": analyse.H1[h], "dev_sd": dev, "worlds_max_sd": wmax, "sigma_used": used,
                  f"P_equivalent_at_d0_{STRICT}": float(rates(z, 0.0, used, N_H1)[2]),
                  f"verdict_mde_R_{STRICT}": 10**-v if math.isfinite(v) else 0.0}
        print("per-comparison", h, out[h], flush=True)
    return out


def main():
    if "--spread-only" in sys.argv:  # the table is seeded and unchanged; refresh the spread estimates
        out = json.loads((ROOT / "results/mde.json").read_text())
        out["spread_estimates"] = spread_estimates()
        out["per_comparison"] = per_comparison(out["spread_estimates"])
        (ROOT / "results/mde.json").write_text(json.dumps(out, indent=2))
        for k, v in out["spread_estimates"].items():
            print("spread", k, v)
        return
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 13
    rng = np.random.default_rng(SEED)
    out = {"n": n, "n_sim": N_SIM, "seed": SEED, "sesoi_R": 1.25, "table": []}
    for shape in ("normal", "t3"):
        z = draws(shape, n, rng)
        for sigma in SIGMAS:
            row = {"shape": shape, "sigma": sigma}
            for label, hf in ((STRICT, N_H1), ("alpha_0.05", 1)):
                row[f"P_equivalent_at_d0_{label}"] = float(rates(z, 0.0, sigma, hf)[2])
                v = mde(z, sigma, hf, "verdict")
                t = mde(z, sigma, hf, "test")
                row[f"verdict_mde_R_{label}"] = 10**-v if math.isfinite(v) else 0.0
                row[f"test_mde_R_{label}"] = 10**-t if math.isfinite(t) else 0.0
            out["table"].append(row)
            print(f"{shape:6s} sigma={sigma:.2f}  P(equiv|0) {row['P_equivalent_at_d0_' + STRICT]:.2f}"
                  f"  verdict MDE R {row['verdict_mde_R_' + STRICT]:.3f} (strict) "
                  f"{row['verdict_mde_R_alpha_0.05']:.3f} (a=0.05)  test MDE R {row['test_mde_R_' + STRICT]:.3f}",
                  flush=True)
    out["spread_estimates"] = spread_estimates()
    for k, v in out["spread_estimates"].items():
        print("spread", k, v)
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results/mde.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
