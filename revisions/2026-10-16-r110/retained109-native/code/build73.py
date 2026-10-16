"""Offline R73 ordinary-source build; no scientific fitting or resimulation."""
from pathlib import Path
import argparse,ast,hashlib,json,re,shutil,subprocess,sys,time
import build72 as b
R=Path(__file__).resolve().parents[1];OLD72=R.parent/'2026-10-11-r72';OLD70=R.parent/'2026-10-11-r70'
DOCS=b.DOCS

def preserve73():
    inherited=b.preserve();a=json.loads((R/'audit/PREPARATION73.json').read_text());statements=proofs=labels=0
    for name,h in a['inherited_sections'].items():
        if b.sha(R/name)!=h or b.sha(OLD72/name)!=h:raise AssertionError('R72 section changed: '+name)
        count=sum((R/(doc+'.tex')).read_text().count('\\input{'+name[:-4]+'}') for doc in DOCS[:-1])
        if count!=1:raise AssertionError(('Inherited section occurrence',name,count))
        text=(R/name).read_text();statements+=len(re.findall(r'\\begin\{(?:theorem|lemma|proposition|corollary)\}',text));proofs+=text.count(r'\begin{proof}');labels+=len(re.findall(r'\\label\{',text))
    for name,h in a['original_wrapper_sha256'].items():
        if b.sha(R/'preserved/R72-original'/name)!=h:raise AssertionError('Original wrapper changed')
    for doc,oldlabels in a['wrapper_labels'].items():
        if set(oldlabels)-set(re.findall(r'\\label\{([^}]+)\}',(R/(doc+'.tex')).read_text())):raise AssertionError('Wrapper label removed')
    record=dict(status='passed',R70=inherited,R72_sections=len(a['inherited_sections']),R72_statements=statements,R72_proofs=proofs,R72_labels=labels,sections_compiled_byte_identically_once=True)
    b.save(R/'audit/PRESERVATION73.json',record);return record

def source_checks():
    freeze=json.loads((R/'SOURCE_FREEZE73.json').read_text())
    for name,h in freeze['files'].items():
        if b.sha(R/name)!=h:raise AssertionError('R73 scientific source freeze changed: '+name)
    finish=json.loads((R/'audit/EXECUTION_FINISHED73.json').read_text())
    if finish['status']!='passed' or finish['complete_construction_services']!=4:raise AssertionError('Construction catalogue incomplete')
    oldfiles=json.loads((R/'audit/SCIENTIFIC_RECORDS72.json').read_text())
    for name,h in oldfiles.items():
        if b.sha(R/'results72'/name)!=h:raise AssertionError('R72 scientific record changed: '+name)
    newfiles={str(p.relative_to(R)):b.sha(p) for p in sorted((R/'results73').rglob('*')) if p.is_file()}
    b.save(R/'audit/SCIENTIFIC_FILES73.json',dict(source_freeze_sha256=b.sha(R/'SOURCE_FREEZE73.json'),design_commit=freeze['design_commit'],new_files=newfiles,retained_R72_scientific_files=len(oldfiles),new_independent_policy_cost_rows=0))
    return dict(R72_files=len(oldfiles),R73_files=len(newfiles),design_commit=freeze['design_commit'])

def response():
    b.response();p=R/'response.tex';text=p.read_text().replace('label=e73supp','label=e73response').replace('label=e72response','label=e73response')
    abstract='Revision R73 addresses the 11 October 2026 advisory report on R67. The original NBO paper is extended by qualification-optimal continuation readouts, exact primal--dual certificates, a predictable original-law cost theorem and four predeclared construction services. Every prior active section and adverse evidence block is retained.'
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+abstract+m[2],text,flags=re.S);p.write_text(text)

