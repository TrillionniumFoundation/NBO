"""Complete offline R81 build; the frozen scientific runs are never retimed."""
from pathlib import Path
import ast,json,re,subprocess,sys,time
import build72 as b
import build77 as inherited
import build79 as prior79
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-12-r80'

def preserve():
    a=json.loads((R/'audit/PREPARATION81.json').read_text())
    for name,h in a['protected_files'].items():
        if b.sha(R/name)!=h or b.sha(OLD/name)!=h:raise AssertionError('R80 protected file changed '+name)
    for name,item in a['active_sections'].items():
        if b.sha(R/name)!=item['sha256']:raise AssertionError('Inherited statement changed '+name)
        needle=r'\input{'+name[:-4]+'}'
        if sum((R/(doc+'.tex')).read_text().count(needle) for doc in b.DOCS[:-1])!=1:raise AssertionError('Inherited section missing/duplicated '+name)
    for name,h in a['original_wrappers'].items():
        if b.sha(R/'preserved/R80-snapshot'/name)!=h:raise AssertionError('Original wrapper missing '+name)
    for name,labels in a['wrapper_labels'].items():
        if set(labels)-set(re.findall(r'\\label\{([^}]+)\}',(R/name).read_text())):raise AssertionError('Wrapper label missing '+name)
    old=prior79.preserve()
    return dict(status='passed',protected_files=len(a['protected_files']),inherited_sections=len(a['active_sections']),all_inherited_sections_compiled_byte_identically_once=True,earlier_79_preservation=old,
        baseline_commit=a['base_commit'],review_commit=a['review_commit'])

def response():
    b.response();p=R/'response.tex';text=p.read_text()
    text=re.sub(r'label=e\d+(?:supp|response)', 'label=e81response',text)
    abstract='Revision R81 develops the original Neural Bellman Operators paper in response to the 11 October 2026 advisory report on R67. Affine-calibrated qualification, independently verified action-switch barriers and optimizer-class cost transfer are integrated with the separately frozen original-law factorial evidence. All inherited scientific records and adverse results are preserved.'
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+abstract+m[2],text,count=1,flags=re.S)
    p.write_text(text)

def test(script,label):
    started=time.perf_counter();text=b.run([sys.executable,'code/'+script],label)
    m=re.search(r'Ran (\d+) tests?',text)
    if not m or not re.search(r'^OK\s*$',text,re.M) or re.search(r'\bskipped\b',text):raise AssertionError('Complete unskipped tests required '+label)
    return dict(status='passed',tests=int(m[1]),seconds=time.perf_counter()-started)

def main():
    begin=time.perf_counter();(R/'audit/build-logs').mkdir(parents=True,exist_ok=True);(R/'build').mkdir(exist_ok=True)
    for p in (R/'code').glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    kept=preserve();tests={}
    for version in (78,79,80,81):tests[str(version)]=test(f'tests{version}.py',f'tests-{version}-current')
    # Exact old decision and allocation records continue to use their original
    # five-controller family. The R81 nine-controller closure is separately named.
    for name,args in [('decision78',[]),('allocation79',[]),('study80',['--verify']),('cost80',['--replay']),('dual81',[]),('tables81',[])]:
        b.run([sys.executable,'code/'+name+'.py']+args,name+'-R81')
    inherited.response=response
    inherited.main(full=True)
    old=json.loads((R/'audit/RELEASE77.json').read_text())
    for label in old['tests']:
        if re.search(r'OK \(skipped=',(R/'audit/build-logs'/('tests-'+label+'.log')).read_text()):raise AssertionError('Skipped inherited test '+label)
    kept=preserve();cost=json.loads((R/'audit/REPLAY80.json').read_text());transfer=json.loads((R/'audit/TRANSFER81.json').read_text())
    construction=json.loads((R/'audit/CONSTRUCTION_REPLAY80.json').read_text())
    if cost['status']!='passed' or transfer['status']!='passed' or construction['status']!='passed':raise AssertionError('Missing full numerical replay')
    manifest={str(p.relative_to(R)):b.sha(p) for p in (R/'code').glob('*81.py')}
    manifest.update({str(p.relative_to(R)):b.sha(p) for p in (R/'sections').glob('*81.tex')})
    for n in ('ECTA.tex','supp.tex','appendix.tex','response.md','CONTENT_MAP81.md'):manifest[n]=b.sha(R/n)
    b.save(R/'audit/SOURCES81.json',manifest)
    record=dict(status='passed',tested_source_commit=old['tested_source_commit'],documents=old['documents'],
        total_tests=old['total_tests']+sum(v['tests'] for v in tests.values()),inherited_tests=old['tests'],additional_suites=tests,skipped_tests=0,
        preservation=kept,earlier_preservation=old['preservation'],source_freezes_unchanged=['SOURCE_FREEZE73.json','SOURCE_FREEZE77.json','SOURCE_FREEZE80.json'],
        R80_full_bin_replay=cost,R80_construction_replay=construction,
        independent_switch_duals=transfer['independent_action_switches'],optimizer_class_comparisons=transfer['exact_optimizer_class_comparisons'],
        inherited_R77_full_bin_replay=old['independent_replay'],retained_r67_r70_tests_and_record_audits=True,
        retained_vector_tree_independently_regenerated=False,new_independent_cost_rows=0,new_fitting_attempts=0,scientific_clocks_replaced=False,
        original_cost_summary_sha256=b.sha(R/'results80/cost/summary.json'),transfer_sha256=b.sha(R/'audit/TRANSFER81.json'),
        tables_sha256=b.sha(R/'audit/TABLES81.json'),source_manifest_sha256=b.sha(R/'audit/SOURCES81.json'),
        build_seconds=time.perf_counter()-begin,visual_inspection='not_performed_by_builder',
        scope='Current-source four-document compilation, all inherited and new unskipped suites, both implementations of every new full-bin path, every new exact action-switch dual, deterministic optimizer-class and economic-choice transfer. No additional IID rows, historical service retiming, or claim of external peer approval.')
    b.save(R/'audit/RELEASE81.json',record)
    print(json.dumps({k:record[k] for k in ('status','total_tests','documents','preservation','R80_full_bin_replay','independent_switch_duals','optimizer_class_comparisons','build_seconds')},indent=2),flush=True)
if __name__=='__main__':main()
