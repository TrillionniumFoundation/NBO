# External Referee Report — R47

**Venue perspective:** Econometrica-level numerical and computational methods  
**Article:** *Certified Bellman Operators for Costly Policy Revision*  
**Repository:** `TrillionniumFoundation/NBO`  
**Reviewed branch:** `revision/econometrica-r47-complete-referee-2026-09-26`  
**Equivalent referee-copy branch:** `revision/econometrica-r47-referee-copy-2026-09-26`  
**Reviewed HEAD:** `1987a1f91ff783cd6f24fa7a9ea6a8118f64c56c`  
**Prior external report addressed by the revision:** `reviews/2026-09-25-econometrica-r44/referee_report.md` at `bdfd4e94b74a41ef904158d0061d10a6fcf39c8c`  
**Review branch:** `review/econometrica-r47-numerical-methods-2026-09-26-1987a1f`  
**Date:** 2026-09-26

## 1. Recommendation

**Reject.**

R47 is the strongest and most intellectually coherent version of this project that I have reviewed. It fixes the publication defect of R44, materializes an ordinary journal-formatted manuscript and supplement, and identifies a genuine central theorem rather than presenting repository engineering as the contribution. The restart-price Bellman certificate is a useful construction. The successor-price minimum and the associated price-change slack correctly preserve one common continuation across restarts. The resulting lower bound is valid with controlled atomic transitions and operating ties, and the exact gap identity separates unused initial allowance, transformed-action slack, and price-flow mismatch. The witness-stability and continuation-best repair results also improve the treatment of approximate operating values. The proof-producing implementation and independent readers remain unusually careful.

These are real advances. They do not, however, establish an Econometrica-level numerical method for the problem advertised in the title.

The principal numerical headline—six of twelve primary target hits—substantially overstates the incremental contribution of R47. The original certified portfolio already closed five primary environments: M0, I0, Q0, Q1, and Q3. The retrospective price extension closes those same five and adds only I3. Thus the new method produces **one additional primary closure out of twelve**. I0 is a zero-cost row; Q0 is essentially exact at the root; M0 and Q1 had already crossed the target with the earlier global trees; and Q3 had already closed under the aggregate formulation. The three newly closed tie rows are meaningful evidence that the certificate remains useful at degeneracy, but they are four perturbations of one small, designed four-state/eight-period construction. The fourth tie row remains far from the target.

Seven of the sixteen portfolio rows remain open. The failures are not marginal: M1, M2, M3, I1, I2, Q2, and T3 retain absolute gaps of approximately 0.00716, 0.00872, 0.02463, 0.00505, 0.00274, 0.00115, and 0.09321, respectively, even after intersecting all valid old and new endpoints. The price-tree calculation itself is weaker than that portfolio on several cases. Its full-search widths are 0.01712 on M1, 0.02115 on M2, 0.02463 on M3, 0.00505 on I1, 0.00274 on I2, 0.00622 on Q2, and 0.09321 on T3. Several runs consume the full time or node budget. The complete-search theorem remains exponential, and the large-model runs process only a small number of expensive nodes.

The strongest external numerical evidence remains favorable to SCIP, whose native nonlinear lower bounds often close substantially tighter intervals faster than the custom proof-producing trees. Those native lower bounds are still not independently certified. This boundary is honestly reported, but it leaves the paper without either a practical superiority result or a verified external baseline of comparable strength. The new price certificate does not post-certify SCIP's global search.

The continuous-state contribution also remains incomplete. Repair density gives a convergent sequence of feasible upper values, but no finite rate and no matching lower sequence. The restart-price and support certificates give valid lower bounds, but no enrichment theorem states that computable prices or supports converge to the unrestricted controlled-continuum optimum. The original thirty positive-cost randomized intervals remain open, and no new optimization of those rows is performed. The nonlinear two-state intervals remain 25%–76% wide at allowance 0.5, with tighter-allowance rows still lower-only.

I did not find an obvious contradiction in the restart-price identity, witness budget, gap-free finite stopping theorem, or repair-density proof. The rejection is therefore not an allegation of hidden arithmetic error. It reflects the gap between a collection of sound one-sided certificates and a broadly effective numerical method, the retrospective and heavily reused nature of the evidence, the absence of a substantive economic application, and the limited incremental closure obtained after a very large amount of machinery.

