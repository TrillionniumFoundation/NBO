# External Referee Report — Neural Bellman Operators (R27)

**Venue standard:** Econometrica-level numerical / computational methodology  
**Recommendation:** **Reject / return as incomplete in the present form. The R27 branch is not a materialized paper revision, and the scientific additions that are described remain protocol-level or post-diagnostic rather than reviewable executed evidence.**  
**Review date:** 2026-09-24  
**Reviewed repository:** TrillionniumFoundation/NBO  
**Reviewed revision branch:** revision/econometrica-r27-constrained-bellman-2026-09-23  
**Reviewed head:** dde239ee518d9f6d5945aebc8743b50de4d1b62b  
**Last complete manuscript inherited on this branch:** R26 at ec845cb2f350bf902d10d789cde17fb69b841ffa  
**Review branch:** review/econometrica-r27-numerical-methods-2026-09-24-dde239e

I reviewed the exact R27 tree, the six-commit difference from the complete R26 manuscript head, the R27 execution protocol, the frozen unknown-solution Bellman design, the post-diagnostic Bellman-completion amendment, the R27 GitHub Actions workflow, the inherited R26 article/supplement/response object, and the immediately preceding R26 numerical-methods referee report.

The first and most important finding is repository-level rather than econometric: **R27 is not presently a paper revision.** The directory `revisions/2026-09-23-r27/` contains exactly three Markdown files:

- `PROTOCOL.md`;
- `UNKNOWN_BELLMAN_DESIGN.md`;
- `BELLMAN_COMPLETION_AMENDMENT.md`.

There is no `ECTA_R27.tex`, `SUPP_R27.tex`, `RESPONSE_R27.tex`, corresponding PDFs, R27 replication directory, R27 results directory, R27 test suite, or R27 reproduction record at the reviewed head. The root `REVISION_INDEX.md` still identifies **R26** as the current review object. The R27 workflow itself expects files that do not exist at the reviewed head.

Accordingly, I cannot honestly treat design prose as if it were an executed Econometrica revision. I nevertheless evaluate the scientific content of the R27 design because it reveals what the next manuscript is intended to claim and because several of those claims, even if executed exactly as described, would still need much sharper attribution.

---

## 1. Executive assessment

R27 is pointed in a more productive direction than R26. In particular, the protocol directly targets several major objections from the preceding review:

1. it proposes a constrained, projected-stationarity extension rather than excluding boundary points;
2. it proposes an unknown-solution stochastic Bellman benchmark instead of another manufactured known-solution verifier example;
3. it proposes a faithful historical-transport control with recentering and explicit nonlinear-remainder accounting;
4. it proposes a production-schedule rollback comparison instead of a deliberately extreme stress injection;
5. it acknowledges that the exact tabular dynamic-programming baseline can be faster;
6. it promises full cost accounting, retained failures, and explicit separation of the finite-state auxiliary economy from the original continuous-time target.

Those are good design choices.

But the current branch does not contain the evidence needed to support any of them. Worse, the post-diagnostic Bellman-completion amendment changes the interpretation of the proposed finite-state success in a way that must be handled very carefully. The completion operator is representation-independent, enumerates feasible actions using the exact model, evaluates the completed suffix policy exactly, and applies exact greedy corrections whenever a local Bellman deficit exceeds a prescribed threshold. This is a legitimate generic certification / repair operator. It is **not** evidence that a neural Bellman solver has learned the difficult policy.

The branch itself already concedes the decisive raw result: in four dimensions the raw neural fitted Bellman policy has worst regret of about **0.3665**, while exact tabular dynamic programming is faster. Against a 0.01 benchmark tolerance, that raw neural result misses by roughly 36.6 times. The proposed completion can then force a small residual certificate by exact model-based corrective sweeps. If that succeeds, the result belongs principally to the completion procedure, not to the neural approximator.

The original continuous-time objective is also unchanged. The inherited complete manuscript still reports a whole-domain bound of **7.181834580823298** against the declared **0.01** target, approximately a 718-fold gap.

