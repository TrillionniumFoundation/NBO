"""Trained NBO critics and non-tensor acquired actors in unchanged primitives.

Single-hidden-layer ReLU expectation is integrated analytically, not by a
midpoint rule. Neural weights are actually fitted; the native witness remains
a separate generator. Verification uses outward interval arithmetic.
"""
from __future__ import annotations
import itertools, math, time
import numpy as np
from fractions import Fraction as F
import operators50 as o
s=o.s; I=o.I; BETA=o.BETA


def dot(x:I,w:np.ndarray)->I:
    w=np.asarray(w); out=I.point(np.zeros(x.lo.shape[:-1]+w.shape[1:]))
    for j in range(len(w)):
        z=s.col(x,j)
        if w.ndim==2:z=I(z.lo[...,None],z.hi[...,None])
        out=out+z*w[j]
    return out


def hinge_mean(z:I,r:F)->I:
    """Monotone endpoint evaluation avoids subtracting nearly equal squares."""
    if r==0:return o.positive(z)
    rl,rh=o.s.c.enclosure(r)
    def endpoint(v):
        out=o.positive_moment(I.point(v),r,1)
        positive=v>=rh;negative=v<=-rh;inside=(v>=-rl)&(v<=rl)
        mid=(I.point(v)+o.s.c.rat_i(r)).square()/o.s.c.rat_i(4*r)
        out.lo=np.where(inside,mid.lo,out.lo);out.hi=np.where(inside,mid.hi,out.hi)
        out.lo=np.where(positive,v,np.where(negative,0,out.lo))
        out.hi=np.where(positive,v,np.where(negative,0,out.hi))
        return out
    a=endpoint(z.lo);b=endpoint(z.hi)
    return I(a.lo,b.hi)


def gradient_cost(x:I,terminal=False)->I:
    d=x.lo.shape[-1]
    nx=I(np.roll(x.lo,-1,axis=-1),np.roll(x.hi,-1,axis=-1))
    pr=I(np.roll(x.lo,1,axis=-1),np.roll(x.hi,1,axis=-1))
    shortage=o.positive(F(1,2)-s.isum(x)*s.c.rat_i(F(2,d)))
    return (x-F(5,8))*s.c.rat_i(F(8 if terminal else 4,d))+(2*x-nx-pr)*s.c.rat_i(F(1,2*d))-I(shortage.lo[...,None],shortage.hi[...,None])*s.c.rat_i(F(8,d))


def primitive_point(x,a,z=0.,terminal=False,p=1):
    d=x.shape[-1];sh=np.maximum(0,.5-2*np.mean(x,axis=-1))
    c=(4 if terminal else 2)*np.mean((x-.625)**2,axis=-1)+np.mean((x-np.roll(x,-1,axis=-1))**2,axis=-1)/4+2*sh**2
    if terminal:return c
    return c+p*a*a+4*a**4


def next_point(x,a,z=0.):
    d=x.shape[-1];v=np.roll(x,-1,axis=-1)
    g=np.where(np.arange(d)%2==0,.5,.25);sg=np.where(np.arange(d)%2==0,1.,-1.)
    return 1/16+x/2+v/8+x*(1-v)/16+np.asarray(a)[...,None]*g+np.asarray(z)[...,None]*sg


