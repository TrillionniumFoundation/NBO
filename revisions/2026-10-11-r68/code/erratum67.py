"""Independent rational witness for the preserved R66 accumulator error."""
from fractions import Fraction as F
from pathlib import Path
import numpy as np
import audit67 as a

def main():
    root=a.R.parent/'2026-10-10-r66';key='comparison-d2-T2-adaptive-s0-r0';folder=root/'results66'/key
    summary=a.read(folder/'summary.json');spec=summary['spec']
    with np.load(folder/'trace.npz') as z:trace={k:z[k] for k in z.files}
    rr,initial=a.s.workload(2,2,64,661204);new,account=a.s.paths(a.StoredActions(trace,2),initial,rr,2,spec['target'])
    x=[F(0),F(0)];value=F(0);actions=[];den=2**a.s.BINBITS
    for t in range(2):
        action=F(float(trace[f't{t}_action'][0]));actions.append(str(action));value+=a.B**t*a.rational_stage(x,[action])
        z=F(2*int(rr['shock_index'][t,0])+1,32*den)-F(1,32);x=a.rational_transition(x,[action],z)
    value+=a.B**2*a.rational_stage(x,[],True)
    oldlower=F(float(trace['cost_lo'][0]));lo=F(float(new['cost_lo'][0]));hi=F(float(new['cost_hi'][0]))
    a.need(oldlower>value,'Pinned old record does not reproduce the counterexample')
    a.need(lo<=value<=hi,'Corrected path does not enclose the rational trajectory')
    for t in range(2):a.equal(new[f't{t}_action'],trace[f't{t}_action'],'Repair changes policy')
    result=dict(status='counterexample_reproduced_and_corrected',original_commit='acf99f51bfcfa2d3f20f545eb5f598984bafdcc1',original_key=key,
        original_trace_sha256=a.sha(folder/'trace.npz'),row=0,initial_state=['0','0'],actions_exact=actions,
        rational_midpoint_cost_exact=str(value),original_lower_exact=str(oldlower),original_lower_excess_exact=str(oldlower-value),
        original_cost_interval=[float(trace['cost_lo'][0]),float(trace['cost_hi'][0])],corrected_cost_interval=[float(new['cost_lo'][0]),float(new['cost_hi'][0])],
        correction='Allocate independent lower and upper cumulative-cost buffers before in-place updates',
        original_scientific_files_modified=False,policy_actions_changed_by_reenclosure=False,additional_independent_observations=0,
        scope='A single independently computed rational midpoint refutes the original whole-bin lower endpoint. The corrected interval encloses the full bin and this midpoint; it is not a midpoint quadrature estimate.')
    a.save(a.R/'audit/ERRATUM67.json',result);print(__import__('json').dumps(result,indent=2))
if __name__=='__main__':main()
