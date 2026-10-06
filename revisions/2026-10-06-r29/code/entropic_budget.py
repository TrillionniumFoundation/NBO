"""Primitive-only training allocation for recursive-entropic square-critic NBO.

The reference gain, risk margins, local tolerances, learning rates and caps
are set before any critic target is evaluated. The theorem is a real-
arithmetic statement. Rounded policies require the independent R28 verifier.
No optimal value or optimal feedback is an input to planning or training.
"""
from __future__ import annotations
from pathlib import Path
import math
import sys
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
for sub in ('2026-10-05-r23', '2026-10-05-r25', '2026-10-06-r27'):
    sys.path.insert(0, str(ROOT / 'revisions' / sub / 'code'))
from policy_certificate import Ball, up, down
from constructive import budget, dyadic_scale
from entropic_certificate import validate, nominal_transform, norm2, add, mul, div, margin


def _positive(x: float, name: str) -> float:
    x = float(x)
    if not math.isfinite(x) or x <= 0:
        raise ValueError(f'{name} must be positive and finite')
    return x


def plan(model: dict, theta: float, tolerance: float = 1e-4,
         reference_gain: np.ndarray | None = None, slack: float = 1e-2) -> dict:
    """Construct a sufficient schedule from economic primitives alone.

    The supplied reference must pass this sufficient spectral-domain test.
    Failure is not proof that the economy has infinite optimal cost. A fixed
    gain 2I is the declared default, not a structural optimal-policy solve.
    All rounding allowances for the returned control remain independently
    assessed by the own-policy verifier; caps concern ideal real arithmetic.
    """
    tol = _positive(tolerance, 'tolerance')
    eta = _positive(slack, 'slack')
    T, d = model['A'].shape[:2]
    ref = (np.broadcast_to(2 * np.eye(d), (T, d, d)).copy()
           if reference_gain is None else np.array(reference_gain, dtype=float, copy=True))
    validate(model, ref, theta)
    beta = float(model['beta'])
    sig = norm2(Ball.exact(model['Sigma']))
    tau = Ball.exact(model['Sigma']).trace().upper()
    q = np.min(np.diagonal(model['Q'], axis1=1, axis2=2), axis=1)
    r = np.min(np.diagonal(model['R'], axis1=1, axis2=2), axis=1)
    pbar = np.zeros(T + 1)
    pbar[T] = norm2(Ball.exact(model['Qf']))
    gamma = np.ones(T)
    envelope = []
    # Scalar PSD envelope: Pbar_t I dominates Sref_t + eta Q_t + beta Fref'Psi Fref.
    for t in range(T - 1, -1, -1):
        A, B, Q, R = (Ball.exact(model[n][t]) for n in ('A', 'B', 'Q', 'R'))
        L = Ball.exact(ref[t])
        F = A - B @ L
        gamma[t] = margin(theta, sig, float(pbar[t + 1]))
        stage = norm2(Q + L.T @ R @ L + Q.scale(eta))
        pbar[t] = add(stage, mul(beta, norm2(F), norm2(F),
                                   div(float(pbar[t + 1]), float(gamma[t]))))
        envelope.append(dict(date=t, stage_upper=stage, reference_transition_upper=norm2(F),
                             coefficient_upper=float(pbar[t]), next_domain_margin=float(gamma[t])))
    # qstar bounds the lower-subsolution perturbation; it is not a fitted quantity.
    qstar = float(min(q))
    a = np.array([norm2(Ball.exact(x)) for x in model['A']])
    b = np.array([norm2(Ball.exact(x)) for x in model['B']])
    Ls = np.array([mul(d, div(float(pbar[t + 1]), float(gamma[t]))) for t in range(T)])
    f = np.array([mul(float(a[t]), add(1., div(mul(beta, float(b[t]), float(b[t]),
                             float(Ls[t])), float(down(d * float(r[t])))))) for t in range(T)])
    lambdas = np.zeros(T + 1)
    mus = np.zeros(T + 1)
    lower_f = np.zeros(T)
    # For zeta_t <= sqrt(s r_t q_t), the nonlinear subsolution account is
    # majorized by s*lambda_t and s*mu_t as long as delta <= qstar and s <= eta.
    for t in range(T - 1, -1, -1):
        gamma_sq_lower = float(down(float(gamma[t]) * float(gamma[t])))
        drift_cap = div(qstar, gamma_sq_lower)
        zeta_cap = float(up(math.sqrt(mul(eta, float(r[t]), float(q[t])))))
        lower_f[t] = add(float(f[t]), div(mul(float(b[t]), add(zeta_cap,
                 mul(beta, float(b[t]), float(f[t]), drift_cap))), float(r[t])))
        local = 0. if t == T - 1 else float(q[t])
        lambdas[t] = add(local, mul(beta, float(lower_f[t]), float(lower_f[t]),
                                          div(float(lambdas[t + 1]), gamma_sq_lower)))
        mus[t] = mul(beta, add(float(mus[t + 1]),
                                 div(mul(tau, float(lambdas[t + 1])), float(gamma[t]))))
    weight = add(mul(float(model['initial_radius_sq']), float(lambdas[0])), float(mus[0]))
    # Reserve half of the welfare allowance for implementation/rounding checks.
    choices = [eta]
    if weight > 0:
        choices.append(float(down(tol / (2 * weight))))
    for t in range(1, T):
        if lambdas[t] > 0:
            choices.append(float(down(qstar / float(lambdas[t]))))
    s = min(choices)
    if not math.isfinite(s) or s <= 0:
        raise ArithmeticError('Primitive allocation not representable at this precision')
    rows = []
    for t in range(T - 2, -1, -1):
        j = t + 1
        coercivity = float(down(d * float(q[j])))
        upper = float(Ls[t])
        chi = mul(beta, float(b[t]), float(f[t]))
        if chi == 0:
            target = max(1., upper)  # The action is continuation independent.
        else:
            product = float(down(float(down(s * float(q[t]))) * float(r[t])))
            numerator = float(down(d * float(down(math.sqrt(product)))))
            target = float(down(numerator / chi))
        if not target > 0:
            raise ArithmeticError('Training tolerance below representable range')
        scale = dyadic_scale(coercivity, .5)
        c = scale * scale
        alpha = float(down(1 / (4 * upper)))
        initial = mul(float(up(math.sqrt(d))), upper)
        cap = budget(initial, target / 2, alpha, c) + 2
        rows.append(dict(date=t, continuation_date=j, m=coercivity, L=upper,
                         scale=scale, c=c, alpha=alpha, target=target,
                         initial_error_upper=initial, ideal_iteration_cap=cap,
                         closed_loop_upper=float(f[t]), sensitivity_upper=chi))
    return dict(theta=float(theta), tolerance=tol, slack=eta, local_scale=s,
                coefficient_envelope=pbar.tolist(), domain_margins=gamma.tolist(),
                coefficient_weights=lambdas.tolist(), constant_weights=mus.tolist(),
                nominal_policy_allowance=mul(s, weight), reference_gain=ref.tolist(),
                reference_envelope=envelope, dates=rows,
                total_ideal_iteration_cap=sum(x['ideal_iteration_cap'] for x in rows),
                allocation_scope='Before all own-policy targets and fits; ideal real arithmetic',
                required_final_check='Independent outward full adapted-policy certificate')


