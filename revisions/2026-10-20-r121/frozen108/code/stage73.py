"""Stage R73 only after a full, self-contained archive rebuild.

No scientific services are rerun. Every selected dependency directory is
archived, including transitive inputs and historical record-test data.
Review-ready publication additionally requires actual hash-bound visual review.
"""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1];REPO=R.parents[1];REL=str(R.relative_to(REPO))
WORK='revision/econometrica-nbo-r73-referee-revision-2026-10-11';SOURCE='revision/econometrica-nbo-r73-source-2026-10-11';READY='revision/econometrica-nbo-r73-review-ready-2026-10-11'
HISTORY=[f'revisions/2026-10-10-r{n}' for n in (62,63,64,65,66,67)]+[f'revisions/2026-10-11-r{n}' for n in (69,70,72)]

def run(args):return subprocess.check_output(args,cwd=REPO,text=True).strip()
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def commit(message):
    run(['git','add','-f',REL,'README.md'])
    if run(['git','diff','--cached','--name-only']):run(['git','commit','-m',message])
    return run(['git','rev-parse','HEAD'])

def main():
    start=time.perf_counter();release=json.loads((R/'audit/RELEASE73.json').read_text())
    if release['status']!='passed' or not release['full_retained_replay']:raise AssertionError('Full retained replay required')
    run(['git','config','user.name','NBO revision verification']);run(['git','config','user.email','nbo-revision@users.noreply.github.com'])
    changed=run(['git','diff','--name-only','HEAD','--',*HISTORY])
    if changed:raise AssertionError('Historical tracked file changed: '+changed)
    old=REPO/'revisions/2026-10-11-r70';companions=[]
    for p in sorted((old/'build').glob('*.pdf')):
        name='prior-'+p.stem+'70.pdf' if p.stem in ('ECTA','supp','response') else p.name
        if name in ('ECTA.pdf','supp.pdf','appendix.pdf','response.pdf'):raise AssertionError('Companion collision')
        shutil.copy2(p,R/'build'/name);companions.append(dict(file='build/'+name,source=str(p.relative_to(REPO)),sha256=sha(p)))
    if not {'build/prior-ECTA70.pdf','build/prior-supp70.pdf'}<=set(x['file'] for x in companions):raise AssertionError('Prior complete editions missing')
    save(R/'audit/COMPANIONS73.json',dict(status='unchanged',files=companions))
    archive_commit=commit('R73: retain tested original-paper revision, four construction services and ordinary compiled documents')
    paths=HISTORY+[REL]
    with tempfile.TemporaryDirectory(prefix='nbo-r73-archive-') as tmp:
        root=Path(tmp);archive=root/'source.tar'
        with archive.open('wb') as stream:subprocess.run(['git','archive',archive_commit,*paths],cwd=REPO,stdout=stream,check=True)
        archive_hash=sha(archive);archive_bytes=archive.stat().st_size
        subprocess.run(['tar','-xf',str(archive),'-C',str(root)],check=True);archive.unlink()
        copy=root/REL;shutil.rmtree(copy/'build');(copy/'build').mkdir()
        for pattern in ('*72.tex','*73.tex'):
            for p in (copy/'tables').glob(pattern):p.unlink()
        dependency=root/'revisions/2026-10-10-r62/inputs/revisions/2026-10-08-r49/code/service49.py'
        if not dependency.exists():raise AssertionError('Transitive original numerical input omitted')
        log=R/'audit/build-logs/clean-rebuild73.log'
        with log.open('w') as output:proc=subprocess.run([sys.executable,str(copy/'code/build73.py'),'--full'],cwd=copy,stdout=output,stderr=subprocess.STDOUT)
        if proc.returncode:raise RuntimeError('Clean full rebuild failed:\n'+log.read_text()[-16000:])
        rebuilt=json.loads((copy/'audit/RELEASE73.json').read_text());matches={}
        if rebuilt['total_tests']!=release['total_tests'] or not rebuilt['full_retained_replay']:raise AssertionError('Incomplete clean regression set')
        for before,after in zip(release['documents'],rebuilt['documents']):
            if before['document']!=after['document']:raise AssertionError('Document order mismatch')
            m=dict(pages_equal=before['pages']==after['pages'],text_equal=before['text_sha256']==after['text_sha256'],pdf_bytes_equal=before['sha256']==after['sha256'])
            if not m['pages_equal'] or not m['text_equal']:raise AssertionError(('Archive PDF mismatch',before['document'],m))
            matches[before['document']]=m
        save(R/'audit/CLEAN_REBUILD73.json',dict(status='passed',archive_commit=archive_commit,archive_sha256=archive_hash,archive_bytes=archive_bytes,archived_paths=paths,
             complete_dependency_and_test_data_archived=True,transitive_service49_sha256=sha(dependency),full_retained_replay=True,total_tests=rebuilt['total_tests'],
             scientific_services_reexecuted=False,generated_pdfs_and_tables_removed=True,network_used_by_builder=False,document_matches=matches,clean_release=rebuilt,log_sha256=sha(log)))
    (REPO/'README.md').write_text('''# Neural Bellman Operators

**R73 — original-paper referee revision.**

Reading target: `'''+READY+'''` (created only after the final visual gate).

[Main article](revisions/2026-10-11-r73/build/ECTA.pdf) · [Technical Supplement](revisions/2026-10-11-r73/build/supp.pdf) · [Numerical and Development Appendix](revisions/2026-10-11-r73/build/appendix.pdf) · [Referee response](revisions/2026-10-11-r73/build/response.pdf)

[Revision guide](revisions/2026-10-11-r73/README.md) · [Content preservation](revisions/2026-10-11-r73/CONTENT_MAP73.md) · [Final manifest](revisions/2026-10-11-r73/audit/FINAL_DELIVERY73.json)

The same NBO title, author, primitives, optimum and historical applications are
retained. R73 adds qualification-optimal continuation readouts, exact
primal--dual certificates and predictable original-law cost qualification.
Four prospectively frozen constructions and their independent exact checks
are retained alongside the earlier cost, vector and reuse evidence. A reduced
qualification bound is not a newly identified policy-cost gain.

All twenty preceding active sections are compiled byte-identically once.
The full archive rebuild includes transitive numerical inputs and every
historical suite's record data. The final manifest, when present with status
passed, binds the completed build, full archive reproduction and actual
hash-bound PDF visual review. Old revision and review branches are unchanged.

Offline full build: `python3 revisions/2026-10-11-r73/code/build73.py --full`.
''')
    save(R/'audit/INHERITED_IMMUTABILITY73.json',dict(status='passed',base_commit='5611b32978a2df5f32bff796f7dd209105cf28b0',modified_historical_tracked_paths=[]))
    excluded={'DELIVERY_FILES73.json','STAGED_DELIVERY73.json','FINAL_DELIVERY73.json','VISUAL73.json'}
    files={str(p.relative_to(R)):sha(p) for p in sorted(R.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in excluded}
    save(R/'audit/DELIVERY_FILES73.json',files)
    save(R/'audit/STAGED_DELIVERY73.json',dict(status='checks_passed_visual_pending',canonical_branch=READY,source_branch=SOURCE,revision_branch=WORK,
         tested_source_commit=release['tested_source_commit'],archive_commit=archive_commit,documents=release['documents'],total_tests=release['total_tests'],
         new_construction_services=4,new_independent_policy_cost_rows=0,files=len(files),delivery_files_sha256=sha(R/'audit/DELIVERY_FILES73.json'),
         workflow_run_id=os.environ.get('GITHUB_RUN_ID'),stage_seconds=time.perf_counter()-start))
    staged=commit('R73: stage full archive-verified paper and complete evidence; visual approval still required')
    run(['git','push','--atomic','origin','HEAD:refs/heads/'+WORK,'HEAD:refs/heads/'+SOURCE])
    for branch in (WORK,SOURCE):
        if not run(['git','ls-remote','--heads','origin','refs/heads/'+branch]).startswith(staged+'\t'):raise AssertionError('Remote stage mismatch')
    print(json.dumps(dict(status='staged_remote_verified',commit=staged,tests=release['total_tests'],canonical_pending_visual=READY,files=len(files)),indent=2))
if __name__=='__main__':main()
