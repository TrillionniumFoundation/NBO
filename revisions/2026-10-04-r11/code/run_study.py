"""Frozen-protocol worker. One seed is a complete, independently logged shard."""
from __future__ import annotations
import argparse,copy,hashlib,json,os,platform,sys,time,traceback
from pathlib import Path
import numpy as np
import torch
from bellman_study import R,ROOT,train,load,Actor,Critic,initial_states,rollout,first_jet,coupling
from policy_certificate import evaluate
from initial_state_inputs import floating_initial_state


def run(seed):
    p=json.loads((R/'PROTOCOL.json').read_text())
    if seed not in p['training_seeds']:raise ValueError('undeclared final seed')
    out=R/'results'/f'seed_{seed}';out.mkdir(parents=True,exist_ok=True)
    ledger=[];start=time.perf_counter()
    def execute(kind,ident,fn):
        t=time.perf_counter()
        try:
            result=fn();ledger.append(dict(kind=kind,id=ident,success=True,seconds=time.perf_counter()-t))
            return result
        except Exception as e:
            ledger.append(dict(kind=kind,id=ident,success=False,seconds=time.perf_counter()-t,error=f'{type(e).__name__}: {e}',traceback=traceback.format_exc()))
            return None
        finally:
            (out/'EXECUTION.json').write_text(json.dumps(dict(seed=seed,commands=ledger,protocol_sha256=hashlib.sha256((R/'PROTOCOL.json').read_bytes()).hexdigest(),source_commit=os.environ.get('NBO_SOURCE_COMMIT',os.environ.get('GITHUB_SHA','local')),python=sys.version,platform=platform.platform(),seconds=time.perf_counter()-start),indent=2)+'\n')
    def fit(d,method,width=32,iterations=120,tag=''):
        ident=f'{method}_d{d}_s{seed}'+tag
        row=execute('fit',ident,lambda:train(d,seed,method,iterations,.1,width,out,tag))
        path=out/f'{ident}.pt'
        return path if row and path.exists() else None
    def ev(path,steps=1024,paths=8192,**kwargs):
        kwargs=floating_initial_state(kwargs)
        return execute('evaluation',path.stem+str((steps,paths,kwargs)),lambda:evaluate(path,steps,paths,test_seed=p['final_noise_seed'],out=out,**kwargs))
    for d in p['dimensions']:
        for method in p['methods']:
            path=fit(d,method)
            if path is None:continue
            ev(path)
            if method=='nbo':
                for nt in p['refinement']['steps']:ev(path,nt,p['refinement']['paths'])
                def diag():
                    a,c,_=load(path);frozen=copy.deepcopy(a)
                    for par in frozen.parameters():par.requires_grad_(False)
                    g=torch.Generator().manual_seed(444000+seed+d);states=initial_states(d,256,g)
                    v,target,_=rollout(frozen,states,torch.tensor(coupling(d)),g,64,True)
                    _,pred,_,grad=first_jet(c,states)
                    value=float((pred-v).square().mean());costate=float((d*(grad-target)).square().mean())
                    row=dict(dimension=d,seed=seed,value_target_mse=value,costate_target_mse=costate,scope='held-out stochastic 64-step fixed-policy value/costate targets, not exact derivative bias')
                    (out/f'DIAGNOSTIC_d{d}.json').write_text(json.dumps(row,indent=2)+'\n');return row
                execute('diagnostic',path.stem,diag)
            if seed==11:
                for it in p['frontier']['iterations']:
                    cp=out/f'{method}_d{d}_s{seed}_k{it}.pt'
                    if cp.exists():ev(cp,512,2048)
                if method=='nbo':
                    for scale in p['radius_stress']['scales']:ev(path,1024,4096,radius_scale=scale)
                    for mean,sd in p['initial_state_stress']['mean_sd']:ev(path,1024,4096,shift=mean,spread=sd)
                    ev(path,1024,4096,shift=-1.,spread=1.5,profile='student3')
        if seed==11:
            for width in [16,64]:
                path=fit(d,'nbo',width,120,f'_width{width}')
                if path:ev(path,1024,4096)
            for method in ['dpo','linear']:
                path=fit(d,method,32,600,'_long')
                if path:ev(path,1024,4096)
    if seed==11:
        for name,bias in [('zero',0.),('positive_saturated',10.)]:
            a=Actor(10,32,.1);c=Critic(10,32)
            with torch.no_grad():a.net.layers[-1].bias.fill_(bias)
            path=out/f'adversary_{name}.pt';torch.save(dict(actor=a.state_dict(),critic=c.state_dict(),dimension=10,method='nbo',width=32,epsilon=.1,iteration=0),path)
            ev(path,1024,4096)
    failures=[x for x in ledger if not x['success']]
    print(json.dumps(dict(seed=seed,completed=len(ledger),failures=failures,seconds=time.perf_counter()-start)),flush=True)
    if failures:raise RuntimeError(f'{len(failures)} logged failures; no seed replacement')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seed',type=int,required=True);a=p.parse_args();run(a.seed)
