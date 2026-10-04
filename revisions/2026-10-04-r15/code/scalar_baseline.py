"""Classical scalar HJB training, policy deployment and independent evaluation.

The one-state member has exactly the capital model's primitives, utility,
terminal value, Brownian variance and action bounds.  The monotone implicit
Howard solver now learns and saves a policy at every time and state node.  Its
interpolated policy is then deployed on fresh common diffusion paths, alongside
saved neural policies.  Thus it is a training comparator, not only an evaluator
of neural snapshots.  Domain/grid refinement and Monte Carlo standard errors
are explicitly numerical diagnostics, not unbounded-domain error certificates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import resource
import re
import time

from scipy.integrate import cumulative_trapezoid
from scipy.linalg import solve_banded

from baselines import (P, old, torch, np, ROOT, R15, legacy, source_commit, write_json,
                       file_sha256, load_policy)
from interval_certificate import I, log_i, tanh_i


def schedule_numpy(t):
    t = np.asarray(t)
    e = np.exp(-P["discount"] * (P["T"] - t))
    w = -np.expm1(-P["discount"] * (P["T"] - t)) / P["discount"] + e
    return 2. / (w + np.sqrt(w * w + 4. * P["adjustment"]))


def action_bounds(t, epsilon=None):
    if epsilon is None:
        return float(P["lower"]), float(P["upper"])
    center = float(schedule_numpy(t))
    lo, hi = center - epsilon, center + epsilon
    if not (P["lower"] <= lo < hi <= P["upper"]):
        raise ValueError("the declared scalar tube must lie in the primitive action box")
    return lo, hi


def scalar_root(p):
    """Positive root of 1/m - zeta*m = p, avoiding cancellation at p < 0."""
    p = np.asarray(p)
    disc = np.sqrt(p * p + 4. * P["adjustment"])
    return np.where(p >= 0., 2. / (p + disc), (disc - p) / (2. * P["adjustment"]))


def best_action(v, y, t, epsilon=None):
    """Exact maximizer of the positive-upwind discrete Hamiltonian.

    The drift changes sign at m=d0(y).  The forward and backward finite
    differences therefore define separate concave branches; both feasible
    branch optima must be compared.  A centered derivative is not substituted.
    """
    dx = y[1] - y[0]
    pf, pb = np.diff(v)[1:] / dx, np.diff(v)[:-1] / dx
    variance = P["idiosyncratic_sigma"] ** 2 + P["common_sigma"] ** 2
    d0 = P["productivity"] - variance / 2. + P["coupling"] * np.tanh(y[1:-1])
    lo, hi = action_bounds(t, epsilon)
    split = np.clip(d0, lo, hi)
    forward = np.clip(scalar_root(pf), lo, split)
    backward = np.clip(scalar_root(pb), split, hi)

    def hamiltonian(m):
        drift = d0 - m
        return (np.log(m) - P["adjustment"] * m * m / 2.
                + np.maximum(drift, 0.) * pf + np.minimum(drift, 0.) * pb)

    hf = np.where(d0 >= lo, hamiltonian(forward), -np.inf)
    hb = np.where(d0 <= hi, hamiltonian(backward), -np.inf)
    return np.where(hf >= hb, forward, backward)


def rates(y, m):
    dx = y[1] - y[0]
    variance = P["idiosyncratic_sigma"] ** 2 + P["common_sigma"] ** 2
    drift = P["productivity"] - variance / 2. + P["coupling"] * np.tanh(y[1:-1]) - m
    diffusion = variance / (2. * dx * dx)
    return diffusion + np.maximum(-drift, 0.) / dx, diffusion + np.maximum(drift, 0.) / dx


def equation_residual(v, vnext, y, m, h):
    low, high = rates(y, m)
    flow = y[1:-1] + np.log(m) - P["adjustment"] * m * m / 2.
    return ((v[1:-1] - vnext[1:-1]) / h + P["discount"] * v[1:-1]
            - low * (v[:-2] - v[1:-1]) - high * (v[2:] - v[1:-1]) - flow)


def grid_interval_data(y):
    """Fixed exact binary64 grid data, with elementary-function enclosures."""
    variance = I(P["idiosyncratic_sigma"]).square() + I(P["common_sigma"]).square()
    return dict(dx=I(float(y[1] - y[0])), diffusion=variance / 2.,
                drift=I(P["productivity"]) - variance / 2.
                + I(P["coupling"]) * tanh_i(I(y[1:-1])))


def equation_residual_enclosure(v, vnext, y, m, h, t, epsilon=None, data=None):
    """Enclose the *maximized* exact finite-grid Bellman residual.

    The grid coordinates, common spacing, time step, boundary values and
    declared action endpoints are exact binary64 inputs to this algebraic
    problem.  log and tanh are evaluated with the inherited outward kernel.
    Each upwind branch is concave in m.  Its tangent at any point bounds its
    maximum by the larger endpoint tangent value.  Enlarging a branch by the
    interval uncertainty in its drift-sign endpoint preserves the upper bound.
    An arbitrary feasible action gives a lower bound on the maximum.  Thus
    rounding in the approximate analytic maximizer is enclosed as well.
    """
    data = grid_interval_data(y) if data is None else data
    dx, drift, eta = data["dx"], data["drift"], data["diffusion"]
    pf = (I(v[2:]) - I(v[1:-1])) / dx
    pb = (I(v[1:-1]) - I(v[:-2])) / dx
    lo, hi = action_bounds(t, epsilon)
    if np.any(m < lo) or np.any(m > hi):
        raise ValueError("residual lower-witness action is infeasible")

    def tangent_upper(slope, left, right):
        valid = left <= right
        # Invalid branches get an arbitrary nonempty dummy interval for the
        # interval operations and are excluded from the subsequent maximum.
        safe_right = np.maximum(left, right)
        proposed = scalar_root((slope.lo + slope.hi) / 2.)
        point = np.maximum(left, np.minimum(safe_right, proposed))
        a = I(point)
        value = log_i(a) - I(P["adjustment"]) * a.square() / 2. + (drift - a) * slope
        derivative = 1. / a - I(P["adjustment"]) * a - slope
        gain = np.maximum(0., np.maximum((derivative * (I(left) - a)).hi,
                                         (derivative * (I(safe_right) - a)).hi))
        upper = (I(value.hi) + I(gain)).hi
        return np.where(valid, upper, -np.inf)

    forward_upper = tangent_upper(pf, np.full_like(v[1:-1], lo), np.minimum(hi, drift.hi))
    backward_upper = tangent_upper(pb, np.maximum(lo, drift.lo), np.full_like(v[1:-1], hi))
    max_upper = np.maximum(forward_upper, backward_upper)
    actual_drift = drift - I(m)
    positive = I(np.maximum(0., actual_drift.lo), np.maximum(0., actual_drift.hi))
    negative = I(np.minimum(0., actual_drift.lo), np.minimum(0., actual_drift.hi))
    witness = (log_i(I(m)) - I(P["adjustment"]) * I(m).square() / 2.
               + positive * pf + negative * pb)
    maximum = I(witness.lo, max_upper)
    laplacian = (I(v[2:]) - 2. * I(v[1:-1]) + I(v[:-2])) / dx.square()
    residual = ((I(v[1:-1]) - I(vnext[1:-1])) / I(h) + I(P["discount"]) * I(v[1:-1])
                - eta * laplacian - I(y[1:-1]) - maximum)
    return residual, maximum


def implicit_policy_step(vnext, y, m, h, boundary):
    low, high = rates(y, m)
    band = np.zeros((3, len(m)))
    band[1] = 1. / h + P["discount"] + low + high
    band[0, 1:] = -high[:-1]
    band[2, :-1] = -low[1:]
    rhs = vnext[1:-1] / h + y[1:-1] + np.log(m) - P["adjustment"] * m * m / 2.
    rhs[0] += low[0] * boundary[0]
    rhs[-1] += high[-1] * boundary[1]
    vint = solve_banded((1, 1), band, rhs, check_finite=True)
    return np.r_[boundary[0], vint, boundary[1]]


def asymptotic_boundaries(times, L):
    """Declared affine far-state boundary data, shared across grid refinements.

    tanh(y) tends to +/-1.  These are the corresponding infinite-far-state
    values, evaluated at +/-L.  At finite L they are boundary approximations,
    not the true unrestricted model's values at the boundary.
    """
    fine = np.linspace(0., P["T"], max(8193, 8 * len(times) + 1))
    rho = P["discount"]
    e = np.exp(-rho * (P["T"] - fine))
    w = -np.expm1(-rho * (P["T"] - fine)) / rho + e
    m = schedule_numpy(fine)
    c = P["productivity"] - (P["idiosyncratic_sigma"] ** 2 + P["common_sigma"] ** 2) / 2.
    result = []
    for sign in (-1., 1.):
        integrand = np.exp(-rho * fine) * (
            np.log(m) - P["adjustment"] * m * m / 2.
            + w * (c + sign * P["coupling"] - m))
        cumulative = cumulative_trapezoid(integrand, fine, initial=0.)
        q = np.exp(rho * fine) * (cumulative[-1] - cumulative)
        result.append(np.interp(times, fine, sign * L * w + q))
    return result


def train_grid(nx, nt, L, out, *, epsilon=None, tolerance=1e-11,
               max_policy_iterations=100, method_fingerprint=None):
    """Train and save a deployable monotone-grid policy, charging every solve."""
    start = time.perf_counter()
    if nx < 5 or nt < 1 or L <= 0 or tolerance <= 0:
        raise ValueError("invalid scalar discretization")
    if float(old.coupling(1)[0, 0]) != 1.:
        raise ValueError("the scalar comparator is pinned to the declared B_11=1 member")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    mode = "full" if epsilon is None else f"tube{epsilon:g}"
    ident = f"scalar_howard_{mode}_nx{nx}_nt{nt}_L{L:g}"
    if method_fingerprint is None:
        specification = dict(method_id="scalar_howard", primitives=dict(P),
                             nx=nx, nt=nt, L=float(L), epsilon=epsilon,
                             tolerance=tolerance, max_policy_iterations=max_policy_iterations,
                             deployment="bilinear_time_state_with_schedule_extension")
        method_fingerprint = hashlib.sha256(json.dumps(
            specification, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    y, times = np.linspace(-L, L, nx), np.linspace(0., P["T"], nt + 1)
    h = P["T"] / nt
    boundary = asymptotic_boundaries(times, L)
    actions = np.empty((nt + 1, nx))
    value_grid = np.empty((nt + 1, nx))
    actions[-1] = float(schedule_numpy(P["T"]))
    v = y.copy()  # g(y)=y in the exact scalar member (dispersion is zero).
    value_grid[-1] = v
    equation_errors = np.zeros(nt)
    enclosed_errors = np.zeros(nt)
    hamiltonian_enclosure_widths = np.zeros(nt)
    howard_iterations = np.zeros(nt, dtype=np.int64)
    total_solves, converged = 0, True
    interval_data = grid_interval_data(y)
    interval_seconds = 0.
    setup_seconds = time.perf_counter() - start
    solve_start = time.perf_counter()
    for k in range(nt - 1, -1, -1):
        vn = v.copy()
        v = vn.copy()
        for iteration in range(1, max_policy_iterations + 1):
            m = best_action(v, y, times[k], epsilon)
            updated = implicit_policy_step(vn, y, m, h, (boundary[0][k], boundary[1][k]))
            total_solves += 1
            difference = float(np.max(abs(updated - v)))
            v = updated
            if difference <= tolerance:
                break
        else:
            converged = False
        howard_iterations[k] = iteration
        m = best_action(v, y, times[k], epsilon)
        equation_errors[k] = float(np.max(abs(equation_residual(v, vn, y, m, h))))
        interval_start = time.perf_counter()
        enclosed, max_h = equation_residual_enclosure(v, vn, y, m, h, times[k], epsilon, interval_data)
        enclosed_errors[k] = float(np.max(enclosed.absmax()))
        hamiltonian_enclosure_widths[k] = float(np.max((I(max_h.hi) - I(max_h.lo)).hi))
        interval_seconds += time.perf_counter() - interval_start
        actions[k, 1:-1] = m
        actions[k, (0, -1)] = float(schedule_numpy(times[k]))
        value_grid[k] = v
    solve_seconds = time.perf_counter() - solve_start
    if not (np.isfinite(v).all() and np.isfinite(actions).all()):
        raise FloatingPointError("nonfinite scalar candidate")
    # For identical grid, terminal and boundary data, the M-matrix comparison
    # gives e_0 <= sum_k h ||r_k||_infty / (1+rho*h)^(k+1).
    contraction = I(0.)
    for k in range(nt - 1, -1, -1):
        contraction = (contraction + I(h) * I(enclosed_errors[k])) / (1. + I(P["discount"]) * I(h))
    contraction_error = float(contraction.hi)
    io_start = time.perf_counter()
    path = out / f"{ident}.npz"
    np.savez_compressed(path, state=y, time=times, action=actions,
                        value_t0=v, value_grid=value_grid,
                        max_equation_residual_by_time=equation_errors,
                        max_equation_residual_upper_by_time=enclosed_errors,
                        hamiltonian_max_enclosure_width_by_time=hamiltonian_enclosure_widths,
                        boundary_left=boundary[0], boundary_right=boundary[1],
                        action_lower_by_time=np.asarray([action_bounds(t, epsilon)[0] for t in times]),
                        action_upper_by_time=np.asarray([action_bounds(t, epsilon)[1] for t in times]),
                        howard_iterations=howard_iterations,
                        epsilon=np.array(np.nan if epsilon is None else epsilon))
    raw_hash = file_sha256(path)
    row = dict(id=ident, method="scalar_howard", method_id="scalar_howard",
               algorithm_id="scalar_howard", model_kind="scalar_policy_table",
               method_fingerprint=method_fingerprint, dimension=1, nx=nx, nt=nt,
               L=float(L), epsilon=epsilon, primitive_action_box=[P["lower"], P["upper"]],
               action_class="primitive_box" if epsilon is None else "common_schedule_tube",
               seconds=time.perf_counter() - start,
               stages=dict(setup_seconds=setup_seconds, solver_and_interval_audit_seconds=solve_seconds,
                           interval_residual_audit_seconds=interval_seconds,
                           policy_serialization_seconds=time.perf_counter() - io_start),
               tridiagonal_solves=total_solves,
               tridiagonal_unknowns_solved=total_solves * (nx - 2),
               greedy_node_evaluations=int((howard_iterations.sum() + nt) * (nx - 2)),
               time_state_policy_coefficients=int(actions.size),
               policy_array_bytes=int(actions.nbytes),
               value_audit_array_bytes=int(value_grid.nbytes),
               maximum_schedule_deviation=float(np.max(abs(actions - schedule_numpy(times)[:, None]))),
               primitive_action_bound_frequency=float(np.mean((actions <= P["lower"] + 1e-12)
                                                               | (actions >= P["upper"] - 1e-12))),
               peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               converged=bool(converged), maximum_howard_iterations=int(howard_iterations.max()),
               max_equation_residual=float(equation_errors.max()),
               max_equation_residual_upper=float(enclosed_errors.max()),
               max_hamiltonian_enclosure_width=float(hamiltonian_enclosure_widths.max()),
               finite_grid_solve_error_bound=contraction_error,
               center_value=float(np.interp(0., y, v)),
               value_at_initial_profiles={str(mu): float(np.interp(mu, y, v))
                                          for mu in [-1., -.5, 0., .5, 1.]},
               policy_path=path.name, policy_sha256=raw_hash,
               source_commit=source_commit(),
               deployment="bilinear interpolation in time and state; analytic schedule outside the state grid; primitive or declared tube clipping",
               error_scope="outward maximized-residual and M-matrix bound for the exact finite-grid equations with the declared binary64 grid/action/boundary inputs, under the inherited interval arithmetic contract; grid/domain and diffusion error remain distinct",
               training_scope="independent classical training; no neural policy, critic, validation score or final shock enters Howard iteration")
    write_json(out / f"{ident}.json", row)
    return row


class ScalarGridPolicy(torch.nn.Module):
    """Actual deployed feedback from the saved classical training candidate."""
    def __init__(self, path):
        super().__init__()
        with np.load(path) as data:
            self.register_buffer("state", torch.from_numpy(data["state"].copy()))
            self.register_buffer("time", torch.from_numpy(data["time"].copy()))
            self.register_buffer("action", torch.from_numpy(data["action"].copy()))
            epsilon = float(data["epsilon"])
        self.epsilon = None if math.isnan(epsilon) else epsilon
        if self.action.shape != (len(self.time), len(self.state)):
            raise ValueError("scalar table shape mismatch")
        self.nx, self.nt = len(self.state), len(self.time) - 1
        self.dx = float(self.state[1] - self.state[0])
        self.dt = float(self.time[1] - self.time[0])

    def forward(self, x):
        if x.shape[1] != 2:
            raise ValueError("a scalar policy requires (time, state)")
        t = x[:, 0].clamp(0., P["T"])
        y = x[:, 1]
        ut = t / self.dt
        it = torch.floor(ut).long().clamp(0, self.nt - 1)
        wt = (ut - it).clamp(0., 1.)
        uy = (y.clamp(float(self.state[0]), float(self.state[-1])) - self.state[0]) / self.dx
        iy = torch.floor(uy).long().clamp(0, self.nx - 2)
        wy = (uy - iy).clamp(0., 1.)
        first = (1. - wy) * self.action[it, iy] + wy * self.action[it, iy + 1]
        second = (1. - wy) * self.action[it + 1, iy] + wy * self.action[it + 1, iy + 1]
        m = ((1. - wt) * first + wt * second)[:, None]
        center = old.schedule(t[:, None])
        outside = ((y < self.state[0]) | (y > self.state[-1]))[:, None]
        m = torch.where(outside, center, m)
        if self.epsilon is None:
            return m.clamp(P["lower"], P["upper"])
        return torch.maximum(center - self.epsilon, torch.minimum(center + self.epsilon, m))


class SchedulePolicy(torch.nn.Module):
    def forward(self, x):
        return old.schedule(x[:, :1])


def evaluate_common_paths(policies, out, *, steps=2048, paths=8192,
                          seed=92515071, label="scalar_confirmation", brownian_base_steps=None,
                          initial_profiles=(-1., 0., 1.), policy_metadata=None):
    """Independent, equal-path evaluation of all deployed scalar candidates.

    Brownian increments are untruncated.  The returned standard errors concern
    these Euler feedback values conditional on all trained tables/weights.
    They contain neither grid-selection uncertainty nor continuous-time bias.
    """
    start = time.perf_counter()
    if paths < 2 or steps < 1 or not policies:
        raise ValueError("invalid scalar evaluation design")
    brownian_base_steps = steps if brownian_base_steps is None else int(brownian_base_steps)
    if brownian_base_steps < steps or brownian_base_steps % steps:
        raise ValueError("the Brownian base mesh must be an integer refinement")
    noise_substeps = brownian_base_steps // steps
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    policy_metadata = {} if policy_metadata is None else policy_metadata
    support = np.asarray(initial_profiles, dtype=np.float64)
    if support.ndim != 1 or len(support) < 1 or not np.isfinite(support).all():
        raise ValueError("invalid scalar initial profiles")
    initial_rng = np.random.default_rng(seed + 100004)
    ids = initial_rng.integers(0, len(support), size=paths)
    initial = support[ids]
    state = {name: initial.copy() for name in policies}
    value = {name: np.zeros(paths) for name in policies}
    forward_seconds = {name: 0. for name in policies}
    outside = {name: 0 for name in policies}
    saturation = {name: 0 for name in policies}
    h = P["T"] / steps
    variance = P["idiosyncratic_sigma"] ** 2 + P["common_sigma"] ** 2
    c = P["productivity"] - variance / 2.
    rng = np.random.default_rng(seed + 1)
    noise_hash = hashlib.sha256()
    for k in range(steps):
        z = np.zeros((paths, 2))
        for _ in range(noise_substeps):
            primitive_z = rng.standard_normal((paths, 2))
            noise_hash.update(primitive_z.tobytes())
            z += primitive_z / math.sqrt(noise_substeps)
        dw = math.sqrt(h) * (P["idiosyncratic_sigma"] * z[:, 0]
                             + P["common_sigma"] * z[:, 1])
        for name, policy in policies.items():
            yy = state[name]
            x = torch.from_numpy(np.c_[np.full(paths, k * h), yy])
            ts = time.perf_counter()
            with torch.no_grad():
                m = policy(x).detach().numpy().ravel()
            forward_seconds[name] += time.perf_counter() - ts
            if not np.isfinite(m).all():
                raise FloatingPointError(f"nonfinite scalar proposal: {name}")
            if ((m < P["lower"] - 1e-14) | (m > P["upper"] + 1e-14)).any():
                raise ValueError(f"infeasible scalar proposal: {name}")
            m = np.clip(m, P["lower"], P["upper"])
            saturation[name] += int(((m <= P["lower"] + 1e-12)
                                    | (m >= P["upper"] - 1e-12)).sum())
            if isinstance(policy, ScalarGridPolicy):
                outside[name] += int(((yy < float(policy.state[0]))
                                     | (yy > float(policy.state[-1]))).sum())
            value[name] += math.exp(-P["discount"] * k * h) * h * (
                np.log(m) + yy - P["adjustment"] * m * m / 2.)
            state[name] = yy + h * (c + P["coupling"] * np.tanh(yy) - m) + dw
    for name in policies:
        value[name] += math.exp(-P["discount"] * P["T"]) * state[name]
    policy_names = list(policies)
    raw = dict(initial_profile=ids, initial_state=initial,
               policy_names=np.asarray(policy_names),
               payoff=np.stack([value[name] for name in policy_names]),
               terminal_state=np.stack([state[name] for name in policy_names]))
    path = out / f"{label}.npz"
    np.savez_compressed(path, **raw)
    rows = []
    for name in policies:
        vv = value[name]
        metadata = policy_metadata.get(name, {})
        by_profile = []
        for index, initial_y in enumerate(support):
            conditional = vv[ids == index]
            by_profile.append(dict(initial_state=float(initial_y), paths=len(conditional),
                                   mean=float(conditional.mean()) if len(conditional) else None,
                                   monte_carlo_standard_error=float(conditional.std(ddof=1) / math.sqrt(len(conditional)))
                                   if len(conditional) > 1 else None))
        rows.append(dict(policy=name, mean=float(vv.mean()),
                         method_id=metadata.get("method_id", name),
                         method_fingerprint=metadata.get("method_fingerprint"),
                         policy_sha256=metadata.get("policy_sha256"),
                         monte_carlo_standard_error=float(vv.std(ddof=1) / math.sqrt(paths)),
                         by_initial_profile=by_profile,
                         deployment_forward_seconds=forward_seconds[name],
                         action_calls=steps, action_states=steps * paths,
                         outside_policy_grid_frequency=outside[name] / (steps * paths),
                         primitive_action_bound_frequency=saturation[name] / (steps * paths)))
    pairs = []
    for left_index, left in enumerate(policy_names):
        for right in policy_names[left_index + 1:]:
            diff = value[left] - value[right]
            by_profile = []
            for index, initial_y in enumerate(support):
                conditional = diff[ids == index]
                by_profile.append(dict(initial_state=float(initial_y), paths=len(conditional),
                                       mean=float(conditional.mean()) if len(conditional) else None,
                                       monte_carlo_standard_error=float(conditional.std(ddof=1) / math.sqrt(len(conditional)))
                                       if len(conditional) > 1 else None))
            pairs.append(dict(left=left, right=right, mean=float(diff.mean()),
                              by_initial_profile=by_profile,
                              monte_carlo_standard_error=float(diff.std(ddof=1) / math.sqrt(paths))))
    result = dict(id=label, dimension=1, paths=paths, steps=steps, seed=seed,
                  brownian_base_steps=brownian_base_steps,
                  normal_variates_generated=2 * paths * brownian_base_steps,
                  simulator_transitions=len(policies) * paths * steps,
                  initial_profiles=support.tolist(), initial_weights=[1. / len(support)] * len(support),
                  initial_index_hash=hashlib.sha256(ids.tobytes()).hexdigest(),
                  initial_state_hash=hashlib.sha256(initial.tobytes()).hexdigest(),
                  noise_sha256=noise_hash.hexdigest(), raw_sha256=file_sha256(path),
                  records=rows, paired_contrasts=pairs, seconds=time.perf_counter() - start,
                  source_commit=source_commit(),
                  scope="fresh common-path Euler evaluation of actually deployed classical and neural feedbacks; numerical conditional Monte Carlo errors, no continuous-time or unbounded-grid certificate")
    write_json(out / f"{label}.json", result)
    return result


def run(out, *, smoke=False, neural_paths=None, seed=None, protocol_path=None):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    protocol_path = R15 / "SCALAR_PROTOCOL.json" if protocol_path is None else Path(protocol_path)
    protocol = json.loads(protocol_path.read_text())
    if protocol["primitives"] != P:
        raise ValueError("scalar protocol must use the declared original-regime primitive dictionary")
    seed = protocol["evaluation_seed"] if seed is None else seed
    grids = [(101, 32, 6.)] if smoke else [
        (grid["nx"], grid["nt"], grid["L"]) for grid in protocol["grids"]]
    fits, policies = [], {"schedule": SchedulePolicy()}
    schedule_fingerprint = hashlib.sha256(json.dumps(
        dict(method_id="analytical_schedule", primitives=dict(P)), sort_keys=True).encode()).hexdigest()
    policy_metadata = {"schedule": dict(method_id="analytical_schedule",
                                        method_fingerprint=schedule_fingerprint)}
    for action_class in protocol["classical_action_classes"]:
        epsilon = action_class["epsilon"]
        for nx, nt, L in grids:
            row = train_grid(nx, nt, L, out, epsilon=epsilon,
                             tolerance=protocol["howard_value_tolerance"],
                             max_policy_iterations=protocol["maximum_policy_iterations_per_time_step"])
            fits.append(row)
            policies[row["id"]] = ScalarGridPolicy(out / row["policy_path"])
            policy_metadata[row["id"]] = {key: row[key] for key in
                                          ["method_id", "method_fingerprint", "policy_sha256"]}
    neural_records = []
    declared = {item["name"]: item for item in protocol["frozen_neural_candidates"]}
    if neural_paths is None:
        neural_paths = {name: ROOT / item["path"] for name, item in declared.items()}
    for name, path in neural_paths.items():
        if name in declared and file_sha256(path) != declared[name]["sha256"]:
            raise ValueError("frozen scalar neural snapshot hash mismatch: " + name)
        policy, _, metadata = load_policy(path)
        if metadata["dimension"] != 1:
            raise ValueError("a scalar neural comparison requires a dimension-one snapshot")
        if name in policies:
            raise ValueError("duplicate scalar comparison name")
        policies[name] = policy
        neural_records.append(dict(name=name, weights_sha256=file_sha256(path),
                                   method_id=declared[name]["method_id"] if name in declared else metadata.get("method_id", metadata["method"]),
                                   iteration=metadata.get("iteration"),
                                   provenance=declared.get(name)))
        neural_spec = dict(method_id=neural_records[-1]["method_id"],
                           weight_sha256=file_sha256(path),
                           source_commit=declared.get(name, {}).get("numerical_source_commit"))
        policy_metadata[name] = dict(method_id=neural_records[-1]["method_id"],
                                     policy_sha256=file_sha256(path),
                                     method_fingerprint=hashlib.sha256(json.dumps(
                                         neural_spec, sort_keys=True).encode()).hexdigest())
        neural_records[-1]["method_fingerprint"] = policy_metadata[name]["method_fingerprint"]
    # Both deployment meshes aggregate the same fine Brownian increments.
    # Their paired sensitivity is separate from the state/time training-grid
    # refinement and from independent Monte Carlo uncertainty at either mesh.
    evaluations = []
    for steps in ([64] if smoke else protocol["evaluation_steps"]):
        evaluations.append(evaluate_common_paths(
            policies, out, steps=steps, paths=128 if smoke else protocol["evaluation_paths"], seed=seed,
            label=f"scalar_confirmation_n{steps}",
            brownian_base_steps=64 if smoke else protocol["brownian_base_steps"],
            initial_profiles=protocol["initial_profiles"], policy_metadata=policy_metadata))
    grid_refinement = []
    for action_class in protocol["classical_action_classes"]:
        ordered = [row for row in fits if row["epsilon"] == action_class["epsilon"]]
        for left, right in zip(ordered[:-1], ordered[1:]):
            grid_refinement.append(dict(
                earlier=left["id"], later=right["id"],
                comparison="domain_at_fixed_mesh" if left["nt"] == right["nt"] else "joint_state_time_refinement",
                center_value_change=right["center_value"] - left["center_value"],
                value_change_at_initial_profiles={str(mu): right["value_at_initial_profiles"][str(mu)]
                                                  - left["value_at_initial_profiles"][str(mu)]
                                                  for mu in protocol["initial_profiles"]},
                earlier_training_seconds=left["seconds"], later_training_seconds=right["seconds"]))
    temporal_refinement = []
    for earlier, later in zip(evaluations[:-1], evaluations[1:]):
        for key in ["initial_state_hash", "initial_index_hash", "noise_sha256", "brownian_base_steps", "paths"]:
            if earlier[key] != later[key]:
                raise AssertionError("unpaired scalar deployment meshes: " + key)
        with np.load(out / (earlier["id"] + ".npz")) as first, np.load(out / (later["id"] + ".npz")) as second:
            if not np.array_equal(first["policy_names"], second["policy_names"]):
                raise AssertionError("different scalar policies on deployment meshes")
            changes = second["payoff"] - first["payoff"]
            names, ids = first["policy_names"].copy(), first["initial_profile"].copy()
        refinement_path = out / f"scalar_mesh_n{later['steps']}_minus_n{earlier['steps']}.npz"
        np.savez_compressed(refinement_path, policy_names=names, payoff_change=changes, initial_profile=ids)
        for index, name in enumerate(names):
            delta = changes[index]
            by_profile = []
            for profile, mu in enumerate(protocol["initial_profiles"]):
                conditional = delta[ids == profile]
                by_profile.append(dict(initial_state=mu, paths=len(conditional),
                                       mean=float(conditional.mean()),
                                       monte_carlo_standard_error=float(conditional.std(ddof=1) / math.sqrt(len(conditional)))))
            temporal_refinement.append(dict(policy=str(name), earlier_steps=earlier["steps"],
                                             later_steps=later["steps"], mean=float(delta.mean()),
                                             monte_carlo_standard_error=float(delta.std(ddof=1) / math.sqrt(len(delta))),
                                             by_initial_profile=by_profile,
                                             raw_sha256=file_sha256(refinement_path),
                                             scope="paired numerical deployment-mesh sensitivity; no time-discretization upper bound"))
    result = dict(classical_fits=fits, neural_candidates=neural_records,
                  evaluations=evaluations, source_commit=source_commit(),
                  grid_refinement=grid_refinement, deployment_mesh_refinement=temporal_refinement,
                  protocol_sha256=file_sha256(protocol_path),
                  stage="official_scalar_comparison" if (not smoke and re.fullmatch(r"[0-9a-f]{40}", source_commit()))
                  else "development_scalar_comparison",
                  comparison_scope="full-box classical training and a separately labelled matched-tube classical training frontier; neural candidates use their saved declared action class",
                  limitation="state-domain and mesh sensitivity do not supply a rigorous error bound for the unbounded scalar diffusion")
    write_json(out / "SCALAR_BASELINE.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--protocol", type=Path, default=R15 / "SCALAR_PROTOCOL.json")
    parser.add_argument("--neural-snapshot", action="append", default=[], metavar="NAME=PATH")
    args = parser.parse_args()
    candidates = dict(value.split("=", 1) for value in args.neural_snapshot) if args.neural_snapshot else None
    result = run(args.out, smoke=args.smoke, neural_paths=candidates, seed=args.seed,
                 protocol_path=args.protocol)
    print(json.dumps({"classical_fits": len(result["classical_fits"]),
                      "neural_candidates": len(result["neural_candidates"]),
                      "evaluation_meshes": len(result["evaluations"])}))
