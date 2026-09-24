"""Run the complete prespecified closure, then optimizer-free independent audit."""
from pathlib import Path
import subprocess,sys,time,json
ROOT=Path(__file__).resolve().parents[2];R=Path(__file__).resolve().parent
records=[]
for flag,name in [('--test','restart_tests.log'),('','restart_closure.log'),('--audit','restart_audit.log')]:
    start=time.perf_counter();cmd=[sys.executable,'-u',str(R/'replication/restart_closure.py'),str(R/'results')]+([flag] if flag else [])
    with (R/'results'/name).open('w') as stream:
        proc=subprocess.run(cmd,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
    records.append({'command':cmd,'exit_code':proc.returncode,'wall_seconds':time.perf_counter()-start,'log':name})
    (R/'results/restart_wall_clock.json').write_text(json.dumps(records,indent=2))
    print(name,proc.returncode,records[-1]['wall_seconds'],flush=True)
    if proc.returncode:sys.exit(proc.returncode)
