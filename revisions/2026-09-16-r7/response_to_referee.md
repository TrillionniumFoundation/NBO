# Response to the sixth-round advisory referee report

**Paper:** *Neural Bellman Operators*, Qian QI  
**Revision:** R7, 16 September 2026  
**Reviewed manuscript:** `24011fef6da09bc05dc79946a3c1779e1fe7d8a8`  
**Report and revision parent:** `10a7cbee28de5126d844dea9eae8c36c5cda9e9b`  
**New branch:** `revision/econometrica-r7-2026-09-16`

We thank the referee for the matched count comparison and for distinguishing the validity of the corrected chord from its incremental contribution. We accept that distinction. This revision develops the comparison mathematically, measures both its common-bank and autonomous costs, supplies a primitive economic sufficient condition, and uses class-specific transition certificates to establish an economic choice on a joint parameter region. It does not respond by deleting the adverse structural QP or mesh-only comparisons, calling exact dynamic programming neural training, or treating a generic welfare tolerance as a risk-sign tolerance.

The complete main manuscript is `ECTA_R7.tex`; the complete supplement is `SUPP_R7.tex`. Unchanged sections are explicit inputs from the immutable R6 paper directory, so the new entry points build full manuscripts, not response appendices. All earlier source, evidence, and review material is preserved. The new proofs are in Supplement S.10–S.11; the executed records, stage timings, policy arrays, and tensor coefficients are in `replication/r7/output/`. `execution_summary.md` is generated from that run rather than manually transcribing favorable figures.

## R6-F1. Localization confounded the comparison; local count dominates

**Response.** We agree with the coefficient ordering in the report. The retained global three-policy column is still a valid upper-bound calculation, but it was not a matched sharpness comparator for an adaptive 17–19-policy bank. The new text states that distinction at the original table, rather than leaving the correction in the response letter alone.

**Comparative theory.** Main Section 6, “The Price of Compressing an Upper Oracle” (`04e_comparative_oracles.tex`, Proposition `prop:r7_dominance`), explicitly gives the localized count recursion, the corrected Bernstein coefficients, and a finite-horizon rectangular upper recursion. The count recursion uses the same action before mixing the two hidden endpoint-law branches. It therefore respects the information enlargement identified in the report; it does not make the feasible policies anticipate the future count. We credit the advisory referee for the first ordering. Supplement S.10 reproduces its proof, including terminal, one-period, two-period, and endpoint-count cases. The code also reproduces the strict two-period example with coefficient vectors `(1,1,1)` and `(1,1/2,1)`.

**What compression buys.** The corrected construction replaces count-dependent propagation weights by the worst endpoint contribution, while retaining the signed cross-operator correction. With exact endpoint values shared, its implementation requires `4H-6` action-wide base-kernel applications for `H>=2`, versus `H(H+1)-2` for count with neighboring continuations cached. At eight dates this is 26 versus 70. The nonzero correction stores seven state vectors, compared with 28 interior count vectors. These counts do not include the common endpoint values, feasible-policy coefficient bank, transition representation, or temporary action arrays. The compact implementation expands only one date's coefficients at a time, and that expansion is charged to certificate time. We do not turn a kernel-call ratio into a claimed wall-clock ratio.

**Matched execution.** `matched.py` freshly solves every original anchor and independently reevaluates its policy coefficients before comparing the three upper recursions on every original interval. States, dates, full target actions, two feasible endpoint policies, and eight closed coefficient cells are identical within every comparison. The 51 original intervals reproduce the report's full-model bounds, with the following count-versus-chord pairs:

| Contract | Corrected bound | Matched local-count bound |
|---:|---:|---:|
| 0 | 0.0009045733003105738 | 0.0007338463674633200 |
| 0.5 | 0.0008998289604379428 | 0.0006851026198662069 |
| 1 | 0.0009414120278261606 | 0.0004357448654037643 |

Every stage is now costed: kernel construction, anchor solves, policy evaluation, local restriction, upper construction, and subdivision. Shared work is measured once and attributed equally. Two coarser common banks at `d=0.5` provide additional precision–work points. The rectangular upper uses the same economic target and lower bank. Raw interval bounds and stage times remain available even when they are unfavorable to an upper method. Full-bank timing is one complete serial single-thread pass, explicitly labeled as such, not a cross-machine comparison with the report.

**Autonomous anchor discovery.** Common banks alone do not answer the referee's question about oracle demand. A separate `adaptive.py` experiment starts each arm at `[0,1]` with an empty policy cache. It fixes `d=0.5`, the `0.001` tolerance, left-first dyadic refinement, two local endpoint policies, and eight coefficient cells. It compares chord-only, count-only, and a cascade that tries count after a chord failure. All rejected parents and all newly requested anchors are charged. The new main table and `adaptive.json` report the realized anchor counts, upper-kernel work, bounds, and total times. We also prove and check that the cascade cannot request an anchor outside the chord-only refinement tree under this common rule. Fewer anchors are not automatically equated with lower elapsed time.

