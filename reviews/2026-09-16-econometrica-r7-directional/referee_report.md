# Referee report: *Neural Bellman Operators*, R7
## Directional spatial audit and contribution assessment

**Author:** Qian Qi  
**Date:** 16 September 2026  
**Recommendation:** **Reject in its present form for Econometrica.**  
**Manuscript:** `revision/econometrica-r7-2026-09-16`, commit `fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17`  
**Manuscript tree:** `cdc8e227881d5e95a8740c4f77298f73a0b9399d`  
**Review branch:** `review/econometrica-r7-directional-audit-2026-09-16-fbfbf90`  
**Historical-review parent:** `a5e4c20458947ddffee9cdbb0e0af5ca792d2979`

This is an owner-commissioned, external-referee-style advisory report. It is not an appointment by Econometrica, a report solicited by the journal, or an editorial decision. The recommendation concerns the present manuscript, not the feasibility of the research program.

## 1. Editorial assessment and manuscript identification

The manuscript contains useful finite-model results, but the economic inference that is supposed to justify its computational apparatus is not yet robust enough to carry the paper. My principal new finding is more specific than the previous spatial objection: **refining wealth alone reverses the no-adjustment first-risk ranking at a corner of the advertised counterfactual region, while the decision calendar, preference grid, action menu, financial primitives, and preference-shock construction are held fixed.** An exact audit of the admissible frozen proposals establishes that this comparison does not omit a distinct action from the original no-adjustment target.

This is not a counterexample to the tensor inequality for the original stored arrays. The distinction is essential. A valid statement about one numerical economy is not automatically an economically informative statement about the model that motivated those arrays. Here the manuscript makes that distinction in its qualifications, but has not supplied the evidence that would make the connection scientifically persuasive. Increasing the precision with which one certifies the original array problem does not resolve the issue.

I also have reservations about the incremental methodological contribution and its relation to the economic application. R7 demonstrates a genuine local precision–work tradeoff; it is no longer fair to say that the compressed oracle has no positive computational case. Nevertheless, the headline economic certificate uses the count construction rather than establishing an economically consequential advantage of compression or learning. The literature boundary also needs a substantive correction: the cited 2016 parameter-lifting paper already treats expected rewards and nondeterministic models. Merely contrasting probabilistic verification with reward optimization does not establish the new contribution.

These concerns require research, not only changes of presentation. I therefore do not recommend acceptance or a revision limited to exposition. At the same time, several earlier technical objections have been answered and should not be recycled as if R7 had done nothing.

There is no newly deposited R8 manuscript in the repository snapshot examined for this report. Both branch inventories inspected during this audit showed `revision/econometrica-r8-2026-09-16` at `3b40e681...`, the earlier R7 review head, and `revision/econometrica-r8-independent-response-2026-09-16` at `a5e4c204...`, the subsequent independent-review head. Comparing the latter with the manuscript commit gives only twelve added review files. The revision index still identifies R7. This is consequently a further review of **unchanged R7**, not an assessment of a nonexistent R8 response. No failure to answer these newer reviews is being attributed to an author response that has not been deposited. [M0, H1–H2]

## 2. Scope, provenance, and executed checks

I consulted the complete R7 entry points, the main manuscript and supplement, the R7 response to R6, relevant inherited operator/model sections, both existing R7 reports, and the source and evidence for the comparative and economic calculations. The new proofs in S.10–S.11, the regional application, and the transition implementation received the closest attention. Tables XVII–XVIII and the arithmetic discussion were also visually inspected in the compiled PDFs. This is not a claim to have independently re-proved every inherited theorem.

