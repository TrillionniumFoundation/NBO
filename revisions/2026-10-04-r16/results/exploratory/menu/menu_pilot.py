"""Exploratory finite quarterly capital menu; never confirmation data.

First-period consumption utility weight and adjustment cost vary; every task
shares exactly the same fixed reference-policy continuation after quarter one.
All candidate methods see the same primitive coefficients and label bank.
"""
from pathlib import Path
import json, math, sys, time
import numpy as np
import torch
from torch import nn
sys.dont_write_bytecode=True
sys.path.insert(0,'/workspace/scratch/f7129d88c27c/NBO/revisions/2026-10-04-r15/code')
import training_core as core
torch.set_num_threads(1);torch.set_default_dtype(torch.float64)
OUT=Path('/workspace/scratch/f7129d88c27c/r16-critic-design')

P=dict(T=2.,discount=.04,productivity=.1,coupling=.3,idiosyncratic_sigma=.6,
       common_sigma=.3,adjustment=.2,lower=.02,upper=2.,CHI=.1)
for name in ['common','bellman_study','tube_neural','tube_certificate','policy_certificate']:
    mod=sys.modules.get(name)
    if mod is not None and hasattr(mod,'P'):mod.P.update({k:v for k,v in P.items() if k!='CHI'})
d=10;steps=8;h=P['T']/steps;seed=380711
weights=core.training_weights(steps);B=torch.from_numpy(core.old.coupling(d))
ref=float(weights['M'][0]/h)
g=torch.Generator().manual_seed(seed)
def states(n):
    mean=torch.rand(n,1,generator=g)-.5
    spread=.5*torch.rand(n,1,generator=g)
    z=torch.randn(n,d,generator=g);z-=z.mean(1,keepdim=True);z/=z.square().mean(1,keepdim=True).sqrt()
    return mean+spread*z
def qbase(x):return -2*P['CHI']*math.exp(-P['discount']*P['T'])*(x[:,1:]-x[:,1:].mean(1,keepdim=True))
def post(y,a):return torch.cat([torch.full((len(y),1),h),y+h*core.drift(y,a,B,P)],1)
def labels(x,local_seed,nrep):
    gen=torch.Generator().manual_seed(local_seed);vals=[];qs=[];nodes=torch.zeros(len(x),dtype=torch.long)
    for r in range(nrep):
        if r%2==0:z=torch.randn(steps,len(x),d+1,generator=gen)
        else:z=-z
        v,q=core.postdecision_target(x,nodes,z,P,weights,B)
        vals.append(v);qs.append(q)
    return torch.stack(vals).mean(0),torch.stack(qs).mean(0)

class VectorCostate(nn.Module):
    def __init__(self):
        super().__init__();self.net=nn.Sequential(nn.Linear(d+1,32),nn.Tanh(),nn.Linear(32,32),nn.Tanh(),nn.Linear(32,d))
        nn.init.zeros_(self.net[-1].weight);nn.init.zeros_(self.net[-1].bias)
    def forward(self,x):return qbase(x)+(P['T']-x[:,:1])*self.net(x)

class TaskActor(nn.Module):
    def __init__(self):
        super().__init__();self.net=nn.Sequential(nn.Linear(d+2,32),nn.Tanh(),nn.Linear(32,32),nn.Tanh(),nn.Linear(32,d))
        nn.init.zeros_(self.net[-1].weight);nn.init.constant_(self.net[-1].bias,math.log((ref-.02)/(2-ref)))
    def forward(self,y,w,eta):return .02+1.98*torch.sigmoid(self.net(torch.cat([y,w,eta],1)))

