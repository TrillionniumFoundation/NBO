#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
mkdir -p revisions/2026-09-26-r50/logs
python revisions/2026-09-26-r50/replication/run_evaluation.py 2>&1 | tee revisions/2026-09-26-r50/logs/reproduction.log
bash R50_BUILD.sh
