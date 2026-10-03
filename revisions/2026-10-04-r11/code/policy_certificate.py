"""Policy-specific capital bounds for innovation-driven sampled controllers.

The simulated controller is part of the specification: its internal Euler
state receives clipped Brownian innovations; the economic state follows the
original continuous diffusion and is NOT stopped or clipped. The certificate
is pointwise in the declared initial state, probabilistic over a fresh noise
bank, and conditional on the documented sampling/binary64 contract.
"""
from __future__ import annotations
import argparse, functools, hashlib, json, math, sys, time
from pathlib import Path
import numpy as np
import torch
from bellman_study import ROOT,R,load,P,CHI,Actor,Critic,greedy
from tube_certificate import I,up,down,exp_i,log_i,sqrt_i,schedule_i,coupling,spectral_bound,enclosure
from fast_arithmetic import tanh_kernel,log_kernel
U=np.finfo(np.float64).eps


def sum_axis(z:I,axis=-1)->I:
    lo=np.moveaxis(z.lo,axis,-1);hi=np.moveaxis(z.hi,axis,-1)
    while lo.shape[-1]>1:
        if lo.shape[-1]%2:
            shape=lo.shape[:-1]+(1,);lo=np.concatenate([lo,np.zeros(shape)],-1);hi=np.concatenate([hi,np.zeros(shape)],-1)
        lo=down(lo[...,::2]+lo[...,1::2]);hi=up(hi[...,::2]+hi[...,1::2])
    return I(lo[...,0],hi[...,0])


def mean_i(z:I,axis=-1)->I:return sum_axis(z,axis)/z.lo.shape[axis]

def nonnegative(x):return I(np.maximum(0.,x.lo),np.maximum(0.,x.hi))

def sqrt_nonnegative(x):
    return sqrt_i(I(np.maximum(0.,x.lo),np.maximum(1e-100,x.hi)))

def gamma(n):return float(up(n*U/(1-n*U)))


def safe_tanh(x):
    """Uniform absolute error < 2^-34 under the stated binary64 contract.

    exp(2x) is range-reduced by 512 and evaluated by degree-14 Horner
    followed by nine squarings. Saturation at |x|=20 contributes <2 exp(-40).
    No numerical accuracy assumption on a platform tanh/exp is used here.
    """
    x=np.asarray(x,dtype=np.float64)
    if tanh_kernel is not None:return tanh_kernel(x.ravel()).reshape(x.shape)
    x=np.clip(x,-20.,20.);r=x/256.
    z=np.full_like(r,1/math.factorial(14))
    for k in range(13,-1,-1):z=z*r+1/math.factorial(k)
    for _ in range(9):z=z*z
    return 1-2/(1+z)


def safe_log(x):
    """Uniform absolute error < 2^-34 on the permitted consumption interval."""
    x=np.asarray(x,dtype=np.float64)
    if np.any(x<=0) or not np.isfinite(x).all():raise ValueError('log domain')
    if log_kernel is not None:return log_kernel(x.ravel()).reshape(x.shape)
    m,e=np.frexp(x);q=(2*m-1)/(2*m+1);q2=q*q
    p=np.full_like(q,1/35)
    for j in range(16,-1,-1):p=1/(2*j+1)+q2*p
    q0=1/3;p0=1/35
    for j in range(16,-1,-1):p0=1/(2*j+1)+q0*q0*p0
    return 2*q*p+(e-1)*(2*q0*p0)


