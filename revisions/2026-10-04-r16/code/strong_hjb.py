"""Direct HJB baseline with exact tanh diffusion jets and residual-only selection.

No payoff simulation is performed by this module.  All economic
parameters are explicit: in particular horizon and terminal dispersion are not
inherited through legacy mutable module aliases.
"""
from __future__ import annotations

from collections import defaultdict
import copy
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np
import torch
from torch import nn

torch.set_default_dtype(torch.float64)
torch.set_num_threads(1)


def coupling(d):
    generator = np.random.default_rng(401 + d)
    b = generator.normal(size=(d, d))
    return torch.from_numpy(b / np.linalg.norm(b, axis=1, keepdims=True))


def schedule(t, params):
    e = torch.exp(-params["discount"] * (params["T"] - t))
    w = (1-e) / params["discount"] + e
    return 2 / (w + torch.sqrt(w*w + 4*params["adjustment"]))


def action_bounds(t, params, epsilon):
    center = schedule(t, params)
    return ((center-epsilon).clamp_min(params["lower"]),
            (center+epsilon).clamp_max(params["upper"]))


def mlp(inputs, width, outputs=1):
    result = nn.Sequential(nn.Linear(inputs, width), nn.Tanh(),
                           nn.Linear(width, width), nn.Tanh(),
                           nn.Linear(width, outputs))
    nn.init.zeros_(result[-1].weight)
    nn.init.zeros_(result[-1].bias)
    return result


def tanh_jet(net, x, sigma_i, sigma_c, *, trace=True):
    """Exact value, full input Jacobian, and spatial covariance contraction.

    The covariance is diag(0, sigma_i^2 I) plus sigma_c^2 (0,1)'(0,1).
    Propagation uses f'=1-f^2 and f''=-2 f (1-f^2).  Nothing stochastic is
    estimated.  The arithmetic graph remains differentiable in every weight.
    """
    n, inputs = x.shape
    a = x
    jacobian = torch.eye(inputs, dtype=x.dtype, device=x.device).expand(n, -1, -1)
    contraction = torch.zeros_like(x)
    for layer in net:
        if isinstance(layer, nn.Linear):
            a = layer(a)
            jacobian = torch.einsum("oi,nij->noj", layer.weight, jacobian)
            if trace:
                contraction = contraction @ layer.weight.T
        elif isinstance(layer, nn.Tanh):
            a = a.tanh()
            first = 1-a.square()
            if trace:
                spatial = jacobian[:, :, 1:]
                variance = sigma_i*sigma_i*spatial.square().sum(2)
                variance = variance + sigma_c*sigma_c*spatial.sum(2).square()
                contraction = first*contraction - 2*a*first*variance
            jacobian = first[:, :, None]*jacobian
        else:
            raise TypeError("exact jet requires an explicit Linear/Tanh network")
    return a, jacobian[:, 0, :], contraction


def scalar_first_jet(net, x):
    """Exact scalar input gradient by explicit reverse propagation.

    Deployment needs one scalar gradient, not a width-by-dimension Jacobian.
    This costs ordinary dense layer products and avoids the d-fold intermediate
    tensors needed only by the exact diffusion-trace training calculation.
    """
    value, history = x, []
    for layer in net:
        if isinstance(layer, nn.Linear):
            value = layer(value)
            history.append(("linear", layer.weight))
        elif isinstance(layer, nn.Tanh):
            value = value.tanh()
            history.append(("tanh", 1-value.square()))
        else:
            raise TypeError("explicit first jet requires Linear/Tanh layers")
    gradient = torch.ones_like(value)
    for kind, array in reversed(history):
        gradient = gradient@array if kind == "linear" else gradient*array
    return value, gradient


