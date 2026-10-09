"""Clean-archive reproduction and non-forced publication of the R54 package."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1]
REPO=R.parents[1]
REL=str(R.relative_to(REPO))
REVISION='revision/econometrica-nbo-r54-referee-revision-2026-10-08'
SOURCE='revision/econometrica-nbo-r54-source-2026-10-08'
READY='revision/econometrica-nbo-r54-review-ready-2026-10-08'
FORBIDDEN={'.ttf','.otf','.woff','.woff2','.pfb','.pfa','.afm','.tfm'}

def run(args,**kw):return subprocess.check_output(args,cwd=REPO,text=True,**kw).strip()
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def commit(message):
    run(['git','add','-f',REL,'README.md'])
    if (REPO/'ECTA.tex').exists():run(['git','add','ECTA.tex'])
    if run(['git','status','--porcelain']):run(['git','commit','-m',message])
    return run(['git','rev-parse','HEAD'])
def main():
    start=time.perf_counter();release=json.loads((R/'audit/RELEASE54.json').read_text())
    if release['status']!='passed':raise AssertionError('Publication build not passed')
    run(['git','config','user.name','NBO revision verification'])
    run(['git','config','user.email','nbo-revision@users.noreply.github.com'])
    archive_sha=commit('R54: retain complete ordinary manuscript, full evidence replay and five compiled documents')
    cleanlog=R/'audit/build-logs/clean-archive54.log'
    with tempfile.TemporaryDirectory(prefix='nbo-r54-clean-') as tmp:
        root=Path(tmp)
        archive=root/'revision.tar'
        with archive.open('wb') as f:subprocess.run(['git','archive',archive_sha,REL],cwd=REPO,stdout=f,check=True)
        subprocess.run(['tar','-xf',str(archive),'-C',str(root)],check=True)
        copy=root/REL
        shutil.rmtree(copy/'build');(copy/'build').mkdir()
        for p in (copy/'tables').glob('*54*'):p.unlink()
        with cleanlog.open('w') as out:
            result=subprocess.run([sys.executable,str(copy/'code/build54.py')],cwd=copy,stdout=out,stderr=subprocess.STDOUT,check=False)
        if result.returncode:raise RuntimeError('Clean-archive rebuild failed: '+cleanlog.read_text()[-5000:])
        reproduced=json.loads((copy/'audit/RELEASE54.json').read_text())
        old={x['document']:x for x in release['documents']};new={x['document']:x for x in reproduced['documents']}
        matches={name:dict(pages_equal=old[name]['pages']==new[name]['pages'],extracted_text_equal=old[name]['extracted_text_sha256']==new[name]['extracted_text_sha256']) for name in old}
        if not all(v['pages_equal'] and v['extracted_text_equal'] for v in matches.values()):raise AssertionError(matches)
        if reproduced['total_tests']!=release['total_tests']:raise AssertionError('Clean test count differs')
        save(R/'audit/CLEAN_REBUILD54.json',dict(status='passed',archive_commit=archive_sha,
            removed_generated_pdfs=True,removed_generated_tables54=True,network_used=False,
            scientific_services_reexecuted=False,document_matches=matches,
            clean_release=reproduced,clean_log_sha256=digest(cleanlog)))
    readme='''# Neural Bellman Operators

**Authoritative complete referee revision: R54.**

Canonical branch: `'''+READY+'''`.

[Main paper](revisions/2026-10-08-r54/build/ECTA.pdf) · [Supplement](revisions/2026-10-08-r54/build/supp.pdf) · [Referee response](revisions/2026-10-08-r54/build/response.pdf)

[Revision guide](revisions/2026-10-08-r54/README.md) · [Complete development](revisions/2026-10-08-r54/build/complete.pdf) · [Complete proof supplement](revisions/2026-10-08-r54/build/complete-supp.pdf)

R54 retains the original title, model, constructive neural backend, broader
applications and adverse comparisons. It adds a proved directed full-sweep
certificate, explicit work and storage accounts, and an integrated actual-cost
study using the separately frozen R53 full-sweep, adaptive and controlled
misspecification records. This publication does not add independent samples or
claim unexecuted high-dimensional or representation-specific superiority.

The five-document build, inherited and new tests, all-record replay, label and
source preservation, and clean offline archive reproduction are bound by
`revisions/2026-10-08-r54/audit/FINAL_DELIVERY54.json`.
The earlier revision and review branches are unchanged.

Offline build: `python3 revisions/2026-10-08-r54/code/build54.py`.
'''
    (REPO/'README.md').write_text(readme)
    wrapper=REPO/'ECTA.tex'
    if wrapper.exists() and len(wrapper.read_text())<500 and 'revisions/' in wrapper.read_text():
        wrapper.write_text(r'\input{revisions/2026-10-08-r54/ECTA}'+'\n')
    allfiles=[p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    if any(p.suffix.lower() in FORBIDDEN for p in allfiles):raise AssertionError('Standalone font file in publication')
    manifest={str(p.relative_to(R)):digest(p) for p in allfiles if p.name!='FINAL_DELIVERY54.json'}
    final=dict(status='passed',canonical_branch=READY,revision_branch=REVISION,source_branch=SOURCE,
        tested_source_commit=release['source_commit'],clean_archive_commit=archive_sha,
        workflow_run_id=os.getenv('GITHUB_RUN_ID'),workflow_head_sha=os.getenv('GITHUB_SHA'),
        file_sha256=manifest,file_count=len(manifest),documents=release['documents'],
        total_tests=release['total_tests'],clean_archive_rebuild='passed',
        source_and_label_preservation='passed',publication_seconds=time.perf_counter()-start,
        new_independent_cost_observations=0,
        scope='scientific source and records preserved; full endpoint replay, five documents and clean rebuild verified; final commit is the manifest-containing descendant of the tested source')
    save(R/'audit/FINAL_DELIVERY54.json',final)
    for name,h in manifest.items():
        if digest(R/name)!=h:raise AssertionError('Final file changed: '+name)
    sha=commit('R54: publish complete original-paper revision with clean-archive and full-delivery evidence')
    run(['git','push','--atomic','origin','HEAD:refs/heads/'+REVISION,'HEAD:refs/heads/'+SOURCE,'HEAD:refs/heads/'+READY])
    for branch in (REVISION,SOURCE,READY):
        line=run(['git','ls-remote','--heads','origin','refs/heads/'+branch])
        if not line.startswith(sha+'\t'):raise AssertionError('Remote publication mismatch: '+branch)
    print(json.dumps(dict(status='remote_publication_verified',commit=sha,branches=[REVISION,SOURCE,READY],files=len(manifest),documents=release['documents'],tests=release['total_tests']),indent=2))
if __name__=='__main__':main()
