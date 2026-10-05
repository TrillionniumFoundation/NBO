"""A new finite-support instance of the inherited nonlinear capital economy."""
from __future__ import annotations
import hashlib, json, math
from pathlib import Path
import numpy as np
import torch
from intervals import I, up, down

torch.set_default_dtype(torch.float64)
torch.set_num_threads(1)


def checksum(x):
    a=np.ascontiguousarray(x,dtype='<f8')
    return hashlib.sha256(str(a.shape).encode()+a.tobytes()).hexdigest()


def make_inputs(d:int):
    h=.25;rho=.04;left=np.arange(4)*h
    A=(np.exp(-rho*left)-np.exp(-rho*(left+h)))/rho
    W=A/rho+(1-1/rho)*math.exp(-rho)*h
    g=np.random.default_rng(195100+d)
    z=np.clip(g.standard_normal((8,4,d+1)),-3.,3.)
    z=np.concatenate([z,-z],axis=0)
    increments=.1*math.sqrt(h)*z[:,:,:d]+.08*math.sqrt(h)*z[:,:,d:]
    u=.55
    constants=W*(-u)+A*(math.log(u)-.10*u*u/2)
    return dict(dimension=d,h=h,c0=float(.05-(.10**2+.08**2)/2),coupling=.08,
        mixing=.20,A=A.tolist(),W=W.tolist(),reference=u,
        terminal_gamma=float(2*.08*math.exp(-rho)),constants=constants.tolist(),
        increments=increments.tolist(),increments_sha256=checksum(increments),
        interpretation='Every stored binary64 coefficient and increment is an exact finite-model input; all sixteen paths have mass 1/16.')


def tasks(n:int,d:int,seed:int):
    g=np.random.default_rng(seed)
    # Always generate the entire maximum-volume catalogue: all six prefixes
    # have identical rows, not seed-dependent changes in the draw layout.
    N=1024
    means=g.uniform(-.5,.5,(N,1));spreads=g.uniform(.05,.5,(N,1))
    v=g.standard_normal((N,d));v-=v.mean(1,keepdims=True)
    v/=np.sqrt((v*v).mean(1,keepdims=True))
    y=means+spreads*v
    pars=np.column_stack([g.uniform(.8,1.2,N),g.uniform(.05,.15,N),g.uniform(0,.12,N),g.uniform(.65,.95,N)])
    return torch.from_numpy(y[:n].copy()),torch.from_numpy(pars[:n].copy())


