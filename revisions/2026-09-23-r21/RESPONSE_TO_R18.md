# Response to the R18 referee report — Revision R21

## Review object and principal changes

We thank the referee for isolating the difference between learning a witness and improving a policy. The input is the report on the R18 publication, committed on review branch `review/econometrica-r18-numerical-methods-2026-09-23` at `074849b9aad1812b59e25e1d3833383ed11aa401`. The new manuscript is `ECTA_R21.tex/pdf`; the complete technical record is `SUPP_R21.tex/pdf`. This response is also compiled as `RESPONSE_R21.pdf`.

R21 inherits the latest R20 scientific source, not an older branch that would omit subsequent work. R20 had executed a new stochastic neural experiment but had not materialized its manuscript. We supply that manuscript and its missing continuous-time proofs. We also add a genuine additional argument: four improving experts do not automatically give an improving mixture, and a verified upper bound on the initial mixture's Jensen benefit is necessary. The resulting theorem establishes actual policy improvement throughout the initial-state rectangle.

The title, author, original economic model, admissible action set, stopping rule, and all-domain 0.01 objective are retained. All inherited scientific files are preserved byte for byte; the root navigation index is updated and its original bytes archived. Earlier substantive main-text inputs and proofs remain in the new main manuscript; superseded introductory and concluding exposition is preserved in the supplement. Original unsuccessful experiments are neither deleted nor relabeled.

## R18-F0 — Review-target integrity

The new revision is a separate descendant branch. Protocol, training source, immutable R20 results, R21 analysis, and publication have separate identities. R20's confirmatory protocol predates its five-seed run. R21 is explicitly a manuscript revision and a new analysis/replay of those frozen policies, not newly randomized training. All actor and network hashes are checked. The canonical manuscript, supplement, response, generated tables, runnable scripts, replay results, and publication manifest are delivered together.

## R18-F1 — Useful neural accuracy on the original economy

A materially different solver object is now evaluated: neural-generated stochastic consumption financed by a conditional-price portfolio, not the old full-state actor/critic pair. The four retained work levels are 0, 100, 400, and 1000. Each of five seeds has four experts and a rigorously defined mixture on the whole rectangle K=[1.98,2.02] x [1.24,1.26]. Every final mixture has an original-economy regret bound below 0.002909 on K at time zero and k=2. Every seed already reaches the unchanged 0.01 target and the additional 0.005 reporting threshold at 100 updates; the 0.002 reporting threshold is missed and remains visible.

The fixed-policy transport theorem further bounds regret by 0.003327 on K x [1.5,2.5], without retraining or testing only sampled prices. This is not a claim of 0.01 accuracy over all initial states of D and all starting times. The global objective is not redefined to make the localized result count as global closure. See the stochastic-policy section, policy-results table, price theorem, and analytic appendix.

## R18-F2 — Witness descent versus actual policy improvement

There is no learned critic in the new acceptance test. A new expert is accepted only when its independently verified payoff lower bound exceeds the incumbent expert's payoff upper bound. All sixty noninitial expert transitions satisfy this strict criterion before subsequent optimization.

We additionally resolve a continuum issue not settled by those sixty tests: an initial mixture can benefit more from concavity than its components. The new Jensen-gap upper bound prevents that benefit from being ignored. It proves an initial-to-final actual payoff gain of at least 0.01762319 at every point of K, for every seed. Combining this with the final optimality bound gives a pointwise true-regret ratio below 0.141101, or more than 85.8 percent reduction. We do not infer that every consecutive mixed policy improves from the corner tests alone. All historical actor/critic swaps and their adverse interpretation are retained.

## R18-F3 — A policy-sensitive acceptance mechanism

The executed R20 mechanism freezes and checks the delivered policy, orders its payoff against the incumbent, and restores both network and optimizer after rejection. Its policy-improvement theorem does not assert convergence of Adam to a global parameter optimum. The conditional-price decoder handles feasibility, the policy-specific interval handles acceptance, and the unrestricted dual handles accuracy. These three mathematical roles are stated separately. The older complete-cover objective theorem remains as a valid a posteriori bridge, not a policy-learning theorem.

## R18-F4 — The continuation-witness floor

