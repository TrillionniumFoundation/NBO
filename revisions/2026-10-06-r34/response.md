# Response to the Referee on Neural Bellman Operators

The authors thank the referee for distinguishing economic accuracy, neural construction, and complete computational work. This revision retains Neural Bellman Operators as the paper's subject and preserves the original controlled-diffusion model, its economic applications, and all unfavorable numerical results. It develops the constructive neural argument rather than replacing the paper with a method-neutral certification study.

The report addressed here is reviews/2026-10-05-econometrica-numerical-methods-r21/referee_report.md at review commit 281e57b18a2d88de68d2219da1a7194e90570d13, with report blob 947147612cc22f5e10ff15faf347fcb3de222656. Its reviewed manuscript is R21 at 278916666b32e03081ffe8d4aa05d9766c259b85. Intervening derivations through R33 are inherited from 5e28283a99f00b3b28f8890abc464b3cd256fa6f. The response differentiates those inherited results from the new R34 argument. The repository report is an advisory referee exercise, not an editorial decision issued by Econometrica.

## Principal changes

The current article brings together the full adapted-policy certificate, the primitive-budget cold construction, the gradient--curvature criterion, and the noncommuting warm-start theorem. The new result joins warm-start learning to a full-policy accuracy target. It allows the fitted Gram matrix to lie on either side of the continuation target and separately pays for its Frobenius fitting error, the evaluator's spectral radius, and the actor equation error. A joint backward induction proves the coefficient envelope and policy comparison without presuming successful training. A finite-arithmetic corollary specifies exact own-policy evaluation and explicitly rounded factor updates. Complete proofs are in the current supplement.

Two exact four-date construction instances exercise this new connection, including actual reuse of previously trained factors, noncommuting initial matrices, nonzero evaluation radii, and inexact actor solves. They are identified as constructive validations, not as independent economic samples. The frozen 72-service recursive experiment is executed under its original ordering, tolerances, and failure rules with a new execution identity. Its complete-work comparison is reported without replacing the original measured clocks. Final counts, source hashes, raw records, test logs, and native compilation results are recorded in audit/RELEASE_AUDIT.json and the accompanying evidence files.

## Responses to the principal objections

### B1. Adaptive reuse is more costly than fresh refitting in the existing experiment

We retain this result. In the eight changed-future cells discussed in the report, the historical check-and-refresh rule is more expensive than fresh refitting, and cached simulation is the least-cost fully certified procedure. The old article, supplement, and raw evidence remain unchanged. The new training theorem does not retroactively improve those clocks.

The mathematical response is a precisely admissible use of an old continuation. An independently bounded target change or a directly checked Gram enclosure admits the old factor into a new training basin. The contraction then gives a finite retraining cap above a stated arithmetic floor. The resulting actor must still pass the full-policy acceptance rule. Evaluation, failed gates, fallback construction, verification, and output enter the same work account. Comparing two sufficient iteration caps is explicitly not treated as a measured work advantage over an early-stopping comparator.

### B2. The finite-law signs do not establish neural necessity

We agree that the finite-law verifier can establish those signs independently of a neural generator. They remain evidence about the original decision target, not a necessity result. The new contribution is a constructive statement about trained hidden weights and their propagation to full-policy accuracy. All factor entries are updated. The current comparison includes the analytic structural solution wherever the model provides it. Neither exact enumeration in the old finite law nor analytic Gaussian integration in the new model is claimed as a neural innovation.

### B3. The composition theorem needs an executed full-policy bridge

The intervening full-policy and recursive-risk derivations are now integrated into the article. They evaluate the returned policy's own future, optimize deviations over the entire real vector action space, and use coefficient inequalities valid on all real states. The initial accuracy comparison is uniform on the declared initial-state ball. The comparator is all adapted policies of finite recursive cost, not only linear, neural, or sampled policies.

R34 adds the missing joint budget for warm construction. The fitted Gram error is Frobenius, the own-policy evaluation radius is spectral, and the latter consequently carries the appropriate dimension factor in the full-action residual. The actor equation residual takes its own share. The independent numerical verifier retains its moment-domain, positivity, and execution checks. These obligations are not inferred from a small training loss or an admissible warm start.

