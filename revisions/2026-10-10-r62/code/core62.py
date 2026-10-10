"""R62 original-optimum bounds. Neural fitting is never used as a proof oracle."""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import ctypes,hashlib,itertools,json,math,subprocess,time
import numpy as np
import neural55 as n
I=n.I;B=F(15,16);R=Path(__file__).resolve().parents[1]
if F(n.BETA)!=B:raise AssertionError('R62 discount differs from the unchanged inherited economic primitives')
TASKS=((2,1,2,(8,16,32,64),16,4),(2,1,3,(8,16,32,64),16,4),(4,1,3,(4,8,16),16,4),(8,1,2,(2,4),8,2),(2,2,2,(8,16,32,64),16,4))
SEEDS=(6201,6202,6203,6204);TOLS=(F(1,2),F(1,4),F(1,8),F(1,16),F(1,32));BATCH=4096

def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def up(x):
    x=F(x);v=float(x)
    return float(np.nextafter(v,np.inf)) if F(v)<x else v
def down(x):
    x=F(x);v=float(x)
    return float(np.nextafter(v,-np.inf)) if F(v)>x else v
def rat(x):return n.s.c.rat_i(F(x))
def need(c,msg):
    if not c:raise AssertionError(msg)
def key(d,m,T):return f'd{d}-m{m}-T{T}'
def constants(d,m,T,sub,A,q):
    G=[F(0)]*T+[F(10,d)];M=[F(0)]*T+[F(26,d)];D=[F(0)]*T+[F(9,d)+F(16,d*d)]
    for t in reversed(range(T)):
        G[t]=F(1037,128*d)+B*F(47,64)*G[t+1]
        M[t]=F(22,d)+F(21,256*d)+B*(F(9,16)*M[t+1]+G[t+1]/8)
        D[t]=F(5,d)+F(16,d*d)+F(21,256*d*d)+B*M[t+1]*(F(85,256)+F(23,256*d))
    kap=[d*v/(8*sub*sub) for v in D]
    norm=F((5 if m==1 else 9)*d,32)
    action=[m*(F(21,4)+B*M[t+1]*norm)/(128*A*A) for t in range(T)]
    shock=[M[t+1]*d*(F(1,1024)+(F(1,4096) if m==2 else F(0)))/(6*q*q) for t in range(T)]
    lam=[F(13,16)+B*F(3*d,8)*G[t+1] for t in range(T)]
    need(all(g<=F(27,d) for g in G) and all(v<=F(54,d) for v in M),'Regularity constants')
    return dict(G=G,M=M,D=D,kappa=kap,action=action,shock=shock,Lambda=lam)
def const_payload(c):return {k:[str(v) for v in vals] for k,vals in c.items()}

def compile_kernel():
    (R/'build').mkdir(exist_ok=True);start=time.perf_counter()
    cmd=['g++','-O3','-std=c++17','-shared','-fPIC','-ffp-contract=off','-fno-fast-math',str(R/'code/interpolate62.cpp'),'-o',str(R/'build/interpolate62.so')]
    subprocess.run(cmd,check=True,capture_output=True)
    return dict(command=cmd,seconds=time.perf_counter()-start,source_sha256=digest(R/'code/interpolate62.cpp'),binary_sha256=digest(R/'build/interpolate62.so'),compiler=subprocess.check_output(['g++','--version'],text=True).splitlines()[0])
