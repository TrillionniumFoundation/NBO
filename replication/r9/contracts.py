"""R9 surrender and first-period permission experiments.

All inherited scientific files are read-only. A STOP action pays G-fee at an
interior rebalancing date, from min_term onward. Forced liquidation still pays
G. The initial risk classification always covers the original interval 1/8.
"""
from __future__ import annotations
import os
for _key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_key] = '1'
import sys, json, time, hashlib, platform
from pathlib import Path
import numpy as np
from scipy.sparse import csr_matrix
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'replication/r8'))
import model as baseline
from model import Model, Specification, r7, old
SIGNS=('positive','nonpositive')
OUT=ROOT/'replication/r9/output'

def serial(x):
    return r7.serial(x)

def save(name,data):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(serial(data),indent=2,allow_nan=False)+'\n')

class Contract:
    """Read-only view of a baseline kernel; no transition array is modified."""
    def __init__(self,base:Model,fee:float=0.,min_term:int=1):
        if not np.isfinite(fee) or fee<0: raise ValueError('fee must be finite and nonnegative')
        if not isinstance(min_term,int) or not 0<=min_term<=base.steps: raise ValueError('invalid minimum term')
        self.base=base;self.e=base.e;self.ns=base.ns;self.steps=base.steps
        self.terminal=base.terminal;self.center=base.center;self.spec=base.spec
        self.fee=float(fee);self.min_term=min_term
        self.na=len(base.e[0].menu)+(3 if base.e[0].extra else 0)
        self.stop=self.na;self.interior=~base.e[0].boundary
        self._masks={}
    def allowed(self,n,adjust=True,sign=None):
        key=(n,adjust,sign if n==0 else None)
        if key not in self._masks:
            orig=r7.mask(self.base,n,adjust,sign)
            orig=np.broadcast_to(orig,(self.ns,self.na))
            stop=(self.interior & (n>=self.min_term))[:,None]
            self._masks[key]=np.concatenate((orig,stop),axis=1)
        return self._masks[key]
    def q(self,k,n,v,d,fee=None):
        fee=self.fee if fee is None else fee
        return np.column_stack((self.base.q(k,n,v,d),self.terminal-fee))
    def continuation(self,k,n,v):
        return np.column_stack((r7.continuation(self.base,k,n,v),np.zeros(self.ns)))
    def selected(self,k,n,policy,v,d,fee=None):
        fee=self.fee if fee is None else fee
        p=np.minimum(policy,self.na-1)
        out=self.base.selected(k,n,p,v,d)
        use=policy==self.stop
        out[use]=self.terminal[use]-fee
        return out
    def pair(self,lam,d,adjust=True):
        if not 0<=lam<=1: raise ValueError('invalid law probability')
        v=np.empty((self.steps+1,self.ns));v[-1]=self.terminal
        p=np.empty((self.steps,self.ns),np.int32)
        for n in range(self.steps-1,-1,-1):
            raw=(1-lam)*self.q(0,n,v[n+1],d)+lam*self.q(1,n,v[n+1],d)
            q=np.where(self.allowed(n,adjust),raw,-np.inf)
            p[n]=q.argmax(1);v[n]=q[np.arange(self.ns),p[n]]
        out={}
        for sign in SIGNS:
            pp=p.copy();vv=v.copy();q=np.where(self.allowed(0,adjust,sign),raw,-np.inf)
            pp[0]=q.argmax(1);vv[0]=q[np.arange(self.ns),pp[0]]
            out[sign]={'value':vv,'policy':pp}
        return out
    def evaluate(self,policy,lam,d,fee=None):
        v=np.empty((self.steps+1,self.ns));v[-1]=self.terminal
        for n in range(self.steps-1,-1,-1):
            v[n]=(1-lam)*self.selected(0,n,policy[n],v[n+1],d,fee)+lam*self.selected(1,n,policy[n],v[n+1],d,fee)
        return v
    def coefficients(self,policy,d,fee=None,all_dates=False):
        prev=self.terminal[None,:];history=[None]*(self.steps+1);history[-1]=prev
        for n in range(self.steps-1,-1,-1):
            h=self.steps-n;z=[]
            for j in range(h+1):
                v=np.zeros(self.ns)
                if j<h:v+=(1-j/h)*self.selected(0,n,policy[n],prev[j],d,fee)
                if j>0:v+=j/h*self.selected(1,n,policy[n],prev[j-1],d,fee)
                z.append(v)
            prev=np.stack(z);history[n]=prev if all_dates else None
        return history if all_dates else prev[:,self.center]
    def moments(self,policy,lam):
        """Exact-array policy moments (base payoff, duration, surrender, effort).
        Discounted surrender is an incidence, not undiscounted probability.
        """
        f=np.zeros((4,self.steps+1,self.ns));f[0,-1]=self.terminal
        rows=np.arange(self.ns)
        for n in range(self.steps-1,-1,-1):
            livepol=policy[n]!=self.stop
            for prob,e in zip((1-lam,lam),self.e):
                cp=np.minimum(policy[n],len(e.menu)-1)
                ks=[(e.common,cp,livepol & (policy[n]<len(e.menu)))]
                if e.extra:ks.append((e.extra[n],np.clip(policy[n]-len(e.menu),0,2),livepol & (policy[n]>=len(e.menu))))
                for k,a,use in ks:
                    if not np.any(use): continue
                    rewards=(k.base[rows,a]-self.spec.cost*k.effort[rows,a],k.duration[rows,a],np.zeros(self.ns),k.effort[rows,a])
                    for j in range(4):
                        z=rewards[j]+k.selected(a,f[j,n+1])
                        f[j,n,use]+=prob*z[use]
            stopped=~livepol
            f[0,n,stopped]=self.terminal[stopped];f[2,n,stopped]=1.
        return f
    def initial_action(self,policy):
        a=int(policy[0,self.center])
        if a==self.stop:return 'surrender'
        if a<len(self.e[0].menu):return self.e[0].menu[a].tolist()
        return self.e[0].extra[0].actions[self.center,a-len(self.e[0].menu)].tolist()

