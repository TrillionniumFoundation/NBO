# Response to the latest Econometrica-style referee report — R12

## Review target and revision lineage

This response addresses the report at review commit `251ad29668788b2a911c4ca6f9c0a226886518d6`, blob `42cee0954515e5578dc579a4ca0428bb4e399b2e`. That report reviewed early R9 source `46aef70a24f74cf57503018a7e7f21cb46af08e3`, not the subsequently completed R10/R11 papers. The present revision begins at the complete R11 commit `85e27ad0c9cdcb68645d62788e1fad2f59ea1a48`. We preserve that entire manuscript, its proofs and its complete supplement rather than treating the old report as permission to discard later work.

The main new result is constructive and numerical: eighteen certified policies supply a policy with regret at most **0.009994024846927508 for every real cost coefficient in [0.5,8]**, at the same central initial state and against the unchanged economy's full adaptive optimum. Three node certificates are inherited and fifteen are new. A finite exact rational envelope calculation certifies the continuous parameter range. This is stronger than asserting success on eighteen sampled prices. The manuscript adds the complete continuation theorem, sign-sensitive expenditure transfer, a conditional finite-refinement bound, all node certificates, refinement costs, and counterfactual interpretation. It retains the original absolute-error target.

The original review is reproduced without edits in `review_input/referee_report.md`. References below use source labels so they remain stable under final pagination. Each response distinguishes an inherited substantive repair from the new R12 extension. No outcome is described as editorial acceptance.

## R9-F1 — An actual revised manuscript

`ECTA_R12.tex` compiles the complete paper, not an experiment announcement. Its main text retains every R11 main-text line in order and adds the cost-continuation section (`r12:continuation`), introductory statement and conclusion. Appendix `r12:proof` contains full proofs and the complete node table. The abstract is rewritten to state the new executed result. `SUPP_R12.tex` reproduces the full R11 main paper and its complete historical supplement. The previous manuscript's obsolete results retain their version identities rather than being deleted or relabeled.

## R9-F2 — Useful original-economy precision

R10/R11 already replaced the reviewed R8 bounds of 14.0914 and 8.33956 with the three original-model certificates below 0.01. R12 extends the guarantee from those three prices to **every real price in [0.5,8]**. Equation `r12:executed` gives the actual uniform upper, and `results/envelope.json` stores its exact rational value. Every lower endpoint is a feasible policy payoff and every upper endpoint covers all original adaptive controls. The initial state remains `(0,2,1.25)`; we do not replace central-state accuracy by an unsupported whole-state statement.

## R9-F3 — Operational constructive refinement

`replication/cost_case.py` produces a new feasible policy and fitted dual, then invokes the preserved outward policy and optimal-value certifiers. `price_envelope.py` computes exact envelope breakpoints and bisects failed cost intervals. Table `r12:frontier` reports all stages: 3, 4, 7, 13, 17 and 18 nodes, ending below 0.01. The original three-node continuum envelope is about 0.023989184, although each node individually met its target. This explicitly exhibits the distinction between pointwise and uniform accuracy. Failed intermediate target tests and interrupted executions remain visible. Proposition `r12:termination` proves a finite-refinement result conditional on local certificate slack; the actual acceptance uses the exact completed certificate and does not assume an unproved optimizer rate.

## R9-F4 — Absolute accuracy of the nonconvex comparison

The complete inherited paper retains the R10 valid lower relaxation for the unchanged nonquadratic benchmark (`r9:lower`), including its nonquadratic terminal payoff, and the R11 independently reference-solvable accuracy studies. A feasible Riccati controller is still an upper comparator for that minimization problem, never a lower bound. R12 does not mislabel its economic continuation result as an absolute accuracy result for a different benchmark. The structural relaxation gap in the nonconvex benchmark is not claimed to disappear by increasing quadrature precision.

## R9-F5 — Frozen holdout rather than favorable development outcomes

Both complete frozen protocols remain in the main paper. R9's predeclared sign inference remains primary for its six panels; no negative mean confidence interval overrides a nonsignificant sign test. R11's separate expanded-tuning holdout reports adjusted sign-test values approximately 0.00952, 0.58154 and 1.0 at dimensions 8, 16 and 32. Its stronger clipped-feedback comparator and all unfavorable outcomes remain visible. R12 adds no new relative-performance experiment and does not pool these different protocols post hoc.

## R9-F6 — Method-specific tuning and boundary selection

The R11 method-specific tuning study is retained in full: 168 recorded trials, an explicit boundary-extension rule, equal nominal tuning opportunities, and 36 entirely new holdout pairs. Those results and their immutable identities remain in `R11_REVIEW.md` and the R11 publication receipt. The new cost-policy polishing is a deterministic economic certificate construction, not an additional holdout-tuning exercise; we do not pretend that its adaptively selected prices were prospectively frozen external-test samples.

## R9-F7 — Accuracy versus computation

