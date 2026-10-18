"""Prospectively fixed R119 exact supporting study and independent finite audit.

The supporting study imports no production science: its algorithm sees only
paid exact point values, a Lipschitz bound and the original uniform law. Its
truth implementation sees formulas, reconstructs the quantile by breakpoints,
and integrates rationally. The original-economy audit calls production ONLY
as the implementation under examination; independent94 reconstructs original
terminal polynomials with Fraction arithmetic and imports no production code.
Neither finite catalogue is a proof of a continuum theorem or a population
experiment. All cases, exceptions, failed inequalities and actual queries stay
in the output. Execution requires a committed prospective source identity.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
RISKS = tuple(map(F, ('0', '1/2', '3/4', '7/8', '15/16', '31/32', '63/64', '255/256')))
BUDGETS = (8, 16, 32, 64)
R = F(1, 32)
BETA = F(15, 16)
TERMINAL_ALLOWANCE = F(1, 2**20)
ORIGINAL_STATES = (
    ('zero2', (F(0), F(0))),
    ('one2', (F(1), F(1))),
    ('asymmetric2', (F(1, 8), F(7, 8))),
    ('mixed4', (F(0), F(1, 2), F(1), F(1, 4))),
)
ORIGINAL_MESHES = (2, 8, 32)
REFERENCE_BINS = 64
TERMINAL_ROOT_STEPS = 32


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ff(value):
    """Exact value of a realized binary float, never a rounded decimal claim."""
    return F(float(value))


def serial(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def save(path, value):
    Path(path).write_text(json.dumps(serial(value), sort_keys=True, indent=2, allow_nan=False) + '\n')


class Ledger:
    def __init__(self):
        self.checks = 0
        self.failures = []

    def check(self, condition, case, statement):
        self.checks += 1
        if not bool(condition):
            self.failures.append(dict(case=case, statement=statement))

    def exception(self, case):
        self.failures.append(dict(case=case, exception=traceback.format_exc()))


@dataclass(frozen=True)
class PLQ:
    name: str
    quadratic: F
    linear: F
    constant: F
    hinges: tuple
    lipschitz: F

    def value(self, z):
        return self.quadratic*z*z + self.linear*z + self.constant + sum(
            weight*max(F(0), z-knot) for knot, weight in self.hinges)

    def integral(self, left, right):
        return (self.quadratic*(right**3-left**3)/3
                + self.linear*(right**2-left**2)/2 + self.constant*(right-left)
                + sum(weight*(max(F(0), right-knot)**2-max(F(0), left-knot)**2)/2
                      for knot, weight in self.hinges))

    def description(self):
        return dict(name=self.name, quadratic=self.quadratic, linear=self.linear,
                    constant=self.constant, hinges=self.hinges, lipschitz=self.lipschitz)


def catalogue():
    """Exactly ten fixed functions, identical at every risk level and budget."""
    return (
        PLQ('constant', F(0), F(0), F(3, 7), (), F(1)),
        PLQ('increasing_linear', F(0), F(1), F(1), (), F(1)),
        PLQ('decreasing_linear', F(0), F(-1), F(1), (), F(1)),
        PLQ('centered_quadratic', F(1), F(0), F(0), (), F(2)),
        PLQ('shifted_quadratic', F(1), F(-1, 2), F(1, 16), (), F(5, 2)),
        PLQ('one_hinge', F(0), F(0), F(0), ((F(1, 3), F(1)),), F(1)),
        PLQ('shifted_absolute', F(0), F(-1), F(-1, 5), ((F(-1, 5), F(2)),), F(1)),
        PLQ('flat_bottom', F(0), F(-1), F(-1, 4),
            ((F(-1, 4), F(1)), (F(1, 3), F(1))), F(1)),
        PLQ('curved_two_hinges', F(1, 4), F(-1, 3), F(1, 7),
            ((F(-1, 2), F(3, 5)), (F(1, 4), F(7, 6))), F(29, 15)),
        PLQ('curved_three_hinges', F(1, 8), F(-3, 4), F(2, 5),
            ((F(-3, 4), F(1, 4)), (F(-1, 8), F(1)), (F(5, 8), F(1, 2))), F(5, 4)),
    )


class PointOracle:
    """Own cache per method/cell; all requests and unique values are charged."""
    def __init__(self, evaluate):
        self._evaluate = evaluate
        self.cache = {}
        self.requests = 0

    def __call__(self, z):
        z = F(z)
        if not -1 <= z <= 1:
            raise ValueError('A point query left the original support')
        self.requests += 1
        if z not in self.cache:
            self.cache[z] = self._evaluate(z)
        return self.cache[z]

    def transcript(self):
        return [dict(point=z, value=v) for z, v in self.cache.items()]


def exact_truth(formula, alpha):
    """Formula-only independent integration, never sign-bisection queries.

