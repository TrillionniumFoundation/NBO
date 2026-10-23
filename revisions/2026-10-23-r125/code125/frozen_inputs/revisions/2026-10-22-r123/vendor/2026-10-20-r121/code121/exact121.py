"""Independent rational original-economic witnesses used by the R121 protocol.

The economic formulas and 64-bin validation design retain their declared
R120 identity; R121 calls this implementation on newly selected R121 actions.
No inherited policy value or old independent result is substituted. Production
models, interval compiler and quadrature routines are not imported.
"""
from __future__ import annotations
import ast
from fractions import Fraction as F
import gzip,hashlib,importlib.util,io,json,os,time
from pathlib import Path
from io121 import REVISION, digest
BINS=64
TERMINAL_STEPS=32
R=F(1,32)
BETA=F(15,16)
EPSILON=F(1,2**20)
TAU=F(1,256)
PRIMITIVE_SHA256="a1a0e4ce5563d1105c3cea9eaad6678c609229446ba6794f7b8a7c03df01ebad"
COUNTS={}


def count(name, n=1):
    COUNTS[name] = COUNTS.get(name, 0) + n


def require(condition, message):
    count("executed_assertions")
    if not condition:
        raise AssertionError(message)


def exact(value):
    if isinstance(value, F):
        return value
    if isinstance(value, str):
        return F(value)
    return F(value)


