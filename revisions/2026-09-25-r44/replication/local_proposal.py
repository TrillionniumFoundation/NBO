"""Optional smooth local proposal; no value here is a global certificate."""
import time
import numpy as np
from scipy.optimize import minimize

def improve(d,cache,initial,seconds=5,maxiter=120):
    n,T,m=d['n'],d['T'],d['m']; dim=len(cache['coords']); b=float(d['beta']); eps=float(d['epsilon'])
    trans=np.array(d['P'],dtype=float); costs=np.array(d['k'],dtype=float)
    loss=np.array(cache['ref'][3],dtype=float); star=cache['ref'][2]; nu=np.array(d['nu'],dtype=float)
    inds={(t,i):[] for t in range(T) for i in range(n)}
    for j,(t,i,a) in enumerate(cache['coords']): inds[t,i].append((a,j))
    A=np.zeros((T*n,dim))
    for j,(t,i,a) in enumerate(cache['coords']): A[t*n+i,j]=1
    x0=np.array([float(initial[t][i][a]) for t,i,a in cache['coords']])
    bounds=[(float(lo),float(hi)) for lo,hi in cache['root']]
    x0=np.clip(x0,[v[0] for v in bounds],[v[1] for v in bounds])
    for t in range(T):
        for i in range(n):
            idx=[j for a,j in inds[t,i]]; s=sum(x0[idx])
            if s>1: x0[idx]/=s
    saved={}; last=[x0.copy()]; begin=time.perf_counter()
    def calc(x):
        if 'x' in saved and np.array_equal(x,saved['x']): return saved
        D=np.zeros(n); C=np.zeros(n); GD=np.zeros((n,dim)); GC=np.zeros((n,dim)); constraints=[]; jac=[]
        for t in reversed(range(T)):
            prob=np.zeros((n,m))
            for i in range(n):
                for a,j in inds[t,i]: prob[i,a]=x[j]
                prob[i,star[t][i]]=1-sum(prob[i])
            qd=loss[t]+b*np.einsum('iaj,j->ia',trans,D)
            qc=costs+b*np.einsum('iaj,j->ia',trans,C)
            kernel=np.einsum('ia,iaj->ij',prob,trans)
            newgd=b*kernel@GD; newgc=b*kernel@GC
            for i in range(n):
                for a,j in inds[t,i]:
                    newgd[i,j]+=qd[i,a]-qd[i,star[t][i]]
                    newgc[i,j]+=qc[i,a]-qc[i,star[t][i]]
            D=np.sum(prob*qd,axis=1); C=np.sum(prob*qc,axis=1); GD,GC=newgd,newgc
            constraints.append(eps-D); jac.append(-GD.copy())
        saved.clear(); saved.update(x=x.copy(),fun=float(nu@C),grad=nu@GC,con=np.concatenate(constraints),jac=np.vstack(jac))
        return saved
    class Stop(Exception): pass
    def callback(x):
        last[0]=x.copy()
        if time.perf_counter()-begin>seconds: raise Stop()
    try:
        res=minimize(lambda x:calc(x)['fun'],x0,jac=lambda x:calc(x)['grad'],bounds=bounds,
                     constraints=[{'type':'ineq','fun':lambda x:1-A@x,'jac':lambda x:-A},{'type':'ineq','fun':lambda x:calc(x)['con'],'jac':lambda x:calc(x)['jac']}],
                     method='SLSQP',callback=callback,options={'ftol':1e-11,'maxiter':maxiter,'disp':False})
        xx=res.x; status=str(res.message)
    except Stop:
        xx=last[0]; status='local_time_cap'
    p=[[[0.]*m for i in range(n)] for t in range(T)]
    for j,(t,i,a) in enumerate(cache['coords']): p[t][i][a]=max(0.,xx[j])
    return p,dict(seconds=time.perf_counter()-begin,status=status,proposal_cost=calc(xx)['fun'])
