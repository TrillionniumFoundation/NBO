"""R79 full source-bound verification; inherited scientific services are not retimed."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,time
import build72 as b
import build77 as old77
import decision78 as decision
import allocation79 as allocation
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-11-r78'

def preserve():
    rec=json.loads((R/'audit/PREPARATION79.json').read_text())
    for name,h in rec['active_sections'].items():
        if b.sha(R/name)!=h or b.sha(OLD/name)!=h:raise AssertionError('Inherited active section changed '+name)
        needle='\\input{'+name[:-4]+'}'
        if sum((R/(doc+'.tex')).read_text().count(needle) for doc in b.DOCS[:-1])!=1:raise AssertionError('Section omitted or duplicated '+name)
    for name,h in rec['original_wrappers'].items():
        if b.sha(R/'preserved/R78-original'/name)!=h:raise AssertionError('Original wrapper not preserved '+name)
    for name,labels in rec['wrapper_labels'].items():
        if set(labels)-set(re.findall(r'\\label\{([^}]+)\}',(R/name).read_text())):raise AssertionError('Inherited wrapper label removed')
    for name,h in rec['inherited_evidence'].items():
        if b.sha(R/name)!=h or b.sha(OLD/name)!=h:raise AssertionError('Historical evidence changed '+name)
    return dict(status='passed',R78_active_sections=len(rec['active_sections']),inherited_evidence_files=len(rec['inherited_evidence']),
        every_inherited_section_compiled_byte_identically_once=True,original_wrappers_retained=True,
        baseline_commit=rec['base_commit'],review_commit=rec['review_commit'])

def response79():
    b.response();p=R/'response.tex';text=p.read_text()
    text=re.sub(r'label=e\d+(?:supp|response)', 'label=e79response',text)
    abstract='Revision R79 responds to the 11 October 2026 advisory report on R67. The original Neural Bellman Operators paper retains attained continuation fits and their original-law cost comparisons, and adds sharp deployment allocation with installation charges and finite-cohort implementation. All inherited scientific observations and unfavorable results are preserved.'
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+abstract+m[2],text,count=1,flags=re.S)
    p.write_text(text)

def main():
    start=time.perf_counter();(R/'audit/build-logs').mkdir(parents=True,exist_ok=True)
    keep=preserve();allocation.main()
    text=b.run([sys.executable,'code/tests79.py'],'tests-79-allocation')
    match=re.search(r'Ran (\d+) tests?',text)
    if not match or not re.search(r'^OK\s*$',text,re.M) or 'skipped' in text:raise AssertionError('Complete unskipped new test success required')
    n=int(match[1])
    # Only the publication wrapper is adapted. Every scientific test, interval
    # implementation and source-freeze check runs through the inherited builder.
    old77.response=response79
    # R78 never deposited PREPARATION78.json. Do not manufacture a past
    # success record: the R79 manifest above checks all actual R78 sections and
    # evidence. Execute its exact decision calculation and tests directly.
    decision.main()
    choice_log=b.run([sys.executable,'code/tests78.py'],'tests-78-sharp-choice')
    cm=re.search(r'Ran (\d+) tests?',choice_log)
    if not cm or not re.search(r'^OK\s*$',choice_log,re.M) or re.search(r'OK \(skipped=',choice_log):
        raise AssertionError('Complete inherited sharp-choice tests required')
    choice_tests=int(cm[1])
    old77.main(full=True)
    previous=json.loads((R/'audit/RELEASE77.json').read_text())
    for label in previous['tests']:
        log=(R/'audit/build-logs'/('tests-'+label+'.log')).read_text()
        if re.search(r'OK \(skipped=',log):raise AssertionError('Skipped inherited test: '+label)
    choice=json.loads((R/'audit/ALLOCATION79.json').read_text());keep=preserve()
    record=dict(status='passed',tested_source_commit=previous['tested_source_commit'],documents=previous['documents'],
        total_tests=previous['total_tests']+choice_tests+n,inherited_test_count=previous['total_tests'],
        inherited_sharp_choice_tests=choice_tests,new_exact_tests=n,full_inherited_tests=previous['tests'],
        skipped_tests=0,preservation=keep,earlier_preservation=previous['preservation'],
        prior_incomplete_wrapper='R78 missing PREPARATION78.json; actual 30-section R79 byte preservation replaces that unavailable publication wrapper, not any scientific test',
        inherited_full_bin_trajectories_per_implementation=previous['independent_replay']['full_bin_trajectories_per_implementation'],
        inherited_exact_midpoint_trajectories=previous['independent_replay']['exact_midpoint_trajectories'],
        cost_replay_status=previous['independent_replay']['status'],recomputed_cost_estimands=previous['independent_replay']['recomputed_estimands'],
        inherited_cost_rows=previous['new_independent_policy_cost_rows'],new_scientific_services=0,new_simulation_rows=0,
        scientific_clocks_replaced=False,original_cost_summary_sha256=b.sha(R/'results77/summary.json'),
        original_source_freeze_sha256=b.sha(R/'SOURCE_FREEZE77.json'),allocation_sha256=b.sha(R/'audit/ALLOCATION79.json'),
        allocation_summary={k:choice[k] for k in ('gain_lower','gain_upper','midpoint_fee','midpoint_mixed_regret','midpoint_pure_regret','exact_full_catalogue_lp_probes','finite_cohort_probes')},
        seconds=time.perf_counter()-start,visual_status='not_assessed_by_builder',
        scope='Full inherited scientific/mathematical suites; both implementations re-evaluate all retained R77 cost bins; exact pure and mixed decision primal-dual checks; four current ordinary-source documents. No new simulations or scientific retiming.')
    b.save(R/'audit/RELEASE79.json',record)
    b.save(R/'audit/PUBLICATION_FILES79.json',{str(p.relative_to(R)):b.sha(p) for p in R.rglob('*') if p.is_file() and not any(x in p.relative_to(R).parts for x in ('__pycache__','build','audit'))})
    print(json.dumps({k:record[k] for k in ('status','total_tests','documents','preservation','allocation_summary','seconds')},indent=2),flush=True)
if __name__=='__main__':main()
