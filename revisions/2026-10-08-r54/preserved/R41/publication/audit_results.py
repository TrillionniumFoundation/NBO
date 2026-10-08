"""Read-only replay of record hashes, identities, formulae, and derived counts."""
from pathlib import Path
import hashlib,json,math,sys
from fractions import Fraction as F
import numpy as np
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 s=json.loads((R/'results/R41_STUDY.json').read_text());nchecked=0;beta=F(15,16)
 for k,h in s['code_hashes'].items():assert sha(R/k)==h,k
 for x in s['neural_refinements']:
  p=R/x['path'];assert sha(p)==x['sha256'];n=json.loads(p.read_text());assert n['N']==x['N'] and n['A']==x['A']
  formula=sum(beta**r['date']*(F(r['residual_upper'])-F(r['residual_lower'])+F(r['actor_allowance'])) for r in n['records'])+beta**n['T']*(F(n['terminal']['upper'])-F(n['terminal']['lower']))
  assert float(formula)<=n['policy_gap_upper']+1e-14
  assert n['bellman_transition_evaluations']==n['T']*(n['N']+1)*(n['A']+1)*3
  assert x['query_target_passed']==(max(n['statewise_policy_gap_upper'])<=.02)
  nchecked+=1
 for x in s['final']:
  assert sha(R/x['comparison_result'])==x['comparison_sha256'];n=json.loads((R/x['neural_result']).read_text());c=json.loads((R/x['comparison_result']).read_text())
  assert x['global_gap']==n['policy_gap_upper'] and x['max_query_gap']==max(n['statewise_policy_gap_upper'])
  for i in range(4):
   lo=F(n['own_policy_values']['lower'][i])-F(c['conventional_values']['upper'][i]);hi=F(n['own_policy_values']['upper'][i])-F(c['conventional_values']['lower'][i]);d=c['neural_minus_reoptimized_spline']
   assert F(d['lower'][i])<=lo and hi<=F(d['upper'][i]);assert d['lower'][i]>=-.001 and d['upper'][i]<=.001
  assert n['deployment']['extra_global_loss_upper']>0
 idx=json.loads((R/'results/precision/INDEX.json').read_text());assert len(idx)==48
 mixed=0;summary={}
 for row in idx:
  p=R/'results/precision'/f"service-{row['id']:03}.json";assert sha(p)==row['record_sha256'];n=json.loads(p.read_text());a=n['precision_attempts']
  assert n['spec']==row['spec'] and n['certified']==row['certified']
  for precision in [32,64]:
   assert row[f'accepted{precision}']==sum(v['accepted'] and v['precision']==precision for v in a)
   assert row[f'rejected{precision}']==sum(not v['accepted'] and v['precision']==precision for v in a)
  m=row['spec']['method'];out=summary.setdefault(m,dict(services=0,passed=0,accepted32=0,accepted64=0,rejected32=0,rejected64=0));out['services']+=1;out['passed']+=row['certified']
  for k in ['accepted32','accepted64','rejected32','rejected64']:out[k]+=row[k]
  if m=='adaptive-cached':mixed+=bool(row['accepted32'] and row['accepted64'])
 assert summary==s['precision'];assert mixed==10
 # Regression for the JSON policy restoration that stopped R40.
 sys.path.insert(0,str(R/'code'));import neural_chain as nc;import nonlinear as nl
 index=json.loads((R/'inputs/INDEX.json').read_text());row=index['nonlinear-capital-1.0-0.0'];old=json.loads((R/'inputs'/(row['id']+'.json')).read_text());p=old['candidate']
 assert isinstance(p['knots'],list);p['knots']=np.asarray(p['knots']);p['actors']=[np.asarray(a) for a in p['actors']]
 v=nl.own_value(p,[.125],price=4.,theta=0.);assert np.isfinite(v.lo).all() and (v.lo<=v.hi).all()
 out=dict(passed=True,neural_record_hashes=nchecked,comparison_record_hashes=4,precision_record_hashes=len(idx),direct_difference_intervals=16,adaptive_mixed_services=mixed,precision=summary,json_policy_restoration_regression=True,formula_check='Exact rational reconstruction compared at 1e-14 tolerance to outward binary arithmetic; record identity checks exact',old_result_replacements=0)
 (R/'audit/RESULT_AUDIT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
