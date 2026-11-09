"""Confirmatory analysis and verdicts (PREREG_P3A.md sections 6 to 8). Every rule that turns
fits into words is in this file, which is frozen with the pre-registration.

  python scripts/analyse.py                       H1, H3, descriptive: results/confirmatory_runs.jsonl
                                                  H2: results/synthetic_h2.jsonl (if present)
  python scripts/analyse.py RUNS.jsonl [H2.jsonl] the same on other files (pipeline checks,
                                                  synthetic worlds)

Writes results/verdicts.json (or results/verdicts_<runs stem>.json) and prints a table.

Rules (PREREG 7.2, 8):
- e_m(X) = mean of log10 E over E-high and E-low. If either task failed (E infinite or an
  error), e_m(X) is a failure; it is never averaged over the surviving task (review A1).
  A missing record (a task never run) stops the analysis.
- A failure is ranked worst: its e is set to the comparison's worst finite e plus one decade.
- Test: exact two-sided Wilcoxon signed-rank test on d_m = e_m(P) - e_m(X), zero differences
  dropped, mid-ranks for ties, null distribution enumerated exactly (no scipy default).
- Estimate: Hodges-Lehmann; intervals: exact Wilcoxon inversion (order statistics of the
  Walsh averages), 95 % and 90 %; a bootstrap interval is reported as secondary.
- Holm over the four confirmatory H1 tests (H1b to H1e); Holm over the fifteen H2 tests.
  H1a (P against F-hard) is descriptive: the synthetic worlds showed it reads "P better" in
  every world, including one where van't Hoff is wrong, so it cannot fail (CORRECTIONS P3A-21).
"""
import functools
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
H1 = {"H1b": "V-pen", "H1c": "A-hard", "H1d": "F-none", "H1e": "C1"}
DESCRIPTIVE = {"H1a": "F-hard", "D-Vnone": "V-none", "D-Frel": "F-rel", "D-PK": "P-K"}
H2_CELLS = ("V-pen", "A-hard", "F-none")
H2_FAMILIES = ("KS", "DA", "FG", "HS", "TC")
H3_CELLS = ("F-none", "F-pen", "F-rel", "V-none", "V-pen", "A-none", "A-pen", "C1")
HARD_CELLS = ("P", "F-hard", "A-hard", "P-K")
E_TASKS = ("E-high", "E-low")
EXTRAP = "extrapolates better than"
HEAT = "estimates the isosteric heat better than"


# ---------------------------------------------------------------- per-material values
def e_by_material(df, cell, value="log10E", tasks=E_TASKS):
    """e_m(cell): mean of `value` over the tasks; NaN (a failure) if any task failed.
    Raises if a task record is missing."""
    sub = df[(df.cell == cell) & df.task.isin(tasks)]
    out = {}
    for mat, g in sub.groupby("material"):
        if sorted(g.task) != sorted(tasks):
            raise ValueError(f"{cell} / {mat}: tasks {sorted(g.task)} != {sorted(tasks)} (incomplete run)")
        v = g[value].to_numpy(float)
        out[mat] = float(v.mean()) if np.all(np.isfinite(v)) else float("nan")
    return pd.Series(out, dtype=float)


def paired_d(eP, eX):
    """d_m = e_m(P) - e_m(X) with failures ranked worst (worst finite + 1 decade)."""
    if set(eP.index) != set(eX.index):
        raise ValueError(f"materials differ: {sorted(set(eP.index) ^ set(eX.index))}")
    both = pd.concat([eP.rename("P"), eX.rename("X")], axis=1).sort_index()
    vals = both.to_numpy(float)
    worst = np.nanmax(vals) + 1.0 if np.isfinite(vals).any() else 0.0
    fails = {"P": int(both.P.isna().sum()), "X": int(both.X.isna().sum())}
    both = both.fillna(worst)
    return (both.P - both.X).to_numpy(float), list(both.index), fails


