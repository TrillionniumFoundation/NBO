"""Clean-archive R79 candidate publication; visual inspection is a later explicit gate."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1];REPO=R.parents[1];REL=str(R.relative_to(REPO))
BRANCH='revision/econometrica-nbo-r79-referee-revision-2026-10-12'
SOURCE='revision/econometrica-nbo-r79-source-2026-10-12'
DEPS=[f'revisions/2026-10-10-r{n}' for n in (62,63,64,65,66,67)]+[f'revisions/2026-10-11-r{n}' for n in (69,70,72,73,77,78)]+[REL]
def run(args):return subprocess.check_output(args,cwd=REPO,text=True).strip()
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):Path(p).write_text(json.dumps(j,sort_keys=True,indent=2)+'\n')
def commit(msg):
    run(['git','add','-f',REL])
    if run(['git','diff','--cached','--name-only']):run(['git','commit','-m',msg])
    return run(['git','rev-parse','HEAD'])
def main():
    start=time.perf_counter();old=json.loads((R/'audit/RELEASE79.json').read_text())
    if old['status']!='passed':raise AssertionError('No passed full release')
    archive=commit('R79: retain full inherited verification, exact deployment certificates and four compiled documents')
    log=R/'audit/build-logs/clean-archive79.log'
    with tempfile.TemporaryDirectory(prefix='nbo-r79-clean-') as tmp:
        root=Path(tmp);tar=root/'source.tar'
        with tar.open('wb') as out:subprocess.run(['git','archive',archive,*DEPS],cwd=REPO,stdout=out,check=True)
        subprocess.run(['tar','-xf',str(tar),'-C',str(root)],check=True);tar.unlink();newroot=root/REL
        shutil.rmtree(newroot/'build');(newroot/'build').mkdir()
        for pattern in ('*78*','*79*'):
            for p in (newroot/'tables').glob(pattern):p.unlink()
        with log.open('w') as out:proc=subprocess.run([sys.executable,str(newroot/'code/build79.py')],cwd=newroot,stdout=out,stderr=subprocess.STDOUT)
        if proc.returncode:raise RuntimeError('Clean reproduction failed:\n'+log.read_text()[-14000:])
        fresh=json.loads((newroot/'audit/RELEASE79.json').read_text())
        if fresh['total_tests']!=old['total_tests']:raise AssertionError('Clean test count differs')
        pairs=[]
        for a,b in zip(old['documents'],fresh['documents']):
            if a['document']!=b['document'] or a['pages']!=b['pages'] or a['text_sha256']!=b['text_sha256']:raise AssertionError('Clean document differs')
            pairs.append(dict(document=a['document'],pages=a['pages'],text_equal=True,pdf_bytes_equal=a['sha256']==b['sha256']))
        for name in ('DECISION78','ALLOCATION79'):
            a=json.loads((R/'audit'/(name+'.json')).read_text());b=json.loads((newroot/'audit'/(name+'.json')).read_text())
            a.pop('seconds',None);b.pop('seconds',None)
            if a!=b:raise AssertionError('Exact decision changed in clean rebuild '+name)
        save(R/'audit/CLEAN_REBUILD79.json',dict(status='passed',archive_commit=archive,documents=pairs,
            total_tests=fresh['total_tests'],pure_and_mixed_exact_results_equal=True,removed_generated_pdfs=True,
            removed_generated_choice_tables=True,network_used_by_builder=False,new_simulation_rows=0,
            clean_build_seconds=fresh['seconds'],log_sha256=sha(log)))
    save(R/'audit/CANDIDATE79.json',dict(status='compiled_and_clean_rebuilt_pending_visual_inspection',
        source_commit=old['tested_source_commit'],archive_commit=archive,workflow_run_id=os.getenv('GITHUB_RUN_ID'),
        documents=old['documents'],total_tests=old['total_tests'],new_simulation_rows=0,review_ready=False,seconds=time.perf_counter()-start))
    head=commit('R79: bind clean offline reproduction pending hash-bound PDF inspection')
    run(['git','push','--atomic','origin','HEAD:refs/heads/'+BRANCH,'HEAD:refs/heads/'+SOURCE])
    for branch in (BRANCH,SOURCE):
        if not run(['git','ls-remote','--heads','origin','refs/heads/'+branch]).startswith(head+'\t'):raise AssertionError('Remote ref mismatch')
    print(json.dumps(dict(status='remote_candidate_verified',commit=head,documents=old['documents'],tests=old['total_tests']),indent=2),flush=True)
if __name__=='__main__':main()
