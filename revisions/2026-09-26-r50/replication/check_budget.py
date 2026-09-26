"""Standalone standard-library arithmetic reader. No optimizer or constructor imports."""
from fractions import Fraction as Q
from itertools import combinations

def rational(x):return [rational(v) for v in x] if isinstance(x,list) else Q(x)
def dot(x,y):return sum((a*b for a,b in zip(x,y)),Q(0))
def verify(proof,raw):
    assert proof['schema']=='nbo-r50-budget-v1' and proof['model']==raw
    n,T,m=raw['n'],raw['T'],raw['m'];b=Q(raw['beta']);eps=Q(raw['epsilon']);
    P,r,k,g,nu=[rational(raw[z]) for z in ['P','r','k','g','nu']]
    assert n>0 and T>0 and m>1 and 0<b<1 and eps>0 and sum(nu)==1 and min(nu)>=0
    for t in range(T):
        for i in range(n):
            for a in range(m):assert len(P[t][i][a])==n and min(P[t][i][a])>=0 and sum(P[t][i][a])==1 and k[t][i][a]>=0
    lo=rational(proof['witness']['lo']);hi=rational(proof['witness']['hi']);assert len(lo)==len(hi)==T+1
    for i in range(n):assert lo[T][i]<=g[i]<=hi[T][i]
    dl=[[[Q(0)]*m for _ in range(n)] for _ in range(T)]
    for t in reversed(range(T)):
        for i in range(n):
            assert lo[t][i]<=max(r[t][i][a]+b*dot(P[t][i][a],lo[t+1]) for a in range(m))
            assert hi[t][i]>=max(r[t][i][a]+b*dot(P[t][i][a],hi[t+1]) for a in range(m))
            for a in range(m):dl[t][i][a]=max(Q(0),lo[t][i]-r[t][i][a]-b*dot(P[t][i][a],hi[t+1]))
    p=rational(proof['policy']);J=[list(g) for _ in range(T+1)];C=[[Q(0)]*n for _ in range(T+1)]
    for t in reversed(range(T)):
        for i in range(n):
            assert len(p[t][i])==m and min(p[t][i])>=0 and sum(p[t][i])==1
            J[t][i]=dot(p[t][i],[r[t][i][a]+b*dot(P[t][i][a],J[t+1]) for a in range(m)])
            C[t][i]=dot(p[t][i],[k[t][i][a]+b*dot(P[t][i][a],C[t+1]) for a in range(m)])
            assert J[t][i]>=hi[t][i]-eps
    U=dot(nu,C[0]);assert U==Q(proof['upper'])
    lam=rational(proof['prices']['field']);assert len(lam)==T+1 and all(x>=0 for row in lam for x in row) and all(x==0 for x in lam[T])
    tree=proof['tree'];assert tree and tree[0]['parent'] is None
    root=[[Q(0),eps] for _ in range(n*(T-1))];seen=set();leaves=[]
    def visit(idx,expected,parent,parent_lb):
        assert idx not in seen;seen.add(idx);rec=tree[idx];assert rec['id']==idx and rec['parent']==parent
        box=rational(rec['box']);assert box==expected
        for l,h in box:assert 0<=l<=h<=eps
        lower=[[Q(0)]*n for _ in range(T+1)];upper=[[eps]*n for _ in range(T)]+[[Q(0)]*n]
        for t in range(1,T):
            for i in range(n):lower[t][i],upper[t][i]=box[(t-1)*n+i]
        V=[[Q(0)]*n for _ in range(T+1)];infeasible=False
        for t in reversed(range(T)):
            for i in range(n):
                acoef=[dl[t][i][a]+b*dot(P[t][i][a],lower[t+1]) for a in range(m)]
                ccoef=[k[t][i][a]+b*dot(P[t][i][a],V[t+1]) for a in range(m)]
                cap=upper[t][i];choices=[ccoef[a] for a in range(m) if acoef[a]<=cap]
                for a,j in combinations(range(m),2):
                    if (acoef[a]-cap)*(acoef[j]-cap)<0:
                        w=(cap-acoef[j])/(acoef[a]-acoef[j]);choices.append(w*ccoef[a]+(1-w)*ccoef[j])
                if not choices:infeasible=True;break
                V[t][i]=min(choices)
            if infeasible:break
        assert rec['infeasible']==infeasible
        if infeasible:assert not rec['children'];return
        raw_lb=dot(nu,V[0])
        W=[[Q(0)]*n for _ in range(T+1)]
        for t in reversed(range(T)):
            for i in range(n):
                ac=[dl[t][i][a]+b*dot(P[t][i][a],lower[t+1]) for a in range(m)]
                shifted=[W[t+1][j]+min((lam[t][i]-lam[t+1][j])*lower[t+1][j],(lam[t][i]-lam[t+1][j])*upper[t+1][j]) for j in range(n)]
                cc=[k[t][i][a]+lam[t][i]*dl[t][i][a]+b*dot(P[t][i][a],shifted) for a in range(m)]
                cap=upper[t][i];choices=[cc[a] for a in range(m) if ac[a]<=cap]
                for a,j in combinations(range(m),2):
                    if (ac[a]-cap)*(ac[j]-cap)<0:
                        z=(cap-ac[j])/(ac[a]-ac[j]);choices.append(z*cc[a]+(1-z)*cc[j])
                W[t][i]=max(lam[t][i]*lower[t][i],min(choices))
        raw_lb=max(raw_lb,sum((nu[i]*max(Q(0),W[0][i]-lam[0][i]*eps) for i in range(n)),Q(0)));lb=max(Q(0),raw_lb,parent_lb)
        assert raw_lb==Q(rec['raw_lower']) and lb==Q(rec['lower'])
        ch=rec['children']
        if ch:
            assert len(ch)==2
            j=rec['split_coordinate'];assert 0<=j<len(box);l,h=box[j];assert l<h
            mid=(l+h)/2;left=[list(z) for z in box];right=[list(z) for z in box];left[j]=[l,mid];right[j]=[mid,h]
            visit(ch[0],left,idx,lb);visit(ch[1],right,idx,lb)
        else:leaves.append(lb)
    visit(0,root,None,Q(0));assert len(seen)==len(tree)
    L=min([U]+leaves);assert L==Q(proof['lower']) and L<=U
    return dict(valid=True,lower=str(L),upper=str(U),width=str(U-L),target_met=U-L<=Q(proof['target']),nodes=len(tree))
