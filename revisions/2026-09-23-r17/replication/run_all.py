"""One-command R17 science reproduction; preserves all outputs and failures."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,os,json,time,hashlib,platform
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=HERE.parent/'results';OUT.mkdir(exist_ok=True)
ENV={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
def call(script,args=()):
    cmd=['python',str(HERE/script),*map(str,args)];name=script.replace('.py','')+('_'+str(args[1]) if script=='nonlinear_inventory.py' else '')
    st=time.perf_counter()
    with open(OUT/f'execution_{name}.log','w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env=ENV)
    row={'command':cmd,'returncode':r.returncode,'seconds':time.perf_counter()-st};print(json.dumps(row),flush=True)
    if r.returncode:raise RuntimeError(row)
    return row
if __name__=='__main__':
    start=time.perf_counter();rows=[call('test_revision.py')]
    # Each main task has its own bounded subprocess parallelism.
    with ThreadPoolExecutor(max_workers=4) as ex:
        fs=[ex.submit(call,'run_suite.py'),ex.submit(call,'run_remaining.py'),ex.submit(call,'wealth_and_riccati.py')]
        def inventory():return [call('nonlinear_inventory.py',['--d',d,'--out',OUT/'nonlinear_inventory'/f'd{d}']) for d in [8,32,128]]
        fi=ex.submit(inventory)
        rows.extend(f.result() for f in fs);rows.extend(fi.result())
    rows.append(call('run_refinement.py'));rows.append(call('diagnostics.py'));rows.append(call('test_revision.py'))
    files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in ['science_manifest.json','execution_ledger.json']}
    (OUT/'execution_ledger.json').write_text(json.dumps({'status':'completed','runs':rows,'elapsed_wall_seconds':time.perf_counter()-start,'platform':platform.platform(),'purpose':'Full source-to-results execution, not inherited R17 checkpoints'},indent=2)+'\n')
    (OUT/'science_manifest.json').write_text(json.dumps({'review_input':'82af00bc296da59e8a3a28ef1bf86c1d6fca2367','file_sha256':files,'no_new_accuracy_assigned_to_historical_objects':True},indent=2)+'\n')