The source and evidence were obtained from Actions run `35063710310`, artifact `10433863234`. The ZIP SHA-256 is `b0bcb8542760adffae90e3ffff7ad61d0fe5b49e0b93e0f66a05eeea170d51c2`. Reconstructing the source with the executed artifact overlays gives exactly manuscript tree `cdc8e227...`; all 27 entries in the authored-source inventory match. The artifact's final-commit record identifies `fbfbf902...`, rather than merely the earlier workflow-triggering commit. The 45-page main PDF and 29-page supplement were present. No tracked manuscript, numerical source, or author evidence file was modified by these checks.

The accompanying programs distinguish three evidence classes. The first is a **rerun of author checks**: the 96-small-model, 480-parameter validation suite, the primitive-family calculation, and the deposited tensor replay. The second is a **reviewer-written Bellman and policy-reevaluation driver** for the exact no-adjustment finite menu, using the author's transition construction on seven spatial grids. The third is an **independently derived interpolation-moment identity** checked against actual kernel weights in thirty interior cases. The latter two programs do not use the author's regional optimizer as their decision rule. They do reuse its transition law and are not independent implementations of the stopped diffusion.

The directional study contains 35 grid/parameter comparisons and 70 class values. Its largest selected-policy replay discrepancy is `1.7763568394002505e-15`; the sparse-multiplication backend differs from the original weighted-gather path by at most `4.440892098500626e-16`. The eight comparable corner class values on the original grid match the author's full-target values within `1.1102230246251565e-16`.

I did **not** rerun historical neural training, the complete author timing contest, the earlier temporal refinement, the prior neural-free regional construction, or the adjusted regime on the new grids. I do not claim a new regional tensor certificate for a refined grid or identify the limiting diffusion's sign. Deposited timings and historical findings are attributed as such below. The reviewer runtimes are recorded for reproducibility, not compared with author timings as a speed benchmark. Full results, including unfavorable and unchanged signs, are in `diagnostic_results.json`; reproduction instructions and identities are in the companion README and manifest.

## 3. Results that R7 has genuinely repaired

**The upper-oracle comparison is now coherent.** The remaining-count recursion uses a common action before the hidden endpoint-law branch. Its enlarged information set explains why it is an upper value rather than a feasible anticipative policy. The coefficientwise ordering against the corrected chord, its preservation under positive subdivision, and the separate rectangular bound have appropriately qualified statements. The induction in S.10 handles endpoint counts and short horizons. I found no algebraic counterexample under the stated finite-model assumptions. [M1, M3]

**The total-error statement is not merely the second-order correction.** The bound `2 L_n w + (1/2) Q_n w^2` includes the loss of the endpoint-policy bank and permits changes in the maximizing action. R7 no longer infers an `O(epsilon^-1/2)` bank size from a quadratic correction: its scalar worst-case interval count is `O(epsilon^-1)` with fixed finite-model constants. The rerun's largest tested bound ratio is `0.5534812664972152`; count replay error is `1.7763568394002505e-15`, and the minimum chord-minus-count coefficient is `-2.220446049250313e-16`, consistent with roundoff. These checks support implementation consistency, not a proof by random testing. [M1, M3]

**The primitive option inequality is a real sufficient condition.** The CRRA curvature identity, quadratic upper/lower option bounds, and endpoint-based uniform family argument provide more than an envelope identity evaluated at an already optimized policy. The rerun gives a uniform relative-option lower bound of `0.0018668287652439802` in the declared two-stage family. I do not reject this proposition as algebraically false. Its relation to the dynamic application is a separate issue. [M2, M4]

**The regional sign certificate is decision-specific.** R7 constructs upper and feasible lower values separately for the two first-risk classes and adjustment regimes. It does not use a generic `10^-3` welfare tolerance to infer a difference around `10^-5`. The deposited tensor replay discrepancy is zero. Subject to the finite-array and arithmetic assumptions, Table XVIII establishes its advertised signs on the original target. [M2, M4–M5]

These repairs are credited without treating successful tests or a long preservation history as evidence that the contribution meets the journal's substantive standard.

## 4. R7-D-F1 — Wealth-only refinement changes the economic decision

