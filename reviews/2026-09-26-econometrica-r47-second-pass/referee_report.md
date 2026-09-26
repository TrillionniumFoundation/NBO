# External Referee Report — R47, Independent Second Pass

**Venue perspective:** Econometrica-level numerical and computational methods  
**Article:** *Certified Bellman Operators for Costly Policy Revision*  
**Repository:** `TrillionniumFoundation/NBO`  
**Reviewed branch:** `revision/econometrica-r47-complete-referee-2026-09-26`  
**Equivalent referee-copy branch:** `revision/econometrica-r47-referee-copy-2026-09-26`  
**Reviewed HEAD:** `1987a1f91ff783cd6f24fa7a9ea6a8118f64c56c`  
**Earlier first-pass report on the same immutable HEAD:** `reviews/2026-09-26-econometrica-r47/referee_report.md` at `c8ac36c50812a88b9dc06bbd1bce5a5013d76371`  
**This review branch:** `review/econometrica-r47-second-pass-numerical-methods-2026-09-26-1987a1f`  
**Date:** 2026-09-26

## 1. Recommendation

**Reject. I do not recommend another incremental revision under the current paper architecture.**

This is an independent second-pass assessment of the same immutable R47 object. No R48 branch or newer R47 commit exists at the time of review. I therefore focus on whether the now-complete article, taken at face value and after its strongest possible reading, delivers the kind of numerical-methods contribution expected at Econometrica.

R47 is mathematically more coherent than the earlier versions. Its restart-price Bellman inequality is a legitimate and potentially useful lower-bounding device for the all-restart common-policy problem. The successor-price minimum is the right correction for preserving a single continuation across incoming states, and the policy-specific identity gives a transparent account of unused allowance, transformed-action slack, and price-flow mismatch. The backward repair results are also useful. The verification boundary is stated more honestly than in most computational submissions: exact proof objects, independent readers, inherited versus new computations, failed target rows, and uncertified SCIP lower bounds are distinguished.

The central problem is no longer basic credibility. It is scientific adequacy.

The newly advertised method is not an end-to-end solver. In the retrospective price experiment, the new computation primarily supplies lower bounds. The upper policies are inherited from earlier methods, their construction cost is excluded from the new runtime, and the additional local proposal is disabled. Even the one newly closed primary row, I3, is closed by pairing a new lower bound with an old feasible incumbent. That is a valid verification result, but it is not evidence that the restart-price method independently finds and certifies a solution.

The operating-witness experiment is likewise not an end-to-end approximate-oracle experiment. The prices and saved policies come from exact finite-model runs; only afterward are finite-precision Bellman enclosures substituted into the certificate and repair interfaces. This verifies error propagation conditional on exact-model design choices. It does not show that the method can generate useful prices, proposals, or final intervals when the true operating value is genuinely unavailable.

The continuous-state theory remains split into two one-sided statements. Repaired simple proposals are dense from above, but no computable rate is given. Restart prices and support functions give valid lower bounds, but no enrichment theorem makes those lower bounds converge to the unrestricted controlled-continuum optimum. The original thirty positive-cost continuous randomized intervals remain open, the nonlinear two-state intervals remain wide, and no new continuous optimization is executed in R47. Thus the broad Borel theory does not yet produce the numerical method motivated by the article.

The finite-state completion theorem is a decidability result with exponential geometry, not a persuasive complexity result. It eventually closes a finite model by refining a high-dimensional policy-probability box and increasing arithmetic precision. At the largest reported dimensions the method processes very few expensive nodes. The strongest external numerical evidence still favors SCIP, whose native lower bounds are not independently certified. The paper therefore lacks both a practical superiority result and a comparably strong verified baseline.

Finally, the evidence remains retrospective and highly reused. Six of twelve primary price-search target hits means one new primary closure relative to the existing certified portfolio. Three tie closures come from one small parametric family, while the fourth tie case remains badly open. There is no untouched benchmark suite, no calibrated economic application, no estimated model, and no welfare result in economic units.

