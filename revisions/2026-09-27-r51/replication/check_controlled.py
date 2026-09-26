"""Standalone rational reader. No import from the constructor or SciPy.
It regenerates lower envelopes from all rectangle corners and checks a full cover.
The logarithm proof uses 34 terms (constructor uses 26) and separate arithmetic.
"""
from fractions import Fraction as Q
import json,sys,time
from functools import lru_cache

@lru_cache(maxsize=32768)
def logarithm(x):
    assert x>0
    if x<1:
        l,h=logarithm(1/x);return -h,-l
    n=0
    while x>2:x=x/2;n+=1
    z=(x-1)/(x+1);power=z;answer=Q(0);scale=2**90
    for k in range(34):
        term=2*power/Q(2*k+1)
        answer+=Q(term.numerator*scale//term.denominator,scale);power*=z*z
    error=Q(34,scale)+2*power/(69*(1-z*z))
    low,high=answer,answer+error
    if n:
        l,h=logarithm(Q(2));low+=n*l;high+=n*h
    return low,high

def val(f,x):return f[0]+f[1]*x

def diff(f,g):return [f[0]-g[0],f[1]-g[1]]

def integral(n,d,l,h):
    if d[1]==0:
        t=sum(n[k]*(h**(k+1)-l**(k+1))/(k+1) for k in range(3))/d[0]
        return t,t
    b=n[2]/d[1];a=(n[1]-b*d[0])/d[1];r=(n[0]-a*d[0])/d[1]
    t=a*(h-l)+b*(h*h-l*l)/2
    if not r:return t,t
    ll,hh=logarithm(val(d,h)/val(d,l))
    return t+min(r*ll,r*hh),t+max(r*ll,r*hh)

def model(raw):
    d={k:([Q(x) for x in v] if isinstance(v,list) else Q(v)) for k,v in raw.items() if k!='id'}
    assert set(d)=={'beta','eps','c','theta','g','h','k'}
    assert 0<d['beta']<1 and d['eps']>0 and d['c']>0
    assert len(d['theta'])==2 and all(abs(t)<=1 for t in d['theta'])
    for key in ['g','h','k']:
        assert len(d[key])==2 and min(d[key][0],sum(d[key]))>0
    assert min(d['h'][0],sum(d['h']))>=d['eps']
    return d

def envelope(d,box):
    # Four moment corners generate affine functions, minimized independently.
    u0,u1,z0,z1=box;cost=[[],[]];reg=[[],[]];cuts={Q(0),Q(1),Q(1,2)}
    for a in range(2):
        for u in [u0,u1]:
            for z in [z0,z1]:
                th=d['theta'][a];b=d['beta'];e=d['eps'];c=d['c']
                level=d['h'][0]+d['h'][1]/2-e*u
                slope=th*(d['h'][1]/6-e*z)
                k=d['k'] if a else [Q(0),Q(0)]
                g=[Q(0),Q(0)] if a else d['g']
                cost[a].append([k[0]+b*c*(level-slope),k[1]+2*b*c*slope])
                reg[a].append([g[0]+b*e*(u-th*z),g[1]+2*b*e*th*z])
    low=Q(0);high=Q(0)
    # The corner minima switch only at x=1/2 because u enters with fixed sign.
    for left,right in [(Q(0),Q(1,2)),(Q(1,2),Q(1))]:
        x=(left+right)/2
        q=[min(fs,key=lambda f:val(f,x)) for fs in cost]
        v=[min(fs,key=lambda f:val(f,x)) for fs in reg]
        breaks={left,right}
        for f in [diff(q[0],q[1]),diff(v[0],v[1]),diff(v[0],[d['eps'],0]),diff(v[1],[d['eps'],0])]:
            if f[1] and left < -f[0]/f[1] < right:breaks.add(-f[0]/f[1])
        breaks=sorted(breaks)
        for l,h in zip(breaks,breaks[1:]):
            x=(l+h)/2;choices=[a for a in range(2) if val(v[a],x)<=d['eps']]
            assert choices
            cheap=min(range(2),key=lambda a:val(q[a],x))
            if cheap in choices:
                z=val(q[cheap],(l+h)/2)*(h-l);ll=hh=z
            else:
                feasible=choices[0];other=1-feasible
                # q_feasible + p_other (q_other-q_feasible), with p_other binding.
                a=diff(q[other],q[feasible]);b=[d['eps']-v[feasible][0],-v[feasible][1]]
                num=[a[0]*b[0],a[0]*b[1]+a[1]*b[0],a[1]*b[1]]
                ll,hh=integral(num,diff(v[other],v[feasible]),l,h)
                z=val(q[feasible],(l+h)/2)*(h-l);ll+=z;hh+=z
            low+=ll;high+=hh
    return low,high

def check(proof):
    start=time.perf_counter();assert proof['schema']=='NBO-controlled-density-v1'
    d=model(proof['raw']);u,z=map(Q,proof['moment'])
    assert 0<=u<=1 and abs(z)<=u*(1-u)
    if proof['restricted']:assert z==0
    L,U=Q(proof['lower']),Q(proof['upper'])
    assert L<=U and U-L==Q(proof['width'])
    assert envelope(d,[u,u,z,z])[1]<=U
    one_dim=proof['restricted'] or all(t==0 for t in d['theta'])
    root=[Q(0),Q(1),Q(0) if one_dim else Q(-1,4),Q(0) if one_dim else Q(1,4)]
    seen=set();leaves=0
    def visit(index,box,inherited=None):
        nonlocal leaves
        assert index not in seen and 0<=index<len(proof['nodes']);seen.add(index)
        node=proof['nodes'][index];assert list(map(Q,node['box']))==box
        a,b,c,e=box;assert a<=b and c<=e
        if node.get('outside'):
            w=min(b,max(a,Q(1,2)));maximum=w*(1-w)
            assert c>maximum or e < -maximum
            assert 'children' not in node;return
        independent=envelope(d,box)[0]
        if inherited is not None:independent=max(independent,inherited)
        given=Q(node['lower']);assert given<=independent
        if 'children' in node:
            axis,mid=node['split'];mid=Q(mid)
            assert axis in [0,2] and box[axis]<mid<box[axis+1]
            assert len(node['children'])==2
            left=box.copy();right=box.copy();left[axis+1]=mid;right[axis]=mid
            visit(node['children'][0],left,given);visit(node['children'][1],right,given)
        else:
            leaves+=1;assert L<=given
            if node.get('pruned'):assert U<=given
    visit(0,root)
    assert len(seen)==len(proof['nodes'])
    assert (proof['status']=='target')==(U-L<=Q(proof['target']))
    return {'verified':True,'nodes':len(seen),'leaves':leaves,'verifier_seconds':time.perf_counter()-start}

if __name__=='__main__':
    print(json.dumps(check(json.load(open(sys.argv[1]))),indent=2))
