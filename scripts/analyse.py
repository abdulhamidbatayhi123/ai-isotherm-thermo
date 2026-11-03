"""Confirmatory analysis and verdicts (PREREG_P3A.md sections 6 to 8).

  python scripts/analyse.py                      results/confirmatory_runs.jsonl
  python scripts/analyse.py results/devcheck_runs.jsonl   (pipeline check on the development set)

Writes results/verdicts.json (or results/verdicts_<input stem>.json) and prints a table.
A failed fit (E infinite or an error) is ranked worst: log10 E = the comparison's worst
finite value plus one decade (stated in PREREG section 7.2).
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
BOOT_SEED = 20261013
N_BOOT = 10_000
SESOI = math.log10(1.25)  # |d| = 0.097: a 25 % change in error
H1 = {"H1a": "F-hard", "H1b": "V-pen", "H1c": "A-hard", "H1d": "F-none"}


def e_by_material(df, cell):
    """e_m(X) = mean log10 E over the tasks E-high and E-low (PREREG 6.1)."""
    sub = df[(df.cell == cell) & df.task.isin(["E-high", "E-low"])]
    return sub.groupby("material")["log10E"].apply(lambda v: v.mean() if len(v) == 2 else np.nan)


def hodges_lehmann(d):
    d = np.asarray(d)
    walsh = (d[:, None] + d[None, :]) / 2.0
    return float(np.median(walsh[np.triu_indices(len(d))]))


def bootstrap_ci(d, level, rng):
    d = np.asarray(d)
    hl = [hodges_lehmann(d[rng.integers(0, len(d), len(d))]) for _ in range(N_BOOT)]
    a = (1 - level) / 2
    return float(np.quantile(hl, a)), float(np.quantile(hl, 1 - a))


def holm(pvals):
    keys = sorted(pvals, key=pvals.get)
    out, running = {}, 0.0
    m = len(keys)
    for i, k in enumerate(keys):
        running = max(running, min(1.0, (m - i) * pvals[k]))
        out[k] = running
    return out


def verdict(p_adj, R, lo95, hi95, lo90, hi90, X):
    """The words of PREREG section 8, from R = 10^d (P's error relative to X's)."""
    if p_adj < 0.05 and R <= 0.8 and hi95 < 1:
        return f"P extrapolates better than {X}."
    if p_adj < 0.05 and R >= 1.25 and lo95 > 1:
        return f"{X} extrapolates better than P."
    if 0.8 <= lo90 and hi90 <= 1.25:
        return f"P and {X} are equivalent within 25 %."
    if p_adj < 0.05 and 0.8 < R < 1.25:
        return f"P and {X} differ, by less than 25 %."
    return f"Inconclusive: the data cannot tell P and {X} apart."


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "results/confirmatory_runs.jsonl"
    df = pd.DataFrame([json.loads(x) for x in src.read_text().splitlines()])
    finite = np.isfinite(df.E) & (df.E > 0)
    df["log10E"] = np.where(finite, np.log10(df.E.where(finite, 1.0)), np.nan)
    rng = np.random.default_rng(BOOT_SEED)
    out = {"input": src.name, "H1": {}, "H3": {}}
    pvals, stash = {}, {}
    eP = e_by_material(df, "P")
    for h, X in H1.items():
        eX = e_by_material(df, X)
        both = pd.concat([eP.rename("P"), eX.rename("X")], axis=1)
        worst = np.nanmax(both.values) + 1.0
        both = both.fillna(worst)  # failures ranked worst
        d = (both.P - both.X).to_numpy()
        if len(d) < 2 or np.allclose(d, 0):
            p = 1.0
        else:
            p = float(stats.wilcoxon(d, alternative="two-sided").pvalue)
        pvals[h] = p
        stash[h] = (X, d, list(both.index))
    p_adj = holm(pvals)
    for h, (X, d, mats) in stash.items():
        hl = hodges_lehmann(d)
        lo95, hi95 = bootstrap_ci(d, 0.95, rng)
        lo90, hi90 = bootstrap_ci(d, 0.90, rng)
        R, ci95, ci90 = 10**hl, (10**lo95, 10**hi95), (10**lo90, 10**hi90)
        out["H1"][h] = {"X": X, "n_materials": len(d), "HL_d": hl, "R": R, "R_ci95": ci95, "R_ci90": ci90,
                        "p": pvals[h], "p_holm": p_adj[h],
                        "verdict": verdict(p_adj[h], R, *ci95, *ci90, X),
                        "d_by_material": dict(zip(mats, map(float, d)))}
    for cell in sorted(df.cell.unique()):
        sub = df[df.cell == cell]
        viol = sub["violations"].apply(lambda v: isinstance(v, dict) and any(
            v[k] > 0 for k in ("nonmonotone", "negative_q", "undefined_qst", "qst_out_of_range")))
        k, n = int(viol.sum()), int(len(sub))
        out["H3"][cell] = {"violating_fits": k, "fits": n, "fraction": k / n if n else float("nan"),
                           "wilson95": wilson(k, n)}
    name = "verdicts.json" if src.name == "confirmatory_runs.jsonl" else f"verdicts_{src.stem}.json"
    (ROOT / "results" / name).write_text(json.dumps(out, indent=2))
    for h, r in out["H1"].items():
        print(f"{h} P vs {r['X']:7s} n={r['n_materials']:2d} R={r['R']:.3f} "
              f"95% [{r['R_ci95'][0]:.3f}, {r['R_ci95'][1]:.3f}] p_holm={r['p_holm']:.4f}  {r['verdict']}")
    for cell, r in out["H3"].items():
        print(f"H3 {cell:7s} violating {r['violating_fits']}/{r['fits']} "
              f"Wilson 95% [{r['wilson95'][0]:.3f}, {r['wilson95'][1]:.3f}]")


if __name__ == "__main__":
    main()
