"""Full predeclared off-mesh census or one complete serial timing repetition."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'): os.environ[key]='1'
import argparse, json, time
from common126 import *


def run(output, repeat=None):
    out,tick,info=start(output,'off-mesh-primary' if repeat is None else 'serial-first-state-timing')
    try:
        verified=verify_inputs()
        import service126 as svc
        svc.configure()
        groups=catalog(); states=STATES if repeat is None else STATES[:1]
        if repeat is not None:
            shift=13*repeat%len(groups); groups=groups[shift:]+groups[:shift]
        count=0; total=0
        for index,budget,arm,loss,mode in groups:
            cohort_start=time.perf_counter(); load_tick=time.perf_counter()
            path=model_path((index,budget,arm,loss))
            model=None if path is None else json.loads(path.read_text())
            load_seconds=time.perf_counter()-load_tick
            for row,state in enumerate(states):
                record=svc.service(state,(.5,.75)[index],model,mode)
                record.update(index=index,budget=budget,arm=arm,training_loss=loss,mode=mode,row=row,
                    repeat=repeat,source_commit=verified['boundaries']['source_commit'],
                    actor_commit=ACTOR_COMMIT,baseline_commit=BASELINE_COMMIT,
                    deterministic_census=True,independent_population_samples=0)
                append(out/'records126.jsonl.gz',record); count+=1
            seconds=time.perf_counter()-cohort_start; total+=seconds
            append(out/'cohorts126.jsonl',dict(index=index,budget=budget,arm=arm,training_loss=loss,mode=mode,
                n=len(states),seconds=seconds,load_seconds=load_seconds))
            print(json.dumps(dict(cohort=[index,budget,arm,loss,mode],decisions=count,seconds=seconds)),flush=True)
        finish(out,tick,decisions=count,cohorts=len(groups),cohort_seconds=total,repeat=repeat,
            source=verified,independent_population_samples=0)
    except BaseException: fail(out,tick); raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--output',required=True)
    parser.add_argument('--repeat',type=int,choices=(0,1,2)); args=parser.parse_args()
    run(args.output,args.repeat)
