"""Check the exact committed referee object before and after a clean rebuild.

The validation output lives outside the checked tree. PDF bytes may differ on
rebuild because of creation metadata; document text, page count, source inputs,
and the hashes of the committed deliverables are checked separately.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
REV=ROOT/'revisions/2026-09-24-r29'
NAMES=['ECTA_R29','SUPP_R29','RESPONSE_R29','COMPUTATION_R29','HISTORY_R29']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def head():return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
def pages(p):
    text=subprocess.check_output(['pdfinfo',str(p)],text=True)
    return int(next(z.split(':',1)[1].strip() for z in text.splitlines() if z.startswith('Pages:')))
def text_digest(p,dest):
    subprocess.run(['pdftotext','-layout',str(p),str(dest)],check=True)
    return sha(dest)
def write(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')

def before(out):
    commit=head()
    if os.environ.get('GITHUB_SHA') and os.environ['GITHUB_SHA']!=commit:
        raise AssertionError('Checkout is not the workflow source commit')
    for ancestor in ['cd1191f278948942f42c6507b4566108f2aa2f6d','d7a809a5913bc5178cba186e003750ee3a9cc574','f1874444422fa2d6aba30c6ff3203fcf47d70341']:
        subprocess.run(['git','merge-base','--is-ancestor',ancestor,commit],cwd=ROOT,check=True)
    manifest=read(REV/'REVISION_MANIFEST.json')
    for path,h in manifest['source_sha256'].items():
        if sha(ROOT/path)!=h:raise AssertionError('Scientific source differs from manifest: '+path)
    for path,h in read(REV/'results/controls/environment.json')['source_sha256'].items():
        if sha(ROOT/path)!=h:raise AssertionError('Executed source changed: '+path)
    build=read(REV/'DOCUMENT_BUILD.json');docs={}
    for name in NAMES:
        p=ROOT/(name+'.pdf');record=build['documents'][name]
        if sha(p)!=record['pdf_sha256'] or pages(p)!=record['pages']:
            raise AssertionError('Committed PDF differs from the build record: '+name)
        if sha(ROOT/(name+'.tex'))!=record['tex_sha256']:
            raise AssertionError('Committed article source differs from the build record: '+name)
        docs[name]={'committed_pdf_sha256':sha(p),'pages':pages(p),'text_sha256':text_digest(p,out/(name+'.committed.txt'))}
    inputs=list((REV/'paper').rglob('*.tex'))+[ROOT/(n+'.tex') for n in NAMES]
    inputs += [ROOT/'REVISION_INDEX.md',ROOT/'R29_REVIEW.md',REV/'disposition.json',REV/'REVISION_MANIFEST.json',REV/'source_audit/PRESERVATION.json',REV/'results/R29_HEADLINE_RESULTS.json',REV/'results/R28_HEADLINE_RESULTS.json']
    snapshot={'checked_commit':commit,'documents':docs,'publication_inputs_sha256':{str(p.relative_to(ROOT)):sha(p) for p in inputs},'build_source_commit':build['build_source_commit'],'science_evidence_commit':build['science_evidence_commit']}
    write(out/'COMMITTED_PUBLICATION.json',snapshot)

def after(out):
    prior=read(out/'COMMITTED_PUBLICATION.json')
    if prior['checked_commit']!=head():raise AssertionError('Commit changed during validation')
    for path,h in prior['publication_inputs_sha256'].items():
        if sha(ROOT/path)!=h:raise AssertionError('Regeneration changed a committed publication input: '+path)
    for name,record in prior['documents'].items():
        p=ROOT/(name+'.pdf')
        if pages(p)!=record['pages']:raise AssertionError('Rebuild changed page count: '+name)
        if text_digest(p,out/(name+'.rebuilt.txt'))!=record['text_sha256']:
            raise AssertionError('Rebuild changed PDF text or layout: '+name)
        record['rebuilt_pdf_sha256']=sha(p)
        log=(ROOT/(name+'.log')).read_text(errors='replace')
        if any(x in log for x in ['undefined','Overfull','multiply defined']):
            raise AssertionError('Unresolved typesetting diagnostics: '+name)
    tests=read(out/'SCIENCE_TESTS.json')
    if not tests['passed'] or tests['checked_commit']!=head():
        raise AssertionError('The exact-head scientific tests did not pass')
    prior.update(status='passed',source_regeneration_identical=True,pdf_text_and_page_counts_identical=True,
                 tests=tests,workflow_run_id=os.environ.get('GITHUB_RUN_ID'),
                 workflow_attempt=os.environ.get('GITHUB_RUN_ATTEMPT'),
                 original_full_domain_target_closed=False,
                 qualification='Checks establish the recorded computational and publication identities; uninstantiated continuous-control hypotheses are not proved by CI.')
    write(out/'PUBLICATION_VALIDATION.json',prior)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['before','after']);parser.add_argument('--directory',type=Path,required=True);args=parser.parse_args()
    args.directory.mkdir(parents=True,exist_ok=True)
    (before if args.phase=='before' else after)(args.directory)
