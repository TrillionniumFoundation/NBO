"""Primitive-only finite training budgets for the NBO capital construction.

The envelope and all caps are computed before fitting any continuation. The
real-arithmetic theorem does not certify floating-point execution: every
returned policy must pass the separate outward Bellman verifier. Riccati is
not an input and no optimum is used to initialize or fit a critic.
"""
from pathlib import Path
import math
import sys
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'revisions/2026-10-05-r23/code'))
sys.path.insert(0, str(ROOT / 'revisions/2026-10-05-r25/code'))
from policy_certificate import Ball, value_balls, up
from constructive import budget, dyadic_scale


def allocation(model: dict, tolerance: float = 1e-4) -> dict:
    """Compute a schedule using primitives, not a fitted or optimal value.

    The experiment uses the declared diagonal-Q/R class. General SPD costs
    require independently supplied coercivity bounds, not diagonal minima.
    """
    if not math.isfinite(tolerance) or tolerance <= 0:
        raise ValueError('Positive finite tolerance required')
    A, B, Q, R, Qf = [np.asarray(model[k], dtype=float)
                       for k in ('A', 'B', 'Q', 'R', 'Qf')]
    T, d = A.shape[:2]
    if A.shape != (T, d, d) or B.shape != A.shape or Q.shape != A.shape or R.shape != A.shape:
        raise ValueError('Compatible square state and control arrays required')
    if not all(np.isfinite(x).all() for x in (A, B, Q, R, Qf)):
        raise ValueError('Nonfinite primitive')
    for cost in (Q, R):
        for matrix in cost:
            if not np.array_equal(matrix, np.diag(np.diag(matrix))) or np.min(np.diag(matrix)) <= 0:
                raise ValueError('This implementation requires positive diagonal stage costs')
    beta = float(model['beta'])
    if not 0 < beta <= 1:
        raise ValueError('Discount factor must be in (0,1]')
    ps, cs = value_balls(A, B, Q, R, Qf, model['Sigma'], beta, np.zeros_like(A))
    reference = float(up(model['initial_radius_sq'] * ps[0].norm_inf() + cs[0].upper()))
    if not 0 < reference < math.inf:
        raise ArithmeticError('Finite positive zero-policy reference required')
    # Half of the requested tolerance is reserved for nominal construction.
    eta = tolerance / (2 * reference)
    upper = [None] * (T + 1)
    upper[T] = Ball.exact(Qf)
    for t in range(T-1, -1, -1):
        aa = Ball.exact(A[t])
        upper[t] = (Ball.exact(Q[t]).scale(float(up(1 + eta)))
                    + (aa.T @ upper[t+1] @ aa).scale(beta))
    rows = []
    for t in range(T-2, -1, -1):
        j = t + 1
        q, r = float(np.min(np.diag(Q[t]))), float(np.min(np.diag(R[t])))
        m = d * float(np.min(np.diag(Q[j])))
        L = float(up(d * upper[j].norm_inf()))
        a = float(Ball.exact(A[t]).norm_f())
        b = float(Ball.exact(B[t]).norm_f())
        chi = beta*b*a*(1+beta*b*b*L/(d*r))
        target = d*math.sqrt(eta*q*r)/(2*chi) if chi else 1.
        s = dyadic_scale(m, .5)
        c = s*s
        alpha = 1/(4*L)
        # A deliberately loose a priori radius avoids subtractive cancellation.
        initial_error_bound = float(up(math.sqrt(d) * L))
        cap = budget(initial_error_bound, target/2, alpha, c)
        rows.append(dict(date=t, continuation_date=j, m=m, L=L, c=c,
                         scale=s, alpha=alpha, target=target,
                         initial_error_bound=initial_error_bound,
                         ideal_iteration_cap=cap))
    return dict(reference_value_upper=reference, eta=eta, dates=rows,
                total_ideal_iteration_cap=sum(r['ideal_iteration_cap'] for r in rows),
                allocation_scope='Before any fit; real-arithmetic cap with a separate rounded-output certificate')


def solve(model: dict, tolerance: float = 1e-4) -> tuple:
    """Return a candidate and a complete capped fitting record, not a certificate."""
    plan = allocation(model, tolerance)
    A, B, Q, R, Qf = [model[k] for k in ('A', 'B', 'Q', 'R', 'Qf')]
    beta = model['beta']
    T, d = A.shape[:2]
    rows = {r['date']: r for r in plan['dates']}
    K = np.zeros_like(A)
    P = np.empty((T+1, d, d)); P[-1] = Qf
    factors = np.zeros_like(A)
    records = []
    for t in range(T-1, -1, -1):
        if t == T-1:
            phat = Qf.copy()
        else:
            row = rows[t]
            M = d * P[t+1]
            W = row['scale'] * np.eye(d)
            checks = 0
            residual = math.inf
            updates = 0
            for j in range(row['ideal_iteration_cap']+1):
                if j % 8 == 0 or j == row['ideal_iteration_cap']:
                    residual = float((Ball.exact(W).T @ Ball.exact(W) - Ball.exact(M)).norm_f())
                    checks += 1
                    if residual <= row['target']:
                        break
                if j < row['ideal_iteration_cap']:
                    W -= row['alpha'] * (W @ (W.T @ W - M))
                    updates += 1
                    if not np.isfinite(W).all():
                        raise ArithmeticError('Nonfinite factor within fixed budget')
            factors[t+1] = W
            phat = W.T @ W / d
            records.append(dict(**row, hidden_updates=updates, gram_checks=checks,
                                stored_target_residual=residual,
                                threshold_met=bool(residual <= row['target'])))
        H = R[t] + beta * B[t].T @ phat @ B[t]
        K[t] = np.linalg.solve(H, beta * B[t].T @ phat @ A[t])
        F = A[t] - B[t] @ K[t]
        P[t] = Q[t] + K[t].T @ R[t] @ K[t] + beta * F.T @ P[t+1] @ F
        P[t] = (P[t] + P[t].T) / 2
    return K, factors, dict(plan=plan, dates=records,
        hidden_updates=sum(r['hidden_updates'] for r in records),
        gram_checks=sum(r['gram_checks'] for r in records),
        all_training_thresholds_met=all(r['threshold_met'] for r in records),
        actor_solves=T, own_policy_matrix_updates=T,
        primitive_envelope_matrix_updates=T, reference_policy_matrix_updates=T,
        simulation_transitions=0)