I did not find an obvious algebraic contradiction in the restart-price theorem, the backward repair argument, the witness budget, or the finite stopping proof. My recommendation is instead based on the mismatch between what is proved and what is needed for an Econometrica numerical-methods article: a coherent algorithm for a consequential economic target, a two-sided approximation theory tied to that algorithm, convincing prospective performance, and an application or breadth result commensurate with the paper's scope.

## 2. Bottom-line assessment

| Question | Second-pass assessment |
|---|---|
| Is the restart-price inequality a valid lower certificate? | Plausibly yes under the stated bounded finite-action assumptions |
| Is the exact gap identity useful? | Yes as a policy/certificate diagnostic |
| Does the price family have a completeness or strong-duality theorem? | No |
| Does R47 provide an independent end-to-end solver? | No; new lower bounds are paired with inherited upper incumbents |
| Does the witness audit test operation without exact operating values? | No; it reuses exact-run prices and saved policies |
| Does the continuum theory give a computable paired convergence scheme? | No |
| Does the finite search have a practically meaningful complexity guarantee? | No; its sufficient completion is exponential |
| Is there prospective evidence on unseen problems? | No |
| Is there a substantive economic application? | No |
| Is the computational archive unusually strong? | Yes |
| Does archival strength compensate for the scientific gaps? | No |
| Editorial recommendation | Reject |

## 3. Main strengths

### 3.1 The paper now studies one well-defined policy object

The target is a common randomized Markov policy, with one action distribution at every state and date, an initial-law implementation objective, and operating protection after every state-date restart. R47 no longer conflates this object with deterministic policies or separately optimized restart plans.

### 3.2 The successor-price correction is conceptually meaningful

For nonnegative state-date prices, the term

\[
\varepsilon\min\{\lambda_t(x),\lambda_{t+1}(y)\}
\]

and its complementary price-change slack are not arbitrary embellishments. They preserve the fact that one future regret variable must serve every incoming transition. This is the cleanest conceptual contribution in the paper.

### 3.3 Backward repair is a useful organizing device

The repair maps approximate feasibility into exact all-restart feasibility and provides an explicit implementation-cost modulus. The upper-witness version correctly chooses the best action against the already repaired continuation rather than against a stale reference continuation.

### 3.4 The paper exposes rather than conceals verification limits

R47 states that SCIP's native global lower bound is not independently certified, that the witness audit is not a difficult learned-oracle experiment, that the price study is retrospective, that the continuous rows remain open, and that finite completion is not polynomial. This candor is a genuine strength.

### 3.5 The finite proof objects are unusually well engineered

Separate readers reconstruct models, Bellman quantities, policy values, price inequalities, tree covers, and witness enclosures. The current build replays inherited proof objects rather than pretending to rerun the original optimization. Mutation tests are finite diagnostics, not mislabeled theorem proofs.

These strengths make R47 a serious research artifact. The blocking findings below explain why they do not make it an Econometrica paper.

## 4. Blocking scientific findings

### R47-SP1 — The R47 method is a lower-bound plug-in, not an end-to-end numerical solver

The retrospective price runs use previously certified feasible policies as incumbents and disable the additional local proposal. The new computation therefore does not generate the upper side of the reported intervals. Its target attainment depends on work performed by earlier algorithms.

This distinction matters most for the headline new success, I3. The price root supplies a much stronger lower endpoint, while the upper endpoint is inherited. The interval closes because two separately developed components meet. The result is a valid portfolio certificate, but it does not show that restart prices alone solve the instance.

The same issue affects runtime claims. Incremental price-search time excludes the cost of obtaining the upper incumbent. A method that receives a high-quality incumbent for free is not being compared under the same information and total-work budget as a method that must discover one.

**Required for a viable numerical paper:** define a complete algorithm whose inputs, upper-policy generation, lower-bound generation, refinement rule, stopping rule, and total cost are all included. Compare this algorithm against alternatives under identical information and cumulative budgets. Portfolio certification may remain as an additional result, but should not be presented as standalone solver performance.

### R47-SP2 — The witness experiment is conditional on exact-model discoveries and therefore does not validate the claimed approximate-oracle workflow