**Severity: publication-blocking economic robustness issue.**  
**Locations:** Main Section 8.13 and Table XVIII, pp. 39–40; `05c_r7_evidence.tex`, lines 15–26; Supplement S.11.3–S.11.4; `replication/r7/decision.py`; reviewer directional program and results. [M4–M5, C1]

The advertised region is

\[
(\lambda,d)\in[0,0.25]\times[0.4,0.45],
\qquad (u,X)=(2,1.25),\quad k=2.
\]

Let `Delta^0` denote the optimal positive-first-position value minus the optimal nonpositive-first-position value when deliberate preference adjustment is prohibited at every date. The regional claim requires this difference to be negative throughout the rectangle. The original upper bound is `-5.2993655605010966e-5`, after the stated per-class arithmetic allowance `3.797650002493679e-9`. [M5]

The previous independent report held eight dates fixed while refining both state coordinates. That was already informative, but left open which spatial component mattered and explicitly disclosed its common-menu comparison. The new experiment separates the coordinates and closes the action-menu qualification for the no-adjustment arm.

### Exact admissible-menu audit

The original target combines two published common meshes, with 1,565 distinct actions, and three state/date-specific frozen proposals. Filtering the union to exact zero deliberate adjustment leaves 185 actions. I inspected every frozen proposal satisfying the same zero-adjustment restriction used by the production code. Across seeds 101, 202, and 303 there are respectively 3,125, 3,074, and 2,956 admissible entries. Each seed has nine distinct admissible triples; every triple is **exactly** present in the 185-action common menu. There is no tolerance-based identification of economically different consumption or portfolio choices. The admissible preference controls themselves are exactly zero.

Therefore, for the original no-adjustment problem, removal of these duplicate proposals changes neither the feasible action envelope nor its Bellman optimum. This is stronger than simply invoking `include_neural=False`, which would also remove the second historical common mesh. The reviewer constructs the union explicitly. The original-grid class values independently reproduce the author's full-target values, as reported above. [C2; `proposal_audit` in the diagnostics]

### Fixed-calendar directional experiment

All runs retain horizon one, eight decision dates, the same 185 admissible controls, operating boundaries, utility, settlement, financial coefficients, endpoint shock generators, and common-parameter mixture. Later risky positions may change sign. The initial state is a grid node on every mesh. Only the grid on which continuation values are represented is changed. Entries below are finite-model point solves, not regional interval claims.

At the corner `(lambda,d)=(0.25,0.45)`:

| Preference nodes × wealth nodes | Change from original spatial representation | `Delta^0` |
|---|---|---:|
| 33 × 49 | Original target | `-5.300125090501595e-5` |
| 65 × 49 | Preference only | `-4.206987444432819e-5` |
| 97 × 49 | Preference only, further refinement | `-3.935073383842802e-5` |
| 33 × 97 | **Wealth only** | **`+6.126273957574035e-5`** |
| 33 × 145 | Wealth only, further refinement | `+9.79426715395082e-5` |
| 65 × 97 | Both coordinates | `+7.20301600420914e-5` |
| 97 × 145 | Both coordinates, further refinement | `+1.1125049083382521e-4` |

Thus the negative no-adjustment ranking does not survive wealth-only refinement. The movement from 33 × 49 to 33 × 97 is `1.142639904807563e-4`, in the same utility units as the reported decision margin. This cannot be explained by the observed replay discrepancies. Preference-grid spacing, preference quadrature, and decision frequency have not changed in that comparison.

The other inspected points are disclosed rather than suppressed. At the center `(0.125,0.425)`, the differences on 33 × 49, 33 × 97, and 97 × 145 are respectively `-2.0932696117847982e-4`, `-9.478053799472086e-5`, and `-4.313025746005561e-5`: all remain negative. At `(0.25,0.4)`, the finest tested grid gives `+2.1809713333098557e-6`, whereas the original gives `-1.6815344568577029e-4`. The evidence is not that every reversal disappears. It is that the **whole-region negative arm** of the reported opposite-ranking conclusion is sensitive to wealth representation.

