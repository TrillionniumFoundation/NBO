# Advisory Referee Report: Neural Bellman Operators

**Recommendation: Reject in its present form.**  
**Date:** 18 September 2026.  
**Standard:** Substantive Econometrica-style assessment.  
**Reviewed snapshot:** `30548ad06852cc0a447dedf1e63cc9e7f79f6c06`.  
**Latest complete scientific revision:** R9, `8c1e0472279fb66a2419b63b3e35df028ecfdd78`.  
**Status:** Owner-commissioned advisory review, not an appointment, report, or editorial decision issued by Econometrica.

## 1. Assessment for the editor

The strongest part of this paper is a specific computational argument: signed compression of transition-law upper information, its comparison with a count-informed relaxation, and the combination with feasible-policy polynomials to certify regional economic decisions. Several earlier weaknesses have been repaired. The positive-duration initial decision, declared finite settlement economy, cardinal preference primitive, and distinctions between stored-array arithmetic and other targets now prevent criticisms that were applicable to earlier drafts. The participation and statewise-enforcement results are coherent under their stated assumptions. Adverse surrender, settlement, and permission experiments have not been hidden.

Nevertheless, the paper has not established a sufficiently integrated economic contribution to warrant publication in its present form. A certificate of an agent's ranking under an imposed mandate is not a certificate of the mandate a service-procuring principal would choose. This distinction is substantive in the paper's own numerical economy, not merely a request for a more general model. My new calculations show that, when the principal can offer sign-restricted mandates with class-specific participation grants, the positive class is preferred in both adjustment regimes at all nine original test contracts with the implementing fee. At these points this remains true throughout the service-price range in which either no-adjustment class is financially feasible. The certified opposite agent rankings therefore do not, by themselves, establish opposite procurement choices.

A second issue is the link between the two-stage primitive mechanism and the full dynamic calculation. The new audit narrows rather than inflates this concern. At the central financially enforced contract, upward-only adjustment reproduces unrestricted values on the entire all-action reachable support, not just at the initial state. Downward-only adjustment likewise reproduces no-adjustment values there. Preference-boundary discharge is impossible from the commissioned state within the eight-date horizon. Consequently, neither distant-state counterexamples nor an appeal to preference-boundary exits explains the focal calculation. A positive dynamic explanation remains necessary on the relevant domain.

These are objections about the content and significance of the economic argument. I do **not** identify a newly falsified theorem among the R9 participation, statewise-fee, or initial-breakpoint propositions examined here. Nor do I require an economics paper to prove neural methods indispensable, solve every possible contracting problem, or transfer a declared finite economy to a diffusion. The missing advance is a well-defined economic object, a mechanism that predicts it, and a certificate for that same object. Another version label or another table of conditional envelopes is not that advance.

## 2. Which revision has actually been reviewed?

The latest named branch inspected, `revision/econometrica-r11-integrated-mechanism-2026-09-18`, points to `30548ad...`, the preceding advisory-review commit. Its revision index still identifies R9 as the current complete manuscript. The R10 full-response branch similarly points to a review snapshot, not to completed new science. There is no completed R10 or R11 paper in this snapshot. This report reviews the inherited R9 science; the version-status observation is not counted as a mathematical defect. [V1–V3]

The source archive was obtained through GitHub Actions run `35222706049`, artifact `10497729014`, produced at `755b507870b54a100616b0658eba9a031eef2833`. Its SHA-256 matches the artifact metadata. The GitHub comparison from that commit to the reviewed snapshot contains seven commits and fourteen added files, all in two review directories. No manuscript, scientific constructor, or scientific result differs. Thus the archive is an adequate pinned source for this audit, but the successful source-packaging job is not evidence that R10 was completed. [V4]

The deposited main paper has 66 pages and the supplement 39. I inspected the relevant operator, error-analysis, transition-law, economic, contracting, and proof sources, and directly rendered main pages 56 and 58 and supplement page 37 to check the procurement, enforcement, and arithmetic tables and qualifications. Historical extensions were inspected selectively; this is not a claim to have independently reproved every extension or rerun historical neural training. The new experiments and their limits are specified below.

