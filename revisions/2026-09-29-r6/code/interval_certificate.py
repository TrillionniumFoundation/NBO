"""Outward-rounded, full-domain certificate for the stopped-consumption MLP.

Arithmetic contract: binary64 round-to-nearest for elementary +,-,*,/ and
standard dot-product forward-error bounds; no overflow, flush-to-zero or NaNs.
Transcendentals do NOT rely on numpy's log/tanh accuracy: exp uses a
range-reduced polynomial with a proved remainder, and log an atanh series.
Stored binary64 weights and primitive coefficients denote exact real numbers.
The certificate does not claim optimizer convergence or high-dimensional
coverage. The complete dyadic leaf cover is part of the raw result.
"""
from __future__ import annotations
import argparse, hashlib, json, math, time
from dataclasses import dataclass
from pathlib import Path
import numpy as np

EPS=np.finfo(np.float64).eps

def down(x): return np.nextafter(np.asarray(x,dtype=np.float64),-np.inf)
def up(x): return np.nextafter(np.asarray(x,dtype=np.float64),np.inf)

@dataclass
class I:
    __array_priority__ = 10000
    lo: np.ndarray
    hi: np.ndarray
    def __init__(self,lo,hi=None):
        self.lo=np.asarray(lo,dtype=float);self.hi=np.asarray(lo if hi is None else hi,dtype=float)
        if np.any(self.lo>self.hi) or not (np.isfinite(self.lo).all() and np.isfinite(self.hi).all()):
            raise FloatingPointError('nonfinite or inverted interval')
    def __add__(self,other):
        other=as_i(other);return I(down(self.lo+other.lo),up(self.hi+other.hi))
    __radd__=__add__
    def __neg__(self):return I(-self.hi,-self.lo)
    def __sub__(self,other):return self+-as_i(other)
    def __rsub__(self,other):return as_i(other)+-self
    def __mul__(self,other):
        other=as_i(other)
        pp=[self.lo*other.lo,self.lo*other.hi,self.hi*other.lo,self.hi*other.hi]
        return I(down(np.minimum.reduce(pp)),up(np.maximum.reduce(pp)))
    __rmul__=__mul__
    def reciprocal(self):
        if np.any((self.lo<=0)&(self.hi>=0)): raise ZeroDivisionError('interval contains zero')
        return I(down(1/self.hi),up(1/self.lo))
    def __truediv__(self,other): return self*as_i(other).reciprocal()
    def __rtruediv__(self,other): return as_i(other)*self.reciprocal()
    def square(self):
        lower=np.where((self.lo<=0)&(self.hi>=0),0,np.minimum(self.lo*self.lo,self.hi*self.hi))
        return I(np.maximum(0,down(lower)),up(np.maximum(self.lo*self.lo,self.hi*self.hi)))
    def absmax(self): return np.maximum(abs(self.lo),abs(self.hi))

def as_i(x): return x if isinstance(x,I) else I(x)

def rational(n,d):
    z=float(n)/float(d)
    return I(down(z),up(z))

def exp_i(x):
    """|r|<=1/8, degree 14; remainder <2^-80 before repeated squaring.

    e^|r| |r|^15/15! < 2*(1/8)^15/15! < 2^-80.
    The extra slack also covers outward endpoint displacement in scaling.
    """
    x=as_i(x);m=float(np.max(x.absmax()))
    if m>100: raise FloatingPointError('exp certificate range exceeded')
    s=max(0,int(math.ceil(math.log2(max(m*8,1)))))
    r=x/(2.**s)
    if np.max(r.absmax())>.125000000000001: raise AssertionError('range reduction')
    out=rational(1,math.factorial(14))
    for k in range(13,-1,-1): out=out*r+rational(1,math.factorial(k))
    out=out+I(-2.**-80,2.**-80)
    for _ in range(s):out=out.square()
    return out

def tanh_i(x):
    z=1-2/(exp_i(2*as_i(x))+1)
    return I(np.maximum(-1,z.lo),np.minimum(1,z.hi))

