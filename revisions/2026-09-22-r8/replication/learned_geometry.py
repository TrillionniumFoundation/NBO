"""Label-free learned actor with a full-domain continuous regret certificate.

The running utility, and only the running utility, is manufactured as
ell_tilde = ell - sup_a R_a(g). Hence g is an exact smooth verification pair
with the ORIGINAL NDU dynamics, controls, covariance and first-exit contract.
This test is not evidence for the original-payoff NDU value.
"""
from __future__ import annotations
import hashlib,json,pathlib,time
import numpy as np
import torch
from torch import nn
from verify_continuum import I,low,high,iv,OUT

torch.set_num_threads(1)
torch.set_default_dtype(torch.float64)

class Actor(nn.Module):
    def __init__(self):
        super().__init__(); self.w=nn.Parameter(torch.randn(4)*.2)
    def forward(self,u):
        c=.05+.75*torch.sigmoid(self.w[0])+u*0
        th=.2*torch.tanh(self.w[2]*(u-2)+self.w[3])
        p=-.5+1.3*torch.sigmoid(self.w[1])+u*0
        return c,th,p

def certificate(weights,cells=2048):
    wc,wp,wt,bt=map(float,weights)
    c=I('.05')+I('.75')/(1+iv.exp(-I(wc)))
    p=-I('.5')+I('1.3')/(1+iv.exp(-I(wp)))
    dc=I('.8')-c
    # Utility increment = integral_c^.8 z^(-u) dz <= (.8-c)c^(-u).
    # -(.8-c)*(.1/x) <= -(.8-c)*.05 throughout the original state box.
    gc=dc*(iv.exp(-I('2.8')*iv.ln(c))-I('.05'))
    gp=I('.006')*(I('.8')-p)-I('.002')*(I('.64')-p*p)
    maxth=0.
    for j in range(cells):
        u=I(I('1.2')+I('1.6')*j/cells,I('1.2')+I('1.6')*(j+1)/cells)
        z=I(wt)*(u-2)+I(bt)
        th=I('.2')*(2/(1+iv.exp(-2*z))-1)
        star=-I('.02')*(u-2)
        maxth=max(maxth,high((th-star)**2))
    gap=gc+gp+I(maxth)
    C=(1-iv.exp(-I('.04')))/I('.04')
    return {'regret_upper_bound':high(C*gap),'hamiltonian_gap_upper':high(gap),
        'consumption_error_upper':high(dc),'portfolio_error_upper':high(I('.8')-p),
        'adjustment_error_upper':high(iv.sqrt(I(maxth))),
        'arithmetic':'mpmath.iv 40 decimal digits; 2048 interval u cells',
        'target':.01,'meets_target':high(C*gap)<=.01}

def run(seed,steps=4000):
    torch.manual_seed(seed); model=Actor(); optim=torch.optim.Adam(model.parameters(),lr=.02)
    start=time.perf_counter(); hist=[]
    for it in range(steps):
        u=1.2+1.6*torch.rand(256); x=.5+1.5*torch.rand(256)
        c,th,p=model(u)
        H=c.pow(1-u)/(1-u)-th.square()-.04*(u-2)*th-.1*c/x+.006*p-.002*p.square()
        loss=-H.mean(); optim.zero_grad(); loss.backward();optim.step()
        if it%100==0: hist.append([it,float(loss.detach())])
    weights=model.w.detach().numpy().tolist()
    result={'seed':seed,'steps':steps,'weights':weights,'training_seconds':time.perf_counter()-start,
        'certificate':certificate(weights),'history':hist,
        'scope':'learned-actor transfer test with original geometry, modified running payoff'}
    (OUT/f'geometry_s{seed}.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    results=[run(s) for s in range(300,306)]
    (OUT/'geometry_summary.json').write_text(json.dumps(results,indent=2)+'\n')
    for r in results: print(r['seed'],r['certificate'])