## 3. Results that should receive credit

The corrected chord is not the uncorrected interpolation of endpoint values. Its signed kernel–continuation correction provides an upper value under the stated affine-law and monotonicity assumptions. Fixed-policy Bernstein representations supply lower values without granting the deployed policy advance knowledge of future shocks. Count-informed upper values and the compressed chord have distinct information and storage requirements. A quadratic correction term is not presented as a quadratic bound on the total policy-bank error. The manuscript's finite-horizon error account also separates evaluation, improvement, boundary, and transition errors. [M1]

The R8 correspondence explicitly relates the problem to date-augmented reward MDPs and parameter lifting, and disclaims priority for regional expected-reward control or policy reuse themselves. The common-target comparison charges shared construction, anchor, policy-evaluation, and replay work. The mesh-only lower bank and the unfavorable reusable quadratic-program comparison remain visible. These repairs should not be erased by repeating an earlier claim that only favorable neural comparisons are shown. [M2, M3]

The economic qualifications also matter. Both position classes can bear risk; no-adjustment preferences remain stochastic; the initial restriction lasts a positive interval; and a change in state-dependent cardinal normalization changes preferences rather than merely notation. Signing grants and fees use a separate additive numeraire, not managed CRRA wealth. The statewise enforcement threshold is only sufficient for equality of initial values, while the continuous risky-share search enlarges only the first-date financial control conditional on finite consumption–adjustment pairs. These are meaningful restrictions, not hidden contradictions. [M4–M6]

## 4. Major concern P1: the certified agent decision is not the procurement decision

### 4.1 An elementary distinction with a material numerical consequence

R9 gives an agent the grant

\[
q_r^*=[G(x_0)-\max_\sigma W^r_\sigma+C(E)]_+
\]

and lets that agent choose a position class. The principal then receives `b A - q`. This is a valid acceptance calculation for the specified mandate. It does not establish which mandate is selected when the principal has additional contracting instruments. The paper expressly disclaims global optimal-contract design; my objection is therefore not that this displayed proposition is false. It is that the procurement interpretation has not yet supplied an economic reason to select the agent-ranking experiment as its central decision object. [M5, lines 7–39; M6]

Consider the limited extension in which the principal may offer either initial sign mandate and its corresponding grant. Retain the same within-class agent optimization, settlement, fee recipient, outside payoff, capacity technology, and policy selection. No consumption-contingent transfer or unrestricted mechanism is introduced. Define

\[
q^r_\sigma=[G(x_0)-W^r_\sigma+C(E)]_+,
\qquad \Pi^r_\sigma(b)=b\mathcal A^r_\sigma-q^r_\sigma.
\]

When both class participation constraints bind,

\[
\Pi^r_+(b)-\Pi^r_-(b)
=\Delta^r+b(\mathcal A^r_+-\mathcal A^r_-).
\tag{P1}
\]

This follows simply by subtracting the two binding grants. At a policy tie it requires the specified agent-policy selection, just as the author's procurement proposition does. Without binding participation, the positive-part formula must be retained. Crucially, `b` is the principal's service valuation, not the operating-benefit parameter `d` in the agent's Bellman reward.

Equation (P1) is not proposed as a novel theorem. It identifies the additional term a procurement decision certificate would have to control. An agent-value difference alone omits the service the principal is buying.

### 4.2 Fresh full-model reoptimization

I reoptimized all four class–regime values at the nine contracts

\[
\lambda\in\{0,0.125,0.25\},\qquad d\in\{0.4,0.425,0.45\},
\]

with `m=1`, `F=E=0.85`, and `C(E)=0.01`. Every original operating action and frozen feasible proposal remains available. The agent's actions are optimized before the principal's payoffs are calculated. At the center, the results are:

