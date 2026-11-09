"""The Paper 3A comparison: models of the factorial, tasks, fitting with seeds, evaluation.

Everything a confirmatory run does is defined here and fixed by PREREG_P3A.md:
  cells     F/V/A x none/pen/hard (section 4), C1, and the secondary P-K
  tasks     E-high, E-low, I-mid (section 5.1)
  fitting   loss on q / q_fit (q_fit from the training temperatures only), Adam then
            L-BFGS, 5 seeds, lowest training loss (5.2, 5.3)
  outcomes  E (6.1), violations on the dense grid G (6.2), isosteric heat (6.3)
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import torch

from . import fit as fitmod
from . import models, thermo, water

CELLS = ("F-none", "F-pen", "F-hard", "V-none", "V-pen", "P", "A-none", "A-pen", "A-hard", "C1", "P-K",
         "F-rel")
# Violation tolerance (PREREG 6.2): a drop of q along an isotherm, or a negative q, counts only
# when larger than this fraction of q_ref; strict counts (tolerance 0) are reported beside it.
VIOL_TOL = 0.02


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
    l2: float = 0.0           # weight decay (MLP cells)
    adam_steps: int = 2000
    lbfgs_steps: int = 300


def build(cell: str, cfg: Config, s_center: float, s_scale: float, q_scale: float):
    """A fresh model of one factorial cell; torch's seed must be set by the caller."""
    common = dict(s_center=s_center, s_scale=s_scale, q_scale=q_scale)
    if cell in ("F-none", "F-pen"):
        return models.MLPIsotherm(hidden=cfg.hidden, depth=cfg.depth, **common)
    if cell == "F-rel":  # s_center, s_scale refer to ln(p/p_sat) here (see fit_cell)
        return models.MLPIsotherm(hidden=cfg.hidden, depth=cfg.depth, inputs="rel", **common)
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
    """Fit one cell from several seeds; returns all results, best first (PREREG 5.3).

    Every scale is set from the training temperatures only (CORRECTIONS P3A-10): ln p is
    centred on its training mean and scaled by its standard deviation (at least 0.5), and
    uptake is scaled by q_fit, the largest training uptake. The material's q_ref, which
    includes the held-out isotherm, is used only to score (E, violations)."""
    sel = np.isin(m.T, train_T)
    s = torch.as_tensor(m.s[sel])
    T = torch.as_tensor(m.T[sel])
    q = torch.as_tensor(m.q[sel])
    q_fit = float(q.max())
    x = s - water.ln_p_sat(T) if cell == "F-rel" else s
    s_center, s_scale = float(x.mean()), float(max(x.std(), 0.5))
    pen = penalty_fn(cell, float(T.min()), float(T.max()), q_fit)
    out = []
    for seed in seeds:
        torch.manual_seed(seed)
        model = build(cell, cfg, s_center, s_scale, q_fit)
        init = torch.cat([p.detach().flatten() for p in model.parameters()]).numpy().copy()
        loss = fitmod.fit(model, s, T, q, adam_steps=cfg.adam_steps,
                          lbfgs_steps=cfg.lbfgs_steps, penalty=pen, penalty_weight=cfg.lam,
                          q_scale=q_fit, l2=cfg.l2)
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


