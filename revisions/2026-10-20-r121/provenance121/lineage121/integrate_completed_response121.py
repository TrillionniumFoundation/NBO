#!/usr/bin/env python3
"""Editorial integration of completed R121 records; no scientific execution.

Preserves exact original quotes, all nested R120 records, and pre-result bytes.
Reads only complete saved result tables and exit receipts.  It does not fit,
evaluate an economic model, draw data, change a protocol, or run a timing test.
"""
from pathlib import Path
from datetime import datetime, timezone
from fractions import Fraction
import copy
import gzip
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / 'results121/report-attempt01/tables121'
MAP_PATH = ROOT / 'provenance121/R97_REQUIREMENTS121.json'
BODY_PATH = ROOT / 'new121/response121_body.tex'
RETENTION_PATH = ROOT / 'CONTENT_RETENTION_MAP121.md'


def identify(path):
    body = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)), 'bytes': len(body),
            'sha256': hashlib.sha256(body).hexdigest(),
            'git_blob_sha1': hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()}


def read_jsonl(name):
    with (gzip.open(TABLES / name, 'rt') if name.endswith('.gz') else (TABLES / name).open()) as f:
        return [json.loads(line) for line in f]


def put(action, boundary, route, *tables):
    return {'action_latex': action, 'remaining_latex': boundary,
            'printed_route_latex': route, 'table_paths': list(tables)}


