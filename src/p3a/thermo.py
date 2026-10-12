"""Thermodynamic quantities evaluated identically for every model.

A model is any callable f(s, T) -> q acting row by row, with s = ln(p / Pa), T in K and
q in mol/kg. Water vapour is an ideal gas and the adsorbed-phase volume is neglected.
"""
import torch

from .constants import R


def _derivatives(f, s, T):
    s = s.detach().clone().requires_grad_(True)
    T = T.detach().clone().requires_grad_(True)
    q = f(s, T)
    q_s, q_T = torch.autograd.grad(q.sum(), [s, T], allow_unused=True)
    zeros = torch.zeros_like(q)  # an input the model ignores has zero derivative
    return q.detach(), zeros if q_s is None else q_s, zeros if q_T is None else q_T


def isosteric_heat(f, s, T):
    """Qst = -R (d ln p / d(1/T)) at constant q = -R T^2 q_T / q_s, in J/mol.

    Returns nan where q_s <= 0, where the isosteric heat is undefined.
    """
    _, q_s, q_T = _derivatives(f, s, T)
    qst = -R * T**2 * q_T / q_s
    return torch.where(q_s > 0, qst, torch.full_like(qst, float("nan")))


def henry_constant(f, T, s_low=-60.0):
    """K(T) = lim q/p as p -> 0, evaluated at p = exp(s_low) Pa (mol kg^-1 Pa^-1)."""
    s = torch.full_like(T, s_low)
    return f(s, T) / torch.exp(s)


def violations(f, s_grid, T_grid):
    """Counts of physical violations on the product grid s_grid x T_grid."""
    S, TT = torch.meshgrid(s_grid, T_grid, indexing="ij")
    s, T = S.reshape(-1), TT.reshape(-1)
    q, q_s, q_T = _derivatives(f, s, T)
    qst = -R * T**2 * q_T / q_s
    return {
        "points": int(s.numel()),
        "nonmonotone_points": int((q_s < 0).sum()),
        "negative_uptake_points": int((q < 0).sum()),
        "undefined_qst_points": int((~(q_s > 0) | ~torch.isfinite(qst)).sum()),
    }


def invert_isotherm(f, q, T, lo=-80.0, hi=60.0, iters=200):
    """Equilibrium s = ln p at which f(s, T) = q, by bisection. f must be increasing in s."""
    lo = torch.full_like(q, lo)
    hi = torch.full_like(q, hi)
    with torch.no_grad():
        for _ in range(iters):
            mid = 0.5 * (lo + hi)
            below = f(mid, T) < q
            lo = torch.where(below, mid, lo)
            hi = torch.where(below, hi, mid)
    return 0.5 * (lo + hi)