For a common quadratic coefficient plus linear hinges, f(u+L)-f(u)
is affine between the union of hinge knots and their shifts by -L.
Evaluate every breakpoint, retain every exact stationary point and both
endpoints, and minimize the exact central integral over this finite set.
"""
    if alpha == 0:
        return dict(cut=None, value=formula.integral(F(-1), F(1))/2,
                    candidates=[], central_length=F(0), tail_length=F(2))
    length = 2*alpha
    left, right = F(-1), F(1)-length
    points = {left, right}
    for knot, _ in formula.hinges:
        for point in (knot, knot-length):
            if left < point < right:
                points.add(point)
    points = sorted(points)
    candidates = set(points)
    for a, b in zip(points, points[1:]):
        da, db = formula.value(a+length)-formula.value(a), formula.value(b+length)-formula.value(b)
        if da == 0:
            candidates.add(a)
        if db == 0:
            candidates.add(b)
        if da < 0 < db:
            candidates.add(a-da*(b-a)/(db-da))
    cut = min(candidates, key=lambda u: (formula.integral(u, u+length), u))
    value = (formula.integral(F(-1), cut)+formula.integral(cut+length, F(1)))/(2*(1-alpha))
    return dict(cut=cut, value=value, candidates=sorted(candidates),
                central_length=length, tail_length=2*(1-alpha))


def active_point_interval(oracle, lipschitz, alpha, n):
    """The theorem's exact-point algorithm, not the original-economy service."""
    m = (n-1).bit_length()
    tail = 2*(1-alpha)
    reason, performed = 'mean', 0
    defect = F(0)
    if alpha == 0:
        cut, components = None, [(F(-1), F(1))]
    else:
        length = 2*alpha
        left, right = F(-1), F(1)-length
        dl, dr = oracle(left+length)-oracle(left), oracle(right+length)-oracle(right)
        if dl >= 0:
            cut, reason = left, 'left_endpoint'
        elif dr <= 0:
            cut, reason = right, 'right_endpoint'
        else:
            reason = 'bracket_midpoint'
            for _ in range(m):
                midpoint = (left+right)/2
                difference = oracle(midpoint+length)-oracle(midpoint)
                performed += 1
                if difference == 0:
                    cut, reason = midpoint, 'exact_zero'
                    break
                if difference < 0:
                    left = midpoint
                else:
                    right = midpoint
            if reason == 'bracket_midpoint':
                cut = (left+right)/2
                defect = lipschitz*(1-alpha)/(2*4**m)
        components = [(F(-1), cut), (cut+length, F(1))]
    low, high, cells = F(0), F(0), []
    for left, right in components:
        if left == right:
            continue
        requested = n*(right-left)/tail
        count = (requested.numerator+requested.denominator-1)//requested.denominator
        for j in range(count):
            l, r = left+(right-left)*j/count, left+(right-left)*(j+1)/count
            z, weight = (l+r)/2, (r-l)/tail
            low += weight*oracle(z)
            high += weight*(oracle(l)+oracle(r))/2
            cells.append((l, r))
    return dict(cut=cut, lower=low, upper=high+defect, tail_lower=low, tail_upper=high,
                localization_allowance=defect, reason=reason, bisections=performed,
                requested_bisections=m, cells=cells, cell_count=len(cells),
                width=high+defect-low, bound=lipschitz*(1-alpha)*(F(1, n*n)+F(1, 2*4**m)),
                unique_queries=len(oracle.cache), query_requests=oracle.requests,
                query_bound=2*n+2*m+8, transcript=oracle.transcript())


