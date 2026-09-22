"""Re-execute certificate arithmetic without retraining or overwriting evidence.
Recomputes all original policies and fitted uppers, the restricted dual, all
absolute lower references, and the interval derivatives of actual neural weights.
The retained scalar action tree is checked separately by the action routine.
"""
from __future__ import annotations
import contextlib,io,json,pathlib,shutil,tempfile,time
ROOT=pathlib.Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-22-r9';OUT=REV/'results'

def run():
 import original_policy_certificate as pol,certify_upper as up,restricted_dual as dual,absolute_lower as absolute,neural_jet as jet,action_certificate as action
 log=io.StringIO();rows=[];start=time.perf_counter()
 with tempfile.TemporaryDirectory(prefix='nbo-r9-cert-') as tmp:
  dest=pathlib.Path(tmp)
  for p in OUT.glob('*.json'):shutil.copy2(p,dest/p.name)
  pol.OUT=up.OUT=dual.OUT=absolute.OUT=jet.OUT=dest
  with contextlib.redirect_stdout(log):
   pol.iv.dps=70
   for tag in ['k0.5','k2','k8','restricted']:
    new=pol.run(tag);old=json.loads((OUT/f'policy_certificate_{tag}.json').read_text())
    lo,hi=new['records'][-1]['policy_value_interval'];olo,ohi=old['records'][-1]['policy_value_interval']
    assert max(abs(lo-olo),abs(hi-ohi))<1e-10
    rows.append({'certificate':'policy_'+tag,'passed':True,'value_interval':[lo,hi]})
   for k in [.5,2.,8.]:
    new=up.run(k);old=json.loads((OUT/f'upper_certificate_k{k:g}.json').read_text())
    assert abs(new['reports'][-1]['upper_value_initial']-old['reports'][-1]['upper_value_initial'])<1e-10
    rows.append({'certificate':f'upper_{k:g}','passed':True,'upper':new['reports'][-1]['upper_value_initial']})
   new=dual.run();old=json.loads((OUT/'restricted_dual_certificate.json').read_text())
   assert abs(new['records'][-1]['restricted_optimal_value_upper']-old['records'][-1]['restricted_optimal_value_upper'])<1e-10
   rows.append({'certificate':'restricted_dual','passed':True,'upper':new['records'][-1]['restricted_optimal_value_upper']})
   absolute.iv.dps=50
   for d in [8,16,32]:
    new=absolute.run(d);old=json.loads((OUT/f'absolute_lower_d{d}.json').read_text())
    assert abs(new['records'][-1]['lower_bound']-old['records'][-1]['lower_bound'])<1e-10
    rows.append({'certificate':f'absolute_lower_{d}','passed':True,'lower':new['records'][-1]['lower_bound']})
   action.iv.dps=50
   import numpy as np
   stored=json.loads((OUT/'action_certificates.json').read_text())
   for a in stored:
    rec=action.certify(np.array(a['gradient']),a['tolerance'])
    assert rec['gap']<=a['tolerance'] and rec['meets_tolerance']
    rows.append({'certificate':f"continuous_action_d{a['dimension']}_tol{a['tolerance']}",'passed':True,'gap':rec['gap']})
   jet.iv.dps=60
   j=jet.run()
   assert all(a['true_neural_action_gap_upper']<=a['tolerance'] for r in j for a in r['action_certificates'])
   rows.append({'certificate':'actual_neural_jets','passed':True,'dimensions':[r['dimension'] for r in j]})
 (REV/'build_logs/certificate-recheck.txt').write_text(log.getvalue())
 result={'status':'PASS','seconds':time.perf_counter()-start,'checks':rows,'scope':'Re-executed certificate arithmetic on frozen inputs, not retraining; endpoint agreement tolerance 1e-10 does not replace outward verification inside each routine.'}
 (REV/'certificate_recheck.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result
if __name__=='__main__':run()
