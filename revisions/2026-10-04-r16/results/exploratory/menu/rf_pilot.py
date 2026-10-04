"""Exploratory reuse of already published R15 replay; no new confirmation."""
from pathlib import Path
import json, time
import numpy as np

ROOT=Path('/workspace/scratch/f7129d88c27c/NBO/revisions/2026-10-04-r15/results/experiment/trials')

def read(d,seed):
    z=np.load(ROOT/f'd{d}_s{seed}/nbo/training/replay.npz')
    x=z['postdecision']; q=z['costate_replicates'].mean(0)
    base=-.06*np.exp(-.04)*(x[:,1:]-x[:,1:].mean(1,keepdims=True))
    return x,q-base

def features(x,w,b):
    tau=1-x[:,0]
    pre=x@w.T+b
    f=tau[:,None]/np.cosh(pre)**2
    g=f[:,:,None]*w[None,:,1:]
    # Same linear scalar lift is available as an unrestricted vector constant.
    gf=np.concatenate([g,tau[:,None,None]*np.broadcast_to(np.eye(x.shape[1]-1),(len(x),x.shape[1]-1,x.shape[1]-1))],axis=1)
    ff=np.column_stack([f,tau])
    return gf,ff

def scalar_fit(g,y,lam):
    n,p,d=g.shape
    a=g.transpose(0,2,1).reshape(n*d,p)/np.sqrt(n*d)
    yy=y.reshape(n*d)/np.sqrt(n*d)
    gram=a.T@a
    return np.linalg.solve(gram+lam*np.trace(gram)/p*np.eye(p),a.T@yy)

def vector_fit(f,y,lam):
    n,p=f.shape
    gram=f.T@f/n
    return np.linalg.solve(gram+lam*np.trace(gram)/p*np.eye(p),f.T@y/n)

out=[]
for d in [10,50]:
    x,y=read(d,1950831757)
    xx,yy=read(d,1818435806)
    xv,yv=xx[:512],yy[:512]
    xt,yt=xx[512:],yy[512:]
    for width in [32,128]:
        rng=np.random.default_rng(17041+d+width)
        w=rng.normal(size=(width,d+1))/np.sqrt(d)
        w[:,0]*=np.sqrt(d)
        b=rng.normal(size=width)
        g,f=features(x,w,b);gv,fv=features(xv,w,b);gt,ft=features(xt,w,b)
        for n in [128,512,1024]:
            best_s,best_v=None,None
            for lam in [1e-7,1e-5,1e-3,1e-1,1.,10.]:
                cs=scalar_fit(g[:n],y[:n],lam)
                cv=vector_fit(f[:n],y[:n],lam)
                vs=np.mean((gv.transpose(0,2,1)@cs-yv)**2)
                vv=np.mean((fv@cv-yv)**2)
                if best_s is None or vs<best_s[0]:best_s=vs,cs,lam
                if best_v is None or vv<best_v[0]:best_v=vv,cv,lam
            ps=gt.transpose(0,2,1)@best_s[1];pv=ft@best_v[1]
            row=dict(d=d,width=width,n=n,scalar_lambda=best_s[2],vector_lambda=best_v[2],
                     scalar_noisy_test_mse=float(np.mean((ps-yt)**2)),vector_noisy_test_mse=float(np.mean((pv-yt)**2)),
                     zero_noisy_test_mse=float(np.mean(yt**2)),
                     scalar_minus_vector_test_loss=float(np.mean((ps-yt)**2-(pv-yt)**2)))
            out.append(row);print(json.dumps(row),flush=True)
Path('/workspace/scratch/f7129d88c27c/r16-critic-design/RF_REPLAY_PILOT.json').write_text(json.dumps(dict(scope='exploratory reuse of existing R15 raw labels; not confirmation',rows=out),indent=2)+'\n')
