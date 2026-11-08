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

    constrained=False (vanthoff and kirchhoff only) gives the matched unconstrained twin for
    the factorial design: the same functional form and, for the same seed, the same initial
    function, but capacities c_k may be negative and every exponent g_k (Henry terms
    included) is a free real number. P1 and P2 are then no longer guaranteed.
    """

    def __init__(self, n_henry=2, n_coop=6, hidden=16, s_center=6.0, s_scale=2.0,
                 q_scale=20.0, theta_span=6.0, t_mode="vanthoff", Q_init_kJ=50.0,
                 constrained=True):
        super().__init__()
        if t_mode not in ("vanthoff", "kirchhoff", "nn"):
            raise ValueError(t_mode)
        if not constrained and t_mode == "nn":
            raise ValueError("the unconstrained twin exists for vanthoff and kirchhoff only")
        self.constrained = constrained
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
            if not constrained:  # same initial function, constraints removed
                with torch.no_grad():
                    c_init = _num.softplus(self.c_raw + 1.0)
                    g_init = torch.cat([torch.ones(n_henry), self.g_min + _num.softplus(self.g_raw)])
                del self.c_raw, self.g_raw
                self.c_lin = nn.Parameter(c_init)
                self.g_free = nn.Parameter(g_init)

    def _terms(self, T):
        k = self.n_henry + self.n_coop
        if self.t_mode == "nn":
            out = self.net(tau_hat(T).unsqueeze(-1))
            c = self.q_scale / k * _num.softplus(out[..., :k] + 1.0)
            raw = out[..., k:] + self.theta_offset
            theta = self.s_center + self.s_scale * self.theta_span * torch.tanh(raw / self.theta_span)
        else:
            Tc = T.unsqueeze(-1)
            c0 = self.q_scale / k * (_num.softplus(self.c_raw + 1.0) if self.constrained
                                     else self.c_lin)
            c = c0 * torch.exp(-1e-3 * self.alpha_milli * (Tc - T_REF))
            theta = (self.s_center + self.s_scale * (self.theta_raw + self.theta_offset)
                     - self.Q_kJ * 1e3 / R * (1.0 / Tc - 1.0 / T_REF))
            if self.t_mode == "kirchhoff":
                theta = theta - self.dc / R * (torch.log(Tc / T_REF) + T_REF / Tc - 1.0)
        if self.constrained:
            g = torch.cat([torch.ones(self.n_henry), self.g_min + _num.softplus(self.g_raw)])
        else:
            g = self.g_free
        return c, theta, g

    def forward(self, s, T):
        c, theta, g = self._terms(T)
        return (c * _num.sigmoid(g * (s.unsqueeze(-1) - theta))).sum(-1)

    def potential(self, s, T):
        if not self.constrained:
            raise ValueError("the unconstrained twin has no guaranteed potential")
        c, theta, g = self._terms(T)
        return (c / g * _num.softplus(g * (s.unsqueeze(-1) - theta))).sum(-1)

    def henry_constant(self, T):
        if not self.constrained:
            raise ValueError("the unconstrained twin has no guaranteed Henry limit")
        c, theta, _ = self._terms(T)
        h = self.n_henry
        return (c[..., :h] * torch.exp(-theta[..., :h])).sum(-1)


class MLPIsotherm(nn.Module):
    """Unconstrained network q(s, T); the same inputs and scaling as P.

    inputs="abs" (F-none, F-pen): (s, 1/T), the inputs of P.
    inputs="rel" (F-rel, descriptive): (ln(p/p_sat(T)), 1/T). Water isotherms of MOFs are
    nearly invariant in p/p_sat, so this is the natural generic competitor (review B4).
    s_center and s_scale then refer to ln(p/p_sat).
    """

    def __init__(self, hidden=32, depth=2, s_center=6.0, s_scale=2.0, q_scale=20.0, inputs="abs"):
        super().__init__()
        if inputs not in ("abs", "rel"):
            raise ValueError(inputs)
        self.s_center, self.s_scale, self.q_scale, self.inputs = s_center, s_scale, q_scale, inputs
        layers, d = [], 2
        for _ in range(depth):
            layers += [nn.Linear(d, hidden), nn.Tanh()]
            d = hidden
        layers.append(nn.Linear(d, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, s, T):
        x0 = s - water.ln_p_sat(T) if self.inputs == "rel" else s
        x = torch.stack([(x0 - self.s_center) / self.s_scale, tau_hat(T)], -1)
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
    """At low pressure q must be linear in p: d ln q / d ln p = 1, so dq/ds = q > 0.

    Scale-free form (revised before the freeze, review C2): the relative difference
    (dq/ds - q) / (|dq/ds| + |q|), which lies in [-1, 1] and is zero only for a linear isotherm,
    plus the same relative measure of negative uptake. The earlier form divided by q_scale and
    was nearly zero for any function at 0.01 Pa, where q itself is tiny. The guard against
    0/0 is 1e-300, far below any representable uptake that matters, so that even a model whose
    uptake at 0.01 Pa is 1e-20 mol/kg is still tested (q_scale is kept for the call signature).
    """
    q, q_s = _q_and_qs(f, s_low, T_low)
    den = q_s.abs() + q.abs() + 1e-300
    return ((q_s - q) / den).pow(2).mean() + (torch.relu(-q) / den).pow(2).mean()


class MultiSiteSips(nn.Module):
    """C1: q = sum_i qm_i (b_i p)^g_i / (1 + (b_i p)^g_i), b_i = b0_i exp(Q_i / RT).

    With fix_first_g=True the first site is Langmuir (g = 1), which restores a Henry limit.
    """

    def __init__(self, n_sites=2, fix_first_g=False, q_scale=20.0, lnb_center=-5.0):
        super().__init__()
        self.fix_first_g = fix_first_g
        self.q_scale = q_scale
        self.qm_raw = nn.Parameter(torch.full((n_sites,), 0.0) + 0.3 * torch.randn(n_sites))
        # ln b at T_REF, 1/Pa: spread around the data's ln p centre
        self.lnb_ref = nn.Parameter(lnb_center + torch.linspace(2.0, -2.0, n_sites) + 0.3 * torch.randn(n_sites))
        self.Q_kJ = nn.Parameter(torch.full((n_sites,), 50.0))
        self.g_raw = nn.Parameter(torch.zeros(n_sites))

    def forward(self, s, T):
        qm = self.q_scale / 1.4 * _num.softplus(self.qm_raw)  # sum about q_scale at init
        lnb = self.lnb_ref + self.Q_kJ * 1e3 / R * (1.0 / T.unsqueeze(-1) - 1.0 / T_REF)
        g = 0.2 + _num.softplus(self.g_raw)
        if self.fix_first_g:
            g = torch.cat([torch.ones(1), g[1:]])
        return (qm * _num.sigmoid(g * (s.unsqueeze(-1) + lnb))).sum(-1)


class CharacteristicCurve(nn.Module):
    """C2: q = W(A), A = RT ln(p_sat(T)/p), W = sum_k c_k sigmoid(-g_k (A - A_k) / A_scale).

    Temperature-invariant in A by construction; W decreasing in A, so q increases with p.
    It has no Henry limit in general (a known property of characteristic-curve models).
    constrained=False: the matched twin with signed c_k and free real g_k, same initial function.
    """

    def __init__(self, n_terms=4, A_scale=2e3, constrained=True, q_scale=20.0):
        super().__init__()
        self.A_scale, self.constrained = A_scale, constrained
        self.c_unit = q_scale / n_terms / 0.7  # each term about q_scale / n_terms at init
        self.c_raw = nn.Parameter(0.3 * torch.randn(n_terms))
        self.A_k = nn.Parameter(torch.linspace(1.0, 8.0, n_terms) + 0.3 * torch.randn(n_terms))
        self.g_raw = nn.Parameter(torch.ones(n_terms))
        if not constrained:
            with torch.no_grad():
                c_init, g_init = self.c_unit * _num.softplus(self.c_raw), _num.softplus(self.g_raw)
            del self.c_raw, self.g_raw
            self.c_lin = nn.Parameter(c_init)
            self.g_free = nn.Parameter(g_init)

    def forward(self, s, T):
        A = R * T * (water.ln_p_sat(T) - s)
        if self.constrained:
            c, g = self.c_unit * _num.softplus(self.c_raw), _num.softplus(self.g_raw)
        else:
            c, g = self.c_lin, self.g_free
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
