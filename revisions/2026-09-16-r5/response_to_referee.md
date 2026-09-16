# Response to the R4 referee report

**Manuscript:** Neural Bellman Operators  
**Revision:** R5, September 16, 2026  
**Review answered:** `reviews/2026-09-16-econometrica-r4/referee_report.md`, review branch `review/econometrica-r4-2026-09-16-f20dcb1`, commit `11082cc5054e91d3b2ac27826705f374ca74bfae`  
**Reviewed manuscript:** R4, `f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32`  
**New manuscript:** `ECTA_R5.tex`; independent supplement `SUPP_R5.tex`.

We thank the referee for separating the repairs achieved in R4 from the remaining economic and methodological questions. The present revision responds with a new economic argument, complete proofs, executed policy repairs, additional comparisons, and a persistent-capacity application. We retain the earlier exact policy-improvement proof, approximate-operator analysis, stochastic trace results, endogenous-preference model, recursive utility, temporal selves, and historical experiments. The revision is not a proposal to abandon these results, nor does it erase unfavorable numerical evidence.

The central addition is a study of **contract-aware, welfare-certified policy reuse**. In a stopped economy, the discounted operating duration and the discounted settlement exposure are linked by an accounting identity. That identity identifies the economically relevant contrast between a flow operating benefit and a liquidation increment. Evaluated policy features then support counterfactual decisions throughout an interval of that contrast. In the executed nonlinear example, the policy library is certified over every date and finite-model state and over the entire parameter interval, not just at the plotted queries. A separate action-separation calculation identifies intervals on which every optimal initial portfolio has the same sign. The initial neural policies are repaired within an explicitly declared positive finite transition model containing all previously tested deviations. The resource comparison now isolates the actor, a full convex-quadratic continuation representation, and a genuinely measured query workload. The game now has persistent installed capacity and an independent all-date dynamic best-response test.

We attribute the general successor-feature, policy-switching, and policy-cache ideas to the relevant prior literature, including Nemecek and Parr (2021). The contribution is not a claim to have invented affine reward decomposition or convex envelopes. It is the economic contract restriction, the operational interval and decision certificates, and the demonstrated use of these objects in the nonlinear stopped economy, together with an empirically resolved computation-cost comparison. The following responses identify the precise additions and their evidence. Machine-dependent measurements are generated from the executed records in `execution_summary.md` and the paper tables; no wall-time number in this letter is a promised performance rate.

## R4-F1 — A specific contribution rather than a collection of certification ingredients

**Response.** We have made the economic counterfactual the organizing question of the introduction and conclusions. If `m` is an operating-flow benefit and `ell` an additive liquidation payoff, any fixed policy satisfies

`J(m,k,ell) = ell + B + (m-rho*ell) A - k C`.

Here `A` is discounted operating duration, `C` is discounted cumulative adjustment effort, and `B` includes the baseline utility and settlement payoff before the adjustment charge. Consequently choices depend on the contrast `d=m-rho*ell`, whereas a coherent annuity shift leaves the entire optimal-policy correspondence unchanged. The proposition also supplies a joint, approximation-robust restriction on changes in duration and effort. It identifies an observational equivalence direction in the primitives; it does not assert that the remaining contrast is automatically identified from data.

The computational result is now tied to this economic object. We independently evaluate policy features and bound the optimum by certified anchor information. Switching among the stored policies attains the lower envelope. An exact piecewise-affine calculation finds the largest envelope gap across the entire scalar interval, including its endogenous intersections, at every state and date. The final library attains the specified `10^-3` welfare tolerance in the nonlinear finite economy. An action-separation proposition then converts endpoint information into a portfolio-sign conclusion throughout intervals, while displaying the band where the sign is not separated.

The underlying upper-envelope inequality is explicitly credited to the policy-cache literature. The new comparison with this closest literature is substantive: the stopped contract supplies the reward contrast, its settlement identity supplies the invariance and observational-equivalence restriction, and the executed interval/action calculations produce economic conclusions with a quantified welfare budget. We ask that the methodological and economic significance be assessed on these results and the measured reuse experiments, rather than on separation or convex inference alone.