def upper_pair(c,a,b,d,za,zb,adjust,method='chord'):
    """Streaming signed chord or count upper; includes STOP in the same menu."""
    if c.steps<2: raise ValueError('R9 uses the inherited eight-date horizon')
    if method=='chord':
        m=np.zeros(c.ns)
        for n in range(c.steps-2,-1,-1):
            diff=zb['positive']['value'][n+1]-za['positive']['value'][n+1]
            D=(b-a)*(c.continuation(0,n,diff)-c.continuation(1,n,diff))
            if n<c.steps-2:
                k0=c.continuation(0,n,m);k1=c.continuation(1,n,m)
                D+=np.maximum((1-a)*k0+a*k1,(1-b)*k0+b*k1)
            if n==0:
                out={};h=c.steps;j=np.arange(h+1)
                for s in SIGNS:
                    m0=max(0.,float(np.where(c.allowed(n,adjust,s),D,-np.inf).max(1)[c.center]))
                    out[s]=(1-j/h)*za[s]['value'][0,c.center]+j/h*zb[s]['value'][0,c.center]+j*(h-j)/(h*(h-1))*m0
                return out
            m=np.maximum(0.,np.where(c.allowed(n,adjust),D,-np.inf).max(1))
    if method=='count':
        prev=c.terminal[None,:]
        for n in range(c.steps-1,-1,-1):
            h=c.steps-n;z=np.empty((h+1,c.ns))
            z[0]=za['positive']['value'][n];z[h]=zb['positive']['value'][n]
            inner={}
            if h>1:
                q0=c.q(0,n,prev[0],d);q1=c.q(1,n,prev[0],d)
                previous=(1-b)*q0+b*q1
                for j in range(1,h):
                    q0=c.q(0,n,prev[j],d);q1=c.q(1,n,prev[j],d)
                    q=(1-j/h)*((1-a)*q0+a*q1)+j/h*previous
                    z[j]=np.where(c.allowed(n,adjust),q,-np.inf).max(1)
                    if n==0:inner[j]={s:float(np.where(c.allowed(n,adjust,s),q,-np.inf).max(1)[c.center]) for s in SIGNS}
                    previous=(1-b)*q0+b*q1
            if n==0:
                out={}
                for s in SIGNS:
                    co=z[:,c.center].copy();co[0]=za[s]['value'][0,c.center];co[-1]=zb[s]['value'][0,c.center]
                    for j in range(1,h):co[j]=inner[j][s]
                    out[s]=co
                return out
            prev=z
    raise ValueError(method)

