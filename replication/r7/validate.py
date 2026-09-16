#!/usr/bin/env python3
"""Small-model independent recursions and deposited coefficient replay.
Random experiments test implementations, not replace the analytical proofs.
"""
from core import *
from types import SimpleNamespace
import gc

class Toy:
    def __init__(self,K,R,g):
        self.K=K;self.R=R;self.terminal=g;self.steps=len(R);self.ns=len(g);self.calls=0
        menu=np.zeros((K.shape[2],3));menu[:,2]=np.arange(K.shape[2])-1
        self.e=[SimpleNamespace(menu=menu,extra=[],common=SimpleNamespace(continuation=self.cont(k))) for k in (0,1)]
    def cont(self,k):
        def f(v):
            self.calls+=1
            return np.einsum('sat,t->sa',self.K[k],v)
        return f
    def q(self,k,n,v,d):return self.R[n,k]+self.e[k].common.continuation(v)

def independent(model,a,b):
    """Plain count and endpoint-policy recursions, no production oracle calls."""
    H=model.steps;S=model.ns;K=model.K;R=model.R
    def step(n,t,v):return (1-t)*R[n,0]+t*R[n,1]+np.einsum('sat,t->sa',(1-t)*K[0]+t*K[1],v)
    def optimal(t):
        v=[None]*H+[model.terminal];p=[None]*H
        for n in range(H-1,-1,-1):
            q=step(n,t,v[n+1]);p[n]=q.argmax(1);v[n]=q.max(1)
        return np.stack(v),np.stack(p)
    va,pa=optimal(a);vb,pb=optimal(b)
    W=[None]*H+[model.terminal[None,:]];F=[None]*H+[model.terminal[None,:]]
    for n in range(H-1,-1,-1):
        h=H-n;w=[];f=[]
        for j in range(h+1):
            q=np.zeros((S,K.shape[2]));z=q.copy()
            if j<h:
                q+=(1-j/h)*step(n,a,W[n+1][j]);z+=(1-j/h)*step(n,a,F[n+1][j])
            if j>0:
                q+=j/h*step(n,b,W[n+1][j-1]);z+=j/h*step(n,b,F[n+1][j-1])
            w.append(q.max(1));f.append(z[np.arange(S),pa[n]])
        W[n]=np.stack(w);F[n]=np.stack(f)
    return va,vb,W,F

def run():
    rng=np.random.default_rng(17092026);checks=0;max_replay=0.;min_order=0.;scaling=[];max_bound_ratio=0.
    for H in (1,2,3,4,6,8,12,16):
        for rep in range(12):
            K=rng.uniform(size=(2,3,3,3));K*=rng.uniform(.7,.99,size=(2,3,3,1))/K.sum(-1,keepdims=True)
            R=rng.uniform(-1,1,size=(H,2,3,3));g=rng.uniform(-1,1,3);model=Toy(K,R,g)
            a,b=sorted(rng.uniform(size=2));va,vb,W,F=independent(model,a,b)
            model.calls=0;M=chord(model,a,b,va,vb);nc=model.calls
            U=expand(model,va,vb,M);model.calls=0;WC=count(model,a,b,0.,va,vb);nw=model.calls
            expected_chord=0 if H==1 else 4*H-6
            assert nc==expected_chord and nw==H*(H+1)-2
            if rep==0:scaling.append(dict(horizon=H,chord_kernel_calls=nc,count_kernel_calls=nw,
                chord_vectors=len(U.M),count_interior_vectors=H*(H-1)//2))
            max_replay=max(max_replay,max(float(abs(x-y).max()) for x,y in zip(W,WC)))
            min_order=min(min_order,min(float((u-w).min()) for u,w in zip(U,W)))
            assert min_order>-2e-12 and max_replay<2e-12
            beta=float(K.sum(-1).max());kappa=float(abs(K[1]-K[0]).sum(-1).max())
            B=[0.]*(H+1);L=B.copy();A=B.copy();B[-1]=float(abs(g).max())
            for n in range(H-1,-1,-1):
                B[n]=float(abs(R[n]).max())+beta*B[n+1]
                L[n]=float(abs(R[n,1]-R[n,0]).max())+kappa*B[n+1]+beta*L[n+1]
                A[n]=kappa*L[n+1]+beta*A[n+1]
                bound=2*L[n]*(b-a)+.5*A[n]*(b-a)**2
                actual=float((U[n]-F[n]).max())
                assert actual<=bound+2e-12
                if bound>0:max_bound_ratio=max(max_bound_ratio,actual/bound)
            for t in (.0,.19,.5,.81,1.):
                exact=solve(model,a+(b-a)*t,0.)['value']
                uw=np.stack([bernstein_value(x,t) for x in W])
                assert (uw-exact).min()>-2e-12
                checks+=1
    # Strict counterexample: first choose a state, then success under opposite laws.
    K=np.zeros((2,3,3,3));K[:,0,0,1]=1.;K[:,0,1:,2]=1.
    R=np.zeros((2,2,3,3));R[1,1,1,:]=1.;R[1,0,2,:]=1.
    toy=Toy(K,R,np.zeros(3));va,vb,W,F=independent(toy,0.,1.)
    U=expand(toy,va,vb,chord(toy,0.,1.,va,vb))
    strict=dict(chord=U[0][:,0],count=W[0][:,0],true_midpoint=solve(toy,.5,0.)['value'][0,0])
    assert np.allclose(strict['chord'],[1,1,1]) and np.allclose(strict['count'],[1,.5,1])
    result=dict(seed=17092026,models=96,parameter_checks=checks,independent_count_replay_max=max_replay,
        minimum_chord_minus_count=min_order,total_error_bound_max_ratio=max_bound_ratio,
        scaling=scaling,strict_example=strict,scope='independent dense small-model implementation versus production count/chord code; tests are not proofs')
    save('validation.json',result);return result

def replay_decision():
    data=json.loads((OUT/'decision.json').read_text());co=np.load(OUT/'decision_coefficients.npz');err=data['roundoff']['per_class_allowance'];maximum=0.
    for i,row in enumerate(data['attempts']):
        for arm in ('adjusted','fixed'):
            U={s:co[f'cell.{i}.{arm}.{s}.upper'] for s in ('positive','nonpositive')}
            L={s:co[f'cell.{i}.{arm}.{s}.lower'] for s in U}
            bounds=[max(float((z-U['nonpositive']).min()) for z in L['positive'])-2*err,
                    min(float((U['positive']-z).max()) for z in L['nonpositive'])+2*err]
            maximum=max(maximum,float(abs(np.array(bounds)-row['delta'][arm]).max()))
            assert np.array_equal(bounds,row['delta'][arm])
    co.close();save('decision_replay.json',dict(maximum_difference=maximum,attempts=len(data['attempts']),
        scope='coefficient-only replay; does not rebuild kernels or optimize policies'))

if __name__=='__main__':
    run()
    if (OUT/'decision_coefficients.npz').exists():replay_decision()
