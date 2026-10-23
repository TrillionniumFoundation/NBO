"""Fresh independent rational original-economy evaluation for B only.

No A economic cache, production solver, fitted model or optimizer is read.
Every original future-cost enclosure uses the unchanged independent94
primitive, fixed16 terminal bisections and the frozen8/32/128 risk ladder.
"""
import argparse,sys,json
from fractions import Fraction as F
from common124b import *

def declared_claims(data):
 claims=[]
 for r in data:
  k=[r[f] for f in ('index','budget','arm','training_loss','mode','row')]
  if F(r['certified_policy_gain_lower'])>0:
   claims.append(dict(key=k,comparison='own-stage',origin=r['stage_incumbent_action'],candidate=r['action'],
    claimed_gain=F(r['certified_policy_gain_lower']),row=r))
  if r['mode']=='joint' and F(r['certified_gain_vs_fused_lower'])>0:
   claims.append(dict(key=k,comparison='joint-vs-fused',origin=r['fused_action'],candidate=r['action'],
    claimed_gain=F(r['certified_gain_vs_fused_lower']),row=r))
 return claims
def run(primary,output):
 out,tick,info=start(output,'B-independent-original-economic-evaluation')
 try:
  verify_source();boundaries();states();data=rows(Path(primary)/RECORDS)
  if len(data)!=58*3*N:raise ValueError('Complete B primary required')
  sys.path.insert(0,str(R123/'vendor/2026-10-20-r121/code121'));import exact121 as ex
  ex.TERMINAL_STEPS=16;ir,primitive=ex.load_primitives();cache={};identities={};claims=[]
  def action_key(row,action):return ex.key(row['state'],action,row['alpha'])
  for r in data:
   values=[r[k] for k in ('action','stage_incumbent_action','original_incumbent_action','fused_action','bridge_action')]
   if r['raw_proposal_kept'] is not None:values.append(r['raw_proposal_kept'])
   values += [p['original_action'] for p in r['full_fused_record']['initial_support_certificates']]
   for a in values:
    k=action_key(r,a);identities.setdefault(k,dict(x=list(map(F,r['state'])),a=F(a),alpha=F(r['alpha'])))
  ordered=sorted(identities);planned=declared_claims(data)
  write(out/'PLAN124B.json',dict(primary_sha256=digest(Path(primary)/RECORDS),unique_action_keys=len(ordered),initial_bins=8,
   accepted_claim_ladder=[32,128],terminal_bisections=16,ordered_keys=ordered,independent_primitive=primitive,
   declared_claims=[{k:c[k] for k in ('key','comparison','origin','candidate','claimed_gain')} for c in planned],
   no_A_cache_read=True,validation_cache_does_not_change_service_cost_or_population_weight=True))
  (out/'witnesses').mkdir()
  def evaluate(k,bins):
   ck=(k,bins)
   if ck not in cache:
    ex.BINS=bins;trace=ex.ExactTrace(out/'witnesses'/f'{ex.key_id(k)}-{bins}.jsonl.gz')
    try:answer=ex.evaluate_action(ir,k,identities[k],trace)
    finally:trace.close()
    cache[ck]=answer;append(out/'evaluations124b.jsonl',answer)
   return cache[ck]
  def best(k):
   found=[v for (kk,_),v in cache.items() if kk==k];fields=('q_lower','q_upper','j_lower','j_upper','optimum_lower')
   b={f:(max if f.endswith('lower') else min)(r[f] for r in found) for f in fields}
   if b['j_lower']>b['j_upper']:raise AssertionError('Independent valid B enclosures contradict')
   return b
  for j,k in enumerate(ordered):
   evaluate(k,8)
   if j%10==0:print(json.dumps(dict(stage='initial',completed=j+1,total=len(ordered))),flush=True)
  for j,c in enumerate(planned):
   row=c['row'];ka,kb=action_key(row,c['origin']),action_key(row,c['candidate'])
   def inspect():
    a,b=best(ka),best(kb);lo=a['j_lower']-b['j_upper'];hi=a['j_upper']-b['j_lower']
    if hi<c['claimed_gain']:raise AssertionError('Independent B economics contradict a certified original-policy gain')
    return dict(gain_lower=lo,gain_upper=hi,claimed_gain_confirmed=lo>=c['claimed_gain'],independent_positive=lo>0,
     candidate_interval_contained=b['j_lower']>=F(row['complete_policy_lower']) and b['j_upper']<=F(row['complete_policy_upper']),claimed_gain=c['claimed_gain'])
   verdict=inspect();levels=[]
   for bins in (32,128):
    if verdict['claimed_gain_confirmed'] and verdict['candidate_interval_contained']:break
    evaluate(ka,bins);evaluate(kb,bins);levels.append(bins);verdict=inspect()
   claim=dict(key=c['key'],comparison=c['comparison'],baseline_key_id=ex.key_id(ka),candidate_key_id=ex.key_id(kb),levels=levels,**verdict)
   append(out/'claims124b.jsonl',claim);claims.append(claim)
   if (j+1)%10==0:print(json.dumps(dict(stage='claims',checked=j+1,total=len(planned))),flush=True)
  for k in ordered:
   append(out/'action_bounds124b.jsonl',dict(key=k,key_id=ex.key_id(k),state=[float(v) for v in identities[k]['x']],action=float(identities[k]['a']),alpha=float(identities[k]['alpha']),
    raw_initial=cache[(k,8)],best=best(k),bins_performed=sorted(b for kk,b in cache if kk==k)))
  finish(out,tick,info,primary_sha256=digest(Path(primary)/RECORDS),unique_original_actions=len(ordered),action_mesh_evaluations=len(cache),
   accepted_claims=len(claims),own_stage_claims=sum(c['comparison']=='own-stage' for c in claims),cumulative_joint_vs_fused_claims=sum(c['comparison']=='joint-vs-fused' for c in claims),
   claimed_gains_confirmed=sum(c['claimed_gain_confirmed'] for c in claims),candidate_intervals_contained=sum(c['candidate_interval_contained'] for c in claims),
   unresolved_claim_checks=sum(not(c['claimed_gain_confirmed'] and c['candidate_interval_contained']) for c in claims),
   counts=ex.COUNTS,terminal_bisections=16,initial_bins=8,claim_ladder=[32,128],no_A_cache_read=True,
   unchanged_future_controller_allowance_added_once=True,rounded_terminal_controller_not_independently_replayed=True)
 except BaseException:fail(out,tick);raise
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--primary',required=True);p.add_argument('--output',required=True);a=p.parse_args();run(a.primary,a.output)
