"""Neural dynamic Cournot feedback with continuous production/investment.
18 Markov states/date; actors improve unilaterally against detached rivals.
Independent continuous-action best responses exploit piecewise-quadratic
structure; the certificate does not require an equilibrium reference.
"""
from __future__ import annotations
import itertools,json,math,time,resource,argparse
from pathlib import Path
import numpy as np
import torch
from torch import nn
OUT=Path(__file__).resolve().parents[1]/'results';torch.set_num_threads(1)
N=3; DISCOUNT=.96; DEP=.1; K=np.array([.25,.75,1.25]); Z=np.array([2.5,3.5]); PZ=np.array([[.8,.2],[.2,.8]])
ST=np.array(list(itertools.product(range(2),range(3),range(3))),int)
FEAT=np.column_stack([Z[ST[:,0]],K[ST[:,1]],K[ST[:,2]]]); S=len(ST)

class Net(nn.Module):
    def __init__(self,out):
        super().__init__();self.net=nn.Sequential(nn.Linear(3,48),nn.Tanh(),nn.Linear(48,48),nn.Tanh(),nn.Linear(48,out))
    def forward(self,s):return self.net((s-s.new_tensor([3.,.75,.75]))/s.new_tensor([.5,.5,.5]))
class Actor(Net):
    def __init__(self,player):super().__init__(2);self.player=player
    def forward(self,s):
        k=s[:,self.player+1];z=super().forward(s).sigmoid()
        # Maintain the declared interval without clipping or capital injections.
        low=(K[0]-(1-DEP)*k).clamp_min(0)
        cap=K[-1]-(1-DEP)*k
        return torch.stack([k*z[:,0],low+(cap-low)*z[:,1]],-1)

def interp_np(v,kn,z):
    f=(kn-K[0])/.5;ij=np.floor(f).astype(int).clip(0,1); w=np.clip(f-ij,0,1);i,j=ij
    return ((1-w[0])*((1-w[1])*v[z,i,j]+w[1]*v[z,i,j+1])+
            w[0]*((1-w[1])*v[z,i+1,j]+w[1]*v[z,i+1,j+1]))

def payoff_np(index,own,rival,player,vnext):
    z,i,j=ST[index];ks=np.array([K[i],K[j]]);acts=[None,None];acts[player]=own;acts[1-player]=rival
    kn=(1-DEP)*ks+np.array([acts[0][1],acts[1][1]])
    continuation=sum(PZ[z,zp]*interp_np(vnext,kn,zp) for zp in range(2))
    q,I=own;return q*(Z[z]-q-rival[0])-.2*I-.4*I*I+DISCOUNT*continuation

def payoff_torch(own,rival,player,vg):
    s=torch.tensor(FEAT,dtype=own.dtype);ks=s[:,1:];acts=torch.stack([own,rival] if player==0 else [rival,own],1)
    kn=(1-DEP)*ks+acts[:,:,1];f=(kn-K[0])/.5;ij=f.floor().long().clamp(0,1);w=(f-ij).clamp(0,1);i,j=ij[:,0],ij[:,1]
    v=vg.reshape(2,3,3);cont=[]
    for z in range(2):
        cont.append((1-w[:,0])*((1-w[:,1])*v[z,i,j]+w[:,1]*v[z,i,j+1])+w[:,0]*((1-w[:,1])*v[z,i+1,j]+w[:,1]*v[z,i+1,j+1]))
    cont=torch.stack(cont,-1);prob=own.new_tensor(PZ[ST[:,0]])
    q,I=own[:,0],own[:,1]
    return q*(s[:,0]-q-rival[:,0])-.2*I-.4*I*I+DISCOUNT*(prob*cont).sum(-1)

def best_response(index,rival,player,vnext):
    """Exact global continuous action search, not a local optimizer.
    Output is quadratic and independent of next capacity. Investment payoff is
    concave quadratic on each interpolation segment; enumerate segment ends
    and its sole stationary point. Rival capacity may fall between grid nodes.
    """
    z,i,j=ST[index];ks=np.array([K[i],K[j]]);ki=ks[player]
    q=float(np.clip((Z[z]-rival[0])/2,0,ki));lo=max(0.,K[0]-(1-DEP)*ki);hi=K[-1]-(1-DEP)*ki
    breaks=np.unique(np.clip(np.r_[lo,hi,K-(1-DEP)*ki],lo,hi));candidates=list(breaks)
    for left,right in zip(breaks[:-1],breaks[1:]):
        if right-left<1e-12:continue
        vl=payoff_np(index,[q,left],rival,player,vnext)+.2*left+.4*left*left
        vr=payoff_np(index,[q,right],rival,player,vnext)+.2*right+.4*right*right
        slope=(vr-vl)/(right-left);stationary=(slope-.2)/.8
        candidates.append(float(np.clip(stationary,left,right)))
    vals=[payoff_np(index,[q,I],rival,player,vnext) for I in candidates];m=int(np.argmax(vals))
    return np.array([q,candidates[m]]),vals[m]

def evaluate(policy):
    V=np.zeros((N+1,2,2,3,3))
    for n in reversed(range(N)):
        for player in range(2):
            flat=V[n,player].reshape(-1)
            for s in range(S):flat[s]=payoff_np(s,policy[n,player,s],policy[n,1-player,s],player,V[n+1,player])
    return V

