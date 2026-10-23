"""One complete deterministic census or one prespecified serial timing pass."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,time
from common125 import *

def run(output,repeat=None):
 out,tick,info=start(output,'deterministic-primary' if repeat is None else 'serial-timing')
 try:
  verified=verify_inputs();import service125 as svc;svc.configure()
  groups=catalog();ss=STATES if repeat is None else STATES[:1]
  if repeat is not None:
   shift=13*repeat%len(groups);groups=groups[shift:]+groups[:shift]
  n=0;total=0
  for index,budget,arm,loss,mode in groups:
   ct=time.perf_counter();lt=time.perf_counter();p=model_path((index,budget,arm,loss));model=None if p is None else json.loads(p.read_text());load=time.perf_counter()-lt
   for row,state in enumerate(ss):
    rec=svc.grid_service(state,(.5,.75)[index]) if arm=='uniform_dp' else svc.service(state,(.5,.75)[index],model,mode)
    rec.update(index=index,budget=budget,arm=arm,training_loss=loss,mode=mode,row=row,state125=list(state),alpha=(.5,.75)[index],repeat=repeat,source_commit=verified['boundaries']['source_commit'],actor_commit=ACTOR_COMMIT,deterministic_census=True,population_observations=0)
    append(out/'records125.jsonl.gz',rec);n+=1
   secs=time.perf_counter()-ct;total+=secs
   append(out/'cohorts125.jsonl',dict(index=index,budget=budget,arm=arm,training_loss=loss,mode=mode,n=len(ss),seconds=secs,load_seconds=load))
   print(json.dumps(dict(cohort=[index,budget,arm,loss,mode],decisions=n,seconds=secs)),flush=True)
  finish(out,tick,decisions=n,cohorts=len(groups),cohort_seconds=total,verified_source=verified,repeat=repeat,independent_population_samples=0)
 except BaseException:fail(out,tick);raise
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--repeat',type=int,choices=[0,1,2]);a=p.parse_args();run(a.output,a.repeat)