class FirstDateMenu:
    """Exact piecewise-affine first-date risky-share envelope for fixed c,theta.
    Original proposals are retained. No claim of continuous c/theta optimality.
    """
    def __init__(self,base,lower=-.6,upper=1.,extra_points=()):
        self.base=base;self.lower=lower;self.upper=upper;self.center=base.center
        self.pairs=np.unique(base.e[0].menu[:,:2],axis=0)
        ss=base.e[0].states[[base.center]];h=1/base.steps;x=ss[0,1]
        knots=[];actions=[];xgrid=np.linspace(.5,2.,base.spec.nx)
        for cc,th in self.pairs:
            ps=[lower,upper,0.,-.5,.8]+list(extra_points)
            for e in base.e:
                m=e.model
                z=m.correlation*old.SIGNS[:,0]+np.sqrt(1-m.correlation**2)*old.SIGNS[:,1]
                slopes=h*m.excess*x+np.sqrt(h)*m.sigma_x*x*z
                intercept=x+h*(m.r*x-cc)
                for b in slopes:
                    if b!=0:ps.extend(((xgrid-intercept)/b).tolist())
            ps=np.unique(np.asarray(ps));ps=ps[(ps>=lower)&(ps<=upper)]
            for pi in ps:actions.append((cc,th,pi))
            knots.append(ps)
        # Existing frozen actions need not lie on the common (c,theta) grid.
        if base.e[0].extra:actions.extend(base.e[0].extra[0].actions[base.center].tolist())
        self.actions=np.unique(np.asarray(actions),axis=0)
        self.endpoints=base.e[0].states[[base.center]]
        self.rows=[];self.reward=[];self.duration=[];self.max_knot_error=0.
        for e in base.e:
            m=e.model;y,live,disc,flow,effort,_,alpha=old.transition(ss,self.actions,h,m)
            if not np.all(alpha==1.) or not np.all(live):raise ValueError('first-period nonexit premise failed')
            ann=-np.expm1(-m.rho*h*alpha)/m.rho
            size=np.array(e.shape)-1;z=(y-old.LO)/(old.HI-old.LO)*size
            ij=np.minimum(np.maximum(np.floor(z).astype(int),0),size-1);fr=z-ij
            inds=[];wts=[]
            for di,dj in ((0,0),(1,0),(0,1),(1,1)):
                w=(fr[...,0] if di else 1-fr[...,0])*(fr[...,1] if dj else 1-fr[...,1])
                inds.append(((ij[...,0]+di)*e.shape[1]+ij[...,1]+dj).reshape(len(self.actions),4))
                wts.append((disc*w/4).reshape(len(self.actions),4))
            ind=np.concatenate(inds,1);wt=np.concatenate(wts,1)
            mat=csr_matrix((wt.ravel(),ind.ravel(),np.arange(0,wt.size+1,16)),shape=(len(self.actions),base.ns))
            mat.sum_duplicates();mat.eliminate_zeros()
            self.rows.append(mat);self.reward.append(flow.mean(-1));self.duration.append(ann.mean(-1))
        self.nknots=len(self.actions)
    def values(self,continuation,lam,d):
        return sum(prob*(rr+d*aa+kk@continuation) for prob,rr,aa,kk in zip((1-lam,lam),self.reward,self.duration,self.rows))
    def endpoint_values(self,continuation,lam,d,pi,adjust=True):
        pairs=self.pairs if adjust else self.pairs[np.abs(self.pairs[:,1])<1e-14]
        actions=np.column_stack((pairs,np.full(len(pairs),pi)))
        ss=self.base.e[0].states[[self.center]];ans=np.zeros(len(actions))
        for prob,e in zip((1-lam,lam),self.base.e):
            y,live,disc,flow,_,_,alpha=old.transition(ss,actions,1/self.base.steps,e.model)
            if not np.all(alpha==1):raise ValueError('endpoint exceeds nonexit range')
            ann=-np.expm1(-e.model.rho*alpha/self.base.steps)/e.model.rho
            ans+=prob*np.mean(flow+d*ann+disc*old.interpolate(continuation.reshape(e.shape),y),axis=-1)
        i=int(ans.argmax());return float(ans[i]),actions[i]
    def optimize(self,continuation,lam,d,adjust=True,long=.8,short=.5,cached=None):
        if not 0<long<=self.upper or not 0<short<=-self.lower:raise ValueError('cap outside declared envelope')
        q=self.values(continuation,lam,d) if cached is None else cached
        ok=(np.abs(self.actions[:,1])<1e-14) if not adjust else np.ones(len(q),bool)
        result={}
        for sign,lo,hi,edge in (('positive',0.,long,long),('nonpositive',-short,0.,-short)):
            # Positive closure includes zero only as a supremum candidate. Every
            # reported positive optimum is additionally checked to be >0.
            sel=ok & (self.actions[:,2]>=lo-1e-13) & (self.actions[:,2]<=hi+1e-13)
            idx=np.where(sel)[0];j=idx[q[idx].argmax()]
            val=float(q[j]);act=self.actions[j].copy()
            ev,ea=self.endpoint_values(continuation,lam,d,edge,adjust)
            if ev>val:val,act=ev,ea
            result[sign]={'value':val,'action':act}
        return result

