"""R25: constructive square-activation NBO with a finalized own-policy future.

No optimal value/gain is used by backward_nbo. Each target is evaluation of the
future gains already returned. The separate Riccati baseline is imported only
by the execution script. Real-arithmetic iteration budgets are not asserted
to certify floating-point rounding: the inherited outward verifier does that.
"""
from pathlib import Path
import math
import sys
import numpy as np
from policy_certificate import Ball, value_balls, up


def budget(e0: float, target: float, alpha: float, c: float) -> int:
    if not all(math.isfinite(x) for x in (e0, target, alpha, c)):
        raise ValueError('Nonfinite budget input')
    if e0 < 0 or target <= 0 or alpha <= 0 or c <= 0 or 2*alpha*c >= 1:
        raise ValueError('Require e0>=0, target>0, and 0<2 alpha c<1')
    if e0 <= target:
        return 0
    return max(0, math.ceil(math.log(e0 / target) / -math.log1p(-2*alpha*c)))


def dyadic_scale(m: float, multiplier: float) -> float:
    if not math.isfinite(m) or m <= 0 or multiplier not in (0.25, 0.5):
        raise ValueError('Positive coercivity and a registered dyadic multiplier required')
    s = math.ldexp(multiplier, math.floor(math.log2(m) / 2))
    if not 0 < s*s <= m:
        raise ArithmeticError('Dyadic initializer outside the proven interval')
    return s


def train_factor(M, m, target, multiplier=0.5, seed=17):
    M = np.asarray(M, dtype=np.float64)
    if M.ndim != 2 or M.shape[0] != M.shape[1] or not np.isfinite(M).all():
        raise ValueError('Finite square target required')
    if not np.allclose(M, M.T, atol=1e-13, rtol=1e-13) or m <= 0 or target <= 0:
        raise ValueError('Symmetric positive target and positive tolerance required')
    M = (M + M.T) / 2
    d = len(M)
    L = float(up(np.max(np.sum(np.abs(M), axis=1))))
    if not math.isfinite(L) or L < m:
        raise ValueError('Inconsistent spectral bounds')
    s = dyadic_scale(m, multiplier)
    c = s*s
    rng = np.random.default_rng(seed)
    O = np.eye(d)[rng.permutation(d)] * rng.choice([-1., 1.], size=(d, 1))
    W = s*O
    alpha = 1/(4*L)
    e0 = float(np.linalg.norm(W.T @ W - M, 'fro'))
    cap = budget(e0, target/2, alpha, c)
    # The factor loop has a prespecified cap. No unrecorded rescue or tolerance
    # relaxation follows a failure. Verifying the rounded result is mandatory.
    checks = 0
    iterations = 0
    residual = math.inf
    for j in range(cap+1):
        if j % 8 == 0 or j == cap:
            residual = float((Ball.exact(W).T @ Ball.exact(W) - Ball.exact(M)).norm_f())
            checks += 1
            if residual <= target:
                iterations = j
                break
        if j < cap:
            W = W - alpha * (W @ (W.T @ W - M))
            if not np.isfinite(W).all():
                raise ArithmeticError('Nonfinite trained factor')
        iterations = j
    return W, {'iterations': iterations, 'ideal_iteration_cap': cap,
               'gram_checks': checks, 'initial_residual': e0, 'target': target,
               'outward_stored_target_residual': residual,
               'training_threshold_met': bool(residual <= target),
               'm': m, 'L': L, 'c': c, 'alpha': alpha,
               'outside_previous_rank_basin': bool(e0 > m/2)}


def backward_nbo(model, tolerance=1e-4, multiplier=0.5, seed=17):
    A, B, Q, R, Qf = [model[k] for k in ('A', 'B', 'Q', 'R', 'Qf')]
    beta = model['beta']
    T, d = A.shape[:2]
    if tolerance <= 0:
        raise ValueError('Positive policy tolerance required')
    zero = np.zeros((T, d, d))
    ps, cs = value_balls(A, B, Q, R, Qf, model['Sigma'], beta, zero)
    reference = float(up(model['initial_radius_sq'] * ps[0].norm_inf() + cs[0].upper()))
    if not reference > 0 or not math.isfinite(reference):
        raise ArithmeticError('Finite positive reference-policy bound required')
    eta_target = tolerance/(2*reference)
    K = zero.copy()
    P = np.empty((T+1, d, d)); P[-1] = Qf.copy()
    factors = np.zeros((T, d, d))
    dates = []
    for t in range(T-1, -1, -1):
        if t == T-1:
            phat = Qf.copy()
        else:
            q = float(np.min(np.diag(Q[t])))
            r = float(np.min(np.diag(R[t])))
            m = d * float(np.min(np.diag(Q[t+1])))
            target_matrix = d * P[t+1]
            L = float(up(np.max(np.sum(np.abs(target_matrix), axis=1))))
            # Frobenius norms are conservative spectral bounds; no SVD or
            # optimal-gain construction enters the allocation or initializer.
            a = float(np.linalg.norm(A[t], 'fro'))
            b = float(np.linalg.norm(B[t], 'fro'))
            chi = beta*b*a*(1+beta*b*b*L/(d*r))
            target = d*math.sqrt(eta_target*q*r)/(2*chi) if chi else 1.
            W, record = train_factor(target_matrix, m, target, multiplier, seed+t)
            factors[t+1] = W
            phat = W.T @ W / d
            record.update(date=t, continuation_date=t+1, coefficient_target=target/d)
            dates.append(record)
        H = R[t] + beta * B[t].T @ phat @ B[t]
        rhs = beta * B[t].T @ phat @ A[t]
        K[t] = np.linalg.solve(H, rhs)
        F = A[t] - B[t] @ K[t]
        P[t] = Q[t] + K[t].T @ R[t] @ K[t] + beta * F.T @ P[t+1] @ F
        P[t] = (P[t] + P[t].T)/2
    counters = {'hidden_updates': sum(x['iterations'] for x in dates),
                'ideal_hidden_update_cap': sum(x['ideal_iteration_cap'] for x in dates),
                'gram_checks': sum(x['gram_checks'] for x in dates),
                'actor_solves': T, 'own_policy_matrix_updates': T,
                'reference_policy_matrix_updates': T,
                'training_thresholds_met': all(x['training_threshold_met'] for x in dates),
                'reference_value_upper': reference, 'eta_allocation': eta_target,
                'dates': dates, 'simulation_transitions': 0}
    return K, factors, P, counters
