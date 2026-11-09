"""Development-set tuning (PREREG_P3A.md section 5.4). Uses only the development materials.

Two stages (revised 2026-11-08 before the freeze, review B3 and B5):
  Stage 1 tunes the structure of the cells that own one: P, A-hard, F-hard, F-none, F-rel
  and C1. Each tries min(N_CONFIGS, grid size) configurations drawn uniformly without
  replacement from its grid with seed 20261013.
  Stage 2 inherits that structure, so that each comparison at equal form differs only in the
  constraint: V-none and P-K take P's configuration, A-none takes A-hard's (no tuning);
  V-pen, A-pen and F-pen take P's, A-hard's and F-none's configuration and tune only the
  penalty weight lambda over LAMS.
Each configuration is fitted on the development materials for the tasks E-high and E-low
from 3 seeds (tuning only; confirmatory fits use 5), the best seed by training loss is kept,
and the score is the mean of e = mean log10 E over tasks and materials. The best
configuration per cell is written to results/dev_best_configs.json, which the confirmatory
run reads.

Resumable: every finished (cell, config, material, task) is appended to
results/dev_runs[_<worker>].jsonl and skipped on restart (all such files are read).
Single-threaded torch: the tensors are small, and threads only contend on a shared CPU, so
parallelism comes from several worker processes on disjoint cells.
A stage-2 cell waits for its stage-1 cell's results, so put both on one worker in order.
Usage: DEV_WORKER=a python scripts/run_dev.py [cell ...]     |   python scripts/run_dev.py --summarise
"""
import itertools
import json
import random
import sys
import time
from dataclasses import asdict
from pathlib import Path

import os

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from p3a import study  # noqa: E402

SEED = 20261013
N_CONFIGS = 12
TUNE_SEEDS = (0, 1, 2)
ADAM = (2000, 4000)
LAMS = (1e-4, 1e-3, 0.01, 0.1, 1.0, 10.0, 100.0)  # 1e-4, 1e-3 added before the freeze (review T3-7)
VTERMS = [(h, c) for h in (1, 2) for c in (2, 4, 6)]

MLP = [dict(hidden=h, depth=d, adam_steps=a, l2=w)
       for h, d, a, w in itertools.product((16, 32, 64), (2, 3), ADAM, (0.0, 1e-5, 1e-4))]

# stage 1: cells that own a structure
GRIDS = {
    "P": [dict(n_henry=h, n_coop=c, adam_steps=a) for (h, c), a in itertools.product(VTERMS, ADAM)],
    "A-hard": [dict(n_terms=n, adam_steps=a) for n, a in itertools.product((3, 4, 6), ADAM)],
    "F-none": MLP,
    "F-rel": MLP,
    "F-hard": [dict(hidden=hd, n_henry=h, n_coop=c, adam_steps=a)
               for hd, (h, c), a in itertools.product((8, 16), VTERMS, ADAM)],
    "C1": [dict(adam_steps=a) for a in ADAM],
}
# stage 2: cells that inherit a stage-1 structure; True = tune lambda over LAMS
INHERIT = {"V-none": ("P", False), "P-K": ("P", False), "A-none": ("A-hard", False),
           "V-pen": ("P", True), "A-pen": ("A-hard", True), "F-pen": ("F-none", True)}


def draw(cell):
    if cell in INHERIT:
        base, tune_lam = INHERIT[cell]
        b = best_config(base)
        if b is None:
            raise RuntimeError(f"{cell} needs {base}'s tuning first (run them in order on one worker)")
        return [dict(b, lam=lam) for lam in LAMS] if tune_lam else [b]
    grid = GRIDS[cell]
    if len(grid) <= N_CONFIGS:
        return grid
    rng = random.Random(f"{SEED}-{cell}")
    return rng.sample(grid, N_CONFIGS)


