#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
REV=revisions/2026-09-22-r12
mkdir -p "$REV/build_logs"
for stem in ECTA_R12 SUPP_R12; do
  for pass in 1 2 3; do
    pdflatex -interaction=nonstopmode -halt-on-error "$stem.tex" > "$REV/build_logs/${stem}_pass${pass}.txt" 2>&1
  done
  cp "$stem.log" "$REV/build_logs/$stem.log"
  cp "$stem.aux" "$REV/build_logs/$stem.aux"
  pdfinfo "$stem.pdf" > "$REV/build_logs/${stem}_pdfinfo.txt"
  pdftotext "$stem.pdf" "$REV/build_logs/${stem}_text.txt"
done
