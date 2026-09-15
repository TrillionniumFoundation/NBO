#!/usr/bin/env python3
"""Deterministic checks supporting the NBO review, not NBO experiment replication.

Run with Python 3.9+ and the standard library only:
    python3 verify_counterexamples.py --output verification_results.json
Optional --source-root /path/to/NBO verifies the pinned manuscript blobs and
extracts the constrained-portfolio data from ECTA.tex. The default run uses
explicitly transcribed manuscript inputs; it does not download or train anything.
A successful check means that the REVIEWER'S diagnostic was reproduced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any

BASE_COMMIT = "bf049e302e9ed38303084e8da16b13717b052a70"
SOURCE_BLOBS = {
    "ECTA.tex": "2278f19fb009911d810d420722d75a298dd84096",
    "supp.tex": "9ba390ec3b4f34f69a11de9db9201e60b4e6ba76",
}
# ECTA.tex, both embedded viscosity_policy.dat definitions, lines 38-90.
PORTFOLIO_DATA = [
    (0.10, 0.513236), (0.59, 0.363228), (1.08, 0.487027),
    (1.57, 0.534042), (2.06, 0.560213), (2.55, 0.577754),
    (3.04, 0.589967), (3.53, 0.598285), (4.02, 0.603704),
    (4.51, 0.607018), (5.00, 0.608903),
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def close(actual: float, expected: float) -> bool:
    return math.isclose(actual, expected, rel_tol=1e-11, abs_tol=1e-12)


def source_audit(root: Path | None) -> dict[str, Any]:
    if root is None:
        return {"mode": "transcribed_inputs", "local_source_hashes_checked": False}
    hashes: dict[str, str] = {}
    for name, expected in SOURCE_BLOBS.items():
        data = (root / name).read_bytes()
        digest = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(digest == expected, f"{name}: expected pinned blob {expected}, found {digest}")
        hashes[name] = digest
    text = (root / "ECTA.tex").read_text(encoding="utf-8")
    blocks = re.findall(
        r"\\begin\{filecontents\*\}\{viscosity_policy\.dat\}(.*?)\\end\{filecontents\*\}",
        text, flags=re.S,
    )
    require(len(blocks) == 2, "Expected two viscosity_policy.dat definitions")
    for block in blocks:
        rows = [tuple(map(float, row.split())) for row in block.strip().splitlines()[1:]]
        require(rows == PORTFOLIO_DATA, "Constrained-portfolio data differ from transcription")
    return {"mode": "pinned_local_sources", "local_source_hashes_checked": True,
            "git_blob_sha1": hashes, "matching_plot_definitions": len(blocks)}


def run_checks() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    def record(name: str, finding: str, passed: bool, **values: Any) -> None:
        require(passed, f"Reviewer diagnostic failed: {name}")
        out.append({"check": name, "finding": finding, "diagnostic_reproduced": True, **values})

    eps = 3.0 / 28.0
    delta = -eps / 2.0 + 7.0 * eps**2 / 3.0
    record("finite_horizon_hard_terminal_counterexample", "R1",
           close(delta, -3.0 / 112.0) and delta < 0,
           epsilon=eps, correct_solution_loss=1-math.exp(-1),
           perturbation_loss_change=delta, terminal_value_both=1.0,
           formula="V*=exp(t-1); V_epsilon=V*-epsilon*(1-t); R_epsilon=-epsilon*(2-t)")

    q, rho, omega = 1.0, 1.0, 1.0
    h = 1.0 / (2.0 * omega)
    biased_value = (q-h)/rho
    record("stationary_composite_loss_bias", "R1",
           close(biased_value, 0.5) and close(-h+omega*h*h, -0.25),
           true_value=q/rho, minimizing_value=biased_value,
           hamiltonian_at_minimum=h, minimum_loss=-h+omega*h*h)

    rows = []
    for e in (0.1, 0.01, 0.001, 0.0001):
        # Uniform probability on [-1,1]; symmetry removes the factor 1/2.
        mean_r2 = 2-2*math.sqrt(1+e*e)+2*e-e*math.atan(1/e)
        rows.append({"epsilon": e, "mean_squared_residual": mean_r2,
                     "value_error_at_zero": math.sqrt(1+e*e)-e+1})
    record("wrong_viscosity_limit_with_vanishing_L2_residual", "R3",
           all(a["mean_squared_residual"] > b["mean_squared_residual"] > 0
               for a, b in zip(rows, rows[1:])) and rows[-1]["value_error_at_zero"] > 1.99,
           sequence=rows, wrong_limit_test_function_F=1.0,
           formula="F(p)=1-|p|; V*=|x|-1; W_epsilon=sqrt(1+epsilon^2)-sqrt(x^2+epsilon^2)")

    rho, gamma, mu, rate, sigma = 0.04, 2.0, 0.08, 0.02, 0.2
    pi = (mu-rate)/(gamma*sigma*sigma)
    m = (rho+(gamma-1)*(rate+(mu-rate)**2/(2*gamma*sigma*sigma)))/gamma
    record("merton_unconstrained_arithmetic", "R4", close(pi, .75) and close(m, .04125),
           correct_portfolio=pi, manuscript_portfolio=.5,
           stationary_consumption_ratio=m, manuscript_constant_ratio=.03,
           caveat="Consumption formula is for the stationary infinite-horizon interpretation, not an unspecified finite-horizon terminal problem.")

    unconstrained_pi = (0.01-0.02)/(2.0*0.2**2)
    record("merton_constrained_arithmetic", "R4", close(unconstrained_pi, -.125),
           correct_unconstrained_portfolio=unconstrained_pi,
           manuscript_unconstrained_portfolio=-.25, constrained_portfolio_all_positive_wealth=0.0)

    values = [p for _, p in PORTFOLIO_DATA]
    count = sum(-.05 <= p <= .1 for p in values)
    record("constrained_plot_source_range", "R5", count == 0 and len(values) == 11,
           number_of_points=len(values), points_inside_declared_y_limits=count,
           y_limits=[-.05, .1], minimum=min(values), maximum=max(values),
           caveat="Source-level range check; not inspection of a compiled PDF.")

    gamma, psi, rho = 5.0, 1.5, .04
    b, a, c, v = 1-gamma, 1-1/psi, 1.0, -.25
    fc = rho*b*c**(a-1)*(b*v)**(1-a/b)
    candidate_m = psi*rho+(1-psi)*(.02+(.08-.02)**2/(2*gamma*.2**2))
    record("epstein_zin_aggregator_sign", "R6", close(fc, -.16) and close(candidate_m, .0455),
           manuscript_f_c=fc, hamiltonian_c_derivative_with_Vx_one=fc-1,
           conventional_difference_form_stationary_candidate=candidate_m,
           caveat="The conventional candidate is algebraic; no claim of infinite-horizon verification for these parameters.")

    c, u = 2.0, 2.0
    derivative = c**(1-u)*(1-(1-u)*math.log(c))/(1-u)**2
    record("endogenous_CRRA_parameter_derivative", "R8", derivative > 0,
           consumption=c, risk_aversion=u, derivative_wrt_risk_aversion=derivative,
           caveat="Derivative of flow utility, not a theorem about the endogenous value derivative V_u.")

    beta, gamma, vx = .7, 2.0, 1.0
    consumption = (beta/vx)**(1/gamma)
    record("present_bias_fixed_shadow_price_margin", "R9", consumption < 1,
           beta=beta, gamma=gamma, fixed_Vx=vx, consumption=consumption,
           beta_one_consumption=1.0, caveat="Holds the shadow price fixed; not a full equilibrium comparative static.")

    q_nash, q_joint = 1/3, 1/4
    unilateral_derivative = 1-2*q_joint-q_joint
    record("cournot_joint_objective_is_not_nash", "R10",
           close(unilateral_derivative, .25) and q_joint != q_nash,
           nash_quantity_each=q_nash, joint_profit_maximizer_quantity_each=q_joint,
           own_payoff_derivative_at_joint_maximum=unilateral_derivative)

    h_true, h_noisy = 2.0, 2.0/3.0
    risk = lambda curvature: 1-curvature+.75*curvature*curvature
    record("squared_unbiased_trace_changes_objective", "R12",
           risk(h_noisy) < risk(h_true) and close(risk(h_noisy), 2/3),
           true_residual_minimizing_curvature=h_true,
           gaussian_one_probe_expected_loss_minimizer=h_noisy,
           noisy_loss_at_true_curvature=risk(h_true), minimum_expected_noisy_loss=risk(h_noisy),
           formula="E[(1-h*z^2/2)^2]=1-h+3*h^2/4 for z~N(0,1)")

    delta, derivative_delta = 1.0, -1.0
    record("TD_squared_loss_gradient_sign", "R7",
           delta*derivative_delta == -1 and -delta*derivative_delta == 1,
           correct_gradient=delta*derivative_delta,
           manuscript_signed_expression=-delta*derivative_delta)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write JSON results to this path")
    parser.add_argument("--source-root", type=Path, help="Optional checkout of the pinned NBO revision")
    args = parser.parse_args()
    try:
        source = source_audit(args.source_root)
        checks = run_checks()
        result = {"reviewed_commit": BASE_COMMIT,
                  "purpose": "Reviewer counterexample and arithmetic verification; not author experiment replication",
                  "source_validation": source,
                  "checks_total": len(checks),
                  "all_reviewer_diagnostics_reproduced": True, "checks": checks}
        rendered = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 0
    except (OSError, ValueError, ArithmeticError) as exc:
        parser.exit(1, f"Verification failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
