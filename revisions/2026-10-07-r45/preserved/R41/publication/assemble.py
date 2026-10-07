"""Materialize R41 from the immutable R39 article and executed R41 records."""
from pathlib import Path
import json,hashlib,re,shutil,subprocess,math
R=Path(__file__).resolve().parents[1]; ROOT=R.parents[1]; OLD=ROOT/'revisions/2026-10-07-r39'; REL=str(R.relative_to(ROOT))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,s):
 p=R/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def tables():
 s=json.loads((R/'results/R41_STUDY.json').read_text()); comparisons=[]; records=[]
 lines=[r'\begin{table}[htbp]\centering\small',r'\caption{Direct certificates for the stored neural continuations}\label{tab:r41direct}',r'\begin{tabular}{rrrrrr}\toprule',r'$P$ & $\theta$ & All-state bound & Query bound & Execution allowance & All refinements (s)\\\midrule']
 for row in s['final']:
  n=json.loads((R/row['neural_result']).read_text()); c=json.loads((R/row['comparison_result']).read_text()); records.append(n);comparisons.append(c)
  elapsed=sum(x['seconds_through_fsync'] for x in s['neural_refinements'] if (x['price'],x['theta'])==(row['price'],row['theta']))
  lines.append(f"{row['price']:g} & {row['theta']:g} & {math.ceil(row['global_gap']*1e6)/1e6:.6f} & {math.ceil(row['max_query_gap']*1e6)/1e6:.6f} & {math.ceil(row['deployed_extra']*1e9)/1e3:.3f} & {elapsed:.3f}"+r'\\')
 lines += [r'\bottomrule\end{tabular}',r'\par\smallskip\begin{minipage}{.97\textwidth}\footnotesize Notes: The query column is the maximum certified loss at $x=1/8,1/4,1/2,3/4$, not an all-state bound. The execution allowance is in units of $10^{-6}$ and covers rounded state acquisition, transition, and costs. Every final mesh has 2,048 state cells and 1,024 action cells; the clocks sum all three attempted meshes through the result-file flush and synchronization. They exclude the inherited training service and are not an end-to-end speed comparison.\end{minipage}\end{table}']
 put('manuscript/direct_table.tex','\n'.join(lines)+'\n')
 lines=[r'\begin{table}[htbp]\centering\small',r'\caption{Precision pressure: accepted updates and rejected attempts}\label{tab:r41precision}',r'\begin{tabular}{lrrrrr}\toprule',r'Method & Certified / 12 & Accept 32 & Accept 64 & Reject 32 & Reject 64\\\midrule']
 for m,v in s['precision'].items():
  lines.append(f"{m.replace('-',' ')} & {v['passed']} & {v['accepted32']} & {v['accepted64']} & {v['rejected32']} & {v['rejected64']}"+r'\\')
 lines += [r'\bottomrule\end{tabular}',r'\par\smallskip\begin{minipage}{.97\textwidth}\footnotesize Notes: Twelve objects cross dimension and conditioning with three economic targets, $10^{-10}$, $10^{-12}$, and $10^{-14}$. Failed fixed32 services are retained. Counts for tuned precision include unsuccessful trials before restarting at the higher precision. One execution per object identifies operation of the mechanism, not a timing distribution.\end{minipage}\end{table}']
 put('manuscript/precision_table.tex','\n'.join(lines)+'\n')
 lines=[r'\begin{longtable}{rrrrr}',r'\caption{Neural cost minus the newly optimized spline cost}\label{tab:r41difference}\\\toprule',r'$P$ & $\theta$ & Initial state & Lower endpoint & Upper endpoint\\\midrule\endfirsthead',r'\toprule $P$ & $\theta$ & Initial state & Lower endpoint & Upper endpoint\\\midrule\endhead']
 worse=better=overlap=0
 for c in comparisons:
  for x,l,u in zip([.125,.25,.5,.75],c['neural_minus_reoptimized_spline']['lower'],c['neural_minus_reoptimized_spline']['upper']):
   assert l<=u and l>=-.001 and u<=.001
   worse+=int(l>0);better+=int(u<0);overlap+=int(l<=0<=u)
   lines.append(f"{c['price']:g} & {c['theta']:g} & {x:.3f} & {math.floor(l*1e9)/1e9:.9f} & {math.ceil(u*1e9)/1e9:.9f}"+r'\\')
 lines += [r'\bottomrule\end{longtable}',r'All intervals are computed by subtracting separately enclosed own-policy values; displayed endpoints are rounded outward. Positive differences mean higher neural cost. Every interval is contained in $[-10^{-3},10^{-3}]$. This is a descriptive, state-specific cardinal tolerance, not statistical equivalence or a uniform-in-state comparison.']
 put('manuscript/difference_table.tex','\n'.join(lines)+'\n')
 audit=dict(direct_comparison=dict(strictly_higher_neural_cost=worse,strictly_lower_neural_cost=better,overlap=overlap,all_16_within_descriptive_margin=.001),all_final_queries_below_002=all(x['max_query_gap']<=.02 for x in s['final']),precision=s['precision'],new_neural_refinements=len(s['neural_refinements']),new_precision_services=48)
 put('audit/DERIVED_TABLES.json',json.dumps(audit,indent=2,sort_keys=True)+'\n')
 return s,audit

