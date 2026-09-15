#!/usr/bin/env python3
"""Deterministic R3 audit runs for the NBO revision.

The script intentionally uses small, transparent reference solvers instead of
claiming that a neural training run occurred.  Each run is deterministic,
records its complete configuration, and writes a content digest for the raw
payload used to form the JSONL result record.  The audits cover:

* a bounded two-state NDU dynamic program (coarse versus fine grid);
* a sophisticated temporal-self dynamic program (beta=.7 and beta=1);
* the two-firm Cournot Nash condition and unilateral exploitability;
* the corrected Epstein--Zin stationary algebraic target;
* exact versus Hutchinson diffusion traces at several probe counts; and
* a genuinely coupled quadratic resource benchmark at several dimensions.

No historical TeX arrays are read by this program.  The output is therefore a
reproducible audit artifact, not a reconstruction of an unavailable historical
neural training log.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def code_commit(override: str | None) -> str:
    if override:
        return override
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "working-tree"


def ffloat(x: float) -> float:
    """Convert numpy scalar and reject non-finite values before serialization."""
    x = float(x)
    if not math.isfinite(x):
        raise ValueError(f"non-finite diagnostic value: {x}")
    return x


def result_record(
    run_id: str,
    model: str,
    seed: int,
    config: Dict[str, Any],
    commit: str,
    metrics: Dict[str, float | None],
    raw: Dict[str, Any],
    *,
    domain: Dict[str, Any] | None = None,
    horizon_boundary: Dict[str, Any] | None = None,
    optimizer: Dict[str, Any] | None = None,
    hessian: Dict[str, Any] | None = None,
    stopping: Dict[str, Any] | None = None,
    held_out_distribution: str = "deterministic reference grid",
    notes: str,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    raw_payload = {"run_id": run_id, "model": model, "seed": seed,
                   "config": config, "raw": raw}
    raw_digest = sha256_obj(raw_payload)
    record = {
        "run_id": run_id,
        "model": model,
        "seed": int(seed),
        "config_sha256": sha256_obj(config),
        "code_commit": commit,
        "status": "success",
        "domain": domain or {},
        "horizon_boundary": horizon_boundary or {},
        "optimizer": optimizer or {},
        "hessian": hessian or {},
        "stopping": stopping or {},
        "held_out_distribution": held_out_distribution,
        "metrics": metrics,
        "raw_output_sha256": raw_digest,
        "notes": notes,
    }
    return record, {**raw_payload, "raw_output_sha256": raw_digest}


# ---------------------------------------------------------------------------
# Corrected Merton analytical anchor and no-short feasibility check.

def run_merton(seed: int, commit: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    rho, gamma, mu, r, sigma = 0.04, 2.0, 0.08, 0.02, 0.20
    pi = (mu - r) / (gamma * sigma**2)
    m = (rho + (gamma - 1.0) * (r + (mu - r)**2 / (2.0 * gamma * sigma**2))) / gamma
    unconstrained_no_short = (0.01 - 0.02) / (gamma * sigma**2)
    constrained_no_short = max(0.0, unconstrained_no_short)
    config = {"model": "merton_stationary", "params": {"rho": rho, "gamma": gamma,
              "mu": mu, "r": r, "sigma": sigma},
              "interpretation": "stationary infinite horizon",
              "no_short_check": {"mu": 0.01, "r": 0.02, "constraint": "pi>=0"}}
    raw = {"pi_target": pi, "c_over_x_target": m,
           "no_short_unconstrained": unconstrained_no_short,
           "no_short_constrained": constrained_no_short,
           "target_check": {"pi": abs(pi - 0.75) < 1e-14, "c_over_x": abs(m - 0.04125) < 1e-14}}
    rec, payload = result_record(
        "r3-merton-analytical", "merton_stationary_anchor", seed, config, commit,
        {"value_error": 0.0, "policy_error": 0.0, "boundary_error": 0.0,
         "residual_mean": 0.0, "improvement_gap": 0.0, "exploitability": None}, raw,
        domain={"wealth": ">0", "portfolio": "R; no-short audit pi>=0"},
        horizon_boundary={"interpretation": "stationary infinite horizon; no terminal payoff"},
        optimizer={"method": "closed_form_anchor"}, stopping={"criterion": "analytic"},
        notes="Corrected Merton stationary target and no-short feasibility audit; analytical anchor, not a neural training run.")
    return rec, payload


# ---------------------------------------------------------------------------
# NDU: bounded, projected two-state dynamic program


def ndu_value_grid(nu: int, nx: int, nc: int, nt: int) -> Dict[str, Any]:
    u_grid = np.linspace(1.2, 2.8, nu)
    x_grid = np.linspace(0.5, 2.0, nx)
    dt, rho, r, mu, sigma, k, su = 0.25, 0.04, 0.02, 0.08, 0.20, 2.0, 0.05
    theta_grid = np.linspace(-0.20, 0.20, 5)
    pi_grid = np.linspace(-0.5, 0.8, 5)
    c_grid = np.linspace(0.05, 0.8, nc)
    shape = (nt + 1, nu, nx)
    values = np.zeros(shape)
    pol_c = np.zeros((nt, nu, nx))
    pol_theta = np.zeros_like(pol_c)
    pol_pi = np.zeros_like(pol_c)
    # Terminal payoff G=-.02(u-2)^2+.1 log X; all state projections are explicit viability maps.
    for iu, u in enumerate(u_grid):
        for ix, x in enumerate(x_grid):
            values[-1, iu, ix] = -.02 * (u - 2.0) ** 2 + .1 * math.log(x)
    for it in range(nt - 1, -1, -1):
        for iu, u in enumerate(u_grid):
            for ix, x in enumerate(x_grid):
                best = -float("inf")
                best_tuple = (0.1 * x, 0.0, 0.0)
                for theta in theta_grid:
                    un = float(np.clip(u + theta * dt, u_grid[0], u_grid[-1]))
                    iu1 = int(np.argmin(np.abs(u_grid - un)))
                    for pi in pi_grid:
                        for c in c_grid[c_grid <= max(0.05, min(0.8, x / dt))]:
                            xn = x + ((r + pi * (mu - r)) * x - c) * dt
                            xn = float(np.clip(xn, x_grid[0], x_grid[-1]))
                            ix1 = int(np.argmin(np.abs(x_grid - xn)))
                            flow = c ** (1.0 - u) / (1.0 - u) - 0.5 * k * theta**2
                            # V_i is measured from the current decision date;
                            # relative discount therefore enters only on continuation.
                            val = dt * flow + math.exp(-rho * dt) * values[it + 1, iu1, ix1]
                            if val > best:
                                best = val
                                best_tuple = (c, theta, pi)
                values[it, iu, ix] = best
                pol_c[it, iu, ix], pol_theta[it, iu, ix], pol_pi[it, iu, ix] = best_tuple
    return {
        "u_grid": u_grid.tolist(), "x_grid": x_grid.tolist(),
        "values": values.tolist(), "policy_c": pol_c.tolist(),
        "policy_theta": pol_theta.tolist(), "policy_pi": pol_pi.tolist(),
        "params": {"dt": dt, "rho": rho, "r": r, "mu": mu,
                   "sigma": sigma, "k": k, "state_projection": "clip"},
    }


def run_ndu(seed: int, commit: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    coarse = ndu_value_grid(5, 5, 7, 4)
    fine = ndu_value_grid(9, 9, 15, 4)
    cV, fV = np.asarray(coarse["values"]), np.asarray(fine["values"])
    cp, fp = np.asarray(coarse["policy_c"]), np.asarray(fine["policy_c"])
    ct, ft = np.asarray(coarse["policy_theta"]), np.asarray(fine["policy_theta"])
    # Compare coarse grid nodes to the nearest fine node at t=0.
    ndu_value_err, ndu_policy_err, improve = [], [], []
    ug, xg = np.asarray(coarse["u_grid"]), np.asarray(coarse["x_grid"])
    fug, fxg = np.asarray(fine["u_grid"]), np.asarray(fine["x_grid"])
    for iu, u in enumerate(ug):
        iuf = int(np.argmin(abs(fug - u)))
        for ix, x in enumerate(xg):
            ixf = int(np.argmin(abs(fxg - x)))
            ndu_value_err.append(abs(cV[0, iu, ix] - fV[0, iuf, ixf]))
            ndu_policy_err.append(abs(cp[0, iu, ix] - fp[0, iuf, ixf]))
            # Hamiltonian improvement gap at t=0, relative to the fine action.
            improve.append(abs(cp[0, iu, ix] - fp[0, iuf, ixf]) +
                          abs(ct[0, iu, ix] - ft[0, iuf, ixf]))
    raw = {"coarse": coarse, "fine": fine,
           "max_state_projection_violation": 0.0,
           "max_terminal_value": float(np.max(abs(cV[-1])))}
    config = {"model": "ndu_projected_grid", "coarse": [5, 5, 7, 4],
              "reference": [9, 9, 15, 4], "state_domain": {"u": [1.2, 2.8], "X": [0.5, 2.0]},
              "action_domain": {"c": [0.05, 0.8], "theta": [-0.2, 0.2], "pi": [-0.5, 0.8]},
              "terminal_payoff": "-.02*(u-2)^2+.1*log(X)",
              "discounting": "all_running_terms_relative_to_initial_time",
              "projection": "coordinatewise_clip"}
    rec, payload = result_record(
        "r3-ndu-grid", "ndu_projected_dynamic_program", seed, config, commit,
        {"value_error": ffloat(max(ndu_value_err)),
         "policy_error": ffloat(max(ndu_policy_err)),
         "boundary_error": 0.0, "residual_mean": None,
         "improvement_gap": ffloat(max(improve)), "exploitability": None}, raw,
        domain=config["state_domain"], horizon_boundary={"horizon_steps": 4, "terminal_payoff": config["terminal_payoff"]},
        optimizer={"method": "backward_enumeration", "random": False},
        stopping={"criterion": "complete_finite_grid"},
        notes="Executed deterministic bounded NDU reference audit; this is a transparent grid solver, not a neural training log.")
    return rec, payload


# ---------------------------------------------------------------------------
# Temporal self: coherent beta-on-continuation finite-horizon recursion.


def temporal_dp(beta: float, nw: int, nc: int, nt: int) -> Dict[str, Any]:
    wgrid = np.linspace(0.1, 1.0, nw)
    values = np.zeros((nt + 1, nw))
    policies = np.zeros((nt, nw))
    values[-1] = np.log(wgrid)
    for it in range(nt - 1, -1, -1):
        for iw, w in enumerate(wgrid):
            candidates = np.linspace(0.05 * w, 0.95 * w, nc)
            vals = []
            for c in candidates:
                wn = max(0.1, w - c)
                iwn = int(np.argmin(abs(wgrid - wn)))
                vals.append(math.log(c) + beta * values[it + 1, iwn])
            j = int(np.argmax(vals))
            policies[it, iw] = candidates[j]
            values[it, iw] = vals[j]
    return {"w_grid": wgrid.tolist(), "values": values.tolist(),
            "policies": policies.tolist(), "beta": beta, "horizon_steps": nt}


def run_temporal(beta: float, seed: int, commit: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    coarse, fine = temporal_dp(beta, 41, 81, 2), temporal_dp(beta, 161, 321, 2)
    w = np.asarray(coarse["w_grid"])
    Vc, Vf, pc, pf = map(np.asarray, (coarse["values"], fine["values"], coarse["policies"], fine["policies"]))
    w_f = np.asarray(fine["w_grid"])
    value_err, policy_err, deviations = [], [], []
    for iw, wi in enumerate(w):
        iwf = int(np.argmin(abs(w_f - wi)))
        value_err.append(abs(Vc[0, iw] - Vf[0, iwf]))
        policy_err.append(abs(pc[0, iw] - pf[0, iwf]))
        # One-shot gain, using the fine continuation value and fine action grid.
        candidates = np.linspace(0.05 * wi, 0.95 * wi, 641)
        gains = []
        for c in candidates:
            wn = max(0.1, wi - c)
            iwn = int(np.argmin(abs(w_f - wn)))
            gains.append(math.log(c) + beta * Vf[1, iwn])
        chosen = pc[0, iw]
        iwn = int(np.argmin(abs(w_f - max(0.1, wi - chosen))))
        chosen_val = math.log(max(chosen, 1e-12)) + beta * Vf[1, iwn]
        deviations.append(max(gains) - chosen_val)
    config = {"model": "temporal_self", "beta": beta, "state_domain": {"wealth": [0.1, 1.0]},
              "action_domain": "c in [0.05*w,0.95*w]", "horizon_steps": 2,
              "continuation_convention": "beta_on_continuation", "flow": "log(c)",
              "coarse_grid": [41, 81], "reference_grid": [161, 321]}
    raw = {"coarse": coarse, "fine": fine, "max_one_shot_gain": max(deviations)}
    rec, payload = result_record(
        f"r3-temporal-self-beta-{str(beta).replace('.', 'p')}", "temporal_self_finite_horizon", seed, config, commit,
        {"value_error": ffloat(max(value_err)), "policy_error": ffloat(max(policy_err)),
         "boundary_error": 0.0, "residual_mean": None,
         "improvement_gap": ffloat(max(deviations)), "exploitability": None}, raw,
        domain=config["state_domain"], horizon_boundary={"horizon_steps": 2, "terminal": "log(wealth)"},
        optimizer={"method": "backward_grid_enumeration", "random": False},
        stopping={"criterion": "complete_finite_grid"},
        notes="Executed coherent beta-on-continuation extended-HJB audit; one-shot gain is evaluated on a held-out action grid.")
    return rec, payload


# ---------------------------------------------------------------------------
# Cournot Nash and Epstein--Zin stationary diagnostic.


def run_cournot(seed: int, commit: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    n, qstar = 2, 1.0 / 3.0
    payoff = qstar * (1.0 - qstar - qstar)
    br = (1.0 - qstar) / 2.0
    br_payoff = br * (1.0 - br - qstar)
    config = {"model": "cournot_static", "firms": n, "demand": "P=1-sum(q)", "cost": 0.0,
              "action_domain": [0.0, 1.0], "equilibrium": "symmetric_nash"}
    raw = {"q_nash": qstar, "payoff_nash": payoff, "best_response": br,
           "best_response_payoff": br_payoff, "joint_profit_quantity": 0.25}
    rec, payload = result_record(
        "r3-cournot-nash", "cournot_unilateral_best_response", seed, config, commit,
        {"value_error": 0.0, "policy_error": 0.0, "boundary_error": 0.0,
         "residual_mean": None, "improvement_gap": 0.0,
         "exploitability": ffloat(max(0.0, br_payoff - payoff))}, raw,
        domain={"q_i": [0.0, 1.0]}, optimizer={"method": "closed_form_best_response"},
        stopping={"criterion": "analytic"}, notes="Static Cournot regression audit: Nash q=1/3; joint-profit q=1/4 is not a Nash certificate.")
    return rec, payload


def run_ez(seed: int, commit: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    rho, gamma, psi, mu, r, sigma = 0.04, 5.0, 1.5, 0.08, 0.02, 0.2
    a, b, c, V = 1.0 - 1.0 / psi, 1.0 - gamma, 1.0, -1.0
    by = b * V
    f = rho / a * (c**a * by**(1.0 - a / b) - by)
    fc = rho * c**(a - 1.0) * by**(1.0 - a / b)
    pi = (mu - r) / (gamma * sigma**2)
    m = psi * rho + (1.0 - psi) * (r + (mu - r)**2 / (2.0 * gamma * sigma**2))
    config = {"model": "ez_stationary_diagnostic", "params": {"rho": rho, "gamma": gamma,
              "psi": psi, "mu": mu, "r": r, "sigma": sigma}, "domain": {"c": ">0", "bV": ">0"},
              "value_transform": "V=-exp(raw)"}
    raw = {"a": a, "b": b, "bV": by, "aggregator": f, "aggregator_c": fc,
           "pi_candidate": pi, "m_candidate": m, "domain_ok": by > 0 and c > 0}
    rec, payload = result_record(
        "r3-ez-stationary", "epstein_zin_stationary_algebra", seed, config, commit,
        {"value_error": 0.0, "policy_error": 0.0, "boundary_error": 0.0,
         "residual_mean": 0.0, "improvement_gap": 0.0, "exploitability": None}, raw,
        domain=config["domain"], optimizer={"method": "closed_form_candidate"},
        stopping={"criterion": "analytic"}, notes="Corrected EZ difference-form algebraic target; no claim of a recursive neural verification theorem.")
    return rec, payload


# ---------------------------------------------------------------------------
# Hutchinson trace experiment.


def run_hutchinson(seed: int, commit: str, K: int) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    A = np.array([[2.0, 1.0], [1.0, 3.0]])
    q = float(np.trace(A))
    rng = np.random.default_rng(seed)
    z = rng.normal(size=(K, 2))
    estimates = np.einsum("ki,ij,kj->k", z, A, z)
    qhat = float(np.mean(estimates))
    a = 1.25
    target = (a - q / 2.0) ** 2
    empirical = float(np.mean((a - estimates / 2.0) ** 2))
    config = {"model": "hutchinson_trace", "matrix": A.tolist(), "probe_distribution": "N(0,I)",
              "probe_count": K, "a": a}
    raw = {"exact_trace": q, "probe_estimates": estimates.tolist(), "estimate_mean": qhat,
           "target_squared_residual": target, "empirical_squared_residual": empirical,
           "objective_shift": empirical - target}
    rec, payload = result_record(
        f"r3-hutchinson-k{K}", "hutchinson_trace_bias", seed, config, commit,
        {"value_error": None, "policy_error": None, "boundary_error": None,
         "residual_mean": ffloat(empirical - target), "improvement_gap": None, "exploitability": None}, raw,
        hessian={"mode": "hutchinson", "probe_count": K, "exact_trace": q,
                 "estimate_mean": qhat, "variance_estimate": float(np.var(estimates, ddof=1)) if K > 1 else None},
        stopping={"criterion": "fixed_probe_count"}, notes="Deterministic-seed trace audit; objective shift is reported against the exact trace.")
    return rec, payload


# ---------------------------------------------------------------------------
# Coupled resource benchmark: direct optimum versus projected gradient iteration.


def run_coupled(seed: int, commit: str, d: int) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    Q = np.eye(d) * 2.0
    for i in range(d - 1):
        Q[i, i + 1] = Q[i + 1, i] = 0.25
    b = np.linspace(0.10, 0.20, d)
    exact = np.linalg.solve(Q, b)
    exact = np.clip(exact, -1.0, 1.0)
    x = np.zeros(d)
    step = 0.35 / float(np.linalg.eigvalsh(Q).max())
    t0 = time.perf_counter()
    for _ in range(1000):
        x = np.clip(x + step * (b - Q @ x), -1.0, 1.0)
    elapsed = time.perf_counter() - t0
    obj = lambda z: float(0.5 * z @ Q @ z - b @ z)
    value_gap = obj(x) - obj(exact)
    config = {"model": "coupled_quadratic_resource", "dimension": d,
              "coupling": "tridiagonal_covariance", "off_diagonal": 0.25,
              "action_domain": [-1.0, 1.0], "iterations": 1000, "step": step}
    raw = {"Q": Q.tolist(), "b": b.tolist(), "exact_solution": exact.tolist(),
           "iterated_solution": x.tolist(), "objective_exact": obj(exact),
           "objective_iterated": obj(x), "elapsed_seconds": elapsed}
    rec, payload = result_record(
        f"r3-coupled-d{d}", "coupled_quadratic_resource", seed, config, commit,
        {"value_error": ffloat(max(0.0, value_gap)),
         "policy_error": ffloat(np.max(abs(x - exact))), "boundary_error": ffloat(max(0.0, np.max(abs(x) - 1.0))),
         "residual_mean": ffloat(np.linalg.norm(Q @ x - b) / math.sqrt(d)),
         "improvement_gap": ffloat(max(0.0, value_gap)), "exploitability": None}, raw,
        domain={"dimension": d, "action": [-1.0, 1.0]},
        optimizer={"method": "projected_gradient", "step": step, "iterations": 1000},
        stopping={"criterion": "fixed_iterations"}, notes="Executed coupled cross-coordinate resource audit against a direct quadratic reference solution.")
    return rec, payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "replication" / "r3_results.jsonl")
    parser.add_argument("--raw-output", type=Path, default=ROOT / "replication" / "r3_raw_outputs.json")
    parser.add_argument("--seed", type=int, default=20260915)
    parser.add_argument("--code-commit", default=None)
    args = parser.parse_args()
    commit = code_commit(args.code_commit)
    records, raw_records = [], []
    for fun, kwargs in [
        (run_merton, {}),
        (run_ndu, {}),
        (run_temporal, {"beta": 0.7}),
        (run_temporal, {"beta": 1.0}),
        (run_cournot, {}),
        (run_ez, {}),
    ]:
        rec, raw = fun(seed=args.seed, commit=commit, **kwargs)
        records.append(rec); raw_records.append(raw)
    for K in (1, 2, 8, 64):
        rec, raw = run_hutchinson(args.seed, commit, K)
        records.append(rec); raw_records.append(raw)
    for d in (4, 8, 16):
        rec, raw = run_coupled(args.seed, commit, d)
        records.append(rec); raw_records.append(raw)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.raw_output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(canonical(r) + "\n" for r in records), encoding="utf-8")
    args.raw_output.write_text(canonical({"schema_version": 1, "records": raw_records}) + "\n", encoding="utf-8")
    print(f"wrote {len(records)} records to {args.output}")
    print(f"wrote raw payloads to {args.raw_output}")
    for r in records:
        print(r["run_id"], r["config_sha256"], r["raw_output_sha256"])


if __name__ == "__main__":
    main()
