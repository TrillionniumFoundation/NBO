"""Full R84 publication: preserved original science plus exact new qualification.

Inherited scientific algorithms are unchanged. This new orchestrator retains
all tests and numerical checks without applying an obsolete editorial page cap.
"""
from pathlib import Path
import argparse,ast,hashlib,json,re,shutil,subprocess,sys,time
import build72 as b
import build73 as old73
import build77 as old77
import build81 as old81
import compatible84 as new
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-12-r83'
DOCS=b.DOCS
b.ENV['SOURCE_DATE_EPOCH']='1791763200'

def read(p):return json.loads(Path(p).read_text())
def need(x,s):
    if not x:raise AssertionError(s)
def preserve():
    a=read(R/'audit/PREPARATION84.json')
    for name,h in a['protected_files'].items():
        need(b.sha(R/name)==h and b.sha(OLD/name)==h,'Inherited source/evidence bytes '+name)
    for name,item in a['active_sections'].items():
        need(b.sha(R/(name+'.tex'))==item['sha256'],'Inherited section bytes '+name)
        counts={doc:(R/doc).read_text().count('\\input{'+name+'}') for doc in ('ECTA.tex','supp.tex','appendix.tex')}
        need(counts[item['document']]==1 and sum(counts.values())==1,'Original placement and unique occurrence '+name)
    for name,h in a['original_wrappers'].items():need(b.sha(R/'preserved/R83-original'/name)==h,'Original wrapper preserved '+name)
    # The inherited publication lock is checked against its original wrappers,
    # never rewritten to pass the new editorial content. Other locked bytes
    # retain their exact current scientific identity.
    lock=read(R/'SOURCE_FREEZE83.json')
    for name,h in lock['files'].items():
        p=R/'preserved/R83-original'/name if name in a['original_wrappers'] else R/name
        need(b.sha(p)==h,'R83 original publication lock '+name)
    need('\\title{Neural Bellman Operators}' in (R/'ECTA.tex').read_text(),'Original title')
    for section,doc in [('compatible84','ECTA'),('study84','ECTA'),('proof84','appendix')]:
        needle='\\input{sections/'+section+'}'
        need((R/(doc+'.tex')).read_text().count(needle)==1,'New compiled section '+section)
    new.freeze()
    return dict(status='passed',baseline_commit=a['baseline_commit'],review_commit=a['controlling_review'],protected_files=len(a['protected_files']),inherited_active_sections=len(a['active_sections']),same_bytes_same_document_once=True,
        original_R83_lock_checked_against_preserved_original_wrappers=True,new_scientific_lock_verified=True)

def response():
    b.response();p=R/'response.tex';s=p.read_text();s=re.sub(r'label=e\d+(?:supp|response)','label=e84response',s)
    abstract='Revision R84 develops the original Neural Bellman Operators paper in response to the 11 October 2026 advisory report on R67. Complete-menu and common-readout qualification connect approximate optimization to sharper original-law policy-cost decisions. Inherited theory, evidence, failures and execution clocks remain preserved.'
    s=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+abstract+m[2],s,count=1,flags=re.S);p.write_text(s)

def check_sources():
    for p in (R/'code').glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    for p in R.rglob('*'):
        if p.is_file() and p.suffix.lower() in b.FONT_EXTENSIONS:raise AssertionError('Standalone font prohibited')
    # References added in this revision use a real author-year entry.
    need('boyd2004' in read(R/'publication/bibliography-entries.json'),'Primary duality reference')

def compile_documents():
    response()
    for name in DOCS:(R/'build'/(name+'.bbl')).unlink(missing_ok=True)
    for it in range(5):
        for name in DOCS:
            b.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build',name+'.tex'],name+'-R84-pass'+str(it))
            if it==0 and name!='response':b.bibliography(name)
    return [b.pdf_record(n) for n in DOCS]

def tables():
    for script,args in [('frontier83',[]),('tables83',[]),('tables84',[])]:b.run([sys.executable,'code/'+script+'.py']+args,script+'-R84')

def render():
    (R/'build').mkdir(exist_ok=True);(R/'audit/build-logs').mkdir(parents=True,exist_ok=True)
    preserve();check_sources();tables();docs=compile_documents()
    out=dict(status='development_render_only',documents=docs,full_release_issued=False,visual_inspection=False)
    b.save(R/'audit/DEVELOPMENT84.json',out);print(json.dumps(out,indent=2),flush=True)

def test(path,label):
    start=time.perf_counter();text=b.run([sys.executable,str(path)],'tests-'+label+'-R84')
    m=re.search(r'Ran (\d+) tests?',text)
    need(m is not None and re.search(r'^OK\s*$',text,re.M) and not re.search(r'\bskipped\b',text),'Complete unskipped test record '+label)
    return dict(status='passed',tests=int(m[1]),seconds=time.perf_counter()-start,log='audit/build-logs/tests-'+label+'-R84.log')

