"""R8 sparse execution of the explicitly specified finite rebalancing economy.

The R4 transition formula and the union of BOTH historical meshes are immutable
inputs.  Sparse storage changes arithmetic order, not controls or probabilities.
All time intervals have length 1/8; wealth perturbations never alter that calendar.
"""
from __future__ import annotations
import os
for _key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_key] = '1'
import sys, time, json, hashlib, platform, resource
from pathlib import Path
from dataclasses import dataclass
import numpy as np
from scipy.sparse import csr_matrix, vstack
ROOT = Path(__file__).resolve().parents[2]
import numerical_core as r7
old = r7.c.old
OUT = ROOT/'replication/r8/output'
OUT.mkdir(parents=True, exist_ok=True)

def save(name, value):
    (OUT/name).write_text(json.dumps(r7.serial(value), indent=2, allow_nan=False)+'\n')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

@dataclass(frozen=True)
class Specification:
    nx: int = 49
    nu: int = 33
    steps: int = 8
    include_proposals: bool = True
    correlation_low: float = -.25
    correlation_high: float = .25
    cardinal_tilt: float = 0.
    settlement_scale: float = 1.
    normalization_scale: float = 1.
    cost: float = 2.

class SparseKernel:
    def __init__(self, states, actions, shape, h, model, spec):
        self.ns = len(states)
        self.na = actions.shape[-2]
        self.actions = np.broadcast_to(actions, (self.ns, self.na, 3))
        self.base = np.empty((self.ns, self.na))
        self.duration = np.empty_like(self.base)
        self.effort = np.empty_like(self.base)
        self.settlement = np.empty_like(self.base)
        self.exit_discount = np.empty_like(self.base)
        self.shape = tuple(shape)
        self.model, self.h, self.states = model, h, states
        size = np.array(shape)-1
        parts=[]; max_replay=0.; max_mass=0.; min_weight=0.
        for first in range(0, self.ns, 48):
            last = min(first+48,self.ns); sl=slice(first,last)
            ss=states[sl,None,:]; aa=self.actions[sl]
            y,live,disc,flow,effort,_,alpha=old.transition(ss,aa,h,model)
            ann=-np.expm1(-model.rho*h*alpha)/model.rho
            settlement=(disc*(~live)*old.terminal(y)).mean(-1)
            base=(flow+model.k*effort+disc*(~live)*old.terminal(y)).mean(-1)
            self.duration[sl]=ann.mean(-1)
            self.effort[sl]=effort.mean(-1)
            self.settlement[sl]=settlement
            self.exit_discount[sl]=(disc*(~live)).mean(-1)
            self.base[sl]=(base+(spec.settlement_scale-1)*settlement
                +spec.cardinal_tilt*(ss[...,0]-2)*self.duration[sl]
                +(spec.normalization_scale-1)/(1-ss[...,0])*self.duration[sl])
            z=(y-old.LO)/(old.HI-old.LO)*size
            ij=np.minimum(np.maximum(np.floor(z).astype(int),0),size-1)
            frac=z-ij; p,q=frac[...,0],frac[...,1]
            ind=np.empty((last-first,self.na,16),dtype=np.int32)
            wt=np.empty(ind.shape)
            for corner,(di,dj,w) in enumerate(((0,0,(1-p)*(1-q)),(1,0,p*(1-q)),(0,1,(1-p)*q),(1,1,p*q))):
                ind[:,:,corner::4]=(ij[...,0]+di)*shape[1]+ij[...,1]+dj
                wt[:,:,corner::4]=disc*live*w/4
            min_weight=min(min_weight,float(wt.min()));max_mass=max(max_mass,float(wt.sum(-1).max()))
            probe=np.sin(np.arange(self.ns))
            expected=(wt*probe[ind]).sum(-1)
            matrix=csr_matrix((wt.ravel(),ind.ravel(),np.arange(0,wt.size+1,16,dtype=np.int64)),shape=((last-first)*self.na,self.ns))
            matrix.sum_duplicates();matrix.eliminate_zeros();matrix.sort_indices()
            max_replay=max(max_replay,float(np.max(abs((matrix@probe).reshape(last-first,self.na)-expected))))
            parts.append(matrix)
        # Keep large kernels blockwise to avoid a second full CSR allocation.
        # This changes storage only; every block passed the direct-gather check.
        self.parts=parts if spec.nx>=145 else None
        self.matrix=None if self.parts is not None else vstack(parts,format='csr')
        if self.parts is None: del parts
        assert min_weight>=0 and max_mass<=np.exp(-model.rho*h)+1e-12
        assert max_replay<2e-12
        self.check=dict(sparse_vs_gather=max_replay,min_weight=min_weight,max_row_mass=max_mass)
    def continuation(self,value):
        return (self.matrix@value).reshape(self.ns,self.na) if self.parts is None else np.concatenate([m@value for m in self.parts]).reshape(self.ns,self.na)
    def selected(self,policy,value):
        if self.parts is None:
            row=np.arange(self.ns)*self.na+policy
            return self.matrix[row]@value
        out=np.empty(self.ns);first=0
        for matrix in self.parts:
            n=matrix.shape[0]//self.na
            rows=np.arange(n)*self.na+policy[first:first+n]
            out[first:first+n]=matrix[rows]@value;first+=n
        return out
    @property
    def nbytes(self):
        arrays=[self.matrix] if self.parts is None else self.parts
        return int(sum(a.data.nbytes+a.indices.nbytes+a.indptr.nbytes for a in arrays)+sum(getattr(self,k).nbytes for k in ('base','duration','effort','settlement','exit_discount')))

