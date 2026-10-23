# R124B: prospective value-bridge and joint Bellman decision services

## Identity, temporal order and original objective

This is a **new post-A design**, motivated by the completed A finding of no incremental joint benefit; it is not an amendment of A's algorithm, sample, clocks, claims or results. A's source boundary is `2f0485174e7f518909ab73311e00251647ed6b47`, its independent state boundary is `a78ee67f386b2b547ecfb5f1986119c199c4fd68`, and its complete executed-evidence publication/readback is `a374219cc1063191d5da2a0d2ff1a41736b13d72`. A used restricted `fused_two` and `joint_two` menus. All its results, including zero joint-specific action or bound improvements, remain unchanged. The separate in-flight R123 experiment contributes only its already-published frozen algorithm and byte-identical dependencies; no unpublished R123 outcome is used.

B strengthens the conventional comparator to the **complete published R123 `fused` service**, called `fused_full` in this study. Its full candidate menu and best qualified selection are computed and paid afresh by every B arm. No original R123 experimental state or result is a B observation.

The economic object remains the original constrained two-date, two-state investment problem: state in `[0,1]^2`, continuous uniform innovation in `[-1/32,1/32]`, discount `15/16`, capacity `A(x)=1/8+(x0+x1)/16`, stage investment cost `a^2+4a^4`, and nested upper-cost AVaR with alpha in `{1/2,3/4}`. The optimized-future Bellman cost is `q=Q_x`. The unchanged implemented terminal controller has cost `J_x(a)=q(a)+eta(a)`, with `0<=eta<=delta=15/2^24`. No derivative or convexity of eta is assumed. The same original-model smoothness formula, strong convexity `mu=2`, qualification tolerance `tau=1/256`, and objective width `omega=1/8192` remain in force.

All56 M121 fitted actors at `796c5f2badf68b051ac6c144884c0e61b87faf5e`, plus the two risk-specific online solvers, are retained. The catalogue contains quadratic, ReLU, exactly matched ordinary hinge, cubic spline, degree-two and degree-three polynomials, and tensor linear grids, each at budgets5/9, training losses VALUE/MARGINAL, and both risk levels. There is no refit, new feature, model selection, hyperparameter adjustment or outcome-based exclusion. Matched hinge retains the same features/readout and pays the inherited ReLU-parent and audit acquisition allocation. B's information mechanisms are representation-neutral.

## B source, draw and execution boundaries

1. Publish this protocol, `REPORTING_SPEC124B.md`, the complete `code124b` source, mathematical statements used by B, requirements, and all imported A/R123/vendor/model/acquisition identities in `SOURCE_FREEZE124B.json`. Read the exact remote bytes back. This new immutable source commit is **F124B**. Analytic rational fixtures, fault injection and import/syntax checks may run before F124B; none evaluates an original-economic state.
2. Only after F124B remote readback, draw exactly320 OS entropy bytes once. Decode64 consecutive five-byte little-endian integers and divide each by `2^40`, yielding exactly32 fresh two-coordinate states. Retain duplicates and all integer/float/hex representations. Preserve the raw bytes. Publish and read back the complete draw as **D124B** before any original-economic evaluation. Independence is conditional on independent uniform OS bits and the frozen post-A design. These finite dyadic state draws do not replace the continuous innovation distribution inside the Bellman operator.
3. Execute the fixed complete primary, then three fresh **serial** timing processes, independent exact staged audit, separate independent economics, and fixed reporting. Each attempt has an exclusive directory, whole parent clock, stdout/stderr, source/draw/actor identity, terminal receipt or explicit preserved failure. Do not silently restart or overwrite a failed attempt. No A cache or state is a B evaluation.

## Three complete services and a shared new menu

Each service begins with a fresh complete original-law `fused_full` computation, including actor load/proposal, original qualification, rejected attempts, fallback, all paid support payloads and every R123 fused-menu candidate. This stronger conventional service is the first B arm.

