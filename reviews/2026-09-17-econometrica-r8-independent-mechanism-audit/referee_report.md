# Referee report: Neural Bellman Operators — independent audit of complete R8
## A valid numerical certificate is not yet a convincing economic mechanism

**Date:** 17 September 2026  
**Journal standard:** Econometrica; owner-commissioned advisory review, not an official journal appointment or decision.  
**Recommendation:** **Reject in its present form. The next scientific revision requires a substantive economic result, not another round of exposition and successful program executions.**  
**Reviewed manuscript:** `revision/econometrica-r8-full-response-2026-09-17`, commit `be77b2a81b4d3a68806c534c1e892d2eb4b1230d`.  
**Historical review retained as branch parent:** `8c20474bca5b7388f5ba4640ec165f1ad8f5e91a`.  
**New review branch:** `review/econometrica-r8-independent-mechanism-audit-2026-09-17-be77b2a`.

## 1. Manuscript identity, recommendation, and evidentiary standard

The latest *complete manuscript* inspected is R8, not R9. At the branch checks for this review, `revision/econometrica-r9-contract-response-2026-09-17` still pointed to `8c20474...`, the head of the preceding R8 review. The GitHub comparison from `be77b2a...` to that head contains four added review files and no change to scientific inputs. A revision branch name is not a manuscript revision. This report therefore evaluates the completed R8 and does not pretend to evaluate an unwritten R9. [M1, P1]

R8 is substantially better than the earlier papers described in the historical reports. It distinguishes the finite economic protocol from a diffusion; fixes the positive-duration interpretation of the first position; declares the cardinal preference primitive; includes four-class dynamic reoptimization; and charges common work in a same-target certificate comparison. These repairs matter. I do not find a basis for alleging that its principal signed-chord theorem is false, that the count recursion is an admissible original policy, or that the current paper claims a demonstrated neural-training speedup from its certificate experiment. It makes none of the latter two mistakes. [M2–M6]

My negative recommendation is instead about the contribution that remains. The strongest new mathematical object is a particular compression of a finite-horizon transition-parameter upper bound. Its economic demonstration is an extremely specific committed operating contract with asymmetric portfolio permissions. The primitive theorem used to motivate the adjustment mechanism operates in a materially different economic regime; in particular, its positive-risk class adjusts the preference index in the opposite direction from the documented initial optimizer in the full dynamic example. The paper has yet to turn these distinct objects into a general-interest economic result. [M3–M6, P2]

The previous complete-R8 report recommended major revision. I agree with its acknowledgment of the mathematical repairs and its substantive concerns, but reach a stricter editorial assessment: acceptance or a routine revise-and-resubmit cannot be justified by this package. This is not a finding of mathematical fraud, nor an argument that the research program should stop. It is a judgment that the current combination of a useful numerical construction, an illustrative primitive inequality, and a restriction-sensitive example has not cleared the contribution threshold.

The journal's stated scope covers theoretical, empirical, abstract, and applied economics. An empirical calibration is therefore not a mandatory condition for this theoretical paper. The condition is an important and rigorous economic contribution. The particular threshold judgment above is mine, not a numerical rule stated by the journal. [W1]

### What was independently executed

I wrote and ran the accompanying standard-library program without importing the author's code. It constructs 24 small rational finite MDPs, each on two parameter intervals, for **48 model–interval cases**. Across horizons one through six, it checks **4,152 exact rational inequalities** and **3,240 common-parameter point-order chains**, with signed rewards, nonzero terminal rewards, and substochastic kernels. It also performs 65-digit Decimal calculations for 27 primitive probability–cost–tilt combinations and the adverse tilt examples. All checks passed. These tests support, rather than undermine, the inspected upper-bound arguments. They are not proofs of the general theorems. [E1]

The full 1,568-action dynamic economy, neural training, spatial refinement, and manuscript PDFs were **not** rerun or recompiled in this review. Repository source was read through the GitHub connector; a local clone was unavailable in this execution environment. All dynamic portfolio, surrender, timing, and grid observations below are explicitly attributed to the author's deposit or the preceding review. They are not disguised as fresh independent numerical solves. The new independent contribution of this audit is the exact-arithmetic stress test, the preference-direction diagnosis, and the analytical closure criteria below. [E1, E2]

