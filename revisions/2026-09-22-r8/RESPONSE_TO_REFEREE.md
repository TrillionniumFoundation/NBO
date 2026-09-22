# Response to the referee: Neural Bellman Operators, Revision R8

**Review answered:** `reviews/2026-09-21-econometrica-r5/referee_report.md`, review commit `69991122b2c3fcd26ce9d695da2e1c5f4eb89eb7`.

**Revision branch:** `revision/econometrica-r8-verified-manuscript-2026-09-22`.

**Inherited source:** `b6bb2e901211cff029a3d602901e00b3b0af90fe`. The R6/R7 protocols and all earlier sources remain intact. R8 is a complete new plaintext manuscript, not a reconstruction of the incomplete R5 transport fragments.

**Canonical files:** `ECTA_R8.tex`, `SUPP_R8.tex`, and this response. New full proofs are in `revisions/2026-09-22-r8/paper/proofs.tex`. All current numerical tables are generated from committed executed records, not manually transcribed results.

We thank the referee for distinguishing improvements in implementation from the scientific requirements of a numerical method. The revision responds with new mathematical results, a materially less intrusive finite safeguard, all-state continuous verification of a trained actor on the original control/exit geometry, and a complete paired comparison against a pinned author implementation on coupled nonconvex controls. We retain the economic model, recursive preferences, temporal selves, dynamic games, counterexamples, historical results, and failed attempts. We also distinguish what is now proved or executed from the precision and scaling questions that the available evidence does not settle.

## R5-F1. The finite candidate certificate and the continuous control problem

**Changes.** The main paper now proves a one-sided continuous verification-pair theorem. For an upper witness U and a policy-specific lower witness L, signed generator inequalities and the actual stopping contract give a bound on V minus J of the implemented policy. No smoothness of the optimal value or uniform controlled-boundary regularity is assumed. The implementation uses outward interval arithmetic rather than sampled residual maxima.

For the original NDU Hamiltonian, the complete constrained selection rule covers consumption, adjustment, negative or zero portfolio curvature, and endpoint maxima. The action-domain audit of this continuous generator therefore does not omit controls between grid nodes. We also prove a separate exact-semigroup decomposition containing time/within-step-feedback, action restriction, state interpolation, quadrature, exit, inner-solve, and arithmetic terms. Each must be bounded on the stated continuation function; missing bounds are not set to zero.

**Executed original-model result.** The retained six-date and twelve-date seed-10 raw nodal policies are deployed as feasible bilinear feedback, continuously reevaluated at the current state, with the feedback function frozen over each decision interval. Their original Brownian dynamics and true first exit are certified with explicit witnesses. The computed uniform date-zero regret bounds are 14.0914048908 and 8.3395605260, respectively.

**Interpretation.** This is an actual continuous-model certificate rather than a null field or an unproved transfer from the finite economy. It is also too conservative to establish the .01 or .05 target. The original-payoff precision requirement is therefore not marked closed. The paper identifies verified spatial residual potentials and a fully bounded semigroup decomposition as concrete tightening routes; it does not report either unexecuted route as a numerical result.

**Locations:** main sections “Verification of the continuous economy” and “A complete discretization accounting route”; proof appendix; `replication/verify_continuum.py`; `results/continuum_witnesses.json`.

## R5-F2. The safeguard changes the algorithm and can replace most of the actor

**Changes.** Raw NBO and threshold-safeguarded NBO are defined as separate algorithms. The new safeguard corrects gains exceeding a tolerance-scaled threshold, then independently re-evaluates and re-audits the corrected policy. It never uses an optimal reference value as its stopping rule. The paper proves a conditional bound on correction share and states its training-convergence hypothesis explicitly.

**Executed result.** On the retained twelve-date seed-10 policy, the previous all-positive-gain sweep replaced 54.6602% of decisions. At a .05 target, the new threshold replaces only **0.8746%**, while reducing the localized finite envelope from **.0922420 to .00682279**. At a .01 target it replaces 4.9350%, with envelope .00676060. No retraining was used to obtain these comparisons. The six-date policy already passes .05 without correction and reaches .00327838 at the .01 target with an 8.7956% correction share.

**Cost and scope.** Each audit still searches all 125 grid actions and the frozen proposal. The twelve-date, two-audit procedure performs 2,362,200 value-action evaluations and 2,343,600 envelope-action evaluations, each with four shock branches, and takes about 1.64 seconds on the recorded worker. This is not a dimension-free safeguard. Historical training time and current audit time are not added across different machines as though they formed a matched end-to-end measurement. The two retained-policy re-audits do not establish a full training-dose or action-dimension scaling law.

**Locations:** main finite-correction section and Table “Thresholded correction of retained NDU policies”; `diagnostics.py`; `results/safeguard_results.json`; corrected policy arrays.

## R5-F3. Numerical convergence of the economic discretization

**Changes.** The revision adds controlled one-factor studies of the time step, state lattice, and action mesh, followed by a finer 96-date, 49-by-61-state, nine-points-per-control cost panel. All arrays and operator-agreement checks are retained.

