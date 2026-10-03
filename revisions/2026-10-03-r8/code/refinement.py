"""Common frozen-policy space/time refinements; differences are not bounds."""
from __future__ import annotations
import json,time,hashlib
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from continuous_actor import Model,NDU,OUT

def run():
    records=[];arrays={};levels=[(17,25,20),(25,37,40),(33,49,80)]
    for method in ['actor','direct']:
      for seed in [11,29,47]:
        path=OUT/f'continuous_{method}_s{seed}_search.npz';z=np.load(path);base=Model();policy=z['policy']
        for nu,nx,nt in levels:
          begin=time.perf_counter();m=Model(nu,nx,nt);pi=np.empty((nt,m.N,3))
          for t in range(nt):
            j=min(base.steps-1,t*base.steps//nt)
            pi[t]=RegularGridInterpolator((base.us,base.ys),policy[j].reshape(base.nu,base.nx,3),bounds_error=True)(m.points)
          pv=m.evaluate(pi);refmodel=NDU(nu,nx,nt);ref,_,_=refmodel.reference();c=(nu//2)*nx+nx//2
          key=f'{method}_s{seed}_{nu}_{nx}_{nt}';arrays[key+'_payoff']=pv;arrays[key+'_reference']=ref
          records.append(dict(method=method,seed=seed,grid=[nu,nx],steps=nt,center_policy_payoff=float(pv[0,c]),
            center_finite_reference=float(ref[0,c]),finite_reference_minus_policy=float(np.max(ref-pv)),
            reference_actions=refmodel.A,seconds=time.perf_counter()-begin,
            frozen_source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            controls='bilinear state interpolation of the same stored policy; left-constant original time schedule',
            scope='nested-grid diagnostics; no monotonicity of errors or continuous-time bias bound is inferred'))
    np.savez_compressed(OUT/'REFINEMENT.npz',**arrays)
    result=dict(records=records,continuous_state_time_error=None,
                raw_sha256=hashlib.sha256((OUT/'REFINEMENT.npz').read_bytes()).hexdigest())
    (OUT/'REFINEMENT.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(json.dumps(run()))