The adjusted arm was not recomputed on these grids. Consequently, I do not claim that the two refined-grid regimes necessarily have the same sign everywhere, or supply new lower bounds for their option difference. Establishing that the required negative arm changes sign at a corner is sufficient to challenge stability of the whole-region conclusion. Nor is the finest grid declared the truth: neither the original nor the refined solutions here carry a bound relative to the intended continuous-state transition problem.

**Required response.** The author must identify the economic target whose risk ranking is meant to be learned, and address this directional sensitivity. A substantive response could control the decision error relative to that target, or economically justify the finite-state transition itself and demonstrate robustness to relevant perturbations of it. Retaining eight dates as a primitive does not answer a test performed at those same dates. Quoting the original tensor theorem does not answer a change in the arrays to which it applies. Moving the favorable rectangle without explaining its movement does not identify the mechanism.

## 5. R7-D-F2 — The omitted numerical error affects the joint shock mechanism

**Severity: major mechanism and error-account issue, supporting F1.**  
**Locations:** `replication/r4/solver.py`, lines 35–66; `replication/r5/contracts.py`, lines 17–61; inherited `03_approximation.tex`, lines 13–46; Supplement S.11.4; reviewer moment program. [C2–C3, M4, M6]

There is an exact local description of what positive bilinear interpolation does to the finite transition. Let `Y` be an interior pre-interpolation quadrature outcome and `Z` the grid-valued outcome represented by the interpolation weights. Let `l_i(Y)` and `r_i(Y)` be the adjacent nodes in coordinate `i`. Tensor-product linear interpolation has

\[
E[Z\mid Y]=Y,
\quad
\operatorname{Cov}(Z)=\operatorname{Cov}(Y)+
\operatorname{diag}\!\left(E[(Y_i-l_i(Y))(r_i(Y)-Y_i)]\right).
\]

To see this, conditional on `Y` each coordinate is randomized between its two neighboring nodes with mean `Y_i`. Its conditional variance is the product of the distances to those nodes; the tensor weights give zero conditional cross covariance. The identity then follows by total covariance. It applies to the interior cases checked here after discounting is divided out. Every quadrature branch is live in those cases, so the calculation does not confuse killing with variance.

The earlier report emphasized the preference marginal. This audit reproduces that issue but also checks the wealth marginal and cross covariance. At `(u,X)=(2,1.25)`, step `h=1/8`, consumption `0.8`, and zero deliberate adjustment, the preference raw variance is `0.0003125`. On the original grid, its interpolated variance is `0.0008838834764831865`, a factor approximately 2.8284. **That factor is unchanged in the wealth-only 33 × 97 comparison.**

For the two initial portfolio choices actually selected in the no-adjustment comparisons, the wealth variance ratios are:

| Portfolio position | Raw wealth variance | Grid/raw ratio, 33 × 49 | Grid/raw ratio, 33 × 97 |
|---|---:|---:|---:|
| `-0.5` | `0.001953125` | `1.0812713398519627` | `1.0187713398519627` |
| `+0.8` | `0.005000000000000004` | `1.0370403017640422` | `1.0075762224168698` |

At endpoint correlation `-0.25`, raw and interpolated cross covariance agree to roundoff. Their **correlations** nevertheless differ because the marginal variances change. For the positive position on the original grid the realized interior correlation is about `-0.145972`, rather than the raw-quadrature correlation `-0.25`. For a negative position the wealth loading reverses the correlation sign; this is not an error in the shock generator. The covariance identity is checked for both endpoint laws and three actions on five grids, with maximum discrepancy `8.538092108323347e-18`.