## 2. Disposition of the repaired objections

| Issue | Assessment in this review |
|---|---|
| Finite versus diffusion target | R8 explicitly takes the finite-protocol route. I do not demand a diffusion sign it no longer asserts. The separate constructor-versus-stored-array boundary is discussed below. |
| Singleton initial action | Repaired for the executed experiment. A one-eighth-year commitment is not a control changed at a single instant. |
| Cardinal normalization | Repaired as a specification issue: `b(u)` is a substantive preference over preference states. Its relevance to the dynamic mechanism remains a contribution question. |
| Count/chord validity and total error | The inspected inductions are coherent under their stated assumptions. The independent rational checks found no counterexample. |
| Same-target accounting | The complete R8 comparison includes common construction, anchors, lower evaluation, arithmetic auditing, and replay. The old absence-of-a-matched-comparison charge should not be repeated. |
| Prior regional methods | The paper now recognizes the relevant parameter-lifting and information-relaxation correspondences. This review does not establish an exhaustive priority claim or an external-software performance ranking. |

The first four judgments come from the active source, including the inherited material actually imported by `ECTA_R8.tex` and `SUPP_R8.tex`, not from treating an author response as the manuscript. [M1–M7]

## 3. R8-I1 — The primitive mechanism and the executed mechanism are not yet connected

**Severity: major; central contribution objection. New analytical diagnosis, not a counterexample to the cardinal-tilt proposition.**

The uniform cardinal-tilt theorem is a valid sufficient inequality for its stated two-stage family. Its economic content should be examined more carefully than the sign of the final option contrast. Let

\[
\Phi_\sigma(\theta)=F_\sigma(\theta)-F_\sigma(0)+a\theta-\tfrac12k\theta^2,
\qquad -0.2\leq\theta\leq0.2.
\]

Supplement S.11 establishes strict concavity and a negative positive-class shadow throughout the probability interval:

\[
-3.118\leq g_+\leq-1.482,
\qquad g_-=2(1-\log 2)=0.61370563888\ldots.
\]

Consequently, throughout the **entire** advertised family, not merely at sampled optimizer rows,

\[
\Phi_+'(0)=g_++a\leq-1.232<0,
\qquad
\Phi_-'(0)=g_-+a\geq0.36370563888\ldots>0.
\]

Strict concavity and the availability of both signs of adjustment imply unique optima with

\[
\theta_+^*<0<\theta_-^*.
\]

This deduction needs no numerical optimizer: a small negative adjustment improves the positive-class objective, and its decreasing derivative precludes a nonnegative maximizer; the reverse argument applies to the other class. The bounds used here are the paper's adversely rounded, analytically justified constants. [M6]

The independent high-precision calculation at `(p,k,a)=(0.08,40,0)` gives

\[
\theta_+^*=-0.0464338126712310\ldots,
\qquad \theta_-^*=0.0145613501634963\ldots,
\]

and a relative option of `0.0488283664668915...`. The new robust lower bound reproduces as `0.000417380273806973...`; the tiny last-digit difference from the deposited floating-point evaluation is immaterial. The adverse tilt `a=1` reproduces a relative option of `-0.0139197656336055...`. These computations verify the specification rather than refute it. [E1]

By contrast, the preceding full-R8 review records, at the original center and the other two inspected contracts, the adjusted initial optimizers

\[
(c,\theta,\pi)_+=(0.8,0.2,0.8),
\qquad(c,\theta,\pi)_-=(0.8,0.2,-0.5).
\]

Both classes increase the preference index at the positive adjustment limit. Those are historical dynamic solves, not new ones in this audit. Further, the full dynamic cost is `k=2`, outside the primitive theorem's `[20,80]` family. The two-stage adjustment changes a preference level; dynamic adjustment is a drift. Their magnitudes should not be equated. The **direction of movement of the index**, however, is a meaningful comparison. [M3, M6, P2]

