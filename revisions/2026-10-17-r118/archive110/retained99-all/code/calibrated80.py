"""Representation-calibrated residual qualification and exact stability witnesses.

Only LP proposals use binary64. Every reported primal objective, dual lower
bound and action-switch constraint is checked using fractions. State distance
is l1; derivative control rows certify the corresponding Lipschitz modulus.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from typing import Sequence
import time
import numpy as np
from scipy.optimize import linprog
from qualification73 import Problem, dot, simplex


def derivative_rows(kind: str) -> tuple[tuple[F,...], ...]:
    rows=[]
    for axis in range(2):
        for j in range(4):
            row=[F(0)]*9
            if kind=='relu':
                for k in range(j+1):row[1+axis*4+k]=F(1)
            elif kind=='bernstein':
                row[1+axis*4+j]=F(4)
                if j:row[axis*4+j]=F(-4)
            else:raise ValueError('Unknown basis')
            rows.append(tuple(row))
    return tuple(rows)


def modulus(theta: Sequence[F], kind: str) -> F:
    if len(theta)!=9:raise ValueError('Nine coefficients required')
    return max(abs(dot(row,theta)) for row in derivative_rows(kind))


@dataclass(frozen=True)
class Calibrated:
    problem: Problem
    kind: str

    @property
    def rows(self):return derivative_rows(self.kind)

    def primal(self,theta):
        p=self.problem;theta=tuple(map(F,theta))
        old=p.primal(theta);L=modulus(theta,self.kind)
        pad=p.radius*(p.bellman_lipschitz+L)
        return dict(theta=theta,nodal_lower=old['nodal_lower'],nodal_upper=old['nodal_upper'],
            residual_lower=old['nodal_lower']-pad,residual_upper=old['nodal_upper']+pad,
            lipschitz=L,objective=old['nodal_upper']-old['nodal_lower']+2*pad,
            legacy_objective_same_labels=old['objective'])

    def dual(self,p,q,xi,nu=F(0),action_row=None,action_offset=F(0)):
        P=self.problem;p=tuple(map(F,p));q=tuple(map(F,q));xi=tuple(map(F,xi));nu=F(nu)
        n=len(P.lower);rows=self.rows
        if len(p)!=n or len(q)!=n or len(xi)!=2*len(rows):raise ValueError('Dual dimension')
        if min(p+q+xi+(nu,))<0 or sum(p)!=1 or sum(q)!=1 or sum(xi)>2*P.radius:raise ValueError('Invalid exact dual')
        d=(F(0),)*9 if action_row is None else tuple(map(F,action_row))
        if len(d)!=9:raise ValueError('Action contrast dimension')
        active=[(row,qj-pj) for row,pj,qj in zip(P.features,p,q) if qj!=pj]
        slope=[sum((row[k]*v for row,v in active),F(0))
               +sum((row[k]*(xi[2*i]-xi[2*i+1]) for i,row in enumerate(rows)),F(0))+nu*d[k] for k in range(9)]
        return sum((v*y for v,y in zip(p,P.upper) if v),F(0))-sum((v*y for v,y in zip(q,P.lower) if v),F(0))+P.constant+nu*F(action_offset)-dot(P.bounds,[abs(s) for s in slope])

    def arrays(self):
        P=self.problem;n=len(P.lower);k=9;r=len(self.rows)
        A=np.zeros((2*n+2*r,k+3));rhs=np.zeros(len(A));phi=np.asarray(P.features,dtype=float)
        A[:n,:k]=-phi;A[:n,k]=-1;rhs[:n]=-np.asarray(P.upper,dtype=float)
        A[n:2*n,:k]=phi;A[n:2*n,k+1]=1;rhs[n:2*n]=np.asarray(P.lower,dtype=float)
        for i,row in enumerate(self.rows):
            A[2*n+2*i,:k]=np.asarray(row,dtype=float);A[2*n+2*i,k+2]=-1
            A[2*n+2*i+1,:k]=-np.asarray(row,dtype=float);A[2*n+2*i+1,k+2]=-1
        c=np.zeros(k+3);c[k:k+3]=[1,-1,2*float(P.radius)]
        bounds=[(-float(B),float(B)) for B in P.bounds]+[(None,None),(None,None),(0,None)]
        return A,rhs,c,bounds

    def solve(self,action_row=None,action_offset=F(0),arrays=None,primal=True):
        began=time.perf_counter();P=self.problem;n=len(P.lower);A,rhs,c,bounds=self.arrays() if arrays is None else arrays
        d=None if action_row is None else tuple(map(F,action_row));c0=F(action_offset)
        scale=F(1)
        if d is not None:
            scale=max((abs(v) for v in d),default=F(0))
            scale=max(scale,abs(c0),F(1,1<<40))
            row=np.zeros(12);row[:9]=np.asarray([v/scale for v in d],dtype=float)
            A=np.vstack((A,row));rhs=np.r_[rhs,-float(c0/scale)]
        result=linprog(c,A_ub=A,b_ub=rhs,bounds=bounds,method='highs',
            options={'presolve':True,'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
        if not result.success:
            p=q=(F(1),)+(F(0),)*(n-1);xi=(F(0),)*16;nu=F(0)
            return dict(solver_success=False,solver_status=int(result.status),solver_message=str(result.message),
                dual_lower=self.dual(p,q,xi),p=p,q=q,xi=xi,nu=nu,seconds=time.perf_counter()-began)
        p=simplex(-result.ineqlin.marginals[:n],40);q=simplex(-result.ineqlin.marginals[n:2*n],40)
        xi=tuple(F(max(0.,float(v))) for v in -result.ineqlin.marginals[2*n:2*n+16])
        alpha=2*P.radius
        if sum(xi)>alpha:xi=tuple(v*alpha/sum(xi) for v in xi)
        nu=F(0) if d is None else F(max(0.,-float(result.ineqlin.marginals[-1])))/scale
        theta=tuple(max(-F(B),min(F(B),F(round(float(v)*2**40),2**40))) for v,B in zip(result.x[:9],P.bounds))
        if d is not None and c0+dot(d,theta)>0:
            extreme=tuple(-F(B) if v>0 else F(B) if v<0 else t for B,v,t in zip(P.bounds,d,theta))
            g=c0+dot(d,theta);e=c0+dot(d,extreme)
            if e>0:raise AssertionError('Floating feasible point in an infeasible exact halfspace')
            lam=g/(g-e);theta=tuple((1-lam)*a+lam*b for a,b in zip(theta,extreme))
        lower=self.dual(p,q,xi,nu,d,c0)
        if not primal:
            return dict(dual_lower=lower,theta=theta,p=p,q=q,xi=xi,nu=nu,solver_success=True,solver_status=0,seconds=time.perf_counter()-began)
        record=self.primal(theta)
        if record['objective']<lower:raise AssertionError('Negative exact calibrated dual gap')
        record.update(dual_lower=lower,optimization_gap=record['objective']-lower,p=p,q=q,xi=xi,nu=nu,
            solver_success=True,solver_status=int(result.status),solver_message=str(result.message),
            iterations=int(result.nit),variables=12,constraints=len(rhs),seconds=time.perf_counter()-began)
        if d is not None:
            record['action_constraint']=c0+dot(d,theta)
            if record['action_constraint']>0:raise AssertionError('Action-switch primal is infeasible')
        return record
