"""Recentered, normwise own-policy verification for recursive Gaussian costs.

Nominal evaluation is a proposal, never a certificate. Each of its Bellman
residuals is enclosed using the inherited outward matrix-ball arithmetic.
A scalar spectral-norm tube propagates evaluation error without repeatedly
feeding a componentwise interval box through the nonlinear matrix inverse.
No optimal policy or optimal-value recursion is used by this module.
"""
from pathlib import Path
import math
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'revisions/2026-10-06-r27/code'))
from entropic_certificate import (
    Ball, add, mul, div, down, norm2, inverse, margin, validate,
    nominal_transform,
)


def nominal_values(model: dict, gains: np.ndarray, theta: float) -> np.ndarray:
    """Propose the coefficients of the stored policy's own value."""
    validate(model, gains, theta)
    T, d = gains.shape[:2]
    out = np.empty((T + 1, d, d))
    out[T] = model['Qf']
    for t in range(T - 1, -1, -1):
        A, B, Q, R = (model[n][t] for n in ('A', 'B', 'Q', 'R'))
        F = A - B @ gains[t]
        psi = nominal_transform(out[t + 1], model['Sigma'], theta)
        value = Q + gains[t].T @ R @ gains[t] + model['beta'] * F.T @ psi @ F
        out[t] = (value + value.T) / 2
        if not np.isfinite(out[t]).all():
            raise ArithmeticError('Nonfinite nominal own-policy proposal')
    return out


def evaluation_tube(model: dict, gains: np.ndarray, theta: float,
                    centers: np.ndarray | None = None) -> tuple:
    """Enclose all own-policy coefficients around arbitrary symmetric centers.

    Returns (centers, spectral radii, diagnostics). Supplied centers may be
    inaccurate: their outward Bellman residuals, not their construction,
    determine acceptance. The terminal center must equal the terminal cost.
    """
    validate(model, gains, theta)
    T, d = gains.shape[:2]
    beta = float(model['beta'])
    C = nominal_values(model, gains, theta) if centers is None else np.array(centers, dtype=float, copy=True)
    if C.shape != (T + 1, d, d) or not np.isfinite(C).all():
        raise ValueError('Invalid own-policy centers')
    if not np.array_equal(C, C.swapaxes(1, 2)) or not np.array_equal(C[T], model['Qf']):
        raise ValueError('Symmetric centers and exact terminal coefficient required')
    sigma = norm2(Ball.exact(model['Sigma']))
    S = Ball.exact(model['Sigma'])
    radii = np.zeros(T + 1)
    diagnostics = [None] * T
    for t in range(T - 1, -1, -1):
        a, b, q, r = (Ball.exact(model[n][t]) for n in ('A', 'B', 'Q', 'R'))
        k = Ball.exact(gains[t])
        f = a - b @ k
        fn, bn = norm2(f), norm2(b)
        center = Ball.exact(C[t + 1])
        p_upper = add(norm2(center), float(radii[t + 1]))
        gamma = margin(theta, sigma, p_upper)
        if theta:
            psi = center @ inverse(Ball.exact(np.eye(d)) - (S @ center).scale(2 * theta))
            psi = (psi + psi.T).scale(.5)
        else:
            psi = center
        propagated = div(float(radii[t + 1]), float(down(gamma * gamma)))
        residual = norm2(q + k.T @ r @ k + (f.T @ psi @ f).scale(beta) - Ball.exact(C[t]))
        radii[t] = add(residual, mul(beta, fn, fn, propagated))
        # D = R K - beta B' Psi(P) F; no subtraction of two large Hessian terms.
        defect = add((r @ k - (b.T @ psi @ f).scale(beta)).norm_f(),
                     mul(beta, bn, f.norm_f(), propagated))
        diagnostics[t] = dict(
            date=t, d=defect, f=fn, b=bn, k=norm2(k),
            r=float(np.min(np.diag(model['R'][t]))), rnorm=norm2(r),
            p=p_upper, evaluation_radius=float(radii[t]),
            evaluation_residual=residual, evaluation_domain_margin=gamma,
        )
    return C, radii, diagnostics


def certify(model: dict, gains: np.ndarray, theta: float,
            execution_error: float = 1e-12) -> dict:
    """Full adapted-policy certificate, using recentered own-policy enclosures."""
    if not math.isfinite(execution_error) or execution_error < 0:
        raise ValueError('Invalid execution-error contract')
    _, radii, diagnostics = evaluation_tube(model, gains, theta)
    T, d = gains.shape[:2]
    beta = float(model['beta'])
    sigma = norm2(Ball.exact(model['Sigma']))
    trace = Ball.exact(model['Sigma']).trace().upper()
    delta = kappa = delta_e = kappa_e = 0.
    dates = []
    for t in range(T - 1, -1, -1):
        rec = diagnostics[t]
        p, f, b, r, dn = (rec[n] for n in ('p', 'f', 'b', 'r', 'd'))
        if t + 1 < T and delta > float(np.min(np.diag(model['Q'][t + 1]))):
            raise ArithmeticError('Lower quadratic envelope lost positivity')
        gamma = margin(theta, sigma, p)
        drift = div(delta, float(down(gamma * gamma)))
        lower_f = add(f, mul(div(b, r), add(dn, mul(beta, b, f, drift))))
        new_delta = add(div(mul(dn, dn), r), mul(beta, lower_f, lower_f, drift))
        new_kappa = mul(beta, add(kappa, div(mul(delta, trace), gamma)))
        gamma_e = margin(theta, sigma, add(p, delta_e))
        psi_upper = div(add(p, delta_e), gamma_e)
        act = add(mul(2., execution_error, rec['k'], rec['rnorm']),
                  mul(execution_error, execution_error, rec['rnorm']),
                  mul(beta, psi_upper,
                      add(mul(2., execution_error, f, b),
                          mul(execution_error, execution_error, b, b))))
        new_delta_e = add(mul(beta, f, f, div(delta_e, float(down(gamma_e * gamma_e)))), act)
        new_kappa_e = mul(beta, add(kappa_e, div(mul(delta_e, trace), gamma_e)))
        delta, kappa, delta_e, kappa_e = new_delta, new_kappa, new_delta_e, new_kappa_e
        dates.append(dict(rec, domain_margin=gamma, implementation_domain_margin=gamma_e,
                          coefficient_allowance=delta, constant_allowance=kappa,
                          implementation_coefficient=delta_e, implementation_constant=kappa_e))
    nominal = add(mul(delta, model['initial_radius_sq']), kappa)
    implementation = add(mul(delta_e, model['initial_radius_sq']), kappa_e)
    return dict(policy_gap_upper=add(nominal, implementation),
                nominal_policy_gap_upper=nominal, implementation_gap_upper=implementation,
                minimum_domain_margin=min(x['domain_margin'] for x in dates),
                minimum_implementation_domain_margin=min(x['implementation_domain_margin'] for x in dates),
                maximum_evaluation_radius=float(np.max(radii)),
                class_approximation_allowance=0., value_transfer_allowance=0.,
                coverage='All real states and vector actions; all adapted finite-recursive-cost comparison policies in the declared discrete model',
                verifier='R28 outward Bellman residual with spectral-norm evaluation tube',
                execution_error_contract=execution_error, dates=dates)