| Regime | Agent difference Delta | Duration difference A+ − A− | Principal difference at b=1 |
|---|---:|---:|---:|
| Adjustment | +0.000196740684027 | +0.002303043895612 | +0.002499784579639 |
| No adjustment | −0.000209326961178 | +0.002335340407378 | +0.002126013446200 |

The adjusted positive/nonpositive grants are `0.791344080902` and `0.791540821586`; the unadjusted grants are `0.826801403844` and `0.826592076882`. At `b=1`, principal surplus is respectively `0.098889195254`, `0.096389410675`, `0.063431872312`, and `0.061305858866`. All four offers therefore satisfy both parties' participation requirements at their minimum grants. The principal prefers the positive mandate in both regimes even though the unadjusted agent prefers the nonpositive class under a common grant. [E1]

The result is not dependent on an isolated choice of `b=1`. At the center the unadjusted principal's ranking switches at approximately `b=0.089634453511`, whereas the positive and nonpositive contracts break even only at approximately `0.928746909365` and `0.930953934683`. Across the nine points, the ranking switch lies between `0.023013565224` and `0.153472966905`; positive-contract break-even lies between `0.903733944358` and `0.953760142341`, and is lower than nonpositive-contract break-even at every point. Thus, at each tested point, every service price at which either unadjusted class is feasible already favors the positive class within this two-mandate menu. This is a pointwise finite-model observation with an elementary price extrapolation, not a certificate over the law–benefit rectangle. [E1]

At `b=1`, the smallest principal surplus over all 36 class-specific offers in the nine-point experiment is approximately `0.039052691839`. Both regimes favor the positive mandate at all nine points. The service-price example in the main paper instead uses `b=0.90`, at which the central adjusted mandate is acceptable but the unadjusted mandate is not. I reproduce that distinction; the manuscript itself states it. One should not describe that example as simultaneous implementation of two accepted procurement regimes with opposite choices. [M7, main p. 56; E1]

### 4.3 Surrender makes the procurement distinction sharper, not redundant

I also reoptimized the central contract at `F=0.80`, retaining capacity `E=0.85` and its cost `0.01`. This keeps the financing convention fixed while changing the surrender charge. In the no-adjustment positive class, duration falls from `0.890233276156` to `0.832928787647`, while the nonpositive duration remains `0.887897935749`. The discounted elective-surrender incidence of the positive class is `0.068995145990`; it is not an undiscounted probability. [E1]

At that center, the no-adjustment agent difference remains negative, `−0.000191857347061`, but the principal difference at `b=1` becomes much more negative, `−0.055161005448310`. Both sign offers remain feasible there. Thus the two-mandate principal now selects opposite signs across adjustment regimes. At the adverse corner `(lambda,d)=(0,0.4)`, the unadjusted agent difference is positive, `+0.001392379630300`, whereas the principal difference is `−0.069128748769681`; the positive offer has negative principal surplus and the nonpositive offer has positive surplus. [E1]

This is not a claim that the low-fee contract is optimal among fees or that it supplies a new favorable continuum region. It demonstrates why a procurement theorem needs service and participation as well as agent values. Active surrender changes precisely the service term that the current agent-sign certificate does not control.

**Required response P1.** State whether the decision maker is an agent receiving an imposed grant, a principal choosing among restricted mandates, or both in a specified sequence. Explain which sign, permission, fee, and term instruments are contractible and why. For the intended institutional menu, identify and certify the relevant payoff comparison. A genuinely exogenous mandate is legitimate, but then procurement is a conditional implementation interpretation, not an explanation of why that mandate is chosen. No unrestricted mechanism-design theorem is required; consistency between the economic decision and the certificate is required.

## 5. Major concern P2: a dynamic mechanism on the relevant support remains missing