**Result.** The time-only sequence at a fixed state grid moves from -1.45149 at 24 dates to -1.60853 at 96 dates. This does not support a convergence claim: the spatial interpolation ratio h-squared over time-step increases. State refinement at 48 dates moves the value from -1.54979 to -1.39165. The paper explains this interaction instead of fitting a spurious order or presenting the .05 policy diagnostic as model convergence.

**Remaining precision requirement.** Shock quadrature and first-exit treatment are not independently refined or rigorously bounded in this new finite-scheme panel. No continuous value, policy, exit-probability, or comparative-static error bar is manufactured from the coarse/fine differences. A fully resolved original-economy numerical calculation remains outstanding.

**Locations:** main approximation-diagnostics section, mesh and cost tables; `diagnostics.py --task mesh`; `results/mesh_results.json` and twelve factor/configuration records.

## R5-F4. Transfer from a manufactured boundary example to a learned actor

**Changes.** The new test uses the original NDU state dimension, three-dimensional control box, correlated diffusion, wealth-dependent portfolio volatility, and first-exit settlement. It changes only the running payoff by subtracting the state/time-dependent optimal residual of the known witness. This modification is stated as a change of economic payoff, not as an equivalent normalization.

Six declared actors are actually trained, without optimal-action labels, to maximize the witness Hamiltonian. Their frozen weights are verified on the full state domain by outward interval arithmetic. The proof directly controls the continuous stopped diffusion, not simulated endpoint exits.

**Result.** All six continuous regret upper bounds are between .00081053 and .00112263. Componentwise action errors are reported separately. The experiment supplies the previously missing learned-actor transfer test on the economic control/exit geometry.

**Scope.** The critic witness is known and the actor has four parameters. This is not evidence that the original-payoff NDU value has been resolved or that a deep high-dimensional critic has been certified.

**Locations:** main learned-geometry section and table; corresponding full proof; `learned_geometry.py`; six weight/history/certificate JSON records.

## R5-F5. A difficult control problem and demonstrated benefit

**Changes.** The new benchmark has bounded d-dimensional controls with a coupled sine running cost, a nonconvex action Hamiltonian, and a coupled terminal payoff. Neither method receives an analytical greedy action or optimal-policy labels. It does not use the earlier Cole–Hopf reduction.

Both methods have identical initial actor/critic weights within each seed and two width-48 tanh layers. The primary budget is ten seconds of single-thread CPU training, with setup and audit costs reported separately. Dimensions 8 and 16 each have six independent training/audit seeds.

**Result.** At dimension 8, mean realized costs are .595671 for NBO and 2.313524 for SOC-MartNet; the paired NBO-minus-SOC difference is -1.717853, with a Student 95% interval [-2.138231, -1.297474]. At dimension 16, the corresponding costs are .480669 and 2.727989, and the paired difference is -2.247320, with interval [-2.512877, -1.981764]. These are favorable results at the declared short training budget.

**Limits.** Setup-plus-training averages approximately 10.69 seconds for NBO and 10.02 for SOC-MartNet, so the paper does not call this an exactly matched ten-second end-to-end race. Constant diffusion is used to match the selected author-code interface. The experiment does not establish distance to the unknown optimum, a matched-accuracy computational frontier, long-budget superiority, or universal dimensional scaling. The earlier unfavorable quadratic-control NBO comparison remains in the supplement.

**Locations:** main external-comparison, uncertainty, and resource sections; `external_comparison.py`; all twelve paired records, 24 checkpoint files, and 12 rollout-array files.

## R5-F6. External implementation and current literature

The comparator now calls the **unmodified author routine** `socmartnet.solver.SOCMartNet.train` from `sx-fang/MartNet` at commit `991ea8dde5bad6ba912eb8cc48b0cb48dbdd6c2a`. Model/network adapters and a completed-update wall-clock scheduler are fully disclosed. Module hashes and the exact source commit are bound in the execution manifest. This is an author-code adapter experiment, not a claim to reproduce the authors' published hardware, architecture, or convergence curves.

The main paper updates the AAAI 2026 exploratory HJB policy-iteration reference, the August 2026 interior-error version of physics-informed policy iteration, the published 2025 SOC-MartNet article, and the published PI–DeepONet article. A contribution matrix distinguishes error objects, inner-action treatment, boundary setting, representation reuse, and the experiment actually run. We do not claim priority for neural policy iteration, martingale control training, or residual verification in general.

## R5-F7. Statistical design and economically meaningful tolerances

The new external design fixes six seeds per dimension and uses a different independent audit seed for each training seed. Within each pair, 4,096 paths share Brownian increments across methods. The primary comparison uses 128 time steps; a nested 64-step audit gives a matched discretization diagnostic. The report separates paired across-seed uncertainty, paired path standard errors, and mesh changes. It does not count paths as independent training runs or treat a mesh change as a certified discretization bound.

The Student intervals are approximate six-seed inference, not distribution-free confidence guarantees. The maximum paired path standard errors are about .01098 and .00900. The measured mesh changes are small relative to the paired method differences, but the remaining time bias is not rigorously bounded.

