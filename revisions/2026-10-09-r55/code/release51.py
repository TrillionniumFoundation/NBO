"""Publish only after an independent, offline Git-archive rebuild succeeds."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tarfile,tempfile
R=Path(__file__).resolve().parents[1]
ROOT=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],text=True).strip())
REL=str(R.relative_to(ROOT))
SOURCE='revision/econometrica-nbo-r51-integrated-source-2026-10-08'
READY='revision/econometrica-nbo-r51-review-ready-2026-10-08'
REVIEW='2822f50100c7a53ec5fe07d39e9b37d487ab0547'
FORBIDDEN={'.ttf','.otf','.woff','.woff2','.pfb','.pfa','.afm','.tfm'}
def call(args,**kwargs):return subprocess.check_output(args,text=True,cwd=ROOT,**kwargs).strip()
def run(args,**kwargs):subprocess.run(args,check=True,cwd=ROOT,**kwargs)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def push(branches):
    run(['git','push','--atomic','origin']+['HEAD:refs/heads/'+n for n in branches])
    head=call(['git','rev-parse','HEAD'])
    rows=call(['git','ls-remote','--heads','origin']+['refs/heads/'+n for n in branches]).splitlines()
    actual={line.split()[1]:line.split()[0] for line in rows}
    if any(actual.get('refs/heads/'+n)!=head for n in branches):raise RuntimeError('Remote ref verification failed')
    return head,actual

def main():
    report=json.loads((R/'audit/RELEASE51.json').read_text())
    if report['status']!='source_bound_build_passed' or report['total_tests']<44:raise RuntimeError('Publication tests not complete')
    for p in R.rglob('*'):
        if p.is_file() and p.suffix.lower() in FORBIDDEN:raise RuntimeError('Prohibited font file '+str(p))
    old={n:(ROOT/n).read_text() for n in ('README.md','ECTA.tex','supp.tex')}
    save(R/'audit/ROOT_NAVIGATION_BEFORE51.json',old)
    (ROOT/'README.md').write_text('# Neural Bellman Operators\n\n**Authoritative referee revision: R51.**\n\nCanonical complete branch: `'+READY+'`.\n\n[Main paper]('+REL+'/build/ECTA.pdf) · [Supplement]('+REL+'/build/supp.pdf) · [Referee response]('+REL+'/build/response.pdf)\n\n[Revision guide]('+REL+'/README.md) · [Complete development]('+REL+'/build/complete.pdf) · [Complete supplement]('+REL+'/build/complete-supp.pdf)\n\nThe original topic, theory, applications and historical adverse evidence are retained. R51 adds finite-sweep incumbent-preserving accuracy theorems and integrates a source-bound reproduction of the recovered cost-directed study. The source, numerical evidence, tests, independent clean-archive rebuild and compiled papers are bound by `'+REL+'/audit/FINAL_DELIVERY51.json`. Earlier revision and review branches are unchanged.\n\nBuild offline with `python '+REL+'/code/build51.py`.\n')
    for n in ('ECTA','supp'):(ROOT/(n+'.tex')).write_text('\\input{'+REL+'/'+n+'.tex}\n')
    run(['git','add',REL,'README.md','ECTA.tex','supp.tex'])
    if call(['git','diff','--cached','--name-only','--diff-filter=D']):raise RuntimeError('Refusing historical deletions')
    run(['git','commit','-m','R51: integrate complete NBO manuscript, sharp finite-sweep proofs, reproduced evidence and PDFs'])
    candidate=call(['git','rev-parse','HEAD']);tree=call(['git','rev-parse','HEAD^{tree}'])
    before={str(p.relative_to(R)):sha(p) for p in R.rglob('*.tex') if not any(q in p.parts for q in ('build','audit'))}
    docs=('ECTA','supp','complete','complete-supp','response')
    text_before={n:hashlib.sha256(subprocess.check_output(['pdftotext','-layout',str(R/'build'/(n+'.pdf')),'-'])).hexdigest() for n in docs}
    with tempfile.TemporaryDirectory(prefix='nbo-r51-clean-') as tmp:
        tmp=Path(tmp);archive=tmp/'candidate.tar'
        with archive.open('wb') as f:run(['git','archive',candidate,REL],stdout=f)
        with tarfile.open(archive) as tar:tar.extractall(tmp,filter='data')
        clean=tmp/REL
        with (R/'audit/clean-archive51.log').open('w') as log:
            run([sys.executable,str(clean/'code/build51.py')],stdout=log,stderr=subprocess.STDOUT)
        clean_report=json.loads((clean/'audit/RELEASE51.json').read_text())
        if clean_report['total_tests']!=report['total_tests']:raise RuntimeError('Clean test count differs')
        changed=[n for n,h in before.items() if sha(clean/n)!=h]
        if changed:raise RuntimeError('Clean generated source mismatch: '+str(changed))
        text_after={n:hashlib.sha256(subprocess.check_output(['pdftotext','-layout',str(clean/'build'/(n+'.pdf')),'-'])).hexdigest() for n in docs}
        if text_after!=text_before:raise RuntimeError('Clean PDF text mismatch')
        manifest=json.loads((R/'audit/PUBLICATION_FILES51.json').read_text())
        if any(sha(clean/n)!=h for n,h in manifest.items()):raise RuntimeError('Clean source/evidence manifest mismatch')
        save(R/'audit/CLEAN_ARCHIVE51.json',dict(status='passed',candidate_commit=candidate,candidate_tree=tree,archive_sha256=sha(archive),source_tex_files_identical=len(before),source_evidence_files_checked=len(manifest),pdf_text_sha256=text_after,compilation=clean_report['compilation'],total_tests=clean_report['total_tests'],network_used_by_rebuild=False,historical_timing_reexecuted=False))
    excluded={'audit/DELIVERY_MANIFEST51.json','audit/FINAL_DELIVERY51.json','audit/REMOTE_RECEIPT51.json'}
    files={str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and str(p.relative_to(R)) not in excluded and '__pycache__' not in p.parts}
    save(R/'audit/DELIVERY_MANIFEST51.json',files)
    save(R/'audit/FINAL_DELIVERY51.json',dict(status='complete_source_bound_submission',candidate_commit=candidate,candidate_tree=tree,review_commit=REVIEW,science_source_commit=os.environ.get('NBO_SCIENCE_SOURCE'),intended_branches=[SOURCE,READY],files=len(files),manifest_sha256=sha(R/'audit/DELIVERY_MANIFEST51.json'),main_sha256=sha(R/'ECTA.tex'),supplement_sha256=sha(R/'supp.tex'),response_sha256=sha(R/'response.md'),pdf_sha256={n:sha(R/'build'/(n+'.pdf')) for n in docs},total_tests=report['total_tests'],clean_archive_passed=True,known_design_reproduction=True,new_statistical_sample_size_claimed=False,remote_delivery_record='REMOTE_RECEIPT51.json records the observed first published head; the final Git head also contains that receipt'))
    run(['git','add',REL+'/audit']);run(['git','commit','-m','R51: bind independent clean rebuild and complete publication manifest'])
    head,actual=push([SOURCE,READY])
    save(R/'audit/REMOTE_RECEIPT51.json',dict(observed_published_head=head,observed_refs=actual,publication_gate_passed=True,force_push_used=False,scope='Receipt observes the complete publication parent; this receipt is the only subsequent bookend addition'))
    run(['git','add',REL+'/audit/REMOTE_RECEIPT51.json']);run(['git','commit','-m','R51: record verified remote publication receipt'])
    final,actual=push([SOURCE,READY])
    print(json.dumps(dict(final_head=final,verified_refs=actual,total_tests=report['total_tests']),indent=2))
if __name__=='__main__':main()