def evidence(s,audit):
 return r'''\section{Direct Neural Evidence and Activated Precision Adaptation}
\label{sec:r41evidence}
The direct certificate changes both the verified continuation and the
returned policy. At each date it evaluates the trained current network
against a Bellman update using the trained next network, then stores an
action minimizing an upper interval endpoint. The terminal fit is included.
We subsequently evaluate that newly constructed policy on its own shock
tree. Its displayed values are not values of the former spline policy or
of the previously selected neural actor.

\subsection{Resolution, policy accuracy, and the economic comparison}
The design retains the four investment economies, with prices $P=1,4$ and
risk parameters $\theta=0,1$. It uses the frozen trained networks and tries
state--action resolutions $(256,128)$, $(1024,512)$, $(2048,1024)$, and,
if necessary, $(4096,2048)$. Refinement stops at the first mesh at which the
maximum certified loss at the four displayed initial states is at most
$0.02$. The first two meshes fail that query target in every economy;
the third passes in every economy. These are twelve new post-training
verification services, not twelve new training runs.

''' +(R/'manuscript/direct_table.tex').read_text()+r'''
The all-state loss remains between approximately $0.0431$ and $0.0459$.
The sharper displayed-state bounds, below $0.0179$, use independently
computed own-policy upper values and the direct neural lower bound on the
optimal value. They must not be extrapolated to unreported states. The
nonzero numerical-execution allowance is approximately $10^{-5}$; it is
added to the appropriate global comparison, not silently discarded.

At the accepted resolution we independently construct a conventional
spline policy and evaluate it at the same initial states. The supplement
reports each interval for neural cost minus this newly optimized spline
cost. All sixteen lie inside $[-0.001,0.001]$. Fourteen have strictly positive
lower endpoints; none has a strictly negative upper endpoint, and two
contain zero. Thus a small descriptive cost margin is established at these
states, while the conventional policy still has strictly smaller verified
cost in fourteen comparisons. Interval overlap is not used as a test of
equivalence. The margin is an explicit descriptive accounting tolerance,
not a preregistered economic indifference threshold or a population claim.

For $P=4$, gains over continuing the former $P=1$ rule have positive lower
endpoints at all eight displayed state--risk pairs, ranging from about
$0.0233$ to $0.0988$. The largest displayed-state near-optimality upper
bound is smaller than the smallest of these gain lower bounds. This
establishes that the direct neural policy's certified regret at the reported
states is smaller than the verified benefit of reoptimization there. It
does not make the price change, the benefit of reoptimization, or the
conventional competitor specific to NBO. All earlier adverse structural,
spline, and finite-law comparisons remain in the article and companion.

\subsection{When binary32 is no longer sufficient}
The earlier factorial correctly separates precision from caching, but its
adaptive paths never require binary64. A separate pressure catalogue now
crosses dimensions $2,8$, target condition numbers $1,16$, and policy targets
$10^{-10},10^{-12},10^{-14}$. The horizon is four, innovation scale is
$0.001$, and risk sensitivity is $0.1$. The inherited acceptance gates are
unchanged. Every proposed factor records its precision, input and output
hashes, acceptance decision, and target identity. A rejected binary32
proposal is charged even when a binary64 proposal subsequently succeeds.

''' +(R/'manuscript/precision_table.tex').read_text()+r'''
Ten of the twelve adaptive services use both precisions; the other two
succeed using binary32 alone. Fixed binary32 certifies only two objects.
Adaptive and fixed binary64 each certify all twelve. The adaptive path
accepts 116 binary32 and 42 binary64 proposals and rejects 42 binary32
proposals. These observations identify actual precision escalation rather
than inferring adaptation from the controller's name. They do not establish
that adaptive complete work is smaller than the best fixed native precision:
extra attempts and verification have real costs, and this pressure catalogue
has one clock per object. A stable efficiency ranking requires a separate
matched-work study.

\subsection{Provenance and what the work comparison measures}
The source-and-result records identify the R39 reviewed article and the
partially executed R40 development attempt separately. The latter stopped
when a deserialized policy's list-valued knots were used as a numerical
array. The new driver restores both knots and actors to arrays before
repricing the old policy. It reruns the entire catalogue in a fresh directory;
it neither overwrites the failed-run outputs nor substitutes new clocks
for the 315 earlier services. The inherited protocol predates this replay,
but some R40 outcomes had already been observed. We therefore do not call
the replay a new blinded or independently prospective experiment.

All three attempted mesh clocks, failed precision attempts, interval
verification, independent queries, result serialization, and the result
file's synchronization are retained. CPU affinity and one-thread execution
are recorded; frequency is not controlled. The inherited reference-label
construction and neural training costs are not part of the new
post-training clocks and cannot be forgotten in a from-scratch comparison.
The conventional comparison is made at the accepted mesh, not at a
separately optimized common stopping target. Accordingly neither set of
new clocks is a claim of neural end-to-end acceleration.

Theorem~\ref{thm:r41dimension} in the supplement gives the explicit cost of
multidimensional verification and continuous-innovation quantization,
including the additional own-policy query tree. This theorem extends the
certificate's domain and makes its dimensional cost visible. The new
executed nonlinear example remains one-dimensional. The evidence therefore
establishes a direct neural continuation certificate and an activated native
precision mechanism, not yet a competitive high-dimensional nonlinear
performance frontier.
'''