def train_field(kind,x,target):
    torch.manual_seed(seed)
    model=core.SplitCritic(d,P,32,16,kind='postdecision',step=h) if kind=='nbo' else VectorCostate()
    pars=model.space.parameters() if kind=='nbo' else model.parameters()
    pars=list(pars);opt=torch.optim.Adam(pars,lr=.003)
    def pred(xx,graph=True):return d*core.first_jet(model,xx,create_graph=graph)[3] if kind=='nbo' else model(xx)
    t=time.perf_counter()
    for it in range(1200):
        ids=torch.randint(len(x),(128,),generator=g)
        loss=(pred(x[ids])-target[ids]).square().mean();opt.zero_grad();loss.backward();opt.step()
    opt=torch.optim.LBFGS(pars,max_iter=300,max_eval=400,line_search_fn='strong_wolfe',tolerance_grad=1e-10,tolerance_change=1e-12)
    def closure():
        opt.zero_grad();loss=(pred(x)-target).square().mean();loss.backward();return loss
    opt.step(closure)
    print(json.dumps(dict(event='field_fit',method=kind,seconds=time.perf_counter()-t,train_mse=float((pred(x,False).detach()-target).square().mean()))),flush=True)
    return model,pred

def task_objective(y,a,w,eta,continuation):
    # Current production is common across alternatives and omitted exactly.
    return weights['A'][0]*(w*torch.log(a).mean(1,keepdim=True)-eta/2*a.mean(1,keepdim=True).square())-weights['B'][0]*a.mean(1,keepdim=True)+continuation

def optimize_actions(y,w,eta,field=None,innovations=None):
    # Same open-loop action optimizer, terminal action guard and iterations.
    aa=nn.Parameter(torch.full((len(y),d),math.log((ref-.02)/(2-ref))))
    opt=torch.optim.Adam([aa],lr=.06)
    for it in range(180):
        a=.02+1.98*torch.sigmoid(aa);x=post(y,a)
        if field is not None:
            q=field(x,False).detach()
            surrogate=-h*(q*a).mean(1,keepdim=True)
        else:
            # Different actions require different recurrences; innovations
            # remain cached and identical over every optimizer iteration.
            surrogate=continuation_differentiable(x,innovations)
        loss=-task_objective(y,a,w,eta,surrogate).mean();opt.zero_grad();loss.backward();opt.step()
    return (.02+1.98*torch.sigmoid(aa)).detach()

def continuation_differentiable(postx,zbank):
    ans=0.
    for z in zbank:
        y=postx[:,1:]+math.sqrt(h)*(P['idiosyncratic_sigma']*z[0,:,:d]+P['common_sigma']*z[0,:,d:])
        value=torch.zeros(len(y),1)
        for k in range(1,steps):
            a=weights['M'][k]/h
            production=P['coupling']*torch.tanh(y@B.T)
            value=value+weights['B'][k]*(production.mean(1,keepdim=True)-a)
            value=value+weights['A'][k]*(torch.log(a)-P['adjustment']/2*a.square())
            noise=P['idiosyncratic_sigma']*z[k,:,:d]+P['common_sigma']*z[k,:,d:]
            y=y+h*core.drift(y,a,B,P)+math.sqrt(h)*noise
        value=value-P['CHI']*math.exp(-P['discount']*P['T'])*(y-y.mean(1,keepdim=True)).square().mean(1,keepdim=True)
        ans=ans+value/len(zbank)
    return ans

def noise_bank(n,local_seed,reps=4):
    gg=torch.Generator().manual_seed(local_seed);zs=[]
    for k in range(reps):
        if k%2==0:z=torch.randn(steps,n,d+1,generator=gg)
        else:z=-z
        zs.append(z)
    return zs

start=time.perf_counter();y=states(512)
a=.02+1.2*torch.rand(512,d,generator=g)
x=post(y,a)
v,q=labels(x,seed+1,4)
label_seconds=time.perf_counter()-start
nbo,nbo_field=train_field('nbo',x,q)
raw,raw_field=train_field('vector',x,q)

yt=states(32)
# All 9 economically distinct tasks are reused at every new initial state.
task=torch.tensor([(w,e) for w in [.8,1.,1.2] for e in [.1,.2,.4]])
ys=yt.repeat_interleave(9,0);ww=task[:,0].repeat(32)[:,None];ee=task[:,1].repeat(32)[:,None]
methods={};work={}
for name,field in [('nbo',nbo_field),('vector_costate',lambda xx,graph=True:raw(xx))]:
    t=time.perf_counter();methods[name]=optimize_actions(ys,ww,ee,field=field);work[name]=time.perf_counter()-t
    print(json.dumps(dict(event='actions',method=name,seconds=work[name])),flush=True)
