"""Local mirror of the immutable historical custody CI, with eight workers."""
from pathlib import Path
import concurrent.futures as cf
import datetime as dt
import gzip
import hashlib
import json
import os
import subprocess
import time

R = Path('/workspace/scratch/913249553838/NBO/revisions/2026-10-18-r119')
O = Path('/workspace/scratch/913249553838/audit/historical_remote119')
O.mkdir(exist_ok=True)
SOURCE = R / 'provenance/historical/HISTORICAL_stream_audit.py'
MANIFEST = O / 'HISTORICAL_stream_all_missing.jsonl'
MANIFEST.write_bytes(gzip.decompress((R / 'provenance/historical/HISTORICAL_stream_all_missing.jsonl.gz').read_bytes()))
ENV = dict(os.environ, PYTHONPATH='/workspace/scratch/913249553838/audit/theory_research/_parser_dep')
PYTHON = '/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python'
START = {'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
         'scope': 'Read-only immutable raw-commit historical custody; no economic execution.',
         'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
         'manifest_sha256': hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
         'shards': 16, 'max_workers': 8, 'related_ci_run': 39103777344}
(O / 'START119.json').write_text(json.dumps(START, indent=2) + '\n')

def run(i):
    argv = [PYTHON, str(SOURCE), 'run', '--manifest', str(MANIFEST),
            '--output', str(O / f'shard-{i:02d}'), '--repository',
            'TrillionniumFoundation/NBO', '--transport', 'raw_commit',
            '--shard-count', '16', '--shard-index', str(i),
            '--object-mib', '128', '--memory-mib', '512',
            '--cpu-seconds', '300', '--wall-seconds', '360',
            '--output-mib', '128']
    start = time.time()
    receipt = {'argv': argv, 'started_unix': start, 'source_sha256': START['source_sha256']}
    p = O / f'COMMAND-{i:02d}.json'
    p.write_text(json.dumps(receipt, indent=2) + '\n')
    log = O / f'shard-{i:02d}.log'
    with log.open('wb') as f:
        proc = subprocess.run(argv, env=ENV, cwd=R, stdout=f, stderr=subprocess.STDOUT)
    receipt.update(exit_code=proc.returncode, ended_unix=time.time(),
                   log_sha256=hashlib.sha256(log.read_bytes()).hexdigest())
    p.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'shard': i, 'exit_code': proc.returncode,
                      'elapsed_seconds': receipt['ended_unix'] - start}), flush=True)
    return receipt

with cf.ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(run, range(16)))
(O / 'COMMANDS119.json').write_text(json.dumps(results, indent=2) + '\n')
