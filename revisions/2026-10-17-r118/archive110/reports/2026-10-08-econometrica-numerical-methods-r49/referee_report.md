# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Latest manuscript/source revision reviewed:** `revision/econometrica-nbo-r49-source-2026-10-08`  
**Pinned revision commit:** `4ede6077aa3d78aa36ec9b9471e5338a636a49f4`  
**Pinned revision tree:** `98098e476c1f8d690e12ae8dc95c976264740693`  
**Pinned main manuscript:** `revisions/2026-10-08-r49/ECTA.tex`, Git blob `599902482457b67e7b7a5a2c40af44dd39f9a940`  
**Pinned technical supplement:** `revisions/2026-10-08-r49/supp.tex`, Git blob `3a99d5c896001e1318dfb3b239cbc71d20ecfa50`  
**Main R49 science run / artifact:** `37725036673` / `11529312739`, SHA-256 `d367b908c754dfa66efd5b6ed40fd6ce46a6e6606cde959811afb850b4b3c601`  
**Prospective graded-FVI run / artifact:** `37728825824` / `11528468638`, SHA-256 `280f32e6cc66344e31c5e04487cd813bdaf21908f6860d1449b2c297f4268517`  
**Report date:** 8 October 2026  
**Recommendation:** **Reject in the present form and do not invite another ordinary revision of the cumulative manuscript. A new, sharply focused paper on owner-preserving compilation and resource-certified policy construction for constrained Lipschitz dynamic programs could merit evaluation, but R49 does not establish an Econometrica-level method-specific advantage for Neural Bellman Operators.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R49 is a technically serious response to the preceding reports. It makes three substantive advances.

First, it replaces repeated dense evaluation of a minimum-of-cones continuation by an owner-preserving multidimensional distance transform. The theorem retains the original action witness and tie rule, and the off-grid corner formula returns the same continuation and policy as full enumeration. This is a useful compilation result. It separates construction, representation, and policy execution more cleanly than prior versions.

Second, it separates state, action, and integration resources. The policy-loss account has the form
\[
  a/N+b/K+q/M+\eta,
\]
and the paper gives a continuous allocation rule, clipped finite-ladder implementation, complete positive-tolerance first-crossing curves, and explicit work counts. This is preferable to scaling all numerical resources by a single inherited resolution parameter.

Third, R49 directly compares the actual policies returned at its first crossings. The comparison uses common innovation paths and evaluates expected discounted policy-cost differences rather than subtracting separate regret bounds. It also adds a priced sensor catalogue and extends the stress study through dimensions three and four.

These changes answer real methodological objections. The decisive new economic evidence, however, is unfavorable to the central method claim.

Among the 96 R49 actual-policy comparisons, the interval for witness cost minus tensor-FVI cost has a strictly positive lower endpoint in **93 cases**, contains zero in **3**, and is strictly negative in **none**. Every one of the 64 comparisons at targets one and two certifies a higher expected cost for the witness policy. At target four, 29 of 32 comparisons favor FVI and three remain unresolved. This pattern holds despite the witness method often having a tighter all-state certificate or crossing a certificate target at a smaller state grid.

This distinction is fundamental. R49 shows that a sharper certificate and an earlier work-to-certificate crossing can coexist with a worse implemented economic policy. The paper is commendably transparent about this result, but it means that the headline numerical advantage is not an advantage in the economic object that ultimately matters.

The conventional comparison also remains unresolved at the algorithmic-design level. The originally named “curvature-FVI” procedure realizes no nonuniform date model at all. Across all 72 matched checkpoints its substantive continuation, actor, ladder, and policy bound are identical to uniform tensor FVI; it merely adds pilot and allocation overhead. Its final complete-prefix time is 13.8–17.3 percent higher, with a median overhead of about 15.1 percent.

The prospective amendment correctly recognizes this issue and executes a genuinely nonuniform graded-FVI block. That amendment is good scientific practice. The result is again adverse: the graded method has a looser final bound in all 12 matched services, by a factor of approximately 1.322–1.339, and is slower in all 12, by a factor of approximately 1.007–1.031. It reaches the one-half target in zero of twelve services, compared with three for uniform FVI and six for the compiled witness. This is informative negative evidence about the selected grading heuristic, not a general result against adaptive conventional dynamic programming.

R49 also remains incomplete as a submission object. The repository root still designates R48 as canonical. There is no `r49-review-ready` branch, no R49 response, no committed R49 result archive, no generated table directory on the manuscript source branch, and no compiled R49 publication. The main science workflow completed the full catalogue and created a local evidence commit, but the evidence-branch push failed with an HTTP 500; the immutable artifact survived. The separately frozen graded evidence did land on its own branch, but that branch and the manuscript branch diverge. Thus a referee can reconstruct and review the R49 science, but there is not one canonical immutable paper-and-evidence object.