def finite_avar(values, alpha):
    """Independent exact equal-mass upper-tail integral, including a split atom."""
    remaining = len(values)*(1-alpha)
    denominator, total = remaining, F(0)
    for value in sorted(values, reverse=True):
        mass = min(F(1), remaining)
        total += mass*value
        remaining -= mass
        if remaining == 0:
            break
    if remaining != 0 or denominator <= 0:
        raise ValueError('Impossible AVaR mass')
    return total/denominator


def whole_point_interval(oracle, alpha, query_cap):
    """Classical whole-support convex-order rule under the same query cap."""
    bins = (query_cap-1)//2
    edges = [oracle(F(-1)+F(2*j, bins)) for j in range(bins+1)]
    mid = [oracle(F(-1)+F(2*j+1, bins)) for j in range(bins)]
    endpoint_mixture = [v for j in range(bins) for v in (edges[j], edges[j+1])]
    low, high = finite_avar(mid, alpha), finite_avar(endpoint_mixture, alpha)
    return dict(bins=bins, lower=low, upper=high, width=high-low,
                unique_queries=len(oracle.cache), query_requests=oracle.requests,
                query_bound=query_cap, transcript=oracle.transcript())


def supporting(output):
    ledger, rows = Ledger(), []
    for formula in catalogue():
        ledger.check(formula.quadratic >= 0 and all(w >= 0 for _, w in formula.hinges), formula.name, 'Convex fixed formula')
        minimum_slope = -2*formula.quadratic+formula.linear
        maximum_slope = 2*formula.quadratic+formula.linear+sum(w for _, w in formula.hinges)
        ledger.check(max(abs(minimum_slope), abs(maximum_slope)) <= formula.lipschitz, formula.name, 'Declared global Lipschitz constant')
        for alpha in RISKS:
            truth = exact_truth(formula, alpha)
            for n in BUDGETS:
                case = f'{formula.name}:alpha={alpha}:n={n}'
                row = dict(case=case, formula=formula.description(), alpha=alpha, n=n, truth=truth)
                try:
                    active = active_point_interval(PointOracle(formula.value), formula.lipschitz, alpha, n)
                    conventional = whole_point_interval(PointOracle(formula.value), alpha, active['query_bound'])
                    row.update(active=active, whole_support=conventional)
                    value = truth['value']
                    ledger.check(active['lower'] <= value <= active['upper'], case, 'Exact original-law AVaR lies in active-tail interval')
                    ledger.check(conventional['lower'] <= value <= conventional['upper'], case, 'Exact original-law AVaR lies in whole-support interval')
                    ledger.check(F(0) <= active['width'] <= active['bound'], case, 'Tail-uniform theorem width bound')
                    ledger.check(active['unique_queries'] <= active['query_bound'], case, 'Paid localization and quadrature obey query cap')
                    ledger.check(conventional['unique_queries'] <= active['query_bound'], case, 'Conventional method obeys identical query cap')
                    ledger.check(active['cell_count'] <= n+1, case, 'At most n+1 positive-length cells')
                    ledger.check(all(r-l <= 2*(1-alpha)/n for l, r in active['cells']), case, 'Declared maximum cell length')
                    selected = value if alpha == 0 else (formula.integral(F(-1), active['cut'])+formula.integral(active['cut']+2*alpha, F(1)))/(2*(1-alpha))
                    ledger.check(active['tail_lower'] <= selected <= active['tail_upper'], case, 'Independent exact selected-tail integral')
                    ledger.check(0 <= value-selected <= active['localization_allowance'], case, 'Independent quantile confirms localization allowance')
                    row.update(selected_tail_exact=selected, localization_error=value-selected,
                               active_lower_error=value-active['lower'], active_upper_error=active['upper']-value,
                               whole_lower_error=value-conventional['lower'], whole_upper_error=conventional['upper']-value,
                               width_winner='active' if active['width'] < conventional['width'] else 'whole' if conventional['width'] < active['width'] else 'tie',
                               minimax_lower_bound_at_cap=formula.lipschitz*(1-alpha)/(6*(active['query_bound']+1)**2))
                except Exception:
                    ledger.exception(case)
                    row['exception'] = traceback.format_exc()
                rows.append(row)
            print(f'supporting {formula.name} alpha={alpha}: retained {len(rows)} cells', flush=True)
    ledger.check(len(rows) == 320, 'catalogue', 'All prospectively fixed supporting cells retained')
    result = dict(status='failed' if ledger.failures else 'passed', checks=ledger.checks,
                  failures=ledger.failures, cells=len(rows), rows=rows,
                  scope='Exact deterministic point-information supporting class on [-1,1]; not original investment outcomes, neural separation, wall-clock superiority or population inference.',
                  budget_convention='Same known convex/Lipschitz class, exact point oracle and query cap; independent per-arm caches; actual paid requests and unique queries retained. Formula access belongs only to the separate truth audit.',
                  lower_bound_scope='The minimax lower bound is worst case over consistent functions, not a pointwise lower bound for each displayed function.')
    save(output/'SUPPORTING_TAIL119.json', result)
    return result


