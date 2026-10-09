"""Publish only after the ordinary R59 package and clean rebuild pass."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1];REPO=R.parents[1];REL=str(R.relative_to(REPO))
REV='revision/econometrica-nbo-r59-referee-revision-2026-10-09'
SOURCE='revision/econometrica-nbo-r59-source-2026-10-09'
READY='revision/econometrica-nbo-r59-review-ready-2026-10-09'
CANDIDATE='revision/econometrica-nbo-r59-publication-candidate-2026-10-09'
FORBIDDEN={'.ttf','.otf','.woff','.woff2','.pfa','.pfb','.afm','.tfm'}

def run(args):return subprocess.check_output(args,cwd=REPO,text=True).strip()
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def commit(message,root_readme=False):
    run(['git','add','-f',REL])
    if root_readme:run(['git','add','README.md'])
    changed=subprocess.run(['git','diff','--cached','--quiet'],cwd=REPO,check=False).returncode
    if changed:run(['git','commit','-m',message])
    return run(['git','rev-parse','HEAD'])

def main():
    start=time.perf_counter();release=json.loads((R/'audit/RELEASE59.json').read_text())
    if release['status']!='passed':raise AssertionError('Publication verification did not pass')
    run(['git','config','user.name','NBO revision verification']);run(['git','config','user.email','nbo-revision@users.noreply.github.com'])
    files=[p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    if any(p.suffix.lower() in FORBIDDEN for p in files):raise AssertionError('Standalone font file cannot be published')
    archive_commit=commit('R59: retain fully reconstructed original-paper revision and seven compiled documents')
    run(['git','push','origin','HEAD:refs/heads/'+CANDIDATE])
    cleanlog=R/'audit/build-logs/clean-archive59.log'
    with tempfile.TemporaryDirectory(prefix='nbo-r59-clean-') as tmp:
        root=Path(tmp);archive=root/'paper.tar'
        with archive.open('wb') as out:subprocess.run(['git','archive',archive_commit,REL],cwd=REPO,stdout=out,check=True)
        subprocess.run(['tar','-xf',str(archive),'-C',str(root)],check=True);copy=root/REL
        shutil.rmtree(copy/'build');(copy/'build').mkdir()
        removed=[]
        for p in (copy/'tables').glob('*59*'):removed.append(p.name);p.unlink()
        with cleanlog.open('w') as log:
            p=subprocess.run([sys.executable,str(copy/'code/build59.py'),'--publication-only'],cwd=copy,stdout=log,stderr=subprocess.STDOUT,check=False)
        if p.returncode:raise RuntimeError('Clean archive rebuild failed: '+cleanlog.read_text(errors='replace')[-6000:])
        clean=json.loads((copy/'audit/RELEASE59.json').read_text());old={d['document']:d for d in release['documents']};new={d['document']:d for d in clean['documents']}
        matches={k:dict(pages_equal=old[k]['pages']==new[k]['pages'],extracted_text_equal=old[k]['extracted_text_sha256']==new[k]['extracted_text_sha256'],pdf_bytes_equal=old[k]['sha256']==new[k]['sha256']) for k in old}
        if set(old)!=set(new) or len(new)!=7 or not all(v['pages_equal'] and v['extracted_text_equal'] for v in matches.values()):raise AssertionError(matches)
        if clean['total_tests']!=release['total_tests'] or clean['result_audit_sha256']!=release['result_audit_sha256']:raise AssertionError('Clean test or scientific evidence identity mismatch')
        save(R/'audit/CLEAN_REBUILD59.json',dict(status='passed',archive_commit=archive_commit,removed_generated_build_directory=True,removed_generated_tables59=removed,network_used=False,retraining=False,new_independent_samples=0,scientific_binding_checked=True,document_matches=matches,clean_release=clean,clean_log_sha256=digest(cleanlog)))
    (REPO/'README.md').write_text('''# Neural Bellman Operators

**Authoritative complete referee revision: R59.**

Canonical branch: `'''+READY+'''`.

[Main paper](revisions/2026-10-09-r59/build/ECTA.pdf) · [Technical supplement](revisions/2026-10-09-r59/build/supp.pdf) · [Point-by-point response](revisions/2026-10-09-r59/build/response.pdf)

[Revision guide](revisions/2026-10-09-r59/README.md) · [Complete development](revisions/2026-10-09-r59/build/complete.pdf) · [Complete proofs](revisions/2026-10-09-r59/build/complete-supp.pdf)

R59 retains the original title, economic laws, constructive own-future backend,
feasible witnesses and Bellman-accuracy objective. It adds proved lossless
trained-neural action screening and prospective transcript invariance, then
integrates the separately frozen R58 matched 36-service execution. Both exact
solvers, all certificates, unique original-law paths and every stopping decision
are reconstructed. Unsuccessful targets and conventional-policy comparisons
remain visible. Publication creates no new training or independent samples.

Seven ordinary-source documents, the inherited and new verification chain,
protected source/label checks and clean offline archive reproduction are bound
by `revisions/2026-10-09-r59/audit/FINAL_DELIVERY59.json`.
Earlier revision and review branches are unchanged. Equal-policy computation
savings and superiority over different policies are explicitly distinct claims.

Offline build: `python3 revisions/2026-10-09-r59/code/build59.py`.
''')
    files=[p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='FINAL_DELIVERY59.json']
    hashes={str(p.relative_to(R)):digest(p) for p in files}
    final=dict(status='passed',canonical_branch=READY,revision_branch=REV,source_branch=SOURCE,baseline_commit=release['baseline_commit'],controlling_review_commit=release['controlling_review_commit'],tested_source_commit=release['source_commit'],clean_archive_commit=archive_commit,workflow_run_id=os.getenv('GITHUB_RUN_ID'),workflow_head_sha=os.getenv('GITHUB_SHA'),documents=release['documents'],total_tests=release['total_tests'],new_theorem_tests=release['new_theorem_tests'],replay_counts=release['replay_counts'],matched_services=release['matched_services'],attained=release['attained'],budget_exhausted=release['budget_exhausted'],all_exact_policy_identities=True,protected_files=release['protected_files'],file_sha256=hashes,file_count=len(hashes),clean_archive_rebuild='passed',original_scientific_clocks_replaced=False,new_training_services=0,new_independent_policy_cost_observations=0,publication_seconds=time.perf_counter()-start,scope='Manifest-containing descendant of the tested ordinary sources; full audit and clean publication passed. Visual inspection is documented separately when performed; no external referee acceptance is asserted.')
    save(R/'audit/FINAL_DELIVERY59.json',final)
    for name,h in hashes.items():
        if digest(R/name)!=h:raise AssertionError('Publication file changed after manifest: '+name)
    sha=commit('R59: publish original NBO revision with complete scientific and clean-archive delivery evidence',True)
    run(['git','push','--atomic','origin','HEAD:refs/heads/'+REV,'HEAD:refs/heads/'+SOURCE,'HEAD:refs/heads/'+READY])
    for branch in (REV,SOURCE,READY):
        if not run(['git','ls-remote','--heads','origin','refs/heads/'+branch]).startswith(sha+'\t'):raise AssertionError('Remote publication identity mismatch: '+branch)
    print(json.dumps(dict(status='remote_publication_verified',commit=sha,branches=[REV,SOURCE,READY],documents=[dict(name=x['document'],pages=x['pages']) for x in release['documents']],tests=release['total_tests'],file_count=len(hashes)),indent=2))
if __name__=='__main__':main()
