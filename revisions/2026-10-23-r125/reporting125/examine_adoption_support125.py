"""Post-execution price-support and exact-policy-identity diagnostic; no economics."""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import gzip, hashlib, json, time

ROOT = Path(__file__).resolve().parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    tick = time.perf_counter()
    p = ROOT/'results125'
    adoption = [json.loads(x) for x in (p/'report/neural_adoption125.jsonl').read_text().splitlines()]
    summaries = [json.loads(x) for x in (p/'report/cohorts_summary125.jsonl').read_text().splitlines()]
    summary_table = {tuple(s['cohort']):s for s in summaries}
    with gzip.open(p/'primary/records125.jsonl.gz','rt') as f:
        data = [json.loads(x) for x in f]
    key = lambda r: tuple(r[k] for k in ('index','budget','arm','training_loss','mode'))
    first = {key(r):r for r in data if r['row']==0}
    assert len(first)==234 and len(adoption)==128
    future = 'unchanged terminal_controller94.terminal_policy with downward 40-bit state observations'
    identity_checks = []
    for risk in (0,1):
        rr = [r for r in first.values() if r['index']==risk and r['arm']!='uniform_dp']
        assert len(rr)==116
        actions = Counter(r['action_hex'] for r in rr)
        assert actions=={'0x1.3fffffe000000p-3':116}
        assert all(r['future_controller']==future and r['state_hex']==rr[0]['state_hex'] and r['alpha']==rr[0]['alpha'] for r in rr)
        identity_checks.append(dict(risk_index=risk,services=116,action_hex=rr[0]['action_hex'],
                                    alpha=rr[0]['alpha'],state_hex=rr[0]['state_hex'],future_controller=future))
    range_rows = []
    for N in (1,32,1000,1000000):
        aa=[a for a in adoption if a['N']==N]
        assert len(aa)==32
        ups=[]
        for a in aa:
            z=a['optimistic']
            assert not z['empty'] and F(z['price_lower'])==0 and z['price_upper'] is not None
            assert F(z['price_upper'])>0 and not z['finite_endpoints_strict']
            assert a['sufficient']['empty']
            ups.append(F(z['price_upper']))
        range_rows.append(dict(N=N,regions=32,positive_price_support=32,
                               all_closed_lower_endpoints='0',minimum_upper_endpoint=str(min(ups)),
                               maximum_upper_endpoint=str(max(ups))))
    witnesses=[]
    for a in adoption:
        own=summary_table[tuple(a['cohort'])];own_record=first[tuple(a['cohort'])];N=F(a['N'])
        own_lower=F(own['acquisition'])/N+F(own['timing_min'])
        matched=[]
        for other in summaries:
            if other['index']!=own['index'] or other['arm']=='relu':continue
            other_record=first[tuple(other['cohort'])]
            if other_record['action']!=own_record['action'] or other_record['future_controller']!=own_record['future_controller']:continue
            assert other_record['state_hex']==own_record['state_hex'] and other_record['alpha']==own_record['alpha']
            upper=F(other['acquisition'])/N+F(other['timing_max'])
            matched.append((upper,tuple(other['cohort']),other))
        assert len(matched)==100
        upper,other_key,other=min(matched,key=lambda z:(z[0],z[1]))
        gap=own_lower-upper
        assert gap>0
        witnesses.append(dict(cohort=a['cohort'],N=a['N'],original_optimistic=a['optimistic'],
            original_sufficient_empty=a['sufficient']['empty'],same_policy_competitors=len(matched),
            chosen_blocker=list(other_key),blocker_choice='minimum competitor upper complete cost, lexicographic cohort tie-break',
            own_lower_complete_cost=str(own_lower),blocker_upper_complete_cost=str(upper),
            strictly_positive_complete_cost_gap=str(gap),
            exact_original_J_difference='0',same_actual_action_hex=own_record['action_hex'],
            same_future_controller=future,strictly_positive_prices_excluded_under_recorded_cost_ranges=True,
            price_zero_is_equal_policy_cost_not_strict_neural_improvement=True))
    controller=ROOT/'code125/frozen_inputs/revisions/2026-10-22-r123/vendor/2026-10-20-r121/frozen108/code/terminal_controller94.py'
    result=dict(status='executed',economic_evaluations=0,services_retimed=0,
        original_classifications_unchanged=True,original_empty_sufficient=128,original_empty_optimistic=0,
        original_optimistic_regions_with_positive_prices=128,original_price_support_ranges=range_rows,
        policy_identity_checks=identity_checks,positive_price_identity_blocker_witnesses=witnesses,
        identity_blocked_positive_price_scenarios=len(witnesses),
        logical_argument='Identical initial state, risk, actual action and immutable terminal controller give identical pathwise original policies and J. For each witness, C_neural_lower>C_conventional_upper, so lambda>0 makes neural J+lambda*C strictly higher under the declared recorded timing range. At lambda=0 the identical J values tie.',
        scope='Post-execution exact diagnostic of the same first-state workload and recorded acquisition/timing scenarios. Not the original preregistered classification; not a new timing experiment, calibrated field price, confidence region or future runtime guarantee. Original interval-only optimistic regions are retained as loose outer sets.',
        fixed_controller_sha256=sha(controller),script_sha256=sha(Path(__file__)),
        inputs={str(q.relative_to(ROOT)):sha(q) for q in (p/'report/neural_adoption125.jsonl',p/'report/cohorts_summary125.jsonl',p/'primary/records125.jsonl.gz')},
        seconds=time.perf_counter()-tick)
    with (p/'ADOPTION_SUPPORT_DIAGNOSTIC125.json').open('x') as f:
        json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('positive_price_identity_blocker_witnesses','inputs')},sort_keys=True))


if __name__=='__main__':
    main()