ITEMS = {
'B1': put(
r'''The executed study now compares VALUE and MARGINAL within identical paid information, features, coefficient bounds and qualification services, and compares those actors with the full conventional menu. All 512 primary ReLU--hinge raw-proposal pairs and all 512 delivered-action pairs are equal; the hinge pays the ReLU acquisition and required audit costs. All 32 primary ReLU/full-menu sufficient and upper not-ruled-out price regions are empty, as are all 160 individual timing regions and all 32 five-clock intersections. Changing the learning objective therefore supplies no neural-specific policy or adoption advantage here. The marginal regularity, finite fitting and action-path results apply to every eligible representation and are stated as shared mathematics.''',
r'''A neural-specific contribution still requires a strict economic or information benefit against methods with the same features, information, feasible policies and full resource bill. The present empty recorded-menu regions do not prove impossibility for every economy, network, or deployment criterion.''',
r'''Table~\ref{tab:learninggains121}, Table~\ref{tab:reluprices121}, and the exact equal-feature rows.''',
'equal_feature_control121.jsonl.gz','all_price_menus121.jsonl.gz','all_five_clock_price_intersections121.jsonl.gz','loss_contrasts121.jsonl'),
'B2': put(
r'''The new constructive upper result obtains outward action-marginal labels from integrated original-risk value enclosures, with explicit finite-difference, risk-level, capacity and rounding allowances. The two actually acquired budgets contain 650 and 2,106 original root-$Q$ contexts across the two risks, respectively, rather than free derivative labels; 1,413,828 terminal label contexts are charged in total. VALUE receives the same complete bundle as MARGINAL. These executed information counts make the interface cost visible. They do not enlarge the class covered by the inherited deterministic univariate fixed-tail lower bound. The original-formula online method remains eligible and its actual cost is retained.''',
r'''No randomized, multivariate, nonuniform-law, formula-oracle, bit-complexity or end-to-end Bellman minimax lower bound is inferred from the earlier scalar oracle construction. Matching lower and upper bounds for the smooth original economy remain open at a separately specified information interface.''',
r'''Proposition~\ref{prop:marginalprobe121}, Table~\ref{tab:allfits121}, and the acquisition rows.''',
'fit_and_acquisition121.jsonl','budget_processes121.jsonl','budget_scaling121.jsonl'),
'B3': put(
r'''The new theorem controls the integral of continuation-marginal error along feasible action paths, treats feature derivative jumps explicitly, and keeps the state anchor when composing recursive values. The stationarity proposition converts an outward original-objective KKT interval into regret and action-distance bounds. The numerical distinction is now decisive: the finite-node marginal residual falls in all 28 paired treatments, but the independently enclosed 64-state mean gain $J_{\rm VALUE}-J_{\rm MARGINAL}$ is strictly negative in every treatment; 889 of 1,792 final action pairs differ. Thus fitting the reported node criterion better does not establish better decisions. The independent tables report original objectives, regret and action-error upper bounds, not only representation error.''',
r'''The off-design feature-range cover is a proved conditional construction but was not numerically certified for the fitted actors. Neither the node residual nor the finite optimizer gap can be substituted for that missing global premise, and no neural geometry separation follows from the shared hinge representation.''',
r'''Theorem~\ref{thm:quotientlearning121}, Proposition~\ref{prop:marginalpolicy121}, Table~\ref{tab:learninggains121}, and Table~\ref{tab:allpolicies121}.''',
'loss_contrasts121.jsonl','policy_cells121.jsonl','fit_and_acquisition121.jsonl'),
'B4': put(
r'''We implemented and independently audited the replacement objective, rather than defending the previous internal span. MARGINAL minimizes a bounded finite-node original-action risk-marginal error; its 28 exact primal/dual gap upper bounds lie between approximately $1.13\times10^{-9}$ and $2.58\times10^{-8}$. All 28 node residuals improve, yet first rejections increase from 60 under VALUE to 294 under MARGINAL, all 28 independently enclosed sample mean gains are negative, and complete primary cohort service is slower in 24 of 28 comparisons. The fixed joint population intervals all contain zero. This is new adverse evidence about the proposed learning-to-service connection, not a positive result borrowed from R120.''',
r'''The intended economic improvement is not established by this experiment. A useful next algorithm must control the off-design action paths and qualification burden, with its acquisition and certification costs paid; the present finite training certificate does not certify that improvement or a positive population gain.''',
r'''Proposition~\ref{prop:boxtraining121}, Table~\ref{tab:learninggains121}, Table~\ref{tab:rawproposals121}, and Table~\ref{tab:fullcost121}.''',
'loss_contrasts121.jsonl','policy_cells121.jsonl','independent_fit_audits121.jsonl.gz','all_cohort_clocks121.jsonl'),
'B5': put(
r'''The complete comparison includes quadratic, degree-two and degree-three polynomial, spline, grid, equal-feature hinge and direct original-formula online controls. Each learned pair pays for the same acquired label bundle and its own fit and required rational audit; the hinge also pays its parent ReLU charge. All rejected proposals, conventional fallback, serialization and complete service clocks remain charged. The exact frontiers contain 1,392 volume-cost rows and 51,072 pairwise price constraints, including four prespecified reuse volumes. No ReLU full-menu sufficient region or upper not-ruled-out region survives in any primary or individual timing scenario. The conventional alternatives therefore remain essential to assessing whether learning buys an economic service.''',
r'''A finite recorded-menu cost frontier is not a universal computational lower bound. Acquisition allocations are derived from measured process components, not separate observed standalone fits, and the independent all-policy research validation is also reported in the study ledger even when it is not a deployment charge.''',
r'''Table~\ref{tab:fullcost121}, Table~\ref{tab:allclocks121}, Table~\ref{tab:reluprices121}, and the complete research ledger.''',
'all_volume_costs121.jsonl','all_cost_frontiers121.jsonl.gz','all_price_constraints121.jsonl.gz','selected_research_stage_costs121.jsonl'),
'B6': put(
r'''The completed economic comparison stays with the same original constrained investment objective and continuous innovation law. Reported prices value a second of computation in normalized objective units and solve the stated strict gain-minus-price-times-extra-cost inequalities exactly. The four reuse volumes and the full conventional menu were fixed before outcomes. The resulting 32 primary, 160 individual-clock and 32 all-five-clock ReLU comparisons have empty sufficient and upper not-ruled-out regions. Their meaning is a conditional decision-service comparison on the specified state cohorts, with exact endpoint and strictness flags, rather than an externally identified willingness to pay.''',
r'''The exercise does not identify welfare prices, an empirical adoption rate or a calibrated firm-level technology choice. Upper not-ruled-out intersections are only pairwise feasibility conditions, not jointly attainable adoption claims. A consequential calibrated application still requires its own data, information model and validation.''',
r'''Table~\ref{tab:reluprices121} and the exact full-menu price constraints and menus.''',
'all_price_constraints121.jsonl.gz','all_price_menus121.jsonl.gz','all_five_clock_price_intersections121.jsonl.gz'),
'B7': put(
r'''The current 56 stored actors and both independent fit audits were published at M before the new 640-byte entropy draw; D then fixed 64 exact two-dimensional states before policy outcomes. Independent original-primitive evaluation covers all 1,301 distinct final-policy and raw-proposal keys and all 3,712 policy comparisons. The prespecified simultaneous family contains two optimum means, 58 regret means, 28 signed learning gains, 112 signed threshold events and 116 one-sided rejection endpoints, with joint coverage at least 95\% under its stated sampling assumptions. All 28 signed population mean-gain intervals contain zero, despite all 28 enclosed sample means being negative. No R97 actor or R120 sample result is transferred to these new actors.''',
r'''The 64 independent states are the statistical units; risks, methods, matched hinges and five repeated clocks do not multiply sample size. Population coverage is conditional on the frozen actors and the stipulated ideal entropy model for the 40-bit product-uniform state law. Cross-representation population adoption and population superiority are not established.''',
r'''Table~\ref{tab:learninggains121}, Table~\ref{tab:allpolicies121}, and the complete fixed population-inference rows.''',
'all_policy_population_inference121.jsonl.gz','all_signed_threshold_events121.jsonl','original_optimum_inference121.jsonl','loss_contrasts121.jsonl'),
'B8': put(
r'''Independent verification now begins at the actual finite fitting problem. A separate standard-library rational implementation reconstructs the stored feature values and derivatives, coefficient rounding, objective intervals and primal/dual witnesses for all 56 actors, executing 771,005 assertions. There are 48 actual optimizer fits and eight exactly matched hinge copies, which are not counted as independent fits. For the 28 MARGINAL actors, the finite-box minimax gap is enclosed by exact rational bounds whose largest upper endpoint is approximately $2.58\times10^{-8}$. The VALUE least-squares audit is reported separately. After fitting, an independent original-primitive evaluator performs 1,406,549 assertions over 167,829 terminal contexts and all delivered and first-proposed policies.''',
r'''The audited problem has fixed features and a prespecified coefficient box. It does not certify globally optimal hidden features, the best unrestricted approximant, the unexecuted global feature cover, or the rounded future controller by exact policy equality. Independence here means a separate implementation, not external human authorship.''',
r'''Proposition~\ref{prop:boxtraining121}, Table~\ref{tab:allfits121}, and the independent fit and policy execution receipts.''',
'independent_fit_audits121.jsonl.gz','fit_and_acquisition121.jsonl','policy_cells121.jsonl'),
'B9': put(
r'''The active account is organized around the original investment decision, integrated-risk marginal learning, its complete mathematical assumptions and the executed economic comparison. The supplement carries complete new proofs, including derivative jumps, boundaries, action-path transport, stationarity and recursive anchors; development material carries the full 58-policy, 28-contrast, clock, cost and price tables. Historical theorems, corrigenda, raw evidence and all 35 original reports remain source-bound. The exact 30-item current response retains every original quotation and every complete R120 map record. The 1,049 inherited item/parent routes remain recoverable without being counted as 1,049 independent or closed scientific issues.''',
r'''Source organization is not evidence that the unresolved neural or economic contribution has been achieved. Final document sizes and source/PDF identities are read from the actual build and publication records. The dated theorem/code registry is a structural index, not a new proof-by-proof revalidation of every historical source.''',
r'''The current source structure, \nolinkurl{CONTENT_RETENTION_MAP121.md}, \nolinkurl{SOURCE_READY121.json}, and \nolinkurl{EVIDENCE_MANIFEST121.json}; later source-specific CI and publication receipts have their own identities.''',
'policy_cells121.jsonl','loss_contrasts121.jsonl'),
'B10': put(
r'''The new experiment produces a sharper scientific obstruction inside the NBO problem: accurately solving an action-marginal finite training objective still fails to improve the delivered original decision. All 28 node residuals fall, all 28 sample mean gains are negative, first rejections rise to 294 from 60, and the full primary cohort service is slower in 24 comparisons. At the same time, all 3,712 delivered policies satisfy the prespecified production qualification and independent evaluation records their original regret and action-error bounds. This separates successful finite fitting and a functioning safeguard from the unachieved learning advantage. The action-path and KKT results specify the missing off-design quantities that a stronger method must actually control.''',
r'''These adverse findings do not complete the original ambition of a computationally competitive neural Bellman operator. Global action-path certification, cost-effective precision allocation and a strict equal-information economic advantage remain research obligations. The paper retains its original problem and Econometrica objective while documenting this unmet mechanism.''',
r'''Table~\ref{tab:learninggains121}, Table~\ref{tab:rawproposals121}, Table~\ref{tab:fullcost121}, and Theorem~\ref{thm:quotientlearning121}.''',
'loss_contrasts121.jsonl','policy_cells121.jsonl','fit_and_acquisition121.jsonl'),
'M1': put(
r'''The author retains Neural Bellman Operators and the Econometrica numerical-methods objective. The scientific concentration requested here is implemented within that research identity: can learning the marginal of the integrated original continuation risk improve the feasible original actor after qualification and full information costs? The revised theory and the frozen VALUE/MARGINAL experiment directly address that question. The executed answer is adverse for this design: every paired sample mean favors VALUE, all fixed population intervals remain unresolved, and the ReLU full-menu price sets are empty. Both the shared methodological contribution and the unachieved neural improvement are stated explicitly.''',
r'''Literal redirection to a different paper or venue is not followed. A negative result is not relabeled as completion of the neural economic objective; the remaining action-path, information-efficiency and adoption questions continue inside the original model.''',
r'''The main theoretical sequence and Table~\ref{tab:learninggains121}; the unchanged original report and complete prior treatment remain above.''',
'loss_contrasts121.jsonl','all_price_menus121.jsonl.gz'),
'M2': put(
r'''The revised novelty statement separates known ingredients from the original-risk construction. Action-null quotients, bounded convex readouts, dual witnesses and KKT regret bounds retain their historical and classical attribution. The new proof derives constrained integrated-AVaR marginal regularity from the investment primitives, obtains paid outward probe labels, verifies the finite stored problem, and carries interval marginal errors through nonsmooth feature ranges into feasible action comparisons while preserving recursive anchors. The actual 2,756 original root-$Q$ contexts and separate fit audits make that construction executable. The experiment establishes no optimality of its information complexity and no neural-exclusive representation gain.''',
r'''The inherited deterministic point-value univariate fixed-$\alpha$ lower bound does not become a general Bellman lower bound through this application. Matching bounds at the original-formula interface and a decision-sensitive learning guarantee beyond the stated cover assumptions remain unproved.''',
r'''Theorem~\ref{thm:rootmarginal121}, Proposition~\ref{prop:marginalprobe121}, Proposition~\ref{prop:boxtraining121}, and Theorem~\ref{thm:quotientlearning121}.''',
'fit_and_acquisition121.jsonl','budget_processes121.jsonl'),
'M3': put(
r'''An action-aligned acquisition target is now actually implemented: the known current-action cost is kept exact, the critic fits intervals for the original integrated continuation-risk marginal in original action units, and its bounded minimax readout has an independent finite optimality audit. VALUE receives the same probes and other paid information. This change lowers all 28 node residuals, but the final actions differ in 889 pairs and the independently bounded sample mean gain is negative in all 28 treatments. The action-path theorem explains why a node fit alone cannot provide the needed off-design guarantee; the proof requires a feature-range cover that this campaign has not certified.''',
r'''An implemented marginal target is not yet a successful policy-improvement or acquisition-allocation mechanism. A globally certified path budget, an economically optimal stopping rule and a positive full-cost learning benefit require further algorithmic development and a separate prospectively frozen experiment.''',
r'''Proposition~\ref{prop:marginalprobe121}, Theorem~\ref{thm:quotientlearning121}, Table~\ref{tab:learninggains121}, and Table~\ref{tab:allfits121}.''',
'loss_contrasts121.jsonl','fit_and_acquisition121.jsonl','all_qualification_attempts121.jsonl.gz'),
'M4': put(
r'''The executed conventional frontier includes quadratic, degree-two and degree-three polynomial, spline, grid, ordinary hinge with the identical ReLU features and coefficients, and direct online original-formula solution. Their information, feasible actor domain and qualification tolerances are held fixed within the prescribed comparisons. The hinge pays the parent learned acquisition and audit charge and matches every one of the 512 primary ReLU raw and delivered actions. Every one of the 32 primary and 160 individual-clock ReLU full-menu upper not-ruled-out price regions is empty. This treats equivalent geometry as equivalent rather than attributing an ordinary hinge construction exclusively to a network.''',
r'''The fixed feature menus and two acquisition budgets do not exhaust conventional approximation or neural architectures. An exclusive neural claim needs a resource-matched separation beyond these identical-feature controls; the present data supply none.''',
r'''Table~\ref{tab:allfits121}, Table~\ref{tab:fullcost121}, Table~\ref{tab:reluprices121}, and the equal-feature control rows.''',
'equal_feature_control121.jsonl.gz','fit_and_acquisition121.jsonl','all_price_menus121.jsonl.gz'),
'M5': put(
r'''Every primary raw proposal, qualification attempt, rejection, returned policy and matched timing row is retained. The 4,066 attempts include all 354 first rejections and their conventional fallback; none is removed from costs or independent evaluation. The new adverse pattern---28 improved node fits with 28 worse sample means, 294 versus 60 first rejections, and no ReLU full-menu price region---is presented alongside all favorable state-level threshold events. The 28 mean comparisons are not independent replications, since the same 64 states and matched feature controls recur. R49, R97, R119 and R120 negative evidence remains unchanged and is not used in place of this new execution.''',
r'''No adverse cell, unfavorable clock or failed historical attempt is converted into a favorable aggregate by reselection or retiming. Current sample signs do not establish population harm: all 28 fixed population mean-gain intervals still contain zero.''',
r'''Table~\ref{tab:learninggains121}, Table~\ref{tab:rawproposals121}, Table~\ref{tab:allclocks121}, and the complete signed threshold rows.''',
'all_qualification_attempts121.jsonl.gz','all_signed_threshold_events121.jsonl','loss_contrasts121.jsonl','all_cohort_clocks121.jsonl'),
'M6': put(
r'''The actual application remains the original two-date constrained investment problem with two state coordinates, continuous innovations, nested AVaR at $\alpha=1/2,3/4$, and the unchanged implemented future-policy allowance. Independent evaluation now reports original objective intervals, original-optimum support bounds, policy regret, action-error upper bounds and complete computation costs for all 58 cells. All 3,712 delivered policies meet the frozen production qualification, but MARGINAL worsens every paired sample mean and yields no ReLU full-menu adoption region. These are economically interpretable investment decisions under the original objective; they are not gains from a substitute posted-price or recursive-utility model.''',
r'''A consequential externally calibrated application and a demonstrable full-cost neural economic benefit remain unfinished. The preserved stochastic-control, nonlinear recursive-utility and NDU/FBSDE connections retain their own hypotheses; this two-date execution neither validates those different models nor changes the intended research direction.''',
r'''The original-economy definitions, Table~\ref{tab:allpolicies121}, Table~\ref{tab:rawproposals121}, and Table~\ref{tab:fullcost121}.''',
'policy_cells121.jsonl','state_economics121.jsonl.gz','all_volume_costs121.jsonl'),
'M7': put(
r'''Both prespecified budgets were acquired and fitted in full before the held-out states: 325 and 1,053 original root-$Q$ contexts per risk, a ratio of $81/25$. The grid and spline feature counts and all actual acquisition, audit and service costs are reported at both budgets. Among the 28 coarse-to-fine original sample mean comparisons, 15 enclosed gains are strictly positive, 12 strictly negative and one contains zero. These are descriptive comparisons on the common fresh sample, not an added population inference family. Different design-node sets also prevent a finite-node residual ratio from serving as an off-design convergence certificate.''',
r'''The experiment is genuine information-budget scaling at fixed dimension and horizon. It does not establish dimension scaling, horizon scaling, an asymptotic rate or monotone improvement with more data; those remain separate scientific requirements.''',
r'''Table~\ref{tab:budgetscaling121}, Table~\ref{tab:allfits121}, and both actual acquisition-process receipts.''',
'budget_scaling121.jsonl','budget_processes121.jsonl','fit_and_acquisition121.jsonl'),
'M8': put(
r'''Five fresh timing processes execute the fixed first 32 states in the same catalogue, and all 9,280 saved timing actions match the primary state and action identities. Among 140 matched MARGINAL/VALUE cohort clocks, MARGINAL is faster in 40 and slower in 100; including the measured allocated acquisition and audit bill changes these counts to 38 and 102. In the 64-state primary cohort it is faster in four of 28 complete-service comparisons. All five clocks, process loads, serialization, rejected proposals and fallback are retained, and the selected study-process ledger includes the independent policy validation. Nested timing processes are not added again to the enclosing primary clock.''',
r'''Five descriptive observations are not a runtime confidence interval or a claim about the machine-independent timing distribution. Allocated standalone deployment costs are calculated from measured components and are distinguished from directly observed whole processes. Repeats do not add independent economic states.''',
r'''Table~\ref{tab:fullcost121}, Table~\ref{tab:allclocks121}, and the selected research-stage cost rows.''',
'all_cohort_clocks121.jsonl','all_volume_costs121.jsonl','selected_research_stage_costs121.jsonl','all_timing_action_checks121.jsonl.gz'),
'M9': put(
r'''The independent fitting implementation has now executed on all 56 stored actors, checking exact feature and derivative assembly and finite primal/dual witnesses without calling the fitting solver. The separate original-primitive evaluator has completed all 1,301 distinct raw and delivered policy keys with 1,406,549 assertions. The fixed inference calculation and deterministic reporter also exited successfully. The reporter binds 473 input files, checks 220,310 record assertions and reproduces 49 stable output files without fitting, new states, original economic evaluations or timing reruns. The standalone source, dependency pins, immutable inputs and reproduction commands distinguish this bounded reporting check from a full scientific replay.''',
r'''A separate implementation is not external authorship, and the finite fitting certificate does not optimize hidden features or establish a global feature cover. Final source-specific CI and publication evidence are distinct from the already successful scientific stages and from the M/R transport workflows; they are identified by their own receipts without a future-success assertion inside this source.''',
r'''The independent fit/policy receipts, \nolinkurl{SOURCE_READY121.json}, \nolinkurl{EVIDENCE_MANIFEST121.json}, and the source-specific CI/publication records.''',
'independent_fit_audits121.jsonl.gz','fit_and_acquisition121.jsonl','selected_research_stage_costs121.jsonl'),
'M10': put(
r'''The principal narrative now follows one economic problem, the original-risk marginal acquisition and fitting construction, its action-path and stationarity theorems, and the completed 28-treatment economic test. Full proofs reside in the supplement; all policy, fitting, budget, timing and price tables and the research history have explicit development routes. The complete original advisory quotations and R120 treatments remain in this response and its machine map. Historical proof and code sources, including the original corrigenda and negative results, remain recoverable by commit and hash rather than being silently deleted to shorten the article.''',
r'''Final page counts are facts of the actual strict build, recorded in the retention and publication records. Structural reorganization does not close the unresolved contribution questions, and a historical syntax/index scan is not a new correctness proof.''',
r'''The main/supplement/development wrappers, \nolinkurl{CONTENT_RETENTION_MAP121.md}, \nolinkurl{SOURCE_READY121.json}, and the actual source/PDF publication records.''',
'policy_cells121.jsonl','loss_contrasts121.jsonl'),
'minor-1': put(
r'''The inherited $N^{-2}$ statement remains an error-versus-information bound under its deterministic scalar oracle convention. The new marginal construction displays its finite probe and label tolerances separately from fitted node error, feature-cover error and action regret. The actual budgets contain 325 and 1,053 original root-$Q$ contexts per risk, and the 28 coarse-to-fine sample comparisons include both positive and negative gains. These two budget observations are reported as executed information scaling, not evidence for an asymptotic exponent or a universal neural convergence rate.''',
r'''No rate for general Bellman information complexity, end-to-end time or economic gain is inferred from a function-class approximation rate or from the two executed budgets.''',
r'''Proposition~\ref{prop:marginalprobe121}, Theorem~\ref{thm:quotientlearning121}, and Table~\ref{tab:budgetscaling121}.''',
'budget_scaling121.jsonl','fit_and_acquisition121.jsonl'),
'minor-2': put(
r'''Every operative interpretation of the inherited lower bound retains the deterministic, point-value, univariate, fixed-$\alpha$ oracle restrictions and its function class. R121 supplies a constructive original-model acquisition interface and its actual paid queries, not a broader lower-bound proof. The direct original-formula online control is retained in all economic comparisons; excluding it on the basis of the narrow oracle theorem would give an unfair computational claim.''',
r'''Randomized, multivariate, nonuniform and formula-oracle lower bounds remain separate open statements. The actual original-model information bill does not itself establish minimax optimality.''',
r'''Theorem~\ref{thm:rootmarginal121}, Proposition~\ref{prop:marginalprobe121}, and the acquisition and complete-frontier rows.''',
'budget_processes121.jsonl','all_cost_frontiers121.jsonl.gz'),
'minor-3': put(
r'''The original-risk regularity and probe propositions retain explicit dependence on the tail probability and capacity constants, while the inherited fixed-tail lower bound keeps its own tail-dependent constant and function class. The executed comparison reports both $\alpha=1/2$ and $\alpha=3/4$ separately throughout the acquisition, regret, loss and cost tables; the 28 paired sample mean gains are negative across both risk levels. No data-dependent risk level has been chosen to improve the claim.''',
r'''The two fixed risk levels do not provide empirical evidence about the $\alpha\uparrow1$ limit. Opposite movements of constants from different bounds or function classes cannot be combined into a uniform sharp-rate claim without the corresponding assumptions and proof.''',
r'''Theorem~\ref{thm:rootmarginal121}, Proposition~\ref{prop:marginalprobe121}, and Table~\ref{tab:learninggains121}.''',
'loss_contrasts121.jsonl','fit_and_acquisition121.jsonl'),
'minor-4': put(
r'''The actual fitting problem fixes a coefficient box of 128 and 30-bit coefficient storage; its exact audit certifies this finite feasible class. All 28 MARGINAL primal/dual gap upper bounds are at most approximately $2.58\times10^{-8}$, and VALUE least-squares gaps are separately reported for the VALUE actors. The two acquired budgets change information and some feature counts, but the coefficient box is unchanged. We therefore report the restriction and its exact solved-problem gap without interpreting it as the best unrestricted approximation or as a coefficient-box sensitivity experiment.''',
r'''Sensitivity to the coefficient bound has not been executed in R121. Changing that bound, features or selection after seeing these outcomes would require a new declared experiment; the present two-budget comparison cannot answer the omitted box-sensitivity request.''',
r'''Proposition~\ref{prop:boxtraining121}, Table~\ref{tab:allfits121}, and Table~\ref{tab:budgetscaling121}.''',
'fit_and_acquisition121.jsonl','independent_fit_audits121.jsonl.gz','budget_scaling121.jsonl'),
'minor-5': put(
r'''The result tables distinguish finite-node marginal residual, finite-box optimization gap, production qualification, independently bounded original-policy regret and action-error upper bounds. The distinction has empirical content: all 28 node residuals decrease while all 28 original sample mean gains are negative. All 3,712 policies pass production qualification, yet that does not establish a better learned decision than VALUE or a neural adoption advantage. Production and independent interval overlap is described only as compatibility; it does not independently certify the narrower production endpoints.''',
r'''A node residual or fitting gap is not an off-design Bellman action gap. The proved feature-cover and KKT implications require their stated hypotheses; the fitted global cover was not numerically certified, and action-error upper bounds are not exact observed action errors.''',
r'''Theorem~\ref{thm:quotientlearning121}, Proposition~\ref{prop:marginalpolicy121}, Table~\ref{tab:learninggains121}, and Table~\ref{tab:allpolicies121}.''',
'loss_contrasts121.jsonl','policy_cells121.jsonl','fit_and_acquisition121.jsonl'),
'minor-6': put(
r'''Each of the 28 loss-contrast rows reports the node-residual change beside the first-rejection change and the independently bounded original gain. Although every node residual improves, rejection counts rise in 18 paired treatments, fall in two and are unchanged in eight; the aggregate is 294 MARGINAL rejections versus 60 VALUE rejections. All 354 rejected first proposals are kept, independently evaluated and charged together with fallback. The raw-proposal table and delivered-policy table distinguish a poor learned suggestion from the corrected policy ultimately returned.''',
r'''A smaller residual is not evidence of fewer rejections or safer raw actions. The 28 treatments reuse the same states and include identical-feature controls, so these counts are descriptive treatment totals rather than 28 independent draws.''',
r'''Table~\ref{tab:learninggains121}, Table~\ref{tab:rawproposals121}, and the complete qualification-attempt rows.''',
'loss_contrasts121.jsonl','policy_cells121.jsonl','all_qualification_attempts121.jsonl.gz'),
'minor-7': put(
r'''The acquisition ledger records the two actual processes and the component allocation used for deployment comparisons; it does not assign sampling coverage to the observed engineering costs. The five fresh service clocks are all reported, with 40 faster and 100 slower MARGINAL cohort comparisons, or 38 and 102 after the allocated acquisition and audit bill. Raw clock observations, complete enclosing processes and calculated reuse costs have separate fields. The independent original-policy validation cost remains visible in the research ledger.''',
r'''Observed minima, maxima, medians and component allocations are not runtime confidence intervals. The fixed 95\% family concerns economic state sampling, not runtime variation; timing repeats do not enlarge its sample.''',
r'''Table~\ref{tab:allclocks121}, Table~\ref{tab:fullcost121}, and the acquisition/research process records.''',
'all_cohort_clocks121.jsonl','budget_processes121.jsonl','selected_research_stage_costs121.jsonl'),
'minor-8': put(
r'''The original R97 zero certified adoption result over quadratic least squares and the exact R120 individual-clock qualifications remain explicitly preserved above. The completed R121 full-menu result is now stronger for its own declared scenarios: zero of 32 primary ReLU price cells, zero of 160 individual timing cells and zero of 32 all-five-clock intersections has a nonempty sufficient or upper not-ruled-out region. The predeclared full menu includes quadratic least squares and the other conventional alternatives at both budgets. Every pair constraint remains in the complete table, so the full-menu result is not silently relabeled as a separate pairwise claim against quadratic alone.''',
r'''An empty full-menu region does not logically imply that every pairwise comparison is impossible, and the older unresolved R120 individual-clock regions remain unchanged. These R121 finite-cohort, measured-cost conditions are not population adoption or a universal impossibility theorem.''',
r'''Table~\ref{tab:reluprices121} and every exact pair constraint, menu and all-five-clock intersection.''',
'all_price_constraints121.jsonl.gz','all_price_menus121.jsonl.gz','all_five_clock_price_intersections121.jsonl.gz'),
'minor-9': put(
r'''The certification account retains the verified approximation, Bellman/HJB residual, recursive-utility and safeguarded-policy connections with their original hypotheses and attribution. R121 adds a complete original-risk marginal construction through constrained tails, a paid interval-label interface, a finite fitting witness and an explicit nonsmooth feature-range transfer. The independently implemented finite audit and original-policy evaluator have both executed, while the global fitted-feature cover remains unexecuted. Classical concentration and binomial inversion ingredients do not become new neural theorems because they support the fixed R121 evidence.''',
r'''The preserved NDU/FBSDE, nonlinear preference, temporal-self and game links require their own well-posedness, filtration, boundary and equilibrium assumptions. The present two-date investment validation neither proves nor executes those different economic claims.''',
r'''The complete new proofs, retained correctness/bridge sources, Table~\ref{tab:allfits121}, and the independent original-policy receipts.''',
'independent_fit_audits121.jsonl.gz','policy_cells121.jsonl'),
'minor-10': put(
r'''Neural Bellman Operators remains the research identity: recursive continuation operators, their learned critics and feasible actors are studied under the original investment objective. The title and contribution distinguish the neural implementation from the representation-neutral theory. Current evidence is stated directly: the marginal objective is accurately solved at the finite nodes, yet every paired sample mean worsens, matched hinge actions equal ReLU, and no ReLU full-menu adoption region is obtained. These findings inform the next original-model algorithmic problem rather than redefining a shared hinge geometry as neural-specific success.''',
r'''The title does not assert an established neural-exclusive economic or information advantage. Achieving such an advantage with equal information, feasible policies and complete costs remains part of the continuing NBO and Econometrica objective.''',
r'''The revised main contribution statement, Table~\ref{tab:learninggains121}, and Table~\ref{tab:reluprices121}.''',
'loss_contrasts121.jsonl','equal_feature_control121.jsonl.gz','all_price_menus121.jsonl.gz')
}


