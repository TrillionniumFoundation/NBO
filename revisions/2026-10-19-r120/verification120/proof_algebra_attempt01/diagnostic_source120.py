#!/usr/bin/env python3
"""Post-freeze exact algebra diagnostics for the R120 proof/implementation bridge.

This source was prepared AFTER scientific freeze F. It is not part of F, is not
a preregistered economic experiment, and cannot modify an actor, sample, policy,
protocol, scientific source, or earlier result. Run only after the controlled
primary/timing processes have ended. The output is an exclusive new directory.

The checks use exact rational polynomial identities, certified affine-corner
bounds, constructive information witnesses, constrained quadratic examples, and
fixed rounding edge cases. They do not call an economic solver, evaluate V1,
train a model, generate initial states, or replay the primary service. A finite
diagnostic does not replace the full mathematical proofs, prove every theorem,
or establish a neural-specific advantage.

All 157 scientific inputs, including the archived mathematical snapshot, are
bound to F before NumPy or any isolated numerical definition is loaded. Only
the frozen interval definitions and the two frozen arithmetic helper functions
are executed from scientific source. The improvement/campaign modules are never
imported. The square-root reference uses integer bisection, not math.isqrt.

Example (the parent author controls when this is actually executed):
  python verification120/proof_algebra120.py \
    --source-commit 369d02724cf12ae0e54390b4e7b5f894f703892e \
    --out verification120/proof_algebra_attempt01
"""
from __future__ import annotations

import argparse
import ast
from fractions import Fraction as Q
import hashlib
import itertools
import json
import math
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import time
import traceback
from types import SimpleNamespace


FROZEN_COMMIT = "369d02724cf12ae0e54390b4e7b5f894f703892e"
FROZEN_COUNT = 157
REVISION = Path(__file__).resolve().parents[1]
BETA, RADIUS, MZ = Q(15, 16), Q(1, 32), Q(181, 64)
SCOPE = {
    "identity": "post-freeze deterministic proof and arithmetic diagnostic",
    "preregistered_economic_experiment": False,
    "economic_solver_calls": 0,
    "model_training_calls": 0,
    "sample_acquisitions": 0,
    "primary_or_timing_replays": 0,
    "full_independent_proof_of_all_theorems": False,
    "information_lower_bound_scope":
        "convex K-Lipschitz scalar-value oracle class with a known fixed density",
    "not_a_lower_bound_for":
        "fixed parametric investment primitives with formula or derivative access",
    "tail_examples_scope":
        "exact quadratic diagnostics including constrained optimizer boundaries",
    "frozen_scientific_source_modified": False,
}


