"""Exact arithmetic for the mixed-norm policy budget in the R34 theorem.

The matrix checker proves assertions about its supplied rational matrices.
A supplied spectral evaluation radius is a premise: its economic provenance
must be established by an own-policy evaluator. The demonstration additionally
checks that radius against an exactly computed own-policy target. No BLAS
roundoff assertion, empirical reliability interval, or timing dominance is
inferred from these checks.
"""
from __future__ import annotations
import importlib.util
from fractions import Fraction as F
from pathlib import Path
from math import isqrt
import sys

_PATH = Path(__file__).resolve().parents[2]/'2026-10-06-r33/code/warm_start.py'
_SPEC = importlib.util.spec_from_file_location('nbo_r33_exact_warm', _PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError('The preserved R33 exact warm-start module is required')
warm = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(warm)
matrix, mm, tr, add, eye = warm.matrix, warm.mm, warm.transpose, warm.add, warm.eye
norm2, sqrt_up, psd, rational = warm.norm2, warm.sqrt_up, warm.psd, warm.rational


def scale(a, s):
    s = rational(s)
    return [[s*x for x in row] for row in a]


def inverse(a):
    """Exact Gauss--Jordan inverse with pivoting and a checked product."""
    a = matrix(a)
    n = len(a)
    if len(a[0]) != n:
        raise ValueError('Square inverse required')
    b = [row[:] + unit for row, unit in zip(a, eye(n))]
    for j in range(n):
        pivot = next((i for i in range(j, n) if b[i][j]), None)
        if pivot is None:
            raise ValueError('Singular matrix')
        b[j], b[pivot] = b[pivot], b[j]
        p = b[j][j]
        b[j] = [v/p for v in b[j]]
        for i in range(n):
            if i == j:
                continue
            c = b[i][j]
            b[i] = [v-c*w for v, w in zip(b[i], b[j])]
    ans = [row[n:] for row in b]
    if mm(a, ans) != eye(n):
        raise ArithmeticError('Exact inverse identity failed')
    return ans


def op_upper(a):
    """sqrt(||A||_1 ||A||_infinity), rounded upward rationally."""
    a = matrix(a)
    inf_norm = max(sum(abs(x) for x in row) for row in a)
    one_norm = max(sum(abs(x) for x in col) for col in tr(a))
    return sqrt_up(inf_norm*one_norm)


def sqrt_down(x, bits=96):
    x = rational(x)
    if x < 0:
        raise ValueError('Nonnegative radicand required')
    s = 1 << bits
    return F(isqrt(x.numerator*s*s//x.denominator), s)


def transform(p, covariance, theta):
    p, covariance = matrix(p), matrix(covariance)
    theta = rational(theta)
    if theta < 0:
        raise ValueError('Nonnegative risk parameter required')
    psd(p); psd(covariance)
    if 2*theta*op_upper(covariance)*op_upper(p) >= 1:
        raise ValueError('Gaussian norm-domain margin is not positive')
    ans = mm(p, inverse(add(eye(len(p)), scale(mm(covariance, p), 2*theta), -1)))
    if ans != tr(ans):
        raise ArithmeticError('Gaussian coefficient lost exact symmetry')
    psd(ans)
    return ans


def target_radius(center, truth, radius):
    """Check an asserted spectral radius against an available exact target."""
    center, truth = matrix(center), matrix(truth)
    radius = rational(radius)
    if radius < 0:
        raise ValueError('Nonnegative target radius required')
    error = add(center, truth, -1)
    psd(add(eye(len(error), radius), error, -1))
    psd(add(eye(len(error), radius), error))


def allocate(stages, terminal, covariance, beta, theta, eta, epsilon, initial_radius):
    """Build the robust primitive budget, checking matrix coercivity exactly.

    Each stage supplies A, B, Q, R, reference feedback L, and strictly
    positive rational lower bounds q and r. The reference is a feasibility
    witness and is not an optimal-control solution or a critic target.
    """
    beta, theta, eta, epsilon, initial_radius = map(rational,
        (beta, theta, eta, epsilon, initial_radius))
    if not 0 < beta <= 1 or theta < 0 or eta <= 0 or epsilon <= 0 or initial_radius < 0:
        raise ValueError('Invalid discount, risk, slack, accuracy, or initial radius')
    if not stages:
        raise ValueError('At least one decision date required')
    terminal, covariance = matrix(terminal), matrix(covariance)
    psd(terminal); psd(covariance)
    d = len(terminal)
    if len(covariance) != d:
        raise ValueError('State and covariance dimensions disagree')
    rows = []
    for st in stages:
        x = {key: matrix(st[key]) for key in ('A', 'B', 'Q', 'R', 'L')}
        q, r = rational(st['q']), rational(st['r'])
        if q <= 0 or r <= 0:
            raise ValueError('Strictly positive coercivity required')
        k = len(x['R'])
        if (len(x['A']) != d or len(x['A'][0]) != d or
            len(x['B']) != d or len(x['B'][0]) != k or
            len(x['Q']) != d or len(x['L']) != k or len(x['L'][0]) != d):
            raise ValueError('Incompatible state or action dimensions')
        psd(add(x['Q'], eye(d, q), -1)); psd(add(x['R'], eye(k, r), -1))
        rows.append(dict(x, q=q, r=r))
    T = len(rows); qstar = min(x['q'] for x in rows)
    sigma = op_upper(covariance)
    tau = sum(covariance[i][i] for i in range(d))
    pbar = [F() for _ in range(T)] + [op_upper(terminal)]
    for t in range(T-1, -1, -1):
        x = rows[t]
        gamma = 1-2*theta*sigma*pbar[t+1]
        if gamma <= 0:
            raise ValueError('Primitive moment-domain failure')
        ref_f = add(x['A'], mm(x['B'], x['L']), -1)
        ref_q = add(scale(x['Q'], 1+eta), mm(mm(tr(x['L']), x['R']), x['L']))
        pbar[t] = op_upper(ref_q) + beta*op_upper(ref_f)**2*pbar[t+1]/gamma
        u, b, anorm = pbar[t+1]/gamma, op_upper(x['B']), op_upper(x['A'])
        v = sqrt_up(eta*x['r']*x['q'])
        f = anorm*(1+beta*b*b*(u+qstar)/x['r']) + b*v/x['r']
        g = f+b/x['r']*(v+beta*b*f*qstar/(gamma*gamma))
        x.update(gamma=gamma, u=u, b=b, f=f, g=g, v=v)
    lam = [F() for _ in range(T+1)]; mu = lam.copy()
    for t in range(T-1, -1, -1):
        x = rows[t]
        lam[t] = x['q']+beta*x['g']**2*lam[t+1]/x['gamma']**2
        mu[t] = beta*(mu[t+1]+tau*lam[t+1]/x['gamma'])
    weight = initial_radius*lam[0]+mu[0]
    choices = [eta] + [qstar/l for l in lam[1:T] if l]
    if weight:
        choices.append(epsilon/weight)
    s = min(choices)
    return dict(d=d, T=T, beta=beta, theta=theta, eta=eta, epsilon=epsilon,
        initial_radius=initial_radius, qstar=qstar, sigma=sigma, tau=tau,
        pbar=pbar, stages=rows, lam=lam, mu=mu, s=s,
        gap_bound=s*weight, covariance=covariance, terminal=terminal)


def local_gate(plan, t, gram, center, actor, evaluation_radius=0):
    """Check the two acceptance inequalities for one returned rational actor.

    The center must evaluate the finalized future. That semantic and its
    supplied spectral radius must be checked by the caller/evaluator.
    """
    x = plan['stages'][t]; d = plan['d']; beta = plan['beta']
    gram, center, actor = matrix(gram), matrix(center), matrix(actor)
    evaluation_radius = rational(evaluation_radius)
    if evaluation_radius < 0:
        raise ValueError('Negative evaluation radius')
    psd(gram)
    fitted = scale(gram, F(1, d))
    closed = add(x['A'], mm(x['B'], actor), -1)
    z = add(mm(x['R'], actor), scale(mm(mm(tr(x['B']), fitted), closed), beta), -1)
    a = sqrt_up(norm2(add(gram, center, -1)))
    z_upper = sqrt_up(norm2(z))
    if a+evaluation_radius > d*plan['qstar']:
        raise ValueError('Candidate magnitude allowance exceeded')
    upper = z_upper+beta*x['b']*x['f']/d*(a+sqrt_up(F(d))*evaluation_radius)
    if upper*upper > plan['s']*x['r']*x['q']:
        raise ValueError('Local policy-loss allowance exceeded')
    # These checks also catch an inconsistent passed-in budget.
    psd(add(eye(d, x['f']**2), mm(tr(closed), closed), -1))
    return dict(gram_error_upper=a, actor_error_upper=z_upper,
        target_radius=evaluation_radius, exact_residual_upper=upper,
        local_loss_upper=upper*upper/x['r'], closed=closed)


def greedy(stage, coefficient, beta):
    beta = rational(beta)
    S = matrix(coefficient); B, R, A = stage['B'], stage['R'], stage['A']
    return mm(inverse(add(R, scale(mm(mm(tr(B), S), B), beta))),
              scale(mm(mm(tr(B), S), A), beta))


def own_coefficient(stage, actor, continuation, beta):
    closed = add(stage['A'], mm(stage['B'], actor), -1)
    p = add(stage['Q'], mm(mm(tr(actor), stage['R']), actor))
    return add(p, scale(mm(mm(tr(closed), continuation), closed), rational(beta)))