t=time.perf_counter();bank=noise_bank(len(ys),seed+2,4)
methods['cached_raw_saa']=optimize_actions(ys,ww,ee,innovations=bank);work['cached_raw_saa']=time.perf_counter()-t
print(json.dumps(dict(event='actions',method='cached_raw_saa',seconds=work['cached_raw_saa'])),flush=True)

# Strong parameterized direct-policy comparator, one actor shared over all tasks.
# Training query states are the SAME 512 state rows used for continuation labels.
torch.manual_seed(seed);actor=TaskActor();opt=torch.optim.Adam(actor.parameters(),lr=.003)
task_ids=torch.randint(9,(len(y),),generator=g);tw=task[task_ids,:1];te=task[task_ids,1:]
direct_bank=noise_bank(len(y),seed+3,4)
t=time.perf_counter()
for it in range(1200):
    ids=torch.randint(len(y),(128,),generator=g)
    act=actor(y[ids],tw[ids],te[ids]);zz=[z[:,ids,:] for z in direct_bank]
    cont=continuation_differentiable(post(y[ids],act),zz)
    loss=-task_objective(y[ids],act,tw[ids],te[ids],cont).mean()
    opt.zero_grad();loss.backward();opt.step()
methods['materialized_dpo']=actor(ys,ww,ee).detach();work['materialized_dpo']=time.perf_counter()-t
print(json.dumps(dict(event='actions',method='materialized_dpo',seconds=work['materialized_dpo'])),flush=True)

# A cached Raw Hamiltonian actor shares every label and the whole task family.
# This removes the weak comparison with only online Monte Carlo candidates.
_,qref=labels(post(y,torch.full_like(y,ref)),seed+4,4)
torch.manual_seed(seed);ractor=TaskActor();opt=torch.optim.Adam(ractor.parameters(),lr=.003)
t=time.perf_counter()
for it in range(1200):
    ids=torch.randint(len(y),(128,),generator=g)
    act=ractor(y[ids],tw[ids],te[ids]);cont=-h*(qref[ids]*act).mean(1,keepdim=True)
    loss=-task_objective(y[ids],act,tw[ids],te[ids],cont).mean()
    opt.zero_grad();loss.backward();opt.step()
methods['materialized_raw_actor']=ractor(ys,ww,ee).detach();work['materialized_raw_actor']=time.perf_counter()-t
print(json.dumps(dict(event='actions',method='materialized_raw_actor',seconds=work['materialized_raw_actor'])),flush=True)

evalbank=noise_bank(len(ys),seed+100,64)
scores={};qq={}
for name,act in methods.items():
    with torch.no_grad():val=task_objective(ys,act,ww,ee,continuation_differentiable(post(ys,act),evalbank)).ravel().numpy()
    scores[name]=val
    print(json.dumps(dict(event='score',method=name,mean=float(val.mean()),action_min=float(act.min()),action_max=float(act.max()))),flush=True)
base=scores['nbo'];contrasts={}
for k,vv in scores.items():
    diff=base-vv;contrasts[k]=dict(mean=float(diff.mean()),min_task=float(diff.reshape(32,9).mean(0).min()),max_task=float(diff.reshape(32,9).mean(0).max()))
record=dict(scope='single prespecified exploratory menu pilot; no protected interval; no confirmatory claim',seed=seed,params=P,d=d,steps=steps,train_states=512,queries=len(ys),label_seconds=label_seconds,work_seconds=work,mean_payoffs={k:float(vv.mean()) for k,vv in scores.items()},nbo_minus=contrasts)
OUT.joinpath('MENU_EXPLORATORY_PILOT.json').write_text(json.dumps(record,indent=2)+'\n')
np.savez_compressed(OUT/'MENU_EXPLORATORY_PILOT.npz',**{f'payoff_{k}':v for k,v in scores.items()},**{f'actions_{k}':v.numpy() for k,v in methods.items()},states=ys.numpy(),tasks=np.column_stack([ww.numpy(),ee.numpy()]))
print(json.dumps(record),flush=True)
