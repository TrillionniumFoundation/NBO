# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r46-review-ready-2026-10-08`  
**Pinned revision commit:** `c3930399e3b8267451096d0e70ea67f49510065e`  
**Pinned revision tree:** `42ac3db0d72ea030afb050754d2ae1da55864bc3`  
**Pinned main manuscript:** `revisions/2026-10-07-r46/ECTA.tex`, Git blob `a845355034c8bd117d397248479b218e4987cc72`  
**Pinned technical supplement:** `revisions/2026-10-07-r46/supp.tex`  
**Pinned response:** `revisions/2026-10-07-r46/response.md`, Git blob `cf6bac2c034ba224db6bd84a24fdf2476544883f`  
**Report date:** 8 October 2026  
**Recommendation:** **Reject in the present form and do not continue the cumulative manuscript through another ordinary revision round. A new, sharply focused paper on witness-preserving Bellman policy certification and deterministic Lipschitz–ReLU construction could merit evaluation, but R46 does not establish an Econometrica-level method-specific contribution for the broad Neural Bellman Operators program.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R46 is a substantial and careful revision. It repairs the publication-completeness defects of the intermediate R43 snapshot, materializes one review-ready article, supplement, response, code base, evidence archive, and clean-build audit, and retains the adverse findings from earlier rounds. The current submission is a coherent object rather than a protocol or a detached workflow artifact.

The principal mathematical addition is also real. The paper observes that the action attaining a Bellman label is useful information and retains that action through the minimum-of-cones continuation. A one-sided policy sandwich then combines the optimal Bellman-residual upper bound with the selected-policy residual directly. For the witness actor, the latter is controlled by the numerical query error rather than by a separate nearest-node actor allowance. I found no immediate algebraic contradiction in the one-sided comparison, the witness-selection proof, or the feasible-repair extension under their stated assumptions.

The result materially sharpens the paper’s deterministic certificate. In the executed scalar catalogue, the witness certificate is tighter than the same-critic nearest-node certificate in all 24 distinct economy-resolution comparisons and tighter than the strengthened spline certificate in 23 of 24. At the finest resolution, it reduces the bound relative to the nearest-node neural ablation by approximately 31.2–32.3 percent and relative to the spline by approximately 3.0–14.5 percent.

The difficulty is that the positive result remains a **certificate improvement for a classical Lipschitz-envelope construction**, not evidence that NBO is a superior or necessary numerical method.

The critic is the finite minimum of Lipschitz cones. The manuscript correctly credits the McShane-type extension and the elementary ReLU realization. The deployed actor is not a learned smooth neural output: it is a finite comparison index carrying the action attached to the active cone. The identical envelope and witness rule can be implemented without describing it as a neural network. Thus the completed result is a useful policy-certification construction, but its specifically neural content is representational rather than computational.

The matched evidence reaches the same conclusion. All three methods—cone witness, cone nearest, and spline nearest—have exactly the same first-crossing resolution in every economic cell and at every declared target. Each method certifies 12/12 services at targets 1/4 and 1/8 and 6/12 at 1/16; all horizon-four services miss the tightest target within the cap. The spline is faster than the witness construction in all 30 common successful target-by-repetition comparisons, while the witness is faster than the deliberately same-critic nearest-node ablation in all 30. No new direct expected-policy-cost experiment is performed for the witness policy. A tighter regret upper bound therefore does not establish a lower realized cost, an earlier target crossing, or a work advantage.

R46 is candid about these limitations, which is commendable. But candor does not by itself supply the missing Econometrica contribution. The executed study is scalar, exact-rational, grid based, and tensor-cover dependent. The state-dependent feasible-witness theorem assumes effective feasible nets and a measurable repair oracle and is checked algebraically rather than exercised in a comparative performance study. The retained controlled-diffusion, recursive-preference, endogenous-preference, temporal-self, and game programs do not receive the new witness construction or matching evidence.

I therefore recommend rejection in the present form. The witness-preserving theorem, the one-sided certificate, and the exact implementation could form the core of a narrower paper if the author isolates the non-neural baseline, supplies direct policy-value comparisons, demonstrates a genuinely multidimensional constrained problem, and aligns the title and economic claims with the result actually established.

## 2. What R46 successfully repairs

### 2.1 The submitted object is complete and immutable

The review-ready branch contains ordinary UTF-8 sources, compiled article, supplement and response, raw records, generated tables, source hashes, tests, preservation records, and clean-rebuild evidence. The final delivery audit records 737 verified files, 49 tests, and successful compilation of a 37-page article, 26-page supplement, and 10-page response with no undefined references, duplicate labels, missing characters, or overfull boxes.

