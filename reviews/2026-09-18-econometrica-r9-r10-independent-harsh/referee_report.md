# Advisory Referee Report: Neural Bellman Operators

**Date:** 18 September 2026  
**Recommendation:** **Reject in its present form.**  
**Assessment standard:** Substantive Econometrica-style review.  
**Reviewed repository snapshot:** `10248e4a7e5d6668bf82de7d3b146f46bb10ad8f`.  
**Latest complete scientific manuscript:** R9, `8c1e0472279fb66a2419b63b3e35df028ecfdd78`.  
**Status:** Owner-commissioned advisory assessment, not a journal appointment, confidential journal communication, or editorial decision issued by Econometrica.

## 1. Assessment for the editor

This paper contains a potentially useful computational contribution and a considerably improved account of its numerical targets. The signed correction for transition-law interpolation, its comparison with count-informed upper values, and the regional decision certificate deserve serious consideration. The latest complete revision also handles participation, surrender, and investment permissions more carefully than a superficial reading of the earlier criticisms would suggest. There is no justification for pretending that every proposition is false, that its finite economy is secretly being passed off as a diffusion, or that adverse experiments have been concealed.

Nevertheless, I cannot recommend publication, or a revision whose principal task would be exposition. The central economic interpretation is still not established at the level required by the paper's ambition. The primitive preference-adjustment result and the headline dynamic calculation operate through different adjustment directions. The contract extension establishes useful conditional implementability but does not resolve the choice between financial enforcement and an available compulsory term. The financially enforced region reproduces the old noncancellable economy because surrender is inactive; an economically active surrender margin has a different and substantially narrower domain. Finally, small changes in investment permissions erase the opposite-position comparison even when combined with the successful fee implementation. Correct local envelopes describe these changes but do not yet provide the integrated dynamic economic result.

My additional computations sharpen these objections rather than manufacture new algebraic errors. Across nine contracts, upward-only adjustment reproduces the unrestricted initial values while downward-only adjustment reproduces the no-adjustment initial values. Importantly, these equalities fail elsewhere on the state grid. Joint permission-and-fee tests show exactly how the claimed decision depends on contractual financial limits. These are reproducible diagnostics, not continuum certificates or an independent enclosure of the transition constructor.

The next substantive advance should explain a dynamic economic mechanism under verifiable primitive conditions and connect its domain to the computation that certifies it. Another correct envelope identity, another version label, or another successful archive job would not address that requirement.

## 2. Version identification: there is no completed R10 manuscript to review

The latest named revision branch inspected twice during this review is `revision/econometrica-r10-full-response-2026-09-18`. Its head is `10248e4a7e5d6668bf82de7d3b146f46bb10ad8f`, which is also the preceding advisory-review commit. The earlier R10 branch, `revision/econometrica-r10-dynamic-mechanism-2026-09-17`, points to `755b507870b54a100616b0658eba9a031eef2833`.

The comparison from the scientific R9 commit to the latest snapshot contains the two preceding review packages and a 65-line R10 workflow. It changes no manuscript, proof, scientific constructor, or scientific result. `REVISION_INDEX.md` still designates R9 as the current complete revision; the R10 main manuscript and supplement entry points are absent. Accordingly, this report assesses the R9 science inherited by the latest branch, not a nonexistent R10 paper. The branch-status observation is not counted as a mathematical defect in R9. [V1–V3]

The downloaded workflow artifact was generated at `755b507`. It contains a source archive and source-commit identifier, not a newly built R10 manuscript. The archive was used to obtain the full pinned R9 sources and PDFs; the GitHub comparison establishes that the later snapshot adds no scientific changes. Successful source packaging is not successful completion of a scientific revision. [V4]

## 3. Scope and findings that should not be reopened inaccurately

I examined the main and supplement entry points, the relevant inherited operator, approximation, transition-law, economic-mechanism, and certification sections, the R9 contracting and permission sections and proofs, the response, execution records, and the numerical implementation used below. The deposited main paper has 66 pages and the supplement 39. Rendered main pages 56–59 and supplement pages 35 and 37 were inspected directly for the procurement, surrender, enforcement, permission, and arithmetic claims. This is not a claim to have independently reproved every inherited extension or rerun all historical experiments. [M1–M7]

