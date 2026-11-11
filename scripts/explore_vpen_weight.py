"""EXPLORATORY (not pre-registered; written 2026-11-11 after the confirmatory verdicts, in answer to review R3 M1 and
R2 M7; correction ledger X-7).

At the weight tuned for accuracy on the development materials (one weight lam for both penalty terms), V-pen left
shape violations in about as many extrapolations as the unpenalised V-none (9 and 8 of 26), so the confirmatory H1b
compares the hard constraints with a penalty that carries little force. This script asks what a penalty with force
costs: V-pen is refitted on the 13 confirmatory materials (E-high and E-low) with the monotonicity term on its own
weight w_mono, the Henry term keeping the tuned weight lam:

    loss = data + lam * henry + w_mono * monotonicity        (tuned: w_mono = lam)

Everything else is the confirmatory V-pen: the tuned configuration (results/dev_best_configs.json), the collocation
points, the scales, the seeds, the fitting code, the selection by training loss, the error E and the violation
counts. Frozen files are not modified.

    python scripts/explore_vpen_weight.py [--shard k/K]   -> results/explore_vpen_weight[.shard<k>].jsonl
    python scripts/explore_vpen_weight.py --set development [--shard k/K]   -> results/explore_vpen_weight_dev[...]
      (ledger X-8 a: the weight chosen on the development materials by the rule written in the ledger first)
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from p3a import models, study  # noqa: E402
from p3a import fit as fitmod  # noqa: E402
from run_dev import load_materials  # noqa: E402

TASKS = ("E-high", "E-low")
W_MONO = (0.1, 10.0, 1000.0)   # the tuned joint weight is 1e-3: these are 1e2, 1e4 and 1e6 times heavier
SEEDS = (0, 1, 2, 3, 4)


def penalty_parts(T_lo, T_hi, q_scale):
    s_c, T_c, s_low, T_low = study.collocation(T_lo, T_hi)

    def mono(model):
        return models.monotonicity_penalty(model, s_c, T_c) / q_scale**2

    def henry(model):
        return models.henry_penalty(model, s_low, T_low, q_scale=q_scale)

    return mono, henry


def fit_weighted(cfg, m, train_T, w_mono):
    """study.fit_cell('V-pen', ...) with the monotonicity weight separated from the Henry weight."""
    sel = np.isin(m.T, train_T)
    s, T, q = (torch.as_tensor(m.s[sel]), torch.as_tensor(m.T[sel]), torch.as_tensor(m.q[sel]))
    q_fit = float(q.max())
    s_center, s_scale = float(s.mean()), float(max(s.std(), 0.5))
    mono, henry = penalty_parts(float(T.min()), float(T.max()), q_fit)
    ratio = w_mono / cfg.lam

    def pen(model):                    # fit() multiplies by penalty_weight = lam
        return ratio * mono(model) + henry(model)

    out = []
    for seed in SEEDS:
        torch.manual_seed(seed)
        model = study.build("V-pen", cfg, s_center, s_scale, q_fit)
        loss = fitmod.fit(model, s, T, q, adam_steps=cfg.adam_steps, lbfgs_steps=cfg.lbfgs_steps, penalty=pen,
                          penalty_weight=cfg.lam, q_scale=q_fit, l2=cfg.l2)
        out.append((loss if np.isfinite(loss) else np.inf, seed, model))
    out.sort(key=lambda r: r[0])
    return out, mono, henry


def main():
    torch.set_num_threads(1)
    k, K = (0, 1)
    if "--shard" in sys.argv:
        k, K = map(int, sys.argv[sys.argv.index("--shard") + 1].split("/"))
    best = json.loads((ROOT / "results/dev_best_configs.json").read_text())
    cfg = study.Config(**best["V-pen"]["config"])
    setname = sys.argv[sys.argv.index("--set") + 1] if "--set" in sys.argv else "confirmatory"
    if setname not in ("confirmatory", "development"):
        raise SystemExit("--set confirmatory|development")
    stem = "explore_vpen_weight" if setname == "confirmatory" else "explore_vpen_weight_dev"   # X-8 (a)
    mats = [m for i, m in enumerate(load_materials(setname)) if i % K == k]
    log = ROOT / (f"results/{stem}.jsonl" if K == 1 else f"results/{stem}.shard{k}.jsonl")
    done = set()
    if log.exists():
        done = {(r["material"], r["task"], r["w_mono"]) for r in map(json.loads, log.read_text().splitlines()) if r}
    for m in mats:
        for task, (train_T, T_out) in study.tasks(m).items():
            if task not in TASKS:
                continue
            for w in W_MONO:
                if (m.name, task, w) in done:
                    continue
                t0 = time.time()
                rec = {"cell": "V-pen", "w_mono": w, "lam": cfg.lam, "material": m.name, "task": task,
                       "T_out": float(T_out), "train_T": [float(t) for t in train_T]}
                try:
                    res, mono, henry = fit_weighted(cfg, m, train_T, w)
                    loss, seed, model = res[0]
                    rec.update({"E": study.error_E(model, m, T_out), "best_seed": seed, "train_loss": float(loss),
                                "E_all_seeds": {str(sd): study.error_E(md, m, T_out) for _, sd, md in res},
                                "violations": study.violation_counts(model, m),
                                "mono_term": float(mono(model).detach()), "henry_term": float(henry(model).detach()),
                                "error": None})
                except Exception as e:  # noqa: BLE001
                    rec.update({"E": float("inf"), "error": repr(e)})
                rec["seconds"] = round(time.time() - t0, 1)
                with log.open("a") as f:
                    f.write(json.dumps(rec) + "\n")
                print("V-pen w_mono", w, m.name, task, f"E={rec['E']:.4g}", f"{rec['seconds']}s", flush=True)


if __name__ == "__main__":
    main()
