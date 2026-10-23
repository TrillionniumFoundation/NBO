#!/usr/bin/env python3
"""Create hash-bound <=8 MiB transport parts; immutable canonical bytes stay intact.
Default makes data parts. --archive makes only the final release-container parts.
"""
from pathlib import Path
import argparse,hashlib,json,os,sys,tempfile,time,traceback
from restore126 import ROOT,LIMIT,identity,require_identity,same,utc,write_json_new

def publish_part(path,raw,expected):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() or path.is_symlink():require_identity(path,expected);return 'verified_existing'
    fd,name=tempfile.mkstemp(prefix='.part126-',dir=path.parent);temp=Path(name)
    try:
        with os.fdopen(fd,'wb') as out:out.write(raw);out.flush();os.fsync(out.fileno())
        require_identity(temp,expected);os.chmod(temp,0o644)
        try:os.link(temp,path,follow_symlinks=False);state='created'
        except FileExistsError:require_identity(path,expected);state='verified_concurrent_existing'
        return state
    finally:
        if temp.exists():temp.unlink()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--archive',action='store_true')
    ap.add_argument('--output',required=True,type=Path)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False);tick=time.perf_counter()
    kind='archive' if a.archive else 'data'
    canonical='release126/NBO_R126_REFEREE_READY.tar.gz' if a.archive else 'results126c/primary01/records126c.jsonl.gz'
    partdir=ROOT/('release126/parts' if a.archive else 'transport126/parts/data')
    indexpath=ROOT/('release126/ARCHIVE_TRANSPORT126.json' if a.archive else 'DATA_TRANSPORT126.json')
    write_json_new(a.output/'START126.json',{'argv':sys.argv,'started_utc':utc(),'kind':kind,'canonical':canonical,'max_part_bytes':LIMIT,'economic_evaluations':0,'scientific_calculations':0})
    result={'status':'running','kind':kind,'canonical':canonical,'parts':[],'economic_evaluations':0,'scientific_calculations':0};code=0
    try:
        source=ROOT/canonical;original=identity(source);parts=[];offset=0
        with source.open('rb') as stream:
            for i,raw in enumerate(iter(lambda:stream.read(LIMIT),b''),1):
                target=partdir/(source.name+f'.part-{i:05d}')
                rec={'index':i,'offset':offset,'path':target.relative_to(ROOT).as_posix(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'git_blob':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()}
                state=publish_part(target,raw,rec);parts.append(rec);result['parts'].append(dict(rec,status=state));offset+=len(raw)
        require_identity(source,original)
        if offset!=original['bytes']:raise ValueError('Source size changed while fragmenting')
        # The ordered parts are independently hashed as the full canonical blob.
        fullsha=hashlib.sha256();fullblob=hashlib.sha1(b'blob '+str(offset).encode()+b'\0')
        for part in parts:
            with (ROOT/part['path']).open('rb') as stream:
                for chunk in iter(lambda:stream.read(1024*1024),b''):fullsha.update(chunk);fullblob.update(chunk)
        if fullsha.hexdigest()!=original['sha256'] or fullblob.hexdigest()!=original['git_blob']:raise ValueError('Ordered transport parts do not equal canonical source')
        index={'schema':'nbo-r126-immutable-byte-transport-v1','kind':kind,'max_part_bytes':LIMIT,'files':[dict(path=canonical,parts=parts,**original)],'scope':'Byte transport only; canonical scientific bytes are unchanged. Fragmentation is not a new execution, model, sample, timing or scientific result.'}
        if indexpath.exists():
            prior=json.loads(indexpath.read_text());comparison=dict(prior);comparison.pop('created_utc',None)
            if comparison!=index:raise ValueError('An unequal transport index already exists; preserve it rather than overwrite')
            index_state='verified_existing'
        else:
            index['created_utc']=utc();write_json_new(indexpath,index);index_state='created'
        result.update(status='passed',canonical_identity=original,index={'path':indexpath.relative_to(ROOT).as_posix(),'status':index_state,**identity(indexpath)},canonical_unchanged=True)
    except Exception as exc:
        code=1;result.update(status='failed',error_type=type(exc).__name__,error=str(exc),traceback=traceback.format_exc())
    result.update(exit_code=code,seconds=time.perf_counter()-tick,completed_utc=utc())
    write_json_new(a.output/'EXECUTION126.json',result);print(json.dumps(result,sort_keys=True));return code
if __name__=='__main__':sys.exit(main())
