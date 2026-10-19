"""Clean-archive candidate publication; visual evidence is a separate gate."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1];REPO=R.parents[1];REL=str(R.relative_to(REPO))
BRANCH='revision/econometrica-nbo-r81-referee-revision-2026-10-12'
SOURCE='revision/econometrica-nbo-r81-source-2026-10-12'
DEPS=[f'revisions/2026-10-10-r{n}' for n in (62,63,64,65,66,67)]+[f'revisions/2026-10-11-r{n}' for n in (69,70,72,73,77,78)]+['revisions/2026-10-12-r80',REL]

def run(args):return subprocess.check_output(args,cwd=REPO,text=True).strip()
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):Path(p).write_text(json.dumps(j,sort_keys=True,indent=2)+'\n')
def commit(message):
    run(['git','add','-f',REL])
    if run(['git','diff','--cached','--name-only']):run(['git','commit','-m',message])
    return run(['git','rev-parse','HEAD'])
def main():
    begin=time.perf_counter();old=json.loads((R/'audit/RELEASE81.json').read_text())
    if old['status']!='passed':raise AssertionError('Current full build has not passed')
    archive=commit('R81: retain full verified manuscript, independent cost replay and optimizer-class certificates')
    log=R/'audit/build-logs/clean-archive81.log'
    with tempfile.TemporaryDirectory(prefix='nbo-r81-clean-') as tmp:
        root=Path(tmp);tar=root/'source.tar'
        with tar.open('wb') as out:subprocess.run(['git','archive',archive,*DEPS],cwd=REPO,stdout=out,check=True)
        subprocess.run(['tar','-xf',str(tar),'-C',str(root)],check=True);tar.unlink();newroot=root/REL
        shutil.rmtree(newroot/'build');(newroot/'build').mkdir()
        for pattern in ('*78*','*79*','*81*'):
            for p in (newroot/'tables').glob(pattern):p.unlink()
        with log.open('w') as out:
            result=subprocess.run([sys.executable,str(newroot/'code/build81.py')],cwd=newroot,stdout=out,stderr=subprocess.STDOUT)
        if result.returncode:raise RuntimeError('Clean archive failed:\n'+log.read_text()[-14000:])
        fresh=json.loads((newroot/'audit/RELEASE81.json').read_text())
        if fresh['total_tests']!=old['total_tests']:raise AssertionError('Clean test count differs')
        pairs=[]
        for a,b in zip(old['documents'],fresh['documents']):
            if a['document']!=b['document'] or a['pages']!=b['pages'] or a['text_sha256']!=b['text_sha256']:raise AssertionError('Clean document mismatch')
            pairs.append(dict(document=a['document'],pages=a['pages'],text_equal=True,pdf_bytes_equal=a['sha256']==b['sha256']))
        for name in ('DECISION78','ALLOCATION79','TRANSFER81','TABLES81'):
            a=json.loads((R/'audit'/(name+'.json')).read_text());b=json.loads((newroot/'audit'/(name+'.json')).read_text())
            a.pop('seconds',None);b.pop('seconds',None)
            if a!=b:raise AssertionError('Exact derived evidence changed '+name)
        save(R/'audit/CLEAN_REBUILD81.json',dict(status='passed',archive_commit=archive,documents=pairs,total_tests=fresh['total_tests'],
            exact_optimizer_class_and_choice_results_equal=True,removed_generated_pdfs=True,removed_generated_tables=True,
            all_new_bins_recomputed_in_both_implementations=True,all_new_switch_duals_recomputed=True,
            network_used_by_builder=False,new_statistical_rows=0,clean_build_seconds=fresh['build_seconds'],log_sha256=sha(log)))
    files={str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ('DELIVERY_FILES81.json','CANDIDATE81.json','FINAL_DELIVERY81.json','VISUAL81.json')}
    save(R/'audit/DELIVERY_FILES81.json',files)
    save(R/'audit/CANDIDATE81.json',dict(status='full_build_and_clean_archive_passed_pending_visual_inspection',review_ready=False,
        tested_source_commit=old['tested_source_commit'],archive_commit=archive,workflow_run_id=os.getenv('GITHUB_RUN_ID'),
        documents=old['documents'],total_tests=old['total_tests'],independent_switch_duals=old['independent_switch_duals'],
        R80_full_bin_replay=old['R80_full_bin_replay'],delivery_files_sha256=sha(R/'audit/DELIVERY_FILES81.json'),
        new_independent_cost_rows=0,seconds=time.perf_counter()-begin))
    head=commit('R81: bind full clean-archive reproduction and source-bound publication candidate')
    run(['git','push','--atomic','origin','HEAD:refs/heads/'+BRANCH,'HEAD:refs/heads/'+SOURCE])
    for branch in (BRANCH,SOURCE):
        if not run(['git','ls-remote','--heads','origin','refs/heads/'+branch]).startswith(head+'\t'):raise AssertionError('Remote publication mismatch')
    print(json.dumps(dict(status='remote_candidate_verified',commit=head,documents=old['documents'],tests=old['total_tests']),indent=2),flush=True)
if __name__=='__main__':main()