A further revision that adds another certificate family on the same sixteen designed finite models would not resolve the journal-fit problem. A viable paper would need either a genuinely convergent and effective two-sided method for the motivating controlled continuous-state class, a prospectively evaluated solver that closes a materially larger fraction of difficult positive-cost problems under equal total-work budgets, or a serious economic application in which the certificates change a substantive conclusion.

## 2. Overall assessment

| Dimension | Assessment |
|---|---|
| Correctness of restart-price lower theorem | Plausibly correct; no obvious contradiction found |
| Correctness of exact policy-to-bound gap identity | Plausibly correct and conceptually useful |
| Treatment of operating ties | Substantially improved |
| Operating-witness accounting | Explicit and independently checked on finite examples |
| Computational transparency | Exceptional |
| Incremental primary closure | Weak: one new primary target hit |
| Tie evidence | Useful but narrow and retrospective |
| Complete-search practicality | Weak beyond small/easy rows; exponential guarantee |
| External solver comparison | Numerically informative but not fully certified |
| Continuous-state optimization | Still lacks a matched, computable two-sided convergence scheme |
| Economic application | Absent; all principal environments are designed known-model exercises |
| Novelty relative to dynamic Lagrangian and constrained-control duality | Not yet positioned sharply enough |
| Suitability for Econometrica | Insufficient |

## 3. What R47 genuinely contributes

The rejection recommendation should not obscure the revision's strongest features.

### 3.1 A coherent common-policy price certificate

For state-date prices \(\lambda_t(x)\ge 0\), the recursion

\[
 u_t(x)=\min_a\left\{k_t(x,a)+\lambda_t(x)(d_t^a(x)-\varepsilon)
 +\beta P_t^a\left[u_{t+1}+\varepsilon\min\{\lambda_t(x),\lambda_{t+1}\}\right](x)\right\}
\]

produces a valid lower certificate for the same common randomized Markov problem. The successor-price minimum is not cosmetic: it accounts for the fact that the same future regret must support every incoming restart. This is a cleaner treatment than applying unrelated restart multipliers.

### 3.2 An exact and interpretable gap decomposition

For a feasible policy, the gap between implementation cost and the price lower certificate is decomposed into unused initial allowance, transformed Bellman slack, and price-change slack, net of the nonnegative-cost clipping improvement. This gives a useful diagnostic for why a certificate is loose. It also makes clear that an operating tie need not itself create a singular constant.

### 3.3 Explicit witness sensitivity

The lower price loss is charged by price magnitudes times certified operating-witness widths, plus directed evaluation error. The upper policy is repaired against the actual repaired continuation using the upper witness. This is preferable to silently treating an approximate operating value as exact.

### 3.4 Tie-safe finite completeness

The gap-free stopping modulus avoids division by a minimum action disadvantage. The proof separates policy-box diameter, directed arithmetic precision, and feasibility repair. It correctly acknowledges that finite-model completeness is exponential and that fixed arithmetic precision creates a nonzero floor.

### 3.5 Strong verification boundaries

The price and price-tree objects are independently replayed, the new witness objects are checked by a separate standard-library reader, and malformed objects are rejected. The paper distinguishes theorem validity, finite arithmetic verification, source identity, and publication integrity. It also states that the R47 build replays rather than reruns the inherited optimizers.

These are substantial methodological and scientific improvements. The concerns below address what they do not yet establish.

## 4. Blocking scientific findings

### R47-F1 — The incremental primary success is one row, not six

The manuscript repeatedly reports that the price-strengthened search reaches six of twelve primary targets. That cumulative count is correct, but it obscures the relevant comparison.

Before R47's price extension, the certified portfolio already met the target on:

- M0;
- I0;
- Q0;
- Q1;
- Q3.

The price-strengthened result meets the target on those same five rows and on I3. Therefore the incremental primary contribution is **I3 alone**.

This distinction is scientifically important. M0 and Q1 are presented as examples where price branching crosses the target, but those economic instances were already solved by earlier methods. Price branching may be a different and useful route, but it is not a new instance-level closure. I0 has zero revision cost. Q0 is numerically near exact at the root. Q3 was already closed by the aggregate formulation. A reader seeing “six of twelve” could reasonably infer six new successful tests; the actual out-of-sample content is zero, and the actual new in-sample primary closure is one.

**Required correction:** make incremental and cumulative target counts equally prominent in the abstract, introduction, and conclusion. Report separately: previously closed rows, newly closed rows, zero-cost rows, root closures, and closures requiring branching.

