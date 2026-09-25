#!/usr/bin/env python3
"""Assemble a self-contained R42 manuscript without changing prior revisions."""
import hashlib,json,math,platform,shutil,statistics,sys
from fractions import Fraction as F
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[1];OLD=ROOT/'revisions/2026-09-25-r40';PAPER=BASE/'paper';GEN=PAPER/'generated'
GEN.mkdir(exist_ok=True,parents=True)
# Copy only inherited dependencies needed by the new main, not the old current index.
for name in ['preamble.tex','main.tex','main_part1.tex','main_part2.tex','main_part3.tex','main_part4.tex','witness_theorem.tex','economic_margin.tex','references.tex']:
    text=(OLD/'paper'/name).read_text().replace('revisions/2026-09-25-r40/paper','revisions/2026-09-25-r42/paper')
    if name=='preamble.tex':text=text.replace('Revision R40','Revision R42')
    (PAPER/name).write_text(text)
for f in (OLD/'paper/generated').iterdir():
    if f.is_file():shutil.copyfile(f,GEN/f.name)

def outdecimal(x,places=9,upper=False):
    x=F(x);scale=10**places;n=x*scale
    k=-((-n.numerator)//n.denominator) if upper else n.numerator//n.denominator
    return f'{k//scale}.{k%scale:0{places}d}'
def sci_up(x):
    v=float(F(x))
    if v==0:return '0'
    power=math.floor(math.log10(v));coeff=math.ceil(v/10**power*1000)/1000
    return rf'${coeff:.3f}\!\times\!10^{{{power}}}$'

suite=json.loads((BASE/'results/structured_suite.json').read_text())
rows=[];work=[]
for i,r in enumerate(suite['outcomes']):
    n,T,m,law,b,e=r['case'];tag={'band':'B','cycle':'C','dense':'D'}[law]
    if r['status']!='certified':
        rows.append(f'{n}&{T}&{m}&{tag}&{float(F(b)):g}&{float(F(e)):g}&---&---&failed \\\\');continue
    rows.append(f'{n}&{T}&{m}&{tag}&{float(F(b)):g}&{float(F(e)):g}&{outdecimal(r["lower"])}&{outdecimal(r["upper"],upper=True)}&{sci_up(r["gap"])} \\\\')
    work.append(f'{i+1}&{n*T}&{r["variables"]}&{r["nonzeros"]}&{r["lp_seconds"]:.4f}&{r["unreduced"]["seconds"]:.4f}&{r["exact_certificate_seconds"]:.4f}&{r["independent"]["seconds"]:.4f}&{r["proof_bytes"]} \\\\')
(GEN/'structured_rows.tex').write_text('\n'.join(rows)+'\n');(GEN/'structured_work.tex').write_text('\n'.join(work)+'\n')
density=json.loads((BASE/'results/density_transfer.json').read_text());rows=[];detail=[]
for d in density['outcomes']:
    width=f'{float(F(d["gap"])):.6f}' if d['applicable'] else '---'
    rows.append(f'{float(F(d["zeta"])):g}&{float(F(d["operator_alpha"])):g}&{float(F(d["a"])):.6f}&{float(F(d["b"])*2):.6f}&{width}&'+('paired' if d['applicable'] else 'condition fails')+' \\\\')
    if d['applicable']:
        detail.append(f'{float(F(d["zeta"])):g}&{sci_up(d["finite_plus_gap"])}&{sci_up(d["finite_minus_gap"])}&{float(F(d["cost_error_twice"])):.6f}&{float(F(d["repair_cost_bound"])):.6f}&{float(F(d["total_theorem_bound"])):.6f} \\\\')
(GEN/'density_rows.tex').write_text('\n'.join(rows)+'\n');(GEN/'density_budget.tex').write_text('\n'.join(detail)+'\n')
primary=json.loads((OLD/'results/primary_combined.json').read_text())['outcomes'];summ=[];detail=[];statistics_out=[]
for T in (4,8,12):
    cohort=[r for r in primary if r['T']==T];pos=[r for r in cohort if F(r['initial_bounds']['uniform']['upper'])>0]
    gaps=[F(r['initial_bounds']['uniform']['relative_gap']) for r in pos]
    savings=[F(r['initial_bounds']['uniform']['deterministic_lower'])-F(r['initial_bounds']['uniform']['upper']) for r in pos]
    positive=[v for v in savings if v>0]
    med=statistics.median(gaps); mx=max(gaps)
    statistics_out.append(dict(T=T,positive_intervals=len(pos),zero_cost=len(cohort)-len(pos),median_relative_gap=str(med),max_relative_gap=str(mx),strict_savings_count=len(positive),minimum_positive_guaranteed_saving=str(min(positive)),maximum_guaranteed_saving=str(max(positive))))
    summ.append(f'{T}&{len(pos)}&{100*float(med):.2f}&{100*float(mx):.2f}&{len(positive)}&{float(min(positive)):.6f}&{float(max(positive)):.6f} \\\\')
for r in primary:
    b=r['initial_bounds']['uniform'];s=F(b['deterministic_lower'])-F(b['upper'])
    detail.append(f'{r["T"]}&{r["proposal"]}&{float(F(r["epsilon"])):g}&{float(F(b["lower"])):.6f}&{float(F(b["upper"])):.6f}&{float(s):.6f}&{100*float(F(b["relative_gap"])):.2f} \\\\')
(GEN/'primary_gap_savings.tex').write_text('\n'.join(summ)+'\n');(GEN/'primary_savings_full.tex').write_text(('\n'.join(detail)+'\n').replace('_', r'\_'))
(BASE/'results/primary_gap_savings.json').write_text(json.dumps(dict(source='R40 primary_combined.json; exact re-tabulation, not a rerun',outcomes=statistics_out),indent=2)+'\n')

p=PAPER/'main_part1.tex';text=p.read_text()
start=text.index('\\begin{abstract}');end=text.index('\\end{abstract}',start)
abstract='''We study the minimum implementation cost of revising an installed policy while protecting operating performance at every state and date. One randomized Markov continuation serves all restarts. Backward feasibility repair yields complete finite-state search; a finite-horizon allowance ladder extends repair to undiscounted problems. Exact aggregation identities reduce an exogenous class of atomic continuous-state models to a linear program without restricting the competing measurable policies. Twelve designed service economies, including 64 states and 64 periods, have independently verified optimality intervals below $9\\times10^{-8}$. An executed density model separates primitive, solver, and repair errors in the continuous transfer bound. In the original action-dependent maintenance cohort, 27 lotteries beat deterministic lower bounds, but all 30 positive-cost randomized intervals remain open; their models lie outside the transfer assumptions. These results distinguish tractable structural certification from generic completeness and retain the common-policy economic objective.'''
text=text[:start]+'\\begin{abstract}\n'+abstract+'\n'+text[end:]
text=text.replace('Strict discounting and a positive operating allowance provide the slack; no global duality assumption is used.','Strict discounting provides a constant slack, while a finite-horizon allowance ladder also permits undiscounted decisions. At zero tolerance an exact restriction to operating-maximizing actions replaces the repair. No global duality assumption is used.')
marker='A second result transfers finite-state certificates to a continuous state space.'
addition='''A structural result makes a different part of the general problem computationally tractable. When state transitions are exogenous, pointwise aggregation and a compatible family of within-cell measures together preserve the optimum over unrestricted measurable common policies. These identities can hold for nonlinear atomic transitions even when total-variation reset approximation fails. The resulting all-restart regret program is linear. Twelve designed service economies, spanning three transition structures, up to 64 regimes and 64 periods, and three or five actions, produce independently verified intervals below $9\\times10^{-8}$. An unreduced Bellman LP is an equally entitled classical comparator; we do not conceal its advantage on some small cases.\n\n'''
text=text.replace(marker,addition+marker)
text=text.replace('The general convergence results, rather than a claimed calibration, carry the methodological argument.','The convergence and exact-reduction results, rather than a claimed calibration, carry the methodological argument. The density experiment now executes the reset error chain; the original endogenous-transition models remain separate evidence rather than being relabeled as instances of the exogenous theorem.')
p.write_text(text)
p=PAPER/'main.tex';t=p.read_text().replace('\\input{revisions/2026-09-25-r42/paper/main_part3}', '\\input{revisions/2026-09-25-r42/paper/slack_ladder}\n\\input{revisions/2026-09-25-r42/paper/atomic_structure}\n\\input{revisions/2026-09-25-r42/paper/main_part3}')
p.write_text(t)
p=PAPER/'main_part3.tex';t=p.read_text().replace('The complete search and the transfer theorem provide the convergence argument.','The complete search, exact structural reduction, and reset transfer provide different routes to a global certificate, each under its stated assumptions.')
p.write_text(t)
p=PAPER/'main_part4.tex';t=p.read_text()
t=t.replace('\\subsection{Prospectively fixed common-Markov problems}', '\\input{revisions/2026-09-25-r42/paper/structured_evidence}\n\n\\subsection{Prospectively fixed common-Markov problems}',1)
t=t.replace('The $(32,256)$ result retains directed construction and structural checks, not the independent label of adjacent rows.','R41 subsequently independently rebuilt the complete $(32,256)$ object; this revision incorporates that successful arithmetic audit with its source and proof hashes.')
t=t.replace('and the R40 audit extends this to the complete $T=32,N=128$ object.','the R40 audit extends this to the complete $T=32,N=128$ object, and the R41 audit extends it to the finest $T=32,N=256$ object. The latter independently checks 92,274,688 support-action inequalities over 2,097,152 state--date cells; the original interval is unchanged.')
t=t.replace('The supplement attaches the prior article and technical supplement verbatim, with a content map.', 'The separate historical volume preserves the prior article and technical supplement verbatim; the current supplement supplies a direct map of the new results.')
t=t.replace('It checks two complete representative objects, not merely selected rows.','Its recorded coverage now includes the complete finest $(32,256)$ object, not merely selected rows. The R42 structural checker separately reconstructs every new finite primal and dual certificate without importing its constructor.')
extra=r'''
\begin{table}[t]
\caption{Open randomized intervals and guaranteed savings are different statistics}\label{tab:gapsavings}
\centering\small
\begin{tabular}{rrrrrrr}
\toprule $T$&Positive&Median (\%)&Max. (\%)&Strict gains&Min. gain&Max. gain\\\midrule
\tablerows{revisions/2026-09-25-r42/paper/generated/primary_gap_savings.tex}
\bottomrule
\end{tabular}
\par\smallskip\footnotesize Width is $(U_R-L_R)/U_R$ among positive-cost intervals. Savings are $L_D-U_R$, not a difference between lower bounds. The last two columns condition on strictly positive savings. All 42 signed savings are in the supplement. These are exact re-tabulations of retained certificates, not new optimization runs.
\end{table}
'''
t=t.replace('\\subsection{Nonlinear two-state bounds}',extra+'\n\\subsection{Nonlinear two-state bounds}')
a=t.index('\\section{Conclusion}');b=t.index('\\input{revisions/2026-09-25-r42/paper/references}',a)
t=t[:a]+r'''\section{Conclusion}\label{sec:conclusion}
A local operating requirement becomes a global revision certificate only when continuation compatibility and the cost of restoring feasibility are controlled together. Backward repair supplies that connection. A date-dependent allowance ladder covers finite undiscounted problems, while exact operating-action restrictions handle zero tolerance. These extensions retain the same common randomized Markov objective rather than replacing it by a necessary-action relaxation.

The exact aggregation result identifies a tractable continuum class without smoothing atomic shocks or restricting competing policies to a cellwise sieve. For exogenous dynamics satisfying two explicit aggregation identities, the common-policy problem is an ordinary linear program. Its twelve executed service economies have tightly closed positive-cost intervals, including longer horizons and more states and actions than the original prospective suite. The density exercise independently exposes the constants of the reset-transfer route, including a failed sufficient tightening condition.

These achievements do not make the original endogenous-transition maintenance gaps disappear. Its 27 deterministic separations remain valid, all 30 positive-cost randomized intervals remain open, and the nonlinear fine interval remains wide even after complete independent arithmetic verification. Generic completeness, exact structural solvability, and a designed policy-class comparison are different economic and computational results. Keeping those distinctions explicit permits the stronger theory and the new closed certificates to extend the method without altering the target or suppressing difficult evidence.

'''+t[b:]
p.write_text(t)
p=GEN/'nonlinear_selected.tex';p.write_text(p.read_text().replace('32 & 256 & 8.8718 & 11.8492 & 25.13 & not independent','32 & 256 & 8.8718 & 11.8492 & 25.13 & full R41'))
p=PAPER/'references.tex';t=p.read_text();marker='\\bibitem[Hettich and Kortanek'
item='''\\bibitem[Dufour and Prieto-Rumeau(2013)]{DufourPrietoRumeau2013}
Dufour, F., and T. Prieto-Rumeau (2013): ``Finite Linear Programming Approximations of Constrained Discounted Markov Decision Processes,'' \\emph{SIAM Journal on Control and Optimization}, 51(2), 1298--1324. doi:10.1137/120867925.

'''
t=t.replace(marker,item+marker);p.write_text(t)
# Root wrappers are additive. Do not modify any prior version's wrappers.
for root,name in [('ECTA_R42.tex','main'),('SUPP_R42.tex','supplement'),('RESPONSE_R42.tex','response'),('COMPUTATION_R42.tex','computation')]:
    (ROOT/root).write_text('\\input{revisions/2026-09-25-r42/paper/'+name+'}\n')
shutil.copyfile(OLD/'history/REVISION_INDEX_before_R40.md',BASE/'history/earlier_index_snapshot.md')
if not (BASE/'history/REVISION_INDEX_before_R42.md').exists() and (ROOT/'REVISION_INDEX.md').exists():
    shutil.copyfile(ROOT/'REVISION_INDEX.md',BASE/'history/REVISION_INDEX_before_R42.md')
print(json.dumps(dict(abstract_words=len(abstract.split()),cases=len(suite['outcomes']),max_gap=max(float(F(r['gap'])) for r in suite['outcomes'] if r['status']=='certified'),primary=statistics_out),indent=2))
