# Referee report: Neural Bellman Operators — complete R8
## Participation, portfolio limits, and the economic content of certification

**Date:** 17 September 2026  
**Manuscript author:** Qian QI  
**Reviewed branch:** `revision/econometrica-r8-full-response-2026-09-17`  
**Reviewed commit:** `be77b2a81b4d3a68806c534c1e892d2eb4b1230d`  
**Review branch:** `review/econometrica-r8-economic-stress-2026-09-17-be77b2a`  
**Recommendation:** **Major revision. Acceptance is not warranted in the present form.**

This is an owner-commissioned advisory referee report written to a demanding general-interest economics standard. It is not an appointment by Econometrica or an editorial decision. The recommendation is based on the current complete manuscript, not on the earlier R8 initialization branches.

## 1. Overall assessment and what R8 has actually repaired

R8 is a substantive revision. The active index identifies a new main manuscript and supplement, and the deposit contains the response, executed numerical evidence, and compiled PDFs. I verified the revision head again before depositing this report. The earlier objection that no R8 manuscript existed no longer applies. Nor would it be fair to carry every R7 objection forward simply because that report recommended rejection. [M1, M2]

The finite-model methodological core has become credible. The signed endpoint correction, its comparison with count information, feasible-policy Bernstein evaluation, and the inclusion of policy-bank error are distinct from neural training residuals. The current economic comparison also charges common construction and validation costs. My rerun reproduces the original decision bounds exactly to the reported floating-point values. I have not found a counterexample to the new cardinal-tilt proposition. The numerical and mathematical repairs should be credited, not erased by a demand for a predetermined negative verdict. [M3–M6, D1]

Nevertheless, the paper is not yet persuasive as a general-interest economics contribution. The flagship opposite-position result concerns an unusually tightly specified operating contract. Two provisions now emerge as quantitatively decisive: the inability to surrender the loss-making operation, and the asymmetric limits on the initial risky position. The revision analyzes liquidation *payoffs* and wealth-settlement granularity, but not these two margins. New reviewer experiments below show that modest changes to initial portfolio permissions remove the opposite-choice result at the original region's center, while permitting surrender after the first commitment interval eliminates the relative adjustment option at the inspected contracts. These findings do not invalidate the theorem for its original policy sets. They do require a substantially better economic account of why those policy sets matter. [M3, M4, D2]

A coherent numerical example is not automatically an economic mechanism of broad interest. Conversely, a theoretical example need not be empirically calibrated or invariant to every change in its primitives. The relevant standard here is that the restrictions doing the substantive work must be economically explained and their role analytically distinguished from the preference mechanism. R8 has not yet completed that task.

### Disposition of the previous six substantive objections

| Previous issue | Assessment of the complete R8 |
|---|---|
| F1: finite versus diffusion target | The requested finite-primitive route is substantially supplied. Both regimes and the common menu are retained; the failed old corner and exploratory nested region are disclosed. I do not renew a demand for a diffusion sign that R8 expressly does not claim. Economic defense of the contract remains material, and the new tests identify specific restrictions requiring it. |
| F2: cardinal preference primitive | The specification of `b(u)` and the uniform common-tilt bound answer the identification-of-primitives objection. The adverse `a=1` example remains outside the stated robust family; it is not a counterexample to the proposition. |
| F3: instantaneous first action | Closed for the stated experiment. The first position has positive duration, and the active manuscript correctly distinguishes it from changing a control on a singleton. |
| F4: dynamic mechanism evidence | The requested four-class reoptimization and feature accounting are now supplied. The accounting is not a new causal theorem, but the paper no longer represents it as one. The surrender and constraint margins below are new economic tests, not an assertion that these computations are absent. |
| F5: same-target computation and storage | Substantially closed for the declared decision target. My rerun supports the bound, and my simpler rectangular comparator does not establish a cheaper successful alternative. This is not evidence of neural necessity or universal solver dominance, neither of which the new comparison claims. |
| F6: closest regional literature | The active correspondence correctly recognizes reward-valued parametric MDPs and distinguishes controlled models from parametric Markov chains. An external software performance comparison is not supplied, but R8 does not claim one. This is no longer a demonstrated misdescription of the prior literature. |

These dispositions are based on the active manuscript and response, not only on the author's descriptions of what was changed. [M2–M7]

