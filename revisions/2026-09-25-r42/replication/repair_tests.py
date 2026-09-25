#!/usr/bin/env python3
"""Exact tests of the finite-horizon slack ladder for action-dependent kernels."""
from fractions import Fraction as Q
import json,random
from pathlib import Path

def norm_weights(rng,n):
    x=[rng.randrange(1,10) for _ in range(n)];return [Q(v,sum(x)) for v in x]
def evaluate(p,P,r,k,beta,g):
    T=len(p);n=len(g);J=[None]*T+[g];C=[None]*T+[[Q(0)]*n]
    for t in reversed(range(T)):
        J[t]=[sum(p[t][i][a]*(r[t][i][a]+beta*sum(P[t][i][a][j]*J[t+1][j] for j in range(n))) for a in range(len(p[t][i]))) for i in range(n)]
        C[t]=[sum(p[t][i][a]*(k[t][i][a]+beta*sum(P[t][i][a][j]*C[t+1][j] for j in range(n))) for a in range(len(p[t][i]))) for i in range(n)]
    return J,C
rows=[]
for beta in (Q(1),Q(19,20),Q(4,5)):
 for T in (1,2,4,6):
  for seed in range(4):
    rng=random.Random(42000+seed+100*T);n=3;m=3
    P=[[[norm_weights(rng,n) for a in range(m)] for i in range(n)] for t in range(T)]
    r=[[[Q(rng.randrange(-8,9),8) for a in range(m)] for i in range(n)] for t in range(T)]
    k=[[[Q(rng.randrange(9),8) for a in range(m)] for i in range(n)] for t in range(T)]
    g=[Q(rng.randrange(-8,9),8) for i in range(n)]
    p=[[norm_weights(rng,m) for i in range(n)] for t in range(T)]
    V=[None]*T+[g]
    for t in reversed(range(T)):
      V[t]=[max(r[t][i][a]+beta*sum(P[t][i][a][j]*V[t+1][j] for j in range(n)) for a in range(m)) for i in range(n)]
    oldJ,oldC=evaluate(p,P,r,k,beta,g)
    peak=max(V[t][i]-oldJ[t][i] for t in range(T) for i in range(n));delta=peak/Q(10**6);eps=peak-delta/2
    z=Q(1,2)
    while eps*(z/2)**T>=delta:z/=2
    assert delta<=eps*z**T and 0<z<1
    tau=[eps*(1-z**(T-t)) for t in range(T+1)]
    q=[[row[:] for row in date] for date in p];after=[None]*T+[g]
    for t in reversed(range(T)):
      after[t]=[]
      for i in range(n):
        vals=[r[t][i][a]+beta*sum(P[t][i][a][j]*after[t+1][j] for j in range(n)) for a in range(m)]
        cur=sum(p[t][i][a]*vals[a] for a in range(m));b=V[t][i]-tau[t];best=max(range(m),key=lambda a:vals[a])
        if cur<b:
          al=(b-cur)/(vals[best]-cur);q[t][i]=[(1-al)*v for v in p[t][i]];q[t][i][best]+=al
        after[t].append(sum(q[t][i][a]*vals[a] for a in range(m)))
    newJ,newC=evaluate(q,P,r,k,beta,g);bound=2*z/(1+z)
    actual=max(sum(abs(q[t][i][a]-p[t][i][a]) for a in range(m))/2 for t in range(T) for i in range(n))
    dc=max(v for date in k for row in date for v in row)*sum((s+1)*beta**s for s in range(T))
    for t in range(T):
      for i in range(n):assert newJ[t][i]>=V[t][i]-tau[t] and newJ[t][i]>=oldJ[t][i]
    assert actual<=bound and max(newC[0][i]-oldC[0][i] for i in range(n))<=dc*bound
    rows.append(dict(beta=str(beta),T=T,seed=seed,delta=str(delta),epsilon=str(eps),z=str(z),actual_tv=str(actual),tv_bound=str(bound),passed=True))
Path(__file__).resolve().parents[1].joinpath('results/repair_tests.json').write_text(json.dumps(dict(schema='R42-action-dependent-slack-ladder-tests',passed=True,cases=rows),indent=2)+'\n')
print('passed',len(rows),'exact action-dependent repair tests')
