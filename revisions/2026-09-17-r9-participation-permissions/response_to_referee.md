# Response to the latest advisory referee report — R9

**Manuscript:** Neural Bellman Operators, Qian QI  
**Revision date:** 17 September 2026  
**Review addressed:** `reviews/2026-09-17-econometrica-r8-economic-stress/referee_report.md` at `8c20474bca5b7388f5ba4640ec165f1ad8f5e91a`  
**Reviewed scientific manuscript:** Complete R8 at `be77b2a81b4d3a68806c534c1e892d2eb4b1230d`  
**New branch:** `revision/econometrica-r9-participation-permissions-2026-09-17`  
**Reading entry points:** `ECTA_R9.tex`, `SUPP_R9.tex`, and the compiled PDFs in this directory.

We thank the referee for distinguishing the repaired finite-model contribution from the new economic questions. We have organized this revision around R8-E1 and R8-E2. We do not treat the changed-contract experiments as counterexamples to the original theorem, and we do not answer them by repeating the original feasibility definitions. The new manuscript supplies a participation and service-procurement economy, a finite-enforcement theorem and regional frontier, a surrender-sensitive option decomposition, and an exact first-date permission analysis. The original contract, adverse experiments, computational comparisons, and historical models remain in the complete paper and supplement.

## R8-E1. Mandatory operation and the surrender margin

### Participation and an economic source of commitment

The new main section **“Participation, Termination, and Portfolio Permissions”**, particularly `subsec:r9_participation`, gives an ex ante acceptance decision. An agent may decline the mandate for `G(x0)`. Acceptance specifies the original managed state and settlement protocol, a minimum operating term, a signing grant, and a surrender charge supported by finite external guarantee capacity. A boundary is a verifiable discharge event under the mandate, whereas interior termination is elective surrender. This distinguishes the *right* to exit from the liquidation amount.

The grant and charge use a separate additive utility numeraire. They do not enter managed wealth: doing so would change the original state, consumption, and transition law. Available enforcement capacity is bounded; a carrying cost `C(E)` enters the participation grant. The stated assumptions are a theoretical procurement institution, not an empirical calibration or an optimal contracting theorem.

**New result: `prop:r9_participation`.** The minimum grant is the positive part of outside value minus optimized operating value plus the capacity cost. A principal who values discounted operating service at flow `b` accepts the contract precisely when that flow covers the grant per unit of service actually delivered, for the specified agent-policy selection. The proof and selection qualifications are in S.13. This adds the principal's participation condition rather than assuming someone will fund a loss-making activity.

At the original center, noncancellable participation requires grants `0.7813440809` with adjustment and `0.8165920769` without adjustment before capacity costs. Adjustment reduces required compensation by `0.0352479960`. The corresponding break-even service flows are approximately `0.87768465` and `0.91969138`.

A positive-cost example makes the financing condition explicit: with charge and capacity `F=E=0.85`, carrying cost `C(E)=0.01`, and net service flow `b=0.90`, the adjusted mandate yields principal surplus approximately `0.0098659` at the minimum grant, whereas the unadjusted mandate yields `-0.0274839`. Both agent participation and the principal's acceptance test are imposed. This is a constructive example in the specified separate-account model, not a monetary willingness-to-pay estimate.

### Surrender and minimum-term reoptimization

The new stop action pays `G-F` at eligible interior rebalancing dates and has zero live continuation. The first interval remains compulsory, and forced boundary liquidation still pays `G`. All four classes are reoptimized at 19 central fee/term specifications and 20 additional fee/contract rows. The entire original action menu and frozen proposals remain in the target.

We reproduce the referee's free-surrender values and the all-state/action/date supersolution check. With surrender after the first interval, both regimes have the same class values and the relative option is zero at the center. The separate date-zero free-surrender contract has value `G(x0)`. These comparisons remain prominent in the main text and table, not hidden in a response appendix.

The revision goes beyond reproducing the two endpoints. At charge `0.70`, the relative adjustment option becomes **negative**, about `-0.00341186`, even though adjustment still improves each class value. The discounted surrender incidences differ across both classes and regimes. At charge `0.80`, opposite choices return at the center, but the original regional conclusion fails: at `(lambda,d)=(0,0.4)`, the no-adjustment difference is `+0.0013923796303`. Both the adverse corner and the failed regional certificate are retained. Free surrender after longer minimum terms also generates a nonmonotone relative option.

