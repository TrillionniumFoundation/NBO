"""R47: outward arithmetic, immutable output and simultaneous direct-cost intervals."""
from __future__ import annotations
import hashlib, json, math, os, sys
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
ROOT=R.parent.parent
sys.path.insert(0,str(R.parent/'2026-10-07-r45'/'code'))
from interval import I, dn, up
BETA=F(15,16)

def canonical(x):
    return (json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()

def write(path,x):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    raw=canonical(x)
    with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    return hashlib.sha256(raw).hexdigest()

def hfile(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def fi(x):
    q=F(x);v=float(q);fv=F(v)
    return I(math.nextafter(v,-math.inf) if fv>q else v,
             math.nextafter(v,math.inf) if fv<q else v)

def fup(x):return float(fi(x).hi)

def isum(a,axis=-1):
    lo=np.moveaxis(a.lo,axis,-1);hi=np.moveaxis(a.hi,axis,-1)
    while lo.shape[-1]>1:
        if lo.shape[-1]%2:
            shape=list(lo.shape);shape[-1]=1
            lo=np.concatenate((lo,np.zeros(shape)),axis=-1)
            hi=np.concatenate((hi,np.zeros(shape)),axis=-1)
        lo=dn(lo[...,::2]+lo[...,1::2]);hi=up(hi[...,::2]+hi[...,1::2])
    return I(lo[...,0],hi[...,0])

def absolute(x):
    return I(np.maximum(0,np.where(x.lo>0,x.lo,np.where(x.hi<0,-x.hi,0))),
             np.maximum(np.abs(x.lo),np.abs(x.hi)))

def bins(rng,shape,bits=48):
    k=rng.integers(0,2**bits,size=shape,dtype=np.int64)
    return I(k.astype(float)/2**bits,(k+1).astype(float)/2**bits)

def moments(a):
    a=np.asarray(a,dtype=np.int64);n=int(a.size)
    # The dyadic endpoints are exact. Integer reductions make the saved moments
    # independent of NumPy's floating reduction and cancellation behavior.
    s=sum(map(int,a));s2=sum(int(v)*int(v) for v in a)
    mean=F(s,n*2**32);variance=F(n*s2-s*s,n*(n-1)*2**64)
    return {'n':n,'sum_integer':str(s),'sum_square_integer':str(s2),
            'mean_exact':str(mean),'variance_exact':str(variance)}

def quantize_interval(a):
    # Multiplication by a power of two is exact for these finite normal inputs.
    lo=np.floor(a.lo*2**32).astype(np.int64)
    hi=np.ceil(a.hi*2**32).astype(np.int64)
    if np.any(lo>hi):raise AssertionError('Reversed endpoints')
    return lo,hi

def radius(variance,n,width,family,alpha=F(1,20)):
    with localcontext() as ctx:
        ctx.prec=90
        D=lambda q:Decimal(q.numerator)/Decimal(q.denominator)
        log=(D(F(4*family)/alpha)).ln().next_plus()
        v=D(F(variance)).next_plus();w=D(F(width)).next_plus()
        z=(2*v*log/Decimal(n)).sqrt().next_plus()+7*w*log/(3*Decimal(n-1))
        return fup(F(z.next_plus()))

def confidence(lo,hi,cost_upper,family,margin=F(1,200)):
    ml,mh=moments(lo),moments(hi);n=ml['n']
    # Rounding to 2^-32 enlarges each signed support endpoint by at most 2^-32.
    width=2*F(cost_upper)+F(2,2**32)
    rl=radius(F(ml['variance_exact']),n,width,family)
    rh=radius(F(mh['variance_exact']),n,width,family)
    lower=-fup(-F(ml['mean_exact'])+F(rl));upper=fup(F(mh['mean_exact'])+F(rh))
    classification=('lower-cost' if upper<0 else 'higher-cost' if lower>0 else 'sign-unresolved')
    return {'lower':lower,'upper':upper,'margin':float(margin),
            'within_margin':lower>=-float(margin) and upper<=float(margin),
            'sign':classification,'lower_endpoint_moments':ml,'upper_endpoint_moments':mh,
            'support_width_exact':str(width),'radius_lower':rl,'radius_upper':rh,
            'family':family,'alpha_exact':'1/20','endpoint_quantization_bits':32}

def save_npz(path,**arrays):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as f:
        np.savez_compressed(f,**arrays);f.flush();os.fsync(f.fileno())
    return hfile(path)