### B4. The original finite support, short horizon, and scalar control are too limited

The original experiment is retained as an auditable decision study. The integrated recursive experiment has 24 decision dates, dimensions 10 and 50, continuous Gaussian innovations, and real vector controls. Future policies are reoptimized for each economic regime. State coverage is established by matrix inequalities rather than a finite state catalogue. The Gaussian structure also provides a strong cheap comparator, which remains visible. Continuous support alone is not presented as proof that the neural procedure is needed or cheaper.

### B5. Fixed-feature theory does not establish hidden-weight neural training

The constructive theory now concerns a square-activation scalar critic with every entry of its factor trainable. The cold theorem supplies a primitive initialization, step size, accuracy allocation, and finite cap. The gradient--curvature theorem supplies an additional checked route to Gram accuracy and excludes the zero-gradient singular saddle. The warm theorem permits rectangular factors, noncommuting starts, and bounded errors in the complete update.

The new policy theorem accepts two-sided factor error, rather than carrying over the cold theorem's one-sided ordering without proof. Its finite-arithmetic corollary supplies a specified realization with rational evaluation and explicit factor rounding. We do not extend these architecture-specific guarantees to arbitrary initialization or to an unenclosed floating-point optimizer. The original smooth-network formulations remain in the paper with their own hypotheses.

### B6. A few seeds do not identify population reliability

The revision separates deterministic reliability from empirical frequency. The warm cap holds for every factor and update perturbation satisfying its verified basin and error account. Randomized implementations supported entirely in that class inherit the implication. The registered service catalogue has a descriptive, finite-design estimand; its two seeds do not estimate success over an unspecified population of fits. Algebraic regression tests, exact construction instances, and repeated verification of a stored candidate are never counted as additional independent economic observations.

### B7. The breadth of economic applications is not supported by one experiment

The original economic applications are preserved in their companion manuscript. The current recursive-risk result is explicit about discounting outside the certainty equivalent, the Gaussian moment domain, and the distinction from other exponential-total-cost conventions. It supplies a complete policy comparison for its declared capital economy. It does not silently certify the separate endogenous-preference, multi-self, or strategic applications. Those retain their stated equilibrium and comparison conditions. This organization preserves the original economic scope without presenting one successful verifier as evidence for every model in it.

### B8. The cumulative manuscript has become difficult to read

The current article is organized around the economic target, decision-relevant errors, full-policy comparison, constructive training, warm reuse, and numerical evidence. Its current technical supplement contains the corresponding proofs. The previous article and supplement remain separately identified historical companions, and the applications remain accessible. No historical theorem, unfavorable table, or application is deleted. A preservation audit records the old source components and labels, while cross-document references distinguish the current argument from the retained historical material. The article itself is not a chronological revision log.

### B9. Stylized primitives and different future-policy targets need clear interpretation

The capital examples are stylized specified economies, not empirical calibrations. The original finite-law signs concern their specified future policy. The current full-policy experiments reoptimize that future in each regime and evaluate the returned future at every preceding date. Changed-valuation and technology responses are interpreted within their declared targets. An old continuation may serve as an initial factor but cannot replace the new policy's own continuation unless a separate evaluation or transport bound pays for that discrepancy.

## Responses to requested changes M1--M10

### M1. Choose one paper

We retain Neural Bellman Operators. The affirmative contribution is a constructive neural path from economic primitives and updated hidden weights to a full-policy accuracy target, including changing futures and finite arithmetic. Certification is the means of proving what the returned neural policy achieves; it is not a replacement topic. At the same time, the paper does not claim empirical neural cost superiority where the recorded comparator is cheaper. A theorem about trainability and an experiment about relative work answer different questions.

### M2. Instantiate every term in the composition bound

The integrated dynamic application supplies six explicit accounts. Own-policy full-action defects come from the actor residual against the returned future's Gaussian continuation. State coverage follows from coefficient inequalities on all real states. Recursive weights are generated by positive moment margins, with separate powers for the quadratic coefficient and the state-independent certainty-equivalent term. The class term is zero because the comparison directly covers all adapted finite-cost policies. The transfer term is zero for the directly specified discrete economy, not for an unverified continuous-model approximation. Rounded policy evaluation and action execution are separately enclosed.

