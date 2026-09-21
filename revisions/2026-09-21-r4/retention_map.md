# R4 retention and correction map

All historical paths below are inherited unchanged from review commit `79a7d84be2cbbf9bd5d181599ee110540128e3b5`. R4 adds a new canonical entry, `ECTA_R4.tex`; it does not overwrite `ECTA.tex`, `ECTA_R2.tex`, `SUPP_R2.tex`, the old replication scripts or previous reports.

| Scientific material | Current authoritative treatment | Historical retention |
|---|---|---|
| Controlled Markov dynamics, Bellman evaluation and improvement | Main economic problem and separated-operator sections; fixed-policy BSDE and Markov closure | Original and R3 TeX unchanged |
| Exact policy-iteration consistency | Proposition `prop:exact`, full strong-topology and shifted-value proof | R3 proof remains available for comparison |
| Neural approximation and stochastic optimization | Explicit finite-model training; derivative-approximation qualifications; invariant-set versus global-optimality distinction | Previous architecture and optimizer descriptions preserved in R3 source |
| Critic/boundary/actor error bridge | New Theorems `thm:continuous` and `thm:finite`, with full proofs | Added result; no historical derivation deleted |
| NDU interior diffusion, preference cost, terminal payoff and action box | Retained in equations `eq:ndu-state` and `eq:ndu-hjb`; full constrained selectors in `app:ndu` | Original derivations unchanged in historical TeX |
| Invalid viable-rectangle/clipping boundary | Replaced for the current model by an explicit first-exit liquidation contract, settlement fee and contract sensitivity | Original boundary interpretation and code retained as historical evidence, not a simultaneous current specification |
| NDU comparative statics | New global adjustment-budget theorem and independently re-solved cost/zero-adjustment panel | Earlier illustrative policy/path arrays remain embedded in old TeX |
| Merton | Actual separated HJB neural updates, automatic derivatives, independent analytical policy evaluation | Original algebraic diagnostics retained |
| Epstein-Zin recursive utility | Correct aggregator, sign domain, driver derivatives, policy-wise evaluation and implicit finite reference | Original recursive application and algebraic anchors retained |
| Sophisticated temporal selves | One coherent improvement/evaluation recursion and beta-below-one analytic test | Earlier inconsistent beta conventions remain only in archived sources |
| Dynamic games | Detached-rival graph, finite three-date capacity game, equilibrium selection and unilateral-deviation definition | Static tests and earlier dynamic-game discussion retained |
| High-dimensional dynamics | Eight-date coupled stochastic LQ actor/Riccati comparison; no static-QP relabeling | Old static coupled QP remains in R3 replication archive |
| Hessian/trace costs | Diffusion-direction accounting, correct mean-trace loss, Gaussian variance proof and U-statistic | Old timing/trace records retained for provenance |
| Composite objective and nonsmooth value caveats | Explicit composite-bias and viscosity-selection counterexamples in `app:limits` | Historical negative controls retained |
| Historical figures and synthetic arrays | No current trained-network inference is attached to them; current tables use executed result records | All original embedded arrays and plots remain unchanged in `ECTA.tex` / `ECTA_R2.tex` |
| Referee materials | R3 report is the fixed input to the point-by-point response | All older reports and R3 response remain unchanged |

The new manuscript organizes its central economic and methodological arguments in the main text and moves proofs, complete constrained rules, boundary qualifications, recursive derivations and replication details to the appendices. Retention does not require presenting incompatible historical equations as if they were simultaneously valid current models. The comparison from the review base should contain additions only to previously absent paths; updates within those new R4 paths are ordinary revision commits.
