# External Referee Report — R48

**Venue perspective:** Econometrica-level numerical and computational methods  
**Article:** *Certified Bellman Operators for Costly Policy Revision*  
**Repository:** `TrillionniumFoundation/NBO`  
**Reviewed branch:** `revision/econometrica-r48-end-to-end-witness-2026-09-26`  
**Reviewed HEAD:** `77b90a92250694271265e91f9624b7d6aacb0dea`  
**Prior report addressed by the revision:** `reviews/2026-09-26-econometrica-r47-second-pass/referee_report.md` at `a535a466ec4975dc14e2d46f73a690c72e11671e`  
**Review branch:** `review/econometrica-r48-numerical-methods-2026-09-26-77b90a9`  
**Date:** 2026-09-26

## 1. Recommendation

**Reject.**

R48 is a genuine redesign, not a cosmetic response to R47. It resolves several important objections from the preceding reports. The manuscript now identifies the exact finite occupation-flow relaxation represented by restart prices, proves that bilinear shared-successor budgets recover the original common-policy problem, supplies exact rational separation examples, constructs both endpoints from raw primitives and certified operating enclosures rather than inherited incumbents, implements target-dependent precision, freezes a new twelve-case evaluation before model generation, and proves an exact restriction–extension result for finitely supported objective laws under controlled finite-atomic dynamics. These are substantial scientific improvements. I did not find an obvious algebraic contradiction in the price/occupation duality, the shared-budget completion, the witness-only stopping theorem, or the finite-observation extension theorem.

The paper nevertheless remains below the standard of an Econometrica numerical-methods contribution.

The fresh numerical evidence is weak in exactly the dimension that matters most. The direct and price formulations each meet the registered absolute target in four of twelve primary cases. The price formulation therefore produces **zero additional target hits** relative to the fresh direct comparator. One of the four successes is a zero-cost case. The remaining successes are all at the smallest size level: the two branching successes use `(n,T,m)=(3,4,3)`, and the remaining positive root closure is also at that level. No nontrivial medium or large primary environment is closed. All eight cases left open by the direct method remain open with prices. The price formulation returns narrower intervals on those eight cases, but at greater aggregate measured cost—approximately 340.52 seconds against 286.26 seconds—and without changing the target-attainment count.

The theoretical advances also stop short of a practical solution method. The supremum of restart-price certificates is correctly characterized as a relaxation, not as the original optimum. Restoring common successor budgets introduces bilinear equations that reimpose the omitted common-policy coupling; this is an exact formulation, but not an efficient resolution of it. The executed price generator does not solve even the ideal clipped price problem in general: it caps prices at 4096, allocates five seconds, enumerates all initial masks only for `n<=4`, and otherwise tests only the full mask and positive-mass singletons. No computable bound quantifies the loss from the cap, mask truncation, or time limit.

The witness-only covering search is end to end and logically complete when caps are removed, but its sufficient completion remains exponential in `nTm`. The largest fresh finite problems have only eight states, twelve periods, and four actions, yet the 30-second/255-node runs still leave material gaps. The operating enclosures are cheap finite Bellman passes; the paper still does not demonstrate the method when globally valid operating witnesses are themselves the hard numerical object.

The new continuum theorem is mathematically useful but narrow. With finite initial support, finite horizon, finite action set, and finitely atomic transitions, the all-action forward closure is finite, so the objective can be reduced exactly to a finite graph and extended off that graph by an operating-best policy. This is an exact reachability reduction, not a general numerical method for diffuse continuous-state economies. The two reported fleet exercises have horizons two and three and only 13 and 76 active decision nodes. Their two-point initial law is deliberately different from the uniform initial law that generated the unresolved motivating cohort. All thirty earlier positive-cost uniform-initial randomized intervals remain open.

The economic application is also not yet an economic application in the journal sense. The fleet example uses designed primitives, an arbitrary conversion of one normalized cost unit to 500 dollars, and an arbitrary budget grid. It yields internally valid conditional budget statements, but no estimated transition law, observed implementation cost, uncertainty analysis, or welfare result. The twelve primary models are likewise synthetic deterministic-hash environments generated by the authors. A source freeze is valuable provenance; it is not external validation.

