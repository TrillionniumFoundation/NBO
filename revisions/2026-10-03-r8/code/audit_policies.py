"""Reuse verified optimal upper arrays, but evaluate each frozen policy anew."""
from __future__ import annotations
import json,time,hashlib
import numpy as np
from action_enclosure import Model,Encloser,I,terminal,up,OUT

def audit():
    sources=[OUT/'continuous_actor_s11_search_action_certificate.npz']
    tight=OUT/'continuous_actor_s11_search_corner_certificate.npz'
    if tight.exists():sources.append(tight)
    best=np.minimum.reduce([np.load(p)['optimal_upper'] for p in sources])
    m=Model();rows=np.arange(m.N);g=terminal(I(m.points[:,0]),I(m.points[:,1]));records=[];saved={}
    for method in ['actor','direct','local']:
      for seed in [11,29,47]:
        stem=f'continuous_{"direct" if method=="local" else method}_s{seed}'+('_steps0' if method=='local' else '')+'_search'
        raw=OUT/f'{stem}.npz';z=np.load(raw);meta=json.loads(raw.with_suffix('.json').read_text())
        for raw_actor in [False,True]:
          tag=stem+('_raw' if raw_actor else '_hybrid');pi=z['raw_policy' if raw_actor else 'policy']
          lo,hi=g.lo.copy(),g.hi.copy();lower=[lo.copy()];upper=[hi.copy()];start=time.perf_counter()
          for t in range(m.steps-1,-1,-1):
            v=Encloser(m,lo,hi).q(rows,pi[t]);lo,hi=v.lo,v.hi;lower.append(lo.copy());upper.append(hi.copy())
          lower=np.array(lower[::-1]);upper=np.array(upper[::-1]);regret=up(best-lower)
          saved[tag+'_lower']=lower;saved[tag+'_upper']=upper
          maxreg=float(regret.max());center=(m.nu//2)*m.nx+m.nx//2
          records.append(dict(method=method,seed=seed,raw=raw_actor,
            policy_regret_upper=maxreg,initial_state_regret_upper=float(regret[0,center]),
            policy_evaluation_bracket_max=float(np.max(up(upper-lower))),evaluation_seconds=time.perf_counter()-start,
            absolute_target_pass={str(t):maxreg<=t for t in [.05,.1,.2,.3]},
            input=raw.name,input_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
            scope='all stored states/times and all continuous actions in the fixed box; no continuous-state/time transfer'))
    saved['common_optimal_upper']=best;path=OUT/'SHARED_ACTION_CERTIFICATES.npz';np.savez_compressed(path,**saved)
    result=dict(records=records,upper_sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        raw_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),continuous_state_time_error=None,
        sharing='one optimal upper array, independently propagated lower/upper payoff arrays for every frozen policy')
    (OUT/'SHARED_ACTION_CERTIFICATES.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return result
if __name__=='__main__':print(json.dumps(audit()))
