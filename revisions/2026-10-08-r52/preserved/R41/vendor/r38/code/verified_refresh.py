"""R38 native floating-point factor refresh with complete-step verification.

The stored float is an exact dyadic. Proposals use binary32 or binary64;
verification uses the inherited outward binary64 matrix balls. No exact
rational products/solves are used by this implementation. Failure is explicit.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import sys
import math
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent/'vendor'))
from entropic_certificate import Ball, up, down, add, mul, div, norm2


def spectral_bounds(M: np.ndarray) -> tuple[float, float]:
    """Sufficient outward Gershgorin bounds; no numerical eigenvalue is a proof."""
    if M.ndim != 2 or M.shape[0] != M.shape[1] or not np.array_equal(M,M.T):
        raise ValueError('A finite, exactly symmetric target is required')
    if not np.isfinite(M).all(): raise ValueError('Nonfinite target')
    bounds=[]
    for i in range(len(M)):
        off=add(*(abs(float(M[i,j])) for j in range(len(M)) if i!=j))
        bounds.append((float(down(M[i,i]-off)),float(up(M[i,i]+off))))
    m=min(x[0] for x in bounds); L=max(x[1] for x in bounds)
    if m<=0: raise ArithmeticError('Target spectral floor not certified')
    return m,L


def gram_error(W: np.ndarray, M: np.ndarray, m: float) -> float:
    B=Ball.exact(W)
    return div((B.T@B-Ball.exact(M)).norm_f(),m)


def cold_factor(M: np.ndarray, height: int | None = None):
    """Scalar identity start, not a target factorization, with a certified basin."""
    m,L=spectral_bounds(M); d=len(M); p=height or d+1
    if p<d: raise ValueError('Factor height must be at least dimension')
    a=2*m*L/(m+L); w=math.sqrt(a)
    W=np.zeros((p,d)); W[:d,:]=np.eye(d)*w
    ab=Ball.exact(w).scale(w)
    rho=max(float(up(div(ab.upper(),m)-1)),float(up(1-float(down(ab.lower()/L)))))
    rho=float(up(rho))
    if not 0<rho<1: raise ArithmeticError('Cold basin is not certified')
    return W,rho,m,L


@dataclass
class FixedTarget:
    target: np.ndarray
    cache: bool = True
    inverse_builds: int = 0
    inverse_applications: int = 0
    proposed_steps: int = 0
    rejected_steps: int = 0
    terminal_gram_checks: int = 0
    scalar_multiply_adds: int = 0
    _inverse: dict = field(default_factory=dict)

    def __post_init__(self):
        self.target=np.asarray(self.target,dtype=np.float64).copy()
        self.target.setflags(write=False)
        self.m,self.L=spectral_bounds(self.target)

    def propose(self,W: np.ndarray,precision: int):
        if precision not in (32,64): raise ValueError('Precision must be 32 or 64')
        dtype=np.float32 if precision==32 else np.float64
        A=self.target.astype(dtype); X=np.asarray(W,dtype=dtype)
        key=precision
        if key not in self._inverse or not self.cache:
            inv=np.linalg.solve(A,np.eye(len(A),dtype=dtype))
            self.inverse_builds+=1
            if self.cache: self._inverse[key]=inv
        else: inv=self._inverse[key]
        H=X.T@X; Z=inv@H
        new=(dtype(.5)*X@(dtype(3)*np.eye(len(A),dtype=dtype)-Z)).astype(np.float64)
        self.inverse_applications+=1;self.proposed_steps+=1
        p,d=W.shape
        self.scalar_multiply_adds+=2*p*d*d+d*d*d
        if not np.isfinite(new).all() or not np.isfinite(Z).all():
            raise ArithmeticError('Nonfinite floating-point proposal')
        # Original stored inputs include all input-conversion errors.
        wb=Ball.exact(W); mb=Ball.exact(self.target); zb=Ball.exact(Z.astype(np.float64))
        residual=(mb@zb-wb.T@wb).norm_f()
        product=(wb@(Ball.exact(3*np.eye(d))-zb)).scale(.5)
        product_error=(Ball.exact(new)-product).norm_f()
        abs_error=add(product_error,mul(.5,norm2(wb),div(residual,self.m)))
        root=float(down(math.sqrt(self.m)))
        nu=div(abs_error,root)
        return new,dict(precision=precision,relative_step_error=nu,
            target_solve_residual_upper=residual,product_and_storage_error_upper=product_error,
            multiply_adds=2*p*d*d+d*d*d)

    def step(self,W,rho,mode='adaptive',terminal_tolerance=None):
        if not 0<rho<1: raise ValueError('A proved radius in (0,1) is required')
        c=float(up((3+rho)/4)); budget=float(down((1-c)*float(down(rho*rho))))
        choices=(32,64) if mode=='adaptive' else (int(mode),)
        rejected=[]
        for prec in choices:
            V,info=self.propose(W,prec)
            nu=info['relative_step_error']; noise=add(mul(2,nu),mul(nu,nu))
            next_radius=add(mul(c,rho,rho),noise)
            acceptance='quadratic-envelope' if noise<=budget else None
            if acceptance is None and terminal_tolerance is not None:
                self.terminal_gram_checks+=1
                direct=gram_error(V,self.target,self.m)
                if direct<=terminal_tolerance:
                    acceptance='terminal-Gram-certificate'
                    next_radius=min(next_radius,direct)
                    info['terminal_gram_upper']=direct
            if acceptance is not None:
                info.update(accepted=True,acceptance=acceptance,starting_radius=rho,next_radius=next_radius,
                            rejected_precisions=rejected)
                return V,next_radius,info
            self.rejected_steps+=1; rejected.append(prec)
        raise ArithmeticError('Whole-step budget exhausted at available native precisions')


def fit(M,tolerance,mode='adaptive',cache=True,start=None,max_updates=32):
    target=FixedTarget(M,cache=cache)
    warm_failed=False
    if start is not None:
        W=np.asarray(start,dtype=float).copy();rho=gram_error(W,M,target.m)
        if not rho<.9:
            warm_failed=True;W,rho,_,_=cold_factor(M,len(W))
    else: W,rho,_,_=cold_factor(M)
    trace=[]
    while gram_error(W,M,target.m)>tolerance:
        if len(trace)>=max_updates: raise ArithmeticError('Update cap exhausted')
        W,rho,info=target.step(W,rho,mode,terminal_tolerance=tolerance);trace.append(info)
    return W,dict(certified=True,relative_gram_upper=gram_error(W,M,target.m),
        requested_relative_tolerance=tolerance,updates=len(trace),trace=trace,
        inverse_builds=target.inverse_builds,inverse_applications=target.inverse_applications,
        rejected_steps=target.rejected_steps,terminal_gram_checks=target.terminal_gram_checks,
        multiply_adds=target.scalar_multiply_adds,warm_gate_failed=warm_failed,m=target.m,L=target.L,
        native_storage_bits_peak=int(W.size*64),
        accepted_mantissa_bits_sum=sum(24 if r['precision']==32 else 53 for r in trace))
