"""Deterministic regression tests, not economic proofs by sampling."""
import copy,json,sys,time
from pathlib import Path
import numpy as np
import torch
import study as S
from budget_coordinates import setup as old_setup

def main():
    records=[]
    def passed(name,**kw):records.append({'name':name,'passed':True,**kw})
    net=S.network(24601);raw=net(S.NODES).detach();q=S.CHART
    assert torch.max(torch.abs(q.T@q-torch.eye(47)))<2e-14
    gauge=torch.zeros(48);gauge[::3]=1
    assert torch.max(torch.abs(q.T@gauge))<2e-14
    passed('47-coordinate orthonormal financing quotient')
    old=old_setup();new=S.setup();a=old(net,True);b=new(net,True)
    assert all(a[k]==b[k] for k in ('b','s','theta','approx_value','approx_budget'))
    go=torch.autograd.grad(old(net),list(net.parameters()));gn=torch.autograd.grad(new(net),list(net.parameters()))
    error=max(float(torch.max(torch.abs(x-y))) for x,y in zip(go,gn));assert error<2e-13
    passed('inherited 8/16 objective and first derivative on unclipped nodes',gradient_error=error)
    mats,geo=S.geometries(net)
    for m,A in mats.items():
        z=S.Coordinates(raw,A);d=new(z,True)
        assert all(d[k]==b[k] for k in ('b','s','theta','approx_value','approx_budget'))
        assert torch.linalg.matrix_rank(A,tol=1e-12)==47
    passed('all direct charts match the initial policy and remain full quotient rank')
    refm,geo=S.geometries(net,True)
    assert all(torch.linalg.matrix_rank(A,tol=1e-12)==48 for A in refm.values())
    passed('reference benchmark retains the nongauge common intercept')
    scaled=S.ScaledActor(net);error=float(torch.max(torch.abs(scaled(S.NODES)-net(S.NODES))).detach());assert error==0
    J=S.flat_jacobian(scaled);assert J.shape==(48,355)
    passed('equivalent powers-of-two parameter chart',output_error=error)
    initial=S.vector(net);j=S.flat_jacobian(net);g=torch.randn(355);g/=torch.linalg.norm(g);h0=net(S.NODES).detach().flatten();remainders=[]
    for e in (1e-3,5e-4):
        S.assign(net,initial+e*g.numpy());remainders.append(float(torch.linalg.norm(net(S.NODES).detach().flatten()-h0-e*j@g)))
    S.assign(net,initial);assert remainders[1]<.30*remainders[0]
    passed('Jacobian transport remainder is second order in this regression',remainders=remainders)
    slab=S.Slab(raw);f=S.setup();f(slab).backward();g0=slab.coefficients.grad.detach().clone();eps=1e-5
    errs=[]
    for ij in ((0,0),(5,1),(12,2)):
        vals=[]
        for sign in (1,-1):
            y=raw.clone();y[ij]+=sign*eps;vals.append(float(f(S.Slab(y)).detach()))
        errs.append(abs((vals[0]-vals[1])/(2*eps)-float(g0[ij])))
    assert max(errs)<1e-8;passed('implicit first derivative against centered differences',max_error=max(errs))
    cstar=(np.sqrt(6)-1)/2;actor={'c':[cstar]*16,'reference':True};c,_=S.reference_check(actor)
    assert c['status']=='CERTIFIED' and c['regret_upper']<1e-10
    assert c['reserve_interval'][0]>.5
    passed('directed analytic reference encloses the attained optimum',regret_upper=c['regret_upper'])
    run=S.optimize(copy.deepcopy(net),S.setup(),'adam',.005,5,(2,5),True)
    assert len(run['snapshots'])==2 and len(run['transport'])==2 and run['gradient_calls']==5
    assert all(np.isfinite(r['linearization_remainder_norm']) for r in run['transport'])
    passed('Adam checkpoint and momentum-metric instrumentation')
    run=S.optimize(copy.deepcopy(net),S.setup(),'lbfgsb',.005,8,(2,5,8))
    assert run['gradient_calls']<=8
    assert all(s['accepted_iterate_call']<=k for k,s in run['snapshots'].items())
    passed('L-BFGS checkpoints never use future accepted iterates')
    S.write(S.REV/'results/tests.json',{'tests':records,'all_passed':True,'scope':'regression tests; mathematical claims require their analytic proofs'})
    print(json.dumps(records,indent=2))
if __name__=='__main__':main()