The main paper retains the R11 continuous-reference matched-accuracy calculations and the separation of deployment and implemented optimization error. The new continuation frontier adds computation needed to certify a whole economic parameter interval, not just fixed-budget realized loss. Successful incremental task durations are explicitly labeled, with inherited costs and interrupted attempts excluded from that particular column. They are not presented as total CPU expenditure or a neural-solver dominance frontier. All actual interruption records are separately retained.

## R9-F8 — Heterogeneous evidence

The original stopped economy, the unchanged coupled nonconvex benchmark, and the R11 tracking, mean-reverting and ill-conditioned reference problems remain distinct in the paper. The complete recursive-utility, temporal-self, game and stochastic-trace material remains in the preservation supplement. The continuum-price result strengthens the motivating economic application; it does not count eighteen parameter points as eighteen independent benchmark families, or use them to claim generic superiority.

## R9-F9 — Failure preservation

The adaptive log records every planned price. Two local multi-batch invocations were interrupted by the tool deadline; their original partial files and explicit interruption statuses remain in `archive/interrupted-round2/` and `archive/interrupted-round3/`. All unfinished prices were explicitly retried and certified. The delivery workflow uploads artifacts with `if: always()` and collects all eighteen planned independent checks even if a matrix job fails. Missing or failed final cells produce a permanent invalid aggregate before acceptance. We do not silently exclude an uncompleted price or replace a failed execution with a claimed success.

## R9-F10 — Immutable complete review target

The publication receipt separates the latest report, complete R11 base, canonical manuscript source, independent execution result, and PDF build commits. Local adaptive-development labels are retained honestly. The remote clean-checkout replay evaluates each frozen policy and dual after the source is pinned. The final referee target is the completed build and receipt, not a running experiment branch. Source-only intermediate commits are not identified as completed papers.

## R9-F11 — Theory and implemented output

The inherited quantitative feasible-output allowance, learned-network derivative enclosures, structured action oracle and implemented-output error identities remain in the paper. R12 adds a precise cost-transfer theorem for the actual stored policies and an executable policy-selection rule. It requires only independently enclosed payoff and expenditure for each frozen policy, not convergence of Adam. The original neural classes and ideal policy-iteration results remain preserved, with their hypotheses. The conditional refinement proposition is explicitly not a theorem that an arbitrary optimizer reaches the required slack. This is a direct mathematical connection from recorded outputs to a stronger verified economic guarantee, not a no-go substitute for the proposed method.

## R9-F12 — Certified economic counterfactuals

The existing certified access and cost-effect intervals are retained without changing the economic units. R12 supplies `r12:effects`, `r12:budgetlower` and `r12:budgetupper`, allowing value comparisons and valid budget secants between arbitrary certified-range prices. The original positive access lower at cost eight and monotonicity establish positive access throughout [0.5,8]. The paper distinguishes sign resolution from a small relative interval width at high prices. Policy expenditures are never relabeled as exact optimal expenditures; existence is required only when discussing the budget of an optimal policy, not for the value or regret certificate.

## R9-F13 — Continuous action certification

The inherited rank-one global action certificate through 128 action dimensions remains in the main paper, together with its actual-network derivative checks at 8 and 16 dimensions. The original economic model also retains its complete analytic action selector at a fixed jet. R12's policy-library selection is an exact finite comparison over pre-certified policies for a price; it is not advertised as a generic high-dimensional global action solver. None of the original tensor-grid safeguard's costs is hidden by the new construction.

## R9-F14 — Theorem-level novelty boundary

The related-work section retains the distinctions from classical stopped verification, monotone approximation, controlled Markov chains, information relaxations, and moment methods. The new section explicitly states that convexity of a supremum of affine payoffs is classical. The new executed object is a parameter-uniform feasible-policy certificate for the unchanged stochastic first-exit economy, with sign-correct expenditure transfer, exact breakpoint acceptance, and a quantified refinement condition. Its contribution is the complete constructive economic guarantee, not a claim to have invented convex analysis or universal global optimization.

## Repository and presentation

The official inherited `econsocart` class and configuration remain unchanged. Definitions precede claims; assumptions, theorem statements, economic interpretation and full proofs have separate locations. Every historical file is checked against the complete R11 base, with the former revision index archived verbatim and retained as a prefix of the updated index. The manuscript and supplement are compiled with no accepted overfull boxes, unresolved references or unresolved citations. An inherited empty-frontmatter-anchor notice is disclosed in the validation report rather than suppressed by changing the journal class.

## Remaining scope, not omitted evidence

The new uniform guarantee varies the adjustment-cost parameter, not every initial state or every economic primitive. Its policy generator is the recorded learned-and-polished time-control class; its upper bound covers the larger original adaptive class. The mathematical guarantee is not a universal neural-optimizer rate, and the external comparisons do not establish universal solver dominance. These distinctions preserve the positive claims that have actually been established and keep all the technical material available for the next referee.
