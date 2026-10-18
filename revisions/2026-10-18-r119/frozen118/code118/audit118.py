"""Independent exact audit: no import of the production recovery algorithm.

Endpoint optima use coefficient-form quadratic completion. The continuum
reference tests all stationary points, constraints and the affine crossing.
The grid reference exhaustively evaluates all 33 actions in every cell.
"""
from fractions import Fraction as F
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import time


def audit(output: Path) -> dict:
    destination = output/'AUDIT118.json'
    if destination.exists():
        raise FileExistsError('Never overwrite an audit receipt')
    start = time.perf_counter()
    data = json.loads((output/'CATALOGUE118.json').read_text())
    endpoints = tuple(map(F, ['-8', '-4', '-2', '-1', '0', '1/4', '1/2', '1', '2', '4', '8']))
    expected = set(itertools.product(tuple(itertools.combinations_with_replacement(endpoints, 2)),
        (F(15,16), F(1)), (F(2), F(8)), (F(1,4), F(1,2), F(3,4))))
    checks, reference_evaluations, seen = 0, 0, set()
    for row in data['rows']:
        lo, hi, beta, mu, center = [F(row[x]) for x in ('lo', 'hi', 'beta', 'mu', 'a0')]
        identity = ((lo, hi), beta, mu, center)
        if identity not in expected or identity in seen:
            raise ArithmeticError('Missing, unexpected or duplicate context')
        seen.add(identity)
        coeff = [(mu/2, beta*t-mu*center, mu*center**2/2) for t in (lo, hi)]
        optima, values = [], []
        for a, b, c in coeff:
            if b >= 0:
                x, v = F(0), c
            elif 2*a+b <= 0:
                x, v = F(1), a+b+c
            else:
                x, v = -b/(2*a), c-b*b/(4*a)
            optima.append(x)
            values.append(v)
        if list(map(F, row['endpoint_optimal_actions'])) != optima or list(map(F, row['endpoint_optimal_costs'])) != values:
            raise ArithmeticError('Endpoint optimum disagreement')
        checks += 4

        def endpoint_regrets(x):
            nonlocal reference_evaluations
            reference_evaluations += 2
            return [a*x*x+b*x+c-v for (a,b,c),v in zip(coeff, values)]

        def worst(x):
            return max(endpoint_regrets(x))

        candidates = set([F(0), F(1)] + optima)
        db = coeff[1][1]-coeff[0][1]
        dc = (coeff[1][2]-values[1])-(coeff[0][2]-values[0])
        if db and 0 <= -dc/db <= 1:
            candidates.add(-dc/db)
        continuum = min((worst(x), x) for x in candidates)
        exact = F(row['action'])
        if continuum != (F(row['worst_regret']), exact):
            raise ArithmeticError('Continuous minimax reference mismatch')
        if endpoint_regrets(exact) != list(map(F, row['endpoint_regrets'])):
            raise ArithmeticError('Endpoint regret mismatch')
        midpoint = F(row['midpoint_action'])
        if worst(midpoint) != F(row['midpoint_worst_regret']) or worst(exact) > worst(midpoint):
            raise ArithmeticError('Midpoint comparison mismatch')
        grid = [(worst(F(k,32)), F(k,32)) for k in range(33)]
        if min(grid) != (F(row['grid_worst_regret']), F(row['grid_action'])):
            raise ArithmeticError('Exhaustive discrete minimax mismatch')
        for trial in row['grid_candidates']:
            if worst(F(trial['action'])) != F(trial['worst_regret']):
                raise ArithmeticError('Grid trial discrepancy')
        if F(row['width']) != hi-lo or F(row['regret_reduction']) != worst(midpoint)-worst(exact):
            raise ArithmeticError('Width or reduction discrepancy')
        checks += 10+len(candidates)+33+len(row['grid_candidates'])
    if seen != expected or data['cells'] != 792:
        raise ArithmeticError('Incomplete catalogue')
    result = {'status': 'passed', 'cells': len(seen), 'exact_record_checks': checks,
        'exhaustive_grid_actions': 33*len(seen), 'reference_endpoint_evaluations': reference_evaluations,
        'production_endpoint_evaluations': data['endpoint_objective_evaluations'],
        'strict_improvements': sum(F(r['regret_reduction']) > 0 for r in data['rows']),
        'equal_regret': sum(F(r['regret_reduction']) == 0 for r in data['rows']),
        'nonzero_width_zero_regret': sum(F(r['width']) > 0 and F(r['worst_regret']) == 0 for r in data['rows']),
        'seconds': time.perf_counter()-start,
        'catalogue_sha256': hashlib.sha256((output/'CATALOGUE118.json').read_bytes()).hexdigest(),
        'audit_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope': 'Independent exact coefficient and exhaustive-grid implementations; not a proof assistant or a new investment experiment.'}
    for key in ('strict_improvements', 'equal_regret', 'nonzero_width_zero_regret'):
        if result[key] != data[key]:
            raise ArithmeticError('Catalogue summary mismatch: '+key)
    destination.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    print(json.dumps(audit(parser.parse_args().output), indent=2))
