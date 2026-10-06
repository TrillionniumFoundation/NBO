# Response to the referee on Neural Bellman Operators

We thank the referee for identifying the distinction between certifying a candidate, constructing that candidate by neural training, and demonstrating a reduction in complete work. We retain the paper's original question and title. The revision develops the neural construction rather than changing the paper into a method-neutral certification article. It incorporates the intervening full-policy and recursive-risk derivations into a single current manuscript and supplies a new evaluation-aware gradient–curvature theorem. All earlier economic applications, proofs, and adverse numerical outcomes remain available in the publication archive and at their original repository paths.

The report reviewed commit `278916666b32e03081ffe8d4aa05d9766c259b85`. This revision starts from `2bbd8900080a009e806f8d9d0f27fb9f0eefe9e1`, including the later R23–R31 developments. These are not represented as work first done in R32. The new contribution is the gradient–curvature implication, its exact algebraic checker and boundary tests, and the complete publication integration with a separately identified replay of the unchanged 72-service recursive catalogue. The release audit records what actually ran. Neither this response nor a successful software check represents an editorial acceptance decision.

## Blocking concerns

### B1. Work to an economic accuracy target

We retain the reported adverse comparison: the earlier check-and-refresh NBO procedure is more expensive than fresh refitting in every displayed future-change cell, and cached SAA is the least-cost fully certified procedure in all eight such cells. Those measurements are not replaced by new clocks. The current evidence section additionally reports complete, independently checked policies in the continuous-Gaussian, vector-control economy. It displays the structural comparator with the same analytic information and includes its lower costs whenever observed. The recursive replay records initialization, all primitive allocation and factor updates, actor solves, candidate writes, verification, and unsuccessful attempts. Closing-ledger and common process overhead are separately identified.

The constructive and gradient–curvature theorems establish properties of the specified trained neural representation; they do not prove that its construction is cheaper. Thus the revision strengthens the neural mathematical contribution without relabeling a policy certificate as a work advantage. A broad claim of neural cost dominance is not made. This empirical part of the referee's objection is not declared resolved by algebra alone.

### B2. Accuracy of the economic response versus necessity of NBO

The finite-law comparative-static bands and the sharper enumeration results are preserved together. The full-policy experiment reoptimizes future vector controls and compares the NBO response with a structural solution; the two experiments answer different economic questions. We no longer use the sign of a certified response to infer that its neural construction was necessary. The positive claim is that a trainable continuation can be constructed to a prescribed full-policy loss allowance and that the actual returned policy is independently checked. Computational necessity would require a different piece of evidence and is not inferred from the sign calculation.

### B3. Executing the policy-composition argument

The all-state capital section instantiates the missing terms for a directly specified discrete-time economy. The own-policy quadratic evaluation supplies continuation coefficients. Completion of squares treats every real vector action, not a candidate menu. Coercivity yields a comparison with all adapted finite-cost policies. The recursive-risk section gives a Bellman subsolution with distinct coefficient and constant allowances, checked Gaussian moment margins, and a separate relative action-execution account. These are uniform algebraic statements over the state space; sampled states are not used to establish coverage.

The class and value-transfer allowances are zero for this directly specified model because the comparison already uses the full adapted class and there is no model discretization. They are not set to zero for the original controlled diffusion or for a strategic equilibrium. The primitive-budget theorem, full proofs, implementation, and unchanged recursive execution are now reachable from the same current article and supplement rather than being detached source fragments.

### B4. The decision problem and its structure

The later policy experiment has 24 dates, ten or fifty vector controls at every date, and continuous Gaussian shocks with unbounded support. Technology and valuation regimes reoptimize all future controls. This directly repairs the scalar-action, four-date, fixed-future limitation of the original experiment as a test of the full-policy theorem. It does not make Gaussian integration difficult in a quadratic economy. We retain the analytic structural solution and explicitly state that continuous support alone is not a demonstration that learned continuation is computationally essential. The new geometry result concerns a trainable square factor within this original controlled-economy program, not an assertion of universal approximation or speed superiority.

### B5. A theorem for updated neural weights

The current constructive theorem updates every entry of the square hidden-weight factor. A reference feedback and primitive spectral envelope determine its initialization scale, step size, local error tolerance, and finite cap before evaluation targets are supplied. A joint backward induction establishes that subsequently generated own-policy targets satisfy those bounds. This is not a theorem for a fixed feature dictionary.

R32 adds a distinct a posteriori implication. If the target is bounded below by mI and the loss Hessian is bounded below by minus kappa times the identity with kappa less than m, the smallest squared singular value of the factor is at least (m-kappa)/3. Its Gram error is consequently bounded by its gradient norm times sqrt(3/(m-kappa)). A complete proof uses a minimum singular-vector direction. The inexact-target corollary explicitly charges both the Hessian perturbation and the factor-Frobenius-norm times the spectral target error. It rejects the singular zero-gradient saddle. The result applies when its full Hessian premise is checked; it does not assert that an arbitrary nonconvex optimizer reaches that premise.

### B6. Method-level reliability and replication

The 480-service additive design retains its prespecified, exhaustively enumerated finite training randomizer. Its success frequency and expected bounded operation counts refer to that declared finite distribution. The 72-service recursive design instead declares a deterministic catalogue estimand with two seeds; its realized clocks and success counts are not population inference. The R32 replay uses the same dimensions, regimes, risks, ordering, seeds, tolerances, and caps. It is an independently identified execution, not an enlarged independent sample supporting a new population claim.

