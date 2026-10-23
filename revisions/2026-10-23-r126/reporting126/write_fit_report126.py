from pathlib import Path
from fractions import Fraction as Q
import json,math,hashlib
root=Path(__file__).resolve().parents[1]
rundir=root/'results126/independent-fit-attempt01'
s=json.loads((rundir/'SUMMARY126.json').read_text())
rows=[json.loads(x) for x in (rundir/'records126.jsonl').read_text().splitlines()]
p=json.loads((root/'results126/launch-fit-attempt01/PROCESS126.json').read_text())
gate=json.loads((rundir/'SOURCE_READBACK126.json').read_text())
reportp=json.loads((root/'results126/launch-fit-report-attempt01/PROCESS126.json').read_text())
def q(d):return Q(int(d['numerator']),int(d['denominator']))
def up(d):
 x=q(d)
 if not x:return '0'
 e=math.floor(math.log10(float(x)));unit=Q(10)**(e-2);z=x/unit;n=(z.numerator+z.denominator-1)//z.denominator
 assert n*unit>=x
 return format(n/100,'.2f')+'e'+str(e)
def latex_up(d):
 t=up(d)
 if t=='0':return '$0$'
 a,b=t.split('e');return '$'+a+r'\times10^{'+b+'}$'
md=['# R126 independent finite-design fitting audit: executed report','',
'The frozen audit completed all 56 declared stored-model cases with exit code 0 under source `769e3eb3ac08beaa7bb6778c1676f15e1f8d6d2b`. Its 184-file source gate matched the code, protocol, input manifest and all 181 immutable historical input files before numerical imports. The original production actors were not replaced. No new economic label, policy observation or population sample was acquired.','',
'## What was independently reproduced','',
'The audit reconstructed the predeclared fixed feature lists, rational monomial/hinge/spline/hat designs, one-sided original-action derivatives, original coefficient boxes, 30-bit ties-to-even rounding and JSON coefficient representations. It configured 24 VALUE problems for BVLS instead of the historical TRF method and independently assembled 24 shifted-variable robust MARGINAL linear programmes. The actual raw logs show four VALUE solves executed BVLS active-set iterations (three with eight iterations and one with seven); the other 20 accepted the feasible unconstrained least-squares solution at iteration zero, sharing that numerical initial-solve path with the original library. All fixed feature designs and rational certificates were independently assembled. The eight ordinary-hinge cases copied their corresponding paid ReLU audit readout, as required by the original protocol. They are not independent fitted observations.','',
'All 56 source/specification/rounding/serialization cases passed, with 227,203 exact assertions. Every one of the 28 VALUE rounded readouts matched the historical dyadic coefficients exactly. Overall, 39 of 56 rounded readouts matched; the 17 different readouts were MARGINAL cases. The same finite-design objective was unchanged in 40 cases, lower in seven and higher in nine. Counts include the explicitly matched hinge copies. Nonunique coefficient agreement was not an acceptance criterion and no refitted candidate was chosen for economic deployment.','',
'NumPy/SciPy numerical infrastructure is shared. The MARGINAL solve uses the shared HiGHS dual-simplex library; the LP solver itself was not independently implemented. The complete independently reconstructed exact designs matched every historical VALUE matrix entry. The maximum derivative entry discrepancy was exactly `3/1829587348619264`, about `1.6397140056e-15`, caused by evaluating historical binary64 entries against the rational reconstruction. The certificate target is the latter exact finite design; these discrepancies are not suppressed as symbolic equality.','',
'## Exact finite-box certificates','',
'All objective and weak-duality bounds were recomputed with rational arithmetic from the serialized readouts. VALUE uses a convex tangent minimized over the original coefficient box; MARGINAL uses normalized nonnegative rational inequality weights and exact box minimization. The largest VALUE sum-of-squares optimality-gap bound is below `2.34e-4`. The largest new MARGINAL robust-node residual gap is below `2.84e-8`; the corresponding maximum for stored historical readouts is below `2.58e-8`. The largest absolute change in a rounded MARGINAL objective is below `1.53e-8`. A finite optimality gap is reported as a bound, not an assertion of an exactly optimal solution.','',
'The following maxima include all four budget/risk cells per loss. Decimal displays are rounded upward. The two VALUE maxima coincide because all 28 VALUE rounded readouts coincide.','',
'| Representation | Exact readout matches / 8 | VALUE maximum gap (stored and audit) | MARGINAL maximum stored gap | MARGINAL maximum audit gap |','|---|---:|---:|---:|---:|']
family_order=('quadratic','relu','hinge','poly2','poly3','spline','grid')
for fam in family_order:
 z=s['families'][fam];md.append('| '+fam+' | '+str(z['exact_coefficient_matches'])+' | '+up(z['value']['independent_maximum_finite_design_gap'])+' | '+up(z['marginal']['stored_maximum_finite_design_gap'])+' | '+up(z['marginal']['independent_maximum_finite_design_gap'])+' |')
