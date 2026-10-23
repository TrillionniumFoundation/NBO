"""Assemble a byte-verified repository-layout author package; no science runs."""
from pathlib import Path
import datetime as dt
import gzip
import hashlib
import io
import json
import tarfile

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PREFIX = 'revisions/2026-10-23-r126'
BUILD_RECEIPT = 'provenance126/native-final/20261023T135002.071606Z/BUILD_RECEIPT126.json'
WORKFLOW = '.github/workflows/nbo-r126-author-package.yml'
EPOCH = 1792713600

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def record(p):
    raw = p.read_bytes()
    return {'bytes': len(raw), 'sha256': sha(raw),
            'git_blob': hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()}

def write(p, data):
    p.write_text(json.dumps(data, indent=2, sort_keys=True)+'\n')

def selected(p):
    if not p.is_file():
        return False
    parts = p.relative_to(ROOT).parts
    if any(x in {'__pycache__', '.git', '.pytest_cache'} for x in parts) or p.suffix == '.pyc':
        return False
    if parts[0] in {'release126', 'ci126', 'replication126', 'replication126c'}:
        return False
    if parts[:2] == ('transport126', 'parts'):
        return False
    return p.name != 'REFEREE_MANIFEST126.json'

def validated_transport():
    index_path = ROOT/'DATA_TRANSPORT126.json'
    validation_path = ROOT/'transport126/VALIDATION126.json'
    index = json.loads(index_path.read_text())
    validation = json.loads(validation_path.read_text())
    assert validation['status'] == 'passed', 'Transport validation must complete before assembly'
    checked_sources = validation['validated_source_hashes']
    assert 'DATA_TRANSPORT126.json' in checked_sources
    for rel, expected in checked_sources.items():
        assert sha((ROOT/rel).read_bytes()) == expected, 'Transport validation source changed: '+rel
    canonical = []
    for row in index['files']:
        rel = Path(row['path'])
        assert not rel.is_absolute() and '..' not in rel.parts
        path = ROOT/rel
        rec = record(path)
        for key in ('bytes', 'sha256', 'git_blob'):
            assert rec[key] == row[key], 'Canonical transport data mismatch: '+row['path']
        canonical.append(row['path'])
    return {'data_index': {'path': index_path.name, **record(index_path)},
            'validation': {'path': validation_path.relative_to(ROOT).as_posix(), **record(validation_path)},
            'canonical_files': canonical,
            'scope': 'The archive includes the original canonical scientific data, the transport index, utilities and validation receipts. Repository-only fragments under transport126/parts/ and release126/parts/ are excluded.'}

