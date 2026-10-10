# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r65-review-ready-2026-10-10`  
**Pinned revision commit:** `34a5ce17dc3ac4681b6d004eca00637f28104e28`  
**Pinned revision tree:** `0e3572437c8edad55ca123545477c5593c917f6d`  
**Pinned main manuscript:** `revisions/2026-10-10-r65/ECTA.tex`, Git blob `2d2570456c2a7e2ae5d038489dcba3116cdde2bb`  
**Pinned technical supplement:** `revisions/2026-10-10-r65/supp.tex`, Git blob `b777d6b74a4f078f065f3eecf473a88de5a80721`  
**Pinned response:** `revisions/2026-10-10-r65/response.md`, Git blob `aee7d72fc496972429d30975c9d74f78a0bf7e40`  
**Publication workflow:** `38041552904`  
**Publication artifact:** `11665588550`, SHA-256 `2c139fc5f139e37deabd7a0f6ca7adea9699d41db059f24950d74f42fddd1cd7`  
**Report date:** 10 October 2026  
**Recommendation:** **Reject in the present form and do not continue the cumulative manuscript through another ordinary revision round. A new, sharply focused paper on certificate-gated, prediction-guided Bellman search without state lattices could merit evaluation, but R65 does not establish an Econometrica-level, method-specific contribution for Neural Bellman Operators.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R65 is the strongest and most coherent version of this project that I have reviewed. It resolves the publication-completeness problem, reduces the active paper to a readable 42-page article and 14-page supplement, integrates the R63 and R64 source-frozen catalogues, preserves the adverse R62 evidence, and adds a useful proposition separating witness accuracy from certificate localization. The canonical branch contains ordinary sources, seven compiled documents, a clean archive rebuild, 63 tests, and a complete replay of 256 isolated services and 55,296 implemented decisions. The provenance and failure-preservation standard is exceptional.

The principal numerical construction is also legitimate. In the original convex capacity-constrained investment economy, a recursive query service bounds the original continuous-action Bellman problem at the state actually acquired. It uses parabolic lower minorants, original-law quadrature, outward arithmetic, action rounding, and a finite recovery contract. A trained selector may propose the location of a necessary action query, but cannot alter the feasible set, lower bound, stopping tolerance, or validity of the returned policy. The certificate-gated version first tests the two boundary actions and consults the predictor only when the current certificate remains unresolved. The resulting complete policy has a uniform original-optimum loss account without storing a tensor state lattice.

I found no immediate algebraic contradiction in the central chain under the stated hypotheses. The semiconcavity minorants, conditional-mean quadrature account, finite refinement argument, acquired-state policy recursion, and prediction/localization inequality are internally consistent. The new localization proposition correctly emphasizes that a close witness is not enough: the lower certificate must also be localized. The safeguards make an inaccurate predictor a work risk rather than a correctness risk.

The decisive issue is contribution identification. R65 demonstrates a safe **prediction-guided certified search procedure**. It does not demonstrate a specifically neural numerical advantage.

The complete cold-start evidence is uniformly unfavorable to the learned services. In every one of the eight task--target cells, either adaptive parabolic search or bisection has the smallest median complete process time. Certificate gating reduces deployment Bellman queries relative to unconditional insertion in all sixteen ReLU and all sixteen quadratic matched transcripts, which is a real and reproducible incremental result. Against adaptive parabolic search, however, the comparison is mixed: ReLU routing uses fewer queries in nine transcripts, the same number in three, and more in four; quadratic routing uses fewer in eleven, the same in two, and more in three.

More importantly, the data do not identify a ReLU-specific benefit. Directly comparing the two routed predictors, ReLU uses fewer deployment queries in nine of sixteen transcripts, ties in two, and uses more in five. The quadratic route has the lower median complete cold-start time in all eight task--target cells. Across the matched seed-level clock medians, ReLU is slower in fifteen of sixteen comparisons. All 72 R64 fitting warnings occur in the ReLU services; the quadratic fits report none. The certificate remains valid despite those warnings because prediction quality is not part of correctness, but that same robustness prevents universal return from being evidence of successful neural training.

