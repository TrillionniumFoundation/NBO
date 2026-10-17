#!/bin/sh
# Build only this revision; never relabel inherited PDFs as current.
set -eu
cd "$(dirname "$0")/.."
mkdir -p build evidence109
if command -v bibtex >/dev/null 2>&1; then BIBTEX=bibtex
elif command -v bibtex.original >/dev/null 2>&1; then BIBTEX=bibtex.original
else echo 'A working BibTeX executable is required' >&2; exit 1; fi
for doc in ECTA supp appendix RESPONSE_TO_REFEREE; do
 pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build "$doc.tex" > "build/$doc.first.log" 2>&1
done
for doc in ECTA supp appendix; do "$BIBTEX" "build/$doc" > "build/$doc.bib.log" 2>&1; done
for pass in 1 2 3; do
 for doc in ECTA supp appendix RESPONSE_TO_REFEREE; do
  pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build "$doc.tex" > "build/$doc.pass$pass.log" 2>&1
 done
done
python3 code109/verify_publication109.py