def main():
    now = datetime.now(timezone.utc).isoformat()
    data = json.loads(MAP_PATH.read_text())
    body = BODY_PATH.read_text()
    retention = RETENTION_PATH.read_text()
    assert len(data['items']) == len(ITEMS) == 30
    assert set(ITEMS) == {x['comment_id'] for x in data['items']}
    assert all(x['r121_executed_outcome'] is None for x in data['items']), 'One-shot integration; refuse overwrite.'
    receipts = ['results121/independent-attempt01/EXECUTION121.json',
                'results121/stats-attempt01/EXECUTION121.json',
                'results121/report-attempt01/EXECUTION_REPORT121.json',
                'results121/training-audit5-attempt01/EXECUTION121.json',
                'results121/training-audit9-attempt01/EXECUTION121.json']
    for rel in receipts:
        row = json.loads((ROOT / rel).read_text())
        assert row['status'] == 'executed' and row['exit_code'] == 0, rel
    summary = json.loads((ROOT / 'results121/report-attempt01/SUMMARY_REPORT121.json').read_text())
    assert summary['signed_sample64_gain_groups']['strict-negative'] == 28
    assert summary['joint_population_gain_groups']['contains-zero'] == 28
    assert summary['marginal_finite_node_residual_lower_groups'] == 28
    assert summary['independent_checks']['executed_assertions'] == 1406549
    assert summary['first_rejections'] == 354
    contrasts = read_jsonl('loss_contrasts121.jsonl')
    policies = read_jsonl('policy_cells121.jsonl')
    assert len(contrasts) == 28 and len(policies) == 58
    assert all(Fraction(x['sample64_gain_upper']) < 0 for x in contrasts)
    byloss = {loss: sum(x['first_rejections'] for x in policies if x['loss'] == loss)
              for loss in ['value', 'marginal', 'online']}
    assert byloss == {'value': 60, 'marginal': 294, 'online': 0}
    assert sum(x['first_rejection_change'] > 0 for x in contrasts) == 18
    assert sum(x['first_rejection_change'] < 0 for x in contrasts) == 2
    assert sum(x['first_rejection_change'] == 0 for x in contrasts) == 8
    budget = read_jsonl('budget_scaling121.jsonl')
    assert [sum(x['original_gain_sign'] == s for x in budget)
            for s in ['strict-positive', 'strict-negative', 'contains-zero']] == [15, 12, 1]
    before_inherited = {x['key']: copy.deepcopy(x['inherited_r120_record_unchanged']) for x in data['items']}
    before_quotes = {x['key']: x['exact_inherited_quote_latex'] for x in data['items']}
    snapshot = ROOT / 'provenance121/lineage121/pre_complete_outcome_integration121'
    snapshot.mkdir(exist_ok=False)
    saved = []
    for p in [BODY_PATH, MAP_PATH, RETENTION_PATH]:
        out = snapshot / (p.name + '.gz')
        out.write_bytes(gzip.compress(p.read_bytes(), mtime=0))
        saved.append({'original': identify(p), 'preserved': identify(out)})
    (snapshot / 'INDEX121.json').write_text(json.dumps({'created_utc': now,
        'scope': 'Exact active drafts immediately before completed-outcome integration; no frozen science changed.',
        'files': saved}, indent=2) + '\n')
    stage_bindings = [identify(ROOT / rel) for rel in receipts]
    report_bindings = [identify(ROOT / ('results121/report-attempt01/' + name)) for name in
                       ['SUMMARY_REPORT121.json', 'EXECUTION_REPORT121.json', 'INPUTS_REPORT121.json',
                        'OUTPUT_MANIFEST121.json', 'TABLE_SCOPE121.md', 'RESEARCH_LEDGER121.json']]
    table_cache = {}
    for item in data['items']:
        spec = ITEMS[item['comment_id']]
        item['r121_pre_result_author_action_latex'] = item['r121_author_action_latex']
        item['r121_pre_result_remaining_requirement_latex'] = item['r121_remaining_requirement_latex']
        item['r121_pre_result_empirical_status'] = item['r121_empirical_status']
        item['r121_author_action_latex'] = spec['action_latex']
        item['r121_remaining_requirement_latex'] = spec['remaining_latex']
        item['r121_empirical_status'] = 'Completed actual R121 primary/timing, independent finite-fit and original-policy evaluation, fixed inference and deterministic reporting; no blanket scientific closure or future source-CI success asserted.'
        item['r121_numerical_route'] = 'new121/numerical121.tex'
        item['r121_executed_outcome'] = {
            'status': 'actual-completed-r121-evidence-integrated',
            'integrated_utc': now,
            'interpretation_latex': spec['action_latex'],
            'remaining_scientific_requirement_latex': spec['remaining_latex'],
            'printed_evidence_route_latex': spec['printed_route_latex'],
            'all_stage_receipts': stage_bindings,
            'table_bindings': [],
            'global_feature_cover_numerically_certified': False,
            'neural_exclusive_advantage_asserted': False,
            'population_positive_mean_learning_gain_asserted': False,
            'original_model_or_objective_changed': False,
            'historical_results_substituted_for_current_execution': False}
        for name in spec['table_paths']:
            if name not in table_cache:
                table_cache[name] = identify(TABLES / name)
            item['r121_executed_outcome']['table_bindings'].append(table_cache[name])
        item['closure_asserted'] = False
        marker = '\\label{response121:' + item['comment_id'] + '}'
        begin = body.index(marker)
        active = body.index('\\paragraph{R121 mathematical and algorithmic action.}', begin)
        candidates = [j for j in (body.find('\\subsection{', active), body.find('\\section{', active)) if j != -1]
        end = min(candidates) if candidates else len(body)
        replacement = ('\\paragraph{Completed R121 mathematical, algorithmic and empirical action.}\n'
                       + spec['action_latex'] + '\n\n'
                       + '\\paragraph{Remaining scientific requirement.}\n' + spec['remaining_latex'] + '\n\n'
                       + '\\paragraph{Current execution and source route.}\n' + spec['printed_route_latex'] + '\n'
                       + 'The item-specific exact table hashes and successful current-stage receipts are bound in '
                       + '\\nolinkurl{provenance121/R97_REQUIREMENTS121.json}. '
                       + 'These are completed R121 observations; the retained R120 evidence above has its own source and sample.\n\n')
        body = body[:active] + replacement + body[end:]
    intro_start = body.index('\\paragraph{Frozen numerical scope and current status.}')
    intro_end = body.index('\\section{Point-by-point response', intro_start)
    intro = r'''\paragraph{Frozen numerical scope and completed execution.}
The scientific source and protocols were published at F,
\nolinkurl{16bf21334efcbc719b83e2ccf10e8527f8b956f2}, before any new
original-model acquisition. Its native tree is
\nolinkurl{2666e47a9b5376904bf53ad187b97a850107fc30}; the exact manifest is
\nolinkurl{SOURCE_FREEZE121.json}. All 56 stored actors and both independent
finite-fitting audits were then published at M,
\nolinkurl{796c5f2badf68b051ac6c144884c0e61b87faf5e}, before held-out
entropy existed. D, \nolinkurl{68eae434c0e61fb1a61c3271c651c83c28619a07},
contains the later 640-byte draw and 64 exact states, published before policy
outcomes. The original continuous innovation law and economic objective are
unchanged. The current mathematical sources are
\nolinkurl{new121/marginal_main.tex} and
\nolinkurl{new121/marginal_proofs.tex}; the executed study follows
\nolinkurl{PROTOCOL121.md}, \nolinkurl{INDEPENDENT_PROTOCOL121.md} and
\nolinkurl{REPORTING_SPEC121.md}.

All 3,712 primary decisions and 9,280 decisions in five serial timing
processes completed; every saved timing action matches its primary identity.
The production records were published at R,
\nolinkurl{f6392f6909d280ecd310f152caab0fafe9091df7}, with 761 declared
native Git blobs checked by \nolinkurl{provenance121/R_PUBLICATION121.json}.
Independent original-policy evaluation subsequently completed all 1,301
distinct policy/proposal keys, 167,829 terminal contexts and 1,406,549
assertions. It covers all delivered policies and all first proposals,
including rejected ones. Independent evaluation started after the complete
production/timing campaign while local HEAD was D and before R transport;
it was not already running when D was originally published. The exact
receipt correction and its prior bytes are preserved in the provenance.

The fixed statistical calculation and the deterministic reporter have also
completed successfully. The reporter checks 473 bound inputs and 220,310
record assertions and reproduces 49 stable output files without new states,
fitting, original economic evaluations or repeated clocks. The executed
results are in \nolinkurl{new121/results121.tex} and
\nolinkurl{new121/development121_results.tex}; exact rows, ledgers and
successful stage receipts are under \nolinkurl{results121/}.

\paragraph{What the completed study establishes and leaves open.}
All 28 MARGINAL treatments lower the finite-node marginal residual, but
every independently enclosed 64-state sample mean gain
$J_{\rm VALUE}-J_{\rm MARGINAL}$ is strictly negative. All 28 fixed joint
population mean-gain intervals contain zero. Of 1,792 paired final actions,
889 differ. First rejections rise from 60 under VALUE to 294 under MARGINAL;
all 3,712 delivered policies are qualified, with zero numerical service
failures and zero exact fallbacks. Thus the safeguard works at its declared
tolerance while the proposed learning objective fails to improve the
original sample mean. Finite fitting was independently audited; the global
fitted-feature cover needed for the stronger off-design theorem was not
numerically certified.

MARGINAL complete primary cohort service is faster in four of 28 comparisons
and slower in 24. Across five timing processes it is faster in 40 of 140
matched cohorts and slower in 100; including the allocated acquisition and
required fit-audit bill gives 38 faster and 102 slower observations. Every
primary ReLU--hinge raw and final action pair agrees. All ReLU full-menu
sufficient and upper not-ruled-out price regions are empty in the 32 primary,
160 individual-clock and 32 all-five-clock comparisons. These are actual
R121 findings, with their original state and clock scopes. They neither
replace the distinct R120 evidence nor establish a population harm,
neural-exclusive advantage or universal adoption impossibility.

The 64 fresh states are the statistical units; repeated methods, risks,
hinges and clocks do not enlarge that sample. The study keeps its original
model and Econometrica objective. Source/PDF identity and source-specific
CI/publication are recorded separately in \nolinkurl{SOURCE_READY121.json},
\nolinkurl{EVIDENCE_MANIFEST121.json} and the subsequent actual publication
receipts. Successful scientific execution and an assembly workflow are not
substitutes for those distinct source-publication records.

'''
    body = body[:intro_start] + intro + body[intro_end:]
    body = body.replace('% R121 author response, source-frozen version awaiting policy outcomes.',
                        '% R121 author response integrating the complete independently evaluated study.')
    body = body.replace('% F, M, D and complete production R are published; independent policy verification and result integration remain pending.',
                        '% F, M, D and production R are published; independent evaluation, fixed inference and reporting completed.')
    body = body.replace('a mathematical subclaim are not blanket closure of the broader request.',
                        'a mathematical subclaim are not blanket closure of the broader request. The current executed observations are integrated item by item, including adverse and statistically unresolved findings.')
    data['scope'] = ('Completed R121 author response with all 30 item-specific actual results. Exact inherited report quotations and complete prior route records remain unchanged. Broader unresolved scientific requests are retained; no blanket closure, neural advantage, future CI success or historical-result substitution is asserted.')
    data['r121_empirical_outcomes_available'] = True
    data['r121_empirical_outcomes_integrated_utc'] = now
    data['r121_publication_stage'] = ('F, M, D and complete primary/timing R published; independent fitting and original-policy validation, fixed inference and deterministic reporting completed successfully. Source/PDF CI and publication have their own subsequent receipts.')
    data['source_binding_scope'] = ('The two mathematical sources remain exact F bytes. Completed independent/stats/report receipts and exact result-table identities are integrated separately; future source/PDF CI success is not asserted.')
    data['r121_current_completed_report_bindings'] = report_bindings
    data['r121_current_completed_stage_bindings'] = stage_bindings
    data['r121_result_integration_scope'] = {'editorial_only': True, 'new_states': 0,
        'training_calls': 0, 'economic_evaluations': 0, 'timing_reruns': 0,
        'protocol_or_frozen_source_mutations': 0, 'sample_selection_changes': 0,
        'all_30_items_integrated': True, 'pre_result_snapshot': str(snapshot.relative_to(ROOT)) + '/INDEX121.json'}
    for item in data['items']:
        assert item['inherited_r120_record_unchanged'] == before_inherited[item['key']]
        assert item['exact_inherited_quote_latex'] == before_quotes[item['key']]
        assert item['exact_inherited_quote_latex'] in body
    assert 'The current R121 outcome is pending' not in body
    assert body.count('\\paragraph{Completed R121 mathematical, algorithmic and empirical action.}') == 30
    # Preserve historical stage descriptions as dated history, then record the actual completed status.
    retention = retention.replace('Integration of policy outcomes and their independent validation remains pending.',
        'Actual acquisition, independent finite-fitting audit, primary/timing campaign, independent original-policy evaluation, fixed inference and reporting have completed. The global fitted-feature cover remains unexecuted.')
    retention = retention.replace('policy outcomes and their independent validation are still pending at this update.',
        'those policy outcomes and their independent validation were pending at that source-freeze update and are now complete, as recorded below.')
    retention = retention.replace('while retaining all economic outcome and closure fields pending.',
        'while retaining economic outcome fields pending at that dated stage and keeping blanket closure unasserted. The subsequent complete-outcome integration below updates the active outcomes without rewriting that prior receipt.')
    retention = retention.replace('Independent economic evaluation, fixed statistical inference and author interpretation remain pending.',
        'Independent economic evaluation and fixed statistical inference were still running or pending at that dated production-stage update; both have subsequently completed and their actual outcomes are integrated below.')
    completed = '''
## Completed R121 outcomes and pointwise author integration

The independent original-policy evaluator, fixed statistical calculation and deterministic reporter have **actually exited 0**. Their exact identities are bound in provenance121/lineage121/COMPLETED_RESPONSE_INTEGRATION121.json and in every relevant current item of provenance121/R97_REQUIREMENTS121.json. All 30 original quotations and all complete inherited R120 records remain unchanged. Each current item now gives its own actual evidence, mathematical route and continuing requirement; closure_asserted remains false. The earlier prospective and production-stage drafts remain preserved, including their historical pending statements, under initial_author_response121, pre_result_author_response121 and pre_complete_outcome_integration121.

| Current R121 observation | Actual completed evidence | Scientific interpretation |
|---|---|---|
| 56 stored actors; 48 actual optimizer fits and eight paid equal-feature hinge copies | Both exact finite-fit audits; 771,005 assertions; full model, design and label identities | A finite fixed-feature, box-constrained fitting certificate; no global hidden-feature optimum or global off-design cover is claimed. |
| 650 and 2,106 original root-Q contexts across two risks at budgets 5 and 9; 1,413,828 terminal label contexts | fit_and_acquisition121.jsonl and both acquisition-process receipts | Paid integrated-risk label acquisition; identical complete information within VALUE/MARGINAL pairs. |
| 3,712 primary decisions, 9,280 timing decisions, 1,301 independent policy/proposal keys, 167,829 terminal contexts, 1,406,549 independent assertions | Complete production, independent and timing identity records | All delivered and first-proposed original policies, including rejected proposals, are retained and independently evaluated. |
| Marginal node residual lower in 28/28 comparisons; independently enclosed sample mean J_VALUE minus J_MARGINAL negative in 28/28; 889/1,792 paired final actions differ | loss_contrasts121.jsonl and policy_cells121.jsonl | Better finite-node fitting did not improve the original sample mean; global action-path premises were not numerically certified. |
| All 28 joint population gain intervals contain zero | Fixed two-optimum, 58-regret, 28-gain, 112-event and 116-rejection-endpoint inference family | At least 95% joint coverage under the stated frozen-actor, ideal-entropy assumptions; 64 states are the units, not methods or clocks. Population gain and harm remain unresolved. |
| First rejections VALUE 60, MARGINAL 294; all 354 kept and charged; 3,712 delivered policies qualified; zero numerical service failures and exact fallbacks | All 4,066 qualification attempts and raw/delivered policy tables | The production safeguard met its fixed requirements; that is distinct from a successful learning mechanism. |
| MARGINAL complete primary cohort faster 4/28, slower 24/28; repeated cohort faster 40/140, slower 100/140; full allocated repeated cost faster 38/140, slower 102/140 | Every saved clock, full-volume cost row and selected research-stage ledger | Costs include labels, fitting, required audits, rejection/fallback and complete service; allocated costs and actual process clocks remain distinct. No runtime confidence interval is claimed. |
| ReLU and hinge have 512 identical primary raw and delivered action pairs | equal_feature_control121.jsonl.gz | Identical shared features and coefficients produce identical decisions with the full learned-feature bill charged to hinge. No exclusive neural geometry advantage is inferred. |
| All ReLU full-menu sufficient and upper not-ruled-out sets empty: primary 32, individual timing 160, all-five-clock intersections 32 | All exact pair constraints, menus and intersections | Current finite-cohort, recorded-cost conditions; unlike R120, the individual current upper sets are also empty. The historical R120 unresolved cells remain unchanged. |
| Two-budget original sample mean gains: 15 strictly positive, 12 strictly negative, one contains zero | budget_scaling121.jsonl | Genuine acquired-information scaling, with no added population family, dimension/horizon scaling, coefficient-box sensitivity or asymptotic rate claim. |
| Reporter binds 473 inputs, checks 220,310 assertions and reproduces 49 stable output files | EXECUTION_REPORT121.json, INPUTS_REPORT121.json and OUTPUT_MANIFEST121.json | Deterministic reporting verification, with zero new economic evaluations, states, fits or clocks; not a full scientific rerun. |

The complete evidence remains in results121/report-attempt01, including every unfavorable row. The new action-path, constrained-stationarity, original-risk regularity, outward-probe and finite-readout proofs are in the frozen mathematical sources. The fitted **global feature cover has not been numerically certified**. The current experiment therefore does not establish an equal-information neural advantage, a positive population learning gain, a cost-optimal adaptive stopping rule, or a consequential externally calibrated application. These are continuing scientific requirements inside the original NBO and Econometrica program, not grounds for replacing the economic objective or counting adverse evidence as completion of the original ambition.

SOURCE_READY121.json, EVIDENCE_MANIFEST121.json and later source-specific CI/publication receipts identify final source/PDF/package validation without a self-referential promise of future success. Actual final document page counts can be added to this retention record after the strict build. The dated historical structural registry remains distinct from the final-source index and from mathematical proof validation.
'''
    retention += completed
    BODY_PATH.write_text(body)
    MAP_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    RETENTION_PATH.write_text(retention)
    item_payload_path = ROOT / 'provenance121/lineage121/COMPLETED_RESPONSE_ITEM_TEXT121.json'
    item_payload_path.write_text(json.dumps({'created_utc': now, 'scope': 'Completed-evidence editorial integration, with no scientific or protocol changes.', 'items': ITEMS}, indent=2, ensure_ascii=False) + '\n')
    receipt = {'schema': 'nbo.r121.completed-author-response-integration.v1',
        'created_utc': now, 'status': 'completed', 'items': 30,
        'exact_original_quotes_unchanged': 30, 'complete_inherited_r120_records_unchanged': 30,
        'stage_receipts': stage_bindings, 'report_files': report_bindings,
        'actual_table_files_used': list(table_cache.values()),
        'first_rejections_by_loss': byloss,
        'pre_integration_snapshot': identify(snapshot / 'INDEX121.json'),
        'item_text': identify(item_payload_path),
        'outputs': [identify(BODY_PATH), identify(MAP_PATH), identify(RETENTION_PATH)],
        'editorial_source': identify(Path(__file__)),
        'new_scientific_execution': False, 'new_protocol_or_sample_selection': False,
        'blanket_closure_asserted': False, 'future_ci_success_asserted': False,
        'global_feature_cover_numerically_certified': False,
        'historical_registry_reexecuted': False}
    out = ROOT / 'provenance121/lineage121/COMPLETED_RESPONSE_INTEGRATION121.json'
    out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'status': 'completed', 'items': 30, 'outputs': receipt['outputs'], 'receipt': identify(out)}, indent=2))


if __name__ == '__main__':
    main()
