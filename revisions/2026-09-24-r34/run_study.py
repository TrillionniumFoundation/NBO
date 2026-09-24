"""Execute and time the complete fixed cohort, then the independent audit."""
from pathlib import Path
import subprocess, sys, time, json, platform
R=Path(__file__).resolve().parent;root=R.parents[1]
rel=R.relative_to(root);out=rel/'results';out_abs=R/'results';out_abs.mkdir(parents=True,exist_ok=True)
commands=[([sys.executable,str(rel/'replication/global_cost.py'),'--test','--out',str(out)],'tests.log')]
commands += [([sys.executable,'-u',str(rel/'replication/global_cost.py'),'--source','revisions/2026-09-24-r32/results','--out',str(out),'--horizon',str(T)],f'H{T}.log') for T in (4,8,12)]
commands += [([sys.executable,str(rel/'replication/recheck.py'),str(out)],'recheck.log'),
             ([sys.executable,str(rel/'replication/report_global.py'),str(rel)],'report.log')]
records=[];started=time.perf_counter()
for cmd,log in commands:
    tic=time.perf_counter()
    with (out_abs/log).open('w') as f:proc=subprocess.run(cmd,cwd=root,stdout=f,stderr=subprocess.STDOUT)
    records.append({'command':cmd,'log':log,'returncode':proc.returncode,'wall_seconds':time.perf_counter()-tic})
    (out_abs/'wall_clock.json').write_text(json.dumps({'records':records,'elapsed_wall_seconds':time.perf_counter()-started,'python':sys.version,'platform':platform.platform()},indent=2))
    print(log,proc.returncode,round(records[-1]['wall_seconds'],3),flush=True)
    if proc.returncode:raise SystemExit(proc.returncode)
summary=json.loads((out_abs/'summary.json').read_text())
assert summary['cases']==summary['passed']==summary['preservation_passed']==42
assert summary['support_solves']==168 and summary['independent_certificates']==252
assert not summary['failures']
