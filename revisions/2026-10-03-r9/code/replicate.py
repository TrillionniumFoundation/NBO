"""Execute the declared R9 program; record every command and failure verbatim."""
from __future__ import annotations
import hashlib,json,os,platform,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1];C=R/'code';O=R/'results';L=R/'logs'
def run():
 O.mkdir(exist_ok=True);L.mkdir(exist_ok=True);records=[];start=time.perf_counter()
 def execute(name,args):
  t=time.perf_counter();log=L/f'{len(records):02d}_{name}.log'
  with log.open('w') as f:p=subprocess.run(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
  record=dict(name=name,command=args,returncode=p.returncode,seconds=time.perf_counter()-t,log=str(log.relative_to(ROOT)),log_sha256=hashlib.sha256(log.read_bytes()).hexdigest());records.append(record)
  (O/'EXECUTION.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(record),flush=True)
  if p.returncode:raise RuntimeError(f'{name}: return code {p.returncode}; see {log}')
 def py(name,file,*args):execute(name,[sys.executable,str(C/file),*map(str,args)])
 py('prepare','assemble.py','--prepare')
 env=dict(python=sys.version,platform=platform.platform(),processor=platform.processor(),source_commit=os.environ.get('NBO_SOURCE_COMMIT'),bootstrap_commit=os.environ.get('NBO_BOOTSTRAP_COMMIT'),workflow_run=os.environ.get('GITHUB_RUN_ID'),threads={k:os.environ.get(k) for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']})
 env['packages']=subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True).splitlines();(O/'ENVIRONMENT.json').write_text(json.dumps(env,indent=2)+'\n')
 py('coarse_complete_action','action_cover.py','revisions/2026-10-03-r8/results/continuous_actor_s29_search.npz','--max-boxes',2000000)
 py('common_accounts','audit.py')
 for nu,nx,nt,guard in [(17,25,20,True),(33,49,40,False),(33,49,40,True)]:
  for seed in [11,29,47]:
   for method in ['actor','search']:
    args=['--nu',nu,'--nx',nx,'--steps',nt,'--seed',seed,'--method',method]+(['--guard'] if guard else [])
    py(f'train_{nu}_{nx}_{nt}_{method}_{seed}_guard{int(guard)}','retrain.py',*args)
 py('fine_complete_action','action_cover.py','revisions/2026-10-03-r9/results/grid_33_49_40_guarded/continuous_actor_s11_search.npz','--max-boxes',1500000,'--tag','fine_guarded_signed_cover')
 execute('nested_diagnostics',[sys.executable,'-c',f"import sys;sys.path.insert(0,{str(C)!r});from audit import nested_diagnostics;nested_diagnostics()"])
 py('fine_shared_accounts','validation.py','nested')
 py('matched_cover','validation.py','matched')
 py('continuous_capital_benchmark','global_benchmark.py')
 py('generate_tables','tables.py')
 py('integrate_manuscripts','assemble.py')
 py('inherited_regression','replay_inherited.py')
 py('r9_regression','test_r9.py')
 (O/'EXECUTION_COMPLETE.json').write_text(json.dumps(dict(complete=True,commands=len(records),all_returncodes_zero=all(r['returncode']==0 for r in records),seconds=time.perf_counter()-start,source_commit=env['source_commit'],scope='execution and accounting success, not universal economic-target success'),indent=2)+'\n')
if __name__=='__main__':run()
