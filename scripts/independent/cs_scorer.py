"""cs_scorer.py - independent scorer for Paper 3A, written by cs-org1 (Claude Science) on 2026-11-09
from the text of PREREG_P3A.md sections 6 to 8 at commit d498792 ONLY; aligned on 2026-11-09 with the
text of sections 7.2 and 7.3 at commit fc80d72 (TG1, TG5, TG6 now written there; n = 13), and on
2026-11-09 (cs-org2) with sections 6 to 8 at commit 5315654 (H1a descriptive, Holm over H1b-H1e,
H1b non-inferiority, H3 prediction on V-pen and P, one "inconclusive" wording, descriptive prefix,
material set against data/dataset_summary.json). The 5315654 changes were written from the text
before analyse.py at 5315654 was compared. It does not import, and was
written without reading, scripts/analyse.py at d498792. (cs-org1 did read analyse.py at f0c98d4
during review T1, so independence from the older scorer is partial.)

Where the text leaves a choice open, the choice made here is marked TEXT-GAP and listed in
the output under "text_gaps"; a disagreement with analyse.py at such a point is a gap in the
text, not necessarily an error in either scorer (PREREG section 10: the text governs).

Usage:
  python cs_scorer.py RUNS.jsonl [RUNS.shard1.jsonl ...] [--h2 H2.jsonl [H2.shard1.jsonl ...]]
                      [--out cs_verdicts.json] [--no-bootstrap] [--expect-n 13]
                      [--dataset-summary data/dataset_summary.json]   (confirmatory run: 7.2)
  python cs_scorer.py --selftest

Inputs: JSON lines as written by scripts/run_confirmatory.py (cell, material, task, E, error,
violations{...}) and scripts/run_synthetic_h2.py (cell, material, family, task, qst_rmse_kJ, error).
Dependencies: numpy only (standard library otherwise).
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

SESOI_LO, SESOI_HI = 0.8, 1.25            # section 7.2 / 8
ALPHA = 0.05                              # "significant": Holm-adjusted p below 0.05
H1 = {"H1b": "V-pen", "H1c": "A-hard", "H1d": "F-none", "H1e": "C1"}  # 7.1 at 5315654: Holm over four
H1A = ("H1a", "F-hard")                         # 7.1 at 5315654: descriptive, unadjusted p
DESCRIPTIVE = {"D-Vnone": "V-none", "D-Frel": "F-rel", "D-PK": "P-K"}  # 6.4
DESC_PREFIX = "Descriptive (unadjusted, not a test): "                 # 7.2 at 5315654
H3_PREDICTION_VPEN = ("some", "often")          # 7.1 at 5315654 ("violates in some fits" / "at least 20 %")
H2_COMPARATORS = ("V-pen", "A-hard", "F-none")                                          # 7.1
TASKS = ("E-high", "E-low")                                                             # 6.1
H2_FAMILIES = ("DA", "FG", "HS", "KS", "TC")                                            # 6.3a, 7.1
N_PREREG = 13                                                                           # 7.2 (fc80d72)
Z95 = 1.959963984540054
BOOT_N, BOOT_SEED = 10_000, 20261013

TEXT_GAPS = [
    "TG1 [in text, 7.2 at fc80d72] H3 denominator: a failed fit is left out of n and reported "
    "separately; its failure counts in H1.",
    "TG2 [in text, 7.2 at fc80d72] Exact HL intervals: C = largest c with P(W+ <= c) <= alpha/2 "
    "under the no-ties null for all n (zeros included); [W_(C+1), W_(M-C)]; unbounded if no c.",
    "TG3 [in text, 7.2 at fc80d72] Two-sided exact p = P(|W+ - mu| >= |w - mu|) (computed as "
    "2 x the smaller tail, capped at 1; equal because the null is symmetric).",
    "TG4 [in text, 7.2 at fc80d72] Ties in |d| are exact floating-point equality.",
    "TG5 [in text, 7.2 at fc80d72] An error value of zero or below stops the analysis. This "
    "scorer stops on any finite E (or qst_rmse_kJ) <= 0, whatever the record's error field.",
    "TG6 [in text, 7.2 at fc80d72] A duplicated record stops the analysis: ANY second record "
    "with the same (cell, material, task[, family]) stops, even if identical.",
    "TG7 [in text, 7.2 at fc80d72] Worst finite e = max over the finite e_m of BOTH P and X; "
    "if neither has one, every d_m is 0.",
    "TG8 [in text, 7.2 at fc80d72] Bootstrap: numpy default_rng(20261013), resampling "
    "materials, percentile interval of HL. Secondary; the draw order (95 % then 90 %, H1a..e "
    "then H2) is not in the text, so values need not match analyse.py bit for bit.",
    "TG9 [in text, 7.2 at fc80d72] The material set is every material in the run file; a "
    "missing (cell, material, E-high/E-low) record stops.",
    "TG10 [in text, 7.2 at fc80d72] H3 uses the tolerant 'in' counts of study.violation_counts.",
    "TG11 [open] A NaN E: the text defines failure as 'E infinite, or an exception'; this "
    "scorer treats NaN as a failure (not a stop).",
    "TG12 [open] n = 13 is stated (7.2) but nothing says a run file with another number of "
    "materials stops; this scorer reports n_matches_prereg and stops only with --expect-n.",
    "TG14 [open, 5315654] H3 prediction: 'V-pen reads \"violates in some fits\" or \"violates in "
    "at least 20 % of fits\"'. Read literally, the row 'fewer than 20 %' (k > 0, hi < 0.20) does "
    "NOT meet it, although 'penalties leave violations' would. This scorer applies the literal "
    "reading and also reports the k > 0 reading.",
    "TG15 [open, 5315654] H3 class labels are not named in section 8; this scorer uses the names "
    "of the 7.4 outcome table ('often', 'some', 'none') and 'rare' for the 'fewer than 20 %' row.",
    "TG16 [open, 5315654] H1a for 'materials with at least 3 training temperatures': taken as the "
    "minimum over P's E-high/E-low records of len(train_T) >= 3; needs train_T in the run file.",
    "TG13 [open] H2 'fifteen tests' / 'each of the five truth families': this scorer stops if "
    "the H2 file lacks one of KS, DA, FG, HS, TC or has another family (treated as a missing "
    "record), so Holm is always over 15. The H2 material set is every material in the H2 "
    "file; it is reported whether it equals the run file's set.",
]


class StopAnalysis(Exception):
    pass


# ---------------------------------------------------------------- reading
def read_jsonl(paths):
    rows = []
    for p in paths:
        for line in Path(p).read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


def is_failed(value, error):
    """Section 7.2: a fit fails if its error is infinite or it raised an exception."""
    v = None if value is None else float(value)
    if v is not None and not math.isnan(v) and not math.isinf(v) and v <= 0:
        raise StopAnalysis(f"non-positive error value {v} (section 7.2, TG5)")
    if error not in (None, "", "null"):
        return True
    if v is None or math.isnan(v) or math.isinf(v):
        return True  # TG11: NaN counted as a failure
    return False


def index_records(rows, key_fields, value_field):
    idx = {}
    for r in rows:
        k = tuple(r[f] for f in key_fields)
        if k in idx:  # section 7.2 at fc80d72: "a duplicated record stops the analysis"
            raise StopAnalysis(f"duplicated record {k} (section 7.2, TG6)")
        idx[k] = (r.get(value_field), r.get("error"))
    return idx


# ---------------------------------------------------------------- per-material e and d
def e_material(idx, cell, material, prefix=()):
    """Section 6.1: mean log10 over E-high and E-low; a failure if either task failed."""
    vals = []
    for t in TASKS:
        k = prefix + (cell, material, t)
        if k not in idx:
            raise StopAnalysis(f"missing record {k} (section 7.2)")
        v, err = idx[k]
        if is_failed(v, err):
            return None  # failed e_m, never the surviving task's value
        vals.append(math.log10(float(v)))
    return sum(vals) / 2.0


def d_vector(idx, materials, X, prefix=()):
    eP = {m: e_material(idx, "P", m, prefix) for m in materials}
    eX = {m: e_material(idx, X, m, prefix) for m in materials}
    finite = [v for v in list(eP.values()) + list(eX.values()) if v is not None]
    worst = (max(finite) + 1.0) if finite else 0.0  # TG7
    d = []
    for m in materials:
        a = eP[m] if eP[m] is not None else worst
        b = eX[m] if eX[m] is not None else worst
        d.append(a - b)
    fails = {"P": sum(v is None for v in eP.values()), X: sum(v is None for v in eX.values())}
    return np.array(d, dtype=float), fails


# ---------------------------------------------------------------- exact signed-rank machinery
def midranks(x):
    """Mid-ranks (1-based) of x; ties share the mean rank (TG4: exact equality)."""
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), dtype=float)
    i = 0
    xs = x[order]
    while i < len(x):
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j + 2) / 2.0
        i = j + 1
    return ranks


def signed_rank_null_counts(doubled_ranks):
    """Counts of each value of S = sum of the doubled ranks given a positive sign, over all 2^n
    sign assignments (exact; integers)."""
    total = int(sum(doubled_ranks))
    counts = [0] * (total + 1)
    counts[0] = 1
    for a in doubled_ranks:
        new = counts[:]
        for s in range(total - a, -1, -1):
            if counts[s]:
                new[s + a] += counts[s]
        counts = new
    return counts


def wilcoxon_exact_two_sided(d):
    """Section 7.2: zeros dropped, mid-ranks for ties, null enumerated exactly (TG3)."""
    nz = d[d != 0.0]
    n = len(nz)
    if n == 0:
        return 1.0, 0.0, 0
    r = midranks(np.abs(nz))
    a = [int(round(2 * x)) for x in r]
    w2 = int(round(2 * r[nz > 0].sum()))
    counts = signed_rank_null_counts(a)
    tot = 2 ** n
    lower = sum(counts[: w2 + 1]) / tot
    upper = sum(counts[w2:]) / tot
    return min(1.0, 2.0 * min(lower, upper)), w2 / 2.0, n


def hodges_lehmann(d):
    n = len(d)
    w = [(d[i] + d[j]) / 2.0 for i in range(n) for j in range(i, n)]
    return float(np.median(w)), np.sort(np.array(w))


def hl_ci_exact(d, level):
    """TG2: distribution-free interval from Walsh order statistics, no-ties null for n."""
    n = len(d)
    _, walsh = hodges_lehmann(d)
    M = len(walsh)
    counts = signed_rank_null_counts(list(range(1, n + 1)))  # ranks 1..n, undoubled
    tot = 2 ** n
    a2 = (1.0 - level) / 2.0
    C, cum = -1, 0
    for c, k in enumerate(counts):
        cum += k
        if cum / tot <= a2 + 1e-15:
            C = c
        else:
            break
    if C < 0:
        return -math.inf, math.inf, C
    return float(walsh[C]), float(walsh[M - C - 1]), C


def bootstrap_ci(d, level, rng):
    hl = np.empty(BOOT_N)
    n = len(d)
    for b in range(BOOT_N):
        hl[b] = hodges_lehmann(d[rng.integers(0, n, n)])[0]
    a = (1 - level) / 2
    return float(np.quantile(hl, a)), float(np.quantile(hl, 1 - a))


def holm(p):
    keys = sorted(p, key=lambda k: p[k])
    m, run, out = len(keys), 0.0, {}
    for i, k in enumerate(keys):
        run = max(run, min(1.0, (m - i) * p[k]))
        out[k] = run
    return out


# ---------------------------------------------------------------- words (section 8)
CLASS_WORDS = {
    "P_better": "P {verb} {X}.",
    "X_better": "{X} {verb} P.",
    "differ_lt25": "P and {X} differ, by less than 25 %.",
    "equivalent": "P and {X} are equivalent within 25 %.",
    "differ_uncertain": "P and {X} differ; the size of the difference is uncertain.",
    "inconclusive": "Inconclusive at this sample size: the data cannot tell P and {X} apart.",
}


def verdict_class(p_adj, R, lo95, hi95, lo90, hi90):
    sig = p_adj < ALPHA
    inside = SESOI_LO <= lo90 and hi90 <= SESOI_HI
    if sig and R <= SESOI_LO and hi95 < 1:
        return "P_better"
    if sig and R >= SESOI_HI and lo95 > 1:
        return "X_better"
    if sig and inside:
        return "differ_lt25"
    if (not sig) and inside:
        return "equivalent"
    if sig:
        return "differ_uncertain"
    return "inconclusive"


def wilson(k, n, z=Z95):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def h3_class(k, n):
    lo, hi = wilson(k, n)
    if n > 0 and lo >= 0.20:
        return "often", lo, hi
    if k == 0:
        return "none", lo, hi
    if hi < 0.20:
        return "rare", lo, hi
    return "some", lo, hi


def h3_words(cell, cls, k, n, hi):
    return {
        "often": f"{cell} violates in at least 20 % of fits ({k}/{n}).",
        "none": f"No violations detected for {cell} (0/{n}; upper 95 % bound {hi:.2f}).",
        "rare": f"{cell} violates in fewer than 20 % of fits ({k}/{n}).",
        "some": f"{cell} violates in some fits ({k}/{n}); whether the rate reaches 20 % is uncertain.",
    }[cls]


def summary_sentences(c):
    """Section 8 at 5315654: program-level sentences from the four confirmatory H1 classes."""
    out = []
    if c["H1b"] in ("P_better", "equivalent", "differ_lt25"):
        out.append("The hard constraints give admissibility at no accuracy cost larger than 25 %.")
    if c["H1b"] == "X_better":
        out.append("The hard constraints cost accuracy.")
    if c["H1c"] == "X_better":
        out.append("The temperature-invariant characteristic curve extrapolates better than the "
                   "learned potential.")
    if c["H1e"] == "X_better":
        out.append("A dual-site Sips model with van't Hoff affinities extrapolates better than the "
                   "learned potential.")
    if c["H1c"] == "P_better" and c["H1d"] == "P_better" and c["H1e"] == "P_better":
        out.append("The learned potential extrapolates better than the characteristic curve, the "
                   "dual-site Sips model and a generic network.")
    if not out:
        out.append("No program-level sentence applies; each comparison is reported on its own.")
    return out


# ---------------------------------------------------------------- one comparison family
def compare(idx, materials, comparisons, verb, prefix_of, do_boot, rng):
    raw, stash = {}, {}
    for h, (X, prefix) in comparisons.items():
        d, fails = d_vector(idx, materials, X, prefix)
        p, wplus, n_eff = wilcoxon_exact_two_sided(d)
        raw[h], stash[h] = p, (X, d, fails, wplus, n_eff)
    padj = holm(raw)
    out = {}
    for h, (X, d, fails, wplus, n_eff) in stash.items():
        hl, _ = hodges_lehmann(d)
        lo95, hi95, C95 = hl_ci_exact(d, 0.95)
        lo90, hi90, C90 = hl_ci_exact(d, 0.90)
        R = 10 ** hl
        Rci95 = (10 ** lo95 if lo95 > -math.inf else 0.0, 10 ** hi95 if hi95 < math.inf else math.inf)
        Rci90 = (10 ** lo90 if lo90 > -math.inf else 0.0, 10 ** hi90 if hi90 < math.inf else math.inf)
        cls = verdict_class(padj[h], R, Rci95[0], Rci95[1], Rci90[0], Rci90[1])
        rec = {"X": X, "n_materials": len(d), "n_nonzero": n_eff, "W_plus": wplus,
               "HL_d": hl, "R": R, "R_ci95_exact": Rci95, "R_ci90_exact": Rci90,
               "walsh_C95": C95, "walsh_C90": C90, "p": raw[h], "p_holm": padj[h],
               "class": cls, "words": CLASS_WORDS[cls].format(X=X, verb=verb),
               "failed_materials": fails, "d_by_material": dict(zip(materials, map(float, d)))}
        if do_boot:
            b95 = bootstrap_ci(d, 0.95, rng)
            b90 = bootstrap_ci(d, 0.90, rng)
            rec["R_ci95_bootstrap"] = (10 ** b95[0], 10 ** b95[1])
            rec["R_ci90_bootstrap"] = (10 ** b90[0], 10 ** b90[1])
        out[h] = rec
    return out


# ---------------------------------------------------------------- main scoring
def confirmatory_materials(summary_path):
    summ = json.loads(Path(summary_path).read_text(encoding="utf-8"))
    return sorted(k for k, v in summ.items() if v.get("set") == "confirmatory")


def score(run_rows, h2_rows=None, do_boot=True, expect_n=None, expect_materials=None):
    rng = np.random.default_rng(BOOT_SEED)
    idx = index_records(run_rows, ("cell", "material", "task"), "E")
    materials = sorted({r["material"] for r in run_rows})
    if expect_n is not None and len(materials) != expect_n:
        raise StopAnalysis(f"{len(materials)} materials in the run file, expected {expect_n} (TG12)")
    if expect_materials is not None and materials != sorted(expect_materials):
        raise StopAnalysis(f"material set {materials} differs from the frozen confirmatory set "
                           f"{sorted(expect_materials)} (section 7.2)")
    res = {"scorer": "cs_scorer.py (from PREREG text; aligned with sections 6-8 at 5315654)",
           "n_materials": len(materials), "n_prereg": N_PREREG,
           "n_matches_prereg": len(materials) == N_PREREG,
           "materials": materials, "text_gaps": TEXT_GAPS}

    # P bug rule (6.2): strict nonmonotone, negative_q, undefined_qst must be 0 for P
    bugs = []
    flags = []
    for r in run_rows:
        v = r.get("violations")
        if not isinstance(v, dict):
            continue
        strict = (v.get("nonmonotone", 0), v.get("negative_q", 0), v.get("undefined_qst", 0))
        if r["cell"] == "P" and any(x > 0 for x in strict):
            bugs.append((r["material"], r["task"], strict))
        if r["cell"] in ("F-hard", "A-hard", "P-K") and (strict[0] > 0 or strict[1] > 0):
            flags.append((r["cell"], r["material"], r["task"], strict[:2]))
    res["construction_flags_non_P"] = flags
    if bugs:
        res["halted"] = f"P shows non-zero strict counts (bug rule, section 6.2): {bugs}"
        return res

    # H1 (Holm over the four confirmatory tests H1b-H1e; section 7.1 at 5315654)
    EXV = "extrapolates better than"
    res["H1"] = compare(idx, materials, {h: (X, ()) for h, X in H1.items()}, EXV, None, do_boot, rng)
    res["summary_sentences"] = summary_sentences({h: res["H1"][h]["class"] for h in H1})
    hi95_b = res["H1"]["H1b"]["R_ci95_exact"][1]
    res["H1b_prediction"] = {"rule": "upper exact 95 % bound of R < 1.25 (section 7.3)",
                             "upper95": hi95_b, "met": bool(hi95_b < SESOI_HI)}

    def descriptive(name, X, mats):
        r = compare(idx, mats, {name: (X, ())}, EXV, None, do_boot, rng)[name]  # Holm of one = raw p
        r["words"] = DESC_PREFIX + r["words"]
        return r

    # H1a, descriptive (7.1): overall and for materials with >= 3 training temperatures (TG16)
    h, X = H1A
    res["H1a_descriptive"] = {"all": descriptive(h, X, materials)}
    ntrain = {}
    for r in run_rows:
        if r["cell"] == "P" and r["task"] in TASKS and isinstance(r.get("train_T"), list):
            ntrain[r["material"]] = min(ntrain.get(r["material"], 99), len(r["train_T"]))
    if len(ntrain) == len(materials):
        sub = [m for m in materials if ntrain[m] >= 3]
        res["H1a_descriptive"]["min3_training_T"] = (descriptive(h, X, sub) if sub else
                                                     {"n_materials": 0})
    else:
        res["H1a_descriptive"]["min3_training_T"] = "not computed: train_T missing (TG16)"
    res["descriptive"] = {}
    for name, X in DESCRIPTIVE.items():
        mats_x = sorted({r["material"] for r in run_rows if r["cell"] == X})
        if mats_x:
            res["descriptive"][name] = descriptive(name, X, mats_x)

    # H3 per cell (all tasks)
    h3 = {}
    for cell in sorted({r["cell"] for r in run_rows}):
        sub = [r for r in run_rows if r["cell"] == cell]
        failed = [r for r in sub if is_failed(r.get("E"), r.get("error"))]
        ok = [r for r in sub if r not in failed]
        for r in ok:
            if not isinstance(r.get("violations"), dict):
                raise StopAnalysis(f"missing violations for {(cell, r['material'], r['task'])}")
        k = sum(1 for r in ok if r["violations"]["tol_drop_isotherms_in"] > 0
                or r["violations"]["tol_negative_points_in"] > 0)
        n = len(ok)
        cls, lo, hi = h3_class(k, n)
        h3[cell] = {"violating_fits": k, "fits": n, "failed_fits_excluded": len(failed),
                    "wilson95": (lo, hi), "class": cls, "words": h3_words(cell, cls, k, n, hi)}
    res["H3"] = h3
    if "P" in h3 and "V-pen" in h3:  # 7.1 at 5315654
        res["H3_prediction"] = {
            "rule": "V-pen reads 'some' or 'often' and P reads 'none' (section 7.1)",
            "met": h3["V-pen"]["class"] in H3_PREDICTION_VPEN and h3["P"]["class"] == "none",
            "met_if_any_violation_counts (TG14)": h3["V-pen"]["violating_fits"] > 0
            and h3["P"]["class"] == "none"}

    # H2 (Holm over fifteen)
    if h2_rows:
        idx2 = index_records(h2_rows, ("family", "cell", "material", "task"), "qst_rmse_kJ")
        mats2 = sorted({r["material"] for r in h2_rows})
        fams = sorted({r["family"] for r in h2_rows})
        if tuple(fams) != H2_FAMILIES:  # TG13: Holm over fifteen needs all five families
            raise StopAnalysis(f"H2 families {fams}, expected {list(H2_FAMILIES)} (TG13)")
        res["H2_materials_equal_run_materials"] = mats2 == materials
        comps = {f"H2-{fam}-{X}": (X, (fam,)) for fam in fams for X in H2_COMPARATORS}
        res["H2"] = compare(idx2, mats2, comps, "estimates the isosteric heat better than",
                            None, do_boot, rng)
        res["H2_n_tests"] = len(comps)
    return res


# ---------------------------------------------------------------- self-test (hand-checkable)
def selftest():
    # Walsh / HL: [1, 2, 9] -> Walsh 1, 1.5, 5, 2, 5.5, 9 -> median 3.5
    assert abs(hodges_lehmann(np.array([1.0, 2.0, 9.0]))[0] - 3.5) < 1e-12
    # exact signed rank, n = 5 all positive: P(W+ = 15) = 1/32, two-sided 2/32
    p, w, n = wilcoxon_exact_two_sided(np.array([1.0, 2, 3, 4, 5]))
    assert n == 5 and w == 15 and abs(p - 2 / 32) < 1e-12
    # zeros dropped
    p0, _, n0 = wilcoxon_exact_two_sided(np.array([0.0, 1, 2, 3, 4, 5]))
    assert n0 == 5 and abs(p0 - p) < 1e-12
    # ties: [1, 1, -2] -> mid-ranks 1.5, 1.5, 3; W+ = 3; null of doubled ranks {3,3,6}
    p_t, w_t, _ = wilcoxon_exact_two_sided(np.array([1.0, 1.0, -2.0]))
    assert w_t == 3.0 and abs(p_t - 1.0) < 1e-12
    # n = 14 no-ties null: known two-sided 5 % critical value of the signed-rank test is 21
    cnt = signed_rank_null_counts(list(range(1, 15)))
    cum = np.cumsum(cnt) / 2 ** 14
    assert cum[21] <= 0.025 < cum[22]
    lo, hi, C = hl_ci_exact(np.arange(1.0, 15.0), 0.95)
    assert C == 21
    # Holm
    adj = holm({"a": 0.01, "b": 0.04, "c": 0.03, "d": 0.5})
    assert abs(adj["a"] - 0.04) < 1e-12 and abs(adj["c"] - 0.09) < 1e-12 and abs(adj["b"] - 0.09) < 1e-12
    # Wilson
    lo, hi = wilson(0, 20)
    assert abs(lo) < 1e-12 and abs(hi - 0.1611) < 1e-3
    # verdict rows
    assert verdict_class(0.01, 0.7, 0.6, 0.9, 0.62, 0.85) == "P_better"
    assert verdict_class(0.5, 1.0, 0.85, 1.2, 0.9, 1.1) == "equivalent"
    assert verdict_class(0.01, 0.9, 0.85, 0.95, 0.86, 0.94) == "differ_lt25"
    assert verdict_class(0.3, 0.7, 0.4, 1.3, 0.45, 1.2) == "inconclusive"
    # failure rule: one failed task -> failed material
    rows = []
    for c in ("P", "F-hard", "V-pen", "A-hard", "F-none", "C1"):
        for m in ("m1", "m2", "m3"):
            for t in TASKS:
                E = 0.05 if c == "P" else 0.1
                err = None
                if c == "P" and m == "m1" and t == "E-low":
                    E, err = float("inf"), "boom"
                rows.append({"cell": c, "material": m, "task": t, "E": E, "error": err,
                             "violations": {"nonmonotone": 0, "negative_q": 0, "undefined_qst": 0,
                                            "tol_drop_isotherms_in": 0, "tol_negative_points_in": 0}})
    r = score(rows, do_boot=False)
    d1 = r["H1"]["H1b"]["d_by_material"]["m1"]
    assert abs(d1 - 1.0) < 1e-12, d1   # worst finite e = log10 0.1 = -1, +1 -> 0; d = 0 - (-1)
    # 5315654: Holm over four (H1b-H1e), H1a descriptive with prefix and unadjusted p
    assert set(r["H1"]) == {"H1b", "H1c", "H1d", "H1e"}
    a = r["H1a_descriptive"]["all"]
    assert a["p_holm"] == a["p"] and a["words"].startswith("Descriptive (unadjusted, not a test): ")
    assert r["H1a_descriptive"]["min3_training_T"].startswith("not computed")  # no train_T here
    # Holm over four: with four equal raw p, every adjusted p is 4 x p (capped at 1)
    adj4 = holm({"H1b": 0.01, "H1c": 0.01, "H1d": 0.01, "H1e": 0.01})
    assert all(abs(v - 0.04) < 1e-12 for v in adj4.values())
    # one 'inconclusive' wording (section 8 / 7.3 at 5315654)
    assert CLASS_WORDS["inconclusive"].format(X="X") == (
        "Inconclusive at this sample size: the data cannot tell P and X apart.")
    # H1b non-inferiority: upper exact 95 % bound of R < 1.25
    hb = r["H1b_prediction"]
    assert hb["met"] == (hb["upper95"] < 1.25)
    # summary sentences: H1b equivalent -> the admissibility sentence only (no H1a sentence left)
    s = summary_sentences({"H1b": "equivalent", "H1c": "inconclusive", "H1d": "inconclusive",
                           "H1e": "inconclusive"})
    assert s == ["The hard constraints give admissibility at no accuracy cost larger than 25 %."]
    # 1296 combinations: never the 'no sentence' line together with another one
    import itertools
    cls6 = list(CLASS_WORDS)
    for combo in itertools.product(cls6, repeat=4):
        ss = summary_sentences(dict(zip(("H1b", "H1c", "H1d", "H1e"), combo)))
        assert len(ss) >= 1 and (len(ss) == 1 or not ss[-1].startswith("No program-level"))
    # H3 labels (TG15) and two-decimal bound (section 8)
    assert h3_class(0, 26)[0] == "none" and h3_class(26, 26)[0] == "often"
    assert h3_class(3, 26)[0] == "some" and h3_class(2, 10)[0] == "some" and h3_class(1, 60)[0] == "rare"
    assert h3_class(1, 100)[0] == "rare"
    assert h3_words("P", "none", 0, 26, wilson(0, 26)[1]).endswith("upper 95 % bound 0.13).")
    # H3 prediction (7.1): V-pen 'some'/'often' and P 'none'
    assert r["H3_prediction"]["met"] is False  # no violations at all in the toy rows
    rv = [dict(x) for x in rows]
    for x in rv:
        if x["cell"] == "V-pen" and x["material"] == "m1":
            x["violations"] = dict(x["violations"], tol_drop_isotherms_in=1)
    pv = score(rv, do_boot=False)
    assert pv["H3"]["V-pen"]["class"] == "some" and pv["H3_prediction"]["met"] is True
    # material set must equal the frozen confirmatory set when given (7.2)
    must_stop_early = False
    try:
        score(rows, do_boot=False, expect_materials=["m1", "m2", "m4"])
    except StopAnalysis:
        must_stop_early = True
    assert must_stop_early
    assert score(rows, do_boot=False, expect_materials=["m3", "m2", "m1"])["n_materials"] == 3
    # descriptive comparison on the materials where X was fitted (6.4), prefixed
    rd = rows + [dict(x, cell="V-none") for x in rows if x["cell"] == "V-pen" and x["material"] != "m3"]
    dd = score(rd, do_boot=False)["descriptive"]["D-Vnone"]
    assert dd["n_materials"] == 2 and dd["words"].startswith("Descriptive (unadjusted")

    # H3 denominator (TG1): P has 6 fits, 1 failed -> n = 5, failed reported apart
    assert r["H3"]["P"]["fits"] == 5 and r["H3"]["P"]["failed_fits_excluded"] == 1, r["H3"]["P"]
    assert r["H3"]["F-hard"]["fits"] == 6 and r["H3"]["F-hard"]["failed_fits_excluded"] == 0

    def must_stop(fn, what):
        try:
            fn()
        except StopAnalysis:
            return
        raise AssertionError(what + " did not stop")

    # missing record stops (TG9)
    must_stop(lambda: score(rows[:-1], do_boot=False), "missing record")
    # duplicated record stops (TG6), identical or conflicting, in the run file and the H2 file
    must_stop(lambda: score(rows + [dict(rows[3])], do_boot=False), "identical duplicate")
    conflict = dict(rows[3]); conflict["E"] = 0.07
    must_stop(lambda: score(rows + [conflict], do_boot=False), "conflicting duplicate")
    # non-positive error value stops (TG5), also when the error field is set, also in a non-H1 task
    for bad in ({"E": 0.0}, {"E": -0.1}, {"E": -0.1, "error": "boom"}):
        rr = [dict(x) for x in rows]; rr[7].update(bad)
        must_stop(lambda: score(rr, do_boot=False), f"E <= 0 {bad}")
    extra = dict(rows[0]); extra.update({"task": "I-mid", "E": 0.0})
    must_stop(lambda: score(rows + [extra], do_boot=False), "E = 0 in I-mid")
    # --expect-n (TG12)
    must_stop(lambda: score(rows, do_boot=False, expect_n=13), "n mismatch with --expect-n")
    assert score(rows, do_boot=False, expect_n=3)["n_matches_prereg"] is False
    # H2: all five families needed (TG13); a duplicated H2 record stops (TG6)
    h2 = [{"family": f, "cell": c, "material": m, "task": t, "qst_rmse_kJ": 2.0 if c == "P" else 3.0,
           "error": None} for f in H2_FAMILIES for c in ("P",) + H2_COMPARATORS
          for m in ("m1", "m2", "m3") for t in TASKS]
    r2 = score(rows, h2, do_boot=False)
    assert r2["H2_n_tests"] == 15 and r2["H2_materials_equal_run_materials"] is True
    must_stop(lambda: score(rows, [x for x in h2 if x["family"] != "TC"], do_boot=False), "missing family")
    must_stop(lambda: score(rows, h2 + [dict(h2[0])], do_boot=False), "H2 duplicate")
    # n = 13 (confirmatory n at fc80d72): exact two-sided 5 % and 10 % critical values 17 and 21
    assert hl_ci_exact(np.arange(1.0, 14.0), 0.95)[2] == 17
    assert hl_ci_exact(np.arange(1.0, 14.0), 0.90)[2] == 21
    print("selftest passed")


def main(argv):
    if "--selftest" in argv:
        selftest()
        return
    out = "cs_verdicts.json"
    do_boot = "--no-bootstrap" not in argv
    args = [a for a in argv if a != "--no-bootstrap"]
    expect_n, expect_mats = None, None
    if "--dataset-summary" in args:
        i = args.index("--dataset-summary")
        expect_mats = confirmatory_materials(args[i + 1])
        del args[i:i + 2]
    if "--expect-n" in args:
        i = args.index("--expect-n")
        expect_n = int(args[i + 1])
        del args[i:i + 2]
    if "--out" in args:
        i = args.index("--out")
        out = args[i + 1]
        del args[i:i + 2]
    h2 = []
    if "--h2" in args:
        i = args.index("--h2")
        h2 = args[i + 1:]
        args = args[:i]
    res = score(read_jsonl(args), read_jsonl(h2) if h2 else None, do_boot, expect_n, expect_mats)
    Path(out).write_text(json.dumps(res, indent=2, default=float), encoding="utf-8")
    for h, v in res.get("H1", {}).items():
        print(f"{h} P vs {v['X']:7s} R={v['R']:.3f} 95% [{v['R_ci95_exact'][0]:.3f}, "
              f"{v['R_ci95_exact'][1]:.3f}] p_holm={v['p_holm']:.4f}  {v['words']}")
    for s in res.get("summary_sentences", []):
        print("SUMMARY:", s)
    if "halted" in res:
        print("HALTED:", res["halted"])


if __name__ == "__main__":
    main(sys.argv[1:])
