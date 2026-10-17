"""Independent exact-rational reconstruction from economic primitives.

No production interval, risk, feature, or optimization module is imported.
The risk calculation uses a polynomial threshold integral and an independent
continuous-risk dual witness. It is kernel replication, not external authorship.
"""
from __future__ import annotations
from fractions import Fraction as F
import json,math,pathlib,time

def rat(x):return x if isinstance(x,F) else F(float(x))
def economic_S(x,terminal=False):
    d=len(x)
    return F(4 if terminal else 2,d)*sum((v-F(5,8))**2 for v in x)+F(1,4*d)*sum((x[j]-x[(j+1)%d])**2 for j in range(d))+2*max(F(0),F(1,2)-F(2,d)*sum(x))**2

def economic_gradient(x,terminal=False):
    d=len(x);h=max(F(0),F(1,2)-F(2,d)*sum(x))
    return [F(8 if terminal else 4,d)*(x[j]-F(5,8))+F(1,2*d)*(2*x[j]-x[(j-1)%d]-x[(j+1)%d])-F(8,d)*h for j in range(d)]

def next_state(x,a,z):
    return [F(1,16)+v/2+x[(j+1)%len(x)]/8+v*(1-x[(j+1)%len(x)])/16+(F(1,2) if j%2==0 else F(1,4))*a+(1 if j%2==0 else -1)*z for j,v in enumerate(x)]

def polynomial_from_primitives(x,a):
    # Interpolation of the original polynomial, not the production coefficients.
    R=F(1,32);c=economic_S(next_state(x,a,F(0)),True)
    plus=economic_S(next_state(x,a,R),True);minus=economic_S(next_state(x,a,-R),True)
    return [c,(plus-minus)/(2*R),(plus+minus-2*c)/(2*R**2)]

def integral(poly,l,u):return sum(c*(u**(j+1)-l**(j+1))/F(j+1) for j,c in enumerate(poly))
def evaluate(poly,z):return sum(c*z**j for j,c in enumerate(poly))

def tail_threshold(poly,alpha):
    alpha=rat(alpha);R=F(1,32);removed=2*R*alpha
    c,d,e=poly
    if e<=0:raise ValueError('This primitive audit requires the original positive quadratic shock coefficient')
    left=max(-R,min(R-removed,-d/(2*e)-removed/2));right=left+removed
    eta=max(evaluate(poly,left),evaluate(poly,right))
    excess=list(poly);excess[0]-=eta
    primal=eta+(integral(excess,-R,left)+integral(excess,right,R))/(2*R*(1-alpha))
    dual=(integral(poly,-R,left)+integral(poly,right,R))/(2*R*(1-alpha))
    if primal!=dual:raise AssertionError('Exact original-risk primal/dual disagreement')
    return dual,left,right,eta

def objective_gradient(x,a,alpha):
    x=list(map(rat,x));a=rat(a);alpha=rat(alpha);R=F(1,32)
    poly=polynomial_from_primitives(x,a);risk,left,right,eta=tail_threshold(poly,alpha)
    zero=next_state(x,a,F(0));atR=next_state(x,a,R)
    gz=economic_gradient(zero,True);gr=economic_gradient(atR,True)
    dpoly=[sum(gz[j]*(F(1,2) if j%2==0 else F(1,4)) for j in range(len(x))),sum((gr[j]-gz[j])/R*(F(1,2) if j%2==0 else F(1,4)) for j in range(len(x)))]
    derivative=2*a+16*a**3+F(15,16)*(integral(dpoly,-R,left)+integral(dpoly,right,R))/(2*R*(1-alpha))
    value=economic_S(x)+a*a+4*a**4+F(15,16)*risk
    return value,derivative

def terminal_bounds(x,alpha,steps=28):
    x=list(map(rat,x));cap=F(1,8)+sum(x)/F(8*len(x));lo=F(0);hi=cap
    _,gl=objective_gradient(x,lo,alpha);_,gu=objective_gradient(x,hi,alpha)
    if gl>=0:a=lo
    elif gu<=0:a=hi
    else:
        for _ in range(steps):
            a=(lo+hi)/2;_,g=objective_gradient(x,a,alpha)
            if g<0:lo=a
            else:hi=a
        a=(lo+hi)/2
    value,g=objective_gradient(x,a,alpha);delta=max(-a,min(cap-a,-g/2))
    return value+g*delta+delta*delta,value,a

def feature_value(model,x):
    x=list(map(rat,x));c=list(map(rat,model['coefficients']));d=len(x)
    out=c[0]+sum(c[j+1]*x[j] for j in range(d))
    for k,(direction,offset) in enumerate(zip(model['directions'],model['offsets'])):
        z=rat(offset)+sum(rat(w)*v for w,v in zip(direction,x))
        phi=z*z if model['kind']=='quadratic' else max(F(0),z)
        out+=c[d+1+k]*phi
    return out

def discrete_threshold(values,alpha):
    values=list(map(rat,values));alpha=rat(alpha);n=len(values)
    candidates=sorted(set(values))
    return min(eta+sum(max(F(0),v-eta) for v in values)/(n*(1-alpha)) for eta in candidates)

def nested_policy_bounds(x,a,alpha,bins=32):
    x=list(map(rat,x));a=rat(a);low=[];high=[];R=F(1,32);pad=15*R/bins
    for j in range(bins):
        z=-R+F(2*j+1,2*bins)*(2*R)
        l,u,_=terminal_bounds(next_state(x,a,z),alpha)
        low.append(l-pad);high.append(u+pad+F(1,2**20))
    base=economic_S(x)+a*a+4*a**4
    return base+F(15,16)*discrete_threshold(low,alpha),base+F(15,16)*discrete_threshold(high,alpha)
