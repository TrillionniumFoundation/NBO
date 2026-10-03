"""Run the complete pinned R10 study and retain every command and failure."""
import hashlib,json,os,platform,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1];C=R/'code';O=R/'results';L=R/'logs'
def run():
 O.mkdir(exist_ok=True);L.mkdir(exist_ok=True);records=[];start=time.perf_counter()
 def execute(name,args):
  ts=time.perf_counter();log=L/f'{len(records):02d}_{name}.log'
  with log.open('w') as f:p=subprocess.run(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
  row=dict(name=name,command=args,returncode=p.returncode,seconds=time.perf_counter()-ts,log=str(log.relative_to(ROOT)),log_sha256=hashlib.sha256(log.read_bytes()).hexdigest())
  records.append(row);(O/'EXECUTION.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(row),flush=True)
  if p.returncode:raise RuntimeError(f'{name} failed; inspect {log}')
 def py(name,file,*args):execute(name,[sys.executable,str(C/file),*map(str,args)])
 env=dict(python=sys.version,platform=platform.platform(),processor=platform.processor(),source_commit=os.environ.get('NBO_SOURCE_COMMIT'),workflow_run=os.environ.get('GITHUB_RUN_ID'),
   threads={k:os.environ.get(k) for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']},packages=subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True).splitlines())
 (O/'ENVIRONMENT.json').write_text(json.dumps(env,indent=2)+'\n')
 py('preserve_base','report.py','prepare')
 py('new_regression','test_r10.py')
 py('continuous_certificates','tube_certificate.py')
 for d in [10,20,50]:
  for method in ['actor','direct_tube','direct_full']:
   for seed in [11,29,47]:py(f'{method}_d{d}_s{seed}','tube_neural.py','--dimension',d,'--seed',seed,'--method',method,'--steps',600)
  py(f'paired_d{d}','paired.py','--dimension',d,'--paths',512)
 py('independent_output_replay','report.py','audit')
 py('tables','report.py','tables')
 py('integration','report.py','integrate')
 py('historical_regression','replay_inherited.py')
 (O/'EXECUTION_COMPLETE.json').write_text(json.dumps(dict(complete=True,commands=len(records),all_returncodes_zero=all(r['returncode']==0 for r in records),seconds=time.perf_counter()-start,source_commit=env['source_commit'],scope='complete execution; economic comparisons and failures remain separate facts'),indent=2)+'\n')
if __name__=='__main__':run()
