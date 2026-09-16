#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
OUT=replication/r4/output
mkdir -p "$OUT/logs"
SOURCE="${1:-$(git rev-parse HEAD)}"
python replication/r4/run.py --mode tests --source-commit "$SOURCE" 2>&1 | tee "$OUT/logs/tests.txt"
python replication/r4/run.py --mode reference --source-commit "$SOURCE" 2>&1 | tee "$OUT/logs/reference.txt"
python replication/r4/run.py --mode neural --seeds 101 --source-commit "$SOURCE" 2>&1 | tee "$OUT/logs/pilot.txt"
python replication/r4/safeguard.py 2>&1 | tee "$OUT/logs/ndu_neural.txt"
python replication/r4/coupled_resource.py 2>&1 | tee "$OUT/logs/resources.txt"
python replication/r4/analysis.py 2>&1 | tee "$OUT/logs/analysis.txt"
python replication/r4/graph_tests.py 2>&1 | tee "$OUT/logs/graphs.txt"
python replication/r4/replay.py 2>&1 | tee "$OUT/logs/replay.txt"
python replication/r4/make_tables.py
python replication/r4/validate.py --source-commit "$SOURCE" 2>&1 | tee "$OUT/logs/validation.txt"