The historical floor above 6.27 is not repaired by finer cells or higher precision. We preserve that diagnosis and the verified one-sided continuation targets. The new regional solver instead uses a separate unrestricted dual functional, which is demonstrably sharp on K, and a policy-specific payoff evaluator. Thus the old critic floor is not a lower bound on every possible verification architecture. We do not claim to have transformed the old critic into a sharp global continuation supersolution. A sharp upper witness on the whole state-time cylinder remains a distinct outstanding object; the revised conclusion keeps that global task explicit.

## R18-F5 — Accessibility versus finite-budget superiority

The paired width-dependent reversal remains in the paper. Accessibility is presented as a consistency repair of an approximation space, not a universal finite-work performance advantage. The new stochastic policy theorem establishes its own pathwise admissibility through conditional pricing and does not borrow numerical superiority from the old accessibility argument.

## R18-F6 — Matched certified classical accuracy

The direct stochastic L-BFGS-B comparator uses the same original economy, sixteen-slab stochastic family, four initial states, full continuous-time checker, common unrestricted optimal upper, and continuum transfer theorem. It reaches a final K-uniform regret bound below 0.002839. At the first 0.005 hit it is faster than each neural seed in the recorded generation-plus-verification ledger. All methods miss 0.002. The entire 415.789-second shared dual-library construction is separately charged to cold-start use or explicitly declared reused; final MPFR and publication replays are additional audit costs.

This is a sharp local classical accuracy frontier, not a completed global MC/SL comparison. The old unrestricted MC/SL candidates and signed decompositions are retained. R20 did not record process peak RSS for the direct stochastic optimizer, and we state that missing quantity rather than replace it with parameter storage. No neural time or memory superiority is claimed.

## R18-F7 — What learning contributes in the high-dimensional example

The initialization-agnostic strong-convexity theorem is explicitly kept separate from learning. The inherited R19 learned-gradient theorem conditions correction work on an independently enclosed initial gradient, with a Lipschitz-cover extension when a genuine state cover is available. Its 32-query matched-tolerance study is retained in full. At dimension 128 and tolerance 0.01, learned starts reduce gradient work on 31 of 32 paired queries; at stricter tolerances the benefit vanishes or reverses. The reported break-even counts use explicitly transferred historical training cost and are not a same-hardware certified speedup. This provides a limited learned-quality effect, not broad neural necessity or a proof over a cube from 32 sample points.

## R18-F8 — Accurate neural policies, not a renamed deterministic library

The successful new policies come from freshly initialized and trained 1-16-16-3 neural networks, with stored weights and separately compiled coefficients. They use factor-dependent consumption and a nonzero portfolio. No inherited optimal policy or value labels train them. The analytic price decoder is identified as a model-based component, not represented as a learned network. The unrestricted dual is likewise an independent comparison tool.

For each of three named deterministic time-control transcriptions, the new neural mixture lower bounds exceed a policy-specific affine upper by at least 0.00455889 throughout K. We distinguish this true stochastic-policy improvement from a blanket comparison with all non-neural methods: the direct stochastic comparator is stronger and remains in the main table. The paper keeps its neural computation identity while specifying exactly which component is learned and which guarantee is model-based.

## R18-F9 — A harder stochastic economic application

The main new evidence is obtained in the original nonlinear stopped economy, with correlated preference and financial shocks and an actively stochastic financial policy. It is not another deterministic strongly-convex control-plan example. The earlier nonlinear high-dimensional example remains a useful separate validation study, with all favorable classical results. Broad high-dimensional stochastic superiority is not inferred from the new two-state experiment.

## R18-F10 — Policy-payoff and economic comparisons

The uniform initial-to-final payoff gain and the independently ordered comparisons with three named deterministic policies provide policy-sensitive evidence on a continuum of initial states. Portfolio and consumption ranges are used to prove admissibility, not treated as accuracy statistics. The old actor-control ranges remain descriptive. No ordering of true policy values is inferred merely from nonoverlapping action ranges or differences between loose regret upper bounds.

## R18-F11 — Welfare interpretation for the learned policies

The new compensation result applies to the learned stochastic policies themselves. At each vertex, keep the learned slope and preference-drift shapes, change only a budget offset, finance consumption from initial wealth increased by 0.002, and verify the exact reserve again. All twenty compensated-policy lower bounds exceed the corresponding original, uncompensated optimal upper. The mixture theorem extends this comparison throughout K. The sufficient increment is 0.16 percent at wealth 1.25 and below 0.162 percent over K. It is not claimed to be minimum compensation or a welfare interpretation of the old seven-unit neural bound. The older 0.624-percent result for a different deterministic library is preserved with its own attribution.

