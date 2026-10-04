"""Contribution-isolating neural HJB baseline in the unchanged capital model.

The shared R15 worker supplies the same split scalar network capacity as NBO,
with the hard terminal lift appropriate to the full value equation.  The
standalone development runner retains the original R12 Critic.  The policy is
its feasible Hamiltonian maximizer, computed at deployment;
there is no separately trained actor in the canonical ``neural_hjb`` method.
Independent Hessian-probe banks give an unbiased *squared PDE residual* objective
conditional on collocation states and current weights.  A negative sampled loss
is possible and is recorded, not truncated.  This optimization objective is not
a uniform residual certificate.

``hjb_step`` is the shared worker interface.  ``train`` is a standalone, charged
development runner.  Production all-cost measurement belongs to the outer R15
worker, which includes process startup, checkpoint I/O and final verification.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import resource
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
R15 = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
_common_path = ROOT / "revisions/2026-10-04-r12/code/common.py"
_spec = importlib.util.spec_from_file_location("nbo_r15_legacy_common", _common_path)
legacy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(legacy)
old, torch, np, P = legacy.old, legacy.torch, legacy.np, legacy.P


def source_commit():
    return os.environ.get("NBO_R15_NUMERICAL_SOURCE_COMMIT",
                          os.environ.get("NBO_R15_SOURCE_COMMIT", "uncommitted-development"))


def write_json(path, row):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2, allow_nan=False) + "\n")


def file_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def population_states(d, n, generator, random_time=True):
    """Exactly the R12 information and collocation design; no optimum labels."""
    t = torch.rand(n, 1, generator=generator) if random_time else torch.zeros(n, 1)
    support = torch.from_numpy(legacy.profiles(d))
    indices = torch.randint(len(support), (n,), generator=generator)
    y = support[indices] - .7 * t + .2 * torch.sqrt(t) * torch.randn(n, d, generator=generator)
    return torch.cat((t, y), dim=1)


def trace_exact(p, x, *, create_graph=True, primitives=None):
    """tr[(sigma_I^2 I + sigma_C^2 11') D_y^2 v], using d + 1 HVPs."""
    primitives = P if primitives is None else primitives
    d = p.shape[1]
    # Even a manufactured affine critic has a zero Hessian.  Keep the returned
    # zero attached to x so derivative-based tests and objectives remain valid.
    answer = x[:, :1] * 0.
    if not p.requires_grad:
        return answer
    for j in range(d):
        h = torch.autograd.grad(p[:, j].sum(), x, create_graph=create_graph,
                                retain_graph=True, allow_unused=True)[0]
        if h is not None:
            answer = answer + primitives["idiosyncratic_sigma"] ** 2 * h[:, j + 1:j + 2]
    h = torch.autograd.grad(p.sum(), x, create_graph=create_graph,
                            retain_graph=True, allow_unused=True)[0]
    if h is not None:
        answer = answer + primitives["common_sigma"] ** 2 * h[:, 1:].sum(1, keepdim=True)
    return answer


def trace_hutchinson(p, x, generator, *, probes=2, create_graph=True, primitives=None):
    """Gaussian covariance probes; each call consumes a disjoint noise bank."""
    if probes < 1:
        raise ValueError("at least one Hessian probe is required")
    primitives = P if primitives is None else primitives
    d = p.shape[1]
    if not p.requires_grad:
        return x[:, :1] * 0.
    answer = x[:, :1] * 0.
    for _ in range(probes):
        z = torch.randn(len(x), d + 1, generator=generator, dtype=x.dtype, device=x.device)
        direction = primitives["idiosyncratic_sigma"] * z[:, :d] + primitives["common_sigma"] * z[:, d:]
        h = torch.autograd.grad((p * direction).sum(), x, create_graph=create_graph,
                                retain_graph=True, allow_unused=True)[0]
        if h is not None:
            answer = answer + (h[:, 1:] * direction).sum(1, keepdim=True) / probes
    return answer


def hjb_residuals(critic, states, B, trace_generator, *, epsilon=.1,
                  probes=2, trace_mode="hutchinson", create_graph=True,
                  primitives=None):
    """Two conditionally independent estimates of the restricted HJB residual.

    R[v] = -v_t - max_m{u(y,m)+b(y,m)'D_y v}
           -.5 tr(Sigma Sigma' D_y^2 v) + rho v.
    The actor maximization is exact up to 44 monotone scalar bisections, as in
    every R12 costate comparison.  Detaching its maximizer differentiates the
    envelope, not a surrogate objective.  Bounds are the common schedule tube;
    epsilon=None is an explicit full-primitive-box experimental variant.
    """
    if trace_mode not in {"hutchinson", "exact"}:
        raise ValueError("unknown trace estimator")
    primitives = P if primitives is None else primitives
    # The common actor/schedule/greedy classes use these unchanged primitives.
    # A volatility scenario may vary diffusion without mutating historical P.
    for key in ["discount", "T", "adjustment", "lower", "upper"]:
        if primitives[key] != P[key]:
            raise ValueError("HJB actor factory needs an explicit adapter for changed " + key)
    x, v, vt, p = old.first_jet(critic, states)
    m = old.greedy(p.detach(), x[:, :1].detach(), epsilon).detach()
    drift = (primitives["productivity"] + primitives["coupling"] * torch.tanh(x[:, 1:] @ B.T)
             - m - (primitives["idiosyncratic_sigma"] ** 2 + primitives["common_sigma"] ** 2) / 2.)
    deterministic = (-vt - old.flow(x[:, 1:], m)
                     - (drift * p).sum(1, keepdim=True)
                     + primitives["discount"] * v)
    if trace_mode == "exact":
        tr = trace_exact(p, x, create_graph=create_graph, primitives=primitives)
        r1 = r2 = deterministic - .5 * tr
    else:
        r1 = deterministic - .5 * trace_hutchinson(
            p, x, trace_generator, probes=probes, create_graph=create_graph, primitives=primitives)
        r2 = deterministic - .5 * trace_hutchinson(
            p, x, trace_generator, probes=probes, create_graph=create_graph, primitives=primitives)
    return r1, r2, m


def hjb_step(critic, states, B, optimizer, trace_generator, *, epsilon=.1,
             probes=2, trace_mode="hutchinson", primitives=None):
    """One PDE optimizer update, returning explicit work and loss diagnostics."""
    start = time.perf_counter()
    optimizer.zero_grad(set_to_none=True)
    r1, r2, m = hjb_residuals(critic, states, B, trace_generator, epsilon=epsilon,
                             probes=probes, trace_mode=trace_mode, primitives=primitives)
    loss = (r1 * r2).mean()
    if not torch.isfinite(loss):
        raise FloatingPointError("nonfinite direct HJB objective")
    loss.backward()
    optimizer.step()
    if not all(torch.isfinite(v).all() for v in critic.parameters()):
        raise FloatingPointError("nonfinite direct HJB weights")
    n, d = len(states), states.shape[1] - 1
    hvps = d + 1 if trace_mode == "exact" else 2 * probes
    return dict(loss=float(loss.detach()), negative_loss=int(loss.detach() < 0),
                collocation_states=n, training_state_visits=0,
                simulator_transitions=0, critic_forward_states=n,
                input_gradient_states=n, hessian_vector_product_states=n * hvps,
                hessian_vector_product_batches=hvps, critic_updates=1,
                actor_updates=0, optimizer_backward_calls=1,
                greedy_action_states=n, greedy_scalar_iterations=44 * n,
                minimum_action=float(m.min()), maximum_action=float(m.max()),
                seconds=time.perf_counter() - start)


def make_policy(critic, epsilon=.1):
    """Canonical tube policy: every decision performs a gradient and 44 bisections."""
    if epsilon is None:
        raise ValueError("canonical neural_hjb uses the same explicit tube as its comparators")
    return old.GreedyPolicy(critic, mode="direct_tube", mix=1., epsilon=epsilon)


def policy_snapshot(critic, *, dimension, width, epsilon, iteration, seed,
                    method_fingerprint=None, critic_family="r12_critic",
                    critic_kind="full_value", time_width=16, critic_step=None,
                    primitives=None):
    """Canonical identifiers stay separate from the historical loader class."""
    return dict(critic=copy.deepcopy(critic.state_dict()), dimension=int(dimension),
                width=int(width), epsilon=float(epsilon), iteration=int(iteration),
                seed=int(seed), method="neural_hjb", method_id="neural_hjb",
                algorithm_id="neural_hjb", model_kind="critic_greedy",
                loader_method="greedy", mode="direct_tube", mix=1.,
                critic_family=critic_family, critic_kind=critic_kind,
                time_width=int(time_width), critic_step=critic_step,
                params=dict(P if primitives is None else primitives),
                method_fingerprint=method_fingerprint,
                online_input_gradient=True, online_scalar_bisections=44)


def load_policy(path, *, critic_factory=None):
    """Load canonical R15 policy metadata without using method names as aliases.

    Historical actor snapshots are also accepted, but retain their original
    identifiers.  The R15 evaluator must report method_id/algorithm_id, never
    infer a scientific comparison from the ``loader_method`` field.
    """
    state = torch.load(Path(path), map_location="cpu", weights_only=True)
    if state.get("schema") == "nbo-r15-candidate-v1" and critic_factory is None:
        from training_core import load_candidate
        return load_candidate(path)
    d = state["dimension"]
    family = state.get("critic_family", "r12_critic")
    if critic_factory is not None:
        critic = critic_factory(state)
    elif family == "split_critic":
        # This import is intentionally local: independent scalar/PDE operator
        # tests do not need the candidate-generation worker.  The production
        # source bundle supplies the authoritative shared factory.
        from training_core import SplitCritic
        critic = SplitCritic(d, state["params"], width=state["width"],
                             time_width=state.get("time_width", 16),
                             kind=state.get("critic_kind", "full_value"),
                             step=state.get("critic_step") or 1. / 64.)
    elif family == "r12_critic":
        critic = old.Critic(d, state["width"])
    else:
        raise ValueError("unknown critic family: " + family)
    critic.load_state_dict(state["critic"])
    critic.eval()
    kind = state.get("model_kind")
    if kind == "critic_greedy" or state["method"] == "greedy":
        actor = old.GreedyPolicy(critic, mode=state.get("mode", "direct_tube"),
                                 mix=state.get("mix", 1.), epsilon=state["epsilon"])
    else:
        actor = (old.LinearActor(d, state["epsilon"]) if state["method"] == "linear"
                 else old.Actor(d, state["width"], state["epsilon"]))
        actor.load_state_dict(state["actor"])
    actor.eval()
    return actor, critic, state


def distill_step(actor, critic, states, optimizer, *, epsilon=.1):
    """Optional same-capacity actor ablation; never relabelled canonical HJB.

    Matching greedy labels costs one critic gradient and 44 scalar iterations
    per state.  The final verifier evaluates the materialized actor itself.
    """
    target = make_policy(critic, epsilon)(states).detach()
    optimizer.zero_grad(set_to_none=True)
    loss = (actor(states) - target).square().mean()
    if not torch.isfinite(loss):
        raise FloatingPointError("nonfinite actor distillation objective")
    loss.backward()
    optimizer.step()
    return dict(loss=float(loss.detach()), actor_updates=1,
                actor_forward_states=len(states), input_gradient_states=len(states),
                greedy_action_states=len(states), greedy_scalar_iterations=44 * len(states),
                simulator_transitions=0)


def train(d, seed, out, *, seconds=20., epsilon=.1, width=32,
          max_iterations=10000, updates=1, batch=128, checkpoint_every=20,
          validation_paths=128, validation_steps=64, learning_rate=.002,
          probes=2, trace_mode="hutchinson", tag="", method_fingerprint=None):
    """Standalone baseline fit; worker orchestration may instead use hjb_step.

    The validation bank selects checkpoints only.  It is never an independent
    confirmation sample.  All candidates and failures remain in the record.
    """
    start = time.perf_counter()
    if d < 1 or seconds <= 0 or max_iterations < 1 or updates < 1 or batch < 1:
        raise ValueError("invalid baseline training budget")
    if epsilon <= 0 or checkpoint_every < 1 or validation_steps < 1:
        raise ValueError("invalid baseline action or validation specification")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    ident = f"neural_hjb_d{d}_s{seed}" + tag
    torch.manual_seed(seed)
    # The R12 initialization creates its actor first.  Consume that same draw
    # sequence so all methods start from identical scalar critic weights.
    discarded_actor = old.Actor(d, width, epsilon)
    del discarded_actor
    critic = old.Critic(d, width)
    B = torch.tensor(old.coupling(d))
    optimizer = torch.optim.Adam(critic.parameters(), lr=learning_rate)
    policy = make_policy(critic, epsilon)
    gs = torch.Generator().manual_seed(18000000 + seed)
    gt = torch.Generator().manual_seed(48000000 + seed)
    validation_seed = 38000000 + seed + d
    history, totals = [], {}
    selected, bestval, best = None, -math.inf, None
    failure, last, done = None, None, 0
    phases = {"initialization_seconds": time.perf_counter() - start,
              "optimizer_seconds": 0., "validation_seconds": 0.,
              "checkpoint_io_seconds": 0., "selected_weight_io_seconds": 0.}

    def checkpoint(iteration):
        nonlocal bestval, best, selected
        ts = time.perf_counter()
        vg = torch.Generator().manual_seed(validation_seed)
        xx = population_states(d, validation_paths, vg, False)
        with torch.no_grad():
            value, visits = old.rollout(policy, xx, B, vg, validation_steps)
        score = float(value.mean())
        if not math.isfinite(score):
            raise FloatingPointError("nonfinite neural HJB validation return")
        phases["validation_seconds"] += time.perf_counter() - ts
        for key, amount in dict(validation_state_visits=visits,
                                validation_input_gradient_states=visits,
                                validation_greedy_scalar_iterations=44 * visits).items():
            totals[key] = totals.get(key, 0) + amount
        snap = policy_snapshot(critic, dimension=d, width=width, epsilon=epsilon,
                               iteration=iteration, seed=seed,
                               method_fingerprint=method_fingerprint)
        ts = time.perf_counter()
        path = out / f"{ident}_k{iteration}.pt"
        torch.save(snap, path)
        checksum = file_sha256(path)
        phases["checkpoint_io_seconds"] += time.perf_counter() - ts
        history.append(dict(iteration=iteration, seconds=time.perf_counter() - start,
                            validation_return=score, loss=None if last is None else last["loss"],
                            work=dict(totals), weights_sha256=checksum,
                            method_id="neural_hjb", method_fingerprint=method_fingerprint))
        if score > bestval:
            bestval, best, selected = score, snap, iteration

    try:
        checkpoint(0)
        for iteration in range(1, max_iterations + 1):
            if time.perf_counter() - start >= seconds:
                break
            states = population_states(d, batch, gs)
            for _ in range(updates):
                last = hjb_step(critic, states, B, optimizer, gt, epsilon=epsilon,
                                probes=probes, trace_mode=trace_mode)
                phases["optimizer_seconds"] += last["seconds"]
                for key, amount in last.items():
                    if key not in {"loss", "seconds", "minimum_action", "maximum_action"}:
                        totals[key] = totals.get(key, 0) + amount
            done = iteration
            final = time.perf_counter() - start >= seconds or done == max_iterations
            if done % checkpoint_every == 0 or final:
                checkpoint(done)
            if final:
                break
        if done and history[-1]["iteration"] != done:
            checkpoint(done)
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    weights_hash = None
    if best is not None:
        ts = time.perf_counter()
        selected_path = out / f"{ident}.pt"
        torch.save(best, selected_path)
        weights_hash = file_sha256(selected_path)
        phases["selected_weight_io_seconds"] = time.perf_counter() - ts
    row = dict(id=ident, method="neural_hjb", method_id="neural_hjb",
               algorithm_id="neural_hjb", model_kind="critic_greedy",
               method_fingerprint=method_fingerprint, dimension=d, seed=seed,
               width=width, epsilon=epsilon, completed_iterations=done,
               selected_iteration=selected, requested_wall_seconds=seconds,
               seconds=time.perf_counter() - start, stages=phases, work=totals,
               history=history, failure=failure, weights_sha256=weights_hash,
               source_commit=source_commit(), trace_mode=trace_mode,
               independent_trace_banks=2 if trace_mode == "hutchinson" else 0,
               probes_per_bank=probes if trace_mode == "hutchinson" else 0,
               actor_parameter_count=0,
               critic_parameter_count=sum(p.numel() for p in critic.parameters()),
               online_input_gradient=True, online_scalar_bisections=44,
               validation_seed=validation_seed,
               selection="maximum declared validation-bank return, including initialization; independent confirmation required",
               budget_scope="internal fit through selected-weight serialization; outer worker charges startup, metadata and final verification",
               peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               scope="direct HJB collocation baseline in the same capital economy, scalar value capacity, state design, and feasible action tube; no uniform residual or optimizer-convergence claim")
    write_json(out / f"{ident}.json", row)
    return row


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dimension", type=int, default=10)
    parser.add_argument("--seed", type=int, default=7919)
    parser.add_argument("--seconds", type=float, default=20.)
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--trace-mode", choices=["hutchinson", "exact"], default="hutchinson")
    args = parser.parse_args()
    result = train(args.dimension, args.seed, args.out, seconds=args.seconds,
                   max_iterations=args.iterations, trace_mode=args.trace_mode)
    print(json.dumps({key: result[key] for key in
                      ["id", "seconds", "completed_iterations", "selected_iteration", "failure"]}))