The strongest contribution in R49 is consequently narrower than the cumulative paper: a policy-owner-preserving compiler for a Lipschitz-envelope dynamic program, an explicit accuracy-resource account, and unusually honest evidence that certificate efficiency need not imply policy quality. I view this as potentially publishable in focused form. I do not view the current evidence as establishing a distinctive neural numerical method, a superior work-to-economic-accuracy frontier, or an Econometrica-scale economic application.

## 2. Substantial improvements

### 2.1 The owner-preserving compilation theorem is useful

For tensor state sites and the \(\ell^1\) cone envelope, R49 preprocesses nodal values and lexicographic original owners by separable one-dimensional distance transforms. An off-grid query then examines only the corners of the containing cell. The original owner—not the transformed grid vertex—is returned, so the feasible action witness is preserved.

The theorem correctly distinguishes three objects: the mathematical min-plus envelope, its native compiled implementation, and an exact affine–ReLU representation of the same object. This removes an avoidable full state-cover scan while leaving the policy unchanged.

### 2.2 State, action, and innovation resources are separated

The explicit account makes clear which policy-loss terms are reduced by state resolution, action resolution, innovation quadrature, and numerical query accuracy. The continuous relaxation gives a transparent benchmark for allocating a fixed error budget. The clipped finite rule acknowledges minimum resolutions and finite caps rather than silently treating continuous optimizer outputs as executable integers.

### 2.3 Complete tolerance curves are reconstructed

The paper does not rely only on four coarse prospective targets. It reconstructs the exact step function from every frozen policy bound and full-prefix work record. This is the right way to expose target sensitivity and to prevent a single favorable threshold from carrying the entire method comparison.

### 2.4 Actual first-crossing policies are compared

This is the most important evidentiary improvement. The left and right policies are the stored objects at the methods’ own first crossings. The expectation is the actual discounted policy-cost difference under the declared initial law and acquisition contract. Common innovations reduce variance but do not change the estimand.

### 2.5 Dimension-three and dimension-four stress runs are included

R49 extends the compiled witness and tensor-FVI constructions beyond the two-state example. The dimension-four compiled implementation is modestly faster than tensor FVI at the coarse target five in the recorded environment, while retaining a tighter bound. This is a useful finite observation about the compilation mechanism.

### 2.6 The adaptive-baseline defect is disclosed prospectively

The amendment was committed before inspecting the graded-study outcomes. It explicitly states why the original curvature-times-length-squared rule can remain uniform on a power-of-two ladder and refuses to relabel the original block. A separate matched block with a genuinely nonuniform grid is then executed without pooling clocks across hosts or runs.

### 2.7 Adverse evidence is retained

R49 reports that the central construction is not uniquely neural, actual policy costs often favor FVI, the first adaptive rule never adapts, the genuinely graded rule is worse on the declared block, tensor-cover dependence remains, information prices are normalized primitives rather than estimated welfare prices, and no universal neural dominance is established. This disclosure is exemplary.

## 3. Blocking concerns

### B1. R49 is not a canonical, self-contained submitted manuscript

The latest R49 manuscript branch is named `r49-source`, not `r49-review-ready`. The repository root still names R48 as authoritative. The R49 source branch contains `ECTA.tex`, `supp.tex`, section files, analysis scripts, and a source manifest, but it does not contain a R49 README declaring a canonical review object, a point-by-point response, the frozen main result records, the generated `tables/` directory required by the LaTeX sources, a release/final-delivery audit, or compiled R49 PDFs.

The main science run completed all scientific jobs and locally committed 842 evidence files, but the branch push failed. The artifact is hash-bound; the intended evidence branch is unavailable. The graded block exists on a separate evidence branch that diverges from the manuscript source branch.

A journal submission must bind manuscript, response, both evidence blocks, generated tables, tests, and release audit into one immutable review-ready branch.

### B2. The identified compiler advantage is not neural-specific

The positive algorithm is the owner-preserving compilation of a classical minimum of Lipschitz cones. The native min-plus implementation and the affine–ReLU circuit compute the same function, return the same owner, deploy the same repaired action, and receive the same certificate.

The distance-transform saving is therefore available to the conventional implementation. It is not evidence that a neural architecture approximates a difficult continuation more efficiently, generalizes across states, or improves nonconvex training. R49 should be judged as a certified dynamic-programming compilation result.

### B3. Direct economic performance strongly favors tensor FVI

The 96 new policy pairs produce the following simultaneous sign pattern for \(J_{\mathrm{witness}}-J_{\mathrm{FVI}}\):

