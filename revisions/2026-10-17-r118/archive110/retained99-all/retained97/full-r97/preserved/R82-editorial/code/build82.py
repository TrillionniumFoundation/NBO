"""Full R82 original-paper build, preservation and independent record replay."""
from pathlib import Path
import ast,json,re,time
import build72 as b
import build81 as inherited
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-12-r81'

def preserve():
    a=json.loads((R/'audit/PREPARATION82.json').read_text())
    for name,h in a['protected_files'].items():
        if b.sha(R/name)!=h or b.sha(OLD/name)!=h:raise AssertionError('R81 protected bytes changed '+name)
    for name,item in a['active_sections'].items():
        if b.sha(R/(name+'.tex'))!=item['sha256']:raise AssertionError('Inherited section changed '+name)
        needle='\\input{'+name+'}'
        counts={doc:(R/doc).read_text().count(needle) for doc in ('ECTA.tex','supp.tex','appendix.tex')}
        if counts[item['document']]!=1 or sum(counts.values())!=1:raise AssertionError('Inherited section moved or duplicated '+name)
    for name,h in a['original_wrappers'].items():
        if b.sha(R/'preserved/R81-original'/name)!=h:raise AssertionError('Original wrapper missing '+name)
    for name,labels in a['wrapper_labels'].items():
        if set(labels)-set(re.findall(r'\\label\{([^}]+)\}',(R/name).read_text())):raise AssertionError('Inherited label removed '+name)
    for name,doc in (('actionwise82','ECTA'),('study82','ECTA'),('proof82','appendix')):
        needle='\\input{sections/'+name+'}'
        if (R/(doc+'.tex')).read_text().count(needle)!=1:raise AssertionError('New section not compiled '+name)
    if '\\title{Neural Bellman Operators}' not in (R/'ECTA.tex').read_text():raise AssertionError('Original title changed')
    return dict(status='passed',inherited_protected_files=len(a['protected_files']),inherited_active_sections=len(a['active_sections']),
        every_inherited_section_same_document_and_bytes=True,original_wrappers_and_outputs_preserved=True,
        baseline_commit=a['baseline_commit'],review_commit=a['review_commit'])

def response():
    b.response();p=R/'response.tex';text=p.read_text()
    text=re.sub(r'label=e\d+(?:supp|response)','label=e82response',text)
    abstract='Revision R82 develops the original Neural Bellman Operators paper in response to the 11 October 2026 advisory report on R67. Directed original-law action contrasts extend attained-controller evidence uniformly to approximately optimized continuation classes. Independent exhaustive whole-bin calculations, complete refinement costs and all inherited evidence are retained.'
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+abstract+m[2],text,count=1,flags=re.S)
    p.write_text(text)

def main():
    begin=time.perf_counter();(R/'audit/build-logs').mkdir(parents=True,exist_ok=True);(R/'build').mkdir(exist_ok=True)
    for p in (R/'code').glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    keep=preserve()
    tests=inherited.test('tests82.py','tests-82-directed-sublevel')
    b.run([__import__('sys').executable,'code/study82.py','replay'],'complete-dual-arithmetic82')
    b.run([__import__('sys').executable,'code/tables82.py'],'tables82')
    inherited.response=response
    inherited.main()
    previous=json.loads((R/'audit/RELEASE81.json').read_text())
    keep=preserve();fresh=json.loads((R/'audit/REPLAY82.json').read_text())
    if fresh['status']!='passed' or previous['status']!='passed':raise AssertionError('Incomplete independent verification')
    science=json.loads((R/'results82/summary.json').read_text())
    if science['source_freeze_sha256']!=b.sha(R/'SOURCE_FREEZE82.json'):raise AssertionError('Science freeze identity')
    sources={str(p.relative_to(R)):b.sha(p) for p in (R/'code').glob('*82.py')}
    sources.update({str(p.relative_to(R)):b.sha(p) for p in (R/'sections').glob('*82.tex')})
    for name in ('ECTA.tex','supp.tex','appendix.tex','response.md','CONTENT_MAP82.md','PROTOCOL82.md'):sources[name]=b.sha(R/name)
    b.save(R/'audit/SOURCES82.json',sources)
    result=dict(status='passed',tested_source_commit=previous['tested_source_commit'],documents=previous['documents'],
        total_tests=previous['total_tests']+tests['tests'],inherited_tests=previous['total_tests'],new_suite=tests,skipped_tests=0,
        preservation=keep,earlier_preservation=previous['preservation'],
        independent_switch_duals=previous['independent_switch_duals'],R80_full_bin_replay=previous['R80_full_bin_replay'],
        inherited_R77_full_bin_replay=previous['inherited_R77_full_bin_replay'],new_actionwise_full_replay=fresh,
        exact_pairwise_transfers=72,complete_sublevel_records=48,own_controller_transfers=24,
        new_independent_cost_rows=0,new_fit_attempts=0,original_scientific_clocks_replaced=False,
        retained_large_vector_tree_independently_regenerated=False,
        source_freeze_sha256=b.sha(R/'SOURCE_FREEZE82.json'),science_summary_sha256=b.sha(R/'results82/summary.json'),
        exact_transfer_sha256=b.sha(R/'results82/transfer.json'),tables_sha256=b.sha(R/'audit/TABLES82.json'),
        source_manifest_sha256=b.sha(R/'audit/SOURCES82.json'),build_seconds=time.perf_counter()-begin,
        visual_inspection='separate_hash_bound_gate_not_implied_by_compilation',
        scope='Four current ordinary-source documents; every inherited and new unskipped suite; all inherited original-law bin computations and switch duals; both implementations of every new paired integration box; no statistical resampling, refitting, historical clock substitution or external peer approval.')
    b.save(R/'audit/RELEASE82.json',result)
    print(json.dumps({k:result[k] for k in ('status','total_tests','documents','preservation','new_actionwise_full_replay','build_seconds')},indent=2),flush=True)
if __name__=='__main__':main()
