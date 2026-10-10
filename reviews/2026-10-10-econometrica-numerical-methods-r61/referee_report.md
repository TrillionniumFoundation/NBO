# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r61-review-ready-2026-10-09`  
**Pinned revision commit:** `19f17cef194b620cfbf9d33e7c78ee051a2dddf0`  
**Pinned revision tree:** `2a7fc185511a78eaf447a01e70f168b05cc839ae`  
**Pinned main manuscript:** `revisions/2026-10-09-r61/ECTA.tex`, Git blob `dcd724c3f2e22ab13cbbcfaa5dceee0cf02bde28`  
**Pinned technical supplement:** `revisions/2026-10-09-r61/supp.tex`, Git blob `31c8932a635722177e72292d6b7eddffac069d4d`  
**Pinned response:** `revisions/2026-10-09-r61/response.md`, Git blob `9c90353fe4268882802496ba6c3bcd12fe0f93bc`  
**Controlling prior advisory review:** `8f56a3ae24ef3ce4383d0e9d1d757bd3ed7378c6`  
**Report date:** 10 October 2026  
**Recommendation:** **Reject in the present form and do not invite another ordinary revision of the cumulative manuscript. A new, sharply focused paper on exact root-free action recovery and stable Bellman certification for analytically integrated neural continuations could merit evaluation after the numerical contribution is isolated from the broader NBO platform, demonstrated at matched original-optimum accuracy, and shown to improve a substantive economic decision relative to strong conventional methods.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R61 is the strongest and most complete version of this project that I have reviewed. It resolves the publication-threshold defects that affected several intermediate revisions. The repository now identifies one canonical review-ready branch; the article, technical supplement, response, complete development article, complete proof companion, and two retained development documents are all bound to a clean archive reconstruction. The final delivery manifest records 8,294 files, 204 passing tests, source and label preservation, and byte-identical rebuilding of all seven documents. The current 91-page article and 58-page supplement have no undefined references, duplicate labels, missing characters, or overfull boxes. These facts materially improve the credibility and reviewability of the submission.

The new mathematics is also substantive. R61 replaces the favorable-separation premise behind the earlier interval screen by an exact root-free construction for the integrated scalar action objective. On every activation piece, the objective is a rational quartic with nonnegative fourth-order coefficient. Its discrete second difference is nondecreasing on the nonnegative action lattice. A concave prefix and a convex tail can therefore be searched with exact rational sign queries, preserving flat segments, adjacent ties, signed cancellation, and the inherited smallest-index convention. The theorem supplies an explicit rational-operation count and a conservative bit-length account. I independently checked the central discrete-curvature candidate rule on 50,000 randomly generated exact rational quartic sequences and found no mismatch with exhaustive minimization.

The paper also separates scalar action structure from action dimension. It gives an exact signed-vertex formula for ReLU ridges under finite mixtures of box-uniform innovations and a terminating rational subdivision method for constrained multi-action lattices with a lexicographic tie rule and an exact fallback. In addition, the revised Bellman section correctly distinguishes one-step interval inclusion from stability of a propagated endpoint map. The fixed-cover min/max/averaging maps used by the executable verifier are proved order preserving and discount-nonexpansive, and the paper supplies a counterexample showing why inclusion alone would not suffice.

R61 further makes meaningful progress on the original accuracy question. A common-reference calculation produces all-state bounds against the original continuous-action Bellman optimum in the two-state, two-date model. The centered ladder reaches a maximum datewise gap of approximately 0.03979 at its final rung, thereby attaining the declared tolerances one-half, one-quarter, one-eighth, and one-sixteenth, but not one-thirty-second. The paper then applies the same lower table to every distinct actor actually returned by the two-date prospective services, without changing those policies. Three of the five distinct actors receive all-state bounds between approximately 0.06778 and 0.07176; two remain near 0.30330. This is a genuine improvement over assigning a separate comparator policy’s certificate to a neural policy.

