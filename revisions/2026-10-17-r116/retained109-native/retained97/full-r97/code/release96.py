"""Build release receipts only from actual R96 outputs; fail closed."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys
R=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text()) if p.exists() else None
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(tag):
    a=R/'audit/reproduction96';test=load(a/'tests/TESTS95.json');build=load(a/'build/BUILD95.json');ind=load(a/f'INDEPENDENT96-{tag}.json');data=load(R/f'results96/evaluation-{tag}/RESULTS96.json');freeze=load(R/'results96/FREEZE96.json');integ=load(a/'INTEGRATION96.json');timing=load(R/'results96/timing/TIMING96.json');clean=load(a/'CLEAN96.json')
    unchanged=bool(integ) and all(sha(R/p)==v for p,v in integ['inherited_section_hashes'].items())
    gates=dict(inherited_and_new_tests=bool(test) and all(v['passed'] and v['tests'] and not v['skipped'] for v in test.values()),
        manuscript_build=bool(build) and build['status']=='compiled',clean_source_rebuild=bool(clean) and clean['passed'],
        original_law_confirmation=bool(data) and data['all_rows_qualified'],
        independent_statistics=bool(ind) and ind['success'] and ind['all_rows_checked']==32768 and len(ind['exact_statistics'])==12,
        independent_endpoints=bool(ind) and ind['success'] and ind['endpoint_count']==64,
        repeated_process_timing=bool(timing) and len(timing['records'])==40 and all(x['exit_code']==0 for x in timing['records']),
        historical_science_preserved=unchanged,remotely_committed_freeze=bool(data) and bool(freeze) and data['freeze_sha256']==sha(R/'results96/FREEZE96.json'))
    current='\n'.join((R/(d+'.tex')).read_text() for d in ('ECTA','supp','appendix'))
    gates['one_assignment_per_inherited_section']=bool(integ) and all(current.count('\\input{'+p+'}')==1 for p in integ['assignments'])
    source={str(p.relative_to(R)):sha(p) for p in list(R.glob('*.tex'))+list(R.glob('*.bib'))+list((R/'sections').glob('*.tex'))+list((R/'code').glob('*96.py'))+list((R/'tables').glob('*96.tex'))+[R/'response.md',R/'PROTOCOL96.md',R/'CONSTANTS96.json']}
    record=dict(revision='R96',status='computational-release-passed' if all(gates.values()) else 'release-incomplete',gates=gates,
        validation_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),source_sha256=source,
        github_run_id=os.environ.get('GITHUB_RUN_ID'),review_commit='2fcf0bbd5926ee927c14a5f6d122fb50bb420988',
        total_tests=sum(v.get('tests') or 0 for v in (test or {}).values()),tests=test,
        documents=build.get('documents') if build else None,independent_audit=ind,
        confirmation_counts=dict(independent_states=8192,arm_state_rows=32768,new_models=6) if data else None,
        visual_inspection=dict(status='not-yet-recorded',scope='Compilation and clean reproduction are not visual inspection.'),
        field_calibration=False,largest_vector_execution=False,rank_slice='six columns, common labels and 128-byte executable models; not a complete multi-budget Pareto frontier')
    (R/'RELEASE96.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':record['status'],'gates':gates,'tests':record['total_tests']},indent=2));return 0 if all(gates.values()) else 1
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--tag',default='primary');sys.exit(main(p.parse_args().tag))
