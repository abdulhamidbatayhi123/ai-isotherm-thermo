"""The statistics and verdict words of scripts/analyse.py, on hand-computable cases and by
brute force over every outcome combination (PAPER_WORKFLOW_LESSONS section 3)."""
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import analyse  # noqa: E402


def test_hodges_lehmann_is_the_median_of_walsh_averages():
    # Walsh averages (i <= j): 1, 1.5, 5, 2, 5.5, 9 -> sorted 1, 1.5, 2, 5, 5.5, 9 -> median 3.5
    assert analyse.hodges_lehmann([1.0, 2.0, 9.0]) == pytest.approx(3.5)
    assert analyse.hodges_lehmann([-1.0, 1.0]) == pytest.approx(0.0)


def test_holm_adjusts_in_order_and_stays_monotone():
    adj = analyse.holm({"a": 0.01, "b": 0.04, "c": 0.03, "d": 0.5})
    assert adj["a"] == pytest.approx(0.04)
    assert adj["c"] == pytest.approx(0.09)
    assert adj["b"] == pytest.approx(0.09)  # 2 x 0.04 = 0.08, raised to the running max
    assert adj["d"] == pytest.approx(0.5)


# ------------------------------------------------------------- review A1: failures
def _df(rows):
    df = pd.DataFrame(rows, columns=["cell", "material", "task", "E"])
    v = df.E.astype(float)
    ok = np.isfinite(v) & (v > 0)
    df["log10E"] = np.where(ok, np.log10(v.where(ok, 1.0)), np.nan)
    return df


def test_one_failed_task_makes_the_material_a_failure_not_the_mean_of_the_other():
    df = _df([("P", "m1", "E-high", 0.01), ("P", "m1", "E-low", float("inf")),
              ("P", "m2", "E-high", 0.01), ("P", "m2", "E-low", 0.1)])
    e = analyse.e_by_material(df, "P")
    assert math.isnan(e["m1"])
    assert e["m2"] == pytest.approx(-1.5)


def test_a_missing_task_record_stops_the_analysis():
    df = _df([("P", "m1", "E-high", 0.01)])
    with pytest.raises(ValueError, match="incomplete"):
        analyse.e_by_material(df, "P")


def test_failures_are_ranked_worst_per_comparison():
    eP = pd.Series({"a": -2.0, "b": float("nan"), "c": -1.0})
    eX = pd.Series({"a": -1.5, "b": -1.2, "c": float("nan")})
    d, mats, fails = analyse.paired_d(eP, eX)
    # worst finite value is -1.0, so failures become 0.0
    assert mats == ["a", "b", "c"]
    assert d == pytest.approx([-0.5, 1.2, -1.0])
    assert fails == {"P": 1, "X": 1}


# ------------------------------------------------------------- exact Wilcoxon (review D2)
@pytest.mark.parametrize("seed", range(6))
def test_exact_wilcoxon_matches_scipy_exact_without_ties(seed):
    d = np.random.default_rng(seed).normal(0.1, 1.0, 12)
    ref = stats.wilcoxon(d, alternative="two-sided", method="exact").pvalue
    assert analyse.wilcoxon_exact(d) == pytest.approx(ref, rel=1e-9)


def test_exact_wilcoxon_by_enumeration_with_ties_and_zeros():
    d = np.array([0.3, -0.3, 0.5, 0.5, 0.0, 1.2, -0.1, 0.5])
    nz = d[d != 0]
    r = stats.rankdata(np.abs(nz))
    obs = r[nz > 0].sum()
    mu = r.sum() / 2
    tot = [sum(r[i] for i in range(len(nz)) if (bits >> i) & 1) for bits in range(2 ** len(nz))]
    p = np.mean([abs(t - mu) >= abs(obs - mu) - 1e-9 for t in tot])
    assert analyse.wilcoxon_exact(d) == pytest.approx(p, rel=1e-12)


def test_exact_wilcoxon_all_zero_is_one():
    assert analyse.wilcoxon_exact([0.0, 0.0, 0.0]) == 1.0


def test_exact_hl_interval_known_case_and_contains_the_estimate():
    # n = 14: P(T+ <= 21) = 0.0247 <= 0.025 < P(T+ <= 22), so C = 21 (standard tables)
    d = np.arange(1, 15, dtype=float)
    lo, hi = analyse.hl_ci_exact(d, 0.95)
    walsh = np.sort(((d[:, None] + d[None, :]) / 2)[np.triu_indices(14)])
    assert lo == walsh[21] and hi == walsh[105 - 22]
    rng = np.random.default_rng(1)
    for _ in range(200):
        x = rng.standard_t(3, 14) * 0.2
        h = analyse.hodges_lehmann(x)
        l95, h95 = analyse.hl_ci_exact(x, 0.95)
        l90, h90 = analyse.hl_ci_exact(x, 0.90)
        assert l95 <= l90 <= h <= h90 <= h95  # review D4: R inside its own intervals, nested


