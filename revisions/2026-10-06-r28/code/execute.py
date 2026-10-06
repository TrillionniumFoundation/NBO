"""Complete follow-up catalogue: fixed generator, recentered common verifier.

The design is informed by the R27 failures. It is a source-frozen numerical
follow-up, not a blind population replication. Every cell and the paired old
verifier outcome are retained. The old-verifier diagnostic is separately timed.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import platform
import sys
import time
import numpy as np

R = Path(__file__).resolve().parents[1]
ROOT = R.parents[1]
sys.path.insert(0, str(ROOT/'revisions/2026-10-06-r27/code'))
sys.path.insert(0, str(R/'code'))
sys.path.insert(0, str(ROOT/'revisions/2026-10-05-r23/code'))
from experiment import economy
from entropic_certificate import candidate, certify as box_certify
from residual_certificate import certify


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def durable(path, row):
    with path.open('a', encoding='utf8') as f:
        f.write(json.dumps(row, sort_keys=True, allow_nan=False)+'\n')
        f.flush(); os.fsync(f.fileno())


def run(source_commit: str):
    if len(source_commit) != 40 or any(c not in '0123456789abcdef' for c in source_commit):
        raise ValueError('An immutable 40-character source commit is required')
    output = R/'results/primary'
    output.mkdir(parents=True, exist_ok=False)
    protocol = json.loads((R/'protocols/PROTOCOL.json').read_text())
    for name, expected in protocol['source_sha256'].items():
        if digest(R/name) != expected:
            raise RuntimeError('Frozen source hash mismatch: '+name)
    identity = dict(source_commit=source_commit, protocol_sha256=digest(R/'protocols/PROTOCOL.json'),
                    python=platform.python_version(), numpy=np.__version__,
                    platform=platform.platform(), started_ns=time.time_ns(),
                    run_id=os.environ.get('GITHUB_RUN_ID'),
                    threads={k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')})
    (output/'EXECUTION_IDENTITY.json').write_text(json.dumps(identity, indent=2)+'\n')
    start = time.perf_counter(); records=[]
    for d in protocol['dimensions']:
      for regime in protocol['regimes']:
       for risk in protocol['risk_per_dimension']:
        for method in protocol['methods']:
            key=f'entropic_d{d}_{regime}_risk{risk:g}_{method}'
            t0=time.perf_counter()
            row=dict(key=key,dimension=d,regime=regime,risk_per_dimension=risk,
                     theta=risk*d,method=method,status='attempted')
            model = gains = None
            try:
                model=economy(d,regime,protocol['horizon']); t1=time.perf_counter()
                gains,factor,counters=candidate(model,risk*d,method,protocol['gram_tolerance']); t2=time.perf_counter()
                certificate=certify(model,gains,risk*d,protocol['execution_error']); t3=time.perf_counter()
                p=output/(key+'.npz')
                np.savez_compressed(p,gains=gains,critic_factor=factor,
                                    **{n:model[n] for n in ('A','B','Q','R','Qf','Sigma')})
                with p.open('rb') as f: os.fsync(f.fileno())
                row.update(status='certified' if certificate['policy_gap_upper']<=protocol['policy_tolerance'] else 'uncertified',
                           certificate=certificate,counters=counters,candidate_sha256=digest(p),candidate_bytes=p.stat().st_size,
                           initialization_seconds=t1-t0,fitting_seconds=t2-t1,verification_seconds=t3-t2,
                           candidate_write_seconds=time.perf_counter()-t3,
                           mean_initial_action=float(np.mean(-gains[0]@np.ones(d))))
            except Exception as error:
                row.update(status='failed',exception=type(error).__name__,message=str(error))
            durable(output/'attempts.jsonl',row)
            row['complete_service_seconds']=time.perf_counter()-t0
            dt=time.perf_counter()
            try:
                if gains is None: raise RuntimeError('Candidate unavailable')
                old=box_certify(model,gains,risk*d,protocol['execution_error'])
                row.update(box_verifier_status='certified' if old['policy_gap_upper']<=protocol['policy_tolerance'] else 'uncertified',
                           box_policy_gap_upper=old['policy_gap_upper'])
            except Exception as error:
                row.update(box_verifier_status='failed',box_exception=type(error).__name__,box_message=str(error))
            row['box_diagnostic_seconds']=time.perf_counter()-dt
            durable(output/'services.jsonl',row); records.append(row)
            print(key,row['status'],'paired-box:',row['box_verifier_status'],flush=True)
    summary=dict(services=len(records),certified=sum(r['status']=='certified' for r in records),
                 failed=sum(r['status']=='failed' for r in records),uncertified=sum(r['status']=='uncertified' for r in records),
                 box_certified=sum(r['box_verifier_status']=='certified' for r in records),
                 box_failed=sum(r['box_verifier_status']=='failed' for r in records),
                 service_seconds_sum=sum(r['complete_service_seconds'] for r in records),
                 box_diagnostic_seconds_sum=sum(r['box_diagnostic_seconds'] for r in records),
                 execution_loop_seconds=time.perf_counter()-start,provenance=identity,
                 interpretation=protocol['interpretation'])
    assert len(records)==protocol['services']
    (output/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True)
    run(parser.parse_args().source_commit)
