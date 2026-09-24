# External Referee Report — R40

**Venue perspective:** Econometrica-level numerical and computational methods  
**Article:** *Certified Bellman Operators for Costly Policy Revision*  
**Repository:** `TrillionniumFoundation/NBO`  
**Reviewed branch:** `revision/econometrica-r40-referee-complete-2026-09-25`  
**Equivalent referee-copy branch:** `revision/econometrica-r40-referee-copy-2026-09-25`  
**Reviewed HEAD:** `d221ddf2fd34b60fc8b1f08526a22c61098d966c`  
**Prior external report addressed by this revision:** `reviews/2026-09-25-econometrica-r38/referee_report.md`  
**Review branch:** `review/econometrica-r40-numerical-methods-2026-09-25-d221ddf`  
**Date:** 2026-09-25

## 1. Recommendation

**Reject in the present form.**

R40 is a materially stronger paper than R38. The revision no longer relies only on a deterministic necessary-action relaxation. It makes the common randomized Markov policy the central object, proves a backward feasibility-repair lemma, derives a complete finite-state probability-lattice construction, gives a stopping theorem for a rational branch-and-bound search, adds a witness-driven version that does not require exact operating values, and states an end-to-end continuous-state transfer result under a certified total-variation reset approximation. The direct McCormick comparator targets the same finite constrained problem. The eight finite environments were prospectively frozen, failures and time caps are retained, and the paper correctly distinguishes the old 42-case development cohort from a prospective audit suite. The direction of the strict-randomization comparison is also correct: a feasible lottery upper cost is placed below a deterministic lower bound. I did not find an obvious contradiction in the core repair argument, the finite lattice theorem, or the inspected rational branch-and-bound code.

These improvements resolve several objections in the R38 report. They do not resolve the central journal-fit problem. The complete method is exponential, with repair constants that become severe when the discount factor is close to one, the operating tolerance is small, or the horizon grows. Under the prospectively fixed budget, the harder two-state and four-state rows remain open, and the verified McCormick comparator is substantially stronger than the paper's interval-Bellman search on every long-horizon pair. The continuous transfer theorem applies to kernels admitting uniform total-variation reset approximation, while both headline continuous-state experiments have atomic transition laws and are explicitly outside that theorem. No executed continuous-state example actually instantiates the advertised end-to-end transfer bound. On the original development cohort, all 30 positive-cost randomized intervals remain nonzero, with maximum relative widths of 14.61%, 32.29%, and 34.23% at horizons 4, 8, and 12. In the nonlinear two-state experiment, selected certified intervals remain 25%–76% wide, the operating allowance is 0.5, and the tighter 0.05 exercise has lower bounds but no certified upper policies.

The paper therefore proves completeness for a restricted finite-state problem and for a restrictive class of total-variation-approximable continuous models, but does not demonstrate a practically useful global numerical method for the atomic continuous-state models that motivate and dominate the evidence. Nor does it provide a substantive economic application, calibration, estimation layer, or welfare conclusion. The strongest empirical result is a valid comparative statement—randomization can beat every deterministic feasible policy in 27 synthetic development configurations—not a solution of the randomized optimum. That statement is interesting, but it is not sufficient for an Econometrica numerical-methods article of this scope.

A further incremental revision that merely adds larger ledgers, more support prices, or more runs on the same development cohort would not be enough. A viable submission would need either a practically effective and certified method for the atomic continuous models, a convincing application to an economically important model, or a substantially sharper theoretical contribution relative to existing constrained-MDP approximation and global-optimization methods.

## 2. What R40 genuinely fixes

The rejection recommendation should not obscure the real progress.

1. **The policy class is now coherent.** The paper centers one common randomized Markov kernel at each date and state. It no longer substitutes a history-conditioned frontier or separate restart-specific continuation for the uniform-initial Markov objective.