def weights(nt:int,sub:int=64):
    if nt<2 or nt&(nt-1) or sub<2 or sub&(sub-1):raise ValueError('use dyadic grids')
    h=P['T']/nt;edges=np.arange(nt+1)*h;left=edges[:-1]
    rho=I(P['discount']);T=I(P['T']);eta=I(P['adjustment'])
    dl=exp_i(-rho*I(left));dr=exp_i(-rho*I(edges[1:]));A=(dl-dr)/rho
    B=A/rho+(1-1/rho)*exp_i(-rho*T)*I(h)
    ll=left[:,None]+np.arange(sub)[None,:]*(h/sub);rr=ll+h/sub;t=I(ll,rr)
    m=schedule_i(t);disc=exp_i(-rho*t);w=(1-exp_i(-rho*(T-t)))/rho+exp_i(-rho*(T-t))
    C=sum_axis(disc*(log_i(m)-w*m-eta*m.square()/2)*(h/sub))
    M=sum_axis(m*(h/sub));J=sum_axis(disc*w*(t-I(left[:,None]))*(h/sub))
    center=schedule_i(I(left))
    return dict(h=h,nt=nt,A=A,B=B,C=C,M=M,J=J,center=center,sub=sub)


def midpoint(x):return (x.lo+x.hi)/2

def radius(x):return np.maximum(up(midpoint(x)-x.lo),up(x.hi-midpoint(x)))