The constructive theorem gives a deterministic, explicitly delimited guarantee for controlled initialization in exact arithmetic. Numerical acceptance still requires the rounded-policy verifier. These deterministic and finite-design statements are kept separate from claims about unspecified random training runs or future economic requests.

### B7. The economic applications

The recursive entropic capital model now has a complete full-state, full-action comparison and an executed neural construction. The original recursive-utility, endogenous-preference, temporal-self, and game formulations remain in the Economic Applications companion, with their own hypotheses. Their models have not been deleted or replaced by the quadratic laboratory. A solved entropic instance does not supply the equilibrium and full-deviation constants for all those applications. Their broader numerical validation is not reported as completed by these experiments.

### B8. Organization and preservation

The main article is organized by economic target, continuation construction, full-policy error, training geometry, and numerical evidence. The current supplement contains the policy, recursive-risk, and constructive proofs required for that chain. The prior article and technical supplement are retained as separately compiled historical documents, and the original applications companion remains present. Cross-reference routing changes in the publication wrappers do not alter historical mathematical bodies. A source-hash and label audit records this preservation. Original repository paths are not edited or deleted. Thus the reader need not follow branch chronology to find the current argument, while no adverse table or previous theorem is silently removed.

### B9. Economic interpretation

The studies are explicitly declared computational economies, not estimates of an observed reform. The early scalar responses condition on specified future policies. The later capital responses reoptimize future policies. The recursive criterion places discounting outside the one-step entropic certainty equivalent; it is not identified with every exponential-of-total-cost convention. The contribution claimed is a constructive numerical theory with transparent laboratory evidence, not empirical identification. A quantitatively calibrated economic application is not manufactured from these inputs.

## Major comments

### M1. Retain a single paper

We retain Neural Bellman Operators and the original controlled-economy question. The method-neutral decision bound serves that question but does not replace it. The architecture-specific finite construction and gradient–curvature result now provide the direct link to trained neural continuation. We do not take the recommendation to change the title or replace the topic as a substitute for improving the original paper.

### M2. The six terms in the policy bound

The current article identifies (i) own-policy, full-action residuals; (ii) all-state coverage through coefficient inequalities; (iii) continuation-domain and inverse margins; (iv) the full adapted policy class; (v) the direct discrete-economy target rather than an uncharged value-transfer claim; and (vi) the separately computed relative execution allowance. The inherited implementation is independently rerun at its original final tolerance. The new factor theorem enters this chain through an explicit actor-residual inequality and does not waive any of these six requirements.

### M3. Richer state and action comparisons

The full-policy experiment changes horizon, action dimension, stochastic support, and future-policy optimization simultaneously relative to the early scalar experiment. We retain its structure-exploiting comparator precisely because these changes do not eliminate its closed-form information. The role of this setting is to execute the neural training-to-policy theorem under an independent verifier; it is not described as evidence that all conventional alternatives are infeasible.

### M4. Prespecified estimands

The unchanged recursive protocol specifies the entire 72-service catalogue and explicitly disclaims population reliability and expected-runtime inference. Its original source-freeze hashes are checked before replay. New algebraic unit tests are development checks, not additional economic replications. The release distinguishes historical measurements, new replay measurements, deterministic proof checks, and the scope of each estimand.

### M5. Refresh policies

The original frozen check-and-refresh result and its failed checks remain intact. The later cold/warm comparison and complete-policy constructions have separate declared designs; they are not retrospectively called an optimized version of the earlier refresh policy. No post-outcome tuning is used to reverse the earlier adverse comparison. A general optimal-refresh claim is not made by the present revision.

### M6. Contribution-isolating work

The evidence separates model initialization, neural allocation and training, actor construction, file writes, and verification. The original counters retain hidden updates, Gram checks, actor solves, own-policy transforms, and simulation transitions. The analytic quadratic setting has zero simulation transitions for both generators, which is disclosed rather than interpreted as neural sampling efficiency. Process-wide peak memory is not relabeled as method-specific memory. The original conventional regression, cached simulation, direct-actor and HJB accounts remain in the historical evidence with their actual, distinct targets.

### M7. Candidate, verifier, and generator

These three objects are distinguished in the abstract, introduction, theorem statements, and evidence interpretation. A certificate concerns the actual returned policy. The finite cap and gradient–curvature theorem concern a specified neural generator or its checked training state. Comparative cost concerns two complete procedures at the same economic tolerance. None is inferred merely from another.

### M8. Future policies and the terminal boundary

The later regimes reoptimize all future controls; the original regimes condition on specified futures. At the last recursive date, the known terminal coefficient Qf still enters through its risk transform Psi_theta(Qf). R32 writes the actor formula explicitly and tests it against both the correct transformed solution and the generally incorrect untransformed one. The existing frozen code already used the correct transform, so this clarification is not reported as a repair to historical numerical outcomes.

### M9. A current theorem chain rather than cumulative narration

The current publication has one entry point and a current proof supplement. Historical materials remain available as an archive rather than being renumbered into another sequence of revision-numbered claims. The original model and applications are retained. Preservation is established by the unchanged source objects and the publication manifest, not by claiming that a short summary replaces the original scientific record.

### M10. Evidentiary standards

The release records immutable base and source commits, the exact referee blob, frozen scientific-input hashes, test logs, new execution identities, complete attempted-service records, compiler logs, and publication-file hashes. Failed checks and failed workflow attempts are not rewritten as successes. New clocks do not replace original clocks. Successful compilation and testing do not certify a theorem's premises in an unexecuted economic model or establish a positive method frontier absent the relevant evidence.