2. **There is now an actual end-to-end finite-state theorem.** The backward repair converts approximate all-restart feasibility into exact feasibility. The probability-lattice theorem and the interval-search stopping result converge to the original constrained randomized optimum, not merely to a one-step necessary relaxation.

3. **Operating approximation is integrated into the error budget.** The witness-driven theorem separates witness width, Bellman residual, policy-lattice error, and repair cost. This is a meaningful improvement over treating the exact operating value as a free oracle.

4. **The continuous-state assumptions are stated honestly.** The paper explicitly says that weak or spatial approximation of atomic successors is not total-variation approximation. It does not claim that the primary affine-shock model or the nonlinear bilinear model falls under the reset theorem.

5. **The comparator is now same-object.** The McCormick/RLT formulation uses the same common policy, initial law, operating constraints, and implementation objective. Floating-point LP output is converted into a rational lower certificate rather than trusted directly.

6. **The strict-randomization result is validly oriented.** A certified feasible lottery upper cost is compared with a deterministic lower bound. The paper does not infer strict benefit merely because a randomized lower bound is below a deterministic cost.

7. **The audit discipline is strong.** Prospective seeds and budgets are committed before the finite suite is generated; stopped runs remain in the tables; zero-cost cases are separated from positive-cost searches; independent verifiers have clearly stated boundaries.

These are substantial corrections. They raise the paper from an audit-heavy collection of relaxations to a genuine methodological attempt. The remaining objections concern scope, practical effectiveness, novelty, and economic importance.

## 3. Overall assessment

| Dimension | Assessment |
|---|---|
| Correctness of the stated repair and finite completeness logic | Plausibly correct; no obvious contradiction found in the inspected argument/code |
| Transparency and reproducibility | Very strong |
| Same-object finite comparator | Strong and useful |
| Practical finite-state performance | Weak beyond very small or short-horizon rows |
| Continuous-state convergence | Theorem is explicit but applies to a restrictive TV-reset class not used by the headline models |
| Primary randomized optimization | Unresolved in every positive-cost row |
| Nonlinear multi-state evidence | Positive lower bounds are an improvement, but intervals remain very wide |
| Independent verification | Strong for selected objects, incomplete for the hardest/final nonlinear row |
| Economic content | Synthetic and uncalibrated |
| Novelty relative to constrained-MDP approximation/global optimization | Not yet established at Econometrica level |
| Suitability for Econometrica | Insufficient |

## 4. Blocking scientific findings

### R40-F1 — The convergence theorem does not cover the paper's two headline continuous-state models

The paper's strongest theoretical statement for continuous states requires a certified reset approximation in total variation. The approximating kernel must send every point in a cell to a mixture of fixed within-cell reference measures, with a uniform operator bound against every bounded Borel test function. The initial law must also decompose exactly through the same reference measures.

This is a legitimate sufficient condition. It is also much stronger than the spatial approximation available for deterministic or finitely atomic transitions. The paper correctly acknowledges that both the one-dimensional affine-shock maintenance model and the two-dimensional bilinear model are atomic and therefore do not satisfy the transfer assumption under ordinary cell smearing. Consequently, the theorem that turns finite search into a convergent continuous-state method does not justify the main primary intervals, the nonlinear intervals, or their observed mesh trends.

More importantly, R40 contains no executed continuous-state example for which the reset constants `d_r`, `d_k`, `d_g`, and `alpha_h` are constructed, the tightened and relaxed finite problems are solved, and the total error bound is numerically closed. The paper proves that such an exercise is possible under suitable densities; it does not demonstrate that the constants are useful on an economic model.

The result is a scope mismatch. The theory is complete on one model class, while the evidence is concentrated on a different class for which no convergence theorem is supplied.

**Required correction:** execute the complete transfer pipeline on at least one nontrivial continuous-state economic model satisfying the stated assumptions, with all primitive, finite-solver, and repair terms reported. Alternatively, develop a validated approximation theory for the atomic transition models that constitute the paper's main evidence. The current theorem-plus-disclaimer architecture is mathematically honest but methodologically incomplete.

