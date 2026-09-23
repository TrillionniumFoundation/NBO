#!/usr/bin/env bash
# Invoke from a full Git checkout: bash revisions/2026-09-23-r24/BUILD_R24.sh
# This rebuilds publication from frozen evidence, not fresh scientific runs.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
rev=revisions/2026-09-23-r24
export PYTHONDONTWRITEBYTECODE=1
python "$rev/replication/assemble_publication.py"
python "$rev/replication/finalize_publication.py"
for target in ECTA_R24 SUPP_R24 RESPONSE_R24; do
  latexmk -pdf -interaction=nonstopmode -halt-on-error "$target.tex"
done
python "$rev/replication/publication_audit.py"
