# Response to the R8 numerical-methods referee report

**Paper:** Neural Bellman Operators  
**Revision:** R9, September 22, 2026  
**Review input:** `reviews/2026-09-22-econometrica-r8/referee_report.md`, blob `7aae4e112a6dd7b5eb231e20cb8b831b6f666d34`  
**Review branch tip:** `9749c3cf28f9438315b8f504a358bbe307ea89a5`  
**Reviewed R8 manuscript commit:** `939b612ff57794a2127f0b0adeb74ab7eef9e72e`  
**New branch:** `revision/econometrica-r9-constructive-certification-2026-09-22`  
**Current manuscript:** `ECTA_R9.tex` and `ECTA_R9.pdf`  
**Complete preservation supplement:** `SUPP_R9.tex` and `SUPP_R9.pdf`

We thank the referee for identifying the remaining numerical chain, rather than repeating objections that R8 had already resolved. This revision changes the construction and the evidence, not the original economy. The running utility, continuous controls, correlated Brownian shocks, first-exit stopping rule, and liquidation settlement are unchanged. The new leading result is a verified positive lower bound on the difference between the optimal flexible and no-adjustment values. At the central state this access gain is at least **0.04094994** for adjustment cost two. It is obtained from a learned feasible policy in the flexible economy and an independently certified upper bound covering every adaptive consumption and portfolio policy in the restricted economy.

The revised paper also implements fitted-polynomial witness refinement, an independent stopped Gaussian-moment policy evaluator, a non-enumerative continuous-action certifier, interval derivatives of actual learned critics, and a rigorous absolute lower reference for the unchanged nonconvex comparison problem. A symmetrically tuned, frozen holdout protocol covers three dimensions, two training budgets, and twelve seeds per panel. All outcomes are retained, including the independent feedback baseline outperforming both learned methods.

The result is not a claim that every requested numerical target has been reached. In particular, the flexible learned policy's current regret bound at cost two is **0.10633861** after outward display rounding, above the unchanged **0.01** target. Its much smaller policy-evaluation interval is not called an optimality bound. The responses below identify precisely which calculation now answers each concern and which stronger question remains separate.

## R8-F1 — Original-economy precision

**Change.** Sections 4–5 and Appendices B–D establish new continuous bounds at `(t,u,x)=(0,2,1.25)` for costs 0.5, 2, and 8. These calculations use the original payoff, not the manufactured geometry test. At cost two, the learned time-control policy has payoff in `[-1.2950431576702368,-1.2950298659650283]`. The independently fitted upper witness bounds the flexible optimum by `-1.1887045536637568`, giving regret at most `0.10633860400648`.

The previous R8 value `8.33956052603494` remains attached to its original retained state-feedback policy and witness. The R9 policy is different: a newly trained time-control neural subclass. We do not report the improvement as a like-for-like re-evaluation of the old actor, and the old result is preserved.

The restricted economy now has an optimal-value interval `[-1.3450394132791428,-1.335993099122843]`, with width below `0.009047`. The flexible feasible policy and restricted upper bound imply the positive **optimal access** welfare lower bound `0.04094994145260621`. Thus an economically informative original-model inequality is established without assuming that either learned policy is optimal.

**Remaining distinction.** The full flexible-policy 0.01 target is not met at any of the three costs. The current certificate is for the stated initial point, not a uniform initial-state region. The restricted precision and the positive access inequality do not establish a narrow two-sided flexible value or an optimal policy surface. `results/scientific_summary.json` explicitly records the flexible target flags as false.

**Evidence.** `original_actor.py`, `original_policy_certificate.py`, `certify_upper.py`, `restricted_dual.py`; Tables 1–4 of the main paper and the corresponding raw records.

## R8-F2 — An operational witness-improvement procedure

**Change.** The eight-unit initial witness gap is no longer built into the new construction. We fit a Chebyshev polynomial `F(h,u)` to a reduced continuous-generator equation and certify it independently using outward Bernstein coefficients, all applicable constrained-control branches, and de Casteljau subdivision. A proved utility-polynomial remainder is included. Small exponential localization terms pay for continuation at artificial verification faces using the global fallback `G`; the economic stopping rule is never replaced by reflection.