There is no logical contradiction. The manuscript explicitly warns that the two-stage family is not a calibration of the stopped economy. That caveat is correct. But the caveat does not provide the missing economic explanation. The primitive positive-class premium rewards a reduction in risk aversion in response to a particular downside consumption lottery. The executed initial adjustment instead raises the index in both competing risky positions, with endogenous consumption, duration, boundary exposure, and cardinal state payoffs. A common positive sign of a four-value contrast does not show that the same mechanism is operating.

R8's feature and reoptimization identities are useful accounting. The author correctly refuses to call them invariant causal shares. They nevertheless do not imply a sign or an economically interpretable sufficient condition for the relative option in the full stopped model. In particular, the response reports that removing the baseline reference-state payoff nearly removes the dynamic relative option. That result makes the specific preference-state incentive more important to explain, not less. [M2, M4]

**Required scientific response.** Derive a sufficient condition in the dynamic economic class actually used for the headline decision, or construct and justify an explicit connecting family. It must account for the sign of deliberate adjustment, the class-specific continuation incentive, and endogenous exit. On the finite menu, one-sided action-value differences are preferable to imposing smooth interior first-order conditions where the optimizer binds. Report the class-specific adjustment direction and its continuation contribution beside the flagship sign certificate. The original primitive theorem should be retained; merely enlarging its table or repeating that it is a separate example would not close this objection.

## 4. R8-I2 — Participation and commitment remain substantive, not semantic, restrictions

**Severity: major. This carries forward R8-E1 from the preceding report; the stopping-penalty analysis below is an additional analytical clarification.**

At the original center `(lambda,d)=(0.125,0.425)`, the preceding review reports mandatory-operation class values of `-0.759029725770272` and `-0.759226466454299` with adjustment, and `-0.794487048712143` and `-0.794277721750965` without deliberate adjustment. Immediate liquidation gives `G(2,1.25)=0.022314355131421...`. Relative to each regime's best class, the utility gaps are approximately `0.7813441` and `0.8165921`. These are cardinal payoff comparisons, **not monetary participation payments**. Negative utility alone is not the problem; the outside-option comparison is. [P2]

The same report changes only the right to surrender after the first compulsory interval. At the center it obtains the same class values in both regimes, `-0.088255899918184` and `-0.088768837682621`, hence the same positive class difference `0.000512937764437` and zero relative adjustment option to displayed precision. Permitting surrender at date zero gives the liquidation payoff. These are changed-contract results, not counterexamples to the original mandatory-operation theorem. The prior all-state supersolution check and its arithmetic scope should remain visible. [P2]

An economic model may legitimately impose a noncancellable commitment. It need not allow free surrender. But calling that commitment a primitive does not explain the participation arrangement, the source of the obligation, or the restrictions on transferring resources into the contract. An unrestricted up-front cardinal transfer can repair a participation inequality without changing conditional investment choices; this observation alone is not a substantive contracting explanation. A monetary implementation would require the corresponding wealth and utility effects and a financing arrangement.

A useful next experiment is available within the paper's own method. Allow voluntary surrender at dates after the first commitment interval, with a nonnegative **cardinal** penalty `q`; retain mandatory boundary liquidation and terminal settlement without that voluntary penalty. For each class and adjustment regime, write

\[
W_\sigma^r(q)=\max_{p\in\mathcal P_\sigma^r}\{B_p-qH_p\},
\]

where `H_p` is discounted incidence of voluntary surrender and `B_p` includes all other payoffs. The extended policy set is fixed when `q` varies. In the finite model this is a maximum of finitely many affine functions. It is decreasing, convex, and one-Lipschitz because `0<=H_p<=1`. At differentiability points,

\[
\frac{d}{dq}(W_+^r-W_-^r)=-(H_+^r-H_-^r).
\]

Thus the penalty can move the risk boundary; its direction depends on class-specific surrender exposure. A general positive-option conclusion does not follow from the envelope identity alone.

There is also a simple finite recovery condition. For fixed remaining primitives and regime, let `W_n^{mand}` be the mandatory-operation continuation. Define

