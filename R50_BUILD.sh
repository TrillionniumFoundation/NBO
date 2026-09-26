#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
R=revisions/2026-09-26-r50
mkdir -p "$R/logs"
python "$R/replication/prepare_publication.py"
python "$R/replication/write_response.py"
python "$R/replication/verify_all.py" | tee "$R/logs/publication-replay.log"
python "$R/replication/test_contracts.py" | tee "$R/logs/contract-tests.json"
python - <<'PY'
import sys
sys.path.insert(0,'revisions/2026-09-26-r50/replication')
from run_evaluation import cross_language
cross_language()
PY
python "$R/replication/tables.py" > "$R/logs/table-generation.log"
python "$R/replication/diagnostics.py"
for name in R48_RECONSTRUCTED_R50 ECTA_R50 SUPP_R50 RESPONSE_R50; do
  rm -f "$name.aux" "$name.out" "$name.brf"
  for pass in 1 2 3 4; do
    pdflatex -interaction=nonstopmode -halt-on-error "$name.tex" > "$R/logs/$name-pass$pass.txt" 2>&1
  done
  cp "$name.log" "$R/logs/$name.log"
done
python "$R/replication/manifest.py" | tee "$R/logs/publication-summary.json"
printf '%s\n' 'R50 arithmetic replay and all four PDF builds completed.'
