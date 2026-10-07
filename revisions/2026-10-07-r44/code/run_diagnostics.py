import subprocess,sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
root=Path(sys.argv[1]); script=root/'code/study.py'
def run(i):
 p=subprocess.run([sys.executable,str(script),'recertify','--id',str(i)],capture_output=True,text=True)
 print(p.stdout,p.stderr,flush=True);return (i,p.returncode)
with ThreadPoolExecutor(max_workers=3) as pool: results=list(pool.map(run,[41,89,120,124,128,145,147]))
(root/'audit/diagnostic_processes.json').write_text(__import__('json').dumps(results))
