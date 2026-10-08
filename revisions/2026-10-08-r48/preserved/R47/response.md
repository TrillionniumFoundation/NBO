# Response to the Referee: Neural Bellman Operators

**Revision:** R47, 8 October 2026.  
**Report addressed:** R46, review commit `0bf1ff6060bb9211762f191b6ead306ae4725beb`.  
**Reviewed manuscript:** `c3930399e3b8267451096d0e70ea67f49510065e`.  
**Author:** Qian QI.

We thank the referee for identifying the distinction between an exact representation, a certified construction, and a competitive economic implementation. We have revised the existing *Neural Bellman Operators* paper. Its title, controlled-economy subject, earlier theorems and applications are retained. The revision does not replace the paper by the narrower subject suggested in the report. Instead, it supplies new theory, direct policy-value evidence, a constrained two-state construction, and an executed acquisition contract within the original framework.

The principal theorem now bounds a witness policy implemented from an acquired state with error. It combines a certified numerical index, feasibility throughout the acquisition set, action quantization, and the one-sided Bellman account. No continuity of the actor is assumed. A causal-information condition makes explicit that observations cannot reveal future innovations while leaving the economic comparator unchanged. For capacity constraints the repair and its displacement budget are constructive.

The direct comparison now evaluates the actual R46 witness, nearest-cone and spline policies at every common original target crossing. The protocol fixed 120 contrasts, four initial-state laws, 131,072 common paths per group, family error 0.01 and a separate decision tolerance 1/1024 before execution. All 120 simultaneous intervals lie within that predeclared band. They all also contain zero. We therefore establish cost proximity at the stated tolerance for the declared initial laws, not a signed cost advantage or equality inferred from insignificant differences. The normative tolerance is not described as a calibrated welfare equivalence.

A second experiment constructs fresh policies in a coupled two-state, continuous-innovation economy with state-dependent investment capacity. Feasible cone witnesses and bilinear fitted-value iteration generate their own future labels on the same fixed ladder. All 24 services and 72 rungs are deposited. Twelve distinct witness policies are additionally tested in 72 acquired-state and action-quantization cases. There are 36,070 active repair events across these cases, and the numerical and measurement allowances are included in the policy bound.

The evidence remains mixed. Both constrained generators reach the coarse target 4 in all twelve services, but neither reaches 2, 1 or 1/2 within the declared cap. The witness's final bound is smaller in each cell, whereas bilinear fitted-value iteration is faster at every common crossing. The original scalar targets still have identical crossing resolutions. The complete scalar step functions, however, identify 19 nonempty tolerance intervals on which both methods attain and the witness uses fewer Bellman queries, one favoring spline, and twenty with equal counts. These are a complete descriptive reconstruction, not favorable new targets chosen after the experiment.

The responses below distinguish an addressed mathematical obligation, an executed experiment, and an economic or comparative claim not established by those results. Passing the tests and publication gates is not an editorial decision.

## Blocking concerns

### B1. The construction is not specifically neural

The new proposition, *Representation control*, states equality of the native min-plus envelope and its affine–ReLU realization when parameters, original action witnesses and the tie rule are the same. We execute the conventional representation on all 24 distinct R46 scalar checkpoints. The diagnostic evaluates 96 fitted date-functions on 1,025 dyadic points each. Native and ReLU evaluations agree in the recorded binary64 outputs; a separate arithmetic budget bounds possible discrepancies. The equality of the mathematical functions and actors is proved algebraically, not inferred from this grid.

The two encodings share the same construction data. They are not counted as independently trained competitors, and a gate microdiagnostic is not represented as a complete-work speed study. Their covering, query and leading work factors are identical. This directly isolates the representation component requested by the referee. It also prevents an unsupported attribution of a classical envelope's performance to its neural name.

NBO remains the subject because the paper studies policy-specific continuation operators, neural constructions and their feasible execution. The earlier learned-hidden-location methods are different generators and retain their separate evidence. The deterministic theorem and its executable guarantee do not require a claim that every generator has a uniquely neural advantage. We have not asserted such an advantage where the identical native representation rules it out.

### B2. The certificate improvement does not change the declared frontier