def exact_constrained_gain(slope, curvature, anchor, left, right):
    displacement = max(left-anchor, min(right-anchor, -slope/curvature))
    return -slope*displacement-curvature*displacement*displacement/2


def load_science():
    sys.path.insert(0, str(ROOT/'code119'))
    import active_tail119 as production
    import numpy as np
    spec = importlib.util.spec_from_file_location('r119_exact_primitives', ROOT/'frozen108/code/independent94.py')
    exact = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exact)
    return production, np, exact


def gain_audit(production, np, ledger):
    rows = []
    intervals = ((F(-1), F(1)), (F(0), F(1)), (F(-1, 32), F(0)), (F(-1, 32), F(-1, 64)))
    eps = F(1, 2**40)
    relative_slopes = ((F(-2), F(-2)), (F(-1), F(-1)), (-1-eps, -1+eps),
                       (F(-1, 4), F(1, 4)), (F(0), F(0)), (-eps, eps),
                       (1-eps, 1+eps), (F(1), F(1)), (F(2), F(2)),
                       (F(-2), F(2)), (F(-3, 4), F(-1, 2)))
    for left, right in intervals:
        for position in (F(0), F(1, 4), F(1, 2), F(3, 4), F(1)):
            anchor = left+(right-left)*position
            for curvature in (F(1, 16), F(1), F(181, 64), F(8)):
                for pair in relative_slopes:
                    case = f'gain:{len(rows)}'
                    low, high = (v*curvature*(right-left) for v in pair)
                    outward = float(production.constrained_gain(production.I(np.array([float(low)]), np.array([float(high)])), float(curvature), np.array([float(anchor)]), float(left), float(right))[0])
                    exact = max(exact_constrained_gain(v, curvature, anchor, left, right) for v in (low, high))
                    ledger.check(np.isfinite(outward) and ff(outward) >= exact >= 0, case, 'Outward gain covers exact endpoint-slope minimization')
                    for j in range(9):
                        middle = low+(high-low)*F(j, 8)
                        ledger.check(exact_constrained_gain(middle, curvature, anchor, left, right) <= exact, case, 'Slope uncertainty covered including interior slopes')
                    rows.append(dict(left=left, right=right, anchor=anchor, curvature=curvature,
                                     slope_interval=(low, high), exact_gain=exact, production_upper=outward,
                                     excess=ff(outward)-exact))
    ledger.check(len(rows) == 880, 'gain', 'All fixed constrained-minimum cases retained')
    return rows


