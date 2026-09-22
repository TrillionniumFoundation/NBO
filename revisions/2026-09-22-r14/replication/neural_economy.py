"""Fresh economic PDE-residual adapter for the two-layer tanh NBO architecture.
Not a rerun of the historical external finite-step objective. The independent
interval audit, not a sampled training loss, determines the certificate.
"""
from __future__ import annotations
import argparse, json, time, resource, platform, os, hashlib
from pathlib import Path
import numpy as np
import torch
from torch import nn
DTYPE=torch.float64

class Net(nn.Module):
    def __init__(self,out:int,width:int=48):
        super().__init__()
        self.layers=nn.Sequential(nn.Linear(3,width),nn.Tanh(),nn.Linear(width,width),nn.Tanh(),nn.Linear(width,out))
    def forward(self,s):
        z=torch.stack((2*s[:,0]-1,(s[:,1]-2)/.8,(s[:,2]-1.25)/.75),dim=-1)
        return self.layers(z)

def actor_action(actor,s):
    a=torch.tanh(actor(s))
    return torch.stack((.425+.375*a[:,0],.2*a[:,1],.15+.65*a[:,2]),dim=-1)

def critic_value(critic,s):
    t,u,x=s.unbind(-1)
    return -.02*(u-2)**2+.1*torch.log(x)+(1-t)*critic(s)[:,0]

def jets(critic,s):
    v=critic_value(critic,s)
    g=torch.autograd.grad(v.sum(),s,create_graph=True)[0]
    gu=torch.autograd.grad(g[:,1].sum(),s,create_graph=True,retain_graph=True)[0]
    gx=torch.autograd.grad(g[:,2].sum(),s,create_graph=True,retain_graph=True)[0]
    return v,g,gu[:,1],gu[:,2],gx[:,2]

def hamiltonian(s,a,j,k):
    v,g,vuu,vux,vxx=j;u=s[:,1];x=s[:,2];c,theta,p=a.unbind(-1)
    utility=-torch.exp((u-1)*(-torch.log(c)))/(u-1)-k*theta**2/2
    return theta*g[:,1]+((.02+.06*p)*x-c)*g[:,2]+.00125*vuu+.02*p**2*x*x*vxx-.0025*p*x*vux+utility

def states(n):
    lo=torch.tensor([0,1.2,.5],dtype=DTYPE);w=torch.tensor([1,1.6,1.5],dtype=DTYPE)
    return (lo+torch.rand(n,3,dtype=DTYPE)*w).requires_grad_(True)

def freeze(net,flag):
    for p in net.parameters():p.requires_grad_(not flag)

def serialize(net):
    return [{'weight':m.weight.detach().cpu().tolist(),'bias':m.bias.detach().cpu().tolist()}
            for m in net.layers if isinstance(m,nn.Linear)]

def load_model(path):
    d=json.loads(Path(path).read_text());a=Net(3,d['width']).double();v=Net(1,d['width']).double()
    for net,key in ((a,'actor'),(v,'critic')):
        for layer,rec in zip([m for m in net.layers if isinstance(m,nn.Linear)],d[key]):
            with torch.no_grad():
                layer.weight.copy_(torch.tensor(rec['weight'],dtype=DTYPE));layer.bias.copy_(torch.tensor(rec['bias'],dtype=DTYPE))
    return a,v,d

