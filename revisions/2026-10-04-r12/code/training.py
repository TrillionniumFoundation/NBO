"""Equal-announced-wall-budget Bellman, direct-policy and affine fits.
No reference optimum or final-test outcome is used in training or selection.
"""
from __future__ import annotations
import copy,math,time,resource
from pathlib import Path
from common import *

def states(d,n,g,random_time=True):
    t=torch.rand(n,1,generator=g) if random_time else torch.zeros(n,1)
    support=torch.from_numpy(profiles(d));ids=torch.randint(len(support),(n,),generator=g)
    y=support[ids]-.7*t+.2*torch.sqrt(t)*torch.randn(n,d,generator=g)
    return torch.cat([t,y],1)

def validate(actor,d,B,seed):
    g=torch.Generator().manual_seed(seed)
    x=states(d,PROTOCOL['validation_paths'],g,False)
    with torch.no_grad():val,used=old.rollout(actor,x,B,g,PROTOCOL['validation_steps'])
    return float(val.mean()),used

def train(d,seed,method,out,tag='',seconds=None,epsilon=None,width=None,value_weight=None,costate_weight=None,updates=None,max_iterations=None):
    if method not in ['nbo','dpo','linear']:raise ValueError('unknown method')
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    budget=PROTOCOL['fit_wall_seconds'] if seconds is None else float(seconds)
    epsilon=PROTOCOL['epsilon'] if epsilon is None else float(epsilon)
    width=PROTOCOL['width'] if width is None else int(width)
    vw=PROTOCOL['value_weight'] if value_weight is None else float(value_weight)
    cw=PROTOCOL['costate_weight'] if costate_weight is None else float(costate_weight)
    cu=PROTOCOL['critic_updates'] if updates is None else int(updates)
    au=PROTOCOL['actor_updates'] if updates is None else int(updates)
    maximum=PROTOCOL['maximum_iterations'] if max_iterations is None else int(max_iterations)
    if budget<=0 or epsilon<=0 or cu<1 or au<1 or maximum<1:raise ValueError('invalid training budget')
    ident=f'{method}_d{d}_s{seed}'+tag
    torch.manual_seed(seed)
    start=time.perf_counter()
    actor=old.LinearActor(d,epsilon) if method=='linear' else old.Actor(d,width,epsilon)
    critic=old.Critic(d,width);B=torch.tensor(old.coupling(d))
    oa=torch.optim.Adam(actor.parameters(),lr=.003);oc=torch.optim.Adam(critic.parameters(),lr=.002)
    gs=torch.Generator().manual_seed(18000000+seed);gb=torch.Generator().manual_seed(28000000+seed)
    validation_seed=38000000+seed+d
    history=[];visits=0;validation_visits=0;critic_updates=0;actor_updates=0;best=None;bestval=-math.inf;failure=None;it=0
    for it in range(1,maximum+1):
        try:
            x=states(d,PROTOCOL['batch'],gs)
            if method=='nbo':
                frozen=copy.deepcopy(actor).eval()
                for p in frozen.parameters():p.requires_grad_(False)
                value,target,used=old.rollout(frozen,x,B,gb,PROTOCOL['rollout_steps'],True);visits+=used
                for _ in range(cu):
                    oc.zero_grad(set_to_none=True);_,v,_,p=old.first_jet(critic,x)
                    lv=(v-value).square().mean();lg=(d*(p-target)).square().mean();loss=vw*lv+cw*lg
                    if not torch.isfinite(loss):raise FloatingPointError('nonfinite critic objective')
                    loss.backward();oc.step();critic_updates+=1
                _,_,_,p=old.first_jet(critic,x);p=p.detach()
                for _ in range(au):
                    oa.zero_grad(set_to_none=True);m=actor(x)
                    la=-(torch.log(m).mean(1,keepdim=True)-P['adjustment']/2*m.mean(1,keepdim=True).square()-(m*p).sum(1,keepdim=True)).mean()
                    if not torch.isfinite(la):raise FloatingPointError('nonfinite actor objective')
                    la.backward();oa.step();actor_updates+=1
                lv=float(lv.detach());lg=float(lg.detach())
            else:
                oa.zero_grad(set_to_none=True);ret,used=old.rollout(actor,x,B,gb,PROTOCOL['rollout_steps']);visits+=used;loss=-ret.mean()
                if not torch.isfinite(loss):raise FloatingPointError('nonfinite direct objective')
                loss.backward();oa.step();actor_updates+=1;lv=float(loss.detach());lg=None
            elapsed=time.perf_counter()-start
            final=(elapsed>=budget or it==maximum)
            if it%PROTOCOL['checkpoint_every']==0 or final:
                score,nv=validate(actor,d,B,validation_seed);validation_visits+=nv
                snap=dict(actor=copy.deepcopy(actor.state_dict()),critic=copy.deepcopy(critic.state_dict()),dimension=d,method=method,width=width,epsilon=epsilon,iteration=it)
                checkpoint=out/f'{ident}_k{it}.pt';torch.save(snap,checkpoint)
                row=dict(iteration=it,seconds=time.perf_counter()-start,validation_return=score,value_loss=lv,costate_loss=lg,training_state_visits=visits,validation_state_visits=validation_visits,critic_updates=critic_updates,actor_updates=actor_updates,weights_sha256=digest(checkpoint))
                history.append(row)
                if score>bestval:bestval=score;best=(it,snap)
            if final or time.perf_counter()-start>=budget:break
        except Exception as exc:failure=f'{type(exc).__name__}: {exc}';break
    elapsed=time.perf_counter()-start
    # The last saved checkpoint is selected only on the independent validation bank.
    if best is None:
        row=dict(id=ident,dimension=d,seed=seed,method=method,failure=failure or 'no checkpoint',history=history,source_commit=source(),requested_wall_seconds=budget)
        write(out/f'{ident}.json',row);return row
    selected,snap=best;path=out/f'{ident}.pt';torch.save(snap,path)
    row=dict(id=ident,dimension=d,seed=seed,method=method,tag=tag,epsilon=epsilon,width=width,value_weight=vw,costate_weight=cw,updates_per_block=cu,requested_wall_seconds=budget,seconds=elapsed,overshoot_seconds=max(0.,elapsed-budget),completed_iterations=it,selected_iteration=selected,training_state_visits=visits,validation_state_visits=validation_visits,critic_updates=critic_updates,actor_updates=actor_updates,history=history,failure=failure,weights_sha256=digest(path),source_commit=source(),peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,selection='maximum independent population validation return; no final-test selection',budget_scope='initialization, optimizer creation, simulation, updates, validation and checkpoint writes; finish current iteration; final selected-weight write excluded')
    write(out/f'{ident}.json',row);print(ident,elapsed,selected,failure,flush=True)
    return row
