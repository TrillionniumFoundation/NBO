"""Materialize actual science files, then freeze them before executing services.

No experiment runs in this preparation step. The inherited R35 generator is
checked by its existing source-freeze installer before these explicit changes.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
root=Path(__file__).resolve().parents[3]
r=root/'revisions/2026-10-07-r37'
subprocess.run([sys.executable,str(root/'revisions/2026-10-06-r35/publication/install_scientific_inputs.py')],check=True)
s=(root/'revisions/2026-10-06-r35/code/exact_comparison.py').read_text()
def replace(old,new):
    global s
    if old not in s:raise RuntimeError('Missing inherited source anchor: '+old)
    s=s.replace(old,new)
replace('R35 comparison on the unaltered R34 specified construction primitives.','R37 comparison on the unaltered R34 specified construction primitives.')
replace('import quadratic_refresh as qr\nr = qr.r','import adaptive_refresh as ar\nqr = ar.qr\nr = ar.r')
replace("method='quadratic-refresh'","method='adaptive-cached'")
replace('if t == T-1:',"if t == T-1 or method == 'structural':")
replace("if method=='quadratic-refresh'\n                  else","if method in ('quadratic-refresh','adaptive-cached')\n                  else")
replace("            elif method=='linear-warm':", """            elif method=='adaptive-cached':
                relative_tolerance = qr.policy_relative_allowance(
                    gram_allowance=tolerance, dimension=d, target_upper=3)
                cap = ar.refresh(factor, center, m=F(3,2),
                    tolerance=relative_tolerance, max_bits=128, max_updates=32)
                factor = cap.pop('factor')
                traces = cap['trace']
            elif method=='linear-warm':""")
replace("for j in range(cap['updates']):","for j in range(0 if method=='adaptive-cached' else cap['updates']):")
replace('r.eye(d, F(1, 10**8)))',"r.eye(d, 0 if method=='structural' else F(1, 10**8)))")
replace('reused_previous_factor=previous is not None and t<T-1,',"reused_previous_factor=previous is not None and t<T-1 and method!='structural',")
replace("noncommuting_fits=sum(v['initial_commutator_squared']>0 for v in records),", """noncommuting_fits=sum(v['initial_commutator_squared']>0 for v in records),
        training_target_inverse_builds=(sum(v['training_cap']['inverse_builds'] for v in records if v['training_cap'])
             if method=='adaptive-cached' else sum(v['hidden_updates'] for v in records) if method=='quadratic-refresh' else 0),
        training_target_inverse_applications=(sum(v['hidden_updates'] for v in records)
             if method in ('adaptive-cached','quadratic-refresh') else 0),
        fractional_bits_sum=(sum(v['training_cap']['stored_factor_bits_sum'] for v in records if v['training_cap'])
             if method=='adaptive-cached' else bits*sum(v['hidden_updates'] for v in records)),
        fractional_bits_max=(max((v['training_cap']['stored_factor_bits_max'] for v in records if v['training_cap']),default=0)
             if method=='adaptive-cached' else bits if method!='structural' else 0),
        stage_own_policy_evaluations=T, actor_solves=T, independent_subsolution_checks=T,
        simulation_transitions=0,
        count_scope='Training target inverse counts exclude Gaussian evaluation and actor solves. All are included in the complete service clock.',""")
replace('storage_bits=bits,',"storage_bits=('adaptive, at most 128' if method=='adaptive-cached' else bits if method!='structural' else 0),")
s=s[:s.index('\ndef execute():')]+'''
def execute():
    import resource
    here = Path(__file__).resolve().parent
    out = here.parent/'results/exact'
    if out.exists():
        raise FileExistsError('Do not overwrite an execution; use a clean working tree')
    out.mkdir(parents=True)
    start = time.perf_counter()
    rows=[]
    for method in ('linear-warm','quadratic-refresh','adaptive-cached','structural'):
        previous=None
        for changed in (False,True):
            began=time.perf_counter()
            try:
                result, previous = construct(changed, previous, method)
                data=json.dumps(encode(result),sort_keys=True,indent=2)+'\\n'
                name=method+'-'+result['regime']+'.json'
                with (out/name).open('w') as stream:
                    stream.write(data);stream.flush();os.fsync(stream.fileno())
                elapsed=time.perf_counter()-began
            except Exception as exc:
                failure=dict(method=method,changed=changed,error=repr(exc),
                    partial_service_seconds=time.perf_counter()-began,
                    scope='Failed attempt; not eight successful services')
                (out/'FAILURE.json').write_text(json.dumps(failure,indent=2)+'\\n')
                raise
            keys=('method','regime','certified','total_hidden_updates','training_target_inverse_builds',
                  'training_target_inverse_applications','fractional_bits_sum','fractional_bits_max',
                  'noncommuting_fits','actor_solves','stage_own_policy_evaluations',
                  'independent_subsolution_checks','simulation_transitions')
            row={k:result[k] for k in keys}
            row.update(policy_gap_upper=float(result['policy_gap_upper']),
                complete_service_seconds=elapsed,record=name,
                record_sha256=hashlib.sha256(data.encode()).hexdigest())
            rows.append(row)
    summary=dict(rows=rows,services=len(rows),certified=sum(v['certified'] for v in rows),
        requested_policy_tolerance='1/10000',source_freeze_commit=os.environ.get('NBO_SOURCE_SHA'),
        run_id=os.environ.get('GITHUB_RUN_ID'),platform=platform.platform(),python=sys.version,
        sum_complete_service_seconds=sum(v['complete_service_seconds'] for v in rows),
        loop_seconds_before_summary=time.perf_counter()-start,
        process_maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        memory_scope='Process high-water only, not a method-specific peak-memory comparison.',
        scope='Eight deterministic construction services, not population samples. Clocks include primitive allocation, own-policy evaluation, all training and gates, actor solves, exact independent policy verification, serialization and fsync. Startup and final ledger are unallocated common work. Existing clocks are not replaced.')
    frozen=json.loads((here.parent/'protocols/SOURCE_FREEZE.json').read_text())
    root=here.parents[2]
    for path,expected in frozen['files'].items():
        if hashlib.sha256((root/path).read_bytes()).hexdigest()!=expected:
            raise RuntimeError('Source changed during execution: '+path)
    summary['source_files_sha256']=frozen['files']
    (here.parent/'results/SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\\n')
    print(json.dumps(rows,indent=2))
if __name__=='__main__': execute()
'''
(r/'code/experiment.py').write_text(s)
s=(root/'revisions/2026-10-06-r35/code/test_inherited_policy.py').read_text()
s=s.replace('import quadratic_refresh as qr\nr = qr.r','import adaptive_refresh as ar\nqr = ar.qr\nr = ar.r')
(r/'code/test_inherited_policy.py').write_text(s)
protocol=dict(design='Eight deterministic exact construction services on unaltered R34 primitives',
    methods_in_order=['linear-warm','quadratic-refresh','adaptive-cached','structural'],
    regimes_in_order=['anchor','changed-valuation'],dimension=2,horizon=4,
    reference_primitives_commit='e05297f1688a19697e0e57fea66f181509548bbf',
    requested_full_policy_tolerance='1/10000',
    target='All adapted finite recursive cost policies; all real vector controls; initial squared norm at most two',
    future='Backward own-policy evaluation after future actors are finalized. Each neural method reuses only its own anchor factors.',
    precision='Linear and original quadratic: 40 bits. Adaptive: first integer satisfying the proved b-squared noise budget, up to 128 bits and 32 updates. Structural: exact rational control without factor fitting.',
    actor='Neural actors retain the inherited 1e-8 diagonal perturbation. Structural actor is exact. All use the same economic tolerance.',
    stopping='All full-action gates and independent matrix subsolution checks, never just fitting loss.',
    failure='Retain the first failed attempt and terminate; never label a partial execution as eight successes. No exclusions or retuning.',
    estimand='Per-object counts and descriptive complete clocks, not population inference or universal neural superiority.',
    work='Primitive allocation through durable detailed record; critic inverse construction and application counts are distinct. Intermediate rational bit growth is charged in clocks; no general bit-operation bound is claimed.',
    common_cost='Startup and final ledger unallocated. Process high-water memory not assigned to methods.',
    integrity='Commit all science sources and this protocol before executing the comparison. Earlier studies and clocks immutable. Unit tests are algebraic development checks.')
(r/'protocols').mkdir(exist_ok=True)
(r/'protocols/PROTOCOL.json').write_text(json.dumps(protocol,indent=2)+'\n')
files=list((r/'code').glob('*.py'))+[r/'protocols/PROTOCOL.json']
files += [root/'revisions/2026-10-06-r33/code/warm_start.py',root/'revisions/2026-10-06-r34/code/robust_policy.py',root/'revisions/2026-10-06-r35/code/quadratic_refresh.py']
manifest=dict(inherited_commit='b274a8326915960c04697d181238908f0f6a261f',
    scope='Materialized science sources to be committed before execution.',
    files={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
(r/'protocols/SOURCE_FREEZE.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Prepared actual experiment, inherited tests, protocol and source hashes; no services executed.')
