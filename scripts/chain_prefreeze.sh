#!/usr/bin/env bash
# Pre-freeze chain (PREREG_P3A.md sections 5.4, 7.3, 7.4): waits for the development tuning to
# finish, writes the tuned configurations, then runs in parallel the four synthetic worlds
# (4 workers), the development-set pipeline check of every cell, and the H2 pipeline check,
# and finally every analysis. Resumable: each step skips finished fits.
# Usage (Git Bash, repo root): bash scripts/chain_prefreeze.sh > logs/chain_prefreeze.log 2>&1
set -u
cd "$(dirname "$0")/.."
P="${P:-python}"   # set P to the interpreter of the environment in requirements-lock.txt
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1

count_tuning() {
  powershell -NoProfile -c "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { \$_.CommandLine -like '*run_dev.py*' -and \$_.CommandLine -notlike '*--summarise*' } | Measure-Object | Select-Object -ExpandProperty Count"
}
echo "$(date -Is) waiting for tuning"
while [ "$(count_tuning | tr -d '\r')" != "0" ]; do sleep 300; done
echo "$(date -Is) tuning finished"
"$P" scripts/run_dev.py --summarise || { echo "summarise failed"; exit 1; }

echo "$(date -Is) launching worlds, dev check, H2 check"
WORLD_WORKER=a "$P" scripts/verdict_worlds.py run KS0 DA --shard 0/2 > logs/worlds_a.log 2>&1 &
WORLD_WORKER=b "$P" scripts/verdict_worlds.py run KS0 DA --shard 1/2 > logs/worlds_b.log 2>&1 &
WORLD_WORKER=c "$P" scripts/verdict_worlds.py run FW FLAT --shard 0/2 > logs/worlds_c.log 2>&1 &
WORLD_WORKER=d "$P" scripts/verdict_worlds.py run FW FLAT --shard 1/2 > logs/worlds_d.log 2>&1 &
"$P" scripts/run_confirmatory.py --dev > logs/devcheck.log 2>&1 &
"$P" scripts/run_synthetic_h2.py --dev > logs/devcheck_h2.log 2>&1 &
wait
echo "$(date -Is) runs finished"

grep -l "Traceback" logs/worlds_?.log logs/devcheck.log logs/devcheck_h2.log && echo "TRACEBACKS FOUND"
"$P" scripts/verdict_worlds.py analyse > logs/worlds_analyse.log 2>&1; echo "worlds analyse exit $?"
"$P" scripts/analyse.py results/devcheck_runs.jsonl results/devcheck_h2.jsonl > logs/devcheck_analyse.log 2>&1; echo "dev analyse exit $?"
"$P" scripts/mde.py --spread-only > logs/mde_spread.log 2>&1; echo "mde spread exit $?"
echo "$(date -Is) chain done"
