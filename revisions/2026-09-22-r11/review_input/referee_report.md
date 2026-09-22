# External Referee Report on Neural Bellman Operators — Revision R9

**Repository:** `TrillionniumFoundation/NBO`  
**Reviewed revision branch:** `revision/econometrica-r9-constructive-certification-2026-09-22`  
**Pinned source commit:** `46aef70a24f74cf57503018a7e7f21cb46af08e3`  
**Inherited complete manuscript commit:** `939b612ff57794a2127f0b0adeb74ab7eef9e72e` (R8)  
**Review date:** 2026-09-22  
**Standard:** Econometrica-level numerical methods / quantitative economics  
**Recommendation:** **REJECT IN ITS PRESENT FORM**  
**Scope:** External-style technical review, not an editorial decision.

## 1. Executive assessment

R9 does not yet constitute a revised paper. Relative to the complete R8 manuscript branch, the R9 source commit reviewed here changes no main-manuscript text, no supplement text, no theorem/proof file, no numerical table, and no original-economy computation. The R8-to-R9 diff adds the R8 referee report, a source-snapshot workflow, a frozen external-benchmark protocol, one external-suite script, and one workflow that is intended to execute that protocol. The current paper read by a referee is therefore still R8.

This distinction is decisive. R8 had already reached the point where the scientific blocker was clear: the original continuous NDU economy could be verified only with regret bounds of 14.0914 and 8.33956 against a stated 0.01 target. R9 has not changed those numbers, has not constructed a tighter witness, has not executed the semigroup error budget, and has not converted the adjustment-cost theorem into a certified economic quantitative result. The flagship computation remains unresolved by orders of magnitude.

R9 does make a useful attempt to strengthen the external SOC-MartNet comparison. It freezes a protocol before holdout execution, increases the holdout to twelve seeds, adds dimension 32 and a 30-second budget, randomizes within-seed method order, introduces limited symmetric learning-rate tuning, and predeclares an exact sign test with Bonferroni correction. Those are meaningful improvements in experimental discipline.

However, the first completed holdout panels already show why the earlier R8 external result was not sufficiently robust. At the 10-second budget, the new holdout gives mean NBO-minus-SOC realized-cost differences of approximately -0.503 at d=8, -0.323 at d=16, and -0.820 at d=32. At d=16 only 8 of 12 paired seed differences are negative. The predeclared one-sided exact sign-test p-value is 0.19385, and the six-panel Bonferroni-adjusted value is 1.0. Thus the robust inferential criterion predeclared by R9 does not support a d=16, 10-second advantage, even though the descriptive Student interval for the mean remains below zero. The mean is being pulled by several large favorable differences while four seeds favor SOC.

This matters because R8 reported much larger mean differences, approximately -1.718 at d=8 and -2.247 at d=16. The independent R9 holdout reduces the magnitudes to roughly 29% and 14% of those R8 values, respectively. The direction remains favorable on average, but the strength and robustness of the effect are clearly sensitive to the tuning and holdout design. A serious revision must replace the R8 development-era claim with the complete frozen-holdout evidence rather than presenting the R9 suite as an auxiliary add-on.

I therefore recommend rejection in the present form. R9 improves experimental hygiene around one external benchmark, but it does not close the paper's central numerical-methods chain and, in one key panel, it weakens rather than confirms the robustness of the previous comparative evidence.

## 2. What R9 improves

I regard the following changes as constructive:

1. The external protocol is frozen in `revisions/2026-09-22-r9/protocol_external.json` before the holdout seeds are used.
2. The author implementation remains pinned to `sx-fang/MartNet` commit `991ea8dde5bad6ba912eb8cc48b0cb48dbdd6c2a`.
3. Holdout seeds `720,...,731` are separated from the disclosed development/warmup seed.
4. The comparison expands to dimensions 8, 16, and 32 and budgets of 10 and 30 seconds.
5. Method order is randomized within seed after warmup.
6. Initial actor and critic parameter hashes are asserted equal within each method pair.
7. Audit Brownian noise is common within a pair, which is appropriate for a paired comparison.
8. The protocol explicitly distinguishes descriptive Student intervals from exact sign inference.
9. Bonferroni correction over the six dimension-budget panels is predeclared.
10. Missing or nonfinite outputs are intended to fail aggregation rather than be silently dropped.

