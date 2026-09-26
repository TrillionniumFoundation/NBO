"""Shared-regret-budget covering search; exact node Bellman programs.
R48 is used only to construct outward witnesses and repair candidate policies.
The lower bound is reconstructed from raw primitives by check_budget.py.
"""
from __future__ import annotations
import sys,time,heapq,json,gzip,hashlib,resource
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'2026-09-26-r48'/'replication'))
import core
Z=F(0); O=F(1)

def row_min(values, gaps, cap):
    candidates=[]; m=len(values)
    for a in range(m):
        if gaps[a]<=cap:
            p=[Z]*m; p[a]=O; candidates.append((values[a],p))
        for b in range(a):
            if (gaps[a]-cap)*(gaps[b]-cap)<0:
                z=(cap-gaps[b])/(gaps[a]-gaps[b]); p=[Z]*m; p[a]=z; p[b]=1-z
                candidates.append((core.dot(p,values),p))
    return min(candidates,key=lambda c:c[0]) if candidates else None

def node(d,w,box,prices=None):
    n,T,m=d['n'],d['T'],d['m']; beta=d['beta']; eps=d['epsilon']
    low=[[Z]*n for _ in range(T+1)]; high=[[eps]*n for _ in range(T)]+[[Z]*n]
    for t in range(1,T):
        for i in range(n): low[t][i],high[t][i]=box[(t-1)*n+i]
    C=[[Z]*n for _ in range(T+1)]; p=[[[Z]*m for _ in range(n)] for _ in range(T)]
    for t in reversed(range(T)):
        for i in range(n):
            gaps=[w['dl'][t][i][a]+beta*core.dot(d['P'][t][i][a],low[t+1]) for a in range(m)]
            values=[d['k'][t][i][a]+beta*core.dot(d['P'][t][i][a],C[t+1]) for a in range(m)]
            ans=row_min(values,gaps,high[t][i])
            if ans is None:return dict(infeasible=True,where=[t,i])
            C[t][i],p[t][i]=ans
    raw=core.dot(d['nu'],C[0]); cost_policy=p
    if prices is not None:
        lam=prices['field'];V=[[Z]*n for _ in range(T+1)];pp=[[[Z]*d['m'] for _ in range(n)] for _ in range(T)]
        for t in reversed(range(T)):
            for i in range(n):
                gaps=[w['dl'][t][i][a]+beta*core.dot(d['P'][t][i][a],low[t+1]) for a in range(m)]
                vv=[V[t+1][j]+min((lam[t][i]-lam[t+1][j])*low[t+1][j],(lam[t][i]-lam[t+1][j])*high[t+1][j]) for j in range(n)]
                values=[d['k'][t][i][a]+lam[t][i]*w['dl'][t][i][a]+beta*core.dot(d['P'][t][i][a],vv) for a in range(m)]
                ans=row_min(values,gaps,high[t][i]);V[t][i]=max(lam[t][i]*low[t][i],ans[0]);pp[t][i]=ans[1]
        raw=max(raw,sum((d['nu'][i]*max(Z,V[0][i]-lam[0][i]*eps) for i in range(n)),Z))
        p=pp
    return dict(infeasible=False,lower=raw,policy=p,cost_policy=cost_policy)

