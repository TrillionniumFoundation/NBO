# R10 referee entry point — Neural Bellman Operators

**Canonical branch:** `revision/econometrica-r10-referee-resolution-2026-09-22`.

This is a substantive manuscript revision based on the completed R9 delivery, not a protocol-only update. Read **`ECTA_R10.pdf`**, **`SUPP_R10.pdf`**, and **`revisions/2026-09-22-r10/response_to_referee.md`** together. The final immutable source, execution-result, manuscript-build, and review-input identities are recorded separately in `revisions/2026-09-22-r10/publication_receipt.json`.

## Review input and baseline

The input report is `reviews/2026-09-22-econometrica-r9-numerical-methods/referee_report.md` on `review/econometrica-r9-numerical-methods-2026-09-22-46aef70`, pinned at **`251ad29668788b2a911c4ca6f9c0a226886518d6`**. It reviewed the early R9 source **`46aef70a24f74cf57503018a7e7f21cb46af08e3`**. R10 begins from the subsequently completed R9 delivery **`23f40e730fcea04efe3d84690d4f0fff5ae466e8`**. The response distinguishes what that intervening delivery supplied from what is new in R10.

## New numerical and mathematical result

The **original continuous stopped economy** now has central-state regret upper bounds below **0.01** at all three declared costs:

| Adjustment cost | Certified regret upper, rounded outward |
|---|---:|
| 0.5 | 0.00987440 |
| 2 | 0.00971727 |
| 8 | 0.00996896 |

These are bounds on the deployed feasible policies relative to the **full original adaptive continuous-action optimum**, not policy-evaluation widths, finite-grid residuals, or Monte Carlo estimates. The policies are explicitly polished neural time-control outputs. All old policies and their bounds remain unchanged in the historical files.

The new affine-preference market-deflator theorem includes the original noise correlation, an adapted conditional-coefficient variance allowance, global supporting-source inequalities, exact first-exit localization, and outward quadrature. A separate proposition turns feasible implementation output errors into an additive original-payoff regret allowance.

At cost two, optimal access welfare lies in **[0.04096859, 0.05973218]**. Raising cost from two to eight lowers optimal welfare by **[0.02318257, 0.04286880]**. Both effects exceed their corresponding interval widths. Optimal expenditure is bounded by a valid secant interval, not identified with an approximate policy's precisely evaluated budget.

## Evidence boundaries

The full 72-pair frozen R9 holdout remains primary external comparative evidence. Inconclusive d=16 sign tests and the stronger independently specified feedback baseline are retained. R10 does not claim that an expanded method-specific external tuning study has been executed, or that the two external training budgets establish matched-accuracy dominance. Its new time-to-tolerance table measures **verification work**, with the excluded fitting and training stages stated explicitly.

## Reproduction and preservation

See `revisions/2026-09-22-r10/replication/README.md`. The pipeline independently re-executes all three new original-model certificates from frozen deployment inputs. A collector running even after matrix failure preserves successful outputs, failed-cell status, and missing-cell metadata in a versioned result commit before marking an incomplete aggregate invalid.

`SUPP_R10.pdf` preserves the entire completed R9 paper and its complete supplement. The earlier fitted construction is also retained, explicitly dated, in the R10 mathematical appendix. All **948** inherited files are hash-checked, with only the root revision index relocated to its archived pre-R10 copy. No primary, review, or preceding revision branch is advanced by this delivery.