def encoded(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encoded(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encoded(v) for v in value]
    return value


def key(x, a, alpha):
    return (tuple(float(v).hex() for v in x), float(a).hex(), float(alpha).hex())


def key_id(k):
    return hashlib.sha256(json.dumps(k, separators=(",", ":")).encode()).hexdigest()


def load_primitives():
    path = REVISION / "frozen108/code/independent94.py"
    require(digest(path) == PRIMITIVE_SHA256, "Independent primitive source identity")
    tree = ast.parse(path.read_text())
    allowed = {"__future__", "fractions", "json", "math", "pathlib", "time"}
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
    require(imports <= allowed, "No production or third-party scientific dependency")
    spec = importlib.util.spec_from_file_location("r121_exact_independent_primitives", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, dict(path=str(path.relative_to(REVISION)), sha256=PRIMITIVE_SHA256,
                        imports=sorted(imports), imported_after_source_commit_gate=True)


class ExactTrace:
    def __init__(self, path):
        self.raw = Path(path).open("xb")
        self.gz = gzip.GzipFile(filename="", mode="wb", fileobj=self.raw, mtime=0)
        self.text = io.TextIOWrapper(self.gz, encoding="utf-8", newline="\n")
        self.rows = 0

    def write(self, row):
        self.text.write(json.dumps(encoded(dict(sequence=self.rows, **row)), sort_keys=True) + "\n")
        self.rows += 1

    def flush(self):
        self.text.flush()
        self.raw.flush()
        os.fsync(self.raw.fileno())

    def close(self):
        self.text.close()
        self.raw.close()


def terminal(ir, y, alpha, support):
    count("terminal_contexts")
    require(all(F(1, 32) <= v <= F(27, 32) for v in y), "Invariant successor domain")
    lower, upper, action = ir.terminal_bounds(y, alpha, steps=TERMINAL_STEPS)
    capacity = F(1, 8) + sum(y) / (8 * len(y))
    require(0 <= action <= capacity, "Independent terminal feasibility")
    bisections = 0 if action in (F(0), capacity) else TERMINAL_STEPS
    count("actual_terminal_bisection_iterations", bisections)
    count("boundary_terminal_contexts" if bisections == 0 else "interior_terminal_contexts")
    require(F(0) <= upper - lower <= EPSILON, "Independent original terminal gap")
    poly = ir.polynomial_from_primitives(y, action)
    require(poly[2] == 5, "Original even-dimensional quadratic shock coefficient")
    risk, left, right, eta = ir.tail_threshold(poly, alpha)
    require(right - left == 2 * R * alpha and -R <= left <= right <= R,
            "Exact feasible continuous-risk density")
    dual = (ir.integral(poly, -R, left) + ir.integral(poly, right, R)) / (2 * R * (1 - alpha))
    excess = list(poly)
    excess[0] -= eta
    primal = eta + (ir.integral(excess, -R, left) + ir.integral(excess, right, R)) / (2 * R * (1 - alpha))
    require(primal == dual == risk, "Independent exact continuous-risk primal-dual identity")
    original_value = ir.economic_S(y) + action**2 + 4 * action**4 + BETA * risk
    require(original_value == upper, "Independent original one-date objective identity")
    result = dict(state=y, action=action, lower=lower, upper=upper, polynomial=poly,
                  tail_left=left, tail_right=right, threshold=eta, risk_primal=primal,
                  risk_dual=dual, terminal_steps=TERMINAL_STEPS,
                  terminal_steps_field_is_interior_budget=True,
                  terminal_bisections_executed=bisections,
                  exact_boundary_sign_checks_precede_interior_bisection=True)
    if support:
        count("independent_state_gradient_supports")
        d = len(y)
        zero, at_r = ir.next_state(y, action, F(0)), ir.next_state(y, action, R)
        g0, gr = ir.economic_gradient(zero, True), ir.economic_gradient(at_r, True)
        # The squared aggregate hinge is independent of this alternating shock.
        # Integrate the exact affine state gradient against the fixed tail density.
        tail_mean = (left**2 - right**2) / (4 * R * (1 - alpha))
        mean_gradient = [g0[j] + (gr[j] - g0[j]) * tail_mean / R for j in range(d)]
        b = [F(1, 2) if j % 2 == 0 else F(1, 4) for j in range(d)]
        p_action = 2 * action + 16 * action**3 + BETA * sum(bj * gj for bj, gj in zip(b, mean_gradient))
        checked_value, checked_derivative = ir.objective_gradient(y, action, alpha)
        require(checked_value == upper and checked_derivative == p_action,
                "Independent integrated state-gradient action derivative identity")
        s_gradient = ir.economic_gradient(y)
        p_state = [s_gradient[j] + BETA * (mean_gradient[j] * (F(1, 2) + (1 - y[(j + 1) % d]) / 16)
                   + mean_gradient[(j - 1) % d] * (F(1, 8) - y[(j - 1) % d] / 16)) for j in range(d)]
        lam = max(F(0), -p_action) if action == capacity else F(0)
        nu = max(F(0), p_action) if action == 0 else F(0)
        residual = p_action + lam - nu
        anchor = upper + lam * (action - capacity) - nu * action - residual**2 / 4
        slope = [v - lam / (8 * d) for v in p_state]
        require(lam >= 0 and nu >= 0 and anchor <= upper, "Feasible Lagrange minorant")
        result.update(state_gradient=p_state, action_gradient=p_action, multiplier_upper=lam,
                      multiplier_lower=nu, stationarity_residual=residual,
                      support_anchor=anchor, support_slope=slope)
    return result


def upper_tail(values, alpha):
    count("exact_finite_tail_sorts")
    k = len(values) * (1 - alpha)
    require(k.denominator == 1 and 1 <= k <= len(values), "Integral equal-mass tail count")
    return sum(sorted(values, reverse=True)[:int(k)]) / k


def evaluate_action(ir, k, values, trace):
    started = time.perf_counter()
    x, a, alpha = values["x"], values["a"], values["alpha"]
    mids, endpoints = [], []
    kid = key_id(k)
    for node in range(2 * BINS + 1):
        z = -R + F(node, 2 * BINS) * 2 * R
        is_midpoint = node % 2 == 1
        result = terminal(ir, ir.next_state(x, a, z), alpha, is_midpoint)
        trace.write(dict(key_id=kid, node=node, z=z, midpoint=is_midpoint, **result))
        (mids if is_midpoint else endpoints).append(result)
    require(len(mids) == BINS and len(endpoints) == BINS + 1, "Complete fixed independent mesh")
    stage = ir.economic_S(x) + a * a + 4 * a**4
    q_lower = stage + BETA * upper_tail([v["lower"] for v in mids], alpha)
    # Duplicated adjacent endpoints are separate equal-probability atoms. They
    # must never be deduplicated from the upper comparison distribution.
    endpoint_atoms = [endpoints[j]["upper"] for j in range(BINS)] + [endpoints[j + 1]["upper"] for j in range(BINS)]
    q_upper = stage + BETA * upper_tail(endpoint_atoms, alpha)
    j_lower, j_upper = q_lower, q_upper + BETA * EPSILON
    require(q_lower <= q_upper <= j_upper, "Original-optimal-future and actual-future interval order")
    tails = int(BINS * (1 - alpha))
    selected = sorted(range(BINS), key=lambda j: (-mids[j]["support_anchor"], j))[:tails]
    # Each selected bin has exactly 1/tails risk mass. This is a feasible
    # original continuous density, not a discretized replacement of the model.
    anchor = stage + BETA * sum(mids[j]["support_anchor"] for j in selected) / tails
    b = [F(1, 2) if j % 2 == 0 else F(1, 4) for j in range(len(x))]
    gradient = 2 * a + 16 * a**3 + BETA * sum(sum(v * bj for v, bj in zip(mids[j]["support_slope"], b)) for j in selected) / tails
    cap = F(1, 8) + sum(x) / (8 * len(x))
    delta = max(-a, min(cap - a, -gradient / 2))
    optimum_lower = anchor + gradient * delta + delta * delta
    require(optimum_lower <= q_upper, "Independent all-action lower and feasible upper compatibility")
    result = dict(key_id=kid, state=[float(v) for v in x], state_hex=list(k[0]),
                  action=float(a), action_hex=k[1], alpha=float(alpha),
                  q_lower=q_lower, q_upper=q_upper, j_lower=j_lower, j_upper=j_upper,
                  optimum_lower=optimum_lower, all_action_anchor=anchor,
                  all_action_gradient=gradient, all_action_minimizer=a + delta,
                  risk_bin_indices=selected, risk_bin_mass=F(1, tails),
                  bins=BINS, terminal_steps=TERMINAL_STEPS,
                  terminal_contexts=2 * BINS + 1, seconds=time.perf_counter() - started,
                  future_controller_allowance_added_exactly_once=BETA * EPSILON)
    count("unique_original_policy_evaluations")
    trace.flush()
    return result
