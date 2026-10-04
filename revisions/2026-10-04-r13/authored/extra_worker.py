"""R13 fixed-work comparisons and independent costate diagnostics.
All candidate choices precede the final noise bank. No policy is selected on
an endpoint. Rollout-costate diagnostics are not continuous-costate certificates.
"""
from __future__ import annotations
import argparse,copy,hashlib,math,platform,resource,subprocess,time,traceback
from pathlib import Path
from common import *
import training,evaluation

def environment(out,seed,smoke):
    write(out/'ENVIRONMENT.json',dict(source_commit=source(),protocol_sha256=digest(R/'PROTOCOL.json'),seed=seed,smoke=smoke,
        python=platform.python_version(),numpy=np.__version__,torch=torch.__version__,platform=platform.platform(),
        processor=platform.processor(),threads=torch.get_num_threads(),cpu_info=Path('/proc/cpuinfo').read_text().split('flags')[0],
        source_files={str(p.relative_to(ROOT)):digest(p) for p in (R/'code').glob('*.py')}))

def nested_bank(actor,x,B,fine_noise,steps):
    """Pathwise policy costates using nested increments and a frozen policy."""
    n_fine=fine_noise.shape[0]
    if n_fine%steps:raise ValueError('non-nested time grids')
    start=x.detach().clone().requires_grad_(True);t=start[:,:1];y=start[:,1:];h=(P['T']-t)/steps
    reward=torch.zeros(len(x),1);ratio=n_fine//steps
    for k in range(steps):
        clock=t+k*h;m=actor(torch.cat([clock,y],1))
        reward=reward+torch.exp(-P['discount']*k*h)*h*old.flow(y,m)
        z=fine_noise[k*ratio:(k+1)*ratio].sum(0)/math.sqrt(ratio)
        noise=P['idiosyncratic_sigma']*z[:,:-1]+P['common_sigma']*z[:,-1:]
        y=y+h*old.drift(y,m,B)+torch.sqrt(h)*noise
    reward=reward+torch.exp(-P['discount']*(P['T']-t))*old.terminal(y)
    p=torch.autograd.grad(reward.sum(),start,create_graph=False)[0][:,1:]
    return reward.detach().numpy().ravel(),p.detach().numpy()

