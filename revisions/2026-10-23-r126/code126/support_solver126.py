"""Finite-budget complete-support Bellman certificates with exact authority.

SciPy/HiGHS proposes LP primal points and multipliers.  Every accepted bound is
recomputed over the ORIGINAL rational convex constraints and finite variable
box.  Solver status, numerical feasibility and a numerical objective never
constitute certificate authority.  This module makes no economic queries.
"""
from __future__ import annotations

from fractions import Fraction as F
import math
import time
import traceback

POINT_SCALE = 2**36
DUAL_SCALE = 2**36
MAX_SOLVES = 8
MAX_NEW_CUTS = 32


def rational(x):
    return x if isinstance(x, F) else F(x)


def canonical_case(raw):
    case = {k: rational(raw[k]) for k in
            ("A", "incumbent", "mu", "L", "delta", "tau", "omega", "old_optimum_lower")}
    case["gradient_cap"] = rational(raw.get("gradient_cap", 7))
    case["payloads"] = [{k: rational(p[k]) for k in
                         ("a", "W", "U", "p_lower", "p_upper", "g_lower", "g_upper")}
                        for p in raw["payloads"]]
    if not case["payloads"]:
        raise ValueError("A nonempty original support pool is required")
    if not 0 < case["mu"] <= case["L"] or case["A"] <= 0 or case["gradient_cap"] < 0:
        raise ValueError("Invalid original geometry")
    for p in case["payloads"]:
        if not (0 <= p["a"] <= case["A"] and p["W"] <= p["U"]
                and p["p_lower"] <= p["p_upper"] and p["g_lower"] <= p["g_upper"]):
            raise ValueError("Malformed original support pool")
    return case


def make_problem(raw, origin, target):
    case = canonical_case(raw)
    origin, target = rational(origin), rational(target)
    A, mu, L, M = (case[k] for k in ("A", "mu", "L", "gradient_cap"))
    if not 0 <= origin <= A or not 0 <= target <= A:
        raise ValueError("Contrast actions must be feasible")
    ps = case["payloads"]
    xs = sorted({F(0), A, origin, target} | {p["a"] for p in ps})
    n, m = len(xs), len(ps)
    lo, hi = [], []
    for x in xs:
        lo.append(max(p["W"] - M * abs(x-p["a"]) for p in ps) - mu*x*x/2)
        hi.append(min(p["U"] + M * abs(x-p["a"]) for p in ps) - mu*x*x/2)
    for x in xs:
        gl = max([-M] + [p["g_lower"] + (mu if x >= p["a"] else L)*(x-p["a"]) for p in ps])
        gu = min([M] + [p["g_upper"] + (L if x >= p["a"] else mu)*(x-p["a"]) for p in ps])
        lo.append(gl-mu*x)
        hi.append(gu-mu*x)
    lo += [p["p_lower"] for p in ps]
    hi += [p["p_upper"] for p in ps]
    if any(a > b for a, b in zip(lo, hi)):
        raise ValueError("Inconsistent original information: empty finite box")
    linear = [F(0)]*(2*n+m)
    linear[xs.index(origin)] += 1
    linear[xs.index(target)] -= 1
    constant = mu*(origin*origin-target*target)/2
    constraints = []
    for i in range(n-1):
        constraints += [["s_lower", i], ["s_upper", i]]
        constraints += ([["area_lower", i], ["area_upper", i]] if L > mu else
                        [["affine_area_pos", i], ["affine_area_neg", i]])
    constraints += [["support", i, j] for i in range(n) for j in range(m)]
    return dict(schema=1, case=case, origin=origin, target=target, nodes=xs,
                box_lower=lo, box_upper=hi, objective_linear=linear,
                objective_constant=constant, constraints=constraints)