class Critic:
    def __init__(self,kind,d,params=None,forest=None):
        self.kind=kind;self.d=d;self.params=params or {};self.forest=forest;self.work=0
    @classmethod
    def terminal(cls,d):return cls('terminal',d)
    @classmethod
    def zero(cls,d):return cls('zero',d)
    def point(self,x):
        self.work+=len(x)
        if self.kind=='zero':return np.zeros(len(x))
        if self.kind=='terminal':return primitive_point(x,0,terminal=True)
        if self.kind=='relu':
            p=self.params;return p['c']+x@p['v']+np.maximum(0,x@p['W']+p['b'])@p['u']
        if self.kind=='quadratic':
            p=self.params;return p['c']+x@p['v']+np.einsum('bi,ij,bj->b',x,p['Q'],x)
        if self.kind=='legacy':return self.forest.evaluate(I.point(x)).midpoint()
        if self.kind=='extra-trees':return self.forest.predict(x)
        raise ValueError(self.kind)
    def interval(self,x):
        self.work+=len(x.lo)
        if self.kind=='zero':return I.point(np.zeros(len(x.lo)))
        if self.kind=='terminal':return s.costs(x,I.point(np.zeros(len(x.lo))),1,True)
        if self.kind=='relu':
            p=self.params;return p['c']+dot(x,p['v'])+dot(o.positive(dot(x,p['W'])+p['b']),p['u'])
        if self.kind=='quadratic':
            p=self.params;v=p['c']+dot(x,p['v'])
            for i in range(self.d):
                for j in range(self.d):
                    term=s.col(x,i).square() if i==j else s.col(x,i)*s.col(x,j)
                    v=v+p['Q'][i,j]*term
            return v
        if self.kind=='legacy':return self.forest.evaluate(x)
        if self.kind=='extra-trees':
            lows=[];highs=[]
            for estimator in self.forest.estimators_:
                tr=estimator.tree_;lo=np.full(len(x.lo),np.inf);hi=-lo.copy()
                stack=[(0,np.arange(len(x.lo)))]
                while stack:
                    node,idx=stack.pop()
                    if not len(idx):continue
                    if tr.children_left[node]<0:
                        value=float(tr.value[node].ravel()[0]);lo[idx]=np.minimum(lo[idx],value);hi[idx]=np.maximum(hi[idx],value)
                    else:
                        j=tr.feature[node];v=tr.threshold[node]
                        stack.append((tr.children_left[node],idx[x.lo[idx,j]<=v]))
                        stack.append((tr.children_right[node],idx[x.hi[idx,j]>v]))
                lows.append(lo);highs.append(hi)
            return s.isum(I(np.stack(lows,-1),np.stack(highs,-1)))/len(lows)
        raise ValueError(self.kind)
    def expected(self,x,a,q=8):
        """Exact analytic ridge/quadratic mean, enclosed bins for tree critics."""
        if self.kind=='terminal':return o.terminal_expectation(x,a)
        if self.kind=='zero':return I.point(np.zeros(len(x.lo)))
        y=o.deterministic_next(x,a);sg=np.where(np.arange(self.d)%2==0,1.,-1.)
        if self.kind=='relu':
            p=self.params;v=p['c']+dot(y,p['v']);z=dot(y,p['W'])+p['b']
            # Each binary64 coefficient is interpreted as its exact dyadic.
            for j,u in enumerate(p['u']):
                radius=abs(sum((F(float(p['W'][i,j]))*int(sg[i]) for i in range(self.d)),F(0)))/32
                v=v+u*hinge_mean(s.col(z,j),radius)
            return v
        if self.kind=='quadratic':
            p=self.params;noise=sum((F(float(p['Q'][i,j]))*int(sg[i]*sg[j]) for i in range(self.d) for j in range(self.d)),F(0))/3072
            return self.interval(y)+s.c.rat_i(noise)
        out=I.point(np.zeros(len(x.lo)))
        for j in range(q):
            z=I.point(np.full(len(x.lo),-1/32+j/(16*q)));z=I(z.lo,z.hi+1/(16*q))
            out=out+self.interval(s.transition(x,a,z))
        return out/q
    def gradient(self,x):
        if self.kind=='zero':return I.point(np.zeros_like(x.lo))
        if self.kind=='terminal':return gradient_cost(x,True)
        p=self.params
        if self.kind=='quadratic':return dot(x,p['Q'])+dot(x,p['Q'].T)+p['v']
        if self.kind=='relu':
            z=dot(x,p['W'])+p['b'];active=I((z.lo>0).astype(float),(z.hi>=0).astype(float))
            return self.weighted_slope(active)
        raise ValueError('A discontinuous tree has no global gradient enclosure')
    def expected_gradient(self,x,a):
        y=o.deterministic_next(x,a)
        if self.kind=='terminal':
            if self.d%2:raise ValueError('Use bin enclosure for odd-dimensional shortage')
            return gradient_cost(y,True)
        if self.kind in ('zero','quadratic'):return self.gradient(y)
        p=self.params;z=dot(y,p['W'])+p['b'];terms=[];sg=[1 if i%2==0 else -1 for i in range(self.d)]
        for j in range(len(p['u'])):
            r=abs(sum((F(float(p['W'][i,j]))*sg[i] for i in range(self.d)),F(0)))/32
            zz=s.col(z,j)
            if r==0:prob=I((zz.lo>0).astype(float),(zz.hi>=0).astype(float))
            else:prob=((zz+s.c.rat_i(r))/s.c.rat_i(2*r)).clip(0,1)
            terms.append(prob)
        return self.weighted_slope(s.stack(terms))
    def weighted_slope(self,prob):
        p=self.params;columns=[]
        for i in range(self.d):
            v=I.point(np.full(len(prob.lo),p['v'][i]))
            for j in range(len(p['u'])):
                v=v+s.col(prob,j)*I.point(p['W'][i,j])*I.point(p['u'][j])
            columns.append(v)
        return s.stack(columns)
    def payload(self):
        if self.kind=='legacy':return dict(kind=self.kind,d=self.d,model=self.forest.payload())
        p={k:np.asarray(v).tolist() for k,v in self.params.items()}
        if self.kind=='extra-trees':
            p['trees']=[dict(left=e.tree_.children_left.tolist(),right=e.tree_.children_right.tolist(),feature=e.tree_.feature.tolist(),threshold=e.tree_.threshold.tolist(),value=e.tree_.value.ravel().tolist()) for e in self.forest.estimators_]
        return dict(kind=self.kind,d=self.d,params=p)


