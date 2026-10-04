"""Replay the four R12 scalar references with frozen stored policies (R14 M8).

No training, policy selection, model change, or grid/boundary change occurs.
Original inputs are read-only and checked again after the replay.  The original
R12 numerical kernels are imported unchanged; an independently written stencil
residual instruments every solve.  Outputs belong to a separate directory.

Example from an integrated repository:
  python revisions/2026-10-04-r14/code/reference_diagnostics.py --repo . \
    --reference-dir revisions/2026-10-04-r12/results/reference \
    --output-dir revisions/2026-10-04-r14/results/reference
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

sys.dont_write_bytecode = True
for _name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import numpy as np
import scipy
import torch

SOURCE_COMMIT = "95053e722e57523c1a61c71f2f8bb7a6afbf09a7"
GRIDS = ((401, 256, 6.0), (801, 512, 6.0),
         (1601, 1024, 6.0), (1601, 1024, 8.0))
INITIAL_STATES = np.array([-1.0, -0.5, 0.0, 0.5, 1.0])
METHODS = ("optimal", "nbo", "dpo", "linear", "anchor")
REPLAY_ATOL = 2e-12
REPLAY_RTOL = 2e-13
BOUND_ATOL = 1e-12
HOWARD_TOL = 1e-11  # The original stopping rule, unchanged.
MAX_HOWARD = 100   # The original cap, unchanged.
SOURCE_PATHS = (
    "revisions/2026-10-04-r12/PROTOCOL.json",
    "revisions/2026-10-04-r12/code/common.py",
    "revisions/2026-10-04-r12/code/reference.py",
    "revisions/2026-10-04-r12/code/reference_audit.py",
    "revisions/2026-10-04-r11/code/bellman_study.py",
    "revisions/2026-10-04-r11/code/policy_certificate.py",
    "revisions/2026-10-04-r11/code/fast_arithmetic.py",
    "revisions/2026-10-04-r10/code/tube_neural.py",
    "revisions/2026-10-04-r10/code/tube_certificate.py",
    "revisions/2026-09-29-r6/code/interval_certificate.py",
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")


def maximum(a):
    return float(np.max(np.abs(a)))


def check_source(repo):
    """Compare the executed kernel closure with the preserved source commit."""
    records = []
    for relative in SOURCE_PATHS:
        local = repo / relative
        pinned = subprocess.check_output(
            ["git", "show", f"{SOURCE_COMMIT}:{relative}"], cwd=repo)
        expected = hashlib.sha256(pinned).hexdigest()
        actual = sha(local)
        if actual != expected:
            raise RuntimeError(f"Unchanged-source requirement failed: {relative}")
        records.append({"path": relative, "sha256": actual,
                        "matches_source_commit": True})
    return records


def residual(v, vnext, y, m, h, p, scalar_coupling):
    """Original-equation residual, with boundary nodes included exactly once.

    Separate from reference.implicit: computes L^m v directly from neighboring
    differences; does not reuse its banded matrix or boundary-adjusted RHS.
    """
    dx = y[1] - y[0]
    diffusion = (p["idiosyncratic_sigma"]**2 + p["common_sigma"]**2) / 2
    mu = p["productivity"] - diffusion + p["coupling"] * np.tanh(
        scalar_coupling * y[1:-1]) - m
    low = diffusion / dx**2 + np.maximum(-mu, 0) / dx
    high = diffusion / dx**2 + np.maximum(mu, 0) / dx
    utility = np.log(m) + y[1:-1] - p["adjustment"] * m*m / 2
    center = v[1:-1]
    r = (center-vnext[1:-1])/h + p["discount"]*center
    r -= low*(v[:-2]-center) + high*(v[2:]-center) + utility
    # Componentwise equation scale; this is a backward-error diagnostic.
    scale = (np.abs(vnext[1:-1])/h + np.abs(utility)
             + (1/h+p["discount"]+low+high)*np.abs(center)
             + low*np.abs(v[:-2]) + high*np.abs(v[2:]))
    scaled = np.abs(r) / np.maximum(scale, np.finfo(float).tiny)
    return r, maximum(scaled)


def action_summary(m, raw, mask, p):
    m = m[mask]
    raw = raw[mask]
    return np.array([
        len(m),
        np.count_nonzero(np.abs(m-p["lower"]) <= BOUND_ATOL),
        np.count_nonzero(np.abs(m-p["upper"]) <= BOUND_ATOL),
        np.count_nonzero(raw < p["lower"]),
        np.count_nonzero(raw > p["upper"]),
    ], dtype=np.int64)


def unpack_action_counts(counts):
    n, lo, hi, clip_lo, clip_hi = map(int, counts)
    return {"nodes": n, "lower_bound_count": lo, "upper_bound_count": hi,
            "lower_bound_frequency": lo/n if n else 0.0,
            "upper_bound_frequency": hi/n if n else 0.0,
            "raw_below_lower_count": clip_lo, "raw_above_upper_count": clip_hi}


def defect_propagation(r, h, rho):
    e = 0.0
    for value in r[::-1]:
        e = (e+h*float(value))/(1+rho*h)
    return e


def summary_metric(diff, x):
    diff = np.asarray(diff)
    i = int(np.argmax(np.abs(diff)))
    return {"max_abs": maximum(diff), "rms": float(np.sqrt(np.mean(diff**2))),
            "state_at_max_abs": float(x[i]), "signed_at_max_abs": float(diff[i])}


def replay(record, actors, ref, reference_dir, output):
    p = ref.P
    nx, nt, length = record["nx"], record["nt"], record["L"]
    ident = record["id"]
    start = time.perf_counter()
    y = np.linspace(-length, length, nx)
    grid = np.linspace(0, p["T"], nt+1)
    h = p["T"]/nt
    boundary = ref.boundaries(grid, length)
    values = {name: y.copy() for name in METHODS}
    time0_actions = {}
    scalar_coupling = float(ref.old.coupling(1)[0, 0])
    core = np.abs(y[1:-1]) <= 1.0
    full = np.ones(nx-2, dtype=bool)
    linear = {name: np.zeros(nt) for name in METHODS}
    scaled_linear = {name: np.zeros(nt) for name in METHODS}
    prescribed_boundary_error = {name: np.zeros(nt) for name in METHODS}
    counts = {name: {"all_interior_time_nodes": np.zeros(5, dtype=np.int64),
                     "core_interior_time_nodes": np.zeros(5, dtype=np.int64)}
              for name in METHODS}
    action_min = {name: float("inf") for name in METHODS}
    action_max = {name: -float("inf") for name in METHODS}
    nonlinear = np.zeros(nt)
    fixed_point = np.zeros(nt)
    iterations = np.zeros(nt, dtype=np.int64)
    last_delta = np.zeros(nt)
    converged = np.zeros(nt, dtype=bool)
    # All Howard iteration records are stored, including the first iteration.
    trace_k, trace_it, trace_delta, trace_linear, trace_nonlinear = [], [], [], [], []
    kernel_residual_agreement = 0.0
    original_aggregate_residual = 0.0
    for k in range(nt-1, -1, -1):
        b = (boundary[0][k], boundary[1][k])
        vn = values["optimal"]
        v = vn.copy()
        for it in range(MAX_HOWARD):
            m = ref.best_action(v, y)
            new, reported_residual = ref.implicit(vn, y, m, h, b)
            gap = maximum(new-v)
            rlin, slin = residual(new, vn, y, m, h, p, scalar_coupling)
            mnew = ref.best_action(new, y)
            rn, _ = residual(new, vn, y, mnew, h, p, scalar_coupling)
            kernel_residual_agreement = max(
                kernel_residual_agreement, abs(maximum(rlin)-reported_residual))
            trace_k.append(k); trace_it.append(it+1); trace_delta.append(gap)
            trace_linear.append(maximum(rlin)); trace_nonlinear.append(maximum(rn))
            linear["optimal"][k] = max(linear["optimal"][k], maximum(rlin))
            scaled_linear["optimal"][k] = max(scaled_linear["optimal"][k], slin)
            v = new
            if gap < HOWARD_TOL:
                converged[k] = True
                break
        iterations[k] = it+1
        last_delta[k] = gap
        m = ref.best_action(v, y)
        check, reported_residual = ref.implicit(vn, y, m, h, b)
        rc, sc = residual(check, vn, y, m, h, p, scalar_coupling)
        linear["optimal"][k] = max(linear["optimal"][k], maximum(rc))
        scaled_linear["optimal"][k] = max(scaled_linear["optimal"][k], sc)
        rn, _ = residual(v, vn, y, m, h, p, scalar_coupling)
        nonlinear[k] = maximum(rn)
        fixed_point[k] = maximum(check-v)/h
        original_aggregate_residual = max(
            original_aggregate_residual, fixed_point[k], reported_residual)
        values["optimal"] = v
        prescribed_boundary_error["optimal"][k] = maximum(v[[0, -1]]-np.asarray(b))
        actions = {"optimal": (m, m)}
        for name, actor in actors.items():
            with torch.no_grad():
                raw = actor(torch.from_numpy(
                    np.c_[np.full(nx-2, grid[k]), y[1:-1]])).numpy().ravel()
            m = np.clip(raw, p["lower"], p["upper"])
            next_value = values[name]
            vv, reported_residual = ref.implicit(next_value, y, m, h, b)
            rf, sf = residual(vv, next_value, y, m, h, p, scalar_coupling)
            linear[name][k] = maximum(rf)
            scaled_linear[name][k] = sf
            kernel_residual_agreement = max(
                kernel_residual_agreement, abs(maximum(rf)-reported_residual))
            prescribed_boundary_error[name][k] = maximum(vv[[0, -1]]-np.asarray(b))
            values[name] = vv
            original_aggregate_residual = max(original_aggregate_residual, reported_residual)
            actions[name] = (m, raw)
        for name, (m, raw) in actions.items():
            counts[name]["all_interior_time_nodes"] += action_summary(m, raw, full, p)
            counts[name]["core_interior_time_nodes"] += action_summary(m, raw, core, p)
            action_min[name] = min(action_min[name], float(m.min()))
            action_max[name] = max(action_max[name], float(m.max()))
            if k == 0:
                time0_actions[name] = m.copy()
                counts[name]["time0_all_interior_nodes"] = action_summary(m, raw, full, p)
                counts[name]["time0_core_interior_nodes"] = action_summary(m, raw, core, p)
    regenerated = {"state": y, "optimal_action_t0": time0_actions["optimal"], **values}
    replay_file = output / f"{ident}.replay.npz"
    np.savez_compressed(replay_file, **regenerated)
    comparisons = {}
    with np.load(reference_dir / f"{ident}.npz", allow_pickle=False) as original:
        if set(original.files) != set(regenerated):
            raise RuntimeError(f"Replay array inventory differs for {ident}")
        for key, value in regenerated.items():
            observed = original[key]
            if value.shape != observed.shape:
                raise RuntimeError(f"Shape mismatch for {ident}:{key}")
            tolerance = REPLAY_ATOL+REPLAY_RTOL*np.abs(observed)
            diff = value-observed
            comparisons[key] = {"shape": list(value.shape),
                "max_abs_difference": maximum(diff),
                "max_tolerance_ratio": float(np.max(np.abs(diff)/tolerance)),
                "bitwise_equal_array": bool(np.array_equal(value, observed)),
                "within_declared_tolerance": bool(np.all(np.abs(diff) <= tolerance))}
    samples = []
    for state in INITIAL_STATES:
        vals = {name: float(np.interp(state, y, values[name])) for name in METHODS}
        actions_at_state = {"optimal": float(np.interp(
            state, y[1:-1], time0_actions["optimal"]))}
        for name, actor in actors.items():
            with torch.no_grad():
                raw = float(actor(torch.tensor([[0.0, state]])).item())
            actions_at_state[name] = float(np.clip(raw, p["lower"], p["upper"]))
        samples.append({"initial_log_capital": float(state), "values": vals,
                        "policy_losses": {name: vals["optimal"]-vals[name]
                                          for name in METHODS if name != "optimal"},
                        "actions": actions_at_state})
    diag_arrays = {
        "time": grid[:-1], "state": y, "action_state": y[1:-1],
        "boundary_time": grid, "boundary_left": boundary[0], "boundary_right": boundary[1],
        "howard_iterations": iterations, "howard_last_value_delta": last_delta,
        "howard_converged": converged, "howard_hjb_residual": nonlinear,
        "howard_fixed_point_residual_over_h": fixed_point,
        "trace_time_index": np.asarray(trace_k, dtype=np.int64),
        "trace_iteration": np.asarray(trace_it, dtype=np.int64),
        "trace_value_delta": np.asarray(trace_delta),
        "trace_linear_equation_residual": np.asarray(trace_linear),
        "trace_hjb_residual_after_iteration": np.asarray(trace_nonlinear),
    }
    for name in METHODS:
        diag_arrays[f"action_t0_{name}"] = time0_actions[name]
        diag_arrays[f"linear_equation_residual_{name}"] = linear[name]
        diag_arrays[f"scaled_linear_residual_{name}"] = scaled_linear[name]
        diag_arrays[f"prescribed_boundary_mismatch_{name}"] = prescribed_boundary_error[name]
    diag_file = output / f"{ident}.diagnostics.npz"
    np.savez_compressed(diag_file, **diag_arrays)
    methods = {}
    for name in METHODS:
        losses = values["optimal"]-values[name]
        value_core = np.abs(y) <= 1.0
        r = nonlinear if name == "optimal" else linear[name]
        methods[name] = {
            "max_linear_equation_residual": float(linear[name].max()),
            "max_scaled_linear_residual": float(scaled_linear[name].max()),
            "max_prescribed_boundary_mismatch": float(prescribed_boundary_error[name].max()),
            "residual_propagation_diagnostic_t0": defect_propagation(r, h, p["discount"]),
            "min_action_all_interior_time_nodes": action_min[name],
            "max_action_all_interior_time_nodes": action_max[name],
            "bound_frequencies": {scope: unpack_action_counts(c)
                                  for scope, c in counts[name].items()},
            "loss_t0_core_max": float(losses[value_core].max()),
            "loss_t0_full_max": float(losses.max()),
            "loss_t0_full_argmax": float(y[np.argmax(losses)]),
            "action_t0_error_core": summary_metric(
                time0_actions[name][core]-time0_actions["optimal"][core], y[1:-1][core]),
        }
    row = {"id": ident, "nx": nx, "nt": nt, "L": length,
           "dx": float(y[1]-y[0]), "dt": h,
           "boundary_quadrature_points": max(8193, 8*len(grid)+1),
           "original_npz_sha256": sha(reference_dir / f"{ident}.npz"),
           "replay_npz": replay_file.name, "replay_npz_sha256": sha(replay_file),
           "diagnostics_npz": diag_file.name, "diagnostics_npz_sha256": sha(diag_file),
           "all_replayed_arrays_match": all(v["within_declared_tolerance"] for v in comparisons.values()),
           "array_comparisons": comparisons,
           "original_aggregate_residual_replayed": original_aggregate_residual,
           "original_reported_aggregate_residual": record["max_equation_residual"],
           "original_kernel_residual_recalculation_max_difference": kernel_residual_agreement,
           "howard": {"all_steps_converged": bool(converged.all()),
               "unconverged_time_indices": np.flatnonzero(~converged).tolist(),
               "iterations_total": int(iterations.sum()),
               "iterations_original": record["policy_iterations"],
               "iterations_match_original": int(iterations.sum()) == record["policy_iterations"],
               "iterations_min": int(iterations.min()), "iterations_max": int(iterations.max()),
               "max_last_value_delta": float(last_delta.max()),
               "max_hjb_residual": float(nonlinear.max()),
               "max_fixed_point_residual_over_h": float(fixed_point.max())},
           "methods": methods, "five_initial_states": samples,
           "seconds_including_instrumentation": time.perf_counter()-start}
    write_json(output / f"{ident}.diagnostics.json", row)
    print(json.dumps({"grid": ident, "replay_match": row["all_replayed_arrays_match"],
                      "howard_residual": row["howard"]["max_hjb_residual"],
                      "seconds": row["seconds_including_instrumentation"]}), flush=True)
    return row, {"state": y, "actions": time0_actions, "values": values}


def refinement(first, second, first_data, second_data):
    ya, yb = first_data["state"], second_data["state"]
    x = ya[(ya >= yb[0]) & (ya <= yb[-1])]
    ax = ya[1:-1]
    ax = ax[(ax >= yb[1]) & (ax <= yb[-2])]
    result = {"from_grid": first["id"], "to_grid": second["id"],
        "type": ("nested_space_time_refinement" if first["L"] == second["L"]
                 else "domain_expansion_with_changed_spatial_spacing"),
        "direction": "second grid minus first grid; second arrays linearly interpolated at first-grid nodes",
        "methods": {}}
    for name in METHODS:
        a, b = first_data["values"][name], second_data["values"][name]
        vd = np.interp(x, yb, b)-np.interp(x, ya, a)
        ld = (np.interp(x, yb, second_data["values"]["optimal"]-b)
              - np.interp(x, ya, first_data["values"]["optimal"]-a))
        ad = (np.interp(ax, yb[1:-1], second_data["actions"][name])
              - np.interp(ax, ya[1:-1], first_data["actions"][name]))
        center_a = np.abs(x) <= 1.0
        center_b = np.abs(ax) <= 1.0
        result["methods"][name] = {
            "value_common_domain": summary_metric(vd, x),
            "value_core": summary_metric(vd[center_a], x[center_a]),
            "policy_loss_common_domain": summary_metric(ld, x),
            "policy_loss_core": summary_metric(ld[center_a], x[center_a]),
            "action_common_interior": summary_metric(ad, ax),
            "action_core": summary_metric(ad[center_b], ax[center_b]),
            "five_state_value_changes": [float(np.interp(s, yb, b)-np.interp(s, ya, a))
                                         for s in INITIAL_STATES],
        }
    return result


def sci(value):
    if value == 0:
        return "0"
    base, exponent = f"{value:.2e}".split("e")
    return "$"+base+r"\times10^{"+str(int(exponent))+"}$"


def tables(result, output):
    rows = result["records"]
    labels = {"optimal": "Howard", "nbo": "NBO", "dpo": "DPO",
              "linear": "Affine", "anchor": "Anchor"}
    lines = [r"\begin{table}[p]", r"\centering\small\setlength{\tabcolsep}{3pt}",
             r"\caption{Scalar reference: equation residuals and Howard convergence}",
             r"\label{tab:r14-reference-residuals}",
             r"\begin{tabular}{rrrrrrr}", r"\toprule",
             r"$n_y$ & $n_t$ & $L$ & HJB residual & Linear residual & Iter./step & Replay error \\",
             r"\midrule"]
    for row in rows:
        m = row["methods"]
        lines.append(f"{row['nx']} & {row['nt']} & {row['L']:g} & "
                     + sci(row["howard"]["max_hjb_residual"]) + " & "
                     + sci(max(v["max_linear_equation_residual"] for v in m.values())) + " & "
                     + f"{row['howard']['iterations_min']}--{row['howard']['iterations_max']} & "
                     + sci(max(v["max_abs_difference"] for v in row["array_comparisons"].values())) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\par\medskip",
                  r"\begin{minipage}{0.97\textwidth}\footnotesize",
                  r"Residuals are maxima over every interior state and every time step. The linear column also includes every Howard linear solve. All time steps satisfy the original $10^{-11}$ value-iterate stopping rule. Replay error is the largest absolute discrepancy across all original arrays; it is a floating-point reproducibility check, not an economic approximation error.",
                  r"\end{minipage}", r"\end{table}", "",
                  r"\begin{table}[p]", r"\centering\small\setlength{\tabcolsep}{3pt}",
                  r"\caption{Scalar fixed-policy residuals and action-bound frequencies}",
                  r"\label{tab:r14-reference-policies}",
                  r"\begin{tabular}{lrrrrr}", r"\toprule",
                  r"Grid $(n_y,n_t,L)$ & NBO & DPO & Affine & Anchor & Max. bound freq. \\",
                  r"\midrule"])
    for row in rows:
        frequency = max(sum(row["methods"][name]["bound_frequencies"]["all_interior_time_nodes"][key]
                            for key in ("lower_bound_frequency", "upper_bound_frequency")) for name in METHODS)
        lines.append(f"$({row['nx']},{row['nt']},{row['L']:g})$ & "
                     + " & ".join(sci(row["methods"][name]["max_linear_equation_residual"])
                                  for name in METHODS[1:]) + f" & {100*frequency:.2f}" + r"\% \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\par\medskip",
                  r"\begin{minipage}{0.97\textwidth}\footnotesize",
                  r"Method columns give maximum fixed-policy equation residuals. The last column is the largest bound frequency among the five policies, counting either endpoint of the unchanged economic action interval at all interior state--time nodes, with absolute tolerance $10^{-12}$. These are unweighted node frequencies, not visitation probabilities. Every imposed Dirichlet boundary value is satisfied by construction; its error relative to the unbounded economy is not enclosed. Method-specific counts, denominators, action ranges, time-zero actions and residual traces are retained in the diagnostic files.",
                  r"\end{minipage}", r"\end{table}"])
    (output / "table_reference_diagnostics.tex").write_text("\n".join(lines)+"\n")
    lines = [r"\begin{table}[p]", r"\centering\small\setlength{\tabcolsep}{3pt}",
             r"\caption{Scalar finite-grid policy losses at five initial states}",
             r"\label{tab:r14-reference-five-states}",
             r"\begin{tabular}{lrrrrr}", r"\toprule",
             r"Grid $(n_y,n_t,L)$ & $y_0$ & NBO & DPO & Affine & Anchor \\", r"\midrule"]
    for gi, row in enumerate(rows):
        if gi:
            lines.append(r"\midrule")
        for i, sample in enumerate(row["five_initial_states"]):
            grid_label = f"$({row['nx']},{row['nt']},{row['L']:g})$" if i == 0 else ""
            lines.append(grid_label+f" & {sample['initial_log_capital']:g} & "
                         + " & ".join(sci(sample["policy_losses"][name]) for name in METHODS[1:]) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\par\medskip",
                  r"\begin{minipage}{0.97\textwidth}\footnotesize",
                  r"Entries are the Howard grid value minus the value of the unchanged stored feedback policy, with common asymptotic Dirichlet data. Values at the five stated initial log-capital levels use linear interpolation of time-zero nodal values when necessary. No policy is refitted or chosen using this table. These are scalar finite-grid losses; they do not estimate the optimum in dimensions 10, 20 or 50.",
                  r"\end{minipage}", r"\end{table}"])
    (output / "table_reference_losses.tex").write_text("\n".join(lines)+"\n")
    lines = [r"\begin{table}[p]", r"\centering\small\setlength{\tabcolsep}{3pt}",
             r"\caption{Scalar value and policy changes under refinement}",
             r"\label{tab:r14-reference-refinement}",
             r"\begin{tabular}{llrrrr}", r"\toprule",
             r"Comparison & Policy & Core value & Core action & Core loss & Common value \\", r"\midrule"]
    for j, comparison in enumerate(result["refinements"]):
        if j:
            lines.append(r"\midrule")
        for i, name in enumerate(METHODS):
            m = comparison["methods"][name]
            title = [r"$401\to801$, $L=6$", r"$801\to1601$, $L=6$", r"$L=6\to8$, $n_y=1601$"][j] if i == 0 else ""
            lines.append(title+" & "+labels[name]+" & "
                         + " & ".join(sci(m[key]["max_abs"]) for key in (
                             "value_core", "action_core", "policy_loss_core", "value_common_domain")) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\par\medskip",
                  r"\begin{minipage}{0.97\textwidth}\footnotesize",
                  r"Entries are maximum absolute changes in values, actions or policy losses. The first three numerical columns use time-zero nodes with $|y|\le1$; the final column uses the full common state interval. The second grid is linearly interpolated at nodes of the first. Policy loss is $\ell=V^{\mathrm H}-V^m$. The first two comparisons halve both state spacing and time step. The last expands the domain at fixed $n_y,n_t$, changing state spacing from $0.0075$ to $0.01$; it is joint domain/spacing sensitivity and does not isolate boundary truncation error. Frozen-policy action changes arise only from interpolation and floating-point evaluation. Full common-interior action changes and their locations are archived.",
                  r"\end{minipage}", r"\end{table}"])
    (output / "table_reference_refinement.tex").write_text("\n".join(lines)+"\n")


SCOPE_NOTE = r"""\subsection{The scalar reference and its residual account}
\label{sec:r14-scalar-account}

