"""Fixed R126 original-economy design; no economic calls on import."""
from pathlib import Path
from fractions import Fraction as F
import datetime as dt
import gzip, hashlib, json, os, platform, resource, sys, time, traceback

ROOT = Path(__file__).resolve().parents[1]
INHERITED = ROOT / 'inherited125'
R123 = INHERITED / 'code125/frozen_inputs/revisions/2026-10-22-r123'
R121 = R123 / 'vendor/2026-10-20-r121'
STATES = tuple((x / 16, y / 16) for x in (3, 9, 15) for y in (3, 9, 15))
ARMS = ('quadratic', 'relu', 'hinge', 'spline', 'poly2', 'poly3', 'grid')
MODES = ('fused_control', 'warm_adaptive', 'direct_terminal')
TARGET, TAU, OMEGA, DELTA = F(1, 65536), F(1, 256), F(1, 8192), F(15, 2**24)
LADDER = (32, 64, 128, 256, 512, 1024, 2048)
MAX_CENTERS, NODE_BUDGET = 8, 32768
ACTOR_COMMIT = '796c5f2badf68b051ac6c144884c0e61b87faf5e'
BASELINE_COMMIT = 'eda26b02fbfb1e02807bc0cee1c0015d62d59e56'


def plain(value):
    if isinstance(value, F): return str(value)
    if isinstance(value, Path): return str(value)
    if isinstance(value, dict): return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [plain(v) for v in value]
    if hasattr(value, 'tolist'): return plain(value.tolist())
    return value


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(2**20), b''): h.update(block)
    return h.hexdigest()


def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(plain(value), stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')


def append(path, value):
    path = Path(path)
    line = (json.dumps(plain(value), sort_keys=True, allow_nan=False) + '\n').encode()
    if path.suffix == '.gz':
        with path.open('ab') as raw:
            with gzip.GzipFile(fileobj=raw, filename='', mode='wb', mtime=0, compresslevel=6) as stream:
                stream.write(line)
    else:
        with path.open('ab') as stream: stream.write(line)


def rows(path):
    path = Path(path)
    with (gzip.open(path, 'rt') if path.suffix == '.gz' else path.open()) as stream:
        return [json.loads(line) for line in stream if line.strip()]


def actors():
    return [(i, 0, 'online', 'online') for i in range(2)] + [
        (i, b, a, loss) for i in range(2) for b in (5, 9)
        for a in ARMS for loss in ('value', 'marginal')]


def catalog():
    return [key + (mode,) for key in actors() for mode in MODES] + [
        (i, 0, 'uniform_dp', 'none', 'grid33') for i in range(2)]


def model_path(key):
    i, b, a, loss = key
    if a in ('online', 'uniform_dp'): return None
    return R121 / f'results121/acquisition{b}-attempt01/models/{i}-{a}-{loss}/model.json'


def verify_inputs(require_remote=True):
    source = json.loads((ROOT / 'SOURCE_FREEZE126.json').read_text())
    for rel, entry in source['files'].items():
        digest = entry if isinstance(entry, str) else entry['sha256']
        if sha(ROOT / rel) != digest: raise ValueError('R126 frozen byte mismatch: ' + rel)
    boundary = None
    if require_remote:
        boundary = json.loads((ROOT / 'BOUNDARIES126.json').read_text())
        if not boundary.get('remote_source_readback_before_economics'):
            raise ValueError('Remote readback must precede all R126 economic evaluations')
        if len(boundary['source_commit']) != 40:
            raise ValueError('A full published scientific source commit is required')
        if boundary['source_manifest_sha256'] != sha(ROOT / 'SOURCE_FREEZE126.json'):
            raise ValueError('R126 source boundary mismatch')
    return dict(files=len(source['files']), source_manifest_sha256=sha(ROOT / 'SOURCE_FREEZE126.json'), boundaries=boundary)


def start(output, kind):
    output = Path(output); output.mkdir(parents=True, exist_ok=False); tick = time.perf_counter()
    info = dict(kind=kind, started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                started_unix=time.time(), argv=sys.argv, python=sys.version, platform=platform.platform(),
                threads={k: os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')},
                shared_host=True, controlled_frequency_or_load=False)
    write(output / 'START126.json', info)
    return output, tick, info


def finish(output, tick, **more):
    receipt = dict(status='executed', exit_code=0, seconds=time.perf_counter()-tick,
                   ended_utc=dt.datetime.now(dt.timezone.utc).isoformat(), ended_unix=time.time(),
                   peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, **more)
    write(output / 'EXECUTION126.json', receipt)
    return receipt


def fail(output, tick):
    write(output / 'FAILURE126.json', dict(status='failed', seconds=time.perf_counter()-tick,
                                          traceback=traceback.format_exc(), partial_outputs_retained=True))
