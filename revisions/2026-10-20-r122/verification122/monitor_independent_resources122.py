"""Administrative read-only observation of an active independent calculation.

This script never imports a solver, changes a state/action, or stops a run.
It appends actual resource/progress observations to the result directory.
"""
from pathlib import Path
import argparse, datetime, json, shutil, time

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--log',required=True,type=Path)
    a=p.parse_args();tick=time.perf_counter();out=a.output.resolve()
    parts=sorted((out/'terminal_witnesses122').glob('*.gz'))
    sealed=out/'SEALED_WITNESS_PARTS122.jsonl'
    policies=out/'POLICY_EVALUATIONS122.jsonl'
    claims=out/'CLAIM_CHECKS122.jsonl'
    lines=a.log.read_text().splitlines() if a.log.exists() else []
    counts=lambda path:sum(1 for _ in path.open()) if path.exists() else 0
    obj={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'witness_parts':len(parts),'witness_total_bytes':sum(p.stat().st_size for p in parts),
         'sealed_parts':counts(sealed),'completed_policy_evaluations':counts(policies),
         'completed_claim_checks':counts(claims),'free_tmpfs_bytes':shutil.disk_usage(out).free,
         'available_memory_kib':next(int(line.split()[1]) for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:')),
         'latest_log_line':lines[-1] if lines else None,
         'failure_receipt_exists':(out/'FAILURE122.json').exists(),
         'execution_receipt_exists':(out/'EXECUTION122.json').exists(),
         'observer_seconds':time.perf_counter()-tick,'original_economic_calls':0}
    with (out/'RESOURCE_MONITOR122.jsonl').open('a') as f:
        f.write(json.dumps(obj,sort_keys=True)+'\n')
    print(json.dumps(obj,sort_keys=True),flush=True)

if __name__=='__main__':main()