**Locations.** Main Introduction; Section “Contract Changes and Certified Policy Reuse,” Propositions `thm:contract` and `thm:sign`, Theorem `thm:reuse`; Supplement S.7; `contracts.py`, `economic_robustness.py`; `contracts.json`, `sign_certificate.json`, `contract_workload.json`. The related-literature section retains Jacka–Mijatović, both relevant Kim versions, Lee–Kim, and Amos–Xu–Kolter, and adds Barreto et al., Chang, and Nemecek–Parr.

## R4-F2 — An operational welfare budget for the nonlinear application

**Response.** We implement the finite-problem route expressly identified in the report. The target is a positive killed Markov chain with 33 by 49 states and eight decision dates. Its common action menu is the **union**, not merely the finer-looking replacement, of the R4 `9×9×13` reference mesh and `7×7×11` diagnostic mesh. These meshes are not nested. We add the three frozen R4 neural policies as state- and date-dependent feasible actions and hold this combined action menu fixed across contracts. Thus every previously diagnosed feasible deviation and every incumbent policy is included.

Backward maximization gives the anchor values. A different feature recursion evaluates the selected policies; a separate comparison with the original NumPy interpolation backup checks the implemented kernel. For adjacent anchor contracts, the optimal-value chord is an upper bound and the evaluated policy lines are lower bounds. We compute the maximum chord-minus-envelope gap by checking endpoints and the intersections of the two policy lines, over all states and dates. This yields an actual uniform counterfactual welfare budget. The lower bound is not a training residual; the upper bound is not inferred from a feasible policy alone. The policy-switching proof explains why a new horizon factor is unnecessary once complete policy values have been bounded.

The chain is the target of this executed certificate. Time discretization, action discretization, and polygonal stopping are parts of its declared definition, not missing constants quietly assigned zero in a Brownian model. The original continuous-time operator account remains in the paper. Its transfer to the diffusion would still require bounds for its operator and action discrepancies. We also report joint state/time/action refinements, rather than treating agreement at one mesh as that missing bound. This separation makes a positive economic conclusion possible now without claiming an uncomputed continuum error.

**Locations.** Main Section “Contract Changes and Certified Policy Reuse”; subsection “Repair and Contract Counterfactuals”; Supplement S.7 and S.8; `contracts.py:Kernel`, `Economy`, `interval_certificate`, `adaptive_bank`; independent replays in `validate.py`.

## R4-F3 — Actor-free deployment and the continuation representation

**Response.** We agree that the actor is a warm start in the resource implementation. All nine dimension–seed combinations now compare actor initialization with zero initialization using exactly the same immutable trained critics, the same feasible set, the same convex optimizer and stopping tolerance, the same held-out states, and all 64 terminal paths. The near equality in lifetime cost found by the referee persists. Both variants meet the common loss target. We preserve and explain that result: accurate convex improvement removes dependence on initialization, so the actor is not the source of asymptotic policy accuracy in this example.

We separately measure actor distillation time, initialization/inference time, online optimization time, and iterations. Targets shared by the two variants are not charged twice. Linear break-even projections for the actor are labelled projections rather than observed workloads; runs with no measured net online saving do not receive a fictitious crossover. The main reusable-feedback workload therefore uses the actor-free solver. The actor remains available as a proposal mechanism in the broader framework and in the nonlinear portfolio experiment, rather than being silently removed from the historical record.

To identify what the continuation representation contributes, we add a full convex quadratic `q(x)+b+l'z+z'Hz`, with `H` positive semidefinite. This comparator has all cross-state quadratic terms. Its output parameters are fitted by projected convex least squares with an explicit projected-gradient tolerance, and it has its own backward training recursion. It uses the same online improvement and complete-tree evaluation. The squared-ReLU representation meets the common policy-loss target in all nine cases, while the full quadratic does not at the executed training budget and fit tolerance. This is evidence relative to the specified comparator, not a claim that no non-neural approximation could match it. An independent critic-only retraining replay verifies that the timing charged to the deployed continuation is for the same representation and weights to numerical tolerance.

**Locations.** Main subsection “What the Actor and the Continuation Representation Contribute”; resource comparison table; Supplement S.8 and the isolated actor-timing table; `resource_ablation.py`; individual `resource_{dimension}_{seed}.json`; `resource_ablation.json`; `validation.json`.

## R4-F4 — A measured reuse workload at matched accuracy

