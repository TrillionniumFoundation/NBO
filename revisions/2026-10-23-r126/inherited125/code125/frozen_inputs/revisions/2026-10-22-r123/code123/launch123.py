"""Measure a whole child process and preserve logs even before scientific import."""
import argparse,datetime as dt,hashlib,json,os,platform,resource,subprocess,sys,time,traceback
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--receipt',required=True);ap.add_argument('command',nargs=argparse.REMAINDER);a=ap.parse_args()
    command=a.command[1:] if a.command[:1]==['--'] else a.command
    out=Path(a.receipt);out.mkdir(parents=True,exist_ok=False)
    start=time.perf_counter();initial=dict(command=command,started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),python=sys.version,platform=platform.platform())
    (out/'START123.json').write_text(json.dumps(initial,indent=2)+'\n')
    error=None;returncode=127
    with (out/'stdout.log').open('xb') as f:
        try:
            result=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT);returncode=result.returncode
        except BaseException:
            error=traceback.format_exc();f.write(error.encode());f.flush()
    rec=dict(initial,ended_utc=dt.datetime.now(dt.timezone.utc).isoformat(),seconds=time.perf_counter()-start,exit_code=returncode,launch_error=error,
             status='executed' if returncode==0 else 'failed',peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
             stdout_sha256=hashlib.sha256((out/'stdout.log').read_bytes()).hexdigest(),all_failed_work_retained=True)
    (out/'LAUNCH123.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec),flush=True)
    raise SystemExit(returncode)

if __name__=='__main__':main()
