#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
D=revisions/2026-09-29-r6
mkdir -p "$D/logs" "$D/artifacts"
BIB=bibtex
if ! command -v "$BIB" >/dev/null 2>&1; then BIB=bibtex.original; fi
pdflatex -interaction=nonstopmode -halt-on-error ECTA.tex > "$D/logs/main_build.log" 2>&1
"$BIB" ECTA >> "$D/logs/main_build.log" 2>&1
pdflatex -interaction=nonstopmode -halt-on-error ECTA.tex >> "$D/logs/main_build.log" 2>&1
pdflatex -interaction=nonstopmode -halt-on-error ECTA.tex >> "$D/logs/main_build.log" 2>&1
pdflatex -interaction=nonstopmode -halt-on-error supp.tex > "$D/logs/supp_build.log" 2>&1
pdflatex -interaction=nonstopmode -halt-on-error supp.tex >> "$D/logs/supp_build.log" 2>&1
if grep -Eq 'There were undefined (references|citations)|Citation .* undefined|Reference .* undefined' ECTA.log supp.log; then
  echo 'Unresolved final-pass references' >&2; exit 1
fi
cp ECTA.pdf "$D/artifacts/NBO_R6.pdf"
cp supp.pdf "$D/artifacts/NBO_R6_supplement.pdf"
