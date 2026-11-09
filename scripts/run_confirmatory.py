"""Confirmatory run (PREREG_P3A.md sections 4 to 6). Refuses to run unless every frozen file
(the pre-registration, the tuned configurations, the power and synthetic-world results, the
dataset and its inclusion log, every piece of code that digitises, fits or scores, this
script, and the environment lock) is identical to the version hashed at the freeze, and the
installed package versions match the lock.

Fits every cell on every confirmatory material for the tasks E-high, E-low and I-mid from
5 seeds; the reported fit is the seed with the lowest training loss (5.3). For it, the
held-out error E (6.1) and the violation counts on the dense grid G (6.2) are recorded,
with every seed's E for the seed spread. Resumable: results/confirmatory_runs.jsonl.

  python scripts/run_confirmatory.py              confirmatory set (needs the freeze)
  python scripts/run_confirmatory.py --dev        development set, for testing the pipeline;
                                                  writes results/devcheck_runs.jsonl
  python scripts/run_confirmatory.py --sensitivity NAME
                                                  descriptive: the H1 cells on the materials of
                                                  data/raw/dataset/variants/NAME whose data differ
                                                  from the main dataset (needs the freeze)
  ... [--shard k/K]                                 any of the runs split over K workers by material
                                                  (logs <name>.shard<k>.jsonl; analyse.py reads them all)
  python scripts/run_confirmatory.py --prepare-freeze
                                                  converts the frozen files to LF without BOM,
                                                  writes .gitattributes (-text) and the manifest,
                                                  and prints the hash to put in MANIFEST_SHA256
"""
import hashlib
import importlib.metadata
import json
import re
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

# Files frozen with the pre-registration (PREREG section 10). A post-freeze edit to any of
# them stops the run. data/raw/dataset/isotherms.csv is local only (third-party data), but its
# hash is public in the manifest.
FROZEN = [
    "PREREG_P3A.md", "requirements-lock.txt", ".gitattributes",
    # tuned configurations, power, synthetic worlds (all computed before the freeze)
    "results/dev_best_configs.json", "results/mde.json", "results/worlds_check.json",
    "results/verdicts_worlds_KS0.json", "results/verdicts_worlds_DA.json",
    "results/verdicts_worlds_FW.json", "results/verdicts_worlds_FLAT.json",
    "results/verdicts_worlds_SUB.json",  # review T5-2
    # the fits behind those results, so every pre-freeze number can be re-derived (review T5)
    "results/dev_runs_a.jsonl", "results/dev_runs_b.jsonl", "results/dev_runs_c.jsonl",
    "results/dev_runs_d.jsonl", "results/dev_runs_e.jsonl", "results/dev_runs_lam_vpen.jsonl",
    "results/dev_runs_lam_apen.jsonl", "results/dev_runs_lam_fpen.jsonl",
    "results/devcheck_runs.jsonl", "results/devcheck_h2.jsonl", "results/verdicts_devcheck_runs.json",
    "results/worlds_KS0.jsonl", "results/worlds_DA.jsonl", "results/worlds_FW.jsonl",
    "results/worlds_FLAT.jsonl", "results/worlds_SUB.jsonl",
    # data
    "data/raw/dataset/isotherms.csv", "data/inclusion_log.csv", "data/dataset_summary.json",
    "data/digitisation_gate_log.csv", "logs/digitisation_validation.json",
    "results/sensitivity_aq_spread.json",
    "data/variants/rule5_v1_inclusion_log.csv", "data/variants/rule5_v2_inclusion_log.csv",
    "data/variants/rule5_none_inclusion_log.csv", "data/variants/minpoints7_inclusion_log.csv",
    "data/variants/co2cl2_s8_inclusion_log.csv",
    "data/raw/dataset/variants/perturb_s1/isotherms.csv", "data/raw/dataset/variants/perturb_s2/isotherms.csv",
    "data/raw/dataset/variants/rule5_v1/isotherms.csv", "data/raw/dataset/variants/rule5_v2/isotherms.csv",
    "data/raw/dataset/variants/rule5_none/isotherms.csv", "data/raw/dataset/variants/minpoints7/isotherms.csv",
    "data/raw/dataset/variants/co2cl2_s8/isotherms.csv",
    "data/digitised_provenance/cho2020_kmf1_20C_30C_coincidence.csv",
    # code that digitises, builds, fits or scores
    "src/p3a/__init__.py", "src/p3a/models.py", "src/p3a/study.py", "src/p3a/thermo.py",
    "src/p3a/fit.py", "src/p3a/_num.py", "src/p3a/water.py", "src/p3a/synthetic.py",
    "src/p3a/constants.py", "src/p3a/digitise.py",
    "scripts/digitise_sources.py", "scripts/build_dataset.py", "scripts/run_dev.py",
    "scripts/run_confirmatory.py", "scripts/run_synthetic_h2.py", "scripts/analyse.py",
    "scripts/mde.py", "scripts/verdict_worlds.py", "scripts/sensitivity.py",
    "scripts/check_colour_separability.py", "scripts/digitisation_validation.py",
    "scripts/digitisation_error.py", "scripts/raster_benchmark.py",
    "scripts/independent/cs_scorer.py",  # the independent scorer named in 7.2 and 7.4
    "tests/test_analysis.py",
]
# SHA-256 of FREEZE_MANIFEST.json, written at the freeze; empty means not frozen
MANIFEST_SHA256 = ""
SEEDS = (0, 1, 2, 3, 4)
LOCKED = ("torch", "numpy", "scipy", "pandas", "pymupdf", "pillow")
_SELF_LINE = re.compile(rb'^MANIFEST_SHA256 = ".*"$', re.M)


