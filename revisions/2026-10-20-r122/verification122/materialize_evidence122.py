"""Verify and materialize losslessly transported R122 evidence; execute no science.

Existing files must already match. Archive members are strictly enumerated,
relative to this revision, and may not overwrite a different native byte.
"""
from __future__ import annotations
import argparse, hashlib, json, os, tempfile, time, zipfile
from pathlib import Path, PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def safe(name):
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name or p.as_posix()!=name:
        raise ValueError('Unsafe archive member '+name)
    if not name.startswith('results122/'):
        raise ValueError('Evidence transport cannot write outside results122: '+name)
    return ROOT.joinpath(*p.parts)
def materialize(request):
    start=time.perf_counter();request=Path(request);obj=json.loads(request.read_text())
    if obj['kind']!='lossless R122 executed-evidence transport':raise ValueError('Unexpected request type')
    expected={r['path']:r for r in obj['files']}
    if len(expected)!=len(obj['files']):raise ValueError('Duplicate manifest member')
    for name in expected:safe(name)
    with tempfile.TemporaryDirectory(prefix='nbo-r122-evidence-') as directory:
        archive=Path(directory)/'evidence.zip';h=hashlib.sha256();total=0
        with archive.open('xb') as out:
            for part in obj['parts']:
                p=request.parent/part['path']
                if p.stat().st_size!=part['bytes'] or digest(p)!=part['sha256']:raise ValueError('Corrupt transport part '+str(p))
                with p.open('rb') as f:
                    for b in iter(lambda:f.read(1<<20),b''):out.write(b);h.update(b);total+=len(b)
        if total!=obj['archive_bytes'] or h.hexdigest()!=obj['archive_sha256']:raise ValueError('Archive identity mismatch')
        added=0;existing=0
        with zipfile.ZipFile(archive) as z:
            infos=z.infolist()
            if len(infos)!=len(expected) or {i.filename for i in infos}!=set(expected):raise ValueError('Archive member census mismatch')
            for i in infos:
                r=expected[i.filename];dest=safe(i.filename)
                if i.is_dir() or ((i.external_attr>>16)&0o170000) not in (0,0o100000):raise ValueError('Nonregular archive member')
                if i.file_size!=r['bytes']:raise ValueError('Declared uncompressed size mismatch')
                if dest.exists():
                    if not dest.is_file() or dest.is_symlink() or dest.stat().st_size!=r['bytes'] or digest(dest)!=r['sha256']:raise ValueError('Existing native file differs: '+str(dest))
                    # Still read the archive member so its CRC and its bytes are checked.
                    native=None;existing+=1
                else:
                    dest.parent.mkdir(parents=True,exist_ok=True)
                    native=tempfile.NamedTemporaryFile(prefix='.transport122-',dir=dest.parent,delete=False)
                target=Path(native.name) if native is not None else None;memberhash=hashlib.sha256();size=0
                try:
                    with z.open(i) as f:
                        for b in iter(lambda:f.read(1<<20),b''):
                            memberhash.update(b);size+=len(b)
                            if native is not None:native.write(b)
                    if native is not None:native.close()
                    if size!=r['bytes'] or memberhash.hexdigest()!=r['sha256']:raise ValueError('Native member hash mismatch: '+i.filename)
                    if target is not None:
                        if dest.exists():raise ValueError('Concurrent native creation: '+str(dest))
                        os.replace(target,dest);added+=1
                finally:
                    if native is not None and not native.closed:native.close()
                    if target is not None and target.exists():target.unlink()
    return {'request':str(request.relative_to(ROOT)),'request_sha256':digest(request),'archive_sha256':obj['archive_sha256'],'files':len(expected),'native_bytes':sum(x['bytes'] for x in expected.values()),'newly_materialized':added,'already_identical':existing,'seconds':time.perf_counter()-start,'no_scientific_execution':True}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--registry',default='transport122/REGISTRY122.json');ap.add_argument('--output',required=True);a=ap.parse_args()
    out=ROOT/a.output;out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():raise FileExistsError(out)
    registry=ROOT/a.registry;data=json.loads(registry.read_text());results=[]
    for name in data['requests']:
        results.append(materialize(ROOT/name));print(json.dumps(results[-1]),flush=True)
    out.write_text(json.dumps({'status':'verified_materialization','registry_sha256':digest(registry),'bundles':results,'scope':'Exact saved bytes only; no new experiment, CI inference or economic claim'},indent=2)+'\n')
if __name__=='__main__':main()
