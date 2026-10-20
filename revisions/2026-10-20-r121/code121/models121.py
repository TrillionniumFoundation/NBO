"""Declared anchored critics and paid bounded VALUE/MARGINAL training.

This module has no original-economy imports. The campaign byte gate runs before
importing it. Floating solvers generate stored coefficients and proposals; their
success flags are not exact optimization or original-policy certificates.
"""
from __future__ import annotations

import copy
import math
import time

import numpy as np
from scipy.interpolate import BSpline
from scipy.optimize import linprog, lsq_linear

ARMS = ("quadratic", "relu", "hinge", "spline", "poly2", "poly3", "grid")
LOSSES = ("value", "marginal")
BOX = 128
COEFFICIENT_BITS = 30
V_KNOTS = (0., .25, .5, .75, 1.)


def capacity(x):
    x = np.asarray(x, dtype=float)
    return .125 + (x[..., 0]+x[..., 1])/16


def action_cost(a):
    return a*a + 4*a**4


def action_gradient(a):
    return 2*a + 16*a**3


def definition(arm, budget):
    if arm not in ARMS or budget not in (5, 9):
        raise ValueError("Undeclared representation or acquisition budget")
    common = dict(arm=arm, budget=budget, variables=["x0", "x1", "v"],
                  anchored_at_v_zero=True, coefficient_bits=COEFFICIENT_BITS,
                  coefficient_box=BOX, stored_coefficient_semantics="exact binary rational",
                  derivative_units="D_v phi / A(x), original-action units",
                  derivative_at_switch="side=-1 means feasible left limit; +1 right limit; 0 right canonical; endpoints only inward")
    if arm in ("quadratic", "poly2", "poly3"):
        exponents = [[0, 0, 1], [1, 0, 1], [0, 1, 1], [0, 0, 2]]
        if arm == "poly3":
            exponents = [[p, q, r] for total in range(1, 4)
                         for p in range(total+1) for q in range(total-p+1)
                         for r in [total-p-q] if r >= 1]
        common.update(type="monomial", exponents=exponents,
                      tensor_order="explicit exponent list")
        lower = [-BOX]*len(exponents)
        if arm == "quadratic":
            lower[3] = 0
    elif arm in ("relu", "hinge"):
        units = [dict(direction=[wx, wy, 1], state_center=[.5, .5],
                      threshold=q, scale=.25)
                 for wx in (-1, 0, 1) for wy in (-1, 0, 1)
                 for q in (.125, .375, .625, .875)]
        common.update(type="anchored_relu", base_exponents=[[0, 0, 1], [1, 0, 1], [0, 1, 1]],
                      units=units, tensor_order="base then wx, wy, threshold; threshold fastest",
                      implementation="matrix ReLU" if arm=="relu" else "coordinate-loop hinge",
                      neural_feature_search_performed=False,
                      hidden_directions_are_fixed_before_labels=True,
                      exact_corresponding_representation="hinge" if arm=="relu" else "relu")
        lower = [-BOX]*3 + [0]*len(units)
    elif arm == "spline":
        knots = [0.]*4 + ([.5] if budget==9 else []) + [1.]*4
        n = len(knots)-4
        columns = [[i, j, k] for i in range(n) for j in range(n) for k in range(1, n)]
        common.update(type="tensor_bspline", degree=3, knots=[knots, knots, knots],
                      axis_basis_counts=[n, n, n], columns=columns,
                      tensor_order="x0 then x1 then v; v fastest; v-index zero omitted")
        lower = [-BOX]*len(columns)
    else:
        state_knots = [j/(budget-1) for j in range(budget)]
        columns = [[i, j, k] for i in range(budget) for j in range(budget) for k in range(1, 5)]
        common.update(type="tensor_hat", degree=1, knots=[state_knots, state_knots, list(V_KNOTS)],
                      axis_basis_counts=[budget, budget, 5], columns=columns,
                      tensor_order="x0 then x1 then v; v fastest; v-index zero omitted")
        lower = [-BOX]*len(columns)
    common.update(coefficient_lower=lower, coefficient_upper=[BOX]*len(lower),
                  feature_count=len(lower))
    return common


