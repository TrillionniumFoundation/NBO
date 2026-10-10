"""Fixed-feature training on purchased original-law endpoint contexts.

Hat/ReLU and degree-four Bernstein arms have the same 5*d coefficients,
training states, endpoint data, loss, box constraint and optimizer budget.
No trained value enters a policy certificate. Exact rational post-evaluation
certifies the achieved convex objective, not a hidden-layer optimum.
"""
from pathlib import Path
from fractions import Fraction as F
import math,sys,time
import numpy as np
from scipy.optimize import minimize
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'2026-10-10-r67/code'))
import kernel66 as k
import certificates67 as cert
import science67 as old
q=k.q;I=k.I;B=k.B
LEARNED=('hat-relu','bernstein4','label-relu','quadratic')
KINDS=('adaptive','upper-minimizer')+LEARNED


def phi(x,kind):
    x=np.asarray(x);d=x.shape[1]
    if kind=='bernstein4':
        return np.concatenate([math.comb(4,j)*x**j*(1-x)**(4-j)/d for j in range(5)],axis=1)
    return np.concatenate([np.maximum(0,1-np.abs(4*x-j))/d for j in range(5)],axis=1)

def exact_phi(row,kind):
    x=[F(float(v)) for v in row];d=len(x)
    if kind=='bernstein4':return tuple(F(math.comb(4,j),d)*z**j*(1-z)**(4-j) for j in range(5) for z in x)
    return tuple(max(F(0),1-abs(4*z-j))/d for j in range(5) for z in x)

def contexts(d,r,tol,n,seed):
    rng=np.random.default_rng(seed);x=rng.integers(0,2**16,size=(n,d))/2**16
    oracle=k.Oracle('adaptive');cap=q.clamp(q.cap_interval(x).lo,q.cap_interval(x).lo)
    left=oracle.q(x,np.zeros(n),r,tol);right=oracle.q(x,cap,r,tol)
    G,M=q.regularity(r-1,d);H=F(21,4)+B*M*F(5*d,32);lam=F(13,16)+B*G*F(3*d,8)
    missing=(q.rat(lam)*(I.point(q.cap_interval(x).hi)-I.point(cap))).hi
    lower=np.maximum(0,np.nextafter(q.parabola_lower(left.lo,right.lo,cap,H)-missing,-np.inf))
    A=1
    while H*(F(1,4*A)+F(1,2**32))**2/8+2*lam/F(2**32)>F(tol)/4:A*=2
    allowance=q.up(lam*(F(1,2**32)+F(1,2**36)))
    return dict(x=x,cap=cap,left_lo=left.lo,left_hi=left.hi,right_lo=right.lo,right_hi=right.hi,
                lower=lower,tol=tol,H=str(H),Lambda=str(lam),allowance=allowance,K=A+1,A=A,work=oracle.counts.copy())

def numeric_loss(w,c,features,margin,penalty):
    z=features@w;cap=c['cap'];co=cap*cap
    score=(1-z)*c['left_hi']+z*c['right_hi']-co*z*(1-z)+c['allowance']-c['lower']
    residual=np.maximum(0,score-c['tol']+margin)
    deriv=c['right_hi']-c['left_hi']+co*(2*z-1)
    loss=c['K']*np.mean(residual**2)+penalty*np.dot(w,w)/2
    gradient=features.T@(2*c['K']*residual*deriv)/len(z)+penalty*w
    return loss/margin**2,gradient/margin**2

def exact_certificate(c,kind,weights,margin,penalty):
    C=[cert.Context(F(0),F(float(cap)),F(float(l)),F(float(u)),F(float(lb)),F(c['tol']),
                    rounding_allowance=F(c['allowance']),work_cap=F(c['K']))
       for cap,l,u,lb in zip(c['cap'],c['left_hi'],c['right_hi'],c['lower'])]
    features=[exact_phi(row,kind) for row in c['x']]
    result=cert.objective(C,features,tuple(map(lambda z:F(float(z)),weights)),F(margin),F(penalty))
    return dict(value_exact=str(result['value']),dual_gap_exact=str(result['dual_gap']),
                value=float(result['value']),dual_gap=float(result['dual_gap']),
                work_upper=float(result['average_work_upper']),coefficient_count=len(weights),
                feature_partition_verified=all(sum(p)==1 and min(p)>=0 for p in features))