The revision is commendably candid about adverse outcomes. It reports that the finite-difference solver is slower on short, wide networks; that the multi-action adaptive subdivision is slower than exhaustive enumeration despite fewer exact evaluations; that the strict eight-dimensional target remains exhausted by every generator; that common-only is the fastest complete service in every matched group; and that no direct policy-cost interval identifies a lower native-ReLU cost than either common-only or quadratic-native.

Those adverse facts are also the reason I cannot recommend publication in Econometrica.

The fresh 96-service catalogue compares four generators at common economic targets. Eighty services attain their target and sixteen exhaust the budget. Every generator has the same 20/24 attainment count because the failures occur in the same strict eight-dimensional cell. Common-only is the fastest complete warm service in all 24 task–target–seed–worker groups. The native ReLU service is slower on average and in median than both common-only and native quadratic. Relative to the mathematically identical screened-ReLU policy, root-free native search is faster in 22 of 24 complete services, but the median end-to-end saving is only about 1.36 percent and two services are slower. The large microbenchmark savings at 513 lattice points therefore do not translate into a decisive complete-service advantage.

The economic comparisons are equally clear. Across the twelve mathematical designs, native ReLU and common-only have seven exact policy identities and five unresolved expected-cost differences; the same is true for native ReLU and quadratic-native. None of the nonidentity intervals identifies lower native-ReLU cost. Across the two worker repetitions, these become fourteen identities and ten unresolved intervals per conventional comparator, not twenty-four independent economic observations. Thus R61 establishes exact implementation improvements for a neural subroutine and stronger policy certificates, but not a neural policy benefit.

The original-optimum result also remains much narrower than the platform claim. It is executed only for the two-state, two-date economy. None of the five actually returned actors reaches one-sixteenth under the fixed-policy revalidation. The higher-dimensional prospective services still stop on an initial-law improvement target rather than an all-state Bellman-optimality target. The strongest direct original-optimum result belongs to a separately designed, conventional interval construction whose centered extension was frozen after the uncentered failure was observed. The chronology is disclosed correctly, but the result should be interpreted as a valuable follow-up accuracy study, not as prospective validation of the whole NBO service family.

The multi-action extension illustrates the same distinction. It is an exact and valid witness-recovery experiment, but it is not a complete two-control policy or welfare study. Adaptive subdivision is roughly 2.7–3.2 times slower than exhaustive search in the reported summary cells, and it invokes exact fallback in the larger cases. The formula also retains exponential dependence on the number of independent uniform components and product-lattice dependence on action dimension.

R61 has therefore reached a technically credible but focused contribution: exact action recovery for a special integrated neural objective, together with stable Bellman certification and exemplary evidence preservation. It has not established that the NBO platform is a better numerical method for economics than strong conventional alternatives, that its learned continuation is economically necessary, that it scales to difficult action dimensions or general shocks, or that it unlocks a substantive economic result. The active publication remains too broad for what the evidence proves.

## 2. What R61 successfully repairs

### 2.1 Canonical, immutable, and reproducible delivery

The latest branch is a genuine review-ready object. The root entry point names R61, the final commit binds the ordinary sources and generated outputs, and the clean archive rebuild reproduces all seven PDFs byte for byte without network access. The publication audit reports 204 passing tests, including 18 new R61 tests, and no new training service or policy-cost observation created by publication.

This resolves the threshold publication objection completely.

### 2.2 Exact action recovery no longer relies on favorable separation

The interval screen remains correct but can retain many actions under flatness or near ties. R61’s finite-difference theorem addresses that case directly. The discrete curvature result permits exact location of a concave-prefix/convex-tail minimum by rational bisection and a bounded set of final objective comparisons. Flat objectives and adjacent exact ties are preserved rather than perturbed into uniqueness.

The implementation therefore has a valid exact answer even when screening is uninformative.

