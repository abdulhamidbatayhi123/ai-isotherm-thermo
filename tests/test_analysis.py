"""The statistics and verdict words of scripts/analyse.py, on hand-computable cases."""
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
    ((0.01, 0.9, 0.85, 0.95, 0.86, 0.94), "P and X are equivalent within 25 %."),
    ((0.01, 0.9, 0.75, 0.95, 0.78, 0.94), "P and X differ, by less than 25 %."),
    ((0.3, 0.7, 0.4, 1.3, 0.45, 1.2), "Inconclusive: the data cannot tell P and X apart."),
])
def test_verdict_words(args, words):
    assert analyse.verdict(*args, "X") == words


def test_wilson_interval_known_values():
    lo, hi = analyse.wilson(0, 20)
    assert lo == 0.0 and hi == pytest.approx(0.1611, abs=1e-3)
    lo, hi = analyse.wilson(10, 20)
    assert lo == pytest.approx(0.2993, abs=1e-3) and hi == pytest.approx(0.7007, abs=1e-3)


def test_sesoi_is_a_quarter_change():
    assert 10**analyse.SESOI == pytest.approx(1.25)
    assert math.isclose(analyse.SESOI, 0.0969, abs_tol=1e-4)
