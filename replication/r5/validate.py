#!/usr/bin/env python3
"""Independent replays and tolerances; never infer a diffusion bound from tests."""
from __future__ import annotations
import argparse, gc, hashlib, json, platform, subprocess, sys
from pathlib import Path
import numpy as np
import scipy
import torch
from contracts import Economy, Kernel, interval_certificate, switching, old, ROOT
from economic_robustness import read_bank, sign_certificate
import resource_ablation as resource
import persistent_game as game
OUT=ROOT/'replication/r5/output'
BASE='11082cc5054e91d3b2ac27826705f374ca74bfae'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def test_contracts():
    e=Economy();bank=read_bank();summary=json.loads((OUT/'contracts.json').read_text())
    assert len(e.menu)+len(e.extra[0].actions[0])==summary['total_action_count']
    diagnostic=old.action_mesh((7,7,11))
    assert all(np.any(np.max(abs(e.menu-a),axis=1)<1e-14) for a in diagnostic)
    # Compare with the separate original NumPy interpolation/backup implementation,
    # not the array contractions used to solve the revised finite problem.
    rng=np.random.default_rng(91836);values=rng.normal(size=e.shape);pol=rng.integers(len(e.menu),size=e.ns)
    original=old.backup(values,e.states,e.menu[pol],1/e.steps,e.model)[0]
    replay=e.common.base[np.arange(e.ns),pol]-2*e.common.effort[np.arange(e.ns),pol]+e.common.selected(pol,values.ravel())
    kernel_error=float(np.max(abs(original-replay)));assert kernel_error<2e-12
    feature_error=0.;anchor_gain=0.;identity_error=0.
    for i,row in enumerate(bank):
        f=e.evaluate(row['policy']);feature_error=max(feature_error,float(np.max(abs(f-row['feature']))))
        v=f[0]+row['d']*f[1]-2*f[2]
        anchor_gain=max(anchor_gain,float(e.one_step_gain(v,row['d']).max()))
        z=e.endpoint_discount(row['policy']);identity_error=max(identity_error,float(np.max(abs(.04*f[1]+z-1))))
        if i%10==0:print('ANCHOR_AUDIT',i,flush=True)
    assert feature_error<2e-11 and anchor_gain<2e-10 and identity_error<2e-12
    cert=max(interval_certificate(bank,i,i+1)['upper_loss'] for i in range(len(bank)-1))
    assert cert<1e-3-1e-9 and abs(cert-summary['uniform_certificate'])<1e-10
    switch_defect=0.;max_upper=0.;F=np.stack([r['feature'] for r in bank]);ds=np.array([r['d'] for r in bank])
    for d in rng.uniform(0,1,37):
        pol=switching(bank,float(d),2.);f=e.evaluate(pol);J=f[0]+d*f[1]-2*f[2];L=np.max(F[:,0]+d*F[:,1]-2*F[:,2],axis=0)
        left=min(int(np.searchsorted(ds,d,side='right')-1),len(bank)-2);a,b=bank[left],bank[left+1];lam=(d-a['d'])/(b['d']-a['d'])
        U=(1-lam)*a['value']+lam*b['value'];switch_defect=max(switch_defect,float(np.max(L-J)));max_upper=max(max_upper,float(np.max(U-J)))
        assert np.max(J-U)<1e-10
    assert switch_defect<1e-10 and max_upper<1e-3
    signs=sign_certificate(e,bank);stored=json.loads((OUT/'sign_certificate.json').read_text());assert signs['groups']==stored['groups']
    del e;gc.collect()
    return dict(anchors=len(bank),kernel_vs_independent_numpy=kernel_error,feature_replay_error=feature_error,
        all_anchor_bellman_gain=anchor_gain,duration_settlement_identity=identity_error,
        entire_interval_value_upper=cert,random_query_switching_defect=switch_defect,
        random_query_upper_loss=max_upper,portfolio_sign_groups=signs['groups'],
        scope='All anchors and states are audited; the whole parameter interval is certified by exact piecewise-affine endpoint/intersection calculations, not random tests.')
