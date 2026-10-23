"""Independent standard-library authority for finite NBO support certificates.

This module imports no solver, fitting, floating-point linear algebra, or
original-economy evaluator. It rebuilds the finite problem, each rational
tangent and the box-corrected dual bound from the serialized original payload.
The economic soundness of that source-bound payload is a separate obligation.
All cheap comparison bounds are independently derived from the same payload.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path

Q = Fraction


def frac(value):
    if isinstance(value, bool):
        raise ValueError("Booleans are not rational observations")
    return value if isinstance(value, Q) else Q(value)


def encode(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    return value


def require(condition, message):
    if not condition:
        raise ValueError(message)


def recover_geometry(raw, origin, target):
    """Reconstruct every program bound; serialized narrower boxes are refused."""
    fields = ("A", "incumbent", "mu", "L", "delta", "tau", "omega", "old_optimum_lower")
    case = {key: frac(raw[key]) for key in fields}
    case["gradient_cap"] = frac(raw.get("gradient_cap", 7))
    pf = ("a", "W", "U", "p_lower", "p_upper", "g_lower", "g_upper")
    case["payloads"] = [{key: frac(p[key]) for key in pf} for p in raw["payloads"]]
    A, mu, L, M = [case[k] for k in ("A", "mu", "L", "gradient_cap")]
    a, b = frac(origin), frac(target)
    require(A > 0 and 0 < mu <= L and M >= 0, "Invalid original geometry")
    require(0 <= a <= A and 0 <= b <= A and 0 <= case["incumbent"] <= A,
            "An original action is infeasible")
    require(min(case["delta"], case["tau"], case["omega"]) >= 0,
            "Negative policy error or tolerance")
    payloads = case["payloads"]
    require(bool(payloads), "The original support pool is empty")
    for p in payloads:
        require(0 <= p["a"] <= A and p["W"] <= p["U"] and
                p["p_lower"] <= p["p_upper"] and p["g_lower"] <= p["g_upper"],
                "Malformed original support")
    nodes = sorted({Q(0), A, a, b, *(p["a"] for p in payloads)})
    n = len(nodes)
    low_f, high_f, low_g, high_g = [], [], [], []
    for x in nodes:
        translated_lows, translated_highs = [], []
        slope_lows, slope_highs = [-M], [M]
        for p in payloads:
            distance = x - p["a"]
            translated_lows.append(p["W"] - M * abs(distance))
            translated_highs.append(p["U"] + M * abs(distance))
            lower_curvature, upper_curvature = ((mu, L) if distance >= 0 else (L, mu))
            slope_lows.append(p["g_lower"] + lower_curvature * distance)
            slope_highs.append(p["g_upper"] + upper_curvature * distance)
        low_f.append(max(translated_lows) - mu*x*x/2)
        high_f.append(min(translated_highs) - mu*x*x/2)
        low_g.append(max(slope_lows) - mu*x)
        high_g.append(min(slope_highs) - mu*x)
    lower = low_f + low_g + [p["p_lower"] for p in payloads]
    upper = high_f + high_g + [p["p_upper"] for p in payloads]
    require(all(l <= u for l, u in zip(lower, upper)), "Empty reconstructed box")
    linear = [Q(0) for _ in lower]
    linear[nodes.index(a)] = Q(1)
    linear[nodes.index(b)] -= 1
    if a == b:
        linear[nodes.index(a)] = Q(0)
    descriptors = []
    for i in range(n - 1):
        descriptors.extend([["s_lower", i], ["s_upper", i]])
        if L == mu:
            descriptors.extend([["affine_area_pos", i], ["affine_area_neg", i]])
        else:
            descriptors.extend([["area_lower", i], ["area_upper", i]])
    descriptors.extend(["support", i, j] for i in range(n) for j in range(len(payloads)))
    return {"schema": 1, "case": case, "origin": a, "target": b, "nodes": nodes,
            "box_lower": lower, "box_upper": upper, "objective_linear": linear,
            "objective_constant": mu*(a*a-b*b)/2, "constraints": descriptors}


def conjugate(value, left, right, K):
    """A direct maximization of a scalar concave quadratic on a closed interval."""
    require(left <= 0 <= right and K >= 0, "Invalid bounded conjugate domain")
    candidates = [left, right]
    if K and left <= value/K <= right:
        candidates.append(value/K)
    # At K=0 and value=0, use the right endpoint, as specified by the format.
    point = max(candidates, key=lambda t: (value*t-K*t*t/2, t))
    return value*point-K*point*point/2, point


def evaluate_constraint(problem, descriptor, point):
    """Independent dense derivative from differential identities, not solver rows."""
    xs, case = problem["nodes"], problem["case"]
    n = len(xs)
    z = list(map(frac, point))
    require(len(z) == len(problem["box_lower"]), "Invalid cut-point dimension")
    mu, A, K = case["mu"], case["A"], case["L"]-case["mu"]
    row = [Q(0)]*len(z)
    kind, i = descriptor[:2]
    if kind == "support":
        j = descriptor[2]
        record = case["payloads"][j]
        pindex = 2*n+j
        p = z[pindex]
        v = p-mu*record["a"]-z[n+i]
        phi, maximizing_t = conjugate(v, -xs[i], A-xs[i], K)
        affine = record["W"] + p*(xs[i]-record["a"]) + mu*record["a"]**2/2-mu*record["a"]*xs[i]
        row[i], row[n+i], row[pindex] = -Q(1), -maximizing_t, xs[i]-record["a"]+maximizing_t
        return affine+phi-z[i], row
    d = xs[i+1]-xs[i]
    s = z[n+i+1]-z[n+i]
    w = z[i+1]-z[i]-z[n+i]*d
    ds, dw = [Q(0)]*len(z), [Q(0)]*len(z)
    ds[n+i], ds[n+i+1] = -Q(1), Q(1)
    dw[i], dw[i+1], dw[n+i] = -Q(1), Q(1), -d
    if kind == "s_lower":
        return -s, [-x for x in ds]
    if kind == "s_upper":
        return s-K*d, ds
    if kind == "area_lower":
        return s*s-2*K*w, [2*s*dx-2*K*dy for dx, dy in zip(ds, dw)]
    if kind == "area_upper":
        return s*s-2*K*s*d+2*K*w, [(2*s-2*K*d)*dx+2*K*dy for dx, dy in zip(ds, dw)]
    if kind == "affine_area_pos":
        return w, dw
    if kind == "affine_area_neg":
        return -w, [-x for x in dw]
    raise ValueError("Unknown original convex constraint")


def derivative_integral(case, left, right, upper):
    """Integrate the envelope using at most two distinct slopes per anchor cell.

    Grouping equal-curvature lines avoids the inherited all-pairs crossing
    partition and provides a separate implementation of the same bound.
    Each active two-slope segment is then clipped by the independently
    proved original-gradient cap. Thus the baseline uses every available
    cheap derivative restriction, including the third (constant) slope.
    """
    left, right = frac(left), frac(right)
    require(0 <= left <= right <= case["A"], "Derivative integral outside domain")
    knots = sorted({left, right, *(p["a"] for p in case["payloads"] if left < p["a"] < right)})
    total = Q(0)
    for l, r in zip(knots, knots[1:]):
        mid = (l+r)/2
        intercepts = {}
        for p in case["payloads"]:
            if upper:
                slope = case["L"] if mid >= p["a"] else case["mu"]
                constant = p["g_upper"]-slope*p["a"]
            else:
                slope = case["mu"] if mid >= p["a"] else case["L"]
                constant = p["g_lower"]-slope*p["a"]
            if slope not in intercepts:
                intercepts[slope] = constant
            elif upper:
                intercepts[slope] = min(intercepts[slope], constant)
            else:
                intercepts[slope] = max(intercepts[slope], constant)
        lines = list(intercepts.items())
        require(1 <= len(lines) <= 2, "Unexpected derivative-cone slopes")
        local = [l, r]
        if len(lines) == 2:
            (v, b), (w, c) = lines
            cross = (c-b)/(v-w)
            if l < cross < r:
                local.insert(1, cross)
        for u, v in zip(local, local[1:]):
            test = (u+v)/2
            line = (min if upper else max)(lines, key=lambda pair: pair[0]*test+pair[1])
            cap = frac(case.get("gradient_cap", 7))*(1 if upper else -1)
            clipped_knots = [u, v]
            crossing = (cap-line[1])/line[0]
            if u < crossing < v:
                clipped_knots.insert(1, crossing)
            for start, end in zip(clipped_knots, clipped_knots[1:]):
                mid_value = line[0]*(start+end)/2+line[1]
                active_cap = mid_value >= cap if upper else mid_value <= cap
                if active_cap:
                    total += cap*(end-start)
                else:
                    total += line[0]*(end*end-start*start)/2+line[1]*(end-start)
    return total


def contrast(case, origin, target):
    a, b = frac(origin), frac(target)
    if a <= b:
        return derivative_integral(case, a, b, False), derivative_integral(case, a, b, True)
    return -derivative_integral(case, b, a, True), -derivative_integral(case, b, a, False)


def absolute_bounds(case, action):
    a = frac(action)
    lower_candidates, upper_candidates = [frac(case["old_optimum_lower"])], []
    for p in case["payloads"]:
        lo, hi = contrast(case, p["a"], a)
        displacement = a-p["a"]
        lower_candidates.extend([p["W"]+lo,
            p["W"]+min(p["p_lower"]*displacement, p["p_upper"]*displacement)+case["mu"]*displacement**2/2])
        upper_candidates.append(p["U"]+hi)
    lower, upper = max(lower_candidates), min(upper_candidates)
    require(lower <= upper, "Inconsistent absolute original-value enclosure")
    return lower, upper


def cheap_bound(case, origin, target):
    if frac(origin) == frac(target):
        return Q(0)
    _, pair = contrast(case, origin, target)
    lower_origin, _ = absolute_bounds(case, origin)
    _, upper_target = absolute_bounds(case, target)
    return min(pair, upper_target-lower_origin)


def verify_certificate(record):
    require(record.get("schema") == 1, "Unknown certificate format")
    given = record["problem"]
    original = recover_geometry(given["case"], given["origin"], given["target"])
    for key in ("nodes", "box_lower", "box_upper", "objective_linear"):
        require(list(map(frac, given[key])) == original[key], "Unlicensed serialized "+key)
    require(frac(given["objective_constant"]) == original["objective_constant"], "Wrong original objective constant")
    require(given["constraints"] == original["constraints"], "Incomplete or reordered constraint identity")
    require(given.get("schema") == 1, "Unknown finite-problem format")
    points = [list(map(frac, v)) for v in record["points"]]
    require(all(len(v) == len(original["box_lower"]) for v in points), "Wrong rational point dimension")
    cuts = record["cuts"]
    reconstructed = []
    for identifiers in cuts:
        require(isinstance(identifiers, (list, tuple)) and len(identifiers) == 2, "Malformed cut identity")
        pi, ci = identifiers
        require(type(pi) is int and type(ci) is int and 0 <= pi < len(points) and 0 <= ci < len(original["constraints"]), "Cut identifier outside the declared record")
        value, slope = evaluate_constraint(original, original["constraints"][ci], points[pi])
        intercept = value-sum((g*x for g, x in zip(slope, points[pi])), Q(0))
        reconstructed.append((intercept, slope))
    residual = list(original["objective_linear"])
    constant = original["objective_constant"]
    used = set()
    for wi, weight in record["dual_weights"]:
        require(type(wi) is int and 0 <= wi < len(cuts) and wi not in used, "Invalid or duplicated dual index")
        used.add(wi)
        y = frac(weight)
        require(y >= 0, "Negative dual weight")
        offset, row = reconstructed[wi]
        constant += y*offset
        residual = [r+y*g for r, g in zip(residual, row)]
    bound = constant+sum((min(r*l, r*u) for r, l, u in zip(residual, original["box_lower"], original["box_upper"])), Q(0))
    require(bound == frac(record["dual_lower"]), "Incorrect rational dual lower bound")
    cheap = cheap_bound(original["case"], original["origin"], original["target"])
    require(cheap == frac(record["cheap_upper"]), "Serialized cheap bound is not its declared same-payload comparator")
    expected = min(cheap, -bound)
    require(frac(record["certified_upper"]) == expected, "Incorrect final contrast intersection")
    require(record.get("economic_queries") == 0, "The pure certificate operation reports economic queries")
    return {"passed": True, "dual_lower": bound, "cheap_upper": cheap,
            "certified_upper": expected, "cut_count": len(cuts), "nonzero_dual_count": len(used),
            "nodes": len(original["nodes"]), "supports": len(original["case"]["payloads"]),
            "conditional_on_source_bound_economic_payload": True,
            "raw_dual_covers_declared_complete_support_class": True,
            "cheap_intersection_also_uses_supplied_original_optimum_lower": True,
            "final_intersection_is_original_policy_bound_not_claimed_sharp_class_extremum": True,
            "solver_imports": False, "floating_point_authority": False}


def cell_regret(nodes, bounds, L):
    xs, us, L = list(map(frac, nodes)), list(map(frac, bounds)), frac(L)
    require(len(xs) >= 2 and len(xs) == len(us) and L > 0, "Malformed regret grid")
    records = []
    for j, (left, right) in enumerate(zip(xs, xs[1:])):
        require(left < right, "Unordered regret grid")
        k = L*(right-left)**2/2
        candidates = [Q(0), Q(1)]
        interior = (us[j+1]-us[j]+k)/(2*k)
        if 0 <= interior <= 1:
            candidates.append(interior)
        def value(t):
            return us[j]*(1-t)+us[j+1]*t+k*t*(1-t)
        t = max(candidates, key=lambda s: (value(s), s))
        records.append({"left": left, "right": right, "maximizing_fraction": t, "bound": value(t)})
    return max([Q(0)]+[r["bound"] for r in records]), records


def _witness(curvatures, initial_slope, level, x):
    """Exact C1 piecewise-quadratic value and derivative on equal cells."""
    x, d = frac(x), Q(1, len(curvatures))
    value, slope, left = frac(level), frac(initial_slope), Q(0)
    for curvature in map(frac, curvatures):
        width = min(d, max(Q(0), x-left))
        value += slope*width+curvature*width*width/2
        slope += curvature*width
        left += d
        if left >= x:
            break
    return value, slope


def fixture_checks():
    """Rational boundary, sharpness, tangent and deliberate-corruption checks."""
    checks = 0
    witnesses = []
    for curvatures in ((1,), (3,), (1, 3), (3, 1), (1, 3, 1), (3, 1, 3)):
        for initial in (-3, -1, 0, 1):
            witnesses.append((curvatures, Q(initial), Q(2)))
    records_for_tampering = []
    for curvatures, initial, level in witnesses:
        mu, L = Q(min(curvatures)), Q(max(curvatures))
        ps = []
        for x in (Q(0), Q(1, 2), Q(1)):
            value, slope = _witness(curvatures, initial, level, x)
            ps.append({"a": x, "W": value, "U": value, "p_lower": slope, "p_upper": slope,
                       "g_lower": slope-Q(1, 8), "g_upper": slope+Q(1, 8)})
        case = {"A": Q(1), "incumbent": Q(1), "mu": mu, "L": L, "gradient_cap": Q(10),
                "delta": Q(0), "tau": Q(10), "omega": Q(10), "old_optimum_lower": Q(-10), "payloads": ps}
        problem = recover_geometry(case, Q(1), Q(1, 4))
        xs = problem["nodes"]
        true_jets = [_witness(curvatures, initial, level, x) for x in xs]
        feasible = [v-mu*x*x/2 for (v, _), x in zip(true_jets, xs)]
        feasible += [s-mu*x for (_, s), x in zip(true_jets, xs)]
        feasible += [p["p_lower"] for p in ps]
        require(all(l <= z <= u for l, z, u in zip(problem["box_lower"], feasible, problem["box_upper"])), "Fixture true jets outside box")
        point = [(l+u)/2 for l, u in zip(problem["box_lower"], problem["box_upper"])]
        cuts = [[0, ci] for ci in range(len(problem["constraints"]))]
        weights = [[ci, Q(1+(ci % 3), 64)] for ci in range(len(cuts))]
        residual, constant = list(problem["objective_linear"]), problem["objective_constant"]
        for ci, desc in enumerate(problem["constraints"]):
            real_value, _ = evaluate_constraint(problem, desc, feasible)
            require(real_value <= 0, "Rational true function violates full-support information")
            value, row = evaluate_constraint(problem, desc, point)
            affine_at_true = value+sum((r*(z-v) for r, z, v in zip(row, feasible, point)), Q(0))
            require(affine_at_true <= real_value, "Constraint tangent is not a minorant")
            y = weights[ci][1]
            constant += y*(value-sum((r*v for r, v in zip(row, point)), Q(0)))
            residual = [r+y*s for r, s in zip(residual, row)]
            checks += 2
        dual = constant+sum((min(r*l, r*u) for r, l, u in zip(residual, problem["box_lower"], problem["box_upper"])), Q(0))
        actual = _witness(curvatures, initial, level, Q(1, 4))[0]-_witness(curvatures, initial, level, Q(1))[0]
        require(actual <= -dual, "Exact dual excluded its compatible true witness")
        cheap = cheap_bound(case, Q(1), Q(1, 4))
        record = {"schema": 1, "problem": problem, "points": [point], "cuts": cuts,
                  "dual_weights": weights, "dual_lower": dual, "cheap_upper": cheap,
                  "certified_upper": min(cheap, -dual), "economic_queries": 0}
        checked = verify_certificate(encode(record))
        require(actual <= checked["certified_upper"], "Final bound excludes a compatible witness")
        records_for_tampering.append(encode(record))
        checks += 3
        # Exact original minimum includes feasible stationary points and boundaries.
        minima = [Q(0), Q(1)]
        d = Q(1, len(curvatures))
        for j, c in enumerate(map(frac, curvatures)):
            left = j*d
            _, slope = _witness(curvatures, initial, level, left)
            root = left-slope/c
            if left <= root <= left+d:
                minima.append(root)
        qstar = min(_witness(curvatures, initial, level, x)[0] for x in minima)
        grid = [Q(j, 8) for j in range(9)]
        for a in grid:
            qa = _witness(curvatures, initial, level, a)[0]
            u = [qa-_witness(curvatures, initial, level, x)[0] for x in grid]
            envelope, _ = cell_regret(grid, u, L)
            regret = qa-qstar
            require(regret <= envelope <= regret+L*Q(1, 8)**2/8, "Wrong whole-domain regret bracket")
            checks += 1
    sharp, cells = cell_regret([Q(0), Q(1)], [Q(0), Q(0)], Q(3))
    require(sharp == Q(3, 8) and cells[0]["maximizing_fraction"] == Q(1, 2), "Sharp rational 1/8 constant failed")
    checks += 1
    capped_case = {"A": Q(1), "incumbent": Q(1), "mu": Q(1), "L": Q(4),
        "gradient_cap": Q(1), "delta": Q(0), "tau": Q(10), "omega": Q(10),
        "old_optimum_lower": Q(1), "payloads": [{"a": Q(0), "W": Q(0), "U": Q(1),
        "p_lower": Q(0), "p_upper": Q(0), "g_lower": Q(-1), "g_upper": Q(1)}]}
    require(derivative_integral(capped_case, Q(0), Q(1), True) == 1,
            "Upper global derivative cap was not integrated")
    require(cheap_bound(capped_case, Q(1), Q(0)) == 0,
            "Supplied original-optimum lower bound was omitted from cheap comparator")
    weak_level_case = dict(capped_case, old_optimum_lower=Q(-10))
    require(cheap_bound(weak_level_case, Q(1), Q(0)) == Q(1, 2),
            "Original optimum bound fixture did not isolate its contribution")
    checks += 3
    # These are algebra-only mutations, never economic experimental observations.
    corruptions = []
    base = records_for_tampering[-1]
    for name in ("negative_weight", "narrower_box", "missing_support", "wrong_dual", "unpaid_cheap", "wrong_objective"):
        bad = copy.deepcopy(base)
        if name == "negative_weight": bad["dual_weights"][0][1] = "-1"
        if name == "narrower_box": bad["problem"]["box_lower"][0] = str(frac(bad["problem"]["box_lower"][0])+1)
        if name == "missing_support": bad["problem"]["constraints"].pop()
        if name == "wrong_dual": bad["dual_lower"] = str(frac(bad["dual_lower"])+1)
        if name == "unpaid_cheap": bad["cheap_upper"] = str(frac(bad["cheap_upper"])-1)
        if name == "wrong_objective": bad["problem"]["objective_linear"][0] = "5"
        try:
            verify_certificate(bad)
        except ValueError as exc:
            corruptions.append({"mutation": name, "correctly_rejected": True, "reason": str(exc)})
        else:
            raise AssertionError("Corrupted certificate was accepted: "+name)
        checks += 1
    for K in (Q(0), Q(1), Q(3)):
        for v in (Q(-4), Q(-1, 3), Q(0), Q(1, 3), Q(4)):
            value, t = conjugate(v, -Q(1, 4), Q(3, 4), K)
            require(value >= max(v*x-K*x*x/2 for x in [Q(j, 16) for j in range(-4, 13)]), "Bounded conjugate failed rational comparison")
            checks += 1
    return {"passed": True, "exact_checks": checks, "piecewise_quadratic_witnesses": len(witnesses),
            "sharp_grid_constant": "1/8", "sharp_case_regret": sharp,
            "deliberate_corruptions": corruptions, "economic_evaluations": 0,
            "scope": "Independent rational mathematics fixtures; no new economic observations or refitting.",
            "implementation": "Python standard library only; no support solver import"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", action="store_true")
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(args.fixtures != bool(args.input), "Choose exactly one of --fixtures and --input")
    if args.fixtures:
        result = fixture_checks()
    else:
        raw = args.input.read_bytes()
        data = json.loads(raw)
        rows = data if isinstance(data, list) else data.get("certificates", [data])
        result = {"passed": True, "source_sha256": hashlib.sha256(raw).hexdigest(),
                  "certificates": [verify_certificate(row) for row in rows]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(encode(result), handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"passed": True, "output": str(args.output),
                      "exact_checks": result.get("exact_checks"),
                      "certificates": len(result.get("certificates", []))}, sort_keys=True))


if __name__ == "__main__":
    main()
