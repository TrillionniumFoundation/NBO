"""Offline ordinary-source R61 publication. No training or new economic samples."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys,time
import build as b
from assemble56 import labels
R=Path(__file__).resolve().parents[1]
DOCS=('ECTA','supp','development','development-supp','complete','complete-supp','response')
SCRIPTS=('tests50.py','publication_tests50.py','tests51.py','tests52.py','tests53.py','tests54.py','tests55.py','tests_tube55.py','tests56.py','tests56_extra.py','tests57.py','tests_transfer57.py','tests58.py','tests59.py','tests60.py','tests_centered60.py','tests61.py')
SCIENTIFIC=('audit/PREPARATION61.json','audit/SCIENCE_REPLAY61.json','audit/SCIENCE_SUMMARY61.json','audit/EXECUTION61.json','audit/FACTORIAL_AUDIT61.json','audit/COMPILER61.json','audit/TESTS61.json')

def read(p):return json.loads(Path(p).read_text())
def need(c,msg):
    if not c:raise AssertionError(msg)
def bindings():
    out={}
    for p in R.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts:continue
        rel=p.relative_to(R)
        if rel.parts[0] in ('build','audit','tables') or str(rel)=='response.tex':continue
        out[str(rel)]=b.digest(p)
    for p in (R/'audit').glob('*FREEZE*.json'):out[str(p.relative_to(R))]=b.digest(p)
    for name in SCIENTIFIC:out[name]=b.digest(R/name)
    return out

def main():
    start=time.perf_counter()
    for name in ('python3','g++','pdflatex','pandoc','pdfinfo','pdftotext'):need(shutil.which(name),'Missing publication dependency: '+name)
    for folder in ('build','tables','audit/build-logs'):(R/folder).mkdir(parents=True,exist_ok=True)
    prep=read(R/'audit/PREPARATION61.json');assembly=read(R/'audit/ASSEMBLY61.json')
    for family in ('protected_sha256','scientific_sha256'):
        for name,h in prep[family].items():need(b.digest(R/name)==h,'Changed inherited source/evidence: '+name)
    import revalidate61,factorial61
    fz=revalidate61.verify();fzf=factorial61.verify();science=read(R/'audit/SCIENCE_REPLAY61.json');factor=read(R/'audit/FACTORIAL_AUDIT61.json');execution=read(R/'audit/EXECUTION61.json');fixed=read(R/'results61-revalidation/summary.json')
    need(science['status']==factor['status']==execution['status']==fixed['status']=='passed','Incomplete executed science')
    need(science['source_freeze_sha256']==fixed['source_freeze_sha256']==fz,'Science source binding')
    need(factor['source_freeze_sha256']==fzf,'Factorial source binding')
    need(science['services']==96 and science['attained']==80 and science['budget_exhausted']==16,'Service catalogue mismatch')
    need(fixed['distinct_actors']==5 and fixed['original_actor_aliases']==32,'Fixed-actor catalogue mismatch')
    need(factor['checked_exact_answers']==3160 and factor['workers']==2,'Factorial answer count')
    binding_path=R/'audit/SOURCE_BINDING61.json'
    before=bindings()
    if binding_path.exists():need(before==read(binding_path)['files_sha256'],'Clean source/scientific-output binding differs')
    tests=b.historical()
    for script in SCRIPTS:tests[script[:-3]]=b.tests([sys.executable,'code/'+script],'r61-'+script[:-3])
    tests['native_factorial61']=b.tests([sys.executable,'code/factorial61.py','--test'],'r61-native-factorial-tests')
    b.run([sys.executable,'code/extend53.py','--test'],'r61-exact-perturbation-regression')
    b.run([sys.executable,'code/cohort55b.py','--test'],'r61-immutable-recording-regression')
    b.run([sys.executable,'code/revalidate61.py','--replay'],'r61-fixed-policy-independent-repeat')
    b.run([sys.executable,'code/tables61.py'],'r61-derived-tables')
    preservation={}
    for d,old in prep['baseline_labels'].items():
        current=set(labels(R,d));missing=sorted(set(old)-current);need(not missing,(d,'Inherited labels missing',missing))
        preservation[d]=dict(inherited_labels=len(old),current_labels=len(current),missing=[])
    b.response();file=R/'response.tex';text=file.read_text()
    abstract='Revision R61 responds to the 9 October 2026 advisory report on R59. The original Neural Bellman Operators paper gains root-free exact witnesses, matched native ablations, fixed-cover stability and original-optimum certification of unchanged returned policies. Earlier theory, applications and adverse evidence remain preserved.'
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+abstract+m[2],text,count=1,flags=re.S)
    text=text.replace(r'\input{preamble}',r'\input{preamble}'+'\n'+r'\setcounter{secnumdepth}{2}',1);file.write_text(text)
    docs=[]
    for name in DOCS:
        record=b.compile_document(name);raw=subprocess.check_output(['pdftotext','-layout',str(R/'build'/(name+'.pdf')),'-']);record['extracted_text_sha256']=hashlib.sha256(raw).hexdigest();(R/'build'/(name+'.txt')).write_bytes(raw);docs.append(record)
    need(before==bindings(),'Scientific input or author source changed during build')
    if not binding_path.exists():b.write_json(binding_path,dict(files_sha256=before,scope='Complete ordinary author sources and immutable scientific inputs/results. Current tables and PDF outputs are derived; volatile build logs are separately bound by delivery.'))
    try:sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:sha=None
    facts=read(R/'audit/PUBLICATION_FACTS61.json')
    result=dict(status='passed',tested_source_commit=sha,baseline_commit=prep['baseline_commit'],controlling_review_commit=prep['controlling_review_commit'],documents=docs,tests=tests,total_tests=sum(v['tests'] for v in tests.values()),new_R61_tests=tests['tests61']['tests']+tests['native_factorial61']['tests'],additional_assertion_suites=['exact perturbation regression','immutable recorder regression'],preservation=preservation,protected_files=len(prep['protected_sha256']),scientific_files=len(prep['scientific_sha256']),source_freeze_sha256=fz,factorial_freeze_sha256=fzf,source_binding_sha256=b.digest(binding_path),science_replay_sha256=b.digest(R/'audit/SCIENCE_REPLAY61.json'),factorial_audit_sha256=b.digest(R/'audit/FACTORIAL_AUDIT61.json'),fixed_policy_summary_sha256=b.digest(R/'results61-revalidation/summary.json'),fixed_policy_replay_sha256=b.digest(R/'audit/REVALIDATION_REPLAY61.json'),publication_facts=facts,new_training_services=0,new_policy_cost_samples=0,new_implementation_work_experiment='R61 matched native factorial, independently executed and frozen before this publication build',original_service_clocks_replaced=False,network_used_by_builder=False,build_seconds=time.perf_counter()-start,typography_scope='Seven document logs, extracted text and output identities. Visual review is a separate record only when performed.',science_scope='Full R60 mathematical reconstruction and R61 executions are independently recorded and identity checked, not rerun or relabeled as new observations by ordinary publication. Fixed-policy endpoint recursion is repeated in this build. Inherited sources/evidence and regression suites are rechecked.',scope='Ordinary original-paper revision, all scientific and inherited source bindings, regression tests, seven-document compilation and current-table regeneration; not external mathematical or editorial acceptance.')
    b.write_json(R/'audit/RELEASE61.json',result)
    print(json.dumps(dict(status='passed',tests=result['total_tests'],new_tests=result['new_R61_tests'],documents=[dict(name=x['document'],pages=x['pages']) for x in docs],services=science['services'],fixed_actors=fixed['distinct_actors'],factorial_answers=factor['checked_exact_answers'],seconds=result['build_seconds']),indent=2),flush=True)
if __name__=='__main__':main()
