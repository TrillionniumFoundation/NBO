"""Regression tests supplement, and do not replace, the analytic proofs."""
from pathlib import Path
import sys,json
import numpy as np
import torch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'revisions/2026-09-23-r16/replication'))
import accessibility_certificate as C
import mpfr_interval as M
from accessibility_neural import Net,load_model,serialize
import interval_objective as D
from nonlinear_inventory import cost_gradient,torch_cost,uniform_bound,directed_check

def main():
    torch.set_num_threads(1);torch.set_default_dtype(torch.float64);tests=[M.test()]
    p=ROOT/'revisions/2026-09-23-r16/results/neural/seed16100/network_step0800.json';a,v,d=load_model(p)
    s,idx=C.cell_grid(4,16,16);s=s[:16];ds=D.I(torch.tensor(s.lo),torch.tensor(s.hi));j=D.critic_jet(ds,v);k=C.critic_jet(s,d)
    discrepancy=max(max(float(np.max(np.abs(x.lo.detach().numpy()-y.lo))),float(np.max(np.abs(x.hi.detach().numpy()-y.hi)))) for x,y in zip(j,k))
    assert discrepancy<1e-8,discrepancy
    tests.append({'name':'independently implemented interval jets','status':'PASS','max_endpoint_difference':discrepancy,'scope':'Floating training implementation regression, not a rounding guarantee'})
    rng=np.random.default_rng(17017);x=rng.uniform(-1,1,8);u=rng.uniform(-.3,.3,(12,8));ut=torch.tensor(u,requires_grad=True);f=torch_cost(torch.tensor(x),ut);g=torch.autograd.grad(f,ut)[0].numpy();fn,gn=cost_gradient(x,u)
    assert abs(fn-f.item())<1e-10 and np.max(abs(g-gn))<1e-10
    tests.append({'name':'nonlinear inventory analytic adjoint vs automatic differentiation','status':'PASS','gradient_max_difference':float(np.max(abs(g-gn)))})
    checks=directed_check(x,u);assert checks['objective_interval'][0]-1e-10<=fn<=checks['objective_interval'][1]+1e-10
    for d0 in [8,32,128]:
        b=[uniform_bound(d0,k)['total_cost_loss_upper'] for k in [0,8,16,24,32]];assert all(x>y for x,y in zip(b,b[1:]));assert b[-1]<.001
    tests.append({'name':'all-state correction bounds decrease at every declared budget','status':'PASS','scope':'Exact rational interval constants for the separately proved convex model'})
    out=HERE.parent/'results/tests.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps({'status':'PASS','tests':tests},indent=2)+'\n');print(out.read_text())
if __name__=='__main__':main()
