#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export R7_SOURCE_COMMIT="${1:-local-worktree}"
mkdir -p replication/r7/logs
python - <<'PY'
import os,json,platform,sys,hashlib
from pathlib import Path
import numpy, scipy, torch
record={'source_commit':os.environ['R7_SOURCE_COMMIT'],'python':sys.version,'numpy':numpy.__version__,'scipy':scipy.__version__,'torch':torch.__version__,'platform':platform.platform(),'processor':platform.processor(),'threads':{k:os.environ[k] for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')}}
if Path('/proc/cpuinfo').exists():record['cpu_model']=next((x.split(':',1)[1].strip() for x in Path('/proc/cpuinfo').read_text().splitlines() if x.startswith('model name')),'unknown')
Path('replication/r7/output').mkdir(exist_ok=True)
Path('replication/r7/output/environment.json').write_text(json.dumps(record,indent=2)+'\n')
inv=Path('revisions/2026-09-16-r7/source_inventory.json')
if inv.exists():
 for name,digest in json.loads(inv.read_text()).items():
  assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
PY
for name in validate primitive decision matched adaptive; do
  python "replication/r7/${name}.py" 2>&1 | tee "replication/r7/logs/${name}.log"
done
python -c "import sys;sys.path.insert(0,'replication/r7');from validate import replay_decision;replay_decision()"
python replication/r7/render_tables.py
