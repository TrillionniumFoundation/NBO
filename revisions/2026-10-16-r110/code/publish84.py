"""Publish a fully rebuilt R84 candidate; visual qualification remains explicit."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1];REPO=R.parents[1];REL=str(R.relative_to(REPO))
BRANCH='revision/econometrica-nbo-r84-referee-revision-2026-10-12'
SOURCE='revision/econometrica-nbo-r84-source-2026-10-12'
CANDIDATE='revision/econometrica-nbo-r84-publication-candidate-2026-10-12'
DEPENDENCIES=[f'revisions/2026-10-10-r{n}' for n in (62,63,64,65,66,67)]+[f'revisions/2026-10-11-r{n}' for n in (69,70,72,73,77,78)]+[f'revisions/2026-10-12-r{n}' for n in (80,81,82,83,84)]

def run(args):return subprocess.check_output(args,cwd=REPO,text=True).strip()
def sha(p):
    with Path(p).open('rb') as h:return hashlib.file_digest(h,'sha256').hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def commit(message):
    run(['git','add','-A','-f',REL,'README.md'])
    if run(['git','diff','--cached','--name-only']):run(['git','commit','-m',message])
    return run(['git','rev-parse','HEAD'])

def main():
    begin=time.perf_counter();release=json.loads((R/'audit/RELEASE84.json').read_text())
    if release['status']!='passed' or release['skipped_tests']!=0:raise AssertionError('Full unskipped build required')
    archive_sha=commit('R84: retain complete original-paper manuscript, exact records, all tests and four compiled documents')
    log=R/'audit/build-logs/clean-archive84.log'
    with tempfile.TemporaryDirectory(prefix='nbo-r84-clean-') as temp:
        root=Path(temp)
        source=subprocess.Popen(['git','archive',archive_sha,*DEPENDENCIES],cwd=REPO,stdout=subprocess.PIPE)
        try:
            subprocess.run(['tar','-xf','-','-C',str(root)],stdin=source.stdout,check=True)
        finally:
            source.stdout.close()
        if source.wait()!=0:raise RuntimeError('Pinned archive preparation failed')
        clean=root/REL;shutil.rmtree(clean/'build');(clean/'build').mkdir()
        for p in (clean/'tables').glob('*84*'):p.unlink()
        with log.open('w') as out:
            job=subprocess.run([sys.executable,str(clean/'code/build84.py')],cwd=clean,stdout=out,stderr=subprocess.STDOUT)
        if job.returncode:raise RuntimeError('Full clean rebuild failed:\n'+log.read_text(errors='replace')[-18000:])
        second=json.loads((clean/'audit/RELEASE84.json').read_text());lookup={x['document']:x for x in second['documents']};matches={}
        for first in release['documents']:
            other=lookup[first['document']];matches[first['document']]=dict(pages_equal=first['pages']==other['pages'],text_equal=first['text_sha256']==other['text_sha256'],pdf_bytes_equal=first['sha256']==other['sha256'])
        if not all(x['pages_equal'] and x['text_equal'] and x['pdf_bytes_equal'] for x in matches.values()):raise AssertionError(matches)
        if second['total_tests']!=release['total_tests'] or second['skipped_tests']!=0:raise AssertionError('Clean full test roster differs')
        save(R/'audit/CLEAN_REBUILD84.json',dict(status='passed',archive_commit=archive_sha,removed_pdfs=True,removed_generated_tables84=True,
            full_unskipped_builder_reexecuted=True,network_used_by_builder=False,new_independent_samples=0,document_matches=matches,
            clean_release=second,clean_log_sha256=sha(log)))
    README='''# Neural Bellman Operators

## R84 original-paper referee revision — fully built publication candidate

Current source and PDF directory: `revisions/2026-10-12-r84/`.

[Main article](revisions/2026-10-12-r84/build/ECTA.pdf) · [Technical supplement](revisions/2026-10-12-r84/build/supp.pdf) · [Numerical and development appendix](revisions/2026-10-12-r84/build/appendix.pdf) · [Point-by-point response](revisions/2026-10-12-r84/build/response.pdf)

R84 preserves the original title, author, economic primitives, attained NBO
construction, original Bellman optimum and every inherited active section.
It adds full-menu and common-readout qualification, a complete economic-transfer
theorem, 2,548 independently checked qualification certificates, and a new
classwide refinement decision. All adverse basis comparisons and old failures
remain visible. The study adds no independent cost sample or fit.

The full unskipped build and clean-archive reproduction are recorded in
`audit/RELEASE84.json` and `audit/CLEAN_REBUILD84.json` inside the current directory.
A separate visual inspection against the actual PDF hashes is still required
before the candidate is called review-ready. `audit/FINAL_DELIVERY84.json`
records the exact current status rather than borrowing an earlier release.

Full offline verification: `python3 revisions/2026-10-12-r84/code/build84.py`.
The inherited source directories specified in `code/publish84.py` are included
in the clean reproduction archive. Older revision and review branches are unchanged.
'''
    (REPO/'README.md').write_text(README)
    (R/'README.md').write_text('''# Neural Bellman Operators — R84

Ordinary submission sources: ECTA.tex, supp.tex, appendix.tex and response.md.
The original title and all inherited active sections remain in their original
documents. CONTENT_MAP84.md locates the new theorem, full proof and catalogue.

code/build84.py executes all inherited and new unskipped suites, preserved
source/evidence checks, relevant full-bin replay, every new exact certificate
and four-document compilation. code/publish84.py repeats that full builder from
a clean archive and checks exact PDF bytes, text and page counts.

The 976 full-menu and 1,572 joint-event certificates and 36 class comparisons
use the original cost family; no new fit or independent cost row is added.
Original scientific clocks are preserved. Incremental execution, independent
replay and publication work are timed separately.

FINAL_DELIVERY84.json records the publication status. Visual qualification is
separate from compilation and must be bound to the actual current PDF hashes.
''')
    files={str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='FINAL_DELIVERY84.json'}
    final=dict(status='publication_candidate_pending_visual_inspection',candidate_branch=CANDIDATE,revision_branch=BRANCH,source_branch=SOURCE,
        tested_source_commit=release['tested_source_commit'],clean_archive_commit=archive_sha,workflow_run_id=os.getenv('GITHUB_RUN_ID'),
        documents=release['documents'],total_tests=release['total_tests'],skipped_tests=0,full_build='passed',clean_archive='passed',
        inherited_content_preserved=True,visual_inspection='not_implied_by_build',new_independent_cost_rows=0,new_fits=0,
        file_count=len(files),file_sha256=files,publication_seconds=time.perf_counter()-begin)
    save(R/'audit/FINAL_DELIVERY84.json',final)
    for n,h in files.items():
        if sha(R/n)!=h:raise AssertionError('Publication file changed '+n)
    head=commit('R84: publish source-bound original-paper revision after complete clean reproduction; visual gate explicit')
    run(['git','push','--atomic','origin','HEAD:refs/heads/'+BRANCH,'HEAD:refs/heads/'+SOURCE,'HEAD:refs/heads/'+CANDIDATE])
    for branch in (BRANCH,SOURCE,CANDIDATE):
        if not run(['git','ls-remote','--heads','origin','refs/heads/'+branch]).startswith(head+'\t'):raise AssertionError('Remote ref mismatch '+branch)
    print(json.dumps(dict(status='remote_publication_candidate_verified',commit=head,branches=[BRANCH,SOURCE,CANDIDATE],documents=release['documents'],total_tests=release['total_tests']),indent=2),flush=True)
if __name__=='__main__':main()