def first_moments(base,continuation_features,lam,action):
    ss=base.e[0].states[[base.center]];a=np.asarray(action)[None,:]
    ans=np.zeros(4)
    for prob,e in zip((1-lam,lam),base.e):
        y,live,disc,flow,effort,_,alpha=old.transition(ss,a,1/base.steps,e.model)
        assert np.all(alpha==1)
        ann=-np.expm1(-e.model.rho*alpha/base.steps)/e.model.rho
        rewards=(flow,ann,np.zeros_like(ann),effort)
        for j in range(4):ans[j]+=prob*np.mean(rewards[j]+disc*old.interpolate(continuation_features[j].reshape(e.shape),y))
    return ans

def risk_slope(base,continuation,lam,action):
    """Derivative on the open interpolation cell containing the chosen share."""
    ss=base.e[0].states[[base.center]];a=np.asarray(action)[None,:];x=ss[0,1]
    ans=0.;h=1/base.steps
    for prob,e in zip((1-lam,lam),base.e):
        y,live,disc,flow,effort,_,alpha=old.transition(ss,a,h,e.model)
        assert np.all(alpha==1)
        size=np.array(e.shape)-1;z=(y-old.LO)/(old.HI-old.LO)*size
        ij=np.minimum(np.maximum(np.floor(z).astype(int),0),size-1);p=z[...,0]-ij[...,0]
        i,j=ij[...,0],ij[...,1];v=continuation.reshape(e.shape);dx=1.5/(e.shape[1]-1)
        vx=((1-p)*(v[i,j+1]-v[i,j])+p*(v[i+1,j+1]-v[i+1,j]))/dx
        m=e.model;zx=m.correlation*old.SIGNS[:,0]+np.sqrt(1-m.correlation**2)*old.SIGNS[:,1]
        dy=h*m.excess*x+np.sqrt(h)*m.sigma_x*x*zx
        ans+=prob*np.mean(disc*vx*dy)
    return float(ans)

def arithmetic_audit(c,width,max_fee=1.):
    """Conservative gamma-bound, relative only to stored primitive arrays.
    Includes fixed-policy feature subtraction and two Bernstein restrictions.
    """
    kernels=[k for e in c.e for k in [e.common]+e.extra]
    beta=max(k.check['max_row_mass'] for k in kernels)+1e-12
    if beta>1+2e-12:raise ValueError('unbudgeted mass')
    R=2*max(max(float(abs(k.base).max()+abs(k.duration).max()+c.spec.cost*abs(k.effort).max()) for k in kernels),float(abs(c.terminal).max())+max_fee)
    N=c.steps;u=2.**-53
    gamma=lambda n:n*u/(1-n*u)
    B=np.zeros(N+1);E=B.copy();M=B.copy();D=B.copy();B[-1]=2*float(abs(c.terminal).max())
    for n in range(N-1,-1,-1):
        B[n]=R+beta*B[n+1]
        E[n]=beta*E[n+1]+gamma(4096)*(1+R+4*beta*(B[n+1]+E[n+1]))
        if n<N-1:
            M[n]=4*width*beta*B[n+1]+beta*M[n+1]
            D[n]=beta*D[n+1]+4*width*beta*E[n+1]+gamma(4096)*(1+8*width*beta*(B[n+1]+E[n+1])+4*beta*(M[n+1]+D[n+1]))
    upper=E[0]+.5*D[0]+gamma(32)*(1+2*(B[0]+E[0])+M[0]+D[0])
    lower=5*E[0]+gamma(4096*(N+1))*(1+8*B[0])
    bound=max(upper,lower)+gamma(64)*(1+4*B[0]+2*M[0])
    if not bound<1e-7:raise ValueError(f'increase arithmetic allowance: {bound}')
    return dict(derived_per_class_bound=bound,per_class_allowance=1e-7,row_mass_bound=beta,reward_bound=R,
        scope='round-to-nearest evaluation of stored arrays; no constructor or diffusion enclosure')

