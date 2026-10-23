"""New paired uncached/cached executions; all scientific decisions stay fixed."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
import argparse
from cache126c import *


def run(output,repeat=None):
    out,tick,info=start(output,'R126C-paired-primary' if repeat is None else 'R126C-paired-first-state-timing')
    try:
        verified=verify_sources(); import service126 as svc; svc.configure()
        groups=catalog(); states=STATES if repeat is None else STATES[:1]
        if repeat is not None:
            shift=13*repeat%len(groups);groups=groups[shift:]+groups[:shift]
        count=0;total=0
        for group_number,cohort in enumerate(groups):
            index,budget,arm,loss,mode=cohort
            phase=0 if repeat is None else repeat+1
            order=VARIANTS if (group_number+phase)%2==0 else tuple(reversed(VARIANTS))
            for variant in order:
                ct=time.perf_counter();load_tick=time.perf_counter()
                path=model_path((index,budget,arm,loss)); model=None if path is None else json.loads(path.read_text())
                load_seconds=time.perf_counter()-load_tick
                for row,state in enumerate(states):
                    st=time.perf_counter()
                    if variant=='cached':
                        with ExactGeometry(svc.env) as cache:
                            record=svc.service(state,(.5,.75)[index],model,mode)
                            counters=dict(cache.counts)
                    else:
                        record=svc.service(state,(.5,.75)[index],model,mode);counters={}
                    elapsed=time.perf_counter()-st
                    record.update(index=index,budget=budget,arm=arm,training_loss=loss,mode=mode,row=row,
                        repeat=repeat,source_commit=verified['original']['boundaries']['source_commit'],
                        actor_commit=ACTOR_COMMIT,baseline_commit=BASELINE_COMMIT,
                        deterministic_census=True,independent_population_samples=0,variant126c=variant,
                        cache_source_commit126c=verified['boundaries']['source_commit'],cache_stats126c=counters,
                        paired_order126c=list(order),complete_service_seconds126c=elapsed)
                    append(out/'records126c.jsonl.gz',record);count+=1
                seconds=time.perf_counter()-ct;total+=seconds
                append(out/'cohorts126c.jsonl',dict(index=index,budget=budget,arm=arm,training_loss=loss,mode=mode,
                    variant126c=variant,n=len(states),seconds=seconds,load_seconds=load_seconds,paired_order126c=list(order)))
                print(json.dumps(dict(cohort=list(cohort),variant=variant,decisions=count,seconds=seconds)),flush=True)
        finish(out,tick,decisions=count,cohorts=len(groups)*2,cohort_seconds=total,repeat=repeat,source=verified,
               economic_information_cached=False,independent_population_samples=0)
    except BaseException:fail(out,tick);raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--repeat',type=int,choices=(0,1,2))
    a=p.parse_args();run(a.output,a.repeat)