def main(full=False):
    start=time.perf_counter();(R/'build').mkdir(exist_ok=True);(R/'audit/build-logs').mkdir(parents=True,exist_ok=True)
    for exe in ('pdflatex','pandoc','pdfinfo','pdftotext'):
        if shutil.which(exe) is None:raise RuntimeError('Missing publication executable '+exe)
    for p in (R/'code').glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    preservation=preserve73();sources=source_checks();tests={}
    suites=[('72-theory',R/'code/tests72.py'),('72-release',R/'code/tests_publication72.py'),('73-exact',R/'code/tests73.py')]
    if full:
        suites += [(str(n),R.parent/f'2026-10-10-r{n}/code/tests{n}.py') for n in (63,64,65,66)]
        suites += [('67-science',R.parent/'2026-10-10-r67/code/tests67.py'),('67-math',R.parent/'2026-10-10-r67/code/tests_math67.py'),('67-records',R.parent/'2026-10-10-r67/code/tests_records67.py'),('69',R.parent/'2026-10-11-r69/code/tests69.py'),('70',OLD70/'code/tests70.py')]
    for name,file in suites:
        begin=time.perf_counter();text=b.run([sys.executable,str(file)],'tests-'+name);found=re.search(r'Ran (\d+) tests?',text)
        if not found or not re.search(r'^OK\s*$',text,re.M):raise AssertionError('Unittest success absent: '+name)
        tests[name]=dict(tests=int(found[1]),status='passed',seconds=time.perf_counter()-begin)
    # Keep the first independently executed R73 check before generating replay times.
    first=R/'audit/FIRST_INDEPENDENT73.json'
    if not first.exists():shutil.copy2(R/'audit/INDEPENDENT73.json',first)
    for name in ('independent72','audit_contract72','tables72','independent73','tables73'):
        b.run([sys.executable,'code/'+name+'.py'],name)
    if full:
        path=OLD70/'audit/RESULT_AUDIT70.json';before=path.read_bytes()
        try:
            b.run([sys.executable,str(OLD70/'code/audit70.py')],'retained-record-audit70',OLD70)
            shutil.copy2(path,R/'audit/RETAINED_REPLAY70_IN_R73.json')
        finally:path.write_bytes(before)
    response()
    for name in DOCS:(R/'build'/(name+'.bbl')).unlink(missing_ok=True)
    for iteration in range(5):
        for name in DOCS:
            b.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build',name+'.tex'],name+'-pass'+str(iteration))
            if iteration==0 and name!='response':b.bibliography(name)
    documents=[b.pdf_record(name) for name in DOCS]
    for d in documents:
        if d['document']=='ECTA' and d['pages']>45:raise AssertionError('Main exceeds internal 45-page target: '+str(d['pages']))
        if d['document']=='supp' and d['pages']>25:raise AssertionError('Supplement exceeds internal 25-page target: '+str(d['pages']))
    abstract=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',(R/'ECTA.tex').read_text(),re.S)[1]
    if len(abstract.split())>150:raise AssertionError('Abstract exceeds 150-word internal target')
    for p in R.rglob('*'):
        if p.is_file() and p.suffix.lower() in b.FONT_EXTENSIONS:raise AssertionError('Standalone font file')
    try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:commit=None
    new=json.loads((R/'audit/INDEPENDENT73.json').read_text());prior=json.loads((R/'audit/INDEPENDENT72.json').read_text())
    report=dict(status='passed',tested_source_commit=commit,full_retained_replay=full,documents=documents,tests=tests,total_tests=sum(v['tests'] for v in tests.values()),preservation=preservation,sources=sources,
                independent73=new,independent72_summary={k:prior[k] for k in ('status','services','failed_services','checked_query_returns','checked_transport_returns','exact_conditional_integrals')},
                current_new_construction_services=4,retained_R72_query_processes=36,new_independent_policy_cost_rows=0,scientific_services_reexecuted=False,
                abstract_words=len(abstract.split()),seconds=time.perf_counter()-start,
                scope='Ordinary-source build, all declared suites, all new construction action values independently recomputed, exact optimization certificates, preserved R72 query evidence and prior full-bin cost replay; no new policy-cost rows or historical service retiming',
                visual_scope='Log/text gates only here; actual PDF visual inspection is a separately hash-bound requirement')
    b.save(R/'audit/RELEASE73.json',report)
    print(json.dumps({k:report[k] for k in ('status','total_tests','documents','preservation','sources','seconds')},indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--full',action='store_true');main(parser.parse_args().full)
