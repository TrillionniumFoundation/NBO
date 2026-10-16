# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r52-review-ready-2026-10-08`  
**Pinned revision commit:** `e82e05e658d6aba9bb843dcece66410d1040a49a`  
**Pinned revision tree:** `0a5b4b0b2972b681aa0b67da7020c8a13b987a80`  
**Pinned main manuscript:** `revisions/2026-10-08-r52/ECTA.tex`, Git blob `90c5671ec8386fc1e027d3acccbd76602084ae0c`  
**Pinned technical supplement:** `revisions/2026-10-08-r52/supp.tex`, Git blob `48a5531203b35b57fed4b9d7d03c7b19dafdedda`  
**Pinned response:** `revisions/2026-10-08-r52/response.md`, Git blob `a56c7d83d741363b7a30849a355b2c30bc2af594`  
**Publication workflow:** `37778705654`  
**Review date:** 8 October 2026  
**Recommendation:** **Reject in the present form and do not invite another ordinary revision of the cumulative manuscript. A new, sharply focused paper on action-contrast-certified, incumbent-preserving policy iteration could merit evaluation if the general certificate is executed in a substantive nonlinear economy, its computational cost is characterized, and actual policy cost becomes the primary numerical endpoint.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R52 is the first version in this sequence that simultaneously clears the publication-completeness threshold and states a mathematically coherent answer to an important question raised by the earlier evidence. The repository now contains one canonical review-ready branch, ordinary main and supplementary sources, a point-by-point response, five compiled documents, a source-bound evidence package, 54 passing inherited and new tests, and an independent clean-archive rebuild. I verified both released workflow artifacts, all 1,037 files listed in the final-delivery manifest, the declared source and policy hashes, and every one of the 524,288 deposited observation-cell rows in the new experiment. I found no immediate algebraic contradiction in the central action-contrast theorem, its sharpness example, the coupled-residual recursion, or the explicit action-null construction.

The new mathematical observation is useful. A continuation approximation matters for a decision through differences of conditional expectations across feasible actions, not through an arbitrary global level or range error. R52 formalizes this with an action-contrast certificate

\[
 |(P_t^a-P_t^b)e_{t+1}(x)|\le R_t(x;a,b)\le\chi_t,
\]

uses it in an incumbent-preserving acceptance gate, and obtains the finite-sweep recursion

\[
 E_t^{k+1}\le \beta_tE_{t+1}^k+
 \alpha_t^k+\zeta_t^k+2\beta_t\chi_t^k.
\]

The paper also provides a constructive, representation-neutral way to upper-bound such contrasts from policy Bellman residual differences and couplings. In the exact case, the theorem shows that finite-horizon policy improvement reaches the original Bellman optimum after at most the horizon number of passes, even if the critic has a nonzero and nonconstant global error that is null for action comparisons. This is a real strengthening of the preceding signed-width analysis.

The new experiment cleanly illustrates the distinction. It inserts the component

\[
 n_M(y)=M(y_1-2y_2+1)_+,
\]

whose global width is \(2M\) but whose action contrast is exactly zero because the action coefficients in the first two transition coordinates are \(1/2\) and \(1/4\). For each of eight frozen policies, the experiment exhausts all \(256^2\) closed observation cells. At \(M=0\), the old global-width gate and the contrast-aware gate agree. At \(M=1,16,4096\), the global-width gate rejects every strict change, whereas the contrast-aware gate returns exactly the same policy as at \(M=0\). All accepted true-cost upper bounds are nonpositive and no feasibility violation is recorded. This is a convincing deterministic regression test of the stated invariance.

The revision is also candid about what the experiment does not establish. It creates no new independent policy-cost estimand. It does not execute the general coupled-residual certificate in the continuous investment model. It does not run a full sequence of policy-improvement sweeps in that economy. It holds the economic policies fixed while varying a deliberately constructed nuisance component. Most importantly, it does not alter the adverse actual-policy evidence inherited from R49 and R51: the witness policy had higher expected cost in 93 of 96 R49 comparisons and lower cost in none; after both methods receive the common terminal repair in the later comparison, witness cost remains higher in 26 of 27 groups and unresolved in one.

