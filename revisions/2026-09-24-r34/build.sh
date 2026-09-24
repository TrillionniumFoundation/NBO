#!/usr/bin/env bash
set -euo pipefail
R=revisions/2026-09-24-r34
mkdir -p "$R/build"
for stem in ECTA SUPP RESPONSE COMPUTATION HISTORY; do
  for pass in 1 2 3; do
    pdflatex -interaction=nonstopmode -halt-on-error "${stem}_R34.tex" > "$R/build/${stem}-${pass}.txt"
  done
  cp "${stem}_R34.log" "$R/build/${stem}_R34.log"
done
python - <<'PY'
from pathlib import Path
import re
for name in ('ECTA','SUPP','RESPONSE','COMPUTATION'):
    t=Path(f'{name}_R34.log').read_text(errors='replace')
    for bad in ('Overfull','There were undefined references','undefined citations','LaTeX Error'):
        assert bad not in t,(name,bad)
print('All current documents compile without overflow or unresolved references.')
PY
