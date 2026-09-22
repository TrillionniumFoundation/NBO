# Response to the R9 Econometrica numerical-methods referee

**Date:** September 22, 2026.  
**Manuscript:** *Neural Bellman Operators*, Revision R10.  
**Revision branch:** `revision/econometrica-r10-referee-resolution-2026-09-22`.  
**Referee input:** review commit `251ad29668788b2a911c4ca6f9c0a226886518d6`, report blob `42cee0954515e5578dc579a4ca0428bb4e399b2e`.  
**Report's reviewed source:** `46aef70a24f74cf57503018a7e7f21cb46af08e3`.  
**Completed R9 source inherited by this revision:** `23f40e730fcea04efe3d84690d4f0fff5ae466e8`.

We thank the referee for requiring a complete chain from the original economic problem to an independently verified numerical result and an economic conclusion larger than its uncertainty. We have produced an actual revised paper and a new mathematical construction. The original continuous central-state regret target is now met at all three stated adjustment-cost coefficients. The paper does not accomplish this by deleting the model, changing its payoff or stopping contract, replacing continuous controls by a finite safeguard, or presenting policy-evaluation precision as optimality precision.

The timing distinction is important. The report accurately described the early R9 source at its pinned commit. The subsequent completed R9 delivery supplied a manuscript, the full frozen holdout, a restricted-economy dual, external absolute lower bounds, and a structured action certifier. It still left the flexible-policy regret around 0.10634 at cost two. We preserve and build on that completed delivery, identify its inherited contributions explicitly, and do not count them as new R10 experiments.

## Principal new result

| Cost coefficient | Independently evaluated feasible-policy payoff | Upper bound on the original optimum | Certified regret upper |
|---|---|---:|---:|
| 0.5 | [-1.27267126, -1.27265474] | -1.26279686 | 0.00987440 |
| 2 | [-1.29502451, -1.29501124] | -1.28530723 | 0.00971727 |
| 8 | [-1.32817604, -1.32816919] | -1.31820708 | 0.00996896 |

Displayed endpoints are rounded outward. Gaps are computed from the full-precision endpoints before display rounding. The policies are **new, explicitly polished time-control outputs**, not the previously retained state-feedback or unpolished time-control policies. The upper bounds cover every original adapted consumption, portfolio, and adjustment control. All older policies, proofs, and numerical records remain unchanged.

The new theorem, “Affine-preference dual and a computable initial upper bound,” is in the current paper's section on constructive flexible-economy certification. Its complete proof derives a global supporting-source inequality on the verification rectangle, a conditional-control coefficient, a Gaussian Poincare variance allowance, the original correlated-noise covariance correction, and the first-exit continuation potentials. The calculation uses one-Gaussian interval quadrature with analytic tails. The current paper also proves a feasible-output perturbation allowance with explicit economic constants.

## R9-F1 — An actual manuscript revision

**Implemented.** `ECTA_R10.tex` and the R10 paper files contain revised abstract, introduction, principal results, economic interpretation, numerical tables, methodological comparisons, conclusion, and complete new proofs. This is not a source-only experimental protocol. The earlier fitted construction is preserved verbatim in a dated appendix. `SUPP_R10.pdf` preserves the entire completed R9 paper and its full preservation supplement; the original source files remain in the branch.

The canonical entry point is `R10_REVIEW.md`; the root index now points to R10. The completed source, execution results, and manuscript build have separate immutable identities in the publication receipt.

## R9-F2 — Useful absolute precision for the original economic computation

**Implemented for all three declared central-state instances.** The table above gives regret below 0.01 at costs 0.5, 2, and 8. The running utility, adjustment cost, consumption units, correlated diffusions, control bounds, domain, discount, terminal settlement, and first-exit liquidation covenant are unchanged.

The primal evaluator checks exact binary deployment constants against the exact decimal action bounds, proves strict wealth feasibility, and includes a positive exact-preference-exit allowance. The dual upper applies to the original full continuous opportunity set. Thus neither the 1.3e-5 policy-evaluation width nor a finite-grid residual is being relabeled as a regret bound. The guarantee is at the declared initial state; a uniform initial-state surface certificate is not inferred.

**Evidence:** `results/actor_k*.json`, `policy_certificate_k*.json`, `flexible_dual_k*.json`, and `scientific_summary.json` under the R10 directory.

## R9-F3 — Operational constructive certification

**Implemented.** `replication/flexible_dual.py` constructs and checks the affine-preference dual on complete interval covers. It then refines the transformed-time/Gaussian source mesh through 4,096, 16,384, and 65,536 boxes. All three coarse calculations miss the target; the cost-0.5 and cost-2 instances cross it at the second level, and cost eight crosses it at the third. The failed coarse precision flags are retained rather than omitted.

The stopping rule accepts only after subtracting a separately verified policy lower endpoint from the global optimal-value upper endpoint. The refinement table reports cumulative verification cost and the individual source, control-gap, variance, localization, and tail quantities. No semigroup error entry is silently assigned zero: this route directly verifies the continuous problem and does not invoke the inherited Euler scheme. A fixed affine relaxation is not claimed to attain every arbitrarily small tolerance, but its finite execution does attain the stated 0.01 target.

