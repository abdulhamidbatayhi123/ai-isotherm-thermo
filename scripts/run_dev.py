"""Development-set tuning (PREREG_P3A.md section 5.4). Uses only the development materials.

For each cell, 6 configurations are drawn uniformly without replacement from that cell's
grid with seed 20261013 (all of them if the grid has 6 or fewer). Each configuration is
fitted on the development materials for the tasks E-high and E-low from 3 seeds (tuning
only; confirmatory fits use 5), the best seed by training loss is kept, and the score is
the mean of e = mean log10 E over tasks and materials. The best configuration per cell is
written to results/dev_best_configs.json, which the confirmatory run reads.

Resumable: every finished (cell, config, material, task) is appended to
results/dev_runs[_<worker>].jsonl and skipped on restart (all such files are read).
Single-threaded torch: the tensors are small, and threads only contend on a shared CPU, so
parallelism comes from several worker processes on disjoint cells.
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
N_CONFIGS = 6
TUNE_SEEDS = (0, 1, 2)
ADAM = (2000, 4000)
LAMS = (0.01, 0.1, 1.0, 10.0, 100.0)
VTERMS = [(h, c) for h in (1, 2) for c in (2, 4, 6)]

GRIDS = {
    "P": [dict(n_henry=h, n_coop=c, adam_steps=a) for (h, c), a in itertools.product(VTERMS, ADAM)],
    "P-K": [dict(n_henry=h, n_coop=c, adam_steps=a) for (h, c), a in itertools.product(VTERMS, ADAM)],
    "V-none": [dict(n_henry=h, n_coop=c, adam_steps=a) for (h, c), a in itertools.product(VTERMS, ADAM)],
    "V-pen": [dict(n_henry=h, n_coop=c, adam_steps=a, lam=l) for (h, c), a, l in itertools.product(VTERMS, ADAM, LAMS)],
    "A-hard": [dict(n_terms=n, adam_steps=a) for n, a in itertools.product((3, 4, 6), ADAM)],
    "A-none": [dict(n_terms=n, adam_steps=a) for n, a in itertools.product((3, 4, 6), ADAM)],
    "A-pen": [dict(n_terms=n, adam_steps=a, lam=l) for n, a, l in itertools.product((3, 4, 6), ADAM, LAMS)],
    "F-none": [dict(hidden=h, depth=2, adam_steps=a) for h, a in itertools.product((16, 32), ADAM)],
    "F-pen": [dict(hidden=h, depth=2, adam_steps=a, lam=l) for h, a, l in itertools.product((16, 32), ADAM, LAMS)],
    "F-hard": [dict(hidden=hd, n_henry=h, n_coop=c, adam_steps=a)
               for hd, (h, c), a in itertools.product((8, 16), VTERMS, ADAM)],
    "C1": [dict(adam_steps=a) for a in ADAM],
}


def draw(cell):
    grid = GRIDS[cell]
    if len(grid) <= N_CONFIGS:
        return grid
    rng = random.Random(f"{SEED}-{cell}")
    return rng.sample(grid, N_CONFIGS)


def load_materials(setname):
    d = pd.read_csv(ROOT / "data/raw/dataset/isotherms.csv")
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
    cells = sys.argv[1:] or list(GRIDS)
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
        s = g.groupby("cfg")["score"].mean().sort_values()
        best[cell] = {"config": json.loads(s.index[0]), "dev_mean_log10E": float(s.iloc[0]),
                      "n_configs_tried": int(s.size), "all": {k: float(v) for k, v in s.items()}}
    (ROOT / "results/dev_best_configs.json").write_text(json.dumps(best, indent=2))
    for cell, b in best.items():
        print(f"{cell:7s} best dev mean log10E {b['dev_mean_log10E']:.3f} ({b['n_configs_tried']} configs) {b['config']}")


if __name__ == "__main__":
    main()
