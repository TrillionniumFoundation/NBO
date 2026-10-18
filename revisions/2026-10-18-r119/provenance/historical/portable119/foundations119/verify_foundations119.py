#!/usr/bin/env python3
"""Exact arithmetic checks supporting the displayed primitive algebra.

This is not a sample-based experiment or an economic performance result.
Multiaffinity and the derivative signs in the proof reduce the transition
range on the outer state/action/shock box to these exact vertex values.
All feasible state-action pairs belong to this outer box.  The other
checks are exact inequalities between the derived uniform constants.
"""

from fractions import Fraction as F
from itertools import product
import json


def ratio(value):
    return str(value)


def main():
    beta = F(15, 16)
    radius = F(1, 32)
    cap_min, cap_max = F(1, 8), F(1, 4)

    # Original F_j: p=x_j, q=x_{j+1}; parity changes b and shock sign.
    extrema = []
    for b, shock_sign in ((F(1, 2), 1), (F(1, 4), -1)):
        values = [
            F(1, 16) + p / 2 + q / 8 + p * (1 - q) / 16
            + b * a + shock_sign * z
            for p, q, a, z in product(
                (F(0), F(1)), (F(0), F(1)),
                (F(0), cap_max), (-radius, radius)
            )
        ]
        extrema.append((min(values), max(values)))

    # Both state derivatives are nonnegative throughout [0,1]^2.
    dp_min = min(F(1, 2) + (1 - q) / 16 for q in (F(0), F(1)))
    dq_min = min(F(1, 8) - p / 16 for p in (F(0), F(1)))
    assert dp_min > 0 and dq_min > 0
    assert extrema == [(F(1, 32), F(27, 32)), (F(1, 32), F(25, 32))]
    assert min(v[0] for v in extrema) > 0
    assert max(v[1] for v in extrema) < 1

    # Cost bounds are dimension independent after their stated normalization.
    target = 2 * F(5, 8) ** 2
    cycle = F(1, 4)
    shortage = 2 * F(1, 2) ** 2
    state_bound = target + cycle + shortage
    terminal_bound = state_bound + target
    action_bound = cap_max ** 2 + 4 * cap_max ** 4
    assert (state_bound, terminal_bound, action_bound) == (
        F(49, 32), F(37, 16), F(5, 64)
    )
    assert state_bound + action_bound == F(103, 64)

    # d times the state curvature, hence also innovation-direction curvature
    # because ||s||_2^2=d in the original alternating-shock model.
    state_curvature_times_d = 4 - beta * F(5, 4)
    assert state_curvature_times_d == F(181, 64) > 0
    action_curvature = F(2)
    column_sum = F(9, 16) + F(1, 8)
    fixed_action_modulus_times_d = 8 + beta * column_sum * 10
    value_modulus_times_d = F(15, 2) + beta * (F(55, 8) + F(15, 32))
    assert fixed_action_modulus_times_d < 15
    assert value_modulus_times_d < 15

    # Downward observation preserves the affine capacity.  The action selected
    # at the observed state has the same fixed-action value evaluated at x.
    observed_gap = F(1, 2 ** 21)
    observation_allowance = 30 * F(1, 2 ** 40)
    certified_terminal_gap = observed_gap + observation_allowance
    epsilon_one = F(1, 2 ** 20)
    assert certified_terminal_gap < epsilon_one

    result = {
        "status": "passed",
        "scope": "exact primitive algebra; not a performance experiment",
        "arithmetic": "Python fractions.Fraction only",
        "transition_vertex_count": 32,
        "transition_ranges_by_parity": [[ratio(a), ratio(b)] for a, b in extrema],
        "minimum_state_partial_derivatives": [ratio(dp_min), ratio(dq_min)],
        "capacity_interval": [ratio(cap_min), ratio(cap_max)],
        "state_cost_upper": ratio(state_bound),
        "terminal_cost_upper": ratio(terminal_bound),
        "stage_cost_upper": ratio(state_bound + action_bound),
        "state_curvature_times_dimension": ratio(state_curvature_times_d),
        "innovation_curvature": ratio(state_curvature_times_d),
        "action_curvature": ratio(action_curvature),
        "fixed_action_lipschitz_times_dimension": ratio(fixed_action_modulus_times_d),
        "value_lipschitz_times_dimension": ratio(value_modulus_times_d),
        "terminal_policy_gap_upper": ratio(certified_terminal_gap),
        "terminal_policy_allowance": ratio(epsilon_one),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
