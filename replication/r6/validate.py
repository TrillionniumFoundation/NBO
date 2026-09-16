#!/usr/bin/env python3
"""R6 evidence validation and read-only replay of the inherited R5 checks."""
from common import *
import argparse,subprocess,importlib.util
import scipy,torch
import contracts

def read(n):return json.loads((OUT/(n+'.json')).read_text())

def historical_replay():
    spec=importlib.util.spec_from_file_location('historical_r5_validation',ROOT/'replication/r5/validate.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    def exact_economy():
        e=contracts.Economy();accelerate_kernel(e);return e
    mod.Economy=exact_economy
    # These functions return evidence; their main() writer is deliberately NOT called.
    return dict(contract=mod.test_contracts(),resource=mod.test_resources(),game=mod.test_game())

def preserved(base):
    raw=subprocess.check_output(['git','ls-tree','-rz',base],cwd=ROOT);checked=0
    for entry in raw.split(b'\0'):
        if not entry:continue
        meta,name=entry.split(b'\t',1);name=name.decode();expected=meta.decode().split()[2]
        if name in ('README.md','REVISION_INDEX.md'):continue
        p=ROOT/name;assert p.exists(),name
        actual=subprocess.check_output(['git','hash-object',str(p)],cwd=ROOT,text=True).strip()
        assert actual==expected,('historical file changed',name);checked+=1
    return dict(base_commit=base,historical_files_byte_identical=checked,allowed_root_pointer_updates=['README.md','REVISION_INDEX.md'])

def run(source=None,base=None,with_history=True):
    unit=read('unit_tests');b=read('bank_comparison');k=read('kernel_certificate');t=read('transport');m=read('mechanism');q=read('structural_qp')
    assert unit['random_full_state_parameter_checks']==660 and unit['exhaustive_policy_checks']==110
    assert b['statewise_ols']['uniform_bound']<1e-3
    assert b['restricted_neural_free_bank']['uniform_bound_vs_original_full_target']<1e-3
    assert len(k['rows'])==3 and [x['d'] for x in k['rows']]==[0.,.5,1.]
    for row in k['rows']:
        assert row['uniform_bound']<1e-3 and row['anchors'][0]==0 and row['anchors'][-1]==1
        ivs=row['intervals'];assert ivs[0]['left']==0 and ivs[-1]['right']==1
        assert all(x['right']==y['left'] for x,y in zip(ivs[:-1],ivs[1:]))
        assert max(x['bound'] for x in ivs)==row['uniform_bound']
        assert all(x['actual_max_loss']<=row['uniform_bound']+2e-10 and x['minimum_upper_slack']>=-2e-10 for x in row['validation_checks'])
    for row in q['rows']:
        assert row['qp_max_gap']<1e-3+2e-11 and row['learned_loss_upper_vs_tight']<1e-3+1e-10
        assert row['gradient_error']<2e-11 and row['feasibility_violation']<2e-12
    for row in m['rows']:
        op=row['option_values'];assert min(op.values())>-2e-11
        assert abs(row['adjustable']['delta']-row['no_deliberate_adjustment']['delta']-(op['positive']-op['nonpositive']))<2e-11
    for row in m['rows']:
        if row['d'] in (.375,.4,.5):assert row['adjustable']['delta']>0>row['no_deliberate_adjustment']['delta']
        if row['d']==1.:assert min(row['adjustable']['delta'],row['no_deliberate_adjustment']['delta'])>0
    for row in m['brackets']:
        if row['bracket']:
            assert row['low_delta']<=0<row['high_delta'] and row['bracket'][1]-row['bracket'][0]<=2e-5
    result=dict(status='all declared R6 assertions passed',unit_tests=unit,
        transition_uniform_bounds=[r['uniform_bound'] for r in k['rows']],
        inherited_replay=historical_replay() if with_history else 'not invoked in this local check',
        preservation=preserved(base) if base else 'base not supplied in this local check')
    sources={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'replication/r6').glob('*')) if p.suffix in ('.py','.sh','.md')}
    sources.update({str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'revisions/2026-09-16-r6/paper').glob('*.tex')) if not p.name.startswith('table_r6_')})
    for p in (ROOT/'ECTA_R6.tex',ROOT/'SUPP_R6.tex'):sources[str(p.relative_to(ROOT))]=sha(p)
    if source:
        subprocess.run(['git','rev-parse','--verify',source+'^{commit}'],cwd=ROOT,check=True,capture_output=True)
        for p,digest in sources.items():assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+p],cwd=ROOT)).hexdigest()==digest,p
    result['source_commit']=source;result['source_bytes_verified']=bool(source)
    save('validation.json',result)
    inputs=[ROOT/'replication/r4/solver.py',ROOT/'replication/r4/coupled_resource.py',ROOT/'replication/r5/contracts.py']
    inputs+=sorted((ROOT/'replication/r4/output').glob('safe_policy_*.npz'))+sorted((ROOT/'replication/r4/output').glob('resource_weights_*.npz'))
    save('manifest.json',dict(revision='R6',review_base=base,source_commit=source,source_commit_verified=bool(source),sources_sha256=sources,
        immutable_inputs_sha256={str(p.relative_to(ROOT)):sha(p) for p in inputs},
        outputs_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(OUT.iterdir()) if p.suffix in ('.json','.npz') and p.name!='manifest.json'},
        environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,torch=torch.__version__,
                         platform=platform.platform(),torch_threads=torch.get_num_threads()),
        scope='Exhaustive finite action/state certificates over declared parameter intervals, double precision; no directed rounding, diffusion transfer, universal neural advantage or journal decision.'))
    print('ALL R6 VALIDATIONS PASSED',flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source-commit');ap.add_argument('--base-commit');ap.add_argument('--skip-history',action='store_true');a=ap.parse_args()
    run(a.source_commit,a.base_commit,not a.skip_history)
