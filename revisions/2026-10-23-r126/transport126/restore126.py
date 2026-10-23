#!/usr/bin/env python3
"""Restore byte-fragment transport; no scientific calculation or overwriting.
Data is the default. --archive additionally restores the separately indexed
release container. Existing canonical files are verified without reading parts.
"""
from pathlib import Path,PurePosixPath
import argparse,datetime,hashlib,json,os,sys,tempfile,time,traceback
ROOT=Path(__file__).resolve().parents[1]
LIMIT=8*1024*1024
BLOCK=1024*1024

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def identity(path):
    path=Path(path)
    if path.is_symlink() or not path.is_file():raise ValueError('Not a regular canonical file: '+str(path))
    size=path.stat().st_size;sha=hashlib.sha256();blob=hashlib.sha1(b'blob '+str(size).encode()+b'\0');n=0
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(BLOCK),b''):
            n+=len(chunk);sha.update(chunk);blob.update(chunk)
    if n!=size:raise ValueError('File size changed while reading: '+str(path))
    return {'bytes':n,'sha256':sha.hexdigest(),'git_blob':blob.hexdigest()}

def safe_path(root,relative):
    p=PurePosixPath(relative)
    if not relative or p.is_absolute() or '..' in p.parts or '.'==relative or '\\' in relative:raise ValueError('Unsafe relative transport path: '+repr(relative))
    result=root.joinpath(*p.parts)
    if root.resolve() not in result.resolve().parents:raise ValueError('Transport path escapes its root: '+relative)
    return result

def same(actual,expected):return all(actual[k]==expected[k] for k in ('bytes','sha256','git_blob'))
def require_identity(path,expected):
    actual=identity(path)
    if not same(actual,expected):raise ValueError('Byte identity mismatch; existing file is not overwritten: '+str(path))
    return actual

def write_json_new(path,obj):
    path=Path(path)
    with path.open('x',encoding='utf-8') as out:json.dump(obj,out,indent=2,sort_keys=True);out.write('\n')

def validate_record(row,kind):
    if type(row['bytes']) is not int or row['bytes']<=0:raise ValueError('Canonical byte count must be positive')
    offset=0
    prefix='transport126/parts/data/' if kind=='data' else 'release126/parts/'
    for index,part in enumerate(row['parts'],1):
        if part['index']!=index or part['offset']!=offset:raise ValueError('Noncontiguous or unordered fragment index')
        if type(part['bytes']) is not int or not 0<part['bytes']<=LIMIT:raise ValueError('Fragment exceeds the declared transport limit')
        if not part['path'].startswith(prefix):raise ValueError('Fragment outside the declared transport namespace')
        offset+=part['bytes']
        for key,length in (('sha256',64),('git_blob',40)):
            if len(part[key])!=length or any(c not in '0123456789abcdef' for c in part[key]):raise ValueError('Invalid fragment digest')
    if offset!=row['bytes']:raise ValueError('Fragment lengths do not cover the canonical file')
    for key,length in (('sha256',64),('git_blob',40)):
        if len(row[key])!=length or any(c not in '0123456789abcdef' for c in row[key]):raise ValueError('Invalid canonical digest')