def serial(value):
    if isinstance(value, Q):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [serial(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return {"nonfinite": repr(value)}
    return value


def write_json(path, obj):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(serial(obj), stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


class Checks:
    def __init__(self, out):
        self.out = out
        self.total = 0
        self.cases = 0
        self.groups = {}
        self.group = "source_binding"
        self.stream = (out / "CHECKS120.jsonl").open("x", encoding="utf-8")

    def require(self, condition, label, **evidence):
        self.total += 1
        self.groups[self.group] = self.groups.get(self.group, 0) + 1
        if not condition:
            self.event("failed", label=label, evidence=evidence)
            raise ArithmeticError(label)

    def event(self, status, **evidence):
        self.stream.write(json.dumps(serial(dict(group=self.group, status=status,
                                                 **evidence)), sort_keys=True,
                                     allow_nan=False) + "\n")
        self.stream.flush()

    def case(self, label, **evidence):
        self.cases += 1
        self.event("case_passed", label=label, **evidence)

    def close(self):
        self.stream.flush()
        os.fsync(self.stream.fileno())
        self.stream.close()


def verify_frozen_source(revision, commit, checks):
    """Local read-only tree/blob checks; never trigger a promisor download."""
    checks.require(commit == FROZEN_COMMIT, "The exact requested F is required")
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1")

    def git(*args):
        return subprocess.run(["git", "-C", str(revision), *args], env=env,
                              check=True, capture_output=True).stdout

    repo = Path(git("rev-parse", "--show-toplevel").decode().strip()).resolve()
    resolved = git("rev-parse", commit + "^{commit}").decode().strip()
    checks.require(resolved == commit, "The commit resolves to F itself")
    prefix = revision.relative_to(repo).as_posix()
    tree_raw = git("ls-tree", "-r", "-z", commit, "--", prefix)
    tree = {}
    for entry in tree_raw.split(b"\0"):
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        mode, kind, identity = metadata.decode().split()
        tree[raw_path.decode()] = (mode, kind, identity)

    def bound(name, expected=None):
        relative = PurePosixPath(name)
        checks.require(not relative.is_absolute() and ".." not in relative.parts,
                       "A source path must remain within the revision", path=name)
        path = revision / relative
        checks.require(not path.is_symlink() and path.is_file(),
                       "A frozen input must be a regular file", path=name)
        path.resolve().relative_to(revision)
        raw = path.read_bytes()
        entry = tree.get(prefix + "/" + name)
        checks.require(entry is not None and entry[0] in ("100644", "100755")
                       and entry[1] == "blob", "Frozen regular blob is in F", path=name)
        actual_sha, actual_blob = sha256(raw), blob_sha(raw)
        checks.require(actual_blob == entry[2], "Local bytes match the F blob", path=name)
        if expected is not None:
            checks.require(actual_sha == expected, "Frozen SHA-256 matches", path=name)
        return dict(path=name, bytes=len(raw), sha256=actual_sha, git_blob=actual_blob)

    manifest_record = bound("SOURCE_FREEZE120.json")
    info = json.loads((revision / "SOURCE_FREEZE120.json").read_text())
    scientific = info["scientific_files"]
    checks.require(len(scientific) == FROZEN_COUNT,
                   "The scientific freeze has the declared 157 inputs",
                   actual=len(scientific))
    indexed = {item["path"]: item for item in info["files"]}
    checks.require(len(indexed) == len(info["files"]) and set(indexed) == set(scientific),
                   "The two source inventories agree without duplicate paths")
    required = {"PROTOCOL120.md", "INDEPENDENT_PROTOCOL120.md",
                "code120/improvement120.py", "frozen108/code/interval94.py",
                "provenance/frozen_mathematics120/policy_improvement_main.tex",
                "provenance/frozen_mathematics120/policy_improvement_proofs.tex"}
    checks.require(required <= set(scientific), "Required theory and arithmetic inputs are frozen")
    records = []
    for name, expected in sorted(scientific.items()):
        item = bound(name, expected)
        checks.require(item == indexed[name], "Source inventory size and identities agree", path=name)
        records.append(item)
    checks.case("all_frozen_inputs", count=len(records), source_commit=commit)
    return dict(source_commit=commit,
                source_tree=git("rev-parse", commit + "^{tree}").decode().strip(),
                source_manifest=manifest_record, scientific_inputs=records,
                git_no_lazy_fetch=True, verified_before_numerical_import=True)


# A minimal exact polynomial algebra, independent of production economic code.
# The four variables are y1, y2, normalized feasible action v, and innovation z.
class P:
    DIM = 4

    def __init__(self, terms=0):
        if isinstance(terms, P):
            self.t = dict(terms.t)
        elif isinstance(terms, dict):
            self.t = {tuple(k): Q(v) for k, v in terms.items() if v}
        else:
            self.t = {(0,) * self.DIM: Q(terms)} if terms else {}

    @classmethod
    def variable(cls, j):
        exponent = [0] * cls.DIM
        exponent[j] = 1
        return cls({tuple(exponent): 1})

    def __add__(self, other):
        answer = dict(self.t)
        for k, v in P(other).t.items():
            answer[k] = answer.get(k, Q(0)) + v
        return P(answer)

    __radd__ = __add__

    def __neg__(self):
        return P({k: -v for k, v in self.t.items()})

    def __sub__(self, other):
        return self + -P(other)

    def __rsub__(self, other):
        return P(other) + -self

    def __mul__(self, other):
        answer = {}
        for k, v in self.t.items():
            for j, w in P(other).t.items():
                exponent = tuple(a + b for a, b in zip(k, j))
                answer[exponent] = answer.get(exponent, Q(0)) + v * w
        return P(answer)

    __rmul__ = __mul__

    def __pow__(self, exponent):
        if not isinstance(exponent, int) or exponent < 0:
            raise ValueError("Only nonnegative integer polynomial powers")
        answer = P(1)
        for _ in range(exponent):
            answer *= self
        return answer

    def derivative(self, j):
        answer = {}
        for key, value in self.t.items():
            if key[j]:
                exponent = list(key)
                exponent[j] -= 1
                answer[tuple(exponent)] = value * key[j]
        return P(answer)

    def value(self, point):
        return sum((v * math.prod(Q(x) ** power for x, power in zip(point, k))
                    for k, v in self.t.items()), Q(0))

    def constant(self):
        if any(any(k) for k in self.t):
            raise ArithmeticError("Polynomial was not constant")
        return self.t.get((0,) * self.DIM, Q(0))


def affine_corner_range(poly, checks, label):
    # Multi-affinity, rather than a grid heuristic, makes these extrema global.
    checks.require(all(all(k <= 1 for k in powers) for powers in poly.t),
                   "Exact corner range requires a multi-affine polynomial", label_detail=label)
    values = [poly.value(point) for point in itertools.product((0, 1), repeat=P.DIM)]
    return min(values), max(values)


def psd2(matrix, checks, label):
    a, b = matrix[0]
    c, d = matrix[1]
    checks.require(b == c and a >= 0 and d >= 0 and a * d - b * c >= 0,
                   label, matrix=matrix)


def primitive_constants(checks, helpers):
    checks.group = "original_primitive_polynomial_constants"
    y1, y2, v, z = (P.variable(j) for j in range(4))
    capacity = Q(1, 8) + Q(1, 16) * (y1 + y2)
    m1 = Q(1, 16) + y1 * Q(1, 2) + y2 * Q(1, 8) + y1 * (1-y2) * Q(1, 16) + capacity*v*Q(1, 2)
    m2 = Q(1, 16) + y2 * Q(1, 2) + y1 * Q(1, 8) + y2 * (1-y1) * Q(1, 16) + capacity*v*Q(1, 4)
    k = 5 * (m1-m2)
    expected_k = Q(35, 16)*(y1-y2) + Q(5, 4)*capacity*v
    checks.require(not (k-expected_k).t, "Bilinear terms cancel exactly in k")

    def stage(x1, x2, active):
        return ((x1-Q(5, 8))**2 + (x2-Q(5, 8))**2
                + Q(1, 4)*(x1-x2)**2 + 2*active*(Q(1, 2)-x1-x2)**2)

    def terminal(x1, x2, active):
        return stage(x1, x2, active) + (x1-Q(5, 8))**2 + (x2-Q(5, 8))**2

    for active in (0, 1):
        expansion = terminal(m1+z, m2-z, active) - terminal(m1, m2, active)
        checks.require(not (expansion-k*z-5*z*z).t,
                       "Exact terminal shock polynomial identity", active_hinge=active)
        for name, poly, lower, upper in (
            ("S", stage(y1, y2, active), Q(2), Q(11)),
            ("g", terminal(y1, y2, active), Q(4), Q(13)),
        ):
            hessian = [[poly.derivative(i).derivative(j).constant() for j in (0, 1)] for i in (0, 1)]
            psd2([[hessian[i][j]-(lower if i == j else 0) for j in (0, 1)] for i in (0, 1)], checks, name+" lower Hessian")
            psd2([[(upper if i == j else 0)-hessian[i][j] for j in (0, 1)] for i in (0, 1)], checks, name+" upper Hessian")
            checks.case("constant_hessian", primitive=name, active_hinge=active,
                        matrix=hessian, lower=lower, upper=upper)

    derivatives = [[p.derivative(j) for j in (0, 1)] for p in (m1, m2)]
    for i, row in enumerate(derivatives):
        for j, derivative in enumerate(row):
            lo, hi = affine_corner_range(derivative, checks, "Dm entry")
            checks.require(lo >= 0, "Normalized transition Jacobian is nonnegative", row=i, column=j)
        _, hi = affine_corner_range(sum(row, P()), checks, "Dm row sum")
        checks.require(hi <= Q(3, 4), "Global Dm row bound", row=i, actual=hi)
    for j in (0, 1):
        _, hi = affine_corner_range(sum((row[j] for row in derivatives), P()), checks, "Dm column sum")
        checks.require(hi <= Q(47, 64), "Global Dm column bound", column=j, actual=hi)
    checks.require(Q(3, 4)*Q(47, 64) < Q(3, 4)**2, "Spectral norm squared bound")

    for j, p in enumerate((m1, m2)):
        hessian = [[p.derivative(i).derivative(k0).constant() for k0 in (0, 1)] for i in (0, 1)]
        checks.require(hessian == [[0, Q(-1, 16)], [Q(-1, 16), 0]],
                       "Exact transition Hessian", component=j)
        # z=(2w-1)R, so the following remains a multi-affine cube polynomial.
        successor = p + (1 if j == 0 else -1)*RADIUS*(2*z-1)
        lo, hi = affine_corner_range(successor, checks, "original invariant domain")
        checks.require(lo >= Q(1, 32) and hi <= Q(27, 32),
                       "Original transition invariant cube", component=j, lower=lo, upper=hi)

    gradient_g = 4*Q(5, 8) + Q(1, 2) + 4*Q(1, 2)
    checks.require(gradient_g == 5, "Coordinate terminal gradient envelope")
    transition_hessian_remainder = 2*gradient_g*Q(1, 16)
    chain_bound = 13*Q(3, 4)**2 + transition_hessian_remainder
    stage_bound = 11 + 5*2*Q(1, 16)**2
    grad_k_sq = 2*Q(35, 16)**2 + 2*Q(5, 64)**2
    checks.require(chain_bound == Q(127, 16), "Terminal chain upper curvature")
    checks.require(stage_bound == Q(1413, 128), "Normalized stage upper curvature")
    checks.require(grad_k_sq == Q(19625, 2048), "Risk-motion squared gradient bound")
    checks.require(Q(10, 16) < Q(4, 5)**2, "sqrt(10)/4 is less than 4/5")

    mu_state = 2-BETA*transition_hessian_remainder
    checks.require(mu_state == Q(181, 128) and 2*mu_state == MZ,
                   "Original state and innovation lower curvature")
    hprime_max = 2*Q(1, 4)+16*Q(1, 4)**3
    checks.require(hprime_max == Q(3, 4), "Capacity endpoint action derivative bound")
    # A direct normalized-action check of the inherited K=15 envelope.
    state_gradient = 4+hprime_max/Q(16)+BETA*5*Q(47, 64)
    checks.require(state_gradient < Q(15, 2), "State-coordinate gradient below 15/d",
                   actual=state_gradient)
    checks.require(2*state_gradient < 15, "Innovation Lipschitz envelope K=15")

    for alpha in (Q(1, 2), Q(3, 4)):
        t = 1-alpha
        independent_m = stage_bound+BETA*(chain_bound+grad_k_sq*alpha/(10*t))
        exact_helper = helpers["exact_modulus"](alpha)
        numeric = helpers["modulus"](float(alpha))
        lower, upper = Q(float(numeric.lo)), Q(float(numeric.hi))
        checks.require(exact_helper == independent_m, "Frozen modulus agrees with independent exact derivation", alpha=alpha)
        checks.require(lower <= independent_m <= upper,
                       "Frozen outward modulus encloses exact M", alpha=alpha)
        tail_curvature = MZ*(alpha/16)
        checks.require(Q(float(tail_curvature)) == tail_curvature,
                       "The passed original tail curvature is exactly dyadic", alpha=alpha)
        checks.case("original_moduli", alpha=alpha, M=independent_m,
                    outward_M=[lower, upper], K=15, m_z=MZ,
                    state_gradient_envelope=state_gradient,
                    tail_curvature=tail_curvature)


def integral(coefficients, left, right):
    return sum((Q(c)*(right**(j+1)-left**(j+1))/Q(j+1)
                for j, c in enumerate(coefficients)), Q(0))


def value(coefficients, x):
    return sum((Q(c)*x**j for j, c in enumerate(coefficients)), Q(0))


def information_constructions(checks):
    checks.group = "fixed_density_information_constructions"
    for nquery, radius, alpha, K in itertools.product(
        (0, 1, 8, 32), (Q(1, 32), Q(1)),
        (Q(0), Q(1, 2), Q(3, 4), Q(255, 256)), (Q(1), Q(15))
    ):
        t, B = 1-alpha, 2*radius*(1-alpha)
        q0, h = -radius+2*radius*alpha, B/(2*(nquery+1))
        for multiplier in (Q(0), Q(1, 4), Q(1), Q(2)):
            E = multiplier*K/(4*(nquery+1))
            lam = min(Q(1), 4*E*(nquery+1)/K)
            excess = [Q(0), lam*K*h/(2*B), -lam*K/(2*B)]
            one_integral = integral(excess, Q(0), h)
            checks.require(one_integral == lam*K*h**3/(12*B),
                           "Exact local quadratic chord integral")
            checks.require(value(excess, Q(0)) == value(excess, h) == 0,
                           "Chord perturbations agree at both endpoints")
            slope_radius = lam*K*h/(2*B)
            checks.require(slope_radius <= E, "Perturbation has the prescribed action modulus")
            checks.require((1-lam)*K/B >= 0, "Each selected-cell derivative is monotone")

            # A declared transcript occupancy checks the constructive witness.
            # The general adaptive argument is in the proof, not inferred from
            # these finitely many transcripts. One oracle query is one scalar.
            queries = [q0+(Q(j)+Q(1, 2))*h for j in range(nquery)]
            occupied = {j for j in range(2*(nquery+1))
                        if any(q0+j*h < p < q0+(j+1)*h for p in queries)}
            available = [j for j in range(2*(nquery+1)) if j not in occupied]
            checks.require(len(occupied) <= nquery and len(available) >= nquery+2,
                           "At least N+2 cells are unqueried in their interiors")
            selected = set(available[:nquery+1])
            previous_right = Q(0)
            for j in range(2*(nquery+1)):
                left, right = q0+j*h, q0+(j+1)*h
                dl, dr = K*(left-q0)/B, K*(right-q0)/B
                if j in selected:
                    dl, dr = dl+slope_radius, dr-slope_radius
                checks.require(0 <= previous_right <= dl <= dr <= K,
                               "Whole constructed continuation remains convex K-Lipschitz",
                               N=nquery, cell=j)
                previous_right = dr
            checks.require(not any(q0+j*h < p < q0+(j+1)*h
                                   for j in selected for p in queries),
                           "Every declared queried scalar value is preserved")
            contrast = (nquery+1)*one_integral/B
            claimed = min(K*radius*t/(48*(nquery+1)**2), E*radius*t/(12*(nquery+1)))
            checks.require(contrast == claimed, "Information interval-width constant is exact")
            checks.case("quadratic_chord_witness", N=nquery, R=radius,
                        alpha=alpha, K=K, E=E, mixing=lam,
                        selected_cells=len(selected), available_cells=len(available),
                        exact_contrast=contrast, claim="interval width, not absolute error")

    # The finite budget conversion is independent of any economic solver.
    for N in (32, 33, 34, 35, 63, 64, 127, 128, 1024):
        n = (N-8)//4
        checks.require(4*n+8 <= N and n >= Q(N, 8), "Exact paid point-budget conversion", N=N)


def tail_transfer_algebra(checks):
    checks.group = "constrained_tail_transfer_algebra"
    counts = {"lower_boundary": 0, "interior": 0, "upper_boundary": 0,
              "zero_displacement": 0, "exact_candidate_tail": 0}
    for alpha, curvature in itertools.product(
        (Q(1, 8), Q(1, 2), Q(3, 4), Q(255, 256)), (Q(1), MZ)
    ):
        t = 1-alpha
        L, B = 2*RADIUS*alpha, 2*RADIUS*t
        left, right = -RADIUS, RADIUS-L
        strong_h = curvature*L
        factor = alpha/(2*curvature*t)
        checks.require(L/(2*curvature*B) == factor,
                       "Tail-transfer coefficient after normalization")
        for ca, cb in itertools.product(tuple(j*RADIUS for j in (-3, -1, 0, 1, 3)), repeat=2):
            coeff_a = [curvature*ca*ca/2, -curvature*ca, curvature/2]
            coeff_b = [curvature*cb*cb/2, -curvature*cb, curvature/2]
            ua = min(right, max(left, ca-L/2))
            ub = min(right, max(left, cb-L/2))
            min_a = integral(coeff_a, ua, ua+L)
            min_b = integral(coeff_b, ub, ub+L)
            E = curvature*abs(ca-cb)
            region = "lower_boundary" if ub == left else ("upper_boundary" if ub == right else "interior")
            slope_at_min = strong_h*(ub+L/2-cb)
            checks.require((ub == left and slope_at_min >= 0) or
                           (ub == right and slope_at_min <= 0) or
                           (left < ub < right and slope_at_min == 0),
                           "Constrained tail first-order condition", region=region)
            cuts = sorted({left+(right-left)*r for r in (Q(0), Q(1, 4), Q(1, 2), Q(3, 4), Q(1))} | {ub})
            for u in cuts:
                Ha, Hb = integral(coeff_a, u, u+L), integral(coeff_b, u, u+L)
                ka, kb = (Ha-min_a)/B, (Hb-min_b)/B
                e = Hb-min_b
                checks.require(ka >= 0 and kb >= 0, "Exact original-density deficits are nonnegative")
                checks.require(strong_h*(u-ub)**2 <= 2*e,
                               "Distance-to-constrained-minimizer bound")
                expected_difference = curvature*L*(ca-cb)
                checks.require(abs(expected_difference) <= E*L, "Integrated difference derivative bound")
                C = E*E*factor
                # Equivalent rational comparison with the positive square root:
                # ka <= kb+C+2sqrt(kb*C). No floating sqrt is used.
                residual = ka-kb-C
                checks.require(residual <= 0 or residual*residual <= 4*kb*C,
                               "Full constrained tail-defect transfer", ka=ka, kb=kb, C=C)
                # Exact completion of the quadratic used in the proof.
                for distance in (Q(0), abs(u-ub), E*L/strong_h, 2*RADIUS):
                    lhs = -strong_h*distance*distance/2+E*L*distance
                    rhs = E*E*L*L/(2*strong_h)
                    checks.require(rhs-lhs == strong_h*(distance-E*L/strong_h)**2/2,
                                   "Tail-transfer quadratic completion")
                counts[region] += 1
                counts["zero_displacement"] += int(E == 0)
                counts["exact_candidate_tail"] += int(kb == 0)
                checks.case("tail_quadratic", alpha=alpha, m_z=curvature,
                            center_a=ca, center_b=cb, cut=u, candidate_region=region,
                            E=E, incumbent_defect=ka, candidate_defect=kb,
                            cross_term_squared=4*kb*C, transfer_residual=residual)
    checks.require(all(counts.values()), "All declared tail boundary and zero cases are exercised", counts=counts)
    checks.case("tail_case_coverage", **counts)


def load_isolated_helpers(revision, checks):
    """Called only after every frozen scientific input has passed its gate."""
    checks.group = "isolated_frozen_arithmetic_definitions"
    import numpy as np
    definitions = {}

    def isolate(path, names, namespace):
        raw = path.read_bytes()
        tree = ast.parse(raw, filename=str(path))
        nodes = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))
                 and node.name in names]
        checks.require({node.name for node in nodes} == set(names) and len(nodes) == len(names),
                       "Exactly the requested frozen definitions are selected", path=str(path))
        checks.require(all(not getattr(node, "decorator_list", ()) for node in nodes),
                       "No unreviewed decorator executes during isolation")
        code = compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), str(path), "exec")
        exec(code, namespace)
        definitions.setdefault(path.relative_to(revision).as_posix(), []).append(dict(
            sha256=sha256(raw), definitions=sorted(names),
            isolated_ast_sha256=sha256(ast.dump(ast.Module(body=nodes, type_ignores=[]),
                                                include_attributes=False).encode())))

    interval = {"np": np}
    isolate(revision / "frozen108/code/interval94.py", ("down", "up", "I", "as_i"), interval)
    calls = {}

    def count(name, amount):
        checks.require(name == "r120_tail_transfer_integer_sqrt_calls",
                       "The isolated helper makes only its declared arithmetic counter call", name=name)
        calls[name] = calls.get(name, 0)+int(amount)

    namespace = {"np": np, "math": math, "Fraction": Q, "I": interval["I"],
                 "up": interval["up"], "econ": SimpleNamespace(count=count)}
    isolate(revision / "code120/improvement120.py", ("modulus", "rational_sqrt_upper"), namespace)
    exact = {"I": Q}
    isolate(revision / "code120/improvement120.py", ("modulus",), exact)
    checks.case("isolated_definitions_loaded", definitions=definitions,
                numpy_version=np.__version__, economic_modules_imported=False)
    return dict(np=np, I=interval["I"], up=interval["up"],
                modulus=namespace["modulus"], sqrt=namespace["rational_sqrt_upper"],
                exact_modulus=exact["modulus"], counter=calls, definitions=definitions,
                numpy_version=np.__version__)


