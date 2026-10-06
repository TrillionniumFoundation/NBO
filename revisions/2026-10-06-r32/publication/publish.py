"""Publish the successful R32 build to a new, non-overwriting revision branch."""
from __future__ import annotations
import base64
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import urllib.request

REPO = 'TrillionniumFoundation/NBO'
SOURCE = os.environ['NBO_SOURCE_SHA']
ROOT = Path(os.environ['NBO_WORKSPACE']).resolve()
REL = 'revisions/2026-10-06-r32'
R = ROOT/REL
BRANCH = 'revision/econometrica-nbo-r32-referee-2026-10-06'


def api(path, data=None):
    raw = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request('https://api.github.com/repos/'+REPO+'/'+path,
        data=raw, headers={'Authorization': 'Bearer '+os.environ['GITHUB_TOKEN'],
        'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json',
        'User-Agent': 'NBO-R32-publication'}, method='GET' if data is None else 'POST')
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.load(response)


def blob(path):
    data = path.read_bytes()
    if len(data) >= 95_000_000:
        raise RuntimeError('Refusing oversized Git blob: '+str(path))
    ans = api('git/blobs', {'content': base64.b64encode(data).decode(), 'encoding': 'base64'})
    return {'path': str(path.relative_to(ROOT)), 'mode': '100644', 'type': 'blob', 'sha': ans['sha']}


if __name__ == '__main__':
    audit = json.loads((R/'audit/RELEASE_AUDIT.json').read_text())
    if audit['publication_source_commit'] != SOURCE or audit['tests_passed'] < 38:
        raise RuntimeError('Successful source-bound test audit required')
    if any(d['undefined_references'] or d['multiply_defined_labels'] for d in audit['compilation']):
        raise RuntimeError('Publication cross-reference checks failed')
    files = []
    for p in R.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts:
            continue
        if p.suffix in ('.aux', '.bbl', '.blg', '.out', '.toc'):
            continue
        files.append(p)
    # Only R32 paths are published; inherited files and workflows are not replaced.
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        entries = list(executor.map(blob, sorted(files)))
    parent = api('git/commits/'+SOURCE)
    tree = api('git/trees', {'base_tree': parent['tree']['sha'], 'tree': entries})
    commit = api('git/commits', {'message': 'R32: publish native integrated manuscript, full response, exact tests and unchanged recursive-policy replay',
             'tree': tree['sha'], 'parents': [SOURCE]})
    # Create only. A pre-existing branch is never silently overwritten or forced.
    ref = api('git/refs', {'ref': 'refs/heads/'+BRANCH, 'sha': commit['sha']})
    result = {'branch': BRANCH, 'commit': commit['sha'], 'tree': tree['sha'],
              'source_commit': SOURCE, 'published_files': len(files)}
    print(json.dumps(result, indent=2), flush=True)
    (ROOT/'REMOTE_PUBLICATION.json').write_text(json.dumps(result, indent=2)+'\n')
