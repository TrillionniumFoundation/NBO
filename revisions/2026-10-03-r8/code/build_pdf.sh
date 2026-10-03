#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
b=revisions/2026-10-03-r8/build
mkdir -p "$b" revisions/2026-10-03-r8/logs
pdflatex -interaction=nonstopmode -halt-on-error -output-directory="$b" ECTA.tex > "$b/main_pass1.stdout" 2>&1
bibtex_cmd=$(command -v bibtex || command -v bibtex.original || command -v bibtex8)
"$bibtex_cmd" "$b/ECTA" > "$b/bibtex.stdout" 2>&1
pdflatex -interaction=nonstopmode -halt-on-error -output-directory="$b" ECTA.tex > "$b/main_pass2.stdout" 2>&1
pdflatex -interaction=nonstopmode -halt-on-error -output-directory="$b" ECTA.tex > "$b/main_pass3.stdout" 2>&1
for tex in supp.tex revisions/2026-10-03-r8/response.tex; do
  name=$(basename "$tex" .tex)
  for pass in 1 2 3; do
    pdflatex -interaction=nonstopmode -halt-on-error -output-directory="$b" "$tex" > "$b/${name}_pass${pass}.stdout" 2>&1
  done
done
python - <<'PY'
import json,re,hashlib
from pathlib import Path
r=Path('revisions/2026-10-03-r8');b=r/'build';result={}
for name in ['ECTA','supp','response']:
 s=(b/f'{name}.log').read_text(errors='replace')
 result[name]={'pdf_sha256':hashlib.sha256((b/f'{name}.pdf').read_bytes()).hexdigest(),
  'pages':int(re.findall(r'Output written on .*?\((\d+) pages?',s,re.S)[-1]),
  'undefined':bool(re.search(r'undefined references|Citation .* undefined|Reference .* undefined|Undefined control sequence',s)),
  'overfull_hbox_pt':[float(v) for v in re.findall(r'Overfull \\hbox \(([\d.]+)pt',s)]}
 assert not result[name]['undefined'],(name,'unresolved references')
(r/'results/COMPILATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
PY
