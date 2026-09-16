#!/usr/bin/env python3
"""R5 referee diagnostics. Writes review output only; author files are immutable.
Run: python reviews/2026-09-16-econometrica-r5/reviewer_diagnostics.py
Dependencies: the existing NumPy/SciPy/PyTorch author environment.
"""
from __future__ import annotations
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[k]='1'
import argparse,hashlib,json,platform,sys,time
from pathlib import Path
import numpy as np
PIN='c9f71077cf6a339573ac07be55d7660797bcf6ea'

def median_runs(fn):
    runs=[fn() for _ in range(3)];r=runs[0]
    r['samples']=[x['seconds'] for x in runs];r['seconds']=float(np.median(r['samples']))
    return r

class TreeQP:
    """Exact parametric nonanticipative QP, no learning or query warm starts.
    Index controls by the 1+4+16 decision histories. Cache the quadratic form.
    Precondition by node probabilities; simplex projection is unchanged because
    the diagonal metric is constant across all controls at any given node.
    """
    def __init__(self,d,r4):
        start=time.perf_counter();self.d=d;self.r4=r4
        self.A,self.shock,self.B=r4.primitives(d);self.m=21*d
        Q=np.eye(d)/d+.2*np.ones((d,d))/d**2
        self.H=np.zeros((self.m,self.m));self.F=np.zeros((self.m,d));self.f0=np.zeros(self.m)
        self.weight=np.repeat(np.r_[1.,np.full(4,.25),np.full(16,1/16)],d)
        states=[(np.eye(d),np.zeros((d,self.m)),np.zeros(d))];self.nodes=[]
        for n in range(4):
            prob=4.**(-n);following=[]
            self.nodes.extend((prob,M,S,b) for M,S,b in states)
            for node,(M,S,b) in enumerate(states):
                self.H+=2*prob*S.T@Q@S;self.F+=2*prob*S.T@Q@M;self.f0+=2*prob*S.T@Q@(b-1)
                if n<3:
                    j=[0,1,5][n]+node;sl=slice(j*d,(j+1)*d)
                    self.H[sl,sl]+=2*.1/d*prob*np.eye(d)
                    nextS=self.A@S;nextS[:,sl]+=np.eye(d)
                    for shock in self.shock:following.append((self.A@M,nextS.copy(),self.A@b+shock))
            states=following
        transformed=self.H/np.sqrt(self.weight[:,None]*self.weight[None,:])
        self.L=float(np.linalg.eigvalsh(transformed)[-1])*(1+1e-12)
        self.setup_seconds=time.perf_counter()-start
    def unpack(self,u):
        d=self.d
        return [u[:,:d].reshape(-1,1,d),u[:,d:5*d].reshape(-1,4,d),u[:,5*d:].reshape(-1,16,d)]
    def check(self):
        rng=np.random.default_rng(9162026);x=rng.uniform(0,1.2,(7,self.d))
        u=self.r4.project(rng.normal(size=(7*21,self.d)),self.B).reshape(7,self.m)
        cost,gs=self.r4.tree_cost_grad(x,self.unpack(u),self.A,self.shock)
        f=x@self.F.T+self.f0;constant=np.zeros(7)
        for p,M,S,b in self.nodes:constant+=p*self.r4.qcost(x@M.T+b)
        direct=.5*np.einsum('bi,ij,bj->b',u,self.H,u)+(u*f).sum(1)+constant
        error=float(abs(direct-cost).max());gerror=float(abs(np.concatenate([g.reshape(7,-1) for g in gs],1)-(u@self.H+f)).max())
        assert max(error,gerror)<2e-11
        return dict(cost_error=error,gradient_error=gerror,min_hessian_eigenvalue=float(np.linalg.eigvalsh(self.H)[0]),L=self.L)
    def solve(self,x,tol=1e-3,max_iter=5000):
        start=time.perf_counter();f=x@self.F.T+self.f0
        u=np.zeros((len(x),self.m));y=u.copy();t=1.
        for it in range(max_iter):
            grad=y@self.H+f
            un=self.r4.project((y-grad/(self.L*self.weight)).reshape(-1,self.d),self.B).reshape(len(x),self.m)
            tn=(1+np.sqrt(1+4*t*t))/2;y=un+(t-1)/tn*(un-u);u=un;t=tn
            if it%10==0 or it==max_iter-1:
                g=u@self.H+f;gap=self.r4.fw_gap(u.reshape(-1,21,self.d),g.reshape(-1,21,self.d),self.B).sum(1)
                if gap.max()<tol:break
        if gap.max()>=tol:raise RuntimeError('Tolerance not met')
        controls=self.unpack(u)
        # Include complete-tree cost AND independent source-tree gap in timing.
        cost,gs=self.r4.tree_cost_grad(x,controls,self.A,self.shock)
        checkgap=sum(self.r4.fw_gap(a,g,self.B).sum(1) for a,g in zip(controls,gs))
        elapsed=time.perf_counter()-start
        gerror=float(abs(np.concatenate([g.reshape(len(x),-1) for g in gs],1)-(u@self.H+f)).max())
        violation=float(max(0.,-u.min(),(u.reshape(-1,21,self.d).sum(-1)-self.B).max()))
        assert gerror<2e-11 and violation<2e-12 and checkgap.min()>-2e-11 and checkgap.max()<tol+2e-11
        return dict(seconds=elapsed,cost=cost,gap=checkgap,iterations=it+1,gradient_discrepancy=gerror,feasibility_violation=violation)

