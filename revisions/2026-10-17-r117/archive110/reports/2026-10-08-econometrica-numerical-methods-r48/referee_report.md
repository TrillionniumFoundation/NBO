# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r48-review-ready-2026-10-08`  
**Pinned revision commit:** `2650fd92f24be0f4807ec8ee0eac1d075a8d63e3`  
**Pinned revision tree:** `20ca4fb03bf1a725190f3a43a456b4ad14411d0d`  
**Pinned main manuscript:** `revisions/2026-10-08-r48/ECTA.tex`, Git blob `13225001aef5007e496f362e820fa7aa4f333400`  
**Pinned technical supplement:** `revisions/2026-10-08-r48/supp.tex`, Git blob `b942469e2db568767d7015bcfb411996104d1155`  
**Pinned response:** `revisions/2026-10-08-r48/response.md`, Git blob `7436820f89f06e4919d1c37dd8e7601060ebd9ed`  
**Report date:** 8 October 2026  
**Recommendation:** **Reject in the present form and do not invite another ordinary revision of the cumulative manuscript. A new, substantially focused paper on witness-preserving compilation and acquisition-aware certification for constrained Lipschitz dynamic programs could merit evaluation, but R48 does not establish an Econometrica-level method-specific contribution for the broad Neural Bellman Operators program.**

> This is a repository-owner-commissioned, AI-assisted advisory report. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R48 is the first revision in this sequence that simultaneously clears the publication threshold and closes most of the operational objections raised in the preceding reports. The branch is canonical, immutable, self-contained, and rebuildable without a live workflow artifact. It contains ordinary sources, a 67-page article, a 61-page supplement, a 13-page response, frozen scientific records, generated tables, release and preservation audits, and a successful offline clean rebuild. I independently verified the final branch identity, the study and publication artifact digests, the frozen source hashes, all 44 service records, all 204 rung checkpoints, all 48 direct policy-cost records, and the publication file manifest.

The principal new mathematical result is real. A literal minimum-of-cones continuation scans all state labels whenever a future value is queried. R48 uses the classical separable distance transform to preprocess nodal envelope values and their original owners, then proves an off-grid cell-corner identity preserving the original feasible action witness and lexicographic tie rule. In fixed dimension this removes a redundant state-cover scan while leaving the mathematical continuation and policy unchanged. I independently spot-checked the exact identity on 160 random rational examples in dimensions one through four, including nonuniform grids, inconsistent labels, zero slopes, ties, and off-grid queries; every full enumeration agreed exactly with the compiled owner rule.

R48 also improves the economic implementation. It supplies a priced finite-bit observation technology, robust capacity repair over the entire acquisition cell, action quantization, and an exact neighboring-bit rule for minimizing a certified resource account. It directly compares actual expected costs of frozen constrained policies rather than subtracting regret upper bounds. It charges failed resolutions, compilation, adaptive pilots, policy construction, certification, acquired-state checks, serialization, and durable output.

The difficulty is no longer formal incompleteness. It is contribution and identification.

The compiler is not a neural-specific numerical method. The paper proves that the native min-plus envelope and its affine–ReLU realization return the same continuation, owner, repaired action, certificate, and policy cost. The distance-transform compiler is available equally to the native implementation. The completed contribution is therefore a useful compilation and certification theorem for a classical Lipschitz-envelope dynamic program. Neural encoding is one exact representation of that algorithm, not the source of the computational saving.

The complete-work evidence is mixed and predominantly unfavorable relative to uniform tensor FVI. At common successful prospective targets, compiled witness is faster in only 3 of 30 matched comparisons and slower in 27. Against the error-driven FVI comparator it is faster in 15 and slower in 15, but the supposedly adaptive method returns uniform grids in all 210 date models, so those rows measure pilot and allocation overhead rather than an effective nonuniform method. At the final common resolution in the four two-state cells, compiled witness has a 15.8–19.5 percent tighter all-state bound but takes about 31.6–32.9 percent more median complete-prefix time than tensor FVI.

The headline target-one attainment advantage is cap- and threshold-sensitive. Compiled witness attains target one in 12 of 12 main services, while each FVI comparator attains it in 6 of 12. But the FVI failures finish at approximately 1.0028 and 1.0131. They miss the normalized threshold by about 0.28 and 1.31 percent. The experiment stops at N=64. This is legitimate prospective evidence, but it is too fragile to carry a broad method claim without a denser accuracy frontier or a further common-resolution rung.

