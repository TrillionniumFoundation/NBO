"""Verify delivered source, evidence and PDF byte identities; no economics."""
from pathlib import Path
import argparse,datetime as dt,hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();out=Path(a.output);out.mkdir(parents=True,exist_ok=False);tick=time.perf_counter()
 m=json.loads((ROOT/'REFEREE_MANIFEST126.json').read_text());wrong=[]
 for rel,rec in m['files'].items():
  path=ROOT/rel
  if not path.is_file() or sha(path)!=rec['sha256']:wrong.append(rel)
 for rel,rec in m.get('repository_files',{}).items():
  path=ROOT.parents[1]/rel
  if not path.is_file() or sha(path)!=rec['sha256']:wrong.append(rel)
 if wrong:raise ValueError('Package mismatches: '+repr(wrong))
 frozen=[]
 for suffix in ('126','126C'):
  path=ROOT/f'SOURCE_FREEZE{suffix}.json'
  assert path.is_file(), 'Missing required scientific source manifest: '+path.name
  f=json.loads(path.read_text());boundary=json.loads((ROOT/f'BOUNDARIES{suffix}.json').read_text())
  assert boundary['remote_source_readback_before_economics'] and len(boundary['source_commit'])==40 and boundary['source_manifest_sha256']==sha(path)
  for rel,entry in f['files'].items():
   want=entry if isinstance(entry,str) else entry['sha256'];assert sha(ROOT/rel)==want,rel
  frozen.append({'source_commit':boundary['source_commit'],'manifest':path.name,'files':len(f['files'])})
 archive=json.loads((ROOT/'release126/ARCHIVE_IDENTITY126.json').read_text())
 assert archive['manifest_sha256']==sha(ROOT/'REFEREE_MANIFEST126.json')
 assert sha(ROOT/archive['path'])==archive['sha256']
 data={'status':'passed','manifest_files':len(m['files']),'repository_files':len(m.get('repository_files',{})),'archive_sha256':archive['sha256'],'frozen_sources':frozen,'economic_queries':0,'seconds':time.perf_counter()-tick,'completed_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
 (out/'PACKAGE_VERIFICATION126.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data))
if __name__=='__main__':main()
