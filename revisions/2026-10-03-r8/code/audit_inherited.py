"""Integrate pinned R7 raw evidence, including paired differences and failures."""
from pathlib import Path
import hashlib,json,math,sys,time
import numpy as np
from scipy.stats import t as student
ROOT=Path(__file__).resolve().parents[3];R7=ROOT/'revisions/2026-10-03-r7/results';OUT=Path(__file__).resolve().parents[1]/'results'
sys.path.insert(0,str(ROOT/'revisions/2026-09-29-r6/code'))
from ndu_neural import NDU
from dynamic_cournot import Game

def summary(x):
    x=np.asarray(x);n=len(x);mu=float(x.mean());se=float(x.std(ddof=1)/math.sqrt(n));radius=float(student.ppf(.975,n-1))*se
    return dict(mean=mu,standard_error=se,ci95=[mu-radius,mu+radius],paths=n,
        scope='pointwise Monte Carlo interval, not simultaneous, not discretization or optimality error')

def audit():
    OUT.mkdir(parents=True,exist_ok=True);paired=[];finite=[];missing=[];digests={}
    def load(path):
        meta=json.loads(path.read_text());raw=path.with_suffix('.npz');sha=hashlib.sha256(raw.read_bytes()).hexdigest()
        if 'raw_sha256' in meta:assert sha==meta['raw_sha256'],path.name
        digests[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
        digests[str(raw.relative_to(ROOT))]=sha
        return meta,np.load(raw)
    for d in [10,20]:
      for seed in [11,29,47]:
       for wide in [False,True]:
        suffix=f'd{d}_s{seed}_steps'+('1000_wide' if wide else '600')
        a,aa=load(R7/f'coverage_coupled_nbo_exact_{suffix}.json')
        b,bb=load(R7/f'coverage_coupled_direct_{suffix}.json')
        assert a['finest_brownian_seed']==b['finest_brownian_seed'] and a['boxes']==b['boxes']
        for n in [40,80,160]:
            paired.append(dict(dimension=d,seed=seed,wide=wide,steps=n,**summary(aa[f'payoff_{n}']-bb[f'payoff_{n}'])))
    for seed in [11,29,47]:
      for method in ['guarded_nbo','direct']:
        meta,z=load(R7/f'ndu_{method}_s{seed}.json');m=NDU();c=m.N//2
        active=~m.boundary;actions=m.actions[z['policy'][:,active]]
        metadata=dict(study='ndu',seed=seed,method=method,training=meta['training_seconds'],verification=meta['verification_seconds'],
            classical=meta['classical_seconds'],value_error=meta['value_error_max'],
            raw_loss=meta['certificates']['raw']['payoff_loss_upper'][0],
            shortlist_loss=meta['certificates']['shortlist']['payoff_loss_upper'][0],
            final_loss=meta['certificates']['final']['payoff_loss_upper'][0],
            corrected_fraction=meta['guard_fraction'],shortlist_fraction=meta['shortlist_fraction_changed'],
            finite_value_range=[float(z['reference'][0].min()),float(z['reference'][0].max())],
            center_value=float(z['reference'][0,c]),
            absolute_target_over_center_magnitude=.1/abs(float(z['reference'][0,c])),
            policy_table_bytes=z['policy'].nbytes,correction_index_bytes=int(np.sum(z['policy']!=z['shortlist_policy']))*16,
            action_lower_frequency=np.mean(np.isclose(actions,m.actions.min(axis=0)),axis=(0,1)).tolist(),
            action_upper_frequency=np.mean(np.isclose(actions,m.actions.max(axis=0)),axis=(0,1)).tolist(),
            all_action_state_queries=meta['counters']['all_action_backups']*m.N*m.A)
        finite.append(metadata)
      for market in [1,2]:
        meta,z=load(R7/f'game_M{market}_s{seed}.json');m=Game(market=market);r=np.arange(m.N)
        count=0
        for t in range(m.steps):
            q=[m.Q(z['values'][t+1,:,i],i) for i in [0,1]]
            gaps=[q[0].max(axis=1,keepdims=True)-q[0],q[1].max(axis=2,keepdims=True)-q[1]]
            joint=np.maximum(*gaps);minimum=joint.reshape(m.N,-1).min(axis=1)
            for index in np.flatnonzero(minimum>1e-11):
                a,b=z['policy'][t,index];count+=1
                missing.append(dict(market=market,seed=seed,t=int(t),state_index=int(index),capital=m.points[index].tolist(),
                    minimum_stage_defect=float(minimum[index]),selected_actions=[int(a),int(b)],
                    selected_defects=[float(gaps[i][index,a,b]) for i in [0,1]]))
        assert count==meta['missing_pure_stages']
        center=z['final_policy_lower'][0,m.N//2]
        finite.append(dict(study='game',market=market,seed=seed,method='guarded_nbo',
            training=meta['training_seconds'],verification=meta['verification_seconds'],
            raw_loss=meta['certificates']['raw']['payoff_loss_upper'],final_loss=meta['certificates']['final']['payoff_loss_upper'],
            corrected_fraction=meta['guard_fraction'],missing_pure=count,active_nodes=int((~m.boundary).sum()*m.steps),
            center_profit=center.tolist(),absolute_target_over_center_magnitude=(.1/np.abs(center)).tolist(),
            policy_table_bytes=z['policy'].nbytes,all_action_state_queries=meta['counters']['all_action_backups']*m.N*m.A**2))
    result=dict(pinned_source='5bab4649728860fb655c5371f3705787f10b4a78',pinned_evidence='b1409008625f550195ce9ead468391ad2449a240',
        paired_payoffs=paired,finite_comparisons=finite,missing_pure_nodes=missing,verified_input_sha256=digests)
    (OUT/'R7_INTEGRATION.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'paired_rows':len(paired),'finite_rows':len(finite),'missing_pure_nodes':len(missing),'input_files_hashed':len(digests)}))
    return result
if __name__=='__main__':audit()
