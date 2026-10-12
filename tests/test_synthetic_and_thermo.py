"""Known-answer tests: analytic isotherms whose isosteric heat and Henry constant are exact."""
import math

import numpy as np
import pytest
import torch

from p3a import synthetic as syn
from p3a import thermo
from p3a.constants import R

T_GRID = torch.tensor([288.15, 298.15, 308.15, 318.15, 338.15])


def _grid(s_lo=3.0, s_hi=8.5, n=60):
    s = torch.linspace(s_lo, s_hi, n)
    S, T = torch.meshgrid(s, T_GRID, indexing="ij")
    return S.reshape(-1), T.reshape(-1)


def test_langmuir_vant_hoff_qst_is_exactly_Q():
    f = syn.langmuir(qm=20.0, b0=1e-9, Q=45e3)
    s, T = _grid()
    qst = thermo.isosteric_heat(f, s, T)
    assert torch.allclose(qst, torch.full_like(qst, 45e3), rtol=1e-10, atol=1e-6)


def test_sips_vant_hoff_qst_is_exactly_Q_for_any_exponent():
    for g in (1.0, 2.5, 6.0):
        f = syn.sips(qm=25.0, b0=2e-10, Q=52e3, g=g)
        s, T = _grid()
        qst = thermo.isosteric_heat(f, s, T)
        assert torch.allclose(qst, torch.full_like(qst, 52e3), rtol=1e-9, atol=1e-5)


def test_kirchhoff_sips_qst_is_Q0_minus_dc_times_T_minus_T0():
    f = syn.sips_kirchhoff(qm=20.0, b_ref=1e-3, Q0=50e3, dc=40.0, g=3.0, T0=298.15)
    s, T = _grid()
    qst = thermo.isosteric_heat(f, s, T)
    assert torch.allclose(qst, 50e3 - 40.0 * (T - 298.15), rtol=1e-9)


def test_dual_site_langmuir_qst_matches_closed_form():
    sites = [(5.0, 1e-9, 60e3), (18.0, 3e-8, 40e3)]
    f = syn.dual_site_langmuir(sites)
    s, T = _grid()
    qst = thermo.isosteric_heat(f, s, T)
    p = torch.exp(s)
    num = torch.zeros_like(s)
    den = torch.zeros_like(s)
    for qm, b0, Q in sites:
        th = (b0 * torch.exp(Q / (R * T)) * p) / (1 + b0 * torch.exp(Q / (R * T)) * p)
        w = qm * th * (1 - th)
        num += w * Q
        den += w
    assert torch.allclose(qst, num / den, rtol=1e-9)


def test_dubinin_astakhov_qst_is_A_plus_vaporisation_enthalpy():
    f = syn.dubinin_astakhov(W0=20.0, E=5e3, n=2.0)
    s, T = _grid(3.0, 7.3)  # below p_sat at 288 K, so A > 0
    qst = thermo.isosteric_heat(f, s, T)
    from p3a import water
    A = R * T * (torch.log(water.p_sat(T)) - s)
    L = water.clausius_clapeyron_enthalpy(T)
    assert torch.allclose(qst, A + L, rtol=1e-9)


def test_isosteric_heat_autodiff_matches_central_differences():
    f = syn.dual_site_langmuir([(5.0, 1e-9, 60e3), (18.0, 3e-8, 40e3)])
    s = torch.tensor([5.0, 6.5, 7.5])
    T = torch.tensor([298.15, 303.15, 330.0])
    qst = thermo.isosteric_heat(f, s, T)
    # independent check: at fixed q, ln p as a function of 1/T by root finding
    for i in range(3):
        q0 = f(s[i : i + 1], T[i : i + 1]).item()

        def lnp_at(Tv):
            lo, hi = -30.0, 30.0
            for _ in range(200):
                mid = 0.5 * (lo + hi)
                if f(torch.tensor([mid]), torch.tensor([Tv])).item() < q0:
                    lo = mid
                else:
                    hi = mid
            return 0.5 * (lo + hi)

        h = 1e-6
        tau = 1.0 / T[i].item()
        d = (lnp_at(1 / (tau + h)) - lnp_at(1 / (tau - h))) / (2 * h)
        assert qst[i].item() == pytest.approx(-R * d, rel=1e-5)


def test_henry_constant_of_langmuir():
    f = syn.langmuir(qm=20.0, b0=1e-9, Q=45e3)
    T = torch.tensor([298.15, 318.15])
    K = thermo.henry_constant(f, T)
    expected = 20.0 * 1e-9 * torch.exp(45e3 / (R * T))
    assert torch.allclose(K, expected, rtol=1e-8)


def test_violation_counter_finds_a_planted_non_monotone_isotherm():
    def bumpy(s, T):
        return 10 * torch.sigmoid(s - 6.0) - 0.5 * torch.exp(-((s - 7.0) ** 2) / 0.01)

    s, T = _grid()
    v = thermo.violations(bumpy, s_grid=torch.linspace(3.0, 8.5, 400), T_grid=T_GRID)
    assert v["nonmonotone_points"] > 0
    v_ok = thermo.violations(syn.langmuir(20.0, 1e-9, 45e3),
                             s_grid=torch.linspace(3.0, 8.5, 400), T_grid=T_GRID)
    assert v_ok["nonmonotone_points"] == 0
    assert v_ok["negative_uptake_points"] == 0
    assert v_ok["undefined_qst_points"] == 0
