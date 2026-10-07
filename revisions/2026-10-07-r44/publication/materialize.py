"""Materialize the frozen R44 release; never alter inherited scientific files."""
from pathlib import Path, PurePosixPath
import base64, hashlib, io, json, lzma, os, subprocess, tempfile, zipfile

R = Path(__file__).resolve().parents[1]
REPO = R.parents[1]
sha = lambda b: hashlib.sha256(b).hexdigest()
XZ_SHA = 'a2b048eefbace81b6404f610cddf0084d844f932f75b77fa9e172e60d7e232b0'
JSON_SHA = 'e041db1444ca4b48cb9becc172c31ccd642d673c4803db435e44bb4b4ea2c3e6'
ARTIFACTS = {
    'R42': (11465997076, '540f80f65c27b9998b2a54375f79413f1a1f3d82bd04e50b810dba6dfed607cc'),
    'R41': (11460768113, 'b5dc1a9fdcedc3279dbd7e9c190425f7e856f1fbcd67083e7452c2febc06aac6'),
}

def safe_relative(name):
    p = PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or not p.parts:
        raise ValueError('Unsafe relative path: '+name)
    return Path(*p.parts)

def artifact(key):
    ident, expected = ARTIFACTS[key]
    repo = os.environ['GITHUB_REPOSITORY']
    with tempfile.TemporaryFile() as f:
        subprocess.run(['gh', 'api', f'/repos/{repo}/actions/artifacts/{ident}/zip'], stdout=f, check=True)
        f.seek(0); data = f.read()
    if sha(data) != expected:
        raise ValueError(key+' artifact digest mismatch')
    return zipfile.ZipFile(io.BytesIO(data))

def main():
    encoded = ''.join((R/'publication'/f'part-{i:02d}.b64').read_text() for i in range(8))
    if len(encoded) != 70492:
        raise ValueError('Incomplete source capsule')
    packed = base64.b64decode(encoded, validate=True)
    if sha(packed) != XZ_SHA:
        raise ValueError('Source capsule digest mismatch')
    raw = lzma.decompress(packed)
    if sha(raw) != JSON_SHA:
        raise ValueError('Decoded source digest mismatch')
    files = json.loads(raw)
    if len(files) != 80:
        raise ValueError('Unexpected source catalogue')
    for name, text in files.items():
        p = R/safe_relative(name)
        if p.exists() and p.read_bytes() != text.encode():
            raise FileExistsError('Refusing to replace different source: '+str(p))
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(text.encode())
    protocol = R/'STUDY_PROTOCOL.md'
    blob = hashlib.sha1(b'blob '+str(protocol.stat().st_size).encode()+b'\0'+protocol.read_bytes()).hexdigest()
    if blob != 'd06948b252773597fd8cd7caccb3ad4308c76e38':
        raise ValueError('Pre-execution protocol changed')
    z = artifact('R42')
    dest = R/'evidence/2026-10-07-r42'
    members = {}
    for info in z.infolist():
        rel = safe_relative(info.filename)
        if info.is_dir():
            (dest/rel).mkdir(parents=True, exist_ok=True); continue
        data = z.read(info)
        p = dest/rel
        if p.exists() and p.read_bytes() != data:
            raise FileExistsError('Refusing to replace different evidence: '+str(p))
        p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data)
        members[info.filename] = sha(data)
    # The imported R42 code expects its historical sibling at this path.
    link = R/'evidence/2026-10-07-r41'
    if not link.exists():
        link.symlink_to('../../2026-10-07-r41', target_is_directory=True)
    if link.resolve() != (R.parent/'2026-10-07-r41').resolve():
        raise ValueError('Wrong historical dependency target')
    old = artifact('R41')
    preserved = {}
    for name in ('ECTA.tex','supp.tex','applications.tex','build/ECTA.pdf','build/supp.pdf','build/applications.pdf'):
        rel = 'revisions/2026-10-07-r41/'+name
        data = old.read(rel)
        if (REPO/rel).read_bytes() != data:
            raise ValueError('Inherited manuscript differs from pinned publication: '+rel)
        preserved[rel] = sha(data)
    report = {'source_xz_sha256':XZ_SHA, 'source_json_sha256':JSON_SHA,
              'source_files':{n:sha(t.encode()) for n,t in files.items()},
              'source_protocol_commit':'32505809223124c6cd4968af1b216d88c25a3b41',
              'artifacts':{k:{'id':v[0],'sha256':v[1]} for k,v in ARTIFACTS.items()},
              'materialized_R42_files':members, 'unchanged_R41_documents':preserved,
              'publication_source_commit':os.environ.get('GITHUB_SHA'),
              'publication_run_id':os.environ.get('GITHUB_RUN_ID'),
              'new_experiment_execution':'Frozen results executed before this publication build; their original clocks are preserved.'}
    (R/'audit/MATERIALIZATION.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    root_readme = REPO/'README.md'
    retained = R/'audit/ROOT_README_BEFORE_R44.md'
    if not retained.exists():
        retained.write_bytes(root_readme.read_bytes())
    root_readme.write_text('''# Neural Bellman Operators — R44

Revision of the original NBO paper in response to the R42 advisory referee report. The title, author, controlled-economy framework, full theory and applications are preserved.

## Current referee package

- [Main article (PDF)](revisions/2026-10-07-r44/build/ECTA.pdf) and [LaTeX source](revisions/2026-10-07-r44/ECTA.tex).
- [Technical supplement (PDF)](revisions/2026-10-07-r44/build/supp.pdf) and [source](revisions/2026-10-07-r44/supp.tex).
- [Point-by-point response](revisions/2026-10-07-r44/response.md) and [response PDF](revisions/2026-10-07-r44/build/response.pdf).
- [Release audit](revisions/2026-10-07-r44/audit/RELEASE_AUDIT.json), [preservation map](revisions/2026-10-07-r44/audit/PRESERVATION.json), [full evidence](revisions/2026-10-07-r44/evidence/2026-10-07-r42), and [build/reproduction instructions](revisions/2026-10-07-r44/README.md).

Seven previously unresolved tighter targets are now certified without changing the original network weights or deployed actors. These are separately reported residual-refinement diagnostics, not a rewrite of the original R42 capped-service failures. All 24 direct neural-minus-ridge policy-cost intervals contain zero; they do not establish a sign or equivalence. Original comparator and precision findings are retained, including adverse outcomes. No unexecuted dimension frontier or stable speed advantage is claimed.

The [complete historical article](revisions/2026-10-07-r41/build/ECTA.pdf), [historical technical supplement](revisions/2026-10-07-r41/build/supp.pdf), and [full economic applications](revisions/2026-10-07-r41/build/applications.pdf) remain unchanged. Earlier revisions and reviews are preserved; the [previous root README](revisions/2026-10-07-r44/audit/ROOT_README_BEFORE_R44.md) remains available.

Build from repository root: `python revisions/2026-10-07-r44/code/build.py`. This audits the frozen evidence and compiles the manuscript; it does not retrain or rewrite diagnostic clocks.
''')
    print('Materialized', len(files), 'R44 files and', len(members), 'R42 evidence files; inherited manuscript bytes unchanged.')

if __name__ == '__main__':
    main()
