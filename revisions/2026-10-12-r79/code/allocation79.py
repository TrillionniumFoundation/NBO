"""Exact controller-allocation certificates from the pinned R77 cost family.

No fitting, new simulations, empirical fees or retiming. A small independent
basis-enumeration LP solver verifies both primal and dual rational witnesses.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import itertools,json,time
import decision78 as d
R=Path(__file__).resolve().parents[1]

def linear_solve(A,b):
    n=len(b)
    if len(A)!=n or any(len(r)!=n for r in A):raise ValueError('Square system required')
    a=[list(map(F,row))+[F(y)] for row,y in zip(A,b)]
    for j in range(n):
        k=next((i for i in range(j,n) if a[i][j]),None)
        if k is None:return None
        a[j],a[k]=a[k],a[j];v=a[j][j];a[j]=[x/v for x in a[j]]
        for i in range(n):
            if i!=j:
                v=a[i][j]
                if v:a[i]=[x-v*y for x,y in zip(a[i],a[j])]
    return [row[-1] for row in a]

def simplex(p,n):
    if len(p)!=n:raise ValueError('Wrong probability dimension')
    p=list(map(F,p))
    if any(x<0 for x in p) or sum(p)!=1:raise ValueError('Invalid probability simplex')
    return p

def matrix(dist,charges):
    n=len(dist)-1;w=list(map(F,charges))
    if n<1 or len(w)!=n or any(len(r)!=n+1 for r in dist):raise ValueError('Wrong cost dimensions')
    return [[F(dist[j+1][i+1])+w[i]-w[j] for i in range(n)] for j in range(n)]

def certificate(H,p,lam):
    rows=len(H)
    if rows<1 or len(H[0])<1 or any(len(r)!=len(H[0]) for r in H):raise ValueError('Nonempty rectangular matrix required')
    n=len(H[0]);p=simplex(p,n);lam=simplex(lam,rows)
    row=[sum(F(x)*y for x,y in zip(r,p)) for r in H]
    col=[sum(lam[j]*F(H[j][i]) for j in range(rows)) for i in range(n)]
    L=min(col);U=max(row)
    if L>U:raise AssertionError('Primal dual order violated')
    return dict(lower=L,upper=U,gap=U-L,p=p,dual=lam,row_payoffs=row,column_payoffs=col)

def solve_game(H):
    """Independent exact basis enumeration; deliberately for small catalogues."""
    H=[list(map(F,r)) for r in H];m=len(H)
    if m<1 or not H[0] or any(len(r)!=len(H[0]) for r in H):raise ValueError('Invalid matrix')
    n=len(H[0]);visited=0
    for k in range(1,min(m,n)+1):
        for S in itertools.combinations(range(n),k):
            for J in itertools.combinations(range(m),k):
                visited+=1
                A=[[H[j][i] for i in S]+[F(-1)] for j in J]+[[F(1)]*k+[F(0)]]
                x=linear_solve(A,[F(0)]*k+[F(1)])
                if x is None or min(x[:-1])<0:continue
                p=[F(0)]*n
                for i,v in zip(S,x[:-1]):p[i]=v
                if any(sum(r[i]*p[i] for i in range(n))>x[-1] for r in H):continue
                B=[[H[j][i] for j in J]+[F(-1)] for i in S]+[[F(1)]*k+[F(0)]]
                y=linear_solve(B,[F(0)]*k+[F(1)])
                if y is None or min(y[:-1])<0:continue
                lam=[F(0)]*m
                for j,v in zip(J,y[:-1]):lam[j]=v
                rec=certificate(H,p,lam)
                if rec['gap']==0:
                    rec['bases_examined']=visited;return rec
    raise AssertionError('No exact primal-dual equilibrium found')

def two_policy(l,u,f):
    l,u,f=map(F,(l,u,f))
    if l>u:raise ValueError('Reversed gain interval')
    if f<=l:return F(1),F(0)
    if f>=u:return F(0),F(0)
    return (u-f)/(u-l),(f-l)*(u-f)/(u-l)

def cohort(l,u,f,m,setup=0):
    if not isinstance(m,int) or m<1:raise ValueError('Positive integer cohort required')
    l,u,f,setup=map(F,(l,u,f,setup))
    if setup<0:raise ValueError('Nonnegative extra setup required')
    p,_=two_policy(l,u,f);a=p*m;k=a.numerator//a.denominator
    candidates=sorted(set([0,m,k,min(k+1,m)]))
    def score(k):
        x=F(k,m)
        return max(x*(f-l),(1-x)*(u-f))+(setup if 0<k<m else 0)
    best=min(score(k) for k in candidates)
    return dict(k=[k for k in candidates if score(k)==best],regret=best,candidates=candidates)

def installed_game(H,m,installation):
    n=len(H)
    if m<=0:raise ValueError('Positive deployment count required')
    if any(len(r)!=n for r in H):raise ValueError('Square catalogue required')
    costs={tuple(sorted(S)):F(k) for S,k in installation.items()}
    subsets=[S for k in range(1,n+1) for S in itertools.combinations(range(n),k)]
    if set(costs)!=set(subsets):raise ValueError('Every nonempty installed subset required')
    for S in subsets:
        if any(costs[S]<costs[(i,)] for i in S):raise ValueError('Installation monotonicity required')
    entries=[]
    for S in subsets:
        B=[[F(H[j][i])+(costs[S]-costs[(j,)])/m for i in S] for j in range(n)]
        rec=solve_game(B);rec['installed']=S;entries.append(rec)
    best=min(x['upper'] for x in entries)
    return dict(value=best,solutions=[x for x in entries if x['upper']==best],all_subset_certificates=entries)

def encode(v):
    if isinstance(v,F):return str(v)
    if isinstance(v,dict):return {str(k):encode(x) for k,x in v.items()}
    if isinstance(v,(tuple,list)):return [encode(x) for x in v]
    return v

def main():
    start=time.perf_counter();source=R/'results77/summary.json'
    if d.sha(source)!=d.SOURCE_SHA:raise AssertionError('Pinned cost data changed')
    s=json.loads(source.read_text());names,edges,_=d.edges_from_summary(s);D=d.closure(len(names)+1,edges)
    if D!=d.independent_closure(len(names)+1,edges):raise AssertionError('Independent closure mismatch')
    n=len(names);ia=names.index('relu-n16');ib=names.index('relu-n8')
    l=-D[ib+1][ia+1];u=D[ia+1][ib+1];width=u-l
    if not 0<l<u:raise AssertionError('Retained fee interval not positive and nondegenerate')
    potentials=d.potentials(D)[1:]
    for theta in potentials:
        if any(theta[b]-theta[a]>c for a,b,c in edges):raise AssertionError('Invalid attaining potential')
    records=[]
    for t in (-l/width,F(0),F(1,4),F(1,2),F(3,4),F(1),F(5,4)):
        f=l+t*width;w=[F(0)]*n;w[ia]=f;H=matrix(D,w)
        game=solve_game(H);pstar,V=two_policy(l,u,f)
        p=[F(0)]*n;p[ia]=pstar;p[ib]=1-pstar
        expected=certificate(H,p,game['dual'])
        if expected['gap'] or V!=game['upper']:raise AssertionError('Full catalogue and two-policy formula disagree')
        values=[]
        for theta in potentials:
            values.append(sum(p[i]*(theta[i+1]+w[i]) for i in range(n))-min(theta[j+1]+w[j] for j in range(n)))
        if max(values)!=V:raise AssertionError('Mixed regret is not attained')
        pure=min(d.regrets(D,w));threshold=pure-V
        cohorts=[]
        for m in (1,2,3,8,64):
            rec=cohort(l,u,f,m);brute=[max(F(k,m)*(f-l),(1-F(k,m))*(u-f)) for k in range(m+1)]
            if rec['regret']!=min(brute):raise AssertionError('Finite-cohort minimum mismatch')
            if l<f<u and rec['regret']-V>max(f-l,u-f)/(2*m):raise AssertionError('Cohort rounding bound')
            cohorts.append(dict(m=m,**rec))
        records.append(dict(relative_fee=t,fee=f,allocation=p,dual=game['dual'],regret=V,
            best_pure_regret=pure,extra_setup_break_even=threshold,exact_lp_gap=game['gap'],
            bases_examined=game['bases_examined'],attaining_row=values.index(V)+1,cohorts=cohorts))
    mid=next(x for x in records if x['relative_fee']==F(1,2))
    if mid['regret']!=width/4 or mid['best_pure_regret']!=width/2:raise AssertionError('Midpoint improvement factor')
    setup_records=[]
    H=[[F(0),width/2],[width/2,F(0)]]
    for k in (F(0),width/8,width/4,width/2):
        installed=installed_game(H,1,{(0,):0,(1,):0,(0,1):k})
        if installed['value']!=min(width/2,width/4+k):raise AssertionError('Installation regime mismatch')
        setup_records.append(dict(extra_setup=k,**installed))
    result=dict(status='passed',cost_source_sha256=d.sha(source),source_rows=s['rows'],new_simulation_rows=0,
        new_training_services=0,scientific_clocks_replaced=False,policies=names,gain_lower=l,gain_upper=u,
        fee_width=width,midpoint_fee=(l+u)/2,midpoint_mixed_regret=width/4,midpoint_pure_regret=width/2,
        matrix_game_records=records,installed_subset_records=setup_records,attaining_potentials=potentials,
        exact_full_catalogue_lp_probes=len(records),finite_cohort_probes=sum(len(x['cohorts']) for x in records),
        literature='Manski (2004), Econometrica 72(4), 1221-1246; conditional qualified-cost minimax regret, not a new statistical-risk theorem',
        scope='Exact postprocessing of the pinned simultaneous cost set. Allocations concern complete controllers before acquisition. Conditional price scenarios are not measured setup costs or additional deployments.',
        seconds=time.perf_counter()-start)
    d.save(R/'audit/ALLOCATION79.json',encode(result))
    text=r'''\begin{table}[htbp]
\centering
\caption{Qualified acquisition-fee choices and deployment allocations}\label{tab:allocation79}
{\small\setlength{\tabcolsep}{4pt}
\begin{tabular}{rrrrr}\hline
Fee position & Fine share & Pure regret upper & Mixed regret upper & Setup saving lower \\\hline
'''
    for rec in records[1:-1]:
        text+=' & '.join([str(rec['relative_fee']),str(rec['allocation'][ia]),d.decimal(rec['best_pure_regret'],False,8),d.decimal(rec['regret'],False,8),d.decimal(rec['extra_setup_break_even'],True,8)])+r' \\'+'\n'
    text+=r'''\hline\end{tabular}}
\par\smallskip{\footnotesize Fee position $t$ means $f=l+t(u-l)$. Both controllers were qualified under the original law; a share selects an entire controller before information acquisition. Regret is worst-case expected loss relative to the best single catalogue controller. The last column is the largest extra normalized cost of maintaining both controllers compatible with strict improvement; equality gives a tie. Values are outward rounded. No row is a new simulation or a calibrated installation fee.}
\end{table}
'''
    (R/'tables').mkdir(exist_ok=True);(R/'tables/allocation79.tex').write_text(text)
    print(json.dumps(encode({k:result[k] for k in ('status','gain_lower','gain_upper','midpoint_fee','midpoint_mixed_regret','midpoint_pure_regret','exact_full_catalogue_lp_probes','finite_cohort_probes','seconds')}),indent=2))
if __name__=='__main__':main()