The direct economic evidence does not favor witness. Across 48 simultaneous constrained-policy comparisons, six intervals place witness cost strictly above FVI cost, none place it below, and 42 contain zero. All 48 intervals lie inside the predeclared controller-replacement fee band, so the paper validly concludes that neither switch recoups that particular fee. However, the fee is 5.75 times the largest absolute confidence endpoint and is a theoretical primitive rather than a calibrated transaction cost. Moreover, the direct comparison freezes the old R47 N=16 policies. It does not compare the new R48 policies behind the headline work-to-target result, including the T=3, p=4 case in which compiled witness crosses at N=32 and tensor FVI at N=64.

The strongest publishable object is thus narrower than the current platform article: a witness-preserving compiler and acquisition-aware certification account for constrained Lipschitz dynamic programs, together with honest evidence that sharper certificates need not imply lower policy cost or lower complete work. This is potentially valuable, but it is not yet an Econometrica-level demonstration of a distinctive neural method or a substantive economic result enabled by NBO.

## 2. Substantial improvements

### 2.1 Canonical and reproducible submission

R48 fixes the threshold defect of R47. The final branch contains the assembled article, supplement, response, code, frozen evidence, build products, preservation map, release audit, and final-delivery ledger. The clean Git-archive rebuild needs neither network access nor an expiring artifact. The active documents have no undefined references, duplicate labels, missing characters, or overfull boxes. The clean rebuild executes 96 regressions and the final delivery verifies 1,430 files while preserving historical paths.

### 2.2 Policy-preserving compiler

The theorem keeps original label ownership through coordinatewise relaxations and proves an off-grid identity for the lexicographically selected original owner. This matters because a transformed grid node may store a value inherited from a distant site; attaching the grid node’s action would change the policy. R48 correctly carries the original witness and handles arbitrary inexact labels and ties.

### 2.3 Separation of numerical objects

The paper now distinguishes compiling a fixed policy, constructing a fresh own-future policy, certifying it relative to the optimum, and directly comparing actual policy costs. The frozen-object compiler benchmark is not added to construction clocks, and a smaller regret certificate is not represented as an observed policy-cost reduction.

### 2.4 Fairer conventional comparison

Uniform tensor FVI and error-driven coordinate FVI use their own fitted futures, the same continuous innovation law, the same feasible action fractions, and the same one-sided all-state criterion. Failed rungs remain in complete prefixes. The paper does not compare a sharpened witness certificate with an intentionally weak conventional residual account.

### 2.5 Acquisition and feasibility contract

The finite-bit sensor reports a state cell, not a fictitiously exact state. Capacity repair is valid over the whole cell and downward action quantization preserves feasibility. Selector arithmetic, acquisition radius, repair displacement, and action spacing enter the policy account. This is a meaningful implementation contribution for discontinuous witness selectors.

### 2.6 Direct expected-cost comparison

The constrained-policy study uses raw discounted path-cost differences under common innovations. It encloses every initial and innovation bin, unresolved actor, sensor cell, and repair branch. Containing zero is not called equality, and lying within a fee band is correctly interpreted as a replacement decision rather than signed superiority.

### 2.7 Preservation of adverse evidence

R48 reports that compiled witness is slower than tensor FVI in 27 of 30 common successful comparisons, the adaptive rule never realizes a nonuniform grid, all methods miss targets one half and one quarter, six direct intervals favor FVI and none favor witness, and higher-dimensional runs are stress tests rather than scaling laws. This disclosure is exemplary.

## 3. Blocking concerns

### B1. The identified computational advance is not neural-specific

The compiler operates on a minimum of Lipschitz cones and propagates original owner indices. Its nodal engine is the classical separable distance transform. The exact ReLU realization and native min-plus implementation are mathematically identical when they share labels, witnesses, and tie rules. The computational saving belongs to the envelope algorithm, not neural encoding.

The correct comparison is compiled witness-envelope dynamic programming versus strong conventional dynamic-programming alternatives. On that comparison the evidence is mixed and often unfavorable. The title may describe a broader research program, but R48 does not identify a computational or economic capability attributable specifically to the neural representation.

### B2. Uniform tensor FVI wins most common-target timing comparisons

Compiled witness is faster than tensor FVI in 3 of 30 common successful target-by-repetition comparisons and slower in 27. At N=64 it is about 1.32 times as slow in each two-state cell while earning a 15.8–19.5 percent tighter certificate.

One cell is strongly favorable: at T=3, p=4 and target two, witness crosses at N=32 in about 5.50 median prefix seconds, while tensor FVI crosses at N=64 in about 54.15 seconds. This is a valid local result, but one threshold cell does not establish a stable method frontier. The paper needs a principled characterization of when certificate sharpness offsets higher same-resolution work.

