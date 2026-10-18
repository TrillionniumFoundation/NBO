#!/usr/bin/env python3
"""Four offline, nonduplicating custody shards; no scientific executions."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
from collections import Counter

p = Path(__file__).resolve().parent
c = sqlite3.connect('file:' + str(p / 'HISTORICAL_index.sqlite') + '?mode=ro', uri=True)
read = {r[0] for r in c.execute('select sha from source_blobs')}
rows = [json.loads(x) for x in open(p / 'HISTORICAL_stream_all_blobs.jsonl')]
remaining = [r for r in rows if r['available'] and r['sha'] not in read]
manifest = p / 'HISTORICAL_stream_available_raw_unread.jsonl'
manifest.write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in remaining))
scope = {'objects': len(remaining), 'formats': dict(Counter(r['parse_suffix'] for r in remaining)),
         'known_bytes': sum(r['bytes'] or 0 for r in remaining),
         'historical_blobs': len(rows), 'historical_available': sum(r['available'] for r in rows),
         'historical_available_already_read_in_source_index': sum(r['available'] and r['sha'] in read for r in rows),
         'manifest_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest(),
         'source_index_snapshot': 'HISTORICAL_coverage.json', 'scientific_experiment': False}
(p / 'HISTORICAL_stream_available_raw_unread.scope.json').write_text(json.dumps(scope, indent=2) + '\n')
out = p / 'HISTORICAL_local_raw_run'
out.mkdir(exist_ok=True)
begin = time.monotonic()
start = datetime.datetime.now(datetime.timezone.utc).isoformat()
env = {**os.environ, 'PYTHONPATH': str(p / '_parser_dep'), 'GIT_NO_LAZY_FETCH': '1'}
jobs = []
for shard in range(4):
    log = open(out / f'shard-{shard}.log', 'w')
    command = [sys.executable, str(p / 'HISTORICAL_stream_audit.py'), 'run', '--manifest', str(manifest),
               '--output', str(out / f'shard-{shard}'), '--transport', 'local', '--local-repo',
               str(p.parent.parent / 'NBO'), '--shard-count', '4', '--shard-index', str(shard)]
    jobs.append((subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env), log))
try:
    statuses = [job.wait() for job, log in jobs]
finally:
    for job, log in jobs:
        if job.poll() is None:
            job.terminate()
            job.wait()
        log.close()
report = {'started_utc': start, 'ended_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'elapsed_seconds': time.monotonic() - begin, 'shard_returncodes': statuses,
          'scope': scope, 'script_sha256': hashlib.sha256((p / 'HISTORICAL_stream_audit.py').read_bytes()).hexdigest(),
          'scientific_experiment': False}
(out / 'supervisor.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
raise SystemExit(0 if all(x == 0 for x in statuses) else 2)