For cost two, the independent policy interval shrinks from width `2.093e-4` to `1.330e-5` over 1,024, 4,096, and 16,384 time rectangles. The upper residual calculation refines from 36 to 57 to 86 terminal Bernstein boxes, with final polynomial residual upper below `8.940e-4` and separately added utility remainder below `2.117e-9`. The initial localization correction is below `1.219e-7`, rather than eight units. Table 2 reports width, residual, box count, and stage timings; raw records include complete construction times.

A second constructive refinement evaluates the bounded-source restricted dual. Its witness interval shrinks from width `0.005673` to `0.001322` to `0.000320` over 16,384, 131,072, and 1,048,576 weighted Taylor boxes. Gaussian tails, exponential remainders, localization, and arithmetic are explicit. This refinement leads directly to the restricted optimal-value enclosure and access-welfare result.

**Remaining distinction.** Refinement validates a fixed candidate with slack; it does not prove that residual least squares converges to the exact value or that its approximation gap vanishes. A wealth-sensitive linear-programming pilot, its rejected coarse diagnostics, and its stopped dense run are retained separately and supply no certified endpoint.

## R8-F3 — The schematic semigroup budget

**Change.** We implement the alternative continuous-verification route rather than assigning uncomputed numbers to the inherited finite-to-continuous decomposition. The fitted upper is checked against the continuous generator over its full verification rectangle and all original continuous actions. The feasible lower has exact deterministic wealth and interval Gaussian-moment evaluation of the original stopped preference process. The restricted upper uses a continuous market-deflator cancellation and a bounded-source stochastic potential. Appendix F gives an explicit scope and error ledger for these routes.

There is no Euler transition error, state interpolation error, or action-grid error in these particular calculations: the deployed time controls and analytic Gaussian evaluator do not use those approximations. Exact preference exit is bounded through a maximal-probability and Cauchy–Schwarz correction. These are reasons an error category is absent, not estimates set to zero without computation.

**Remaining distinction.** We have not completed the old killed-Euler scheme's semigroup discrepancy budget. Its named terms, mesh differences, exit diagnostics, and finite envelopes remain in the complete historical supplement, without being repurposed as continuous certificates.

## R8-F4 — Non-enumerative action certification and cost

**Change.** Section 6 and Appendix E implement a global oracle for the unchanged coupled nonconvex action Hamiltonian. Scalar dual subproblems are strongly convex. A lower bound on each action-sum interval combines their certified minima with a quadratic minorant of the coupled sine term. Feasible actions supply upper bounds. Only the scalar sum interval is subdivided; no tensor action grid is enumerated.

The retained ten runs cover action dimensions 8, 16, 32, 64, and 128 at tolerances `1e-3` and `1e-5`. All pass their declared tolerances. The 128-dimensional `1e-5` run uses 339 scalar boxes and 43,392 scalar convex subproblems; its certified gap is below `4.679e-6`. Table 5 reports every run, tolerance, cost count, and elapsed time. At dimensions 8 and 16, interval differentiation of the actual retained learned critic also encloses the difference between its mathematical jet and the floating-point gradient used to propose the action.

**Remaining distinction.** These are fixed-jet action certificates exploiting rank-one nonconvex coupling. There is one test jet per dimension, not a statistical complexity law. Whole-state residual covering remains a separate cost. The old 125-action finite safeguard, raw NBO, and this new oracle remain distinct objects; no correction-share statistic is described as certification cost.

## R8-F5 — Manufactured payoff versus an unknown-value problem

**Change.** The new actor is trained under the original utility and liquidation contract. Its value is not supplied to training, and the upper polynomial is independently fitted and globally checked. The restricted upper comes from an auxiliary deflator construction, not from modifying the reward to make a chosen value exact. The original-model policy, upper witness, and welfare comparison now have independent executed error budgets.

**Remaining distinction.** The original-payoff actor is a time-control neural subclass with zero portfolio, not a claim to have solved unrestricted state-feedback critic learning. Its feasible payoff still yields a valid lower bound on the full original optimum. The four-parameter R8 manufactured-payoff test is preserved in full, explicitly identified as a verifier test, and does not supply any R9 economic bound.

## R8-F6 — Absolute accuracy of the external comparison

**Change.** Section 7 adds an independent rigorous lower bound for the exact nonconvex benchmark family. A pointwise quadratic running-cost relaxation, followed by removal of control bounds, admits a Cole–Hopf representation while retaining the original nonquadratic terminal payoff. Orthogonal Gaussian coordinates integrate out, leaving a one-dimensional positive integral with outward quadrature and a proved tail bound.

