"""Continuous-economy regret enclosure, not a sampled Bellman certificate.

Uses the inherited interval kernel without modifying it. All input binary64
coefficients denote exact reals under that kernel's documented contract.
"""
from __future__ import annotations
import hashlib, json, math, sys, time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'revisions/2026-09-29-r6/code'))
from interval_certificate import I, exp_i, log_i, down, up
P=dict(T=1.,discount=.04,productivity=.10,coupling=.15,
       idiosyncratic_sigma=.15,common_sigma=.10,adjustment=.2,lower=.02,upper=2.)
CHI=.03

def coupling(d:int)->np.ndarray:
    rng=np.random.default_rng(401+d);B=rng.normal(size=(d,d))
    return B/np.linalg.norm(B,axis=1,keepdims=True)

def sqrt_i(x:I)->I:
    if np.any(x.lo<0):raise ValueError('negative radicand')
    lo=np.maximum(0,down(np.sqrt(x.lo)));hi=up(np.sqrt(x.hi))
    for _ in range(16):
        bl=(lo>0)&(I(lo).square().hi>x.lo);bh=I(hi).square().lo<x.hi
        if not (bl.any() or bh.any()):return I(lo,hi)
        lo=np.where(bl,np.maximum(0,down(lo)),lo);hi=np.where(bh,up(hi),hi)
    raise ArithmeticError('square-root endpoint verification failed')

def sum_i(z:I)->I:
    lo=np.ravel(z.lo);hi=np.ravel(z.hi)
    if not len(lo):return I(0.)
    while len(lo)>1:
        if len(lo)%2:lo=np.r_[lo,0.];hi=np.r_[hi,0.]
        z=I(lo[::2],hi[::2])+I(lo[1::2],hi[1::2]);lo,hi=z.lo,z.hi
    return I(lo[0],hi[0])

def spectral_bound(B:np.ndarray)->dict:
    """Positive interval LDL pivots verify lambda*Id - B.T@B > 0.

    The SVD proposes lambda only; it is never accepted without this test.
    The Schur recurrence encloses the exact real recurrence at every pivot.
    """
    B=np.asarray(B,dtype=np.float64)
    if B.ndim!=2 or B.shape[0]!=B.shape[1] or not np.isfinite(B).all():
        raise ValueError('expected a finite square coupling matrix')
    d=len(B);g=I(np.zeros((d,d)))
    for row in B:g=g+I(row[:,None])*I(row[None,:])
    proposed=float(np.linalg.norm(B,2)**2)
    attempts=[]
    for j in range(8):
        lam=float(up(proposed*(1+10.**(-6+j))+10.**(-12+j)))
        A=I(lam)*I(np.eye(d))-g;pivots=[];ok=True
        for k in range(d):
            pivot=I(A.lo[k,k],A.hi[k,k]);pivots.append([float(pivot.lo),float(pivot.hi)])
            if pivot.lo<=0:ok=False;break
            if k+1<d:
                v=I(A.lo[k+1:,k],A.hi[k+1:,k])/pivot
                block=I(A.lo[k+1:,k+1:],A.hi[k+1:,k+1:])-pivot*I(v.lo[:,None],v.hi[:,None])*I(v.lo[None,:],v.hi[None,:])
                A.lo[k+1:,k+1:]=block.lo;A.hi[k+1:,k+1:]=block.hi
        attempts.append(dict(lambda_candidate=lam,positive_pivots=ok,pivots=pivots))
        if ok:
            return dict(dimension=d,lambda_upper=lam,norm_upper=float(sqrt_i(I(lam)).hi),
                        attempts=attempts,matrix_sha256=hashlib.sha256(B.tobytes()).hexdigest())
    raise ArithmeticError('unable to verify positive spectral majorant')

def schedule_i(t:I)->I:
    rho=I(P['discount']);tau=I(P['T'])-t
    e=exp_i(-rho*tau);w=(1-e)/rho+e
    return 2/(w+sqrt_i(w.square()+4*I(P['adjustment'])))

def exponential_integral(a:I,tau:I)->I:
    if a.lo<=0<=a.hi:
        # Integral of exp(a*v), v in [0,tau], by an enclosed power series.
        term=tau;out=term
        for k in range(1,25):term=term*a*tau/(k+1);out=out+term
        radius=I(float(a.absmax()))*I(float(tau.absmax()))
        if radius.hi>2:raise ValueError('series range')
        power=I(1.)
        for _ in range(25):power=power*radius
        error=exp_i(radius)*power*I(float(tau.absmax()))/math.factorial(26)
        return out+I(-float(error.hi),float(error.hi))
    return (exp_i(a*tau)-1)/a

