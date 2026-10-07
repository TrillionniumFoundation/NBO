"""One fresh process per capped service; exact first-crossing checkpoint boundary."""
from __future__ import annotations
import time
BOOT=time.perf_counter()
import os,sys,json,hashlib,platform,traceback
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-07-r41'
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(path,obj,default=None):
    path.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(obj,default=default,sort_keys=True,separators=(',',':'))+'\n').encode()
    with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    return sha(raw)
def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--spec',required=True);ap.add_argument('--directory',required=True);args=ap.parse_args()
    spec=json.loads(args.spec);dest=Path(args.directory);dest.mkdir(parents=True,exist_ok=True)
    affinity=None
    if hasattr(os,'sched_getaffinity'):
        affinity=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{affinity})
    import numpy as np
    if spec['kind']=='scalar':
        import scalar_training as module
        encode=module.nl.encode
    elif spec['kind']=='coupled':
        import coupled_training as module
        encode=module.encode
    else:
        sys.path.insert(0,str(OLD/'code'));import precision_catalogue as module
        encode=module.ps.json_default
    interval_counts={}
    if spec['kind']!='precision':
        import torch
        torch.set_num_threads(1)
        cls=module.nl.I if spec['kind']=='scalar' else module.I
        # Semantic array-operation counts, not a hardware FLOP claim.
        for key in ('__add__','__mul__','__truediv__','square'):
            old=getattr(cls,key)
            def counted(self,*args,_old=old,_key=key):
                result=_old(self,*args);interval_counts[_key]=interval_counts.get(_key,0)+int(result.lo.size);return result
            setattr(cls,key,counted)
            if key=='__add__':cls.__radd__=counted
            if key=='__mul__':cls.__rmul__=counted
    initialized=time.perf_counter();started=initialized;checkpoints=[]
    def checkpoint(payload,index):
        payload['semantic_interval_operations_so_far']=dict(interval_counts)
        h=dump(dest/'checkpoints'/f'{index:02}.json',payload,encode)
        checkpoints.append(dict(index=index,sha256=h,seconds_through_fsync=time.perf_counter()-started))
    status='completed';error=None
    try:
        if spec['kind']=='scalar':
            fn=module.neural_service if spec['method']=='direct-neural' else module.spline_service
            result=fn(spec['price'],spec['theta'],spec['seed'],checkpoint)
        elif spec['kind']=='coupled':result=module.service(spec['price'],spec['seed'],spec['method'],checkpoint)
        else:
            module.ATTEMPTS.clear();result=module.ps.service(spec['service'])
            result['precision_attempts']=list(module.ATTEMPTS)
            result['precision_work']={str(b):dict(attempts=sum(t['precision']==b for t in module.ATTEMPTS),accepted=sum(t['precision']==b and t['accepted'] for t in module.ATTEMPTS),rejected=sum(t['precision']==b and not t['accepted'] for t in module.ATTEMPTS),multiply_adds=sum(t['multiply_adds'] for t in module.ATTEMPTS if t['precision']==b)) for b in (32,64)}
        result['semantic_interval_operations']=dict(interval_counts)
        result['service_spec']=spec
    except Exception:
        status='software_exception';error=traceback.format_exc();result=dict(service_spec=spec,error=error,checkpoints=checkpoints)
    record_hash=dump(dest/'record.json',result,encode);elapsed=time.perf_counter()-started
    clock=dict(spec=spec,status=status,error=error,seconds_through_fsync=elapsed,initialization_seconds=initialized-BOOT,checkpoints=checkpoints,record_sha256=record_hash,source_sha256={p.name:sha(p.read_bytes()) for p in sorted((R/'code').glob('*.py'))},python=platform.python_version(),numpy=np.__version__,cpu_affinity=affinity,frequency_controlled=False,independent_process=True)
    if status=='completed':
        clock['crossings']=result.get('crossings');clock['all_state_gap']=result.get('all_state_gap',result.get('accepted_global_bound',result.get('policy_gap_upper')))
        clock['certified']=result.get('certified')
        if 'precision_work' in result:clock['precision_work']=result['precision_work']
    dump(dest/'clock.json',clock);print(json.dumps(clock),flush=True)
    if error:raise RuntimeError(error)
if __name__=='__main__':main()
