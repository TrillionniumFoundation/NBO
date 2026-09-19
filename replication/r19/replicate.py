"""Authoritative R19 generation entry point, including the exact-policy control.

Runs the base experiment and then evaluates the exact DP's returned policies on
the same worker, with the same state/action target and feasible first-date rules.
All comparator rows include their policy evaluation and upper-reference costs.
"""
from __future__ import annotations
import json,time
import numpy as np
import generate as base

_original_proposals=base.proposals

def complete_proposals(eng):
    _original_proposals(eng)
    path=base.OUT/'proposals.json';result=json.loads(path.read_text())
    old=np.load(base.OUT/'proposal_witness.npz',allow_pickle=False)
    archive={k:old[k] for k in old.files};old.close()
    for adj in (True,False):
      for lam in result['test_laws']:
        eng.cache.clear();t=time.perf_counter()
        v,p,f=eng.solve(lam,.42425,.85,adj,1);reference=time.perf_counter()-t
        t=time.perf_counter();lower=base.pb.value(eng,p,lam,adj);evaluation=time.perf_counter()-t
        tag=f'{int(adj)}.{lam}.exact.None'
        for s in base.SIGNS:archive[tag+'.policy.'+s]=p
        result['rows'].append(dict(id=tag,adjustment=adj,law=lam,method='exact',seed=None,
          proposal_seconds=0.,evaluation_seconds=evaluation,reference_seconds=reference,
          teacher_seconds=0.,training_seconds=0.,online_with_reference_seconds=reference+evaluation,
          parameter_bytes=p.nbytes,lower_witnesses=lower,
          reference_values={s:f[s][0] for s in base.SIGNS},
          gaps={s:max(0.,f[s][0]-lower[s]['value'])+2*base.EPS for s in base.SIGNS}))
        print('EXACT_CONTROL',tag,result['rows'][-1]['gaps'],flush=True)
    result['scope']+=' Exact-DP policies are additionally evaluated on this same worker; no fictitious teacher or fitting cost is assigned to that control.'
    np.savez_compressed(base.OUT/'proposal_witness.npz',**archive)
    base.put(path,result)

if __name__=='__main__':
    base.proposals=complete_proposals
    base.main()