The 64 witness objects are generated from four precision levels on the same sixteen finite models. The prices are inherited from checked source certificates, and the upper proposals are saved policies from exact finite runs. The experiment then asks whether conservative operating enclosures can reproduce a valid lower potential and repair those already good policies.

This is an error-propagation audit. It does not answer the operational question faced in a large model: how to find useful prices and policies when only approximate operating information is available. An exact-
\(V\) run has already revealed the geometry used to select the price field and incumbent.

The distinction is particularly important because the witness budget is price-amplified:

\[
\Gamma_0=\sum_t\beta^t\bigl(\|\lambda_t\|_\infty(w_t+\beta w_{t+1})+q_t\bigr).
\]

A price field optimized using exact information can be both stronger and differently conditioned than one found from noisy enclosures. The audit reports endpoint losses but does not report the price norms and conditioning that determine portability.

**Required correction:** run the full pipeline using only approximate operating witnesses. Generate prices, candidates, repairs, and final intervals without access to exact \(V\) or exact disadvantages at any design stage. Report price norms, oracle construction cost, Bellman residuals, expectation-enclosure cost, proposal quality, repair displacement, and the final certified gap.

### R47-SP3 — The restart-price family is not shown to converge to the constrained optimum

The theorem says that every admissible nonnegative price field produces a valid lower bound. The exact gap identity explains why a selected price is loose. Neither result establishes strong duality, density of the affine price family, or a computable sequence whose lower values converge to \(\mathcal K_R\).

The price-flow slack shows the limitation directly. A single separable state-date field need not encode the joint future-regret geometry. Adding branches or more price fields may help, but the paper gives no enrichment topology, no convergence theorem, and no rate.

There is also an objective mismatch in the finite price proposal. The LP maximizes the un-clipped quantity \(\sum_i\nu_i u_{0i}\), while the valid displayed lower certificate is \(\sum_i\nu_i\max\{0,u_{0i}\}\). These objectives differ whenever the potential changes sign. This does not invalidate a reconstructed certificate; it confirms that the LP is a heuristic proposal mechanism rather than an optimizer of the reported bound.

**Required correction:** characterize the supremum over price fields. Prove a strong-duality result under meaningful conditions, or give a convergent hierarchy of richer price objects. Otherwise the paper must describe restart prices as one valid lower-bound family rather than as the organizing solution method.

### R47-SP4 — The exact gap identity is diagnostic, not a computable global optimality gap

For a fixed feasible policy and fixed price certificate, the identity decomposes the difference between that policy's cost and the clipped lower bound. This is useful. It does not identify the distance between the policy and the true optimum unless the lower certificate is itself tight.

Moreover, after clipping, the equality contains the correction

\[
-\int(-u_0)_+\,d\nu.
\]

Thus the policy-to-bound gap is not literally a sum of nonnegative slacks. The manuscript explains the subtraction, but repeatedly describing the result as a “nonnegative-slack gap decomposition” is rhetorically stronger than the displayed identity.

On difficult rows, the decomposition can tell the reader that price-flow mismatch is large. It does not say which additional price basis, partition, or branching decision will reduce the global gap at a useful rate.

**Required correction:** distinguish a policy-versus-certificate identity from an optimum-versus-algorithm error decomposition. Report whether each slack component is actionable and demonstrate that a prescribed refinement decreases it on hard cases.

### R47-SP5 — The upper and lower continuum theories do not form a numerical approximation theorem

The repair-density theorem gives

\[
U_N\downarrow\mathcal K_R
\]

through an enumeration of repaired rational simple proposals. It supplies no finite \(N\) rate and, under general Borel primitives, no effective method for evaluating each member exactly. The dominating measures used in the proof have mass \(m^t\), already signaling poor horizon scaling.

The lower side consists of valid price or support certificates. There is no theorem that a computable enrichment of partitions, witnesses, and prices raises the lower endpoint to the same limit. Consequently the paper has no continuum stopping rule of the form “refine until \(U_N-L_N\le\eta\).”

