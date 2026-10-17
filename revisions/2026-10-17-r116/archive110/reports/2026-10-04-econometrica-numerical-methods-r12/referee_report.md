# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r12-development-2026-10-04`  
**Pinned revision commit:** `39344d49e11cca02d1ddd8d63207b186c7668f8b`  
**Pinned revision tree:** `578b882b2e60440b1e708608afc0b0e05629fcec`  
**Pinned root manuscript blob:** `2b2a36d07e368f92c29868ff7afcf98ad8f24d89` (`ECTA.tex`)  
**Report date:** 4 October 2026  
**Recommendation:** **Reject in the present form. The current object is an incomplete development snapshot rather than a completed revision, and the remaining contribution questions call for a substantially focused new submission rather than another ordinary revision of this cumulative manuscript.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R12 is a thoughtful response to the R11 report at the level of research design. It directly targets the previous objections. The source introduces:

1. a direct common-path comparison of NBO with direct policy optimization and affine policies, instead of subtracting separate schedule-relative lower bounds;
2. a finite initial-state population rather than relying only on the favorable origin;
3. a costate-error-to-Hamiltonian-loss inequality intended to isolate what the Bellman evaluation block contributes;
4. an observation theorem implementing the innovation-driven controller from continuous state histories plus private randomization;
5. a one-dimensional nonlinear monotone HJB reference;
6. equal announced fitting-time budgets, checkpoint frontiers, critic and radius ablations, state stresses, and a self-financed management-fee calculation; and
7. a proposed clean workflow that would execute all ten seeds in dimensions 10, 20, and 50 and then atomically publish evidence and referee branches.

These are sensible responses. The new mathematical statements are materially clearer than the claims criticized in earlier rounds. I found no immediate algebraic contradiction in the costate inequality, the conditional-projection identity, the direct paired construction, or the observation-space Brownian reconstruction under the exact assumptions stated.

The decisive problem is that the revision under review has **not executed or materialized the study on which its new claims depend**.

At the pinned snapshot:

- the only R12 branch is the `development` branch;
- the workflow intended to create `revision/econometrica-nbo-r12-evidence-2026-10-04` and `revision/econometrica-nbo-r12-referee-2026-10-04` has not run, because its trigger branch does not exist;
- `revisions/2026-10-04-r12/results/` is absent;
- the generated R12 tables, results summary, full-results supplement input, audit, remote-execution ledger, table manifest, and compiled final documents are absent;
- the root `ECTA.tex` and `supp.tex` remain the R11 roots until an unexecuted integration script rewrites them;
- the most complete available artifact explicitly labels itself a **development smoke** with one seed, dimension 10, 32 evaluation paths, three primary fits, and inconclusive intervals; and
- the current complete manuscript check is red. The R12 unit tests pass, but an inherited preservation test fails because the root `README.md` no longer has the archived hash, and the development build is deliberately failed by unresolved overfull material.

Consequently, the response document describes “executed evidence” that is not present in the reviewed tree. The numerical assertions that would decide whether R12 answers the R11 report—especially NBO versus direct policy optimization—cannot be refereed from this snapshot.

A protocol, a theorem, and a workflow are not substitutes for results. The current branch is a promising preregistered-style design plus development diagnostics, not a completed paper revision.

Even setting this threshold issue aside, the intended design leaves substantive concerns. The main theorem remains conditional and method-agnostic; the proposed 20-second wall-clock comparison is not a matched-accuracy numerical benchmark; the observed-history implementation assumes continuous noiseless observation, known coefficients, an exact drift integral, and private Brownian randomization; the scalar reference cannot validate high-dimensional near-optimality; and the economic application remains highly stylized relative to the size and breadth of the manuscript.

I therefore cannot recommend publication or another ordinary revision of this submission. A future, sharply focused paper could be worth evaluating after it supplies a single immutable source-and-evidence snapshot, passes its own preservation and compilation gates, reports all final paired outcomes, and demonstrates a method-specific contribution at matched economic accuracy and total work.

## 2. What R12 successfully improves at the design level

The negative recommendation should not obscure genuine progress.

### 2.1 Direct method differences are now the estimand

