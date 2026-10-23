"""Execute saved-evidence verification; no economic experiment or retiming."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write('\n')


def main():
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out = ROOT/'ci124'/('evidence-'+stamp)
    out.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    identity = dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
        started_utc=dt.datetime.now(dt.timezone.utc).isoformat(), python=sys.version,
        platform=platform.platform(), github_run_id=os.environ.get('GITHUB_RUN_ID'),
        github_run_attempt=os.environ.get('GITHUB_RUN_ATTEMPT'),
        runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        new_economic_evaluations=0, new_states=0, new_training=0,
        new_service_timing_processes=0,
        scope='Exact verification of already executed saved evidence, with separate replay costs')
    save(out/'START124.json',identity)
    commands = [
        ('materialize-a',['verification124/transport124.py','materialize','transport124/experiment-a/TRANSPORT124.json']),
        ('abstract-joint',['verification124/verify_joint_witness124.py']),
        ('exact-a',['code124/verify124.py','--primary','results124/primary','--output',str(out/'exact-a'),
                    '--timing','results124/timing0','--timing','results124/timing1','--timing','results124/timing2']),
        ('publication-a',['verification124/publication_audit124.py','--output',str(out/'PUBLICATION_AUDIT124.json')]),
        ('post-a-saturation',['postfreeze124/verify_saturation124.py',
             '--primary','results124/primary/records124.jsonl','--audit','results124/audit/EXECUTION124.json',
             '--output',str(out/'saturation-a')]),
    ]
    receipts=[]
    try:
        for name,args in commands:
            tick=time.perf_counter()
            with (out/(name+'.stdout')).open('xb') as stdout, (out/(name+'.stderr')).open('xb') as stderr:
                process=subprocess.run([sys.executable,*args],cwd=ROOT,stdout=stdout,stderr=stderr)
            receipt=dict(stage=name,argv=[sys.executable,*args],exit_code=process.returncode,
                         seconds=time.perf_counter()-tick)
            receipts.append(receipt)
            save(out/(name+'.json'),receipt)
            print(json.dumps(receipt),flush=True)
            if process.returncode:
                raise RuntimeError('Saved-evidence stage failed: '+name)
        save(out/'EXECUTION124.json',dict(status='passed',identity=identity,stages=receipts,
             seconds=time.perf_counter()-start,ended_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
             independent_original_economics_reexecuted=False,
             manuscript_compiled=False,experiment_b_included=False))
    except BaseException:
        save(out/'FAILURE124.json',dict(status='failed',identity=identity,stages=receipts,
             seconds=time.perf_counter()-start,traceback=traceback.format_exc(),partial_outputs_retained=True))
        raise


if __name__ == '__main__':
    main()