This last point is decisive. R52 gives a sharper and more economically appropriate certificate. It does not show that the proposed generator returns a better policy, reaches a common policy-cost target with less work, or unlocks an economic result unavailable to a strong conventional method. The central positive result is furthermore representation-neutral. The same action-contrast theorem, coupled-residual certificate, action-null cancellation, and incumbent gate apply to native dynamic-programming representations. The paper itself correctly states that the native min-plus object and its exact ReLU encoding are not distinct empirical methods.

My recommendation is therefore rejection in the present form. The strongest publishable object is now clear: a focused paper on policy-relevant continuation error, safe incumbent-preserving improvement, and constructive action-contrast certificates. Such a paper could be important. It would need, however, to execute the nontrivial certificate rather than only an exact null-space identity, quantify the work required to construct it, carry out full sweeps in a substantive nonlinear model, and evaluate the resulting work-to-actual-policy-cost frontier.

## 2. What R52 successfully repairs

The negative recommendation should not obscure substantial progress.

### 2.1 The submission is complete, canonical, and reproducible

R52 resolves the administrative failure identified in the R50 threshold report. The root README identifies R52 as the authoritative revision. The review-ready branch, main article, supplement, response, complete development editions, generated tables, raw records, source manifests, release audit, and clean rebuild are present together.

The active article is 51 pages, the active supplement 40 pages, the response 7 pages, the complete development article 117 pages, and the complete supplement 101 pages. The release audit reports no undefined references, duplicate labels, missing characters, fatal errors, or overfull boxes. The only compilation notices are disclosed font-shape substitutions. The clean archive deletes generated outputs and rebuilds all five documents offline without rerunning scientific services.

This is a genuine reviewable object rather than a detached workflow or source fragment.

### 2.2 The action-contrast theorem targets the right economic error

A global sup-norm or range bound can be conservative for a decision because it charges components that shift every feasible action by the same conditional amount. R52 identifies the correct policy-relevant quantity and preserves the original Bellman optimum, feasibility class, acquisition contract, and incumbent-safety guarantee.

The acceptance proof is direct. For an accepted proposal, the critic comparison plus the certified proposal–incumbent error contrast bounds the true advantage. For a rejected proposal, the exact incumbent is retained. The accuracy proof then controls the rejected incumbent relative to every feasible action with two action-contrast terms, which explains the coefficient two. I independently checked these identities and the one-period sharpness example.

This is conceptually cleaner than paying a global critic width at every action comparison.

### 2.3 The coupled-residual construction avoids assuming the unknown policy value

The paper does not merely postulate a small action contrast. It writes the policy-evaluation error as a residual plus a propagated future error and bounds pairwise error differences through couplings with the correct marginals. The recursion intersects this pairwise bound with the separately valid signed width. The same construction then bounds differences under two feasible action kernels.

This is a legitimate constructive route. It requires neither an optimal transport minimizer nor smoothness of the incumbent policy. It also degrades safely to the original scalar width when the pairwise enclosure is uninformative.

### 2.4 The action-null example is exact and economically tied to the stated model

The example is not inferred from sampled residuals. It follows algebraically from the action exposures in the original investment dynamics. Under a common innovation, \(y_1-2y_2\) is invariant to the action, so every bounded measurable function of that combination is action-null. The ReLU component has arbitrarily large global width and exactly zero decision effect.

The paper correctly states that this is a representation-level robustness property shared by any implementation of the same function. It is not relabeled as a neural superiority result.

### 2.5 The exhaustive ablation is unusually well recorded

The study fixes all eight inherited policies before execution, enumerates every closed eight-bit observation cell, preserves the original repair and action lattice, records every proposal and interval endpoint, and replays the unmodified inherited terminal gate independently. It keeps the same policy catalogue at all amplitudes and reports zero new independent policy-cost estimands.

My independent replay confirms:

- 8 services;
- 524,288 cells;
- 4,194,304 scalar and contrast gate decisions;
- 406,464 contrast-aware strict changes;
- 31,165 blocked changes;
- 86,659 equal proposals;
- zero feasibility violations;
- no positive-amplitude strict change accepted by the old global-width gate; and
- exact amplitude invariance of the contrast-aware returned policy.

