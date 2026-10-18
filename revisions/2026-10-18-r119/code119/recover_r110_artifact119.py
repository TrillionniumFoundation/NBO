"""Read-only recovery of one immutable R110 GitHub Actions artifact.

Download authorization is used only for GitHub's fixed artifact endpoint. The
signed storage redirect receives NO GitHub Authorization header. No recovered
file is imported, executed, revised, or used as a replacement R119 observation.
The original ZIP hash, every member hash, content-bound source/output manifests
and complete selected payload are retained. The selected ZIP is split into
strictly sub-400 MB transport parts; these are byte chunks, not independent ZIPs.

Prepared before recovery; existence of this script asserts no recovery success.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

REPO = 'TrillionniumFoundation/NBO'
ARTIFACT = 12053947106
RUN = 38899876276
COMMIT = '4ba2bbaa11b5fa59f83705b28b35bf82a63ca169'
TREE = '5885983fdef89cdc11fe471753cccfa46160956f'
EXPECTED_ZIP_SHA = 'dff93fc7dbf82f7a36ffbfde0c9c74a7b8ebc1006e3fd72ba33927c065e430cb'
EXPECTED_ZIP_BYTES = 638792519
API = f'https://api.github.com/repos/{REPO}/actions/artifacts/{ARTIFACT}'
BLOCK = 1024*1024
PAPER_HASHES = {
    'ECTA.tex': '565666c40cdb321322adbdfb45c4d225cb5748a60f6981d18b2cf4ac872b80a9',
    'supp.tex': 'f6e0282da02fa8fba4768e10476e15cfb2b26d6e3fcda5d51054283e9b775ceb',
    'appendix.tex': '5ae1c79abb326e6e1d97c60e064b6f1abfcb539b7d847ab798af5153b920b79c',
    'RESPONSE_TO_REFEREE.tex': 'd285101347c6080d545aa907e470320e34061ca285551074c8384d1da27131ff',
}
PDF_HASHES = {
    'ECTA': '8324c98438f7d1277af2764849c92d7ab9b22e3d78a162754d3f360068811213',
    'supp': '0a1e07772f0727dbec5df4e8e732696b7718281f5140101f08dfe70cd1895a17',
    'appendix': '493dc6d4e7871516b948f9b47c409cfb47f235efb1e1ca851662234c2017297b',
    'RESPONSE_TO_REFEREE': 'cbaeca5c13b44448087b1b09cdc05961903e3dcc6bcf4e91532e1e2497436c89',
}


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')


def require(condition, message):
    if not condition:
        raise ArithmeticError(message)


def file_hash(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(BLOCK), b''):
            h.update(block)
    return h.hexdigest()


def safe_name(name):
    require(isinstance(name, str) and name != '', 'Empty archive/manifest path')
    require('\x00' not in name and '\\' not in name and not name.startswith('/'), 'Absolute or platform-ambiguous archive path')
    clean = name[:-1] if name.endswith('/') else name
    require(clean and all(p not in ('', '.', '..') and ':' not in p for p in clean.split('/')), 'Unsafe archive path component')
    path = PurePosixPath(clean)
    require(not path.is_absolute() and str(path) == clean, 'Noncanonical archive path')
    return str(path)


def joined(base, relative):
    return safe_name(str(PurePosixPath(base)/safe_name(relative)))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        return None


def authorized_request(url, token):
    require(url in (API, API+'/zip'), 'Only the fixed immutable artifact API is authorized')
    return urllib.request.Request(url, headers={
        'Authorization': 'Bearer '+token,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'NBO-R119-immutable-R110-custody',
    })


def download(out):
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    require(bool(token), 'No authorized GitHub token configured for this read-only recovery')
    opener = urllib.request.build_opener(NoRedirect)
    with opener.open(authorized_request(API, token), timeout=60) as response:
        body = response.read(2*BLOCK+1)
    require(len(body) <= 2*BLOCK, 'Unexpectedly large artifact metadata response')
    metadata = json.loads(body)
    require(metadata['id'] == ARTIFACT and metadata['workflow_run']['id'] == RUN, 'Artifact/run identity mismatch')
    require(metadata['workflow_run']['head_sha'] == COMMIT, 'Artifact source commit mismatch')
    require(metadata['size_in_bytes'] == EXPECTED_ZIP_BYTES, 'Artifact byte-size metadata mismatch')
    require(metadata.get('digest') == 'sha256:'+EXPECTED_ZIP_SHA, 'Artifact digest metadata mismatch')
    require(not metadata['expired'], 'The immutable original artifact has expired')
    save(out/'manifests'/'ARTIFACT_METADATA.json', metadata)
    try:
        response = opener.open(authorized_request(API+'/zip', token), timeout=60)
    except urllib.error.HTTPError as redirect:
        require(redirect.code in (301, 302, 303, 307, 308), 'Artifact endpoint did not return an authorized download redirect')
        location = redirect.headers.get('Location', '')
        redirect.close()
        target = urllib.parse.urlsplit(location)
        host = (target.hostname or '').lower()
        allowed = (host.endswith('.blob.core.windows.net') or host.endswith('.actions.githubusercontent.com')
                   or host in ('objects.githubusercontent.com', 'github.com', 'api.github.com'))
        require(target.scheme == 'https' and not target.username and not target.password and allowed, 'Unrecognized artifact storage redirect')
        # Never forward the GitHub bearer token to signed object storage.
        request = urllib.request.Request(location, headers={'User-Agent': 'NBO-R119-immutable-R110-custody'})
        response = urllib.request.urlopen(request, timeout=60)
    path = out/'original-artifact12053947106.zip'
    h, size, progress = hashlib.sha256(), 0, 0
    with response, path.open('xb') as destination:
        while True:
            block = response.read(BLOCK)
            if not block:
                break
            size += len(block)
            require(size <= EXPECTED_ZIP_BYTES, 'Artifact stream exceeds its immutable declared size')
            destination.write(block); h.update(block)
            if size-progress >= 64*BLOCK:
                print(f'R110 immutable artifact downloaded {size} bytes', flush=True)
                progress = size
    require(size == EXPECTED_ZIP_BYTES and h.hexdigest() == EXPECTED_ZIP_SHA, 'Downloaded original archive identity mismatch')
    return path


def inspect_all(archive):
    records, by_name = [], {}
    for index, info in enumerate(archive.infolist()):
        name = safe_name(info.filename)
        require(name not in by_name, 'Duplicate normalized archive member')
        mode = info.external_attr >> 16
        kind = stat.S_IFMT(mode)
        require(kind in (0, stat.S_IFREG, stat.S_IFDIR), 'Symlink or special archive member rejected')
        require(not (info.flag_bits & 1), 'Encrypted archive member rejected')
        row = dict(path=name, bytes=info.file_size, compressed_bytes=info.compress_size,
                   crc32=f'{info.CRC:08x}', directory=info.is_dir(), unix_mode=mode)
        if not info.is_dir():
            h, git, size = hashlib.sha256(), hashlib.sha1(), 0
            git.update(b'blob '+str(info.file_size).encode()+b'\x00')
            with archive.open(info) as stream:
                for block in iter(lambda: stream.read(BLOCK), b''):
                    size += len(block); h.update(block); git.update(block)
            require(size == info.file_size, 'Member decompression size mismatch')
            row.update(sha256=h.hexdigest(), git_blob=git.hexdigest())
        by_name[name] = row; records.append(row)
        if (index+1) % 1000 == 0:
            print(f'R110 content hashed {index+1} archive members', flush=True)
    return records, by_name


def select_bound_members(archive, by_name):
    attempts = []
    for name in by_name:
        if PurePosixPath(name).name != 'REMOTE_ATTEMPT110.json':
            continue
        obj = json.loads(archive.read(name))
        if str(obj.get('run_id')) == str(RUN) and obj.get('workflow_commit') == COMMIT:
            attempts.append((name, obj))
    require(len(attempts) == 1, 'Need exactly one content-matching original R110 remote execution manifest')
    manifest_name, manifest = attempts[0]
    require(manifest.get('job_status_before_receipt') == 'success', 'Original remote manifest does not record success')
    base = str(PurePosixPath(manifest_name).parent)
    selected = {manifest_name}
    checks = []
    for item in manifest['files']:
        name = joined(base, item['path'])
        require(name in by_name and not by_name[name]['directory'], 'Original output manifest member is absent')
        row = by_name[name]
        require(row['sha256'] == item['sha256'] and row['bytes'] == item['bytes'], 'Original output content manifest mismatch: '+name)
        require(name not in selected, 'Duplicate original output manifest entry')
        selected.add(name)
        checks.append(dict(path=name, sha256=row['sha256'], bytes=row['bytes'], output_manifest_verified=True))
    exports = []
    for name in selected:
        if PurePosixPath(name).name != 'REMOTE_SOURCE_EXPORT110.json':
            continue
        obj = json.loads(archive.read(name))
        if obj.get('workflow_commit') == COMMIT and obj.get('revision_tree') == TREE:
            exports.append((name, obj))
    require(len(exports) == 1, 'Need exactly one content-matching R110 scientific source export')
    export_name, source = exports[0]
    source_base = str(PurePosixPath(export_name).parent)
    paper_checks = []
    for filename, expected in PAPER_HASHES.items():
        name = joined(source_base, filename)
        require(name in selected and by_name[name]['sha256'] == expected, 'Complete native R110 manuscript source identity mismatch: '+filename)
        paper_checks.append(dict(path=name, sha256=expected))
    pdf_checks = []
    for document, expected in PDF_HASHES.items():
        matches = sorted(name for name in selected if by_name[name].get('sha256') == expected)
        require(bool(matches), 'Actual logged R110 PDF bytes absent: '+document)
        pdf_checks.append(dict(document=document, sha256=expected, matching_paths=matches))
    export_checks = []
    for item in source['files']:
        name = joined(source_base, item['path'])
        row = by_name.get(name)
        match = row is not None and row.get('sha256') == item['sha256'] and row.get('git_blob') == item['git_blob']
        # Generated reports may be replaced by this very source/build run. Keep
        # that distinction; only immutable source extensions must still match.
        immutable = PurePosixPath(name).suffix.lower() in ('.tex','.bib','.bst','.cls','.sty','.py','.sh')
        require(match or not immutable, 'Immutable exported scientific source changed inside original artifact: '+name)
        export_checks.append(dict(path=name, declared_sha256=item['sha256'], declared_git_blob=item['git_blob'],
                                  actual_sha256=None if row is None else row.get('sha256'),
                                  exact_export_match=match, immutable_source=immutable))
    frozen_checks = []
    for filename in ('SOURCE_FREEZE110.json', 'SOURCE_FREEZE108.json'):
        name = joined(source_base, filename)
        require(name in selected, 'Original core source freeze missing: '+filename)
        freeze = json.loads(archive.read(name))
        for relative, expected in freeze['scientific_files'].items():
            path = joined(source_base, relative)
            require(path in selected and by_name[path]['sha256'] == expected, 'Original frozen executable dependency mismatch: '+path)
            frozen_checks.append(dict(manifest=name, path=path, sha256=expected))
    return sorted(selected), dict(original_execution_manifest=manifest_name,
        original_source_export=export_name, workflow_commit=COMMIT, revision_tree=TREE,
        output_files=checks, manuscript_source=paper_checks, logged_pdf_bytes=pdf_checks,
        source_export_checks=export_checks, frozen_executable_checks=frozen_checks,
        selection_rule='All exact files named by the content-verified original run manifest plus that manifest; no branch-name heuristic or favorable-result filter.',
        scope='Immutable original R110 source/build/reproduction bytes. This recovery does not rerun science, re-time methods, inspect every proof, or substitute these data for R119.')


def extract_and_repack(archive, selected, by_name, out):
    destination = out/'selected'
    destination.mkdir()
    repacked = out/'r110-verified-selected.zip'
    with zipfile.ZipFile(repacked, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as packed:
        for index, name in enumerate(selected):
            relative = safe_name(name)
            path = destination.joinpath(*PurePosixPath(relative).parts)
            require(path.resolve().is_relative_to(destination.resolve()), 'Selected extraction escaped custody directory')
            path.parent.mkdir(parents=True, exist_ok=True)
            h = hashlib.sha256()
            info = zipfile.ZipInfo(relative, date_time=archive.getinfo(name).date_time)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            with archive.open(name) as incoming, path.open('xb') as local, packed.open(info, 'w', force_zip64=True) as copy:
                for block in iter(lambda: incoming.read(BLOCK), b''):
                    local.write(block); copy.write(block); h.update(block)
            require(h.hexdigest() == by_name[name]['sha256'], 'Extracted selected bytes changed')
            if (index+1) % 1000 == 0:
                print(f'R110 safely extracted and repacked {index+1} selected files', flush=True)
    return repacked


def split_repack(path, out, part_bytes):
    require(1_000_000 <= part_bytes < 400_000_000, 'Every transport part must be strictly below 400 MB')
    total_hash = file_hash(path)
    parts = []
    with path.open('rb') as incoming:
        index = 0
        while True:
            first = incoming.read(min(BLOCK, part_bytes))
            if not first:
                break
            folder = out/'parts'/f'part-{index:03d}'
            folder.mkdir(parents=True)
            target = folder/'chunk.bin'
            h, size = hashlib.sha256(), 0
            with target.open('xb') as local:
                block = first
                while block:
                    local.write(block); h.update(block); size += len(block)
                    if size == part_bytes:
                        break
                    block = incoming.read(min(BLOCK, part_bytes-size))
            record = dict(index=index, path=str(target.relative_to(out)), bytes=size, sha256=h.hexdigest(),
                          concatenation_offset=index*part_bytes, complete_repacked_zip_sha256=total_hash)
            save(folder/'PART.json', record)
            parts.append(record); index += 1
    require(sum(p['bytes'] for p in parts) == path.stat().st_size, 'Transport splitting lost bytes')
    manifest = dict(parts=parts, complete_repacked_zip_sha256=total_hash, complete_repacked_zip_bytes=path.stat().st_size,
        original_zip_sha256=EXPECTED_ZIP_SHA, original_zip_bytes=EXPECTED_ZIP_BYTES,
        instruction='Verify each chunk SHA and concatenate in increasing index to reconstruct the NEW selected ZIP; then verify its complete SHA. Its selected member bytes match the original immutable ZIP. Individual chunks are not standalone ZIPs.')
    save(out/'manifests'/'REPACK_PARTS.json', manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--local-zip', type=Path, help='Optional already-downloaded ORIGINAL ZIP; the same immutable hash and byte-size checks remain mandatory')
    parser.add_argument('--part-bytes', type=int, default=350_000_000)
    args = parser.parse_args()
    require(not args.output.exists(), 'Refusing to overwrite any previous recovery or failed attempt')
    args.output.mkdir(parents=True)
    start = time.time()
    save(args.output/'manifests'/'START.json', dict(status='started', started_unix=start,
        original_artifact=ARTIFACT, original_run=RUN, original_commit=COMMIT,
        source_sha256=file_hash(Path(__file__)), current_custody_workflow_commit=os.environ.get('GITHUB_SHA'),
        current_custody_workflow_run=os.environ.get('GITHUB_RUN_ID'), python=sys.version,
        scientific_execution=False, expected_original_zip_sha256=EXPECTED_ZIP_SHA))
    try:
        if args.local_zip:
            original = args.output/'original-artifact12053947106.zip'
            with args.local_zip.open('rb') as src, original.open('xb') as dst:
                shutil.copyfileobj(src, dst, BLOCK)
        else:
            original = download(args.output)
        require(original.stat().st_size == EXPECTED_ZIP_BYTES and file_hash(original) == EXPECTED_ZIP_SHA,
                'Original immutable artifact ZIP hash or size mismatch')
        with zipfile.ZipFile(original) as archive:
            members, by_name = inspect_all(archive)
            save(args.output/'manifests'/'ALL_MEMBERS.json', dict(original_zip_sha256=EXPECTED_ZIP_SHA,
                original_zip_bytes=original.stat().st_size, members=members, member_count=len(members),
                uncompressed_bytes=sum(v['bytes'] for v in members), all_members_fully_hashed_and_crc_checked=True))
            selected, bound = select_bound_members(archive, by_name)
            save(args.output/'manifests'/'CONTENT_SELECTION.json', bound)
            repacked = extract_and_repack(archive, selected, by_name, args.output)
        pieces = split_repack(repacked, args.output, args.part_bytes)
        receipt = dict(status='verified_original_bytes_and_repacked', artifact_id=ARTIFACT, original_run=RUN,
            original_commit=COMMIT, original_zip_sha256=EXPECTED_ZIP_SHA, original_zip_bytes=EXPECTED_ZIP_BYTES,
            actual_member_count=len(members), selected_files=len(selected), omitted_members=[v['path'] for v in members if v['path'] not in selected],
            selected_zip_sha256=pieces['complete_repacked_zip_sha256'], selected_zip_bytes=pieces['complete_repacked_zip_bytes'],
            transport_parts=len(pieces['parts']), maximum_part_bytes=max(p['bytes'] for p in pieces['parts']),
            source_export_exact_matches=sum(v['exact_export_match'] for v in bound['source_export_checks']),
            source_export_generated_differences=[v for v in bound['source_export_checks'] if not v['exact_export_match']],
            manifests=[dict(path=str(p.relative_to(args.output)), sha256=file_hash(p)) for p in sorted((args.output/'manifests').glob('*.json'))],
            started_unix=start, completed_unix=time.time(), scientific_execution=False,
            scope='Original immutable R110 artifact byte custody only; no reproduced scientific outcomes or R119 observation claimed.')
        save(args.output/'manifests'/'RECOVERY_RECEIPT.json', receipt)
        print(json.dumps({k:v for k,v in receipt.items() if k not in ('omitted_members','source_export_generated_differences','manifests')}, indent=2), flush=True)
        print('Upload manifests/ separately and EACH parts/part-NNN directory as a separate artifact; do not upload original ZIP or all parts into one oversized artifact.', flush=True)
    except Exception as exc:
        message = re.sub(r'https?://\S+', '[URL omitted]', str(exc))
        for name in ('GITHUB_TOKEN', 'GH_TOKEN'):
            token = os.environ.get(name)
            if token:
                message = message.replace(token, '[credential omitted]')
        save(args.output/'manifests'/'FAILED.json', dict(status='failed', original_artifact=ARTIFACT,
            exception_class=type(exc).__name__, message=message, failed_unix=time.time(),
            scientific_execution=False, partial_files_retained=True))
        print('R110 recovery failed: '+type(exc).__name__+': '+message, flush=True)
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