def test_exact_hl_interval_is_infinite_when_n_is_too_small():
    assert analyse.hl_ci_exact([0.1, 0.2], 0.95) == (-math.inf, math.inf)


def test_exact_hl_interval_coverage_by_simulation():
    rng = np.random.default_rng(7)
    hits = sum(lo <= 0.3 <= hi for lo, hi in
               (analyse.hl_ci_exact(rng.normal(0.3, 1, 14), 0.95) for _ in range(2000)))
    assert hits / 2000 >= 0.94


# ------------------------------------------------------------- verdict words
@pytest.mark.parametrize("args, cls, words", [
    ((0.01, 0.7, 0.6, 0.9, 0.62, 0.85), "P_better", "P extrapolates better than X."),
    ((0.01, 1.4, 1.1, 1.8, 1.15, 1.7), "X_better", "X extrapolates better than P."),
    ((0.5, 1.0, 0.85, 1.2, 0.9, 1.1), "equivalent", "P and X are equivalent within 25 %."),
    ((0.01, 0.9, 0.85, 0.95, 0.86, 0.94), "differ_small", "P and X differ, by less than 25 %."),
    ((0.01, 0.9, 0.75, 0.95, 0.78, 0.94), "differ_uncertain", "P and X differ; the size of the difference is uncertain."),
    ((0.3, 0.7, 0.4, 1.3, 0.45, 1.2), "inconclusive", "Inconclusive at this sample size: the data cannot tell P and X apart."),
])
def test_verdict_words(args, cls, words):
    assert analyse.verdict(*args, "X") == (cls, words)


def test_verdict_table_is_exhaustive_consistent_and_never_contradicts_the_numbers():
    """Every combination gets exactly one class, and each class's own conditions hold."""
    grid = [0.5, 0.7, 0.79, 0.8, 0.81, 0.9, 1.0, 1.1, 1.24, 1.25, 1.26, 1.5, 2.0]
    n = 0
    for p in (0.001, 0.049, 0.05, 0.5):
        for lo95, lo90, R, hi90, hi95 in itertools.combinations_with_replacement(grid, 5):
            cls, w = analyse.verdict(p, R, lo95, hi95, lo90, hi90, "X")
            n += 1
            within = 0.8 <= lo90 and hi90 <= 1.25
            assert cls in analyse.VERDICT_CLASSES
            if cls == "P_better":
                assert p < 0.05 and R <= 0.8 and hi95 < 1
            elif cls == "X_better":
                assert p < 0.05 and R >= 1.25 and lo95 > 1
            elif cls == "differ_small":
                assert p < 0.05 and within
            elif cls == "equivalent":
                assert p >= 0.05 and within
            elif cls == "differ_uncertain":
                assert p < 0.05 and not within
            else:
                assert p >= 0.05 and not within
    assert n > 10000


def test_summary_sentences_never_contradict_and_always_say_something():
    """All 6^4 combinations of the four confirmatory H1 classes."""
    contradictory = [("no accuracy cost", "hard constraints cost"),
                     ("better than the characteristic curve, the", "characteristic curve extrapolates better"),
                     ("better than the characteristic curve, the", "dual-site Sips model with")]
    n = 0
    for combo in itertools.product(analyse.VERDICT_CLASSES, repeat=4):
        cls = dict(zip(("H1b", "H1c", "H1d", "H1e"), combo))
        s = analyse.summary_sentences(cls)
        n += 1
        assert len(s) >= 1 and len(set(s)) == len(s)
        joined = " | ".join(s)
        for a, b in contradictory:
            assert not (a in joined and b in joined), (cls, s)
        if s[0].startswith("No program-level"):
            assert len(s) == 1
        # each sentence only when its condition holds
        if "hard constraints cost" in joined:
            assert cls["H1b"] == "X_better"
        if "no accuracy cost" in joined:
            assert cls["H1b"] in ("P_better", "equivalent", "differ_small")
    assert n == 6**4


