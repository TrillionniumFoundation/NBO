#!/bin/sh
# Rebuild this revision. Never copy an earlier PDF into the current build path.
set -eu
cd "$(dirname "$0")/.."
python3 materialize110.py
mkdir -p build evidence110
if command -v bibtex >/dev/null 2>&1; then BIBTEX=bibtex
elif command -v bibtex.original >/dev/null 2>&1; then BIBTEX=bibtex.original
else echo 'BibTeX executable required' >&2; exit 1; fi
for doc in ECTA supp appendix RESPONSE_TO_REFEREE; do
 pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build "$doc.tex" >"build/$doc.first.log" 2>&1
done
for doc in ECTA supp appendix; do "$BIBTEX" "build/$doc" >"build/$doc.bib.log" 2>&1; done
for pass in 1 2 3; do
 for doc in ECTA supp appendix RESPONSE_TO_REFEREE; do
  pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build "$doc.tex" >"build/$doc.pass$pass.log" 2>&1
 done
done
python3 code110/verify110.py "$@"