## R18-T1 — Signed decomposition in the main text

The new results section explicitly states that every final historical accessibility-aware policy-side component is zero and the remainder is the positive comparison component. Full signed tables remain in the retained development. The new policy-specific lower/upper test is described next to its actual-payoff gains, not only in an appendix.

## R18-T2 — All-seed actor/critic interchanges

The complete R19 all-ten-seed factorial is retained, including initial/initial, final/initial, initial/final, and final/final pairings. Those frozen historical objects are not relabeled as new R21 training. The new solver does not need to manufacture a favorable critic swap because its acceptance evaluator is policy-specific and contains no learned critic.

## R18-T3 — Trace excess and fixed-witness floor

All thirty historical trace checkpoints, floor values, and explicit lift interventions remain in the manuscript and supplement. Their meaning is explained in the new main text: the floor diagnoses a particular critic family and is not refuted by a localized dual-functional bound for a different stochastic policy.

## R18-T4 — Acceptance terminology

We use strict policy-payoff acceptance for the new expert mechanism. We do not call the old certificate incumbent rule policy improvement, and we distinguish expert acceptance from interior mixture improvement. The latter requires the new Jensen theorem. There is no unsupported claim that Adam implements globally convergent policy iteration.

## R18-T5 — Scaling of complete-cover work

The retained cost analysis keeps state dimension, number of boxes, network width/depth, Hessian-jet components, and action-maximization work explicit. A tensor cover remains exponential in dimension; chunked checking reduces working memory but not total cover work. The new four-expert construction is a local two-state method, not a dimension-free substitute for that cover.

## R18-T6 — Initialization-agnostic guarantees

The current introduction, results discussion, and retained learned-frontier section explicitly distinguish a correction theorem valid from an untrained initialization from a theorem that depends on learned initial gradient quality. Neither is used to erase the strong zero-start or accelerated baselines.

## R18-T7 — Amortization and matched targets

All inherited tolerance-dependent correction counts, solver/check-inclusive times, and transferred-cost break-even calculations at 0.01, 0.001, 0.0001, and 0.000001 remain. The new original-economy table separately reports 0.01/0.005 hits and 0.002 misses for neural and direct stochastic methods, along with the shared-upper and publication-audit costs. No end-to-end neural speedup is claimed where the evidence does not support it.

## R18-T8 — Finest-grid classical deterioration

The old MC/SL signed decompositions and control-range audits are preserved rather than replaced by the new strong local comparator. The old finest-grid deterioration cannot rank true policy values from certificate totals alone. The new direct comparator is evaluated sharply and is explicitly a different comparison object.

## R18-T9 — Arithmetic independence

We describe the MPFR implementation as a separate directed arithmetic implementation of shared analytic mathematics. The manuscript gives the self-financing proof, Gaussian conditioning, analytic quadrature-disc bounds, tails, stopping correction, and continuum transfer explicitly. Neither overlapping numerical intervals nor a successful test suite is described as independent formal verification of that theorem stack.

## R18-T10 — Predeclared execution versus later analysis

The exploratory seed is excluded, the five confirmatory seeds and work levels were fixed in R20's prior protocol, and every acceptance check preceded the next update. R21's Jensen-gap analysis, fixed-policy price transport, and independent replays are explicitly post-training mathematical analyses. Their role is not confused with additional confirmatory optimization runs.

## New gates R19-A through R19-F

R19-A now has a uniform, policy-sensitive initial-to-final improvement theorem on K, in addition to all sixty expert acceptances. R19-B is advanced through a sharp regional dual comparison, but a new globally sharp continuation supersolution is not claimed. R19-C is achieved on K at time zero, and over K x [1.5,2.5] by price transport; its full-D/all-start-times reading remains outstanding. R19-D has a sharp same-domain classical stochastic comparator and explicit cost accounting, but not a complete global MC/SL frontier. R19-E has a limited learned-quality/work effect in the retained finite-query study, not a broad high-dimensional stochastic neural advantage. R19-F is strengthened by actually trained stochastic neural policies with useful verified original-economy accuracy; the learned generator, classical decoder, payoff evaluator, and unrestricted comparator are not conflated.

These are concrete mathematical and numerical changes, not a request to accept lower accuracy or to ignore adverse results. The final manuscript maintains the global objective and gives the next referee both the strengthened regional theorems and the exact boundaries of the evidence.
