"""Clean ordinary-source R57 reproduction and non-forced remote publication."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile,shutil,time
R=Path(__file__).resolve().parents[1];REPO=R.parents[1];REL=str(R.relative_to(REPO))
REVISION='revision/econometrica-nbo-r57-referee-revision-2026-10-09'
SOURCE='revision/econometrica-nbo-r57-source-2026-10-09'
READY='revision/econometrica-nbo-r57-review-ready-2026-10-09'
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
    start=time.perf_counter();release=json.loads((R/'audit/RELEASE57.json').read_text())
    if release['status']!='passed' or release['publication_only']:raise AssertionError('Full current-source verification required')
    run(['git','config','user.name','NBO revision verification']);run(['git','config','user.email','nbo-revision@users.noreply.github.com'])
    archive_sha=commit('R57: retain seven compiled documents and full new and inherited numerical verification')
    log=R/'audit/build-logs/clean-archive57.log'
    with tempfile.TemporaryDirectory(prefix='nbo-r57-clean-') as tmp:
        root=Path(tmp);tar=root/'revision.tar'
        with tar.open('wb') as out:subprocess.run(['git','archive',archive_sha,REL],cwd=REPO,stdout=out,check=True)
        subprocess.run(['tar','-xf',str(tar),'-C',str(root)],check=True);copy=root/REL;shutil.rmtree(copy/'build');(copy/'build').mkdir()
        for pattern in ('*56.tex','*57.tex'):
            for p in (copy/'tables').glob(pattern):p.unlink()
        with log.open('w') as out:proc=subprocess.run([sys.executable,str(copy/'code/build57.py'),'--publication-only'],cwd=copy,stdout=out,stderr=subprocess.STDOUT,check=False)
        if proc.returncode:raise RuntimeError('Clean R57 publication rebuild failed: '+log.read_text()[-7000:])
        reproduced=json.loads((copy/'audit/RELEASE57.json').read_text());old={x['document']:x for x in release['documents']};new={x['document']:x for x in reproduced['documents']}
        matches={n:dict(pages_equal=old[n]['pages']==new[n]['pages'],text_equal=old[n]['extracted_text_sha256']==new[n]['extracted_text_sha256'],pdf_bytes_equal=old[n]['sha256']==new[n]['sha256']) for n in old}
        if not all(x['pages_equal'] and x['text_equal'] for x in matches.values()):raise AssertionError(matches)
        if reproduced['total_tests']!=release['total_tests']:raise AssertionError('Clean test count mismatch')
        save(R/'audit/CLEAN_REBUILD57.json',dict(status='passed',archive_commit=archive_sha,source_evidence_binding='passed',generated_pdfs_removed=True,generated_tables56_and57_removed=True,document_matches=matches,clean_release=reproduced,log_sha256=digest(log),scope='Offline clean publication reconstruction, tests and complete scientific-source/evidence binding; not another training or economic-service execution'))
    (REPO/'README.md').write_text('''# Neural Bellman Operators

**Authoritative complete referee revision: R57.**

Canonical branch: `'''+READY+'''`.

[Main paper](revisions/2026-10-09-r57/build/ECTA.pdf) · [Technical supplement](revisions/2026-10-09-r57/build/supp.pdf) · [Referee response](revisions/2026-10-09-r57/build/response.pdf)

[Revision guide](revisions/2026-10-09-r57/README.md) · [Complete development](revisions/2026-10-09-r57/build/complete.pdf) · [Complete proofs](revisions/2026-10-09-r57/build/complete-supp.pdf)

R57 continues the original NBO title, economic laws, constructive own-future backend and Bellman-accuracy target. It adds a fitted-witness transfer theorem, explicit action-sensitive neural moduli, and a new prospective experiment actually deploying exact trained neural action search. Ninety separately reconstructed target services and eighteen independent returned-policy comparison sets are retained with their frozen protocol and source.

The seven-document publication, exact solver and full certificate/path replay, inherited verification, complete service registry and clean archive reproduction are bound by `revisions/2026-10-09-r57/audit/FINAL_DELIVERY57.json`.

Earlier revision and review branches are unchanged. Prior theory, applications, failed attempts and adverse comparisons remain in the development companions and preserved sources. Exact fitted minimization, stricter verification endpoints and identified economic superiority are reported as distinct claims.
''')
    wrapper=REPO/'ECTA.tex'
    if wrapper.exists() and len(wrapper.read_text())<500 and 'revisions/' in wrapper.read_text():wrapper.write_text(r'\input{revisions/2026-10-09-r57/ECTA}'+'\n')
    files=[p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    if any(p.suffix.lower() in FORBIDDEN for p in files):raise AssertionError('Standalone font file in publication')
    manifest={str(p.relative_to(R)):digest(p) for p in files if p.name!='FINAL_DELIVERY57.json'}
    save(R/'audit/FINAL_DELIVERY57.json',dict(status='passed',canonical_branch=READY,revision_branch=REVISION,source_branch=SOURCE,tested_source_commit=release['source_commit'],clean_archive_commit=archive_sha,workflow_run_id=os.getenv('GITHUB_RUN_ID'),workflow_head_sha=os.getenv('GITHUB_SHA'),file_sha256=manifest,file_count=len(manifest),documents=release['documents'],total_tests=release['total_tests'],new_scientific_services=release['new_scientific_services'],new_paired_sets=release['new_paired_sets'],attained=release['attained'],budget_exhausted=release['budget_exhausted'],clean_publication_rebuild='passed',source_and_label_preservation='passed',publication_seconds=time.perf_counter()-start,scope='Manifest-containing descendant of the tested source, with new frozen economic execution and complete current-source replay. Earlier observations, clocks and branches remain unchanged; no external editorial acceptance claimed.'))
    for name,h in manifest.items():
        if digest(R/name)!=h:raise AssertionError('Final file changed: '+name)
    sha=commit('R57: publish the complete original-paper referee revision and clean-rebuild evidence')
    run(['git','push','--atomic','origin','HEAD:refs/heads/'+REVISION,'HEAD:refs/heads/'+SOURCE,'HEAD:refs/heads/'+READY])
    for branch in (REVISION,SOURCE,READY):
        if not run(['git','ls-remote','--heads','origin','refs/heads/'+branch]).startswith(sha+'\t'):raise AssertionError('Remote publication mismatch: '+branch)
    print(json.dumps(dict(status='remote_publication_verified',commit=sha,branches=[REVISION,SOURCE,READY],files=len(manifest),tests=release['total_tests'],documents=release['documents']),indent=2))
if __name__=='__main__':main()