Therefore R27, as currently committed, does not change the publication-level conclusion.

---

## 2. Repository and submission-object audit

### R27-F1 — There is no reviewable R27 manuscript

The current R27 head contains no R27 article, supplement, response, PDFs, results, or replication code.

The six commits ahead of the R26 science head add only:

- the prior R26 referee report and manifest;
- the R27 workflow;
- the R27 execution protocol;
- the frozen unknown-solution benchmark design;
- the Bellman-completion amendment.

This is a work branch, not a completed revision object.

For an auditable computational paper, submission identity is part of the scientific record. A referee cannot infer a manuscript from an intended workflow.

**Required correction:** materialize a single review-ready R27 object with article, supplement, response, all referenced tables/figures, code, frozen results, tests, PDFs, and a revision manifest pinned to one exact commit.

### R27-F2 — The branch says the raw Bellman experiment was executed, but the evidence is absent

`BELLMAN_COMPLETION_AMENDMENT.md` states that the raw unknown-solution inventory experiment “has now been executed,” that policies and results are retained, that several small neural instances attain the exact optimal policy, and that the four-dimensional worst regret is about 0.3665.

None of the corresponding policy tables, hashes, raw result files, scripts, timings, logs, exact-rational witnesses, or test records is present in the R27 directory at the reviewed head.

This is not a minor packaging issue. The whole point of the R27 design is to prevent outcome-dependent reinterpretation by freezing candidates before reference evaluation. Without the frozen artifacts, the referee cannot verify that freeze chronology.

**Required correction:** commit the raw candidate policies, SHA-256 manifests, model specification, training logs, exact-reference generation record, independent evaluation output, and immutable candidate hashes.

### R27-F3 — The committed R27 CI workflow is aspirational rather than validating the reviewed head

The workflow `.github/workflows/r27-revision.yml` attempts to run

`python revisions/2026-09-23-r27/replication/test_revision.py`

and compile

`ECTA_R27.tex`, `SUPP_R27.tex`, and `RESPONSE_R27.tex`.

Those files do not exist at the reviewed head.

Moreover, the validation job is gated by a commit-message condition requiring `[validate-r27]`. The reviewed HEAD message does not contain that token. On a manual workflow dispatch, the push-specific `head_commit.message` field is not a reliable basis for enabling the job.

Thus the presence of a workflow file must not be described as validation of R27.

**Required correction:** make the validation path executable from a clean checkout, run it on the final referee commit, retain the workflow run and artifact identifiers, and record the exact checked commit.

---

## 3. Scientific blocking findings

### R27-F4 — Bellman completion is a generic exact-model repair operator, not a neural result

The amendment proposes a representation-independent completion operator. For each frozen candidate policy it:

1. reads the frozen action table;
2. sweeps backward over the finite-horizon model;
3. evaluates every feasible action against the already completed suffix policy;
4. retains the proposed action only if its exact local Bellman deficit is sufficiently small;
5. otherwise replaces it with an exact greedy action;
6. computes an exact residual envelope.

This is a sound and useful construction.

It is also largely independent of whether the initial candidate came from a neural network, a polynomial fit, a myopic rule, or an arbitrary table.

Therefore any post-completion 0.01 certificate must not be attributed to “Neural Bellman Operators” unless the paper separately quantifies how much the neural candidate reduced the repair burden compared with generic baselines.

At minimum, the completed frontier should include:

- raw neural policies;
- raw polynomial policies;
- myopic policies;
- random feasible policies;
- simple tabular approximate policies;
- all of the above after the **same** completion operator.

Report the fraction of states changed, local deficits before repair, exact work, memory, and total end-to-end cost. If a crude initial policy is repaired almost as cheaply as the neural one, then the neural fitting stage is not carrying the numerical contribution.

### R27-F5 — The post-diagnostic completion experiment is exploratory, not confirmatory

The branch is commendably explicit that the completion amendment was written **after** observing the raw experiment and the four-dimensional regret around 0.3665.

That disclosure is correct scientific practice.

