"""Explicit R16 calibration adapter around byte-preserved R15 kernels.

Each worker process binds exactly one economic design.  The adapter replaces
the R15 training entry-point guard in memory and uses the explicit R16 verifier;
no historical file is edited.  Copied scalar CHI aliases and the defining
globals of imported functions are checked, in addition to shared P objects.
New constants and quadrature weights must be computed after binding.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
R15 = ROOT / "revisions/2026-10-04-r15"
_ACTIVE_BINDING = None
PRIMITIVE_KEYS = {"T", "discount", "productivity", "coupling",
    "idiosyncratic_sigma", "common_sigma", "adjustment", "lower", "upper", "CHI"}


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def _validated(primitives, epsilon, population):
    p = {key: float(value) for key, value in primitives.items()}
    if set(p) != PRIMITIVE_KEYS or not all(math.isfinite(x) for x in p.values()):
        raise ValueError("complete finite R16 primitive dictionary required")
    fixed = dict(discount=.04, productivity=.1, adjustment=.2, lower=.02, upper=2.)
    if any(p[key] != value for key, value in fixed.items()):
        raise ValueError("R16 keeps discount, productivity, adjustment, and primitive action box fixed")
    if p["T"] not in (1., 2.) or p["CHI"] not in (.03, .1):
        raise ValueError("R16 horizon or terminal dispersion outside registered envelope")
    if not (0 < p["coupling"] <= .3 and 0 <= p["idiosyncratic_sigma"] <= .6
            and 0 <= p["common_sigma"] <= .3):
        raise ValueError("R16 coupling or volatility outside registered envelope")
    epsilon = float(epsilon)
    if epsilon not in (.1, .2):
        raise ValueError("R16 action radius outside registered envelope")
    if not {"means", "spreads"}.issubset(population) or set(population)-{"means", "spreads", "weights"}:
        raise ValueError("initial population requires explicit means and spreads")
    weights = population.get("weights")
    population = {name: [float(x) for x in population[name]] for name in ("means", "spreads")}
    if (len(population["means"]) != 3 or len(population["spreads"]) != 3
            or not all(math.isfinite(x) for values in population.values() for x in values)
            or min(population["spreads"]) < 0):
        raise ValueError("R16 uses an explicit nine-profile population")
    if weights is not None:
        if not isinstance(weights, str) or not weights.startswith("uniform over nine"):
            raise ValueError("R16 explicitly uses the uniform nine-profile law")
        population["weights"] = weights
    rho, adjustment = p["discount"], p["adjustment"]
    def center(t):
        e = math.exp(-rho*(p["T"]-t))
        w = (1-e)/rho+e
        return 2/(w+math.sqrt(w*w+4*adjustment))
    if center(0)-epsilon <= p["lower"] or center(p["T"])+epsilon >= p["upper"]:
        raise ValueError("registered schedule tube is not strictly inside the primitive action box")
    return p, epsilon, population


@dataclass
class BoundCapital:
    params: dict
    epsilon: float
    population: dict
    calibration_id: str
    core: object
    verifier: object
    modules: tuple
    function_globals: tuple

    @property
    def primitives_sha256(self):
        return canonical_hash(self.params)

    @property
    def identity(self):
        return dict(primitives=self.params, epsilon=self.epsilon,
                    initial_state_population=self.population, calibration_id=self.calibration_id)

    @property
    def identity_sha256(self):
        return canonical_hash(self.identity)

    def support(self, dimension):
        d = int(dimension)
        if d < 1:
            raise ValueError("positive economic dimension required")
        if d == 1:
            pattern = np.zeros(1, dtype=np.float64)
        else:
            pattern = np.linspace(-1., 1., d)
            pattern -= pattern.mean()
            pattern /= np.sqrt(np.mean(pattern*pattern))
        return np.asarray([mean+spread*pattern for mean in self.population["means"]
                           for spread in self.population["spreads"]], dtype=np.float64)

    def assert_bound(self):
        expected = {k: v for k, v in self.params.items() if k != "CHI"}
        for module in self.modules:
            if hasattr(module, "P") and dict(module.P) != expected:
                raise AssertionError("mixed economic P alias: "+module.__name__)
            if hasattr(module, "CHI") and float(module.CHI) != self.params["CHI"]:
                raise AssertionError("mixed terminal-dispersion alias: "+module.__name__)
        for label, namespace in self.function_globals:
            if "P" in namespace and dict(namespace["P"]) != expected:
                raise AssertionError("mixed defining-function P: "+label)
            if "CHI" in namespace and float(namespace["CHI"]) != self.params["CHI"]:
                raise AssertionError("mixed defining-function CHI: "+label)
        return True

    def _accept_primitives(self, primitives):
        requested = {key: float(value) for key, value in primitives.items()}
        if requested != self.params:
            raise ValueError("worker attempted to cross its fixed R16 economic identity")
        self.assert_bound()
        return dict(self.params)

    def validate_protocol(self, protocol):
        if protocol["design"]["primitives"] != self.params:
            raise ValueError("training protocol has different primitives")
        if protocol["design"]["primitives_sha256"] != self.primitives_sha256:
            raise ValueError("training primitive hash mismatch")
        if float(protocol["training"]["epsilon"]) != self.epsilon:
            raise ValueError("training radius differs from the bound economy")
        if protocol["design"]["initial_state_population"] != self.population:
            raise ValueError("training initial population differs from the verifier")
        self.assert_bound()

    def training_run(self, protocol, dimension, seed, method_id, out, metadata=None):
        self.validate_protocol(protocol)
        if method_id not in ("nbo", "raw_costate", "direct_policy"):
            raise ValueError("R16 strong HJB uses its explicit standalone implementation")
        return self.core.TrainingRun(protocol, dimension, seed, method_id, out, metadata)

    def load_candidate(self, path):
        self.assert_bound()
        actor, critic, state = self.core.load_candidate(path)
        if state["params"] != self.params or float(state["epsilon"]) != self.epsilon:
            raise ValueError("candidate has a different bound economic identity")
        return actor, critic, state

    def held_reference(self, steps):
        self.assert_bound()
        weights = self.core.training_weights(int(steps))
        return weights["M"]/(self.params["T"]/int(steps))

    def audit_record(self, quadrature_steps=64):
        self.assert_bound()
        pc = importlib.import_module("policy_certificate")
        neural = importlib.import_module("tube_neural")
        torch = self.core.torch
        weights = pc.weights(quadrature_steps)
        if weights["h"] != self.params["T"]/quadrature_steps:
            raise AssertionError("quadrature horizon does not match training/verifier horizon")
        test = torch.tensor([[.3, -.2, .7], [-.4, .5, -.1]], dtype=torch.float64)
        expected = test.mean(1, keepdim=True)-self.params["CHI"]*(test-test.mean(1, keepdim=True)).square().mean(1, keepdim=True)
        error = float((neural.terminal(test)-expected).abs().max())
        if error != 0.:
            raise AssertionError("terminal function uses a stale copied dispersion penalty")
        root_files = {}
        for module in self.modules:
            path = Path(module.__file__).resolve()
            root_files[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        return dict(schema="nbo-r16-capital-binding-v1", identity=self.identity,
            identity_sha256=self.identity_sha256, primitives_sha256=self.primitives_sha256,
            module_aliases=[module.__name__ for module in self.modules],
            defining_functions=[label for label, _ in self.function_globals],
            source_sha256=root_files, quadrature_steps=quadrature_steps,
            quadrature_step=weights["h"], terminal_identity_error=error,
            process_scope="one fixed economic design per fresh worker process",
            random_stream_domain="NBO-R16-robustness-v1/"+self.calibration_id,
            historical_source_files_modified=False,
            roundoff_and_transfer_scope="fresh calibration-specific constants required; this binding audit is not a transfer proof")


def active_binding():
    if _ACTIVE_BINDING is None:
        raise RuntimeError("R16 verifier requires an explicitly bound economic design")
    _ACTIVE_BINDING.assert_bound()
    return _ACTIVE_BINDING


def bind_economy(primitives, epsilon, initial_state_population, calibration_id):
    """Return the isolated R16 economic binding and validated R15 interfaces."""
    global _ACTIVE_BINDING
    params, epsilon, population = _validated(primitives, epsilon, initial_state_population)
    identity = dict(primitives=params, epsilon=epsilon, initial_state_population=population,
                    calibration_id=str(calibration_id))
    if _ACTIVE_BINDING is not None:
        if _ACTIVE_BINDING.identity != identity:
            raise RuntimeError("a worker process may not change its R16 economic design")
        _ACTIVE_BINDING.assert_bound()
        return _ACTIVE_BINDING
    for path in [R15/"code", ROOT/"revisions/2026-10-04-r12/code"]:
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    core = importlib.import_module("training_core")
    verifier = importlib.import_module("capital_verifier")
    baselines = importlib.import_module("baselines")
    names = ("common", "bellman_study", "tube_neural", "tube_certificate", "policy_certificate")
    modules = tuple(importlib.import_module(name) for name in names)+(core, verifier, baselines, baselines.legacy)
    expected = {key: value for key, value in params.items() if key != "CHI"}
    for module in modules:
        if hasattr(module, "P"):
            module.P.clear()
            module.P.update(expected)
        if hasattr(module, "CHI"):
            module.CHI = params["CHI"]
    globals_to_check = []
    for name in names:
        module = sys.modules[name]
        for attribute in ("schedule", "terminal", "flow", "drift", "greedy", "weights",
                          "constants", "schedule_i", "enclosure", "rollout"):
            function = getattr(module, attribute, None)
            if callable(function) and hasattr(function, "__globals__"):
                globals_to_check.append((name+"."+attribute, function.__globals__))
    globals_to_check.append(("tube_neural.Actor.forward", core.old.Actor.forward.__globals__))
    bound = BoundCapital(params, epsilon, population, str(calibration_id), core, verifier,
                         modules, tuple(globals_to_check))
    bound.assert_bound()

    def configure(primitives):
        return bound._accept_primitives(primitives)

    def stream_seed(seed, dimension, domain, stage=0):
        word = f"NBO-R16-robustness-v1/{bound.calibration_id}/{seed}/{dimension}/{domain}/{stage}"
        return int.from_bytes(hashlib.sha256(word.encode()).digest()[:8], "big") % (2**63-1)

    core.configure_primitives = configure
    core.stream_seed = stream_seed
    _ACTIVE_BINDING = bound
    return bound
