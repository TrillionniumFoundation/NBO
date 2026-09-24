"""Build R30 article tables and review documents from frozen exact evidence."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext,ROUND_CEILING,ROUND_FLOOR
from statistics import median
from flint import arb,ctx
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1];G=R/'paper/generated';G.mkdir(parents=True,exist_ok=True)

def load(n):return json.loads((R/'results'/n).read_text())
def ff(v):return float(F(v))
def med(rows,key):return median(ff(x[key]) for x in rows)
def number(x):return f'{float(x):.4g}'
def outward(q,upper=True,digits=6):
 q=F(q)
 with localcontext() as c:
  c.prec=max(90,len(str(abs(q.numerator)))+len(str(q.denominator))+10)
  d=Decimal(q.numerator)/Decimal(q.denominator)
  return str(d.quantize(Decimal(1).scaleb(-digits),rounding=ROUND_CEILING if upper else ROUND_FLOOR))
def ball_interval(rec,digits=5):
 ctx.prec=200;b=arb(rec['ball']);lo=F(str(b.lower().fmpq()));hi=F(str(b.upper().fmpq()))
 return '['+outward(lo,False,digits)+', '+outward(hi,True,digits)+']'
def table(label,caption,cols,header,rows,note=''):
 body='\n'.join(' & '.join(map(str,r))+r' \\' for r in rows)
 return '\\begin{table}[htbp]\n\\centering\\footnotesize\n\\caption{'+caption+'}\\label{'+label+'}\n\\begin{tabular}{'+cols+'}\\toprule\n'+header+r' \\\midrule'+'\n'+body+'\n\\bottomrule\\end{tabular}\n'+('\\par\\smallskip\\begin{minipage}{.98\\textwidth}\\footnotesize '+note+'\\end{minipage}\n' if note else '')+'\\end{table}\n'
def write(n,s): (G/n).write_text(s)

responses=[
('R29-SP-F1','Regional work and strongest classical baseline','New conditional complexity theorem; no universal neural speed advantage',r'Sections 3--6 replace mandatory state enumeration by whole-region inequalities and a geometry-dependent work bound. The operating-mode example certifies the continuum, but its exact symbolic sign solver and online budget guard exploit the same structure. Their inclusion prevents a claim that neural fitting is necessary or generally fastest. The intervention-cost theorem supplies a separate economic objective. The inherited adverse total-cost ratios are retained.'),
('R29-SP-F2','Universal completion pass rate','Corrected interpretation',r'The abstract and numerical section no longer treat universal post-completion success as approximation efficacy. The raw-policy error bounds, fitting and proof costs, region counts, policy sizes, weighted intervention costs, and strong structural baselines are reported separately. Passing completed objects are implementation consistency checks.'),
('R29-SP-F3','Raw accuracy at scale','New raw evidence; inherited failures unchanged',r'The new frozen cohort reports raw continuous-domain regret for all 60 candidates, not only for selected seeds. Raw passes and failures are shown by model, width and optimizer. No new result reclassifies the inherited inventory failures. The operating-mode family is a separate one-dimensional structural example, not a rescue of the old high-dimensional accuracy claim.'),
('R29-SP-F4','Neural-specific value','Neural exclusivity not established',r'The title identifies neural proposals and certified Bellman operators as different objects. Polynomial proposals, the exact symbolic sign solver, the online minimum-intervention guard, Bernstein-based structural solving and vectorized DP receive the same model information. Neural fitting is fully charged. The paper does not claim a method-specific speed advantage contradicted by these controls.'),
('R29-SP-F5','Economic value and minimum intervention','New theorem and exact cost enclosure',r'Section 4 defines discounted, policy-induced occupancy cost and proves a minimum-cost Bellman recursion within explicit certified action sets. Section 5 bounds the implemented cover cost above and below relative to the local-loss class optimum. Priority weights and exact operating gains replace Hamming distance as the economic comparison. The exact online guard is acknowledged to attain that class optimum; global optimality over every true-regret-feasible policy is not claimed.'),
('R29-SP-F6','Reference-free terminology','Corrected terminology and accounting',r'The current text uses precomputed-optimum-free and independently implemented exact reference. It expressly charges the complete model, own-policy evaluation, witness construction, range bounds, compilation and checking. Absence of an optimal-value file is not presented as a reduction in model information or Bellman work.'),
('R29-SP-F7','Scalability and seed coverage','New regional-cardinality result, not high-dimensional robustness',r'The new cover applies to a continuum and hence to midpoint grids with cardinality up to 2^40 without materializing them. The example is explicitly one-dimensional. It uses five seeds, two widths and two optimizers for each of three gain functions. The inherited dimension-five through dimension-seven runs remain single-configuration pipeline demonstrations; no multidimensional neural robustness theorem is inferred.'),
('R29-SP-F8','Original full-domain target','Original target remains numerically unresolved',r'The original economy, current-state actor requirement, all-state/all-restart .01 target, and bound 7.181834580823298 remain explicit. The new active-boundary derivative computation is a substantive instantiation where stopping is material, but it does not reduce the inherited global bound or certify the unrestricted actor. The response does not mark this numerical requirement closed.'),
('R29-SP-F9','Economically material stopping','New validated active-boundary calculation',r'Section 7 moves the restart to preference 1.22 while retaining the original model primitives. The lower-boundary hitting probability at zero adjustment is rigorously enclosed near .6891565168. A killed kernel retains that boundary exactly, and validated Gaussian moments enclose payoff and two derivatives for all five predeclared controls. The failed first nested-integration attempt is retained; it is not promoted to a certificate.'),
('R29-SP-F10','Polling versus verified optimization','New derivative-bracketing comparator; 47-dimensional oracle uninstantiated',r'The inherited central-state polling schedule is compared with derivative bracketing using the identical validated oracle and concavity audit. Construction, audit, search calls and achieved projected-gradient bounds are separated. Bracketing requires fewer oracle calls in these scalar comparisons. The paper retains polling as a generic certificate wrapper and does not extrapolate it to an instantiated 47-dimensional solver.'),
('R29-SP-F11','Restricted economic comparative static','New boundary curvature result; restricted class stated',r'The active-boundary calculation yields strictly positive second-derivative intervals near zero adjustment and strictly negative ones at .1 and .2. Thus central-state concavity cannot be transferred to the boundary. Consumption and investment remain fixed in this calculation; it is not an unrestricted comparative static or a proof of interval-wide monotonicity from five points.'),
('R29-SP-F12','Rollback benefit','Preserved in audit material; no net-benefit claim',r'The complete R29 rollback evidence is reproduced in the historical annex. Its acceptance/restoration contract is retained, but the paired final outcomes are not presented as positive welfare or solver-performance evidence. This revision does not claim a new prospective avoided-loss experiment for the inherited production schedule.'),
('R29-SP-F13','Historical transport identity','Preserved as an implementation identity',r'The original full-recentering argument and numerical records remain in the historical annex. The main text identifies the same carrier, gradient, Jacobian and Adam history and highlights the roughly 1.39--1.50 omitted nonlinear displacement in the earlier control. Equivalence is not called an alternative optimizer or a computational saving.'),
('R29-SP-F14','Prospective evidence and dependence','Frozen new exploratory cohort; no independence claim',r'The protocol was committed before the new local scientific runs. All seeds, widths, optimizers and model functions were retained. The amendment records the failed nested integral and stronger post-diagnostic classical controls without changing the candidates. The study is explicitly report-informed and exploratory; neither 60 candidates nor repeated certificates are described as independent economic replications.'),
('R29-SP-F15','Nearest-neighbor novelty','Explicit theorem-level comparison',r'The introduction compares residual propagation, rollout/policy improvement, approximate policy iteration, baseline-bootstrapped safe improvement and verified numerics. Bellman comparison is identified as classical. The stated mathematical additions are the certified-class cost optimization, whole-region proof obligations and their geometry-dependent work accounting. The strong online guard is included rather than obscured by a novelty claim.'),
('R29-SP-F16','Coherent paper and preservation','Restructured main argument; no historical deletion',r'The main argument now follows regional certification, economically weighted revision, structural computation and active-boundary diagnosis. The complete prior article, supplement, response, computational appendix and historical annex are reproduced in HISTORY_R30. Original source and evidence directories are not overwritten. Transport and rollback no longer carry independent solver-superiority claims.'),
('R29-SP-F17','Title and certified object','Object-specific title',r'The title is Certified Bellman Operators with Neural Proposals: Adaptive Verification and Costly Policy Revision. It identifies both the approximation stage and the certified object without attributing a representation-independent guarantee or a repaired policy to a raw neural network.'),
('R29-SP-T1','Zero-tolerance limit','Proposition and exact tests',r'The zero-tolerance proposition states the finite exact zero-tolerance limit and proves optimality by backward induction. Retained optimal ties need not equal the replacement tie rule. Sixteen small exact policy cases are checked. No claim of zero-tolerance interval-subdivision termination at irrational roots is made.'),
('R29-SP-T2','Total certified-solution ratios','Main-table addition',r'The article displays both (repair+verification)/DP and (fit+repair+verification)/DP for every inherited row with the necessary recorded times. Missing fitting times are not imputed as zero. Ratios are derived from the displayed R29 inputs and not reported with spurious input precision.'),
('R29-SP-T3','Edit count versus scan cost','New algorithm and explicit distinction',r'The exhaustive algorithm still has full-scan cost regardless of edits. The new implementation certifies complete intervals, counts every range-oracle call and breakpoint, and separately charges compilation and checking. Its work depends on certificate geometry, not automatically on the number of edited actions.'),
('R29-SP-T4','Weighted edit metrics','Exact occupancy and payoff records',r'The new records include discounted occupancy edits, state-priority-weighted cost with weight 1+x, exact raw-to-completed operating-payoff gains, independent overlay checks, and break-even intervention shadow prices. The displayed continuous-density integrals are not mislabeled as finite-grid occupancy estimates.'),
('R29-SP-T5','Stronger rollout and improvement controls','Analytic structural comparison; no new inventory rollout panel',r'In the new exogenous-transition family every continuation cancels from the action comparison, at every lookahead depth and after any policy-evaluation step. Exact symbolic optimization and the online cost-minimizing guard are therefore stronger controls than a shallow rollout. These are implemented. A new deeper-rollout panel for the inherited inventory family is not claimed.'),
('R29-SP-T6','Optimized exact baseline','Vectorized DP and exact structural controls',r'The new experiment includes full-grid vectorized backward recursion, explicitly labeled binary64 diagnostic arithmetic, and a genuinely exact symbolic structural policy with zero regret. Both use the same primitives as the neural certificate. The old scalar reference and its timings remain unchanged, and no arithmetic certificate is inferred from floating-point DP output.'),
('R29-SP-T7','Rational bit complexity','Asymptotic bound and observed bit sizes',r'Section 5 gives a common-denominator bound Q^{2(T-t)+1}, bit growth O(T log Q+log((T+1)R)), and the coarse primitive-denominator version. Rational arithmetic and normalization costs are distinguished from enumeration. Each new cover records its maximum integer bit length and serialized size.'),
('R29-SP-T8','Principled budget choice','Explicit economic design problem',r'Section 4 defines budget selection over a finite prespecified family: solve minimum revision cost in each nonempty certified class, then select the least-cost class. This is exactly optimal over that union, not an efficient solution to unrestricted budget design. The experiment fixes a common budget prospectively and does not claim a numerically optimized state-budget profile.'),
('R29-SP-T9','Actual stopping boundary','Validated boundary experiment',r'The same response and evidence as R29-SP-F9 apply: preference 1.22, material lower exit, killed-kernel derivatives, explicit tails and time truncation, and all five predeclared controls. The tiny probability bound pertains only to the opposite boundary.'),
('R29-SP-T10','47-dimensional bridge','Not falsely closed',r'The full financed/current-state derivative and residual constants are not supplied by the scalar moment oracle. The original all-domain target and this missing instantiation remain explicit in the article, supplement and machine-readable disposition. No readiness test or passing finite certificate is substituted for the missing mathematical/computational object.'),
('R29-SP-T11','Hardware deployment','Exact compiled object; hardware neural rounding not certified',r'The compiler and integer-index evaluator use exact rational arithmetic and explicit tie points. Tests link every leaf and endpoint to the frozen mathematical network. The manuscript does not claim that arbitrary hardware floating-point evaluation of the network inherits that guarantee. An additional end-to-end rounding enclosure would be needed for that different deployment object.'),
('R29-SP-T12','Independent implementation and information','Terminology corrected',r'The reference is described as independently implemented, with the same model information. The new structural controls exploit all the same analytic identities and primitives. Software independence and information independence are not conflated.')]

mapping={
 'F':[2,1,3,5,4,7,8,10,12,13,15,6,14,7,16,17],
 'T':['T1','T2','T3','T4','F5','T5','T12','T6','F7','T7','F10','F10','T10','F11','T11','F13','F13','F12'],
 'P':['T2','T11','F15','F16'],
 'N':['F16','F1','F5','T5','F4','F14','F8','T10','F12','F15','T6','F14']}

def texplain(text):
 return ''.join({'_':r'\_', '^':r'\textasciicircum{}', '{':r'\{', '}':r'\}', '&':r'\&', '%':r'\%'}.get(c,c) for c in text)

def build():
 rows=load('adaptive/summary.json');baselines=load('adaptive/baselines.json');econ=load('adaptive/economic_comparisons.json');poly=load('adaptive/polynomial_controls.json')
 rawpass=sum(F(x['worst_regret_upper'])<=F(1,100) for x in rows)
 write('macros.tex',f'\\newcommand{{\\RThirtyRawPass}}{{{rawpass}}}\n')
 groups=[];costs=[];economic=[]
 for model in ('linear','cubic','quadratic'):
  z=[x for x in rows if x['model']==model];bs=next(x for x in baselines if x['model']==model and x['method']=='structured_matched')
  p=next(x for x in poly if x['model']==model)
  groups.append([model.capitalize(),f"{sum(F(x['worst_regret_upper'])<=F(1,100) for x in z)}/20",int(med(z,'leaf_count')),f"{min(x['bound_calls'] for x in z)}--{max(x['bound_calls'] for x in z)}",max(x['max_certificate_integer_bits'] for x in z),f"{number(min(x['certificate_bytes'] for x in z)/1024)}--{number(max(x['certificate_bytes'] for x in z)/1024)}"])
  total=median(sum(x[k] for k in ('training_seconds','compilation_seconds','certification_seconds','independent_check_seconds')) for x in z)
  vd=next(x for x in baselines if x['model']==model and x['method']=='vectorized_dp' and x['m']==20)
  costs.append([model.capitalize(),number(med(z,'training_seconds')),number(med(z,'compilation_seconds')),number(med(z,'certification_seconds')+med(z,'independent_check_seconds')),number(total),number(bs['seconds']),number(vd['seconds'])])
  economic.append([model.capitalize(),number(med(z,'occupancy_edits')),number(med(z,'priority_edits')),number(med(z,'expected_payoff_gain')),f"${outward(max(F(x['extra_cost_bound']) for x in z),True,12)}$"])
 write('summary.tex',table('tab:summary30','Frozen neural candidates: raw accuracy and exact proof objects','lrrrrr','Gain & Raw passes & Median cells & Bound calls & Max bits & Certificate KiB',groups,'Raw passes require an independently enclosed worst-state, all-restart regret no greater than .01. Counts are not independent economic replications. Certificate size includes exact rational endpoints and proof bounds.'))
 write('costs.tex',table('tab:cost30','Observed construction work in seconds','lrrrrrr','Gain & Fit & Compile & Cert.+check & Total & Structural & Grid DP',costs,'Each entry is descriptive single-environment timing. Total is the median of each candidate\'s full sum, not a sum of separately rounded medians. Structural is the matched-tolerance Bernstein solver; it is not the exact symbolic sign rule. Grid DP materializes $2^{20}$ states and uses binary64. All methods have the same model primitives.'))
 mx=max(F(x['extra_cost_bound']) for x in rows);thresholds=[F(x['break_even_revision_price']) for x in econ if x['break_even_revision_price'] is not None]
 text=table('tab:econ30','Discounted economic intervention metrics','lrrrr','Gain & Occupancy edits & Priority cost & Operating gain & Extra-cost upper',economic,'First three numerical columns are medians across the 20 neural candidates. The last is an outward-rounded upper bound on the largest observed upper-minus-lower cost enclosure in the stated local-loss class. All quantities concern the continuous reset density.')
 text+=f"The largest cost-enclosure gap is at most {outward(mx,True,12)}. All three polynomial proposals meet the raw .01 criterion; their details are in the computational appendix. Among the neural comparisons with positive saved intervention cost, the largest break-even shadow price is below {outward(max(thresholds),True,6)}. At the illustrative price $\\lambda=1/20$, {sum(F(x['net_advantage_at_price_1_20'])>0 for x in econ)} of {len(econ)} exact paired comparisons favor the completed policy over the near-exact structural policy after intervention cost. This is an accounting comparison, not a statistical replication count.\n"
 write('economics.tex',text)
 old=[('2/4',16,.001072,None,.002268,.001611),('3/4',64,.00803,None,.008217,.006628),('4/4',256,.03729,2.291,.03296,.03244),('4/5',625,.103,3.28,.1022,.08187),('5/4',1024,.2064,4.424,.1498,.1556),('6/4',4096,1.103,13.33,.6971,.7865),('7/4',16384,5.495,51.6,3.677,4.668)]
 leg=[]
 for dl,n,dp,fit,repair,verify in old:leg.append([dl,f'{n:,}',number(dp),number(repair+verify),number((repair+verify)/dp),'--' if fit is None else number(fit+repair+verify),'--' if fit is None else number((fit+repair+verify)/dp)])
 write('legacy.tex',table('tab:legacy30','Unchanged R29 exhaustive benchmark and total-work ratios','lrrrrrr','$d/L$ & States & DP s & Repair+check s & Ratio & Full s & Full/DP',leg,'Full includes new fitting, budget repair and verification only. Unmeasured or unavailable costs are not silently added as zero. These ratios use the displayed inherited stage times.'))
 stops=[]
 for th in ('-0.2','-0.1','0','0.1','0.2'):
  row=load('stopping/'+th.replace('-','minus').replace('.','p')+'.json')
  stops.append([th,ball_interval(row['exit_probability'],5),ball_interval(row['derivatives']['0']['enclosure'],4),ball_interval(row['derivatives']['1']['enclosure'],4),ball_interval(row['derivatives']['2']['enclosure'],4)])
 write('stopping.tex',table('tab:stopping30','Unchanged original economy at the active-boundary restart','lrrrr','$\\theta$ & Exit probability & $J_\\theta$ & $J_\\theta^{\\prime}$ & $J_\\theta^{\\prime\\prime}$',stops,'All endpoints are rounded outward from validated balls. This is one restart and a fixed constant-control class, not the original whole-domain target. The opposite-boundary and time-truncation errors are included.'))
 brackets=load('bracketing.json');br=[]
 for x in brackets:
  b,p=x['derivative_bracket'],x['poll'];br.append([x['k'],number(x['setup_seconds']+x['concavity_audit_seconds']),b['oracle_calls'],p['oracle_calls'],number(b['search_seconds']),number(p['search_seconds']),number(b['projected_gradient_upper']),number(p['projected_gradient_upper'])])
 write('bracketing.tex',table('tab:bracket30','The same validated central-state oracle under two search procedures','lrrrrrrr','$k$ & Setup+audit s & Bracket calls & Poll calls & Bracket s & Poll s & Bracket bound & Poll bound',br,'The bracketing target is .005. The inherited poll meshes have the achieved bound displayed here, not an artificially matched value. Both methods require the same oracle construction and concavity audit.'))
 # Detailed data use compact cohort IDs, with the full tag in the JSON records.
 detail='\\begingroup\\footnotesize\\setlength{\\tabcolsep}{3pt}\n\\begin{longtable}{llrrrrrr}\\caption{All neural candidates; A = Adam, B = L-BFGS}\\\\\\toprule\nGain & Method/width/seed & Raw regret upper & Cells & Calls & Occupancy & Priority & Full s \\\\\\midrule\\endfirsthead\n\\toprule Gain & Method/width/seed & Raw regret upper & Cells & Calls & Occupancy & Priority & Full s \\\\\\midrule\\endhead\n\\bottomrule\\endfoot\n'
 for x in rows:
  tag=('A' if x['method']=='adam' else 'B')+f"/{x['width']}/{x['seed']-30000}"
  full=sum(x[k] for k in ('training_seconds','compilation_seconds','certification_seconds','independent_check_seconds'))
  detail+=' & '.join([x['model'],tag,outward(F(x['worst_regret_upper']),True,6),str(x['leaf_count']),str(x['bound_calls']),number(ff(x['occupancy_edits'])),number(ff(x['priority_edits'])),number(full)])+r' \\'+'\n'
 detail+='\\end{longtable}\\endgroup\n'
 detail+=table('tab:poly30','Polynomial controls with the same observations and known degree','lrrrrr','Gain & Raw regret upper & Fit s & Compile s & Certify s & Cells',[[x['model'],outward(F(x['worst_regret_upper']),True,12),number(x['fit_seconds']),number(x['compilation_seconds']),number(x['certification_seconds']),x['leaf_count']] for x in poly],'These are exact compiled dyadic policies from fitted polynomial coefficients. An irrational root is not asserted to equal its dyadic approximation.')
 write('detailed.tex',detail)
 pre=(ROOT/'revisions/2026-09-24-r29/paper/preamble.tex').read_text().replace('Revision R29','Revision R30')
 (R/'paper/preamble.tex').write_text(pre)
 refs=(ROOT/'revisions/2026-09-24-r29/paper/references.tex').read_text().replace('\\end{thebibliography}',r'''\bibitem[Laroche, Trichelair, and Tachet des Combes(2019)]{Laroche2019}
Laroche, R., P. Trichelair, and R. Tachet des Combes (2019): ``Safe Policy Improvement with Baseline Bootstrapping,'' \emph{Proceedings of Machine Learning Research}, 97, 3652--3661.
\bibitem[Scherrer(2013)]{Scherrer2013}
Scherrer, B. (2013): ``Performance Bounds for $\lambda$ Policy Iteration and Application to the Game of Tetris,'' \emph{Journal of Machine Learning Research}, 14(36), 1181--1227.
\bibitem[FLINT Project(2026)]{Flint2026}
FLINT Project (2026): ``acb\_calc.h: Calculus with Complex-Valued Functions,'' official documentation, accessed September 24, 2026. Implementation: python-flint 0.8.0. \url{https://flintlib.org/doc/acb_calc.html}.
\end{thebibliography}''')
 refs=refs.replace('\n\\bibitem','\n\n\\bibitem').replace('\n\\end{thebibliography}','\n\n\\end{thebibliography}')
 (R/'paper/references.tex').write_text(refs)
 front=r'''\input{revisions/2026-09-24-r30/paper/preamble}
\input{revisions/2026-09-24-r30/paper/generated/macros}
\begin{document}\begin{frontmatter}
\title{TITLE}
\runtitle{RUN}
\begin{aug}\author[id=au1,addressref={add1}]{\fnms{Qian}~\snm{QI}\ead[label=e1]{qiqian@pku.edu.cn}}\address[id=add1]{\orgname{Peking University}}\end{aug}
'''
 title='Certified Bellman Operators with Neural Proposals: Adaptive Verification and Costly Policy Revision'
 abstract=r'''\begin{abstract}We study Bellman computation with a uniform operating-performance requirement and an explicit cost of revising an installed policy. Regional comparison inequalities certify whole state sets, while a constrained Bellman recursion minimizes discounted intervention cost within a certified policy class. In an operating-mode economy, exact polynomial bounds and rational neural-policy compilation cover a continuous state interval without grid enumeration. Of 60 frozen neural proposals, \RThirtyRawPass\ meet the .01 requirement before repair. Economically weighted revision costs are enclosed relative to the local-class minimum. Exact symbolic, online-guard, polynomial, and vectorized classical controls receive the same model information; neural-specific computational superiority is not inferred. The preceding exhaustive inventory pipeline remains slower than exact dynamic programming. In the original stopped consumption--portfolio economy, a killed-kernel oracle encloses payoff and derivatives at a restart with substantial exit probability and establishes a change in curvature. The original current-state, whole-domain accuracy target remains distinct from these proved and computed results.\end{abstract}
\begin{keyword}\kwd{Bellman operators}\kwd{Policy revision}\kwd{Certified computation}\kwd{Neural proposals}\kwd{Stopped control}\end{keyword}
\end{frontmatter}
'''
 (ROOT/'ECTA_R30.tex').write_text(front.replace('TITLE',title).replace('RUN','Certified Bellman Operators')+abstract+'\\input{revisions/2026-09-24-r30/paper/main}\n\\clearpage\\input{revisions/2026-09-24-r30/paper/references}\n\\end{document}\n')
 (ROOT/'SUPP_R30.tex').write_text(front.replace('TITLE','Supplement to Certified Bellman Operators with Neural Proposals').replace('RUN','Supplement R30')+'\\end{frontmatter}\n\\input{revisions/2026-09-24-r30/paper/supplement}\n\\clearpage\\input{revisions/2026-09-24-r30/paper/references}\n\\end{document}\n')
 (ROOT/'COMPUTATION_R30.tex').write_text(front.replace('TITLE','Computational Appendix: Revision R30').replace('RUN','Computation R30')+r'''\end{frontmatter}
\section{Reading the evidence}
All exact fractions, candidate parameters, raw failures, region covers, derivative enclosures, and source identities are stored under \texttt{revisions/2026-09-24-r30/results}. Displayed decimal performance bounds are rounded outward. Timings are single-environment observations, not confidence intervals. The article and supplement give model and theorem scopes; this appendix does not extend them.
\input{revisions/2026-09-24-r30/paper/generated/summary}
\input{revisions/2026-09-24-r30/paper/generated/costs}
\input{revisions/2026-09-24-r30/paper/generated/economics}
\input{revisions/2026-09-24-r30/paper/generated/stopping}
\input{revisions/2026-09-24-r30/paper/generated/bracketing}
\clearpage\input{revisions/2026-09-24-r30/paper/generated/detailed}
\clearpage\input{revisions/2026-09-24-r30/paper/generated/legacy}
\end{document}
''')
 resp=front.replace('TITLE','Response to the R29 Econometrica Referee Reports').replace('RUN','Response R30')+r'''\end{frontmatter}
\section{Review objects and substantive revision}
We address the independent second-pass report at review commit \nolinkurl{3175974aed89dac1595af174a201dcae7bcfae31} and the first R29 report at \nolinkurl{3f2724d3db622d26f6b1e439fc01311c4858ee7e}. Both concern manuscript commit \nolinkurl{788246778893695471015ce4db76e6a61a2c9ca0}. This is a new R30 scientific object, not a relabeling of R29's response to R27.

The revision adds regional certification, a minimum-intervention Bellman problem, exact weighted cost enclosures, a frozen new model/cohort, strong structural classical controls, a genuinely active stopping-boundary oracle, and a matched-oracle search comparison. The original whole-domain .01 target and the 47-dimensional derivative/residual bridge are not falsely marked complete. The entire R29 submission object and earlier history are preserved in HISTORY\_R30. The item-by-item dispositions below distinguish new results, corrected interpretation, preserved audit material, and uncompleted numerical requirements.
\section{Independent second-pass report}
'''
 disposition=[]
 for code,title,status,text in responses:
  resp+='\\subsection{'+code+': '+texplain(title)+'}\n\\textit{Disposition: '+texplain(status)+'.} '+texplain(text)+'\n'
  disposition.append({'id':code,'issue':title,'status':status,'response':text,'main_source':'revisions/2026-09-24-r30/paper/main.tex'})
 resp+='\\section{First R29 report: complete item crosswalk}\nThe following crosswalk addresses every first-report finding, technical comment, presentation comment and numbered next-revision request. Each entry adopts the substantive response and qualification in the identified second-pass item; it does not declare an uncompleted requirement resolved.\n'
 lookup={x[0]:x for x in responses}
 for category,targets in mapping.items():
  for i,target in enumerate(targets,1):
   suffix='F'+str(target) if isinstance(target,int) else target;ref='R29-SP-'+suffix;code=('R29-' if category!='N' else 'R29-')+category+str(i)
   item=lookup[ref]
   resp+='\\paragraph{'+code+'.} '+texplain(item[1])+'. See '+ref+'. '+texplain(item[2])+'.\n'
   disposition.append({'id':code,'issue':item[1],'status':item[2],'response_reference':ref})
 resp+='\\end{document}\n';(ROOT/'RESPONSE_R30.tex').write_text(resp)
 (R/'disposition.json').write_text(json.dumps(disposition,indent=2)+'\n')
 (ROOT/'HISTORY_R30.tex').write_text(r'''\documentclass[12pt]{article}
\usepackage[margin=1in]{geometry}\usepackage{pdfpages,hyperref}
\begin{document}\thispagestyle{empty}
\begin{center}{\Large Certified Bellman Operators with Neural Proposals}\\[12pt]{\large Historical Preservation Annex, R30}\\[8pt]September 24, 2026\end{center}
This annex reproduces the complete R29 article, supplement, response, computational appendix and historical annex without changing their pages. The R29 historical annex retains the R26 documents and earlier embedded material. Original source and evidence remain unchanged in their directories. Current scientific interpretation is given in \texttt{ECTA\_R30} and \texttt{RESPONSE\_R30}; historical text is preserved for audit rather than silently rewritten.
\clearpage\includepdf[pages=-]{ECTA_R29.pdf}
\includepdf[pages=-]{SUPP_R29.pdf}
\includepdf[pages=-]{RESPONSE_R29.pdf}
\includepdf[pages=-]{COMPUTATION_R29.pdf}
\includepdf[pages=-]{HISTORY_R29.pdf}
\end{document}
''')
 # Preserve the earlier pointer before updating the current review route.
 audit=R/'source_audit';audit.mkdir(exist_ok=True)
 if not (audit/'REVISION_INDEX_before_R30.md').exists(): (audit/'REVISION_INDEX_before_R30.md').write_bytes((ROOT/'REVISION_INDEX.md').read_bytes())
 (ROOT/'REVISION_INDEX.md').write_text('# Current review object: R30\n\nRead ECTA_R30.pdf, SUPP_R30.pdf, RESPONSE_R30.pdf, COMPUTATION_R30.pdf and HISTORY_R30.pdf.\n\nLatest addressed report: reviews/2026-09-24-econometrica-r29-second-pass/referee_report.md at 3175974aed89dac1595af174a201dcae7bcfae31. The first R29 report at 3f2724d3db622d26f6b1e439fc01311c4858ee7e is also covered item by item. Both reviewed manuscript 788246778893695471015ce4db76e6a61a2c9ca0.\n\nSee R30_REVIEW.md and revisions/2026-09-24-r30/disposition.json. Original sources/results are unchanged. The previous index is preserved in revisions/2026-09-24-r30/source_audit/REVISION_INDEX_before_R30.md. The original continuous all-domain .01 target is not certified; its bound remains 7.181834580823298.\n')
 print('Built R30 source tables and',len(disposition),'review dispositions; raw passes',rawpass)
if __name__=='__main__':build()
