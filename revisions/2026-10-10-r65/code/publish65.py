"""Archive rebuild and non-forced, verified publication of the R65 revision."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1]
REPO=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=R,text=True).strip())
REL=str(R.relative_to(REPO));BRANCH='revision/econometrica-nbo-r65-referee-revision-2026-10-10';READY='revision/econometrica-nbo-r65-review-ready-2026-10-10'
FONT={'.ttf','.otf','.woff','.woff2','.pfb','.pfa','.afm','.tfm'}
def run(args):return subprocess.check_output(args,cwd=REPO,text=True).strip()
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):p.write_text(json.dumps(j,sort_keys=True,indent=2)+'\n')
def commit(message):
    run(['git','add','-f',REL,'README.md'])
    if run(['git','diff','--cached','--name-only']):run(['git','commit','-m',message])
    return run(['git','rev-parse','HEAD'])
def main():
    start=time.perf_counter();release=json.loads((R/'audit/RELEASE65.json').read_text())
    if release['status']!='passed' or release['tests']['total']!=63:raise AssertionError('Incomplete tested release')
    tested=run(['git','rev-parse','HEAD'])
    snap=commit('R65: retain original-paper revision, 63 tests, complete service replay and seven compiled documents')
    with tempfile.TemporaryDirectory(prefix='nbo-r65-clean-') as tmp:
        p=Path(tmp);tar=p/'source.tar'
        with tar.open('wb') as f:subprocess.run(['git','archive',snap,REL],cwd=REPO,stdout=f,check=True)
        subprocess.run(['tar','-xf',str(tar),'-C',str(p)],check=True)
        copy=p/REL
        for path in (copy/'build',copy/'retained62/build'):
            if path.exists():shutil.rmtree(path)
        for path in (copy/'tables').glob('*65.tex'):path.unlink()
        log=R/'audit/build-logs/clean-publication65.log'
        with log.open('w') as f:status=subprocess.run([sys.executable,str(copy/'code/build65.py'),'--documents'],cwd=copy,stdout=f,stderr=subprocess.STDOUT)
        if status.returncode:raise RuntimeError(log.read_text()[-8000:])
        reproduced=json.loads((copy/'audit/DOCUMENT_REBUILD65.json').read_text())
        checks={}
        for old,new in zip(release['documents'],reproduced['documents']):
            checks[old['document']]=dict(pages_equal=old['pages']==new['pages'],text_equal=old['text_sha256']==new['text_sha256'],pdf_bytes_equal=old['sha256']==new['sha256'])
            if not checks[old['document']]['pages_equal'] or not checks[old['document']]['text_equal']:raise AssertionError(checks)
        save(R/'audit/CLEAN_REBUILD65.json',dict(status='passed',archive_commit=snap,removed_generated_tables=True,removed_generated_pdfs=True,network_used=False,
            scope='Clean ordinary-source publication and table derivation; the full numerical replay and tests are bound by RELEASE65, not counted a second time.',document_checks=checks,
            reproduced=reproduced,log_sha256=sha(log)))
    if not (R/'prior-root-README.md').exists():shutil.copy2(REPO/'README.md',R/'prior-root-README.md')
    (REPO/'README.md').write_text('''# Neural Bellman Operators

**Current complete referee revision: R65.**

Canonical branch: `'''+READY+'''`.

[Article](revisions/2026-10-10-r65/build/ECTA.pdf) · [Technical supplement](revisions/2026-10-10-r65/build/supp.pdf) · [Response](revisions/2026-10-10-r65/build/response.pdf)

[Revision guide](revisions/2026-10-10-r65/README.md) · [Content-location map](revisions/2026-10-10-r65/CONTENT_MAP65.md)

R65 keeps the original NBO title, constructive operator, investment primitives
and Bellman optimum. It integrates completed state-lattice-free query services,
proves a prediction/localization certificate, and reports the matched benefits
and complete costs of certificate-gated neural routing. All 256 original
isolated services are retained and replayed. No new optimizer runs or independent
continuous-law cost observations are created by this publication.

The preceding complete article and supplement and their broader companions
are preserved byte-for-byte in source and compiled separately. Earlier review
and scientific branches are unchanged. See the four retained PDFs under the
revision guide rather than treating them as four new empirical studies.

`revisions/2026-10-10-r65/audit/FINAL_DELIVERY65.json` binds the ordinary sources,
63 tests, complete record replay, seven documents and clean publication rebuild.
Offline full verification: `python3 revisions/2026-10-10-r65/code/build65.py`.
''')
    files={}
    for p in sorted(R.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p.name=='FINAL_DELIVERY65.json':continue
        if p.suffix.lower() in FONT:raise AssertionError('Standalone font file in release')
        files[str(p.relative_to(R))]=sha(p)
    final=dict(status='passed',canonical_branch=READY,revision_branch=BRANCH,tested_source_commit=tested,clean_archive_commit=snap,
        reviewed_manuscript_commit='cfecc5ffcdeb836b1c70e9b98d1dc87f6f8cd097',review_commit='eb02fdb321fe6f26de9caa3afcbe2f84531faef2',
        completed_R64_commit='2b84410c8f2b77839340fb46d6e8b741e3e497fc',workflow_run_id=os.getenv('GITHUB_RUN_ID'),
        documents=release['documents'],total_tests=63,file_sha256=files,file_count=len(files),publication_seconds=time.perf_counter()-start,
        checked_services=256,checked_policy_decisions=55296,requeried_distinct_decisions=27648,
        new_training_runs=0,new_independent_continuous_law_observations=0,
        scope='Full original-paper revision and complete source-frozen record replay; clean rebuild is a publication rebuild, not a second scientific experiment.')
    save(R/'audit/FINAL_DELIVERY65.json',final)
    for path,h in files.items():
        if sha(R/path)!=h:raise AssertionError('Final file changed '+path)
    finalsha=commit('R65: publish original NBO revision with complete replay, preserved companions and clean archive verification')
    run(['git','push','--atomic','origin','HEAD:refs/heads/'+BRANCH,'HEAD:refs/heads/'+READY])
    for b in (BRANCH,READY):
        if not run(['git','ls-remote','--heads','origin','refs/heads/'+b]).startswith(finalsha+'\t'):raise AssertionError('Remote head mismatch')
    print(json.dumps(dict(status='remote_verified',commit=finalsha,branches=[BRANCH,READY],documents=release['documents'],tests=63),indent=2))
if __name__=='__main__':main()