At the finest resolution, original-value lower bounds are `-0.08498597660676563`, `-0.20445643072631145`, and `-0.2872351470516064` for dimensions 8, 16, and 32. Table 6 records all three quadrature refinements. Table 8 reports estimated policy cost in excess of these absolute lower references, alongside actual training clocks.

**Remaining distinction.** A precise quadrature of a relaxation need not be a tight original optimum. The Monte Carlo policy-cost estimate is not an outward deterministic upper, so its excess over the rigorous lower reference is not relabeled as a deterministic regret certificate. This answers the request for a trustworthy lower reference but does not produce a matched-small-regret efficiency frontier.

## R8-F7 — Symmetric tuning, budgets, dimensions, order, and another comparator

**Change.** Commit `46aef70a24f74cf57503018a7e7f21cb46af08e3` freezes the protocol before tuning and holdout execution. Both methods receive six ten-second validation trials per dimension: two seeds crossed with three learning-rate multipliers, selected by the same mean-validation-cost rule. Holdout seeds are distinct. The suite covers dimensions 8, 16, and 32 and budgets 10 and 30 seconds. Each pair starts from identical actor and critic weights, with recorded hashes. Method-specific warmup and seed-randomized order address initialization and end-to-end timing concerns; setup-plus-training and training-only clocks are both retained.

The author solver remains pinned at `sx-fang/MartNet@991ea8dde5bad6ba912eb8cc48b0cb48dbdd6c2a`; its training routine is not rewritten. The distinct Adam and RMSprop optimization systems and their native scaling remain disclosed. An independently specified clipped quadratic-feedback baseline is evaluated on the same unchanged nonquadratic payoff.

The complete workflow `35682656529` succeeds, including all 72 holdout pairs and automatic evidence commit `58007e6edf8a6d80e930e025138f38d978a82aba`. NBO's mean cost is lower than SOC-MartNet's in all six panels. However, the independent quadratic-feedback baseline has lower mean cost than both learned methods in every panel. Tripling training budget gives only small NBO mean improvements. Both findings are reported prominently rather than omitted.

**Remaining distinction.** Two budgets, one benchmark family, and three dimensions do not establish a general scaling theorem or a matched-accuracy frontier. The absolute reference and all learning/timing records are now available to assess the actual achieved accuracy rather than infer it from pairwise superiority.

## R8-F8 — Connecting neural errors to the quantities being certified

**Change.** Theorem 2 gives an explicit cover-and-oracle bound for a learned witness and feasible policy: verified boundary error, representative residual intervals, full-cell variation bounds, and a global action gap imply a continuous policy-regret bound. It yields vanishing regret for any sequence whose certified allowances vanish, without assuming parameter convergence. It does not derive a supremum bound from an empirical mean-square loss.

The action implementation additionally differentiates the actual eight- and sixteen-dimensional neural critics in interval arithmetic. The resulting componentwise jet errors are propagated through the continuous action box, adding at most four times their sum to the certified action gap. This is an executed parameter-to-jet-to-action connection at the stored states.

**Remaining distinction.** No global Adam convergence rate, exact-operator compactness result for these networks, or whole-state high-dimensional critic certificate is asserted. The exact policy-iteration theorem and its strong assumptions remain in the historical supplement. The independent verifier can audit another solver's policy; that portability is explicit rather than treated as a unique property of NBO training.

## R8-F9 — A continuous economic result rather than finite-scheme comparative statics

**Change.** The cost grid now has original continuous policy payoff intervals, optimal-value upper bounds, policy adjustment-budget intervals, and two-sided access-value enclosures. At costs 0.5, 2, and 8, certified **optimal access** welfare lower bounds are respectively `0.06274788587516177`, `0.04094994145260621`, and `0.007812123627567446`. They compare with the optimal restricted economy, not a chosen restricted benchmark policy. The restricted-witness integration width is more than 128 times smaller than the cost-two minimum access gain.

The deployed policies' adjustment budgets are enclosed near `0.01960483159556555`, `0.01242015505497370`, and `0.001926182620275735`. The quantities are not finite-grid outputs and include exact stopping corrections. Table 4 explicitly distinguishes these **policy** budgets from the **optimal** access comparison.

