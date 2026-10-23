"""Analytic engineering fixture only; no investment state or population unit."""
import argparse,copy,sys,time
from fractions import Fraction as F
from common124 import ROOT,R123,write,serial,Path
sys.path.insert(0,str(R123/'code123'))
import envelope123 as env
import joint124 as joint
from verify124 import RationalCertificate,checked_dual

def main(destination):
 tick=time.perf_counter()
 case=dict(A=F(1),incumbent=F(0),mu=F(1),L=F(2),delta=F(0),tau=F(1),omega=F(1),old_optimum_lower=F(-1),
  payloads=[dict(a=F(0),W=F(0),U=F(0),p_lower=F(-1,2),p_upper=F(-1,2),g_lower=F(-1,2),g_upper=F(-1,2)),
  dict(a=F(1),W=F(3,16),U=F(3,16),p_lower=F(1),p_upper=F(1),g_lower=F(1),g_upper=F(1))])
 case=env.normalize(case);b=F(3,8);p=joint.problem(case,b)
 point=[F(0),F(-5,64),F(3,16),F(-1,2),F(0),F(1)]
 lam=[F(0),F(1,2),F(0),F(0),F(1,2),F(0),F(0),F(0)]
 witness=dict(problem=p,point=point,multipliers=lam,dual=joint.exact_bound(p,point,lam))
 assert witness['dual']['contrast_upper']==F(-5,64)
 engine=RationalCertificate(case)
 assert checked_dual(engine,b,serial(witness))==F(-5,64)
 proposed=joint.solve(case,b);upper=checked_dual(engine,b,serial(proposed))
 assert F(-5,64)<=upper<F(-1,16)
 # The compatible piecewise derivative is integrated exactly and attains both
 # observed endpoint levels plus the sharp interior value.
 def hv(x):
  if x<=F(1,8):return x*x/2
  if x<=F(5,8):return F(1,128)+(x-F(1,8))/8
  return F(9,128)+(x*x-F(25,64))/2-(x-F(5,8))/2
 q=lambda x:hv(x)+x*x/2-x/2
 assert q(F(0))==0 and q(b)==F(-5,64) and q(F(1))==F(3,16)
 rejected=[]
 for mutation in ('negative-multiplier','forged-bound','wrong-box'):
  bad=serial(copy.deepcopy(witness))
  if mutation=='negative-multiplier':bad['multipliers'][1]='-1'
  elif mutation=='forged-bound':bad['dual']['contrast_upper']='-1'
  else:bad['problem']['upper'][1]='0'
  try:checked_dual(engine,b,bad)
  except (AssertionError,ValueError):rejected.append(mutation)
  else:raise AssertionError('Tampered certificate accepted: '+mutation)
 result=dict(status='passed',kind='analytic engineering diagnostic',original_economic_outcomes=0,population_units=0,
  exact_sharp_upper=str(F(-5,64)),old_best_guarantee=str(F(-1,16)),strict_gain_increment=str(F(1,64)),
  hand_dual=serial(witness),solver_proposal=serial(proposed),rejected_mutations=rejected,seconds=time.perf_counter()-tick)
 write(Path(destination),result)
 print(serial({k:v for k,v in result.items() if k not in ('hand_dual','solver_proposal')}))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--output',default=str(ROOT/'provenance124/ANALYTIC_FIXTURE124.json'));main(parser.parse_args().output)
