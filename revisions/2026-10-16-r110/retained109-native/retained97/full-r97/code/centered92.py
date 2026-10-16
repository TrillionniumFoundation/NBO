"""Exact reference-centered AVaR kernels. No floating LP status is a certificate."""
from __future__ import annotations
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from typing import Sequence


def rational(x):
    if isinstance(x, float):
        raise TypeError('Use exact rational inputs, not binary floating point')
    return F(x)


def probability(p):
    p=tuple(map(rational,p))
    if not p or any(x<0 for x in p) or sum(p,F(0))!=1:
        raise ValueError('Nonempty exact probability vector required')
    return p


def dot(a,b):
    if len(a)!=len(b):raise ValueError('Dot-product dimensions')
    return sum((rational(x)*rational(y) for x,y in zip(a,b)),F(0))


@lru_cache(maxsize=None)
def vertices(p,alpha):
    p=probability(p);alpha=rational(alpha)
    if not 0<=alpha<1:raise ValueError('Risk level must be in [0,1)')
    caps=tuple(v/(1-alpha) for v in p);out=set();n=len(p)
    # A capped-simplex vertex has at most one coordinate off its bounds.
    for free in range(n):
        rest=[i for i in range(n) if i!=free]
        for mask in product((0,1),repeat=n-1):
            q=[F(0)]*n
            for i,b in zip(rest,mask):q[i]=caps[i] if b else F(0)
            q[free]=1-sum(q,F(0))
            if 0<=q[free]<=caps[free]:out.add(tuple(q))
    if not out:raise AssertionError('Nonempty capped simplex lost')
    return tuple(sorted(out))


def kernel(p,alpha,f):
    f=tuple(map(rational,f));qs=vertices(tuple(map(rational,p)),rational(alpha))
    values=tuple(dot(q,f) for q in qs);ref=max(values)
    gaps=tuple(ref-v for v in values)
    if min(gaps)!=0 or any(k<0 for k in gaps):raise AssertionError('Centered penalty')
    return {'q':qs,'k':gaps,'reference':ref}


def evaluate(k,z,indices=None):
    js=range(len(k['q'])) if indices is None else tuple(indices)
    js=tuple(js)
    if not js or len(set(js))!=len(js) or any(j<0 or j>=len(k['q']) for j in js):
        raise ValueError('Nonempty distinct valid risk-piece indices required')
    return max(dot(k['q'][j],z)-k['k'][j] for j in js)


def support_box(d,lo,hi):
    if len(d)!=len(lo) or len(lo)!=len(hi):raise ValueError('Box dimensions')
    if any(l>u for l,u in zip(lo,hi)):raise ValueError('Reversed error box')
    return sum((v*(u if v>0 else l) for v,l,u in zip(d,lo,hi)),F(0))


def safe_pieces(k,lo,hi):
    j0=min(range(len(k['q'])),key=lambda j:k['k'][j]);q0=k['q'][j0]
    kept=[];cuts=[]
    for j,q in enumerate(k['q']):
        support=support_box(tuple(x-y for x,y in zip(q,q0)),lo,hi)
        gap=k['k'][j]-k['k'][j0]
        if support<gap:cuts.append({'piece':j,'witness':j0,'support':support,'gap':gap})
        else:kept.append(j)
    if j0 not in kept:raise AssertionError('A reference witness was removed')
    return kept,cuts


def decode_model(m):
    T=int(m['T']);S=len(m['g']);A=len(m['c'][0][0])
    if T<1 or S<1 or A<1:raise ValueError('Positive dimensions required')
    p=[[[probability(v) for v in row] for row in layer] for layer in m['p']]
    c=[[[rational(v) for v in row] for row in layer] for layer in m['c']]
    f=[[rational(v) for v in row] for row in m['f']]
    g=list(map(rational,m['g']));beta=list(map(rational,m['beta']));alpha=rational(m['alpha'])
    if len(p)!=T or len(c)!=T or len(f)!=T+1 or len(beta)!=T or any(b<0 for b in beta):
        raise ValueError('Horizon or discount contract')
    if any(len(row)!=S for row in f) or any(len(layer)!=S for layer in p+c):raise ValueError('State dimensions')
    if any(len(row)!=A for layer in p+c for row in layer):raise ValueError('Action dimensions')
    if any(len(v)!=S for layer in p for row in layer for v in row):raise ValueError('Successor dimensions')
    if not 0<=alpha<1:raise ValueError('Risk level')
    return T,S,A,p,c,f,g,beta,alpha


def prepare(m):
    T,S,A,p,c,f,g,beta,alpha=decode_model(m)
    kernels=[[[kernel(p[t][s][a],alpha,f[t+1]) for a in range(A)] for s in range(S)] for t in range(T)]
    r=[[[c[t][s][a]+beta[t]*kernels[t][s][a]['reference']-f[t][s] for a in range(A)] for s in range(S)] for t in range(T)]
    pi=[[min(range(A),key=lambda a:r[t][s][a]) for s in range(S)] for t in range(T)]
    return kernels,r,pi