These are real improvements over R8-F7 and R8-F11. They do not, however, resolve the paper's primary scientific blockers.

## 3. Blocking finding R9-F1: R9 is not a manuscript revision

The R8-to-R9 comparison contains no modification to:

- `ECTA_R8.tex`;
- `SUPP_R8.tex`;
- `revisions/2026-09-22-r8/paper/main.tex`;
- `revisions/2026-09-22-r8/paper/numerics.tex`;
- `revisions/2026-09-22-r8/paper/proofs.tex`;
- any R8 manuscript table;
- the original-payoff continuum witness computation.

The scientific text therefore still makes the R8 claims and still contains the R8 limitations. A new experiment protocol is not a response to the full referee report.

**Required:** produce an actual revised manuscript that incorporates the complete R9 evidence, revises every affected claim, and responds point-by-point to the outstanding numerical-methods findings.

## 4. Blocking finding R9-F2: the flagship original economic computation remains uncertified at useful precision

The original continuous first-exit NDU problem remains the central economic application. Its executed continuous regret bounds remain approximately

- 14.0914048908 for the retained N=6 policy;
- 8.3395605260 for the retained N=12 policy;

against a stated target of 0.01.

The better certificate is therefore more than 800 times the target. The paper's useful theorem about approximate comparative statics says, correctly, that the numerical error must be smaller than the economic effect being interpreted. The computation still fails that requirement.

Nothing in R9 changes the witness family, the residual enclosures, the boundary treatment, the policy, or the resulting gap. The external synthetic benchmark cannot substitute for solving the motivating economic problem.

**Required:** obtain a verified original-payoff continuum error small enough to resolve the economic quantity actually reported.

## 5. Blocking finding R9-F3: “constructive certification” has not been delivered

The branch name emphasizes constructive certification, but the new R9 files implement only an external comparative-performance experiment. They do not implement:

- constructive refinement of upper/lower witnesses for the original NDU model;
- occupation-potential refinement;
- adaptive state partitioning driven by certificate width;
- a complete semigroup error enclosure;
- a non-enumerative global Hamiltonian certifier;
- a proof-backed stopping rule that shrinks the original-model certificate below the target.

R8 already explained what these routes would require. R9 does not execute them.

**Required:** turn at least one stated certification route into an operational algorithm, show certificate width versus computation/refinement, and close the original-model target.

## 6. Blocking finding R9-F4: the external suite still has no absolute accuracy reference

The R9 script introduces a clipped Riccati/LQ feedback as an additional policy. This is not an independent lower bound for the nonconvex minimization problem.

For a minimization problem, the realized cost of any feasible policy is an **upper bound** on the optimal cost, not a lower bound. The LQ controller may be a useful benchmark policy, but it cannot by itself give an absolute regret bound for NBO or SOC-MartNet on the unchanged nonquadratic objective.

This is especially important because the module docstring says that “the independent lower bound is separate,” while no such lower-bound calculation is present in the reviewed R9 source. The protocol likewise calls the Riccati object an “other comparator,” not a certified bound.

Consequently, even a statistically clear NBO-minus-SOC difference would establish only relative pipeline performance. It would not establish that either method is accurate.

**Required:** add a valid lower bound, a verified reference solution, a dual certificate, or a low-dimensional continuation of the same benchmark family with independently controlled absolute error.

## 7. Blocking finding R9-F5: the frozen holdout materially weakens the earlier external-performance claim

At the time of this review, the 10-second holdout jobs for d=8,16,32 have completed in workflow run `35682656529`. From their recorded seed-level outputs:

### d = 8, 10 seconds

- 12/12 paired differences favor NBO;
- mean difference: -0.50298;
- descriptive Student 95% interval: approximately [-0.63143, -0.37453];
- exact one-sided sign-test p-value: 0.000244;
- six-panel Bonferroni value: 0.001465.

### d = 16, 10 seconds

- 8/12 paired differences favor NBO and 4/12 favor SOC;
- mean difference: -0.32302;
- median difference: approximately -0.16716;
- descriptive Student 95% interval: approximately [-0.61775, -0.02828];
- exact one-sided sign-test p-value: 0.19385;
- six-panel Bonferroni value: 1.0.

