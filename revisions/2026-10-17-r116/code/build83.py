"""Full ordinary-source R83 build and independently regenerated evidence."""
from pathlib import Path
import argparse,ast,json,re,sys,time
import build72 as b
import build81 as inherited
import freeze83
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-12-r82'

def preserve():
    a=json.loads((R/'audit/PREPARATION83.json').read_text())
    for name,h in a['protected_files'].items():
        if b.sha(R/name)!=h or b.sha(OLD/name)!=h:raise AssertionError('Inherited bytes changed '+name)
    for name,item in a['active_sections'].items():
        if b.sha(R/(name+'.tex'))!=item['sha256']:raise AssertionError('Inherited section changed '+name)
        needle='\\input{'+name+'}'
        counts={doc:(R/doc).read_text().count(needle) for doc in ('ECTA.tex','supp.tex','appendix.tex')}
        if counts[item['document']]!=1 or sum(counts.values())!=1:raise AssertionError('Section moved, omitted or duplicated '+name)
    for name,h in a['original_wrappers'].items():
        if b.sha(R/'preserved/R82-attempt'/name)!=h:raise AssertionError('Original wrapper changed '+name)
    for doc,labels in a['wrapper_labels'].items():
        if set(labels)-set(re.findall(r'\\label\{([^}]+)\}',(R/doc).read_text())):raise AssertionError('Inherited label removed')
    if b.sha(R/'preserved/R82-attempt-audit/build-logs/execute82.log')!=a['inherited_failed_log_sha256']:raise AssertionError('Failed attempt record changed')
    for section,doc in [('actionwise82','ECTA'),('frontier83','ECTA'),('study83','ECTA'),('proof82','appendix'),('proof83','appendix'),('study82','appendix')]:
        if (R/(doc+'.tex')).read_text().count('\\input{sections/'+section+'}')!=1:raise AssertionError('Uncompiled new section '+section)
    if '\\title{Neural Bellman Operators}' not in (R/'ECTA.tex').read_text():raise AssertionError('Original title changed')
    return dict(status='passed',protected_files=len(a['protected_files']),active_inherited_sections=len(a['active_sections']),every_inherited_section_same_bytes_same_document_once=True,
        interrupted_R82_preserved=True,complete_paper_commit=a['complete_paper_commit'],review_commit=a['review_commit'])

def response():
    b.response();p=R/'response.tex';text=p.read_text();text=re.sub(r'label=e\d+(?:supp|response)','label=e83response',text)
    abstract='Revision R83 develops the original Neural Bellman Operators paper in response to the 11 October 2026 advisory report on R67. Actionwise cost transfer and exact economic stopping frontiers qualify a continuum of approximately optimized continuations. The original-law evidence, all inherited sections and the interrupted integration record are retained.'
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+abstract+m[2],text,count=1,flags=re.S);p.write_text(text)

def compile_only():
    # Development rendering cannot issue a release or waive scientific gates.
    (R/'build').mkdir(exist_ok=True);(R/'audit/build-logs').mkdir(parents=True,exist_ok=True);response()
    for name in b.DOCS:(R/'build'/(name+'.bbl')).unlink(missing_ok=True)
    for it in range(5):
        for name in b.DOCS:
            b.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build',name+'.tex'],name+'-development'+str(it))
            if it==0 and name!='response':b.bibliography(name)
    result=[b.pdf_record(name) for name in b.DOCS];print(json.dumps(result,indent=2));return result

def main():
    start=time.perf_counter();(R/'audit/build-logs').mkdir(parents=True,exist_ok=True);(R/'build').mkdir(exist_ok=True)
    freeze83.verify();keep=preserve()
    for p in (R/'code').glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    tests={str(n):inherited.test(f'tests{n}.py',f'tests-{n}-R83') for n in (82,83)}
    ex=json.loads((R/'results83/EXECUTION83.json').read_text());clock=json.loads((R/'results83/EXECUTION_CLOCK83.json').read_text())
    if ex['status']!='passed' or not ex['full_reintegration'] or b.sha(R/'results83/EXECUTION83.json')!=clock['execution_sha256']:raise AssertionError('Missing complete source-bound recovery')
    if ex['source_freeze83_sha256']!=b.sha(R/'SOURCE_FREEZE83.json'):raise AssertionError('Recovery not bound to this locked source')
    b.run([sys.executable,'code/replay83.py','--full'],'full-paired-replay83')
    b.run([sys.executable,'code/frontier83.py'],'exact-economic-frontier83')
    b.run([sys.executable,'code/tables83.py'],'tables83')
    # Check the exact economic objects against the independent local development
    # calculation; these hashes are not a prospective statistical commitment.
    if b.sha(R/'results83/frontier.json')!='e7eacce26ccba5590fe1ac75cf02f3b661442f71b018622412d3eb8f51364082':raise AssertionError('Exact frontier differs from development cross-check')
    if b.sha(R/'results83/transfer.json')!='fc5bdb4741d9e2a91689fbed93ea233a3261f97a9a9d36bf2ff55c13c991800c':raise AssertionError('Exact transfers differ from development cross-check')
    inherited.response=response;inherited.main()
    old=json.loads((R/'audit/RELEASE81.json').read_text());keep=preserve();freeze83.verify()
    replay=json.loads((R/'audit/REPLAY83.json').read_text());frontier=json.loads((R/'results83/frontier.json').read_text())
    if old['status']!='passed' or replay['status']!='passed' or frontier['status']!='passed':raise AssertionError('Incomplete gates')
    if b.sha(R/'results83/EXECUTION83.json')!=clock['execution_sha256']:raise AssertionError('Execution clocks replaced by replay')
    result=dict(status='passed',tested_source_commit=old['tested_source_commit'],documents=old['documents'],
        total_tests=old['total_tests']+sum(x['tests'] for x in tests.values()),inherited_test_count=old['total_tests'],new_suites=tests,skipped_tests=0,
        preservation=keep,earlier_preservation=old['preservation'],source_freeze83_sha256=b.sha(R/'SOURCE_FREEZE83.json'),
        R80_full_bin_replay=old['R80_full_bin_replay'],R77_full_bin_replay=old['inherited_R77_full_bin_replay'],independent_switch_duals=old['independent_switch_duals'],new_actionwise_replay=replay,
        frontier_strata=frontier['model_tolerance_strata'],frontier_targets=frontier['comparison_targets'],independent_frontier_grid_checks=frontier['independent_frontier_grid_checks'],
        execution83_sha256=b.sha(R/'results83/EXECUTION83.json'),frontier_sha256=b.sha(R/'results83/frontier.json'),transfer_sha256=b.sha(R/'results83/transfer.json'),
        new_independent_cost_rows=0,new_fitting_attempts=0,original_scientific_clocks_replaced=False,largest_vector_tree_independently_regenerated=False,
        build_seconds=time.perf_counter()-start,visual_inspection='separate_hash_bound_gate_not_implied_by_compilation',
        scope='Four ordinary-source documents; every inherited and new unskipped suite; full R77/R80 and actionwise bin replay; exact dual and continuum-frontier verification. No statistical resampling, refitting, replacement of original scientific clocks, or claim of external peer approval.')
    b.save(R/'audit/RELEASE83.json',result)
    print(json.dumps({k:result[k] for k in ('status','total_tests','documents','preservation','frontier_strata','frontier_targets','independent_frontier_grid_checks','build_seconds')},indent=2),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--compile-only',action='store_true');a=p.parse_args();compile_only() if a.compile_only else main()
