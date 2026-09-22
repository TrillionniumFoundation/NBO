"""R8 paired nonconvex-control comparison against PINNED author SOC-MartNet.

No changes to the external solver. Model/network adapters and a scheduler
that stops after a completed update are the entire integration surface.
The experiment estimates realized cost differences, NOT optimality losses.
"""
from __future__ import annotations
import argparse,copy,hashlib,io,json,math,pathlib,sys,time,contextlib
import numpy as np
from scipy.stats import t as student_t
import torch
from torch import nn
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=ROOT/'revisions/2026-09-22-r8/results'
torch.set_num_threads(1)
torch.set_default_dtype(torch.float32)
DT=1/16; SIGMA=math.sqrt(2)*.4

def cost(a):
    return a.square().mean(-1,keepdim=True)+.3*torch.sin(a.sum(-1,keepdim=True))+.1*torch.sin(a).square().mean(-1,keepdim=True)
def terminal(x):
    return (x-.5).square().mean(-1,keepdim=True)+.2*torch.cos(x.sum(-1,keepdim=True)/math.sqrt(x.shape[-1]))
class Net(nn.Module):
    def __init__(self,d,actor):
        super().__init__(); self.actor=actor
        self.net=nn.Sequential(nn.Linear(d+1,48),nn.Tanh(),nn.Linear(48,48),nn.Tanh(),nn.Linear(48,d if actor else 1))
    def forward(self,t,x):
        t=t+torch.zeros_like(x[...,:1]); y=self.net(torch.cat((t,x),-1))
        return torch.tanh(y) if self.actor else terminal(x)+(1-t)*y

def digest(model):
    return hashlib.sha256(b''.join(v.detach().cpu().numpy().tobytes() for v in model.state_dict().values())).hexdigest()
class BudgetStop(Exception): pass
class Budget:
    def __init__(self,start,seconds): self.start=start;self.seconds=seconds;self.steps=0
    def step(self):
        self.steps+=1
        if time.perf_counter()-self.start>=self.seconds: raise BudgetStop

def train_soc(a,v,d,seconds,source):
    sys.path.insert(0,str(source/'code/SOCMartNet-v3-refactored'))
    from socmartnet.solver import SOCMartNet
    from socmartnet.networks import test_net
    rho=test_net(d,600)
    opts=[torch.optim.RMSprop(a.parameters(),lr=.003/math.sqrt(d)),
          torch.optim.RMSprop(v.parameters(),lr=.003/math.sqrt(d)),
          torch.optim.RMSprop(rho.parameters(),lr=.01)]
    def H(t,x,u,val,vx,vxx): return 2*(u*vx.squeeze(-2)).sum(-1,keepdim=True)+cost(u)
    solver=SOCMartNet(torch.tensor(DT),lambda t,x:torch.zeros_like(x),
        lambda t,x:SIGMA*torch.ones_like(x),H,terminal,d,t0=torch.tensor(0.))
    start=time.perf_counter(); budget=Budget(start,seconds)
    log=io.StringIO()
    with contextlib.redirect_stdout(log):
        try:
            solver.train((a,v,rho),opts,(None,None,budget),10**9,torch.zeros(1024,d),[64],
                rank=0,lam0=10,N=16,err_func=lambda:torch.tensor(float('nan')),
                log_gap=1000,J=2,K=1,delta4=10,lam_bar=1000,renew_frac=0)
        except BudgetStop: pass
    a.eval();v.eval();rho.eval()
    return {'training_seconds':time.perf_counter()-start,'outer_updates':budget.steps,
        'adversary_parameters':sum(p.numel() for p in rho.parameters()),'log':log.getvalue()},rho

def train_nbo(a,v,d,seconds):
    oa=torch.optim.Adam(a.parameters(),lr=.003); ov=torch.optim.Adam(v.parameters(),lr=.003)
    start=time.perf_counter(); steps=0; history=[]
    while time.perf_counter()-start<seconds:
        for _ in range(3):
            t=torch.randint(0,16,(256,1))*DT
            x=SIGMA*torch.sqrt(t)*torch.randn(256,d)
            with torch.no_grad():
                aa=a(t,x); xn=x[:,None,:]+2*aa[:,None,:]*DT+SIGMA*math.sqrt(DT)*torch.randn(256,4,d)
                target=cost(aa)*DT+v(t[:,None,:]+DT,xn).mean(1)
            pred=v(t,x); loss=(pred-target).square().mean()
            ov.zero_grad();loss.backward();ov.step()
        t=torch.randint(0,16,(256,1))*DT; x=SIGMA*torch.sqrt(t)*torch.randn(256,d)
        ov.zero_grad(set_to_none=True)
        for p in v.parameters(): p.requires_grad_(False)
        aa=a(t,x); xn=x[:,None,:]+2*aa[:,None,:]*DT+SIGMA*math.sqrt(DT)*torch.randn(256,4,d)
        objective=(cost(aa)*DT+v(t[:,None,:]+DT,xn).mean(1)).mean()
        oa.zero_grad(); objective.backward();oa.step()
        assert all(p.grad is None for p in v.parameters())
        for p in v.parameters():p.requires_grad_(True)
        steps+=1
        if steps%100==0: history.append([steps,float(loss.detach()),float(objective.detach())])
    a.eval();v.eval()
    return {'training_seconds':time.perf_counter()-start,'outer_updates':steps,'history':history}