The scalar reference isolates policy evaluation and policy improvement in a
nonlinear member of the coupled-capital family. It uses the three stored scalar
actors selected in the original experiment and the analytical anchor, without
retraining. The four state--time--domain specifications are
$(401,256,6)$, $(801,512,6)$, $(1601,1024,6)$ and $(1601,1024,8)$, where the
last coordinate is the half-width $L$ of the log-capital interval. All model
coefficients, action limits, terminal values and boundary data remain those
of the original reference. The diagnostic program checks the source and input
hashes before computation and verifies the input hashes again afterwards.

Write $\eta=(\sigma_{\mathrm{id}}^2+\sigma_{\mathrm{com}}^2)/2$,
$c=\alpha-\eta$, and $a$ for the adjustment-cost coefficient. The realized
scalar coupling entry is $B_{11}=1$. For scalar log capital $y$ and consumption
rate $m\in[\underline m,\overline m]=[0.02,2]$, the running payoff and drift are
\[
 u(y,m)=y+\log m-\frac a2m^2,
 \qquad \mu(y,m)=c+\beta\tanh y-m.
\]
The terminal payoff is $y$; the cross-sectional dispersion term vanishes in
one dimension. Put $t_k=kh$, $h=T/n_t$ and let $\delta$ be the uniform state
spacing. The original upwind generator is
\begin{align*}
 (L^m_\delta v)_i
 &=q_i^-(m)(v_{i-1}-v_i)+q_i^+(m)(v_{i+1}-v_i),\\
 q_i^-&=\frac{\eta}{\delta^2}+\frac{(-\mu_i)^+}{\delta},\\
 q_i^+&=\frac{\eta}{\delta^2}+\frac{\mu_i^+}{\delta}.