But it has a consequence: the completion result cannot be presented as if it were part of the prospectively frozen R27 efficacy test. It is an exploratory response to a disappointing raw result.

A strong revision should preserve two separate records:

- **prospective frozen experiment:** the raw benchmark defined before training;
- **post-diagnostic extension:** the completion operator and all results obtained after seeing the raw outcome.

The paper should not merge these into one undifferentiated “R27 success.”

### R27-F6 — The unknown-solution benchmark is genuine, but far too small to motivate neural approximation

The benchmark uses inventory states with (L=4) and dimensions (d=2,3,4). That corresponds to only:

- 16 states for (d=2);
- 64 states for (d=3);
- 256 states for (d=4),

per time slice, with horizon 8. The resolution control (d=4,L=5) has only 625 states.

These are useful unit tests for an unknown-solution Bellman pipeline. They are not high-dimensional control problems.

The design itself says exact tabular dynamic programming is the strongest baseline, and the amendment says it is faster. That is not surprising at these state counts.

The benchmark therefore can establish:

- information symmetry;
- candidate freezing;
- exact policy evaluation;
- Bellman-residual certification;
- pipeline correctness.

It cannot establish a computational reason to use neural approximation.

### R27-F7 — The proposed whole-state residual certificate sacrifices the scalability that is supposed to motivate neural methods

The completion/certification procedure evaluates the finite graph state by state and feasible action by feasible action with exact arithmetic.

That is appropriate for a small reference problem. But then the certification complexity is essentially tabular in the state-action graph. The paper must not use this result as evidence that neural approximation has solved the curse of dimensionality.

The correct interpretation is:

> a neural or polynomial candidate can be compiled into a finite policy table and then audited / repaired by an exact finite-state procedure on small models.

That is valuable, but much narrower than a scalable Neural Bellman Operator.

### R27-F8 — The raw four-dimensional neural result is materially unsuccessful at the stated 0.01 tolerance

The amendment reports worst regret of about 0.3665 in four dimensions.

That is not a near miss. It is roughly 36.6 times the 0.01 target.

If post-completion regret falls below 0.01, the manuscript must show, separately:

- raw regret;
- completed regret;
- number and fraction of corrected actions;
- maximum and distribution of local deficits;
- cost of completion;
- cost of exact residual verification;
- cost of the exact tabular benchmark;
- neural fitting cost;
- total standalone pipeline cost.

Otherwise a reader may incorrectly attribute exact-repair performance to the raw neural solver.

### R27-F9 — The projected-stationarity extension is only a promise at this head

The R27 protocol says that fixed-scale interval-certified coordinate polling will be extended to a closed box using a projected-gradient mapping.

That is the right conceptual fix for the boundary defect identified in R26.

But there is no R27 theorem, proof, implementation, numerical instantiation, or test on the reviewed head.

Therefore the prior constrained-stationarity objection remains open.

A paper-level result needs a precise stationarity measure, a finite-work theorem, oracle-failure semantics, boundary handling, and an executed instance.

### R27-F10 — The proposed original-economy scalar slice is not the original 47-dimensional problem

The protocol fixes (c=3/4), (p=0), a scalar (	hetain[-1/5,1/5]), one initial state, and two preference-cost values.

This could be a useful economically meaningful diagnostic.

It is not:

- the 47-dimensional financed class;
- a whole-domain actor;
- all start states and times;
- the original uniform 0.01 target.

The protocol correctly says not to substitute it for those objects. The eventual manuscript must maintain that distinction just as explicitly.

### R27-F11 — The stopped-gradient / derivative bridge is still not available

The protocol proposes Girsanov-based payoff derivative bounds, an independent bound on preference-exit probability, and validated numerical integration.

Those are exactly the kinds of ingredients that could make the reduced problem informative.

But no derivation or numerical constants are committed in R27.

The central question remains whether differentiable proposal directions can be related quantitatively to the exact stopped economic objective. Finite differences, secants, and local slices are not substitutes for that bridge.

