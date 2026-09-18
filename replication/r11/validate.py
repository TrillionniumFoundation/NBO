"""Independent checks of the deposited R11 evidence (no inherited checkpoints)."""
from pathlib import Path
import json
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'replication/r11/output'
def read(name):return json.loads((OUT/(name+'.json')).read_text())
def main():
    checks={}; a=read('chord_certificate');b=read('count_certificate');d=read('dominance');v=read('validation')
    assert a['box']==b['box']==d['box']
    for z in (a,b):
        assert z['certified'] and z['bounds']['adjusted'][0]>.00018762
        assert z['bounds']['zero'][1]<-.00012218
        assert z['bounds']['active_surrender_gain'][0]>.000034708
        assert z['bounds']['adjusted'][1]<.00020240 and z['bounds']['zero'][0]>-.00017930
        assert z['bounds']['adjusted'][0]-z['bounds']['zero'][1]>.0003098
    checks['both_joint_certificates']=True
    assert len(d['dates'])==8 and d['reachable_counts']==[1,30,100,203,342,495,637,735,833]
    assert max(z['negative_minus_zero_upper'] for z in d['dates'])<-.000070902
    checks['strict_reachable_transport']=True
    arr=np.load(OUT/'certificate_arrays.npz',allow_pickle=False)
    assert np.all(arr['interval_lower']<=arr['interval_upper'])
    assert arr['reachable'].sum(axis=1).tolist()==d['reachable_counts']
    for k in arr.files:
        assert np.isfinite(arr[k]).all(),k
        if '.first.' in k and '.positive.' in k:assert arr[k][2]>0,k
    checks['deposited_coefficients_support_and_feasibility']=True
    knots=np.load(OUT/'first_date_operator.npz',allow_pickle=False)
    for k in (0,1):assert np.all(knots[f'csr.{k}.data']>=0)
    assert len(knots['actions'])>0
    stress=read('stress');assert len(stress['cases'])==12
    assert max(stress['maximum_report_replay_error'],stress['maximum_selected_direct_error'])<2e-11
    checks['all_joint_adverse_replays']=True
    dirs=read('directional');assert len(dirs['nine_point_replays'])==9
    assert max(max(r['up_full_initial_error'],r['down_zero_initial_error']) for r in dirs['nine_point_replays'])<2e-11
    w=dirs['alternative_initial_state'];assert abs(w['full_minus_up']-1.221130888309406)<2e-11
    assert abs(w['down_minus_zero']-1.302731114145440)<2e-11
    checks['directions_and_adverse_state']=True
    mech=read('mechanism')
    for key in ('noncancellable','active_center'):
        for s in ('positive','nonpositive'):assert mech[key][s]['reconstruction_error']<2e-11
    checks['dynamic_selected_control_decomposition']=True
    inst=read('institutions')
    for rows in inst['frontiers'].values():
        assert len(rows)==8 and max(z['implemented_value_error'] for z in rows)<2e-11
        assert np.all(np.diff([z['exact_statewise_capacity'] for z in rows])<=0)
    for z in inst['choices']:
        assert z['chosen_term']==int(np.argmin(z['all_eight_costs']))+1
        assert abs(z['total_procurement_cost']-z['grant']-z['term_cost'])<2e-13
        assert z['chosen_term']==({0.:8,.005:8,.01:7,.02:1,.04:1}[z['term_cost_rate']])
    checks['priced_instrument_selection_and_strict_implementation']=True
    assert len(v['direct_interior_points'])==6 and v['all_required_checks_passed']
    assert v['arithmetic']['derived_per_class_bound']<v['arithmetic']['per_class_allowance']==1e-7
    work=read('work_account')
    for method in ('chord','count'):
        total=sum(work[k] for k in ('constructor_seconds','shared_endpoint_seconds','validation_seconds',method+'_nonendpoint_seconds'))
        assert abs(total-work[method+'_matched_total_seconds'])<1e-9
    checks['arithmetic_and_matched_work_account']=True
    result={'all_passed':True,'checks':checks,'check_groups':len(checks)}
    (OUT/'independent_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
