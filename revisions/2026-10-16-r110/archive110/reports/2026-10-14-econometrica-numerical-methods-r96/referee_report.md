# Referee Report on "Neural Bellman Operators"

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r96-risk-resolution-2026-10-13`  
**Pinned revision commit:** `9a80ab7d4de97c9a61747899766fab43ec3c2598`  
**Pinned revision tree:** `060388fb8ca68b162da9bef3a15ccad6fd09378b`  
**Pinned main manuscript:** `revisions/2026-10-13-r96/ECTA.tex`, Git blob `1766b114f69cecfdec1b9b6dc28ba43225fae8c6`  
**Pinned technical supplement:** `revisions/2026-10-13-r96/supp.tex`, Git blob `7e8c1ff2ef3c372a8b066d5011b7866234dd28da`  
**Pinned numerical and development appendix:** `revisions/2026-10-13-r96/appendix.tex`, Git blob `2dd200b9a50f46fe805057d93a66c33f53357b31`  
**Pinned response:** `revisions/2026-10-13-r96/response.md`, Git blob `2433742c29ab9a0988bba5a34eff3b43122a20c4`  
**Pinned protocol:** `revisions/2026-10-13-r96/PROTOCOL96.md`, Git blob `f738038cb53a442e56306e076306839c59961397`  
**Pinned release ledger:** `revisions/2026-10-13-r96/RELEASE96.json`, Git blob `893e142157d6126c78ddccc399b5d997b5c39a84`  
**Publication workflow:** `38434737915`  
**Publication artifact:** `11836246327`, SHA-256 `d6765a9724669f3061a2dbd8ff55a533210c05827fb5a641a0eb251583cab19c`  
**Report date:** 14 October 2026  
**Recommendation:** **Reject in the present form and close the ordinary cumulative revision cycle. A substantially refocused new paper on certified stored continuations and decision-scale risk precision could merit evaluation, but R96 does not establish an Econometrica-level neural-specific numerical contribution or a consequential economic result.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R96 is a serious and materially improved revision. It repairs the failed R95 release boundary, freezes a source-first remote lineage, narrows the equivalence margin to a decision-scale tolerance, matches the fitted methods by design rank, label count, and serialized payload, executes admission and fallback rules under the original law, and recomputes the full 32,768-row statistical catalogue. The manuscript now has a coherent theorem--algorithm--evidence chain for recursive-risk dynamic programs.

The strongest new theoretical result is the convex-order enclosure for AVaR. For a convex Lipschitz continuation on a bounded interval, the manuscript brackets the continuous law between a midpoint rule and an endpoint-mixture rule and obtains an explicit second-order width. It then propagates this deterministic enclosure through a recursively qualified policy comparison and couples it to a prospective finite-sample design. The stated sharpness example shows that the constant is attained for the specified midpoint/endpoint pair. I found no immediate algebraic contradiction in the new recursive qualification, centered-risk identity, AVaR enclosure, prospective precision theorem, or the written sharpness construction under their stated assumptions.

The numerical design is also much stronger than in the preceding report. The online solver, quadratic continuation, rank-matched ReLU continuation, and adaptive spline continuation receive the same 1,024 labels per risk level. The three stored models have design rank six and equal 128-byte serialized payloads. They are evaluated on 4,096 new independent states at each of two risk levels. Every proposed action is admitted or rejected by the same original-law certificate and can fall back to the protected solver. The paper therefore measures complete callable services rather than raw predictor outputs.

The new experiment succeeds at its prospective precision objective. All twelve simultaneous paired intervals fit strictly inside the predeclared equivalence margin of `1/1280`, and the largest simultaneous half-width is approximately `0.00024531`, about 31.4 percent of that margin. This is a genuine advance over the very loose earlier comparisons.

The central difficulty, however, is no longer numerical validity. It is contribution identification and economic importance.

First, the successful object is a method-neutral qualification architecture. Stored continuations reduce online work; original-law lower and upper bounds decide whether their proposals may be used. The same validity, fallback, and recursive policy guarantee apply to quadratic, ReLU, and spline representations. In the actual experiment the equal-rank quadratic service is fastest at both risk levels, has no rejected first proposals, and has policy costs statistically equivalent to every other arm. The ReLU representation is neither the computational winner nor uniquely responsible for the certification theorem.

Second, all twelve economic difference intervals contain zero. Point estimates favor the online solver against every stored continuation, although the differences are small and all services are declared equivalent at the chosen margin. The experiment establishes noninferiority at a numerical tolerance. It does not show that the neural service changes an economic conclusion, improves expected welfare, or dominates a strong conventional approximation.

Third, the manuscript proves a purchase condition but does not close the purchase problem with the deposited experiment. The timing table measures fresh 32-state service processes, while the preparation ledger separates construction, calibration, and coverage work. The paper does not yet provide a complete per-arm acquisition cost, a predeclared reuse horizon, a stable break-even frontier, and an economically interpreted compute-price/adoption-fee region for the R96 services. The theoretical inequality is correct as an accounting identity, but the empirical purchase conclusion is not instantiated.

Fourth, the risk experiment remains narrow: a two-dimensional, two-date, scalar-control investment problem with a 20-bit dyadic initial law and two AVaR parameters. The product extension of the quadrature theorem still uses product evaluation points. The release ledger itself marks the largest vector execution as absent. R96 therefore does not establish that the favorable precision and service comparison survive multiple controls, longer horizons, or many independent innovations.

Finally, the verification standard, while unusually strong, does not yet independently cover the entire critical stack. The release recomputes every statistical row and audits 64 random endpoints, but it does not independently replay conventional proposal selection or the full acquisition pipeline. A separate ARM64 sibling branch reports bit-identical outputs and the same timing ordering, but that evidence is not part of the pinned source branch and does not reproduce full construction or energy accounting. Given the project's history of interval-enclosure errors, an independent implementation of the critical endpoint and selection logic remains important.

My recommendation is therefore rejection in the present form. The material contains the basis for a valuable new paper, but that paper should be narrower, method-neutral in its core claims, explicit about what is specifically neural, and organized around a complete acquisition-and-reuse frontier or a substantively consequential recursive-risk application.

## 2. Scope of the review

I reviewed the pinned R96 article, technical supplement, numerical and development appendix, response, protocol, release ledger, theorem sections, proof sections, generated tables, timing receipts, remote provenance note, and the successful publication workflow and artifact identity. I also inspected the separate ARM64 evidence branch as supplementary information but do not credit it as part of the pinned R96 submission.

I did not refit the models, rerun the full Bellman campaign, or produce a new statistical sample. This report evaluates the frozen sources and deposited execution records, checks the main mathematical chain at referee level, and recomputes the principal comparisons from the reported numbers. It is not a formal proof-assistant verification of every inherited theorem.

## 3. What R96 successfully repairs

### 3.1 The release boundary is now real

R95 failed its own publication gate. R96 replaces that status with a successful source-bound release, a clean reconstruction, 445 passing tests, a successful workflow, and a 306,772,776-byte artifact with a recorded digest. The final remote provenance commit changes only the delivery record and does not silently alter the scientific source.

### 3.2 The recursive-risk target is explicit

The paper no longer treats an expected-cost certificate as if it automatically covered nonlinear recursive risk. It states a signed recursive qualification theorem, supplies risk-specific transport moduli, and uses centered risk increments so that the reference continuation and the candidate continuation are compared under the correct recursive operator.

### 3.3 The continuous-law enclosure has decision-scale order

The midpoint/endpoint convex-order bracket gives a width proportional to `n^{-2}` for convex Lipschitz continuation values under AVaR. The product extension states the coordinatewise accumulation and does not disguise the product-point burden. The manuscript also gives a construction showing sharpness for the specified enclosure pair.

### 3.4 The precision target is prospective

The sample size, deterministic enclosure allowance, simultaneous family size, and equivalence margin are fixed before reading the outcomes. The resulting maximum half-width is well below the declared margin. This turns the comparison from an underpowered sign test into an informative equivalence statement for the declared experiment.

### 3.5 Representation budgets are substantially better matched

Quadratic, ReLU, and spline continuations use the same label catalogue, design rank, and serialized payload. The paper discloses feature selection and separates construction from online service. This is a meaningful improvement over comparisons in which network size or information content differed mechanically across arms.

### 3.6 Qualification and fallback are executed

The stored continuation does not obtain certificate authority. Each first proposal is checked under the original model; rejected proposals invoke the protected path. The final service therefore remains feasible and qualified even when a fitted representation proposes poorly.

### 3.7 The full statistical catalogue is retained

The deposited evaluation contains 32,768 arm-state rows over 8,192 distinct states. The release recomputes the reported statistics from all rows rather than from a selected summary. Failed first proposals, timing ranges, and negative comparisons are retained.

### 3.8 The manuscript is appropriately restrained about universal neural superiority

The conclusion acknowledges that the present experiment does not establish universal representation superiority. This restraint is scientifically appropriate and should be preserved in any successor paper.

## 4. Assessment of the new theory

### 4.1 Recursive qualification and centering

The recursive qualification theorem is conceptually sound: local signed endpoint errors and transport allowances are propagated through the monotone recursive-risk operator, and a common-parameter policy comparison is transferred through occupation measures. The centered-risk identity is useful because it separates the reference continuation from the incremental candidate error without changing the underlying risk functional.

The exposition should nevertheless distinguish three layers more sharply: the general recursive comparison lemma, the model-specific modulus used for AVaR or entropic risk, and the implementable lower/upper endpoint construction. These are mathematically different contributions. At present they are presented as one platform, which makes it difficult to assess exactly where novelty lies.

### 4.2 Convex-order AVaR enclosure

The midpoint distribution is dominated by the continuous cell law in convex order, while the endpoint mixture dominates it. Monotonicity of AVaR under convex order then brackets the risk. The interpolation remainder yields the stated second-order width. Under the written convexity, Lipschitz, support, and arithmetic assumptions, the argument appears correct.

The novelty claim needs to be narrower. The proof uses classical convexity and midpoint/trapezoid ideas, followed by a standard tail-risk variational representation. The paper should state precisely whether the contribution is a new optimal constant, a new rule pair, a new recursive deployment, or a new audit-ready implementation. The current sharpness result is sharpness for the specified midpoint/endpoint bracket, not a lower bound over all deterministic quadrature schemes with the same information budget.

The product extension also deserves a more candid complexity statement in the theorem itself. The error adds over coordinates, but the direct point set is a Cartesian product. A dimension-free-looking error formula should not obscure the exponential evaluation count.

### 4.3 Prospective precision and equivalence

The power calculation is one of the strongest parts of R96. It combines a deterministic service-enclosure width with a simultaneous paired concentration term and explicitly intersects the statistical interval with the uniform policy-loss range. The resulting design answers a well-posed question: are the four admitted services equivalent within `1/1280` on the declared distribution?

That question is numerically meaningful but not yet economically interpreted. The manuscript repeatedly invokes a one-percent scale, but the relationship between `1/1280` in normalized model cost and an economically material welfare or policy threshold is not calibrated. The theorem gives decision precision conditional on a margin; the application must justify the margin.

### 4.4 Purchase and reuse theorem

The purchase inequality is a useful bookkeeping statement. It correctly separates the value of a cost improvement, online service savings, acquisition cost, and fixed adoption fees. But it remains largely prospective in R96. A top-journal numerical paper should execute the frontier: measure each component with a common boundary, propagate uncertainty, and state the workload count or price region at which adoption is certified or rejected.

## 5. Numerical findings

### 5.1 Policy-cost comparison

The mean cost point estimates are:

| Risk level | Online | Quadratic | ReLU | Spline |
|---|---:|---:|---:|---:|
| `alpha=0.50` | `0.6197369` | `0.6198883` | `0.6199340` | `0.6199407` |
| `alpha=0.75` | `0.6308045` | `0.6309583` | `0.6309673` | `0.6310478` |

Every stored continuation has a slightly higher point estimate than the online solver. None of the twelve simultaneous paired intervals excludes zero. All twelve intervals do lie inside the declared equivalence margin. The correct conclusion is therefore numerical equivalence at the chosen tolerance, not cost superiority.

The most demanding interval is approximately `[-0.0004887, 0.0000020]`, and the largest half-width is approximately `0.00024531`. This is a precise and useful result, but its substantive interpretation depends entirely on the economic meaning of the margin.

### 5.2 Online service time

For fresh 32-state processes, including startup and shutdown, the median times are:

| Risk level | Online | Quadratic | ReLU | Spline |
|---|---:|---:|---:|---:|
| `alpha=0.50` | `1.53020` | `0.98127` | `1.29428` | `1.26250` |
| `alpha=0.75` | `1.52729` | `0.98531` | `1.27456` | `1.26657` |

Relative to online solution, the median reductions are about 35.9 percent for quadratic, 15.4--16.5 percent for ReLU, and 17.1--17.5 percent for spline. Quadratic is the fastest arm at both risk levels. Five processes per cell and uncontrolled processor frequency make these descriptive measurements, not a hardware-general runtime distribution, but the gap between quadratic and ReLU is much larger than the close-clock issue in earlier revisions.

### 5.3 Admission behavior

The quadratic first proposal is never rejected. ReLU first proposals are rejected in 1,136 of 4,096 states at `alpha=0.50` and 1,266 states at `alpha=0.75`, rates of about 27.7 and 30.9 percent. Spline rejection rates are about 31.1 and 26.2 percent. Across the stored arms there are 4,750 rejected first proposals, while no service reaches final exact fallback.

This distinction matters. The service-level theorem proves that the verifier survives weak proposals. It does not prove that the fitted proposal is reliable. A representation that is rejected in roughly one quarter to one third of states may still yield a useful service, but the paper should report how much of its apparent saving comes from accepted proposals, declined proposals, and conventional repair.

### 5.4 Construction and acquisition cost

The campaign receipts show approximately 15.47 seconds for preparation, 452.62 seconds for evaluation, and 51.66 seconds for the timing campaign. The displayed component table reports feature search and coverage construction, but explicitly notes that those columns are not the entire preparation boundary. Model files are equally small, yet equal serialized size does not imply equal acquisition cost.

The missing object is a per-arm complete acquisition receipt that starts from the common frozen primitives and ends with a validated, durable, deployable model. Without that object, the purchase and reuse theorem cannot be evaluated empirically.

### 5.5 Architecture evidence

A separate ARM64 branch reports bit-identical outputs and the same method ordering. This is useful robustness evidence. It should either be merged into a single review-ready source and release ledger or be excluded from the formal submission claim. At present the pinned source and the architecture evidence are separate lineages. Moreover, frequency remains uncontrolled, and the architecture branch does not reproduce full construction or energy accounting.

## 6. Blocking concerns

### B1. The neural-specific contribution is not identified

The certificate, recursive guarantee, risk enclosure, and fallback are representation-neutral. The fitted ReLU is one proposal generator among several. The equal-rank quadratic continuation is faster, has no rejected first proposals, and is statistically equivalent in policy cost. R96 demonstrates the usefulness of stored continuations plus qualification, not a specifically neural Bellman operator advantage.

### B2. The main new rate is not yet separated from classical ingredients

The second-order AVaR enclosure is useful, but the paper does not sufficiently isolate what is new relative to classical convex-order, midpoint/trapezoid, interpolation-error, and AVaR variational arguments. Sharpness for one specified bracket should not be presented as a broad information-theoretic optimality result.

### B3. The economic result is equivalence, not improvement

All twelve paired intervals contain zero. The point estimates favor the online solver. The experiment establishes noninferiority within a declared normalized margin but does not identify an economic gain, welfare change, or altered policy conclusion.

### B4. The acquisition-and-reuse frontier is not executed

The paper proves a purchase condition but does not produce complete per-arm acquisition costs, a predeclared reuse horizon, stable break-even workloads, or certified price-fee regions for the actual R96 services. Online timing alone is insufficient for a purchase result.

### B5. Fallback masks predictor reliability

A complete service may be reliable because the verifier rejects poor predictions. ReLU and spline first proposals are rejected in roughly 26--31 percent of states, whereas quadratic has zero rejections. Service reliability therefore cannot be attributed to neural fitting. The paper needs an explicit decomposition of proposal quality, admission, repair, and final work.

### B6. Scope and scaling remain narrow

The active risk experiment has two states, two dates, one control, and two AVaR levels. The product quadrature construction retains a Cartesian evaluation burden. The release contains no largest-vector execution. The paper does not show that the precision or work advantage survives longer horizons, multiple controls, or many innovations.

### B7. The independent verification boundary remains partial

All statistical rows are recomputed, which is excellent, but only 64 random endpoints are independently audited, about 0.195 percent of the arm-state rows. Conventional proposal selection and the full learning-to-action path are not independently reimplemented. The history of enclosure defects makes an independent endpoint and selection implementation especially important.

### B8. Timing evidence is descriptive and split across lineages

There are five repetitions per arm-risk cell, processor frequency is recorded but uncontrolled, and the separate ARM64 evidence is not part of the pinned source branch. Machine-independent operation counts, controlled or normalized frequency, and full acquisition measurements are needed before making broad computational claims.

### B9. The active submission remains too cumulative

The active package contains a 47-page article, a 59-page supplement, a 194-page appendix, and a 5-page response. Much of the appendix preserves historical developments outside the new recursive-risk evidence. Preservation is commendable, but a journal submission should not require the reader to separate the current theorem from a cumulative archive. The release ledger also says that visual inspection has not yet been recorded.

### B10. Econometrica-level economic consequence is absent

The manuscript supplies a careful numerical certification system, but it does not demonstrate that the method changes a substantive economic inference or opens a broadly important computational frontier. The normalized tolerance, compute price, and adoption fee remain uncalibrated. Without a consequential application or a demonstrably general numerical advance, the paper remains below the venue's threshold.

## 7. Major comments and required changes

### M1. Reframe the central contribution

Center a successor paper on certified stored continuations for recursive-risk dynamic programs. State clearly that qualification is method-neutral and that representation-specific value is an empirical question. The title, abstract, and introduction should not imply that the successful theorem is intrinsically neural.

### M2. Establish the precise novelty of the risk enclosure

Provide a focused comparison with the closest convex-order and quadrature results. State whether novelty lies in the rate, constant, rule pair, recursive composition, finite-precision implementation, or decision-design coupling. If an optimality claim is retained, prove a lower bound over a clearly defined class of admissible information and rules.

### M3. Execute the full acquisition-and-reuse frontier

For every arm, measure a common end-to-end boundary from frozen primitives through labels, feature search, fitting, validation, serialization, identity checks, and durable deployment. Predeclare reuse counts and compute-price/adoption-fee grids. Report the first workload count at which the complete net-benefit interval becomes positive, negative, or remains unresolved.

### M4. Identify representation-specific value across budgets

Repeat the comparison over several matched ranks, feature budgets, and label budgets. Include the certificate-aware fixed-feature neural readout as an actual arm. Compare it with quadratic, spline, nearest-neighbor, derivative, and other strong conventional approximations under identical information and admission rules. A neural claim requires a region in which neural structure, rather than storage alone, improves the frontier.

### M5. Decompose admission and repair work

For each arm and risk level, report accepted first proposals, rejected proposals, reason codes, protected refinement counts, final fallback counts, endpoint evaluations, and time spent in each stage. Map rejection rates over the state domain. This will distinguish predictor quality from verifier resilience.

### M6. Justify the economic margin

Translate `1/1280` into an economically interpretable loss, welfare, or policy metric in a calibrated application. Alternatively, present the margin explicitly as a numerical engineering tolerance and narrow the paper's economic claims. Do not describe a normalized percentage as economically material without a calibration.

### M7. Add a meaningful scaling experiment

Execute at least one longer-horizon, multi-control recursive-risk problem with multiple innovations. Compare against strong conventional solvers and report endpoint counts, quadrature points, memory, rational recovery, and wall-clock work. The experiment should expose, not hide, the product-law and descendant-tree costs.

### M8. Independently reimplement the critical calculations

Use a separate implementation for continuous-law endpoint integration, AVaR evaluation, action lower bounds, acquisition branching, and conventional proposal selection. Audit a stratified set covering boundaries, rejected proposals, high curvature, and both risk levels, or rerun the full manageable R96 catalogue independently. Preserve every discrepancy.

### M9. Integrate architecture and timing evidence

Place the x86 and ARM evidence under one pinned release lineage. Report operation counts and component times in addition to clocks, control or normalize processor frequency where possible, and include full construction, model loading, qualification, and energy if energy is claimed. Architecture replication should not live only on a sibling branch.

### M10. Replace the cumulative archive with a focused submission

Move historical diffusion, preference, game, and prior numerical editions to a repository archive. Keep the active article and supplement limited to the theorem, algorithm, proof, current experiment, and essential inherited lemmas. Complete and record a visual inspection of the final PDFs.

## 8. Minor and technical comments

1. Explain prominently that the evaluation initial law is a 20-bit dyadic approximation and distinguish it from a claim of exact continuous-state sampling.
2. Keep the one-service enclosure width `w` distinct from the possible `2w` contribution to a paired difference.
3. State exactly which paired observations share initial states, shocks, and arithmetic paths, and where independence enters the concentration argument.
4. Report the fitted coefficients, selected nonlinear features, conditioning diagnostics, and any ties in forward selection.
5. Give complete per-arm acquisition receipts rather than selected construction components.
6. Report the exact cost of digest validation, model loading, admission, rejection handling, and fallback.
7. Clarify that the sharpness example is for the specified midpoint/endpoint enclosure, not all quadrature methods.
8. Put the Cartesian point count next to the product-extension error bound.
9. Integrate the ARM64 evidence or mark it explicitly as outside the formal R96 release.
10. Record the missing visual inspection before calling the package referee-ready.
11. Explain the lineage between the final provenance commit, the scientific execution commit, and the workflow artifact head in one table.
12. Avoid the phrase "one-percent economic relevance" unless the normalization is tied to a calibrated economic object.

## 9. A focused publishable route

A credible new submission could be organized around:

> **Certified Stored Continuations for Recursive-Risk Dynamic Programs**

Its essential components would be:

1. a concise recursive qualification theorem;
2. a precisely situated convex-order AVaR enclosure;
3. a decision-scale prospective precision theorem;
4. a representation-neutral admission and fallback algorithm;
5. matched representation comparisons over several budgets;
6. complete acquisition and reuse accounting;
7. a calibrated economic margin or an explicitly numerical engineering objective;
8. a longer-horizon or multi-control risk application; and
9. an independent implementation audit of the critical interval kernels.

This route preserves the strongest R96 advances while removing the unsupported implication that neural representation is the source of validity or the observed computational frontier.

## 10. Recommendation

R96 is rigorous, transparent, and substantially stronger than R95. It closes the failed release, supplies a coherent recursive-risk certificate, proves a useful second-order AVaR enclosure, designs the comparison prospectively, matches representation budgets, and establishes precise equivalence for the declared experiment. These are significant achievements.

For Econometrica, however, the paper still lacks the required combination of clearly isolated numerical novelty, neural-specific advantage, complete purchase evidence, scaling relevance, and economic consequence. The equal-rank quadratic service is the computational winner; ReLU proposals are frequently rejected; all economic differences remain unresolved in sign; and the declared equivalence margin is not economically calibrated. The successful core is a general qualification architecture for stored continuations.

I therefore recommend **rejection in the present form and closure of the ordinary cumulative revision cycle**, while encouraging a substantially refocused new submission built around certified stored continuations and decision-scale recursive-risk precision.
