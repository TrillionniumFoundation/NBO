#!/usr/bin/env python3
"""Matched-grid errors, occupation statistics, and analytical negative controls.
All policy metrics include consumption, preference effort, and portfolio share.
"""
import json,hashlib,time,argparse
from pathlib import Path
from scipy.integrate import quad
from solver import *


def negative_controls():
    roots=np.roots([4.,0.,-4.,-.2]);r=np.sort(roots.real[np.abs(roots.imag)<1e-12])
    H=lambda a:-(a*a-1)**2+.2*a
    stable=[float(x) for x in r if -12*x*x+4<0];global_value=max(H(x) for x in list(r)+[-2.,2.])
    bad=min(stable);gap=float(global_value-H(bad));assert gap>.39
    viscosity=[]
    for eps in [.1,.03,.01]:
        res=quad(lambda x:(1-abs(x)/math.sqrt(x*x+eps*eps))**2,-1,1,epsabs=1e-12)[0]/2
        wrong=math.sqrt(1+eps*eps)-eps
        viscosity.append(dict(eps=eps,population_residual_mse=res,value_error_at_zero=1+wrong))
    assert viscosity[-1]['population_residual_mse']<viscosity[0]['population_residual_mse']
    return dict(actor_counterexample=dict(stationary_points=r.tolist(),bad_attractor=bad,second_derivative=-12*bad*bad+4,global_improvement_gap=gap),
                viscosity=viscosity,composite_loss=dict(eps=.1,loss_change=-.1/2+7*.1**2/3),
                no_short_sale=dict(unconstrained_share=(.01-.02)/(2*.2**2),constrained_share=0.))


def occupation(policies,m=Model()):
    """Exact forward masses for the interpolation-defined finite Markov chain.
    Bilinear weights are transition probabilities, not nearest-node rounding.
    Spatial-boundary hits terminate; terminal-date interior mass survives.
    """
    N,nu,nx,_=policies.shape;s,bd=grid(nu,nx);sf=s.reshape(-1,2);mass=np.zeros((nu,nx));mass[nu//2,nx//2]=1.
    cumulative_exit=0.;expected_time=0.;overshoot=0.;effort=0.
    for n in range(N):
        y,live,disc,flow,cost,d,alpha=transition(sf,policies[n].reshape(-1,3),1/N,m)
        w=mass.ravel()[:,None]/4
        expected_time+=float((w*alpha/N).sum());effort+=float((w*cost).sum())*math.exp(-m.rho*n/N)
        cumulative_exit+=float((w*(~live)).sum());new=np.zeros((nu,nx))
        pre=sf[:,None,:]+d;over=np.maximum(np.maximum(LO-pre,pre-HI),0).max(-1)
        if np.any(w>0):overshoot=max(overshoot,float(np.max(np.where(w>0,over,0))))
        size=np.array([nu-1,nx-1]);z=(y-LO)/(HI-LO)*size
        ij=np.minimum(np.maximum(np.floor(z).astype(int),0),size-1);f=z-ij
        i,j=ij[...,0],ij[...,1];p,q=f[...,0],f[...,1]
        for di,dj,weight in [(0,0,(1-p)*(1-q)),(1,0,p*(1-q)),(0,1,(1-p)*q),(1,1,p*q)]:
            np.add.at(new,(i+di,j+dj),w*live*weight)
        cumulative_exit+=float(new[bd].sum());new[bd]=0.;mass=new
    assert abs(cumulative_exit+mass.sum()-1)<1e-10
    return dict(exit_probability=float(cumulative_exit),terminal_survival_probability=float(mass.sum()),expected_stopping_time=expected_time,
                integrated_discounted_effort=effort,occupied_pre_exit_overshoot_max=overshoot,
                interpretation='Interpolation-defined Markov chain; not a Brownian first-passage certificate.')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='replication/r4/output');a=ap.parse_args();out=Path(a.out);m=Model();start=time.perf_counter()
    ref=solve_grid(33,49,8,(9,9,13),m);rv=np.array(ref['values']);rp=np.array(ref['policies'])
    np.savez_compressed(out/'matched_reference.npz',values=rv,policies=rp,efforts=ref['efforts'])
    ss,bd=grid(33,49);interior=~bd;rows=[];center=np.array([[2.,1.25]])
    for name in ['neural_policy_seed_101']+[f'safe_policy_{seed}' for seed in [101,202,303]]:
        path=out/(name+'.npz')
        if not path.exists():continue
        z=np.load(path);v=z['values'];p=z['policies'];vd=rv[0]-v[0];ad=abs(rp-p)
        row=dict(run=name,initial_value_difference=float(interpolate(vd,center)[0]),initial_value=float(interpolate(v[0],center)[0]),
                 initial_time_value_difference_max=float(vd[interior].max()),initial_time_value_difference_min=float(vd[interior].min()),
                 initial_time_value_difference_rmse=float(np.sqrt(np.mean(vd[interior]**2))),
                 policy_mae_c_theta_pi=ad[:,interior,:].mean((0,1)).tolist(),policy_max_c_theta_pi=ad[:,interior,:].max((0,1)).tolist(),
                 occupation=occupation(p))
        rows.append(row)
    refinements=[]
    for path in sorted(out.glob('ref_*.npz')):
        z=np.load(path);refinements.append(dict(run=path.stem,occupation=occupation(z['policies'],Model(k=float(path.stem.rsplit('_',1)[1])))))
    result=dict(reference=dict(grid=[33,49],steps=8,actions=[9,9,13],seconds=ref['elapsed'],initial_value=float(interpolate(rv[0],center)[0]),
                              occupation=occupation(rp)),comparisons=rows,reference_occupations=refinements,negative_controls=negative_controls())
    (out/'analysis_results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