### d = 32, 10 seconds

- 12/12 paired differences favor NBO;
- mean difference: -0.81974;
- descriptive Student 95% interval: approximately [-0.96244, -0.67703];
- exact one-sided sign-test p-value: 0.000244;
- six-panel Bonferroni value: 0.001465.

The d=16 result is exactly the sort of case for which the predeclared sign test is useful: the mean is negative because some NBO-favorable seeds have large magnitude, but the direction is not stable across seeds. A revised paper must not privilege the negative Student interval and demote the predeclared exact sign test after observing the data.

Moreover, the holdout means at d=8 and d=16 are dramatically smaller in magnitude than the R8 six-seed development-era means. This is evidence that the original comparison was highly sensitive to the experimental protocol.

**Required:** report the frozen holdout as the primary comparative evidence, distinguish exploratory R8 results from confirmatory R9 results, and interpret panels according to the predeclared inference rule.

## 8. Major finding R9-F6: the “symmetric tuning” exercise is too narrow and lands on the tuning-grid boundary

R9 tunes only the actor/critic learning-rate multiplier over ({1/3,1,3}), using two tuning seeds. The selected multipliers are:

- d=8: NBO 1/3, SOC 3;
- d=16: NBO 3, SOC 3;
- d=32: NBO 1/3, SOC 3.

Thus SOC selects the **largest allowed multiplier in every dimension**, and NBO also selects the largest multiplier at d=16. This is a warning that the tuning box may be truncating the preferred region. A comparison cannot be called well-tuned merely because both methods were offered the same three scalar multipliers.

The asymmetry is also structural. The SOC adversary learning rate is explicitly not tuned. Its test-network architecture, multiplier dynamics, J/K choices and related solver parameters are fixed. NBO and SOC have different training mechanisms and different effective update costs. Equal wall-clock opportunity is a valid performance metric, but a one-dimensional learning-rate multiplier does not establish that each method received a comparably serious method-specific tuning effort.

**Required:** justify the tuning domain, expand it when optima hit the boundary, tune method-specific consequential hyperparameters under equal tuning budgets, and separate “same scalar grid” from “fair method-specific tuning.”

## 9. Major finding R9-F7: fixed wall-clock performance is not a matched-accuracy computational frontier

The 10-second and 30-second panels answer one useful question: which configured pipeline gives lower realized cost after a specified CPU training budget?

They do not answer:

- how much wall-clock time each method requires to reach a common absolute error;
- how either method approaches the unknown optimum;
- whether one method dominates at longer budgets;
- whether the ordering changes with tighter deployment meshes;
- whether either method's stopping criterion correlates with true error.

Without an absolute reference, the paper cannot convert these fixed-budget comparisons into a numerical-efficiency claim in the usual scientific-computing sense.

**Required:** add an absolute error axis and report matched-accuracy as well as matched-wall-clock frontiers.

## 10. Major finding R9-F8: one synthetic benchmark family is not evidence of general numerical superiority

R9 expands one coupled nonconvex family across three dimensions and two budgets. That is better than a single point, but it is still one hand-designed objective, one diffusion structure, one horizon, one action box, one architecture family, and one external comparator.

The paper's broader framework includes stopping, recursive utility, sophisticated temporal selves, games, and trace estimation. None of those claims is validated by the R9 holdout.

**Required:** either narrow the performance claim to this benchmark family or predeclare a heterogeneous multi-problem suite that includes problems with different conditioning, boundary behavior, coupling structures, and reference-solution mechanisms.

## 11. Major finding R9-F9: the workflow does not fully implement the stated failure-preservation policy

The protocol says every run should be preserved and the aggregate should fail on missing/nonfinite output. The workflow's `collect` job, however, has a normal `needs: holdout` dependency. If any holdout matrix job fails, the collection/commit step will not run by default.

In that event, successful sibling outputs may remain only as GitHub Actions artifacts and logs rather than being committed into the revision package. Those artifacts are retention-limited. This is weaker than the stated “preserve every run” policy.

A robust evidence pipeline should collect with `if: always()`, record explicit success/failure status for every planned cell, preserve successful outputs, preserve failure metadata, and then mark the aggregate invalid when required cells are missing.

