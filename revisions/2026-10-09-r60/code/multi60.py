"""Two-control rational optimization with exact box-shock ReLU integration.
The economic extension is nested at a2=0 with the second shock disabled.
This is a fitted-action experiment, not a claim of full two-control policy welfare.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import product
from math import factorial
import time
import search60 as u
n=u.n

def mean_relu(z,radii):
    radii=[abs(F(r)) for r in radii if r]
    if not radii:return max(F(0),z)
    q=len(radii);den=F(2**q*factorial(q+1))
    for r in radii:den*=r
    value=F(0)
    for signs in product((-1,1),repeat=q):
        x=z+sum(s*r for s,r in zip(signs,radii));sign=1
        for s in signs:sign*=s
        value+=sign*max(F(0),x)**(q+1)
    return value/den

@dataclass
class Objective2:
    linear:list
    quadratic:list
    quartic:list
    cross:F
    features:list
    def value(self,a):
        return sum(self.linear[j]*a[j]+self.quadratic[j]*a[j]**2+self.quartic[j]*a[j]**4 for j in range(2))+self.cross*a[0]*a[1]+sum(w*mean_relu(z+sum(s[j]*a[j] for j in range(2)),r) for w,z,s,r in self.features)
    def bound(self,lo,hi):
        lower=F(0);upper=F(0)
        for j in range(2):
            for c,p in ((self.linear[j],1),(self.quadratic[j],2),(self.quartic[j],4)):
                a,b=sorted((c*lo[j]**p,c*hi[j]**p));lower+=a;upper+=b
        a,b=sorted((self.cross*lo[0]*lo[1],self.cross*hi[0]*hi[1]));lower+=a;upper+=b
        for w,z,s,r in self.features:
            low=z;high=z
            for j in range(2):
                a,b=sorted((s[j]*lo[j],s[j]*hi[j]));low+=a;high+=b
            a,b=sorted((w*mean_relu(low,r),w*mean_relu(high,r)));lower+=a;upper+=b
        return lower,upper
    def payload(self):return dict(linear=list(map(str,self.linear)),quadratic=list(map(str,self.quadratic)),quartic=list(map(str,self.quartic)),cross=str(self.cross),features=[[str(w),str(z),list(map(str,s)),list(map(str,r))] for w,z,s,r in self.features])
    @classmethod
    def load(cls,v):return cls(list(map(F,v['linear'])),list(map(F,v['quadratic'])),list(map(F,v['quartic'])),F(v['cross']),[(F(w),F(z),list(map(F,s)),list(map(F,r))) for w,z,s,r in v['features']])

def from_critic(state,critic,two_shocks):
    if critic.kind!='relu' or len(state)!=2:raise ValueError('Expected trained two-state ReLU critic')
    x=list(map(F,state));p=critic.params;beta=F(n.BETA)
    f=[F(1,16)+x[j]/2+x[1-j]/8+x[j]*(1-x[1-j])/16 for j in range(2)]
    B=[[F(1,2),F(1,4)],[F(1,4),F(1,2)]]
    linear=[beta*sum(F(float(p['v'][i]))*B[i][j] for i in range(2)) for j in range(2)];features=[]
    for k in range(len(p['u'])):
        W=[F(float(p['W'][i,k])) for i in range(2)];z=F(float(p['b'][k]))+sum(W[i]*f[i] for i in range(2))
        slopes=[sum(W[i]*B[i][j] for i in range(2)) for j in range(2)]
        radii=[abs(W[0]-W[1])/32]
        if two_shocks:radii.append(abs(W[0]+W[1])/64)
        features.append((beta*F(float(p['u'][k])),z,slopes,radii))
    return Objective2(linear,[F(1),F(1)],[F(4),F(4)],F(1,4),features)

def exhaustive(o,cap,Q):
    start=time.perf_counter();best=None;score=None;count=0;ties=0;bits=0
    for i in range(cap+1):
        for j in range(cap-i+1):
            value=o.value((F(i,Q),F(j,Q)));count+=1;bits=max(bits,value.numerator.bit_length(),value.denominator.bit_length())
            if score is None or value<score:best=(i,j);score=value;ties=1
            elif value==score:ties+=1
    return dict(index=list(best),objective_exact=str(score),evaluations=count,ties=ties,seconds=time.perf_counter()-start,max_recorded_operand_bits=bits)

def adaptive(o,cap,Q,node_limit=256):
    start=time.perf_counter();seeds={(0,0),(cap,0),(0,cap),(cap//3,cap//3)}
    vals={a:o.value(tuple(F(x,Q) for x in a)) for a in seeds};best=min(vals,key=lambda k:(vals[k],k));score=vals[best]
    stack=[((0,0),(cap,cap))];nodes=0;pruned=0;peak=1;exact=len(vals)
    while stack:
        if nodes>=node_limit:
            r=exhaustive(o,cap,Q);r.update(fallback=True,nodes=nodes,pruned=pruned,peak_stack=peak,pre_fallback_evaluations=exact,seconds=time.perf_counter()-start);return r
        lo,hi=stack.pop();nodes+=1
        if sum(lo)>cap:pruned+=1;continue
        lower,upper=o.bound(tuple(F(x,Q) for x in lo),tuple(F(x,Q) for x in hi))
        if lower>score or (lower==score and lo>=best):pruned+=1;continue
        if lo==hi:
            v=o.value(tuple(F(x,Q) for x in lo));exact+=1
            if (v,lo)<(score,best):score=v;best=lo
        else:
            axis=max(range(2),key=lambda j:hi[j]-lo[j]);mid=(lo[axis]+hi[axis])//2
            lh=list(hi);lh[axis]=mid;rl=list(lo);rl[axis]=mid+1
            stack.extend(((tuple(rl),hi),(lo,tuple(lh))));peak=max(peak,len(stack))
    return dict(index=list(best),objective_exact=str(score),evaluations=exact,nodes=nodes,pruned=pruned,peak_stack=peak,fallback=False,seconds=time.perf_counter()-start)
