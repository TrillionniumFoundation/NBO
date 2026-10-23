#!/usr/bin/env python3
"""Pre-freeze exact implementation crosscheck on abstract fixed quadratics.

No original economic state, random sample, actor, or outcome is evaluated.
The source hash binds the reviewed implementation snapshot.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import time

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / '2026-10-22-r123/code123'))
sys.path.insert(0, str(BASE / '2026-10-23-r124/code124'))
import joint124
import envelope123
from common124 import serial
from verify124 import RationalCertificate, checked_dual


def main():
    tick = time.perf_counter()
    q = lambda t: F(3, 2) * t * t - t + 2
    g = lambda t: 3 * t - 1
    payloads = []
    for a in (F(0), F(3, 4), F(3, 4)):
        payloads.append(dict(a=a, W=q(a)-F(1, 16), U=q(a)+F(1, 16),
                             p_lower=g(a), p_upper=g(a),
                             g_lower=g(a)-F(1, 8), g_upper=g(a)+F(1, 8)))
    cases = []
    for origin, target in ((F(1, 4), F(5, 8)), (F(0), F(1)), (F(1), F(0))):
        case = envelope123.normalize(dict(A=F(1), incumbent=origin,
            mu=F(1), L=F(4), delta=F(1, 100), tau=F(10), omega=F(10),
            old_optimum_lower=F(0), payloads=payloads))
        problem = joint124.problem(case, target)
        n = len(problem['nodes'])
        original = [q(t) for t in problem['nodes']] + [g(t) for t in problem['nodes']]
        assert all(lo <= z <= hi for lo, z, hi in zip(problem['lower'], original, problem['upper']))
        assert all(c <= 0 for c, _ in joint124.exact_constraints(problem, original))
        # Deliberately infeasible tangent point: validity must not depend on
        # the optimizer's feasibility or on where the tangent is taken.
        proposed = [v + F((-1)**i * (i+1), 7) for i, v in enumerate(original)]
        constraints = joint124.exact_constraints(problem, proposed)
        step = F(1, 11)
        gradient_checks = 0
        for index, (_, grad) in enumerate(constraints):
            for coordinate in range(2*n):
                plus, minus = list(proposed), list(proposed)
                plus[coordinate] += step
                minus[coordinate] -= step
                derivative = (joint124.exact_constraints(problem, plus)[index][0]
                            - joint124.exact_constraints(problem, minus)[index][0]) / (2*step)
                assert derivative == grad[coordinate]
                gradient_checks += 1
        multipliers = [F(i % 5, 13) for i in range(len(constraints))]
        dual = joint124.exact_bound(problem, proposed, multipliers)
        actual = q(target) - q(origin)
        assert dual['contrast_upper'] >= actual
        record = dict(problem=problem, point=proposed, multipliers=multipliers, dual=dual)
        independently_checked = checked_dual(RationalCertificate(case), target, serial(record))
        assert independently_checked == dual['contrast_upper']
        cases.append(dict(origin=str(origin), target=str(target), nodes=n,
                          exact_gradient_checks=gradient_checks,
                          true_contrast=str(actual), certified_upper=str(independently_checked),
                          deliberately_infeasible_tangent=True,
                          noisy_value_and_derivative_intervals=True,
                          duplicate_anchor_preserved=True))
    paths = [BASE/'2026-10-23-r124/code124'/name for name in
             ('joint124.py','service124.py','verify124.py','fixture124.py')]
    result = dict(status='passed-exact-abstract-code-crosscheck',
                  economic_states_evaluated=0, random_states_drawn=0,
                  source_sha256={str(p.relative_to(BASE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                  checks=cases, seconds=time.perf_counter()-tick)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
