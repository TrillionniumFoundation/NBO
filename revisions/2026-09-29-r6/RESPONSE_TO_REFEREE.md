# Response to the 28 September 2026 numerical-methods report

**Paper:** Neural Bellman Operators. **Revision:** R6, 29 September 2026.
**Report source:** `reviews/2026-09-28-econometrica-numerical-methods-r2/referee_report.md`, report branch commit `278fb174eaee816259642675533a7281815a3df4`.
**Reviewed main manuscript:** R2 commit `d9054ab6284369ccd6134286e9d2694e3621d562`, blob `d3261aaa857ce9bdc1c479cc3785711846a3f845`.
**Revision ancestry:** R5 commit `28e769a7e8f10cf89871b1a17e35c6ce269329aa`.

The report is the repository-owner-commissioned advisory report identified in its own preamble, not an Econometric Society editorial decision. We respond to its substantive numerical and mathematical objections. The economic scope, title, author, recursive utility, preference adjustment, temporal selves, games, and diffusion-trace agenda are retained. The revision supplies new trained computations rather than substituting another topic or treating exactly solvable laboratories as generic neural evidence.

## B1. Execute the proposed method

The new section **A Trained Neural Boundary-Value Problem** trains actual two-hidden-layer actors and critics on a nonhomothetic consumption diffusion with labor income and a specified retirement payoff on exit. `stopped_consumption.py` imports the existing `nbo_core` differentiation and block losses. Neither reference values nor reference policies enter training. Three seeds, separate optimization histories, exact weights, held-out values/derivatives/actions, and both boundary errors are retained.

The new NDU section trains width-32 multilayer critics and categorical actors against their own Bellman continuation arrays in the original preference-adjustment economy. The dense-capital section trains multilayer networks with nonquadratic, densely coupled drift, common noise, and a shared adjustment cost in dimensions 2, 5, 10, and 20. No Riccati or Lyapunov solve supplies their critic. These experiments directly address the absence of a nontrivial neural economic solve.

Failures are substantive results. All three joint-loss consumption ablations fail the specified residual/action accuracy criteria. An initial NDU classification implementation produced large policy losses and is archived; cost-sensitive Bellman losses and exclusion of economically irrelevant absorbing-face labels repair that implementation. One principal NDU seed still misses the declared policy-regret target. Two 20-state primary NBO seeds miss the high-dimensional diagnostic target. No seed is removed because it is unfavorable.

## B2. Isolate the numerical contribution

The consumption comparator is direct neural HJB with the identical critic architecture, feasible action optimizer, seed convention, collocation construction, and total L-BFGS inner-iteration cap. The comparison also includes an independent monotone upwind policy-iteration reference and a deliberately joint-differentiated loss ablation. Architecture depth/width and critic-to-actor iteration allocations are varied separately.

For NDU, direct finite-Bellman fitting uses the same critic and action set; eliminating the actor gives a stronger result at this budget. For dense capital, direct HJB and NBO share the network class, sample budget, exact derivative treatment, and globally solved action problem. We report actual closure counts, times, diagnostic thresholds, failures, and process-level memory rather than claiming equal floating-point work from an equal iteration cap. The new evidence does **not** establish universal NBO superiority over direct HJB. It identifies where an explicit actor has approximation cost and where the block graph prevents a consequential optimization error.

The literature discussion now explicitly identifies approximate modified policy iteration (Scherrer et al., 2015). DGM and deep BSDE remain relevant alternatives, but this revision does not mislabel its plain-MLP direct-HJB baseline as the gated DGM architecture or claim an executed deep-BSDE comparison. Those comparisons are not prerequisites hidden inside the reported numerical advantage: no such universal advantage is asserted.

## B3 and M1–M3. Make certificates operational and distinguish error layers

The stopped-consumption experiment implements an outward-rounded interval verifier. It covers every point of the entire state interval, propagates values and first/second derivatives through the stored network, maximizes over the entire closed consumption interval, and verifies both stopping faces. A strong-concavity bound controls the action gap without a sampled Lipschitz estimate. The complete dyadic leaf cover and hashes are saved. All six primary NBO/direct runs meet a uniform residual threshold of 0.002; the resulting conservative regret bounds are below 0.051 utility units. These bounds do not use a numerical-reference discretization estimate.

The certificate is conditional on an explicitly stated binary64 arithmetic contract. Exp/log enclosures use range reduction and polynomial remainder bounds; comparisons with 80-digit arithmetic and independent automatic differentiation are tests, not a formal machine proof. This is a concrete continuous-domain implementation in one state, not a claim that interval subdivision avoids dimensional complexity.

The implemented-map definition specifies its domain, codomain, evaluation/improvement maps, sampling stream, and structured verification output. The differential-to-Bellman proposition keeps the generator consistency error explicit. Finite-horizon certificates return time-indexed evaluation, improvement, boundary, and regret accounts. The NDU computation evaluates every finite state, time, and action, while leaving continuous-action and time/state approximation errors unavailable rather than zero. The supplement states which hypotheses are checked separately for each application.

The viscosity theorem remains a perturbation theorem for a monotone scheme under scaled approximation errors. We do not infer the required `o(h)` rate from a finite optimizer run. Representation, incomplete optimization, action coverage, discretization, and embedding a discrete policy in continuous time are separate accounts. This resolves the implementation/interpretation ambiguity without deleting the theorem or claiming an optimizer convergence proof that was not established.

