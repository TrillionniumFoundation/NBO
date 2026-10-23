"""Independent rational finite-design readout certificates for R121.

Only standard-library arithmetic and serialized basis descriptions are used.
No production feature, optimization, actor, or economic kernel is imported.
Certificates concern the declared finite design and box, not an unproved
off-design error bound or an original-policy regret bound.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
from functools import lru_cache
import gzip
import json
from pathlib import Path
import resource
import time
import traceback

from custody121 import verify_source
from io121 import append_jsonl, digest, exclusive_attempt, write_json

COUNTS = {}


def require(condition, message):
    COUNTS['assertions'] = COUNTS.get('assertions', 0)+1
    if not condition:
        raise ArithmeticError(message)


def rat(value):
    if isinstance(value, dict) and set(value) >= {'numerator', 'denominator'}:
        return F(value['numerator'], value['denominator'])
    return F(value)


def encode(value):
    if isinstance(value, F):
        return dict(numerator=value.numerator, denominator=value.denominator)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    return value


@lru_cache(maxsize=None)
def bspline_axis(knots, degree, x, derivative=False):
    """Cox--de Boor recurrence, including the exact inward endpoint limit."""
    k = tuple(map(F, knots)); x = F(x)
    require(k[0] <= x <= k[-1], 'Spline domain')
    base = [F(int(k[i] <= x < k[i+1])) for i in range(len(k)-1)]
    if x == k[-1]:
        active = max(i for i in range(len(k)-1) if k[i] < k[i+1])
        base[active] = F(1)
    levels = [base]
    for p in range(1, degree+1):
        old = levels[-1]; new = []
        for i in range(len(k)-p-1):
            left = F(0) if k[i+p] == k[i] else (x-k[i])*old[i]/(k[i+p]-k[i])
            right = F(0) if k[i+p+1] == k[i+1] else (k[i+p+1]-x)*old[i+1]/(k[i+p+1]-k[i+1])
            new.append(left+right)
        levels.append(new)
    if not derivative:
        return tuple(levels[-1])
    old = levels[-2]; answer = []
    for i in range(len(k)-degree-1):
        left = F(0) if k[i+degree] == k[i] else degree*old[i]/(k[i+degree]-k[i])
        right = F(0) if k[i+degree+1] == k[i+1] else degree*old[i+1]/(k[i+degree+1]-k[i+1])
        answer.append(left-right)
    return tuple(answer)


@lru_cache(maxsize=None)
def hat_axis(knots, x, derivative=False, side=0):
    k = tuple(map(F, knots)); x = F(x)
    require(k[0] <= x <= k[-1], 'Hat domain')
    choices = [i for i in range(len(k)-1)
               if (k[i] < x <= k[i+1] if side < 0 else k[i] <= x < k[i+1])]
    cell = choices[0] if choices else (0 if x == k[0] else len(k)-2)
    width = k[cell+1]-k[cell]; answer = [F(0)]*len(k)
    if derivative:
        answer[cell], answer[cell+1] = -1/width, 1/width
    else:
        answer[cell], answer[cell+1] = (k[cell+1]-x)/width, (x-k[cell])/width
    return tuple(answer)


def basis(desc, u, derivative=False, side=0):
    """Sparse exact serialized feature row, D_a when derivative=True."""
    x, y, v = map(F, u); kind = desc['type']; answer = {}
    require(all(F(0) <= z <= 1 for z in (x, y, v)), 'Feature domain')
    if kind == 'monomial':
        for j, (p, q, r) in enumerate(desc['exponents']):
            z = x**p*y**q*(r*v**(r-1) if derivative else v**r)
            if z:
                answer[j] = z
    elif kind == 'anchored_relu':
        for j, (p, q, r) in enumerate(desc['base_exponents']):
            z = x**p*y**q*(r*v**(r-1) if derivative else v**r)
            if z:
                answer[j] = z
        offset = len(desc['base_exponents'])
        for j, unit in enumerate(desc['units']):
            wx, wy, wv = map(F, unit['direction'])
            cx, cy = map(F, unit['state_center']); scale = F(unit['scale'])
            anchor = scale*(wx*(x-cx)+wy*(y-cy)-F(unit['threshold']))
            z = anchor+scale*wv*v
            require(wv > 0 and scale > 0, 'Declared positive action feature directions')
            value = (scale*wv if z > 0 or (z == 0 and side >= 0) else F(0)) if derivative else max(F(0), z)-max(F(0), anchor)
            if value:
                answer[offset+j] = value
    elif kind in ('tensor_bspline', 'tensor_hat'):
        if kind == 'tensor_bspline':
            axes = [bspline_axis(tuple(k), desc['degree'], z, derivative and j == 2)
                    for j, (k, z) in enumerate(zip(desc['knots'], (x, y, v)))]
        else:
            axes = [hat_axis(tuple(k), z, derivative and j == 2, side if j == 2 else 0)
                    for j, (k, z) in enumerate(zip(desc['knots'], (x, y, v)))]
        for j, (p, q, r) in enumerate(desc['columns']):
            value = axes[0][p]*axes[1][q]*axes[2][r]
            if value:
                answer[j] = value
    else:
        raise ValueError('Unknown serialized basis')
    if derivative:
        cap = F(1, 8)+(x+y)/16
        answer = {j: z/cap for j, z in answer.items()}
    COUNTS['exact_feature_rows'] = COUNTS.get('exact_feature_rows', 0)+1
    COUNTS['nonzero_feature_entries'] = COUNTS.get('nonzero_feature_entries', 0)+len(answer)
    return answer


def dot(row, theta):
    return sum((v*theta[j] for j, v in row.items()), F(0))


def box_min(gradient, lower, upper):
    return sum((g*(lo if g >= 0 else hi) for g, lo, hi in zip(gradient, lower, upper)), F(0))


def load_json(path):
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt', encoding='utf-8') as stream:
        return json.load(stream)


def audit_model(model, fit, labels, design, witness_path):
    start = time.perf_counter(); desc = model['basis']; n = desc['feature_count']
    theta = [F(int(v), model['theta_denominator']) for v in model['theta_numerators']]
    lower, upper = list(map(F, desc['coefficient_lower'])), list(map(F, desc['coefficient_upper']))
    require(len(theta) == n == len(lower) == len(upper), 'Readout dimension')
    require(all(lo <= t <= hi for t, lo, hi in zip(theta, lower, upper)), 'Exact coefficient box')
    require(model['theta_denominator'] == 2**30, 'Prospective 30-bit coefficients')
    require(theta == list(map(F, model['theta'])), 'Serialized exact readout values')
    require(model['theta_hex'] == [float(t).hex() for t in theta], 'Serialized readout hexadecimal identity')
    for row in labels['marginals']:
        require(F(row['continuation_marginal_lower']) <= F(row['continuation_marginal_upper']), 'Marginal interval order')
    dr = []
    for i, row in enumerate(labels['marginals']):
        v = F(row['u'][2])
        sides = [1] if v == 0 else [-1] if v == 1 else [-1, 1] if desc['type'] in ('anchored_relu', 'tensor_hat') else [0]
        for side in sides:
            dr.append(dict(label_index=i, u=row['u'], side=side,
                           lower=row['continuation_marginal_lower'], upper=row['continuation_marginal_upper']))
    require(dr == design['derivative_rows'], 'Independently assembled one-sided derivative design')
    matrix = []; dl = []; dh = []; node_upper = F(0); max_assembly = F(0)
    for i, row in enumerate(dr):
        exact = basis(desc, row['u'], True, row['side']); matrix.append(exact)
        lo, hi = F(row['lower']), F(row['upper']); dl.append(lo); dh.append(hi)
        value = dot(exact, theta); residual = max(value-lo, hi-value)
        node_upper = max(node_upper, residual)
        saved = design['derivative_matrix'][i]
        require(len(saved) == n, 'Derivative matrix width')
        max_assembly = max(max_assembly, max(abs(exact.get(j, F(0))-F(z)) for j, z in enumerate(saved)))
        append_jsonl(witness_path, encode(dict(kind='marginal-primal', row=i, exact_feature=exact,
                       lower=lo, upper=hi, fitted=value, robust_residual=residual)))
    objective = F(0); gradient = [F(0)]*n; value_assembly = F(0)
    for i, row in enumerate(labels['values']):
        exact = basis(desc, row['u']); lo = F(row['continuation_difference_lower']); hi = F(row['continuation_difference_upper'])
        require(lo <= hi, 'Value interval order')
        target = (lo+hi)/2; residual = dot(exact, theta)-target; objective += residual**2
        for j, z in exact.items():
            gradient[j] += 2*z*residual
        saved = design['value_matrix'][i]
        value_assembly = max(value_assembly, max(abs(exact.get(j, F(0))-F(z)) for j, z in enumerate(saved)))
        append_jsonl(witness_path, encode(dict(kind='value-primal', row=i, exact_feature=exact,
                       target=target, residual=residual)))
    convex_lower = objective+box_min(gradient, lower, upper)-sum(g*t for g, t in zip(gradient, theta))
    # Squared loss is nonnegative; taking the maximum tightens a valid bound.
    convex_lower = max(F(0), convex_lower)
    require(convex_lower <= objective, 'Value convex-support lower bound')
    result = dict(loss=model['loss'], arm=desc['arm'], budget=desc['budget'], feature_count=n,
                  marginal_primal_upper=node_upper, value_sum_of_squares=objective,
                  value_mean_of_squares=objective/len(labels['values']),
                  value_optimum_lower=convex_lower, value_optimality_gap_upper=objective-convex_lower,
                  derivative_assembly_max_exact_error=max_assembly, value_assembly_max_exact_error=value_assembly,
                  finite_node_claim_only=True, policy_certificate_claimed=False,
                  original_derivative_interval_validity_comes_from_separate_primitive_proof=True)
    if model['loss'] == 'marginal':
        raw = fit['raw_solver']['inequality_marginals']
        require(len(raw) == 2*len(matrix), 'All LP inequality dual multipliers')
        weights = [max(F(0), -F(z)) for z in raw]
        mass = sum(weights)
        require(mass >= 0, 'Nonnegative candidate dual mass')
        weights = [w/mass for w in weights] if mass else [F(1,len(weights))]*len(weights)
        plus = weights[:len(matrix)]; minus = weights[len(matrix):]
        require(sum(weights) == 1 and all(w >= 0 for w in weights), 'Exact normalized dual simplex')
        dual_gradient = [F(0)]*n
        constant = sum((-lo*p+hi*m for lo, hi, p, m in zip(dl, dh, plus, minus)), F(0))
        for row, p, m in zip(matrix, plus, minus):
            for j, z in row.items():
                dual_gradient[j] += (p-m)*z
        dual_lower = max(F(0), constant+box_min(dual_gradient, lower, upper))
        require(dual_lower <= node_upper, 'Rational LP weak duality for stored readout')
        result.update(marginal_optimum_lower=dual_lower, marginal_optimality_gap_upper=node_upper-dual_lower,
                      dual_weights_normalized_from_float_candidate=mass>0,
                      zero_candidate_mass_uses_prospective_uniform_weights=mass==0,
                      exact_dual_feasibility_does_not_require_float_stationarity=True)
        append_jsonl(witness_path, encode(dict(kind='marginal-dual', plus=plus, minus=minus,
                       box_gradient=dual_gradient, constant=constant, lower_bound=dual_lower)))
    append_jsonl(witness_path, encode(dict(kind='value-convex-support', gradient=gradient,
                   lower_bound=convex_lower, objective=objective)))
    result.update(seconds=time.perf_counter()-start)
    return result


def main():
    p = argparse.ArgumentParser(); p.add_argument('--source-commit', required=True)
    p.add_argument('--acquisition', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args(); source = verify_source(args.source_commit)
    out, initial = exclusive_attempt(args.output, 'training_audit121', source); clock = time.perf_counter()
    try:
        acquisition = args.acquisition.resolve(); paths = sorted((acquisition/'models').glob('*/*model.json'))
        if not paths:
            paths = sorted((acquisition/'models').glob('*/model.json'))
        require(len(paths) == 28, 'Two risks, seven representations, two losses in each acquisition')
        records = []
        for path in paths:
            model = load_json(path); folder = path.parent
            index = int(folder.name.split('-')[0])
            label_path = acquisition/f'labels-{index}.json'
            labels = load_json(label_path)
            fit_path = folder/'fit.json'; design_path = folder/'design.json.gz'
            fit, design = load_json(fit_path), load_json(design_path)
            receipt = audit_model(model, fit, labels, design, out/f'{folder.name}-witnesses.jsonl')
            receipt.update(index=index, alpha=labels['alpha'], model_sha256=digest(path),
                           labels_sha256=digest(label_path), fit_sha256=digest(fit_path), design_sha256=digest(design_path))
            append_jsonl(out/'models121.jsonl', encode(receipt)); records.append(encode(receipt))
            print('TRAINING_AUDIT', folder.name, 'complete', round(receipt['seconds'], 3), flush=True)
        write_json(out/'EXECUTION121.json', dict(status='executed', exit_code=0, source=source,
                   started_unix=initial['started_unix'], ended_unix=time.time(), total_seconds=time.perf_counter()-clock,
                   counts=COUNTS, audited_models=len(records), records=records,
                   max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   external_authorship_claimed=False, pure_standard_library_rational_arithmetic=True))
    except BaseException:
        append_jsonl(out/'FAILED121.jsonl', dict(status='failed', exception=traceback.format_exc(),
                       source=source, ended_unix=time.time(), elapsed_seconds=time.perf_counter()-clock,
                       counts=COUNTS, partial_evidence_retained=True))
        raise


if __name__ == '__main__':
    main()
