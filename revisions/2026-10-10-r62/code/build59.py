"""Offline R59 audit and seven-document publication.

The full build reconstructs saved scientific records without retraining.
--publication-only checks their binding and rebuilds the documents; it does
not describe cached scientific verification as a new execution.
"""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys,time
import build as b
import build57 as previous
from assemble56 import labels
R=Path(__file__).resolve().parents[1];DOCS=previous.DOCS

def read(p):return json.loads(p.read_text())
def binding_files():
    files=previous.binding_files()
    for folder in ('results58','preserved'):
        for p in (R/folder).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts:files[str(p.relative_to(R))]=b.digest(p)
    for name in ('response59.md','COMMON_ACCURACY_AMENDMENT.md','NUMERICAL_CORRECTION.md'):
        if (R/name).exists():files[name]=b.digest(R/name)
    return files

def main(publication_only=False):
    start=time.perf_counter()
    for folder in ('build','tables','audit/build-logs'):(R/folder).mkdir(parents=True,exist_ok=True)
    assembly=read(R/'audit/ASSEMBLY59.json')
    for name,h in assembly['retained_sha256'].items():
        if b.digest(R/name)!=h:raise AssertionError('R58 protected source/evidence changed: '+name)
    import study58
    freeze=study58.verify()
    tests={name:b.tests([sys.executable,'code/'+file],name) for name,file in [('lossless_screen58','tests58.py'),('lossless_transcript59','tests59.py')]}
    if publication_only:
        binding=read(R/'audit/SCIENCE_BINDING59.json')
        if binding['files_sha256']!=binding_files():raise AssertionError('R59 scientific source/evidence binding differs')
        if b.digest(R/'audit/RESULT_AUDIT59.json')!=binding['result_audit_sha256']:raise AssertionError('R59 replay record replaced')
    else:b.run([sys.executable,'code/audit59.py'],'scientific-replay59')
    b.run([sys.executable,'code/tables59.py'],'publication-tables59')
    previous.main(publication_only=publication_only)
    inherited=read(R/'audit/RELEASE57.json')
    # Only the current response frontmatter is generated here. The body and
    # original article sources are ordinary committed documents.
    b.response();file=R/'response.tex';text=file.read_text()
    abstract='Revision R59 responds to the 9 October 2026 advisory report on R54. The original Neural Bellman Operators paper retains its constructive and economic targets and adds lossless trained-neural action search, prospective transcript invariance and complete matched-work evidence from the separately frozen R58 execution.'
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+abstract+m[2],text,count=1,flags=re.S);file.write_text(text)
    response=b.compile_document('response');docs=[response if x['document']=='response' else x for x in inherited['documents']]
    for doc in docs:
        raw=subprocess.check_output(['pdftotext','-layout',str(R/'build'/(doc['document']+'.pdf')),'-'])
        doc['extracted_text_sha256']=hashlib.sha256(raw).hexdigest();(R/'build'/(doc['document']+'.txt')).write_bytes(raw)
    preservation={}
    for name,old in assembly['baseline_labels'].items():
        now=set(labels(R,name));missing=sorted(set(old)-now)
        if missing:raise AssertionError((name,'Missing inherited labels',missing))
        preservation[name]=dict(inherited_labels=len(old),current_labels=len(now),missing=[])
    for name,h in assembly['retained_sha256'].items():
        if b.digest(R/name)!=h:raise AssertionError('Protected file changed during build: '+name)
    result=read(R/'audit/RESULT_AUDIT59.json')
    if result['status']!='passed' or result['services']!=36 or not result['all_exact_policy_identities']:raise AssertionError('Incomplete matched execution replay')
    if not publication_only:
        b.write_json(R/'audit/SCIENCE_BINDING59.json',dict(files_sha256=binding_files(),result_audit_sha256=b.digest(R/'audit/RESULT_AUDIT59.json'),scope='Ordinary current sources and complete frozen scientific source/result records bound after full reconstruction; derived publication tables are regenerated.'))
    try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:commit=None
    report=dict(status='passed',source_commit=commit,baseline_commit=assembly['baseline_commit'],controlling_review_commit=assembly['controlling_review_commit'],documents=docs,tests={**inherited['tests'],**tests},total_tests=inherited['total_tests']+sum(x['tests'] for x in tests.values()),new_theorem_tests=tests['lossless_transcript59']['tests'],preservation=preservation,protected_files=len(assembly['retained_sha256']),scientific_source_freeze_sha256=freeze,matched_services=result['services'],attained=result['attained'],budget_exhausted=result['budget_exhausted'],all_exact_policy_identities=result['all_exact_policy_identities'],replay_counts=result['counts'],inherited_release_sha256=b.digest(R/'audit/RELEASE57.json'),result_audit_sha256=b.digest(R/'audit/RESULT_AUDIT59.json'),science_binding_sha256=b.digest(R/'audit/SCIENCE_BINDING59.json'),new_training_services=0,new_independent_path_observations=0,original_clocks_replaced=False,publication_only=publication_only,build_seconds=time.perf_counter()-start,network_used_by_builder=False,typography_scope='Seven complete document compilation logs, extracted text and output hashes. Visual inspection is recorded separately when performed.',scope='Original NBO paper, inherited test/audit chain and complete R58 matched-work reconstruction. Repeated inputs are identity-checked; this is not an external mathematical or editorial approval.')
    b.write_json(R/'audit/RELEASE59.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('tests','preservation','documents')},indent=2))
    print(json.dumps([dict(document=x['document'],pages=x['pages']) for x in docs],indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--publication-only',action='store_true');main(parser.parse_args().publication_only)
