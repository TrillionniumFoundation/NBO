"""Full offline R78 build. No new scientific execution or retiming."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,time
import build77 as prior
import build72 as b
import decision78 as decision
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-11-r77'

def preservation():
    rec=json.loads((R/'audit/PREPARATION78.json').read_text())
    for name,h in rec['unchanged_active_sections'].items():
        if b.sha(R/name)!=h or b.sha(OLD/name)!=h:raise AssertionError('Changed R77 section '+name)
        needle='\\input{'+name[:-4]+'}'
        count=sum((R/(doc+'.tex')).read_text().count(needle) for doc in b.DOCS[:-1])
        if count!=1:raise AssertionError(('R77 section omitted or duplicated',name,count))
    for name,h in rec['original_wrappers'].items():
        if b.sha(R/'preserved/R77-original'/name)!=h:raise AssertionError('Original R77 wrapper changed')
    for name,labels in rec['wrapper_labels'].items():
        after=set(re.findall(r'\\label\{([^}]+)\}',(R/name).read_text()))
        if set(labels)-after:raise AssertionError('Inherited wrapper label missing')
    for name,h in rec['unchanged_evidence'].items():
        if b.sha(R/name)!=h or b.sha(OLD/name)!=h:raise AssertionError('Changed historical scientific evidence '+name)
    return dict(status='passed',R77_active_sections=len(rec['unchanged_active_sections']),
        R77_evidence_files=len(rec['unchanged_evidence']),all_R77_sections_compiled_byte_identically_once=True,
        original_wrappers_retained=True,base_commit=rec['base_commit'],review_commit=rec['controlling_review_commit'])

def main():
    start=time.perf_counter();(R/'audit/build-logs').mkdir(parents=True,exist_ok=True)
    kept=preservation();decision.main()
    text=b.run([sys.executable,'code/tests78.py'],'tests-78-sharp-choice')
    m=re.search(r'Ran (\d+) tests?',text)
    if not m or not re.search(r'^OK\s*$',text,re.M):raise AssertionError('New exact test success missing')
    newtests=int(m[1]);prior.main(full=True)
    old=json.loads((R/'audit/RELEASE77.json').read_text());analysis=json.loads((R/'audit/DECISION78.json').read_text())
    kept=preservation()
    report=dict(status='passed',tested_source_commit=old['tested_source_commit'],documents=old['documents'],
        full_inherited_tests=old['tests'],inherited_test_count=old['total_tests'],new_exact_tests=newtests,
        total_tests=old['total_tests']+newtests,preservation=kept,earlier_preservation=old['preservation'],
        inherited_full_bin_trajectories_per_implementation=old['independent_replay']['full_bin_trajectories_per_implementation'],
        inherited_exact_midpoint_trajectories=old['independent_replay']['exact_midpoint_trajectories'],
        cost_replay_status=old['independent_replay']['status'],recomputed_cost_estimands=old['independent_replay']['recomputed_estimands'],
        inherited_cost_rows=old['new_independent_policy_cost_rows'],new_scientific_services=0,new_simulation_rows=0,
        scientific_clocks_replaced=False,original_cost_summary_sha256=b.sha(R/'results77/summary.json'),
        inherited_scientific_freeze_sha256=b.sha(R/'SOURCE_FREEZE77.json'),decision_sha256=b.sha(R/'audit/DECISION78.json'),
        decision_summary={k:analysis[k] for k in ('strict_cost_order','zero_charge_winners','zero_charge_regrets','matched_gains','strict_transitive_pair_improvements','checked_attaining_potentials','independent_algorithms_agree')},
        refinement_fee={k:analysis['refinement_fee'][k] for k in ('lower','upper','minimax_switch')},
        seconds=time.perf_counter()-start,visual_status='not_assessed_by_builder',
        scope='Full inherited numerical and mathematical suites, every inherited R77 cost bin independently re-evaluated twice, 30 exact cost intervals, new attainable simultaneous choice and fee checks, and four compiled ordinary-source documents. Graph postprocessing creates no observations.')
    b.save(R/'audit/RELEASE78.json',report)
    files={str(p.relative_to(R)):b.sha(p) for p in R.rglob('*') if p.is_file() and not any(x in p.relative_to(R).parts for x in ('__pycache__','build','audit'))}
    b.save(R/'audit/PUBLICATION_FILES78.json',files)
    print(json.dumps({k:report[k] for k in ('status','total_tests','documents','preservation','decision_summary','refinement_fee','seconds')},indent=2),flush=True)
if __name__=='__main__':main()