There is an additional review-object defect at the exact HEAD reviewed here. The branch contains no materialized R48 article PDF, no ordinary root `ECTA_R48.tex` entry, no R48 review index or build script, and no committed `paper/generated` directory. Yet the manuscript source calls `primary_rows.tex` and `fleet_rows.tex` through a macro that performs literal file inclusion. Those files are absent from the reviewed tree. The current R48 source therefore does not compile as committed, and the numerical tables needed to read the article are not part of the review object. This is not the main scientific reason for rejection, but it independently prevents the present HEAD from being a complete journal submission.

R48 is now a serious methodological paper with several publishable ingredients. The remaining gap is not best addressed by another certificate layer on the same architecture. A viable Econometrica submission would need a materially stronger result along at least one of three routes: an efficient and demonstrably competitive algorithm on difficult positive-cost problems; a paired approximation theory and executed solver for a diffuse continuous-state economic model; or a substantive economic application whose conclusions depend on the certification machinery.

## 2. Overall assessment

| Dimension | Assessment |
|---|---|
| Price/occupation-flow characterization | Substantive and plausibly correct |
| Shared-budget completion | Exact, but bilinear and computationally unresolved |
| Separation examples | Useful and clarifying |
| End-to-end use of operating witnesses | Real improvement over R47 |
| Independence from inherited incumbents | Successfully addressed in the fresh experiment |
| Finite-model correctness and replayability | Strong |
| Fresh target attainment | Weak: 4/12 for both methods |
| Incremental target attainment of prices | Zero |
| Medium/large positive-cost closure | None |
| Practical complexity | Weak; exponential completion and capped failures |
| External baseline | Missing from the fresh experiment |
| Continuum coverage | Exact only for finite-support, finite-atomic forward closures |
| Diffuse continuous-state target | Still open |
| Economic content | Designed contract, not empirical or calibrated application |
| Publication completeness at reviewed HEAD | Incomplete and not compilable as committed |
| Suitability for Econometrica | Insufficient |

## 3. What R48 genuinely accomplishes

The recommendation should not obscure the fact that R48 addresses several prior objections in a scientifically meaningful way.

### 3.1 It characterizes the price relaxation rather than overselling it

For finite models, the manuscript derives a linear occupation-flow program whose dual value equals the supremum of the un-clipped restart-price Bellman certificates. The edge-allocation variables make clear why incoming transitions may allocate a successor regret budget inconsistently. The added equations

`alpha[t,i,j] = f[t,i,j] * b[t+1,j]` and  
`gamma[t,i,j] = f[t,i,j] * (epsilon - b[t+1,j])`

restore one shared successor budget. This is a valuable conceptual clarification. The exact example with values `5/4 < 27/16 < 7/4` demonstrates both the gain over a constant multiplier and the remaining gap to the original common-policy optimum.

### 3.2 It corrects the clipped-objective issue

The manuscript no longer equates maximization of the full-mask un-clipped objective with maximization of the displayed clipped certificate. The mask characterization and the separate clipping counterexample are useful. This is a direct and satisfactory response to a weakness in R47.

### 3.3 It constructs an actual end-to-end finite pipeline

Each fresh run constructs directed operating enclosures, an initial conditional-cost policy, a local proposal, repaired feasible policies, price proposals, node relaxations, and a complete retained cover from raw primitives. No exact operating value, saved policy, old price field, or inherited endpoint is supplied to the run. The arithmetic reader reconstructs the endpoints exactly.

### 3.4 It implements adaptive precision

The witness routine starts at eight bits and increases precision until both the repair and capped-price amplification budgets meet the declared fractions of the target. This is materially better than invoking an asymptotic precision schedule while executing a fixed grid.

### 3.5 It gives an exact finite-observation continuum theorem

For finite-support initial laws and controlled finite-atomic transitions, the forward set under all action and shock sequences is finite. The off-set backward extension is a clean argument establishing global all-state feasibility without changing the objective. This gives a genuine paired certificate for the stated finite-observation Borel problem, not merely a discretized approximation.

### 3.6 It uses a prospectively frozen fresh sample

The scientific source hashes and protocol were fixed before generating the twelve primary environments. Every primary result, including capped failures, is retained. This is a significant improvement over repeatedly developing on the old cohort.

These strengths make the paper technically serious. The blocking findings below concern the remaining scientific and editorial threshold.

## 4. Blocking scientific and computational findings

