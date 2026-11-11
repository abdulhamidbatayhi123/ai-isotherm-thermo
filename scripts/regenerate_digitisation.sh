#!/usr/bin/env bash
# Regenerate every digitised source, the dataset, the colour gate, the measured error model
# and the raster benchmark with the current digitiser. Log: logs/regenerate_digitisation.log
set -euo pipefail
cd "$(dirname "$0")/.."
P="${P3A_PY:-python}"   # set P3A_PY to the interpreter of the environment in requirements-lock.txt
export PYTHONIOENCODING=utf-8
echo "== $(date -u +%FT%TZ) start"
"$P" scripts/digitise_sources.py
"$P" -W ignore scripts/build_dataset.py
"$P" scripts/check_colour_separability.py
"$P" scripts/digitisation_error.py
"$P" scripts/raster_benchmark.py > logs/raster_benchmark.log
tail -1 logs/raster_benchmark.log
echo "== $(date -u +%FT%TZ) done"