\[
q_* = \max_{1\leq n<N,\ s\text{ interior}}[G(s)-W_n^{mand}(s)]_+.
\]

For `q>=q_*`, backward induction gives the mandatory continuation at every eligible surrender date: `G-q` never exceeds it, and choosing continuation reproduces it. With the first interval compulsory, the original class values are recovered as well. Bounded payoffs ensure a finite sufficient penalty. A uniform version takes the supremum over the compact parameter set and both regimes. This is a sufficient recovery bound, not the smallest penalty preserving a reversal, and it does not solve participation.

Importantly, the new surrender action has reward `G-q` and zero continuation kernel. It therefore fits the paper's finite affine-reward and affine-transition framework. The missing experiment is not blocked by an incompatibility with its certificate machinery.

**Required scientific response.** Specify an economically motivated commitment and participation arrangement; map the two risk frontiers over a meaningful penalty or minimum-term range; show where a certified preference option survives. Preserve the original mandatory contract and the adverse free-surrender results. A favorable sign obtained only by making the surrender penalty arbitrarily large would recover the old assumption rather than explain it.

## 5. R8-I3 — The headline reversal is a comparison between binding permissions

**Severity: major for economic interpretation. The numerical evidence is inherited from R8-E2, not newly generated here.**

The actual initial comparison is a long position at `0.8` against a short position at `-0.5`, with consumption at its upper bound and, when allowed, adjustment at its upper bound. The nonpositive class is not a risk-free class. The interior mean–variance/preference-hedging formula is not a characterization of these boundary optimizers. R8 qualifies that formula correctly; the central economic discussion should make the realized binding constraints equally prominent. [M3, P2]

The preceding report retained a negative diagnostic result: a dense within-box first-position scan did not materially improve the six inspected class pairs. The adverse finding was instead a precisely defined expansion of the first-period menu, holding all later menus and continuation values fixed:

| Initial permission at the original center | Adjusted difference | No-adjustment difference | Relative option |
|---|---:|---:|---:|
| Original menu | 0.000196740684 | -0.000209326961 | 0.000406067645 |
| Add risky share `0.82` | 0.000554759104 | 0.000178901666 | 0.000375857438 |
| Add risky share `-0.51` | -0.000011968637 | -0.000442988698 | 0.000431020061 |

The relative option stays positive while the opposite-position conclusion disappears at the original center in either direction of permission expansion. The interventions do **not** refute the original certificate, establish failure at every parameter point, or rule out a shifted region of opposite positions. They establish that the highlighted center is sensitive to small, transparently specified changes in binding permissions. [P2]

The implication is not that a theoretical result must be invariant to every portfolio constraint. It is that the economic source and value of these particular constraints must be part of the result. A graph of another selected rectangle would not identify that role. Finite differences between the displayed menus are secants for changed finite targets, not continuously estimated constraint multipliers; they must not be relabeled as derivatives without further work.

**Required scientific response.** State the source of the long and short limits, keep the initial commitment horizon fixed, and map both switching boundaries against those limits. Distinguish a relative adjustment premium from an opposite-choice region. Establish whether an interpretable range of contracting and portfolio permissions supports the same qualitative mechanism. Reoptimize the correct changed target and preserve negative results. An empirical estimate of every bound is not mandatory, but arbitrary bounds cannot carry the paper's economic interpretation without analysis.

## 6. R8-I4 — The numerical contribution is real, but its demonstrated scope is narrow

**Severity: major for the claimed general-interest contribution, not a finding of a false theorem.**

The signed-chord calculation has a clear algebraic identity behind it. Mixing endpoint backups creates a cross term involving `(K_a-K_b)(v_b-v_a)`. Endpoint supersolutions remove the two nonpositive residual terms; positivity and a maximum over the endpoint propagations control the remaining correction. The count proof keeps the current action common across conditional endpoint branches. The short-horizon and endpoint cases in S.10 are handled explicitly. [M5, M6]

