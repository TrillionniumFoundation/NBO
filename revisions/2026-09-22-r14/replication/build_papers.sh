#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
BUILD=revisions/2026-09-22-r14/build_logs/latex
mkdir -p "$BUILD"
for name in ECTA_R14 SUPP_R14; do
  for pass in 1 2 3; do
    pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory="$BUILD" "$name.tex" > "revisions/2026-09-22-r14/build_logs/${name}_pass${pass}.txt" 2>&1
  done
  if grep -E 'undefined references|undefined citations|Overfull \\hbox|Overfull \\vbox' "$BUILD/$name.log"; then
    echo "Unresolved document warning: $name" >&2; exit 1
  fi
  cp "$BUILD/$name.pdf" "$name.pdf"
done
