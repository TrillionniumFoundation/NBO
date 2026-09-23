"""Build publication tables only from frozen evidence, never from prose."""
from pathlib import Path
import hashlib,json,platform,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'revisions/2026-09-23-r26';OLD=ROOT/'revisions/2026-09-23-r25/results'
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def tex(p,s):p.write_text(s+'\n')
NAMES={'neural':'Neural','direct':'Direct','diagonal':'Diagonal','tangent':'Static tangent','white':'Whitening','moving':'Moving transport'}
selection=read(OLD/'tuning_selection.json');data=read(OLD/'heldout_ledger.json');online=read(R/'results/online_summary.json');jets=read(R/'results/jet_summary.json')
summary=[];pairs=[]
for order in ((8,16),(12,24)):
 rows=[]
 for arm,opt in [(a,'historical_transport_adam' if a=='moving' else 'adam') for a in NAMES]+[('neural','lbfgsb'),('direct','lbfgsb')]:
  rs=[r for r in data if r['orders']==list(order) and r['arm']==arm and r['optimizer']==opt]
  assert len(rs)==2
  s={'orders':list(order),'arm':arm,'optimizer':opt,'regret_upper':max(r['final_deployed_certificate']['regret_upper'] for r in rs)}
  for k in ('gradient_calls','generation_seconds','checker_seconds'):s[k]=sum(r[k] for r in rs)/len(rs)
  summary.append(s)
  name=NAMES[arm]+(' L-BFGS-B' if opt=='lbfgsb' else ' Adam')
  rows.append(f"{name} & {s['regret_upper']:.7f} & {s['gradient_calls']:.1f} & {s['generation_seconds']:.3f} & {s['checker_seconds']:.3f} " +r'\\')
 tex(R/f"paper/heldout_{order[0]}_{order[1]}.tex",'\n'.join(rows))
 for seed in (25101,25102):
  r=[r for r in data if r['orders']==list(order) and r['seed']==seed]
  neural=next(x for x in r if x['arm']=='neural' and x['optimizer']=='adam')['final_deployed_certificate']['value_interval']
  direct=next(x for x in r if x['arm']=='direct' and x['optimizer']=='lbfgsb')['final_deployed_certificate']['value_interval']
  pairs.append({'seed':seed,'orders':order,'neural_minus_direct_lbfgsb':[float(np.nextafter(neural[0]-direct[1],-np.inf)),float(np.nextafter(neural[1]-direct[0],np.inf))]})
rows=[]
for r in online:
 rows.append(f"{r['seed']} & {NAMES[r['arm']]} & {r['accepted_count']}/{r['rejected_count']} & {r['final_deployed_certificate']['regret_upper']:.7f} & {r['generation_seconds']:.3f} & {r['checkpoint_check_seconds']+r['initial_checker_seconds']:.3f} & {r['actual_coupled_seconds']:.3f} "+r'\\')
tex(R/'paper/online_table.tex','\n'.join(rows))
rows=[]
for r in online:
 for b in r['blocks']:
  c=b['certificate'];interval=c.get('value_interval',[None,None])
  cand=f"{c['regret_upper']:.6f}" if 'regret_upper' in c else '--'
  rows.append(f"{r['seed']} & {NAMES[r['arm']]} & {b['block']} & {b['rate']:.3g} & {cand} & "+('Accept' if b['accepted'] else 'Restore')+r'\\')
tex(R/'paper/checkpoint_table.tex','\n'.join(rows))
rows=[]
for arm,s in selection.items():
 for trial in s['trials']:
  rows.append(f"{NAMES[arm]} & {trial['learning_rate']:.3g} & {trial['mean_certified_lower']:.8f} & "+('Yes' if trial['all_feasible'] else 'No')+(' & Selected' if trial['learning_rate']==s['selected_rate'] else ' & --')+r'\\')
tex(R/'paper/tuning_table.tex','\n'.join(rows))
rows=[]
for r in jets['neural']:
 for a in r['attempts']:
  rows.append(f"{r['seed']} & {a['cells']:,} & {a['first_order_regret_upper_same_cells']:.8f} & {a['regret_upper']:.8f} & {a['seconds']:.3f} "+r'\\')
tex(R/'paper/jet_table.tex','\n'.join(rows))
rows=[]
for r in jets['neural']:
 rows.append(str(r['seed'])+' & '+' & '.join(f"{v['upper']:.9f}" for v in r['restart_upper'])+r'\\')
tex(R/'paper/restart_table.tex','\n'.join(rows))
report={'remote_review_commit':'0eb0400ae311333fb77826ef9e2f067718926ae8','remote_reviewed_manuscript':'14ce582e188f437cc8d99f310edd4f06515936a4','remote_r25_evidence_commit':'c78d934c0b3b8d346a40c7ddcaf415e167462265',
        'remote_write_completed':False,'original_full_state':read(OLD/'full_state/summary.json'),'heldout':summary,'pairwise':pairs,
        'online':[{k:r[k] for k in ('seed','arm','accepted_count','rejected_count','actual_coupled_seconds','gradient_calls','generation_seconds','checkpoint_check_seconds','initial_checker_seconds','shadow_seconds_excluded','final_deployed_certificate')} for r in online],
        'jet_certificates':jets,'tuning_selection':selection,'original_stopped_gradient_certificate':False,
        'method_scope':'Original economy retained; manufactured reference is separately identified; no neural frontier claim.'}
write(R/'results/PUBLICATION_SUMMARY.json',report)
write(R/'results/local_environment.json',{'python':sys.version,'numpy':np.__version__,'platform':platform.platform(),'execution':'local serial CPU','r25_timings':'imported from separate recorded CI environment; not compared as a hardware speedup'})
print('Frozen publication tables generated. Matched payoff intervals:',pairs)