### R47-F2 — The price experiment is retrospective and does not use an equal total-work comparison

The sixteen models, their failures, earlier bounds, and incumbents were already observed. The price search was developed after price and root outputs were available. It initializes with previously certified upper policies and disables the local proposal. Its reported incremental runtime excludes the work that produced those incumbents. The scalar portfolio further combines all valid old and new calculations.

This is acceptable as development evidence and is labeled honestly. It cannot establish general solver performance. Nor can runtime or node comparisons be interpreted as equal-budget comparisons when one method inherits an incumbent generated by another method.

**Required correction:** freeze the final price algorithm, price-generation rule, branching rule, arithmetic precision, and total-work accounting before a new heterogeneous benchmark suite is generated. Charge incumbent generation, price generation, root construction, search, and verification to each compared method or explicitly compare portfolios under equal cumulative budgets.

### R47-F3 — Seven portfolio rows remain open and the hard failures are material

After intersecting all certified endpoints, the unresolved rows and approximate widths are:

| Case | Portfolio width |
|---|---:|
| M1 | 0.007157 |
| M2 | 0.008723 |
| M3 | 0.024625 |
| I1 | 0.005053 |
| I2 | 0.002737 |
| Q2 | 0.001151 |
| T3 | 0.093208 |

The price search does not dominate the portfolio. Its own widths on M1, M2, and Q2 are substantially worse because older methods supply stronger lower endpoints. T3 reaches the full 2,047-node cap with essentially the price-root gap unchanged. M3 processes only 23 nodes within the time budget and barely improves its root. These are precisely the cases needed to establish practical value.

**Required correction:** explain structurally why each hard row remains open, not only through gap-decomposition labels. Provide controlled ablations of price fields, support cuts, product formulation, branching, incumbent generation, and LP time allocation. Demonstrate a material reduction on the hard rows under a fixed total budget.

### R47-F4 — The restart-price family is valid but not shown to be complete

Theorem 1 provides a one-sided lower certificate for every bounded nonnegative price field. The exact gap identity diagnoses looseness for a chosen policy and price field. Neither result proves that optimizing over the proposed price family attains the constrained optimum, nor that a computable sequence of prices drives the lower endpoint to it.

The price-flow term is especially revealing: on open cases, one separable state-date affine price field does not represent the jointly feasible future-regret geometry tightly. The paper suggests branching or additional fields, but gives no convergence theorem for price enrichment and no complexity bound for such enrichment.

There is also a smaller optimization mismatch. The finite price LP maximizes \(\sum_i\nu_i u_{0i}\), whereas the reported valid lower certificate is \(\sum_i\nu_i\max\{0,u_{0i}\}\). These objectives differ when the potential changes sign. This does not invalidate any reported certificate, but it means the LP is a proposal mechanism rather than an optimizer of the displayed clipped lower bound.

**Required correction:** characterize the supremum of restart-price certificates. Prove strong duality or a convergent enrichment scheme under explicit assumptions, or state prominently that the price LP is a heuristic lower-bound generator. Clarify the unclipped-versus-clipped objective distinction.

### R47-F5 — The tie evidence is narrow and partly structurally easy

The exact and near-tie results are a genuine improvement. They come from one four-state, eight-period, three-action family with four values of one reward perturbation. T0 has an exactly representable zero operating value and a 32-dimensional optimal-action face. T1 and T2 are close perturbations of that same construction. T3 remains open with width about 0.0932.

This shows that the price certificate can exploit a particular tie geometry. It does not establish robustness across multiple tied faces, time-varying ties, nonzero operating value, larger action sets, longer horizons, or ties embedded in economically distinct model families.

**Required correction:** include prospectively frozen tie environments from several model families and scales. Report how price magnitudes, price-flow slack, root strength, and search effort behave as the tie geometry changes.

### R47-F6 — Finite completeness remains primarily a decidability result

The gap-free theorem is correct-looking and valuable because it does not use a minimum positive action gap. Its sufficient depth is

\[
8d\left\lceil\log_2(1/w_*)\right\rceil,
\qquad d=nT(m-1),
\]

and the number of nodes is exponential in that depth. For the largest finite models, \(d\) is already 1,536. The price and product relaxations also add substantial per-node cost. The hard runs consequently process only tens or hundreds of nodes within the time cap.

The theorem requires arithmetic precision to increase for arbitrarily small requested gaps. The implementation retains fixed denominator grids. This is a valid implementation with a numerical floor, not an executed adaptive-precision complete algorithm.