def mechanism(path,out,smoke=False):
    start=time.perf_counter();path=Path(path);actor,critic,st=old.load(path);d=st['dimension'];B=torch.tensor(old.coupling(d))
    ns=4 if smoke else PROTOCOL['mechanism_states'];nr=4 if smoke else PROTOCOL['mechanism_replicates']
    steps=[8,16] if smoke else PROTOCOL['mechanism_steps'];fine=max(steps)
    generator=torch.Generator().manual_seed(PROTOCOL['mechanism_noise_seed']+d)
    states=training.states(d,ns,generator,True);x=states.repeat_interleave(nr,dim=0)
    for p in actor.parameters():p.requires_grad_(False)
    raw=dict(states=states.numpy());banks=[]
    for bank in [0,1]:
        g=torch.Generator().manual_seed(PROTOCOL['mechanism_noise_seed']+10000*bank+d)
        noise=torch.randn(fine,len(x),d+1,generator=g);bankdata={}
        for n in steps:
            val,q=nested_bank(actor,x,B,noise,n);q=d*q.reshape(ns,nr,d);val=val.reshape(ns,nr)
            raw[f'q_b{bank}_n{n}']=q;raw[f'value_b{bank}_n{n}']=val;bankdata[n]=q
        banks.append(bankdata)
    xx,v,_,p=old.first_jet(critic,states);pred=(d*p).detach().numpy();vpred=v.detach().numpy().ravel()
    qa=banks[0][fine].mean(1);qb=banks[1][fine].mean(1)
    raw.update(critic_costate=pred,critic_value=vpred)
    target_var=np.mean((banks[0][fine]-banks[1][fine])**2)/2
    mse=np.mean((pred-qa)*(pred-qb));noisy_mse=np.mean((pred-qa)**2)
    def H(q,m):return np.log(m).mean(1)-P['adjustment']/2*m.mean(1)**2-(q*m).mean(1)
    qref=torch.tensor(qa/d);qhat=torch.tensor(pred/d);eps=st['epsilon'];t=states[:,:1]
    mstar=old.greedy(qref,t,eps).detach().numpy();mcritic=old.greedy(qhat,t,eps).detach().numpy()
    with torch.no_grad():mactor=actor(states).numpy()
    raw.update(reference_greedy=mstar,critic_greedy=mcritic,actor_action=mactor)
    gap=np.maximum(0,H(qa,mstar)-H(qa,mactor));cgap=np.maximum(0,H(qa,mstar)-H(qa,mcritic))
    delta=np.maximum(0,H(pred,mcritic)-H(pred,mactor));mu=P['upper']**-2
    bound=(np.sqrt(delta)+np.sqrt(np.mean((qa-pred)**2,axis=1)/(2*mu)))**2
    if np.any(gap>bound+2e-10):raise AssertionError('deterministic costate/Hamiltonian inequality failed')
    raw.update(action_loss=gap,critic_greedy_loss=cgap,mechanism_upper=bound)
    bias=[]
    for n in steps[:-1]:
        dif=banks[0][n]-banks[0][fine];mean=dif.mean(1)
        bias.append(dict(coarse=n,fine=fine,mean_costate_difference_rms=float(np.sqrt(np.mean(mean**2))),
                         rms_standard_error=float(np.sqrt(np.mean(np.var(dif,axis=1,ddof=1)/nr)))))
    ident=path.stem+'_mechanism';rp=out/(ident+'.npz');np.savez_compressed(rp,**raw)
    result=dict(record_type='mechanism',id=ident,weights=str(path.relative_to(ROOT)),weights_sha256=digest(path),raw_sha256=digest(rp),
        source_commit=source(),dimension=d,method=st['method'],states=ns,replicates_per_bank=nr,independent_banks=2,
        rollout_costate_variance=float(target_var),regression_mse_unbiased_estimate=float(mse),regression_mse_to_noisy_mean=float(noisy_mse),
        mean_actor_hamiltonian_loss=float(gap.mean()),mean_critic_greedy_hamiltonian_loss=float(cgap.mean()),mean_mechanism_upper=float(bound.mean()),
        nested_costate_differences=bias,seconds=time.perf_counter()-start,
        critic_role='trained candidate-generation critic' if st['method']=='nbo' else 'unused initialized critic; not a trained baseline critic',
        interpretation='Independent finite-rollout diagnostics. The cross-bank MSE estimate may be negative. Reference costates are Monte Carlo conditional means, not exact continuous-time costates; no costate-accuracy or optimizer-population confidence claim.')
    write(out/(ident+'.json'),result);return result