def constants(d,nt,epsilon,y0,wt=None,zcap=10.,clip_u=8.):
    """Conservative global analytic coefficients, separately from sample data."""
    wt=wt or weights(nt);h=wt['h'];T=P['T'];rho=P['discount'];lam=P['coupling'];eta=P['adjustment']
    B=coupling(d);sp=spectral_bound(B);beta=float((I(lam)*I(sp['norm_upper'])).hi)
    q=I(P['idiosyncratic_sigma']).square()*sum_axis(I(B).square(),1)+I(P['common_sigma']).square()*sum_axis(I(B),1).square()
    G=float((I(lam)*sqrt_i(mean_i(q))).hi)
    Q=float((I(lam)*sqrt_i(mean_i(q.square()))/2).hi) # |tanh''| <= 1
    s0=float(sqrt_nonnegative(mean_i((I(y0)-mean_i(I(y0))).square())).hi)
    c=float(P['productivity']-(P['idiosyncratic_sigma']**2+P['common_sigma']**2)/2)
    mstart=schedule_i(I(0.));mend=schedule_i(I(T))
    alo=float(down(mstart.lo-epsilon));ahi=float(up(mend.hi+epsilon))
    if alo<=P['lower'] or ahi>=P['upper']:raise ValueError('radius outside the primitive box')
    speed=1. # |m0'| <= 1 for these coefficients; checked independently in tests.
    # Bounded innovations make a deterministic forward roundoff budget possible.
    M=max(abs(c-alo),abs(c-ahi))+lam
    state_cap=2*(float(np.max(abs(y0)))+M*T+(P['idiosyncratic_sigma']+P['common_sigma'])*zcap*T/math.sqrt(h)+1)
    doterr=gamma(d+2)*state_cap*np.abs(B).sum(1).max()
    ferr=lam*(2.**-34+doterr)+gamma(8)*(abs(c)+lam+ahi)
    noise_cap=(P['idiosyncratic_sigma']+P['common_sigma'])*zcap*math.sqrt(h)
    step_round=h*ferr+gamma(16)*(state_cap+h*M+noise_cap)+8*U*noise_cap
    path_round=nt*step_round*math.exp(beta*T)
    if path_round>=1:raise ArithmeticError('roundoff bootstrap bound failed')
    # E(Z-clip(Z))^2 <= E[Z^2 1{|Z|>zcap}] <= 2 phi(zcap)(zcap+1/zcap).
    tail_variance=2*math.exp(-zcap*zcap/2)/math.sqrt(2*math.pi)*(zcap+1/zcap)
    clipped_noise_error=math.sqrt(P['idiosyncratic_sigma']**2+P['common_sigma']**2)*math.sqrt(T*tail_variance)*math.exp(beta*T)
    # The scalar quadratures use outward enclosures; the nominal M0 is its midpoint.
    mquad=float(sum_axis(I(radius(wt['M']))).hi)
    Amax=float(sum_axis(wt['A']).hi);Bmax=float(sum_axis(wt['B']).hi)
    quadrature=float(sum_axis(I(radius(wt['C']))).hi)
    quadrature+=float(sum_axis(I(radius(wt['A']))).hi)*(max(abs(math.log(alo)),abs(math.log(ahi)))+eta*ahi*ahi/2)
    quadrature+=float(sum_axis(I(radius(wt['B']))).hi)*(2*lam+ahi)
    evaluation_round=(2.**-34+gamma(4*d+16)*(1+abs(math.log(alo))+ahi**2))*Amax
    evaluation_round+=2*Bmax*ferr+gamma(32*nt+64)*(1+Amax*max(abs(math.log(alo)),abs(math.log(ahi)))+Bmax*(2*lam+ahi)+eta*Amax*ahi**2/2)
    evaluation_round+=32*CHI*gamma(4*d+20)*state_cap**2
    stat_error=float(up(quadrature+evaluation_round))
    Jsum=float(sum_axis(wt['J']).hi)
    def bias(eps,mquad_error=0.):
        lo=float(down(mstart.lo-eps));hi=float(up(mend.hi+eps));Mb=max(abs(c-lo),abs(c-hi))+lam
        K=float(up(beta*Mb+Q))
        t=np.arange(nt)*h
        ui=I(h)*exp_i(I(beta)*I(t))*(I(K)*I(t)/2+I(G)*sqrt_nonnegative(I(t)/3))
        u=ui.hi
        uT=float((I(h)*exp_i(I(beta)*I(T))*(I(K)*I(T)/2+I(G)*sqrt_i(I(T)/3))).hi)
        extra=float((I(path_round)+I(clipped_noise_error)+exp_i(I(beta)*I(T))*I(mquad_error)).hi)
        u=up(u+extra);uT=float(up(uT+extra))
        prod=beta*float(sum_axis(wt['B']*I(u)).hi)+K*Jsum
        spread=float((I(s0)+(I(lam)+I(eps))*I(T)+I(P['idiosyncratic_sigma'])*sqrt_i((1-I(1)/d)*I(T))).hi)
        end=float((I(CHI)*exp_i(-I(rho)*I(T))*I(uT)*(2*I(spread)+I(uT))).hi)
        return dict(total=float(up(prod+end+1e-12)),production=float(up(prod)),terminal=float(up(end)),strong_error=float(up(uT)),K=K,spread_bound=spread)
    ba=bias(epsilon);bb=bias(0.,mquad)
    total_bias=float(up(ba['total']+bb['total']+stat_error))
    # A deterministic envelope plus a Gaussian concentration tail for the
    # projected clipped-noise vector gives a rigorous clipping-bias bound.
    eps_eff=epsilon+speed*h+float(radius(wt['M']).max())/h+2*step_round/h
    if float(mstart.lo)-eps_eff<=0:raise ValueError('effective radius violates log domain')
    times=np.arange(nt)*h;D=eps_eff*np.expm1(beta*times)/beta;DT=eps_eff*math.expm1(beta*T)/beta
    prodmax=beta*float(sum_axis(wt['B']*I(D)).hi)
    rmax=.5*eps_eff**2*(1/(float(mstart.lo)-eps_eff)**2+eta)*Amax
    C=prodmax+rmax+CHI*math.exp(-rho*T)*(DT**2+2*DT*(s0+lam*T+nt*step_round))+stat_error
    An=2*CHI*math.exp(-rho*T)*DT*P['idiosyncratic_sigma']*math.sqrt(T/d)
    clip=float(up(C+An*(math.sqrt(d-1)+clip_u)+1e-10))
    tail=float(up(An*math.exp(-clip_u*clip_u/2)/clip_u+1e-16))
    anchor=enclosure(B,0.,s0,16384,sp)
    return dict(dimension=d,steps=nt,epsilon=epsilon,initial_state=list(map(float,y0)),initial_spread_upper=s0,beta=beta,G=G,Q=Q,
      bias_upper=total_bias,actor_bias=ba,anchor_bias=bb,quadrature_and_statistic_roundoff=stat_error,
      clipping_threshold=clip,clipping_bias=tail,clip_u=clip_u,gaussian_cap=zcap,
      forward_roundoff=path_round,normal_clipping_strong_error=clipped_noise_error,state_cap=state_cap,
      scalar_M0_quadrature=mquad,spectral=sp,anchor_upper=anchor['anchor_regret'][1],
      arithmetic_backend=('numba-polynomial' if tanh_kernel is not None else 'numpy-polynomial'),
      arithmetic_contract='binary64 round-to-nearest and standard dot forward error; proved polynomial tanh/log error budgets; ideal iid Gaussian innovations rounded within machine error; not machine-formal RNG verification',
      scope='fixed initial state; original continuous capital economy; innovation-driven sampled controller; not continuously observed-state feedback')