This is strong evidence for the deterministic identity being tested.

### 2.6 The adverse economic evidence remains visible

The paper retains rather than overwrites the result that actual witness-policy cost is generally higher than FVI cost. It also retains:

- failed resource allocations;
- the fact that the first curvature-based FVI rule did not change the grid;
- the adverse genuinely graded-FVI block;
- tensor-cover dependence;
- finite information-price assumptions;
- the distinction between own-incumbent improvement and cross-method dominance; and
- all previous numerical corrections and replay identities.

This level of evidentiary preservation is exemplary.

### 2.7 The revision separates theorem, deterministic regression, and statistical evidence

R52 explicitly distinguishes:

1. a general conditional theorem;
2. exact finite-state regression exercises;
3. an exhaustive terminal-date robustness ablation; and
4. inherited finite-sample expected-cost comparisons.

It does not pool these objects into an artificial sample size or claim that a repeated deterministic policy is a new economic observation. That separation is essential and correctly maintained.

## 3. Blocking concerns

### B1. The main positive theorem is not a method-specific neural result

The action-contrast theorem concerns a critic, a feasible proposal, an incumbent, and verified conditional-expectation differences. It applies equally to a spline, a table, a min-plus envelope, a projection method, or a neural network. The coupled-residual certificate is likewise representation-neutral.

The explicit ReLU nuisance shows that a neural representation can contain a large irrelevant component. But the same component can be stored natively, and the paper acknowledges this. Nothing in the theorem establishes that a neural representation constructs the needed critic, residual-difference enclosure, coupling integral, or action supremum more efficiently than a conventional representation.

This does not make the theorem unimportant. It does mean that the paper's central R52 advance should be evaluated as a general policy-certification result, not as evidence for a distinctive Neural Bellman Operators advantage.

### B2. The experiment validates a hand-constructed exact identity, not the general certificate

The experimental nuisance is chosen precisely so that its action contrast vanishes symbolically. Once the identity \(1/2-2(1/4)=0\) is established, amplitude invariance is the mathematical prediction. The exhaustive cell replay is valuable for checking implementation, boundary handling, feasibility, and arithmetic, but it does not test the difficult part of Proposition 52.

In particular, the experiment does not construct or evaluate:

- residual-difference functions \(H_t(x,y)\) in the continuous economy;
- the pair-state recursion \(D_t(x,y)\);
- nontrivial action-kernel couplings;
- a positive, state-dependent \(R_t(x;a,b)\);
- a certified uniform supremum \(\chi_t\); or
- the work and conservatism of those objects.

The new theorem's generality is therefore supported by proofs and finite-state tests, while the economic experiment tests only the exactly null special case.

### B3. R52 does not change the adverse actual-policy ranking

The manuscript's own retained evidence is decisive:

- R49: 96 witness-minus-FVI expected-cost intervals; witness cost strictly higher in 93, strictly lower in 0, unresolved in 3.
- R51 common terminal repair: witness cost higher before repair in 27 of 27 groups; after both methods are repaired, witness cost remains higher in 26 and unresolved in 1.
- Every witness incumbent has a positive own-incumbent gain, showing that safe improvement and cross-method superiority are different questions.

R52 creates no new independent cost estimand because its contrast-aware policies are identical to the inherited unperturbed repaired policies. The experiment therefore cannot improve, weaken, or reinterpret the existing ranking.

An Econometrica numerical-method contribution need not dominate in every cell. But when the direct economic endpoint overwhelmingly favors the conventional comparator, the paper must identify a different capability of comparable importance. R52 identifies a better certificate, not such an economic capability.

### B4. The computational cost of the coupled-residual certificate is uncharacterized

In a finite state model, the proposed recursion is naturally defined on state pairs. A direct implementation can require storage and propagation on \(|X|^2\) pairs, followed by action-pair or action-supremum calculations. In a continuous state model, one must represent and verify \(D_t(x,y)\), construct couplings with certified marginals, integrate the pairwise envelope, and take a uniform feasible-action supremum.

These operations may be comparable to, or harder than, direct policy evaluation or a more accurate Bellman solve. The paper says that the work is not free, but it does not provide:

