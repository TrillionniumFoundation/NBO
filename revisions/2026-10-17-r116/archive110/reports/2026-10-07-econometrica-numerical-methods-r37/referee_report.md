# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r37-review-ready-2026-10-07`  
**Pinned revision commit:** `9792d3dee69351f672dcc09098422b35207060a7`  
**Pinned revision tree:** `df6abbbd45f46c0aed6b1345a895e3e33ce6c503`  
**Pinned main manuscript:** `revisions/2026-10-07-r37/ECTA.tex`, Git blob `7eb470685079f8d9a761aaca118298a3d9656aad`  
**Pinned technical supplement:** `revisions/2026-10-07-r37/supp.tex`, Git blob `7a01a77fb29f5151296c64ab0eb7246b975cc942`  
**Pinned response:** `revisions/2026-10-07-r37/response.md`, Git blob `e4249020d498251a63060ea4a2a1bd619a9b4c40`  
**Report date:** 7 October 2026  
**Recommendation:** **Reject in the present form. A new, substantially narrower paper on certified finite-precision continuation construction in risk-sensitive linear-quadratic control could merit evaluation, but the present manuscript does not establish an Econometrica-level numerical method for the broad NBO program.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R37 is a serious and technically much stronger revision. It is no longer an unfinished workflow, a collection of aspirational theorem statements, or a paper whose positive claims depend on hiding unfavorable comparisons. The current branch provides a coherent 45-page article, a 35-page active technical supplement, a point-by-point response, source-frozen evidence, a preservation ledger, and current native publication entry points. The author explicitly distinguishes three objects that previous versions often blurred: a certificate for a returned policy, a theorem constructing an admissible continuation, and an empirical comparison of complete work.

The new mathematical core is also credible. In whitened coordinates, the proposed refresh is a Newton--Schulz polar iteration. The paper does not claim that classical matrix iteration as new. Instead, it gives a deterministic perturbation account for rectangular factors and noncommuting initial Gram matrices, allocates whole-step implementation error, derives a finite update cap and a fractional-storage bound, and connects the resulting Gram allowance to an all-action, all-state policy-loss certificate in a finite-horizon entropic linear-quadratic economy. I checked the central identity
\[
\bar Y^\top\bar Y-I=(-3E^2+E^3)/4
\]
and the perturbation step used to obtain the squared error envelope. I found no immediate algebraic contradiction in that theorem or in its use inside the stated warm-start policy budget.

The revision therefore deserves credit for resolving many earlier correctness and provenance objections. The remaining problem is not that the new result is false or undocumented. It is that the successful result is far narrower than the paper's title, applications, and Econometrica-level numerical-method ambition.

The trainable continuation in the complete theorem is a square-activation network that represents a quadratic form exactly. Its hidden-weight update is a matrix-factor iteration for a positive definite target that is itself available from analytic Gaussian evaluation. The actor is obtained from a quadratic linear system. The comparison economy is a risk-sensitive linear-quadratic Gaussian model for which a structural Riccati procedure solves the policy exactly and is substantially faster. The new experiment has dimension two, four decision dates, two closely related valuation matrices, exact rational products and solves, no simulated transitions, and eight deterministic services. It demonstrates that one carefully designed neural factor construction terminates and can be certified. It does not yet demonstrate that Neural Bellman Operators solve an economically important problem that strong conventional methods cannot solve, or that the new construction gives a work-to-accuracy advantage over a contribution-isolating baseline.

The most favorable numerical comparison is also not cleanly attributable to precision adaptation. The reported “adaptive-cached” procedure combines two changes: adaptive factor precision and reuse of a fixed target inverse within a fit. The inherited fixed-precision quadratic implementation rebuilds that inverse at every update. In the anchor economy both procedures take six hidden updates, but the fixed implementation builds six target inverses while the adaptive-cached implementation builds three. There is no fixed-precision cached baseline, no adaptive-precision uncached baseline, and no fixed-precision baseline tuned to the lowest precision that attains the common economic target. Consequently, the measured clock difference does not isolate the contribution named in the theorem.

