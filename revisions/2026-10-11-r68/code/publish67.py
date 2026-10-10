"""Clean source-archive reproduction and non-forced R67 remote publication."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1];REPO=R.parents[1];REL=str(R.relative_to(REPO))
PREFIX='revision/econometrica-nbo-r67-';DATE='2026-10-10'
AUTHOR=PREFIX+'referee-revision-'+DATE;SOURCE=PREFIX+'source-'+DATE;READY=PREFIX+'review-ready-'+DATE
FONTS={'.ttf','.otf','.woff','.woff2','.pfb','.pfa','.afm','.tfm'}
def call(args):return subprocess.check_output(args,cwd=REPO,text=True).strip()
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,sort_keys=True,indent=2)+'\n')
def commit(message):
    call(['git','add','-f',REL,'README.md'])
    if subprocess.run(['git','diff','--cached','--quiet'],cwd=REPO).returncode:call(['git','commit','-m',message])
    return call(['git','rev-parse','HEAD'])
def main():
    start=time.perf_counter();release=json.loads((R/'audit/RELEASE67.json').read_text())
    if release['status']!='passed' or len(release['documents'])!=9:raise AssertionError('Incomplete publication')
    rootreadme='''# Neural Bellman Operators

**Current complete referee revision: R67.**

Canonical branch: `'''+READY+'''`.

[Main article](revisions/2026-10-10-r67/build/ECTA.pdf) · [Technical supplement](revisions/2026-10-10-r67/build/supp.pdf) · [Point-by-point response](revisions/2026-10-10-r67/build/response.pdf)

[Revision guide](revisions/2026-10-10-r67/README.md) · [Preserved content map](revisions/2026-10-10-r67/CONTENT_MAP67.md)

R67 retains the original NBO title, model, constructive neural operator and
Bellman optimum. It adds a computable pre-query certificate, a certificate-aware
ReLU readout with an optimization-gap bound, and a two-control extension.
The complete corrected 212-process catalogue includes ten same-gate controls,
eight fitting seeds, prospective cached reuse, continuous-law costs of the
actual callable policies, and two-control/two-shock scaling through four dates.

An independent rational trajectory check detected endpoint aliasing in R66's
cumulative path account. R67 preserves that counterexample and the entire old
execution, repairs the accumulator, freezes a separate source version, and
reruns every declared process. Repeated streams are not additional IID data.

The current article, supplement and response and six unchanged historical
companions are bound by `revisions/2026-10-10-r67/audit/FINAL_DELIVERY67.json`.
Numerical and mathematical regression tests, all-record replay, source/statement
preservation and a clean offline archive rebuild are recorded separately.
The older review and scientific branches remain unchanged.

Full offline verification: `python3 revisions/2026-10-10-r67/code/build67.py`.
'''
    (REPO/'README.md').write_text(rootreadme)
    archive_commit=commit('R67: retain ordinary original-paper revision, corrected evidence replay and nine compiled documents')
    cleanlog=R/'audit/build-logs/clean-archive67.log'
    with tempfile.TemporaryDirectory(prefix='nbo67-clean-') as tmp:
        base=Path(tmp);archive=base/'inputs.tar'
        paths=['revisions/2026-10-10-r'+str(n) for n in range(62,68)]
        with archive.open('wb') as f:subprocess.run(['git','archive',archive_commit,*paths],cwd=REPO,stdout=f,check=True)
        subprocess.run(['tar','-xf',str(archive),'-C',str(base)],check=True)
        clean=base/REL
        shutil.rmtree(clean/'build');(clean/'build').mkdir()
        for p in (clean/'tables').glob('*67*'):p.unlink()
        with cleanlog.open('w') as out:proc=subprocess.run([sys.executable,str(clean/'code/build67.py')],cwd=clean,stdout=out,stderr=subprocess.STDOUT)
        if proc.returncode:raise RuntimeError('Clean archive failed:\n'+cleanlog.read_text()[-8000:])
        new=json.loads((clean/'audit/RELEASE67.json').read_text())
        olddocs={d['document']:d for d in release['documents']};newdocs={d['document']:d for d in new['documents']}
        matches={name:dict(pages_equal=d['pages']==newdocs[name]['pages'],text_equal=d['text_sha256']==newdocs[name]['text_sha256'],pdf_bytes_equal=d['sha256']==newdocs[name]['sha256']) for name,d in olddocs.items()}
        if not all(x['pages_equal'] and x['text_equal'] for x in matches.values()):raise AssertionError(matches)
        if release['tests']!=new['tests']:raise AssertionError('Clean test count mismatch')
        save(R/'audit/CLEAN_REBUILD67.json',dict(status='passed',archive_commit=archive_commit,removed_generated_pdfs=True,removed_generated_tables=True,full_record_and_test_replay=True,new_scientific_services=0,additional_independent_rows=0,network_used_by_builder=False,documents=matches,clean_release=new,log_sha256=sha(cleanlog)))
    files={str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='FINAL_DELIVERY67.json'}
    if any(Path(p).suffix.lower() in FONTS for p in files):raise AssertionError('Standalone font file in delivery')
    record=json.loads((R/'audit/RESULT_AUDIT67.json').read_text())
    delivery=dict(status='passed',canonical_branch=READY,revision_branch=AUTHOR,source_branch=SOURCE,
        clean_archive_commit=archive_commit,scientific_source_branch=PREFIX+'science-source-'+DATE,
        scientific_executed_branch=PREFIX+'science-executed-'+DATE,
        reviewed_r65_commit='34a5ce17dc3ac4681b6d004eca00637f28104e28',referee_commit='d548a97f461160296239ed6a973d4a91ef9d1fad',
        workflow_run_id=os.getenv('GITHUB_RUN_ID'),documents=release['documents'],tests=release['tests'],preservation=release['preservation'],
        clean_archive_rebuild='passed',file_sha256=files,file_count=len(files),publication_seconds=time.perf_counter()-start,
        scope='The final commit contains this manifest and descends from the fully tested source archive. Source freezes, actual corrected process receipts, raw enclosures, record replay and proofs are separate evidence objects. No external mathematical acceptance claim.')
    save(R/'audit/FINAL_DELIVERY67.json',delivery)
    final=commit('R67: publish original NBO referee revision with corrected full execution and clean-archive verification')
    call(['git','push','--atomic','origin','HEAD:refs/heads/'+AUTHOR,'HEAD:refs/heads/'+SOURCE,'HEAD:refs/heads/'+READY])
    for branch in (AUTHOR,SOURCE,READY):
        if not call(['git','ls-remote','--heads','origin','refs/heads/'+branch]).startswith(final+'\t'):raise AssertionError('Remote ref mismatch '+branch)
    print(json.dumps(dict(status='remote_publication_verified',commit=final,branches=[AUTHOR,SOURCE,READY],documents=release['documents'],tests=release['tests']),indent=2))
if __name__=='__main__':main()
