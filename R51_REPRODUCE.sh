#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python revisions/2026-09-27-r51/replication/evaluate_controlled.py
bash R51_BUILD.sh