### R40-F2 — Completeness is obtained through an exponential construction with practically severe constants

For an `n`-state, `m`-action, `T`-period problem, the probability-lattice theorem may enumerate

`binom(M+m-1,m-1)^(nT)`

policies. The interval-search stopping theorem likewise gives a full binary-tree bound exponential in the number of state-date probability coordinates. The paper does not claim polynomial complexity, which is appropriate. But the practical implications are more serious than the prose suggests.

The repair modulus contains `(1-beta) epsilon` in the denominator. In the paper's common setting `beta=0.95` and `epsilon=0.01`, the fixed slack is only 0.0005. Unless the approximate feasibility error is much smaller than this number, the repair fraction can be close to one. The perturbation constants also accumulate weighted remaining-horizon terms. Thus the theoretical stopping width can require extraordinarily fine probability boxes precisely in the long-horizon, high-discount, tight-tolerance settings of economic interest.

The prospective computations confirm this. The method closes or nearly closes short cases, but it does not reach the prescribed 0.001 gap in the long rows under 4,096 nodes and a 60-second cap. A theorem asserting finite termination at an astronomically large depth is not by itself a practical numerical method.

**Required correction:** derive and demonstrate problem-dependent contraction or curvature arguments that materially reduce the worst-case search, provide error-versus-work scaling over several orders of magnitude, and show nontrivial closure beyond four states and short horizons. The paper must distinguish formal decidability from computational usefulness much more sharply in the abstract and conclusion.

### R40-F3 — The same-object McCormick comparator dominates the proposed interval search on the difficult prospective rows

The direct comparator is one of the strongest parts of R40, but its results are unfavorable to the proposed interval-Bellman method.

Under matched information and the precommitted caps:

- two states, horizon 8: interval search leaves a 19.45% relative gap; McCormick leaves 5.28%;
- two states, horizon 12: interval search leaves 5.47%; McCormick leaves 1.46%;
- four states, horizon 8: interval search leaves 40.58%; McCormick leaves 21.01%;
- four states, horizon 12: interval search leaves 26.34%; McCormick leaves 11.79%.

The stronger program costs more per node and reaches the time cap, but it gives a substantially better certificate in every hard pair. The paper appropriately does not claim dominance. That restraint also raises the central question: what is the numerical contribution of the Bellman-specific search beyond a proof-oriented implementation of generic branch-and-bound?

In the short rows, both methods solve tiny problems. In the long rows, neither closes the interval, and the classical global-programming formulation is stronger. This is not persuasive evidence for a new numerical method at the target journal.

**Required correction:** show a class of economically meaningful problems in which the proposed structure yields a decisive computational advantage over strong global-optimization formulations, or recast the method as a verification layer around existing solvers rather than as a competitive solver. Comparisons should include memory, node quality, bound improvement per second, and scaling in `n`, `m`, and `T`.

### R40-F4 — The primary randomized optimum remains unresolved in every nontrivial row

The development cohort has 42 configurations. Twelve are exact zero-cost cases. All 30 positive-cost common randomized Markov intervals retain nonzero width. The maximum gap divided by the upper endpoint rises from 14.61% at horizon 4 to 32.29% at horizon 8 and 34.23% at horizon 12.

The 27 strict gains over deterministic policies are valid and interesting: a feasible randomized deployment is cheaper than a lower bound for every deterministic feasible policy. But this is a comparative policy-class result, not a global solution of the randomized problem. It does not identify the randomized optimum, establish near-optimality of the lottery, or show that the remaining interval is economically negligible.

The distinction matters because the title and abstract emphasize global certification. On the paper's oldest and most developed benchmark, the method has still not closed one positive-cost randomized optimum. The widening horizon profile is exactly where a dynamic numerical method should demonstrate strength.

