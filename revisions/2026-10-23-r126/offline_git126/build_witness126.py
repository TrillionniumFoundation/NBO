#!/usr/bin/env python3
"""Package the exact F126 identity objects needed by the frozen finite-fit gate.
Post-execution transport work only; no fitting, economic queries or ref updates.
"""
from pathlib import Path
import hashlib,json,subprocess,datetime
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
F='769e3eb3ac08beaa7bb6778c1676f15e1f8d6d2b'
OUT=ROOT/'offline_git126'
def git(*args,input=None):
    return subprocess.run(['git','-C',str(REPO),*args],input=input,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
def oid(expr):return git('rev-parse',expr).decode().strip()
gatepath=ROOT/'results126/independent-fit-attempt01/SOURCE_READBACK126.json'
gate=json.loads(gatepath.read_text());assert gate['source_commit']==F
files=gate['verified_files'];assert len(files)==184
objects={F:'commit'}
root_tree=oid(F+'^{tree}');objects[root_tree]='tree'
records=[]
for row in files:
    path=Path(row['path']); assert not path.is_absolute() and '..' not in path.parts
    raw=(REPO/path).read_bytes();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
    blob=oid(F+':'+path.as_posix());objects[blob]='blob'
    saved=git('cat-file','blob',blob);assert raw==saved
    for depth in range(1,len(path.parts)):
        tree=oid(F+':'+Path(*path.parts[:depth]).as_posix());objects[tree]='tree'
    records.append(dict(row,git_blob=blob))
order=[F]+sorted(k for k,t in objects.items() if t=='tree')+sorted(k for k,t in objects.items() if t=='blob')
pack=OUT/'F126_GATE_OBJECTS.pack'
with pack.open('wb') as dest:
    subprocess.run(['git','-C',str(REPO),'pack-objects','--stdout','--no-reuse-delta','--no-reuse-object'],input=('\n'.join(order)+'\n').encode(),stdout=dest,stderr=subprocess.PIPE,check=True)
metadata=[]
for k in order:
    typ=objects[k];raw=git('cat-file',typ,k)
    assert hashlib.sha1((typ+' '+str(len(raw))+'\0').encode()+raw).hexdigest()==k
    metadata.append({'oid':k,'type':typ,'bytes':len(raw),'payload_sha256':hashlib.sha256(raw).hexdigest()})
manifest={'schema':'r126-minimal-offline-git-path-witness-v1','source_commit':F,'source_root_tree':root_tree,
 'purpose':'Exact offline git-show identity for the 184 immutable files required by the frozen R126 independent historical-data fitting audit.',
 'scope':'Minimal commit/path-tree/blob witness, not a full clone or complete commit-ancestor/object graph. Unrelated tree entries and commit ancestors are intentionally absent; a full git fsck connectivity claim is not made.',
 'source_gate_receipt':'results126/independent-fit-attempt01/SOURCE_READBACK126.json','source_gate_receipt_sha256':hashlib.sha256(gatepath.read_bytes()).hexdigest(),
 'gate_files':records,'objects':metadata,'object_count':len(metadata),'gate_file_count':len(records),
 'pack':{'path':pack.name,'bytes':pack.stat().st_size,'sha256':hashlib.sha256(pack.read_bytes()).hexdigest()},
 'pack_self_contained':True,'economic_evaluations':0,'fits':0,
 'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(OUT/'WITNESS_MANIFEST126.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
print(json.dumps({'gate_files':len(records),'objects':len(metadata),'types':{t:sum(x==t for x in objects.values()) for t in ('commit','tree','blob')},'pack_bytes':pack.stat().st_size,'pack_sha256':manifest['pack']['sha256']}))