def train(out,steps,width,seed,batch):
    start=time.perf_counter();cpu=time.process_time();out.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(1);torch.set_default_dtype(DTYPE);torch.manual_seed(seed);np.random.seed(seed);torch.use_deterministic_algorithms(True)
    protocol={'version':'R14','model':'original stopped preference-adjustment economy','k':2,'seed':seed,'width':width,
      'hidden_layers':2,'activation':'tanh','dtype':'float64','checkpoints':steps,'batch':batch,'critic_steps_per_actor':3,
      'critic_lr':.0005,'actor_lr':.0002,'boundary_penalty':.025,'optimizer':'Adam','threads':1,
      'initialization':'fresh PyTorch initialization; output heads rescaled .1',
      'historical_scope':'same two-hidden-layer tanh architecture; new economic PDE-residual adapter, NOT the external finite-step objective',
      'training_stopping':'fixed iteration counts; no validation-target stopping','inherited_proof_objects':False,
      'acceptance':'Only enclosed stopped residual/trace/action bounds certify performance.'}
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    actor=Net(3,width).double();critic=Net(1,width).double()
    with torch.no_grad():
        actor.layers[-1].weight.mul_(.1);critic.layers[-1].weight.mul_(.1)
        actor.layers[-1].bias.copy_(torch.atanh(torch.tensor([(.75-.425)/.375,.5,-.15/.65])))
        critic.layers[-1].bias.fill_(-1.3)
    oa=torch.optim.Adam(actor.parameters(),lr=protocol['actor_lr']);ov=torch.optim.Adam(critic.parameters(),lr=protocol['critic_lr'])
    hist=[];snaps=[];k=2.
    for step in range(1,max(steps)+1):
        freeze(actor,True);freeze(critic,False)
        for _ in range(3):
            s=states(batch);j=jets(critic,s);a=actor_action(actor,s).detach()
            residual=j[1][:,0]+hamiltonian(s,a,j,k)-.04*j[0]
            b=states(max(16,batch//4)).detach().clone();face=torch.arange(len(b))%4
            b[face==0,1]=1.2;b[face==1,1]=2.8;b[face==2,2]=.5;b[face==3,2]=2.
            trace=(1-b[:,0])*(critic(b)[:,0]+8)
            loss=residual.square().mean()+protocol['boundary_penalty']*trace.square().mean()
            if not torch.isfinite(loss):raise ArithmeticError('Nonfinite critic loss')
            ov.zero_grad();loss.backward();torch.nn.utils.clip_grad_norm_(critic.parameters(),20);ov.step()
        freeze(actor,False);freeze(critic,True)
        s=states(batch);j=tuple(q.detach() for q in jets(critic,s));a=actor_action(actor,s)
        improvement=-hamiltonian(s,a,j,k).mean()
        if not torch.isfinite(improvement):raise ArithmeticError('Nonfinite actor loss')
        oa.zero_grad();improvement.backward();torch.nn.utils.clip_grad_norm_(actor.parameters(),20);oa.step()
        if step%10==0 or step in steps:
            hist.append({'step':step,'critic_objective':float(loss.detach()),'sample_residual_mse':float(residual.square().mean().detach()),
             'sample_boundary_mse':float(trace.square().mean().detach()),'actor_objective':float(improvement.detach()),
             'wall_seconds_from_start':time.perf_counter()-start,'process_seconds_from_start':time.process_time()-cpu})
        if step in steps:
            payload={'format':'binary64 weights in decimal round-trip JSON','version':'R14','seed':seed,'step':step,'width':width,'k':2,
              'actor':serialize(actor),'critic':serialize(critic),'protocol_sha256':hashlib.sha256((out/'protocol.json').read_bytes()).hexdigest(),
              'training_wall_seconds':time.perf_counter()-start,'training_process_seconds':time.process_time()-cpu,
              'model_constants':'exact decimal in theorem; nearest binary64 in training; rational enclosures in audit'}
            p=out/f'network_step{step:04d}.json';p.write_text(json.dumps(payload,indent=2)+'\n')
            snaps.append({'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'step':step})
            print(json.dumps(hist[-1]),flush=True)
    record={'status':'completed','wall_seconds':time.perf_counter()-start,'process_seconds':time.process_time()-cpu,
      'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'hardware':platform.platform(),'processor':platform.processor(),
      'logical_cpu_count':os.cpu_count(),'torch_threads':torch.get_num_threads(),'torch_version':torch.__version__,'numpy_version':np.__version__,
      'gpu_used':False,'snapshots':snaps,'failed_iterations':0,'optimizer_restarts':0,
      'scope':'Entire fresh run after process entry; interpreter startup/import cost separately recorded by shell time.'}
    (out/'history.json').write_text(json.dumps(hist,indent=2)+'\n');(out/'resource_ledger.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--steps',nargs='+',type=int,default=[100,300,800]);ap.add_argument('--width',type=int,default=48);ap.add_argument('--seed',type=int,default=1401);ap.add_argument('--batch',type=int,default=128)
    args=ap.parse_args();train(args.out,args.steps,args.width,args.seed,args.batch)