_LIB=None
class Table:
    def __init__(self,values,d,sub):
        global _LIB
        self.values=np.ascontiguousarray(values,dtype=np.float64).reshape(-1);self.d=d;self.sub=sub
        need(len(self.values)==(sub+1)**d and np.isfinite(self.values).all(),'Invalid nodal table')
        K=(3*d+4)*(1<<d)+32;ma=F(float(np.abs(self.values).max()))
        self.error=up(F(K,2**53-K)*ma+F(K,2**1022));self.ops=K
        cube=self.values.reshape((sub+1,)*d);self.lips=[]
        for j in range(d):
            diff=I.point(np.take(cube,np.arange(1,sub+1),axis=j))-I.point(np.take(cube,np.arange(sub),axis=j))
            v=float(np.maximum(np.abs(diff.lo),np.abs(diff.hi)).max());self.lips.append(up(F(v)*sub))
        self.lips=np.array(self.lips);self.queries=0
        if _LIB is None:
            _LIB=ctypes.CDLL(str(R/'build/interpolate62.so'))
            _LIB.interpolate62.argtypes=[ctypes.POINTER(ctypes.c_double)]*3+[ctypes.c_size_t,ctypes.c_int,ctypes.c_int]
            _LIB.interpolate62.restype=ctypes.c_int
    def point(self,x):
        x=np.ascontiguousarray(x,dtype=np.float64);need(x.ndim==2 and x.shape[1]==self.d,'Point dimensions')
        out=np.empty(len(x));ptr=lambda a:a.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        status=_LIB.interpolate62(ptr(self.values),ptr(x),ptr(out),len(x),self.d,self.sub)
        need(status==0,'Native interpolation rejected inputs: '+str(status));self.queries+=len(x)
        return out
    def interval(self,x):
        need(np.all(x.lo>=0) and np.all(x.hi<=1),'Transition outside state cube')
        center=x.midpoint();y=self.point(center)
        radius=np.maximum((I.point(center)-I.point(x.lo)).hi,(I.point(x.hi)-I.point(center)).hi)
        allowance=n.s.isum(I.point(radius)*I.point(self.lips)).hi
        error=(I.point(allowance)+I.point(self.error)).hi
        return I((I.point(y)-I.point(error)).lo,(I.point(y)+I.point(error)).hi)

def grid(d,sub):
    count=(sub+1)**d
    for start in range(0,count,BATCH):
        stop=min(start+BATCH,count);idx=np.arange(start,stop,dtype=np.int64);z=idx.copy();x=np.empty((len(idx),d))
        for j in reversed(range(d)):x[:,j]=(z%(sub+1))/sub;z//=sub+1
        yield start,stop,x

def capacity(x):return F(1,8)+n.s.isum(x)*rat(F(1,8*x.lo.shape[-1]))
def cap_points(x):return .125+x.sum(axis=1)/(8*x.shape[1])
def action_cost(a):
    result=n.s.isum(a.square()+4*a.square().square())
    if a.lo.shape[1]==2:result=result+n.s.col(a,0)*n.s.col(a,1)/4
    return result
def stage(x,a):return n.s.costs(x,I.point(np.zeros(len(x.lo))),1)+action_cost(a)
def terminal(x):return n.s.costs(x,I.point(np.zeros(len(x.lo))),1,True)
def transition(x,a,z1,z2=0.):
    out=n.o.deterministic_next(x,n.s.col(a,0));d=x.lo.shape[1]
    if a.lo.shape[1]==2:
        second=np.where(np.arange(d)%2==0,.25,.5);v=n.s.col(a,1);out=out+I(v.lo[:,None],v.hi[:,None])*second
    signs=np.where(np.arange(d)%2==0,1.,-1.)
    if isinstance(z1,I):out=out+I(z1.lo[:,None],z1.hi[:,None])*signs
    else:out=out+z1*signs
    if isinstance(z2,I):out=out+I(z2.lo[:,None],z2.hi[:,None])
    else:out=out+z2
    return out

