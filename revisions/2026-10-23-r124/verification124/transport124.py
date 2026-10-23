"""Lossless publication transport; it never executes scientific calculations.

Make an archive of explicit native directories, record every native SHA-256,
split compressed bytes for reliable repository transfer, and independently
materialize checked members. Native output paths are never overwritten with
different bytes. All archive paths must be regular files within this revision.
"""
from pathlib import Path
import argparse, datetime, hashlib, io, json, stat, zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def make(destination, directories):
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    paths = {}
    for directory in directories:
        directory = Path(directory).resolve()
        if not directory.is_relative_to(ROOT):
            raise ValueError("Only this revision's explicit native directories")
        for p in sorted(directory.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:
                if p.is_symlink():
                    raise ValueError("No symlink transport")
                paths[str(p.relative_to(ROOT))] = p
    if not paths:
        raise ValueError("Empty native transport")
    buffer = io.BytesIO()
    members = {}
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED,
                         compresslevel=9, allowZip64=True) as z:
        for name, p in sorted(paths.items()):
            data = p.read_bytes()
            entry = zipfile.ZipInfo(name, (2026, 10, 23, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            z.writestr(entry, data)
            members[name] = {'bytes': len(data), 'sha256': digest(data)}
    data = buffer.getvalue()
    parts = []
    for index, offset in enumerate(range(0, len(data), 524288)):
        content = data[offset:offset+524288]
        name = f'evidence124.zip.part{index:04d}'
        (destination / name).write_bytes(content)
        parts.append({'path': name, 'bytes': len(content), 'sha256': digest(content)})
    manifest = dict(format='NBO-lossless-zip-parts-v1',
        created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        archive_sha256=digest(data), archive_bytes=len(data),
        native_files=len(members), native_bytes=sum(v['bytes'] for v in members.values()),
        parts=parts, files=members, scientific_calculations=0)
    (destination/'TRANSPORT124.json').write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k not in ('parts','files')}, indent=2))


def materialize(manifest_path):
    manifest_path = Path(manifest_path).resolve()
    m = json.loads(manifest_path.read_text())
    chunks = []
    for p in m['parts']:
        data = (manifest_path.parent/p['path']).read_bytes()
        if len(data) != p['bytes'] or digest(data) != p['sha256']:
            raise ValueError('Corrupt transport part '+p['path'])
        chunks.append(data)
    data = b''.join(chunks)
    if len(data) != m['archive_bytes'] or digest(data) != m['archive_sha256']:
        raise ValueError('Archive identity differs')
    restored = existing = 0
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = z.namelist()
        if len(names) != len(set(names)) or set(names) != set(m['files']):
            raise ValueError('Archive member census differs')
        for info in z.infolist():
            relative = Path(info.filename)
            mode = (info.external_attr >> 16) & 0o170000
            if relative.is_absolute() or '..' in relative.parts or '\\' in info.filename or info.is_dir() or mode not in (0, stat.S_IFREG):
                raise ValueError('Unsafe archive member')
            target = (ROOT/relative).resolve()
            if not target.is_relative_to(ROOT):
                raise ValueError('Member escapes revision')
            content = z.read(info)
            expected = m['files'][info.filename]
            if len(content) != expected['bytes'] or digest(content) != expected['sha256']:
                raise ValueError('Corrupt native member '+info.filename)
            if target.exists():
                if target.read_bytes() != content:
                    raise ValueError('Refuse to overwrite different native evidence '+info.filename)
                existing += 1
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open('xb') as stream:
                    stream.write(content)
                restored += 1
    print(json.dumps(dict(status='all-transport-and-native-hashes-verified',
        restored_files=restored, existing_identical_files=existing,
        native_bytes=m['native_bytes'], scientific_calculations=0), indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='mode', required=True)
    make_parser = sub.add_parser('make')
    make_parser.add_argument('--output', required=True)
    make_parser.add_argument('directories', nargs='+')
    restore_parser = sub.add_parser('materialize')
    restore_parser.add_argument('manifest')
    a = p.parse_args()
    if a.mode == 'make':
        make(a.output, a.directories)
    else:
        materialize(a.manifest)
