# Response to the R3 referee report: Neural Bellman Operators

Review input: `reviews/2026-09-16-econometrica-r3/referee_report.md` at `79a7d84be2cbbf9bd5d181599ee110540128e3b5`.

Revision branch: `revision/econometrica-r4-stochastic-operator-2026-09-21`.

The authoritative manuscript is now `ECTA_R4.tex`, with main text and complete technical appendices under this revision's `paper/` directory. The prior manuscript, supplement, reports, derivations and embedded arrays remain unchanged. This response addresses the commissioned repository report; it does not represent an editorial decision or invitation from Econometrica.

The revision adds actual computations and substantive arguments rather than replacing the economic program with a list of qualifications. Its main additions are a boundary-aware continuous-time policy-value bound, a directly computable finite-operator counterpart, a repaired exact policy-iteration argument, and a global comparative-static theorem for preference adjustment. The numerical record contains trained policies, independent policy evaluation, active preference adjustment, corrected stochastic transitions, and explicit equilibrium calculations. The remaining unexecuted generalizations are identified below so that an implemented correction is not confused with evidence for a broader claim.

## F1. An executable neural method and actual author runs

**Change.** `replication/merton.py` performs separated continuous-HJB updates with automatic first and second wealth derivatives. The critic has a trained homothetic amplitude; the actor has two trained logits. Analytical controls and value are audit targets, never training labels. `replication/solver.py` supplies a nonlinear, two-hidden-layer, width-48 tanh actor and critic for the stochastic NDU finite operator. Every next-date critic is frozen; the actor is improved against that neural continuation; the current critic evaluates the enacted hard actor. An independent NumPy solver re-evaluates the resulting policy and exhaustively solves the same finite economy.

**Evidence.** Seeds 0, 1 and 2 have maximum date-zero NDU policy value losses .01129065, .02352608 and .01279688. All meet the declared .05 finite-model target. The failed initial pilot and two incomplete twelve-date attempts are retained in `results/summary.json`, not counted as successes. Successful checkpoints, raw arrays and training logs are in the accompanying review bundle; the repository contains their generating code and executed metric record. Three Merton runs recover the optimal consumption ratio and portfolio with independently evaluated value losses below 4.70e-9.

**Location and scope.** Main sections `sec:method` and `sec:results`; Appendix `app:repro`. The NDU network is trained on all interior lattice nodes, not an unexecuted mesh-free sampling protocol. The Merton model is a three-parameter homothetic neural benchmark, not a deep-network scalability result. A nonlinear high-dimensional continuous-HJB training result has not been substituted for either experiment.

## F2. The NDU generator must contain the stated diffusion

**Change.** The stochastic transition includes preference diffusion, portfolio-dependent wealth diffusion and the negative cross covariance. Four correlated equiprobable branches replace the deterministic rounded transition. Both NumPy and PyTorch implement the operator independently.

**Evidence.** `audits.py generator` evaluates the generators of `1,u,X,u^2,X^2,uX`, their drift and covariance, at four time steps. The covariance discrepancy is below 1e-12 and NumPy/PyTorch Bellman values agree within 7.11e-15 in the audited float64 test. The mixed generator includes the covariance term rather than inferring it from a parameter label.

**Location and scope.** Equation `eq:ndu-hjb`, transition `eq:quadrature`, Appendix `app:ndu`. These are local consistency tests. Positive interpolation, time discretization and first-passage treatment still require their own convergence analysis; they are not certified by matching a covariance matrix.

## F3. The rectangle and clipping do not define the claimed viable economy

**Change.** We retain the original interior diffusion, compact control box, flow normalization and terminal payoff, but specify an explicit first-exit liquidation contract: `g(t,u,X)=G(u,X)-F(1-t)`, with baseline `F=8`. The process terminates at settlement. The code finds the first straight-segment boundary intersection in its killed-Euler approximation; it does not replenish wealth and then allow more consumption. The manuscript states plainly that liquidation is different from reflection and different from the previously asserted state-constraint interpretation.

**Evidence.** An exit regression starts at wealth .51 with consumption .8 and zero portfolio, reaches .5 at a fraction .0506457331 of the proposed step, and terminates. Re-solved fee-6 and fee-10 contracts and exit probabilities are reported separately.

**Location and scope.** Main subsection "The liquidation contract" and Appendix `app:ndu`. The fee is a declared economic primitive, not an empirically calibrated estimate. It is not portrayed as a harmless numerical projection. The theorem on adjustment costs keeps the settlement contract fixed when varying the adjustment price.