def test_resources():
    summary=json.loads((OUT/'resource_ablation.json').read_text());checks=[]
    for row in summary['cases']:
        d,seed=row['d'],row['seed'];critics,actors,x,test,original=resource.load(d,seed)
        relearnt,timing=resource.train_critics(d,seed,'relu')
        error=max(float(np.max(abs(critics[n].value(test)-relearnt[n].value(test)))) for n in range(3))
        assert error<1e-9
        replay=resource.evaluate(critics,None,test,'zero');cost_error=float(np.max(abs(replay['cost']-np.array(row['zero']['cost']))));assert cost_error<1e-9
        assert row['actor']['loss_upper_max']<1e-3 and row['zero']['loss_upper_max']<1e-3 and row['reference_gap']<1e-7
        assert row['actor_cost_difference_max']<1e-8
        quad=max(log['fit']['projected_gradient'] for log in row['quadratic_training']['logs']);assert quad<1e-8
        checks.append(dict(d=d,seed=seed,critic_retraining_error=error,zero_policy_replay_error=cost_error,
            actor_free_upper_loss=row['zero']['loss_upper_max'],quadratic_upper_loss=row['quadratic']['loss_upper_max'],quadratic_projected_gradient=quad))
        print('RESOURCE_AUDIT',d,seed,flush=True)
    for w in summary['workloads']:
        assert w['validation_reference_gap_max']<1e-7 and w['reference_matched_gap_max']<1e-3
        assert w['target_pass'] and w['loss_upper_max']<1e-3
    return dict(cases=checks,workload_sizes=[w['queries'] for w in summary['workloads']],
        timing_scope='Measured single-thread workloads; no universal speed theorem or extrapolated actor advantage.')
def test_game():
    data=json.loads((OUT/'persistent_game.json').read_text());result={}
    for name in ('reset','persistent'):
        row=data[name];p=np.array(row['policies']);br=game.all_date_best_response(p,row['survival'])
        assert br['max_positive_gain']<1e-10 and np.max(abs(br['baseline']-np.array(row['values'])))<1e-12
        bad=p.copy();bad[-1,0,1,1,0]=1.;neg=game.all_date_best_response(bad,row['survival'])
        assert np.max(np.array(neg['gains'])[-1])>.1
        result[name]=dict(all_date_gain=br['max_positive_gain'],date_player_state_count=p.size,
            late_date_negative_control=float(np.max(np.array(neg['gains'])[-1])))
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-commit');a=ap.parse_args();result={}
    result['contract']=test_contracts();result['resource']=test_resources();result['game']=test_game()
    result['threshold_status']='all declared assertions passed'
    sources={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'replication/r5').glob('*.py'))}
    sources.update({str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'replication/r5').glob('*.sh'))})
    verified=False
    if a.source_commit:
        subprocess.run(['git','rev-parse','--verify',a.source_commit+'^{commit}'],cwd=ROOT,check=True,capture_output=True)
        for path,digest in sources.items():
            assert hashlib.sha256(subprocess.check_output(['git','show',a.source_commit+':'+path],cwd=ROOT)).hexdigest()==digest,path
        verified=True
    result['source_commit']=a.source_commit;result['source_bytes_verified']=verified
    (OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    oldinputs=[ROOT/'replication/r4/solver.py',ROOT/'replication/r4/coupled_resource.py']
    oldinputs+=sorted((ROOT/'replication/r4/output').glob('safe_policy_*.npz'))
    oldinputs+=sorted((ROOT/'replication/r4/output').glob('resource_weights_*.npz'))
    oldinputs+=sorted((ROOT/'replication/r4/output').glob('resource_results_*.json'))
    manifest=dict(revision='R5',review_base=BASE,source_commit=a.source_commit,source_commit_verified=verified,
        sources_sha256=sources,immutable_inputs_sha256={str(p.relative_to(ROOT)):sha(p) for p in oldinputs},
        outputs_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(OUT.iterdir()) if p.suffix in ('.json','.npz') and p.name!='manifest.json'},
        environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,torch=torch.__version__,platform=platform.platform(),threads=torch.get_num_threads()),
        interpretation='Finite-model double-precision certificates and measured workloads. No Brownian first-exit, continuous-action, interval-arithmetic, or journal-acceptance claim.')
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('ALL R5 VALIDATIONS PASSED',flush=True)
if __name__=='__main__':main()
