"""Separate rational original-economy evaluation for R124 chosen policies.

The independent94 primitive is unchanged. New R124 validation effort is fixed
at16 terminal bisections and8 whole-support cells initially, with32/128 cells
for every unresolved accepted claim. A failed gap assertion aborts and keeps
all partial witnesses. No production solver, model, NumPy or SciPy is imported.
"""
import argparse,sys,json
from fractions import Fraction as F
from common124 import *


def run(primary,output):
 out,tick,info=start(output,'independent-original-economic-evaluation')
 try:
  verify_source();boundaries();states();data=rows(Path(primary)/'records124.jsonl')
  if len(data)!=58*2*N:raise ValueError('Complete R124 primary required')
  sys.path.insert(0,str(R123/'vendor/2026-10-20-r121/code121'))
  import exact121 as ex
  ex.TERMINAL_STEPS=16
  ir,primitive=ex.load_primitives();cache={};identities={};claims=[]
  def action_key(row,action):return ex.key(row['state'],action,row['alpha'])
  for row in data:
   values=[row['action'],row['baseline_action']]
   if row['raw_proposal_kept'] is not None:values.append(row['raw_proposal_kept'])
   values += [r['original_action'] for r in row['initial_support_certificates']]
   for a in values:
    k=action_key(row,a);identities.setdefault(k,dict(x=list(map(F,row['state'])),a=F(a),alpha=F(row['alpha'])))
  ordered=sorted(identities)
  write(out/'PLAN124.json',dict(primary_sha256=digest(Path(primary)/'records124.jsonl'),
   unique_action_keys=len(ordered),initial_bins=8,accepted_claim_ladder=[32,128],terminal_bisections=16,
   ordered_keys=ordered,independent_primitive=primitive,validation_cache_does_not_change_service_cost_or_population_weight=True))
  def evaluate(k,bins):
   ck=(k,bins)
   if ck not in cache:
    ex.BINS=bins;kid=ex.key_id(k);trace=ex.ExactTrace(out/'witnesses'/f'{kid}-{bins}.jsonl.gz')
    try:answer=ex.evaluate_action(ir,k,identities[k],trace)
    finally:trace.close()
    cache[ck]=answer
    append(out/'evaluations124.jsonl',answer)
   return cache[ck]
  (out/'witnesses').mkdir()
  def best(k):
   found=[r for (kk,_),r in cache.items() if kk==k]
   fields=('q_lower','q_upper','j_lower','j_upper','optimum_lower')
   b={f:(max if f.endswith('lower') else min)(r[f] for r in found) for f in fields}
   if b['j_lower']>b['j_upper']:raise AssertionError('Independent valid bounds contradict')
   return b
  for j,k in enumerate(ordered):
   evaluate(k,8)
   if j%10==0:print(json.dumps(dict(stage='initial',completed=j+1,total=len(ordered))),flush=True)
  for j,row in enumerate(data):
   if not row['accepted_improvement']:continue
   ka,kb=action_key(row,row['baseline_action']),action_key(row,row['action'])
   def inspect():
    a,b=best(ka),best(kb);gain_lo=a['j_lower']-b['j_upper'];gain_hi=a['j_upper']-b['j_lower']
    certified=F(row['certified_policy_gain_lower'])
    if gain_hi<certified:raise AssertionError('Independent economics contradict certified gain')
    return dict(gain_lower=gain_lo,gain_upper=gain_hi,
     claimed_gain_confirmed=gain_lo>=certified,
     candidate_interval_contained=b['j_lower']>=F(row['complete_policy_lower']) and b['j_upper']<=F(row['complete_policy_upper']),
     independent_positive=gain_lo>0,claimed_gain=certified)
   verdict=inspect();levels=[]
   for bins in (32,128):
    if verdict['claimed_gain_confirmed'] and verdict['candidate_interval_contained']:break
    evaluate(ka,bins);evaluate(kb,bins);levels.append(bins);verdict=inspect()
   claim=dict(key=[row[k] for k in ('index','budget','arm','training_loss','mode','row')],
    baseline_key_id=ex.key_id(ka),candidate_key_id=ex.key_id(kb),levels=levels,**verdict)
   append(out/'claims124.jsonl',claim);claims.append(claim)
   if len(claims)%10==0:print(json.dumps(dict(stage='claims',checked=len(claims),primary_row=j)),flush=True)
  for k in ordered:
   append(out/'action_bounds124.jsonl',dict(key=k,key_id=ex.key_id(k),state=[float(v) for v in identities[k]['x']],action=float(identities[k]['a']),alpha=float(identities[k]['alpha']),
    raw_initial=cache[(k,8)],best=best(k),bins_performed=sorted(b for kk,b in cache if kk==k)))
  finish(out,tick,info,primary_sha256=digest(Path(primary)/'records124.jsonl'),unique_original_actions=len(ordered),
   action_mesh_evaluations=len(cache),accepted_changes=len(claims),
   claimed_gains_confirmed=sum(c['claimed_gain_confirmed'] for c in claims),
   candidate_intervals_contained=sum(c['candidate_interval_contained'] for c in claims),
   unresolved_claim_checks=sum(not(c['claimed_gain_confirmed'] and c['candidate_interval_contained']) for c in claims),
   counts=ex.COUNTS,terminal_bisections=16,initial_bins=8,claim_ladder=[32,128],
   unchanged_future_controller_allowance_added_once=True,rounded_terminal_controller_not_independently_replayed=True)
 except BaseException:fail(out,tick);raise

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--primary',required=True);p.add_argument('--output',required=True);a=p.parse_args();run(a.primary,a.output)
