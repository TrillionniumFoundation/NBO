"""Exact checks for the new resource model and finite-policy fixtures."""
from fractions import Fraction as Q
from itertools import product
import json, math
from pathlib import Path
R=Path(__file__).resolve().parents[1]

def validate(eta, terms):
    if not eta or any(Q(x)<=0 for x in eta): raise ValueError('Positive allowances')
    for c,a in terms:
        if Q(c)<=0 or len(a)!=len(eta) or any(type(p)!=int or p<0 for p in a):
            raise ValueError('Positive coefficients and nonnegative integer exponents')

def objective(eta, terms, setup=0):
    validate(eta,terms)
    return Q(setup)+sum((Q(c)*math.prod(Q(x)**(-p) for x,p in zip(eta,a)) for c,a in terms),Q(0))

def gradient(eta, terms):
    validate(eta,terms)
    return tuple(sum((-Q(c)*a[i]*math.prod(Q(x)**(-p) for x,p in zip(eta,a))/Q(eta[i]) for c,a in terms),Q(0)) for i in range(len(eta)))

def certificate(eta,terms,w,epsilon,caps,lam=None,nu=None,setup=0):
    eta,w,caps=tuple(map(Q,eta)),tuple(map(Q,w)),tuple(map(Q,caps));epsilon=Q(epsilon)
    if len(w)!=len(eta) or len(caps)!=len(eta) or any(x<=0 for x in w+caps) or epsilon<=0:
        raise ValueError('Dimensions and positive budget inputs')
    if sum(x*y for x,y in zip(eta,w))>epsilon or any(x>y for x,y in zip(eta,caps)):
        raise ValueError('Feasible candidate required')
    upper=objective(eta,terms,setup);g=gradient(eta,terms)
    lam=max(-x/y for x,y in zip(g,w)) if lam is None else Q(lam)
    nu=(Q(0),)*len(eta) if nu is None else tuple(map(Q,nu))
    if len(nu)!=len(eta) or lam<0 or any(v<0 for v in nu) or any(x+lam*y+v<0 for x,y,v in zip(g,w,nu)):
        raise ValueError('Dual feasibility')
    lower=upper-sum(x*y for x,y in zip(g,eta))-lam*epsilon-sum(x*y for x,y in zip(nu,caps))
    if lower>upper:raise AssertionError('Invalid certificate ordering')
    return dict(eta=eta,gradient=g,lambda_=lam,nu=nu,lower=lower,upper=upper,gap=upper-lower)

def dyadic(x):
    x=Q(x);v=Q(1)
    if x<=0:raise ValueError('Positive value')
    while v>x:v/=2
    while 2*v<=x:v*=2
    return v

def transition(t,x,a):
    p=Q(1+(t+2*x+a)%3,5)
    return (p,1-p)

def cost(t,x,a):return Q(t+x+2*a,7)
def terminal(x):return Q(3+6*x,10)
def policy(theta,T=3):
    return tuple(tuple(min((0,1),key=lambda a:(a*(Q(theta)*(-1 if (t+x)%2 else 1)+Q(t-x,3)),a)) for x in (0,1)) for t in range(T))

def path_cost(pol):
    T=len(pol);total=Q(0);beta=Q(15,16)
    for path in product((0,1),repeat=T+1):
        mass=Q(1,2);value=Q(0)
        for t in range(T):
            a=pol[t][path[t]];value+=beta**t*cost(t,path[t],a)
            mass*=transition(t,path[t],a)[path[t+1]]
        total+=mass*(value+beta**T*terminal(path[-1]))
    return total

def reference_values(T):
    values=[None]*T+[(terminal(0),terminal(1))];beta=Q(15,16)
    for t in reversed(range(T)):
        values[t]=tuple(cost(t,x,0)+beta*sum(p*v for p,v in zip(transition(t,x,0),values[t+1])) for x in (0,1))
    return values

def occupation_difference(pol):
    values=reference_values(len(pol));mass=(Q(1,2),Q(1,2));answer=Q(0);beta=Q(15,16)
    for t,row in enumerate(pol):
        nxt=[Q(0),Q(0)]
        for x,a in enumerate(row):
            ps=transition(t,x,a)
            adv=cost(t,x,a)+beta*sum(p*v for p,v in zip(ps,values[t+1]))-values[t][x]
            answer+=beta**t*mass[x]*adv
            for y,p in enumerate(ps):nxt[y]+=mass[x]*p
        mass=tuple(nxt)
        if sum(mass)!=1:raise AssertionError('Conservation')
    return answer

def coverage(actual,retained):
    if not set(actual)<=set(retained):raise ValueError('Missing actual pattern')
    return True

def example():
    from scipy.optimize import minimize_scalar,linprog
    terms=((1,(1,0)),(1,(1,1)),(2,(0,2)))
    opt=minimize_scalar(lambda x:1/x+1/(x*(.5-x))+2/(.5-x)**2,bounds=(.001,.499),method='bounded',options={'xatol':1e-14})
    x=Q(math.floor(float(opt.x)*2**24),2**24);eta=(x,Q(1,2)-x)
    cert=certificate(eta,terms,(1,1),Q(1,2),(1,1))
    u,v=eta;independent=1/u+1/(u*v)+2/v**2
    g=(-1/u**2-1/(u*u*v),-1/(u*v*v)-4/v**3)
    if independent!=cert['upper'] or g!=cert['gradient']:raise AssertionError('Independent resource arithmetic')
    lower=independent-g[0]*u-g[1]*v-max(-g[0],-g[1])/2
    if lower!=cert['lower']:raise AssertionError('Independent dual arithmetic')
    relaxed=linprog([0,0,-1],A_ub=[[1,1,0],[-1,0,1],[0,-1,1]],b_ub=[1,0,0],bounds=[(0,1)]*3,method='highs')
    if not relaxed.success or abs(relaxed.fun+.5)>1e-12:raise AssertionError('Pair-conflict LP')
    actual=((0,1),(1,0));values=[Q(a*b) for a,b in actual]
    patterns=sorted(set(policy(t) for t in (-2,-1,0,1,2)))
    differences=[path_cost(p)-path_cost(((0,0),)*3) for p in patterns]
    for p,v in zip(patterns,differences):
        if v!=occupation_difference(p):raise AssertionError('Independent path/occupation identity')
    return dict(resource=cert,equal_allocation=objective((Q(1,4),)*2,terms),pattern_example={'unrestricted':1,'pair_conflict':Q(1,2),'complete_patterns':max(values),'attained_patterns':actual},three_date_patterns=len(patterns),three_date_cost_differences=differences)

def encode(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x

if __name__=='__main__':
    out=example();(R/'audit').mkdir(exist_ok=True)
    (R/'audit/MATH89.json').write_text(json.dumps(encode(out),sort_keys=True,indent=2)+'\n')
    print(json.dumps(encode(out),indent=2))
