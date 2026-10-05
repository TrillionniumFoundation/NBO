"""Replay every recorded enclosure; check exact scaling, never refit a policy."""
from __future__ import annotations
import hashlib,json,time
from pathlib import Path
import numpy as np
import torch
import intervals
from economy import Economy,tasks
from study import verify_freeze
R=Path(__file__).resolve().parents[1]

def main():
    start=time.perf_counter();freeze=verify_freeze()
    source=R/'results/registered/SUMMARY.json'
    s=json.loads(source.read_text());assert len(s['records'])==252 and not s['failures']
    original=intervals._exp_positive_point
    monitor={'calls':0,'arguments':0,'largest_argument':0.0}
    def checked(x):
        xx=np.asarray(x,dtype=np.float64)
        k=0
        while np.max(xx,initial=0)/2**k>.5:k+=1
        scaled=np.ldexp(xx,-k)
        # The analytical implementation uses exact binary scaling. Verify that
        # no actual certified argument loses a subnormal bit at that step.
        if not np.array_equal(np.ldexp(scaled,k),xx):
            raise ArithmeticError('binary scaling was not exact on an actual certificate argument')
        monitor['calls']+=1;monitor['arguments']+=xx.size
        monitor['largest_argument']=max(monitor['largest_argument'],float(np.max(xx,initial=0)))
        return original(xx)
    intervals._exp_positive_point=checked
    count=0;points=0
    try:
        for row in s['records']:
            d=row['dimension'];n=row['queries']
            e=Economy(json.loads((R/f'protocols/economy_d{d}.json').read_text()))
            y,t=tasks(n,d,195520+d)
            for stage in row['stages']:
                a=torch.tensor(stage['selected_actions'],dtype=torch.float64)
                c=e.certify(y,a,t)
                if c!=stage['certificate']:
                    raise AssertionError(f"certificate replay differs: {d} {n} {row['stream']} {row['method']}")
                count+=1;points+=n
            print('verified',d,n,row['stream'],row['method'],flush=True)
    finally:
        intervals._exp_positive_point=original
    rec={'summary_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'freeze_sha256':freeze,
         'complete_services':252,'stages_replayed':count,'task_certificates_replayed':points,
         'all_certificate_fields_exactly_reproduced':True,'exact_binary_scaling':monitor,
         'audit_seconds':time.perf_counter()-start,'scope':'Post-execution deterministic verification; no fitting, new task, new simulation observation, or extra independent stream.'}
    (R/'results/CERTIFICATE_REPLAY.json').write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
    print(json.dumps(rec,indent=2))
if __name__=='__main__':main()