| Target | Witness higher cost | Witness lower cost | Unresolved |
|---:|---:|---:|---:|
| 4 | 29 | 0 | 3 |
| 2 | 32 | 0 | 0 |
| 1 | 32 | 0 | 0 |
| **Total** | **93** | **0** | **3** |

The median interval midpoint is approximately `0.01198`; the largest is approximately `0.10310`. Both full-information and eight-bit comparisons predominantly favor FVI. When actual economic policies are directly compared and the sign never favors the proposed method, certificate efficiency cannot be presented as an economic method advantage.

### B4. Certificate attainment and policy quality point in opposite directions

The two-state witness method reaches targets 4, 2, and 1 in all twelve services and reaches one-half in six. Uniform FVI reaches the first three in all twelve and one-half in three. In the price-four cells, witness often crosses targets two and one at a smaller grid and lower prefix time.

Yet the policies at those crossings have higher expected cost in the direct study. The method is optimizing or certifying a conservative bound more effectively, not returning the better policy on the tested economies.

The paper needs a joint frontier whose ordinate is actual policy cost—or a valid upper confidence bound on it—and whose abscissa is complete construction plus verification work.

### B5. The original adaptive FVI comparison did not adapt

Every original curvature-FVI date model is uniform. Across 72 matched rung checkpoints, the state/action ladders, policy bounds, stored actors, and substantive continuation models are identical to tensor FVI. Only method metadata, pilots, and timing differ. The curvature version is slower by a factor of approximately `1.138–1.173`, median `1.151`.

Those rows are not evidence against adaptive FVI. They show that one proposed heuristic failed to alter the grid and imposed overhead.

### B6. The genuinely nonuniform graded baseline is also unfavorable, but not definitive

The prospective graded block executes nonuniform date models. It has a worse final bound in 12/12 pairs, with graded/uniform ratios of approximately `1.322–1.339`; it is slower in 12/12, with ratios of approximately `1.007–1.031`; and it reaches target one-half in 0/12 services, versus 3/12 for uniform FVI.

This is useful negative evidence about one equal-curvature-mass rule. It is not a comparison with adaptive sparse grids, hierarchical surpluses, local residual refinement, anisotropic partitions, or other strong conventional methods.

### B7. The dimension study remains a low-dimensional tensor-cover stress test

The executed dimensions are two, three, and four. Ladders and caps differ by dimension, and target five is coarse relative to the one-half frontier studied in two dimensions. Three repetitions reproduce identical checkpoints and only repeat timing.

The state cover still grows as \((N+1)^d\), the off-grid query retains a \(2^d\) corner factor, and action/integration costs remain multiplicative. R49 removes one redundant dense scan; it does not resolve the dimensional bottleneck motivating neural dynamic programming.

### B8. The resource-allocation theorem is a proxy optimization, not yet a complete adaptive algorithm

The continuous allocation result is useful as an accounting identity. Its proxy \(T(N+1)^d(K+1)M\) counts Bellman state-action-innovation evaluations, but not compilation, interpolation, selector execution, interval arithmetic, storage traffic, verification, serialization, or hardware-dependent costs.

The executed study still uses a short predeclared ladder rather than choosing resources prospectively from the theorem. The paper should either implement the allocation rule and compare complete realized work, or present it as an analytical planning bound rather than an empirical efficiency result.

### B9. The sensor-selection result is valid but economically underidentified

The sensor catalogue supplies 104 policy-cost contrasts relative to sixteen-bit acquisition. Of these, 101 contain zero and three certify higher cost at lower precision. The upper-bound selector responds monotonically to the declared bit price.

The bit prices are normalized primitives, not estimated information costs. The selector minimizes a conservative simultaneous upper bound, not observed expected net cost. There is no calibrated sensor technology or sensitivity analysis translating the chosen bits into a substantive adoption decision.

### B10. The cumulative scope remains disproportionate to the completed contribution

The article retains controlled diffusions, recursive utility, endogenous preferences, temporal selves, games, learned critics, factor constructions, mixed precision, witness envelopes, acquisition, and information pricing.

R49’s new evidence directly supports compact finite-horizon expectation problems, tensor state covers and scalar constrained actions, exact owner-preserving Lipschitz envelopes, low-dimensional FVI comparators, and normalized theoretical investment economies. Historical applications do not receive the R49 compiler, allocation rule, first-crossing comparison, or sensor evidence.

## 4. Major comments and required changes

### M1. Produce one canonical R49 submission

Materialize ordinary sources, generated tables, both evidence blocks, response, build outputs, clean-rebuild records, and final-delivery identities on one `r49-review-ready` branch.

### M2. Reframe the principal algorithm as compiled witness dynamic programming

State the native min-plus algorithm first. Treat the affine–ReLU realization as an exact representation theorem. Any neural-specific claim must concern a property not shared by the identical native algorithm.

