"""Deterministic byte transport for completed evidence, separate from experiments."""
from __future__ import annotations
import argparse,datetime as dt,hashlib,json,time,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directories',nargs='+',required=True);ap.add_argument('--bundle',required=True);ap.add_argument('--archive',required=True);a=ap.parse_args()
    tick=time.perf_counter();started=dt.datetime.now(dt.timezone.utc).isoformat();bundle=ROOT/a.bundle;bundle.mkdir(parents=True,exist_ok=False)
    paths=[]
    for name in a.directories:
        p=ROOT/name
        if not p.is_dir() or not p.resolve().is_relative_to((ROOT/'results122').resolve()):raise ValueError(name)
        paths.extend(q for q in p.rglob('*') if q.is_file())
    paths=sorted(set(paths));records=[]
    for p in paths:
        if p.is_symlink():raise ValueError('No symbolic evidence inputs')
        records.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)})
    archive=Path(a.archive);archive.parent.mkdir(parents=True,exist_ok=True)
    if archive.exists():raise FileExistsError(archive)
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for p,r in zip(paths,records):
            info=zipfile.ZipInfo(r['path'],date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o100644<<16);info.create_system=3
            with p.open('rb') as src,z.open(info,'w',force_zip64=True) as dst:
                for b in iter(lambda:src.read(1<<20),b''):dst.write(b)
            if p.stat().st_size!=r['bytes'] or digest(p)!=r['sha256']:raise ValueError('Evidence mutated during transport: '+str(p))
    parts=[]
    with archive.open('rb') as f:
        j=0
        for b in iter(lambda:f.read(8*1024*1024),b''):
            p=bundle/f'payload.part{j:03d}';p.write_bytes(b)
            parts.append({'path':p.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'git_blob_sha':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()});j+=1
    obj={'kind':'lossless R122 executed-evidence transport','source_commit':'2f483615c8bc0037e43ec01a16cce05c724f8c60','state_commit':'a3323b6f557315ea91b536637419ef6fd7984b61','created_utc':started,'archive_bytes':archive.stat().st_size,'archive_sha256':digest(archive),'files':records,'parts':parts,'native_file_count':len(records),'native_bytes':sum(r['bytes'] for r in records),'scope':'Byte preservation only. Exact native relative paths and SHA256 identities are restored by materialize_evidence122.py. Compression does not change any method, record, state, clock, interval or outcome.','actual_publication_work_seconds':time.perf_counter()-tick}
    (bundle/'REQUEST122.json').write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:obj[k] for k in ('archive_bytes','archive_sha256','native_file_count','native_bytes','actual_publication_work_seconds')}))
if __name__=='__main__':main()
