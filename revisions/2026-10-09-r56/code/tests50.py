"""Exact and independent regression checks for R50."""
import itertools, unittest, tempfile, json
from pathlib import Path
from fractions import Fraction as F
import operators50 as o
np=o.np;I=o.I

class R50Tests(unittest.TestCase):
 def test_terminal_integral_exact(self):
  for d,p in itertools.product((2,3,4),(1,4)):
   for x in [[F(1,8)]*d,[F(1,2)]*d,[F(j+1,d+2) for j in range(d)]]:
    a=F(1,16);gam=[F(1,2) if j%2==0 else F(1,4) for j in range(d)];sg=[1 if j%2==0 else -1 for j in range(d)]
    y=[F(1,16)+x[j]/2+x[(j+1)%d]/8+x[j]*(1-x[(j+1)%d])/16+gam[j]*a for j in range(d)]
    def terminal(z):
     v=[q+ss*z for q,ss in zip(y,sg)]
     return 4*sum((q-F(5,8))**2 for q in v)/d+sum((v[j]-v[(j+1)%d])**2 for j in range(d))/(4*d)+2*max(F(0),F(1,2)-2*sum(v)/d)**2
    cuts=[F(-1,32),F(1,32)]
    if sum(sg):
     root=(F(d,4)-sum(y))/sum(sg)
     if cuts[0]<root<cuts[1]:cuts.insert(1,root)
    integral=sum(((b-a)*(terminal(a)+4*terminal((a+b)/2)+terminal(b))/6 for a,b in zip(cuts,cuts[1:])),F(0))*16
    xnp=np.array([list(map(float,x))]);ai=I.point([float(a)]);v=o.terminal_expectation(I.point(xnp),ai)
    self.assertLessEqual(F(float(v.lo[0])),integral);self.assertGreaterEqual(F(float(v.hi[0])),integral)
 def test_centered_difference(self):
  for d,p in itertools.product((2,3,4),(1,4)):
   for q in (F(1,8),F(1,2),F(7,8)):
    x=[q]*d;a=F(37,4096);b=F(683,4096);exact=o.exact_q(x,a,p)-o.exact_q(x,b,p)
    diff=o.final_difference(I.point([list(map(float,x))]),I.point([float(a)]),I.point([float(b)]),p)
    self.assertLessEqual(F(float(diff.lo[0])),exact);self.assertGreaterEqual(F(float(diff.hi[0])),exact)
 def test_derivative_convex(self):
  for d,p in itertools.product((2,3,4),(1,4)):
   x=[F(3,16)]*d;der=[o.exact_q(x,F(i,64),p,True) for i in range(17)]
   for a,b in zip(der,der[1:]):self.assertGreaterEqual(b-a,F(2*p,64))
   for i in (0,3,16):
    v=o.final_derivative(I.point([list(map(float,x))]),I.point([i/64]),p)
    self.assertLessEqual(F(float(v.lo[0])),der[i]);self.assertGreaterEqual(F(float(v.hi[0])),der[i])
 def test_integer_optimizer(self):
  for d in (2,3,4):
   bins=np.array([[31]*d,[127]*d,[239]*d]);counts={};a=o.proposal(bins,8,1,counts)
   for row,aa in zip(bins,a):
    x=[F(2*int(b)+1,512) for b in row];cap=(o.QUANTUM*(256*d+sum(row)))//(8*d*256)
    j=int(round(aa*o.QUANTUM));q=o.exact_q(x,F(j,o.QUANTUM),1)
    for k in set([0,int(cap),max(0,j-1),min(int(cap),j+1)]):self.assertLessEqual(q,o.exact_q(x,F(k,o.QUANTUM),1))
 def test_gate_all_corners_and_interior(self):
  payload=o.s.rung(4,2,1,2,1,'compiled-witness');pi=o.AcquiredPolicy(payload)
  bins=np.array(list(itertools.product((0,17,127,211,255),repeat=2)),dtype=np.int64);a,b=pi.cell_actions(1,bins,True)
  for cell,old,new in zip(bins,a,b):
   if old==new:continue
   for offset in itertools.product((F(0),F(1,3),F(1)),repeat=2):
    x=[(F(int(i))+u)/256 for i,u in zip(cell,offset)]
    self.assertLessEqual(o.exact_q(x,F(float(new)),1),o.exact_q(x,F(float(old)),1))
 def test_acquisition_feasibility(self):
  for d in (2,3,4):
   j=o.s.rung(4,1,1,2,1,'compiled-witness',d);pi=o.AcquiredPolicy(j)
   bins=np.array([[0]*d,[255]*d,[17]*d]);base,new=pi.cell_actions(1,bins,True)
   for cell,a,b in zip(bins,base,new):
    cap=F(1,8)+sum(map(int,cell))/F(8*d*256)
    self.assertTrue(F(0)<=F(float(a))<=cap and F(0)<=F(float(b))<=cap)
 def test_finite_budget_plan_is_global(self):
  for d in (2,3,4):
   j=o.plan(d,2,1,F(5));self.assertEqual(j['status'],'planned');self.assertLessEqual(F(j['primitive_bound'])+F(j['arithmetic_reserve']),5)
   a,b,q=map(F,j['coefficients'])
   for N,K,M in itertools.product((4,8,16,32,64),(1,2,4,8,16),(1,2,4,8,16)):
    if a/N+b/K+q/M<=5-F(1,10**8):self.assertLessEqual(j['proxy_queries'],2*(N+1)**d*(K+1)*M)
 def test_failure_is_not_an_allocation(self):
  self.assertEqual(o.plan(4,3,4,F(1,10**6))['status'],'cap-failure')
 def test_surplus_changes_partition(self):
  j=o.surplus_rung(8,2,1,2,1);self.assertGreater(j['nonuniform_date_models'],0);self.assertGreater(j['counts']['surplus_comparisons'],0)
  q=sum((o.BETA**t*F(r['component']) for t,r in enumerate(j['rows'])),F(0))+o.BETA**j['T']*F(j['terminal_width']);self.assertEqual(q,F(j['policy_bound_exact']))
 def test_finite_reference_advantage_identity(self):
  T=3;beta=F(3,4);states=range(3);acts=range(2);noise=[(0,F(1,3)),(1,F(2,3))]
  c=lambda t,x,a:F((x+1)*(a+1)+t,7);nxt=lambda x,a,z:(x+a+z)%3
  base=[[x%2 for x in states] for _ in range(T)]
  V=[[F(0)]*3 for _ in range(T)]+[[F(x*x,3) for x in states]]
  for t in reversed(range(T)):
   for x in states:V[t][x]=c(t,x,base[t][x])+beta*sum(w*V[t+1][nxt(x,base[t][x],z)] for z,w in noise)
  new=[];advantages=[]
  for t in range(T):
   row=[];adv=[]
   for x in states:
    qs=[c(t,x,a)+beta*sum(w*V[t+1][nxt(x,a,z)] for z,w in noise) for a in acts];a=min(acts,key=lambda a:(qs[a],a));row.append(a);adv.append(qs[a]-V[t][x])
   new.append(row);advantages.append(adv)
  for initial in states:
   true=F(0);tel=F(0)
   for zz in itertools.product((0,1),repeat=T):
    prob=F(1);x=initial;cost=F(0);ad=F(0)
    for t,z in enumerate(zz):
     prob*=noise[z][1];a=new[t][x];cost+=beta**t*c(t,x,a);ad+=beta**t*advantages[t][x];x=nxt(x,a,z)
    cost+=beta**T*V[T][x];true+=prob*cost;tel+=prob*ad
   self.assertEqual(true-V[0][initial],tel);self.assertLessEqual(true,V[0][initial])
 def test_robust_cell_gate_not_center_test(self):
  # Direct difference enclosure must cover all true states in the observed cell.
  x=I([[.25,.5]],[[.25+1/256,.5+1/256]]);a=I.point([.0625]);b=I.point([.125]);v=o.final_difference(x,a,b,4)
  for xx in itertools.product((F(1,4),F(1,4)+F(1,256)),(F(1,2),F(1,2)+F(1,256))):
   q=o.exact_q(xx,F(1,16),4)-o.exact_q(xx,F(1,8),4);self.assertLessEqual(F(float(v.lo[0])),q);self.assertGreaterEqual(F(float(v.hi[0])),q)
 def test_zero_action_change_encloses_zero(self):
  v=o.final_difference(I([[0,0]],[[1,1]]),I.point([.125]),I.point([.125]),1);self.assertLessEqual(v.lo[0],0);self.assertGreaterEqual(v.hi[0],0)
 def test_catalogue_safety_and_price_regret(self):
  low=[F(0),F(-2,10),F(1,10)];high=[F(0),F(-1,10),F(3,10)];work=[1,3,2]
  for gamma in (F(0),F(1,10),F(2)):
   upper=[h+gamma*w for h,w in zip(high,work)];lower=[l+gamma*w for l,w in zip(low,work)];pick=min(range(3),key=lambda j:upper[j])
   for truth in itertools.product(*[list({a,b}) for a,b in zip(low,high)]):
    net=[v+gamma*w for v,w in zip(truth,work)];self.assertLessEqual(net[pick]-min(net),upper[pick]-min(lower))
 def test_statistical_family(self):
  import math
  self.assertGreater(sum((F(13)**j/math.factorial(j) for j in range(50)),F(0)),F(4*512)/F(1,100))

if __name__=='__main__':unittest.main(verbosity=2)
