"""Run the frozen `scripts/sensitivity.py verdicts NAME` on sharded run files, unchanged.

The frozen script reads results/confirmatory_runs.jsonl and results/sensitivity_<NAME>_runs.jsonl
as single files; the runs were launched in shards (<stem>.shard<k>.jsonl) after the freeze. This
wrapper concatenates the shards into those two file names, calls the frozen `verdicts(NAME)`,
and removes the two merged files again (they must not exist beforehand: scripts/analyse.py
reads a plain file and its shards together and would stop on the duplicates). A variant whose
data change no material has no sensitivity runs; it gets an empty run file, so its verdicts are
those of the main runs on its member set. Correction ledger X-3.

    python scripts/sens_verdicts_sharded.py NAME   -> results/sensitivity_NAME.json (+ _combined.jsonl)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))


def merge(stem):
    dst = ROOT / "results" / f"{stem}.jsonl"
    if dst.exists():
        sys.exit(f"REFUSED: {dst.name} exists; this wrapper only creates and removes its own merged files")
    shards = sorted((ROOT / "results").glob(f"{stem}.shard*.jsonl"))
    lines = [ln for f in shards for ln in f.read_text().splitlines() if ln.strip()]
    dst.write_text("".join(ln + "\n" for ln in lines))
    return dst, len(shards), len(lines)


def main(name):
    made = []
    try:
        for stem in ("confirmatory_runs", f"sensitivity_{name}_runs"):
            dst, k, n = merge(stem)
            made.append(dst)
            print(f"merged {k} shards of {stem}: {n} records")
        import sensitivity
        sensitivity.verdicts(name)
    finally:
        for f in made:
            f.unlink()


if __name__ == "__main__":
    main(sys.argv[1])