These facts should not be overinterpreted. The identity does not establish that local wealth-variance inflation alone causes the value-difference movement. Wealth interpolation changes continuation values throughout the domain, including behavior near the stopping boundary, and optimal later decisions may change. The point is narrower and stronger: **repairing preference-grid variance alone is not a sufficient response to the observed sensitivity**, because wealth-only refinement changes the ranking while that variance is unchanged. A decomposition of wealth continuation, boundary effects, and endogenous controls is now warranted.

The manuscript already defines an operator-error term that includes interpolation, quadrature, transitions, and stopped payoffs. My objection is not that the abstract theorem lacks this term. It is that the economic certificate operationalizes arithmetic for stored arrays, not this model-approximation error. [M6]

For example, suppose class-optimum approximation errors at the stated initial state could be bounded uniformly over the region by `E_+` and `E_-`. The original finite-target interval for the class difference would have to be enlarged by `E_+ + E_-`. A sufficient condition for its no-adjustment sign to survive is that this sum be smaller than the certified margin of roughly `5.2994e-5`. A direct error bound for the difference could be more efficient; separate global value bounds are not mandatory. Either route must address the relevant model, not only floating-point summation. More parameter subdivisions and a smaller arithmetic allowance will not control the spatial effect documented in F1.

## 6. R7-D-F3 — The distinctive computation is not yet tied to a robust economic payoff

**Severity: major contribution issue.**  
**Locations:** Main introduction, Sections 6 and 8.12–8.13, Tables XVI–XVIII; S.10; author response to R6-F1/F2. [M0–M5]

The valid positive result deserves a precise statement. In the deposited autonomous experiment, chord-only refinement uses 18 anchors and 73.41 seconds; count-only uses 11 and 115.38 seconds; the cascade uses 11 and 127.73 seconds. All arms use the same target and `10^-3` tolerance, and rejected parents are charged. These are author-reported single-pass measurements, not timings rerun here. They demonstrate that a cheaper, weaker upper oracle can win despite requesting more anchors. [M5]

The work account is also meaningful: conditional on shared exact endpoint solutions, the correction needs `4H-6` action-wide kernel applications versus `H(H+1)-2` for the specified cached count recursion. At eight dates these are 26 and 70. The stored correction has seven nonzero state vectors versus 28 interior count vectors. However, the common feasible-policy coefficients still require order `m S H^2`; action-wide arrays, transition representation, endpoint optimization, and restriction/subdivision remain. R7 explicitly acknowledges these qualifications. They should not be removed, and the local count is not being asserted to be globally complexity-optimal. [M1, M3]

What remains unclear is why these gains change an important economic answer. The strict regional risk result uses localized count upper values. The experimental endpoint solutions are exact finite-action optimizations. The new no-adjustment audit shows that, in that arm, admissible frozen proposals add no distinct actions at all. The prior review additionally reports a neural-free feasible bank sufficient for the original full-target regional upper construction, but that result is historical evidence rather than a new execution in this audit. [H1]

None of this proves that neural proposal mechanisms are useless, or that corrected chords cannot contribute in a different regime. It does mean that the title and broad architecture are not yet an explanation for the demonstrated economic gain. A correct certificate combined with an exact grid optimizer is valuable; its distinctive advantage must nevertheless be established rather than inferred from the presence of a neural component elsewhere in the manuscript.

A focused next comparison should use an economically justified target and a decision-level tolerance, hold policy and information access comparable, and measure complete costs including endpoint construction, feasible-policy evaluation, refinement, and verification. It should identify when the compressed construction or learned proposals materially improve that workload. This does not require winning every benchmark, proving a dimension-free theorem, or replacing every conventional solver. It requires one persuasive, robust connection between the paper's distinctive ingredient and an economic question. Passing F1 alone would not establish that contribution, and a favorable timing table alone would not resolve F1.

## 7. R7-D-F4 — The literature boundary is drawn too loosely

**Severity: substantive positioning issue; not an allegation that the exact new theorem already exists.**  
**Location:** `04e_comparative_oracles.tex`, line 36, and the R7 literature discussion. [M1]

