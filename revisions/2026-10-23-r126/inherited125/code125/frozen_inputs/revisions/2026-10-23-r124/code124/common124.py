"""R124 custody. Importing this module executes no economic primitive."""
from pathlib import Path
from fractions import Fraction as F
import datetime as dt, hashlib,json,os,platform,resource,sys,time,traceback
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
R123=ROOT.parent/'2026-10-22-r123'
N=16
ARMS=('quadratic','relu','hinge','spline','poly2','poly3','grid')
MODES=('fused_two','joint_two')
ACTOR_COMMIT='796c5f2badf68b051ac6c144884c0e61b87faf5e'

def serial(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,Path):return str(x)
 if isinstance(x,dict):return {str(k):serial(v) for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [serial(v) for v in x]
 if hasattr(x,'tolist'):return serial(x.tolist())
 return x

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(serial(x),f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
def append(p,x):
 with Path(p).open('a') as f:f.write(json.dumps(serial(x),sort_keys=True,allow_nan=False)+'\n')
def rows(p):
 with Path(p).open() as f:return [json.loads(line) for line in f if line.strip()]
def catalog():return [(i,0,'online','online') for i in range(2)]+[(i,b,a,l) for i in range(2) for b in (5,9) for a in ARMS for l in ('value','marginal')]
def model_path(key):
 i,b,a,l=key
 return None if a=='online' else R123/'vendor/2026-10-20-r121/results121'/f'acquisition{b}-attempt01/models/{i}-{a}-{l}/model.json'
def verify_source():
 p=ROOT/'SOURCE_FREEZE124.json';m=json.loads(p.read_text());files=m.get('files',m.get('scientific_files'))
 if not isinstance(files,dict) or not files:raise ValueError('Complete frozen scientific file map required')
 for rel,sha in files.items():
  if digest(REPO/rel)!=sha:raise ValueError('Frozen scientific bytes differ: '+rel)
 return {'manifest_sha256':digest(p),'verified_files':len(files),'verified_before_scientific_import':True}
def boundaries(require_state=True):
 b=json.loads((ROOT/'BOUNDARIES124.json').read_text())
 for f in ('source_commit','state_commit') if require_state else ('source_commit',):
  if len(b[f])!=40 or any(c not in '0123456789abcdef' for c in b[f]):raise ValueError('Full immutable commit required: '+f)
 if b['source_manifest_sha256']!=digest(ROOT/'SOURCE_FREEZE124.json'):raise ValueError('Source identity mismatch')
 if require_state and b['states_sha256']!=digest(ROOT/'results124/states/states124.json'):raise ValueError('State identity mismatch')
 return b

def start(out,kind):
 out=Path(out);out.mkdir(parents=True,exist_ok=False);tick=time.perf_counter()
 info={'kind':kind,'started_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'started_unix':time.time(),
 'argv':sys.argv,'python':sys.version,'platform':platform.platform(),
 'threads':{k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')},
 'cpu':next((s for s in Path('/proc/cpuinfo').read_text().splitlines() if s.startswith('model name')),'unknown'),
 'frequency_and_external_load_controlled':False}
 write(out/'START124.json',info);return out,tick,info

def finish(out,tick,info,**extra):
 r={'status':'executed','exit_code':0,'seconds':time.perf_counter()-tick,'ended_unix':time.time(),
 'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,**extra};write(out/'EXECUTION124.json',r);return r

def fail(out,tick):write(out/'FAILURE124.json',{'status':'failed','seconds':time.perf_counter()-tick,'traceback':traceback.format_exc(),'partial_outputs_retained':True})

def states():
 b=boundaries();data=json.loads((ROOT/'results124/states/states124.json').read_text());raw=(ROOT/'results124/states/entropy124.bin').read_bytes()
 if len(raw)!=160 or len(data['states'])!=N:raise ValueError('Complete fixed state census required')
 for j,r in enumerate(data['states']):
  v=[int.from_bytes(raw[(2*j+k)*5:(2*j+k+1)*5],'little') for k in range(2)]
  if r['row']!=j or r['integers']!=v or r['state']!=[x/2**40 for x in v] or r['hex']!=[float(x).hex() for x in r['state']]:raise ValueError('Entropy/state mismatch')
 return data['states']
