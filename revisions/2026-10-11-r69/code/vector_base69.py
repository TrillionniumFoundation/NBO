"""Two controls and two independent continuous innovations, without state tables.

This is the already specified capacity-coupled R62 investment extension.
Adaptive triangular action covers and original-law descendant queries are
new; inherited tensor references are never loaded or consulted.
"""
from pathlib import Path
import sys,itertools,math
import numpy as np
import kernel66 as k
q=k.q;I=k.I;F=k.F;B=k.B
import core62 as c


def project(a,cap):
    a=np.maximum(0,np.asarray(a,dtype=float));hit=a.sum(axis=1)>cap
    t=np.clip((a[:,0]-a[:,1]+cap)/2,0,cap)
    a[hit]=np.stack([t,cap-t],axis=1)[hit]
    return np.floor(a*2**32)/2**32

def terminal_value_grad(x,a):
    xx=I.point(x);aa=I.point(a);d=x.shape[1]
    y=c.transition(xx,aa,0.,0.);n=q.n;nx=I(np.roll(y.lo,-1,axis=1),np.roll(y.hi,-1,axis=1))
    short=F(1,2)-n.s.isum(y)*q.rat(F(2,d))
    mean1=n.hinge_mean(short,F(1,32))
    mean2=n.o.positive_moment(short,F(1,32),2)
    value=4*n.s.isum((y-F(5,8)).square())/d+n.s.isum((y-nx).square())/(4*d)+2*mean2+q.rat(F(1,512))
    value=c.stage(xx,aa)+q.rat(B)*value
    gradients=[]
    for j in range(2):
        bj=np.where(np.arange(d)%2==j,.5,.25);diff=bj-np.roll(bj,-1)
        D=8*n.s.isum((y-F(5,8))*bj)/d+n.s.isum((y-nx)*diff)/(2*d)-3*mean1
        av=n.s.col(aa,j);other=n.s.col(aa,1-j)
        gradients.append(2*av+16*av.square()*av+other/4+q.rat(B)*D)
    return value,n.s.stack(gradients)


def parabolic_triangle_lower(vertices,lows,H):
    """Validated dual lower bound for each triangular minorant.

Floating minimizers are proposals only; the supporting-plane lower bound is
computed outward. Thus projection or linear-solve rounding cannot forge it.
"""
    v=np.asarray(vertices);lo=np.asarray(lows);N=len(v)
    z0,z1,z2=(I.point(v[:,j,:]) for j in range(3));n=q.n
    b1=I.point(lo[:,1])-I.point(lo[:,0])-q.rat(H/2)*(n.s.isum(z1.square())-n.s.isum(z0.square()))
    b2=I.point(lo[:,2])-I.point(lo[:,0])-q.rat(H/2)*(n.s.isum(z2.square())-n.s.isum(z0.square()))
    e1=z1-z0;e2=z2-z0
    det=n.s.col(e1,0)*n.s.col(e2,1)-n.s.col(e1,1)*n.s.col(e2,0)
    if np.any((det.lo<=0)&(det.hi>=0)):raise RuntimeError('Degenerate triangular arithmetic')
    ax=(b1*n.s.col(e2,1)-b2*n.s.col(e1,1))/det
    ay=(n.s.col(e1,0)*b2-n.s.col(e2,0)*b1)/det
    A=n.s.stack([ax,ay]);C=I.point(lo[:,0])-q.rat(H/2)*n.s.isum(z0.square())-n.s.isum(A*z0)
    center=-A.midpoint()/float(H);candidates=[]
    # All edge projections and the unconstrained minimizer are allowed as
    # support points, even if roundoff puts a point outside the triangle.
    candidates.append(center)
    for j,h in ((0,1),(1,2),(2,0)):
        edge=v[:,h]-v[:,j];frac=np.sum((center-v[:,j])*edge,axis=1)/np.sum(edge*edge,axis=1)
        candidates.append(v[:,j]+np.clip(frac,0,1)[:,None]*edge)
    out=np.full(N,-np.inf)
    for point in candidates:
        p=I.point(point);val=q.rat(H/2)*n.s.isum(p.square())+n.s.isum(A*p)+C
        grad=q.rat(H)*p+A
        support=np.stack([n.s.isum(grad*(I.point(v[:,j])-p)).lo for j in range(3)])
        lb=(I.point(val.lo)+I.point(support.min(axis=0))).lo
        out=np.maximum(out,lb)
    return out