Quatmann et al. (2016) already extend parametric models with rewards in Section 2.1; Section 2.2 includes expected-reward specifications and nondeterministic models. Its Section 3.3 explicitly discusses regional expected-reward verification, with additional restrictions, including disjoint reward/probability parameters for transition rewards. Section 4 treats original action nondeterminism. Thus R7's contrast between principally probabilistic specifications and a reward optimum is not a sufficient contribution boundary. This does **not** show that the corrected chord, its count ordering, or its policy-bank bound appears there. It requires a careful mapping of assumptions and outputs, including finite horizon, signed rewards, shared parameter dependence, action information, and feasible lower policies. [L1]

Heck et al. (2025) is also pertinent: generalized parameter lifting and its big-step transformations are directed at obtaining tighter regional abstractions and reducing refinement. Its principal setting is parametric Markov chains and reachability specifications, not automatically R7's controlled reward problem. I do not infer implementational equivalence or a dominance result from the abstract. Nevertheless, the paper should explain how its dependence/compression tradeoff relates to that work, rather than treating a simple rectangular comparator as exhausting relevant refinements. [L2]

A theorem-level differentiation is needed before an originality claim can be evaluated confidently. Merely adding citations will not supply it. Conversely, no requirement is being imposed to benchmark an entire verification package on a task its assumptions do not support.

## 8. R7-D-F5 — The primitive economic model explains a possibility, not yet the dynamic result

**Severity: major explanatory gap, conditional on repairing the numerical application.**  
**Locations:** Main primitive proposition and risk-frontier discussion; Supplement S.11.1–S.11.2. [M2, M4, M7]

The two-stage sufficient condition isolates a legitimate channel: the squared preference shadow, scaled by curvature and effort cost, can make adjustment more valuable for one consumption lottery than another. It is not merely the observation that a larger feasible set helps. The paper is also explicit that the risky lottery, the operating-duration difference, and the cost range in this specialization do not calibrate or approximate the eight-date stopped economy. That candor is appropriate.

But this leaves the principal economic narrative incomplete. In the specialization, lotteries and discounted operating durations are primitives fixed before the preference choice. In the dynamic application, consumption, wealth, stopping, subsequent risky choices, and adjustment jointly determine payoffs and exposure. The initial risk class constrains only the first portfolio position, not a fixed consumption distribution. An option ordering in the former environment does not by itself predict an option ordering in the latter. A region certificate would establish the numerical ordering; it would not by itself identify its cause.

A substantive bridge could take the form of a justified dynamic sufficient condition, a transparent limiting specialization, or controlled economic counterfactuals that separate consumption exposure, operating duration, settlement, and later policy changes. The resulting account should explain the direction of the adjustment premium before treating the successful optimized difference as its explanation. Empirical calibration is not a prerequisite for a theoretical contribution, but a mechanism must have content beyond a chosen example.

The inherited model already acknowledges that preference-dependent cardinal normalization affects incentives and that stopping and settlement matter. I do not allege that these caveats are missing. The unresolved question is which restrictions make the economic prediction portable, especially after F1 shows sensitivity in the numerical representation of wealth.

## 9. Presentation and disposition of the next response

One concrete inconsistency should be corrected: the final sentence of `04e_comparative_oracles.tex` says that the measured frontier does not represent the cascade as an executed autonomous timing contest. Table XVII and the later text do report such an autonomous experiment. The intended distinction between the common-bank frontier and the separate autonomous experiment is recoverable, but the sentence should name it explicitly. This is a presentation repair, not a reason to disregard the executed adaptive evidence. [M1, M5]

The paper should preserve the repaired theorems, adverse comparisons, and original certified arrays as a documented result. It should not erase the original region or silently replace its transition law. A new response should state which objections are mathematical, which concern approximation to an economic target, and which concern contribution. Those categories have different remedies.