def region_certificate(base,fees=(.85,.9),min_term=1,region=(0.,.25,.4,.45),methods=('chord','count'),subdivisions=4,name='regional.json'):
    a,b,dl,dh=region;fees=tuple(dict.fromkeys(fees));contracts={f:Contract(base,f,min_term) for f in fees}
    anchors={};low={};policies={};checks=[];start=time.perf_counter()
    for adj in (True,False):
        for f,c in contracts.items():
            for lam in (a,b):
                for d in (dl,dh):
                    anchors[adj,f,lam,d]=c.pair(lam,d,adj)
                    for s,it in anchors[adj,f,lam,d].items():
                        p=it['policy'];key=(adj,f,lam,d,s);policies['.'.join(map(str,key))]=p
                        b0=c.coefficients(p,0.,0.);a0=c.coefficients(p,1.,0.)-b0;h0=b0-c.coefficients(p,0.,1.)
                        low[key]=(b0,a0,h0)
                        ev=c.evaluate(p,lam,d)
                        err=float(np.max(abs(ev-it['value'])))
                        rep=abs(float(r7.bernstein_value(b0+d*a0-f*h0,lam))-it['value'][0,c.center])
                        assert max(err,rep)<2e-11
                        checks.append(dict(key=key,replay_error=err,polynomial_error=rep))
    setup=time.perf_counter()-start
    arith=arithmetic_audit(next(iter(contracts.values())),b-a,max(1.,max(fees)));eps=arith['per_class_allowance']
    outputs=[];upstore={}
    for method in methods:
        tic=time.perf_counter();up={}
        for adj in (True,False):
            for f,c in contracts.items():
                for d in (dl,dh):
                    z=upper_pair(c,a,b,d,anchors[adj,f,a,d],anchors[adj,f,b,d],adj,method)
                    for s,co in z.items():up[adj,f,d,s]=co;upstore[f'{method}.{adj}.{f}.{d}.{s}']=co
        bounds={};cellrows=[]
        for adj in (True,False):
            interval=[np.inf,-np.inf]
            for left,right in zip(np.linspace(a,b,subdivisions+1)[:-1],np.linspace(a,b,subdivisions+1)[1:]):
                corners=[(f,d) for f in fees for d in (dl,dh)]
                U={s:np.stack([r7.restrict(up[adj,f,d,s],(left-a)/(b-a),(right-a)/(b-a)) for f,d in corners]) for s in SIGNS}
                L={s:[] for s in SIGNS}
                for key,(bc,ac,hc) in low.items():
                    aa,ff,ll,dd,s=key
                    if aa!=adj:continue
                    L[s].append(np.stack([r7.restrict(bc+d*ac-f*hc,left,right) for f,d in corners]))
                lo=max(float((p-U['nonpositive']).min()) for p in L['positive'])-2*eps
                hi=min(float((U['positive']-p).max()) for p in L['nonpositive'])+2*eps
                interval[0]=min(interval[0],lo);interval[1]=max(interval[1],hi)
                cellrows.append(dict(adjustment=adj,lambda_interval=[left,right],bounds=[lo,hi]))
            bounds['adjusted' if adj else 'no_adjustment']=interval
        outputs.append(dict(method=method,bounds=bounds,signs_certified=bounds['adjusted'][0]>0 and bounds['no_adjustment'][1]<0,upper_and_subdivision_seconds=time.perf_counter()-tic,cells=cellrows))
    result=dict(fees=list(fees),minimum_term=min_term,region=list(region),subdivisions=subdivisions,methods=outputs,
        common_setup_seconds=setup,base_construction_seconds=base.build_seconds,arithmetic=arith,checks=checks,
        scope='same full menu plus interior surrender; fixed fee and benefit per contract; interpolation in fee and benefit uses convex upper values and affine fixed-policy payoffs')
    save(name,result)
    np.savez_compressed(OUT/(Path(name).stem+'_policies.npz'),**policies)
    np.savez_compressed(OUT/(Path(name).stem+'_coefficients.npz'),**upstore,**{'.'.join(map(str,k))+'.'+n:v for k,co in low.items() for n,v in zip(('base','duration','surrender'),co)})
    return result