def fit(kind,x,y,seed,width=32,epochs=120):
    d=x.shape[1]
    if kind=='extra-trees':
        from sklearn.ensemble import ExtraTreesRegressor
        f=ExtraTreesRegressor(n_estimators=16,max_depth=8,min_samples_leaf=3,random_state=seed,n_jobs=1).fit(x,y)
        return Critic(kind,d,forest=f)
    if kind=='quadratic':
        pairs=list(itertools.combinations_with_replacement(range(d),2));Z=np.column_stack([np.ones(len(x)),x]+[x[:,i]*x[:,j] for i,j in pairs])
        penalty=np.eye(Z.shape[1])*1e-6;penalty[0,0]=0
        w=np.linalg.solve(Z.T@Z+penalty,Z.T@y);Q=np.zeros((d,d))
        for z,(i,j) in zip(w[d+1:],pairs):Q[i,j]=Q[j,i]=z/(1 if i==j else 2)
        p=dict(c=w[0],v=w[1:d+1],Q=Q)
    elif kind=='relu':
        rng=np.random.default_rng(seed);W=rng.normal(0,.7/(d**.5),(d,width));b=-np.full(width,.1);u=rng.normal(0,.05,width);v=np.zeros(d);c=np.mean(y)
        pars=[W,b,u,v,np.array(c)];ms=[np.zeros_like(z) for z in pars];vs=[z.copy() for z in ms]
        initial_W=W.copy()
        for step in range(1,epochs+1):
            W,b,u,v,c=pars;h=x@W+b;relu=np.maximum(0,h);err=(relu@u+x@v+c-y)*2/len(x)
            dh=err[:,None]*u*(h>0);grads=[x.T@dh,dh.sum(0),relu.T@err,x.T@err,err.sum()]
            for j,g in enumerate(grads):
                ms[j]=.9*ms[j]+.1*g;vs[j]=.999*vs[j]+.001*g*g
                pars[j]-=.01*(ms[j]/(1-.9**step))/(np.sqrt(vs[j]/(1-.999**step))+1e-8)
        W,b,u,v,c=pars
        # A final linear output fit uses learned, not fixed random, features.
        Z=np.column_stack([np.ones(len(x)),x,np.maximum(0,x@W+b)]);pen=np.eye(Z.shape[1])*1e-4;pen[0,0]=0
        w=np.linalg.solve(Z.T@Z+pen,Z.T@y);p=dict(W=W,b=b,c=w[0],v=w[1:d+1],u=w[d+1:])
        if np.array_equal(W,initial_W):raise AssertionError('Hidden layer was not fitted')
    else:raise ValueError(kind)
    p={k:np.round(np.asarray(z)*2**24)/2**24 for k,z in p.items()}
    return Critic(kind,d,p)


