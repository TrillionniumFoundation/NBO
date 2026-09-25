"""State/date restart-price certificates; floating optimization proposes prices only.

The certificate is a small nonnegative rational price field. Its lower endpoint
is reconstructed by a directed Bellman pass, not a solver objective or dual bound.
R46 is a retrospective response experiment on the unchanged R44 primitives.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import argparse, gzip, hashlib, json, math, sys, time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'revisions/2026-09-25-r46'
BASE=ROOT/'revisions/2026-09-25-r44'
Q=2**44
Z=F(0)

def dot(a,b): return sum((x*y for x,y in zip(a,b)),Z)
def floorq(v): return F((v.numerator*Q)//v.denominator,Q)
def parse(raw):
    d=dict(raw)
    for key in ['beta','epsilon']: d[key]=F(raw[key])
    for key in ['nu','terminal']: d[key]=list(map(F,raw[key]))
    for key in ['r','k']: d[key]=[list(map(F,row)) for row in raw[key]]
    d['P']=[[list(map(F,row)) for row in state] for state in raw['P']]
    return d

def operating(d):
    n,T,m,b=d['n'],d['T'],d['m'],d['beta']
    V=[[Z]*n for _ in range(T+1)]; V[T]=d['terminal'][:]
    loss=[[[Z]*m for _ in range(n)] for _ in range(T)]
    face_cost=[[Z]*n for _ in range(T+1)]; face=[]
    for t in reversed(range(T)):
        for i in range(n):
            q=[d['r'][i][a]+b*dot(d['P'][i][a],V[t+1]) for a in range(m)]
            V[t][i]=max(q)
            loss[t][i]=[V[t][i]-z for z in q]
            aa=[a for a in range(m) if q[a]==V[t][i]]
            face.append(len(aa)-1)
            face_cost[t][i]=min(d['k'][i][a]+b*dot(d['P'][i][a],face_cost[t+1]) for a in aa)
    return V,loss,face_cost,sum(face)

def propose(d,loss,seconds=120,constant=False):
    n,T,m,b,e=d['n'],d['T'],d['m'],d['beta'],d['epsilon']
    bounds=[]; idx={}
    def var(key,lo=None,hi=None):
        j=len(bounds);idx[key]=j;bounds.append((lo,hi));return j
    for t in range(T):
        for i in range(n): var(('u',t,i))
    if constant:
        j=var(('constant',),0,None)
        for t in range(T):
            for i in range(n):idx['l',t,i]=j
    else:
        for t in range(T):
            for i in range(n):var(('l',t,i),0,None)
    edges={i:sorted({j for a in range(m) for j,p in enumerate(d['P'][i][a]) if p}) for i in range(n)}
    if not constant:
        for t in range(T-1):
            for i in range(n):
                for j in edges[i]:var(('z',t,i,j),0,None)
    rows=[]
    def row(terms,rhs):
        c={}
        for j,v in terms:c[j]=c.get(j,Z)+v
        rows.append(({j:v for j,v in c.items() if v},rhs))
    if not constant:
        for t in range(T-1):
            for i in range(n):
                for j in edges[i]:
                    z=idx['z',t,i,j]
                    row([(z,1),(idx['l',t,i],-1)],Z)
                    row([(z,1),(idx['l',t+1,j],-1)],Z)
    for t in range(T):
        for i in range(n):
            for a in range(m):
                terms=[(idx['u',t,i],1),(idx['l',t,i],e-loss[t][i][a])]
                if t<T-1:
                    for j,p in enumerate(d['P'][i][a]):
                        if p:
                            terms.append((idx['u',t+1,j],-b*p))
                            terms.append((idx['l',t,i] if constant else idx['z',t,i,j],-b*e*p))
                row(terms,d['k'][i][a])
    ii=[];jj=[];vv=[]
    for h,(rr,rhs) in enumerate(rows):
        for j,v in rr.items():ii.append(h);jj.append(j);vv.append(float(v))
    A=coo_matrix((vv,(ii,jj)),shape=(len(rows),len(bounds))).tocsr()
    c=np.zeros(len(bounds))
    for i,v in enumerate(d['nu']):c[idx['u',0,i]]=-float(v)
    started=time.perf_counter()
    res=linprog(c,A_ub=A,b_ub=np.array([float(rhs) for rr,rhs in rows]),bounds=bounds,method='highs',options={'time_limit':seconds,'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
    elapsed=time.perf_counter()-started
    prices=[[Z]*n for _ in range(T)]
    if res.x is not None:
        for t in range(T):
            for i in range(n):
                v=float(res.x[idx['l',t,i]])
                if not math.isfinite(v):raise ValueError('nonfinite price proposal')
                prices[t][i]=max(Z,F(round(v*Q),Q))
    return prices,dict(lp_status=int(res.status),lp_message=str(res.message),primal_available=res.x is not None,variables=len(bounds),constraints=len(rows),nonzeros=A.nnz,lp_seconds=elapsed,native_objective=-float(res.fun) if res.fun is not None else None)

def lower(d,loss,prices):
    n,T,m,b,e=d['n'],d['T'],d['m'],d['beta'],d['epsilon']
    u=[[Z]*n for _ in range(T+1)]
    for t in reversed(range(T)):
        for i in range(n):
            lam=prices[t][i]; terms=[]
            for a in range(m):
                v=d['k'][i][a]+lam*(loss[t][i][a]-e)
                if t<T-1:v+=b*sum((p*(u[t+1][j]+e*min(lam,prices[t+1][j])) for j,p in enumerate(d['P'][i][a]) if p),Z)
                terms.append(v)
            u[t][i]=floorq(min(terms))
    # Costs, not transformed continuation values, are nonnegative.
    return dot(d['nu'],[max(Z,v) for v in u[0]]),u

def candidate(raw):
    name=raw['case_name'];items=[]
    for method in ['bellman','aggregate','scip']:
        path=BASE/'proofs'/name/f'{method}.json.gz'
        obj=json.loads(gzip.decompress(path.read_bytes()))
        assert obj['model']=={k:v for k,v in raw.items() if k!='case_name'}
        key='verified_candidate_upper' if method=='scip' else 'upper'
        items.append((F(obj[key]),method,obj['policy'],hashlib.sha256(path.read_bytes()).hexdigest()))
    return min(items,key=lambda r:r[0])

def run(name):
    started=time.perf_counter();path=BASE/'models'/f'{name}.json';data=path.read_bytes();raw=json.loads(data)
    protocol=json.loads((BASE/'PROTOCOL.json').read_text())
    assert hashlib.sha256(data).hexdigest()==protocol['models_sha256'][name]
    d=parse(raw);V,loss,H,face_dimension=operating(d);operating_seconds=time.perf_counter()-started
    upper,origin,policy,source_hash=candidate(dict(raw,case_name=name))
    output=[]
    for constant in [True,False]:
        ts=time.perf_counter();prices,meta=propose(d,loss,constant=constant);tl=time.perf_counter();L,u=lower(d,loss,prices)
        assert L<=upper,(name,L,upper)
        method='constant' if constant else 'restart'
        proof=dict(schema='nbo-r46-restart-prices-v1',model=raw,model_sha256=hashlib.sha256(data).hexdigest(),protocol_sha256=hashlib.sha256((BASE/'PROTOCOL.json').read_bytes()).hexdigest(),precision=44,prices=prices,transformed_lower=u,lower=L,upper=upper,policy=policy,upper_origin=origin,upper_source_sha256=source_hash,target='1/1000')
        out=R/'proofs'/name;out.mkdir(parents=True,exist_ok=True)
        binary=gzip.compress(json.dumps(proof,default=str,separators=(',',':')).encode(),mtime=0)
        (out/f'{method}.json.gz').write_bytes(binary)
        result=dict(name=name,method=method,lower=str(L),upper=str(upper),gap=float(upper-L),relative_gap=float((upper-L)/upper) if upper else 0,target_met=upper-L<=F(1,1000),proof_sha256=hashlib.sha256(binary).hexdigest(),proof_bytes=len(binary),face_dimension=face_dimension,operating_seconds=operating_seconds,certificate_seconds=time.perf_counter()-tl,total_seconds=time.perf_counter()-ts,upper_origin=origin,**meta)
        output.append(result);print(json.dumps(result),flush=True)
    (R/'results').mkdir(exist_ok=True)
    (R/'results'/f'{name}.json').write_text(json.dumps(output,indent=2)+'\n')
    return output

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('names',nargs='+');args=ap.parse_args()
    for name in args.names:run(name)