class ExactCritic(nn.Module):
    def __init__(self, d, params, width=32, time_width=16):
        super().__init__()
        self.d, self.params = int(d), dict(params)
        self.width, self.time_width = width, time_width
        self.time = mlp(1, time_width)
        self.space = mlp(d+1, width)

    def base(self, states):
        p = self.params
        t, y = states[:, :1], states[:, 1:]
        tau = p["T"]-t
        e = torch.exp(-p["discount"]*tau)
        w = (1-e)/p["discount"] + e
        mean = y.mean(1, keepdim=True)
        dispersion = (y-mean).square().mean(1, keepdim=True)
        return w*mean-p["CHI"]*e*dispersion

    def forward(self, states):
        return self.base(states)+(self.params["T"]-states[:, :1])*(
            self.time(states[:, :1])+self.space(states)/self.d)

    def jet(self, states, *, trace=True):
        p, d = self.params, self.d
        t, y = states[:, :1], states[:, 1:]
        tau = p["T"]-t
        e = torch.exp(-p["discount"]*tau)
        w = (1-e)/p["discount"]+e
        mean = y.mean(1, keepdim=True)
        centered = y-mean
        dispersion = centered.square().mean(1, keepdim=True)
        value_base = w*mean-p["CHI"]*e*dispersion
        time_base = (p["discount"]-1)*e*mean-p["CHI"]*p["discount"]*e*dispersion
        gradient_base = w/d-2*p["CHI"]*e*centered/d
        trace_base = -2*p["CHI"]*e*p["idiosyncratic_sigma"]**2*(1-1/d)
        tv, tj = scalar_first_jet(self.time, t)
        if trace:
            sv, sj, st = tanh_jet(self.space, states, p["idiosyncratic_sigma"],
                                 p["common_sigma"], trace=True)
        else:
            sv, sj = scalar_first_jet(self.space, states)
            st = None
        value = value_base+tau*(tv+sv/d)
        vt = time_base-tv-sv/d+tau*(tj+sj[:, :1]/d)
        gradient = gradient_base+tau*sj[:, 1:]/d
        contraction = trace_base+tau*st/d if trace else None
        return value, vt, gradient, contraction

    def metadata(self):
        return dict(critic_family="r16_exact_tanh_split", dimension=self.d,
                    width=self.width, time_width=self.time_width, params=self.params)


def greedy_newton(costate, t, params, epsilon, *, tolerance=2e-13,
                  max_newton=16, fallback_bisections=44):
    """Safeguarded vector root for the exact concave Hamiltonian maximizer.

    Solve z=mean clip(1/(d*p+adjustment*z), l, u).  The residual is strictly
    increasing, with derivative at least one; rowwise brackets are retained.
    The fallback is charged and returned, never silently hidden.
    """
    with torch.no_grad():
        low, high = action_bounds(t, params, epsilon)
        a, b = low.clone(), high.clone()
        q, k = costate.detach()*costate.shape[1], params["adjustment"]
        z = (a+b)/2
        iterations, fallback = 0, 0

        def at(point):
            den = q+k*point
            unconstrained = 1/den.clamp_min(1e-300)
            action = torch.where(den > 0, unconstrained, high.expand_as(q))
            action = torch.maximum(low, torch.minimum(high, action))
            free = (den > 0) & (unconstrained > low) & (unconstrained < high)
            f = point-action.mean(1, keepdim=True)
            df = 1+k*torch.where(free, unconstrained.square(), torch.zeros_like(q)).mean(1, keepdim=True)
            return action, f, df

        for _ in range(max_newton):
            action, residual, derivative = at(z)
            iterations += 1
            if residual.abs().max() <= tolerance:
                break
            active = residual.abs() > tolerance
            a = torch.where(active & (residual < 0), z, a)
            b = torch.where(active & (residual >= 0), z, b)
            candidate = z-residual/derivative
            inside = (candidate >= a) & (candidate <= b)
            z = torch.where(active, torch.where(inside, candidate, (a+b)/2), z)
        else:
            for _ in range(fallback_bisections):
                active = residual.abs() > tolerance
                z = torch.where(active, (a+b)/2, z)
                action, residual, _ = at(z)
                fallback += 1
                if residual.abs().max() <= tolerance:
                    break
                a = torch.where(active & (residual < 0), z, a)
                b = torch.where(active & (residual >= 0), z, b)
        action, residual, _ = at(z)
        if not torch.isfinite(action).all() or residual.abs().max() > 5*tolerance:
            raise ArithmeticError("Hamiltonian root residual tolerance was not met")
        return action, dict(newton_batches=iterations, fallback_bisection_batches=fallback,
                            scalar_row_iterations=len(t)*(iterations+fallback),
                            maximum_fixed_point_residual=float(residual.abs().max()))


def exact_residual(critic, states, B, epsilon=.1):
    params = critic.params
    value, vt, p, trace = critic.jet(states)
    action, work = greedy_newton(p, states[:, :1], params, epsilon)
    flow = (torch.log(action)+states[:, 1:]).mean(1, keepdim=True)
    flow -= params["adjustment"]/2*action.mean(1, keepdim=True).square()
    drift = (params["productivity"]+params["coupling"]*torch.tanh(states[:, 1:] @ B.T)-action
             -(params["idiosyncratic_sigma"]**2+params["common_sigma"]**2)/2)
    residual = -vt-flow-(p*drift).sum(1, keepdim=True)-trace/2+params["discount"]*value
    return residual, work


