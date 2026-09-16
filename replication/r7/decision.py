#!/usr/bin/env python3
"""Two-dimensional, class-specific risk/adjustment sign certificates.
The reported sign is proved on Bernstein cells, not by the validation samples.
"""
from core import *

def allowance(mix,maxd=1.):
    kernels=[e.common for e in mix.e]+[z for e in mix.e for z in e.extra]
    assert all(k.weight.shape[-1]==16 and k.weight.min()>=0 for k in kernels)
    beta=max(float(k.weight.sum(-1).max()) for k in kernels)+1e-12
    assert beta<=1+2e-12
    R=2*max(float(abs(k.base).max()+maxd*abs(k.duration).max()+2*abs(k.effort).max()) for k in kernels)
    G=2*float(abs(mix.terminal).max());V=(G+mix.steps*R)*max(1.,beta)**mix.steps
    operations=4096*(mix.steps+1);u=np.finfo(float).eps/2;gamma=operations*u/(1-operations*u)
    error=2*gamma*(1+2*V+R)*max(1.,beta)**mix.steps
    return dict(per_class_allowance=error,unit_roundoff=u,operation_budget=operations,
        absolute_reward_bound=R,value_magnitude_bound=V,row_mass_bound=beta,
        largest_intermediate_contract=maxd,scope='IEEE round-to-nearest bound relative to stored finite kernel/reward arrays; not discretization or kernel-generation error')

def run(mix=None):
    begin=time.perf_counter();mix=build() if mix is None else mix
    center=int(np.linalg.norm(mix.e[0].states-[2,1.25],axis=1).argmin());rounding=allowance(mix);err=rounding['per_class_allowance']
    bank={};uppers={};checks=[];arrays={};coefficient_arrays={};bank_manifest=[];counters={'anchor_solves':0,'count_constructions':0}
    def anchor(t,d,adj):
        key=(t,d,adj)
        if key not in bank:
            z=classes(mix,t,d,adj);counters['anchor_solves']+=1
            for name,item in z.items():
                p=item['policy'];actions=mix.e[0].controls(p)
                if not adj:assert np.max(np.abs(actions[:,:,1]))==0.
                if name=='positive':assert np.min(actions[0,:,2])>0
                else:assert np.max(actions[0,:,2])<=0
                co0=mix.policy_coefficients(p,0.);co1=mix.policy_coefficients(p,1.)
                item['intercept']=co0[0][:,center];item['duration']=co1[0][:,center]-co0[0][:,center]
                direct=mix.evaluate(p,t,d)
                replay=max(float(abs(direct-item['value']).max()),float(abs(bernstein_value(co0[0]+d*(co1[0]-co0[0]),t)[center]-direct[0,center])))
                assert replay<2e-11
                checks.append(dict(theta=t,d=d,adjustment=adj,sign=name,evaluation_error=replay,value=float(direct[0,center]),first_risk_min=float(actions[0,:,2].min()),first_risk_max=float(actions[0,:,2].max()),maximum_absolute_adjustment=float(abs(actions[:,:,1]).max())))
                ix=len(bank_manifest);arrays[f'policy.{ix}']=p;arrays[f'base.{ix}']=item['intercept'];arrays[f'duration.{ix}']=item['duration']
                bank_manifest.append(dict(index=ix,theta=t,d=d,adjustment=adj,sign=name))
            bank[key]=z
        return bank[key]
    def upper(a,b,d,adj,sign):
        key=(a,b,d,adj,sign)
        if key not in uppers:
            za=anchor(a,d,adj)[sign];zb=anchor(b,d,adj)[sign]
            co=count(mix,a,b,d,za['value'],zb['value'],adj,sign)
            uppers[key]=co[0][:,center];counters['count_constructions']+=1
        return uppers[key]
    cells=[];attempts=[]
    def inspect(a,b,dl,dh,level):
        bounds={};gaps={}
        for adj in (True,False):
            U={s:np.stack([upper(a,b,d,adj,s) for d in (dl,dh)]) for s in ('positive','nonpositive')}
            L={s:[] for s in U}
            for s in U:
                for t in (a,b):
                    for da in (dl,dh):
                        z=anchor(t,da,adj)[s]
                        L[s].append(np.stack([restrict(z['intercept']+d*z['duration'],a,b) for d in (dl,dh)]))
            cid=len(attempts);arm='adjusted' if adj else 'fixed'
            for s in U:
                coefficient_arrays[f'cell.{cid}.{arm}.{s}.upper']=U[s]
                coefficient_arrays[f'cell.{cid}.{arm}.{s}.lower']=np.stack(L[s])
            lower=max(float((l-U['nonpositive']).min()) for l in L['positive'])-2*err
            higher=min(float((U['positive']-l).max()) for l in L['nonpositive'])+2*err
            bounds['adjusted' if adj else 'fixed']=[lower,higher]
            gaps['adjusted' if adj else 'fixed']={s:max(0.,min(float((U[s]-l).max()) for l in L[s]))+2*err for s in U}
        rec=dict(theta=[a,b],d=[dl,dh],level=level,delta=bounds,class_gaps=gaps)
        good=bounds['adjusted'][0]>0 and bounds['fixed'][1]<0
        rec['accepted']=good;attempts.append(rec)
        print('DECISION',a,b,dl,dh,level,bounds,'ACCEPT' if good else 'SPLIT',flush=True)
        if good:cells.append(rec)
        else:
            if level>=8:raise RuntimeError('decision precision not reached at declared maximum depth')
            if level%2==0:
                mid=(a+b)/2;inspect(a,mid,dl,dh,level+1);inspect(mid,b,dl,dh,level+1)
            else:
                mid=(dl+dh)/2;inspect(a,b,dl,mid,level+1);inspect(a,b,mid,dh,level+1)
    inspect(0.,.25,.4,.45,0)
    area=sum((r['theta'][1]-r['theta'][0])*(r['d'][1]-r['d'][0]) for r in cells)
    assert abs(area-.25*.05)<1e-14
    result=dict(region={'theta':[0.,.25],'d':[.4,.45]},initial_state=mix.e[0].states[center],
        full_states=mix.ns,dates=mix.steps,full_actions=len(mix.e[0].menu)+3,cost=2.,
        minimum_adjusted_advantage=min(z['delta']['adjusted'][0] for z in cells),
        minimum_fixed_disadvantage=min(-z['delta']['fixed'][1] for z in cells),
        minimum_relative_option=sum([min(z['delta']['adjusted'][0] for z in cells),min(-z['delta']['fixed'][1] for z in cells)]),
        cells=cells,attempts=attempts,roundoff=rounding,checks=checks,counts=counters,
        bank_manifest=bank_manifest,elapsed_seconds=time.perf_counter()-begin,scope='entire joint parameter rectangle at the stated initial state; first risk sign and all-date adjustment restriction; stored finite target')
    np.savez_compressed(OUT/'decision_policy_bank.npz',**arrays)
    np.savez_compressed(OUT/'decision_coefficients.npz',**coefficient_arrays)
    save('decision.json',result);return result
if __name__=='__main__':run()
