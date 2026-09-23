"""Check every preserved historical PDF page and seal reproducible delivery metadata."""
import hashlib,json,os,re,subprocess,sys
try:
    import fitz
except ImportError:
    subprocess.run([sys.executable,"-m","pip","install","PyMuPDF==1.26.7"],check=True)
    import fitz
from pathlib import Path
ROOT=Path.cwd();REV=ROOT/'revisions/2026-09-23-r26'
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pages(p):
    with fitz.open(p) as doc:
        return [''.join(page.get_text().split()) for page in doc]
combined=pages(ROOT/'SUPP_R26.pdf');rows=[];start=0
for doc in ('ECTA_R24','SUPP_R24'):
    source=pages(REV/'history'/f'{doc}_as_reviewed.pdf')
    positions=[i for i in range(start,len(combined)-len(source)+1) if combined[i:i+len(source)]==source]
    assert len(positions)==1,(doc,positions)
    at=positions[0]
    rows.extend({'source':doc,'source_page':j+1,'combined_page':at+j+1,'text_identical_ignoring_whitespace':True} for j in range(len(source)))
    start=at+len(source)
assert len(rows)==151
write(REV/'results/historical_pdf_audit.json',{'pages':rows,'preserved_pages':151,'all_text_identical_ignoring_whitespace':True})
counts={name:len(pages(ROOT/name)) for name in ('ECTA_R26.pdf','SUPP_R26.pdf','RESPONSE_R26.pdf')}
assert counts=={'ECTA_R26.pdf':15,'SUPP_R26.pdf':159,'RESPONSE_R26.pdf':6},counts
print('Verified PDF page counts and all 151 historical pages:',counts)
status=json.loads((REV/'results/test_summary.json').read_text())
assert status['tests_run']==11 and status['passed'] and status['failures']==0 and status['errors']==0
review=ROOT/'R26_REVIEW.md';s=review.read_text()
s+='\n## Repository-side publication\n\nThe original preparation metadata above is retained as historical provenance. This remote package is reproduced from the 35 hash-verified delivered source files and the exact pinned R24/R25 inputs. All eleven checks and the 151-page preservation audit must pass before the workflow atomically creates both R26 references. The successful workflow artifact contains `R26_REMOTE_PUBLICATION_RECEIPT.json`, recording the exact commit and the read-back of both remote heads. No existing branch is overwritten.\n'
review.write_text(s)
environment=REV/'results/local_environment.json';d=json.loads(environment.read_text());d['execution']='GitHub Actions serial CPU reproduction of the delivered R26 source';d['workflow_run']=os.environ['GITHUB_RUN_ID'];write(environment,d)
manifest={'frozen_base':os.environ['BASE'],'local_delivery_commit':'19aea758e73826fc1ad64326f0172079d5396745',
 'source_payload_sha256':'caad5af9a8f8496780446046554feff87eadd7faadfcba7d7308fbf525140fbe',
 'workflow_run':os.environ['GITHUB_RUN_ID'],'pdf_page_counts':counts,'tests':status,
 'publication_status':'Prepared and validated before atomic push; use the post-push workflow receipt and remote refs as proof of publication.',
 'pdf_sha256':{name:sha(ROOT/name) for name in counts},
 'original_scientific_scope_unchanged':True,'historical_pdf_pages_preserved':151}
write(REV/'results/REMOTE_BUILD_MANIFEST.json',manifest)