This resolves the threshold objection to the incomplete R43 snapshot.

### 2.2 The one-sided policy comparison is the right mathematical object

The new proposition does not separately take absolute residual widths when the selected-policy residual and the optimal residual share the same fitted continuation. If
\[
 f_t-\mathcal T_t f_{t+1}\le u_t,\qquad
 \mathcal T_t^\pi f_{t+1}-f_t\le d_t,
\]
the policy gap is controlled by the discounted sum of \(u_t+d_t\), plus the terminal width. The account is invariant to date-specific additive shifts of the continuation.

This is a useful refinement of the earlier centered certificate.

### 2.3 The action witness is retained correctly

For the active cone
\[
 f_t(x)=y_{t,i}+L_t\|x-x_{t,i}\|_1,
\]
the construction deploys the original feasible action whose query attained \(y_{t,i}\). Transporting that same state-action pair gives
\[
 Q_t(f_{t+1};x,\pi_t^{\mathrm w}(x))-f_t(x)\le e_t.
\]
The implementation preserves original action identities through dominated labels, intersections, and ties. This closes a gap that would remain if the envelope values were regularized without retaining their attaining actions.

### 2.4 The conventional comparisons are strengthened rather than held fixed at a weak certificate

The nearest-node neural ablation and the spline receive a one-sided cellwise allowance computed from the complete set of knots, state nodes, and nearest-cell boundaries. The paper therefore does not compare the witness theorem only against the older separated bound.

This is an appropriate response to the prior referee’s concern about weak comparators.

### 2.5 The new experiment is prospective relative to the execution

The protocol fixes the economic cells, methods, grid ladder, targets, repetitions, failure treatment, and work boundary before the 36-service execution. All 216 rungs are retained. The actor change is correctly treated as a new policy rather than as recertification of an old one.

### 2.6 State-dependent feasibility is treated explicitly

The feasible-witness theorem no longer transports a node action into a state where it may be inadmissible. Under a Hausdorff-Lipschitz feasible correspondence, effective feasible nets, and a certified measurable repair, the bound charges action-net error and repair displacement in addition to query and state-cover errors.

The assumptions are strong, but the mathematical obligation is visible.

### 2.7 Adverse evidence is preserved

The paper reports:

- identical first-crossing resolutions for all three methods;
- six tight-target failures for each method;
- one frontier point where the spline certificate is tighter;
- spline clocks lower in all 30 common successful comparisons;
- no new direct policy-cost ranking;
- the earlier unresolved paired intervals;
- and the adverse adaptive-precision result.

This is exemplary disclosure.

## 3. Blocking concerns

### B1. The distinctive construction is not specifically neural

The positive theorem uses a classical minimum of Lipschitz cones. Its exact ReLU realization is mathematically correct, but it does not create a method-specific neural advantage. The deployed policy is a finite comparison selector returning an attached action index; it is not a neural actor trained from data.

An equivalent implementation can store the cone parameters and perform the same comparisons without a neural-network abstraction. It would return exactly the same continuation, witness policy, certificate, and work up to representation-level constants.

The paper should therefore distinguish:

1. the classical Lipschitz-envelope algorithm;
2. its exact ReLU circuit representation; and
3. any computational advantage attributable to the neural representation.

R46 establishes the first two. It does not establish the third.

### B2. The certificate improvement does not improve the declared work-to-target frontier

The central empirical fact is that every method has the same first-crossing resolution for every economic cell and every target. The witness construction’s tighter bound never moves a crossing to an earlier rung on the predeclared ladder.

At common successful targets:

- witness versus cone-nearest: witness is faster in 30/30 comparisons;
- witness versus spline: witness is faster in 0/30 comparisons.

The primitive Bellman-query counts are also the same at common crossings because the methods traverse the same state/action ladders. The positive empirical finding is therefore a sharper bound at a fixed resolution, not a better certified work-to-target service than the spline.

For a numerical-method paper, this distinction is decisive.

### B3. R46 does not compare the new witness policy’s actual economic cost

The witness selector is a new deployed policy. Its policy value is not compared directly with the spline policy or the nearest-node policy in the new catalogue.

The paper correctly states that a tighter regret upper bound does not rank realized policy costs. The prior direct comparisons do not fill the gap:

- the earlier scalar signed comparisons frequently favored the spline;
- the coupled neural-minus-ridge intervals all contained zero; and
- those comparisons concern different policies and experiments.

A predeclared, paired direct expected-cost comparison for the witness policy is necessary before the certificate advantage can be interpreted as an economic method advantage.

