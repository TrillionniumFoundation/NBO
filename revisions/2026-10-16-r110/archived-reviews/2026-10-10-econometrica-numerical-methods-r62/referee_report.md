# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r62-review-ready-2026-10-10`  
**Pinned revision commit:** `cfecc5ffcdeb836b1c70e9b98d1dc87f6f8cd097`  
**Pinned revision tree:** `8e7d70f846f0744edb35ee0de35d85cb210d64be`  
**Pinned main manuscript:** `revisions/2026-10-10-r62/ECTA.tex`, Git blob `85cce114c7e1682e2a9af14d0fceab6e3bb61ac3`  
**Pinned technical supplement:** `revisions/2026-10-10-r62/supp.tex`, Git blob `6e8203aef5002c29058e39cea30229e2fc597e2b`  
**Pinned response:** `revisions/2026-10-10-r62/response.md`, Git blob `66747b3d259f25ec36750f04a69982a10a8c9891`  
**Completed science commit:** `d868cb5bc113e521be134cb9f50f04b5c68b3493`  
**Science workflow / artifact:** `38016958569` / `11656912797`, SHA-256 `33416454ea1418303e132c4fd00cba1f47c7c48ee3564acf2b808833e105c9fb`  
**Publication workflow / artifact:** `38020293255` / `11658151910`, SHA-256 `25b15a12a5ad2ed15af1291f7a5ca2789bbe9ac2abfd9f7550ece872b45e3963`  
**Report date:** 10 October 2026  
**Recommendation:** **Reject in the present form and do not continue the cumulative manuscript through another ordinary revision round. A new, sharply focused paper on whole-domain certification of implemented policies in convex capacity-constrained dynamic programs could merit evaluation, but R62 does not establish a method-specific Econometrica-level contribution for Neural Bellman Operators.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R62 is a substantial and technically serious response to the R61 report. It resolves two of the previous review’s most important formal objections. First, the paper now derives primitive convexity, Lipschitz, semiconcavity, interpolation, quadrature, and action-cover bounds for the original investment model rather than relying on a reduced or surrogate target. Second, it certifies the actual implemented policy against the original continuous-action optimum. The policy is constructed by barycentrically interpolating stored nodal actions and then accounting separately for state acquisition, action rounding, floating arithmetic, and the loss incurred by the policy’s own future behavior.

The new prospective study is also materially stronger than the preceding evidence. It fixes five cells before execution: state dimensions two, four, and eight; horizons two and three; scalar and two-control policies; and five common accuracy targets. It preserves pure fitted policies and common-augmented fitted policies as different economic objects. Direct policy-cost comparisons use fresh common paths, and the release contains a clean-archive rebuild, source bindings, complete interval records, and an unusually detailed work ledger.

I spot-checked the central analytical chain. In particular, the stated state-curvature margin
\[
 4/d-\beta(27/d)/8=107/(128d)
\]
is arithmetically consistent; the midpoint quadrature allowance follows from semiconcavity and conditional variances; and the barycentric actual-policy argument is the appropriate way to avoid assuming continuity of the fitted actor. I found no immediate algebraic contradiction in these central R62 statements under their declared hypotheses. The result is a genuine whole-domain verification theorem for this convex dynamic program.

The decisive difficulty is no longer formal correctness. It is contribution identification.

The prospective evidence is unfavorable to the specifically neural method claim. The pure ReLU policy has strictly higher expected cost than the common Bellman policy in all twenty task--seed comparisons. Its common-augmented counterpart has twenty intervals containing zero against the common policy. The pure quadratic policy is also strictly worse in sixteen of twenty comparisons and unresolved in four. The augmented policies recover the common policy’s certificate almost exactly—the largest final-bound difference is below `2.7e-12`—because the common candidate remains available at every node. The fitted proposal is selected on only about 5.2 percent of ReLU node--date opportunities and 6.4 percent of quadratic opportunities at the finest declared rungs.

The work frontier points in the same direction. Across the twenty task--tolerance cells attained by at least one declared policy, the common Bellman method has the smallest recorded complete release work in all twenty. Adding a fitted proposal increases recorded work by roughly 2--11 percent, depending on the cell, without a certified cost improvement. At the highest declared dimension, the common reference already uses 390,625 states and 7,031,250 point--action queries, yet certifies only the coarse target `1/2`; all four tighter targets are exhausted. The tensor construction therefore remains exponential and the eight-dimensional experiment is a coarse feasibility point, not a high-dimensional accuracy result.

