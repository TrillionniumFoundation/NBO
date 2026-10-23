"""Frozen R124 independent states and complete serial matched campaign."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,sys,time
from common124 import *


def draw(output):
 out,tick,info=start(output,'new-independent-state-draw')
 try:
  verified=verify_source();b=boundaries(False)
  if not b.get('remote_source_readback_before_draw'):raise ValueError('Remote source readback must precede entropy draw')
  raw=os.urandom(160);(out/'entropy124.bin').write_bytes(raw);ss=[]
  for j in range(N):
   v=[int.from_bytes(raw[(2*j+k)*5:(2*j+k+1)*5],'little') for k in range(2)];x=[z/2**40 for z in v]
   ss.append(dict(row=j,integers=v,state=x,hex=[z.hex() for z in x]))
  write(out/'states124.json',dict(source_commit=b['source_commit'],actor_commit=ACTOR_COMMIT,states=ss,
   sampling='16 independent pairs of40-bit dyadic coordinates, conditional on independent uniform OS entropy bits',duplicates_retained=True))
  finish(out,tick,info,verified_source=verified,source_commit=b['source_commit'],states=N,entropy_bytes=len(raw))
 except BaseException:fail(out,tick);raise


def run(output,repeat=None):
 out,tick,info=start(output,'primary' if repeat is None else 'timing')
 try:
  verified=verify_source();binding=boundaries();ss=states();import service124 as svc
  svc.configure();groups=[k+(m,) for k in catalog() for m in MODES]
  if repeat is not None:
   shift=11*repeat%len(groups);groups=groups[shift:]+groups[:shift];ss=ss[:4]
  n=0;cohort_total=0;loads=0
  for index,budget,arm,loss,mode in groups:
   ct=time.perf_counter();lt=time.perf_counter();p=model_path((index,budget,arm,loss));model=None if p is None else json.loads(p.read_text());load_seconds=time.perf_counter()-lt;loads+=load_seconds
   count0=svc.prior.old.econ.COUNTS.copy()
   for state in ss:
    record=svc.service(state['state'],(.5,.75)[index],model,mode)
    record.update(index=index,budget=budget,arm=arm,training_loss=loss,mode=mode,row=state['row'],alpha=(.5,.75)[index],
     repeat=repeat,source_commit=binding['source_commit'],state_commit=binding['state_commit'],actor_commit=ACTOR_COMMIT,
     population_observation=repeat is None)
    if repeat is not None:
     # Complete timing policies/counters retained; already-verified arithmetic
     # witnesses are not duplicated in timing files. Equality audit is exact.
     record={k:record[k] for k in ('index','budget','arm','training_loss','mode','row','alpha','repeat','source_commit','state_commit','actor_commit','population_observation','state','state_hex','action','action_hex','baseline_action','baseline_action_hex','complete_policy_lower','complete_policy_upper','original_optimum_lower','certified_regret_upper','loss','width','qualified','accepted_improvement','certified_policy_gain_lower','selected_menu_index','additional_original_risk_queries','dual_solves_started','dual_solves_completed','dual_solver_successes','dual_seconds','complete_seconds','counts','raw_proposal_kept','enhancement_failure')}
    append(out/'records124.jsonl',record);n+=1
   secs=time.perf_counter()-ct;cohort_total+=secs
   append(out/'cohorts124.jsonl',dict(index=index,budget=budget,arm=arm,training_loss=loss,mode=mode,
    n=len(ss),seconds=secs,load_seconds=load_seconds,counts=svc.prior.old.lab.inherited.base.counter_delta(count0)))
   print(json.dumps(dict(cohort=[index,budget,arm,loss,mode],completed_rows=n,seconds=secs)),flush=True)
  finish(out,tick,info,verified_source=verified,boundaries=binding,decisions=n,cohorts=len(groups),
   cohort_seconds=cohort_total,load_seconds=loads,repeat=repeat,independent_states=N if repeat is None else 0,
   full_process_clock_excludes_no_scientific_child=True)
 except BaseException:fail(out,tick);raise

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['states','run']);p.add_argument('--output',required=True);p.add_argument('--repeat',type=int,choices=[0,1,2]);a=p.parse_args()
 draw(a.output) if a.mode=='states' else run(a.output,a.repeat)
