"""Three known-model families. Parameters are designed, not calibrated data."""
from fractions import Fraction as F
import random, json
from pathlib import Path

def create(family,seed,n,T,m,beta,epsilon):
    if family=='maintenance':
        from global_solver import old
        x=old.model(seed,n,T,m,beta,epsilon); x['family']=family; return x
    rng=random.Random(seed); P=[]; r=[]; k=[]
    w0=rng.randrange(1,3); w1=rng.randrange(3,5); probs=[F(w0,8),F(w1,8),F(8-w0-w1,8)]
    for i in range(n):
        ps=[]; rs=[]; ks=[]
        installed=min(m-1,max(0,n//2-i)) if family=='inventory' else (1 if i<n//2 else min(2,m-1))
        for a in range(m):
            row=[F(0)]*n; reward=F(0)
            for shock,prob in enumerate(probs):
                if family=='inventory':
                    order=min(a,n-1-i); stocked=i+order; sold=min(stocked,shock); nxt=stocked-sold
                    payoff=F(2*sold,n)-F(3*order,4*n)-F(nxt,5*n)-F(max(0,shock-stocked),2*n)
                elif family=='queue':
                    nxt=min(n-1,max(0,i-a)+shock); payoff=-F(i,n)-F(a*a,3*m*m)-F(max(0,i-a+shock-(n-1)),n)
                else: raise ValueError(family)
                row[nxt]+=prob; reward+=prob*payoff
            ps.append(row); rs.append(reward); ks.append((F(1)+F(i,n))*int(a!=installed))
        P.append(ps); r.append(rs); k.append(ks)
    return dict(family=family,seed=seed,n=n,T=T,m=m,beta=F(beta),epsilon=F(epsilon),P=P,r=r,k=k,
                terminal=[F(i,4*n) if family=='inventory' else -F(i,2*n) for i in range(n)],nu=[F(1,n)]*n)

def tie(tau,n=4,T=8):
    tau=F(tau); P=[]; r=[]; k=[]
    for i in range(n):
        rows=[]
        for a in range(3):
            row=[F(0)]*n
            for j,w in [(i,F(1,2)),(((i+1)%n if a==0 else (max(0,i-1) if a==1 else 0)),F(1,2))]: row[j]+=w
            rows.append(row)
        P.append(rows); r.append([F(0),-tau,-F(1,5)-F(i,10*n)]); k.append([F(1)+F(i,n),F(7,10)+F(i,2*n),F(0)])
    return dict(family='near_tie',seed=0,n=n,T=T,m=3,beta=F(19,20),epsilon=F(1,100),P=P,r=r,k=k,terminal=[F(0)]*n,nu=[F(1,n)]*n,tau=str(tau))

def specifications():
    dimensions=[(4,4,3,'9/10','1/100'),(8,8,3,'19/20','1/100'),(8,16,4,'19/20','1/200'),(16,32,4,'19/20','1/1000')]
    return [dict(name=f'{family}{j}',family=family,seed=440101+fi*10+j,n=n,T=T,m=m,beta=beta,epsilon=eps)
            for fi,family in enumerate(['maintenance','inventory','queue']) for j,(n,T,m,beta,eps) in enumerate(dimensions)]

if __name__=='__main__':
    dest=Path(__file__).resolve().parents[1]/'models'; dest.mkdir(exist_ok=True)
    for spec in specifications():
        name=spec['name']; args={k:v for k,v in spec.items() if k!='name'}
        (dest/f'{name}.json').write_text(json.dumps(create(**args),default=str,indent=2)+'\n')
    for j,tau in enumerate(['0','1/100000000','1/10000','1/100']):
        (dest/f'tie{j}.json').write_text(json.dumps(tie(tau),default=str,indent=2)+'\n')
