"""Positive Epstein--Zin neural saving/portfolio operator.
Nonhomothetic bequests, stochastic control-dependent portfolio returns,
continuous two-output actor, positive critic, independent NumPy evaluation.
The finite killed/lognormal operator is declared; no continuous BSDE accuracy
is inferred. The sign transform is exact, not a penalty on invalid utility.
"""
from __future__ import annotations
import argparse,json,math,time,resource
from pathlib import Path
import numpy as np
from numpy.polynomial.hermite import hermgauss
import torch
from torch import nn
OUT=Path(__file__).resolve().parents[1]/'results'
torch.set_num_threads(1)
N=6; DT=1/N; BETA=math.exp(-.5*DT); A=1-1/1.5; B=1-5.
X=np.linspace(.25,4.,101); LO=np.array([.005,-1.]); SCALE=np.array([2.995,3.])
Z,W=hermgauss(4); Z=np.sqrt(2)*Z; W=W/math.sqrt(math.pi)

def bequest(x): return .2+x**.6

def q_np(actions,nextC):
    # actions may be (states,2) or (states,alternatives,2).
    x=X.reshape((len(X),)+(1,)*(actions.ndim-2)); m,p=actions[...,0],actions[...,1]
    y=x[...,None]*(1-m[...,None]*DT)*np.exp((.02+.1*p[...,None]-.5*.3**2*p[...,None]**2)*DT+.3*p[...,None]*math.sqrt(DT)*Z)
    cont=np.interp(y,X,nextC)
    cont=np.where((y<X[0])|(y>X[-1]),bequest(y),cont)
    risk=(np.sum(W*cont**B,axis=-1))**(A/B)
    return ((1-BETA)*(m*x)**A+BETA*risk)**(1/A)

class Net(nn.Module):
    def __init__(self,out):
        super().__init__(); self.net=nn.Sequential(nn.Linear(1,48),nn.Tanh(),nn.Linear(48,48),nn.Tanh(),nn.Linear(48,out))
    def forward(self,x): return self.net(x.log()[:,None])
class Actor(Net):
    def __init__(self): super().__init__(2)
    def forward(self,x): return x.new_tensor(LO)+x.new_tensor(SCALE)*super().forward(x).sigmoid()
class Critic(Net):
    def __init__(self): super().__init__(1)
    def forward(self,x): return (.2+x**.6)*super().forward(x).squeeze(-1).exp()

def q_torch(actions,vg):
    x=torch.tensor(X,dtype=actions.dtype); m,p=actions[:,0],actions[:,1]
    z=actions.new_tensor(Z); w=actions.new_tensor(W)
    y=x[:,None]*(1-m[:,None]*DT)*torch.exp((.02+.1*p[:,None]-.5*.3**2*p[:,None]**2)*DT+.3*p[:,None]*math.sqrt(DT)*z)
    f=(y-X[0])/(X[-1]-X[0])*(len(X)-1); idx=f.floor().long().clamp(0,len(X)-2); wt=(f-idx).clamp(0,1)
    c=(1-wt)*vg[idx]+wt*vg[idx+1]; c=torch.where((y<X[0])|(y>X[-1]),.2+y**.6,c)
    risk=(w*c.pow(B)).sum(-1).pow(A/B)
    return ((1-BETA)*(m*x).pow(A)+BETA*risk).pow(1/A)

def evaluate(policy):
    C=np.empty((N+1,len(X))); C[-1]=bequest(X)
    for n in reversed(range(N)):
        C[n]=q_np(policy[n],C[n+1]); C[n,[0,-1]]=bequest(X[[0,-1]])
    return C

def global_q(nextC,proposal):
    m,p=np.meshgrid(np.linspace(.005,3,31),np.linspace(-1,2,31),indexing='ij')
    aa=np.stack([m.ravel(),p.ravel()],-1); allact=np.broadcast_to(aa,(len(X),len(aa),2))
    q=q_np(allact,nextC); j=q.argmax(-1); val=q[np.arange(len(X)),j]; pp=q_np(proposal,nextC)
    best=np.where((pp>val)[:,None],proposal,aa[j]); val=np.maximum(val,pp)
    return val,best

def audit(policy,proposal):
    C=evaluate(policy); U=np.zeros_like(C); uniform=0.; greedy=np.empty_like(policy)
    for n in reversed(range(N)):
        v,greedy[n]=global_q(C[n+1],proposal[n]); gap=np.maximum(np.log(v/C[n]),0); gap[[0,-1]]=0
        # CES monotonicity and log nonexpansiveness yield a safe scalar bound.
        # An independent full optimal recursion below audits it after stopping.
        uniform += float(gap.max())
        U[n]=uniform
    return C,uniform,greedy

