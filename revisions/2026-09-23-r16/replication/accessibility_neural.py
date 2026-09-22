"""Full-horizon R16 neural candidates with stopping-accessibility constraints.
The original economy and comparator action set are unchanged. The chosen
portfolio vanishes at the upper wealth face. Certification is mathematical-real
with an explicit pre-distance output error contract, not deployed libm proof.
"""
from pathlib import Path
import sys,json,time,resource,hashlib,platform,argparse
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
OLD=ROOT/'revisions/2026-09-22-r14/replication'
sys.path.insert(0,str(OLD))
import torch
from torch import nn
from neural_economy import Net,freeze,serialize,load_model,hamiltonian

def actor_action(net,s):
    y=torch.tanh(net(s));dist=(2-s[:,2])/1.5
    return torch.stack((.425+.375*y[:,0],.2*y[:,1],dist*(.15+.65*y[:,2])),dim=-1)

def critic_value(net,s,all_faces=False):
    t,u,x=s.unbind(-1)
    B=(-torch.expm1(-12*(u-1.2)))*(-torch.expm1(-12*(2.8-u)))*(-torch.expm1(-4*(x-.5)))
    if all_faces:B=B*(-torch.expm1(-4*(2-x)))
    return -.02*(u-2)**2+.1*torch.log(x)+(1-t)*(-8+B*torch.nn.functional.softplus(net(s)[:,0]))

def jets(net,s,all_faces=False):
    v=critic_value(net,s,all_faces);g=torch.autograd.grad(v.sum(),s,create_graph=True)[0]
    gu=torch.autograd.grad(g[:,1].sum(),s,create_graph=True,retain_graph=True)[0]
    gx=torch.autograd.grad(g[:,2].sum(),s,create_graph=True,retain_graph=True)[0]
    return v,g,gu[:,1],gu[:,2],gx[:,2]

def states(n):
    z=torch.rand(n,3,dtype=torch.float64)
    # Predeclared extra mass near accessible faces, not a posteriori selection.
    m=n//4;faces=torch.arange(m)%3;r=torch.rand(m,dtype=torch.float64)*.06
    z[:m,1]=torch.where(faces==0,r,torch.where(faces==1,1-r,z[:m,1]))
    z[:m,2]=torch.where(faces==2,r,z[:m,2])
    return (torch.tensor([0,1.2,.5])+z*torch.tensor([1,1.6,1.5])).requires_grad_(True)

def train(out,seed,width,checkpoints=(800,2400),batch=128,all_faces=False):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    start=time.perf_counter();cpu=time.process_time()
    torch.set_num_threads(1);torch.set_default_dtype(torch.float64);torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True);np.random.seed(seed)
    a=Net(3,width).double();v=Net(1,width).double()
    with torch.no_grad():
        a.layers[-1].weight.mul_(.1);v.layers[-1].weight.mul_(.1)
        a.layers[-1].bias.copy_(torch.atanh(torch.tensor([(.75-.425)/.375,.5,-.15/.65])))
        v.layers[-1].bias.fill_(6.7)
    oa=torch.optim.Adam(a.parameters(),lr=.0002);ov=torch.optim.Adam(v.parameters(),lr=.0005)
    hist=[];paths=[]
    for step in range(1,max(checkpoints)+1):
        freeze(a,True);freeze(v,False)
        for _ in range(3):
            s=states(batch);j=jets(v,s,all_faces);ac=actor_action(a,s).detach()
            res=j[1][:,0]+hamiltonian(s,ac,j,2)-.04*j[0];loss=res.square().mean()
            if not torch.isfinite(loss):raise ArithmeticError('Nonfinite critic objective')
            ov.zero_grad();loss.backward();nn.utils.clip_grad_norm_(v.parameters(),20);ov.step()
        freeze(a,False);freeze(v,True)
        s=states(batch);j=tuple(q.detach() for q in jets(v,s,all_faces));obj=-hamiltonian(s,actor_action(a,s),j,2).mean()
        if not torch.isfinite(obj):raise ArithmeticError('Nonfinite actor objective')
        oa.zero_grad();obj.backward();nn.utils.clip_grad_norm_(a.parameters(),20);oa.step()
        if step%50==0 or step in checkpoints:
            hist.append({'step':step,'sample_residual_mse':float(loss.detach()),'actor_objective':float(obj.detach()),'wall_seconds':time.perf_counter()-start})
        if step in checkpoints:
            d={'version':'R16','seed':seed,'width':width,'step':step,'k':2,'actor':serialize(a),'critic':serialize(v),
               'all_faces_ablation':all_faces,'architecture':'accessible-face-softplus; wealth-distance portfolio',
               'training_wall_seconds':time.perf_counter()-start,'training_cpu_seconds':time.process_time()-cpu}
            p=out/f'network_step{step:04d}.json';p.write_text(json.dumps(d,indent=2)+'\n');paths.append(p)
            print(json.dumps({k:d[k] for k in ['seed','width','step','training_wall_seconds']}),flush=True)
    (out/'history.json').write_text(json.dumps(hist,indent=2)+'\n')
    (out/'resources.json').write_text(json.dumps({'status':'completed','wall_seconds':time.perf_counter()-start,
      'cpu_seconds':time.process_time()-cpu,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      'platform':platform.platform(),'torch_version':torch.__version__,'threads':1,'optimizer_restarts':0,
      'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')
    return paths

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--seed',type=int,required=True)
    p.add_argument('--width',type=int,default=16);p.add_argument('--steps',type=int,nargs='+',default=[800,2400]);p.add_argument('--all-faces',action='store_true')
    a=p.parse_args();train(a.out,a.seed,a.width,a.steps,all_faces=a.all_faces)
