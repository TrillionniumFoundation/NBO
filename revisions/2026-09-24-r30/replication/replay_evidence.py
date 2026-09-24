"""Reconstruct verbose exact records from frozen candidates and observations.
No training or timing observation is repeated or relabeled. Hashes check that
replayed scientific records equal the original local execution byte for byte.
"""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib
import adaptive as a
import economics as e
OUT=a.REV/'results/adaptive'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 observations=read(OUT/'frozen_observations.json');rows=[]
 for obs in observations:
  tag=obs['tag'];payload=read(OUT/'candidates'/f'{tag}.json');c=a.MODELS[obs['model']]
  s,p=a.compile_nn(payload['params']);a.save(OUT/'compiled'/f'{tag}.json',{'segments':s,'points':[[x,b] for x,b in p.items()]})
  cert=a.complete(c,s,p);a.save(OUT/'certificates'/f'{tag}.json',cert)
  row=dict(obs,**a.verify(c,cert),**a.raw_regret(c,s,p))
  expected=row.pop('original_row_sha256');assert a.digest(row)==expected,tag
  assert (OUT/'certificates'/f'{tag}.json').stat().st_size==row['certificate_bytes']
  assert a.digest(cert)==row['certificate_sha256'];rows.append(row)
 a.save(OUT/'summary.json',rows)
 for model,c in a.MODELS.items():
  for label,raw,tol in [('constant0',0,a.ETA),('constant1',1,a.ETA),('structured_matched',0,a.ETA),('structured_near_exact',0,F(1,10**12))]:
   s,p=a.constant(raw);cert=a.complete(c,s,p,tol);a.save(OUT/'baselines'/f'{model}_{label}.json',cert)
  payload=read(OUT/'candidates'/f'{model}_polynomial.json');coeff=list(map(F,payload['coefficients']))
  s,p=e.compile_polynomial(coeff);a.save(OUT/'compiled'/f'{model}_polynomial.json',{'segments':s,'points':[[x,b] for x,b in p.items()]})
  cert=a.complete(c,s,p);a.save(OUT/'certificates'/f'{model}_polynomial.json',cert)
 economic=[]
 for row in rows:
  tag=row['tag'];c=a.MODELS[row['model']];raw=e.decode_segments(OUT/'compiled'/f'{tag}.json')
  completed=e.policy_segments(read(OUT/'certificates'/f'{tag}.json'))
  reference=e.policy_segments(read(OUT/'baselines'/f"{row['model']}_structured_near_exact.json"))
  cr=e.overlay_cost(raw,reference);cc=e.overlay_cost(raw,completed)
  welfare=e.mean_reward(c,reference)-e.mean_reward(c,completed);saved=cr-cc
  economic.append({'tag':tag,'reference_priority_cost':str(cr),'completion_priority_cost':str(cc),
   'saved_priority_cost':str(saved),'reference_minus_completion_payoff':str(welfare),
   'break_even_revision_price':str(welfare/saved) if saved>0 else None,
   'net_advantage_at_price_1_20':str(F(1,20)*saved-welfare),
   'comparison':'same raw incumbent; structure-aware reference certified within H*1e-12; no CPU shadow price assumed'})
 a.save(OUT/'economic_comparisons.json',economic)
 files=[*list((OUT/'compiled').glob('*.json')),*list((OUT/'certificates').glob('*.json')),*list((OUT/'baselines').glob('*.json')),OUT/'summary.json',OUT/'economic_comparisons.json']
 hashes={str(p.relative_to(a.REV)):sha(p) for p in files}
 expected=read(a.REV/'results/REPLAY_EXPECTED_SHA256.json')
 assert len(hashes)==expected['files']
 aggregate=hashlib.sha256(json.dumps(hashes,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 assert aggregate==expected['aggregate_sha256'],(aggregate,expected)
 print('Replayed 60 frozen neural candidates, 3 polynomial candidates and exact economic records; all original hashes match.')
if __name__=='__main__':main()
