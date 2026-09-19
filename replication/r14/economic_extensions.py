"""Executed R14 experiments on the unchanged, hash-identified settlement arrays.

No output is treated as a theorem premise unless independently reconstructed.
The projection diagnostic concerns a local moment, not a value-error bound.
"""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,time,resource,itertools
from pathlib import Path
from fractions import Fraction as Q
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'replication/r13'))
from canonical import load,dump,digest
from engine import Engine,SIGNS
from certified_arithmetic import derive,upward,downward
from oracle_polytope import response_polytope,encode
from continuous_fees import maximize,frac
D0=.42425;LAM=.125;EPS=1e-10

def moment(b,j):
    # Select an interior, drift-free preference action with zero financial risk.
    ids=np.flatnonzero((abs(j.fm.actions[:,1])<1e-14)&(abs(j.fm.actions[:,2])<1e-14))
    if not len(ids):raise ValueError('no drift-free interior moment row')
    i=int(ids[np.argmin(j.fm.actions[ids,0])]);u=b.e[0].states[:,0];mom=[]
    for k in (0,1):
        row=j.fm.rows[k].getrow(i);mass=sum(frac(x) for x in row.data)
        mean=sum(frac(x)*frac(u[v]) for x,v in zip(row.data,row.indices))/mass
        var=sum(frac(x)*(frac(u[v])-mean)**2 for x,v in zip(row.data,row.indices))/mass
        mom.append(dict(mass=encode(mass),mean=encode(mean),variance=encode(var),variance_float=float(var)))
    target=Q(5,100)**2/Q(8)
    return dict(action=j.fm.actions[i].tolist(),initial_preference=2.,time_step='1/8',preference_mesh='1/20',diffusion_variance=encode(target),stored_rows=mom,variance_ratio=mom[0]['variance_float']/float(target),variance_excess=mom[0]['variance_float']-float(target),interpretation='Exact rational second moment of normalized stored live-state row. The matching unprojected drift-free diffusion increment has variance sigma_u^2 dt. This diagnostic is not a bound on private value or purchaser surplus and does not certify the diffusion-to-array approximation.')

def oracle(j):
    cases=[]
    for adj,m,F in [(True,2,.625),(False,4,.525)]:
        hh=.02;offsets=[[0.,0.],[hh,0.],[-hh,0.],[0.,hh],[0.,-hh],[hh,F*hh],[-hh,-F*hh]]
        qs=[]
        for td,tf in offsets:
            # Feature coordinates are (duration, surrender), so +tf is -fee.
            z=j.solve(LAM,D0+td,F-tf,adj,.8,.5,m=m)
            qs.append(dict(offset=[td,tf],d=D0+td,F=F-tf,values={s:float(z['first'][s]['value']) for s in SIGNS}))
            j.cache.clear()
        for sign in SIGNS:
            for eta in (0.,1e-4):
                runs=[]
                for n,name in [(5,'coordinate_queries'),(7,'joint_queries')]:
                    vals=[r['values'][sign] for r in qs[:n]]
                    lp,ix=response_polytope(offsets[:n],[frac(x)-frac(EPS) for x in vals],[frac(x)+frac(EPS) for x in vals],[(0,1),(0,1)],eta)
                    c=[Q(0)]*len(lp.box);c[2]=Q(1);c[3]=frac(F)
                    ans=maximize(lp,c)
                    runs.append(dict(name=name,lp=lp.json(),objective=[encode(x) for x in c],dual=ans))
                cases.append(dict(adjustment=adj,term=m,fee=F,sign=sign,eta=eta,queries=qs,runs=runs,upper_reduction=runs[0]['dual']['certified_upper']-runs[1]['dual']['certified_upper']))
    return dict(cases=cases,scope='Same settlement target. Sharpness of the lifted polytope is across affine-response economies consistent with these queries; fixed-MDP response feasibility can tighten it further.')

def mechanisms(b,j):
    rows=[];archive={}
    for lam,d,F,m in itertools.product((0.,.125,1.),(.35,D0,.5),(0.,.4,.8),(1,4)):
        za=j.solve(lam,d,F,True,.8,.5,m=m);z0=j.solve(lam,d,F,False,.8,.5,m=m)
        O=za['v'][1]-z0['v'][1];tag='m%03d'%len(rows)
        archive[tag+'.adjusted_v']=za['v'][1:];archive[tag+'.fixed_v']=z0['v'][1:]
        classes={};kernels={}
        for sign in SIGNS:
            f=za['first'][sign]
            if len(f['indices'])!=1:raise ValueError('unexpected non-knot first action in mechanism map')
            action=f['action'].copy();action[1]=0.
            ids=np.flatnonzero(np.all(abs(j.fm.actions-action)<1e-14,axis=1))
            if len(ids)!=1:raise ValueError('unavailable zero-drift counterfactual')
            i=int(ids[0]);K=(1-lam)*j.fm.rows[0].getrow(i)+lam*j.fm.rows[1].getrow(i);kernels[sign]=K
            qa=float(((1-lam)*j.q(0,za['v'][1],d)+lam*j.q(1,za['v'][1],d))[i]);q0=float(((1-lam)*j.q(0,z0['v'][1],d)+lam*j.q(1,z0['v'][1],d))[i])
            classes[sign]=dict(local=float(f['value']-qa),future=float((K@O).item()),replacement=float(q0-z0['first'][sign]['value']),option=float(f['value']-z0['first'][sign]['value']),first_action=f['action'].tolist(),zero_counterfactual_index=i,adjusted_value=float(f['value']),fixed_value=float(z0['first'][sign]['value']))
        signed=kernels['positive']-kernels['nonpositive'];dif={k:classes['positive'][k]-classes['nonpositive'][k] for k in ('local','future','replacement','option')}
        residual=dif['option']-sum(dif[k] for k in ('local','future','replacement'))
        if abs(residual)>2e-11:raise ValueError('mechanism identity failed')
        er=2*EPS*float(abs(signed).sum());wealth=b.e[0].states[:,1]
        bins=[float((signed@(O*mask)).item()) for mask in (wealth<1.25,wealth>=1.25)]
        rows.append(dict(id=tag,law=lam,d=d,fee=F,term=m,classes=classes,difference=dif,future_interval=[dif['future']-er,dif['future']+er],wealth_contributions=bins,identity_residual=residual))
        j.cache.clear();print('MECHANISM',tag,lam,d,F,m,dif,flush=True)
    return dict(rows=rows,grid=dict(laws=[0.,.125,1.],benefits=[.35,D0,.5],fees=[0.,.4,.8],terms=[1,4]),scope='54 explicitly enumerated points, including adverse cases; not a continuum sign theorem.'),archive

if __name__=='__main__':
    t=time.perf_counter();b,j=load(ROOT/'replication/r13/canonical');audit=derive(b,j,EPS);out=HERE/'output'
    diagnostic=moment(b,j);joint=oracle(j);mech,archive=mechanisms(b,j)
    np.savez_compressed(out/'mechanism_values.npz',**archive)
    dump(out/'economic_extensions.json',dict(schema='nbo-r14-economic-extensions-v1',canonical_manifest_sha256=digest(ROOT/'replication/r13/canonical/manifest.json'),arithmetic=audit,projection_diagnostic=diagnostic,joint_oracle=joint,mechanisms=mech,mechanism_values_sha256=digest(out/'mechanism_values.npz'),elapsed_seconds=time.perf_counter()-t,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
    print('ECONOMIC EXTENSIONS DONE',flush=True)
