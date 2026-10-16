# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r39-review-ready-2026-10-07`  
**Pinned revision commit:** `f472a7c21f2f9db5285f1bf7746edf2d9463638e`  
**Pinned revision tree:** `c7837c55b507b3e50eed6af0bca13444b968fc06`  
**Pinned main manuscript:** `revisions/2026-10-07-r39/ECTA.tex`, Git blob `47d8055754a931d8403f8f76c5bd75e058336d0c`  
**Pinned technical supplement:** `revisions/2026-10-07-r39/supp.tex`, Git blob `d6dfa92d125a012acb17f8840892aa0a91b70847`  
**Pinned response:** `revisions/2026-10-07-r39/response.md`, Git blob `26b027387c77e963fcb50624044f5c8ef6586b33`  
**Pinned applications companion:** `revisions/2026-10-07-r39/applications.tex`, Git blob `7ddd174718f7c07c5376fe1d5d73942c905c5b20`  
**Report date:** 7 October 2026  
**Recommendation:** **Reject in the present form and do not continue this cumulative manuscript through another ordinary revision round. A new, sharply focused paper on verified nonlinear policy construction, or a genuinely method-specific NBO study in a scalable nonlinear economy, could merit evaluation.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R39 is a substantive response to the preceding report. It is not a cosmetic revision. The author adds a nonlinear Bellman comparison on compact state and action spaces, a finite spline/ReLU construction, an exact all-state breakpoint check for trained ReLU continuations, a residual-based native-arithmetic verification result, a precision-by-caching factorial, a five-target stopping study, transported warm-start failures, and a nonlinear investment-cost counterfactual. The current source is self-contained, the active article and supplement compile cleanly, the R38 evidence is preserved rather than reconstructed, and unfavorable structural and spline comparisons remain visible.

I independently replayed the committed publication and evidence audits, verified all 128 active publication hashes and all 315 raw service-record hashes, recomputed the principal work and accuracy comparisons, and checked the central rectangular Newton--Schulz Gram identity in exact rational arithmetic. I found no immediate algebraic contradiction in the new residual-oscillation theorem, endpoint proposition, or complete-step matrix residual bound under their stated assumptions. R39 therefore resolves several threshold objections that previously prevented a serious assessment of the numerical contribution.

The remaining problem is identification of that contribution.

The nonlinear policy certificate is built around a certified spline Bellman construction. The trained ReLU network is fitted to the spline's deterministic nodal values and proposes actions; those actions are then checked against the spline-based interval Bellman brackets. The guaranteed fallback is the same spline written exactly as a ReLU network. This is a valid certified policy procedure, but it does not yet show that the trained neural continuation itself is an independently certified Bellman approximation or that neural fitting creates an economic capability unavailable to the conventional construction.

The precision experiment has an even sharper identification problem. Across all 96 adaptive services, the 1,530 accepted factor updates use binary32. There is not a single binary64 update and not a single rejected precision attempt. The tuned fixed-precision procedure selects fixed32-cached in all 48 services, with one trial in every case. For each of the 48 matched adaptive-cached and tuned-cached services, the policy gap, checks, update sequence, counters, and domain margins are identical. Thus the experiment successfully separates caching from the update rule, but it does not empirically exercise precision adaptation. It compares fixed binary32 with fixed binary64 under an adaptive label.

The conventional comparators also remain decisive. The structural method is faster than the best factor method in every one of the sixteen quadratic policy objects. The spline method is faster than the trained neural service in all four nonlinear economies, by factors between approximately 2.43 and 11.84, and has a smaller global policy-gap bound in all four. Using the reported policy-value intervals at the sixteen displayed state--economy cells, the neural policy has strictly higher cost than the spline policy in ten cells, strictly lower cost in none, and overlapping intervals in six. At the new investment price alone, the neural policy is strictly worse in three of eight displayed cells and unresolved in five.

