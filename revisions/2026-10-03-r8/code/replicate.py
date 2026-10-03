"""Execute the R8 source; retain failures and separate training from verification.

The corner cover can run on a separately pinned core while subsequent training
runs execute. Affinities and wall times are recorded. No result file is skipped.
"""
from __future__ import annotations
import hashlib,json,os,platform,subprocess,sys,time
from pathlib import Path
import numpy as np,scipy,torch
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1]
CODE=R/'code';OUT=R/'results';LOG=R/'logs';OUT.mkdir(exist_ok=True);LOG.mkdir(exist_ok=True)
affinity=sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else []
training_cpu=affinity[0] if affinity else None;verification_cpu=affinity[1] if len(affinity)>1 else training_cpu
context={'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__,'torch':torch.__version__,
 'source_commit':os.environ.get('NBO_SOURCE_COMMIT','local-uncommitted-source'),
 'github_run_id':os.environ.get('GITHUB_RUN_ID'), 'available_affinity':affinity,
 'training_cpu':training_cpu,'verification_cpu':verification_cpu,'threads':1,
 'timing_scope':'per-process wall time; verification runs on a separately pinned core when available; shared memory/system load is not eliminated'}
(OUT/'ENVIRONMENT.json').write_text(json.dumps(context,indent=2)+'\n')
(R/'logs/pip_freeze.txt').write_text(subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True))
records=[];running=[]
def launch(args,tag,cpu,wait=True):
 f=open(LOG/f'{tag}.log','w');start=time.perf_counter()
 env={**os.environ,'OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','PYTHONHASHSEED':'0'}
 command=[sys.executable,'-u',str(CODE/args[0]),*args[1:]]
 if cpu is not None:command=['taskset','-c',str(cpu),*command]
 p=subprocess.Popen(command,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
 item=(p,f,start,tag,args,cpu)
 if wait:finish(item)
 else:running.append(item)
 return item
def finish(item):
 p,f,start,tag,args,cpu=item;status=p.wait();f.close()
 records.append(dict(tag=tag,arguments=args,affinity_cpu=cpu,returncode=status,wall_seconds=time.perf_counter()-start))
 (OUT/'EXECUTION.json').write_text(json.dumps(records,indent=2)+'\n')
 if status:raise RuntimeError(f'{tag} exited {status}; see its retained log')
 print(json.dumps(records[-1]),flush=True)
# Fixed development failures are rerun, not removed from the study.
for args,tag in [(['continuous_actor.py','--smoke'],'actor_smoke'),
 (['continuous_actor.py'],'raw_actor'),
 (['continuous_actor.py','--heads','4','--fresh'],'four_head_reset'),
 (['continuous_actor.py','--method','direct'],'direct_gradient')]:launch(args,tag,training_cpu)
# Freeze seed 11 before starting either independent global action verifier.
launch(['continuous_actor.py','--seed','11','--search'],'actor_s11_search',training_cpu)
launch(['action_enclosure_tight.py','continuous_actor_s11_search.npz'],'corner_action_cover',verification_cpu,False)
for method in ['actor','direct']:
 for seed in [11,29,47]:
  if method=='actor' and seed==11:continue
  launch(['continuous_actor.py','--method',method,'--seed',str(seed),'--search'],f'{method}_s{seed}_search',training_cpu)
for seed in [11,29,47]:launch(['continuous_actor.py','--method','direct','--seed',str(seed),'--actor-steps','0','--search'],f'local_s{seed}',training_cpu)
for market in [1,2]:
 launch(['comparators.py','game','--method','classical','--market',str(market)],f'classical_game_M{market}',training_cpu)
 for seed in [11,29,47]:launch(['comparators.py','game','--method','direct','--market',str(market),'--seed',str(seed)],f'direct_game_M{market}_s{seed}',training_cpu)
for degree in [6,10,14]:launch(['comparators.py','ndu','--method','chebyshev','--degree',str(degree)],f'chebyshev_d{degree}',training_cpu)
for seed in [11,29,47]:launch(['comparators.py','ndu','--method','gated','--seed',str(seed)],f'gated_s{seed}',training_cpu)
for file,tag in [('audit_inherited.py','inherited_evidence_audit'),('refinement.py','frozen_policy_refinement')]:launch([file],tag,training_cpu)
launch(['action_enclosure.py','continuous_actor_s11_search.npz','--max-boxes','800000','--depth','24','--tolerance','.002'],'slope_action_cover',training_cpu)
for item in running:finish(item)
for file,tag in [('audit_policies.py','shared_action_envelopes'),('build_tables.py','generated_tables'),('assemble.py','integrated_manuscript'),('build_response.py','response'),('test_r8.py','new_tests'),('replay_inherited.py','inherited_tests')]:launch([file],tag,training_cpu)
(OUT/'EXECUTION_COMPLETE.json').write_text(json.dumps({'complete':True,'source_commit':context['source_commit'],'command_count':len(records)},indent=2)+'\n')