def main():
    transport = validated_transport()
    native = json.loads((ROOT/BUILD_RECEIPT).read_text())
    assert native['status'] == 'compiled_clean'
    assert not native['issues'] and not native['placeholders'] and not native['source_mutations_during_build']
    for rel, digest in {**native['source_sha256'], **native['graphic_asset_sha256']}.items():
        assert sha((ROOT/rel).read_bytes()) == digest, rel
    for row in native['pdfs']:
        assert sha((ROOT/row['path']).read_bytes()) == row['sha256'], row['path']
    boundaries = {}
    for suffix in ('126', '126C'):
        mpath=ROOT/f'SOURCE_FREEZE{suffix}.json'
        boundary=json.loads((ROOT/f'BOUNDARIES{suffix}.json').read_text())
        assert boundary['source_manifest_sha256'] == sha(mpath.read_bytes())
        m=json.loads(mpath.read_text())
        for rel, val in m['files'].items():
            assert sha((ROOT/rel).read_bytes()) == (val if isinstance(val,str) else val['sha256']), rel
        boundaries[suffix]={'source_commit':boundary['source_commit'],'manifest':mpath.name,
                            'manifest_sha256':sha(mpath.read_bytes()),'files':len(m['files']),
                            'remote_readback_before_economics':boundary['remote_source_readback_before_economics']}
    visuals={}
    for name in ('MAIN','SUPPLEMENT','DEVELOPMENT','RESPONSE'):
        path=ROOT/f'provenance126/VISUAL_{name}126.json'
        visuals[path.relative_to(ROOT).as_posix()]=record(path)
    source_pdf={'schema':'r126-current-source-pdf-binding-v1',
                'baseline_commit':'eda26b02fbfb1e02807bc0cee1c0015d62d59e56',
                'controlling_report_commit':'9723c6cd2cc8b3e071422f3e522d4a843946db63',
                'controlling_report_sha256':'479b28c8800084846336cac078877a01dbbd2bae546d179633a2734401da19b9',
                'scientific_boundaries':boundaries,
                'native_build_receipt':{'path':BUILD_RECEIPT,**record(ROOT/BUILD_RECEIPT)},
                'declared_source_sha256':native['source_sha256'],
                'declared_graphic_sha256':native['graphic_asset_sha256'],
                'actual_project_inputs':native['actual_project_inputs'],
                'pdfs':native['pdfs'],'visual_receipts':visuals,
                'scope':'Current author sources and actually compiled PDFs. Scientific execution, visual inspection, remote publication and CI have distinct receipts. The final publication commit identifies this file; no self-referential commit hash is invented.'}
    write(ROOT/'SOURCE_PDF_HASHES126.json',source_pdf)
    files={p.relative_to(ROOT).as_posix():record(p) for p in sorted(ROOT.rglob('*')) if selected(p)}
    manifest={'schema':'r126-referee-author-package-v1','files':files,
              'repository_files':{WORKFLOW:record(REPO/WORKFLOW)},
              'scientific_boundaries':boundaries,
              'publication_transport':transport,
              'excluded':['this manifest itself','release126/ archive and its separate transport/verification receipts and fragments','transport126/parts/ repository transport fragments; canonical scientific files remain included','Python bytecode caches','new CI or replication output directories'],
              'preservation':'Historical sources, scientific inputs, all saved current scientific outcomes, unsuccessful attempts, exact witnesses, native build logs, final PDFs and visual QA records are included. Historical repository objects outside this R126 delivery retain their immutable Git routes.',
              'remote_ci_status':'Not asserted by this pre-publication manifest; inspect the workflow run for the actual publication commit.'}
    write(ROOT/'REFEREE_MANIFEST126.json',manifest)
    release=ROOT/'release126';release.mkdir(exist_ok=True)
    target=release/'NBO_R126_REFEREE_READY.tar.gz'
    if target.exists():raise FileExistsError('Preserve any existing package; use a distinct attempt before regeneration')
    archive_paths=[(ROOT/rel,PREFIX+'/'+rel) for rel in sorted(files)]
    archive_paths += [(ROOT/'REFEREE_MANIFEST126.json',PREFIX+'/REFEREE_MANIFEST126.json'),(REPO/WORKFLOW,WORKFLOW)]
    with target.open('xb') as out:
        with gzip.GzipFile(fileobj=out,mode='wb',mtime=0,filename='',compresslevel=6) as gz:
            with tarfile.open(fileobj=gz,mode='w|') as tar:
                for path, name in sorted(archive_paths,key=lambda x:x[1]):
                    raw=path.read_bytes();info=tarfile.TarInfo(name)
                    info.size=len(raw);info.mtime=EPOCH;info.mode=0o644;info.uid=info.gid=0;info.uname=info.gname=''
                    tar.addfile(info,io.BytesIO(raw))
    expected={name:record(path) for path,name in archive_paths}
    seen=set()
    with tarfile.open(target,'r|gz') as tar:
        for member in tar:
            assert member.isfile() and member.name in expected and member.name not in seen
            assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
            raw=tar.extractfile(member).read(); rec=expected[member.name]
            assert len(raw)==rec['bytes'] and sha(raw)==rec['sha256'],member.name
            seen.add(member.name)
    assert seen==set(expected)
    identity={'schema':'r126-referee-archive-identity-v1','path':target.relative_to(ROOT).as_posix(),**record(target),
              'members':len(archive_paths),'repository_layout':True,
              'manifest_sha256':sha((ROOT/'REFEREE_MANIFEST126.json').read_bytes()),
              'workflow_sha256':sha((REPO/WORKFLOW).read_bytes()),
              'pdfs':native['pdfs'],
              'offline_identity_witness':'offline_git126/F126_GATE_OBJECTS.pack',
              'source_commits':[x['source_commit'] for x in boundaries.values()]}
    write(release/'ARCHIVE_IDENTITY126.json',identity)
    verification={'status':'passed','archive_sha256':identity['sha256'],'all_members_read_and_sha256_verified':len(seen),
                  'unsafe_or_duplicate_members':0,'economic_calculations':0,
                  'completed_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
    write(release/'ARCHIVE_VERIFICATION126.json',verification)
    print(json.dumps({'files':len(files),'repository_files':1,'archive_members':len(seen),'archive_bytes':identity['bytes'],
                      'archive_sha256':identity['sha256'],'archive':str(target)}))
if __name__=='__main__':main()
