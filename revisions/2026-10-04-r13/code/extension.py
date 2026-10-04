"""Fixed-work replay and independent diagnostics; never selects on final payoffs."""
from __future__ import annotations
import argparse, hashlib, json, math, os, platform, sys, time
from pathlib import Path
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[3]
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'revisions/2026-10-04-r12/code'))
import common as c
import training as tr
import evaluation as ev
P=c.P; old=c.old; pc=c.pc
PLAN=json.loads((R/'PROTOCOL.json').read_text())

def save(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')

def rollout_pair(actor,x,B,z,steps):
    """Differentiated Euler returns with nested Brownian increments, not a CT oracle."""
    fine=len(z)
    if fine%steps: raise ValueError('grids must be nested')
    ratio=fine//steps; noise=z.reshape(steps,ratio,*z.shape[1:]).sum(1)/math.sqrt(ratio)
    start=x.detach().clone().requires_grad_(True); t=start[:,:1]; y=start[:,1:]
    h=(P['T']-t)/steps; reward=torch.zeros(len(x),1)
    for k in range(steps):
        m=actor(torch.cat([t+k*h,y],1))
        reward=reward+torch.exp(-P['discount']*k*h)*h*old.flow(y,m)
        dw=P['idiosyncratic_sigma']*noise[k,:,:-1]+P['common_sigma']*noise[k,:,-1:]
        y=y+h*old.drift(y,m,B)+torch.sqrt(h)*dw
    reward=reward+torch.exp(-P['discount']*(P['T']-t))*old.terminal(y)
    q=torch.autograd.grad(reward.sum(),start)[0][:,1:]*B.shape[0]
    return reward.detach().numpy().ravel(),q.detach().numpy()

def mechanism(weights,out):
    actor,critic,state=old.load(weights);d=state['dimension']
    for p in actor.parameters():p.requires_grad_(False)
    seed=PLAN['mechanism_seed']+d
    x=tr.states(d,PLAN['mechanism_states'],torch.Generator().manual_seed(seed))
    B=torch.from_numpy(old.coupling(d));g=torch.Generator().manual_seed(seed+10000)
    values={k:[] for k in PLAN['mechanism_steps']}; costates={k:[] for k in PLAN['mechanism_steps']}
    begin=time.perf_counter()
    for rep in range(PLAN['mechanism_replicates']):
        z=torch.randn(max(PLAN['mechanism_steps']),len(x),d+1,generator=g)
        for steps in PLAN['mechanism_steps']:
            v,q=rollout_pair(actor,x,B,z,steps);values[steps].append(v);costates[steps].append(q)
    co,fi=PLAN['mechanism_steps'];qc=np.asarray(costates[co]);qf=np.asarray(costates[fi]);ref=qf.mean(0)
    ref_se2=qf.var(0,ddof=1)/len(qf)
    _,vhat,_,p=old.first_jet(critic,x);pred=(d*p).detach().numpy();vhat=vhat.detach().numpy().ravel()
    def H(q,m):return np.log(m).mean(-1)-P['adjustment']/2*m.mean(-1)**2-(q*m).mean(-1)
    with torch.no_grad():a=actor(x).numpy()
    opt=old.greedy(torch.from_numpy(ref/d),x[:,:1],state['epsilon']).numpy()
    implied=old.greedy(torch.from_numpy(pred/d),x[:,:1],state['epsilon']).numpy()
    raw_greedy=old.greedy(torch.from_numpy(qc[0]/d),x[:,:1],state['epsilon']).numpy()
    gap=H(ref,opt)-H(ref,a);gapc=H(ref,opt)-H(ref,implied);gapraw=H(ref,opt)-H(ref,raw_greedy)
    ident=Path(weights).stem+'_mechanism';raw=Path(out)/(ident+'.npz')
    np.savez_compressed(raw,states=x.numpy(),q_coarse=qc,q_fine=qf,critic_q=pred,critic_value=vhat,
                        values_coarse=np.asarray(values[co]),values_fine=np.asarray(values[fi]),
                        actor_action=a,reference_greedy=opt,critic_greedy=implied,raw_greedy=raw_greedy,
                        actor_gap=gap,critic_greedy_gap=gapc,raw_greedy_gap=gapraw)
    row={'id':ident,'dimension':d,'weights':str(Path(weights).relative_to(ROOT)),
         'weights_sha256':c.digest(weights),'raw_sha256':c.digest(raw),'source_commit':c.source(),
         'rollout_variance_coarse':float(qc.var(0,ddof=1).mean()),
         'rollout_variance_fine':float(qf.var(0,ddof=1).mean()),
         'critic_costate_mse_to_fine_mean':float(((pred-ref)**2).mean()),
         'critic_costate_mse_mc_debiased':float((((pred-ref)**2)-ref_se2).mean()),
         'raw_costate_mse_to_independent_fine_mean':float(((qc[0]-qf[1:].mean(0))**2).mean()),
         'nested_costate_mean_change':float(((qc.mean(0)-ref)**2).mean()),
         'fine_mean_mc_variance':float(ref_se2.mean()),
         'critic_value_mse_to_fine_mean':float(((vhat-np.asarray(values[fi]).mean(0))**2).mean()),
         'actor_hamiltonian_gap':float(gap.mean()),'critic_greedy_hamiltonian_gap':float(gapc.mean()),
         'raw_greedy_hamiltonian_gap':float(gapraw.mean()),
         'seconds':time.perf_counter()-begin,'states':len(x),'replicates':len(qf),'grids':[co,fi],
         'scope':'Held-out nested Euler-costate diagnostic. Fine rollout mean is noisy and discretized, not the unknown continuous-time costate. Hamiltonian gaps use that independent mean, not the learned critic. No causal or continuous-time error certification is inferred from correlations.'}
    save(Path(out)/(ident+'.json'),row);return row

def fixed_work(d,seed,environment):
    out=R/'results'/f'{environment}_d{d}_s{seed}';out.mkdir(parents=True,exist_ok=True)
    env={'source_commit':c.source(),'primary_source_commit':PLAN['primary_source_commit'],
         'protocol_sha256':c.digest(R/'PROTOCOL.json'),'python':platform.python_version(),
         'torch':torch.__version__,'numpy':np.__version__,'platform':platform.platform(),
         'machine':platform.machine(),'cpu':Path('/proc/cpuinfo').read_text().split('model name')[-1].split('\n')[0] if Path('/proc/cpuinfo').exists() else platform.processor(),
         'threads':torch.get_num_threads(),'environment':environment,'dimension':d,'seed':seed}
    save(out/'ENVIRONMENT.json',env)
    fit=[];evaluations=[];comparisons=[];diagnostics=[];ledger=[]
    for i,name in enumerate(PLAN['fixed_methods']):
        method='nbo' if name=='raw' else name
        tag='_fixed_'+name
        try:
            row=tr.train(d,seed,method,out,tag=tag,seconds=1e9,
                         max_iterations=max(PLAN['fixed_iterations']),costate_mode='raw' if name=='raw' else 'critic')
            fit.append(row)
            if row.get('failure'):raise RuntimeError(row['failure'])
            if row['completed_iterations']!=max(PLAN['fixed_iterations']):raise AssertionError('fixed work incomplete')
            for k in PLAN['fixed_iterations']:
                weight=out/f"{row['id']}_k{k}.pt"
                r=ev.evaluate(weight,out,design='population',steps=PLAN['final_steps'],paths=PLAN['final_paths'],test_seed=PLAN['final_noise_seed'])
                r['extension_method']=name;r['training_seed']=seed
                save(out/(r['id']+'.json'),r);evaluations.append(r)
            if name=='nbo':diagnostics.append(mechanism(out/f"{row['id']}_k{max(PLAN['fixed_iterations'])}.pt",out))
            ledger.append({'task':name,'completed':True})
        except Exception as exc:
            ledger.append({'task':name,'completed':False,'error':f'{type(exc).__name__}: {exc}'})
            save(out/'FAILURES.json',ledger)
    for k in PLAN['fixed_iterations']:
        by={r['extension_method']:r for r in evaluations if r['iteration']==k}
        for other in ['dpo','linear','raw']:
            if 'nbo' in by and other in by:
                a,b=by['nbo'],by[other]
                comparisons.append(ev.paired(out/(a['id']+'.json'),out/(b['id']+'.json'),out,label=f'paired_d{d}_s{seed}_k{k}_nbo_{other}'))
    expected=4*len(PLAN['fixed_iterations']);ok=all(r['completed'] for r in ledger) and len(evaluations)==expected and len(comparisons)==3*len(PLAN['fixed_iterations'])
    result={'source_commit':c.source(),'protocol_sha256':c.digest(R/'PROTOCOL.json'),
            'dimension':d,'seed':seed,'environment':environment,'fits':fit,'evaluations':[r['id'] for r in evaluations],
            'comparisons':[r['id'] for r in comparisons],'diagnostics':diagnostics,'ledger':ledger,'complete':ok}
    save(out/'FIXED_WORK.json',result)
    if not ok:raise RuntimeError('incomplete fixed-work study; failures retained')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dimension',type=int,required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--environment',default='ubuntu24');a=p.parse_args()
    if a.dimension not in PLAN['dimensions'] or a.seed not in PLAN['fixed_work_seeds']:raise ValueError('undeclared study cell')
    fixed_work(a.dimension,a.seed,a.environment)