**Required correction:** reorganize the headline results around the actual status of the randomized intervals, not around the count of deterministic separations. Report median and maximum relative widths, guaranteed savings `(K_D lower - randomized upper)`, and unresolved randomized optimality separately. A publishable numerical claim requires closing or tightly bounding a substantial number of positive-cost rows, including longer horizons.

### R40-F5 — The atomic primary bounds are one-shot certificates, not a convergent numerical sequence

For the primary atomic model, the lower endpoint is assembled from finite support prices, a connected local program, and whole-domain witness bounds. The upper endpoint comes from a specific backward lottery. These are valid one-sided constructions. R40 supplies no theorem that adding support prices, local multipliers, cells, or lottery candidates drives their gap to zero for this continuum atomic problem.

The finite-state complete search cannot simply be invoked because the state is continuous, and the reset transfer cannot be invoked because the transition kernel is atomic. Thus the central primary table is not an incomplete execution of a known convergent algorithm; it is an interval produced by two useful but structurally unmatched constructions.

This is the most important remaining methodological gap. The paper has solved finite-state completeness and a separate continuous aggregation theorem, but not the continuous atomic problem actually used to claim economic gains.

**Required correction:** provide a validated convergence mechanism for the atomic continuum problem—such as a structure-preserving state partition, exact symbolic reduction, or another complete enclosure method—or narrow the article to finite-state and TV-reset models. Observed improvement from additional support prices is not a convergence theorem.

### R40-F6 — The nonlinear experiment is still far from an optimality result

Replacing a zero lower endpoint with a positive lower endpoint is genuine progress. The resulting intervals remain very wide:

- `T=8, N=64`: 76.01% relative gap;
- `T=16, N=128`: 45.32%;
- `T=32, N=64`: 61.05%;
- `T=32, N=128`: 35.11%;
- `T=32, N=256`: 25.13%.

The full table also contains coarse configurations with relative gaps near 100% and rows for which no feasible upper candidate is certified. The operating allowance is 0.5, much looser than the 0.01 and 0.05 primary allowances. At the tighter 0.05 allowance, the four reported exercises are explicitly lower-bound-only because no matching feasible upper policy exists.

There is no atomic-state convergence theorem, so the decline in selected gaps as the grid changes cannot be extrapolated to a continuum optimum. The finest `T=32, N=256` headline row is not independently verified; the independent label applies to selected neighboring objects, including `T=32, N=128`, not the finest row.

**Required correction:** produce paired lower and upper certificates at economically meaningful tolerances, prove convergence for the atomic box representation, and independently verify the finest reported object. A 25%–76% interval under a tolerance of 0.5 is an exploratory feasibility result, not evidence of high-dimensional certified optimization.

### R40-F7 — The prospective suite is credible but too small and homogeneous to establish general performance

The protocol is a real improvement: seeds, solver hashes, node budgets, time caps, and tolerance were committed before execution. However, the resulting suite contains only eight synthetic environments generated by one rational maintenance template. It uses two or four states, two actions, horizons 3, 4, 8, and 12, and an installed action that is structurally simple.

This is not a meaningful stress test of the theorem's general finite-action statement, the witness-driven operating approximation, or the proposed economic breadth. No finite experiment has more than four states or more than two actions. No model has a nontrivial estimated transition law, multiple constraints, a large action set, or a difficult operating solve. The holdout is prospective relative to the code, but not external evidence of broad numerical usefulness.

**Required correction:** freeze and evaluate a much broader suite spanning larger state spaces, at least three actions, heterogeneous transition structures, multiple tolerance regimes, and applications not generated by the same maintenance template. The evaluation should include strong off-the-shelf global solvers and report all failures under fixed budgets.

### R40-F8 — The witness-driven theorem is not demonstrated where operating approximation is actually difficult

The witness theorem is potentially useful. It avoids passing the exact operating value to the repair and gives a computable budget involving witness width, Bellman residual, and policy discretization. Yet the principal continuous maintenance experiment has an exact operating solve taking negligible time, and the finite audit models also have exact finite operating dynamic programs.

