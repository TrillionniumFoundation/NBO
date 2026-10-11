"""Publish only a tested R70 manuscript and a matching clean-archive rebuild."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1];REPO=R.parents[1];REL=str(R.relative_to(REPO))
WORK='revision/econometrica-nbo-r70-referee-revision-2026-10-11'
SOURCE='revision/econometrica-nbo-r70-source-2026-10-11'
READY='revision/econometrica-nbo-r70-review-ready-2026-10-11'
BASE='2c07e464e81930f14b3122054704731ec5a139ff'
DEPENDENCIES=['revisions/2026-10-10-r'+str(n) for n in (62,63,64,65,66,67)]+['revisions/2026-10-11-r69',REL]

def run(args):return subprocess.check_output(args,cwd=REPO,text=True).strip()
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,sort_keys=True,indent=2)+'\n')
def commit(message):
    run(['git','add','-f',REL,'README.md'])
    if run(['git','diff','--cached','--name-only']):run(['git','commit','-m',message])
    return run(['git','rev-parse','HEAD'])
def main():
    begin=time.perf_counter();release=json.loads((R/'audit/RELEASE70.json').read_text())
    if release['status']!='passed':raise AssertionError('Current build has not passed')
    run(['git','config','user.name','NBO revision verification']);run(['git','config','user.email','nbo-revision@users.noreply.github.com'])
    archive_sha=commit('R70: retain complete original-paper revision, independent audits and compiled reading set')
    log=R/'audit/build-logs/clean-archive70.log'
    with tempfile.TemporaryDirectory(prefix='nbo-r70-clean-') as tmp:
        root=Path(tmp);tar=root/'sources.tar'
        with tar.open('wb') as out:subprocess.run(['git','archive',archive_sha,*DEPENDENCIES],cwd=REPO,stdout=out,check=True)
        subprocess.run(['tar','-xf',str(tar),'-C',str(root)],check=True)
        clean=root/REL;shutil.rmtree(clean/'build');(clean/'build').mkdir()
        for p in (clean/'tables').glob('*70.tex'):p.unlink()
        for name in ('RELEASE70.json','RESULT_AUDIT70.json','DETAILS70.json','SUMMARY70.json','CATALOGUE70.json','TABLES70.json','TESTS70.json'):(clean/'audit'/name).unlink(missing_ok=True)
        with log.open('w') as out:proc=subprocess.run([sys.executable,str(clean/'code/build70.py')],cwd=clean,stdout=out,stderr=subprocess.STDOUT)
        if proc.returncode:raise RuntimeError('Clean archive failed:\n'+log.read_text(errors='replace')[-12000:])
        second=json.loads((clean/'audit/RELEASE70.json').read_text());matches={}
        for before in release['documents']+release['companions']:
            after=next(x for x in second['documents']+second['companions'] if x['document']==before['document'])
            matches[before['document']]=dict(pages_equal=before['pages']==after['pages'],text_equal=before['text_sha256']==after['text_sha256'],pdf_bytes_equal=before['sha256']==after['sha256'])
        if not all(x['pages_equal'] and x['text_equal'] for x in matches.values()):raise AssertionError(('Archive document mismatch',matches))
        if release['total_tests']!=second['total_tests']:raise AssertionError('Test count changed')
        save(R/'audit/CLEAN_REBUILD70.json',dict(status='passed',archive_commit=archive_sha,network_used=False,generated_current_pdfs_and_tables_removed=True,all_test_suites_and_record_audits_rerun=True,document_matches=matches,clean_release=second,log_sha256=sha(log)))
    (REPO/'README.md').write_text('''# Neural Bellman Operators

**R70 — complete referee revision.**

Canonical branch: `'''+READY+'''`.

[Article](revisions/2026-10-11-r70/build/ECTA.pdf) · [Technical supplement](revisions/2026-10-11-r70/build/supp.pdf) · [Response to the referee](revisions/2026-10-11-r70/build/response.pdf)

[Revision guide](revisions/2026-10-11-r70/README.md) · [Content preservation map](revisions/2026-10-11-r70/CONTENT_MAP70.md) · [Final delivery manifest](revisions/2026-10-11-r70/audit/FINAL_DELIVERY70.json)

The original NBO topic, economic law and constructive operator remain intact.
R70 integrates the separately frozen R69 catalogue, certificate-aware readouts,
independent-context validation, predictable-deployment work bounds, paid
Bellman-centered cost inference and independent exact full-bin reconstruction.
All twelve scalar contrasts meet the predeclared equivalence margin, without
identifying strict cost superiority or a universal neural work advantage.

The unchanged R67 article and supplement and the broader prior development
remain companion PDFs in the R70 build directory. Historical sources, adverse
comparisons, warnings and the interval-accounting counterexample are retained.
The final manifest binds the tests, record replay, current documents and clean
offline archive reproduction. Numerical policy identity is an additional premise
when combining cost inference with deployment observations across runtimes.

Offline build: `python3 revisions/2026-10-11-r70/code/build70.py`.
''')
    manifest={str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='FINAL_DELIVERY70.json'}
    final=dict(status='passed',canonical_branch=READY,revision_branch=WORK,source_branch=SOURCE,tested_source_commit=release['tested_source_commit'],clean_archive_commit=archive_sha,review_commit=release['review_commit'],reviewed_manuscript_commit=release['reviewed_manuscript_commit'],executed_evidence_commit=BASE,workflow_run_id=os.environ.get('GITHUB_RUN_ID'),workflow_head_sha=os.environ.get('GITHUB_SHA'),file_sha256=manifest,files=len(manifest),readme_sha256=sha(REPO/'README.md'),documents=release['documents'],companions=release['companions'],total_tests=release['total_tests'],independent_audit=release['independent_audit'],preservation=release['preservation'],clean_archive_rebuild='passed',publication_seconds=time.perf_counter()-begin,new_independent_inference_rows=0,scope=release['scope'],visual_scope=release['visual_scope'])
    save(R/'audit/FINAL_DELIVERY70.json',final)
    for name,h in manifest.items():
        if sha(R/name)!=h:raise AssertionError('Manifest input changed '+name)
    head=commit('R70: publish original-paper referee revision with independent full-bin and clean-archive verification')
    changed=run(['git','diff','--name-only',BASE,head]).splitlines()
    allowed=lambda p:p.startswith(REL+'/') or p.startswith('.github/workflows/nbo-r70-') or p=='README.md'
    bad=[p for p in changed if not allowed(p)]
    if bad:raise AssertionError('Historical or unrelated paths changed: '+repr(bad))
    run(['git','push','--atomic','origin','HEAD:refs/heads/'+WORK,'HEAD:refs/heads/'+SOURCE,'HEAD:refs/heads/'+READY])
    for branch in (WORK,SOURCE,READY):
        if not run(['git','ls-remote','--heads','origin','refs/heads/'+branch]).startswith(head+'\t'):raise AssertionError('Remote branch mismatch '+branch)
    print(json.dumps(dict(status='remote_publication_verified',commit=head,branches=[WORK,SOURCE,READY],tests=release['total_tests'],documents=release['documents'],files=len(manifest)),indent=2))
if __name__=='__main__':main()
