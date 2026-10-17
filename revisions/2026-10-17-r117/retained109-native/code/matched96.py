"""Rank-six, label-matched, fixed-payload convex continuation construction.

All candidate searches are paid. Equal solver-call budgets are not equal CPU
work; actual time, active coefficients and conditioning remain in the record.
"""
from __future__ import annotations
import json
import numpy as np
from scipy.optimize import lsq_linear
from representations94 import Fit, features
from interval94 import I, as_i, stack
from investment94 import count

KINDS=('quadratic','relu','spline')


class MatchedFit(Fit):
    def interval(self, x, gradient=False):
        x=as_i(x);d=x.lo.shape[-1];theta=self.coefficients
        val=I(theta[0])+(x*theta[1:d+1]).sum()
        grad=[I(np.broadcast_to(theta[j+1],x.lo.shape[:-1])) for j in range(d)]
        for k,(direction,offset) in enumerate(zip(self.directions,self.offsets)):
            w=theta[d+1+k];z=(x*direction).sum()+offset
            if self.kind=='quadratic':phi=z.square();deriv=z*2
            else:phi=z.positive();deriv=I((z.lo>0).astype(float),(z.hi>0).astype(float))
            val=val+phi*w
            if gradient:
                for j in range(d):grad[j]=grad[j]+deriv*I(w)*I(direction[j])
        size=int(np.prod(x.lo.shape[:-1]))
        count('continuation_interval_values',size)
        count('continuation_nonlinear_features',len(self.offsets)*size)
        return (val.checked(),stack(grad).checked()) if gradient else val.checked()


def exact_rank_witness(kind,x,W,b):
    from fractions import Fraction as F
    basis=[];ids=[]
    for i,row in enumerate(x):
        xx=[F(float(t)) for t in row]
        zz=[sum(F(float(t))*v for t,v in zip(w,xx))+F(float(o)) for w,o in zip(W,b)]
        v=[F(1)]+xx+[z*z if kind=='quadratic' else max(F(0),z) for z in zz]
        for pivot,u in basis:
            factor=v[pivot];v=[a-factor*c for a,c in zip(v,u)]
        pivot=next((j for j,a in enumerate(v) if a),None)
        if pivot is not None:
            div=v[pivot];basis.append((pivot,[a/div for a in v]));ids.append(i)
        if len(basis)==6:return {'rank':6,'row_indices':ids,'arithmetic':'exact rational feature values'}
    raise ArithmeticError('Final executable representation is not exactly rank six')


def construct(kind,x,y):
    if x.shape[1]!=2 or kind not in KINDS:
        raise ValueError('The matched primary slice has dimension two')
    W,b=features(kind,2)
    if kind=='spline':
        # Knots adapt to training covariates only; greedy selection also uses labels.
        for k in range(32):
            b[k]=-np.quantile(x[:,k%2],(k//2+1)/17)
        b=np.rint(b*2**16)/2**16
    z=x@W.T+b;phi=z*z if kind=='quadratic' else np.maximum(z,0)
    base=np.column_stack((np.ones(len(x)),x));chosen=[];trials=[]
    for step in range(3):
        candidates=[]
        for j in range(32):
            if j in chosen:continue
            columns=chosen+[j];A=np.column_stack((base,phi[:,columns]))
            singular=np.linalg.svd(A,compute_uv=False)
            rank=int(np.linalg.matrix_rank(A))
            if rank!=A.shape[1]:
                trials.append(dict(step=step,candidate=j,rank=rank,admitted=False));continue
            lower=np.r_[np.full(3,-np.inf),np.zeros(len(columns))]
            fit=lsq_linear(A,y,bounds=(lower,np.full(A.shape[1],np.inf)),
                           method='trf',tol=1e-10,max_iter=1000,lsq_solver='exact')
            if not np.all(np.isfinite(fit.x)):
                raise ArithmeticError('Nonfinite candidate retained as campaign failure')
            loss=float(np.sum((A@fit.x-y)**2))
            trials.append(dict(step=step,candidate=j,rank=rank,admitted=True,
                               success=bool(fit.success),iterations=int(fit.nit),loss=loss))
            candidates.append((loss,j,fit.x.copy(),singular))
            count('r96_candidate_fit_solves')
        if not candidates:raise ArithmeticError('No full-rank candidate; no replacement arm')
        _,j,theta,singular=min(candidates,key=lambda item:(item[0],item[1]));chosen.append(j)
    theta=np.rint(theta*2**30)/2**30;theta[3:]=np.maximum(theta[3:],0)
    A=np.column_stack((base,phi[:,chosen]));residual=A@theta-y
    record=dict(training_rows=len(x),effective_design_rank=int(np.linalg.matrix_rank(A)),
                nonlinear_features=3,coefficient_count=6,selected_features=chosen,
                active_nonlinear_coefficients=int(np.count_nonzero(theta[3:])),
                condition_number=float(singular[0]/singular[-1]),
                rmse=float(np.sqrt(np.mean(residual**2))),candidate_trials=trials,
                payload_bytes=128,adaptive_knots=kind=='spline',exact_rank_witness=exact_rank_witness(kind,x,W[chosen],b[chosen]))
    return MatchedFit(kind,W[chosen],b[chosen],theta,record)


def encode(model):
    # One family tag, six directions, three offsets, six coefficients: 16 float64s.
    numbers=np.r_[float(KINDS.index(model.kind)),model.directions.ravel(),
                  model.offsets,model.coefficients]
    if len(numbers)!=16:raise ValueError('Fixed payload budget violated')
    return np.asarray(numbers,dtype='<f8').tobytes()


def decode(raw):
    if len(raw)!=128:raise ValueError('Wrong payload length')
    a=np.frombuffer(raw,dtype='<f8').copy()
    if not np.all(np.isfinite(a)) or a[0] not in (0.,1.,2.):raise ValueError('Invalid model')
    if np.any(a[13:]<0):raise ValueError('Nonconvex readout rejected')
    return MatchedFit(KINDS[int(a[0])],a[1:7].reshape(3,2),a[7:10],a[10:16],{})
