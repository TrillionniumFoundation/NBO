"""Deterministic verification gates for the subsequent paired-transfer theorem.

No policy is fitted or evaluated and no official checkpoint/payoff bank is
read.  High-precision function identities, arithmetic retention, fallback
scope, same-event invariance, and frozen-source identities are checked.
This filename intentionally does not enter the old dynamic test_* closure.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import itertools
import json
import math
from pathlib import Path
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import report_paired_transfer as paired


def dec(x):
    return Decimal.from_float(float(x))


def must_reject(function):
    try:
        function()
    except (ValueError, AssertionError):
        return
    raise AssertionError('a violated mathematical/identity contract was accepted')


def check_positive_series():
    # All dates are exact dyadics, including the original first and last cells.
    times = np.array([0., 2.**-20, 1./2048, 1./64, .125, .5, 1.])
    count = 0
    with localcontext() as ctx:
        ctx.prec = 100
        for beta in [.15, .31, .75]:
            for radius in [0., .1, .2]:
                got = paired.positive_D_integrals(times, beta, radius)
                b, r = dec(beta), dec(radius)
                for i, tf in enumerate(times):
                    t = dec(tf)
                    e = (b*t).exp()
                    exact = [r*(e-1)/b,
                        r*(e-1-b*t)/(b*b),
                        r*r/(b*b)*(((2*b*t).exp()-1)/(2*b)-2*(e-1)/b+t)]
                    for interval, value in zip(got, exact):
                        if value < 0 and abs(value) < Decimal('1e-85'):
                            value = Decimal(0)
                        if not dec(interval.lo[i]) <= value <= dec(interval.hi[i]):
                            raise AssertionError(f'positive-series enclosure failed at beta={beta}, r={radius}, t={tf}')
                        count += 1
        upper = paired.high(4/(3*paired.pc.sqrt_nonnegative(paired.I(3.))))
        if dec(upper) < 4/(3*Decimal(3).sqrt()):
            raise AssertionError('global tanh second derivative is not enclosed')
    must_reject(lambda: paired.positive_D_integrals(times, 1., .2))
    must_reject(lambda: paired.positive_D_integrals(np.array([-1., 0.]), .2, .2))
    return dict(name='positive_series_and_tanh_constant', high_precision_enclosures=count,
        precision_decimal_digits=100, first_original_time=1./2048, status='passed')


def check_interval_spectral():
    lo = np.array([[1., -2.], [3., .5]])
    hi = lo+np.array([[2.**-30, 2.**-29], [2.**-28, 2.**-27]])
    upper, proof = paired.spectral_interval(paired.I(lo, hi))
    # For a two-by-two interval box, convexity of the matrix norm reduces its
    # maximum to a corner.  Compute every corner norm independently in Decimal.
    with localcontext() as ctx:
        ctx.prec = 100
        maximum = Decimal(0)
        for flags in itertools.product([0, 1], repeat=4):
            a, b, c, d = [dec(hi.ravel()[i] if flags[i] else lo.ravel()[i]) for i in range(4)]
            tr = a*a+b*b+c*c+d*d
            determinant = (a*d-b*c)**2
            norm = ((tr+(tr*tr-4*determinant).sqrt())/2).sqrt()
            maximum = max(maximum, norm)
        if dec(upper) < maximum:
            raise AssertionError('interval-matrix norm omitted radius or an endpoint')
    return dict(name='interval_matrix_operator_norm', corners_verified=16,
        certified_upper=upper, independent_maximum=str(maximum),
        midpoint_and_radius_proof=proof, status='passed')


def check_original_event():
    # These are hand-written arithmetic fixtures, not stochastic observations.
    values = np.array([-.5, -.25, -.125, 0., .0625, .125, .25, .5])
    delta = paired.stats.ConfidenceBudget(.02, 238).event_alpha
    old = paired.stats.empirical_bernstein(values, bound=.25, bias=.02, clipping_tail=1e-7, event_alpha=delta)
    new = paired.stats.empirical_bernstein(values, bound=.25, bias=.005, clipping_tail=1e-7, event_alpha=delta)
    paired.assert_same_event(old, new)
    if not (new['lower'] > old['lower'] and new['upper'] < old['upper']):
        raise AssertionError('deterministic bias replacement did not narrow the same event')
    changed = dict(new, variance=new['variance']+1.)
    must_reject(lambda: paired.assert_same_event(old, changed))
    seeds = list(range(16))
    fixtures = {s: values+(s-8)/1024 for s in seeds}
    args = dict(declared_seeds=seeds, noise_keys={s: 'arithmetic-fixture-'+str(s) for s in seeds},
        bounds={s: .25 for s in seeds}, clipping_tails={s: 1e-7 for s in seeds},
        event_alpha=delta, confirmation_independent_of_selection=True)
    old_mean = paired.stats.finite_stream_mean(fixtures, biases={s: .02 for s in seeds}, **args)
    new_mean = paired.stats.finite_stream_mean(fixtures, biases={s: .005 for s in seeds}, **args)
    paired.assert_same_event(old_mean, new_mean)
    missing = dict(fixtures)
    del missing[15]
    must_reject(lambda: paired.stats.finite_stream_mean(missing, biases={s: .005 for s in seeds}, **args))
    return dict(name='unchanged_finite_expectation_events', individual_and_complete_16_stream_events=True,
        omitted_stream_rejected=True, changed_moment_rejected=True, additional_confidence_events=0, status='passed')


def check_fallback_and_saved_terms(protocol, account):
    av = paired.av
    _, saved = av.account(account['dimension'], 2048, .1, av.population(account['dimension']))
    confirmation = dict(dimension=account['dimension'], steps=2048, epsilon=.1,
        implementation='specified inward-guarded innovation-history controller',
        analytic_schedule=False, primitives_sha256=account['primitives_sha256'],
        constants=saved, clipping_threshold=saved['clipping_threshold'],
        bias=saved['bias_upper'], clipping_tail=saved['clipping_bias'],
        actor_bias_upper=saved['actor_bias_upper'], statistic_error_upper=saved['statistic_error_upper'])
    def normal(c):
        return dict(record=dict(fallback=False, final_confirmation=c),
            constants={k: paired.frozen.allowance(c, k) for k in ['clip', 'bias', 'tail', 'actor_bias', 'statistic_error']})
    left = normal(confirmation)
    fallback = dict(record=dict(fallback=True), constants={k: 0. for k in ['clip', 'bias', 'tail', 'actor_bias', 'statistic_error']})
    both = paired.refined_allowances(fallback, fallback, account)
    if any(both['refined'][k] for k in ['clip', 'bias', 'tail']) or both['refinement_applied']:
        raise AssertionError('two analytical references must remain exact zero')
    mixed = paired.refined_allowances(left, fallback, account)
    if mixed['refined'] != mixed['original'] or mixed['refined']['bias'] != left['constants']['bias']:
        raise AssertionError('mixed fallback lost its full original transfer')
    pair = paired.refined_allowances(left, left, account)
    candidate = pair['new_theorem_bias_candidate']
    if candidate < account['ideal_paired_transfer']+2*saved['statistic_error_upper']+paired.DIRECT_SUBTRACTION_CUSHION:
        raise AssertionError('paired total omitted an inherited statistic term')
    increased = copy.deepcopy(confirmation)
    increased['statistic_error_upper'] += 1e-5
    larger = paired.refined_allowances(left, normal(increased), account)
    if larger['new_theorem_bias_candidate'] <= candidate+0.999e-5:
        raise AssertionError('saved per-policy arithmetic increase was not charged')
    wrong = copy.deepcopy(confirmation)
    wrong['constants']['components'][0]['spectral']['matrix_sha256'] = '0'*64
    must_reject(lambda: paired.refined_allowances(left, normal(wrong), account))
    changed = copy.deepcopy(protocol)
    changed['design']['primitives']['common_sigma'] = .31
    must_reject(lambda: paired.calculate(changed, 10))
    return dict(name='fallback_scope_and_saved_arithmetic', both_fallback_exact=True,
        mixed_fallback_original_bias=True, changed_matrix_rejected=True,
        changed_primitives_rejected=True, increased_saved_arithmetic_retained=True,
        normal_pair_bias=candidate, subtraction_allowance=paired.DIRECT_SUBTRACTION_CUSHION,
        status='passed')


def check_stored_proposal_replay(protocol, accounts):
    original = paired.tc.spectral_bound
    def forbidden_new_svd(*args, **kwargs):
        raise AssertionError('stored-proposal replay called a new SVD proposal')
    try:
        paired.tc.spectral_bound = forbidden_new_svd
        for account in accounts:
            replay = paired.calculate(protocol, account['dimension'],
                coefficient_proposals=account['coefficient_proofs'])
            if replay != account:
                raise AssertionError('scientific account did not replay exactly with verified stored proposals')
    finally:
        paired.tc.spectral_bound = original
    bad = copy.deepcopy(accounts[0]['coefficient_proofs']['coupling'])
    bad['lambda_upper'] = .01
    bad['norm_upper'] = 1.
    must_reject(lambda: paired.verified_spectral(paired.av.old.coupling(accounts[0]['dimension']), bad))
    return dict(name='saved_spectral_proposal_replay', dimensions_verified=len(accounts),
        new_svd_proposals=0, complete_scientific_accounts_exact=True,
        invalid_spectral_majorant_rejected=True, endpoint_tolerance=0., status='passed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', type=Path, default=paired.R15/'PROTOCOL.json')
    parser.add_argument('--out', type=Path, help='Optional new JSON record; existing records are not overwritten')
    args = parser.parse_args()
    start = time.perf_counter()
    protocol = json.loads(args.protocol.read_text())
    rows = [check_positive_series(), check_interval_spectral(), check_original_event()]
    accounts = [paired.calculate(protocol, d) for d in protocol['design']['dimensions']]
    if not all(math.isfinite(r['proposed_total_upper']) and r['proposed_total_upper'] > 0 for r in accounts):
        raise AssertionError('nonfinite/nonpositive model allowance')
    rows.append(check_fallback_and_saved_terms(protocol, accounts[0]))
    rows.append(check_stored_proposal_replay(protocol, accounts))
    sources = paired.source_bindings(args.protocol)
    rows.append(dict(name='executed_source_and_protocol_identities', status='passed',
        files_verified=len(sources['frozen_imported_files']), numerical_source_commit=paired.FROZEN_NUMERICAL_SOURCE))
    result = dict(status='passed', generated_utc=datetime.now(timezone.utc).isoformat(),
        checks=rows, sources=sources, no_official_weights_or_payoff_arrays_read=True,
        no_simulation_or_fitting=True, additional_confidence_events=0,
        model_bound_summaries=[{k: r[k] for k in ['dimension', 'ideal_paired_transfer',
            'inherited_statistic_arithmetic', 'direct_subtraction_cushion',
            'proposed_total_upper', 'inherited_direct_transfer_upper']} for r in accounts],
        elapsed_seconds=time.perf_counter()-start)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        paired.write_json(args.out, result)
    print(json.dumps(dict(status=result['status'], checks=len(rows),
        elapsed_seconds=result['elapsed_seconds'], model_bounds=result['model_bound_summaries']), indent=2))


if __name__ == '__main__':
    main()
