"""R30 execution of the inherited, previously frozen R29 finite catalogue.

No outcome-dependent budget, tolerance, seed, method, or exception filtering.
The final verifier is independent of the generator and its nominal targets.
"""
from pathlib import Path
import hashlib
import json
import os
import platform
import resource
import sys
import time
import numpy as np
R = Path(__file__).resolve().parents[1]
ROOT = R.parents[1]
for revision in ('2026-10-05-r23', '2026-10-06-r27', '2026-10-06-r28', '2026-10-06-r29'):
    sys.path.insert(0, str(ROOT / 'revisions' / revision / 'code'))
from experiment import economy
from entropic_certificate import candidate
from residual_certificate import certify
from entropic_budget import solve


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def durable(path, row):
    with path.open('a', encoding='utf8') as handle:
        handle.write(json.dumps(row, sort_keys=True, allow_nan=False) + '\n')
        handle.flush()
        os.fsync(handle.fileno())


def run():
    manifest = json.loads((R / 'protocols/SOURCE_FREEZE.json').read_text())
    for name, expected in manifest['files'].items():
        if digest(ROOT / name) != expected:
            raise RuntimeError('Frozen scientific input mismatch: ' + name)
    commit = os.environ.get('NBO_SOURCE_COMMIT', '')
    if len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        raise RuntimeError('NBO_SOURCE_COMMIT must be the remote source-freeze SHA')
    protocol = json.loads((R / 'protocols/PROTOCOL.json').read_text())
    out = R / 'results/primary'
    out.mkdir(parents=True, exist_ok=False)
    identity = dict(source_commit=commit, inherited_design_commit=manifest['base_commit'],
        source_manifest_sha256=digest(R / 'protocols/SOURCE_FREEZE.json'),
        protocol_sha256=digest(R / 'protocols/PROTOCOL.json'), python=platform.python_version(),
        numpy=np.__version__, platform=platform.platform(), machine=platform.machine(),
        execution_location='local research container', started_ns=time.time_ns(),
        requested_threads={k: os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')})
    (out / 'EXECUTION_IDENTITY.json').write_text(json.dumps(identity, indent=2) + '\n')
    rows = []
    pair = 0
    closing_ledger_seconds = 0.
    begin = time.perf_counter()
    for d in protocol['dimensions']:
      for regime in protocol['regimes']:
       for risk in protocol['risk_per_dimension']:
        for seed in protocol['seeds']:
         methods = protocol['methods'] if pair % 2 == 0 else protocol['methods'][::-1]
         pair += 1
         for method in methods:
          key = f'd{d}_{regime}_rho{risk:g}_seed{seed}_{method}'
          t0 = time.perf_counter()
          row = dict(key=key, dimension=d, horizon=protocol['horizon'], regime=regime,
                     risk_per_dimension=risk, theta=risk*d, seed=seed, method=method, status='attempted')
          try:
            model = economy(d, regime, protocol['horizon'])
            t1 = time.perf_counter()
            if method == 'NBO-primitive-risk':
                K, W, counters = solve(model, risk*d, protocol['policy_tolerance'], seed=seed, slack=protocol['slack'])
            else:
                K, W, counters = candidate(model, risk*d, 'structural')
            t2 = time.perf_counter()
            path = out / (key + '.npz')
            np.savez_compressed(path, gains=K, critic_factor=W,
                **{name: model[name] for name in ('A','B','Q','R','Qf','Sigma')})
            with path.open('rb') as handle:
                os.fsync(handle.fileno())
            t3 = time.perf_counter()
            row.update(candidate_sha256=digest(path), candidate_bytes=path.stat().st_size,
                returned_array_bytes=K.nbytes+W.nbytes, counters=counters,
                initial_action=(-K[0] @ np.ones(d)).tolist(),
                mean_initial_action=float(np.mean(-K[0] @ np.ones(d))),
                initialization_seconds=t1-t0, fitting_seconds=t2-t1, candidate_write_seconds=t3-t2)
            cert = certify(model, K, risk*d, protocol['execution_error'])
            row.update(certificate=cert, verification_seconds=time.perf_counter()-t3,
                status='certified' if cert['policy_gap_upper'] <= protocol['policy_tolerance']
                and counters['all_training_thresholds_met'] else 'uncertified')
          except Exception as error:
            row.update(status='failed', exception=type(error).__name__, message=str(error))
          durable(out / 'attempts.jsonl', row)
          row['complete_service_seconds'] = time.perf_counter()-t0
          closing_start = time.perf_counter()
          durable(out / 'services.jsonl', row)
          closing_ledger_seconds += time.perf_counter()-closing_start
          rows.append(row)
          print(key, row['status'], row['complete_service_seconds'], flush=True)
    summary = dict(services=len(rows), certified=sum(x['status']=='certified' for x in rows),
        failed=sum(x['status']=='failed' for x in rows), uncertified=sum(x['status']=='uncertified' for x in rows),
        complete_service_seconds_sum=sum(x['complete_service_seconds'] for x in rows),
        closing_ledger_seconds=closing_ledger_seconds, execution_loop_seconds=time.perf_counter()-begin,
        process_maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        memory_scope='Process high-water mark; not a method-specific peak-memory comparison', identity=identity)
    assert len(rows) == protocol['primary_services'], summary
    (out / 'SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    run()