def density_audit(production, np, ledger):
    rows = []
    for alpha in (F(1, 2), F(3, 4)):
        length, tail = 2*R*alpha, 2*R*(1-alpha)
        cuts = sorted({-R+tail*F(j, 16) for j in range(17)} | {-R+F(1, 2**32), R-length-F(1, 2**32)})
        for m in (2, 4, 8, 16, 32, 64):
            mids, edges, weights = production.tail_mesh(np.array(list(map(float, cuts))), float(alpha), m)
            for i, cut in enumerate(cuts):
                case = f'density:alpha={alpha}:m={m}:cut={cut}'
                el = [-R+(cut+R)*F(j, m) for j in range(m+1)]
                er = [cut+length+(R-cut-length)*F(j, m) for j in range(m+1)]
                exact_edges = el+er
                exact_mids = [(v[j]+v[j+1])/2 for v in (el, er) for j in range(m)]
                exact_weights = [(cut+R)/(m*tail)]*m+[(R-cut-length)/(m*tail)]*m
                got_weights = list(map(ff, weights[i]))
                ledger.check(list(map(ff, mids[i])) == exact_mids, case, 'Production midpoints equal exact rational construction')
                ledger.check(list(map(ff, edges[i])) == exact_edges, case, 'Production edges equal exact rational construction')
                ledger.check(got_weights == exact_weights, case, 'Production weights equal exact rational construction')
                ledger.check(sum(got_weights) == 1 and min(got_weights) >= 0, case, 'Exactly unit density mass and nonnegative weights')
                ledger.check(all(w > 0 for w in got_weights if w != 0), case, 'Every retained nonempty cell has positive weight')
                ledger.check(sum(w == 0 for w in got_weights) == (m if cut in (-R, R-length) else 0), case, 'Only empty boundary tail has zero weights; production still pays those nodes')
                rows.append(dict(alpha=alpha, m=m, cut=cut, mass=sum(got_weights),
                                 minimum_weight=min(got_weights), zero_weights=sum(w == 0 for w in got_weights),
                                 cells=2*m, original_density_on_tail=1/(1-alpha)))
    ledger.check(len(rows) == 228, 'density', 'All fixed density cases retained')
    return rows


