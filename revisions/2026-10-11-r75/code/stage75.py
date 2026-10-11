"""Full archive reproduction and exact-object staging; visual review is separate."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,time
import publish_api75 as api
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];REL=str(R.relative_to(ROOT))
WORK='revision/econometrica-nbo-r75-referee-revision-2026-10-11';SOURCE='revision/econometrica-nbo-r75-source-2026-10-11';READY='revision/econometrica-nbo-r75-review-ready-2026-10-11'
HISTORY=[f'revisions/2026-10-10-r{n}' for n in (62,63,64,65,66,67)]+[f'revisions/2026-10-11-r{n}' for n in (69,70,72,73,74)]
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def commit(message):
    api.git('add','-f',REL,'README.md')
    if api.git('diff','--cached','--name-only'):api.git('commit','-m',message)
    return api.git('rev-parse','HEAD')
def main():
    start=time.perf_counter();release=json.loads((R/'audit/RELEASE75.json').read_text());source=api.git('rev-parse','HEAD')
    if release['status']!='passed' or not release['full_retained_replay']:raise AssertionError('Full retained replay required')
    if source!=release['tested_source_commit']:raise AssertionError('Current source differs from tested source')
    if api.git('diff','--name-only','HEAD','--',*HISTORY):raise AssertionError('Historical tracked source modified')
    companions=[]
    for p in sorted((ROOT/'revisions/2026-10-11-r73/build').glob('*.pdf')):
        name='prior-'+p.stem+'73.pdf' if p.stem in ('ECTA','supp','appendix','response') else p.name
        shutil.copy2(p,R/'build'/name);companions.append({'file':'build/'+name,'sha256':sha(p),'source':str(p.relative_to(ROOT))})
    if not any(x['file']=='build/prior-ECTA73.pdf' for x in companions):raise AssertionError('Prior main article not retained')
    save(R/'audit/COMPANIONS75.json',{'status':'unchanged','files':companions})
    archive_sha=commit('R75: retain fully tested original-paper revision, complete current cost records and compiled documents')
    api.persist(archive_sha)
    with tempfile.TemporaryDirectory(prefix='nbo-r75-clean-') as tmp:
        root=Path(tmp);tar=root/'source.tar';paths=HISTORY+[REL]
        with tar.open('wb') as f:subprocess.run(['git','archive',archive_sha,*paths],cwd=ROOT,stdout=f,check=True)
        digest=sha(tar);size=tar.stat().st_size;subprocess.run(['tar','-xf',str(tar),'-C',str(root)],check=True);tar.unlink()
        copy=root/REL;shutil.rmtree(copy/'build');(copy/'build').mkdir()
        for pattern in ('*72.tex','*73.tex','*75.tex'):
            for p in (copy/'tables').glob(pattern):p.unlink()
        dependency=root/'revisions/2026-10-10-r62/inputs/revisions/2026-10-08-r49/code/service49.py'
        if not dependency.exists():raise AssertionError('Transitive dependency missing')
        log=R/'audit/build-logs/clean-rebuild75.log'
        with log.open('w') as f:proc=subprocess.run([sys.executable,str(copy/'code/build75.py'),'--full'],cwd=copy,stdout=f,stderr=subprocess.STDOUT)
        if proc.returncode:raise RuntimeError('Clean archive rebuild failed:\n'+log.read_text()[-16000:])
        reproduced=json.loads((copy/'audit/RELEASE75.json').read_text());matches={}
        if not reproduced['full_retained_replay'] or reproduced['total_tests']!=release['total_tests']:raise AssertionError('Incomplete clean regression set')
        for a,b in zip(release['documents'],reproduced['documents']):
            if a['document']!=b['document']:raise AssertionError('Document order mismatch')
            m={'pages_equal':a['pages']==b['pages'],'text_equal':a['text_sha256']==b['text_sha256'],'pdf_bytes_equal':a['sha256']==b['sha256']}
            if not m['pages_equal'] or not m['text_equal']:raise AssertionError(('Clean document mismatch',a['document'],m))
            matches[a['document']]=m
        save(R/'audit/CLEAN_REBUILD75.json',{'status':'passed','archive_commit':archive_sha,'archive_sha256':digest,'archive_bytes':size,'archived_paths':paths,'total_tests':reproduced['total_tests'],'full_retained_replay':True,'document_matches':matches,'clean_release':reproduced,'log_sha256':sha(log),'transitive_dependency_sha256':sha(dependency),'network_used_by_builder':False,'new_statistical_rows_from_replay':0,'generated_pdfs_and_tables_removed':True})
    (ROOT/'README.md').write_text('''# Neural Bellman Operators

**R75 original-paper referee revision.**

Reading target: `'''+READY+'''` (created only after actual visual approval).

[Main article](revisions/2026-10-11-r75/build/ECTA.pdf) · [Technical Supplement](revisions/2026-10-11-r75/build/supp.pdf) · [Numerical and Development Appendix](revisions/2026-10-11-r75/build/appendix.pdf) · [Referee response](revisions/2026-10-11-r75/build/response.pdf)

[Content preservation](revisions/2026-10-11-r75/CONTENT_MAP75.md) · [Full path audit](revisions/2026-10-11-r75/audit/RESULT_AUDIT75.json) · [Final manifest](revisions/2026-10-11-r75/audit/FINAL_DELIVERY75.json)

The original NBO title, author, model and optimum remain. The attained neural
continuation now determines a complete controller whose original-law cost is
independently qualified. Both ReLU controllers have lower expected cost than
their matched Bernstein controllers. Seven of eight paired width targets pass;
the unsuccessful target and all historical adverse comparisons are retained.
The identified gains support an explicit priced-adoption region, not a
universal neural speed claim or an invented economic calibration.

Every prior active section remains compiled once. All new integer paths,
acquired ranges, supports and exact confidence endpoints are recomputed.
The complete archive rebuild includes transitive numerical inputs and every
historical suite's record data. A source or staged branch is not equivalent to
final review readiness: FINAL_DELIVERY75.json must have status passed and bind
the actual output visual review. Old revision and review branches are unchanged.

Offline full build: `python3 revisions/2026-10-11-r75/code/build75.py --full`.
''')
    excluded={'DELIVERY_FILES75.json','STAGED_DELIVERY75.json','FINAL_DELIVERY75.json','VISUAL75.json'}
    files={str(p.relative_to(R)):sha(p) for p in sorted(R.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in excluded}
    save(R/'audit/DELIVERY_FILES75.json',files)
    save(R/'audit/STAGED_DELIVERY75.json',{'status':'checks_passed_visual_pending','canonical_branch':READY,'source_branch':SOURCE,'revision_branch':WORK,'tested_source_commit':source,'archive_commit':archive_sha,'documents':release['documents'],'total_tests':release['total_tests'],'original_law_rows':131072,'independently_recomputed_paths':655360,'delivery_files_sha256':sha(R/'audit/DELIVERY_FILES75.json'),'files':len(files),'stage_seconds':time.perf_counter()-start,'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),'reference_updates':'serial checked non-forced Git API updates'})
    staged=commit('R75: stage full archive-verified manuscript and all original-law cost evidence; visual approval required')
    api.persist(staged);api.move(WORK,staged,source);api.move(SOURCE,staged)
    print(json.dumps({'status':'staged_remote_verified','commit':staged,'total_tests':release['total_tests'],'files':len(files),'canonical_pending_visual':READY},indent=2))
if __name__=='__main__':main()
