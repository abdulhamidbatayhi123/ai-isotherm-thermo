"""The Paper 3A comparison: models of the factorial, tasks, fitting with seeds, evaluation.

Everything a confirmatory run does is defined here and fixed by PREREG_P3A.md:
  cells     F/V/A x none/pen/hard (section 4), C1, and the secondary P-K
  tasks     E-high, E-low, I-mid (section 5.1)
  fitting   loss on q / q_ref, Adam then L-BFGS, 5 seeds, lowest training loss (5.2, 5.3)
  outcomes  E (6.1), violations on the dense grid G (6.2), isosteric heat (6.3)
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import torch

from . import fit as fitmod
from . import models, thermo, water

CELLS = ("F-none", "F-pen", "F-hard", "V-none", "V-pen", "P", "A-none", "A-pen", "A-hard", "C1", "P-K")


@dataclass
class Material:
    name: str
    T: np.ndarray       # K, per point
    s: np.ndarray       # ln(p / Pa), per point
    q: np.ndarray       # mol/kg, per point

    @property
    def temps(self):
        return np.unique(self.T)

    @property
    def q_ref(self):
        return float(self.q.max())


def tasks(m: Material):
    """{task: (training temperatures, held-out temperature)} (PREREG 5.1)."""
    Ts = sorted(m.temps)
    out = {"E-high": (Ts[:-1], Ts[-1]), "E-low": (Ts[1:], Ts[0])}
    if len(Ts) >= 3:
        mid = Ts[(len(Ts) - 1) // 2]
        out["I-mid"] = ([t for t in Ts if t != mid], mid)
    return out


@dataclass
class Config:
    """Hyperparameters of one cell (PREREG 5.4)."""
    n_henry: int = 2
    n_coop: int = 4
    n_terms: int = 4          # A models
    hidden: int = 16
    depth: int = 2
    lam: float = 1.0          # penalty weight
    adam_steps: int = 2000
    lbfgs_steps: int = 300


def build(cell: str, cfg: Config, s_center: float, s_scale: float, q_scale: float):
    """A fresh model of one factorial cell; torch's seed must be set by the caller."""
    common = dict(s_center=s_center, s_scale=s_scale, q_scale=q_scale)
    if cell in ("F-none", "F-pen"):
        return models.MLPIsotherm(hidden=cfg.hidden, depth=cfg.depth, **common)
    if cell == "F-hard":
        return models.PotentialIsotherm(cfg.n_henry, cfg.n_coop, hidden=cfg.hidden, t_mode="nn", **common)
    if cell in ("V-none", "V-pen"):
        return models.PotentialIsotherm(cfg.n_henry, cfg.n_coop, t_mode="vanthoff", constrained=False, **common)
    if cell == "P":
        return models.PotentialIsotherm(cfg.n_henry, cfg.n_coop, t_mode="vanthoff", **common)
    if cell == "P-K":
        return models.PotentialIsotherm(cfg.n_henry, cfg.n_coop, t_mode="kirchhoff", **common)
    if cell in ("A-none", "A-pen"):
        return models.CharacteristicCurve(cfg.n_terms, constrained=False, q_scale=q_scale)
    if cell == "A-hard":
        return models.CharacteristicCurve(cfg.n_terms, q_scale=q_scale)
    if cell == "C1":
        return models.MultiSiteSips(2, q_scale=q_scale, lnb_center=-s_center)
    raise ValueError(cell)


def collocation(T_lo, T_hi, n_s=60, n_T=9):
    """Unlabelled penalty points: s from ln(1 Pa) to ln(0.9 p_sat(T)); T from T_lo - 15 K to
    T_hi + 15 K, which includes the held-out temperature (PREREG section 4)."""
    Ts = torch.linspace(T_lo - 15.0, T_hi + 15.0, n_T)
    S, TT = [], []
    for T in Ts:
        s_hi = float(water.ln_p_sat(T.reshape(1)) + math.log(0.9))
        S.append(torch.linspace(0.0, s_hi, n_s))
        TT.append(torch.full((n_s,), float(T)))
    s_low = torch.full((n_T,), math.log(0.01))
    return torch.cat(S), torch.cat(TT), s_low, Ts.clone()


def penalty_fn(cell, T_lo, T_hi, q_scale):
    if not cell.endswith("-pen"):
        return None
    s_c, T_c, s_low, T_low = collocation(T_lo, T_hi)

    def pen(model):
        p = models.monotonicity_penalty(model, s_c, T_c) / q_scale**2
        if not cell.startswith("A"):  # the characteristic curve has no Henry limit
            p = p + models.henry_penalty(model, s_low, T_low, q_scale=q_scale)
        return p

    return pen


