"""Executed neural, polynomial and nearest-anchor proposal comparisons.

The MLP is actually trained (NumPy Adam, no prewritten predictions). Teacher,
training, online proposal, policy evaluation and exact upper-reference costs are
reported separately. Any unfavorable neural outcome remains in the deposit.
"""
from __future__ import annotations
import time,resource,json
from pathlib import Path
import numpy as np
from canonical import load,dump,digest
from engine import Engine,SIGNS,EPS
from certified_arithmetic import derive
HERE=Path(__file__).parent

def features(eng,lam):
    s=eng.b.e[0].states.astype(float);u=s[:,0];x=np.log(s[:,1]);u=(u-u.mean())/(u.std()+1e-12);x=(x-x.mean())/(x.std()+1e-12)
    return np.concatenate([np.column_stack((u,x,np.full(eng.S,n/8),np.full(eng.S,lam))) for n in range(1,8)])
def polynomial(x):
    return np.column_stack((np.ones(len(x)),x,*[x[:,i]*x[:,j] for i in range(x.shape[1]) for j in range(i,x.shape[1])]))
def train(X,y,k,epochs=45,seed=1319):
    rng=np.random.default_rng(seed);dims=[X.shape[1],32,32,k];w=[]
    for a,b in zip(dims[:-1],dims[1:]):w.extend([rng.normal(0,np.sqrt(2/a),(a,b)),np.zeros(b)])
    moments=[np.zeros_like(z) for z in w];squares=[np.zeros_like(z) for z in w];step=0;losses=[]
    for epoch in range(epochs):
        order=rng.permutation(len(X));loss=0.
        for start in range(0,len(X),512):
            ids=order[start:start+512];xx=X[ids];yy=y[ids];z1=xx@w[0]+w[1];h1=np.maximum(z1,0);z2=h1@w[2]+w[3];h2=np.maximum(z2,0);z3=h2@w[4]+w[5];z3-=z3.max(1,keepdims=True);p=np.exp(z3);p/=p.sum(1,keepdims=True);loss-=np.log(np.maximum(p[np.arange(len(ids)),yy],1e-300)).sum();p[np.arange(len(ids)),yy]-=1;p/=len(ids)
            g4=h2.T@p;g5=p.sum(0);g2=(p@w[4].T)*(z2>0);g3=g2.sum(0);g2w=h1.T@g2;g0=(g2@w[2].T)*(z1>0);grads=[xx.T@g0,g0.sum(0),g2w,g3,g4,g5]
            norm=np.sqrt(sum(float((g*g).sum()) for g in grads));scale=min(1.,5./max(norm,1e-30));step+=1
            for i,g in enumerate(grads):
                g*=scale;moments[i]=.9*moments[i]+.1*g;squares[i]=.999*squares[i]+.001*g*g
                w[i]-=.002*(moments[i]/(1-.9**step))/(np.sqrt(squares[i]/(1-.999**step))+1e-8)
        losses.append(float(loss/len(X)))
    return w,losses

def scores(X,w):return np.maximum(np.maximum(X@w[0]+w[1],0)@w[2]+w[3],0)@w[4]+w[5]
def feasible(eng,z,classes,adj):
    result=np.zeros((8,eng.S),np.int32)
    for n in range(1,8):
        a=z[(n-1)*eng.S:n*eng.S];mask=eng.mask(n,adj,1)[:,classes]
        if not mask.any(1).all():raise ValueError('proposal class set has no feasible action')
        result[n]=classes[np.where(mask,a,-np.inf).argmax(1)]
    return result

def value(eng,p,lam,adj,verify=False):
    v=eng.b.terminal.copy()
    for n in range(7,0,-1):
        if not eng.mask(n,adj,1)[eng.ix,p[n]].all():raise ValueError('infeasible proposed action')
        if verify:
            q=(1-lam)*eng.q(0,n,v,.42425,.85)+lam*eng.q(1,n,v,.42425,.85);v=q[eng.ix,p[n]]
        else:v=(1-lam)*eng.selected(0,n,p[n],v,.42425,.85)+lam*eng.selected(1,n,p[n],v,.42425,.85)
    q=(1-lam)*eng.fq(0,v,.42425)+lam*eng.fq(1,v,.42425)
    out={}
    for s in SIGNS:
        mask=eng.first_mask(adj,s,.8,.5)
        if s=='positive':mask&=eng.fm.actions[:,2]>0
        ids=np.flatnonzero(mask);i=int(ids[np.argmax(q[ids])]);out[s]=dict(value=float(q[i]),first_index=i,first_action=eng.fm.actions[i].tolist())
    return out

