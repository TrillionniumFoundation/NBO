"""Execute all 24 predeclared R45 services sequentially in fresh processes."""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    frozen=json.loads((ROOT/'audit/SOURCE_FREEZE.json').read_text())
    for name,h in frozen['sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    output=ROOT/'results/services'
    if output.exists(): raise SystemExit('Refusing to replace existing service evidence')
    output.mkdir(parents=True)
    methods=['min-plus-ReLU','piecewise-linear-spline']
    schedule=[]
    for rep in range(3):
        for T in (2,4):
            for p in (1,4):
                for method in (methods if rep%2==0 else methods[::-1]):
                    schedule.append({'method':method,'horizon':T,'price':p,'repeat':rep})
    (ROOT/'results/schedule.json').write_text(json.dumps(schedule,indent=2)+'\n')
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    allstart=time.perf_counter()
    for j,s in enumerate(schedule):
        dest=output/f'service-{j:03d}'
        command=[sys.executable,str(ROOT/'code/constructive.py'),'--method',s['method'],
                 '--horizon',str(s['horizon']),'--price',str(s['price']),
                 '--repeat',str(s['repeat']),'--out',str(dest)]
        started=time.perf_counter()
        p=subprocess.run(command,env=env,text=True,capture_output=True)
        (output/f'service-{j:03d}.log').write_text(p.stdout+p.stderr)
        (output/f'service-{j:03d}-process.json').write_text(json.dumps({
            'specification':s,'exit_code':p.returncode,'seconds_including_startup_and_exit':time.perf_counter()-started},indent=2)+'\n')
        print(j,s,'exit',p.returncode,p.stdout,flush=True)
        if p.returncode: raise SystemExit(p.returncode)
    (ROOT/'results/EXECUTION.json').write_text(json.dumps({'services':24,'rungs':144,
        'seconds_including_all_processes':time.perf_counter()-allstart,
        'source_commit':os.environ.get('GITHUB_SHA','local-source-hash-freeze'),
        'schedule':'repeat, horizon, price; method order reversed in middle repetition',
        'scope':'isolated sequential fresh processes; CPU frequency not controlled; no independent cost comparison'},indent=2)+'\n')