# ---------------------------------------------------------------- exact Wilcoxon
def _null_counts(r2):
    """Exact null distribution of 2*T+ (sum of doubled ranks given a + sign) under random
    signs; r2 are the doubled mid-ranks (integers). Returns counts indexed by 2*T+."""
    counts = np.zeros(int(sum(r2)) + 1)
    counts[0] = 1.0
    for r in r2:
        shifted = np.zeros_like(counts)
        shifted[r:] = counts[: len(counts) - r]
        counts = counts + shifted
    return counts


def wilcoxon_exact(d, tol=1e-12):
    """Two-sided exact Wilcoxon signed-rank p-value; zero differences dropped (Wilcoxon's
    method), ties given mid-ranks; the null distribution is enumerated exactly."""
    d = np.asarray(d, float)
    d = d[np.abs(d) > tol]
    n = len(d)
    if n == 0:
        return 1.0
    ranks = stats.rankdata(np.abs(d))  # mid-ranks
    r2 = np.rint(2 * ranks).astype(int)
    t2 = int(r2[d > 0].sum())
    counts = _null_counts(r2)
    probs = counts / counts.sum()
    mu = r2.sum() / 2.0
    support = np.arange(len(counts))
    extreme = np.abs(support - mu) >= abs(t2 - mu) - 1e-9
    return float(min(1.0, probs[extreme].sum()))


def hodges_lehmann(d):
    d = np.asarray(d, float)
    walsh = (d[:, None] + d[None, :]) / 2.0
    return float(np.median(walsh[np.triu_indices(len(d))]))


def hl_ci_exact(d, level):
    """Exact distribution-free interval for the HL shift: the order statistics C+1 and M-C of
    the M = n(n+1)/2 Walsh averages, where C is the largest value with P(T+ <= C) <= alpha/2
    under the untied null with n ranks. Coverage is at least `level`. Infinite if n is too
    small for any C."""
    d = np.asarray(d, float)
    n = len(d)
    C = _hl_critical(n, round(level, 10))
    if C < 0:
        return (-math.inf, math.inf)
    walsh = np.sort(((d[:, None] + d[None, :]) / 2.0)[np.triu_indices(n)])
    M = len(walsh)
    return (float(walsh[C]), float(walsh[M - C - 1]))


@functools.lru_cache(maxsize=None)
def _hl_critical(n, level):
    """Largest C with P(T+ <= C) <= (1 - level)/2 under the untied null with n ranks; -1 if none."""
    counts = _null_counts([2 * k for k in range(1, n + 1)])  # indexed by 2*T+
    cdf = np.cumsum(counts / counts.sum())[::2]  # P(T+ <= t), t = 0..n(n+1)/2
    ok = np.nonzero(cdf <= (1.0 - level) / 2 + 1e-12)[0]
    return int(ok[-1]) if len(ok) else -1


def bootstrap_ci(d, level, rng):
    d = np.asarray(d, float)
    hl = [hodges_lehmann(d[rng.integers(0, len(d), len(d))]) for _ in range(N_BOOT)]
    a = (1 - level) / 2
    return float(np.quantile(hl, a)), float(np.quantile(hl, 1 - a))


def holm(pvals):
    keys = sorted(pvals, key=lambda k: (pvals[k], k))
    out, running = {}, 0.0
    m = len(keys)
    for i, k in enumerate(keys):
        running = max(running, min(1.0, (m - i) * pvals[k]))
        out[k] = running
    return out


# ---------------------------------------------------------------- verdict words
def verdict(p_adj, R, lo95, hi95, lo90, hi90, X, verb=EXTRAP):
    """(class, words) of PREREG section 8, from R = 10^d (P's error relative to X's).
    The rows are evaluated in this order; every outcome falls in exactly one class."""
    sig = p_adj < 0.05
    within = 0.8 <= lo90 and hi90 <= 1.25
    if sig and R <= 0.8 and hi95 < 1:
        return "P_better", f"P {verb} {X}."
    if sig and R >= 1.25 and lo95 > 1:
        return "X_better", f"{X} {verb} P."
    if sig and within:
        return "differ_small", f"P and {X} differ, by less than 25 %."
    if within:
        return "equivalent", f"P and {X} are equivalent within 25 %."
    if sig:
        return "differ_uncertain", f"P and {X} differ; the size of the difference is uncertain."
    return "inconclusive", f"Inconclusive: the data cannot tell P and {X} apart."


