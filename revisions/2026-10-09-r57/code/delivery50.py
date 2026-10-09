"""Bind a prepared R50 payload without claiming an unperformed remote push."""
from pathlib import Path
import argparse, datetime, hashlib, json
R=Path(__file__).resolve().parents[1]
EXCLUDE={'audit/DELIVERY_FILES_SHA256.json','audit/FINAL_DELIVERY.json'}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['local-review-package','prepared-for-push'],default='local-review-package');args=ap.parse_args()
 files={}
 for p in sorted(R.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts or p.suffix=='.pyc':continue
  name=str(p.relative_to(R))
  if name not in EXCLUDE:files[name]=sha(p)
 manifest=R/'audit/DELIVERY_FILES_SHA256.json';manifest.write_text(json.dumps(files,indent=2,sort_keys=True)+'\n')
 release=json.loads((R/'audit/RELEASE_AUDIT.json').read_text())
 record={'status':args.mode,'prepared_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'remote_push_performed_during_preparation':False,'remote_commit_created_during_preparation':None,'intended_repository':'TrillionniumFoundation/NBO','intended_source_branch':'revision/econometrica-nbo-r50-cost-directed-source-2026-10-08','intended_review_branch':'revision/econometrica-nbo-r50-cost-directed-review-ready-2026-10-08','base_review_commit':'2822f50100c7a53ec5fe07d39e9b37d487ab0547','manifest_sha256':sha(manifest),'bound_files':len(files),'tests_passed':release['total_tests'],'pdfs':release['compilation'],'clean_archive_rebuild':'audit/CLEAN_ARCHIVE_REBUILD.json','scope':'Complete local manuscript/evidence package. A successful offline build is not a GitHub push or referee approval. An executed publisher emits an independent PUSH_RECEIPT.json after checking both remote refs.'}
 (R/'audit/FINAL_DELIVERY.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n');print(json.dumps(record,indent=2))
if __name__=='__main__':main()