def _hat(values, knots, derivative=False, side=0):
    values = np.asarray(values, float).reshape(-1)
    knots = np.asarray(knots, float)
    if np.any((values < knots[0]) | (values > knots[-1])):
        raise ValueError("Hat evaluation outside the declared domain")
    sides = np.broadcast_to(np.asarray(side, int), values.shape)
    # At an interior switch each requested one-sided derivative is explicit.
    cells_right = np.searchsorted(knots, values, side="right")-1
    cells_left = np.searchsorted(knots, values, side="left")-1
    cells = np.where(sides < 0, cells_left, cells_right)
    cells = np.clip(cells, 0, len(knots)-2)
    widths = knots[cells+1]-knots[cells]
    result = np.zeros((len(values), len(knots)))
    ids = np.arange(len(values))
    if derivative:
        result[ids, cells] = -1/widths
        result[ids, cells+1] = 1/widths
    else:
        result[ids, cells] = (knots[cells+1]-values)/widths
        result[ids, cells+1] = (values-knots[cells])/widths
    return result


def _bspline(values, knots, degree, derivative=0):
    n = len(knots)-degree-1
    b = BSpline(knots, np.eye(n), degree, extrapolate=False)
    if derivative:
        b = b.derivative(derivative)
    return np.asarray(b(np.asarray(values, float)), float)


def feature_matrix(desc, u, derivative=False, side=0):
    u = np.asarray(u, float)
    if u.ndim != 2 or u.shape[1] != 3 or np.any(~np.isfinite(u)) or np.any((u < 0) | (u > 1)):
        raise ValueError("Declared features require finite rows in [0,1]^3")
    x0, x1, v = u.T
    kind = desc["type"]
    if kind == "monomial":
        cols = []
        for p, q, r in desc["exponents"]:
            col = x0**p * x1**q
            col = col * (r*v**(r-1) if derivative else v**r)
            cols.append(col)
        answer = np.column_stack(cols)
    elif kind == "anchored_relu":
        base = np.column_stack([np.ones(len(u)), x0, x1])
        if not derivative:
            base = base*v[:, None]
        sides = np.broadcast_to(np.asarray(side, int), (len(u),))
        columns = []
        # The two encodings have exactly the same declared finite features.
        # The hinge control uses an explicit coordinate loop; no new labels or
        # free feature search is assigned to it.
        if desc["implementation"] == "matrix ReLU":
            directions = np.array([r["direction"] for r in desc["units"]], float)
            thresholds = np.array([r["threshold"] for r in desc["units"]])
            centered = u.copy(); centered[:, :2] -= .5
            z = (centered @ directions.T-thresholds)/4
            anchor = ((centered[:, :2] @ directions[:, :2].T)-thresholds)/4
            if derivative:
                nonlinear = ((z > 0) | ((z == 0) & (sides[:, None] >= 0))).astype(float)/4
            else:
                nonlinear = np.maximum(z, 0)-np.maximum(anchor, 0)
        else:
            for unit in desc["units"]:
                wx, wy, _ = unit["direction"]
                z0 = (wx*(x0-.5)+wy*(x1-.5)-unit["threshold"])/4
                z = z0+v/4
                columns.append((((z > 0) | ((z == 0) & (sides >= 0))).astype(float)/4)
                               if derivative else np.maximum(z, 0)-np.maximum(z0, 0))
            nonlinear = np.column_stack(columns)
        answer = np.column_stack([base, nonlinear])
    elif kind in ("tensor_bspline", "tensor_hat"):
        if kind == "tensor_bspline":
            b0 = _bspline(x0, desc["knots"][0], 3)
            b1 = _bspline(x1, desc["knots"][1], 3)
            bv = _bspline(v, desc["knots"][2], 3, int(derivative))
        else:
            b0 = _hat(x0, desc["knots"][0]); b1 = _hat(x1, desc["knots"][1])
            bv = _hat(v, desc["knots"][2], derivative, side)
        answer = np.column_stack([b0[:, i]*b1[:, j]*bv[:, k] for i, j, k in desc["columns"]])
    else:
        raise ValueError("Unknown frozen feature type")
    if derivative:
        answer = answer/capacity(u[:, :2])[:, None]
    if answer.shape != (len(u), desc["feature_count"]) or np.any(~np.isfinite(answer)):
        raise ArithmeticError("Invalid finite feature matrix")
    return answer


