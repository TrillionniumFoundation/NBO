"""Exact minimax Bellman-action recovery for a supplied risk interval.

This is a scalar quadratic Bellman oracle subproblem, not the investment
experiment. The executable catalogue is fixed in PROTOCOL118.md. All
arithmetic in decisions, objective values and certificates is rational.
"""
from fractions import Fraction as F
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import platform
import sys
import time

ENDPOINTS = tuple(map(F, ('-8', '-4', '-2', '-1', '0', '1/4', '1/2', '1', '2', '4', '8')))
BETAS = (F(15, 16), F(1))
CURVATURES = (F(2), F(8))
CENTERS = (F(1, 4), F(1, 2), F(3, 4))
DENOMINATOR = 32


def project(a: F) -> F:
    return max(F(0), min(F(1), a))


def cost(a: F, theta: F, beta: F, mu: F, a0: F) -> F:
    return mu * (a-a0)**2 / 2 + beta*a*theta


def recover(lo: F, hi: F, beta: F, mu: F, a0: F) -> dict:
    if any(not isinstance(v, F) for v in (lo, hi, beta, mu, a0)):
        raise TypeError('Exact Fraction inputs are required')
    if lo > hi or beta <= 0 or mu <= 0 or not F(0) <= a0 <= F(1):
        raise ValueError('Invalid risk interval or economic parameters')
    pl, pu = (project(a0-beta*t/mu) for t in (lo, hi))
    vl, vu = cost(pl, lo, beta, mu, a0), cost(pu, hi, beta, mu, a0)
    evaluations = 2  # Endpoint optimum values, paid once per standalone call.
    if pl == pu:
        robust = pl
    else:
        robust = (vu-vl)/(beta*(hi-lo))
    if not pu <= robust <= pl:
        raise ArithmeticError('Secant action violates optimizer bracket')
    midpoint = project(a0-beta*(lo+hi)/(2*mu))

    def evaluate(a: F) -> tuple:
        nonlocal evaluations
        values = (cost(a, lo, beta, mu, a0), cost(a, hi, beta, mu, a0))
        evaluations += 2
        regrets = (values[0]-vl, values[1]-vu)
        if min(regrets) < 0:
            raise ArithmeticError('Negative regret')
        return values, regrets, max(regrets)

    rv, rr, rg = evaluate(robust)
    mv, mr, mg = evaluate(midpoint)
    k = robust*DENOMINATOR
    floor = k.numerator//k.denominator
    ceil = -(-k.numerator//k.denominator)
    candidates = sorted({F(floor, DENOMINATOR), F(ceil, DENOMINATOR)})
    tried = []
    for a in candidates:
        cv, cr, cg = evaluate(a)
        tried.append({'action': str(a), 'endpoint_costs': list(map(str, cv)),
                      'endpoint_regrets': list(map(str, cr)), 'worst_regret': str(cg)})
    chosen = min(tried, key=lambda r: (F(r['worst_regret']), F(r['action'])))
    if rg > mg:
        raise ArithmeticError('Minimax action worse than midpoint control')
    return {
        'lo': str(lo), 'hi': str(hi), 'width': str(hi-lo), 'beta': str(beta),
        'mu': str(mu), 'a0': str(a0), 'endpoint_optimal_actions': list(map(str, (pl, pu))),
        'endpoint_optimal_costs': list(map(str, (vl, vu))), 'action': str(robust),
        'endpoint_costs': list(map(str, rv)), 'endpoint_regrets': list(map(str, rr)),
        'worst_regret': str(rg), 'midpoint_action': str(midpoint),
        'midpoint_endpoint_costs': list(map(str, mv)),
        'midpoint_endpoint_regrets': list(map(str, mr)), 'midpoint_worst_regret': str(mg),
        'regret_reduction': str(mg-rg), 'same_endpoint_optimizer': pl == pu,
        'grid_denominator': DENOMINATOR, 'grid_candidates': tried,
        'grid_action': chosen['action'], 'grid_worst_regret': chosen['worst_regret'],
        'endpoint_objective_evaluations': evaluations,
        'continuous_recovery_endpoint_values': 2,
        'continuous_certificate_endpoint_evaluations': 2,
        'midpoint_control_endpoint_evaluations': 2,
        'grid_endpoint_evaluations': 2*len(tried),
    }


def run(output: Path, freeze_commit: str) -> dict:
    if output.exists():
        raise FileExistsError('Never overwrite an attempted catalogue')
    if len(freeze_commit) != 40 or any(c not in '0123456789abcdef' for c in freeze_commit):
        raise ValueError('Actual source-freeze Git commit required')
    output.mkdir(parents=True)
    start = time.perf_counter()
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (output/'START.json').write_text(json.dumps({'source_freeze_commit': freeze_commit,
        'source_sha256': source_hash, 'python': sys.version, 'platform': platform.platform(),
        'started_unix': time.time(), 'original_investment': False,
        'scope': 'New exact supporting diagnostic; no population sampling or timing superiority claim.'}, indent=2)+'\n')
    rows = []
    try:
        for lo, hi in itertools.combinations_with_replacement(ENDPOINTS, 2):
            for beta, mu, a0 in itertools.product(BETAS, CURVATURES, CENTERS):
                row = recover(lo, hi, beta, mu, a0)
                row['cell'] = len(rows)
                rows.append(row)
        if len(rows) != 792:
            raise ArithmeticError('Incomplete prespecified catalogue')
        result = {'status': 'executed', 'cells': len(rows), 'rows': rows,
            'source_freeze_commit': freeze_commit, 'source_sha256': source_hash,
            'elapsed_seconds': time.perf_counter()-start,
            'strict_improvements': sum(F(r['regret_reduction']) > 0 for r in rows),
            'equal_regret': sum(F(r['regret_reduction']) == 0 for r in rows),
            'nonzero_width_zero_regret': sum(F(r['width']) > 0 and F(r['worst_regret']) == 0 for r in rows),
            'endpoint_objective_evaluations': sum(r['endpoint_objective_evaluations'] for r in rows),
            'scope': 'All 792 fixed scalar Bellman-interval cells; not new investment or population evidence.'}
        (output/'CATALOGUE118.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
        return {k: v for k, v in result.items() if k != 'rows'}
    except Exception as error:
        (output/'FAILED118.json').write_text(json.dumps({'error': repr(error), 'completed_rows': rows,
            'source_freeze_commit': freeze_commit, 'elapsed_seconds': time.perf_counter()-start}, indent=2)+'\n')
        raise


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--freeze-commit', required=True)
    args = p.parse_args()
    print(json.dumps(run(args.output, args.freeze_commit), indent=2))