R11 correctly objected that two positive lower endpoints relative to a schedule do not identify the sign of the NBO-minus-direct-policy difference. R12 proposes to form that difference path by path on the same initial profiles and innovations and to apply the finite-family empirical Bernstein calculation directly to it. The shared schedule trajectory is checked and cancelled. This is the right inferential object.

The source also distinguishes three statements that had previously been too easy to conflate:

- a fitted policy improves on the analytical schedule;
- NBO improves on direct policy optimization; and
- either policy is close to the unknown optimum.

These are different questions, and R12 now says so.

### 2.2 The critic mechanism is formulated as a testable conditional claim

The costate proposition is useful. Strong concavity of the consumption Hamiltonian gives a quadratic action-loss account involving critic costate error and actor suboptimality. The accompanying conditional-projection identity separates irreducible rollout-costate variation from regression error.

Importantly, the manuscript acknowledges that these identities do not prove that the fitted critic reduces mean-square error, do not identify an Euler-rollout costate with the continuous-time costate, and do not prove optimizer convergence. The proposed raw-costate, value-only, costate-only, update-count, width, and direct-policy ablations are appropriate tests of the mechanism.

### 2.3 Initial-state heterogeneity is brought into the primary design

The proposed nine-profile population varies aggregate log capital and cross-sectional dispersion. The theorem is correctly described as integrated over that finite population, not uniform over all states and not calibrated to an empirical population. Severe stresses remain separate and are not supposed to inherit the population guarantee.

This is a substantial conceptual improvement over a single favorable initial condition.

### 2.4 The information structure is made explicit

The observation proposition no longer treats latent Brownian innovations as if they were automatically observed. Under continuous noiseless observation of the full capital path, known coefficients and actions, an exact drift integral, and an independent scalar Brownian randomizer, the construction completes the rank-deficient right-inverse innovation with a null-space component. The source correctly describes the result as distributional rather than pathwise recovery of the original latent null driver.

The assumptions are strong, but they are now visible.

### 2.5 The scalar reference is independent of the neural critic

The one-state calculation uses a monotone implicit discretization, full-box maximization, and fixed-policy solves. It is not a Riccati identity and does not use the NBO critic as its own benchmark. As a diagnostic of one nonlinear member of the model family, this is a useful addition.

### 2.6 Development failures are retained

The repository records development failures, uses a separate development-noise seed, and labels the available run as smoke evidence. This is good scientific practice.

## 3. Blocking concerns

### B1. The submitted snapshot is not a completed revision

This is the threshold issue.

The R12 protocol announces ten seeds, three dimensions, three primary methods, 8,192 final paths, 1,024 time cells, two primary initial-state designs, method contrasts, auxiliary ablations, fresh-radius fits, state stresses, and a scalar reference. None of the final aggregate evidence is present in the pinned tree.

The manuscript source refers to generated files including:

- `table_primary.tex`;
- `results_summary.tex`;
- `table_paired.tex`;
- `table_cost.tex`;
- `table_stress.tex`;
- `table_fee.tex`;
- `table_reference.tex`; and
- `full_results.tex`.

Those files are absent. So are `results/AUDIT.json`, `REMOTE_EXECUTION.json`, `TABLE_MANIFEST.json`, final seed-level weights and raw arrays, the final compiled R12 manuscript, supplement, and response, and the evidence and referee branches that the clean workflow is designed to publish.

The root paper in the branch is not the integrated R12 article. It still imports the R11 policy-specific, learning, and study files. `integrate.py` is intended to rewrite those roots after the numerical evidence is generated. That step has not produced a committed final source.

A referee cannot validate final numerical claims from placeholders and workflow intentions. The submission must first exist as one immutable, internally coherent source-and-evidence snapshot.

### B2. The current publication gate is red

The current head has a successful diagnostic inspection job and a failed complete manuscript check.

The R12-specific test suite reports 19 passing tests. The inherited replay then fails `test_12_historical_inputs_are_unchanged`: the present root `README.md` hash is `53563a181caa72a3f1541807a64b22d2f8522447660c534bccf1ea8f1a352dda`, while the archived R8 manifest expects `62959439bf18f80c2cb2d1e0da4ff82c73d4a645249658eef5a6a37a54bce03b`.