### R48-F1 — The exact reviewed HEAD is not a complete, compilable journal submission

The branch contains the modular TeX source under `revisions/2026-09-26-r48/paper`, but it does not contain a materialized R48 PDF, a root article entry, a build script, a review index, or a numerical supplement. More importantly, `evidence.tex` literally inputs generated table files from `revisions/2026-09-26-r48/paper/generated`, while that directory and those files are absent from the tree.

The missing files are not optional decoration. They contain the primary and fleet tables on which the numerical claims depend. A reader cannot compile the source or inspect the paper in its intended typeset form from the reviewed commit.

**Required correction:** publish one immutable, self-contained review object containing the ordinary source, every generated table and figure, the article and supplement PDFs, build logs, and a manifest. The final paper branch—not an uncommitted local build—must reproduce successfully from that object.

### R48-F2 — The price formulation produces zero additional primary target hits

On the source-frozen sample, both formulations meet the `10^-3` absolute target in W0, I0, Q0, and T1. Prices tighten every one of the other eight intervals but close none of them. Thus the method-relative success count is

- direct formulation: 4/12;
- price formulation: 4/12;
- additional price closures: 0/12.

This is the most important empirical result and should dominate the interpretation. Narrower intervals can be useful, but the paper is presented as a numerical certification method with an explicit stopping target. On that criterion, the new price formulation does not improve the success count.

**Required correction:** center the abstract and conclusion on the zero incremental target-hit result. To support a stronger numerical-methods claim, demonstrate additional difficult positive-cost closures under the same total-work budget on a prospectively frozen suite.

### R48-F3 — Every substantive primary success occurs at the smallest scale

T1 is a zero-cost row. Q0 closes at the root. W0 and I0 require branching, but all three positive-cost successes use the smallest configuration `(n,T,m)=(3,4,3)`. No positive-cost medium case `(5,8,3)` and no large case `(8,12,4)` reaches the target under either formulation.

Consequently, “four of twelve” overstates breadth. The evidence is more accurately summarized as success on the easy/small level and failure on every nontrivial larger level.

**Required correction:** report target attainment by size and by positive-cost status in the abstract. A convincing revision must close a meaningful fraction of medium and large positive-cost rows, not merely reduce their intervals.

### R48-F4 — The eight open rows remain materially open

The paper reports price widths of approximately 0.01110, 0.01086, and 0.01174 on W2, I2, and Q2, and approximately 0.05238 on T2. T0 reaches the node cap with a nonzero width. These gaps are one to two orders of magnitude larger than the declared target.

The fact that T2 improves from a direct width near 0.95040 to 0.05238 is a real relaxation improvement, but it is still a failed certification at the registered accuracy. Precision is not the explanation: the tie witnesses are exactly represented at the initial witness level, so the remaining gap is optimization slack.

**Required correction:** provide structural diagnostics for every open row and demonstrate that the proposed algorithm—not merely the relaxation—can turn those improvements into certified target attainment.

### R48-F5 — The price method is more expensive in aggregate without closing more cases

Across the twelve primary cases, measured all-in work is about 286.26 seconds for the direct formulation and 340.52 seconds for the price formulation, an increase of roughly 19 percent. The price formulation processes fewer nodes in some cases because each node is more expensive. It returns tighter intervals but the same target count.

A single 30-second soft construction cap does not produce a full performance profile. It is unknown whether direct search would dominate at shorter budgets, whether price search would eventually convert its tighter roots into more closures, or whether the ranking reverses at different accuracy levels.

**Required correction:** report certified gap-versus-total-work curves under several common budgets, including all oracle, proposal, pricing, search, serialization, and verification costs. The relevant comparison is the Pareto frontier of certified width against cumulative resources.

### R48-F6 — The implemented price generator does not solve the theoretical clipped price problem

The theory characterizes the clipped supremum through a maximum over initial-support masks. The implementation, however,

- caps every price at 4096;
- allocates at most five seconds to price generation;
- enumerates all nonempty masks only when `n<=4`;
- for larger models tries the full mask and positive-mass singletons only;
- uses floating LP output merely as a rationally replayed proposal.

These choices preserve validity, but no error bound relates the executed lower certificate to the theoretical price supremum. The distinction becomes more consequential precisely in the medium and large cases where mask enumeration is truncated.