## R9-F4 — An absolute reference for the external nonconvex problem

**Supplied by completed R9 and retained in the current paper.** The scalar-integral Cole–Hopf relaxation gives a genuine lower bound for the unchanged bounded-control minimization problem. It retains the nonquadratic terminal payoff, bounds the running cost pointwise, and relaxes control bounds in the direction appropriate for a lower bound. Its positive scalar integral is enclosed with analytic tails and outward arithmetic.

The independent clipped quadratic-feedback rule remains a **feasible comparator**, not a lower bound. The new paper retains this distinction and does not use the lower-reference quadrature width as an estimate of the structural relaxation gap. External Monte Carlo costs minus that lower reference are not described as deterministic policy-regret enclosures.

**Evidence:** the retained absolute-lower-bound proposition and `revisions/2026-09-22-r9/results/absolute_lower_d*.json`.

## R9-F5 — Complete frozen holdout and primary inference

**Implemented in completed R9 and verified again for R10.** All six panels and all 72 seed pairs remain the primary external comparative evidence. The d=16, 10-second Bonferroni-adjusted exact sign value remains 1; its 30-second counterpart is approximately 0.438. Neither is described as a robust seed-level ordering. Descriptive Student intervals are not promoted over the predeclared exact sign rule.

The completed holdout replaces the earlier exploratory comparison in the current paper. Its smaller effect magnitudes are not hidden. The independent quadratic-feedback baseline has lower mean cost than both learned methods in every panel, and that unfavorable result remains explicit. The R10 validator recomputes the exact binomial sign probabilities from the retained twelve differences per panel and checks every planned seed identity. No holdout seed is reused for a new tuning claim.

## R9-F6 — Boundary-selected and insufficiently method-specific tuning

**The stronger tuning requirement is not claimed to be experimentally closed.** We agree that equal numbers of trials on one common learning-rate grid do not establish equally effective method-specific tuning. SOC selects the upper grid boundary in all three dimensions; NBO also selects a boundary. The current paper keeps the exact architectures, adversary configuration, optimizer differences, trial counts, and selected-domain limitation visible.

R10 does not silently enlarge the grid after reading the same holdout, relabel that data as a new confirmation, or claim that the adversary and multiplier dynamics have been tuned when they have not. The frozen conditional comparison remains intact; no broader best-tuned-method claim is needed for the new original-economy theorem or certificate. A newly executed, separately held-out method-specific tuning study is not included in this delivery. This remains an explicitly identified experimental limitation rather than a falsely closed item.

## R9-F7 — Absolute-error and time-to-accuracy axes

**Advanced by an executed original-model verification frontier; external head-to-head matched accuracy remains unestablished.** The new table gives certified regret against 0.01 and cumulative work required to cross that threshold, not just realized cost after a clock budget. It includes policy evaluation and dual preparation/refinement and explicitly excludes inherited network training, fitting, imports, and setup. The raw stage clocks are versioned.

The external family also retains its rigorous absolute lower reference and all matched-wall-clock panels. Two external training budgets plus sampled policy costs do not establish an all-in, matched-accuracy dominance result, and the paper does not say otherwise. The new frontier closes the operational certification-cost link for the principal economic instances; it is not presented as an external neural-efficiency tournament.

## R9-F8 — Scope across problem families and broader operators

**The theorem/evidence boundary is made explicit without removing the broader material.** The original stopped economic family now has absolute central-state certificates; the coupled nonconvex family has separate action certificates, an absolute lower reference, and a frozen comparison. These are distinct claims and are not pooled into a universal superiority statement.

Recursive utility, sophisticated temporal selves, games, trace estimation, and their historical derivations remain in the complete preservation supplement. Their hypotheses and optimality notions are not replaced by the additive-utility numerical results. A heterogeneous, newly executed multi-problem neural-performance suite is not claimed. No equation or historical numerical result is deleted to manufacture apparent generality or apparent closure.

## R9-F9 — Failure-preserving versioned evidence

**Implemented in the new delivery workflow.** Each planned cost cell has an explicit status record. The collection job runs under `if: always()` after the matrix, retains successful outputs and failure diagnostics, records missing cells explicitly, and creates a result commit even when the aggregate is invalid. Only after preservation does an incomplete or nonfinite aggregate fail. This avoids an ordinary `needs` dependency silently skipping the versioned collection step.

`replication/collect_evidence.py` performs completeness and consistency checks against the complete declared cell plan; `run_cell.py` saves partial progress and exception metadata. Fault-injection tests exercise missing cells, nonfinite certificates, and explicit failed cells. Those tests are labeled synthetic pipeline tests, not failed economic experiments. Successful and unsuccessful refinement levels are separately retained within each real cell.

## R9-F10 — Immutable source, results, build, and review identities

