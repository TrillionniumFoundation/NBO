"""Rational common-Markov repair driven by a checked operating upper witness.
The constructor never computes or accepts the exact operating optimum V.
Certification of U as an upper witness is a separate caller obligation.
All probabilities, stage arrays, and witnesses are exact Fraction objects.
"""
from __future__ import annotations
from fractions import Fraction as F
from typing import Any


def evaluate(model: dict[str, Any], policy: list[list[list[F]]]):
    n, m, T, beta = model['n'], model['m'], model['T'], model['beta']
    J, C = [None]*T+[model['g'][:]], [None]*T+[[F(0)]*n]
    for t in range(T-1, -1, -1):
        J[t], C[t] = [], []
        for i in range(n):
            prob=policy[t][i]
            if len(prob)!=m or min(prob)<0 or sum(prob)!=1:
                raise ValueError('invalid action simplex')
            J[t].append(sum(prob[a]*(model['r'][a][i]+beta*sum(model['P'][a][i][j]*J[t+1][j] for j in range(n))) for a in range(m)))
            C[t].append(sum(prob[a]*(model['k'][a][i]+beta*sum(model['P'][a][i][j]*C[t+1][j] for j in range(n))) for a in range(m)))
    return J,C


def repair(model: dict[str, Any], U: list[list[F]], policy: list[list[list[F]]], epsilon: F):
    """Return a feasible policy, its values, and an exact a-posteriori audit.

    Reject a nonpositive witness slack rather than interpreting failure of this
    sufficient condition as infeasibility of the original control problem.
    """
    if not __debug__:
        raise RuntimeError('run certificate code without Python -O')
    n,m,T,beta=model['n'],model['m'],model['T'],model['beta']
    if not (0<beta<1 and epsilon>0 and len(U)==T+1 and U[-1]==model['g']):
        raise ValueError('invalid discount, tolerance, or terminal witness')
    if any(len(row)!=n for row in U): raise ValueError('witness shape')
    for a in range(m):
        if any(len(row)!=n or min(row)<0 or sum(row)!=1 for row in model['P'][a]):
            raise ValueError('invalid transition kernel')
    defects=[]
    for t in range(T):
        for i in range(n):
            optimum=max(model['r'][a][i]+beta*sum(model['P'][a][i][j]*U[t+1][j] for j in range(n)) for a in range(m))
            defects.append(U[t][i]-optimum)
    d=max([F(0)]+defects); sigma=(1-beta)*epsilon-d
    if sigma<=0: raise ValueError('uncertified repair: witness slack is not positive')
    oldJ,oldC=evaluate(model,policy)
    delta=max([F(0)]+[U[t][i]-epsilon-oldJ[t][i] for t in range(T) for i in range(n)])
    fixed=[[row[:] for row in stage] for stage in policy]
    J=[None]*T+[model['g'][:]]; actual_tv=F(0)
    for t in range(T-1,-1,-1):
        J[t]=[]
        for i in range(n):
            q=[model['r'][a][i]+beta*sum(model['P'][a][i][j]*J[t+1][j] for j in range(n)) for a in range(m)]
            p=policy[t][i]; qp=sum(p[a]*q[a] for a in range(m)); target=U[t][i]-epsilon
            if qp<target:
                a_star=max(range(m),key=lambda a:(q[a],-a))
                alpha=(target-qp)/(q[a_star]-qp)
                fixed[t][i]=[(1-alpha)*p[a]+alpha*int(a==a_star) for a in range(m)]
            val=sum(fixed[t][i][a]*q[a] for a in range(m)); J[t].append(val)
            assert val>=target and val>=oldJ[t][i]
            actual_tv=max(actual_tv,sum(abs(fixed[t][i][a]-p[a]) for a in range(m))/2)
    freshJ,C=evaluate(model,fixed); assert freshJ==J
    K=max(x for row in model['k'] for x in row)
    if min(x for row in model['k'] for x in row)<0: raise ValueError('negative revision cost')
    DC=K*sum((s+1)*beta**s for s in range(T))
    radius=delta/(sigma+delta)
    assert actual_tv<=radius
    assert all(C[t][i]-oldC[t][i]<=DC*radius for t in range(T) for i in range(n))
    return fixed,J,C,dict(defect=d,sigma=sigma,delta=delta,actual_tv=actual_tv,tv_bound=radius,cost_bound=DC*radius)