md+=['','These are optimization certificates on the fixed finite training design. They do not establish fitted approximation error on the entire continuous domain, independently reacquire the economic labels, verify a new deployed policy, or provide actor-specific population inference. R121 used fixed pre-label features; checking them does not constitute new learned feature selection. These limits remain explicit in the B8/M9 response.','',
'## Complete audit costs and custody','',
f'The external process clock was {p["seconds"]:.9f} seconds, including process startup/shutdown and all source checks, imports, 48 solves, rational checking, input/output and serialization. The internal audit clock was {s["execution"]["total_seconds"]:.9f} seconds. Peak child resident memory was {p["peak_child_rss_kib"]:,} KiB. The derivative summary process separately took {reportp["seconds"]:.9f} seconds. These are research-verification costs on a shared host, after the serial production-timing campaign had finished; other research work could run concurrently. They are not a new deployment training bill, a speed comparison with historical TRF, or a timing confidence interval.','',
'The immutable input manifest binds original acquisition source `16bf21334efcbc719b83e2ccf10e8527f8b956f2`, original actor publication `796c5f2badf68b051ac6c144884c0e61b87faf5e`, and complete recovered custody head `f6392f6909d280ecd310f152caab0fafe9091df7`. All four label files, 56 model files, 56 fit files and 56 design files remain unchanged. Every raw new solver result was stored before its exact certificate was checked; no model failed or was dropped in this attempt.','',
'Evidence: `results126/independent-fit-attempt01/EXECUTION126.json`, `SOURCE_READBACK126.json`, `ENVIRONMENT126.json`, `records126.jsonl`, `SUMMARY126.json`, and every per-model `RAW_SOLVER126.json`, `CERTIFICATE126.json`, `INPUT_IDENTITIES126.json` and `independent_model.json`. Whole-process receipt: `results126/launch-fit-attempt01/PROCESS126.json`. The summary script and its independent process receipt are in `reporting126/summarize_fit126.py` and `results126/launch-fit-report-attempt01/`.','']
assert len(gate['verified_files'])==184
md += ['## Production-report scope field','', 'The unchanged frozen production report retains `independent_refitting_executed=False` for its own service process. The separately identified, actually executed fitting audit reported here has its own source gate, protocol, inputs, raw results and whole-process receipt. Its success is not silently assigned to the production process.','']
(root/'FIT_AUDIT_REPORT126.md').write_text('\n'.join(md))
main=r'''\subsection{Independent acquisition implementation audit}
\label{sec:fitauditresults126}
The separate historical-data audit reproduces all 56 stored acquisition cases:
24 value fits, 24 robust marginal fits and eight matched hinge copies.  It
independently reconstructs the fixed features, exact designs, one-sided
original-action derivatives, dyadic rounding and serialization.  The BVLS configuration executes a distinct active-set path for four value
fits; 20 return the feasible unconstrained solution through the shared numerical
initial-solve path. All 28 value-loss rounded readouts, including four hinge
copies, reproduce the historical coefficients exactly.
Overall 39 readouts match; the 17 differing marginal readouts are retained.
All 56 cases pass the specified checks.  The maximum exact finite-box
sum-of-squares optimality-gap bound is below $2.34\times10^{-4}$; the
maximum new robust marginal gap is below $2.84\times10^{-8}$.

These results address independent acquisition implementation without changing
the deployed actors.  The marginal formulation is independently assembled but
shares the HiGHS solver; no external solver-implementation independence is
claimed.  The audit does not reacquire economic labels or prove approximation
error on the entire continuous domain.  It uses zero new economic queries and
adds 21.824 seconds of complete research verification on the shared host.
The proofs and full case records appear in the supplement and development
companion.  Finite fitting optimality and original-policy regret remain
separate quantities.
'''
table=[r'\begin{table}[t]',r'\centering\small',r'\caption{Independent finite-design fitting audit}',r'\label{tab:fitreproduction126}',r'\begin{tabular}{lrrrr}',r'\hline',r'Representation & Same / 8 & VALUE gap & Stored M gap & Audit M gap \\',r'\hline']
for fam in family_order:
 z=s['families'][fam];table.append(fam+' & '+str(z['exact_coefficient_matches'])+' & '+latex_up(z['value']['independent_maximum_finite_design_gap'])+' & '+latex_up(z['marginal']['stored_maximum_finite_design_gap'])+' & '+latex_up(z['marginal']['independent_maximum_finite_design_gap'])+r' \\')
