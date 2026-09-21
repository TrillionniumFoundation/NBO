"""Joint refinement and stopped-boundary tests; no continuum error is guessed.
The manufactured control benchmark has a verified nonlinear exact solution.
The NDU path reuses R4 primitives with a separately assembled sparse operator.
"""
from __future__ import annotations
import sys, json, math, time, argparse, resource
from pathlib import Path
from dataclasses import asdict
import numpy as np
from scipy.sparse import csr_matrix
from numpy.polynomial.hermite import hermgauss
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'revisions/2026-09-21-r4/replication'))
import solver as old
OUT=Path(__file__).resolve().parents[1]/'results'

def sparse_ndu(cfg):
    """Cache interpolation weights once; algebraically identical to R4 Q."""
    start=time.perf_counter(); s,bd=old.states(cfg); aa=old.actions(cfg); S=len(s); A=len(aa)
    hit,frac,_=old.transition_numpy(s[:,None,:],aa[None,:,:],cfg)
    disc=np.exp(-cfg.rho*cfg.dt*frac); surv=frac>=1-1e-12
    flow=aa[None,:,0]**(1-s[:,0,None])/(1-s[:,0,None])-.5*cfg.k*aa[None,:,1]**2
    integ=-np.expm1(-cfg.rho*cfg.dt*frac)/cfg.rho
    r0=(integ*flow[:,:,None]+disc*(~surv)*old.settlement(cfg.dt*frac,hit,cfg)).mean(-1)
    rt=(disc*(~surv)*cfg.fee).mean(-1)
    rb=(integ*.5*aa[None,:,1,None]**2).mean(-1)
    re=(~surv).mean(-1)
    f=(hit-[cfg.ulo,cfg.xlo])/[cfg.uhi-cfg.ulo,cfg.xhi-cfg.xlo]*[cfg.nu-1,cfg.nx-1]
    iu=np.floor(f[...,0]).astype(np.int32).clip(0,cfg.nu-2); ix=np.floor(f[...,1]).astype(np.int32).clip(0,cfg.nx-2)
    wu=np.clip(f[...,0]-iu,0,1); wx=np.clip(f[...,1]-ix,0,1)
    ids=np.stack([iu*cfg.nx+ix,iu*cfg.nx+ix+1,(iu+1)*cfg.nx+ix,(iu+1)*cfg.nx+ix+1],-1)
    weights=np.stack([(1-wu)*(1-wx),(1-wu)*wx,wu*(1-wx),wu*wx],-1)
    weights *= surv[...,None]*math.exp(-cfg.rho*cfg.dt)/4
    P=csr_matrix((weights.reshape(-1),ids.reshape(-1),np.arange(0,S*A*16+1,16,dtype=np.int64)),shape=(S*A,S))
    P.eliminate_zeros(); P.sum_duplicates()
    rng=np.random.default_rng(82); v=rng.normal(size=S)
    agreement=float(np.max(abs((P@v).reshape(S,A)+r0+.3*rt-old.q_numpy(s[:,None,:],aa[None,:,:],v,.3,cfg))))
    del hit,frac,disc,surv,integ,f,iu,ix,wu,wx,ids,weights
    V=np.empty((cfg.n+1,S)); pol=np.empty((cfg.n,S),np.int32); B=np.zeros_like(V); E=np.zeros_like(V)
    V[-1]=old.settlement(cfg.T,s,cfg)
    for n in reversed(range(cfg.n)):
        q=r0+(n*cfg.dt)*rt+(P@V[n+1]).reshape(S,A); j=q.argmax(-1); rows=np.arange(S)*A+j
        V[n]=q[np.arange(S),j]; V[n,bd]=old.settlement(n*cfg.dt,s[bd],cfg); pol[n]=j
        # Calculate only selected-action transitions for auxiliary quantities.
        Ps=P[rows]
        B[n]=rb[np.arange(S),j]+Ps@B[n+1]; B[n,bd]=0
        E[n]=re[np.arange(S),j]+(Ps@E[n+1])*math.exp(cfg.rho*cfg.dt); E[n,bd]=1
    tag=f'coupled_n{cfg.n}_u{cfg.nu}_x{cfg.nx}_a{cfg.na}_k{cfg.k:g}'
    center=np.array([[2.,1.25]]); idx=int(np.argmin(np.sum((s-center)**2,axis=-1)))
    result=dict(tag=tag,config=asdict(cfg),dt=cfg.dt,
        h2_over_dt=max(((cfg.uhi-cfg.ulo)/(cfg.nu-1))**2,((cfg.xhi-cfg.xlo)/(cfg.nx-1))**2)/cfg.dt,
        action_mesh_max=1.3/(cfg.na-1),center_value=float(old.interp(V[0],center,cfg)[0]),
        center_budget=float(old.interp(B[0],center,cfg)[0]),center_exit=float(old.interp(E[0],center,cfg)[0]),
        nearest_node=s[idx].tolist(),nearest_node_action=aa[pol[0,idx]].tolist(),
        operator_agreement_max=agreement,seconds=time.perf_counter()-start,
        sparse_nnz=P.nnz,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        continuum_error_bound=None,continuous_boundary_regular_for_all_actions=False)
    assert agreement<1e-11
    np.savez_compressed(OUT/(tag+'.npz'),V=V,policy_indices=pol,B=B,exit_probability=E,actions=aa)
    (OUT/(tag+'.json')).write_text(json.dumps(result,indent=2)); print(json.dumps(result),flush=True)
    return result

