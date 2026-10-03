#!/usr/bin/env python3
"""Independent numerical checks for the NBO R10 referee review.

This script deliberately does not import the manuscript's certificate code. It
reconstructs the stated capital model, coupling matrices, scalar regret
integrals, and selected stress inequalities using NumPy/SciPy only. The
reported outward endpoints are treated as comparison targets, not as inputs to
our calculations.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import quad

T = 1.0
RHO = 0.04
KAPPA = 0.15
SIGMA_I = 0.15
ZETA = 0.2
CHI = 0.03
LOWER = 0.02
UPPER = 2.0
EPSILON = 0.1

REPORTED_BOUNDS = {
    10: {
        0.00: {"anchor": 0.01875, "tube": 0.05743, "comp_pct": 6.04},
        0.25: {"anchor": 0.02152, "tube": 0.06184, "comp_pct": 6.52},
        0.50: {"anchor": 0.02455, "tube": 0.06649, "comp_pct": 7.02},
    },
    20: {
        0.00: {"anchor": 0.02553, "tube": 0.06725, "comp_pct": 7.11},
        0.25: {"anchor": 0.02881, "tube": 0.07219, "comp_pct": 7.65},
        0.50: {"anchor": 0.03235, "tube": 0.07740, "comp_pct": 8.22},
    },
    50: {
        0.00: {"anchor": 0.02754, "tube": 0.07009, "comp_pct": 7.42},
        0.25: {"anchor": 0.03097, "tube": 0.07518, "comp_pct": 7.98},
        0.50: {"anchor": 0.03465, "tube": 0.08054, "comp_pct": 8.57},
    },
}

REPORTED_COST = {
    10: {"schedule_total": 0.113, "actor_total": 5.397,
         "schedule_deploy_ms": 0.053, "actor_deploy_ms": 1.703},
    20: {"schedule_total": 0.115, "actor_total": 5.715,
         "schedule_deploy_ms": 0.058, "actor_deploy_ms": 1.766},
    50: {"schedule_total": 0.129, "actor_total": 6.387,
         "schedule_deploy_ms": 0.054, "actor_deploy_ms": 1.840},
}

ACTOR_MINUS_SCHEDULE = {
    10: 0.0012992443603554134,
    20: -0.001953936999741234,
    50: -0.0006473220386174106,
}


def coupling(dimension: int) -> np.ndarray:
    rng = np.random.default_rng(401 + dimension)
    matrix = rng.normal(size=(dimension, dimension))
    return matrix / np.linalg.norm(matrix, axis=1, keepdims=True)


def w(time: float) -> float:
    discount = math.exp(-RHO * (T - time))
    return (1.0 - discount) / RHO + discount


def schedule(time: float) -> float:
    wt = w(time)
    return 2.0 / (wt + math.sqrt(wt * wt + 4.0 * ZETA))


def curvature(time: float) -> float:
    anchor = schedule(time)
    return 2.0 * (
        math.log(anchor / UPPER) + (UPPER - anchor) / anchor
    ) / (UPPER - anchor) ** 2


def integral_exp_beta(beta: float) -> float:
    return math.expm1(beta * T) / beta


def independent_certificate(dimension: int, spread: float) -> dict[str, float]:
    matrix = coupling(dimension)
    spectral_norm = float(np.linalg.norm(matrix, 2))
    beta = KAPPA * spectral_norm
    q_d = spread + KAPPA * T + SIGMA_I * math.sqrt((1.0 - 1.0 / dimension) * T)

    def kernel(time: float) -> float:
        nested, _ = quad(
            lambda future: math.exp(-RHO * future)
            * w(future)
            * math.exp(beta * (future - time)),
            time,
            T,
            epsabs=1e-12,
            epsrel=1e-12,
            limit=200,
        )
        return (
            beta * nested
            + 2.0 * CHI * math.exp(-RHO * T) * q_d
            * math.exp(beta * (T - time))
        )

    anchor, _ = quad(
        lambda time: 0.5 * math.exp(RHO * time)
        * kernel(time) ** 2 / curvature(time),
        0.0,
        T,
        epsabs=2e-11,
        epsrel=2e-11,
        limit=200,
    )
    tube_loss, _ = quad(
        lambda time: EPSILON * kernel(time)
        + 0.5 * EPSILON**2 * math.exp(-RHO * time)
        * ((schedule(time) - EPSILON) ** -2 + ZETA),
        0.0,
        T,
        epsabs=2e-11,
        epsrel=2e-11,
        limit=200,
    )
    tube_loss += (
        CHI * math.exp(-RHO * T) * EPSILON**2
        * integral_exp_beta(beta) ** 2
    )
    total = anchor + tube_loss
    compensation = 100.0 * (
        math.exp(RHO * total / (1.0 - math.exp(-RHO * T))) - 1.0
    )
    return {
        "spectral_norm": spectral_norm,
        "beta": beta,
        "anchor": anchor,
        "tube_loss_allowance": tube_loss,
        "tube": total,
        "comp_pct": compensation,
    }


def inequality_stress(samples: int = 300_000) -> dict[str, Any]:
    rng = np.random.default_rng(20261004)
    times = rng.random(samples)
    anchors = np.array([schedule(float(t)) for t in times])
    actions = LOWER + (UPPER - LOWER) * rng.random(samples)
    mus = 2.0 * (
        np.log(anchors / UPPER) + (UPPER - anchors) / anchors
    ) / (UPPER - anchors) ** 2
    global_residual = (
        np.log(actions / anchors) - (actions - anchors) / anchors
        + 0.5 * mus * (actions - anchors) ** 2
    )

    perturbations = EPSILON * (2.0 * rng.random(samples) - 1.0)
    local_remainder = (
        perturbations / anchors - np.log1p(perturbations / anchors)
    )
    local_upper = perturbations**2 / (2.0 * (anchors - EPSILON) ** 2)

    return {
        "samples": samples,
        "schedule_min": float(anchors.min()),
        "schedule_max": float(anchors.max()),
        "maximum_global_tangent_inequality_residual": float(global_residual.max()),
        "maximum_local_tube_inequality_residual": float((local_remainder - local_upper).max()),
        "global_tangent_inequality_passed": bool(global_residual.max() <= 1e-11),
        "local_tube_inequality_passed": bool((local_remainder - local_upper).max() <= 1e-11),
    }


def build_results() -> dict[str, Any]:
    certificate_rows: list[dict[str, Any]] = []
    for dimension in (10, 20, 50):
        for spread in (0.0, 0.25, 0.5):
            calculated = independent_certificate(dimension, spread)
            reported = REPORTED_BOUNDS[dimension][spread]
            certificate_rows.append({
                "dimension": dimension,
                "initial_std_upper": spread,
                "independent": calculated,
                "reported_outward_table": reported,
                "reported_anchor_is_above_independent_value": reported["anchor"] >= calculated["anchor"],
                "reported_tube_is_above_independent_value": reported["tube"] >= calculated["tube"],
                "reported_compensation_is_above_independent_value": reported["comp_pct"] >= calculated["comp_pct"],
                "anchor_rounding_slack": reported["anchor"] - calculated["anchor"],
                "tube_rounding_slack": reported["tube"] - calculated["tube"],
                "compensation_rounding_slack_pct": reported["comp_pct"] - calculated["comp_pct"],
            })

    method_contribution: list[dict[str, Any]] = []
    for dimension in (10, 20, 50):
        baseline = independent_certificate(dimension, 0.0)
        cost = REPORTED_COST[dimension]
        measured = ACTOR_MINUS_SCHEDULE[dimension]
        method_contribution.append({
            "dimension": dimension,
            "actor_minus_schedule_payoff": measured,
            "actor_improved_on_schedule_in_reported_paired_simulation": measured > 0.0,
            "tube_bound_to_anchor_bound_ratio": baseline["tube"] / baseline["anchor"],
            "tube_allowance": baseline["tube_loss_allowance"],
            "positive_actor_gain_as_fraction_of_tube_allowance": (
                measured / baseline["tube_loss_allowance"] if measured > 0 else None
            ),
            "actor_total_cost_to_schedule_total_cost_ratio": cost["actor_total"] / cost["schedule_total"],
            "actor_deployment_to_schedule_deployment_ratio": cost["actor_deploy_ms"] / cost["schedule_deploy_ms"],
        })

    all_bounds_dominate = all(
        row["reported_anchor_is_above_independent_value"]
        and row["reported_tube_is_above_independent_value"]
        and row["reported_compensation_is_above_independent_value"]
        for row in certificate_rows
    )

    return {
        "schema_version": 1,
        "purpose": "Independent referee reconstruction of R10 scalar certificate arithmetic and contribution diagnostics",
        "reviewed_commit": "8ded2629289c4633141b9fac1aa9b41a8c1595af",
        "independence": {
            "imports_manuscript_certificate_code": False,
            "uses_saved_neural_weights": False,
            "uses_reported_outward_endpoints_as_calculation_inputs": False,
            "numerical_stack": "NumPy plus SciPy adaptive quadrature",
        },
        "inequality_stress": inequality_stress(),
        "certificate_rows": certificate_rows,
        "all_reported_outward_endpoints_dominate_independent_values": all_bounds_dominate,
        "method_contribution_diagnostics": method_contribution,
        "summary": {
            "certificate_arithmetic_reconstructed": all_bounds_dominate,
            "dimensions_with_positive_reported_actor_minus_schedule_payoff": [
                d for d, value in ACTOR_MINUS_SCHEDULE.items() if value > 0.0
            ],
            "dimensions_with_nonpositive_reported_actor_minus_schedule_payoff": [
                d for d, value in ACTOR_MINUS_SCHEDULE.items() if value <= 0.0
            ],
            "interpretation": (
                "The continuous-time bound and printed outward endpoints are numerically corroborated. "
                "The bound is architectural: the untrained schedule has the tighter guarantee and the "
                "reported actor improves on that schedule only in dimension 10."
            ),
        },
        "limitations": [
            "This is not a formal verification of the repository's outward binary64 implementation.",
            "It does not independently retrain the neural policies or replay binary weight files.",
            "It does not remove Euler bias from the manuscript's paired payoff comparisons.",
            "It checks selected theorem inequalities by randomized stress rather than proving them.",
        ],
    }


def main() -> None:
    result = build_results()
    output = Path(__file__).with_name("independent_results.json")
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result["summary"], indent=2))
    if not result["all_reported_outward_endpoints_dominate_independent_values"]:
        raise SystemExit("reported endpoint did not dominate independent calculation")
    if not result["inequality_stress"]["global_tangent_inequality_passed"]:
        raise SystemExit("global tangent inequality stress failed")
    if not result["inequality_stress"]["local_tube_inequality_passed"]:
        raise SystemExit("local tube inequality stress failed")


if __name__ == "__main__":
    main()