VERDICT_CLASSES = ("P_better", "X_better", "differ_small", "equivalent", "differ_uncertain", "inconclusive")


def summary_sentences(cls):
    """Program-level sentences chosen by rule from the H1 classes (PREREG 8). All that apply
    are reported; the default applies when none does."""
    s = []
    if cls["H1b"] in ("P_better", "equivalent", "differ_small"):
        s.append("The hard constraints give admissibility at no accuracy cost larger than 25 %.")
    if cls["H1b"] == "X_better":
        s.append("The hard constraints cost accuracy.")
    if cls["H1c"] == "X_better":
        s.append("The temperature-invariant characteristic curve extrapolates better than the "
                 "learned potential.")
    if cls["H1e"] == "X_better":
        s.append("A dual-site Sips model with van't Hoff affinities extrapolates better than the "
                 "learned potential.")
    if cls["H1c"] == "P_better" and cls["H1d"] == "P_better" and cls["H1e"] == "P_better":
        s.append("The learned potential extrapolates better than the characteristic curve, the "
                 "dual-site Sips model and a generic network.")
    if not s:
        s.append("No program-level sentence applies; each comparison is reported on its own.")
    return s


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def h3_words(k, n, X):
    """(class, words) for the violation fraction of model X (PREREG 8); rows in order."""
    lo, hi = wilson(k, n)
    if n > 0 and lo >= 0.20:
        return "often", f"{X} violates in at least 20 % of fits ({k}/{n})."
    if k == 0:
        return "none", f"No violations detected for {X} (0/{n}; upper 95 % bound {hi:.2f})."
    if hi < 0.20:
        return "rare", f"{X} violates in fewer than 20 % of fits ({k}/{n})."
    return "some", f"{X} violates in some fits ({k}/{n}); whether the rate reaches 20 % is uncertain."


# ---------------------------------------------------------------- one comparison
def compare(eP, eX, X, p_value_store, verb):
    d, mats, fails = paired_d(eP, eX)
    p = wilcoxon_exact(d)
    p_value_store.append(p)
    return {"X": X, "d": d, "mats": mats, "fails": fails, "p": p, "verb": verb}


def finish(c, p_adj, rng):
    d = c["d"]
    hl = hodges_lehmann(d)
    lo95, hi95 = hl_ci_exact(d, 0.95)
    lo90, hi90 = hl_ci_exact(d, 0.90)
    b95 = bootstrap_ci(d, 0.95, rng)
    R = 10**hl
    ci95, ci90 = (10**lo95, 10**hi95), (10**lo90, 10**hi90)
    cls, words = verdict(p_adj, R, *ci95, *ci90, c["X"], c["verb"])
    return {"X": c["X"], "n_materials": len(d), "HL_d": hl, "R": R, "R_ci95": ci95, "R_ci90": ci90,
            "R_ci95_bootstrap": (10**b95[0], 10**b95[1]), "p": c["p"], "p_adj": p_adj,
            "failures": c["fails"], "class": cls, "verdict": words,
            "d_by_material": dict(zip(c["mats"], map(float, d)))}


def load(path, value_col="E"):
    """Run records from `path`, or from its shards <stem>.shard<k>.jsonl if they exist (the
    plain file and its shards together; a record appearing twice stops the analysis)."""
    path = Path(path)
    files = ([path] if path.exists() else []) + sorted(path.parent.glob(f"{path.stem}.shard*{path.suffix}"))
    if not files:
        raise FileNotFoundError(path)
    rows = [json.loads(x) for f in files for x in f.read_text().splitlines() if x.strip()]
    df = pd.DataFrame(rows)
    keys = [c for c in ("world", "family", "cell", "material", "task") if c in df]
    if df.duplicated(keys).any():
        raise ValueError(f"duplicate run records in {[f.name for f in files]}")
    v = pd.to_numeric(df[value_col], errors="coerce")
    if ((v <= 0) & np.isfinite(v)).any():  # an error of exactly zero or below can only be a bug
        raise ValueError(f"non-positive {value_col} in {[f.name for f in files]}")
    finite = np.isfinite(v) & (v > 0)
    df["log10E"] = np.where(finite, np.log10(v.where(finite, 1.0)), np.nan)
    return df


