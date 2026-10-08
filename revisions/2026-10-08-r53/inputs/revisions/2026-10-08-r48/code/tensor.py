"""Exact witness-preserving continuous tensor compilation.

The nodal L1 transform is classical (Felzenszwalb and Huttenlocher, 2012).
Every stored owner is an ORIGINAL label/action index, with lexicographic ties.
"""
from __future__ import annotations
import itertools, math
from common import *

class Model:
    def __init__(self,axes,labels,kind,L=None):
        self.axes=[np.asarray(a,dtype=float) for a in axes];self.d=len(axes)
        if not 1<=self.d<=4:raise ValueError('Implemented dimensions: 1--4')
        for a in self.axes:
            if len(a)<2 or a[0]!=0 or a[-1]!=1 or np.any(np.diff(a)<=0):raise ValueError('Invalid axis')
        self.shape=tuple(map(len,self.axes));self.S=math.prod(self.shape)
        self.nodes=np.array(list(itertools.product(*self.axes)))
        self.v=np.asarray(labels,dtype=float).reshape(-1)
        if len(self.v)!=self.S or not np.isfinite(self.v).all():raise ValueError('Incomplete labels')
        self.kind=kind;self.bits=0
        self.counts={'point_values':0,'corner_terms':0,'multilinear_cells':0,'transform_relaxations':0,'exact_selector_fallbacks':0}
        if kind=='witness':
            self.L=F(L)
            if self.L<0:raise ValueError('Negative slope')
            self._transform()
        elif kind=='fvi':
            v=self.v.reshape(self.shape);L=F(0)
            for j,ax in enumerate(self.axes):
                for k in range(len(ax)-1):
                    a=np.take(v,k,axis=j).ravel();b=np.take(v,k+1,axis=j).ravel()
                    gap=F(float(ax[k+1]))-F(float(ax[k]))
                    L=max(L,max(abs(F(float(y))-F(float(x)))/gap for x,y in zip(a,b)))
            self.L=L;self.z=None;self.owners=None
            self.bits=max(max(q.numerator.bit_length(),q.denominator.bit_length()) for q in [L]+list(map(lambda v:F(float(v)),self.v)))
        else:raise ValueError('Unknown representation')
        self.h=sum((max(F(float(b))-F(float(a)) for a,b in zip(ax,ax[1:]))/2 for ax in self.axes),F(0))
    def _transform(self):
        z=[F(float(v)) for v in self.v];owners=list(range(self.S))
        strides=[math.prod(self.shape[j+1:]) for j in range(self.d)]
        for j,axis in enumerate(self.axes):
            stride=strides[j];other=[range(n) if k!=j else (0,) for k,n in enumerate(self.shape)]
            for index in itertools.product(*other):
                root=sum(i*s for i,s in zip(index,strides));ids=[root+k*stride for k in range(len(axis))]
                for seq in (range(1,len(ids)),range(len(ids)-2,-1,-1)):
                    forward=isinstance(seq,range) and seq.step==1
                    for k in seq:
                        prev=k-1 if forward else k+1;u,v=ids[k],ids[prev]
                        cost=z[v]+self.L*abs(F(float(axis[k]))-F(float(axis[prev])))
                        self.counts['transform_relaxations']+=1
                        if (cost,owners[v])<(z[u],owners[u]):z[u]=cost;owners[u]=owners[v]
        self.z=z;self.owners=np.array(owners,dtype=np.int64);self.zi=c.array_i(z)
        self.bits=max(max(q.numerator.bit_length(),q.denominator.bit_length()) for q in z+[self.L])
    def cells(self,x):
        x=np.asarray(x,dtype=float).reshape(-1,self.d)
        if np.any(x<0) or np.any(x>1) or not np.isfinite(x).all():raise ValueError('State outside cube')
        return np.stack([np.clip(np.searchsorted(ax,x[:,j],side='right')-1,0,len(ax)-2) for j,ax in enumerate(self.axes)],axis=-1)
    def corner_ids(self,ij):
        return np.stack([np.ravel_multi_index(tuple((ij+offset).T),self.shape) for offset in itertools.product((0,1),repeat=self.d)],axis=1)
    def point(self,x):
        x=np.asarray(x,dtype=float).reshape(-1,self.d);ij=self.cells(x);ids=self.corner_ids(ij)
        self.counts['point_values']+=len(x)
        if self.kind=='witness':
            self.counts['corner_terms']+=int(ids.size)
            dist=isum(abs_i(I.point(x[:,None,:])-I.point(self.nodes[ids])))
            q=I(self.zi.lo[ids],self.zi.hi[ids])+c.rat_i(self.L)*dist
            return I(np.min(q.lo,axis=1),np.min(q.hi,axis=1))
        self.counts['multilinear_cells']+=len(x)
        v=I.point(self.v[ids].reshape((len(x),)+(2,)*self.d))
        for j in range(self.d-1,-1,-1):
            left=self.axes[j][ij[:,j]]
            right=self.axes[j][ij[:,j]+1]
            t=(I.point(x[:,j])-I.point(left))/(I.point(right)-I.point(left))
            shape=(len(x),)+(1,)*j;t=I(t.lo.reshape(shape),t.hi.reshape(shape))
            a=I(v.lo[...,0],v.hi[...,0]);b=I(v.lo[...,1],v.hi[...,1]);v=a+t*(b-a)
        return v
    def evaluate(self,x):
        center=np.clip(x.midpoint(),0,1);v=self.point(center)
        r=np.maximum(np.nextafter(center-x.lo,np.inf),np.nextafter(x.hi-center,np.inf))
        err=c.rat_i(self.L)*isum(I.point(r))
        return v+I(-err.hi,err.hi)
    def candidate_owners(self,x):
        return self.owners[self.corner_ids(self.cells(x))]
    def exact(self,x):
        """Dense rational reference; validation only, never a fast-path oracle."""
        x=list(map(F,x));return min((F(float(y))+self.L*sum(abs(u-F(float(v))) for u,v in zip(x,node)),i) for i,(y,node) in enumerate(zip(self.v,self.nodes)))
    def actor(self,x,actions):
        """Hull of all exact actor values attained in a state box.

        Closed intersecting cells are included. Degenerate ambiguous queries
        are resolved exactly, preserving the original lowest-index tie rule.
        """
        actions=np.asarray(actions,dtype=float);n=len(x.lo)
        ilo=self.cells(x.lo);ihi=self.cells(x.hi)
        low=np.empty(n);high=np.empty(n);amb=0
        if self.kind=='fvi':
            first=np.stack([np.searchsorted((a[:-1]+a[1:])/2,x.lo[:,j],side='left') for j,a in enumerate(self.axes)],axis=-1)
            last=np.stack([np.searchsorted((a[:-1]+a[1:])/2,x.hi[:,j],side='right') for j,a in enumerate(self.axes)],axis=-1)
            ids=np.ravel_multi_index(tuple(first.T),self.shape);low[:]=actions[ids];high[:]=actions[ids]
            bad=np.any(first!=last,axis=1)
            for k in np.flatnonzero(bad):
                # A point on a nearest-node boundary uses the smaller index.
                if np.array_equal(x.lo[k],x.hi[k]):continue
                choices=[actions[np.ravel_multi_index(ix,self.shape)] for ix in itertools.product(*[range(a,b+1) for a,b in zip(first[k],last[k])])]
                low[k],high[k]=min(choices),max(choices)
            return I(low,high),int(np.count_nonzero(low!=high))
        ids=self.candidate_owners(x.midpoint())
        qi=I.point(self.v[ids])+c.rat_i(self.L)*isum(abs_i(I(x.lo[:,None,:],x.hi[:,None,:])-I.point(self.nodes[ids])))
        poss=qi.lo<=np.min(qi.hi,axis=1)[:,None]
        low[:]=np.min(np.where(poss,actions[ids],np.inf),axis=1)
        high[:]=np.max(np.where(poss,actions[ids],-np.inf),axis=1)
        bad=np.any(ilo!=ihi,axis=1)
        exact_bad=(low!=high)&np.all(x.lo==x.hi,axis=1)
        for k in np.flatnonzero(bad|exact_bad):
            corners=list(itertools.product(*[range(a,b+2) for a,b in zip(ilo[k],ihi[k])]))
            sites=np.unique([self.owners[np.ravel_multi_index(q,self.shape)] for q in corners])
            if np.array_equal(x.lo[k],x.hi[k]):
                point=list(map(lambda v:F(float(v)),x.lo[k]))
                winner=min((F(float(self.v[i]))+self.L*sum(abs(u-F(float(v))) for u,v in zip(point,self.nodes[i])),int(i)) for i in sites)[1]
                low[k]=high[k]=actions[winner];self.counts['exact_selector_fallbacks']+=1
            else:
                box=I(x.lo[k:k+1,None,:],x.hi[k:k+1,None,:])
                q=I.point(self.v[sites])+c.rat_i(self.L)*isum(abs_i(box-I.point(self.nodes[sites])))
                possible=q.lo[0]<=np.min(q.hi);aa=actions[sites[possible]]
                low[k],high[k]=np.min(aa),np.max(aa)
        return I(low,high),int(np.count_nonzero(low!=high))
    def payload(self):
        out={'axes':[a.tolist() for a in self.axes],'labels':self.v.tolist(),'kind':self.kind,'L':str(self.L),'state_cover':str(self.h)}
        if self.kind=='witness':out.update(transformed_labels=list(map(str,self.z)),original_owners=self.owners.tolist())
        return out
    @classmethod
    def load(cls,j):
        model=cls(j['axes'],j['labels'],j['kind'],j['L'])
        if model.L!=F(j['L']):raise AssertionError('Modulus mismatch')
        if model.kind=='witness' and 'original_owners' in j:
            assert model.owners.tolist()==j['original_owners'] and list(map(str,model.z))==j['transformed_labels']
        return model