The new localization proposition does not close this empirical gap. Its sufficient condition depends on the distance from the proposed action to the unknown true minimizer and, at a boundary, on the derivative at that unknown minimizer. Those are explanatory quantities, not computable stopping or training observables in the deposited services. The implementation still stops on the directly computed certificate gap. R65 therefore explains why a prediction can help, but does not provide an ex ante training-to-query theorem showing when the fitted ReLU will help or how often it will do so.

The state-lattice-free result is valuable but also narrower than the paper's broader numerical framing. The execution has one scalar action, one scalar innovation, and horizons two and three. State dimension rises to sixteen, but the primitive normalization keeps the action and quadrature budgets dimension-independent while every transition and cost remains linear in the number of coordinates. The continuation tree still grows sharply with horizon: the three-date tight-target adaptive service uses more than thirty thousand deployment queries for only 32 workload trajectories. There is no tensor-free two-control execution, multidimensional innovation experiment, or long-horizon frontier.

Finally, R65 creates no new independent continuous-law expected-cost comparison for the query controllers. Its finite dyadic workload is an exact reproducibility and implementation diagnostic, not an IID policy-value experiment. The earlier R62 continuous-law evidence remains adverse to the pure fitted policies and unresolved for common-augmented policies, but those are different policy objects. The current paper consequently establishes safe accuracy and measured work, not an economic gain from the newly routed controller.

I therefore recommend rejection in the present form. I would take seriously a new paper centered on **certificate-gated prediction-guided Bellman search**, provided it identifies the incremental value of the predictor against equally flexible non-neural proposals, executes a prospective repeated-use and direct-policy-value design, and substantially narrows the economic and methodological claims.

## 2. What R65 successfully repairs

### 2.1 The submitted object is complete, immutable, and readable

R65 has one canonical review-ready branch. The active article, supplement, and response are ordinary UTF-8 sources and compile to 42, 14, and 9 pages. The preceding and complete historical editions remain available as separate companions rather than being interleaved through the active reading path. The clean rebuild reproduces every document, and the final delivery binds the source, 63 tests, 256 service records, and seven PDFs.

This is a major improvement over prior cumulative revisions.

### 2.2 The implemented policy is certified against the original optimum

The validity theorem concerns the complete callable controller, including state acquisition, feasible action rounding, original-law continuation queries, and the policy's own future. It does not assign a certificate to an ideal actor while deploying another policy. The comparison is with the original continuous-action Bellman optimum in the declared investment economy.

### 2.3 Learning is separated correctly from verification

The predictor proposes an action-query location. It supplies neither a Bellman endpoint nor a lower bound. Every routed query must pass the same original-law evaluator and certificate as a conventional query. Invalid or unhelpful proposals cannot forge a successful policy certificate.

This is an appropriate architecture for safe learned optimization.

### 2.4 Gating has a genuine matched effect

The insertion and routing arms reconstruct the same fitted model for a matched task, seed, and repetition. Routing reduces deployment queries relative to unconditional insertion in all sixteen ReLU and all sixteen quadratic distinct transcripts. This result is not produced by changing weights, workloads, or targets.

### 2.5 The state-lattice-free service is executed at dimension sixteen

The R65 service returns the `1/128` original-optimum contract at sixteen state coordinates without a stored tensor state table. That is a meaningful implementation result, especially relative to the earlier tensor study, which reached only a coarse target in eight dimensions.

### 2.6 Predictor failure does not undermine mathematical reliability

All 256 declared services return their stated contracts. The real-arithmetic cap and exact-rational recovery rule make the validity statement independent of optimizer convergence. No floating workload invokes recovery, but its precision condition and tests are retained rather than omitted.

### 2.7 Adverse evidence is prominent

The article and response state that conventional methods win every complete cold-start cell, that the previous pure ReLU policy comparisons were adverse, that the query workload creates no new continuous-law gain interval, and that the observed query savings do not pay for training. This is exemplary disclosure.

## 3. Blocking concerns

### B1. The successful contribution is prediction-guided certified search, not a specifically neural method

The proof is valid for any finite proposed action. If a proposal is declined, the gated service exactly reproduces the conventional parabolic transcript under common arithmetic and tie rules. Correctness, termination, feasibility, and original-optimum accuracy come from conventional curvature bounds and certified Bellman queries.