**Required:** make failure preservation part of the versioned evidence package, not an ephemeral CI side effect.

## 12. Major finding R9-F10: the reviewed R9 package is incomplete and mutable at the branch level

At the pinned source commit, the external workflow is still running. The three 30-second holdout jobs and the final collection step have not yet produced a committed `summary.json` or complete R9 result directory.

The workflow is designed to push generated results back to the same R9 branch. That is acceptable only if source identity and result identity are treated as separate immutable commits. A branch name by itself is not a stable review target.

This report therefore intentionally pins `46aef70...` as its reviewed source. It does not speculate about unfinished 30-second results.

**Required:** publish a complete result commit, bind it to the frozen source commit in a manifest, revise the paper from that result commit, and make the referee entry point identify both hashes.

## 13. Blocking finding R9-F11: the neural optimization theory remains disconnected from the implemented algorithm

The strongest convergence argument in the manuscript is still an exact-operator result requiring compactness, strong (C^{1,2}) precompactness/continuity, selector continuity, closure under improvement, and comparison. These assumptions are not proved for the actual neural classes, Adam/RMSprop trajectories, stochastic training objectives, or stopped economic application.

The rigorous results are principally a posteriori verification results: if one supplies a policy and valid witnesses/enclosures, then one can bound performance. That is useful. But it does not show that NBO training itself converges to such objects at a stated rate or cost.

The R9 holdout does not address this theory-algorithm gap.

**Required:** either establish a quantitative link from neural approximation/optimization errors to the verified quantities, or reposition the contribution explicitly as an a posteriori verification architecture that can sit on top of multiple policy generators.

## 14. Blocking finding R9-F12: the economic comparative static remains a theorem without a certified quantitative application

The adjustment-cost monotonicity theorem is one of the paper's more economically interpretable results. Yet the reported finite-scheme adjustment budgets are still not accompanied by continuum enclosures tight enough to resolve their differences. The original continuous regret bounds are far too large.

Thus the paper has a theorem explaining what accuracy is required, but the central computation still does not attain that accuracy.

**Required:** produce certified intervals for the relevant value functions, adjustment budgets, and welfare-access quantities whose widths are smaller than the reported economic effects.

## 15. Major finding R9-F13: the finite safeguard remains exhaustive and low-dimensional

Nothing in R9 changes the finite candidate-action safeguard. The favorable low correction fraction does not remove the need to enumerate the candidate action set during certification. The current NDU audit remains tied to a low-dimensional tensor action grid plus the neural proposal.

This is a major limitation for a method advertised as relevant to high-dimensional control. The external neural benchmark avoids the finite safeguard, but it also lacks absolute certification.

**Required:** demonstrate a scalable global action certifier, or state clearly that the rigorous finite safeguard is limited to low action dimension.

## 16. Major finding R9-F14: the paper still lacks a clean novelty boundary against rigorous numerical control

The strongest mathematical objects in the paper are supersolution/subsolution verification, stopped Itô arguments, finite dynamic-programming gain bounds, and telescoping operator-error decompositions. The manuscript discusses neighboring neural methods more carefully than earlier versions, but the novelty claim still needs to be stated theorem-by-theorem against classical verification, monotone dynamic programming, validated numerics, and rigorous HJB error analysis.

The external benchmark cannot carry this novelty burden because it is comparative empirical evidence, not a new certification theorem.

**Required:** identify exactly which assumptions, boundary setting, constructive certificate, or economic error-calibration result is new, and benchmark that object against the rigorous-numerics literature rather than only neural-control papers.

## 17. Reproducibility and repository hygiene

The repository is substantially more auditable than early revisions, but several details should be fixed:

1. `REVISION_INDEX.md` remains stale and identifies R3 as the current revision.
2. R9 should have a human-readable referee entry point analogous to `R8_REVIEW.md`.
3. The exact frozen source commit, execution result commit, manuscript-build commit, and referee source commit should be recorded separately.
4. Failed matrix cells should be retained in versioned evidence.
5. The final manuscript should be generated only after the frozen holdout is complete, so that table text cannot remain out of sync with the evidence.