class MaterializedActor(nn.Module):
    def __init__(self, d, params, width=32, epsilon=.1):
        super().__init__()
        self.d, self.params, self.epsilon = d, dict(params), epsilon
        # State dictionary preserves the conventional net.layers.* interface.
        self.net = nn.Module()
        self.net.layers = mlp(d+1, width, d)

    def forward(self, states):
        safe = torch.cat((states[:, :1], states[:, 1:].clamp(-100., 100.)), 1)
        low, high = action_bounds(states[:, :1], self.params, self.epsilon)
        return (low+high)/2+(high-low)/2*self.net.layers(safe).tanh()


class GreedyPolicy(nn.Module):
    """Optimized direct deployment of the selected HJB critic."""
    def __init__(self, critic, epsilon=.1):
        super().__init__()
        self.critic, self.epsilon = critic, float(epsilon)
        self.work = defaultdict(int)

    def forward(self, states):
        with torch.no_grad():
            _, _, costate, _ = self.critic.jet(states, trace=False)
            action, work = greedy_newton(costate, states[:, :1], self.critic.params, self.epsilon)
        self.work["online_critic_first_jet_rows"] += len(states)
        self.work["online_scalar_row_iterations"] += work["scalar_row_iterations"]
        self.work["online_fallback_bisection_batches"] += work["fallback_bisection_batches"]
        return action


def initial_profiles(d, population):
    if d == 1:
        pattern = np.zeros(1, dtype=np.float64)
    else:
        pattern = np.linspace(-1., 1., d)
        pattern -= pattern.mean()
        pattern /= np.sqrt(np.mean(pattern*pattern))
    return torch.from_numpy(np.asarray([mean+spread*pattern for mean in population["means"]
        for spread in population["spreads"]], dtype=np.float64))


def broad_states(d, n, seed, params, population, scale=1.5):
    generator = torch.Generator().manual_seed(seed)
    support = initial_profiles(d, population)
    initial = support[torch.randint(len(support), (n,), generator=generator)]
    t = params["T"]*torch.rand(n, 1, generator=generator)
    z = torch.randn(n, d+1, generator=generator)
    noise = params["idiosyncratic_sigma"]*z[:, :d]+params["common_sigma"]*z[:, d:]
    mean_drift = params["productivity"]-(params["idiosyncratic_sigma"]**2+params["common_sigma"]**2)/2-schedule(t/2, params)
    y = initial+mean_drift*t+scale*t.sqrt()*noise
    return torch.cat((t, y), 1)


def reference_occupation(d, n, seed, params, population, steps=64, held_schedule=None):
    generator = torch.Generator().manual_seed(seed)
    support = initial_profiles(d, population)
    y = support[torch.randint(len(support), (n,), generator=generator)]
    nodes = torch.randint(steps, (n,), generator=generator)
    result = torch.zeros(n, d+1)
    b, h = coupling(d), params["T"]/steps
    c0 = params["productivity"]-(params["idiosyncratic_sigma"]**2+params["common_sigma"]**2)/2
    for k in range(steps):
        t = torch.full((n, 1), h*k)
        states = torch.cat((t, y), 1)
        result[nodes == k] = states[nodes == k]
        z = torch.randn(n, d+1, generator=generator).clamp(-10., 10.)
        noise = params["idiosyncratic_sigma"]*z[:, :d]+params["common_sigma"]*z[:, d:]
        action = schedule(t, params) if held_schedule is None else held_schedule[k]
        drift = c0+params["coupling"]*torch.tanh(y@b.T)-action
        y = y+h*drift+math.sqrt(h)*noise
    return result, dict(occupation_trajectories=n, simulator_transitions=n*steps,
        reference_rule="left schedule (standalone development)" if held_schedule is None else "supplied common cell-average schedule",
        innovation_clipping_threshold=10.)


def residual_diagnostic(critic, states, B, epsilon, batch=256):
    start = time.perf_counter()
    values, rows = [], 0
    with torch.no_grad():
        for chunk in states.split(batch):
            residual, work = exact_residual(critic, chunk, B, epsilon)
            values.append(residual[:, 0])
            rows += work["scalar_row_iterations"]
    residual = torch.cat(values)
    time_strata = []
    for index in range(4):
        lower, upper = critic.params["T"]*index/4, critic.params["T"]*(index+1)/4
        use = (states[:, 0] >= lower) & (states[:, 0] < upper)
        if index == 3:
            use |= states[:, 0] == upper
        part = residual[use]
        time_strata.append(dict(time_lower=lower, time_upper=upper, count=int(use.sum()),
            rms=None if not len(part) else float(part.square().mean().sqrt()),
            mean=None if not len(part) else float(part.mean())))
    return dict(residual_rms=float(residual.square().mean().sqrt()),
                residual_mean=float(residual.mean()), residual_sample_max=float(residual.abs().max()),
                rows=len(states), scalar_row_iterations=rows,
                time_strata=time_strata,
                seconds=time.perf_counter()-start,
                scope="independent collocation diagnostic, not a uniform value or residual certificate"), residual


