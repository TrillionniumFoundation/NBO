"""Exact fitted-action witnesses and a generator-independent reference verifier.

All economic primitives are inherited unchanged. The fixed reference is the
installed zero policy; refinement attempts are not deployed between attempts.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import floor, ceil
import numpy as np
import sympy as sp
import neural55 as n
import tube55 as tube
import algebraic56 as old


def reduce_objective(state, critic):
    """Return exact action-dependent coefficients, omitting a common constant."""
    x=list(map(old.rational,state));d=len(x)
    g=[F(1,2) if j%2==0 else F(1,4) for j in range(d)]
    f=[F(1,16)+x[j]/2+x[(j+1)%d]/8+x[j]*(1-x[(j+1)%d])/16 for j in range(d)]
    features=[];squares=[];q1=F(0);q2=F(1)
    if critic.kind=='relu':
        _,q1,q2,features,_=old.reduce_critic(state,critic.params)
    elif critic.kind=='quadratic':
        p=critic.params;v=list(map(old.rational,p['v']));Q=[[old.rational(z) for z in row] for row in p['Q']]
        q1=n.BETA*(sum(v[j]*g[j] for j in range(d))+sum(Q[i][j]*(f[i]*g[j]+g[i]*f[j]) for i in range(d) for j in range(d)))
        q2+=n.BETA*sum(Q[i][j]*g[i]*g[j] for i in range(d) for j in range(d))
    elif critic.kind=='terminal':
        if d%2:raise ValueError('Analytic terminal shortage uses even dimensions')
        q1=n.BETA*(F(8,d)*sum((f[j]-F(5,8))*g[j] for j in range(d))+F(1,2*d)*sum((f[j]-f[(j+1)%d])*(g[j]-g[(j+1)%d]) for j in range(d)))
        q2+=n.BETA*(F(4,d)*sum(z*z for z in g)+F(1,4*d)*sum((g[j]-g[(j+1)%d])**2 for j in range(d)))
        squares=[(2*n.BETA,F(1,2)-F(2,d)*sum(f),-F(2,d)*sum(g))]
    elif critic.kind!='zero':raise ValueError('No algebraic solver for '+critic.kind)
    def value(a):
        return q1*a+q2*a*a+4*a**4+sum(w*old.hinge(z+s*a,r) for w,z,s,r in features)+sum(w*max(F(0),z+s*a)**2 for w,z,s in squares)
    return q1,q2,features,squares,value


def minimize(state,critic,capindex,quantum=4096):
    capindex=int(capindex)
    if quantum<=0 or not 0<=capindex<=quantum//4:raise ValueError('Invalid lattice')
    q1,q2,features,squares,value=reduce_objective(state,critic);cap=F(capindex,quantum);knots={F(0),cap}
    for w,z,s,r in features:
        if s:
            for e in (-r,r):
                k=(e-z)/s
                if 0<k<cap:knots.add(k)
    for w,z,s in squares:
        if s and 0<-z/s<cap:knots.add(-z/s)
    knots=sorted(knots);indices={0,capindex};roots=0;a=sp.Symbol('a')
    def near(l,h):
        for j in range(max(0,floor(l*quantum)),min(capindex,ceil(h*quantum))+1):indices.add(j)
    for k in knots:near(k,k)
    for l,h in zip(knots,knots[1:]):
        m=(l+h)/2;c1=q1;c2=q2
        for w,z,s,r in features:
            v=z+s*m
            if v>=r:c1+=w*s
            elif r and v>-r:c1+=w*s*(z+r)/(2*r);c2+=w*s*s/(4*r)
        for w,z,s in squares:
            if z+s*m>0:c1+=2*w*z*s;c2+=w*s*s
        poly=sp.Poly(16*a**3+sp.Rational(2*c2.numerator,c2.denominator)*a+sp.Rational(c1.numerator,c1.denominator),a)
        for (lo,hi),mult in poly.intervals(eps=sp.Rational(1,4*quantum),inf=sp.Rational(l.numerator,l.denominator),sup=sp.Rational(h.numerator,h.denominator)):
            roots+=1;near(F(int(lo.p),int(lo.q)),F(int(hi.p),int(hi.q)))
    indices=sorted(indices);best=min(indices,key=lambda j:(value(F(j,quantum)),j))
    return dict(index=best,objective_exact=str(value(F(best,quantum))),candidate_indices=indices,pieces=max(0,len(knots)-1),isolated_roots=roots,lattice_size=capindex+1)


def proposals(critics,part,mode):
    T=len(critics)-1;N=len(part.lo)
    grid=np.zeros((T,N),dtype=np.uint16) if mode=='common-only' else n.propose(critics,part)
    exact=grid.copy();records=[]
    for t in range(T):
        terminal=t==T-1
        if not terminal and mode not in ('relu-exact','quadratic-exact'):continue
        for k in range(N):
            r=minimize(part.centers[k],critics[t+1],int(part.capindex[k]));exact[t,k]=r['index']
            value=reduce_objective(part.centers[k],critics[t+1])[-1]
            r.update(date=t,leaf=k,grid_index=int(grid[t,k]),grid_regret_exact=str(value(F(int(grid[t,k]),4096))-F(r['objective_exact'])),common_terminal=terminal)
            if terminal:grid[t,k]=exact[t,k]
            elif F(r['grid_regret_exact'])<0:raise AssertionError('Algebraic witness is worse than the feasible grid action')
            records.append(r)
    return grid,exact,records


class ReferenceVerifier:
    """Same signed smooth-reference intervals for every candidate generator."""
    def __init__(self,part,T,q):
        self.part=part;self.T=T;self.q=q;self.work={}
    def advantage(self,t,a):
        if t==self.T-1:
            return n.o.final_difference(self.part.box,a,n.I.point(np.zeros(len(a.lo))),1)
        out=tube.signed_zero_advantage(self.part.box,a,self.T-t-1,self.q,self.work)
        same=(a.lo==0)&(a.hi==0);out.lo[same]=out.hi[same]=0
        return out
    def sweep(self,grid,exact=None):
        N=len(self.part.lo);policy=np.zeros((self.T,N),dtype=np.uint16);raw={};rows=[]
        fullcap=n.s.cap(self.part.box).hi
        for t in range(self.T):
            menu=[self.part.capindex*j//8 for j in range(9)]+[grid[t]]
            if exact is not None and t<self.T-1:menu.append(exact[t])
            lowers=[];uppers=[];U=np.zeros(N);chosen=policy[t].copy()
            baseline_U=None;baseline_policy=None
            for j,ix in enumerate(menu):
                val=self.advantage(t,n.I.point(ix/4096));take=val.hi<U;chosen[take]=ix[take];U[take]=val.hi[take]
                lowers.append(val.lo);uppers.append(val.hi)
                if j==9:baseline_U=U.copy();baseline_policy=chosen.copy()
            covers=[];L=np.zeros(N)
            for j in range(8):
                val=self.advantage(t,n.I(fullcap*j/8,fullcap*(j+1)/8));covers.append(val.lo);L=np.minimum(L,val.lo)
            if np.any(U>0) or np.any(L>U) or np.any(chosen>self.part.capindex):raise AssertionError('Invalid whole-cell certificate')
            if np.any(U>baseline_U):raise AssertionError('Nested menu worsened certified upper advantage')
            C=np.maximum(L,np.minimum(0,np.min(lowers,axis=0)));gap=(n.I.point(U)-n.I.point(L)).hi
            policy[t]=chosen
            raw.update({f't{t}_indices':np.array(menu),f't{t}_lower':np.array(lowers),f't{t}_upper':np.array(uppers),f't{t}_covers':np.array(covers),f't{t}_U':U,f't{t}_L':L,f't{t}_C':C,f't{t}_gap':gap,f't{t}_selected':chosen,f't{t}_baseline_U':baseline_U,f't{t}_baseline_policy':baseline_policy})
            rows.append(dict(date=t,changed=int(np.count_nonzero(chosen)),extra_witness_changes=int(np.count_nonzero(chosen!=baseline_policy)),upper_strict_improvements=int(np.count_nonzero(U<baseline_U)),gap_upper=float(gap.max()),candidate_component_upper=float((n.I.point(U)-n.I.point(C)).hi.max()),cover_component_upper=float((n.I.point(C)-n.I.point(L)).hi.max()),max_candidate_width=float(np.max(np.array(uppers)-np.array(lowers))),max_upper_improvement=float(np.max(baseline_U-U))))
        return policy,rows,raw