def constraint(problem, descriptor, z):
    """Return exact c(z), sparse subgradient for the convex constraint c<=0."""
    xs, case = problem["nodes"], problem["case"]
    n = len(xs)
    mu, K, A = case["mu"], case["L"]-case["mu"], case["A"]
    kind, i = descriptor[:2]
    if kind == "support":
        j = descriptor[2]
        p = case["payloads"][j]
        v = z[2*n+j]-mu*p["a"]-z[n+i]
        t = max(-xs[i], min(A-xs[i], v/K)) if K else (A-xs[i] if v >= 0 else -xs[i])
        phi = v*t-K*t*t/2
        ell = p["W"]+z[2*n+j]*(xs[i]-p["a"])+mu*p["a"]*p["a"]/2-mu*p["a"]*xs[i]
        return ell+phi-z[i], {i: F(-1), n+i: -t, 2*n+j: xs[i]-p["a"]+t}
    d = xs[i+1]-xs[i]
    s = z[n+i+1]-z[n+i]
    w = z[i+1]-z[i]-z[n+i]*d
    if kind == "s_lower":
        return -s, {n+i: F(1), n+i+1: F(-1)}
    if kind == "s_upper":
        return s-K*d, {n+i: F(-1), n+i+1: F(1)}
    if kind == "area_lower":
        return s*s-2*K*w, {i: 2*K, i+1: -2*K, n+i: -2*s+2*K*d, n+i+1: 2*s}
    if kind == "area_upper":
        return s*s-2*K*(s*d-w), {i: -2*K, i+1: 2*K, n+i: -2*s, n+i+1: 2*s-2*K*d}
    if kind == "affine_area_pos":
        return w, {i: F(-1), i+1: F(1), n+i: -d}
    if kind == "affine_area_neg":
        return -w, {i: F(1), i+1: F(-1), n+i: d}
    raise ValueError("Unknown convex constraint")


def tangent(problem, ci, point):
    value, gradient = constraint(problem, problem["constraints"][ci], point)
    rhs = sum((v*point[k] for k, v in gradient.items()), F(0))-value
    return gradient, rhs


def exact_dual_bound(problem, cuts, multipliers):
    if len(cuts) != len(multipliers) or any(v < 0 for v in multipliers):
        raise ValueError("Invalid dual dimensions or sign")
    residual = list(problem["objective_linear"])
    intercept = problem["objective_constant"]
    for (row, rhs), weight in zip(cuts, multipliers):
        if not weight:
            continue
        intercept -= weight*rhs
        for k, value in row.items():
            residual[k] += weight*value
    correction = sum((min(v*a, v*b) for v, a, b in
                      zip(residual, problem["box_lower"], problem["box_upper"])), F(0))
    return intercept+correction


def dyadic(x, scale):
    if not math.isfinite(float(x)):
        raise ValueError("Nonfinite LP proposal")
    return F(round(float(x)*scale), scale)