The new economic counterfactual is valid but does not isolate NBO. It shows that a newly selected rule improves on continuing to use the old price-one rule after investment cost rises to four. The conventional spline policy produces the same kind of positive reoptimization comparison and remains the stronger work comparator. The paper explicitly acknowledges that the result is not neural-versus-spline superiority.

R39 has therefore produced a credible verification framework and two careful construction laboratories. It has not yet demonstrated an Econometrica-level, method-specific numerical advantage or an economic result that depends on Neural Bellman Operators rather than on the accompanying conventional verifier and optimizer. The broad title and retained platform-level applications remain disproportionate to what the new evidence establishes.

I recommend rejection in the present form. I would take seriously a new paper that either makes the verifier deliberately method-neutral and studies reliable policy construction, or directly certifies a trained neural Bellman continuation in a genuinely nonlinear, multidimensional economy where strong conventional methods do not dominate complete work and economic accuracy.

## 2. What R39 successfully repairs

The recommendation should not obscure substantial progress.

### 2.1 The submitted object is complete, current, and reproducible

The review-ready branch identifies a single immutable R39 source-and-evidence snapshot. The active article, technical supplement, response, and applications companion are separately materialized. The publication artifact is tied to the source commit and workflow run. The active article has 60 pages, the supplement 39, the applications companion 48, and the response 4. The checked logs report no undefined references, duplicate labels, missing characters, or overfull boxes in any active document.

The R39 audit verifies the inherited R38 source and result hashes rather than silently rerunning or retiming the experiment. The original 315 service clocks are preserved. This is exemplary provenance practice.

### 2.2 The nonlinear Bellman comparison is mathematically clean

The residual-oscillation theorem is stated for continuous nonlinear dynamics on compact state and action spaces, a finite shock law, and monotone cash-invariant conditional evaluation. It compares the returned policy with all feasible adapted policies. The bound correctly separates the oscillation of the Bellman residual, the actual selected-action allowance, and the terminal discrepancy.

The proof uses monotonicity, cash invariance, and backward induction rather than a quadratic Gaussian identity. The theorem does not assume that the optimal value lies in a neural class or that a stochastic optimizer converges.

### 2.3 The constructive fallback is finite and explicit

The state and action mesh, interval Bellman evaluation, Lipschitz interpolation allowance, and stored-action allowance yield a finite construction for every positive target at a fixed finite horizon. The exact one-hidden-layer ReLU representation of a linear spline is correctly stated. The manuscript also correctly says that relabeling the spline as a ReLU is not a neural work advantage.

### 2.4 The trained-network endpoint check is genuinely all-state

For a scalar ReLU network and a linear spline, their difference is affine between the union of spline knots and neural breakpoints. Checking every interval endpoint therefore gives the exact supremum. R39 handles nondyadic roots and zero-slope units, deduplicates sixty stored date records to seventeen distinct networks, and verifies all seventeen by independent exact rational endpoint calculations. The new uniform network-to-spline bounds lie between approximately `0.0006703` and `0.0009840`, a material sharpening relative to the previous mesh-Lipschitz bounds.

### 2.5 The native matrix-step result addresses the correct error object

The new proposition verifies arbitrary stored inverse and product proposals through residuals against the original inputs. This can include input conversion, inverse approximation, caching, multiplication, and final storage effects. It is a more credible implementation contract than charging only the last rounding operation. The paper also refrains from calling this an arbitrary-precision bit-complexity theorem.

### 2.6 The factorial removes the old caching confound at the design level

R39 crosses fixed64/adaptive precision with rebuilt/cached target inverses, adds tuned cached native precision, retains the structural solution, charges failed checks, and reports five stopping targets. Large transported target changes fail the warm gates and fall back; those failures remain in the record. The manuscript no longer attributes the old joint adaptive-cached contrast solely to precision.

### 2.7 The economic counterfactual has a clear accounting interpretation