**Required correction:** derive a computable cap/truncation bound or provide a convergent price-and-mask enrichment algorithm with a stopping test. At minimum, execute cap, time, and mask-sensitivity studies on the failed rows.

### R48-F7 — Shared-budget completion is an exact reformulation, not an efficient solution

The shared-budget equations correctly identify the coupling omitted by the occupation relaxation. They are bilinear in edge flows and successor budgets. Adding them restores the original nonconvex common-policy problem; it does not establish that the price method solves that problem efficiently.

The numerical algorithm therefore returns to probability-box branch-and-bound with McCormick relaxations. The strongest conceptual theorem explains the relaxation gap but does not eliminate it. The paper should not allow “common-budget completion” to sound like a tractable strong-duality result for the original problem.

**Required correction:** distinguish exact formulation from algorithmic resolution everywhere. A stronger contribution would supply exploitable structure, decomposition, convexification under substantive assumptions, or a convergence-rate result for restoring common budgets.

### R48-F8 — Finite completion remains exponential and is tested only at modest dimensions

The stopping proof bisects probability coordinates in a space of dimension `d=nTm`. The sufficient depth is proportional to `d log(1/w*)`, implying an exponential node bound. The largest fresh model has `d=8*12*4=384`, which is already far smaller than many economic dynamic programs, yet the 255-node and 30-second runs fail on every large positive-cost case.

The theorem establishes decidability under finite precision refinement. It does not establish practical scalability. The proof size and rational residual calculations also become material: even a medium W1 price run produces a proof object of roughly half a megabyte and uses about 235 MiB process high-water memory, while still ending at the time cap.

**Required correction:** add systematic scaling in `n`, `T`, `m`, beta, and epsilon separately; report memory, proof size, node throughput, and certified gap; and provide complexity-reducing structure beyond exhaustive policy-probability partitioning.

### R48-F9 — The fresh comparator is internal, not an external numerical baseline

The direct and price formulations share the same driver, witness constructor, greedy incumbent, local proposal, branching infrastructure, arithmetic residual machinery, and verification ecosystem. This is a controlled formulation ablation, not an independent benchmark against the state of the art.

Historical SCIP results were often numerically favorable but remain outside the exact lower-bound boundary. R48 does not rerun a modern global solver on the new source-frozen cases, nor does it post-certify such a solver's cover.

**Required correction:** include at least one strong external solver or independently implemented method on the same raw problems and total-work budgets. Either use independently checkable proof logging or reconstruct an external branch-and-bound cover rationally.

### R48-F10 — The “fresh sample” is too small and too internally designed to establish general performance

The source freeze is good practice, but the sample contains only one deterministic-hash environment for each family/size cell: twelve primary cases in total. The generator, solver, theorem, and evaluation protocol are all authored within the same project. There are no repeated draws, third-party instances, public benchmark problems, or uncertainty intervals for success rates.

The tie rows are three sizes from one construction family. Warranty, inventory, and queue labels add variety, but all share the same code path, finite action structure, rational data, and all-restart objective.

**Required correction:** freeze the final algorithm and evaluate it on a substantially larger suite that includes multiple seeds per cell, third-party or independently authored instances, adversarial cases, and all failures. Report distributions of certified width and cost rather than a twelve-row count alone.

### R48-F11 — The scaling design is completely confounded

Across levels, state count, horizon, action count, discount factor, operating allowance, and initial support all change together. In particular, the largest level simultaneously has more states, more periods, more actions, beta closer to one, a tighter epsilon, and an initial law supported only on two states.

The observed deterioration cannot be attributed to dimension, horizon, discounting, tolerance, or sparsity. It therefore provides little empirical support for the paper's numerical complexity discussion.

**Required correction:** use a factorial or one-factor-at-a-time scaling design around fixed base models. Include repeated runs and report both absolute and normalized work/error measures.

### R48-F12 — The operating-witness challenge remains easy in the executed experiments

R48 now genuinely generates prices and policies from witnesses rather than exact operating values. That is an important correction. But each witness is obtained by a directed finite Bellman pass over at most eight states and twelve dates. This is not the regime that motivates approximate dynamic programming.

No fitted value function, sparse grid, simulation-based expectation enclosure, neural approximation, high-dimensional state, or expensive robust expectation is used. The paper therefore validates the error interface, not the method's usefulness when constructing globally valid witnesses is the central difficulty.

