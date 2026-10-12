"""Isotherm models. Each is a module with forward(s, T) -> q, s = ln(p / Pa), T in K, q in mol/kg.

P    PotentialIsotherm   learned adsorbed-phase potential; P1, P2 and P3 by construction
U    MLPIsotherm         unconstrained network
Pen  MLPIsotherm + monotonicity_penalty + henry_penalty
C1   MultiSiteSips       classical multi-site Sips with van't Hoff affinities
C2   CharacteristicCurve Dubinin-Polanyi, q = W(A), A = RT ln(p_sat / p)
"""
import torch
from torch import nn

from . import _num, water
from .constants import R

T_REF = 300.0


def tau_hat(T):
    """Scaled inverse temperature, about 1 at 273 K and -2 at 373 K."""
    return (T_REF / T - 1.0) / 0.1


class PotentialIsotherm(nn.Module):
    """Reduced spreading pressure psi(s, T) = sum_k c_k(T)/g_k softplus(g_k (s - theta_k(T))).

    q* = d psi / d s = sum_k c_k(T) sigmoid(g_k (s - theta_k(T))).
    Henry terms have g_k = 1; cooperative terms have g_k = g_min + softplus(.) with g_min = 1.5,
    so that a cooperative term cannot imitate a Henry term at accessible pressures.
    By construction: psi convex in s (q* strictly increasing), q* > 0 and bounded, and
    q*/p -> K(T) = sum over Henry terms of c_k exp(-theta_k) > 0 as p -> 0.

    Temperature dependence (t_mode):
      "vanthoff"  theta_k(T) = theta_k0 - (Q_k/R)(1/T - 1/T_REF): each term has a constant heat Q_k.
      "kirchhoff" adds a constant heat-capacity term, Q_k(T) = Q_k - dc_k (T - T_REF):
                  theta_k(T) = theta_k0 - (Q_k/R)(1/T - 1/T_REF) - (dc_k/R)(ln(T/T_REF) + T_REF/T - 1).
      "nn"        c_k(T) and theta_k(T) from a free tanh network of 1/T; theta_k is kept within
                  s_center +- theta_span * s_scale. Fits well, extrapolates poorly in T.
    In "vanthoff" and "kirchhoff", c_k(T) = c_k0 exp(-alpha_k (T - T_REF)) (adsorbate expansion).
    The choice of t_mode does not affect P1, P2 or P3, which hold in every mode.
    """

    def __init__(self, n_henry=2, n_coop=6, hidden=16, s_center=6.0, s_scale=2.0,
                 q_scale=20.0, theta_span=6.0, t_mode="vanthoff", Q_init_kJ=50.0):
        super().__init__()
        if t_mode not in ("vanthoff", "kirchhoff", "nn"):
            raise ValueError(t_mode)
        self.n_henry, self.n_coop, self.t_mode = n_henry, n_coop, t_mode
        k = n_henry + n_coop
        self.s_center, self.s_scale, self.q_scale, self.theta_span = (
            s_center, s_scale, q_scale, theta_span)
        self.register_buffer("theta_offset", torch.linspace(-1.5, 1.5, k))
        self.g_min = 1.5
        self.g_raw = nn.Parameter(torch.full((n_coop,), 0.7))  # g = 1.5 + softplus(0.7), about 2.6
        if t_mode == "nn":
            self.net = nn.Sequential(nn.Linear(1, hidden), nn.Tanh(), nn.Linear(hidden, 2 * k))
        else:
            # seeded jitter, so that different seeds start from different points
            self.c_raw = nn.Parameter(0.3 * torch.randn(k))
            self.theta_raw = nn.Parameter(0.3 * torch.randn(k))
            self.Q_kJ = nn.Parameter(float(Q_init_kJ) + 5.0 * torch.randn(k))
            self.alpha_milli = nn.Parameter(torch.zeros(k))  # 1e-3 / K
            if t_mode == "kirchhoff":
                self.dc = nn.Parameter(torch.zeros(k))  # J mol^-1 K^-1

    def _terms(self, T):
        k = self.n_henry + self.n_coop
        if self.t_mode == "nn":
            out = self.net(tau_hat(T).unsqueeze(-1))
            c = self.q_scale / k * _num.softplus(out[..., :k] + 1.0)
            raw = out[..., k:] + self.theta_offset
            theta = self.s_center + self.s_scale * self.theta_span * torch.tanh(raw / self.theta_span)
        else:
            Tc = T.unsqueeze(-1)
            c0 = self.q_scale / k * _num.softplus(self.c_raw + 1.0)
            c = c0 * torch.exp(-1e-3 * self.alpha_milli * (Tc - T_REF))
            theta = (self.s_center + self.s_scale * (self.theta_raw + self.theta_offset)
                     - self.Q_kJ * 1e3 / R * (1.0 / Tc - 1.0 / T_REF))
            if self.t_mode == "kirchhoff":
                theta = theta - self.dc / R * (torch.log(Tc / T_REF) + T_REF / Tc - 1.0)
        g = torch.cat([torch.ones(self.n_henry), self.g_min + _num.softplus(self.g_raw)])
        return c, theta, g

    def forward(self, s, T):
        c, theta, g = self._terms(T)
        return (c * _num.sigmoid(g * (s.unsqueeze(-1) - theta))).sum(-1)

    def potential(self, s, T):
        c, theta, g = self._terms(T)
        return (c / g * _num.softplus(g * (s.unsqueeze(-1) - theta))).sum(-1)

    def henry_constant(self, T):
        c, theta, _ = self._terms(T)
        h = self.n_henry
        return (c[..., :h] * torch.exp(-theta[..., :h])).sum(-1)


