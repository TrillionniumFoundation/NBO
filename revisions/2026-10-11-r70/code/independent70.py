"""Exact rational full-bin path replay; no NBO numerical module is imported.

Transition bounds use coordinate monotonicity on the unit cube. Cost terms
use rational interval extensions. This checks complete continuous bins with
unambiguous acquired actions, not an optimal Bellman descendant tree.
"""
from fractions import Fraction as F
from decimal import Decimal,localcontext
import numpy as np
B=F(15,16)
def iv(x):return (F(x),F(x))
def add(a,b):return (a[0]+b[0],a[1]+b[1])
def neg(a):return (-a[1],-a[0])
def sub(a,b):return add(a,neg(b))
def scale(a,b):
    b=F(b);return (a[0]*b,a[1]*b) if b>=0 else (a[1]*b,a[0]*b)
def square(a):return (F(0) if a[0]<=0<=a[1] else min(a[0]*a[0],a[1]*a[1]),max(a[0]*a[0],a[1]*a[1]))
def positive(a):return (max(F(0),a[0]),max(F(0),a[1]))
def total(items):
    out=iv(0)
    for a in items:out=add(out,a)
    return out

def cost(x,a=(),terminal=False):
    d=len(x);level=scale(total(square(sub(z,iv(F(5,8)))) for z in x),F(4 if terminal else 2,d))
    adjacent=scale(total(square(sub(x[j],x[(j+1)%d])) for j in range(d)),F(1,4*d))
    shortage=scale(square(positive(sub(iv(F(1,2)),scale(total(x),F(2,d))))),2)
    value=add(add(level,adjacent),shortage)
    if not terminal:
        action=sum((z*z+4*z**4 for z in a),F(0))
        if len(a)==2:action+=a[0]*a[1]/4
        value=add(value,iv(action))
    return value

def transition(x,a,z,w=(F(0),F(0))):
    d=len(x);out=[]
    for j in range(d):
        f=lambda u,v:F(1,16)+u/2+v/8+u*(1-v)/16
        y=(f(x[j][0],x[(j+1)%d][0]),f(x[j][1],x[(j+1)%d][1]))
        expose=(F(1,2) if j%2==0 else F(1,4))*a[0]
        if len(a)==2:expose+=(F(1,4) if j%2==0 else F(1,2))*a[1]
        out.append(add(add(add(y,iv(expose)),z if j%2==0 else neg(z)),w))
    return out

def contained(a,lo,hi,label):
    if not F(float(lo))<=a[0]<=a[1]<=F(float(hi)):
        raise AssertionError((label,tuple(map(str,a)),str(lo),str(hi)))

def path_bins(randoms,trace,T,vector=False):
    den=2**48;N=len(randoms['initial_index']);complete=ambiguous=states=0
    for i in range(N):
        x=[(F(int(v),den),F(int(v)+1,den)) for v in randoms['initial_index'][i]];acc=iv(0);done=True
        for t in range(T):
            vals=np.atleast_1d(trace[f't{t}_action'][i])
            if not np.isfinite(vals).all():ambiguous+=1;done=False;break
            a=tuple(F(float(z)) for z in vals);obs=tuple(F(float(z)) for z in trace[f't{t}_observed'][i])
            for j,interval in enumerate(x):
                low=F((interval[0]*2**24).__floor__(),2**24);high=F((interval[1]*2**24).__floor__(),2**24)
                if low!=high or low!=obs[j]:raise AssertionError(('Full-bin acquisition',i,t,j))
                if f't{t}_state_lo' in trace:contained(interval,trace[f't{t}_state_lo'][i,j],trace[f't{t}_state_hi'][i,j],('state',i,t,j))
            cap=F(1,8)+sum((z[0] for z in x),F(0))/(8*len(x))
            if min(a)<0 or sum(a)>cap or any((z*2**32).denominator!=1 for z in a):raise AssertionError(('Action contract',i,t))
            acc=add(acc,scale(cost(x,a),B**t));states+=1
            k=int(randoms['shock_index'][t,i]);z=(F(k,16*den)-F(1,32),F(k+1,16*den)-F(1,32));w=iv(0)
            if vector:
                k=int(randoms['second_shock_index'][t,i]);w=(F(k,32*den)-F(1,64),F(k+1,32*den)-F(1,64))
            x=transition(x,a,z,w)
        if done:
            acc=add(acc,scale(cost(x,terminal=True),B**T));contained(acc,trace['cost_lo'][i],trace['cost_hi'][i],('cumulative full-bin cost',i));complete+=1
    return dict(rows=N,full_bin_rows=complete,ambiguous_rows=ambiguous,state_action_steps=states)

def centered_interval(first,second,reported,Gfirst,Gsecond):
    a,b=first;c,d=second;n=len(a)
    for lo,hi,G in ((a,b,Gfirst),(c,d,Gsecond)):
        if any(not 0<=F(float(x))<=F(float(y))<=F(G)+F(1,2**48) for x,y in zip(lo,hi)):raise AssertionError('Centered support violation')
    lower=sum((F(float(x))-F(float(y)) for x,y in zip(a,d)),F(0))/n
    upper=sum((F(float(x))-F(float(y)) for x,y in zip(b,c)),F(0))/n
    with localcontext() as ctx:
        ctx.prec=80;dec=lambda x:Decimal(x.numerator)/Decimal(x.denominator)
        width=F(reported['support_width_exact']);radius=dec(width)*(Decimal(str(reported['log_upper']))/Decimal(2*n)).sqrt()
        lo=dec(lower)-radius-Decimal('1e-70');hi=dec(upper)+radius+Decimal('1e-70')
        if Decimal.from_float(reported['interval'][0])>lo or Decimal.from_float(reported['interval'][1])<hi:raise AssertionError('Independent interval containment')
    return dict(rows=n,lower_mean_exact=str(lower),upper_mean_exact=str(upper),status='passed')
