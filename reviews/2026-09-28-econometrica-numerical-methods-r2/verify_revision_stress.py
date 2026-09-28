#!/usr/bin/env python3
"""Independent NDU action-set stress test for the NBO R2 referee review.

This script preserves the R2 state/time grid, Brownian cubature, reflection,
wealth stopping rule, terminal payoff, model parameters, and interpolation.
It changes only the finite action set to test whether the published 27-action
reference is robust to action-domain expansion.

It is a reviewer diagnostic, not an alternative estimate of the continuous-
action optimum.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.interpolate import RegularGridInterpolator


ROOT = Path(__file__).resolve().parents[3]

EXPECTED_SHA256 = {
    "ECTA.tex": "6e848362e29221e620719ce8ca38ba02663e8964f139e2ca361faa242aefac53",
    "supp.tex": "0ffa810ad1cb079b4d81f26b8cdcb2629f05116183c65eee772b5b90bce5f92d",
    "revisions/2026-09-28/code/experiments.py":
        "5b8a26f7c0ff7b8d8812cf3ee56b18d766ed5233bd3dd706ab13b23f1d01ca43",
    "revisions/2026-09-28/code/nbo_core.py":
        "abba09e93bea3b2847e9841512fbdc45987483962b677c39f68a89439b915b87",
    "revisions/2026-09-28/code/test_revision.py":
        "023fc388b17118600e5fa2f0f16c466127f291e119cfe6862c3b04cce3aed33e",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def action_product(consumption: list[float], portfolio: list[float],
                   adjustment: list[float]) -> np.ndarray:
    return np.array(
        np.meshgrid(consumption, portfolio, adjustment, indexing="ij")
    ).reshape(3, -1).T


ACTION_SETS = {
    "baseline_27": action_product(
        [0.02, 0.05, 0.10],
        [0.0, 0.375, 0.75],
        [-0.15, 0.0, 0.15],
    ),
    "expanded_theta_63": action_product(
        [0.02, 0.05, 0.10],
        [0.0, 0.375, 0.75],
        [-0.45, -0.30, -0.15, 0.0, 0.15, 0.30, 0.45],
    ),
    "expanded_all_175": action_product(
        [0.02, 0.05, 0.10, 0.20, 0.30],
        [0.0, 0.375, 0.75, 1.125, 1.50],
        [-0.45, -0.30, -0.15, 0.0, 0.15, 0.30, 0.45],
    ),
}


def solve_reference(actions: np.ndarray, *, cost: float, nu: int, nx: int,
                    steps: int) -> dict:
    """Repeat the R2 positive-weight NDU scheme with a supplied action set."""
    us = np.linspace(1.2, 3.0, nu)
    ys = np.linspace(math.log(0.5), math.log(2.0), nx)
    U, Y = np.meshgrid(us, ys, indexing="ij")
    X = np.exp(Y)
    points = np.column_stack([U.ravel(), Y.ravel()])
    dt = 1.0 / steps

    r, mu, sigma, sigma_u, corr, rho = 0.02, 0.08, 0.2, 0.08, -0.3, 0.04

    def terminal(u: np.ndarray, y: np.ndarray) -> np.ndarray:
        return np.exp((1.0 - u) * y) / (1.0 - u)

    def reflect(u: np.ndarray) -> np.ndarray:
        length = us[-1] - us[0]
        z = (u - us[0]) % (2.0 * length)
        return us[0] + np.where(z <= length, z, 2.0 * length - z)

    value = terminal(U, Y)
    first_policy = None

    for _ in range(steps - 1, -1, -1):
        interp = RegularGridInterpolator((us, ys), value, bounds_error=True)
        q_values = []

        for m, p, theta in actions:
            expected = np.zeros(U.size)
            directions = (
                (math.sqrt(2.0), 0.0),
                (-math.sqrt(2.0), 0.0),
                (0.0, math.sqrt(2.0)),
                (0.0, -math.sqrt(2.0)),
            )
            for z1, z2 in directions:
                up = reflect(
                    points[:, 0] + theta * dt + sigma_u * math.sqrt(dt) * z1
                )
                yp = (
                    points[:, 1]
                    + (
                        r
                        + p * (mu - r)
                        - m
                        - 0.5 * p * p * sigma * sigma
                    ) * dt
                    + p * sigma * math.sqrt(dt)
                    * (corr * z1 + math.sqrt(1.0 - corr * corr) * z2)
                )
                outside = (yp < ys[0]) | (yp > ys[-1])
                yp = np.clip(yp, ys[0], ys[-1])
                continuation = interp(np.column_stack([up, yp]))
                continuation[outside] = terminal(up[outside], yp[outside])
                expected += continuation / 4.0

            reward = (
                (m * X.ravel()) ** (1.0 - U.ravel())
                / (1.0 - U.ravel())
                - 0.5 * cost * theta * theta
            )
            q_values.append(dt * reward + math.exp(-rho * dt) * expected)

        q_values_array = np.asarray(q_values)
        choice = np.argmax(q_values_array, axis=0)
        value = np.max(q_values_array, axis=0).reshape(U.shape)
        first_policy = actions[choice].reshape(*U.shape, 3)

        # Preserve the R2 wealth stopping boundary at every time level.
        value[:, 0] = terminal(U[:, 0], Y[:, 0])
        value[:, -1] = terminal(U[:, -1], Y[:, -1])

    i, j = nu // 2, nx // 2
    policy = first_policy[i, j]
    upper_hits = [
        bool(np.isclose(policy[0], actions[:, 0].max())),
        bool(np.isclose(policy[1], actions[:, 1].max())),
        bool(np.isclose(policy[2], actions[:, 2].max())),
    ]
    lower_hits = [
        bool(np.isclose(policy[0], actions[:, 0].min())),
        bool(np.isclose(policy[1], actions[:, 1].min())),
        bool(np.isclose(policy[2], actions[:, 2].min())),
    ]

    return {
        "grid": [nu, nx],
        "steps": steps,
        "cost": cost,
        "number_of_actions": int(len(actions)),
        "center_u": float(us[i]),
        "center_wealth": float(math.exp(ys[j])),
        "center_value": float(value[i, j]),
        "center_action": [float(x) for x in policy],
        "center_action_hits_upper_bound": upper_hits,
        "center_action_hits_lower_bound": lower_hits,
        "interpretation": (
            "Finite-action sensitivity diagnostic; not a continuous-action optimum."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("verification_results.json"),
    )
    args = parser.parse_args()

    identities = {}
    for relative, expected in EXPECTED_SHA256.items():
        actual = sha256(ROOT / relative)
        identities[relative] = {
            "expected_sha256": expected,
            "actual_sha256": actual,
            "matched": actual == expected,
        }

    runs = []
    for nu, nx, steps in ((17, 25, 20), (25, 37, 40)):
        for cost in (1.0, 5.0):
            for name, actions in ACTION_SETS.items():
                result = solve_reference(
                    actions, cost=cost, nu=nu, nx=nx, steps=steps
                )
                result["action_set"] = name
                runs.append(result)

    result = {
        "schema_version": 1,
        "reviewed_commit": "d9054ab6284369ccd6134286e9d2694e3621d562",
        "source_identity": identities,
        "all_source_identities_matched": all(
            item["matched"] for item in identities.values()
        ),
        "diagnostic": "NDU finite-action-domain sensitivity",
        "fixed_elements": [
            "state grids",
            "time grids",
            "model parameters",
            "utility and adjustment cost",
            "Brownian cubature",
            "reflection rule",
            "wealth stopping rule",
            "terminal payoff",
            "interpolation",
        ],
        "changed_element": "finite action set only",
        "runs": runs,
        "conclusion": (
            "The published 27-action reference selects all three upper/lower "
            "action-grid endpoints at the center and changes materially under "
            "action-set expansion. The diagnostic does not identify the true "
            "continuous-action optimum; it establishes that action truncation "
            "is binding and unquantified in the reported reference."
        ),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