Several existing repairs merit explicit credit. The initial sign restriction applies over a positive-duration first interval, not an isolated control value. Both positive and nonpositive holdings can be risky. The finite randomized-settlement economy is a declared target, distinct from a diffusion. The cardinal payoff from changing the preference state is an explicit economic primitive. Grants and surrender charges use a separate additive utility numeraire rather than silently entering managed CRRA wealth. The statewise fee threshold is not confused with a necessary threshold for equality only at the commissioned initial state. The continuous risky-share reduction is restricted to the first date, with finite consumption–adjustment pairs and the original later action menu. The unfavorable surrender and permission cases remain visible.

The participation and statewise-enforcement arguments appear sound under those stated assumptions. The exact first-date breakpoint argument is also appropriate for the specified piecewise-affine settlement target. My rejection recommendation is not a finding that these propositions fail. It concerns what economic result they collectively establish and the interpretation of that result.

## 4. Major concern A: the actual dynamic adjustment mechanism remains unproved

### 4.1 A primitive example is not a dynamic mechanism theorem

The two-stage primitive family makes the positive class want to reduce the preference index, whereas the nonpositive class wants to increase it. Its cost range is 20–80. The common-cardinal-tilt calculation preserves the relevant opposing primitive shadows. This is a meaningful result about that family. The dynamic economy instead has cost coefficient 2, stochastic preference transitions, settlement, boundary discharge, and continuation values. Its initial optimal drift is positive in both position classes. The manuscript itself acknowledges that the dynamic direction is not mechanically inherited. [M2, M3]

That acknowledgment prevents an erroneous contradiction claim, but it does not supply the missing positive explanation. A positive difference between two adjustment-option values can occur through many mechanisms. Showing that the primitive example and the dynamic computation have the same sign for that difference does not establish that the example explains the computation.

### 4.2 New all-date directional tests at nine contracts

For each of the nine points in

\[
\lambda\in\{0,0.125,0.25\},\qquad d\in\{0.4,0.425,0.45\},
\]

I reoptimized four economies: the full adjustment menu, upward-only adjustment, downward-only adjustment, and no deliberate adjustment. Restrictions apply at every date and state; all other financial controls and the first-period position classification retain their original meaning. The mandate is noncancellable, with eight decision intervals. The commissioned initial state is `(u,X)=(2,1.25)`.

At every one of these nine points, both initial class values in the upward-only economy equal their unrestricted counterparts to the precision recorded by the audit. Both downward-only initial class values equal their no-adjustment counterparts. The largest recorded initial discrepancy in either comparison is zero in binary64 arithmetic. Selected differences, with `Delta = W_positive - W_nonpositive`, are:

| Law probability | Operating benefit | Full or upward-only Delta | No adjustment or downward-only Delta |
|---|---:|---:|---:|
| 0 | 0.400 | +0.000068894883357 | -0.000369477264388 |
| 0 | 0.450 | +0.000184047078138 | -0.000252009676302 |
| 0.125 | 0.425 | +0.000196740684027 | -0.000209326961178 |
| 0.25 | 0.400 | +0.000209377450567 | -0.000168153445686 |
| 0.25 | 0.450 | +0.000324529645348 | -0.000053001250905 |

At the center, the unrestricted positive and nonpositive values are approximately `-0.759029725770272` and `-0.759226466454299`; their no-adjustment counterparts are `-0.794487048712143` and `-0.794277721750965`. The relative adjustment option is `0.000406067645205`. The nine-point extension therefore strengthens the previous center-only observation: downward adjustment is unnecessary for the tested initial-state reversal. It does not provide a certificate for every point of the parameter rectangle. [E1, E2]

### 4.3 A material qualification: the directional equality is not global

The audit also searched the computed state/date value arrays. At the center contract but at initial state `(u,X)=(1.25,1.59375)`, the nonpositive-class value with full adjustment exceeds its upward-only counterpart by approximately **1.221130888309406**. At the same state the downward-only value exceeds its no-adjustment counterpart by approximately **1.302731114145440**. These are alternative initial-state comparisons, not a claim that the state is reached from the commissioned initial condition.

Thus the evidence does not support a universal statement that downward adjustment is valueless in this model. It supports a more interesting question: why does upward adjustment suffice for the commissioned initial states while downward adjustment matters elsewhere? A valid dynamic result must state its initial-state, parameter, and policy domain rather than extrapolate the nine initial-value equalities to the whole grid. [E1, `global_gap_witnesses`]