def train(kind,d,T,samples,seed):
    if kind in ('compiled-witness','tensor-fvi'):
        if d!=2:raise ValueError('Legacy comparison declared in d=2')
        N=8 if samples<=256 else 16
        old=s.rung(N,4,4,T,1,kind,d)
        return [Critic('legacy',d,forest=s.Model.load(m)) for m in old['models'][:-1]]+[Critic.terminal(d)],[dict(legacy_counts=old['counts'],N=N,K=4,M=4)]
    rng=np.random.default_rng(seed);critics=[None]*T+[Critic.terminal(d)];logs=[]
    for t in reversed(range(T)):
        x=rng.random((samples,d));cap=1/8+np.mean(x,axis=1)/8;actions=cap[:,None]*np.arange(17)/16
        xx=I.point(np.repeat(x,17,axis=0));aa=I.point(actions.ravel())
        v=s.costs(xx,aa,1)+float(BETA)*critics[t+1].expected(xx,aa)
        vals=v.midpoint().reshape(samples,17);labels=vals.min(axis=1)
        begin=time.perf_counter();critics[t]=fit(kind,x,labels,seed+100+t)
        err=critics[t].point(x)-labels
        logs.append(dict(date=t,samples=samples,training_seed=seed,fitting_seed=seed+100+t,training_states=x.tolist(),training_labels=labels.tolist(),bellman_actions=17*samples,fit_seconds=time.perf_counter()-begin,training_mse=float(np.mean(err**2)),fit_enclosure_width_max=float(v.width().max())))
    return critics,logs


class Partition:
    """Dyadic, locally split rectangles; never materializes a tensor grid."""
    def __init__(self,d,leaves,seed=551):
        rng=np.random.default_rng(seed);self.d=d;self.nodes=[dict(lo=np.zeros(d),hi=np.ones(d))];active=[0]
        # Geometry chosen before the generator, identical for all methods.
        while len(active)<leaves:
            scores=[np.prod(self.nodes[k]['hi']-self.nodes[k]['lo'])*(1+.25*np.sum((self.nodes[k]['lo']+self.nodes[k]['hi'])/2)) for k in active]
            k=active.pop(int(np.argmax(scores)));node=self.nodes[k];width=node['hi']-node['lo']
            candidates=np.flatnonzero(width>=width.max()-.0000001);j=int(rng.choice(candidates))
            cut=(node['lo'][j]+node['hi'][j])/2;lo=node['lo'].copy();hi=node['hi'].copy();hi[j]=cut
            left=len(self.nodes);self.nodes.append(dict(lo=lo,hi=hi));lo=node['lo'].copy();hi=node['hi'].copy();lo[j]=cut
            right=len(self.nodes);self.nodes.append(dict(lo=lo,hi=hi));node.update(axis=j,cut=cut,left=left,right=right);active.extend([left,right])
        self.active=active;self.lo=np.stack([self.nodes[k]['lo'] for k in active]);self.hi=np.stack([self.nodes[k]['hi'] for k in active]);self.box=I(self.lo,self.hi)
        for i,k in enumerate(active):self.nodes[k]['leaf']=i
        self.centers=(self.lo+self.hi)/2
        self.capindex=np.floor(s.cap(self.box).lo*4096).astype(np.int64)
        self.membership_tests=0;self.ambiguous_boxes=0;self.box_queries=0
    def locate(self,x):
        out=np.empty(len(x),dtype=int);stack=[(0,np.arange(len(x)))]
        while stack:
            k,idx=stack.pop()
            if not len(idx):continue
            node=self.nodes[k]
            if 'leaf' in node:out[idx]=node['leaf'];continue
            left=x[idx,node['axis']]<node['cut']
            stack.extend([(node['left'],idx[left]),(node['right'],idx[~left])])
        return out
    def ranges(self,x,lo,hi):
        outlo=np.empty(len(x.lo));outhi=np.empty_like(outlo);self.box_queries+=len(outlo)
        for start in range(0,len(outlo),256):
            xx=x.lo[start:start+256];yy=x.hi[start:start+256]
            hit=np.all((xx[:,None,:]<=self.hi)&(yy[:,None,:]>=self.lo),axis=2)
            if not np.all(hit.any(axis=1)):raise AssertionError('Uncovered transition box')
            self.membership_tests+=hit.size*self.d;self.ambiguous_boxes+=int(np.sum(hit.sum(axis=1)>1))
            outlo[start:start+len(xx)]=np.min(np.where(hit,lo,np.inf),axis=1);outhi[start:start+len(xx)]=np.max(np.where(hit,hi,-np.inf),axis=1)
        return I(outlo,outhi)
    def actor(self,x,indices):
        k=self.locate(x.midpoint());same=np.all((x.lo>self.lo[k])&(x.hi<self.hi[k]),axis=1)
        a=indices[k]/4096;lo=a.copy();hi=a.copy();idx=np.flatnonzero(~same)
        if len(idx):
            v=self.ranges(I(x.lo[idx],x.hi[idx]),indices/4096,indices/4096);lo[idx]=v.lo;hi[idx]=v.hi
        return I(lo,hi)
    def payload(self):return dict(lo=self.lo.tolist(),hi=self.hi.tolist(),capindex=self.capindex.tolist(),nodes=[{k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in n.items()} for n in self.nodes])


