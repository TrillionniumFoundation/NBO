"""Shared exact arithmetic, provenance and immutable record I/O for R48."""
from __future__ import annotations
import hashlib, json, os, sys
from pathlib import Path
from fractions import Fraction as F
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
R=Path(__file__).resolve().parents[1]
P45=R.parent/'2026-10-07-r45'; P46=R.parent/'2026-10-07-r46'; P47=R.parent/'2026-10-08-r47'
sys.path.insert(0,str(P45/'code'))
import constructive as c
from interval import I
import numpy as np
BETA=F(15,16)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(path,obj):return c.write_new(Path(path),obj)
def read(path):return json.loads(Path(path).read_text())
def col(x,j):return I(x.lo[...,j],x.hi[...,j])
def stack(xs,axis=-1):return I(np.stack([x.lo for x in xs],axis),np.stack([x.hi for x in xs],axis))
def isum(x,axis=-1):
    # Explicit additions have a transparent outward-rounding account.
    y=np.moveaxis(x.lo,axis,-1);z=np.moveaxis(x.hi,axis,-1)
    out=I.point(np.zeros(y.shape[:-1]))
    for j in range(y.shape[-1]):out=out+I(y[...,j],z[...,j])
    return out

def abs_i(x):
    return I(np.where((x.lo<=0)&(x.hi>=0),0,np.minimum(abs(x.lo),abs(x.hi))),np.maximum(abs(x.lo),abs(x.hi)))

def cap(x):return F(1,8)+isum(x)*c.rat_i(F(1,8*x.lo.shape[-1]))
def costs(x,a,p,terminal=False):
    d=x.lo.shape[-1]
    target=isum((x-F(5,8)).square())*c.rat_i(F(4 if terminal else 2,d))
    rolled=I(np.roll(x.lo,-1,axis=-1),np.roll(x.hi,-1,axis=-1))
    imbalance=isum((x-rolled).square())*c.rat_i(F(1,4*d))
    shortage=(F(1,2)-isum(x)*c.rat_i(F(2,d))).clip(0,1).square()*2
    state=target+imbalance+shortage
    return state if terminal else state+p*a.square()+4*a.square().square()

def transition(x,a,z):
    d=x.lo.shape[-1];out=[]
    for j in range(d):
        u,v=col(x,j),col(x,(j+1)%d)
        out.append(F(1,16)+u/2+v/8+u*(1-v)/16+(F(1,2) if j%2==0 else F(1,4))*a+(z if j%2==0 else -z))
    return stack(out).clip(0,1)

def moduli(d,p):
    if d not in (2,3,4):raise ValueError('Study primitive dimensions are 2,3,4')
    return F(13,2*d),F(9,d),F(11,16),sum((F(1,2) if j%2==0 else F(1,4) for j in range(d)),F(0)),F(p,2)+F(1,4),F(1,8*d)
