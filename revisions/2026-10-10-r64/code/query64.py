"""Certificate-gated learned query routing; original economic primitives.

A prediction replaces a necessary query location, never adds a mandatory
initial point or supplies a certificate endpoint. Inherited sources are read
without modification. Scalar-control and even state dimension are explicit.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'2026-10-10-r63/code'))
import query63 as q
import numpy as np
F=q.F; I=q.I; B=q.B

class Oracle(q.Oracle):
    def __init__(self,mode='adaptive',models=None,max_probes=512):
        super().__init__(mode,models,max_probes)
        self.counts.update(prediction_free_returns=0,routed_queries=0,prediction_declined=0)

    def _solve(self,x,r,tol):
        x=np.asarray(x,dtype=float)
        if x.ndim!=2 or x.shape[1]%2 or r<1 or not np.all(np.isfinite(x)) or np.any(x<0) or np.any(x>1):
            raise ValueError('Invalid state')
        if not 0<tol<1:raise ValueError('Invalid tolerance')
        N,d=x.shape
        if r==1:return self.terminal(x,tol)
        self.counts['value_queries']+=N
        self.counts['max_batch']=max(N,self.counts['max_batch'])
        G,M=q.regularity(r-1,d);H=F(21,4)+B*M*F(5*d,32)
        lam=F(13,16)+B*G*F(3*d,8)
        capacity=q.cap_interval(x);cap=q.clamp(capacity.lo,capacity.lo)
        missing=q.rat(lam)*(I.point(capacity.hi)-I.point(cap))
        points=np.zeros((N,self.max_probes));lows=np.zeros_like(points);highs=np.zeros_like(points)
        points[:,1]=cap;size=np.full(N,2,dtype=int)
        left=self.q(x,points[:,0],r,tol);right=self.q(x,cap,r,tol)
        lows[:,0]=left.lo;highs[:,0]=left.hi;lows[:,1]=right.lo;highs[:,1]=right.hi
        running_lower=np.nextafter(q.parabola_lower(left.lo,right.lo,cap,H)-missing.hi,-np.inf)
        predicted=np.full(N,np.nan);asked=np.zeros(N,dtype=bool)
        active=np.arange(N);outlo=np.zeros(N);outup=np.zeros(N);outact=np.zeros(N)
        while len(active):
            width=int(size[active].max());cols=np.arange(width-1)[None,:]
            valid=cols<(size[active]-1)[:,None]
            p=points[active,:width];ll=lows[active,:width];hh=highs[active,:width]
            used=np.arange(width)[None,:]<size[active,None]
            endwidth=(I.point(hh)-I.point(ll)+I.point(missing.hi[active,None])).hi
            if np.any(used & (endwidth>5*tol/8)):
                raise RuntimeError('Precision budget exceeded; certificate withheld')
            h=I.point(p[:,1:])-I.point(p[:,:-1]);K=q.rat(H/2)*h.square()
            lft=I.point(ll[:,:-1]);rgt=I.point(ll[:,1:]);diff=rgt-lft
            safeK=np.where(valid,K.hi,1.);kk=I.point(safeK)
            mid=(lft+rgt)/2-kk/4-diff.square()/(4*kk)
            low=np.where(diff.lo>=safeK,lft.lo,np.where(diff.hi<=-safeK,rgt.lo,mid.lo))
            low=np.where(valid,low,np.inf)
            which=np.argmin(low,axis=1)
            lb=np.nextafter(np.maximum(0,low[np.arange(len(active)),which]-missing.hi[active]),-np.inf)
            running_lower[active]=np.maximum(running_lower[active],lb);lb=running_lower[active]
            candidate=np.where(used,hh,np.inf);best=np.argmin(candidate,axis=1)
            ub=candidate[np.arange(len(active)),best];gap=(I.point(ub)-I.point(lb)).hi
            done=gap<=tol;ids=active[done]
            outlo[ids]=lb[done];outup[ids]=ub[done];outact[ids]=p[np.flatnonzero(done),best[done]]
            first=done & (size[active]==2)
            self.counts['accepted_first_partition']+=int(first.sum())
            self.counts['prediction_free_returns']+=int(first.sum())
            todo=active[~done];interval=which[~done]
            if not len(todo):break
            if np.any(size[todo]>=self.max_probes):raise RuntimeError('Declared refinement cap exhausted')
            l=points[todo,interval];u=points[todo,interval+1];fraction=np.full(len(todo),.5)
            if self.mode!='bisection':
                k=q.up(H/2)*(u-l)**2;dif=lows[todo,interval+1]-lows[todo,interval]
                fraction=np.clip(.5-dif/(2*k),.25,.75)
            probe=q.clamp(l+fraction*(u-l),u)
            if self.mode in ('relu','quadratic'):
                new=todo[~asked[todo]]
                if len(new):predicted[new]=self.propose(x[new],r,cap[new]);asked[new]=True
                suggestion=predicted[todo]
                route=(suggestion>=l+.25*(u-l)) & (suggestion<=u-.25*(u-l))
                probe=np.where(route,suggestion,probe)
                self.counts['routed_queries']+=int(route.sum())
                self.counts['prediction_declined']+=int((~route).sum())
            # Fifth-interior condition is checked, not presumed after rounding.
            if np.any((probe<=l)|(probe>=u)|(probe<l+.2*(u-l))|(probe>u-.2*(u-l))):
                raise RuntimeError('Rounded query violates protected interior')
            val=self.q(x[todo],probe,r,tol)
            for row,j,v,vl,vu in zip(todo,interval+1,probe,val.lo,val.hi):
                sz=size[row]
                points[row,j+1:sz+1]=points[row,j:sz].copy()
                lows[row,j+1:sz+1]=lows[row,j:sz].copy();highs[row,j+1:sz+1]=highs[row,j:sz].copy()
                points[row,j]=v;lows[row,j]=vl;highs[row,j]=vu;size[row]+=1
            self.counts['refinements']+=len(todo);active=todo
        self.counts['max_probes']=max(self.counts['max_probes'],int(size.max()))
        if np.any(outup<outlo) or np.any(outact>capacity.lo):raise AssertionError('Invalid certificate')
        return dict(lower=outlo,upper=outup,action=outact,probes=size,
                    gap=(I.point(outup)-I.point(outlo)).hi,
                    fitted_selected=asked & np.isfinite(predicted) & (outact==predicted))
