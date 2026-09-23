"""Materialize the R29 referee object from frozen evidence; never synthesize results."""
from __future__ import annotations
import collections, hashlib, importlib.util, json, math, re, statistics, subprocess
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
REV=ROOT/'revisions/2026-09-24-r29';OLD=ROOT/'revisions/2026-09-24-r28'
G=REV/'paper/generated';G.mkdir(parents=True,exist_ok=True)
BASE='cd1191f278948942f42c6507b4566108f2aa2f6d'

def load(p):return json.loads(Path(p).read_text())
def write(p,s):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def tex(s):
    return str(s).replace('\\',r'\textbackslash{}').replace('&',r'\&').replace('_',r'\_').replace('%',r'\%').replace('#',r'\#').replace('^',r'\textasciicircum{}').replace('~',r'\textasciitilde{}')
def evidence_tex(s):
    return ' '.join((r'\nolinkurl{'+w+'}') if ('/' in w or '_' in w or '.json' in w or '.py' in w or '.txt' in w) else tex(w) for w in str(s).split())
def table(name,caption,headers,filename,cols=None,long=False):
    cols=cols or ('l'+'r'*(len(headers)-1))
    if long:
        return '\n\\begingroup\\footnotesize\\setlength{\\tabcolsep}{4pt}\n\\begin{longtable}{'+cols+'}\n\\caption{'+caption+'}\\label{tab:'+name+'}\\\\\n\\toprule\n'+' & '.join(headers)+r' \\'+'\n\\midrule\\endfirsthead\n\\toprule\n'+' & '.join(headers)+r' \\'+'\n\\midrule\\endhead\n\\bottomrule\\endfoot\n\\tablerows{revisions/2026-09-24-r29/paper/generated/'+filename+'.tex}\n\\end{longtable}\n\\endgroup\n'
    return '\n\\begin{table}[htbp]\\centering\\small\n\\caption{'+caption+'}\\label{tab:'+name+'}\n\\begin{tabular}{'+cols+'}\\toprule\n'+' & '.join(headers)+r' \\'+'\n\\midrule\n\\tablerows{revisions/2026-09-24-r29/paper/generated/'+filename+'.tex}\n\\bottomrule\\end{tabular}\n\\end{table}\n'
def front(title,short,abstract=None):
    s=r'\input{revisions/2026-09-24-r29/paper/preamble}'+'\n'+r'\input{revisions/2026-09-24-r29/paper/generated/macros}'+'\n'+r'\begin{document}\begin{frontmatter}'+'\n'+r'\title{'+title+'}\n'+r'\runtitle{'+short+'}\n'+r'\begin{aug}\author[id=au1,addressref={add1}]{\fnms{Qian}~\snm{QI}\ead[label=e1]{qiqian@pku.edu.cn}}\address[id=add1]{\orgname{Peking University}}\end{aug}'+'\n'
    if abstract:s+=r'\begin{abstract}'+abstract+r'\end{abstract}'+'\n'+r'\begin{keyword}\kwd{Bellman operators}\kwd{Stochastic control}\kwd{Certified computation}\kwd{Preference adjustment}\kwd{Neural approximation}\end{keyword}'+'\n'
    return s+r'\end{frontmatter}'+'\n'

