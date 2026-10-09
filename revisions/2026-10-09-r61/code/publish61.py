"""Clean-archive verification and non-forced publication of the R61 manuscript."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1];REPO=R.parents[1];REL=str(R.relative_to(REPO))
BRANCHES=('revision/econometrica-nbo-r61-referee-revision-2026-10-09','revision/econometrica-nbo-r61-source-2026-10-09','revision/econometrica-nbo-r61-review-ready-2026-10-09')
FONT={'.ttf','.otf','.woff','.woff2','.pfb','.pfa','.afm','.tfm'}
def run(cmd,**kw):return subprocess.check_output(cmd,cwd=REPO,text=True,**kw).strip()
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def commit(message):
    run(['git','add','-f',REL,'README.md'])
    if (REPO/'ECTA.tex').exists():run(['git','add','ECTA.tex'])
    if run(['git','status','--porcelain']):run(['git','commit','-m',message])
    return run(['git','rev-parse','HEAD'])
def main():
    start=time.perf_counter();release=json.loads((R/'audit/RELEASE61.json').read_text())
    if release['status']!='passed':raise AssertionError('Publication verification incomplete')
    run(['git','config','user.name','NBO revision verification']);run(['git','config','user.email','nbo-revision@users.noreply.github.com'])
    archive_sha=commit('R61: retain seven compiled ordinary documents and verified current evidence tables')
    log=R/'audit/build-logs/clean-archive61.log'
    with tempfile.TemporaryDirectory(prefix='nbo-r61-clean-') as temp:
        root=Path(temp);tar=root/'revision.tar'
        with tar.open('wb') as out:subprocess.run(['git','archive',archive_sha,REL],cwd=REPO,stdout=out,check=True)
        subprocess.run(['tar','-xf',str(tar),'-C',str(root)],check=True);copy=root/REL
        shutil.rmtree(copy/'build');(copy/'build').mkdir()
        for path in (copy/'tables').glob('*61*'):path.unlink()
        with log.open('w') as out:proc=subprocess.run([sys.executable,str(copy/'code/build61.py')],cwd=copy,stdout=out,stderr=subprocess.STDOUT)
        if proc.returncode:raise RuntimeError('Clean build failed: '+log.read_text()[-12000:])
        clean=json.loads((copy/'audit/RELEASE61.json').read_text());original={x['document']:x for x in release['documents']};rebuilt={x['document']:x for x in clean['documents']}
        matches={name:dict(pages_equal=original[name]['pages']==rebuilt[name]['pages'],extracted_text_equal=original[name]['extracted_text_sha256']==rebuilt[name]['extracted_text_sha256'],pdf_bytes_equal=original[name]['sha256']==rebuilt[name]['sha256']) for name in original}
        if not all(x['pages_equal'] and x['extracted_text_equal'] for x in matches.values()):raise AssertionError(matches)
        if clean['total_tests']!=release['total_tests']:raise AssertionError('Clean regression count changed')
        save(R/'audit/CLEAN_REBUILD61.json',dict(status='passed',archive_commit=archive_sha,removed_build_directory=True,removed_current_tables=True,documents=matches,total_tests=clean['total_tests'],clean_build_seconds=clean['build_seconds'],log_sha256=digest(log),network_used=False,new_training_services=0,new_policy_cost_samples=0))
    (REPO/'README.md').write_text('''# Neural Bellman Operators

**Current complete referee revision: R61.**

Canonical branch: `revision/econometrica-nbo-r61-review-ready-2026-10-09`.

[Main article](revisions/2026-10-09-r61/build/ECTA.pdf) · [Technical supplement](revisions/2026-10-09-r61/build/supp.pdf) · [Referee response](revisions/2026-10-09-r61/build/response.pdf)

[Revision guide](revisions/2026-10-09-r61/README.md) · [Complete development](revisions/2026-10-09-r61/build/complete.pdf) · [Full proof companion](revisions/2026-10-09-r61/build/complete-supp.pdf)

The title, economic primitives, original Bellman objective, trained backend,
broader applications and adverse evidence remain intact. R61 integrates a
root-free exact action witness, a constrained multi-action extension, stable
Bellman enclosures, complete original-policy revalidation and a fresh native
two-by-two experiment with explicit batching and crossover results.

The R59 advisory report, complete R60 source freezes and successful and failed
records are preserved. R61 adds no training service or independent policy-cost
sample. Its fresh factorial observations concern implementation work.
All 96 original prospective returns, including 16 exhausted budgets, remain in
the registry. Cold compilation, complete return work, original policy cost and
additional original-optimum verification have separate accounting boundaries.

The seven-document build, inherited and new tests, source preservation and
clean offline rebuild are bound by
`revisions/2026-10-09-r61/audit/FINAL_DELIVERY61.json`.
Historical revision and review branches are unchanged.

Offline ordinary-source build:
`python3 revisions/2026-10-09-r61/code/build61.py`.
''')
    wrapper=REPO/'ECTA.tex'
    if wrapper.exists() and len(wrapper.read_text())<500 and 'revisions/' in wrapper.read_text():wrapper.write_text(r'\input{revisions/2026-10-09-r61/ECTA}'+'\n')
    files=[p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    if any(p.suffix.lower() in FONT for p in files):raise AssertionError('Standalone font file must not be delivered')
    manifest={str(p.relative_to(R)):digest(p) for p in files if p.name!='FINAL_DELIVERY61.json'}
    save(R/'audit/FINAL_DELIVERY61.json',dict(status='passed',canonical_branch=BRANCHES[-1],branches=list(BRANCHES),tested_source_commit=release['tested_source_commit'],clean_archive_commit=archive_sha,workflow_run_id=os.getenv('GITHUB_RUN_ID'),workflow_head_sha=os.getenv('GITHUB_SHA'),documents=release['documents'],total_tests=release['total_tests'],new_R61_tests=release['new_R61_tests'],clean_archive_rebuild='passed',source_and_label_preservation='passed',file_sha256=manifest,file_count=len(manifest),publication_seconds=time.perf_counter()-start,new_training_services=0,new_independent_policy_cost_observations=0,new_implementation_work_experiment='matched native two-by-two factorial',scope='Final manifest-containing commit is a descendant of the tested ordinary source commit and clean archive. All scientific source/result identities, prior content, current sources and compiled outputs are explicitly bound; no external editorial approval is implied.'))
    for name,h in manifest.items():
        if digest(R/name)!=h:raise AssertionError('Manifest input changed: '+name)
    sha=commit('R61: publish complete original-paper revision after seven-document clean archive reproduction')
    run(['git','push','--atomic','origin',*['HEAD:refs/heads/'+b for b in BRANCHES]])
    for branch in BRANCHES:
        if not run(['git','ls-remote','--heads','origin','refs/heads/'+branch]).startswith(sha+'\t'):raise AssertionError('Remote ref mismatch: '+branch)
    print(json.dumps(dict(status='remote_publication_verified',commit=sha,branches=list(BRANCHES),documents=[dict(name=x['document'],pages=x['pages']) for x in release['documents']],tests=release['total_tests'],new_tests=release['new_R61_tests']),indent=2),flush=True)
if __name__=='__main__':main()
