"""Pre-freeze check that every H1 verdict can go either way (PAPER_WORKFLOW_LESSONS section 10).

Two synthetic worlds, independent of the confirmatory data:
  KS-world  every material is a Kirchhoff-Sips truth (inside P's family)
  DA-world  every material is a Dubinin-Astakhov truth (inside A-hard's family)
Each world has N_MAT synthetic materials whose shapes are drawn from a declared distribution
(step position, step width, capacity, Henry share), measured at 15, 25 and 35 C on a
25-point grid in p/psat from 0.02 to 0.9, with noise SIGMA_REL x q_ref. The H1 cells are
fitted with the tuned configurations (2 seeds, to save compute) for E-high and E-low, and
the H1 verdicts are computed with the analysis code of the confirmatory run.

Expected if the design can discriminate: in the DA-world, H1c is not "P extrapolates better
than A-hard"; in the KS-world, H1c is not "A-hard extrapolates better than P". A world in
which every verdict is the same would show that the test cannot fail.

  python scripts/verdict_worlds.py            writes results/worlds_runs.jsonl and
                                              results/verdicts_worlds_<world>.json
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
from p3a import study, synthetic as syn, water  # noqa: E402
from p3a.constants import R  # noqa: E402

N_MAT = 14
SIGMA_REL = 0.002
TEMPS_C = (15.0, 25.0, 35.0)
RH = np.linspace(0.02, 0.9, 25)
CELLS = ("P", "F-hard", "V-pen", "A-hard", "F-none")
SEEDS = (0, 1)
SHAPE_SEED = 20261108


def draw_shapes(rng):
    """Declared shape distribution: step at p/psat 0.05 to 0.40, width (in ln p) 0.05 to
    0.30, capacity 10 to 40 mol/kg, Henry share 0.02 to 0.25."""
    return [dict(step=rng.uniform(0.05, 0.40), width=rng.uniform(0.05, 0.30),
                 cap=rng.uniform(10, 40), henry=rng.uniform(0.02, 0.25)) for _ in range(N_MAT)]


def truth_for(world, sh):
    T0 = 298.15
    psat0 = float(water.p_sat(torch.tensor([T0])))
    s_step = math.log(sh["step"] * psat0)
    if world == "KS":
        g = max(1.5, 1.0 / sh["width"])
        a = syn.sips_kirchhoff(sh["henry"] * sh["cap"], math.exp(-(s_step - 1.5)), 55e3, 0.0, 1.0, T0)
        b = syn.sips_kirchhoff((1 - sh["henry"]) * sh["cap"], math.exp(-s_step), 48e3, 40.0, g, T0)
        return lambda s, T: a(s, T) + b(s, T)
    if world == "DA":
        A_step = R * T0 * math.log(1.0 / sh["step"])
        n = min(6.0, max(1.0, 1.0 / (5 * sh["width"])))
        E = A_step / (math.log(2.0) ** (1.0 / n))  # W = W0/2 at the step
        return syn.dubinin_astakhov(sh["cap"], E, n)
    raise ValueError(world)


def world_materials(world, shapes):
    out = []
    for i, sh in enumerate(shapes):
        truth = truth_for(world, sh)
        T = np.repeat([t + 273.15 for t in TEMPS_C], len(RH))
        s = np.concatenate([np.log(RH * float(water.p_sat(torch.tensor([t + 273.15])))) for t in TEMPS_C])
        with torch.no_grad():
            q = truth(torch.as_tensor(s), torch.as_tensor(T)).numpy()
        rng = np.random.default_rng(SHAPE_SEED + 100 * i + (0 if world == "KS" else 1))
        q = q + rng.normal(0, SIGMA_REL * q.max(), q.shape)
        out.append(study.Material(f"{world}-world material {i}", T, s, q))
    return out


def main():
    best = json.loads((ROOT / "results/dev_best_configs.json").read_text())
    shapes = draw_shapes(np.random.default_rng(SHAPE_SEED))
    log = ROOT / "results/worlds_runs.jsonl"
    done = set()
    if log.exists():
        done = {(r["world"], r["cell"], r["material"], r["task"])
                for r in map(json.loads, log.read_text().splitlines())}
    for world in ("KS", "DA"):
        for m in world_materials(world, shapes):
            for cell in CELLS:
                cfg = study.Config(**best[cell]["config"])
                for task in ("E-high", "E-low"):
                    if (world, cell, m.name, task) in done:
                        continue
                    train_T, T_out = study.tasks(m)[task]
                    t0 = time.time()
                    try:
                        res = study.fit_cell(cell, cfg, m, train_T, seeds=SEEDS)
                        E = study.error_E(res[0].model, m, T_out)
                    except Exception:
                        E = float("inf")
                    rec = {"world": world, "cell": cell, "material": m.name, "task": task, "E": E,
                           "config": asdict(cfg), "seconds": round(time.time() - t0, 1)}
                    with log.open("a") as f:
                        f.write(json.dumps(rec) + "\n")
                    print(world, cell, m.name, task, f"E={E:.3g}", flush=True)
    # verdicts per world with the confirmatory analysis code
    import analyse
    rows = [json.loads(x) for x in log.read_text().splitlines()]
    for world in ("KS", "DA"):
        sub = ROOT / f"results/worlds_{world}.jsonl"
        sub.write_text("".join(json.dumps(r) + "\n" for r in rows if r["world"] == world))
        sys.argv = ["analyse.py", str(sub)]
        analyse.main()


if __name__ == "__main__":
    main()
