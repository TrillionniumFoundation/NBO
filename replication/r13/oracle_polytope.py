"""Sharp finite-query response sets and rational weak-duality certificates.

HiGHS proposes multipliers. Fractions validate an upper bound for the ORIGINAL
rational inequalities, without requiring exact dual stationarity or trusting a
solver's success flag. See Theorems 1 and 2 and Supplement S.16.
"""
from __future__ import annotations
from fractions import Fraction as Q
from dataclasses import dataclass
from typing import Sequence
import numpy as np
from scipy.optimize import linprog

def fraction(x):
    if isinstance(x,Q):return x
    if isinstance(x,(int,np.integer)):return Q(int(x))
    return Q.from_float(float(x))

def encode(q):return str(q.numerator)+'/'+str(q.denominator)

def upper_float(q):
    x=float(q)
    return float(np.nextafter(x,np.inf)) if fraction(x)<q else x

@dataclass
class RationalLP:
    """Maximize c*x subject to A*x<=b and a finite, nonempty variable box."""
    A:list
    b:list
    box:list
    def __post_init__(self):
        self.A=[[fraction(a) for a in row] for row in self.A]
        self.b=list(map(fraction,self.b));self.box=[tuple(map(fraction,x)) for x in self.box]
        n=len(self.box)
        if len(self.A)!=len(self.b) or any(len(r)!=n for r in self.A):raise ValueError('LP dimensions')
        if any(l>u for l,u in self.box):raise ValueError('LP variable bounds')
    def dual_bound(self,c,multipliers):
        c=list(map(fraction,c));lam=list(map(fraction,multipliers))
        if len(lam)!=len(self.b) or len(c)!=len(self.box) or any(x<0 for x in lam):raise ValueError('invalid weak-duality multipliers')
        residual=[cc-sum(l*a[j] for l,a in zip(lam,self.A)) for j,cc in enumerate(c)]
        value=sum(l*b for l,b in zip(lam,self.b))+sum(max(r*lo,r*hi) for r,(lo,hi) in zip(residual,self.box))
        return value,residual
    def maximize(self,c):
        c=list(map(fraction,c))
        z=linprog(-np.array(c,float),A_ub=np.array(self.A,float),b_ub=np.array(self.b,float),bounds=np.array(self.box,float),method='highs')
        if not z.success:raise ValueError('LP proposal failed: '+z.message)
        # Box constraints are kept in the support function, not dualized.
        lam=np.maximum(0.,-z.ineqlin.marginals)
        bound,residual=self.dual_bound(c,lam)
        return dict(proposed_objective=float(-z.fun),certified_upper=upper_float(bound),exact_upper=encode(bound),multipliers=lam.tolist(),residual=[encode(r) for r in residual],proposed_point=z.x.tolist(),status=z.message)
    def validate(self,c,record):
        v,r=self.dual_bound(c,record['multipliers'])
        if encode(v)!=record['exact_upper'] or upper_float(v)!=record['certified_upper']:raise ValueError('incorrect rational LP bound')
        return v
    def json(self):
        return dict(A=[[encode(x) for x in row] for row in self.A],b=[encode(x) for x in self.b],box=[[encode(x) for x in row] for row in self.box])
    @classmethod
    def from_json(cls,z):return cls([[Q(x) for x in row] for row in z['A']],[Q(x) for x in z['b']],[[Q(x) for x in row] for row in z['box']])

def response_polytope(offsets,lower,upper,feature_box,eta=0):
    """Lifted sharp oracle set, with v=W(0), alpha=J(response;0).

    K is a box here; extra polytope restrictions can be appended for EACH feature
    block. Offsets[0]=0. The intercept bounds below follow from the lower queries,
    compact K, and beta_i<=v; they are not arbitrary truncations.
    """
    t=[[fraction(x) for x in row] for row in offsets]
    L=list(map(fraction,lower));U=list(map(fraction,upper));K=[tuple(map(fraction,x)) for x in feature_box];eta=fraction(eta)
    m=len(t);p=len(K)
    if not m or len(L)!=m or len(U)!=m or any(len(row)!=p for row in t) or any(t[0]) or any(l>u for l,u in zip(L,U)) or eta<0:raise ValueError('invalid oracle input')
    # v,alpha,z ; then beta_i,z_i for each query i.
    width=2+p+m*(1+p);A=[];b=[]
    def row(coeff,rhs):
        rr=[Q(0)]*width
        for j,val in coeff.items():rr[j]=fraction(val)
        A.append(rr);b.append(fraction(rhs))
    def wi(i):return 2+p+i*(1+p)
    box=[(L[0],U[0]),(L[0]-eta,U[0])]+K
    for i in range(m):
        max_feature=sum(max(ti*l,ti*u) for ti,(l,u) in zip(t[i],K))
        box += [(L[i]-max_feature,U[0])]+K
    row({1:1,0:-1},0);row({0:1,1:-1},eta)
    for j in range(m):row({1:1,**{2+k:t[j][k] for k in range(p)}},U[j])
    for i in range(m):
        ii=wi(i);row({ii:1,0:-1},0)
        for j in range(m):row({ii:1,**{ii+1+k:t[j][k] for k in range(p)}},U[j])
        row({ii:-1,**{ii+1+k:-t[i][k] for k in range(p)}},-L[i])
    row({wi(0):1,0:-1},0);row({wi(0):-1,0:1},0)
    return RationalLP(A,b,box),dict(value=0,intercept=1,features=list(range(2,2+p)),support_planes=[wi(i) for i in range(m)])

def reconstruct_menu(point,indices,p):
    out=[dict(intercept=point[1],features=point[2:2+p])]
    out += [dict(intercept=point[i],features=point[i+1:i+1+p]) for i in indices['support_planes']]
    return out

def exact_vertex(lp,point,tolerance=1e-7):
    """Recover an exact rational vertex from a proposed active set, then check it."""
    n=len(lp.box);rows=[]
    for a,b in zip(lp.A,lp.b):
        if abs(float(sum(aa*fraction(x) for aa,x in zip(a,point))-b))<tolerance:rows.append(a+[b])
    for i,(lo,hi) in enumerate(lp.box):
        for b in set((lo,hi)):
            if abs(float(fraction(point[i])-b))<tolerance:
                a=[Q(0)]*n;a[i]=Q(1);rows.append(a+[b])
    basis={}
    for rr in rows:
        rr=list(rr)
        for j,pivot in sorted(basis.items()):
            if rr[j]:
                z=rr[j];rr=[x-z*y for x,y in zip(rr,pivot)]
        nz=next((j for j in range(n) if rr[j]),None)
        if nz is not None:
            z=rr[nz];rr=[x/z for x in rr]
            for j,pivot in list(basis.items()):
                if pivot[nz]:
                    z=pivot[nz];basis[j]=[x-z*y for x,y in zip(pivot,rr)]
            basis[nz]=rr
        if len(basis)==n:break
    if len(basis)!=n:raise ValueError('proposed point has no recovered full-rank vertex')
    x=[basis[j][-1] for j in range(n)]
    if any(sum(a*v for a,v in zip(row,x))>b for row,b in zip(lp.A,lp.b)) or any(not lo<=v<=hi for v,(lo,hi) in zip(x,lp.box)):raise ValueError('recovered rational vertex is infeasible')
    return x
