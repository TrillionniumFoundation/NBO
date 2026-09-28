"""Block-specific differential NBO and finite-state acceptance certificates.

The differential core is available for unrestricted smooth networks. The
published calibration laboratory separately identifies its restricted classes.
No optimizer stopping condition is substituted for an economic certificate.
"""
from __future__ import annotations
from typing import Callable
import numpy as np
import torch
from scipy.optimize import brentq
from torch import nn


class HardTerminalValue(nn.Module):
    """Input columns: time, then state. Enforce the specified terminal payoff."""
    def __init__(self, network: nn.Module, terminal: Callable, horizon: float):
        super().__init__()
        if horizon <= 0:
            raise ValueError('horizon must be positive')
        self.network, self.terminal, self.horizon = network, terminal, horizon

    def forward(self, tx: torch.Tensor) -> torch.Tensor:
        return self.terminal(tx[:,1:])+(self.horizon-tx[:,:1])*self.network(tx)


def jet(value: nn.Module, tx: torch.Tensor):
    """Exact derivatives; batch-separable networks are required (no BatchNorm)."""
    tx=tx.detach().requires_grad_(True)
    v=value(tx)
    dv=torch.autograd.grad(v.sum(),tx,create_graph=True)[0]
    rows=[]
    for i in range(1,tx.shape[1]):
        rows.append(torch.autograd.grad(dv[:,i].sum(),tx,create_graph=True,retain_graph=True)[0][:,1:])
    return tx,v,dv[:,:1],dv[:,1:],torch.stack(rows,dim=1)


def critic_loss(value: nn.Module, actor: nn.Module, tx: torch.Tensor, hamiltonian: Callable):
    """No actor gradients, including through the state sampling distribution."""
    tx,v,vt,vx,vxx=jet(value,tx)
    with torch.no_grad():
        actions=actor(tx)
    residual=-vt-hamiltonian(tx,actions,v,vx,vxx)
    return residual.square().mean()


def actor_loss(value: nn.Module, actor: nn.Module, tx: torch.Tensor, hamiltonian: Callable):
    """Actor sees critic levels AND all derivative channels as fixed inputs."""
    tx,v,_,vx,vxx=jet(value,tx)
    return -hamiltonian(tx.detach(),actor(tx.detach()),v.detach(),vx.detach(),vxx.detach()).mean()


def unilateral_actor_loss(i: int, values: list[nn.Module], actors: list[nn.Module],
                          tx: torch.Tensor, hamiltonian: Callable):
    tx,v,_,vx,vxx=jet(values[i],tx)
    actions=[actor(tx.detach()) if j==i else actor(tx.detach()).detach()
             for j,actor in enumerate(actors)]
    return -hamiltonian(i,tx.detach(),actions,v.detach(),vx.detach(),vxx.detach()).mean()


def independent_probe_loss(deterministic: torch.Tensor, diffusion_factor: torch.Tensor,
                           hessian: torch.Tensor, probes: int, generator=None):
    """Unbiased product objective; each probe bank is conditionally independent.

    The factor has shape (batch,state,Brownian). The exact-Hessian version here
    makes the covariance placement testable; a production HVP implementation
    may replace contractions without changing the probe independence rule.
    """
    if probes < 1:
        raise ValueError('probes must be positive')
    batch,_,brownian=diffusion_factor.shape
    residuals=[]
    for _ in range(2):
        z=torch.randn(batch,probes,brownian,dtype=hessian.dtype,device=hessian.device,generator=generator)
        direction=torch.einsum('bdm,bkm->bkd',diffusion_factor,z)
        trace=torch.einsum('bki,bij,bkj->bk',direction,hessian,direction).mean(dim=1,keepdim=True)
        residuals.append(deterministic-.5*trace)
    return (residuals[0]*residuals[1]).mean()


class ImplicitBellman:
    """Finite-state, finite-action recursive Bellman map.

    f(state,action,v) must be continuous and have slope at most -discount.
    This is a mathematical contract, not something inferable from a callback.
    The supplied bracket must contain every scalar root encountered.
    """
    def __init__(self, transitions: np.ndarray, f: Callable, step: float,
                 discount: float, bracket: tuple[float,float]):
        p=np.asarray(transitions,dtype=float)
        if p.ndim!=3 or p.shape[0]!=p.shape[2] or np.min(p)<0 or not np.allclose(p.sum(axis=2),1):
            raise ValueError('P must have shape (state,action,state) and stochastic rows')
        if step<=0 or discount<=0 or bracket[0]>=bracket[1]:
            raise ValueError('invalid step, discount or root bracket')
        self.P,self.f,self.h,self.discount,self.bracket=p,f,step,discount,bracket
        self.q=1/(1+discount*step)

    def action_values(self,v: np.ndarray) -> np.ndarray:
        v=np.asarray(v,dtype=float)
        if v.shape!=(self.P.shape[0],) or not np.isfinite(v).all():
            raise ValueError('invalid value array')
        continuation=self.P@v;out=np.empty_like(continuation)
        for s in range(out.shape[0]):
            for a in range(out.shape[1]):
                out[s,a]=brentq(lambda z:z-self.h*self.f(s,a,z)-continuation[s,a],
                                 *self.bracket,xtol=1e-13)
        return out

    def certificate(self,v: np.ndarray,policy: np.ndarray) -> dict:
        policy=np.asarray(policy)
        if policy.shape!=(self.P.shape[0],) or not np.issubdtype(policy.dtype,np.integer) or np.min(policy)<0 or np.max(policy)>=self.P.shape[1]:
            raise ValueError('invalid deterministic policy')
        av=self.action_values(v);pv=av[np.arange(len(v)),policy];best=av.max(axis=1)
        error=float(np.max(abs(v-pv)));gap=float(np.max(best-pv))
        return {'evaluation_error':error,'greedification_gap':gap,'contraction':self.q,
                'value_error_bound':(error+gap)/(1-self.q),
                'policy_regret_bound':(2*error+gap)/(1-self.q),
                'domain':'all states and all actions of this finite model'}
