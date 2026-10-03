"""Tune both direct critic families by validation, preserving all candidates."""
import copy,hashlib,json,os,sys,time
from pathlib import Path
import numpy as np
import torch
from bellman_study import R,ROOT,Critic,Actor,GreedyPolicy,validation,coupling,initial_states,greedy,schedule
import tube_neural as legacy
from policy_certificate import evaluate


def run():
    out=R/'results'/'greedy';out.mkdir(parents=True,exist_ok=True)
    protocol=json.loads((R/'PROTOCOL.json').read_text());ledger=[];start=time.perf_counter()
    for d in [10,20,50]:
        B=torch.tensor(coupling(d));seed=11
        for mode in ['direct_tube','direct_full']:
            history=[];best=None;bestval=-float('inf')
            for steps in [200,600,1200]:
                folder=out/f'{mode}_d{d}_k{steps}';folder.mkdir(exist_ok=True);legacy.OUT=folder
                row=legacy.train(d,seed,mode,steps);saved=folder/f'{mode}_d{d}_s{seed}.pt'
                state=torch.load(saved,map_location='cpu',weights_only=True)
                critic=Critic(d,state['width']);critic.load_state_dict(state['critic'])
                for mix in [0.,.25,.5,1.]:
                    policy=GreedyPolicy(critic,mode,mix,.1);t=time.perf_counter()
                    score=validation(policy,d,B,881000+d,128,64)
                    h=dict(mode=mode,dimension=d,steps=steps,mix=mix,validation_return=score,training_seconds=row['training_seconds'],validation_seconds=time.perf_counter()-t,failure=row['failure'])
                    history.append(h)
                    if score>bestval:bestval=score;best=(steps,mix,copy.deepcopy(critic.state_dict()))
                print(json.dumps(history[-4:]),flush=True)
            steps,mix,weights=best;path=out/f'greedy_{mode}_d{d}.pt'
            torch.save(dict(actor={},critic=weights,dimension=d,method='greedy',mode=mode,mix=mix,width=32,epsilon=.1,iteration=steps),path)
            row=dict(dimension=d,mode=mode,history=history,selected_steps=steps,selected_mix=mix,weights_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),selection='validation only; full critic is projected at deployment and labelled conservative hybrid')
            (out/f'TUNING_{mode}_d{d}.json').write_text(json.dumps(row,indent=2)+'\n')
            result=evaluate(path,1024,4096,test_seed=protocol['final_noise_seed'],out=out)
            ledger.append(dict(id=result['id'],success=True))
            g=torch.Generator().manual_seed(778000+d);x=initial_states(d,256,g)
            xx=x.detach().requires_grad_(True);v=critic(xx);p=torch.autograd.grad(v.sum(),xx)[0][:,1:].detach();pert=[]
            for scale in [0.,.01,.05,.1]:
                pp=p+scale*torch.randn(p.shape,generator=g)/d;m=greedy(pp,x[:,:1])
                pert.append(dict(gradient_perturbation=scale,lower_frequency=float((m<=legacy.P['lower']+1e-12).double().mean()),upper_frequency=float((m>=legacy.P['upper']-1e-12).double().mean()),schedule_action_rms=float(((m-schedule(x[:,:1]))**2).mean().sqrt())))
            (out/f'PERTURBATION_{mode}_d{d}.json').write_text(json.dumps(dict(rows=pert,scope='controlled derivative perturbations, not an estimate of true critic-gradient bias'),indent=2)+'\n')
    (out/'EXECUTION.json').write_text(json.dumps(dict(source_commit=os.environ.get('NBO_SOURCE_COMMIT',os.environ.get('GITHUB_SHA','local')),commands=ledger,seconds=time.perf_counter()-start,protocol_sha256=hashlib.sha256((R/'PROTOCOL.json').read_bytes()).hexdigest()),indent=2)+'\n')

if __name__=='__main__':run()