## 2. R8-E1 — Mandatory operation, not merely liquidation value, is a central economic primitive

**Severity:** Major; publication-blocking unless the contracting rationale and this margin are substantively addressed.  
**Status:** New reviewer counterfactual and quantitative evidence, building on the manuscript's openly stated supersolution property.  
**Locations:** The stopped operating economy, equation labelled `eq:superG`; the finite protocol and dynamic mechanisms; Supplement S.12. [M3, M4]

The paper specifies a first-exit operating contract and explicitly acknowledges that continued operation is costly relative to liquidation. This is not a hidden coding mistake. But varying the multiplier on liquidation payments is not equivalent to varying the *right to liquidate*. The distinction is consequential here.

At the original region center, `(lambda,d)=(0.125,0.425)`, the full-menu class values are:

| Regime | Positive first position | Nonpositive first position | Difference |
|---|---:|---:|---:|
| Adjustment permitted | -0.759029725770272 | -0.759226466454299 | +0.000196740684027 |
| Deliberate adjustment prohibited | -0.794487048712143 | -0.794277721750965 | -0.000209326961178 |

The relative adjustment option is consequently `0.000406067645205`. Meanwhile, immediate liquidation at the initial state gives

\[
G(2,1.25)=0.1\log(1.25)=0.022314355131421.
\]

Thus the optimized mandatory-operation value is approximately `0.7813441` below immediate liquidation with adjustment and `0.8165921` below it without deliberate adjustment. These are comparisons in the manuscript's cardinal utility units, not monetary willingness-to-pay estimates. Negative utility by itself is not objectionable; the relevant comparison is with the explicitly specified payoff from leaving the regime. [M3, D2]

### A counterfactual preserving the first-period commitment

To avoid undoing the corrected positive-duration estimand, keep the first interval of length `1/8` compulsory. At subsequent rebalancing dates, allow the agent to receive the existing payoff `G` voluntarily. No transition, flow payoff, risk class, grid, or financial control is otherwise changed. The continuation recursion becomes

\[
Z_n(x)=\max\{G(x),\max_{a\in A_r(x,n)}[r_n^{\lambda,d}(x,a)+K_n^\lambda(x,a)Z_{n+1}]\},
\quad n\geq1,
\]

with the original sign-restricted action optimization at date zero. This is a changed economic contract, not a purported alternative implementation of the original one.

A new all-state/action/date check finds `G` to be a supersolution of the finite continuation problem throughout the original parameter rectangle. For each of the eight dates, I evaluate `T_n^{lambda,d,a}G-G` at `lambda=0,0.25` and `d=0.45`. The largest interior residual over these checks is `-0.021496645281670`; boundary rows pay `G` exactly in the stored arithmetic. Duration rewards are nonnegative, and the fixed-action backup is affine in `lambda`. These endpoint inequalities therefore cover `lambda in [0,0.25]` and `d in [0.4,0.45]` for the stored finite arrays. Backward induction implies `Z_n=G` at the dates where surrender is permitted. The large interior slack should not be confused with a directed-rounding enclosure of the economic transition constructor. [D2]

A separately implemented optional-stopping recursion confirms the implication. At the original center, with the first interval still compulsory, it gives:

| Regime | Positive first position | Nonpositive first position | Difference |
|---|---:|---:|---:|
| Adjustment permitted | -0.088255899918184 | -0.088768837682621 | +0.000512937764437 |
| Deliberate adjustment prohibited | -0.088255899918184 | -0.088768837682621 | +0.000512937764437 |

The relative adjustment option is zero to the displayed precision, and both regimes choose the positive class. The same equality of the two regime-specific class values occurs at the other two inspected contracts, `(0,0.4)` and `(0.25,0.45)`. If surrender is additionally available at date zero, the optimal value is simply `G(2,1.25)` in all six regime–contract comparisons. I do not infer a uniform zero-option theorem from three optimized rows; the uniform result established by the endpoint check is the continuation supersolution property. [D2]

The continuous benchmark points in the same direction for an independent reason. Adding an operating flow `d<=0.45` to the manuscript's inequality `eq:superG` still leaves an upper bound of `-0.3662`. In an otherwise corresponding voluntary-stopping formulation, the discounted liquidation payoff plus accumulated running reward is a supermartingale, making immediate liquidation optimal. This is an implication of the inherited analytical inequality, not an inference that the finite grids have converged. [M3]

