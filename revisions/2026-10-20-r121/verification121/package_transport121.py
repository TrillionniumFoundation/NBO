"""Deterministic byte transport only: no scientific evaluation or selection."""
from pathlib import Path
import argparse, datetime, hashlib, json, os, zipfile

PREFIX='revisions/2026-10-20-r121'

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def main():
 p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,required=True)
 p.add_argument('--bundle-id',required=True);p.add_argument('--archive',type=Path,required=True)
 p.add_argument('--include',action='append',required=True);a=p.parse_args()
 repo=a.repository.resolve();native=repo/PREFIX
 if not a.bundle_id or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in a.bundle_id):raise ValueError('Safe bundle id required')
 dest=native/'transport121/bundles'/a.bundle_id;dest.mkdir(parents=True,exist_ok=False)
 selected={}
 for name in a.include:
  root=(native/name).resolve();root.relative_to(native)
  if not root.exists():raise FileNotFoundError(root)
  for x in ([root] if root.is_file() else sorted(root.rglob('*'))):
   if x.is_symlink():raise ValueError('No symlink transport')
   if x.is_file():selected[x.relative_to(repo).as_posix()]=x
 files=[];a.archive.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(a.archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True)as z:
  for name,x in sorted(selected.items()):
   raw=x.read_bytes();blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
   info=zipfile.ZipInfo(name,(2026,10,20,0,0,0));info.external_attr=(0o100644<<16);info.create_system=3
   info.compress_type=zipfile.ZIP_STORED if x.suffix in('.gz','.png','.pdf','.zip')else zipfile.ZIP_DEFLATED
   z.writestr(info,raw,compress_type=info.compress_type,compresslevel=6)
   files.append(dict(path=name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),git_blob=blob))
 parts=[]
 with a.archive.open('rb')as f:
  i=0
  while data:=f.read(8*1024*1024):
   name=f'payload.zip.part{i:04d}';x=dest/name
   with x.open('xb')as out:out.write(data)
   parts.append(dict(name=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
   i+=1
 request=dict(kind='nbo-r121-byte-transport-v1',bundle_id=a.bundle_id,revision_prefix=PREFIX,
  archive=dict(bytes=a.archive.stat().st_size,sha256=sha(a.archive)),parts=parts,files=files)
 with (dest/'REQUEST121.json').open('x')as f:json.dump(request,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps({'bundle_id':a.bundle_id,'request':str(dest/'REQUEST121.json'),'archive_bytes':a.archive.stat().st_size,'native_files':len(files),'native_bytes':sum(x['bytes']for x in files),'parts':len(parts),'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},sort_keys=True))

if __name__=='__main__':main()