def training_design(desc, labels):
    value_rows = labels["values"]
    vu = np.array([row["u"] for row in value_rows])
    va = feature_matrix(desc, vu)
    vl = np.array([row["continuation_difference_lower"] for row in value_rows])
    vh = np.array([row["continuation_difference_upper"] for row in value_rows])
    rows = []
    for index, row in enumerate(labels["marginals"]):
        v = row["u"][2]
        sides = [1] if v==0 else [-1] if v==1 else [-1, 1] if desc["type"] in ("anchored_relu", "tensor_hat") else [0]
        for side in sides:
            rows.append(dict(label_index=index, u=row["u"], side=side,
                lower=row["continuation_marginal_lower"], upper=row["continuation_marginal_upper"]))
    du = np.array([row["u"] for row in rows])
    ds = np.array([row["side"] for row in rows])
    da = feature_matrix(desc, du, derivative=True, side=ds)
    dl = np.array([row["lower"] for row in rows]); dh = np.array([row["upper"] for row in rows])
    return dict(value_matrix=va, value_lower=vl, value_upper=vh,
                derivative_matrix=da, derivative_lower=dl, derivative_upper=dh,
                derivative_rows=rows, value_rows=[dict(u=row["u"], label_index=j) for j, row in enumerate(value_rows)])