def log_atanh(z):
    """2*sum_{j=0}^{24} z^(2j+1)/(2j+1), |z|<.334.

    Remainder <=2*.334^51/(51*(1-.334^2)) <2^-72.
    """
    z=as_i(z)
    if np.max(z.absmax())>=.334: raise AssertionError('log reduction')
    zz=z.square(); p=rational(1,49)
    for k in range(23,-1,-1):p=p*zz+rational(1,2*k+1)
    return 2*z*p+I(-2.**-72,2.**-72)
LOG2=log_atanh(rational(1,3))

def log_point(x):
    if np.any(np.asarray(x)<=0):raise ValueError('log domain')
    mantissa,exponent=np.frexp(np.asarray(x,dtype=float))
    # Frexp and the multiplication by two are exact in the permitted range.
    m=I(2*mantissa);return log_atanh((m-1)/(m+1))+(exponent-1)*LOG2

def log_i(x):
    x=as_i(x);return I(log_point(x.lo).lo,log_point(x.hi).hi)

def affine(x,W,b=None):
    W=np.asarray(W,dtype=float);pos=np.maximum(W,0);neg=np.minimum(W,0)
    lo=x.lo@pos.T+x.hi@neg.T;hi=x.hi@pos.T+x.lo@neg.T
    if b is not None:lo=lo+b;hi=hi+b
    count=2*W.shape[1]+8
    gamma=up(count*EPS/(1-count*EPS))
    absolute=x.absmax()@np.abs(W).T
    if b is not None:absolute=absolute+np.abs(b)
    error=up(gamma*up(absolute))
    return I(down(lo-error),up(hi+error))

def network_jets(x,layers):
    h=x;d=I(np.ones_like(x.lo));dd=I(np.zeros_like(x.lo))
    for k,layer in enumerate(layers):
        W=np.asarray(layer['weight']);b=np.asarray(layer['bias'])
        h=affine(h,W,b);d=affine(d,W);dd=affine(dd,W)
        if k<len(layers)-1:
            th=tanh_i(h);one=1-th.square()
            one=I(np.maximum(0,one.lo),np.minimum(1,one.hi))
            second=-2*th*one
            dd=second*d.square()+one*dd;d=one*d;h=th
    return h,d,dd

def value_jets(x,model):
    p=model['parameters'];l,u=p['lower'],p['upper'];scale=I(2)/(I(u)-l)
    z=scale*(x-l)-1;n,nz,nzz=network_jets(z,model['value'])
    nx=nz*scale;nxx=nzz*scale.square()
    g0,g1=model['boundary_values'];slope=(I(g1)-g0)/(I(u)-l)
    q=(x-l)*(u-x);qp=I(l)+u-2*x
    v=I(g0)+slope*(x-l)+q*n
    vx=slope+qp*n+q*nx
    vxx=-2*n+2*qp*nx+q*nxx
    return v,vx,vxx

def optimal_interval(vx,p):
    # c*(p) is nonincreasing; use outward reciprocals on its positive branch.
    lo=np.where(vx.hi>0,down(1/np.maximum(vx.hi,1e-300)),p['c_upper'])
    hi=np.where(vx.lo>0,up(1/np.maximum(vx.lo,1e-300)),p['c_upper'])
    return I(np.clip(lo,p['c_lower'],p['c_upper']),np.clip(hi,p['c_lower'],p['c_upper']))

def enclose(left,right,model):
    x=I(np.asarray(left)[:,None],np.asarray(right)[:,None]);p=model['parameters']
    v,vx,vxx=value_jets(x,model);best=optimal_interval(vx,p)
    if model['actor'] is None:c=best
    else:
        z=2*(x-p['lower'])/(I(p['upper'])-p['lower'])-1
        raw,_,_=network_jets(z,model['actor'])
        c=I(p['c_lower'])+(I(p['c_upper'])-p['c_lower'])*(1+tanh_i(raw/2))/2
    residual=(I(p['discount'])*v-log_i(c)
        -(I(p['income'])+p['interest']*x-c)*vx
        -rational(1,2)*I(p['volatility']).square()*x.square()*vxx)
    if model['actor'] is None:gap=I(np.zeros_like(left))
    else:
        gap=log_i(best)-log_i(c)+(c-best)*vx
        # Strong concavity: h(c*)-h(c) <= C^2*(1/c-p)^2/2.
        C=I(np.maximum(c.hi,best.hi))
        strong=rational(1,2)*C.square()*(1/c-vx).square()
        gap=I(np.minimum(gap.lo,0),np.minimum(gap.hi,strong.hi))
    return residual.lo.ravel(),residual.hi.ravel(),np.maximum(0,gap.hi.ravel())