def best_config(cell):
    """The stage-1 best configuration of `cell` from the finished runs, or None if any of its
    drawn configurations is unfinished."""
    rows = [r for r in all_runs() if r["cell"] == cell]
    if not rows:
        return None
    mats = load_materials("development")
    need = len(draw(cell)) * len(mats) * 2
    if len(rows) < need:
        return None
    df = pd.DataFrame(rows)
    df["cfg"] = df["config"].apply(lambda c: json.dumps(c, sort_keys=True))
    worst = df["log10E"].dropna().max() + 1.0 if df["log10E"].notna().any() else 1.0
    s = df.assign(score=df["log10E"].fillna(worst)).groupby("cfg")["score"].mean().sort_values()
    full = json.loads(s.index[0])
    keys = set().union(*GRIDS[cell])  # keep only the structural keys the grid varies
    return {k: v for k, v in full.items() if k in keys}


def load_materials(setname, path=None):
    d = pd.read_csv(path or ROOT / "data/raw/dataset/isotherms.csv")
    d = d[d["set"] == setname]
    out = []
    for (mat, src), g in d.groupby(["material", "source"]):
        out.append(study.Material(f"{mat} | {src}", g.T_K.to_numpy(float),
                                  np.log(g.p_Pa.to_numpy(float)), g.q_molkg.to_numpy(float)))
    return out


def all_runs():
    rows = []
    for f in sorted((ROOT / "results").glob("dev_runs*.jsonl")):
        rows += [json.loads(line) for line in f.read_text().splitlines() if line.strip()]
    return rows


def main():
    if sys.argv[1:] == ["--summarise"]:
        return summarise()
    torch.set_num_threads(1)
    cells = sys.argv[1:] or list(GRIDS) + list(INHERIT)
    mats = load_materials("development")
    worker = os.environ.get("DEV_WORKER", "")
    log = ROOT / f"results/dev_runs{'_' + worker if worker else ''}.jsonl"
    log.parent.mkdir(exist_ok=True)
    done = {(r["cell"], json.dumps(r["config"], sort_keys=True), r["material"], r["task"]) for r in all_runs()}
    for cell in cells:
        for cfg_d in draw(cell):
            cfg = study.Config(**cfg_d)
            key_cfg = json.dumps(asdict(cfg), sort_keys=True)
            for m in mats:
                for task in ("E-high", "E-low"):
                    if (cell, key_cfg, m.name, task) in done:
                        continue
                    train_T, T_out = study.tasks(m)[task]
                    t0 = time.time()
                    try:
                        res = study.fit_cell(cell, cfg, m, train_T, seeds=TUNE_SEEDS)
                        E = study.error_E(res[0].model, m, T_out)
                        err = None
                    except Exception as e:  # recorded as a failure, never dropped
                        E, err = float("inf"), repr(e)
                    rec = {"cell": cell, "config": asdict(cfg), "material": m.name, "task": task,
                           "E": E, "log10E": float(np.log10(E)) if np.isfinite(E) and E > 0 else None,
                           "error": err, "seconds": round(time.time() - t0, 1)}
                    with log.open("a") as f:
                        f.write(json.dumps(rec) + "\n")
                    print(cell, cfg_d, m.name, task, f"E={E:.4g}", f"{rec['seconds']}s", flush=True)
    summarise()


def summarise():
    df = pd.DataFrame(all_runs())
    df["cfg"] = df["config"].apply(lambda c: json.dumps(c, sort_keys=True))
    # a failure (inf E) scores as the worst observed log10 E plus one decade
    worst = df["log10E"].dropna().max() + 1.0 if df["log10E"].notna().any() else 1.0
    df["score"] = df["log10E"].fillna(worst)
    best = {}
    for cell, g in df.groupby("cell"):
        if cell not in GRIDS and cell not in INHERIT:
            continue
        s = g.groupby("cfg")["score"].mean().sort_values()
        best[cell] = {"config": json.loads(s.index[0]), "dev_mean_log10E": float(s.iloc[0]),
                      "n_configs_tried": int(s.size), "all": {k: float(v) for k, v in s.items()}}
    (ROOT / "results/dev_best_configs.json").write_text(json.dumps(best, indent=2))
    for cell, b in best.items():
        print(f"{cell:7s} best dev mean log10E {b['dev_mean_log10E']:.3f} ({b['n_configs_tried']} configs) {b['config']}")


if __name__ == "__main__":
    main()
