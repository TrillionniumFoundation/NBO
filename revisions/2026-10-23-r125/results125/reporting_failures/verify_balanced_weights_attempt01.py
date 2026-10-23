"""Read-only exact census-weight and direct-online-reference reconciliation."""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import gzip, hashlib, json, time

ROOT = Path(__file__).resolve().parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run():
    tick = time.perf_counter()
    p = ROOT / 'results125'
    with gzip.open(p / 'primary/records125.jsonl.gz', 'rt') as f:
        data = [json.loads(line) for line in f]
    key = lambda r: (str(F(r['alpha'])), tuple(r['state_hex']))
    groups = {}
    for mode in ('fused_control', 'warm_adaptive', 'cold_adaptive', 'warm_fixed512'):
        selected = [r for r in data if r['mode'] == mode]
        c = Counter(key(r) for r in selected)
        assert len(selected) == 232 and len(c) == 8 and set(c.values()) == {29}
        groups[mode] = dict(decisions=232, weight_per_risk_state='1/8',
                            multiplicity_per_risk_state=29)
    controls = [r for r in data if r['arm'] == 'online' and r['mode'] == 'fused_control']
    baseline = {key(r): r for r in controls}
    assert len(controls) == len(baseline) == 8
    paired = 0
    for r in data:
        if r['arm'] == 'online':
            b = baseline[key(r)]
            for field in ('action_hex', 'complete_policy_lower', 'complete_policy_upper',
                          'certified_regret_upper', 'future_controller'):
                assert r[field] == b[field], (r['mode'], key(r), field)
            assert r['qualified'] and r['target_qualified125']
            assert not r['new_queries125']
            paired += 1
    assert paired == 32
    grid = [r for r in data if r['mode'] == 'grid33']
    assert Counter(key(r) for r in grid) == Counter(key(r) for r in controls)
    for mode in groups:
        assert set(key(r) for r in data if r['mode'] == mode) == set(baseline)
    cohorts = [json.loads(line) for line in (p / 'primary/cohorts125.jsonl').read_text().splitlines()]
    parent = json.loads((p / 'launch-primary/PROCESS125.json').read_text())
    residual = F(parent['seconds']) - sum((F(c['seconds']) for c in cohorts), F(0))
    online_cohorts = [c for c in cohorts if c['arm'] == 'online' and c['mode'] == 'fused_control']
    complete = sum((F(c['seconds']) for c in online_cohorts), F(0)) + residual * len(online_cohorts) / len(cohorts)
    result = dict(status='executed', economic_evaluations=0, exact_weighting=True,
                  groups=groups, direct_online=dict(decisions=8, weight_per_risk_state='1/8',
                  all_mode_economic_record_identities_checked=32,
                  mean_original_j_lower=str(sum((F(r['complete_policy_lower']) for r in controls), F(0))/8),
                  mean_original_j_upper=str(sum((F(r['complete_policy_upper']) for r in controls), F(0))/8),
                  stronger_target=8, acquisition_charge=0,
                  complete_primary_parent_allocated_seconds=str(complete),
                  complete_primary_seconds_per_decision=str(complete/8),
                  subset_of_fused_control=True),
                  uniform_dp=dict(decisions=8, weight_per_risk_state='1/8'),
                  scientific_source_changed=False,
                  inputs={str(q.relative_to(ROOT)): sha(q) for q in (
                      p/'primary/records125.jsonl.gz', p/'primary/cohorts125.jsonl',
                      p/'launch-primary/PROCESS125.json')},
                  script_sha256=sha(Path(__file__)), seconds=time.perf_counter()-tick)
    target = p / 'BALANCED_WEIGHTING125.json'
    with target.open('x') as f:
        json.dump(result, f, indent=2, sort_keys=True); f.write('\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    run()
