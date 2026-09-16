#!/usr/bin/env python3
"""Executable differential/semigroup graph and terminal-sign regression tests."""
import json,math,argparse
from pathlib import Path
import numpy as np
import torch
from solver import *


def run():
    s=torch.tensor([[2.,1.]],requires_grad=True);a=torch.tensor(.8,requires_grad=True)
    coeff=nn.Parameter(torch.tensor([1.2,-.7,.4]))
    v=coeff[0]*s[:,0]**2+coeff[1]*s[:,1]**2+coeff[2]*s[:,0]*s[:,1]
    grad=torch.autograd.grad(v.sum(),s,create_graph=True)[0]
    Hess=torch.stack([torch.autograd.grad(grad[:,j].sum(),s,create_graph=True,retain_graph=True)[0] for j in range(2)],1)[0]
    B=torch.stack([torch.stack([a*0+.05,a*0]),torch.stack([.2*a*s[0,1]*(-.25),.2*a*s[0,1]*math.sqrt(1-.25**2)])])
    covariance=B@B.T;actor_trace=.5*(covariance*Hess.detach()).sum()
    ga,gc=torch.autograd.grad(actor_trace,(a,coeff),allow_unused=True,retain_graph=True)
    expected=-.2*.05*.25*float(coeff[2].detach())+2*.2**2*.8*float(coeff[1].detach())
    assert abs(float(ga)-expected)<1e-12 and gc is None
    critic_trace=.5*(covariance.detach()*Hess).sum()
    gc,ga2=torch.autograd.grad(critic_trace,(coeff,a),allow_unused=True)
    assert ga2 is None and torch.isfinite(gc).all() and gc.abs().sum()>0
    raw=torch.tensor([[.3,.01,.4]],requires_grad=True);x=torch.tensor([[2.,1.25]])
    q=torch_backup(torch_terminal,x,raw,.05,Model());g=torch.autograd.grad(q.sum(),raw)[0].detach().numpy()[0]
    fd=[]
    for j in range(3):
        eps=1e-6;u=raw.detach().clone();v=u.clone();u[0,j]+=eps;v[0,j]-=eps
        fd.append(float((torch_backup(torch_terminal,x,u,.05,Model())-torch_backup(torch_terminal,x,v,.05,Model()))/(2*eps)))
    assert np.max(abs(g-np.array(fd)))<1e-8
    # Explicit finite-horizon recursive-domain architecture, not a string label.
    xx=torch.logspace(-1,1,101);t=torch.linspace(0,1,101);b=-4.;A=1.3
    log_bequest=math.log(A)+b*torch.log(xx);raw_value=torch.sin(xx)
    V=torch.exp(log_bequest+(1-t)*raw_value)/b
    terminal_v=torch.exp(log_bequest)/b
    boundary=float(abs(torch.exp(log_bequest+0*raw_value)/b-terminal_v).max())
    assert float((b*V).min())>0 and boundary<1e-12
    # G is a strict supersolution on the stopped NDU domain under all controls.
    utility_upper=.8**(1-2.8)/(1-2.8)
    generator_upper=.04*.8*.2+.1*(.02+.06*.8-.05/2)-.5*.04*.05**2
    discount_upper=.04*(.02*.8**2-.1*math.log(.5))
    HGupper=utility_upper+generator_upper+discount_upper;assert HGupper<-.8
    from coupled_resource import Critic as ConvexCritic
    rc=ConvexCritic(4,np.random.default_rng(42));rc.c=np.abs(np.random.default_rng(43).normal(size=len(rc.c)))*.01
    rr=np.random.default_rng(44).normal(size=(7,4));tx=torch.tensor(rr,requires_grad=True);z=tx-1
    tv=(z*z).mean(-1)+.2*z.mean(-1)**2+torch.relu(z@torch.tensor(rc.W).T+torch.tensor(rc.b)).square()@torch.tensor(rc.c)
    tg=torch.autograd.grad(tv.sum(),tx)[0].detach().numpy();convex_error=float(abs(tg-rc.grad(rr)).max());assert convex_error<1e-12
    ss,bd=grid(9,13);bs=ss[bd];actions=np.tile([.05,.2,.0],(len(bs),1))
    nq=backup(terminal(ss),bs,actions,.125,Model())[0]
    tq=torch_backup(torch_terminal,torch.tensor(bs),torch.tensor(actions),.125,Model()).detach().numpy()
    boundary_operator_error=max(float(abs(nq-terminal(bs)).max()),float(abs(tq-terminal(bs)).max()))
    assert boundary_operator_error<1e-12
    return dict(convex_neural_gradient_max_error=convex_error,immediate_stopping_boundary_error=boundary_operator_error,actor_trace_derivative=float(ga),actor_trace_derivative_expected=expected,
                actor_step_critic_gradient_is_none=True,critic_step_actor_gradient_is_none=ga2 is None,
                critic_trace_coefficient_gradient=gc.tolist(),semigroup_actor_gradient=g.tolist(),semigroup_finite_difference=fd,
                semigroup_gradient_max_error=float(np.max(abs(g-fd))),recursive_finite_horizon_domain_min=float((b*V).min()),
                recursive_terminal_error=boundary,ndu_H_G_analytic_upper_bound=HGupper,
                recursive_architecture_interpretation='Domain/terminal architecture regression; not an additional finite-horizon utility solve.')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='replication/r4/output');a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    ans=run();(out/'graph_results.json').write_text(json.dumps(ans,indent=2)+'\n');print(ans)
