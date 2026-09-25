#!/usr/bin/env python3
"""Independent, optimizer-free exact arithmetic reconstruction for R42.
No constructor imports, NumPy, SciPy, or stored value-function arrays.
"""
import argparse,copy,gzip,json,time
from fractions import Fraction as Q
from pathlib import Path

def verify(obj):
    assert obj['schema']=='NBO-R42-exogenous-exact-v1'
    d=obj['model'];n,T,m=(d[k] for k in ('n','T','m'))
    beta=Q(d['beta']);eps=Q(d['epsilon']); assert 0<beta<=1 and eps>0
    P=[[Q(x) for x in row] for row in d['P']]
    r=[[Q(x) for x in row] for row in d['r']]
    k=[[Q(x) for x in row] for row in d['k']]
    nu=[Q(x) for x in d['nu']]
    assert len(P)==len(r)==len(k)==len(nu)==n
    assert sum(nu)==1 and min(nu)>=0
    for i in range(n):
        assert len(P[i])==n and sum(P[i])==1 and min(P[i])>=0
        assert len(r[i])==len(k[i])==m and min(k[i])>=0
        # Independently rederive the declared service economy.
        demand=Q(2*i+1,2*n)
        rr=[-(demand-Q(a,m-1))**2 for a in range(m)]
        installed=max(0,max(range(m),key=lambda a:rr[a])-1)
        kk=[Q(0) if a==installed else 1+demand+Q(abs(a-installed),m-1) for a in range(m)]
        assert r[i]==rr and k[i]==kk and nu[i]==Q(2*(i+1),n*(n+1))
        for j in range(n):
            if d['kind']=='dense': v=Q(1,2*n)+(Q(1,2) if i==j else 0)
            elif d['kind']=='cycle': v=Q(3,4) if i==j else (Q(1,4) if j==(i+1)%n else Q(0))
            elif d['kind']=='band':
                v=Q(1+min(i,j)%3,16) if abs(i-j)==1 else Q(0)
                if i==j:v=1-(Q(1+(i-1)%3,16) if i else 0)-(Q(1+i%3,16) if i+1<n else 0)
            else:raise AssertionError('unknown primitive family')
            assert P[i][j]==v
    p=[[[Q(x) for x in row] for row in date] for date in obj['policy']]
    assert len(p)==T
    for date in p:
        assert len(date)==n
        for row in date:assert len(row)==m and min(row)>=0 and sum(row)==1
    # Direct scalar Bellman reconstruction; do not trust stored regret/costs.
    loss=[[max(rr)-v for v in rr] for rr in r]
    nextD=[Q(0)]*n;nextC=[Q(0)]*n;maxD=Q(0)
    for t in reversed(range(T)):
        D=[];C=[]
        for i in range(n):
            dd=sum(p[t][i][a]*loss[i][a] for a in range(m))+beta*sum(P[i][j]*nextD[j] for j in range(n))
            cc=sum(p[t][i][a]*k[i][a] for a in range(m))+beta*sum(P[i][j]*nextC[j] for j in range(n))
            assert 0<=dd<=eps;D.append(dd);C.append(cc);maxD=max(maxD,dd)
        nextD,nextC=D,C
    upper=sum(nu[i]*nextC[i] for i in range(n))
    ys=[Q(v) for v in obj['dual_simplex']]; yd=[Q(v) for v in obj['dual_loss']]
    assert len(ys)==len(yd)==n*T
    bound=sum(ys); occ=nu[:]
    for t in range(T):
        for i in range(n):
            for a in range(m):
                rc=beta**t*occ[i]*k[i][a]-ys[t*n+i]+loss[i][a]*yd[t*n+i]
                if rc<0:bound+=rc
            rd=-yd[t*n+i]
            if t>0:rd+=beta*sum(P[j][i]*yd[(t-1)*n+j] for j in range(n))
            if rd<0:bound+=rd*eps
        occ=[sum(occ[i]*P[i][j] for i in range(n)) for j in range(n)]
    lower=max(Q(0),bound)
    s=obj['results'];assert Q(s['upper'])==upper and Q(s['lower'])==lower
    assert Q(s['gap'])==upper-lower>=0 and Q(s['max_regret'])==maxD
    assert Q(s['relative_gap'])==((upper-lower)/upper if upper else 0)
    return dict(passed=True,n=n,T=T,m=m,lower=str(lower),upper=str(upper),gap=str(upper-lower),
                all_restart_checks=n*T,action_probability_checks=n*T*m,arithmetic='Python Fraction; optimizer-free independent reconstruction')

def mutations(obj):
    tests=[]
    for name in ('negative_probability','forged_upper','forged_lower','invalid_kernel'):
        x=copy.deepcopy(obj)
        if name=='negative_probability':x['policy'][0][0][0]='-1'
        if name=='forged_upper':x['results']['upper']=str(Q(x['results']['upper'])-1)
        if name=='forged_lower':x['results']['lower']=str(Q(x['results']['lower'])+1)
        if name=='invalid_kernel':x['model']['P'][0][0]='2'
        try:verify(x)
        except (AssertionError,ValueError):tests.append(dict(name=name,rejected=True))
        else:raise AssertionError('mutation accepted: '+name)
    return tests

def main():
    ap=argparse.ArgumentParser();ap.add_argument('proof');ap.add_argument('--out');ap.add_argument('--mutations',action='store_true');a=ap.parse_args()
    with gzip.open(a.proof,'rt') as f:o=json.load(f)
    st=time.perf_counter();v=verify(o);v['seconds']=time.perf_counter()-st
    if a.mutations:v['mutation_tests']=mutations(o)
    text=json.dumps(v,indent=2,sort_keys=True)
    if a.out:Path(a.out).write_text(text+'\n')
    print(text)
if __name__=='__main__':main()