### B3. Target-one attainment is threshold-sensitive

The six FVI failures at target one finish at about 1.0028 or 1.0131. A 1.4 percent relaxation makes both FVI methods pass every main service; a slightly tighter target may remove witness passes. Because the ladder stops at N=64, the 12/12 versus 6/12 headline depends materially on one normalized threshold and the cap.

The complete positive-tolerance frontier should be primary. At minimum, the paper needs sensitivity around every declared target and either a common N=128 rung in the near-miss cells or a resource-based explanation for excluding it.

### B4. Direct policy costs never favor witness

Among 48 constrained-policy comparisons, witness has strictly higher expected cost in six, strictly lower cost in zero, and 42 remain unresolved. The adverse intervals occur at initial state `(7/8,7/8)`, price one, under both horizons and every observation contract. This pattern deserves economic interpretation.

The direct evidence does not show that the tighter witness certificate translates into a better policy. At best it shows that the old installed policies are close relative to a separately specified fee.

### B5. The direct comparison is disconnected from the new work frontier

R48 freezes the R47 N=16 witness and bilinear-FVI policies for the direct study. This protects the comparison from post-selection, but it does not evaluate the policies returned by R48’s first crossings. The favorable T=3, p=4 target-two pair—witness at N=32 and FVI at N=64—is never directly compared by actual expected cost.

A prospective direct comparison of the policies returned at each declared first crossing is needed to connect work-to-certificate evidence to economic performance.

### B6. The no-replacement conclusion relies on a generous, uncalibrated fee

All intervals lie inside `[-1/64,1/64]`. The fee is 0.015625, while the largest absolute endpoint is about 0.002717. The conclusion is robust for that theoretical primitive, but the fee is neither estimated nor calibrated and is 5.75 times the largest endpoint.

The informative object is a break-even fee frontier by task. The paper should report the smallest fee for which neither switch is certified to pay, and explain the economic relevance of the chosen fee across prices, horizons, sensors, and initial laws.

### B7. The adaptive baseline does not adapt

The error-driven FVI rule returns uniform grids in all 210 date models. All 60 adaptive checkpoints have the same continuations and actors as uniform FVI. The extra cost is pilot and allocation overhead. This is useful negative evidence about one heuristic, not a meaningful comparison against adaptive cells, sparse grids, hierarchical refinement, or other strong nonuniform methods.

### B8. Higher-dimensional runs are not matched-accuracy scaling evidence

Dimensions three and four use different maximum resolutions, one execution per cell, and no common certified target across dimensions. At the final rungs, witness certificates are 12.5–17.2 percent tighter while times are about 1.05–1.42 times larger than tensor FVI. These are finite stress observations, not scaling estimates. The tensor state cover, action grid, innovation factor, and `2^d` corner term remain visible.

R48 removes a redundant scan but does not solve the high-dimensional problem normally motivating neural dynamic programming.

### B9. The priced sensor theorem minimizes a conservative bound, not actual net cost

The rule minimizes `G + KΔ + A 2^{-b} + Cb`. This is a valid deterministic account, but it need not minimize actual expected policy cost plus information cost. The selected bits are 12–16, whereas the direct policy-cost experiment evaluates exact, six-bit, and ten-bit implementations. The empirical study therefore does not evaluate the precision choices selected by the theorem.

A stronger result would compare actual net policy cost across the same bit-price grid and report whether the certified minimizer is economically close to the simulated optimum under the declared model.

### B10. The cumulative scope remains disproportionate

The active article is 67 pages, the supplement 61 pages, and the response 13 pages. The manuscript retains controlled diffusions, recursive utility, endogenous preferences, temporal selves, games, nonconvex training, factor constructions, mixed precision, witness envelopes, sensor design, and direct sampling.

The new evidence directly supports a narrower claim: a policy-preserving compiler and acquisition-aware certificate for low-dimensional constrained Lipschitz dynamic programs, with mixed comparative performance. The cumulative form obscures one theorem-evidence chain capable of meeting Econometrica’s standards for novelty, generality, computational importance, and economic consequence.

## 4. Required changes for a new submission

