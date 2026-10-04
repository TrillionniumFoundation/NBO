"""Restore the 19 immutable, hash-pinned executed study artifacts.

No numerical computation is repeated. Authentication is used only for the
GitHub API request; the signed storage request never receives that header.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[3]
R = Path(__file__).resolve().parents[1]


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for b in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def download(artifact, repository, target):
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        raise RuntimeError('GITHUB_TOKEN is required to restore retained Actions artifacts')
    url = 'https://api.github.com/repos/' + repository + '/actions/artifacts/' + str(artifact['artifact_id']) + '/zip'
    request = urllib.request.Request(url, headers={
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'NBO-R14-evidence-restoration',
    })
    try:
        response = urllib.request.build_opener(NoRedirect()).open(request, timeout=120)
    except urllib.error.HTTPError as error:
        if error.code not in (301, 302, 303, 307, 308):
            raise RuntimeError('Artifact API returned HTTP ' + str(error.code)) from None
        destination = error.headers['Location']
        if urllib.parse.urlparse(destination).scheme != 'https':
            raise RuntimeError('Artifact redirect must use HTTPS')
        # Deliberately construct a fresh unauthenticated request.
        response = urllib.request.urlopen(destination, timeout=120)
    with response, Path(target).open('wb') as output:
        shutil.copyfileobj(response, output, length=1024 * 1024)
    if Path(target).stat().st_size != artifact['size_bytes']:
        raise AssertionError('Archive size mismatch: ' + artifact['name'])
    if digest(target) != artifact['archive_sha256']:
        raise AssertionError('Archive digest mismatch: ' + artifact['name'])


def restore(verify_only=False):
    manifest = json.loads((R / 'ARTIFACT_RESTORE_MANIFEST.json').read_text())
    if manifest['repository'] != 'TrillionniumFoundation/NBO' or len(manifest['artifacts']) != 19:
        raise AssertionError('Unexpected evidence family')
    checked = {}
    restored = []
    with tempfile.TemporaryDirectory(prefix='nbo-r14-archives-') as temporary:
        for artifact in manifest['artifacts']:
            expected = artifact['files']
            already = all((ROOT / p).is_file() and digest(ROOT / p) == h for p, h in expected.items())
            if not already:
                if verify_only:
                    raise AssertionError('An executed evidence file is absent or altered: ' + artifact['name'])
                archive_path = Path(temporary) / (str(artifact['artifact_id']) + '.zip')
                download(artifact, manifest['repository'], archive_path)
                found = set()
                with zipfile.ZipFile(archive_path) as archive:
                    for member in archive.infolist():
                        if member.is_dir():
                            continue
                        relative = PurePosixPath(member.filename)
                        if relative.is_absolute() or '..' in relative.parts:
                            raise AssertionError('Unexpected archive path')
                        name = str(PurePosixPath(artifact['destination']) / relative)
                        if name not in expected or name in found:
                            raise AssertionError('Unexpected or duplicated archive member: ' + name)
                        target = ROOT / name
                        if not target.resolve().is_relative_to(ROOT.resolve()):
                            raise AssertionError('Archive path escaped repository')
                        data = archive.read(member)
                        if hashlib.sha256(data).hexdigest() != expected[name]:
                            raise AssertionError('Archive member identity mismatch: ' + name)
                        if target.exists() and digest(target) != expected[name]:
                            raise AssertionError('Refusing to overwrite a different existing file: ' + name)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(data)
                        found.add(name)
                if found != set(expected):
                    raise AssertionError('Archive member list is incomplete')
                archive_path.unlink()
            for name, sha in expected.items():
                if name in checked and checked[name] != sha:
                    raise AssertionError('Conflicting shared artifact member: ' + name)
                if digest(ROOT / name) != sha:
                    raise AssertionError('Restored evidence mismatch: ' + name)
                checked[name] = sha
            restored.append({k: artifact[k] for k in ['artifact_id', 'name', 'run_id', 'source_commit', 'archive_sha256']})
            print('Verified', artifact['name'], len(expected), 'files', flush=True)
    result = {
        'artifacts': restored,
        'unique_files': len(checked),
        'all_members_identical': True,
        'restore_manifest_sha256': digest(R / 'ARTIFACT_RESTORE_MANIFEST.json'),
        'generating_commits': sorted({a['source_commit'] for a in restored}),
        'scope': 'Exact retained execution artifacts; no new training and no relabelled generating source.',
    }
    (R / 'results').mkdir(exist_ok=True)
    (R / 'results/ARTIFACT_RESTORATION.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    restore(args.verify_only)