## B4. Action bounds in preference adjustment

The new sensitivity program independently reproduces the referee's coarse-grid values for the 27-, 63-, and 175-action sets. It also evaluates 1,053 actions inside the fixed expanded box, a wider action box, a wider wealth domain, two finer state/time grids, and both adjustment-cost parameters. Every control's upper/lower boundary frequency is retained. All utility levels, normalization, correlation, stopping data, and reflection rules remain those of the original model.

The earlier reference is retained as the solution of its declared constrained approximation. Its endpoint choices are no longer offered as an unqualified continuous-control reference. Widening the feasible box changes the constrained economy; refining a fixed box is a different operation. The new tables reveal continuing consumption and portfolio bound sensitivity, instead of concealing it behind state-grid refinement. Neural and reference errors are compared only within the same stated finite economy.

## B5. Neural scaling rather than matrix identities

The original coupled LQ calculation remains, explicitly classified as an exact matrix-identity/integration check. It is not counted among the new neural training runs. The dense nonlinear capital study actually differentiates and optimizes generic networks; the productivity matrix, covariance, shared action cost, terminal data, architectures, and seeds are saved.

Fixed sampled-accuracy targets and first observed crossings are reported together with final failures. Monte Carlo policy-payoff checks show that small residuals in the initial fitted box do not ensure payoff accuracy along paths outside that box. A labeled follow-up expands the domain and optimization budget. Both successful and failed wider-domain results remain in the record. These results advance the proposed scaling experiment while explicitly separating sampled diagnostics from a uniform high-dimensional welfare certificate.

## B6. Deliver economic extensions

NDU now receives actual neural fits and independent policy evaluation. The dynamic capital Cournot model now receives backward equilibrium calculations and independently optimized dynamic fixed-rival best responses over every finite state, own action, and time. Six principal configurations include two space/time/action resolutions, both market-size normalizations, alternative equilibrium tie selection, and asymmetric adjustment costs. All six have zero detected unilateral exploitability at the stated numerical precision. A coarser test with a missing pure stage equilibrium is explicitly identified as approximate and verifies time-indexed deviation bounds.

This result concerns the specified finite dynamic game. It is not a trained neural Markov-perfect equilibrium or a proof of continuous-control equilibrium convergence. The recursive-utility and temporal-self models, proofs, and calibrated analytical examples are retained unchanged in economic scope. They are not relabeled as unrestricted neural computations. Thus the extension program now contains delivered NDU and dynamic-game calculations without conflating approximation classes.

## B7. Coherent breadth without deleting the original agenda

The revised order establishes a complete model–operator–bound–neural experiment chain before returning to the original economic applications. Common evaluation, improvement, boundary, and deviation accounts organize those applications. Every original scientific section and principal proof remains. Superseded descriptions of unexecuted experiments are replaced by the new executed record; exact R2 main/supplement sources are archived, and the older reviewed archive and R5 derivation are inherited. The section-preservation map identifies each location.

## M4. Stochastic trace execution

`coupled_diffusion.py` uses actual Hessian-vector products during ten-state neural training. The product method uses two independent banks of two Gaussian probes; the single-bank comparator squares a four-probe estimate. Exact traces evaluate the common held-out residuals. All seeds, objective signs, times, and payoff samples are retained. A separate regression checks both the product objective and its parameter gradient against the exact expression under declared Monte Carlo tolerances. Similar observed performance at this covariance scale is reported rather than inferring a training advantage from unbiasedness alone.

## M5. Durable and exact-source reproduction

The R6 package contains executable source, generated tables, stored parameters, pointwise arrays, full interval covers, optimizer histories, per-path payoffs, best-response maps, logs, dependency versions, and content hashes. Its replication workflow is restricted to the new R6 candidate branch. It first commits the materialized source, then reruns the experiments and checks, regenerates tables/PDFs, and commits the raw evidence with the exact computational source commit. The review branch, main branch, and older revision branches are not modified. Failed accuracy targets remain false in the output.

The local complete archive accompanies the revision. Local and remote executions carry separate provenance; a successful repository workflow is not described as independent referee approval. The primary data counts, source identities, and successful/failed test outcomes are machine readable. Remote status is reported only after querying the actual workflow and branch head.

## M6. The meaning of “operator”

The NBO is now a specified randomized numerical map from an admissible policy, critic initialization, and sampling stream to a value approximation, improved feasible policy, and verification record. Its evaluation/improvement steps are identified with approximate policy iteration. The positive-weight Bellman map is a separately defined analytical/discrete object, and the new transfer proposition states the conditions connecting it to a differential candidate. Neither neural fitting nor an informal use of “operator” is credited with monotonicity or contraction.

## Reading order for re-review

Read the new implemented-map subsection, differential/discrete accounts, and trained stopped-consumption section first. Then inspect the NDU neural and action-sensitivity tables, dynamic fixed-rival best-response section, and dense nonlinear/trace experiments. The supplement contains arithmetic details, application-specific assumptions, all seed-level results, and coverage failures. The code and raw artifacts permit each claim to be checked independently of the response letter.