For warm construction, the new local gate checks both the fitted coefficient's magnitude and its mixed-norm action-error allowance. The first prevents an overshooting factor from invalidating the primitive envelope; the second pays for Gram, evaluation, and actor error in the economic objective. The exact construction additionally verifies a Bellman matrix subsolution independently of the scalar error recursion. Numerical executions keep their distinct implementation allowances.

### M3. Use a harder stochastic and dynamic setting

The continuous-support, 24-date, vector-control experiment replaces neither the original economic model nor its historical evidence. It adds a directly specified dynamic application in which full-support enumeration is unavailable and full-policy verification does not rely on sampled state coverage. The strong structural solution receives the same analytic information as the neural method. Consequently the experiment tests constructive neural accuracy under a demanding comparison, while preserving the distinction between a harder certificate and an economic need for neural approximation.

### M4. Define the reliability estimand and preserve failures

The article states the admissible deterministic input class for each construction and the declared finite service catalogue for realized outcomes. The frozen catalogue, both registered seeds, all attempted certificates, failure classifications, and denominator counts are retained. A replay is assigned a separate source and execution identity. It is not pooled with the original execution to create an artificial population sample. Domain failure, precision-floor failure, warm-gate failure, and failure of the final policy test remain distinct outcomes.

### M5. Improve the refresh decision without hiding failed work

The warm-start gate tests whether the old factor can be retrained within the proved basin. It does not accept the old action or the final policy. A direct new-target enclosure may be sharper than the old-error-plus-drift gate. A failed gate invokes a charged fallback; a requested tolerance below the arithmetic floor requires more accurate arithmetic or a different verified construction. Increasing the iteration count alone does not justify acceptance. All these decisions leave an explicit work and failure record.

### M6. Compare complete work against strong alternatives

The complete service includes primitive-envelope construction, own-policy evaluation, all hidden-weight updates, actor solves, residual checks, failed attempts, verification, serialization, and durable writes. Closing-ledger and common overhead are separately recorded. Analytic Gaussian information is available to both compared procedures, and zero simulation counts are not represented as a neural sampling advantage. Process high-water memory is reported only as a process quantity, not as a method-specific peak-memory comparison. The new replay table and cellwise cost ratios are computed from the complete service records.

### M7. Distinguish candidate accuracy, constructive learning, and neural necessity

The abstract, introduction, theorem discussion, experiment interpretation, and conclusion now use these distinctions consistently. A full-policy certificate establishes what a candidate achieves. A finite hidden-weight cap establishes a property of the declared construction. A complete-work comparison describes which executed procedure was cheaper. The new results strengthen the first two statements without using them as a substitute for the third or for a necessity theorem.

### M8. Clarify economic comparative statics and the returned future

Each dynamic target is evaluated after its future policy is finalized. The changed economy therefore receives its own continuation and its own policy verification. The exact warm-reuse instance stores the actual old trained factors, the changed targets, their noncommutation checks, the updated factors, and the resulting vector actors. The old specified-future comparisons are retained with their original interpretation. The known terminal coefficient is risk-transformed before the terminal actor solve; it is not replaced by the raw terminal quadratic unless that transform is unchanged.

### M9. Supply a readable native publication and a traceable preservation record

The release uses the repository's Econometrica class and author--year bibliography. It supplies current article and proof-supplement entry points, the response, and retained historical and application companions. The previously missing R23 generated-table dependencies are reconstructed from frozen records rather than filled with invented results. Source hashes, unchanged-input checks, cross-reference diagnostics, and component preservation are recorded separately from the scientific prose. Native compilation status and any remaining page diagnostics are reported as observed, not presumed from the presence of LaTeX source.

### M10. Retain the evidence standard

Every added scientific statement is tied either to a proof with explicit premises or to an identified execution. Unit tests and exact rational checks do not establish economic calibration, population reliability, or ordinary BLAS roundoff correctness. A successful build is not an external referee's acceptance. The source and publication branches preserve the report, the inherited derivations, the new argument, the completed executions, and their audit trail for the next referee to examine independently.