Moreover, all nonstructural procedures oversolve the declared \(10^{-4}\) policy tolerance by at least roughly five orders of magnitude: the largest reported nonstructural gap bound is approximately \(1.01\times10^{-9}\). The complete-service clocks are single sub-quarter-second observations. The adaptive procedure is about 9.8 percent faster than fixed quadratic refresh in the anchor service and 12.4 percent faster in the changed-valuation service, but those differences are not supported by repeated timing, machine-independent operation counts, or a total bit-complexity analysis. The structural procedure remains about 5.1 times faster in the anchor service and 20.5 times faster in the changed service.

My recommendation is therefore rejection in the present form. The new theorem could support a focused paper, particularly if the author isolates the algorithmic contribution, develops a realistic floating-point implementation and complexity analysis, and demonstrates it on a genuinely nonlinear or otherwise nonstructural economic problem. The present manuscript, however, still asks one exact quadratic construction to carry a broad paper on controlled diffusions, recursive utility, endogenous preferences, temporal selves, and games.

## 2. What R37 successfully repairs

The negative recommendation should not obscure substantial progress.

### 2.1 The current submission is a real, reviewable object

The root entry points identify R37 rather than silently pointing to an older revision. The current article, supplement, response, applications companion, historical article, and historical supplement are separately identified. The release audit pins the R21 report, the science-freeze commit, the evidence commit, and the publication source. The compilation audit reports no undefined references, duplicate labels, missing characters, or overfull boxes in the current article and active supplement.

This resolves the threshold problem that affected several earlier revisions: the referee is now reviewing one immutable source-and-evidence snapshot.

### 2.2 The precision theorem is stated at the correct perturbation level

The theorem does not pretend that rounding only the final stored factor covers errors in all preceding matrix operations. It assumes a whole-step perturbation bound and proves that
\[
 \|E_{j+1}\|_2\leq c_r\rho_j^2+2\nu_j+\nu_j^2\leq\rho_j^2.
\]
The argument accommodates rectangular factors and does not require the initial Gram matrix and target to commute. The proof correctly gets commutation only after rewriting the ideal Gram update as a polynomial in the single symmetric error matrix.

The theorem also distinguishes its general deterministic perturbation statement from the more specialized exact-products-plus-entrywise-rounding bit schedule. This distinction is mathematically important and is stated honestly.

### 2.3 The paper closes a genuine policy-comparison chain in the declared model

The strongest positive advance over R21 is not merely the matrix iteration. The article now combines:

1. own-policy recursive evaluation;
2. an all-action residual;
3. an entropic Gaussian moment-domain account;
4. separate quadratic and state-independent propagation allowances;
5. a primitive policy-error allocation;
6. an evaluation-radius allowance;
7. a factor-training allowance;
8. an actor-equation allowance; and
9. an independent Bellman subsolution check.

Within the stated finite-horizon recursive-risk linear-quadratic economy, this is a real full-policy result. The comparator is all adapted policies of finite recursive cost and all real vector controls, not a finite action catalogue or the neural policy class. The coefficient inequalities cover all states rather than sampled states.

### 2.4 The training theorem avoids an obvious circularity

The primitive envelope, initialization scale, step size, stopping allowance, and finite cap are selected before the realized own-policy target is supplied. The returned future policy is finalized before its continuation is evaluated. This is materially better than using a successful fitted policy to justify the assumptions under which it was trained.

The paper also distinguishes cold construction, a gradient--curvature criterion, and warm construction. It does not silently transfer a fixed-feature regression theorem to a jointly trained network. Every entry of the square factor can change.

### 2.5 The evidence retains unfavorable comparators and failed historical checks

The earlier finding that check-and-refresh costs more than fresh neural refitting in every one of eight changed-future cells remains visible. Cached sample-average optimization remains the cheapest fully certified method in those cells. The structural risk-sensitive linear-quadratic solution is retained in the new experiment and is much faster than all neural constructions. The author does not reinterpret these adverse results as victories.

