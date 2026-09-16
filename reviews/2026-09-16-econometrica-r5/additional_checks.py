#!/usr/bin/env python3
"""Referee extension: a common-mesh policy bank against the ORIGINAL full target.
Reuses the 47 deposited anchor locations and full-target optimal upper values.
No learned action is allowed in any lower-bound policy. This is not an
end-to-end timing comparison or a claim of autonomous anchor discovery.
Also re-executes the author's all-nine resource and all-date game validators,
without calling their main() or overwriting any author output.
"""
from __future__ import annotations
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[k]='1'
import argparse, hashlib, json, platform, sys
from pathlib import Path
import numpy as np

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path(__file__).with_name('additional_results.json'));args=p.parse_args()
    root=Path(__file__).resolve().parents[2];sys.path[:0]=[str(root/'replication/r5'),str(root/'replication/r4')]
    import contracts as c
    import importlib.util
    spec=importlib.util.spec_from_file_location('nbo_r5_author_validation',root/'replication/r5/validate.py')
    assert spec is not None and spec.loader is not None
    v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
    import scipy,torch
    e=c.Economy();e.extra=[]
    z=np.load(root/'replication/r5/output/contract_bank.npz');ds=z['d'];upper=z['values']
    bank=[];loss=[];replay=0.;bellman=0.
    for i,d in enumerate(ds):
        r=e.optimal(float(d));bank.append(r)
        replay=max(replay,float(abs(e.evaluate(r['policy'])-r['feature']).max()))
        bellman=max(bellman,float(e.one_step_gain(r['value'],float(d)).max()))
        loss.append(float((upper[i]-r['value']).max()))
        if i%10==0:print('RESTRICTED_BANK',i,flush=True)
    rows=[]
    for i in range(len(ds)-1):
        a,b=ds[i:i+2];Fa,Fb=bank[i]['feature'],bank[i+1]['feature']
        ia,ib=Fa[0]-2*Fa[2],Fb[0]-2*Fb[2];sa,sb=Fa[1],Fb[1]
        den=sa-sb;cross=np.divide(ib-ia,den,out=np.full_like(den,a),where=abs(den)>1e-14)
        best=-np.inf;loc=None
        for d in (np.full_like(den,a),np.full_like(den,b),np.clip(cross,a,b)):
            lam=(d-a)/(b-a);gap=(1-lam)*upper[i]+lam*upper[i+1]-np.maximum(ia+d*sa,ib+d*sb)
            if gap.max()>best:
                best=float(gap.max());idx=np.unravel_index(np.argmax(gap),gap.shape)
                loc=dict(date=int(idx[0]),state=e.states[idx[1]].tolist(),d=float(d[idx]))
        rows.append(dict(left=float(a),right=float(b),upper_loss=best,location=loc))
    bound=max(r['upper_loss'] for r in rows)
    # Numerical replay of switches supplements, but does NOT establish, the
    # exact piecewise-affine all-parameter certificate just computed.
    F=np.stack([r['feature'] for r in bank]);switch_defect=0.;max_query_upper=0.
    for d in np.random.default_rng(9162027).uniform(0,1,31):
        pol=c.switching(bank,float(d),2.);f=e.evaluate(pol);J=f[0]+d*f[1]-2*f[2]
        L=np.max(F[:,0]+d*F[:,1]-2*F[:,2],axis=0)
        j=min(np.searchsorted(ds,d,side='right')-1,len(ds)-2);lam=(d-ds[j])/(ds[j+1]-ds[j]);U=(1-lam)*upper[j]+lam*upper[j+1]
        switch_defect=max(switch_defect,float((L-J).max()));max_query_upper=max(max_query_upper,float((U-J).max()))
        assert pol.max()<len(e.menu) and (J-U).max()<2e-10
    assert replay<2e-11 and bellman<2e-10 and switch_defect<2e-10 and max_query_upper<=bound+2e-10
    result=dict(reviewed_commit='c9f71077cf6a339573ac07be55d7660797bcf6ea',
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        environment=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,torch=torch.__version__,platform=platform.platform()),
        common_mesh_bank=dict(anchors=len(ds),common_actions=len(e.menu),neural_actions_allowed=False,
            original_full_target_upper_values_used=True,anchor_locations_reused=True,
            max_anchor_loss_vs_full_target=max(loss),uniform_loss_bound_vs_full_target=bound,
            common_menu_bellman_gain=bellman,feature_replay_error=replay,
            random_switching_defect=switch_defect,random_switch_upper=max_query_upper,intervals=rows,
            scope='All original finite-model states, dates, and d in [0,1], k=2; same full target upper oracle; no Brownian or timing claim.'))
    print('COMMON_MESH_UNIFORM_BOUND',bound,flush=True)
    del e,bank,F
    import gc;gc.collect()
    result['author_resource_validator_reexecution']=v.test_resources()
    result['author_game_validator_reexecution']=v.test_game()
    args.output.write_text(json.dumps(result,indent=2)+'\n');print('WROTE',args.output,flush=True)
if __name__=='__main__':main()
