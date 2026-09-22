"""Exact rational continuum-price certification; no sampled-price acceptance.
Convex chords upper-bound the full adaptive optimum. Frozen feasible policies
supply affine lower bounds, with independent expenditure intervals. Every
maximum is attained at an exact upper-envelope vertex or an interval endpoint.
"""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, math, os, pathlib, subprocess, sys, time
from fractions import Fraction as F
ROOT=pathlib.Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-22-r12'
TARGET=F('0.01')
def dump(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def upward(x):
 y=float(x)
 return math.nextafter(y,math.inf) if F(y)<x else y
def downward(x):
 y=float(x)
 return math.nextafter(y,-math.inf) if F(y)>x else y

def anchors():
 src=ROOT/'revisions/2026-09-22-r10/results/scientific_summary.json';data=json.loads(src.read_text())
 return [{'k':r['k'],'L':r['policy_value_interval'][0],'U':r['optimal_value_interval'][1],
          'B':r['policy_adjustment_budget_interval'],'actor_path':f"revisions/2026-09-22-r10/results/actor_k{r['k']:g}.json",
          'origin':'inherited','source_path':str(src.relative_to(ROOT)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'seconds':0.} for r in data['economy']]

def load_nodes():
 nodes=anchors()
 for path in sorted((REV/'results/cases').glob('*/status.json')):
  data=json.loads(path.read_text())
  if data['status']=='success':
   data['origin']='new';data['source_path']=str(path.relative_to(ROOT));data['source_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();nodes.append(data)
 # Never treat failed/missing planned nodes as successes. Recomputed duplicate
 # prices may improve bounds only after their own independent certificate.
 keep={}
 for d in nodes:
  k=F(d['k'])
  if k in keep:raise ValueError('Duplicate certified price')
  if not all(math.isfinite(z) for z in [d['k'],d['L'],d['U'],*d['B']]) or d['L']>d['U'] or not 0<=d['B'][0]<=d['B'][1]:raise ValueError('Invalid input interval')
  keep[k]=d
 return [keep[k] for k in sorted(keep)]

def lines_on(nodes,a,b):
 lines=[]
 for i,n in enumerate(nodes):
  k=F(n['k']);B=F(n['B'][1] if a>=k else n['B'][0])
  # The enclosing interval has no certified price in its interior.
  assert k<=a or k>=b
  lines.append((-B,F(n['L'])+k*B,i))
 return lines

def upper_hull(lines):
 same={}
 for m,c,i in lines:
  if m not in same or (c,-i)>(same[m][0],-same[m][1]):same[m]=(c,i)
 hull=[]
 for m in sorted(same):
  c,i=same[m];start=None
  while hull:
   pm,pc,pi,ps=hull[-1];start=(pc-c)/(m-pm)
   if ps is None or start>ps:break
   hull.pop()
  if not hull:start=None
  hull.append((m,c,i,start))
 return hull

def certify(nodes):
 if len(nodes)<2 or F(nodes[0]['k'])!=F('.5') or F(nodes[-1]['k'])!=F(8):raise ValueError('Missing boundary certificate')
 if any(F(a['k'])>=F(b['k']) for a,b in zip(nodes[:-1],nodes[1:])):raise ValueError('Unordered or duplicate price')
 for n in nodes:
  if not all(math.isfinite(z) for z in [n['k'],n['L'],n['U'],*n['B']]) or n['L']>n['U'] or not 0<=n['B'][0]<=n['B'][1]<=.02:raise ValueError('Invalid node')
 cells=[];worst=(F(-1),None)
 for left,right in zip(nodes[:-1],nodes[1:]):
  a,b=F(left['k']),F(right['k']);ua,ub=F(left['U']),F(right['U'])
  lines=lines_on(nodes,a,b);hull=upper_hull(lines)
  points=sorted({a,b}|{q[3] for q in hull if q[3] is not None and a<q[3]<b})
  vertices=[];maxgap=F(-1);arg=None
  for x in points:
   lower,ix=max((m*x+c,-i) for m,c,i in lines);ix=-ix
   upper=((b-x)*ua+(x-a)*ub)/(b-a);gap=upper-lower
   if gap<0:raise ValueError('Inconsistent upper and feasible-policy lower bounds')
   vertices.append({'price_rational':str(x),'gap_rational':str(gap),'gap_upper':upward(gap),'actor_index':ix})
   if gap>maxgap:maxgap,arg=gap,x
  cell={'left':float(a),'right':float(b),'max_gap_rational':str(maxgap),'max_gap_upper':upward(maxgap),'maximizer_rational':str(arg),
        'target_met':maxgap<TARGET,'vertices':vertices}
  cells.append(cell)
  if maxgap>worst[0]:worst=(maxgap,arg)
 return {'status':'PASS' if all(c['target_met'] for c in cells) else 'REFINE',
         'interval':[.5,8.],'target':.01,'certified_prices':len(nodes),'cells':cells,
         'uniform_regret_upper':upward(worst[0]),'uniform_regret_rational':str(worst[0]),
         'maximizer_rational':str(worst[1]),'nodes':nodes,
         'scope':'Every real adjustment price in [0.5,8], central initial state, unchanged stopped economy, selection from frozen feasible policies; no claim of uniformity over initial states.'}

def execute(k):
 out=REV/f'results/cases/k{k:g}';out.mkdir(parents=True,exist_ok=True)
 command=[sys.executable,str(REV/'replication/cost_case.py'),'--k',repr(k),'--out',str(out)]
 with (out/'process.log').open('w') as log:
  p=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1'))
 return {'k':k,'returncode':p.returncode,'status_file':str((out/'status.json').relative_to(ROOT))}

def refine(workers=4,rounds=1,max_nodes=96):
 clock=time.perf_counter();logpath=REV/'results/refinement_history.json'
 history=json.loads(logpath.read_text()) if logpath.exists() else {'rounds':[],'status':'started','target':.01,'selection':'Bisect failing intervals in increasing-price order, one parallel batch per invocation; no sampled-price acceptance.'}
 for _ in range(rounds):
  nodes=load_nodes();current=certify(nodes);dump(REV/'results/envelope.json',current)
  if current['status']=='PASS':history['status']='PASS';break
  proposals=[(F(c['left'])+F(c['right']))/2 for c in current['cells'] if not c['target_met']][:workers]
  if len(nodes)+len(proposals)>max_nodes:history['status']='NODE_LIMIT';break
  for x in proposals:
   if F(float(x))!=x:raise ValueError('Bisection price not exactly binary64 representable')
  record={'before_nodes':len(nodes),'before_uniform_regret':current['uniform_regret_upper'],'planned_prices':[float(x) for x in proposals],'source_commit':os.environ.get('R12_SOURCE_COMMIT','local-development'),'status':'running'}
  history['rounds'].append(record);dump(logpath,history);t=time.perf_counter()
  with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:results=list(pool.map(execute,[float(x) for x in proposals]))
  record.update(status='success' if all(r['returncode']==0 for r in results) else 'failed',results=results,wall_seconds=time.perf_counter()-t);dump(logpath,history)
  if record['status']!='success':history['status']='FAILED';dump(logpath,history);raise RuntimeError('A planned cell failed; raw states retained')
 final=certify(load_nodes());dump(REV/'results/envelope.json',final)
 history['status']=final['status'];history['last_invocation_seconds']=time.perf_counter()-clock;dump(logpath,history)
 print(json.dumps({k:final[k] for k in ['status','certified_prices','uniform_regret_upper','maximizer_rational']}),flush=True)
 return final
def query(price,nodes=None):
 """Evaluate an exact decimal string/rational; floats denote binary64 reals."""
 k=F(price);nodes=load_nodes() if nodes is None else nodes
 if not F('.5')<=k<=F(8):raise ValueError('Price outside certified range')
 for a,b in zip(nodes[:-1],nodes[1:]):
  left,right=F(a['k']),F(b['k'])
  if left<=k<=right:
   lines=lines_on(nodes,left,right);L,i=max((m*k+c,-j) for m,c,j in lines);i=-i
   U=((right-k)*F(a['U'])+(k-left)*F(b['U']))/(right-left)
   return {'price_rational':str(k),'actor_path':nodes[i]['actor_path'],'selected_node':nodes[i]['k'],
           'value_interval':[downward(L),upward(U)],'lower_rational':str(L),'upper_rational':str(U),
           'regret_upper':upward(U-L),'regret_rational':str(U-L)}
 raise AssertionError('No covering interval')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--rounds',type=int,default=1);p.add_argument('--workers',type=int,default=4);p.add_argument('--check-only',action='store_true');a=p.parse_args()
 if a.check_only:dump(REV/'results/envelope.json',certify(load_nodes()))
 else:refine(a.workers,a.rounds)