R62 consequently establishes a valuable but method-neutral object: a second-order, whole-domain certificate for implemented policies in a specified convex investment model. It does not show that a Neural Bellman Operator produces a better policy, a cheaper certified service, a sharper certificate than the common reference, or an economic conclusion unavailable to the conventional construction. Indeed, the new evidence directly documents the opposite for the pure ReLU policies.

The publication remains far broader than this successful contribution. The active article is 106 pages and the active supplement 69 pages; complete preserved companions are 216 and 175 pages. The retained program spans controlled diffusions, recursive utility, endogenous preferences, temporal selves, games, finite precision, reuse, and multiple historical experiments. R62’s new theorem and evidence do not close those distinct numerical obligations.

I therefore recommend rejection in the present form. I would take seriously a new paper centered on whole-domain original-optimum certification for implemented policies in convex, capacity-constrained dynamic programs, provided the contribution is separated from the candidate generator, the numerical comparison is redesigned around strong adaptive conventional baselines, and the paper is reduced to one coherent theorem--algorithm--evidence chain.

## 2. What R62 successfully repairs

### 2.1 The comparison target is now the original optimum

The new theorem compares the stored and implemented policy with the original continuous-action Bellman optimum. It no longer stops at a fitted continuation target, a finite action menu, a one-step improvement opportunity, or a reduced baseline. State interpolation, continuous-shock integration, continuous-action coverage, numerical Bellman enclosures, and implementation error are all visible in the same account.

This is the most important positive advance in R62.

### 2.2 The actual returned policy is certified

The certificate is not assigned to an ideal nodal actor while another policy is deployed. At each off-grid state, the returned action is the barycentric combination of the vertex actions. Joint convexity of the exact state--action objective yields an off-grid one-step bound, and backward propagation accounts for the returned policy’s own future. Downward state acquisition and action rounding receive explicit allowances.

This closes the gap between a verifier’s internal object and the implementable economic policy.

### 2.3 The primitive regularity chain is explicit

For the declared model, the revision supplies:

- convexity of the Bellman value;
- interior differentiability;
- a uniform Lipschitz envelope;
- semiconcavity and coordinate second-difference bounds;
- nonnegative multilinear interpolation error;
- second-order interpolation and midpoint-quadrature errors; and
- a second-order action-cover allowance.

The constants are propagated from economic primitives instead of inferred from successful numerical output.

### 2.4 Pure and augmented policies are correctly separated

R62 preserves two different policy objects:

1. a pure fitted ReLU or quadratic proposal; and
2. a common-augmented proposal that may select the fitted action only when its verified upper endpoint improves the common candidate.

This prevents a successful fallback service from being reported as evidence that the pure fitted policy succeeded.

### 2.5 The two-control experiment is a full dynamic policy

The two-control cell no longer reports only a single query or a one-step action. Both action coordinates are propagated at every date, feasibility is checked under their shared capacity, and the full policy receives the same whole-domain comparison to the original optimum.

### 2.6 Direct policy costs are reported

The new common-path comparison evaluates the actual frozen policies. The paper does not infer a policy-cost ranking by subtracting two regret bounds. The result that all twenty pure ReLU policies have higher expected cost than the common policy is retained rather than hidden.

### 2.7 Publication and provenance are strong

The canonical branch is source-bound and clean-rebuildable. The final audit records 295 interval objects, 18,806,777 nodal action records, 40 fitted services, 327,680 prospective path rows, and 8,855 release files. The article, supplement, response, and preserved companions compile without undefined references, duplicate labels, missing characters, or overfull boxes.

The preproduction discount mismatch was caught before the successful source freeze, corrected, and disclosed. This is appropriate scientific practice.

## 3. Blocking concerns

### B1. The prospective evidence is adverse to the pure neural policy

The strongest direct result is not neutral:

- pure ReLU minus common: 20 strictly positive intervals, 0 negative, 0 unresolved;
- pure quadratic minus common: 16 strictly positive, 0 negative, 4 unresolved;
- pure ReLU minus augmented ReLU: 20 strictly positive intervals; and
- pure quadratic minus augmented quadratic: 16 strictly positive, 4 unresolved.

Costs are minimized, so the pure fitted policy is worse wherever the interval is strictly positive. No pure fitted policy has a direct interval certifying lower expected cost than the common policy.

