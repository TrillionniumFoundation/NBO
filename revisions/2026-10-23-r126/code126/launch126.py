"""Whole parent-process cost and complete stdout, including unsuccessful attempts."""
import argparse,subprocess
from common126 import *

parser=argparse.ArgumentParser(); parser.add_argument('--receipt',required=True)
parser.add_argument('command',nargs=argparse.REMAINDER); args=parser.parse_args()
command=args.command[1:] if args.command and args.command[0]=='--' else args.command
out,tick,info=start(args.receipt,'external-whole-process')
try:
    environment=os.environ.copy()
    for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'): environment[name]='1'
    with (out/'stdout.log').open('xb') as stream:
        result=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,env=environment)
    write(out/'PROCESS126.json',dict(command=command,returncode=result.returncode,
        seconds=time.perf_counter()-tick,peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss))
    if result.returncode: raise SystemExit(result.returncode)
    finish(out,tick,command=command)
except BaseException: fail(out,tick); raise
