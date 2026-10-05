"""Frozen deterministic construction study. Preserve failed checks and all clocks."""
from pathlib import Path
import hashlib, json, os, platform, resource, sys, time
import numpy as np
from constructive import ROOT, backward_nbo
from experiment import economy, riccati
from policy_certificate import certify
R = Path(__file__).resolve().parents[1]


def append(path, obj):
    with path.open('a') as f:
        f.write(json.dumps(obj, sort_keys=True, allow_nan=False)+'\n'); f.flush(); os.fsync(f.fileno())


def main():
    protocol = json.loads((R/'protocols/PROTOCOL.json').read_text())
    freeze = json.loads((R/'protocols/FREEZE.json').read_text())
    for p, h in freeze['files'].items():
        assert hashlib.sha256((R/p).read_bytes()).hexdigest() == h, p
    out = R/'results/primary'
    out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    records=[]
    for d in protocol['dimensions']:
      for regime in protocol['regimes']:
       for scale in protocol['initial_scale_multipliers']:
        for method in protocol['methods']:
            key=f'd{d}_{regime}_s{scale}_{method}'
            start=time.perf_counter()
            model=economy(d,regime,protocol['horizon'])
            if method=='backward-NBO':
                K,W,P,count=backward_nbo(model,protocol['tolerance'],scale,protocol['orientation_seed'])
            else:
                K=riccati(model);W=np.empty((0,));P=np.empty((0,))
                count={'hidden_updates':0,'ideal_hidden_update_cap':0,'gram_checks':0,
                       'actor_solves':protocol['horizon'],'own_policy_matrix_updates':protocol['horizon'],
                       'reference_policy_matrix_updates':0,'training_thresholds_met':True,'dates':[],
                       'simulation_transitions':0}
            constructed=time.perf_counter()
            cert=certify(model,K,protocol['execution_error_budget'])
            verified=time.perf_counter()
            candidate=out/(key+'.npz')
            with candidate.open('wb') as f:
                np.savez_compressed(f,gains=K,critic_factor=W,own_target_matrices=P,
                                   **{n:model[n] for n in ('A','B','Q','R','Qf','Sigma')})
                f.flush();os.fsync(f.fileno())
            record={'key':key,'dimension':d,'regime':regime,'scale':scale,'method':method,
                    'candidate_file':candidate.name,
                    'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),
                    'certificate':cert,'certified':bool(cert['policy_gap_upper']<=protocol['tolerance']),
                    'counters':count,'construction_seconds':constructed-start,
                    'verification_seconds':verified-constructed,
                    'candidate_bytes':candidate.stat().st_size,
                    'working_arrays_bytes':int(K.nbytes+W.nbytes+P.nbytes+sum(model[n].nbytes for n in ('A','B','Q','R','Qf','Sigma')))}
            append(out/'attempts.jsonl',record)
            end=time.perf_counter()
            service={k:v for k,v in record.items() if k not in ('counters','certificate')}
            service.update(total_service_seconds=end-start,
                           durable_write_and_audit_seconds=end-verified,
                           policy_gap_upper=cert['policy_gap_upper'],
                           implementation_gap_upper=cert['implementation_gap_upper'],
                           hidden_updates=count['hidden_updates'],ideal_hidden_update_cap=count['ideal_hidden_update_cap'],
                           actor_solves=count['actor_solves'],gram_checks=count['gram_checks'],
                           final_policy_checks=1,failed_final_policy_checks=int(not record['certified']))
            append(out/'services.jsonl',service);records.append(service)
            print(key,record['certified'],cert['policy_gap_upper'],end-start,flush=True)
    summary={'protocol':protocol,'freeze':freeze,'services':len(records),
             'certified':sum(x['certified'] for x in records),
             'runtime_seconds_before_summary':time.perf_counter()-started,
             'sum_service_seconds':sum(x['total_service_seconds'] for x in records),
             'process_high_water_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
             'python':platform.python_version(),'numpy':np.__version__,'platform':platform.platform(),
             'scope':'Frozen deterministic construction experiment. Isometric orientations are symmetries, not independent training trials. Both scale levels and every failure retained. No retrospective first-success clock.',
             'clock_scope':'Service clock includes initialization, reference evaluation, all factor updates and gram checks, actor solves, outward final verification, compressed writes, fsync and attempt-ledger write. Service-ledger and summary writes, imports, and environment setup are outside each service clock; loop total separately reported.'}
    (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('protocol','freeze')},indent=2))

if __name__=='__main__':main()
