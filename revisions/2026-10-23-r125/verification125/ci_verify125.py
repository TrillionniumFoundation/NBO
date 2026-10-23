"""Run independently recorded R125 package, algebra and document CI gates.

No new training, population sample, or protected historical experiment is run.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out = ROOT / 'ci125' / stamp
    out.mkdir(parents=True, exist_ok=False)
    tick = time.perf_counter()
    receipt = {'started_utc': stamp, 'github_sha': os.environ.get('GITHUB_SHA'),
               'github_run_id': os.environ.get('GITHUB_RUN_ID'),
               'scope': 'package hashes, source gate, saved-certificate replay, exact mathematical fixtures and four-document compilation',
               'fresh_original_economy_experiment': False, 'commands': [], 'status': 'running'}

    def save():
        (out / 'CI_RECEIPT125.json').write_text(json.dumps(receipt, indent=2) + '\n')

    def run(label, command):
        start = time.perf_counter()
        log = out / (label + '.log')
        row = {'label': label, 'command': list(map(str, command)), 'status': 'running'}
        receipt['commands'].append(row)
        save()
        with log.open('wb') as f:
            result = subprocess.run(list(map(str, command)), cwd=ROOT, stdout=f,
                                    stderr=subprocess.STDOUT, check=False)
        row.update(exit_code=result.returncode, seconds=time.perf_counter() - start,
                   status='passed' if result.returncode == 0 else 'failed',
                   log_sha256=hashlib.sha256(log.read_bytes()).hexdigest())
        save()
        print(json.dumps(row), flush=True)
        if result.returncode:
            print(log.read_text(errors='replace')[-8000:])
            raise RuntimeError('CI gate failed: ' + label)

    try:
        run('delivered-package', [sys.executable, 'verification125/verify_package125.py',
                                 '--output', out / 'package'])
        run('exact-fixtures', [sys.executable, 'code125/fixtures125.py', '--output', out / 'fixtures'])
        copied = out / 'check_obstacle_interpolation125.py'
        shutil.copyfile(ROOT / 'provenance/check_obstacle_interpolation125.py', copied)
        run('independent-obstacle-algebra', [sys.executable, copied])
        run('saved-certificate-replay', [sys.executable, 'code125/verify125.py',
            '--primary', 'results125/primary', '--timing', 'results125/timing0',
            '--timing', 'results125/timing1', '--timing', 'results125/timing2',
            '--output', out / 'replay'])
        run('four-native-documents', [sys.executable, 'build125.py', '--passes', '4',
            '--receipt-dir', str(out.relative_to(ROOT) / 'build_receipts')])
        receipt['status'] = 'passed'
    except BaseException as exc:
        receipt.update(status='failed', error_type=type(exc).__name__, error=str(exc))
        raise
    finally:
        receipt['seconds'] = time.perf_counter() - tick
        receipt['finished_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
        save()
        print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