def audit(policy):
    V=evaluate(policy);BR=np.zeros_like(V);actions=np.empty_like(policy)
    for n in reversed(range(N)):
        for player in range(2):
            flat=BR[n,player].reshape(-1)
            for s in range(S):actions[n,player,s],flat[s]=best_response(s,policy[n,1-player,s],player,BR[n+1,player])
    return V,BR,actions

def train(seed=60):
    torch.manual_seed(seed);st=torch.tensor(FEAT,dtype=torch.float32);actors=[];critics=[];hist=[]
    nextv=[torch.zeros(S),torch.zeros(S)];start=time.perf_counter()
    for n in reversed(range(N)):
        act=[Actor(0),Actor(1)];cri=[Net(1),Net(1)];opts=[torch.optim.Adam(a.parameters(),lr=.006) for a in act]
        leaks=[]
        for it in range(1200):
            for player in range(2):
                for p in act[1-player].parameters():p.grad=None
                with torch.no_grad():rival=act[1-player](st).detach()
                value=payoff_torch(act[player](st),rival,player,nextv[player]);loss=-value.mean()
                opts[player].zero_grad(set_to_none=True);loss.backward();opts[player].step()
                if it==1199:leaks.append(any(p.grad is not None for p in act[1-player].parameters()))
        targets=[]
        with torch.no_grad():
            choices=[a(st).detach() for a in act]
            targets=[payoff_torch(choices[i],choices[1-i],i,nextv[i]).detach() for i in range(2)]
        nxt=[]
        for player in range(2):
            opt=torch.optim.Adam(cri[player].parameters(),lr=.006)
            for it in range(500):
                loss=(cri[player](st)[:,0]-targets[player]).square().mean();opt.zero_grad();loss.backward();opt.step()
            opt=torch.optim.LBFGS(cri[player].parameters(),max_iter=200,line_search_fn='strong_wolfe')
            def closure():
                opt.zero_grad();loss=(cri[player](st)[:,0]-targets[player]).square().mean();loss.backward();return loss
            opt.step(closure)
            with torch.no_grad():nxt.append(cri[player](st)[:,0].detach())
        hist.append(dict(date=n,rival_gradient_leak=any(leaks),evaluation_sup_errors=[float((nxt[i]-targets[i]).abs().max()) for i in range(2)]))
        actors.insert(0,act);critics.insert(0,cri);nextv=nxt
    training=time.perf_counter()-start
    with torch.no_grad():policy=np.array([[a(st).numpy() for a in act] for act in actors],dtype=float)
    start=time.perf_counter();V,BR,bract=audit(policy);gain=BR-V
    # Independent NumPy/Torch objective comparison, including off-grid capacity.
    rng=np.random.default_rng(90);test=rng.normal(size=(2,3,3));agreement=[]
    for player in range(2):
        tq=payoff_torch(torch.tensor(policy[0,player]),torch.tensor(policy[0,1-player]),player,torch.tensor(test.reshape(-1))).numpy()
        nq=np.array([payoff_np(s,policy[0,player,s],policy[0,1-player,s],player,test) for s in range(S)])
        agreement.append(float(abs(tq-nq).max()))
    # Check the analytic global best response against a dense auxiliary grid.
    max_dense_violation=0.
    for player in range(2):
        for s in range(S):
            own,best=best_response(s,policy[0,1-player,s],player,BR[1,player]);ki=FEAT[s,player+1]
            for I in np.linspace(max(0,K[0]-(1-DEP)*ki),K[-1]-(1-DEP)*ki,101):
                val=payoff_np(s,[own[0],I],policy[0,1-player,s],player,BR[1,player]);max_dense_violation=max(max_dense_violation,val-best)
    met=dict(seed=seed,N=N,states=S,capacity_grid=K.tolist(),demand=Z.tolist(),demand_transition=PZ.tolist(),
        discount=DISCOUNT,depreciation=DEP,investment_cost='0.2 I+0.4 I^2',
        capacity_rule='I in [max(0,.25-.9K),1.25-.9K], K_next=.9K+I; no clipping or capital injection',
        actor_outputs_per_player=2,training_actions_continuous=True,training_equilibrium_labels=False,
        training_seconds=training,audit_seconds=time.perf_counter()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        history=hist,torch_numpy_agreement=max(agreement),dense_grid_exceeds_analytic_BR=max_dense_violation,
        dynamic_best_response_gain_t0=gain[0].reshape(2,-1).max(-1).tolist(),
        dynamic_best_response_gain_all_subgames=float(gain.max()),
        payoff_at_low_demand_mid_capacity=V[0,:,0,1,1].tolist(),target=.05,pass_target=float(gain.max())<=.05,
        certificate_scope='Full continuous production and investment deviations on the declared finite Markov state operator; no continuum-state equilibrium assertion')
    assert max(agreement)<1e-10 and max_dense_violation<1e-10 and not any(h['rival_gradient_leak'] for h in hist)
    tag=f'game_s{seed}';OUT.mkdir(exist_ok=True);(OUT/(tag+'.json')).write_text(json.dumps(met,indent=2))
    np.savez_compressed(OUT/(tag+'.npz'),states=FEAT,policy=policy,value=V,best_response_value=BR,best_response_policy=bract)
    torch.save(dict(actors=[[a.state_dict() for a in act] for act in actors],critics=[[c.state_dict() for c in cri] for cri in critics]),OUT/(tag+'.pt'))
    print(json.dumps(met),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seed',type=int,default=60);a=p.parse_args();train(a.seed)
