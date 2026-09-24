# R36 referee-response execution protocol

Date: 2026-09-24. Repository: TrillionniumFoundation/NBO.
Review baseline: a6b191b90ffa59c41bbf7be0ac9b3ed4707de738.
Reviewed manuscript: d0cfe1b17cc66cde393f4e2d1700270975bb7e30.
Parent retained without alteration: 39d160ec712c33c8ce965721c80055f1b94b4825, including the R35 protocol.
Destination: revision/econometrica-r36-certified-global-revision-2026-09-24 only.

## Unchanged primary target

Retain all 42 R34 configurations, the original maintenance primitives, the frozen installed policies, horizons 4, 8, and 12, and all-state/all-restart operating tolerances 0.01 and 0.05. Keep the deterministic Markov and randomized/history-conditioned policy classes distinct. A necessary-action deterministic cost bound is never a randomized lower bound. Operating preservation is checked separately and is not a hidden modification of the constrained optimum.

## Primary execution at this checkpoint

A fresh exact operating dynamic program, a necessary-action outer-class cost recursion, and separately evaluated feasible upper candidates have been executed for all 42 configurations. The lower and upper costs agree exactly in 24 cases, including 12 strictly positive-cost cases. All 14 horizon-four cases are exact. The remaining 18 cases retain their nonzero intervals. No claim of randomized global optimality follows from these deterministic equalities.

A separately implemented SymPy Rational row/partition verifier has checked the 42 proof objects. It imports no Fraction/PW constructor, affine-composition routine, or optimizing-envelope routine. It checks primitive Bellman equations and inequalities on open-cell endpoint limits and isolated points, actual transition pullbacks, necessary-action threshold crossings, terminal conditions, exact integrals, frozen-proposal hashes, and policy-class metadata. At this checkpoint all checks passed and all 15 declared corruption categories were rejected. This statement is confined to the primary objects; additional studies require their own recorded execution and verification.

## Additional referee-directed studies

Replace the eight-point local multiplier approximation with an exact three-action, one-constraint LP and adaptive whole-cell certificates. Use rational primal vertices and dual line intersections, and prove a whole-cell primal/dual gap by quadratic sign checks. The propagation theorem controls approximation to the continuous local restart relaxation, not the structural global duality gap. Compare tolerances 1/100, 1/200, and 1/400 and exact versus constructed operating witnesses on both horizon-four neural31001 configurations. Hold the local cost floor at zero in this diagnostic; do not mislabel it as a complete decomposition of the R34 nonzero support floor.

Economic sensitivities use eleven transparent one-at-a-time specifications, three condition/calendar installed rules, and two explicitly separate operating tolerances. Dynamic and pointwise revision must use identical action restrictions and their own transition occupancies. These are normalized economic examples, not an empirical dollar calibration or a random population sample. Retain all outcomes.

The nonlinear multistate extension is a distinct economic specification. Its discretization errors and tolerances must be reported explicitly; it cannot silently replace the unchanged primary cohort or establish a dimension-free rate. Retain unsuccessful certificates and record all exploratory amendments.

## Publication discipline

Preserve all prior branches, files, proofs, experiments, and reports. Provide a new Econometrica-format manuscript, full technical supplement, point-by-point response, computation report, source manifest, and lossless historical annex. Retain the original stopped consumption-portfolio program and distinguish any operator-level connection from a solution of that separate all-domain control problem.

Only actual executed numerical results and actual completed builds may be reported as passing. Record the precise remote publication commit and verify it after pushing. Do not force-push or modify main, review, R35, or other revision branches.
