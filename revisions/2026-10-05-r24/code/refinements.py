"""R24 refinements of the inherited own-policy certificate.

A midpoint linear solve proposes V; only its outward-enclosed residual is
trusted. No optimal policy or observed reward enters the certificate.
Learning-budget helpers describe the real-arithmetic theorem; they are not
silently substituted for a floating-point training or outer-loop guarantee.
"""
from __future__ import annotations
import math
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / 'revisions/2026-10-05-r23/code'
if str(OLD) not in sys.path:
    sys.path.insert(0, str(OLD))
from policy_certificate import Ball, up, down, positive_sum, certify, value_balls


def learning_budget(m: float, L: float, error: float, target: float,
                    alpha: float | None = None) -> dict:
    """Evaluate a sufficient real-arithmetic inner-loop budget.

    Inputs m and L must already be valid spectral bounds. This calculation
    is not a spectral verifier. Returned budgets are numerical evaluations
    of the displayed formula, not rounded interval certificates.
    """
    vals = (m, L, error, target)
    if not all(math.isfinite(v) for v in vals):
        raise ValueError('learning inputs must be finite')
    if m <= 0 or L < m or error < 0 or target <= 0:
        raise ValueError('invalid spectral bounds or residual target')
    if error > m / 2:
        raise ValueError('rank basin is not established')
    cap = 1 / (8 * (L + m))
    alpha = cap if alpha is None else float(alpha)
    if not math.isfinite(alpha) or not 0 < alpha <= cap:
        raise ValueError('step exceeds the sufficient theorem bound')
    rate_log = math.log1p(-alpha * m)
    if error <= target:
        steps = 0
    else:
        steps = math.ceil(2 * math.log(error / target) / -rate_log)
    return {'steps': steps, 'alpha': alpha,
            'residual_bound': error * math.exp(steps * rate_log / 2),
            'rank_lower': math.sqrt(m / 2),
            'scope': 'real-arithmetic inner loop; spectral premises supplied'}


def propagated_training_bound(m: float, L: float, error: float,
                              alpha: float, perturbations: list[float]) -> dict:
    """Outward scalar enclosure for a *supplied* per-step perturbation bound.

    Each perturbation bounds the entire implemented step minus the exact
    gradient step at the same current W. This routine does not infer those
    bounds from a training log or assume they vanish for floating point.
    """
    learning_budget(m, L, error, max(error, 1e-300), alpha)
    q = float(up(math.sqrt(float(up(1.0 - float(down(alpha * m)))))))
    s = float(up(math.sqrt(float(up(L + float(up(m / 2)))))))
    b = float(error)
    history = [b]
    for omega in perturbations:
        if not math.isfinite(omega) or omega < 0:
            raise ValueError('invalid implementation perturbation')
        a = float(up(q * b))
        cross = float(up(float(up(2.0 * s)) * omega))
        square = float(up(omega * omega))
        b = float(up(float(up(a + cross)) + square))
        history.append(b)
        if b > m / 2:
            return {'basin_verified': False, 'history': history,
                    'failure': 'propagated residual leaves sufficient rank basin'}
    return {'basin_verified': True, 'history': history}


def energy_bound(H: Ball, D: Ball, qdiag: np.ndarray, r_lower: float,
                 proposal: np.ndarray | None = None) -> dict:
    """Bound lambda_max(Q^-1/2 D' H^-1 D Q^-1/2).

    H must enclose a symmetric matrix known to satisfy H >= r_lower I.
    Q is exactly the positive diagonal qdiag. Model-level validation and
    these structural premises are supplied by certify_refined below.
    """
    qdiag = np.asarray(qdiag, dtype=np.float64)
    d = len(qdiag)
    if H.c.shape != (d, d) or D.c.shape != (d, d):
        raise ValueError('energy matrices must be square and conformable')
    if (not math.isfinite(r_lower) or r_lower <= 0 or
            not np.all(np.isfinite(qdiag)) or np.any(qdiag <= 0)):
        raise ValueError('strict positive coercivity bounds required')
    if proposal is None:
        proposal = np.linalg.solve(H.c, D.c)
    proposal = np.asarray(proposal, dtype=np.float64)
    if proposal.shape != D.c.shape or not np.all(np.isfinite(proposal)):
        raise ValueError('invalid solve proposal')
    v = Ball.exact(proposal)
    residual = D - H @ v
    remainder = float(up(residual.norm_f_sq() / r_lower))
    s = v.T @ H @ v + v.T @ residual + residual.T @ v
    s = s + Ball.exact(np.eye(d) * remainder)
    row_upper = positive_sum(s.abs_upper(), axis=1)
    eta = float(np.max(up(row_upper / qdiag)))
    if eta < 0 or not math.isfinite(eta):
        raise ArithmeticError('nonfinite residual-energy enclosure')
    return {'eta': eta, 'solve_residual_frobenius_upper': residual.norm_f(),
            'residual_remainder_upper': remainder,
            'method': 'outward residual energy and diagonal-Q row sums'}


def certify_refined(model: dict, gains: np.ndarray,
                    execution_error: float = 1e-12) -> dict:
    """A deterministic refinement available symmetrically to every method."""
    original = certify(model, gains, execution_error)
    P, _ = value_balls(*[model[k] for k in
                        ('A', 'B', 'Q', 'R', 'Qf', 'Sigma', 'beta')], gains)
    beta = model['beta']
    date_records = []
    chosen = []
    for t, old_eta in enumerate(original['local_relative_bounds']):
        a, b, r, k = [Ball.exact(v) for v in
                     (model['A'][t], model['B'][t], model['R'][t], gains[t])]
        H = r + (b.T @ P[t + 1] @ b).scale(beta)
        D = H @ k - (b.T @ P[t + 1] @ a).scale(beta)
        try:
            rec = energy_bound(H, D, np.diag(model['Q'][t]),
                               float(np.min(np.diag(model['R'][t]))))
            eta = min(old_eta, rec['eta'])
            date_records.append({'date': t, 'available': True,
                                 'original_eta': old_eta, **rec})
        except (np.linalg.LinAlgError, ArithmeticError, ValueError) as exc:
            eta = old_eta
            date_records.append({'date': t, 'available': False,
                                 'original_eta': old_eta,
                                 'reason': type(exc).__name__ + ': ' + str(exc)})
        chosen.append(eta)
    eta = max(chosen)
    ratio = float(up(eta / float(down(1.0 + eta))))
    ideal = float(up(ratio * original['policy_value_upper']))
    combined = float(up(ideal + original['implementation_gap_upper']))
    # Taking the minimum of two valid deterministic bounds is itself valid.
    final = min(original['policy_gap_upper'], combined)
    return {'policy_gap_upper': final, 'energy_eta_upper': eta,
            'energy_ideal_gap_upper': ideal,
            'original': original, 'date_records': date_records,
            'available_dates': sum(r['available'] for r in date_records),
            'selected_date_bounds': chosen,
            'scope': 'same stored policy, unrestricted adapted comparison, '
                     'same implementation allowance; no new fitting clock'}