def restore_file(source_root,destination_root,row,kind):
    validate_record(row,kind)
    final=safe_path(destination_root,row['path'])
    if final.exists() or final.is_symlink():
        verified=require_identity(final,row)
        return dict(path=row['path'],status='verified_existing',parts_read=0,**verified)
    final.parent.mkdir(parents=True,exist_ok=True)
    fd,tempname=tempfile.mkstemp(prefix='.restore126-',dir=final.parent)
    temp=Path(tempname);parts_checked=[]
    try:
        fullsha=hashlib.sha256();fullblob=hashlib.sha1(b'blob '+str(row['bytes']).encode()+b'\0');total=0
        with os.fdopen(fd,'wb') as out:
            for part in row['parts']:
                path=safe_path(source_root,part['path'])
                if path.is_symlink() or not path.is_file():raise ValueError('Missing regular fragment: '+str(path))
                psha=hashlib.sha256();pblob=hashlib.sha1(b'blob '+str(part['bytes']).encode()+b'\0');n=0
                with path.open('rb') as inp:
                    for chunk in iter(lambda:inp.read(BLOCK),b''):
                        n+=len(chunk)
                        if n>part['bytes']:raise ValueError('Fragment longer than indexed bytes: '+part['path'])
                        psha.update(chunk);pblob.update(chunk);fullsha.update(chunk);fullblob.update(chunk);out.write(chunk);total+=len(chunk)
                got={'bytes':n,'sha256':psha.hexdigest(),'git_blob':pblob.hexdigest()}
                if not same(got,part):raise ValueError('Fragment byte identity mismatch: '+part['path'])
                parts_checked.append(dict(path=part['path'],index=part['index'],**got))
            out.flush();os.fsync(out.fileno())
        assembled={'bytes':total,'sha256':fullsha.hexdigest(),'git_blob':fullblob.hexdigest()}
        if not same(assembled,row):raise ValueError('Reassembled canonical identity mismatch')
        require_identity(temp,row)
        os.chmod(temp,0o644)
        try:
            # Linking in the same directory atomically creates an absent name.
            # Unlike replace/rename, it cannot overwrite a racing existing file.
            os.link(temp,final,follow_symlinks=False)
            status='restored'
        except FileExistsError:
            require_identity(final,row);status='verified_concurrent_existing'
        require_identity(final,row)
        return dict(path=row['path'],status=status,parts_read=len(parts_checked),parts_verified=parts_checked,**assembled)
    finally:
        # Only this invocation's private assembly file is removed.
        if temp.exists():temp.unlink()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data',action='store_true',help='Explicitly select the default data restoration')
    ap.add_argument('--archive',action='store_true',help='Additionally require and restore the release-container transport index')
    ap.add_argument('--destination-root',type=Path,default=ROOT,help='Optional fresh destination layout; indexes/parts remain relative to this script')
    ap.add_argument('--output',required=True,type=Path,help='New attempt receipt directory')
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False);tick=time.perf_counter()
    destination=a.destination_root.resolve();destination.mkdir(parents=True,exist_ok=True)
    write_json_new(a.output/'START126.json',{'argv':sys.argv,'started_utc':utc(),'source_root':str(ROOT),'destination_root':str(destination),'economic_evaluations':0,'scientific_calculations':0,'archive_requested':a.archive})
    result={'status':'running','files':[],'indexes':[],'economic_evaluations':0,'scientific_calculations':0}
    code=0
    try:
        indexes=[('data',ROOT/'DATA_TRANSPORT126.json')]
        if a.archive:indexes.append(('archive',ROOT/'release126/ARCHIVE_TRANSPORT126.json'))
        for kind,indexpath in indexes:
            index=json.loads(indexpath.read_text())
            if index['schema']!='nbo-r126-immutable-byte-transport-v1' or index['kind']!=kind or index['max_part_bytes']!=LIMIT:raise ValueError('Unsupported transport schema or part limit')
            if not index['files']:raise ValueError('Empty transport index')
            result['indexes'].append({'path':indexpath.relative_to(ROOT).as_posix(),**identity(indexpath)})
            seen=set()
            for row in index['files']:
                if row['path'] in seen:raise ValueError('Duplicate canonical transport path')
                seen.add(row['path']);result['files'].append(restore_file(ROOT,destination,row,kind))
        result['status']='passed'
    except Exception as exc:
        code=1;result.update(status='failed',error_type=type(exc).__name__,error=str(exc),traceback=traceback.format_exc())
    result.update(exit_code=code,seconds=time.perf_counter()-tick,completed_utc=utc(),source_root=str(ROOT),destination_root=str(destination))
    write_json_new(a.output/'EXECUTION126.json',result);print(json.dumps(result,sort_keys=True));return code
if __name__=='__main__':sys.exit(main())
