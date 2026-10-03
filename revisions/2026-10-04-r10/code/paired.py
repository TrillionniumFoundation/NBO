"""Common-noise deployment comparison; intervals exclude Euler bias."""
from __future__ import annotations
import hashlib,json,math,time
from pathlib import Path
import numpy as np
import torch
from scipy.stats import t as student
from tube_neural import P,OUT,Critic,Actor,action as proposal_action,flow,drift,terminal
from tube_certificate import coupling,I,schedule_i,up,down

def tube_guard(proposal,t,epsilon=.1):
    """Inward control endpoints from an outward schedule interval.

    Adjacent clock floats cover rounding of a real input clock. No neural
    exponential or tanh accuracy is used to enforce the action tube.
    """
    clock=t.detach().numpy()
    if not np.isfinite(clock).all() or np.any((clock<0)|(clock>P['T'])):
        raise ValueError('clock outside the finite horizon')
    center=schedule_i(I(np.maximum(0,down(clock)),np.minimum(P['T'],up(clock))))
    lo=up(center.hi-epsilon);hi=down(center.lo+epsilon)
    if np.any(lo>hi):raise ArithmeticError('empty inward action tube')
    lo=torch.from_numpy(lo);hi=torch.from_numpy(hi)
    fallback=(lo+hi)/2
    proposal=torch.where(torch.isfinite(proposal),proposal,fallback)
    return torch.maximum(lo,torch.minimum(hi,proposal))

def action(critic,actor,x,method,epsilon=.1):
    proposal=proposal_action(critic,actor,x,method,epsilon)
    return tube_guard(proposal,x[:,:1],epsilon) if method in ['actor','direct_tube'] else proposal

def stats(a):
    a=np.asarray(a,dtype=float);n=len(a);se=float(a.std(ddof=1)/math.sqrt(n));mu=float(a.mean())
    radius=float(student.ppf(.975,n-1))*se
    return dict(mean=mu,se=se,ci95=[mu-radius,mu+radius],paths=n,
                interpretation='pointwise Monte Carlo interval only; Euler bias is not included')

def run(d,paths=512):
    start=time.perf_counter();B=torch.tensor(coupling(d));fine=160
    gen=torch.Generator().manual_seed(20261004+d)
    dwfine=torch.randn(fine,paths,d+1,generator=gen)*math.sqrt(P['T']/fine)
    policies=[('anchor',None,None,None)];sources={}
    for method in ['actor','direct_tube','direct_full']:
      for seed in [11,29,47]:
        ident=f'{method}_d{d}_s{seed}';path=OUT/f'{ident}.pt'
        state=torch.load(path,map_location='cpu',weights_only=True)
        if not torch.equal(state['B'],B):raise AssertionError('coupling mismatch')
        critic=Critic(d,state['width']);critic.load_state_dict(state['critic'])
        actor=Actor(d,state['width'],state['epsilon']);actor.load_state_dict(state['actor'])
        policies.append((method,seed,critic,actor));sources[ident]=hashlib.sha256(path.read_bytes()).hexdigest()
    raw={'fine_increments':dwfine.numpy()};records=[];contrasts=[];online=[]
    onlinegen=torch.Generator().manual_seed(611+d)
    online_x=torch.cat([torch.rand(256,1,generator=onlinegen),torch.randn(256,d,generator=onlinegen)],1)
    for method,seed,critic,actor in policies:
        for _ in range(3):action(critic,actor,online_x,method)
        ts=time.perf_counter()
        for _ in range(20):action(critic,actor,online_x,method)
        online.append(dict(method=method,seed=seed,batch=256,seconds=(time.perf_counter()-ts)/20,
                      includes='full deployed policy, including inward schedule guard for tube methods'))
    for nt in [40,80,160]:
        dw=dwfine.reshape(nt,fine//nt,paths,d+1).sum(dim=1);h=P['T']/nt
        for method,seed,critic,actor in policies:
            ident='anchor' if method=='anchor' else f'{method}_d{d}_s{seed}'
            y=torch.zeros(paths,d);pv=torch.zeros(paths,1);elapsed=time.perf_counter()
            for n in range(nt):
                x=torch.cat([torch.full((paths,1),n*h),y],dim=1)
                m=action(critic,actor,x,method)
                with torch.no_grad():
                    pv+=math.exp(-P['discount']*n*h)*h*flow(y,m)
                    y+=h*drift(y,m,B)+P['idiosyncratic_sigma']*dw[n,:,:d]+P['common_sigma']*dw[n,:,d:]
            with torch.no_grad():pv+=math.exp(-P['discount']*P['T'])*terminal(y)
            a=pv.numpy().ravel();raw[f'{ident}_{nt}']=a
            if nt==160:raw[f'{ident}_terminal']=y.numpy()
            records.append(dict(id=ident,steps=nt,seconds=time.perf_counter()-elapsed,**stats(a)))
        for seed in [11,29,47]:
            for other in ['anchor','direct_tube','direct_full']:
                a=raw[f'actor_d{d}_s{seed}_{nt}'];name=other if other=='anchor' else f'{other}_d{d}_s{seed}'
                contrasts.append(dict(seed=seed,steps=nt,contrast=f'actor - {other}',**stats(a-raw[f'{name}_{nt}'])))
    path=OUT/f'PAIRED_d{d}.npz';np.savez_compressed(path,**raw)
    result=dict(dimension=d,brownian_seed=20261004+d,brownian_drivers=d+1,covariance_rank=d,
       seconds=time.perf_counter()-start,records=records,contrasts=contrasts,online=online,
       policy_source_sha256=sources,raw_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
       continuous_euler_error=None,confidence_scope='no multiplicity correction; not used in structural proof')
    (OUT/f'PAIRED_d{d}.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(dimension=d,seconds=result['seconds'],contrasts=[r for r in contrasts if r['steps']==160])),flush=True)
    return result
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--dimension',type=int,required=True);p.add_argument('--paths',type=int,default=512);a=p.parse_args();run(a.dimension,a.paths)
