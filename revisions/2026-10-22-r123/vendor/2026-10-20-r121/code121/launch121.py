"""Record actual immutable R121 subprocess launches, including failed prefixes."""
from __future__ import annotations
import argparse,datetime,hashlib,json,os,platform,resource,subprocess,sys,time
from pathlib import Path


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write(path, obj):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(obj,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
        f.flush();os.fsync(f.fileno())


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('command',nargs=argparse.REMAINDER)
    a=p.parse_args();cmd=a.command
    if cmd and cmd[0]=='--':cmd=cmd[1:]
    if not cmd:raise ValueError('An actual command is required')
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    started=utc();clock=time.perf_counter()
    repo=Path(__file__).resolve().parents[3]
    head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
    env=dict(os.environ)
    for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:
        env[k]='1'
    env['PYTHONHASHSEED']='0';env['PYTHONDONTWRITEBYTECODE']='1'
    record={'command':cmd,'working_directory':os.getcwd(),'started_utc':started,
            'head_at_launch':head,'python':sys.version,'platform':platform.platform(),
            'thread_environment':{k:env[k] for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','PYTHONHASHSEED']},
            'parent_pid':os.getpid(),'status':'started'}
    write(out/'START_LAUNCH121.json',record)
    with (out/'stdout.log').open('xb') as f:
        try:
            run=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env=env)
            code=run.returncode
        except BaseException as exc:
            f.write((repr(exc)+'\n').encode());code=125
        f.flush();os.fsync(f.fileno())
    record.update(status='executed' if code==0 else 'failed',exit_code=code,
                  ended_utc=utc(),elapsed_seconds=time.perf_counter()-clock,
                  stdout_bytes=(out/'stdout.log').stat().st_size,
                  stdout_sha256=hashlib.sha256((out/'stdout.log').read_bytes()).hexdigest(),
                  child_peak_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                  all_partial_outputs_retained=True)
    write(out/'LAUNCH121.json',record)
    print(json.dumps(record,sort_keys=True),flush=True)
    raise SystemExit(code)


if __name__=='__main__':main()
