#!/bin/sh
# A new attributable reproduction. Never overwrite the deposited measured run.
set -eu
cd "$(dirname "$0")/.."
ROOT=$(pwd)
OUTPUT=${1:?Supply a new, non-existing output directory}
if [ -e "$OUTPUT" ]; then echo 'Refusing to overwrite an existing attempt' >&2; exit 1; fi
mkdir -p "$OUTPUT"
OUTPUT=$(cd "$OUTPUT" && pwd)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export NBO_FROZEN108="$ROOT/frozen108"
export NBO_PROTOCOL108=29180a4ce4a6db7298e7458ecdfff3da08abb08f
export NBO_SOURCE110=5e1eae8a7017dd728b71440de3368062700fd747
python3 frozen108/code108/test108.py >"$OUTPUT/preflight108.log" 2>&1
python3 code110/test110.py >"$OUTPUT/preflight110.log" 2>&1
python3 frozen108/code108/campaign108.py all --output "$OUTPUT/r108-reproduction" >"$OUTPUT/campaign108.log" 2>&1
python3 frozen108/code108/audit108.py kernel --output "$OUTPUT/r108-reproduction" >"$OUTPUT/kernel108.log" 2>&1
python3 frozen108/code108/audit108.py records --output "$OUTPUT/r108-reproduction" >"$OUTPUT/audit108.log" 2>&1
python3 code110/gain_budget110.py all --acquired "$OUTPUT/r108-reproduction" --output "$OUTPUT/gain-budget" >"$OUTPUT/campaign110.log" 2>&1
python3 code110/audit110.py --output "$OUTPUT/gain-budget" --inherited "$OUTPUT/r108-reproduction" >"$OUTPUT/audit110.log" 2>&1
printf '%s\n' 'Both independent reproductions and their audits succeeded.' 'These new clocks are not replacements for the deposited local measurements.'
