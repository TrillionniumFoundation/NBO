"""Independent arithmetic, provenance, and finite-state theorem regressions."""
from pathlib import Path
from fractions import Fraction as F
import hashlib, itertools, json, math, unittest, platform
import numpy as np
import study as s
R=s.ROOT
J=lambda p:json.loads(p.read_text())
class RevisionTests(unittest.TestCase):
 def test_original_record_hashes(self):
  for i in range(150):s.load_service(i)
 def test_original_source_hashes(self):
  a=J(R/'results/R42_REPLAY.json')
  self.assertEqual(len(a['original_source_hashes']),5)
  for n,h in a['original_source_hashes'].items():self.assertEqual(hashlib.sha256((s.INPUT/'code'/n).read_bytes()).hexdigest(),h)
 def test_original_counts_and_failures(self):
  a=J(R/'results/R42_REPLAY.json');self.assertEqual(sum(a['method_counts'].values()),150)
  self.assertEqual(a['attainment']['direct-neural@0.04'],6)
  self.assertEqual(a['attainment']['convex-neural@0.1'],5)
  self.assertEqual(a['scalar_direct_signs']['0.06']['positive'],29)
 def test_new_record_hashes_and_executed_source(self):
  h=hashlib.sha256((R/'code/study.py').read_bytes()).hexdigest()
  for p in (R/'results').glob('*.clock.json'):
   c=J(p);record=p.with_name(p.name.replace('.clock.json','.json'))
   self.assertEqual(hashlib.sha256(record.read_bytes()).hexdigest(),c['record_sha256'])
   self.assertEqual(h,c['source_sha256'])
 def test_retained_policies_and_bounds(self):
  for i in s.FAILED:
   q=J(R/'results'/f'recertify-{i:03d}.json');r,c=s.load_service(i);old=r['attempts'][-1]
   actor=old['actors'] if i==128 else old['policy']['actors']
   self.assertEqual(s.digest(actor),q['original_actor_sha256']);self.assertEqual(s.digest(r['networks']),q['network_sha256'])
   self.assertEqual(q['training_updates'],0);self.assertEqual(q['new_stored_actor_scalars'],0)
   bound=s.policy_bound(q['refined_residual_records'],old['terminal'],[z['actor_allowance'] for z in old['records']])
   self.assertEqual(bound,q['retained_policy_bound']);self.assertLessEqual(bound,q['target'])
   self.assertGreater(old['policy_gap_upper'],q['target'])
 def test_exact_pairwise_moments(self):
  for x in ([.1,.2,.3,.7],[-1.,1.,3.5,4.,-.25],[2.]*11):
   m,v=s.endpoint_moments(np.array(x));true=sum(map(F,x))/len(x)
   var=sum((F(z)-true)**2 for z in x)/(len(x)-1)
   self.assertLessEqual(F(float(m.lo)),true);self.assertGreaterEqual(F(float(m.hi)),true);self.assertGreaterEqual(F(v),var)
 def test_exact_sqrt_upper(self):
  for x in [0.,1e-100,.1,2.,1e50,math.nextafter(1.,math.inf)]:self.assertGreaterEqual(F(s.sqrt_up(x))**2,F(x))
 def test_uniform_moment_identity(self):
  # Compare the inherited two-uniform squared-hinge expectation with a
  # rationally integrated one-uniform reduction, including degenerate slopes.
  h=F(1,32)
  for y in [F(-1,10),F(-1,64),F(0),F(1,64),F(1,10)]:
   exact=(max(y+h,0)**3-max(y-h,0)**3)/(6*h)
   yi=s.I.point(float(y));hh=s.I.point(float(h))
   a=(yi+hh);b=(yi-hh)
   ap=s.I(np.maximum(a.lo,0),np.maximum(a.hi,0));bp=s.I(np.maximum(b.lo,0),np.maximum(b.hi,0))
   v=(ap*ap*ap-bp*bp*bp)/(6*hh)
   # y is first represented by its exact stored binary coefficient.
   yy=F(float(y));ex=(max(yy+h,0)**3-max(yy-h,0)**3)/(6*h)
   self.assertLessEqual(F(float(v.lo)),ex);self.assertGreaterEqual(F(float(v.hi)),ex)
 def test_actor_boundary_inclusion(self):
  v={'N':1,'actors':[[[0.,0.],[.1,0.],[0.,.1],[.05,.05]]]*4}
  a,b=s.actor_interval(v,0,[s.I.point(np.array([.5])),s.I.point(np.array([.5]))])
  self.assertEqual(b,1)
  for j in (0,1):self.assertLessEqual(a[j].lo[0],0);self.assertGreaterEqual(a[j].hi[0],.1)
 def test_confidence_reconstruction(self):
  from nonlinear import log_bound
  log=log_bound(s.I.point(9600.))
  pairs=sorted((R/'results').glob('paired-?-?.json'));self.assertEqual(len(pairs),24)
  for p in pairs:
   z=J(p);lims=[]
   for j,key in enumerate(('lower_endpoint_moments','upper_endpoint_moments')):
    m=z[key];rad=s.I.point(s.sqrt_up((2*s.I.point(m['sample_variance_upper'])*log/z['sample_size']).hi))+7*s.I.point(z['range_upper'])*log/(3*(z['sample_size']-1))
    mean=s.I(m['mean_lower'],m['mean_upper'])
    lims.append(float((mean-rad).lo) if j==0 else float((mean+rad).hi))
   self.assertEqual(z['confidence_lower'],max(lims[0],z['support_lower']))
   self.assertEqual(z['confidence_upper'],min(lims[1],z['support_upper']))
   self.assertLessEqual(z['confidence_lower'],0);self.assertGreaterEqual(z['confidence_upper'],0)
 def test_bin_identities(self):
  for p in (R/'results').glob('paired-?-?.json'):
   z=J(p);rg=np.random.Generator(np.random.PCG64(z['simulation_seed']))
   x=rg.integers(0,2**40,size=(z['sample_size'],4,2),dtype=np.uint64)
   self.assertEqual(hashlib.sha256(x.astype('<u8').tobytes()).hexdigest(),z['innovation_bin_sha256'])
 def test_finite_state_policy_theorem_and_shift(self):
  rng=np.random.default_rng(441)
  for trial in range(40):
   T=3;S=3;A=2;b=F(3,4)
   c=[[[F(int(rng.integers(-10,11)),8) for _ in range(A)] for _ in range(S)] for _ in range(T)]
   f=[[F(int(rng.integers(-10,11)),8) for _ in range(S)] for _ in range(T+1)]
   g=[F(int(rng.integers(-10,11)),8) for _ in range(S)]
   pi=[[int(rng.integers(A)) for _ in range(S)] for _ in range(T)]
   # Action-dependent equiprobable two-point transitions.
   nxt=lambda x,a:((x+a)%S,(x+a+1)%S)
   q=lambda t,x,a,v:c[t][x][a]+b*sum(v[y] for y in nxt(x,a))/2
   ell=[];uu=[];eta=[]
   for t in range(T):
    qq=[[q(t,x,a,f[t+1]) for a in range(A)] for x in range(S)]
    rr=[f[t][x]-min(qq[x]) for x in range(S)]
    ell.append(min(rr));uu.append(max(rr));eta.append(max(qq[x][pi[t][x]]-min(qq[x]) for x in range(S)))
   rr=[f[T][x]-g[x] for x in range(S)];ell.append(min(rr));uu.append(max(rr))
   V=g[:];J=g[:]
   for t in reversed(range(T)):
    V=[min(q(t,x,a,V) for a in range(A)) for x in range(S)]
    J=[q(t,x,pi[t][x],J) for x in range(S)]
   G=sum(b**t*(uu[t]-ell[t]+eta[t]) for t in range(T))+b**T*(uu[T]-ell[T])
   for x in range(S):self.assertGreaterEqual(J[x]-V[x],0);self.assertLessEqual(J[x]-V[x],G)
   d=[F(int(rng.integers(-5,6))) for _ in range(T+1)]
   newwidth=[(uu[t]+d[t]-b*d[t+1])-(ell[t]+d[t]-b*d[t+1]) for t in range(T)]
   self.assertEqual(newwidth,[uu[t]-ell[t] for t in range(T)])
 def test_exact_paired_telescoping(self):
  # Enumerate every trajectory for two policies and arbitrary continuations.
  b=F(3,4);T=3;f=[[F(t+x,7) for x in range(2)] for t in range(4)]
  cost=lambda x,a:F(2*x+a,5);g=lambda x:F(3*x,4)
  scores=[];costs=[]
  for bits in itertools.product((0,1),repeat=T):
   sv=[];cv=[]
   for policy in (0,1):
    x=0;score=f[0][x];c=F(0)
    for t,z in enumerate(bits):
     a=policy;q=cost(x,a)+b*sum(f[t+1][(x+a+zz)%2] for zz in (0,1))/2
     score+=b**t*(q-f[t][x]);c+=b**t*cost(x,a);x=(x+a+z)%2
    score+=b**T*(g(x)-f[T][x]);c+=b**T*g(x);sv.append(score);cv.append(c)
   scores.append(sv[0]-sv[1]);costs.append(cv[0]-cv[1])
  self.assertEqual(sum(scores),sum(costs))
 def test_completed_processes(self):
  for name,n in [('diagnostic_processes.json',7),('paired_processes.json',24)]:
   a=J(R/'audit'/name);self.assertEqual(len(a),n)
   for z in a:self.assertEqual(z[-1],0)
if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(RevisionTests)
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 (R/'audit/TEST_AUDIT.json').write_text(json.dumps({'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'passed':result.wasSuccessful(),'python':platform.python_version(),'study_sha256':hashlib.sha256((R/'code/study.py').read_bytes()).hexdigest()},indent=2)+'\n')
 raise SystemExit(not result.wasSuccessful())
