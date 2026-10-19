"""Bind a resumed package to the already published immutable S and P bytes.

This does not regenerate the published source/PDF manifest. Original ephemeral
TeX auxiliary payloads were not in P and are explicitly unavailable after the
runtime reset; their original hashes stay in the unchanged published manifest.
All native S/P files, actual manuscript inputs and PDFs are checked directly.
No scientific program or typesetting command is imported or executed.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import traceback

S = '6250abfd317f3b2a56cb1303eb5ce78249bf4042'
P = '68df062c7a29736b57f8bdb9e13bec951f510c7f'


def record(path):
    assert path.is_file() and not path.is_symlink(), str(path)
    before = path.stat()
    h = hashlib.sha256()
    g = hashlib.sha1(b'blob ' + str(before.st_size).encode() + b'\0')
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
            g.update(b)
    after = path.stat()
    assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
    return {'bytes': before.st_size, 'sha256': h.hexdigest(), 'git_blob': g.hexdigest()}


def write_new(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n')


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--revision', type=Path, required=True)
    a.add_argument('--derivatives', type=Path, required=True)
    a.add_argument('--output', type=Path, required=True)
    args = a.parse_args()
    root = args.revision.resolve()
    out = args.output.resolve()
    assert not out.is_relative_to(root)
    out.mkdir(parents=True, exist_ok=False)
    receipt = {'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
               'author_source_commit': S, 'pdf_commit': P, 'status': 'started',
               'scientific_execution': False, 'build_execution': False,
               'published_source_pdf_manifest_rewritten': False}
    try:
        env = dict(os.environ, GIT_NO_LAZY_FETCH='1')
        def git(*argv):
            return subprocess.check_output(['git', *argv], cwd=root, env=env)
        repo = Path(git('rev-parse', '--show-toplevel').decode().strip())
        prefix = root.relative_to(repo).as_posix() + '/'
        def tree(commit):
            assert git('rev-parse', '--verify', commit + '^{commit}').decode().strip() == commit
            result = {}
            for entry in git('ls-tree', '-r', '-z', commit, '--', prefix).split(b'\0'):
                if not entry:
                    continue
                head, name = entry.split(b'\t', 1)
                mode, kind, blob = head.decode().split()
                name = name.decode()
                assert kind == 'blob' and name.startswith(prefix)
                result[name[len(prefix):]] = {'git_blob': blob, 'git_mode': mode}
            return result
        source, published = tree(S), tree(P)
        assert len(source) == 1224 and len(published) == 1233
        assert all(published[k] == v for k, v in source.items())
        records = {}
        for name, expected in sorted(published.items()):
            got = record(root / name)
            assert got['git_blob'] == expected['git_blob'], name
            records[name] = {'path': name, **got, 'git_mode': expected['git_mode'],
                'kind': 'author_source' if name in source else 'publication_derivative'}
        spm_path = root / 'SOURCE_PDF_MANIFEST119.json'
        spm = json.loads(spm_path.read_bytes())
        assert spm['author_source_commit'] == S
        build = json.loads((root / spm['build_receipt']['path']).read_bytes())
        assert build['status'] == 'compiled_clean' and not build['issues'] and not build['placeholders']
        assert len(build['commands']) == 19 and all(x['exit_code'] == 0 for x in build['commands'])
        declared = dict(build['source_sha256'], **build['graphic_asset_sha256'])
        for name, expected in declared.items():
            assert name in source and records[name]['sha256'] == expected, name
        for rows in spm['actual_project_inputs'].values():
            for row in rows:
                assert row['path'] in source and records[row['path']]['sha256'] == row['sha256']
        assert len(spm['pdfs']) == 4
        for row in spm['pdfs']:
            assert all(records[row['path']][k] == row[k] for k in ('bytes', 'sha256'))
        auxiliary = sorted({name for group in build['generated_build_inputs'].values() for name in group})
        selection = json.loads(args.derivatives.read_bytes())
        chosen = selection['files']
        assert len({row['path'] for row in chosen}) == len(chosen)
        for row in chosen:
            name = row['path']
            pp = PurePosixPath(name)
            assert not pp.is_absolute() and '..' not in pp.parts and str(pp) == name
            assert name not in ('REFEREE_READY_INPUTS119.json', 'REFEREE_READY_PACKAGE119.json')
            assert not name.startswith('referee-ready119.zip')
            got = record(root / name)
            assert all(got[k] == row[k] for k in ('bytes', 'sha256', 'git_blob'))
            if name in records:
                assert records[name]['sha256'] == got['sha256']
            else:
                records[name] = {'path': name, **got, 'kind': 'publication_derivative'}
        assert 'PUBLICATION119.json' in records and 'FINAL_CI_STATUS119.json' in records
        assert json.loads((root / 'PUBLICATION119.json').read_bytes())['author_source_commit'] == S
        spec = {'schema': 'NBO_R119_RESUMED_REFEREE_READY_INPUT_V1',
            'author_source_commit': S, 'pdf_commit': P,
            'repository_revision_path': prefix.rstrip('/'),
            'repository_tree_sha': git('rev-parse', S + '^{tree}').decode().strip(),
            'native_files': len(source), 'native_bytes': sum(records[k]['bytes'] for k in source),
            'files': [records[k] for k in sorted(records)],
            'publication_derivative_members': len(records) - len(source),
            'selection': record(args.derivatives),
            'source_pdf_manifest': record(spm_path),
            'original_ephemeral_auxiliary_payloads': {'paths': auxiliary,
                'available_now': [p for p in auxiliary if (root / p).is_file()],
                'scope': 'Original hashes retained in unchanged published SPM; no claim of recovered original auxiliary bytes. The committed source is complete and successful independent CI compilation has its own artifact.'},
            'scope': 'Every native immutable author-source S file and every native published P file, plus explicitly selected current publication/CI/recovery derivatives. Scientific source, original raw evidence and distributed PDF bytes are unchanged. This new container replaces an unavailable local-only packaging derivative and is not a new experiment.'}
        write_new(out / 'REFEREE_READY_INPUTS119.json', spec)
        receipt.update({'status': 'verified_input_prepared', 'source_files': len(source),
                        'published_files': len(published), 'declared_build_sources': len(declared),
                        'package_members': len(records), 'input_manifest': record(out / 'REFEREE_READY_INPUTS119.json'),
                        'preparer': record(Path(__file__))})
    except BaseException:
        receipt['status'] = 'failed'
        receipt['exception'] = traceback.format_exc()
        raise
    finally:
        receipt['finished_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
        write_new(out / 'RESUMED_INPUT_PREPARATION119.json', receipt)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    main()