**Mechanism, not only a table:** for each fixed policy the value is base payoff plus operating benefit times discounted duration minus fee times discounted elective-surrender incidence. The value envelope implies `Delta_F=-(S_plus-S_minus)`. A four-class contrast need not preserve the sign of either regime's adjustment gain. Under binding class-specific participation, the relative adjustment option is exactly the difference in participation-compensation savings across the two position classes. These identities distinguish an adjustment technology's level value from its effect on the selected position.

### A finite-enforcement frontier that preserves the original region

**New result: `prop:r9_enforcement`.** On the all-action reachable support, the maximum of `G-V_n` over surrender-eligible continuation nodes is necessary and sufficient for *statewise* equality with the noncancellable problem. It is only sufficient for equality of the two initial values; we do not describe it as the smallest initial-sign-preserving fee. The threshold is nonincreasing in the minimum term and the operating benefit. Policy inclusion proves that adjustment weakly lowers the enforcement capacity required to implement continued operation.

A two-policy no-adjustment Bernstein lower bank produces a common sufficient frontier over the original rectangle `[0,0.25] x [0.4,0.45]`. With surrender available after one interval, the computed sufficient charge is `0.8348592806`, including the arithmetic allowance; the displayed sufficient value is rounded upward to `0.834860`. The frontier falls as the minimum term increases. Reachability reduces the sufficient one-interval bound from more than `2.53` over all grid nodes to less than `0.835` over the actual mandate's possible continuation states.

The original opposite-position region is separately certified for **every** fee in `[0.85,0.90]`, with both chord and count on the full operating menu plus surrender. The bounds, including `2e-7` padding per difference, are

- Adjusted difference: `[0.0000686948833572, 0.0003247296453481]`.
- No-adjustment difference: `[-0.0003696772643877, -0.0000528012509051]`.

Thus the original conclusion is implemented by a finite, priced enforcement capacity rather than only by formally prohibiting exit. This does not make the capacity restriction immaterial; the free and intermediate-charge failures show why its price matters. No replacement favorable law/benefit rectangle is substituted for the original one.

**Locations:** new main sections `sec:r9_contract` and `sec:r9_evidence`; tables `tab:r9_procurement`, `tab:r9_surrender`, `tab:r9_enforcement`, and `tab:r9_fee_certificate`; S.13; `replication/r9/output/surrender.json`, `reachable_fee.json`, `procurement.json`, and the three `*_certificate` deposits.

## R8-E2. Binding long and short permissions

### Actual optimizers and the economic target

The four initial optimizers now appear **beside the original decision-certificate table**, in `tab:r9_initial`, through the R9 copy of `05d_decision_evidence.tex`. They are `(0.8,0.2,0.8)` and `(0.8,0.2,-0.5)` with adjustment, and the same financial controls with deliberate adjustment zero in the other regime. Both investment permissions bind. We explicitly distinguish positive exposure from risk-taking itself and retain stochastic preference movement in the no-adjustment regime.

The added contracting section treats the long and short bounds as different initial permissions: a funded-purchase/liquidity-reserve permission and a stock-borrowing or collateral line. Their asymmetry is an explicit contractual restriction, not an estimate of a universal market limit or an unconstrained optimum. We retain the interior hedge formula with its original interior qualification and do not use it to characterize these boundary optimizers.

### An exact within-box diagnostic, not a denser scan

**New result: `prop:r9_knots`.** At the initial state, for risky share in `[-0.6,1]`, all first-step conditional arrivals remain strictly interior. Conditional on a consumption/adjustment pair, the preference interpolation weights do not depend on risky share and wealth arrivals are affine in it. The first-date payoff is consequently continuous and piecewise affine. Endpoints and wealth-node crossings exactly exhaust the financial maxima for each fixed pair.

The implementation has 121 common consumption/adjustment pairs and 2,689 candidate triples over that wider interval, plus the inherited feasible-proposal treatment. It reproduces the original finite-menu values at all nine inspected original contracts. It does **not** claim continuous optimization in consumption or deliberate adjustment, nor does it change later-date menus or the initial duration.

### Both permission boundaries and both benefit boundaries

