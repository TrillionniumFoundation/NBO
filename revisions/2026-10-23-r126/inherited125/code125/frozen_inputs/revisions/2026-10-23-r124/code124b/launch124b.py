"""Complete parent clock and stdout/stderr custody for a B child process."""
import argparse,os,subprocess,time,resource
from common124b import start,finish,fail,write
p=argparse.ArgumentParser();p.add_argument('--receipt',required=True);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
command=a.command[1:] if a.command and a.command[0]=='--' else a.command
out,tick,info=start(a.receipt,'B-external-process')
try:
 env=os.environ.copy()
 for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):env[k]='1'
 with (out/'stdout.log').open('xb') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=env)
 write(out/'PROCESS124B.json',dict(command=command,returncode=r.returncode,seconds=time.perf_counter()-tick,
  peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,all_stdout_stderr_preserved=True))
 if r.returncode:raise SystemExit(r.returncode)
 finish(out,tick,info,command=command)
except BaseException:fail(out,tick);raise