### R27-F12 — The historical-transport mechanism isolation remains unexecuted

R27 specifies a materially better mechanism experiment than R26:

- separately implemented quotient-gradient pullback;
- parameter-moment transport;
- recentering on the full nonlinear carrier output after every update;
- explicit nonlinear remainder;
- no unmatched output cap;
- recorded mismatch and timings.

This is a good protocol.

But there is no implementation or output at the reviewed head. Hence the prior mechanism-isolation objection remains unresolved.

### R27-F13 — The production rollback comparison remains unexecuted

The protocol improves on the R26 fault-injection study by proposing:

- prospectively fixed rates;
- coupled gated and ungated trajectories;
- identical block structure;
- identical L-BFGS-B restart rules;
- full checkpoint intervals;
- total cost and memory accounting.

Again, this is the right experiment.

Again, no results are committed.

The paper therefore still does not show whether certification-coupled rollback improves a production solver rather than merely restoring state correctly after a bad proposal.

### R27-F14 — The original continuous-time target remains missed by about 718×

Because there is no R27 manuscript or new original-economy result, the operative complete paper is still R26.

Its current-state whole-domain bound remains

[
7.181834580823298,
]

against a declared target of

[
0.01.
]

The gap is approximately 718-fold.

Nothing in the R27 protocol or finite-state completion amendment closes that original target.

### R27-F15 — The root review lineage is stale on the R27 branch

At the reviewed R27 head, the root `REVISION_INDEX.md` still says:

- “Current review object: R26”;
- “Latest report addressed” is the older R24 report.

Yet the R27 protocol explicitly starts from the R26 review and the repository contains the R25 second-pass and R26 reports.

For a paper whose strongest virtue is auditability, this must be repaired before a referee copy is declared final.

### R27-F16 — The literature and novelty problem is still open

The R27 material contains no new literature positioning.

The completion theorem is a finite-horizon Bellman-residual / greedy-repair argument. The protocol itself correctly says not to claim invention of policy iteration or dynamic programming.

Likewise, projected direct search, validated numerics, fitted value iteration, residual bounds, and policy repair all have substantial literatures.

A new manuscript needs a serious primary-source comparison that identifies exactly what is novel:

- theorem;
- oracle construction;
- certification architecture;
- coupling rule;
- transport mechanism;
- or economic application.

Without that, the paper risks combining known ingredients into a very elaborate audit pipeline without isolating a publishable methodological novelty.

### R27-F17 — Two neural seeds are not enough to establish robustness of a parameterization-sensitive method

The frozen benchmark design uses two neural seeds for each architecture.

That is acceptable for a deterministic diagnostic table, but not enough to characterize a method whose prior record shows strong sensitivity to:

- initialization;
- architecture;
- parameter chart;
- optimizer;
- learning rate;
- output scaling;
- verification tolerance.

The final paper should report a structured robustness map rather than relying on two seeds.

### R27-F18 — A completed finite-state policy is not a neural deployment certificate

The design correctly states that a compiled finite-state policy table is the certified deployment object, not floating-point neural execution.

That qualification is essential.

If the final claimed policy is a repaired action table, then the numerical contribution should be described as a certified finite-state policy pipeline whose **proposal** may be neural, not as a certified neural policy execution.

---

## 4. Technical comments on the proposed Bellman completion

### R27-T1 — State the residual identity and performance-loss bound precisely

The manuscript should define the completed-policy value (V_t^pi) and local residual/deficit, for example

[
delta_t(s)
=
max_{ain A(s)}
left{
r_t(s,a)+eta P_{t,s,a}V_{t+1}^{pi}
ight}
-
V_t^pi(s).
]

Then prove the statewise recursion that bounds (V_t^*-V_t^pi).

Stopping/default states, terminal payoff, feasibility, and time dependence must appear explicitly.

### R27-T2 — Explain exactly what information the completion operator uses

The amendment says it does not read (V^*). Good.

But it does use:

- the full transition law;
- exact rewards;
- exact suffix-policy values;
- all feasible actions;
- exact arithmetic.