**Required correction:** execute an end-to-end example with a genuinely nontrivial operating oracle. Charge all witness construction and expectation-verification work and report how price amplification affects the final revision interval.

### R48-F13 — The continuum theorem is a finite-reachability theorem with a narrow objective-law condition

The exact restriction–extension theorem is correct-looking and useful. Its computational content follows because, under finite support, finite horizon, finite actions, and at most `S` atoms per transition, the all-action reachable set contains at most `|H0|(mS)^t` points at date `t`.

This is not a generic continuous-state approximation theorem. It does not cover diffuse objective laws, continuous shocks, continuous actions, or kernels with densities. The exponential forward graph may also become larger than a conventional grid very quickly. Exact equality of rational successor states must be decidable.

**Required correction:** narrow the title and broad continuum claims to finite-observation atomic systems, or add a paired approximation theorem and executable stopping rule for diffuse initial laws and genuinely continuous kernels.

### R48-F14 — The fleet calculations are small designed finite graphs, not evidence for broad continuous-state scalability

The fleet exercises have horizons two and three. Their active decision-node counts are 13 and 76. The finite forward sets are exact and the full-state extension is analytically valid, but the optimization problems themselves are small finite graphs.

The reported near-zero price widths therefore demonstrate a favorable finite-support special case. They do not validate the method on the original uniform-initial continuous problem, a long horizon, or a high-dimensional condition process. The manuscript correctly states that the old thirty positive-cost intervals remain open; that boundary is decisive for journal fit.

**Required correction:** solve a materially larger controlled-atom problem and, more importantly, provide paired results under a diffuse initial law rather than changing the economic objective to a two-point population.

### R48-F15 — The economic application is illustrative rather than substantive

The fleet contract uses the original affine synthetic primitives, not data. The initial fleet consists of two selected condition points with fixed weights. One normalized implementation unit is declared to equal 500 dollars, and the budget grid is selected as 100, 250, 500, and 1,000 dollars. The resulting budget statements are mechanically correct conditional on these choices.

They do not constitute empirical economic evidence. There is no estimation, calibration discipline, model uncertainty, institutional validation, or welfare analysis. A different arbitrary unit conversion changes the headline dollar conclusions proportionally.

**Required correction:** either remove the monetary framing and present the exercise honestly as a numerical illustration, or add a genuine application with disciplined primitives, uncertainty, and an economically meaningful decision loss.

### R48-F16 — A common absolute target is not an economically comparable accuracy standard

The `10^-3` target is invariant across models whose objective scales and upper costs differ. Target attainment is therefore sensitive to arbitrary normalization. The paper acknowledges that cost scaling should scale the target, but the headline count still treats all twelve rows identically.

For the illustrative 500-dollar conversion, `10^-3` corresponds to 50 cents, an accuracy far finer than the economic budget distinctions being discussed. Conversely, a failed absolute target can coexist with an economically negligible relative interval in a large-cost problem.

**Required correction:** retain the registered absolute target for protocol integrity, but make relative width, certified decision loss, and application-specific budget separation equally prominent. Report conclusions that are invariant to arbitrary unit changes.

### R48-F17 — The tie evidence does not show robust tie handling in computation

The tie formulation is algebraically valid without a strict action gap, which is a strength. Computationally, however, T1 is a zero-cost closure, while T0 and T2 remain open. The tied operating witnesses are exactly representable, so witness error cannot explain the failures.

The result is therefore: validity at ties, one trivial closure, and two optimization failures. It does not establish that the price formulation is practically robust to large or time-varying optimal faces.

**Required correction:** report face dimensions, price fields, shared-budget residuals, root versus tree gains, and target performance across several prospectively frozen tie families—not only three sizes of one generator.

### R48-F18 — The literature positioning remains far too thin

The current bibliography contains only nine items. The paper needs a substantially deeper comparison with constrained MDP occupation formulations, semi-infinite and generalized moment programs, adjustment and switching-cost models, stochastic programming duality, spatial branch-and-bound, verified global optimization, robust dynamic programming, safe policy improvement, and numerical economics.

The restart-price occupation relaxation and common-budget completion may be novel in this exact form, but the manuscript does not establish that novelty relative to the closest mathematical formulations. Nor does it explain what standard occupation or nonlinear programming approaches would return on the same finite problem.

