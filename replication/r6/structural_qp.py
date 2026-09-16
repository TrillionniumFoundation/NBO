#!/usr/bin/env python3
"""Matched structural reuse, following the R5 referee's explicit QP counterexample.
The quadratic form is independently assembled here, generalized to an arbitrary
finite tree horizon, and checked against the original full-tree implementation.
No query solutions, future shocks, or cross-query warm starts are supplied.
"""
from common import *
import coupled_resource as r4
import resource_ablation as r5

class TreeQP:
    def __init__(self,d,horizon=3):
        t=time.perf_counter();self.d=d;self.N=horizon
        self.A,self.shock,self.B=r4.primitives(d);self.counts=[4**n for n in range(horizon)]
        self.offsets=np.cumsum([0]+self.counts);self.nodes_count=int(self.offsets[-1]);self.m=self.nodes_count*d
        Q=np.eye(d)/d+.2*np.ones((d,d))/d**2
        self.H=np.zeros((self.m,self.m));self.F=np.zeros((self.m,d));self.f0=np.zeros(self.m)
        self.weight=np.repeat(np.concatenate([np.full(4**n,4.**(-n)) for n in range(horizon)]),d)
        states=[(np.eye(d),np.zeros((d,self.m)),np.zeros(d))];self.nodes=[]
        for n in range(horizon+1):
            prob=4.**(-n);following=[]
            for node,(M,S,b) in enumerate(states):
                self.nodes.append((prob,M,S,b))
                self.H+=2*prob*S.T@Q@S;self.F+=2*prob*S.T@Q@M;self.f0+=2*prob*S.T@Q@(b-1)
                if n<horizon:
                    j=self.offsets[n]+node;sl=slice(j*d,(j+1)*d)
                    self.H[sl,sl]+=2*.1/d*prob*np.eye(d)
                    nextS=self.A@S;nextS[:,sl]+=np.eye(d)
                    for shock in self.shock:following.append((self.A@M,nextS.copy(),self.A@b+shock))
            states=following
        self.L=float(np.linalg.eigvalsh(self.H/np.sqrt(self.weight[:,None]*self.weight[None,:]))[-1])*(1+1e-12)
        self.setup_seconds=time.perf_counter()-t
    def unpack(self,u):
        return [u[:,self.offsets[n]*self.d:self.offsets[n+1]*self.d].reshape(-1,4**n,self.d) for n in range(self.N)]
    def check(self):
        rng=np.random.default_rng(9162026);x=rng.uniform(0,1.2,(7,self.d))
        u=r4.project(rng.normal(size=(7*self.nodes_count,self.d)),self.B).reshape(7,self.m)
        cost,gs=r4.tree_cost_grad(x,self.unpack(u),self.A,self.shock)
        f=x@self.F.T+self.f0;constant=np.zeros(7)
        for p,M,S,b in self.nodes:constant+=p*r4.qcost(x@M.T+b)
        direct=.5*np.einsum('bi,ij,bj->b',u,self.H,u)+(u*f).sum(1)+constant
        err=float(abs(direct-cost).max());ge=float(abs(np.concatenate([g.reshape(7,-1) for g in gs],1)-(u@self.H+f)).max())
        assert max(err,ge)<2e-11
        return dict(cost_error=err,gradient_error=ge,min_eigenvalue=float(np.linalg.eigvalsh(self.H)[0]))
    def solve(self,x,tol=1e-3,max_iter=5000):
        start=time.perf_counter();f=x@self.F.T+self.f0;u=np.zeros((len(x),self.m));y=u.copy();t=1.
        for it in range(max_iter):
            g=y@self.H+f
            un=r4.project((y-g/(self.L*self.weight)).reshape(-1,self.d),self.B).reshape(len(x),self.m)
            tn=(1+np.sqrt(1+4*t*t))/2;y=un+(t-1)/tn*(un-u);u=un;t=tn
            if it%10==0 or it==max_iter-1:
                g=u@self.H+f;gap=r4.fw_gap(u.reshape(-1,self.nodes_count,self.d),g.reshape(-1,self.nodes_count,self.d),self.B).sum(1)
                if gap.max()<tol:break
        if gap.max()>=tol:raise RuntimeError('QP tolerance not met')
        controls=self.unpack(u);cost,gs=r4.tree_cost_grad(x,controls,self.A,self.shock)
        gap=sum(r4.fw_gap(a,g,self.B).sum(1) for a,g in zip(controls,gs))
        elapsed=time.perf_counter()-start
        err=float(abs(np.concatenate([g.reshape(len(x),-1) for g in gs],1)-(u@self.H+f)).max())
        violation=float(max(0.,-u.min(),(u.reshape(-1,self.nodes_count,self.d).sum(-1)-self.B).max()))
        assert err<2e-11 and violation<2e-12 and gap.min()>-2e-11 and gap.max()<tol+2e-11
        return dict(seconds=elapsed,cost=cost,gap=gap,iterations=it+1,gradient_error=err,feasibility_violation=violation)