A method paper can publish an adverse result, but the manuscript cannot simultaneously use these data as affirmative evidence that NBO is a competitive policy generator.

### B2. The augmented result is generated by a conventional fallback

The common-augmented policy retains the common Bellman candidate at every node and inserts a fitted proposal only when the latter has a smaller verified upper endpoint. The final guarded bounds are numerically indistinguishable from the common bounds:

- maximum ReLU guarded-minus-common final-bound difference: below `2.7e-12`;
- maximum quadratic guarded-minus-common final-bound difference: below `2.0e-12`.

At the finest declared rungs, fitted actions supply only about 5.2 percent of ReLU node--date witnesses and 6.4 percent of quadratic witnesses. Even with those substitutions, all twenty guarded-minus-common expected-cost intervals contain zero.

The augmented policy is a valid safe catalogue policy. It is not evidence that the fitted neural continuation improves on the conventional Bellman construction. The current results identify the common candidate as the effective accuracy and reliability anchor.

### B3. The pure fitted policies do not reach the tight targets

Across the twenty fitted task--seed objects, attainment counts are:

| Policy | `1/2` | `1/4` | `1/8` | `1/16` | `1/32` |
|---|---:|---:|---:|---:|---:|
| Pure ReLU | 16 | 16 | 12 | 4 | 0 |
| Pure quadratic | 16 | 16 | 12 | 8 | 0 |
| Augmented ReLU | 20 | 16 | 16 | 16 | 12 |
| Augmented quadratic | 20 | 16 | 16 | 16 | 12 |

The augmented counts are inherited from the common fallback. The pure ReLU is generally less accurate than the pure quadratic and can be more than twenty times looser than the common final bound in the declared cells. This is not a successful method-specific accuracy frontier.

### B4. The common method wins every attainable complete-work comparison

The release reports twenty task--tolerance cells for which at least one declared policy attains the target. In every one, the common Bellman policy has the smallest recorded complete release work.

Median fitted-to-common component-work ratios increase with the difficulty of the cell. They are approximately:

- ReLU: 1.04, 1.05, 1.06, 1.07, and 1.11 across the five cells;
- quadratic: 1.02, 1.02, 1.05, 1.06, and 1.11.

The postproduction accounting audit transparently charges an unallocated residual of about 5.43 seconds to every method. That convention does not change the ranking, but it is not an observed method-specific runtime. CPU frequency is uncontrolled and the clocks are single-host descriptive observations. The evidence therefore establishes no NBO work advantage; it consistently favors the common comparator.

### B5. The multidimensional result remains a tensor-grid feasibility experiment

At the finest declared rungs, the common reference uses:

| Cell | State nodes | Point--action queries | Final bound |
|---|---:|---:|---:|
| `d2-m1-T2` | 4,225 | 143,650 | 0.00374 |
| `d2-m1-T3` | 4,225 | 215,475 | 0.00758 |
| `d2-m2-T2` | 4,225 | 1,292,850 | 0.00541 |
| `d4-m1-T3` | 83,521 | 4,259,571 | 0.05712 |
| `d8-m1-T2` | 390,625 | 7,031,250 | 0.37961 |

The eight-dimensional cell uses only four subdivisions per coordinate and certifies only `1/2`; targets `1/4`, `1/8`, `1/16`, and `1/32` all exhaust the cap. The paper correctly discloses the exponential dependence, but this means the experiment does not demonstrate a practical high-dimensional numerical method.

A four- or eight-dimensional tensor reference is not a substitute for comparison with sparse-grid, adaptive-partition, monotone-convex, low-rank, or modern approximate-policy-iteration methods.

### B6. The successful theorem is model-specific and method-neutral

The new proof uses a particular combination of:

- finite horizon;
- a compact cube state space;
- convex stage and terminal costs;
- an affine capacity simplex;
- a transition whose nonlinearity admits an explicit convexity-defect bound;
- conditional expectations with bounded independent shocks; and
- multilinear interpolation on a tensor lattice.

These assumptions define a coherent and useful class. They do not establish the broad controlled-diffusion, recursive-utility, endogenous-preference, temporal-self, or dynamic-game program retained by the paper. Nor does the proof depend on the candidate being neural: it verifies any stored nodal action catalogue satisfying the numerical brackets.

The correct contribution is a verification theorem for a convex dynamic program, not a general foundation for Neural Bellman Operators.

### B7. Training reliability is not identified

