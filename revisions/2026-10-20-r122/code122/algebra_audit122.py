"""Independent exact audit of serialized R122 support-to-action arithmetic.

Only the Python standard library is imported.  No economic primitive, fitted
actor, production interval compiler or service implementation is imported.
The audit establishes consequences of the recorded support premises; it does
not independently establish those premises or replace original-risk checks.
"""
from fractions import Fraction as F
import math

DELTA = F(15, 16 * 2**20)
TAU, WIDTH = F(1, 256), F(1, 8192)
FRACTIONS = tuple(F(1, 2**j) for j in range(6))


def smoothness(alpha):
    beta, mz = F(15, 16), F(181, 64)
    m = F(1413, 128) + beta * (F(127, 16) + F(19625, 20480) * alpha / (1 - alpha))
    c = F(4, 5) * m
    return 5 + beta * (F(5, 16) * m + c*c * alpha / (mz * (1 - alpha)))


def outward(q, upper):
    v = float(q)
    if (upper and F(v) < q) or (not upper and F(v) > q):
        v = math.nextafter(v, math.inf if upper else -math.inf)
    return v


def quadratic_minimum(w, p, mu, lo, hi):
    d = max(lo, min(hi, -p / mu))
    return w + p*d + mu*d*d/2


def audit(row):
    """Validate one saved primary record; return additive integer counters.

    Arithmetic/numerical failure records are accepted only as unchanged,
    zero-gain policies; their completed prefixes are still checked.  These
    counters count algebraic checks, never economic or population observations.
    """
    counts = dict(rows=1, assertions=0, supports=0, candidates=0,
                  candidate_certificates=0, qualified_candidates=0,
                  accepted_actions=0, retained_failure_rows=0)
    identity = tuple(row.get(k) for k in ('index', 'row', 'budget', 'arm', 'loss', 'service'))

    def require(ok, label):
        counts['assertions'] += 1
        if not ok:
            raise ArithmeticError('Independent R122 algebra: ' + label + ' ' + repr(identity))

    alpha = F(row['alpha'])
    require(alpha in (F(1, 2), F(3, 4)), 'declared risk')
    x = tuple(map(F, row['state']))
    require(len(x) == 2 and all(0 <= v <= 1 for v in x), 'original state domain')
    a = F(row['baseline_action'])
    capacity = F(1, 8) + sum(x) / 16
    require(0 <= a <= capacity, 'incumbent feasibility')
    require(F(row['baseline_upper']) >= F(row['baseline_lower']), 'incumbent interval order')
    require(0 <= F(row['baseline_upper']) - F(row['baseline_optimum_lower']) <= TAU,
            'completed incumbent regret cap')
    require(F(row['baseline_upper']) - F(row['baseline_lower']) <= WIDTH,
            'completed incumbent width cap')
    attempts = row['support_attempts']
    failure = row.get('enhancement_numerical_failure')
    if failure is not None:
        counts['retained_failure_rows'] += 1
        require(failure['all_partial_attempts'] == attempts, 'preserved failure prefix')
        require(failure['exception_type'] in ('ArithmeticError', 'FloatingPointError',
                'OverflowError', 'ZeroDivisionError', 'LinAlgError'), 'recoverable exception class')
        require(not row['accepted_improvement'] and F(row['certified_policy_gain_lower']) == 0,
                'numerical failure keeps zero-gain incumbent')
    require(row['service'] in ('control', 'recycled', 'adaptive'), 'service identity')
    require(row['extra_candidate_economic_queries'] == 0, 'declared same-payload query account')
    require(len(attempts) <= (0 if row['service'] == 'control' else 1 if row['service'] == 'recycled' else 3),
            'finite prospective ladder')
    eligible_last = []
    failed_qualification = 0
    paid_bins = []
    for number, record in enumerate(attempts):
        partial = failure is not None and number == len(attempts)-1
        c, g = record['certificate'], record['gradient']
        counts['supports'] += 1
        require(F(c['original_action']) == a and c['original_state'] == [row['state']],
                'support at unchanged original incumbent')
        require(c['support_curvature'] == 2 and c['full_support_continuous_risk'] is True,
                'declared original support premises')
        w, u = F(c['support_anchor_lower']), F(c['original_q_upper'])
        pl, pu = F(c['support_slope_lower']), F(c['support_slope_upper'])
        gap, L, mu = u-w, smoothness(alpha), F(2)
        require(gap >= 0 and pl <= pu and L >= mu, 'support and smoothness consistency')
        require(F(g['action']) == a and F(g['capacity']) == capacity and F(g['L']) == L
                and F(g['mu']) == mu and F(g['anchor_gap_upper']) == gap, 'original gradient input identity')
        require(g['global_gradient_cap'] == 7 and g['missing_feasible_side_uses_proved_global_cap'] is True,
                'boundary cap premise')
        radii = []
        for side, room in (('right_radius', capacity-a), ('left_radius', a)):
            r = g[side]
            if room == 0:
                require(r is None, 'missing side remains absent')
                radii.append(None)
            else:
                hs = {room} | {F(1, 2**j) for j in range(2, 41) if F(1, 2**j) <= room}
                h = min(hs, key=lambda t: (gap/t + (L-mu)*t/2, t))
                radius = gap/h + (L-mu)*h/2
                require(r is not None and F(r['h']) == h and F(r['radius']) == radius,
                        'exact finite feasible-radius minimum')
                radii.append(radius)
        gl = F(-7) if radii[0] is None else max(F(-7), pl-radii[0])
        gu = F(7) if radii[1] is None else min(F(7), pu+radii[1])
        require(F(g['lower']) == gl <= gu == F(g['upper']), 'derivative interval arithmetic')
        regret = max(F(0), *(-quadratic_minimum(F(0), z, mu, -a, capacity-a) for z in (gl, gu)))
        require(F(record['remaining_original_q_gain_upper']) == regret, 'constrained gradient regret bound')
        safe_capacity = F(record['proposal_capacity'])
        require(0 <= safe_capacity <= capacity and (safe_capacity*2**30).denominator == 1,
                'saved feasible 30-bit proposal capacity')
        if gu < 0:
            ideal = min(safe_capacity-a, -gu/L)
        elif gl > 0:
            ideal = max(-a, -gl/L)
        else:
            ideal = F(0)
        menu = record['candidate_menu']
        require(len(menu) <= 6 and (partial or len(menu) == 6), 'complete six-candidate menu or failed prefix')
        eligible = []
        for j, entry in enumerate(menu):
            counts['candidates'] += 1
            p = entry['proposal']
            fraction = FRACTIONS[j]
            raw = a + fraction*ideal
            b = F(max(0, min(int(raw*2**30), int(safe_capacity*2**30))), 2**30)
            d = b-a
            model = max(gl*d, gu*d) + L*d*d/2
            gain = -model-DELTA
            require(entry['fraction_index'] == j and F(p['fraction']) == fraction,
                    'prospective fraction and tie index')
            require(F(p['candidate']) == b and F(p['displacement']) == d and 0 <= b <= capacity,
                    'actual rounded feasible action')
            require(F(p['robust_original_q_gain_lower']) == -model
                    and F(p['original_policy_gain_lower']) == gain
                    and p['unchanged_action'] == (b == a), 'actual-action gain arithmetic')
            if b == a:
                require(entry.get('reason') == 'unchanged-action', 'zero-displacement refusal')
                continue
            if gain <= 0:
                require(entry.get('reason') == 'future-policy-allowance-not-separated', 'nonpositive-gain refusal')
                continue
            if 'candidate_certificate' not in entry:
                require(partial and j == len(menu)-1, 'only a failed last calculation may be incomplete')
                continue
            z = entry['candidate_certificate']
            counts['candidate_certificates'] += 1
            lower, upper = w + min(pl*d, pu*d) + d*d, u + model + DELTA
            optimum = max(min(quadratic_minimum(w, t, mu, -a, capacity-a) for t in (pl, pu)),
                          F(c['optimum_lower']), F(row['baseline_optimum_lower']))
            require(lower <= upper and optimum <= upper, 'derived candidate interval consistency')
            require(F(z['exact_policy_lower']) == lower and F(z['exact_policy_upper']) == upper
                    and F(z['exact_optimum_lower']) == optimum, 'candidate exact rational interval')
            lo, hi, bound = outward(lower, False), outward(upper, True), outward(optimum, False)
            loss = math.nextafter(hi-bound, math.inf)
            width = math.nextafter(hi-lo, math.inf)
            require(z['lower'] == lo and z['upper'] == hi and z['optimum_lower'] == bound
                    and z['loss'] == loss and z['width'] == width, 'outward binary endpoints and qualifications')
            qualified = loss <= float(TAU) and width <= float(WIDTH)
            require(z['qualified'] == qualified == entry['candidate_qualified']
                    and z['derived_without_candidate_economic_queries'] is True, 'separate gain/regret/width gate')
            if qualified:
                counts['qualified_candidates'] += 1
                eligible.append((gain, b, j, z))
            else:
                failed_qualification += 1
        eligible_last = eligible
        if number == 0:
            require(record['stage'] == 'recycled', 'reuse existing initial support')
            matches = [z for z in row['initial_support_certificates']
                       if z['original_action'] == row['baseline_action'] and z['alpha'] == row['alpha']]
            require(bool(matches) and c == matches[-1], 'last already-paid same-action support')
        else:
            require(record['stage'] == 'paid-precision-refinement' and record['bins'] in (256, 512),
                    'prespecified additional incumbent mesh')
            paid_bins.append(record['bins'])
        require(record['bins'] == c['bins'], 'saved mesh identity')
        if number < len(attempts)-1:
            require(not eligible and regret > DELTA, 'no refinement after a successful or dominated stop')
        if eligible:
            winner = min(eligible, key=lambda t: (-t[0], t[1], t[2]))
            require((partial and 'selected_fraction_index' not in record)
                    or record.get('selected_fraction_index') == winner[2], 'greatest gain and fixed tie rule')
    require(paid_bins == sorted(set(paid_bins)), 'fixed ordered nonrepeated paid meshes')
    require(row['refinement_count'] == len(paid_bins), 'paid incumbent-query count')
    started = row['paid_refinement_levels_started']
    require(started == sorted(set(started)) and all(b in (256, 512) for b in started)
            and row['paid_refinement_attempt_count'] == len(started), 'all paid refinement starts retained')
    require(paid_bins == started[:len(paid_bins)] and len(started)-len(paid_bins) <= (1 if failure else 0),
            'failed partial refinement remains in paid work account')
    allowed = ([] if not attempts or row['service'] != 'adaptive' else
               [b for b in (256, 512) if b > attempts[0]['bins']])
    require(started == allowed[:len(started)], 'skip duplicate or coarser already-paid meshes')
    if attempts and failure is None and not row['accepted_improvement'] and regret > DELTA:
        require(started == allowed, 'exhaust the fixed finer-only ladder before returning')
    require(row['candidate_algebra_attempts'] == counts['candidates']
            and row['candidate_bound_attempts'] == counts['candidate_certificates']
            and row['refused_candidate_bound_attempts'] == failed_qualification,
            'complete retained algebra work counts')
    require(row['candidate_rejected'] == (failed_qualification > 0), 'retained qualification refusals')
    if row['accepted_improvement']:
        require(failure is None and bool(eligible_last), 'accepted policy has completed eligible menu')
        gain, b, j, z = min(eligible_last, key=lambda t: (-t[0], t[1], t[2]))
        require(F(row['action']) == b != a and F(row['certified_policy_gain_lower']) == gain > 0,
                'returned accepted actual action and original gain')
        for name, source in (('complete_policy_lower', 'lower'), ('complete_policy_upper', 'upper'),
                             ('original_optimum_lower', 'optimum_lower'), ('certified_regret_upper', 'loss'),
                             ('lower', 'lower'), ('upper', 'upper'), ('optimum_lower', 'optimum_lower'),
                             ('loss', 'loss'), ('width', 'width')):
            require(row[name] == z[source], 'returned qualified candidate ' + name)
        counts['accepted_actions'] = 1
        require(row['improvement_stop'] == 'strict-original-policy-descent-certified', 'successful stopping identity')
    else:
        require(F(row['action']) == a and F(row['certified_policy_gain_lower']) == 0,
                'retention is exact same policy and zero gain')
        require(row['complete_policy_lower'] == row['baseline_lower']
                and row['complete_policy_upper'] == row['baseline_upper']
                and row['original_optimum_lower'] == row['baseline_optimum_lower'],
                'retained completed incumbent certificate')
        require(failure is not None or not eligible_last, 'qualified strict candidate cannot be silently discarded')
        if failure is not None:
            require(row['improvement_stop'] == 'recorded-enhancement-numerical-failure-retain-completed-incumbent',
                    'failed enhancement stopping identity')
        elif row['service'] == 'control':
            require(row['improvement_stop'] == 'control', 'control stopping identity')
        elif not attempts:
            require(row['improvement_stop'] == 'exact-fallback-has-no-recyclable-quadratic-support',
                    'missing support stopping identity')
        else:
            expected = ('original-q-potential-no-larger-than-future-allowance' if regret <= DELTA
                        else 'no-qualified-strict-improvement-in-frozen-six-step-menu')
            require(row['improvement_stop'] == expected, 'no-acceptance stopping identity')
    require(row['qualified'] is True and float(row['action']).hex() == row['action_hex'],
            'qualified actual binary action identity')
    return counts
