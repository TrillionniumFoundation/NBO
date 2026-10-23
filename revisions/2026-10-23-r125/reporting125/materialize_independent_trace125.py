"""Lossless transport reconstruction; never an economic evaluation."""
from pathlib import Path
import hashlib,json

def ensure_trace(root):
 root=Path(root);m=json.loads((root/'POSTFREEZE_AUDIT_FREEZE125.json').read_text());meta=m['logical_independent_terminal_trace'];target=root/meta['path']
 digest=hashlib.sha256();size=0
 for rel in meta['parts']:
  p=root/rel;part_hash=hashlib.sha256()
  with p.open('rb') as f:
   while True:
    block=f.read(1024*1024)
    if not block:break
    part_hash.update(block);digest.update(block);size+=len(block)
  if part_hash.hexdigest()!=m['files'][rel]:raise ValueError('Transport part hash mismatch: '+rel)
 if size!=meta['bytes'] or digest.hexdigest()!=meta['sha256']:raise ValueError('Concatenation is not the original independent evidence byte stream')
 if not target.exists():
  with target.open('xb') as out:
   for rel in meta['parts']:
    with (root/rel).open('rb') as f:
     while True:
      block=f.read(1024*1024)
      if not block:break
      out.write(block)
 actual=hashlib.sha256()
 with target.open('rb') as f:
  while True:
   block=f.read(1024*1024)
   if not block:break
   actual.update(block)
 if target.stat().st_size!=size or actual.hexdigest()!=meta['sha256']:raise ValueError('Existing original independent evidence differs from transport identity')
 return dict(path=str(target),bytes=size,sha256=actual.hexdigest(),parts=meta['parts'],economic_evaluations=0)

if __name__=='__main__':print(json.dumps(ensure_trace(Path(__file__).resolve().parents[1]),sort_keys=True))
