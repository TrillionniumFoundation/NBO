"""Two-output proposals under the unchanged two-shock Bellman certificate.

The generated ordinary vector_base69.py retains the R67 lower-bound kernel.
A proposed interior action supplies only an additional paid upper witness.
Uniform refinement changes the split choice, never the global lower bound.
"""
import time
import numpy as np
from scipy.optimize import minimize
import readout69 as r
from vector_base69 import Oracle as Base,project
import vector66 as prior
q=r.q

class Oracle(Base):
    def __init__(self,kind='simplicial',models=None):
        super().__init__(max_nodes=1024,batch=256)
        self.kind=kind;self.models=models or {};self.uniform=(kind=='uniform')
        self.counts.update(proposal_queries=0,prediction_seconds=0.)
    def proposal(self,x,horizon,cap):
        if self.kind not in ('hat-vector','quadratic-vector'):return None
        start=time.perf_counter();key=horizon if horizon in self.models else str(horizon)
        W=np.asarray(self.models[key]);P=r.phi(x,'hat-relu') if self.kind=='hat-vector' else q.polynomial(x)
        value=P@W
        if self.kind=='hat-vector':value=cap[:,None]*value
        answer=project(value,cap);self.counts['proposal_queries']+=len(x)
        self.counts['prediction_seconds']+=time.perf_counter()-start
        return answer

def fit(d,T,seed,kind,n=12):
    if kind not in ('hat-vector','quadratic-vector'):return {},dict(seconds=0.,dates=[],labels=0),{}
    start=time.perf_counter();rng=np.random.default_rng(seed);x=rng.integers(0,2**16,size=(n,d))/2**16
    cap=q.clamp(q.cap_interval(x).lo,q.cap_interval(x).lo);models={};records=[];raw={'states':x}
    for horizon in range(2,T+1):
        begin=time.perf_counter();oracle=prior.Oracle(batch=128)
        teacher=oracle.solve(x,horizon,1/16);labels=teacher['action'];label_seconds=time.perf_counter()-begin
        P=r.phi(x,'hat-relu') if kind=='hat-vector' else q.polynomial(x)
        Y=labels/cap[:,None] if kind=='hat-vector' else labels
        if kind=='hat-vector':
            def fun(w):
                W=w.reshape(P.shape[1],2);err=P@W-Y
                return float(np.mean(err**2)),(P.T@err/len(P)).reshape(-1)
            result=minimize(fun,np.full(P.shape[1]*2,.25),jac=True,method='L-BFGS-B',
                bounds=[(0.,1.)]*(P.shape[1]*2),options=dict(maxiter=160,gtol=1e-9,ftol=1e-14))
            W=np.round(np.clip(result.x.reshape(P.shape[1],2),0,1)*2**16)/2**16
            status=dict(success=bool(result.success),iterations=int(result.nit),message=str(result.message))
        else:
            W=np.linalg.solve(P.T@P+np.eye(P.shape[1])*1e-6,P.T@Y);status=dict(success=True,iterations=1,message='ridge proposal')
        models[horizon]=W.tolist();raw[f'r{horizon}_labels']=labels
        records.append(dict(r=horizon,label_seconds=label_seconds,seconds=time.perf_counter()-begin,
            label_counts=oracle.counts,optimizer=status,coefficients=int(W.size)))
    return models,dict(seconds=time.perf_counter()-start,dates=records,labels=n*(T-1),
        scope='Two-output proposal trained on identical paid labels; scalar certificate-loss theorem is not relabeled as a vector training theorem'),raw
