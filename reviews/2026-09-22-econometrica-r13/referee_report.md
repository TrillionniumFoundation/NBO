# Referee Report — Neural Bellman Operators, purported Revision R13

**Venue standard:** Econometrica-level numerical/computational methodology  
**Recommendation:** **Reject / return without a new substantive review round. The submitted R13 branch is not a scientific revision of R12.**  
**Review date:** 2026-09-22  
**Reviewed branch:** `revision/econometrica-r13-neural-state-verification-2026-09-22`  
**Reviewed commit:** `442ef9be75e620b53f923cdc476be50edaa64ca7`  
**Last actual manuscript revision:** `revision/econometrica-r12-uniform-cost-certification-2026-09-22`, commit `4ff0404833a6d6773bcf7afab361013d732df686`

## 1. Executive assessment

I first audited the identity of the purported R13 revision before re-evaluating the numerical claims. That audit is decisive.

The branch named `revision/econometrica-r13-neural-state-verification-2026-09-22` points to commit `442ef9be75e620b53f923cdc476be50edaa64ca7`. This is exactly the commit whose message is

> `review(r12): add Econometrica numerical-methods referee report`.

Relative to the actual R12 manuscript commit `4ff0404833a6d6773bcf7afab361013d732df686`, the purported R13 branch is ahead by exactly one commit and the only changed file is

`reviews/2026-09-22-econometrica-r12/referee_report.md`

with 788 added lines. There are no manuscript, theorem, code, result, replication, table, figure, or response changes.

More strongly, the purported R13 branch is **identical** to the previous review branch
`review/econometrica-r12-numerical-methods-2026-09-22-4ff0404`: zero commits ahead, zero commits behind, and zero changed files.

The repository root contains `ECTA_R12.tex/.pdf` and `SUPP_R12.tex/.pdf`; there is no `ECTA_R13`, `SUPP_R13`, R13 response, R13 result directory, R13 publication receipt, or R13 replication package. The `revisions/` directory stops at `2026-09-22-r12`.

Therefore there is no new R13 scientific object for a referee to assess. The last reviewable paper remains R12, and the previous R12 report is part of the current branch rather than something the authors have answered.

This is not a cosmetic repository issue. A revision branch name is not evidence of a revision. For a paper whose central contribution is auditable numerical verification, immutable version identity is itself part of the scientific record.

I consequently maintain the R12 rejection. I also rechecked the main R12 evidence to determine whether any first-order objection could have become obsolete through hidden changes. None has: there are no hidden changes.

---

## 2. Version-integrity finding: R13 has zero scientific delta

### R13-F0 — Blocking: the purported revision is only the prior referee report

The exact repository comparison is:

- R12 manuscript commit: `4ff0404833a6d6773bcf7afab361013d732df686`;
- purported R13 head: `442ef9be75e620b53f923cdc476be50edaa64ca7`;
- commits added: 1;
- files changed: 1;
- changed file: the R12 referee report;
- manuscript/source/result changes: 0.

The current R13 branch and the prior R12 review branch are byte-for-byte identical at the Git object level.

### Required

Before another referee round, the authors must produce an actual revision commit containing, at minimum:

1. a new canonical manuscript source and compiled paper;
2. a point-by-point response to the R12 report;
3. new or changed theorem/code/result objects corresponding to the claimed repairs;
4. an immutable source/result/build receipt identifying the exact review target; and
5. a revision index that points unambiguously to that new target.

Until this exists, any substantive “R13 review” would merely re-review R12 under a different branch name.

---

## 3. The central methodological mismatch remains unchanged

### R13-F1 — Blocking: the strongest certificate is still not a certified Neural Bellman policy

The R12 main text explicitly concedes that its economic calculation does not execute a whole-state neural critic certificate. The strongest economic result instead uses a feasible policy that is independently polished and then verified by a separate primal/dual stack.

A representative R12 actor record,
`revisions/2026-09-22-r12/results/cases/k4.25/actor_k4.25.json`, records:

- 16 deterministic time slabs;
- deterministic arrays for consumption and preference adjustment;
- portfolio control `p=0` on every slab;
- `algorithm: L-BFGS-B output polishing with exact differentiable budget projection`;
- `training_scope: finite time-control class; output polishing is not a claim of Adam convergence`.

The decisive lower bound is then obtained by exact stopped policy evaluation. The decisive upper bound is a model-specific affine-preference market-deflator dual.

That is a legitimate validated stochastic-control calculation. But the end-to-end theorem is not a theorem about the advertised neural Bellman training pipeline.

The current scientific chain is still:

neural/inherited candidate  
→ finite deterministic time-control polishing  
→ exact stopped policy evaluation  
→ model-specific dual upper bound  
→ central-state certificate  
→ affine cost-parameter envelope.

That chain can support a paper about validated stochastic-control certification. It does not yet support the stronger title-level claim that Neural Bellman Operators themselves are the verified numerical method.

### Required

Choose one coherent paper identity:

**A. Neural-method paper:** certify the stored neural actor/critic end to end over a nontrivial state region.

**B. Validated-control paper:** reframe the contribution around primal/dual certification and treat neural training as one optional candidate generator.

The present hybrid identity remains unacceptable.

---

## 4. The paper still does not certify a policy/value surface

### R13-F2 — Blocking: the flagship guarantee remains pointwise at one initial state

The R12 manuscript repeatedly states that the original-economy guarantee is at

`(t,u,x)=(0,2,1.25)`.

The continuum result is uniform in the scalar cost coefficient `k in [0.5,8]`, but not in the economically relevant state variables.

A numerical dynamic-programming method should normally establish the quality of a policy/value object over a state region, not only one scalar initial value. The current calculation does not show:

- verified performance from neighboring initial wealth/preferences;
- behavior near the first-exit boundary;
- a certified feedback map on a state set;
- a state-dependent error surface;
- or a computational route to policy-function accuracy.

### Required

Provide a nontrivial state-domain certificate, for example a verified cover with uniform regret, a certified value/policy enclosure on a rectangle, or an executed theorem showing how pointwise certificates propagate across initial states at controlled cost.

---

## 5. The neural bridge theorem remains unexecuted on the flagship problem

### R13-F3 — Blocking: the cover-and-oracle theorem is still an interface theorem

The R12 main text states a quantitative cover-and-oracle theorem for a neural witness and policy. It requires cellwise residual control, moduli, a global action oracle, neural derivative allowances, stopping-trace control, and assembly into a whole-policy regret bound.

The same text then explicitly says that the economic calculation instead fits an independent polynomial witness and does **not** claim to have certified a whole-state neural critic.

This is a serious gap between theorem architecture and executed method.

The paper has shown that the pieces can be written down. It has not shown that the pieces close numerically for the neural object that motivates the paper.

### Required

Execute the complete bridge on an actual stored neural policy/value pair on a nontrivial state-time domain. Report every error term and its contribution to the final regret bound.

---

## 6. Reproducibility is still being described as independence

### R13-F4 — Blocking: the “independent replay” uses the same certifier implementation

The R12 clean-checkout replay imports the production certifiers directly:

`original_policy_certificate as policy`

and

`flexible_dual as dual`.

It then recomputes the same quantities and checks agreement with stored values to approximately `1e-13`.

This is useful and should be retained. It verifies clean-checkout reproducibility and guards against file drift. It is not independent numerical verification: a shared implementation error is reproduced by construction.

This distinction matters because the final continuum tolerance is extremely tight.

### Required

Cross-check the decisive primal and dual bounds with genuinely independent numerical code, preferably using a different interval implementation and a materially different decomposition. A high-precision second implementation or formally checked core would also be acceptable.

---

## 7. The final tolerance remains too close to the acceptance boundary

### R13-F5 — Blocking: the continuum certificate clears 0.01 by only about 5.98e-6