### 2.3 The principal timing confound is isolated

The new native two-by-two factorial crosses activation reduction with exhaustive or finite-difference search while holding language, rational arithmetic, objective, lattice, tie rule, and final postcheck fixed. This is the correct response to the R59 concern that the prior algebraic-versus-screened contrast changed several mechanisms simultaneously.

At a 513-point lattice, finite differences save a median of approximately 61–73 percent relative to exhaustive search at the same reduced representation, and every instance in those cells is faster. At width 32 and a 33-point lattice, the median saving is instead approximately minus 18 to minus 19 percent. The paper reports this crossover rather than claiming uniform dominance.

### 2.4 The stress catalogue is materially harder

The retained regimes include activation crossing, large signed cancellation, adjacent exact minimizers, and a completely flat objective. Coarser outward bounds, larger lattices, fallbacks, operand diagnostics, array sizes, and repeated shuffled order are preserved. The result is no longer supported only by a one-survivor production catalogue.

### 2.5 A non-scalar exact witness extension is supplied honestly

The uniform-box expectation formula is exact and includes signed output weights. The constrained subdivision theorem has a correct finite fallback and retains polytope feasibility and lexicographic ties. The paper explicitly records the exponential shock-integration term count and worst-case product action-lattice size.

It does not mislabel this query experiment as a full multi-action economic service.

### 2.6 The Bellman consistency argument now states the needed stability premise

The fixed-cover endpoint maps used by the executable computation are proved monotone and discount-nonexpansive. Numerical outward error is separately budgeted rather than assumed stable merely because intervals contain the truth. This is an important mathematical correction.

### 2.7 The original optimum and the returned policy are no longer conflated

The centered construction produces one policy and a narrow original-optimum bracket. R61 separately revalidates the actual returned prospective actors on a fixed grid, includes every actor identity irrespective of generator or reported policy cost, and retains both clipped and unclipped upper recursions. The verification creates no new policy or cost sample and has its own work account.

### 2.8 Strong conventional controls and unsuccessful targets remain visible

Common-only, quadratic-native, screened ReLU, and native ReLU all face the same prospective targets and verifier. Common-only is not discarded merely because it has no fitted continuation. The strict high-dimensional target remains budget exhausted under all methods. Conventional policy identities and unresolved intervals are reported without being converted into a neural victory.

This is exemplary disclosure.

## 3. Blocking concerns

### B1. The exact-search contribution remains highly specialized

The root-free theorem is tied to a scalar nonnegative action lattice and an integrated piecewise quartic with nonnegative fourth-order coefficient. The trained continuation is a one-hidden-layer affine–ReLU network, and the exact integration uses scalar uniform or finite mixtures of box-uniform shocks with rational stored inputs.

These assumptions are not merely implementation details. They create the discrete curvature and exact rational structure. The result does not cover deeper networks, smooth activations, general innovation laws, continuous-action optimization without a fixed lattice, or coupled multivariate objectives with an analogous curvature structure.

The paper should present the theorem as a strong special-purpose exact solver, not as general validation of Neural Bellman Operators.

### B2. The best conventional complete service remains uniformly cheaper

Common-only is the fastest complete warm service in every one of the 24 matched task–target–seed–worker groups. Its mean complete-return time is approximately 15.75 seconds, compared with 17.11 for native quadratic, 18.75 for native ReLU, and 18.98 for screened ReLU. It achieves the same 20/24 attainment count as every fitted method.

For cold single use, native compilation widens the disadvantage further. The revision correctly reports compilation separately, but the economic decision maker still has no reason in the executed catalogue to pay for the fitted ReLU continuation when the common verified action family returns the same attained-status pattern at lower work.

A numerical-method contribution cannot be established solely by making the most expensive neural branch modestly less expensive than its previous implementation.

### B3. No direct economic comparison identifies a lower neural policy cost