The development build also fails the repository’s own publication criterion. The generated 42-page main article has overfull boxes of 13.16042 pt and 3.44923 pt, and the five-page response has an overfull box of 1.36119 pt. The 118-page supplement has no reported overfull box in that run. `build.py` then raises an error because unresolved overfull material is defined as a failure.

The problem is not the aesthetic importance of one box. It is that the revision repeatedly describes a clean single-source publication gate while the gate has not passed. An external report should not promote a development artifact past the repository’s own acceptance conditions.

### B3. The central empirical question remains unanswered

R11’s central numerical objection was not that a paired comparison could not be designed. It was that NBO’s small apparent advantage over direct policy optimization was not certified.

R12 supplies the right design, but not the final data.

The only available development smoke has one training stream, dimension 10 only, 32 final paths rather than 8,192, roughly 0.35-second fits rather than the declared 20-second final budget, three primary fitted policies, and four direct paired comparisons.

Its population NBO-minus-DPO mean paired statistic is approximately `0.0001956`, but the smoke interval is approximately `[-0.19095, 0.19134]`. The origin contrast is also wholly inconclusive. The smoke response itself correctly states that zero of one population NBO policies has a positive lower endpoint and zero of one NBO-minus-DPO comparison is signed.

These development numbers do not argue against NBO. They show why the final study is indispensable. Until the final ten-seed evidence exists, there is no empirical basis for the revised manuscript’s method-comparison contribution.

### B4. Equal wall time is not a sufficient primary benchmark for a numerical method

The proposed primary comparison assigns each method an announced 20-second fitting budget on the same worker, permits the current iteration to finish, and records overshoot. This is transparent, but it does not by itself create a scientifically stable comparison.

Wall-clock training depends on CPU model and load, low-level linear algebra, compilation and warm-up, Python and PyTorch scheduling, validation frequency, checkpoint serialization, batch shapes, method-specific iteration granularity, and the amount of simulator work performed in an overshooting final iteration.

R12 records visits, updates, memory, and checkpoints, which is useful. Still, the main numerical comparison should be organized around economic accuracy and total work, not one hardware-specific stopping time. At minimum, the paper needs fixed-iteration and fixed-simulator-visit replays, accuracy-versus-work frontiers using the full verification calculation, a second environment or convincing invariance analysis, a matched endpoint criterion, and a clear separation between candidate-generation cost and certification cost.

A method that is slightly better after twenty seconds but requires much more expensive verification, or loses at equal certified accuracy, has not established a numerical advantage.

### B5. The costate theorem does not establish the value of the learned critic

The new action-loss inequality is conditional on the critic’s costate error relative to the relevant policy costate and the actor’s approximate solution of the critic-defined improvement problem.

The conditional-projection identity says that conditional expectation is the best square-integrable predictor of a rollout target. It does not show that the fitted network approximates that conditional expectation well, that the rollout target has small continuous-time bias, or that reducing target MSE improves the final deployed policy at the relevant states.

Thus the theorem is a mechanism lemma, not a method theorem. Its numerical value depends entirely on the missing ablation evidence.

A publishable method claim would require the final record to demonstrate, across dimensions and seeds, that learned costates improve held-out costate accuracy relative to raw rollout costates; that the gain survives a discretization-bias analysis; that improved costate accuracy predicts a smaller independently measured Hamiltonian gap; that the smaller gap predicts better paired economic performance; and that the gain is not reproduced by a cheaper direct-policy or actor-only method.

Without that chain, the critic remains an optional candidate-generation device rather than the source of the paper’s numerical contribution.

### B6. The observation theorem solves a strong and nonstandard implementation problem

The observation proposition is mathematically coherent under its assumptions, but those assumptions materially narrow the economic claim.

The controller requires continuous noiseless observation of every capital coordinate, exact knowledge of all drift and diffusion coefficients, exact knowledge of its own continuously accumulated actions, exact evaluation of the drift integral from the observed path, persistent internal memory, and an independent private Brownian motion used to synthesize the unobserved null-space innovation.

This is not an ordinary deterministic Markov state-feedback rule. It is a randomized, history-dependent controller in an enlarged filtration.