The piecewise-rational maintenance discussion gives a possible representation route for individual repaired proposals, but no executed optimizer, no joint lower sequence, no complexity estimate for breakpoint proliferation, and no new closure of the original rows.

**Required correction:** provide one matched continuum scheme with explicit assumptions, computable lower and upper sequences, verified expectation/integration errors, convergence to the same target, and an executable stopping criterion. Existence of a dense feasible class is not a numerical algorithm.

### R47-SP6 — The motivating continuous-state problem is still unsolved

All thirty positive-cost randomized intervals in the original continuous maintenance cohort remain open. Their median relative widths grow with horizon. The nonlinear two-state intervals remain approximately 25%–76% wide at allowance \(1/2\), and the tighter allowance calculations remain lower-only. The stopped-control material remains historical rather than solved.

R47 adds a theorem applicable to controlled atomic kernels, but applicability of an inequality is not numerical resolution. No new optimization is performed on the motivating continuous cohort.

This is especially damaging because the finite models are not the original scientific target. The project has moved from a difficult action-dependent continuous problem to exact-known finite surrogates where operating dynamic programming is cheap.

**Required correction:** close a meaningful subset of the original positive-cost randomized intervals or replace the motivating application with one that the proposed method actually solves. The result should include a complete error budget and independent verification of both endpoints.

### R47-SP7 — Finite completion is an exponential decidability result

The sufficient depth scales with

\[
8d\left\lceil\log_2(1/w_*)\right\rceil,
\qquad d=nT(m-1),
\]

before conversion to a binary-tree node bound. At the largest reported finite size, \(d=16\times32\times3=1536\). The theorem therefore does not explain practical tractability.

The experiments confirm the problem. Expensive root relaxations and exact proof production leave only a small node budget on the largest cases. M3 improves very little in 23 nodes. T3 reaches the full 2,047-node cap and remains far from target. Several medium cases consume the time cap while remaining open.

The theoretical statement also requires increasing arithmetic precision for every arbitrarily small requested target. The implementation uses fixed grids. This is a valid finite-precision certificate system, not an executed arbitrary-accuracy algorithm.

**Required correction:** give dimension- and horizon-scaling experiments on unseen instances; implement adaptive precision; provide total work versus certified gap curves; and identify structural conditions under which node growth is controlled. “Finite without caps” must not be used as a proxy for computational usefulness.

### R47-SP8 — The cumulative success count masks the incremental result

The price search reaches six of twelve primary targets, but the preexisting certified portfolio already closed M0, I0, Q0, Q1, and Q3. R47 adds I3. Thus the incremental primary closure is one row.

Among the six cumulative successes:

- I0 has zero implementation cost;
- Q0 is essentially exact at the root;
- Q3 had already closed under the aggregate formulation;
- M0 and Q1 had already closed under earlier trees;
- I3 is the sole newly closed primary row.

Seven of sixteen final portfolio rows remain open. The unresolved portfolio gaps are approximately 0.00716, 0.00872, 0.02463, 0.00505, 0.00274, 0.00115, and 0.09321 on M1, M2, M3, I1, I2, Q2, and T3.

**Required correction:** every headline table should separate cumulative closures, incremental closures, zero-cost rows, root closures, branching closures, and rows closed only through a multi-method portfolio.

### R47-SP9 — The tie experiment is informative but too narrow to establish robustness

T0, T1, and T2 are successful and demonstrate that the certificate does not algebraically break when a minimum action disadvantage vanishes. That is a real result.

However, all four tie cases come from one four-state, eight-period, three-action construction and vary one reward perturbation. T0 has an exactly represented zero operating value. The exact-tie face dimension is large, but the surrounding model is small and specially designed. T3 remains open with a width around 0.0932 after the node cap.

The evidence therefore establishes validity and one favorable geometry, not robust performance near general switching surfaces.

**Required correction:** prospectively freeze several unrelated tie structures: time-varying ties, multiple disconnected optimal faces, nonzero operating values, larger action sets, longer horizons, and ties embedded in distinct economic models. Report price magnitudes and price-flow slack as the perturbation geometry changes.