There are four fixed fitting seeds and forty fitted services. The 327,680 path rows belong to policy-cost evaluation; they are not independent optimizer runs. The paper correctly avoids a population claim, but the title and broad method framing still invite one.

R62 does not estimate:

- the probability that fresh neural training reaches a declared certificate;
- expected performance over initialization or task distributions;
- a worst-case deterministic training cap for the fitted ReLU architecture; or
- the work required after failed training and restart.

The safe augmented service avoids this problem by falling back to the common policy. That is an adoption rule, not a neural training guarantee.

### B8. The baseline set is insufficient for the claimed numerical-method scope

The common Bellman lattice is a strong and appropriate internal comparator, and it already dominates the fitted methods. But the manuscript retains a broad numerical-method ambition without comparing against adaptive conventional methods designed for convex dynamic programs.

A top-journal method study should include, where applicable:

- adaptive or sparse-grid dynamic programming;
- monotone/convex interpolation methods;
- conventional fitted-value or policy iteration with the same verifier;
- structured quadratic or local polynomial approximations; and
- dimension-adaptive integration and action search.

Because the elementary common lattice already wins every complete-work cell, the absence of stronger conventional baselines is consequential rather than cosmetic.

### B9. The economic conclusion is limited

The study uses normalized theoretical investment economies. It provides no estimated primitives, calibrated welfare metric, empirically meaningful policy counterfactual, or economic valuation of the symbolic certification fee. The direct economic result is principally that the pure fitted policies cost more than the common policy, while augmented policies are statistically unresolved against it.

A numerical paper need not be empirical. But then it must establish a broadly useful algorithmic frontier. R62 does not: the conventional policy is cheaper, sharper, and at least as good in direct cost on the deposited evidence.

### B10. The cumulative publication remains disproportionate to the result

The active article is 106 pages and its supplement 69 pages. Complete preserved companions are 216 and 175 pages. The paper contains a long sequence of historical constructions, corrections, applications, evidence regimes, and audit layers.

The new R62 chain can be stated much more sharply:

1. primitive convexity and semiconcavity;
2. second-order Bellman enclosures;
3. certification of the actual acquired policy;
4. a candidate catalogue with a safe common fallback; and
5. an adverse prospective comparison.

That is potentially a valuable focused paper. In the present cumulative form, the central theorem and the decisive negative evidence are difficult to identify, and the breadth substantially exceeds what the R62 experiment establishes.

## 4. Major comments and required changes

### M1. Separate the verifier from the candidate generator

The paper should define the verification layer as a method-neutral object and evaluate ReLU, quadratic, common-lattice, and other generators through it. Claims about NBO should be restricted to incremental performance beyond the verifier and beyond the common candidate.

### M2. Make the adverse prospective result the primary numerical conclusion

The abstract and introduction should state prominently that:

- all twenty pure ReLU policies have higher expected cost than the common policy;
- augmented-versus-common comparisons are unresolved;
- common has the smallest complete work in all attainable cells; and
- the eight-dimensional cell reaches only the coarse target.

These are not ancillary caveats. They are the main prospective findings.

### M3. Add strong adaptive conventional baselines

The next study should use the same original-optimum verifier for adaptive sparse grids, convex interpolation, fitted-value iteration, policy iteration, and structure-exploiting approximations. Baselines must choose their own accuracy and refinement schedules, and all failed stages must be charged.

### M4. Demonstrate a setting in which the fitted representation adds value

The current common lattice supplies the policy accuracy and the fitted proposal does not improve expected cost or complete work. A new benchmark should be selected because the fitted continuation can plausibly reduce reference work—without retaining a full conventional solution as a fallback at every state.

### M5. Specify a training-reliability estimand

Choose and preregister one of the following:

- expected certified performance over a stated initialization distribution;
- probability of reaching a target under a fixed work budget;
- deterministic worst-case performance over a finite initialization catalogue; or
- total work including restart and failure.

Four fixed seeds cannot support a general reliability statement.

### M6. Replace the post hoc residual allocation with direct service timings

The current residual charge is transparent and conservative, but future comparisons should execute each deployable service in an isolated process from raw primitives through durable output. Repeated runs, fixed affinity, controlled thread counts, and machine-independent operation counts should accompany wall clocks.

### M7. Provide independent mathematical validation of the R62 theorem

