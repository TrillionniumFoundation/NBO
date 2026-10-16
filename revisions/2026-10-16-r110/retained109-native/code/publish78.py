"""Clean archive build and non-forced publication of a compiled R78 candidate.

The review-ready branch is deliberately not created here. It requires a later
human/assistant inspection record tied to these exact PDF hashes.
"""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1];REPO=R.parents[1];REL=str(R.relative_to(REPO))
BRANCH='revision/econometrica-nbo-r78-referee-revision-2026-10-11'
SOURCE='revision/econometrica-nbo-r78-source-2026-10-11'
DEPENDENCIES=[f'revisions/2026-10-10-r{n}' for n in (62,63,64,65,66,67)]+[f'revisions/2026-10-11-r{n}' for n in (69,70,72,73,77,78)]

def run(args):return subprocess.check_output(args,cwd=REPO,text=True).strip()
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):Path(p).write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def commit(msg):
    run(['git','add','-f',REL])
    if run(['git','diff','--cached','--name-only']):run(['git','commit','-m',msg])
    return run(['git','rev-parse','HEAD'])

def main():
    begin=time.perf_counter();release=json.loads((R/'audit/RELEASE78.json').read_text())
    if release['status']!='passed':raise AssertionError('Full build is not passed')
    archive_sha=commit('R78: retain four compiled documents, full dual-arithmetic replay and sharp-choice audit')
    logfile=R/'audit/build-logs/clean-archive78.log'
    with tempfile.TemporaryDirectory(prefix='nbo-r78-clean-') as tmp:
        root=Path(tmp);tar=root/'source.tar'
        with tar.open('wb') as out:subprocess.run(['git','archive',archive_sha,*DEPENDENCIES],cwd=REPO,stdout=out,check=True)
        subprocess.run(['tar','-xf',str(tar),'-C',str(root)],check=True);tar.unlink()
        clean=root/REL
        import shutil
        shutil.rmtree(clean/'build');(clean/'build').mkdir()
        for p in (clean/'tables').glob('*78*'):p.unlink()
        with logfile.open('w') as out:
            proc=subprocess.run([sys.executable,str(clean/'code/build78.py')],cwd=clean,stdout=out,stderr=subprocess.STDOUT)
        if proc.returncode:raise RuntimeError('Clean build failed:\n'+logfile.read_text()[-16000:])
        rebuilt=json.loads((clean/'audit/RELEASE78.json').read_text())
        if rebuilt['total_tests']!=release['total_tests']:raise AssertionError('Clean test count differs')
        pairs=[]
        for old,new in zip(release['documents'],rebuilt['documents']):
            if old['document']!=new['document'] or old['text_sha256']!=new['text_sha256'] or old['pages']!=new['pages']:raise AssertionError('Clean document mismatch')
            pairs.append(dict(document=old['document'],pages=old['pages'],text_equal=True,pdf_bytes_equal=old['sha256']==new['sha256']))
        olddecision=json.loads((R/'audit/DECISION78.json').read_text());newdecision=json.loads((clean/'audit/DECISION78.json').read_text())
        olddecision.pop('seconds');newdecision.pop('seconds')
        if olddecision!=newdecision:raise AssertionError('Clean exact decision mismatch')
        save(R/'audit/CLEAN_REBUILD78.json',dict(status='passed',archive_commit=archive_sha,documents=pairs,
            total_tests=rebuilt['total_tests'],exact_decision_equal=True,removed_generated_pdfs=True,
            removed_generated_tables78=True,network_used_by_builder=False,new_simulation_rows=0,
            build_seconds=rebuilt['seconds'],log_sha256=sha(logfile)))
    candidate=dict(status='compiled_and_clean_rebuilt_pending_visual_inspection',
        source_commit=release['tested_source_commit'],archive_commit=archive_sha,
        workflow_run_id=os.getenv('GITHUB_RUN_ID'),documents=release['documents'],total_tests=release['total_tests'],
        full_cost_replay='passed',clean_rebuild='passed',preservation='passed',new_simulation_rows=0,
        seconds=time.perf_counter()-begin,review_ready=False)
    save(R/'audit/CANDIDATE78.json',candidate)
    shahead=commit('R78: bind clean offline reproduction and await hash-bound PDF inspection')
    run(['git','push','--atomic','origin','HEAD:refs/heads/'+BRANCH,'HEAD:refs/heads/'+SOURCE])
    for branch in (BRANCH,SOURCE):
        if not run(['git','ls-remote','--heads','origin','refs/heads/'+branch]).startswith(shahead+'\t'):raise AssertionError('Remote ref mismatch')
    print(json.dumps(dict(status='compiled_candidate_remotely_verified',head=shahead,branches=[BRANCH,SOURCE],documents=release['documents']),indent=2),flush=True)
if __name__=='__main__':main()
