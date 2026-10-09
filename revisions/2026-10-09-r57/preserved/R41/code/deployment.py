"""All-domain binary32 execution bounds and an explicit deployed interpreter.

Range/error arithmetic below uses exact rationals. Random fixtures are tests,
not the source of the uniform guarantee. The objective is the finite-horizon
recursive cost of the specified rounded numerical transition/cost program;
no physical actuator or unbounded Gaussian-state validation is asserted.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
import sys,json,math
import numpy as np
R=Path(__file__).resolve().parents[1]
OLD=(R/'vendor/r38/code') if (R/'vendor/r38/code').exists() else R.parent/'2026-10-07-r38/code'
sys.path.insert(0,str(OLD))
from nonlinear import I,risk,encode
U=F(1,2**24);TINY=F(1,2**150)
@dataclass(frozen=True)
class B:
    lo:F;hi:F;e:F=F(0)
    def __post_init__(self):
        if self.lo>self.hi or self.e<0:raise ValueError('Invalid range/error')
    @property
    def mag(self):return max(abs(self.lo),abs(self.hi))
    @staticmethod
    def exact(x):return B(F(x),F(x))
    @staticmethod
    def rnd(lo,hi,prop):return B(lo,hi,prop+U*(max(abs(lo),abs(hi))+prop)+TINY)
    def __add__(self,o):
        o=o if isinstance(o,B) else B.exact(o)
        return B.rnd(self.lo+o.lo,self.hi+o.hi,self.e+o.e)
    __radd__=__add__
    def __neg__(self):return B(-self.hi,-self.lo,self.e)
    def __sub__(self,o):return self+(-(o if isinstance(o,B) else B.exact(o)))
    def __rsub__(self,o):return B.exact(o)+(-self)
    def __mul__(self,o):
        o=o if isinstance(o,B) else B.exact(o)
        p=[self.lo*o.lo,self.lo*o.hi,self.hi*o.lo,self.hi*o.hi]
        return B.rnd(min(p),max(p),self.mag*o.e+o.mag*self.e+self.e*o.e)
    __rmul__=__mul__
    def clip(self,a,b):
        a,b=F(a),F(b)
        return B(min(b,max(a,self.lo)),min(b,max(a,self.hi)),self.e)

def graph_bounds(price):
    x=B(F(0),F(1),U+TINY);a=B(F(0),F(1,4));z=B(F(-1,16),F(1,16))
    transition=(F(13,16)*x+a+F(1,16)*(x*(1-x))+z).clip(0,1)
    aa=a*a;d=x-F(11,16);p=(F(3,8)-x).clip(0,1)
    cost=(d*d+F(price)*aa)+4*(aa*aa)+2*(p*p)
    terminal=2*(d*d)+2*(p*p)
    return dict(sensor=U+TINY,transition=transition.e,cost=cost.e,terminal=terminal.e)

def f32(x):return np.asarray(x,dtype=np.float32)

def native_transition(x,a,z):
    x,a,z=f32(x),f32(a),f32(z)
    return np.clip(f32(f32(f32(f32(13/16)*x)+a)+f32(f32(1/16)*f32(x*f32(f32(1)-x))))+z, f32(0),f32(1)).astype(np.float32)

def native_cost(x,a,price):
    x,a=f32(x),f32(a);aa=f32(a*a);d=f32(x-f32(11/16));p=np.clip(f32(f32(3/8)-x),f32(0),f32(1))
    return f32(f32(f32(f32(d*d)+f32(f32(price)*aa))+f32(f32(4)*f32(aa*aa)))+f32(f32(2)*f32(p*p)))

def native_terminal(x):
    x=f32(x);d=f32(x-f32(11/16));p=np.clip(f32(f32(3/8)-x),f32(0),f32(1))
    return f32(f32(f32(2)*f32(d*d))+f32(f32(2)*f32(p*p)))

def deployed_values(policy,states):
    knots=np.asarray(policy['knots'],dtype=float);cuts=(knots[:-1]+knots[1:])/2
    acts=[np.asarray(a,dtype=np.float32) for a in policy['actors']]
    if not all(np.array_equal(np.asarray(a,dtype=float),b.astype(float)) for a,b in zip(policy['actors'],acts)):raise ValueError('Nonexact action conversion')
    def rec(t,x):
        if t==policy['T']:return I.point(native_terminal(x).astype(float))
        idx=np.searchsorted(cuts,x.astype(float),side='left');a=acts[t][idx]
        xp=native_transition(x[...,None],a[...,None],np.array([-1/16,0,1/16],dtype=np.float32))
        return I.point(native_cost(x,a,policy['price']).astype(float))+.9375*risk(rec(t+1,xp),policy['theta'])
    return rec(0,f32(states))

def apply(result):
    b=graph_bounds(result['price']);ex=I.point(0.);disc=I.point(1.)
    uf=lambda x:math.nextafter(float(x),math.inf)
    for rec in result['records']:
        term=2*I.point(rec['bellman_state_lipschitz'])*uf(b['sensor'])+uf(b['cost'])+.9375*rec['future_neural_lipschitz']*I.point(uf(b['transition']))
        ex=ex+disc*term;disc=disc*.9375
    ex=ex+disc*uf(b['terminal'])
    vals=deployed_values(result['policy'],result['own_policy_values']['states'])
    return dict(unit_roundoff=float(U),underflow_absolute_allowance=str(TINY),
        primitive_upper={k:uf(v) for k,v in b.items()},
        primitive_exact={k:[str(v.numerator),str(v.denominator)] for k,v in b.items()},
        extra_global_loss_upper=ex.hi.item(),deployed_global_excess_cost_upper=(I.point(result['policy_gap_upper'])+ex).hi.item(),
        deployed_values=dict(lower=vals.lo,upper=vals.hi),
        statewise_deployed_excess_cost_upper=(vals-I.point(result['optimal_value_lower'])).hi,
        scope='Rounded binary32 transition and stage/terminal cost; exact recursive risk evaluated by intervals. Comparison lower value belongs to the exact stored economic model. No nonnegative gap is asserted for the perturbed transition model.')

def test():
    rng=np.random.default_rng(4107);count=0;worst=0.
    for price in [1,4]:
        b=graph_bounds(price)
        cases=[(0.,0.,-1/16),(1.,.25,1/16),(.375,.125,0.),(.6875,0.,0.)]
        cases += [(float(x),float(k)/4096,float(z)) for x,k,z in zip(rng.random(512),rng.integers(0,1025,512),rng.choice([-1/16,0,1/16],512))]
        for xf,af,zf in cases:
            x,a,z=F(xf),F(af),F(zf)
            ideal_t=min(F(1),max(F(0),F(13,16)*x+a+F(1,16)*x*(1-x)+z))
            ideal_c=(x-F(11,16))**2+price*a*a+4*a**4+2*max(F(0),F(3,8)-x)**2
            ideal_g=2*(x-F(11,16))**2+2*max(F(0),F(3,8)-x)**2
            errors=[abs(F(float(native_transition(xf,af,zf)))-ideal_t),abs(F(float(native_cost(xf,af,price)))-ideal_c),abs(F(float(native_terminal(xf)))-ideal_g)]
            for err,key in zip(errors,['transition','cost','terminal']):
                assert err<=b[key],(price,xf,af,key,float(err),float(b[key]))
                worst=max(worst,float(err/b[key]))
            count+=1
    return dict(exact_rational_native_fixtures=count,maximum_observed_fraction_of_uniform_bound=worst,
        all_state_proof='Rational range/error induction with |round(y)-y| <= u|y| + 2^-150; clipping nonexpansive')
if __name__=='__main__':
    out={'tests':test(),'primitive_bounds':{str(p):{k:math.nextafter(float(v),math.inf) for k,v in graph_bounds(p).items()} for p in [1,4]}}
    (R/'audit/DEPLOYMENT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2))