The price change from one to four is economically more meaningful than the preceding small quadratic valuation perturbation. The fixed-rule exposure formula separates mechanical repricing from the gain due to reoptimization. Independent shock-tree intervals establish positive gains from reoptimizing relative to retaining the old rule at the reported states and under both risk specifications. The manuscript does not call these results an empirical calibration or a neural-versus-spline victory.

## 3. Blocking concerns

### B1. The nonlinear certificate is spline-centered; the trained neural continuation is not independently certified as the Bellman object

The nonlinear theorem is valid for any supplied sequence of continuous functions with global residual and actor bounds. The finite construction instantiates it with a verified spline. The spline's nodal Bellman intervals determine the residual bounds, the state interpolation error, and the action allowances.

The trained network then receives the spline's certified nodal values as deterministic training data. It uses its own continuation predictions to propose actions, but the selected actions are certified against the independent spline Bellman brackets. The new breakpoint calculation certifies the uniform distance between the trained network and that spline. It does not directly establish the trained network's own Bellman residual against its own future network, nor propagate the network-to-spline discrepancy through a complete neural residual chain.

Consequently, the procedure certifies a **neural-proposed policy with a spline verifier**. That can be useful, but it is different from showing that a Neural Bellman Operator has learned and certified its own continuation. The fallback guarantee reinforces this distinction: termination follows because the verified spline has an exact ReLU representation, not because the width-31 trained network is guaranteed to converge.

The paper should either recast the contribution explicitly as method-neutral verified dynamic programming in which a neural network is one proposal mechanism, or build the full residual account around the trained network itself, including its own future continuation at each date, its all-state Bellman residual, terminal error, and selected-action allowance.

### B2. The precision-adaptation mechanism is never activated in the deposited experiment

Across `adaptive-cached` and `adaptive-uncached`, 96 services and 1,530 accepted factor updates are reported. All 1,530 use binary32. Zero use binary64, and zero precision attempts are rejected.

The tuned procedure selects `fixed32-cached` in all 48 of its services and uses exactly one trial each time. For all 48 matched objects and repetitions, its certificate path is identical to `adaptive-cached`: the same policy bound, checkpoint sequence, update sequence, counts, and moment-domain margin.

Thus the new factorial identifies caching effects but does not supply an empirical example of adaptive precision. It shows that binary32 is sufficient throughout the finite design. An adaptive controller that never changes precision is observationally a fixed-precision method.

A convincing design must include prospectively fixed cases in which binary32 fails and binary64 succeeds, some dates use binary32 and others binary64, rejected precision attempts are charged, and the adaptive rule improves complete work relative to the best fixed native precision at the same economic target.

### B3. Strong conventional methods dominate complete work and often the reported policy cost

For the sixteen quadratic policy objects, the structural method is faster than the best of the five factor-based procedures in every case. The best-factor/structural median service-time ratio ranges from approximately `1.09` to `5.20`, with median approximately `2.58`.

Adaptive precision does not deliver a stable timing gain even against fixed64 within the factor family: adaptive-cached is faster than fixed64-cached in 7 of 16 objects, and adaptive-uncached is faster than fixed64-uncached in 7 of 16. At the displayed `10^{-4}` object, adaptive-cached takes about `0.433` seconds versus `0.415` for fixed64-cached and `0.170` for structural control.

In the nonlinear study, the conventional spline service is faster in all four economies. The neural/spline median complete-service ratio ranges from approximately `2.43` to `11.84`. The neural global policy-gap bound is larger in all four economies.

Treating lower costs as better, the displayed state-specific intervals show neural cost strictly higher than spline cost in 10 of 16 state--economy cells, strictly lower in 0, and overlapping in 6. At the changed price `P=4`, the counts are 3 strictly higher, 0 strictly lower, and 5 overlapping.

A numerical-method paper need not dominate every benchmark. But when conventional methods are uniformly faster and the new method is never strictly better on the displayed nonlinear cost intervals, the manuscript needs a different demonstrated capability that justifies the new construction. R39 does not yet provide one.

