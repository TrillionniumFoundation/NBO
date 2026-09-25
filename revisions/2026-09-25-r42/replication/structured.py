#!/usr/bin/env python3
"""R42 structural LP proposals and exact primal/dual certificates.
Floating-point optimization proposes a policy and equality multipliers only.
The independent checker, verify_structured.py, imports none of this module.
"""
from __future__ import annotations
import argparse, gzip, json, math, platform, resource, sys, time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

DEN=10**12

def model(n:int,T:int,m:int,kind:str,beta:str,epsilon:str)->dict:
    assert n>=2 and T>=1 and m>=2 and 0<F(beta)<=1 and F(epsilon)>0
    P=[[F(0) for _ in range(n)] for _ in range(n)]
    if kind=='band':
        for i in range(n-1):
            v=F(1+i%3,16); P[i][i+1]=v; P[i+1][i]=v
        for i in range(n): P[i][i]=1-sum(P[i])
    elif kind=='cycle':
        for i in range(n):
            P[i][i]=F(3,4); P[i][(i+1)%n]=F(1,4)
    elif kind=='dense':
        for i in range(n):
            for j in range(n): P[i][j]=F(1,2*n)+(F(1,2) if i==j else 0)
    else: raise ValueError(kind)
    r=[]; k=[]; best=[]
    for i in range(n):
        q=F(2*i+1,2*n); row=[-(q-F(a,m-1))**2 for a in range(m)]
        b=max(range(m),key=lambda a:row[a]); a0=max(0,b-1)
        r.append(row); best.append(b)
        k.append([F(0) if a==a0 else 1+q+F(abs(a-a0),m-1) for a in range(m)])
    nu=[F(2*(i+1),n*(n+1)) for i in range(n)]
    return dict(n=n,T=T,m=m,kind=kind,beta=F(beta),epsilon=F(epsilon),P=P,r=r,k=k,nu=nu,best=best)

def lp_data(d:dict,unreduced:bool=False):
    n,T,m=d['n'],d['T'],d['m']; B=float(d['beta']); P=np.array(d['P'],float)
    r=np.array(d['r'],float); k=np.array(d['k'],float); nu=np.array(d['nu'],float)
    rmax=r.max(axis=1); loss=rmax[:,None]-r
    q=n*T; npol=q*m; size=npol+q*(2 if unreduced else 1)
    I=[];J=[];A=[];rhs=[]
    def row(items,b):
        no=len(rhs);rhs.append(b)
        for j,v in items:
            if v: I.append(no);J.append(j);A.append(float(v))
    for t in range(T):
        for i in range(n): row([((t*n+i)*m+a,1) for a in range(m)],1)
    V=np.zeros((T+1,n))
    for t in range(T-1,-1,-1): V[t]=rmax+B*P@V[t+1]
    for t in range(T):
        for i in range(n):
            items=[(npol+t*n+i,1)]
            items += [((t*n+i)*m+a,-(r if unreduced else loss)[i,a]) for a in range(m)]
            if t+1<T: items += [(npol+(t+1)*n+j,-B*P[i,j]) for j in range(n)]
            row(items,0)
    if unreduced:
        for t in range(T):
            for i in range(n):
                items=[(npol+q+t*n+i,1)]+[((t*n+i)*m+a,-k[i,a]) for a in range(m)]
                if t+1<T: items += [(npol+q+(t+1)*n+j,-B*P[i,j]) for j in range(n)]
                row(items,0)
    c=np.zeros(size); bounds=[(0,1)]*npol
    # A tiny inward allowance is only a numerical proposal device. The exact
    # checker always evaluates the original declared allowance.
    e=max(float(d['epsilon'])-1e-9,float(d['epsilon'])/2)
    if unreduced:
        bounds += [(V[t,i]-e,V[t,i]) for t in range(T) for i in range(n)]
        bounds += [(0,float(k.max())*sum(B**s for s in range(T-t))) for t in range(T) for i in range(n)]
        c[npol+q:npol+q+n]=nu
    else:
        bounds += [(0,e)]*q
        w=nu.copy()
        for t in range(T):
            c[t*n*m:(t+1)*n*m]=(B**t*w[:,None]*k).ravel(); w=w@P
    mat=coo_matrix((A,(I,J)),shape=(len(rhs),size)).tocsr()
    return c,mat,np.array(rhs),bounds

