"""Exact rational algebra checks of report-origin corrigenda, not experiments."""
from fractions import Fraction as F
from pathlib import Path
import datetime
import hashlib
import json
import time


def run():
    start = time.time()
    checks = []

    def equal(name, observed, expected):
        assert observed == expected, (name, observed, expected)
        checks.append({"name": name, "observed": str(observed),
                       "expected": str(expected), "passed": True})

    eps = F(3, 28)
    # Integral (2-t)^2 dt on [0,1], evaluated coefficient by coefficient.
    residual_square_integral = sum(c / (k + 1)
                                   for k, c in enumerate([F(4), F(-4), F(1)]))
    equal("integrated_residual_coefficient", residual_square_integral, F(7, 3))
    equal("composite_loss_perturbation", -eps / 2 + eps**2 * residual_square_integral,
          F(-3, 112))
    equal("perturbation_preserves_terminal", -eps * (1 - F(1)), F(0))
    equal("stationary_composite_prefers_nonroot", -F(1, 2) + F(1, 2)**2, F(-1, 4))
    mu, rate, gamma, sigma, rho = F(8, 100), F(2, 100), F(2), F(1, 5), F(1, 25)
    portfolio = (mu - rate) / (gamma * sigma**2)
    consumption = (rho + (gamma - 1) *
                   (rate + (mu-rate)**2 / (2*gamma*sigma**2))) / gamma
    equal("stationary_merton_portfolio", portfolio, F(3, 4))
    equal("stationary_merton_consumption", consumption, F(33, 800))
    unconstrained = (F(1, 100)-rate) / (gamma*sigma**2)
    equal("constrained_merton_unconstrained_share", unconstrained, F(-1, 8))
    equal("constrained_merton_projection", max(F(0), unconstrained), F(0))
    gamma, psi = F(5), F(3, 2)
    equal("formal_ez_portfolio", (mu-rate)/(gamma*sigma**2), F(3, 10))
    equal("formal_ez_consumption", psi*rho + (1-psi)*
          (rate+(mu-rate)**2/(2*gamma*sigma**2)), F(91, 2000))
    equal("old_ez_marginal_at_unit_domain", rho*(1-gamma), F(-4, 25))
    equal("corrected_ez_marginal_at_unit_domain", rho, F(1, 25))
    # Gaussian E Z^2 = 1 and E Z^4 = 3 are the analytic moment inputs.
    equal("gaussian_squared_loss_stationary_point", F(1) / F(3, 2), F(2, 3))
    equal("exact_squared_loss_stationary_point", F(1) / F(1, 2), F(2))
    equal("cournot_nash_unilateral_derivative", 1-2*F(1, 3)-F(1, 3), F(0))
    equal("cournot_joint_optimum_unilateral_derivative", 1-2*F(1, 4)-F(1, 4), F(1, 4))
    equal("cournot_joint_optimum_total_output_derivative", 1-2*F(1, 2), F(0))
    source = Path(__file__)
    tex = source.with_name("original_correctness119.tex")
    end = time.time()
    return {"scope": "Non-preregistered exact rational proof diagnostic of the original report's algebra; no policy training, economic experiment, historical rerun, or global verification theorem.",
            "origin": {"report_id": "2026-09-15-econometrica", "author_source_commit": "bf049e302e9ed38303084e8da16b13717b052a70"},
            "started_utc": datetime.datetime.fromtimestamp(start, datetime.timezone.utc).isoformat(),
            "ended_utc": datetime.datetime.fromtimestamp(end, datetime.timezone.utc).isoformat(),
            "elapsed_seconds": end-start,
            "checks": checks, "all_checks_passed": True,
            "script_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "tex_sha256": hashlib.sha256(tex.read_bytes()).hexdigest(),
            "analytical_not_numerically_tested": ["viscosity selection counterexample proof", "Brownian domain exit proof", "infinite-horizon Merton and Epstein-Zin verification", "NDU economic normalization and identification", "temporal-self and dynamic-game existence"]}


if __name__ == "__main__":
    p = Path(__file__).with_name("original_correctness_regression119.json")
    record = run()
    p.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"checks": len(record["checks"]), "passed": True,
                      "artifact": str(p), "elapsed_seconds": record["elapsed_seconds"]}))