**Required correction:** provide a comprehensive theorem-level literature map and precise novelty claims. Compare formulations, not only broad fields.

### R48-F19 — Verification is strong but not independent scientific replication

The arithmetic reader is separately written and the contract tests are useful. Nevertheless, the generator, constructor, checker, theorem specification, and interpretation share one repository and one mathematical design. Both formulations use the same driver and candidate machinery. Common-mode modeling errors can survive all internal checks.

The source-freeze and evaluation-complete files are self-authored provenance records. They establish chronology and identity, not external preregistration or independent correctness.

**Required correction:** obtain an independently implemented replication of representative cases, preferably in another language or optimization stack, and release a minimal external-facing benchmark specification from which third parties can reconstruct the target without importing project code.

### R48-F20 — The manuscript still combines more scope than the evidence supports

The paper contains finite occupation duality, bilinear completion, exact separation examples, witness-only branch-and-bound, finite-observation continuum transfer, a synthetic fresh benchmark, a designed fleet contract, and a preserved archive of earlier results. Each component is individually interesting, but the numerical evidence does not support all of the resulting scope.

A tighter paper could make a strong contribution around one of two objects:

1. the exact price-relaxation/common-budget theory, with focused computational diagnostics; or
2. a verified finite-support atomic-control solver, with serious scaling and an application.

The present title and narrative continue to suggest a general certified Bellman method for costly policy revision, while the successful algorithmic evidence is limited to small finite problems and finite reachable graphs.

**Required correction:** reduce the central claim and reorganize around one theorem–algorithm–application chain. Preservation of historical material need not imply inclusion in the scientific argument.

## 5. Minimum requirements for a substantially redesigned submission

The following are not minor-revision requests. A future submission should satisfy a coherent subset sufficient to establish one clear contribution.

1. **Publish a complete immutable review object.** Include all generated files, PDFs, source, scripts, logs, manifests, and a one-command build.

2. **Demonstrate nontrivial prospective closures.** The final algorithm should close a meaningful fraction of medium and large positive-cost instances under fixed total budgets, not only tighten failed intervals.

3. **Quantify price-generation suboptimality.** Supply a convergent cap/mask enrichment procedure or computable loss bounds for the executed price portfolio.

4. **Use an external verified comparator.** Compare certified gap versus time and memory against an independently implemented global method.

5. **Provide interpretable scaling.** Vary dimensions, horizon, discounting, actions, and tolerance separately over multiple instances.

6. **Test a difficult operating oracle.** Use approximate operating values whose global enclosure is a genuine numerical task and charge that work.

7. **Advance the diffuse continuous-state problem.** Give a paired computable convergence theorem and an executed example under a diffuse initial law, or narrow all continuum claims to finite-support atomic systems.

8. **Add economic substance.** Analyze a calibrated, estimated, or institutionally disciplined application with uncertainty and economically meaningful accuracy.

9. **Expand the literature and novelty analysis.** Position each theorem against the closest occupation, duality, and verified-optimization results.

10. **Obtain external replication.** Separate mathematical correctness, arithmetic verification, and performance generalization through an independent implementation.

## 6. Additional technical and presentation comments

1. Put a table in the abstract or introduction separating zero-cost, root, branching, medium/large, and method-relative closures.

2. Report exact upper costs and relative widths beside every absolute width in the main primary table.

3. For each open row, report the root lower, final lower, initial upper, final upper, and the fraction of improvement attributable to upper versus lower movement.

4. Show certified gap versus cumulative all-in time for every case, not only final endpoints.

5. Report method-specific memory in separate processes; the current sequential family process prevents a clean comparison.

6. Include the number of LP variables, constraints, products, leaves, proof bytes, and verifier time for every run in one table.

7. State the exact number of masks attempted and LP statuses for every price run.

8. Add price-cap sensitivity at, for example, 256, 1,024, 4,096, and 16,384 on all failed rows.

9. Add mask-enrichment sensitivity for `n>4`, including pairs and selected larger subsets.

10. Distinguish the ideal clipped price supremum, the capped proposal value, the rational replay value, the root relaxation value, and the full-tree lower endpoint in every diagnostic table.

