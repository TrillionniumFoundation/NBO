#!/usr/bin/env python3
"""Post-F124 exact audit of saved saturation premises, with no economic calls.

Only standard-library arithmetic and existing saved records are used. This is
a post-execution mathematical diagnosis, not a prospective trial or a retiming.
The caller supplies the immutable primary JSONL and its prior independent audit.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import time
import traceback


CHECKS = 0


def require(test, message):
    global CHECKS
    CHECKS += 1
    if not test:
        raise AssertionError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    return value


def write(path, value):
    Path(path).write_text(json.dumps(encode(value), indent=2, sort_keys=True) + "\n")


def key(row):
    return (row['index'], row['budget'], row['arm'], row['training_loss'],
            row['alpha'], row['row'])


def cone(glo, ghi, a, x, mu, L):
    d = x - a
    return (glo + (mu if d >= 0 else L) * d,
            ghi + (L if d >= 0 else mu) * d)


def contrast(glo, ghi, a, x, mu, L):
    d = x - a
    return (min(glo*d, ghi*d) + mu*d*d/2,
            max(glo*d, ghi*d) + L*d*d/2)


def constant_curvature(nodes, a, f, g, curvature):
    return ([f+g*(x-a)+curvature*(x-a)**2/2 for x in nodes] +
            [g+curvature*(x-a) for x in nodes])


def local_L_curvature(nodes, a, b, f, g, mu, L):
    """Curvature L on the action segment, mu on its complement."""
    left, right = min(a, b), max(a, b)
    K = L-mu
    positive = lambda x: max(F(0), x)
    def integral(x):
        return ((left-a)*(x-a) +
                (positive(x-left)**2-positive(a-left)**2
                 -positive(x-right)**2+positive(a-right)**2)/2)
    values = [f+g*(x-a)+mu*(x-a)**2/2+K*integral(x) for x in nodes]
    gradients = [g+mu*(x-a)+K*(max(left, min(right, x))-a) for x in nodes]
    return values+gradients


def feasible(problem, point, context):
    nodes = list(map(F, problem['nodes']))
    n = len(nodes)
    lo, hi = list(map(F, problem['lower'])), list(map(F, problem['upper']))
    mu, L, K = F(problem['mu']), F(problem['L']), F(problem['K'])
    require(len(point) == len(lo) == len(hi) == 2*n, context+' dimension')
    require(K == L-mu and K > 0, context+' curvature')
    for i, (v, l, u) in enumerate(zip(point, lo, hi)):
        require(l <= v <= u, context+f' box coordinate {i}')
    for i, (left, right) in enumerate(zip(nodes, nodes[1:])):
        d = right-left
        s = point[n+i+1]-point[n+i]-mu*d
        w = point[i+1]-point[i]-point[n+i]*d-mu*d*d/2
        require(d > 0 and 0 <= s <= K*d, context+f' slope edge {i}')
        require(s*s <= 2*K*w, context+f' lower area edge {i}')
        require(s*s <= 2*K*(s*d-w), context+f' upper area edge {i}')


def abstract_menu_witness():
    # This example uses the information class, not an evaluated investment state.
    mu, L, A = F(2), F(4), F(1, 4)
    a, b = F(0), A/2
    anchors = [(F(0), -mu*A, mu*A), (A, F(0), 2*mu*A)]
    for x, low, high in anchors:
        lo, hi = cone(low, high, x, a, mu, L)
        require(lo <= 0 <= hi, 'abstract menu witness has inactive anchor proposal')
    nodes = [F(0), b, A]
    for x in nodes:
        q = mu*(x*x-A*x)/2
        g = mu*(x-A/2)
        require(mu*(x-A) <= g <= mu*(x+A), 'abstract derivative cones')
        if x in (F(0), A):
            require(q == 0, 'abstract exact levels')
    bound = -mu*A*A/8
    require(bound == F(-1, 64), 'abstract chord gain')
    return dict(A=A, mu=mu, L=L, incumbent=a, candidate=b,
                paid_values=['q(0)=0', 'q(A)=0'], derivative_intervals=anchors,
                derivative_cone_lower='mu*(x-A)', derivative_cone_upper='mu*(x+A)',
                all_fused_and_single_anchor_proposals_equal_incumbent=True,
                exact_joint_upper=bound, attaining_function='mu*(x*x-A*x)/2',
                economic_evaluations=0, abstract_information_fixture=True)


def run(primary, receipt, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    try:
        identity = sha(primary)
        audit = json.loads(Path(receipt).read_text())
        require(audit.get('status') == 'executed' and audit.get('status_detail') == 'passed',
                'Prior independent audit has not passed')
        require(audit['primary_sha256'] == identity, 'Prior reader and primary hash differ')
        rows = [json.loads(line) for line in Path(primary).open()]
        require(len(rows) == 1856, 'Complete A primary census')
        source_ids = sorted({r['source_commit'] for r in rows})
        state_ids = sorted({r['state_commit'] for r in rows})
        require(len(source_ids) == len(state_ids) == 1, 'Single frozen A identity')
        pairs = {}
        for row in rows:
            k = key(row)
            require(row['mode'] in ('fused_two', 'joint_two'), 'Undeclared A service')
            require(row['mode'] not in pairs.setdefault(k, {}), 'Duplicate primary cell/state')
            pairs[k][row['mode']] = row
        require(len(pairs) == 928, 'Complete matched pairs')
        counts = Counter()
        slacks = []
        witness_file = out/'SATURATION_WITNESSES124.jsonl'
        case_file = out/'SATURATION_CASES124.jsonl'
        with witness_file.open('x') as wf, case_file.open('x') as cf:
            for k, pair in sorted(pairs.items()):
                require(set(pair) == {'fused_two', 'joint_two'}, 'Missing comparison mate')
                f, j = pair['fused_two'], pair['joint_two']
                context = repr(k)
                for field in ('state_hex', 'baseline_action_hex', 'case', 'full_common_menu',
                              'action_hex', 'complete_policy_lower', 'complete_policy_upper',
                              'original_optimum_lower', 'loss', 'width', 'counts',
                              'certified_policy_gain_lower', 'accepted_improvement',
                              'selected_menu_index'):
                    require(f[field] == j[field], context+' paired field '+field)
                require(j['enhancement_failure'] is None, context+' completed enhancement')
                case = j['case']
                require(case is not None, context+' paid information exists')
                A, a, mu, L = map(F, (case['A'], case['incumbent'], case['mu'], case['L']))
                ps = case['payloads']
                require(A == F(1, 8)+sum(map(F, j['state']))/16, context+' original capacity')
                require(a == F(j['baseline_action']) and 0 <= a <= A, context+' incumbent identity')
                require(0 < mu < L and mu == 2, context+' original curvature')
                require(len(ps) == len(j['initial_support_certificates']), context+' support count')
                counts['joint_rows'] += 1
                counts[f'rows_with_{len(ps)}_supports'] += 1
                counts['paired_actions_identical'] += 1
                all_cones_straddle = all(
                    lo <= 0 <= hi for lo, hi in
                    [cone(F(p['g_lower']), F(p['g_upper']), F(p['a']), a, mu, L) for p in ps])
                distinct = {F(z['b']) for z in j['full_common_menu']} - {a}
                all_at_incumbent = not distinct
                if len(ps) == 2:
                    counts['two_support_interior_incumbents'] += (0 < a < A)
                    counts['two_support_empty_nonincumbent_menu'] += all_at_incumbent
                    counts['two_support_all_individual_cones_straddle_zero'] += all_cones_straddle
                    require(all_at_incumbent and not j['selected_common_menu'],
                            context+' observed two-support candidate inactivity')
                require(len(f['selected_common_menu']) == len(j['selected_common_menu']),
                        context+' matched selected candidate count')
                if j['dual_solves_started']:
                    counts['solve_bearing_rows'] += 1
                    require(len(ps) == 1 and F(ps[0]['a']) == a,
                            context+' single paid anchor is incumbent')
                    require(j['dual_solves_started'] == j['dual_solves_completed'] ==
                            len(j['selected_common_menu']), context+' complete candidate solves')
                for jf, ff in zip(j['selected_common_menu'], f['selected_common_menu']):
                    counts['saturated_candidates'] += 1
                    require(jf['b'] == ff['b'] and jf['menu_index'] == ff['menu_index'],
                            context+' same finite candidate')
                    require(jf['certificate'] == ff['certificate'], context+' equal exact certificate')
                    require(jf['outward'] == ff['outward'], context+' equal outward certificate')
                    require(jf['dual_started'] and jf['dual_completed'], context+' solve custody')
                    p, original = ps[0], j['initial_support_certificates'][0]
                    W, U, glo, ghi = map(F, (p['W'], p['U'], p['g_lower'], p['g_upper']))
                    b = F(jf['b'])
                    require(0 <= b <= A and b != a and W <= U and glo <= ghi,
                            context+' scalar information premises')
                    for saved, raw in (('a', 'original_action'), ('W', 'support_anchor_lower'),
                                       ('U', 'original_q_upper'), ('p_lower', 'support_slope_lower'),
                                       ('p_upper', 'support_slope_upper')):
                        require(F(p[saved]) == F(original[raw]), context+' raw payload binding '+saved)
                    problem = jf['dual_witness']['problem']
                    nodes = list(map(F, problem['nodes']))
                    require(nodes == sorted({F(0), a, b, A}), context+' complete exact nodes')
                    require(F(problem['mu']) == mu and F(problem['L']) == L,
                            context+' same node curvatures')
                    require(nodes[problem['origin_index']] == a and
                            nodes[problem['target_index']] == b, context+' contrast orientation')
                    intervals = [contrast(glo, ghi, a, x, mu, L) for x in nodes]
                    cones = [cone(glo, ghi, a, x, mu, L) for x in nodes]
                    expected_lo = [W+v[0] for v in intervals]+[v[0] for v in cones]
                    expected_hi = [U+v[1] for v in intervals]+[v[1] for v in cones]
                    require(list(map(F, problem['lower'])) == expected_lo and
                            list(map(F, problem['upper'])) == expected_hi,
                            context+' full boxes equal sole-anchor transported information')
                    low, high = contrast(glo, ghi, a, b, mu, L)
                    require(F(ff['certificate']['change_lower']) == low and
                            F(ff['certificate']['change_upper']) == high,
                            context+' fused integrated bounds equal exact scalar formula')
                    g = ghi if b > a else glo
                    upper_point = constant_curvature(nodes, a, U, g, L)
                    lower_point = constant_curvature(nodes, a, W, glo if b > a else ghi, mu)
                    local_point = local_L_curvature(nodes, a, b, U, g, mu, L)
                    for name, point in (('upper', upper_point), ('lower', lower_point),
                                        ('local-curvature-upper', local_point)):
                        feasible(problem, point, context+' '+name)
                        value = point[problem['target_index']]-point[problem['origin_index']]
                        require(value == (low if name == 'lower' else high), context+' attained '+name)
                    n = len(nodes)
                    cap_compatible = all(F(-7) <= v <= F(7) for v in local_point[n:])
                    counts['local_L_witness_respects_global_cap_7'] += cap_compatible
                    counts['global_L_witness_exceeds_cap_7'] += any(abs(v) > 7 for v in upper_point[n:])
                    q_upper = U+high
                    require(F(ff['certificate']['upper']) == q_upper+F(case['delta']),
                            context+' fused absolute upper')
                    recorded_dual = F(jf['dual_witness']['dual']['contrast_upper'])
                    require(recorded_dual >= high, context+' sound dual cannot beat feasible witness')
                    require(min(high, recorded_dual) == high and
                            min(q_upper+F(case['delta']), U+high+F(case['delta'])) ==
                            F(ff['certificate']['upper']), context+' no-solve exact replacement')
                    slacks.append(recorded_dual-high)
                    counts['recorded_slsqp_iterations'] += jf['dual_witness']['solver'].get('nit', 0)
                    counts['recorded_objective_evaluations'] += jf['dual_witness']['solver'].get('nfev', 0)
                    counts['recorded_objective_jacobian_evaluations'] += jf['dual_witness']['solver'].get('njev', 0)
                    wf.write(json.dumps(encode(dict(cell_state=k, menu_index=jf['menu_index'],
                        a=a, b=b, W=W, U=U, glo=glo, ghi=ghi, nodes=nodes, mu=mu, L=L,
                        contrast_lower=low, contrast_upper=high, upper_point=upper_point,
                        lower_point=lower_point, cap_compatible_upper_point=local_point,
                        cap_compatible=cap_compatible, recorded_dual_excess=recorded_dual-high,
                        raw_support_constraints_not_added_to_interpolation=True)), sort_keys=True)+'\n')
                cf.write(json.dumps(encode(dict(cell_state=k, support_count=len(ps),
                    distinct_paid_anchors=len({F(p['a']) for p in ps}),
                    incumbent_is_interior=0 < a < A, full_menu_size=len(j['full_common_menu']),
                    distinct_nonincumbent_candidates=len(distinct),
                    all_individual_derivative_cones_straddle_zero=all_cones_straddle,
                    recorded_dual_calls=j['dual_solves_started'],
                    post_execution_no_solve_gate_applicable=bool(j['dual_solves_started']) and len(ps)==1
                        and F(ps[0]['a'])==a)), sort_keys=True)+'\n')
        require(counts['saturated_candidates'] == 404 and counts['solve_bearing_rows'] == 202,
                'Complete saved A saturation census')
        require(counts['rows_with_1_supports'] == 830 and counts['rows_with_2_supports'] == 98,
                'Complete observed support census')
        fixture = abstract_menu_witness()
        write(out/'MENU_STARVATION_WITNESS124.json', fixture)
        result = dict(status='passed-exact-post-execution-saturation-audit',
            phase='post-F124-A mathematical diagnosis, not prospective economic evidence',
            primary_sha256=identity, prior_independent_audit_sha256=sha(receipt),
            checker_sha256=sha(__file__), source_commit=source_ids[0], state_commit=state_ids[0],
            completed_utc=datetime.now(timezone.utc).isoformat(), seconds=time.perf_counter()-started,
            assertions=CHECKS, counts=dict(counts),
            recorded_dual_excess_min=min(slacks), recorded_dual_excess_max=max(slacks),
            optimization_calls_mathematically_redundant_for_the_implemented_relaxation=404,
            fresh_economic_evaluations=0, fresh_random_draws=0,
            production_or_scientific_library_imports=False, frozen_files_modified=False,
            elapsed_time_saving_claimed=False, frozen_campaign_costs_rescored=False,
            raw_support_or_full_primitive_minimax_claimed=False,
            witnesses_sha256=sha(witness_file), cases_sha256=sha(case_file))
        write(out/'SATURATION124.json', result)
        print(json.dumps(encode(result), indent=2, sort_keys=True))
    except Exception:
        write(out/'FAILURE_SATURATION124.json', dict(status='failed', assertions=CHECKS,
            seconds=time.perf_counter()-started, traceback=traceback.format_exc(),
            partial_outputs_retained=True, fresh_economic_evaluations=0))
        raise


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--primary', required=True)
    ap.add_argument('--audit', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    run(args.primary, args.audit, args.output)