def probe_variance_diagnostic(critic, states, *, seed, counts=(2, 8, 32),
                              independent_banks=64):
    """Independent trace-variance audit against an exact Hessian contraction.

    The full Hessian is materialized once solely for this small diagnostic.
    Counts use nested prefixes of the same frozen bank; they cannot select a
    fitted model.  Both the original Gaussian covariance estimator and an
    idiosyncratic Rademacher/exact-common estimator are retained.
    """
    if independent_banks < 2 or min(counts) < 1:
        raise ValueError("trace-variance diagnostic needs at least two banks")
    start = time.perf_counter()
    p, d = critic.params, critic.d
    x = states.detach().requires_grad_(True)
    v = critic(x)
    gradient = torch.autograd.grad(v.sum(), x, create_graph=True)[0][:, 1:]
    hessian = torch.stack([torch.autograd.grad(gradient[:, j].sum(), x,
        retain_graph=True)[0][:, 1:] for j in range(d)], 1).detach()
    exact = p["idiosyncratic_sigma"]**2*torch.diagonal(hessian, dim1=1, dim2=2).sum(1)
    common = p["common_sigma"]**2*hessian.sum((1, 2))
    exact = exact+common
    with torch.no_grad():
        analytic = critic.jet(states)[3][:, 0]
    error = float((analytic-exact).abs().max())
    if error > 5e-11:
        raise ArithmeticError("analytic trace disagrees with independent Hessian diagnostic")
    generator = torch.Generator().manual_seed(seed)
    raw = dict(states=states.detach().numpy(), full_hessian=hessian.numpy(),
               exact_trace=exact.numpy())
    rows = []
    for kind in ["gaussian_covariance", "rademacher_idiosyncratic_exact_common"]:
        estimates = []
        for bank in range(independent_banks):
            if kind == "gaussian_covariance":
                z = torch.randn(len(states), max(counts), d+1, generator=generator)
                direction = p["idiosyncratic_sigma"]*z[:, :, :d]+p["common_sigma"]*z[:, :, d:]
                quadratic = torch.einsum("nki,nij,nkj->nk", direction, hessian, direction)
            else:
                z = 2*torch.randint(2, (len(states), max(counts), d), generator=generator)-1
                direction = p["idiosyncratic_sigma"]*z.to(states.dtype)
                quadratic = torch.einsum("nki,nij,nkj->nk", direction, hessian, direction)+common[:, None]
            estimates.append(torch.stack([quadratic[:, :count].mean(1) for count in counts]))
        estimates = torch.stack(estimates)
        raw[kind+"_bank_estimates"] = estimates.numpy()
        for index, count in enumerate(counts):
            observations = estimates[:, index, :]
            rows.append(dict(kind=kind, probes_per_bank=count, independent_banks=independent_banks,
                state_rows=len(states), average_conditional_variance=float(observations.var(0, unbiased=True).mean()),
                empirical_mean_squared_error=float((observations-exact).square().mean()),
                empirical_mean_bias=float((observations-exact).mean()),
                largest_absolute_bank_error=float((observations-exact).abs().max())))
    return dict(rows=rows, analytic_vs_autograd_max_error=error,
                diagnostic_hessian_rows=len(states)*d,
                diagnostic_quadratic_rows=2*len(states)*independent_banks*max(counts),
                seconds=time.perf_counter()-start,
                used_for_checkpoint_selection=False,
                scope="Monte Carlo trace-variance diagnostic on a frozen finite state bank, not a uniform certificate"), raw