def solve(model: dict, theta: float, tolerance: float = 1e-4, seed: int = 2901,
          reference_gain: np.ndarray | None = None, slack: float = 1e-2) -> tuple:
    """Train with a prespecified cap; failures are retained, never silently rescued."""
    allocation = plan(model, theta, tolerance, reference_gain, slack)
    T, d = model['A'].shape[:2]
    beta = float(model['beta'])
    K = np.zeros((T, d, d)); Wstore = np.zeros_like(K)
    P = np.empty((T + 1, d, d)); P[T] = model['Qf']
    rows = {x['date']: x for x in allocation['dates']}
    records = []
    rng = np.random.default_rng(seed)
    for t in range(T - 1, -1, -1):
        psi = nominal_transform(P[t + 1], model['Sigma'], theta)
        phat = psi
        if t < T - 1:
            row = rows[t]; M = d * psi
            O = np.eye(d)[rng.permutation(d)] * rng.choice([-1., 1.], size=(d, 1))
            W = row['scale'] * O
            checks = 0; updates = 0; residual = math.inf
            for j in range(row['ideal_iteration_cap'] + 1):
                if j % 8 == 0 or j == row['ideal_iteration_cap']:
                    residual = (Ball.exact(W).T @ Ball.exact(W) - Ball.exact(M)).norm_f()
                    checks += 1
                    if residual <= row['target']:
                        break
                if j < row['ideal_iteration_cap']:
                    W -= row['alpha'] * (W @ (W.T @ W - M))
                    updates += 1
                    if not np.isfinite(W).all():
                        raise ArithmeticError('Nonfinite critic iterate within frozen cap')
            Wstore[t + 1] = W; phat = W.T @ W / d
            records.append(dict(**row, updates=updates, gram_checks=checks,
                                outward_stored_target_residual=float(residual),
                                threshold_met=bool(residual <= row['target'])))
        A, B, Q, R = (model[n][t] for n in ('A', 'B', 'Q', 'R'))
        K[t] = np.linalg.solve(R + beta * B.T @ phat @ B, beta * B.T @ phat @ A)
        F = A - B @ K[t]
        P[t] = Q + K[t].T @ R @ K[t] + beta * F.T @ psi @ F
        P[t] = (P[t] + P[t].T) / 2
    return K, Wstore, dict(plan=allocation, dates=records, seed=int(seed),
        hidden_updates=sum(x['updates'] for x in records),
        gram_checks=sum(x['gram_checks'] for x in records),
        all_training_thresholds_met=all(x['threshold_met'] for x in records),
        actor_solves=T, own_policy_matrix_updates=T, entropic_transforms=T,
        primitive_envelope_matrix_updates=T, simulation_transitions=0)
