"""Restore original evidence by artifact identity, never refit or replace clocks."""
from pathlib import Path
import hashlib, io, json, os, subprocess, urllib.parse, urllib.request, zipfile
ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = 11359269970
EXPECTED = '9fa53a7eefc33ddb7270e490de910d135e3d89940dfd7064f2254a3c9c9c211e'
PREFIX = 'revisions/2026-10-05-r25/results/'
BASE = 'e7cfba39ea548b295305ab39040d0ba84d791c74'
class ScopedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if urllib.parse.urlsplit(newurl).hostname != 'api.github.com':
            new.remove_header('Authorization')
        return new

def recover():
    archive = os.environ.get('NBO_R25_ARCHIVE')
    if archive:
        data = Path(archive).read_bytes()
    else:
        url = f'https://api.github.com/repos/TrillionniumFoundation/NBO/actions/artifacts/{ARTIFACT}/zip'
        req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json'})
        data = urllib.request.build_opener(ScopedRedirect()).open(req, timeout=120).read()
    assert hashlib.sha256(data).hexdigest() == EXPECTED, 'Artifact identity mismatch'
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for item in z.infolist():
            name = item.filename
            assert name.startswith(PREFIX) and '..' not in Path(name).parts, name
            if item.is_dir():
                continue
            target = ROOT / name
            raw = z.read(item)
            if target.exists():
                assert target.read_bytes() == raw, f'Refusing to overwrite different evidence: {name}'
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
    r = ROOT / PREFIX
    identity = json.loads((r / 'EXECUTION_IDENTITY.json').read_text())
    assert identity['frozen_source_commit'] == '9bf608d5154dfb61ff0ab209c2b66d1f8dbcc148'
    assert str(identity['run_id']) == '37339128420'
    if (ROOT / '.git').exists():
        for name in ('SUMMARY.json', 'services.jsonl'):
            p = ROOT / 'revisions/2026-10-05-r23/results/primary' / name
            raw = subprocess.check_output(['git', 'show', BASE + ':' + str(p.relative_to(ROOT))], cwd=ROOT)
            if p.exists():
                assert p.read_bytes() == raw, p
            else:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(raw)
    out = ROOT / 'revisions/2026-10-06-r26/results'
    out.mkdir(parents=True, exist_ok=True)
    manifest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in r.rglob('*') if p.is_file()}
    record = {'artifact_id': ARTIFACT, 'artifact_sha256': EXPECTED, 'execution_run': 37339128420, 'execution_identity': identity, 'recovered_files_sha256': manifest, 'scope': 'Original successful scientific execution recovered from its surviving artifact. The original Git push failed. No fitting rerun or primary clock replacement.'}
    (out / 'RECOVERY.json').write_text(json.dumps(record, indent=2) + '\n')
    print('Recovered and hashed', len(manifest), 'original evidence files')
if __name__ == '__main__':
    recover()