The paper therefore does not show the theorem performing its intended role: controlling a difficult approximate operating solution while simultaneously delivering a useful global revision interval. Small finite witness-refinement tables do not establish that the constants remain informative when operating approximation is the bottleneck.

**Required correction:** apply the witness-driven method to a model where exact operating dynamic programming is unavailable, report certified witness construction cost, residuals, repair margins, and final revision gaps, and compare with a reference solution where possible. Otherwise the theorem remains largely disconnected from the numerical evidence.

### R40-F9 — The continuous transfer assumptions are restrictive and the reported rate hides severe dimensional and tolerance constants

The reset theorem requires a uniform operator error over all bounded Borel functions, exact use of within-cell reference measures, and an initial-law representation through those same measures. A transition density with strong uniform regularity can satisfy the condition, but many economic models contain deterministic state components, discrete shocks, occasionally binding constraints, or singular transitions that do not.

Even in the density case, the stated `O(h)` primitive error is multiplied by horizon- and discount-dependent operating and cost envelopes, while the number of cells grows as `h^{-dim X}`. The repair term becomes poorly conditioned when `(1-beta) epsilon` is small. The paper acknowledges the curse of dimensionality but does not quantify the resulting total work or exhibit useful constants.

The model-uncertainty proposition is similarly demanding: it assumes operating and cost errors uniform over every common policy, state, and date. The current numerical margins set the uncertainty radii to zero. Thus the robust interpretation is formal rather than empirically operational.

**Required correction:** provide computed constants and complexity for a representative density model, clarify how reference measures and the initial law are constructed, and show how the total certificate behaves with dimension, discounting, and tolerance. The current transfer result should not be presented as broad continuous-state scalability.

### R40-F10 — The economic contribution remains synthetic and uncalibrated

The maintenance primitives, revision weights, tolerances, installed rules, initial laws, and randomization permissions are designed. The neural and spline incumbents are computational policies, not estimated organizational rules. No data discipline the transition law or the implementation cost. There is no sampling uncertainty, parameter estimation error, or monetary welfare interpretation.

The administration-cost threshold is mathematically valid under its assumptions, but those assumptions are strong: randomization overhead does not affect operating payoffs or dynamics, deterministic policies pay no analogous overhead, and a deterministic lower bound and lottery upper cost are compared under known primitives. In the current results the model-error radii are `a=b=0`.

The 27 strict separations therefore show that randomization can matter in designed examples. They do not establish that economically relevant institutions permit such lotteries, that the gains survive estimated uncertainty, or that the normalized savings are material.

**Required correction:** add a serious economic application with calibrated or estimated primitives, verified uncertainty sets, and an economically interpretable implementation-cost scale. Absent such an application, the theoretical and computational advance must be substantially broader and stronger than currently demonstrated.

### R40-F11 — Verification is strongest on selected easy objects and incomplete on the hardest headline evidence

The independent finite verifier is a major strength. The continuum and nonlinear verifiers also have more meaningful separation from construction code than in R38. Nevertheless, coverage is uneven.

The nonlinear verifier independently reconstructs selected complete objects, not the entire nonlinear table. The finest `T=32, N=256` interval—used to support the best reported nonlinear relative gap—does not receive the independent label. Tight-tolerance lower-only rows are not paired with an independently checked feasible policy because none exists. The local and transfer assumptions remain mathematical trust boundaries rather than machine-checked conclusions.

Cross-run hashes, source snapshots, mutation tests, and publication manifests establish provenance and catch specified faults. They cannot validate an unexecuted approximation assumption or establish that the selected economic model is appropriate.

**Required correction:** independently verify the hardest and finest objects, not only representative smaller rows; provide a theorem-to-checker coverage map; and distinguish explicitly among independent arithmetic verification, same-code validation, protocol hash matching, and publication integrity in the main result tables.

