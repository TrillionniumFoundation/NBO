"""Independent witness arithmetic on canonical arrays; no R11 Bellman routines."""
from __future__ import annotations
import numpy as np
from canonical import core
SIGNS=('positive','nonpositive')
EPS=1e-7
TOL=2e-10

def close(a,b,label):
    a=np.asarray(a);b=np.asarray(b)
    if a.shape!=b.shape or not np.isfinite(a).all() or not np.isfinite(b).all():raise ValueError('invalid '+label)
    gap=float(np.max(np.abs(a-b))) if a.size else 0.
    if gap>TOL:raise ValueError(f'{label} mismatch: {gap}')
    return gap

def restrict(co,a,b):
    """Independent de Casteljau restriction, not the generator's implementation."""
    def split(x,t):
        x=np.array(x,dtype=float,copy=True);left=[x[0]];right=[x[-1]]
        for _ in range(len(x)-1):
            x=(1-t)*x[:-1]+t*x[1:];left.append(x[0]);right.append(x[-1])
        return np.asarray(left),np.asarray(right[::-1])
    if not 0<=a<=b<=1:raise ValueError('invalid Bernstein cell')
    x=split(co,a)[1] if a else np.asarray(co)
    return split(x,(b-a)/(1-a))[0] if a<1 else np.full_like(x,x[-1])