This is good computational practice.

### 2.6 The evidentiary language is appropriately limited

The eight new services are called deterministic construction objects, not population samples. The paper does not pool overlapping algebra tests as independent economic observations. It labels process high-water memory correctly, distinguishes training-target inverse constructions from applications, and states that stored fractional precision is not total rational bit complexity.

### 2.7 The presentation is materially improved

The active article is 45 pages and the active supplement 35 pages. The old 51-page article, 232-page supplement, and 48-page applications companion remain accessible but are labeled separately. The current argument can now be read without reconstructing thirty-seven revision branches.

## 3. Blocking concerns

### B1. The new “neural” theorem is an exact quadratic matrix-factor construction, not yet a general numerical method for NBO

The complete constructive result concerns
\[
 \widehat U(x)=\|Wx\|^2/d+c,
\]
so its continuation class is precisely the cone of positive-semidefinite quadratic forms represented through a factor. The target matrix is computed from an analytically evaluable Gaussian quadratic continuation. The update is a classical polar/Newton--Schulz factor iteration.

Calling the factor a trainable hidden layer is formally correct, but the numerical substance is matrix square-root or factor construction. The theorem does not address the central difficulties ordinarily associated with neural dynamic programming:

- approximation bias for a nonquadratic continuation;
- finite-sample estimation of the continuation target;
- stochastic optimization;
- nonconvex training outside a specially controlled basin;
- irregular or constrained action sets;
- nonlinear state transitions;
- high-dimensional integration without analytic Gaussian formulas;
- value and gradient generalization away from a coefficient identity; or
- interaction between representation error and endogenous state visitation.

The architecture-specific theorem is still worthwhile. But its successful completion does not validate the broad Neural Bellman Operators framework described in the title and retained applications. A top-journal numerical-method paper must show that the method addresses a computational difficulty not already removed by the model's analytic structure.

### B2. The numerical design does not isolate precision adaptation from target-inverse caching

The table labels the new method “Quadratic, adaptive,” while the source and protocol call it “adaptive-cached.” The distinction matters.

At every positive update, the fixed quadratic routine constructs a target inverse. The new routine constructs one inverse for the fixed target and reuses it across updates. Thus, in the anchor economy:

- fixed quadratic: six updates and six target-inverse constructions;
- adaptive-cached: six updates and three target-inverse constructions.

The bits also change from fixed 40-bit storage to an adaptive 18--21-bit schedule. Both changes can affect the clock. The experiment therefore does not identify whether the 9.8 percent anchor speedup comes from lower precision, fewer inverse constructions, implementation differences, or their interaction.

A contribution-isolating design needs at least a 2-by-2 comparison:

| Precision | Target inverse |
|---|---|
| Fixed | rebuilt every update |
| Fixed | cached within fit |
| Adaptive | rebuilt every update |
| Adaptive | cached within fit |

It should also include a fixed-precision cached procedure at the minimum constant precision that satisfies the same economic target. Without these cells, the main empirical claim about precision adaptation is not identified.

### B3. The procedures are not compared at a binding or matched economic accuracy

The requested policy tolerance is \(10^{-4}\). The largest nonstructural gap bound is approximately \(1.01\times10^{-9}\); several gaps are near \(10^{-14}\). Hence every method oversolves the declared economic target by at least about 98,000 times, and some by far more.

This has two consequences.

First, the experiment does not show the work needed to meet the economic target. It shows the work generated by a particular conservative implementation that continues until a much tighter internal condition happens to hold.

Second, a method may look faster or slower because its discrete update jumps to a very different final accuracy. Comparing clock time without an accuracy frontier is not a matched numerical experiment.

The paper needs a target sweep, for example \(10^{-2},10^{-4},10^{-6},10^{-8},10^{-10}\), together with actual early stopping at the first certified policy bound below each target. At each target, report the final policy bound, all failed checks, total time, update counts, solve counts, storage precision, and memory. The main comparison should be work to a binding economic tolerance, not work to method-specific overachievement.

