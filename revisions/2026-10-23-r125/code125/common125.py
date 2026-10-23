"""Prospective R125 custody and fixed deterministic design; no economics on import."""
from pathlib import Path
from fractions import Fraction as F
import datetime as dt, gzip, hashlib, json, os, platform, resource, sys, time, traceback
ROOT=Path(__file__).resolve().parents[1]
CODE=ROOT/'code125'
FROZEN=CODE/'frozen_inputs'
R123=FROZEN/'revisions/2026-10-22-r123'
R121=R123/'vendor/2026-10-20-r121'
STATES=((.25,.25),(.25,.75),(.75,.25),(.75,.75))
ARMS=('quadratic','relu','hinge','spline','poly2','poly3','grid')
MODES=('fused_control','warm_adaptive','cold_adaptive','warm_fixed512')
ACTOR_COMMIT='796c5f2badf68b051ac6c144884c0e61b87faf5e'
TARGET=F(1,65536);TAU=F(1,256);OMEGA=F(1,8192);DELTA=F(15,2**24)
LADDER=(32,64,128,256,512,1024,2048)
MAX_CENTERS=8
NODE_BUDGET=32768

def plain(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,Path):return str(x)
 if isinstance(x,dict):return {str(k):plain(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [plain(v) for v in x]
 if hasattr(x,'tolist'):return plain(x.tolist())
 return x
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(plain(x),f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
def append(p,x):
 p=Path(p);line=(json.dumps(plain(x),sort_keys=True,allow_nan=False)+'\n').encode()
 if p.suffix=='.gz':
  with p.open('ab') as f:
   with gzip.GzipFile(fileobj=f,filename='',mode='wb',mtime=0,compresslevel=6) as g:g.write(line)
 else:
  with p.open('ab') as f:f.write(line)
def rows(p):
 p=Path(p)
 with (gzip.open(p,'rt') if p.suffix=='.gz' else p.open()) as f:return [json.loads(x) for x in f if x.strip()]
def actors():return [(i,0,'online','online') for i in range(2)]+[(i,b,a,l) for i in range(2) for b in (5,9) for a in ARMS for l in ('value','marginal')]
def catalog():return [k+(m,) for k in actors() for m in MODES]+[(i,0,'uniform_dp','none','grid33') for i in range(2)]
def model_path(k):
 i,b,a,l=k
 return None if a in ('online','uniform_dp') else R121/f'results121/acquisition{b}-attempt01/models/{i}-{a}-{l}/model.json'
def verify_inputs(require_remote=True):
 m=json.loads((ROOT/'SOURCE_FREEZE125.json').read_text())
 for rel,d in m['files'].items():
  if sha(ROOT/rel)!=d:raise ValueError('R125 frozen scientific byte mismatch: '+rel)
 if require_remote:
  b=json.loads((ROOT/'BOUNDARIES125.json').read_text())
  if not b.get('remote_source_readback_before_economics') or len(b['source_commit'])!=40:raise ValueError('Remote F125 gate is required')
  if b['source_manifest_sha256']!=sha(ROOT/'SOURCE_FREEZE125.json'):raise ValueError('R125 source boundary differs')
 else:b=None
 return dict(files=len(m['files']),manifest_sha256=sha(ROOT/'SOURCE_FREEZE125.json'),boundaries=b)
def start(out,kind):
 out=Path(out);out.mkdir(parents=True,exist_ok=False);tick=time.perf_counter()
 info=dict(kind=kind,started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),started_unix=time.time(),argv=sys.argv,python=sys.version,platform=platform.platform(),threads={k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')},shared_host=True,controlled_frequency_or_load=False)
 write(out/'START125.json',info);return out,tick,info
def finish(out,tick,**more):
 r=dict(status='executed',exit_code=0,seconds=time.perf_counter()-tick,ended_unix=time.time(),peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,**more)
 write(out/'EXECUTION125.json',r);return r
def fail(out,tick):write(out/'FAILURE125.json',dict(status='failed',seconds=time.perf_counter()-tick,traceback=traceback.format_exc(),partial_outputs_retained=True))
