#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
R=revisions/2026-09-27-r51
mkdir -p "$R/logs"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python "$R/replication/publication.py"
python "$R/replication/test_controlled.py" > "$R/logs/contracts.txt" 2>&1
python "$R/replication/verify.py" > "$R/logs/replay.txt" 2>&1
for doc in ECTA_R51 SUPP_R51 RESPONSE_R51; do
  for pass in 1 2 3; do
    pdflatex -interaction=nonstopmode -halt-on-error "$doc.tex" > "$R/logs/$doc-pass$pass.txt" 2>&1
  done
  cp "$doc.log" "$R/logs/$doc.log"
  if grep -Eq 'There were undefined references|There were undefined citations|multiply defined' "$doc.log"; then
    echo "Unresolved TeX references in $doc" >&2; exit 1
  fi
  pdfinfo "$doc.pdf" > "$R/logs/$doc-pdfinfo.txt"
done
python "$R/replication/assemble_pdfs.py"
python "$R/replication/manifest.py"
echo 'R51: frozen sources, 8 contracts, 54 full-cover proofs and all three PDFs verified.'
