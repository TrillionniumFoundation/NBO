"""External scientific-process clock and durable failure receipt.

Run as: python code122/launch122.py --receipt results122/launch-name01 -- python ... --output results122/name01
The receipt measures the actual scientific child from process spawn through
exit, including its interpreter, imports, source checks and failures.
"""
from __future__ import annotations
import argparse,datetime as dt,json,os,platform,resource,subprocess,sys,time,traceback
from pathlib import Path

def write(p,obj):
 with Path(p).open('x') as f:json.dump(obj,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')

def main():
 p=argparse.ArgumentParser();p.add_argument('--receipt',required=True,type=Path);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
 command=a.command[1:] if a.command and a.command[0]=='--' else a.command
 if not command:raise ValueError('Explicit scientific command required')
 receipt=a.receipt.resolve();receipt.mkdir(parents=True,exist_ok=False)
 env=os.environ.copy()
 for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):env[k]='1'
 child_output=None
 if '--output' in command:child_output=str(Path(command[command.index('--output')+1]).resolve())
 initial=dict(command=command,cwd=str(Path.cwd()),child_output=child_output,receipt_directory=str(receipt),started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),started_unix=time.time(),python=sys.version,platform=platform.platform(),threads={k:env[k] for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')},clock_scope='actual child spawn through exit; includes child interpreter/imports/source gate; wrapper startup and receipt writes separate')
 write(receipt/'START_LAUNCH122.json',initial);tick=time.perf_counter()
 try:
  with (receipt/'stdout.log').open('x') as stream:process=subprocess.run(command,env=env,stdout=stream,stderr=subprocess.STDOUT)
  code=process.returncode;error=None
 except BaseException:
  code=-1;error=traceback.format_exc()
 result=dict(initial,ended_unix=time.time(),outer_seconds=time.perf_counter()-tick,exit_code=code,error=error,max_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,status='executed' if code==0 else 'failed',all_partial_outputs_retained=True)
 write(receipt/'LAUNCH122.json',result)
 if child_output and Path(child_output).is_dir():write(Path(child_output)/'OUTER_EXECUTION122.json',result)
 print(json.dumps({k:result[k] for k in ('status','exit_code','outer_seconds','child_output','receipt_directory')},indent=2),flush=True)
 if code:raise SystemExit(code if code>0 else 1)

if __name__=='__main__':main()