The original first crossings and failures are unchanged. We now reconstruct the full first-crossing function over the entire positive tolerance axis from every recorded scalar rung. The union of the two methods' exact rational bounds defines 48 intervals below the largest breakpoint in each cell. There are 19 intervals on which both attain and the witness uses fewer prefix Bellman queries, one on which spline uses fewer, twenty with equal query counts, four where only witness attains, and four where both exhaust the cap. Above each largest breakpoint both use the first rung.

Every interval, including the unfavorable one, is reported in the supplement and machine-readable records. Prefix work includes all preceding failed resolutions. Interval counts are not interpreted as probabilities or economically weighted measures. No target from these curves is substituted into the original prospective attainment table. Thus the revision identifies exactly where certificate sharpness changes a resource decision while preserving the referee's observation about the original coarse targets.

### B3. The actual witness policy cost has not been compared

This gap is now addressed by a new fixed-design execution. We load the actual saved policies, not newly trained substitutes, at all ten common economy/target crossings. The primary initial law is uniform on the full scalar state interval; fixed states 1/8, 1/2 and 7/8 are additional declared estimands. Three pairwise contrasts at each of forty groups yield 120 direct comparisons.

The own-continuation Bellman telescoping score has expectation equal to actual expected policy cost. Its deterministic support uses signed optimal and selected-policy residuals, the range of the initial continuation difference, and terminal differences. It is not the difference of two regret upper bounds. Forty-bit innovation bins preserve the continuous economic law through interval enclosure. Ambiguous actor choices are enclosed rather than discarded: 3,932,160 actor-query ambiguities are recorded among 44,040,192 actor queries. Mean, variance, logarithm and square-root calculations have explicit conservative arithmetic accounts.

All 120 intervals are contained in the ex ante band ±1/1024 at simultaneous confidence at least 0.99 under the stated independent-bin model. The largest absolute endpoints are approximately 0.00011613 for witness–nearest-cone, 0.00019755 for witness–spline, and 0.00020777 for nearest-cone–spline. All signed comparisons remain unresolved because every interval contains zero. This supplies a valid tolerance-based economic comparison, not evidence of a lower witness cost. The fixed pseudorandom stream provides reproducibility; the statistical theorem explicitly states its sampling assumption.

### B4. The evidence remains scalar

The new construction study executes a coupled two-state economy, horizons two and three, continuous common uncertainty with opposite state exposures, nonlinear transition terms, nonlinear adjustment cost, a shortage penalty, and investment capacity depending on both current state coordinates. Both the feasible witness and conventional bilinear fitted-value iteration use their own fitted future. The common ladder is 4, 8 and 16 subdivisions. Three isolated repetitions per method and economic cell give 24 services and 72 rungs.

The state-dependent construction is therefore no longer supported only by an algebraic example. The new conventional comparator is fitted-value iteration, as requested among the admissible comparison families. It is not described as a sparse-grid or adaptive-partition method. Two dimensions do not establish a high-dimensional frontier; tensor coverage and the numerical costs remain explicit. The tight capped failures are reported rather than replaced by a sufficient-budget theorem.

### B5. The theorem assumes hard computational primitives

For the new economy, every relevant primitive is explicit. The revision proves invariance, state and action Lipschitz moduli, effective finite state and feasible-action covers, the measurable capacity repair, and a midpoint remainder for the original continuous innovation law. At a shock resolution M, the deterministic integration remainder is L/(32M) for a continuation with modulus L. Outward numerical evaluation and label rounding are additional errors, not substitutes for this remainder.

The primitive recursion gives a horizon-uniform continuation modulus because its coefficient is 705/1024. The new cap formula bounds the policy loss by C/N plus explicit numerical terms and gives a sufficient dyadic resolution as a function of tolerance. It also distinguishes arbitrarily accurate arithmetic from the fixed binary64 study. This removes the hidden-oracle objection for this particular class while keeping the general theorem's effective-computability hypotheses visible.

The direct cone implementation has a larger leading evaluation count than bilinear fitted-value iteration. The resource statement does not claim that the explicit operations are cheaper merely because they can be written as a neural circuit.

### B6. Realistic state acquisition and selection are not exercised

