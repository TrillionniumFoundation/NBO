#!/usr/bin/env python3
"""Independent exact mathematics for the prospective R124B design.

Standard library only; no scientific-service imports, random draw, original
Bellman evaluation, optimizer, economic outcome or timing comparison.  The
polynomial fixture is an abstract information-class example and is not an
observed state of the investment model.
"""
from fractions import Fraction as F
from math import factorial
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import json


def encode(x):
    if isinstance(x, F):
        return str(x)
    if isinstance(x, dict):
        return {str(k): encode(v) for k, v in x.items()}
    if isinstance(x, (tuple, list)):
        return [encode(v) for v in x]
    return x


def verify():
    checks = []

    def require(name, predicate):
        if not predicate:
            raise AssertionError(name)
        checks.append(name)

    series_a = sum((F(25, 2)**j / factorial(j) for j in range(31)), F(0))
    series_b = sum((F(49, 4)**j / factorial(j) for j in range(31)), F(0))
    require('A exponential lower bound', series_a > 250000)
    require('B exponential lower bound', series_b > 200000)
    n, tau, radius_gain, radius_signed = 32, F(1, 256), F(7, 4096), F(7, 2048)
    require('B gain exponent', 2*n*radius_gain**2/tau**2 == F(49, 4))
    require('B signed exponent', 2*n*radius_signed**2/(2*tau)**2 == F(49, 4))
    require('B service census', 58*3 == 174)
    require('B gain census', 174+58 == 232)
    require('B signed census', 2*174 == 348)
    require('B gain allocation', F(464, 200000) < F(1, 100))
    require('B signed allocation', F(696, 200000) < F(3, 100))
    require('B binomial allocation', 232*F(1, 23200) == F(1, 100))
    failure_a = F(812, 250000) + F(1, 100)
    failure_b = F(1160, 200000) + F(1, 100)
    failure_ab = failure_a + failure_b
    require('B stronger failure bound', failure_b == F(79, 5000))
    require('Combined failure bound', failure_ab == F(3631, 125000))
    require('Combined coverage exceeds95percent', failure_ab < F(1, 20))

    # An exact information-class example with a genuine qualified bridge
    # improvement.  This is deliberately not a generated economic observation.
    A, mu, L = F(1, 4), F(2), F(4)
    s, t = F(1, 16), F(9, 128)
    d = t-s
    delta, omega = F(15, 2**24), F(1, 8192)
    ell_s, upper_s = -2*d, 2*d
    ell_t, upper_t = F(0), 4*d
    q = lambda x: (x-s)*(x-t)
    qp = lambda x: 2*x-s-t
    require('Original capacity and brackets', 0 <= s < t <= A)
    require('Exact paid levels', q(s) == q(t) == 0)
    require('Admissible curvature', mu == 2 <= L)
    require('Paid derivative intervals', ell_s <= qp(s) <= upper_s and ell_t <= qp(t) <= upper_t)
    at_origin = [(ell_s, upper_s), (ell_t-L*d, upper_t-mu*d)]
    require('Individual derivative proposals retain origin', all(lo <= 0 <= hi for lo, hi in at_origin))
    require('Fused derivative proposal retains origin', max(lo for lo, hi in at_origin) <= 0 <= min(hi for lo, hi in at_origin))
    u_star, b = F(1, 2), (s+t)/2
    require('Midpoint generated on30bitactiongrid', b*2**30 == int(b*2**30))
    require('Pair minimizer and midpoint coincide', s+u_star*d == b == F(17, 256))
    q_upper = -mu*u_star*(1-u_star)*d*d/2
    q_lower = ell_s*(b-s)+mu*(b-s)**2/2
    # Over [s,t] the fused upper derivative is 2d+2(x-s), and
    # the lower derivative is -2d+2(x-s).  These are direct extrema
    # of the two transported anchor cones, not production-code calls.
    fused_contrast = 2*d*(b-s)+(b-s)**2
    fused_absolute_upper = d*d/4
    require('Bridge polynomial attains upper', q(b) == q_upper == -d*d/4)
    require('Candidate lower bound', q_lower == -3*d*d/4 <= q(b))
    require('Fused contrast cannot accept candidate', fused_contrast == 5*d*d/4 > 0)
    require('Bridge improves fused absolute upper', q_upper < fused_absolute_upper)
    bridge_contrast = min(fused_contrast, q_upper-F(0))
    transported_upper = min(q_upper, F(0)+bridge_contrast)
    require('Bridge transport and contrast', transported_upper == bridge_contrast == q_upper)
    gain = -bridge_contrast-delta
    lower, upper = q_lower, transported_upper+delta
    optimum_lower = -d*d
    regret = upper-optimum_lower
    width = upper-lower
    require('Qualified incumbent width', delta <= omega)
    require('Qualified incumbent regret', delta-optimum_lower <= tau)
    require('Bridge strict safe gain', gain == F(241, 2**24) > F(1, 2**24))
    require('Bridge candidate width', width == F(527, 2**24) <= omega)
    require('Bridge candidate regret', regret == F(783, 2**24) <= tau)
    require('Original optimal lower bound', optimum_lower <= q(b))
    # A discontinuous allowable future error demonstrates that no hidden
    # differentiability is being used: eta(s)=0 and eta(b)=delta attain
    # the single-delta policy comparison exactly.
    actual_policy_difference = q(b)+delta-q(s)
    require('Single future allowance attained', actual_policy_difference == -gain)
    require('Cumulative gain bounded by commontau', gain <= tau)

    # Out-of-bracket rounding must not reuse the unrounded pair upper.
    bad_s, bad_t = F(1, 10), F(11, 100)
    ideal = (bad_s+bad_t)/2
    rounded = F((ideal/F(1, 16)).numerator // (ideal/F(1, 16)).denominator, 16)
    require('Rounding outside paid bracket example', rounded < bad_s < ideal < bad_t)
    bad_u = (rounded-bad_s)/(bad_t-bad_s)
    invalid_upper = -F(2)*bad_u*(1-bad_u)*(bad_t-bad_s)**2/2
    # q_bad(bad_s)=0 and q_bad(bad_t)=-1 are enclosed by upper0
    # at both endpoints, with second derivative2. Extrapolating both
    # endpoint uppers creates an invalid bound when u<0.
    q_bad = lambda x: -(x-bad_s)/(bad_t-bad_s)+(x-bad_s)*(x-bad_t)
    require('Extrapolated upper is invalid', q_bad(rounded) > invalid_upper)
    require('Actual bracket gate rejects invalid pair', not (bad_s <= rounded <= bad_t))

    return dict(
        status='passed', checks=len(checks), check_names=checks,
        scope='Prospective abstract rational mathematics only; zero new states or original-model evaluations; no production imports.',
        inference=dict(
            series_terms=31, series_a=series_a, series_b=series_b,
            n_B=n, service_cells=174, nonnegative_gain_cells=232,
            signed_cells=348, gain_radius=radius_gain,
            signed_radius=radius_signed, event_alpha=F(1, 23200),
            first_failure_upper=failure_a, second_failure_upper=failure_b,
            joint_failure_upper=failure_ab,
            interpretation='Strict upper bounds because positive exponential terms are omitted; B conditional on all A-informed preparation before its draw.'),
        bridge_fixture=dict(
            kind='Abstract polynomial information-class fixture, not an investment-model state',
            capacity=A, mu=mu, L=L, paid_actions=[s,t], paid_values=[F(0),F(0)],
            paid_derivative_intervals=[[ell_s,upper_s],[ell_t,upper_t]],
            incumbent=s, candidate=b, optimum_lower=optimum_lower,
            fused_contrast_upper=fused_contrast, fused_absolute_upper=fused_absolute_upper,
            bridge_contrast_upper=bridge_contrast, q_lower=q_lower,
            q_upper=q_upper, delta=delta, gain_lower=gain,
            policy_lower=lower, policy_upper=upper, regret_upper=regret,
            width=width, tau=tau, omega=omega),
        rounding_counterexample=dict(
            paid_actions=[bad_s,bad_t], ideal_action=ideal,
            realized_action=rounded, extrapolated_pair_bound=invalid_upper,
            true_polynomial_value=q_bad(rounded), pair_is_excluded=True))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    out = verify()
    out.update(
        checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        executed_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    with args.output.open('x') as f:
        json.dump(encode(out), f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps(dict(status=out['status'], checks=out['checks'], output=str(args.output))))


if __name__ == '__main__':
    main()
