"""Prospectively fixed full-support algebra study on paid R126 source records.

All 58 first-state fused cohorts and the remaining 16 online state contexts
are included. No model fitting, new risk queries, or unobserved cohort selection
occurs here. The published primary-service record remains unchanged.
"""
import os
for _key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_key] = '1'
import argparse
import json
import time
import traceback

from common126 import *
from support_solver126 import solve_contrast, continuous_regret_envelope
from strong_cheap126 import cheap_upper as strong_cheap_upper


def run(primary, output):
    out, tick, info = start(output, 'same-paid-information-support-algebra')
    try:
        verified = verify_inputs()
        import service126 as svc
        svc.configure()
        before_counts = svc.old.econ.COUNTS.copy()
        primary = Path(primary)
        source = primary / 'records126.jsonl.gz'
        records = rows(source)
        if len(records) != 1584:
            raise ValueError('All 1584 original R126 primary decisions are required')
        selected = [r for r in records if r['mode'] == 'fused_control' and
                    (r['row'] == 0 or r['arm'] == 'online')]
        if len(selected) != 74:
            raise ValueError('The fixed census of all 74 support pools is required')
        write(out/'INPUT126.json', dict(primary_sha256=sha(source), selected_pool_count=74,
              selection='all58 first-state fused cohorts and all16 remaining online state contexts',
              source=verified, new_economic_queries=0, independent_policy_samples=0,
              cost_scope='Original paid primary-service cost plus measured new algebra; no fresh end-to-end prefix timing'))
        totals = dict(pools=0, no_support_pools=0, failed_pools=0, contrasts=0,
                      strictly_sharper_contrasts=0, candidate_actions=0,
                      strictly_sharper_regrets=0, strict_qualified_gains=0,
                      lp_calls=0, lp_failures=0, new_economic_queries=0)
        for number, record in enumerate(selected):
            ct = time.perf_counter()
            identity = {k: record[k] for k in ('index','budget','arm','training_loss','row','state126','alpha')}
            row = dict(pool_index=number, identity=identity,
                       original_primary_service_seconds=record['complete_service_seconds126'],
                       original_counts=record['counts126'], candidates=[], failure=None)
            totals['pools'] += 1
            supports = record['initial_support_certificates']
            try:
                if not supports:
                    totals['no_support_pools'] += 1
                    row['status'] = 'no-paid-support-ledger-no-solver-inference'
                else:
                    state = tuple(record['state126'])
                    case = svc.prior.make_case(supports, state, record['alpha'], record)
                    A, incumbent = case['A'], case['incumbent']
                    grid = sorted({F(0), A/4, A/2, 3*A/4, A, incumbent})
                    actions = sorted({incumbent, A})
                    common = svc.env.support_minimum(case)
                    endpoint = {x: svc.env.candidate(case,x,'fused',common) for x in grid}
                    for action in actions:
                        candidate_tick = time.perf_counter()
                        cheap = svc.terminal_certificate(case, action, common)
                        uppers = []
                        contrast_ids = []
                        incumbent_upper = F(0)
                        for origin in grid:
                            cheap_upper = strong_cheap_upper(case,origin,action)
                            solved = solve_contrast(case,origin,action,cheap_upper)
                            solved.update(pool_index=number, identity=identity,
                                          comparison='same paid record; capped fused derivative plus original endpoint levels and optimum floor')
                            solved_id = totals['contrasts']
                            append(out/'contrasts126.jsonl.gz',solved)
                            contrast_ids.append(solved_id)
                            totals['contrasts'] += 1
                            totals['strictly_sharper_contrasts'] += solved['certified_upper'] < cheap_upper
                            totals['lp_calls'] += solved['lp_calls']
                            totals['lp_failures'] += int(solved['failure'] is not None) + sum(h['status'] != 0 for h in solved['history'])
                            uppers.append(solved['certified_upper'])
                            if origin == incumbent:
                                incumbent_upper = solved['certified_upper']
                        grid_regret, cells = continuous_regret_envelope(grid, uppers, case['L'])
                        regret = min(cheap['direct_regret'], grid_regret+case['delta'])
                        gain = F(0) if action == incumbent else -incumbent_upper-case['delta']
                        acceptable = action != incumbent and gain > 0 and regret <= TAU and cheap['width'] <= OMEGA
                        rec = dict(action=action, grid=grid, contrast_record_ids=contrast_ids,
                                   cheap_original_regret=cheap['direct_regret'], grid_regret=grid_regret,
                                   cells=cells, retained_original_regret=regret,
                                   lower=cheap['lower'], upper=cheap['upper'], width=cheap['width'],
                                   certified_gain_lower=gain, strict_qualified_gain=acceptable,
                                   target_qualified=regret <= TARGET and cheap['width'] <= OMEGA,
                                   changed_primary_policy=False, seconds=time.perf_counter()-candidate_tick)
                        row['candidates'].append(rec)
                        totals['candidate_actions'] += 1
                        totals['strictly_sharper_regrets'] += regret < cheap['direct_regret']
                        totals['strict_qualified_gains'] += acceptable
                    row['status'] = 'bounded-certificate-calculation-completed'
            except BaseException as exc:
                totals['failed_pools'] += 1
                row.update(status='failed-pool-retained-no-inference', failure=dict(
                    type=type(exc).__name__, message=str(exc), traceback=traceback.format_exc()))
            row['new_algebra_seconds'] = time.perf_counter()-ct
            row['accounted_prefix_plus_algebra_seconds'] = row['original_primary_service_seconds']+row['new_algebra_seconds']
            append(out/'pools126.jsonl.gz', row)
            print(json.dumps(dict(pool=number+1, status=row['status'], seconds=row['new_algebra_seconds'])),flush=True)
        if svc.old.econ.COUNTS != before_counts:
            raise AssertionError('The declared algebra-only study made economic calls')
        write(out/'SUMMARY126.json', dict(totals, all_original_primary_results_retained=True,
              changed_primary_policies=0, finite_solver_optimality_certified=False,
              scope='All selected pools retained; independently replay exact certificates before claims',
              controlled_host_timing=False, independent_population_samples=0))
        finish(out,tick,source=verified,**totals)
    except BaseException:
        fail(out,tick)
        raise


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--primary',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    run(args.primary,args.output)