@torch.no_grad()
def rollout(actor,noise,coarse=False):
    M,P,d=noise.shape
    increments=noise.reshape(M//2,2,P,d).sum(1) if coarse else noise
    h=1/increments.shape[0];x=torch.zeros(P,d); value=torch.zeros(P,1)
    for n,dw in enumerate(increments):
        a=actor(torch.full((P,1),n*h),x)
        value+=h*cost(a);x+=2*h*a+SIGMA*dw
    return (value+terminal(x)).squeeze(-1).numpy()

def run(d,seed,source,seconds=10,paths=4096):
    torch.manual_seed(seed); a0=Net(d,True);v0=Net(d,False)
    initial={'actor':digest(a0),'critic':digest(v0)}; models={};results={}
    for method in ['nbo','soc']:
        torch.manual_seed(seed+100000); a=copy.deepcopy(a0);v=copy.deepcopy(v0)
        start=time.perf_counter()
        if method=='nbo': info=train_nbo(a,v,d,seconds);extra={}
        else:
            info,rho=train_soc(a,v,d,seconds,source);extra={'adversary':rho.state_dict()}
        info['setup_and_training_seconds']=time.perf_counter()-start
        info['actor_parameters']=sum(p.numel() for p in a.parameters())
        info['critic_parameters']=sum(p.numel() for p in v.parameters())
        assert all(torch.isfinite(p).all() for p in a.parameters())
        torch.save({'actor':a.state_dict(),'critic':v.state_dict(),**extra},OUT/f'external_d{d}_s{seed}_{method}.pt')
        models[method]=a;results[method]=info
    start=time.perf_counter();torch.manual_seed(12000+seed)
    noise=torch.randn(128,paths,d)/math.sqrt(128)
    arrays={}
    for method,model in models.items():
        arrays[method+'_128']=rollout(model,noise)
        arrays[method+'_64']=rollout(model,noise,True)
        results[method]['mean_cost_128']=float(arrays[method+'_128'].mean(dtype=np.float64))
        results[method]['mean_cost_64']=float(arrays[method+'_64'].mean(dtype=np.float64))
        results[method]['path_standard_error']=float(arrays[method+'_128'].std(ddof=1,dtype=np.float64)/math.sqrt(paths))
        results[method]['mesh_change']=results[method]['mean_cost_128']-results[method]['mean_cost_64']
    diff=arrays['nbo_128'].astype(float)-arrays['soc_128'].astype(float)
    result={'dimension':d,'seed':seed,'initial_state_hashes':initial,'methods':results,
        'paired_difference':float(diff.mean()),'paired_path_standard_error':float(diff.std(ddof=1)/math.sqrt(paths)),
        'audit_seconds':time.perf_counter()-start,'audit_paths':paths,
        'estimand':'NBO minus SOC-MartNet realized cost; negative favors NBO',
        'scope':'adapter comparison at the declared CPU budget, not an optimality certificate'}
    np.savez_compressed(OUT/f'external_d{d}_s{seed}_paths.npz',**arrays)
    (OUT/f'external_d{d}_s{seed}.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['dimension','seed','paired_difference','audit_seconds']}),flush=True)
    return result

def summarize():
    rows=[]
    for d in [8,16]:
        files=[OUT/f'external_d{d}_s{s}.json' for s in range(400,406)]
        if not all(f.exists() for f in files):continue
        rr=[json.loads(f.read_text()) for f in files];diff=np.array([r['paired_difference'] for r in rr])
        half=float(student_t.ppf(.975,5)*diff.std(ddof=1)/math.sqrt(6))
        rows.append({'dimension':d,'seeds':6,'paired_mean':float(diff.mean()),'paired_t_95':[float(diff.mean()-half),float(diff.mean()+half)],
          'raw_differences':diff.tolist(),'mean_nbo_cost':float(np.mean([r['methods']['nbo']['mean_cost_128'] for r in rr])),
          'mean_soc_cost':float(np.mean([r['methods']['soc']['mean_cost_128'] for r in rr])),
          'mean_nbo_mesh_change':float(np.mean([r['methods']['nbo']['mesh_change'] for r in rr])),
          'mean_soc_mesh_change':float(np.mean([r['methods']['soc']['mesh_change'] for r in rr])),
          'max_paired_path_se':max(r['paired_path_standard_error'] for r in rr)})
    (OUT/'external_summary.json').write_text(json.dumps({'rows':rows,'inference':'Paired Student interval across six independent training/audit seeds; finite-sample Gaussian approximation, not a certified coverage guarantee. Mesh changes are diagnostics, not error bounds.'},indent=2)+'\n')
    print(rows)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=pathlib.Path,required=True)
    ap.add_argument('--seed',type=int);ap.add_argument('--dimension',type=int,default=8)
    ap.add_argument('--seconds',type=float,default=10);ap.add_argument('--paths',type=int,default=4096)
    args=ap.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    if args.seed is not None:run(args.dimension,args.seed,args.source,args.seconds,args.paths)
    summarize()