For the second and third arms, let `a_F` denote that actual completed fused action. Keep every paid raw support and derivative-recovery premise. For duplicate paid anchor locations, a pairwise upper endpoint uses the minimum of the already-paid upper bounds at that location; no support or acquisition work is removed. Sort the distinct paid anchor locations.

The **new menu is generated once from a_F**. With at least two distinct paid anchors, enumerate every sorted pair `s<t`, first its strong-convex value-bridge minimizer and then its midpoint. For paid upper endpoints `U_s,U_t`, the bridge upper at `b=s+u(t-s)` is

`(1-u) U_s + u U_t - (mu/2) u(1-u)(t-s)^2`, for `0<=u<=1`.

Its minimizer is `u*=clip(1/2-(U_t-U_s)/(mu*(t-s)^2),0,1)`. Then append the six neighbors `a_F +/- A/16`, `a_F +/- A/64`, and `a_F +/- A/256`, in denominator order and negative-before-positive order. Round every proposed action downward onto the inherited30-bit grid and clip to the feasible grid capacity. Preserve every raw proposal and its provenance. Deduplicate actual actions by first occurrence for new-stage evaluation. A bridge inequality is used **only if its own anchor pair brackets the actual rounded action**. All bracketing pairs are considered; no unclipped or unrounded surrogate action is called the deployed action.

With fewer than two distinct anchors, this new menu is empty. This is an explicit experimental restriction; all such rows remain in the population and cost census. The A single-anchor saturation result does not automatically prove optimality of this restriction after the fused action moves away from an anchor.

The **bridge** arm evaluates this complete new menu using the same original fused derivative/support bounds plus every eligible pairwise bridge upper. Its incumbent is the actual completed fused action. It retains the best qualified strictly improving candidate by certified original-J gain descending, action ascending, then first menu index ascending; otherwise it retains the fused policy.

The **joint** arm first computes and pays the entire bridge arm itself. Its incumbent is the actual completed bridge action, `a_B`. It uses the **same menu that was generated from a_F**, without recentering candidate generation or buying a new Bellman observation at a_B. It recomputes legitimate bounds at a_B from the original paid ledger and applies the frozen exact rational joint interpolation certificate to every distinct nonidentity menu action. A candidate identical to the current incumbent has exact zero contrast and needs no optimization. No outcome, confidence interval or timing result changes this rule.

## Exact original-J certification and failures

Let `u(b)` be the minimum of the fused absolute q upper and all eligible bridge upper bounds, and let `l(a)` be the original fused/raw-support q lower at the current actual stage incumbent. Start the q-contrast upper at the minimum of the original fused contrast and `u(b)-l(a)`. In the joint stage also intersect this with the **exact rational dual contrast upper**. Transport the upper through the incumbent by replacing `u(b)` with `min(u(b),u(a)+contrast_upper)`. Keep the original valid q lower and original-optimum lower bound.

For a changed action, `J(b)-J(a)<=contrast_upper+delta`. Thus the gain lower is `-contrast_upper-delta`, and the candidate's J upper is `u(b)+delta`. Add delta exactly once in each stage implication. Require strictly positive original-J gain, regret at most tau, and interval width at most omega in exact rational arithmetic **and after outward binary64 conversion**. No smoothness of implemented J is used. The joint-versus-fused cumulative guarantee is the sum of the sequential bridge and joint gain lower bounds; telescoping uses the same original implemented controller throughout.

The imported joint module uses all paid anchors,0,A,the actual incumbent and candidate. Adjacent value/derivative interpolation constraints use the same original mu/L. Its finite boxes are necessary consequences of paid values and derivative cones. No extra global cap is imposed at every new node; no floating optimum is presented as the exact minimax value of a stronger capped class. SLSQP (`maxiter160`, `ftol1e-10`) only proposes a point and nonnegative-clipped multipliers. The exact convex-Lagrangian tangent plus its full finite-box gradient residual gives a sound rational bound regardless of optimizer success, primal feasibility or stationarity. Every started solve is recorded before execution; partial point/multipliers, exceptions, statuses and elapsed work remain visible. Unhelpful dual bounds are retained and charged.

