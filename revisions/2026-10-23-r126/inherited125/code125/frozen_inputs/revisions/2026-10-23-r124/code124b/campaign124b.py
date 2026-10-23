"""New post-A prospective draw and complete independently paid R124B services."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,time
from common124b import *

def draw(output):
 out,tick,info=start(output,'new-independent-B-state-draw')
 try:
  verified=verify_source();b=boundaries(False)
  if not b.get('remote_source_readback_before_draw'):raise ValueError('Remote B source readback must precede entropy draw')
  raw=os.urandom(320);(out/'entropy124b.bin').write_bytes(raw);ss=[]
  for j in range(N):
   v=[int.from_bytes(raw[(2*j+k)*5:(2*j+k+1)*5],'little') for k in range(2)];x=[z/2**40 for z in v]
   ss.append(dict(row=j,integers=v,state=x,hex=[z.hex() for z in x]))
  write(out/'states124b.json',dict(source_commit=b['source_commit'],actor_commit=ACTOR_COMMIT,states=ss,
   sampling='32 fresh independent pairs of40-bit dyadic coordinates conditional on independent uniform OS entropy bits',duplicates_retained=True,
   post_A_design=True,no_A_or_R123_states_or_outcomes_used_as_B_observations=True))
  finish(out,tick,info,verified_source=verified,source_commit=b['source_commit'],states=N,entropy_bytes=len(raw))
 except BaseException:fail(out,tick);raise
def run(output,repeat=None):
 out,tick,info=start(output,'B-primary' if repeat is None else 'B-timing')
 try:
  verified=verify_source();binding=boundaries();ss=states();import service124b as svc
  svc.configure();groups=[k+(m,) for k in catalog() for m in MODES]
  if repeat is not None:
   shift=11*repeat%len(groups);groups=groups[shift:]+groups[:shift];ss=ss[:TIMED_N]
  n=0;cohort_total=0.;loads=0.
  for index,budget,arm,loss,mode in groups:
   ct=time.perf_counter();lt=time.perf_counter();p=model_path((index,budget,arm,loss));model=None if p is None else json.loads(p.read_text());load_seconds=time.perf_counter()-lt;loads+=load_seconds
   count0=svc.prior.old.econ.COUNTS.copy()
   for state in ss:
    record=svc.service(state['state'],(.5,.75)[index],model,mode)
    record.update(index=index,budget=budget,arm=arm,training_loss=loss,mode=mode,row=state['row'],alpha=(.5,.75)[index],
     repeat=repeat,source_commit=binding['source_commit'],state_commit=binding['state_commit'],actor_commit=ACTOR_COMMIT,
     population_observation=repeat is None,phase='B-post-A-independent-design')
    # Full lossless arithmetic witnesses remain in timing records as well.
    append(out/RECORDS,record);n+=1
   secs=time.perf_counter()-ct;cohort_total+=secs
   append(out/'cohorts124b.jsonl',dict(index=index,budget=budget,arm=arm,training_loss=loss,mode=mode,n=len(ss),
    seconds=secs,load_seconds=load_seconds,counts=svc.prior.old.lab.inherited.base.counter_delta(count0)))
   print(json.dumps(dict(cohort=[index,budget,arm,loss,mode],completed_rows=n,seconds=secs)),flush=True)
  finish(out,tick,info,verified_source=verified,boundaries=binding,decisions=n,cohorts=len(groups),cohort_seconds=cohort_total,
   load_seconds=loads,repeat=repeat,independent_states=N if repeat is None else 0,
   lossless_record_format='concatenated gzip JSONL members; mtime0; compression included in cohort and parent cost',full_witnesses_retained=True)
 except BaseException:fail(out,tick);raise
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['states','run']);p.add_argument('--output',required=True);p.add_argument('--repeat',type=int,choices=[0,1,2]);a=p.parse_args()
 draw(a.output) if a.mode=='states' else run(a.output,a.repeat)
