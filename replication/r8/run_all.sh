#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
mkdir -p replication/r8/logs replication/r8/output
python - <<'PY'
import sys,platform,json,os
from pathlib import Path
import numpy,scipy
Path('replication/r8/output/environment.json').write_text(json.dumps(dict(python=sys.version,numpy=numpy.__version__,scipy=scipy.__version__,platform=platform.platform(),source_commit=os.environ.get('NBO_SOURCE_SHA','local-execution'),threads=1),indent=2)+'\n')
PY
for script in model validate primitive mechanisms certificate; do
  python "replication/r8/$script.py" > "replication/r8/logs/$script.log" 2>&1
done
for n in 49 97 145; do
  python replication/r8/spatial.py --nx "$n" > "replication/r8/logs/spatial_${n}.log" 2>&1
done
python replication/r8/render_tables.py
python replication/r8/build_report.py --precompile