### B4. The completed numerical evidence remains scalar and tensor-cover dependent

The executed witness catalogue has one state, one action, horizons two and four, and resolutions up to 512. The theorem’s direct-cover work retains factors of order \(h^{-d}\) and \(k^{-a}\). Nothing in the result removes the curse of dimensionality.

The two-state capacity-constrained example in the feasible-witness section is an algebraic admissibility check, not an executed work-to-accuracy study. Earlier two-state nonlinear experiments used different learned continuations and do not validate the new witness backend.

The paper therefore lacks a genuinely multidimensional nonlinear benchmark for its new central construction.

### B5. The constructive theorem assumes computational primitives that can contain the hard part

Finite termination requires:

- certified state and action covers at arbitrary positive radii;
- Bellman-query enclosures to arbitrary positive tolerance;
- certified integration of the innovation law;
- effective feasible action nets;
- and, for state-dependent constraints, a feasible measurable repair with a known displacement bound.

These are valid sufficient assumptions. But they are not innocuous. In many economic control problems, certified integration, feasible covering, or repair is the principal computational problem.

The paper gives an explicit work expression, which is useful, but no complexity result showing that these oracles are cheaper than a conventional dynamic-programming construction in the classes motivating the broad NBO program.

### B6. The deployed actor and numerical-selection contract are not exercised under realistic acquisition and arithmetic

The reference implementation uses exact rational switchpoints and exact state acquisition. The actor is a discontinuous finite selector. The theorem contains allowances for approximate indices, state error, action error, and feasible repair, but the executed catalogue does not stress those allowances.

A practical deployment must specify:

- how the state is acquired;
- how rational switchpoints are represented and compared;
- how ambiguous cells are handled;
- how the action witness is stored and repaired;
- and how the resulting execution error is certified on ordinary hardware.

Without such an execution, the numerical implementation result remains an exact construction laboratory.

### B7. The timing and work evidence is too narrow for a general efficiency conclusion

The study uses three local repetitions of deterministic objects. CPU frequency is uncontrolled. Exact rational compilation, parsing, and serialization are included, but the reported primitive counts are explicitly not floating-point operation counts or bit complexity.

The local timing finding is nevertheless clear: the spline is faster. What is missing is a stable scaling account explaining how the methods compare as dimension, horizon, target tolerance, label precision, and constraint complexity change.

Repeated scalar clocks cannot support a general numerical-method claim.

### B8. The economic application does not supply an Econometrica-scale substantive result

The new catalogue is a stylized investment laboratory used to compare certificates. It is not calibrated, estimated, or tied to a substantive policy counterfactual. The new witness evidence does not change the actual policy-cost conclusions.

A top-journal numerical method may be valuable without empirical calibration, but it should then solve a computationally consequential economic problem or establish a broadly useful efficiency frontier. R46 does neither.

### B9. The broad platform framing remains disproportionate to the completed result

The active paper retains controlled diffusions, recursive preferences, endogenous preferences, temporal selves, and games as part of the NBO program. The witness theorem, however, is executed only for a compact finite-horizon expectation problem with a common scalar action set; the state-dependent extension remains theoretical.

Preserving historical applications is legitimate. Presenting them as coequal support for the current numerical-method contribution is not. The title and contribution list still suggest a general platform that the R46 evidence does not establish.

## 4. Major comments and required changes

### M1. Isolate a non-neural implementation of the identical witness envelope

Run the same cone-and-witness algorithm as a conventional min-plus/Lipschitz dynamic-programming method. Use the same data structures, selector, arithmetic, and certificate. This is the correct baseline for identifying whether the ReLU representation adds anything computationally.

### M2. Add a predeclared direct policy-cost comparison

For every common first crossing, compare witness, nearest-cone, and spline policies on common innovation paths. The estimand should be the actual policy-cost difference, not the difference of regret bounds. Prespecify superiority or equivalence margins in economic units.

### M3. Use a finer target ladder or continuous work-to-bound curves

The coarse targets \(1/4,1/8,1/16\) conceal the fact that the witness certificate is often tighter without changing the first crossing. Report work as a function of the achieved certified bound, or use a denser predeclared target grid.

### M4. Execute the state-dependent feasible-witness construction

The new theorem should be tested on a genuinely state-dependent action set where repair is nontrivial and its work is material. Compare exact repair, approximate repair, and a conventional constrained dynamic-programming baseline.

### M5. Provide a multidimensional nonlinear benchmark

At minimum, execute the witness backend in a coupled two- or three-state nonlinear economy with continuous uncertainty and state-dependent constraints. Include sparse-grid, adaptive-partition, fitted-value, or approximate-policy-iteration comparators.

