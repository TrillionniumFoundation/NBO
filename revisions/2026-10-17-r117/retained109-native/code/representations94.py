"""Three prespecified convex continuation fits; one common target matrix."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib,json,time
import numpy as np
from scipy.optimize import lsq_linear
from interval94 import I,as_i,expand,stack,up,down
from investment94 import count

@dataclass
class Fit:
    kind:str
    directions:np.ndarray
    offsets:np.ndarray
    coefficients:np.ndarray
    record:dict
    def float_eval(self,x,gradient=False):
        x=np.asarray(x);d=x.shape[-1];w=self.coefficients[d+1:]
        z=np.einsum('...d,kd->...k',x,self.directions,optimize=False)+self.offsets
        phi=z*z if self.kind=='quadratic' else np.maximum(z,0)
        val=self.coefficients[0]+np.einsum('...d,d->...',x,self.coefficients[1:d+1],optimize=False)+np.einsum('...k,k->...',phi,w,optimize=False)
        count('continuation_proposal_values',int(np.prod(x.shape[:-1])))
        if not gradient:return val
        deriv=2*z if self.kind=='quadratic' else (z>0).astype(float)
        gr=self.coefficients[1:d+1]+np.einsum('...k,k,kd->...d',deriv,w,self.directions,optimize=False)
        return val,gr
    def interval(self,x,gradient=False):
        x=as_i(x);d=x.lo.shape[-1];theta=self.coefficients
        val=I(theta[0])+(x*theta[1:d+1]).sum()
        grad=[I(np.broadcast_to(theta[j+1],x.lo.shape[:-1])) for j in range(d)]
        for k,(direction,offset) in enumerate(zip(self.directions,self.offsets)):
            w=theta[d+1+k]
            z=(x*direction).sum()+offset
            if self.kind=='quadratic':phi=z.square();deriv=z*2
            else:
                phi=z.positive()
                deriv=I((z.lo>0).astype(float),(z.hi>0).astype(float))
            val=val+phi*w
            if gradient:
                for j in range(d):grad[j]=grad[j]+deriv*I(w)*I(direction[j])
        count('continuation_interval_values',int(np.prod(x.lo.shape[:-1])))
        count('continuation_nonlinear_features',32*int(np.prod(x.lo.shape[:-1])))
        return (val.checked(),stack(grad).checked()) if gradient else val.checked()
    def to_dict(self):
        return dict(kind=self.kind,directions=self.directions.tolist(),offsets=self.offsets.tolist(),coefficients=self.coefficients.tolist(),record=self.record)
    @classmethod
    def from_dict(cls,o):return cls(o['kind'],np.array(o['directions']),np.array(o['offsets']),np.array(o['coefficients']),o['record'])
    def identity(self):
        obj={k:v for k,v in self.to_dict().items() if k!='record'}
        return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def features(kind,d):
    if kind not in ('relu','spline','quadratic'):raise ValueError('Unknown frozen arm')
    K=32
    rng=np.random.Generator(np.random.PCG64(202610139310+d))
    if kind=='spline':
        W=np.zeros((K,d));b=np.zeros(K)
        counts=[sum(k%d==j for k in range(K)) for j in range(d)]
        seen=[0]*d
        for k in range(K):
            j=k%d;seen[j]+=1;W[k,j]=1;b[k]=-seen[j]/(counts[j]+1)
    else:
        W=rng.uniform(-1,1,size=(K,d));W/=np.sum(np.abs(W),axis=1,keepdims=True)
        # Shared primitive-only directions. No evaluation rows determine them.
        W=np.rint(W*2**16)/2**16
        points=rng.uniform(0,1,size=(K,d));b=-np.sum(W*points,axis=1)
    b=np.rint(b*2**16)/2**16
    return W,b

def fit(kind,x,y):
    start=time.perf_counter();d=x.shape[-1];W,b=features(kind,d)
    z=x@W.T+b;phi=z*z if kind=='quadratic' else np.maximum(z,0)
    A=np.column_stack((np.ones(len(x)),x,phi))
    low=np.r_[np.full(d+1,-np.inf),np.zeros(32)]
    result=lsq_linear(A,y,bounds=(low,np.full(A.shape[1],np.inf)),method='trf',tol=1e-10,max_iter=1000,lsq_solver='exact')
    if not np.all(np.isfinite(result.x)):raise ArithmeticError('Nonfinite fit; no scientific replacement allowed')
    theta=np.rint(result.x*2**30)/2**30;theta[d+1:]=np.maximum(0,theta[d+1:])
    residual=A@theta-y
    record=dict(training_rows=len(x),nonlinear_features=32,total_coefficients=len(theta),effective_rank=int(np.linalg.matrix_rank(A)),solver='scipy.optimize.lsq_linear/trf/exact',success=bool(result.success),status=int(result.status),iterations=int(result.nit),max_iterations=1000,tolerance=1e-10,dyadic_readout_bits=30,training_rmse=float(np.sqrt(np.mean(residual**2))),training_max_abs=float(np.max(np.abs(residual))),fit_seconds=time.perf_counter()-start)
    count('fit_attempts');count('training_feature_rows',len(x));return Fit(kind,W,b,theta,record)