### Why this matters, and what would answer it

The economic choice is therefore partly a choice about coping with an obligation to remain in a costly regime. A preference-adjustment premium inside such a contract may be interesting. But the paper must explain the obligation, who accepts or imposes it, and why the outside option is available at a resource or preference boundary but unavailable at an ordinary decision date. Calling the stopping rule a primitive is mathematically sufficient to define a value function; it does not establish the economic relevance of the particular restriction producing the result.

A satisfactory revision should supply a concrete theoretical contracting rationale, including participation or commitment, and analyze a surrender margin such as a termination charge or a minimum operating term. It should retain the original contract and the adverse free-surrender comparison. It should determine when the relative option and opposite-position region survive, and connect that condition to the relevant duration and preference-state incentives. There is no requirement that free surrender preserve the original conclusion, or that every theoretical contract be empirically calibrated. A response limited to repeating that liquidation incentives were disclosed would not address the new quantitative result.

## 3. R8-E2 — The flagship comparison is between binding long and short limits

**Severity:** Major for the economic interpretation and robustness of the central example.  
**Status:** New, matched-menu reviewer experiments.  
**Locations:** The feasible control box, the risk-class definition, and the regional decision tables. [M3–M5]

The class definition is positive versus nonpositive risky exposure, not risky participation versus a risk-free position. In my full-target solutions at all three inspected contracts, the initial optimizers are

\[
(c,\theta,\pi)_+^{\rm adj}=(0.8,0.2,0.8),\qquad
(c,\theta,\pi)_-^{\rm adj}=(0.8,0.2,-0.5),
\]

and the same consumption and risky-share limits with `theta=0` in the no-deliberate-adjustment regime. Both competing positions carry risky exposure; all reported initial financial choices are at their respective limits. The interior mean–variance/preference-hedging formula is consequently not a direct characterization of these particular optimizers. The manuscript correctly states the interior qualifications, but the economic discussion should make the realized binding constraints equally prominent. [M3, D2]

This is not a complaint that the action mesh merely missed zero. I scanned 653 risky positions within the original limits, including zero and positions immediately on either side, using every distinct common-mesh consumption–adjustment pair and the original optimized continuation. The scan did not improve any of the six original class pairs beyond rounding. This is a negative result for the proposed within-box diagnostic, not a proof of optimality over every continuously varying control. It must be retained alongside the adverse tests. [D2]

### Small, explicit changes to the first-period permissions

Next, leave every later-date menu, the settlement lottery, cardinal preferences, operating benefit, and original action unchanged. At the first date, add the existing common consumption–adjustment pairs combined with one additional risky share. Existing frozen proposals remain admissible. Thus this is an exactly defined finite first-period menu expansion, not an uncontrolled full-horizon recalibration. The previously optimized continuation is still the correct continuation of the changed problem.

At the original region center:

| First-period menu | Adjusted class difference | No-adjustment class difference | Relative option |
|---|---:|---:|---:|
| Original | +0.000196740684 | -0.000209326961 | +0.000406067645 |
| Add `pi=0.82` | +0.000554759104 | +0.000178901666 | +0.000375857438 |
| Add `pi=-0.51` | -0.000011968637 | -0.000442988698 | +0.000431020061 |

A two-percentage-point extension of the initial long limit produces positive first positions in both regimes. A one-percentage-point extension of the short permission produces nonpositive positions in both regimes. The latter adjusted difference is about `-1.197e-5`, far larger in magnitude than the original per-class arithmetic allowance. These are direct first-action evaluations under a changed feasible menu; the original certificate is not being transferred without an error account. [D2]

The relative adjustment option remains positive in both interventions. That fact is important: these experiments do **not** refute the option mechanism, the original sign theorem, or the existence of another region between shifted indifference loci. They do show that the highlighted opposite-position conclusion at its original center is conditional on tightly specified asymmetric portfolio permissions. Wealth-grid robustness alone does not address this dependence. Neither does a common-cardinal-tilt theorem for a separate two-stage economy.

