"""R43: verified proposals for controlled common-Markov revision.
SciPy supplies proposals only. All published endpoints use rational arithmetic.
Run verify_regret.py separately to reconstruct the contract and endpoints.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import gzip, hashlib, json, math, random, resource, sys, time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

ZERO=F(0); ONE=F(1)
GRID=2**40
def floor_grid(x): return F((x.numerator*GRID)//x.denominator,GRID)
def quantize(x): return F(round(float(x)*GRID),GRID)
def enc(x):
    if isinstance(x,F): return str(x)
    if isinstance(x,np.integer): return int(x)
    raise TypeError(type(x).__name__)
def dot(x,y): return sum((a*b for a,b in zip(x,y)),ZERO)
def model(seed:int,n:int,T:int,m:int,beta:str,epsilon:str):
    rng=random.Random(seed)
    P=[]; r=[]; k=[]
    # Actions improve a condition process, rather than merely serving demand.
    # All costs, transition weights and installed actions are designed primitives.
    prices=[F(0),F(9,100),F(8,25),F(11,20),F(4,5)]
    for i in range(n):
        pp=[]; rr=[]; kk=[]
        installed=0 if i>=n//2 else (seed%2)
        for a in range(m):
            weights=[max(1,38-10*a)+rng.randrange(4),36+rng.randrange(4),
                     12+7*a+rng.randrange(4),2+11*a+rng.randrange(4)]
            destinations=[max(0,i-1),i,min(n-1,i+1),n-1]
            row=[ZERO]*n
            for j,w in zip(destinations,weights): row[j]+=F(w,sum(weights))
            pp.append(row)
            rr.append(F(i,n-1)-prices[a]-F(rng.randrange(1,20)*a,100000))
            kk.append((ONE+F(i,n-1))*int(a!=installed))
        P.append(pp); r.append(rr); k.append(kk)
    return dict(seed=seed,n=n,T=T,m=m,beta=F(beta),epsilon=F(epsilon),P=P,r=r,k=k,
                terminal=[F(i,2*(n-1)) for i in range(n)],nu=[F(1,n)]*n)
def parse_model(raw):
    d=dict(raw)
    for key in ('beta','epsilon'): d[key]=F(d[key])
    for key in ('terminal','nu'): d[key]=list(map(F,d[key]))
    for key in ('r','k'): d[key]=[list(map(F,row)) for row in d[key]]
    d['P']=[[list(map(F,row)) for row in state] for state in d['P']]
    return d

def reference(d):
    n,T,m=d['n'],d['T'],d['m']; b=d['beta']
    V=[[ZERO]*n for _ in range(T+1)]; H=[[ZERO]*n for _ in range(T+1)]
    V[T]=d['terminal'][:]; star=[[0]*n for _ in range(T)]
    loss=[[[ZERO]*m for _ in range(n)] for _ in range(T)]
    gain=[[[ZERO]*m for _ in range(n)] for _ in range(T)]
    for t in range(T-1,-1,-1):
        for i in range(n):
            q=[d['r'][i][a]+b*dot(d['P'][i][a],V[t+1]) for a in range(m)]
            a0=max(range(m),key=lambda a:q[a]); star[t][i]=a0; V[t][i]=q[a0]
            H[t][i]=d['k'][i][a0]+b*dot(d['P'][i][a0],H[t+1])
            for a in range(m):
                loss[t][i][a]=V[t][i]-q[a]
                gain[t][i][a]=H[t][i]-d['k'][i][a]-b*dot(d['P'][i][a],H[t+1])
    ratios=[gain[t][i][a]/loss[t][i][a] for t in range(T) for i in range(n)
            for a in range(m) if loss[t][i][a]>0]
    strict=all(loss[t][i][a]>0 for t in range(T) for i in range(n) for a in range(m) if a!=star[t][i])
    return V,H,star,loss,gain,min([ZERO]+ratios),max([ZERO]+ratios),strict

class Program:
    def __init__(self): self.keys=[]; self.idx={}; self.bounds=[]; self.eq=[]; self.ub=[]; self.obj={}
    def var(self,key,l,u):
        assert l<=u,(key,l,u)
        j=len(self.keys); self.idx[key]=j; self.keys.append(key); self.bounds.append((l,u)); return j
    def row(self,coeff,rhs,eq=False):
        clean={j:F(v) for j,v in coeff.items() if v}; (self.eq if eq else self.ub).append((clean,F(rhs)))
    def product(self,x,y,key):
        lx,ux=self.bounds[x]; ly,uy=self.bounds[y]
        vals=[lx*ly,lx*uy,ux*ly,ux*uy]; w=self.var(key,min(vals),max(vals))
        self.row({w:-1,y:lx,x:ly},lx*ly)
        self.row({w:-1,y:ux,x:uy},ux*uy)
        self.row({w:1,y:-ux,x:-ly},-ux*ly)
        self.row({w:1,y:-lx,x:-uy},-lx*uy)
        return w

def build(d,mode='scaled'):
    n,T,m=d['n'],d['T'],d['m']; b=d['beta']; eps=d['epsilon']
    V,H,star,loss,gain,lminus,lplus,strict=reference(d)
    lp=Program(); costcap=max(x for row in d['k'] for x in row)
    for t in range(T):
        for i in range(n):
            for a in range(m):
                if a!=star[t][i]:
                    u=min(ONE,eps/loss[t][i][a]) if loss[t][i][a]>0 else ONE
                    lp.var(('p',t,i,a),ZERO,u)
    for t in range(T):
        cap=costcap*sum((b**j for j in range(T-t)),ZERO)
        for i in range(n):
            lp.var(('D',t,i),ZERO,eps)
            lo,hi=H[t][i]-cap,H[t][i]
            if mode=='scaled' and strict: lo=max(lo,lminus*eps); hi=min(hi,lplus*eps)
            lp.var(('S',t,i),lo,hi)
    for t in range(T):
        for i in range(n):
            aa=[a for a in range(m) if a!=star[t][i]]
            pp={a:lp.idx[('p',t,i,a)] for a in aa}
            lp.row({j:ONE for j in pp.values()},ONE)
            lp.row({pp[a]:loss[t][i][a] for a in aa},eps)
            if mode=='scaled' and strict:
                lp.row({lp.idx[('S',t,i)]:1,lp.idx[('D',t,i)]:-lplus},0)
                lp.row({lp.idx[('S',t,i)]:-1,lp.idx[('D',t,i)]:lminus},0)
            for kind,stage in [('D',loss),('S',gain)]:
                row={lp.idx[(kind,t,i)]:ONE}
                for a in aa: row[pp[a]]=-stage[t][i][a]
                if t<T-1:
                    pa0=d['P'][i][star[t][i]]
                    for j in range(n):
                        v=lp.idx[(kind,t+1,j)]
                        if pa0[j]: row[v]=row.get(v,ZERO)-b*pa0[j]
                    for a in aa:
                        for j in range(n):
                            delta=d['P'][i][a][j]-pa0[j]
                            if delta:
                                v=lp.idx[(kind,t+1,j)]
                                w=lp.product(pp[a],v,('w',kind,t,i,a,j))
                                row[w]=-b*delta
                lp.row(row,0,eq=True)
    lp.obj={lp.idx[('S',0,i)]:-d['nu'][i] for i in range(n)}
    return lp,(V,H,star,loss,gain,lminus,lplus,strict)

def residual_bound(lp,y,lam):
    assert len(y)==len(lp.eq) and len(lam)==len(lp.ub) and min(lam,default=ZERO)>=0
    coeff=[ZERO]*len(lp.keys)
    for j,c in lp.obj.items(): coeff[j]+=c
    val=ZERO
    for u,(row,rhs) in zip(y,lp.eq):
        val+=u*rhs
        for j,c in row.items(): coeff[j]-=u*c
    for u,(row,rhs) in zip(lam,lp.ub):
        val-=u*rhs
        for j,c in row.items(): coeff[j]+=u*c
    return floor_grid(val)+sum((floor_grid(min(c*l,c*u)) for c,(l,u) in zip(coeff,lp.bounds)),ZERO)

def repair(d,proposal,ref):
    V,H,star,loss,gain,*_=ref; n,T,m=d['n'],d['T'],d['m']; b=d['beta']; eps=d['epsilon']
    D=[[ZERO]*n for _ in range(T+1)]; C=[[ZERO]*n for _ in range(T+1)]
    p=[[[ZERO]*m for _ in range(n)] for _ in range(T)]
    max_tv=ZERO
    for t in range(T-1,-1,-1):
        for i in range(n):
            st=star[t][i]; row=[max(ZERO,min(ONE,F(x))) for x in proposal[t][i]]; row[st]=ZERO
            z=sum(row,ZERO)
            if z>1: row=[v/z for v in row]
            row[st]=ONE-sum(row,ZERO)
            q=[loss[t][i][a]+b*dot(d['P'][i][a],D[t+1]) for a in range(m)]
            regret=dot(row,q)
            margin=F(m-1,GRID)*max(abs(qa-q[st]) for qa in q)
            target=eps-margin
            if target<=q[st]:
                row=[ZERO]*m; row[st]=ONE
            elif regret>target:
                alpha=(regret-target)/(regret-q[st]); max_tv=max(max_tv,alpha*(ONE-row[st]))
                row=[v*(ONE-alpha) for v in row]; row[st]+=alpha
            row=[floor_grid(v) if a!=st else ZERO for a,v in enumerate(row)]
            row[st]=ONE-sum(row,ZERO)
            p[t][i]=row; D[t][i]=dot(row,q)
            C[t][i]=sum((row[a]*(d['k'][i][a]+b*dot(d['P'][i][a],C[t+1])) for a in range(m)),ZERO)
            assert 0<=D[t][i]<=eps and sum(row)==1
    return p,dot(d['nu'],C[0]),max_tv,max(x for row in D for x in row)

def solve(d,mode='scaled',seconds=30):
    start=time.perf_counter(); lp,ref=build(d,mode); build_seconds=time.perf_counter()-start
    def sparse(rows):
        ii=[]; jj=[]; vv=[]
        for i,(row,rhs) in enumerate(rows):
            for j,v in row.items(): ii.append(i); jj.append(j); vv.append(float(v))
        return coo_matrix((vv,(ii,jj)),shape=(len(rows),len(lp.keys))).tocsr(),np.array([float(rhs) for _,rhs in rows])
    A,b=sparse(lp.ub); E,e=sparse(lp.eq); c=np.zeros(len(lp.keys))
    for j,v in lp.obj.items(): c[j]=float(v)
    ts=time.perf_counter()
    res=linprog(c,A_ub=A,b_ub=b,A_eq=E,b_eq=e,bounds=[(float(l),float(u)) for l,u in lp.bounds],method='highs',options={'time_limit':seconds,'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
    solve_seconds=time.perf_counter()-ts
    available=res.x is not None and res.eqlin.marginals is not None
    y=[quantize(x) for x in res.eqlin.marginals] if available else [ZERO]*len(lp.eq)
    lam=[max(ZERO,quantize(-x)) for x in res.ineqlin.marginals] if available else [ZERO]*len(lp.ub)
    proposal=[[[ZERO]*d['m'] for _ in range(d['n'])] for _ in range(d['T'])]
    if available:
        for t in range(d['T']):
            for i in range(d['n']):
                for a in range(d['m']):
                    if a!=ref[2][t][i]: proposal[t][i][a]=max(ZERO,quantize(res.x[lp.idx[('p',t,i,a)]]))
    ta=time.perf_counter()
    lower=max(ZERO,dot(d['nu'],ref[1][0])+residual_bound(lp,y,lam))
    policy,upper,tv,operating=repair(d,proposal,ref)
    assert lower<=upper
    metadata=dict(mode=mode,strict=ref[-1],lp_status=int(res.status),lp_message=str(res.message),variables=len(lp.keys),equalities=len(lp.eq),inequalities=len(lp.ub),nonzeros=A.nnz+E.nnz,build_seconds=build_seconds,lp_seconds=solve_seconds,arithmetic_seconds=time.perf_counter()-ta,peak_process_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,lower=str(lower),upper=str(upper),gap=float(upper-lower),relative_gap=float((upper-lower)/upper) if upper else 0.0,max_repair_tv=str(tv),max_operating_regret=str(operating),d_min=str(min(ref[3][t][i][a] for t in range(d['T']) for i in range(d['n']) for a in range(d['m']) if a!=ref[2][t][i])),lminus=str(ref[5]),lplus=str(ref[6]))
    proof=dict(schema='nbo-r43-regret-v1',model=d,mode=mode,y=y,lambda_nonnegative=lam,policy=policy,lower=lower,upper=upper)
    return proof,metadata

def write_proof(path,proof):
    data=json.dumps(proof,default=enc,separators=(',',':')).encode()
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(gzip.compress(data,mtime=0))
    return hashlib.sha256(path.read_bytes()).hexdigest()

if __name__=='__main__':
    d=model(430000,3,4,3,'.95','.01')
    for mode in ('unscaled','scaled'):
        proof,meta=solve(d,mode); print(json.dumps(meta,indent=2))
        write_proof(Path(__file__).parents[1]/'proofs'/('development_'+mode+'.json.gz'),proof)
