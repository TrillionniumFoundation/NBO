"""Charge the shared envelope's saved initializer without a hidden free oracle.

For N=1 the sole candidate pays for a separate initializer unless its own
construction already includes that same actor-29 hybrid. For N=9 the complete
nine-hybrid comparison includes actor-29 and books its construction once in
the own-construction column. N=100 is explicitly hypothetical and assumes
that initializer is likewise among the costed population. This changes costs
only: no policy, payoff interval, optimal envelope or welfare bound is altered.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1]

def correct():
 p=R/'results/COMMON_ACCOUNTS.json';raw=p.read_bytes();data=json.loads(raw)
 source=ROOT/'revisions/2026-10-03-r8/results/continuous_actor_s29_search.json'
 initial=json.loads(source.read_text())
 seed_cost=initial['training_seconds']+initial['timings']['reference']+initial['timings']['policy_evaluation']
 archive=R/'archive/COMMON_ACCOUNTS_before_cost_correction.json';archive.parent.mkdir(exist_ok=True)
 if not data.get('cost_accounting_correction'):archive.write_bytes(raw)
 changes=[]
 for row in data['records']:
  own=row['training_seconds']+row['original_reference_seconds']+row['original_policy_evaluation_seconds']+row['policy_evaluation_seconds']
  same=(row['method']=='actor' and row['seed']==29)
  extra=0. if same else seed_cost
  totals={str(n):own+data['shared_cover_seconds']/n+(extra if n==1 else 0.) for n in [1,9,100]}
  row['initializer_construction_seconds']=seed_cost
  row['standalone_additional_initializer_seconds']=extra
  row['total_cost_by_number_policies']=totals
  welfare=row['compensation']['seconds'] if row['compensation'] else 0.
  row['total_with_compensation_by_number_policies']={k:v+welfare for k,v in totals.items()}
  row['cost_basis']='R8 archived candidate and initializer construction; pinned R9 cover; separately timed payoff and compensation verification. Mixed provenance, not a same-machine training race.'
  changes.append({'method':row['method'],'seed':row['seed'],'raw':row['raw'],'standalone_extra_seconds':extra})
 data['cost_accounting_correction']={'initializer_source':str(source.relative_to(ROOT)),
  'initializer_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
  'initializer_construction_seconds':seed_cost,
  'N1':'standalone candidate; separately charge the actor-29 hybrid initializer unless already included in this candidate construction',
  'N9':'the complete nine-hybrid comparison includes the actor-29 initializer; its construction is already charged once among own-construction costs',
  'N100':'hypothetical amortization; assumes the initializer is among the costed population, not 100 executed experiments',
  'unchanged':'all policies, raw arrays, payoff and optimal-value bounds, pass flags and compensation percentages'}
 p.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
 record={'scope':'deterministic cost correction only; no numerical policy result changed',
  'before_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'after_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
  'initializer_source_sha256':data['cost_accounting_correction']['initializer_source_sha256'],
  'initializer_construction_seconds':seed_cost,'changes':changes}
 (R/'results/COST_ACCOUNTING_AUDIT.json').write_text(json.dumps(record,indent=2)+'\n')
 return record
if __name__=='__main__':print(json.dumps(correct(),indent=2))