class Economy:
    def __init__(self,inputs:dict):
        self.inputs=inputs;self.d=int(inputs['dimension']);self.h=inputs['h'];self.lam=inputs['coupling'];self.mix=inputs['mixing'];self.c0=inputs['c0'];self.gamma=inputs['terminal_gamma'];self.ref=inputs['reference']
        self.A=np.asarray(inputs['A']);self.W=np.asarray(inputs['W']);self.const=np.asarray(inputs['constants']);self.noise=np.asarray(inputs['increments'])
        if checksum(self.noise)!=inputs['increments_sha256']:raise ValueError('finite law hash mismatch')
        self.z=torch.from_numpy(self.noise.copy())
    def mix_state(self,y):return (1-self.mix)*y+self.mix*y.mean(-1,keepdim=True)
    def base(self,x):return -self.gamma/2*((x-x.mean(-1,keepdim=True))**2).mean(-1)
    def post(self,y,a):return y+self.h*(self.c0+self.lam*torch.tanh(self.mix_state(y))-a[:,None])
    def current(self,a,t):return self.A[0]*(t[:,0]*torch.log(a)-t[:,1]*a*a/2-t[:,2]*a)-self.W[0]*a
    def future(self,x,ids=None):
        z=self.z if ids is None else self.z[ids]
        y=x[None,:,:]+z[:,0,None,:];r=torch.zeros(y.shape[:-1],dtype=y.dtype)
        for k in range(1,4):
            prod=self.lam*torch.tanh(self.mix_state(y))
            r=r+self.W[k]*prod.mean(-1)+self.const[k]
            y=y+self.h*(self.c0+prod-self.ref)+z[:,k,None,:]
        return r+self.base(y)
    def value(self,y,a,t,ids=None):return self.current(a,t)+self.future(self.post(y,a),ids).mean(0)
    def value_gradient(self,x,ids):
        xx=x.detach().clone().requires_grad_(True)
        val=self.future(xx,ids).mean(0)
        grad=torch.autograd.grad(val.sum(),xx)[0]
        return val.detach(),grad.detach()
    def derivative(self,y,a,t,ids=None):
        aa=a.detach().clone().requires_grad_(True)
        v=self.value(y,aa,t,ids)
        return torch.autograd.grad(v.sum(),aa)[0].detach()
    def curvature_lower(self,y,t):
        """Uniform-in-action upper bound on S(x(a))'' on each task interval.

        P bounds the infinity norm of the first path derivative, D the
        second. The concave terminal Var(p) term is dropped, never reversed.
        All constants and bounds are evaluated with outward arithmetic.
        """
        yn=y.detach().numpy();tn=t.detach().numpy()
        P=I(self.h);D=I(0.);M=I(0.)
        R=I(yn.max(1)-yn.min(1))
        # Widen subtraction of extrema explicitly.
        R=I(yn.max(1))-I(yn.min(1))+2*I(self.h)*self.lam
        range_noise=I(self.noise.max(2))-I(self.noise.min(2))
        R=R[None,:]+range_noise[:,0,None]
        for k in range(1,4):
            prod2=self.lam*(D+2*P.square())
            M=M+self.W[k]*prod2
            D=D+self.h*prod2
            P=(1+I(self.h)*self.lam)*P
            R=R+2*I(self.h)*self.lam+range_noise[:,k,None]
        M=M+self.gamma*(R*D).mean(0)
        current=I(self.A[0])*(I(tn[:,0])/I(tn[:,3]).square()+I(tn[:,1]))
        result=(current-M).lo
        if np.any(result<=0):raise ArithmeticError('no uniform strong-concavity certificate')
        return result
    def interval_derivative(self,y,a,t):
        yn=y.detach().numpy();an=a.detach().numpy();tn=t.detach().numpy()
        mix=lambda q:(1-I(self.mix))*q+self.mix*q.mean(-1,True)
        yy=I(yn)+self.h*(self.c0+self.lam*mix(I(yn)).tanh()-I(an)[:,None])
        yy=yy[None,:,:]+I(self.noise[:,0,None,:])
        pp=I(np.full(yy.lo.shape,-self.h));der=I(np.zeros(yy.lo.shape[:-1]))
        for k in range(1,4):
            tan=mix(yy).tanh();prod=self.lam*tan
            dp=self.lam*(1-tan.square())*mix(pp)
            der=der+self.W[k]*dp.mean(-1)
            yy=yy+self.h*(self.c0+prod-self.ref)+I(self.noise[:,k,None,:])
            pp=pp+self.h*dp
        der=der-self.gamma*((yy-yy.mean(-1,True))*pp).mean(-1)
        cur=self.A[0]*(I(tn[:,0])/I(an)-I(tn[:,1])*I(an)-I(tn[:,2]))-self.W[0]
        return cur+der.mean(0)
    def certify(self,y,a,t):
        if not torch.isfinite(a).all() or torch.any(a<.05) or torch.any(a>t[:,3]):raise ValueError('infeasible selected action')
        derivative=self.interval_derivative(y,a,t);kappa=self.curvature_lower(y,t)
        av=a.detach().numpy();cap=t[:,3].numpy()
        res=np.maximum(np.abs(derivative.lo),np.abs(derivative.hi))
        res=np.where(av==.05,np.maximum(0,derivative.hi),res)
        res=np.where(av==cap,np.maximum(0,-derivative.lo),res)
        upper=(I(res).square()/(2*I(kappa))).hi
        return dict(mean_regret_upper=float(I(upper).mean().hi),regret_upper=upper.tolist(),
            kappa_lower=kappa.tolist(),derivative_lower=derivative.lo.tolist(),derivative_upper=derivative.hi.tolist())
