"""Explicit finite-state policy accounts and the sufficient-cost allocation.

These routines are executable checks of the stated finite-horizon identities.
They do not infer state coverage from an empirical catalogue.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Sequence
import numpy as np

@dataclass(frozen=True)
class Allocation:
    allowances: tuple[float, ...]
    counts: tuple[int, ...]
    continuous_cost: float
    integer_cost: float
    slack: float

def allocate(weights: Sequence[float], rates: Sequence[float], costs: Sequence[float],
             fixed_errors: Sequence[float], target: float) -> Allocation:
    """Minimize sum c_t*A_t/e_t^2 for positive weights and feasible target.

Rate and coverage assumptions must be established separately. Counts are
ceilings of sufficient real budgets; no model-family minimum is inferred.
"""
    w,A,c,b=map(lambda x:np.asarray(x,dtype=float),(weights,rates,costs,fixed_errors))
    if w.ndim!=1 or not len(w) or any(x.shape!=w.shape for x in (A,c,b)):
        raise ValueError('nonempty equal-length one-dimensional inputs required')
    if not all(np.all(np.isfinite(x)) for x in (w,A,c,b)) or not math.isfinite(target):
        raise ValueError('finite inputs required')
    if np.any(w<=0) or np.any(A<=0) or np.any(c<=0) or np.any(b<0):
        raise ValueError('weights, rates, costs positive; fixed errors nonnegative')
    E=float(target-np.dot(w,b))
    if E<=0:raise ValueError('target has no positive approximation allowance')
    a=A*c;H=float(np.sum(np.cbrt(a)*np.cbrt(w*w)))
    e=(E/H)*np.cbrt(a/w)
    counts=tuple(math.ceil(float(z)) for z in A/(e*e))
    return Allocation(tuple(map(float,e)),counts,H**3/E**2,
                      math.fsum(float(ci)*ni for ci,ni in zip(c,counts)),E)

def finite_policy_account(rewards, transitions, beta, policy, terminal):
    """Exact-model floating arithmetic account, not an interval certificate.

Shapes: rewards [T,S,A], transitions [T,S,A,S], policy [T,S].
All feasible actions and all states of the provided finite model are used.
"""
    r=np.asarray(rewards,float);P=np.asarray(transitions,float)
    b=np.asarray(beta,float);pi=np.asarray(policy);v=np.asarray(terminal,float)
    if r.ndim!=3:raise ValueError('rewards must have shape [T,S,A]')
    T,S,A=r.shape
    if P.shape!=(T,S,A,S) or b.shape!=(T,) or pi.shape!=(T,S) or v.shape!=(S,):
        raise ValueError('inconsistent model dimensions')
    if not all(np.all(np.isfinite(x)) for x in (r,P,b,v)) or np.any(b<0) or np.any(P<0):
        raise ValueError('finite rewards and nonnegative finite kernels/weights required')
    if not np.allclose(P.sum(-1),1,rtol=0,atol=1e-12):raise ValueError('nonstochastic kernel')
    if not np.issubdtype(pi.dtype,np.integer) or np.any(pi<0) or np.any(pi>=A):
        raise ValueError('policy actions must be feasible integers')
    vp=np.empty((T+1,S));vs=vp.copy();gap=np.zeros((T,S));envelope=np.zeros((T+1,S))
    vp[T]=v;vs[T]=v
    for t in reversed(range(T)):
        qp=r[t]+b[t]*np.einsum('sak,k->sa',P[t],vp[t+1])
        qs=r[t]+b[t]*np.einsum('sak,k->sa',P[t],vs[t+1])
        vp[t]=qp[np.arange(S),pi[t]];vs[t]=qs.max(1)
        gap[t]=qp.max(1)-vp[t]
        envelope[t]=gap[t]+b[t]*np.einsum('sak,k->sa',P[t],envelope[t+1]).max(1)
    weights=np.r_[1.,np.cumprod(b[:-1])]
    return dict(policy_values=vp,optimal_values=vs,local_advantages=gap,
                state_envelope=envelope,weights=weights,
                uniform_bound=float(np.dot(weights,gap.max(1))))
