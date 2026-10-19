"""Record the actual metadata-only R119 container construction after recovery."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import platform
import resource
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent / 'package_attempt01'
out.mkdir(exist_ok=False)
command = [sys.executable, 'package119.py', 'referee-ready', '--input-manifest',
           'REFEREE_READY_INPUTS119.json', '--source-commit',
           '6250abfd317f3b2a56cb1303eb5ce78249bf4042']
def fileinfo(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return {'path': str(p.relative_to(root)), 'bytes': p.stat().st_size, 'sha256': h.hexdigest()}
record = {'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'argv': command,
          'cwd': str(root), 'python': sys.version, 'platform': platform.platform(),
          'packager': fileinfo(root / 'package119.py'),
          'input_manifest': fileinfo(root / 'REFEREE_READY_INPUTS119.json'),
          'recorder': fileinfo(Path(__file__)), 'scientific_execution': False,
          'typesetting_execution': False, 'status': 'started'}
with (out / 'PRELAUNCH119.json').open('x') as f:
    json.dump(record, f, indent=2, sort_keys=True)
    f.write('\n')
started = time.monotonic()
with (out / 'stdout.log').open('xb') as stdout, (out / 'stderr.log').open('xb') as stderr:
    executed = subprocess.run(command, cwd=root, stdout=stdout, stderr=stderr)
record.update({'exit_code': executed.returncode,
               'finished_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
               'elapsed_packaging_seconds': time.monotonic() - started,
               'stdout': fileinfo(out / 'stdout.log'), 'stderr': fileinfo(out / 'stderr.log'),
               'status': 'passed' if executed.returncode == 0 else 'failed'})
if executed.returncode == 0:
    summary = json.loads((out / 'stdout.log').read_bytes())
    assert summary['status'] == 'verified'
    record['packager_summary'] = summary
    record['output_manifest'] = fileinfo(root / 'REFEREE_READY_PACKAGE119.json')
with (out / 'PACKAGE_EXECUTION119.json').open('x') as f:
    json.dump(record, f, indent=2, sort_keys=True)
    f.write('\n')
print(json.dumps(record, sort_keys=True))
raise SystemExit(executed.returncode)