### R40-F12 — The numerical novelty relative to existing constrained-MDP and global-optimization methods is not yet convincing

The paper correctly acknowledges that McCormick envelopes, best-bound search, weak duality, policy discretization, and verified arithmetic are classical. Its distinctive object is the all-state/all-date operating constraint with one shared Markov continuation, together with an explicit feasibility repair.

That formulation is useful. The remaining question is whether the repair and stopping bound constitute an Econometrica-level numerical advance rather than an exponential completeness proof attached to standard global search. The prospective results currently favor the direct McCormick formulation on the hard rows. The transfer theorem is related to existing finite approximation results for constrained MDPs and is not numerically instantiated. The paper does not establish a rate or computational advantage that follows from the Bellman structure.

**Required correction:** sharpen the theorem-level novelty relative to finite approximations, occupation-measure compatibility formulations, semi-infinite programming, and global bilinear optimization. Demonstrate either a strictly stronger guarantee or a practical advantage on problems where existing methods fail. Repository engineering and proof-object discipline, while excellent, are not sufficient novelty by themselves.

### R40-F13 — The local-LP component remains computationally expensive relative to its contribution

The adaptive local study displays approximately first-order interval contraction as the requested tolerance is halved, but the work grows sharply. In the hardest reported horizon-four one-dimensional row, the finest request uses roughly 12,500 cells and more than 80–100 seconds to reduce the local interval width to about 0.00464.

R40 connects a local-support construction to the primary lower endpoint, which is an improvement over the disconnected R38 diagnostic. It still does not close the global randomized intervals or establish global duality. The component is expensive even in one state dimension and four decision dates.

**Required correction:** report the marginal improvement in each final global interval per unit of local work, compare against direct statewise LP evaluation and additional global-search nodes, and remove or relegate the component if it does not materially change an economic conclusion.

### R40-F14 — The stated scope remains narrower than the title and broad methodological framing

All convergence arguments are finite horizon. The repair requires strict discounting and a strictly positive operating tolerance. No result is given for `beta=1`, zero tolerance, average cost, or infinite horizon. The constants deteriorate as `beta` approaches one or `epsilon` approaches zero. These are not peripheral cases in economic dynamic programming.

The title and abstract do not foreground these restrictions. The paper also retains a stopped continuous-control program that remains unsolved and is outside the demonstrated method.

**Required correction:** narrow the title and claims to finite-horizon, positive-tolerance, discounted revision certification, or extend the theory materially. The stopped-control material should remain archival unless the full action/discretization errors are actually certified.

## 5. Minimum scientific requirements for a future submission

A future submission would need a coherent subset of the following changes.

1. **Bridge theory and headline evidence.** Either give a convergent certificate for the atomic continuous-state models or make a TV-reset model the main executed application.

2. **Demonstrate practical closure.** Close or tightly bound nontrivial long-horizon problems with more than four states and at least three actions. Formal finite termination is not enough.

3. **Establish a computational advantage.** Show where Bellman-specific structure outperforms strong global-programming baselines under matched accuracy, time, and memory.

4. **Resolve a substantial share of the primary randomized optima.** The current 27 deterministic separations are not substitutes for tight randomized optimality intervals.

5. **Strengthen the nonlinear evidence.** Use meaningful tolerances, provide paired feasible upper policies, prove or otherwise validate refinement behavior, and independently verify the finest object.

6. **Execute the witness and transfer theory.** Report a model in which exact operating values are genuinely unavailable and all terms in the end-to-end error budget are numerically useful.

7. **Add economic discipline.** Calibrate or estimate a substantive application, or provide verified uncertainty sets that make the administration and model-error margins economically interpretable.

8. **Clarify novelty.** State exactly what theorem or computational capability is unavailable from existing constrained-MDP finite approximation and generic global optimization.

Without these changes, the paper is best understood as an unusually careful, verified research program for small finite common-Markov problems and one-sided atomic-model certificates, not as a general Econometrica-level numerical method.

