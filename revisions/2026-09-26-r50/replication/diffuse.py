"""Affine-cost, continuous-uniform-reset common-policy control.
Constructs a cellwise globally feasible policy and an outward-rounded integrated dual.
The lower certificate covers ALL Borel policies, not just grid policies.
"""
from fractions import Fraction as F
from pathlib import Path
import json,time,gzip,sys,resource,hashlib
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
Z=F(0)
def enc(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {k:enc(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [enc(v) for v in x]
    return x

def affine(c,x):return F(c[0])+F(c[1])*x

def envelope(lines,l,u):
    pts={l,u}
    for i,(a,b) in enumerate(lines):
        for c,d in lines[:i]:
            if b!=d:
                x=(c-a)/(b-d)
                if l<x<u:pts.add(x)
    pts=sorted(pts);total=Z
    for l,u in zip(pts,pts[1:]):
        a,b=min(lines,key=lambda ab:ab[0]+ab[1]*(l+u)/2)
        total+=a*(u-l)+b*(u*u-l*l)/2
    return total

def lower_value(raw,lam,q):
    T,m,N=raw['T'],raw['m'],len(lam[0]);beta=F(raw['beta']);eps=F(raw['epsilon']);gamma=list(map(F,raw['gamma']));total=Z
    avg=[sum(v)/N for v in lam]
    for t in range(T):
        for c in range(N):
            lines=[]
            for a in range(m):
                d=[(1-gamma[a])*F(z) for z in raw['g'][t]]
                lines.append(tuple(beta**t*F(raw['k'][t][a][j])+(lam[t][c]+q[t])*d[j] for j in range(2)))
            z=envelope(lines,F(c,N),F(c+1,N))
            total+=F((z*(1<<50)).numerator//(z*(1<<50)).denominator,1<<50)
        residual=(beta*(q[t-1]+avg[t-1]) if t else Z)-q[t]
        total+=eps*min(Z,residual)-eps*avg[t]
    return max(Z,total)

def construct(raw,N,method='highs-ds',lp_seconds=20):
    start=time.perf_counter();T,m=raw['T'],raw['m'];beta=F(raw['beta']);eps=F(raw['epsilon']);gamma=list(map(F,raw['gamma']));dim=T*N*m+T
    eq=[];erhs=[];ub=[];urhs=[];obj=np.zeros(dim)
    def pv(t,c,a):return (t*N+c)*m+a
    def mv(t):return T*N*m+t
    for t in range(T):
        mr={mv(t):F(1)}
        if t+1<T:mr[mv(t+1)]=-beta
        for c in range(N):
            x=F(2*c+1,2*N);row={}
            for a in range(m):
                gap=(1-gamma[a])*affine(raw['g'][t],x)
                mr[pv(t,c,a)]=-gap/N
                endpoints=[(1-gamma[a])*affine(raw['g'][t],F(j,N)) for j in (c,c+1)]
                row[pv(t,c,a)]=max(endpoints)
                obj[pv(t,c,a)]=float(beta**t*affine(raw['k'][t][a],x)/N)
            if t+1<T:row[mv(t+1)]=beta
            ub.append(row);urhs.append(eps)
            eq.append({pv(t,c,a):F(1) for a in range(m)});erhs.append(F(1))
        eq.append(mr);erhs.append(Z)
    def sparse(rows):
        ii=[];jj=[];vv=[]
        for i,row in enumerate(rows):
            for j,z in row.items():
                if z:ii.append(i);jj.append(j);vv.append(float(z))
        return coo_matrix((vv,(ii,jj)),shape=(len(rows),dim)).tocsr()
    setup=time.perf_counter()-start
    result=linprog(obj,A_ub=sparse(ub),b_ub=np.array(urhs,float),A_eq=sparse(eq),b_eq=np.array(erhs,float),bounds=[(0,1)]*(T*N*m)+[(0,float(eps))]*T,method=method,options={'time_limit':lp_seconds})
    lp_elapsed=time.perf_counter()-start-setup
    bits=40;den=1<<bits
    def rq(x):return F(round(float(x)*den),den) if np.isfinite(x) else Z
    if result.x is None:
        proposal=np.zeros((T,N,m));proposal[:,:,gamma.index(F(1))]=1
    else:proposal=np.asarray(result.x[:T*N*m]).reshape(T,N,m)
    lam=[[Z]*N for _ in range(T)];q=[Z]*T
    if result.ineqlin.marginals is not None:
        lam=[[max(Z,rq(-N*result.ineqlin.marginals[t*N+c])) for c in range(N)] for t in range(T)]
        q=[rq(result.eqlin.marginals[t*(N+1)+N]) for t in range(T)]
    best=gamma.index(F(1));M=[Z]*(T+1);p=[[[Z]*m for _ in range(N)] for _ in range(T)];cost=Z
    for t in reversed(range(T)):
        cap=eps-beta*M[t+1];assert cap>0
        for c in range(N):
            row=[max(Z,rq(z)) for z in proposal[t,c]];s=sum(row)
            row=[z/s for z in row] if s else [F(a==best) for a in range(m)]
            gaps=[max((1-gamma[a])*affine(raw['g'][t],F(j,N)) for j in (c,c+1)) for a in range(m)]
            regret=sum((row[a]*gaps[a] for a in range(m)),Z)
            if regret>cap:
                z=cap/regret;row=[v*z for v in row];row[best]+=1-z
            row=[F(v.numerator*den//v.denominator,den) if a!=best else Z for a,v in enumerate(row)];row[best]=1-sum(row)
            assert min(row)>=0 and sum(row)==1 and sum((row[a]*gaps[a] for a in range(m)),Z)<=cap
            p[t][c]=row;x=F(2*c+1,2*N)
            M[t]+=sum((row[a]*(1-gamma[a])*affine(raw['g'][t],x)/N for a in range(m)),Z)
            cost+=beta**t*sum((row[a]*affine(raw['k'][t][a],x)/N for a in range(m)),Z)
        M[t]+=beta*M[t+1];assert M[t]<=eps
    L=lower_value(raw,lam,q);assert L<=cost
    return dict(schema='nbo-r50-diffuse-v1',model=raw,N=N,method=method,policy=p,lambda_density=lam,moment_prices=q,moments=M,lower=L,upper=cost,target='1/1000',lp_status=int(result.status),lp_variables=dim,lp_constraints=len(eq)+len(ub),setup_seconds=setup,lp_seconds=lp_elapsed,construction_seconds=time.perf_counter()-start)

def generate(T=8,m=3,beta='9/10',eps='1/20',slope='2/5',seed=401):
    # Source-defined rational synthetic primitives; no fitted data.
    def noise(t,a,key,den):
        v=int(hashlib.sha256(f'r50:{seed}:{t}:{a}:{key}'.encode()).hexdigest()[:10],16)
        return F(v%den,den)
    gam=[F(a,m-1) for a in range(m)]
    g=[];k=[]
    for t in range(T):
        g.append([F(4,5)+noise(t,0,'g',17)/5,F(slope)*(F(1,2)+noise(t,0,'s',19))])
        k.append([[gam[a]*(F(1,5)+noise(t,a,'cost',23)/3),gam[a]*(F(1,10)+noise(t,a,'slope',29)/3)] for a in range(m)])
    return enc(dict(name=f'D-{seed}-T{T}-m{m}-b{beta}-e{eps}-s{slope}',T=T,m=m,beta=beta,epsilon=eps,gamma=gam,g=g,k=k,kernel='uniform-independent-reset',initial_law='uniform[0,1]',data_status='synthetic'))

if __name__=='__main__':
    from check_diffuse import verify
    raw=generate(seed=9001);r=construct(raw,64);e=enc(r);print(verify(e,raw));print('seconds',r['construction_seconds'])
