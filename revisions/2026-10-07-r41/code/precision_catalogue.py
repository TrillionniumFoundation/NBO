"""Economic-target stress catalogue; every native precision attempt is logged.

Only trace collection is added to R38. Acceptance gates and stopping targets
are unchanged. One execution per object is mechanism, not timing-frontier,
evidence. Resumption reads existing records; it never replaces a clock.
"""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import sys,json,hashlib,time,platform,argparse
R=Path(__file__).resolve().parents[1];OLD=(R/'vendor/r38') if (R/'vendor/r38/code').exists() else R.parent/'2026-10-07-r38'
sys.path.insert(0,str(OLD/'code'))
import numpy as np
import policy_study as ps
from verified_refresh import FixedTarget
ATTEMPTS=[]
class TracedTarget(FixedTarget):
    def step(self,W,rho,mode='adaptive',terminal_tolerance=None):
        self.context=dict(starting_radius=rho,mode=mode,terminal_tolerance=terminal_tolerance,
            target_sha256=hashlib.sha256(self.target.tobytes()).hexdigest())
        first=len(ATTEMPTS)
        try:
            V,nr,info=super().step(W,rho,mode,terminal_tolerance)
            for x in ATTEMPTS[first:]:x['accepted']=False
            ATTEMPTS[-1].update(accepted=True,acceptance=info['acceptance'],next_radius=nr)
            return V,nr,info
        except Exception as exc:
            for x in ATTEMPTS[first:]:x.update(accepted=False,step_error=str(exc))
            raise
    def propose(self,W,precision):
        V,info=super().propose(W,precision)
        ATTEMPTS.append(dict(**self.context,**info,input_sha256=hashlib.sha256(W.tobytes()).hexdigest(),output_sha256=hashlib.sha256(V.tobytes()).hexdigest()))
        return V,info
ps.FixedTarget=TracedTarget

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,default=0);ap.add_argument('--stop',type=int,default=48);args=ap.parse_args()
    affinity=None
    if hasattr(os,'sched_getaffinity'):
        available=sorted(os.sched_getaffinity(0));os.sched_setaffinity(0,{available[0]});affinity=available[0]
    dest=R/'results/precision';dest.mkdir(exist_ok=True)
    specs=[dict(kind='policy',name=f'd{d}-c{c:g}-e{e:g}',epsilon=e,economy=dict(d=d,T=4,condition=c,valuation=1.,sigma=.001,theta=.1),method=m)
        for d,c in [(2,1.),(2,16.),(8,1.),(8,16.)] for e in [1e-10,1e-12,1e-14]
        for m in ['fixed32-cached','fixed64-cached','adaptive-cached','tuned-cached']]
    for i in range(args.start,min(args.stop,len(specs))):
        spec=specs[i];path=dest/f'service-{i:03}.json';cp=path.with_suffix('.clock.json')
        if path.exists():
            if not cp.exists():raise RuntimeError('Unfinished previous service; never silently rerun')
            continue
        ATTEMPTS.clear();start=time.perf_counter();result=ps.service(spec)
        result['precision_attempts']=list(ATTEMPTS)
        result['execution']=dict(cpu_affinity=affinity,frequency_controlled=False,python=platform.python_version(),numpy=np.__version__,repetitions=1,protocol_commit='d66fc832e67050518317de6f505bcd2eb98a3158',trace_overhead_included=True,timing_claim='Mechanism catalogue only')
        raw=(json.dumps(result,default=ps.json_default,sort_keys=True,separators=(',',':'))+'\n').encode()
        with path.open('wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
        row=dict(id=i,spec=spec,record_sha256=hashlib.sha256(raw).hexdigest(),seconds_through_fsync=time.perf_counter()-start,certified=result['certified'],gap=result['policy_gap_upper'],accepted32=sum(x['accepted'] and x['precision']==32 for x in ATTEMPTS),accepted64=sum(x['accepted'] and x['precision']==64 for x in ATTEMPTS),rejected32=sum(not x['accepted'] and x['precision']==32 for x in ATTEMPTS),rejected64=sum(not x['accepted'] and x['precision']==64 for x in ATTEMPTS))
        cp.write_text(json.dumps(row,indent=2,sort_keys=True)+'\n');print(json.dumps(row),flush=True)
    ledger=[json.loads(p.read_text()) for p in sorted(dest.glob('service-*.clock.json'))]
    (dest/'INDEX.json').write_text(json.dumps(ledger,indent=2,sort_keys=True)+'\n')
    source={str(p.relative_to(OLD)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (OLD/'code').rglob('*.py')}
    (dest/'SOURCE.json').write_text(json.dumps(dict(source=source,trace_wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
