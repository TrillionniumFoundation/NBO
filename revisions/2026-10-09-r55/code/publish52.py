"""Independent clean-archive verification and additive remote publication."""
from pathlib import Path
import hashlib,io,json,os,shutil,subprocess,sys,tarfile,tempfile
R=Path(__file__).resolve().parents[1]
ROOT=R.parents[1]
REL=str(R.relative_to(ROOT))
BRANCH='revision/econometrica-nbo-r52-source-2026-10-08'
READY='revision/econometrica-nbo-r52-review-ready-2026-10-08'
def run(args,**kw):return subprocess.run(args,check=True,**kw)
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def main():
    release=json.loads((R/'audit/RELEASE52.json').read_text())
    if release['status']!='passed' or release['total_tests']!=54:raise AssertionError('Publication gate incomplete')
    run(['git','add','-f',REL],cwd=ROOT)
    run(['git','commit','-m','R52: commit complete source-bound robustness evidence and five compiled documents'],cwd=ROOT)
    candidate=git('rev-parse','HEAD');tree=git('rev-parse','HEAD^{tree}')
    archive=subprocess.check_output(['git','archive','HEAD',REL],cwd=ROOT)
    with tempfile.TemporaryDirectory(prefix='nbo-r52-clean-') as temp:
        clean=Path(temp)
        with tarfile.open(fileobj=io.BytesIO(archive)) as t:
            for m in t.getmembers():
                if Path(m.name).is_absolute() or '..' in Path(m.name).parts or not(m.isfile() or m.isdir()):raise ValueError('Unsafe archive member')
            t.extractall(clean)
        C=clean/REL
        for n in ('build','tables','audit/build-logs'):
            shutil.rmtree(C/n,ignore_errors=True)
        for p in C.rglob('__pycache__'):shutil.rmtree(p)
        with (R/'audit/clean-build52.log').open('w') as log:
            run([sys.executable,str(C/'code/build52.py')],cwd=clean,stdout=log,stderr=subprocess.STDOUT)
        second=json.loads((C/'audit/RELEASE52.json').read_text())
        if second['total_tests']!=54 or second['new_record_audit']!=release['new_record_audit']:raise AssertionError('Clean rebuild disagrees')
        for p in (R/'tables').glob('*.tex'):
            if sha(p)!=sha(C/'tables'/p.name):raise AssertionError('Changed generated table: '+p.name)
        texts={}
        for n in ('ECTA','supp','complete','complete-supp','response'):
            a=subprocess.check_output(['pdftotext',str(R/'build'/(n+'.pdf')),'-'])
            b=subprocess.check_output(['pdftotext',str(C/'build'/(n+'.pdf')),'-'])
            if a!=b:raise AssertionError('Clean PDF text differs: '+n)
            texts[n]=hashlib.sha256(a).hexdigest()
        save(R/'audit/CLEAN_ARCHIVE52.json',{'status':'passed','candidate_commit':candidate,'candidate_tree':tree,
            'deleted_before_rebuild':['build','tables','audit/build-logs','all __pycache__'],
            'tests':54,'all_generated_tables_identical':True,'pdf_text_sha256':texts,
            'scientific_services_rerun':False,'network_used_by_builder':False})
    delivered={str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='FINAL_DELIVERY52.json'}
    save(R/'audit/FINAL_DELIVERY52.json',{'status':'complete_source_bound_submission','candidate_commit':candidate,'candidate_tree':tree,
         'predecessor_commit':'62ffa8d0753c82a1363831f49a297c815d89204f',
         'review_commit':'2822f50100c7a53ec5fe07d39e9b37d487ab0547',
         'substantive_review_commit':'4708450610c38e6b8963670cecadc887508c85c0',
         'science_source_commit':json.loads((R/'audit/SOURCE_FREEZE52.json').read_text())['source_commit'],
         'tests':54,'new_cells_audited':524288,'new_independent_cost_estimands':0,
         'clean_archive_passed':True,'pdf_sha256':{n:sha(R/'build'/(n+'.pdf')) for n in texts},
         'files':delivered,'canonical_branch':READY,'github_run_id':os.environ.get('GITHUB_RUN_ID'),
         'identity_note':'The final remote Git head includes this record. It is not self-hashed; candidate sources and current output hashes are explicit.'})
    (ROOT/'README.md').write_text('# Neural Bellman Operators\n\n**Authoritative complete referee revision: R52.**\n\nCanonical branch: `'+READY+'`.\n\n[Main paper]('+REL+'/build/ECTA.pdf) · [Supplement]('+REL+'/build/supp.pdf) · [Referee response]('+REL+'/build/response.pdf)\n\n[Revision guide]('+REL+'/README.md) · [Complete development]('+REL+'/build/complete.pdf) · [Complete supplement]('+REL+'/build/complete-supp.pdf)\n\nR52 adds proved action-contrast accuracy and coupled-residual certificates, and an exhaustive original-economy robustness ablation. The original title, model, broad theory, applications and adverse evidence are retained. All inherited and new tests, source/evidence checks, five-document compilation and clean archive reproduction are bound by `'+REL+'/audit/FINAL_DELIVERY52.json`. The older branches are unchanged.\n\nOffline build: `python '+REL+'/code/build52.py`.\n')
    run(['git','add','-f',REL,'README.md'],cwd=ROOT)
    run(['git','commit','-m','R52: bind independent clean rebuild and publish complete referee-ready manuscript'],cwd=ROOT)
    head=git('rev-parse','HEAD')
    existing=git('ls-remote','--heads','origin','refs/heads/'+READY)
    if existing:raise RuntimeError('Refusing to overwrite an existing review-ready branch')
    run(['git','push','--atomic','origin',f'HEAD:refs/heads/{BRANCH}',f'HEAD:refs/heads/{READY}'],cwd=ROOT)
    for branch in (BRANCH,READY):
        if git('ls-remote','--heads','origin','refs/heads/'+branch).split()[0]!=head:raise AssertionError('Remote head mismatch')
    print(json.dumps({'status':'remote_verified','head':head,'source_branch':BRANCH,'review_ready_branch':READY},indent=2))
if __name__=='__main__':main()
