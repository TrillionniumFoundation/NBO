"""Prepare bounded, lossless transport of an explicitly selected author snapshot.

Read-only with respect to selected native inputs and Git references. The output
is administrative custody, never an economic execution or preregistration.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PREFIX = 'revisions/2026-10-20-r122/'
PART_BYTES = 180 * 1024


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def canonical(name):
    p = PurePosixPath(name)
    need(isinstance(name, str) and name and not p.is_absolute() and '..' not in p.parts
         and '.git' not in p.parts and '\\' not in name and str(p) == name, 'Unsafe path')
    return name


def ordinary(name):
    path = REPO
    for part in PurePosixPath(canonical(name)).parts:
        path /= part
        need(not path.is_symlink(), 'Symlink in selected path: ' + name)
    need(path.is_file() and path.resolve().is_relative_to(REPO), 'Missing ordinary selected file: ' + name)
    return path


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--paths', type=Path, required=True)
    parser.add_argument('--tag', required=True)
    args = parser.parse_args()
    need(args.tag and all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in args.tag), 'Simple unique tag required')
    started = time.perf_counter()
    source_parent = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=REPO, text=True).strip()
    need(branch == 'revision/econometrica-nbo-r122-action-information-2026-10-20', 'Wrong isolated branch')
    selected = json.loads(args.paths.read_text())
    need(isinstance(selected, list) and selected and len(selected) == len(set(selected)), 'Explicit unique path list required')
    selected = sorted(canonical(name) for name in selected)
    need(all(name.startswith(PREFIX) or (name.startswith('.github/workflows/nbo-r122-') and name.endswith('.yml')) for name in selected), 'Selection outside revision scope')
    out = ROOT / 'transport122/author-source' / args.tag
    out.mkdir(parents=True, exist_ok=False)
    # Query only explicit paths. A full historical-tree size traversal in a
    # partial clone would perform unnecessary remote blob reads.
    base = {}
    for start in range(0, len(selected), 100):
        data = subprocess.check_output(['git', 'ls-tree', '-z', source_parent, '--', *selected[start:start+100]], cwd=REPO)
        for record in data.split(b'\0'):
            if not record:
                continue
            info, name = record.decode().split('\t', 1)
            mode, kind, blob = info.split()
            need(kind == 'blob' and mode in ('100644', '100755'), 'Existing non-ordinary target')
            base[name] = (mode, blob)
    frozen = ROOT / 'SOURCE_FREEZE122.json'
    need(digest(frozen) == 'eba26439a799392b7553d06fea5f17828c8988b9f72f4e049058771985ac8b0f', 'Frozen scientific inventory changed')
    scientific = json.loads(frozen.read_text())['scientific_files']
    rows, unchanged, selected_bindings = [], [], []
    with tempfile.TemporaryDirectory(prefix='nbo-r122-author-transport-') as temp:
        archive = Path(temp) / 'author-source.zip'
        with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as target:
            for name in selected:
                path = ordinary(name)
                data = path.read_bytes()
                need(len(data) < 95 * 1024 * 1024, 'Individual native file exceeds declared Git size bound')
                identity = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                mode = '100755' if path.stat().st_mode & 0o111 else '100644'
                selected_bindings.append(dict(path=name, bytes=len(data), sha256=sha(data), mode=mode))
                if name in scientific:
                    need(sha(data) == scientific[name], 'Frozen scientific bytes would change')
                if base.get(name) == (mode, identity):
                    unchanged.append(name)
                    continue
                row = dict(path=name, bytes=len(data), sha256=sha(data), git_blob=identity,
                    base_blob=base.get(name, (None, None))[1], mode=mode)
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = (0o100755 if mode == '100755' else 0o100644) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                target.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
                need(path.read_bytes() == data, 'Selected file changed during snapshot')
                rows.append(row)
        need(rows, 'No changed native file to promote')
        expected = {row['path']: row for row in rows}
        with zipfile.ZipFile(archive) as saved:
            infos = saved.infolist()
            need(len(infos) == len(rows) and {x.filename for x in infos} == set(expected), 'Prepared archive membership differs')
            for info in infos:
                row = expected[info.filename]
                data = saved.read(info)
                mode = '100755' if (info.external_attr >> 16) & 0o111 else '100644'
                need(len(data) == row['bytes'] and sha(data) == row['sha256'] and mode == row['mode'], 'Prepared ZIP member differs from selected native bytes or mode')
        parts = []
        with archive.open('rb') as source:
            for index in range((archive.stat().st_size + PART_BYTES - 1) // PART_BYTES):
                data = source.read(PART_BYTES)
                path = out / ('payload.part%04d' % index)
                with path.open('xb') as stream:
                    stream.write(data)
                parts.append(dict(path=path.relative_to(REPO).as_posix(), bytes=len(data), sha256=sha(data)))
        manifest = dict(schema='nbo.r122.exact-author-source-transport.v1', path_root='repository',
            scientific_execution=False, observed_parent_commit=source_parent,
            explicit_selection_sha256=digest(args.paths), archive_bytes=archive.stat().st_size,
            archive_sha256=digest(archive), native_bytes=sum(row['bytes'] for row in rows),
            member_count=len(rows), files=rows, parts=parts,
            unchanged_selected_paths=unchanged,
            scope='Lossless author and administrative native-byte snapshot. New source promotion has its own commit; all frozen experimental sources, samples, results and costs retain their identities.')
        manifest_path = out / 'SOURCE_TRANSPORT122.json'
        write(manifest_path, manifest)
    for row in selected_bindings:
        path = ordinary(row['path'])
        need(path.stat().st_size == row['bytes'] and digest(path) == row['sha256'], 'Selected snapshot input changed before closure')
        mode = '100755' if path.stat().st_mode & 0o111 else '100644'
        need(mode == row['mode'], 'Selected native mode changed before closure')
    need(digest(frozen) == 'eba26439a799392b7553d06fea5f17828c8988b9f72f4e049058771985ac8b0f', 'Frozen inventory changed during preparation')
    trigger = dict(schema='nbo.r122.author-source-promotion.v1',
        manifest=manifest_path.relative_to(REPO).as_posix(), manifest_sha256=digest(manifest_path))
    write(out / 'TRIGGER_PAYLOAD122.json', trigger)
    receipt = dict(status='prepared_and_checked_exact_native_transport',
        reader_sha256=digest(Path(__file__)), observed_parent_commit=source_parent,
        finished_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        manifest=manifest_path.relative_to(REPO).as_posix(), manifest_sha256=digest(manifest_path),
        selected_files=len(selected), changed_files=len(rows), unchanged_files=len(unchanged),
        native_bytes=manifest['native_bytes'], archive_bytes=manifest['archive_bytes'],
        archive_sha256=manifest['archive_sha256'], parts=len(parts), part_max_bytes=PART_BYTES,
        elapsed_seconds=time.perf_counter()-started,
        new_scientific_evaluations=0, remote_publication_asserted=False,
        cost_clock_components=[dict(category='author_source_transport_preparation',
            clock_fields=[['elapsed_seconds']], partial_lower_bound_only=True,
            overlaps_counted_parent=False, scope='This actual serial source-transport preparation only; no remote upload or source-promotion workflow included.')])
    write(out / 'PREPARATION122.json', receipt)
    print(json.dumps({key: receipt[key] for key in ('status','changed_files','unchanged_files','native_bytes','archive_bytes','parts','elapsed_seconds','manifest_sha256')}))


if __name__ == '__main__':
    main()