A useful elementary diagnostic is the derivative of the baseline cardinal flow:

\[
\partial_u\frac{c^{1-u}}{1-u}
=\frac{c^{1-u}\{1+(u-1)\log c\}}{(1-u)^2}.
\]

At the selected consumption `c=0.8`, the expression in braces is at least `1+1.8 log(0.8) = 0.598341607634...` on the preference domain `[1.2,2.8]`. It is positive. Higher preference states can therefore raise future cardinal flow utility at that consumption even without an informal risk-tolerance explanation. But this calculation neither proves the sign of the full continuation derivative nor the optimal adjustment drift or its differential value across position classes. Boundary discharge, wealth transitions, future consumption choices, and liquidation remain essential.

**Required response A.** Give a dynamic proposition, or verifiable sufficient conditions with a certified domain, for the continuation incentive and the class differential. Explain the observed directional asymmetry across initial states. Distinguish the two-stage primitive mechanism from the dynamic mechanism rather than using one as a substitute for the other. Preserve the existing primitive theorem and adverse cases; the missing result cannot be supplied by renaming the numerical option premium.

## 5. Major concern B: participation is coherent, but the institutional comparison remains incomplete

For the stipulated separate-account mandate, the minimum grant

\[
q^*=[G(x_0)-\max_\sigma W_\sigma+C(E)]_+
\]

and the principal's condition `b A >= q*` correctly account for both compensation and delivered service. The policy-selection qualification is explicit. These are not algebraic errors. Nor is an unrestricted optimal-contract theorem logically necessary for a paper studying an exogenously fixed mandate. [M4]

The difficulty arises when the enforcement–commitment frontier is interpreted as an economic comparison of instruments. The minimum operating term makes operation compulsory before date `m`; `m=8` supplies the original noncancellable mandate independently of the fee. The explicit resource cost is the capacity cost `C(E)`, not a separately modeled cost of choosing or enforcing a longer compulsory term.

Consider an `m=1` contract with a fee large enough to implement the noncancellable policy. Compare it with `m=8`, `F=E=0`, and `C(0)=0`. Conditional on the hard term being selectable and carrying no independent cost, the same operating values and selected service duration are available without the positive capacity cost. Whenever participation binds, the hard-term grant is lower by exactly `C(E)`; the principal's surplus rises by the same amount. If participation does not bind, the positive-part formula requires the corresponding qualification. The dominance observation is conditional, not a theorem that every fixed-term model is inconsistent.

The main paper's own procurement table shows the equal operating-duration and zero-capacity-cost grant entries at `F=0.85,m=1` and `m=8`. Adding a capacity cost to the former does not by itself price the opportunity to choose the latter. I inspected that table; I do not count its entries as a newly executed procurement experiment. [M5, main p. 56]

**Required response B.** Specify which institution is actually being chosen. A fixed or constrained term can be economically legitimate, but its restriction and the associated substantive question must be explained. An endogenous instrument comparison needs a term-enforcement technology, constraint, or cost treated on the same footing as capacity. Compare grants, service, enforcement costs, and policy selection under common primitives. A conditional implementability frontier should not be advertised as an economically selected mechanism without this additional step.

## 6. Major concern C: inactive implementation, active surrender, and financial permissions are different results

### 6.1 The successful fee box disables the termination margin

For the original finite action target, the statewise threshold is the maximum eligible reachable liquidation shortfall against noncancellable continuation. Backward induction yields equality of continuation values above that threshold; action-set inclusion makes adjustment weakly reduce the required threshold. These are useful, correctly qualified statements. [M4, M6]

The deposited sufficient regional bound for surrender after one interval is `0.8348592805606002`. The paper's successful fee interval `[0.85,0.90]` lies strictly above it. Conditional on that stated stored-array bound and error allowance, surrender is strictly inferior at every eligible reachable live node throughout the original law/benefit rectangle. The fee box implements the old mandate; it does not supply a region in which an exercised surrender option explains the reversal. The bound and the interval certificate were inspected in this review, not independently regenerated as a complete regional sweep. [M5, main pp. 57–58; M6]

This does not make the result empty: finite financial enforcement can implement the stipulated compulsory operation, and its capacity cost can enter participation. But the economic content is implementability. Treating an inactive extra dimension as evidence for a richer active mechanism would overstate what has been established.