def normalised_bytes(path):
    """File bytes with a UTF-8 BOM removed and CRLF normalised to LF, so that a Windows
    checkout hashes like the committed blob (PAPER_WORKFLOW_LESSONS section 10). This script
    is hashed with its own MANIFEST_SHA256 value blanked, so writing the value does not
    change its hash."""
    b = Path(path).read_bytes()
    if b.startswith(b"\xef\xbb\xbf"):
        b = b[3:]
    b = b.replace(b"\r\n", b"\n")
    if Path(path).resolve() == Path(__file__).resolve():
        b = _SELF_LINE.sub(b'MANIFEST_SHA256 = ""', b)
    return b


def sha256_lf(path):
    return hashlib.sha256(normalised_bytes(path)).hexdigest()


def environment():
    return {"python": sys.version.split()[0],
            **{p: importlib.metadata.version(p) for p in LOCKED}}


def write_lock():
    env = environment()
    (ROOT / "requirements-lock.txt").write_text(
        "# Exact versions used for the frozen runs (checked by scripts/run_confirmatory.py)\n"
        + f"# python {env.pop('python')}\n" + "".join(f"{k}=={v}\n" for k, v in env.items()), newline="\n")


def prepare_freeze():
    """Once, at the freeze: lock, LF without BOM, .gitattributes, manifest."""
    write_lock()
    attrs = ["# Frozen with PREREG_P3A.md: stored and checked out byte for byte (no EOL conversion)"]
    attrs += [f"{f} -text" for f in FROZEN if f != ".gitattributes" and not f.startswith("data/raw/")]
    (ROOT / ".gitattributes").write_text("\n".join(attrs) + "\n", newline="\n")
    for f in FROZEN:
        path = ROOT / f
        raw = path.read_bytes()
        norm = raw[3:] if raw.startswith(b"\xef\xbb\xbf") else raw
        norm = norm.replace(b"\r\n", b"\n")
        if norm != raw:
            path.write_bytes(norm)
    return write_manifest()


def write_manifest():
    man = {"files": {f: sha256_lf(ROOT / f) for f in FROZEN}, "environment": environment()}
    (ROOT / "FREEZE_MANIFEST.json").write_text(json.dumps(man, indent=2, sort_keys=True) + "\n", newline="\n")
    return sha256_lf(ROOT / "FREEZE_MANIFEST.json")


def check_freeze():
    if not MANIFEST_SHA256:
        sys.exit("REFUSED: the pre-registration is not frozen (no manifest hash in this script).")
    if sha256_lf(ROOT / "FREEZE_MANIFEST.json") != MANIFEST_SHA256:
        sys.exit("REFUSED: FREEZE_MANIFEST.json differs from the frozen version.")
    man = json.loads((ROOT / "FREEZE_MANIFEST.json").read_text())
    if sorted(man["files"]) != sorted(FROZEN):
        sys.exit("REFUSED: the frozen file list changed.")
    for f, h in man["files"].items():
        if sha256_lf(ROOT / f) != h:
            sys.exit(f"REFUSED: {f} differs from the frozen version.")
    env = environment()
    if env != man["environment"]:
        sys.exit(f"REFUSED: environment {env} differs from the frozen {man['environment']}.")


def shard_arg():
    """--shard k/K -> (k, K); (0, 1) without it."""
    if "--shard" not in sys.argv:
        return 0, 1
    k, K = sys.argv[sys.argv.index("--shard") + 1].split("/")
    return int(k), int(K)


def main():
    if "--prepare-freeze" in sys.argv:
        h = prepare_freeze()
        print(f'FREEZE_MANIFEST.json written. Set MANIFEST_SHA256 = "{h}" in this script.')
        return
    dev = "--dev" in sys.argv
    sens = sys.argv[sys.argv.index("--sensitivity") + 1] if "--sensitivity" in sys.argv else None
    if not dev:
        check_freeze()
    best = json.loads((ROOT / "results/dev_best_configs.json").read_text())
    mats = load_materials("development" if dev else "confirmatory")
    log = ROOT / ("results/devcheck_runs.jsonl" if dev else "results/confirmatory_runs.jsonl")
    cells, task_names = study.CELLS, None
    if sens:  # descriptive sensitivity analysis (PREREG 3.3, 6.4): H1 cells, E tasks, changed materials only
        main = {m.name: m for m in mats}
        mats = [m for m in load_materials("confirmatory", ROOT / f"data/raw/dataset/variants/{sens}/isotherms.csv")
                if m.name not in main or not (np.array_equal(m.T, main[m.name].T)
                                              and np.array_equal(m.s, main[m.name].s)
                                              and np.array_equal(m.q, main[m.name].q))]
        log = ROOT / f"results/sensitivity_{sens}_runs.jsonl"
        cells, task_names = ("P", "F-hard", "V-pen", "A-hard", "F-none", "C1"), ("E-high", "E-low")
    k, K = shard_arg()
    if K > 1:  # parallel workers: material i goes to shard i mod K, each with its own log
        mats = [m for i, m in enumerate(mats) if i % K == k]
        log = log.with_name(f"{log.stem}.shard{k}{log.suffix}")
    done = set()
    if log.exists():
        for line in log.read_text().splitlines():
            r = json.loads(line)
            done.add((r["cell"], r["material"], r["task"]))
    for m in mats:
        for cell in cells:
            if cell == "P-K" and len(m.temps) < 5:
                continue  # needs at least 4 training temperatures (PREREG section 4)
            cfg = study.Config(**best[cell]["config"])
            for task, (train_T, T_out) in study.tasks(m).items():
                if (cell, m.name, task) in done or (task_names and task not in task_names):
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
