# Advisory Referee Report: Neural Bellman Operators

**Date:** 18 September 2026  
**Standard of assessment:** Econometrica-style substantive referee review  
**Recommendation:** **Reject in its present form**  
**Latest revision-branch snapshot:** `755b507870b54a100616b0658eba9a031eef2833`  
**Latest complete scientific revision:** R9, `8c1e0472279fb66a2419b63b3e35df028ecfdd78`  
**Review type:** Owner-commissioned independent advisory assessment. This document is not an appointment, report, or editorial decision issued by Econometrica.

## 1. Assessment for the editor

The paper has made real progress. Its finite-model decision target is now explicit; the participation account no longer treats an external transfer as managed CRRA wealth; the statewise enforcement proposition is meaningful; and the unfavorable surrender and permission experiments are retained. The numerical work examined in this review is substantially reproducible. I do not recommend rejection because a training residual was incorrectly declared a proof, because the finite model is secretly a diffusion, or because the participation formula is algebraically wrong. Those would be inaccurate criticisms of this version.

I nevertheless do not find the integrated economic contribution sufficiently established. The primitive preference-adjustment theorem and the central dynamic decision operate through different directions of adjustment. A fresh all-date restriction experiment makes this distinction considerably sharper than an observation about the initial action: at the original central contract, upward-only adjustment reproduces both unrestricted class values, whereas downward-only adjustment reproduces both no-adjustment values. The dynamic result is therefore not evidence that the positive-position class uses the primitive theorem's downward-adjustment channel. A continuation-value decomposition identifies where the numerical gain comes from, but the paper still lacks primitive conditions explaining that dynamic channel and its risk-class differential.

The contracting extension is coherent as a fixed-mandate participation exercise, but its strongest regional result prices an enforcement instrument that renders surrender strictly inactive. The same model also permits a fully compulsory term without separately pricing that commitment. Conditional on that term being selectable and costless, it delivers the same service while avoiding the positive capacity charge. This is not a contradiction of the fixed-contract proposition; it limits what the extension establishes about economically chosen institutions.

Finally, the genuinely promising computational contribution is the signed compression of transition-law information and its precision/work tradeoff. Generic affine-policy envelopes and transfer identities do not supply an additional economic theorem simply by being attached to a participation contract. The remaining task is substantive integration, not another layer of terminology, version labels, or appendices. The recommendation is an assessment of contribution and unresolved interpretation, not a claim that every theorem is false.

## 2. What is actually the latest revision?

The latest named revision branch is `revision/econometrica-r10-dynamic-mechanism-2026-09-17`, at `755b507870b54a100616b0658eba9a031eef2833`. Its sole change relative to its parent is the 65-line workflow `.github/workflows/revision-r10.yml`. There is no `ECTA_R10.tex`, `SUPP_R10.tex`, `replication/r10/run.py`, or completed R10 response/manuscript at this snapshot. `REVISION_INDEX.md` still identifies R9 as the current complete revision. [V1–V3]

The comparison from the R9 scientific commit to this snapshot contains only the preceding R9 review package and the R10 workflow. It contains no modification to a manuscript, numerical constructor, or R9 result. The successful R10 workflow run `35222706049` packages a source archive; its conditional research/build blocks do not execute without the missing source files. The downloaded artifact contains only `build-r10/source.tar.xz` and `build-r10/source_commit.txt`. A successful archive job is not a successful scientific revision. [V2–V4]

Accordingly, this report evaluates the latest complete R9 manuscript inherited by R10, not an invented R10 paper. The absence of a new R10 manuscript is a version-status finding, not an additional mathematical defect in R9. The preceding consolidated R9 report is treated as a set of questions to test, not as authoritative evidence of their answers. [H1]

## 3. Scope, evidence, and repairs that should not be reopened

The principal inputs were the R9 main manuscript and supplement, their TeX entry points and relevant inherited sections, the response and execution summary, the contract implementation, and the preceding R9 review. Particular attention was given to the operator/error account, transition-law chord and count comparison, primitive and dynamic mechanism sections, participation, stopping, permissions, and their associated proofs. The deposited PDFs have 66 and 39 pages respectively; the procurement, surrender, and enforcement tables were also inspected in rendered pages 56–58 of the main manuscript. This is not a claim to have independently re-proved every inherited extension or retrained every historical neural experiment.

