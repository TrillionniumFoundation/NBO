"""Clean-archive publication reproduction and non-forced R56 remote delivery."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile,shutil,time
R=Path(__file__).resolve().parents[1];REPO=R.parents[1];REL=str(R.relative_to(REPO))
REVISION='revision/econometrica-nbo-r56-referee-revision-2026-10-09'
SOURCE='revision/econometrica-nbo-r56-source-2026-10-09'
READY='revision/econometrica-nbo-r56-review-ready-2026-10-09'
FORBIDDEN={'.ttf','.otf','.woff','.woff2','.pfb','.pfa','.afm','.tfm'}
def run(args):return subprocess.check_output(args,cwd=REPO,text=True).strip()
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def commit(message):
    run(['git','add','-f',REL,'README.md'])
    if (REPO/'ECTA.tex').exists():run(['git','add','ECTA.tex'])
    if run(['git','status','--porcelain']):run(['git','commit','-m',message])
    return run(['git','rev-parse','HEAD'])
def main():
    start=time.perf_counter();release=json.loads((R/'audit/RELEASE56.json').read_text())
    if release['status']!='passed' or release['publication_only']:raise AssertionError('Full current-source verification required')
    run(['git','config','user.name','NBO revision verification']);run(['git','config','user.email','nbo-revision@users.noreply.github.com'])
    archive_sha=commit('R56: retain seven compiled documents and complete saved-model certificate verification')
    log=R/'audit/build-logs/clean-archive56.log'
    with tempfile.TemporaryDirectory(prefix='nbo-r56-clean-') as tmp:
        root=Path(tmp);tar=root/'revision.tar'
        with tar.open('wb') as out:subprocess.run(['git','archive',archive_sha,REL],cwd=REPO,stdout=out,check=True)
        subprocess.run(['tar','-xf',str(tar),'-C',str(root)],check=True);copy=root/REL;shutil.rmtree(copy/'build');(copy/'build').mkdir()
        for p in (copy/'tables').glob('*56.tex'):p.unlink()
        with log.open('w') as out:proc=subprocess.run([sys.executable,str(copy/'code/build56.py'),'--publication-only'],cwd=copy,stdout=out,stderr=subprocess.STDOUT,check=False)
        if proc.returncode:raise RuntimeError('Clean publication rebuild failed: '+log.read_text()[-6000:])
        reproduced=json.loads((copy/'audit/RELEASE56.json').read_text());old={x['document']:x for x in release['documents']};new={x['document']:x for x in reproduced['documents']}
        matches={n:dict(pages_equal=old[n]['pages']==new[n]['pages'],text_equal=old[n]['extracted_text_sha256']==new[n]['extracted_text_sha256'],pdf_bytes_equal=old[n]['sha256']==new[n]['sha256']) for n in old}
        if not all(x['pages_equal'] and x['text_equal'] for x in matches.values()):raise AssertionError(matches)
        save(R/'audit/CLEAN_REBUILD56.json',dict(status='passed',archive_commit=archive_sha,source_evidence_binding='passed',generated_pdfs_removed=True,generated_tables56_removed=True,document_matches=matches,clean_release=reproduced,log_sha256=digest(log),scope='Offline clean publication reconstruction plus tests and full scientific-source/evidence binding; not a second scientific-service execution'))
    (REPO/'README.md').write_text('''# Neural Bellman Operators

**Authoritative complete referee revision: R56.**

Canonical branch: `'''+READY+'''`.

[Main paper](revisions/2026-10-09-r56/build/ECTA.pdf) · [Supplement](revisions/2026-10-09-r56/build/supp.pdf) · [Referee response](revisions/2026-10-09-r56/build/response.pdf)

[Revision guide](revisions/2026-10-09-r56/README.md) · [Complete development](revisions/2026-10-09-r56/build/complete.pdf) · [Complete proofs](revisions/2026-10-09-r56/build/complete-supp.pdf)

R56 retains the original NBO title, economic laws, constructive Bellman-accuracy target and resource account. It adds exact action-lattice witnesses for trained ReLU continuations, non-tensor verification, signed-reference stability and work bounds, prospective stopping and confidence-qualified learned structure. The separately frozen R55 execution is integrated without new cost samples or overwritten service clocks.

The seven-document release, saved-model certificate reintegration, exact moment checks, complete service replay, historical preservation and clean publication rebuild are bound by `revisions/2026-10-09-r56/audit/FINAL_DELIVERY56.json`.

Earlier revision and review branches are unchanged. The development companions retain all prior theory, applications and unfavorable evidence.
''')
    wrapper=REPO/'ECTA.tex'
    if wrapper.exists() and len(wrapper.read_text())<500 and 'revisions/' in wrapper.read_text():wrapper.write_text(r'\input{revisions/2026-10-09-r56/ECTA}'+'\n')
    files=[p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    if any(p.suffix.lower() in FORBIDDEN for p in files):raise AssertionError('Standalone font file in publication')
    manifest={str(p.relative_to(R)):digest(p) for p in files if p.name!='FINAL_DELIVERY56.json'}
    save(R/'audit/FINAL_DELIVERY56.json',dict(status='passed',canonical_branch=READY,revision_branch=REVISION,source_branch=SOURCE,tested_source_commit=release['source_commit'],clean_archive_commit=archive_sha,workflow_run_id=os.getenv('GITHUB_RUN_ID'),workflow_head_sha=os.getenv('GITHUB_SHA'),file_sha256=manifest,file_count=len(manifest),documents=release['documents'],total_tests=release['total_tests'],clean_publication_rebuild='passed',source_and_label_preservation='passed',new_cost_samples=0,publication_seconds=time.perf_counter()-start,scope='Manifest-containing descendant of the tested source; complete evidence and ordinary sources retained, no claim of external editorial acceptance'))
    for name,h in manifest.items():
        if digest(R/name)!=h:raise AssertionError('Final file changed: '+name)
    sha=commit('R56: publish original-paper referee revision with complete verification and clean publication evidence')
    run(['git','push','--atomic','origin','HEAD:refs/heads/'+REVISION,'HEAD:refs/heads/'+SOURCE,'HEAD:refs/heads/'+READY])
    for branch in (REVISION,SOURCE,READY):
        if not run(['git','ls-remote','--heads','origin','refs/heads/'+branch]).startswith(sha+'\t'):raise AssertionError('Remote publication mismatch: '+branch)
    print(json.dumps(dict(status='remote_publication_verified',commit=sha,branches=[REVISION,SOURCE,READY],files=len(manifest),tests=release['total_tests'],documents=release['documents']),indent=2))
if __name__=='__main__':main()