table += [r'\hline',r'\end{tabular}',r'\par\smallskip\parbox{0.96\linewidth}{\footnotesize All four risk/budget cells per loss are retained. Positive decimal gaps are rounded upward. VALUE denotes sum squared loss; M denotes the robust marginal-node residual. VALUE coefficients coincide in every case. These are finite-design optimization gaps and do not measure economic policy regret.}',r'\end{table}']
main += '\n'+'\n'.join(table)+'\n'
main += r'The unchanged production report records \nolinkurl{independent_refitting_executed=False} for its own service scope. The separately identified audit reported here has its own execution, source-gate and research-cost receipts; it is not silently reassigned to that production process.'+'\n'
(root/'new126/fit_results126.tex').write_text(main)
tex=[r'\section{Independent finite-design fitting audit}',r'\label{dev:fitaudit126}',
'Under the actual R126 source boundary, all 56 declared cases completed with exit code zero. The source gate matched 184 files before numerical imports: the audit code, protocol, input manifest and all 181 immutable historical inputs. There were 24 VALUE and 24 MARGINAL solver invocations, plus eight matched ordinary-hinge copies of their paid ReLU readouts. No fitted actor entered the production census, and there were zero new economic queries.',
'All 227,203 exact assertions passed. Every VALUE rounded readout reproduced the historical coefficients. Overall, 39 readouts matched exactly and 17 MARGINAL readouts differed. The exact rounded objective was unchanged in 40 cases, lower in seven and higher in nine; these counts include the matched hinge copies and are not independent observations. Nonunique coefficient matching was not a pass criterion.',
'The original VALUE design entries coincide with the independent rational reconstruction. The maximum derivative-entry discrepancy is exactly $3/1829587348619264$, approximately $1.640\\times10^{-15}$. The exact finite-design certificates use the rational reconstruction. They do not assert symbolic identity of historical floating derivative matrices.',
'VALUE is independently assembled and configured for BVLS instead of historical TRF. Four actual VALUE solves execute the BVLS active set (three with eight iterations and one with seven). The other 20 accept the feasible unconstrained solution at iteration zero and share that numerical initial-solve path with the original library. Four VALUE hinge readouts copy the paid ReLU fit. The independently shifted MARGINAL formulation uses the shared HiGHS dual-simplex library. Neither implementation independence of that LP library nor independent reacquisition of economic labels is claimed.',
'\nThe following maxima retain every risk/budget cell. Displayed positive gaps are rounded upward; their full rational values are stored. The VALUE column applies to both old and new readouts because all VALUE rounded coefficients coincide.\n',r'\begin{center}\small',r'\begin{tabular}{lrrrr}',r'\hline',r'Representation & Same / 8 & VALUE gap & Stored M gap & Audit M gap \\',r'\hline']
for fam in family_order:
 z=s['families'][fam];tex.append(fam+' & '+str(z['exact_coefficient_matches'])+' & '+latex_up(z['value']['independent_maximum_finite_design_gap'])+' & '+latex_up(z['marginal']['stored_maximum_finite_design_gap'])+' & '+latex_up(z['marginal']['independent_maximum_finite_design_gap'])+r' \\')