The accompanying `reviewer_checks.py` uses the author's pinned finite-array constructor and an independently written Bellman recursion. It preserves the original 1,568 operating actions, including three deposited proposals, on 1,617 states and eight dates, except for explicitly identified directional restrictions and stopping interventions. It reoptimizes both initial position classes rather than evaluating a single frozen policy. It also reconstructs the reachable-state enforcement bank, checks the all-action stopping supersolution, and recomputes procurement values. Results and environment are in `reviewer_results.json`; execution checkpoints are separately retained. This is independent dynamic-programming orchestration, not an independent enclosure of the transition constructor.

The original full/no-adjustment Bellman values agree exactly with the author's recursion in the four focal comparisons. The largest selected-control reconstruction discrepancy is approximately `1.33e-15`. All 633 pre-existing input files checked by the audit retain their hashes. These facts support implementation consistency; they do not bound uncomputed real-arithmetic constructor errors or transfer a conclusion to a diffusion.

Several repairs deserve explicit credit. The positive/nonpositive position classification applies over the first interval of length one eighth of a year, not an isolated control value. The finite randomized-settlement economy is declared to be an economic target in its own right. The payoff from changing the preference index is explicitly cardinal, rather than inferred from a CRRA coefficient alone. The signing grant and surrender charge use a separate additive utility numeraire. The exact fee threshold concerns equality at every reachable continuation node; equality merely at the initial state has a weaker requirement. The first-date continuous risky-share reduction is not presented as continuous optimization of every control at every date. These qualifications are substantive and should be preserved. [M1–M4]

## 4. Major concern M1: The dynamic economic mechanism remains insufficiently established

### 4.1 The primitive and dynamic directions must be distinguished

In the two-stage primitive family, the positive-class adjustment shadow is negative throughout the specified probability interval, with magnitude between approximately 1.482 and 3.118. The nonpositive-class shadow at the baseline is `2(1-log(2)) > 0`. A common cardinal tilt of magnitude at most 0.25 preserves these opposite signs. Together with the stated curvature and cost restrictions, the primitive positive class optimally lowers the preference index while the other class raises it. The positive relative option is a valid result about that family. [M2, P1]

The full dynamic experiment instead uses cost coefficient `k=2`, stochastic preference transitions, liquidation, and continuation values; the primitive family uses `k` between 20 and 80. A primitive level adjustment is not identical to a dynamic drift control. The paper itself correctly says that the dynamic direction is not inherited mechanically. There is therefore no counterexample to the primitive theorem merely because both dynamic initial controls equal `theta=0.2`. The unresolved issue is what positive economic prediction connects that theorem to the dynamic result, rather than a coincidence in the sign of a four-value contrast.

### 4.2 New test: restrict the direction at every date and reoptimize

At `(lambda,d)=(0.125,0.425)`, with the original noncancellable term `m=8`, define `Delta=W_+-W_-`. I recomputed four economies using the same financial controls, transitions, and first-period position classification. The restrictions on deliberate adjustment apply at every date and state, not just to the first action.

| Deliberate adjustment menu | Positive class value | Nonpositive class value | Delta |
|---|---:|---:|---:|
| Original unrestricted menu | -0.759029725770272 | -0.759226466454299 | +0.000196740684027 |
| Upward only, theta >= 0 | -0.759029725770272 | -0.759226466454299 | +0.000196740684027 |
| No deliberate adjustment | -0.794487048712143 | -0.794277721750965 | -0.000209326961178 |
| Downward only, theta <= 0 | -0.794487048712143 | -0.794277721750965 | -0.000209326961178 |

The unrestricted and upward-only relative options both equal `0.00040606764520489946`; the downward-only relative option is zero. These equalities are focal numerical findings at the stored-array target. They are not asserted uniformly over the original parameter rectangle, across every state, or across a continuous control set. They establish that access to downward deliberate adjustment is unnecessary for the headline reversal at this contract. [E1: `directional`]

A response that merely repeats the primitive option bound, the unrestricted positive relative option, or a list of reoptimized sensitivities will not answer this diagnostic. The author needs to explain why upward drift is valuable to both dynamic classes and why its differential value reverses their initial ranking.

### 4.3 A more informative decomposition than the initial action alone

