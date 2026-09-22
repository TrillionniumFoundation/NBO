#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
logs=revisions/2026-09-22-r9/build_logs
mkdir -p "$logs"
for stem in ECTA_R9 SUPP_R9; do
  for pass in 1 2 3; do
    pdflatex -interaction=nonstopmode -halt-on-error "$stem.tex" > "$logs/$stem.pass$pass.txt" 2>&1
  done
  cp "$stem.log" "$logs/$stem.final.log"
  pdfinfo "$stem.pdf" > "$logs/$stem.pdfinfo.txt"
  pdftotext "$stem.pdf" "$logs/$stem.extracted.txt"
done
