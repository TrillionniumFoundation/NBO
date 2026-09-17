# Response to the latest substantive referee report

**Manuscript:** Neural Bellman Operators.  
**Author:** Qian QI.  
**Revision:** R8, 17 September 2026.  
**Report addressed:** `reviews/2026-09-17-econometrica-latest-substantive/referee_report.md`, review commit `bb9144d3da7be059af7452dababb9fa5763b335c`.  
**Prior complete manuscript:** R7, `fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17`.

We thank the referee for distinguishing valid finite-model results from the economic and computational claims that require additional evidence. This revision supplies a complete new main manuscript and supplement, new arguments, executed two-regime economic counterfactuals, and a matched decision-certification experiment. It preserves the existing operator results, applications, appendices, structural countercomparisons, adverse observations, and all historical reviews. The earlier R8 initialization is not treated as a completed revision.

## F1. Economic target, wealth granularity, and the decision margin

**Changes in the manuscript:** “The Economic Decision and Its Robustness,” particularly the finite settlement protocol and target-error account; “Economic Robustness and the Cost of a Decision Certificate”; Supplement S.12.1 and S.12.5. **Evidence:** `replication/r8/output/spatial_{49,97,145}.json`, the corresponding nested-region certificate files, and the original-region `decision_contest.json`.

We take the referee's explicit finite-economic-primitive route rather than insert an unevaluated diffusion constant. The manuscript now specifies an eight-date rebalancing contract with four-shock candidate arrivals, straight-line early liquidation, discounted operating annuities, and mean-preserving randomized settlement on recorded wealth balances and preference tiers. It explains the economic content of the settlement lottery, including the extra conditional variance. This is an analytical contract, not a claim that an observed financial institution uses random rounding. The continuous-state diffusion and its approximation theory remain in the paper as distinct objects.

The original rectangle is retained. We reoptimize both risk classes in both adjustment regimes on the 49-, 97-, and 145-node wealth grids, keeping the calendar and preference grid fixed. The common-menu arm uses exactly the union of both meshes (1,565 controls), not the shortcut that drops a mesh. The full arm additionally retains the frozen proposals and explicitly prolongs them at new wealth nodes. All four old corners and the center remain in the evidence. At the vulnerable corner the no-adjustment sign changes on finer wealth lotteries, while the adjusted sign and positive relative option survive. We do not reclassify this result as a proof of diffusion convergence or conceal it behind a favorable new region.

The new indifference brackets map the movement of both regime boundaries. A common nested rectangle, lambda in [0,0.125] and d in [0.4,0.425], is then certified separately for each of the three full-menu finite protocols. That statement is a continuum result in the contract and law-mixture coordinates for those protocols, not a claim over every possible grid. Its exploratory selection is disclosed. The earlier wider nested trial on [0,0.25] by [0.4,0.425], including its failure at 97 wealth nodes, is also preserved when available in the execution record.

The target-error inequality is stated explicitly. The historical common per-class requirement below 2.6496827802505486e-5 is identified as a required additional budget, not an estimated error. The original arrays' arithmetic allowance is not charged twice. A strict sign for the continuous diffusion is not asserted without that additional evidence. This boundary does not remove the continuous model, alter the finite theorem, or abandon the economic choice question.

## F2. The cardinal primitive and its robustness

**Changes:** the “Preferences over Preference Changes” subsection and the new uniform cardinal-tilt proposition; Supplement S.12.2. **Evidence:** `primitive_robustness.json` and `mechanisms.json`.

We write utility as the integral of marginal consumption utility from reference consumption one plus a preference-state payoff b(u). The original formula corresponds to b(u)=1/(1-u). This grounds the cross-preference cardinal comparison as a distinct preference over preference states; fixed-u CRRA curvature alone does not identify it.

A new theorem establishes that, throughout the original probability–cost family, all common tilts a in [-0.25,0.25] preserve a relative option greater than 0.0004173. With the stated duration difference, the contract shift exceeds 0.0008346. The proof uses the inherited valid curvature bounds but couples the common cost in the two class bounds rather than taking incompatible adverse cost values separately. Feasibility and all rounded constants are supplied. The optimizer rows check the implementation and are not used as a proof of the continuum assertion.

The referee's contrary examples at a=1 and a=2 are independently reproduced and retained. We do not characterize those changes as harmless utility renormalizations. The dynamic experiment separately changes the common tilt and the reference-state payoff, recomputing all four class values. It does not transfer the two-stage no-adjustment invariance to a stochastic preference state. Indeed, the common tilt's dynamic effect differs from its two-stage effect; the new text explains that distinction rather than claiming the specialization calibrates the dynamic target.

## F3. A nondegenerate first-risk decision

**Changes:** the opening of the inherited risk-frontier section, the positive-duration subsection and proposition, and the explicit finite protocol.

The certified initial position is held over one eighth of a year, until liquidation. A continuous-time analogue must constrain a positive-duration interval and preserve that interval under temporal refinement. We prove that changing a bounded measurable control at a single deterministic instant changes neither its drift integral nor its stochastic integral, hence neither the stopped path nor its payoff. A literal singleton sign partition therefore has equal class suprema.

