from pathlib import Path
import subprocess,sys,json
from concurrent.futures import ThreadPoolExecutor
r=Path(sys.argv[1]); script=r/'code/study.py'
def run(v):
 p,s=v;p0=subprocess.run([sys.executable,str(script),'paired','--pair',str(p),'--state',str(s)],capture_output=True,text=True)
 print(p0.stdout,p0.stderr,flush=True);return [p,s,p0.returncode]
with ThreadPoolExecutor(max_workers=2) as pool: result=list(pool.map(run,[(p,s) for p in range(6) for s in range(4)]))
(r/'audit/paired_processes.json').write_text(json.dumps(result))
