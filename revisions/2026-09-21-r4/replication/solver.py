"""NBO R4: independent NumPy control reference and separated PyTorch NBO.

The finite model is a killed, correlated Euler/quadrature chain, NOT a
projection of an allegedly viable diffusion. Scientific timings are metadata.
The critic sees fixed-policy targets, never optimal reference values.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import copy, hashlib, itertools, json, math, time
import numpy as np
import torch
from torch import nn

torch.set_num_threads(1)
BASE = Path(__file__).resolve().parents[1]

@dataclass(frozen=True)
class Config:
    n: int = 12
    nu: int = 25
    nx: int = 31
    na: int = 5
    k: float = 2.0
    fee: float = 8.0
    rho: float = .04
    r: float = .02
    excess: float = .06
    su: float = .05
    sx: float = .2
    corr: float = -.25
    T: float = 1.0
    ulo: float = 1.2
    uhi: float = 2.8
    xlo: float = .5
    xhi: float = 2.0

    def __post_init__(self):
        if min(self.n, self.nu, self.nx, self.na) < 2 or self.k <= 0:
            raise ValueError('positive cost and at least two points required')
        if not abs(self.corr) < 1:
            raise ValueError('correlation must be interior')

    @property
    def dt(self): return self.T/self.n


def actions(cfg: Config):
    return np.array(list(itertools.product(np.linspace(.05,.8,cfg.na),
          np.linspace(-.2,.2,cfg.na),np.linspace(-.5,.8,cfg.na))))


def states(cfg: Config):
    u=np.linspace(cfg.ulo,cfg.uhi,cfg.nu); x=np.linspace(cfg.xlo,cfg.xhi,cfg.nx)
    s=np.stack(np.meshgrid(u,x,indexing='ij'),-1).reshape(-1,2)
    boundary=np.any((s==[cfg.ulo,cfg.xlo])|(s==[cfg.uhi,cfg.xhi]),axis=-1)
    return s,boundary


def settlement(t, s, cfg):
    return -.02*(s[...,0]-2)**2+.1*np.log(s[...,1])-cfg.fee*(cfg.T-t)


def transition_numpy(s, a, cfg):
    """Broadcast s(...,2), a(...,3); return four next points and exit fractions.
    An exit is a liquidation at the FIRST straight-segment intersection.
    No state is reset and allowed to consume again.
    """
    z=np.array([[-1.,-1.],[-1.,1.],[1.,-1.],[1.,1.]])
    s,a=np.broadcast_arrays(s[...,None,:],np.zeros(a.shape[:-1]+(1,2))) [0], a
    u,x=s[...,0],s[...,1]
    c,th,p=[a[...,i,None] for i in range(3)]
    b=(cfg.r+cfg.excess*p)*x-c
    du=th*cfg.dt+cfg.su*np.sqrt(cfg.dt)*z[:,0]
    dx=b*cfg.dt+cfg.sx*p*x*np.sqrt(cfg.dt)*(cfg.corr*z[:,0]+np.sqrt(1-cfg.corr**2)*z[:,1])
    du,dx=np.broadcast_arrays(du,dx)
    inc=np.stack([du,dx],-1)
    lo=np.array([cfg.ulo,cfg.xlo]); hi=np.array([cfg.uhi,cfg.xhi])
    y=s+inc
    frac=np.ones(y.shape[:-1])
    for j in range(2):
        d=inc[...,j]
        safe=np.where(abs(d)>1e-15,d,1.)
        fj=np.where(y[...,j]<lo[j],(lo[j]-s[...,j])/safe,
                    np.where(y[...,j]>hi[j],(hi[j]-s[...,j])/safe,1.))
        frac=np.minimum(frac,fj)
    frac=np.clip(frac,0.,1.)
    hit=s+frac[...,None]*inc
    return hit,frac,inc


def interp(v, y, cfg):
    """Positive bilinear interpolation, only on surviving/exit points."""
    f=(y-np.array([cfg.ulo,cfg.xlo]))/np.array([cfg.uhi-cfg.ulo,cfg.xhi-cfg.xlo])
    f=f*np.array([cfg.nu-1,cfg.nx-1]); i=np.floor(f).astype(int)
    i[...,0]=np.clip(i[...,0],0,cfg.nu-2); i[...,1]=np.clip(i[...,1],0,cfg.nx-2)
    w=np.clip(f-i,0,1); iu,ix=i[...,0],i[...,1]
    vv=v.reshape(cfg.nu,cfg.nx)
    return ((1-w[...,0])*((1-w[...,1])*vv[iu,ix]+w[...,1]*vv[iu,ix+1])+
            w[...,0]*((1-w[...,1])*vv[iu+1,ix]+w[...,1]*vv[iu+1,ix+1]))


def q_numpy(s,a,vnext,t,cfg,pre=None):
    hit,frac,_=transition_numpy(s,a,cfg) if pre is None else pre
    dtau=cfg.dt*frac
    surv=frac>=1-1e-12
    cont=np.where(surv,interp(vnext,hit,cfg),settlement(t+dtau,hit,cfg))
    u=np.broadcast_to(s[...,0],np.broadcast_shapes(s.shape[:-1],a.shape[:-1]))
    c,th=a[...,0],a[...,1]
    flow=c**(1-u)/(1-u)-.5*cfg.k*th**2
    disc=np.exp(-cfg.rho*dtau)
    integ=-np.expm1(-cfg.rho*dtau)/cfg.rho
    return np.mean(integ*flow[...,None]+disc*cont,axis=-1)


def reference(cfg: Config, policy=None):
    """Backward solution/evaluation on every finite state, exhaustive actions."""
    start=time.perf_counter(); ss,bound=states(cfg); aa=actions(cfg)
    V=np.empty((cfg.n+1,len(ss))); P=np.empty((cfg.n,len(ss)),dtype=int)
    B=np.zeros_like(V); Exit=np.zeros_like(V)
    V[-1]=settlement(cfg.T,ss,cfg)
    pre=transition_numpy(ss[:,None,:],aa[None,:,:],cfg)
    for n in reversed(range(cfg.n)):
        t=n*cfg.dt; q=q_numpy(ss[:,None,:],aa[None,:,:],V[n+1],t,cfg,pre)
        ind=q.argmax(-1) if policy is None else np.asarray(policy(n,ss),dtype=int)
        P[n]=ind; V[n]=q[np.arange(len(ss)),ind]
        V[n,bound]=settlement(t,ss[bound],cfg)
        hit,frac,inc=[p[np.arange(len(ss)),ind] for p in pre]
        disc=np.exp(-cfg.rho*cfg.dt*frac)
        integ=-np.expm1(-cfg.rho*cfg.dt*frac)/cfg.rho
        surv=frac>=1-1e-12
        B[n]=np.mean(.5*aa[ind,1,None]**2*integ+disc*surv*interp(B[n+1],hit,cfg),-1)
        Exit[n]=np.mean((~surv)+surv*interp(Exit[n+1],hit,cfg),-1)
        B[n,bound]=0.; Exit[n,bound]=1.
    return {'V':V,'P':P,'B':B,'Exit':Exit,'seconds':time.perf_counter()-start}


class MLP(nn.Module):
    def __init__(self,out,width=48):
        super().__init__(); self.net=nn.Sequential(nn.Linear(2,width),nn.Tanh(),
                         nn.Linear(width,width),nn.Tanh(),nn.Linear(width,out))
    def forward(self,s):
        z=(s-s.new_tensor([2.,1.25]))/s.new_tensor([.8,.75])
        return self.net(z)


class Critic(nn.Module):
    def __init__(self,t,cfg,width=48):
        super().__init__(); self.t=t; self.cfg=cfg
        self.net=nn.Sequential(nn.Linear(6,width),nn.Tanh(),nn.Linear(width,width),nn.Tanh(),nn.Linear(width,1))
    def forward(self,s):
        cfg=self.cfg
        z=(s-s.new_tensor([cfg.ulo,cfg.xlo]))/s.new_tensor([cfg.uhi-cfg.ulo,cfg.xhi-cfg.xlo])
        f=torch.cat([2*z-1,torch.log(z.clamp_min(.001))/5,torch.log((1-z).clamp_min(.001))/5],-1)
        terminal=-.02*(s[...,0]-2)**2+.1*s[...,1].log()
        interior=terminal+(cfg.T-self.t)*self.net(f).squeeze(-1)
        boundary=((z<=1e-6)|(z>=1-1e-6)).any(-1)
        # Finite-chain boundary states are killed immediately; no false C2 claim.
        return torch.where(boundary,terminal-cfg.fee*(cfg.T-self.t),interior)


class Terminal(nn.Module):
    def forward(self,s): return -.02*(s[...,0]-2)**2+.1*s[...,1].log()


def q_torch(s,aa,nextnet,t,cfg):
    """Independent torch quadrature implementation; actor receives detached Q."""
    z=s.new_tensor([[-1.,-1.],[-1.,1.],[1.,-1.],[1.,1.]])
    ss=s[:,None,None,:]; a=aa[None,:,None,:]
    u=ss[...,0]; x=ss[...,1]; c=a[...,0]; th=a[...,1]; p=a[...,2]
    du=th*cfg.dt+cfg.su*math.sqrt(cfg.dt)*z[:,0]
    dx=((cfg.r+cfg.excess*p)*x-c)*cfg.dt+cfg.sx*p*x*math.sqrt(cfg.dt)*(cfg.corr*z[:,0]+math.sqrt(1-cfg.corr**2)*z[:,1])
    du=du.expand_as(dx); inc=torch.stack([du,dx],-1); y=ss+inc
    tau=torch.ones_like(dx)
    for j,lo,hi in [(0,cfg.ulo,cfg.uhi),(1,cfg.xlo,cfg.xhi)]:
        d=inc[...,j]; safe=torch.where(d.abs()>1e-12,d,torch.ones_like(d))
        f=torch.where(y[...,j]<lo,(lo-ss[...,j])/safe,
              torch.where(y[...,j]>hi,(hi-ss[...,j])/safe,torch.ones_like(d)))
        tau=torch.minimum(tau,f)
    tau=tau.clamp(0,1); hit=ss+tau[...,None]*inc
    # Positive bilinear interpolation of neural values on the declared lattice.
    # Thus the numpy reference and neural training target are the SAME finite operator.
    grid=torch.tensor(states(cfg)[0],dtype=s.dtype,device=s.device)
    vg=nextnet(grid).reshape(cfg.nu,cfg.nx)
    frac=(hit-hit.new_tensor([cfg.ulo,cfg.xlo]))/hit.new_tensor([cfg.uhi-cfg.ulo,cfg.xhi-cfg.xlo])
    frac=frac*hit.new_tensor([cfg.nu-1,cfg.nx-1]); ind=torch.floor(frac).long()
    iu=ind[...,0].clamp(0,cfg.nu-2); ix=ind[...,1].clamp(0,cfg.nx-2)
    wu=(frac[...,0]-iu).clamp(0,1); wx=(frac[...,1]-ix).clamp(0,1)
    cont=(1-wu)*((1-wx)*vg[iu,ix]+wx*vg[iu,ix+1])+wu*((1-wx)*vg[iu+1,ix]+wx*vg[iu+1,ix+1])
    settle=-.02*(hit[...,0]-2)**2+.1*hit[...,1].log()-cfg.fee*(cfg.T-t-cfg.dt*tau)
    cont=torch.where(tau>=1-1e-6,cont,settle)
    flow=c**(1-u)/(1-u)-.5*cfg.k*th**2
    disc=torch.exp(-cfg.rho*cfg.dt*tau)
    integ=-torch.expm1(-cfg.rho*cfg.dt*tau)/cfg.rho
    return (integ*flow+disc*cont).mean(-1)


def train_nbo(cfg,seed=0,actor_steps=400,critic_steps=800,width=48,ns=768):
    """Backward separated finite-action NBO. NO reference solution is input.
    Candidate Qs use only the previous fitted neural continuation.
    Global finite-action improvement labels prevent a stationary-actor fallacy.
    A hard actor is evaluated, never the soft training distribution.
    """
    torch.manual_seed(seed); rng=np.random.default_rng(seed)
    aa=torch.tensor(actions(cfg),dtype=torch.float32)
    critics=[None]*(cfg.n+1); critics[-1]=Terminal(); actors=[None]*cfg.n; logs=[]
    start=time.perf_counter()
    for n in reversed(range(cfg.n)):
        t=n*cfg.dt
        # Finite-operator collocation includes every interior lattice point.
        # Out-of-sample performance is audited separately on refined lattices.
        ss,bmask=states(cfg)
        st=torch.tensor(ss[~bmask],dtype=torch.float32)
        nxt=critics[n+1]
        for p in nxt.parameters(): p.requires_grad_(False); p.grad=None
        with torch.no_grad(): q=q_torch(st,aa,nxt,t,cfg); labels=q.argmax(-1)
        actor=MLP(len(aa),width)
        if n<cfg.n-1: actor.load_state_dict(actors[n+1].state_dict())
        opt=torch.optim.Adam(actor.parameters(),lr=.004)
        for it in range(actor_steps):
            opt.zero_grad(set_to_none=True); logits=actor(st)
            # CE helps represent state-dependent global maximizers. Q regret is in utility units.
            loss=nn.functional.cross_entropy(logits,labels)+((q.max(-1).values-(logits.softmax(-1)*q).sum(-1))).mean()
            loss.backward(); opt.step()
        with torch.no_grad(): chosen=actor(st).argmax(-1); target=q.gather(1,chosen[:,None]).squeeze(1)
        crit=Critic(t,cfg,width)
        if n<cfg.n-1: crit.net.load_state_dict(critics[n+1].net.state_dict())
        opt=torch.optim.Adam(crit.parameters(),lr=.004)
        for it in range(critic_steps):
            opt.zero_grad(set_to_none=True); err=crit(st)-target
            loss=(err**2).mean(); loss.backward(); opt.step()
        # A deterministic quasi-Newton finish improves the critic, not the policy target.
        opt=torch.optim.LBFGS(crit.parameters(),lr=.8,max_iter=250,line_search_fn='strong_wolfe')
        def closure():
            opt.zero_grad(set_to_none=True); l=((crit(st)-target)**2).mean(); l.backward(); return l
        opt.step(closure)
        with torch.no_grad():
            gap=q.max(-1).values-q.gather(1,actor(st).argmax(-1)[:,None]).squeeze(-1)
            ce=(crit(st)-target)
        logs.append({'n':n,'critic_train_rmse':float((ce.square().mean()).sqrt()),
                     'actor_train_gain_max':float(gap.max()),
                     'actor_train_gain_mean':float(gap.mean()),
                     'critic_grad_leak_during_actor':any(p.grad is not None for p in nxt.parameters())})
        critics[n]=crit; actors[n]=actor
        print(f'nbo seed={seed} n={n}: critic_rmse={logs[-1]["critic_train_rmse"]:.4g}',flush=True)
    seconds=time.perf_counter()-start
    def policy(n,s):
        with torch.no_grad(): return actors[n](torch.tensor(s,dtype=torch.float32)).argmax(-1).numpy()
    evaluation=reference(cfg,policy)
    ss,bd=states(cfg); v=np.stack([c(torch.tensor(ss,dtype=torch.float32)).detach().numpy() for c in critics])
    exact=reference(cfg); gain=[]; bound=0.; dt=cfg.dt
    for n in reversed(range(cfg.n)):
        q=q_numpy(ss[:,None,:],actions(cfg)[None,:,:],evaluation['V'][n+1],n*dt,cfg)
        g=q.max(-1)-q[np.arange(len(ss)),evaluation['P'][n]]; g[bd]=0
        gm=float(g.max()); gain.append(gm); bound=gm+math.exp(-cfg.rho*dt)*bound
    loss=exact['V']-evaluation['V']; pol=actions(cfg)[evaluation['P']]; optpol=actions(cfg)[exact['P']]
    metrics={'seed':seed,'config':asdict(cfg),'evidence_class':'neural_finite_operator',
      'train_seconds':seconds,'evaluation_seconds':evaluation['seconds'],'reference_seconds':exact['seconds'],
      'policy_loss_t0_max':float(loss[0].max()),'policy_loss_t0_mean':float(loss[0,~bd].mean()),
      'policy_loss_t0_min':float(loss[0].min()),'training_measure':'all interior lattice points','finite_model_gain_bound':bound,
      'critic_error_vs_evaluated_policy_max':float(abs(v-evaluation['V']).max()),
      'policy_component_max_difference_c_theta_pi':abs(pol-optpol).max(axis=(0,1)).tolist(),
      'policy_component_mean_difference_c_theta_pi':abs(pol[:,~bd]-optpol[:,~bd]).mean(axis=(0,1)).tolist(),
      'liquidation_boundary_error_max':float(abs(v[:,bd]-evaluation['V'][:,bd]).max()),
      'continuous_diffusion_value_error':None,
      'continuous_diffusion_value_error_reason':'time/state/control/boundary-crossing limit not certified by this finite-model test',
      'execution_status':'completed','tolerance_target':.05,
      'tolerance_status':'passed' if loss[0].max()<=.05 else 'not_met',
      'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'source_base_commit':'79a7d84be2cbbf9bd5d181599ee110540128e3b5'}
    return metrics,{'actors':actors,'critics':critics,'logs':logs,'evaluated':evaluation,'optimal':exact,'predicted':v}


def save_training(cfg,seed,**kwargs):
    met,obj=train_nbo(cfg,seed,**kwargs); out=BASE/'results'; out.mkdir(exist_ok=True)
    stem=f'ndu_n{cfg.n}_a{cfg.na}_k{cfg.k:g}_seed{seed}'
    (out/(stem+'.json')).write_text(json.dumps(met,indent=2))
    (out/(stem+'_training.json')).write_text(json.dumps(obj['logs'],indent=2))
    torch.save({'config':asdict(cfg),'actors':[m.state_dict() for m in obj['actors']],
                 'critics':[m.state_dict() for m in obj['critics'][:-1]],'width':kwargs.get('width',48)},out/(stem+'.pt'))
    np.savez_compressed(out/(stem+'.npz'),Vpolicy=obj['evaluated']['V'],Voptimal=obj['optimal']['V'],
          actor=obj['evaluated']['P'],Vcritic=obj['predicted'])
    print(json.dumps(met,indent=2),flush=True)
    return met

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--seed',type=int,default=0); p.add_argument('--n',type=int,default=12)
    p.add_argument('--na',type=int,default=5); p.add_argument('--actor-steps',type=int,default=400)
    p.add_argument('--critic-steps',type=int,default=800); args=p.parse_args()
    save_training(Config(n=args.n,na=args.na),args.seed,actor_steps=args.actor_steps,critic_steps=args.critic_steps)
