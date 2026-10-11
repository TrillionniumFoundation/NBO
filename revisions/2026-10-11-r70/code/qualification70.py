"""Keep qualification work distinct from an already qualified reuse service."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
def main():
    marker=R/'audit/QUALIFICATION_BOUNDARY70.json'
    if marker.exists():return
    p=R/'sections/study70.tex';s=p.read_text();s=s.replace("actual adoption still depends on complete work and the purchaser's declared prices.","adoption depends on declared prices and complete work, including newly purchased qualification.");p.write_text(s)
    p=R/'sections/supp70.tex';s=p.read_text();needle=r'\input{tables/adoption70}'
    note=r'''\paragraph{Qualification is not free.}
The displayed reuse thresholds condition on a common or previously paid qualification calculation. The process receipts cover the complete reuse service, not the separate policy-cost inference experiment. For a first purchase, let $C_q$ be additional qualification work not paid by the benchmark alternative. In Proposition~\ref{prop:adoption70}, use $W_\pi=W^{\rm run}_\pi+C_q$ and $W_\nu=W^{\rm run}_\nu$; the observed saving becomes $S-C_q$. This is a change of the explicit accounting boundary, not an additional theorem assumption about free inference. Charging the entire observed shared inference process gives $C_q$ approximately $9.03$ seconds in the small task and $408.63$ seconds in the larger task. Every displayed matched saving then becomes negative. Thus the current receipts do not identify a positive qualification-plus-reuse work saving under that conservative first-purchase boundary. An allocated marginal inference time or a longer repayment horizon was not separately executed. The machine-readable table retains both boundaries, and the general price region remains valid with the actual charged work and installation fee.
'''
    if needle not in s:raise AssertionError('Adoption table anchor')
    s=s.replace(needle,needle+'\n'+note,1);p.write_text(s)
    p=R/'code/tables70.py';s=p.read_text();s=s.replace("saving=saving,policy_cost_upper=upper", "saving=saving,qualification_seconds=x['seconds'],qualification_adjusted_saving=saving-x['seconds'],policy_cost_upper=upper")
    s=s.replace("'Conditional complete-reuse adoption thresholds'","'Conditional reuse-stage adoption thresholds'")
    s=s.replace("'Seed 6901; zero incremental installation fee. The loss upper", "'Seed 6901; zero incremental installation fee and common or previously paid qualification. The loss upper")
    s=s.replace("Prices are declared inputs, not estimated currency values.", "Newly purchased qualification work must be added before claiming a first-purchase saving. Prices are declared inputs, not estimated currency values.")
    p.write_text(s)
    p=R/'response.md';s=p.read_text();needle='## B10 and M10: Scope, style and preservation of the original paper'
    addition='The economic account now explicitly separates already qualified reuse from a first purchase of qualification. The complete reuse receipts do not include the separately paid policy-cost inference experiment. Any noncommon qualification work must therefore be added to the candidate work before applying the purchase proposition. Under the conservative boundary charging the entire observed shared inference process, approximately 9.03 or 408.63 seconds, every displayed matched work saving becomes negative. The tables and machine record distinguish these two boundaries. Neither an unmeasured marginal inference allocation nor an unexecuted longer amortization horizon is substituted for that cost.\n\n'
    if needle not in s:raise AssertionError('Response accounting anchor')
    s=s.replace(needle,addition+needle,1);p.write_text(s)
    record=dict(status='explicit_accounting_boundaries',reuse_thresholds='common or previously paid qualification',first_qualification='add any noncommon qualification cost; conservative whole shared-service allocation recorded',scientific_receipts_changed=False)
    marker.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
