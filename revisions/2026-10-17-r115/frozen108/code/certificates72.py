"""Exact contracts for frozen NBO continuations and purchased witnesses.

This module imports no production numerical kernel. Fractions represent
binary floating inputs exactly; callers must never replace a bound with a
rounded-to-nearest decimal before certification.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from typing import Sequence

BETA=F(15,16)


def rational(x):
    if isinstance(x,F):return x
    return F(float(x)) if isinstance(x,float) else F(x)


def regularity(remaining:int,dimension:int):
    if remaining<0 or dimension<2 or dimension%2:raise ValueError('model dimensions')
    G=F(10,dimension)
    for _ in range(remaining):G=F(1037,128*dimension)+BETA*F(47,64)*G
    return G


def moduli(remaining:int,dimension:int):
    if remaining<1:raise ValueError('decision date')
    Gn=regularity(remaining-1,dimension)
    return regularity(remaining,dimension),F(8,dimension)+BETA*F(11,16)*Gn,F(13,16)+BETA*F(3*dimension,8)*Gn


def capacity(state:Sequence[F]):
    if len(state)<2 or len(state)%2 or any(x<0 or x>1 for x in state):raise ValueError('state')
    return F(1,8)+sum(state,F(0))/(8*len(state))


def repair(action:Sequence[F],cap:F,bits:int=32):
    if bits<1 or len(action) not in (1,2) or min(action)<0 or cap<0:raise ValueError('repair')
    den=2**bits;c=F((cap*den).__floor__(),den);total=sum(action,F(0))
    scale=min(F(1),c/total) if total else F(1)
    result=tuple(F((a*scale*den).__floor__(),den) for a in action)
    if min(result)<0 or sum(result)>cap:raise ArithmeticError('feasibility')
    return result


@dataclass(frozen=True)
class Witness:
    state:tuple[F,...]
    action:tuple[F,...]
    lower:F
    upper:F
    remaining:int
    context:str

    def validate(self):
        if self.remaining<1 or self.lower>self.upper or not self.context:raise ValueError('certificate')
        if len(self.action) not in (1,2) or min(self.action)<0 or sum(self.action)>capacity(self.state):raise ValueError('witness feasibility')


def transport(record:Witness,state:Sequence[F],tolerance:F,context:str):
    record.validate();x=tuple(map(rational,state));tol=rational(tolerance)
    if len(x)!=len(record.state) or tol<=0:raise ValueError('query')
    capacity(x)
    if record.context!=context:return None
    action=repair(record.action,capacity(x));dist=sum((abs(a-b) for a,b in zip(x,record.state)),F(0))
    displacement=sum((abs(a-b) for a,b in zip(action,record.action)),F(0))
    LV,LQ,LA=moduli(record.remaining,len(x))
    lower=max(F(0),record.lower-LV*dist)
    upper=record.upper+LQ*dist+LA*displacement
    if upper-lower>tol:return None
    return dict(lower=lower,upper=upper,action=action,gap=upper-lower,
                state_distance=dist,action_displacement=displacement,
                value_modulus=LV,state_modulus=LQ,action_modulus=LA)


def relu_uniform_mean(center:F,radii:Sequence[F]):
    """E[(center+sum U_j)_+] for one/two centered uniform projections."""
    c=rational(center);r=tuple(abs(rational(a)) for a in radii if a)
    positive=lambda x:max(F(0),x)
    if not r:return positive(c)
    if len(r)==1:
        a=r[0];return (positive(c+a)**2-positive(c-a)**2)/(4*a)
    if len(r)==2:
        a,b=r
        return (positive(c+a+b)**3-positive(c+a-b)**3-positive(c-a+b)**3+positive(c-a-b)**3)/(24*a*b)
    raise ValueError('at most two independent innovations')


def relu_box_mean_independent(center:F,radii:Sequence[F]):
    """Independent exact clipping/integration, not positive-part powers.

Clip a square by one half-plane and integrate the affine function on the
resulting polygon by a fan triangulation. Degenerate 1D laws are integrated
as intervals. This implementation shares only Fraction arithmetic.
"""
    c=rational(center);r=[abs(rational(x)) for x in radii if x]
    if not r:return max(F(0),c)
    if len(r)==1:
        a=r[0];left=max(-F(1),-c/a);right=F(1)
        if left>=right:return F(0)
        return (c*(right-left)+a*(right*right-left*left)/2)/2
    if len(r)!=2:raise ValueError('dimension')
    a,b=r;poly=[(-F(1),-F(1)),(F(1),-F(1)),(F(1),F(1)),(-F(1),F(1))]
    val=lambda z:c+a*z[0]+b*z[1]
    clipped=[]
    for p,q in zip(poly,poly[1:]+poly[:1]):
        f,g=val(p),val(q)
        if f>=0:clipped.append(p)
        if (f<0 and g>0) or (f>0 and g<0):
            s=f/(f-g);clipped.append((p[0]+s*(q[0]-p[0]),p[1]+s*(q[1]-p[1])))
    if len(clipped)<3:return F(0)
    p=clipped[0];answer=F(0)
    for q,s in zip(clipped[1:-1],clipped[2:]):
        area=abs((q[0]-p[0])*(s[1]-p[1])-(q[1]-p[1])*(s[0]-p[0]))/2
        answer+=area*(val(p)+val(q)+val(s))/3
    return answer/4


def centered_support(residual_oscillation,greedy_pi,greedy_nu,terminal_oscillation=F(0),beta=BETA):
    if len(residual_oscillation)!=len(greedy_pi) or len(greedy_pi)!=len(greedy_nu):raise ValueError('horizons')
    if min([rational(terminal_oscillation)]+list(residual_oscillation)+list(greedy_pi)+list(greedy_nu))<0:raise ValueError('negative allowance')
    common=sum((beta**t*rational(w) for t,w in enumerate(residual_oscillation)),F(0))+beta**len(greedy_pi)*rational(terminal_oscillation)
    upper=common+sum((beta**t*rational(e) for t,e in enumerate(greedy_pi)),F(0))
    lower=-common-sum((beta**t*rational(e) for t,e in enumerate(greedy_nu)),F(0))
    return lower,upper