THEORY=r'''
\section{State-dependent residual budgets}\label{sec:budget29}
The uniform local tolerance in Theorem~\ref{thm:completion28} reserves the same amount for every possible future stage. Once a continuation has been completed, however, its actual residual envelope is known. We can allocate only the amount needed by that continuation, and test the raw action against the remaining budget. This distinction concerns preservation of candidate decisions, not a change in the information available to the algorithm.

Let $e_t:S_t\to[0,\infty)$ be a prescribed family of error budgets, with $e_T=0$ and zero budget at settled states. Assume that, at every nonsettled state,
\begin{equation}\label{eq:superbudget29}
 e_t(s)\ge\beta\max_{a\in A_t(s)}\sum_{s'}P_t(s'\mid s,a)e_{t+1}(s').
\end{equation}
A common tolerance $e_t(s)=\varepsilon$ before settlement satisfies this condition when $\beta\le1$. During the backward construction, let $v_{t+1}$ and $B_{t+1}$ be the exact value and residual envelope of the already completed suffix. Set
\begin{align}
 q_t(s,a)&=r_t(s,a)+\beta P_{t,s,a}v_{t+1},\\
 c_t(s)&=\beta\max_{a\in A_t(s)}P_{t,s,a}B_{t+1},\qquad
 a_t^{\rm rem}(s)=e_t(s)-c_t(s).\label{eq:allowance29}
\end{align}
Retain the raw action $a^0=\pi^0_t(s)$ exactly when
\begin{equation}\label{eq:retain29}
 \max_a q_t(s,a)-q_t(s,a^0)\le a_t^{\rm rem}(s).
\end{equation}
Otherwise choose a maximizing feasible action, using a fixed tie rule. For the selected action $a$, set $v_t(s)=q_t(s,a)$ and
\begin{equation}\label{eq:budgetrec29}
 B_t(s)=\max_b q_t(s,b)-q_t(s,a)+c_t(s).
\end{equation}
At a settled state, apply its settlement payoff and set $B_t=0$; the terminal value is the stated terminal payoff and $B_T=0$.

\begin{theorem}[Budgeted completion and policy preservation]\label{thm:budget29}
Under the finite-state assumptions of Theorem~\ref{thm:completion28} and \eqref{eq:superbudget29}, the backward construction is well defined. At every state and restart,
\begin{equation}\label{eq:budgetguarantee29}
 v_t^{\pi^0}(s)\le v_t^{\bar\pi}(s)\le V_t^*(s),\qquad
 0\le V_t^*(s)-v_t^{\bar\pi}(s)\le B_t(s)\le e_t(s).
\end{equation}
The local remaining allowance is nonnegative. Conditional on the already completed suffix and on using envelope \eqref{eq:budgetrec29}, the rule retains the raw action whenever that envelope can certify it within $e_t(s)$. No optimal value or optimal action reference is needed. Its arithmetic enumeration order is $O(TNAD)$; exact bit complexity and storage are charged separately.
\end{theorem}
\begin{proof}
The assertion holds at the terminal time and at settlement. Suppose it holds at $t+1$. Since $0\le B_{t+1}\le e_{t+1}$ and transition probabilities are nonnegative, \eqref{eq:superbudget29} gives $0\le c_t(s)\le e_t(s)$. Thus the allowance in \eqref{eq:allowance29} is nonnegative. If the raw action passes \eqref{eq:retain29}, adding $c_t$ proves $B_t\le e_t$. If it fails, a maximizing feasible action exists by finiteness; its local deficit is zero, so $B_t=c_t\le e_t$.

For the accuracy statement, write $d_{t+1}=V_{t+1}^*-v_{t+1}^{\bar\pi}$. By the induction hypothesis $0\le d_{t+1}\le B_{t+1}$. The Bellman equation and the elementary inequality $\max_a(x_a+y_a)\le\max_a x_a+\max_a y_a$ yield
\[
 V_t^*-v_t^{\bar\pi}
 =\max_a\{q_t(s,a)+\beta P_{t,s,a}d_{t+1}\}-q_t(s,\bar\pi_t(s))
 \le B_t(s).
\]
The loss is nonnegative by optimality of $V^*$. For preservation, assume $v_{t+1}^{\bar\pi}\ge v_{t+1}^{\pi^0}$. The selected action has $q_t(s,\bar\pi_t(s))\ge q_t(s,\pi_t^0(s))$, because it is either the raw action or a maximizer. Positivity of the transition law then gives
\[
 v_t^{\bar\pi}(s)\ge r_t(s,\pi_t^0(s))+\beta P_{t,s,\pi_t^0(s)}v_{t+1}^{\pi^0}=v_t^{\pi^0}(s).
\]
This closes the induction. Finally, once $v_{t+1}$ and $B_{t+1}$ are fixed, $c_t$ does not depend on the selected current action. The raw action satisfies $B_t\le e_t$ if and only if \eqref{eq:retain29} holds. Computing the action values and propagating the envelope each enumerates at most $TNAD$ successor contributions. None of these steps calls an optimal-reference solver.
\end{proof}

The preservation inequality also holds for the uniform-threshold operator, by the same induction. It is a pointwise economic comparison on the finite model, stronger than observing that a printed regret bound decreased. It does not carry over automatically to a continuous-state economy or to a floating-point neural implementation.

The theorem is locally permissive, not globally minimum-edit. Changing a later action changes both its value and its envelope, which can change earlier decisions. Consequently we make no claim that the budget rule changes fewer actions on every input, nor that either rule yields the cheapest certified policy. The two rules are compared on exactly the same raw tables. A fixed common tolerance has the advantage of certifying every restart, rather than just one initial distribution. More general budgets satisfying \eqref{eq:superbudget29} can incorporate state-specific accuracy priorities.

This construction uses the full model, feasible-action enumeration, and exact suffix evaluation. These are the same information resources available to exact backward induction. Classical dynamic programming supplies the Bellman comparison argument; the methodological addition here is the explicit candidate-preservation rule, its state-dependent certificate budget, and the joint proof of local permissiveness, whole-state accuracy, and payoff monotonicity. It is not an invention of policy iteration or an unconditional neural acceleration theorem.
'''

LITERATURE=r'''
\subsection{Relation to established numerical methods}\label{sec:literature29}
The oracle and conclusion must be matched before comparing methods. Fitted value iteration propagates approximation and sampling errors through a value recursion; \citet{MunosSzepesvari2008} give finite-sample bounds under their approximation and distributional assumptions. Our finite graph instead permits exact model evaluation after a policy is frozen. Its deterministic, all-state certificate is obtained by enumeration; it cannot be advertised as a better statistical rate or as a solution of the dimensionality problem addressed by approximation methods.

Constrained direct search predates the present work. \citet{KoldaLewisTorczon2003} organize direct-search methods and their convergence mechanisms; \citet{KoldaLewisTorczon2006} relate a stationarity measure to the step-length control in generating-set search under linear constraints. The contribution of Theorem~\ref{thm:box28} is the explicit interval-width requirement, the short-face alternative for a box, the work factor $W(\kappa h^2)$, and the unresolved-oracle outcome. The theorem is an instantiated certificate argument, not a claim to have originated constrained derivative-free optimization.

The verified-numerics literature, represented by \citet{Rump2010}, supplies the reason for using directed enclosures rather than tolerances on floating-point residuals. The stopped slice contributes a concrete analytic oracle: change of path measure controls the stopping discrepancy, while polynomial moments, Gaussian tails, and directed rounding enclose the objective and its first two derivatives. Neither neural stochastic-control approximation \citep{HureEtAl2021} nor a small training residual alone supplies those particular deterministic enclosures. Conversely, the slice has one constant preference-control parameter and does not establish a general high-dimensional oracle.

The comparative economic benchmark remains the unchanged consumption--portfolio model. Dual bounds and information relaxation \citep{BrownSmithSun2010,BrownSmith2014}, classical constrained quasi-Newton optimization \citep{ByrdEtAl1995}, and projection and sparse-grid methods \citep{Judd1998,BrummScheidegger2017} are substantive comparators, not incidental implementation choices. The numerical contribution is identified by theorem, oracle, coupling rule, and executed application separately. A general claim of neural superiority would require a favorable accuracy--total-work comparison; the present revision reports that comparison rather than assuming its outcome.
'''

