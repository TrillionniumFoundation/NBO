"""Directed common-innovation certificates for the original d=2 economy.

No policy-value oracle: every leaf uses original stage costs and the analytic
last innovation. All acquired-actor discontinuities are enclosed by exact
integer rectangle extrema. The state law and shock law stay continuous.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import hashlib, json, math, sys, time
import numpy as np
import operators50 as o
s=o.s; I=o.I; F=o.F; BETA=o.BETA


def intersect(a:I,b:I)->I:
    return I(np.maximum(a.lo,b.lo),np.minimum(a.hi,b.hi))


def zero(n:int)->I:return I(np.zeros(n),np.zeros(n))


def positive_difference(x:I,y:I,delta:I)->I:
    """ReLU(x)-ReLU(y), preserving a separately verified x-y interval."""
    naive=o.positive(x)-o.positive(y)
    lip=I(np.minimum(0,delta.lo),np.maximum(0,delta.hi))
    out=intersect(naive,lip)
    both=(x.lo>=0)&(y.lo>=0); neither=(x.hi<=0)&(y.hi<=0)
    out.lo=np.where(both,np.maximum(out.lo,delta.lo),out.lo)
    out.hi=np.where(both,np.minimum(out.hi,delta.hi),out.hi)
    out.lo=np.where(neither,0,out.lo);out.hi=np.where(neither,0,out.hi)
    return out


def state_difference(x:I,y:I,delta:I,terminal:bool=False)->I:
    """Centered polynomial cost identity; d=2 and exact binary constants."""
    if x.lo.shape[-1]!=2:raise ValueError('This implementation is for d=2')
    val=s.isum(delta*(x+y-F(5,4)))*(2 if terminal else 1)
    dx=s.col(x,0)-s.col(x,1);dy=s.col(y,0)-s.col(y,1)
    dd=s.col(delta,0)-s.col(delta,1)
    val=val+F(1,4)*dd*(dx+dy)
    bx=F(1,2)-s.isum(x);by=F(1,2)-s.isum(y)
    val=val+2*positive_difference(bx,by,-s.isum(delta))*(o.positive(bx)+o.positive(by))
    return val


def action_difference(a:I,b:I,p:int)->I:
    return (a-b)*(a+b)*(p+4*(a.square()+b.square()))


def next_difference(x:I,y:I,delta:I,a:I,b:I)->I:
    # F(x,a,z)-F(y,b,z): the common innovation cancels, not its marginal law.
    out=[]
    for j in range(2):
        v=(j+1)%2
        out.append(s.col(delta,j)*(F(1,2)+(1-s.col(x,v))/16)
                   +s.col(delta,v)*(F(1,8)-s.col(y,j)/16)
                   +(F(1,2) if j==0 else F(1,4))*(a-b))
    return s.stack(out)


def last_pair(x:I,y:I,delta:I,a:I,b:I,p:int)->I:
    # Terminal noise variance terms cancel exactly in d=2; the shortage
    # depends on y1+y2, so the common +/- shock cancels there as well.
    out=state_difference(x,y,delta)+action_difference(a,b,p)
    xx=o.deterministic_next(x,a);yy=o.deterministic_next(y,b)
    dd=next_difference(x,y,delta,a,b)
    return out+float(BETA)*state_difference(xx,yy,dd,True)


class RectangleActor:
    """Exact 2-D range extrema, with O(log(n)^2 n^2) preprocessing."""
    def __init__(self,actions:np.ndarray,bits:int):
        self.n=1<<bits;self.bits=bits
        a=np.asarray(actions)
        if a.shape!=(self.n,self.n) or np.any(a<0) or np.any(a>1024) or np.any(a!=np.floor(a)):
            raise ValueError('Expected quantum indices on a square observation grid')
        self.a=a.astype(np.uint16);levels=bits+1
        self.mn=np.zeros((levels,levels,self.n,self.n),dtype=np.uint16)
        self.mx=self.mn.copy();self.mn[0,0]=self.mx[0,0]=self.a
        for k in range(1,levels):
            h=1<<(k-1);n=self.n-(1<<k)+1
            self.mn[k,0,:n]=np.minimum(self.mn[k-1,0,:n],self.mn[k-1,0,h:h+n])
            self.mx[k,0,:n]=np.maximum(self.mx[k-1,0,:n],self.mx[k-1,0,h:h+n])
        for k in range(levels):
            for l in range(1,levels):
                h=1<<(l-1);n=self.n-(1<<l)+1
                self.mn[k,l,:,:n]=np.minimum(self.mn[k,l-1,:,:n],self.mn[k,l-1,:,h:h+n])
                self.mx[k,l,:,:n]=np.maximum(self.mx[k,l-1,:,:n],self.mx[k,l-1,:,h:h+n])
        self.logs=np.floor(np.log2(np.arange(1,self.n+1))).astype(np.int64)
        self.queries=0;self.ambiguous=0
    def action(self,x:I)->I:
        lo=np.clip(np.floor(x.lo*self.n).astype(np.int64),0,self.n-1)
        hi=np.clip(np.floor(x.hi*self.n).astype(np.int64),0,self.n-1)
        k=self.logs[hi[:,0]-lo[:,0]];l=self.logs[hi[:,1]-lo[:,1]]
        i0=lo[:,0];i1=hi[:,0]-(1<<k)+1;j0=lo[:,1];j1=hi[:,1]-(1<<l)+1
        lows=[];highs=[]
        for i,j in ((i0,j0),(i0,j1),(i1,j0),(i1,j1)):
            lows.append(self.mn[k,l,i,j]);highs.append(self.mx[k,l,i,j])
        self.queries+=len(lo);self.ambiguous+=int(np.count_nonzero(np.any(lo!=hi,axis=1)))
        return I(np.minimum.reduce(lows).astype(float)/4096,np.maximum.reduce(highs).astype(float)/4096)
    @property
    def bytes(self):return self.a.nbytes+self.mn.nbytes+self.mx.nbytes+self.logs.nbytes


class PairCertificate:
    def __init__(self,policies:np.ndarray,bits:int=5,q:int=16,p:int=1):
        if q<1 or q&(q-1):raise ValueError('Dyadic innovation bins required')
        self.actors=[RectangleActor(a,bits) for a in policies];self.T=len(self.actors);self.q=q;self.p=p
        self.counts={'pair_nodes':0,'coupling_bins':0,'analytic_terminal_pairs':0,'initial_pairs':0,
                     'initial_identity_pairs':0,'largest_batch':0}
        self.node_abs_bound=[0.0]*self.T
        self.residual_abs_bound=[0.0]*self.T
    def _visit(self,t:int,x:I,y:I,delta:I,a:I,b:I)->I:
        n=len(a.lo);self.counts['pair_nodes']+=n;self.counts['largest_batch']=max(self.counts['largest_batch'],n)
        stage_residual=state_difference(x,y,delta)+action_difference(a,b,self.p)
        self.residual_abs_bound[t]=max(self.residual_abs_bound[t],float(np.max(np.maximum(abs(stage_residual.lo),abs(stage_residual.hi)),initial=0)))
        if t==self.T-1:
            self.counts['analytic_terminal_pairs']+=n
            out=last_pair(x,y,delta,a,b,self.p)
        else:
            stage=stage_residual
            dd=next_difference(x,y,delta,a,b)
            xx=o.deterministic_next(x,a);yy=o.deterministic_next(y,b)
            # Stream each innovation child; memory does not grow as q^T.
            total=zero(n)
            for j in range(self.q):
                z=I.point(np.full(n,-1/32+j/(16*self.q)))
                z=I(z.lo,z.hi+1/(16*self.q))
                zz=s.stack([z,-z]);xa=xx+zz;yb=yy+zz
                aa=self.actors[t+1].action(xa);bb=self.actors[t+1].action(yb)
                total=total+self._visit(t+1,xa,yb,dd,aa,bb)
                self.counts['coupling_bins']+=n
            out=stage+float(BETA)*(total/self.q)
        self.node_abs_bound[t]=max(self.node_abs_bound[t],float(np.max(np.maximum(abs(out.lo),abs(out.hi)),initial=0)))
        return out
    def contrast(self,t:int,x:I,a:I,b:I)->I:
        n=len(a.lo);self.counts['initial_pairs']+=n
        same=(a.lo==a.hi)&(b.lo==b.hi)&(a.lo==b.lo)
        self.counts['initial_identity_pairs']+=int(same.sum())
        out=zero(n);idx=np.flatnonzero(~same)
        if len(idx):
            xx=I(x.lo[idx],x.hi[idx]);aa=I(a.lo[idx],a.hi[idx]);bb=I(b.lo[idx],b.hi[idx])
            v=self._visit(t,xx,xx,I.point(np.zeros_like(xx.lo)),aa,bb)
            out.lo[idx]=v.lo;out.hi[idx]=v.hi
        return out
    def work(self):
        return dict(self.counts,actor_queries=sum(a.queries for a in self.actors),
                    ambiguous_actor_boxes=sum(a.ambiguous for a in self.actors),
                    rectangle_table_bytes=sum(a.bytes for a in self.actors),
                    node_absolute_bounds=self.node_abs_bound,stage_residual_absolute_bounds=self.residual_abs_bound)


def policy_digest(a:np.ndarray)->str:
    return hashlib.sha256(np.asarray(a,dtype='<u2').tobytes()).hexdigest()


def sweep(policies:np.ndarray,bits:int=5,q:int=16,p:int=1)->tuple[np.ndarray,dict,dict]:
    n=1<<bits;T=len(policies)
    bins=np.stack(np.meshgrid(np.arange(n),np.arange(n),indexing='ij'),axis=-1).reshape(-1,2)
    x=I(bins/n,(bins+1)/n)
    caplo=(4096*(2*n+bins.sum(axis=1)))//(16*n)
    caphi=(2*n+bins.sum(axis=1)+2)/(16*n)  # exact dyadic, only for lower covers
    engine=PairCertificate(policies,bits,q,p);new=policies.copy();reports=[];records={}
    for t in range(T):
        before=engine.work();start=time.perf_counter();base=policies[t].reshape(-1).astype(float)/4096
        ub=np.zeros(n*n);selected=policies[t].reshape(-1).copy()
        cl=[];cu=[];qindices=[];rmax=0.;abs_gate=0;scalar_gate=0
        for j in range(9):
            ai=(caplo*j)//8;a=I.point(ai/4096);b=I.point(base)
            val=engine.contrast(t,x,a,b)
            # h=0 is a verification gauge, not a policy generator. Residual
            # r=c^pi and D=pair cost difference are nonconstant and non-null.
            immediate=action_difference(a,b,p)
            err=(val-immediate)/float(BETA)
            rr=np.maximum(abs(err.lo),abs(err.hi));rmax=max(rmax,float(rr.max()))
            absu=(immediate+float(BETA)*I.point(rr)).hi
            remaining=T-t
            stage_bound=F(99+4*p,64)
            terminal_bound=F(37,16)
            w=sum((BETA**k*stage_bound for k in range(remaining-1)),F(0))+BETA**(remaining-1)*terminal_bound
            scalaru=(immediate+float(BETA)*s.c.rat_i(w)).hi
            different=ai!=policies[t].reshape(-1)
            abs_gate+=int(np.count_nonzero(different&(absu<=0)))
            scalar_gate+=int(np.count_nonzero(different&(scalaru<=0)))
            take=val.hi<ub  # incumbent wins ties; all deployed changes strict
            selected[take]=ai[take];ub[take]=val.hi[take]
            cl.append(val.lo);cu.append(val.hi);qindices.append(ai)
        low=np.zeros(n*n);ll=[];lu=[]
        for j in range(8):
            aa=I(caphi*j/8,caphi*(j+1)/8)
            val=engine.contrast(t,x,aa,I.point(base));low=np.minimum(low,val.lo)
            ll.append(val.lo);lu.append(val.hi)
            err=(val-action_difference(aa,I.point(base),p))/float(BETA)
            rmax=max(rmax,float(np.max(np.maximum(abs(err.lo),abs(err.hi)))))
        eps=I.point(ub)-I.point(low)
        new[t]=selected.reshape(n,n)
        changed=selected!=policies[t].reshape(-1)
        
        if not (np.all(selected<=caplo) and np.all(ub<=0) and np.all(low<=ub)):
            raise AssertionError(dict(date=t,feasible=bool(np.all(selected<=caplo)),safe=bool(np.all(ub<=0)),ordered=bool(np.all(low<=ub)),bad=np.flatnonzero(low>ub).tolist(),lower=low.tolist(),upper=ub.tolist()))
        records.update({f't{t}_candidate_lo':np.array(cl),f't{t}_candidate_hi':np.array(cu),
                        f't{t}_candidate_indices':np.array(qindices),f't{t}_cover_lo':np.array(ll),
                        f't{t}_cover_hi':np.array(lu),f't{t}_selected':selected,
                        f't{t}_accepted_upper':ub,f't{t}_continuous_inf_lower':low,
                        f't{t}_greedy_gap_upper':eps.hi})
        reports.append(dict(date=t,changed_cells=int(changed.sum()),retained_cells=int((~changed).sum()),
            strict_candidate_comparisons=int(sum(np.count_nonzero((np.array(qindices)[j]!=policies[t].reshape(-1))&(np.array(cu)[j]<0)) for j in range(9))),
            blocked_candidate_comparisons=int(sum(np.count_nonzero((np.array(qindices)[j]!=policies[t].reshape(-1))&(np.array(cu)[j]>=0)) for j in range(9))),
            absolute_contrast_candidate_acceptances=abs_gate,scalar_width_candidate_acceptances=scalar_gate,
            anchored_action_contrast_upper=rmax,uniform_action_contrast_upper=min(s.c.enclosure(w)[1],float(np.nextafter(2*rmax,np.inf))),greedy_gap_upper=float(eps.hi.max()),
            largest_accepted_upper=float(ub[changed].max()) if changed.any() else None,
            seconds=time.perf_counter()-start,work_before=before,work_after=engine.work()))
    return new,dict(dates=reports,work=engine.work(),before_sha256=policy_digest(policies),after_sha256=policy_digest(new)),records