For native ReLU versus common-only, seven of twelve mathematical designs are exact policy identities and five cost intervals contain zero. The same pattern holds against native quadratic. Native ReLU and screened ReLU are identical by construction. No interval establishes a lower native-ReLU expected cost, and no interval establishes a higher one either.

This evidence is scientifically useful, but its implication is nonranking—not neural superiority. The manuscript’s economic contribution therefore rests on general certification logic and normalized examples, not on an economic outcome uniquely delivered by the learned continuation.

### B4. Large query-level gains collapse to a small complete-service effect

The matched native factorial shows convincing large-lattice query savings. Yet replacing screened with native ReLU search changes complete warm return time by a median of only about 1.36 percent across the 24 paired services. Native is faster in 22 pairs and slower in two; the range is approximately minus 3.01 to plus 3.30 percent.

This compression is economically important. Fitting, whole-cell verification, inference, serialization, and process overhead dominate enough of the service that a 60–73 percent action-search microbenchmark gain at the largest lattice does not materially reorder methods.

The paper should not let the microbenchmark become the headline when the complete-service frontier remains conventional-method dominated.

### B5. The exact witness has limited demonstrated policy leverage

The complete reconstruction records twelve additional-witness cell changes, but direct final-policy comparisons still produce only identities or unresolved intervals relative to the conventional policies. A local action change or a narrower upper endpoint is not itself an identified policy-cost gain.

The paper needs an application in which exact fitted action recovery materially changes a complete policy and yields a direct economic or certification benefit that survives comparison with the strongest conventional service.

### B6. Original-optimum accuracy is established only in the smallest executed economy

The centered Bellman ladder reaches a 0.03979 all-state gap only in the two-state, two-date model. It requires approximately 289.74 seconds of cumulative centered work at the final rung. The strictest declared tolerance one-thirty-second is not attained.

For actual returned actors, three of five distinct policies attain one-eighth but none attains one-sixteenth; two retain bounds near 0.30330. The dimensions four and eight prospective services do not receive an analogous original-optimum revalidation. Their stopping targets remain initial-law cost reductions relative to zero investment.

Consequently, R61 does not yet show that NBO provides high-accuracy Bellman solutions in the dimensions emphasized by the service experiment.

### B7. The centered accuracy result is a disclosed follow-up, not the primary prospective design

The uncentered experiment was observed first and failed the tighter targets. The common-reference extension was then designed and separately frozen. This is acceptable scientific practice because the chronology is explicit and all earlier failures are retained. It nevertheless means the narrow 0.03979 result is a second-stage methodological intervention motivated by the first-stage failure.

A decisive paper should prospectively test the centered construction, including fixed-policy revalidation, over multiple dimensions and economic cells rather than relying on one post-failure design in the easiest case.

### B8. The multi-action extension is exact but computationally adverse

The two-control query experiment validates exact constrained recovery, but adaptive subdivision is slower than exhaustive enumeration despite using fewer exact point evaluations. The table reports median adaptive/exhaustive time ratios around 2.68–3.24, and the larger cases invoke fallbacks. Across the underlying records, the ratio remains above one in every case.

The extension also has no complete policy, Bellman-optimality, or welfare comparison. It therefore establishes correctness of a more general witness calculation but no numerical advantage in the additional action dimension.

### B9. Scaling and reliability evidence remain limited

The service catalogue uses two fixed training seeds and two worker repetitions of identical mathematical objects and path streams. These repetitions describe implementation robustness; they do not estimate optimizer reliability, task-population performance, or independent policy-cost uncertainty. Processor frequency is uncontrolled and hardware counters are unavailable.

The exact complexity accounts are welcome, but they retain rational bit-length dependence, product action-lattice size, exponential box-shock terms, and state-cover growth. No experiment demonstrates favorable scaling against sparse-grid, adaptive dynamic programming, modern mixed-integer/interval optimization, or other strong conventional solvers in a genuinely difficult action dimension.

