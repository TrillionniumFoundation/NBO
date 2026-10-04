#!/usr/bin/env python3
"""Independent post-execution arithmetic audit of the R16 robustness report.

This standard-library-only program checks protected summaries, all declared
streams, empirical-Bernstein formulas, pooled moments, deterministic transfer
accounts, decision flags, and final attainment fractions. It does not simulate,
fit, download raw arrays, or import the frozen estimator/inference implementation.
The source-bound collector's raw-array replay is a separate operation.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, localcontext
import argparse
import collections
import datetime
import hashlib
import json
import math

REVISION = Path('revisions/2026-10-04-r16')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rational(v):
    return F(float(v))


def dec(v):
    return Decimal.from_float(float(v))


def down(v):
    return math.nextafter(float(v), -math.inf)


def up(v):
    return math.nextafter(float(v), math.inf)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--protocol', type=Path)
    parser.add_argument('--evidence-commit')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    report = (args.report or root / REVISION / 'results/robustness/report/REPORT.json').resolve()
    protocol = (args.protocol or root / REVISION / 'protocols/robustness.json').resolve()
    out = args.out.resolve()
    if out in {report, protocol, Path(__file__).resolve()}:
        parser.error('audit output must differ from every input')
    r = json.loads(report.read_text())
    p = json.loads(protocol.read_text())
    checks = collections.Counter()
    failures = []

    def check(ok, label, where=''):
        checks[label] += 1
        if not ok:
            failures.append({'check': label, 'where': where})

    alpha = math.nextafter(p['inference']['alpha'] / 648, 0.)
    delta = p['economic_decisions']['material_payoff_margin']
    calibrations = {x['id']: x for x in p['calibrations']}
    seeds = p['seeds']
    dimensions = p['dimensions']
    methods = p['methods']
    endpoints = methods + [a + '__minus__' + b for a, b in p['confirmation']['direct_contrasts']]
    check(r['complete'] and r['protocol_sha256'] == sha(protocol), 'complete frozen-protocol identity')
    check(r['calibrations'] == p['calibrations'], 'exact frozen economic calibrations')
    check(len(seeds) == len(set(seeds)) == 8, 'all eight unique fixed streams')
    check(r['trials'] == 64 and r['fresh_group_processes'] == 256 and r['policy_outputs'] == 320,
          'complete economic-family execution counts')
    check(r['confidence_event_count_verified'] == 648 and r['confidence']['event_count'] == 648,
          'complete two-sided family cardinality')
    check(r['confidence']['alpha'] == .01 and r['confidence']['event_alpha'] == alpha and
          648 * rational(alpha) <= rational(.01), 'simultaneous probability allocation')
    check(r['economic_margin'] == delta == .0001, 'preserved economic margin')
    expected_seed = {(c, d, s, e) for c in calibrations for d in dimensions for s in seeds for e in endpoints}
    expected_pool = {(c, d, e) for c in calibrations for d in dimensions for e in endpoints}
    key = lambda x: (x['calibration_id'], x['dimension'], x['endpoint'])
    skey = lambda x: (x['calibration_id'], x['dimension'], x['stream_seed'], x['endpoint'])
    seed_rows = {skey(x): x for x in r['seed_endpoints']}
    pool_rows = {key(x): x for x in r['method_endpoints']}
    check(len(r['seed_endpoints']) == len(seed_rows) == 576 and set(seed_rows) == expected_seed,
          'all 576 distinct conditional endpoints')
    check(len(r['method_endpoints']) == len(pool_rows) == 72 and set(pool_rows) == expected_pool,
          'all 72 distinct finite-stream endpoints')

    def audit_eb(z, n, where):
        check(z['paths'] == n and z['event_alpha'] == alpha, 'path count and unchanged event alpha', where)
        check(all(math.isfinite(z[k]) for k in ['clipped_mean', 'variance', 'range_lower', 'range_upper',
              'bias', 'clipping_tail', 'lower', 'upper']) and z['lower'] <= z['upper'] and
              z['range_lower'] == -z['range_upper'] and z['variance'] >= 0 and z['bias'] >= 0 and
              z['clipping_tail'] >= 0, 'finite protected interval and allowances', where)
        with localcontext() as ctx:
            ctx.prec = 100
            vlo = dec(max(0., down(z['variance'])))
            vhi = dec(up(z['variance']))
            ell = (Decimal(4) / dec(alpha)).ln()
            nd = Decimal(n)
            bound = dec(z['range_upper'])
            ml = (2 * vlo * ell / nd).sqrt() + 14 * bound * ell / (3 * (nd - 1))
            mh = (2 * vhi * ell / nd).sqrt() + 14 * bound * ell / (3 * (nd - 1))
            margin = z['empirical_bernstein_margin']
            check(dec(margin) >= ml - Decimal('1e-90') and margin <= up(up(mh)),
                  'independent 100-digit empirical-Bernstein formula', where)
            zl, zh = dec(down(z['clipped_mean'])), dec(up(z['clipped_mean']))
            allowance = dec(z['bias']) + dec(z['clipping_tail'])
            check(down(zl - mh - allowance) <= z['lower'] <= up(zh - ml - allowance) and
                  down(zl + ml + allowance) <= z['upper'] <= up(zh + mh + allowance),
                  'protected endpoints within serialized exact-moment enclosure', where)

    def decision(z):
        lower, upper = z['lower'], z['upper']
        return dict(statistical_superiority=lower > 0,
            economically_material_superiority=lower > delta, noninferiority=lower > -delta,
            practical_equivalence=lower > -delta and upper < delta,
            economically_material_inferiority=upper < -delta,
            unresolved=not (lower > delta or upper < -delta or (lower > -delta and upper < delta)))

    unchanged = ['paths', 'clipped_mean', 'variance', 'range_lower', 'range_upper',
                 'empirical_bernstein_margin', 'clipping_tail', 'event_alpha', 'clipped_paths']
    for rows, n in [(r['seed_endpoints'], 8192), (r['method_endpoints'], 65536)]:
        for z in rows:
            where = '/'.join(map(str, skey(z) if 'stream_seed' in z else key(z)))
            audit_eb(z, n, where)
            if z['endpoint_type'] == 'direct_method_contrast':
                check(z['decision'] == decision(z), 'independent economic decision flags', where)
                old = z['original_transfer_endpoint']
                audit_eb(old, n, where + '/original_transfer')
                check(all(old[k] == z[k] for k in unchanged), 'unchanged random event under paired transfer', where)
                check(z['bias'] <= old['bias'] and z['lower'] >= old['lower'] and z['upper'] <= old['upper'],
                      'deterministic transfer sharpens same interval', where)
            else:
                check(z['endpoint_type'] == 'schedule_gain' and z['endpoint'] in methods,
                      'schedule endpoint interpretation', where)

    def moment_band(v):
        return rational(down(v)), rational(up(v))

    for z in r['method_endpoints']:
        c, d, e = key(z)
        where = f'{c}/d{d}/{e}'
        rows = [seed_rows[c, d, s, e] for s in seeds]
        check(z['declared_seeds'] == seeds and z['seed_count'] == 8 and z['paths_per_seed'] == 8192,
              'exact finite uniform stream law', where)
        noise = z['confirmation_noise_keys']
        check(set(noise) == set(map(str, seeds)) and len(set(noise.values())) == 8,
              'independent confirmation keys across streams', where)
        check(z['range_upper'] == max(x['range_upper'] for x in rows), 'pooled maximal range', where)
        for allowance in ['bias', 'clipping_tail']:
            exact = sum((rational(x[allowance]) for x in rows), F(0)) / 8
            check(rational(z[allowance]) >= exact, 'outward mean stratum ' + allowance, where)
        check(z['clipped_paths'] == sum(x['clipped_paths'] for x in rows), 'pooled clipping accounting', where)
        for s, x in zip(seeds, rows):
            check(z['per_seed_means'][str(s)] == x['mean'], 'preserved per-stream arithmetic mean', where + f'/{s}')
        means = [moment_band(x['clipped_mean']) for x in rows]
        ml = sum((a for a, b in means), F(0)) / 8
        mu = sum((b for a, b in means), F(0)) / 8
        zl, zu = moment_band(z['clipped_mean'])
        check(zl <= mu and zu >= ml, 'exact-rational pooled mean serialization', where)
        within_lower = sum((rational(max(0., down(x['variance']))) for x in rows), F(0)) * 8191
        within_upper = sum((rational(up(x['variance'])) for x in rows), F(0)) * 8191
        between_lower = F(0)
        between_upper = F(0)
        for i, (a, b) in enumerate(means):
            for c2, d2 in means[i + 1:]:
                lo, hi = a - d2, b - c2
                between_lower += F(0) if lo <= 0 <= hi else min(lo * lo, hi * hi)
                between_upper += max(lo * lo, hi * hi)
        vmin = (within_lower + 1024 * between_lower) / 65535
        vmax = (within_upper + 1024 * between_upper) / 65535
        vl, vu = moment_band(z['variance'])
        check(vl <= vmax and vu >= vmin, 'exact-rational within-between pooled variance', where)
        if e in methods:
            check(rational(z['full_adapted_class_regret_upper']) >=
                  rational(z['full_adapted_class_anchor_upper']) - rational(z['lower']),
                  'outward full-adapted-class regret subtraction', where)

    accounts = {}
    account_hashes = {}
    for c, calibration in calibrations.items():
        for d in dimensions:
            path = root / REVISION / f'protocols/robustness_constants/{c}_d{d}.json'
            a = json.loads(path.read_text())
            accounts[c, d] = a
            account_hashes[f'{c}_d{d}'] = sha(path)
            check(a['economic_primitives'] == calibration['primitives'] and
                  a['primitives_sha256'] == calibration['primitives_sha256'] and
                  a['epsilon'] == calibration['epsilon'] and a['protocol_sha256'] == sha(protocol),
                  'pre-confirmation paired economic identity', f'{c}/d{d}')
            check(a['steps'] == 2048 and a['economic_primitives']['T'] in [1., 2.] and
                  rational(a['beta']) * rational(a['economic_primitives']['T']) < 1,
                  'physical horizon and positive-series regime', f'{c}/d{d}')
    details = {skey(x): x for x in r['paired_allowance_details']}
    expected_details = {x for x in expected_seed if '__minus__' in x[-1]}
    check(len(details) == len(r['paired_allowance_details']) == 256 and set(details) == expected_details,
          'all 256 conditional direct-transfer accounts')
    for k, z in details.items():
        c, d, s, e = k
        where = '/'.join(map(str, k))
        a = accounts[c, d]
        current = seed_rows[k]
        old = current['original_transfer_endpoint']
        if z['eligibility'] != 'two_simulated_total_held_policies':
            check(z['refined'] == z['original'] and not z['refinement_applied'], 'fallback retains original theorem', where)
        else:
            terms = z['numerical_terms']
            exact = rational(a['ideal_paired_transfer']) + rational(terms['direct_subtraction_cushion'])
            for side in ['left', 'right']:
                t = terms[side]
                exact += sum((rational(t[name]) for name in ['production_upper', 'terminal_upper', 'statistic_error_upper']), F(0))
                check(t['statistic_error_upper'] >= a['inherited_single_statistic_arithmetic_upper'],
                      'both full statistic-error accounts retained', where + '/' + side)
            check(rational(z['new_theorem_bias_candidate']) >= exact, 'exact-rational paired allowance addition', where)
            check(z['refined']['bias'] == min(z['original']['bias'], z['new_theorem_bias_candidate']) and
                  z['refinement_applied'] == (z['new_theorem_bias_candidate'] < z['original']['bias']),
                  'deterministic minimum of valid transfer bounds', where)
        for endpoint, account in [(current, z['refined']), (old, z['original'])]:
            check(endpoint['bias'] == account['bias'] and endpoint['range_upper'] == account['clip'] and
                  endpoint['clipping_tail'] == account['tail'], 'reported endpoint binds saved transfer account', where)
        check(z['original']['clip'] == z['refined']['clip'] and z['original']['tail'] == z['refined']['tail'],
              'range and population-tail unchanged by theorem', where)

    identities = {(x['calibration_id'], x['dimension'], x['stream_seed'], x['method_id']): x for x in r['identity_records']}
    expected_ids = {(c, d, s, m) for c in calibrations for d in dimensions for s in seeds for m in methods}
    check(len(identities) == len(r['identity_records']) == 320 and set(identities) == expected_ids,
          'all 320 distinct policy identities')
    for c in calibrations:
        for d in dimensions:
            for s in seeds:
                ns = {identities[c, d, s, m]['noise_hash'] for m in methods}
                check(len(ns) == 1, 'common innovations within each five-method trial', f'{c}/d{d}/s{s}')
    attained = {}
    for z in r['final_certified_attainment']:
        c, d, m = z['calibration_id'], z['dimension'], z['method_id']
        rows = [seed_rows[c, d, s, m] for s in seeds]
        lower = sum(x['lower'] >= z['target'] for x in rows)
        upper = sum(x['upper'] >= z['target'] for x in rows)
        check(z['seed_count'] == 8 and z['definitely_attaining'] == lower and z['possibly_attaining'] == upper and
              z['probability_lower'] == lower / 8 and z['probability_upper'] == upper / 8,
              'finite-population final attainment fractions', f'{c}/d{d}/{m}/{z["target"]}')
        attained[c, d, m, z['target']] = lower
    expected_attainment = {(c, d, m, t) for c in calibrations for d in dimensions for m in methods for t in [.0005, .001]}
    check(len(r['final_certified_attainment']) == 80 and set(attained) == expected_attainment,
          'complete fixed final-target family without extra probability events')
    for w in r['work']:
        c, d, m = w['calibration_id'], w['dimension'], w['method_id']
        check(set(w['per_seed_complete_seconds']) == set(map(str, seeds)) and
              w['fallback_count'] == sum(identities[c, d, s, m]['fallback'] for s in seeds) and
              w['fixed_final_target_attained'] == attained[c, d, m, .0005],
              'no stream or failed-target attrition from work', f'{c}/d{d}/{m}')
    gains = [z for z in r['method_endpoints'] if z['endpoint_type'] == 'schedule_gain']
    direct = [z for z in r['method_endpoints'] if z['endpoint_type'] == 'direct_method_contrast']
    summary = []
    for z in gains:
        if z['endpoint'] == 'nbo':
            a = accounts[z['calibration_id'], z['dimension']]
            summary.append({k: z[k] for k in ['calibration_id', 'dimension', 'raw_mean', 'lower', 'upper',
                'full_adapted_class_regret_upper']} | {'fixed_paired_transfer_upper': a['proposed_total_upper']})
    categories = {name: sum(z['decision'][name] for z in direct) for name in decision(direct[0])}
    wins = [{k: z[k] for k in ['calibration_id', 'dimension', 'endpoint', 'lower', 'upper']} for z in direct
            if z['decision']['economically_material_superiority']]
    record = dict(schema='nbo-r16-final-robustness-independent-math-audit-v1', status='FAIL' if failures else 'PASS',
        auditor='r16_math', audited_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        audit_phase='post-execution independent protected-summary audit',
        report_file=str(REVISION / 'results/robustness/report/REPORT.json'), report_sha256=sha(report),
        protocol_sha256=sha(protocol), numerical_source_commit=r['numerical_source_commit'],
        evidence_commit=args.evidence_commit, audit_program_file=str(REVISION / 'code/audit_final_robustness_report.py'),
        audit_program_sha256=sha(__file__), exact_checks=dict(checks), failures=failures,
        probability_events=648, protected_records_checked_including_original_transfer=936,
        direct_transfer_accounts=256, distinct_policy_outputs=320,
        pooled_schedule_gains_positive=sum(z['lower'] > 0 for z in gains),
        pooled_schedule_gains_total=len(gains), pooled_direct_categories=categories,
        materially_superior_pooled_direct_comparisons=wins, nbo_economic_cells=summary,
        fallback_outputs=sum(z['fallback'] for z in identities.values()),
        preconfirmation_paired_account_sha256=account_hashes,
        full_adapted_class_regret_upper_range=[min(z['full_adapted_class_regret_upper'] for z in gains),
            max(z['full_adapted_class_regret_upper'] for z in gains)],
        scope='Exact rational allowance, pool-moment, regret and attainment checks; independent 100-digit EB formulas from protected published summaries. The frozen collector separately replays raw arrays. This audit does not claim a second raw-bank replay or re-prove the previously audited general-horizon transfer.',
        interpretation=dict(finite_eight_stream_population_only=True, no_cross_calibration_pooling=True,
            unresolved_is_not_equivalence=True, positive_gain_is_not_near_optimality=True,
            continuous_robustness_long_horizon=2., finite_menu_long_horizon=4.,
            joint_stress_is_not_single_primitive_causal_attribution=True,
            hjb_collocation_diagnostics_are_not_uniform_residual_certificates=True),
        no_frozen_scientific_source_changed=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'status': record['status'], 'checks': sum(checks.values()), 'failures': failures,
        'positive_schedule_gains': record['pooled_schedule_gains_positive'],
        'direct_categories': categories, 'audit_program_sha256': record['audit_program_sha256']}, indent=2))
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