The focal unrestricted first controls are `(c,theta,pi)=(0.8,0.2,0.8)` and `(0.8,0.2,-0.5)`. Hold consumption and risky share at those respective values and compare initial `theta=0.2` with `theta=0`, using the optimized adjusted continuation at date one.

| Initial action-value difference | Positive class | Nonpositive class |
|---|---:|---:|
| Current reward difference | -0.004987520807318 | -0.004987520807318 |
| Continuation-value difference | +0.016423620511671 | +0.016373226238042 |
| Net gain from initial upward adjustment | +0.011436099704353 | +0.011385705430724 |
| Value of future adjustment with initial theta fixed at zero | +0.024021223237518 | +0.023665549865942 |

Thus the current adjustment cost is paid in both classes; the initial action is justified by a larger continuation gain. For this ordered comparison, the difference in the initial-action gains is `0.000050394273628518`, while the difference in future-adjustment values is `0.000355673371576382`. Their sum is the relative option `0.00040606764520489946`. An initial downward action instead has a negative continuation increment in both classes. [E1: `initial_action_value_diagnostics`]

This is an exact accounting of the executed focal action-value comparisons up to floating-point error, not a causal decomposition into invariant shares. The ordering and the fixed financial controls matter. In particular, these entries should not be relabeled as structural percentage contributions. Nevertheless, they isolate an economically important fact: the relative premium is predominantly associated, in this ordering, with access to future adjustment, not merely with the difference between the two observed initial drift choices.

**Required substantive response.** Develop a dynamic result or verifiable primitive sufficient conditions explaining the sign of the continuation incentive and its difference across risk classes, with stochastic preferences, stopping, and cardinal preference-state payoffs present. The theorem need not force the dynamic model into the two-stage mechanism. It must identify the actual mechanism, show its economic domain, and distinguish it from the primitive example. Reproduce the directional test and extend it to a declared neighborhood or give a certified boundary for its failure. A favorable point table alone is not a regional mechanism theorem.

## 5. Major concern M2: Priced surrender enforcement is compared with an unpriced compulsory term

The participation proposition is correct for the stipulated separate-account contract. With outside value `G(x0)`, capacity cost `C(E)`, and an optimally selected initial class, the minimum grant is

$$q^*=[G(x_0)-\max_\sigma W_\sigma+C(E)]_+.$$

For a specified optimizing agent policy with discounted duration `A`, the principal's surplus is `bA-q*`. This correctly avoids comparing a cheap but abandoned service with a fully delivered one. The paper also expressly disclaims optimality over all mandates. These are not omissions to manufacture into errors. [M3, lines 7–39]

The limitation is that minimum term and financial enforcement are asymmetric primitives. Before date `m`, operation is compulsory. The case `m=8` reproduces the noncancellable mandate regardless of `F`. Yet the explicit cost in the model is the cost of capacity `E`, not a separate cost of enforcing or obtaining acceptance of a compulsory term beyond its operating-value effect. [M3, lines 9–13]

The issue can be measured without changing the financial model. At the original center, let `b=0.9`. The outside value is `0.02231435513142098`. Reoptimization gives:

| Regime and mandate | Capacity cost | Operating duration | Minimum grant | Principal surplus |
|---|---:|---:|---:|---:|
| Adjustment, F=0.85, m=1 | 0.01 | 0.890233276156 | 0.791344080902 | +0.009865867639 |
| Adjustment, F=0, m=8 | 0 | 0.890233276156 | 0.781344080902 | +0.019865867639 |
| No adjustment, F=0.85, m=1 | 0.01 | 0.887897935749 | 0.826592076882 | -0.027483934709 |
| No adjustment, F=0, m=8 | 0 | 0.887897935749 | 0.816592076882 | -0.017483934709 |

The first and third rows reproduce the manuscript's positive-cost example. The other rows implement its own hard-term alternative with `E=F=0` and `C(0)=0`. Both operating value and selected duration are unchanged; the grant falls by exactly 0.01. [E1: `procurement`]

This conditional comparison does not establish an unrestricted optimal mechanism, nor does it reverse the example's finding that adjustment can enable mutually acceptable service. It establishes that **when the hard term is selectable, has no independent cost, and C(0)=0, the positive-capacity-cost implementation is dominated by that hard-term alternative for the same service**. A mathematical substitution between two enforcement primitives does not by itself price both instruments economically.