# ------------------------------------------------------------- H3 words (review C1)
def test_h3_words_are_exhaustive_and_consistent():
    for n in range(1, 61):
        for k in range(0, n + 1):
            cls, w = analyse.h3_words(k, n, "X")
            lo, hi = analyse.wilson(k, n)
            assert cls in ("often", "none", "rare", "some")
            if cls == "often":
                assert lo >= 0.20
            elif cls == "none":
                assert k == 0 and lo < 0.20
            elif cls == "rare":
                assert k > 0 and hi < 0.20
            else:
                assert k > 0 and lo < 0.20 <= hi


def test_h3_words_one_violation_is_not_called_often():
    assert analyse.h3_words(1, 28, "V-pen")[0] in ("some", "rare")


def test_wilson_interval_known_values():
    lo, hi = analyse.wilson(0, 20)
    assert lo == 0.0 and hi == pytest.approx(0.1611, abs=1e-3)
    lo, hi = analyse.wilson(10, 20)
    assert lo == pytest.approx(0.2993, abs=1e-3) and hi == pytest.approx(0.7007, abs=1e-3)


def test_sesoi_is_a_quarter_change():
    assert 10**analyse.SESOI == pytest.approx(1.25)
    assert math.isclose(analyse.SESOI, 0.0969, abs_tol=1e-4)


# ------------------------------------------------------------- end to end on a toy file
def test_main_runs_on_a_toy_run_file(tmp_path, monkeypatch):
    rng = np.random.default_rng(0)
    rows = []
    for i in range(6):
        for cell in ("P",) + tuple(analyse.H1.values()) + ("V-none", "F-hard"):
            for task in ("E-high", "E-low", "I-mid"):
                E = float(10 ** rng.normal(-1.5, 0.3)) if not (cell == "F-none" and i == 0) else float("inf")
                viol = {"points": 10, "nonmonotone": 0, "negative_q": 0, "undefined_qst": 0,
                        "qst_out_of_range": 0, "tol_drop_isotherms_in": int(cell == "V-none"),
                        "tol_negative_points_in": 0, "tol_drop_isotherms_out": 0,
                        "tol_negative_points_out": 0}
                rows.append({"cell": cell, "material": f"m{i}", "task": task, "E": E, "T_out": 300.0,
                             "train_T": [280.0, 290.0], "train_loss": 1e-4, "violations": viol})
    f = tmp_path / "toy_runs.jsonl"
    f.write_text("".join(json.dumps(r) + "\n" for r in rows))
    monkeypatch.setattr(analyse, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["analyse.py", str(f)])
    out = analyse.main()
    assert set(out["H1"]) == {"H1b", "H1c", "H1d", "H1e"}
    assert "H1a" in out["descriptive"]
    assert out["H1"]["H1d"]["failures"]["X"] == 1
    assert out["H3"]["cells"]["V-none"]["class"] == "often"
    assert out["H3"]["cells"]["P"]["class"] == "none"


def test_load_reads_shards_and_refuses_duplicates(tmp_path):
    rec = lambda m, t: json.dumps({"cell": "P", "material": m, "task": t, "E": 0.01}) + "\n"  # noqa: E731
    (tmp_path / "runs.shard0.jsonl").write_text(rec("a", "E-high") + rec("a", "E-low"))
    (tmp_path / "runs.shard1.jsonl").write_text(rec("b", "E-high") + rec("b", "E-low"))
    df = analyse.load(tmp_path / "runs.jsonl")
    assert len(df) == 4 and set(df.material) == {"a", "b"}
    (tmp_path / "runs.shard2.jsonl").write_text(rec("a", "E-high"))
    with pytest.raises(ValueError, match="duplicate"):
        analyse.load(tmp_path / "runs.jsonl")


def test_h3_leaves_failed_fits_out_of_n_and_reports_them():
    v_ok = {"points": 1, "nonmonotone": 0, "negative_q": 0, "undefined_qst": 0, "qst_out_of_range": 0,
            "tol_drop_isotherms_in": 1, "tol_negative_points_in": 0, "tol_drop_isotherms_out": 0,
            "tol_negative_points_out": 0}
    df = pd.DataFrame([{"cell": "V-none", "material": "a", "task": "E-high", "E": 0.1, "violations": v_ok},
                       {"cell": "V-none", "material": "a", "task": "E-low", "E": float("inf"), "violations": None}])
    r = analyse.analyse_h3(df)["cells"]["V-none"]
    assert r["fits"] == 1 and r["failed_fits"] == 1 and r["violating_in_domain"] == 1


def test_non_positive_error_stops_the_analysis(tmp_path):
    f = tmp_path / "r.jsonl"
    f.write_text(json.dumps({"cell": "P", "material": "a", "task": "E-high", "E": 0.0}) + "\n")
    with pytest.raises(ValueError, match="non-positive"):
        analyse.load(f)