The new economic theorem bounds a possible adjustment-budget reversal by the sum of policy regret bounds divided by the price change, plus any budget measurement errors. Value enclosures give secant bounds for optimal budgets and interval bounds for the value of access to adjustment. These formulas replace cross-model reuse of an arbitrary .05 threshold with explicit accuracy requirements. The original utility normalization is retained; no empirical welfare calibration is claimed. The recursive and game seed counts have not been enlarged by the external experiment.

## R5-F8. Recursive utility and games

The manuscript preserves the Epstein–Zin aggregator and sign domain, sophisticated-self evaluation convention, and unilateral all-subgame game verification. A new monotone-Lipschitz operator proof extends finite gain accounting with products of step-specific Lipschitz constants. It states the invariant continuation-value domain required for a nonlinear recursive operator.

The prior recursive raw failures and 961-action repairs, and the small three-date game, remain visible in full. They are not replaced by the favorable additive-control experiment. No new large-scale recursive or game experiment has been executed in R8; the general mathematical framework and the small-model computational evidence remain distinct. This empirical scaling requirement is not marked closed by a theorem about a different control problem.

## R5-F9. Adjustment-cost comparisons and action refinement

The new nine-points-per-component, 729-action panel reports central values -1.416240, -1.437379, and -1.468043 at k=.5, 2, and 8, and adjustment budgets .016811, .011583, and .001888. Every economy is independently re-solved. This preserves the predicted budget ordering at finer finite-action resolution.

More importantly, the new approximate-optimality theorem and value-interval proposition show exactly what is required to certify the economic comparison. They do not infer a pointwise ordering of adjustment from a first-order condition. Because the original continuous value enclosures remain wide, we do not claim that the welfare effect or its magnitude is resolved beyond all approximation error. The consumption corner and finite action discretization remain disclosed.

## R5-F10. Complete and reproducible manuscript artifact

R8 provides complete canonical plaintext main and supplement sources, a human-readable response, all generated table inputs, and a one-command clean build. The supplement includes the entire retained R4 exposition and proofs without altering those files and all six delivered R5 tables. No partial base64 transport capsule is required.

The numerical execution manifest binds source commit `14ecbd481b0586cfbb72a0c00239184a4a2b0553`, run `35676743048`, the author implementation, raw arrays, checkpoints, logs, and all numerical source inputs. The review build additionally binds its exact manuscript checkout, every table and source input, validation report, and PDF output. The delivery commit contains generated outputs; its parent/source identity is explicit rather than falsely claiming a manifest can hash its own final commit.

Run from the repository root:

```sh
bash revisions/2026-09-22-r8/build.sh
```

This verifies the executed evidence, recomputes the paired statistics from raw path arrays, checks corrected-policy shares, generates the current tables, compiles both manuscripts, and writes the build manifest. Re-executing stochastic training is a separate documented command and workflow; a clean manuscript build does not silently retrain or replace the committed experiment.

## Direct answers to the referee's ten questions

1. **Finite to continuous controls:** the complete NDU fixed-jet action rule and one-sided continuous witnesses provide a direct route; the semigroup theorem gives the alternative fully accounted discretization route.
2. **Omitted error terms:** every term is named in the exact-semigroup decomposition. They are not all numerically enclosed by the present scheme study. The direct witness test instead audits the continuous feedback itself.
3. **What is the safeguard?** A distinct, explicit policy-improvement algorithm, not a diagnostic renamed as neural training.
4. **Its scaling?** Full candidate-action enumeration remains; exact action-operation counts are reported. No action-dimension-free guarantee is claimed.
5. **Why did the n=12 raw actor fail?** Its independently measured finite gain envelope exceeds the target. The new audit shows that correcting fewer than 1% of decisions suffices for one retained policy at the .05 target; it does not manufacture a causal explanation or a new raw training success.
6. **Recursive raw failures?** Both remain failures at their target; their global-grid corrections and cost are retained, not credited to the raw neural actor.
7. **Beyond analytic greedy action?** The new coupled sine-control Hamiltonian is nonconvex and trained without an analytic optimizer or labels.
8. **The NBO benefit?** The new paired author-code experiment favors NBO at its declared short budget; the prior unfavorable quadratic-control comparison is preserved.
9. **Tolerance calibration?** The approximate comparative-static and value-interval results tie required utility precision to the price change and the economic effect, without claiming empirical calibration.
10. **Exact reproduction?** The clean build, immutable execution records, source/output manifests, and full plaintext/PDF artifacts supply a single reviewable chain. The incomplete historical R5 capsule is not used.

## Status for the next review

The revision makes substantive progress on the control-domain proof, continuous verification implementation, trained geometry transfer, safeguard dependence, external comparison, statistical reporting, and reviewability. It does **not** assert that all scientific requirements are closed. The key remaining quantitative requirements are a tight original-payoff continuous NDU enclosure, validated exit/quadrature contributions if the scheme route is used, and larger recursive/game and matched-accuracy scaling experiments. These are stated without removing the underlying economic questions or substituting a no-go conclusion for the revision.