## F4. Preference adjustment, complete policy errors and re-solved costs

**Change.** Bilinear continuation replaces nearest-neighbor rounding, so preference actions are not locked to zero by the relative grid/time spacing. All three controls are compared with the finite optimum. Feasible Bellman improvement and policy-coordinate distance have different metric names. The model is re-solved independently for `k=.5,2,8` and for the restricted policy set `theta=0`.

**Economic result.** Theorem `thm:cost` proves that `V(k)=sup_pi[A(pi)-kB(pi)]` is convex and nonincreasing, and any optimal discounted adjustment budgets obey `B(k2)<=B(k1)` for `k2>k1`. At differentiability points, `V'(k)=-B(pi_k)`. This is a global revealed-preference argument, not a sign inference from `theta=V_u/k`.

**Evidence.** Central budgets are .01651962, .01192052 and .00230932. Allowing preference adjustment improves central value by .06447963, .04329315 and .01158166. Budget/value monotonicity and dominance over zero adjustment are tested at all finite states and dates. The nonzero-action share averages over all decision dates and interior nodes. Seed-0 portfolio policy discrepancy remains as large as .975 on the full lattice; it is not hidden by the much smaller value regret. Separate time, state and action refinements show material value differences, which are retained rather than relabeled continuum error bounds.

## F5. Sophisticated-self evaluation and improvement

**Change.** Equation `eq:selves` uses the ordinary discount factor in policy evaluation and the additional present-bias factor only in the acting self's improvement. The same recursion is used by the executed diagnostic and the appendix derivation.

**Evidence.** At `beta=.7`, the two-decision-date log model gives initial consumption share `1/(1+2 beta)=5/12`, rather than the geometric-beta value `1/(1+beta+beta^2)`. The evaluation-equation discrepancy is below 8.89e-16. A dense feasible deviation search is explicitly labeled a lower bound; strict concavity and the analytical first-order condition establish global optimality for this particular example. The beta-one check is retained but is not used as evidence against an error that disappears at beta one.

## F6. Squaring the mean trace versus averaging squared residuals

**Change.** The current experiment evaluates `(a-mean(q)/2)^2`, not `mean((a-q/2)^2)`. Appendix `app:trace` proves the Gaussian variance identity and also gives an unbiased cross-probe U-statistic, with its finite-sample qualifications.

**Evidence.** For the report's matrix, the expected objective is `1+7.5/K`. At `K=1,2,8,64`, 30,000 batches produce means 8.5149621, 4.8227717, 1.9308789 and 1.1136903. All are within five reported Monte Carlo standard errors of their respective expectations. The wrong estimand and the U-statistic are recorded separately. No probe-count timing is treated as a complexity theorem.

## F7. Actor stationarity is not global improvement

**Change.** The false implication from isolated actor stationary points to policy-iteration fixed points has been replaced by its actual missing condition. The action-level supporting-hyperplane gap bounds regret for a differentiable concave Hamiltonian on a convex compact set. The NDU constrained selector handles concave slices, nonpositive wealth derivatives and nonconcave/zero-curvature portfolio slices explicitly. The finite implementation enumerates its entire declared action set.

**Evidence.** The stable suboptimal stationary point of `H(a)=-(a^2-1)^2+.2a` has computed global gap .3998745872. It appears in the main text and the regression suite. The two-timescale appendix states an invariant-set conclusion with its hypotheses; it does not identify finite-step Adam with that asymptotic algorithm, or shared-parameter stationarity with pointwise action optimality.

## F8. The exact-iteration limit and the neural-to-value bridge

**Change.** Proposition `prop:exact` and its full proof identify the common monotone value limit, then establish `E(p)=E(I(p))` along the shifted subsequence. They do not equate limiting policies merely because successive values agree. The topology includes the time derivative and spatial derivatives needed to pass the evaluation equation to the limit.

**New quantitative results.** Theorem `thm:continuous` proves `V*-J^pi <= 2b+C_rho(T-t)(2 epsilon+eta)` under explicit stopped-process, integrability, boundary and uniform-residual hypotheses. Theorem `thm:finite` proves the backward finite-operator counterpart. Independent exact finite-policy evaluation eliminates the critic defect from the latter certificate. The proof also states how a separately verified numerical-economy error could be added.

**Evidence and boundary.** The NDU gain-based finite upper bounds are .2593311, .2644908 and .5205032 and dominate the measured initial value losses. They are conservative. The boundary-switched finite critic is not passed off as a globally C2 test function, and an L2 loss or sampled residual is not passed off as a uniform continuum bound. The continuum NDU error remains unmeasured.