The neural network therefore affects only the location of some interior probes. That can be useful, but it is not enough to support a method-specific NBO claim unless the neural proposal is shown to improve the relevant frontier relative to equally flexible non-neural predictors. R65's own full quadratic predictor is at least as compelling: it wins more of the route-versus-adaptive query comparisons, reports no fitting warnings, and has the lower median complete time in all eight task--target cells.

### B2. Conventional methods win all complete cold-start comparisons

The publication's primary service boundary includes imports, Bellman-generated training labels, fitting, deployment queries, exact workload reconstruction, serialization, fsync, and process exit. Under that complete boundary:

- adaptive parabolic search wins five task--target cells;
- bisection wins three; and
- no learned service wins any of the eight.

This is not a small qualification. It is the principal numerical-method comparison. The paper has demonstrated a safe learned component, but not a competitive learned service on the frozen workloads.

### B3. The ReLU representation is not identified as the useful predictor

Among sixteen distinct matched routed transcripts:

- ReLU uses fewer queries than quadratic in 9;
- they tie in 2; and
- ReLU uses more in 5.

The quadratic route has lower complete-time cell medians in 8/8 cells. At the seed-level median-clock comparison, ReLU is slower in 15/16 cases. The representation and optimizer therefore do not deliver a reproducible incremental advantage over a conventional quadratic predictor on the declared feature map.

A broad neural-method paper needs more than showing that one neural proposal can participate safely.

### B4. The localization proposition is explanatory but not operational for the fitted models

The bound
\[
 2w+\Lambda\Delta+Hh^2/8+\lambda e+He^2/2
\]
contains `e`, the distance from the proposal to the unknown true minimizer, and `lambda`, the derivative magnitude at that minimizer when it lies on a boundary. The services do not observe these quantities, certify them from training loss, or use them to decide whether the predictor will close the certificate.

The proposition therefore gives an after-the-fact decomposition and a useful theoretical sufficient condition. It does not provide:

- a computable predictor-quality certificate;
- a training objective whose achieved value implies query savings;
- a probability of certificate closure under a declared task distribution; or
- a deterministic work improvement bound for the fitted ReLU.

The actual algorithm still learns whether the proposal helped only after paying for and certifying the query.

### B5. The claimed repeated-use value is not executed and is often remote in query-count units

R65 states the correct arithmetic break-even condition for repeated identical workloads. The data, however, do not execute a cached-model repeated-use service or measure its complete amortized cost.

As a deliberately favorable diagnostic, treat one training Bellman query as equal to one saved deployment Bellman query. Even under that simplification, the finite ReLU break-even counts against adaptive search range from about 86 to 2,304 identical workload repetitions, with a median of 1,152; seven of sixteen transcripts have no positive deployment saving at all. For quadratic routing the finite range is about 154 to 3,389, with a median of 2,304; five transcripts have no positive saving.

These calculations are not timing or economic break-even estimates—training queries and deployment queries need not have equal cost—but they show why an actual prospective amortization experiment is essential.

### B6. There is no direct continuous-law policy-cost comparison for the new controllers

The query catalogues use fixed dyadic workloads with named boundary replacements. Their exact rational averages are excellent implementation diagnostics, but are explicitly not IID estimates under the continuous law. R65 creates zero new independent continuous-law observations.

The earlier direct comparisons cannot be transferred automatically:

- the pure fitted policies are different economic objects;
- the common-augmented policies retain a stored conventional candidate; and
- the new callable query controller recomputes a certificate at every state.

Without a direct comparison of the new returned policies, the paper establishes policy-loss guarantees and work, not expected economic gains from routing.

### B7. Training reliability is not identified

The finite catalogue has two fitting seeds per learned method and two process repetitions. The repetitions have identical fitted parameters and traces and are timing repetitions, not independent optimizer draws. There are 104 retained fitting warnings across R63 and R64; all 72 R64 warnings occur in the ReLU insertion and routing services, while the quadratic services report none.