### R47-SP10 — The evidence is a development cohort after an extraordinary number of revisions

The same problem family and many of the same cases have been inspected, revised, reparameterized, and re-solved across a long sequence of branches. R47 is explicit that its price extension is retrospective. The final algorithm has not been evaluated on an untouched suite.

Independent arithmetic verification prevents silent alteration of a declared object. It does not prevent methodological overfitting to repeatedly observed failures. The distinction is analogous to test-set reuse in empirical work.

**Required correction:** freeze code and hyperparameters, publish hashes before solving, and run a new holdout suite spanning model family, horizon, action count, state dimension, discounting, tolerance, and tie structure. Retain every failed row and predefine the primary aggregate metric.

### R47-SP11 — The external global-solver comparison remains unresolved

SCIP often reports materially tighter native gaps, and it reports more numerical target hits. Its feasible candidates are independently evaluated; its native lower bounds are not. This is transparent but leaves an asymmetric comparison.

The paper cannot claim that the custom proof-producing method is practically superior. It also cannot promote the external solver's strongest lower endpoints into certified results. The current comparison therefore documents a tradeoff without establishing a numerical advantage.

**Required correction:** use a solver/proof format whose global cover can be checked, post-certify node relaxations and branch decisions, or implement a separate rational branch-and-bound baseline. Compare certified gap against total CPU, memory, proof size, and verification time.

### R47-SP12 — Computing the operating oracle remains the dominant untested bottleneck

The strongest finite experiments begin from exact rational operating dynamic programs. The witness extension requires global lower and upper enclosures and, for its clean upper perturbation bound, the guard

\[
\xi<(1-\beta)\varepsilon.
\]

For \(\beta=0.95\) and \(\varepsilon=0.001\), this requires a uniform witness width below \(5\times10^{-5}\). In high-dimensional economic models, obtaining a certified sup-norm enclosure at this scale can be harder than the policy-revision problem itself.

The upper repair also requires verified expectations of the repaired continuation and a pointwise best action. These operations are cheap in the reported finite models and potentially formidable in the settings used to motivate approximation.

**Required correction:** demonstrate the method with a genuinely expensive operating oracle—such as a sparse-grid, fitted, simulation-based, or high-dimensional value approximation—and include the cost of proving its global enclosure.

### R47-SP13 — The economic contract is unusually conservative and remains unvalidated

The operating constraint holds after every state and date, including zero-probability states. This is a strong robust-restart requirement, not the standard expected constrained-MDP object. The objective, by contrast, is integrated under one initial law. The asymmetry may be economically appropriate, but no substantive institution or application is used to justify it.

The randomized policy assumes fresh state-dependent lotteries. Implementation cost charges realized departure from an installed rule, while governance, communication, and lottery administration costs are absent unless added through a hypothetical break-even calculation. All costs are normalized and known.

**Required correction:** provide an application in which all-restart protection, fresh randomization, installed-policy departure costs, and the initial-law objective arise from an explicit economic institution. Show that the certified result changes an economic decision.

### R47-SP14 — The novelty claim is not positioned tightly enough against classical duality and constrained-control formulations

The manuscript acknowledges that McCormick envelopes, spatial branching, weak duality, dynamic programming, and constrained MDPs are established. The central claimed novelty is the restart-price recursion and exact shared-continuation gap identity.

That claim requires a more systematic comparison with dynamic Lagrangian relaxations, occupation-measure formulations with common-policy compatibility, resource-augmented dynamic programs, multiobjective Bellman methods, and information-relaxation duals. The current literature section is broader than earlier versions but still does not establish whether the price recursion is a new dual, a specialized reformulation of an existing constrained-control dual, or a convenient computable restriction.

**Required correction:** derive the relation formally. State which dual feasible objects correspond to the proposed prices, whether the bound is dominated by or dominates standard relaxations, and provide a theorem-level novelty statement rather than an implementation-level distinction.

### R47-SP15 — The title and scope remain broader than the demonstrated contribution