That is a powerful model oracle. The paper should compare its information and work requirements with the tabular dynamic-programming baseline, not merely emphasize that (V^*) was not read.

### R27-T3 — Add trivial-policy controls for the completion stage

The decisive diagnostic is not whether neural and polynomial candidates can be repaired.

It is whether their pre-repair quality materially lowers the cost or number of changes relative to trivial policies.

Run the identical completion on:

- random feasible tables;
- myopic one-step greedy policies;
- simple base-stock / inventory heuristics where appropriate.

### R27-T4 — Report action-change topology, not only percentages

A 1% changed-action fraction can be benign or catastrophic depending on where those states lie.

Report changes by:

- time;
- inventory region;
- default boundary proximity;
- restart time;
- local residual magnitude.

### R27-T5 — Exact arithmetic costs must be charged honestly

Rational backward evaluation can experience numerator/denominator growth.

Report:

- arithmetic backend;
- exact-operation counts if practical;
- wall time;
- CPU time;
- peak memory;
- bit-length growth.

Do not compare uncharged exact-reference work with floating-point fitting time.

### R27-T6 — The fixed (eta) rule should be justified against remaining horizon

The global choice

[
eta
=
arepsilon /
sum_{j=0}^{T-1}eta^j
]

is transparent and conservative.

The supplement should explain whether state/time-dependent thresholds could reduce unnecessary corrections, and why the fixed rule was chosen for the frozen experiment.

### R27-T7 — Separate “candidate generation,” “completion,” and “certification”

These are distinct numerical stages.

A table should report each stage independently and in total.

### R27-T8 — Verify no reference leakage programmatically

Because the central benchmark claim depends on the exact reference being created only after candidates are frozen, add an automated provenance check that records:

- candidate hashes;
- candidate commit;
- reference-generation commit or event;
- exact input paths;
- absence of reference reads during candidate generation.

### R27-T9 — The strongest classical baseline must remain visible

If exact tabular dynamic programming is faster and exact, it belongs in the main table, not only the supplement.

### R27-T10 — Do not equate a finite-state certificate with continuous-domain interval verification

The finite graph removes the continuous-domain covering problem.

The final paper should keep these complexity regimes separate.

---

## 5. What is genuinely improved in the R27 design

Although the present branch is not review-ready, several design decisions are worth preserving.

### Substantive improvements

- **Unknown-solution benchmark:** exact optimal actions are withheld from candidate generation.
- **Frozen information protocol:** candidate policies are intended to be hashed before the reference solve.
- **Constrained optimization theory:** the protocol explicitly targets projected stationarity.
- **Mechanism isolation:** the proposed historical-transport comparison corrects the major R26 confounds.
- **Production rollback test:** the design moves away from fault injection toward paired gated/ungated runs.
- **Negative-result disclosure:** the branch explicitly records that raw four-dimensional neural regret is about 0.3665 and tabular DP is faster.
- **Post-diagnostic labeling:** the completion amendment admits that it was created after observing the raw result.
- **No substitution claim:** the discrete benchmark and scalar original-economy slice are explicitly not substitutes for the original continuous-time whole-domain objective.

These choices make a future R27 potentially much more informative than R26.

They are not yet results.

---

## 6. Requirements for a materially reviewable next snapshot

### N1 — Materialize the actual R27 referee copy

Commit:

- `ECTA_R27.tex/pdf`;
- `SUPP_R27.tex/pdf`;
- `RESPONSE_R27.tex/pdf`;
- complete R27 scientific source;
- replication code;
- results;
- tests;
- manifests;
- reproduction instructions.

### N2 — Preserve the raw Bellman experiment exactly

The raw experiment must remain immutable and separately reportable after the post-diagnostic completion extension.

### N3 — Add a full R26 disposition matrix

Address every R26 blocking finding, technical comment, and requested action individually, and retain the R25 second-pass crosswalk where still relevant.

### N4 — Make the completion contribution attribution-proof

Report raw versus completed performance and include trivial-policy completion controls.