def fit_one(critic, train_states, selection_states, B, *, seed, epsilon=.1,
            learning_rate=.0015, adam_updates=1200, batch=128,
            lbfgs_iterations=150, lbfgs_evaluations=220, checkpoint_every=200,
            residual_stop_rms=.001, minimum_adam_updates=400,
            checkpoint_directory=None):
    """Fit and select only by independent exact-residual diagnostic.

    A separate untouched audit bank is required after selection.  A minimum
    score on this selection bank is not itself an independent error estimate.
    """
    generator = torch.Generator().manual_seed(seed)
    optimizer = torch.optim.Adam(critic.parameters(), lr=learning_rate)
    history, best, best_score = [], None, math.inf
    best_label, prior_value, prior_action, stopped = None, None, None, False
    selection_groups = selection_states if isinstance(selection_states, dict) else {"pooled": selection_states}
    selection_all = torch.cat(list(selection_groups.values()))
    counters = defaultdict(int)
    start = time.perf_counter()

    def select(label):
        nonlocal best, best_score, best_label, prior_value, prior_action
        groups = {}
        for name, states in selection_groups.items():
            groups[name], _ = residual_diagnostic(critic, states, B, epsilon)
            counters["selection_exact_jet_rows"] += len(states)
            counters["selection_scalar_row_iterations"] += groups[name]["scalar_row_iterations"]
        score = math.sqrt(sum(group["residual_rms"]**2 for group in groups.values())/len(groups))
        values, actions = [], []
        with torch.no_grad():
            for chunk in selection_all.split(batch):
                v, _, p, _ = critic.jet(chunk, trace=False)
                action, work = greedy_newton(p, chunk[:, :1], critic.params, epsilon)
                values.append(v)
                actions.append(action)
                counters["selection_first_jet_rows"] += len(chunk)
                counters["selection_scalar_row_iterations"] += work["scalar_row_iterations"]
            value, action = torch.cat(values), torch.cat(actions)
            terminal = selection_all.clone()
            terminal[:, 0] = critic.params["T"]
            terminal_error = float((critic(terminal)-critic.base(terminal)).abs().max())
        row = dict(checkpoint=label, elapsed_seconds=time.perf_counter()-start,
            residual_rms=score, collocation_groups=groups, terminal_value_error=terminal_error,
            value_change_rms=None if prior_value is None else float((value-prior_value).square().mean().sqrt()),
            policy_change_rms=None if prior_action is None else float((action-prior_action).square().mean().sqrt()),
            change_scope="successive iterates on the selection bank; not value or policy error against an optimum")
        prior_value, prior_action = value, action
        if checkpoint_directory is not None:
            directory = Path(checkpoint_directory)
            directory.mkdir(parents=True, exist_ok=True)
            path = directory / (label+".pt")
            torch.save(dict(schema="nbo-r16-hjb-critic-v1", **critic.metadata(),
                            weights=critic.state_dict(), checkpoint=label,
                            payoff_used_for_selection=False), path)
            row["checkpoint_file"] = path.name
            row["checkpoint_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        history.append(row)
        if score < best_score:
            best_score, best_label = score, label
            best = copy.deepcopy(critic.state_dict())
        return score

    select("initial")
    for update in range(adam_updates):
        ids = torch.randint(len(train_states), (batch,), generator=generator)
        optimizer.zero_grad(set_to_none=True)
        residual, work = exact_residual(critic, train_states[ids], B, epsilon)
        loss = residual.square().mean()
        if not torch.isfinite(loss):
            raise FloatingPointError("nonfinite exact HJB objective")
        loss.backward()
        optimizer.step()
        counters["adam_updates"] += 1
        counters["training_exact_jet_rows"] += len(ids)
        counters["training_scalar_row_iterations"] += work["scalar_row_iterations"]
        if (update+1) % checkpoint_every == 0 or update+1 == adam_updates:
            score = select(f"adam_{update+1}")
            if update+1 >= minimum_adam_updates and score <= residual_stop_rms:
                stopped = True
                break
    if lbfgs_iterations and not stopped:
        optimizer = torch.optim.LBFGS(critic.parameters(), lr=1., max_iter=lbfgs_iterations,
            max_eval=lbfgs_evaluations, history_size=30, tolerance_grad=1e-10,
            tolerance_change=1e-12, line_search_fn="strong_wolfe")

        def closure():
            optimizer.zero_grad(set_to_none=True)
            objective = 0.
            for states in train_states.split(batch):
                residual, work = exact_residual(critic, states, B, epsilon)
                loss = residual.square().sum()/len(train_states)
                if not torch.isfinite(loss):
                    raise FloatingPointError("nonfinite L-BFGS HJB objective")
                loss.backward()
                objective += loss.detach()
                counters["training_exact_jet_rows"] += len(states)
                counters["training_scalar_row_iterations"] += work["scalar_row_iterations"]
            counters["lbfgs_closure_calls"] += 1
            return objective

        optimizer.step(closure)
        counters["lbfgs_iterations"] += int(optimizer.state[next(iter(critic.parameters()))].get("n_iter", 0))
        select("lbfgs_final")
    critic.load_state_dict(best)
    return dict(history=history, selected_residual_rms=best_score, selected_checkpoint=best_label,
                work=dict(counters), seconds=time.perf_counter()-start,
                stopped_by_independent_residual=stopped,
                residual_stop_rms=residual_stop_rms,
                payoff_used_for_selection=False)


def distill(critic, actor, states, *, seed, updates=1200, batch=128,
            learning_rate=.002, lbfgs_iterations=100):
    """Cache greedy targets once, then materialize the HJB actor itself."""
    start = time.perf_counter()
    labels, root_rows = [], 0
    with torch.no_grad():
        for chunk in states.split(batch):
            _, _, p, _ = critic.jet(chunk, trace=False)
            action, work = greedy_newton(p, chunk[:, :1], critic.params, actor.epsilon)
            labels.append(action)
            root_rows += work["scalar_row_iterations"]
    labels = torch.cat(labels)
    optimizer = torch.optim.Adam(actor.parameters(), lr=learning_rate)
    generator = torch.Generator().manual_seed(seed)
    for _ in range(updates):
        ids = torch.randint(len(states), (batch,), generator=generator)
        optimizer.zero_grad(set_to_none=True)
        loss = (actor(states[ids])-labels[ids]).square().mean()
        loss.backward()
        optimizer.step()
    closures = 0
    if lbfgs_iterations:
        optimizer = torch.optim.LBFGS(actor.parameters(), lr=1., max_iter=lbfgs_iterations,
            max_eval=2*lbfgs_iterations, history_size=20, tolerance_grad=1e-10,
            tolerance_change=1e-12, line_search_fn="strong_wolfe")
        def closure():
            nonlocal closures
            optimizer.zero_grad(set_to_none=True)
            loss = (actor(states)-labels).square().mean()
            loss.backward()
            closures += 1
            return loss
        optimizer.step(closure)
    return dict(seconds=time.perf_counter()-start, greedy_label_rows=len(states),
                greedy_scalar_row_iterations=root_rows, actor_adam_updates=updates,
                actor_lbfgs_closures=closures,
                fitted_action_mse=float((actor(states)-labels).square().mean().detach()),
                scope="training distillation error; final verifier must evaluate this actor")


def deployment_diagnostic(critic, actor, groups, B, epsilon, batch=256):
    """Untouched finite-state residual and distilled-action diagnostics."""
    start = time.perf_counter()
    rows, raw, counts = {}, {}, defaultdict(int)
    for name, states in groups.items():
        residual, vector = residual_diagnostic(critic, states, B, epsilon, batch)
        counts["audit_exact_jet_rows"] += len(states)
        counts["audit_scalar_row_iterations"] += residual["scalar_row_iterations"]
        action_errors, hamiltonian_gaps = [], []
        with torch.no_grad():
            for chunk in states.split(batch):
                _, _, p, _ = critic.jet(chunk, trace=False)
                greedy, work = greedy_newton(p, chunk[:, :1], critic.params, epsilon)
                deployed = actor(chunk)
                action_errors.append(deployed-greedy)
                gap = (torch.log(greedy)-torch.log(deployed)).mean(1)
                gap -= critic.params["adjustment"]/2*(greedy.mean(1).square()-deployed.mean(1).square())
                gap -= (p*(greedy-deployed)).sum(1)
                hamiltonian_gaps.append(gap)
                counts["audit_first_jet_rows"] += len(chunk)
                counts["audit_actor_rows"] += len(chunk)
                counts["audit_scalar_row_iterations"] += work["scalar_row_iterations"]
        errors, gaps = torch.cat(action_errors), torch.cat(hamiltonian_gaps)
        rows[name] = dict(residual=residual,
            distilled_action_rms_error=float(errors.square().mean().sqrt()),
            distilled_action_sample_max_error=float(errors.abs().max()),
            distilled_hamiltonian_gap_mean=float(gaps.mean()),
            distilled_hamiltonian_gap_sample_min=float(gaps.min()),
            distilled_hamiltonian_gap_sample_max=float(gaps.max()))
        raw[name+"_states"] = states.numpy()
        raw[name+"_residual"] = vector.numpy()
        raw[name+"_action_error"] = errors.numpy()
        raw[name+"_hamiltonian_gap"] = gaps.numpy()
    return dict(groups=rows, work=dict(counts), seconds=time.perf_counter()-start,
                used_for_selection=False,
                scope="finite-state diagnostics; residual and action gaps do not certify value error"), raw


def derived_seed(seed, dimension, domain):
    word = f"NBO-R16-HJB-v1/{seed}/{dimension}/{domain}"
    return int.from_bytes(hashlib.sha256(word.encode()).digest()[:8], "big") % (2**63-1)


def run_hjb_family(*, dimension, params, epsilon, population, seed, configuration,
                   out, reference_held_schedule, source_metadata=None):
    """Execute the prospectively declared residual-selected HJB family.

    The outer worker starts the complete clock before importing this module.
    This function returns both prespecified deployment objects.  Neither can
    be dropped or selected using a final economic payoff.  All candidate fits,
    unsuccessful stopping checks, and both deployment preparation costs are
    retained in the shared family record.
    """
    start = time.perf_counter()
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    c, d = configuration, int(dimension)
    expected = {"T", "discount", "productivity", "coupling", "idiosyncratic_sigma",
                "common_sigma", "adjustment", "lower", "upper", "CHI"}
    if set(params) != expected or not all(math.isfinite(float(x)) for x in params.values()):
        raise ValueError("incomplete or nonfinite HJB economy")
    if not (params["T"] > 0 and params["discount"] > 0 and params["adjustment"] > 0
            and params["CHI"] >= 0 and params["idiosyncratic_sigma"] >= 0
            and params["common_sigma"] >= 0 and 0 < params["lower"] < params["upper"]):
        raise ValueError("invalid HJB economy")
    params = {key: float(value) for key, value in params.items()}
    stream_namespace = str((source_metadata or {}).get("calibration_id", "development_unregistered"))
    def seed_for(domain):
        return derived_seed(seed, d, stream_namespace+"/"+domain)
    held = torch.as_tensor(reference_held_schedule, dtype=torch.float64).detach().clone().reshape(-1)
    if len(held) != c["occupation_steps"] or not torch.isfinite(held).all():
        raise ValueError("explicit common reference schedule has the wrong grid")
    if not bool(((held > params["lower"]) & (held < params["upper"])).all()):
        raise ValueError("common reference schedule leaves the primitive action box")
    identity = dict(params=params, epsilon=float(epsilon), population=population,
                    dimension=d, seed=int(seed), configuration=c,
                    training_stream_namespace=stream_namespace,
                    reference_held_schedule_sha256=hashlib.sha256(held.numpy().tobytes()).hexdigest())
    fingerprint = hashlib.sha256(json.dumps(identity, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    B = coupling(d)
    state_start = time.perf_counter()
    train_occ, occ_work = reference_occupation(d, c["training_rows"],
        seed_for("training_occupation"), params, population, c["occupation_steps"], held)
    train_broad = broad_states(d, c["training_rows"]//2,
        seed_for("training_broad"), params, population, c["broad_noise_scale"])
    select_occ, select_work = reference_occupation(d, c["selection_rows_per_group"],
        seed_for("selection_occupation"), params, population, c["occupation_steps"], held)
    select_broad = broad_states(d, c["selection_rows_per_group"],
        seed_for("selection_broad"), params, population, c["broad_noise_scale"])
    audit_occ, audit_work = reference_occupation(d, c["audit_rows_per_group"],
        seed_for("audit_occupation"), params, population, c["occupation_steps"], held)
    audit_broad = broad_states(d, c["audit_rows_per_group"],
        seed_for("audit_broad"), params, population, c["broad_noise_scale"])
    selection = dict(occupation=select_occ, broad=select_broad)
    audit = dict(occupation=audit_occ, broad=audit_broad)
    np.savez_compressed(out/"collocation.npz", train_occupation=train_occ.numpy(),
        train_broad=train_broad.numpy(), selection_occupation=select_occ.numpy(),
        selection_broad=select_broad.numpy(), audit_occupation=audit_occ.numpy(),
        audit_broad=audit_broad.numpy(), reference_held_schedule=held.numpy())
    phases = dict(collocation_and_io_seconds=time.perf_counter()-state_start)
    candidates, selected, best, selected_critic = [], None, math.inf, None
    for index, variant in enumerate(c["candidates"]):
        torch.manual_seed(seed_for("shared_critic_initialization"))
        critic = ExactCritic(d, params, c["critic_width"], c["critic_time_width"])
        states = train_occ if variant["collocation"] == "occupation" else torch.cat((
            train_occ[:c["training_rows"]//2], train_broad))
        if variant["collocation"] not in ["occupation", "half_occupation_half_broad"]:
            raise ValueError("unregistered HJB collocation variant")
        variant_dir = out/"candidates"/variant["id"]
        candidate_start = time.perf_counter()
        try:
            record = fit_one(critic, states, selection, B,
                seed=seed_for("shared_optimizer_indices"), epsilon=epsilon,
                learning_rate=variant["learning_rate"], adam_updates=c["adam_updates"],
                batch=c["batch"], lbfgs_iterations=c["lbfgs_iterations"],
                lbfgs_evaluations=c["lbfgs_evaluations"], checkpoint_every=c["checkpoint_every"],
                residual_stop_rms=c["residual_stop_rms"],
                minimum_adam_updates=c["minimum_adam_updates"], checkpoint_directory=variant_dir)
            record.update(variant=variant, failure=None)
            if record["selected_residual_rms"] < best:
                best, selected, selected_critic = record["selected_residual_rms"], variant["id"], copy.deepcopy(critic)
        except Exception as exc:
            record = dict(variant=variant, failure=f"{type(exc).__name__}: {exc}",
                seconds=time.perf_counter()-candidate_start,
                earlier_checkpoint_files_retained=True, selected=False)
        candidates.append(record)
        variant_dir.mkdir(parents=True, exist_ok=True)
        (variant_dir/"FIT.json").write_text(json.dumps(record, indent=2, allow_nan=False)+"\n")
    if selected_critic is None:
        (out/"FAILURE.json").write_text(json.dumps(dict(candidates=candidates), indent=2)+"\n")
        raise RuntimeError("every registered HJB candidate failed; no replacement seed is permitted")
    critic = selected_critic
    torch.manual_seed(seed_for("materialized_actor_initialization"))
    actor = MaterializedActor(d, params, c["actor_width"], epsilon)
    distillation_states = torch.cat((train_occ[:c["training_rows"]//2], train_broad))
    distillation = distill(critic, actor, distillation_states,
        seed=seed_for("actor_optimizer"), updates=c["distillation_adam_updates"],
        batch=c["batch"], learning_rate=c["distillation_learning_rate"],
        lbfgs_iterations=c["distillation_lbfgs_iterations"])
    diagnostics, raw = deployment_diagnostic(critic, actor, audit, B, epsilon, c["batch"])
    np.savez_compressed(out/"independent_diagnostics.npz", **raw)
    probe_states = audit_broad[:c["probe_diagnostic_rows"]]
    probe, raw = probe_variance_diagnostic(critic, probe_states,
        seed=seed_for("probe_diagnostics"),
        counts=tuple(c["probe_counts"]), independent_banks=c["probe_diagnostic_banks"])
    np.savez_compressed(out/"probe_diagnostics.npz", **raw)
    metadata = dict(schema="nbo-r16-hjb-candidate-v1", **critic.metadata(),
        epsilon=epsilon, actor_width=c["actor_width"], configuration_fingerprint=fingerprint,
        seed=seed, selected_variant=selected, selected_by="independent exact PDE residual only",
        source_metadata=dict(source_metadata or {}), final_payoff_used_for_fitting=False)
    for kind, state in [("hjb_greedy", None), ("hjb_distilled", actor.state_dict())]:
        torch.save(dict(**metadata, method_id=kind, critic=critic.state_dict(), actor=state), out/(kind+".pt"))
    record = dict(schema="nbo-r16-hjb-family-v1", configuration_fingerprint=fingerprint,
        identity=identity, source_metadata=dict(source_metadata or {}),
        candidates=candidates, selected_variant=selected,
        selected_residual_rms=best, distillation=distillation,
        independent_diagnostics=diagnostics, probe_diagnostics=probe,
        collocation_work=dict(training=occ_work, selection=select_work, audit=audit_work),
        phases=phases, critic_parameters=sum(p.numel() for p in critic.parameters()),
        actor_parameters=sum(p.numel() for p in actor.parameters()),
        output_method_ids=["hjb_greedy", "hjb_distilled"],
        operation_counters_complete=all(candidate.get("failure") is None for candidate in candidates),
        operation_counter_scope="If any candidate failed, saved counters cover completed calls only and are not represented as a complete operation total. The full parent clock still includes every failed attempt.",
        seconds=time.perf_counter()-start,
        family_cost_scope="all four fits, selection checkpoints, distillation, independent diagnostics, and I/O within this call; outer complete clock additionally charges startup and economic checks",
        deployment_cost_rule="both prespecified methods include the full shared family construction cost; no final-payoff selection or uncharged baseline search",
        payoff_evaluations=0)
    (out/"HJB_FAMILY.json").write_text(json.dumps(record, indent=2, allow_nan=False)+"\n")
    return GreedyPolicy(critic, epsilon), actor, record


def load_candidate(path):
    state = torch.load(Path(path), map_location="cpu", weights_only=True)
    if state.get("schema") != "nbo-r16-hjb-candidate-v1":
        raise ValueError("not a registered R16 HJB candidate")
    critic = ExactCritic(state["dimension"], state["params"], state["width"], state["time_width"])
    critic.load_state_dict(state["critic"])
    critic.eval()
    if state["method_id"] == "hjb_greedy":
        actor = GreedyPolicy(critic, state["epsilon"])
    elif state["method_id"] == "hjb_distilled":
        actor = MaterializedActor(state["dimension"], state["params"], state["actor_width"], state["epsilon"])
        actor.load_state_dict(state["actor"])
    else:
        raise ValueError("unknown HJB deployment method")
    actor.eval()
    return actor, critic, state
