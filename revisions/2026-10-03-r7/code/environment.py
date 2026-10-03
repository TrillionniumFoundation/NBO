"""Capture source, math-library and platform identity without credentials."""
import contextlib, hashlib, io, json, os, platform, subprocess, sys
from pathlib import Path
import numpy as np, scipy, torch, mpmath
R=Path(__file__).resolve().parents[1]
s=io.StringIO()
with contextlib.redirect_stdout(s):np.show_config()
def command(args):
    try:return subprocess.run(args,capture_output=True,text=True,timeout=10).stdout
    except (OSError,subprocess.TimeoutExpired):return 'unavailable'
data=dict(python=sys.version,platform=platform.platform(),machine=platform.machine(),processor=platform.processor(),
    versions=dict(numpy=np.__version__,scipy=scipy.__version__,torch=torch.__version__,mpmath=mpmath.__version__),
    numpy_config=s.getvalue(),torch_config=torch.__config__.show(),lscpu=command(['lscpu']),compiler=command(['gcc','--version']),
    thread_environment={k:os.environ.get(k) for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','PYTHONHASHSEED']},
    policy='training code sets float64, one PyTorch thread, and deterministic algorithms; no cross-platform bitwise claim',
    source_commit=command(['git','rev-parse','HEAD']).strip(),
    source_hashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((R/'code').glob('*.py'))})
(R/'results').mkdir(exist_ok=True,parents=True)
(R/'results/ENVIRONMENT.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(data['versions']))
