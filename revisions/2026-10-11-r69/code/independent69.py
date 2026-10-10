"""Independent rational primitives, with no imports from NBO numerical kernels.

The mathematical economic formulas are shared; implementation and arithmetic
are independent. Mid-bin trajectory checks audit every new stored path, not
the enormous inherited vector Bellman descendant trees.
"""
from fractions import Fraction as F
import math
B=F(15,16)

def stage(x,a,terminal=False):
    d=len(x);s=max(F(0),F(1,2)-2*sum(x)/d)
    value=(4 if terminal else 2)*sum((v-F(5,8))**2 for v in x)/d
    value+=sum((x[j]-x[(j+1)%d])**2 for j in range(d))/(4*d)+2*s*s
    if not terminal:
        value+=sum(v*v+4*v**4 for v in a)
        if len(a)==2:value+=a[0]*a[1]/4
    return value

def transition(x,a,z,w=F(0)):
    d=len(x)
    return [F(1,16)+x[j]/2+x[(j+1)%d]/8+x[j]*(1-x[(j+1)%d])/16
        +(F(1,2) if j%2==0 else F(1,4))*a[0]
        +((F(1,4) if j%2==0 else F(1,2))*a[1] if len(a)==2 else 0)
        +(1 if j%2==0 else -1)*z+w for j in range(d)]

def terminal_q(x,a):
    d=len(x);y=transition(x,a,F(0));s=F(1,2)-2*sum(y)/d
    value=4*sum((v-F(5,8))**2 for v in y)/d
    value+=sum((y[j]-y[(j+1)%d])**2 for j in range(d))/(4*d)
    if len(a)==1:value+=2*max(F(0),s)**2+F(5,3072)
    else:
        rad=F(1,32);moment=(max(F(0),s+rad)**3-max(F(0),s-rad)**3)/(6*rad)
        value+=2*moment+F(1,512)
    return stage(x,a)+B*value

def regularity(r,d):
    G,M=F(10,d),F(26,d)
    for _ in range(r):G,M=F(1037,128*d)+B*F(47,64)*G,F(22,d)+F(21,256*d)+B*(F(9,16)*M+G/8)
    return G,M

def uniform_value(x,r,tolerance,counts=None):
    if counts is None:counts={'q_queries':0,'terminal_queries':0}
    d=len(x);G,M=regularity(r-1,d);H=F(21,4)+B*M*F(5*d,32);cap=F(1,8)+sum(x)/(8*d)
    A=1
    while H*(cap/A)**2/8>tolerance/4:A*=2
    bins=1;zeta=B*M*d/6144
    while r>1 and zeta/(bins*bins)>tolerance/4:bins*=2
    low=None;high=None
    for j in range(A+1):
        a=[cap*j/A];counts['q_queries']+=1
        if r==1:
            lo=hi=terminal_q(x,a);counts['terminal_queries']+=1
        else:
            ls=us=F(0)
            for z in range(bins):
                child=transition(x,a,F(2*z+1-bins,32*bins))
                l,u=uniform_value(child,r-1,tolerance/(4*B),counts);ls+=l;us+=u
            lo=stage(x,a)+B*ls/bins;hi=stage(x,a)+B*us/bins+zeta/(bins*bins)
        low=lo if low is None else min(low,lo);high=hi if high is None else min(high,hi)
    return max(F(0),low-H*(cap/A)**2/8),high

def audit_paths(randoms,trace,T,vector=False):
    den=2**48;N=len(randoms['initial_index']);checked=0;ambiguous=0
    for i in range(N):
        state=[F(2*int(v)+1,2*den) for v in randoms['initial_index'][i]];total=F(0);complete=True
        for t in range(T):
            recorded=trace[f't{t}_action'][i]
            if not math.isfinite(float(recorded[0] if vector else recorded)):
                ambiguous+=1;complete=False;break
            action=list(map(lambda z:F(float(z)),recorded)) if vector else [F(float(recorded))]
            obs=[F((x*2**24).__floor__(),2**24) for x in state]
            observed=trace[f't{t}_observed'][i]
            if any(x!=F(float(y)) for x,y in zip(obs,observed)):raise AssertionError(('Independent acquisition disagreement',i,t))
            cap=F(1,8)+sum(state)/(8*len(state))
            if min(action)<0 or sum(action)>cap:raise AssertionError(('Independent feasibility disagreement',i,t))
            if f't{t}_state_lo' in trace:
                if any(not F(float(l))<=x<=F(float(u)) for x,l,u in zip(state,trace[f't{t}_state_lo'][i],trace[f't{t}_state_hi'][i])):
                    raise AssertionError(('Independent state enclosure disagreement',i,t))
            total+=B**t*stage(state,action)
            z=F(2*int(randoms['shock_index'][t,i])+1,32*den)-F(1,32)
            w=F(2*int(randoms['second_shock_index'][t,i])+1,64*den)-F(1,64) if vector else F(0)
            state=transition(state,action,z,w)
        if complete:
            total+=B**T*stage(state,[],True)
            if not F(float(trace['cost_lo'][i]))<=total<=F(float(trace['cost_hi'][i])):
                raise AssertionError(('Independent cumulative cost disagreement',i,str(total)))
            checked+=1
    return dict(complete_midbin_paths_checked=checked,conservatively_ambiguous_paths=ambiguous,
                scope='Exact independent acquisition, feasibility, transition and cumulative cash-cost check on every represented mid-bin trajectory; not full-bin reintegration of the optimal-value descendant tree')
