"""EXPLORATORY, descriptive (written 2026-11-11 after the confirmatory verdicts, review R4; correction ledger X-8 c).

The pre-registered heat-range count (PREREG 6.2) is taken over the whole evaluation grid, which reaches 20 K beyond
the measured temperatures. This script asks where the out-of-range heats of the real-data fits lie relative to the
part of the isotherm that the synthetic heat test (H2) scores: for every E-high and E-low fit of P, V-pen, A-hard,
C1 and the exploratory P-sign, the reported seed is refitted with the frozen code and configuration (the refit must
reproduce the recorded E), and at the held-out temperature

  * at the measured held-out states where the model's own loading lies in 0.1 to 0.9 q_ref (the H2 window,
    PREREG 6.3a), the isosteric heat is evaluated and the states with Qst < 0, Qst > 150 kJ/mol or an undefined Qst
    are counted;
  * Qst and q along 200 points of p/p_sat in 1e-3 .. 0.95 are saved (for the example figure).

    python scripts/heat_window_real.py [--shard k/K]   -> results/heat_window_real[.shard<k>].jsonl
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
from refit_diagnostics import records  # noqa: E402
from explore_p_signs import fit_psign  # noqa: E402

CELLS = ("P", "V-pen", "A-hard", "C1", "P-sign")
TASKS = ("E-high", "E-low")
QST_HI = 150.0


def psign_records():
    out = {}
    for f in sorted((ROOT / "results").glob("explore_p_signs.shard*.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                out[(r["material"], r["task"])] = r
    return out


def window_heat(model, m, T_out):
    sel = m.T == T_out
    s = torch.as_tensor(m.s[sel])
    T = torch.as_tensor(m.T[sel])
    with torch.no_grad():
        q = model(s, T)
    keep = torch.isfinite(q) & (q >= 0.1 * m.q_ref) & (q <= 0.9 * m.q_ref)
    out = {"n_states": int(sel.sum()), "n_window": int(keep.sum())}
    if int(keep.sum()) == 0:
        out.update({"neg": 0, "high": 0, "undef": 0, "qst_min": None, "qst_max": None})
        return out
    qst = thermo.isosteric_heat(model, s[keep], T[keep]).detach().numpy() / 1e3
    fin = np.isfinite(qst)
    out.update({"neg": int((fin & (qst < 0)).sum()), "high": int((fin & (qst > QST_HI)).sum()),
                "undef": int((~fin).sum()),
                "qst_min": float(np.nanmin(qst)) if fin.any() else None,
                "qst_max": float(np.nanmax(qst)) if fin.any() else None})
    return out


def heat_curve(model, T_out):
    lnps = float(water.ln_p_sat(torch.tensor([T_out], dtype=torch.float64)))
    x = np.logspace(-3, math.log10(0.95), 200)
    s = torch.as_tensor(np.log(x) + lnps)
    T = torch.full_like(s, T_out)
    with torch.no_grad():
        q = model(s, T).numpy()
    qst = thermo.isosteric_heat(model, s, T).detach().numpy() / 1e3
    return {"x": x.tolist(), "q": q.tolist(), "qst_kJ": [float(v) if np.isfinite(v) else None for v in qst]}


def main():
    torch.set_num_threads(1)
    k, K = (0, 1)
    if "--shard" in sys.argv:
        k, K = map(int, sys.argv[sys.argv.index("--shard") + 1].split("/"))
    best = json.loads((ROOT / "results/dev_best_configs.json").read_text())
    recs, precs = records(), psign_records()
    mats = [m for i, m in enumerate(load_materials("confirmatory")) if i % K == k]
    log = ROOT / ("results/heat_window_real.jsonl" if K == 1 else f"results/heat_window_real.shard{k}.jsonl")
    done = set()
    if log.exists():
        done = {(r["cell"], r["material"], r["task"]) for r in map(json.loads, log.read_text().splitlines()) if r}
    for m in mats:
        tasks = study.tasks(m)
        for cell in CELLS:
            cfg = study.Config(**best["P" if cell == "P-sign" else cell]["config"])
            for task in TASKS:
                if (cell, m.name, task) in done:
                    continue
                train_T, T_out = tasks[task]
                t0 = time.time()
                if cell == "P-sign":
                    rec0 = precs[(m.name, task)]
                    seed = int(rec0["best_seed"])
                    model = fit_psign(cfg, m, train_T, seeds=(seed,))[0][2]
                else:
                    rec0 = recs[(cell, m.name, task)]
                    assert asdict(cfg) == rec0["config"]
                    seed = int(rec0["best_seed"])
                    model = study.fit_cell(cell, cfg, m, train_T, seeds=(seed,))[0].model
                E = study.error_E(model, m, T_out)
                out = {"cell": cell, "material": m.name, "task": task, "T_out": float(T_out), "seed": seed,
                       "E_refit": E, "E_record": rec0["E"], "E_rel_diff": abs(E - rec0["E"]) / rec0["E"],
                       "window": window_heat(model, m, float(T_out)), "curve": heat_curve(model, float(T_out)),
                       "q_ref": float(m.q_ref)}
                out["seconds"] = round(time.time() - t0, 1)
                with log.open("a") as f:
                    f.write(json.dumps(out) + "\n")
                w = out["window"]
                print(cell, m.name, task, f"E {E:.4g} rel {out['E_rel_diff']:.1e}",
                      f"window {w['n_window']} neg {w['neg']} high {w['high']} undef {w['undef']}",
                      f"{out['seconds']}s", flush=True)


if __name__ == "__main__":
    main()
