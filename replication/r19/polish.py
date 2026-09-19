"""Reconcile notation and evidence scope in generated current sources only.

Every historical source remains untouched. The exact rational auxiliary checks
below concern the examples stated in the normalized supplementary interface.
"""
from fractions import Fraction as Q
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'revisions/2026-09-20-r19/paper';O=ROOT/'replication/r19/output'

def change(path,old,new):
    s=path.read_text()
    if old in s:path.write_text(s.replace(old,new))
    elif new not in s:raise ValueError('expected source not found: '+str(path)+' '+old[:80])

def main():
    m=P/'main.tex'
    change(m,"write a policy's payoff at the central benefit as $B-FH$, absorbing $dA$ into $B$.","write a policy's payoff at the central benefit as $\\mathcal B-FH$, where $\\mathcal B=B+dA$ includes the fixed operating benefit.")
    change(m,' B+\\delta A-F_iH\\leq U(d+\\delta,F_i).',' \\mathcal B+\\delta A-F_iH\\leq U(d+\\delta,F_i).')
    change(m,'$B-FH\\geq L(d,F_i)-(F-F_i)h_i-\\eta$','$\\mathcal B-FH\\geq L(d,F_i)-(F-F_i)h_i-\\eta$')
    change(m,'new value queries charge $10^{-10}$ only after the audit verifies that this allowance covers their operations.','retained finer value queries charge $10^{-10}$ only after the audit verifies that this allowance covers their operations. The new initial-threshold and repeated-proposal checks conservatively charge $10^{-7}$ per value.')
    change(m,"Accordingly, the paper's executed strict inequalities are about the hash-identified settlement array economy","Accordingly, the settlement application's executed strict inequalities are about the hash-identified settlement array economy")
    op=P/'interface_operator.tex'
    change(op,'For a difference of two certified bounds, the same conclusion applies to the combined signed coefficient of a shared error vector.','For a correctly oriented lower-minus-upper comparison, the corresponding error allowance uses the combined signed coefficient of the shared error vector. Subtracting two upper bounds alone does not certify a payoff difference.')
    change(op,'Let the terminal error be bounded by $E_{N,t}$. Recursively define','Let the terminal error be bounded by $E_{N,t}$ and initialize $E^+_{N,t}=E^-_{N,t}=E_{N,t}$. Recursively define')
    info=P/'interface_information.tex'
    old='In a two-period example, taking an action with loss $0.06$ at both dates passes a local $0.1$ cutoff twice but loses $0.12$ initially.'
    new='In a two-period example, taking an action with loss $0.01$ at both dates passes a local $0.01$ cutoff twice but loses $0.02$ initially.'
    change(info,old,new)
    change(info,'The exact rational fixtures in the supplement check both the occupancy identity and the local-cutoff counterexample.','The exact rational fixtures check the two-date and rare-state loss examples; the complete occupancy identity is proved below.')
    # Independent rational examples, with every probability and loss explicit.
    eta=Q(1,100);occupancy=[Q(1),Q(1)];loss=[eta,eta]
    total=sum(x*l for x,l in zip(occupancy,loss));rare=Q(1,100)*Q(1)
    coeff=[Q(3),Q(-2),Q(-1)];shared=sum(coeff)*Q(1,1000);independent=sum(abs(x) for x in coeff)*Q(1,1000)
    if not (total==Q(1,50)>eta and rare==eta and shared==0 and independent==Q(3,500)):
        raise ValueError('auxiliary rational example failed')
    record=dict(schema='nbo-r19-auxiliary-rational-v1',passed=True,two_date_loss=str(total),global_budget=str(eta),rare_state_expected_loss=str(rare),shared_error_charge=str(shared),independent_error_charge=str(independent),scope='Exact examples of global occupancy weighting and correctly oriented shared-error accounting; not an empirical constructor correlation assumption.')
    (O/'auxiliary_validation.json').write_text(json.dumps(record,indent=2)+'\n')
    print('Current-source notation and signed-error scope reconciled; exact auxiliary examples passed.')
if __name__=='__main__':main()
