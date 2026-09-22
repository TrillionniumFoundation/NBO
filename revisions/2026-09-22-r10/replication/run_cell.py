"""Re-execute a planned original-model certificate; never discard failed output.
This command does not refit policies or change the frozen reference controls.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, os, pathlib, platform, shutil, subprocess, sys, time, traceback
ROOT = pathlib.Path(__file__).resolve().parents[3]
REV = ROOT / 'revisions/2026-09-22-r10'
def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
def main(k, destination):
    if k not in (.5, 2., 8.): raise ValueError('Cost is not a planned cell')
    tag = f'k{k:g}'; out = pathlib.Path(destination).resolve(); out.mkdir(parents=True, exist_ok=True)
    source = os.environ.get('R10_SOURCE_COMMIT') or subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    status = {'cell': tag, 'cost': k, 'source_commit': source, 'status': 'running',
              'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'python': platform.python_version(), 'platform': platform.platform()}
    clock = time.perf_counter(); write(out/'status.json', status)
    try:
        import verify_inputs
        status['input_validation'] = verify_inputs.run()
        import numpy, mpmath
        status.update(numpy=numpy.__version__, mpmath=mpmath.__version__)
        for stem in ('actor', 'dual_pilot'):
            src = REV / 'results' / f'{stem}_{tag}.json'
            shutil.copy2(src, out / src.name)
        sys.path.insert(0, str(ROOT/'revisions/2026-09-22-r9/replication'))
        import original_policy_certificate as policy
        import flexible_dual as dual
        policy.OUT = out; dual.OUT = out
        policy.run(tag, resolutions=(64, 256, 1024))
        result = dual.run(k, resolutions=((4,64), (8,128), (16,256)))
        assert result['status'] == 'complete' and result['records'][-1]['target_met']
        status['status'] = 'success'
    except BaseException as exc:
        status['status'] = 'failed'; status['exception'] = type(exc).__name__ + ': ' + str(exc)
        (out/'exception.txt').write_text(traceback.format_exc())
        raise
    finally:
        status['seconds'] = time.perf_counter() - clock
        status['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        status['files'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file() and p.name != 'status.json'}
        write(out/'status.json', status)
if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--k', type=float, required=True); p.add_argument('--output', required=True)
    a = p.parse_args(); main(a.k, a.output)