### M3. Make actual policy cost the primary performance endpoint

Report a common work-to-policy-cost frontier. Certificate width can remain a safety guarantee, but it should not substitute for policy performance when the two orderings conflict in 93 of 96 comparisons.

### M4. Explain why the witness policy is systematically more costly

Decompose policy differences by state, date, action, capacity repair, and active owner. The signs suggest a systematic conservative-action or approximation mechanism, not random noise.

### M5. Replace the failed adaptive baseline with strong adaptive methods

Retain the original and graded negative results, but add at least one method that demonstrably changes its partition in response to an economically relevant residual or surplus criterion and has a competitive implementation.

### M6. Use common-accuracy dimension experiments

Choose at least one target attained by both methods at every reported dimension, keep comparable allocations, and report complete work, memory, and policy cost.

### M7. Execute the separated-resource allocation prospectively

Let the theorem choose or constrain \((N,K,M)\) before each service. Compare against isotropic ladders and method-specific adaptive policies. Preserve failed allocations and planning/verification costs.

### M8. Report resource counts beyond the Bellman-query proxy

Include continuation evaluations, interpolation/corner work, compiled-transform work, actor queries, interval operations, stored coefficients, peak memory, and durable-output costs. Distinguish machine-independent counts from clocks.

### M9. Connect sensor prices to an economic model

Specify an information technology that gives bit prices economic meaning. Compare the certified choice with the ex post expected-net-cost minimizer and report the cost of conservatism.

### M10. Focus the paper

A focused article should have one model class, one compiled-witness theorem, one resource-allocation result, one strong conventional comparison, one direct policy-cost study, and one acquisition decision.

## 5. Potentially publishable focused route

A credible new submission could be titled:

> **Owner-Preserving Compilation and Resource-Certified Policies for Constrained Lipschitz Dynamic Programs**

Its mathematical core would be the original-owner distance transform, off-grid policy identity, acquisition/repair policy sandwich, separated resource allocation, and finite-precision verification. Its numerical core would compare the same returned policies—not only their certificates—against uniform FVI and genuinely competitive adaptive methods on common-accuracy frontiers. Native and ReLU encodings should be treated as representations of one algorithm.

## 6. Independent verification

I downloaded and audited both frozen R49 artifacts. The deposited standard-library audit verifies 836 main-study result hashes and 288 graded-study result hashes; reads all 60 main services and 300 rungs and all 36 graded services and 216 rungs; verifies all 20 repeated service groups have identical checkpoint ladders; verifies all 72 original curvature/tensor checkpoint pairs are substantively identical and produce zero nonuniform date models; reconstructs target attainment and first-crossing clocks; recomputes all 96 new policy-cost signs and 104 sensor contrasts; and recomputes graded-versus-uniform bound and timing ratios.

The principal reconstructed findings are:

- two-state witness attainment at targets `4, 2, 1, 1/2`: `12/12, 12/12, 12/12, 6/12`;
- two-state uniform-FVI attainment: `12/12, 12/12, 12/12, 3/12`;
- original curvature-FVI: zero nonuniform date models and 72/72 substantive checkpoint matches with uniform FVI;
- curvature/uniform final-prefix time ratio: `1.138–1.173`, median `1.151`;
- new policy-cost signs: 93 witness-higher, zero witness-lower, three unresolved;
- targets one and two: 64/64 intervals certify higher witness cost;
- graded FVI: worse final bound and higher time in all 12 matched pairs;
- graded/uniform final-bound ratio: `1.322–1.339`;
- graded/uniform final-prefix time ratio: `1.007–1.031`;
- graded attainment at target one-half: `0/12`.

I did not rerun construction, simulation, LaTeX, or timing services. New executions would create new observations rather than verify the frozen records.

## 7. Recommendation

R49 contains useful mathematics and unusually strong negative evidence. The owner-preserving compiler is a real contribution. The resource decomposition is clear. The direct first-crossing policy comparison is exactly the experiment the prior reports requested. The author also identifies and repairs a defective adaptive baseline without rewriting the original record.

Those improvements do not support the cumulative paper’s central claim. The compiler is method-neutral; the original adaptive comparator does not adapt; the genuine graded comparator is worse than uniform FVI; dimensional evidence remains low-dimensional and tensor based; and, most importantly, actual policy costs favor FVI in 93 of 96 R49 comparisons and never favor witness. The R49 paper-and-evidence object is also not canonical or self-contained.

I therefore recommend **rejection in the present form and no further ordinary revision of the cumulative manuscript**. I would take seriously a new, focused submission on owner-preserving compiled dynamic programming and acquisition-aware certification, provided it treats neural encoding as representation rather than identified advantage, makes actual economic policy cost primary, uses stronger adaptive baselines, and supplies one canonical reproducible submission.