def run(d,target=F(1,1000),seconds=10,nodes=511,local_seconds=1):
    start=time.perf_counter(); w=core.witness(d,target)
    p,U,_=core.repair(d,w,greedy=True); initial=U; local={}
    if local_seconds>0:
        q,local=core.local_proposal(d,w,p,min(local_seconds,seconds/4))
        q,u,_=core.repair(d,w,q)
        if u<U:p,U=q,u
    prices=core.prices(d,w,min(2,seconds/5))
    n,T=d['n'],d['T']; root=[(Z,d['epsilon'])]*(n*(T-1))
    tree=[]; frontier=[]; trajectories=[]; root_lower=None
    def add(box,parent=None,depth=0):
        nonlocal p,U,root_lower
        a=node(d,w,box,prices); idx=len(tree)
        row=dict(id=idx,parent=parent,depth=depth,children=[],box=box,infeasible=a['infeasible'])
        if a['infeasible']:
            row['where']=a['where'];tree.append(row);return idx
        row['raw_lower']=a['lower'];row['lower']=max(Z,a['lower'],tree[parent]['lower'] if parent is not None else Z)
        if root_lower is None:root_lower=row['lower']
        q,u,_=core.repair(d,w,a['policy'])
        qc,uc,_=core.repair(d,w,a['cost_policy'])
        if uc<u:q,u=qc,uc
        if u<U:p,U=q,u
        J,_=core.policy_value(d,a['policy']); row['candidate_upper']=u
        if box:
            scores=[]
            for j,(l,h) in enumerate(box):
                t,i=divmod(j,n); t+=1
                # Focus on disagreement between actual candidate regret and allocated budget.
                violation=max(Z,w['hi'][t][i]-J[t][i]-h)
                scores.append((h-l)*(violation+d['epsilon']/100))
            split=max(range(len(box)),key=lambda j:box[j][1]-box[j][0]) if depth%4==0 else max(range(len(box)),key=lambda j:scores[j])
            row['split_coordinate']=split
        tree.append(row);heapq.heappush(frontier,(row['lower'],idx));return idx
    add(root)
    stop='target'
    while frontier:
        L=min(U,frontier[0][0]);trajectories.append(dict(seconds=time.perf_counter()-start,lower=L,upper=U,nodes=len(tree)))
        if U-L<=target:break
        if time.perf_counter()-start>=seconds:stop='time';break
        if len(tree)+2>nodes:stop='nodes';break
        lb,idx=heapq.heappop(frontier);r=tree[idx];box=r['box']
        if not box:stop='atomic';heapq.heappush(frontier,(lb,idx));break
        j=r['split_coordinate'];a,b=box[j];mid=(a+b)/2
        left=list(box);right=list(box);left[j]=(a,mid);right[j]=(mid,b)
        c1=add(left,idx,r['depth']+1);c2=add(right,idx,r['depth']+1);r['children']=[c1,c2]
    L=min(U,min((v for v,i in frontier),default=U))
    result=dict(schema='nbo-r50-budget-v1',model=core.enc(d),target=target,lower=L,upper=U,initial_upper=initial,root_lower=root_lower,policy=p,witness=w,prices=prices,tree=tree,trajectory=trajectories,stop=stop,construction_seconds=time.perf_counter()-start,local=local,budget_dimension=len(root),probability_dimension=n*T*d['m'])
    return result

if __name__=='__main__':
    import argparse
    from check_budget import verify
    ap=argparse.ArgumentParser();ap.add_argument('model');ap.add_argument('output');ap.add_argument('--seconds',type=float,default=10);ap.add_argument('--nodes',type=int,default=511);a=ap.parse_args()
    start=time.perf_counter(); raw=json.loads(Path(a.model).read_text());d=core.load(raw);core.validate(d)
    r=run(d,seconds=a.seconds,nodes=a.nodes); enc=core.enc(r)
    binary=gzip.compress(json.dumps(enc,sort_keys=True,separators=(',',':')).encode(),mtime=0)
    Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_bytes(binary)
    ts=time.perf_counter();checked=verify(enc,raw);vt=time.perf_counter()-ts
    summary={k:v for k,v in enc.items() if k not in ['model','tree','policy','witness','prices']}
    summary.update(verification=checked,verify_seconds=vt,all_in_seconds=time.perf_counter()-start,proof_bytes=len(binary),proof_sha256=hashlib.sha256(binary).hexdigest(),peak_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
    Path(a.output+'.summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(raw.get('name',a.model),checked,'seconds',summary['all_in_seconds'],'nodes',len(r['tree']),flush=True)
