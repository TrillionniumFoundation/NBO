"""Validate the committed evidence without rerunning stochastic training.

Successful validation establishes consistency and provenance, not a mathematical
precision target or acceptance of a scientific claim.
"""
from __future__ import annotations
import hashlib,json,math,pathlib,statistics
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[3]
BASE=ROOT/'revisions/2026-09-22-r8'; R=BASE/'results'
def load(name):return json.loads((R/name).read_text())
def check_close(a,b,atol=2e-8):
    if not math.isclose(float(a),float(b),rel_tol=1e-8,abs_tol=atol):
        raise AssertionError((a,b))
def run():
    manifest=load('execution_manifest.json')
    assert manifest['source_commit']=='14ecbd481b0586cfbb72a0c00239184a4a2b0553'
    assert manifest['author_commit']=='991ea8dde5bad6ba912eb8cc48b0cb48dbdd6c2a'
    verified=0
    for group in ['source_sha256','result_sha256']:
        for path,digest in manifest[group].items():
            p=ROOT/path
            assert p.is_file(),f'Missing execution input/output: {path}'
            assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,f'Changed execution input/output: {path}'
            verified+=1
    summary={x['dimension']:x for x in load('external_summary.json')['rows']}
    assert set(summary)=={8,16}
    paired=[]
    for d in [8,16]:
        means=[]
        for seed in range(400,406):
            row=load(f'external_d{d}_s{seed}.json')
            assert row['dimension']==d and row['seed']==seed and row['audit_paths']==4096
            z=np.load(R/f'external_d{d}_s{seed}_paths.npz')
            for method in ['nbo','soc']:
                assert (R/f'external_d{d}_s{seed}_{method}.pt').is_file()
                for n in [64,128]:
                    values=z[f'{method}_{n}'].astype(float)
                    assert values.shape==(4096,) and np.isfinite(values).all()
                    check_close(values.mean(),row['methods'][method][f'mean_cost_{n}'])
                delta=z[f'{method}_128'].astype(float)-z[f'{method}_64'].astype(float)
                check_close(delta.mean(),row['methods'][method]['mesh_change'])
                assert row['methods'][method]['training_seconds']>=10
                assert row['methods'][method]['setup_and_training_seconds']>=row['methods'][method]['training_seconds']
            diff=z['nbo_128'].astype(float)-z['soc_128'].astype(float)
            check_close(diff.mean(),row['paired_difference'])
            check_close(diff.std(ddof=1)/math.sqrt(4096),row['paired_path_standard_error'])
            means.append(float(diff.mean()))
        mean=statistics.mean(means)
        half=2.570581835636314*statistics.stdev(means)/math.sqrt(6)
        check_close(mean,summary[d]['paired_mean'])
        check_close(mean-half,summary[d]['paired_t_95'][0])
        check_close(mean+half,summary[d]['paired_t_95'][1])
        paired.append({'dimension':d,'seeds':6,'mean_from_raw_arrays':mean,'paired_t_95':[mean-half,mean+half]})
    geometry=[]
    for seed in range(300,306):
        x=load(f'geometry_s{seed}.json');c=x['certificate']
        assert x['seed']==seed and x['steps']==4000 and len(x['weights'])==4
        assert all(math.isfinite(v) for v in x['weights'])
        assert 0<c['regret_upper_bound']<.01 and c['meets_target']
        geometry.append(c['regret_upper_bound'])
    continuous=load('continuum_witnesses.json')
    assert len(continuous['records'])==2
    for x in continuous['records']:
        p=ROOT/'revisions/2026-09-21-r5/results'/f"{x['tag']}.npz"
        assert hashlib.sha256(p.read_bytes()).hexdigest()==x['policy_sha256']
        assert x['continuous_regret_upper_bound_t0']>.01 and not x['meets_target']
        C=-math.expm1(-.04)/.04
        check_close(8+(x['beta']-x['alpha'])*C,x['continuous_regret_upper_bound_t0'])
    for x in load('safeguard_results.json'):
        z=np.load(R/f"threshold_{x['tag']}_{x['target']:g}.npz")
        old=ROOT/'revisions/2026-09-21-r5/results'
        cfg=json.loads((old/f"{x['tag']}.json").read_text())['config']
        original=np.load(old/f"{x['tag']}.npz")['proposal'].reshape(cfg['n'],cfg['nu'],cfg['nx'],3)
        changed=z['policy'].reshape(original.shape)
        fraction=np.any(np.abs(changed[:,1:-1,1:-1]-original[:,1:-1,1:-1])>1e-10,axis=-1).mean()
        check_close(fraction,x['history'][-1]['overridden_fraction'])
        check_close(np.max(z['bound'][0]),x['history'][-1]['localized_bound'])
        assert x['final_pass']==(x['history'][-1]['localized_bound']<=x['target'])
    meshes=load('mesh_results.json')
    assert len(meshes)==12
    assert {x['factor'] for x in meshes}=={'time','state','action','joint_cost'}
    assert all(x['continuum_error_bound'] is None for x in meshes)
    assert load('algebra_results.json')['random_jets']==1000
    report={'status':'passed','bound_files_checked':verified,'execution_commit':manifest['source_commit'],
        'execution_run':manifest['run_id'],'paired_statistics_recomputed':paired,
        'learned_geometry_regret_range':[min(geometry),max(geometry)],
        'original_continuum_precision_target_met':False,
        'interpretation':'Provenance, completeness and numerical consistency validation. Not a declaration that all scientific precision or scaling requirements are met.'}
    (BASE/'validation_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':run()
