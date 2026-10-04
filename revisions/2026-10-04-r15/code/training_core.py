"""R15 frozen-policy Bellman evaluation and matched candidate generators.

All simulated training paths live on one global grid.  The postdecision value
targets are for the finite-grid, transformed capital payoff and the feasible
cell-average schedule.  A trained 64-cell critic used on a finer audit grid is
an arbitrary predictor; its coarse-to-fine error is measured, never set to zero.
Historical source files are imported without modification.  Primitive aliases
are configured only inside the newly launched method worker process.
"""
from __future__ import annotations

from collections import defaultdict
import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import time

import numpy as np
import torch
from torch import nn

ROOT = Path(__file__).resolve().parents[3]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "revisions/2026-10-04-r12/code"))
import common as legacy

old = legacy.old
torch.set_default_dtype(torch.float64)
torch.set_num_threads(1)


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def source_commit():
    return os.environ.get("NBO_R15_NUMERICAL_SOURCE_COMMIT", os.environ.get("NBO_R15_SOURCE_COMMIT", "uncommitted-development"))


def stream_seed(seed, dimension, domain, stage=0):
    word = f"NBO-R15-v1/{seed}/{dimension}/{domain}/{stage}"
    return int.from_bytes(hashlib.sha256(word.encode()).digest()[:8], "big") % (2**63 - 1)


def configure_primitives(params):
    """Explicit isolated-process compatibility for unchanged legacy kernels."""
    params = {k: float(v) for k, v in params.items()}
    if set(params) != {"T", "discount", "productivity", "coupling", "idiosyncratic_sigma",
                       "common_sigma", "adjustment", "lower", "upper", "CHI"}:
        raise ValueError("primitive dictionary is incomplete or contains unknown keys")
    for key in ["T", "discount", "lower", "upper", "adjustment"]:
        if params[key] <= 0:
            raise ValueError("invalid positive primitive: " + key)
    if params["T"] != 1. or params["CHI"] != .03:
        raise ValueError("R15 holds the horizon and dispersion preference fixed")
    p = {k: v for k, v in params.items() if k != "CHI"}
    # The imports below share the economic parameter object in the historical
    # source.  Checking each alias prevents an accidentally mixed calibration.
    for name in ["common", "bellman_study", "tube_neural", "tube_certificate", "policy_certificate"]:
        module = sys.modules.get(name)
        if module is not None and hasattr(module, "P"):
            module.P.update(p)
            if dict(module.P) != p:
                raise AssertionError("mixed primitive alias: " + name)
            if hasattr(module, "CHI") and module.CHI != params["CHI"]:
                raise AssertionError("mixed dispersion-preference alias")
    return params


def mlp(inputs, width):
    net = nn.Sequential(nn.Linear(inputs, width), nn.Tanh(), nn.Linear(width, width), nn.Tanh(), nn.Linear(width, 1))
    nn.init.zeros_(net[-1].weight)
    nn.init.zeros_(net[-1].bias)
    return net


class SplitCritic(nn.Module):
    """Scalar continuation with separate time level and spatial costate fit.

    For ``postdecision``, tx[:,0] is the date AFTER the current Gaussian step,
    while tx[:,1:] is its deterministic mean BEFORE that step.  At the last
    decision, the residual vanishes and the quadratic terminal lift remains.
    ``full_value`` uses the original-value lift for the direct HJB comparator.
    Only the known lifts differ; learned residual capacity is identical.
    """
    def __init__(self, d, params, width=32, time_width=16, kind="postdecision", step=1/64):
        super().__init__()
        if kind not in ["postdecision", "full_value"]:
            raise ValueError("unknown critic kind")
        self.d, self.params, self.width, self.time_width = d, dict(params), width, time_width
        self.kind, self.step = kind, float(step)
        self.time = mlp(1, time_width)
        self.space = mlp(d+1, width)

    def base(self, tx):
        p = self.params
        t, y = tx[:, :1], tx[:, 1:]
        tau = p["T"] - t
        mean = y.mean(1, keepdim=True)
        dispersion = ((y-mean)**2).mean(1, keepdim=True)
        if self.kind == "full_value":
            e = torch.exp(-p["discount"]*tau)
            w = (1-e)/p["discount"] + e
            return w*mean - p["CHI"]*e*dispersion
        # E clip(G,[-10,10])^2 differs from one below binary64 resolution.
        # This known-lift rounding is part of predictor error, not an asserted
        # exact floating-point expectation or a new probability certificate.
        noise_dispersion = p["idiosyncratic_sigma"]**2 * (1-1/self.d) * (tau+self.step)
        return -p["CHI"]*math.exp(-p["discount"]*p["T"])*(dispersion+noise_dispersion)

    def forward(self, tx):
        tau = self.params["T"]-tx[:, :1]
        return self.base(tx) + tau*(self.time(tx[:, :1]) + self.space(tx)/self.d)

    def metadata(self):
        return dict(critic_family="split_critic", critic_kind=self.kind, critic_step=self.step,
                    width=self.width, time_width=self.time_width, dimension=self.d,
                    params=self.params, primitives_sha256=canonical_hash(self.params))


