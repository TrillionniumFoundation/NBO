#!/usr/bin/env python3
"""R7 reviewer checks: author-suite replay and matched neural-free lower bank.
Uses the author's finite target and kernel executor, NOT an independent
reimplementation of the stopped diffusion. Never writes author output files.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys, time
from pathlib import Path
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'): os.environ[k]='1'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    root=args.repo.resolve();sys.path.insert(0,str(root/'replication/r7'))
    import core
    sys.path.insert(0,str(root/'replication/r7'))
    import decision, validate, primitive
    import numpy as np
    result={'reviewed_commit':'fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17','scope':'matched neural-free feasible lower policies against unchanged deposited full-menu class upper tensors; author kernel executor reused','environment':{'python':sys.version,'numpy':np.__version__}}
    def write():
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(core.serial(result),indent=2,allow_nan=False)+'\n')
    inv=json.loads((root/'revisions/2026-09-16-r7/source_inventory.json').read_text())
    bad=[p for p,h in inv.items() if hashlib.sha256((root/p).read_bytes()).hexdigest()!=h]
    assert not bad;result['source_inventory']={'entries':len(inv),'mismatches':bad}
    captures={}
    validate.save=lambda name,data:captures.__setitem__(name,core.serial(data))
    primitive.save=validate.save
    validate.run();validate.replay_decision();primitive.run()
    result['author_suite_replay']=captures;write();print('AUTHOR SUITE PASS',flush=True)
    begin=time.perf_counter();mix=core.build();build_seconds=time.perf_counter()-begin
    meta=json.loads((root/'replication/r7/output/decision.json').read_text())
    coeff=np.load(root/'replication/r7/output/decision_coefficients.npz')
    center=int(np.linalg.norm(mix.e[0].states-[2.,1.25],axis=1).argmin());err=decision.allowance(mix)['per_class_allowance']
    nmenu=len(mix.e[0].menu)
    def solve_classes(t,d,adj):
        v=np.empty((mix.steps+1,mix.ns));v[-1]=mix.terminal;p=np.empty((mix.steps,mix.ns),np.int32)
        for n in range(mix.steps-1,-1,-1):
            q=((1-t)*mix.q(0,n,v[n+1],d)+t*mix.q(1,n,v[n+1],d))[:,:nmenu]
            allow=np.ones(nmenu,bool) if adj else np.abs(mix.e[0].menu[:,1])<=1e-14
            q=np.where(allow,q,-np.inf);p[n]=q.argmax(1);v[n]=q[np.arange(mix.ns),p[n]]
        out={}
        for sign in ('positive','nonpositive'):
            ok=mix.e[0].menu[:,2]>0 if sign=='positive' else mix.e[0].menu[:,2]<=0
            qq=np.where(ok,q,-np.inf);pp=p.copy();pp[0]=qq.argmax(1);vv=v.copy();vv[0]=qq.max(1)
            assert pp.max()<nmenu
            b=mix.policy_coefficients(pp,0.);one=mix.policy_coefficients(pp,1.)
            intercept=b[0][:,center];duration=one[0][:,center]-intercept
            evaluated=mix.evaluate(pp,t,d);replay=float(abs(evaluated-vv).max());assert replay<2e-11
            out[sign]={'intercept':intercept,'duration':duration,'focal_value':vv[0,center],'control':mix.e[0].menu[pp[0,center]],'replay_error':replay}
        return out
    rows=[];corners=[]
    for adj in (True,False):
        arm='adjusted' if adj else 'fixed';low={s:[] for s in ('positive','nonpositive')}
        for t in (0.,.25):
            for d in (.4,.45):
                z=solve_classes(t,d,adj)
                for s,item in z.items():
                    low[s].append(np.stack([core.restrict(item['intercept']+dd*item['duration'],0.,.25) for dd in (.4,.45)]))
                    corners.append({'adjustment':adj,'lambda':t,'d':d,'sign':s,'value':item['focal_value'],'control':item['control'],'replay_error':item['replay_error']})
                print('MESH CORNER',adj,t,d,z['positive']['focal_value']-z['nonpositive']['focal_value'],flush=True)
        upper={s:coeff[f'cell.0.{arm}.{s}.upper'] for s in low}
        lo=max(float((v-upper['nonpositive']).min()) for v in low['positive'])-2*err
        hi=min(float((upper['positive']-v).max()) for v in low['nonpositive'])+2*err
        gaps={s:max(0.,min(float((upper[s]-v).max()) for v in low[s]))+2*err for s in low}
        rows.append({'adjustment':adj,'delta_interval':[lo,hi],'class_gaps':gaps})
    result['mesh_only_lower_against_original_full_target']={'common_actions':nmenu,'excluded_neural_actions_per_state_date':3,'dates':mix.steps,'states':mix.ns,'region':meta['region'],'initial_state':mix.e[0].states[center],'per_class_arithmetic_allowance':err,'rows':rows,'corners':corners,'build_seconds':build_seconds,'elapsed_seconds':time.perf_counter()-begin,'positive_reversal_certified':bool(rows[0]['delta_interval'][0]>0 and rows[1]['delta_interval'][1]<0)}
    result['tracked_inputs_unchanged']=all(hashlib.sha256((root/p).read_bytes()).hexdigest()==h for p,h in inv.items());assert result['tracked_inputs_unchanged'];write()
    print(json.dumps(core.serial(result['mesh_only_lower_against_original_full_target']),indent=2),flush=True)
if __name__=='__main__':main()