def solve(d:dict,compare:bool=True)->dict:
    start=time.perf_counter(); n,T,m=d['n'],d['T'],d['m']; B=d['beta']; eps=d['epsilon']
    c,A,b,bounds=lp_data(d); prep=time.perf_counter()-start
    st=time.perf_counter()
    sol=linprog(c,A_eq=A,b_eq=b,bounds=bounds,method='highs',options={
        'time_limit':60.,'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
    lptime=time.perf_counter()-st
    if not sol.success: return dict(status='proposal_failed',solver_message=sol.message,lp_seconds=lptime)
    st=time.perf_counter(); p=[]
    xx=sol.x[:n*T*m].reshape(T,n,m)
    for t in range(T):
        pp=[]
        for i in range(n):
            f=np.maximum(xx[t,i],0); f=f/f.sum()
            v=[F(math.floor(float(a)*DEN),DEN) for a in f]
            v[d['best'][i]]+=1-sum(v); pp.append(v)
        p.append(pp)
    # Exact backward repair, including beta=1. Exogenous transitions allow
    # direct loss accounting. The inward LP allowance usually makes it idle.
    D=[[F(0) for i in range(n)] for t in range(T+1)]
    C=[[F(0) for i in range(n)] for t in range(T+1)]
    repair_max=F(0)
    loss=[[max(rr)-x for x in rr] for rr in d['r']]
    edges=[[(j,v) for j,v in enumerate(row) if v] for row in d['P']]
    for t in range(T-1,-1,-1):
        for i in range(n):
            nxt=B*sum(v*D[t+1][j] for j,v in edges[i]); allowed=eps-nxt
            assert allowed>=0
            cur=sum(p[t][i][a]*loss[i][a] for a in range(m))
            alpha=F(0) if cur<=allowed else (cur-allowed)/cur
            if alpha:
                p[t][i]=[(1-alpha)*v for v in p[t][i]];p[t][i][d['best'][i]]+=alpha
                repair_max=max(repair_max,alpha)
            D[t][i]=sum(p[t][i][a]*loss[i][a] for a in range(m))+nxt
            C[t][i]=sum(p[t][i][a]*d['k'][i][a] for a in range(m))+B*sum(v*C[t+1][j] for j,v in edges[i])
    U=sum(v*x for v,x in zip(d['nu'],C[0]))
    # Round equality multipliers; they need NOT be dual feasible.
    ys=[F(round(float(v)*DEN),DEN) for v in sol.eqlin.marginals[:n*T]]
    yd=[F(round(float(v)*DEN),DEN) for v in sol.eqlin.marginals[n*T:]]
    lower=sum(ys); w=d['nu'][:]; bt=F(1)
    for t in range(T):
        for i in range(n):
            for a in range(m):
                residual=bt*w[i]*d['k'][i][a]-ys[t*n+i]+loss[i][a]*yd[t*n+i]
                lower+=min(F(0),residual)
            residual=-yd[t*n+i]
            if t: residual+=B*sum(d['P'][j][i]*yd[(t-1)*n+j] for j in range(n))
            lower+=eps*min(F(0),residual)
        w=[sum(w[i]*d['P'][i][j] for i in range(n)) for j in range(n)];bt*=B
    L=max(F(0),lower);assert L<=U
    exacttime=time.perf_counter()-st
    stats=dict(status='certified',lower=str(L),upper=str(U),gap=str(U-L),relative_gap=str((U-L)/U) if U else '0',
               max_regret=str(max(max(row) for row in D)),repair_max=str(repair_max),
               preparation_seconds=prep,lp_seconds=lptime,exact_certificate_seconds=exacttime,
               variables=len(c),equalities=A.shape[0],nonzeros=A.nnz,lp_iterations=sol.nit,
               peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    if compare:
        st=time.perf_counter(); cc,AA,bb,bo=lp_data(d,True); data_time=time.perf_counter()-st
        st=time.perf_counter(); s2=linprog(cc,A_eq=AA,b_eq=bb,bounds=bo,method='highs',options={
            'time_limit':60.,'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
        stats['unreduced']=dict(status=int(s2.status),success=bool(s2.success),seconds=time.perf_counter()-st,
             preparation_seconds=data_time,variables=len(cc),equalities=AA.shape[0],nonzeros=AA.nnz,
             proposed_objective=float(s2.fun) if s2.fun is not None else None,
             interpretation='Same-object Bellman LP with ordinary HiGHS presolve; floating comparison, not an independent certificate')
    md={k:v for k,v in d.items() if k!='best'}
    def enc(x):
        if isinstance(x,F):return str(x)
        if isinstance(x,list):return [enc(v) for v in x]
        if isinstance(x,dict):return {k:enc(v) for k,v in x.items()}
        return x
    return enc(dict(schema='NBO-R42-exogenous-exact-v1',model=md,policy=p,dual_simplex=ys,dual_loss=yd,results=stats,
                    trust_boundary='Finite arithmetic only; continuum aggregation identities are proved in the manuscript.'))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--case',nargs=6,required=True);ap.add_argument('--out',required=True);ap.add_argument('--no-compare',action='store_true');arg=ap.parse_args()
    n,T,m,kind,b,e=arg.case;d=model(int(n),int(T),int(m),kind,b,e);out=solve(d,not arg.no_compare)
    p=Path(arg.out);p.parent.mkdir(parents=True,exist_ok=True)
    with gzip.open(p,'wt') as f:json.dump(out,f,sort_keys=True)
    print(json.dumps(out.get('results',out),sort_keys=True))
if __name__=='__main__':main()