The independent exact-rational audit checks coefficientwise count/chord and count/rectangular orderings, fixed-policy lower evaluation against the common-parameter optimum, and the stated total coefficient-error estimate. It includes local intervals `[1/4,3/4]`, not only the original endpoint pair. It found no violation. Its modest finite examples are not a replacement for the proof or a benchmark against the production sparse implementation. [E1]

The paper's own complete-R8 summary reports total times of `10.596131` seconds for full-bank chord, `16.468749` for full-bank count, and `13.788331` for mesh-only lower-bank chord against the same full target. Both upper methods yield the same successful reported decision margins. These are single serial observations with common costs charged, not medians, confidence intervals, or measurements newly produced by this audit. They demonstrate an attributable saving for that workload. [M7]

The theory's action-wide application counts, `4H-6` against `H(H+1)-2` for the specified incremental upper constructions, are also useful. But those counts are not a lower bound on every alternative algorithm, a solution to state-space complexity, or evidence that an approximate neural endpoint can be certified cheaply. The current economic experiment uses exact finite-model endpoint optima; its mesh-only lower bank succeeds. The paper now acknowledges all of this. Repeating the old neural-necessity objection as though it were an undisclosed defect would be unfair. [M4–M7]

The contribution question remains: what economic inference becomes available, reliable, or materially less costly because of this compression? The current strongest answer is a carefully certified, low-dimensional contract example whose substantive interpretation still faces R8-I1–I3. The broader neural, recursive, equilibrium, and quadratic examples do not automatically strengthen the incremental transition-law result simply because they inhabit the same manuscript.

Parameter lifting and information relaxation supply relevant prior frameworks. R8's correspondence is a meaningful improvement, but the internal chord/count experiment is not a performance comparison with the complete external systems. The inspected primary sources support that distinction; they do not justify either an exhaustive priority claim for NBO or a claim that existing software already dominates it. [M2, M5; W2–W4]

**Required scientific response.** Establish a consequential economic use for the transition-law method and identify exactly which new theorem or computation delivers it. Retain the controlled same-target comparison and unfavorable neural/structural controls. Where a scalability claim is intended, vary the horizon and target size with full construction, lower-bank, validation, and memory costs included. A neural-independent contribution is acceptable; the paper need not manufacture neural indispensability. What is missing is a sufficiently important economic payoff, not an obligatory victory for a particular architecture.

## 7. R8-I5 — Keep the exact protocol, stored model, and other targets separate

**Severity: bounded verification/presentation issue. Already disclosed in R8 and noted previously; not a new numerical refutation.**

Supplement S.12 explicitly scopes its `1e-7` per-class allowance to computations relative to stored transition and reward arrays. It excludes an enclosure of the economic transition constructor's logarithms, square roots, exponentials, boundary fractions, and settlement weights. Selected-policy replay is valuable implementation evidence, but it is not an outward-rounded uniform constructor bound. This is distinct from diffusion error: an exact finite settlement protocol and its floating-point stored realization are already two objects. [M4, M7, P2]

There are two clean presentations. One is to declare the stored arrays themselves the exact finite economic object. The other is to keep the analytic finite lottery as the exact object and add a constructor error budget. The current qualifications point toward this distinction but should be collected at the flagship certificate rather than left for a reader to reconstruct.

For example, with the same admissible controls, uniform row reward error `delta_R,n`, kernel row-l1 error `delta_K,n`, a bound `B_{n+1}` on the target continuation, and stored row mass bounded by `beta_hat,n`, the elementary recursion

\[
E_N=\delta_g,\qquad
E_n=\delta_{R,n}+\delta_{K,n}B_{n+1}+\widehat\beta_n E_{n+1}
\]

bounds fixed-policy and optimal-value differences. It follows by adding and subtracting the stored kernel applied to the target continuation and using nonexpansiveness of action maximization. Separate class errors then enlarge the difference certificate.

For the complete R8 margins currently reported, the smaller absolute directional margin is `5.2801250905127e-5`. Hence an **additional equal per-class** transfer error strictly below `2.64006254525635e-5` suffices for both signs. This calculation uses R8's charged allowance, not the slightly different historical threshold quoted for an earlier certificate. It is a required budget, not a measured constructor error. [M4, M7]

