"""Execute the complete source-frozen R27 catalogue without selective retries."""
from pathlib import Path
import hashlib
import json
import os
import platform
import sys
import time
import numpy as np
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
sys.path.insert(0,str(R/'code'))
sys.path.insert(0,str(ROOT/'revisions/2026-10-05-r23/code'))
from experiment import economy, riccati
from policy_certificate import certify as additive_certify
from primitive_budget import solve
from entropic_certificate import candidate, certify as entropic_certify


def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def durable_jsonl(path, row):
    with path.open('a',encoding='utf8') as f:
        f.write(json.dumps(row,sort_keys=True,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())


def run():
    output=R/'results/primary';output.mkdir(parents=True,exist_ok=False)
    protocol=json.loads((R/'protocols/PROTOCOL.json').read_text())
    environment=dict(python=platform.python_version(),numpy=np.__version__,platform=platform.platform(),
                     threads=1,protocol_sha256=digest(R/'protocols/PROTOCOL.json'),
                     frozen_source_commit=os.environ.get('GITHUB_SHA','UNCOMMITTED'),
                     run_id=os.environ.get('GITHUB_RUN_ID'),started_ns=time.time_ns())
    if environment['frozen_source_commit']=='UNCOMMITTED':
        raise RuntimeError('Primary execution requires its committed source identity')
    (output/'EXECUTION_IDENTITY.json').write_text(json.dumps(environment,indent=2)+'\n')
    start=time.perf_counter();records=[]
    for family in ('primitive','entropic'):
      for d in protocol['dimensions']:
       for regime in protocol['regimes']:
        for risk in ([0.] if family=='primitive' else protocol['risk_per_dimension']):
         for method in protocol[family+'_methods']:
          key=f'{family}_d{d}_{regime}_risk{risk:g}_{method}'
          t0=time.perf_counter();rec=dict(key=key,family=family,dimension=d,regime=regime,
              risk_per_dimension=risk,theta=risk*d,method=method,status='attempted')
          try:
            model=economy(d,regime,protocol['horizon']);t1=time.perf_counter()
            if family=='primitive':
                if method=='NBO-primitive': K,W,counters=solve(model,protocol['policy_tolerance'])
                else:
                    K=riccati(model);W=np.zeros_like(K)
                    counters=dict(hidden_updates=0,gram_checks=0,actor_solves=model['horizon'],
                                  own_policy_matrix_updates=model['horizon'],simulation_transitions=0,
                                  all_training_thresholds_met=True)
            else:
                K,W,counters=candidate(model,risk*d,method,protocol['gram_tolerance'])
            t2=time.perf_counter()
            cert=(additive_certify(model,K,protocol['execution_error']) if family=='primitive'
                  else entropic_certify(model,K,risk*d,protocol['execution_error']))
            t3=time.perf_counter()
            p=output/(key+'.npz')
            np.savez_compressed(p,gains=K,critic_factor=W,**{n:model[n] for n in ('A','B','Q','R','Qf','Sigma')})
            with p.open('rb') as f:os.fsync(f.fileno())
            stored_bytes=p.stat().st_size
            rec.update(status='certified' if cert['policy_gap_upper']<=protocol['policy_tolerance'] else 'uncertified',
                       certificate=cert,counters=counters,candidate_sha256=digest(p),candidate_bytes=stored_bytes,
                       mean_initial_action=float(np.mean(-K[0]@np.ones(d))),
                       initialization_seconds=t1-t0,fitting_seconds=t2-t1,verification_seconds=t3-t2,
                       candidate_write_seconds=time.perf_counter()-t3)
          except Exception as error:
            rec.update(status='failed',exception=type(error).__name__,message=str(error))
          # Include a durable detailed attempt write, then close its bill in the
          # service ledger. The ledger write itself is common reporting overhead.
          durable_jsonl(output/'attempts.jsonl',rec)
          rec['complete_service_seconds']=time.perf_counter()-t0
          durable_jsonl(output/'services.jsonl',rec);records.append(rec)
          print(key,rec['status'],rec['complete_service_seconds'],flush=True)
    summary=dict(services=len(records),certified=sum(r['status']=='certified' for r in records),
                 failed=sum(r['status']=='failed' for r in records),
                 uncertified=sum(r['status']=='uncertified' for r in records),
                 service_seconds_sum=sum(r['complete_service_seconds'] for r in records),
                 execution_loop_seconds=time.perf_counter()-start,
                 provenance=environment,scope=protocol['primary_estimand'])
    assert len(records)==protocol['primary_services'],summary
    (output/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':run()