tex +=[r'\hline',r'\end{tabular}',r'\end{center}',
'These are finite-design optimization bounds, not certificates of fitted error on the entire continuous domain. Checking the original fixed features does not create a learned feature-selection procedure. The stored and audit robust residuals differ by less than $1.53\\times10^{-8}$ in every MARGINAL case; no such change is promoted to an economic policy improvement.',
f'The complete external audit process took {p["seconds"]:.9f} seconds; the internal clock was {s["execution"]["total_seconds"]:.9f} seconds, and peak child resident memory was {p["peak_child_rss_kib"]:,} KiB. The separate descriptive summary process took {reportp["seconds"]:.9f} seconds. Production timing had finished before this research audit began. The host could execute other research computations concurrently, so these clocks are neither deployment timing samples nor a comparison with old fitting clocks. All 48 solves, rational arithmetic, input/output, source readback and serialization remain charged.',
r'\subsection{Complete fixed-case ledger}',
'The next table lists all 56 cases. Risk indices zero and one are the original levels $1/2$ and $3/4$. The gap is the exact finite-box upper bound on optimization error, displayed with upward rounding. It is sum squared loss for VALUE (V) and maximum robust node residual for MARGINAL (M). Readout equality refers to the complete rounded historical coefficient vector.',
r'\begingroup\small',r'\begin{longtable}{rrlcrrr}',r'\hline',r'Budget & Risk & Representation & Loss & Same & Finite gap & Audit seconds \\',r'\hline\endfirsthead',r'\hline Budget & Risk & Representation & Loss & Same & Finite gap & Audit seconds \\ \hline\endhead']
for x in rows:
 c=x['independent_value_certificate' if x['loss']=='value' else 'independent_marginal_certificate']
 tex.append(f'{x["budget"]} & {x["risk_index"]} & {x["arm"]} & '+('V' if x['loss']=='value' else 'M')+' & '+('1' if x['coefficient_exact_match_to_historical'] else '0')+' & '+latex_up(c['optimality_gap_upper'])+f' & {x["elapsed_seconds"]:.6f}'+r' \\')
tex +=[r'\hline\end{longtable}\endgroup',
r'The full source readback, environment, raw solver outputs, exact rational certificates, audit-only serialized models and process logs are retained under \nolinkurl{results126/independent-fit-attempt01/} and \nolinkurl{results126/launch-fit-attempt01/}. The original 56 actor bytes and four label datasets retain their original publication and acquisition identities. No failure was discarded; this attempt had zero failed model cases.']
text='\n\n'.join(tex)+'\n';filtered=[];inside=False
for line in text.splitlines():
 if r'\begin{tabular}' in line or r'\begin{longtable}' in line:inside=True
 if line or not inside:filtered.append(line)
 if r'\end{tabular}' in line or r'\end{longtable}' in line:inside=False
(root/'new126/fit_development126.tex').write_text('\n'.join(filtered)+'\n')
print(json.dumps({'report':'FIT_AUDIT_REPORT126.md','main':'new126/fit_results126.tex','development':'new126/fit_development126.tex','rows':len(rows),'source_gate_files':len(gate['verified_files'])}))