The primitive family in the paper has adjustment cost in `[20,80]` and opposite preference-index incentives across the two consumption exposures. Its positive class benefits from reducing the preference index. The full dynamic economy instead has cost `2`, endogenous consumption and exit, stochastic preferences, and positive initial adjustment in both classes. The text explicitly says that the dynamic direction is not mechanically inherited. This acknowledgment avoids a false inference, but does not itself provide the positive explanation. [M4, lines 43–97]

For the central `F=0.85,m=1` contract, my new all-date restrictions reproduce the familiar initial comparisons: upward-only adjustment has exactly the same stored-arithmetic initial values as unrestricted adjustment; downward-only adjustment has the same initial values as no adjustment. More importantly, I constructed the support reachable under **any** original action and either endpoint shock law, not merely under an optimizing policy. The same equalities hold, to the recorded binary64 precision, at every state–date on that support. The largest recorded difference is zero for both comparisons and both initial classes. [E2]

They do not hold on the whole grid. The largest full-minus-upward gap over all states and dates is approximately `0.299093534370`, and the largest downward-minus-zero gap is approximately `0.301089004306`. These figures concern the financially enforced contract in this audit. They should not be confused with the larger distant-state witnesses in the previous noncancellable audit. Off-support behavior can refute an all-grid universal claim; it cannot by itself explain the commissioned initial-state result. [E2; H1]

There is also a simple support calculation. On the original preference grid the spacing is `0.05`. At any live grid state the proposed preference increment satisfies

\[
|\delta u|\leq 0.2/8+0.05/\sqrt8
=0.04267766953\ldots <0.05.
\]

The two-point settlement therefore moves at most one preference-grid step per date. Induction gives

\[
u_n\in[2-0.05n,\,2+0.05n].
\tag{P2}
\]

At maturity this is `[1.6,2.4]`, strictly inside the preference domain `[1.2,2.8]`. A forced exit occurring partway through an interval does not enlarge the proposed preference increment. Hence preference-boundary discharge cannot occur from the commissioned state under the original action box within this horizon. The constructed support confirms these endpoints and contains respectively `1,30,100,203,342,495,637,735,833` nodes at dates zero through eight, with no preference-boundary node. The analytic bound concerns the declared finite protocol, not a diffusion. Wealth-boundary discharge remains possible. [M4, lines 7–16; E2]

This strengthens the case for a focused dynamic result. One need not prove that upward adjustment suffices at every irrelevant state. One needs to explain its incentive on the economically relevant support and why its value is greater in one position class. At consumption `c=0.8`, for example,

\[
\partial_u\frac{c^{1-u}}{1-u}
=\frac{c^{1-u}\{1+(u-1)\log c\}}{(u-1)^2}>0
\]

throughout the model's preference domain. The minimum bracket is approximately `0.598341607634`. Thus upward movement can directly improve future cardinal flow utility at that consumption. This is a diagnostic of the explicit primitive, not a proof of the optimal drift, the full continuation derivative, or the class-option difference. Wealth transitions, wealth liquidation, consumption changes, and covariance still have to be accounted for.

The affine feature-envelope identities organize a reoptimization experiment, but a difference of four nonnegative reoptimization gains has no predetermined sign. The paper already acknowledges this. Reporting the same sign in the two-stage example and the full model does not close the gap between them. [M4, lines 69–97]

**Required response P2.** Supply a dynamic proposition or verifiable sufficient conditions on a declared relevant domain, connecting preference incentives, continuation values, and the class differential. Use the support restriction rather than appealing to impossible preference-boundary exits. Preserve the primitive theorem and the adverse cases, but do not let the primitive theorem stand in for the dynamic result. A computer-assisted domain certificate is acceptable; point equality alone is not a primitive explanation or a continuum proof.

## 6. Major concern P3: implementation, instrument choice, and an active exit option remain separate

The statewise fee threshold is a useful implementation result. Its proof compares `G-F` with noncancellable continuation and uses backward induction on a closed reachable support. Menu inclusion makes adjustment weakly reduce the required threshold. Nothing in my checks invalidates that logic. [M5; M6]

