"""R14 finite-observation transfer and shared-noise Euler diagnostics.

The mathematical bound concerns the original continuous diffusion. The
simulation is explicitly a finite-Euler diagnostic and creates no confidence
interval or fitted policy. Invoke only on the prespecified saved NBO k80
weights. The source below uses the inherited outward interval arithmetic and
protected polynomial activations, while retaining the full model primitives.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np


PROTOCOL = {
    "record_type": "finite_observation_diagnostic_protocol",
    "noise_seed": 1410047919,
    "dimensions": [10, 20, 50],
    "training_seed": 7919,
    "checkpoint_iteration": 80,
    "method": "nbo",
    "paths": 128,
    "actor_cells": [64, 128],
    "truth_refinement": 8,
    "sensor_noise_rms": [0.0, 0.001, 0.01],
    "population_means": [-0.5, 0.0, 0.5],
    "population_spreads": [0.0, 0.25, 0.5],
    "population_weights": "uniform over the nine declared profiles",
    "seed_derivation": "economic seed = base + 10000*d + cells; sensor seed = economic seed + 10000000",
    "selection": "prespecified original saved NBO iteration-80 weights; no new fitting or outcome selection",
    "observation": "direct finite measured-state feedback, with independent per-coordinate Gaussian noise of normalized L2 RMS nu",
    "physical_grid": "8 fine Euler cells per actor decision cell; physical state and Brownian innovations are never clipped",
    "parent": "same protected saved-weight actor on its clipped-innovation internal Euler state",
    "scope": "finite-Euler paired diagnostic and deterministic continuous-diffusion transfer allowance; no new stochastic certificate",
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")


def load_runtime(repo):
    sys.path.insert(0, str(Path(repo) / "revisions/2026-10-04-r11/code"))
    old = importlib.import_module("bellman_study")
    pc = importlib.import_module("policy_certificate")
    tc = importlib.import_module("tube_certificate")
    torch = importlib.import_module("torch")
    torch.set_default_dtype(torch.float64)
    torch.set_num_threads(1)
    return old, pc, tc, torch


def population(d):
    v = np.linspace(-1.0, 1.0, d)
    v -= v.mean()
    v /= np.sqrt(np.mean(v * v))
    return np.asarray([
        mu + spread * v
        for mu in PROTOCOL["population_means"]
        for spread in PROTOCOL["population_spreads"]
    ])


def network_account(actor, d, epsilon, P, pc, tc, torch):
    """Outward bounds for ideal clipped-input tanh network vs protected map."""
    I = pc.I
    layers = [m for m in actor.modules() if isinstance(m, torch.nn.Linear)]
    if not layers:
        raise ValueError("actor contains no affine layers")
    bounds = I(np.r_[P["T"], np.full(d, 100.0)])
    # Include input representation within the protected map. A measurement
    # error before that map belongs to nu, not to this arithmetic term.
    errors = I(4.0 * np.finfo(float).eps) * bounds
    lip = I(epsilon)
    for layer in layers:
        W = layer.weight.detach().numpy()
        bias = layer.bias.detach().numpy()
        aw, ab = I(abs(W)), I(abs(bias))
        magnitudes = pc.sum_axis(aw * bounds, axis=1) + ab
        errors = (pc.sum_axis(aw * errors, axis=1)
                  + I(pc.gamma(W.shape[1] + 2)) * magnitudes
                  + I(2.0 ** -34))
        bounds = I(np.full(W.shape[0], float(pc.up(1.0 + 2.0 ** -34))))
        frob = tc.sqrt_i(tc.sum_i(I(W).square()))
        one = float(np.max(pc.sum_axis(aw, axis=0).hi))
        infinity = float(np.max(pc.sum_axis(aw, axis=1).hi))
        induced = tc.sqrt_i(I(one) * I(infinity))
        lip = lip * I(min(float(frob.hi), float(induced.hi)))
    errors = I(epsilon) * errors + I(pc.gamma(4)) * (
        I(P["upper"]) + I(epsilon) * bounds)
    error = tc.sqrt_i(pc.mean_i(errors.square()))
    return {
        "lipschitz_upper": float(lip.hi),
        "actor_roundoff_rms_upper": float(error.hi),
        "input_representation_included": True,
        "layers": len(layers),
        "activation_error_upper": 2.0 ** -34,
        "interpretation": "saved binary64 coefficients as exact reals; global tanh Lipschitz bound and protected-kernel roundoff; common inward guard is nonexpansive",
    }


class ProtectedActor:
    """The exact same protected map is used by both compared controllers."""

    def __init__(self, actor, epsilon, pc, torch):
        self.pc = pc
        self.epsilon = epsilon
        self.layers = [
            (m.weight.detach().numpy().copy(), m.bias.detach().numpy().copy())
            for m in actor.modules() if isinstance(m, torch.nn.Linear)
        ]

    def __call__(self, t, states, center, lo, hi):
        z = np.c_[np.full(len(states), t), np.clip(states, -100.0, 100.0)]
        for W, bias in self.layers:
            z = self.pc.safe_tanh(z @ W.T + bias)
        proposal = center + self.epsilon * z
        if not np.isfinite(proposal).all():
            raise FloatingPointError("nonfinite protected actor proposal")
        return np.maximum(lo, np.minimum(hi, proposal))


def transfer_allowance(actor, st, cells, noise_rms, support, old, pc, tc, torch):
    """Outward version of Proposition r14sensor, independent of diagnostic data."""
    I = pc.I
    P, chi = old.P, old.CHI
    d, epsilon = int(st["dimension"]), float(st["epsilon"])
    T, h = I(P["T"]), I(P["T"]) / cells
    kappa, sigma_i, sigma_c = I(P["coupling"]), I(P["idiosyncratic_sigma"]), I(P["common_sigma"])
    B = old.coupling(d)
    sp = tc.spectral_bound(B)
    beta = I(float((kappa * I(sp["norm_upper"])).hi))
    q = sigma_i.square() * pc.sum_axis(I(B).square(), axis=1)
    q = q + sigma_c.square() * pc.sum_axis(I(B), axis=1).square()
    H = kappa * tc.sqrt_i(pc.mean_i(q))
    Qf = kappa * tc.sqrt_i(pc.mean_i(q.square())) / 2
    wt = pc.weights(cells)
    lower = float(pc.down(np.min(wt["center"].lo) - epsilon))
    upper = float(pc.up(np.max(wt["center"].hi) + epsilon))
    if lower <= P["lower"] or upper >= P["upper"]:
        raise ValueError("action tube does not lie inside primitive action box")
    c0 = I(P["productivity"]) - (sigma_i.square() + sigma_c.square()) / 2
    M = I(float((c0 - I(lower, upper)).absmax())) + kappa
    K = beta * M + Qf
    sigma_bar = tc.sqrt_i(sigma_i.square() + sigma_c.square())
    zcap = I(10.0)
    pi = I(math.pi - 1e-15, math.pi + 1e-15)
    vc = 2 * pc.exp_i(-zcap.square() / 2) * (zcap + 1 / zcap) / tc.sqrt_i(2 * pi)
    net = network_account(actor, d, epsilon, P, pc, tc, torch)
    L, delta = I(net["lipschitz_upper"]), I(net["actor_roundoff_rms_upper"])
    initial_max = float(np.max(abs(support)))
    spreads = []
    for y in support:
        yi = I(y)
        spreads.append(float(pc.sqrt_nonnegative(pc.mean_i((yi - pc.mean_i(yi)).square())).hi))
    s0 = max(spreads)
    state_cap = 2 * (I(initial_max) + M * T + (sigma_i + sigma_c) * zcap * T / tc.sqrt_i(h) + 1)
    row_norm = I(float(np.max(pc.sum_axis(I(abs(B)), axis=1).hi)))
    dot_error = I(pc.gamma(d + 2)) * state_cap * row_norm
    drift_round = kappa * (I(2.0 ** -34) + dot_error)
    drift_round = drift_round + I(pc.gamma(8)) * (I(float(c0.absmax())) + kappa + I(upper))
    noise_cap = (sigma_i + sigma_c) * zcap * tc.sqrt_i(h)
    xi = h * drift_round + I(pc.gamma(20)) * (state_cap + h * M + noise_cap)
    xi = xi + I(16 * np.finfo(float).eps) * noise_cap
    bootstrap = I(cells) * xi * pc.exp_i(beta * T)
    if float(bootstrap.hi) >= 1:
        raise ArithmeticError("internal roundoff bootstrap failed")
    Qterminal = I(s0) + (kappa + I(epsilon)) * T
    Qterminal = Qterminal + sigma_i * tc.sqrt_i((1 - I(1) / d) * T)

    e, physical, b_previous = I(0.0), I(0.0), 0.0
    prod_budget, deficit_budget = I(0.0), I(0.0)
    cap = float((2 * I(epsilon)).hi)
    growth = pc.exp_i(beta * h)
    if float(beta.lo) > 0:
        action_kernel = (growth - 1) / beta
    else:
        action_kernel = h
    rows = []
    for k in range(cells):
        ak = min(cap, float((L * (e + I(noise_rms)) + 2 * delta).hi))
        ai = I(ak)
        tk1 = I(P["T"] * (k + 1) / cells)
        forcing = h * (K * tk1 / 2 + H * tc.sqrt_i(tk1 / 3))
        forcing = forcing + sigma_bar * tc.sqrt_i(tk1 * vc) + (k + 1) * xi
        b_next = max(b_previous, float(forcing.hi))
        e_next = (1 + beta * h) * e + h * ai + (I(b_next) - I(b_previous))
        e = I(float(e_next.hi))
        physical = I(float((growth * physical + action_kernel * ai).hi))
        clock = P["T"] * k / cells
        next_clock = P["T"] * (k + 1) / cells
        schedule_cell = pc.schedule_i(I(clock, next_clock))
        center_cell = pc.schedule_i(I(clock))
        radius = I(epsilon) + I(float((schedule_cell - center_cell).absmax()))
        m_minus = float(pc.down(float(center_cell.lo) - epsilon))
        if m_minus <= 0 or float(schedule_cell.lo) <= 0:
            raise ArithmeticError("invalid deficit-gradient denominator")
        deficit_lip = radius * (1 / (I(float(schedule_cell.lo)) * I(m_minus)) + I(P["adjustment"]))
        prod_budget = prod_budget + beta * I(wt["B"].lo[k], wt["B"].hi[k]) * physical
        deficit_budget = deficit_budget + I(wt["A"].lo[k], wt["A"].hi[k]) * deficit_lip * ai
        rows.append({
            "cell": k, "node_error_next_upper": float(e.hi),
            "action_error_upper": ak, "forcing_next_upper": b_next,
            "physical_error_next_upper": float(physical.hi),
            "deficit_lipschitz_upper": float(deficit_lip.hi),
        })
        b_previous = b_next
    terminal_budget = 2 * I(chi) * pc.exp_i(-I(P["discount"]) * T) * Qterminal * physical
    total = prod_budget + deficit_budget + terminal_budget
    return {
        "record_type": "continuous_diffusion_sensor_transfer_allowance",
        "dimension": d, "cells": cells, "sensor_noise_rms": noise_rms,
        "network": net, "drift_lipschitz_upper": float(beta.hi),
        "generator_H_upper": float(H.hi), "generator_K_upper": float(K.hi),
        "gaussian_clip_second_moment_upper": float(vc.hi),
        "initial_spread_upper": s0, "initial_max_abs": initial_max,
        "internal_state_cap": float(state_cap.hi),
        "recurrence_roundoff_per_cell_upper": float(xi.hi),
        "roundoff_bootstrap_upper": float(bootstrap.hi),
        "terminal_internal_error_upper": float(e.hi),
        "terminal_physical_error_upper": float(physical.hi),
        "max_action_difference_upper": max(r["action_error_upper"] for r in rows),
        "production_payoff_allowance": float(prod_budget.hi),
        "consumption_deficit_allowance": float(deficit_budget.hi),
        "terminal_dispersion_allowance": float(terminal_budget.hi),
        "payoff_difference_upper": float(total.hi),
        "spectral_matrix_sha256": sp["matrix_sha256"],
        "recursion": rows,
        "scope": "deterministic upper bound between two original continuous physical diffusions under stated arithmetic and observation assumptions; no fitted-parent payoff certificate is manufactured",
    }


def diagnose(path, out, old, pc, tc, torch, repo):
    actor, _critic, st = old.load(Path(path))
    d, epsilon = int(st["dimension"]), float(st["epsilon"])
    if Path(path).name != f"nbo_d{d}_s7919_fixed_nbo_k80.pt":
        raise ValueError("undeclared saved checkpoint identity")
    if d not in PROTOCOL["dimensions"] or st["method"] != "nbo":
        raise ValueError("weights outside prespecified method/dimension set")
    if int(st["iteration"]) != PROTOCOL["checkpoint_iteration"]:
        raise ValueError("use original prespecified iteration-80 checkpoint")
    P, chi = old.P, old.CHI
    protected = ProtectedActor(actor, epsilon, pc, torch)
    support = population(d)
    B = old.coupling(d)
    paths = PROTOCOL["paths"]
    c0 = P["productivity"] - (P["idiosyncratic_sigma"] ** 2 + P["common_sigma"] ** 2) / 2
    raw, rows = {}, []

    def production(y):
        return P["coupling"] * pc.safe_tanh(y @ B.T)

    def flow(y, action):
        return (pc.safe_log(action) + y).mean(1) - P["adjustment"] / 2 * action.mean(1) ** 2

    def terminal(y):
        return y.mean(1) - chi * ((y - y.mean(1, keepdims=True)) ** 2).mean(1)

    for cells in PROTOCOL["actor_cells"]:
        fine = cells * PROTOCOL["truth_refinement"]
        ratio = PROTOCOL["truth_refinement"]
        h, dt = P["T"] / cells, P["T"] / fine
        seed = PROTOCOL["noise_seed"] + 10000 * d + cells
        rng = np.random.default_rng(seed)
        economic = rng.standard_normal((fine, paths, d + 1))
        ids = rng.integers(len(support), size=paths)
        initial = support[ids].copy()
        sensing_seed = seed + 10000000
        errors = np.random.default_rng(sensing_seed).standard_normal((cells, paths, d))
        coarse = economic.reshape(cells, ratio, paths, d + 1).sum(1) / math.sqrt(ratio)
        wt = pc.weights(cells)
        centers = pc.midpoint(wt["center"])
        low = pc.up(wt["center"].hi - epsilon)
        high = pc.down(wt["center"].lo + epsilon)
        raw[f"n{cells}_initial_indices"] = ids
        raw[f"n{cells}_initial_states"] = initial
        for nu in PROTOCOL["sensor_noise_rms"]:
            allowance = transfer_allowance(actor, st, cells, nu, support, old, pc, tc, torch)
            start = time.perf_counter()
            internal, physical_parent, physical_sensor = initial.copy(), initial.copy(), initial.copy()
            parent_payoff, sensor_payoff = np.zeros(paths), np.zeros(paths)
            max_internal_error = np.zeros(paths)
            max_action_difference = np.zeros(paths)
            for k in range(cells):
                clock = k * h
                observed = physical_sensor + nu * errors[k]
                parent_action = protected(clock, internal, centers[k], low[k], high[k])
                sensor_action = protected(clock, observed, centers[k], low[k], high[k])
                action_distance = np.sqrt(np.mean((parent_action - sensor_action) ** 2, axis=1))
                max_action_difference = np.maximum(max_action_difference, action_distance)
                for j in range(ratio):
                    n = k * ratio + j
                    discounted_dt = math.exp(-P["discount"] * n * dt) * dt
                    parent_payoff += discounted_dt * flow(physical_parent, parent_action)
                    sensor_payoff += discounted_dt * flow(physical_sensor, sensor_action)
                    dw = math.sqrt(dt) * (
                        P["idiosyncratic_sigma"] * economic[n, :, :d]
                        + P["common_sigma"] * economic[n, :, d:])
                    physical_parent += dt * (c0 + production(physical_parent) - parent_action) + dw
                    physical_sensor += dt * (c0 + production(physical_sensor) - sensor_action) + dw
                clipped = np.clip(coarse[k], -10.0, 10.0)
                dw_internal = math.sqrt(h) * (
                    P["idiosyncratic_sigma"] * clipped[:, :d]
                    + P["common_sigma"] * clipped[:, d:])
                internal += h * (c0 + production(internal) - parent_action) + dw_internal
                node_error = np.sqrt(np.mean((physical_sensor - internal) ** 2, axis=1))
                max_internal_error = np.maximum(max_internal_error, node_error)
            discount_terminal = math.exp(-P["discount"] * P["T"])
            parent_payoff += discount_terminal * terminal(physical_parent)
            sensor_payoff += discount_terminal * terminal(physical_sensor)
            difference = sensor_payoff - parent_payoff
            key = f"d{d}_n{cells}_nu{nu:g}"
            raw[key + "_paired_payoff"] = difference
            raw[key + "_parent_payoff"] = parent_payoff
            raw[key + "_sensor_payoff"] = sensor_payoff
            raw[key + "_max_node_error"] = max_internal_error
            raw[key + "_max_action_difference"] = max_action_difference
            raw[key + "_terminal_parent"] = physical_parent
            raw[key + "_terminal_sensor"] = physical_sensor
            raw[key + "_terminal_internal"] = internal
            rows.append({
                "id": key, "dimension": d, "actor_cells": cells,
                "fine_euler_cells": fine, "paths": paths,
                "sensor_noise_rms": nu,
                "economic_noise_seed": seed, "sensor_noise_seed": sensing_seed,
                "economic_noise_sha256": hashlib.sha256(economic.tobytes()).hexdigest(),
                "sensor_standard_noise_sha256": hashlib.sha256(errors.tobytes()).hexdigest(),
                "fine_euler_mean_sensor_minus_parent": float(difference.mean()),
                "descriptive_mc_standard_error": float(difference.std(ddof=1) / math.sqrt(paths)),
                "fine_euler_max_abs_paired_difference": float(abs(difference).max()),
                "sample_rms_terminal_state_difference": float(np.sqrt(np.mean((physical_sensor - physical_parent) ** 2))),
                "seconds": time.perf_counter() - start,
                "allowance": allowance,
                "scope": "shared-noise finite-Euler implementation diagnostic; standard error describes simulation dispersion and omits fine-Euler bias; no continuous-payoff confidence claim",
            })
    ident = f"nbo_d{d}_s7919_k80_finite_observation"
    raw_path = out / (ident + ".npz")
    np.savez_compressed(raw_path, **raw)
    result = {
        "record_type": "finite_observation_diagnostic",
        "weights": str(Path(path).resolve().relative_to(repo.resolve())), "weights_sha256": digest(path),
        "dimension": d, "stored_iteration": int(st["iteration"]),
        "protocol": PROTOCOL, "rows": rows,
        "raw_file": str(raw_path.resolve().relative_to(repo.resolve())), "raw_sha256": digest(raw_path),
        "economic_claim": "The deterministic allowance applies conditionally to the specified two continuous-economy controllers. This diagnostic creates no schedule-relative endpoint and no NBO-versus-DPO result.",
    }
    write(out / (ident + ".json"), result)
    print(json.dumps({"dimension": d, "rows": len(rows), "raw_sha256": result["raw_sha256"]}), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--weights", required=True, nargs="+", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    # Materialize the protocol before runtime loading, weights inspection, or
    # any diagnostic computation. No result can change the declared choices.
    write(args.out / "PROTOCOL.json", PROTOCOL)
    old, pc, tc, torch = load_runtime(args.repo)
    environment = {
        "python": platform.python_version(), "platform": platform.platform(),
        "numpy": np.__version__, "torch": torch.__version__,
        "threads": torch.get_num_threads(),
        "script_sha256": digest(__file__),
        "reporting_checkout": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=args.repo, text=True).strip(),
        "weights": {str(p.resolve().relative_to(args.repo.resolve())): digest(p) for p in args.weights},
        "historical_kernels": {str(Path(module.__file__).resolve().relative_to(args.repo.resolve())): digest(module.__file__) for module in [old, pc, tc]},
        "protocol_sha256": digest(args.out / "PROTOCOL.json"),
    }
    write(args.out / "ENVIRONMENT.json", environment)
    rows = [diagnose(path, args.out, old, pc, tc, torch, args.repo) for path in args.weights]
    if sorted(r["dimension"] for r in rows) != PROTOCOL["dimensions"]:
        raise ValueError("the complete diagnostic requires exactly dimensions 10, 20, and 50")
    write(args.out / "INDEX.json", {
        "complete": True, "records": len(rows), "diagnostic_rows": sum(len(r["rows"]) for r in rows),
        "protocol_sha256": digest(args.out / "PROTOCOL.json"),
        "weights_sha256": [r["weights_sha256"] for r in rows],
        "interpretation": "complete prescribed finite-observation diagnostic; no new training and no statistical superiority assertion",
    })


if __name__ == "__main__":
    main()