**Required substantive response.** Specify the institutional choice problem. Either fix or constrain the minimum term exogenously and explain the economic question under that restriction, or introduce and discipline a term-enforcement technology/cost and compare it with financial capacity. An endogenous exercise should report delivered service, grants, capacity/term costs, and agent policy selection under the same primitives. Merely adding a carrying cost to `E` does not answer the opportunity cost of a freely available hard term. Conversely, a fixed-term theorem should not be criticized for failing to solve a different, unrestricted contract-design problem; the issue is what additional contribution the paper claims from that restricted exercise.

## 6. Major concern M3: The successful fee box is an implementation region, not an active-surrender explanation

The statewise threshold proposition is a useful result. For the noncancellable continuation `V_n`, an eligible surrender payoff is `G-F`, so a fee above the maximum positive continuation shortfall implements the same continuation values. Adjustment weakly lowers the exact required capacity because it weakly raises continuation values. That policy-inclusion argument is sound under the stated common target and reachable support. [M3, lines 54–88]

I reconstructed the reachable sets and both deposited feasible-policy coefficient banks. The reachable counts from dates zero through eight are

`[1, 30, 100, 203, 342, 495, 637, 735, 833]`.

Coefficient reconstruction differs from the deposit by at most `8.88e-16`. Reapplying the 16 law-subinterval restrictions and the `1e-7` allowance reproduces the sufficient fees for terms one through eight:

`[0.8348592805606002, 0.7642922686416340, 0.6815819738829658, 0.5857509714769409, 0.4741575551445589, 0.3429905146065858, 0.1873940581439002, 0]`.

The first number is below 0.85 by `0.015140719439399764`. Hence throughout the original law/benefit rectangle and the fee interval `[0.85,0.90]`, surrender is strictly inferior at every eligible reachable live node in the original finite target. Both regimes reproduce the noncancellable continuation values; elective surrender exposure is zero and the local fee derivative of operating value is zero. The extra fee dimension does not generate an additional interaction of an exercised surrender option with adjustment in this box. This is a legitimate finite-fee implementation theorem, but its economic content must be stated accordingly. [E1: `enforcement`; M3; M4, Tables XXVIII–XXIX]

It would be equally wrong to infer that active surrender can never coexist with opposite position rankings. My independent recursion reproduces the author's stronger pointwise evidence:

| F, with m=1 at the original center | Delta with adjustment | Delta without adjustment | Relative option |
|---|---:|---:|---:|
| 0.00 | +0.000512937764437 | +0.000512937764437 | 0 |
| 0.70 | +0.004305649785109 | +0.007717507548133 | -0.003411857763024 |
| 0.80 | +0.000196740684027 | -0.000191857347061 | +0.000388598031087 |
| 0.85 | +0.000196740684027 | -0.000209326961178 | +0.000406067645205 |

At `F=0.80`, the positive no-adjustment class has discounted surrender exposure `0.06899514599046101`; the other three class/regime exposures are zero. Thus the center does have active surrender and opposite rankings. But at the published adverse corner `(lambda,d)=(0,0.4)` with the same fee, the independently reoptimized no-adjustment difference is **positive**, `0.0013923796303004776`; the adjusted difference is also positive, `0.00006889488335726224`. The original rectangle's opposite-sign assertion consequently fails there. R9 already discloses these facts and receives credit for doing so. [E1: `surrender`, `adverse_fee_080_corner`; M4, Table XXVII]

Free surrender is also not a numerical artifact found only in the focal table. The recomputed all-action endpoint supersolution test has largest interior residual `-0.02149664528166964` at the maximal benefit, with zero boundary residual. Affinity in the law and nonnegative duration extend this check over the original law/benefit rectangle. With the first interval compulsory, the focal policies surrender at the first eligible date; the reported `0.9950124791926822` is discounted incidence, not a 99.5 percent probability. [E1: `supersolution`, `surrender`]

**Required substantive response.** Separate three results: implementation of the old mandate by an inactive surrender right; the active-surrender center example; and regional robustness with active surrender. The third has not been established merely by certifying `[0.85,0.90]`. A valuable next result would characterize a region with an exercised termination margin and explain how the ordering changes at its boundaries, while retaining the `F=0.80` adverse corner. Alternatively, develop the welfare/cost implications of an implementation theorem rather than presenting inactive surrender as evidence for a richer active mechanism. This is a demand for added economic content, not for changing a correct numerical sign.

