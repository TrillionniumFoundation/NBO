"""Matched action-cover work and shared nested-grid policy accounts."""
from __future__ import annotations
import json,time
import numpy as np
from action_cover import ROOT,R8,OUT,Model,CornerEncloser,maximize,I,up
import action_enclosure as old_cover
from audit import save,sha,payoff_envelope,full_domain

def matched_cover():
    p=OUT/'continuous_actor_s29_search_signed_cover.npz';z=np.load(p);v=z['optimal_upper'];pi=np.load(R8/'results/continuous_actor_s29_search.npz')['policy'];m=Model();records=[]
    for t in [19,10,0]:
        for method in ['corner','signed']:
            begin=time.perf_counter()
            if method=='signed':upper,proposal,stats=maximize(m,v[t+1],pi[t],tolerance=.0002,max_depth=40,max_boxes=500000)
            else:
                old=old_cover.Encloser;old_cover.Encloser=CornerEncloser
                try:upper,stats=old_cover.maximize(m,v[t+1],pi[t],tolerance=.0002,max_depth=40,max_boxes=500000)
                finally:old_cover.Encloser=old
            records.append(dict(method=method,time_index=t,elapsed=time.perf_counter()-begin,**{k:q for k,q in stats.items() if k!='history'}))
    return save('MATCHED_COVER',dict(records=records,continuation_sha256=sha(p),same_continuation=True,same_initial_policy=True,
       scope='one-step enclosure comparison on identical continuation arrays, feasible incumbents, tolerance and budget; includes gradient work in wall time'))

def nested_accounts():
    cp=OUT/'fine_guarded_signed_cover.npz';z=np.load(cp);opt=z['optimal_upper'];meta=json.loads(cp.with_suffix('.json').read_text());m=Model(33,49,40);records=[];arrays={}
    for folder in sorted(OUT.glob('grid_33_49_40*')):
      for p in sorted(folder.glob('*.npz')):
        info=json.loads(p.with_suffix('.json').read_text());zz=np.load(p);pi=zz['policy'];begin=time.perf_counter();lo,hi=payoff_envelope(m,pi);secs=time.perf_counter()-begin
        gap=up(opt-lo);tag=folder.name+'_'+p.stem;arrays[tag+'_lower']=lo;arrays[tag+'_upper']=hi
        residual=0.
        for t in range(m.steps):
            q=CornerEncloser(m,zz['values'][t+1]).q(np.arange(m.N),pi[t]);rr=I(zz['values'][t])-q
            residual=max(residual,float(np.max(rr.absmax())))
        records.append(dict(method='actor' if info['method']=='actor' else 'search',seed=info['seed'],guarded=info.get('continuation_guard',False),
          source=str(p.relative_to(ROOT)),source_sha256=sha(p),training_seconds=info['training_seconds'],
          policy_evaluation_seconds=secs,shared_cover_seconds=meta['seconds'],regret_upper=float(gap.max()),
          all_node_target_pass=bool(gap.max()<=.1),guard_fraction=info.get('critic_guard_fraction'),
          max_indexed_target_residual=info.get('counters',{}).get('critic_guard_max_residual'),independent_policy_residual_upper=residual,
          indexed_correction_uncompressed_bytes=sum(zz[k].nbytes for k in zz.files if 'indexed_correction' in k or 'correction_mask' in k),
          correction_storage_includes_all_dates=True,continuous_state_time_error=None,
          **full_domain(zz['finite_reference']-zz['policy_values'],m,pi)))
    return save('NESTED_CERTIFICATES',dict(records=records,optimal_upper_sha256=sha(cp),scope='complete continuous controls on 33 x 49 states and 40 dates; separate from continuous state/time transfer'),arrays)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('task',choices=['matched','nested']);a=p.parse_args()
    print(json.dumps(matched_cover() if a.task=='matched' else nested_accounts(),indent=2))
