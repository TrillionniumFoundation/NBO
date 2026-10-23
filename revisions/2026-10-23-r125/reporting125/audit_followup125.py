"""Separately frozen post-primary independent refinement; original audit retained."""
from pathlib import Path
import argparse,gzip,json,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code125'))
from common125 import *
BINS_FOLLOWUP=512
MAX_REQUESTED_CONTEXTS=112750

def decoded(x):
 if isinstance(x,str):
  try:return F(x)
  except ValueError:return x
 if isinstance(x,list):return [decoded(v) for v in x]
 if isinstance(x,dict):return {k:decoded(v) for k,v in x.items()}
 return x

def run(output):
 out,tick,info=start(output,'separately-frozen-post-primary-independent-refinement')
 try:
  original=verify_inputs();m=json.loads((ROOT/'POSTFREEZE_AUDIT_FREEZE125.json').read_text())
  for rel,h in m['files'].items():
   if sha(ROOT/rel)!=h:raise ValueError('Follow-up frozen input mismatch: '+rel)
  boundary=json.loads((ROOT/'POSTFREEZE_AUDIT_BOUNDARY125.json').read_text())
  if not boundary.get('remote_readback_before_new_economics') or len(boundary['source_commit'])!=40 or boundary['manifest_sha256']!=sha(ROOT/'POSTFREEZE_AUDIT_FREEZE125.json'):raise ValueError('Follow-up remote source gate missing')
  from materialize_independent_trace125 import ensure_trace
  transport_identity=ensure_trace(ROOT)
  p=ROOT/'results125';checks=rows(p/'independent/checks125.jsonl');primary=rows(p/'primary/records125.jsonl.gz');oldrows=rows(p/'independent/evaluations125.jsonl.gz')
  previous={r['key_id']:decoded(r) for r in oldrows}
  selected=set()
  for c in checks:
   if not(c['contained'] and c['gain_confirmed']):selected.update((c['final_key'],c['baseline_key']))
  if len(selected)!=110 or len(selected)*(2*BINS_FOLLOWUP+1)>MAX_REQUESTED_CONTEXTS:raise ValueError('Prospective complete refinement set differs')
  write(out/'SELECTION125.json',dict(keys=sorted(selected),unique_actions=len(selected),rule='both actual final and completed-prefix keys for every initial unresolved containment or gain check',post_primary_selection=True,original_checks_sha256=sha(p/'independent/checks125.jsonl')))
  sys.path.insert(0,str(R121/'code121'));import exact121 as ex
  ir,identity=ex.load_primitives();ex.BINS=BINS_FOLLOWUP;ex.TERMINAL_STEPS=32
  # Exact old terminal witnesses are reusable at identical rational state/risk.
  # Nested meshes make old nodes endpoints of the new mesh. No production
  # output is treated as an independent witness.
  terminal_fields=('state','action','lower','upper','polynomial','tail_left','tail_right','threshold','risk_primal','risk_dual','terminal_steps','terminal_steps_field_is_interior_budget','terminal_bisections_executed','exact_boundary_sign_checks_precede_interior_bisection','state_gradient','action_gradient','multiplier_upper','multiplier_lower','stationarity_residual','support_anchor','support_slope')
  cache_tick=time.perf_counter()
  cache={};source_trace=p/'independent/terminal_witnesses125.jsonl.gz';trace_hash=sha(source_trace)
  with gzip.open(source_trace,'rt') as f:
   for line in f:
    row=json.loads(line)
    if row['key_id'] not in selected:continue
    v=decoded({k:row[k] for k in terminal_fields if k in row});alpha=F(previous[row['key_id']]['alpha']);k=(tuple(v['state']),alpha)
    if k in cache:
     assert cache[k]['lower']==v['lower'] and cache[k]['upper']==v['upper'] and cache[k]['action']==v['action']
     ex.count('cached_duplicate_identity_checks')
    if k not in cache or 'support_anchor' in v:
     cache[k]=dict(v,reused_original_trace_sha256=trace_hash,reused_original_sequence=row['sequence'],reused_original_key_id=row['key_id'])
  cache_loading_seconds=time.perf_counter()-cache_tick
  primitive_terminal=ex.terminal
  def terminal(ir,y,alpha,support):
   k=(tuple(y),alpha);v=cache.get(k)
   if v is not None and (not support or 'support_anchor' in v):
    ex.count('reused_independent_terminal_contexts');return v
   return primitive_terminal(ir,y,alpha,support)
  ex.terminal=terminal;trace=ex.ExactTrace(out/'terminal_witnesses125.jsonl.gz');evaluated={}
  try:
   for kid in sorted(selected):
    old=previous[kid];x=tuple(F(float.fromhex(v)) for v in old['state_hex']);a=F(float.fromhex(old['action_hex']));alpha=F(old['alpha']);key=ex.key(x,a,alpha)
    if ex.key_id(key)!=kid:raise ValueError('Original actual action identity mismatch')
    v=ex.evaluate_action(ir,key,dict(x=x,a=a,alpha=alpha),trace);append(out/'evaluations125.jsonl.gz',v)
    # Intersection retains every already valid independent bound; no old
    # successful containment is sacrificed to numerical non-nesting.
    merged=dict(v)
    for fld in ('q_lower','j_lower','optimum_lower'):merged[fld]=max(F(old[fld]),F(v[fld]))
    for fld in ('q_upper','j_upper'):merged[fld]=min(F(old[fld]),F(v[fld]))
    if merged['q_lower']>merged['q_upper']:raise ArithmeticError('Independent audit intervals conflict')
    evaluated[kid]=merged
    print(json.dumps(dict(key_id=kid,completed=len(evaluated),new_terminal_contexts=ex.COUNTS.get('terminal_contexts',0),reused_terminal_contexts=ex.COUNTS.get('reused_independent_terminal_contexts',0))),flush=True)
  finally:trace.close()
  combined=dict(previous,**evaluated);table={tuple(r[k] for k in ('index','budget','arm','training_loss','mode','row')):r for r in primary};results=[]
  for c in checks:
   r=table[tuple(c[k] for k in ('index','budget','arm','training_loss','mode','row'))];v=combined[c['final_key']];b=combined[c['baseline_key']]
   lo,hi=F(r['complete_policy_lower']),F(r['complete_policy_upper']);contained=lo<=v['j_lower']<=v['j_upper']<=hi;overlap=not(v['j_upper']<lo or v['j_lower']>hi)
   same=c['final_key']==c['baseline_key'];gl=F(0) if same else b['j_lower']-v['j_upper'];gu=F(0) if same else b['j_upper']-v['j_lower'];claim=F(c['claimed_gain']);gain_ok=not c['accepted'] or gl>=claim
   result=dict(**{k:c[k] for k in ('index','budget','arm','training_loss','mode','row','final_key','baseline_key','accepted')},initial_contained=c['contained'],initial_gain_confirmed=c['gain_confirmed'],contained=contained,gain_confirmed=gain_ok,independent_gain_lower=gl,independent_gain_upper=gu,claimed_gain=claim,contradiction=not overlap or (c['accepted'] and gu<claim))
   append(out/'checks125.jsonl',result);results.append(result)
  summary=dict(audit_status='completed-with-any-remaining-checks-explicit',initial_audit_unchanged=True,initial_contained=850,initial_accepted_gain_confirmed=193,decisions=len(results),contained=sum(c['contained'] for c in results),unresolved_containment=sum(not c['contained'] for c in results),accepted=sum(c['accepted'] for c in results),accepted_gain_confirmed=sum(c['accepted'] and c['gain_confirmed'] for c in results),contradictions=sum(c['contradiction'] for c in results),new_unique_actions=len(evaluated),requested_terminal_contexts=len(evaluated)*(2*BINS_FOLLOWUP+1),requested_context_cap=MAX_REQUESTED_CONTEXTS,counts=ex.COUNTS,cache_loading_seconds=cache_loading_seconds,cached_unique_terminal_states=len(cache),cache_source_sha256=trace_hash,source_boundary=boundary,independent_primitive=identity,original_source=original,transport_identity=transport_identity,changed_production_policies=0,new_population_samples=0)
  assert summary['counts'].get('terminal_contexts',0)+summary['counts'].get('reused_independent_terminal_contexts',0)==summary['requested_terminal_contexts']
  write(out/'SUMMARY125.json',summary)
  if summary['contradictions']:raise ArithmeticError('Follow-up independent economics contradicts a production claim')
  finish(out,tick,**summary)
 except BaseException:fail(out,tick);raise
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();run(a.output)
