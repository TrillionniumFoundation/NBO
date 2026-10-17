"""Stage tested R72 publication on new branches after clean archive reproduction.

The review-ready ref is created only after a separate hash-bound visual check.
No historical branch or scientific observation is rewritten.
"""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1];REPO=R.parents[1];REL=str(R.relative_to(REPO));OLD=R.parent/'2026-10-11-r70'
WORK='revision/econometrica-nbo-r72-referee-revision-2026-10-11';SOURCE='revision/econometrica-nbo-r72-source-2026-10-11';READY='revision/econometrica-nbo-r72-review-ready-2026-10-11'

def run(args):return subprocess.check_output(args,cwd=REPO,text=True).strip()
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def commit(message):
    run(['git','add','-f',REL,'README.md'])
    if run(['git','diff','--cached','--name-only']):run(['git','commit','-m',message])
    return run(['git','rev-parse','HEAD'])
def main():
    start=time.perf_counter();release=json.loads((R/'audit/RELEASE72.json').read_text())
    if release['status']!='passed' or not release['full_retained_replay']:raise AssertionError('Full release validation required')
    if release['independent_audit']['failed_services']:raise AssertionError('A failed service must be explicitly dispositioned before release')
    run(['git','config','user.name','NBO revision verification']);run(['git','config','user.email','nbo-revision@users.noreply.github.com'])
    old_changed=run(['git','diff','--name-only','HEAD','--','revisions/2026-10-10-r62','revisions/2026-10-10-r63','revisions/2026-10-10-r64','revisions/2026-10-10-r65','revisions/2026-10-10-r66','revisions/2026-10-10-r67','revisions/2026-10-11-r69','revisions/2026-10-11-r70'])
    if old_changed:raise AssertionError('Historical tracked bytes modified: '+old_changed)
    companions=[]
    for file in sorted((OLD/'build').glob('*.pdf')):
        name='prior-'+file.stem+'70.pdf' if file.stem in ('ECTA','supp','response') else file.name
        if name in ('ECTA.pdf','supp.pdf','appendix.pdf','response.pdf'):raise AssertionError('Companion collision')
        shutil.copy2(file,R/'build'/name)
        companions.append(dict(file='build/'+name,source=str(file.relative_to(REPO)),sha256=sha(file)))
    if not {'build/prior-ECTA70.pdf','build/prior-supp70.pdf'}<=set(x['file'] for x in companions):raise AssertionError('Prior complete paper missing')
    save(R/'audit/COMPANIONS72.json',dict(status='unchanged',files=companions))
    for p in R.rglob('*'):
        if p.is_file() and p.suffix.lower() in {'.ttf','.otf','.woff','.woff2','.pfb','.pfa','.afm','.tfm'}:raise AssertionError('Standalone font')
    archive_sha=commit('R72: retain ordinary original-paper revision, complete local scientific records and tested PDFs')
    paths=[REL,'revisions/2026-10-11-r70/sections']+[f'revisions/2026-10-10-r{n}/code' for n in (62,63,64,65,66,67)]+['revisions/2026-10-11-r69/code']
    with tempfile.TemporaryDirectory(prefix='nbo-r72-clean-') as tmp:
        root=Path(tmp);archive=root/'source.tar'
        with archive.open('wb') as output:subprocess.run(['git','archive',archive_sha,*paths],cwd=REPO,stdout=output,check=True)
        subprocess.run(['tar','-xf',str(archive),'-C',str(root)],check=True)
        copy=root/REL;shutil.rmtree(copy/'build');(copy/'build').mkdir()
        for p in (copy/'tables').glob('*72.tex'):p.unlink()
        log=R/'audit/build-logs/clean-rebuild72.log'
        with log.open('w') as output:result=subprocess.run([sys.executable,str(copy/'code/build72.py')],cwd=copy,stdout=output,stderr=subprocess.STDOUT)
        if result.returncode:raise RuntimeError('Clean rebuild failed:\n'+log.read_text()[-12000:])
        rebuilt=json.loads((copy/'audit/RELEASE72.json').read_text());matches={}
        for before,after in zip(release['documents'],rebuilt['documents']):
            match=dict(pages_equal=before['pages']==after['pages'],text_equal=before['text_sha256']==after['text_sha256'],pdf_bytes_equal=before['sha256']==after['sha256'])
            if not match['pages_equal'] or not match['text_equal']:raise AssertionError(('Clean document mismatch',before['document'],match))
            matches[before['document']]=match
        save(R/'audit/CLEAN_REBUILD72.json',dict(status='passed',archive_commit=archive_sha,document_matches=matches,new_suite_tests=rebuilt['total_tests'],full_inherited_suites_run_before_archive=True,scientific_services_reexecuted=False,generated_current_pdfs_and_tables_removed=True,log_sha256=sha(log)))
    (REPO/'README.md').write_text('''# Neural Bellman Operators

**R72 — original-paper referee revision.**

Canonical reading branch: `'''+READY+'''`.

[Main article](revisions/2026-10-11-r72/build/ECTA.pdf) · [Technical Supplement](revisions/2026-10-11-r72/build/supp.pdf) · [Numerical and Development Appendix](revisions/2026-10-11-r72/build/appendix.pdf) · [Referee response](revisions/2026-10-11-r72/build/response.pdf)

[Revision guide](revisions/2026-10-11-r72/README.md) · [Preservation map](revisions/2026-10-11-r72/CONTENT_MAP72.md) · [Final delivery](revisions/2026-10-11-r72/audit/FINAL_DELIVERY72.json)

The original title, operator, economic primitives, optimum and historical
applications are retained. R72 adds frozen-continuation cost/regret certificates,
exact conditional ReLU moments and paid Bellman-witness transport with capacity
repair. Its 36 complete processes preserve every descendant cost on a miss;
new transfer and moment operations receive independent rational checks.

All fifteen preceding active sections are compiled unchanged in the current
reading set. Prior complete PDFs and adverse numerical evidence remain
companions. New query workloads are not independent policy-cost samples,
and a successful reuse is not an empirical theorem of neural superiority.

The final manifest, when present with status passed, binds the completed
source/record checks, clean reproduction and actual PDF visual inspection.
All old review and revision branches remain unchanged.

Offline full build: `python3 revisions/2026-10-11-r72/code/build72.py --full`.
''')
    save(R/'audit/INHERITED_IMMUTABILITY72.json',dict(status='passed',modified_tracked_historical_paths=[],baseline_commit='b576584cb5b1ff5ceccbcf37a3fa6e1ac613aca6'))
    files={str(p.relative_to(R)):sha(p) for p in sorted(R.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in ('DELIVERY_FILES72.json','STAGED_DELIVERY72.json','FINAL_DELIVERY72.json','VISUAL72.json')}
    save(R/'audit/DELIVERY_FILES72.json',files)
    stage=dict(status='staged_checks_passed_visual_pending',canonical_branch=READY,source_branch=SOURCE,revision_branch=WORK,
               tested_source_commit=release['tested_source_commit'],clean_archive_commit=archive_sha,workflow_run_id=os.environ.get('GITHUB_RUN_ID'),
               source_freeze_sha256=sha(R/'SOURCE_FREEZE72.json'),scientific_manifest_sha256=sha(R/'audit/SCIENTIFIC_RECORDS72.json'),
               publication_files_manifest_sha256=sha(R/'audit/DELIVERY_FILES72.json'),release_sha256=sha(R/'audit/RELEASE72.json'),
               clean_rebuild_sha256=sha(R/'audit/CLEAN_REBUILD72.json'),companions_sha256=sha(R/'audit/COMPANIONS72.json'),
               documents=release['documents'],total_tests=release['total_tests'],new_processes=36,new_independent_policy_cost_rows=0,
               file_count=len(files),stage_seconds=time.perf_counter()-start,
               visual_inspection='pending separate hash-bound inspection; review-ready ref not yet created')
    save(R/'audit/STAGED_DELIVERY72.json',stage)
    for name,h in files.items():
        if sha(R/name)!=h:raise AssertionError('Staged file changed '+name)
    final=commit('R72: stage full inherited replay, new evidence, four documents and clean archive checks')
    run(['git','push','--atomic','origin','HEAD:refs/heads/'+WORK,'HEAD:refs/heads/'+SOURCE])
    for branch in (WORK,SOURCE):
        if not run(['git','ls-remote','--heads','origin','refs/heads/'+branch]).startswith(final+'\t'):raise AssertionError('Remote stage differs')
    print(json.dumps(dict(status=stage['status'],commit=final,documents=stage['documents'],tests=stage['total_tests'],files=len(files)),indent=2))
if __name__=='__main__':main()