def propose(critics,partition):
    cap=partition.capindex;menu=(cap[:,None]*np.arange(17)//16)/4096;pol=[]
    for t in range(len(critics)-1):
        x=I.point(np.repeat(partition.centers,17,axis=0));a=I.point(menu.ravel())
        q=s.costs(x,a,1)+float(BETA)*critics[t+1].expected(x,a)
        k=np.argmin(q.hi.reshape(len(cap),17),axis=1);pol.append(np.rint(menu[np.arange(len(cap)),k]*4096).astype(np.uint16))
    return np.array(pol)


def residual(critic,future,part,indices,q=8):
    x=part.box;a=I.point(indices/4096);naive=s.costs(x,a,1)+float(BETA)*future.expected(x,a,q)-critic.interval(x)
    if critic.kind in ('extra-trees','legacy') or future.kind in ('extra-trees','legacy'):return naive
    center=I.point(part.centers);rc=s.costs(center,a,1)+float(BETA)*future.expected(center,a,q)-critic.interval(center)
    gy=future.expected_gradient(x,a);gx=[]
    for j in range(part.d):
        prev=(j-1)%part.d;nxt=(j+1)%part.d
        gx.append(s.col(gy,j)*(F(1,2)+(1-s.col(x,nxt))/16)+s.col(gy,prev)*(F(1,8)-s.col(x,prev)/16))
    grad=gradient_cost(x)+float(BETA)*s.stack(gx)-critic.gradient(x)
    meanvalue=rc+s.isum(grad*(x-center))
    out=I(np.maximum(naive.lo,meanvalue.lo),np.minimum(naive.hi,meanvalue.hi))
    if np.any(out.lo>out.hi):raise AssertionError('Residual enclosures disagree')
    return out


class Cache:
    def __init__(self,critics,part,policy,q=8):
        self.critics=critics;self.part=part;self.pol=policy;self.T=len(policy);self.q=q;N=len(part.lo)
        self.err=[None]*self.T+[I.point(np.zeros(N))];self.direct=[None]*self.T
        self.residuals=[];self.ranges=[None]*self.T
        for t in reversed(range(self.T)):
            a=I.point(policy[t]/4096)
            r=residual(critics[t],critics[t+1],part,policy[t],q)
            self.ranges[t]=r
            e=r if t==self.T-1 else r+float(BETA)*self.future_band(t+1,part.box,a,'err')
            base=o.final_q(part.box,a,1) if t==self.T-1 else s.costs(part.box,a,1)+float(BETA)*self.future_band(t+1,part.box,a,'direct')
            # Independent direct hull bounds may tighten the residual enclosure.
            h=critics[t].interval(part.box);frombase=base-h
            e=I(np.maximum(e.lo,frombase.lo),np.minimum(e.hi,frombase.hi));J=h+e
            base=I(np.maximum(base.lo,J.lo),np.minimum(base.hi,J.hi))
            self.err[t]=e;self.direct[t]=base;self.residuals.append(dict(date=t,width=float(r.width().max()),error_width=float(e.width().max()),direct_width=float(base.width().max())))
    def future_band(self,t,x,a,kind):
        cache=getattr(self,kind)[t];v=I.point(np.zeros(len(a.lo)))
        for j in range(self.q):
            z=I(np.full(len(a.lo),-1/32+j/(16*self.q)),np.full(len(a.lo),-1/32+(j+1)/(16*self.q)))
            nx=s.transition(x,a,z);v=v+self.part.ranges(nx,cache.lo,cache.hi)
        return v/self.q
    def advantage(self,t,x,a,b):
        if t==self.T-1:return o.final_difference(x,a,b,1)
        immediate=(a-b)*(a+b)*(1+4*(a.square()+b.square()))
        aa=self.future_band(t+1,x,a,'err');bb=self.future_band(t+1,x,b,'err')
        learned=immediate+float(BETA)*(self.critics[t+1].expected(x,a,self.q)-self.critics[t+1].expected(x,b,self.q)+aa-bb)
        direct=immediate+float(BETA)*(self.future_band(t+1,x,a,'direct')-self.future_band(t+1,x,b,'direct'))
        out=I(np.maximum(learned.lo,direct.lo),np.minimum(learned.hi,direct.hi))
        same=(a.lo==a.hi)&(b.lo==b.hi)&(a.lo==b.lo);out.lo[same]=out.hi[same]=0
        if np.any(out.lo>out.hi):raise AssertionError('Advantage enclosures disagree')
        return out
    def sweep(self,proposals=None):
        N=len(self.part.lo);new=self.pol.copy();report=[];raw={};fullcap=s.cap(self.part.box).hi
        for t in range(self.T):
            base=I.point(self.pol[t]/4096);U=np.zeros(N);chosen=self.pol[t].copy();Clo=np.zeros(N);L=np.zeros(N);lower=[];upper=[]
            menu=[self.part.capindex*j//8 for j in range(9)]
            if proposals is not None:menu.append(proposals[t])
            for ai in menu:
                val=self.advantage(t,self.part.box,I.point(ai/4096),base)
                take=val.hi<U;U[take]=val.hi[take];chosen[take]=ai[take];Clo=np.minimum(Clo,val.lo);lower.append(val.lo);upper.append(val.hi)
            covers=[]
            for j in range(8):
                val=self.advantage(t,self.part.box,I(fullcap*j/8,fullcap*(j+1)/8),base);L=np.minimum(L,val.lo);covers.append(val.lo)
            # L and candidate lower are independent lower bounds on the menu infimum.
            C=np.maximum(L,Clo);gap=I.point(U)-I.point(L);new[t]=chosen
            if np.any(U>0) or np.any(chosen>self.part.capindex) or np.any(L>U):raise AssertionError('Invalid safe selection')
            report.append(dict(date=t,changed=int(np.count_nonzero(chosen!=self.pol[t])),gap=float(gap.hi.max()),candidate_enclosure_component=float((I.point(U)-I.point(C)).hi.max()),continuous_cover_component=float((I.point(C)-I.point(L)).hi.max())))
            raw.update({f't{t}_lower':lower,f't{t}_upper':upper,f't{t}_cover':covers,f't{t}_U':U,f't{t}_L':L,f't{t}_C':C,f't{t}_selected':chosen})
        return new,report,raw


def score(policy,part,x,z):
    total=I.point(np.zeros(len(x.lo)))
    for t in range(len(policy)-1):
        a=part.actor(x,policy[t]);total=total+float(BETA**t)*s.costs(x,a,1);x=s.transition(x,a,z[t])
    a=part.actor(x,policy[-1]);return total+float(BETA**(len(policy)-1))*o.final_q(x,a,1)