### 6.2 New joint reoptimization confirms both the favorable center and its failure boundary

The independent Bellman recursion reproduces the active-surrender center at `F=0.80,m=1`. At `(lambda,d)=(0.125,0.425)`, the adjusted difference is `+0.000196740684027` and the no-adjustment difference is `-0.000191857347061`. The positive no-adjustment class has discounted elective-surrender exposure `0.068995145990461`; the other three exposures are zero. This exposure is not an undiscounted probability.

At `(lambda,d)=(0,0.4)` and the same fee, the adjusted difference is `+0.000068894883357`, but the no-adjustment difference becomes **+0.001392379630300**. Its positive-class surrender exposure is `0.087947508925297`. The original opposite-sign rectangle fails. R9 already discloses the failure, and the review gives credit for that disclosure. At fee `0.85`, the tested center and corner return to the noncancellable class values, with zero elective-surrender exposure. [E1; M5]

### 6.3 Joint permission tests show why a central decision theorem is still needed

I combined those stopping continuations with the manuscript's exact first-date risky-share breakpoint search. This is continuous optimization only of the first risky share conditional on the finite consumption–adjustment pairs; later actions remain the original finite menu. The continuation recursion is independently written; the breakpoint implementation is the author's and is not represented as an independent second implementation.

At the center contract, the following results obtain. `L` and `S` are the initial long and short permissions; the minimum term is one interval.

| Fee | Long permission | Short permission | Adjusted Delta | No-adjustment Delta |
|---|---:|---:|---:|---:|
| 0.80 | 0.80 | 0.50 | +0.000196740684027 | -0.000191857347061 |
| 0.80 | 0.82 | 0.50 | +0.000554759103774 | +0.000197830973605 |
| 0.80 | 0.80 | 0.51 | -0.000011968637109 | -0.000425519084378 |
| 0.85 | 0.80 | 0.50 | +0.000196740684027 | -0.000209326961178 |
| 0.85 | 0.82 | 0.50 | +0.000554759103774 | +0.000178901666151 |
| 0.85 | 0.80 | 0.51 | -0.000011968637109 | -0.000442988698495 |

A two-percentage-point increase in the long permission makes both regimes prefer a positive position; a one-percentage-point increase in the short permission makes both prefer a nonpositive position. The additional fee implementation does not remove this dependence on financial permissions. These joint tests extend, rather than contradict, the manuscript's separately reported no-surrender permission sensitivities. The author expressly states that the regional fee certificate does not automatically extend to enlarged permission menus. [E1; M4; M5, main p. 59]

The mathematical implication is not that the old certificate is wrong. The economic implication is that adjustment, permission limits, and operating commitment must be understood jointly. At a binding boundary, the familiar unconstrained portfolio intuition does not determine the sign. The manuscript's conditional permission shadow values and implicit-boundary derivatives correctly describe local movement, but they do not yet identify the economically relevant joint domain.

**Required response C.** Separate and connect three claims: financial implementation with inactive surrender; a genuinely active-surrender mechanism; and the position comparison under financial permissions. Provide a joint economic domain or a substantive boundary characterization, with a certificate for any claimed continuum region. Preserve the unfavorable corner and both permission interventions. A collection of individually favorable slices does not establish the joint mechanism.

## 7. Major concern D: the computational contribution needs an integrated economic payoff

The strongest method in the present manuscript is the signed cross-operator correction for an affine transition-law mixture and its relation to the count-information construction. A raw endpoint chord can fail; the correction addresses that failure. The sharper count construction and the cheaper compressed recursion answer a real precision–work question. I did not identify a counterexample to the corrected argument under its assumptions. Second-order correction error is not being treated here as second-order total policy-bank loss. [M7]

Other ingredients should be credited at their actual level. The exact policy-improvement statements are conditional mathematical results, not a guarantee that neural training finds the required selector or residual bound. The affine reward-feature envelope and the participation formula are useful accounting tools, but neither by itself supplies a novel dynamic economic mechanism. A certificate can establish the sign of a precisely defined decision without explaining why that decision occurs.