Every service still returns because the verifier tolerates arbitrary finite predictions. This establishes verifier reliability, not neural fitting reliability. R65 provides neither a population success probability nor a deterministic training guarantee for the ReLU selector.

### B8. State-lattice-free does not yet imply a broadly scalable dynamic-programming method

The state-table factor is removed, but other resource dependencies remain:

- one scalar action;
- one scalar innovation;
- horizons only two and three;
- recursive quadrature over descendants;
- a finite-precision recovery path with potentially substantial rational cost; and
- no executed tensor-free two-control or multidimensional-shock case.

The dimension-sixteen result is useful, but the model's normalized regularity keeps action and quadrature budgets independent of dimension by construction. The three-date tight-target workload already requires roughly 31,000 deployment queries for 32 paths. The paper does not yet show how the approach behaves at economically relevant horizons or richer uncertainty.

### B9. The economic purchase criterion is formal rather than empirically instantiated

The decision rule correctly distinguishes uniform regret, expected gain, computation price, and deployment fee. But the model-loss conversion, per-second price, reuse count, and initial-state law are user-supplied parameters, not estimated or calibrated objects. Because the new controllers have no direct continuous-law gain interval, the purchase calculation cannot identify a favorable learned deployment from the deposited evidence.

At the observed cold-start contract, the least expensive eligible service is conventional in every cell.

### B10. The title and residual platform scope remain broader than the established result

The active paper is much more focused than R62 and deserves credit for that. Nevertheless, “Neural Bellman Operators” still suggests a method family covering more than the completed scalar expectation problem. The preserved diffusion, recursive-preference, endogenous-preference, temporal-self, and game developments retain separate assumptions and do not receive the R65 state-grid-free query theorem or evidence.

The completed result is best described as a certified prediction-assisted search method for a convex capacity-constrained dynamic program. The broader title and historical platform do not add method-specific evidence.

## 4. Major comments and required changes

### M1. Reframe the central object

Center the paper on certificate-gated prediction-guided Bellman search. State explicitly that the verifier is method-neutral and that the predictor is a warm-start/query-location device. Avoid using the safety theorem itself as evidence for neural superiority.

### M2. Add contribution-isolating predictor baselines

Compare ReLU, quadratic, linear, spline, derivative-based, nearest-training-action, and deliberately simple heuristic proposals under the identical gate. The key outcome is not fit error but certificate progress and total saved work conditional on paying for the predictor.

### M3. Make localization operational

Develop a computable surrogate for certificate closure, such as a certified upper bound on action regret, a prediction interval for the optimum, or a learned lower-certificate localization model. Show how the achieved training criterion implies a bound on expected or worst-case additional queries.

### M4. Execute the amortized service prospectively

Train once, preserve the model, and execute a preregistered sequence of new query workloads. Include model loading, drift checks, failed reuse, verification, and durable output. Report the actual break-even point in complete work rather than an algebraic possibility.

### M5. Compare the actual new policies under the continuous law

Use a fresh, source-frozen common-path design for adaptive search, bisection, ReLU routing, and quadratic routing. The estimand should be expected policy-cost differences for the actual callable controllers, not finite dyadic workload means or differences of regret bounds.

### M6. Expand the dynamic difficulty

Execute at least one tensor-free case with two controls, a multidimensional innovation, and a longer horizon. Report how descendant counts, batching, memory, recovery, and accuracy scale. The current dimension result alone does not address horizon and shock-tree complexity.

### M7. Study training reliability

Use a prespecified distribution or deterministic catalogue of more than two fitting initializations and several economic tasks. Report fit failures, warnings, routed/declined proposal rates, certificate progress, and complete work. Separate verifier return reliability from predictor usefulness.

### M8. Report prediction-value diagnostics directly

For every routed proposal, record:

- upper-witness improvement;
- lower-certificate improvement;
- zero-progress events;
- action distance to a high-accuracy reference where available;
- query saved or added relative to the matched conventional transcript; and
- predictor evaluation and training costs.

This would connect the new localization theorem to the evidence.

### M9. Strengthen the economic application

Either calibrate the computation-versus-policy-loss tradeoff in a substantive application or present the paper as a numerical certification contribution. A symbolic monetary conversion does not by itself provide an Econometrica-scale economic result.

