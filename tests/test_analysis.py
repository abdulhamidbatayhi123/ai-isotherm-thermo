"""The statistics and verdict words of scripts/analyse.py, on hand-computable cases."""
import itertools
import math
import sys
from pathlib import Path

import numpy as np
import pytest

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


@pytest.mark.parametrize("args, words", [
    ((0.01, 0.7, 0.6, 0.9, 0.62, 0.85), "P extrapolates better than X."),
    ((0.01, 1.4, 1.1, 1.8, 1.15, 1.7), "X extrapolates better than P."),
    ((0.5, 1.0, 0.85, 1.2, 0.9, 1.1), "P and X are equivalent within 25 %."),
    ((0.01, 0.9, 0.85, 0.95, 0.86, 0.94), "P and X differ, by less than 25 %."),
    ((0.01, 0.9, 0.75, 0.95, 0.78, 0.94), "P and X differ; the size of the difference is uncertain."),
    ((0.3, 0.7, 0.4, 1.3, 0.45, 1.2), "Inconclusive: the data cannot tell P and X apart."),
])
def test_verdict_words(args, words):
    assert analyse.verdict(*args, "X") == words


def test_verdict_table_is_exhaustive_consistent_and_never_contradicts_the_numbers():
    """Brute force over outcome combinations (PAPER_WORKFLOW_LESSONS section 3): every
    combination gets exactly one sentence, and each sentence's own conditions hold."""
    grid = [0.5, 0.7, 0.79, 0.8, 0.81, 0.9, 1.0, 1.1, 1.24, 1.25, 1.26, 1.5, 2.0]
    n = 0
    for p in (0.001, 0.049, 0.05, 0.5):
        for lo95, lo90, R, hi90, hi95 in itertools.combinations_with_replacement(grid, 5):
            w = analyse.verdict(p, R, lo95, hi95, lo90, hi90, "X")
            n += 1
            if w == "P extrapolates better than X.":
                assert p < 0.05 and R <= 0.8 and hi95 < 1
            elif w == "X extrapolates better than P.":
                assert p < 0.05 and R >= 1.25 and lo95 > 1
            elif w.startswith("P and X differ, by less"):
                assert p < 0.05 and 0.8 <= lo90 and hi90 <= 1.25
            elif w.startswith("P and X are equivalent"):
                assert p >= 0.05 and 0.8 <= lo90 and hi90 <= 1.25
            elif w.startswith("P and X differ; the size"):
                assert p < 0.05 and not (0.8 <= lo90 and hi90 <= 1.25)
            else:
                assert w.startswith("Inconclusive") and p >= 0.05 and not (0.8 <= lo90 and hi90 <= 1.25)
    assert n > 10000


def test_wilson_interval_known_values():
    lo, hi = analyse.wilson(0, 20)
    assert lo == 0.0 and hi == pytest.approx(0.1611, abs=1e-3)
    lo, hi = analyse.wilson(10, 20)
    assert lo == pytest.approx(0.2993, abs=1e-3) and hi == pytest.approx(0.7007, abs=1e-3)


def test_sesoi_is_a_quarter_change():
    assert 10**analyse.SESOI == pytest.approx(1.25)
    assert math.isclose(analyse.SESOI, 0.0969, abs_tol=1e-4)