def train(seed=50):
    torch.manual_seed(seed); x=torch.tensor(X,dtype=torch.float32); vg=x.new_tensor(bequest(X))
    actors=[None]*N; critics=[None]*N; hist=[]; start=time.perf_counter()
    for n in reversed(range(N)):
        actor=Actor(); critic=Critic()
        if n<N-1:
            actor.load_state_dict(actors[n+1].state_dict()); critic.load_state_dict(critics[n+1].state_dict())
        op=torch.optim.Adam(actor.parameters(),lr=.006)
        for it in range(700):
            q=q_torch(actor(x),vg); loss=-q[1:-1].log().mean(); op.zero_grad();loss.backward();op.step()
        with torch.no_grad(): target=q_torch(actor(x),vg); target[[0,-1]]=x.new_tensor(bequest(X[[0,-1]]))
        op=torch.optim.Adam(critic.parameters(),lr=.004)
        for it in range(700):
            loss=(critic(x).log()-target.log()).square().mean();op.zero_grad();loss.backward();op.step()
        with torch.no_grad():
            vg=critic(x).detach();vg[[0,-1]]=x.new_tensor(bequest(X[[0,-1]]))
            hist.append(dict(date=n,log_evaluation_rmse=float(loss.sqrt())))
        actors[n]=actor;critics[n]=critic
    sec=time.perf_counter()-start
    with torch.no_grad(): proposal=np.stack([a(x).numpy() for a in actors]).astype(float)
    # Verify the Torch target at unrelated continuous actions against NumPy.
    rng=np.random.default_rng(95); test=LO+SCALE*rng.random((len(X),2)); nextC=bequest(X)*(.9+.04*np.sin(X))
    agreement=float(np.max(abs(q_np(test,nextC)-q_torch(torch.tensor(test),torch.tensor(nextC)).numpy())))
    policy=proposal.copy(); trace=[]; raw=evaluate(policy); start=time.perf_counter()
    for it in range(N+1):
        C,bound,greedy=audit(policy,proposal); trace.append(dict(sweep=it,log_value_loss_bound=bound))
        if bound<=.01:break
        policy=greedy
    # Candidate-set optimal reference is NOT used to construct the proposal or stop.
    opt=np.empty_like(C);opt[-1]=bequest(X)
    for n in reversed(range(N)):
        opt[n],_=global_q(opt[n+1],proposal[n]);opt[n,[0,-1]]=bequest(X[[0,-1]])
    met=dict(seed=seed,N=N,dt=DT,gamma=5,psi=1.5,beta=BETA,wealth_grid=[.25,4.,101],
        consumption_fraction_bounds=[.005,3.],portfolio_bounds=[-1.,2.],terminal='0.2+x^0.6',
        boundary='Immediate nonhomothetic bequest if the lognormal endpoint leaves the numerical interval; boundary nodes settle immediately',
        actor_outputs=2,training_action_enumeration=False,training_optimal_labels=False,
        training_seconds=sec,audit_seconds=time.perf_counter()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        torch_numpy_agreement=agreement,history=hist,safeguard_history=trace,
        raw_log_value_loss_t0=float(np.log(opt[0]/raw[0]).max()),certified_log_value_loss_bound=bound,
        safeguarded_log_value_loss_t0=float(np.log(opt[0]/C[0]).max()),
        center_raw_consumption_fraction=float(np.interp(1.,X,proposal[0,:,0])),center_raw_portfolio=float(np.interp(1.,X,proposal[0,:,1])),
        center_value=float(np.interp(1.,X,C[0])),minimum_positive_certainty_equivalent=float(C.min()),
        successful=bound<=.01,continuum_error_bound=None)
    assert agreement<1e-10 and met['safeguarded_log_value_loss_t0']<=bound+1e-9
    tag=f'recursive_s{seed}';OUT.mkdir(exist_ok=True);(OUT/(tag+'.json')).write_text(json.dumps(met,indent=2))
    np.savez_compressed(OUT/(tag+'.npz'),X=X,proposal=proposal,policy=policy,raw=raw,value=C,optimal=opt)
    torch.save(dict(actors=[a.state_dict() for a in actors],critics=[c.state_dict() for c in critics]),OUT/(tag+'.pt'))
    print(json.dumps(met),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seed',type=int,default=50);a=p.parse_args();train(a.seed)