The stored final uniform regret upper is

`0.009994024846927508`.

The nominal margin below the declared target is therefore only

`0.01 - 0.009994024846927508 = 5.975153072492e-6`.

The exact rational envelope arithmetic is not the main concern. The concern is the upstream enclosure stack that supplies each node: interval arithmetic, Gaussian moments, localization, supporting planes, stopping corrections, quadrature, clipping, witness fitting, and binary floating-point export.

A same-code replay cannot justify a top-journal claim when acceptance is determined by a six-micro-unit margin.

### Required

Either obtain a materially separated certificate—e.g. visibly below 0.009—or demonstrate robustness under higher precision, finer quadrature, enlarged primitive bounds, alternate interval arithmetic, and perturbed witnesses, together with an independent implementation.

---

## 8. The flagship problem still lacks a true accuracy-versus-computation frontier

### R13-F6 — Blocking: the reported “frontier” is a parameter-refinement frontier

The R12 `frontier.json` records 3, 4, 7, 13, 17, and 18 cost nodes, with the continuum envelope shrinking from about 0.02399 to 0.009994.

That is informative, but it is not a convergence frontier for the numerical method on the original dynamic program. It does not show that increasing policy richness, witness richness, grid/cover resolution, neural capacity, or verification work drives the original-economy regret from, say,

0.01 → 0.005 → 0.0025 → 0.001.

The paper therefore still demonstrates success against one chosen threshold rather than a controlled accuracy law.

### Required

For the unchanged original economy, report verified error against total computational work while systematically increasing the approximation/certificate resources that are supposed to converge.

---

## 9. End-to-end generation cost remains unmeasured

### R13-F7 — Major: the reported 325 seconds is not the cost of the method

The R12 frontier explicitly labels its timing as cumulative successful task-wall durations. It excludes inherited calculations and interrupted attempts and is not an end-to-end resource account.

The clean replay also starts from frozen policies and dual pilots; it does not regenerate the complete scientific object from scratch.

For a numerical-method paper, the relevant quantity is not merely the time needed to re-verify already selected proof objects.

### Required

Provide a clean end-to-end run that includes:

- neural training or other candidate generation;
- output polishing;
- witness/dual fitting;
- adaptive node selection;
- all failed/refined attempts;
- rigorous verification;
- CPU/GPU hardware and memory;
- wall-clock and processor time.

Separate proposal cost from certification cost, but report both.

---

## 10. The paper still lacks strong same-problem classical baselines

### R13-F8 — Blocking: no serious classical solver is compared on the flagship economy at matched accuracy

The external neural benchmark and the reference-solvable suites do not answer the most relevant question: how does the proposed end-to-end method compare with strong non-neural numerical methods on the same stopped preference-adjustment economy?

For an Econometrica-level numerical contribution, the paper needs same-problem evidence against credible classical alternatives: for example monotone HJB/PDE methods where feasible, adaptive sparse grids, controlled Markov-chain approximation, direct collocation, policy iteration with conventional bases, or another serious primal/dual method.

Without this, the paper cannot establish whether the neural machinery improves the accuracy/cost frontier or merely generates a candidate that a specialized verifier later certifies.

### Required

Add at least two strong classical baselines on the unchanged flagship problem and compare them at matched verified accuracy, not fixed nominal training time.

---

## 11. The high-dimensional action result is still not a high-dimensional control result

### R13-F9 — Major: 128-dimensional certification concerns a structured frozen-jet oracle

The 128-dimensional result is useful as a structured global action-optimization certificate. It is not an end-to-end solution of a 128-dimensional stochastic dynamic program.

At dimensions 8 and 16, actual learned gradients are audited at recorded states. At larger dimensions, the experiment uses independently generated frozen jets in the same structured Hamiltonian family.

This does not validate a 128-dimensional neural Bellman PDE, policy iteration sequence, state-space residual, or dynamic economic model.

### Required

