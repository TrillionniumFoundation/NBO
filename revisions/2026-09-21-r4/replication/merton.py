#!/usr/bin/env python3
"""Separated continuous HJB neural update on an independently solvable economy.
A homothetic one-weight critic and a two-logit constant actor are neural
parameterizations, not a general-purpose deep architecture. No analytical
optimal policy/value enters either loss. Analytic evaluation is audit-only.
"""
import hashlib,json,time
from pathlib import Path
import numpy as np
import torch
from torch import nn
BASE=Path(__file__).resolve().parents[1]
torch.set_num_threads(1); torch.set_default_dtype(torch.float64)

def run(seed):
    torch.manual_seed(seed); start=time.perf_counter()
    logA=nn.Parameter(torch.tensor(5.0+.1*seed))
    raw=nn.Parameter(torch.tensor([-.6,.2])+.05*torch.randn(2))
    x=torch.linspace(.5,2,41,requires_grad=True)
    trace=[]
    def policy():
        y=torch.sigmoid(raw); return .005+.065*y[0],-.5+1.5*y[1]
    def jets():
        v=-logA.exp()/x
        vx=torch.autograd.grad(v.sum(),x,create_graph=True)[0]
        vxx=torch.autograd.grad(vx.sum(),x,create_graph=True)[0]
        return v,vx,vxx
    actor_to_critic_grad=None
    for it in range(18):
        m,p=policy(); m,p=m.detach(),p.detach()
        oc=torch.optim.LBFGS([logA],max_iter=35,line_search_fn='strong_wolfe',tolerance_grad=1e-12,tolerance_change=1e-14)
        def ce():
            oc.zero_grad(); v,vx,vxx=jets()
            residual=-1/(m*x)+((.02+.06*p)-m)*x*vx+.5*(.2*p*x)**2*vxx-.04*v
            loss=(m*x*residual).square().mean(); loss.backward(); return loss
        oc.step(ce)
        v,vx,vxx=[y.detach() for y in jets()]
        logA.grad=None
        oa=torch.optim.LBFGS([raw],max_iter=50,line_search_fn='strong_wolfe',tolerance_grad=1e-11,tolerance_change=1e-14)
        def ae():
            oa.zero_grad(); m,p=policy()
            H=-1/(m*x.detach())+((.02+.06*p)-m)*x.detach()*vx+.5*(.2*p*x.detach())**2*vxx-.04*v
            loss=-(x.detach()*H).mean()/logA.exp().detach(); loss.backward(); return loss
        oa.step(ae)
        assert logA.grad is None
        actor_to_critic_grad='disconnected'
        m,p=policy(); trace.append({'iteration':it,'A':float(logA.exp().detach()),'m':float(m.detach()),'pi':float(p.detach())})
    m,p=[float(v.detach()) for v in policy()]; A=float(logA.exp().detach())
    D=.04+.02+.06*p-m-.04*p*p
    assert D>0
    Aeval=1/(m*D); mstar=.04125; pstar=.75; Astar=1/mstar**2
    value_loss=(Aeval-Astar)/.5
    result={'seed':seed,'evidence_class':'continuous_HJB_homothetic_neural',
      'critic_architecture':'V(x)=-exp(logA)/x; one trained parameter; AD first and second derivatives',
      'actor_architecture':'two trained sigmoid logits for m=c/x and portfolio share',
      'm':m,'pi':p,'Acritic':A,'Aindependent_policy_evaluation':Aeval,
      'm_error':abs(m-mstar),'pi_error':abs(p-pstar),
      'value_loss_max_on_half_to_two':value_loss,'critic_value_error_max':abs(A-Aeval)/.5,
      'scaled_HJB_residual_abs':abs(-1/m+A*D),'transversality_decay_rate':D,
      'critic_gradient_from_actor':actor_to_critic_grad,
      'seconds':time.perf_counter()-start,'execution_status':'completed',
      'tolerance_status':'passed' if value_loss<=1e-4 else 'not_met','value_tolerance':1e-4,
      'terminal_boundary_error':None,'terminal_boundary_error_reason':'infinite horizon; transversality checked instead',
      'trace':trace,'weights':{'logA':float(logA.detach()),'actor_logits':raw.detach().tolist()},
      'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'source_base_commit':'79a7d84be2cbbf9bd5d181599ee110540128e3b5'}
    return result
if __name__=='__main__':
    results=[run(s) for s in (0,1,2)]
    (BASE/'results'/'merton.json').write_text(json.dumps(results,indent=2))
    for r in results: print({k:r[k] for k in ('seed','m','pi','value_loss_max_on_half_to_two','scaled_HJB_residual_abs','seconds')})