Numerical failure retains the last completed qualified stage: bridge failure retains fused, and joint failure retains the completed bridge. Distinct fused, bridge, joint and outer failure flags plus original service/proposal failures are reported. An incomplete enhancement is never counted as a strict improvement. A contradiction in independent verification aborts with partial evidence retained.

## Complete experiment, serial clocks and evidence

Primary: all58 actor/risk cells times3 services times32 states = **5568 decisions**. The32 fresh initial states are the only independent population units.

Timings: three fresh serial processes, all174 service cohorts on exactly the first8 declared states = **4176 additional timed decisions**. Rotate the174-cohort order by `11*r modulo174`, for repeats r=0,1,2. Fix BLAS/OMP/MKL threads to one before scientific imports. Store full arithmetic witnesses in both primary and timing records. Lossless gzip JSONL uses fixed mtime0 and compression level6; compression/write work occurs inside the measured cohort and whole parent process. No record, rejected candidate or failed attempt is omitted to reduce file size. Exact final decisions, gains, qualification fields, primitive counts and stage identities must agree with primary on those first8 states. Preserve every clock; do not infer hardware-independent runtime confidence or controlled-frequency conditions.

The independent standard-library reader binds all cases to the actual original state, risk, model smoothness, capacity, tolerances and complete paid ledger. It rederives derivative intervals, the full fused menu, pairwise bridge geometry, fixed candidate menu, exact joint bounds, outward gates and ties. It verifies cross-arm identity of the actual completed fused prefixes and bridge incumbent, not merely identical raw actors. It checks all full timing records as well. Reporting requires and hashes its passing receipt.

## Independent original-economy validation

A separate process uses unchanged `independent94.py` rational primitives through the exact121 wrapper and does not import a production model, optimizer or solver. It evaluates **every distinct final action, actual stage incumbent, original incumbent, fused action, bridge action, available raw actor proposal and paid support anchor**, beginning with8 whole-support cells. Each interior terminal problem uses exactly16 bisections, and every terminal gap must belong to `[0,2^-20]`. Preserve every rational terminal/risk witness, work count and clock.

For every positive own-stage certificate, and every positive cumulative joint-versus-fused certificate, validate direct J gain and containment of the reported candidate interval. If either is unresolved, refine the origin and candidate through32 then128 cells, in that fixed order, stopping only on both confirmations or exhaustion. Identical action/mesh keys may share validation cache work **within B only**; this changes neither decision-service charges nor statistical weight. Retain the original8-cell bounds, chronological claim verdicts and every later refinement separately. Keep all unresolved and negative evidence. No B policy is changed after validation.

This calculation encloses optimized-future q and adds the proved unchanged uniform implemented-future allowance. It does not directly replay every rounded terminal-controller action. Original continuous-risk evaluation is never relabeled as a different discrete economic model.

## Complete inference, cost and interpretation

`REPORTING_SPEC124B.md` fixes all174 policy cells,232 nonnegative gain cells and threshold events,348 signed comparisons,696 clock cells and480 price menus. B inference is conditional on A and the frozen post-A B design. No A outcome is substituted as a B observation or validation.

Every hypothetical standalone service pays its inherited model-specific acquisition, the complete common parent residual, cold load, original fused prefix, bridge prefix where applicable, every candidate, every dual attempt and full inference/output work. Volumes32/256/4096/65536 are declared extrapolations, not newly measured throughput. Independent validation and publication-audit work belong to the separate actual research ledger. Historical unknown interrupted work remains unknown.

No improvement is presumed. A bridge victory is a victory of a strong conventional information method. A joint victory is evidence about the extra usable joint value/derivative information under the same ledger, subject to its full cost. ReLU/hinge equality, traditional winners, empty adoption regions, unresolved inference, absent gains and unhelpful optimizer work are all retained. Neural-specific superiority, higher-dimensional scaling and real-world calibration remain separate claims requiring their own evidence.