The deposited sufficient regional threshold is `0.8348592805606002`. The successful fee interval `[0.85,0.90]` exceeds it. Conditional on that stated bound and its arithmetic account, surrender is strictly inferior at every eligible reachable interior node of the original target. The successful three-dimensional box implements the earlier noncancellable economy; it is not a box in which exercised surrender explains the reversal. This is substantive implementability, but not evidence of an active exit mechanism. The manuscript discloses the adverse fee-0.80 corner, and my fresh computation reproduces it. [M7, main p. 58; E1]

There is a separate instrument-choice issue. The hard term `m=8` already gives noncancellable operation independently of the fee. When it is available without its own enforcement cost and `C(0)=0`, compare it with the financially enforced `m=1,F=E=0.85,C(E)=0.01` contract. The new center computations give the same four operating values and durations, while the hard-term grants are lower by exactly `0.01`; principal surplus is higher by exactly `0.01`. This is the numerical counterpart of the binding-participation subtraction, not a new numerical mystery. [M5, lines 9–13; E1]

The dominance is conditional on the hard term being selectable and costless beyond the specified primitives. It does not make an exogenously fixed minimum term inconsistent. But a comparison that prices capacity while leaving an equally available hard commitment unpriced cannot establish selection of financial enforcement. A term constraint, term-enforcement technology, or cost can be legitimate; it needs economic content and common treatment with the capacity instrument.

Initial permissions are another distinct margin. R9 shows binding long and short limits, exact first-date piecewise-affine optimization, and two regime-specific boundaries. The preceding review combines these permissions with stopping continuations: at the center with `F=0.85`, increasing the long permission from `0.80` to `0.82` makes both agent differences positive, whereas increasing the short permission from `0.50` to `0.51` makes both negative. I inspected these results and the manuscript's qualifications; I did **not** rerun the continuous-permission search in the present audit. The changes enlarge the target, and the author explicitly excludes automatic coverage by the original fee certificate. They are not counterexamples to that certificate. [M5, permission and certification subsections; M7; H1]

**Required response P3.** Keep three claims distinct: a finite charge implements a fixed mandate; exercised surrender alters incentives and service; and an institution chooses between feasible instruments. Develop the intended one into a substantive result under common primitives. For a contracting-choice interpretation, explain why the hard-term alternative is not trivially preferred and how permission choice is restricted. Another favorable fee interval with an inactive surrender option would not resolve these questions.

## 7. The computational contribution: potentially useful, but not a substitute for the missing economics

The methodological claim is narrower and more credible than the title alone suggests. Its merit should be assessed as a particular compression, information ordering, total-error analysis, and measured regional decision application. It should not be judged as though it still claims to invent policy iteration or all parametric reward verification. The explicit correspondence and adverse structural benchmarks are strengths. [M1–M3]

The remaining concern is the breadth and economic leverage of that incremental result. The successful sign application uses eight dates, a low-dimensional grid, finite consumption–adjustment pairs, affine scalar transition mixtures, and a deliberately specified settlement protocol. These restrictions are legitimate, but the paper must explain when the sharper count information or compressed correction enables an economically material decision that less expensive alternatives do not resolve. Generic performance superiority, neural necessity, or scalability to arbitrary high-dimensional control does not follow. The proper exit is a transparent domain-of-use argument and a same-target comparison on the final economic estimand, not another unrelated demonstration.

The external literature check reinforces the need for precise scope, not a claim of duplication. Heck et al. (2025) study dependency-sensitive lifting for parametric Markov **chains**, not the same controlled reward problem. Chatterjee et al. (2025) develop fixed-point certificates for MDP reachability and expected rewards and independently checkable implementations. These are relevant comparisons for dependency handling and certificate checking, respectively; neither paper's published experiments establish a performance ranking against NBO. R9 already discusses the former line of work. The latter helps clarify what independent checking means. A proof-assistant formalization is not a publication requirement here. [L1, L2]