def original_economy_audit(production, np, exact, ledger):
    rows, reference_rows, context_data = [], [], []
    cache = {}

    def terminal_at(state, alpha):
        key = (tuple(state), alpha)
        if key not in cache:
            lo, hi, action = exact.terminal_bounds(state, alpha, steps=TERMINAL_ROOT_STEPS)
            poly = exact.polynomial_from_primitives(state, action)
            risk, left, right, eta = exact.tail_threshold(poly, alpha)
            value, gradient = exact.objective_gradient(state, action, alpha)
            case = f'primitive:{len(cache)}'
            ledger.check(poly[2] == 5, case, 'Original terminal polynomial reconstructed from primitive point values')
            ledger.check(value == hi and lo <= value, case, 'Independent primitive value and root enclosure agree')
            ledger.check(hi-lo <= TERMINAL_ALLOWANCE, case, 'Independent last-date bound tighter than unchanged controller allowance')
            cache[key] = dict(lower=lo, upper=hi, action=action, polynomial=poly, risk=risk,
                              tail=(left, right), eta=eta, gradient=gradient)
        return cache[key]

    for name, state in ORIGINAL_STATES:
        cap = F(1, 8)+sum(state)/(8*len(state))
        actions = (('zero', F(0)), ('half_capacity', cap/2), ('near_capacity', cap-F(1, 2**36)))
        for alpha in (F(1, 2), F(3, 4)):
            for action_name, action in actions:
                context = f'{name}:alpha={alpha}:action={action_name}'
                try:
                    stage = exact.economic_S(state)+action*action+4*action**4
                    mid = [terminal_at(exact.next_state(state, action, -R+F(2*j+1, 2*REFERENCE_BINS)*(2*R)), alpha)['lower'] for j in range(REFERENCE_BINS)]
                    end = [terminal_at(exact.next_state(state, action, -R+F(j, REFERENCE_BINS)*(2*R)), alpha)['upper'] for j in range(REFERENCE_BINS+1)]
                    mixture = [v for j in range(REFERENCE_BINS) for v in (end[j], end[j+1])]
                    qlo, qhi = stage+BETA*finite_avar(mid, alpha), stage+BETA*finite_avar(mixture, alpha)
                    reference = dict(context=context, state=state, alpha=alpha, action=action,
                                     optimum_continuation_lower=qlo, optimum_continuation_upper=qhi,
                                     implemented_policy_lower=qlo, implemented_policy_upper=qhi+BETA*TERMINAL_ALLOWANCE,
                                     full_support_bins=REFERENCE_BINS, terminal_root_steps=TERMINAL_ROOT_STEPS)
                    reference_rows.append(reference)
                    x, aa = np.array([list(map(float, state))]), np.array([float(action)])
                    tail_state = production.tail_state(x, aa, float(alpha))
                    cut = ff(tail_state['cut'][0]); length, tail_length = 2*R*alpha, 2*R*(1-alpha)
                    fl = terminal_at(exact.next_state(state, action, cut), alpha)
                    fr = terminal_at(exact.next_state(state, action, cut+length), alpha)
                    dlo, dhi = fr['lower']-fl['upper'], fr['upper']-fl['lower']
                    prod_dlo, prod_dhi = ff(tail_state['derivative_lower'][0]), ff(tail_state['derivative_upper'][0])
                    ledger.check(prod_dlo <= dlo <= dhi <= prod_dhi, context, 'Outward residual contains independent exact terminal-value difference enclosure')
                    exact_gain = max(exact_constrained_gain(v, F(181, 64)*length, cut, -R, R-length) for v in (prod_dlo, prod_dhi))
                    ledger.check(ff(tail_state['kappa'][0]) >= exact_gain/tail_length, context, 'Original-risk tail defect covers independent constrained minimization')
                    for m in ORIGINAL_MESHES:
                        case = f'{context}:m={m}'
                        produced = production.certificate(x, aa, float(alpha), m, tail_state)
                        left_edges = [-R+(cut+R)*F(j, m) for j in range(m+1)]
                        right_edges = [cut+length+(R-cut-length)*F(j, m) for j in range(m+1)]
                        selected_lo, selected_hi = F(0), F(0)
                        for edges in (left_edges, right_edges):
                            for l, r in zip(edges, edges[1:]):
                                weight = (r-l)/tail_length
                                vm = terminal_at(exact.next_state(state, action, (l+r)/2), alpha)
                                vl = terminal_at(exact.next_state(state, action, l), alpha)
                                vr = terminal_at(exact.next_state(state, action, r), alpha)
                                selected_lo += weight*vm['lower']
                                selected_hi += weight*(vl['upper']+vr['upper'])/2
                        p = {key: ff(produced[key][0]) for key in ('lower', 'upper', 'optimum_lower', 'loss', 'width', 'kappa', 'selected_tail_lower', 'selected_tail_upper', 'slope_lower', 'slope_upper')}
                        ledger.check(p['selected_tail_lower'] <= selected_lo <= selected_hi <= p['selected_tail_upper'], case, 'Independent exact midpoint/secant enclosures inside outward selected-tail bounds')
                        ledger.check(p['lower'] <= stage+BETA*selected_lo, case, 'Original stage and selected-tail lower bound aggregated outward')
                        ledger.check(p['upper'] >= stage+BETA*(selected_hi+exact_gain/tail_length+TERMINAL_ALLOWANCE), case, 'Original policy upper charges risk localization and unchanged terminal policy')
                        ledger.check(p['lower'] <= reference['implemented_policy_upper'] and reference['implemented_policy_lower'] <= p['upper'], case, 'Independent full-support original-policy interval overlaps certificate')
                        true_minimum = p['lower']-max(exact_constrained_gain(v, F(2), action, F(0), cap) for v in (p['slope_lower'], p['slope_upper']))
                        ledger.check(p['optimum_lower'] <= true_minimum, case, 'Outward original-action quadratic minimization includes full feasible capacity')
                        ledger.check(p['loss'] >= p['upper']-p['optimum_lower'] >= 0, case, 'Complete-policy regret allowance arithmetic')
                        ledger.check(p['width'] >= p['upper']-p['lower'] >= 0, case, 'Original-policy width arithmetic')
                        ledger.check(p['optimum_lower'] <= qhi, case, 'Optimum lower bound consistent with independent feasible policy')
                        rows.append(dict(case=case, state=state, alpha=alpha, action=action, cut=cut, m=m,
                                         production=p, independent_selected_lower=selected_lo,
                                         independent_selected_upper=selected_hi, independent_tail_defect=exact_gain/tail_length,
                                         reference_context=context, qualified=p['loss'] <= F(1, 256) and p['width'] <= F(1, 8192)))
                    context_data.append((name, alpha, action, rows[-len(ORIGINAL_MESHES):], reference))
                except Exception:
                    ledger.exception(context)
                    rows.append(dict(case=context, exception=traceback.format_exc()))
                print(f'original audit {context}: {len(cache)} rational terminal contexts retained', flush=True)
    # These finite cross-action probes diagnose the global-minorant implementation;
    # they do not replace the all-action proof in the supplement.
    for name, alpha, action, local_rows, reference in context_data:
        for other_name, other_alpha, candidate, _, other_reference in context_data:
            if (other_name, other_alpha) != (name, alpha):
                continue
            displacement = candidate-action
            for row in local_rows:
                p = row['production']
                lower_support = p['lower']+min(p['slope_lower']*displacement, p['slope_upper']*displacement)+displacement**2
                ledger.check(lower_support <= other_reference['optimum_continuation_upper'], row['case'], 'Finite independent cross-action original-Q support consistency')
    ledger.check(len(reference_rows) == 24, 'original', 'All fixed original-economy reference contexts retained')
    ledger.check(len(rows) == 72, 'original', 'All fixed original-economy resolution cases retained')
    primitives = [dict(state=key[0], alpha=key[1], **value) for key, value in cache.items()]
    return dict(rows=rows, reference_rows=reference_rows, primitive_records=primitives,
                scope='Finite deterministic original investment audit, 24 state/action/risk contexts and 72 resolutions. Independent whole-support intervals concern the same original Q and unchanged terminal-controller allowance. Interval overlap and cross-action probes are consistency checks, not exact observed policy regret or a replacement for the continuum proof.')