class Oracle:
    def __init__(self,max_nodes=1024,batch=1024):
        self.max_nodes=max_nodes;self.batch=batch
        self.counts=dict(value_queries=0,q_queries=0,terminal_queries=0,shock_children=0,
                         refinements=0,max_batch=0,max_triangles=0,rational_fallbacks=0,rational_q_queries=0,
                         stored_state_nodes=0,controls=2,shock_dimension=2)
    def qbound(self,x,a,r,tol):
        self.counts['q_queries']+=len(x)
        if r==1:
            self.counts['terminal_queries']+=len(x)
            return terminal_value_grad(x,a)[0]
        d=x.shape[1];G,M=q.regularity(r-1,d)
        zeta=B*M*d*F(5,24576);bins=1
        while zeta/(bins*bins)>F(tol)/4:bins*=2
        pairs=list(itertools.product(range(bins),repeat=2));den=len(pairs)
        xx=np.repeat(x,den,axis=0);aa=np.repeat(a,den,axis=0)
        zz=np.tile(np.array([float(F(2*z+1-bins,32*bins)) for z,w in pairs]),len(x))
        ww=np.tile(np.array([float(F(2*w+1-bins,64*bins)) for z,w in pairs]),len(x))
        lower=[];upper=[]
        for start in range(0,len(xx),self.batch):
            end=min(start+self.batch,len(xx))
            y=c.transition(I.point(xx[start:end]),I.point(aa[start:end]),I.point(zz[start:end]),I.point(ww[start:end]))
            mid=y.midpoint();rad=np.maximum((I.point(mid)-I.point(y.lo)).hi,(I.point(y.hi)-I.point(mid)).hi)
            err=q.rat(G)*q.n.s.isum(I.point(rad))
            child=self.solve(mid,r-1,float(F(tol)/(4*B)))
            lower.append((I.point(child['lower'])-err).lo);upper.append((I.point(child['upper'])+err).hi)
            self.counts['shock_children']+=len(mid)
        low=q.n.s.isum(I.point(np.concatenate(lower).reshape(len(x),den)))
        high=q.n.s.isum(I.point(np.concatenate(upper).reshape(len(x),den)))
        stage=c.stage(I.point(x),I.point(a));den=bins*bins
        return I((stage+q.rat(B)*low/den).lo,(stage+q.rat(B)*high/den+q.rat(zeta/den)).hi)
    def terminal(self,x,tol):
        N,d=x.shape;cap=q.clamp(q.cap_interval(x).lo,q.cap_interval(x).lo)
        a=project(np.column_stack([q.terminal_guess(x)/2,q.terminal_guess(x)/2]),cap)
        _,M=q.regularity(0,d);H=float(F(21,4)+B*M*F(9*d,32))
        active=np.arange(N);outl=np.zeros(N);outu=np.zeros(N);outa=np.zeros((N,2));probes=np.zeros(N,dtype=int)
        old=a.copy();z=a.copy();momentum=1.
        lam=F(13,16)+B*q.regularity(0,d)[0]*F(3*d,8)
        missing=(q.rat(lam)*(I.point(q.cap_interval(x).hi)-I.point(cap))).hi
        for step in range(400):
            if not len(active):break
            value,grad=terminal_value_grad(x[active],a[active]);self.counts['q_queries']+=len(active);self.counts['terminal_queries']+=len(active)
            dot=q.n.s.isum(grad*I.point(a[active]));minimum=np.minimum(0,grad.lo.min(axis=1))
            gap=(dot-I.point(cap[active])*I.point(minimum)+I.point(missing[active])).hi
            lower=(I.point(value.lo)-I.point(np.maximum(0,gap))).lo
            total=(I.point(value.hi)-I.point(lower)).hi;ok=total<=tol;probes[active]+=1
            ids=active[ok];outl[ids]=np.maximum(0,lower[ok]);outu[ids]=value.hi[ok];outa[ids]=a[ids]
            active=active[~ok]
            if not len(active):break
            # A fixed-step accelerated projected gradient is a proposal engine;
            # only the outward Frank--Wolfe residual authorizes return.
            _,g=terminal_value_grad(x[active],z[active]);self.counts['terminal_queries']+=len(active)
            new=project(z[active]-g.midpoint()/H,cap[active]);nxt=(1+math.sqrt(1+4*momentum**2))/2
            z[active]=project(new+(momentum-1)/nxt*(new-a[active]),cap[active]);a[active]=new;momentum=nxt
        if len(active):raise RuntimeError('Terminal vector precision/cap')
        return dict(lower=outl,upper=outu,action=outa,gap=(I.point(outu)-I.point(outl)).hi,probes=probes)
    def solve(self,x,r,tol):
        x=np.asarray(x,dtype=float)
        if x.ndim!=2 or x.shape[1]%2 or np.any(x<0) or np.any(x>1) or not np.isfinite(x).all():raise ValueError('State')
        if len(x)>self.batch:
            rows=[self.solve(x[j:j+self.batch],r,tol) for j in range(0,len(x),self.batch)]
            return {name:np.concatenate([v[name] for v in rows]) for name in rows[0]}
        self.counts['value_queries']+=len(x);self.counts['max_batch']=max(len(x),self.counts['max_batch'])
        try:return self._solve(x,r,tol)
        except RuntimeError:
            rows=[]
            for row in x:
                self.counts['rational_fallbacks']+=1;rows.append(self.rational(list(map(lambda z:F(float(z)),row)),r,F(tol)))
            lo=np.array([float(np.nextafter(float(z[0]),-np.inf)) for z in rows]);hi=np.array([float(np.nextafter(float(z[1]),np.inf)) for z in rows])
            return dict(lower=lo,upper=hi,action=np.array([[float(a) for a in z[2]] for z in rows]),gap=(I.point(hi)-I.point(lo)).hi,probes=np.zeros(len(x),dtype=int))
    def _solve(self,x,r,tol):
        if r==1:return self.terminal(x,tol)
        N,d=x.shape;G,M=q.regularity(r-1,d);H=F(21,4)+B*M*F(9*d,32);lam=F(13,16)+B*G*F(3*d,8)
        capacity=q.cap_interval(x);cap=q.clamp(capacity.lo,capacity.lo)
        missing=(q.rat(lam)*(I.point(capacity.hi)-I.point(cap))).hi
        rounding=q.up(2*lam/F(2**32));points=np.zeros((N,self.max_nodes,2));points[:,1,0]=cap;points[:,2,1]=cap
        lows=np.zeros((N,self.max_nodes));highs=np.zeros_like(lows);sizes=np.full(N,3,dtype=int)
        for j in range(3):
            v=self.qbound(x,points[:,j],r,tol);lows[:,j]=v.lo;highs[:,j]=v.hi
        proposal=self.proposal(x,r,cap) if hasattr(self,'proposal') else None
        if proposal is not None:
            if proposal.shape!=(N,2) or np.any(proposal<0) or np.any(proposal.sum(axis=1)>cap):
                raise ValueError('Invalid optional vector witness')
            points[:,3]=proposal
            value=self.qbound(x,proposal,r,tol)
            lows[:,3]=value.lo;highs[:,3]=value.hi;sizes+=1
        # The optional witness changes only the upper certificate. The
        # original triangle still covers every feasible continuous action.
        triangles=[[(0,1,2)] for _ in x];running=np.zeros(N);active=np.arange(N)
        outl=np.zeros(N);outu=np.zeros(N);outa=np.zeros((N,2))
        while len(active):
            flat=[(row,tri) for row in active for tri in triangles[row]]
            verts=np.array([points[row,list(tri)] for row,tri in flat]);vals=np.array([lows[row,list(tri)] for row,tri in flat])
            lower=parabolic_triangle_lower(verts,vals,H);offset=0;todo=[];edges=[]
            for row in active:
                num=len(triangles[row]);loc=int(np.argmin(lower[offset:offset+num]));lb=float(lower[offset+loc]);offset+=num
                running[row]=max(running[row],float(np.nextafter(lb-missing[row],-np.inf)))
                sz=sizes[row];best=int(np.argmin(highs[row,:sz]));upper=(I.point(highs[row,best])+I.point(rounding)).hi.item()
                if np.max((I.point(highs[row,:sz])-I.point(lows[row,:sz])+I.point(missing[row])+I.point(rounding)).hi)>5*tol/8:
                    raise RuntimeError('Vector endpoint width')
                gap=(I.point(upper)-I.point(running[row])).hi.item()
                if gap<=tol:
                    outl[row]=running[row];outu[row]=upper;outa[row]=np.floor(points[row,best]*2**32)/2**32
                else:
                    if sz>=self.max_nodes:raise RuntimeError('Vector cap')
                    splitloc=loc
                    if getattr(self,'uniform',False):
                        splitloc=max(range(len(triangles[row])),key=lambda n:max(
                            np.sum((points[row,triangles[row][n][j]]-points[row,triangles[row][n][h]])**2)
                            for j,h in ((0,1),(1,2),(2,0))))
                    tri=triangles[row][splitloc];j,h=max(((0,1),(1,2),(2,0)),key=lambda e:np.sum((points[row,tri[e[0]]]-points[row,tri[e[1]]])**2))
                    other=({0,1,2}-{j,h}).pop();pa,pb,pc=tri[j],tri[h],tri[other];middle=(points[row,pa]+points[row,pb])/2
                    if np.array_equal(middle,points[row,pa]) or np.array_equal(middle,points[row,pb]):raise RuntimeError('Vector rounding floor')
                    points[row,sz]=middle;triangles[row][splitloc]=(pa,sz,pc);triangles[row].append((sz,pb,pc));todo.append(row);edges.append(sz)
            if not todo:break
            todo=np.array(todo);edges=np.array(edges);v=self.qbound(x[todo],points[todo,edges],r,tol)
            lows[todo,edges]=v.lo;highs[todo,edges]=v.hi;sizes[todo]+=1;self.counts['refinements']+=len(todo);active=todo
            self.counts['max_triangles']=max(self.counts['max_triangles'],max(map(len,triangles)))
        return dict(lower=outl,upper=outu,action=outa,gap=(I.point(outu)-I.point(outl)).hi,probes=sizes)
    def rational(self,x,r,tol):
        d=len(x);G,M=q.regularity(r-1,d);H=F(21,4)+B*M*F(9*d,32);lam=F(13,16)+B*G*F(3*d,8)
        cap0=F(1,8)+sum(x)/(8*d);cap=F((cap0*2**32).__floor__(),2**32);miss=lam*(cap0-cap)
        if tol<=16*lam/F(2**32):raise RuntimeError('Vector request below action precision')
        A=1
        while H*(cap/A)**2+2*lam/F(2**32)+miss>tol/4:A*=2
        zeta=B*M*d*F(5,24576);bins=1
        while r>1 and zeta/(bins*bins)>tol/4:bins*=2
        low=None;upper=None;chosen=None
        for i in range(A+1):
            for j in range(A-i+1):
                a=[F((cap*i*2**32/A).__floor__(),2**32),F((cap*j*2**32/A).__floor__(),2**32)];self.counts['rational_q_queries']+=1
                y=[F(1,16)+x[k]/2+x[(k+1)%d]/8+x[k]*(1-x[(k+1)%d])/16+(F(1,2) if k%2==0 else F(1,4))*a[0]+(F(1,4) if k%2==0 else F(1,2))*a[1] for k in range(d)]
                stage=exact_stage(x,a)
                if r==1:
                    b=F(1,2)-2*sum(y)/d;radius=F(1,32)
                    moment=(max(F(0),b+radius)**3-max(F(0),b-radius)**3)/(6*radius)
                    future=4*sum((v-F(5,8))**2 for v in y)/d+sum((y[k]-y[(k+1)%d])**2 for k in range(d))/(4*d)+2*moment+F(1,512)
                    l=u=stage+B*future
                else:
                    l=u=F(0)
                    for z,w in itertools.product(range(bins),repeat=2):
                        state=[y[k]+(1 if k%2==0 else -1)*F(2*z+1-bins,32*bins)+F(2*w+1-bins,64*bins) for k in range(d)]
                        ll,uu,_=self.rational(state,r-1,tol/(4*B));l+=ll;u+=uu
                    l=stage+B*l/(bins*bins);u=stage+B*u/(bins*bins)+zeta/(bins*bins)
                low=l if low is None else min(low,l)
                if upper is None or (u,a)<(upper,chosen):upper=u;chosen=a
        low=max(F(0),low-H*(cap/A)**2-2*lam/F(2**32)-miss)
        if upper-low>tol:raise AssertionError('Vector rational allowance')
        return low,upper,chosen


def exact_stage(x,a,terminal=False):
    d=len(x);s=max(F(0),F(1,2)-2*sum(x)/d)
    val=(4 if terminal else 2)*sum((v-F(5,8))**2 for v in x)/d+sum((x[j]-x[(j+1)%d])**2 for j in range(d))/(4*d)+2*s*s
    return val if terminal else val+sum(v*v+4*v**4 for v in a)+a[0]*a[1]/4