def resource_audit(root):
    import coupled_resource as r4
    import resource_ablation as r5
    critics,_,_,_,_=r5.load(4,101)
    training=median_runs(lambda:r5.train_critics(4,101,'relu')[1])
    qp=TreeQP(4,r4);check=qp.check()
    points=np.random.default_rng(541021).uniform(0,1.2,(2048,4))
    deposited=json.loads((root/'replication/r5/output/resource_workloads.json').read_text());rows=[]
    qp.solve(points[:2]);r5.evaluate(critics,None,points[:2],'zero')
    for i,count in enumerate((32,128,512,2048)):
        x=points[:count];assert np.array_equal(x,np.array(deposited[i]['raw']['initial_states']))
        learned=median_runs(lambda:r5.evaluate(critics,None,x,'zero'))
        original=median_runs(lambda:r4.reference(x,qp.A,qp.shock,qp.B,tol=1e-3))
        reuse=median_runs(lambda:qp.solve(x))
        ref=np.array(deposited[i]['raw']['reference_cost']);rgap=np.array(deposited[i]['raw']['reference_gap'])
        total=training['seconds']+learned['seconds'];qtotal=qp.setup_seconds+reuse['seconds']
        row=dict(queries=count,critic_training_seconds=training['seconds'],learned_query_seconds=learned['seconds'],learned_total_seconds=total,
            author_reference_seconds=original['seconds'],author_reference_gap=float(original['gap'].max()),
            reusable_qp_setup_seconds=qp.setup_seconds,reusable_qp_query_seconds=reuse['seconds'],reusable_qp_total_seconds=qtotal,
            reusable_qp_max_gap=float(reuse['gap'].max()),reusable_qp_iterations=reuse['iterations'],
            learned_max_loss_upper=float((learned['cost']-ref+rgap).max()),qp_loss_upper_vs_tight_reference=float((reuse['cost']-ref+rgap).max()),
            gradient_discrepancy=reuse['gradient_discrepancy'],feasibility_violation=reuse['feasibility_violation'],
            learned_vs_deposited_cost_error=float(abs(learned['cost']-np.array(deposited[i]['raw']['policy_cost'])).max()),
            author_over_learned_ratio=original['seconds']/total,learned_over_qp_ratio=total/qtotal,
            timing_samples=dict(learned=learned['samples'],author_reference=original['samples'],reusable_qp=reuse['samples']),
            raw=dict(qp_cost=reuse['cost'].tolist(),qp_gap=reuse['gap'].tolist()))
        assert row['learned_vs_deposited_cost_error']<2e-8
        print('RESOURCE',{k:v for k,v in row.items() if k not in ('raw','timing_samples')},flush=True);rows.append(row)
    return dict(d=4,seed=101,held_out_seed=541021,algebra_check=check,training_samples_seconds=training['samples'],rows=rows,
        scope='Same finite economy and R5 held-out queries, cold-start controls, all 64 paths, setup included, serial one-thread median-of-three timing.')