For another assessment, the decisive items are a traceable answer to the wealth-only sign change, a decision-level treatment of the relevant approximation error or a substantive defense of the finite-state economic primitive, a robust end-to-end contribution comparison, and a corrected relationship to the verification literature. The primitive economic interpretation should then be connected to the model actually being solved. These are not demands for arbitrary additional scope. They address the manuscript's central promise that computational certification distinguishes economic behavior from approximation error.

**Bottom line:** R7 has improved enough that its finite-model mathematics should be taken seriously. It has not yet established that its flagship economic conclusion is stable under the numerical representation of the stated economy, nor that its distinctive computational ingredient delivers a sufficiently consequential advance. My recommendation remains **reject in the present form**.

## Source locators

All manuscript and source paths below are fixed at the reviewed commit, not a mutable branch. Page references refer to the compiled R7 PDFs. The accompanying JSON and reviewer scripts supply the new numerical evidence.

- **M0:** [R7 revision index](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/REVISION_INDEX.md), [entry point](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/ECTA_R7.tex), and [response to R6](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/revisions/2026-09-16-r7/response_to_referee.md).
- **M1:** [Comparative oracles and total error](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/revisions/2026-09-16-r7/paper/04e_comparative_oracles.tex), especially lines 25–36 and 53–69.
- **M2:** [Primitive option and tensor certificate](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/revisions/2026-09-16-r7/paper/04f_economic_certification.tex), lines 1–73.
- **M3:** [S.10 comparative proofs](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/revisions/2026-09-16-r7/paper/S10_comparison_proofs.tex).
- **M4:** [S.11 economic proofs and arithmetic account](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/revisions/2026-09-16-r7/paper/S11_economic_proofs.tex), especially lines 44–68; supplement pp. 27–28.
- **M5:** [R7 computational evidence](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/revisions/2026-09-16-r7/paper/05c_r7_evidence.tex) and included tables; main pp. 38–40.
- **M6:** [Inherited approximation theorem](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/revisions/2026-09-16-r6/paper/03_approximation.tex), lines 13–46.
- **M7:** [Stopped preference model](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/revisions/2026-09-16-r6/paper/04_preferences.tex) and [risk-frontier analysis](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/revisions/2026-09-16-r6/paper/04d_risk_frontier.tex).
- **C1:** [Regional decision implementation](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/replication/r7/decision.py) and [deposited output](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/replication/r7/output/decision.json).
- **C2:** [Kernel and action-menu construction](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/replication/r5/contracts.py), lines 17–87.
- **C3:** [Transition and interpolation source](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/replication/r4/solver.py), lines 35–76.
- **H1:** [Earlier R7 report](https://github.com/TrillionniumFoundation/NBO/blob/a5e4c20458947ddffee9cdbb0e0af5ca792d2979/reviews/2026-09-16-econometrica-r7/referee_report.md).
- **H2:** [Prior independent R7 report](https://github.com/TrillionniumFoundation/NBO/blob/a5e4c20458947ddffee9cdbb0e0af5ca792d2979/reviews/2026-09-16-econometrica-r7-independent/referee_report.md).
- **L1:** Quatmann, T., C. Dehnert, N. Jansen, S. Junges, and J.-P. Katoen (2016), *Parameter Synthesis for Markov Models: Faster Than Ever*, [arXiv:1602.05113](https://arxiv.org/abs/1602.05113), Sections 2.1–2.2, 3.3, and 4. Primary text checked on 16 September 2026.
- **L2:** Heck, L., T. Quatmann, J. Spel, J.-P. Katoen, and S. Junges (2025), *Generalized Parameter Lifting: Finer Abstractions for Parametric Markov Chains*, [arXiv:2504.05965v2](https://arxiv.org/abs/2504.05965v2), Sections 1, 3, and 6. Primary text checked on 16 September 2026. The controlled reward problem is not assumed equivalent to that paper's setting.