### M10. Submit one focused paper

The next submission should contain one model class, one certificate-gated algorithm, one predictor-comparison design, one direct policy-value experiment, and one scaling study. Preserve the historical NBO development in the repository, but do not ask the active journal submission to carry it as evidence for the new method.

## 5. A focused publishable route

A credible new submission could be titled along the lines of:

> **Certificate-Gated Prediction-Guided Bellman Search**

Its contribution would be:

1. a predictor-independent original-optimum policy certificate;
2. a gated action-search algorithm that cannot lose validity when predictions fail;
3. an operational localization/progress condition;
4. strong neural and non-neural predictor baselines;
5. direct policy-value comparisons;
6. a prospective amortized-use experiment;
7. multi-control and longer-horizon scaling evidence; and
8. complete work-to-certified-accuracy frontiers.

Such a paper would make the negative and positive R65 findings useful: learning can reorganize certified search, but the economic value of that reorganization must be demonstrated rather than inferred from safety.

## 6. Independent verification performed for this report

I downloaded the source-bound R65 publication artifact and verified its SHA-256:

`2c139fc5f139e37deabd7a0f6ca7adea9699d41db059f24950d74f42fddd1cd7`.

I then independently parsed the committed R63/R64 audit records and recomputed the following:

1. **Publication identity and completeness.** The canonical branch is R65; the active article, supplement, and response have 42, 14, and 9 pages; all seven documents reproduce under the clean rebuild; 63 tests pass.
2. **Catalogue completeness.** The frozen evidence contains 96 R63 and 160 R64 services, all returned; 55,296 policy decisions are bound; 27,648 distinct observations are re-queried; no declared workload invokes rational fallback.
3. **Cold-start winners.** Adaptive parabolic search has the lowest median complete time in five cells and bisection in three. No learned method wins a cell.
4. **Gating effect.** ReLU routing and quadratic routing each reduce deployment queries relative to unconditional insertion in all sixteen distinct matched transcripts.
5. **Conventional comparison.** ReLU routing is lower/equal/higher than adaptive in 9/3/4 transcripts; quadratic routing is 11/2/3.
6. **Representation comparison.** ReLU routing is lower/equal/higher than quadratic routing in deployment queries in 9/2/5 transcripts. Quadratic routing has the lower complete-time median in all eight task--target cells.
7. **Warnings.** The two catalogues contain 104 fitting warnings. In R64, 36 belong to ReLU insertion and 36 to ReLU routing; none belong to the quadratic or conventional methods.
8. **Amortization diagnostic.** Under the deliberately simplifying one-training-query-equals-one-deployment-query convention, finite ReLU break-even counts against adaptive search have minimum/median/maximum approximately 86/1,152/2,304 repeated identical workloads, with seven transcripts having no positive savings. Quadratic counts are approximately 154/2,304/3,389, with five transcripts having no positive savings.
9. **Resource records.** The largest live batch is 2,048 states, peak process memory is 98,860 KiB, and the worst recorded complete process time is approximately 2.5831 seconds.

The review directory includes the standard-library audit script and its actual machine-readable output. I did not rerun fitting, Bellman services, policy evaluation, or timing experiments, because those would create new observations rather than verify the frozen records.

## 7. Recommendation

R65 is mathematically careful, reproducible, and unusually honest about adverse evidence. It establishes a useful safe-search architecture: predictions may alter where the algorithm queries, while a conventional certificate retains authority over validity. It also demonstrates that a state lattice can be avoided in a structured high-dimensional state model.

Those achievements are not enough for the present Econometrica submission. The conventional methods are faster in every complete cold-start cell, the quadratic predictor is at least as compelling as the ReLU predictor, the localization result is not operationalized for trained models, expected economic gains for the new controllers are not measured, and the repeated-use advantage is hypothetical rather than executed.

I therefore recommend **rejection in the present form**, without another ordinary revision of the cumulative manuscript. A new, focused paper on certificate-gated prediction-guided Bellman search could merit serious consideration if it isolates predictor value, supplies direct economic comparisons, and demonstrates a complete amortized and scaling advantage in at least one consequential setting.