def bank_audit(root,remove):
    import contracts as c
    import economic_robustness as er
    z=np.load(root/'replication/r5/output/contract_bank.npz');e=c.Economy()
    F=z['features'];V=z['values'];P=z['policies'];ds=z['d'];replay=0.;gain=0.;intervals=[];restricted=[]
    for i,d in enumerate(ds):
        replay=max(replay,float(abs(e.evaluate(P[i])-F[i]).max()));gain=max(gain,float(e.one_step_gain(V[i],float(d)).max()))
        if i+1<len(ds):
            a,b=ds[i:i+2];Fa,Fb=F[i:i+2];ia=Fa[0]-2*Fa[2];ib=Fb[0]-2*Fb[2];sa=Fa[1];sb=Fb[1];den=sa-sb
            cross=np.divide(ib-ia,den,out=np.full_like(den,a),where=abs(den)>1e-14);g=-np.inf
            for q in (a,b,np.clip(cross,a,b)):
                lam=(q-a)/(b-a);g=max(g,float(((1-lam)*V[i]+lam*V[i+1]-np.maximum(ia+q*sa,ib+q*sb)).max()))
            intervals.append(dict(left=float(a),right=float(b),upper_loss=g))
        if remove:
            extras=e.extra;e.extra=[];r=e.optimal(float(d));e.extra=extras;delta=V[i]-r['value']
            center=int(np.argmin(np.linalg.norm(e.states-[2,1.25],axis=1)))
            restricted.append(dict(d=float(d),max_loss_vs_full_target=float(delta.max()),focal_loss=float(delta[0,center]),focal_controls=e.controls(r['policy'])[0,center].tolist()))
        if i%10==0:print('BANK',i,flush=True)
    bank=[dict(d=float(d),k=2.,value=V[i],feature=F[i],policy=P[i]) for i,d in enumerate(ds)]
    signs=er.sign_certificate(e,bank)
    assert signs['groups']==json.loads((root/'replication/r5/output/sign_certificate.json').read_text())['groups']
    return dict(anchors=len(ds),feature_replay_error=replay,all_anchor_bellman_gain=gain,independently_recomputed_uniform_bound=max(r['upper_loss'] for r in intervals),
        intervals=intervals,sign_groups=signs['groups'],neural_action_selection_count=int((P>=len(e.menu)).sum()),total_decisions=int(P.size),
        restricted_common_menu_comparison=restricted,restriction_scope='Remove only three frozen neural actions; retain full common union mesh. Exact full-menu loss comparison at the 47 anchors, not an entire-interval claim.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);ap.add_argument('--mode',choices=['resource','bank','all'],default='all')
    ap.add_argument('--remove-neural',action='store_true');ap.add_argument('--output',type=Path,default=Path(__file__).with_name('diagnostic_results.json'));a=ap.parse_args()
    root=a.root.resolve();sys.path[:0]=[str(root/'replication/r5'),str(root/'replication/r4')]
    import scipy,torch
    result=dict(reviewed_commit=PIN,python=sys.version,numpy=np.__version__,scipy=scipy.__version__,torch=torch.__version__,platform=platform.platform(),
        processor=platform.processor(),thread_environment={k:os.environ[k] for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')})
    if a.mode in ('resource','all'):result['resource']=resource_audit(root)
    if a.mode in ('bank','all'):result['bank']=bank_audit(root,a.remove_neural)
    result['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();a.output.write_text(json.dumps(result,indent=2)+'\n');print('WROTE',a.output,flush=True)
if __name__=='__main__':main()