A satisfactory response should explain the economic source of the long and short limits and map the two regime-specific switching boundaries against those permissions while preserving the decision horizon. An analytical comparison using one-sided value sensitivities or appropriate constraint multipliers would help distinguish a change in preference incentives from a change in the price of a binding permission. It is not necessary to prove invariance to arbitrary limits. It is necessary to show where the flagship conclusion is an economically consequential preference-adjustment result rather than a thin interval selected between two constraint-sensitive value surfaces.

The wording should also continue to distinguish a positive position from risk taking itself. A position of `-0.5` is not absence of risk. Likewise, the no-deliberate-adjustment experiment retains stochastic preferences; it is not a constant-preference-state economy.

## 4. The computational result survives a new adverse comparator

I attempted a simpler same-target alternative rather than assuming the count/chord comparison was sufficient. The reviewer implementation uses the reset upper recursion

\[
B_n^I(x)=\max_{a,e\in\{a_I,b_I\}}[r_n^{e,d}(x,a)+K_n^e(x,a)B_{n+1}^I]
\]

with the same full target, first-action restrictions, and deposited feasible-policy bank. It subdivides only the law-mixture interval and uses convex interpolation in the operating benefit. The construction is the rectangular relaxation already discussed in the manuscript, not a claimed new algorithm or an implementation of an external verification system. [M6, D3]

| Equal law-mixture cells | Adjusted lower difference | No-adjustment upper difference | Both signs pass? |
|---:|---:|---:|:---:|
| 1 | -0.000021539744 | +0.000150973194 | No |
| 2 | +0.000023567523 | +0.000049070988 | No |
| 4 | +0.000046128809 | -0.000001868898 | Yes |

The entries include `2e-7` padding per difference, as in the R8 comparison. The four-cell upper/restriction computation took approximately `7.68` seconds in the deposited reviewer run, excluding common lower-bank construction. This is a serial component diagnostic, not a matched end-to-end software ranking. It does not establish a cheap successful one-cell alternative that would erase the chord's contribution. [D3]

My separate rerun of the author's complete contest gives exactly the original full-bank bounds

\[
\Delta^{\rm adj}\in[0.0000686948833572,\,0.0003247296453481],
\quad
\Delta^{0}\in[-0.0003696772643877,\,-0.0000528012509051].
\]

Both chord and count pass. The mesh-only lower bank also passes against the unchanged full-menu upper target. The rerun totals were `15.274`, `21.793`, and `18.967` seconds for full-bank chord, full-bank count, and mesh-bank chord respectively. The author's deposited totals are different because they were measured in a different execution environment. Neither set should be described as independent-machine medians. [M5, D1]

Accordingly, I withdraw the old lack-of-a-same-target-comparison objection. The demonstrated result is an attributable gain from a compressed upper construction in the declared task. It is not a new neural-learning speedup: no network was trained for these arms, and the non-neural lower bank succeeds. The paper now makes that distinction. Its broad architectural title should not obscure where the actual incremental contribution lies, but the absence of neural necessity is not by itself a mathematical defect.

The literature comparison is also materially improved. Quatmann and coauthors treat parametric Markov models including MDP and reward formulations; Heck and coauthors study dependency-sensitive lifting for parametric Markov chains. R8's state/date and cemetery-state correspondence and its information-order distinctions are therefore relevant. The internal comparator is not a performance benchmark of those complete systems. I found no basis in this audit to renew the prior mischaracterization charge or to pronounce an exhaustive priority result. [M7, W1, W2]

## 5. What the next revision must establish

The next response should be organized around R8-E1 and R8-E2, not another undifferentiated list of successful program executions. For each, it should state the changed economic primitive, preserve the original experiment, reoptimize the relevant policy classes, and explain the movement of the original switching region. A justified noncancellable contract and economically meaningful portfolio permissions can answer the critique; a new favorable rectangle without an explanation of the old one's movement cannot.

The new economic analysis should remain tied to the strongest valid computational result. The signed compression, total policy-bank error, positive-duration estimand, and cardinal-tilt theorem should be retained. So should the adverse mesh-only, structural-solver, wealth-granularity, and cardinal examples. There is no reason to remove these results or to abandon the research program. There is also no reason to treat an exact finite-array certificate as resolving whether the certified contract is the economically relevant one.

