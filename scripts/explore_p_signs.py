"""EXPLORATORY (not pre-registered; written 2026-11-10 after the confirmatory verdicts; correction ledger X-6).

The diagnostics of the reported fits (scripts/refit_diagnostics.py) showed that P's worst extrapolation
(COF-SO3H, E-high, E = 4.0) comes from a term with a negative heat (Q_k = -129 kJ/mol) and a negative expansion
coefficient (alpha_k = -0.043 1/K): its affinity and its capacity both rise with temperature. P constrains the
shape in pressure, not the sign of the temperature dependence. This script fits a variant, P-sign, that adds the
two constraints natural for water: Q_k > 0 (exothermic adsorption on every term) and alpha_k >= 0 (capacity that
does not rise with temperature). Everything else is P: the same class, the same tuned structure, the same initial
function for a given seed (the parent constructor draws the same random numbers; Q starts at the same values, alpha
at about zero, as in P), the same fitting code, seeds, selection rule, error and violation counts. Frozen files are
not modified; the variant lives here.

    python scripts/explore_p_signs.py [--shard k/K]   -> results/explore_p_signs[.shard<k>].jsonl
"""
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from p3a import _num, models, study, water  # noqa: E402
from p3a import fit as fitmod  # noqa: E402
from run_dev import load_materials  # noqa: E402
from refit_diagnostics import heat_split  # noqa: E402

TASKS = ("E-high", "E-low", "I-mid")
ALPHA_RAW0 = -10.0  # softplus(-10) = 4.5e-5, i.e. alpha about 4.5e-8 1/K at the start (P starts at 0)


class PSign(models.PotentialIsotherm):
    """P with Q_k = softplus(Q_raw) > 0 (kJ/mol) and alpha_k = 1e-3 softplus(alpha_raw) >= 0 (1/K)."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)  # same random draws as P, so the same initial function for a seed
        with torch.no_grad():
            q0 = self.Q_kJ.detach().clone()
        del self.Q_kJ, self.alpha_milli
        # inverse softplus of the starting heats (all near 50 kJ/mol, so the inverse is the value itself)
        self.Q_raw = nn.Parameter(q0 + torch.log(-torch.expm1(-q0)))
        self.alpha_raw = nn.Parameter(torch.full_like(q0, ALPHA_RAW0))

    @property
    def Q_kJ(self):
        return _num.softplus(self.Q_raw)

    @property
    def alpha_milli(self):
        return _num.softplus(self.alpha_raw)


def fit_psign(cfg, m, train_T, seeds=(0, 1, 2, 3, 4)):
    """study.fit_cell for P, with PSign in place of PotentialIsotherm (same scales, loss, optimiser)."""
    sel = np.isin(m.T, train_T)
    s, T, q = (torch.as_tensor(m.s[sel]), torch.as_tensor(m.T[sel]), torch.as_tensor(m.q[sel]))
    q_fit = float(q.max())
    s_center, s_scale = float(s.mean()), float(max(s.std(), 0.5))
    out = []
    for seed in seeds:
        torch.manual_seed(seed)
        model = PSign(cfg.n_henry, cfg.n_coop, s_center=s_center, s_scale=s_scale, q_scale=q_fit, t_mode="vanthoff")
        loss = fitmod.fit(model, s, T, q, adam_steps=cfg.adam_steps, lbfgs_steps=cfg.lbfgs_steps, penalty=None,
                          penalty_weight=cfg.lam, q_scale=q_fit, l2=cfg.l2)
        out.append((loss if np.isfinite(loss) else np.inf, seed, model))
    return sorted(out, key=lambda r: r[0])


def main():
    torch.set_num_threads(1)
    k, K = (0, 1)
    if "--shard" in sys.argv:
        k, K = map(int, sys.argv[sys.argv.index("--shard") + 1].split("/"))
    best = json.loads((ROOT / "results/dev_best_configs.json").read_text())
    cfg = study.Config(**best["P"]["config"])
    mats = [m for i, m in enumerate(load_materials("confirmatory")) if i % K == k]
    log = ROOT / ("results/explore_p_signs.jsonl" if K == 1 else f"results/explore_p_signs.shard{k}.jsonl")
    done = set()
    if log.exists():
        done = {(r["material"], r["task"]) for r in map(json.loads, log.read_text().splitlines()) if r}
    for m in mats:
        for task, (train_T, T_out) in study.tasks(m).items():
            if task not in TASKS or (m.name, task) in done:
                continue
            t0 = time.time()
            rec = {"cell": "P-sign", "material": m.name, "task": task, "T_out": float(T_out),
                   "train_T": [float(t) for t in train_T]}
            try:
                res = fit_psign(cfg, m, train_T)
                loss, seed, model = res[0]
                rec.update({"E": study.error_E(model, m, T_out), "best_seed": seed, "train_loss": float(loss),
                            "E_all_seeds": {str(sd): study.error_E(md, m, T_out) for _, sd, md in res},
                            "train_loss_all_seeds": {str(sd): float(ls) for ls, sd, _ in res},
                            "violations": study.violation_counts(model, m), "heat": heat_split(model, m),
                            "Q_kJ": model.Q_kJ.detach().numpy().tolist(),
                            "alpha_per_K": (1e-3 * model.alpha_milli.detach().numpy()).tolist(), "error": None})
            except Exception as e:  # noqa: BLE001
                rec.update({"E": float("inf"), "error": repr(e)})
            rec["seconds"] = round(time.time() - t0, 1)
            with log.open("a") as f:
                f.write(json.dumps(rec) + "\n")
            print("P-sign", m.name, task, f"E={rec['E']:.4g}", f"{rec['seconds']}s", flush=True)


if __name__ == "__main__":
    main()