### B4. The nonquadratic execution is one-dimensional and grid-first

The new nonlinear economy has one scalar state, one scalar constrained action, three shock outcomes, and four decision dates. The reference construction uses 256 state cells and 128 action cells. The trained network has 31 hidden units and is trained on the reference spline's deterministic values.

The constructive theorem's finite argument is based on state and action refinement. Its direct extension has the usual grid dependence in state and action dimension, while exact finite-shock policy evaluation grows with the horizon unless additional structure is used. The dimensions 2 through 32 in the same repository belong to the quadratic matrix experiment; they do not demonstrate scaling of the new nonlinear construction.

This is a useful proof-of-concept, not evidence that NBO resolves a high-dimensional nonlinear economic problem. The next study needs a genuinely multidimensional nonlinear continuation, continuous or high-support uncertainty, a strong approximate-dynamic-programming baseline, and a work-to-certified-accuracy analysis that includes the verifier.

### B5. The economic gain is a stale-policy comparison, not a method-specific or near-optimality result

The counterfactual asks whether the new price-four neural-selected policy improves on continuing to use the price-one conventional rule. The answer is yes at the reported states. The positive lower endpoints for the neural comparison range from approximately `0.0212` to `0.0976`.

This is economically interpretable, but the old rule is deliberately not reoptimized after a fourfold change in investment cost. The conventional price-four spline policy produces the same type of positive reoptimization comparison. The paper explicitly states that the neural policy is not shown to outperform the newly optimized spline policy.

The global neural policy-loss bounds, approximately `0.236` to `0.254`, are also materially larger than many of the reported reoptimization gains. They certify feasibility and conservative distance to the optimum, but not a sharp solution of the nonlinear control problem.

For Econometrica, the method should unlock an economic conclusion that cannot be obtained as sharply and more cheaply by the conventional baseline. Here the economic conclusion is that reoptimization matters after a large price change; it is not specific to NBO.

### B6. The end-to-end implemented policy is not fully covered by the native arithmetic theorem

The matrix-factor services verify native proposals through residual enclosures, but the policy certificate is stated for the exact-real interpretation of stored feedback coefficients. The deposited policy services use a zero action-execution allowance. This does not certify all floating-point evaluation of the feedback, state propagation, clipping, or actuator output on the declared state domain.

The nonlinear implementation uses interval Bellman arithmetic and independently checks selected actions, which is stronger at the construction stage. Yet the paper still lacks one common end-to-end numerical contract from stored model data through deployed action evaluation and state transition to the economic objective.

A practical numerical-method contribution should instantiate the existing execution-error propositions with nonzero, measured or verified bounds. It should not leave the last policy-evaluation layer exact by convention after emphasizing native arithmetic elsewhere.

### B7. Timing and complexity evidence remains descriptive rather than a stable numerical frontier

The protocol uses three clocks per deterministic object, one thread, and a fixed shuffle. CPU affinity and frequency are not controlled. Several services are sub-second. The paper correctly avoids significance claims, but then the small timing differences within the factor family cannot carry a numerical-efficiency conclusion.

The manuscript gives useful operation counters, but not a complete asymptotic work or storage theorem for the nonlinear procedure, the interval verifier, or the native residual certification. It does not quantify how total verified work scales jointly with state dimension, action dimension, shock support, horizon, condition number, and requested policy accuracy.

A top numerical-method paper should provide either a credible complexity theory or a sufficiently broad, repeated scaling experiment. R39 provides neither for the new nonlinear method.

### B8. The cumulative scope remains broader than the completed evidence

The active publication comprises a 60-page main article, a 39-page supplement, and a 48-page applications companion. It retains controlled diffusions, endogenous preferences, recursive utility, temporal selves, and strategic games. The two complete constructive instances are a risk-sensitive linear-quadratic Gaussian economy and a one-dimensional compact-state nonlinear investment economy.