def bounds(m,kernels,r,pi,radius):
    T,S,A,p,c,f,g,beta,alpha=decode_model(m);radius=rational(radius)
    if radius<0:raise ValueError('Negative residual radius')
    e=[radius*F(1+s,S) for s in range(S)]
    L=[[F(0)]*S for _ in range(T+1)];U=[[F(0)]*S for _ in range(T+1)]
    L[T]=[g[s]-f[T][s]-e[s] for s in range(S)]
    U[T]=[g[s]-f[T][s]+e[s] for s in range(S)]
    scalar_lo=min(L[T]);scalar_hi=max(U[T])
    for t in reversed(range(T)):
        for s in range(S):
            L[t][s]=min(r[t][s][a]-e[s]+beta[t]*evaluate(kernels[t][s][a],L[t+1]) for a in range(A))
            a=pi[t][s]
            U[t][s]=r[t][s][a]+e[s]+beta[t]*evaluate(kernels[t][s][a],U[t+1])
        scalar_lo=min(r[t][s][a]-e[s] for s in range(S) for a in range(A))+beta[t]*scalar_lo
        scalar_hi=max(r[t][s][pi[t][s]]+e[s] for s in range(S))+beta[t]*scalar_hi
    cuts=[];kept_count=0;total_count=0
    for t in range(T):
        for s in range(S):
            for a in range(A):
                k=kernels[t][s][a];kept,removed=safe_pieces(k,L[t+1],U[t+1])
                if evaluate(k,L[t+1],kept)!=evaluate(k,L[t+1]):raise AssertionError('Pruned lower changed')
                if evaluate(k,U[t+1],kept)!=evaluate(k,U[t+1]):raise AssertionError('Pruned upper changed')
                cuts.append({'t':t,'state':s,'action':a,'kept':kept,'removed':removed})
                kept_count+=len(kept);total_count+=len(k['q'])
    return {'radius':radius,'L':L,'U':U,'scalar_bound':scalar_hi-scalar_lo,
            'initial_loss_bounds':[u-l for l,u in zip(L[0],U[0])],
            'pieces_before':total_count,'pieces_after':kept_count,'cuts':cuts}


def flow(m,kernels,r,pi,exact):
    T,S,A,p,c,f,g,beta,alpha=decode_model(m);u=exact['U']
    masses=[[F(0)]*S for _ in range(T+1)];masses[0]=[F(1,S)]*S
    choices=[];B=F(1);objective=F(0);inequalities=0
    for t in range(T):
        js=[]
        for s in range(S):
            a=pi[t][s];k=kernels[t][s][a]
            j=max(range(len(k['q'])),key=lambda j:dot(k['q'][j],u[t+1])-k['k'][j]);js.append(j)
            for j2 in range(len(k['q'])):
                if u[t][s]<r[t][s][a]+beta[t]*(dot(k['q'][j2],u[t+1])-k['k'][j2]):raise AssertionError('Exact dual infeasible')
                inequalities+=1
            objective+=B*masses[t][s]*(r[t][s][a]-beta[t]*k['k'][j])
            for z in range(S):masses[t+1][z]+=masses[t][s]*k['q'][j][z]
        choices.append(js);B*=beta[t]
    objective+=B*dot(masses[T],[g[s]-f[T][s] for s in range(S)])
    dual=dot(masses[0],u[0])
    if objective!=dual:raise AssertionError('Risk-flow primal-dual disagreement')
    return {'masses':masses,'choices':choices,'objective':objective,'dual':dual,'inequalities':inequalities}


def fixture(T,alpha,theta):
    theta=rational(theta);S=3;A=2;p=[];c=[]
    for t in range(T):
        pp=[];cc=[]
        for s in range(S):
            ps=[];cs=[]
            for a in range(A):
                w=(1+(t+s+a)%3,1+(2*s+a)%4,1+(t+2*a)%3)
                ps.append(tuple(F(v,sum(w)) for v in w))
                cs.append(F((s+2*a+t)%5-2,7)+F(a,5))
            pp.append(ps);cc.append(cs)
        p.append(pp);c.append(cc)
    f=[[F(T-t,20)*theta+(theta+1)/7*max(F(0),F(s,2)-F(1,2))+F(t%3,11)*max(F(0),F(1,2)-F(s,2)) for s in range(S)] for t in range(T+1)]
    return {'T':T,'alpha':rational(alpha),'theta':theta,'p':p,'c':c,'f':f,'g':[F(0),F(1,3),F(-1,4)],'beta':[F(3,4)]*T}


def absorbing(T):
    return {'T':T,'alpha':F(1,2),'theta':'absorbing','p':[[[(F(1),F(0))]*2,[(F(0),F(1))]*2] for _ in range(T)],
            'c':[[[F(0),F(1)],[F(0),F(1)]] for _ in range(T)],'f':[[F(0),F(T-t)] for t in range(T+1)],
            'g':[F(0),F(0)],'beta':[F(1)]*T}


def strings(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):strings(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [strings(v) for v in x]
    return x