The original comparison's localization confound is therefore replaced by a matched ordering theorem, a work and storage account, a common-bank frontier, and an independent adaptive comparison. The correction is a controlled compression, not a sharper upper bound than localized count.

## R6-F2. A valid finite-model construction needs a positive computational case

**Response.** The computational claim is now supported by results about the allocation of upper-information work and endpoint solves, not by the mere existence of another valid inequality. The new comparative experiment retains the conventional solvers on both sides. Exact finite-action backward optimization still constructs the demonstrated endpoints; no unexecuted neural residual shortcut is used to explain the measured costs.

**Total-error theorem.** Theorem `thm:r7_total_error` establishes a bound on the complete endpoint-policy coefficient certificate, not only the added cross term. From primitive reward bounds, substochastic row masses, reward differences, and kernel differences, it recursively constructs `V_n`, `L_n`, and `Q_n`. On width `w`, the certificate is at most

`max_n {2 L_n w + (1/2) Q_n w^2}`.

The proof controls conditional-count fixed-policy coefficients as well as pointwise optimal values. It allows maximizing actions to change. It yields a finite dyadic termination rule and an `O(epsilon^-1)` worst-case scalar interval count for fixed finite-model constants. We explicitly do not infer an `O(epsilon^-1/2)` policy-bank rate from the second-order correction. Nor is this a dimension-free high-dimensional parameter covering theorem. These are positive quantitative statements with explicit constants and a proof, rather than additional qualifications on the old bound.

**Scaling and storage.** Supplement S.10 separates upper-oracle work, action/state dependence, lower-policy storage, and subdivision. The lower bank still requires order `m S H^2` coefficients and `m S H` policy indices. Instrumented small-model backends check the actual production kernel-call counts and compact-vector counts at horizons 1, 2, 3, 4, 6, 8, 12, and 16. These tests validate implementation accounting; the recursions prove the scaling statement. Main tables separately report what happens in the complete stopped economy.

**Regional verification comparison.** We add Quatmann, Dehnert, Jansen, Junges, and Katoen (2016), and specifically recognize that repeated-parameter regional certification and the two-toss obstruction already occur there. The text distinguishes finite-horizon reward optimization with feasible-policy lower values from their probabilistic verification specification, and distinguishes three dependence relaxations: state/datewise endpoint resets, a revealed remaining regime count, and the compressed signed correction. We implement the explicitly stated rectangular reward recursion on the same finite target. It is not claimed to be a reimplementation or benchmark of their software, and no exhaustive priority claim is made for regional verification. The learned policy proposals, exact OLS comparison, structural QP, and mesh-only bank retain their original attributions.

The positive case is thus a controlled precision–work/anchor-demand choice within a reusable representation, coupled to a decision the representation actually certifies. Its general scientific significance remains a matter for evaluation, not a status inferred from passing tests.

## R6-F3. The economic identities do not predict an option ordering from primitives

**Response.** The envelope and set-inclusion identities are retained, but they are no longer the only portable economic result. Proposition `prop:r7_primitive` derives a primitive sufficient condition in a two-stage CRRA specialization. It takes consumption lotteries, an initial preference index, an adjustment interval, effort cost, and an operating-duration difference as primitives. It does not condition the sign prediction on moments of already optimized dynamic policies.

For each class, let `g_sigma` be expected utility's derivative with respect to the preference index at zero adjustment and let `M_sigma` bound its negative second derivative over the feasible preference interval. CRRA utility is strictly concave in that index for `u>1`, giving

`g_sigma^2 / [2(k+M_sigma)] <= Omega_sigma <= g_sigma^2 / (2k)`,

provided the lower quadratic's trial adjustment is feasible. The relative-option sufficient condition follows by subtracting the negative-class upper bound from the positive-class lower bound. With a positive primitive duration difference, it predicts both a contract-equivalent downward threshold shift and an interval on which the two adjustment regimes select opposite risk classes. The proof is global on the stated preference interval; it is not an interior portfolio first-order condition.

**An entire family, not just selected rows.** The family has `u0=2`, adjustment bound `0.2`, fixed consumption `0.5` in the nonpositive class, and risky consumption `0.05` or `0.8`. The downside probability ranges over `[0.06,0.10]`, the cost over `[20,80]`, and the duration difference is `0.5`. The proof uses a convex integral representation of negative CRRA preference curvature to bound its maximum at endpoint preferences; it is affine in the lottery probability. Conservative primitive extrema establish a relative option exceeding `0.00186` and a threshold shift exceeding `0.00372` everywhere in this probability–cost rectangle. The nine displayed optimizations are checks and illustrations, not the basis of the continuum claim. Each test contract is selected from the primitive lower bound before using the optimized option values.

