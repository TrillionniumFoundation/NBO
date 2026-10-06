"""Materialize the exact source-frozen comparison; never run an unchecked payload."""
from pathlib import Path
import hashlib
import json
root=Path(__file__).resolve().parents[3]
r=root/'revisions/2026-10-06-r35'
s=(root/'revisions/2026-10-06-r34/code/exact_construction.py').read_text()
s=s.replace('import robust_policy as r','import quadratic_refresh as qr\nr = qr.r\nimport os\nimport platform\nimport sys')
s=s.replace('def construct(changed=False, previous=None):',"def construct(changed=False, previous=None, method='quadratic-refresh'):")
s=s.replace('e0 = r.warm.gate(factor, center, m=F(3, 2), upper=3, radius=F(1, 2))',"e0 = (qr.relative_gate(factor, center, m=F(3, 2)) if method=='quadratic-refresh'\n                  else r.warm.gate(factor, center, m=F(3, 2), upper=3, radius=F(1, 2)))")
old='''            nu = r.sqrt_up(F(len(factor)*d))/(2*(1 << bits))
            cap = r.warm.plan(m=F(3, 2), upper=3, radius=F(1, 2), alpha=F(1, 8),
                initial=e0, tolerance=tolerance, factor_error=nu, max_updates=10000)'''
new='''            absolute_nu = r.sqrt_up(F(len(factor)*d))/(2*(1 << bits))
            if method=='quadratic-refresh':
                nu = absolute_nu/r.sqrt_down(F(3, 2))
                relative_tolerance = qr.policy_relative_allowance(
                    gram_allowance=tolerance, dimension=d, target_upper=3)
                cap = qr.plan(initial=e0, tolerance=relative_tolerance, factor_error=nu)
            elif method=='linear-warm':
                nu = absolute_nu
                cap = r.warm.plan(m=F(3, 2), upper=3, radius=F(1, 2), alpha=F(1, 8),
                    initial=e0, tolerance=tolerance, factor_error=nu, max_updates=10000)
            else:
                raise ValueError('Unregistered construction method')'''
assert old in s;s=s.replace(old,new)
old='''                factor, actual_nu = r.warm.quantized_step(factor, center, F(1, 8), bits=bits)
                if actual_nu > nu:
                    raise ArithmeticError('Step error exceeded its planned allowance')
                envelope = cap['q']*envelope+cap['noise']
                error_squared = r.norm2(r.add(r.mm(r.tr(factor), factor), center, -1))
                if error_squared > envelope*envelope:
                    raise ArithmeticError('Warm contraction envelope violated')'''
new='''                if method=='quadratic-refresh':
                    factor, actual_nu = qr.quantized_step(factor, center, m=F(3, 2), bits=bits)
                    envelope = cap['c']*envelope*envelope+cap['noise']
                    gram_now = r.mm(r.tr(factor), factor)
                    r.psd(r.add(gram_now, r.scale(center, 1-envelope), -1))
                    r.psd(r.add(r.scale(center, 1+envelope), gram_now, -1))
                    absolute_envelope = r.sqrt_up(d)*3*envelope
                else:
                    factor, actual_nu = r.warm.quantized_step(factor, center, F(1, 8), bits=bits)
                    envelope = cap['q']*envelope+cap['noise']
                    absolute_envelope = envelope
                if actual_nu > nu:
                    raise ArithmeticError('Step error exceeded its planned allowance')
                error_squared = r.norm2(r.add(r.mm(r.tr(factor), factor), center, -1))
                if error_squared > absolute_envelope*absolute_envelope:
                    raise ArithmeticError('Warm contraction envelope violated')'''