## 7. Major concern M4: The paper still needs a demonstrably integrated contribution

The strongest mathematical component is not the separation of an actor and critic, a reward-feature identity, or the affine-policy participation envelope. It is the signed cross-operator correction for changing transition laws, its relation to count-informed upper coefficients, and the accounting of policy-bank error and work at a fixed decision tolerance. The manuscript now states the relevant distinctions carefully: count is sharper on matched banks; compressed propagation can save work; second-order correction error is not second-order total bank loss; common construction and validation costs must be counted. I do not identify a counterexample to the corrected-chord proof in this review. [C1–C2]

The existing comparison with optimistic linear support is also not absent. Alegre, Bazzan, and da Silva develop successor-feature/OLS transfer for linearly expressible reward tasks. Kim and coauthors' current policy-iteration paper studies fixed-policy neural PDE evaluation and pointwise improvement. Generalized parameter lifting addresses regional dependence in parametric Markov chains. These are relevant primary comparators, but none should be casually declared identical to the paper's controlled finite-horizon signed correction. The manuscript already discusses them. A plagiarism or blanket duplication allegation would be unsupported. [L1–L3; C3]

The editorial problem is the remaining increment. The main paper is 66 pages before a 39-page supplement, yet the central economic mechanism still requires the separation in M1, and the latest contracting additions mainly attach correct optimization identities to stipulated institutions. My request is not an empirical calibration as a prerequisite for theoretical economics, a universal neural speed advantage, or deletion of difficult adverse evidence. It is an integrated result showing what economic question becomes answerable because the computational certificate is available, which substantive primitive inequalities deliver the answer, and where the answer ceases to hold.

The measured audit constructor stores approximately 775 million bytes for this two-state, eight-date target. That is a description of this constructor, not a process peak-memory measurement or an impossibility claim about scaling. The present audit did not rerun the full timing frontier or neural training. Any renewed computational comparison should retain the same-target, same-tolerance discipline already achieved in R8/R9 and should not turn upper-recursion storage savings into unsupported end-to-end or high-dimensional claims. [E1: `constructor`; C2]

## 8. Technical qualifications and reproducibility status

The favorable replay checks do not supply interval enclosures for exponentials, powers, interpolation weights, or all action rows in a real-arithmetic constructor. R9 explicitly distinguishes that error from arithmetic on stored arrays. I retain the distinction rather than call it an undisclosed defect. Similarly, the first-date permission breakpoint theorem changes the first-date risky-share target; the fee certificate does not automatically extend to those enlarged menus. The proof is conditional on finite consumption/adjustment pairs and later finite actions. The current review inspected that target distinction but did not independently regenerate every permission root or the full chord/count certificate sweep. [M3, lines 90–139]

One exploratory attempt used a larger directional point list and was interrupted before completing the intended run. Its log is retained as `exploratory_interrupted_run.log`; it is not counted as a completed regional experiment. The successfully completed production script is the center-only directional test plus the surrender, adverse-corner, replay, supersolution, enforcement-bank, and procurement checks recorded here. The retained execution checkpoints and final JSON identify that scope exactly. No new training, R10 manuscript build, or diffusion experiment is claimed.

A rerun may differ in elapsed time, memory allocation, and last-bit floating-point values. The script's comparison tolerance is `2e-11`; the substantive class differences discussed above are much larger. These are finite-array consistency checks, not replacements for the separate mathematical certificate or its constructor-error budget.

## 9. Conditions for a meaningful reconsideration

| Item | Evidence needed | What would not close it |
|---|---|---|
| M1: dynamic mechanism | A dynamic sign/ordering result under stated economic primitives; all-date directional reoptimization and a declared robustness domain; continuation incentives connected to that result | Repeating the primitive theorem or the positive four-value contrast |
| M2: institutional comparison | Either an economically justified fixed/constrained term, or a comparable term/capacity choice with costs, participation, and delivered service | Pricing capacity while leaving a selectable hard-term alternative unexplained |
| M3: surrender contribution | A clear implementation theorem and its welfare implications, or a separately certified active-surrender region and boundary mechanism | Counting a strictly inactive fee interval as an active-termination robustness result |
| M4: integration | A central economic proposition whose numerical sign/region requires the stated certificate, with matched work/precision evidence | More generic envelope identities, additional labels, or unsupported neural-necessity claims |
| Version and execution | An actual complete revision, response map, immutable source identities, and executed checks for that same candidate | A branch name or successful conditional archive workflow |