These are secondary to the scientific blockers above.

## 18. Minimum conditions for a credible next submission

### P0 — close the original economic computation

- Construct an operational witness- or semigroup-refinement algorithm.
- Obtain a continuous original-payoff certificate below the economically calibrated tolerance.
- Show certificate width and runtime as the refinement target tightens.
- Convert the adjustment-cost theorem into a genuinely certified quantitative conclusion.

### P0 — establish absolute numerical accuracy

- Add a valid lower bound, dual/reference solution, or verified low-dimensional continuation for the nonconvex benchmark.
- Report absolute regret/error in addition to NBO-minus-comparator differences.
- Add matched-accuracy frontiers.

### P0 — finish and incorporate the frozen R9 evidence

- Complete all six predeclared dimension-budget panels.
- Treat the exact sign test as primary where the protocol says it is primary.
- Do not describe d=16, 10 seconds as robustly favorable if the sign test remains non-significant.
- Replace R8 development-era external claims with the frozen holdout results in the actual manuscript.

### P1 — strengthen comparative fairness

- Expand tuning ranges when selected settings hit a boundary.
- Give each method an equal tuning budget but allow method-specific consequential hyperparameters.
- Add at least one additional credible comparator/reference.
- Use a predeclared multi-problem benchmark suite.

### P1 — align theory and implementation

- Connect neural training errors to certified regret, or explicitly reposition NBO as a verification framework rather than a convergent neural solver theorem.
- Demonstrate a non-enumerative action certification route if high-dimensional action claims are retained.

### P1 — harden evidence retention

- Collect results and failure metadata under `if: always()`.
- Commit a complete planned-cell manifest even when the run fails.
- Pin separate source, result, build, and review commits.

## 19. Recommendation

**Reject in its present form.**

R9 improves the design of one external comparison but does not revise the paper's central numerical result. The flagship NDU economy remains uncertified at economically useful precision; no constructive original-model certifier has been implemented; the external benchmark still lacks an absolute accuracy reference; and the theory remains largely a posteriori verification rather than a convergence theory for the implemented neural optimizer.

The new frozen holdout also demonstrates why the previous external evidence should not be treated as settled. At d=16 and 10 seconds, the robust predeclared sign criterion fails, and the effect magnitudes at d=8 and d=16 are much smaller than in R8. That is scientifically useful information, but it requires the manuscript to become more cautious, not more expansive.

A credible next revision should close one complete chain:

**economically meaningful model -> trained policy/value -> constructive global certificate -> small absolute error -> economic conclusion larger than the error -> computational cost to reach that accuracy.**

The current repository has pieces of this chain. It does not yet close it.

---

## Evidence reviewed

I reviewed the following repository state and evidence:

- `revision/econometrica-r9-constructive-certification-2026-09-22` at `46aef70a24f74cf57503018a7e7f21cb46af08e3`;
- the R8 complete manuscript inherited at `939b612ff57794a2127f0b0adeb74ab7eef9e72e`;
- `ECTA_R8.tex`, `SUPP_R8.tex`, `R8_REVIEW.md`;
- `revisions/2026-09-22-r8/paper/main.tex`;
- `revisions/2026-09-22-r8/paper/numerics.tex`;
- `revisions/2026-09-22-r8/paper/proofs.tex`;
- the R8 response, validation records, continuum certificates, safeguard/mesh results, and external comparison described in the manuscript;
- `reviews/2026-09-22-econometrica-r8/referee_report.md`;
- `revisions/2026-09-22-r9/protocol_external.json`;
- `revisions/2026-09-22-r9/replication/external_suite.py`;
- `.github/workflows/r9-external-holdout.yml`;
- `.github/workflows/r9-source-snapshot.yml`;
- the R8-to-R9 commit/file comparison;
- workflow run `35682656529`;
- completed 10-second holdout job logs:
  - d=8: job `106603288104`;
  - d=16: job `106603288110`;
  - d=32: job `106603288073`;
- completed tuning jobs and selected multipliers:
  - d=8: job `106602738332`;
  - d=16: job `106602738288`;
  - d=32: job `106602738092`.

The three 30-second holdout jobs and final collection step were still in progress at the pinned review time and are deliberately not treated as evidence in this report.