### B4. The finite-precision result is not yet a practical floating-point algorithm or a bit-complexity theorem

The theorem's general first part accepts a certified whole-step perturbation \(\nu_j\). That is useful, but an implementation must still obtain that enclosure for matrix multiplication, target solves, caching, and rounding.

The explicit bit schedule assumes exact matrix products and exact target solves, followed only by entrywise factor rounding. The executed implementation uses exact rational arithmetic. The reported bit sum counts stored fractional bits across factor updates. It does not count:

- numerator and denominator growth in exact products;
- exact inverse construction cost as a function of operand bit length;
- rational normalization and greatest-common-divisor work;
- conditioning-dependent floating-point solve accuracy;
- residual certification costs at realistic dimensions;
- data movement and conversion costs; or
- total bit operations.

The paper acknowledges most of these limitations, but they are central rather than peripheral. A finite stored-precision schedule is not yet a practical finite-precision numerical method.

A publishable computational contribution would provide either:

1. a floating-point implementation with directed-rounding or residual-based enclosures for the complete step and a backward-stability analysis; or
2. an explicit arithmetic-complexity theorem in dimension, horizon, condition number, target accuracy, and operand bit length.

Without one of these, the result is best viewed as a constructive existence theorem implemented in an exact small-matrix laboratory.

### B5. The new theorem is not tested outside a two-dimensional, four-date exact laboratory

The new experiment uses:

- state dimension two;
- action dimension two;
- four decision dates;
- two nearly identical state-cost matrices;
- analytic Gaussian evaluation;
- zero simulation transitions;
- exact rational matrix operations; and
- one deterministic service per method and regime.

This is a useful algebraic validation instance. It is not a numerical benchmark.

The paper points to older dimensions 10 and 50, a 24-date recursive-risk catalogue, and other application evidence. But the new adaptive-precision algorithm is not executed there. The new timing and precision conclusions therefore cannot be inferred from those older records.

At minimum, the new construction should be run across:

- a dimension and horizon grid;
- several condition numbers and moment-domain margins;
- several target changes, including warm-gate failures;
- cold starts and genuinely transported warm starts;
- multiple certified accuracy targets;
- repeated timing runs; and
- one problem in which continuation evaluation is not an exact Gaussian coefficient calculation.

### B6. The full-policy theorem remains model-specific while the manuscript retains platform-level framing

The article is commendably explicit that the recursive-risk capital model does not discharge the obligations of the diffusion, endogenous-preference, temporal-self, or game applications. Yet those applications remain part of the active article's economic scope and the title remains “Neural Bellman Operators.”

The strongest theorem relies on:

- discrete finite horizon;
- unconstrained real vector actions;
- linear dynamics;
- quadratic stage and terminal costs;
- Gaussian innovations;
- an entropic transform with a positive moment margin;
- analytic own-policy coefficient evaluation; and
- positive-definite quadratic targets.

These assumptions are not defects. They are exactly why a complete theorem is possible. But then the paper should be framed around that theorem. The current broad framing invites the reader to treat the result as a constructive foundation for the entire NBO program, while the active evidence does not support that inference.

### B7. The economic contribution remains too small for Econometrica

The new economic experiment changes the state-cost matrix from identity to
\[
 \operatorname{diag}(201/200,199/200).
\]
Every method then solves a four-date, two-dimensional theoretical economy. No economic comparative static, policy mechanism, welfare decomposition, calibration, or substantive counterfactual is developed from the result. The purpose is to exercise factor reuse and precision allocation.

That is appropriate for a numerical-analysis paper, but the numerical contribution would then need to be correspondingly strong and general. Here the structural solution is exact and 5 to 20 times faster, the adaptive neural speedup over the inherited neural routine is not isolated, and the test is too small for scaling conclusions.

The broad applications companion does not repair this problem because those applications do not receive the new constructive theorem or new method comparison. The paper therefore sits awkwardly between computational economics and numerical linear algebra without yet delivering the decisive contribution expected in either direction.