### N5 — Prove the completion theorem cleanly

State assumptions, stopping semantics, exact residual definition, and the whole-state/restart bound.

### N6 — Instantiate constrained stationarity

A theorem alone is insufficient. Execute it on at least one meaningful original-economy problem and report oracle work.

### N7 — Execute the historical-transport isolation experiment

Commit full parameter/moment trajectories, nonlinear remainder, quotient mismatch, cap activity, output steps, and timings.

### N8 — Execute the paired production rollback experiment

Compare gated versus ungated variants and include the strongest classical solver under the same verification gate.

### N9 — Give a complete standalone cost ledger

Include fitting, model construction, policy compilation, exact reference, certification, completion, verification, rollback, memory, and amortized versus non-amortized totals.

### N10 — Add real scaling evidence

The 16/64/256-state benchmark is too small. Increase state-space size and report where tabular reference, completion, neural fitting, and certification each become limiting.

### N11 — Expand the literature review

Position every claimed methodological contribution against primary literature in derivative-free constrained optimization, approximate dynamic programming, fitted value iteration, Bellman-residual error bounds, verified numerics, neural stochastic control, and computational economics.

### N12 — Fix repository lineage

The final R27 branch should identify R27 as the current review object and correctly name the latest addressed reports.

### N13 — Run CI on the exact referee head

The final reportable snapshot should have a reproducible successful validation run tied to the exact commit under review.

---

## 7. Recommendation

**Reject / return as incomplete in the present form.**

This is not primarily because the R27 ideas are poor. Several are materially better targeted than the R26 additions.

The problem is more basic: **the current R27 branch is not a paper revision.**

At the reviewed head:

- there is no R27 article;
- there is no R27 supplement;
- there is no R27 response;
- there are no R27 result files;
- there is no R27 replication directory;
- there is no R27 test suite;
- the workflow points to nonexistent files;
- the root index still identifies R26 as the review object.

Scientifically, the most important new disclosed fact is also unfavorable to a Neural Bellman Operator claim: the raw four-dimensional neural fitted Bellman policy has worst regret around 0.3665 while exact tabular dynamic programming is faster. The proposed completion operator can be useful, but because it is representation-independent and performs exact model-based greedy repair, any successful completed certificate must be attributed to that generic repair stage unless the authors demonstrate a material neural-specific reduction in correction work.

The original continuous-time target also remains untouched at the reviewable manuscript level: 7.181834580823298 versus 0.01.

R27 could become a strong audit of where neural proposal mechanisms do and do not help inside a certified dynamic-programming pipeline. It is not yet that paper. The next review should occur only after the protocol has been converted into one exact, complete, reproducible referee snapshot.

---

## 8. Source map inspected

### Exact R27 review target

- branch: `revision/econometrica-r27-constrained-bellman-2026-09-23`
- head: `dde239ee518d9f6d5945aebc8743b50de4d1b62b`

### R27 files

- `revisions/2026-09-23-r27/PROTOCOL.md`
- `revisions/2026-09-23-r27/UNKNOWN_BELLMAN_DESIGN.md`
- `revisions/2026-09-23-r27/BELLMAN_COMPLETION_AMENDMENT.md`
- `.github/workflows/r27-revision.yml`

### Inherited complete manuscript

- `ECTA_R26.tex/pdf`
- `SUPP_R26.tex/pdf`
- `RESPONSE_R26.tex/pdf`
- `R26_REVIEW.md`
- `REVISION_INDEX.md`
- `revisions/2026-09-23-r26/`

### Prior referee context

- `reviews/2026-09-23-econometrica-r26/referee_report.md`
- `reviews/2026-09-23-econometrica-r26/review_manifest.json`
- earlier R25 second-pass numerical-methods review referenced by R26

### Branch-difference check

R26 science head `ec845cb2f350bf902d10d789cde17fb69b841ffa` to R27 head is six commits ahead and changes only the prior-review records, one workflow file, and the three R27 Markdown design/protocol files listed above. No R27 manuscript or result object is present.
