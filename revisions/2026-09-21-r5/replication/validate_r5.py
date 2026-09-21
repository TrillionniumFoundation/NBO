"""Independent algebra and delivered-array checks. Not a formal proof checker."""
from pathlib import Path
import json, math, sys
import numpy as np
import torch
import continuous_actor as ca
from nonlinear_control import Value
from boundary_certificate import occupation_bound
D=Path(__file__).resolve().parents[1];O=D/'results'
torch.set_num_threads(1)
def main():
    checks={};rng=np.random.default_rng(1984)
    cfg=ca.old.Config(n=6);s,bd=ca.old.states(cfg)
    s=s[~bd][::13];a=rng.uniform([.05,-.2,-.5],[.8,.2,.8],(len(s),3));v=rng.normal(size=cfg.nu*cfg.nx)
    qt=ca.q_direct(torch.tensor(s),torch.tensor(a),torch.tensor(v),.2,cfg).detach().numpy()
    qn=ca.old.q_numpy(s,a,v,.2,cfg);err=float(np.max(abs(qt-qn)));assert err<1e-9;checks['direct_operator_max_error']=err
    # Check the analytical high-dimensional jet against automatic differentiation.
    torch.manual_seed(812);m=Value(3,17).double();torch.nn.init.normal_(m.output.weight,std=.1)
    tx=torch.randn(9,4,dtype=torch.float64,requires_grad=True);t=tx[:,0].sigmoid();x=tx[:,1:]
    # Differentiate independent (t,x) coordinates, not the sigmoid parameter.
    z=torch.cat([t[:,None],x],-1).detach().requires_grad_(True)
    val,vt,g,lap=m.jet(z[:,0],z[:,1:]);grad=torch.autograd.grad(val.sum(),z,create_graph=True)[0]
    la=sum(torch.autograd.grad(grad[:,i].sum(),z,retain_graph=True)[0][:,i] for i in range(1,4))
    err=max(float((vt-grad[:,0]).abs().max()),float((g-grad[:,1:]).abs().max()),float((lap-la).abs().max()));assert err<1e-10;checks['analytic_jet_max_error']=err
    counts=0;largest_violation=0.
    for f in O.glob('n*_s*_w*_a*_c*_lr*.npz'):
        a=np.load(f);violation=float(np.max(a['optimal_value']-a['policy_value']-a['local_bound']))
        largest_violation=max(largest_violation,violation);assert violation<2e-8;assert np.isfinite(a['policy']).all();counts+=1
    checks.update(ndu_array_sets_checked=counts,ndu_all_date_envelope_violation=largest_violation)
    # Girsanov drift neutralization, including zero risky investment.
    er=0.
    for p in [-.5,0,.3,.8]:
        th=.17;su=.05;sx=.2;chi=-.25;X=1.3
        S=np.array([[su,0],[chi*sx*p*X,math.sqrt(1-chi*chi)*sx*p*X]])
        z=np.array([th/su,-chi*th/(su*math.sqrt(1-chi*chi))])
        er=max(er,float(np.max(abs(S@z-[th,0]))))
    assert er<1e-12;checks['preference_drift_neutralization_error']=er
    # Piecewise analytical occupation barrier, tested away from its joins.
    b=.07;sig=.4;A=1.;lam=2*A/sig**2;xs=np.linspace(.0001,b-.0001,101)
    wp=(np.exp(lam*(b-xs))-1)/A;wpp=-lam*np.exp(lam*(b-xs))/A
    er=float(np.max(abs(A*wp+.5*sig**2*wpp+1)));assert er<1e-12
    assert occupation_bound(b,0)==0 and occupation_bound(b,.5)>0
    checks['boundary_barrier_generator_error']=er
    summaries=[]
    for kind in ['recursive_s*.json','game_s*.json','nonlinear_d*.json']:
        for f in O.glob(kind):
            a=json.loads(f.read_text());assert np.isfinite(a['training_seconds'])
            if 'torch_numpy_agreement' in a:assert a['torch_numpy_agreement']<1e-9
            if 'dense_grid_exceeds_analytic_BR' in a:assert a['dense_grid_exceeds_analytic_BR']<1e-9
            if 'history' in a:
                assert not any(x.get('critic_gradient_leak',False) or x.get('rival_gradient_leak',False) for x in a['history'])
            summaries.append(f.name)
    checks['extension_records_checked']=len(summaries)
    checks['scope']='Arithmetic and array validation only; target misses, continuum consistency assumptions, statistical confidence, and novelty are not converted into passed proofs.'
    checks['passed']=True;(O/'validation.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks),flush=True)
if __name__=='__main__':main()
