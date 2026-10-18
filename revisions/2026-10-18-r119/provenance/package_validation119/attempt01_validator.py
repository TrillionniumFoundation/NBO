"""Attributable package validation, preserving the original scientific records."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import archive119

ROOT = Path(__file__).resolve().parent
CUSTODY = '095936f1a7556d90d74809e63d75d9959d118360'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        raise FileExistsError('Preserve every package-validation attempt; choose a fresh output path.')
    out.mkdir(parents=True)
    record = {'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'scope': 'Archive/source validation, fresh record-audit replay, declared exact fixture reuse and native proof algebra. No policy campaign or performance clock is rerun.',
              'python': sys.version, 'platform': platform.platform(),
              'commands': [], 'freezes': [], 'status': 'running'}
    try:
        record['checkout_sha'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    except subprocess.CalledProcessError:
        record['checkout_sha'] = None
    record['validator_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
               MKL_NUM_THREADS='1', NBO_SOURCE119=CUSTODY)

    def save():
        (out / 'VALIDATION119.json').write_text(json.dumps(record, indent=2) + '\n')

    def command(argv, label):
        p = out / (label + '.log')
        start = time.time()
        with p.open('wb') as f:
            result = subprocess.run(argv, cwd=ROOT, env=env, stdout=f,
                                    stderr=subprocess.STDOUT, timeout=900)
        row = {'argv': argv, 'started_unix': start, 'ended_unix': time.time(),
               'exit_code': result.returncode, 'log': p.name,
               'log_sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
        record['commands'].append(row)
        save()
        if result.returncode:
            raise RuntimeError('Validation stage failed: ' + label)
        print(json.dumps({'stage': label, 'exit_code': result.returncode}), flush=True)

    save()
    try:
        for name in ['SOURCE_FREEZE119.json', 'SOURCE_FREEZE119B.json', 'SOURCE_FREEZE119C.json']:
            freeze = json.loads((ROOT / name).read_bytes())
            checked = []
            for path, expected in freeze['files'].items():
                actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
                assert actual == expected, path
                checked.append({'path': path, 'sha256': actual})
            record['freezes'].append({'manifest': name,
                                      'manifest_sha256': hashlib.sha256((ROOT / name).read_bytes()).hexdigest(),
                                      'checked': checked})
        record['archives'] = [archive119.process(kind) for kind in ['current', 'r110']]
        replay = out / 'replay'
        archive119.process('current', replay)
        for phase, script, directory in [('A', 'audit119.py', 'primary119'),
                                          ('B', 'audit119b.py', 'primary119b'),
                                          ('C', 'audit119c.py', 'primary119c')]:
            command([sys.executable, 'code119/' + script, '--output',
                     str(replay / 'results119' / directory)], 'record-audit-' + phase)
        command([sys.executable, 'code119/independent_fused119.py',
                 '--custody-commit', CUSTODY, '--output', str(out / 'declared-fused-fixtures')],
                'declared-exact-fixtures')
        math = out / 'proof-algebra'
        math.mkdir()
        shutil.copyfile(ROOT / 'code119/verify_original_correctness119.py', math / 'verify_original_correctness119.py')
        shutil.copyfile(ROOT / 'new119/original_correctness119.tex', math / 'original_correctness119.tex')
        command([sys.executable, str(math / 'verify_original_correctness119.py')], 'original-proof-algebra')
        record['status'] = 'passed'
    except BaseException as error:
        record['status'] = 'failed'
        record['failure_type'] = type(error).__name__
        record['failure'] = str(error)
        raise
    finally:
        record['finished_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
        save()
    print(json.dumps({'status': record['status'], 'receipt': str(out / 'VALIDATION119.json')}))


if __name__ == '__main__':
    main()