def first_jet(critic, states, create_graph=True):
    x = states.detach().requires_grad_(True)
    value = critic(x)
    grad = torch.autograd.grad(value.sum(), x, create_graph=create_graph)[0]
    return x, value, grad[:, :1], grad[:, 1:]


def training_weights(steps):
    wt = legacy.pc.weights(steps)
    return {name: torch.from_numpy(legacy.pc.midpoint(wt[name]).copy()) for name in ["A", "B", "M"]}


def profiles(d, population):
    if d == 1:
        v = np.zeros(1)
    else:
        v = np.linspace(-1., 1., d)
        v -= v.mean()
        v /= np.sqrt(np.mean(v*v))
    return torch.from_numpy(np.asarray([mu+s*v for mu in population["means"] for s in population["spreads"]], dtype=np.float64))


def drift(y, action, B, params):
    c0 = params["productivity"]-(params["idiosyncratic_sigma"]**2+params["common_sigma"]**2)/2
    return c0+params["coupling"]*torch.tanh(y@B.T)-action


class ReferencePolicy(nn.Module):
    def __init__(self, d, params, steps, weights):
        super().__init__()
        self.d, self.params, self.steps = d, dict(params), steps
        self.register_buffer("held_schedule", weights["M"]/(params["T"]/steps))

    def forward(self, states):
        indices = torch.floor(states[:, 0]*self.steps/self.params["T"]+1e-10).long().clamp(0, self.steps-1)
        return self.held_schedule[indices, None].expand(-1, self.d)


class AnalyticalSchedule(nn.Module):
    """Exact economic fallback; verifier handles its zero relative payoff."""
    is_analytical_schedule = True
    def __init__(self, d, params):
        super().__init__()
        self.d, self.params = d, dict(params)
    def forward(self, states):
        return old.schedule(states[:, :1]).expand(-1, self.d)


def occupation(actor, d, n, seed, steps, params, population, counters=None):
    """One uniform-node state from each independent global-grid trajectory."""
    g = torch.Generator().manual_seed(seed)
    support = profiles(d, population)
    y = support[torch.randint(len(support), (n,), generator=g)].clone()
    nodes = torch.randint(steps, (n,), generator=g)
    result = torch.zeros(n, d+1)
    B, h = torch.from_numpy(old.coupling(d)), params["T"]/steps
    with torch.no_grad():
        for k in range(steps):
            states = torch.cat([torch.full((n, 1), k*h), y], 1)
            use = nodes == k
            result[use] = states[use]
            action = actor(states)
            z = torch.randn(n, d+1, generator=g).clamp(-10., 10.)
            noise = params["idiosyncratic_sigma"]*z[:, :d]+params["common_sigma"]*z[:, d:]
            y = y+h*drift(y, action, B, params)+math.sqrt(h)*noise
    if counters is not None:
        counters["simulator_transitions"] += n*steps
        counters["occupation_trajectory_starts"] += n
        counters["occupation_state_rows"] += n
        counters["actor_forward_rows"] += n*steps
    return result, nodes


def postdecision_inputs(states, nodes, params, weights, B):
    h = params["T"]/len(weights["A"])
    pi = weights["M"][nodes, None]/h
    y = states[:, 1:]+h*drift(states[:, 1:], pi, B, params)
    after = (nodes.to(torch.float64)+1)*h
    return torch.cat([after[:, None], y], 1)


