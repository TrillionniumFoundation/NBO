#!/usr/bin/env bash
set -euo pipefail
SOURCE_SHA="${1:?Supply the reachable commit identifying these source bytes}"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p replication/r5/output/logs build-r5
python replication/r5/contracts.py 2>&1 | tee replication/r5/output/logs/contracts.log
python replication/r5/economic_robustness.py 2>&1 | tee replication/r5/output/logs/economic_robustness.log
python replication/r5/resource_ablation.py 2>&1 | tee replication/r5/output/logs/resource_ablation.log
python replication/r5/persistent_game.py 2>&1 | tee replication/r5/output/logs/persistent_game.log
python replication/r5/validate.py --source-commit "$SOURCE_SHA" 2>&1 | tee replication/r5/output/logs/validation.log
python replication/r5/tables.py
python replication/r5/execution_summary.py
