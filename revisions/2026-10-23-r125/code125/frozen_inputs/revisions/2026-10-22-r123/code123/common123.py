"""R123 immutable-file checks and complete, exclusive execution receipts."""
from pathlib import Path
from fractions import Fraction
import datetime as dt,gzip,hashlib,json,os,platform,resource,sys,time,traceback

ROOT=Path(__file__).resolve().parents[1]
N=32
ARMS=('quadratic','relu','hinge','spline','poly2','poly3','grid')
MODES=('r122','best_single','fused','probe_fused')
FIELDS=('index','budget','arm','training_loss','mode')

def serial(x):
    if isinstance(x,Fraction):return str(x)
    if isinstance(x,Path):return str(x)
    if isinstance(x,dict):return {str(k):serial(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [serial(v) for v in x]
    if hasattr(x,'tolist'):return serial(x.tolist())
    return x

def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def write(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(serial(x),f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')

def append(p,x):
    with Path(p).open('a') as f:f.write(json.dumps(serial(x),sort_keys=True,allow_nan=False)+'\n')

def rows(p):
    op=gzip.open if str(p).endswith('.gz') else open
    with op(p,'rt') as f:
        for line in f:
            if line.strip():yield json.loads(line)

def actors():
    return [(i,0,'online','online') for i in range(2)]+[(i,b,a,l) for i in range(2) for b in (5,9) for a in ARMS for l in ('value','marginal')]

def groups():return [k+(m,) for k in actors() for m in MODES]

def model_path(key):
    i,b,a,l=key[:4]
    return None if a=='online' else ROOT/'vendor/2026-10-20-r121/results121'/f'acquisition{b}-attempt01/models/{i}-{a}-{l}/model.json'

def verify_source():
    path=ROOT/'SOURCE_FREEZE123.json';manifest=json.loads(path.read_text())
    for rel,sha in manifest['files'].items():
        if digest(ROOT/rel)!=sha:raise ValueError('Frozen scientific member changed: '+rel)
    return dict(source_manifest_sha256=digest(path),files=len(manifest['files']),checked_before_scientific_import=True)

def boundaries(require_state=True):
    b=json.loads((ROOT/'BOUNDARIES123.json').read_text())
    if digest(ROOT/'SOURCE_FREEZE123.json')!=b['source_manifest_sha256']:raise ValueError('Source boundary mismatch')
    if require_state and digest(ROOT/'results123/states/states123.json')!=b['states_sha256']:raise ValueError('State boundary mismatch')
    for field in (['source_commit','state_commit'] if require_state else ['source_commit']):
        if len(b[field])!=40 or any(c not in '0123456789abcdef' for c in b[field]):raise ValueError('Full published commit required')
    return b

def start(output,kind):
    tick=time.perf_counter();out=Path(output);out.mkdir(parents=True,exist_ok=False)
    initial=dict(kind=kind,started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),started_unix=time.time(),
                 command=sys.argv,python=sys.version,platform=platform.platform(),
                 threads={k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')},
                 cpu=next((s for s in Path('/proc/cpuinfo').read_text().splitlines() if s.startswith('model name')),'unknown'),
                 frequency_and_external_load_controlled=False)
    write(out/'START123.json',initial)
    return out,tick,initial

def finish(out,tick,initial,**extra):
    receipt=dict(status='executed',exit_code=0,seconds=time.perf_counter()-tick,ended_unix=time.time(),
                 peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,**extra)
    write(out/'EXECUTION123.json',receipt);return receipt

def failed(out,tick):
    write(out/'FAILURE123.json',dict(status='failed',seconds=time.perf_counter()-tick,traceback=traceback.format_exc(),all_partial_outputs_retained=True))