def main():
    start=time.perf_counter();b,j=load(HERE/'canonical');eng=Engine(b,j);audit=derive(b,j);records=[];fits=[];archive={};max_discrepancy=0.
    for adj in (True,False):
        t=time.perf_counter();anchors=[]
        for lam in (.12,.13):
            v,p,f=eng.solve(lam,.42425,.85,adj,1);anchors.append(p.copy())
        teacher=time.perf_counter()-t
        X=np.concatenate([features(eng,lam) for lam in (.12,.13)]);targets=np.concatenate([p[1:].ravel() for p in anchors]);classes,y=np.unique(targets,return_inverse=True)
        t=time.perf_counter();weights,losses=train(X,y,len(classes));neural_train=time.perf_counter()-t
        t=time.perf_counter();phi=polynomial(X);onehot=np.eye(len(classes))[y];beta=np.linalg.solve(phi.T@phi+1e-5*np.eye(phi.shape[1]),phi.T@onehot);poly_train=time.perf_counter()-t
        key=str(int(adj));archive[key+'.classes']=classes;archive[key+'.polynomial']=beta
        for i,w in enumerate(weights):archive[key+f'.weight.{i}']=w
        for i,p in enumerate(anchors):archive[key+f'.anchor.{i}']=p
        fits.append(dict(adjustment=adj,teacher_seconds=teacher,neural_training_seconds=neural_train,polynomial_training_seconds=poly_train,training_rows=len(X),action_classes=len(classes),epochs=45,seed=1319,loss_initial=losses[0],loss_final=losses[-1],neural_parameter_bytes=sum(w.nbytes for w in weights)+classes.nbytes,polynomial_parameter_bytes=beta.nbytes+classes.nbytes,nearest_anchor_bytes=sum(p.nbytes for p in anchors),training_laws=[.12,.13]))
        for lam in (0.,.125,.25,.75,1.):
            t=time.perf_counter();ref,pp,ff=eng.solve(lam,.42425,.85,adj,1);reference=time.perf_counter()-t
            for method in ('neural','polynomial','nearest_anchor'):
                t=time.perf_counter()
                if method=='neural':p=feasible(eng,scores(features(eng,lam),weights),classes,adj)
                elif method=='polynomial':p=feasible(eng,polynomial(features(eng,lam))@beta,classes,adj)
                else:p=anchors[int(lam>.125)].copy()
                proposal=time.perf_counter()-t;t=time.perf_counter();vv=value(eng,p,lam,adj);evaluation=time.perf_counter()-t;t=time.perf_counter();check=value(eng,p,lam,adj,True);verification=time.perf_counter()-t
                for s in SIGNS:
                    diff=abs(vv[s]['value']-check[s]['value']);max_discrepancy=max(max_discrepancy,diff);assert diff<2e-10
                    assert vv[s]['value']<=ff[s][0]+2*EPS
                tag=f'{int(adj)}.{lam}.{method}';archive[tag+'.policy']=p
                records.append(dict(id=tag,adjustment=adj,law=lam,method=method,proposal_seconds=proposal,evaluation_seconds=evaluation,upper_reference_seconds=reference,verification_seconds=verification,online_certified_seconds=proposal+evaluation+reference+verification,gaps={s:max(0.,ff[s][0]-vv[s]['value'])+2*EPS for s in SIGNS},lower_witnesses=vv,exact_upper_values={s:ff[s][0]+EPS for s in SIGNS}))
                print('PROPOSAL',tag,records[-1]['gaps'],flush=True)
            eng.cache.clear()
    np.savez_compressed(HERE/'extensions/proposal_witness.npz',**archive)
    dump(HERE/'extensions/proposals.json',dict(schema='nbo-r13-proposal-benchmark-v1',canonical_manifest_sha256=digest(HERE/'canonical/manifest.json'),fits=fits,rows=records,scope='Teacher-trained continuation policies on one fixed settlement target; common exact first-date feasible optimization and exact-DP upper reference are charged. This experiment does not establish universal neural necessity or superiority.',independent_policy_evaluation_max_discrepancy=max_discrepancy,policy_archive_sha256=digest(HERE/'extensions/proposal_witness.npz'),elapsed_seconds=time.perf_counter()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
if __name__=='__main__':main()