\end{align*}
Both coefficients are nonnegative. A fixed-policy backward step solves
\[
 \frac{v_i^k-v_i^{k+1}}{h}+\rho v_i^k
 -(L^{m_i^k}_\delta v^k)_i-u(y_i,m_i^k)=0
\]
at every interior node. Boundary values enter neighboring differences exactly
once. In particular, residuals are evaluated in this original equation,
not by subtracting a boundary-adjusted right-hand side after reintroducing
the boundary terms.

For Howard improvement, the Hamiltonian depending on $m$ is
\[
 \log m-\frac a2m^2+(d_i-m)^+p_i^f+(d_i-m)^-p_i^b,
\]
where
\[
 d_i=c+\beta\tanh y_i,\qquad
 p_i^f=\frac{v_{i+1}-v_i}{\delta},\qquad
 p_i^b=\frac{v_i-v_{i-1}}{\delta},
\]
where $z^-=\min(z,0)$. On each of the intervals cut by $m=d_i$, the
objective is strictly concave. Its unconstrained maximizer has the form
$2/(p+\sqrt{p^2+4a})$, with the algebraically equivalent stable expression
used when $p<0$. Clipping this root to each nonempty interval and comparing
the two attained values gives the global scalar action maximum for the
upwind Hamiltonian. Thus the reported HJB residual uses the full economic
action interval, without action-grid enumeration or a neural critic.