def _plain(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


def fit(desc, labels, loss, sink=None):
    if loss not in LOSSES:
        raise ValueError("Undeclared fitted loss")
    started = time.perf_counter()
    td = time.perf_counter(); design = training_design(desc, labels); design_seconds = time.perf_counter()-td
    bounds = (np.array(desc["coefficient_lower"], float), np.array(desc["coefficient_upper"], float))
    if sink is not None:
        sink(dict(event="fit-design-complete", loss=loss, basis=desc,
                  design=_plain(design), design_seconds=design_seconds))
    ts = time.perf_counter()
    if loss == "value":
        result = lsq_linear(design["value_matrix"], (design["value_lower"]+design["value_upper"])/2,
                            bounds=bounds, method="trf", tol=1e-12, max_iter=1000, lsmr_tol=1e-14)
        raw = dict(success=bool(result.success), status=int(result.status), message=result.message,
                   x=result.x.tolist(), cost=float(result.cost), optimality=float(result.optimality),
                   active_mask=result.active_mask.tolist(), iterations=int(result.nit))
        theta_raw = result.x
    else:
        a, lo, hi = design["derivative_matrix"], design["derivative_lower"], design["derivative_upper"]
        aub = np.vstack([np.column_stack([a, -np.ones(len(a))]),
                         np.column_stack([-a, -np.ones(len(a))])])
        bub = np.concatenate([lo, -hi])
        objective = np.r_[np.zeros(a.shape[1]), 1.]
        result = linprog(objective, A_ub=aub, b_ub=bub,
            bounds=list(zip(bounds[0], bounds[1]))+[(0, None)], method="highs",
            options={"presolve": True, "dual_feasibility_tolerance": 1e-9,
                     "primal_feasibility_tolerance": 1e-9, "ipm_optimality_tolerance": 1e-10})
        raw = dict(success=bool(result.success), status=int(result.status), message=result.message,
                   x=None if result.x is None else result.x.tolist(),
                   objective=None if result.fun is None else float(result.fun), iterations=int(result.nit),
                   inequality_marginals=None if result.ineqlin.marginals is None else result.ineqlin.marginals.tolist(),
                   inequality_residuals=None if result.ineqlin.residual is None else result.ineqlin.residual.tolist(),
                   lower_marginals=None if result.lower.marginals is None else result.lower.marginals.tolist(),
                   upper_marginals=None if result.upper.marginals is None else result.upper.marginals.tolist(),
                   constraint_order="first A theta - t <= lower; then -A theta - t <= -upper",
                   dual_certificate_is_not_inferred_from_float_success=True)
        theta_raw = None if result.x is None else result.x[:-1]
    solve_seconds = time.perf_counter()-ts
    if sink is not None:
        sink(dict(event="fit-solver-complete", loss=loss, raw_solver=raw, solve_seconds=solve_seconds))
    if not result.success or theta_raw is None or np.any(~np.isfinite(theta_raw)):
        error = RuntimeError("Declared bounded fit failed; preserve the complete attempt")
        error.fit121 = dict(basis=desc, loss=loss, raw_solver=raw, design=_plain(design))
        raise error
    tr = time.perf_counter()
    theta = np.clip(np.rint(theta_raw*2**COEFFICIENT_BITS)/2**COEFFICIENT_BITS, *bounds)
    marginal = design["derivative_matrix"] @ theta
    residual = np.maximum(marginal-design["derivative_lower"], design["derivative_upper"]-marginal)
    value = design["value_matrix"] @ theta
    vmid = (design["value_lower"]+design["value_upper"])/2
    report = dict(loss=loss, raw_solver=raw, design_seconds=design_seconds,
                  solver_seconds=solve_seconds, rounded_readout=theta.tolist(),
                  coefficient_dyadic_numerators=[int(round(v*2**COEFFICIENT_BITS)) for v in theta],
                  coefficient_denominator=2**COEFFICIENT_BITS,
                  rounding_rule="nearest dyadic at 30 bits, ties to even; project to the declared box",
                  floating_node_marginal_worst_residual=float(np.max(residual)),
                  floating_value_midpoint_mean_squared_residual=float(np.mean((value-vmid)**2)),
                  residual_is_finite_node_only=True,
                  exact_fit_optimality_claim=False,
                  coefficient_rounding_and_diagnostics_seconds=time.perf_counter()-tr,
                  fit_seconds=time.perf_counter()-started)
    model = dict(kind="r121-anchored-root-critic", basis=desc, loss=loss,
                 theta=theta.tolist(), theta_hex=[float(v).hex() for v in theta],
                 anchor=copy.deepcopy(labels["anchor"]),
                 theta_numerators=report["coefficient_dyadic_numerators"], theta_denominator=2**COEFFICIENT_BITS,
                 target="original continuous-risk root continuation difference; terminal model and policy unchanged",
                 fit_global_certificate_claim=False)
    return model, report, design


def hinge_copy(relu_model, relu_report):
    model, report = copy.deepcopy(relu_model), copy.deepcopy(relu_report)
    model["basis"] = definition("hinge", model["basis"]["budget"])
    model["exact_feature_and_readout_identity_with_relu"] = True
    report["copied_readout_not_an_independent_fit"] = True
    report["full_relu_fit_and_label_charge_required"] = True
    return model, report


def _anchor(model, x):
    a = model["anchor"]
    knots = a["state_knots"]
    values = np.asarray(a["q0_midpoints"]).reshape(len(knots), len(knots))
    b0 = _hat([x[0]], knots)[0]; b1 = _hat([x[1]], knots)[0]
    return float(b0 @ values @ b1)


def critic(model, x, v, include_anchor=True):
    x, v = np.asarray(x, float), np.asarray(v, float).reshape(-1)
    u = np.column_stack([np.broadcast_to(x, (len(v), 2)), v])
    learned = feature_matrix(model["basis"], u) @ np.asarray(model["theta"])
    answer = action_cost(capacity(x)*v)+learned
    return answer + (_anchor(model, x) if include_anchor else 0.)


def action_breaks(desc, x):
    answer = [0., 1.]
    if desc["type"] == "anchored_relu":
        for unit in desc["units"]:
            wx, wy, _ = unit["direction"]
            cut = unit["threshold"]-wx*(x[0]-.5)-wy*(x[1]-.5)
            if 0 < cut < 1:
                answer.append(float(cut))
    elif desc["type"] in ("tensor_bspline", "tensor_hat"):
        answer.extend(desc["knots"][2])
    return sorted(set(answer))


def _piece_polynomial(model, x, mid):
    """Coefficients in t=v-mid, obtained from the actual declared basis."""
    from numpy.polynomial import Polynomial as P
    desc, theta = model["basis"], np.asarray(model["theta"])
    vpoly = P([mid, 1.]); a = float(capacity(x))*vpoly
    answer = a*a+4*a**4
    kind = desc["type"]
    if kind == "monomial":
        for coef, (p, q, r) in zip(theta, desc["exponents"]):
            answer += coef*x[0]**p*x[1]**q*vpoly**r
    elif kind == "anchored_relu":
        answer += (theta[0]+theta[1]*x[0]+theta[2]*x[1])*vpoly
        for coef, unit in zip(theta[3:], desc["units"]):
            wx, wy, _ = unit["direction"]
            base = (wx*(x[0]-.5)+wy*(x[1]-.5)-unit["threshold"])/4
            answer += -coef*max(base, 0)
            if base+mid/4 > 0:
                answer += coef*(P([base])+vpoly/4)
    elif kind == "tensor_bspline":
        b0 = _bspline([x[0]], desc["knots"][0], 3)[0]
        b1 = _bspline([x[1]], desc["knots"][1], 3)[0]
        coefficients = []
        for order in range(4):
            bv = _bspline([mid], desc["knots"][2], 3, order)[0]
            coefficients.append(sum(c*b0[i]*b1[j]*bv[k] for c, (i, j, k) in zip(theta, desc["columns"]))/math.factorial(order))
        answer += P(coefficients)
    elif kind == "tensor_hat":
        u = np.array([[x[0], x[1], mid]])
        val = float(feature_matrix(desc, u)[0] @ theta)
        derivative_v = float(feature_matrix(desc, u, derivative=True)[0] @ theta)*float(capacity(x))
        answer += P([val, derivative_v])
    else:
        raise ValueError("Unknown piece type")
    return answer


def actor(model, x):
    """Enumerate all pieces and all computed real critical points, then round.

This is a strong full-piece numerical proposal search. Qualification uses the
original model later. No floating root completeness or fitted-global-optimum
certificate is inferred from this search.
"""
    started = time.perf_counter()
    x = np.asarray(x, float)
    if x.shape != (2,) or np.any((x < 0) | (x > 1)):
        raise ValueError("One original two-dimensional state is required")
    breaks = action_breaks(model["basis"], x)
    candidates = list(breaks); pieces = []
    for left, right in zip(breaks[:-1], breaks[1:]):
        mid = (left+right)/2
        polynomial = _piece_polynomial(model, x, mid)
        deriv = polynomial.deriv()
        roots = deriv.roots()
        record = dict(left=left, right=right, center=mid,
                      polynomial_coefficients=polynomial.coef.tolist(), derivative_coefficients=deriv.coef.tolist(), roots=[])
        for root in roots:
            real, imag = float(np.real(root)), float(np.imag(root))
            value = real+mid
            near_real = abs(imag) <= 2**-36*(1+abs(real))
            inside = left-2**-36 <= value <= right+2**-36
            accepted = near_real and inside
            if accepted:
                candidates.append(float(np.clip(value, left, right)))
            record["roots"].append(dict(real=real, imaginary=imag, normalized_action=value,
                accepted_as_proposal_candidate=bool(accepted), near_real=bool(near_real), in_piece_tolerance=bool(inside),
                derivative_residual=float(abs(deriv(real)))))
        pieces.append(record)
    candidates = sorted(set(candidates))
    values = critic(model, x, candidates, include_anchor=False)
    if np.any(~np.isfinite(values)):
        raise ArithmeticError("Nonfinite learned proposal objective")
    selected = int(np.argmin(values))
    cap = float(capacity(x)); raw_action = cap*candidates[selected]
    action = min(math.floor(raw_action*2**30)/2**30, math.floor(cap*2**30)/2**30)
    u = np.array([[x[0], x[1], action/cap]])
    left = float(feature_matrix(model["basis"], u, True, -1)[0] @ np.asarray(model["theta"]))+float(action_gradient(action))
    right = float(feature_matrix(model["basis"], u, True, 1)[0] @ np.asarray(model["theta"]))+float(action_gradient(action))
    return action, dict(rule="all declared action pieces and every computed real derivative root plus endpoints",
        state=x.tolist(), state_hex=[float(v).hex() for v in x], capacity=cap,
        pieces=pieces, candidate_normalized_actions=candidates, candidate_anchored_objective=values.tolist(),
        selected_candidate=selected, unrounded_action=raw_action, action=action, action_hex=action.hex(),
        rounded_normalized_action=action/cap,
        rounding_rule="downward 30-bit original action then downward feasible capacity",
        fitted_left_action_derivative=left, fitted_right_action_derivative=right,
        exact_global_optimizer_claim=False, original_optimizer_claim=False,
        action_piece_count=len(pieces), polynomial_root_count=sum(len(r["roots"]) for r in pieces),
        evaluated_proposal_count=len(candidates), seconds=time.perf_counter()-started)