Two narrower presentation corrections would improve the next submission. First, put the actual initial class optimizers and their binding constraints beside the flagship decision table. Second, distinguish the exact mathematical settlement protocol, the stored floating-point model, and any other economic target in one error-account statement. S.12 already excludes kernel-construction error from its arithmetic allowance; selected-control replay supports implementation consistency but is not an independent interval enclosure of every transcendental operation in that constructor. This is a scope limitation already disclosed, not a newly demonstrated numerical failure. [M3–M5]

My recommendation is therefore substantive major revision, not acceptance after exposition alone. The numerical core earns a serious further hearing. The economics must now explain the restrictions that the new diagnostics show are doing decisive work.

## 6. Review scope and reproducibility

I inspected the active entry points, new R8 theory and response, inherited operator/approximation/transition and risk arguments relevant to the claims, the replication sources, deposited arrays and summaries, and text from the compiled main and supplement. I visually checked selected rendered pages, including the dynamic-mechanism table and the supplementary streaming/arithmetic discussion. The verified PDFs have 55 and 33 pages. I did not independently re-prove every inherited model or recompile the PDFs in this review.

The executed work comprises the author's 60-model/240-class/720-point validation, the primitive robustness program, the full original decision contest, and the new reviewer economics and rectangular experiments. The dense rerun's maximum count discrepancy was zero; its minimum chord-minus-count coefficient was `-2.220446049250313e-16`; its maximum policy replay discrepancy was `4.440892098500626e-16`. The full contest's maximum direct selected-policy discrepancy was `1.3322676295501878e-15`. The cardinal family bound reproduced as `0.00041738027380697413`. These are tests of implementations and numerical constants, not substitutes for the proofs. [D1]

The new reviewer code imports the author's hash-pinned transition constructor and kernels. It is independently written experiment and recursion code, **not** a wholly independent economic discretization. Its within-box search, menu extensions, all-state surrender check, optional-stopping recursion, and rectangular comparison are separately identified. No historical network was retrained, no 97/145-wealth-node spatial run was rerun, and no continuous-state convergence or external verification-software benchmark was performed. Those historical results remain attributed to the author's deposit.

The evidence package records nine runtime-input hashes, the two protected manifest identities, the original artifact provenance, and checks on 23 deposited numerical output files and the two PDFs. The author-program reruns took place in a separate working copy; the repository's scientific inputs were not modified. The review adds only files in its own review directory.

## 7. Sources and deposited evidence

All manuscript paths below refer to the reviewed commit identified above; they are unchanged scientific inputs in this review branch.

**M1.** `REVISION_INDEX.md`; `ECTA_R8.tex`; `SUPP_R8.tex`; R8 `build_manifest.json`.  
**M2.** `revisions/2026-09-17-r8-full-response/response_to_referee.md`; prior report `reviews/2026-09-17-econometrica-latest-substantive/referee_report.md`.  
**M3.** `revisions/2026-09-17-r8-full-response/paper/04_preferences.tex`, especially the control box, liquidation payoff, and `eq:superG`.  
**M4.** Same paper directory: `04g_decision_economics.tex` and `S12_full_response.tex`, including the cardinal-tilt proof, finite protocol, and arithmetic boundary.  
**M5.** Same paper directory: `05d_decision_evidence.tex` and `table_r8_*.tex`; `replication/r8/output/decision_contest.json`, `mechanisms.json`, and spatial outputs.  
**M6.** Same paper directory: `04e_comparative_oracles.tex`; inherited `revisions/2026-09-16-r6/paper/04c_kernel_transfer.tex` and R7 S.10–S.11 arguments.  
**M7.** R8 `04h_literature_correspondence.tex`, introduction, and conclusion.  
**D1.** This directory: `reviewer_results.json`, author-rerun and provenance sections.  
**D2.** This directory: `reviewer_results.json`, economic-stress section; executable `reviewer_checks.py --mode economics` regenerates the detailed rows.  
**D3.** This directory: `reviewer_results.json`, rectangular-comparison section; executable `reviewer_checks.py --mode rectangular` regenerates the detailed cells.  
**W1.** Quatmann, Dehnert, Jansen, Junges, and Katoen (2016), *Parameter Synthesis for Markov Models: Faster Than Ever*, arXiv:1602.05113, especially model/reward definitions and parameter lifting.  
**W2.** Heck, Quatmann, Spel, Katoen, and Junges (2025), *Generalized Parameter Lifting: Finer Abstractions for Parametric Markov Chains*, arXiv:2504.05965.
