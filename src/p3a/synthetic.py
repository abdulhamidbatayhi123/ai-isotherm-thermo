"""Analytic isotherms with known isosteric heats and Henry constants, for tests.

Every function returns f(s, T) -> q, with s = ln(p / Pa), T in K and q in mol/kg.
"""
import math

import torch

from . import _num, water
from .constants import R

T_REF = 298.15


def b0_from(b_ref, Q, T_ref=T_REF):
    """Pre-exponential factor b0 such that b(T_ref) = b_ref for b = b0 exp(Q / RT)."""
    return b_ref / math.exp(Q / (R * T_ref))


def _lnb(b0, Q, T):
    return math.log(b0) + Q / (R * T)


def langmuir(qm, b0, Q):
    """q = qm b p / (1 + b p), b = b0 exp(Q/RT). Isosteric heat is exactly Q."""
    return sips(qm, b0, Q, 1.0)


def sips(qm, b0, Q, g):
    """q = qm (b p)^g / (1 + (b p)^g). q depends on b p only, so the heat is exactly Q."""

    def f(s, T):
        return qm * _num.sigmoid(g * (s + _lnb(b0, Q, T)))

    return f


def dual_site_langmuir(sites):
    """Sum of Langmuir sites; sites = [(qm, b0, Q), ...]."""
    return dual_site_sips([(qm, b0, Q, 1.0) for qm, b0, Q in sites])


def dual_site_sips(sites):
    """Sum of Sips sites; sites = [(qm, b0, Q, g), ...]."""
    parts = [sips(*site) for site in sites]

    def f(s, T):
        return sum(p(s, T) for p in parts)

    return f


def dubinin_astakhov(W0, E, n):
    """q = W0 exp(-(A/E)^n), A = RT ln(p_sat/p). Isosteric heat is A + L(T)."""

    def f(s, T):
        A = R * T * (water.ln_p_sat(T) - s)
        return W0 * torch.exp(-((A / E) ** n))

    return f


def sips_kirchhoff(qm, b_ref, Q0, dc, g, T0=T_REF):
    """Sips term whose heat varies with temperature as Q(T) = Q0 - dc (T - T0).

    ln b(T) = ln b_ref + (Q0/R)(1/T - 1/T0) + (dc/R)(ln(T/T0) + T0/T - 1), from
    d ln b / d(1/T) = Q(T)/R. The isosteric heat is exactly Q(T) at every loading.
    """

    def f(s, T):
        lnb = (math.log(b_ref) + Q0 / R * (1.0 / T - 1.0 / T0)
               + dc / R * (torch.log(T / T0) + T0 / T - 1.0))
        return qm * _num.sigmoid(g * (s + lnb))

    return f


def fowler_guggenheim(qm, K_ref, Q0, w, T_ref=T_REF):
    """Fowler-Guggenheim isotherm (mobile monolayer with lateral attraction w > 0):

        p = theta / ((1 - theta) K(T)) * exp(-w theta / RT),  K(T) = K_ref exp((Q0/R)(1/T - 1/T_ref)).

    Monotone (no phase transition) while w < 4RT. The isosteric heat is exactly
    Qst = Q0 + w theta. Neither the van't Hoff site mixture nor the characteristic curve
    contains this family, so it is a fair benchmark for the heat.
    The forward map solves for theta by bisection and then takes one Newton step with
    gradients, which gives exact first derivatives at the root (implicit function theorem).
    """

    def residual(theta, s, T):
        lnK = math.log(K_ref) + Q0 / R * (1.0 / T - 1.0 / T_ref)
        return torch.log(theta) - torch.log1p(-theta) - lnK - w * theta / (R * T) - s

    def f(s, T):
        if torch.any(w >= 4 * R * T):
            raise ValueError("w >= 4RT: the isotherm has a phase transition")
        with torch.no_grad():
            lo = torch.zeros_like(s)
            hi = torch.ones_like(s)
            for _ in range(200):
                mid = 0.5 * (lo + hi)
                below = residual(mid, s, T) < 0  # residual increases with theta
                lo = torch.where(below, mid, lo)
                hi = torch.where(below, hi, mid)
            th0 = 0.5 * (lo + hi)
        th0 = th0.clamp(1e-300, 1 - 1e-16)
        dF = 1.0 / th0 + 1.0 / (1.0 - th0) - w / (R * T)
        theta = th0 - residual(th0, s, T) / dF.detach()
        return qm * theta

    return f