class MLPIsotherm(nn.Module):
    """Unconstrained network q(s, T); the same inputs and scaling as P."""

    def __init__(self, hidden=32, depth=2, s_center=6.0, s_scale=2.0, q_scale=20.0):
        super().__init__()
        self.s_center, self.s_scale, self.q_scale = s_center, s_scale, q_scale
        layers, d = [], 2
        for _ in range(depth):
            layers += [nn.Linear(d, hidden), nn.Tanh()]
            d = hidden
        layers.append(nn.Linear(d, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, s, T):
        x = torch.stack([(s - self.s_center) / self.s_scale, tau_hat(T)], -1)
        return self.q_scale * self.net(x).squeeze(-1)


def _q_and_qs(f, s, T):
    s = s.detach().clone().requires_grad_(True)
    q = f(s, T)
    (q_s,) = torch.autograd.grad(q.sum(), s, create_graph=True)
    return q, q_s


def monotonicity_penalty(f, s_col, T_col):
    """mean(relu(-dq/ds)^2) on collocation points; differentiable in f's parameters."""
    _, q_s = _q_and_qs(f, s_col, T_col)
    return torch.relu(-q_s).pow(2).mean()


def henry_penalty(f, s_low, T_low, q_scale=20.0):
    """At low pressure q must be linear in p, i.e. d ln q / d ln p = 1, so dq/ds = q > 0."""
    q, q_s = _q_and_qs(f, s_low, T_low)
    return ((q_s - q) / q_scale).pow(2).mean() + (torch.relu(-q) / q_scale).pow(2).mean()


class MultiSiteSips(nn.Module):
    """C1: q = sum_i qm_i (b_i p)^g_i / (1 + (b_i p)^g_i), b_i = b0_i exp(Q_i / RT).

    With fix_first_g=True the first site is Langmuir (g = 1), which restores a Henry limit.
    """

    def __init__(self, n_sites=2, fix_first_g=False):
        super().__init__()
        self.fix_first_g = fix_first_g
        self.qm_raw = nn.Parameter(torch.full((n_sites,), 2.0))
        self.lnb_ref = nn.Parameter(torch.linspace(-3.0, -7.0, n_sites))  # ln b at T_REF, 1/Pa
        self.Q_kJ = nn.Parameter(torch.full((n_sites,), 50.0))
        self.g_raw = nn.Parameter(torch.zeros(n_sites))

    def forward(self, s, T):
        qm = 10.0 * _num.softplus(self.qm_raw)
        lnb = self.lnb_ref + self.Q_kJ * 1e3 / R * (1.0 / T.unsqueeze(-1) - 1.0 / T_REF)
        g = 0.2 + _num.softplus(self.g_raw)
        if self.fix_first_g:
            g = torch.cat([torch.ones(1), g[1:]])
        return (qm * _num.sigmoid(g * (s.unsqueeze(-1) + lnb))).sum(-1)


class CharacteristicCurve(nn.Module):
    """C2: q = W(A), A = RT ln(p_sat(T)/p), W = sum_k c_k sigmoid(-g_k (A - A_k) / A_scale).

    Temperature-invariant in A by construction; W decreasing in A, so q increases with p.
    It has no Henry limit in general (a known property of characteristic-curve models).
    """

    def __init__(self, n_terms=4, A_scale=2e3):
        super().__init__()
        self.A_scale = A_scale
        self.c_raw = nn.Parameter(torch.zeros(n_terms))
        self.A_k = nn.Parameter(torch.linspace(1.0, 8.0, n_terms))  # in units of A_scale
        self.g_raw = nn.Parameter(torch.ones(n_terms))

    def forward(self, s, T):
        A = R * T * (water.ln_p_sat(T) - s)
        c = 5.0 * _num.softplus(self.c_raw)
        g = _num.softplus(self.g_raw)
        z = -g * (A.unsqueeze(-1) / self.A_scale - self.A_k)
        return (c * _num.sigmoid(z)).sum(-1)


class LDFRate(nn.Module):
    """Linear-driving-force coefficient k(q, s, T) = softplus(network) >= 0, in 1/s.

    The rate dq/dt = k (q*(s, T) - q) has the sign of mu_gas - mu_ads(q) whenever q* is
    strictly increasing in s, so entropy production is never negative (P4).
    """

    def __init__(self, hidden=8):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(3, hidden), nn.Tanh(), nn.Linear(hidden, 1))

    def forward(self, q, s, T):
        x = torch.stack([q / 20.0, (s - 6.0) / 2.0, tau_hat(T)], -1)
        return _num.softplus(self.net(x).squeeze(-1))
