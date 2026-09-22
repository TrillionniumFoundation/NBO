"""Separate source, numerical-result, PDF-build and report identities; no self-hash."""
from __future__ import annotations
import argparse,hashlib,json,os,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-22-r11'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(source,result,build=None):
 sourcefiles={}
 for p in sorted(REV.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(REV)
  if any(s in rel.parts for s in ['__pycache__','ci_results','build_logs']):continue
  if p.name in ['source_manifest.json','publication_receipt.json','validation_report.json','validation_tests.json','inherited_manifest.json']:continue
  sourcefiles[str(p.relative_to(ROOT))]=sha(p)
 for f in ['ECTA_R11.tex','SUPP_R11.tex','R11_REVIEW.md','REVISION_INDEX.md']:sourcefiles[f]=sha(ROOT/f)
 (REV/'source_manifest.json').write_text(json.dumps({'manuscript_source_commit':source,'independent_result_commit':result,'files':sourcefiles},indent=2)+'\n')
 if build:
  ext=json.loads((REV/'results/robustness_receipt.json').read_text())
  receipt={'manuscript':'Neural Bellman Operators, R11','base_commit':'d633bd60818998e53051cee6e7ad351c52a61795','review_input_commit':'251ad29668788b2a911c4ca6f9c0a226886518d6','review_input_blob':'42cee0954515e5578dc579a4ca0428bb4e399b2e','external_study':ext,'manuscript_source_commit':source,'independent_result_commit':result,'manuscript_build_commit':build,'workflow_run':os.environ.get('GITHUB_RUN_ID'),'files':{f:sha(ROOT/f) for f in ['ECTA_R11.pdf','SUPP_R11.pdf','revisions/2026-09-22-r11/source_manifest.json','revisions/2026-09-22-r11/validation_report.json','revisions/2026-09-22-r11/ci_results/status.json']},'note':'This receipt is committed after the PDF build. It intentionally does not attempt to include its own commit hash.'}
  (REV/'publication_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--result',required=True);p.add_argument('--build');a=p.parse_args();run(a.source,a.result,a.build)
