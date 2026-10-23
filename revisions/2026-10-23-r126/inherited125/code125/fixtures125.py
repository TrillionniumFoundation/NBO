"""Exact rational boundary, support-retention, and strict-action witnesses."""
import argparse
from common125 import *
from support125 import *

def run(output):
 out,tick,info=start(output,'exact-rational-mathematical-fixtures')
 try:
  source=verify_inputs();n=0;tests=[]
  # A=1, mu=1,L=2; h=q-x^2/2. Same paid value/derivative boxes.
  ns_reduced=[(F(0),F(0),F(-1,4)),(F(1,2),F(-1,8),F(-1,4)),(F(1),F(-1,4),F(-1,4))]
  ns_full=[(F(0),F(0),F(1,8)),(F(1,2),F(1,16),F(1,8)),(F(1),F(1,8),F(1,8))]
  support=[(F(1,2),F(0),F(1),F(1),F(1))]
  reduced=verify_interpolation(1,1,2,ns_reduced,[])
  rejected=verify_interpolation(1,1,2,ns_reduced,support)
  full=verify_interpolation(1,1,2,ns_full,support)
  assert reduced['feasible'] and not rejected['feasible'] and full['feasible'];n+=3
  # q(0)=0,q(1/2)>=0 imply q(1)>=1/4 by strong convexity.
  # The original paid support at x=1 gives q(1)>=5/8, with equality
  # for q_full=x^2/2+x/8. Both endpoint extrema have exact witnesses.
  reduced_upper=F(-1,4);full_upper=F(-5,8)
  assert full_upper<reduced_upper and reduced_upper-full_upper==F(3,8);n+=1
  assert F(1,2)+F(-1,4)==-reduced_upper and F(1,2)+F(1,8)==-full_upper;n+=2
  tests.append(dict(name='strict-original-action-contrast-versus-omitted-support',reduced=reduced,rejected_reduced=rejected,full=full,reduced_upper_contrast=reduced_upper,full_upper_contrast=full_upper,additional_certified_gain=F(3,8),comparison_scope='omitting a paid raw support; cheap direct support evaluation attains the same endpoint bound; no neural-specific or computational dominance claim'))
  # All stored-node support tests pass, but the omitted interior violates
  # the affine obstacle. The Phi constraint detects the inconsistency.
  bad_nodes=[(F(0),F(0),F(-1,2)),(F(1,4),F(-3,32),F(-1,4)),(F(1),F(0),F(1,2))]
  bad_support=[(F(1,4),F(-5,64),F(1,4),F(1,4),F(1,4))]
  assert verify_interpolation(1,1,2,bad_nodes,[])['feasible'];n+=1
  assert all(f+F(7,64)>=0 for x,f,g in bad_nodes);n+=1
  rejected_interior=verify_interpolation(1,1,2,bad_nodes,bad_support)
  assert not rejected_interior['feasible'];n+=1
  assert F(-1,8)<F(-7,64);n+=1
  tests.append(dict(name='stored-node-tests-miss-interior-support-violation',check=rejected_interior,interior_violation=F(1,64),scope='deliberately inconsistent mathematical payload, not admissible economic data'))
  for K in (F(0),F(1),F(3)):
   for v in (F(-2),F(-1,3),F(0),F(1,3),F(2)):
    for l,u in ((F(-1),F(1)),(F(0),F(1)),(F(-1),F(0))):
     value,t=phi(K,v,l,u)
     assert l<=t<=u;n+=1
     for s in (l,(2*l+u)/3,(l+2*u)/3,u):assert value>=v*s-K*s*s/2;n+=1
  # Nonstationary exact dual point: min_{[-1,2]} z is -1.
  dual=residual_lower_bound([1],[F(3,2)],[],[],[],[-1],[2]);assert dual==-1;n+=1
  tests.append(dict(name='box-residual-dual-correction',exact_bound=dual))
  from service125 import update_bracket
  for optimum in (F(0),F(1,4),F(1,2),F(3,4),F(1)):
   lo,hi=F(0),F(1)
   for j in range(6):
    a=(lo+hi)/2;width=hi-lo;g=2*(a-optimum);e=width/4
    nl,nh=update_bracket(lo,hi,a,g-e,g+e)
    assert nl<=optimum<=nh and nh-nl<=width/2;n+=1;lo,hi=nl,nh
  tests.append(dict(name='constrained-original-gradient-bracket-boundaries',quadratic_cases=5,steps_each=6))
  write(out/'FIXTURES125.json',dict(checks=n,tests=tests,source=source,economic_outcomes=False))
  finish(out,tick,checks=n,source=source,exact_rational=True,economic_outcomes=False)
 except BaseException:fail(out,tick);raise
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();run(a.output)
