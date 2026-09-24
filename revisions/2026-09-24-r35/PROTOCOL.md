# R35 execution and interpretation protocol

Date: 2026-09-24. Repository: TrillionniumFoundation/NBO.
Review baseline: a6b191b90ffa59c41bbf7be0ac9b3ed4707de738, including reviews/2026-09-24-econometrica-r34/referee_report.md.
Reviewed manuscript parent: d0cfe1b17cc66cde393f4e2d1700270975bb7e30.
Destination: revision/econometrica-r35-global-exactness-2026-09-24 only.

## Scientific target

Retain the R34 maintenance primitives, 42 installed-policy configurations, all-state/all-restart operating constraints, and tolerances 0.01 and 0.05. Distinguish the deterministic Markov minimum from the randomized minimum explicitly. A necessary-action cost lower bound is a deterministic-policy bound; it must NEVER be reported as a randomized lower bound. Preserve the R34 randomized support/restart bounds as a separate comparison. A feasible backward continuation is an upper-bound generator, not automatically a globally optimal policy.

Construct the exact operating value from the model and charge its computation. Form the necessary deterministic action set V_t - T^a V_{t+1} <= epsilon, solve its cost Bellman recursion, and independently verify both this lower bound and each deployed policy's operating/cost equations. Declare exact deterministic optimality only when exact integrated lower and feasible upper costs agree. Keep every remaining positive interval.

## Completed primary execution at this checkpoint

The full 42-case exact construction and a separate SymPy Rational row/partition verifier have been executed locally. The verifier imports no constructor, composition, or optimizing-envelope module. It checks isolated points, open-cell endpoint limits, action eligibility crossings, terminal conditions, Bellman inequalities, exact integrals, and policy-class metadata. The verified counts are 24 exact deterministic global optima, of which 12 have positive cost. Ten mutation categories are rejected. This checkpoint is not a claim that the remaining 18 positive-cost cases or the randomized problem have been solved.

Frozen R34 installed policies are reused. Neural training is not re-executed or described as new. Upper candidates use penalties 0, 1, 4, and 16 as computational selection parameters, plus the retained feasible R34 candidate and the necessary-class selector when independently feasible. These penalties are not calibrated intervention prices and do not justify any lower-bound convergence claim.

## Multiplier correction

Solve the three-action, one-inequality randomized local relaxation exactly by primal vertices and dual line intersections. Its exact statewise frontier can be rational rather than piecewise affine. Adaptive open-cell refinement is accepted only after exact quadratic inequalities prove a primal-upper/fixed-dual-lower gap. Isolated knots use the exact point LP. The resulting convergence theorem concerns the continuous local restart RELAXATION, not global strong duality. The declared local tolerances are 1/100, 1/200, and 1/400; numerical sensitivity uses the two T=4 neural31001 cases. The unchanged R34 support floor is used across witness versus exact-V diagnostics, so this comparison does not purport to isolate the support floor's witness error.

## Economic sensitivities

Report all 66 configurations: eleven one-at-a-time primitive specifications, three economically interpretable threshold/calendar installed rules, two tolerances (0.05 and 0.20), horizon eight. Compare dynamic and pointwise revision within exactly the same sufficient action class. Vary discounting, revision weights, initial density, maintenance cost, and defer persistence. These are normalized illustrative economics, not an empirical dollar calibration or random-sample frequency estimate.

## Nonlinear two-state extension and research chronology

Use a separate two-component maintenance economy on [0,1]^2 with bilinear action-dependent transitions, four actions, two shocks, and whole-box directed integer enclosures. The final product experiment has horizons 4, 8, 16, 32; meshes 16, 32, 64, 128, 256 per dimension; and upper generators with penalties zero and four. Its operating tolerance is 0.5 and is NOT substituted for either tolerance of the unchanged primary cohort. Keep failed box certificates and nonzero revision intervals in the same result set.

This is referee-informed exploratory research. An initial zero-penalty pilot on meshes through 128 failed its operating certificate in all sixteen configurations. That pilot is retained. The operating-priority generator and mesh 256 are transparent amendments, not retrospectively preregistered successes. The nonlinear constructor uses outward integer arithmetic; the separate SymPy verifier's headline 42-object coverage is for the primary one-dimensional cohort, not silently extended to the two-dimensional arrays.

## Publication and preservation

Preserve all prior branches, files, proofs, unsuccessful experiments, and referee reports. The focused new article is accompanied by a full technical supplement, point-by-point response, computation report, preservation map, and lossless historical PDF annex. The original stopped consumption-portfolio target is retained unchanged; no maintenance result is represented as solving that distinct current-state problem.

The final publication must include executed results, source hashes, build checks, and exact remote provenance. A proposed workflow or unexecuted test is not a passing test. Only this new revision branch may receive publication commits; no force-push or modification of main/review/other revision branches is authorized by this protocol.
