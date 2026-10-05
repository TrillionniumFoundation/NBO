"""Audit immutable R20 services without fitting or generating observations."""
from __future__ import annotations
import hashlib,json,sys,time
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-05-r20'
sys.path.insert(0,str(OLD/'code'))
import future_study as f
import intervals
import torch

def records():
    manifest=json.loads((OLD/'results/EVIDENCE_STORAGE.json').read_text());rows=[]
    for d in (10,50):
        for q in f.VOLUMES:
            for seed in f.STREAMS:
                for method in f.SERVICES:
                    name=f'future-study/d{d}_q{q}_s{seed}_{method}.json'
                    raw=(OLD/'results'/name).read_bytes();expected=manifest['original_files'][name]
                    assert len(raw)==expected['bytes'] and hashlib.sha256(raw).hexdigest()==expected['sha256'],name
                    x=json.loads(raw)
                    assert (x['dimension'],x['queries_per_regime'],x['stream'],x['service'])==(d,q,seed,method)
                    rows.append(x)
    return rows

def main():
    begin=time.perf_counter();source=f.check_source();rows=records()
    env=json.loads((OLD/'results/future-study/DESIGN_AND_ENVIRONMENT.json').read_text())
    assert source==env['source_sha256'];old_exp=intervals._exp_positive_point
    monitor={'calls':0,'arguments':0,'largest_argument':0.0}
    def checked(x):
        x=np.asarray(x,dtype=np.float64);k=0
        while np.max(x,initial=0)/2**k>.5:k+=1
        if not np.array_equal(np.ldexp(np.ldexp(x,-k),k),x):raise ArithmeticError('nonexact scaling')
        monitor['calls']+=1;monitor['arguments']+=x.size
        monitor['largest_argument']=max(monitor['largest_argument'],float(np.max(x,initial=0)))
        return old_exp(x)
    intervals._exp_positive_point=checked;attempts=points=outcomes=economic=0
    try:
        for row in rows:
            d,q=row['dimension'],row['queries_per_regime']
            data=json.loads((f.BASE/f'protocols/economy_d{d}.json').read_text());y,t=f.tasks(q,d,200700+d)
            assert row['task_sha256']==f.checksum(np.c_[y.numpy(),t.numpy()])
            assert [g['regime'] for g in row['regimes']]==[r[0] for r in f.REGIMES]
            for regime,g in zip(f.REGIMES,row['regimes']):
                e=f.FutureEconomy(data,regime);assert row['finite_inputs'][e.regime]==e.inputs
                for i,item in enumerate(g['attempts']):
                    a=torch.tensor(item['actions'],dtype=torch.float64);c=e.certify(y,a,t)
                    assert c==item['certificate'],(d,q,row['stream'],row['service'],e.regime,i)
                    assert all(item[k]>=0 for k in ['fit_seconds','query_seconds','verification_seconds'])
                    if i<len(g['attempts'])-1:assert c['mean_regret_upper']>f.TOLERANCE
                    attempts+=1;points+=q
                assert g['certified']==(c['mean_regret_upper']<=f.TOLERANCE)
                assert g['service_seconds']+1e-8>=sum(sum(s[k] for k in ['fit_seconds','query_seconds','verification_seconds']) for s in g['attempts'])
                if 'economic_certificate' in g:
                    h=g['economic_certificate'];az=torch.tensor(h['zero_charge_actions'],dtype=torch.float64)
                    zero=t.clone();zero[:,2]=0;cz=e.certify(y,az,zero);assert cz==h['zero_charge_certificate']
                    band=f.optimal_action_interval(a,t,c);bz=f.optimal_action_interval(az,zero,cz)
                    bm=band.mean();difference=(bz-band).mean()
                    assert h['mean_optimal_action']==[float(bm.lo),float(bm.hi)]
                    assert h['mean_withdrawal_reduction_due_to_charge']==[float(difference.lo),float(difference.hi)]
                    economic+=1
                outcomes+=1
            assert row['all_regimes_certified']==all(g['certified'] for g in row['regimes'])
            parts=row['initialization_seconds']+row['anchor_fit_seconds']+sum(g['service_seconds'] for g in row['regimes'])+row['final_record_write_seconds']
            assert abs(parts-row['accounted_service_seconds'])<1e-8
            print('verified',d,q,row['stream'],row['service'],flush=True)
    finally:intervals._exp_positive_point=old_exp
    assert (len(rows),outcomes,attempts,points,economic)==(168,840,984,319062,120)
    result={'services':len(rows),'regime_outcomes':outcomes,'attempt_certificates':attempts,'task_certificates':points,'economic_counterfactual_certificates':economic,'all_recorded_certificate_fields_replayed_exactly':True,'evidence_file_hashes_verified':len(rows),'frozen_source_sha256':source,'exact_binary_scaling':monitor,'audit_seconds':time.perf_counter()-begin,'scope':'Deterministic post-execution audit; no new fitting streams, scientific observations, or replacement clocks.'}
    (R/'results/FUTURE_AUDIT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