Narrow the claim to what is actually computed: a structured high-dimensional action-oracle result. If the paper wishes to claim high-dimensional dynamic-control capability, solve and certify a corresponding complete dynamic problem.

---

## 12. The external comparison still does not establish numerical superiority

### R13-F10 — Blocking: the retained baseline evidence is unfavorable to a superiority narrative

The R12 paper correctly reports that the independently specified clipped quadratic-feedback baseline has lower mean cost than both learned methods in every retained panel. It also reports that dimension-16 seed-level comparisons do not establish a robust ordering.

These are valuable negative results and should remain.

They mean, however, that the paper cannot simultaneously use the external study as evidence that NBO is the superior numerical solver. At most it supports some pairwise differences relative to the pinned SOC-MartNet implementation under specific fixed budgets and protocols.

### Required

Separate three claims rigorously:

1. candidate-generation quality;
2. certification validity;
3. numerical efficiency versus alternatives.

Do not use certification success as evidence of solver superiority, or isolated solver comparisons as evidence for the certificate theorem.

---

## 13. The continuation theorem remains model-specialized

### R13-F11 — Major: the continuum result exploits affine dependence on the cost parameter

The R12 continuum theorem is mathematically useful because, for fixed policy,

`J_k(pi) = A(pi) - k B(pi)`.

This yields affine policy lines, convexity of the optimum as a supremum of affine functions, and an exact envelope calculation.

That construction does not by itself provide a general Neural Bellman continuation method for parameters that change dynamics, volatility, constraints, discounting, boundary conditions, or transition kernels.

### Required

State the scope narrowly—affine objective parameters with a common admissible policy set—or develop a genuinely broader continuation theorem with explicit moduli and executed numerical evidence.

---

## 14. Uniform policy regret does not automatically resolve comparative statics

### R13-F12 — Major: the 0.01 policy guarantee is not the same as uniformly sharp economic effects

The continuum policy library gives a uniform policy-regret bound. It does not imply that differences in optimal value across nearby cost parameters are themselves resolved to economically meaningful relative precision.

When the welfare difference of interest is of the same order as the combined value intervals, comparative-static conclusions can remain weak even though each policy is individually within 0.01 of its optimum.

### Required

Map the cost regions in which the certified value intervals determine the sign and magnitude of economically relevant differences. Distinguish “policy nearly optimal” from “comparative static sharply identified.”

---

## 15. The general theory remains too thin relative to the amount of specialized machinery

### R13-F13 — Major: the contribution is still an accumulation of partially separate components

The manuscript contains several distinct objects:

- a stopped preference-adjustment economy;
- primal/dual pointwise certification;
- an affine parameter envelope;
- a neural cover/oracle theorem not executed on the flagship problem;
- a structured nonconvex action oracle;
- external neural holdouts;
- independent reference-control problems;
- multiple historical preservation layers.

Each can be useful. Together they still do not form one clean end-to-end theorem-and-computation result at the level expected for a top general economics journal.

The manuscript would be stronger if it completed one methodological chain rather than continuing to add adjacent demonstrations.

### Required

Rebuild the main paper around one central theorem, one primary algorithm, one flagship end-to-end experiment, one matched benchmark set, and one reproducible accuracy/cost frontier. Move historical preservation to Git history and a compact reproducibility appendix.

---

## 16. Editorial and provenance issues

### R13-F14 — Major: the repository's canonical-version metadata is still internally confusing

`REVISION_INDEX.md` begins with the heading “canonical revision R10,” while later sections identify R11 and R12 as newer current revisions. Historical preservation explains how this happened, but it is not acceptable as the primary navigation mechanism for a live referee target.

The purported R13 branch then compounds the problem by using a revision name for a commit that contains no revision.

For an auditable numerical paper, version identity should be simpler than the numerical proof itself.

### Required

Create a single machine-readable and human-readable canonical manifest containing:

- current manuscript version;
- exact source commit;
- exact result commit;
- exact build commit;
- exact referee-response commit;
- superseded versions;
- and one unambiguous review entry point.

---

## 17. What remains genuinely strong

The negative recommendation should not obscure the substantive progress already present in R12.

I regard the following as valuable:

1. the original stopped economy now has nontrivial primal/dual central-state certificates rather than loose illustrative bounds;
2. the affine-cost envelope is an exact finite acceptance calculation rather than sampled interpolation;
3. negative holdout evidence is retained instead of suppressed;
4. the repository preserves failures and immutable identities better than earlier revisions;
5. the structured continuous-action oracle is a useful computational primitive;
6. the paper has become more explicit about the distinction between a posteriori verification and optimizer convergence.

Those strengths are precisely why the next revision should focus on closing the central method chain instead of adding another layer of scope.

---

## 18. Minimum conditions for another referee round

I would not recommend sending the paper back to an external referee until the repository contains an actual new manuscript revision satisfying the following P0 items.

### P0.1 — Actual revision identity

A new R13 (or later) manuscript, response, result package, and immutable receipt must exist at a new commit. A branch name alone is insufficient.

### P0.2 — Decide the scientific identity

Either certify a neural Bellman policy/value object end to end, or reframe as a validated stochastic-control certification framework.

### P0.3 — Whole-state executed certificate

Run the neural residual/jet/action/boundary machinery on a nontrivial state domain.

### P0.4 — Independent verification

Use a genuinely separate primal/dual implementation and obtain materially more slack than the current 5.98e-6 acceptance margin.

### P0.5 — Flagship accuracy/cost frontier

Demonstrate controlled tightening of verified error on the original economy and report full end-to-end resource cost.

### P0.6 — Serious same-problem baselines

Compare against strong classical numerical methods on the unchanged original problem at matched accuracy.

Only after those items are present would secondary issues—presentation, parameter generality, reference-suite architecture, high-dimensional extensions, and comparative-statical resolution—be worth another full round.

---

## 19. Recommendation

**Reject / return without a new substantive review round.**

This recommendation is stronger procedurally than the R12 recommendation for a simple reason: the branch presented as R13 is not a new scientific revision. It is the R12 manuscript plus the R12 referee report.

Scientifically, nothing has changed since the last report. The strongest positive result remains a carefully constructed pointwise validated-control certificate. The principal unresolved question remains whether the advertised Neural Bellman methodology itself can be made into an end-to-end, state-space, independently verified numerical method with a controlled accuracy/computation frontier and competitive same-problem benchmarks.

A new branch name does not answer that question.

---

## 20. Evidence reviewed

### Repository identity

- repository: `TrillionniumFoundation/NBO`;
- R12 manuscript commit: `4ff0404833a6d6773bcf7afab361013d732df686`;
- R12 review commit / purported R13 head: `442ef9be75e620b53f923cdc476be50edaa64ca7`;
- branch comparison R12→R13: one commit, one file, referee report only;
- branch comparison R12-review→R13: identical.

### Main paper state

- `ECTA_R12.tex`;
- `SUPP_R12.tex`;
- `R12_REVIEW.md`;
- `REVISION_INDEX.md`;
- `revisions/2026-09-22-r12/paper/main.tex`;
- `revisions/2026-09-22-r12/paper/continuation.tex`;
- `revisions/2026-09-22-r12/paper/continuation_proof.tex`.

### Numerical evidence

- `revisions/2026-09-22-r12/results/envelope.json`;
- `revisions/2026-09-22-r12/results/frontier.json`;
- `revisions/2026-09-22-r12/results/refinement_history.json`;
- `revisions/2026-09-22-r12/results/cases/k4.25/actor_k4.25.json`.

### Replication and referee history

- `revisions/2026-09-22-r12/replication/recheck.py`;
- `revisions/2026-09-22-r12/response_to_referee.md`;
- `reviews/2026-09-22-econometrica-r12/referee_report.md`.