def empirical_lower(values,clip,bias,tail,family_size=1000,alpha=.05):
    x=np.asarray(values,dtype=float)
    if x.ndim!=1 or len(x)<2 or not np.isfinite(x).all():raise ValueError('invalid paired samples')
    y=np.clip(x,-clip,clip);n=len(y);center=float(y.mean())
    mu=mean_i(I(y));v=sum_axis((I(y)-I(center)).square())/(n-1)
    ell=log_i(I(2*family_size/alpha))
    margin=sqrt_nonnegative(2*v*ell/n)+I(float(up(14*clip)))*ell/(3*(n-1))
    lower=I(float(mu.lo))-I(float(margin.hi))-I(bias)-I(tail)
    upper=I(float(mu.hi))+I(float(margin.hi))+I(bias)+I(tail)
    return dict(mean=float(x.mean()),sample_sd=float(x.std(ddof=1)),clipped_mean=[float(mu.lo),float(mu.hi)],
      empirical_bernstein_margin=float(margin.hi),lower=float(lower.lo),upper=float(upper.hi),
      paths=n,clipped_payoffs=int(np.count_nonzero(x!=y)),family_size=family_size,alpha=alpha,
      confidence='simultaneous two-sided bounds use a further factor two in family_size when requested; this call allocates alpha/family_size to each one-sided statement')


