#!/usr/bin/env python3
"""Contract-normalization checks, uniformly certified portfolio signs,
joint finite-model refinements, and an actual matched-accuracy query workload."""
from __future__ import annotations
import gc,json,time,sys,hashlib
from pathlib import Path
import numpy as np
from contracts import Economy,Kernel,switching,old,ROOT
OUT=ROOT/'replication/r5/output'

def read_bank():
    z=np.load(OUT/'contract_bank.npz')
    return [dict(d=float(d),k=2.,value=z['values'][i],feature=z['features'][i],policy=z['policies'][i]) for i,d in enumerate(z['d'])]

def root_data(e,center):
    K=e.common;idx=K.index[center];weight=K.weight[center]
    base=K.base[center]-e.k*K.effort[center];duration=K.duration[center];acts=e.menu
    if e.extra:
        Z=e.extra[0];idx=np.vstack([idx,Z.index[center]]);weight=np.vstack([weight,Z.weight[center]])
        base=np.r_[base,Z.base[center]-e.k*Z.effort[center]];duration=np.r_[duration,Z.duration[center]]
        acts=np.vstack([acts,Z.actions[center]])
    return idx,weight,base,duration,acts

def sign_certificate(e,bank):
    center=int(np.argmin(np.linalg.norm(e.states-[2,1.25],axis=1)))
    idx,weight,base,duration,acts=root_data(e,center);F=np.stack([r['feature'] for r in bank])
    # At each endpoint: a feasible fixed first action followed by a fixed library
    # policy. The same pair is required at BOTH interval endpoints.
    intercept=base[None,:]+(weight[None,:,:]*(F[:,0,1]-2*F[:,2,1])[:,idx]).sum(-1)
    slopes=duration[None,:]+(weight[None,:,:]*F[:,1,1][:,idx]).sum(-1)
    bands=[]
    for left,right in zip(bank[:-1],bank[1:]):
        a,b=left['d'],right['d']
        upper_a=base+a*duration+(weight*left['value'][1,idx]).sum(-1)
        upper_b=base+b*duration+(weight*right['value'][1,idx]).sum(-1)
        entry=dict(left=a,right=b)
        for name,desired,opposite in [('positive',acts[:,2]>0,acts[:,2]<=0),('negative',acts[:,2]<0,acts[:,2]>=0)]:
            ga=intercept[:,desired]+a*slopes[:,desired]-upper_a[opposite].max()
            gb=intercept[:,desired]+b*slopes[:,desired]-upper_b[opposite].max()
            margin=np.minimum(ga,gb);loc=np.unravel_index(np.argmax(margin),margin.shape)
            entry[name+'_margin']=float(margin[loc]);entry[name+'_library']=int(loc[0]);entry[name+'_action']=acts[desired][loc[1]].tolist()
        entry['certified']='positive' if entry['positive_margin']>1e-10 else 'negative' if entry['negative_margin']>1e-10 else 'unresolved'
        bands.append(entry)
    groups=[]
    for row in bands:
        if groups and groups[-1]['sign']==row['certified']:groups[-1]['right']=row['right']
        else:groups.append(dict(sign=row['certified'],left=row['left'],right=row['right']))
    return dict(intervals=bands,groups=groups,scope='Every parameter in each reported interval; all feasible first actions of the fixed finite menu; state (2,1.25), date zero. Opposite-sign actions bounded above by convex endpoint chords.')

def direct_query_workload(e,bank):
    # Identical 101 entire-policy queries, no parameter training observations.
    ds=np.linspace(0,1,101);center=int(np.argmin(np.linalg.norm(e.states-[2,1.25],axis=1)))
    start=time.perf_counter();reused=[]
    for d in ds:
        pol=switching(bank,float(d),2.);f=e.evaluate(pol);reused.append(f[0]+d*f[1]-2*f[2])
    reuse=time.perf_counter()-start;start=time.perf_counter();loss=[]
    for i,d in enumerate(ds):
        true=e.optimal(float(d));err=true['value']-reused[i]
        assert err.min()>-1e-10
        loss.append(dict(d=float(d),max_value_loss=float(err.max()),initial_value_loss=float(err[0,center])))
        if i%20==0:print('DIRECT',i,flush=True)
    direct=time.perf_counter()-start
    return dict(queries=101,reuse_complete_policy_seconds=reuse,direct_complete_policy_seconds=direct,
                reuse_only_speed_ratio=direct/reuse,max_observed_loss=max(x['max_value_loss'] for x in loss),raw=loss)

def refinements():
    rows=[]
    configs=[((17,25),4,(5,5,7)),((33,49),8,(7,7,11)),((49,73),16,(9,9,13))]
    for shape,steps,counts in configs:
        e=Economy(shape,steps,counts,include_neural=False);center=int(np.argmin(np.linalg.norm(e.states-[2,1.25],axis=1)))
        for d in (0.,.5,1.):
            r=e.optimal(d);f=r['feature'];pol=e.controls(r['policy']);_,st=e.occupation(r['policy'],np.eye(1,e.ns,center).ravel())
            rows.append(dict(grid=list(shape),steps=steps,actions=list(counts),d=d,value=float(r['value'][0,center]),
                duration=float(f[1,0,center]),effort=float(f[2,0,center]),controls=pol[0,center].tolist(),**st))
            print('REFINE',shape,d,rows[-1]['value'],flush=True)
        del e;gc.collect()
    corr=[]
    for rho in (-.25,0.,.25):
        e=Economy((33,49),8,(7,7,11),correlation=rho,include_neural=False)
        center=int(np.argmin(np.linalg.norm(e.states-[2,1.25],axis=1)))
        for d in (0.,1.):
            r=e.optimal(d);corr.append(dict(correlation=rho,d=d,controls=e.controls(r['policy'])[0,center].tolist(),
                 value=float(r['value'][0,center]),duration=float(r['feature'][1,0,center])))
        del e;gc.collect()
    # Cost coefficient experiment: exact finite policies, all controls reoptimized.
    e=Economy((25,37),8,(9,9,13),include_neural=False);center=int(np.argmin(np.linalg.norm(e.states-[2,1.25],axis=1)));costs=[]
    for k in (.5,2.,8.):
        r=e.optimal(0.,k);C=float(r['feature'][2,0,center]);costs.append(dict(k=k,effort=C,weighted_cost=k*C,value=float(r['value'][0,center])))
    assert all(costs[j+1]['effort']<=costs[j]['effort']+1e-12 for j in range(2))
    return dict(joint_refinements=rows,correlation_robustness=corr,cost_effort=costs,
       interpretation='Grid, time, and action approximation all refined. Finite-economy robustness observations, not a Brownian stopping error bound or a calibrated estimate.')

def main():
    e=Economy();bank=read_bank();signs=sign_certificate(e,bank)
    (OUT/'sign_certificate.json').write_text(json.dumps(signs,indent=2)+'\n');print('SIGN',signs['groups'],flush=True)
    workload=direct_query_workload(e,bank);(OUT/'contract_workload.json').write_text(json.dumps(workload,indent=2)+'\n')
    del e;gc.collect();result=refinements();result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (OUT/'economic_robustness.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
