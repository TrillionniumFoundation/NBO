# NBO R73 — original-paper revision and prospective qualification design

Controlling advisory report: R67, review commit
`4b27b56f4514f6c1d77b69fe707f7202f8b06b19`, dated 11 October 2026.
Original manuscript development base: R72 source commit
`5611b32978a2df5f32bff796f7dd209105cf28b0`, retaining completed R70
`b576584cb5b1ff5ceccbcf37a3fa6e1ac613aca6` and the frozen R69 scientific catalogue.
No historical review or revision branch is modified.

## Fixed scientific design, committed before its four services run

The original scalar-control, two-state nonlinear investment model, price one,
horizon two, common opposite-signed uniform innovation on [-1/32,1/32], original
capacity, stage costs and terminal payoff are unchanged. There are four complete
backward constructions: covers with 8 or 16 midpoint cells per coordinate,
crossed with an additive shallow ReLU or degree-four Bernstein basis. Both have
nine readout coefficients (including a constant), each bounded by eight.

At each date the future is the continuation actually constructed at the next
date. Exact conditional moments evaluate all 33 equally spaced feasible actions
at each midpoint. The continuous-action lower cover subtracts its proven action
modulus times the exact fill radius; no convexity of a fitted critic is assumed.
Another 33 proposals per midpoint are downward quantized at 1/4096 and feasible
throughout its closed observation cell. The selected acquired policy and the
zero-action comparison receive uniform greedy-gap bounds. Fitting, integration,
covering, robust action selection, record writing and all ablations are charged.

The qualification readout minimizes the proved residual-oscillation LP.
Coefficient and dual probability proposals are rationalized at 28 bits and
checked exactly. The predeclared optimization-gap tolerance is 1/65536.
A bounded least-squares readout uses the identical features and identical fixed
future labels as an objective ablation at each stage; it does not create a
separately propagated least-squares controller. Solver messages and failure
statuses are retained. There is one complete service per design point and no
selection or retuning after viewing the catalogue. A source freeze must be
committed and verified before any of the four services executes.

The independent checker recomputes all final-date action values from the retained
original rational primitive. For the fitted future it uses exact integration by
piecewise-affine segmentation (ReLU) or the positive five-point Boole rule
(Bernstein), not the production moment expansion. It recomputes every nodal
lower cover, robust selected action, global residual range, greedy-gap allowance,
primal/dual value and accumulated original-optimum bound. No scientific service
clock is overwritten by the checker.

## Inference and claim boundaries

These four constructions add qualified NBO continuations, not independent policy
cost observations. The new anytime theorem is checked with exact finite-model
regressions, including the entire 4,096-leaf adaptive diagnostic tree; that tree
is not a replacement investment experiment. No historical fixed-sample interval
is retroactively advertised as an anytime interval. A fixed controller/reset
contract and a varying-controller conditional average are different estimands.
Failed numerical episodes retain their predictable full support and paid work.

The proposed readout theorem concerns a fixed feature class conditional on its
actual fixed future. Its objective bound does not imply joint optimality over
all dates, unrestricted hidden-layer training success, or uniform neural speed.
The new residual qualification uses an explicitly paid tensor cover. R70's
non-tensor action verifier and R72's witness cache remain available and distinct.

## Manuscript and release

Retain every R72 section and prior mathematical statement exactly once in the
main article, Technical Supplement or Numerical and Development Appendix.
The preceding optimal-advantage centering section may move intact to the
supplement so the main article can present fitted-continuation qualification
and sequential cost certification. Preserve the original title, author,
primitives, constructive backend, broader historical applications and all adverse
comparisons. Record the content map and byte identities.

Run all inherited suites and new exact tests; retain all R72 scientific records.
The clean archive must include the full transitive Python import closure,
including R62/inputs/revisions/2026-10-08-r49/code/service49.py. Rebuild all current
PDFs and derived tables without scientific reruns. Do not create the review-ready
ref until the mathematical/numerical checks, complete archive rebuild, actual
visual inspection and final manifest have succeeded.