assert old in s;s=s.replace(old,new)
s=s.replace('result = dict(regime=', 'result = dict(method=method, regime=')
s=s[:s.index('\ndef execute():')]+'''
def execute():
    here = Path(__file__).resolve().parent
    start = time.perf_counter()
    rows = []
    out = here.parent/'results/exact'
    out.mkdir(parents=True, exist_ok=True)
    # Frozen ordering: no clock-based selection, tolerance adjustment, or exclusions.
    for method in ('linear-warm', 'quadratic-refresh'):
        factors = None
        for changed in (False, True):
            began = time.perf_counter()
            result, factors = construct(changed, factors, method)
            data = json.dumps(encode(result), sort_keys=True, indent=2)+'\\n'
            name = method+'-'+result['regime']+'.json'
            with (out/name).open('w') as stream:
                stream.write(data); stream.flush(); os.fsync(stream.fileno())
            elapsed = time.perf_counter()-began
            rows.append(dict(method=method, regime=result['regime'], certified=result['certified'],
                total_hidden_updates=result['total_hidden_updates'],
                new_target_linear_solves=(result['total_hidden_updates'] if method=='quadratic-refresh' else 0),
                noncommuting_fits=result['noncommuting_fits'],
                policy_gap_upper=float(result['policy_gap_upper']),
                exact_policy_gap_upper=encode(result['policy_gap_upper']),
                complete_service_seconds=elapsed, record=name,
                record_sha256=hashlib.sha256(data.encode()).hexdigest()))
    source_paths = [here/'exact_comparison.py', here/'quadratic_refresh.py',
        qr._BACKEND, r._PATH, here.parent/'protocols/PROTOCOL.json']
    report = dict(rows=rows, requested_policy_tolerance='1/10000',
        execution_source_commit=os.environ.get('NBO_SOURCE_SHA'),
        source_sha256={str(p.relative_to(here.parents[2])):hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in source_paths},
        platform=platform.platform(), python=sys.version,
        sum_complete_service_seconds=sum(x['complete_service_seconds'] for x in rows),
        loop_seconds_before_summary=time.perf_counter()-start,
        scope='Four exact specified construction services: two methods times two regimes. '
              'Not independent samples, a population test, or evidence of superiority over structural control. '
              'Target solves, all factor updates and checks, actors, full-policy verification, '
              'serialization and durable record writes are included. Common interpreter/module '
              'startup and final summary/ledger overhead are not allocated to either method.')
    (here.parent/'results/EXACT_COMPARISON.json').write_text(json.dumps(report,indent=2)+'\\n')
    print(json.dumps([{k:v for k,v in row.items() if k!='exact_policy_gap_upper'} for row in rows],indent=2))

if __name__=='__main__':
    execute()
'''
s=s.replace('"""Two exact, specified construction instances, not a population experiment.', '"""R35 comparison on the unaltered R34 specified construction primitives.')
(r/'code/exact_comparison.py').write_text(s)
(r/'protocols').mkdir(exist_ok=True)
(r/'protocols/PROTOCOL.json').write_text('''{
  "design": "Exact constructive method comparison on inherited R34 primitives",
  "methods_in_execution_order": ["linear-warm", "quadratic-refresh"],
  "regimes_in_order": ["anchor", "changed-valuation"],
  "dimension": 2,
  "horizon": 4,
  "storage_bits": 40,
  "requested_full_policy_tolerance": "1/10000",
  "primitives": "Exactly those in R34 exact_construction.py at e05297f1688a19697e0e57fea66f181509548bbf",
  "comparison": "Each method constructs its own anchor and actually reuses its own anchor factors in the changed economy. Every stage evaluates its finalized future.",
  "stopping": "Apply the proved cap to the same R34 absolute Gram allowance; verify all relative/absolute errors, R34 local gates and the independent full-policy subsolution.",
  "failures": "No exclusions. An assertion or domain/gate/precision failure terminates the execution with a retained log; no partial result is reported as four successful services.",
  "account": "Evaluation, target solves, gates, all hidden updates, actor solves, exact policy checks, serialization and durable service output; startup and final summary are separately identified.",
  "estimand": "Deterministic counts and descriptive service clocks for these four objects, not population reliability or neural necessity.",
  "historical_evidence": "No inherited economic clocks or source-frozen protocol is overwritten."
}
''')
s=(root/'revisions/2026-10-06-r34/code/test_robust_policy.py').read_text()
s=s.replace('import robust_policy as r','import quadratic_refresh as qr\nr = qr.r')
s=s.replace('self.assertGreaterEqual(r.sqrt_up(F(4))*e, r.sqrt_up(r.norm2(E)))','''# Compare exact squared norms; separately test the outward enclosure.
        # sqrt_up(4)*e is exact 1/50, whereas sqrt_up(1/2500) is
        # generally strictly larger than 1/50 on the dyadic grid.
        self.assertEqual((r.sqrt_up(F(4))*e)**2, r.norm2(E))
        self.assertGreaterEqual(r.sqrt_up(r.norm2(E))**2, r.norm2(E))''')
(r/'code/test_inherited_policy.py').write_text(s)
manifest=json.loads((r/'protocols/SOURCE_FREEZE.json').read_text())
for path,expected in manifest['files'].items():
    actual=hashlib.sha256((root/path).read_bytes()).hexdigest()
    if actual!=expected: raise RuntimeError('Source freeze mismatch: '+path+' '+actual)
print('All five pre-execution source hashes match.')