The R9 arithmetic account is expressly for stored arrays. Its derived per-class allowance is about `1.43e-8`, below its adopted `1e-7`, and class differences include both allowances. It separately prices reward, kernel-row, and terminal errors needed for another target. My direct replay agrees to approximately `1.33e-15`, but both implementations still share the underlying transition formula. That agreement is not an independent outward-rounded enclosure of the constructor. It neither proves a diffusion transfer nor reveals a contradiction in an author who explicitly does not claim such a transfer. [M6, supplement p. 37; E2]

## 8. Disposition of the preceding review

| Previous concern | Present disposition |
|---|---|
| Primitive versus dynamic direction | Still substantive; new reachable-support analysis narrows the appropriate domain and rules out preference-boundary discharge as a focal explanation. |
| Financial enforcement versus compulsory term | Still conditional but material for instrument selection; fresh hard-term comparison reproduces equal operation and the capacity-cost difference. |
| Active surrender and permission dependence | Author disclosures credited; active-fee cases freshly reproduced, continuous-permission cases inspected rather than relabeled as new runs. |
| Need for an integrated economic decision | Strengthened by the new agent-versus-principal comparison; the relevant procurement contrast contains delivered service, not just agent value. |

There has been no new scientific revision since these earlier reports in the inspected snapshot. A new review should not pretend that absent R10/R11 material has answered them, nor manufacture an algebraic failure simply to make the recommendation harsher. [V1–V4; H1]

## 9. What would constitute a substantive response?

First, specify an economic decision and an institutional menu that make the computational estimand the object someone actually chooses. Either develop the fixed-mandate agent economy as such, with a compelling economic question, or analyze a constrained procurement sequence with both service and participation. Preserve, rather than hide, the adverse sign-mandate comparisons above.

Second, establish a dynamic mechanism on an explicit relevant domain. The evidence now points toward a reachable-support upward-adjustment result and away from preference-boundary explanations at the commissioned initial state. State assumptions that predict the class differential, and distinguish sufficient conditions from numerical domain verification. The two-stage result and the dynamic feature identities should support, not replace, this argument.

Third, attach the certificate to that same economic result. For a principal comparison, feasible-policy evidence must account for service as well as value, with policy selection and any discontinuities treated explicitly. For an active-surrender claim, show a meaningful domain where that option is exercised; for an instrument-selection claim, account for hard-term enforcement and capacity consistently. Maintain the original adverse contracts and the clear distinction between finite, stored-array, and other targets.

Finally, organize the main paper around the incremental theorem and its economic consequence. The substantial historical material can remain accessible without requiring the reader to reconstruct the contribution from successive layers of revisions. None of these requirements is a request to delete unfavorable content or to weaken a valid mathematical claim. They are requirements to establish what the paper's central claim means.

## 10. Execution record and limits

The final `reviewer_audit.py` was run afresh without checkpoints. It uses an independently written Bellman orchestration, action/sign/stop masks, and selected-control feature recursion. It retains the author's pinned reward/transition construction and frozen proposals. Direct selected-control replay reconstructs the four shocks, within-period annuity, liquidation, and interpolation without using the stored CSR reward/kernel backup. The original author `Contract.pair` is called only for final central parity validation, not to produce the audit values. [E1, E2]

Twelve contract specifications were solved in two regimes, yielding 48 initial class values. Two additional directional restrictions at the central enforced contract yield four more, for 52 in total. Every selected value function was replayed over all grid states and all dates. The maximum absolute value discrepancy is `1.3322676295501878e-15`; central production parity has maximum discrepancy zero. Thirteen pinned source/entry/proposal files have identical hashes before and after execution. The CSV contains all 26 paired cases, not a favorable selection. Diagnostics retain support counts, off-support directional gaps, versions, source identities, and limitations.

