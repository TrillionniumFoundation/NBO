"""Exact structural controls, including an online minimum-intervention guard.
These comparators exploit the same exogenous-transition model information.
They are added after the first cover diagnostics; no candidate is retuned.
"""
import json,time
from fractions import Fraction as F
import adaptive as a
OUT=a.REV/'results/adaptive'

def optimal(c,x):return int(a.val(c,x)>=0)
def guard(c,x,raw,eta=a.ETA):return raw if (1-2*raw)*a.val(c,x)<=eta else 1-raw

def main():
 rows=[]
 for model,c in a.MODELS.items():
  start=time.perf_counter();answers=[optimal(c,F(2*i+1,2**21)) for i in range(10000)]
  sec=time.perf_counter()-start
  assert all((2*z-1)*a.val(c,F(2*i+1,2**21))>=0 for i,z in enumerate(answers))
  rows.append({'model':model,'method':'exact_symbolic_sign','uniform_regret':'0',
   'representation':'a(x)=1{f(x)>=0}, exact rational Horner evaluation at deployment',
   'polynomial_degree':len(c)-1,'queried_states':10000,'evaluation_seconds':sec,
   'all_state_proof':'continuation is action independent; chosen action maximizes primitive reward',
   'benchmark_scope':'structural proof, not a scan of all grid states'})
  rows.append({'model':model,'method':'online_exact_budget_guard','uniform_regret_upper':str(a.EPS),
   'representation':'retain raw if (1-2*raw)*f(x)<=eta; switch otherwise',
   'optimality_scope':'minimum nonnegative weighted intervention cost within local-loss <=eta class; action-independent occupancy',
   'extra_cost_relative_to_local_minimum':'0',
   'deployment_work':'raw-policy evaluation plus one exact polynomial comparison per queried state',
   'offline_cost':'no region construction required; model identity and exact evaluator must still be validated'})
 a.save(OUT/'structural_controls.json',rows)
if __name__=='__main__':main()
