# Referee Report on "Neural Bellman Operators"

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r67-review-ready-2026-10-10`  
**Pinned revision commit:** `eacd3e217ae1e2e9ea6e154b48da7d103159d051`  
**Pinned revision tree:** `57db1bd03f307e19146635b7b37cce3a1c707ccc`  
**Pinned main manuscript:** `revisions/2026-10-10-r67/ECTA.tex`, Git blob `1c3afc1c381f82f01b8a875f4bf1f70285f58ae9`  
**Pinned technical supplement:** `revisions/2026-10-10-r67/supp.tex`, Git blob `af3598a71089dc6cedd916f4c8ca9bea7fd61b95`  
**Pinned response:** `revisions/2026-10-10-r67/response.md`, Git blob `8c2706f50dd8cd021449c4f324f9797f0772ade4`  
**Publication workflow:** `38063998843`  
**Publication artifact:** `11674836596`, SHA-256 `d7f9274c3dca3697e95b22bb62d6d9df14ed0d677859033e0a4850584d8d031b`  
**Report date:** 11 October 2026  
**Recommendation:** **Reject in the present form and do not continue the cumulative manuscript through another ordinary revision round. A new, sharply focused paper on certificate-gated, prediction-guided Bellman search could merit evaluation, but R67 does not establish an Econometrica-level method-specific or economic advantage for Neural Bellman Operators.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R67 is the strongest and most scientifically informative revision of this project that I have reviewed. It is a canonical, source-bound submission with a 42-page article, a 15-page supplement, an 8-page response, a clean archive rebuild, 135 passing tests, and a corrected 212-service numerical catalogue. The revision preserves prior evidence, all fitting warnings, failed reuse, and a substantive path-enclosure error together with an exact counterexample and corrected rerun. The provenance and failure-preservation standard is exceptional.

The new theoretical contribution is real. In the original nonlinear investment economy, the paper derives a pre-query certificate from already purchased Bellman endpoint bounds and a strong-convexity upper chord. A proposed rounded action can be returned without another Bellman query when this certificate closes. If it does not close, safeguarded conventional refinement retains correctness and finite termination. A margin loss bounds additional endpoint work without referring to the unknown minimizing action. A fixed-feature ReLU readout minimizes a convex certificate-aware objective and receives a computable box dual-gap certificate. I found no immediate algebraic contradiction in the pre-query closure theorem, the work-loss inequality, the certified-readout proposition, or the simplicial two-control minorant under their stated assumptions.

The corrected experiment is also substantially stronger than the earlier evidence. It compares ten selector rules, uses eight predetermined fitting seeds, executes twenty-four prospective reuse blocks per process, directly evaluates the new callable policies under the original continuous law, and extends the verifier to two controls and two independent continuous innovations. It distinguishes prediction, certification, policy loss, and complete work rather than treating any one of them as a substitute for the others.

The decisive difficulty is no longer formal correctness. It is contribution identification and economic importance.

The successful object is a method-neutral certified search procedure. A predictor proposes a query location; primitive curvature, verified Bellman endpoints, and conventional safeguarded refinement supply validity. The same gate is available to quadratic, linear, spline, nearest-action, derivative, analytic, and heuristic proposals. R67 shows that learned proposals can participate safely. It does not identify a specifically neural numerical advantage.

The complete cold-start evidence is unfavorable to the ReLU service. In the two-state, two-date task, ReLU reduces the median Bellman-query count by about 2.0 percent relative to adaptive search, but its median complete process time is about 110 percent higher. In the eight-state, three-date task, it uses about 0.7 percent more queries and about 67 percent more complete time. The quadratic selector has a nominal sub-microsecond median advantage in the small task, far below what two uncontrolled-frequency repetitions can identify, and is about 38 percent slower in the harder task. Adaptive search is the clear complete-work winner there.

Prospective reuse produces only a narrow and non-neural positive result. Of twenty-four complete reuse processes, four beat their matched adaptive process; all four are quadratic services in the two-state task. No ReLU reuse process wins. Only one process records a persistent prefix crossing within the twenty-four-block window, and that crossing occurs at the final block. In the eight-state, three-date task, adaptive search wins both repetitions by a material margin.

The direct expected-cost experiment measures the right estimand but does not rank the methods. All twelve simultaneous paired intervals contain zero. Their widths range from approximately `0.05283` to `0.06604`, while the largest absolute raw mean difference is approximately `3.92e-5`. The median interval half-width is roughly 2,833 times the corresponding absolute raw mean difference. The experiment is too conservative or too small to identify economically relevant differences among the callable controllers.

The vector extension exposes the unresolved horizon problem. The simplicial two-control verifier requires 44 Bellman action queries at two dates, 2,957 at three dates, and about 8.1 million at four dates. Complete process time rises from roughly 0.3--0.4 seconds to 7--11 seconds and then to 530--841 seconds. The state lattice is absent, but the two-innovation descendant tree remains dominant. The vector catalogue contains only the simplicial verifier and four designed paths per service; it is not a comparative trained two-output experiment or a long-horizon scalability result.

R67 therefore establishes a credible and reproducible theorem--algorithm--audit chain for safe prediction-guided Bellman search. It does not establish that a neural selector improves the complete-work frontier, lowers expected policy cost, or unlocks a substantive economic result unavailable to strong conventional search. I recommend rejection in the present form. A focused new paper could be valuable if it treats the predictor as an optional query policy, isolates its incremental contribution against equally flexible non-neural proposals, executes a convincing repeated-use design, and obtains a direct economic comparison with useful precision.

## 2. What R67 successfully repairs

### 2.1 The pre-query decision is computable

The earlier localization result depended on the distance to an unknown minimizer. R67 replaces that object by a strong-convexity upper chord constructed from verified endpoint upper bounds and the current global lower certificate. The resulting screen uses information already present in the numerical transcript.

### 2.2 Prediction cannot forge a certificate

A predictor supplies only a feasible proposed action. It supplies neither a Bellman endpoint nor a lower bound. A failed screen changes no certificate and authorizes no unprotected split. The protected fallback therefore preserves feasibility, termination, and the original-optimum policy account for arbitrary finite predictions.

### 2.3 The work loss and readout objective are auditable

The clipped margin loss bounds the additional endpoint-query count context by context. The validation theorem states the predictor-independent context-law requirement rather than silently treating recursive on-policy contexts as IID. The fixed-feature ReLU readout has a convex objective and a computable optimization gap. The unnormalized squared certificate surplus in the readout objective makes the displayed `F(w)/tau^2` work bound internally consistent.

### 2.4 Strong conventional selectors are retained

The comparison includes adaptive parabolic search, bisection, upper-chord minimization, an analytic derivative proposal, a midpoint heuristic, full quadratic, linear, additive spline, nearest-action, and ReLU selectors. The gate and verifier are common, so the attribution question is visible.

### 2.5 Prospective reuse is executed

Models are fitted and serialized once and then loaded for twenty-four predetermined workloads. Loading, hashing, identity validation, a deliberately stale acquisition-contract identifier, fallback, all queries, durable block records, summary creation, and process shutdown are included in the measured service.

### 2.6 The new callable policies receive direct continuous-law comparisons

The inference services evaluate adaptive, bisection, ReLU, and quadratic callable controllers on common continuous-law paths. The estimand is the actual expected policy-cost difference, not the difference between regret bounds. The paper correctly reports that all signed comparisons remain unresolved.

### 2.7 The two-control theorem is executed and horizon cost is disclosed

The simplicial action minorant, two-shock quadrature allowance, feasible witnesses, and acquired-policy recursion are exercised in the retained two-control model. The very large horizon-four query count and process time are reported rather than hidden behind the absence of a state table.

### 2.8 A substantive numerical error is preserved and corrected

An independent rational trajectory showed that aliased cumulative-cost arrays produced an invalid lower endpoint. R67 preserves the original run, gives the counterexample, allocates independent lower and upper buffers, and reruns the entire fixed catalogue with unchanged random indices. This is exemplary scientific practice.

## 3. Blocking concerns

### B1. The method-specific contribution is not identified

Correctness, termination, feasibility, and original-optimum accuracy are predictor-independent. Neural content changes only the location of some optional interior probes. The same certificate and fallback apply to conventional proposals. The paper establishes safe prediction-assisted search, not a distinctively neural numerical method.

### B2. ReLU query savings do not survive the complete cold-start boundary

The complete service includes imports, training labels, fitting, prediction, Bellman queries, path enclosures, serialization, durable output, and shutdown. In the small task, ReLU saves about 2.0 percent of queries but takes about 2.10 times the adaptive time. In the harder task, it uses more queries and takes about 1.67 times the adaptive time. These are adverse complete-work findings.

The quadratic selector's nominal small-task win is below one microsecond in the median and is not statistically or operationally identified by two timing repetitions with uncontrolled processor frequency.

### B3. Prospective reuse is narrow, task-dependent, and non-neural

Only four of twenty-four complete learned reuse processes beat matched adaptive search, all four are quadratic services in the easy task, and no ReLU process wins. The only persistent prefix crossing occurs at block 24, the final observed block. The difficult task favors adaptive search in both repetitions. This does not support a stable amortized NBO advantage.

### B4. Expected-cost inference has insufficient resolving power

All twelve paired intervals contain zero. Interval widths are about `0.053--0.066`, whereas raw mean differences are at most about `3.92e-5`. The median half-width is roughly 2,833 times the corresponding absolute mean. The experiment cannot identify superiority, noninferiority at an economically chosen margin, or a purchase-relevant gain.

### B5. The certificate-aware training theorem is not yet a benchmark training-to-performance result

The fixed-feature readout proposition is constructive and useful, but the central numerical catalogue retains separately trained L-BFGS and conventional fits. The certified readout is not a full benchmark arm with independent validation contexts, calibrated work-loss generalization, and a demonstrated complete-work advantage. The theorem therefore shows how one could train an auditable predictor, not that the benchmark neural predictor succeeds on the declared tasks.

### B6. The vector extension reveals severe horizon dependence

The two-control, two-innovation service goes from 44 action queries at two dates to 2,957 at three dates and approximately 8.1 million at four dates. The three-to-four-date increase is about 2,741 times in queries and 72--73 times in process time. Removing a state lattice does not solve the descendant-tree problem.

### B7. Independent replay does not cover the largest new computations end to end

The publication replay re-queries ninety distinct scalar comparison services, but it does not independently re-integrate the largest vector trees or every reuse and inference endpoint query. Source hashes and internal consistency are strong, but an independent implementation of the critical large computations is still missing.

### B8. Return reliability is not predictor reliability

All 212 corrected services return and none times out, which is excellent evidence for the safeguarded verifier. It is not evidence that neural fitting is reliable, because conventional refinement absorbs poor proposals. The catalogue contains 48 fitting warnings, all associated with ReLU proposals. Eight fixed seeds are useful finite-catalogue evidence, not a population success probability or a deterministic hidden-layer training theorem.

### B9. The economic purchase conclusion remains unresolved

The purchase formula is correct, but all direct gain intervals cross zero. Compute prices, adoption fees, and the monetary value of normalized loss units are user-supplied rather than estimated. Cold-start evidence favors conventional search, while the observed reuse win is tiny, task-specific, and quadratic. The deposited evidence does not license a specifically neural purchase decision.

### B10. The remaining scope is broader than the established theorem--evidence chain

The active article is more focused than prior revisions, but the title and retained platform still encompass controlled diffusions, recursive preferences, endogenous preferences, temporal selves, and games. The operational and statistical claims established in R67 concern a convex expected-cost investment economy plus a low-dimensional simplicial extension. Preserved historical material is not evidence that the R67 query theorem extends to those distinct domains.

## 4. Major comments and required changes

### M1. Reframe the central contribution

Center the paper on certificate-gated prediction-guided Bellman search. State that the certificate and fallback are method-neutral and that a predictor is an optional query policy whose incremental value must be identified separately.

### M2. Use predictor baselines that isolate representation and information

Organize all predictor comparisons around identical information sets, feature budgets, validation contexts, and training costs. Include the certified fixed-feature readout as an executed arm and compare it with quadratic, linear, spline, nearest-action, derivative, and analytic proposals.

### M3. Validate the work-loss objective prospectively

Freeze the readout, evaluate its predicted work loss on an independent predictor-independent context stream, and compare the validated bound with realized additional queries and complete work. Treat recursively generated contexts with an appropriate dependent-data or sequential design.

### M4. Strengthen the reuse experiment

Use more tasks, more predeclared models, more timing repetitions, and a longer window. Require a stable crossing well before the terminal block. Report machine-independent operation counts and model-load, validation, fallback, and drift-check costs separately.

### M5. Redesign direct policy-cost inference around target precision

Decompose interval width into sampling, bin enclosure, acquisition ambiguity, deterministic support, and arithmetic terms. Select path count and bin precision to resolve a prespecified economic margin. Claim equivalence or noninferiority only with a predeclared economically meaningful margin.

### M6. Add a genuine vector comparison

Compare the simplicial verifier with derivative branch-and-bound, adaptive simplex refinement, and at least one trained two-output proposal under identical certificates. Include direct policy costs and report the horizon-four memory and operation ledger explicitly.

### M7. Independently reimplement the critical endpoint calculations

Use a separate implementation for cumulative path enclosures, acquisition branching, continuous-law endpoint integration, and the large simplicial recursion. Preserve every disagreement as first-class evidence.

### M8. Separate numerical observations from timing claims

Increase timing repetitions where differences are small, control or record processor frequency, and report uncertainty. Prefer machine-independent counts for close comparisons. Distinguish training, model load, prediction, endpoint evaluation, rational recovery, path evaluation, serialization, and shutdown.

### M9. Supply an economically consequential application

Either calibrate the computation/policy tradeoff in an economically interpretable setting or narrow the claim to numerical certification. A top-journal method paper should demonstrate that the method changes a substantive economic conclusion or a broadly important computational frontier.

### M10. Further reduce the platform claim

Keep historical companions in the archive, but let the active article make one claim: a safe, auditable, prediction-guided Bellman query algorithm in a specified convex control class. The title, abstract, and conclusion should not imply numerical validation of the broader historical program.

## 5. A focused publishable route

A credible new submission could be organized around:

> **Certificate-Gated Prediction-Guided Bellman Search**

Its essential components would be:

1. the pre-query closure theorem;
2. deterministic and validated work-loss bounds;
3. the certified fixed-feature readout;
4. a method-neutral safeguarded fallback;
5. prospective predictor validation on independent contexts;
6. an executed reuse frontier with stable break-even evidence;
7. direct policy-cost inference at meaningful precision;
8. a vector comparator study; and
9. an independent implementation audit of the critical interval kernels.

This would preserve the strongest R67 contribution while removing the need to defend a neural or economic superiority claim that the deposited evidence does not support.

## 6. Recommendation

R67 is rigorous, transparent, and materially stronger than its predecessors. Its pre-query certificate, work-sensitive loss, prospective reuse protocol, direct callable-policy inference, and preservation of the enclosure counterexample are all valuable. I encourage the author to develop these ideas further.

For Econometrica, however, the present paper still lacks the required combination of method-specific novelty, complete-work advantage, economic identification, and scope discipline. The strongest positive result is a safe prediction-assisted verifier whose correctness is conventional and whose neural component does not win the main comparisons. The reuse result is narrow and non-neural; the economic contrasts are unresolved; and the vector experiment exposes severe horizon growth.

I therefore recommend **rejection in the present form**, with the possibility that a substantially refocused new submission could merit evaluation.