The manuscript is transparent that these instances do not discharge every application's assumptions. Nevertheless, the title, abstract, and cumulative structure continue to present a platform-level theory. The new evidence does not yet support that breadth.

This is not a request to delete valid work. It is a request to identify the paper that has actually been established. The strongest current object is a method-neutral verification framework with two constructive examples and honest negative comparisons, not a demonstrated general neural Bellman method for all retained applications.

## 4. Major comments and required changes

### M1. Close the trained-network Bellman chain

Use the trained network itself as `v_t` in the residual theorem. Certify its own-policy continuation recursively, its all-state Bellman residual over continuous actions, its terminal discrepancy, and the actual selected action. If the spline is needed as the verifier, describe the method as spline-verified neural proposal generation rather than as a certified learned Bellman continuation.

### M2. Design cases that actually exercise precision adaptation

Prespecify moment margins, conditioning, dimensions, and targets for which binary32 fails and binary64 succeeds. Include mixed schedules, rejected precision attempts, and native fallback. Compare the adaptive procedure with the best fixed precision selected without post hoc knowledge.

### M3. Report method-level equivalence or inferiority margins

The current result often says the neural and conventional intervals overlap. Define an economically meaningful equivalence margin and design the policy-evaluation precision to resolve it. An absence of strict neural superiority is not evidence of equality.

### M4. Move the nonlinear study beyond one state and one action

A credible scaling study should include at least one multidimensional nonlinear economy in which tensor grids are no longer a competitive reference. Use a strong sparse-grid, projection, simulation-regression, or fitted-value baseline and charge its verification in the same way.

### M5. Compare the actual reoptimized policies directly

For the price-change experiment, report certified neural-minus-spline policy-cost intervals under `P=4`, not only each method against the stale old rule. The already reported state intervals suggest no neural advantage. Make this direct comparison a primary result.

### M6. Instantiate nonzero execution allowances

Certify the stored-to-deployed actor evaluation, including floating arithmetic, clipping or projection, and state transition. Report the size of this allowance relative to the policy gap and the economic reoptimization gain.

### M7. Provide total verified-work scaling

Separate proposal construction, interval or residual verification, action optimization, policy evaluation, failed checks and fallbacks, memory and data movement, and durable output. Then analyze dependence on dimension, horizon, support size, conditioning, and target accuracy.

### M8. Use a performance protocol appropriate to small clock differences

For sub-second services, use isolated repeated executions, fixed warm-up rules, process pinning and frequency control where available, and enough repetitions to characterize system noise. Preserve machine-independent counters as the primary explanation of any speed difference.

### M9. Align claims with the strongest completed contribution

There are two coherent papers available.

**Verification-centered paper:** make the Bellman residual and policy certificate method-neutral, compare spline, neural, structural, and other candidate generators, and treat the adverse neural comparisons as results.

**NBO-centered paper:** demonstrate a trained neural continuation that is directly certified, scales beyond the conventional construction, and enables an economically substantive result at competitive total work.

The present manuscript tries to be both.

### M10. Consolidate the active source and notation

R39 is more self-contained than its predecessors, but the active article still carries a large inherited framework and multiple numerical programs. A new submission should contain one central theorem chain, one authoritative algorithm, one main economic realization, and one evidence design. Historical materials can remain in the repository without remaining coequal parts of the journal article.

## 5. Focused publishable routes

### 5.1 Verified nonlinear policy construction

A strong paper could center on the residual-oscillation theorem and certified policy construction. The neural network would be one candidate generator among several. The paper would compare complete work to a policy target, explain when the verifier is worth its cost, and report both positive and negative candidate-generator findings.

This route is already substantially supported by R39, but it requires narrower claims and a multidimensional example.

### 5.2 A genuinely method-specific Neural Bellman Operator