RESPONSE='''# Response to the R39 advisory referee report — R41

Paper: **Neural Bellman Operators**. The title, economic topic, authorship, controlled-economy framework, and full applications companion are retained. This is a revision of the existing paper, not a replacement paper on another topic. The report is an owner-commissioned advisory report, not an Econometrica editorial decision.

## Reviewed sources and revision identity

The report is pinned to `c95c0771c468db7d98ee9746a6bf5972de242569`; its reviewed manuscript is `f472a7c21f2f9db5285f1bf7746edf2d9463638e`. The development parent is `a4ec3525a7184e2d2fe04953d131fbfd725ac941`. The complete R39 publication and R40 failed-run artifacts are retained with their hashes. New material is confined to `revisions/2026-10-07-r41`, apart from root entry points, the repository reading guide, and its dedicated workflow. No historical paper, report, source, or clock is deleted or overwritten.

We thank the referee for distinguishing the validity of the comparison theorem from identification of a specifically neural numerical contribution. We retain NBO as the object of study and address the mathematical and implementation objections directly. We do not treat a negative benchmark as a reason to change the topic, and we do not represent an unestablished performance advantage as a proved result.

## B1 / M1 — The learned continuation itself

**Implemented and proved.** The new main section, “The Trained Continuation as the Certified Bellman Object,” evaluates every stored current network against the Bellman operator containing its own stored future network. The residual endpoints include both current-network and future-network arithmetic, state cover, continuous-action cover, and terminal-network discrepancy. The selected policy is newly constructed from these neural Q intervals and evaluated on its own future shock tree. The global guarantee is against all adapted feasible policies, not just neural policies.

The proof explicitly includes the current network's Lipschitz term, which cannot be omitted merely because the former spline interpolated its nodes. Rational affine-region compilation is an exact evaluation of the network's trained weights, not substitution of a reference spline. Tests execute the direct verifier with the conventional spline evaluator disabled. The networks' original spline-label training history and cost remain disclosed. This closes the distinction between a spline-certified neural proposal and certification of the learned Bellman continuation itself without claiming reference-free training.

## B2 / M2 — Precision actually changes

**Mechanism exercised; efficiency not presumed.** The pressure design has twelve objects and four methods, hence 48 services. Fixed32 passes two objects. Fixed64, adaptive, and tuned precision each pass all twelve. Adaptive execution accepts 116 binary32 and 42 binary64 proposals, with 42 rejected binary32 proposals. Ten adaptive services mix precisions. Every attempted input, output, precision, target, and acceptance is retained; the acceptance gate is inherited unchanged.

The design predates the new complete replay, but some failed R40 outputs had been observed. It is not described as a fresh prospective experiment. One execution per object is sufficient to demonstrate an activated branch and its certificate, not stable adaptive superiority over the best fixed precision. That comparative-work part of the comment remains open to measurement.

## B3 / M3 — The strongest conventional comparator

**Direct comparison added; unfavorable results retained.** At the accepted resolution a new conventional spline policy is independently constructed and evaluated. All sixteen neural-minus-spline cost intervals are contained within a descriptive cardinal margin of plus or minus 0.001. Fourteen nevertheless have strictly positive lower endpoints, none has a strictly negative upper endpoint, and two overlap zero. Thus the reported neural policy is close at these states, not superior. Overlap is never equated with equivalence.

The comparison uses the same final verification resolution; it does not tune both procedures to a separately chosen common global accuracy. Its clocks are not presented as a matched end-to-end work victory. All R39 structural and spline dominance observations remain visible. A competitive method-specific complete-work frontier has not been established by these new services.

## B4 / M4 — Dimension and uncertainty

**General extension and explicit work theorem added; nonlinear scaling experiment still required.** The supplement extends the direct neural certificate to compact multidimensional state and action spaces and continuous innovations with a certified quantizer. A coupling argument charges innovation discretization inside the same residual and actor account. The theorem gives state/action/innovation cover counts, network-forward and risk-evaluation work, streaming storage, output size, attempted-refinement sums, and the separate exponential policy-query tree cost.

This is a genuine mathematical extension, not an empirical claim that a scalar execution scales freely. The current nonlinear execution is still scalar; quadratic dimensions 2 through 32 are not relabeled nonlinear evidence. A coupled multidimensional nonlinear benchmark with a strong sparse, projection, or fitted dynamic-programming baseline remains a substantive experimental requirement. No high-dimensional neural advantage is asserted without that experiment.

## B5 / M5 — Economic gain versus numerical regret

**Sharper direct regret and contemporaneous baseline added.** Every economy now passes a 0.02 target at the four declared initial states. The largest displayed-state bound is below 0.0179. Full-domain bounds are separately reported, approximately 0.0431 to 0.0459. These are not interchangeable. At the eight changed-price state-risk pairs the verified gain over the old rule has lower endpoints above 0.0232. Thus, at the displayed states, the certified neural regret is smaller than the verified gain from reoptimization.

The paper also supplies the neural-versus-new-spline cost intervals requested in B3, so the stale-rule comparison is no longer the only policy contrast. Reoptimization remains available to both methods; no economic result is attributed exclusively to NBO merely because the old rule is deliberately not reoptimized. The 0.001 margin is descriptive, not a preregistered welfare threshold.

## B6 / M6 — Nonzero numerical execution

**Instantiated for the nonlinear program.** The implementation supplies rational range-and-error propagation through the actual separate-operation binary32 graph. It charges state acquisition, transition, stage cost, terminal cost, and clipping; dyadic action values and selection cutpoints are exactly representable. A discontinuous actor is handled by the distance to the selected node, not an assumed actor Lipschitz constant. The resulting additional global allowance is about 0.00001 and is never set to zero.

The main proposition distinguishes the feasible rounded actor in the original economic model from the numerical economy with rounded transitions and accounting. Only the former has a nonnegative gap against the original optimum. The latter has a valid upper excess-cost bound, but need not have a nonnegative difference because its primitives are perturbed. Recursive risk is interval-evaluated with its stated mathematical meaning. Fused arithmetic, flush-to-zero hardware, and physical actuators are outside this tested contract. This instantiation does not retroactively certify every retained quadratic deployment pipeline.

## B7 / M7–M8 — Complete work and stable timing

**Work accounting sharpened; clocks kept descriptive.** All failed meshes and precision attempts are retained. The neural table sums all three attempted meshes through result-file synchronization, rather than reporting only a favorable final mesh. The historical label-construction and training work is explicitly outside these new post-training clocks and remains chargeable in a from-scratch comparison. CPU affinity, one-thread execution, native versions, code hashes, and frequency-control status are recorded. The data do not warrant a timing-distribution or asymptotic-speed claim.

The work theorem displays state/action dimension, innovation support or quantization size, horizon, network evaluation size, risk-evaluation precision costs, and output/working storage. It distinguishes precision-dependent primitive cost and conditioning data from an unjustified universal unit-cost constant. Refinement only reduces verification slack; a fixed inaccurate network retains its intrinsic Bellman residual floor. An additional repeated matched-work scaling experiment is still needed for the full frontier requested by the referee.

## B8 / M9–M10 — One paper and one authoritative chain

**Integrated rather than replaced.** The abstract, introduction, conclusion, and reading guide now lead from the stored learned continuation to its own Bellman residual, actor allowance, terminal discrepancy, own-policy comparison, and execution account. The main article and supplement are materialized self-contained sources. Earlier theoretical statements, complete original applications, historical manuscripts, and adverse empirical results are retained. A label-preservation audit confirms that no inherited active theorem label disappears.

The complete constructive economic instances are the recursive quadratic capital economy and scalar nonlinear investment economy. The continuous-innovation multidimensional extension is identified as a theorem with explicit cost, not as an executed economy. The controlled-diffusion, recursive-utility, endogenous-preference, temporal-self, and game applications retain their own hypotheses and are not certified simply by citing the two numerical instances. The retained breadth is a framework with explicit obligations, not a claim that every application's assumptions have been computationally discharged.

## Source repair and verification

The R40 science attempt failed after reading a JSON policy whose knot and actor arrays remained Python lists. R41 restores both numerical arrays before repricing, adds a regression check for that restoration, and reruns the entire catalogue in a fresh directory. The failed artifact and all earlier clocks are preserved. No partial result is silently promoted to a complete execution.

The publication includes direct neural and risk arithmetic fixtures, exact rational native-execution fixtures, source/record hashes, a deterministic result audit, four compiled active PDFs, complete historical companions, and a release manifest. Compilation and numerical audit are evidence of the deposited revision's internal consistency, not independent referee approval or a proof of a comparative advantage that was not observed.
'''