11. Give the occupation-flow primal witness corresponding to selected finite price certificates, not only price fields.

12. Quantify violation of shared-budget compatibility in the occupation relaxation and relate it empirically to the final optimization gap.

13. The common-budget completion theorem should state clearly whether zero-flow edges permit arbitrary budgets and how these are handled numerically.

14. Report numerical conditioning and rational bit lengths of reconstructed prices and residuals.

15. Explain why the fixed cap 4096 is economically and numerically reasonable; at present it is only protocol-fixed.

16. The witness precision table should report `xi/s`, price amplification, selected bits, and oracle time for every individual row, not only aggregates.

17. The upper-repair theorem requires `xi < (1-beta)epsilon`; highlight how severe this becomes as beta approaches one and epsilon shrinks.

18. For the level-2 models, explain the effect of placing initial mass only on two states while retaining all-state constraints. This changes both objective conditioning and the clipped mask problem.

19. Separate target failure caused by upper-policy weakness from failure caused by lower-bound weakness.

20. Report how often the local optimizer improves the greedy incumbent and by how much after exact repair.

21. The branch rule alternates widest-coordinate fairness with product defect. Provide ablations against pure widest, strong branching, and reliability branching in a separately frozen study.

22. Clarify whether time-cap overruns caused by completing exact operations are included consistently for both methods.

23. State the largest denominator and numerator bit lengths in the proof objects and their effect on replay cost.

24. For the fleet graphs, report the number of duplicate successor merges and the unmerged path count.

25. Demonstrate the off-forward-set extension on representative queried states and state its compilation cost.

26. The phrase “zero spatial approximation error” is correct for exact closure but can mislead readers about computational difficulty. Always pair it with the exponential graph-size bound.

27. Do not call the fleet tasks “observed” without immediately stating that the states and weights are designed rather than drawn from data.

28. Remove or de-emphasize dollar conclusions unless the conversion is institutionally grounded. Normalized-unit budget separation is sufficient for a numerical illustration.

29. Report sensitivity of the fleet conclusion to the two-point weights, epsilon, and lottery-administration cost.

30. Add at least one diffuse-law experiment, even if it fails, to quantify the gap between the exact finite-support theorem and the motivating target.

31. Reproduce the old uniform-law intervals only as a clearly separated historical benchmark; do not let archive volume substitute for progress on them.

32. The tie generator uses a hidden potential to construct rewards. Explain how representative this geometry is and publish independent tie generators not based on that device.

33. The comparison should include solution quality under a fixed proof-size budget as well as a time budget.

34. Expand the bibliography substantially and identify the closest existing nonlinear occupation formulations.

35. Add a concise theorem-assumption-evidence matrix to the main paper, not only the supplement.

36. Distinguish analytic Borel measurability from what the finite contract checker verifies in every summary claim.

37. State explicitly that exact rational replay proves the serialized finite inequalities, not correctness of the model generator or theorem.

38. Make all publication artifacts available from a stable root review index rather than requiring readers to infer paths under `revisions/`.

39. Include a clean-room reproduction command that does not depend on uncommitted generated files.

40. If the paper retains the broad title, the conclusion must summarize the unsolved diffuse-law and medium/large cases at least as prominently as the successful finite-support examples.

## 7. Final editorial view

R48 deserves substantial credit. It answers the strongest conceptual criticism of R47 by identifying exactly what restart prices optimize and by refusing to equate that relaxation with the original common-policy value. It also replaces inherited-incumbent evidence with a genuinely end-to-end witness-only pipeline and supplies an exact finite-observation transfer theorem. These are meaningful research contributions.

The numerical evidence, however, remains too weak for Econometrica. The new price formulation adds zero fresh primary target hits, all substantive closures occur at the smallest scale, every medium and large positive-cost row remains open, aggregate work is higher than for the direct formulation, and no external verified method is compared. The continuum success reduces to small finite forward graphs under a two-point objective law, while the motivating diffuse-law intervals remain unresolved. The economic illustration is synthetic and arbitrarily scaled. Finally, the exact reviewed HEAD is not a complete compilable publication object.

The project has reached the point where further repository sophistication or another relaxation on the same small suite would have sharply diminishing scientific value. The next credible step is a narrower theorem with decisive evidence, a materially more capable solver, or a real economic application.

**Recommendation: Reject.**