“Certified Bellman Operators” suggests a general operator-level numerical framework. The executed advance is narrower: a restart-price lower certificate, a brute-force finite covering mechanism, and a precision audit on exact-known finite models. The broad controlled-continuum target remains unresolved.

The article also continues to carry deterministic history, finite product relaxations, tie theory, witness theory, continuum density, exact aggregation, fibers, nonlinear boxes, SCIP, and archival material. The integration is better than before, but the burden remains disproportionate to the central quantitative result.

**Required correction:** narrow the paper to the restart-price theorem and a decisive application, or build a genuinely unified algorithmic theory covering the full claimed scope.

### R47-SP16 — Verification strength should not be confused with scientific generalization

Hashes prove identity. Rational readers prove declared inequalities for declared finite objects. Mutation tests show rejection of selected corruptions. None of these establish that the mathematical specification matches the intended economic model, that every theorem assumption holds in code, or that performance generalizes.

The independent readers share the authors' specification of the target and primitive model. A common modeling error can survive constructor and verifier. The continuum theorems are analytic and not machine checked. The current evidence is excellent for arithmetic provenance and limited for external scientific validation.

**Required correction:** add independent model-contract tests, a separately implemented benchmark formulation, and external replication on new environments. Keep provenance claims distinct from claims of economic correctness and algorithmic performance.

### R47-SP17 — Important restrictions are structural, not merely expository

The main theory assumes finite actions, bounded rewards, bounded nonnegative implementation costs, finite horizon, positive allowance, and known kernels. Exact zero allowance receives a special finite-action face recursion. Continuous actions, unbounded states/costs, estimated kernels, learning uncertainty, and negative implementation transfers are outside the central method.

These restrictions exclude many of the economic dynamic programs for which an Econometrica numerical-methods paper would be most consequential.

**Required correction:** either narrow the claims to the bounded finite-action setting or extend the theory and experiments to a materially broader class.

### R47-SP18 — The accuracy target lacks economic interpretation

The absolute target \(10^{-3}\) was fixed and is consistently applied. That is good protocol discipline. It remains a tolerance in normalized departure-cost units. A rescaling of costs rescales the meaning of success, as the paper itself notes.

Several unresolved rows have small relative widths while failing the absolute target; others have economically material relative gaps. Without a calibrated application, target attainment is a numerical convention rather than a statement about decision relevance.

**Required correction:** report relative gaps and decision-loss implications alongside the absolute criterion. In an application, choose the target from an economically meaningful indifference threshold.

## 5. Minimum requirements for a substantially redesigned submission

A future submission should not respond by adding another bound family to the same sixteen models. It should satisfy a coherent set of the following requirements.

1. **An end-to-end algorithm.** The method must generate both feasible upper policies and valid lower bounds without free inherited incumbents.
2. **A matched continuum approximation theorem.** Computable lower and upper sequences must converge to the same controlled continuous-state target with an executable error budget.
3. **A genuine approximate-oracle experiment.** Prices and policies must be generated using only certified approximate operating information.
4. **Prospective evaluation.** Final code and parameters must be frozen before a new holdout suite is solved.
5. **Equal total-work baselines.** Incumbent generation, lower-bound generation, refinement, serialization, and verification must all be charged.
6. **A verified strong external baseline.** The comparison should include independently checkable global lower bounds from a credible alternative formulation.
7. **A substantive economic application.** The model should justify all-restart protection and implementation costs and yield a decision-relevant conclusion.
8. **A sharper novelty theorem.** The relationship to constrained-MDP duality and dynamic Lagrangian methods must be formalized.
9. **Practical scaling evidence.** Certified gap-versus-work curves should vary state dimension, horizon, action count, discounting, tolerance, and tie geometry.
10. **A narrower article.** The paper should center on one theorem-algorithm-application chain rather than an archive of adjacent partial results.

## 6. Technical and presentation comments

