#!/usr/bin/env python3
"""Build an evidence ledger from actual results, with reachable source provenance.
Program completion, test tolerance, and economic evidence class are separate.
"""
import argparse,hashlib,json,platform,subprocess
from pathlib import Path
import numpy as np, scipy, torch

ROOT=Path(__file__).resolve().parents[2]
R4=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clean(x):
    if isinstance(x,dict):return {k:clean(v) for k,v in x.items() if 'seconds' not in k and k not in ['elapsed','peak_rss_kib','source_sha256']}
    if isinstance(x,list):return [clean(v) for v in x]
    return x

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='replication/r4/output');ap.add_argument('--source-commit');a=ap.parse_args();out=Path(a.out).resolve()
    sources={str(p.relative_to(ROOT)):sha(p) for p in sorted(R4.glob('*.py'))};verified=False
    if a.source_commit:
        subprocess.run(['git','rev-parse','--verify',a.source_commit+'^{commit}'],cwd=ROOT,check=True,capture_output=True)
        for path,digest in sources.items():
            data=subprocess.check_output(['git','show',a.source_commit+':'+path],cwd=ROOT)
            assert hashlib.sha256(data).hexdigest()==digest,(path,'source commit does not identify executed bytes')
        verified=True
    required=['tests_results','reference_results','neural_results','analysis_results','graph_results','replay_results']
    required +=[f'safe_results_{s}' for s in [101,202,303]]+[f'resource_results_{d}_{s}' for d in [4,8,16] for s in [101,202,303]]
    ledger=[]
    for name in required:
        path=out/(name+'.json');data=json.loads(path.read_text())
        if name.startswith('resource_results'):
            cls=data['evidence_class'];metric={'cost_loss_upper_max':data['cost_excess_upper_max'],'reference_gap_max':data['reference_gap_max'],'constraint_violation_max':data['constraint_violation_max']}
            passed=data['cost_excess_upper_max']<1e-3 and data['reference_gap_max']<1e-7 and data['constraint_violation_max']<1e-10
            assert passed,name
            status='passed_declared_heldout_targets';threshold={'cost_loss_upper_max':1e-3,'reference_gap_max':1e-7,'constraint_violation_max':1e-10}
        elif name.startswith('safe_results'):
            cls=data['evidence_class'];metric={k:data[k] for k in ['initial_value','critic_vs_policy_max','sampled_feasible_gain_max','boundary_error']}
            status='reported_diagnostics_not_uniform_certificate';threshold=None
            assert data['boundary_error']<1e-12
        else:
            cls={'tests_results':'analytical_feature_and_finite_state_regression_suite','reference_results':'finite_stopped_diffusion_reference','neural_results':'neural_development_pilot','analysis_results':'independent_policy_and_occupation_comparison','graph_results':'automatic_differentiation_and_domain_tests','replay_results':'deposited_weight_replay'}[name]
            metric=None;threshold=None;status='assertions_completed' if name in ['tests_results','graph_results','replay_results'] else 'reported_diagnostics'
        ledger.append(dict(run_id=name,evidence_class=cls,execution_status='completed',tolerance_status=status,source_commit=a.source_commit,source_bytes_verified_against_commit=verified,
                           record=str(path.relative_to(ROOT)),record_sha256=sha(path),scientific_payload_sha256=hashlib.sha256(json.dumps(clean(data),sort_keys=True,separators=(',',':')).encode()).hexdigest(),metrics=metric,thresholds=threshold,
                           unmeasured_metrics_reason='Full numerical arrays and definitions are in the linked record; null means not a common cross-experiment metric.'))
    (out/'ledger.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in ledger))
    weights={str(p.relative_to(ROOT)):sha(p) for p in sorted(out.glob('*.npz'))}
    manifest=dict(revision='R4',branch='revision/econometrica-r4-2026-09-16',review_commit='79a7d84be2cbbf9bd5d181599ee110540128e3b5',source_commit=a.source_commit,
                  source_commit_verified=verified,source_sha256=sources,checkpoint_and_array_sha256=weights,
                  environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,torch=torch.__version__,torch_threads=torch.get_num_threads()),
                  ledger_records=len(ledger),ledger_sha256=sha(out/'ledger.jsonl'),timing_policy='Timing excluded from scientific payload digests, included in complete file digests.',
                  certification_policy='Resource gaps apply to enumerated finite trees and stored initial states in double precision. NDU continuum error certificates are not inferred from held-out residuals.')
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Validated',len(ledger),'evidence records; source commit verified:',verified)
if __name__=='__main__':main()
