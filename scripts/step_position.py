"""Step-position error at the held-out temperature (PREREG 6.4, descriptive): "the error in
p/p_sat at half of q at p/p_sat = 0.90".

The confirmatory records keep E and the violation counts but not the fitted curves, so this
script refits the SELECTED seed (the one with the lowest training loss, recorded as best_seed)
of every E-high and E-low fit of the six H1 cells, with the frozen configuration and code. The
fit is deterministic (float64, CPU, one thread, torch.manual_seed per seed), so each refit must
reproduce the recorded E; the script records the relative difference and the summary reports
the largest one (a reproducibility check of the confirmatory run).

Step position of a curve at the held-out temperature T: the p/p_sat at which the curve first
reaches half of its own uptake at p/p_sat = 0.90. For the model the curve is evaluated on a
dense grid (2000 points, p/p_sat 1e-4 to 0.90); for the data it is the observed isotherm,
linearly interpolated in p/p_sat (the observed uptake at 0.90 is interpolated between the two
nearest points, or taken at the last point if the isotherm stops below 0.90). Error =
model step - observed step, in p/p_sat. The reading of "half of q at 0.90" as each curve's own
uptake is ours; the PREREG text does not say which curve's uptake.

    python scripts/step_position.py [--shard k/K]   -> results/step_position[.shard<k>].jsonl
"""
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from p3a import study, water  # noqa: E402
from run_dev import load_materials  # noqa: E402

CELLS = ("P", "V-pen", "A-hard", "F-none", "C1", "F-hard")
TASKS = ("E-high", "E-low")
X_TOP = 0.90


def records():
    out = {}
    for f in sorted((ROOT / "results").glob("confirmatory_runs.shard*.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                out[(r["cell"], r["material"], r["task"])] = r
    return out


def first_half_crossing(x, q):
    """p/p_sat where q first reaches half of q at x = X_TOP (x ascending), or nan."""
    q_top = float(np.interp(X_TOP, x, q)) if x[-1] >= X_TOP else float(q[-1])
    half = 0.5 * q_top
    if not np.isfinite(half) or half <= 0:
        return float("nan")
    above = np.nonzero(q >= half)[0]
    if len(above) == 0:
        return float("nan")
    i = above[0]
    if i == 0:
        return float(x[0])
    x0, x1, q0, q1 = x[i - 1], x[i], q[i - 1], q[i]
    return float(x0 + (half - q0) * (x1 - x0) / (q1 - q0))


def step_model(model, T):
    lnps = float(water.ln_p_sat(torch.tensor([T], dtype=torch.float64)))
    x = np.logspace(-4, np.log10(X_TOP), 2000)
    s = torch.as_tensor(np.log(x) + lnps)
    with torch.no_grad():
        q = model(s, torch.full_like(s, T)).numpy()
    return first_half_crossing(x, q)


def step_data(m, T):
    sel = m.T == T
    lnps = float(water.ln_p_sat(torch.tensor([T], dtype=torch.float64)))
    x = np.exp(m.s[sel] - lnps)
    o = np.argsort(x)
    return first_half_crossing(x[o], m.q[sel][o])


def main():
    torch.set_num_threads(1)
    k, K = (0, 1)
    if "--shard" in sys.argv:
        k, K = map(int, sys.argv[sys.argv.index("--shard") + 1].split("/"))
    best = json.loads((ROOT / "results/dev_best_configs.json").read_text())
    recs = records()
    mats = [m for i, m in enumerate(load_materials("confirmatory")) if i % K == k]
    log = ROOT / ("results/step_position.jsonl" if K == 1 else f"results/step_position.shard{k}.jsonl")
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
                train_T, T_out = tasks[task]
                assert asdict(cfg) == rec0["config"], f"{cell}: config differs from the run record"
                t0 = time.time()
                res = study.fit_cell(cell, cfg, m, train_T, seeds=(int(rec0["best_seed"]),))[0]
                E = study.error_E(res.model, m, T_out)
                sm, sd = step_model(res.model, float(T_out)), step_data(m, float(T_out))
                rec = {"cell": cell, "material": m.name, "task": task, "T_out": float(T_out),
                       "seed": int(rec0["best_seed"]), "E_refit": E, "E_record": rec0["E"],
                       "E_rel_diff": abs(E - rec0["E"]) / rec0["E"],
                       "step_model": sm, "step_data": sd, "step_error": sm - sd,
                       "seconds": round(time.time() - t0, 1)}
                with log.open("a") as f:
                    f.write(json.dumps(rec) + "\n")
                print(cell, m.name, task, f"E {E:.4g} (record {rec0['E']:.4g})",
                      f"step {sm:.4f} vs {sd:.4f}", f"{rec['seconds']}s", flush=True)


if __name__ == "__main__":
    main()
