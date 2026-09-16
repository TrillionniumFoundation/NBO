#!/usr/bin/env python3
"""Reviewer time-mesh sensitivity, not a diffusion convergence certificate.
Preserves the full union of both author mesh menus, no neural proposals; source
R7 already has a separate matched ablation against the unchanged full target.
Only the number of dates changes. The state grid and primitives stay fixed.
"""
from __future__ import annotations
import argparse,gc,json,os,sys,time
from pathlib import Path
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--horizons',nargs='+',type=int,default=[8]);a=ap.parse_args()
    sys.path.insert(0,str(a.repo.resolve()/'replication/r7'));import core;import numpy as np
    menu=np.unique(np.concatenate([core.c.old.action_mesh((9,9,13)),core.c.old.action_mesh((7,7,11))]),axis=0)
    def economy(h,corr):
        e=core.c.Economy.__new__(core.c.Economy);e.shape=(33,49);e.steps=h;e.k=2.;e.model=core.c.old.Model(k=2.,correlation=corr)
        ss,bd=core.c.old.grid(*e.shape);e.states=ss.reshape(-1,2);e.boundary=bd.ravel();e.ns=len(e.states);e.menu=menu
        e.common=core.c.Kernel(e.states,e.menu,e.shape,1./h,e.model);e.extra=[];e.r4=[];e.counts=[9,9,13];e.build_seconds=0.;return e
    result={'reviewed_commit':'fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17','scope':'finite-model temporal sensitivity; fixed 33x49 state grid and 1565-action union mesh, no neural proposals; not a continuum certificate','rows':[]}
    for h in a.horizons:
        start=time.perf_counter();mix=core.Mixture(economy(h,-.25),economy(h,.25));center=int(np.linalg.norm(mix.e[0].states-[2.,1.25],axis=1).argmin());rows=[]
        for t,d in [(0.,.4),(0.,.45),(.125,.425),(.25,.4),(.25,.45)]:
            for adj in (True,False):
                z=core.classes(mix,t,d,adj);vp=float(z['positive']['value'][0,center]);vm=float(z['nonpositive']['value'][0,center]);err=0.
                for item in z.values():err=max(err,float(abs(mix.evaluate(item['policy'],t,d)-item['value']).max()))
                assert err<2e-11
                row={'dates':h,'lambda':t,'d':d,'adjustment':adj,'positive_value':vp,'nonpositive_value':vm,'delta':vp-vm,'positive_control':menu[z['positive']['policy'][0,center]],'nonpositive_control':menu[z['nonpositive']['policy'][0,center]],'policy_replay_error':err}
                rows.append(row);print('TIME',h,t,d,adj,vp-vm,flush=True)
                partial=dict(result);partial['in_progress']={'dates':h,'points':rows};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(core.serial(partial),indent=2,allow_nan=False)+'\n')
        result['rows'].append({'dates':h,'points':rows,'elapsed_seconds':time.perf_counter()-start})
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(core.serial(result),indent=2,allow_nan=False)+'\n')
        for e in mix.e:
            if hasattr(e.common,'original_continuation'):del e.common.original_continuation
        del mix,z,e;gc.collect()
if __name__=='__main__':main()
