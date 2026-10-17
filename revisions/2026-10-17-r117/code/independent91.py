"""Independent finite-state original-law evaluator for R91.

No risk91 import, optimizer, NumPy, SciPy or binary floating point. Tail risk
is evaluated by the capped-density dual, not support-threshold minimization.
"""
from fractions import Fraction as F


def tail_dual(values, probabilities, alpha):
    values, probabilities, alpha = tuple(map(F, values)), tuple(map(F, probabilities)), F(alpha)
    if not values or len(values) != len(probabilities):
        raise ValueError('Empty or unmatched finite law')
    if not 0 <= alpha < 1 or any(p < 0 for p in probabilities) or sum(probabilities) != 1:
        raise ValueError('Invalid probability law or tail level')
    remaining, answer = F(1), F(0)
    for i in sorted(range(len(values)), key=lambda i: values[i], reverse=True):
        amount = min(remaining, probabilities[i]/(1-alpha))
        answer += amount*values[i]
        remaining -= amount
        if not remaining:
            break
    if remaining:
        raise ArithmeticError('The capped-density constraints could not fill unit mass')
    return answer


def original_values(costs, transitions, terminal, discounts, alpha, policy=None):
    """Separate backward recursion for all states; policy=None computes optimum."""
    if not len(costs) == len(transitions) == len(discounts):
        raise ValueError('Horizon mismatch')
    value = tuple(map(F, terminal)); history = [value]
    for t in range(len(costs)-1, -1, -1):
        if F(discounts[t]) < 0:
            raise ValueError('Negative discount')
        out = []
        for x in range(len(costs[t])):
            choices = range(len(costs[t][x])) if policy is None else (policy[t][x],)
            possible = []
            for a in choices:
                if not 0 <= a < len(costs[t][x]):
                    raise ValueError('Infeasible original action')
                possible.append(F(costs[t][x][a]) + F(discounts[t]) *
                                tail_dual(value, transitions[t][x][a], alpha))
            out.append(min(possible))
        value = tuple(out); history.append(value)
    return tuple(reversed(history))