- a complexity bound for constructing \(D\) and \(R\);
- a scalable approximation scheme with an error account;
- memory requirements;
- a comparison with the original global-width certificate; or
- an executed continuous-state instance with \(\chi>0\).

Without this information, the new certificate is mathematically constructive but not yet a demonstrated numerical method.

### B5. The finite-sweep near-optimality result is not executed in the continuous benchmark

The theorem's strongest conclusion is that exact contrast, search, and comparison conditions yield the original Bellman optimum after at most \(T\) passes. The investment experiment, however, changes only the final decision date while leaving all earlier dates fixed. Exact finite-state tests exercise one through five passes, but they are regression programs, not a numerical solution of the paper's continuous economic model.

Thus the paper has not shown:

- how evaluation, action-search, and comparison errors evolve across passes;
- whether the coupled certificate tightens or deteriorates after policy changes;
- how often the incumbent gate blocks improvements at earlier dates;
- whether the certified gap contracts in the predicted manner; or
- the complete work required to reach a declared policy-loss target.

The gap between the strongest theorem and the executed economic evidence remains substantial.

### B6. Exact action-null membership is structurally known; approximate or learned nullity is not addressed

The experiment uses an exact, hand-engineered action-null component. In practice, a learned critic error will rarely lie exactly in a known null space. A numerically useful method needs to handle components that are approximately null, incorrectly classified, or null only on a subset of the feasible state-action domain.

The paper correctly insists that null membership must be established. It does not yet provide a practical procedure for discovering or verifying such structure in a general neural approximation. Nor does it show robustness when the action coefficients, innovation coupling, feasible set, or learned component are slightly misspecified.

A sweep over controlled violations of the identity would reveal whether the contrast certificate degrades gracefully and whether its verification cost is justified. The current amplitude sweep varies only the size of an exactly irrelevant component, so it cannot answer this question.

### B7. No improved common work-to-actual-policy-cost frontier is established

The R52 service clocks measure loading frozen policies, enumerating cells, evaluating gates, replaying the inherited policy, and serializing records. They do not include policy construction, multi-pass evaluation, or a new expected-cost comparison. Mean recorded service time is about 4.03 seconds for witness incumbents and 3.79 seconds for FVI incumbents, but these diagnostic clocks are not a matched method comparison and should not be interpreted as one.

The inherited construction study separates resources more carefully and executes a common-accuracy block, yet actual policy costs still favor FVI. R52 has no new ordinate for the economically relevant frontier. The central empirical question remains unanswered:

> At a common upper confidence bound on actual expected policy cost, what complete work does each method require from primitives through construction, improvement, verification, and durable output?

Certificate robustness is useful, but it is not a substitute for this frontier.

### B8. The dimensional bottleneck motivating neural methods is unchanged

The executed economic models remain in dimensions two through four and rely on tensor state covers. The compiled witness method removes a redundant dense scan but retains exponential state-grid and corner factors. R52's new ablation is only two-dimensional. The action-contrast theorem does not alter those covering costs, and a pair-state residual certificate may introduce an additional dimensional burden.

There is no new evidence for:

- sparse or adaptive state representations at common accuracy;
- non-tensor high-dimensional performance;
- memory scaling of the coupled certificate;
- neural generalization replacing exhaustive coverage; or
- a dimension in which the neural representation enables a calculation that conventional methods cannot execute.

The high-dimensional motivation remains largely separate from the established result.

### B9. The economic interpretation remains normalized and method-neutral

The investment environments are transparent theoretical laboratories, which is appropriate for numerical analysis. But the new robustness result says only that a known irrelevant critic component should not block an otherwise certified terminal action change. It produces no new calibrated counterfactual, welfare conclusion, controller-adoption decision, or information-price estimate.

The retained sensor prices and replacement fees are normalized primitives rather than estimated economic costs. The action-null correction can improve a certificate without changing any policy or expected cost. Consequently, R52 strengthens the method's internal accounting but does not deliver an Econometrica-scale substantive economic result.

### B10. The cumulative scope remains disproportionate to the completed contribution

The active article is now substantially more focused than earlier versions, and the complete editions appropriately preserve history. Nevertheless, the project still spans controlled diffusions, recursive utility, endogenous preferences, temporal selves, games, trained critics, matrix factors, mixed precision, min-plus compilation, acquisition, information pricing, safe improvement, and action contrasts.