1. **Reframe the contribution around the underlying min-plus/Lipschitz dynamic-programming algorithm.** Treat native and ReLU encodings as one method.
2. **Make the complete tolerance frontier primary.** Report target sensitivity around the near-miss threshold and, where feasible, add a common further rung.
3. **Directly compare the actual first-crossing policies.** Include the favorable T=3, p=4 target-two pair.
4. **Report break-even replacement-fee curves.** Retain the predeclared 1/64 decision but expose its sensitivity.
5. **Use a genuinely adaptive conventional baseline.** The completed error-driven rule never adapts.
6. **Execute a common-accuracy dimension study.** Match targets and caps across dimensions and repeat cells.
7. **Connect sensor choice to actual net cost.** Compare certified and simulated precision decisions on the same grid.
8. **Separate deterministic compiler reliability from neural optimizer reliability.** Exact timing repetitions say nothing about nonconvex training populations.
9. **Sharpen the novelty comparison to certified dynamic programming, min-plus methods, distance transforms, and verified control.**
10. **Produce a focused new paper rather than another cumulative revision.**

## 5. Potentially publishable focused route

A credible new submission could be titled:

> **Witness-Preserving Compilation and Acquisition-Aware Certification for Constrained Dynamic Programs**

Its mathematical core would be the continuous off-grid owner identity, policy-preserving distance-transform compilation, one-sided certification with acquisition and repair, explicit accuracy/work allocation, and direct cost inference for the policies returned by the work frontier.

Its numerical core would compare compiled witness dynamic programming with uniform and genuinely adaptive conventional methods on common-accuracy frontiers, including higher-dimensional cases where the computational mechanism matters. Native and ReLU implementations should be treated as one algorithm with two encodings.

Its economic core should make one resource decision—information acquisition, controller replacement, or another implementation choice—whose conclusion is not predetermined by a large arbitrary charge and whose sensitivity is fully reported.

## 6. Independent verification

I downloaded and audited:

- study artifact `11523019602`, SHA-256 `9ac1f57b4e4b899594029e775c1f1c9e921ad943490e85481badedcd5d722bbc`;
- publication artifact `11524319892`, SHA-256 `b82272add8e7ea630ef1ab45455b079514fd848311e2d23db84d2b11ab9cd5df`.

The deposited standard-library audit:

1. verifies all eight frozen scientific source hashes;
2. verifies all 44 service records and 204 checkpoint hashes;
3. reconstructs target attainment and common-target timing comparisons;
4. recomputes final bound/time ratios in dimensions two through four;
5. verifies all 48 direct cost records, sign counts, fee decisions, endpoint extrema, path counts, and joint comparison time;
6. recomputes sensor-bit choice frequencies;
7. recomputes all 36 dense/compiled representation timing ratios including setup;
8. runs 160 exact rational compiler spot checks in dimensions one through four; and
9. verifies the 1,430-file publication manifest, the 96-test clean rebuild, active-source hashes, and historical-path preservation.

The independently reconstructed headline findings are:

- 44 services and 204 rungs;
- compiled-witness attainment `12/12, 12/12, 12/12, 0/12, 0/12` at targets `4, 2, 1, 1/2, 1/4`;
- each FVI method attainment `12/12, 12/12, 6/12, 0/12, 0/12`;
- compiled witness faster than tensor FVI in 3/30 common successful comparisons and slower in 27/30;
- compiled witness faster than adaptive FVI in 15/30 and slower in 15/30;
- direct signs: six witness-higher, zero witness-lower, 42 unresolved;
- all 48 tasks exclude recouping the declared 1/64 fee in either direction;
- dense/compiled frozen-object time ratio including setup: range 1.873–4.523, median 2.916;
- clean rebuild: 96 tests, 67-page article, 61-page supplement, 13-page response.

I did not rerun training, scientific simulation, LaTeX, or timing services. A new run would create new scientific and performance observations rather than verify the frozen ones.

## 7. Recommendation

R48 is technically serious and unusually auditable. It repairs the R47 publication failure, proves a useful policy-preserving compiler, integrates acquisition and feasibility into the policy contract, executes a complete prospective catalogue, and directly compares actual policy costs. The author also retains unfavorable findings.

The evidence nevertheless does not establish the contribution claimed by the cumulative paper. The saving is available to the identical native min-plus construction; tensor FVI is faster in most common-target comparisons; the target-one advantage is threshold-sensitive; direct policy costs never favor witness and sometimes favor FVI; the adoption conclusion depends on a large theoretical fee; the adaptive baseline does not adapt; and higher-dimensional runs are not a common-accuracy scaling result. The broad NBO platform remains much larger than the completed theorem-evidence chain.

I therefore recommend **rejection in the present form and no further ordinary revision of the cumulative manuscript**. I would take seriously a new, sharply focused submission on witness-preserving compilation and acquisition-aware certified dynamic programming, provided it isolates the non-neural algorithmic contribution, compares the policies returned by the work frontier, uses stronger conventional baselines, and develops one economically meaningful resource decision.
