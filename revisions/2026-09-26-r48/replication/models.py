"""Prospectively specified R48 models. Imported without creating any instance.
All examples are designed computational environments, not estimated economies.
The finite fleet instances use exactly the original controlled affine maps.
"""
from fractions import Fraction as F
from hashlib import sha256
import random
import core
CASES=[(family,level) for family in ['warranty','inventory','queue','ties'] for level in range(3)]+[('fleet',0),('fleet',1)]

def generate(family,level):
    if family=='fleet': return fleet(level)
    rng=random.Random(int(sha256(f'NBO-r48-holdout-v1:{family}:{level}:2026-09-26'.encode()).hexdigest(),16))
    n=[3,5,8][level]; T=[4,8,12][level]; m=[3,3,4][level]; beta=[F(7,8),F(15,16),F(63,64)][level]; eps=[F(1,50),F(1,100),F(1,200)][level]
    P=[]; r=[]; k=[]
    for t in range(T):
        pt=[]; rt=[]; kt=[]
        for i in range(n):
            rowp=[]; rowr=[]
            installed=(i+t//3)%m if family=='ties' else 0
            rowk=[F(0) if a==installed else F(32+rng.randrange(33),32)*(1+F(i,4*n)) for a in range(m)]
            for a in range(m):
                weights=[rng.randrange(1,8) for _ in range(3)]; total=sum(weights)
                weights=[F(v,total) for v in weights]; dist=[F(0)]*n
                if family=='warranty':
                    succ=[max(0,min(n-1,i+shock-(2*a if a else 0))) for shock in [0,1,2]]
                    reward=F(n-i,n)-F(a,4)+F((i+t)%3,64)
                elif family=='inventory':
                    stock=min(n-1,i+a); succ=[max(0,stock-demand) for demand in [0,1,2]]
                    reward=sum((weights[z]*F(min(stock,z),2) for z in range(3)),F(0))-F(a,5)-F(stock,32)
                elif family=='queue':
                    succ=[min(n-1,max(0,i-a)+arrival) for arrival in [0,1,2]]
                    reward=-F(i*i,4*n)-F(a,5)+F((t+1)%2,64)
                else:
                    succ=[(i+1+a)%n,(i+2*a)%n,rng.randrange(n)]; reward=F(0)
                for j,prob in zip(succ,weights): dist[j]+=prob
                rowp.append(dist); rowr.append(reward)
            pt.append(rowp); rt.append(rowr); kt.append(rowk)
        P.append(pt); r.append(rt); k.append(kt)
    g=[F(n-i,4*n) if family=='warranty' else (F(i,8) if family=='inventory' else -F(i,8)) for i in range(n)]
    if family=='ties':
        # A model-building device; no potential or exact value is supplied to the solver.
        phi=[[F(2*i+3*t,16)+F((i+t)%2,8) for i in range(n)] for t in range(T+1)]
        g=phi[-1]
        for t in range(T):
            for i in range(n):
                tied={((t+i)%m),((t+i+1+(i%2))%m)}
                for a in range(m):
                    loss=F(0) if a in tied else F(1+(i+t+a)%3,64)*(F(1,16) if level==1 else F(1))
                    r[t][i][a]=phi[t][i]-beta*core.dot(P[t][i][a],phi[t+1])-loss
    weights=[1+(3*i+level)%7 for i in range(n)]
    if level==2: weights=[1 if i in [0,n-1] else 0 for i in range(n)]
    nu=[F(z,sum(weights)) for z in weights]
    return dict(name=f'{family}{level}',family=family,level=level,n=n,T=T,m=m,beta=beta,epsilon=eps,P=P,r=r,k=k,g=g,nu=nu,units='normalized realized implementation cost',design='new deterministic-hash development holdout; not empirical')

def fleet(level):
    T=2+level; m=3; beta=F(19,20); eps=F(1,100)
    slopes=[F(3,4),F(17,20),F(1,10)]; shifts=[[F(0),F(1,20)],[F(1,10),F(7,50)],[F(4,5),F(17,20)]]; probs=[F(3,5),F(2,5)]; expense=[F(0),F(3,20),F(9,20)]
    states=[[F(1,5),F(4,5)]]
    for t in range(T): states.append(sorted({slopes[a]*x+c for x in states[-1] for a in range(m) for c in shifts[a]}))
    n=max(len(s) for s in states[:-1]); P=[]; r=[]; k=[]
    for t in range(T):
        pt=[]; rt=[]; kt=[]; index={x:j for j,x in enumerate(states[t+1])}
        for i in range(n):
            rowp=[]; rowr=[]; rowk=[]
            for a in range(m):
                dist=[F(0)]*n
                if i>=len(states[t]): dist[0]=F(1); reward=F(0); cost=F(0)
                else:
                    x=states[t][i]; reward=x-expense[a]; cost=F(0) if a==0 else 1+x
                    if t==T-1:
                        reward+=beta*sum((q*(slopes[a]*x+c)/2 for q,c in zip(probs,shifts[a])),F(0)); dist[0]=F(1)
                    else:
                        for q,c in zip(probs,shifts[a]): dist[index[slopes[a]*x+c]]+=q
                rowp.append(dist); rowr.append(reward); rowk.append(cost)
            pt.append(rowp);rt.append(rowr);kt.append(rowk)
        P.append(pt);r.append(rt);k.append(kt)
    nu=[F(3,4),F(1,4)]+[F(0)]*(n-2)
    return dict(name=f'fleet{level}',family='fleet',level=level,n=n,T=T,m=m,beta=beta,epsilon=eps,P=P,r=r,k=k,g=[F(0)]*n,nu=nu,active_states=[len(x) for x in states],state_values=core.enc(states),units='500 dollars per normalized implementation cost',initial_contract='two observed conditions with weights 3/4 and 1/4; not uniform initial law',terminal_folded_into_last_reward=True,design='original affine controlled atoms, finite observed fleet; not empirical data')