def postdecision_target(post, nodes, z, params, weights, B):
    """Exact differentiated finite-grid sample for the frozen held schedule.

    First consume xi_k at the supplied postdecision mean.  Current reward ell_k
    is excluded.  Subsequent rewards start at k+1, on the SAME fixed global grid.
    Vectorization pads completed tails; inactive arithmetic is counted separately.
    """
    steps, n, d = len(weights["A"]), len(post), B.shape[0]
    h = params["T"]/steps
    start = post[:, 1:].detach().clone().requires_grad_(True)
    noise = lambda zz: params["idiosyncratic_sigma"]*zz[:, :d]+params["common_sigma"]*zz[:, d:]
    y = start+math.sqrt(h)*noise(z[0])
    reward = torch.zeros(n, 1)
    for offset in range(1, steps):
        node = nodes+offset
        active = (node < steps)[:, None]
        j = node.clamp(max=steps-1)
        action = weights["M"][j, None]/h
        production = params["coupling"]*torch.tanh(y@B.T)
        ell = weights["B"][j, None]*production.mean(1, keepdim=True)
        ell = ell+weights["A"][j, None]*(torch.log(action)-params["adjustment"]/2*action.square())-weights["B"][j, None]*action
        reward = reward+torch.where(active, ell, torch.zeros_like(ell))
        candidate = y+h*drift(y, action, B, params)+math.sqrt(h)*noise(z[offset])
        y = torch.where(active, candidate, y)
    dispersion = ((y-y.mean(1, keepdim=True))**2).mean(1, keepdim=True)
    reward = reward-params["CHI"]*math.exp(-params["discount"]*params["T"])*dispersion
    q = d*torch.autograd.grad(reward.sum(), start)[0]
    return reward.detach(), q.detach()


def postdecision_labels(post, nodes, seed, params, weights, B, replicates=4, counters=None):
    if replicates != 4:
        raise ValueError("the frozen R15 primary uses four antithetic rollouts")
    generator = torch.Generator().manual_seed(seed)
    values, costates = [], []
    steps, n, d = len(weights["A"]), len(post), B.shape[0]
    for rep in range(replicates):
        if rep % 2 == 0:
            innovations = torch.randn(steps, n, d+1, generator=generator).clamp(-10., 10.)
        else:
            innovations = -innovations
        value, q = postdecision_target(post, nodes, innovations, params, weights, B)
        values.append(value)
        costates.append(q)
    if counters is not None:
        counters["simulator_transitions"] += replicates*int((steps-nodes).sum())
        counters["padded_rollout_arithmetic_rows"] += replicates*n*steps
        counters["rollout_starts"] += replicates*n
        counters["first_derivative_rows"] += replicates*n
        counters["backward_passes"] += replicates
        counters["raw_costate_label_rows"] += replicates*n
    return torch.stack(values), torch.stack(costates)


def direct_rollout(actor, support, ids, innovations, params, weights, B):
    """Differentiable complete global-grid transformed payoff for DPO."""
    y = support[ids].clone()
    n, steps = len(y), len(weights["A"])
    h = params["T"]/steps
    result = torch.zeros(n, 1)
    for k in range(steps):
        tx = torch.cat([torch.full((n, 1), k*h), y], 1)
        action = actor(tx)
        production = params["coupling"]*torch.tanh(y@B.T)
        mean = action.mean(1, keepdim=True)
        result = result+weights["B"][k]*(production.mean(1, keepdim=True)-mean)
        result = result+weights["A"][k]*(torch.log(action).mean(1, keepdim=True)-params["adjustment"]/2*mean.square())
        noise = params["idiosyncratic_sigma"]*innovations[k, :, :-1]+params["common_sigma"]*innovations[k, :, -1:]
        y = y+h*drift(y, action, B, params)+math.sqrt(h)*noise
    dispersion = ((y-y.mean(1, keepdim=True))**2).mean(1, keepdim=True)
    return result-params["CHI"]*math.exp(-params["discount"]*params["T"])*dispersion


