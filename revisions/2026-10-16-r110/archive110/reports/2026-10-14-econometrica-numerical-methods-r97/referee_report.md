# Referee Report on "Neural Bellman Operators"

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r97-referee-ready-2026-10-14`  
**Pinned revision commit:** `f802fe64d91d9f5c1c8f86123b0fbe114e622279`  
**Pinned revision tree:** `7952f056ec360f33a8f87e8f78e54775c9aeb320`  
**Pinned main manuscript:** `revisions/2026-10-14-r97/ECTA.tex`, Git blob `21bafe01e624662b3ab099280a139108afc1a335`  
**Pinned technical supplement:** `revisions/2026-10-14-r97/supp.tex`, Git blob `5cc64be254b073411451d0a865473a2b99eecd14`  
**Pinned response:** `revisions/2026-10-14-r97/response.md`, Git blob `c155ea6444274b125a160aed1b6e11aea5f4e150`  
**Pinned protocol:** `revisions/2026-10-14-r97/PROTOCOL97.md`, Git blob `c3173746f183fb24a62583e9152f2a26937cf93c`  
**Pinned release ledger:** `revisions/2026-10-14-r97/RELEASE97.json`, Git blob `d30cb12cb3d64b8853586ebe754c730571443f52`  
**Publication workflow:** `38514480061`  
**Publication artifact:** `11871551096`, SHA-256 `0ba9775b8ccb3ce81d268795dd7f5ad22ca02d24515ed501b779bfff5d2bec75`  
**Report date:** 14 October 2026  
**Recommendation:** **Reject in the present form and close the ordinary cumulative revision cycle. R97 contains a careful method-neutral certification result and an unusually transparent negative acquisition experiment, but it does not establish an Econometrica-level neural-specific numerical contribution, a sufficiently broad information-complexity advance, or a consequential economic application. A new standalone paper centered on certified recursive-risk computation and the observed misalignment between residual certificates and delivered decisions could merit evaluation in a specialized numerical-economics or computational-methods venue.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R97 is the most disciplined and candid revision in this sequence. It preserves the adverse R96 comparison, places the new experiment behind a prospective remote protocol, records every candidate and rejection, gives a successful source-bound workflow, and discloses the remaining scientific obligations. The release contains a 47-page article, a 37-page technical supplement, a 230-page development appendix, and a 5-page response. The workflow reports 445 inherited and eight new tests, successful builds, source identities, an independent proposal replay, exact statistical checks, and rational endpoint checks. The provenance and failure-preservation standard is exceptional.

The new mathematical statements are mostly correct under their written assumptions. The deterministic information theorem constructs two convex Lipschitz continuations that agree at every adaptively selected value query but have different AVaR tail integrals. The resulting lower width is of order `N^{-2}`, matching the retained midpoint--endpoint upper exponent at each fixed risk level. The oblique-ridge proposition gives the stated exact ReLU representation and the stated best errors for additive functions and total-degree-two polynomials. The verified-readout proposition correctly guarantees that an accepted candidate cannot have a larger validated residual span than its least-squares baseline. The interval purchase theorem is a correct unit-consistent accounting identity.

These positive results are narrower than the paper's platform. The information lower bound concerns deterministic point-value information for a one-dimensional uniform innovation, a fixed AVaR level, and a convex Lipschitz continuation class. It gives neither a randomized lower bound nor a multivariate tractability result. The oblique-ridge example is an approximation example, not an action-loss or policy-regret separation, and a conventional method supplied with the same oblique hinge is equivalent. The readout theorem obtains nonworsening by validating both candidates and retaining the smaller span; it does not show that residual-span minimization improves the action certificate or the delivered service. The purchase theorem becomes economically informative only after externally credible prices, acquisition costs, and policy-cost intervals are supplied.

The new experiment is particularly informative because it exposes that last distinction. Across all 36 matched least-squares/certificate-aware pairs, the certificate-aware fit strictly reduces the validated residual span. Yet it reduces proposal rejections in only 11 cells, leaves five unchanged, and increases them in 20. Total first-proposal rejections rise from 644 under least squares to 757 under certificate-aware fitting. The effect is most adverse for the quadratic family: its median relative span improvement is about 29.1 percent, but rejections rise from 91 to 210 and worsen in 10 of 12 cells. ReLU rejections are essentially unchanged, 286 versus 287. Spline rejections fall modestly, 267 to 260. This is strong evidence that the chosen global residual objective is not reliably aligned with the action-relevant certificate.

Complete work remains favorable to the conventional quadratic service. At risk levels 0.50 and 0.75, quadratic least squares has median 32-decision workload times of approximately 0.589 and 0.580 seconds. ReLU certificate-aware times are approximately 0.749 and 0.731 seconds; ReLU least-squares times are approximately 0.758 and 0.759 seconds. The operation ledger gives the same ordering: quadratic least squares uses approximately 4.71 and 5.43 million terminal proposal queries, compared with approximately 10.00 and 10.94 million for certificate-aware ReLU. Stored continuations improve on the online service, but the neural representation does not define the complete-work frontier.

The purchase grid does not reverse that conclusion. Of 1,800 conditional cells, 156 are classified as adoption, 199 as rejection, and 1,445 as unresolved. Every certified adoption is relative to the online solver. No learned or certificate-aware service is certified adopted over quadratic least squares. The grid uses the distribution-free policy-cost difference bound `[-1/256,1/256]`, observed clock ranges, externally selected compute prices, and externally selected fees. It is a sensitivity calculation, not an empirically calibrated economic purchase result.

R97 therefore establishes three useful facts: a narrow deterministic AVaR information exponent, a safe validate-and-retain readout construction, and a negative empirical finding about certificate-oriented fitting. It does not establish a specifically neural advantage, a broad new theory of continuous-risk information, or an economic result that changes a substantive conclusion. For Econometrica, the contribution remains below the required threshold.

## 2. Scope of review and independent checks

I reviewed the pinned article, supplement, response, protocol, release and finalization ledgers, new theorem and proof files, R96 retained comparison, all R97 generated tables, machine-readable campaign summaries, operation counts, price grid, independent audit receipt, workflow record, and publication artifact.

I downloaded artifact `11871551096` and verified its SHA-256 digest. I recomputed the finite-catalogue summaries with a separate standard-library script deposited with this report. The audit verifies all 24 source/PDF identities listed by the release, all 84 acquisition-process exit codes, all 42 timing-process exit codes, the 36 matched span comparisons, the operation ledger, the price-grid classifications, and the exact counts in the independent audit receipt. The result was `passed`.

This review did not refit the models, rerun the Bellman campaign, create new policy observations, or independently prove every inherited theorem. The independent proposal implementation covers all 32,768 retained R96 arm-state proposals and selected exact endpoints, but it does not independently implement feature selection, interval-aware fitting, coefficient rounding, or whole-domain validation. The downloadable artifact also omits some inherited repository modules required to execute every new test in isolation. These are reproducibility limits, not evidence that the successful remote workflow failed.

## 3. Assessment of the new theory

### 3.1 Deterministic AVaR information lower bound

The proof is credible. Running the deterministic adaptive algorithm on a quadratic tail and replacing that tail by its chords after the transcript is fixed produces two convex, monotone, `K`-Lipschitz functions with the same query values. Their AVaR difference is the integral of the chord error over the tail. Convexity of the cube gives the stated lower width. The construction properly handles adaptive query locations and is stronger than merely showing sharpness of one fixed quadrature pair.

The result must nevertheless be stated narrowly. It is a deterministic, univariate, point-value oracle lower bound for a uniform law and a fixed AVaR level. It does not cover randomized algorithms, derivative or formula access, nonuniform laws, multiple innovations, or a continuation supplied in a representation that can be integrated analytically. The lower and upper constants also have opposite dependence on `1-alpha`; the theorem matches the exponent at fixed `alpha`, not a tail-uniform constant.

The relationship to classical information-based complexity needs a sharper novelty map. The indistinguishable-input method, convex integration bounds, and AVaR tail representation are classical ingredients. The paper's new object appears to be the explicit tail construction tied to the recursive-policy certificate. That is useful, but it is not a broad new complexity theory for continuous-risk dynamic programming.

### 3.2 Oblique representation comparison

The corner-difference argument for additive functions and the diagonal reduction for total-degree-two polynomials are sound. The proposition correctly identifies a geometry that one oblique ReLU represents exactly while the two restricted comparator classes cannot.

It does not identify a neural numerical advantage. A conventional oblique-hinge dictionary represents the same function exactly. The proposition gives no lower bound on action error, policy regret, endpoint work, acquisition cost, or required design rank for the actual investment continuation. It is an illustrative approximation separation and should be presented as such.

### 3.3 Verified readout improvement

The validate-and-retain proposition is correct and useful as a safety wrapper. It separates a numerical candidate generator from certificate authority: the rounded candidate is checked on the whole domain and retained only when its validated residual span is no worse.

The proposition is also close to a selection tautology. It guarantees improvement in the metric used to select the candidate, not alignment of that metric with the Bellman action gap. The new experiment shows that this distinction is first order. A top-journal contribution would need an action-aligned theorem—for example, conditions under which the acquisition objective controls proposal rejection, expected endpoint work, or policy-cost resolution on a declared context law.

### 3.4 Purchase frontier

The factor `B` correcting the per-decision/whole-workload mismatch is essential, and the interval subtraction is correct. The theorem cleanly separates policy cost, online work, acquisition cost, fixed fees, and workload count.

The empirical frontier remains conditional. Clock ranges are descriptive observations rather than future-hardware confidence bounds, the policy interval is the broad deterministic `[-1/256,1/256]`, and prices and fees are externally chosen. The grid classifies sensitivity regions; it does not estimate an economically meaningful adoption decision.

## 4. Numerical assessment

### 4.1 Certificate span and action-relevant rejection move in different directions

All 36 certificate-aware candidates are retained and strictly reduce the validated residual span. The median relative reduction is about 20.9 percent. Yet aggregate proposal rejections increase by 113, from 644 to 757.

| Family | Median relative span reduction | LS rejections | CA rejections | Improved / tied / worsened cells |
|---|---:|---:|---:|---:|
| Quadratic | 29.1% | 91 | 210 | 1 / 1 / 10 |
| ReLU | 18.0% | 286 | 287 | 5 / 2 / 5 |
| Spline | 20.9% | 267 | 260 | 5 / 2 / 5 |

The quadratic result is especially important: the globally tighter residual is accompanied by far more rejected first proposals. Thus the certificate-aware objective should not be presented as a service-level success. The scientifically interesting result is the misalignment itself.

### 4.2 Complete workload and operation counts favor quadratic least squares

For rank six and 1,024 labels, the medians are:

| Risk | Online | Quadratic LS | Quadratic CA | ReLU LS | ReLU CA | Spline LS | Spline CA |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.841 | 0.589 | 0.694 | 0.758 | 0.749 | 0.768 | 0.753 |
| 0.75 | 0.849 | 0.580 | 0.678 | 0.759 | 0.731 | 0.734 | 0.729 |

These are descriptive clocks from three repetitions, not sampling distributions. However, the machine-independent operation ledger supports the same ordering. Quadratic least squares requires substantially fewer proposal queries than either ReLU arm. The certificate-aware fitting cost also makes quadratic CA slower than quadratic LS despite its smaller residual span.

### 4.3 Purchase regions do not support a neural adoption claim

The 1,800-cell grid gives 156 adoption, 199 rejection, and 1,445 unresolved cells. The detailed breakdown is decisive: quadratic LS is adopted over online in 48 cells; other stored services are sometimes adopted over online; but every comparison against quadratic LS has zero adoption cells. Certificate-aware quadratic has 22 rejection cells against quadratic LS, ReLU CA has 30, and the other learned services have 33 each. The evidence supports stored continuations in some price regimes, not neural or certificate-aware dominance.

### 4.4 The retained R96 economic comparison remains unresolved

All twelve retained simultaneous policy-cost intervals cross zero. They establish equivalence at the engineering margin but do not identify welfare improvement. Point estimates favor the online service against every stored continuation. R97 appropriately preserves this evidence, but no new population policy-cost campaign is executed for the 84 newly fitted actors.

### 4.5 Scale remains narrow

The active experiment is still a two-dimensional, two-date, scalar-control investment problem with two AVaR levels. The product quadrature theorem discloses a Cartesian evaluation burden, and the historical vector experiment discloses adverse horizon growth. R97 does not execute a longer-horizon, multiple-control, multiple-innovation continuous-risk tournament.

## 5. Reproducibility and audit quality

The source-bound release is unusually strong. The successful workflow, artifact digest, PDF hashes, protocol/source identities, preserved failed CI attempt, development disclosure, independent proposal replay, exact-rational statistics, and rational endpoint checks are all valuable. The report found no discrepancy in the deposited finite catalogue.

Two limitations remain material. First, fitting is not independently reimplemented. The independent code verifies proposals after the stored models exist, not the data-to-model acquisition path that is central to R97. Second, the referee artifact is not standalone: some inherited modules needed by the new scripts remain outside the downloadable package. A container or lockfile with the full executable dependency closure would improve the publication boundary.

## 6. Blocking concerns

### B1. Neural specificity remains unestablished

Validity, recursive qualification, the AVaR enclosure, the information lower bound, and the fallback are representation-neutral. The ReLU family is not the complete-work winner and is never certified adopted over quadratic least squares.

### B2. The information-complexity result is too narrow for the platform claim

The theorem is a specialized deterministic one-dimensional oracle result. It does not establish randomized, multivariate, nonuniform-law, or end-to-end Bellman complexity lower bounds.

### B3. The representation result is not decision-theoretic

The ridge example separates restricted approximation classes but does not separate policies, service work, or economic outcomes. A conventional method with the same hinge is equivalent.

### B4. The certificate-aware objective fails its intended service connection

It improves residual span in 36 of 36 cells but worsens aggregate rejections and most quadratic cells. The missing theorem is the connection from the trained objective to action-relevant resolution.

### B5. Complete work favors a strong conventional method

Quadratic least squares is faster, uses fewer proposal queries, and has no neural acquisition overhead. R97 therefore does not shift the computational frontier toward NBO-specific representation.

### B6. The purchase exercise is conditional sensitivity, not economic identification

No learned service is adopted over quadratic least squares. Prices and fees are external, clocks are descriptive, and the policy interval is broad. The exercise does not change an economic conclusion.

### B7. The new 84 actors lack direct population policy-cost inference

R97 transfers only the uniform deterministic qualification bound to the new services. The R96 statistical intervals belong to different frozen actors and cannot establish the new actors' mean-cost ordering.

### B8. Independent verification stops before fitting

Feature selection, interval-aware fitting, rounding, domain validation, and serialization are not independently reproduced. This is the critical new acquisition stack.

### B9. The active submission remains cumulative and disproportionate

A 47-page article, 37-page supplement, and 230-page appendix are excessive for the narrow current theorem and negative acquisition experiment. Historical preservation need not determine the active submission's length.

### B10. The negative result is more compelling than the platform claim

The strongest new fact is that a valid global residual objective can fail to improve delivered decisions. The manuscript should either make that misalignment central or supply a new action-aligned objective and theorem.

## 7. Major changes required for a new submission

### M1. Recast the paper around one method-neutral question

Ask when a stored continuation can be safely purchased for recursive-risk dynamic decisions. Treat neural networks as one optional representation, not the source of validity.

### M2. Establish the true novelty of the information theorem

Give a theorem-by-theorem comparison with information-based complexity. Add a genuinely new randomized, nonuniform-law, multivariate, or Bellman-compositional result, or present the current theorem as a specialized supporting lemma.

### M3. Develop an action-aligned acquisition objective

Construct a loss that controls rejection, endpoint work, or policy-cost resolution on a predeclared context law. Prove the connection and validate it prospectively against complete work.

### M4. Expand the conventional geometry frontier

Compare ReLU with conventional oblique hinges, adaptive triangulation, convex regression, and representation-neutral basis selection under equal information, rank, acquisition, and validation budgets.

### M5. Treat the negative result as first-class evidence

Report aggregate and cell-level rejection changes beside span improvements, explain where the global objective allocates approximation effort, and do not label 36/36 span reduction as delivered-service success.

### M6. Execute a consequential application or narrow the claim

Either calibrate policy margins, compute prices, fees, and workloads in an application where adoption matters, or state that the paper is about numerical certification rather than economic purchase.

### M7. Add a genuine scaling experiment

Vary horizon, controls, innovation dimension, and risk level under matched comparators. Report product-point counts, memory, endpoint work, acquisition, and complete service work.

### M8. Strengthen timing evidence

Use more repetitions, record or control processor state, and make operation counts primary. Predeclare the inferential target for deployment clocks if a probabilistic purchase claim is desired.

### M9. Independently reimplement fitting and package a standalone environment

Reproduce feature selection, interval-aware fitting, rounding, whole-domain validation, and serialization independently. Include a container or lockfile and all inherited modules needed to run the new tests from the artifact alone.

### M10. Shorten the active submission substantially

Move historical material to an archival companion. The active article should contain only the current qualification theorem, precise information result, acquisition objective, matched experiment, and supported economic interpretation.

## 8. Minor comments

1. State `N^{-2}` consistently as an error-versus-information rate; “information exponent two” is easy to misread.
2. Put “deterministic, point-value, univariate, fixed-alpha” adjacent to every high-level summary of the lower bound.
3. Discuss the opposite tail-level behavior of the lower and upper constants as `alpha` approaches one.
4. The readout coefficient bounds are acquisition restrictions, not characterizations of the best approximation; report sensitivity.
5. Distinguish validated residual span from Bellman action gap in terminology and tables.
6. Report rejection changes beside every span improvement.
7. Label the acquisition bracket as an observed engineering range, not a confidence interval.
8. State visibly that there are zero adoption regions over quadratic least squares.
9. Compare the certification contribution carefully with existing verified approximation and HJB-residual literatures.
10. The title should not carry more neural-specific content than the theorem and evidence identify.

## 9. Recommendation

R97 is rigorous, transparent, and substantially better organized scientifically than earlier revisions. The deterministic AVaR lower-bound construction is credible; the release and audit discipline are excellent; and the complete negative acquisition evidence is valuable. The author deserves credit for preserving the quadratic winner, all zero-crossing economic intervals, and every adverse rejection reversal.

For Econometrica, however, the active contribution remains insufficient. The new information theorem is narrow and built from classical information-based-complexity reasoning. The representation theorem is illustrative rather than decision-theoretic. The certificate-aware objective improves its own validation metric but does not improve delivered decisions reliably. Quadratic least squares remains the complete-work winner, no learned service is certified adopted over it, and no externally calibrated economic conclusion changes.

I therefore recommend **rejection in the present form and closure of the ordinary cumulative revision cycle**. A new standalone paper could be worthwhile if it is shorter, method-neutral, centered on the observed certificate-to-decision misalignment, and supported by an action-aligned theorem, an independent fitting implementation, a broader conventional frontier, and an economically meaningful or genuinely scaled application.