The existing comparison with optimistic linear support and successor features is relevant and should not be erased. Alegre, Bazzan, and da Silva (2022) study transfer across linearly parameterized rewards with common transition dynamics. Their fixed-dynamics reward-transfer setup is not identical to a controlled finite-horizon family in which the transition law changes at every date. Conversely, the presence of a different transition-law construction does not make every affine reward identity new. The manuscript already discusses this distinction and includes neural-free and structural countercomparisons; I do not allege their absence or blanket duplication. [L1; M7]

What remains insufficient is the connection to a central economic theorem. The paper should make clear what economically meaningful region, institutional comparison, or policy conclusion becomes answerable because the certificate is available, which primitive inequalities generate that result, and which cost of obtaining precision is relevant to that task. The current application demonstrates small but certified class-value differences for a carefully stipulated finite target, alongside economic margins that can readily change those signs. That is a useful experiment, but a substantial integrated contribution cannot be inferred from the number of correct intermediate propositions.

The current audit constructor holds `775,469,952` bytes of kernel payload for 1,617 states, 1,568 operating actions, and eight dates. This is not process peak memory, an end-to-end timing, or an impossibility result about scaling. I did not rerun neural training or the complete timing frontier. Existing same-target, same-tolerance comparisons should be retained; no universal neural advantage is required, and none should be inferred from this audit.

**Required response D.** Organize the contribution around an economic question whose answer genuinely uses the certified computation, not around a sequence of generic optimization identities. State the new transition-law result precisely relative to reward-transfer methods, retain matched construction/validation costs, and connect numerical precision to the mechanism or contractual decision. This is a demand for substantive integration, not for empirical calibration as a prerequisite for theoretical economics.

## 8. Target, arithmetic, and evidentiary qualifications

The stored-array arithmetic allowance and the error in constructing those arrays are separate. Supplement S.13.5 makes that distinction explicitly and supplies a target-transfer inequality. The reported per-class arithmetic analysis is below the deliberately larger allowance of `1e-7`; the displayed class-difference intervals include `2e-7`. Nothing in the replay below supplies interval enclosures for all powers, exponentials, interpolation weights, or transition rows in a real-arithmetic constructor. A sign claim about another target must charge its discrepancy through the stated transfer account. A diffusion additionally needs an appropriate consistency and approximation argument. [M6]

That limitation is disclosed, not a newly discovered hidden error. It still matters economically because several class differences are small. A substantive extension should either remain explicitly about the finite stored-array target or demonstrate that its target-transfer budget is below the relevant decision margin. Last-bit agreement is not such a demonstration.

The new numerical evidence uses an independently written Bellman recursion and action restrictions on the author's pinned reward/transition arrays. The permission search and surrender-moment routines are shared author components. Four joint contracts were revalidated against the production recursion, including checkpoints from an interrupted invocation; focal selected-control reconstruction was also checked. The maximum recorded production/reconstruction discrepancy is approximately `1.33e-15`, against tolerance `2e-11`. All 633 pre-existing non-cache archive files checked before and after execution retained their hashes. This establishes consistency and preservation of those local inputs, not independent construction of the economic model. [E1–E3]

The first execution was interrupted by the execution-time limit after saving nine directional cases and three joint cases. A second invocation completed the remaining joint case. A final validation invocation rechecked every joint checkpoint and the focal comparisons. All three logs are retained. The final invocation's approximately 18.3 seconds is only that resumed validation segment, not an end-to-end workload benchmark. No incomplete directional case is counted as completed, and no continuum claim is inferred from nine points.

## 9. What would constitute a substantive reconsideration?

| Concern | Necessary substantive evidence | Insufficient response |
|---|---|---|
| A: dynamic mechanism | Dynamic sign or ordering conditions; explicit state/parameter domain; explanation of upward sufficiency at the commissioned state and downward value elsewhere | Repeating the two-stage example, the relative option sign, or an initial-control table |
| B: institutional comparison | A justified fixed/constrained term, or a comparable cost/feasibility account for compulsory terms and financial capacity, with participation and service | Pricing capacity while leaving a selectable hard-term alternative unexamined |
| C: joint economic domain | A coherent connection among inactive implementation, active surrender, and permission-dependent position rankings; regional certification where claimed | Combining favorable slices or treating an inactive fee dimension as an active mechanism |
| D: integrated contribution | A central economic result that uses the transition-law certificate, with explicit assumptions and matched precision/work accounting | More envelope identities, labels, or unsupported neural-necessity rhetoric |
| Target and execution | Exact candidate identity; complete manuscript/response; executed checks on that science; explicit target-transfer budget | A new branch name, packaging workflow, or numerical replay relabeled as a constructor enclosure |

