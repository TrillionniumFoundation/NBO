#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p build results99
python3 code99/exact_decision.py
python3 code99/independent_decision.py
python3 code99/test99.py > results99/test99.log 2>&1
python3 -m compileall -q code99
for doc in ECTA supp appendix response99; do
  pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build "$doc.tex" > "build/$doc.first.log" 2>&1
done
for doc in ECTA supp appendix; do bibtex "build/$doc" > "build/$doc.bib.log" 2>&1; done
for pass in 1 2 3; do
 for doc in ECTA supp appendix response99; do
  pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build "$doc.tex" > "build/$doc.pass$pass.log" 2>&1
 done
done
python3 code99/check99.py