The new acquisition-aware theorem allows a discontinuous witness index. A numerically selected cone may exceed the exact minimum by a certified amount. The state is represented by an acquisition set containing the true state, and the action is required to be feasible throughout that set. The resulting selected-policy residual adds the numerical index allowance, twice the continuation modulus times the acquisition radius, and the objective cost of robust repair and quantization.

The deployed tests use ordinary binary64 score comparisons on dyadic measured inputs with coordinate radii zero, 2^-12 and 2^-8, exact robust repair or downward action spacing 2^-12, and all twelve distinct constrained witness policies. Each of the six configurations includes 32,670 state–date queries. All actions are feasible throughout their corresponding acquisition boxes. Robust repair is active in 36,070 case-query events; quantization changes 6,609 recorded actions in the fine nonzero-acquisition configuration. A uniform arithmetic theorem supplies the selection allowance. The measurement grid exercises the implementation but is not used as a substitute for an all-state proof.

For the scalar value comparison, rational switchpoints are enclosed outward and every intersecting actor cell is included. The numerical contrast thus exercises actual ambiguity handling as well as the separate boundary regressions. These contracts are stated for the declared dyadic input format; other sensor or floating-point formats require their own distance-formation allowance.

### B7. The work and timing evidence is too narrow

The revision supplies the full scalar work-to-bound step functions, a new constrained dimension, and a total explicit operation account for the specified routines. With two state coordinates, one action and one shock, direct cone construction has O(T N^6) work and bilinear fitted-value iteration O(T N^4), while both store O(T N^2) labels and actions. The account includes feasible action nets, own-future query construction, continuous-law integration, representation evaluation, cell verification, selector queries, acquisition repair, arithmetic precision and serialization.

The new local observations favor the conventional implementation at all twelve common constrained crossings. We report medians and ranges from three isolated processes, fixed CPU affinity and single-thread numerical libraries. CPU frequency is not controlled. Primitive-object counts are not relabeled as exact FLOP counts or bit complexity. Direct-cost evaluation has a separate new process clock and is not added to historical construction clocks from another host to manufacture a matched end-to-end timing result. A general neural efficiency advantage is not established by these measurements.

### B8. The economic application does not establish a substantive result at the claimed level

The new theorem and experiment support concrete economic uses within the declared normalized models. The acquisition result certifies feasibility and a loss account for a policy that is actually implementable with uncertain state information and capacity constraints. The scalar direct comparison establishes cost proximity at a predeclared decision tolerance under a full initial-state distribution, rather than only comparing certificates. A finite-catalogue adoption theorem then permits selecting by upper cost difference plus a known implementation charge while retaining the simultaneous uncertainty account.

These are policy-evaluation and decision results, not a new estimated counterfactual or evidence of neural indispensability. The tolerance is a stated preference over numerical decision error, not a calibrated welfare margin. The two-state tight targets remain unachieved and no direct policy-value study of those new constrained policies is claimed. The current evidence therefore advances the original economic methodology without pretending to supply the calibrated application the referee describes.

### B9. Broad platform scope exceeds the executed result

The revision keeps the original controlled-diffusion, recursive-preference, endogenous-preference, temporal-self and game developments and their application-specific hypotheses. It does not count their preservation as new empirical support. The common monotone cash-invariant comparison governs the acquisition theorem under its causal conditional-evaluation assumptions. The direct sampling theorem uses conditional expectation and is visibly restricted to that case.

The active article now contains the primitive construction, execution contract and direct-cost results needed for its new argument. The supplement supplies their proofs and all comparison tables. Historical companions remain preserved, but the new results do not require treating an old application as an unperformed R47 experiment. The title is retained as requested by the scope of this continuing paper; its contribution statements distinguish these objects explicitly.

## Major comments

### M1. Isolate an identical non-neural implementation

Completed as an explicit native min-plus control, an all-state representation-equivalence proposition, and ordinary numerical gate tests on all 24 witness checkpoints. The same original parameters, action witnesses and tie rule are used. Shared construction is not counted twice. No representation-specific speed benefit is inferred.

### M2. Add a predeclared direct comparison

Completed for all common original first crossings and all three policy pairs. The protocol commit precedes source freezing and execution. The zero superiority threshold, separate 1/1024 decision tolerance, initial laws, path count and family error are unchanged. All 120 exact intervals and endpoint statistics are deposited. The new theorem distinguishes signed superiority, tolerance-based proximity and adaptive catalogue choice.