def main(seed,smoke=False,secondary=False):
    seed=int(seed);where='extra_development' if smoke else ('secondary_results' if secondary else 'extra_results')
    out=R/where/str(seed);out.mkdir(parents=True,exist_ok=True);environment(out,seed,smoke)
    budgets=[4,8] if smoke else PROTOCOL['fixed_work_budgets'];dims=[10] if smoke else ([10,50] if secondary else PROTOCOL['dimensions'])
    if smoke:PROTOCOL['checkpoint_every']=4
    records=[];tasks=[]
    warm=torch.nn.Parameter(torch.zeros(1));optimizer=torch.optim.Adam([warm]);(warm*warm).sum().backward();optimizer.step()
    try:
        for d in dims:
            chosen={}
            order=list(PROTOCOL['methods']);rotation=seed%len(order);order=order[rotation:]+order[:rotation]
            for method in order:
                tr=training.train(d,seed,method,out,tag='_fixed',seconds=86400.,max_iterations=max(budgets))
                if tr.get('failure') or not tr.get('weights_sha256'):raise RuntimeError('fixed-work fit failed: '+str(tr))
                chosen[method]={}
                for budget in budgets:
                    hist=[h for h in tr['history'] if h['iteration']<=budget]
                    if not hist or max(h['iteration'] for h in hist)!=budget:raise AssertionError('fixed work checkpoint absent')
                    winner=max(hist,key=lambda h:h['validation_return']);end=max(hist,key=lambda h:h['iteration'])
                    cp=out/f"{tr['id']}_k{winner['iteration']}.pt";alias=out/f'{method}_d{d}_s{seed}_work{budget}.pt'
                    alias.write_bytes(cp.read_bytes())
                    selection=dict(record_type='work_selection',id=alias.stem,dimension=d,method=method,seed=seed,budget=budget,
                        weights=str(alias.relative_to(ROOT)),weights_sha256=digest(alias),selected_checkpoint=str(cp.relative_to(ROOT)),
                        selected_iteration=winner['iteration'],fit_seconds=end['seconds'],training_state_visits=end['training_state_visits'],
                        validation_state_visits=end['validation_state_visits'],critic_updates=end['critic_updates'],actor_updates=end['actor_updates'],
                        source_commit=source(),selection='best validation checkpoint within the fixed prefix; identical prefixes, no final-data selection',
                        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
                    write(out/(alias.stem+'_selection.json'),selection)
                    row=evaluation.evaluate(alias,out,design='population',steps=32 if smoke else None,paths=64 if smoke else None,
                        test_seed=PROTOCOL['development_noise_seed'] if smoke else PROTOCOL['fixed_work_noise_seed'])
                    chosen[method][budget]=row;records.append(row['id'])
                if seed==PROTOCOL['mechanism_seed'] and not secondary:
                    mechanism(out/f'{method}_d{d}_s{seed}_work{max(budgets)}.pt',out,smoke)
                tasks.append(dict(dimension=d,method=method,completed=True,budgets=budgets))
            for budget in budgets:
                for left,right in PROTOCOL['method_contrasts']:
                    a=chosen[left][budget];b=chosen[right][budget]
                    evaluation.paired(out/(a['id']+'.json'),out/(b['id']+'.json'),out)
            if seed==PROTOCOL['observation_seed'] and d in PROTOCOL['observation_dimensions'] and not smoke and not secondary:
                from sensor import audit
                audit(out/f'nbo_d{d}_s{seed}_work{max(budgets)}.pt',out)
    except Exception:
        (out/'failure.txt').write_text(traceback.format_exc());write(out/'EXECUTION.json',dict(seed=seed,smoke=smoke,secondary=secondary,success=False,tasks=tasks,source_commit=source()));raise
    write(out/'EXECUTION.json',dict(seed=seed,smoke=smoke,secondary=secondary,success=True,tasks=tasks,source_commit=source(),
          protocol_sha256=digest(R/'PROTOCOL.json'),policy_evaluations=records))

def auxiliary_mechanisms():
    out=R/'extra_results/aux_mechanisms';out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for p in sorted((R/'results/aux').glob('*.json')):
        r=json.loads(p.read_text())
        if 'history' in r and r.get('weights_sha256') and r.get('method')=='nbo' and r.get('dimension') in [10,50]:
            rows.append(mechanism(p.with_suffix('.pt'),out))
    write(out/'MECHANISM_INDEX.json',dict(source_commit=source(),rows=[r['id'] for r in rows]))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--seed',type=int,default=7919);parser.add_argument('--smoke',action='store_true');parser.add_argument('--secondary',action='store_true');parser.add_argument('--aux-mechanisms',action='store_true');a=parser.parse_args()
    if a.aux_mechanisms:auxiliary_mechanisms()
    else:main(a.seed,a.smoke,a.secondary)