1. Add an explicit column giving the source and historical compute cost of every upper incumbent used by the price runs.
2. Report “newly closed relative to the previous certified portfolio” beside every cumulative success count.
3. Separate method-only intervals from portfolio intervals in the abstract.
4. State whether the I3 upper incumbent was generated by a custom tree, local proposal, SCIP candidate, or another inherited method.
5. Report \(\max_{t,i}\lambda_{ti}\), median price, and price dispersion for every case and relate these to witness amplification.
6. Show each term of the policy-to-certificate identity as an absolute amount and as a share of the unclipped gap.
7. Report the clipping correction separately; do not call the final equality purely nonnegative.
8. Explain why the finite LP maximizes the un-clipped objective rather than the displayed clipped lower certificate.
9. Include a case where optimizing the un-clipped objective produces a worse clipped bound than another feasible price field, or prove this cannot occur under the executed initial laws.
10. Report how much each old lower bound, restart-price bound, price-root bound, and price-tree bound contributes to the final portfolio row.
11. Charge the cost of constructing inherited incumbents when reporting portfolio efficiency.
12. Give proof-object size and independent replay time for every R47 price tree in the main supplement table.
13. Report the fraction of total search time spent in LP proposals, exact residual reconstruction, policy repair, serialization, and verification.
14. Show certified gap trajectories for every nonroot price-search target and for representative failures, not only selected successes.
15. For T3, explain why 2,047 nodes do not improve the root width and identify the dominant unresolved geometry.
16. Report whether branching is ever performed on coordinates with zero or negligible effect on the lower bound.
17. Add strong-branching or reliability-branching ablations on a frozen subset.
18. In the witness audit, disclose that prices and proposals were selected using exact-model runs in every relevant table caption.
19. Run a second witness experiment in which prices are generated from the lower/upper witnesses themselves.
20. Report witness-enclosure construction complexity, not only certificate construction and checking time.
21. Plot lower-endpoint loss against \(\Gamma_0\) and against \(\|\lambda\|_\infty\xi\).
22. For the three 16-bit guard failures, report the actual minimum denominator margin and repair mass.
23. Clarify whether finite expectation evaluations are exact rational sums in all witness objects.
24. For the continuum density theorem, distinguish mathematical enumeration from a computable enumeration with certified integration.
25. Quantify piece growth in the piecewise-rational maintenance repair for at least one nontrivial horizon.
26. State explicitly that repaired simple proposals need not remain simple, so the enumerated proposal class is not itself the deployed policy class.
27. Provide a formal comparison between restart prices and constant Lagrange multipliers in a standard constrained-MDP dual.
28. Explain whether unrestricted state-date prices can be interpreted as a potential on a regret-budget state augmentation.
29. The multi-criterion extension should remain out of the main contribution unless a feasible common repair and an experiment are supplied.
30. Report absolute and relative widths together for all rows; normalized absolute targets alone are not decision-relevant.
31. Remove “global optimization” from keywords unless the practical solver claim is made precise.
32. Reconsider the plural “Operators” in the title; the paper's decisive new object is one certificate recursion.
33. Move historical stopped-control and unrelated earlier derivations entirely outside the submission package.
34. Shorten the main article. The current breadth makes it difficult to identify which results are necessary for the principal claim.
35. Add a compact assumptions/results matrix showing policy class, state/action class, exact versus approximate oracle, lower completeness, upper completeness, executed evidence, and independent verification.

## 7. Editorial conclusion

R47 has crossed an important threshold: it is now a coherent, readable, and mathematically serious manuscript rather than merely a sophisticated repository protocol. The restart-price correction and exact policy-specific identity are worthwhile ideas, and the authors' computational provenance practices are exemplary.

The paper nevertheless remains below the Econometrica bar. The new method is chiefly a lower-bound verifier attached to inherited upper policies. The approximate-witness evidence is conditional on exact-run discoveries. The continuum problem lacks a paired computable convergence theory. The finite completion result is exponential. The prospective evidence and economic application are absent. The strongest external solver remains numerically favorable but uncertified. Most importantly, after the large expansion of theory and infrastructure, the incremental primary closure is one retrospective row and the motivating continuous problem remains open.

**Recommendation: Reject. A future submission should be a substantially redesigned paper, not R48 as another incremental layer on the same development cohort.**