def bridge_survival(x,y,variance):
    """Brownian bridge interval survival: killed/free Gaussian density ratio.
    The image series uses k=-3,...,3. Values are clipped only for roundoff.
    At the tested largest variance .01, omitted Gaussian images are negligible.
    """
    out=np.zeros(np.broadcast_shapes(x.shape,y.shape)); delta=y-x
    for k in range(-3,4):
        out += np.exp(-((delta+2*k)**2-delta**2)/(2*variance))
        out -= np.exp(-((y+x+2*k)**2-delta**2)/(2*variance))
    return np.where((y>0)&(y<1),np.clip(out,0,1),0.)

def manufactured(N,mode='bridge'):
    start=time.perf_counter(); dt=1/N; nx=2*N+1; na=N//2+1; nq=4+2*int(math.log2(N//16+1))
    x=np.linspace(0,1,nx); aa=np.linspace(-1,1,na); sigma=.4; kappa=.2
    z,w=hermgauss(nq); z=np.sqrt(2)*z; w=w/math.sqrt(math.pi)
    y=x[:,None,None]+aa[None,:,None]*dt+sigma*math.sqrt(dt)*z[None,None,:]
    xx=np.broadcast_to(x[:,None,None],y.shape)
    survival=((y>0)&(y<1)).astype(float) if mode=='endpoint' else bridge_survival(xx,y,sigma*sigma*dt)
    f=np.clip(y,0,1)*(nx-1); ix=np.floor(f).astype(np.int32).clip(0,nx-2); wx=f-ix
    ids=np.stack([ix,ix+1],-1); weights=np.stack([1-wx,wx],-1)*survival[...,None]*w[None,None,:,None]
    P=csr_matrix((weights.reshape(-1),ids.reshape(-1),np.arange(0,nx*na*nq*2+1,nq*2)),shape=(nx*na,nx))
    P.eliminate_zeros(); P.sum_duplicates()
    V=np.empty((N+1,nx)); pol=np.empty((N,nx)); V[-1]=math.exp(-1)*np.sin(math.pi*x)
    for n in reversed(range(N)):
        t=n*dt; v=math.exp(-t)*np.sin(math.pi*x); vx=math.exp(-t)*math.pi*np.cos(math.pi*x)
        # -v_t-.5*sigma^2*v_xx-sup_a(a v_x-a^2/(2kappa)); a*=kappa*v_x lies strictly inside A.
        f0=v+.5*sigma*sigma*math.pi**2*v-.5*kappa*vx*vx
        q=dt*(f0[:,None]-aa[None,:]**2/(2*kappa))+(P@V[n+1]).reshape(nx,na)
        j=q.argmax(-1); V[n]=q[np.arange(nx),j]; V[n,[0,-1]]=0; pol[n]=aa[j]
        # Boundary controls are never enacted; extend nearest interior control for interpolation.
        pol[n,0]=pol[n,1]; pol[n,-1]=pol[n,-2]
    exact=np.exp(-np.arange(N+1)[:,None]*dt)*np.sin(math.pi*x)[None,:]
    astar=kappa*np.exp(-np.arange(N)[:,None]*dt)*math.pi*np.cos(math.pi*x)[None,:]
    node_action_error=float(np.max(abs(pol-astar)))
    uniform_action_error=node_action_error+kappa*math.pi*dt+kappa*math.pi**3*(1/(nx-1))**2/8
    result=dict(N=N,nx=nx,na=na,quadrature_points=nq,mode=mode,dt=dt,h2_over_dt=(1/(nx-1))**2/dt,
        all_time_value_sup_error=float(np.max(abs(V-exact))),t0_value_sup_error=float(np.max(abs(V[0]-exact[0]))),
        policy_node_sup_error=node_action_error,
        continuous_interpolated_policy_loss_upper=uniform_action_error**2/(2*kappa),
        bound_scope='Exact benchmark only: continuous Ito verification and a globally valid action interpolation bound',
        seconds=time.perf_counter()-start)
    tag=f'manufactured_n{N}_{mode}'; np.savez_compressed(OUT/(tag+'.npz'),V=V,policy=pol,exact=exact,actions_exact=astar)
    (OUT/(tag+'.json')).write_text(json.dumps(result,indent=2)); print(json.dumps(result),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--task',choices=['manufactured','ndu'],default='manufactured')
    p.add_argument('--n',type=int,default=16); p.add_argument('--nu',type=int,default=13); p.add_argument('--nx',type=int,default=16)
    p.add_argument('--na',type=int,default=3); p.add_argument('--k',type=float,default=2)
    p.add_argument('--mode',choices=['bridge','endpoint'],default='bridge'); a=p.parse_args(); OUT.mkdir(exist_ok=True)
    if a.task=='manufactured': manufactured(a.n,a.mode)
    else: sparse_ndu(old.Config(n=a.n,nu=a.nu,nx=a.nx,na=a.na,k=a.k))