**Response.** The original short stochastic resource model is retained with its actual horizon, shock rank, and dimensions. We do not replace its specialized reference by a slower grid algorithm. Instead we test the stated use case: reusable feedback at fresh initial states. With the dimension-four, seed-101 trained continuation fixed, a new seed supplies batches of 32, 128, 512, and 2,048 initial states. Every policy is evaluated on its complete scenario tree. The reference is solved at the same `10^-3` target for timing, and a tighter reference gap supplies the accuracy bound for both arms. Critic-only training, zero-start improvement, and policy evaluation are included in the reusable method's total. The resulting table shows the actual crossover on the recorded machine, not an extrapolation from one query.

A second measured reuse experiment concerns economically different **contracts**, not merely new starting points. It compares 101 complete-policy counterfactuals evaluated by the certified library with 101 complete backward optimizations of the same finite portfolio economy. The reusable arm includes feature-based selection and full policy evaluation. The paper separately reports kernel construction and adaptive library preparation, so the online ratio is not confused with a training-inclusive ratio. The uniform interval certificate is stronger than the accuracy checks at these 101 workload queries; the latter independently validate the implementation and measure cost.

These additions establish a concrete successful workload while retaining the original evidence that the specialized resource reference is cheaper at a small batch. They do not assert a dimension-independent complexity result, a universal hardware-independent speed advantage, or success in an unexecuted long-horizon neural problem.

**Locations.** Main computation section; resource workload and contract-reuse tables; Supplement S.8; `resource_workloads.json`, `contract_workload.json`; explicit accounting in `replication/r5/README.md`.

## R4-F5 — Locating and repairing material policy deviations

**Response.** The revision no longer relies on a favorable single starting state. It replays each original neural policy and records its largest feasible deviation, the attaining state and date, its loss relative to the exact optimum of the expanded finite menu, and its occupation under both the focal initial state and a declared initial population. The population is uniform on grid nodes in `[1.6,2.4]×[0.8,1.6]`. Occupation-weighted sums are described as diagnostics, not upper bounds on optimal-policy welfare loss. The largest off-policy deviations cannot be dismissed merely because a selected starting distribution does not reach their maximizers.

We then repair the policies using the expanded menu containing both old action meshes and every incumbent. Independent evaluation of the repaired baseline yields no profitable one-step deviation above the numerical verification tolerance at any date or state. The subsequent contract library certifies all dates and states over the entire declared parameter interval. This resolves the specific finite-model profitable-deviation problem constructively instead of changing the diagnostic or hiding the boundary region.

The refinement panel now jointly changes the time grid, interpolation grid, and control mesh. In particular, the intermediate contrast can have a different portfolio sign on the coarsest model; that observation is retained. The baseline and high-operating-benefit signs survive the displayed joint refinements and the separate correlation panel. We do not transfer the exact switch interval from one finite model to the diffusion or to the other meshes without a bound that would justify that transfer.

**Locations.** Main repair and contract-counterfactual subsections; repair table; Supplement joint-refinement table; `contracts.json:baseline`, including locations and both occupation measures; `economic_robustness.json`; full `contract_bank.npz`; `validate.py`.

## R4-F6 — Economic meaning of liquidation and utility levels

**Response.** We retain the stopped economy and its declared cardinal units. We do not revive reinjection or present a changed running reward as a utility-representation equivalence. The revised question concerns a flow benefit of remaining in operation relative to a separately specified settlement increment. The identities for duration and terminal exposure prove which joint changes preserve choices and which genuinely change the contract.

This yields two separate tests. First, coherent annuity shifts preserve all policy rankings exactly, and an independently evaluated discounted-exit recursion verifies the identity numerically. Second, varying `d` with the outside-option increment fixed changes the operating-duration incentive. We solve and certify this entire contrast interval, rather than selecting only the two specifications that reverse a sign. A first-action comparison bounds all opposite-sign alternatives above, using the same fixed action and continuation policy as a witness at both interval endpoints. It identifies regions of strictly negative and strictly positive optimal initial portfolio and reports the intervening unresolved band. Value accuracy alone is not used to assert a sign at a near tie.

The interval is an explicitly specified contract experiment in the paper's fixed utility units, not an empirically estimated subsidy range. The economic finding is that the operating-benefit/settlement contrast can reverse the portfolio even when the covariance is unchanged; it is not a universal sign theorem for preference hedging. Separate zero and positive correlation re-solves test this distinction. The diffusion formulas separating mean–variance and preference-hedging terms, their necessary curvature conditions, and the baseline supersolution calculation remain available. The baseline supersolution bound is not asserted unchanged for every altered contract.