class Engine:
    def __init__(self,b,j):
        self.b=b;self.fm=j.fm;self.box=j.box;self.N=b.steps;self.S=b.ns
        self.A=len(b.e[0].menu)+len(b.e[0].extra[0].actions[0]);self.stop=self.A
        self.ix=np.arange(self.S);self.cache={}
    def controls(self,n):return np.concatenate((np.broadcast_to(self.b.e[0].menu,(self.S,len(self.b.e[0].menu),3)),self.b.e[0].extra[n].actions),axis=1)
    def mask(self,n,adj,m,up=False):
        theta=self.controls(n)[:,:,1]
        good=np.ones(theta.shape,bool) if adj else np.abs(theta)<1e-14
        if up:good &= theta>=-1e-14
        return np.column_stack((good,(~self.b.e[0].boundary)&(n>=m)))
    def first_mask(self,adj,s,L,S,up=False):
        a=self.fm.actions
        mask=(a[:,2]>=(-S if s=='nonpositive' else 0)-1e-13)&(a[:,2]<=(0 if s=='nonpositive' else L)+1e-13)
        if not adj:mask &= abs(a[:,1])<1e-14
        if up:mask &= a[:,1]>=-1e-14
        return mask
    def q(self,k,n,v,d,F,continuation=False):
        vals=[]
        for z in (self.b.e[k].common,self.b.e[k].extra[n]):
            val=(z.matrix@v).reshape(self.S,z.na)
            if not continuation:val=val+z.base+d*z.duration-self.b.spec.cost*z.effort
            vals.append(val)
        vals.append(np.zeros((self.S,1)) if continuation else (self.b.terminal-F)[:,None])
        return np.concatenate(vals,axis=1)
    def fq(self,k,v,d,continuation=False):
        val=self.fm.rows[k]@v
        return val if continuation else val+self.fm.reward[k]+d*self.fm.duration[k]
    def first(self,q,adj,L,S):
        out={}
        for s in SIGNS:
            ids=np.where(self.first_mask(adj,s,L,S))[0];i=ids[np.argmax(q[ids])]
            edge=L if s=='positive' else -S
            for pair in self.fm.pairs:
                if not adj and abs(pair[1])>1e-14:continue
                rows=np.all(self.fm.actions[:,:2]==pair,axis=1)
                if not np.any(rows&(self.fm.actions[:,2]==edge)):
                    raise ValueError('independent finite-knot checker needs the stated cap knot')
            out[s]=(float(q[i]),int(i))
        return out
    def solve(self,lam,d,F,adj,m,L=.8,S=.5):
        if not (0<=lam<=1 and -2<=d<=2 and 0<=F<=2 and 1<=m<=8):raise ValueError('parameters outside verified arithmetic domain')
        key=(lam,d,0. if m==8 else F,adj,m,L,S)
        if key in self.cache:return self.cache[key]
        v=np.empty((self.N+1,self.S));v[-1]=self.b.terminal
        p=np.zeros((self.N,self.S),dtype=np.int32)
        for n in range(self.N-1,0,-1):
            q=(1-lam)*self.q(0,n,v[n+1],d,F)+lam*self.q(1,n,v[n+1],d,F)
            q=np.where(self.mask(n,adj,m),q,-np.inf);p[n]=q.argmax(1);v[n]=q[self.ix,p[n]]
        v[0]=0.
        fq=(1-lam)*self.fq(0,v[1],d)+lam*self.fq(1,v[1],d)
        ans=(v,p,self.first(fq,adj,L,S));self.cache[key]=ans
        return ans
    def selected(self,k,n,p,v,d,F):
        if p.dtype.kind not in 'iu' or np.any(p<0) or np.any(p>self.stop):raise ValueError('invalid policy index')
        value=self.b.terminal-F
        value=value.copy();e=self.b.e[k];nm=len(e.menu)
        for z,offset,used in ((e.common,0,p<nm),(e.extra[n],nm,(p>=nm)&(p<self.stop))):
            ids=np.flatnonzero(used)
            if not len(ids):continue
            aa=p[ids]-offset;rows=ids*z.na+aa
            value[ids]=z.base[ids,aa]+d*z.duration[ids,aa]-self.b.spec.cost*z.effort[ids,aa]+z.matrix[rows]@v
        return value
    def first_index(self,action,adj,s,L,S):
        hits=np.flatnonzero(np.all(np.abs(self.fm.actions-action)<1e-14,axis=1))
        if len(hits)!=1:raise ValueError('first action is not a unique canonical knot')
        i=int(hits[0])
        if not self.first_mask(adj,s,L,S)[i] or (s=='positive' and action[2]<=0):raise ValueError('infeasible lower first action')
        return i
    def coefficients(self,p,action,adj,m,s,d,F,L,S):
        if p.shape!=(self.N,self.S):raise ValueError('policy shape')
        for n in range(1,self.N):
            if np.any(p[n]<0) or np.any(p[n]>self.stop) or not np.all(self.mask(n,adj,m)[self.ix,p[n]]):
                raise ValueError('infeasible lower continuation policy')
        first=self.first_index(action,adj,s,L,S)
        prev=self.b.terminal[None,:]
        for n in range(self.N-1,0,-1):
            h=self.N-n;out=[]
            for i in range(h+1):
                val=np.zeros(self.S)
                if i<h:val+=(1-i/h)*self.selected(0,n,p[n],prev[i],d,F)
                if i:val+=i/h*self.selected(1,n,p[n],prev[i-1],d,F)
                out.append(val)
            prev=np.stack(out)
        out=[]
        for i in range(self.N+1):
            val=0.
            if i<self.N:val+=(1-i/self.N)*self.fq(0,prev[i],d)[first]
            if i:val+=i/self.N*self.fq(1,prev[i-1],d)[first]
            out.append(val)
        return np.asarray(out)
    def upper(self,a,b,d,F,adj,m,L,S,method):
        va,_,fa=self.solve(a,d,F,adj,m,L,S);vb,_,fb=self.solve(b,d,F,adj,m,L,S)
        h=self.N;ii=np.arange(h+1)
        out={s:(1-ii/h)*fa[s][0]+ii/h*fb[s][0] for s in SIGNS}
        if method=='chord':
            major=np.zeros(self.S)
            for n in range(self.N-2,0,-1):
                dv=vb[n+1]-va[n+1]
                signed=(b-a)*(self.q(0,n,dv,0,0,True)-self.q(1,n,dv,0,0,True))
                k0=self.q(0,n,major,0,0,True);k1=self.q(1,n,major,0,0,True)
                signed+=np.maximum((1-a)*k0+a*k1,(1-b)*k0+b*k1)
                major=np.maximum(0,np.where(self.mask(n,adj,m),signed,-np.inf).max(1))
            dv=vb[1]-va[1]
            signed=(b-a)*(self.fq(0,dv,0,True)-self.fq(1,dv,0,True))
            k0=self.fq(0,major,0,True);k1=self.fq(1,major,0,True)
            signed+=np.maximum((1-a)*k0+a*k1,(1-b)*k0+b*k1)
            for s in SIGNS:out[s]+=ii*(h-ii)/(h*(h-1))*max(0,float(signed[self.first_mask(adj,s,L,S)].max()))
        elif method=='count':
            prev=self.b.terminal[None,:]
            for n in range(self.N-1,0,-1):
                h=self.N-n;cur=np.empty((h+1,self.S));cur[0]=va[n];cur[-1]=vb[n]
                for i in range(1,h):
                    qa=(1-a)*self.q(0,n,prev[i],d,F)+a*self.q(1,n,prev[i],d,F)
                    qb=(1-b)*self.q(0,n,prev[i-1],d,F)+b*self.q(1,n,prev[i-1],d,F)
                    cur[i]=np.where(self.mask(n,adj,m),(1-i/h)*qa+(i/h)*qb,-np.inf).max(1)
                prev=cur
            h=self.N
            for i in range(1,h):
                qa=(1-a)*self.fq(0,prev[i],d)+a*self.fq(1,prev[i],d)
                qb=(1-b)*self.fq(0,prev[i-1],d)+b*self.fq(1,prev[i-1],d)
                q=(1-i/h)*qa+i/h*qb
                for s in SIGNS:out[s][i]=q[self.first_mask(adj,s,L,S)].max()
        else:raise ValueError('unknown upper method')
        return out