## 4. Major comments and required changes

### M1. Run a contribution-isolating factorial comparison

Separate adaptive precision, inverse caching, warm-start reuse, and update rule. Report all combinations using the same code boundary and stopping target. A table that changes two mechanisms at once cannot support a mechanism claim.

### M2. Compare at matched certified accuracy

Use actual early stopping at several economic tolerances. Do not compare methods that happen to finish with gap bounds differing by several orders of magnitude. Report work-to-certificate curves, not one point.

### M3. Replace single sub-second clocks with a reproducible performance protocol

Each service is timed once and completes in approximately 0.01--0.28 seconds. At this scale, interpreter state, allocation, filesystem latency, CPU scheduling, and exact-integer implementation details can materially affect the ranking.

Use repeated isolated executions, warm-up rules fixed in advance, CPU and frequency controls where possible, and medians plus dispersion. Also report machine-independent counts sufficient to explain the timing differences.

### M4. Supply a realistic finite-precision implementation

Implement the method in floating point or interval/ball arithmetic at dimensions where exact rational arithmetic is no longer a plausible production method. Certify the complete matrix step, including multiplication and solve errors. Compare the predicted precision schedule with the precision actually needed.

### M5. Give an explicit complexity statement

State how work and storage depend on:

- state dimension \(d\);
- factor height \(p\);
- horizon \(T\);
- target condition number;
- initial relative error;
- policy tolerance;
- Gaussian moment margin; and
- actor/evaluation allowances.

The current \(O(\log\log(1/\tau))\) update behavior is only one component. Inverse construction, applications, certification, own-policy evaluation, and bit growth must enter the total statement.

### M6. Test the construction where neural approximation is genuinely nontrivial

A convincing next experiment would use a nonlinear continuation that is not exactly represented by a quadratic factor and for which a structural Riccati solution is unavailable. It should include representation bias, out-of-sample state coverage, and a strong conventional numerical baseline.

The question is not whether a neural method must always win. The question is whether the distinctive NBO construction enables a certified economic result that simpler methods cannot obtain at comparable work.

### M7. Study the warm-start domain rather than only successful in-basin cases

The target-change bound is a useful sufficient condition. The experiment should vary the magnitude and direction of future changes, report how often the transported factor remains in the basin, measure fallback cost, and include failed warm gates. This is the operational content of continuation reuse.

### M8. Align the title, abstract, and contribution list with the completed theorem

If the paper remains centered on the current result, a title such as “Certified Finite-Precision Continuation Construction for Risk-Sensitive Linear-Quadratic Control” would be more accurate. The controlled-diffusion and application program can be described as motivation and future scope rather than as coequal established contributions.

### M9. Deepen the literature comparison around the actual new object

The article appropriately cites classical polar iteration. It should engage more directly with:

- certified Newton--Schulz and polar decomposition;
- matrix square-root and inverse-square-root iterations;
- mixed-precision iterative refinement;
- verified linear algebra and interval matrix computation;
- risk-sensitive LQG Riccati recursions; and
- approximate dynamic programming with certified policy loss.

The novelty must be located precisely in the coupling between precision allocation and economic policy tolerance, not in the underlying matrix iteration.

### M10. Further simplify the active publication

The current presentation is much improved, but the main article still imports components from several historical revision directories and retains a broad economic-scope section whose applications live in a separate 48-page companion. A final focused paper should have one self-contained source tree, one notation system, and one theorem-evidence chain.

## 5. A focused publishable route

The strongest publishable object in R37 is not yet the full NBO platform. It is a narrower result:

> A certified mixed-precision factor-refresh method for own-policy continuation matrices in finite-horizon risk-sensitive linear-quadratic control, with a deterministic link from factor error to policy loss.

A focused paper could make a serious contribution if it contains the following.

### 5.1 Mathematical core

State the general whole-step perturbation theorem for rectangular factors and noncommuting starts. Derive the economic allocation and target-change basin. Give either floating-point backward error or bit complexity for the implemented method.

