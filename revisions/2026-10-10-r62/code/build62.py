"""Offline R62 publication: no fitting, new sample paths, or science retiming."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys,time
import build as b
from assemble56 import labels
R=Path(__file__).resolve().parents[1]
DOCS=('ECTA','supp','development','development-supp','complete','complete-supp','response')
SCRIPTS=('tests50.py','publication_tests50.py','tests51.py','tests52.py','tests53.py','tests54.py','tests55.py','tests_tube55.py','tests56.py','tests56_extra.py','tests57.py','tests_transfer57.py','tests58.py','tests59.py','tests60.py','tests_centered60.py','tests61.py','tests62.py')

def need(c,msg):
    if not c:raise AssertionError(msg)
def read(p):return json.loads(Path(p).read_text())
def bindings():
    files={}
    for p in R.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts:continue
        rel=p.relative_to(R)
        if rel.parts[0] in ('build','audit','tables') or str(rel)=='response.tex':continue
        files[str(rel)]=b.digest(p)
    for name in ('audit/SOURCE_FREEZE62.json','audit/EXECUTION62.json','audit/COMPILER62.json','audit/PREPARATION62.json','audit/PREPRODUCTION_CORRECTION62.json','audit/PRODUCTION_ENVELOPE62.json','audit/RESULT_INTERPRETATION62.json'):files[name]=b.digest(R/name)
    return files

def main():
    start=time.perf_counter()
    for name in ('g++','pdflatex','pandoc','pdfinfo','pdftotext'):need(shutil.which(name),'Missing publication dependency: '+name)
    for folder in ('build','tables','audit/build-logs'):(R/folder).mkdir(parents=True,exist_ok=True)
    import science62
    fz=science62.verify();execution=read(R/'audit/EXECUTION62.json');prep=read(R/'audit/PREPARATION62.json');assembly=read(R/'audit/ASSEMBLY62.json')
    need(execution['status']=='executed' and execution['source_freeze_sha256']==fz,'Incomplete scientific execution')
    need(execution['primitive_fitted_services']==40 and execution['independent_path_rows_under_declared_model']==327680,'Prospective catalogue incomplete')
    for name,h in prep['protected_sha256'].items():need(b.digest(R/name)==h,'Changed predecessor scientific file: '+name)
    before=bindings();bindfile=R/'audit/SOURCE_BINDING62.json'
    if bindfile.exists():need(read(bindfile)['files_sha256']==before,'Committed source/science binding differs before build')
    b.run(['g++','-O3','-std=c++17','-shared','-fPIC','-ffp-contract=off','-fno-fast-math','code/interpolate62.cpp','-o','build/interpolate62.so'],'r62-interpolation-build')
    b.run(['g++','-O3','-std=c++17','code/search60.cpp','-o','build/native60'],'r62-exact-native-build')
    tests=b.historical()
    for script in SCRIPTS:tests[script[:-3]]=b.tests([sys.executable,'code/'+script],'r62-'+script[:-3])
    tests['native_factorial61']=b.tests([sys.executable,'-m','unittest','discover','-s','code','-p','factorial61.py','-v'],'r62-retained-native-factorial-tests')
    need(tests['native_factorial61']['tests']==4,'All four retained factorial fixtures must execute')
    b.run([sys.executable,'code/extend53.py','--test'],'r62-retained-exact-perturbation')
    b.run([sys.executable,'code/cohort55b.py','--test'],'r62-retained-immutable-recorder')
    b.run([sys.executable,'code/revalidate61.py','--replay'],'r62-retained-fixed-actor-replay')
    b.run([sys.executable,'code/audit62.py'],'r62-science-replay')
    b.run([sys.executable,'code/account62.py'],'r62-complete-work-account')
    b.run([sys.executable,'code/tables62.py'],'r62-current-tables')
    preservation={}
    for name,old in prep['baseline_labels'].items():
        current=set(labels(R,name));missing=sorted(set(old)-current);need(not missing,(name,'Inherited labels missing',missing))
        preservation[name]=dict(inherited_labels=len(old),current_labels=len(current),missing=[])
    b.write_json(R/'audit/PRECOMPILE_VERIFICATION62.json',dict(status='passed',tests=tests,total_tests=sum(v['tests'] for v in tests.values()),preservation=preservation,source_freeze_sha256=fz))
    b.response();path=R/'response.tex';text=path.read_text()
    abstract='Revision R62 responds to the advisory report of 10 October 2026 on R61. The original Neural Bellman Operators paper gains primitive Bellman regularity, a second-order certificate for the actual acquired policy, and prospective multidimensional and complete two-control economic comparisons. Prior theory, applications and adverse evidence are preserved.'
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+abstract+m[2],text,count=1,flags=re.S)
    text=text.replace(r'\input{preamble}',r'\input{preamble}'+'\n'+r'\setcounter{secnumdepth}{2}',1);path.write_text(text)
    documents=[];failures={}
    for name in DOCS:
        try:
            record=b.compile_document(name)
            raw=subprocess.check_output(['pdftotext','-layout',str(R/'build'/(name+'.pdf')),'-'])
            record['extracted_text_sha256']=hashlib.sha256(raw).hexdigest();(R/'build'/(name+'.txt')).write_bytes(raw);documents.append(record)
            print(json.dumps(dict(document=name,status='passed',pages=record['pages'])),flush=True)
        except (RuntimeError,subprocess.CalledProcessError) as error:
            failures[name]=str(error);print(json.dumps(dict(document=name,status='failed',error=str(error))),flush=True)
    b.write_json(R/'audit/DOCUMENT_GATES62.json',dict(status='failed' if failures else 'passed',documents=documents,failures=failures))
    if failures:raise RuntimeError('Publication withheld: '+json.dumps(failures))
    need(before==bindings(),'Ordinary build changed scientific inputs or author sources')
    if not bindfile.exists():b.write_json(bindfile,dict(files_sha256=before,scope='All ordinary author sources and immutable scientific inputs/outputs, including the production-envelope receipt and the complete-catalogue interpretation. Generated tables, PDF outputs and volatile replay logs have separate release bindings.'))
    try:sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:sha=None
    replay=read(R/'audit/SCIENCE_REPLAY62.json');facts=read(R/'audit/PUBLICATION_FACTS62.json');work=read(R/'audit/COMPLETE_WORK62.json')
    need(work['status']=='passed' and replay['complete_work_ledger_sha256']==b.digest(R/'audit/COMPLETE_WORK62.json'),'Complete-production charge binding')
    result=dict(status='passed',tested_source_commit=sha,baseline_commit=prep['baseline_commit'],controlling_review_commit=prep['review_commit'],source_freeze_sha256=fz,source_binding_sha256=b.digest(bindfile),documents=documents,tests=tests,total_tests=sum(v['tests'] for v in tests.values()),new_R62_tests=tests['tests62']['tests'],preservation=preservation,protected_files=len(prep['protected_sha256']),checked_nodal_action_records=replay['checked_nodal_action_records'],checked_interval_records=replay['checked_interval_records'],reintegrated_primitive_point_action_queries=replay['reintegrated_primitive_point_action_queries'],fitting_services_in_frozen_execution=40,path_rows_in_frozen_execution=327680,new_training_services_in_build=0,new_policy_cost_samples_in_build=0,publication_facts=facts,complete_work_ledger_sha256=b.digest(R/'audit/COMPLETE_WORK62.json'),complete_work_scope=work['scope'],build_seconds=time.perf_counter()-start,network_used_by_builder=False,original_service_clocks_replaced=False,typography_scope='Seven document compilation logs, extracted text and output identities. Font substitutions are retained; any visual review has its own separate record.',science_scope=replay['scope'],scope='Ordinary-source original-paper revision, complete retained science bindings, inherited/new regression tests, all stored decision and interval recursions, seven-document compilation. Not external mathematical or editorial acceptance.')
    b.write_json(R/'audit/RELEASE62.json',result)
    print(json.dumps(dict(status='passed',tests=result['total_tests'],new_tests=result['new_R62_tests'],documents=[dict(name=d['document'],pages=d['pages']) for d in documents],checked_nodes=result['checked_nodal_action_records'],checked_intervals=result['checked_interval_records'],seconds=result['build_seconds']),indent=2),flush=True)
if __name__=='__main__':main()