def material_class():
    p = ROOT / "data/inclusion_log.csv"
    if not p.exists():
        return {}
    log = pd.read_csv(p)
    return {f"{r.material} | {r.source}": r["class"] for _, r in log.iterrows()}


# ---------------------------------------------------------------- main analysis
def analyse_h1(df, rng):
    out = {"H1": {}, "descriptive": {}}
    eP = e_by_material(df, "P")
    comps, ps = {}, []
    for h, X in H1.items():
        comps[h] = compare(eP, e_by_material(df, X), X, ps, EXTRAP)
    p_adj = holm({h: c["p"] for h, c in comps.items()})
    for h, c in comps.items():
        out["H1"][h] = finish(c, p_adj[h], rng)
    out["summary"] = summary_sentences({h: r["class"] for h, r in out["H1"].items()})
    # descriptive comparisons: same estimate and words, unadjusted p, labelled descriptive
    for name, X in DESCRIPTIVE.items():
        if X not in set(df.cell):
            continue
        eX = e_by_material(df, X)
        c = compare(eP.loc[eX.index], eX, X, [], EXTRAP)
        out["descriptive"][name] = finish(c, c["p"], rng)
    # failures per cell; optimisation diagnostic P vs V-none (review B3)
    out["failures_per_cell"] = {c: int((~np.isfinite(pd.to_numeric(g.E, errors="coerce"))).sum())
                                for c, g in df.groupby("cell")}
    if "train_loss" in df and {"P", "V-none"} <= set(df.cell):
        a = df[df.cell == "P"].set_index(["material", "task"]).train_loss
        b = df[df.cell == "V-none"].set_index(["material", "task"]).train_loss
        r = np.log10(pd.to_numeric(a, errors="coerce") / pd.to_numeric(b, errors="coerce"))
        r = r[np.isfinite(r)]
        out["train_loss_log10_ratio_P_over_Vnone"] = {"median": float(r.median()) if len(r) else None,
                                                      "n": int(len(r))}
    # extrapolation distance and subgroups (review I2; PREREG 6.4)
    cls = material_class()
    for h, r in out["H1"].items():
        dd = pd.Series(r["d_by_material"])
        dist, ntrain = {}, {}
        for mat in dd.index:
            g = df[(df.material == mat) & (df.cell == "P") & df.task.isin(E_TASKS)]
            dist[mat] = float(np.mean([min(abs(row.T_out - t) for t in row.train_T) for row in g.itertuples()])) \
                if "T_out" in g and len(g) else float("nan")
            ntrain[mat] = int(min(len(t) for t in g.train_T)) if "train_T" in g and len(g) else 0
        dist = pd.Series(dist)
        ok = dist.notna()
        rho = stats.spearmanr(dist[ok], dd[ok]).statistic if ok.sum() >= 3 else float("nan")
        sub3 = dd[pd.Series(ntrain) >= 3]
        groups = {}
        for k in ("MOF", "COF"):
            g = dd[[cls.get(m) == k for m in dd.index]]
            if len(g):
                groups[k] = {"n": int(len(g)), "HL_d": hodges_lehmann(g.to_numpy()), "R": 10**hodges_lehmann(g.to_numpy())}
        r["descriptive"] = {"spearman_d_vs_heldout_distance": float(rho),
                            "subgroup_3plus_training_T": {"n": int(len(sub3)),
                                                          "HL_d": hodges_lehmann(sub3.to_numpy()) if len(sub3) else None},
                            "by_class": groups}
    return out


def analyse_h2(h2, rng):
    out = {}
    comps, ps = {}, []
    for fam in H2_FAMILIES:
        sub = h2[h2.family == fam]
        if sub.empty:
            continue
        eP = e_by_material(sub, "P")
        for X in H2_CELLS:
            comps[f"H2-{fam}-{X}"] = compare(eP, e_by_material(sub, X), X, ps, HEAT)
    p_adj = holm({k: c["p"] for k, c in comps.items()})
    for k, c in comps.items():
        out[k] = finish(c, p_adj[k], rng)
    return out