def assemble():
 s,a=tables(); ev=evidence(s,a);put('manuscript/direct_evidence.tex',ev)
 for doc in ['ECTA','supp','applications']:
  text=(OLD/(doc+'.tex')).read_text().replace('2026-10-07-r39','2026-10-07-r41')
  if doc=='ECTA':
   abstract='''This paper develops Neural Bellman Operators for policy evaluation and feasible improvement in controlled economies. Centered continuation errors connect learned values to full-policy loss. A direct nonlinear certificate evaluates each trained network against the Bellman operator containing its own future network, including all-state residuals, selected actions, and terminal error. A separate execution account covers rounded state acquisition, transitions, and costs. A quadratic construction connects hidden-factor updates to economic tolerances; a pressure experiment activates native precision escalation and retains rejected attempts. In nonlinear investment economies, direct neural policy-loss bounds at declared states are smaller than verified gains from reoptimization after an investment-price change. Contemporaneously optimized spline policies remain competitive and often have strictly smaller cost. A dimension-explicit extension covers continuous innovations and accounts for verification and policy-query work. The controlled-economy framework and complete applications are retained with their application-specific hypotheses.'''
   text=re.sub(r'(?<=\\begin\{abstract\}).*?(?=\\end\{abstract\})','\n'+abstract+'\n',text,count=1,flags=re.S)
   anchor=r'\section{Verified Floating-Point Implementation}'
   # Use the actual existing heading containing the stable section label.
   m=re.search(r'\\section\{[^}]+\}\s*\\label\{sec:r39floating\}',text);assert m
   text=text[:m.start()]+(R/'manuscript/direct_neural.tex').read_text()+'\n'+text[m.start():]
   m=re.search(r'\\section\{[^}]+\}\\label\{sec:r37evidence\}',text);assert m
   text=text[:m.start()]+ev+'\n'+text[m.start():]
   roadmap=r'''\paragraph{The current operational chain.}
Section~\ref{sec:r41direct} makes the stored trained network itself the
Bellman object and distinguishes original-model policy loss from numerical
execution cost. Section~\ref{sec:r41evidence} reports its direct certificates,
contemporaneously reoptimized comparators, and precision-pressure paths.
The dimension and continuous-innovation extension in
Theorem~\ref{thm:r41dimension} exposes verification cost explicitly.
The earlier comparison and training results below remain in force under
their stated assumptions. The scalar nonlinear execution does not stand in
for a coupled high-dimensional performance experiment.
'''
   text=text.replace(r'\paragraph{Contribution and roadmap.}',roadmap+'\n'+r'\paragraph{Contribution and roadmap.}',1)
   text=text.replace('Precision adaptation reduces storage precision and recorded\ncomplete service time relative to the two inherited neural constructions\nin both specified regimes.','The earlier joint adaptive-cached implementation reduces stored precision and has smaller recorded complete-service clocks than the two inherited neural constructions in both specified regimes; that contrast alone does not identify a precision effect.')
   text=text.replace(r'\bibliographystyle{ecta-fullname}',r'''The direct neural chain now certifies the learned continuation itself,
including its own terminal discrepancy and the policy selected from its own
future values. Its execution allowance is nonzero, and its pressure paths
actually reject binary32 before accepting binary64. These are constructive
advances in the same NBO framework. The direct comparisons also identify
what they do not establish: cost closeness at specified states is not neural
superiority, and an explicit multidimensional work theorem is not an
executed high-dimensional frontier.

\bibliographystyle{ecta-fullname}''')
  elif doc=='supp':
   text=text.replace(r'\bibliographystyle{ecta-fullname}',(R/'manuscript/direct_supplement.tex').read_text()+'\n'+(R/'manuscript/difference_table.tex').read_text()+'\n'+r'\bibliographystyle{ecta-fullname}')
  put(doc+'.tex',text)
  shutil.copy2(OLD/(doc+'_references.bib'),R/(doc+'_references.bib'))
 for n in ['econsocart.cls','econsocart.cfg','ecta-fullname.bst']:shutil.copy2(OLD/n,R/n)
 (R/'build').mkdir(exist_ok=True)
 for p in (OLD/'build').glob('*.aux'):shutil.copy2(p,R/'build'/p.name)
 for name in ['historical_article.pdf','historical_supplement.pdf']:shutil.copy2(OLD/'build'/name,R/'build'/name)
 put('response.md',RESPONSE)
 subprocess.run(['pandoc',str(R/'response.md'),'-f','markdown','-t','latex','--standalone','-V','geometry:margin=1in','-V','fontsize=11pt','-V','fontfamily=mathpazo','-o',str(R/'response.tex')],check=True)
 text=(R/'response.tex').read_text()
 text=re.sub(r'\\texttt\{([0-9a-f]{40})\}',lambda m:r'\allowbreak'.join(r'\texttt{'+m[1][i:i+8]+'}' for i in range(0,40,8)),text)
 put('response.tex',text)
 label=re.compile(r'\\label\{([^}]+)\}');old_labels=set();new_labels=set()
 for doc in ['ECTA','supp','applications']:
  old_labels.update(label.findall((OLD/(doc+'.tex')).read_text()));new_labels.update(label.findall((R/(doc+'.tex')).read_text()))
 assert not old_labels-new_labels
 put('audit/PRESERVATION.json',json.dumps(dict(inherited_sources={str(p.relative_to(ROOT)):sha(p) for p in OLD.glob('*.tex')},inherited_active_labels=len(old_labels),missing_inherited_active_labels=sorted(old_labels-new_labels),historical_deletions=[],historical_overwrites=[],current_editorial_changes=['abstract','introduction operational chain','historical precision interpretation','conclusion'],new_main_modules=['direct neural certificate','numerical execution','direct evidence and activated precision'],new_supplement=['rational arithmetic','dimension and continuous innovations','own-policy differences'],applications_complete=True),indent=2,sort_keys=True)+'\n')
 for doc in ['ECTA','supp']:(ROOT/(doc+'.tex')).write_text(r'\input{'+REL+'/'+doc+'.tex}\n')
 readme='''# Neural Bellman Operators — R41

Revision of the existing NBO paper responding to the R39 advisory referee report. The title, original economic framework, and complete applications remain unchanged.

## Read the revision

- [Main article](build/ECTA.pdf) and [self-contained source](ECTA.tex).
- [Technical supplement](build/supp.pdf), including arithmetic and dimension/continuous-innovation work proofs.
- [Point-by-point response](response.md) and [response PDF](build/response.pdf).
- [Complete applications](build/applications.pdf), [historical article](build/historical_article.pdf), and [historical supplement](build/historical_supplement.pdf).
- [Executed study](results/R41_STUDY.json), [deterministic audit](audit/RESULT_AUDIT.json), [release audit](audit/RELEASE_AUDIT.json), and [file hashes](audit/FILES_SHA256.json).

The learned current and future networks are now directly Bellman-certified. The new four-economy study passes a 0.02 query-state policy target; all-state bounds are reported separately. Binary32 rejection and binary64 escalation are executed and charged. Numerical execution has a nonzero error account. A contemporaneously reoptimized spline remains a strong competitor; no unobserved neural speed or cost superiority is claimed. The multidimensional continuous-innovation theorem is not misreported as an executed nonlinear scaling benchmark.

The R40 failed-run outputs and R39 publication are preserved; new clocks are not replacements for inherited clocks. See the response for exactly which comparative-performance requests still require additional evidence.

Build from repository root: `python revisions/2026-10-07-r41/publication/build.py`. Reproduce science in a fresh directory, never over completed records: `python revisions/2026-10-07-r41/code/study.py`.
'''
 put('README.md',readme)
 (ROOT/'README.md').write_text(readme.replace('](build/',']('+REL+'/build/').replace('](ECTA.tex)',']('+REL+'/ECTA.tex)').replace('](response.md)',']('+REL+'/response.md)').replace('](results/',']('+REL+'/results/').replace('](audit/',']('+REL+'/audit/'))
if __name__=='__main__':assemble()
