"""Read-only post-execution reporting for the complete R119 phase-B campaign.

This reporting program is authored after phase A and before reading phase-B
outcomes. It imports only the standard library, changes no scientific record,
and never trains, evaluates an economic primitive, or reruns a timing clock.
The existing phase-A outputs are retained separately; their times are not pooled.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from itertools import combinations
import argparse
import csv
import hashlib
import json
import math
import statistics

ROOT = Path('/workspace/scratch/913249553838/NBO/revisions/2026-10-18-r119')
OUT = Path(__file__).resolve().parent
ARMS = ('online', 'quadratic', 'relu', 'hinge', 'spline', 'poly2', 'poly3', 'grid')
SERVICES = ('compiled', 'geometric', 'active-tail', 'masked-tail', 'budgeted-tail')


def load(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fr(value):
    return F(float(value))


def exact_mean(values):
    return sum(map(fr, values)) / len(values)


def mean(values):
    return float(exact_mean(values))


def mean_down(values):
    return math.nextafter(mean(values), -math.inf)


def mean_up(values):
    return math.nextafter(mean(values), math.inf)


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, sort_keys=True, indent=2,
                                     allow_nan=False) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--expected-source', required=True)
    args = parser.parse_args()
    raw = args.raw.resolve()
    checks = 0

    def check(condition, message):
        nonlocal checks
        checks += 1
        if not condition:
            raise ArithmeticError(message)

    campaign = load(raw / 'CAMPAIGN119B.json')
    catalogue = load(raw / 'CATALOGUE119.json')
    record_audit = load(raw / 'AUDIT119B.json')
    reference = load(raw / 'REFERENCE119.json')
    acquisition = load(raw / 'ACQUISITION119.json')
    source = campaign['source']
    check(source['executable_protocol_commit'] == args.expected_source,
          'Actual prospective phase-B source commit')
    check(record_audit['status'] == 'passed', 'Executed phase-B record audit')
    check(not (raw / 'FAILED.json').exists(), 'No campaign failure receipt')
    check(len(catalogue['entries']) == 80, 'All phase-B primary services')
    entries = catalogue['entries'][:]
    for repeat in range(7):
        process = load(raw / 'timing' / f'PROCESS-{repeat}.json')
        check(process['repeat'] == repeat and len(process['entries']) == 80,
              'All seven distinct complete timing catalogues retained')
        entries.extend(process['entries'])
        receipt = campaign['processes'][repeat]
        check(receipt['exit_code'] == 0, 'Actual timing subprocess exit status')
        check(sha(raw / 'timing' / f'PROCESS-{repeat}.log') == receipt['log_sha256'],
              'Timing subprocess log identity')

    records = {}
    budget_rows = []
    for entry in entries:
        path = raw / entry['path']
        check(sha(path) == entry['sha256'], 'Unchanged raw manifest bytes')
        data = load(path)
        records[entry['path']] = data
        histories = {r['row']: [] for r in data['rows']}
        payload_account = Counter()
        for attempt in data['attempts']:
            histories[attempt['row']].append(attempt)
        for row in data['rows']:
            lo, hi, optimum, loss, width = map(fr, (
                row['lower'], row['upper'], row['optimum_lower'], row['loss'], row['width']))
            check(lo <= hi and optimum <= hi, 'Returned original-policy certificate ordering')
            check(hi - optimum <= loss <= F(1, 256), 'Original regret allowance and gate')
            check(hi - lo <= width <= F(1, 8192), 'Original policy-width allowance and gate')
            cap = F(1, 8) + (fr(row['x0']) + fr(row['x1'])) / 16
            check(0 <= fr(row['action']) <= cap, 'Original action feasibility')
            check(fr(row['action_distance_upper']) ** 2 >= loss,
                  'Original strong-convexity action-distance allowance')
            check(row['returned_action_changed'] == (row['action'] != row['proposed']),
                  'Actual proposal-change label')
            if data['service'] in ('masked-tail', 'budgeted-tail'):
                history = histories[row['row']]
                attempts = [a for a in history if a['kind'] == 'budgeted-tail']
                check(bool(attempts), 'Retained positive-tail preliminary history')
                levels = [a['bins_per_tail'] for a in attempts]
                cut = fr(attempts[0]['cut'])
                high_cut = F(1, 32) - fr(data['alpha']) / 16
                tails = int(cut > F(-1, 32)) + int(cut < high_cut)
                outward = 2 + tails * sum(2 * m + 1 for m in levels)
                floating = 4 + 12 * int(F(-1, 32) < cut < high_cut)
                payload_account['r119b_tail_residual_point_values'] += 2
                payload_account['r119b_midpoint_terminal_rows'] += tails * sum(levels)
                payload_account['r119b_endpoint_terminal_rows'] += tails * sum(m + 1 for m in levels)
                payload_account['r119b_tail_proposal_point_values'] += floating
                check(tails in (1, 2), 'Every retained density has positive tail mass')
                schedule = [2, 4] if data['service'] == 'budgeted-tail' else [2, 4, 8, 16, 32, 64]
                check(levels == schedule[:len(levels)], 'Declared precision prefix')
                if data['service'] == 'budgeted-tail':
                    check(outward <= 30, 'All-row exact 30-payload outward budget')
                    if tails == 1:
                        check(outward <= 16, 'Boundary-row exact 16-payload outward budget')
                check(floating <= 16, 'All-row floating proposal budget')
                budget_rows.append(dict(file=entry['path'], service=data['service'],
                    row=row['row'], positive_tails=tails, levels=levels,
                    outward_values=outward, floating_values=floating,
                    fallback=any(a['kind'] == 'full-support-fallback' for a in history),
                    primary=entry['path'].startswith('catalogue/')))
        if payload_account:
            for key, expected in payload_account.items():
                check(data['counts'].get(key, 0) == expected,
                      'Every current-phase file matches its actual compiler query counter: ' + key)

    refs = {}
    service_contrasts = Counter()
    for item in reference['records']:
        i = item['index']
        for state in item['states']:
            check(state['optimum_lower'] <= state['optimum_upper'], 'Reference optimum bracket')
            check(len(state['policies']) == 40, 'Every phase-B service receives a reference')
            check(len(state['contrasts']) == 80, 'All ten within-arm service contrasts retained')
            for policy in state['policies']:
                refs[i, policy['policy'], state['row']] = policy
                check(fr(policy['regret_upper']) >=
                      fr(policy['upper']) - fr(state['optimum_lower']),
                      'Reference original regret upper allowance')
                check(fr(policy['action_distance_upper']) ** 2 >= fr(policy['regret_upper']),
                      'Reference original action-distance upper allowance')
            for contrast in state['contrasts']:
                key = contrast['control'] + '->' + contrast['treatment']
                for label in ('identical_policy', 'strictly_improved', 'strictly_worse'):
                    service_contrasts[key + '/' + label] += int(contrast[label])
                service_contrasts[key + '/total'] += 1
                if contrast['identical_policy']:
                    check(contrast['lower'] == contrast['upper'] == 0,
                          'Identical original policy has exactly zero economic contrast')

    frontier = []
    standalone = []
    for i, alpha in enumerate((0.5, 0.75)):
        for arm in ARMS:
            acquired = load(raw / 'models' / f'{i}-{arm}' / 'acquisition.json')
            check(sha(raw / 'models' / f'{i}-{arm}' / 'model.json') == acquired['model_sha256'],
                  'Current phase-B paid model bytes')
            components = {key: acquired.get(key, 0.0) for key in (
                'label_cost_if_standalone_seconds', 'fit_seconds', 'audit_seconds', 'serialization_seconds')}
            if arm == 'hinge':
                relu = load(raw / 'models' / f'{i}-relu' / 'acquisition.json')
                components.update(fit_seconds=relu['fit_seconds'], audit_seconds=relu['audit_seconds'],
                                  underlying_relu_serialization_seconds=relu['serialization_seconds'])
            acquisition_seconds = sum(components.values())
            fitting = acquired.get('fit', {})
            standalone.append(dict(index=i, alpha=alpha, arm=arm, components=components,
                seconds=acquisition_seconds, label_sites=acquired['label_sites'],
                payload_bytes=acquired['payload_bytes'], candidate_solves=fitting.get('candidate_solves'),
                fit_trials=len(fitting.get('trials', [])),
                audit_trials=len(acquired.get('audit', {}).get('trials', [])),
                inherited_full_acquisition_from='relu' if arm == 'hinge' else None))
            loading = catalogue['model_loading'][i]['per_arm'][arm]
            for service in SERVICES:
                data = records[f'catalogue/{i}-{arm}-{service}.json']
                rows = data['rows']
                clocks = [records[f'timing/{r}-{i}-{arm}-{service}.json']['seconds'] for r in range(7)]
                policies = [refs[i, arm + '/' + service, j] for j in range(144)]
                check(all(row['action'] == policy['action'] for row, policy in zip(rows, policies)),
                      'Actual returned policy reference identity')
                for row, policy in zip(rows, policies):
                    check(row['lower'] <= policy['upper'] and policy['lower'] <= row['upper'],
                          'Production and independently refined original-policy enclosures overlap')
                counts = data['counts']
                frontier.append(dict(index=i, alpha=alpha, arm=arm, service=service,
                    acquisition_seconds=acquisition_seconds, model_loading_seconds=loading,
                    payload_bytes=acquired['payload_bytes'],
                    primary144_service_seconds=data['seconds'],
                    primary144_proposal_seconds=data['proposal_seconds'],
                    component_sum_acquisition_loading_primary144_seconds=acquisition_seconds+loading+data['seconds'],
                    timing32_median_seconds=statistics.median(clocks),
                    timing32_min_seconds=min(clocks), timing32_max_seconds=max(clocks),
                    timing32_all_seconds=clocks,
                    primary_mean_original_cost_lower=mean_down([p['lower'] for p in policies]),
                    primary_mean_original_cost_upper=mean_up([p['upper'] for p in policies]),
                    primary_mean_regret_lower=max(0.0, mean_down([p['regret_lower'] for p in policies])),
                    primary_mean_regret_upper=mean_up([p['regret_upper'] for p in policies]),
                    primary_max_regret_upper=max(p['regret_upper'] for p in policies),
                    primary_mean_action_distance_upper=mean_up([p['action_distance_upper'] for p in policies]),
                    primary_max_action_distance_upper=max(p['action_distance_upper'] for p in policies),
                    first_attempt_rejections=sum(r['first_attempt_rejected'] for r in rows),
                    proposals_repaired=sum(r['proposal_repaired'] for r in rows),
                    returned_actions_changed=sum(r['returned_action_changed'] for r in rows),
                    exact_fallbacks=sum(r['exact_fallback'] for r in rows),
                    attempted_certificates=len(data['attempts']),
                    rejected_attempted_certificates=sum(not a['qualified'] for a in data['attempts']),
                    initial_schedule_exhausted=len({a['row'] for a in data['attempts']
                                                  if a['kind'] == 'full-support-fallback'}),
                    accepted_resolution_histogram=dict(Counter(r['bins'] for r in rows)),
                    certificate_max_width=max(r['width'] for r in rows),
                    certificate_max_loss=max(r['loss'] for r in rows),
                    original_risk_point_queries=counts.get('terminal_original_risk_queries', 0),
                    terminal_proposal_queries=counts.get('terminal_proposal_queries', 0),
                    compiled_terminal_rows=counts.get('compiled_terminal_rows', 0),
                    risk_sort_items=counts.get('risk_sort_items', 0), counts=counts))

    lookup = {(r['index'], r['arm'], r['service']): r for r in frontier}
    comparisons = []
    for i in range(2):
        for arm in ARMS:
            for control, treatment in combinations(SERVICES, 2):
                a, b = lookup[i, arm, control], lookup[i, arm, treatment]
                aa = records[f'catalogue/{i}-{arm}-{control}.json']['rows']
                bb = records[f'catalogue/{i}-{arm}-{treatment}.json']['rows']
                ratios = {label: b[field] / a[field] if a[field] else None for label, field in (
                    ('median_time_ratio', 'timing32_median_seconds'),
                    ('primary_time_ratio', 'primary144_service_seconds'),
                    ('full144_component_ratio', 'component_sum_acquisition_loading_primary144_seconds'),
                    ('risk_query_ratio', 'original_risk_point_queries'),
                    ('compiled_row_ratio', 'compiled_terminal_rows'),
                    ('sorting_item_ratio', 'risk_sort_items'))}
                comparisons.append(dict(index=i, alpha=a['alpha'], arm=arm, control=control,
                    treatment=treatment, identical_primary_policies=sum(x['action'] == y['action']
                                                                 for x, y in zip(aa, bb)),
                    faster_timing_repeats=sum(b['timing32_all_seconds'][r] < a['timing32_all_seconds'][r]
                                             for r in range(7)), **ratios))

    identities = []
    for i in range(2):
        for service in SERVICES:
            contexts = [('primary', f'catalogue/{i}', 144)] + [
                (f'timing-{r}', f'timing/{r}-{i}', 32) for r in range(7)]
            for scope, prefix, count in contexts:
                a, b = (records[f'{prefix}-{arm}-{service}.json'] for arm in ('relu', 'hinge'))
                identities.append(dict(index=i, service=service, scope=scope, rows=count,
                    exact_row_identity=a['rows'] == b['rows'],
                    exact_attempt_identity=a['attempts'] == b['attempts']))
    check(all(r['exact_row_identity'] and r['exact_attempt_identity'] for r in identities),
          'Complete current-phase ReLU/hinge record and attempted-certificate identity')

    economic = []
    for item in reference['records']:
        for control, treatment in combinations(ARMS, 2):
            lower, upper = [], []
            same = cheaper = costlier = 0
            for state in item['states']:
                policies = {p['policy']: p for p in state['policies']}
                a, b = (policies[arm + '/compiled'] for arm in (control, treatment))
                if a['action'] == b['action']:
                    lo = hi = F(0)
                    same += 1
                else:
                    lo, hi = fr(b['lower']) - fr(a['upper']), fr(b['upper']) - fr(a['lower'])
                lower.append(lo)
                upper.append(hi)
                cheaper += int(hi < 0)
                costlier += int(lo > 0)
            economic.append(dict(alpha=item['alpha'], control=control, treatment=treatment,
                mean_difference_lower=math.nextafter(float(sum(lower)/144), -math.inf),
                mean_difference_upper=math.nextafter(float(sum(upper)/144), math.inf),
                exact_mean_lower=str(sum(lower)/144), exact_mean_upper=str(sum(upper)/144),
                same=same, treatment_strictly_lower_cost=cheaper,
                treatment_strictly_higher_cost=costlier, not_resolved=144-same-cheaper-costlier))

    budgets = []
    for service in ('masked-tail', 'budgeted-tail'):
        for scope in ('primary', 'timing'):
            rows = [r for r in budget_rows if r['service'] == service and r['primary'] == (scope == 'primary')]
            boundary = [r for r in rows if r['positive_tails'] == 1]
            budgets.append(dict(service=service, scope=scope, rows=len(rows), boundary_rows=len(boundary),
                outward_values=sum(r['outward_values'] for r in rows),
                maximum_outward_values=max(r['outward_values'] for r in rows),
                maximum_boundary_outward_values=max([r['outward_values'] for r in boundary], default=None),
                floating_values=sum(r['floating_values'] for r in rows),
                maximum_floating_values=max(r['floating_values'] for r in rows),
                schedule_histogram=dict(Counter(','.join(map(str, r['levels'])) for r in rows)),
                complete_fallback_rows=sum(r['fallback'] for r in rows)))

    comparison_totals = []
    for control, treatment in combinations(SERVICES, 2):
        subset = [r for r in comparisons if r['control'] == control and r['treatment'] == treatment]
        comparison_totals.append(dict(control=control, treatment=treatment, cells=len(subset),
            median_faster=sum(r['median_time_ratio'] < 1 for r in subset),
            primary144_faster=sum(r['primary_time_ratio'] < 1 for r in subset),
            full144_component_faster=sum(r['full144_component_ratio'] < 1 for r in subset),
            faster_all_seven_repeats=sum(r['faster_timing_repeats'] == 7 for r in subset),
            slower_all_seven_repeats=sum(r['faster_timing_repeats'] == 0 for r in subset),
            identical_primary_policy_pairs=sum(r['identical_primary_policies'] for r in subset)))

    totals = dict(source_commit=args.expected_source, files=len(entries),
        primary_decisions=sum(len(v['rows']) for p, v in records.items() if p.startswith('catalogue/')),
        timing_decisions=sum(len(v['rows']) for p, v in records.items() if p.startswith('timing/')),
        exact_postexecution_checks=checks, campaign_inside_seconds=campaign['total_elapsed_seconds'],
        acquisition_shared_seconds=acquisition['seconds'],
        reference_seconds=sum(r['seconds'] for r in reference['records']),
        reference_unique_actions=sum(r['unique_policy_queries'] for r in reference['records']),
        primary_exact_fallbacks=sum(r['exact_fallbacks'] for r in frontier),
        primary_returned_action_repairs=sum(r['returned_actions_changed'] for r in frontier),
        maximum_primary_regret_upper=max(r['primary_max_regret_upper'] for r in frontier),
        primary_service_seconds={s: sum(r['primary144_service_seconds'] for r in frontier if r['service'] == s)
                                 for s in SERVICES},
        original_risk_point_queries={s: sum(r['original_risk_point_queries'] for r in frontier if r['service'] == s)
                                    for s in SERVICES},
        relu_hinge_identical_record_pairs=len(identities),
        relu_hinge_identical_decision_pairs=sum(r['rows'] for r in identities),
        service_contrasts=dict(service_contrasts), comparison_totals=comparison_totals,
        native_record_checks=record_audit['exact_record_checks'])
    check(totals['primary_decisions'] == 11520 and totals['timing_decisions'] == 17920,
          'Complete announced current-phase numerical population')
    totals['exact_postexecution_checks'] = checks
    result = dict(totals=totals, frontier=frontier, comparisons=comparisons,
        acquisition=standalone, representation_identity=identities,
        exact_preliminary_budgets=budgets,
        source_hashes={str(p.relative_to(ROOT)): sha(p) for p in (
            raw/'CAMPAIGN119B.json', raw/'AUDIT119B.json', raw/'REFERENCE119.json',
            raw/'CATALOGUE119.json', ROOT/'SOURCE_FREEZE119B.json')},
        interpretation='Complete phase-B post-execution reporting. This is prospectively frozen development on the previously seen state catalogue. Fresh phase-B acquisition and clocks are analyzed only against contemporaneous controls. All phase-A results remain separately reported. Mean bounds describe the deterministic original-economy catalogue, not population confidence intervals. Full acquisition/loading/service component sums use observed costs and are not retimings.')
    dump('R119B_NUMERICAL_REVIEW.json', result)
    dump('R119B_ECONOMIC_COMPARISONS.json', economic)
    dump('R119B_EXACT_PRELUDE_ROWS.json', budget_rows)
    flat = [{k: v for k, v in row.items() if not isinstance(v, (dict, list))} for row in frontier]
    with (OUT/'R119B_FRONTIER80.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(flat[0]))
        writer.writeheader()
        writer.writerows(flat)
    print(json.dumps(totals, sort_keys=True, indent=2))
    print(json.dumps(budgets, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
