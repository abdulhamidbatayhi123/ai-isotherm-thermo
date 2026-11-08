"""Descriptive analyses fixed in PREREG_P3A.md sections 3.3, 6.3b and 6.4 (no hypothesis).

  python scripts/sensitivity.py perturb            writes the digitisation-perturbed datasets
                                                   data/raw/dataset/variants/perturb_s1, perturb_s2
  python scripts/run_confirmatory.py --sensitivity NAME    fits the changed materials (needs the freeze)
  python scripts/sensitivity.py verdicts NAME      H1 verdicts on the variant: the main confirmatory
                                                   runs of its unchanged materials plus the
                                                   sensitivity runs of the changed ones
  python scripts/sensitivity.py aq-spread          A(q) spread of included against excluded materials
                                                   (selection check, review E1); no model
  python scripts/sensitivity.py mof801             MOF-801 heat check (section 6.3b), descriptive

Outputs: results/sensitivity_<name>.json.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from p3a import study, thermo, water  # noqa: E402
from p3a.constants import R  # noqa: E402

PERTURB_RH = 0.027          # the benchmark's largest systematic offset, in p/psat
PERTURB_SEEDS = (1, 2)
NUMERIC_SOURCES = ("mgsu102_2025_natcommun",)  # numeric source data: not perturbed
H1_CELLS = ("P", "F-hard", "V-pen", "A-hard", "F-none", "C1")
M_W = 18.01528e-3           # kg/mol
MOF801_WINDOW_GG = (0.19, 0.20)
MOF801_DSC_KJ = 53.3


def psat(T):
    return water.p_sat(torch.as_tensor(np.asarray(T, float))).numpy()


def perturb():
    """Each digitised isotherm (material, source, T) shifted in p/psat by a random sign times
    PERTURB_RH; points pushed to p/psat <= 0 are dropped; the 0.90 cut is reapplied."""
    d = pd.read_csv(ROOT / "data/raw/dataset/isotherms.csv")
    for seed in PERTURB_SEEDS:
        rng = np.random.default_rng(seed)
        parts = []
        for (mat, src, T), g in d.groupby(["material", "source", "T_K"], sort=True):
            g = g.copy()
            if src not in NUMERIC_SOURCES and g["set"].iloc[0] == "confirmatory":
                rh = g.p_Pa / psat(g.T_K) + rng.choice([-1.0, 1.0]) * PERTURB_RH
                g["p_Pa"] = rh * psat(g.T_K)
                g["rh"] = rh
                g = g[(g.rh > 0) & (g.rh <= 0.90)]
            parts.append(g)
        out = ROOT / f"data/raw/dataset/variants/perturb_s{seed}"
        out.mkdir(parents=True, exist_ok=True)
        pd.concat(parts).to_csv(out / "isotherms.csv", index=False)
        print("written", out)


def verdicts(name):
    import analyse
    from run_dev import load_materials
    main_runs = [json.loads(x) for x in (ROOT / "results/confirmatory_runs.jsonl").read_text().splitlines()]
    sens_runs = [json.loads(x) for x in (ROOT / f"results/sensitivity_{name}_runs.jsonl").read_text().splitlines()]
    members = {m.name for m in load_materials("confirmatory", ROOT / f"data/raw/dataset/variants/{name}/isotherms.csv")}
    changed = {r["material"] for r in sens_runs}
    rows = [r for r in main_runs if r["material"] in members - changed and r["cell"] in H1_CELLS
            and r["task"] in analyse.E_TASKS] + sens_runs
    f = ROOT / f"results/sensitivity_{name}_combined.jsonl"
    f.write_text("".join(json.dumps(r) + "\n" for r in rows))
    sys.argv = ["analyse.py", str(f)]
    out = analyse.main()
    summary = {"variant": name, "n_materials": len(members), "changed_or_added": sorted(changed),
               "H1": {h: {"class": r["class"], "R": r["R"], "R_ci95": r["R_ci95"]} for h, r in out["H1"].items()}}
    (ROOT / f"results/sensitivity_{name}.json").write_text(json.dumps(summary, indent=2))


def a_of_q(g, q_grid):
    """A = RT ln(psat/p) (kJ/mol) interpolated at q_grid along one isotherm (points sorted
    by p, uptake made non-decreasing by a running maximum only for the interpolation)."""
    g = g.sort_values("p_Pa")
    A = R * g.T_K.to_numpy() * np.log(psat(g.T_K) / g.p_Pa.to_numpy()) / 1e3
    q = np.maximum.accumulate(g.q_molkg.to_numpy())
    ok = (q_grid >= q.min()) & (q_grid <= q.max())
    out = np.full_like(q_grid, np.nan)
    if ok.any() and len(np.unique(q)) > 1:
        qu, idx = np.unique(q, return_index=True)
        out[ok] = np.interp(q_grid[ok], qu, A[idx])
    return out


def aq_spread():
    """Per material: the mean over loadings 0.2 to 0.8 q_ref of the standard deviation of
    A(q) across temperatures (kJ/mol), from every visible point with 0 < p/psat <= 0.90;
    for included and excluded materials (selection check, PREREG 6.4)."""
    import build_dataset as bd
    cols = ["material", "class", "set", "source", "T_K", "p_Pa", "q_molkg", "provenance"]
    raw = pd.DataFrame([r for f in bd.SOURCES for r in f()], columns=cols)
    raw = raw[(raw.p_Pa > 0) & (raw.p_Pa / psat(raw.T_K) <= 0.90)]
    log = pd.read_csv(ROOT / "data/inclusion_log.csv").set_index(["material", "source"])
    res = {}
    for (mat, src), g in raw.groupby(["material", "source"]):
        if g["set"].iloc[0] != "confirmatory":
            continue
        q_ref = g.q_molkg.max()
        q_grid = np.linspace(0.2, 0.8, 25) * q_ref
        A = np.array([a_of_q(h, q_grid) for _, h in g.groupby("T_K")])
        n_T = np.sum(np.isfinite(A), axis=0)
        sd = np.where(n_T >= 2, np.nanstd(np.where(np.isfinite(A), A, np.nan), axis=0, ddof=1), np.nan) \
            if A.shape[0] >= 2 else np.full(len(q_grid), np.nan)
        res[f"{mat} | {src}"] = {"decision": log.loc[(mat, src), "decision"],
                                 "n_temperatures": int(A.shape[0]),
                                 "A_spread_kJmol": float(np.nanmean(sd)) if np.isfinite(sd).any() else None}
    inc = [v["A_spread_kJmol"] for v in res.values() if v["decision"] == "include" and v["A_spread_kJmol"] is not None]
    exc = [v["A_spread_kJmol"] for v in res.values() if v["decision"] == "exclude" and v["A_spread_kJmol"] is not None]
    out = {"per_material": res, "median_included": float(np.median(inc)) if inc else None,
           "median_excluded": float(np.median(exc)) if exc else None, "n_included": len(inc), "n_excluded": len(exc)}
    (ROOT / "results/sensitivity_aq_spread.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({k: v for k, v in out.items() if k != "per_material"}, indent=2))


def mof801():
    """Descriptive heat check: each model fitted to all five MOF-801 (Kim 2018) temperatures
    (minpoints7 variant), Qst averaged at 303.15 K (30 C, the temperature of the DSC value) over model loadings 0.19 to 0.20 g/g,
    against the DSC integral value 53.3 kJ/mol (Kim et al. 2016)."""
    from run_dev import load_materials
    mats = [m for m in load_materials("confirmatory", ROOT / "data/raw/dataset/variants/minpoints7/isotherms.csv")
            if m.name.startswith("MOF-801")]
    if not mats:
        sys.exit("MOF-801 not in the minpoints7 variant")
    m = mats[0]
    best = json.loads((ROOT / "results/dev_best_configs.json").read_text())
    lo, hi = (w / M_W for w in MOF801_WINDOW_GG)  # mol/kg
    T = 303.15
    s = torch.linspace(math.log(10.0), float(water.ln_p_sat(torch.tensor([T]))) + math.log(0.9), 2000)
    Tt = torch.full_like(s, T)
    out = {"material": m.name, "window_molkg": [lo, hi], "dsc_kJmol": MOF801_DSC_KJ, "cells": {}}
    for cell in ("P", "V-pen", "A-hard", "F-none", "C1"):
        cfg = study.Config(**best[cell]["config"])
        res = study.fit_cell(cell, cfg, m, list(m.temps))
        with torch.no_grad():
            q = res[0].model(s, Tt)
        keep = (q >= lo) & (q <= hi)
        qst = thermo.isosteric_heat(res[0].model, s[keep], Tt[keep]) / 1e3 if keep.any() else torch.tensor([])
        val = float(qst.mean()) if qst.numel() and torch.all(torch.isfinite(qst)) else None
        out["cells"][cell] = {"qst_kJmol": val, "n_states": int(keep.sum()), "train_loss": res[0].train_loss}
        print(cell, val)
    (ROOT / "results/sensitivity_mof801.json").write_text(json.dumps(out, indent=2))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "perturb":
        return perturb()
    if cmd == "verdicts":
        return verdicts(sys.argv[2])
    if cmd == "aq-spread":
        return aq_spread()
    if cmd == "mof801":
        return mof801()
    sys.exit(__doc__)


if __name__ == "__main__":
    main()
