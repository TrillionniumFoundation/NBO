"""Independent exact reader of Borel lower bounds and whole-cell upper policies.
No numerical, generator, or constructor imports. Affine envelopes are integrated exactly, then rounded downward at 50 bits.
"""
from fractions import Fraction as Q
from itertools import combinations

def integrate_min(coeff,left,right):
    cuts=[left,right]
    for (a,b),(c,d) in combinations(coeff,2):
        if b!=d:
            x=(c-a)/(b-d)
            if left<x<right:cuts.append(x)
    cuts=sorted(set(cuts));v=Q(0)
    for x,y in zip(cuts,cuts[1:]):
        a,b=min(coeff,key=lambda z:z[0]+z[1]*(x+y)/2)
        v+=(y-x)*(a+b*(x+y)/2)
    return v

def verify(e,raw):
    assert e['schema']=='nbo-r50-diffuse-v1' and e['model']==raw
    assert raw['kernel']=='uniform-independent-reset' and raw['initial_law']=='uniform[0,1]'
    T,m,N=raw['T'],raw['m'],e['N'];beta=Q(raw['beta']);eps=Q(raw['epsilon']);ga=list(map(Q,raw['gamma']))
    assert T>=1 and m>=2 and N>=1 and 0<beta<1 and eps>0 and len(ga)==m and min(ga)>=0 and max(ga)==1
    g=[[Q(z) for z in v] for v in raw['g']];k=[[[Q(z) for z in c] for c in row] for row in raw['k']]
    assert len(g)==len(k)==T
    for t in range(T):
        assert g[t][0]>0 and sum(g[t])>0 and len(k[t])==m
        for a in range(m):assert k[t][a][0]>=0 and sum(k[t][a])>=0
    p=[[[Q(v) for v in row] for row in t] for t in e['policy']];M=[Q(0)]*(T+1);U=Q(0)
    assert len(p)==T
    for t in reversed(range(T)):
        assert len(p[t])==N
        for c in range(N):
            row=p[t][c];assert len(row)==m and min(row)>=0 and sum(row)==1
            mid=Q(2*c+1,2*N)
            for endpoint in (Q(c,N),Q(c+1,N)):
                d=sum((row[a]*(1-ga[a])*(g[t][0]+g[t][1]*endpoint) for a in range(m)),Q(0))
                assert d+beta*M[t+1]<=eps
            M[t]+=sum((row[a]*(1-ga[a])*(g[t][0]+g[t][1]*mid)/N for a in range(m)),Q(0))
            U+=beta**t*sum((row[a]*(k[t][a][0]+k[t][a][1]*mid)/N for a in range(m)),Q(0))
        M[t]+=beta*M[t+1]
    assert M==list(map(Q,e['moments'])) and U==Q(e['upper'])
    lam=[[Q(v) for v in row] for row in e['lambda_density']];q=list(map(Q,e['moment_prices']))
    assert len(lam)==len(q)==T and all(len(row)==N and min(row)>=0 for row in lam)
    avg=[sum(row)/N for row in lam];L=Q(0)
    for t in range(T):
        for c in range(N):
            coeff=[tuple(beta**t*k[t][a][j]+(lam[t][c]+q[t])*(1-ga[a])*g[t][j] for j in range(2)) for a in range(m)]
            z=integrate_min(coeff,Q(c,N),Q(c+1,N))
            scaled=z*(2**50)
            L+=Q(scaled.numerator//scaled.denominator,2**50)
        residual=-q[t]+(beta*(avg[t-1]+q[t-1]) if t else Q(0))
        L+=eps*min(Q(0),residual)-eps*avg[t]
    L=max(Q(0),L);assert L==Q(e['lower']) and L<=U
    return dict(valid=True,lower=str(L),upper=str(U),width=str(U-L),target_met=U-L<=Q(e['target']),whole_state=True,lower_policy_class='all-Borel')
