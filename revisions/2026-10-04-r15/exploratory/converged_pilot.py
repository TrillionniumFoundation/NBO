"""EXPLORATORY ONLY. Converge fixed-policy Sobolev replay; no payoff search."""
from pathlib import Path
import copy,json,sys,time
import numpy as np
import torch
from torch import nn
sys.path.insert(0,str(Path(__file__).parent))
import critic_pilot as p

class ExposureCritic(nn.Module):
    def __init__(self,d,width=32):
        super().__init__();self.space=p.mlp(7,width);self.time=p.mlp(1,16)
        self.register_buffer('B',torch.from_numpy(p.old.coupling(d)))
    def forward(self,tx):
        t,y=tx[:,:1],tx[:,1:];n,d=y.shape;z=y@self.B.T
        row=self.B.sum(1)[None,:].expand_as(y)
        zz=z@self.B.T;fz=torch.tanh(z)@self.B.T
        mu=y.mean(1,keepdim=True).expand_as(y)
        feats=torch.stack([t.expand_as(y),y,z,row,zz,fz,mu],-1)
        spatial=self.space(feats.reshape(n*d,7)).reshape(n,d).mean(1,keepdim=True)
        return p.baseline(tx)+(1-t)*(self.time(t)+spatial)

def run():
    base=Path(__file__).parent/'d20_s7919_high_anchor';out=base/'converged';out.mkdir(exist_ok=True)
    oldrecord=json.loads((base/'PILOT.json').read_text());p.P.update(oldrecord['primitive_parameters'])
    with np.load(base/'BANKS.npz') as z:arr={k:torch.from_numpy(z[k]) for k in z.files}
    x=arr['train_states'];test=arr['diagnostic_states'];v=arr['train_values'].mean(0);q=arr['train_q'].mean(0)
    raw={'raw1':arr['raw_q'][0],'raw_antithetic2':arr['raw_q'][:2].mean(0),'raw_antithetic4':arr['raw_q'].mean(0)}
    results=[]
    for name,make,weights in [('split_lbfgs',lambda:p.SplitCritic(20,32),base/'split_blocked_value.pt'),
                              ('exposure_lbfgs',lambda:ExposureCritic(20,32),None)]:
        torch.manual_seed(151053021);critic=make()
        if weights:critic.load_state_dict(torch.load(weights,weights_only=True))
        start=time.perf_counter();calls=0;history=[]
        optimizer=torch.optim.LBFGS(critic.space.parameters(),lr=1,max_iter=300,max_eval=400,
                                   tolerance_grad=1e-10,tolerance_change=1e-12,history_size=30,line_search_fn='strong_wolfe')
        def closure():
            nonlocal calls
            optimizer.zero_grad(set_to_none=True)
            _,_,_,grad=p.old.first_jet(critic,x);loss=(20*grad-q).square().mean()
            loss.backward();calls+=1
            if calls%50==0:
                diag,_=p.diagnostic(critic,test,arr['fine_values'],arr['fine_q'],raw)
                history.append(dict(calls=calls,loss=float(loss.detach()),diagnostic=diag))
            return loss
        optimizer.step(closure)
        timeopt=torch.optim.Adam(critic.time.parameters(),lr=.003)
        with torch.no_grad():space=critic(x)-p.baseline(x)-(1-x[:,:1])*critic.time(x[:,:1])
        for _ in range(400):
            pred=p.baseline(x)+space+(1-x[:,:1])*critic.time(x[:,:1]);loss=(pred-v).square().mean()
            timeopt.zero_grad(set_to_none=True);loss.backward();timeopt.step()
        diag,pred=p.diagnostic(critic,test,arr['fine_values'],arr['fine_q'],raw)
        torch.save(critic.state_dict(),out/(name+'.pt'));np.savez_compressed(out/(name+'.npz'),q=pred)
        row=dict(name=name,scope='EXPLORATORY: reused pilot bank, full-batch fixed-policy objective; not confirmatory',
                 closure_calls=calls,seconds=time.perf_counter()-start,history=history,diagnostic=diag)
        results.append(row);p.dump(out/'PILOT.json',results);print(name,row,flush=True)

if __name__=='__main__':run()
