"""Five strong, reusable R16 menu candidate generators, before confirmation.

NBO and vector regression receive identical cached off-policy derivative rows.
Raw actors reuse every derivative over all tasks. DPO reuses all innovations and
materializes one task-conditioned actor. SAA retains its innovation bank as its
budget increases. Every saved action is evaluated later by a separate verifier.
"""
from __future__ import annotations

from collections import defaultdict
import copy
import hashlib
import math
import os
from pathlib import Path
import time

import numpy as np
import torch
from torch import nn

from menu_economy import (array_hash, canonical_hash, fixed_queries, noise_bank,
                          sample_states, scalar_query_spec, stream_seed, task_tensors, write_json)

METHODS = ("nbo_scalar", "vector_costate", "raw_actor", "dpo_actor", "raw_saa")


def sync_file(path):
    with Path(path).open("rb") as f:
        os.fsync(f.fileno())


def save_shards(stem, arrays, axes, rows_per_shard):
    """Store every array losslessly while keeping individual files bounded."""
    stem = Path(stem)
    counts = {np.asarray(arrays[k]).shape[axes[k]] for k in arrays}
    if len(counts) != 1:
        raise ValueError("cache arrays do not share their declared row axis")
    count = counts.pop(); files = []
    for part, start in enumerate(range(0, count, rows_per_shard)):
        stop = min(count, start+rows_per_shard)
        payload = {}
        for key, value in arrays.items():
            index = [slice(None)]*value.ndim
            index[axes[key]] = slice(start, stop)
            payload[key] = value[tuple(index)]
        path = stem.with_name(stem.name+f"_part{part:03d}.npz")
        np.savez_compressed(path, **payload); sync_file(path)
        files.append(dict(path=path.name, start=start, stop=stop,
            bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    manifest = stem.with_name(stem.name+"_manifest.json")
    write_json(manifest, dict(schema="nbo-r16-lossless-cache-shards-v1", total_rows=count,
        axes=axes, arrays={k: dict(shape=list(v.shape), sha256=array_hash(v)) for k, v in arrays.items()},
        antithetic_reconstruction="independent_innovations[p] then its exact negative, interleaved; no independent innovation is dropped",
        parts=files))
    return manifest


def mlp(inputs, outputs, width):
    model = nn.Sequential(nn.Linear(inputs, width), nn.Tanh(),
        nn.Linear(width, width), nn.Tanh(), nn.Linear(width, outputs))
    nn.init.zeros_(model[-1].weight)
    nn.init.zeros_(model[-1].bias)
    return model


class ScalarContinuation(nn.Module):
    def __init__(self, economy, width):
        super().__init__()
        self.economy = economy
        self.space = mlp(economy.dimension+1, 1, width)
        self.register_buffer("intercept", torch.zeros(1))

    def forward(self, x):
        e = self.economy
        tx = torch.cat([torch.full((len(x), 1), e.h), x], 1)
        return e.base_value(x)+(e.p["T"]-e.h)*self.space(tx)/e.dimension+self.intercept

    def costate(self, x, create_graph=False):
        xx = x.detach().requires_grad_(True)
        return self.economy.dimension*torch.autograd.grad(self(xx).sum(), xx,
                                                          create_graph=create_graph)[0]


class VectorCostate(nn.Module):
    def __init__(self, economy, width):
        super().__init__()
        self.economy = economy
        self.space = mlp(economy.dimension+1, economy.dimension, width)

    def forward(self, x):
        e = self.economy
        tx = torch.cat([torch.full((len(x), 1), e.h), x], 1)
        return e.base_costate(x)+(e.p["T"]-e.h)*self.space(tx)

    def costate(self, x, create_graph=False):
        return self(x)


class TaskActor(nn.Module):
    def __init__(self, economy, width):
        super().__init__()
        self.economy = economy
        self.space = mlp(economy.dimension+4, economy.dimension, width)

    def forward(self, y, task):
        lo, hi = task["lower"], task["upper"]
        center = torch.full_like(lo, float(self.economy.schedule[0]))
        frac = ((center-lo)/(hi-lo)).clamp(.01, .99)
        offset = torch.log(frac)-torch.log1p(-frac)
        inp = torch.cat([y]+[task[k] for k in ["utility_weight", "adjustment", "lower", "upper"]], 1)
        return lo+(hi-lo)*torch.sigmoid(offset+self.space(inp))


def guarded_actions(value, tasks):
    lo, hi = tasks["lower"].numpy(), tasks["upper"].numpy()
    x = np.asarray(value.detach().numpy(), dtype=np.float64)
    if not np.isfinite(x).all():
        raise FloatingPointError("nonfinite deployed menu action")
    return np.minimum(np.nextafter(hi, lo), np.maximum(np.nextafter(lo, hi), x))


def solve_actions(economy, states, tasks, cfg, counters, *, field=None, innovations=None,
                  initial_actions=None):
    if (field is None) == (innovations is None):
        raise ValueError("choose exactly one reusable field or cached SAA objective")
    lo, hi = tasks["lower"], tasks["upper"]
    if initial_actions is None:
        center = torch.full_like(states, float(economy.schedule[0]))
    else:
        center = torch.as_tensor(initial_actions, dtype=torch.float64)
    frac = ((center-lo)/(hi-lo)).clamp(.0001, .9999)
    latent = nn.Parameter(torch.log(frac)-torch.log1p(-frac))
    optimizer = torch.optim.Adam([latent], lr=cfg["query_learning_rate"])
    def action():
        return lo+(hi-lo)*torch.sigmoid(latent)
    def objective():
        a = action()
        post = economy.postdecision(states, a)
        if field is not None:
            q = field.costate(post, create_graph=False).detach()
            value = -economy.h*(q*a).mean(1, keepdim=True)
            counters["cached_surrogate_queries"] += len(states)
            if isinstance(field, ScalarContinuation):
                counters["critic_forward_rows"] += len(states)
                counters["first_derivative_rows"] += len(states)
            else:
                counters["vector_forward_rows"] += len(states)
        else:
            value = economy.continuation(post, innovations, counters).mean(0)
            counters["cached_innovation_rows_consumed"] += innovations.shape[0]*len(states)
        return economy.current_payoff(states, a, tasks)+value
    for _ in range(cfg["query_updates"]):
        loss = -objective().mean()
        if not torch.isfinite(loss):
            raise FloatingPointError("nonfinite query objective")
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
        counters["query_action_updates"] += len(states)
        counters["backward_passes"] += 2 if isinstance(field, ScalarContinuation) else 1
    # An independently declared fixed objective is available for scalar NBO and
    # SAA. Vector-field queries instead retain the same Adam root procedure.
    refinement = dict(available=not isinstance(field, VectorCostate), closure_calls=0)
    if refinement["available"] and cfg["query_lbfgs_iterations"]:
        optimizer = torch.optim.LBFGS([latent], max_iter=cfg["query_lbfgs_iterations"],
            max_eval=cfg["query_lbfgs_evaluations"], line_search_fn="strong_wolfe",
            tolerance_grad=1e-10, tolerance_change=1e-12)
        def closure():
            optimizer.zero_grad(set_to_none=True)
            a = action(); post = economy.postdecision(states, a)
            if field is None:
                future = economy.continuation(post, innovations, counters).mean(0)
            else:
                future = field(post)
                counters["critic_forward_rows"] += len(states)
                counters["first_derivative_rows"] += len(states)
            loss = -(economy.current_payoff(states, a, tasks)+future).mean()
            if not torch.isfinite(loss):
                raise FloatingPointError("nonfinite query refinement objective")
            loss.backward(); refinement["closure_calls"] += 1
            counters["backward_passes"] += 1
            return loss
        optimizer.step(closure)
        counters["query_lbfgs_closures"] += refinement["closure_calls"]
    return guarded_actions(action(), tasks), refinement


class MenuRun:
    def __init__(self, economy, protocol, method, seed, out):
        if method not in METHODS or method not in protocol["methods"]:
            raise ValueError("undeclared menu candidate method")
        self.e, self.protocol, self.method, self.seed = economy, protocol, method, int(seed)
        self.out = Path(out); self.out.mkdir(parents=True, exist_ok=True)
        self.cfg = protocol["training"]
        self.counters, self.history = defaultdict(int), []
        self.stage = 0
        self.data = {}
        self.queries = fixed_queries(protocol, economy.dimension)
        self.ystate = torch.from_numpy(self.queries["states"])
        self.query_tasks = {k: torch.from_numpy(self.queries[k]) for k in
                            ["utility_weight", "adjustment", "lower", "upper"]}
        torch.manual_seed(self.sseed("initialization"))
        self.model = (ScalarContinuation(economy, self.cfg["field_width"]) if method == "nbo_scalar"
            else VectorCostate(economy, self.cfg["field_width"]) if method == "vector_costate"
            else TaskActor(economy, self.cfg["actor_width"]) if method in ["raw_actor", "dpo_actor"] else None)
        self.actor_optimizer = (torch.optim.Adam(self.model.parameters(), lr=self.cfg["actor_learning_rate"])
                               if method in ["raw_actor", "dpo_actor"] else None)
        self.saa_innovations = None
        self.saa_actions = None
        self.saa_generator = torch.Generator().manual_seed(self.sseed("saa_query_noise"))

    def sseed(self, domain, stage=0):
        return stream_seed(self.seed, self.e.calibration["id"], self.e.dimension, domain, stage)

    def append_replay(self, target, stage):
        previous = len(self.data.get("states", []))
        count = target-previous
        if count <= 0:
            raise ValueError("nonincreasing declared menu replay budget")
        y = sample_states(count, self.e.dimension, self.sseed("training_states", stage))
        generator = torch.Generator().manual_seed(self.sseed("postdecision_training_actions", stage))
        a = self.e.p["lower"]+(self.e.p["upper"]-self.e.p["lower"])*torch.rand(count, self.e.dimension, generator=generator)
        if self.method == "raw_actor":
            a = torch.full_like(y, float(self.e.schedule[0]))
        x = self.e.postdecision(y, a)
        z = noise_bank(self.e, count, self.sseed("shared_continuation_labels", stage),
                       self.cfg["label_antithetic_paths"], self.counters)
        new = dict(states=y, postdecision=x, training_actions=a)
        if self.method in ["nbo_scalar", "vector_costate", "raw_actor"]:
            v, q = self.e.labels(x, z, self.counters)
            new.update(value_replicates=v, costate_replicates=q)
        else:
            new["innovations"] = z
        for key, value in new.items():
            axis = 2 if key == "innovations" else 1 if key.endswith("replicates") else 0
            self.data[key] = value if key not in self.data else torch.cat([self.data[key], value], dim=axis)
        self.counters["training_state_rows"] += count
        self.counters["postdecision_state_rows"] += count
        # Every original label bank is durable and has an exact target key.
        payload = {key: value.numpy() for key, value in new.items()}
        payload.pop("innovations", None)
        payload["independent_innovations"] = z[::2].numpy()
        axes = {key: 2 if key == "independent_innovations" else 1 if key.endswith("replicates") else 0 for key in payload}
        label_file = save_shards(self.out/f"label_bank_stage{stage}", payload, axes, 128)
        return dict(new_rows=count, cache_key=self.e.cache_key(x, z),
            cache_file=label_file.name, cache_sha256=hashlib.sha256(label_file.read_bytes()).hexdigest())

    def fit_field(self, stage, generator):
        x = self.data["postdecision"]
        target = self.data["costate_replicates"].mean(0)
        parameters = list(self.model.space.parameters())
        optimizer = torch.optim.Adam(parameters, lr=self.cfg["field_learning_rate"])
        n = len(x)
        def prediction(xx, graph):
            self.counters["critic_forward_rows" if self.method == "nbo_scalar" else "vector_forward_rows"] += len(xx)
            if self.method == "nbo_scalar":
                self.counters["first_derivative_rows"] += len(xx)
                if graph:
                    self.counters["second_derivative_rows"] += len(xx)
            return self.model.costate(xx, create_graph=graph)
        for _ in range(self.cfg["field_adam_updates_per_stage"]):
            ids = torch.randint(n, (self.cfg["batch_size"],), generator=generator)
            loss = (prediction(x[ids], True)-target[ids]).square().mean()
            if not torch.isfinite(loss):
                raise FloatingPointError("nonfinite continuation regression")
            optimizer.zero_grad(set_to_none=True); loss.backward(); optimizer.step()
            self.counters["field_adam_updates"] += 1
            self.counters["backward_passes"] += 2 if self.method == "nbo_scalar" else 1
        optimizer = torch.optim.LBFGS(parameters, max_iter=self.cfg["field_lbfgs_iterations"],
            max_eval=self.cfg["field_lbfgs_evaluations"], line_search_fn="strong_wolfe",
            tolerance_grad=1e-10, tolerance_change=1e-12)
        closure_calls = 0
        def closure():
            nonlocal closure_calls
            optimizer.zero_grad(set_to_none=True)
            loss = (prediction(x, True)-target).square().mean()
            if not torch.isfinite(loss):
                raise FloatingPointError("nonfinite full-replay continuation loss")
            loss.backward(); closure_calls += 1
            self.counters["backward_passes"] += 2 if self.method == "nbo_scalar" else 1
            return loss
        optimizer.step(closure)
        self.counters["field_lbfgs_closures"] += closure_calls
        if self.method == "nbo_scalar":
            with torch.no_grad():
                self.model.intercept.zero_()
                self.model.intercept.copy_((self.data["value_replicates"].mean(0)-self.model(x)).mean().reshape(1))
        with torch.enable_grad():
            mse = float((prediction(x, False).detach()-target).square().mean())
        return dict(replay_costate_mse=mse, lbfgs_closure_calls=closure_calls,
                    metric_scope="training diagnostic only; not continuation risk or welfare")

    def fit_actor(self, stage, generator):
        y = self.data["states"]
        q = self.data["costate_replicates"].mean(0) if self.method == "raw_actor" else None
        losses = []
        for it in range(self.cfg["actor_updates_per_stage"]):
            ids = torch.randint(len(y), (self.cfg["batch_size"],), generator=generator)
            # Any current task may reuse the same state/continuation label.
            task_ids = torch.randint(len(self.protocol["tasks"]), (len(ids),), generator=generator)
            task = task_tensors(self.protocol["tasks"], task_ids)
            action = self.model(y[ids], task)
            if q is not None:
                future = -self.e.h*(q[ids]*action).mean(1, keepdim=True)
                self.counters["cached_costate_rows_consumed"] += len(ids)
            else:
                innovations = self.data["innovations"][:, :, ids]
                future = self.e.continuation(self.e.postdecision(y[ids], action), innovations, self.counters).mean(0)
                self.counters["cached_innovation_rows_consumed"] += innovations.shape[0]*len(ids)
            loss = -(self.e.current_payoff(y[ids], action, task)+future).mean()
            if not torch.isfinite(loss):
                raise FloatingPointError("nonfinite task actor objective")
            self.actor_optimizer.zero_grad(set_to_none=True); loss.backward(); self.actor_optimizer.step()
            self.counters["actor_updates"] += 1
            self.counters["actor_forward_rows"] += len(ids)
            self.counters["backward_passes"] += 1
            if it in (0, self.cfg["actor_updates_per_stage"]-1):
                losses.append(dict(update=it+1, training_loss=float(loss.detach())))
        return dict(training_losses=losses,
            metric_scope="cached shared-label task actor objective; no held-out economic claim")

    def scalar_candidate(self):
        if self.method != "nbo_scalar":
            raise ValueError("the registered scalar diagnostic uses the final NBO continuation")
        spec = scalar_query_spec(self.protocol, self.e)
        grid = torch.linspace(0., 1., self.protocol["scalar_accuracy"]["candidate_grid_points"])
        left, right = torch.tensor(spec["a_left"]), torch.tensor(spec["a_right"])
        actions = left[None, :]+grid[:, None]*(right-left)[None, :]
        states = torch.tensor(spec["state"])[None, :].expand(len(grid), -1)
        tasks = task_tensors([spec["task"]], torch.zeros(len(grid), dtype=torch.long))
        with torch.no_grad():
            values = self.e.current_payoff(states, actions, tasks)+self.model(self.e.postdecision(states, actions))
        chosen = int(values.argmax())
        self.counters["critic_forward_rows"] += len(grid)
        self.counters["scalar_candidate_grid_queries"] += len(grid)
        spec.update(candidate_s=float(grid[chosen]), selected_grid_index=chosen,
            candidate_grid_points=len(grid), selected_critic_values_sha256=array_hash(values.numpy()),
            selection="maximum of the frozen scalar-critic Q over the declared grid; no confirmation outcomes",
            failed_fit=False, stage=self.stage, seed=self.seed,
            primary_vector_candidate_unchanged=True)
        np.savez_compressed(self.out/"scalar_candidate_grid.npz", scalar_parameters=grid.numpy(),
                            critic_values=values.numpy())
        sync_file(self.out/"scalar_candidate_grid.npz")
        write_json(self.out/"SCALAR_CANDIDATE.json", spec)
        return spec

    def advance(self, stage):
        if stage != self.stage+1 or stage > len(self.cfg["cumulative_replay_states"]):
            raise ValueError("menu work stages must advance exactly once")
        start = time.perf_counter()
        details = {}
        if self.method != "raw_saa":
            details["new_cache"] = self.append_replay(self.cfg["cumulative_replay_states"][stage-1], stage)
            generator = torch.Generator().manual_seed(self.sseed("shared_optimizer_minibatches", stage))
            if self.method in ["nbo_scalar", "vector_costate"]:
                details.update(self.fit_field(stage, generator))
                for parameter in self.model.parameters():
                    parameter.requires_grad_(False)
                actions, solve = solve_actions(self.e, self.ystate, self.query_tasks,
                    self.cfg, self.counters, field=self.model)
                for parameter in self.model.parameters():
                    parameter.requires_grad_(True)
                details["query_solver"] = solve
            else:
                details.update(self.fit_actor(stage, generator))
                with torch.no_grad():
                    actions = guarded_actions(self.model(self.ystate, self.query_tasks), self.query_tasks)
                self.counters["actor_forward_rows"] += len(actions)
        else:
            paths = self.cfg["saa_antithetic_paths"][stage-1]
            # Draw only the new pairs from a persistent generator. Earlier
            # innovations are reused as stored; none are regenerated.
            old_paths = 0 if self.saa_innovations is None else len(self.saa_innovations)
            fresh = torch.randn((paths-old_paths)//2, self.e.steps, len(self.ystate),
                self.e.dimension+1, generator=self.saa_generator).clamp(-10., 10.)
            new_paths = torch.stack([fresh, -fresh], dim=1).flatten(0, 1)
            z = new_paths if self.saa_innovations is None else torch.cat([self.saa_innovations, new_paths], 0)
            self.counters["independent_gaussian_scalars_generated"] += (paths-old_paths)//2*self.e.steps*len(self.ystate)*(self.e.dimension+1)
            self.counters["innovation_scalars_materialized"] += (paths-old_paths)*self.e.steps*len(self.ystate)*(self.e.dimension+1)
            self.saa_innovations = z
            actions, solve = solve_actions(self.e, self.ystate, self.query_tasks,
                self.cfg, self.counters, innovations=z, initial_actions=self.saa_actions)
            self.saa_actions = actions
            details.update(query_solver=solve, antithetic_paths=paths,
                cache_prefix_preserved=True, unchanged_query_noise=True)
            cache_manifest = save_shards(self.out/f"saa_noise_stage{stage}",
                dict(independent_innovations=fresh.numpy()), dict(independent_innovations=2), 64)
            details["new_noise_cache"] = dict(path=cache_manifest.name,
                previous_paths=old_paths, new_independent_pairs=(paths-old_paths)//2,
                sha256=hashlib.sha256(cache_manifest.read_bytes()).hexdigest())
        self.stage = stage
        if self.method == "nbo_scalar" and stage == len(self.cfg["cumulative_replay_states"]):
            details["scalar_candidate"] = self.scalar_candidate()
        path = self.out/f"actions_stage{stage}.npz"
        np.savez_compressed(path, actions=actions, states=self.queries["states"],
            task_id=self.queries["task_id"], state_id=self.queries["state_id"],
            **{k: self.queries[k] for k in ["utility_weight", "adjustment", "lower", "upper"]})
        sync_file(path)
        if self.model is not None:
            model_path = self.out/f"model_stage{stage}.pt"
            torch.save(dict(method=self.method, stage=stage, calibration=self.e.calibration["id"],
                continuation_sha256=self.e.continuation_sha256, seed=self.seed,
                model=copy.deepcopy(self.model.state_dict()), configuration=self.cfg,
                final_confirmation_used=False), model_path)
            sync_file(model_path)
        row = dict(stage=stage, seconds=time.perf_counter()-start, method=self.method,
            actions_file=path.name, actions_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            deployed_action_array_sha256=array_hash(actions),
            min_action=float(actions.min()), max_action=float(actions.max()),
            counters=dict(self.counters), continuation_sha256=self.e.continuation_sha256,
            query_catalog_sha256=self.queries["catalog_sha256"], **details)
        self.history.append(row)
        write_json(self.out/f"stage{stage}.json", row)
        return row