### M6. Report realistic execution error

Implement the selector with finite-precision state input and ordinary numeric comparisons. Exercise ambiguous switchpoint handling and action repair. Report the additional certificate and work, rather than leaving these as theorem-only allowances.

### M7. Give a total complexity statement

The work account should combine cover sizes, Bellman queries, innovation integration, circuit construction, selector queries, repair, storage, arithmetic precision, and verification. State explicitly when the neural representation improves any term relative to the identical non-neural envelope.

### M8. Separate theorem reliability from finite-cap performance

The unbounded deterministic construction terminates under strong effective-computability assumptions. The finite catalogue has its own capped attainment. Keep these objects separate and quantify the cap required as a function of tolerance and dimension.

### M9. Align the economic claim with the evidence

Either produce an economic result that depends on the witness construction, or present the paper as a numerical certification contribution. The current investment example does not justify the breadth of the economic framing.

### M10. Further focus the publication

A focused paper should contain one model class, one witness construction, one implementation contract, one direct policy-value experiment, and one multidimensional constrained benchmark. The preserved historical program can remain in an archive rather than carrying the main publication’s contribution claim.

## 5. A focused publishable route

A credible new submission could center on:

> **Witness-Preserving Bellman Certification for Lipschitz Dynamic Programs**

The core would be:

1. the one-sided policy sandwich;
2. the action-witness construction;
3. the feasible-repair extension;
4. an exact or verified finite-precision implementation;
5. a non-neural identical-envelope baseline;
6. direct policy-cost comparisons;
7. multidimensional constrained experiments; and
8. complete work-to-certified-accuracy curves.

The paper should describe the ReLU circuit as one exact implementation of the envelope, not as evidence that a generic neural optimizer has solved the problem. That narrower contribution is mathematically coherent and potentially useful.

## 6. Independent verification performed for this report

I performed the following checks against the pinned R46 snapshot and its source-bound study artifact.

1. **Artifact identity.** The downloaded artifact `nbo-r46-study` has SHA-256  
   `8cb0fa519bb5e9c15760541d29ca3af5312e73ca728a39ea81a5fc521ba7235a`, matching the GitHub artifact digest.
2. **Frozen sources.** All three study-source hashes in `EXECUTION_FREEZE.json` match.
3. **Complete catalogue.** I verified 36 service records, 216 checkpoint files, and every checkpoint hash referenced by its service record.
4. **Attainment.** Each method reaches 1/4 and 1/8 in 12/12 services and 1/16 in 6/12.
5. **First crossings.** All methods have identical first-crossing resolutions in every cell and target; repetition checkpoints are identical.
6. **Certificate comparisons.** The witness bound is tighter than cone-nearest in 24/24 distinct frontier rows and tighter than spline in 23/24.
7. **Finest-grid reductions.** Relative to cone-nearest, the witness bound falls by approximately 31.20–32.27 percent. Relative to spline, it falls by approximately 2.99–14.50 percent.
8. **Timing comparisons.** At common successful targets, witness is faster than cone-nearest in 30/30 comparisons and faster than spline in 0/30. Across the four full-frontier median clocks, witness is about 4.48–11.06 percent slower than spline and 18.30–21.20 percent faster than cone-nearest.
9. **Shift invariance.** An independent exact-rational spot check confirms that the one-sided gap account is invariant to arbitrary date-specific continuation shifts.
10. **Publication gate.** The repository records 49 tests, a clean rebuild without network access or reexecution, and clean 37-, 26-, and 10-page article, supplement, and response documents.

I did not rerun or retime the study. A new execution would create new timing observations. The review directory includes a standard-library audit script and its machine-readable output.

## 7. Recommendation

R46 is the strongest and most coherent version of the project I have reviewed. The action-witness idea is useful, the one-sided policy account is mathematically well motivated, the feasible-repair extension addresses a real obligation, and the repository’s evidentiary discipline is excellent.

The remaining problem is substantive. The new construction is a classical Lipschitz envelope with an exact ReLU representation and a finite action-index selector. Its tighter certificate does not change any declared target crossing, does not lower recorded work relative to the spline, and is not accompanied by a direct policy-cost advantage. The executed evidence remains scalar, exact-rational, and stylized; the state-dependent and broader economic extensions are not comparably executed.

I therefore recommend **rejection in the present form and no further ordinary revision of the cumulative manuscript**. A new, sharply focused submission on witness-preserving Bellman certification, with a non-neural identical-envelope baseline, direct policy-cost comparisons, and a multidimensional constrained benchmark, could merit serious evaluation.
