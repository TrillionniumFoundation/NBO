"""Read-only scientific validation. Assertions are theorem-premise checks, not proofs."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,itertools,random,copy,sys,argparse,time
import adaptive as a
import economics as eco
from structural import optimal,guard
from flint import arb
R=a.REV;OUT=R/'results/adaptive'; counts={}
def load(p):return json.loads(Path(p).read_text())
def tally(k,n=1):counts[k]=counts.get(k,0)+n

def rejects(f):
 try:f()
 except (AssertionError,ValueError,RuntimeError):tally('rejected_malformed_objects');return
 raise AssertionError('malformed object accepted')

def verify_candidates():
 rows=load(OUT/'summary.json');events=load(OUT/'FREEZE_MANIFEST.json')
 assert len(rows)==len(events)==60
 assert len({r['tag'] for r in rows})==60
 assert {(r['model'],r['method'],r['width'],r['seed']) for r in rows}==set(itertools.product(a.MODELS,('adam','lbfgs'),(8,16),range(30001,30006)))
 for row,event in zip(rows,events):
  tag=row['tag'];payload=load(OUT/'candidates'/f'{tag}.json')
  assert event['tag']==tag and a.digest(payload)==event['sha256']
  segments,points=a.compile_nn(payload['params']);compiled=load(OUT/'compiled'/f'{tag}.json')
  assert segments==[(F(l),F(r),b) for l,r,b in compiled['segments']]
  assert points=={F(x):b for x,b in compiled['points']}
  cert=load(OUT/'certificates'/f'{tag}.json');assert a.digest(cert)==row['certificate_sha256']
  metrics=a.verify(a.MODELS[row['model']],cert)
  assert all(row[k]==v for k,v in metrics.items())
  for leaf in cert['leaves']:
   l,r=F(leaf['l']),F(leaf['r']);m=(l+r)/2
   # Every leaf must lie inside a compiled constant-score-sign piece.
   assert any(ll<=l<r<=rr and b==leaf['raw'] for ll,rr,b in segments)
   assert leaf['raw']==int(a.nnval(payload['params'],m)>=0)
   tally('linked_certificate_regions')
  for p in cert['points']:
   assert p['raw']==int(a.nnval(payload['params'],F(p['x']))>=0);tally('linked_tie_points')
  raw=a.raw_regret(a.MODELS[row['model']],segments,points)
  assert all(row[k]==v for k,v in raw.items())
  assert F(row['guaranteed_regret'])<=a.EPS
  for m in (8,12,20,40):
   for i in (0,2**m//3,2**m//2,2**m-1):
    x=F(2*i+1,2**(m+1));act=a.deploy_index(cert,i,m);f=a.val(a.MODELS[row['model']],x)
    assert max(F(0),f)-act*f<=a.ETA;tally('integer_grid_query_checks')
  tally('neural_candidate_certificates')
  assert eco.overlay_cost(segments,eco.policy_segments(cert))==F(row['priority_edits'])
  tally('independent_occupancy_overlays')
 for model,c in a.MODELS.items():
  p=load(OUT/'candidates'/f'{model}_polynomial.json')
  comp=load(OUT/'compiled'/f'{model}_polynomial.json');segments=[(F(l),F(r),b) for l,r,b in comp['segments']];points={F(x):b for x,b in comp['points']}
  cert=load(OUT/'certificates'/f'{model}_polynomial.json');a.verify(c,cert)
  assert a.raw_regret(c,segments,points)['worst_regret_upper']==next(z for z in load(OUT/'polynomial_controls.json') if z['model']==model)['worst_regret_upper']
  tally('polynomial_candidate_certificates')
  for name in ('constant0','constant1','structured_matched','structured_near_exact'):
   a.verify(c,load(OUT/'baselines'/f'{model}_{name}.json'));tally('classical_cover_certificates')
  for i in range(257):
   x=F(i,256);f=a.val(c,x);assert max(F(0),f)-optimal(c,x)*f==0
   for raw in (0,1):
    b=guard(c,x,raw);assert max(F(0),f)-b*f<=a.ETA
    assert (b-raw)*f>=0
    if b!=raw:assert max(F(0),f)-raw*f>a.ETA
    tally('exact_structural_guard_checks')


def negative_and_algebra():
 c=a.MODELS['linear'];s,p=a.constant(0);ce=a.complete(c,s,p)
 bad=copy.deepcopy(ce);bad['leaves'][0]['l']='1/100';rejects(lambda:a.verify(c,bad))
 bad=copy.deepcopy(ce);bad['points'].pop();rejects(lambda:a.verify(c,bad))
 bad=copy.deepcopy(ce);bad['leaves'][0]['raw_gap_hi']='-100';rejects(lambda:a.verify(c,bad))
 bad=copy.deepcopy(ce);bad['eta']='-1';rejects(lambda:a.verify(c,bad))
 rejects(lambda:a.complete(c,s,p,F(-1)))
 rejects(lambda:a.deploy_index(ce,-1,4));rejects(lambda:a.deploy_index(ce,16,4))
 rng=random.Random(1937)
 for _ in range(100):
  poly=[F(rng.randint(-20,20),13) for _ in range(4)]
  l=F(rng.randrange(0,10),10);r=l+F(1,10);lo,hi=a.bernstein(poly,l,r)
  for j in range(11):assert lo<=a.val(poly,l+(r-l)*F(j,10))<=hi
  tally('exact_bernstein_polynomial_checks')
 # Zero tolerance is a finite-state exact completion statement, not a claim
 # that continuous interval subdivision terminates at an irrational root.
 beta=F(9,10);P=[[[F(3,4),F(1,4)],[F(1,4),F(3,4)]],[[F(1,2),F(1,2)],[F(2,3),F(1,3)]]]
 rewards=[[[F(0),F(1,3)],[F(1,2),F(1,5)]],[[F(2,5),F(1,4)],[F(0),F(3,5)]]]
 def evaluate(pol,cost=False,raw=None):
  v=[F(0),F(0)]
  for t in (1,0):
   v=[(F(pol[t][s]!=raw[t][s])*(s+1) if cost else rewards[t][s][pol[t][s]])+beta*sum(P[s][pol[t][s]][j]*v[j] for j in (0,1)) for s in (0,1)]
  return v
 def backwards(raw,allowed=None,cost=False):
  v=[F(0),F(0)];pol=[[0,0],[0,0]];values=[None,None,v]
  for t in (1,0):
   new=[]
   for s in (0,1):
    choices=allowed[t][s] if allowed else (0,1)
    q={b:(F(b!=raw[t][s])*(s+1) if cost else rewards[t][s][b])+beta*sum(P[s][b][j]*v[j] for j in (0,1)) for b in choices}
    best=(min if cost else max)(q.values());b=raw[t][s] if raw[t][s] in q and q[raw[t][s]]==best else next(b for b in choices if q[b]==best)
    pol[t][s]=b;new.append(best)
   v=new;values[t]=v
  return pol,values
 policies=[[[b[0],b[1]],[b[2],b[3]]] for b in itertools.product((0,1),repeat=4)]
 for raw in policies:
  pi,U=backwards(raw);assert evaluate(pi)==U[0]
  assert U[0]==[max(evaluate(q)[s] for q in policies) for s in (0,1)];tally('zero_tolerance_exact_policies')
  # Give a large enough budget to make the known optimal action feasible;
  # require own-policy improvement separately as in the paper.
  v0=[None,None,[F(0),F(0)]]
  for t in (1,0):v0[t]=[rewards[t][s][raw[t][s]]+beta*sum(P[s][raw[t][s]][j]*v0[t+1][j] for j in (0,1)) for s in (0,1)]
  e=[[F(1),F(1)],[F(1,2),F(1,2)],[F(0),F(0)]]
  B=[[[],[]],[[],[]]]
  for t in (0,1):
   for s in (0,1):
    for b in (0,1):
     q=rewards[t][s][b]+beta*sum(P[s][b][j]*(U[t+1][j]-e[t+1][j]) for j in (0,1))
     q0=rewards[t][s][b]+beta*sum(P[s][b][j]*v0[t+1][j] for j in (0,1))
     if q>=U[t][s]-e[t][s] and q0>=v0[t][s]:B[t][s].append(b)
  if all(B[t][s] for t in (0,1) for s in (0,1)):
   chosen,D=backwards(raw,B,True)
   eligible=[p for p in policies if all(p[t][s] in B[t][s] for t in (0,1) for s in (0,1))]
   assert D[0]==[min(evaluate(q,True,raw)[s] for q in eligible) for s in (0,1)]
   for q in eligible:
    v=evaluate(q);assert all(v[s]>=v0[0][s] and U[0][s]-v[s]<=e[0][s] for s in (0,1))
   tally('certified_class_bruteforce_optima')


def stopping_records(recompute=False):
 import stopping as st
 rows=[]
 for text in ('-0.2','-0.1','0','0.1','0.2'):
  row=load(R/'results/stopping'/(text.replace('-','minus').replace('.','p')+'.json'));rows.append(row)
  p,_=st.exit_prob(arb(text));assert p.overlaps(arb(row['exit_probability']['ball']))
  for j in range(3):
   rec=row['derivatives'][str(j)];assert 'error' not in rec
   ball=arb(rec['enclosure']['ball']);assert ball.is_finite() and ball.rad()<arb('.005')
   if recompute:
    v,err,stats=st.payoff_derivative(arb(text),j);assert ball.overlaps(v)
   tally('validated_stopping_enclosures')
 assert arb(rows[2]['exit_probability']['ball'])>arb('.68')
 assert arb(rows[2]['derivatives']['2']['enclosure']['ball'])>0
 assert arb(rows[3]['derivatives']['2']['enclosure']['ball'])<0
 for row in load(R/'results/bracketing.json'):
  assert row['derivative_bracket']['projected_gradient_upper']<=.005
  assert row['derivative_bracket']['oracle_calls']<row['poll']['oracle_calls'];tally('classical_derivative_comparisons')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(R/'results/VALIDATION.json'));ap.add_argument('--recompute-stopping',action='store_true');args=ap.parse_args();start=time.perf_counter()
 verify_candidates();negative_and_algebra();stopping_records(args.recompute_stopping)
 out={'status':'PASS','checks':counts,'elapsed_seconds':time.perf_counter()-start,
  'stopping_recomputed':args.recompute_stopping,'original_full_domain_target_certified':False,
  'scope':'R30 only; inherited R29 validation is run separately on the remote full checkout'}
 Path(args.output).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