def evaluate(path:Path,steps=1024,paths=8192,radius_scale=1.,shift=0.,spread=0.,test_seed=9100000,out:Path|None=None,profile="linear"):
    total_start=time.perf_counter()
    out=out or R/'results';out.mkdir(parents=True,exist_ok=True)
    a,c,state=load(path);d=state['dimension'];eps=state['epsilon']*radius_scale
    B=coupling(d);y0=np.full(d,shift)
    if spread:
        if profile=='student3':
            from scipy.stats import t as student
            v=student.ppf((np.arange(d)+.5)/d,3)
        elif profile=='linear':v=np.linspace(-1,1,d)
        else:raise ValueError('unknown initial profile')
        v-=v.mean();y0+=spread*v/np.sqrt(np.mean(v*v))
    wt=weights(steps);con=constants(d,steps,eps,y0,wt);h=wt['h']
    Am,Bm,Cm,Mm=[midpoint(wt[k]) for k in ['A','B','C','M']]
    lo=up(wt['center'].hi-eps);hi=down(wt['center'].lo+eps)
    za=np.tile(y0,(paths,1));z0=za.copy();prod=np.zeros(paths);loss=np.zeros(paths)
    rng=np.random.default_rng(test_seed+d);noise_hash=hashlib.sha256();action_sat=0;outside=0;nonfinite=0;max_state=0.;start=time.perf_counter();noise_clipped=0
    c0=P['productivity']-(P['idiosyncratic_sigma']**2+P['common_sigma']**2)/2
    for k in range(steps):
        xx=np.concatenate([np.full((paths,1),k*h),za],1)
        with torch.no_grad():proposal=a(torch.from_numpy(xx)).numpy()
        center=float(midpoint(wt['center'])[k]);proposal=center+radius_scale*(proposal-center)
        nonfinite+=int((~np.isfinite(proposal)).sum());proposal=np.where(np.isfinite(proposal),proposal,center)
        m=np.maximum(lo[k],np.minimum(hi[k],proposal))
        if eps>0:action_sat+=int((abs(m-center)>.99*eps).sum())
        outside+=int(((za< -1.5)|(za>.5)).any(1).sum())
        fa=P['coupling']*safe_tanh(za@B.T);f0=P['coupling']*safe_tanh(z0@B.T)
        ma=m.mean(1);prod+=Bm[k]*(fa-f0).mean(1)
        loss+=Cm[k]-Am[k]*safe_log(m).mean(1)+Bm[k]*ma+P['adjustment']/2*Am[k]*ma*ma
        z=rng.standard_normal((paths,d+1));noise_hash.update(z.tobytes());noise_clipped+=int((abs(z)>10).sum());z=np.clip(z,-10.,10.)
        dw=math.sqrt(h)*(P['idiosyncratic_sigma']*z[:,:d]+P['common_sigma']*z[:,d:])
        za=za+h*(c0+fa-m)+dw;z0=z0+h*(c0+f0)-Mm[k]+dw
        max_state=max(max_state,float(abs(za).max()),float(abs(z0).max()))
    va=((za-za.mean(1,keepdims=True))**2).mean(1);v0=((z0-z0.mean(1,keepdims=True))**2).mean(1)
    term=-CHI*math.exp(-P['discount']*P['T'])*(va-v0);raw=prod-loss+term
    bound=empirical_lower(raw,con['clipping_threshold'],con['bias_upper'],con['clipping_bias'],family_size=2000)
    ident=path.stem+f'_n{steps}_r{radius_scale:g}_mean{shift:g}_sd{spread:g}'+('' if profile=='linear' else '_'+profile)
    rawpath=out/(ident+'.npz');np.savez_compressed(rawpath,paired_gain=raw,production=prod,consumption_deficit=loss,terminal_gain=term,terminal_policy=za,terminal_anchor=z0)
    sim_seconds=time.perf_counter()-start
    bench=np.concatenate([np.full((256,1),.5),za[:256]],1)
    decision_start=time.perf_counter()
    for _ in range(12):
        with torch.no_grad():pp=a(torch.from_numpy(bench)).numpy()
        mm=np.maximum(lo[steps//2],np.minimum(hi[steps//2],pp))
        _next=bench[:,1:]+h*(c0+P['coupling']*safe_tanh(bench[:,1:]@B.T)-mm)
    decision_seconds=(time.perf_counter()-decision_start)/12
    record=dict(id=ident,source_path=str(path.relative_to(ROOT)),weights_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
      dimension=d,method=state['method'],iteration=state['iteration'],steps=steps,paths=paths,radius_scale=radius_scale,shift=shift,spread=spread,profile=profile,
      bound=bound,constants=con,policy_regret_upper=float(up(con['anchor_upper']-bound['lower'])),
      seconds=time.perf_counter()-total_start,simulation_seconds=sim_seconds,decision_batch256_seconds=decision_seconds,action_saturation_frequency=action_sat/(steps*paths*d),outside_training_box_frequency=outside/(steps*paths),nonfinite_proposals=nonfinite,
      noise_seed=test_seed+d,noise_sha256=noise_hash.hexdigest(),noise_clipped=noise_clipped,max_internal_state=max_state,
      raw_sha256=hashlib.sha256(rawpath.read_bytes()).hexdigest(),
      interpretation='conditional statistical continuous-time bound for the explicitly deployed innovation controller; not a uniform PDE certificate, optimizer guarantee, or empirical calibration')
    if record['policy_regret_upper']<0:raise ArithmeticError('negative regret endpoint contradicts the confidence event')
    if max_state>con['state_cap']:raise AssertionError('arithmetic cap violated')
    (out/(ident+'.json')).write_text(json.dumps(record,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:record[k] for k in ['id','seconds','bound','policy_regret_upper']}),flush=True)
    return record

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('weights');p.add_argument('--steps',type=int,default=1024);p.add_argument('--paths',type=int,default=8192);p.add_argument('--development',action='store_true');a=p.parse_args()
    evaluate(Path(a.weights).resolve(),a.steps,a.paths,out=R/'development' if a.development else None)