def solve_contrast(case, origin, target, cheap_upper, max_solves=MAX_SOLVES):
    """Upper q(target)-q(origin), intersected with a separately valid cheap bound.

    Every LP call and discarded proposal is retained.  The bound also applies
    after an LP failure; finite budgets do not imply full-program optimality.
    """
    import numpy as np
    from scipy.optimize import linprog

    started = time.perf_counter()
    problem = make_problem(case, origin, target)
    lo, hi = problem["box_lower"], problem["box_upper"]
    cheap_upper = rational(cheap_upper)
    if origin == target:
        return dict(schema=1, problem=problem, points=[], cuts=[], dual_weights=[],
                    dual_lower=F(0), certified_upper=F(0), cheap_upper=F(0),
                    history=[], failure=None, seconds=time.perf_counter()-started,
                    economic_queries=0, lp_calls=0, exact_replay_required=True)
    points = [tuple((a+b)/2 for a, b in zip(lo, hi))]
    descriptors = [(0, i) for i in range(len(problem["constraints"]))]
    cuts = [tangent(problem, i, points[0]) for i in range(len(problem["constraints"]))]
    best = exact_dual_bound(problem, [], [])
    best_weights = []
    history, failure = [], None
    lp_calls = 0
    for iteration in range(max_solves):
        phase = time.perf_counter()
        try:
            count = len(lo)
            matrix, rhs, scales = [], [], []
            for row, b in cuts:
                scale = max([F(1, 2**20), abs(b)] + [abs(v) for v in row.values()])
                matrix.append([float(row.get(k, F(0))/scale) for k in range(count)])
                rhs.append(float(b/scale))
                scales.append(scale)
            lp_calls += 1
            result = linprog(np.array([float(v) for v in problem["objective_linear"]]),
                             A_ub=np.asarray(matrix), b_ub=np.asarray(rhs),
                             bounds=[(float(a), float(b)) for a, b in zip(lo, hi)],
                             method="highs-ds", options={"dual_feasibility_tolerance": 1e-9,
                                                        "primal_feasibility_tolerance": 1e-9,
                                                        "maxiter": 2000})
            row = dict(iteration=iteration, constraints=len(cuts), status=int(result.status),
                       message=str(result.message), iterations=int(getattr(result, "nit", 0)),
                       seconds=time.perf_counter()-phase)
            history.append(row)
            if not result.success:
                row["certificate_accepted"] = False
                break
            weights = [max(F(0), dyadic(-v, DUAL_SCALE))/scale
                       for v, scale in zip(result.ineqlin.marginals, scales)]
            bound = exact_dual_bound(problem, cuts, weights)
            row.update(rational_lower=bound, numerical_lp_objective=float(result.fun)+float(problem["objective_constant"]),
                       certificate_accepted=True, nonzero_weights=sum(bool(w) for w in weights))
            if bound > best:
                best, best_weights = bound, list(weights)
            point = tuple(max(a, min(b, dyadic(v, POINT_SCALE))) for v, a, b in zip(result.x, lo, hi))
            values = [(constraint(problem, descriptor, point)[0], ci)
                      for ci, descriptor in enumerate(problem["constraints"])]
            violated = sorted([(v, ci) for v, ci in values if v > 0], reverse=True)
            row.update(maximum_exact_violation=max([F(0)]+[v for v, _ in values]),
                       violation_count=len(violated))
            row["seconds_with_exact_replay"] = time.perf_counter()-phase
            if not violated or iteration+1 == max_solves:
                break
            pi = len(points)
            points.append(point)
            for value, ci in violated[:MAX_NEW_CUTS]:
                descriptors.append((pi, ci))
                cuts.append(tangent(problem, ci, point))
        except BaseException as exc:
            failure = dict(exception_type=type(exc).__name__, message=str(exc),
                           traceback=traceback.format_exc(), iteration=iteration,
                           seconds=time.perf_counter()-phase)
            break
    sparse_weights = [[i, w] for i, w in enumerate(best_weights) if w]
    final_upper = min(cheap_upper, -best)
    return dict(schema=1, problem=problem, points=points, cuts=descriptors,
                dual_weights=sparse_weights, dual_lower=best,
                certified_upper=final_upper, cheap_upper=cheap_upper,
                history=history, failure=failure, seconds=time.perf_counter()-started,
                economic_queries=0, lp_calls=lp_calls, exact_replay_required=True,
                numerical_optimality_claim=False, source_information="same complete paid support pool")


def continuous_regret_envelope(nodes, upper_contrasts, L):
    """Exact smoothness interpolation bound for q(a)-min q on the whole domain."""
    xs = list(map(rational, nodes))
    us = list(map(rational, upper_contrasts))
    L = rational(L)
    if len(xs) < 2 or len(xs) != len(us) or L <= 0:
        raise ValueError("Invalid action regret grid")
    bounds = list(us)
    cells = []
    for i in range(len(xs)-1):
        d = xs[i+1]-xs[i]
        if d <= 0:
            raise ValueError("Strictly increasing action grid required")
        t = max(F(0), min(F(1), F(1, 2)+(us[i+1]-us[i])/(L*d*d)))
        bound = (1-t)*us[i]+t*us[i+1]+L*d*d*t*(1-t)/2
        cells.append(dict(left=xs[i], right=xs[i+1], maximizing_fraction=t, bound=bound))
        bounds.append(bound)
    return max(F(0), max(bounds)), cells