**Required correction:** provide practical complexity results, error-versus-work curves across dimensions and horizons, and an implemented adaptive-precision schedule. Clearly separate “eventually finite without caps” from “computationally useful at the reported scale.”

### R47-F7 — The external baseline remains asymmetrically verified

SCIP reports eight native numerical target hits and often reaches tighter gaps faster. Its feasible candidates are independently evaluated, but its global lower bounds remain solver-reported floating-point quantities. The exact portfolio therefore uses internal rational lower bounds rather than SCIP's native lower values.

The paper is transparent about this boundary, but the resulting comparison is incomplete. It cannot claim that the custom method is competitive with a modern global solver, and it cannot count SCIP's strongest results as certified evidence. At the same time, the external solver's favorable numerical performance weakens the case that the proposed tree is practically necessary.

**Required correction:** post-certify SCIP's node relaxations and global cover, use a solver with proof logging that can be independently checked, or build an independent rational branch-and-bound baseline. Compare certified gap versus total time and memory, not only native solver reports against proof-producing custom code.

### R47-F8 — The witness experiment validates an interface, not a difficult operating oracle

The 64 witness objects are four precision variants of the same sixteen finite models. Their operating witnesses come from cheap directed finite Bellman passes. They do not test a high-dimensional approximation method, simulation-based oracle, fitted value function, sparse grid, neural approximation, or model with expensive expectation bounds.

At 16 bits the maximum measured lower loss is about 0.2804 and the maximum analytic budget about 2.8755; the sufficient repair guard fails in three models. At 24 bits the maximum loss is about 0.001007, already comparable to the entire stopping target, while the maximum budget remains about 0.01038. Only four price-only intervals meet the target at every precision, and those include the zero-cost or specially structured I0/T0/T1/T2 rows.

The sufficient condition \(\xi<(1-\beta)\varepsilon\) becomes severe under high discounting and tight operating tolerances. For \(\beta=0.95\) and \(\varepsilon=0.001\), the allowable uniform witness width is below \(5\times10^{-5}\).

**Required correction:** apply the witness theory to a model in which constructing global operating enclosures is genuinely difficult. Report enclosure cost, residuals, expectation errors, price amplification, repair changes, and final certified revision gap.

### R47-F9 — The controlled-continuum result remains one-sided and rate-free

Repair density proves that repaired rational simple proposals can approximate the unrestricted Borel optimum from above. This is an expressivity theorem. It supplies:

- no finite partition error rate;
- no computational complexity bound;
- no matching lower sequence;
- no stopping rule for the original continuous problem.

The dominating measures have total mass growing as \(m^t\), and the enumerated rational policy class is countable but combinatorially enormous. For the original maintenance model, the piecewise-rational representation can grow rapidly and is not executed in this revision.

The lower price/support constructions remain one-sided as well. No theorem pairs the upper enumeration with a convergent lower hierarchy for general controlled atomic dynamics.

**Required correction:** construct a computable two-sided hierarchy for the original controlled atomic class, prove convergence with an explicit error budget, and execute it on positive-cost rows. A density theorem for feasible upper policies and an unrelated valid lower family do not by themselves form a numerical method.

### R47-F10 — The motivating continuous-state evidence is unchanged

All thirty positive-cost randomized intervals in the original maintenance cohort remain open. Their median relative widths rise with horizon. The nonlinear two-state intervals remain 25%–76% wide at allowance 0.5; at allowance 0.05 the calculations remain lower-only. No new continuous optimization run is reported.

This is not a peripheral issue. The article repeatedly uses the continuous controlled model to motivate the method, yet all new numerical progress is on finite designed models or inherited structural reductions.

**Required correction:** close or tightly bound a meaningful subset of the original positive-cost randomized rows, including longer horizons, or remove that model as the central numerical motivation and narrow the paper to finite-state certification.

### R47-F11 — Continuous-state price computation is not operationalized

The restart-price theorem allows bounded Borel price fields and controlled atomic transitions. To become a numerical lower method on a continuum, it still requires:

- a representable price field;
- certified evaluation of the price Bellman recursion over the whole state space;
- verified integration under the initial law;
- an enrichment rule whose lower endpoints converge.

None of these components is supplied for general controlled continuous dynamics. The finite state-date LP does not directly transfer to an uncountable state space.