The manuscript should not present this primarily as recovering a practical state-feedback implementation. It is an existence-equivalence result for a particular information structure. Economically, one must explain who observes the continuous capital path without noise, how the drift integral is formed, why private Brownian randomization is available and innocuous, and whether randomized controls belong to the intended admissible class.

For a numerical-method contribution, the more relevant implementation would use discrete, possibly noisy observations and a stated filtering or state-reconstruction procedure. That would add a nontrivial error term, which is currently outside the theorem.

### B7. The scalar HJB reference does not validate high-dimensional accuracy

The one-state development diagnostic is encouraging: in the smoke run, the finite-grid center-value loss is about `1.6e-5` for NBO, `2.0e-4` for DPO, `9.1e-4` for the affine actor, and `1.47e-3` for the anchor.

But this calculation cannot establish that NBO approximately solves the 10-, 20-, or 50-dimensional control problem.

The scalar model removes cross-sectional dispersion, changes the role of common versus idiosyncratic risk, and permits a direct monotone grid solve. The learned actor is evaluated as Markov feedback on that grid, whereas the high-dimensional guarantee concerns a randomized innovation-history implementation. The reference therefore checks code and one nonlinear special case. It is not evidence that the high-dimensional costate, value, or policy error is small.

The high-dimensional regret endpoint remains anchored to a broad analytical schedule bound. Unless the final study closes a meaningful fraction of that bound, the result is still safe improvement rather than accurate solution of the HJB.

### B8. The economic decision experiment does not by itself supply Econometrica-level content

The management-fee identity is exact for log utility: a proportional fee shifts utility by a known discounted `log(1-tau)` term. This is a transparent way to translate a utility interval into an adoption threshold.

It is not, however, a new economic application. It is an algebraic transformation of the same policy difference in the same stylized model. The nine-profile population is explicitly not empirical. The capital economy is not calibrated to data, and the fee is not tied to actual implementation costs.

This may be useful exposition, but it does not resolve R11’s concern that the application is too stylized and the gains too small to carry a very broad paper. A top-journal numerical method should either unlock a substantive economic result that strong existing methods cannot obtain or establish a broadly useful computational improvement across a carefully controlled suite.

The present cumulative manuscript still spans recursive utility, endogenous preferences, time inconsistency, dynamic games, viscosity selection, interval verification, stochastic traces, high-dimensional capital, observation reconstruction, and management fees. The R12 theorem and intended experiment are much narrower than that title and scope.

## 4. Major comments

### M1. Materialize the exact submitted paper

The final branch should contain the authoritative integrated `ECTA.tex`, `supp.tex`, response, generated tables, PDFs, raw results, and manifests. A reviewer should not have to infer the paper from an integration program that will later rewrite root files.

### M2. Do not call protocol text “executed evidence”

The response should be generated only after the final evidence exists, and every numerical sentence should be bound to the evidence commit.

### M3. Report seed-by-seed direct contrasts before aggregating

For every dimension and both origin and population designs, the final paper should show the paired mean, lower and upper continuous-time endpoints, training and verification work, whether NBO beats DPO, loses to DPO, or is inconclusive, and all ten seed-level outcomes.

A count of favorable seeds is useful but not sufficient. There is no declared probability model over optimization seeds, so the paper should avoid treating ten seed outcomes as an inferential sample from an undefined optimizer population.

### M4. Add fixed-work and fixed-accuracy comparisons

The same fitted checkpoints can support fixed wall time, fixed simulator visits, fixed update counts, fixed peak memory, fixed candidate-generation work, and minimum total work required to achieve a declared certified endpoint. The last is the economically relevant numerical comparison.

### M5. Validate the mechanism chain

The final ablation table should connect rollout-target variance, critic held-out value and costate error, independent Hamiltonian action loss, paired payoff performance, and total computation. Otherwise “what the critic contributes” remains theoretical motivation rather than an empirical result.

### M6. Clarify the comparator filtration

The deterministic performance envelope is said to cover randomized adapted controls, and the proof argues that independent randomization cannot exceed the best deterministic realization in expected payoff. This point should be stated in the main theorem, including the admissible filtration and any conditioning on the private randomizer.

### M7. Separate pathwise observation from numerical observation