The imposed boundary functions have the form
$b_\pm(t)=\pm Lw(t)+Q_\pm(t)$, where
\[
 w(t)=\frac{1-e^{-\rho(T-t)}}{\rho}+e^{-\rho(T-t)},\qquad
 \overline m(t)=\frac{2}{w(t)+\sqrt{w(t)^2+4a}},
\]
and
\[
 Q_\pm(t)=\int_t^T e^{-\rho(s-t)}
 \left[\log\overline m(s)-\frac a2\overline m(s)^2
       +w(s)\{c\pm\beta-\overline m(s)\}\right]ds.
\]
The original cumulative-trapezoid rule and time interpolation evaluate these
functions. They represent asymptotic boundary data shared by all policies;
they are not independently verified exact boundary values for each learned
policy in the unbounded economy. Their satisfaction at grid endpoints is
an algebraic check, not a bound on economic boundary bias.

For the optimized grid value, define the original-equation HJB defect
\[
 r_i^k=\frac{v_i^k-v_i^{k+1}}{h}+\rho v_i^k
       -\max_m\{u(y_i,m)+(L^m_\delta v^k)_i\}.
\]
For a fixed policy, omit the maximization and use its stored feedback action.
The diagnostic files retain the maximum residual at every time step, the
linear residual of every Howard evaluation, every iterate difference, and
the iteration count. The original stopping rule is an iterate difference
below $10^{-11}$, with a cap of 100 iterations. A separate Howard check
evaluates $\|\mathcal T_k(v^k)-v^k\|_\infty/h$, where $\mathcal T_k$
solves the linear system for the greedy policy selected from $v^k$.