def independent_dyadic_root_ceiling(rational):
    """Different integer algorithm: bisection, with no call to isqrt/sqrt."""
    p, q = rational.numerator << 80, rational.denominator
    lo, hi = 0, 1 << ((p.bit_length()+1)//2)
    while lo < hi:
        mid = (lo+hi)//2
        if mid*mid*q >= p:
            hi = mid
        else:
            lo = mid+1
    return lo, Q(lo, 2**40)


def upward_float(rational):
    result = float(rational)
    if Q(result) < rational:
        result = math.nextafter(result, math.inf)
    return result


def rounding_edges(checks, helpers):
    checks.group = "frozen_square_root_rational_edges"
    np, sqrt = helpers["np"], helpers["sqrt"]
    cases = [("zero", 0.0), ("negative_zero", -0.0),
             ("least_subnormal", float.fromhex("0x0.0000000000001p-1022")),
             ("largest_subnormal", float.fromhex("0x0.fffffffffffffp-1022")),
             ("least_normal", float.fromhex("0x1p-1022")),
             ("largest_finite", float.fromhex("0x1.fffffffffffffp+1023"))]
    for exponent in (-80, -40, -2, 0, 2, 26, 80, 200, 1000):
        x = float.fromhex("0x1p" + str(exponent))
        cases.extend([(f"power_{exponent}_below", math.nextafter(x, 0.0)),
                      (f"power_{exponent}_exact", x),
                      (f"power_{exponent}_above", math.nextafter(x, math.inf))])
    rational_cases = [Q(1, 3), Q(7, 10), Q(1, 2**80+1), Q(1, 2**1100),
                      Q((2**52+1)**2, 2**104)]
    for j, exact in enumerate(rational_cases):
        x = upward_float(exact)
        checks.require(math.isfinite(x) and Q(x) >= exact,
                       "A nonbinary rational is converted to a valid binary upper input", rational=exact)
        cases.append((f"rational_upper_{j}", x))

    values = np.asarray([x for _, x in cases], dtype=np.float64).reshape(2, -1)
    output = sqrt(values)
    checks.require(output.shape == values.shape, "Frozen sqrt preserves non-scalar input shape")
    directed_count, exact_square_count = 0, 0
    for (label, x), numeric in zip(cases, output.reshape(-1)):
        exact_input, exact_output = Q(x), Q(float(numeric))
        integer, bound = independent_dyadic_root_ceiling(exact_input)
        checks.require(bound*bound >= exact_input and
                       (integer == 0 or Q(integer-1, 2**40)**2 < exact_input),
                       "Independent dyadic upper root is the least feasible grid point", label_detail=label)
        checks.require(exact_output >= bound and exact_output*exact_output >= exact_input,
                       "Frozen output encloses both rational grid and true root", label_detail=label)
        checks.require(exact_output == 0 or Q(math.nextafter(float(numeric), -math.inf)) < bound,
                       "Frozen binary64 result is the least float above its dyadic bound", label_detail=label)
        directed = Q(float(bound)) < bound
        directed_count += int(directed)
        exact_square_count += int(bound*bound == exact_input)
        checks.case("sqrt_edge", label_detail=label, input_hex=x.hex(),
                    exact_input=exact_input, grid_integer=integer, grid_bound=bound,
                    output_hex=float(numeric).hex(), exact_output=exact_output,
                    directed_conversion_required=directed)
    checks.require(directed_count > 0 and exact_square_count > 0,
                   "Directed-rounding and exact-square equality branches both occur",
                   directed=directed_count, exact_squares=exact_square_count)
    scalar = sqrt(np.asarray(1.0))
    checks.require(scalar.shape == () and float(scalar) == 1.0, "Scalar exact-square edge")
    empty = sqrt(np.asarray([], dtype=float))
    checks.require(empty.size == 0, "Empty arithmetic input is harmless")
    for label, invalid in (("negative", -1.0), ("negative_subnormal", -float.fromhex("0x0.0000000000001p-1022")),
                           ("nan", math.nan), ("positive_infinity", math.inf), ("negative_infinity", -math.inf)):
        try:
            sqrt(np.asarray([0.0, invalid]))
        except ValueError:
            checks.case("invalid_sqrt_input_rejected", label_detail=label)
        else:
            raise ArithmeticError("Frozen sqrt accepted invalid input: " + label)

    # Compose the same interval expression used in _tail_density, without
    # locating a tail, evaluating a continuation, or importing that module.
    I = helpers["I"]
    for alpha, E, kappa in itertools.product((Q(1, 2), Q(3, 4)),
                                            (Q(0), Q(1, 1024), Q(1, 16), Q(1)),
                                            (Q(0), Q(1, 2**40), Q(1, 16))):
        factor = alpha/(2*MZ*(1-alpha))
        computed_factor = (I(float(alpha))/(I(float(2*MZ))*(1-I(float(alpha))))).hi
        checks.require(Q(float(computed_factor)) >= factor, "Outward transfer-factor premise")
        computed = (I(sqrt(float(kappa)))+I(float(E))*I(sqrt(computed_factor))).square().hi
        upper = Q(float(computed))
        cross_square = kappa*E*E*factor
        residual = upper-kappa-E*E*factor
        checks.require(residual >= 0 and residual*residual >= 4*cross_square,
                       "Composed production transfer arithmetic is outward", alpha=alpha, E=E, kappa=kappa)
        checks.case("outward_transfer_composition", alpha=alpha, E=E, kappa=kappa,
                    exact_factor=factor, factor_upper=Q(float(computed_factor)),
                    resulting_upper=upper)


def remaining_exact_edges(checks):
    checks.group = "fixed_work_and_population_constants"
    for n0, J, c, c0 in itertools.product((1, 2), (0, 1, 6), (Q(0), Q(1), Q(3, 2)), (Q(0), Q(5))):
        nJ = n0*2**J
        total = sum((c*n0*2**j+c0 for j in range(J+1)), Q(0))
        exact_bound = c*(2*nJ-n0)+c0*(J+1)
        checks.require(total == exact_bound and exact_bound <= 2*c*nJ+c0*(J+1),
                       "Non-strict doubled-work bound includes c=0 and J=0")
    x = Q(1089, 128)
    checks.require(2*64*Q(33, 128)**2 == x, "Exact frozen Hoeffding exponent")
    taylor = sum((x**j/Q(math.factorial(j)) for j in range(21)), Q(0))
    checks.require(taylor > 3840, "Exact exponential lower Taylor bound")
    checks.require(Q(192, 7680)+Q(48, 1920) == Q(1, 20),
                   "Declared event and mean family error budgets sum to 5 percent")
    checks.require(BETA*Q(1, 2**20) == Q(15, 2**24), "Original future comparison allowance")
    checks.case("fixed_constants", hoeffding_exponent=x,
                exp_lower_taylor=taylor, gain_ceiling=Q(1, 256),
                future_contrast_radius=Q(15, 2**24))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--revision", type=Path, default=REVISION)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    revision, out = args.revision.resolve(), args.out.resolve()
    # Fail closed on an existing output path. No earlier failure is overwritten.
    out.mkdir(parents=True, exist_ok=False)
    script_raw = Path(__file__).read_bytes()
    started = time.time()
    start = dict(status="started", started_unix=started,
                 argv=sys.argv, python=sys.version, pid=os.getpid(),
                 source_commit=args.source_commit, revision=str(revision),
                 diagnostic_source_sha256=sha256(script_raw), scope=SCOPE)
    write_json(out / "START120.json", start)
    checks = Checks(out)
    helpers, binding, failure = None, None, None
    numerical_definition_loading_attempted = False
    try:
        binding = verify_frozen_source(revision, args.source_commit, checks)
        write_json(out / "SOURCE_BINDING120.json", binding)
        numerical_definition_loading_attempted = True
        helpers = load_isolated_helpers(revision, checks)
        primitive_constants(checks, helpers)
        information_constructions(checks)
        tail_transfer_algebra(checks)
        rounding_edges(checks, helpers)
        remaining_exact_edges(checks)
        checks.require(not ({"investment94", "kernel108", "campaign108", "improvement120",
                             "campaign120", "independent120"} & set(sys.modules)),
                       "No economic solver or campaign module was imported")
    except BaseException as exc:
        failure = dict(type=type(exc).__name__, message=str(exc),
                       traceback=traceback.format_exc(), group=checks.group)
        write_json(out / "FAILURE120.json", failure)
    finally:
        checks.close()
    ended = time.time()
    outputs = []
    for path in sorted(out.iterdir()):
        if path.is_file():
            raw = path.read_bytes()
            outputs.append(dict(path=path.name, bytes=len(raw), sha256=sha256(raw)))
    summary = dict(status="passed" if failure is None else "failed", scope=SCOPE,
                   source_commit=args.source_commit,
                   diagnostic_source_sha256=sha256(script_raw),
                   started_unix=started, ended_unix=ended, elapsed_seconds=ended-started,
                   checks=checks.total, completed_cases=checks.cases, groups=checks.groups,
                   numerical_definition_loading_attempted=numerical_definition_loading_attempted,
                   frozen_source_binding_passed=binding is not None,
                   isolated_arithmetic_counters=helpers["counter"] if helpers else {},
                   numpy_version=helpers["numpy_version"] if helpers else None,
                   outputs=outputs, failure=failure)
    write_json(out / "SUMMARY120.json", summary)
    print(json.dumps(dict(status=summary["status"], checks=checks.total,
                          completed_cases=checks.cases, output=str(out)), sort_keys=True))
    return 0 if failure is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
