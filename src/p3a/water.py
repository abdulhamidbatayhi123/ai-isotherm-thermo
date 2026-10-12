"""Saturation pressure of water and the enthalpy that the Clausius-Clapeyron equation assigns to it.

p_sat uses the IAPWS saturation-pressure equation (Wagner and Pruss 1993, IAPWS
supplementary release on saturation properties, SR1-86(1992), eq. (1)). The constants and the check values in
tests/test_water.py come from the live release, read 2026-10-12 (research/lit_3a_classical.md, C30).
"""
import torch

from .constants import R

T_C = 647.096  # K
P_C = 22.064e6  # Pa
_A = (-7.85951783, 1.84408259, -11.7866497, 22.6807411, -15.9618719, 1.80122502)
_E = (1.0, 1.5, 3.0, 3.5, 4.0, 7.5)


def ln_p_sat(T):
    """Natural log of the saturation pressure in Pa, for 273.16 K <= T <= T_C."""
    th = 1.0 - T / T_C
    acc = torch.zeros_like(T)
    for a, e in zip(_A, _E):
        acc = acc + a * th**e
    return torch.log(torch.as_tensor(P_C)) + (T_C / T) * acc


def p_sat(T):
    return torch.exp(ln_p_sat(T))


def clausius_clapeyron_enthalpy(T):
    """L(T) = -R d ln p_sat / d(1/T) = R T^2 d ln p_sat / dT, in J/mol.

    This is the vaporisation enthalpy of an ideal vapour over an incompressible liquid of
    negligible volume, the same approximation used for the isosteric heat. It is not the
    exact vaporisation enthalpy.
    """
    Tg = T.detach().clone().requires_grad_(True)
    d = torch.autograd.grad(ln_p_sat(Tg).sum(), Tg)[0]
    return R * T**2 * d