## 6. Additional technical and presentation comments

1. The abstract should state that the executed continuous-state models are outside the reset-transfer theorem.

2. The abstract should also state that all 30 positive-cost primary randomized intervals remain nonzero.

3. Report median as well as maximum relative gaps by horizon in the main text.

4. For strict randomization gains, show the guaranteed saving `L_D-U_R`, not only the randomized optimality interval width.

5. Keep the direction of the strict comparison explicit: a lottery **upper** cost lies below a deterministic **lower** bound.

6. The finite suite should report the number of policy coordinates `nT`, not only states and horizon.

7. Give the theorem-implied worst-case node bound numerically for each prospective row. This would reveal how informative the stopping theorem is in practice.

8. Report bound improvement per node for interval and McCormick search, since both methods often hit different effective iteration costs.

9. The 60-second cap is checked between proof-producing iterations and some rows exceed 60 seconds. State this prominently wherever times are compared.

10. Explain why binary-action experiments are representative of the general finite-action theorem; preferably add a prospectively fixed three-action suite.

11. Provide a full table of witness width `e`, residual `d`, margin `sigma`, lattice error, and repair fraction. A passing witness label is not enough.

12. For the transfer theorem, distinguish total variation under the operator convention from action-distribution total variation in every theorem statement, not only nearby prose.

13. The exact decomposition `nu=sum nu_i mu_i` deserves a separate discussion. It can be restrictive when the reference measures are chosen to approximate transition densities rather than the initial law.

14. Quantify how the transfer constants scale with `T`, `beta`, and `epsilon`; the displayed asymptotic `O(h)` rate alone is misleading.

15. For every nonlinear row, identify whether the upper endpoint exists, whether it is independently verified, and whether threshold-crossing boxes incur conservative cost.

16. Do not visually emphasize the finest nonlinear relative gap without equally emphasizing that it lacks the independent label.

17. The tighter nonlinear tolerance table should not be interpreted as an optimization interval because it has no certified upper endpoint.

18. Separate development, prospective synthetic audit, and empirical validation in every summary. The first two exist; the third does not.

19. The administration-cost threshold assumes no effect on operating dynamics. Discuss how a state- or action-dependent overhead would alter feasibility and cost certification.

20. The robust-model proposition requires policy-uniform error bounds. Explain how such bounds could be obtained from estimated primitives rather than simply setting `a=b=0`.

21. Report the cost of constructing independent verification objects separately from constructor time and publication overhead.

22. The protocol committed source hashes before execution rather than embedding all source in the protocol commit. The final audit should surface the exact hash-equality check in a short human-readable table.

23. The literature discussion should compare the common-continuation coupling with an explicit occupation-measure formulation, not only describe why independent restart measures would be wrong.

24. The stopped-control program should be removed from the main narrative unless it produces a new complete certificate. Its inherited 7.1818 bound versus a 0.01 target demonstrates non-closure, not applicability.

25. The historical archive is valuable, but the current article should be readable and auditable without traversing forty revisions. Keep provenance separate from scientific exposition.

## 7. Final editorial view

R40 deserves substantial credit. It responds to the previous report at the level of mathematics rather than only at the level of packaging. The common-policy formulation is now explicit, the repair theorem supplies a real bridge from approximate to exact feasibility, the finite-state method has a genuine completeness statement, and the same-object McCormick comparison is informative. The paper's authors are also unusually candid about budget stops, development data, atomic-transition limitations, and verification boundaries.

That candor reveals why the paper is still not ready for Econometrica. The complete method is computationally prohibitive beyond very small problems; the stronger classical comparator dominates the proposed search on the hard prospective rows; the continuous transfer theorem is not exercised on the models used for the economic conclusions; the primary randomized optimum is unresolved in every positive-cost case; and the nonlinear intervals remain too wide to support an optimality claim. The economic evidence is synthetic and does not compensate for these numerical limitations.

**Recommendation: Reject.**