The primitive constants, convexity defect, semiconcavity recursion, simplex interpolation, boundary action cover, and floating execution account form the paper’s most valuable technical contribution. They deserve a compact self-contained proof, numerical counterexample tests at each boundary case, and, ideally, independent formal or interval validation.

### M8. Quantify approximation and memory scaling beyond the tensor grid

Report accuracy and work as dimension, horizon, action dimension, shock dimension, and target tolerance change. A practical method must show how it avoids or manages the exponential state lattice rather than merely documenting it.

### M9. Supply an economically meaningful adoption problem

If the symbolic certification fee is retained, specify an economic unit and a decision maker’s loss function. Otherwise, present the work frontier directly and avoid implying a welfare interpretation that is not calibrated.

### M10. Refocus the manuscript

A publishable paper should contain one model class, one verification theorem, one implementation contract, one prospective comparison, and one concise account of limitations. Historical applications and prior revision evidence can remain in a repository archive rather than in the active Econometrica submission.

## 5. A focused publishable route

The strongest object in R62 is a potential paper of the following form:

> **Whole-Domain Certification of Implemented Policies in Convex Dynamic Programs**

Its contribution would be:

1. primitive convexity, Lipschitz, and semiconcavity bounds;
2. signed second-order interpolation and quadrature enclosures;
3. continuous-action lower and upper Bellman brackets;
4. an actual-policy certificate with state acquisition and action rounding;
5. a method-neutral interface for candidate generators; and
6. a prospective numerical comparison that includes strong adaptive conventional methods.

Such a paper could report the present adverse neural findings as an informative result: neural proposals need not improve a strong conventional candidate, and a safe catalogue can prevent damage while preserving a rigorous certificate. That is a scientifically defensible contribution. It is different from claiming an Econometrica-level advantage for Neural Bellman Operators as a broad platform.

## 6. Independent verification performed for this report

I downloaded and verified both source-bound R62 artifacts:

- science artifact SHA-256: `33416454ea1418303e132c4fd00cba1f47c7c48ee3564acf2b808833e105c9fb`;
- publication artifact SHA-256: `25b15a12a5ad2ed15af1291f7a5ca2789bbe9ac2abfd9f7550ece872b45e3963`.

A standard-library audit deposited with this report independently checked:

1. the five task records and their summary/cost/clock hash bindings;
2. all 295 published interval records;
3. the release count of 18,806,777 nodal action records;
4. the clean-archive publication status;
5. all prospective target-attainment counts;
6. all direct-cost sign classifications used above;
7. the complete-work winner in every attainable task--target cell;
8. the fraction of additional fitted witness nodes;
9. the final common, pure, and augmented policy bounds; and
10. the final reference node and point--action query counts.

The recomputed key findings are:

- pure ReLU versus common: `20 positive / 0 unresolved / 0 negative`;
- augmented ReLU versus common: `0 positive / 20 unresolved / 0 negative`;
- pure quadratic versus common: `16 positive / 4 unresolved / 0 negative`;
- augmented quadratic versus common: `0 positive / 20 unresolved / 0 negative`;
- common complete-work wins: `20 / 20` attainable cells;
- maximum augmented-minus-common final-bound difference: below `3e-12`;
- pure ReLU `1/32` attainments: `0 / 20`;
- pure quadratic `1/32` attainments: `0 / 20`;
- additional finest-rung witness shares: approximately `5.23%` for ReLU and `6.36%` for quadratic.

The audit does not rerun training, simulation, compilation, or timing. New executions would create new optimizer and hardware observations rather than verify the frozen records. The four fitting seeds remain a finite catalogue, and the single-host clocks support no hardware-general inference.

## 7. Recommendation

R62 is mathematically and evidentially stronger than R61. The original-optimum certificate for the actual implemented policy is a real contribution, and the repository’s provenance and negative-result disclosure are exemplary.

Nevertheless, the paper does not meet the standard for an Econometrica numerical-methods contribution in its present form. The common conventional Bellman construction supplies the sharpest reliable policies, wins every attainable complete-work comparison, and is never beaten by the pure ReLU policy in direct expected cost. The augmented neural policies recover the common frontier only by retaining that common policy as a fallback. The high-dimensional evidence remains a coarse tensor-grid experiment, and the broad historical program is not validated by the new model-specific theorem.

I therefore recommend **rejection in the present form and no further ordinary revision of the cumulative manuscript**. A new, substantially shorter submission centered on method-neutral whole-domain certification for convex dynamic programs could merit serious review.