## F9. Coupled dynamic scalability rather than a static quadratic program

**Change.** We add an eight-date stochastic LQ model at dimensions 4, 8 and 16, with off-diagonal state dynamics, nonseparable state cost and correlated shocks. A trained linear actor is improved against a frozen quadratic policy evaluator and compared with an independent Riccati recursion. The stochastic continuation constant is retained.

**Evidence.** Maximum held-out value discrepancies are 6.59e-14, 1.54e-14 and 3.32e-14. Reference and actor times are separately recorded; Riccati is faster. The known quadratic family is acknowledged as favorable. The static R3 calculation remains in the archive, not recast as a dynamic solve.

**Remaining evidence.** This closes the static-versus-dynamic mismatch for the new regression, but it does not complete a constrained nonlinear high-dimensional, matched adaptive-sparse-grid comparison. No such performance result or general complexity theorem is claimed to have been executed.

## F10. Extension evidence and non-fabricated zero errors

**Change.** Merton now has actual neural updates and independent evaluation. The recursive extension adds a finite-horizon implicit Epstein-Zin saving calculation, with an executed sign transform and a checked implicit equation. The game extension includes both an automatic-differentiation rival-detachment test and a genuinely dynamic three-date finite capacity game.

**Evidence.** The recursive implicit-equation residual is 2.46e-13 or less, minimum `bV` is .0625, and the terminal transform error is below 8.89e-16. The finite game's exhaustive one-shot deviation maximum is computed as zero; three state-date problems have multiple pure equilibria, and the lexicographic selection rule and full profile are preserved in the raw bundle. Neural recursive-portfolio error and neural dynamic-MPE error are null with reasons, not fabricated zeros.

**Remaining evidence.** The finite recursive reference is not a trained nonlinear recursive portfolio solver. The finite game is not a trained high-dimensional MPE or a competitive-limit calculation. Their model formulations and technical requirements remain in the manuscript and appendices.

## F11. Closest literature, semilinearity and differentiation costs

**Change.** The introduction discusses neural policy iteration, Hamilton-Jacobi deep operator iteration, martingale control learning, direct policy approximation and continuous-time policy improvement. Primary preprints by Kim et al., Lee and Kim, Cai et al., Han and E, and Jacka and Mijatovic are cited with identifiable versions or identifiers. The motivating Qi manuscript's bibliographic identity was checked against the retained repository source.

**Positioning.** The manuscript identifies its specific boundary-aware error decomposition and preference-adjustment result without claiming that neural policy iteration, operator factorization or avoiding a closed-form optimizer is new by itself. It defines semilinearity through highest-order derivative dependence and does not call every BSDE a Pontryagin adjoint equation. Exact trace contraction is discussed in terms of diffusion directions, network derivative cost and accuracy, without a universal dimension-50 or dimension-100 crossover.

## F12. Reachable provenance, defined metrics, failures and builds

**Change.** The declared review base is reachable: `79a7d84be2cbbf9bd5d181599ee110540128e3b5`. Executed source bytes are identified by SHA-256 and by reachable source commits on this new branch. The base commit is explicitly a historical parent, not a claim that it already contained the newly written scripts. Execution completion and tolerance attainment are separate fields. Scientific payload hashing excludes wall-clock metadata. Full policy vectors, exact estimand names, null reasons and unfavorable refinements are retained.

**Delivery.** `README_R4.md`, the retention map, manifest, source scripts and `results/summary.json` identify the review package. The attached bundle additionally contains trained NDU weights, raw arrays, training histories, the failed pilot's exact source and binary checkpoint, and complete game profiles. Those binaries are not represented as already committed to GitHub. The source scripts regenerate them.

**Build status.** The canonical entry uses the repository's Econometric Society `econsocart` class. A separate standard-class reading copy of the full text and appendix has been compiled and visually inspected. This is not claimed to be a verified canonical Econometrica-class build. The remote export workflow was queued at the last check; its status is not evidence of a passed build or test.

## What is ready for the next review

The revised mathematical arguments, explicit economic boundary contract, implemented stochastic operators, actual neural experiments, independently evaluated finite-model policy losses and adjustment-cost theorem can now be assessed directly. The remaining continuum approximation error, broad nonlinear scaling comparisons, neural recursive-portfolio/MPE experiments and canonical class build are stated as outstanding validation, not silently set to zero. The revision preserves the economic program and the historical record while providing new proofs and executed evidence for its current claims.