The old attainment-only wording has been replaced in the active R8 manuscript, not merely contradicted in a response appendix. The paper distinguishes an initial commitment-value difference, a lifetime duration feature, and a local Hamiltonian comparison with flow units. The original finite eight-date experiment is unchanged.

## F4. Mechanisms in the executed dynamic economy

**Changes:** dynamic feature accounting and reoptimization proposition; full-model mechanism tables and interpretation; Supplement S.12.3. **Evidence:** `mechanisms.json` contains 36 specification–contract comparisons and 144 class solves.

The full model retains k=2, endogenous consumption and investment, adjustment, preference and wealth shocks, stopping, and liquidation. We vary the common cardinal tilt, the preference-state payoff, liquidation payoffs, the operating-benefit contrast, the mixture weight, and an actual zero-covariance law. Both regimes and both first-risk classes are reoptimized in every comparison. An equal mixture of the two nonzero-correlation laws is not substituted for the zero-covariance intervention.

Six independently evaluated policy moments give an exact cardinal accounting. Baseline policies are also reevaluated under the changed primitive, and their additional gains from reoptimization are reported. The finite-policy envelope and add-and-subtract identity state exactly what this exercise establishes. We do not call the optimized-moment account an empirically identified causal decomposition.

The results are discriminating. Removing the reference-state payoff makes the relative option numerically negligible while preserving positive risk in both regimes. Increasing that payoff can produce a larger positive option while both regimes choose the nonpositive class. Altering liquidation or covariance can move both choices without eliminating the positive relative option. The paper therefore explains the interaction of preference formation, cardinal incentives, and boundary opportunities in the actual dynamic economy instead of relying on the option identity alone or on a two-stage calibration that was not performed.

## F5. Computational contribution at the same economic target

**Changes:** streaming economic-certificate implementation and its main-text comparison; Supplement S.12.4–S.12.5. **Evidence:** `decision_contest.json`, all coefficient and policy arrays, `streaming_validation.json`, and the arithmetic audit.

The comparison now targets the original full 1,568-action economy and its decision rectangle, not the generic 1e-3 welfare target. Chord and count use the same full-menu endpoint optima and lower policies. Both include model construction and frozen-proposal loading, anchor optimization, lower-policy evaluation, arithmetic auditing, and independent selected-control replay. The count upper bound is weakly sharper, but the less expensive corrected chord already certifies the same economically relevant signs. Stage and total timings are reported without claiming independent-machine medians or a universal solver ranking.

A separately constructed mesh-only lower bank is judged against the same full-menu upper target and also passes. This is evidence that newly learned proposals are not necessary for this particular decision. The three historical proposals are a common frozen input defining part of the target; their loading is charged, and historical training is explicitly distinguished from current execution. Adding an equal historical cost to all arms changes percentage savings but not the attributable difference between the upper components. No new neural training speedup is inferred.

The storage response is an implementation, not an upper-array ratio. The focal-state lower coefficients are streamed and reduced to intercept–duration arrays; complete policy indices are retained. Kernel and reward payload, lower coefficient storage, policy storage, and peak process memory are reported separately. The large kernel remains the dominant object. The inherited all-state/all-date result is preserved and is not claimed to come free with focal-state streaming.

Independent dense tests cover 60 models, 240 class recursions, and 720 parameter-point comparisons. The new arithmetic budget propagates endpoint errors into the signed correction and checks an a priori per-class allowance before acceptance. Small observed replay discrepancies are not substituted for this account.

## F6. Correspondence with the closest regional methods

**Changes:** “Correspondence with Regional Parameter Methods,” the related-literature discussion, and the bibliography.

We explicitly acknowledge that Quatmann et al. (2016) define parametric MDPs and reward properties. The revised comparison augments state by date, treats action rewards and terminal rewards, represents substochastic mass with a cemetery state without double-paying exits, and explains how signed rewards can be shifted without creating a policy-dependent survival reward. It distinguishes a common parameter from a reset relaxation, the order of action and law information, the count-informed upper recursion, feasible common-parameter lower policies, and the signed cross-operator compression.

Heck et al. (2025) is discussed for dependency-sensitive abstractions of parametric Markov chains, not silently identified with the controlled reward target. The paper claims the particular compression, its ordering and total error analysis, and its decision-specific computational use. It does not claim that regional expected-reward control first becomes possible here, and it does not call the internal chord/count experiment a benchmark of the complete external software systems.

## Minor presentation correction

The comparative-oracle section now distinguishes the common-bank frontier from the separately executed autonomous chord/count/cascade experiment. The latter's real timing evidence is retained.

## Delivery and evidentiary boundary

The main and supplementary entry points are `ECTA_R8.tex` and `SUPP_R8.tex`. The new branch preserves the latest review as its ancestor. The execution summary, source inventory, protected-history manifest, PDFs, and complete replay instructions accompany the manuscript. Passing these computational checks is not a representation of an Econometrica appointment, editorial decision, empirical calibration, exhaustive literature-priority search, or proof of a diffusion sign. It supplies a complete and substantially revised paper for the next independent review.
