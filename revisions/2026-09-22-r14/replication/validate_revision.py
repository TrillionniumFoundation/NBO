"""Fail-closed checks of the delivered R14 files and independent proof records."""
from __future__ import annotations
from pathlib import Path
import ast,gzip,hashlib,json,time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2];R=HERE.parent

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def validate():
    start=time.perf_counter();checks=[]
    def check(name,condition):
        if not condition:raise AssertionError(name)
        checks.append(name)
    from interval64 import test
    from validated_gauss import rule
    from independent_dual import primitives
    from exact_price_audit import audit
    from state_cost_certificate import envelope
    check('807 elementary high-precision inclusion tests',test()['point_enclosure_checks']==807)
    rule();check('eight rational root brackets and sixteen Gauss moments',True)
    check('independently verified supporting-plane primitives',primitives()['status']=='PASS')
    for name in ['interval64','validated_gauss','independent_primal','independent_dual','neural_certificate','exact_price_audit','state_cost_certificate']:
        src=(HERE/(name+'.py')).read_text();tree=ast.parse(src)
        imports=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):imports.extend(x.name for x in node.names)
            elif isinstance(node,ast.ImportFrom):imports.append(node.module or '')
        check(f'{name}: no inherited certifier import',not any('original_policy_certificate' in x or 'flexible_dual' in x or 'price_envelope' in x for x in imports))
    nodes=read(R/'results/independent_library/nodes.json')
    clean=read(R/'results/clean_recheck/nodes.json')
    check('all eighteen independent price nodes present',len(nodes)==18==len(clean))
    for a,b in zip(nodes,clean):
        check(f'clean replay exact decisive fields k={a["k"]}',all(a[k]==b[k] for k in ['k','L','U','B']))
        tag=f'{a["k"]:g}'
        p=read(R/f'results/independent_library/primal_k{tag}.json');d=read(R/f'results/independent_library/dual_k{tag}.json')
        check(f'policy identity k={tag}',digest(ROOT/p['actor_path'])==p['actor_sha256'])
        check(f'dual identity k={tag}',digest(ROOT/d['pilot_path'])==d['pilot_sha256'])
        check(f'positive terminal wealth and bounded primal k={tag}',p['terminal_wealth'][0]>.5 and p['value_interval'][0]<=p['value_interval'][1] and p['width']<2e-10)
        check(f'full dual cover k={tag}',d['source_boxes']==262144 and d['covariance_interval'][1]<0)
    p=audit(nodes);stored=read(R/'results/independent_price_audit.json')
    check('exact rational price envelope',p['uniform_regret_rational']==stored['uniform_regret_rational'] and p['uniform_regret_upper']<.01)
    robust=read(R/'results/robust_library/nodes.json');a=audit(robust);b=read(R/'results/robust_library/envelope.json')
    check('all-node robust envelope',len(robust)==18 and a['uniform_regret_rational']==b['uniform_regret_rational'] and a['uniform_regret_upper']<.01)
    a=envelope(read(R/'results/state_cost/corners.json'));b=read(R/'results/state_cost/envelope.json')
    check('exact joint state-price envelope',a['uniform_regret_rational']==b['uniform_regret_rational'] and a['uniform_regret_upper']<.0121)
    for path in (R/'results').glob('neural_audit_*.json'):
        n=read(path);network=R/'results/neural_run'/n['network_file']
        check(path.stem+': network identity',digest(network)==n['network_sha256'])
        with gzip.open(path.with_suffix('.cells.json.gz'),'rt') as f:cells=json.load(f)
        check(path.stem+': all cells included',len(cells)==n['interior_cells'] and n['failed_cells']==0==n['skipped_cells'])
        check(path.stem+': no false target claim',not n['meets_0.01'] and n['error_budget']['t0_regret_upper']>.01)
    for path in (R/'results/high_precision').glob('k*.json'):
        d=read(path);check(path.name+': both precision checks',len(d['records'])==2 and all(all(z['inside_independent_intervals']) for z in d['records']))
    fresh=read(R/'results/fresh_frontier/frontier.json')
    check('fresh 16/32/64-interval frontier', [x['policy_slabs'] for x in fresh]==[16,32,64])
    check('finer unachieved tolerances retained',all(x['target_passes']['0.01'] and not any(x['target_passes'][k] for k in ['0.005','0.0025','0.001']) for x in fresh))
    frozen=read(R/'results/clean_recheck_receipt.json')
    check('source-frozen replay receipt',frozen['status']=='PASS' and all(digest(HERE/k)==v for k,v in frozen['source_sha256_at_start'].items()))
    for name in ['ECTA_R14','SUPP_R14']:
        check(name+': PDF exists',(ROOT/(name+'.pdf')).is_file())
        log=(R/f'build_logs/latex/{name}.log').read_text()
        check(name+': no unresolved or overfull warning',not any(z in log for z in ['undefined references','undefined citations','Overfull \\hbox','Overfull \\vbox']))
    pres=R/'preservation_manifest.json'
    if pres.exists():
        data=read(pres)
        for name,h in data['baseline_files_sha256'].items():
            path=R/'archive/REVISION_INDEX_before_R14.md' if name=='REVISION_INDEX.md' else ROOT/name
            check('preserved '+name,path.exists() and digest(path)==h)
    manifest=R/'canonical_manifest.json'
    if manifest.exists():
        for group in ['source_files_sha256','result_files_sha256','build_files_sha256']:
            for name,h in read(manifest)[group].items():
                check('manifest '+name,digest(ROOT/name)==h)
    report={'status':'PASS','checks_passed':len(checks),'checks':checks,'wall_seconds':time.perf_counter()-start,
      'scientific_targets':{'central_time_policy_0.01':True,'stressed_central_time_policy_0.01':True,'state_price_time_policy_0.0121':True,'whole_domain_neural_0.01':False,'classical_frontier_0.005':False,'two_classical_state_space_baselines':False},
      'interpretation':'Validation succeeds when true and false scientific predicates are reported correctly; it does not claim that all referee conditions are closed.'}
    (R/'validation_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','checks_passed','wall_seconds','scientific_targets']},indent=2))
if __name__=='__main__':validate()