def certificate(path,target_residual=.002,target_gap=.0002,max_depth=18,batch=2048):
    start=time.perf_counter();path=Path(path);model=json.loads(path.read_text());p=model['parameters']
    if 'boundary_values' not in model:raise ValueError('missing exact stored boundary constants')
    l,u=p['lower'],p['upper'];left=np.array([l]);right=np.array([u]);depth=0;accepted=[];processed=0
    while len(left):
        remaining=[]
        for j in range(0,len(left),batch):
            a,b=left[j:j+batch],right[j:j+batch]
            rlo,rhi,gap=enclose(a,b,model);processed+=len(a)
            rows=np.c_[a,b,rlo,rhi,gap]
            good=(np.maximum(abs(rlo),abs(rhi))<=target_residual)&(gap<=target_gap)
            if depth==max_depth:good[:]=True
            if np.any(good):accepted.append(rows[good])
            if np.any(~good):remaining.append(rows[~good,:2])
        if not remaining:break
        rem=np.concatenate(remaining);middle=(rem[:,0]+rem[:,1])/2
        left=np.r_[rem[:,0],middle];right=np.r_[middle,rem[:,1]];depth+=1
    leaves=np.concatenate(accepted);leaves=leaves[np.argsort(leaves[:,0])]
    if leaves[0,0]!=l or leaves[-1,1]!=u or not np.array_equal(leaves[:-1,1],leaves[1:,0]):
        raise AssertionError('certificate does not cover the complete interval')
    if not np.all(leaves[:,1]>leaves[:,0]):raise AssertionError('empty cover leaf')
    e=float(np.max(np.maximum(abs(leaves[:,2]),abs(leaves[:,3]))));eta=float(np.max(leaves[:,4]))
    # Primitive arithmetic is enclosed too; stopping payoff is not silently exact.
    boundary=[]
    for x,g in zip([l,u],model['boundary_values']):
        gg=log_i(I(p['income'])+I(p['discount'])*I(x))/I(p['discount'])
        boundary.append(float((I(g)-gg).absmax()))
    B=max(boundary);rho=I(p['discount'])
    E=float((I(B)+I(e)/rho).hi);VE=float((I(B)+(I(e)+eta)/rho).hi)
    R=float((2*I(B)+(2*I(e)+eta)/rho).hi)
    leafpath=path.with_name(path.stem+'_interval_leaves.npz')
    np.savez_compressed(leafpath,leaves=leaves,columns=np.array(['left','right','residual_lower','residual_upper','gap_upper']))
    out=dict(model_id=model['model_id'],model_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        interval_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        domain=[l,u],scope='entire continuous state interval and all admissible consumption actions',
        covered=True,leaf_count=len(leaves),processed_boxes=processed,max_depth_used=depth,
        residual_upper=e,action_gap_upper=eta,boundary_error_by_face=boundary,
        policy_value_error_upper=E,optimal_value_error_upper=VE,policy_regret_upper=R,
        target_residual=target_residual,target_gap=target_gap,
        passed=bool(e<=target_residual and eta<=target_gap),
        seconds=time.perf_counter()-start,leaf_sha256=hashlib.sha256(leafpath.read_bytes()).hexdigest(),
        assumptions=['binary64 arithmetic and standard dot-product error contract',
            'stopped diffusion and Dirichlet comparison on [.5,2.5]',
            'coefficients and stored weights denote their exact binary64 real values'],
        unchecked=['formal machine verification of the arithmetic implementation'])
    path.with_name(path.stem+'_certificate.json').write_text(json.dumps(out,indent=2))
    return out

def main():
    parser=argparse.ArgumentParser();parser.add_argument('model',nargs='+');parser.add_argument('--depth',type=int,default=18)
    parser.add_argument('--residual',type=float,default=.002);parser.add_argument('--gap',type=float,default=.0002)
    a=parser.parse_args()
    for path in a.model: print(json.dumps(certificate(path,a.residual,a.gap,a.depth)),flush=True)
if __name__=='__main__':main()