The R52 theorem concerns expected discounted costs with linear conditional-expectation differences. The new economic evidence is a two-dimensional final-date ablation. Historical applications do not receive the new action-contrast certificate, full-sweep execution, or actual-cost frontier.

The strongest result would be easier to assess and more valuable in a paper whose title, theorem chain, algorithms, experiments, and claims all concern the same object.

## 4. Major comments and required changes

### M1. Reframe the central contribution as a general action-contrast policy certificate

Lead with the representation-neutral theorem. State clearly which results apply to any critic representation and which, if any, depend on a neural architecture. Treat the ReLU action-null example as an exact realization, not as the identification of a neural method advantage.

### M2. Execute the coupled-residual certificate with a nonzero contrast bound

In the continuous investment model, construct \(H_t\), \(D_t\), \(R_t\), and \(\chi_t\) for an error that is neither globally small nor exactly null. Deposit all pairwise approximation and integration errors. Compare the resulting certificate with the original signed-width fallback in sharpness, work, memory, and accepted actions.

### M3. Run full incumbent-preserving policy sweeps in the economic benchmark

Execute all dates for up to \(T\) passes. At each pass report:

- the retained and proposed policy;
- evaluation bands;
- action-search error;
- contrast-certificate error;
- blocked and accepted cells;
- certified optimality gap;
- actual expected policy cost; and
- complete cumulative work.

This is the natural numerical counterpart of the theorem.

### M4. Study approximate action-null structure and misspecification

Perturb the action exposures, the nuisance direction, and the common-innovation assumption by prespecified amounts. Replace the zero certificate by a small verified positive one. Show how policy safety, accepted changes, and work vary with the degree of non-nullity. Include false-null rejection tests.

### M5. Provide a complexity and approximation theory for the pair-state recursion

State storage and arithmetic costs as functions of state dimension, action dimension, horizon, cover radii, coupling representation, and target accuracy. Develop structure-exploiting alternatives—such as analytic couplings, separable bounds, low-rank pair functions, or local pair covers—and prove their additional error accounts.

### M6. Make actual policy cost the primary numerical endpoint

Retain worst-case policy-loss certificates as safety constraints. Rank methods by complete work to a common actual-cost criterion or valid upper confidence bound. Report both own-incumbent gain and cross-method cost after each improvement pass.

### M7. Compare with stronger adaptive conventional methods

Uniform tensor FVI is already a strong comparator in the recorded cells. The failed curvature and adverse graded heuristics should remain. Add at least one residual- or surplus-driven sparse/adaptive method that demonstrably changes its representation and is evaluated under the same policy-cost and certification requirements.

### M8. Add a genuinely non-tensor dimension experiment

Use a model for which exhaustive tensor coverage is infeasible but the economic policy can still be checked by an independent method. Report memory, state queries, coupling work, action search, and policy cost at common accuracy. Dimensions two through four do not establish the scaling claim that motivates neural approximation.

### M9. Position the theorem against the closest policy-improvement and state-abstraction literature

The paper should distinguish its contribution from approximate policy iteration error propagation, performance-difference and advantage bounds, bisimulation or state metrics, potential-based transformations, value-equivalence, and robust policy improvement. The novelty appears to lie in combining verified action-contrast error, acquired-cell feasibility, and incumbent preservation; that combination should be stated precisely.

### M10. Produce a shorter, self-contained article

A focused submission should contain:

1. one expected-cost model class;
2. the action-contrast theorem and sharpness result;
3. one scalable constructive certificate;
4. one full-sweep algorithm;
5. one nonlinear benchmark with actual-cost and complete-work frontiers; and
6. a concise account of representation neutrality.

The broader historical NBO development can remain available as an archive or companion rather than carrying the burden of the main contribution.

## 5. A focused publishable route

The most promising new paper would be organized around the following claim:

> **Verified action contrasts, rather than global value error, are sufficient for safe incumbent-preserving policy improvement and finite-horizon accuracy.**

A credible paper could proceed in four steps.

### 5.1 Theory

