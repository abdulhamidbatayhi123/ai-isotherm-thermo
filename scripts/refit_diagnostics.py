"""Diagnostics of the reported fits, by exact refit of their selected seeds (written 2026-11-10 after the
confirmatory verdicts, in answer to the fresh-eyes review R1; correction ledger X-4). Descriptive only.

For every E-high and E-low fit of the cells below, the selected seed (best_seed of the run record) is
refitted with the frozen code and configuration; the refit must reproduce the recorded E. Then:
  1. The isosteric heat on the PREREG 6.2 grid G, split by domain ("in": the penalty domain, T within
     T_min - 15 K .. T_max + 15 K and p <= 0.90 p_sat; "out": the rest of G) into the counts of points with
     Qst < 0, Qst > 150 kJ/mol and undefined Qst (q_s <= 0 or not finite). The run records hold only the
     total count of Qst outside 0..150 kJ/mol (PREREG 6.2 strict count), not its sign or domain.
  2. For the van't Hoff cells (P, V-none, V-pen) the fitted heats Q_k (kJ/mol) and expansion
     coefficients alpha_k (1/K) of every term, with each term's capacity at T_out.
  3. The predicted isotherm at the held-out temperature on 200 points of p/p_sat in 1e-3 .. 0.95 (for the
     example figure), with the observed points' p/p_sat.
For P on COF-SO3H in E-high all five seeds are refitted and their training losses recorded (the run
records keep only the selected seed's training loss).

    python scripts/refit_diagnostics.py [--shard k/K]   -> results/refit_diagnostics[.shard<k>].jsonl
"""
import json
import math
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from p3a import study, thermo, water  # noqa: E402
from run_dev import load_materials  # noqa: E402

CELLS = ("P", "V-pen", "V-none", "A-hard", "C1", "F-hard", "F-none")
TASKS = ("E-high", "E-low")
ALL_SEEDS = {("P", "COF-SO3H", "E-high")}


def records():
    out = {}
    for f in sorted((ROOT / "results").glob("confirmatory_runs.shard*.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                out[(r["cell"], r["material"], r["task"])] = r
    return out


def heat_split(model, m):
    s, T = study.dense_grid(m)
    _, q_s, q_T = thermo._derivatives(model, s, T)
    qst = (-thermo.R * T**2 * q_T / q_s).detach().numpy() / 1e3
    qs = q_s.detach().numpy()
    Tn, sn = T.numpy(), s.numpy()
    T_lo, T_hi = m.temps.min() - 15.0, m.temps.max() + 15.0
    inside = ((Tn >= T_lo - 1e-9) & (Tn <= T_hi + 1e-9)
              & (sn <= water.ln_p_sat(T).numpy() + math.log(0.90) + 1e-12))
    undef = ~(np.isfinite(qst) & (qs > 0))
    out = {"points": int(sn.size)}
    for dom, mask in (("in", inside), ("out", ~inside)):
        ok = mask & ~undef
        out[f"neg_{dom}"] = int((ok & (qst < 0)).sum())
        out[f"high_{dom}"] = int((ok & (qst > 150)).sum())
        out[f"undef_{dom}"] = int((mask & undef).sum())
        out[f"n_{dom}"] = int(mask.sum())
    return out


def vanthoff_terms(model, T_out):
    if not hasattr(model, "Q_kJ") or not hasattr(model, "alpha_milli"):
        return None
    with torch.no_grad():
        Q = model.Q_kJ.detach().numpy().tolist()
        alpha = (1e-3 * model.alpha_milli.detach().numpy()).tolist()
    return {"Q_kJ": Q, "alpha_per_K": alpha}


def curve(model, m, T_out):
    lnps = float(water.ln_p_sat(torch.tensor([T_out], dtype=torch.float64)))
    x = np.logspace(-3, math.log10(0.95), 200)
    s = torch.as_tensor(np.log(x) + lnps)
    with torch.no_grad():
        q = model(s, torch.full_like(s, T_out)).numpy()
    sel = m.T == T_out
    # the measured points are third-party data (data/open/README.md): keep only their count and a hash
    # (2026-11-12; scripts/strip_observed_points.py did the same to the existing records)
    from strip_observed_points import obs_hash
    x_obs, q_obs = np.exp(m.s[sel] - lnps).tolist(), m.q[sel].tolist()
    return {"x": x.tolist(), "q": q.tolist(), "n_obs": len(x_obs), "obs_sha256": obs_hash(x_obs, q_obs)}


def main():
    torch.set_num_threads(1)
    k, K = (0, 1)
    if "--shard" in sys.argv:
        k, K = map(int, sys.argv[sys.argv.index("--shard") + 1].split("/"))
    best = json.loads((ROOT / "results/dev_best_configs.json").read_text())
    recs = records()
    mats = [m for i, m in enumerate(load_materials("confirmatory")) if i % K == k]
    log = ROOT / ("results/refit_diagnostics.jsonl" if K == 1 else f"results/refit_diagnostics.shard{k}.jsonl")
    done = set()
    if log.exists():
        done = {(r["cell"], r["material"], r["task"]) for r in map(json.loads, log.read_text().splitlines()) if r}
    for m in mats:
        tasks = study.tasks(m)
        for cell in CELLS:
            cfg = study.Config(**best[cell]["config"])
            for task in TASKS:
                if (cell, m.name, task) in done:
                    continue
                rec0 = recs[(cell, m.name, task)]
                assert asdict(cfg) == rec0["config"]
                train_T, T_out = tasks[task]
                t0 = time.time()
                all_seeds = (cell, m.name.split(" |")[0], task) in ALL_SEEDS
                seeds = (0, 1, 2, 3, 4) if all_seeds else (int(rec0["best_seed"]),)
                res = study.fit_cell(cell, cfg, m, train_T, seeds=seeds)
                sel = [r for r in res if r.seed == int(rec0["best_seed"])][0]
                E = study.error_E(sel.model, m, T_out)
                out = {"cell": cell, "material": m.name, "task": task, "T_out": float(T_out),
                       "seed": int(rec0["best_seed"]), "E_refit": E, "E_record": rec0["E"],
                       "E_rel_diff": abs(E - rec0["E"]) / rec0["E"],
                       "heat": heat_split(sel.model, m), "terms": vanthoff_terms(sel.model, float(T_out)),
                       "curve": curve(sel.model, m, float(T_out))}
                if all_seeds:
                    out["all_seeds"] = [{"seed": r.seed, "train_loss": r.train_loss,
                                         "E": study.error_E(r.model, m, T_out),
                                         "terms": vanthoff_terms(r.model, float(T_out))} for r in res]
                out["seconds"] = round(time.time() - t0, 1)
                with log.open("a") as f:
                    f.write(json.dumps(out) + "\n")
                h = out["heat"]
                print(cell, m.name, task, f"E {E:.4g} rel {out['E_rel_diff']:.1e}",
                      f"neg in/out {h['neg_in']}/{h['neg_out']} high in/out {h['high_in']}/{h['high_out']}",
                      f"{out['seconds']}s", flush=True)


if __name__ == "__main__":
    main()