### B10. The publication scope remains disproportionate to the completed contribution

The active article and supplement contain 149 pages. The complete article and proof companion contain another 365 pages, in addition to retained development documents. The broad research program includes diffusions, recursive preferences, endogenous preferences, temporal selves, games, acquisition, safe improvement, and many historical experiments.

The R61 advance is narrower: exact action search for a special integrated ReLU objective, one two-control query extension, one low-dimensional Bellman frontier, and deterministic revalidation of five actors. The broader applications do not receive this exact solver or matched original-optimum execution.

For Econometrica, either the paper must demonstrate a broadly consequential numerical method and economic result, or the publication must be focused around the contribution actually established. R61 does neither sufficiently.

## 4. Major comments and required changes

### M1. Reorganize around one numerical contribution

A focused article should center on the root-free exact witness, the transfer to a returned policy, and stable Bellman certification. The broader NBO development can remain as archived companion material rather than carrying the active contribution claim.

### M2. Compare best neural and conventional services at matched original-optimum accuracy

The current complete services share an initial-law target, whereas original-optimum accuracy is evaluated only later and only for the smallest case. A decisive comparison should charge every method from primitives through a common all-state Bellman tolerance, including any post-selection fixed-policy verification.

### M3. Execute the centered Bellman program prospectively beyond two states and two dates

Predeclare dimensions, horizons, tolerances, refinement ladders, and complete cost boundaries before seeing results. Include the actual returned actors of all generators, not only a separate constructed policy.

### M4. Turn the multi-action extension into a complete economic experiment

Construct and certify full two-control policies, compare them directly with optimized conventional methods, and report actual expected policy-cost differences. Query-level exactness is insufficient.

### M5. Include optimized conventional action solvers

The correct comparison set includes native exhaustive evaluation, specialized quartic/discrete-convex solvers, adaptive interval branch and bound, and an optimized constrained-lattice method. For larger action dimensions, include mature conventional optimization routines with verified postchecks rather than only the paper’s own fallback.

### M6. Identify an economically active exact witness

Select the economic design prospectively, not by choosing favorable realized cells, but ensure that the scientific question makes exact fitted action recovery consequential. Report how often the witness changes the final policy, how much the all-state certificate changes, and whether direct policy cost changes.

### M7. Strengthen timing and resource inference

Use controlled processor frequency where feasible, several physical architectures, randomized paired orders, adequate repetitions, and kernel-level counters. Report total bytes moved, peak memory by method, rational operand distributions, compilation amortization, and batch effects under the complete-service boundary.

### M8. Make the bit-complexity result operational

Connect the conservative operand-length theorem to observed temporary sizes in the actual rational engine, including numerator/denominator growth and normalization. State a complete complexity bound in width, lattice size, action dimension, shock dimension, target accuracy, and coefficient bit length.

### M9. Separate deterministic correctness from optimizer reliability

The exact witness theorem is deterministic conditional on a fitted continuation. Training reliability is a different estimand. Prespecify a distribution or finite catalogue of training initializations and economic tasks, retain all failures, and report the probability or fraction of producing a continuation that reaches the same original-optimum target.

### M10. Supply a calibrated or substantively consequential economic use case

The current formulas for computation price, installation charge, and use count are correct accounting identities but contain no empirically or institutionally grounded inputs. Demonstrate a decision whose recommendation changes because of the verified numerical improvement, or state explicitly that the paper is a numerical-analysis contribution rather than an Econometrica-scale economic application.

## 5. A focused publishable route

The strongest standalone object in R61 is:

> **Exact Root-Free Action Recovery and Stable Bellman Certification for Integrated ReLU Continuations**

A credible new submission on this topic would contain:

1. the discrete-curvature theorem and exact tie-preserving solver;
2. a concise transcript or policy-transfer theorem;
3. fixed-cover stability and a whole-domain Bellman certificate;
4. a language- and representation-matched factorial with optimized baselines;
5. a complete multi-action economic service rather than a query test;
6. prospective work-to-original-optimum frontiers in several dimensions;
7. direct expected policy-cost comparisons; and
8. a compact economic application in which exact recovery changes the implemented decision.

Such a paper could make a valuable contribution even if conventional methods win some cells. The present cumulative manuscript makes it difficult to identify and assess that contribution cleanly.

## 6. Independent verification performed for this report

I audited the canonical R61 branch and the deposited publication-audit artifact without retraining, resimulating, rebuilding LaTeX, or retiming services.

The artifact audited is:

- artifact ID `11626669714`;
- name `nbo-r61-paper-and-publication-audit`;
- SHA-256 `144cc465cb625473d23d14547accd839a517e851ea1a01af1c8b3f64383c672b`.

The deterministic audit confirms:

- 96 complete services, of which 80 attain and 16 exhaust the budget;
- 5,600 protected predecessor files and 2,141 scientific input files checked;
- 2,408 scalar solver records;
- 24,576 cell-date decisions;
- 1,128 confidence-interval records;
- 1,896,448 reconstructed original-law path rows;
- 3,160 exact native-factorial answers checked;
- five distinct fixed-policy actors revalidated;
- zero new training services and zero new independent policy-cost observations in the publication audit.

Recomputing the complete-service comparison gives:

- common-only fastest in all 24 matched groups;
- each mode attains 20 of 24 services and exhausts four;
- native ReLU faster than screened ReLU in 22 of 24 matched complete services;
- median native-versus-screened saving approximately 1.364 percent;
- saving range approximately minus 3.011 to plus 3.299 percent.

Recomputing direct policy-cost classifications across the two worker replicas gives, for both common-only and quadratic-native:

- 14 exact policy identities;
- 10 unresolved intervals containing zero;
- zero intervals identifying lower native-ReLU cost;
- zero intervals identifying higher native-ReLU cost.

These are replicas of twelve mathematical designs, not twenty-four independent economic comparisons.

The original-optimum audit confirms the centered final gap `0.03978614928330127`, cumulative recorded centered work of approximately `289.742` seconds, and fixed-policy bounds of approximately `0.06778`, `0.07175`, and `0.30330`. Three of five distinct actors attain one-eighth; none attains one-sixteenth.

The multi-action audit confirms 32 query records, eight fallback records, and adaptive/exhaustive time ratios above one throughout the underlying records. The median ratio is approximately `3.237`.

Finally, I independently exercised the discrete quartic candidate rule on 50,000 exact rational test sequences with nonnegative fourth-order coefficients. Exhaustive smallest-minimizer search and the concave-prefix/convex-tail candidate rule agreed in every case. This is a spot check of the central lemma, not an independent proof of every result in the cumulative manuscript.

The review directory contains the standard-library verification script and its machine-readable output.

## 7. Recommendation

R61 is mathematically and computationally serious. It closes the publication chain, corrects the stability argument, removes the favorable-separation assumption from exact scalar action recovery, isolates the main implementation confound, extends exact integration and search to constrained multiple controls, and supplies valid original-optimum certificates for the constructed policy and actual returned actors. The provenance and adverse-evidence disclosure are exemplary.

The remaining issue is not correctness of the narrow result. It is contribution and fit. The exact solver is specialized; the complete-service savings are small; common-only is faster everywhere; direct policy-cost comparisons identify no neural advantage; high-dimensional services are not certified against the original optimum; the multi-action method is slower than exhaustive search; and the broad economic platform remains unsupported by matching execution.

I therefore recommend **rejection in the present form and no further ordinary revision of the cumulative manuscript**. I would take seriously a new, focused submission built around exact root-free action recovery and stable Bellman certification, provided it supplies matched original-optimum frontiers, a complete multi-action experiment, strong conventional baselines, and an economically consequential use case.
