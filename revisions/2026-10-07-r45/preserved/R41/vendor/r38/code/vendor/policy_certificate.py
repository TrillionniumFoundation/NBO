"""Outward matrix-ball arithmetic and a coercive full-policy certificate.

All input doubles are the exact binary coefficients of the declared economy.
Only classical float64 BLAS products are used. Products are enclosed with a
2*k-operation gamma bound; subnormal absolute errors are dominated by 2*k*tiny.
Overflow, nonfinite inputs and invalid radii fail closed.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np

U = np.finfo(np.float64).eps / 2
TINY = np.finfo(np.float64).tiny


def up(x):
    y = np.nextafter(np.asarray(x, dtype=np.float64), np.inf)
    if not np.all(np.isfinite(y)):
        raise ArithmeticError('nonfinite upper enclosure')
    return y


def down(x):
    y = np.nextafter(np.asarray(x, dtype=np.float64), -np.inf)
    if not np.all(np.isfinite(y)):
        raise ArithmeticError('nonfinite lower enclosure')
    return y


def gamma(n: int) -> float:
    if n < 1 or n * U >= 0.01:
        raise ValueError('invalid rounding-error dimension')
    return float(up((n * U) / float(down(1 - n * U))))


def positive_sum(x, axis=None):
    a = np.asarray(x, dtype=np.float64)
    if np.any(a < 0) or not np.all(np.isfinite(a)):
        raise ValueError('positive_sum needs finite nonnegative entries')
    n = a.size if axis is None else a.shape[axis]
    return up(up(np.sum(a, axis=axis) / float(down(1 - gamma(max(n, 1))))) + n * TINY)


def positive_dot(a, b):
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    if np.any(a < 0) or np.any(b < 0):
        raise ValueError('positive_dot needs nonnegative entries')
    k = a.shape[-1]
    return up(up((a @ b) / float(down(1 - gamma(2 * k)))) + (2 * k) * TINY)


@dataclass(frozen=True)
class Ball:
    c: np.ndarray
    r: np.ndarray

    def __post_init__(self):
        if self.c.shape != self.r.shape or np.any(self.r < 0):
            raise ValueError('invalid ball shape or radius')
        if not np.all(np.isfinite(self.c)) or not np.all(np.isfinite(self.r)):
            raise ArithmeticError('nonfinite ball')

    @classmethod
    def exact(cls, x):
        a = np.asarray(x, dtype=np.float64).copy()
        return cls(a, np.zeros_like(a))

    @property
    def T(self):
        return Ball(self.c.T, self.r.T)

    def __add__(self, other):
        if not isinstance(other, Ball):
            other = Ball.exact(other)
        c = self.c + other.c
        mag = up(np.abs(self.c) + np.abs(other.c))
        er = up(up(U * mag) + TINY)
        return Ball(c, up(up(self.r + other.r) + er))

    def __neg__(self):
        return Ball(-self.c, self.r)

    def __sub__(self, other):
        return self + (-other if isinstance(other, Ball) else Ball.exact(-np.asarray(other)))

    def scale(self, a: float):
        a = float(a)
        if not math.isfinite(a):
            raise ValueError('nonfinite scale')
        c = self.c * a
        er = up(up(U * up(abs(a) * np.abs(self.c))) + TINY)
        return Ball(c, up(up(abs(a) * self.r) + er))

    def __matmul__(self, other):
        if not isinstance(other, Ball):
            other = Ball.exact(other)
        k = self.c.shape[-1]
        c = self.c @ other.c
        mag = positive_dot(np.abs(self.c), np.abs(other.c))
        rad = up(up(gamma(2 * k) * mag) + (2 * k) * TINY)
        for term in (positive_dot(np.abs(self.c), other.r),
                     positive_dot(self.r, np.abs(other.c)),
                     positive_dot(self.r, other.r)):
            rad = up(rad + term)
        return Ball(c, rad)

    def abs_upper(self):
        return up(np.abs(self.c) + self.r)

    def norm_inf(self) -> float:
        return float(np.max(positive_sum(self.abs_upper(), axis=1)))

    def norm_f_sq(self) -> float:
        a = self.abs_upper()
        return float(positive_sum(up(a * a)))

    def norm_f(self) -> float:
        return float(up(math.sqrt(self.norm_f_sq())))

    def trace(self):
        c = float(np.trace(self.c))
        diag_abs = np.abs(np.diag(self.c))
        er = float(up(gamma(max(len(diag_abs), 1)) * positive_sum(diag_abs)))
        r = float(up(up(positive_sum(np.diag(self.r)) + er) + len(diag_abs) * TINY))
        return Ball(np.asarray(c), np.asarray(r))

    def upper(self) -> float:
        return float(up(self.c + self.r))

    def lower(self) -> float:
        return float(down(self.c - self.r))


def value_balls(A, B, Q, R, Qf, Sigma, beta, gains, execution_error=0.0):
    """Quadratic upper envelope, exact for the stored policy when error=0.

    When execution_error>0, the extra action at every state/date may be any
    adapted e with ||e||_2 <= execution_error*||x||_2. No overflow-free physical
    executor on arbitrary real inputs is silently assumed.
    """
    T, d = len(gains), len(Qf)
    if execution_error < 0 or not 0 < beta <= 1:
        raise ValueError('invalid beta or implementation allowance')
    P = [None] * (T + 1)
    c = [None] * (T + 1)
    P[T], c[T] = Ball.exact(Qf), Ball.exact(0.0)
    S = Ball.exact(Sigma)
    for t in range(T - 1, -1, -1):
        a, b, q, r, k = [Ball.exact(v) for v in (A[t], B[t], Q[t], R[t], gains[t])]
        f = a - b @ k
        value = q + k.T @ r @ k + (f.T @ P[t+1] @ f).scale(beta)
        if execution_error:
            e = execution_error
            rnorm, bnorm = r.norm_inf(), b.norm_f()
            pnorm = P[t+1].norm_inf()
            # Every norm and positive arithmetic operation is outward bounded.
            h1 = float(up(2 * up((r @ k).norm_f() * e)))
            h2 = float(up(rnorm * up(e * e)))
            h3 = float(up(2 * up(up((P[t+1] @ f).norm_f() * bnorm) * e)))
            h4 = float(up(up(pnorm * up(bnorm * bnorm)) * up(e * e)))
            h = float(up(up(h1 + h2) + up(beta * up(h3 + h4))))
            value = value + Ball.exact(np.eye(d) * h)
        P[t] = value
        c[t] = (c[t+1] + (P[t+1] @ S).trace()).scale(beta)
    return P, c


def certify(model: dict, gains: np.ndarray, execution_error=1e-12) -> dict:
    """No optimal-policy coefficients or grid observations enter this verifier."""
    A, B, Q, R, Qf, S, beta = [model[k] for k in ('A','B','Q','R','Qf','Sigma','beta')]
    T, d = gains.shape[:2]
    if gains.shape != (T, d, d) or np.asarray(A).shape != gains.shape:
        raise ValueError('policy/model shape mismatch')
    if any(not np.array_equal(m, np.diag(np.diag(m))) for m in list(Q)+list(R)):
        raise ValueError('this implementation requires diagonal positive stage costs')
    if np.min(Q) < 0 or np.min(R) < 0 or np.min(np.diagonal(Q,axis1=1,axis2=2)) <= 0 or np.min(np.diagonal(R,axis1=1,axis2=2)) <= 0:
        raise ValueError('stage costs must be strictly positive on the diagonal')
    if not np.array_equal(Qf,np.diag(np.diag(Qf))) or np.min(np.diag(Qf)) < 0:
        raise ValueError('terminal cost must be nonnegative diagonal')
    if not np.array_equal(S,S.T):
        raise ValueError('covariance must be exactly symmetric')
    off=np.abs(S).copy();np.fill_diagonal(off,0)
    if np.any(np.diag(S) < positive_sum(off,axis=1)):
        raise ValueError('covariance diagonal-dominance certificate unavailable')
    if not 0 < beta <= 1 or model['initial_radius_sq'] <= 0:
        raise ValueError('invalid discount or initial domain')
    P, c = value_balls(A,B,Q,R,Qf,S,beta,gains)
    eta, date_bounds = 0.0, []
    for t in range(T):
        a,b,r,k = [Ball.exact(v) for v in (A[t],B[t],R[t],gains[t])]
        H = r + (b.T @ P[t+1] @ b).scale(beta)
        D = H @ k - (b.T @ P[t+1] @ a).scale(beta)
        qmin, rmin = float(np.min(np.diag(Q[t]))), float(np.min(np.diag(R[t])))
        denom = float(down(qmin*rmin))
        if denom <= 0:
            raise ArithmeticError('positive coercivity denominator unavailable')
        et = float(up(D.norm_f_sq()/denom))
        date_bounds.append(et)
        eta = max(eta,et)
    radius_sq = float(model['initial_radius_sq'])
    value_upper = float(up(up(radius_sq * P[0].norm_inf()) + c[0].upper()))
    rho = float(up(eta/float(down(1.0+eta))))
    ideal_gap = float(up(rho*value_upper))
    impl = 0.0
    if execution_error:
        Pe,ce=value_balls(A,B,Q,R,Qf,S,beta,gains,execution_error)
        diff=Pe[0]-P[0]
        impl = max(0.0,float(up(up(radius_sq*diff.norm_inf())+(ce[0]-c[0]).upper())))
    return {'eta':eta,'local_relative_bounds':date_bounds,
            'policy_value_upper':value_upper,'ideal_gap_upper':ideal_gap,
            'implementation_gap_upper':impl,'policy_gap_upper':float(up(ideal_gap+impl)),
            'initial_radius_sq':radius_sq,'domain':'all R^d; uniform reported bound on declared initial ball',
            'comparison':'all adapted finite-cost policies; all real vector actions',
            'class_gap':0.0,'value_transfer_gap':0.0,
            'execution_error_budget':execution_error,
            'arithmetic':'outward float64 matrix balls; gamma_(2k), underflow allowance, fail-closed'}