**Required correction:** specify a finite price representation and whole-domain verification scheme, prove approximation stability for that representation, and demonstrate lower-bound convergence on a nontrivial continuous model.

### R47-F12 — Novelty relative to dynamic Lagrangian duality is not established sharply enough

The new theorem uses state-date multipliers for regret constraints, a Bellman recursion, and a telescoping policy-to-bound identity. The manuscript cites constrained MDPs, information relaxation, and global optimization, but does not give a sufficiently precise comparison with dynamic Lagrangian duals, approximate linear programming, occupation-measure duality with common-policy compatibility, or Bellman inequality certificates.

The successor-price hinge may be new and useful. At Econometrica level, the paper must identify exactly which existing dual class fails without it, whether the new certificate is equivalent to a known dual after state augmentation, and under what conditions its supremum is tight.

**Required correction:** provide theorem-level equivalence or separation results relative to the closest dual formulations. Expand the literature review beyond broad field citations.

### R47-F13 — The success criterion has no economic calibration

The absolute target \(10^{-3}\) was prospectively fixed and consistently applied, which is good practice. It is nevertheless expressed in normalized, designed implementation-cost units. The paper correctly notes the scaling rule, but no economic loss, decision reversal, welfare threshold, or policy recommendation is tied to this accuracy.

Some unresolved relative gaps are small, while some target hits concern zero or nearly exact costs. A numerical tolerance is not economically meaningful merely because it was fixed before execution.

**Required correction:** motivate accuracy through an economic decision or calibrated scale, or report a family of scale-free criteria alongside the absolute target.

### R47-F14 — The economic evidence remains synthetic

Maintenance, inventory, and queueing labels provide useful structural variety, but all primitives are generated within the repository, fully known, and normalized. There is no estimated transition law, parameter uncertainty, sampling error, empirical implementation cost, or external policy question.

A pure methods article can be suitable without calibration if the method is broadly decisive. Here practical performance remains mixed and the motivating continuum problem remains unresolved. The absence of an application therefore matters.

**Required correction:** add a substantive economic application or substantially strengthen the general algorithmic contribution. More variants generated by the same codebase will not establish external relevance.

### R47-F15 — Verification quality should not be confused with scientific closure

The independent readers, hashes, exact fractions, mutation tests, and publication manifests are exemplary. R47 replays inherited R46 objects but does not rerun their optimizers. The witness audit checks the declared finite contracts. None of this proves that the price family is complete, the search is practical, the economic model is important, or the theorem is novel relative to the closest literature.

The manuscript sometimes devotes more attention to provenance and preservation than to comparative numerical analysis. Verification is a necessary property of a certified method, not the primary measure of its scientific contribution.

**Required correction:** reduce audit exposition in the main article and use the space for stronger same-object comparisons, structural analysis of failures, and economic interpretation.

### R47-F16 — The paper remains an omnibus of differently scoped results

The current article is more coherent than R43, but it still combines:

- a restart-price lower certificate;
- exact gap diagnostics;
- finite covering search;
- strict-gap root rates;
- approximate operating witnesses;
- one-sided Borel repair density;
- exact aggregation;
- reset transfer;
- observable fibers;
- original continuous one-sided bounds;
- nonlinear experiments;
- historical deterministic and randomized comparisons.

These components have different assumptions, different notions of convergence, and different empirical status. The paper's strongest theorem and strongest numerical evidence are not yet one theorem-experiment pair solving one important problem end to end.

**Required correction:** narrow the paper around either (a) restart-price dual certification and its finite solver, or (b) a complete controlled-continuum method. Preserve the broader research archive without requiring the journal article to carry every historical component.

## 5. Minimum requirements for a future submission

A future submission should satisfy a coherent subset of the following rather than adding another layer to the same omnibus package.

1. **Prospective evaluation of the final algorithm.** Freeze the complete price/search method and run a new suite with equal total-work accounting. Demonstrate a substantial number of new positive-cost closures across multiple families and scales.

2. **A completeness result for price enrichment.** Establish strong duality or a convergent hierarchy of restart-price certificates, including how state-dependent fields are represented and verified.

3. **A fair verified external baseline.** Certify the external solver's lower bound or implement an independently checkable global-optimization baseline with comparable cuts and budgets.

4. **An executed difficult operating-oracle application.** Use genuinely approximate operating witnesses and carry their construction error through to a useful final revision interval.