def fit(d,T,target,seed,kind,train_n=48):
    if kind not in LEARNED:return {},dict(seconds=0.,dates=[],contexts=0,labels=0,kind=kind),{}
    start=time.perf_counter();tol=old.budget(T,target)[0];models={};reports=[];raw={}
    for r in range(2,T+1):
        begin=time.perf_counter();c=contexts(d,r,tol,train_n,seed+100*r)
        # All learned arms receive the identical purchased information set.
        q.APPROX_COUNTS.update(training_value_nodes=0,training_q_queries=0)
        labels,_=q.approximate(c['x'],r,q=2,iters=5 if r>=3 else 9)
        data_seconds=time.perf_counter()-begin;begin=time.perf_counter()
        tau=tol/4;penalty=1e-7;P=phi(c['x'],kind);exact=None
        if kind in ('hat-relu','bernstein4'):
            res=minimize(lambda w:numeric_loss(w,c,P,tau,penalty),np.full(P.shape[1],.5),jac=True,
                method='L-BFGS-B',bounds=[(0.,1.)]*P.shape[1],options=dict(maxiter=160,ftol=1e-14,gtol=1e-8,maxls=30))
            weights=np.round(np.clip(res.x,0,1)*2**16)/2**16
            model=weights.tolist();exact=exact_certificate(c,kind,weights,tau,penalty)
            optimizer=dict(success=bool(res.success),message=str(res.message),iterations=int(res.nit))
        elif kind=='label-relu':
            y=np.clip(labels/c['cap'],0,1)
            def fun(w):
                error=P@w-y;return float(np.mean(error**2)),2*P.T@error/len(y)
            res=minimize(fun,np.full(P.shape[1],.5),jac=True,method='L-BFGS-B',bounds=[(0.,1.)]*P.shape[1],options=dict(maxiter=160,ftol=1e-14,gtol=1e-8))
            weights=np.round(np.clip(res.x,0,1)*2**16)/2**16;model=weights.tolist()
            optimizer=dict(success=bool(res.success),message=str(res.message),iterations=int(res.nit))
        else:
            P=q.polynomial(c['x']);weights=np.linalg.solve(P.T@P+np.eye(P.shape[1])*1e-6,P.T@labels);model=weights.tolist()
            optimizer=dict(success=True,message='ridge normal equation; proposal only',iterations=1)
        models[r]=dict(kind=kind,weights=model)
        raw.update({f'r{r}_{name}':val for name,val in c.items() if isinstance(val,np.ndarray)})
        raw[f'r{r}_labels']=labels
        reports.append(dict(r=r,data_seconds=data_seconds,fit_and_certificate_seconds=time.perf_counter()-begin,
                            optimizer=optimizer,exact_certificate=exact,endpoint_work=c['work'],label_work=q.APPROX_COUNTS.copy(),
                            margin=tau,penalty=penalty,tolerance=tol,recovery_root_cap=c['K'],coefficient_count=len(weights)))
    return models,dict(seconds=time.perf_counter()-start,dates=reports,contexts=train_n*(T-1),labels=train_n*(T-1),kind=kind),raw

def prediction(kind,models,x,r,cap):
    model=models[r] if r in models else models[str(r)];w=np.asarray(model['weights'])
    if kind=='quadratic':a=q.polynomial(x)@w
    else:a=cap*(phi(x,kind)@w)
    return q.clamp(a,cap)

class Oracle(k.Oracle):
    def __init__(self,kind='adaptive',models=None,record=False):
        super().__init__('relu' if kind in LEARNED else kind,models,record=record)
        self.kind=kind
    def propose(self,x,r,cap):
        start=time.perf_counter();self.counts['learned_proposals']+=len(x)
        a=prediction(self.kind,self.models,x,r,cap)
        self.counts['prediction_seconds']+=time.perf_counter()-start
        return a

def validate(d,T,target,kind,models,seed,n=256):
    if kind not in LEARNED:return [],{}
    tol=old.budget(T,target)[0];reports=[];raw={}
    for r in range(2,T+1):
        start=time.perf_counter();c=contexts(d,r,tol,n,seed+20000+100*r)
        pred=prediction(kind,models,c['x'],r,c['cap'])
        upper=k.chord_upper(np.zeros(n),c['cap'],c['left_hi'],c['right_hi'],pred)
        score=(I.point(upper)-I.point(c['lower'])).hi
        tau=tol/4;surplus=(I.point(score)-I.point(tol)+I.point(tau))
        loss=np.minimum(1.,(I.point(np.maximum(0,surplus.hi)).square()/q.rat(F(tau)**2)).hi)
        fail=score>tol;actual=np.zeros(n,dtype=int);gaps=np.maximum(0,score.copy())
        oracle=k.Oracle('adaptive')
        ids=np.flatnonzero(fail)
        if len(ids):
            A=c['A'];actions=q.clamp(c['cap'][ids,None]*np.arange(A+1)/A,c['cap'][ids,None])
            xx=np.repeat(c['x'][ids],A+1,axis=0);aa=actions.reshape(-1)
            values=oracle.q(xx,aa,r,tol)
            lower=values.lo.reshape(len(ids),A+1);high=values.hi.reshape(len(ids),A+1)
            if np.any((I.point(high)-I.point(lower)).hi>5*tol/8):raise AssertionError('Validation endpoint precision contract')
            maxstep=np.max(np.diff(actions,axis=1),axis=1)
            cover=q.rat(F(c['H'])/8)*I.point(maxstep).square()
            miss=q.rat(F(c['Lambda']))*(q.cap_interval(c['x'][ids])-I.point(c['cap'][ids]))
            L=(I.point(lower.min(axis=1))-cover-I.point(miss.hi)).lo
            gaps[ids]=(I.point(high.min(axis=1))-I.point(L)).hi
            if np.any(gaps[ids]>tol):raise AssertionError('Independent full-action validation recovery failed')
            actual[ids]=A+1
        if np.any(actual>c['K']*loss):raise AssertionError('Work-loss domination failed')
        raw.update({f'r{r}_{name}':val for name,val in c.items() if isinstance(val,np.ndarray)})
        raw.update({f'r{r}_action':pred,f'r{r}_score':score,f'r{r}_loss':loss,f'r{r}_additional_root_queries':actual,f'r{r}_gap':gaps})
        reports.append(dict(r=r,rows=n,screen_returns=int((~fail).sum()),loss_mean=float(loss.mean()),
            mean_additional_root_queries=float(actual.mean()),K=c['K'],
            validation_work_upper=min(float(c['K']),float(c['K']*(loss.mean()+math.sqrt(12/(2*n))))),
            log_upper=12.,family_error=.01,endpoint_work=c['work'],recovery_work=oracle.counts,
            seconds=time.perf_counter()-start,
            scope='Independent uniform acquired-state contexts; fixed full-action mesh recovery after failure, not recursive on-policy IID data'))
    return reports,raw
