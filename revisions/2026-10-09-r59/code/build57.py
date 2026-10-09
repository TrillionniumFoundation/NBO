"""Offline R57 scientific verification and ordinary-source publication.

--publication-only checks source/result bindings, reruns tests and regenerates
all documents. It does not rerun training or create new statistical evidence.
"""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys,time
import build as b
import build56 as previous
from assemble56 import labels
R=Path(__file__).resolve().parents[1]
DOCS=previous.DOCS

def binding_files():
    result=previous.bound_files()
    for folder in ('results57','sections','publication'):
        for f in (R/folder).rglob('*'):
            if f.is_file() and '__pycache__' not in f.parts:result[str(f.relative_to(R))]=b.digest(f)
    for f in R.iterdir():
        if f.is_file() and (f.suffix in ('.tex','.bib','.cls','.cfg') or f.name in ('response.md','response57.md')) and f.name!='response.tex':result[f.name]=b.digest(f)
    return result

def main(publication_only=False):
    start=time.perf_counter()
    for name in ('build','tables','audit/build-logs'):(R/name).mkdir(parents=True,exist_ok=True)
    import study57
    freeze=study57.verify();assembly=json.loads((R/'audit/ASSEMBLY57.json').read_text())
    for name,h in assembly['retained_sha256'].items():
        if b.digest(R/name)!=h:raise AssertionError('R56 protected file changed: '+name)
    tests={}
    for name,script in [('exact_witness57','tests57.py'),('transfer_moduli57','tests_transfer57.py')]:tests[name]=b.tests([sys.executable,'code/'+script],name)
    if publication_only:
        binding=json.loads((R/'audit/SCIENCE_BINDING57.json').read_text())
        if binding_files()!=binding['files_sha256']:raise AssertionError('R57 clean source/evidence binding differs')
        if b.digest(R/'audit/RESULT_AUDIT57.json')!=binding['result_audit_sha256']:raise AssertionError('R57 scientific replay replaced')
    else:b.run([sys.executable,'code/audit57.py'],'full-record-reintegration57')
    b.run([sys.executable,'code/tables57.py'],'tables57')
    previous.main(publication_only=publication_only)
    inherited=json.loads((R/'audit/RELEASE56.json').read_text())
    # The inherited runner reconstructs the seven documents; replace only its
    # inherited response frontmatter and recompile the current response.
    b.response();path=R/'response.tex';text=path.read_text()
    abstract='Revision R57 responds to the 9 October 2026 advisory review of R54, continuing the complete R56 manuscript. The same Neural Bellman Operators paper gains a fitted-witness transfer theorem, action-sensitive neural moduli and a newly executed prospective exact-action comparison. Original theory, applications and adverse evidence are preserved.'
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+abstract+m[2],text,count=1,flags=re.S);path.write_text(text)
    response=b.compile_document('response');docs=[response if z['document']=='response' else z for z in inherited['documents']]
    for z in docs:
        raw=subprocess.check_output(['pdftotext','-layout',str(R/'build'/(z['document']+'.pdf')),'-']);z['extracted_text_sha256']=hashlib.sha256(raw).hexdigest();(R/'build'/(z['document']+'.txt')).write_bytes(raw)
    preservation={}
    for name,before in assembly['baseline_labels'].items():
        after=set(labels(R,name));missing=sorted(set(before)-after)
        if missing:raise AssertionError((name,'Missing R56 labels',missing))
        preservation[name]=dict(inherited_labels=len(before),current_labels=len(after),missing=[])
    audit=json.loads((R/'audit/RESULT_AUDIT57.json').read_text())
    if audit['status']!='passed' or audit['services']!=90 or audit['paired_sets']!=18:raise AssertionError('Incomplete R57 science audit')
    if not publication_only:b.write_json(R/'audit/SCIENCE_BINDING57.json',dict(files_sha256=binding_files(),result_audit_sha256=b.digest(R/'audit/RESULT_AUDIT57.json'),scope='All current ordinary manuscript sources and frozen numerical source/result records bound after full replay'))
    try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:commit=None
    report=dict(status='passed',source_commit=commit,baseline_commit=assembly['baseline_commit'],controlling_review_commit=assembly['controlling_review_commit'],documents=docs,tests={**inherited['tests'],**tests},total_tests=inherited['total_tests']+sum(x['tests'] for x in tests.values()),preservation=preservation,retained_files=len(assembly['retained_sha256']),new_scientific_services=audit['services'],new_paired_sets=audit['paired_sets'],attained=audit['attained'],budget_exhausted=audit['budget_exhausted'],checked_cell_decisions=audit['checked_cell_decisions'],checked_stopping_looks=audit['checked_stopping_looks'],unique_certificate_and_solver_reintegrations=audit['unique_certificate_and_solver_reintegrations'],paired_classifications=audit['paired_classifications'],neural_extra_witness_cell_decisions=audit['neural_extra_witness_cell_decisions'],source_freeze_sha256=freeze,science_binding_sha256=b.digest(R/'audit/SCIENCE_BINDING57.json'),result_audit_sha256=b.digest(R/'audit/RESULT_AUDIT57.json'),publication_only=publication_only,build_seconds=time.perf_counter()-start,network_used_by_builder=False,new_observations_created_by_builder=0,typography_scope='Seven document compilation logs, text and output hashes; visual inspection is a separate review',scope='Current ordinary paper plus full saved-model, exact-search, certificate, interval-path and moment replay; old observations and clocks remain unchanged. Not external mathematical or editorial approval.')
    b.write_json(R/'audit/RELEASE57.json',report)
    print(json.dumps(dict(status=report['status'],tests=report['total_tests'],services=audit['services'],attained=audit['attained'],paired=audit['paired_classifications'],documents=[dict(name=z['document'],pages=z['pages']) for z in docs],seconds=report['build_seconds']),indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--publication-only',action='store_true');main(p.parse_args().publication_only)