**Locations.** Contract-contrast proposition and its proof; portfolio-sign proposition and interval table; independent normalization check; correlation and joint-refinement outputs; the original preference-model section and Supplement S.3 remain intact.

## R4-F7 — Adjustment effort is not adjustment expenditure

**Response.** The abstract and new economic results use **discounted cumulative adjustment effort** for `C`. The expenditure/charge in the objective is `kC`. The new table reports both for each original cost coefficient. It retains the nonmonotonicity of the weighted charge instead of incorrectly extending the effort theorem. The proof and its approximate-policy version are unchanged; the joint contract proposition uses the same correctly defined effort functional.

**Locations.** Abstract, contract section, Supplement S.8, `table_r5_effort.tex`, `economic_robustness.json:cost_effort`.

## R4-F8 — Persistent capital and nontrivial dynamic strategic feedback

**Response.** The reset model is retained as a transparent regression, including its closed-form early actions. A new twelve-date game has `Pr(K_i'=1)=s K_i+(1-s K_i)a_i`, with `s=0.8`. Installed capacity can survive; investment repairs or replaces absent capacity. Both current capacities enter the continuation maximand. The original demand transition, operating-profit equation, convex investment cost, and salvage payoff are retained, making the economic source of the change explicit.

At each state and date we solve the two clipped affine best-response equations by checking all nine active-set combinations. The action objective is strictly concave in the player's own investment. The recorded product of best-response slopes is below one, establishing uniqueness for every solved continuation game. Backward induction gives the finite-horizon Markov-perfect profile. Investment now varies with installed capacity and over nonterminal dates. A separately evaluated full unilateral dynamic best response checks every date, state, and player. The complete policies and values are deposited.

This is evidence for a persistent dynamic game and a reliable equilibrium reference. It is not labelled a trained neural equilibrium experiment. The existing neural graph checks and continuous-time game formulation remain in the manuscript and supplement with their own roles.

**Locations.** Main extensions section, persistent-capacity table; Supplement S.8 derivation and uniqueness argument; `persistent_game.py`, `persistent_game.json`.

## R4-F9 — All-date exploitability, including a late-date negative control

**Response.** The discrepancy is repaired in the new executable implementation while the historical source remains unchanged for audit. The comparison of a player's full unilateral best-response value with the frozen-profile value is inside the backward date loop. The program stores the entire date–player–state gain array, signed extrema, and the attaining location. It runs for both the original reset game and the new persistent game. The stronger test finds no gain beyond floating-point tolerance; we do not relabel rounding-level signed differences as economic arbitrage.

A deliberately distorted final-date investment is an explicit negative control. It produces a material late-date gain, and the validator checks that final-date slice directly rather than merely inspecting the overall root statistic. This makes the tested scope match the revised statement in the supplement and prevents a date-zero-only implementation from passing through an uninformative equilibrium example.

**Locations.** `persistent_game.py:all_date_best_response`; `persistent_game.json:best_response` and `deliberately_distorted_late_policy`; Supplement S.8; `validate.py:test_game`.

## Preservation, execution, and reading order

The revision branch starts from the exact R4 **review** commit, not from main or an older manuscript. Every earlier review, manuscript, proof, negative control, figure, raw result, and checkpoint remains at its original path. The preservation map records how substantive material carries into the new manuscript. The only pre-existing file changed is the root revision index, which retains an explicit link to the R4 reading order. New source and new results are isolated in the R5 directories.

The authoritative reading order is: `ECTA_R5.tex` and its PDF; `SUPP_R5.tex` and its PDF; this response; `execution_summary.md`; then the source, full arrays, validation report, manifest, and build log. The source manifest pins the reachable commit identifying the executed scripts. The build report verifies preservation and manuscript compilation. Numerical certificates are explicitly for the specified finite models in double precision, with the stated tolerances; they are not interval-arithmetic or uncomputed continuous-time guarantees.

The report being answered is an owner-commissioned advisory review. This revision package does not represent journal submission, referee appointment, or an editorial decision. Its scientific claims are the stated propositions, proofs, executed comparisons, and error bounds, now available for renewed scrutiny.