### 5.2 Contribution-isolating algorithm study

Use factorial baselines, target sweeps, repeated timing, operation counts, conditioning experiments, dimensions large enough to expose scaling, and explicit fallback cases.

### 5.3 Economic study

Apply the method to a risk-sensitive control problem where continuation matrices change repeatedly and factor reuse has a substantive economic purpose. Report complete reoptimization, policy changes, and welfare or cost consequences. Include the structural Riccati comparator throughout.

### 5.4 Extension beyond exact quadratics

Either extend the theorem to a controlled nonlinear approximation class or clearly state that the contribution is certified linear-quadratic control. The current broad NBO applications should not be used as evidence for an extension that has not been completed.

## 6. Independent verification performed for this report

I performed the following checks against the pinned R37 snapshot.

1. **Snapshot identity.** I fixed the review-ready branch at commit `9792d3dee69351f672dcc09098422b35207060a7` and tree `df6abbbd45f46c0aed6b1345a895e3e33ce6c503`. The main, active supplement, and response blobs are recorded above.
2. **Publication status.** The current audit records a 45-page article and 35-page active supplement with no undefined references, duplicate labels, missing characters, or overfull boxes. The historical supplement's retained vertical warning is not attributed to the current article.
3. **Protocol and evidence.** The committed protocol declares dimension two, horizon four, two regimes, four methods, tolerance \(10^{-4}\), exact rational work, and deterministic per-object inference. The results contain eight services, all certified, and zero simulated transitions.
4. **Comparison arithmetic.** From the committed summary, adaptive storage bits fall from 240 to 102 in the anchor case and from 120 to 54 in the changed case, reductions of 57.5 and 55.0 percent. Complete clocks fall by approximately 9.82 and 12.38 percent relative to the inherited fixed quadratic implementation.
5. **Confounding check.** Fixed and adaptive quadratic methods use the same six and three hidden updates, but target-inverse builds differ by three in the anchor case and by zero in the changed case. Thus the anchor clock contrast combines precision and caching effects.
6. **Accuracy check.** The largest nonstructural policy gap is approximately \(1.0118\times10^{-9}\), compared with the requested \(10^{-4}\), a ratio of approximately 98,833.
7. **Structural comparison.** The adaptive procedure's recorded service clock is approximately 5.07 times the structural clock in the anchor case and 20.52 times it in the changed case.
8. **Algebraic spot check.** Using exact rational arithmetic and a non-diagonal error matrix, I independently checked the Newton--Schulz Gram identity used in the precision proof. I also checked the logic of adding the implemented perturbation through \(2\nu+\nu^2\).
9. **Scope of verification.** I did not rerun or retime the original services. A rerun would produce new timing observations rather than verify the recorded ones. The review directory contains a deterministic script that verifies the committed source hashes, result arithmetic, protocol identities, and central matrix identity from the pinned repository snapshot.

The review directory includes that verification script, its machine-readable result, and a manifest pinning the reviewed scope.

## 7. Recommendation

R37 is the strongest and most careful version of this project that I have reviewed. The author has converted a diffuse empirical program into a mathematically explicit chain from continuation error to full-policy loss, and has treated provenance and adverse evidence with unusual care. The new precision theorem appears internally coherent under its assumptions.

Nevertheless, the paper does not yet meet the standard for an Econometrica numerical-methods contribution. Its complete neural construction is an exact quadratic matrix factorization inside a model with a faster closed-form structural solution. The new experiment is too small and too structurally favorable to validate the broad NBO program. Its most favorable clock comparison does not isolate precision adaptation, all procedures vastly oversolve the declared target, the finite-precision implementation relies on exact rational products and solves, and no complexity or scaling result establishes practical advantage.

I therefore recommend **rejection in the present form**. I would take seriously a new, substantially narrower submission on certified finite-precision continuation construction in risk-sensitive linear-quadratic control, or a genuinely new NBO paper that demonstrates the same constructive chain in a nonlinear economic problem where learning the continuation is necessary and economically consequential.
