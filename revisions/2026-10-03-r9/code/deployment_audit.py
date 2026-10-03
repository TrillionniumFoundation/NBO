"""Post-protocol audit of six frozen fine-grid raw actors; no retraining.
All primary policy arrays and hybrid bounds are preserved. This audit follows
local deployment checks and is not described as preregistered evidence.
"""
from pathlib import Path
import hashlib,json,time
import numpy as np
from action_cover import ROOT,OUT,Model,up
from audit import payoff_envelope
R=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 upperpath=OUT/'fine_guarded_signed_cover.npz';upper=np.load(upperpath)['optimal_upper'];m=Model(33,49,40)
 hybrid=json.loads((OUT/'NESTED_CERTIFICATES.json').read_text())['records'];rows=[];arrays={};inputs={};begin=time.perf_counter()
 for guarded in [False,True]:
  folder=OUT/('grid_33_49_40_guarded' if guarded else 'grid_33_49_40')
  for seed in [11,29,47]:
   p=folder/f'continuous_actor_s{seed}_search.npz';inputs[str(p.relative_to(ROOT))]=digest(p)
   z=np.load(p);t=time.perf_counter();lower,higher=payoff_envelope(m,z['raw_policy']);gap=up(upper-lower)
   match=[x for x in hybrid if x['method']=='actor' and x['seed']==seed and x['guarded']==guarded];assert len(match)==1
   tag=f'actor_{seed}_guard{int(guarded)}';arrays[tag+'_lower']=lower;arrays[tag+'_upper']=higher
   rows.append(dict(seed=seed,guarded_continuation=guarded,raw_actor_regret_upper=float(gap.max()),hybrid_regret_upper=match[0]['regret_upper'],
    raw_target_pass=bool(gap.max()<=.1),independent_payoff_seconds=time.perf_counter()-t,source=str(p.relative_to(ROOT)),source_sha256=inputs[str(p.relative_to(ROOT))],continuous_state_time_error=None))
 for name,h in inputs.items():assert digest(ROOT/name)==h,name
 assert len(rows)==6 and {r['seed'] for r in rows}=={11,29,47}
 raw=OUT/'FINE_RAW_DEPLOYMENT.npz';np.savez_compressed(raw,**arrays)
 result=dict(records=rows,seconds=time.perf_counter()-begin,raw_sha256=digest(raw),upper_envelope_sha256=digest(upperpath),
  scope='complete continuous actions at all fine-grid nodes and dates; raw actor arrays, not searched hybrids',
  design='post-protocol frozen-output audit after local exploratory checks; no retraining or seed selection',source_arrays_unchanged=True,new_training_runs=0)
 (OUT/'FINE_RAW_DEPLOYMENT.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 lines=[r'\begin{table}[htbp]',r'\centering\small',r'\caption{Raw actor and hybrid deployment on the same fine grid}\label{tab:r9rawfine}',r'\begin{tabular}{lrrrr}',r'\toprule',r'Continuation & Seed & Raw bound & Hybrid bound & Raw $\leq0.1$ \\',r'\midrule']
 for x in rows:
  label='Guarded' if x['guarded_continuation'] else 'Unguarded'
  lines.append(f"{label} & {x['seed']} & {x['raw_actor_regret_upper']:.4f} & {x['hybrid_regret_upper']:.4f} & "+('Yes' if x['raw_target_pass'] else 'No')+r' \\')
 lines += [r'\bottomrule',r'\end{tabular}',r'\par\vspace{3pt}\begin{minipage}{0.97\linewidth}\footnotesize',
  'Same 33 by 49 state grid, forty dates, and complete-action upper envelope. Every saved raw actor is evaluated without local search. This post-protocol audit adds no training runs and changes no hybrid result. Bounds retain the arithmetic contract and exclude continuous-state/time transfer.',r'\end{minipage}',r'\end{table}']
 table=R/'manuscript/table_raw_deployment.tex';table.write_text('\n'.join(lines)+'\n')
 (R/'DEPLOYMENT_MANIFEST.json').write_text(json.dumps(dict(input_sha256=inputs,optimal_upper_sha256=digest(upperpath),output_sha256={str(p.relative_to(ROOT)):digest(p) for p in [raw,OUT/'FINE_RAW_DEPLOYMENT.json',table]}),indent=2)+'\n')
 print(json.dumps(result,indent=2),flush=True);return result
if __name__=='__main__':run()
