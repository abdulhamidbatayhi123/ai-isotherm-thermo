"""Synthetic isosteric-heat benchmark, H2 (PREREG_P3A.md section 6.3a).

For every material, three truths with exact isosteric heats are built so that their shape
matches the material's measured isotherm at its middle temperature (fitted here by least
squares; only shape parameters are fitted, the thermodynamic parameters are fixed):
  KS  Kirchhoff-Sips, two sites: a Langmuir site (Q0 = 55 kJ/mol, dc = 0) and a cooperative
      Sips site (Q0 = 48 kJ/mol, dc = 40 J/mol/K, exponent g >= 1.5)  -> inside P's family
  DA  Dubinin-Astakhov q = W0 exp(-(A/E)^n), 1 <= n <= 6                -> inside A's family
  FG  Fowler-Guggenheim, Q0 = 45 kJ/mol, 0 < w < 3.9 R T_min           -> inside neither
Each truth is sampled at the material's own (p, T) points at every temperature, with
Gaussian noise of standard deviation SIGMA_REL x q_ref (the measured raster digitisation
error, rounded up; scripts/digitisation_error.py). The cells P, V-pen, A-hard and F-none
are fitted with the tuned configurations for the tasks E-high and E-low from 5 seeds, and
the RMS error of Qst (kJ/mol) at the held-out temperature is recorded (study.qst_error).

  python scripts/run_synthetic_h2.py          confirmatory materials (needs the freeze)
  python scripts/run_synthetic_h2.py --dev    development materials (pipeline check)
"""
import json
import math
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import torch
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from p3a import study, synthetic as syn  # noqa: E402
from p3a.constants import R  # noqa: E402
from run_confirmatory import SEEDS, check_freeze  # noqa: E402
from run_dev import load_materials  # noqa: E402

SIGMA_REL = 0.002
CELLS = ("P", "V-pen", "A-hard", "F-none")
FAMILIES = ("KS", "DA", "FG")
T_REF = 298.15


def make_truth(family, p):
    if family == "KS":
        a = syn.sips_kirchhoff(p[0], math.exp(p[1]), 55e3, 0.0, 1.0, T_REF)
        b = syn.sips_kirchhoff(p[2], math.exp(p[3]), 48e3, 40.0, 1.5 + p[4], T_REF)
        return lambda s, T: a(s, T) + b(s, T)
    if family == "DA":
        return syn.dubinin_astakhov(p[0], p[1], p[2])
    if family == "FG":
        return syn.fowler_guggenheim(p[0], math.exp(p[1]), 45e3, p[2], T_REF)
    raise ValueError(family)


def fit_truth(family, m: study.Material):
    """Shape parameters of a truth fitted to the middle-temperature isotherm (least squares
    on q / q_ref, bounded); returns the parameter vector."""
    Ts = sorted(m.temps)
    Tm = Ts[(len(Ts) - 1) // 2]
    sel = m.T == Tm
    s, T, q = (torch.as_tensor(m.s[sel]), torch.as_tensor(m.T[sel]), m.q[sel] / m.q_ref)
    qr = m.q_ref
    s_mid = float(np.median(m.s[sel]))
    if family == "KS":
        x0 = [0.2 * qr, -s_mid + 1.5, 0.8 * qr, -s_mid, 1.0]
        lb = [0.0, -30.0, 0.0, -30.0, 0.0]
        ub = [2 * qr, 10.0, 2 * qr, 10.0, 20.0]
    elif family == "DA":
        x0 = [qr, 3e3, 2.0]
        lb = [0.1 * qr, 100.0, 1.0]
        ub = [3 * qr, 2e4, 6.0]
    else:
        Tmin = float(min(Ts))
        x0 = [qr, -s_mid, 0.5 * 3.9 * R * Tmin]
        lb = [0.1 * qr, -30.0, 1.0]
        ub = [3 * qr, 10.0, 3.9 * R * Tmin]

    def resid(p):
        with torch.no_grad():
            return make_truth(family, p)(s, T).numpy() / qr - q

    r = least_squares(resid, x0, bounds=(lb, ub), max_nfev=4000)
    return list(map(float, r.x)), float(np.sqrt(np.mean(r.fun**2)))


def synthetic_material(m, family, params, seed):
    truth = make_truth(family, params)
    with torch.no_grad():
        q = truth(torch.as_tensor(m.s), torch.as_tensor(m.T)).numpy()
    rng = np.random.default_rng(seed)
    q_noisy = q + rng.normal(0.0, SIGMA_REL * m.q_ref, size=q.shape)
    return study.Material(f"{m.name} | synthetic {family}", m.T.copy(), m.s.copy(), q_noisy), truth


def main():
    dev = "--dev" in sys.argv
    if not dev:
        check_freeze()
    best = json.loads((ROOT / "results/dev_best_configs.json").read_text())
    mats = load_materials("development" if dev else "confirmatory")
    log = ROOT / ("results/devcheck_h2.jsonl" if dev else "results/synthetic_h2.jsonl")
    done = set()
    if log.exists():
        for line in log.read_text().splitlines():
            r = json.loads(line)
            done.add((r["cell"], r["material"], r["family"], r["task"]))
    for i, m in enumerate(mats):
        for j, family in enumerate(FAMILIES):
            params, fit_rmse = fit_truth(family, m)
            sm, truth = synthetic_material(m, family, params, seed=1000 * i + j)
            for cell in CELLS:
                cfg = study.Config(**best[cell]["config"])
                for task in ("E-high", "E-low"):
                    if (cell, m.name, family, task) in done:
                        continue
                    train_T, T_out = study.tasks(sm)[task]
                    t0 = time.time()
                    rec = {"cell": cell, "material": m.name, "family": family, "task": task,
                           "truth_params": params, "truth_fit_rmse_rel": fit_rmse, "config": asdict(cfg)}
                    try:
                        res = study.fit_cell(cell, cfg, sm, train_T, seeds=SEEDS)
                        rec.update({"qst_rmse_kJ": study.qst_error(res[0].model, truth, sm, T_out),
                                    "E": study.error_E(res[0].model, sm, T_out), "error": None})
                    except Exception as e:
                        rec.update({"qst_rmse_kJ": float("inf"), "E": float("inf"), "error": repr(e)})
                    rec["seconds"] = round(time.time() - t0, 1)
                    with log.open("a") as f:
                        f.write(json.dumps(rec) + "\n")
                    print(cell, m.name, family, task, f"Qst RMSE={rec['qst_rmse_kJ']:.3g} kJ/mol",
                          f"{rec['seconds']}s", flush=True)


if __name__ == "__main__":
    main()
