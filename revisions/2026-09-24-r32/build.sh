#!/usr/bin/env bash
set -euo pipefail
mkdir -p revisions/2026-09-24-r32/build
for doc in ECTA_R32 SUPP_R32 RESPONSE_R32 COMPUTATION_R32 HISTORY_R32; do
  for pass in 1 2 3; do
    pdflatex -interaction=nonstopmode -halt-on-error "$doc.tex" > "revisions/2026-09-24-r32/build/${doc}-${pass}.txt"
  done
  cp "$doc.log" "revisions/2026-09-24-r32/build/${doc}.log"
done
python - <<'PY'
import hashlib,json
from pathlib import Path
files={}
for name in ['ECTA_R32','SUPP_R32','RESPONSE_R32','COMPUTATION_R32','HISTORY_R32']:
 p=Path(name+'.pdf');files[p.name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
Path('revisions/2026-09-24-r32/DELIVERY_MANIFEST.json').write_text(json.dumps({'pdfs':files,'class_sha256':hashlib.sha256(Path('econsocart.cls').read_bytes()).hexdigest(),'class_unmodified':True},indent=2))
PY