class TrainingRun:
    """One continuing method stream; caller performs and charges real checks."""
    def __init__(self, protocol, dimension, seed, method_id, out, metadata=None):
        self.protocol, self.dimension, self.seed, self.method_id = protocol, int(dimension), int(seed), method_id
        self.out = Path(out)
        self.out.mkdir(parents=True, exist_ok=True)
        self.metadata = dict(metadata or {})
        self.cfg = protocol["training"]
        self.params = configure_primitives(protocol["design"]["primitives"])
        self.primitive_hash = canonical_hash(self.params)
        if self.primitive_hash != protocol["design"]["primitives_sha256"]:
            raise AssertionError("wrong primitive fingerprint")
        if method_id not in protocol["design"]["methods"]:
            raise ValueError("undeclared method")
        self.steps = self.cfg["global_steps"]
        self.h = self.params["T"]/self.steps
        self.width = self.cfg["actor_width"]
        self.epsilon = self.cfg["epsilon"]
        self.weights = training_weights(self.steps)
        self.B = torch.from_numpy(old.coupling(dimension))
        self.population = protocol["design"]["initial_state_population"]
        self.reference = ReferencePolicy(dimension, self.params, self.steps, self.weights)
        self.counters, self.history = defaultdict(int), []
        self.stage, self.train_states, self.train_nodes, self.post = 0, None, None, None
        self.value_replicates, self.q_replicates = None, None
        torch.manual_seed(stream_seed(seed, dimension, "initialization"))
        self.actor = old.Actor(dimension, self.width, self.epsilon)
        self.critic = SplitCritic(dimension, self.params, self.cfg["critic_width"], self.cfg["critic_time_width"],
                                  kind="full_value" if method_id == "neural_hjb" else "postdecision", step=self.h)
        self.actor_optimizer = torch.optim.Adam(self.actor.parameters(), lr=self.cfg["actor_lr"])
        self.hjb_optimizer = torch.optim.Adam(self.critic.parameters(), lr=self.cfg["hjb_lr"])
        if method_id == "neural_hjb":
            import baselines
            self.actor = baselines.make_policy(self.critic, self.epsilon)
        self.algorithm_configuration_fingerprint = canonical_hash(dict(method_id=method_id, training=self.cfg, primitives=self.params))
        self.method_fingerprint = self.metadata.get("method_fingerprint", self.algorithm_configuration_fingerprint)

    def _append_occupation(self, stage, target_size):
        current = 0 if self.train_states is None else len(self.train_states)
        count = target_size-current
        if count <= 0:
            raise ValueError("non-increasing replay budget")
        states, nodes = occupation(self.reference, self.dimension, count,
                                    stream_seed(self.seed, self.dimension, "occupation", stage),
                                    self.steps, self.params, self.population, self.counters)
        post = postdecision_inputs(states, nodes, self.params, self.weights, self.B)
        def append(oldvalue, new):
            return new if oldvalue is None else torch.cat([oldvalue, new], 0)
        self.train_states = append(self.train_states, states)
        self.train_nodes = append(self.train_nodes, nodes)
        self.post = append(self.post, post)
        self.counters["postdecision_state_rows"] += count
        if self.method_id in ["nbo", "raw_costate"]:
            values, q = postdecision_labels(post, nodes,
                stream_seed(self.seed, self.dimension, "continuation_labels", stage), self.params,
                self.weights, self.B, self.cfg["antithetic_replicates"], self.counters)
            self.value_replicates = values if self.value_replicates is None else torch.cat([self.value_replicates, values], 1)
            self.q_replicates = q if self.q_replicates is None else torch.cat([self.q_replicates, q], 1)
        return count

    def _fit_critic(self, stage, generator):
        cfg, n, d = self.cfg, len(self.post), self.dimension
        target_q, target_v = self.q_replicates.mean(0), self.value_replicates.mean(0)
        optimizer = torch.optim.Adam(self.critic.space.parameters(), lr=cfg["critic_lr"])
        for _ in range(cfg["critic_adam_updates_per_stage"]):
            ids = torch.randint(n, (cfg["batch"],), generator=generator)
            _, _, _, grad = first_jet(self.critic, self.post[ids])
            loss = (d*grad-target_q[ids]).square().mean()
            if not torch.isfinite(loss):
                raise FloatingPointError("nonfinite Sobolev objective")
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            self.counters["critic_updates"] += 1
            self.counters["critic_adam_updates"] += 1
            self.counters["critic_forward_rows"] += len(ids)
            self.counters["first_derivative_rows"] += len(ids)
            self.counters["second_derivative_rows"] += len(ids)
            self.counters["backward_passes"] += 2
        lb = cfg["critic_lbfgs"]
        optimizer = torch.optim.LBFGS(self.critic.space.parameters(), lr=lb["lr"], max_iter=lb["max_iter"],
            max_eval=lb["max_eval"], tolerance_grad=lb["tolerance_grad"], tolerance_change=lb["tolerance_change"],
            history_size=lb["history_size"], line_search_fn=lb["line_search_fn"])
        closure_calls = 0
        def closure():
            nonlocal closure_calls
            optimizer.zero_grad(set_to_none=True)
            _, _, _, grad = first_jet(self.critic, self.post)
            objective = (d*grad-target_q).square().mean()
            if not torch.isfinite(objective):
                raise FloatingPointError("nonfinite full replay objective")
            objective.backward()
            closure_calls += 1
            self.counters["critic_forward_rows"] += n
            self.counters["first_derivative_rows"] += n
            self.counters["second_derivative_rows"] += n
            self.counters["backward_passes"] += 2
            self.counters["critic_lbfgs_closure_calls"] += 1
            return objective
        optimizer.step(closure)
        first_parameter = next(iter(self.critic.space.parameters()))
        lb_iterations = int(optimizer.state[first_parameter].get("n_iter", 0))
        self.counters["critic_updates"] += lb_iterations
        self.counters["critic_lbfgs_iterations"] += lb_iterations
        # Value-level noise may change only the time intercept, never the
        # spatial derivative fit. No value target or label is discarded.
        with torch.no_grad():
            spatial = self.critic.space(self.post)/d
            base = self.critic.base(self.post)
        self.counters["critic_forward_rows"] += n
        time_optimizer = torch.optim.Adam(self.critic.time.parameters(), lr=cfg["critic_time_lr"])
        for _ in range(cfg["critic_time_updates_per_stage"]):
            ids = torch.randint(n, (cfg["batch"],), generator=generator)
            tau = self.params["T"]-self.post[ids, :1]
            pred = base[ids]+tau*(spatial[ids]+self.critic.time(self.post[ids, :1]))
            loss = (pred-target_v[ids]).square().mean()
            if not torch.isfinite(loss):
                raise FloatingPointError("nonfinite time-intercept objective")
            time_optimizer.zero_grad(set_to_none=True)
            loss.backward()
            time_optimizer.step()
            self.counters["critic_updates"] += 1
            self.counters["critic_time_updates"] += 1
            self.counters["critic_forward_rows"] += len(ids)
            self.counters["backward_passes"] += 1
        _, _, _, p = first_jet(self.critic, self.post, create_graph=False)
        self.counters["critic_forward_rows"] += n
        self.counters["first_derivative_rows"] += n
        self.counters["backward_passes"] += 1
        q = (d*p).detach()
        with torch.no_grad():
            final_value = self.critic(self.post)
        self.counters["critic_forward_rows"] += n
        return q, dict(lbfgs_iterations=lb_iterations, lbfgs_closure_calls=closure_calls,
                       replay_costate_mse=float((q-target_q).square().mean()),
                       replay_value_mse=float((final_value-target_v).square().mean()),
                       replay_label_replicates=4,
                       objective_scope="training replay fit diagnostics; no held-out or continuous-time error bound")

    def _fit_actor(self, q, stage, generator):
        cfg, n = self.cfg, len(self.train_states)
        q = q.detach()
        # SAME reference-postdecision Hamiltonian linearization for NBO/Raw.
        # All labels may be reused, and both have identical actor update counts.
        A, B = self.weights["A"][self.train_nodes, None], self.weights["B"][self.train_nodes, None]
        effective_q = B/A+self.h/A*q
        for _ in range(cfg["actor_updates_per_stage"][stage-1]):
            ids = torch.randint(n, (cfg["batch"],), generator=generator)
            action = self.actor(self.train_states[ids])
            objective = torch.log(action).mean(1)-self.params["adjustment"]/2*action.mean(1).square()-(action*effective_q[ids]).mean(1)
            loss = -objective.mean()
            if not torch.isfinite(loss):
                raise FloatingPointError("nonfinite actor objective")
            self.actor_optimizer.zero_grad(set_to_none=True)
            loss.backward()
            self.actor_optimizer.step()
            self.counters["actor_updates"] += 1
            self.counters["actor_forward_rows"] += len(ids)
            self.counters["cached_costate_rows_consumed"] += len(ids)
            self.counters["backward_passes"] += 1
        with torch.no_grad():
            action = self.actor(self.train_states)
            hamiltonian = torch.log(action).mean(1)-self.params["adjustment"]/2*action.mean(1).square()-(action*effective_q).mean(1)
        self.counters["actor_forward_rows"] += n
        return dict(replay_actor_hamiltonian=float(hamiltonian.mean()),
                    actor_objective_scope="common reference-costate Hamiltonian on cached training states; not a held-out Q maximization certificate")

    def _fit_direct(self, stage, generator):
        cfg, d = self.cfg, self.dimension
        support = profiles(d, self.population)
        for _ in range(cfg["direct_updates_per_stage"][stage-1]):
            ids = torch.randint(len(support), (cfg["batch"],), generator=generator)
            self.actor_optimizer.zero_grad(set_to_none=True)
            for rep in range(cfg["antithetic_replicates"]):
                if rep % 2 == 0:
                    innovations = torch.randn(self.steps, len(ids), d+1, generator=generator).clamp(-10., 10.)
                else:
                    innovations = -innovations
                value = direct_rollout(self.actor, support, ids, innovations, self.params, self.weights, self.B)
                loss = -value.mean()/cfg["antithetic_replicates"]
                if not torch.isfinite(loss):
                    raise FloatingPointError("nonfinite direct policy objective")
                loss.backward()
                self.counters["simulator_transitions"] += len(ids)*self.steps
                self.counters["actor_forward_rows"] += len(ids)*self.steps
                self.counters["rollout_starts"] += len(ids)
                self.counters["backward_passes"] += 1
            self.actor_optimizer.step()
            self.counters["actor_updates"] += 1

    def _fit_hjb(self, stage, generator):
        import baselines
        cfg, n = self.cfg, len(self.train_states)
        probe_generator = torch.Generator().manual_seed(stream_seed(self.seed, self.dimension, "hjb_probes", stage))
        losses = []
        for update in range(cfg["hjb_updates_per_stage"][stage-1]):
            ids = torch.randint(n, (cfg["batch"],), generator=generator)
            result = baselines.hjb_step(self.critic, self.train_states[ids], self.B, self.hjb_optimizer, probe_generator,
                epsilon=self.epsilon, probes=cfg["hjb_trace_probes"], trace_mode="hutchinson", primitives=self.params)
            losses.append(dict(update=update+1, loss=result["loss"], negative_loss=result["negative_loss"],
                               minimum_action=result["minimum_action"], maximum_action=result["maximum_action"]))
            self.counters["critic_updates"] += 1
            self.counters["critic_forward_rows"] += len(ids)
            self.counters["first_derivative_rows"] += len(ids)
            self.counters["second_derivative_rows"] += 2*cfg["hjb_trace_probes"]*len(ids)
            self.counters["hessian_vector_rows"] += 2*cfg["hjb_trace_probes"]*len(ids)
            self.counters["backward_passes"] += 2+2*cfg["hjb_trace_probes"]
            self.counters["action_search_iterations"] += 44*len(ids)
        return dict(hjb_training_losses=losses, negative_hjb_losses=sum(r["negative_loss"] for r in losses),
                    hjb_objective_scope="unbiased product of two independent trace-residual estimates; negative minibatch values are retained")

    def advance(self, stage):
        if stage != self.stage+1 or stage > len(self.cfg["cumulative_replay_states"]):
            raise ValueError("stages must advance exactly once in order")
        start = time.perf_counter()
        new_states = self._append_occupation(stage, self.cfg["cumulative_replay_states"][stage-1])
        generator = torch.Generator().manual_seed(stream_seed(self.seed, self.dimension, self.method_id+"_optimizer", stage))
        details = {}
        if self.method_id == "nbo":
            q, details = self._fit_critic(stage, generator)
            actor_generator = torch.Generator().manual_seed(stream_seed(self.seed, self.dimension, "actor_distillation", stage))
            details.update(self._fit_actor(q, stage, actor_generator))
        elif self.method_id == "raw_costate":
            actor_generator = torch.Generator().manual_seed(stream_seed(self.seed, self.dimension, "actor_distillation", stage))
            details.update(self._fit_actor(self.q_replicates.mean(0), stage, actor_generator))
        elif self.method_id == "direct_policy":
            self._fit_direct(stage, generator)
        elif self.method_id == "neural_hjb":
            details.update(self._fit_hjb(stage, generator))
        self.stage = stage
        row = dict(stage=stage, cumulative_replay_states=len(self.train_states), new_states=new_states,
                   stage_seconds=time.perf_counter()-start, counters=dict(self.counters), **details)
        self.history.append(row)
        return row

    def snapshot(self):
        kind = "critic_greedy" if self.method_id == "neural_hjb" else "neural_actor"
        return dict(schema="nbo-r15-candidate-v1", method_id=self.method_id,
            method_fingerprint=self.method_fingerprint,
            algorithm_configuration_fingerprint=self.algorithm_configuration_fingerprint,
            dimension=self.dimension, seed=self.seed,
            width=self.width, critic_width=self.cfg["critic_width"], time_width=self.cfg["critic_time_width"], epsilon=self.epsilon,
            actor_kind=kind, actor=None if kind == "critic_greedy" else copy.deepcopy(self.actor.state_dict()),
            critic=copy.deepcopy(self.critic.state_dict()) if self.method_id in ["nbo", "neural_hjb"] else None,
            critic_family="split_critic", critic_kind=self.critic.kind, critic_step=self.h,
            stage=self.stage, N_train=self.steps, N_audit=self.protocol["confirmation"]["steps"],
            params=self.params, primitives_sha256=self.primitive_hash,
            source_commit=self.metadata.get("source_commit", source_commit()),
            numerical_source_commit=self.metadata.get("source_commit", source_commit()),
            protocol_sha256=self.metadata.get("protocol_sha256", canonical_hash(self.protocol)),
            training_history=copy.deepcopy(self.history),
            stage_work=dict(self.counters), reference_policy="cell-average analytical schedule M_k/h",
            actor_loss="same reference-postdecision Hamiltonian linearization for NBO and raw_costate",
            final_test_used_for_fitting=False)

    def save_checkpoint(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.snapshot(), path)
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def save_replay(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        values = dict(states=self.train_states.numpy(), nodes=self.train_nodes.numpy(), postdecision=self.post.numpy())
        if self.value_replicates is not None:
            values.update(value_replicates=self.value_replicates.numpy(), costate_replicates=self.q_replicates.numpy())
        np.savez_compressed(path, **values)
        return hashlib.sha256(path.read_bytes()).hexdigest()


def load_candidate(path, *, critic_step=None):
    state = torch.load(path, map_location="cpu", weights_only=True)
    params = configure_primitives(state["params"])
    if canonical_hash(params) != state["primitives_sha256"]:
        raise AssertionError("checkpoint primitive identity")
    d = state["dimension"]
    critic = None
    if state.get("critic") is not None:
        critic = SplitCritic(d, params, state.get("critic_width", state["width"]), state["time_width"], state["critic_kind"],
                            state["critic_step"] if critic_step is None else critic_step)
        critic.load_state_dict(state["critic"])
        critic.eval()
    if state["actor_kind"] == "analytical_schedule":
        actor = AnalyticalSchedule(d, params)
    elif state["actor_kind"] == "critic_greedy":
        import baselines
        actor = baselines.make_policy(critic, state["epsilon"])
    else:
        actor = old.Actor(d, state["width"], state["epsilon"])
        actor.load_state_dict(state["actor"])
    actor.eval()
    return actor, critic, state


def save_fallback(path, protocol, dimension, seed, method_id, *, metadata=None, failure=None, counters=None):
    """Keep a failed complete stream; do not silently replace its seed."""
    metadata = dict(metadata or {})
    params = configure_primitives(protocol["design"]["primitives"])
    state = dict(schema="nbo-r15-candidate-v1", method_id=method_id, dimension=dimension, seed=seed,
        width=protocol["training"]["actor_width"], time_width=protocol["training"]["critic_time_width"],
        epsilon=protocol["training"]["epsilon"], actor_kind="analytical_schedule", actor=None, critic=None,
        critic_family="split_critic", critic_kind="postdecision", critic_step=params["T"]/protocol["training"]["global_steps"],
        stage=0, N_train=protocol["training"]["global_steps"], N_audit=protocol["confirmation"]["steps"],
        params=params, primitives_sha256=canonical_hash(params),
        source_commit=metadata.get("source_commit", source_commit()),
        numerical_source_commit=metadata.get("source_commit", source_commit()),
        protocol_sha256=metadata.get("protocol_sha256", canonical_hash(protocol)),
        method_fingerprint=metadata.get("method_fingerprint", canonical_hash(dict(method_id=method_id, training=protocol["training"], primitives=params))),
        algorithm_configuration_fingerprint=canonical_hash(dict(method_id=method_id, training=protocol["training"], primitives=params)),
        fallback=True, failure=failure, stage_work=dict(counters or {}), final_test_used_for_fitting=False)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(state, path)
    return hashlib.sha256(path.read_bytes()).hexdigest()