def audit(output):
    ledger, result = Ledger(), {}
    production, np, exact = load_science()
    for name, operation in (
        ('constrained_gain', lambda: gain_audit(production, np, ledger)),
        ('dyadic_density', lambda: density_audit(production, np, ledger)),
        ('original_economy', lambda: original_economy_audit(production, np, exact, ledger)),
    ):
        try:
            result[name] = operation()
        except Exception:
            ledger.exception(name)
            result[name] = dict(exception=traceback.format_exc())
        save(output/'AUDIT_PROGRESS119.json', dict(checks=ledger.checks, failures=ledger.failures, completed=list(result)))
    result.update(status='failed' if ledger.failures else 'passed', checks=ledger.checks,
                  failures=ledger.failures, numpy_version=np.__version__)
    save(output/'INDEPENDENT_TAIL119.json', result)
    return result


def bind_sources(commit):
    if len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('A full lowercase immutable Git commit is required')
    required = [ROOT/'code119/independent_tail119.py', ROOT/'code119/active_tail119.py',
                ROOT/'VALIDATION_PROTOCOL119.md', ROOT/'PROTOCOL119.md', ROOT/'REVISION_BOUNDARY119.md',
                ROOT/'frozen108/SOURCE_FREEZE108.json']
    frozen = json.loads((ROOT/'frozen108/SOURCE_FREEZE108.json').read_text())['scientific_files']
    for relative, expected in frozen.items():
        path = ROOT/'frozen108'/relative
        if digest(path) != expected:
            raise ValueError(f'Inherited frozen source mismatch: {relative}')
        required.append(path)
    identities = []
    for path in sorted(set(required)):
        relative = path.relative_to(REPO).as_posix()
        committed = subprocess.run(['git', 'show', f'{commit}:{relative}'], cwd=REPO, check=True, capture_output=True).stdout
        if path.read_bytes() != committed:
            raise ValueError(f'Execution source differs from prospective commit: {relative}')
        identities.append(dict(path=relative, sha256=digest(path)))
    return dict(custody_commit=commit, sources=identities, python=sys.version,
                platform=platform.platform(), source_policy='Exact committed bytes checked before any scientific imports or observations.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('supporting', 'audit'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--custody-commit', required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Refusing to overwrite any prior execution or failed attempt')
    args.output.mkdir(parents=True)
    started = time.time()
    try:
        provenance = bind_sources(args.custody_commit)
        provenance.update(mode=args.mode, started_unix=started, argv=sys.argv)
        save(args.output/'PROVENANCE119.json', provenance)
        result = supporting(args.output) if args.mode == 'supporting' else audit(args.output)
        save(args.output/'EXECUTION119.json', dict(status=result['status'], mode=args.mode,
             custody_commit=args.custody_commit, started_unix=started, ended_unix=time.time(),
             output_files=[dict(path=p.name, sha256=digest(p)) for p in sorted(args.output.iterdir()) if p.is_file()]))
        if result['status'] != 'passed':
            raise ArithmeticError('One or more retained independent checks failed; inspect the complete output')
    except Exception:
        save(args.output/'FAILED119.json', dict(mode=args.mode, custody_commit=args.custody_commit,
             started_unix=started, failed_unix=time.time(), exception=traceback.format_exc()))
        raise


if __name__ == '__main__':
    main()
