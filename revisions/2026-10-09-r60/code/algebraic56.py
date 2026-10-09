"""Certified scalar-action search for a saved single-layer neural critic.

All coefficients and evaluations are exact rationals. Cubic stationary roots
are isolated rationally; no floating root or optimizer-success assumption is
used. This is a new solver/regression, not a rerun of R55 economic observations.
"""
from fractions import Fraction as F
from math import floor,ceil
import sympy as sp

def rational(x):return x if isinstance(x,F) else F(float(x))
def hinge(z,r):
    if r==0:return max(F(0),z)
    if z<=-r:return F(0)
    if z>=r:return z
    return (z+r)**2/(4*r)

def reduce_critic(state,params,beta=F(15,16),price=F(1)):
    x=list(map(rational,state));d=len(x);gamma=[F(1,2) if j%2==0 else F(1,4) for j in range(d)]
    drift=[F(1,16)+x[j]/2+x[(j+1)%d]/8+x[j]*(1-x[(j+1)%d])/16 for j in range(d)]
    v=list(map(rational,params['v']));W=params['W'];u=list(map(rational,params['u']));b=list(map(rational,params['b']))
    q0=beta*(rational(params['c'])+sum(vj*y for vj,y in zip(v,drift)));q1=beta*sum(vj*g for vj,g in zip(v,gamma));features=[]
    for j,uj in enumerate(u):
        w=[rational(W[i][j]) for i in range(d)]
        z=b[j]+sum(wi*y for wi,y in zip(w,drift));a=sum(wi*g for wi,g in zip(w,gamma));r=abs(sum(w[i]*(1 if i%2==0 else -1) for i in range(d)))/32
        features.append((beta*uj,z,a,r))
    def value(a):return q0+q1*a+price*a*a+4*a**4+sum(u*hinge(z+s*a,r) for u,z,s,r in features)
    return q0,q1,price,features,value

def minimize_lattice(state,params,capindex,quantum=4096):
    if not isinstance(capindex,int) or not isinstance(quantum,int) or quantum<=0 or not 0<=capindex<=quantum//4:raise ValueError('Expected integer cap in the global nonnegative action range')
    q0,q1,q2,features,value=reduce_critic(state,params);cap=F(capindex,quantum);knots={F(0),cap};a=sp.Symbol('a')
    for u,z,s,r in features:
        if s:
            for endpoint in (-r,r):
                point=(endpoint-z)/s
                if 0<point<cap:knots.add(point)
    knots=sorted(knots);indices={0,capindex};root_count=0;pieces=0
    def add_near(left,right):
        for k in range(max(0,floor(left*quantum)),min(capindex,ceil(right*quantum))+1):indices.add(k)
    for knot in knots:add_near(knot,knot)
    for left,right in zip(knots,knots[1:]):
        if left==right:continue
        middle=(left+right)/2;c1=q1;c2=q2;pieces+=1
        for weight,z,s,r in features:
            mid=z+s*middle
            if mid>=r:c1+=weight*s
            elif r>0 and mid>-r:
                c1+=weight*s*(z+r)/(2*r);c2+=weight*s*s/(4*r)
        poly=sp.Poly(16*a**3+sp.Rational(2*c2.numerator,c2.denominator)*a+sp.Rational(c1.numerator,c1.denominator),a)
        intervals=poly.intervals(eps=sp.Rational(1,4*quantum),inf=sp.Rational(left.numerator,left.denominator),sup=sp.Rational(right.numerator,right.denominator))
        for (lo,hi),multiplicity in intervals:
            root_count+=1;add_near(F(int(lo.p),int(lo.q)),F(int(hi.p),int(hi.q)))
    candidates=sorted(indices);scores={k:value(F(k,quantum)) for k in candidates};best=min(candidates,key=lambda k:(scores[k],k))
    return dict(index=best,value_exact=str(scores[best]),candidate_indices=candidates,pieces=pieces,isolated_roots=root_count,feature_count=len(features),lattice_size=capindex+1,arithmetic='exact dyadic inputs, rational cubic isolation and exact rational comparison')
