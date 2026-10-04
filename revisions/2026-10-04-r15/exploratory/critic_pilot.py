"""Exploratory R15 frozen-policy diagnosis. Never a confirmatory experiment.

All outputs are scratch-only. Original economic coefficients and policy are
unchanged. No policies are selected, improved, or evaluated on the final bank.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,math,sys,time
from pathlib import Path
import numpy as np
import torch
from torch import nn

sys.dont_write_bytecode=True
ROOT=Path('/workspace/scratch/f7129d88c27c/NBO')
sys.path.insert(0,str(ROOT/'revisions/2026-10-04-r12/code'))
import common as c
old=c.old; P=dict(c.P)
torch.set_default_dtype(torch.float64)
torch.set_num_threads(1)

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')

def baseline(tx):
    t,y=tx[:,:1],tx[:,1:];tau=1-t;e=torch.exp(-P['discount']*tau)
    w=(1-e)/P['discount']+e;mu=y.mean(1,keepdim=True)
    return w*mu-c.CHI*e*((y-mu)**2).mean(1,keepdim=True)

def model_drift(y,m,B):
    return P['productivity']+P['coupling']*torch.tanh(y@B.T)-m-(P['idiosyncratic_sigma']**2+P['common_sigma']**2)/2

class Anchor(nn.Module):
    def forward(self,tx):return old.schedule(tx[:,:1]).expand_as(tx[:,1:])

def mlp(inputs,width):
    m=nn.Sequential(nn.Linear(inputs,width),nn.Tanh(),nn.Linear(width,width),nn.Tanh(),nn.Linear(width,1))
    nn.init.zeros_(m[-1].weight);nn.init.zeros_(m[-1].bias)
    return m

class SplitCritic(nn.Module):
    def __init__(self,d,width=32):
        super().__init__();self.d=d;self.time=mlp(1,16);self.space=mlp(d+1,width)
    def forward(self,tx):
        return baseline(tx)+(1-tx[:,:1])*(self.time(tx[:,:1])+self.space(tx)/self.d)

class CoupledCritic(nn.Module):
    def __init__(self,d,width=16):
        super().__init__();self.time=mlp(1,16);self.space=mlp(4,width)
        self.register_buffer('B',torch.tensor(old.coupling(d)))
    def forward(self,tx):
        t,y=tx[:,:1],tx[:,1:];n,d=y.shape
        z=y@self.B.T;mu=y.mean(1,keepdim=True)
        features=torch.stack([t.expand_as(y),y,z,mu.expand_as(y)],-1)
        residual=self.space(features.reshape(n*d,4)).reshape(n,d).mean(1,keepdim=True)
        return baseline(tx)+(1-t)*(self.time(t)+residual)

def occupation(actor,d,n,seed,steps=64):
    """One discounted-time state per independent candidate trajectory."""
    g=torch.Generator().manual_seed(seed)
    support=torch.from_numpy(c.profiles(d));y=support[torch.randint(9,(n,),generator=g)].clone()
    times=torch.arange(steps)/steps
    weights=torch.exp(-P['discount']*times);weights/=weights.sum()
    pick=torch.multinomial(weights,n,replacement=True,generator=g)
    out=torch.zeros(n,d+1);B=torch.from_numpy(old.coupling(d));h=1/steps
    with torch.no_grad():
        for k in range(steps):
            x=torch.cat([torch.full((n,1),k*h),y],1)
            use=pick==k;out[use]=x[use]
            m=actor(x);z=torch.randn(n,d+1,generator=g)
            noise=P['idiosyncratic_sigma']*z[:,:d]+P['common_sigma']*z[:,d:]
            y=y+h*model_drift(y,m,B)+math.sqrt(h)*noise
    return out

def target(actor,x,B,z):
    n,d=len(x),B.shape[0];steps=len(z)
    start=x.detach().clone().requires_grad_(True);t=start[:,:1];y=start[:,1:]
    h=(1-t)/steps;reward=torch.zeros(n,1)
    for k in range(steps):
        m=actor(torch.cat([t+k*h,y],1))
        reward=reward+torch.exp(-P['discount']*k*h)*h*old.flow(y,m)
        noise=P['idiosyncratic_sigma']*z[k,:,:d]+P['common_sigma']*z[k,:,d:]
        y=y+h*model_drift(y,m,B)+torch.sqrt(h)*noise
    reward=reward+torch.exp(-P['discount']*(1-t))*old.terminal(y)
    q=d*torch.autograd.grad(reward.sum(),start)[0][:,1:]
    return reward.detach(),q.detach()

def sample_targets(actor,x,B,seed,reps,steps,antithetic=False):
    g=torch.Generator().manual_seed(seed);values=[];costates=[]
    for r in range(reps):
        if not antithetic or r%2==0:
            z=torch.randn(steps,len(x),B.shape[0]+1,generator=g)
        else:z=-z
        v,q=target(actor,x,B,z);values.append(v);costates.append(q)
    return torch.stack(values),torch.stack(costates)

def predict(critic,x):
    with torch.enable_grad():
        _,v,_,p=old.first_jet(critic,x)
    return v.detach(),p.detach()*x.shape[1].__sub__(1)

def diagnostic(critic,x,values,q,rawq):
    d=x.shape[1]-1;v,p=predict(critic,x);ref=q.mean(0)
    mse=float((p-ref).square().mean());noise=float(q.var(0,unbiased=True).mean()/len(q))
    optimal=old.greedy(ref/d,x[:,:1],.1);predaction=old.greedy(p/d,x[:,:1],.1)
    H=lambda a: torch.log(a).mean(1)-P['adjustment']/2*a.mean(1).square()-(ref*a).mean(1)
    gap=float((H(optimal)-H(predaction)).mean())
    row=dict(costate_mse=mse,reference_variance=noise,costate_mse_mc_debiased=mse-noise,
             value_mse=float((v-values.mean(0)).square().mean()),hamiltonian_gap=gap)
    for name,r in rawq.items():
        act=old.greedy(r/d,x[:,:1],.1)
        row[name+'_mse']=float((r-ref).square().mean())
        row[name+'_hamiltonian_gap']=float((H(optimal)-H(act)).mean())
    return row,p.numpy()

def gradient_diagnosis(critic,x,v,q):
    critic=copy.deepcopy(critic);params=list(critic.parameters());_,pred,_,p=old.first_jet(critic,x)
    lv=.05*(pred-v).square().mean();lq=((x.shape[1]-1)*p-q).square().mean()
    gv=torch.autograd.grad(lv,params,retain_graph=True,allow_unused=True)
    gq=torch.autograd.grad(lq,params,allow_unused=True)
    gv=torch.cat([(torch.zeros_like(p) if g is None else g).ravel() for p,g in zip(params,gv)])
    gq=torch.cat([(torch.zeros_like(p) if g is None else g).ravel() for p,g in zip(params,gq)])
    return dict(weighted_value_loss=float(lv.detach()),costate_loss=float(lq.detach()),
                value_gradient_norm=float(gv.norm()),costate_gradient_norm=float(gq.norm()),
                cosine=float(gv@gq/(gv.norm()*gq.norm())))

def run(d,seed=7919,updates=600,tag='',anchor=False,names=None):
    out=Path('/workspace/scratch/f7129d88c27c/r15-exploration')/(f'd{d}_s{seed}'+('_'+tag if tag else ''))
    out.mkdir(parents=True,exist_ok=True)
    weight=ROOT/f'revisions/2026-10-04-r13/results/ubuntu24_d{d}_s{seed}/nbo_d{d}_s{seed}_fixed_nbo_k80.pt'
    begin=time.perf_counter();actor,online,state=old.load(weight)
    if anchor:actor=Anchor()
    for p in actor.parameters():p.requires_grad_(False)
    B=torch.from_numpy(old.coupling(d))
    x=occupation(actor,d,1024,151003001+d);test=occupation(actor,d,128,151013001+d)
    vb,qb=sample_targets(actor,x,B,151023001+d,4,32,True)
    vf,qf=sample_targets(actor,test,B,151033001+d,32,128,False)
    vr,qr=sample_targets(actor,test,B,151043001+d,4,32,True)
    raw={'raw1':qr[0],'raw_antithetic2':qr[:2].mean(0),'raw_antithetic4':qr.mean(0)}
    baseline_result,pred=diagnostic(online,test,vf,qf,raw)
    diagnosis=gradient_diagnosis(online,x[:128],vb[0,:128],qb[0,:128])
    configurations=[('replay_online_init',lambda:copy.deepcopy(online),.05),
                    ('replay_fresh',lambda:old.Critic(d,32),.05),
                    ('replay_costate_only',lambda:old.Critic(d,32),0.),
                    ('replay_split_scaled',lambda:SplitCritic(d,32),.05),
                    ('replay_coupled',lambda:CoupledCritic(d,16),.05),
                    ('split_blocked_value',lambda:SplitCritic(d,32),-1.),
                    ('coupled_blocked_value',lambda:CoupledCritic(d,16),-1.)]
    if names:configurations=[x for x in configurations if x[0] in names.split(',')]
    record=dict(scope='EXPLORATORY ONLY: frozen historical policy, fresh scratch occupation/rollout banks; no economic final-bank inference or design selection guarantee',
                dimension=d,training_seed=seed,historical_weight=str(weight.relative_to(ROOT)),
                primitive_parameters=P,actor='schedule' if anchor else 'historical_nbo_k80',
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                historical_weight_sha256=hashlib.sha256(weight.read_bytes()).hexdigest(),
                bank=dict(train_states=1024,train_rollouts_per_state=4,antithetic=True,train_steps=32,
                          diagnostic_states=128,reference_replicates=32,reference_steps=128,
                          occupation_steps=64,distribution='one discounted-grid-time state per independent candidate trajectory'),
                updates=updates,batch=128,lr=.002,baseline=baseline_result,loss_gradient_diagnosis=diagnosis,
                data_generation_seconds=time.perf_counter()-begin,variants=[])
    dump(out/'PILOT.json',record)
    np.savez_compressed(out/'BANKS.npz',train_states=x.numpy(),train_values=vb.numpy(),train_q=qb.numpy(),
                        diagnostic_states=test.numpy(),fine_values=vf.numpy(),fine_q=qf.numpy(),raw_q=qr.numpy(),online_q=pred)
    for name,make,valueweight in configurations:
        torch.manual_seed(151053001+d);t0=time.perf_counter();critic=make();opt=torch.optim.Adam(critic.space.parameters() if valueweight<0 else critic.parameters(),lr=.002)
        if valueweight<0:timeopt=torch.optim.Adam(critic.time.parameters(),lr=.002)
        g=torch.Generator().manual_seed(151063001+d);history=[]
        for k in range(1,updates+1):
            ids=torch.randint(len(x),(128,),generator=g);_,v,_,p=old.first_jet(critic,x[ids])
            lv=(v-vb.mean(0)[ids]).square().mean();lq=(d*p-qb.mean(0)[ids]).square().mean()
            loss=max(0,valueweight)*lv+lq;opt.zero_grad(set_to_none=True);loss.backward();opt.step()
            if valueweight<0:
                xx=x[ids];tau=1-xx[:,:1]
                with torch.no_grad():spatial=critic(xx)-baseline(xx)-tau*critic.time(xx[:,:1])
                v=baseline(xx)+spatial+tau*critic.time(xx[:,:1]);lv=(v-vb.mean(0)[ids]).square().mean()
                timeopt.zero_grad(set_to_none=True);lv.backward();timeopt.step()
            if k%200==0 or k==updates:
                diag,pred=diagnostic(critic,test,vf,qf,raw)
                history.append(dict(iteration=k,seconds=time.perf_counter()-t0,value_loss=float(lv.detach()),costate_loss=float(lq.detach()),diagnostic=diag))
        torch.save(critic.state_dict(),out/(name+'.pt'))
        np.savez_compressed(out/(name+'_prediction.npz'),q=pred)
        row=dict(name=name,value_weight=valueweight,seconds=time.perf_counter()-t0,parameters=sum(p.numel() for p in critic.parameters()),history=history)
        record['variants'].append(row);dump(out/'PILOT.json',record)
        print(d,name,history[-1]['diagnostic'],flush=True)
    record['total_seconds']=time.perf_counter()-begin;dump(out/'PILOT.json',record)
    print('baseline',d,baseline_result,'gradients',diagnosis,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dimension',type=int,default=20);p.add_argument('--updates',type=int,default=600)
    p.add_argument('--tag',default='');p.add_argument('--anchor',action='store_true');p.add_argument('--names')
    p.add_argument('--sigma-idio',type=float,default=.15);p.add_argument('--sigma-common',type=float,default=.1)
    a=p.parse_args();P['idiosyncratic_sigma']=a.sigma_idio;P['common_sigma']=a.sigma_common
    run(a.dimension,updates=a.updates,tag=a.tag,anchor=a.anchor,names=a.names)