State the safety theorem, finite-sweep accuracy recursion, coefficient sharpness, and action-null quotient structure in the most general economically meaningful expected-cost setting. Clarify the information and feasibility assumptions.

### 5.2 Constructive numerical certificate

Develop one practically computable contrast certificate. Give approximation, integration, arithmetic, and complexity bounds. Demonstrate that its cost is materially below recomputing a uniformly accurate policy value in at least one relevant class.

### 5.3 Full-sweep experiment

Run the algorithm from primitives through several improvement passes in a nonlinear constrained economy. Compare with strong policy-iteration/FVI alternatives. Use actual expected policy cost as the primary performance measure and the certified bound as a safety constraint.

### 5.4 Economic decision

Show a controller-replacement, information-acquisition, or policy-adoption decision whose conclusion changes because action-contrast certification admits an improvement that a global-width certificate rejects. Calibrate or otherwise justify the economic tolerance and implementation charge.

This would be a coherent numerical-method contribution. It would not require claiming that an exact ReLU encoding is computationally superior to the native representation.

## 6. Independent verification performed for this report

I performed the following checks against the pinned R52 snapshot.

1. **Branch and source identity.** I fixed the canonical branch at commit `e82e05e658d6aba9bb843dcece66410d1040a49a` and tree `0a5b4b0b2972b681aa0b67da7020c8a13b987a80`.
2. **Workflow artifacts.** I downloaded both R52 artifacts and verified SHA-256 digests:
   - `nbo-r52-paper-and-audits`: `a34df1b4a50d6c8fabbdfe76dc33ca37e2baabffb849ca328e419f66834d6905`;
   - `nbo-r52-complete-revision`: `c5d91ae956e72ce0dffb160d2aad8f6627e9e0e6c288f248a5caef525e1ec1db`.
3. **Final delivery.** I recomputed the hashes of all 1,037 files listed in `FINAL_DELIVERY52.json`; all matched.
4. **Publication audit.** I checked the five document page counts, 54-test total, clean-archive status, and absence of fatal compilation defects, undefined references, duplicate labels, missing characters, and overfull boxes.
5. **Source freeze.** I verified all six newly frozen scientific source hashes and all eight policy-checkpoint hashes.
6. **Full record replay.** I streamed every row of every compressed cell file: 524,288 cells and 4,194,304 gate decisions. I checked ordering, interval validity, feasibility, the contrast gate, all four scalar-width gates, summary counts, accepted upper bounds, and amplitude-invariant policy identity.
7. **Recomputed totals.** The replay gives 406,464 strict contrast-aware changes, 31,165 blocked changes, and 86,659 equal proposals. The strict-change fraction is approximately 0.77527. The old global-width gate accepts no strict change for any positive amplitude.
8. **Theory spot checks.** Exact rational arithmetic confirms the action cancellation `1/2 - 2(1/4) = 0` and the stated one-period sharpness example.
9. **Inherited economic evidence.** I rechecked the deposited R49 sign counts `93/0/3` and the later common-repair counts `26/0/1`, together with positive own-incumbent gains in all 27 groups.
10. **Scope.** I did not retrain, resimulate, recompile, or retime the services. New runs would constitute new observations. The verification script and its machine-readable output are included with this report.

## 7. Recommendation

R52 is mathematically and procedurally the strongest version of this project. It resolves the submission-completeness problem, identifies the correct decision-relevant critic error, supplies a plausible constructive certificate, and validates an exact action-null invariance with exceptional auditability. These are meaningful achievements.

They do not, however, establish the broad numerical-method claim required for publication in Econometrica. The new result is representation-neutral; its general computational burden is not characterized; the continuous benchmark executes only an exact-null terminal ablation; no new actual-cost observation is generated; full policy sweeps are not performed; the dimensional bottleneck remains; and the retained direct economic comparisons overwhelmingly favor FVI.

I therefore recommend **rejection in the present form and no further ordinary revision of the cumulative manuscript**. I would take seriously a new, focused submission on action-contrast-certified incumbent-preserving policy iteration, provided it executes the general certificate, supplies a complete complexity and work account, runs full sweeps in a substantive nonlinear economy, and evaluates actual policy cost as the primary endpoint.