The significance of these residuals can be stated directly. Let
$\widetilde v$ be the exact solution of the same finite-grid backward
equations, with the same frozen policy (or the same Bellman operator),
terminal data and boundary data, and let $v$ be the approximate sequence
whose defect is $r$. In exact arithmetic, the fixed-policy matrix has
positive diagonal, nonpositive
off-diagonal entries, and row sums at least $h^{-1}+\rho$ after boundary
elimination. The discrete maximum principle therefore yields
\[
 \|\widetilde v^k-v^k\|_\infty
 \le \frac{\|\widetilde v^{k+1}-v^{k+1}\|_\infty+hR_k}{1+\rho h}
\]
whenever the boundary data agree and $\|r^k\|_\infty\le R_k$.
The same estimate holds for the Bellman step: at a positive maximum of the
difference, select an action maximizing the Hamiltonian of the upper
candidate and apply the fixed-action maximum principle; interchange the
candidates for the negative part. With exact common terminal data this gives
\[
 \|\widetilde v^0-v^0\|_\infty
 \le\sum_{k=0}^{n_t-1}\frac{hR_k}{(1+\rho h)^{k+1}}
 \le \frac{\max_k R_k}{\rho}\{1-(1+\rho h)^{-n_t}\}.
\]
The archived propagation diagnostic substitutes the observed floating-point
residuals in this formula. These residuals are not outward-rounded enclosures,
so that substitution is a numerical diagnostic rather than a certified bound.
The estimate concerns the finite-grid equations with the prescribed boundary
data; it does not include consistency, state interpolation or boundary bias.

