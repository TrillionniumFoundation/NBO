"""Clean archive and non-forced R83 publication; visual gate stays separate."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1];REPO=R.parents[1];REL=str(R.relative_to(REPO))
BRANCH='revision/econometrica-nbo-r83-referee-revision-2026-10-12'
SOURCE='revision/econometrica-nbo-r83-source-2026-10-12'
CANDIDATE='revision/econometrica-nbo-r83-publication-candidate-2026-10-12'
DEPS=[f'revisions/2026-10-10-r{n}' for n in (62,63,64,65,66,67)]+[f'revisions/2026-10-11-r{n}' for n in (69,70,72,73,77,78)]+[f'revisions/2026-10-12-r{n}' for n in (80,81,82,83)]
def run(args):return subprocess.check_output(args,cwd=REPO,text=True).strip()
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
def commit(message):
    run(['git','add','-A','-f',REL,'README.md'])
    if run(['git','diff','--cached','--name-only']):run(['git','commit','-m',message])
    return run(['git','rev-parse','HEAD'])
def main():
    start=time.perf_counter();release=json.loads((R/'audit/RELEASE83.json').read_text())
    if release['status']!='passed':raise AssertionError('Failed complete build')
    run(['git','config','user.name','NBO revision verification']);run(['git','config','user.email','nbo-revision@users.noreply.github.com'])
    initial=commit('R83: retain complete ordinary manuscript, source-bound recovery, every test and four compiled documents')
    for path in DEPS:
        if not (REPO/path).exists():raise FileNotFoundError(path)
    cleanlog=R/'audit/build-logs/clean-archive83.log'
    with tempfile.TemporaryDirectory(prefix='nbo-r83-clean-') as temp:
        root=Path(temp);archive=root/'source.tar'
        with archive.open('wb') as stream:subprocess.run(['git','archive',initial,*DEPS],cwd=REPO,stdout=stream,check=True)
        subprocess.run(['tar','-xf',str(archive),'-C',str(root)],check=True)
        copy=root/REL;shutil.rmtree(copy/'build');(copy/'build').mkdir()
        for path in (copy/'tables').glob('*8[23].tex'):path.unlink()
        (copy/'results83/frontier.json').unlink();(copy/'results83/transfer.json').unlink()
        with cleanlog.open('w') as out:
            status=subprocess.run([sys.executable,str(copy/'code/build83.py')],cwd=copy,stdout=out,stderr=subprocess.STDOUT,check=False)
        if status.returncode:raise RuntimeError('Clean archive failed: '+cleanlog.read_text(errors='replace')[-9000:])
        second=json.loads((copy/'audit/RELEASE83.json').read_text())
        original={x['document']:x for x in release['documents']};other={x['document']:x for x in second['documents']}
        matches={name:dict(pages_equal=doc['pages']==other[name]['pages'],text_equal=doc['text_sha256']==other[name]['text_sha256'],pdf_bytes_equal=doc['sha256']==other[name]['sha256']) for name,doc in original.items()}
        if not all(x['pages_equal'] and x['text_equal'] for x in matches.values()):raise AssertionError(matches)
        if second['total_tests']!=release['total_tests'] or second['frontier_sha256']!=release['frontier_sha256'] or second['transfer_sha256']!=release['transfer_sha256']:raise AssertionError('Clean tests or exact economic objects differ')
        if sha(copy/'results83/EXECUTION83.json')!=release['execution83_sha256']:raise AssertionError('Clean build retimed execution')
        save(R/'audit/CLEAN_REBUILD83.json',dict(status='passed',archive_commit=initial,removed_generated_pdfs=True,removed_new_tables=True,removed_derived_economic_results=True,
            complete_builder_reexecuted=True,new_observations=0,source_network_access_by_builder=False,document_matches=matches,clean_release=second,clean_log_sha256=sha(cleanlog)))
    (REPO/'README.md').write_text('''# Neural Bellman Operators

R83 publication candidate: `'''+CANDIDATE+'''`.

The complete ordinary-source manuscript is in revisions/2026-10-12-r83.
Its main paper, Technical Supplement, Numerical and Development Appendix and
point-by-point referee response retain the original NBO topic and every
inherited active section. New actionwise transfer and economic stopping
frontiers are proved and independently checked under the original law.

Full build and clean-archive reproduction have passed. Final visual
qualification and a hash-bound FINAL_DELIVERY83 manifest are separate gates;
this intermediate candidate is not review-ready merely because it compiled.
The R82 failed attempt and all older branches remain unchanged.
''')
    manifest={str(path.relative_to(R)):sha(path) for path in R.rglob('*') if path.is_file() and '__pycache__' not in path.parts and path.name!='PUBLICATION_CANDIDATE83.json'}
    for name in manifest:
        if Path(name).suffix.lower() in {'.ttf','.otf','.woff','.woff2','.pfb','.pfa','.afm','.tfm'}:raise AssertionError('Standalone font file')
    save(R/'audit/PUBLICATION_CANDIDATE83.json',dict(status='build_and_clean_reproduction_passed_visual_pending',tested_source_commit=release['tested_source_commit'],clean_archive_commit=initial,
        workflow_run_id=os.getenv('GITHUB_RUN_ID'),documents=release['documents'],total_tests=release['total_tests'],source_freeze83_sha256=release['source_freeze83_sha256'],
        file_sha256=manifest,file_count=len(manifest),new_cost_rows=0,new_fits=0,publication_seconds=time.perf_counter()-start))
    final=commit('R83: qualify publication candidate with complete clean-archive reproduction and evidence hashes')
    run(['git','push','--atomic','origin',*['HEAD:refs/heads/'+name for name in (BRANCH,SOURCE,CANDIDATE)]])
    for name in (BRANCH,SOURCE,CANDIDATE):
        if not run(['git','ls-remote','--heads','origin','refs/heads/'+name]).startswith(final+'\t'):raise AssertionError('Remote branch differs '+name)
    print(json.dumps(dict(status='candidate_remote_verified',commit=final,branches=[BRANCH,SOURCE,CANDIDATE],tests=release['total_tests']),indent=2))
if __name__=='__main__':main()
