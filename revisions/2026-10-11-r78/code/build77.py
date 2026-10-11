"""Offline full R77 manuscript build and independent numerical replay.

The original scientific clocks and historical source branches are never
retimed or overwritten. A build log is not a visual inspection certificate.
"""
from pathlib import Path
import argparse,ast,json,re,shutil,subprocess,sys,time
import build72 as b
import build73 as inherited
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-11-r73'
DOCS=b.DOCS

def preservation():
    prior=inherited.preserve73();record=json.loads((R/'audit/PREPARATION77.json').read_text())
    statements=proofs=0
    for name,entry in record['inherited_active_sections'].items():
        if b.sha(R/name)!=entry['sha256'] or b.sha(OLD/name)!=entry['sha256']:raise AssertionError('R73 section changed: '+name)
        needle='\\input{'+name[:-4]+'}'
        count=sum((R/(doc+'.tex')).read_text().count(needle) for doc in DOCS[:-1])
        if count!=1:raise AssertionError(('Inherited section omitted or duplicated',name,count))
        text=(R/name).read_text();statements+=len(re.findall(r'\\begin\{(?:theorem|lemma|proposition|corollary)\}',text));proofs+=text.count(r'\begin{proof}')
    for name,h in record['original_wrappers'].items():
        if b.sha(R/'preserved/R73-original'/name)!=h:raise AssertionError('Preserved wrapper changed')
    for doc,labels in record['wrapper_labels'].items():
        if set(labels)-set(re.findall(r'\\label\{([^}]+)\}',(R/(doc+'.tex')).read_text())):raise AssertionError('Original wrapper label removed')
    for name,h in record['inherited_evidence'].items():
        if b.sha(R/name)!=h or b.sha(OLD/name)!=h:raise AssertionError('Inherited scientific evidence changed: '+name)
    result=dict(status='passed',prior=prior,R73_active_sections=len(record['inherited_active_sections']),R73_formal_statements=statements,R73_proof_blocks=proofs,
        inherited_evidence_files=len(record['inherited_evidence']),all_inherited_sections_compiled_byte_identically_once=True,
        old_wrappers_preserved=True,base_commit=record['base_commit'])
    b.save(R/'audit/PRESERVATION77.json',result);return result

def response():
    b.response();path=R/'response.tex';text=path.read_text()
    text=text.replace('label=e77supp','label=e77response').replace('label=e73supp','label=e77response').replace('label=e72response','label=e77response')
    abstract='Revision R78 responds to the advisory report on R67 dated 11 October 2026. The original Neural Bellman Operators paper connects attained continuation qualification to the original-law costs of its complete constructed controllers. Exact conditional integration, two independent full-bin evaluations, explicit precision components and sharp price-uniform catalogue choice extend the retained theory and evidence.'
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+abstract+m[2],text,count=1,flags=re.S)
    path.write_text(text)

def main(full=False):
    start=time.perf_counter();(R/'build').mkdir(exist_ok=True);(R/'audit/build-logs').mkdir(parents=True,exist_ok=True)
    for exe in ('pdflatex','pandoc','pdfinfo','pdftotext'):
        if shutil.which(exe) is None:raise RuntimeError('Missing publication dependency '+exe)
    for p in (R/'code').glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    kept=preservation();sources=inherited.source_checks();tests={}
    suites=[('72-theory',R/'code/tests72.py'),('72-release',R/'code/tests_publication72.py'),('73-exact',R/'code/tests73.py'),('77-cost',R/'code/tests77.py')]
    if full:
        suites += [(str(n),R.parent/f'2026-10-10-r{n}/code/tests{n}.py') for n in (63,64,65,66)]
        suites += [('67-science',R.parent/'2026-10-10-r67/code/tests67.py'),('67-math',R.parent/'2026-10-10-r67/code/tests_math67.py'),('67-records',R.parent/'2026-10-10-r67/code/tests_records67.py'),('69',R.parent/'2026-10-11-r69/code/tests69.py'),('70',R.parent/'2026-10-11-r70/code/tests70.py')]
    for label,file in suites:
        began=time.perf_counter();text=b.run([sys.executable,str(file)],'tests-'+label)
        match=re.search(r'Ran (\d+) tests?',text)
        if not match or not re.search(r'^OK\s*$',text,re.M):raise AssertionError('Unittest success missing: '+label)
        tests[label]=dict(status='passed',tests=int(match[1]),seconds=time.perf_counter()-began)
    for name in ('independent72','audit_contract72','tables72','independent73','tables73'):
        b.run([sys.executable,'code/'+name+'.py'],name)
    if full:
        old70=R.parent/'2026-10-11-r70';report=old70/'audit/RESULT_AUDIT70.json';original=report.read_bytes()
        try:
            b.run([sys.executable,str(old70/'code/audit70.py')],'retained-record-audit70',old70)
            shutil.copy2(report,R/'audit/RETAINED_REPLAY70_IN_R77.json')
        finally:report.write_bytes(original)
    # Full new endpoint reimplementation is mandatory even for the shorter build.
    b.run([sys.executable,'code/cost77.py','--replay'],'complete-independent-cost77')
    b.run([sys.executable,'code/tables77.py'],'new-cost-tables77')
    response()
    for name in DOCS:(R/'build'/(name+'.bbl')).unlink(missing_ok=True)
    for iteration in range(5):
        for name in DOCS:
            b.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build',name+'.tex'],name+'-pass'+str(iteration))
            if iteration==0 and name!='response':b.bibliography(name)
    documents=[b.pdf_record(name) for name in DOCS]
    for document in documents:
        if document['document']=='ECTA' and document['pages']>45:raise AssertionError('Main exceeds internal 45-page target: '+str(document['pages']))
        if document['document']=='supp' and document['pages']>25:raise AssertionError('Supplement exceeds internal 25-page target: '+str(document['pages']))
    abstract=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',(R/'ECTA.tex').read_text(),re.S)[1]
    if len(abstract.split())>150:raise AssertionError('Abstract exceeds internal 150-word target')
    for p in R.rglob('*'):
        if p.is_file() and p.suffix.lower() in b.FONT_EXTENSIONS:raise AssertionError('Standalone font file')
    try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:commit=None
    fresh=json.loads((R/'results77/summary.json').read_text());replay=json.loads((R/'audit/REPLAY77.json').read_text())
    report=dict(status='passed',tested_source_commit=commit,full_retained_replay=full,documents=documents,tests=tests,
        total_tests=sum(x['tests'] for x in tests.values()),preservation=kept,inherited_sources=sources,
        new_independent_policy_cost_rows=fresh['rows'],new_complete_qualification_services=1,
        original_optimal_value_queries=0,independent_replay=replay,scientific_service_clocks_replaced=False,
        original_summary_sha256=b.sha(R/'results77/summary.json'),source_freeze_sha256=b.sha(R/'SOURCE_FREEZE77.json'),
        findings=json.loads((R/'audit/TABLES77.json').read_text()),abstract_words=len(abstract.split()),seconds=time.perf_counter()-start,
        visual_status='not_assessed_by_builder',scope='All declared suites, inherited evidence preservation, full new dual-arithmetic path replay, exact interval statistics and four ordinary-source documents; actual visual review is separate')
    b.save(R/'audit/RELEASE77.json',report)
    print(json.dumps({k:report[k] for k in ('status','total_tests','documents','preservation','new_independent_policy_cost_rows','findings','seconds')},indent=2),flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--full',action='store_true');main(parser.parse_args().full)
