"""R73 residual-oscillation readout qualification with rational primal/dual checks.

An LP proposes a readout; exact arithmetic, not its solver status, certifies the
achieved uniform residual range and the optimization gap for the fixed labels.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
import time
from typing import Sequence


def dot(a: Sequence[F], b: Sequence[F]) -> F:
    return sum((F(x)*F(y) for x,y in zip(a,b)),F(0))


@dataclass(frozen=True)
class Problem:
    features: tuple[tuple[F,...],...]
    lower: tuple[F,...]
    upper: tuple[F,...]
    lipschitz: tuple[F,...]
    bounds: tuple[F,...]
    radius: F
    bellman_lipschitz: F

    def __post_init__(self) -> None:
        n,k = len(self.lower),len(self.bounds)
        if not n or not k or len(self.upper)!=n or len(self.features)!=n or len(self.lipschitz)!=k:
            raise ValueError('Inconsistent finite qualification arrays')
        if any(len(row)!=k for row in self.features) or any(F(l)>F(u) for l,u in zip(self.lower,self.upper)):
            raise ValueError('Invalid feature row or Bellman interval')
        if min(map(F,self.lipschitz+self.bounds+(self.radius,self.bellman_lipschitz)))<0:
            raise ValueError('Moduli, radius and coefficient limits must be nonnegative')

    @property
    def penalty(self) -> tuple[F,...]:
        return tuple(2*F(self.radius)*F(v) for v in self.lipschitz)

    @property
    def constant(self) -> F:
        return 2*F(self.radius)*F(self.bellman_lipschitz)

    def primal(self, theta: Sequence[F]) -> dict:
        theta = tuple(map(F,theta))
        if len(theta)!=len(self.bounds) or any(abs(v)>F(b) for v,b in zip(theta,self.bounds)):
            raise ValueError('Readout outside the declared coefficient box')
        values = [dot(row,theta) for row in self.features]
        l = min(F(y)-v for y,v in zip(self.lower,values))
        u = max(F(y)-v for y,v in zip(self.upper,values))
        L = dot(self.lipschitz,[abs(v) for v in theta])
        pad = F(self.radius)*(F(self.bellman_lipschitz)+L)
        return {'theta':theta,'nodal_lower':l,'nodal_upper':u,
                'residual_lower':l-pad,'residual_upper':u+pad,
                'lipschitz':L,'objective':u-l+2*pad}

    def dual(self, p: Sequence[F], q: Sequence[F]) -> F:
        p,q = tuple(map(F,p)),tuple(map(F,q))
        if len(p)!=len(self.lower) or len(q)!=len(p) or min(p+q)<0 or sum(p)!=1 or sum(q)!=1:
            raise ValueError('Dual multipliers must be exact probability vectors')
        slopes = [sum((row[k]*(qj-pj) for row,pj,qj in zip(self.features,p,q)),F(0)) for k in range(len(self.bounds))]
        support = sum((F(B)*max(F(0),abs(s)-lam) for B,s,lam in zip(self.bounds,slopes,self.penalty)),F(0))
        return dot(p,self.upper)-dot(q,self.lower)-support+self.constant

    def verify(self, theta: Sequence[F], p: Sequence[F], q: Sequence[F]) -> dict:
        record = self.primal(theta)
        record['dual_lower'] = self.dual(p,q)
        record['optimization_gap'] = record['objective']-record['dual_lower']
        if record['optimization_gap']<0:
            raise AssertionError('Negative exact primal--dual gap')
        return record


def simplex(values: Sequence[float], bits: int = 24) -> tuple[F,...]:
    w = tuple(F(max(0,round(float(v)*2**bits)),2**bits) for v in values)
    if not sum(w):
        return (F(1),)+(F(0),)*(len(w)-1)
    return tuple(v/sum(w) for v in w)


def solve(problem: Problem, bits: int = 24) -> dict:
    """Finite LP with an a posteriori exact gap; failed solvers retain a fallback."""
    import numpy as np
    from scipy.optimize import linprog
    start = time.perf_counter()
    n,k = len(problem.lower),len(problem.bounds)
    features = np.asarray(problem.features,dtype=float)
    A = np.zeros((2*n+2*k,2*k+2));rhs = np.zeros(2*n+2*k)
    A[:n,:k] = -features;A[:n,-2] = -1;rhs[:n] = -np.asarray(problem.upper,dtype=float)
    A[n:2*n,:k] = features;A[n:2*n,-1] = 1;rhs[n:2*n] = np.asarray(problem.lower,dtype=float)
    for j in range(k):
        A[2*n+2*j,j] = 1;A[2*n+2*j,k+j] = -1
        A[2*n+2*j+1,j] = -1;A[2*n+2*j+1,k+j] = -1
    objective = np.zeros(2*k+2);objective[k:2*k] = np.asarray(problem.penalty,dtype=float)
    objective[-2:] = [1,-1]
    bounds = [(-float(B),float(B)) for B in problem.bounds]+[(0,None)]*k+[(None,None)]*2
    proposed = linprog(objective,A_ub=A,b_ub=rhs,bounds=bounds,method='highs',
                       options={'presolve':True,'maxiter':10000})
    if proposed.success:
        theta = tuple(max(-F(B),min(F(B),F(round(float(v)*2**bits),2**bits))) for v,B in zip(proposed.x[:k],problem.bounds))
        p = simplex(-proposed.ineqlin.marginals[:n],bits)
        q = simplex(-proposed.ineqlin.marginals[n:2*n],bits)
    else:
        theta = (F(0),)*k;p=q=(F(1),)+(F(0),)*(n-1)
    record = problem.verify(theta,p,q)
    record.update(p=p,q=q,solver_success=bool(proposed.success),solver_status=int(proposed.status),
                  solver_message=str(proposed.message),iterations=int(proposed.nit),
                  variables=2*k+2,constraints=2*n+2*k,seconds=time.perf_counter()-start,
                  inference='optimization and residual qualification; no statistical observations')
    return record
