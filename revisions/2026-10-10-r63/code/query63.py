"""State-grid-free Bellman interval queries in the unchanged scalar economy.

All proposals (including learned ones) are untrusted. Only outward Bellman
brackets control acceptance; no stored common policy is consulted.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import itertools, math, sys, time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent/'2026-10-10-r62'
sys.path.insert(0,str(BASE/'code'))
import neural55 as n
I=n.I; B=F(15,16); SCALE=2**32
APPROX_COUNTS=dict(training_value_nodes=0,training_q_queries=0)

def rat(x):return n.s.c.rat_i(F(x))
def up(x):
    v=float(x);return float(np.nextafter(v,np.inf)) if F(v)<F(x) else v

def regularity(r,d):
    G,M=F(10,d),F(26,d)
    for _ in range(r):
        G,M=F(1037,128*d)+B*F(47,64)*G,F(22,d)+F(21,256*d)+B*(F(9,16)*M+G/8)
    return G,M

def coefficients(x):
    """Features computed from original states, not a conventional solution."""
    return np.column_stack([x, x.mean(axis=1), x[:,::2].mean(axis=1),
                            x[:,1::2].mean(axis=1), (x*x).mean(axis=1),
                            (x*np.roll(x,-1,axis=1)).mean(axis=1)])

def polynomial(features):
    return np.column_stack([np.ones(len(features)),features]+[features[:,i]*features[:,j] for i,j in itertools.combinations_with_replacement(range(features.shape[1]),2)])

def cap_interval(x):return F(1,8)+n.s.isum(I.point(x))*rat(F(1,8*x.shape[1]))
def cap_point(x):return .125+x.mean(axis=1)/8

def clamp(a,cap):
    a=np.asarray(a,dtype=float)
    return np.floor(np.maximum(0,np.minimum(cap,np.where(np.isfinite(a),a,cap/2)))*SCALE)/SCALE

def parabola_lower(left,right,length,H):
    kk=rat(F(H)/2)*I.point(length).square();k=I.point(kk.hi)
    diff=I.point(right)-I.point(left)
    low=((I.point(left)+I.point(right))/2-k/4-diff.square()/(4*k)).lo
    return np.where(diff.lo>=k.hi,left,np.where(diff.hi<=-k.hi,right,low))

class Oracle:
    def __init__(self,mode='adaptive',models=None,max_probes=512):
        if mode not in ('adaptive','bisection','relu','quadratic'):raise ValueError(mode)
        self.mode=mode;self.models=models or {};self.max_probes=max_probes
        self.counts=dict(value_queries=0,q_queries=0,terminal_queries=0,shock_children=0,
                         learned_proposals=0,accepted_first_partition=0,refinements=0,
                         max_batch=0,max_probes=0,stored_state_nodes=0,rational_fallbacks=0,rational_q_queries=0)
    def propose(self,x,r,cap):
        self.counts['learned_proposals']+=len(x)
        features=coefficients(x)
        model=self.models[r]
        if self.mode=='relu':
            W,b,u,c=model
            value=np.maximum(0,features@W+b)@u+c
        else:
            value=polynomial(features)@model
        return clamp(value,cap)
    def q(self,x,a,r,tol):
        self.counts['q_queries']+=len(x)
        xx=I.point(x);aa=I.point(a)
        if r==1:
            self.counts['terminal_queries']+=len(x)
            return n.o.final_q(xx,aa,1)
        _,M=regularity(r-1,x.shape[1]);zeta=B*M*x.shape[1]/6144
        q=1
        while zeta/(q*q)>F(tol)/4:q*=2
        child_tol=float(F(tol)/(4*B))
        y=n.o.deterministic_next(xx,aa);sign=np.where(np.arange(x.shape[1])%2==0,1.,-1.)
        G,_=regularity(r-1,x.shape[1])
        # Batch only the current quadrature descendants, never a state lattice.
        zl=np.tile(np.array([(2*j+1-q)/(32*q) for j in range(q)]),len(x))
        box=I(np.repeat(y.lo,q,axis=0),np.repeat(y.hi,q,axis=0))+I.point(zl[:,None]*sign)
        mid=box.midpoint();radius=np.maximum((I.point(mid)-I.point(box.lo)).hi,(I.point(box.hi)-I.point(mid)).hi)
        delta=n.s.isum(I.point(radius))*rat(G)
        child=self.solve(mid,r-1,child_tol)
        lower=I.point(child['lower'])-delta;upper=I.point(child['upper'])+delta
        lower=n.s.isum(I(lower.lo.reshape(len(x),q),lower.hi.reshape(len(x),q)))/q
        upper=n.s.isum(I(upper.lo.reshape(len(x),q),upper.hi.reshape(len(x),q)))/q
        self.counts['shock_children']+=len(mid)
        cost=n.s.costs(xx,aa,1)
        low=cost+rat(B)*lower
        high=cost+rat(B)*upper+rat(zeta/(q*q))
        return I(low.lo,high.hi)
    def terminal(self,x,tol):
        N,d=x.shape;self.counts['value_queries']+=N;self.counts['max_batch']=max(N,self.counts['max_batch'])
        capacity=cap_interval(x);cap=clamp(capacity.lo,capacity.lo)
        action=clamp(terminal_guess(x),cap)
        lowa=np.zeros(N);higha=cap.copy();done=np.zeros(N,dtype=bool)
        outlo=np.empty(N);outup=np.empty(N);outact=np.empty(N);probes=np.zeros(N,dtype=int)
        for _ in range(50):
            ids=np.flatnonzero(~done)
            if not len(ids):break
            xx=I.point(x[ids]);aa=I.point(action[ids]);der=n.o.final_derivative(xx,aa,1);value=n.o.final_q(xx,aa,1)
            self.counts['terminal_queries']+=len(ids);self.counts['q_queries']+=len(ids);probes[ids]+=1
            res=np.maximum(abs(der.lo),abs(der.hi))
            res=np.where((action[ids]==0)&(der.lo>=0),0,res)
            res=np.where((action[ids]==cap[ids])&(der.hi<=0),0,res)
            G,_=regularity(0,d);lam=F(13,16)+B*G*F(3*d,8)
            miss=rat(lam)*(I.point(capacity.hi[ids])-I.point(cap[ids]))
            lower=(I.point(value.lo)-I.point(res).square()/4-miss).lo
            gap=(I.point(value.hi)-I.point(lower)).hi;ok=gap<=tol
            hit=ids[ok];outlo[hit]=np.maximum(0,lower[ok]);outup[hit]=value.hi[ok];outact[hit]=action[hit];done[hit]=True
            todo=ids[~ok];negative=der.hi[~ok]<0;positive=der.lo[~ok]>0
            if np.any(~negative&~positive):raise RuntimeError('Terminal arithmetic ambiguity above tolerance')
            lowa[todo]=np.where(negative,action[todo],lowa[todo]);higha[todo]=np.where(positive,action[todo],higha[todo])
            action[todo]=clamp((lowa[todo]+higha[todo])/2,cap[todo])
        if not done.all():raise RuntimeError('Terminal certification cap exhausted')
        self.counts['max_probes']=max(self.counts['max_probes'],int(probes.max()))
        return dict(lower=outlo,upper=outup,action=outact,probes=probes,gap=(I.point(outup)-I.point(outlo)).hi)

    def solve(self,x,r,tol):
        try:return self._solve(x,r,tol)
        except RuntimeError:
            # The controller remains defined when a floating screen or cap
            # fails. Exact rational enumeration is a finite, paid fallback,
            # not a stored conventional policy at every state.
            rows=[]
            for state in np.asarray(x):
                self.counts['rational_fallbacks']+=1
                rows.append(self.rational(list(map(lambda z:F(float(z)),state)),r,F(tol)))
            lo=np.array([float(np.nextafter(float(a),-np.inf)) for a,b,c in rows])
            hi=np.array([float(np.nextafter(float(b),np.inf)) for a,b,c in rows])
            return dict(lower=lo,upper=hi,action=np.array([float(c) for a,b,c in rows]),
                        probes=np.zeros(len(rows),dtype=int),gap=(I.point(hi)-I.point(lo)).hi,
                        fitted_selected=np.zeros(len(rows),dtype=bool))

    def rational(self,x,r,tol):
        d=len(x);G,M=regularity(r-1,d);H=F(21,4)+B*M*F(5*d,32)
        lam=F(13,16)+B*G*F(3*d,8);capacity=F(1,8)+sum(x)/(8*d)
        cap=F((capacity*SCALE).__floor__(),SCALE);miss=lam*(capacity-cap)
        if tol<=8*lam/SCALE:raise RuntimeError('Requested accuracy exceeds declared action precision')
        A=1
        while H*(cap/A+F(1,SCALE))**2/8+miss>tol/4:A*=2
        bins=1
        if r>1:
            while B*M*d/(6144*bins*bins)>tol/4:bins*=2
        values=[]
        for j in range(A+1):
            a=F((cap*j*SCALE/A).__floor__(),SCALE);self.counts['rational_q_queries']+=1
            if r==1:lo=hi=n.o.exact_q(x,a,1)
            else:
                sh=max(F(0),F(1,2)-2*sum(x)/d)
                stage=2*sum((z-F(5,8))**2 for z in x)/d+sum((x[k]-x[(k+1)%d])**2 for k in range(d))/(4*d)+2*sh*sh+a*a+4*a**4
                L=U=F(0)
                for k in range(bins):
                    z=F(2*k+1-bins,32*bins)
                    y=[F(1,16)+x[i]/2+x[(i+1)%d]/8+x[i]*(1-x[(i+1)%d])/16+(F(1,2) if i%2==0 else F(1,4))*a+(1 if i%2==0 else -1)*z for i in range(d)]
                    l,u,_=self.rational(y,r-1,tol/(4*B));L+=l;U+=u
                lo=stage+B*L/bins;hi=stage+B*U/bins+B*M*d/(6144*bins*bins)
            values.append((lo,hi,a))
        lo=max(F(0),min(v[0] for v in values)-H*(cap/A+F(1,SCALE))**2/8-miss)
        _,hi,action=min(values,key=lambda v:(v[1],v[2]))
        if hi-lo>tol:raise AssertionError('Rational fallback budget')
        return lo,hi,action

    def _solve(self,x,r,tol):
        x=np.asarray(x,dtype=float)
        if x.ndim!=2 or x.shape[1]%2 or r<1 or not np.all(np.isfinite(x)) or np.any(x<0) or np.any(x>1):raise ValueError('Invalid state')
        if not (0<tol<1):raise ValueError('Invalid tolerance')
        N,d=x.shape
        if r==1:return self.terminal(x,tol)
        self.counts['value_queries']+=N;self.counts['max_batch']=max(N,self.counts['max_batch'])
        G,Mnext=regularity(r-1,d);H=F(21,4)+B*Mnext*F(5*d,32)
        lam=F(13,16)+B*G*F(3*d,8)
        capacity=cap_interval(x);cap=clamp(capacity.lo,capacity.lo)
        missing=rat(lam)*(I.point(capacity.hi)-I.point(cap))
        # Every point partitions the entire feasible interval. Endpoints remain
        # even when a network predicts the optimizer with high confidence.
        points=np.zeros((N,self.max_probes));lows=np.zeros_like(points);highs=np.zeros_like(points)
        points[:,1]=cap;size=np.full(N,2,dtype=int)
        a=self.q(x,points[:,0],r,tol);b=self.q(x,cap,r,tol)
        lows[:,0]=a.lo;highs[:,0]=a.hi;lows[:,1]=b.lo;highs[:,1]=b.hi
        running_lower=np.nextafter(parabola_lower(a.lo,b.lo,cap,H)-missing.hi,-np.inf)
        if self.mode in ('relu','quadratic'):
            prediction=self.propose(x,r,cap);inside=(prediction>0)&(prediction<cap)
            ids=np.flatnonzero(inside)
            if len(ids):
                v=self.q(x[ids],prediction[ids],r,tol)
                points[ids,2]=cap[ids];lows[ids,2]=b.lo[ids];highs[ids,2]=b.hi[ids]
                points[ids,1]=prediction[ids];lows[ids,1]=v.lo;highs[ids,1]=v.hi;size[ids]=3
        initial=size.copy();predicted=prediction.copy() if self.mode in ('relu','quadratic') else np.full(N,np.nan);active=np.arange(N);outlo=np.zeros(N);outup=np.zeros(N);outact=np.zeros(N)
        while len(active):
            width=int(size[active].max());cols=np.arange(width-1)[None,:];valid=cols<(size[active]-1)[:,None]
            p=points[active,:width];ll=lows[active,:width];hh=highs[active,:width]
            used=np.arange(width)[None,:]<size[active,None]
            endwidth=(I.point(hh)-I.point(ll)+I.point(missing.hi[active,None])).hi
            if np.any(used & (endwidth>5*tol/8)):raise RuntimeError('Precision budget exceeded; certificate withheld')
            h=I.point(p[:,1:])-I.point(p[:,:-1]);K=rat(H/2)*h.square()
            left=I.point(ll[:,:-1]);right=I.point(ll[:,1:]);diff=right-left
            # Minimize the semiconcavity parabola. Use outward arithmetic on
            # uncertain interior minima and exact monotone-branch endpoint lows.
            safeK=np.where(valid,K.hi,1.);kk=I.point(safeK)
            mid=(left+right)/2-kk/4-diff.square()/(4*kk)
            low=np.where(diff.lo>=safeK,left.lo,np.where(diff.hi<=-safeK,right.lo,mid.lo))
            low=np.where(valid,low,np.inf)
            which=np.argmin(low,axis=1);lb=low[np.arange(len(active)),which]-missing.hi[active]
            lb=np.nextafter(np.maximum(0,lb),-np.inf)
            running_lower[active]=np.maximum(running_lower[active],lb);lb=running_lower[active]
            candidate=np.where(np.arange(width)[None,:]<size[active,None],hh,np.inf)
            best=np.argmin(candidate,axis=1);ub=candidate[np.arange(len(active)),best]
            gap=(I.point(ub)-I.point(lb)).hi
            done=gap<=tol
            ids=active[done];outlo[ids]=lb[done];outup[ids]=ub[done];outact[ids]=p[np.flatnonzero(done),best[done]]
            self.counts['accepted_first_partition']+=int(np.count_nonzero(done & (size[active]==initial[active])))
            todo=active[~done];interval=which[~done]
            if not len(todo):break
            if np.any(size[todo]>=self.max_probes):raise RuntimeError('Declared action refinement cap exhausted')
            l=points[todo,interval];rr=points[todo,interval+1]
            # Exact dyadic bisection on the action lattice ensures coverage and
            # a finite cap; fitted values never change an acceptance threshold.
            fraction=np.full(len(todo),.5)
            if self.mode!='bisection':
                k=up(H/2)*(rr-l)**2; dif=lows[todo,interval+1]-lows[todo,interval]
                fraction=np.clip(.5-dif/(2*k),.25,.75)
            probe=clamp(l+fraction*(rr-l),rr)
            if np.any((probe<=l)|(probe>=rr)):raise RuntimeError('Arithmetic/quantum floor above requested tolerance')
            val=self.q(x[todo],probe,r,tol)
            for row,j,v,vl,vu in zip(todo,interval+1,probe,val.lo,val.hi):
                s=size[row]
                points[row,j+1:s+1]=points[row,j:s].copy();lows[row,j+1:s+1]=lows[row,j:s].copy();highs[row,j+1:s+1]=highs[row,j:s].copy()
                points[row,j]=v;lows[row,j]=vl;highs[row,j]=vu;size[row]+=1
            self.counts['refinements']+=len(todo);active=todo
        self.counts['max_probes']=max(self.counts['max_probes'],int(size.max()))
        if np.any(outup<outlo) or np.any(outact>capacity.lo):raise AssertionError('Invalid certificate')
        return dict(lower=outlo,upper=outup,action=outact,probes=size,
                    gap=(I.point(outup)-I.point(outlo)).hi,
                    fitted_selected=(predicted>0)&(predicted<cap)&(outact==predicted))

def local_tolerance(T,target):
    S=sum((B**j for j in range(T)),F(0));return float(F(target)/(2*S))
def policy_allowance(T,target):
    # State acquisition uses 40 bits, action proposals already use 32 bits.
    delta=F(local_tolerance(T,target));bound=F(0)
    for r in range(1,T+1):
        # dG<=27, dG_future<=27. Bound Q state transfer plus V transfer.
        implementation=F(8,2**40)+B*F(27*11,16*2**40)+F(27,2**40)
        bound=delta+implementation+B*bound
    return up(bound)

def terminal_guess(x):
    d=x.shape[1];y=n.next_point(x,np.zeros(len(x)));gamma=np.where(np.arange(d)%2==0,.5,.25)
    diff=gamma-np.roll(gamma,-1)
    D=(8*(y-.625)*gamma).mean(axis=1)+((y-np.roll(y,-1,axis=1))*diff).mean(axis=1)/2
    b=.5-2*y.mean(axis=1);C=2+float(B)*41/32
    def root(c,z):
        scale=np.sqrt(c/48);return 2*scale*np.sinh(np.arcsinh(-z/(32*scale**3))/3)
    a=root(C,float(B)*D)
    active=b-.75*a>0
    a=np.where(active,root(C+float(B)*9/4,float(B)*(D-3*b)),a)
    return np.maximum(0,np.minimum(cap_point(x),a))

def approximate(x,r,q=2,iters=10):
    """Unverified training labels only; never used in a lower certificate."""
    APPROX_COUNTS['training_value_nodes']+=len(x)
    d=x.shape[1];cap=cap_point(x);lo=np.zeros(len(x));hi=cap.copy();g=(math.sqrt(5)-1)/2
    def objective(a):
        APPROX_COUNTS['training_q_queries']+=len(x)
        if r==1:
            # Same analytic expression, floating-only for training speed.
            y=n.next_point(x,a);s=np.maximum(0,.5-2*y.mean(axis=1))
            terminal=4*((y-.625)**2).mean(axis=1)+((y-np.roll(y,-1,axis=1))**2).mean(axis=1)/4+2*s*s+5/3072
            return n.primitive_point(x,a)+float(B)*terminal
        total=np.zeros(len(x))
        for j in range(q):total+=approximate(n.next_point(x,a,(2*j+1-q)/(32*q)),r-1,q,iters)[1]
        return n.primitive_point(x,a)+float(B)*total/q
    if r==1:
        a=terminal_guess(x);return a,objective(a)
    a=hi-g*(hi-lo);b=lo+g*(hi-lo);fa=objective(a);fb=objective(b)
    for _ in range(iters):
        take=fa<=fb;hi=np.where(take,b,hi);lo=np.where(take,lo,a)
        # Reevaluate both probes to make label work explicit and independent of
        # branch ordering; this is deliberately not a timing baseline.
        a=hi-g*(hi-lo);b=lo+g*(hi-lo);fa=objective(a);fb=objective(b)
    options=np.stack([np.zeros(len(x)),cap,a,b]);values=np.stack([objective(v) for v in options]);ii=np.argmin(values,axis=0)
    return options[ii,np.arange(len(x))],values[ii,np.arange(len(x))]

def fit_models(d,T,seed,kind,rows=96):
    from sklearn.neural_network import MLPRegressor
    import warnings
    rng=np.random.default_rng(seed);x=rng.integers(0,2**16+1,size=(rows,d))/2**16
    # Fixed boundary training points, separate from the frozen evaluation stream.
    x[:4]=np.array([np.zeros(d),np.ones(d),np.full(d,.25),np.full(d,.75)])
    features=coefficients(x);models={};reports=[];start=time.perf_counter()
    for r in range(2,T+1):
        begin=time.perf_counter();y,_=approximate(x,r,q=2,iters=5 if r==3 else 9)
        label_seconds=time.perf_counter()-begin;begin=time.perf_counter()
        if kind=='relu':
            model=MLPRegressor(hidden_layer_sizes=(24,),activation='relu',solver='lbfgs',alpha=1e-5,
                               max_iter=160,max_fun=2000,tol=1e-8,random_state=seed+r)
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always');model.fit(features,y)
            models[r]=(model.coefs_[0],model.intercepts_[0],model.coefs_[1].ravel(),float(model.intercepts_[1][0]))
            pred=model.predict(features);messages=[str(w.message) for w in caught]
        else:
            z=polynomial(features);reg=np.eye(z.shape[1])*1e-6;reg[0,0]=0
            weights=np.linalg.solve(z.T@z+reg,z.T@y);models[r]=weights;pred=z@weights;messages=[]
        reports.append(dict(remaining_dates=r,label_seconds=label_seconds,fit_seconds=time.perf_counter()-begin,
                            training_mse=float(np.mean((pred-y)**2)),warnings=messages))
    return models,dict(rows=rows,seed=seed,kind=kind,seconds=time.perf_counter()-start,dates=reports)
