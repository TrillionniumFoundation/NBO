"""R122 custody and immutable evidence I/O; no economic execution on import."""
from __future__ import annotations
import datetime as dt, gzip, hashlib, json, os, platform, resource, subprocess, sys, time, traceback
from pathlib import Path
from fractions import Fraction
F=Fraction
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
R121=ROOT.parent/'2026-10-20-r121'
N=32
SERVICES=('control','recycled','adaptive')
ARMS=('quadratic','relu','hinge','spline','poly2','poly3','grid')
ACTOR_COMMIT='796c5f2badf68b051ac6c144884c0e61b87faf5e'

def digest(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def plain(v):
 if isinstance(v,Fraction):return str(v)
 if isinstance(v,Path):return str(v)
 if isinstance(v,dict):return {str(k):plain(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [plain(x) for x in v]
 if hasattr(v,'tolist'):return plain(v.tolist())
 return v

def dump(p,obj):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8') as f:json.dump(plain(obj),f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')

def append(p,obj):
 with Path(p).open('a',encoding='utf-8') as f:f.write(json.dumps(plain(obj),sort_keys=True,allow_nan=False)+'\n')

def rows(p):
 op=gzip.open if str(p).endswith('.gz') else open
 with op(p,'rt',encoding='utf-8') as f:return [json.loads(s) for s in f if s.strip()]

def git_file(commit,rel):
 return subprocess.check_output(['git','show',commit+':'+str(rel)],cwd=REPO)

def verify_source(commit):
 if len(commit)!=40 or any(c not in '0123456789abcdef' for c in commit):raise ValueError('Full immutable source commit required')
 path=ROOT/'SOURCE_FREEZE122.json';rel=path.relative_to(REPO)
 if git_file(commit,rel)!=path.read_bytes():raise ValueError('Source manifest differs from immutable F')
 d=json.loads(path.read_text())
 for rel,sha in sorted(d['scientific_files'].items()):
  p=REPO/rel
  if digest(p)!=sha:raise ValueError('Local frozen source differs: '+rel)
  if hashlib.sha256(git_file(commit,rel)).hexdigest()!=sha:raise ValueError('Git frozen source differs: '+rel)
 return {'source_commit':commit,'manifest_sha256':digest(path),'files':len(d['scientific_files']),'verified_before_scientific_import':True}

def catalog():
 return [(i,0,'online','online') for i in range(2)]+[(i,b,a,l) for i in range(2) for b in (5,9) for a in ARMS for l in ('value','marginal')]

def model_path(key):
 i,b,a,l=key
 return None if a=='online' else R121/'results121'/f'acquisition{b}-attempt01'/'models'/f'{i}-{a}-{l}'/'model.json'

def identities(n=N):return {(i,j,b,a,l,s) for i,b,a,l in catalog() for j in range(n) for s in SERVICES}
def key(r):return (r['index'],r['row'],r['budget'],r['arm'],r['loss'],r['service'])

def verify_actors():
 record=[]
 for k in catalog():
  p=model_path(k)
  if p:
   rel=p.relative_to(REPO);b=p.read_bytes()
   if git_file(ACTOR_COMMIT,rel)!=b:raise ValueError('Inherited actor is not its actual immutable M: '+str(rel))
   record.append({'key':k,'path':str(rel),'sha256':hashlib.sha256(b).hexdigest()})
 return record

def start(output,mode,source):
 out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
 obj={'mode':mode,'source':source,'started_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'started_unix':time.time(),'argv':sys.argv,'python':sys.version,'platform':platform.platform(),'threads':{k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')},'process_receipt_excludes_parent_launcher_overhead':True}
 dump(out/'START122.json',obj);return out,obj,time.perf_counter()

def finish(out,initial,tick,extra=None):
 d={'status':'executed','exit_code':0,'started_unix':initial['started_unix'],'ended_unix':time.time(),'seconds':time.perf_counter()-tick,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
 d.update(extra or {});dump(out/'EXECUTION122.json',d)

def fail(out,tick):dump(out/'FAILURE122.json',{'status':'failed','seconds':time.perf_counter()-tick,'traceback':traceback.format_exc(),'all_partial_outputs_retained':True})


def validated_states(directory,source_commit,state_commit):
 p=Path(directory).resolve();manifest=json.loads((p/'STATE_MANIFEST122.json').read_text())
 if manifest['source_commit']!=source_commit or manifest['actor_commit']!=ACTOR_COMMIT:raise ValueError('State boundary source mismatch')
 for name,sha in manifest['files'].items():
  if digest(p/name)!=sha or hashlib.sha256(git_file(state_commit,(p/name).relative_to(REPO))).hexdigest()!=sha:raise ValueError('State bytes not immutable D: '+name)
 if git_file(state_commit,(p/'STATE_MANIFEST122.json').relative_to(REPO))!=(p/'STATE_MANIFEST122.json').read_bytes():raise ValueError('State manifest not remote D')
 subprocess.run(['git','merge-base','--is-ancestor',source_commit,state_commit],cwd=REPO,check=True)
 data=json.loads((p/'states122.json').read_text())['states'];raw=(p/'entropy122.bin').read_bytes()
 if len(raw)!=320 or len(data)!=32:raise ValueError('Complete fixed 32-state census required')
 for j,r in enumerate(data):
  ints=[int.from_bytes(raw[(2*j+k)*5:(2*j+k+1)*5],'little') for k in range(2)]
  if r['row']!=j or r['integers']!=ints or r['state']!=[n/2**40 for n in ints] or r['hex']!=[v.hex() for v in r['state']]:raise ValueError('Entropy-to-state identity differs')
 return data


def validated_primary(directory,source_commit):
 p=Path(directory);binding=json.loads((p/'STATES_USED122.json').read_text())
 if binding['source_commit']!=source_commit or binding['actor_commit']!=ACTOR_COMMIT:raise ValueError('Primary boundary source differs')
 state_commit=binding['state_commit'];states=validated_states(REPO/binding['state_directory'],source_commit,state_commit)
 data=rows(p/'records122.jsonl')
 if len(data)!=len(identities()) or {key(r) for r in data}!=identities():raise ValueError('Full primary identity census required')
 for r in data:
  if r['source_commit']!=source_commit or r['state_commit']!=state_commit or r['actor_commit']!=ACTOR_COMMIT or r['population_observation'] is not True or r['repeat'] is not None:raise ValueError('Mixed scientific identity in primary')
  if r['state']!=states[r['row']]['state'] or r['state_hex']!=states[r['row']]['hex'] or r['alpha']!=(.5,.75)[r['index']]:raise ValueError('Primary state/risk identity differs')
  cap=F(1,8)+sum(map(F,r['state']))/16
  for field,hfield in (('action','action_hex'),('baseline_action','baseline_action_hex')):
   a=F(r[field])
   if not 0<=a<=cap or float(a).hex()!=r[hfield]:raise ValueError('Infeasible or misidentified primary '+field)
  raw=r['raw_proposal_kept']
  if raw is None:
   if not r.get('proposal_numerical_failure'):raise ValueError('Absent raw proposal without numerical failure')
  elif not 0<=F(raw)<=cap or float(raw).hex()!=r['first_proposal_action_hex']:raise ValueError('Infeasible or misidentified raw actor proposal')
  if raw!=r['baseline_first_proposal_action']:raise ValueError('Raw actor proposal changed in reporting')
  if r['qualified'] is not True:raise ValueError('Unqualified final primary policy')
 return data,binding