The consumption downside changes the magnitude of the preference-adjustment shadow; its squared magnitude relative to curvature and effort cost determines the bound. The result is therefore more specific than “a larger feasible set helps.” It does not assert that every increase in risk must raise the option premium. The specialization is explicitly an explanatory model, not a substitute calibration or approximation theorem for the eight-date stopped economy. The latter retains every original financial, stopping, and preference-risk primitive and receives the new decision-specific computation below.

## R6-F4. The transition welfare certificate does not certify the risk conclusion

**Response.** We agree that a generic `0.001` welfare guarantee cannot determine a difference on the order of `1e-5`. The new experiment does not use that tolerance, and it does not convert the old `2e-5` direct-solver bracket into a certified transition threshold.

**Decision-specific theorem.** Proposition `prop:r7_tensor` constructs constrained upper and feasible lower values separately for each first-risk class and each adjustment regime. At fixed transition probability, class values are convex in the contract coefficient. Hence interpolation of valid upper polynomials at the two contract endpoints is an upper value throughout the contract interval. Fixed-policy values are affine in that coefficient and polynomial in the repeated transition parameter. Tensor Bernstein coefficient extrema then give a uniform lower and upper bound on the class difference. The theorem includes separate absolute arithmetic allowances and directly certifies strict signs. It does not require the duration-separation assumption used for global threshold uniqueness.

**Full-model region result.** At the original initial state `(u,X)=(2,1.25)` and `k=2`, the new calculation covers the entire joint region

`lambda in [0,0.25], d in [0.4,0.45]`.

The full target has 1,617 states, eight dates, and 1,568 actions before imposing the stated class and adjustment restrictions. The no-adjustment arm fixes deliberate adjustment to zero at all dates and states but retains stochastic preference shocks, the same shock-law mixture, stopping boundary, settlement, consumption menu, and financial primitives. Later risky positions may change sign. Eight corner optimizations yield sixteen feasible class policies, and eight localized count constructions supply the upper coefficients. The original rectangle is accepted without additional subdivision.

The deposited bounds imply an adjusted positive-class advantage greater than `6.8887e-5`, a no-adjustment nonpositive-class advantage greater than `5.2993e-5`, and a relative adjustment option greater than `1.2188e-4` throughout that rectangle. The precise bounds, largest class-value gaps, and arithmetic allowance are generated into the new main table from the executed records. This is the required connection: the reusable transition representation and its error account establish the economic ranking over a region, rather than coexist with another list of exact point solves.

**Error budget and reproducibility.** `decision.json` separates the four class gaps from the per-class arithmetic allowance. The latter uses a conservative path-operation budget, nonnegative sixteen-entry row bounds, and absolute reward/value magnitude bounds relative to the stored finite arrays. It includes intermediate policy evaluations at `d=1`, even though the reported region ends at `d=0.45`. Supplement S.11 specifies the round-to-nearest model and its limitations. This is not represented as directed-rounding interval arithmetic or a quadrature/diffusion error certificate. The complete tensor upper/lower coefficients and policy-feature arrays are deposited; `validate.replay_decision` reconstructs the reported sign bounds without any optimizer call. Independent selected-kernel evaluation checks corner policies through a separate arithmetic path. Neither replay nor a grid of corners is substituted for the tensor inequality.

This new strict-region result has no threshold uniqueness claim. The inherited direct-solver brackets remain useful and explicitly retain their original scope. Thus the missing connection is supplied without overstating the precision or changing the economic target.

## Preservation, manuscript organization, and verification

All historical files except the revision index remain byte-identical to the report's parent. The index is advanced by prepending an R7 entry while retaining its earlier contents. The new main manuscript includes the full original operator analysis, continuous-time formulation, finite approximation account, original stopped economy, reward certificates, Merton and Epstein–Zin exercises, temporal-self model, persistent competition, structural QP, mesh-only ablation, old transition results, and direct risk brackets. Changed prose corrects the comparative inference and reorganizes the contribution; no unfavorable table or economic model is removed.

The manuscripts use the repository's `econsocart` journal class without modifying its class or configuration. The abstract, definitions, propositions, proofs, economic interpretation, and numerical captions are separately structured. New longer proofs and replication details are in the supplement. These are complete journal-style review copies, not a representation that a journal has invited this revision, appointed the advisory referee, or approved the findings.

`build_report.json` records actual compilation, page counts, reference and box checks, hashes, and protected-history verification. `source_inventory.json` pins the authored inputs, and the workflow records a reachable source commit before executing them. Passing these checks is evidence about the delivered files and implementations, not an editorial verdict. The new comparative and economic propositions and their executed implications are the substantive basis for another review.
