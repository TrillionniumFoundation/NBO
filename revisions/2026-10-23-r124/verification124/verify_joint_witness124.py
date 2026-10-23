#!/usr/bin/env python3
"""Independent exact arithmetic for R124's abstract joint-information witness.

No production certificate, economic integration module, floating optimizer, or
random sample is imported. This is an algebraic validation, not an empirical
investment outcome and not a neural-specific comparison.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path


def affine_integral(slope, intercept, left, right):
    return slope * (right * right - left * left) / 2 + intercept * (right - left)


# The transformed derivative h' has slope in [0,1]. Adding t^2/2-t/2
# gives a C1 objective with derivative slopes in [1,2].
PIECES = (
    (F(0), F(1, 8), F(1), F(0)),
    (F(1, 8), F(5, 8), F(0), F(1, 8)),
    (F(5, 8), F(1), F(1), -F(1, 2)),
)


def transformed_value(t):
    value = F(0)
    for left, right, slope, intercept in PIECES:
        stop = min(t, right)
        if stop > left:
            value += affine_integral(slope, intercept, left, stop)
    return value


def objective(t):
    return transformed_value(t) + t * t / 2 - t / 2


def derivative(t):
    for left, right, slope, intercept in PIECES:
        if left <= t <= right:
            return slope * t + intercept + t - F(1, 2)
    raise AssertionError("outside declared interval")


def quadratic_minimum(pieces):
    candidates = []
    for left, right, c2, c1, c0 in pieces:
        points = [left, right]
        if c2 > 0:
            stationary = -c1 / (2 * c2)
            if left <= stationary <= right:
                points.append(stationary)
        candidates.extend((c2 * x * x + c1 * x + c0, x) for x in points)
    return min(candidates)


def main():
    # Independently verify junctions and the supplied information.
    for (_, right, slope, intercept), (left2, _, slope2, intercept2) in zip(PIECES, PIECES[1:]):
        assert right == left2
        assert slope * right + intercept == slope2 * left2 + intercept2
    assert all(0 <= slope <= 1 for _, _, slope, _ in PIECES)
    assert objective(F(0)) == 0
    assert objective(F(1)) == F(3, 16)
    assert derivative(F(0)) == -F(1, 2)
    assert derivative(F(1)) == 1
    candidate = F(3, 8)
    assert derivative(candidate) == 0
    assert objective(candidate) == -F(5, 64)

    # Exact minimization of the two old upper bounds, separately. The
    # minimum of their pointwise minimum is the lesser of these minima.
    old_from_zero = quadratic_minimum((
        (F(0), F(1, 2), F(1), -F(1, 2), F(0)),
        (F(1, 2), F(1), F(1, 2), F(0), -F(1, 8)),
    ))
    old_from_one = quadratic_minimum((
        (F(0), F(1, 2), F(1, 2), -F(1, 2), F(1, 16)),
        (F(1, 2), F(1), F(1), -F(1), F(3, 16)),
    ))
    assert old_from_zero == (-F(1, 16), F(1, 4))
    assert old_from_one == (-F(1, 16), F(1, 2))

    # A sharp exact dual for the JOINT fixed-candidate interpolation
    # problem. z=h(3/8), v=h'(3/8), objective H=15/128-z.
    z, v = F(5, 128), F(1, 8)
    y1 = y2 = F(1, 2)
    c1 = z - F(3, 8) * v + v * v / 2
    c2 = z - F(1, 16) + F(1, 8) * v + v * v / 2
    lagrangian = F(15, 128) - z + y1 * c1 + y2 * c2
    residual_z = -1 + y1 + y2
    residual_v = y1 * (v - F(3, 8)) + y2 * (v + F(1, 8))
    assert c1 == c2 == residual_z == residual_v == 0
    assert lagrangian == F(5, 64)
    assert transformed_value(candidate) == z
    assert derivative(candidate) - candidate + F(1, 2) == v

    # All adjacent interpolation constraints, including those unused by
    # this sharp dual, are verified independently in rational arithmetic.
    xs = [F(0), candidate, F(1)]
    interpolation = []
    for left, right in zip(xs, xs[1:]):
        d = right - left
        s = derivative(right) - derivative(left) - d
        w = objective(right) - objective(left) - derivative(left) * d - d * d / 2
        lower_slack = 2 * w - s * s
        upper_slack = 2 * (s * d - w) - s * s
        assert 0 <= s <= d
        assert lower_slack >= 0 and upper_slack >= 0
        interpolation.append({"left": str(left), "right": str(right), "s": str(s),
                              "w": str(w), "lower_slack": str(lower_slack),
                              "upper_slack": str(upper_slack)})
    result = {
        "status": "passed-exact-rational-algebra",
        "scope": "abstract scalar smooth-convex information class; no economic sample",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "mu": "1", "L": "2", "A": "1", "incumbent": "0",
        "joint_candidate": str(candidate),
        "old_best_upper_contrast": "-1/16",
        "joint_exact_upper_contrast": "-5/64",
        "certified_gain_increment": str(F(5, 64) - F(1, 16)),
        "endpoint_values": [str(objective(F(0))), str(objective(F(1)))],
        "endpoint_derivatives": [str(derivative(F(0))), str(derivative(F(1)))],
        "dual_multipliers": [str(y1), str(y2)],
        "dual_point_h_value_and_derivative": [str(z), str(v)],
        "dual_residual": [str(residual_z), str(residual_v)],
        "dual_lower_bound_on_negative_contrast": str(lagrangian),
        "interpolation_checks": interpolation,
        "neural_specific_claim": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