At the original center and short permission `0.5`, the two long-permission switches are approximately `0.7890095` with adjustment and `0.8107837` without adjustment. Holding the long permission at `0.8`, the short-permission switches are approximately `0.5094806` and `0.4907037`. These paired boundaries explain why adding long share `0.82` or short share `-0.51` moves the original center out of the opposite-choice interval. Both adverse changes remain in the tables.

The corresponding center long-permission shadow values are about `0.0179009` and `0.0194114`; the short-permission values are `0.0200460` and `0.0225172`. They are derived from the interpolation-cell continuation slope and checked against finite differences, not inferred from an unconstrained mean-variance formula.

The operating-benefit roots are also reoptimized with continuation policies changing at **every** trial benefit. At `lambda=0.125`, the adjusted/no-adjustment crossing pair is approximately:

- Original permissions: `(0.339574, 0.515873)`.
- Long permission `0.82`: `(0.139861, 0.334568)`.
- Short permission `0.51`: `(0.429666, 0.597689)`.

Both regimes and all three law probabilities appear for each permission intervention. The duration and permission-price envelope formulas explain these movements. The roots are local floating-point brackets, not global uniqueness claims or directed-rounding interval enclosures. The separately certified original finite region retains its stronger uniform interpretation.

**Locations:** `subsec:r9_permissions`, `prop:r9_knots`, `eq:r9_permission_prices`, `eq:r9_frontier_derivatives`, `tab:r9_permissions`, `tab:r9_benefit_frontiers`, and S.13; `replication/r9/output/permissions.json` retains all nine permission comparisons and eighteen reoptimized benefit roots.

## The two presentation corrections

**Initial actions:** addressed beside the original certificate rather than only in an author response. Both risky positions and all active initial bounds are displayed.

**One target-error account:** the new `subsec:r9_certificate` and S.13 explicitly distinguish (i) the real-arithmetic mathematical settlement contract, (ii) the stored reward/kernel target, and (iii) another protocol or diffusion target. An explicit Bellman perturbation recursion prices reward, row-kernel, and terminal errors; class-difference transfer adds both class errors. The arithmetic audit is enlarged for the third policy feature, surrender incidence. Its derived per-class bound is about `1.431e-8`, below the accepted `1e-7` allowance. Selected-control reconstruction is not relabeled as an independent interval enclosure of the constructor. No uncomputed transition or diffusion error is assumed to vanish.

## Retained methodological contribution and adverse evidence

We retain the signed compression, count ordering, total policy-bank error, positive-duration estimand, common-cardinal-tilt theorem, and the cost-matched original decision contest. We also retain the successful mesh-only lower bank, the adverse reusable structural-solver comparison, the wealth-granularity failures, the large-cardinal-tilt example, recursive utility, temporal selves, and persistent capacity competition. No new network training, neural-necessity claim, external-verification-software benchmark, or universal solver ranking is introduced by R9.

The referee's one/two/four-cell rectangular comparison remains in the preserved review directory with its original component-only timing interpretation. We do not count it as a new matched end-to-end author benchmark. The earlier R8 dispositions F1--F6 remain credited rather than reopened indiscriminately.

## Validation, preservation, and scope

The new stop implementation is checked against 81 enumerated continuation policies per class/point in 12 random small models (120 class-point comparisons), and against 80 full-model class/parameter comparisons. Direct selected-control reconstruction, polynomial replay, convexity, action eligibility, and date-zero free exit are separately checked. These executions supplement the proofs; they do not prove a general theorem by sampling.

The source run verifies 398 protected historical/numerical entries. New sources live under `replication/r9` and this revision directory, plus the two new entry points. The current index is prepended while its historical content remains unchanged. All reviewed scientific sources, historical results, and review files remain at their original paths. Main and supplement use the repository's Econometric Society `econsocart` class and existing reference style.

The remaining target distinctions are explicit assumptions and error obligations, not purportedly completed constructor/diffusion enclosures. The numerical roots are not interval proofs. The contract is a specified procurement institution, not a globally optimal or empirically calibrated mechanism. These qualifications prevent a new claim from outrunning its proof; they do not replace the requested substantive economic response. The actual revision, full evidence, proofs, and reproducible build are provided for another independent advisory review.
