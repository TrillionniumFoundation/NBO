"""Execute the frozen R29 catalogue once, preserving candidates before checks."""
from pathlib import Path
import hashlib
import json
import os
import platform
import sys
import time
import numpy as np
R=Path(__file__).resolve().parents[1]; ROOT=R.parents[1]
for sub in ('2026-10-05-r23','2026-10-06-r27','2026-10-06-r28','2026-10-06-r29'):
    sys.path.insert(0,str(ROOT/'revisions'/sub/'code'))
from experiment import economy
from entropic_certificate import candidate
from residual_certificate import certify
from entropic_budget import solve


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def durable(path,row):
    with path.open('a',encoding='utf8') as f:
        f.write(json.dumps(row,sort_keys=True,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())


def run():
    freeze=json.loads((R/'protocols/SOURCE_FREEZE.json').read_text())
    for name,expected in freeze['files'].items():
        actual=digest(ROOT/name)
        if actual!=expected:raise RuntimeError('Frozen source mismatch: '+name)
    commit=os.environ.get('NBO_SOURCE_COMMIT','')
    if len(commit)!=40 or any(c not in '0123456789abcdef' for c in commit):
        raise RuntimeError('NBO_SOURCE_COMMIT must identify the remote source freeze')
    protocol=json.loads((R/'protocols/PROTOCOL.json').read_text())
    out=R/'results/primary';out.mkdir(parents=True,exist_ok=False)
    identity=dict(source_commit=commit,source_manifest_sha256=digest(R/'protocols/SOURCE_FREEZE.json'),
        protocol_sha256=digest(R/'protocols/PROTOCOL.json'),python=platform.python_version(),
        numpy=np.__version__,platform=platform.platform(),machine=platform.machine(),
        execution_location='GitHub Actions' if os.environ.get('GITHUB_ACTIONS')=='true' else 'local research container',
        run_id=os.environ.get('GITHUB_RUN_ID'),threads_requested=1,started_ns=time.time_ns())
    (out/'EXECUTION_IDENTITY.json').write_text(json.dumps(identity,indent=2)+'\n')
    start=time.perf_counter(); records=[]; pair=0; ledger_seconds=0.
    for d in protocol['dimensions']:
      for regime in protocol['regimes']:
       for risk in protocol['risk_per_dimension']:
        for seed in protocol['seeds']:
         order=protocol['methods'] if pair%2==0 else protocol['methods'][::-1];pair+=1
         for method in order:
          key=f'd{d}_{regime}_rho{risk:g}_seed{seed}_{method}'
          t0=time.perf_counter();rec=dict(key=key,dimension=d,horizon=protocol['horizon'],
              regime=regime,risk_per_dimension=risk,theta=risk*d,seed=seed,method=method,status='attempted')
          try:
            model=economy(d,regime,protocol['horizon']);t1=time.perf_counter()
            if method=='NBO-primitive-risk':
                K,W,counters=solve(model,risk*d,protocol['policy_tolerance'],seed=seed,slack=protocol['slack'])
            else:K,W,counters=candidate(model,risk*d,'structural')
            t2=time.perf_counter()
            p=out/(key+'.npz')
            np.savez_compressed(p,gains=K,critic_factor=W,
                **{n:model[n] for n in ('A','B','Q','R','Qf','Sigma')})
            with p.open('rb') as f:os.fsync(f.fileno())
            rec.update(candidate_sha256=digest(p),candidate_bytes=p.stat().st_size,
                counters=counters,mean_initial_action=float(np.mean(-K[0]@np.ones(d))),
                initialization_seconds=t1-t0,fitting_seconds=t2-t1)
            t3=time.perf_counter();rec['candidate_write_seconds']=t3-t2
            cert=certify(model,K,risk*d,protocol['execution_error']);t4=time.perf_counter()
            rec.update(certificate=cert,verification_seconds=t4-t3,
                status='certified' if cert['policy_gap_upper']<=protocol['policy_tolerance'] and counters['all_training_thresholds_met'] else 'uncertified')
          except Exception as error:
            rec.update(status='failed',exception=type(error).__name__,message=str(error))
          durable(out/'attempts.jsonl',rec)
          rec['complete_service_seconds']=time.perf_counter()-t0
          tledger=time.perf_counter();durable(out/'services.jsonl',rec);ledger_seconds+=time.perf_counter()-tledger
          records.append(rec)
          print(key,rec['status'],rec['complete_service_seconds'],flush=True)
    summary=dict(services=len(records),certified=sum(r['status']=='certified' for r in records),
        failed=sum(r['status']=='failed' for r in records),uncertified=sum(r['status']=='uncertified' for r in records),
        complete_service_seconds_sum=sum(r['complete_service_seconds'] for r in records),
        closing_ledger_seconds=ledger_seconds,execution_loop_seconds=time.perf_counter()-start,identity=identity)
    assert len(records)==protocol['primary_services'],summary
    (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':run()
