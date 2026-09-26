"""All-Borel two-period control with state/action-dependent continuous densities.
Only Fraction inequalities and explicitly bounded logarithms certify endpoints.
Floating optimization is an optional proposal, never a lower certificate.
"""
from fractions import Fraction as F
from functools import lru_cache
import json, heapq, time, math

ZERO=F(0); ONE=F(1); EPSLOG=F(1,2**72)
def enc(x):
    if isinstance(x,F): return str(x)
    if isinstance(x,dict): return {k:enc(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [enc(v) for v in x]
    return x

def validate(raw):
    d={k:([F(x) for x in v] if isinstance(v,list) else F(v)) for k,v in raw.items() if k!='id'}
    assert 0<d['beta']<1 and d['eps']>0 and d['c']>0
    assert len(d['theta'])==2 and all(abs(x)<=1 for x in d['theta'])
    for k in ['g','h','k']:
        assert len(d[k])==2
        assert min(d[k][0],sum(d[k]))>0
    assert min(d['h'][0],sum(d['h']))>=d['eps']
    return d

def ev(a,x): return a[0]+a[1]*x

def sub(a,b): return [a[0]-b[0],a[1]-b[1]]

def add(a,b): return [a[0]+b[0],a[1]+b[1]]

@lru_cache(maxsize=32768)
def log_bound(z):
    """Enclose log(z) by a rational atanh series, with range reduction."""
    assert z>0
    if z<1:
        a,b=log_bound(1/z);return -b,-a
    power=0
    while z>2:z/=2;power+=1
    t=(z-1)/(z+1); t2=t*t; term=t; lo=F(0)
    # Round each term down to bound rational bit growth, including rounding loss.
    scale=2**80
    for j in range(26):
        v=2*term/(2*j+1);lo+=F((v.numerator*scale)//v.denominator,scale);term*=t2
    hi=lo+F(26,scale)+2*term/(53*(1-t2))
    if power:
        a,b=log_bound(F(2));lo+=power*a;hi+=power*b
    return lo,hi

def integrate_ratio(num,den,a,b):
    n0,n1,n2=num;e,f=den
    if not f:
        assert e!=0
        v=(n0*(b-a)+n1*(b*b-a*a)/2+n2*(b**3-a**3)/3)/e
        return v,v
    linear=n2/f;constant=(n1-linear*e)/f;rem=n0-constant*e
    value=linear*(b*b-a*a)/2+constant*(b-a)
    if not rem:return value,value
    ratio=(e+f*b)/(e+f*a);assert ratio>0
    lo,hi=log_bound(ratio);scale=rem/f
    return value+min(scale*lo,scale*hi),value+max(scale*lo,scale*hi)

def integrate_row(q,v,eps,left,right):
    """Pointwise two-action LP integrated over an interval; exact breakpoints."""
    cuts={left,right}
    lines=[sub(v[0],[eps,0]),sub(v[1],[eps,0]),sub(v[0],v[1]),sub(q[0],q[1])]
    for a,b in lines:
        if b and left < -a/b < right:cuts.add(-a/b)
    cuts=sorted(cuts);low=F(0);high=F(0)
    for a,b in zip(cuts,cuts[1:]):
        x=(a+b)/2;vs=[ev(z,x) for z in v];qs=[ev(z,x) for z in q]
        feasible=[i for i in range(2) if vs[i]<=eps]
        if not feasible:return None
        cheap=0 if qs[0]<=qs[1] else 1
        if cheap in feasible:
            val=q[cheap][0]*(b-a)+q[cheap][1]*(b*b-a*a)/2;lo=hi=val
        else:
            # q1 + (q0-q1)(eps-v1)/(v0-v1).
            dq=sub(q[0],q[1]);r=[eps-v[1][0],-v[1][1]];den=sub(v[0],v[1])
            num=[dq[0]*r[0],dq[0]*r[1]+dq[1]*r[0],dq[1]*r[1]]
            lo,hi=integrate_ratio(num,den,a,b)
            val=q[1][0]*(b-a)+q[1][1]*(b*b-a*a)/2;lo+=val;hi+=val
        low+=lo;high+=hi
    return low,high

def coefficients(d,box,side,exact=False):
    """Affine cost/regret lower envelopes on each sign interval of 2x-1."""
    ul,uh,vl,vh=box;eps=d['eps'];beta=d['beta'];c=d['c']
    A=d['h'][0]+d['h'][1]/2;B=d['h'][1]/6
    costs=[];regrets=[]
    for a,theta in enumerate(d['theta']):
        # Cost decreases in u and theta*(2x-1)*v; regret increases in them.
        cv=vh if theta*side>=0 else vl
        rv=vl if theta*side>=0 else vh
        k=d['k'] if a==1 else [F(0),F(0)]
        gap=d['g'] if a==0 else [F(0),F(0)]
        cost=beta*c*(B-eps*cv)*theta
        reg=beta*eps*rv*theta
        costs.append([k[0]+beta*c*(A-eps*uh)-cost,k[1]+2*cost])
        regrets.append([gap[0]+beta*eps*ul-reg,gap[1]+2*reg])
    return costs,regrets

def bound(d,box):
    low=F(0);high=F(0)
    for a,b,side in [(F(0),F(1,2),-1),(F(1,2),F(1),1)]:
        q,v=coefficients(d,box,side);res=integrate_row(q,v,d['eps'],a,b)
        if res is None:return None
        low+=res[0];high+=res[1]
    scale=2**48
    return F((low.numerator*scale)//low.denominator,scale),F(-((-high.numerator*scale)//high.denominator),scale)

def domain_max(l,h):
    x=min(h,max(l,F(1,2)));return x*(1-x)

def disjoint(box):
    l,h,a,b=box;maximum=domain_max(l,h)
    return a>maximum or b < -maximum

def candidate(box):
    l,h,a,b=box;u=(l+h)/2;v=min(u*(1-u),max(-u*(1-u),(a+b)/2));return u,v

def exact_cost(d,u,v):
    assert 0<=u<=1 and abs(v)<=u*(1-u)
    return bound(d,[u,u,v,v])

def run(raw,target=F(1,1000),max_nodes=20000,seconds=60,restricted=False):
    start=time.perf_counter();d=validate(raw)
    one_dim=restricted or all(t==0 for t in d['theta'])
    root=[F(0),F(1),F(0) if one_dim else F(-1,4),F(0) if one_dim else F(1,4)]
    best=None;point=None
    for u in [F(0),F(1,4),F(1,2),F(3,4),F(1)]:
        for v in ([F(0)] if restricted else [-u*(1-u),F(0),u*(1-u)]):
            up=exact_cost(d,u,v)[1]
            if best is None or up<best:best,point=up,[u,v]
    root_bound=bound(d,root)[0]
    nodes=[{'box':root,'lower':root_bound}];queue=[(root_bound,0)]
    traces=[];count=1
    while queue:
        global_low=queue[0][0]
        if best-global_low<=target or count+2>max_nodes or time.perf_counter()-start>=seconds:break
        _,idx=heapq.heappop(queue);node=nodes[idx];box=node['box']
        if node['lower']>=best:node['pruned']=True;continue
        j=0 if one_dim or box[1]-box[0]>=box[3]-box[2] else 2
        mid=(box[j]+box[j+1])/2;node['split']=[j,mid];node['children']=[]
        for b in (box[:j+1]+[mid]+box[j+2:],box[:j]+[mid]+box[j+1:]):
            cid=len(nodes);child={'box':b};nodes.append(child);node['children'].append(cid);count+=1
            if disjoint(b):child['outside']=True;continue
            lo=bound(d,b)[0];lo=max(lo,node['lower']);child['lower']=lo
            u,v=candidate(b);up=exact_cost(d,u,v)[1]
            if up<best:best,point=up,[u,v]
            if lo>=best:child['pruned']=True
            else:heapq.heappush(queue,(lo,cid))
        if count in [3,7,15,31,63,127,255,511,1023,2047,4095,8191,16383]:
            traces.append({'nodes':count,'construction_seconds':time.perf_counter()-start,'lower':min(best,queue[0][0]) if queue else best,'upper':best})
    lower=min(best,queue[0][0]) if queue else best
    result={'schema':'NBO-controlled-density-v1','raw':raw,'restricted':restricted,'target':target,
            'nodes':nodes,'moment':point,'lower':lower,'upper':best,'width':best-lower,
            'construction_seconds':time.perf_counter()-start,'trace':traces,
            'status':'target' if best-lower<=target else ('node_cap' if count+2>max_nodes else 'time_cap')}
    return enc(result)

if __name__=='__main__':
    raw={'id':'pilot','beta':'3/4','eps':'1/5','c':'3/2','theta':['3/4','-3/4'],'g':['1/4','1/2'],'h':['1','1/2'],'k':['1','1/2']}
    for restricted in [False,True]:
        r=run(raw,seconds=15,max_nodes=4000,restricted=restricted)
        print({k:v for k,v in r.items() if k not in ['nodes','trace','raw']})
        open('/tmp/pilot-'+str(restricted)+'.json','w').write(json.dumps(r))
