# Referee Report on "Neural Bellman Operators"

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r84-source-delivery-2026-10-12`  
**Pinned delivery commit:** `c1314494aca25e68f1426b554938e6fe89dd8409`  
**Pinned delivery tree:** `d799d244898baf319960a3f16f202dc2ec6b18e6`  
**Underlying referee-revision commit:** `a84023e693df9c13e01268c8a1c4d02a8e8b1d5e`  
**Underlying science-executed commit:** `9e92417a50129e3abff51f9167ed83466866cb1e`  
**Underlying science-source commit:** `2eac8514e703cc43ad6aba3d4ca8a9b5671c99f7`  
**Pinned main manuscript:** `revisions/2026-10-12-r84/ECTA.tex`, Git blob `f027055925d999d4f6476eb35cd296c018f63e7c`  
**Pinned delivery note:** `revisions/2026-10-12-r84/DELIVERY84.md`, Git blob `eebb0beee08511557f28e040c61169be7bdfb786`  
**Pinned independent audit:** `revisions/2026-10-12-r84/audit/VERIFY84.json`, Git blob `e78630c21e44f7861415c1554618f9481a737f5b`  
**Publication workflow:** `38225828054`, status `queued` at the review freeze  
**Report date:** 12 October 2026  
**Recommendation:** **Reject in the present form and do not continue this cumulative manuscript through another ordinary revision round. A sharply focused paper on economically targeted stopping and certificate-gated Bellman search could merit evaluation, but R84 still does not establish an Econometrica-level neural, computational, or economic advantage, and the latest source snapshot is not a completed review-ready submission.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R84 is a serious and technically competent response to the R67 report. It does not hide the earlier negative comparisons. Instead, it adds an actionwise optimization-to-cost transfer, an economic stopping frontier, a single readout shared across two declared regimes, a complete finite menu of ordinary and hybrid services, and a rational assignment-dual layer that transfers interval-valued costs and measured work into a conditional purchase decision. The accompanying exact-arithmetic audit is unusually transparent. The source-delivery note also correctly distinguishes scientific execution from a completed publication package.

I find the principal new mathematical statements internally coherent under their stated hypotheses. The actionwise theorem maps a qualification sublevel into a set of possible first-date actions and then into an original-law cost band. The stopping-frontier theorem organizes those bands over optimization tolerances. The common-readout statement sums contextwise certificate bounds under one coefficient vector, and the finite-menu and assignment results apply elementary minimization and weak duality correctly. I did not locate an algebraic contradiction in this chain.

The revision also improves the empirical record. It retains 336 complete services, including 208 ordinary and 128 hybrid services, with all expected statuses. It reports 48 fitting warnings rather than deleting them. A common readout is constructed by exact rational arithmetic and receives a finite dual-gap certificate. The independent audit checks 2,548 qualification certificates and 16,548 assignment inequalities without invoking the optimization implementation. No new fitting attempt or new independent policy-cost row is mislabeled as evidence.

These are meaningful repairs. They do not, however, resolve the central Econometrica question.

The strongest R84 result remains a method-neutral certification and stopping architecture. Correctness is supplied by finite action menus, original-law interval calculations, verified Bellman bounds, protected fallback, and weak duality. The word "neural" is not doing the identifying work. The exact finite-catalogue winner in the small task is a hybrid combining the certified readout with an analytic endpoint. In the harder task, that readout lowers the chosen deterministic work ledger but is slower in complete process time than adaptive search. The direct policy-cost contrasts remain unresolved in sign. The assignment separation is therefore conditional on externally chosen prices, fees, and a particular work measure; it is not an estimated economic gain.

The theoretical expansion is also narrower than the title suggests. The actionwise transfer fixes a finite first-date partition, a finite action menu, and a common continuation policy. The common-readout result is a finite-catalogue compatibility statement, not an approximation or generalization theorem for unseen states, tasks, or equilibria. The assignment result is an auditable accounting device, not a new economic identification argument. The two-control evidence continues to display severe horizon growth.

Finally, the latest branch is explicitly a source-delivery snapshot, not a completed review-ready package. At the review freeze, the full ordinary-LaTeX publication workflow was still queued. The repository states that the latest PDF, nonempty bibliography, clean archive reconstruction, visual inspection, and final delivery manifest remain gated on that workflow. A journal referee should not treat an older PDF or a source push as the final submission.

My recommendation is therefore rejection in the present form. The project contains publishable ideas, but the best route is a new, sharply bounded numerical-method paper centered on economically targeted stopping for certified Bellman search, with a predeclared independent evaluation, calibrated economic margins, a hardware-independent complexity ledger, and a completed reproducible package.

## 2. What R84 successfully adds

### 2.1 Actionwise optimization-to-cost transfer

R84 improves materially on a binary worst-case charge for uncertified cells. Given a fixed first-date partition, finite action menus, a common continuation, and interval enclosures for retained action contrasts, the theorem encloses the policy cost of every readout in a qualification sublevel. This is a valid deterministic transfer on the simultaneous attained-policy event. It is useful that ties are retained and that the paper does not present an inconclusive switch certificate as an observed policy failure.

### 2.2 An economic stopping frontier

The stopping-frontier theorem makes explicit that optimization tolerances and economic losses have different units. The finite knot construction is operational: once the actionwise bands are available, one can determine sufficient replacement or equivalence regions without another optimizer call or another policy-cost observation. The endpoint convention at switch knots is handled correctly.

### 2.3 A genuinely common readout on declared catalogues

The revision no longer reports only separately tuned readouts and then describes them as compatible. A single rational coefficient vector is evaluated across the two declared context catalogues. Contextwise certificate validity survives the shared parameter restriction, and the summed unresolved-work bound is auditable.

### 2.4 Complete-menu accounting

The comparison contains ordinary and hybrid services, analytic and learned proposals, loading and validation costs, Bellman work, path evaluation, serialization, and shutdown. The exact finite-catalogue winner is identified without deleting adverse arms. The harder-task wall-clock reversal is visible.

### 2.5 Conditional economic transfer with an exact dual certificate

For a declared finite assignment problem, interval-valued policy costs, deterministic work charges, prices, and fees are propagated through a rational primal-dual certificate. A zero assignment duality gap is a strong reproducibility feature. The paper appropriately states the decision as conditional on the declared economic inputs.

### 2.6 Independent exact-arithmetic checking

The deposited audit uses fractions, an independently coded antiderivative calculation, and a sparse-support dual rather than importing the construction module or an LP solver. It checks every new winner, joint event, and economic dual in its stated scope. This is a high standard of internal auditability.

### 2.7 Honest separation of science and publication

The delivery note does not claim a latest PDF or page count that has not been produced. It records that source accessibility, numerical execution, and final publication are separate gates. This is the correct disclosure.

## 3. Blocking concerns

### B1. The latest object is not a completed review-ready submission

The source-delivery branch states that the latest ordinary-LaTeX publication workflow has not completed. At the review freeze, workflow `38225828054` remained queued. Consequently the latest main article, supplement, appendix, bibliography, log audit, clean archive reconstruction, rendered-page inspection, and final delivery manifest have not been jointly verified for the reviewed source.

This is not a cosmetic issue. R84 changes tables, appendix layout, cross-references, and the central theorem-to-evidence chain. An older PDF cannot substitute for compilation and visual inspection of the current source. The journal package is incomplete.

### B2. The active title and platform remain broader than the proved R84 transfer

The actionwise theorem fixes a finite first-date acquisition partition, a finite action menu on each cell, and a common feasible continuation after that date. The executed transfer is tied to the two-date expected-cost economy and inherited finite-bin evidence. This is not yet a generic result for the full range of diffusions, recursive preferences, endogenous preferences, temporal selves, and games retained by the NBO platform.

The manuscript should not use archival breadth as evidence for the scope of the R84 theorem. The active title, abstract, and conclusion still invite a broader interpretation than the new theorem supports.

### B3. Method-specific identification is still absent

The certificate, actionwise transfer, protected fallback, economic frontier, and assignment dual are method-neutral. A ReLU, Bernstein polynomial, quadratic, spline, nearest-action rule, analytic endpoint, or any other feasible proposal can enter the same verifier. The common readout is one possible query policy; it is not the source of validity.

The small-task exact winner is explicitly a hybrid of a certified readout and an analytic endpoint. That is a useful service, but it does not identify a neural advantage. R84 is strongest when read as a paper about certificate-gated search and stopping, not Neural Bellman Operators as a representation-specific method.

### B4. Common-readout compatibility is a finite-catalogue result, not a generalization theorem

The shared-readout statement is valid because one coefficient vector is evaluated on finitely many declared contexts and contextwise guarantees are summed. It does not show that a low-complexity shared readout exists for a population of states, for a new task, or for a longer horizon. Nor does it provide an approximation rate, sample-complexity result, sequential generalization guarantee, or stability result under endogenous context generation.

The exact rational construction is therefore a strong finite audit, but it does not yet support the broader claim that one learned operator transfers across regimes.

### B5. The exact finite-catalogue winner does not establish ex ante superiority

The complete menu is valuable as a descriptive finite comparison. Selecting its exact winner on the same frozen catalogue does not by itself establish that the winning service will dominate on a new workload distribution. R84 generates no new independent policy-cost rows and no new fit attempts. The finite-catalogue choice therefore needs either a separate prospective test or a theorem connecting the selection rule to future workloads.

The paper should distinguish "best among these completed receipts" from "preferred service before observing a new workload."

### B6. Deterministic work and complete wall-clock time point in different directions

For the small task, the certified-readout plus analytic-endpoint service has the lowest declared deterministic work and a lower complete time than adaptive search. For the harder task, the same type of service lowers the deterministic work ledger but is materially slower in complete process time: approximately 16.50 seconds versus 11.50 seconds for adaptive search in the retained summary.

This divergence is not a nuisance to average away. It means the work weights are decision-defining. The paper needs a predeclared, machine-independent operation model tied to actual bottlenecks, plus timing uncertainty and cross-machine evidence. A purchaser should not be told that a service is cheaper unless the price vector corresponds to the resources actually consumed.

### B7. Direct policy-cost differences remain unresolved

The transfer record retains the direct original-law contrasts rather than replacing them with certificate widths. That is correct. Their signs nevertheless remain unresolved. The retained finite family of policy-cost intervals crosses zero, including the comparisons involving the selected readout services.

R84 therefore does not identify a lower expected economic cost for the readout, the hybrid winner, or a neural service. The assignment result can still select a service because of declared work prices and fees, but that is a conditional computation decision, not evidence of an economic policy improvement.

### B8. The assignment separation is conditional bookkeeping, not an identified economic result

The exact rational assignment dual proves the optimum of the supplied finite assignment problem. It does not identify the values of computation, deployment fees, or the monetary conversion of normalized policy loss. Those inputs are declared by the analyst. Separation from a baseline can be produced by the chosen resource prices even when every direct policy-cost gain interval contains zero.

The paper needs a sensitivity region over prices and fees, an economically defended calibration, and a clear account of which conclusions hold uniformly over that region. Without this, the economic transfer is an auditable decision formula rather than an Econometrica-level economic finding.

### B9. Predictor reliability is still protected by conventional fallback

All 336 services attaining their expected statuses is strong evidence for the verifier and execution harness. It is not evidence that the fitting procedures are uniformly reliable. The catalogue retains 48 warnings. A bad predictor can still return a certified policy because the protected conventional routine absorbs its failure.

The paper should separately report predictor failures, fallback frequency, certificate closures, and the incremental work caused by each warning class. Service reliability and predictor reliability are different estimands.

### B10. The horizon bottleneck remains unresolved

The inherited two-control, two-innovation experiment still grows from 44 Bellman action queries at two dates to 2,957 at three dates and roughly 8.1 million at four dates. The absence of a state lattice does not remove the descendant tree. R84's menu and assignment layer do not change this computational fact.

A top numerical-method paper needs either a new complexity result, a pruning/decomposition method that changes the horizon frontier, or a candid restriction of the claim to short horizons.

### B11. Independent verification is strong but not yet end to end for the reviewed package

`VERIFY84.json` independently checks the new winners, joint events, and assignment inequalities. Its own scope states that inherited bin qualification is rerun separately by the full publication build. That build had not completed at the review freeze. The latest typeset package and the complete inherited-to-new evidence chain therefore lack one final jointly bound audit.

In addition, exact recomputation of summary arithmetic is not the same as an independently implemented Bellman solver, path enclosure engine, and large vector recursion. The heaviest numerical objects still deserve a second implementation.

### B12. The theoretical novelty is not yet commensurate with the manuscript's scale

The actionwise transfer and stopping frontier are useful. Under the stated finite-menu assumptions, however, their proofs are short conditioning, set inclusion, monotonicity, and interval propagation arguments. The common-readout theorem sums valid contextwise bounds, and the assignment theorem invokes finite minimization and weak duality.

These results can anchor a focused methods paper, especially when coupled to a decisive experiment. In the present cumulative manuscript, they do not yet justify the breadth, title, and Econometrica-level contribution claim.

## 4. Major comments and required changes

### M1. Complete and freeze one review-ready package

Produce the latest main article, supplement, appendix, response, bibliography, build logs, rendered-page inspection, clean archive reconstruction, and final delivery manifest from one pinned source commit. Do not ask a referee to combine the latest source with an older PDF.

### M2. Reframe the paper around the identified contribution

Center the article on economically targeted stopping and certificate-gated Bellman search. State that proposals are optional and method-neutral. Treat neural, polynomial, analytic, and conventional proposals as competing query policies rather than making neural representation the validity claim.

### M3. State the exact scope of the actionwise theorem

Put the fixed first-date partition, finite menu, and common-continuation restriction in the abstract and main theorem discussion. Either extend the result recursively to complete multi-date policy classes or refrain from presenting it as a general NBO policy-cost transfer.

### M4. Prospectively validate the common readout

Freeze the shared readout before a new predictor-independent stream of states and tasks. Report its certificate score, fallback work, complete work, and policy cost on that stream. A finite-catalogue construction can remain as a training audit, but it should not be the only evidence of transfer.

### M5. Predeclare and validate the resource metric

Define a hardware-independent operation ledger covering endpoint evaluations, descendants, interval operations, rational recovery, model evaluation, loading, serialization, and memory. Estimate the mapping from this ledger to wall-clock and energy on more than one machine. Report timing uncertainty rather than relying on two closely spaced repetitions.

### M6. Design policy-cost inference around an economic margin

Choose a prespecified superiority, noninferiority, or equivalence margin with economic meaning. Decompose interval width into sampling variation, bin enclosure, acquisition ambiguity, support bounds, and arithmetic error. Select sample size and precision to resolve that margin.

### M7. Calibrate the assignment inputs and give uniform sensitivity results

Justify computation prices, adoption fees, and the value of normalized policy loss in an application. Report the region of price-fee vectors for which the selected assignment is unchanged. Separate conclusions driven by policy-cost intervals from conclusions driven entirely by resource prices.

### M8. Add an out-of-sample menu-selection experiment

Use the menu rule to select a service on a training or calibration catalogue, then execute the selected service and all main comparators on a distinct workload catalogue. Report regret of the selector relative to the ex post menu winner. This is necessary to turn exact finite-menu ranking into a prospective method.

### M9. Address horizon growth directly

Compare the simplicial verifier with derivative branch-and-bound, adaptive simplex subdivision, sparse quadrature, and at least one trained multi-output proposal under the same certificates. Give a complexity account in horizon, shock dimension, action dimension, and tolerance. If the descendant tree remains unavoidable, narrow the claims.

### M10. Separate predictor diagnostics from verifier diagnostics

For each model family, report fitting warnings, invalid predictions, screen closures, protected fallbacks, zero-progress probes, and incremental work. Do not use 100 percent service return as evidence for training reliability.

### M11. Independently reimplement the critical kernels

Use a separate code path for original-law action contrasts, acquisition branching, interval propagation, common-readout scoring, and the large vector recursion. Preserve all disagreements and bind the independent outputs to the final source commit.

### M12. Reduce and reorganize the manuscript

A new article should contain one theorem-to-algorithm-to-experiment chain. Historical diffusion, recursive-preference, temporal-self, and game material can remain in archival companions. The main paper should not require cumulative version archaeology to determine which claim is active.

## 5. Minor comments

1. Define "exact winner" at first use as a winner only on the frozen finite catalogue and declared work ledger.
2. Put deterministic work and complete process time in adjacent columns throughout.
3. Report the 336-service decomposition, warning count, and missing/failed/timeout counts in the main text, not only generated records.
4. State explicitly that R84 creates no new fit attempt and no new independent policy-cost row.
5. Distinguish the science-source commit, science-executed commit, referee-revision commit, and source-delivery commit in every manifest.
6. Give the simultaneous-family size and error allocation for every policy-cost table.
7. Report how much of each classwide interval comes from attained-policy uncertainty versus optimization-class enlargement.
8. Explain why the common feature map is economically and numerically comparable across `d=2` and `d=8`.
9. Include price-fee breakpoints at which the assignment changes.
10. Label inherited vector evidence as inherited; do not present it as a new R84 experiment.
11. Place all warning messages and their affected services in a compact appendix table.
12. Make the reproduction command fail if the final PDF, bibliography, visual inspection, or clean rebuild is absent.

## 6. A focused publishable route

A credible new submission could be titled:

> **Economically Targeted Stopping for Certified Bellman Search**

Its core should be:

1. a method-neutral pre-query certificate and protected fallback;
2. the actionwise optimization-to-cost transfer with exact scope;
3. the finite economic stopping frontier;
4. one predeclared shared proposal class;
5. a prospective independent validation design;
6. a hardware-independent work model connected to measured cost;
7. direct policy-cost inference at a meaningful margin;
8. price-fee sensitivity for the purchase rule;
9. a vector and horizon comparator study; and
10. an independently implemented, fully frozen publication package.

This route preserves the strongest R84 ideas without asking a neural label, a finite-menu winner, or a conditional assignment price to carry more identifying content than the evidence supports.

## 7. Recommendation

R84 is rigorous, candid, and substantially better than R67. The actionwise transfer, stopping frontier, common-readout audit, full-menu accounting, and exact assignment dual are genuine contributions to reproducible numerical decision making. The repository's refusal to overstate an unfinished publication build is also commendable.

For Econometrica, however, the present manuscript still lacks the required combination of sharply identified novelty, prospective computational advantage, resolved economic consequence, scalable numerical evidence, and completed delivery. The certificate architecture is method-neutral; the selected easy-task winner is hybrid; the harder-task wall-clock result favors adaptive search; direct policy-cost signs remain unresolved; the assignment conclusion is conditional on external prices; and the latest review-ready package does not yet exist.

I therefore recommend **rejection in the present form**, while encouraging a new, focused submission built around economically targeted stopping for certified Bellman search.