**Remaining distinction.** The two-sided optimal access intervals remain too wide to estimate the gain's magnitude narrowly. The flexible-value enclosures also do not identify informative optimal-budget secants or a pointwise policy ordering. The positive minimum welfare result is the economic conclusion established at this precision, not a claim that the larger original precision requirement is satisfied.

## R8-F10 — Recursive utility, temporal selves, and games

**Change.** The current main analysis focuses on the additive original economy and the nonconvex control comparison. The full R8 exposition, equations, and proofs, the full R4 main text and appendix, and every delivered R5 table are included in `SUPP_R9` through unchanged source inputs. This preserves Epstein–Zin and stochastic differential utility, sophisticated temporal selves, games, counterexamples, trace calculations, failures, and finite safeguards.

There is no new large-scale recursive-utility or game claim based on the additive-control evidence. Nothing is removed from the historical source record to obtain this focus; the preservation manifest verifies inherited files.

## R8-F11 — Holdout inference and robust summaries

**Change.** The comparison now has twelve independent holdout seeds per panel rather than six development-era seeds. The complete selection protocol predates execution. Every seed difference, median, interquartile range, descriptive Student interval, paired path standard error, and checkpoint is retained. The primary robust sign calculation is reported with a Bonferroni correction over the six predeclared dimension–budget panels.

All twelve paired differences favor NBO in dimensions 8 and 32 at both budgets, giving adjusted sign-test values `0.00146484375`. At dimension 16 the adjusted values are 1 and `0.43798828125`, so these panels do not establish the same robust ordering. These differences in evidential strength are not hidden behind a pooled favorable average.

**Remaining distinction.** The sign test concerns the joint training-and-audit pipeline under independent seed draws; it does not certify a PDE or remove finite-path/rounding uncertainty. The model family and adapters were developed before this freeze, and holdout seeds do not constitute held-out problem families. This is a stronger predeclared holdout record, not a claim of a multi-problem confirmatory benchmark.

## R8-F12 — Rigorous-control and numerical-analysis positioning

**Change.** Section 8 compares the results theorem by theorem with classical stopped verification, monotone viscosity approximation, controlled Markov-chain approximation, stochastic dynamic-program dual bounds, and occupation-measure relaxations. We add Brown–Smith–Sun, Brown–Smith, Kushner–Dupuis, and Lasserre–Henrion–Prieur–Trélat alongside the retained Barles–Souganidis, adaptive-grid, and neural-method references.

The stopped Itô proof and finite telescoping argument are not claimed as new generic principles. The model-specific contributions carrying the new conclusions are the fitted witness with explicit small stopped localization, the portfolio-canceling bounded-source restricted witness, the independently verified original-payoff learned policy, the interval neural-jet/action bridge, and the structured scalar action certifier. The occupation-measure literature's deterministic polynomial assumptions are not invoked as a convergence theorem for the present logarithmic stochastic-exit economy.

## Presentation, preservation, and reproducibility

`REVISION_INDEX.md` now points to the single canonical R9 manuscript, supplement, response, evidence, and validation files. The previous R3 index is preserved byte-for-byte in the R9 archive. We have not deleted or moved the R8 referee-copy branch or any prior review. Both main and supplement use the Econometric Society `econsocart` class, retain the existing author metadata, and build from ordinary checked-in TeX inputs without decoding transport fragments. All new proofs are in the mathematical appendix; historical breadth is preserved in the supplement.

The replication README provides exact commands and scope distinctions. Validation checks the continuous certificate inputs and inequalities, all declared external seeds and pinned code, preserved source hashes, generated tables, and clean compilation. Complete source and evidence are committed on the new R9 branch; the primary and review branches remain unchanged by this work.

## What this resubmission establishes

The original economy now has an executed chain from a learned feasible policy and independently constructed continuous witnesses to a strictly positive optimal access-welfare inequality. The restricted optimum is enclosed within the original 0.01 scale at the central state, while the flexible policy's wider regret remains explicitly recorded. The revision supplies constructive refinement, a continuous non-tensor action certifier, actual neural-jet enclosures, an absolute benchmark lower reference, and a frozen comparison retaining unfavorable controls and panels. We submit these substantive results for renewed technical assessment, without interpreting partial precision progress as closure of every stronger target in the report.
