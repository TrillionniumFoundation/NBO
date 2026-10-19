#!/usr/bin/env python3
"""Read-only Git/SPM/archive byte verification after R119 workspace restoration."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse
import gzip
import hashlib
import json
import os
import shutil
import stat
import subprocess
import time

EXPECTED_SOURCE = '6250abfd317f3b2a56cb1303eb5ce78249bf4042'
EXPECTED_PUBLICATION = '68df062c7a29736b57f8bdb9e13bec951f510c7f'
EXPECTED_ARCHIVES = {
    'current-results119.tar.gz': (26500711, 'cf7df5eaa1b67966584993b51db8a60d289b89d5e5c809f3d35807b9f9668cf1'),
    'r110-generated-evidence119.tar.gz': (14014082, '2dc7269fe761792570ff404819a5f1284e7f580bf70fcdc3272ebb911f6918cc'),
    'validation-d119.tar.gz': (49644124, '89ccf40eb1bbb470369df479e6441946ef4ef83587d139bd1f0d05a0607ec127'),
}


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def safe_relative(value):
    p = PurePosixPath(value)
    assert not p.is_absolute() and '..' not in p.parts
    return p


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--revision', type=Path, required=True)
    parser.add_argument('--audit-root', type=Path, required=True)
    args = parser.parse_args()
    revision = args.revision.resolve()
    repository = revision.parents[1]
    relative_revision = revision.relative_to(repository).as_posix()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    output = args.audit_root.resolve() / ('RECOVERY119_' + stamp)
    output.mkdir(parents=True, exist_ok=False)
    events_path = output / 'EVENTS119.jsonl'
    events = events_path.open('x', buffering=1)
    started = time.time()
    env = dict(os.environ)
    env['GIT_NO_LAZY_FETCH'] = '1'

    def event(row):
        events.write(json.dumps(row, sort_keys=True, separators=(',', ':')) + '\n')
        events.flush()
        os.fsync(events.fileno())

    def git(*arguments):
        result = subprocess.run(['git', *arguments], cwd=repository, env=env, capture_output=True)
        assert result.returncode == 0, (arguments, result.stderr.decode(errors='replace'))
        return result.stdout

    def tree(commit, path):
        result = {}
        for raw in git('ls-tree', '-r', '-z', commit + ':' + path).split(b'\0'):
            if not raw:
                continue
            head, name = raw.split(b'\t', 1)
            mode, kind, blob = head.decode().split()
            key = name.decode()
            safe_relative(key)
            assert key not in result and kind == 'blob'
            result[key] = {'git_mode': mode, 'git_blob': blob}
        return result

    def identity(base, relative, expected):
        safe_relative(relative)
        p = base / relative
        s = p.lstat()
        assert expected['git_mode'] in ('100644', '100755'), ('nonregular tracked mode', relative)
        assert stat.S_ISREG(s.st_mode) and not p.is_symlink(), relative
        executable = bool(s.st_mode & 0o111)
        assert executable == (expected['git_mode'] == '100755'), ('executable mode', relative)
        size = s.st_size
        blob = hashlib.sha1(('blob ' + str(size) + '\0').encode())
        full = hashlib.sha256()
        with p.open('rb') as f:
            for block in iter(lambda: f.read(1024 * 1024), b''):
                blob.update(block)
                full.update(block)
        after = p.lstat()
        assert (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns) == (
            after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        assert blob.hexdigest() == expected['git_blob'], ('Git blob mismatch', relative)
        return {'path': relative, 'bytes': size, 'sha256': full.hexdigest(),
                'git_blob': blob.hexdigest(), 'git_mode': expected['git_mode']}

    def compare(row, observed):
        assert row['bytes'] == observed['bytes'] and row['sha256'] == observed['sha256'], row['path']
        if 'git_blob' in row:
            assert row['git_blob'] == observed['git_blob'], row['path']
        if 'git_mode' in row:
            assert row['git_mode'] == observed['git_mode'], row['path']

    try:
        head = git('rev-parse', 'HEAD').decode().strip()
        parent = git('show', '-s', '--format=%P', head).decode().strip()
        assert head == EXPECTED_PUBLICATION and parent == EXPECTED_SOURCE
        event({'stage': 'started', 'unix': started, 'publication_commit': head,
               'author_source_commit': parent, 'scientific_rerun': False})
        stree = tree(parent, relative_revision)
        ptree = tree(head, relative_revision)
        assert len(stree) == 1224 and len(ptree) == 1233
        assert set(stree).issubset(ptree)
        assert all(stree[p] == ptree[p] for p in stree)
        derivatives = sorted(set(ptree) - set(stree))
        assert len(derivatives) == 9
        observed = {p: identity(revision, p, ptree[p]) for p in sorted(ptree)}
        event({'stage': 'all_native_publication_blobs_passed', 'files': len(observed),
               'bytes': sum(row['bytes'] for row in observed.values())})
        spm = json.loads((revision / 'SOURCE_PDF_MANIFEST119.json').read_text())
        inventory_path = 'provenance/final_publication119/source_binding/AUTHOR_SOURCE_INVENTORY119.json'
        inventory = json.loads((revision / inventory_path).read_text())
        assert inventory['author_source_commit'] == spm['author_source_commit'] == parent
        assert inventory['native_files'] == spm['native_files'] == len(stree)
        assert len(inventory['files']) == len(stree)
        assert {row['path'] for row in inventory['files']} == set(stree)
        assert len({row['path'] for row in inventory['files']}) == len(stree)
        for row in inventory['files']:
            compare(row, observed[row['path']])
        source_bytes = sum(observed[p]['bytes'] for p in stree)
        assert inventory['native_bytes'] == spm['native_bytes'] == source_bytes == 210506054
        source_tree = git('rev-parse', parent + '^{tree}').decode().strip()
        native_tree = git('rev-parse', parent + ':' + relative_revision).decode().strip()
        assert source_tree == inventory['repository_tree_sha'] == spm['repository_tree_sha']
        assert native_tree == inventory['native_revision_tree_sha'] == spm['native_revision_tree_sha']
        pdfs = []
        for row in spm['pdfs']:
            compare(row, observed[row['path']])
            assert (revision / row['path']).read_bytes().startswith(b'%PDF-')
            pdfs.append(observed[row['path']])
        assert len(pdfs) == 4
        compare(spm['build_receipt'], observed[spm['build_receipt']['path']])
        actual_inputs = 0
        for rows in spm['actual_project_inputs'].values():
            for row in rows:
                assert row['path'] in stree
                compare(row, observed[row['path']])
                actual_inputs += 1
        event({'stage': 'source_inventory_spm_and_pdf_bindings_passed',
               'source_files': len(stree), 'source_bytes': source_bytes,
               'publication_derivatives': len(derivatives), 'pdfs': len(pdfs),
               'actual_project_input_occurrences': actual_inputs})
        workflows = tree(head, '.github/workflows')
        workflow_rows = [identity(repository / '.github/workflows', p, row)
                         for p, row in sorted(workflows.items())]
        event({'stage': 'restored_workflow_blob_identities_passed', 'files': len(workflow_rows)})
        part_specs = []
        for name in ('evidence119/ARCHIVE_PARTS119.json', 'evidence119/VALIDATION_D_ARCHIVE_PARTS119.json'):
            part_specs.extend(json.loads((revision / name).read_text()))
        archive_manifests = {}
        for name in ('CURRENT_RESULTS_ARCHIVE119.json', 'R110_GENERATED_ARCHIVE119.json', 'VALIDATION_D_ARCHIVE119.json'):
            manifest = json.loads((revision / 'evidence119' / name).read_text())
            archive_manifests[manifest['archive']] = (name, manifest)
        assert {row['archive'] for row in part_specs} == set(EXPECTED_ARCHIVES)
        archives = []
        for spec in part_specs:
            manifest_name, manifest = archive_manifests[spec['archive']]
            wanted_bytes, wanted_sha = EXPECTED_ARCHIVES[spec['archive']]
            assert spec['archive_bytes'] == manifest['bytes'] == wanted_bytes
            assert spec['archive_sha256'] == manifest['sha256'] == wanted_sha
            concat = hashlib.sha256()
            size = 0
            parts = []
            for index, part in enumerate(spec['parts']):
                assert part['path'] == spec['archive'] + '.part' + str(index).zfill(3)
                relative = 'evidence119/' + part['path']
                compare(part, observed[relative])
                h = hashlib.sha256()
                count = 0
                with (revision / relative).open('rb') as f:
                    for block in iter(lambda: f.read(1024 * 1024), b''):
                        concat.update(block)
                        h.update(block)
                        count += len(block)
                assert count == part['bytes'] and h.hexdigest() == part['sha256']
                size += count
                parts.append(dict(observed[relative]))
            assert size == wanted_bytes and concat.hexdigest() == wanted_sha
            archives.append({'archive': spec['archive'], 'bytes': size, 'sha256': concat.hexdigest(),
                             'parts': parts, 'member_manifest': manifest_name,
                             'declared_members_in_verified_manifest': len(manifest['members']),
                             'declared_uncompressed_member_bytes': sum(r['bytes'] for r in manifest['members']),
                             'scope': 'All part bytes and concatenated container hash reread. No extraction, member re-evaluation, or experiment execution.'})
            event({'stage': 'archive_container_passed', 'archive': spec['archive'],
                   'parts': len(parts), 'bytes': size, 'sha256': concat.hexdigest()})
        assert git('rev-parse', 'HEAD').decode().strip() == head
        events.close()
        inventory_output = output / 'RECOVERED_NATIVE_IDENTITIES119.jsonl.gz'
        with inventory_output.open('xb') as f:
            with gzip.GzipFile(filename='', fileobj=f, mode='wb', compresslevel=9, mtime=0) as compressed:
                for row in observed.values():
                    compressed.write((json.dumps(row, sort_keys=True, separators=(',', ':')) + '\n').encode())
        result = {
            'schema': 'NBO-R119-post-restoration-byte-custody-v1',
            'status': 'passed_all_requested_restored_byte_identities',
            'started_unix': started, 'finished_unix': time.time(),
            'author_source_commit': parent, 'publication_commit': head,
            'source_tree': source_tree, 'native_source_tree': native_tree,
            'native_source_files': len(stree), 'native_source_bytes': source_bytes,
            'native_publication_files': len(ptree),
            'native_publication_bytes': sum(r['bytes'] for r in observed.values()),
            'source_paths_modified_or_removed_in_publication_commit': 0,
            'publication_derivatives': [observed[p] for p in derivatives],
            'source_pdf_manifest_identity': observed['SOURCE_PDF_MANIFEST119.json'],
            'source_inventory_identity': observed[inventory_path],
            'actual_project_input_occurrences_verified': actual_inputs,
            'generated_build_input_scope': 'Recorded historical build metadata; generated auxiliary files were not regenerated or required as native publication files.',
            'pdfs': pdfs, 'workflows_verified': workflow_rows,
            'archives': archives,
            'native_identity_inventory': {'path': inventory_output.name,
                                          'bytes': inventory_output.stat().st_size,
                                          'sha256': sha(inventory_output)},
            'event_log': {'path': events_path.name, 'bytes': events_path.stat().st_size,
                          'sha256': sha(events_path)},
            'verifier_source_sha256': sha(Path(__file__)),
            'preinterruption_zip': {'bytes': 178247262,
                                    'sha256': '1cfa881913f4c61113b78cd59d3e659738898f4b4459bd2784a54493b6571751',
                                    'status': 'Previously observed local-only derivative unavailable on resumption; not reconstructed or verified by this audit.'},
            'scope': 'Read-only local file/Git/SPM/archive identity validation after root restoration. No Git refs changed, no network fetch performed, no scientific solver imported, no numerical data regenerated, no typesetting or CI execution inferred.',
        }
        receipt = output / 'RECOVERY_CUSTODY119.json'
        with receipt.open('x') as f:
            json.dump(result, f, sort_keys=True, indent=2)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        # Root authorized only this publication-derivative copy after all checks pass.
        native_destination = revision / 'provenance/final_publication119/resumption119' / output.name
        native_destination.mkdir(parents=True, exist_ok=False)
        copies = []
        for source_file in (receipt, inventory_output, events_path, Path(__file__)):
            destination = native_destination / source_file.name
            with source_file.open('rb') as fin, destination.open('xb') as fout:
                shutil.copyfileobj(fin, fout, 1024 * 1024)
            assert sha(source_file) == sha(destination)
            copies.append({'source': str(source_file), 'destination': str(destination),
                           'bytes': destination.stat().st_size, 'sha256': sha(destination)})
        copy_receipt = output / 'NATIVE_COPY_BINDING119.json'
        with copy_receipt.open('x') as f:
            json.dump({'status': 'copied_after_identity_verification', 'copies': copies}, f, indent=2, sort_keys=True)
            f.write('\n')
        print(json.dumps({'status': result['status'], 'receipt': str(receipt),
                          'receipt_sha256': sha(receipt), 'native_copy': str(native_destination),
                          'source_files': len(stree), 'publication_files': len(ptree),
                          'workflow_files': len(workflow_rows), 'pdfs': pdfs,
                          'archives': [{'archive': a['archive'], 'parts': len(a['parts']),
                                        'bytes': a['bytes'], 'sha256': a['sha256']} for a in archives],
                          'copy_receipt_sha256': sha(copy_receipt)}), flush=True)
    except BaseException as exc:
        if not events.closed:
            event({'stage': 'aborted', 'unix': time.time(), 'exception_type': type(exc).__name__,
                   'exception': str(exc)})
            events.close()
        raise


if __name__ == '__main__':
    main()