The tables report all four grids, the five initial states
$y_0\in\{-1,-0.5,0,0.5,1\}$, the policies' action-bound frequencies, and
changes in values, optimal actions and policy losses. Initial-state values
are linearly interpolated from nodal time-zero values. Bound frequencies
use an absolute tolerance of $10^{-12}$ and count equally weighted interior
state--time nodes; they are not occupation probabilities. The first two grid
comparisons halve both $h$ and $\delta$. Increasing $L$ from 6 to 8 at fixed
$(n_y,n_t)=(1601,1024)$ changes $\delta$ from 0.0075 to 0.01. This comparison
measures joint domain and spacing sensitivity, not boundary truncation error
in isolation. Full common-domain changes and their locations accompany the
central-region summaries.

The scalar calculation supplies an independent finite-grid benchmark for
nonlinear feedback, with a reproducible algebraic error account. In the
10-, 20- and 50-dimensional economies, cross-sectional dispersion, the
coupling matrix and the covariance structure remain economically active.
Moreover, this scalar benchmark evaluates Markov feedback, whereas the
continuous-time deployment theorem specifies a randomized controller with
innovation history. Scalar reference losses therefore have their stated
one-dimensional meaning; multidimensional conclusions rely on the separate
multidimensional policy comparisons and certification arguments.
"""

SUPPLEMENT_WRAPPER = r"""% The main manuscript already contains the residual/convergence tables.
% Do not include table_reference_diagnostics.tex again in this wrapper.
\section{Independent scalar reference diagnostics}
\label{sec:r14-reference-supplement}
\input{revisions/2026-10-04-r14/results/reference/reference_scope.tex}
\input{revisions/2026-10-04-r14/results/reference/table_reference_losses.tex}
\input{revisions/2026-10-04-r14/results/reference/table_reference_refinement.tex}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--reference-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    repo, reference_dir, output = (p.resolve() for p in (
        args.repo, args.reference_dir, args.output_dir))
    if output == reference_dir or output.is_relative_to(reference_dir):
        raise RuntimeError("Output must not overwrite or enter the original reference directory")
    output.mkdir(parents=True, exist_ok=True)
    source_files = check_source(repo)
    sys.path.insert(0, str(repo / "revisions/2026-10-04-r12/code"))
    ref = importlib.import_module("reference")
    torch.set_default_dtype(torch.float64)
    torch.set_num_threads(1)
    meta = json.loads((reference_dir / "REFERENCE.json").read_text())
    if meta["source_commit"] != SOURCE_COMMIT:
        raise RuntimeError("Reference source is not the preserved primary source")
    observed_grids = tuple((r["nx"], r["nt"], r["L"]) for r in meta["records"])
    if observed_grids != GRIDS:
        raise RuntimeError("Expected exactly the four original announced grids in order")
    names = ["REFERENCE.json", "ENVIRONMENT.json"]
    for row in meta["records"]:
        filename = row["id"]+".npz"
        if sha(reference_dir / filename) != row["raw_sha256"]:
            raise RuntimeError(f"Original reference digest mismatch: {filename}")
        names.extend([filename, row["id"]+".json"])
    actors = {}
    actor_provenance = []
    for method in METHODS[1:4]:
        fit = next(f for f in meta["fits"] if f["method"] == method)
        filename = fit["id"]+".pt"
        if fit["dimension"] != 1 or sha(reference_dir / filename) != fit["weights_sha256"]:
            raise RuntimeError(f"Frozen scalar actor identity mismatch: {filename}")
        actor, _, state = ref.old.load(reference_dir / filename)
        if state["dimension"] != 1 or state["method"] != method:
            raise RuntimeError(f"Stored actor metadata mismatch: {filename}")
        actor.eval()
        actors[method] = actor
        names.append(filename)
        actor_provenance.append({"method": method, "file": filename,
                                 "sha256": sha(reference_dir / filename),
                                 "selected_iteration": fit["selected_iteration"]})
    class Anchor(torch.nn.Module):
        def forward(self, x):
            return ref.old.schedule(x[:, :1])
    actors["anchor"] = Anchor()
    before = {name: sha(reference_dir / name) for name in names}
    rows, arrays = [], []
    for record in meta["records"]:
        row, data = replay(record, actors, ref, reference_dir, output)
        rows.append(row); arrays.append(data)
    refinements = [refinement(rows[i], rows[i+1], arrays[i], arrays[i+1]) for i in range(3)]
    after = {name: sha(reference_dir / name) for name in names}
    if before != after:
        raise RuntimeError("Original reference input changed during replay")
    result = {
        "revision": "R14", "purpose": "R12 referee M8 frozen-policy scalar diagnostics",
        "source_commit": SOURCE_COMMIT, "source_files": source_files,
        "diagnostic_program_sha256": sha(__file__),
        "source_reference_repository_path": "revisions/2026-10-04-r12/results/reference",
        "original_input_sha256": before, "original_inputs_unchanged": before == after,
        "frozen_actor_provenance": actor_provenance,
        "model_parameters": ref.P, "scalar_coupling": float(ref.old.coupling(1)[0, 0]),
        "initial_states": INITIAL_STATES.tolist(),
        "replay_tolerance": {"absolute": REPLAY_ATOL, "relative": REPLAY_RTOL,
            "meaning": "arraywise abs(replay-original) <= absolute + relative*abs(original); floating-point replay, not a model error bound"},
        "action_bound_absolute_tolerance": BOUND_ATOL,
        "howard_value_update_tolerance": HOWARD_TOL, "howard_iteration_cap": MAX_HOWARD,
        "runtime": {"python": platform.python_version(), "platform": platform.platform(),
            "numpy": np.__version__, "scipy": scipy.__version__, "torch": torch.__version__,
            "torch_threads": torch.get_num_threads(),
            "thread_environment": {name: os.environ.get(name) for name in (
                "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS")}},
        "records": rows, "refinements": refinements,
        "all_original_arrays_reproduced": all(r["all_replayed_arrays_match"] for r in rows),
        "all_howard_steps_converged": all(r["howard"]["all_steps_converged"] for r in rows),
        "all_howard_iteration_counts_match": all(r["howard"]["iterations_match_original"] for r in rows),
        "scope": "One-state Markov-feedback finite-grid HJB/fixed-policy diagnostics with the original shared asymptotic Dirichlet boundaries; no neural critic enters the solve. No new fitting or model changes. Spatial/time consistency and true boundary bias are not enclosed. The domain expansion also changes dx. Scalar results do not certify 10-, 20-, or 50-dimensional value, costate, policy error, or randomized history-controller performance.",
        "residual_scope": "Floating-point equation residuals and their comparison-principle propagation are diagnostics, not outward-rounded certified enclosures.",
    }
    write_json(output / "REFERENCE_DIAGNOSTICS.json", result)
    tables(result, output)
    (output / "reference_scope.tex").write_text(SCOPE_NOTE)
    (output / "reference_supplement.tex").write_text(SUPPLEMENT_WRAPPER)
    manifest = {"source_commit": SOURCE_COMMIT,
                "diagnostic_program_sha256": result["diagnostic_program_sha256"],
                "original_inputs": before,
                "outputs": {p.name: sha(p) for p in sorted(output.iterdir())
                            if p.is_file() and p.name != "MANIFEST.json"}}
    write_json(output / "MANIFEST.json", manifest)
    if not (result["all_original_arrays_reproduced"]
            and result["all_howard_steps_converged"]
            and result["all_howard_iteration_counts_match"]):
        raise SystemExit("Replay/convergence gate failed; diagnostics retained without altering originals")
    print(json.dumps({"all_original_arrays_reproduced": True,
                      "original_inputs_unchanged": True,
                      "output": str(output)}), flush=True)


if __name__ == "__main__":
    main()