The nine original contracts are point checks, not a new regional certificate. The full author fee/chord/count sweep, historical neural training, continuous-permission roots, and diffusion approximation were not rerun. No timing contest is attached to the execution time. The kernel-storage count is `775469952` bytes; it is not peak process memory. The selected-policy replay uses the same primitive transition function, so its independence is explicitly limited. A failed unauthenticated clone attempt preceded the successful connector artifact download; no evidence is attributed to that failed attempt.

**Final recommendation:** reject the present manuscript. The valid computational and conditional-contract results should be retained. The next scientific revision needs an integrated economic argument, not a nominal increment in revision number.

## Source register

All manuscript/code paths below refer to the immutable reviewed snapshot `30548ad06852cc0a447dedf1e63cc9e7f79f6c06`; the scientific files are unchanged from the complete R9 commit. Equation/proposition labels are more stable than page numbering.

**V1.** GitHub branch collection inspected on 18 September 2026; latest named R11 and previous review both point to `30548ad...`.  
**V2.** `REVISION_INDEX.md`, opening R9 section; `ECTA_R9.tex`; `SUPP_R9.tex`.  
**V3.** Commit `30548ad...`, message `review: add reading order and clean reproduction instructions`.  
**V4.** GitHub comparison `755b507...30548ad`; Actions run `35222706049`, artifact `10497729014`; archive identities in `review_manifest.json`.

**M1.** `revisions/2026-09-16-r6/paper/02_operators.tex`, `03_approximation.tex`, `04c_kernel_transfer.tex`; `revisions/2026-09-17-r8-full-response/paper/04e_comparative_oracles.tex`; `revisions/2026-09-16-r7/paper/S10_comparison_proofs.tex`.  
**M2.** `revisions/2026-09-17-r8-full-response/paper/04h_literature_correspondence.tex`, lines 1–23.  
**M3.** R9 `paper/01_introduction.tex`, `paper/05d_decision_evidence.tex`; inherited R6/R7 computation and evidence sections included by `ECTA_R9.tex`.  
**M4.** `revisions/2026-09-17-r8-full-response/paper/04g_decision_economics.tex`, especially lines 7–16, 43–97, 100–109; `04_preferences.tex`; `04d_risk_frontier.tex`; `S12_full_response.tex`.  
**M5.** `revisions/2026-09-17-r9-participation-permissions/paper/04i_contracting.tex`: `prop:r9_participation`, `prop:r9_enforcement`, `prop:r9_knots`, and `subsec:r9_certificate`.  
**M6.** R9 `paper/S13_contract_proofs.tex`, especially lines 20–35 and subsection S.13.5; supplement pp. 33–39.  
**M7.** R9 `paper/05e_contract_evidence.tex`, `table_r9_procurement.tex`, `table_r9_surrender.tex`, `table_r9_enforcement.tex`, `table_r9_fee_certificate.tex`, `table_r9_permissions.tex`; main pp. 56–59; `response_to_referee.md`. The deposited regional results, not new full-sweep executions, support the regional assertions discussed above.

**H1.** `reviews/2026-09-18-econometrica-r9-r10-independent-harsh/referee_report.md`, sections 4–6, and its `reviewer_results.json`; preserved prior review, not relabeled as current execution.

**E1.** This directory's `reviewer_results.csv`: all fresh class values, durations, discounted surrender incidence, participation grants, and principal comparisons.  
**E2.** This directory's `reviewer_audit.py`, `reviewer_diagnostics.json`, `execution.log`, and `review_manifest.json`.

**L1.** Heck, L., T. Quatmann, J. Spel, J.-P. Katoen, and S. Junges (2025), *Generalized Parameter Lifting: Finer Abstractions for Parametric Markov Chains*, arXiv:2504.05965v2, especially abstract and model scope. https://arxiv.org/abs/2504.05965  
**L2.** Chatterjee et al. (2025), *Fixed Point Certificates for Reachability and Expected Rewards in MDPs*, arXiv:2501.11467, especially the certificate-checking discussion and contributions on p. 2. https://arxiv.org/abs/2501.11467
