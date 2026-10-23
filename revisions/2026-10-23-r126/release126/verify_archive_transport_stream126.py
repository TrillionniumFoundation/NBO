"""Independently check archive-fragment identities by streaming; no copy or science."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,time
ROOT=Path(__file__).resolve().parents[1]

def main():
    tick=time.perf_counter()
    index_path=ROOT/'release126/ARCHIVE_TRANSPORT126.json'
    identity_path=ROOT/'release126/ARCHIVE_IDENTITY126.json'
    raw=index_path.read_bytes();index=json.loads(raw)
    archive=json.loads(identity_path.read_text())
    assert index['schema']=='nbo-r126-immutable-byte-transport-v1'
    assert index['kind']=='archive' and index['max_part_bytes']==8*2**20
    assert len(index['files'])==1
    row=index['files'][0]
    assert row['path']=='release126/NBO_R126_REFEREE_READY.tar.gz'
    assert all(row[k]==archive[k] for k in ('bytes','sha256','git_blob'))
    full_sha=hashlib.sha256();full_blob=hashlib.sha1(b'blob '+str(row['bytes']).encode()+b'\0')
    total=0;seen=set();checks=[]
    for ordinal,part in enumerate(row['parts'],1):
        assert part['index']==ordinal and part['offset']==total
        assert type(part['bytes']) is int and 0<part['bytes']<=8*2**20
        rel=Path(part['path'])
        assert not rel.is_absolute() and '..' not in rel.parts
        assert rel.parts[:2]==('release126','parts') and part['path'] not in seen
        seen.add(part['path']);path=ROOT/rel
        assert path.is_file() and not path.is_symlink()
        part_sha=hashlib.sha256();part_blob=hashlib.sha1(b'blob '+str(part['bytes']).encode()+b'\0');size=0
        with path.open('rb') as inp:
            for data in iter(lambda:inp.read(2**20),b''):
                size+=len(data);part_sha.update(data);part_blob.update(data)
                total+=len(data);full_sha.update(data);full_blob.update(data)
        got={'bytes':size,'sha256':part_sha.hexdigest(),'git_blob':part_blob.hexdigest()}
        assert all(got[k]==part[k] for k in got),part['path']
        checks.append({'index':ordinal,'path':part['path'],**got})
    combined={'bytes':total,'sha256':full_sha.hexdigest(),'git_blob':full_blob.hexdigest()}
    assert all(combined[k]==row[k] for k in combined)
    manifest_sha=hashlib.sha256((ROOT/'REFEREE_MANIFEST126.json').read_bytes()).hexdigest()
    assert archive['manifest_sha256']==manifest_sha
    report={'schema':1,'status':'passed','completed_utc':datetime.now(timezone.utc).isoformat(),
            'seconds':time.perf_counter()-tick,'kind':'independent_streaming_archive_transport_identity_check',
            'index':{'path':index_path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(raw).hexdigest()},
            'archive_identity_sha256':hashlib.sha256(identity_path.read_bytes()).hexdigest(),
            'manifest_sha256':manifest_sha,'canonical_archive':{'path':row['path'],**combined},
            'parts_checked':checks,'maximum_part_bytes':max(x['bytes'] for x in checks),
            'full_restored_copy_written':False,'canonical_archive_modified':False,
            'economic_evaluations':0,'scientific_execution':False,
            'verifier_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'scope':'All fragment byte counts, ordering, offsets, SHA256 and Git blob identities, and concatenated canonical identity verified independently without importing transport utilities. This is a streaming transport check, not a fresh economic execution or a claim that CI has run.'}
    output=ROOT/'release126/ARCHIVE_TRANSPORT_STREAM_VERIFICATION126.json'
    with output.open('x') as stream:json.dump(report,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'status':'passed','parts':len(checks),'archive':combined,'manifest_sha256':manifest_sha,'receipt':output.relative_to(ROOT).as_posix()}))
if __name__=='__main__':main()