Alternatively, retain NBO as the protagonist and add a problem in which continuation reuse, shared value-gradient structure, or amortized evaluation creates a demonstrated advantage. The trained continuation itself must satisfy the operational residual chain. The benchmark should make direct spline or structural solution unavailable or genuinely expensive, while remaining strong and credible.

The goal need not be universal neural superiority. It should be one economically meaningful capability that is both specific to the method and established at matched certified accuracy and total work.

## 6. Independent verification performed for this report

I performed the following checks against the pinned R39 snapshot.

1. **Snapshot identity.** I fixed the review at commit `f472a7c21f2f9db5285f1bf7746edf2d9463638e` and tree `c7837c55b507b3e50eed6af0bca13444b968fc06`.
2. **Publication artifact.** I downloaded artifact `nbo-r39-native-review-publication`, ID `11454277229`, whose GitHub digest is `d295c8593277373b4d016d17cd6268bf960d6e3936ba49c70ec9e1c1f83f1844`.
3. **Publication hashes.** All 128 entries in the active publication manifest match their files.
4. **Compilation.** The active 60-page article, 39-page supplement, 48-page applications companion, and 4-page response have no recorded undefined references, duplicate labels, missing characters, or overfull boxes.
5. **Raw evidence.** All 315 economic service records match the hashes in the execution ledger. The ledger contains 288 policy services, 12 trained-network services, 12 spline services, and 3 frontier services, plus one excluded warm-up.
6. **Adaptive precision.** The 48 adaptive-cached services use 765 binary32 updates and zero binary64 updates. The 48 adaptive-uncached services do the same. There are zero rejected precision attempts.
7. **Tuned fixed precision.** All 48 tuned-cached services select fixed32-cached on the first trial. Every matched tuned/adaptive-cached certificate path is identical.
8. **Quadratic work.** Structural control is faster than the best factor method in all 16 policy objects; the best-factor/structural median service-time ratio ranges from about `1.09` to `5.20`.
9. **Nonlinear work and cost.** The neural service is slower than spline in all four economies, with median time ratios from about `2.43` to `11.84`. The neural global gap is larger in all four. Among the sixteen displayed state--economy value intervals, neural cost is strictly higher in ten, lower in zero, and unresolved in six.
10. **Network endpoints.** The audit contains sixty date records, seventeen distinct networks, and nineteen passing exact rational endpoint checks. The certified network-to-spline error range is approximately `[0.0006703, 0.0009840]`.
11. **Counterfactuals.** Both the neural and spline new-price rules have positive lower reoptimization gains relative to retaining the old rule. For the neural rule, all eight reported price-four state-risk lower endpoints are positive.
12. **Algebraic spot check.** I independently verified the rectangular, noncommuting Newton--Schulz Gram identity in exact rational arithmetic.
13. **Scope.** I did not rerun or retime the original 315 services. Their clocks are frozen observations. The review directory contains the deterministic audit script and its machine-readable output.

## 7. Recommendation

R39 deserves substantial credit. It answers the preceding report with real mathematics, better experimental identification, native arithmetic verification, a nonquadratic construction, and an economically interpretable counterfactual. The source and evidence discipline is unusually strong. I found no immediate contradiction in the central new theorems under their stated assumptions.

Nevertheless, the manuscript does not yet meet the standard for an Econometrica numerical-methods contribution. The certified nonlinear procedure remains spline-centered; the trained network is a proposal device rather than an independently certified Bellman continuation. The claimed adaptive-precision mechanism is not exercised in any of 1,530 adaptive updates. Structural and spline methods dominate complete work, and the neural policy is never strictly better on the displayed same-economy spline comparisons. The nonlinear realization is one-dimensional, the reoptimization gain is not method-specific, and the cumulative platform-level scope remains much broader than the completed evidence.

I therefore recommend **rejection in the present form and no further ordinary revision of this cumulative submission**. A new, focused paper on verified nonlinear policy construction, or a new NBO paper that directly certifies a trained continuation and demonstrates a scalable method-specific economic capability, could merit serious consideration.