class Economy:
    def __init__(self,spec,correlation):
        self.spec=spec;self.shape=(spec.nu,spec.nx);self.steps=spec.steps;self.k=spec.cost
        self.model=old.Model(correlation=correlation,k=spec.cost)
        ss,bd=old.grid(*self.shape);self.states=ss.reshape(-1,2);self.boundary=bd.ravel();self.ns=len(self.states)
        self.menu=np.unique(np.concatenate((old.action_mesh((9,9,13)),old.action_mesh((7,7,11)))),axis=0)
        assert len(self.menu)==1565
        self.common=SparseKernel(self.states,self.menu,self.shape,1/self.steps,self.model,spec)
        self.extra=[]
        if spec.include_proposals:
            if spec.nu!=33 or spec.steps!=8:
                raise ValueError('The declared proposal extension preserves preference nodes and the eight-date calendar')
            proposals=[]
            xold=np.linspace(.5,2,49);xnew=np.linspace(.5,2,spec.nx)
            for seed in (101,202,303):
                original=np.load(ROOT/f'replication/r4/output/safe_policy_{seed}.npz')['policies'].reshape(8,33,49,3)
                extended=np.empty((8,33,spec.nx,3))
                for n in range(8):
                    for i in range(33):
                        for j in range(3):
                            extended[n,i,:,j]=np.interp(xnew,xold,original[n,i,:,j])
                if spec.nx==49: assert np.array_equal(extended,original)
                proposals.append(extended.reshape(8,self.ns,3))
            for n in range(self.steps):
                self.extra.append(SparseKernel(self.states,np.stack([p[n] for p in proposals],1),self.shape,1/self.steps,self.model,spec))
    def controls(self,policy):
        out=self.menu[np.minimum(policy,len(self.menu)-1)].copy()
        for n in range(self.steps):
            use=policy[n]>=len(self.menu)
            if self.extra and np.any(use):
                out[n,use]=self.extra[n].actions[np.where(use)[0],policy[n,use]-len(self.menu)]
        return out