def qbound(x,a,t,T,q,m,const,next_tables=None):
    lo=I.point(np.zeros(len(x.lo)));hi=I.point(np.zeros(len(x.lo)))
    zs=[-1/32+(j+.5)/(16*q) for j in range(q)]
    ws=[-1/64+(j+.5)/(32*q) for j in range(q)] if m==2 else [0.]
    for z,w in itertools.product(zs,ws):
        state=transition(x,a,z,w)
        if t==T-1:v=terminal(state);low=v.lo;high=v.hi
        else:low=next_tables[0].interval(state).lo;high=next_tables[1].interval(state).hi
        lo=lo+I.point(low);hi=hi+I.point(high)
    count=len(zs)*len(ws);lo=lo/count;hi=hi/count
    if t<T-1:lo=lo-rat(const['kappa'][t+1])
    hi=hi+rat(const['shock'][t]);s=stage(x,a)
    return I((s+rat(B)*lo).lo,(s+rat(B)*hi).hi)

def fractions_menu(m,A):
    return [(i/A,) for i in range(A+1)] if m==1 else [(i/A,j/A) for i in range(A+1) for j in range(A-i+1)]

def reference(d,m,T,sub,A,q):
    start=time.perf_counter();c=constants(d,m,T,sub,A,q);N=(sub+1)**d
    lowers=np.empty((T,N));uppers=np.empty((T,N));actions=np.empty((T,N,m));selected_upper=np.empty((T,N));raw_min_lower=np.empty((T,N));work=[];nxt=None
    for t in reversed(range(T)):
        begin=time.perf_counter();count=0
        for first,last,points in grid(d,sub):
            xx=I.point(points);cap=cap_points(points);L=np.full(len(points),np.inf);U=L.copy();sel=np.zeros((len(points),m))
            for frac in fractions_menu(m,A):
                aa=I.point(cap[:,None]*np.array(frac));val=qbound(xx,aa,t,T,q,m,c,nxt);L=np.minimum(L,val.lo)
                take=val.hi<U;U[take]=val.hi[take];sel[take]=aa.lo[take];count+=len(points)
            raw_min_lower[t,first:last]=L;low=np.maximum(0.,(I.point(L)-rat(c['action'][t])).lo)
            need(np.all(low<=U) and np.all(sel>=0) and np.all(sel.sum(axis=1)<=cap),'Reference feasibility/order')
            lowers[t,first:last]=low;uppers[t,first:last]=U;actions[t,first:last]=sel;selected_upper[t,first:last]=U
        nxt=(Table(lowers[t],d,sub),Table(uppers[t],d,sub))
        work.append(dict(date=t,point_action_queries=count,seconds=time.perf_counter()-begin,node_bracket_width=float((I.point(uppers[t])-I.point(lowers[t])).hi.max())))
    return dict(d=d,m=m,T=T,n=sub,A=A,q=q,nodes=N,constants=const_payload(c),work=sorted(work,key=lambda r:r['date']),seconds=time.perf_counter()-start),dict(lower=lowers,upper=uppers,policy=actions,selected_upper=selected_upper,lattice_min_lower=raw_min_lower)

class Actor:
    def __init__(self,policy,d,sub):
        self.policy=np.asarray(policy);self.T,self.N,self.m=self.policy.shape;self.d=d;self.sub=sub
        self.tables=[[Table(self.policy[t,:,j],d,sub) for j in range(self.m)] for t in range(self.T)]
    def allowance(self,t):
        value=F(0)
        for tab in self.tables[t]:
            value+=sum((F(float(z)) for z in tab.lips),F(0))/2**40+F(1,2**20)+2*F(tab.error)+F(1,2**48)
        return value
    def interval(self,t,x):
        scale=2**40;obs=I(np.floor(x.lo*scale)/scale,np.floor(x.hi*scale)/scale);items=[]
        for tab in self.tables[t]:
            v=tab.interval(obs);lo=(I.point(v.lo)-I.point(up(2*F(tab.error)+F(1,2**20)+F(1,2**48)))).lo
            items.append(I(np.maximum(0.,lo),np.maximum(0.,v.hi)))
        return n.s.stack(items)
    def point(self,t,x):
        obs=np.floor(np.asarray(x)*2**40)/2**40;actions=[]
        for tab in self.tables[t]:
            v=tab.point(obs);lo=(I.point(v)-I.point(tab.error)).lo
            actions.append(np.maximum(0,np.floor(lo*2**20)/2**20))
        return np.stack(actions,axis=1)

