"""Pre-freeze check that the verdicts can go each way (PREREG_P3A.md section 7.4;
PAPER_WORKFLOW_LESSONS section 10). Rewritten 2026-11-08 before the freeze (review G1).

Four synthetic worlds, each with as many materials as the confirmatory set, independent of
the confirmatory uptake data.
Material i uses the temperatures of confirmatory material i (temperatures only, which the
pre-registration lists), on a 25-point grid in p/psat from 0.02 to 0.90, with Gaussian noise
of SIGMA_REL x q_ref (q_ref = the truth's largest uptake on that grid). Shapes (step
position, width, capacity, Henry share) are drawn from a declared distribution, seed
SHAPE_SEED.

  KS0   two-site Sips, van't Hoff (dc = 0): exactly inside P's family (rival of A-hard)
  DA    Dubinin-Astakhov: exactly inside A-hard's family
  FW    Kirchhoff-Sips with a large heat capacity (dc = 250 J/mol/K): van't Hoff is wrong,
        the free temperature network can follow it (H1a can fail)
  FLAT  one weakly curved Langmuir site (Q = 50 kJ/mol): every model can fit it; no benign
        model should be flagged by H3 and the hard and penalty models should agree
  SUB   sub-linear Sips (exponent 0.5 to 0.9), van't Hoff: outside P's family (exponents 1 or
        >= 1.5), inside V-none's and V-pen's: the world in which H1b can fail (added P3A-21)

Expectations, fixed before any world was run (EXPECT): each names the classes of section 8
that count as "as expected". A world whose verdict misses its expectation is reported with
the freeze, and its cause is found before the freeze.

The cells P, F-hard, V-pen, A-hard, F-none, C1 (the five H1 comparisons) and V-none are
fitted with the tuned configurations from 5 seeds for E-high and E-low; violations are
counted on grid G as in the confirmatory run; the verdicts come from scripts/analyse.py.

  WORLD_WORKER=a python scripts/verdict_worlds.py run KS0 DA [--shard 0/2]
  python scripts/verdict_worlds.py analyse      -> results/verdicts_worlds_<W>.json,
                                                   results/worlds_check.json
"""
import json
import math
import os
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

SIGMA_REL = 0.004  # largest measured raster RMS per isotherm maximum (0.0034), rounded up
RH = np.linspace(0.02, 0.90, 25)
CELLS = ("P", "F-hard", "V-pen", "A-hard", "F-none", "C1", "V-none")
SEEDS = (0, 1, 2, 3, 4)
SHAPE_SEED = 20261108
WORLDS = ("KS0", "DA", "FW", "FLAT", "SUB")
T0 = 298.15

EXPECT = {
    "KS0": {"H1c": ["P_better"], "H1b": ["equivalent", "differ_small", "P_better"]},
    "DA": {"H1c": ["X_better"]},
    "FW": {"H1a": ["X_better", "inconclusive", "equivalent", "differ_small", "differ_uncertain"]},
    # added 2026-11-09 after the first four worlds, before the freeze (CORRECTIONS P3A-21):
    # a truth P cannot represent but its unconstrained twin can, so that H1b can fail
    "SUB": {"H1b": ["X_better"]},
    "FLAT": {"H1b": ["equivalent", "differ_small"],
             "H3": {"P": ["none"], "V-pen": ["none", "rare", "some"], "V-none": ["none", "rare", "some"],
                    "F-none": ["none", "rare", "some"]}},
}


def draw_shapes(rng, n):
    """Step at p/psat 0.05 to 0.40, width (in ln p) 0.05 to 0.30, capacity 10 to 40 mol/kg,
    Henry share 0.02 to 0.25."""
    return [dict(step=rng.uniform(0.05, 0.40), width=rng.uniform(0.05, 0.30),
                 cap=rng.uniform(10, 40), henry=rng.uniform(0.02, 0.25)) for _ in range(n)]


def truth_for(world, sh):
    psat0 = float(water.p_sat(torch.tensor([T0])))
    s_step = math.log(sh["step"] * psat0)
    g = max(1.5, 1.0 / sh["width"])
    if world == "KS0":
        a = syn.sips_kirchhoff(sh["henry"] * sh["cap"], math.exp(-(s_step - 1.5)), 55e3, 0.0, 1.0, T0)
        b = syn.sips_kirchhoff((1 - sh["henry"]) * sh["cap"], math.exp(-s_step), 48e3, 0.0, g, T0)
        return lambda s, T: a(s, T) + b(s, T)
    if world == "FW":
        a = syn.sips_kirchhoff(sh["henry"] * sh["cap"], math.exp(-(s_step - 1.5)), 55e3, 0.0, 1.0, T0)
        b = syn.sips_kirchhoff((1 - sh["henry"]) * sh["cap"], math.exp(-s_step), 48e3, 250.0, g, T0)
        return lambda s, T: a(s, T) + b(s, T)
    if world == "DA":
        A_step = R * T0 * math.log(1.0 / sh["step"])
        n = min(6.0, max(1.0, 1.0 / (5 * sh["width"])))
        E = A_step / (math.log(2.0) ** (1.0 / n))  # W = W0/2 at the step
        return syn.dubinin_astakhov(sh["cap"], E, n)
    if world == "SUB":
        # sub-linear Sips (exponent 0.5 to 0.9, a heterogeneous surface; no finite Henry slope):
        # P's terms have exponent 1 or >= 1.5, its unconstrained twin's exponents are free
        g_sub = 0.5 + 0.4 * (sh["width"] - 0.05) / 0.25
        return syn.sips_kirchhoff(sh["cap"], math.exp(-s_step), 50e3, 0.0, g_sub, T0)
    if world == "FLAT":
        # Langmuir with theta = 0.6 at p/psat = 0.9 and 25 C: weakly curved
        b = 0.6 / 0.4 / (0.9 * psat0)
        return syn.sips_kirchhoff(sh["cap"], b, 50e3, 0.0, 1.0, T0)
    raise ValueError(world)