**Implemented.** The source publication, independent execution-result collection, manuscript build, and final receipt are separate commits. The receipt records the reviewed source, report commit/blob, completed R9 base, new canonical source, result commit, manuscript-build commit, workflow run, and hashes of the two PDFs and validation records. A moving branch name alone is not the review target.

The exact R9 review report is imported from its pinned blob for the canonical package. The inherited frozen external protocol and full result commit remain separately identified as `46aef70...` and `58007e6...`. No unfinished 30-second job is used as evidence: the completed holdout predates this R10 manuscript.

## R9-F11 — Quantitative implementation-to-certificate link

**Implemented for the controls and certificate actually deployed.** The current paper proves an explicit original-payoff allowance for feasible consumption and adjustment output errors. With their time-integrated errors denoted by delta_c and delta_theta, the allowance is

`(3 + 0.2 exp(0.02)) delta_c + (25 + 0.2 k + 0.032) delta_theta + 8(14.1 + 0.02 k) exp(-72)`.

The proof includes exact first-exit events and requires budget feasibility separately. The actual stored constants incur no unmeasured network-evaluation allowance because they are verified as exact binary reals. The accepted-output rule returns a policy only after a proved regret inequality, and its full finite execution is present. The retained learned-jet/action and cover/oracle theorem supplies the complementary derivative-error interface.

These are quantitative connections between implemented objects and performance. They are not an unproved theorem that Adam, RMSprop, or L-BFGS-B converges globally for arbitrary neural classes. The earlier exact-operator theory remains intact with its hypotheses; it is not used to justify an optimizer trajectory that fails those hypotheses.

## R9-F12 — Certified economic comparisons rather than qualitative monotonicity alone

**Implemented for the reported welfare and deployed-policy expenditure comparisons.** At cost two, optimal access welfare is in `[0.04096859, 0.05973218]`. The original optimal welfare loss when cost rises from two to eight is in `[0.02318257, 0.04286880]`. Each interval's width is smaller than its lower endpoint, so the stated economic effect dominates its uncertainty.

All three deployed adjustment expenditures have separately verified intervals. Optimal expenditure at cost two is additionally enclosed by valid value secants in `[0.00386376, 0.01960529]`, conditional on an optimizer's existence. The lower endpoint is positive; the upper remains the primitive bound. We do not replace this broad optimal-expenditure set by the much narrower interval for the displayed approximate policy. The 0.5-to-2 cost comparison and cost-eight access comparison resolve their signs but have larger relative uncertainty; the text says so. No optimal pointwise adjustment ordering is inferred.

## R9-F13 — Beyond the finite tensor safeguard

**Supplied by completed R9 and strengthened in the original model.** The retained rank-one action certifier uses scalar partitioning and strongly convex dual subproblems rather than a tensor action grid, with executed continuous-action certificates through 128 dimensions. The learned eight- and sixteen-dimensional cases include interval derivative allowances for the actual checkpoint weights.

The new original-economy upper also avoids action enumeration: every portfolio term cancels algebraically, consumption is handled by its exact constrained conjugate, and adjustment is bounded through an adapted conditional coefficient and its conjugate. These are constructive structured routes, not a generic dimension-free theorem for every nonconvex Hamiltonian. The earlier low-dimensional tensor safeguard and all of its costs remain preserved, not retroactively renamed scalable.

## R9-F14 — Novelty relative to rigorous numerical control

**Implemented theorem by theorem.** Classical stopped verification, Gaussian integration by parts, Poincare inequalities, convex conjugacy, and primal–dual analysis are used as foundations, not claimed as inventions. The new contribution is the model-specific affine-preference supporting construction, its explicit conditional-coefficient variance correction, its original-contract localization, and its executed combination with independent feasible-policy bounds to cross the economic tolerance.

The related-work section distinguishes this construction from classical monotone approximation, controlled Markov chains, sparse grids, information-relaxation duality, occupation-measure relaxations, and neural policy iteration. The new proof makes every assumption and constant used by the calculation visible. The output-error proposition and the accuracy-calibrated welfare intervals are separate from the comparative-performance evidence. The frozen external comparison is not used as a substitute for mathematical novelty.

## Preservation and verification record

The principal source uses the repository's `econsocart` class in `ecta` mode and retains the author metadata. The source tree contains the complete new proof, current numerical tables, an independent re-execution runner, the failure-preserving collector, exact input identities, a full historical-file map, and manuscript/evidence validation. The two PDFs are built from a clean canonical source/result checkout before publication.

Every one of the 948 inherited files is checked against the completed R9 base. The sole updated historical path is the root index, whose preceding bytes are archived. The earlier fitted section is preserved verbatim in the R10 appendix, and both complete preceding PDFs are reproduced in the supplement. No primary, review, or older revision branch is merged into or overwritten by this revision.

The principal original-model 0.01 target is closed. An expanded method-specific external tuning study and an external all-in matched-accuracy superiority claim are **not** marked as established. This separation is part of the evidence record, not a substitution of a weaker economic model for the one the referee asked us to solve.