def violation_counts(model, m: Material, tol=VIOL_TOL):
    """Violation counts on G (PREREG 6.2).

    Strict counts (every point of G): dq/ds < 0, q < 0, undefined Qst, Qst outside 0 to
    150 kJ/mol.
    Tolerant counts, split by domain (review C1): "in" is the penalty collocation domain
    (T within T_min - 15 K .. T_max + 15 K, p <= 0.90 p_sat), "out" is the rest of G. On each
    grid isotherm (fixed T) the drop is the largest fall of q below its running maximum as s
    increases; an isotherm violates if its drop exceeds tol x q_ref, and a point violates if
    q < -tol x q_ref. H3's primary count is "in"; "out" is reported separately.
    """
    s, T = dense_grid(m)
    q, q_s, q_T = thermo._derivatives(model, s, T)
    qst = -thermo.R * T**2 * q_T / q_s
    finite = torch.isfinite(qst) & (q_s > 0)
    out = {
        "points": int(s.numel()),
        "nonmonotone": int((q_s < 0).sum()),
        "negative_q": int((q < 0).sum()),
        "undefined_qst": int((~finite).sum()),
        "qst_out_of_range": int((finite & ((qst < 0) | (qst > 150e3))).sum()),
    }
    thr = tol * m.q_ref
    T_lo, T_hi = m.temps.min() - 15.0, m.temps.max() + 15.0
    Tn, sn, qn = T.numpy(), s.numpy(), q.detach().numpy()
    in_T = (Tn >= T_lo - 1e-9) & (Tn <= T_hi + 1e-9)
    in_s = sn <= water.ln_p_sat(T).numpy() + math.log(0.90) + 1e-12
    inside = in_T & in_s
    for dom, mask in (("in", inside), ("out", ~inside)):
        n_iso, n_neg = 0, 0
        for Tv in np.unique(Tn):
            idx = (Tn == Tv) & mask
            if idx.sum() < 2:
                continue
            qi = qn[idx]  # s increases along each row of G
            drop = float(np.max(np.maximum.accumulate(qi) - qi))
            n_iso += int(drop > thr)
            n_neg += int((qi < -thr).sum())
        out[f"tol_drop_isotherms_{dom}"] = n_iso
        out[f"tol_negative_points_{dom}"] = n_neg
    return out


def violates(v, domain="in"):
    """H3 primary rule (PREREG 6.2): a fit violates if, in the domain, any grid isotherm drops
    by more than the tolerance or any point lies below minus the tolerance."""
    return bool(v[f"tol_drop_isotherms_{domain}"] > 0 or v[f"tol_negative_points_{domain}"] > 0)


def p_bug(v):
    """P must show zero strict counts of the first three kinds (PREREG 6.2), or it is a bug and
    the analysis halts. qst_out_of_range is excluded: it can be non-zero for P."""
    return bool(v["nonmonotone"] > 0 or v["negative_q"] > 0 or v["undefined_qst"] > 0)


def qst_error(model, truth, m: Material, T_out, min_states=3):
    """Synthetic benchmark (PREREG 6.3a). Returns (primary, secondary), RMS in kJ/mol.

    Primary, loading-matched (review F1): at each held-out state (p, T) the model's loading
    q_model(p, T) is taken; where it lies in 0.1 to 0.9 q_ref, the model's Qst there is compared
    with the truth's Qst at the same loading and temperature, found by inverting the truth
    (which is monotone). This compares Qst(q) curves without inverting a possibly
    non-monotone model.
    Secondary, state-matched: the two heats at the observed states whose true loading lies in
    0.1 to 0.9 q_ref.
    A task fails (inf) if any compared Qst is undefined or non-finite, or if fewer than
    min_states states fall in the window. This favours models whose heat is defined
    everywhere, and is declared in PREREG 6.3a."""
    sel = m.T == T_out
    s = torch.as_tensor(m.s[sel])
    T = torch.as_tensor(m.T[sel])
    lo, hi = 0.1 * m.q_ref, 0.9 * m.q_ref

    def rms(a, b):
        d = (a - b) / 1e3
        if d.numel() < min_states or not torch.all(torch.isfinite(d)):
            return float("inf")
        return float(torch.sqrt(torch.mean(d**2)))

    with torch.no_grad():
        q_mod = model(s, T)
        q_true = truth(s, T)
    keep = torch.isfinite(q_mod) & (q_mod >= lo) & (q_mod <= hi)
    if int(keep.sum()) < min_states:
        primary = float("inf")
    else:
        s_star = thermo.invert_isotherm(truth, q_mod[keep], T[keep])
        with torch.no_grad():
            back = truth(s_star, T[keep])
        if not torch.all(torch.abs(back - q_mod[keep]) <= 1e-6 * m.q_ref):
            primary = float("inf")  # the truth cannot reach the model's loading (review T3-12)
        else:
            primary = rms(thermo.isosteric_heat(model, s[keep], T[keep]),
                          thermo.isosteric_heat(truth, s_star, T[keep]))
    keep2 = (q_true >= lo) & (q_true <= hi)
    if int(keep2.sum()) < min_states:
        secondary = float("inf")
    else:
        secondary = rms(thermo.isosteric_heat(model, s[keep2], T[keep2]),
                        thermo.isosteric_heat(truth, s[keep2], T[keep2]))
    return primary, secondary
