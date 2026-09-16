#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
mkdir -p replication/r6/logs
for name in unit_tests bank_comparison transport kernel_certificate mechanism structural_qp; do
  python "replication/r6/${name}.py" 2>&1 | tee "replication/r6/logs/${name}.log"
done
python replication/r6/render_tables.py
python replication/r6/validate.py --source-commit "${1:?source commit required}" \
  --base-commit 0d0e79a52e540bd0647801ce316f051d667c6797 2>&1 | tee replication/r6/logs/validation.log
