#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
R=revisions/2026-09-26-r47
mkdir -p "$R/build" "$R/results" "$R/proofs"
export PYTHONINTMAXSTRDIGITS=0
export PYTHONPATH="${PWD}/revisions/2026-09-25-r44/replication:${PYTHONPATH:-}"
if [[ "${1:-}" != "--documents-only" ]]; then
 python3 "$R/replication/replay_r46.py" > "$R/build/r46_replay.log"
 python3 "$R/replication/witness_audit.py" > "$R/build/witness_construct.log"
 python3 "$R/replication/verify_witness.py" > "$R/build/witness_check.log"
 python3 "$R/replication/test_witness.py" > "$R/build/witness_mutations.log"
fi
# Regenerate the preserved R45 table sources; their original hashes must match.
mkdir -p revisions/2026-09-25-r45/results revisions/2026-09-25-r45/paper/generated
python3 revisions/2026-09-25-r45/replication/check_search_modulus.py > "$R/build/old_modulus.log"
python3 revisions/2026-09-25-r45/replication/check_quantized_repair.py > "$R/build/old_quantized.log"
python3 revisions/2026-09-25-r45/replication/tabulate.py > "$R/build/old_tables.log"
python3 revisions/2026-09-25-r45/replication/tabulate_extra.py >> "$R/build/old_tables.log"
cp revisions/2026-09-25-r45/paper/generated/*.tex "$R/paper/generated/"
python3 "$R/replication/tabulate_r47.py" > "$R/build/tables.log"
# Regenerate figures from immutable archived results; no optimizer is run.
python3 revisions/2026-09-25-r45/replication/plot.py
cp revisions/2026-09-25-r45/paper/generated/*.pdf "$R/paper/generated/"
python3 "$R/replication/plot_r47.py"
for n in ECTA_R45 SUPP_R45 RESPONSE_R45 HISTORY_R45 ECTA_R47 SUPP_R47 RESPONSE_R47 COMPUTATION_R47 HISTORY_R47; do
 latexmk -pdf -interaction=nonstopmode -halt-on-error "$n.tex" > "$R/build/$n.build.log" 2>&1
 cp "$n.log" "$R/build/$n.latex.log"
 if grep -qE 'There were undefined references|Citation .* undefined|LaTeX Error|Emergency stop' "$n.log"; then
  printf 'Unresolved LaTeX diagnostics in %s\n' "$n" >&2;exit 1
 fi
done
python3 - <<'PY'
from pathlib import Path
import json,sys,platform,subprocess,importlib.metadata
r=Path('revisions/2026-09-26-r47')
packages={}
for p in ['numpy','scipy','matplotlib','pypdf']:
 try:packages[p]=importlib.metadata.version(p)
 except importlib.metadata.PackageNotFoundError:packages[p]='not installed'
env=dict(python=sys.version,platform=platform.platform(),packages=packages,tex=subprocess.check_output(['pdflatex','--version'],text=True).splitlines()[0])
(r/'build/environment.json').write_text(json.dumps(env,indent=2)+'\n')
PY
printf 'All nine current and preserved documents compiled.\n'
