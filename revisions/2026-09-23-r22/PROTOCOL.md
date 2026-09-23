# R22 prospective execution protocol

Date: 2026-09-23. Parent review: fc16c4fb27b54e11c67ce1983b6830a39038f063, reviews/2026-09-23-econometrica-r21-final/referee_report.md. This protocol is committed before the new R22 executions. R20/R21 results remain frozen and are not relabeled.

## Crossed representation and optimizer design

Use the unchanged R20 original-economy proposal objective, 16 slabs, and directed stochastic-policy checker. Factors: original 1-16-16-3 tanh Actor versus direct 16-by-3 coefficients; Adam (learning rate 0.005) versus SciPy L-BFGS-B (maxls 40, ftol 1e-13, gtol 1e-8). Three independent ensembles use base seeds 22000, 22100, 22200. Vertex v uses base_seed+v, so corners are independently initialized. Vertices in lexicographic order: (1.98,1.24), (1.98,1.26), (2.02,1.24), (2.02,1.26).

Within a seed/vertex block, initialize the direct coefficients to the exact binary64 raw outputs of the initialized neural Actor at all 16 slab nodes. Both optimizers use the same initial Actor state or mapped coefficient state. Verify equality of delivered initial b, s, theta vectors, not merely equality of random-seed labels. The total gradient-call cap is 400 per configuration. L-BFGS-B can stop earlier at its declared tolerances; on budget exhaustion retain the last accepted optimizer iterate, not an unevaluated or unaccepted line-search point. Retain initial and final policies, neural or direct parameter states, counts, and certificates. Compare final policies with initial policy-specific payoff intervals; an unverified or non-improving proposal is not silently substituted for the incumbent. Record function/gradient calls, accepted optimizer iterations, line-search evaluations, reporting forwards, checker calls, generation/checking times, and parameter dimension separately.

Primary endpoint: certified final policy payoff and regret at each vertex, with all four factor cells reported. Secondary a posteriori endpoints: general-initialization continuum bounds, true policy improvement where interval separation proves it, and conditional accuracy/work frontiers. No claim of neural advantage is prescribed; unfavorable outcomes must be retained. This protocol is not a preregistration of a global full-state accuracy success.

## Active acceptance-gate stress test

Use the original Actor at the first vertex, seed 22300, Adam learning rate 0.5, eight successive blocks of 25 gradient calls, checking after every block. Accept only if the proposed lower payoff endpoint exceeds the incumbent upper endpoint. A failed feasibility check is a rejection, not missing data. Restore the entire network, optimizer, and RNG state after rejection; record state hashes before proposal and after restoration. Supplement with explicit no-op and degraded-incumbent fault-injection regression tests, clearly distinguished from optimization outcomes. Report all checks and rejection costs. Do not infer broad optimizer robustness from this stress test.

## Proof and implementation audits

Derive an initial-mixture Jensen bound valid for unequal slopes and preference drifts, paying for factor and preference tails explicitly. Report its value for every independently initialized ensemble without assuming a positive improvement result. Provide state-domain coverage and online complexity accounting, a proof-to-code dependency table, and an explicit status for full-state and global-witness objectives. The original all-domain 0.01 objective, adverse direct baselines, model, and substantive historical arguments are retained.

## Delivery

All new material belongs to revision/econometrica-r22-crossed-certification-2026-09-23. Preserve main, prior review branches, and prior scientific files. Materialize editable ECTA_R22, SUPP_R22, RESPONSE_R22 sources, compiled PDFs, code, results, and an item-by-item response. Do not claim an unexecuted workflow or an unproved gate is closed.