### M3. Report continuous work-to-bound curves

Completed as exact step functions on the full union of rational certificate breakpoints, with all failures and every favorable or unfavorable interval retained. These are explicitly descriptive curves of the frozen R46 frontier, not a new prospective target list. They complement rather than rewrite the original first-crossing table.

### M4. Execute state-dependent feasibility and repair

Completed in the new coupled capacity-constrained economy. The construction uses feasible node nets and the explicit repair at the current state. The deployment study compares exact robust repair with downward quantized repair and includes acquisition uncertainty. Active repairs and quantization changes are reported, along with the added certificate and query work. The bilinear conventional policy is repaired against the same true capacity.

### M5. Provide a multidimensional nonlinear benchmark

Completed at the requested two-state minimum with continuous uncertainty, nonseparable nonlinear dynamics and state-dependent constraints. Bilinear fitted-value iteration is the conventional comparator. All 72 rungs are preserved. This does not establish performance in dimensions where tensor coverage is infeasible, and no unexecuted sparse-grid comparator is claimed.

### M6. Report realistic execution error

Completed for the declared binary64/dyadic acquired-input contract and the original scalar interval selectors. The theorem does not assume that the discontinuous actor is Lipschitz. Feasibility holds throughout the acquisition set, not only at measured inputs. Conversion, score arithmetic, index excess, robust repair and action quantization enter explicit bounds. Causal observation conditions are now stated.

### M7. Combine all complexity terms

The new resource subsection gives covering, feasible-action, integration, representation, selection, repair, storage, numerical-precision and verification costs. The native and ReLU versions of the identical envelope have equal leading terms. The explicit two-state implementation exposes, rather than hides, its larger direct-envelope evaluation factor relative to bilinear fitted-value iteration.

### M8. Separate mathematical termination and finite-cap outcomes

The sufficient cap follows from primitive moduli and a tolerance allocation, including numerical accuracy. The fixed three-rung experiment has its own attainment array: each generator reaches 4 in 12/12 services and reaches none of the tighter targets. Neither object is substituted for the other. Acquisition consumes an additional part of the same tolerance budget.

### M9. Align economic claims with the evidence

The article now states two implemented economic conclusions: feasible acquired-state policy execution with a full loss account, and direct scalar policy-cost proximity at a prespecified tolerance. The adoption theorem makes the latter usable for catalogue choice under simultaneous uncertainty. These are not described as calibration, universal neural superiority or a counterfactual unavailable to traditional methods.

### M10. Further focus the publication

We have retained the same NBO paper rather than changed its topic. Within that paper, the new argument has a clear progression: an acquired-state policy, a uniform feasible-execution theorem, a fully specified constrained construction, and a direct policy-value decision. The supplement contains the proofs, complete tables and resource details. Earlier claims and applications are preserved with their original conditions; all prior active LaTeX labels are retained. The preservation audit makes the change boundary explicit.

## Reproduction and scope

The protocol was committed at `7d2329406b53047eb6fa35fe366d94f2fcb37a12`; scientific source was frozen at `04d0638169ae7adbdd8bb21f9d1fea5b1ef68de2`. Workflow `37663771622` completed the fixed execution and pushed evidence commit `4da0b2c286793f75a56ad6d8228cb0da82aabc60`. The study artifact's SHA-256 is `782e437ccb4886a18f6692b02d0e4a109abe67d729e53f5c266cf1f5df2428db`.

The publication build reconstructs all 120 direct intervals and all 72 constrained rung bounds without resimulating, retraining or rewriting clocks. It verifies checkpoint hashes, identical repetitions and the five frozen scientific sources; reruns the inherited 49 tests and the 20 new regressions; and compiles the article, supplement and this response. The previous manuscript, reviews and evidence are untouched. The new active sources and PDFs are materialized on a fresh review-ready branch. Clean rebuilds require the pinned repository inputs, not a still-live workflow artifact.

The first workflow trigger preceded the source-hash manifest and stopped at its existence guard without executing a study. The subsequent manifest-bound full run completed without a scientific-source amendment or protocol retuning. Development fixtures are excluded from empirical clocks. Details and immutable source identities are recorded in the development disclosure and release audit.
