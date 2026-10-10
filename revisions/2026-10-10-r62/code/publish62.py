"""Clean-archive reproduction and atomic non-forced R62 remote publication."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1];REPO=R.parents[1];REL=str(R.relative_to(REPO))
REV='revision/econometrica-nbo-r62-referee-revision-2026-10-10'
READY='revision/econometrica-nbo-r62-review-ready-2026-10-10'
PUB='revision/econometrica-nbo-r62-publication-2026-10-10'
SCIENCE='d868cb5bc113e521be134cb9f50f04b5c68b3493'
FORBIDDEN={'.ttf','.otf','.woff','.woff2','.pfb','.pfa','.afm','.tfm'}

def run(args,**kw):return subprocess.check_output(args,cwd=REPO,text=True,**kw).strip()
def read(p):return json.loads(Path(p).read_text())
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def need(ok,msg):
    if not ok:raise AssertionError(msg)
def commit(message):
    run(['git','add','-f',REL,'README.md'])
    if (REPO/'ECTA.tex').exists():run(['git','add','ECTA.tex'])
    if run(['git','status','--porcelain']):run(['git','commit','-m',message])
    return run(['git','rev-parse','HEAD'])
def main():
    start=time.perf_counter();release=read(R/'audit/RELEASE62.json');need(release['status']=='passed','Publication not passed')
    run(['git','config','user.name','NBO revision verification']);run(['git','config','user.email','nbo-revision@users.noreply.github.com'])
    archive_sha=commit('R62: retain seven compiled documents, all inherited/new tests and exhaustive stored-policy replay')
    cleanlog=R/'audit/build-logs/clean-archive62.log'
    with tempfile.TemporaryDirectory(prefix='nbo-r62-clean-') as tmp:
        root=Path(tmp);archive=root/'revision.tar'
        with archive.open('wb') as out:subprocess.run(['git','archive',archive_sha,REL],cwd=REPO,stdout=out,check=True)
        subprocess.run(['tar','-xf',str(archive),'-C',str(root)],check=True)
        copy=root/REL;shutil.rmtree(copy/'build');(copy/'build').mkdir()
        for p in (copy/'tables').glob('*62.tex'):p.unlink()
        for name in ('RELEASE62.json','SCIENCE_REPLAY62.json','PUBLICATION_FACTS62.json'):
            p=copy/'audit'/name
            if p.exists():p.unlink()
        with cleanlog.open('w') as out:
            result=subprocess.run([sys.executable,str(copy/'code/build62.py')],cwd=copy,stdout=out,stderr=subprocess.STDOUT,check=False)
        if result.returncode:raise RuntimeError('Clean archive failed: '+cleanlog.read_text()[-6000:])
        rebuilt=read(copy/'audit/RELEASE62.json');first={d['document']:d for d in release['documents']};second={d['document']:d for d in rebuilt['documents']}
        checks={k:dict(pages_equal=first[k]['pages']==second[k]['pages'],extracted_text_equal=first[k]['extracted_text_sha256']==second[k]['extracted_text_sha256'],pdf_bytes_equal=first[k]['sha256']==second[k]['sha256']) for k in first}
        need(all(v['pages_equal'] and v['extracted_text_equal'] for v in checks.values()),'Clean documents differ')
        need(rebuilt['total_tests']==release['total_tests'] and rebuilt['checked_nodal_action_records']==release['checked_nodal_action_records'],'Clean verification differs')
        save(R/'audit/CLEAN_REBUILD62.json',dict(status='passed',archive_commit=archive_sha,removed_generated_pdfs=True,removed_current_tables=True,removed_volatile_current_replay=True,network_used=False,new_fitting_services=0,new_policy_cost_samples=0,document_checks=checks,rebuilt_release=rebuilt,log_sha256=digest(cleanlog)))
    (REPO/'README.md').write_text('''# Neural Bellman Operators

**Current complete referee revision: R62.**

Canonical branch: `'''+READY+'''`.

[Article](revisions/2026-10-10-r62/build/ECTA.pdf) · [Technical supplement](revisions/2026-10-10-r62/build/supp.pdf) · [Response to the referee](revisions/2026-10-10-r62/build/response.pdf)

[Revision guide](revisions/2026-10-10-r62/README.md) · [Complete development](revisions/2026-10-10-r62/build/complete.pdf) · [Complete proof companion](revisions/2026-10-10-r62/build/complete-supp.pdf)

R62 preserves the original NBO paper and develops primitive regularity and a
second-order original-optimum certificate for the actual acquired policy.
A separately frozen prospective study covers several state dimensions,
longer horizons and complete two-control economic policies. Pure and
common-augmented neural and conventional actors retain their own certificates,
direct policy-cost comparisons and full computational charges.

`revisions/2026-10-10-r62/audit/FINAL_DELIVERY62.json` binds the complete sources,
scientific records, tests, seven documents and clean offline archive rebuild.
The controlling R61 review, earlier revision branches and unfavorable results
are unchanged. The source-freeze and completed-science branches retain their
separate provenance; they are not additional independent experiments.

Offline build: `python3 revisions/2026-10-10-r62/code/build62.py`.
''')
    wrapper=REPO/'ECTA.tex'
    if wrapper.exists() and len(wrapper.read_text())<500 and 'revisions/' in wrapper.read_text():wrapper.write_text(r'\input{revisions/2026-10-10-r62/ECTA}'+'\n')
    files=[p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    need(not any(p.suffix.lower() in FORBIDDEN for p in files),'Standalone font file prohibited')
    manifest={str(p.relative_to(R)):digest(p) for p in files if p.name!='FINAL_DELIVERY62.json'}
    final=dict(status='passed',canonical_branch=READY,revision_branch=REV,publication_branch=PUB,completed_science_commit=SCIENCE,tested_source_commit=release['tested_source_commit'],clean_archive_commit=archive_sha,source_freeze_sha256=release['source_freeze_sha256'],workflow_run_id=os.getenv('GITHUB_RUN_ID'),workflow_head_sha=os.getenv('GITHUB_SHA'),file_count=len(manifest),files_sha256=manifest,documents=release['documents'],total_tests=release['total_tests'],new_R62_tests=release['new_R62_tests'],checked_nodal_action_records=release['checked_nodal_action_records'],checked_interval_records=release['checked_interval_records'],fitting_services=40,prospective_path_rows=327680,source_preservation='passed',clean_archive_rebuild='passed',publication_seconds=time.perf_counter()-start,scope='Original NBO paper revised with frozen prospective science and ordinary sources; stored-policy/inference replay and clean seven-document build verified; final manifest-containing commit is a descendant of the tested source, not a claim of external mathematical/editorial acceptance.')
    save(R/'audit/FINAL_DELIVERY62.json',final)
    for name,h in manifest.items():need(digest(R/name)==h,'Final file changed: '+name)
    sha=commit('R62: publish original-paper revision, prospective full-policy evidence and clean-archive verification')
    run(['git','push','--atomic','origin',*('HEAD:refs/heads/'+branch for branch in (REV,READY,PUB))])
    for branch in (REV,READY,PUB):need(run(['git','ls-remote','--heads','origin','refs/heads/'+branch]).startswith(sha+'\t'),'Remote ref differs: '+branch)
    print(json.dumps(dict(status='remote_publication_verified',commit=sha,branches=[REV,READY,PUB],files=len(manifest),tests=release['total_tests'],documents=[dict(name=d['document'],pages=d['pages']) for d in release['documents']]),indent=2),flush=True)
if __name__=='__main__':main()