def certificate(policy,selected_upper,lower,d,m,T,sub,A,q):
    const=constants(d,m,T,sub,A,q);actor=Actor(policy,d,sub);bound=F(0);dates=[]
    for t in reversed(range(T)):
        nodegap=float((I.point(selected_upper[t])-I.point(lower[t])).hi.max());need(nodegap>=0,'Negative optimal advantage allowance')
        implementation=actor.allowance(t);greedy=F(nodegap)+const['kappa'][t]
        bound=greedy+const['Lambda'][t]*implementation+B*bound
        dates.append(dict(date=t,node_gap_upper=nodegap,interpolation_allowance_exact=str(const['kappa'][t]),implementation_action_error_exact=str(implementation),greedy_allowance_exact=str(greedy),policy_gap_exact=str(bound),policy_gap_upper=up(bound)))
    return dict(dates=sorted(dates,key=lambda z:z['date']),maximum_date_gap_upper=max(z['policy_gap_upper'] for z in dates),initial_gap_upper=up(bound)),actor

def transferred_actions(proposal,points,t):
    loc=proposal['partition'].locate(points);old=proposal['actions'][t,loc];centers=proposal['partition'].centers[loc]
    ratios=old/cap_points(centers)[:,None];cap=cap_points(points)
    out=np.maximum(0,np.floor((ratios*cap[:,None])*4096)/4096)
    # Exact dyadic feasibility check; proportional correction is followed by
    # downward integer rounding and does not rely on SLSQP feasibility.
    for k in range(len(out)):
        if out[k].sum()>cap[k]:out[k]=np.floor(out[k]*(cap[k]/out[k].sum())*4096)/4096
    need(np.all(out.sum(axis=1)<=cap),'Transferred proposal infeasible')
    return out

def policy_from_proposal(ref,arrays,proposal):
    start=time.perf_counter();d,m,T,sub,A,q=(ref[k] for k in ('d','m','T','n','A','q'));c=constants(d,m,T,sub,A,q)
    pure=np.empty_like(arrays['policy']);pupper=np.empty_like(arrays['upper']);guard=arrays['policy'].copy();gupper=arrays['upper'].copy();counts=[]
    for t in range(T):
        nxt=None if t==T-1 else (Table(arrays['lower'][t+1],d,sub),Table(arrays['upper'][t+1],d,sub))
        changed=0
        for first,last,points in grid(d,sub):
            act=transferred_actions(proposal,points,t);v=qbound(I.point(points),I.point(act),t,T,q,m,c,nxt)
            pure[t,first:last]=act;pupper[t,first:last]=v.hi;take=v.hi<gupper[t,first:last]
            guard[t,first:last][take]=act[take];gupper[t,first:last][take]=v.hi[take];changed+=int(take.sum())
        counts.append(dict(date=t,additional_witness_nodes=changed))
    pc,_=certificate(pure,pupper,arrays['lower'],d,m,T,sub,A,q);gc,_=certificate(guard,gupper,arrays['lower'],d,m,T,sub,A,q)
    return dict(seconds=time.perf_counter()-start,counts=counts,pure_certificate=pc,guarded_certificate=gc),dict(pure=pure,pure_upper=pupper,guarded=guard,guarded_upper=gupper)

def path_cost(actor,x,z1,z2):
    total=I.point(np.zeros(len(x.lo)))
    for t in range(actor.T):
        a=actor.interval(t,x);total=total+rat(B**t)*stage(x,a);x=transition(x,a,z1[t],z2[t] if actor.m==2 else 0.)
    return total+rat(B**actor.T)*terminal(x)

def support(T):return sum((B**t*F(103,64) for t in range(T)),F(0))+B**T*F(37,16)