def main():
    start=time.perf_counter();(R/'build').mkdir(exist_ok=True);(R/'audit/build-logs').mkdir(parents=True,exist_ok=True)
    for exe in ('pdflatex','pandoc','pdfinfo','pdftotext'):need(shutil.which(exe) is not None,'Publication dependency '+exe)
    check_sources();keep=preserve();earlier=old81.preserve();older=old77.preservation();oldlocks=old73.source_checks()
    suites=[('72-theory',R/'code/tests72.py'),('72-release',R/'code/tests_publication72.py'),('73',R/'code/tests73.py'),('77',R/'code/tests77.py')]
    suites += [(str(n),R/'code'/f'tests{n}.py') for n in (78,79,80,81,82,83,84)]
    suites += [(str(n),R.parent/f'2026-10-10-r{n}/code/tests{n}.py') for n in (63,64,65,66)]
    suites += [('67-science',R.parent/'2026-10-10-r67/code/tests67.py'),('67-math',R.parent/'2026-10-10-r67/code/tests_math67.py'),('67-records',R.parent/'2026-10-10-r67/code/tests_records67.py'),('69',R.parent/'2026-10-11-r69/code/tests69.py'),('70',R.parent/'2026-10-11-r70/code/tests70.py')]
    tests={label:test(path,label) for label,path in suites}
    scripts=[('independent72',[]),('audit_contract72',[]),('tables72',[]),('independent73',[]),('tables73',[]),
        ('decision78',[]),('allocation79',[]),('study80',['--verify']),('cost80',['--replay']),('dual81',[]),('tables81',[]),
        ('cost77',['--replay']),('tables77',[]),('replay83',['--full']),('verify84',[])]
    phases={}
    for script,args in scripts:
        begin=time.perf_counter();print('Full check',script,flush=True)
        b.run([sys.executable,'code/'+script+'.py']+args,script+'-full-R84');phases[script]=time.perf_counter()-begin
    old70=R.parent/'2026-10-11-r70';report=old70/'audit/RESULT_AUDIT70.json';original=report.read_bytes()
    try:
        b.run([sys.executable,str(old70/'code/audit70.py')],'retained-record-audit70-R84',old70)
        shutil.copy2(report,R/'audit/RETAINED_REPLAY70_IN_R84.json')
    finally:report.write_bytes(original)
    tables()
    need(b.sha(R/'results83/frontier.json')=='e7eacce26ccba5590fe1ac75cf02f3b661442f71b018622412d3eb8f51364082','Original exact continuum frontier')
    need(b.sha(R/'results83/transfer.json')=='fc5bdb4741d9e2a91689fbed93ea233a3261f97a9a9d36bf2ff55c13c991800c','Original class transfer')
    docs=compile_documents();keep=preserve();check_sources()
    for path in ('audit/REPLAY77.json','audit/REPLAY80.json','audit/REPLAY83.json','audit/VERIFY84.json'):
        need(read(R/path)['status']=='passed','Complete independent check '+path)
    try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:commit=None
    abstract=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',(R/'ECTA.tex').read_text(),re.S)[1]
    source={str(p.relative_to(R)):b.sha(p) for folder in ('code','sections') for p in (R/folder).glob('*84.*')}
    for name in ('ECTA.tex','supp.tex','appendix.tex','response.md','PROTOCOL84.md','SOURCE_FREEZE84.json','CONTENT_MAP84.md','references84.bib'):source[name]=b.sha(R/name)
    b.save(R/'audit/SOURCES84.json',source)
    result=dict(status='passed',tested_source_commit=commit,documents=docs,tests=tests,total_tests=sum(t['tests'] for t in tests.values()),skipped_tests=0,
        preservation=keep,earlier_preservation=earlier,older_preservation=older,inherited_scientific_locks=oldlocks,
        original_actionwise_boxes_per_implementation=read(R/'audit/REPLAY83.json')['paired_boxes_per_implementation'],
        R77_full_bin_replay=read(R/'audit/REPLAY77.json'),R80_full_bin_replay=read(R/'audit/REPLAY80.json'),actionwise_full_bin_replay=read(R/'audit/REPLAY83.json'),
        exact_compatibility_check=read(R/'audit/VERIFY84.json'),new_results=read(R/'audit/TABLES84.json'),scientific_process=read(R/'audit/PROCESS84.json'),
        phase_seconds=phases,build_seconds=time.perf_counter()-start,source_manifest_sha256=b.sha(R/'audit/SOURCES84.json'),
        new_independent_policy_cost_rows=0,new_fitting_attempts=0,original_scientific_clocks_replaced=False,largest_vector_tree_independently_regenerated=False,
        abstract_words=len(abstract.split()),editorial_page_policy='Report actual document lengths while retaining every inherited substantive section; old internal 45-page development target is not a scientific validation gate.',
        visual_status='Separate inspection against actual PDF hashes is required; compilation alone is not visual qualification.',
        scope='All inherited and new unskipped suites; original scientific-source preservation; independently implemented complete relevant bin replay; every new exact certificate; four current ordinary-source PDFs. No new sampling, refitting, or claim of external mathematical approval.')
    b.save(R/'audit/RELEASE84.json',result)
    print(json.dumps({k:result[k] for k in ('status','tested_source_commit','documents','total_tests','preservation','new_results','build_seconds')},indent=2),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--render',action='store_true');args=p.parse_args();render() if args.render else main()
