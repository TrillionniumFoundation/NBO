# R24 prospective protocol: state, geometry, and numerical efficiency

2026-09-23. This protocol is committed after reading both R23 reports and inspecting the complete R23 source and frozen outputs, but before executing any R24 scientific run. A single inherited-policy checker smoke test is not an R24 outcome. This is a new design motivated by known R23 findings, not retrospective preregistration of R23.

## Frozen scientific object

Repository: TrillionniumFoundation/NBO. Reviewed manuscript: c09835c92042cb881d0bbdd3cab99b98d0a9d225. Latest second-pass review: fdc60e04d6aca33ad964da77db69c8ba3621a14b, reviews/2026-09-23-econometrica-r23-second-pass/referee_report.md. First-pass report: fafff2ccfa218b5de4ea73a4d0eb21d468166c98. The new branch descends from the second-pass review, preserving the reviewed manuscript. The original economy, original current-state problem, and full-domain regret target 0.01 remain unchanged. No local or auxiliary-model result substitutes for that target.

## Method and geometry

Use the inherited 1-16-16-3 tanh network and 16 slabs. Let Q be an orthonormal 48-by-47 chart orthogonal to the common-intercept gauge. At the matched initial network compute the actual output Jacobian J and G=Q'JJ'Q. The four direct Adam charts are identity, diagonal square root of G, regularized square root of G (tangent metric), and regularized inverse square root of G (whitening). Regularize eigenvalues relative to the largest by 1e-5, and normalize each coordinate matrix to squared Frobenius norm 47. All direct charts have the same complete financed output family; preprocessing time is charged separately. Diagnose the actual Jacobian spectrum, Adam output metric, and first-order output-update remainder. Momentum transport is explicit; do not equate Adam's momentum update to a current-gradient metric step.

The proposal objective uses Gauss-Legendre time and Gauss-Hermite shock integration, the inherited implicit financing root, and bounded preference clipping outside [1.2,2.8]. The clipping supplies a well-defined auxiliary objective on Gaussian tails; it is not a replacement of the original stopped model. The original directed stopped-policy checker remains unchanged. Ordinary gradient-refinement differences are diagnostics, not rigorous gradient-error bounds.

## Disjoint tuning

Tuning seeds 24001 and 24002, initial state (2,1.25), quadrature orders (8,16), and 200 objective/gradient calls. For each of neural, direct, diagonal, tangent, and whitened Adam, test learning rates 0.005, 0.02, 0.08. Select the rate maximizing the mean independently certified final payoff lower bound across the two tuning seeds; an infeasible result scores negative infinity. Ties within 1e-10 use the smaller rate. Retain every result. Each arm receives six 200-call trials; this is equal tuning-call allocation, not equal wall-clock cost. Charge the actual preprocessing, generation, and verification costs.

## Held-out central factorial and anytime records

Seeds 24101 and 24102, state (2,1.25), proposal orders (8,16) and (12,24), all five selected Adam methods and neural/direct L-BFGS-B. L-BFGS-B uses maxls=40, ftol=1e-13, gtol=1e-8. Cap each trajectory at 400 objective/gradient calls. Freeze policies at calls 25, 50, 100, 200, 400. For line-search methods use the latest accepted iterate whose call index does not exceed the checkpoint; if converged, explicitly label carried-forward endpoints and actual calls. Certify every checkpoint with the unchanged checker. Deployment accepts only a candidate lower payoff bound strictly above the incumbent upper bound. The underlying proposal trajectory is not falsely described as rollback-coupled: checkpoint acceptance determines deployment, not the proposal gradient path. Report all acceptance and rejection decisions, including unchanged converged candidates, without claiming they demonstrate a convergence benefit.

At every checkpoint evaluate common raw-output gradients at both proposal orders. These are fixed-policy discretization diagnostics. Record financing offset/derivative diagnostics, Jacobian singular values, and Adam-induced metric eigenvalues where applicable. Show accuracy against calls, generation seconds, generation plus checking, and total including the unamortized inherited dual cost of 415.789 seconds. No runtime comparison to historical machines is treated as a controlled timing experiment.

## External state-coverage dimension

At seed 24300+i for lexicographically ordered vertices, run a 3-by-3 grid: u in {1.98,2,2.02}, x in {1.24,1.255,1.27}. This gives nine genuinely distinct experts and four cells over a region 50 percent wider in wealth than R23. Use neural Adam, direct Adam, tangent Adam, and direct L-BFGS-B; the selected tuning rates, (8,16) proposal rule and 400-call cap are fixed. Certify every endpoint. Apply the retained common-shock concavity/exit correction and convex-dual theorem cellwise; charge all nine expert checks, not duplicated-expert latency. A failed vertex leaves that cell uncertified rather than silently removing it. This is a low-dimensional multicell study, not evidence of high-dimensional scaling.

## Mechanism and reference diagnostics

Revisit the frozen seed-23203 neural L-BFGS-B failure. Retain the original run, regenerate the baseline, and test an equivalent parameter chart with layer-group powers-of-two scales (1/4,1,4), a tighter-tolerance restart, and direct optimization from the failed output array. Report trajectories, gradients, output distances, and conditioning. These are explicitly post-hoc failure diagnostics, not held-out method selection.

Include a separately named deterministic consumption-saving reference economy: T=1, r=rho=0, u=2 fixed, no risky asset or preference adjustment, running utility -1/c, terminal utility log R, wealth 1.25, and c in [0.05,0.8]. Its optimum is constant c solving c+c^2=1.25 with R=c^2>0.5. The 16-slab neural/direct machinery contains that optimizer. Directed arithmetic encloses its exact reference payoff and every candidate payoff, separating solver error from checker width; temporal quadrature and policy-class approximation errors are zero. This is not a solution of the original stochastic economy.

## Publication and integrity

State the augmented-state Bellman problem and its relation to the original value explicitly, preserving the distinction from a successful current-state policy on (t,u,x). Prove the Jacobian/momentum transport and financing-gradient perturbation results with hypotheses, not with numerical assertions. Keep all R23 mathematics, prose, adverse outcomes and historical developments in the new manuscript or its preserved appendix/supplement. Correct the stale full-state summary name through a new versioned canonical record without editing frozen historical evidence. Supply a transitive source/data lock, full ledger, point-by-point response to both reports, and a machine-readable finding disposition. Compile ECTA_R24, SUPP_R24 and RESPONSE_R24 using the retained Econometrica class. Publish only new R24 revision branches. All failed configurations and build attempts remain visible. Do not assert full closure, neural dominance, rigorous gradient-error numbers, or successful nonreplicable/full-state execution unless the delivered evidence proves them.