5. **A two-sided continuous-state method.** Pair a computable lower hierarchy with the repaired simple-policy upper hierarchy and close positive-cost controlled-atomic examples.

6. **Economic relevance.** Tie the numerical tolerance and certified policy result to an economically meaningful application, calibrated scale, or robust decision.

7. **Sharper novelty positioning.** State exactly how the restart-price recursion and hinge residual differ from existing dynamic Lagrangian, occupation-measure, information-relaxation, and approximate-LP duals.

8. **A narrower article.** Select one central theorem and one decisive experimental program; move preservation history and secondary model classes to the archive.

## 6. Additional technical and presentation comments

1. State in the abstract that the price method adds one newly closed primary environment relative to the prior certified portfolio.

2. Report cumulative hits and incremental hits in separate columns.

3. Separate zero-cost exactness, nearly exact root rows, root closures, and branch-dependent closures.

4. Charge the cost of inherited incumbent construction when reporting portfolio or price-search total work.

5. Report price-generation time, price-replay time, tree time, and independent verification time separately for every row.

6. Add proof bytes and peak memory to the main price table for the hard cases.

7. Report the exact stop reason for every price search in the main table, not only in the supplement.

8. Show all components of the gap identity by case, normalized by total gap as well as in absolute units.

9. Report price magnitudes and conditioning. Large prices directly amplify witness error.

10. Explain whether price caps, variable scaling, or LP regularization are used.

11. Provide sensitivity to the price-proposal objective and to the clipping at zero.

12. Clarify that maximizing the un-clipped initial potential need not maximize the clipped certificate.

13. Distinguish an exact restart-price LP optimum from a rounded numerical proposal and from the reconstructed Bellman certificate.

14. For T0, report the optimal cost, operating value, face dimension, and which tied actions carry the certified policy.

15. For T3, diagnose whether the residual is dominated by initial slack, action slack, price-flow slack, or upper-policy quality.

16. Do not treat T0–T3 as four independent tie applications; they are perturbations of one construction.

17. Report \(\xi/((1-\beta)\varepsilon)\) for every witness row so the repair guard's conditioning is visible.

18. Separate lower-endpoint witness loss from upper-policy repair loss rather than summarizing only the paired interval.

19. Explain why 24-bit maximum lower loss slightly exceeds the global \(10^{-3}\) target and what this implies for practical precision selection.

20. Provide an adaptive witness-precision rule driven by the desired final gap.

21. For the repair-density theorem, give an explicit finite-horizon error formula in terms of the \(L_1(\mu_t)\) proposal errors, not only the existence argument.

22. State the growth of \(\mu_t(X)=m^t\) prominently when discussing numerical use.

23. Distinguish representability of a rational compiled incumbent from an arbitrary floating-point neural policy throughout the continuous section.

24. Report absolute and relative widths together for every positive-cost row.

25. Explain the policy consequences of each unresolved interval: whether alternative actions or deployment decisions remain ambiguous.

26. Keep SCIP native lower bounds, internally certified lower bounds, and independently checked upper policies in separate columns in every table.

27. Do not describe the scalar portfolio as one algorithm with a 120-second budget; it is the intersection of several separately funded computations.

28. The common-refinement dominance result is unexecuted and may have multiplicative cell growth; keep it out of performance conclusions.

29. The multi-criterion extension supplies a lower certificate but not a general feasibility repair. This limitation should appear in the theorem statement, not only after it.

30. The literature review remains too short for a paper making a new dynamic dual certificate claim. Add direct comparisons to the closest constrained-control and dynamic-programming dual formulations.

## 7. Final editorial view

R47 contains a legitimate theorem, a careful exact gap identity, improved treatment of ties, and outstanding computational audit practice. It materially advances the project beyond the earlier necessary-action and root-relaxation stages. The exact-tie closure is particularly useful evidence that the new lower certificate is not merely an inverse-gap device.

The numerical record is still not strong enough for Econometrica. The method adds one new primary closure on a retrospective development suite, leaves seven portfolio rows open, remains exponential, and does not solve the original controlled continuous-state problem. The approximate-witness evidence is an interface audit on easy finite operating dynamic programs, not a difficult oracle application. SCIP's strongest lower bounds remain uncertified, and the economic environments remain uncalibrated synthetic examples.

The paper is therefore best viewed as a rigorous verified-computation framework with a promising new lower certificate, not yet as a broadly effective numerical method for important economic dynamic programs.

**Recommendation: Reject.**