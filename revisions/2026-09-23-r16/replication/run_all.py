"""One-command model-to-evidence reproduction; separate processes/arithmetic.
Run from repository root. Existing outputs are refused rather than overwritten.
"""
from pathlib import Path
import sys,os,json,time,subprocess,platform,hashlib,traceback
HERE=Path(__file__).resolve().parent;P=HERE.parent;ROOT=HERE.parents[2]

def main():
    start=time.perf_counter();out=P/'results';out.mkdir(parents=True,exist_ok=True);logs=P/'build_logs';logs.mkdir(exist_ok=True)
    import torch,numpy,scipy,sympy
    try:sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    except Exception:sha=None
    environment={'source_commit':sha,'python':sys.version,'platform':platform.platform(),'processor':platform.processor(),
      'logical_cpu_count':os.cpu_count(),'torch':torch.__version__,'numpy':numpy.__version__,'scipy':scipy.__version__,'sympy':sympy.__version__,
      'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*') if p.suffix in ['.py','.c']},
      'execution':'four experiment processes run concurrently; neural has two seed processes and MPFR four node processes; timings include contention, not a solver-superiority benchmark'}
    (out/'execution_environment.json').write_text(json.dumps(environment,indent=2)+'\n')
    jobs=[];handles=[]
    for program,folder,extra in [('run_neural_suite.py','neural',['--workers','2']),('mpfr_library.py','mpfr_library',['--workers','4']),
        ('structured_inventory.py','inventory',[]),('fresh_price_library.py','fresh_library',[])]:
        log=(logs/(folder+'.log')).open('w');handles.append(log)
        cmd=[sys.executable,str(HERE/program),'--out',str(out/folder)]+extra
        jobs.append((folder,subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)))
    status=[]
    for folder,job in jobs:status.append({'experiment':folder,'returncode':job.wait()})
    for f in handles:f.close()
    (out/'pipeline_attempts.json').write_text(json.dumps(status,indent=2)+'\n')
    if any(r['returncode'] for r in status):raise RuntimeError('A complete experiment failed; see preserved logs; no final certificate publication')
    with (logs/'baselines.log').open('w') as f:
        subprocess.run([sys.executable,str(HERE/'classical_baselines.py'),'--out',str(out/'baselines'),'--network',str(out/'neural/seed16100/network_step2400.json')],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
    subprocess.run([sys.executable,str(HERE/'foundation_checks.py')],cwd=ROOT,check=True)
    (out/'pipeline_resources.json').write_text(json.dumps({'status':'completed','wall_seconds':time.perf_counter()-start,
      'scope':'full new candidate generation, inherited-library arithmetic cross-check, all complete certificates, classical candidates, exact envelopes and welfare normalization; packages/import setup excluded'},indent=2)+'\n')
if __name__=='__main__':main()
