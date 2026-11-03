"""Confirmatory run (PREREG_P3A.md sections 4 to 6). Refuses to run unless the frozen
pre-registration and the frozen development-set configurations are byte-identical to the
versions whose SHA-256 is written below at the freeze.

Fits every cell on every confirmatory material for the tasks E-high, E-low and I-mid from
5 seeds; the reported fit is the seed with the lowest training loss (5.3). For it, the
held-out error E (6.1) and the violation counts on the dense grid G (6.2) are recorded,
with every seed's E for the seed spread. Resumable: results/confirmatory_runs.jsonl.

  python scripts/run_confirmatory.py              confirmatory set (needs the freeze)
  python scripts/run_confirmatory.py --dev        development set, for testing the pipeline;
                                                  writes results/devcheck_runs.jsonl
"""
import hashlib
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from p3a import study  # noqa: E402
from run_dev import load_materials  # noqa: E402

# written at the freeze (commit "FREEZE PREREG_P3A"); empty means not frozen
PREREG_SHA256 = ""
DEV_CONFIGS_SHA256 = ""
SEEDS = (0, 1, 2, 3, 4)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_freeze():
    if not PREREG_SHA256 or not DEV_CONFIGS_SHA256:
        sys.exit("REFUSED: the pre-registration is not frozen (no hash written in this script).")
    if sha256(ROOT / "PREREG_P3A.md") != PREREG_SHA256:
        sys.exit("REFUSED: PREREG_P3A.md differs from the frozen version.")
    if sha256(ROOT / "results/dev_best_configs.json") != DEV_CONFIGS_SHA256:
        sys.exit("REFUSED: results/dev_best_configs.json differs from the frozen version.")


def main():
    dev = "--dev" in sys.argv
    if not dev:
        check_freeze()
    best = json.loads((ROOT / "results/dev_best_configs.json").read_text())
    mats = load_materials("development" if dev else "confirmatory")
    log = ROOT / ("results/devcheck_runs.jsonl" if dev else "results/confirmatory_runs.jsonl")
    done = set()
    if log.exists():
        for line in log.read_text().splitlines():
            r = json.loads(line)
            done.add((r["cell"], r["material"], r["task"]))
    for m in mats:
        for cell in study.CELLS:
            if cell == "P-K" and len(m.temps) < 5:
                continue  # needs at least 4 training temperatures (PREREG section 4)
            cfg = study.Config(**best[cell]["config"])
            for task, (train_T, T_out) in study.tasks(m).items():
                if (cell, m.name, task) in done:
                    continue
                t0 = time.time()
                rec = {"cell": cell, "material": m.name, "task": task, "T_out": float(T_out),
                       "train_T": [float(t) for t in train_T], "config": asdict(cfg)}
                try:
                    res = study.fit_cell(cell, cfg, m, train_T, seeds=SEEDS)
                    rec.update({
                        "E": study.error_E(res[0].model, m, T_out),
                        "best_seed": res[0].seed,
                        "train_loss": res[0].train_loss,
                        "E_all_seeds": {str(r.seed): study.error_E(r.model, m, T_out) for r in res},
                        "violations": study.violation_counts(res[0].model, m),
                        "error": None})
                except Exception as e:  # an error is a failure, never dropped
                    rec.update({"E": float("inf"), "error": repr(e)})
                rec["seconds"] = round(time.time() - t0, 1)
                with log.open("a") as f:
                    f.write(json.dumps(rec) + "\n")
                print(cell, m.name, task, f"E={rec['E']:.4g}", f"{rec['seconds']}s", flush=True)


if __name__ == "__main__":
    main()