def median(fn):
    rows=[fn() for _ in range(3)];r=rows[0];r['timing_samples']=[x['seconds'] for x in rows];r['seconds']=float(np.median(r['timing_samples']));return r

def run():
    critics,_,_,_,_=r5.load(4,101);training=median(lambda:r5.train_critics(4,101,'relu')[1])
    qp=TreeQP(4);algebra=qp.check();points=np.random.default_rng(541021).uniform(0,1.2,(2048,4))
    old=json.loads((ROOT/'replication/r5/output/resource_workloads.json').read_text());rows=[]
    qp.solve(points[:2]);r5.evaluate(critics,None,points[:2],'zero')
    for i,count in enumerate((32,128,512,2048)):
        x=points[:count];assert np.array_equal(x,np.array(old[i]['raw']['initial_states']))
        nn=median(lambda:r5.evaluate(critics,None,x,'zero'));ref=median(lambda:r4.reference(x,qp.A,qp.shock,qp.B,tol=1e-3))
        st=median(lambda:qp.solve(x));tight=np.array(old[i]['raw']['reference_cost']);tightgap=np.array(old[i]['raw']['reference_gap'])
        row=dict(queries=count,critic_training_seconds=training['seconds'],learned_query_seconds=nn['seconds'],
            learned_total_seconds=training['seconds']+nn['seconds'],original_reference_seconds=ref['seconds'],
            qp_setup_seconds=qp.setup_seconds,qp_query_seconds=st['seconds'],qp_total_seconds=qp.setup_seconds+st['seconds'],
            qp_max_gap=float(st['gap'].max()),qp_loss_upper_vs_tight=float((st['cost']-tight+tightgap).max()),
            learned_loss_upper_vs_tight=float((nn['cost']-tight+tightgap).max()),
            learned_cost_replay_error=float(abs(nn['cost']-np.array(old[i]['raw']['policy_cost'])).max()),
            qp_iterations=st['iterations'],gradient_error=st['gradient_error'],feasibility_violation=st['feasibility_violation'],
            timing_samples=dict(learned=nn['timing_samples'],original=ref['timing_samples'],qp=st['timing_samples']),
            raw=dict(qp_cost=st['cost'],qp_gap=st['gap'],learned_cost=nn['cost']))
        assert row['learned_loss_upper_vs_tight']<1e-3+1e-10
        rows.append(row);print('QP',count,row['learned_total_seconds'],row['qp_total_seconds'],flush=True)
    save('structural_qp.json',dict(rows=rows,algebra=algebra,training_samples=training['timing_samples'],
        method='probability-scaled exact convex QP; cold zero controls; all 64 paths; original tree gradients verify every query',
        source_sha256=sha(__file__),review_source='reviews/2026-09-16-econometrica-r5/reviewer_diagnostics.py'))
if __name__=='__main__':run()