def materialize():
    code=(OLD/'replication/render_tables.py').read_text()
    code=code.replace("REV=ROOT/'revisions/2026-09-24-r28';R=REV/'results';G=REV/'paper/generated'", "REV=ROOT/'revisions/2026-09-24-r29';R=ROOT/'revisions/2026-09-24-r28/results';G=REV/'paper/generated'")
    code=code.replace("(R/'R28_HEADLINE_RESULTS.json')","(REV/'results/R28_HEADLINE_RESULTS.json')")
    rp=REV/'replication/render_inherited.py';write(rp,code)
    spec=importlib.util.spec_from_file_location('render29inherited',rp);renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer);renderer.main()
    num=renderer.number;up=lambda x:num(math.nextafter(float(x),math.inf) if float(x)>0 else x,bound='upper');med=statistics.median
    rows=load(REV/'results/controls/summary.json');assert len(rows)==115
    nvariants=sum(len(r['variants']) for r in rows);assert nvariants==286
    mainvar=lambda r,rule:next(v for v in r['variants'] if v['rule']==rule and F(v['epsilon'])==F(1,100))
    def label(r):
        s=r['spec'];k=s['kind']
        return 'N%d/%d/%d'%(s['width'],s['depth'],s['seed']-27000) if k=='neural' else 'P%d'%s['degree'] if k=='polynomial' else 'R%d'%(s['seed']-29000) if k=='random' else {'myopic':'Myopic','base_stock':'Base stock','tabular2':'Two-period'}[k]
    def emit(name,data):write(G/(name+'.tex'),''.join(' & '.join(map(str,z))+r' \\'+'\n' for z in data))
    groups=[];scale=[];full=[];cost=[];deficits=[];sens=[];top=[];memory=[];attribution=[]
    models=[(2,4),(3,4),(4,4),(4,5),(5,4),(6,4),(7,4)]
    for d,L in models:
        a=[r for r in rows if (r['d'],r['L'])==(d,L)]
        groups.append([f'{d}/{L}',a[0]['states'],len(a),sum(F(r['raw_bound_rational'])<=F(1,100) for r in a),sum(F(r['raw']['worst_regret_rational'])<=F(1,100) for r in a),sum(F(mainvar(r,'fixed')['bound_rational'])<=F(1,100) for r in a),sum(F(mainvar(r,'budget')['bound_rational'])<=F(1,100) for r in a)])
        nn=[r['generation']['wall_seconds'] for r in a if r['spec']['kind']=='neural' and not r['inherited']]
        scale.append([f'{d}/{L}',a[0]['states'],num(a[0]['independent_reference']['wall_seconds']),num(med(nn)) if nn else '--',num(med(mainvar(r,'fixed')['completion']['wall_seconds'] for r in a)),num(med(mainvar(r,'budget')['completion']['wall_seconds'] for r in a)),num(med(mainvar(r,'budget')['certification']['wall_seconds'] for r in a))])
        memory.append([f'{d}/{L}',a[0]['model_array_bytes'],a[0]['policy_bytes'],a[0]['logical_feasible_state_action_successor_terms_per_sweep'],a[0]['dense_successor_slots_per_sweep'],max(v['maximum_integer_bit_length'] for r in a for v in r['variants']),max(v['completion']['process_high_water_kib'] for r in a for v in r['variants'])])
        for kind in ['neural','polynomial','random','myopic','base_stock','tabular2']:
            b=[r for r in a if r['spec']['kind']==kind]
            if not b:continue
            attribution.append([f'{d}/{L}',tex(kind),len(b),up(max(r['raw']['worst_regret'] for r in b)),num(100*med(mainvar(r,'fixed')['changed_fraction_nonstopped'] for r in b)),num(100*med(mainvar(r,'budget')['changed_fraction_nonstopped'] for r in b)),num(med(mainvar(r,'budget')['completion']['wall_seconds'] for r in b))])
        for t in range(8):
            vs=[mainvar(r,'budget') for r in a]
            changes=sum(z[-1] for v in vs for z in v['topology'] if z[0]==t)
            near=sum(z[-1] for v in vs for z in v['topology'] if z[0]==t and z[2]==0)
            top.append([f'{d}/{L}',t,changes,near,up(max(r['raw']['worst_regret_by_restart'][t] for r in a)),up(max(v['evaluation']['worst_regret_by_restart'][t] for v in vs))])
    for r in rows:
        f,b=mainvar(r,'fixed'),mainvar(r,'budget');ident=[f"{r['d']}/{r['L']}",label(r)]
        full.append(ident+[up(r['raw']['worst_regret']),up(r['raw_bound_upper']),up(f['bound_upper']),up(b['bound_upper']),f['changed_actions'],b['changed_actions']])
        cost.append(ident+[num(r['generation']['wall_seconds'])+('*' if r['inherited'] else ''),num(r['raw_certification']['wall_seconds']),num(b['completion']['wall_seconds']),num(b['certification']['wall_seconds']),num(b['standalone_measured_components_seconds']),num(b['standalone_measured_components_cpu_seconds'])])
        q=b['suffix_deficit_quantiles'];deficits.append(ident+[up(q['median']),up(q['q90']),up(q['q99']),up(q['max']),b['maximum_integer_bit_length']])
        if len(r['variants'])>2:
            for eps in [F(1,1000),F(1,100),F(1,20)]:
                x=next(v for v in r['variants'] if v['rule']=='fixed' and F(v['epsilon'])==eps);y=next(v for v in r['variants'] if v['rule']=='budget' and F(v['epsilon'])==eps)
                sens.append(ident+[str(eps),x['changed_actions'],y['changed_actions'],up(x['bound_upper']),up(y['bound_upper'])])
    for name,data in [('r29_groups',groups),('r29_scale',scale),('r29_full',full),('r29_cost',cost),('r29_deficits',deficits),('r29_sensitivity',sens),('r29_topology',top),('r29_memory',memory),('r29_attribution',attribution)]:emit(name,data)
    summary={'candidate_count':len(rows),'variant_count':nvariants,'models':models,'maximum_states':max(r['states'] for r in rows),'all_variants_certified':all(F(v['bound_rational'])<=F(v['epsilon']) for r in rows for v in r['variants']),
      'raw_regret_passes':sum(F(r['raw']['worst_regret_rational'])<=F(1,100) for r in rows),'raw_residual_passes':sum(F(r['raw_bound_rational'])<=F(1,100) for r in rows),'worst_raw_regret':max(r['raw']['worst_regret'] for r in rows),'budget_fewer_changes_cases':sum(mainvar(r,'budget')['changed_actions']<mainvar(r,'fixed')['changed_actions'] for r in rows),'budget_more_changes_cases':sum(mainvar(r,'budget')['changed_actions']>mainvar(r,'fixed')['changed_actions'] for r in rows),'same_changes_cases':sum(mainvar(r,'budget')['changed_actions']==mainvar(r,'fixed')['changed_actions'] for r in rows),'original_full_domain_bound':7.181834580823298,'original_target':.01,'original_full_domain_target_closed':False}
    write(REV/'results/R29_HEADLINE_RESULTS.json',json.dumps(summary,indent=2)+'\n')
    macro=(G/'macros.tex').read_text()+''.join('\\newcommand{\\'+k+'}{'+str(v)+'}\n' for k,v in {'NewCases':115,'NewVariants':286,'MaxStates':16384,'BudgetFewer':summary['budget_fewer_changes_cases'],'BudgetMore':summary['budget_more_changes_cases'],'BudgetSame':summary['same_changes_cases'],'RawRegretPass':summary['raw_regret_passes'],'RawBoundPass':summary['raw_residual_passes']}.items());write(G/'macros.tex',macro)
    pre=(ROOT/'revisions/2026-09-23-r26/paper/preamble.tex').read_text().replace('Revision R26 --- working manuscript','Revision R29 --- September 24, 2026')
    write(REV/'paper/preamble.tex',pre)
    for p in (OLD/'paper').glob('*.tex'):
        write(REV/'paper'/p.name,p.read_text().replace('revisions/2026-09-24-r28/paper/generated','revisions/2026-09-24-r29/paper/generated').replace('Max parameter difference & Max output difference & Max retained remainder','Parameter difference & Output difference & Retained remainder'))
    refs=(REV/'paper/references.tex').read_text()
    extra=r'''
\bibitem[Kolda, Lewis, and Torczon(2003)]{KoldaLewisTorczon2003}
Kolda, T. G., R. M. Lewis, and V. Torczon (2003): ``Optimization by Direct Search: New Perspectives on Some Classical and Modern Methods,'' \emph{SIAM Review}, 45(3), 385--482.

\bibitem[Kolda, Lewis, and Torczon(2006)]{KoldaLewisTorczon2006}
Kolda, T. G., R. M. Lewis, and V. Torczon (2006): ``Stationarity Results for Generating Set Search for Linearly Constrained Optimization,'' \emph{SIAM Journal on Optimization}, 17(4), 943--968.

'''
    write(REV/'paper/references.tex',refs.replace(r'\end{thebibliography}',extra+r'\end{thebibliography}'))
    write(REV/'paper/budgets.tex',THEORY)
    write(REV/'paper/positioning.tex',LITERATURE)
    evidence=r'''
\section{Candidate attribution, robustness, and state-space scaling}\label{sec:controls29}
The new cohort holds the 34 R28 raw policies fixed and adds 81 candidates under a committed protocol. On each original model we add ten random feasible tables, a one-period greedy policy, a base-stock rule, and two-period truncated dynamic programming. The width-32, depth-two seed panel is expanded to ten seeds at $(d,L)=(4,4)$ and five at $(4,5)$. At dimensions five, six, and seven we run six fixed proposal rules each. No failed candidate is replaced. The seven models contain between 16 and 16,384 states per time slice; the largest is 64 times the original 256-state four-dimensional graph. This is a finite-graph scaling study, not a claim to solve a high-dimensional continuous problem.

Every new raw action table and training record is hashed before its own completion. All reference-free variants are frozen before the independent full-horizon optimal reference is constructed for that model. A runtime audit rejects optimal-reference file reads, and the candidate/completion context disables the independent optimal solver. The exact reference is generated by a separate scalar implementation. The program checks every state and restart against it, not only a start-state average. The process had access to prior R27/R28 outcomes, so these additions and the residual-budget rule are exploratory, despite their fixed cohort and enforced program dependencies. The missing original R27 raw-run artifacts have not been reconstructed; R28 and R29 are separately identified executions.

Table~\ref{tab:r29coverage} distinguishes true raw regret, a reference-free raw residual bound, and the guarantees after repair. There are \NewCases\ raw policies and \NewVariants\ completed variants, including the 14-policy tolerance panel at $.001$, $.01$, and $.05$. All completed variants satisfy their exact rational tolerance. A failed raw residual test is not, by itself, proof that raw regret exceeds the tolerance; the independent reference determines the latter count. The budget rule makes fewer changes than the fixed rule in \BudgetFewer\ main-cohort cases, more in \BudgetMore, and the same number in \BudgetSame. These are paired deterministic comparisons, not independent statistical replications.
'''
    evidence+=table('r29coverage','Exact all-state/all-restart coverage at tolerance $.01$',['$d/L$','$N$','Cases','Raw bound','Raw regret','Fixed','Budget'],'r29_groups')
    evidence+=r'''
The control experiment makes attribution observable. Random, myopic, base-stock, and two-period policies receive exactly the same two completion operators as neural and polynomial proposals. Detailed corrections by time, inventory total, minimum inventory, and number of empty coordinates are retained, together with suffix-conditioned deficit quantiles. Thus a small correction fraction can be distinguished from corrections concentrated near default or at early restart times. Raw-to-completed payoff monotonicity follows from Theorem~\ref{thm:budget29}, not from a reduction in a certificate alone.

Completion cost need not be proportional to the number of corrected actions: even a policy requiring no changes incurs the model-wide action scan. A small neural correction fraction therefore does not establish a computational advantage. Table~\ref{tab:r29scaling} retains exact dynamic programming visibly and charges both repair and verification. All times within that table are measured on the same R29 execution environment. A dash means that no new neural fitting run was specified for that model; inherited R28 fitting times are not combined with R29 hardware timings. Full candidate-specific ledgers are in the computational appendix.
'''
    n7=next(r for r in rows if r['d']==7 and r['tag']=='neural_w32_h2_s27303')
    m7=next(r for r in rows if r['d']==7 and r['tag']=='myopic')
    evidence+=('In the largest graph, the specified neural proposal requires '+str(mainvar(n7,'budget')['changed_actions'])+' replacements out of '+str(8*(n7['states']-1))+' nonsettled state--time decisions under the budget rule, compared with '+str(mainvar(m7,'budget')['changed_actions'])+' for the myopic control. Its raw worst regret is '+up(n7['raw']['worst_regret'])+', compared with '+up(m7['raw']['worst_regret'])+' for that control. This is a substantial candidate-preservation difference in the executed model. It is not a total-work advantage: the neural fitting stage costs '+num(n7['generation']['wall_seconds'])+' seconds, whereas the independent full optimal solve costs '+num(n7['independent_reference']['wall_seconds'])+' seconds in the same execution.\n\n')
    evidence+=table('r29scaling','Same-execution stage costs (seconds; medians over the specified policies)',['$d/L$','$N$','Exact DP','New neural','Fixed repair','Budget repair','Verify'],'r29_scale')
    evidence+=r'''
The logical work count is $T\sum_s|A(s)|D$ successor contributions for one feasible-action sweep. The vector implementation also records the larger dense count $TNAD$, model-array bytes, compiled-policy bytes, integer bit lengths, CPU time, wall time, and process high-water resident memory. High-water memory includes libraries, previous cases, and live models; it is not an isolated per-candidate peak. The standalone component sum charges the full model and independent reference to each policy without amortization. Interpreter startup and file serialization are included in the outer cohort measurement but not silently allocated into individual method timings. Reusing an inherited candidate does not make its historical training free; those rows are explicitly marked as replay-only rather than new standalone fitting measurements.

The original economy remains distinct. The two rigorously enclosed preference-adjustment slices, six independently implemented transport paths, and twelve paired production trajectories are reproduced from the frozen R28 evidence. They instantiate boundary-aware polling, the stopped likelihood-ratio bridge for the stated scalar class, and full-state rollback. They do not establish the financed 47-dimensional derivative bridge or change the original current-state, whole-domain bound $7.181834580823298$ against $.01$. Nor does the present cost ledger recover the unmeasured construction time of inherited central dual infrastructure. These are identified mathematical and measurement requirements, not replaced by auxiliary success.
'''
    write(REV/'paper/controls.tex',evidence)
    abstract=r'''We study Bellman solution procedures that separate neural proposals, economically meaningful improvement, and independent certification. A backward residual-budget operator preserves candidate actions whenever the completed continuation leaves sufficient accuracy allowance. We prove all-state, all-restart accuracy and pointwise payoff improvement without an optimal-value reference. Exact-rational experiments audit 115 frozen proposals and 286 completions, including trivial-policy controls and graphs with up to 16,384 states. For continuous control, precision-aware coordinate polling certifies projected stationarity at active box constraints. A likelihood-ratio oracle instantiates its assumptions in a stopped consumption--portfolio economy with costly preference adjustment. Independently implemented historical transport and paired rollback experiments identify the roles of parameter geometry and deployment checks. Classical comparators, raw failures, and verification costs remain explicit. The original whole-domain accuracy target is retained separately from the proved finite-state and restricted-class results.'''
    assert len(abstract.split())<=150
    article=front('Neural Bellman Operators','Neural Bellman Operators',abstract)
    for part in ['economy','operators','budgets','positioning','computation','controls']:article+=r'\input{revisions/2026-09-24-r29/paper/'+part+'}\n'
    article+=r'''
\section{Conclusion}
A Bellman method must identify its approximation object, control class, restart set, verification oracle, and total computational work. The residual-budget theorem constructs a uniformly accurate finite-state policy while preserving every candidate action that its suffix envelope can certify. The constrained-poll theorem and stopped slice give a separate continuous-control guarantee, including boundary stationarity and oracle-precision costs. The exact transport identity and paired deployment experiment identify mechanisms without attributing generic repair to neural fitting. These contributions retain the original economic problem and its $.01$ target. They do not turn a finite graph into a continuous-domain certificate, and they do not declare the original $7.181834580823298$ bound closed. The complete computational and historical appendices retain all unsuccessful candidates, detailed derivations, and prior evidence.
\begin{appendix}
\input{revisions/2026-09-24-r29/paper/proofs}
\end{appendix}
\clearpage\input{revisions/2026-09-24-r29/paper/references}
\end{document}
''';write(ROOT/'ECTA_R29.tex',article)
    supp=front('Supplement to Neural Bellman Operators: Revision R29','NBO: Supplement R29')
    supp+=r'''
\section{Review object and preservation}
The article, this supplement, the computational appendix, the point-by-point response, and the historical annex form one revision object. The base evidence commit is \texttt{cd1191f278948942f42c6507b4566108f2aa2f6d}; the latest addressed report is R27, dated September 24, 2026, at \texttt{d6f6f7fa2b0ef40e42206dc64406f004cc83c71e}. R26 and the independent R25 second pass are addressed individually in the response. No earlier source, result, or review branch is overwritten. The old root index is retained in the source audit. The original R27 raw-run files were absent from its reviewed tree; a later re-execution cannot supply an earlier freeze event.

\section{Exact arithmetic and independent checks}
The inventory implementation uses arbitrary-precision Python integers, NumPy object arrays, and exact Fraction comparisons. At $(d,L)$, rewards have denominator $100d$. Backward denominator recursion multiplies by $100D$ per stage, where $D=d+2$ is the number of equiprobable demand outcomes. Hence action deficits, envelope comparisons, and tolerance acceptance use integers after exact scaling. Printed decimals are explanatory only; bounds are rounded outward by the table renderer. The independently implemented scalar reference enumerates primitive transitions and rewards, rather than calling the vectorized action-value or completion routines.

For each model, candidate and completion files are sealed before reference creation. The recorded dependency audit prohibits reference files and the optimal solver during generation. This establishes the program's information path, not blinding of the investigator to earlier results. Each policy's feasibility, settlement convention, own-value recursion, residual envelope, and every reference gap are checked. Uniform and budgeted completion both improve the raw policy pointwise on this graph. Hash and event-order checks are supplemented by unit tests of infeasible actions, settlement, exact boundary comparisons, and forbidden reference reads.

\section{Controls and correction burden}
A myopic action maximizes the exact one-period reward. The base-stock policy orders toward $\lceil(L-1)/2\rceil$, choosing the lowest-index most deficient good and at most two units. The two-period comparator uses the exact terminal payoff at the endpoint of a truncated two-step horizon; it does not read the full-horizon reference. Random policies are sampled independently from feasible actions at each nonsettled state and time. All receive the same repair rules and budgets. The fixed cohort, including the pre-execution seed-index clarification, is preserved in the protocol files.
'''
    supp+=table('r29attribution','Proposal quality and median correction burden; percentages exclude settled states',['$d/L$','Proposal','Cases','Raw regret max',r'Fixed $\%$',r'Budget $\%$','Repair s'],'r29_attribution',long=True)
    supp+=r'\section{Tolerance sensitivity}'+'\n'+r'The same 14 policies are evaluated at all three tolerances; these repeated audits are not independent replications. Changes depend on the completed suffix, so the table is descriptive rather than a global minimum-edit theorem.'+'\n'
    supp+=table('r29tol','Identical raw candidates under fixed and state-dependent budgets',['$d/L$','Policy',r'$\varepsilon$','Fixed changes','Budget changes','Fixed bound','Budget bound'],'r29_sensitivity',long=True)
    supp+=r'\section{Memory, bit growth, and enumeration work}'+'\n'
    supp+=table('r29memory','Storage and arithmetic coverage; RSS is a process high-water mark in KiB',['$d/L$','Model B','Policy B','Feasible terms','Dense slots','Bits','RSS KiB'],'r29_memory',long=True)
    supp+=r'''
\section{Original-economy oracle and production evidence}
The article gives the complete likelihood-ratio proof, analytic remainder construction, projected-poll theorem, and transport identity. The following tables retain the executed precision levels and matched production comparison. Class regret is relative to the fixed scalar preference-adjustment class, not the original unrestricted policy problem. A successful pointwise interval gate is a payoff comparison, whereas a smaller original full-domain bound is only a certificate improvement. The original financed dual-construction time remains unmeasured; all recorded central timing totals state their conditional scope.
'''
    supp+=table('slicepolls','All executed scalar polling meshes and precision-dependent work',['$k$','$h$',r'$\theta$','Calls',r'$\|G_1\|$ bound','Seconds','Call bound'],'slice_poll_rows',long=True)
    supp+=table('sliceerrors','Analytic derivative remainder budgets (orders zero, one, and two)',['$k$','Order','Flow','Terminal','Stopping','Total'],'slice_error_rows',long=True)
    supp+=table('transportdist','Full-path displacement and moment diagnostics',['Seed','Order','Min step','Median','95th pct.','$m$ discrepancy','$v$ discrepancy'],'mechanism_distribution_rows',long=True)
    supp+=table('pairedprod','Paired final-payoff interval: gated minus ungated',['Seed','Method','Lower','Upper','Proved positive','Rejections'],'production_pair_rows',cols='rlrrlr',long=True)
    supp+=r'\section{Interpretation of exact-commit validation}'+'\n'+r'The read-only validation workflow checks the final source commit from a clean checkout, verifies frozen scientific hashes, rebuilds the PDFs, and records the exact SHA, run identifier, and artifact identity in its output. The record is external to the commit it identifies, avoiding a self-referential hash assertion. Compilation, tests, and workflow success do not prove uninstantiated hypotheses of the original continuous-control theorems.'+'\n'+r'\end{document}'+'\n';write(ROOT/'SUPP_R29.tex',supp)
    comp=front('Computational Appendix to Neural Bellman Operators: R29','NBO: Computational Appendix')
    comp+=r'\section{Complete fixed-cohort record}'+'\n'+r'Every candidate appears below. N denotes width/depth/seed minus 27000; P denotes polynomial degree; R denotes random seed minus 29000. Raw regret is computed only after the candidate has been frozen. Raw and completed bounds are reference-free exact residual certificates. The complete statewise values, action tables, restart losses, and correction topology are retained as machine-readable files.'+'\n'
    comp+=table('r29all','All 115 candidates at $.01$: raw performance, completion bounds, and action changes',['$d/L$','Policy','Raw regret','Raw bound','Fixed bound','Budget bound','Fixed edits','Budget edits'],'r29_full',long=True)
    comp+=r'\section{Stage-by-stage cost ledger}'+'\n'+r'An asterisk marks inherited-policy replay: its R28 fitting work is not repeated or included in the R29 generation entry. The component sum charges the full reference and model per policy and includes the raw audit and selected budget repair, not all sensitivity variants. It excludes startup and serialization, which remain in the cohort resource record. CPU and wall time are different measurements. Full model-construction, reference, policy compilation, comparison, and amortization fields remain in each JSON record.'+'\n'
    comp+=table('r29allcost','Seconds by candidate; totals are non-amortized measured component sums',['$d/L$','Policy','Generate','Raw audit','Repair','Verify','Wall sum','CPU sum'],'r29_cost',long=True)
    comp+=table('r29deficits','Deficits of raw actions against completed suffixes under the budget rule',['$d/L$','Policy','Median','90th pct.','99th pct.','Maximum','Bits'],'r29_deficits',long=True)
    comp+=table('r29topology','Corrections by time and inventory boundary; worst losses over all candidates in a model',['$d/L$','Time','Edits','Min inventory 0','Raw restart loss','Budget restart loss'],'r29_topology',long=True)
    comp+=r'\section{Inherited R28 detailed execution ledgers}'+'\n'+r'These are the original R28 hardware measurements, not cross-hardware speedup comparisons. Their underlying records remain byte-for-byte unchanged.'+'\n'
    for name,caption,headers,cols in [
      ('inventory_full_rows','All original R28 inventory candidates',['$d,L$','Policy','Raw bound','Raw loss','Complete bound','Complete loss','Edits'],None),
      ('inventory_work_rows','Original R28 work and correction ledger',['$d,L$','Policy','Build','Compile','Ref.-free','Standalone',r'$\%$ edits','99th loss'],None),
      ('inventory_restart_rows','Original R28 restart losses',['$d,L$','Time','Raw worst','Complete worst'],None),
      ('mechanism_cost_rows','Recentered transport timing',['Seed','Order','Setup','Neural','Transport','Diagnostics','Total'],None),
      ('production_cost_rows','Paired production timing',['Seed','Method','Setup','Generation','Checker','Bookkeeping','Total'],'rlrrrrr'),
      ('production_decision_rows','Every production checkpoint decision',['Seed','Method','Block','Lower','Upper','Margin','Width','Decision'],'rlrrrrrl')]:
        comp+=table(name,caption,headers,name,cols=cols,long=True)
    comp+=r'\end{document}'+'\n';write(ROOT/'COMPUTATION_R29.tex',comp)
    hist=r'''\documentclass[12pt]{article}
\usepackage[margin=1in]{geometry}\usepackage{pdfpages,hyperref}
\begin{document}\thispagestyle{empty}
\begin{center}{\Large Neural Bellman Operators}\\[12pt]{\large Historical Preservation Annex, R29}\\[8pt]September 24, 2026\end{center}
This annex reproduces the complete last materialized R26 article, supplement, and response without changing their pages. The R26 supplement itself retains the complete reviewed R24 article and supplement. The current article incorporates the later R28 scientific sources and adds R29 results; all intermediate source and evidence directories are retained in the repository. Historical claims are to be read with the current point-by-point response, not as a replacement for its updated conclusions.
\clearpage\includepdf[pages=-]{ECTA_R26.pdf}
\includepdf[pages=-]{SUPP_R26.pdf}
\includepdf[pages=-]{RESPONSE_R26.pdf}
\end{document}
''';write(ROOT/'HISTORY_R29.tex',hist)
    response=front('Response to the Referees: Neural Bellman Operators, R29','NBO: Response R29')
    response+=r'''\section{Overview}
We thank the referee for identifying both the absent R27 submission object and the scientific attribution problem. This revision supplies a materialized article, supplement, complete computational ledger, historical annex, code, frozen evidence, and executable validation. It retains the title, original economy, original $.01$ whole-domain target, and every earlier source and result. We respond through proofs, explicit oracles, independently evaluated controls, and complete disclosure of outcomes. We do not treat a response entry, successful compilation, or an auxiliary-model certificate as proof that the original all-state target has been achieved.

The R27 report is the latest report addressed. The R26 findings and the independent R25 second pass are cross-referenced individually below. The original R27 raw-run artifacts were not present at the reviewed commit; the later R28 execution is not represented as recovery of that missing record. The R29 extensions are exploratory relative to all prior outcomes, with fixed cohorts and programmatically enforced reference isolation.
'''
    disposition=load(REV/'disposition.json');last=None
    for item in disposition:
        group=item['id'].split('-F')[0].split('-T')[0].split('-N')[0]
        if group!=last:response+='\\section{'+tex(group)+'}\n';last=group
        response+='\\subsection{'+tex(item['id']+' --- '+item['issue'])+'}\n'+tex(item['response'])+'\n\n'+r'\emph{Evidence:} '+evidence_tex(item['evidence'])+'\n\n'+r'\emph{Disposition:} '+tex(item['status'])+'\n'
    response+=r'\end{document}'+'\n';write(ROOT/'RESPONSE_R29.tex',response)
    oldindex=ROOT/'REVISION_INDEX.md';save=REV/'source_audit/REVISION_INDEX_before_R29.md'
    if not save.exists():write(save,oldindex.read_text())
    write(oldindex,'# Current review object: R29\n\nRead ECTA_R29.pdf, SUPP_R29.pdf, RESPONSE_R29.pdf, COMPUTATION_R29.pdf and HISTORY_R29.pdf.\n\nLatest addressed report: reviews/2026-09-24-econometrica-r27/referee_report.md at d6f6f7fa2b0ef40e42206dc64406f004cc83c71e. Also addressed individually: R26 and the independent R25 second pass.\n\nScientific base: '+BASE+'. New source/evidence: revisions/2026-09-24-r29/. R29 has 115 frozen candidates, 286 completed variants, complete raw failures and classical controls. Original current-state/all-state/all-restart target remains 0.01, with inherited bound 7.181834580823298; finite-state and restricted-class certificates do not replace it.\n\nSee R29_REVIEW.md for reproduction and exact-commit validation. Earlier root index is preserved in revisions/2026-09-24-r29/source_audit/REVISION_INDEX_before_R29.md. All historical source/results remain unchanged.\n')
    write(ROOT/'R29_REVIEW.md','# R29 referee copy\n\nArticle: ECTA_R29.tex/pdf. Essential supplement: SUPP_R29.tex/pdf. Point-by-point response: RESPONSE_R29.tex/pdf. Complete numerical tables: COMPUTATION_R29.tex/pdf. Historical preservation: HISTORY_R29.tex/pdf.\n\nLatest report: R27 (2026-09-24). `revisions/2026-09-24-r29/disposition.json` covers every R27 finding/comment/request, R26 item, and R25 second-pass item.\n\n## Reproduction\n\nPython 3.13; numpy 2.3.5; scipy 1.17.0; torch 2.10.0 CPU; sympy 1.14.0; mpmath 1.3.0. Set OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1.\n\nRun `python revisions/2026-09-24-r29/replication/test_revision.py`; then `python revisions/2026-09-24-r29/replication/materialize.py`. Compile each of ECTA_R29, SUPP_R29, RESPONSE_R29, COMPUTATION_R29 and HISTORY_R29 with `latexmk -pdf -interaction=nonstopmode -halt-on-error`.\n\nTo re-execute science, use a fresh checkout with a separate output directory: the script refuses to overwrite an existing completed model. Set the module OUT variable to a new directory or move the existing results aside in an uncommitted working copy, then run controls.py. Never overwrite the archived evidence. Each environment records its own timings and source hashes.\n\nThe science workflow freezes results; the separate read-only validation workflow has no commit-message gate and checks the exact final referee commit. Run/artifact identity belongs to the external validation record, not a self-referential source hash.\n\nThe 0.01 original continuous-domain objective is not certified. Unknown-solution finite-state completion, scalar stopped-control stationarity, transport identities, and rollback are separate claims with separate evidence.\n')
    tracked=subprocess.check_output(['git','ls-files','-s'],cwd=ROOT,text=True).splitlines();pres=[]
    for z in tracked:
        left,path=z.split('\t',1);mode,blob,_=left.split()
        if path.startswith('revisions/2026-09-24-r29/') or path.startswith('.github/workflows/r29-') or re.match(r'^(ECTA|SUPP|RESPONSE|COMPUTATION|HISTORY)_R29\.',path) or path=='R29_REVIEW.md':continue
        if path=='REVISION_INDEX.md':continue
        pres.append({'path':path,'git_blob':blob})
    write(REV/'source_audit/PRESERVATION.json',json.dumps({'declared_scientific_base':BASE,'entries':pres},indent=2)+'\n')
    manifest={'base_evidence_commit':BASE,'latest_review_commit':'d6f6f7fa2b0ef40e42206dc64406f004cc83c71e','object':'R29','documents':['ECTA_R29','SUPP_R29','RESPONSE_R29','COMPUTATION_R29','HISTORY_R29'],'headline_results':summary,'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted((REV/'paper').glob('*.tex'))},'self_referential_commit_hash':False,'validation_record':'external GitHub Actions artifact at the checked SHA'}
    write(REV/'REVISION_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':materialize()
