"""New all-action independent rational evaluation for R122; no production imports.

Every final, completed-control and available raw actor action is evaluated.
Accepted improvement claims get a fixed independent 64/128/256/512-cell ladder.
Unresolved independent endpoint/gain checks remain unresolved, not passed.
"""
from __future__ import annotations
import argparse,json,sys,time
from pathlib import Path
from fractions import Fraction as F
from common122 import *


def main():
 p=argparse.ArgumentParser();p.add_argument('--source-commit',required=True);p.add_argument('--primary',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
 out,initial,tick=start(a.output,'independent',{'claimed_source_commit':a.source_commit});trace=None
 try:
  source=verify_source(a.source_commit);dump(out/'VERIFIED_SOURCE122.json',source)
  primary=Path(a.primary)/'records122.jsonl';data,binding=validated_primary(a.primary,a.source_commit)
  if len(data)!=len(identities()) or {key(r) for r in data}!=identities():raise ValueError('All primary decisions required')
  for r in data:
   if r['source_commit']!=a.source_commit or r['population_observation'] is not True:raise ValueError('Primary source and sample mismatch')
  from algebra_audit122 import audit
  algebra={}
  for r in data:
   for field,count in audit(r).items():algebra[field]=algebra.get(field,0)+count
  dump(out/'ALGEBRA_AUDIT122.json',{'primary_sha256':digest(primary),'primary_state_binding':binding,'verifier_sha256':digest(Path(__file__).with_name('algebra_audit122.py')),'counts':algebra,'original_economic_queries':0,'production_service_imported':False,'scope':'independent exact consequences of serialized support premises; primitive economics checked separately below'})
  sys.path.insert(0,str(R121/'code121'));import exact121 as ex
  ir,primitive=ex.load_primitives();actions={};refs={}
  for r in data:
   x=tuple(map(F,r['state']));alpha=F(r['alpha'])
   for role,value in (('final',r['action']),('baseline',r['baseline_action']),('raw',r['raw_proposal_kept'])):
    if value is None:refs[(key(r),role)]=None;continue
    action=F(value);k=ex.key(x,action,alpha);actions[k]={'x':x,'a':action,'alpha':alpha};refs[(key(r),role)]=k
  dump(out/'INPUTS122.json',{'primary_sha256':digest(primary),'primary_state_binding':binding,'primary_rows':len(data),'unique_initial_policy_keys':len(actions),'independent_primitive':primitive,'base_bins':64,'accepted_claim_ladder':[64,128,256,512],'terminal_iterations_if_interior':32,'same_future_allowance':'15/16777216'})
  class SegmentedTrace:
   def __init__(self):
    self.number=0;self.total_rows=0;self.parts=[];self.open()
   def open(self):
    self.path=out/'terminal_witnesses122'/f'part{self.number:05d}.jsonl.gz';self.path.parent.mkdir(exist_ok=True)
    self.inner=ex.ExactTrace(self.path)
   def write(self,row):self.inner.write(row);self.total_rows+=1
   def seal(self):
    self.inner.close();self.parts.append({'path':str(self.path.relative_to(out)),'bytes':self.path.stat().st_size,'sha256':digest(self.path)})
    append(out/'SEALED_WITNESS_PARTS122.jsonl',self.parts[-1])
   def flush(self):
    self.inner.flush()
    if self.path.stat().st_size>=4*1024*1024:
     self.seal();self.number+=1;self.open()
   def close(self):
    self.seal();dump(out/'WITNESS_MANIFEST122.json',{'parts':self.parts,'records':self.total_rows,'no_record_omissions':True,'segment_seals_after_complete_policy_evaluation':True})
  trace=SegmentedTrace();cache={};best={}
  def evaluate(k,bins):
   ck=(k,bins)
   if ck in cache:return cache[ck]
   ex.BINS=bins;result=ex.evaluate_action(ir,k,actions[k],trace)
   cache[ck]=result
   if k not in best:best[k]=dict(result)
   else:
    previous=best[k]
    for field in ('q_lower','j_lower','optimum_lower'):previous[field]=max(previous[field],result[field])
    for field in ('q_upper','j_upper'):previous[field]=min(previous[field],result[field])
    previous['bins']=max(previous['bins'],bins)
    if previous['q_lower']>previous['q_upper'] or previous['j_lower']>previous['j_upper']:raise ArithmeticError('Independent mesh intervals contradict')
   append(out/'POLICY_EVALUATIONS122.jsonl',ex.encoded(result))
   return result
  for j,k in enumerate(sorted(actions)):
   evaluate(k,64)
   if (j+1)%16==0 or j+1==len(actions):print('INDEPENDENT_BASE',j+1,len(actions),round(time.perf_counter()-tick,3),flush=True)
  def check_claim(r):
   old=best[refs[(key(r),'baseline')]];new=best[refs[(key(r),'final')]]
   claimed=F(r['certified_policy_gain_lower'])
   return {'gain_confirmed':old['j_lower']-new['j_upper']>=claimed,
     'positive_gain_confirmed':old['j_lower']-new['j_upper']>0,
     'candidate_interval_contained':new['j_lower']>=F(r['complete_policy_lower']) and new['j_upper']<=F(r['complete_policy_upper']),
     'candidate_interval_compatible':max(new['j_lower'],F(r['complete_policy_lower']))<=min(new['j_upper'],F(r['complete_policy_upper'])),
     'independent_gain_lower':old['j_lower']-new['j_upper'],'independent_gain_upper':old['j_upper']-new['j_lower'],
     'claimed_gain_lower':claimed,'baseline_bins':old['bins'],'candidate_bins':new['bins']}
  accepted=[r for r in sorted(data,key=key) if r['accepted_improvement']]
  for j,r in enumerate(accepted):
   attempts=[]
   for bins in (64,128,256,512):
    evaluate(refs[(key(r),'baseline')],bins);evaluate(refs[(key(r),'final')],bins)
    checked=check_claim(r);attempts.append({'requested_bins':bins,**checked})
    if not checked['candidate_interval_compatible']:raise ArithmeticError('Independent original economic intervals contradict candidate')
    if checked['gain_confirmed'] and checked['candidate_interval_contained']:break
   append(out/'CLAIM_CHECKS122.jsonl',{'identity':key(r),'attempts':attempts,'unresolved_after_fixed_ladder':not(checked['gain_confirmed'] and checked['candidate_interval_contained'])})
   if (j+1)%16==0 or j+1==len(accepted):print('INDEPENDENT_CLAIMS',j+1,len(accepted),round(time.perf_counter()-tick,3),flush=True)
  trace.close();trace=None
  optima={}
  for k,z in best.items():
   sk=(k[0],k[2]);lo,hi=z['optimum_lower'],z['q_upper']
   if sk in optima:lo,hi=max(lo,optima[sk][0]),min(hi,optima[sk][1])
   if lo>hi:raise ArithmeticError('Independent original optimum contradiction')
   optima[sk]=(lo,hi)
  confirmations=0;containments=0;unresolved=0
  for r in sorted(data,key=key):
   fk,bk=refs[(key(r),'final')],refs[(key(r),'baseline')];z,old=best[fk],best[bk]
   lo,hi=optima[(fk[0],fk[2])];reglo=max(F(0),z['j_lower']-hi);reghi=z['j_upper']-lo
   if reghi<reglo:raise ArithmeticError('Invalid independent original regret interval')
   same=fk==bk;gl,gu=(F(0),F(0)) if same else (old['j_lower']-z['j_upper'],old['j_upper']-z['j_lower'])
   claim=F(r['certified_policy_gain_lower']);confirmed=same or gl>=claim
   contained=z['j_lower']>=F(r['complete_policy_lower']) and z['j_upper']<=F(r['complete_policy_upper'])
   compatible=max(z['j_lower'],F(r['complete_policy_lower']))<=min(z['j_upper'],F(r['complete_policy_upper']))
   if not compatible or gl>F(1,256) or gu<claim:raise ArithmeticError('Independent result contradicts proved primary account')
   cap=F(1,8)+sum(map(F,r['state']))/16
   result={f:r[f] for f in ('index','row','budget','arm','loss','service','state_hex')}
   result.update(source_commit=a.source_commit,state_commit=binding['state_commit'],actor_commit=ACTOR_COMMIT,independent_policy_lower=z['j_lower'],independent_policy_upper=z['j_upper'],independent_q_lower=z['q_lower'],independent_q_upper=z['q_upper'],
    independent_optimum_lower=lo,independent_optimum_upper=hi,independent_regret_lower=reglo,independent_regret_upper=reghi,
    squared_original_action_error_upper=min(cap*cap,reghi),baseline_policy_lower=old['j_lower'],baseline_policy_upper=old['j_upper'],
    independent_gain_lower=gl,independent_gain_upper=gu,theorem_gain_lower=claim,theorem_gain_upper=F(1,256),theorem_regret_cap=F(1,256),
    independent_gain_claim_confirmed=confirmed,independent_candidate_interval_contained=contained,independent_compatibility=compatible,
    final_key_id=z['key_id'],baseline_key_id=old['key_id'],original_action_hex=r['action_hex'],same_policy_exact_zero=same,
    initial_raw_proposal_key_id=None if refs[(key(r),'raw')] is None else ex.key_id(refs[(key(r),'raw')]))
   append(out/'COMPARISONS122.jsonl',result)
   if r['accepted_improvement']:
    confirmations+=confirmed;containments+=contained;unresolved+=not(confirmed and contained)
  for k,z in sorted(best.items()):append(out/'BEST_POLICY_BOUNDS122.jsonl',ex.encoded(z))
  if digest(primary)!=json.loads((out/'INPUTS122.json').read_text())['primary_sha256']:raise ValueError('Primary input mutated')
  finish(out,initial,tick,{'primary_rows':len(data),'unique_policy_keys':len(actions),'actual_independent_evaluations':len(cache),'accepted_primary_decisions':len(accepted),
    'accepted_gain_claims_independently_confirmed':confirmations,'accepted_candidate_intervals_independently_contained':containments,'accepted_joint_checks_unresolved':unresolved,
    'counts':ex.COUNTS,'no_new_population_states':True,'production_derivative_code_imported':False,'independent_scope':'exact rational original primitive evaluations, not an external-author referee report'})
 except BaseException:
  if trace is not None:trace.close()
  fail(out,tick);raise

if __name__=='__main__':main()