The next response should address these items directly without withdrawing valid theorems, suppressing adverse results, or merely lowering the stated ambition. Reorganization may improve exposition, but the missing economic result cannot be supplied by exposition alone. At the reviewed snapshot the rejection recommendation remains warranted.

## 10. Source and evidence register

Repository references below are pinned to immutable commits. Local section names and line ranges refer to TeX sources, not PDF text-extraction line numbers.

**Version evidence**

- **V1:** [Revision index at the reviewed snapshot](https://github.com/TrillionniumFoundation/NBO/blob/755b507870b54a100616b0658eba9a031eef2833/REVISION_INDEX.md).
- **V2:** [Latest revision commit and its sole workflow addition](https://github.com/TrillionniumFoundation/NBO/commit/755b507870b54a100616b0658eba9a031eef2833).
- **V3:** [R9-scientific-to-latest-snapshot comparison](https://github.com/TrillionniumFoundation/NBO/compare/8c1e0472279fb66a2419b63b3e35df028ecfdd78...755b507870b54a100616b0658eba9a031eef2833).
- **V4:** [R10 archive workflow run](https://github.com/TrillionniumFoundation/NBO/actions/runs/35222706049). Downloaded artifact ID `10497729014`, SHA-256 `16be7b1e9c1e7b29e440fafda41ed1419049653baf92083c5d5d855aedd05931`.

**Manuscript and proofs**

- **M1:** [R9 main entry point](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/ECTA_R9.tex) and [supplement entry point](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/SUPP_R9.tex).
- **M2:** [Economic decision, cardinal primitive, and dynamic reoptimization](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r8-full-response/paper/04g_decision_economics.tex), especially lines 7–18, 29–40, 42–67, and 69–99.
- **M3:** [Participation, enforcement, permissions, and target-error account](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r9-participation-permissions/paper/04i_contracting.tex).
- **M4:** [R9 contract evidence](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r9-participation-permissions/paper/05e_contract_evidence.tex), main PDF pages 56–58, Tables XXVI–XXIX.
- **P1:** [Primitive proof and shadow bounds](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-16-r7/paper/S11_economic_proofs.tex) and [cardinal robustness proof](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r8-full-response/paper/S12_full_response.tex).
- **C1:** [Corrected transition-law chord](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-16-r6/paper/04c_kernel_transfer.tex).
- **C2:** [Matched upper-oracle ordering and total error](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r8-full-response/paper/04e_comparative_oracles.tex).
- **C3:** [Literature correspondence](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r8-full-response/paper/04h_literature_correspondence.tex).
- **H1:** [Previous consolidated R9 advisory report](https://github.com/TrillionniumFoundation/NBO/blob/b039099bba4acdef9b0f6c4de38df8aeef01672e/reviews/2026-09-17-econometrica-r9-consolidated-contract-audit/referee_report.md). Its objections were retested, not counted as independent verification.

**New executed evidence**

- **E1:** [Reviewer results](reviewer_results.json), generated by [reviewer checks](reviewer_checks.py); [execution checkpoints](reviewer_checkpoints.json); [scope and provenance manifest](review_manifest.json). The direction experiment and ordered action-value decomposition are additional diagnostics, not just transcriptions of R9 tables.

**Primary literature checked on 18 September 2026**

- **L1:** Alegre, L. N., A. Bazzan, and B. C. da Silva (2022), [Optimistic Linear Support and Successor Features as a Basis for Optimal Policy Transfer](https://proceedings.mlr.press/v162/alegre22a.html), PMLR 162, 394–413.
- **L2:** Kim, Y., M. Kim, Y. Kim, and N. Cho, [Physics-Informed Policy Iteration for High-Dimensional Hamilton–Jacobi–Bellman Equations: Interior Error Bounds without Boundary Data](https://arxiv.org/abs/2508.01718v2), arXiv v2 dated 9 August 2026.
- **L3:** Heck, L., T. Quatmann, J. Spel, J.-P. Katoen, and S. Junges, [Generalized Parameter Lifting: Finer Abstractions for Parametric Markov Chains](https://arxiv.org/abs/2504.05965v2), arXiv v2 dated 4 August 2025, accepted to ATVA 2025.