class Model(r7.Mixture):
    def __init__(self,spec=Specification()):
        t=time.perf_counter();self.spec=spec
        self.e=tuple(Economy(spec,r) for r in (spec.correlation_low,spec.correlation_high))
        self.steps=spec.steps;self.ns=self.e[0].ns
        self.terminal=spec.settlement_scale*old.terminal(self.e[0].states)
        self.backend_checks=[k.check for e in self.e for k in [e.common]+e.extra]
        self.build_seconds=time.perf_counter()-t
        self.center=int(np.linalg.norm(self.e[0].states-[2,1.25],axis=1).argmin())
        assert np.max(abs(self.e[0].states[self.center]-[2,1.25]))<1e-12
    def q(self,k,n,v,d,cost=None):
        return super().q(k,n,v,d,cost=self.spec.cost if cost is None else cost)
    def selected(self,k,n,pol,v,d,cost=None):
        return super().selected(k,n,pol,v,d,cost=self.spec.cost if cost is None else cost)
    @property
    def nbytes(self):
        return sum(k.nbytes for e in self.e for k in [e.common]+e.extra)
    def direct(self,policy,t,d):
        """Independent selected-control formula; does not use stored CSR rewards."""
        values=np.empty((self.steps+1,self.ns));values[-1]=self.terminal
        actions=self.e[0].controls(policy);s=self.e[0].states
        for n in range(self.steps-1,-1,-1):
            out=np.zeros(self.ns)
            for prob,e in zip((1-t,t),self.e):
                y,live,disc,flow,cost,_,alpha=old.transition(s,actions[n],1/self.steps,e.model)
                ann=-np.expm1(-e.model.rho*alpha/self.steps)/e.model.rho
                tilt=self.spec.cardinal_tilt*(s[:,0]-2)+(self.spec.normalization_scale-1)/(1-s[:,0])
                terminal=self.spec.settlement_scale*old.terminal(y)
                out+=prob*np.mean(flow+ann*(d+tilt[:,None])+disc*np.where(live,old.interpolate(values[n+1].reshape(e.shape),y),terminal),axis=-1)
            values[n]=out
        return values
    def features(self,policy,t):
        """Exact optimized-policy moments, not a causal decomposition.
        order: consumption exposure, cardinal baseline, tilt exposure, duration,
               quadratic effort, liquidation payoff.
        """
        F=np.zeros((6,self.steps+1,self.ns));F[5,-1]=old.terminal(self.e[0].states)
        s=self.e[0].states;actions=self.e[0].controls(policy);rows=np.arange(self.ns)
        for n in range(self.steps-1,-1,-1):
            for prob,e in zip((1-t,t),self.e):
                cp=np.minimum(policy[n],len(e.menu)-1)
                kernels=[(e.common,cp,policy[n]<len(e.menu))]
                if e.extra: kernels.append((e.extra[n],np.maximum(policy[n]-len(e.menu),0),policy[n]>=len(e.menu)))
                for kernel,act,use in kernels:
                    if not np.any(use):continue
                    duration=kernel.duration[rows,act];u=s[:,0];c=actions[n,:,0]
                    rewards=np.stack(((c**(1-u)-1)/(1-u)*duration,duration/(1-u),(u-2)*duration,duration,kernel.effort[rows,act],kernel.settlement[rows,act]))
                    for j in range(6):
                        cur=rewards[j]+kernel.selected(act,F[j,n+1])
                        F[j,n,use]+=prob*cur[use]
        return F
    def class_pair(self,t,d,adjust=True,mesh_only=False):
        """First risky action applies for 1/8 year; later positions unrestricted."""
        v=np.empty((self.steps+1,self.ns));v[-1]=self.terminal
        p=np.empty((self.steps,self.ns),np.int32)
        for n in range(self.steps-1,-1,-1):
            q=(1-t)*self.q(0,n,v[n+1],d)+t*self.q(1,n,v[n+1],d)
            allowed=r7.mask(self,n,adjust)
            if mesh_only:
                if np.isscalar(allowed):allowed=np.ones(q.shape,bool)
                else:allowed=allowed.copy()
                allowed[:,len(self.e[0].menu):]=False
            q=np.where(allowed,q,-np.inf)
            p[n]=q.argmax(1);v[n]=q[np.arange(self.ns),p[n]]
        out={}
        for sign in ('positive','nonpositive'):
            pp=p.copy();vv=v.copy();qq=np.where(r7.mask(self,0,adjust,sign),q,-np.inf)
            pp[0]=qq.argmax(1);vv[0]=qq[np.arange(self.ns),pp[0]]
            out[sign]=dict(value=vv,policy=pp)
        return out

def constrained_chord(mix,a,b,va,vb,adjust,sign):
    zero=np.zeros(mix.ns);M=[zero]*(mix.steps+1)
    for n in range(mix.steps-2,-1,-1):
        diff=vb[n+1]-va[n+1]
        D=(b-a)*(r7.continuation(mix,0,n,diff)-r7.continuation(mix,1,n,diff))
        if n<mix.steps-2:
            k0=r7.continuation(mix,0,n,M[n+1]);k1=r7.continuation(mix,1,n,M[n+1])
            D+=np.maximum((1-a)*k0+a*k1,(1-b)*k0+b*k1)
        M[n]=np.maximum(np.where(r7.mask(mix,n,adjust,sign),D,-np.inf).max(1),0)
    return r7.CompactUpper(mix,va,vb,M)

if __name__=='__main__':
    mix=Model();results=[]
    for adj in (True,False):
        z=mix.class_pair(.25,.45,adj)
        for sign,item in z.items():
            direct=mix.direct(item['policy'],.25,.45)
            F=mix.features(item['policy'],.25)
            reconstructed=F[0]+F[1]+.45*F[3]-2*F[4]+F[5]
            print('DIRECT',adj,sign,np.max(abs(direct-item['value'])),np.unravel_index(np.argmax(abs(direct-item['value'])),direct.shape),direct[0,mix.center],item['value'][0,mix.center],flush=True)
            assert np.max(abs(direct-item['value']))<2e-11
            assert np.max(abs(reconstructed-item['value']))<2e-11
            results.append(dict(adjust=adj,sign=sign,value=float(item['value'][0,mix.center]),direct_error=float(np.max(abs(direct-item['value']))),features=F[:,0,mix.center]))
    result=dict(rows=results,build_seconds=mix.build_seconds,kernel_bytes=mix.nbytes,maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,backend_checks=mix.backend_checks)
    save('model_validation.json',result);print(json.dumps(r7.serial(result),indent=2))
