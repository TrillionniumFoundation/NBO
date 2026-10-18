"""Execution recorder only; commands and scientific source are independently bound."""
from pathlib import Path
import argparse,subprocess,time,json,hashlib,os,sys
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--stage',required=True);p.add_argument('--source',required=True);p.add_argument('command',nargs=argparse.REMAINDER)
a=p.parse_args(); command=a.command[1:] if a.command and a.command[0]=='--' else a.command
logs=a.root/'results119/logs';logs.mkdir(parents=True,exist_ok=True)
log=logs/(a.stage+'.log');receipt=logs/(a.stage+'.json')
if log.exists() or receipt.exists():raise FileExistsError('Preserve every actual attempted command')
env=os.environ.copy();env.update(NBO_SOURCE119=a.source,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
record=dict(stage=a.stage,command=command,cwd=str(a.root),source_commit=a.source,started_unix=time.time(),recorder_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
receipt.write_text(json.dumps(record,indent=2)+'\n')
started=time.perf_counter()
with log.open('x') as stream:
    process=subprocess.run(command,cwd=a.root,env=env,stdout=stream,stderr=subprocess.STDOUT)
record.update(ended_unix=time.time(),elapsed_seconds=time.perf_counter()-started,exit_code=process.returncode,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest())
receipt.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record),flush=True)
sys.exit(process.returncode)