def analyse_h3(df):
    out = {"cells": {}, "P_bug_fits": []}
    for cell, g in df.groupby("cell"):
        v = [x for x in g["violations"] if isinstance(x, dict)]
        n_err = int(len(g) - len(v))  # a failed fit has no model to judge: out of n, reported apart
        k_in = sum(_violates(x, "in") for x in v)
        k_out = sum(_violates(x, "out") for x in v)
        k_strict = sum(any(x[c] > 0 for c in ("nonmonotone", "negative_q")) for x in v)
        n = int(len(v))
        cls, words = h3_words(k_in, n, cell)
        out["cells"][cell] = {"fits": n, "violating_in_domain": int(k_in), "violating_extrapolated_band": int(k_out),
                              "violating_strict": int(k_strict), "failed_fits": n_err,
                              "fraction": k_in / n if n else float("nan"), "wilson95": wilson(k_in, n),
                              "class": cls, "words": words}
        if cell == "P":
            out["P_bug_fits"] = [f"{r.material} / {r.task}" for r in g.itertuples()
                                 if isinstance(r.violations, dict) and _p_bug(r.violations)]
    # H3 prediction (revised before the freeze, P3A-21): penalties leave violations that the hard
    # constraints remove. F-none violates in every synthetic world, so it is reported, not predicted.
    vpen = out["cells"].get("V-pen", {}).get("class")
    p_none = out["cells"].get("P", {}).get("class") == "none"
    out["prediction"] = {"V_pen_class": vpen, "P_none": p_none,
                         "met": vpen in ("some", "often") and p_none}
    return out


def _violates(v, dom):
    return bool(v.get(f"tol_drop_isotherms_{dom}", 0) > 0 or v.get(f"tol_negative_points_{dom}", 0) > 0)


def _p_bug(v):
    return bool(v["nonmonotone"] > 0 or v["negative_q"] > 0 or v["undefined_qst"] > 0)


def main():
    args = sys.argv[1:]
    src = Path(args[0]) if args else ROOT / "results/confirmatory_runs.jsonl"
    h2src = Path(args[1]) if len(args) > 1 else (ROOT / "results/synthetic_h2.jsonl" if not args else None)
    if h2src is not None and not h2src.exists() and not list(h2src.parent.glob(f"{h2src.stem}.shard*")):
        h2src = None
    rng = np.random.default_rng(BOOT_SEED)
    df = load(src)
    out = {"input": src.name}
    out.update(analyse_h1(df, rng))
    if "violations" in df:
        out["H3"] = analyse_h3(df)
    if h2src is not None:
        out["H2_input"] = h2src.name
        out["H2"] = analyse_h2(load(h2src, "qst_rmse_kJ"), rng)
        out["H2_secondary_state_matched"] = analyse_h2(load(h2src, "qst_rmse_state_kJ"), rng)
    name = "verdicts.json" if src.name == "confirmatory_runs.jsonl" else f"verdicts_{src.stem}.json"
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / name).write_text(json.dumps(out, indent=2, default=float))
    for h, r in out["H1"].items():
        print(f"{h} P vs {r['X']:7s} n={r['n_materials']:2d} R={r['R']:.3f} "
              f"95% [{r['R_ci95'][0]:.3f}, {r['R_ci95'][1]:.3f}] p_holm={r['p_adj']:.4f}  {r['verdict']}")
    for s in out["summary"]:
        print("SUMMARY:", s)
    for h, r in out.get("H2", {}).items():
        print(f"{h:14s} R={r['R']:.3f} p_holm={r['p_adj']:.4f}  {r['verdict']}")
    if "H3" in out:
        for cell, r in out["H3"]["cells"].items():
            print(f"H3 {cell:7s} {r['words']}")
        print("H3 prediction met:", out["H3"]["prediction"]["met"])
        if out["H3"]["P_bug_fits"]:
            sys.exit(f"HALT (PREREG 6.2): P violates on {len(out['H3']['P_bug_fits'])} fits; a bug to fix first.")
    print("written", ROOT / "results" / name)
    return out


if __name__ == "__main__":
    main()
