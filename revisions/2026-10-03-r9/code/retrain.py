"""Fresh R8 neural blocks on nested grids, with an optional critic residual guard.
The guard uses the selected policy's own target, not an optimizing action label.
Its indexed corrections and uncorrected outputs are retained and costed.
"""
from __future__ import annotations
import argparse,json,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'revisions/2026-10-03-r8/code'))
import continuous_actor as base
OUT=Path(__file__).resolve().parents[1]/'results'

def run(nu=33,nx=49,steps=40,seed=11,method='actor',guard=False):
    if method not in ['actor','search']:raise ValueError(method)
    oldmodel,oldout,oldfit,oldput=base.Model,base.OUT,base.fit_critic,base.put_weights
    folder=OUT/f'grid_{nu}_{nx}_{steps}{"_guarded" if guard else ""}'
    folder.mkdir(parents=True,exist_ok=True)
    base.Model=lambda *args,**kw:oldmodel(nu,nx,steps)
    base.OUT=folder;state={};tau=.1/steps**2
    def guarded_fit(net,x,terminal,lifting,target,adam,polish,counters):
        value=oldfit(net,x,terminal,lifting,target,adam,polish,counters)
        selected=np.nextafter(np.abs(value-target),np.inf)>tau
        delta=np.where(selected,target-value,0.)
        result=np.where(selected,target,value)
        state['delta']=delta;state['selected']=selected;state['raw']=value.copy()
        counters['critic_guard_changed_nodes']=counters.get('critic_guard_changed_nodes',0)+int(selected.sum())
        counters['critic_guard_total_nodes']=counters.get('critic_guard_total_nodes',0)+len(selected)
        counters['critic_guard_tolerance']=tau
        counters['critic_guard_max_residual']=max(counters.get('critic_guard_max_residual',0.),float(np.nextafter(abs(result-target).max(),np.inf)))
        return result
    def save_weights(saved,net,prefix):
        oldput(saved,net,prefix)
        if guard and prefix.startswith('critic_t'):
            saved[prefix+'indexed_correction']=state['delta'].copy()
            saved[prefix+'correction_mask']=state['selected'].copy()
            saved[prefix+'uncorrected_nodal_values']=state['raw'].copy()
    if guard:base.fit_critic=guarded_fit;base.put_weights=save_weights
    try:
        result=base.solve(seed=seed,method='actor' if method=='actor' else 'direct',actor_steps=160 if method=='actor' else 0,critic_steps=320,polish=300,search=True)
    finally:base.Model,base.OUT,base.fit_critic,base.put_weights=oldmodel,oldout,oldfit,oldput
    result['continuation_guard']=guard
    result['deployment_object']='nodal hybrid policy; fitted neural critic plus explicit indexed residual correction' if guard else 'nodal actor/search hybrid; uncorrected fitted critic'
    if guard:
        c=result['counters'];result['critic_guard_fraction']=c['critic_guard_changed_nodes']/c['critic_guard_total_nodes']
        result['critic_guard_rate']='tau_h=0.1*h^2 on the discrete target, by construction; not a convergence rate for Adam'
    (folder/Path(result['raw_file']).with_suffix('.json')).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'final_run':result['raw_file'],'grid':[nu,nx,steps],'guard':guard,'guard_fraction':result.get('critic_guard_fraction'),'max_finite_reference_advantage':result['finite_reference_minus_policy_max']}),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--nu',type=int,default=33);p.add_argument('--nx',type=int,default=49);p.add_argument('--steps',type=int,default=40)
    p.add_argument('--seed',type=int,default=11);p.add_argument('--method',choices=['actor','search'],default='actor');p.add_argument('--guard',action='store_true');a=p.parse_args()
    run(a.nu,a.nx,a.steps,a.seed,a.method,a.guard)
