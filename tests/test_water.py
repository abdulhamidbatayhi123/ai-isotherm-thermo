"""p_sat against the verification table of IAPWS SR1-86(1992), Table 1.

Source: https://iapws.org/technical-guidance/release/Supp-sat.download, read in full on
2026-10-12 (research/lit_3a_classical.md, C30).
"""
import pytest
import torch

from p3a import water
from p3a.constants import R


@pytest.mark.parametrize("T, p", [(273.16, 611.657), (373.1243, 101325.0)])
def test_p_sat_matches_iapws_verification_table(T, p):
    assert water.p_sat(torch.tensor([T])).item() == pytest.approx(p, rel=1e-6)


def test_vaporisation_enthalpy_matches_iapws_slope_at_triple_point():
    # Table 1 at 273.16 K: dp/dT = 44.436693 Pa/K, p = 611.657 Pa
    T = torch.tensor([273.16])
    expected = R * 273.16**2 * 44.436693 / 611.657
    assert water.clausius_clapeyron_enthalpy(T).item() == pytest.approx(expected, rel=1e-6)
