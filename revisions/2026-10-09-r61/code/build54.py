"""Offline build of the ordinary R54 paper; never reruns scientific services."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys,time
import build as b
from assemble54 import expanded
R=Path(__file__).resolve().parents[1]
DOCS=('ECTA','supp','complete','complete-supp','response')

def main():
    start=time.perf_counter()
    for executable in ('pdflatex','pandoc','pdfinfo','pdftotext'):
        if shutil.which(executable) is None:raise RuntimeError('Missing publication dependency: '+executable)
    for folder in ('audit','audit/build-logs','tables','build'):(R/folder).mkdir(parents=True,exist_ok=True)
    assembly=json.loads((R/'audit/ASSEMBLY54.json').read_text())
    for name,h in assembly['retained_sha256'].items():
        if b.digest(R/name)!=h:raise AssertionError('Changed inherited file: '+name)
    tests=b.historical()
    for label,script in [('construction50','tests50.py'),('publication50','publication_tests50.py'),('finite_sweeps51','tests51.py'),('contrasts52','tests52.py'),('continuous_sweeps53','tests53.py'),('directed54','tests54.py')]:
        tests[label]=b.tests([sys.executable,'code/'+script],label)
    b.run([sys.executable,'code/extend53.py','--test'],'controlled-misspecification-exact-tests')
    for label,script in [('inherited-record-audit','audit50.py'),('inherited-tables','tables50.py'),('contrast-record-audit','audit52.py'),('full-sweep-record-audit','audit54.py'),('full-sweep-tables','tables54.py')]:
        b.run([sys.executable,'code/'+script],label)
    preservation={}
    for name,before in assembly['baseline_labels'].items():
        after=set(re.findall(r'\\label\{([^}]+)\}',expanded(R,R/(name+'.tex'))))
        missing=sorted(set(before)-after)
        if missing:raise AssertionError((name,'Missing inherited labels',missing))
        preservation[name]=dict(inherited_labels=len(before),current_labels=len(after),missing=[])
    b.response()
    response=R/'response.tex';text=response.read_text()
    abstract='Revision R54. This response addresses the 8 October 2026 advisory report on R52 and integrates the separately frozen full-sweep evidence into the same Neural Bellman Operators paper. Original theory, applications and adverse results are preserved.'
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+abstract+m[2],text,count=1,flags=re.S)
    response.write_text(text)
    docs=[b.compile_document(name) for name in DOCS]
    for doc in docs:
        name=doc['document'];raw=subprocess.check_output(['pdftotext','-layout',str(R/'build'/(name+'.pdf')),'-'])
        doc['extracted_text_sha256']=hashlib.sha256(raw).hexdigest()
        (R/'build'/(name+'.txt')).write_bytes(raw)
    audit=json.loads((R/'audit/RESULT_AUDIT54.json').read_text())
    try:source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
    except subprocess.CalledProcessError:source_commit=None
    result=dict(status='passed',source_commit=source_commit,documents=docs,tests=tests,
        total_tests=sum(x['tests'] for x in tests.values()),
        additional_controlled_perturbation_test='exact harmful false-null example and 64 perturbed-domain checks',
        preservation=preservation,inherited_files_hash_checked=len(assembly['retained_sha256']),
        baseline_commit=assembly['baseline_commit'],controlling_review_commit=assembly['controlling_review_commit'],
        scientific_source_freezes_checked=['SOURCE_FREEZE53.json','SOURCE_FREEZE53_EXTENSION.json'],
        record_audit_sha256=b.digest(R/'audit/RESULT_AUDIT54.json'),
        checked_full_sweep_cell_decisions=audit['checked_full_sweep_cell_decisions'],
        checked_misspecification_cell_cases=audit['misspecification']['checked_cell_cases'],
        new_scientific_services=0,new_policy_cost_samples=0,network_used_by_builder=False,
        build_seconds=time.perf_counter()-start,
        scope='ordinary source build, exact/interval regression tests, all stored decisions and endpoint inference replay; no claim of independent complete reintegration or mathematical peer approval',
        typography_scope='five PDF compilation logs and text extraction; visual inspection is separately documented only if performed')
    b.write_json(R/'audit/RELEASE54.json',result)
    files={str(f.relative_to(R)):b.digest(f) for f in R.rglob('*') if f.is_file() and not any(x in f.parts for x in ('__pycache__','build','audit'))}
    b.write_json(R/'audit/PUBLICATION_FILES54.json',files)
    print(json.dumps(dict(status=result['status'],tests=result['total_tests'],documents=docs,record_cells=result['checked_full_sweep_cell_decisions'],perturbation_cells=result['checked_misspecification_cell_cases'],seconds=result['build_seconds']),indent=2))
if __name__=='__main__':main()