The exact continuous-history proposition is a mathematical benchmark. A practical algorithm observes a finite stream of floating-point measurements. The paper should either add a discrete-observation implementation and transfer error or narrow its language to the exact continuous observation model.

### M8. Strengthen the scalar reference diagnostics

The final reference should report all nested grids and domains, value and policy changes under refinement, boundary sensitivity, linear-system and Howard residuals, action-bound frequencies, fixed-policy residuals, and the learned policies’ losses at more than the center state.

### M9. Reduce cumulative scope

A focused paper could center on a policy-specific continuous-time certificate, direct NBO-versus-DPO comparisons in the capital model, the observation implementation, and one independent low-dimensional reference. The remaining historical applications can be archived or developed in separate papers.

Keeping a 42-page main article and a 118-page supplement makes it difficult to identify the theorem–algorithm–experiment chain that is supposed to justify publication.

### M10. Preserve the good evidentiary practices

The final version should retain separate development and final noise banks, all unsuccessful seeds, raw arrays and fitted weights, common-path identity checks, adverse policies, explicit state stresses, exact-source hashes, fixed family allocation, and the distinction between software completion and a positive economic result.

## 5. Independent inspection of the available artifact

I downloaded and inspected the retained development artifact from workflow run `37165156468`, tied to commit `b0ba58edad3260be6eaa7c0acd7b96ee6c735906`.

It contains three dimension-10 primary fits (`nbo`, `dpo`, `linear`), one seed (`7919`), 32-path origin and population evaluations, four direct paired comparisons, a raw-costate development ablation, one scalar reference grid, 19 passing R12 tests, compiled development PDFs, and an audit explicitly marked `development: true`.

The audit reports `primary_fits = 3`, `all_fits = 7`, `policy_evaluations = 7`, `method_comparisons = 4`, `one_sided_used = 22` of 4,000 allocated, and no signed population NBO improvement or NBO-minus-DPO conclusion.

This artifact is useful for checking that the new pipeline can produce the proposed objects. It is not evidence for the final claims because it uses neither the final training budget nor the final path count, dimensions, or seeds.

I also inspected the artifacts retained from the current and preceding failed complete checks. They confirm the historical-hash failure and the typography gate described above.

## 6. Conditions for a potentially reviewable future paper

A future submission should meet all of the following before external review begins.

1. **One immutable evidence snapshot.** Publish the integrated manuscript, supplement, response, raw arrays, weights, tables, logs, manifests, and compiled PDFs in one descendant commit.
2. **A green internal gate.** Resolve the historical-preservation policy consistently, pass all inherited and current tests, and pass the declared compilation checks.
3. **All final results present.** Execute all ten fixed streams in dimensions 10, 20, and 50 without replacing failed runs.
4. **Direct paired inference.** Report NBO-minus-DPO and NBO-minus-affine endpoints for every declared seed and design.
5. **Matched-accuracy work frontiers.** Compare total work to reach the same certified economic accuracy, in addition to the announced-time experiment.
6. **Mechanism evidence.** Demonstrate the critic-to-costate-to-Hamiltonian-to-payoff chain using independent held-out quantities.
7. **A realistic implementation variant.** Either add discrete/noisy observation and its transfer account or explicitly narrow the claim to exact continuous observation with private randomization.
8. **A stronger absolute benchmark.** Use the scalar reference as a diagnostic, not as evidence for high-dimensional accuracy; provide a materially tighter high-dimensional policy benchmark or state the result as safe improvement only.
9. **A focused contribution.** Reduce the manuscript to the theorem, algorithm, evidence, and economic question actually established.

## 7. Recommendation

R12 shows serious methodological learning. It responds directly to the previous report and proposes a much better experiment. The costate bound, paired comparison, finite-population extension, and observation-space construction are useful ingredients.

But the object currently in the repository is not the completed R12 paper described by its response. It is a development branch with missing final evidence, non-materialized manuscript integration, a red complete check, and only an explicitly non-final smoke artifact.

I therefore recommend **rejection in the present form**. I would not invite another ordinary revision of this cumulative submission. A future, substantially focused paper could merit a fresh review after the complete evidence exists and the method-specific and economic contribution is demonstrated rather than scheduled.