The earlier report's principal scientific concerns remain unresolved because no intervening scientific revision is present. This review adds a nine-point directional experiment, alternative-initial-state witnesses that limit its extrapolation, and joint fee/permission reoptimization. The author should address those findings directly while preserving the valid results and unfavorable evidence. At the reviewed snapshot, the appropriate recommendation remains rejection in present form.

## 10. Source register and reproducibility

Repository sources are pinned below. References to page numbers concern the deposited R9 PDFs, not text-extraction line numbers. The accompanying code and results are evidence of the specific executed checks, not a replacement for the mathematical arguments.

### Version and provenance

- **V1:** [Latest inspected revision ref](https://github.com/TrillionniumFoundation/NBO/tree/revision/econometrica-r10-full-response-2026-09-18), observed at `10248e4a7e5d6668bf82de7d3b146f46bb10ad8f`. This branch link is mutable; the recorded SHA defines the review.
- **V2:** [Revision index at the reviewed snapshot](https://github.com/TrillionniumFoundation/NBO/blob/10248e4a7e5d6668bf82de7d3b146f46bb10ad8f/REVISION_INDEX.md).
- **V3:** [Scientific R9 to reviewed-snapshot comparison](https://github.com/TrillionniumFoundation/NBO/compare/8c1e0472279fb66a2419b63b3e35df028ecfdd78...10248e4a7e5d6668bf82de7d3b146f46bb10ad8f).
- **V4:** [Workflow run 35222706049](https://github.com/TrillionniumFoundation/NBO/actions/runs/35222706049), artifact `10497729014`, SHA-256 `16be7b1e9c1e7b29e440fafda41ed1419049653baf92083c5d5d855aedd05931`, source commit `755b507870b54a100616b0658eba9a031eef2833`.

### Manuscript and proofs

- **M1:** [R9 main entry point](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/ECTA_R9.tex) and [supplement entry point](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/SUPP_R9.tex).
- **M2:** [Decision economy, cardinal primitive, and dynamic mechanisms](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r8-full-response/paper/04g_decision_economics.tex).
- **M3:** [Primitive economic proofs](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-16-r7/paper/S11_economic_proofs.tex) and [cardinal robustness and associated response proofs](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r8-full-response/paper/S12_full_response.tex).
- **M4:** [Participation, termination, and portfolio permissions](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r9-participation-permissions/paper/04i_contracting.tex).
- **M5:** [Contract evidence](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r9-participation-permissions/paper/05e_contract_evidence.tex); main PDF Tables XXVI–XXX, pages 56–59.
- **M6:** [Contract proofs and arithmetic/target distinction](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r9-participation-permissions/paper/S13_contract_proofs.tex), especially S.13.2–S.13.5.
- **M7:** [Signed transition-law correction](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-16-r6/paper/04c_kernel_transfer.tex), [comparative upper oracles](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r8-full-response/paper/04e_comparative_oracles.tex), and [literature correspondence](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r8-full-response/paper/04h_literature_correspondence.tex).
- **H1:** [Preceding advisory report](https://github.com/TrillionniumFoundation/NBO/blob/10248e4a7e5d6668bf82de7d3b146f46bb10ad8f/reviews/2026-09-18-econometrica-latest-r9-r10-audit/referee_report.md). Its conclusions were treated as questions to investigate, not independent evidence of their correctness.

### New review evidence

- **E1:** [Complete reviewer results](reviewer_results.json).
- **E2:** [Executed reviewer audit](reviewer_audit.py), including explicit independence limits and all-date directional restrictions.
- **E3:** [Review manifest](review_manifest.json) and [execution logs](execution_logs.txt). [README](README.md) gives reproduction and scope.

### Primary comparator checked

- **L1:** Alegre, Lucas Nunes, Ana Bazzan, and Bruno C. da Silva (2022), [Optimistic Linear Support and Successor Features as a Basis for Optimal Policy Transfer](https://proceedings.mlr.press/v162/alegre22a.html), Proceedings of Machine Learning Research 162, 394–413. In particular, Section 3.1 defines the common-dynamics, varying-reward task family. This report does not claim an exhaustive current-literature search or a proof of novelty.
