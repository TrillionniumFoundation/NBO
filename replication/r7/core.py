"""R7 finite-model oracles. R4--R6 are immutable, explicitly imported inputs."""
from __future__ import annotations
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import sys, json, time, hashlib, platform
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'replication/r6'),str(ROOT/'replication/r5'),str(ROOT/'replication/r4')]
from transport import Mixture, restrict, bernstein_value, envelope_certificate
from kernel_certificate import continuation
import contracts as c
OUT=ROOT/'replication/r7/output';OUT.mkdir(parents=True,exist_ok=True)
def serial(x):
    if isinstance(x,dict):return {str(k):serial(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [serial(v) for v in x]
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    return x
def save(name,data):
    (OUT/name).write_text(json.dumps(serial(data),indent=2,allow_nan=False)+'\n')
def build():return Mixture(c.Economy(correlation=-.25),c.Economy(correlation=.25))
def mask(mix,n,adjust=True,sign=None):
    if adjust and (n>0 or sign is None):return True
    cache=getattr(mix,'_r7_masks',{})
    key=(n,adjust,sign if n==0 else None)
    if key in cache:return cache[key]
    e=mix.e[0]
    ok=np.ones(len(e.menu),bool) if adjust else np.abs(e.menu[:,1])<=1e-14
    if n==0 and sign is not None:ok &= e.menu[:,2]>0 if sign=='positive' else e.menu[:,2]<=0
    ok=np.broadcast_to(ok,(e.ns,len(e.menu)))
    if e.extra:
        aa=e.extra[n].actions
        extra=np.ones(aa.shape[:2],bool) if adjust else np.abs(aa[:,:,1])<=1e-14
        if n==0 and sign is not None:extra &= aa[:,:,2]>0 if sign=='positive' else aa[:,:,2]<=0
        ok=np.concatenate((ok,extra),axis=1)
    cache[key]=ok;mix._r7_masks=cache
    return ok

def solve(mix,t,d,adjust=True,sign=None):
    v=np.empty((mix.steps+1,mix.ns));v[-1]=mix.terminal
    p=np.empty((mix.steps,mix.ns),np.int32)
    for n in range(mix.steps-1,-1,-1):
        q=(1-t)*mix.q(0,n,v[n+1],d)+t*mix.q(1,n,v[n+1],d)
        q=np.where(mask(mix,n,adjust,sign),q,-np.inf)
        p[n]=q.argmax(1);v[n]=q[np.arange(mix.ns),p[n]]
    return {'value':v,'policy':p}

def chord(mix,a,b,va,vb):
    """Four kernel applications per nontrivial layer; skip known zero layers."""
    zero=np.zeros(mix.ns);M=[zero]*(mix.steps+1)
    for n in range(mix.steps-2,-1,-1):
        diff=vb[n+1]-va[n+1]
        D=(b-a)*(continuation(mix,0,n,diff)-continuation(mix,1,n,diff))
        if n<mix.steps-2:
            k0=continuation(mix,0,n,M[n+1]);k1=continuation(mix,1,n,M[n+1])
            D+=np.maximum((1-a)*k0+a*k1,(1-b)*k0+b*k1)
        M[n]=np.maximum(D.max(1),0)
    return M

class CompactUpper:
    """Store only the H-1 nonzero correction vectors; expand one date on demand.
    Endpoint values are shared references. Certificate timings include expansion.
    """
    def __init__(self,mix,va,vb,M):
        self.steps=mix.steps;self.terminal=mix.terminal
        self.va=va;self.vb=vb;self.M=tuple(M[:max(0,mix.steps-1)])
    def __len__(self):return self.steps+1
    def __getitem__(self,n):
        if n<0:n+=len(self)
        if not 0<=n<len(self):raise IndexError(n)
        if n==self.steps:return self.terminal[None,:]
        h=self.steps-n;j=np.arange(h+1)[:,None]
        co=(1-j/h)*self.va[n]+j/h*self.vb[n]
        if h>1:co+=j*(h-j)/(h*(h-1))*self.M[n]
        return co
    def __iter__(self):
        for n in range(len(self)):yield self[n]

def expand(mix,va,vb,M):return CompactUpper(mix,va,vb,M)

def count(mix,a,b,d,va,vb,adjust=True,sign=None):
    """Localized count recursion, same action before the hidden endpoint draw.
    Cache neighboring count continuations, never all action arrays at once.
    Exact endpoint coefficients are shared with the anchor solves.
    """
    co=[None]*(mix.steps+1);co[-1]=mix.terminal[None,:]
    for n in range(mix.steps-1,-1,-1):
        h=mix.steps-n;z=np.empty((h+1,mix.ns));z[0]=va[n];z[h]=vb[n]
        if h>1:
            allowed=mask(mix,n,adjust,sign)
            q0=mix.q(0,n,co[n+1][0],d);q1=mix.q(1,n,co[n+1][0],d)
            previous=(1-b)*q0+b*q1
            for j in range(1,h):
                q0=mix.q(0,n,co[n+1][j],d);q1=mix.q(1,n,co[n+1][j],d)
                qa=(1-a)*q0+a*q1
                z[j]=np.where(allowed,(1-j/h)*qa+j/h*previous,-np.inf).max(1)
                previous=(1-b)*q0+b*q1
        co[n]=z
    return co

def rectangular(mix,a,b,d):
    v=np.empty((mix.steps+1,mix.ns));v[-1]=mix.terminal
    for n in range(mix.steps-1,-1,-1):
        q0=mix.q(0,n,v[n+1],d);q1=mix.q(1,n,v[n+1],d)
        v[n]=np.maximum((1-a)*q0+a*q1,(1-b)*q0+b*q1).max(1)
    return [np.broadcast_to(v[n],(mix.steps-n+1,mix.ns)).copy() for n in range(mix.steps+1)]


def classes(mix,t,d,adjust=True):
    v=np.empty((mix.steps+1,mix.ns));v[-1]=mix.terminal
    p=np.empty((mix.steps,mix.ns),np.int32)
    for n in range(mix.steps-1,-1,-1):
        q=(1-t)*mix.q(0,n,v[n+1],d)+t*mix.q(1,n,v[n+1],d)
        q=np.where(mask(mix,n,adjust),q,-np.inf)
        p[n]=q.argmax(1);v[n]=q[np.arange(mix.ns),p[n]]
    out={}
    for sign in ('positive','nonpositive'):
        pp=p.copy();vv=v.copy();qq=np.where(mask(mix,0,adjust,sign),q,-np.inf)
        pp[0]=qq.argmax(1);vv[0]=qq[np.arange(mix.ns),pp[0]]
        out[sign]={'value':vv,'policy':pp}
    return out
