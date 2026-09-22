"""Hash canonical R9 source/evidence and compiled review PDFs."""
import hashlib,json,os,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-22-r9'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files={}
for p in sorted(REV.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or 'build_logs' in p.parts:continue
 if p.name in {'source_manifest.json','validation_report.json','certificate_recheck.json'}:continue
 files[str(p.relative_to(ROOT))]=sha(p)
for n in ['ECTA_R9.tex','SUPP_R9.tex','R9_REVIEW.md','REVISION_INDEX.md','econsocart.cls']:
 files[n]=sha(ROOT/n)
try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
except Exception:commit=None
out={'source_commit_before_artifact_commit':commit,'workflow_trigger_commit':os.getenv('GITHUB_SHA'),
 'review_base':'9749c3cf28f9438315b8f504a358bbe307ea89a5','frozen_external_source':'46aef70a24f74cf57503018a7e7f21cb46af08e3',
 'source_and_evidence_sha256':files,'compiled_pdf_sha256':{n:sha(ROOT/n) for n in ['ECTA_R9.pdf','SUPP_R9.pdf']},
 'derived_validation_sha256':{n:sha(REV/n) for n in ['validation_report.json','certificate_recheck.json'] if (REV/n).exists()},
 'scope':'Manifest excludes itself, cache files, and mutable build logs; full inherited preservation has its own manifest.'}
(REV/'source_manifest.json').write_text(json.dumps(out,indent=2)+'\n')
print('Hashed',len(files),'source/evidence files and two PDFs')