@dataclass
class FitResult:
    cell: str
    seed: int
    train_loss: float
    model: torch.nn.Module = field(repr=False)
    init_vector: np.ndarray = field(repr=False)


def fit_cell(cell, cfg, m: Material, train_T, seeds=(0, 1, 2, 3, 4)):
    """Fit one cell from several seeds; returns all results, best first (PREREG 5.3)."""
    sel = np.isin(m.T, train_T)
    s = torch.as_tensor(m.s[sel])
    T = torch.as_tensor(m.T[sel])
    q = torch.as_tensor(m.q[sel])
    q_ref = m.q_ref
    s_center, s_scale = float(s.mean()), float(max(s.std(), 0.5))
    pen = penalty_fn(cell, float(T.min()), float(T.max()), q_ref)
    out = []
    for seed in seeds:
        torch.manual_seed(seed)
        model = build(cell, cfg, s_center, s_scale, q_ref)
        init = torch.cat([p.detach().flatten() for p in model.parameters()]).numpy().copy()
        loss = fitmod.fit(model, s, T, q, adam_steps=cfg.adam_steps,
                          lbfgs_steps=cfg.lbfgs_steps, penalty=pen, penalty_weight=cfg.lam,
                          q_scale=q_ref)
        out.append(FitResult(cell, seed, loss, model, init))
    inits = np.stack([r.init_vector for r in out])
    if len(out) > 1 and np.allclose(inits, inits[0]):
        raise RuntimeError(f"{cell}: all seeds start from the same parameters (CORRECTIONS P3A-3)")
    return sorted(out, key=lambda r: r.train_loss if np.isfinite(r.train_loss) else np.inf)


def error_E(model, m: Material, T_out):
    """E = RMSE(q_pred - q_obs) / q_ref over the held-out isotherm (PREREG 6.1)."""
    sel = m.T == T_out
    with torch.no_grad():
        pred = model(torch.as_tensor(m.s[sel]), torch.as_tensor(m.T[sel])).numpy()
    if not np.all(np.isfinite(pred)):
        return float("inf")
    return float(np.sqrt(np.mean((pred - m.q[sel]) ** 2)) / m.q_ref)


def dense_grid(m: Material, n_s=400, dT=2.5):
    """Grid G (PREREG 6.2): s from ln(1 Pa) to ln(0.95 p_sat(T)); T from T_min - 20 K to
    T_max + 20 K in 2.5 K steps."""
    T_lo, T_hi = m.temps.min() - 20.0, m.temps.max() + 20.0
    Ts = np.arange(T_lo, T_hi + 1e-9, dT)
    S, TT = [], []
    for T in Ts:
        s_hi = float(water.ln_p_sat(torch.tensor([T])) + math.log(0.95))
        S.append(np.linspace(0.0, s_hi, n_s))
        TT.append(np.full(n_s, T))
    return torch.as_tensor(np.concatenate(S)), torch.as_tensor(np.concatenate(TT))


def violation_counts(model, m: Material):
    """Counts on G: dq/ds < 0, q < 0, undefined Qst, Qst outside 0 to 150 kJ/mol."""
    s, T = dense_grid(m)
    q, q_s, q_T = thermo._derivatives(model, s, T)
    qst = -thermo.R * T**2 * q_T / q_s
    finite = torch.isfinite(qst) & (q_s > 0)
    return {
        "points": int(s.numel()),
        "nonmonotone": int((q_s < 0).sum()),
        "negative_q": int((q < 0).sum()),
        "undefined_qst": int((~finite).sum()),
        "qst_out_of_range": int((finite & ((qst < 0) | (qst > 150e3))).sum()),
    }


def qst_error(model, truth, m: Material, T_out):
    """Synthetic benchmark (PREREG 6.3a): RMS of Qst_model - Qst_true in kJ/mol, over the
    held-out isotherm's own (p, T) states whose true loading lies in 0.1 to 0.9 q_ref.
    Comparing at the observed states avoids inverting non-monotone models to a loading."""
    sel = m.T == T_out
    s = torch.as_tensor(m.s[sel])
    T = torch.as_tensor(m.T[sel])
    with torch.no_grad():
        q_true = truth(s, T)
    keep = (q_true >= 0.1 * m.q_ref) & (q_true <= 0.9 * m.q_ref)
    if keep.sum() == 0:
        return float("nan")
    a = thermo.isosteric_heat(model, s[keep], T[keep])
    b = thermo.isosteric_heat(truth, s[keep], T[keep])
    d = (a - b) / 1e3
    if not torch.all(torch.isfinite(d)):
        return float("inf")
    return float(torch.sqrt(torch.mean(d**2)))