def enclosure(B:np.ndarray,eps:float=.1,spread:float=0.,panels:int=16384,
              spectral:dict|None=None)->dict:
    if panels<2 or eps<0 or spread<0:raise ValueError('invalid certificate settings')
    start=time.perf_counter();d=len(B);spectral=spectral or spectral_bound(B)
    if spectral['matrix_sha256']!=hashlib.sha256(np.asarray(B,dtype=np.float64).tobytes()).hexdigest():
        raise ValueError('spectral certificate matrix mismatch')
    rho=I(P['discount']);T=I(P['T']);zeta=I(P['adjustment']);chi=I(CHI)
    beta=I(float((I(P['coupling'])*I(spectral['norm_upper'])).hi))
    sgrid=np.linspace(0,P['T'],panels+1);s=I(sgrid[:-1],sgrid[1:]);ds=I(sgrid[1:])-I(sgrid[:-1]);tau=T-s
    q=I(spread)+I(P['coupling'])*T+I(P['idiosyncratic_sigma'])*sqrt_i((1-I(1)/d)*T)
    K=beta*(exp_i(-rho*s)/rho*exponential_integral(beta-rho,tau)
         +(1-1/rho)*exp_i(-rho*T)*exponential_integral(beta,tau))
    K=K+2*chi*exp_i(-rho*T)*q*exp_i(beta*tau)
    K=I(np.maximum(0,K.lo),K.hi)
    m0=schedule_i(s);M=I(P['upper']);gap=M-m0
    if np.min(m0.lo)-eps<=P['lower'] or np.max(m0.hi)+eps>=P['upper']:
        raise ValueError('the certified tube is not strictly inside primitive actions')
    mu=2*(log_i(m0/M)+gap/m0)/gap.square()
    if np.min(mu.lo)<=0:raise ArithmeticError('nonpositive curvature enclosure')
    anchor=sum_i(exp_i(rho*s)*K.square()/(2*mu)*ds)
    curvature=1/(m0-I(eps)).square()+zeta
    loss=sum_i((I(eps)*K+I(eps).square()*exp_i(-rho*s)*curvature/2)*ds)
    loss=loss+chi*exp_i(-rho*T)*I(eps).square()*exponential_integral(beta,T).square()
    total=anchor+loss
    return dict(dimension=d,epsilon=eps,initial_std_upper=spread,panels=panels,
                beta_upper=float(beta.hi),anchor_regret=[float(anchor.lo),float(anchor.hi)],
                tube_loss_allowance=[float(loss.lo),float(loss.hi)],
                regret_upper=float(total.hi),certificate_seconds=time.perf_counter()-start,
                primitive_action_box=[P['lower'],P['upper']],
                scope='original continuous-time capital economy; all initial means and cross-sectional standard deviation <= stated bound; all adapted competitors in original action box',
                network_condition='each deployed action differs from common schedule by at most epsilon at every time and state',
                matrix_sha256=spectral['matrix_sha256'],spectral_lambda=spectral['lambda_upper'],
                arithmetic='conditional outward binary64, polynomial exp/log, checked square roots and positive interval LDL pivots',
                not_implied=['Adam convergence','actor advantage over the feasible anchor','certificate for the preference economy','machine formal verification'])

def run(out:Path)->dict:
    out.mkdir(parents=True,exist_ok=True);rows=[];norms=[];arrays={};start=time.perf_counter()
    for d in [10,20,50]:
        B=coupling(d);sp=spectral_bound(B);norms.append(sp);arrays[f'B_{d}']=B
        for spread in [0.,.25,.5]:
            for eps in [0.,.05,.1]:
                for panels in [4096,16384]:rows.append(enclosure(B,eps,spread,panels,sp))
    np.savez_compressed(out/'MATRICES.npz',**arrays)
    result=dict(parameters=P,terminal_dispersion_penalty=CHI,records=rows,spectral=norms,
                seconds=time.perf_counter()-start)
    (out/'CONTINUOUS_CERTIFICATES.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return result
if __name__=='__main__':
    result=run(Path(__file__).resolve().parents[1]/'results')
    print(json.dumps([r for r in result['records'] if r['panels']==16384 and r['epsilon']==.1],indent=2))
