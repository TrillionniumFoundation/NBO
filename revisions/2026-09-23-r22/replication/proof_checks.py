"""Machine checks of explicit analytic constants and execution invariants."""
from pathlib import Path
import json,sys,math
import numpy as np
from continuum import ROOT,REV,I,Q,exp,sqrt,pi,read,save

def main():
    phase_bound=Q('6.5')*(Q('.025')*2*Q('1.0625')*Q('.0625')+Q('.3')*(Q('1.0625')*Q('.5')+Q('8.5')*Q('.0625')))
    assert phase_bound.hi<Q('2.25').lo and Q('2.25').hi<(3*pi()/4).lo
    assert sqrt(Q(2)).hi<Q('1.5').lo
    density=exp(Q('.125'))/sqrt(2*pi());weight=2*Q('1.0625')*exp(Q('.04')*Q('.0625')**2)
    magnitude=(2*Q('.95'))**2*density*weight
    assert magnitude.hi<100 and density.hi<1 and weight.hi<3
    records=list((REV/'results/crossed').glob('seed*/vertex*/*/record.json'));assert len(records)==48
    assert all(read(p)['gradient_evaluations']<=400 for p in records)
    for p in (REV/'results/crossed').glob('seed*/vertex*'):
        rr=[read(f) for f in p.glob('*/record.json')];assert len(rr)==4
        assert len({r['initial_policy_sha256'] for r in rr})==1
        assert read(p/'matching.json')['exact_binary64_match']
    stress=read(REV/'results/stress/records.json')
    assert any(not r['accepted'] for r in stress)
    assert all(r['restoration_exact'] for r in stress if not r['accepted'])
    for phase in ['initial','candidate']:
        c=read(REV/f'results/full_state/{phase}_certificate.json')
        assert c['interior_cells']==1024 and c['skipped_cells']==0 and c['failed_cells']==0
    # Deterministic full-state sensitivity is diagnostic, not a uniform theorem.
    grad=np.array(read(REV/'results/full_state/state_dependence_diagnostic.json')['derivatives_action_by_point_by_state'])
    assert np.any(np.abs(grad[:,:,1])>1e-12) and np.any(np.abs(grad[:,:,2])>1e-12)
    m=read(REV/'results/moment_continuum.json')
    assert all(r['neural_adam_minus_direct_adam_uniform_payoff_gain_lower']>0 for r in m['conditional_representation_comparison'])
    assert read(REV/'results/rejection_recovery/summary.json')['accepted_after_first_rejection']
    save(REV/'results/proof_checks.json',{'status':'PASS','complex_logistic_phase_upper':float(phase_bound.hi),
          'complex_pair_integrand_upper':float(magnitude.hi),'cauchy_M_used':100,'crossed_configurations':48,
          'complete_domain_cells_per_audit':1024,'skipped_cells':0,'matched_policy_blocks':12,
          'all_registered_configurations_retained':True,'note':'analytic inequalities and code invariants; not a proof-assistant check'})
if __name__=='__main__':main()