There is no evidence here that ordinary floating-point constructor errors actually reverse the decision. I would not turn this disclosure into an invented fatal numerical bug. The remedy is a precise target declaration or a checked error enclosure, not removal of the finite-model theorem.

## 8. Minimum conditions for a persuasive next revision

The publication-blocking concerns are R8-I1–I4. They should not be buried under a count of passed tests. A coherent revision would put the dynamic mechanism, commitment and participation structure, and binding permissions into one economic argument, then apply the strongest valid certificate to that argument. The adjustment-direction result above is a concrete diagnostic to explain, not a reason to discard the two-stage proposition. The voluntary-surrender family is directly compatible with the existing method and provides a disciplined way to investigate the contract restriction. The portfolio-permission frontier separates the robust relative option from the more fragile opposite-choice claim.

The main manuscript should place the actual optimizers and binding constraints next to the headline sign table and give one consolidated target-error account. The theory, historical adverse outcomes, exact structural comparators, and previous reports should all remain accessible. Reorganization does not require deleting evidence or diminishing valid theorems.

An additional favorable rectangle, a larger suite of solver checks, or another statement that all restrictions are primitives would not be a sufficient response. A substantive economic result explaining when the mechanism survives, why the contract is of interest, and what the computational innovation enables could be. On the present record, I recommend rejection rather than acceptance after further exposition.

## 9. Sources and reproducibility

All scientific source paths below refer to `be77b2a81b4d3a68806c534c1e892d2eb4b1230d`; the history source refers to `8c20474...`. `source_inventory.json` records observed Git blob identities. No claim is made that every inherited appendix or compiled PDF was independently verified.

**M1:** `REVISION_INDEX.md`, `ECTA_R8.tex`, `SUPP_R8.tex`.  
**M2:** `revisions/2026-09-17-r8-full-response/response_to_referee.md`; its `paper/01_introduction.tex`.  
**M3:** R8 `paper/04_preferences.tex`, especially `eq:ndu_terminal`, the feasible box, `eq:superG`, and the qualified interior conditions.  
**M4:** R8 `paper/04g_decision_economics.tex` and `paper/S12_full_response.tex`.  
**M5:** `revisions/2026-09-16-r6/paper/04c_kernel_transfer.tex`; R8 `paper/04e_comparative_oracles.tex`.  
**M6:** `revisions/2026-09-16-r7/paper/S10_comparison_proofs.tex` and `paper/S11_economic_proofs.tex`.  
**M7:** R8 `execution_summary.md`; inherited R6 `paper/02_operators.tex` and `paper/03_approximation.tex`.  
**P1:** GitHub branch/ref reads and the commit comparison `be77b2a...` to `8c20474...`; only the four preceding review files differ.  
**P2:** `reviews/2026-09-17-econometrica-r8-economic-stress/referee_report.md`, especially R8-E1, R8-E2, computational comparison, and review scope. Its dynamic numbers are inherited observations, not reruns by this review.  
**E1:** This directory's `reviewer_checks.py` and `reviewer_results.json`; independent exact-rational tests and Decimal primitive checks.  
**E2:** This directory's `README.md` and `source_inventory.json`; execution boundaries and source identities.

**W1:** Wiley / Econometric Society, [Econometrica: Aims and Scope](https://onlinelibrary.wiley.com/page/journal/14680262/homepage/aims.htm), consulted 17 September 2026.  
**W2:** Quatmann, Dehnert, Jansen, Junges, and Katoen (2016), [Parameter Synthesis for Markov Models: Faster Than Ever](https://arxiv.org/abs/1602.05113).  
**W3:** Heck, Quatmann, Spel, Katoen, and Junges (2025), [Generalized Parameter Lifting: Finer Abstractions for Parametric Markov Chains](https://arxiv.org/abs/2504.05965).  
**W4:** Brown, Smith, and Sun (2010), *Information Relaxations and Duality in Stochastic Dynamic Programs*, Operations Research 58(4), 785–801; acknowledged as the information-relaxation foundation in the inspected R6 kernel-transfer section. This review does not claim a new external literature-priority result.
