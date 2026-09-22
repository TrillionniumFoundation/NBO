"""Mathematical cross-checks and evidence failure tests; no acceptance by assertion."""
from __future__ import annotations
import hashlib,json,os,pathlib,tempfile
import numpy as np
from scipy.integrate import solve_ivp
import accuracy
ROOT=accuracy.ROOT;REV=accuracy.REV

def run():
 checks=[]
 for case in accuracy.inputs():
  ref,_=accuracy.reference(case);value=0.
  for j in range(case['d']):
   a,b,q,r,s,w,x=[case[k][j] for k in ['a','b','q','r','sigma','terminal_weight','initial_centered']]
   sol=solve_ivp(lambda t,z:[q+2*a*z[0]-b*b*z[0]*z[0]/r,z[0]],(0.,1.),[w,0.],rtol=2e-12,atol=2e-14)
   assert sol.success;value+=sol.y[0,-1]*x*x+s*s*sol.y[1,-1]
  assert abs(value/case['d']-float(ref.mid))<2e-10
  g=accuracy.improve(case,32);c=accuracy.certificate(case,g)
  changed=g.copy();changed[0,0]+=.3;p=accuracy.certificate(case,changed)
  assert p['policy_sha256']!=c['policy_sha256'] and p['policy_cost'][0]>c['policy_cost'][1]
  bad=g.copy();bad[0,0]=np.nan
  try:accuracy.certificate(case,bad)
  except AssertionError:pass
  else:raise AssertionError('Nonfinite policy accepted')
  checks.append({'test':'independent_Riccati_ODE_and_policy_mutation','case':case['name'],'status':'PASS'})
 tracking=accuracy.inputs()[0];ref,_=accuracy.reference(tracking)
 analytic=.25/5+tracking['sigma'][0]**2*np.log(5)/4
 assert abs(analytic-float(ref.mid))<2e-15
 checks.append({'test':'tracking_closed_form','status':'PASS'})
 protocol=json.loads((REV/'protocol.json').read_text());assert not set(protocol['external']['holdout_seeds'])&set(range(720,732))
 # The failure-preserving collector must publish an invalid aggregate even with no artifacts.
 import robustness
 os.environ.setdefault('R11_SOURCE_COMMIT','test-missing-cell-input')
 with tempfile.TemporaryDirectory() as td:
  base=pathlib.Path(td);s=robustness.collect(base/'empty',base/'out')
  assert s['status']=='FAIL' and len(s['planned_cells'])==3 and (base/'out/summary.json').is_file()
 checks.append({'test':'all_missing_cells_preserved_as_invalid','status':'PASS'})
 for k in ['0.5','2','8']:
  p=REV/f'results/original_recheck/k{k}/flexible_dual_k{k}.json'
  old=ROOT/f'revisions/2026-09-22-r10/results/flexible_dual_k{k}.json'
  x=json.loads(p.read_text())['records'][-1];y=json.loads(old.read_text())['records'][-1]
  assert x['target_met'] and abs(x['certified_regret_upper']-y['certified_regret_upper'])<1e-13
 checks.append({'test':'all_three_original_economy_certificates_reproduced','status':'PASS'})
 # Frozen gains must reproduce every canonical interval and policy digest.
 summary=json.loads((REV/'results/accuracy/summary.json').read_text());cases={c['name']:c for c in accuracy.inputs()}
 for r in summary['rows']:
  name=(f"bellman_N{r['slabs']}" if r['method']=='quadratic_Bellman' else f"adam_{r['updates']}")
  gains=np.array(json.loads((REV/f"results/accuracy/{r['case']}/{name}_gains.json").read_text()))
  check=accuracy.certificate(cases[r['case']],gains)
  assert check['policy_sha256']==r['policy_sha256']
  assert max(abs(np.array(check['absolute_regret'])-r['absolute_regret']))<1e-13
 checks.append({'test':'all_30_stored_policy_certificates_reproduced','status':'PASS','count':len(summary['rows'])})
 result={'status':'PASS','checks':checks,'note':'ODE and torch tolerances are software cross-checks, not the proofs of interval enclosures.'}
 accuracy.dump(REV/'validation_tests.json',result);print(json.dumps(result,indent=2));return result
if __name__=='__main__':run()
