"""Offline R56 verification/publication; no training or new policy-cost paths.

--publication-only checks the complete source/evidence binding and regenerates
publication tables and PDFs. It does not claim a second scientific execution.
"""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,sys,time
import build as b
from assemble56 import expanded
R=Path(__file__).resolve().parents[1]
DOCS=('ECTA','supp','development','development-supp','complete','complete-supp','response')

def bound_files():
    out={}
    for folder in ('code','inputs','evidence','results','results52','results53','results53-extension','results55','results55-tube','attempts'):
        for f in (R/folder).rglob('*'):
            if f.is_file() and '__pycache__' not in f.parts:out[str(f.relative_to(R))]=b.digest(f)
    for f in (R/'audit').glob('*FREEZE*.json'):out[str(f.relative_to(R))]=b.digest(f)
    for f in R.glob('*PROTOCOL*.md'):out[str(f.relative_to(R))]=b.digest(f)
    return out

def main(publication_only=False):
    start=time.perf_counter()
    for x in ('pdflatex','pandoc','pdfinfo','pdftotext'):
        if shutil.which(x) is None:raise RuntimeError('Missing publication dependency: '+x)
    for f in ('audit','audit/build-logs','tables','build'):(R/f).mkdir(parents=True,exist_ok=True)
    assembly=json.loads((R/'audit/ASSEMBLY56.json').read_text())
    for name,h in assembly['retained_sha256'].items():
        if b.digest(R/name)!=h:raise AssertionError('Inherited file changed: '+name)
    tests=b.historical()
    for label,script in [('construction50','tests50.py'),('publication50','publication_tests50.py'),('finite_sweeps51','tests51.py'),('contrasts52','tests52.py'),('continuous_sweeps53','tests53.py'),('directed54','tests54.py'),('trained_and_prospective55','tests55.py'),('signed_tubes55','tests_tube55.py'),('algebraic_and_pipeline56','tests56.py'),('multiple_roots56','tests56_extra.py')]:
        tests[label]=b.tests([sys.executable,'code/'+script],label)
    b.run([sys.executable,'code/cohort55b.py','--test'],'immutable-controller56')
    import study53,extend53,prospective55,execute_tube55,cohort55b
    freezes=[study53.verify_freeze(),extend53.verify(),prospective55.verify(),execute_tube55.verify(),cohort55b.verify()]
    if publication_only:
        binding=json.loads((R/'audit/SCIENCE_BINDING56.json').read_text())
        if binding['files_sha256']!=bound_files():raise AssertionError('Clean reproduction source/evidence binding differs')
        if b.digest(R/'audit/RESULT_AUDIT56.json')!=binding['result_audit_sha256']:raise AssertionError('Unverified audit substituted')
    else:
        b.run([sys.executable,'code/audit56.py'],'full-record-reintegration56')
        b.write_json(R/'audit/SCIENCE_BINDING56.json',dict(files_sha256=bound_files(),result_audit_sha256=b.digest(R/'audit/RESULT_AUDIT56.json'),scope='All frozen scientific sources, inputs, records and the new exact replay implementation bound before publication'))
    b.run([sys.executable,'code/tables56.py'],'tables56')
    preservation={}
    for name,before in assembly['baseline_labels'].items():
        after=set(re.findall(r'\\label\{([^}]+)\}',expanded(R,R/(name+'.tex'))));missing=sorted(set(before)-after)
        if missing:raise AssertionError((name,'Missing inherited labels',missing))
        preservation[name]=dict(inherited_labels=len(before),current_labels=len(after),missing=[])
    b.response();response=R/'response.tex';text=response.read_text()
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'Revision R56 responds to the 9 October 2026 advisory report on R54. The same Neural Bellman Operators paper retains its original constructive and economic targets and adds trained-neural action witnesses, non-tensor verification, prospective stopping and confidence-qualified learned structure.'+m[2],text,count=1,flags=re.S);response.write_text(text)
    docs=[b.compile_document(name) for name in DOCS]
    for z in docs:
        raw=subprocess.check_output(['pdftotext','-layout',str(R/'build'/(z['document']+'.pdf')),'-']);z['extracted_text_sha256']=hashlib.sha256(raw).hexdigest();(R/'build'/(z['document']+'.txt')).write_bytes(raw)
    result=json.loads((R/'audit/RESULT_AUDIT56.json').read_text())
    try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:commit=None
    report=dict(status='passed',source_commit=commit,documents=docs,tests=tests,total_tests=sum(z['tests'] for z in tests.values()),preservation=preservation,retained_files=len(assembly['retained_sha256']),source_freezes_verified=freezes,
        result_audit_sha256=b.digest(R/'audit/RESULT_AUDIT56.json'),science_binding_sha256=b.digest(R/'audit/SCIENCE_BINDING56.json'),
        services=132,primary_attained=result['primary']['attained'],sensitivity_attained=result['tube']['attained'],unique_certificate_reintegrations=sum(result[c]['unique_certificate_reintegrations'] for c in ('primary','tube')),
        checked_service_cell_decisions=sum(result[c]['checked_cell_decisions'] for c in ('primary','tube')),checked_stopping_looks=sum(result[c]['checked_looks'] for c in ('primary','tube')),learned_null_cell_cases=result['learned_null']['cell_cases'],
        publication_only=publication_only,build_seconds=time.perf_counter()-start,new_scientific_services=0,new_cost_samples=0,network_used_by_builder=False,
        historical_evidence_scope='Inherited source/evidence identities and tests rechecked; historical economic observations are not resimulated',
        typography_scope='Seven document logs, extracted text and output hashes; visual inspection is documented separately',scope='Same-algorithm certificate reintegration from saved fits, exact-rational moment validation, stopping replay and publication; not external mathematical approval')
    b.write_json(R/'audit/RELEASE56.json',report)
    print(json.dumps(dict(status='passed',tests=report['total_tests'],documents=[dict(name=z['document'],pages=z['pages']) for z in docs],seconds=report['build_seconds'],publication_only=publication_only),indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--publication-only',action='store_true');main(parser.parse_args().publication_only)
