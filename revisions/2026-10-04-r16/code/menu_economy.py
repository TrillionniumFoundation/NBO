"""R16 finite-period capital menus with an exactly shared continuation target.

The stored binary64 weights, schedule, states and coupling matrices define exact
real coefficients of this finite Bellman problem. They are not asserted to be
an unqualified continuum approximation. A temporary current reward or action
constraint can change; every future primitive and the reference policy cannot.
Historical Python modules and their process globals are never imported here.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile

import numpy as np
import torch

torch.set_default_dtype(torch.float64)
torch.set_num_threads(1)
PRIMITIVE_KEYS = {"T", "discount", "productivity", "coupling", "idiosyncratic_sigma",
                  "common_sigma", "adjustment", "lower", "upper", "CHI"}


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def array_hash(value):
    x = np.ascontiguousarray(value, dtype="<f8")
    return hashlib.sha256(str(x.shape).encode()+x.tobytes()).hexdigest()


def stream_seed(seed, calibration, dimension, domain, stage=0):
    msg = f"NBO-R16-menu-v1/{int(seed)}/{calibration}/{int(dimension)}/{domain}/{stage}"
    return int.from_bytes(hashlib.sha256(msg.encode()).digest()[:8], "big") % (2**63-1)


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="."+path.name+".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as f:
            f.write(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False)+"\n")
            f.flush(); os.fsync(f.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def coefficient_proposal(primitives, steps):
    """Deterministic source-generation proposal; stored outputs define the model."""
    p, K = primitives, int(steps)
    h, rho, T = p["T"]/K, p["discount"], p["T"]
    left = np.arange(K)*h
    A = (np.exp(-rho*left)-np.exp(-rho*(left+h)))/rho
    W = A/rho+(1-1/rho)*math.exp(-rho*T)*h
    # A fixed midpoint quadrature proposes a feasible schedule. The saved
    # numbers themselves are the policy; no exact-average assertion is needed.
    dates = left[:, None]+(np.arange(512)[None, :]+.5)*h/512
    e = np.exp(-rho*(T-dates)); costate = (1-e)/rho+e
    schedule = np.mean(2/(costate+np.sqrt(costate*costate+4*p["adjustment"])), axis=1)
    return dict(A=A.tolist(), W=W.tolist(), schedule=schedule.tolist(),
                terminal_discount=float(math.exp(-rho*T)),
                terminal_penalty=float(p["CHI"]*math.exp(-rho*T)),
                drift_constant=float(p["productivity"]-(p["idiosyncratic_sigma"]**2+p["common_sigma"]**2)/2),
                noise_i_step=float(p["idiosyncratic_sigma"]*math.sqrt(h)),
                noise_c_step=float(p["common_sigma"]*math.sqrt(h)),
                interpretation="stored binary64 coefficients are exact finite-model inputs")


@dataclass
class MenuEconomy:
    calibration: dict
    dimension: int
    matrix: object

    def __post_init__(self):
        self.p = {k: float(v) for k, v in self.calibration["primitives"].items()}
        self.dimension = int(self.dimension)
        self.steps = int(self.calibration["steps"])
        if set(self.p) != PRIMITIVE_KEYS or self.steps < 2 or self.dimension < 1:
            raise ValueError("incomplete finite capital economy")
        if not all(math.isfinite(v) for v in self.p.values()):
            raise ValueError("nonfinite economic primitive")
        if not (0 < self.p["lower"] < self.p["upper"] and self.p["T"] > 0
                and self.p["discount"] > 0 and self.p["adjustment"] >= 0
                and self.p["CHI"] >= 0 and self.p["coupling"] >= 0
                and self.p["idiosyncratic_sigma"] >= 0 and self.p["common_sigma"] >= 0):
            raise ValueError("invalid primitive domain")
        self.h = self.p["T"]/self.steps
        co = self.calibration["coefficients"]
        self.A = np.asarray(co["A"], dtype=np.float64)
        self.W = np.asarray(co["W"], dtype=np.float64)
        self.schedule = np.asarray(co["schedule"], dtype=np.float64)
        self.terminal_discount = float(co["terminal_discount"])
        self.terminal_penalty = float(co["terminal_penalty"])
        self.gamma = 2*self.terminal_penalty
        self.noise_i = float(co["noise_i_step"])
        self.noise_c = float(co["noise_c_step"])
        self.B = np.asarray(self.matrix, dtype=np.float64)
        if (self.A.shape != (self.steps,) or self.W.shape != (self.steps,)
                or self.schedule.shape != (self.steps,)
                or self.B.shape != (self.dimension, self.dimension)):
            raise ValueError("finite coefficient shape mismatch")
        if (not all(np.isfinite(x).all() for x in [self.A, self.W, self.schedule, self.B])
                or np.any(self.A <= 0) or np.any(self.W <= 0)
                or np.any(self.schedule < self.p["lower"])
                or np.any(self.schedule > self.p["upper"])):
            raise ValueError("invalid finite coefficient or reference policy")
        self.c0 = float(co["drift_constant"])
        self.bt = torch.from_numpy(self.B.copy())
        self.at = torch.from_numpy(self.A.copy())
        self.wt = torch.from_numpy(self.W.copy())
        self.pit = torch.from_numpy(self.schedule.copy())
        self.continuation_identity = dict(schema="nbo-r16-menu-continuation-v1",
            primitives=self.p, dimension=self.dimension, steps=self.steps,
            coefficients=co, coupling_matrix_sha256=array_hash(self.B),
            innovation_law="independent standard Gaussian idiosyncratic and common shocks",
            first_noise_step="included at the supplied postdecision mean",
            reference_policy="stored feasible schedule at dates 1,...,K-1")
        self.continuation_sha256 = canonical_hash(self.continuation_identity)

    def drift(self, y, action):
        return self.c0+self.p["coupling"]*torch.tanh(y@self.bt.T)-action

    def postdecision(self, y, action):
        return y+self.h*self.drift(y, action)

    def base_value(self, x):
        centered = x-x.mean(1, keepdim=True)
        return -self.gamma/2*centered.square().mean(1, keepdim=True)

    def base_costate(self, x):
        return -self.gamma*(x-x.mean(1, keepdim=True))

    def current_payoff(self, y, action, tasks, include_common=False):
        w, eta = tasks["utility_weight"], tasks["adjustment"]
        mean = action.mean(1, keepdim=True)
        value = self.A[0]*(w*torch.log(action).mean(1, keepdim=True)-eta/2*mean.square())-self.W[0]*mean
        if include_common:
            value = value+self.W[0]*self.p["coupling"]*torch.tanh(y@self.bt.T).mean(1, keepdim=True)
        return value

    def continuation(self, x, innovations, counters=None):
        """Differentiable future payoff. innovations has shape [rep,K,row,d+1]."""
        if (innovations.ndim != 4 or innovations.shape[1] != self.steps
                or innovations.shape[2] != len(x) or innovations.shape[3] != self.dimension+1):
            raise ValueError("continuation innovation shape mismatch")
        p, d, n, reps = self.p, self.dimension, len(x), innovations.shape[0]
        values = []
        for z in innovations:
            noise = self.noise_i*z[0, :, :d]+self.noise_c*z[0, :, d:]
            y = x+noise
            reward = torch.zeros(n, 1, dtype=x.dtype)
            for k in range(1, self.steps):
                action = self.pit[k]
                production = p["coupling"]*torch.tanh(y@self.bt.T)
                reward = reward+self.wt[k]*(production.mean(1, keepdim=True)-action)
                reward = reward+self.at[k]*(torch.log(action)-p["adjustment"]/2*action.square())
                noise = self.noise_i*z[k, :, :d]+self.noise_c*z[k, :, d:]
                y = y+self.h*(self.c0+production-action)+noise
            reward = reward-self.gamma/2*(y-y.mean(1, keepdim=True)).square().mean(1, keepdim=True)
            values.append(reward)
        if counters is not None:
            counters["simulator_transitions"] += reps*n*self.steps
            counters["continuation_paths"] += reps*n
            counters["continuation_queries"] += n
        return torch.stack(values)

    def labels(self, x, innovations, counters=None):
        xx = x.detach().clone().requires_grad_(True)
        v = self.continuation(xx, innovations, counters)
        qs = []
        for r in range(len(v)):
            qs.append(self.dimension*torch.autograd.grad(v[r].sum(), xx,
                          retain_graph=r+1 < len(v), create_graph=False)[0])
        if counters is not None:
            counters["raw_costate_label_rows"] += len(v)*len(x)
            counters["backward_passes"] += len(v)
        return v.detach(), torch.stack(qs).detach()

    def cache_key(self, x, innovations):
        return canonical_hash(dict(continuation=self.continuation_sha256,
            states=array_hash(x.detach().cpu().numpy()),
            innovations=array_hash(innovations.detach().cpu().numpy())))


def noise_bank(economy, n, seed, replicates, counters=None):
    if int(replicates) < 2 or int(replicates) % 2:
        raise ValueError("an even number of antithetic paths is required")
    g = torch.Generator().manual_seed(int(seed))
    pairs = torch.randn(replicates//2, economy.steps, n, economy.dimension+1, generator=g).clamp(-10., 10.)
    result = torch.stack([pairs, -pairs], dim=1).flatten(0, 1)
    if counters is not None:
        counters["independent_gaussian_scalars_generated"] += pairs.numel()
        counters["innovation_scalars_materialized"] += result.numel()
    return result


def sample_states(n, dimension, seed):
    g = torch.Generator().manual_seed(int(seed))
    mean = torch.rand(n, 1, generator=g)-.5
    spread = .5*torch.rand(n, 1, generator=g)
    if dimension == 1:
        return mean
    z = torch.randn(n, dimension, generator=g)
    z = z-z.mean(1, keepdim=True)
    z = z/z.square().mean(1, keepdim=True).sqrt()
    return mean+spread*z


def task_tensors(tasks, ids=None):
    if ids is None:
        ids = torch.arange(len(tasks), dtype=torch.long)
    result = {}
    for key in ["utility_weight", "adjustment", "lower", "upper"]:
        a = torch.tensor([float(t[key]) for t in tasks])[:, None]
        result[key] = a[ids]
    return result


def fixed_queries(protocol, dimension):
    catalog = protocol["query_catalogs"][str(dimension)]
    states = np.asarray(catalog["states"], dtype=np.float64)
    if array_hash(states) != catalog["states_sha256"]:
        raise ValueError("fixed query catalog hash mismatch")
    tasks = protocol["tasks"]
    repeated = np.repeat(states, len(tasks), axis=0)
    result = dict(states=repeated,
        state_id=np.repeat(np.arange(len(states)), len(tasks)),
        task_id=np.tile(np.arange(len(tasks)), len(states)))
    for key in ["utility_weight", "adjustment", "lower", "upper"]:
        result[key] = np.tile(np.asarray([float(t[key]) for t in tasks]), len(states))[:, None]
    result["catalog_sha256"] = canonical_hash(dict(states=catalog["states_sha256"], tasks=tasks))
    return result


def load_economy(protocol, calibration_id, dimension):
    matches = [c for c in protocol["calibrations"] if c["id"] == calibration_id]
    if len(matches) != 1 or int(dimension) not in protocol["dimensions"]:
        raise ValueError("undeclared menu calibration or dimension")
    matrix = protocol["coupling_matrices"][str(dimension)]
    if array_hash(matrix["values"]) != matrix["sha256"]:
        raise ValueError("coupling matrix hash mismatch")
    return MenuEconomy(matches[0], int(dimension), matrix["values"])


def scalar_query_spec(protocol, economy):
    cfg = protocol["scalar_accuracy"]
    state_id, task_id = int(cfg["state_index"]), int(cfg["task_index"])
    state = np.asarray(protocol["query_catalogs"][str(economy.dimension)]["states"][state_id])
    task = protocol["tasks"][task_id]
    radius = float(cfg["action_radius"])
    left = np.full(economy.dimension, max(float(task["lower"]), float(economy.schedule[0])-radius))
    right = np.full(economy.dimension, min(float(task["upper"]), float(economy.schedule[0])+radius))
    return dict(state=state.tolist(), task=task, a_left=left.tolist(), a_right=right.tolist(),
        query_id=dict(state_index=state_id, task_index=task_id, task_id=task["id"]),
        continuation_sha256=economy.continuation_sha256,
        action_class="one common withdrawal rate in the fixed reference +/- radius segment, followed by the same future policy",
        class_selected_before_fitting=True)