def confirmatory_temperatures():
    summ = json.loads((ROOT / "data/dataset_summary.json").read_text())
    return [v["temperatures_K"] for k, v in sorted(summ.items()) if v["set"] == "confirmatory"]


def world_materials(world):
    temps_all = confirmatory_temperatures()
    shapes = draw_shapes(np.random.default_rng(SHAPE_SEED), len(temps_all))
    out = []
    for i, (sh, temps) in enumerate(zip(shapes, temps_all)):
        truth = truth_for(world, sh)
        T = np.repeat(np.asarray(temps, float), len(RH))
        s = np.concatenate([np.log(RH * float(water.p_sat(torch.tensor([t])))) for t in temps])
        with torch.no_grad():
            q = truth(torch.as_tensor(s), torch.as_tensor(T)).numpy()
        rng = np.random.default_rng(SHAPE_SEED + 100 * i + WORLDS.index(world))
        q = q + rng.normal(0, SIGMA_REL * q.max(), q.shape)
        out.append(study.Material(f"{world}-world material {i}", T, s, q))
    return out


def run(worlds, shard):
    best = json.loads((ROOT / "results/dev_best_configs.json").read_text())
    worker = os.environ.get("WORLD_WORKER", "")
    log = ROOT / f"results/worlds_runs{'_' + worker if worker else ''}.jsonl"
    done = {(r["world"], r["cell"], r["material"], r["task"]) for r in all_rows()}
    k, K = shard
    torch.set_num_threads(1)
    for world in worlds:
        for i, m in enumerate(world_materials(world)):
            if i % K != k:
                continue
            for cell in CELLS:
                cfg = study.Config(**best[cell]["config"])
                for task in ("E-high", "E-low"):
                    if (world, cell, m.name, task) in done:
                        continue
                    train_T, T_out = study.tasks(m)[task]
                    t0 = time.time()
                    rec = {"world": world, "cell": cell, "material": m.name, "task": task,
                           "T_out": float(T_out), "train_T": [float(t) for t in train_T], "config": asdict(cfg)}
                    try:
                        res = study.fit_cell(cell, cfg, m, train_T, seeds=SEEDS)
                        rec.update({"E": study.error_E(res[0].model, m, T_out), "train_loss": res[0].train_loss,
                                    "violations": study.violation_counts(res[0].model, m), "error": None})
                    except Exception as e:
                        rec.update({"E": float("inf"), "error": repr(e)})
                    rec["seconds"] = round(time.time() - t0, 1)
                    with log.open("a") as f:
                        f.write(json.dumps(rec) + "\n")
                    print(world, cell, m.name, task, f"E={rec['E']:.3g}", f"{rec['seconds']}s", flush=True)


def all_rows():
    rows = []
    for f in sorted((ROOT / "results").glob("worlds_runs*.jsonl")):
        rows += [json.loads(x) for x in f.read_text().splitlines() if x.strip()]
    return rows


def analyse_worlds():
    import analyse
    rows = all_rows()
    check = {}
    for world in WORLDS:
        sub = [r for r in rows if r["world"] == world]
        if not sub:
            continue
        f = ROOT / f"results/worlds_{world}.jsonl"
        f.write_text("".join(json.dumps(r) + "\n" for r in sub))
        sys.argv = ["analyse.py", str(f)]
        try:
            out = analyse.main()
        except SystemExit as e:  # a P bug halts: record it as an unmet expectation
            check[world] = {"halted": str(e)}
            continue
        res = {}
        for key, allowed in EXPECT[world].items():
            if key == "H3":
                for cell, ok in allowed.items():
                    got = out["H3"]["cells"][cell]["class"]
                    res[f"H3 {cell}"] = {"got": got, "allowed": ok, "met": got in ok}
            else:
                r = out["H1"].get(key) or out["descriptive"][key]
                res[key] = {"got": r["class"], "allowed": allowed, "met": r["class"] in allowed,
                            "R": r["R"], "R_ci95": r["R_ci95"]}
        check[world] = res
    (ROOT / "results/worlds_check.json").write_text(json.dumps(check, indent=2))
    for w, r in check.items():
        for k, v in r.items():
            print(f"{w:5s} {k:10s} {v}")


def main():
    if sys.argv[1:2] == ["analyse"]:
        return analyse_worlds()
    if sys.argv[1:2] != ["run"]:
        sys.exit(__doc__)
    args = sys.argv[2:]
    shard = (0, 1)
    if "--shard" in args:
        i = args.index("--shard")
        a, b = args[i + 1].split("/")
        shard = (int(a), int(b))
        args = args[:i] + args[i + 2:]
    run(args or list(WORLDS), shard)


if __name__ == "__main__":
    main()
