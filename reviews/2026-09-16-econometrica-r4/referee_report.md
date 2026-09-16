# Referee Report: Neural Bellman Operators — Revision R4

**Review date:** September 16, 2026  
**Repository:** TrillionniumFoundation/NBO  
**Reviewed branch:** `revision/econometrica-r4-2026-09-16`  
**Reviewed commit:** `f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32`  
**Authoritative manuscript:** `ECTA_R4.tex` and its included sections; standalone supplement `SUPP_R4.tex`.  
**Previous report:** R3 report at `79a7d84be2cbbf9bd5d181599ee110540128e3b5`.  
**Recommendation:** **Reject in its present form.**

This is an owner-commissioned, AI-assisted advisory review written to the substantive standard expected of an Econometrica referee. It is not a journal commission, an appointment by Econometrica, or an editorial decision. The report evaluates the pinned revision, not the author's intentions. It adds review material on a new branch without changing the manuscript, author programs, or deposited author results.

## 1. Assessment for the editor

R4 is a substantially more credible manuscript than R3. There are now actual trained policies and value approximations, a stochastic transition retaining the specified covariance, a coherent exit contract, and a genuine constrained stochastic resource experiment. The exact policy-improvement proof has been repaired. The principal finite-horizon error account is mathematically sound under its stated hypotheses. The response also correctly abandons the implication from isolated actor stationary points to optimal policies. These changes should be credited rather than obscured by recycling the previous report.

The difficulty has consequently changed. R3 often computed the wrong object. R4 largely specifies its objects correctly, but it has not established a sufficiently important new methodological or economic contribution. Its strongest verified numerical result is a small convex stochastic program solved with an approximate convex continuation function and an online convex optimizer. Its main nonlinear economic application still exhibits large independently measured profitable deviations. Its economic theorem is a general envelope/revealed-preference argument, and the numerical policy conclusions are highly sensitive to the utility level relative to liquidation.

A new reviewer experiment identifies a particularly important omission in the author's ablation. With the same trained resource critics, replacing the neural actor by a zero initial action and retaining the convex improvement solver changes complete lifetime policy costs by at most **1.33 × 10⁻¹¹** and **4.65 × 10⁻¹¹** in two independently rerun cases. Both actor-free policies still satisfy the reported **10⁻³** target. The actor does reduce root optimization iterations in these cases; it is not literally without computational effect. But the manuscript has not isolated the economic or computational contribution of learning that actor rather than solving the surrogate convex decision problem directly.

There are also narrower, demonstrable problems. The abstract's monotonicity language about adjustment “expenditure” is not the theorem about unweighted effort: the paper's own table gives a nonmonotone coefficient-weighted cost. The supplement describes dynamic exploitability as a maximum over all dates, while the implementation aggregates that statistic only at date zero. An independent all-date calculation finds no economically significant deviation in the stated game, so this is a reporting defect, not evidence of a false equilibrium. More importantly, the reset-capacity specification makes equilibrium investment independent of current capacities and identical at the first three dates.

I recommend rejection, not another mechanical round of certification and relabeling. A new submission would need a sharper contribution and a substantive demonstration of it. More diagnostics can establish reliability, but reliability of a combination of familiar ingredients is not itself a sufficient general-interest contribution. Nothing in this recommendation requires abandoning the research program or deleting its historical materials.

## 2. What this revision genuinely resolves

The specific objections in the previous report should be separated from their broader publication implications. The following assessments concern source inspection and the selected executions described in Section 5; they are not a claim that every deposited experiment was independently reproduced.

| Previous finding | Assessment of R4 |
|---|---|
| R3-F1: no executable neural solver | The absence is resolved. `solver.py`, `safeguard.py`, and `coupled_resource.py` implement trained representations. Their contribution and performance remain open issues. |
| R3-F2: missing diffusion and covariance | Resolved at the transition-construction level: all intended covariance components enter the four-branch rule. A continuum error bound remains unavailable. |
| R3-F3: impossible state constraint and reinjection | Resolved by an explicitly different stopped economy. This is a legitimate model change, not proof that the former state constraint was viable. |
| R3-F4: grid-locked adjustment and omitted portfolio | Positive interpolation restores the adjustment margin, and all controls and genuine feasible gains are reported. Those gains now reveal significant remaining inaccuracies. |
| R3-F5: beta repeated in ordinary continuation | The displayed and implemented sophisticated-self recursions now separate evaluation from the acting self's criterion. |
| R3-F6: wrong K-probe estimand | The batch mean is squared before averaging over repeated batches; the old statistic is retained as a negative control. |
| R3-F7: suboptimal stationary actor limit | The invalid implication is removed and its counterexample is retained. Convex and candidate improvement are distinguished from actor optimization. |
| R3-F8: incomplete exact proof and absent error bridge | The exact limiting-value argument is repaired. A correct conditional error account is supplied, but its inputs are not established for the nonlinear economic application. |
| R3-F9: static pseudo-scalability calculation | A real three-period stochastic resource problem replaces it. The new experiment is limited, but calling it a static calculation would be wrong. |
| R3-F10: arithmetic presented as solved applications | Homothetic feature solves, finite-state games, and graph/domain tests are now distinguished. Their limited scope is largely disclosed. |
| R3-F11: closest literature omitted | The relevant comparisons are now cited. The remaining issue is demonstrated incremental contribution, not bibliography alone. |
| R3-F12: unreachable source and status conflation | The R4 source anchor resolves, and the manifest distinguishes evidence and tolerance status. I verified the two author modules used in my executions byte-for-byte, not every artifact in the manifest. |

The exact evaluation topology now includes the time derivative and appropriate traces. The proof correctly obtains equality of limiting values, `E(p) = E(I(p))`, rather than assuming equality of limiting policies. The trace U-statistic argument also correctly separates fixed-parameter unbiasedness from optimization and generalization. I do not find a reason to repeat the earlier allegations against those repaired statements. [M2, M3, S1, S2, RESPONSE]

## 3. Detailed findings

### R4-F1. The contribution remains a collection of useful but largely elementary components — blocking for publication

**Sources:** Introduction; main Sections 2–4; Supplement S.1; references [1]–[4] below.

The finite-horizon theorem follows by inserting the target and implemented backups into two sup-norm recursions. If `D_n` is the critic's distance from its policy value and `R_n` its distance from the optimal value, the proof establishes

\[
D_n\leq\epsilon_n+\kappa_n+\gamma_nD_{n+1},\qquad
R_n\leq\epsilon_n+\delta_n+\kappa_n+\gamma_nR_{n+1}.
\]

Backward substitution and the triangle inequality yield the stated policy-loss bound. The bookkeeping is correct. It neither proves a new approximation rate for the network nor controls its statistical or optimization errors. The paper itself identifies the proof as backward error propagation. Architecture independence is useful, but also means that this theorem does not establish a distinctive neural method.

The other principal economic result follows from

\[
V(k)=\sup_{\pi}\{B^{\pi}-kC^{\pi}\}.
\]

Convexity is the upper-envelope property; monotonicity of optimal effort follows by adding the two optimality inequalities. Endogenous stopping does not complicate that argument once the policy class is fixed and `k` enters only the objective. The approximate-policy version adds the two objective losses. This is a correct and useful diagnostic, but it holds for essentially any optimization problem with a nonnegative activity penalized linearly by a coefficient. It does not reveal a distinctive mechanism of endogenous risk preferences.

The two improvement safeguards are likewise familiar operations: include a proposal in a feasible finite search, or bound a differentiable convex objective by its linear minimization gap. The finite-tree cost interval is the direct tangent inequality. The manuscript appropriately declines priority for input-convex architecture, neural policy iteration, or pointwise improvement. What remains to support a contribution of this journal's scope?

The relevant comparisons have substance, not merely similar titles. Jacka and Mijatović study continuous-time policy improvement under explicit stochastic-control hypotheses [1]. Kim and coauthors' August 9, 2026 revision combines neural fixed-policy evaluation with pointwise improvement and an interior error analysis involving continuous residual and boundary-information terms [2]. Lee and Kim combine policy iteration with operator learning, including reuse across terminal functions [3]. Amos, Xu, and Kolter explicitly develop inference by optimizing over inputs to convex neural representations [4]. These references do not prove that every R4 application is already solved. They do show why separation, convex inference, and residual accounting cannot by themselves carry the novelty claim.

**Required resolution:** State one specific advance over the closest applicable method and establish it. This could be an operational error guarantee in a difficult economic problem, a convincingly measured computational advantage, or a consequential economic result inaccessible to simpler methods. Merely assembling the existing theorems and tests under a common name is insufficient. This is an assessment of significance, not an assertion that the conditional theorems are false or that an exhaustive priority search has been completed.

### R4-F2. The policy-loss theorem is not yet an operational error budget for the main nonlinear application — major

**Sources:** [M3, M5, S1, S3], especially equations labeled `eq:eps`, `eq:delta`, `eq:kappa`, `eq:value_bound`, and `eq:differential_bound`.

The crucial error is not just a critic training residual. The theorem requires the discrepancy between the implemented and target operators on the learned continuation, uniformly over the relevant state-action set. In the stopped portfolio economy that discrepancy contains time discretization, covariance quadrature, interpolation, and first-exit payoff approximation. The Torch training backup evaluates a network at successor locations; the NumPy evaluator propagates a bilinearly interpolated grid value. Both differ from exact stopped-diffusion evaluation.

R4 acknowledges these differences. That acknowledgment avoids a false certification claim, but it does not supply the missing quantitative link. No numerical upper bound for the relevant `kappa_n` is obtained, the finite candidate sets do not come with verified continuum covering/Lipschitz error bounds, and held-out residual maxima are not uniform bounds. Thus the new theorem cannot determine whether the errors are small enough for a particular economic comparison in the principal nonlinear example.

The independently certified resource losses do not fill this hole. They are obtained by a different, valid route: evaluate the full finite tree and bound its optimum through a convex reference. The general error account is unnecessary for that calculation. At present, the nonlinear application lacks its inputs, while the application with a useful certificate bypasses it.

This is not a demand for a global classical PDE theorem at rectangle corners. The paper may instead establish an explicit finite-problem result, a defensible local/occupation-weighted economic guarantee, or a carefully validated numerical convergence claim. But it must identify which substantive conclusion the new analysis enables that the reference calculation alone would not.

**Required resolution:** Instantiate the bound or a suitable replacement in an economically meaningful case, including the operator and action-approximation components. State an error tolerance in the units of the economic conclusion and show that it is met. A declaration that the missing constants exist, or another sampled residual table, does not complete this task.

### R4-F3. The strongest experiment does not establish that learning the actor contributes to policy accuracy — blocking for the claimed methodological contribution

**Sources:** [RESOURCE], functions `run`, `greedy`, and `Critic.fit`; [M5, S6]; reviewer diagnostics D1–D2.

The resource training sequence first computes greedy controls and target values using a **zero** starting action. It then trains an actor to imitate those controls and fits the critic to the already-computed target values. The actor's fitted output does not enter the critic's training target. At deployment, its only role in the final policy is to initialize the convex improvement solver.

The author's same-weight ablation removes improvement and keeps the actor. That correctly measures how much the online solver improves the proposal. It does not measure whether the actor is needed when that solver is retained. In fact, the construction provides a natural missing comparator: the identical trained continuation functions, with zero initialization of the same convex optimizer at every query.

I independently reran the exact author source at dimension four and seeds 101 and 202, reloaded the resulting weights, and evaluated both policies over all 64 terminal shock paths at each of the 32 held-out initial states. The policy-cost accumulation was written separately from the author's reporting loop. Both variants use the same learned critics, feasible set, transitions, and optimizer tolerances.

| Reviewer rerun | Actor-initialized upper loss | Zero-initialized upper loss | Maximum absolute difference in lifetime cost |
|---|---:|---:|---:|
| d = 4, seed 101 | 0.000644631967976 | 0.000644631967743 | 1.33075 × 10⁻¹¹ |
| d = 4, seed 202 | 0.000488447419116 | 0.000488447422331 | 4.64895 × 10⁻¹¹ |

The actor-initialized replay exactly reproduces the locally rerun policy costs. Both zero-initialized policies remain below the `10^-3` target. This is evidence from two selected cases, not a claim about all nine dimension-seed combinations.

There is a real countervailing fact: the actor reduces root solver iterations from 101 to 81 in seed 101 and from 121 to 101 in seed 202. Later-date iteration counts are unchanged in these tests. A warm start may be valuable. The missing issue is whether those savings justify training and evaluating the actor, particularly across large query batches. That net benefit has not been measured.

Strong convexity explains the near-identical accuracy: the one-period surrogate has a unique minimizer, and sufficiently accurate minimization largely removes dependence on initialization. This does **not** show that the learned convex critic is dispensable. It shows that the experiment does not isolate a contribution from a learned actor to policy quality, even though the actor/proposal component receives considerable methodological emphasis.

**Required resolution:** Add the actor-free baseline and separately report actor training cost, inference cost, solver iterations, and amortized total cost. Compare critic feature classes or a suitable non-neural value approximation to identify what the representation contributes. Retain the successful finite-tree accuracy result, but do not infer necessity or advantage of the full architecture from an ablation that removes only its indispensable optimizer.

### R4-F4. The resource benchmark is valid but too limited to supply the missing general computational result — major

**Sources:** [M5, S6, RESOURCE, T-RESOURCE].

The model is genuinely dynamic, stochastic, coupled, and constrained. Its scenario-tree reference is nonanticipative; the tangent-gap inequality is appropriate for the convex objective. These are meaningful improvements over R3. They do not establish broad high-dimensional performance.

There are three decisions, four shock realizations per step, 21 decision nodes per initial state, and 64 terminal paths. The shock loading has rank two. State dimensions are four, eight, and sixteen. The test evaluates 32 fresh initial states per seed. These are specific finite experiments, not evidence of robustness to long horizons, richer shock structure, or a difficult nonconvex continuation problem. A valid pointwise certificate on those trees supplies no automatic guarantee for an unseen continuum of initial conditions.

The manuscript also correctly reports that the structure-exploiting reference is faster at the common tolerance. From its table, median neural end-to-end times are about 10.1, 11.8, and 14.1 times the corresponding reference times across the three dimensions. I do not treat this as an unfair baseline, a hidden timing error, or proof that neural approximation can never be useful. The author explicitly acknowledges the result. But the possible advantage of a reusable feedback representation is still conjectural at the tested workload, and each feedback query continues to solve an optimization problem.

Nor would replacing the reference by an intentionally inferior generic grid method settle the issue. The appropriate comparator exploits the actual problem's convex structure. A useful comparison should establish either a break-even workload, generalization to new economically relevant queries, or a capability for which the simpler solver genuinely becomes inadequate.

**Required resolution:** Measure the claimed use case at matched accuracy, including online improvement and query volume, or provide a different substantive application demonstrating a clear capability gain. A larger dimension label with the same short rank-two scenario tree is not by itself the needed advance. These are scope and significance concerns; the reported nine passes are not being relabeled as failures.

### R4-F5. The nonlinear portfolio policies remain materially improvable, and initial-state agreement does not settle their economic reliability — major

**Sources:** [M5, SAFE, SOLVER, T-NDU, T-POLICY, T-REFINE].

The main table reports maximum feasible one-step gains of 0.228318, 0.210235, and 0.228568 for the three safeguarded seeds. These gains use the independently evaluated policy continuation and include the incumbent action. They therefore demonstrate actual profitable deviations **within that finite evaluation model**, not merely different control coordinates. They are lower observations of possible improvement, not upper bounds on all deviations.

By contrast, reference-minus-policy differences at the single initial state are approximately 0.0010–0.0014. The maximum initial critic/policy discrepancy reaches 0.934824 for seed 303. The full-vector policy table reports maximum discrepancies of 0.562 in consumption, 0.400 in adjustment, and 1.300 in portfolio share. The last two are the full admissible ranges. Large control differences near switching surfaces need not imply large welfare losses, so I do not interpret each coordinate discrepancy as a welfare failure. The feasible gain calculation, however, is already in value units and independently establishes meaningful remaining suboptimality at the tested states.

Discretization uncertainty is also material to interpreting the initial-state comparison. The published joint refinements change the initial reference value from -1.140548 to -1.136916 to -1.135019. Their successive changes, approximately 0.003632 and 0.001897, are comparable to or larger than the displayed neural initial-state discrepancy. Those changes are not rigorous continuum error estimates. They do show why close agreement with one finite reference cannot be promoted into comparable accuracy for the diffusion economy.

Furthermore, the reference uses a finite action mesh, whereas a neural proposal can take actions outside that mesh. Thus `V_R - J` is a comparison with a feasible finite-action reference, not automatically a nonnegative loss relative to the continuum optimum. R4 mostly labels this carefully; future argumentation must retain the distinction.

The aggregate k-panel is separately re-solved by grid maximization, not by retraining and validating neural policies at each k. Its monotone effort pattern is a useful consistency check, but it does not independently validate neural comparative statics. Because the discrete objective has the same affine-in-k structure as the theorem, that ordering is largely a property the correctly optimized finite model is expected to possess.

**Required resolution:** Identify where the large feasible gains arise, their occupation relevance under economically meaningful starting distributions, and their consequences for the intended comparative statics. Improve the policies or supply a defensible welfare-error account on the economically relevant region. Refine the operator and action approximation jointly where the conclusion is sensitive. A hard boundary identity and a favorable single starting point cannot substitute for that work.

### R4-F6. Liquidation and the cardinal utility level drive the economic application, without an adequate robustness argument — major

**Sources:** [M4, S3, T-K]; reviewer diagnostic D3.

The stopped contract is mathematically coherent. It also substantively changes the economic problem. The paper proves that its liquidation payoff is a strict supersolution: continued operation incurs a negative flow-plus-generator-minus-discount relative to that payoff for every admissible action. It explicitly acknowledges that exit incentives are part of the calibration. I agree with that acknowledgment, but do not see an economic justification or robustness analysis that would permit the numerical portfolio signs to carry broader substantive meaning.

The issue is not limited to normalization depending on the controlled preference state. Even adding a constant `m` to the running reward changes policy rankings when liquidation occurs at a policy-dependent time and the terminal payoff is left fixed:

\[
J_m^{\pi}-J_0^{\pi}
=m\,A^{\pi},\qquad
A^{\pi}=E^{\pi}\int_0^{\tau}e^{-\rho t}dt
=\frac{1-E^{\pi}e^{-\rho\tau}}{\rho}.
\]

Thus the level of utility relative to the outside option affects the willingness to prolong operation. This is an economically different specification, not an innocuous representation change. If the terminal payoff were also increased by `m/rho`, the combined change would instead be the policy-independent constant `m/rho`. A coherent economic account must explain the relative normalization of both objects.

I re-solved the author's finite transition model after adding one unit to running reward while holding the liquidation payoff fixed. At `(u,X)=(2,1.25)`, all other coefficients, feasible controls, shock rules, and action meshes were unchanged.

| Finite approximation | Running reward shift | Initial value | Initial `(c, theta, pi)` | Discounted operating duration |
|---|---:|---:|---|---:|
| 17 × 25, four dates | 0 | -1.1405481993 | (0.8, 0.2, -0.5) | 0.8847052744 |
| 17 × 25, four dates | 1 | -0.2532151541 | (0.8, 0.2, 0.8) | 0.8919359411 |
| 33 × 49, eight dates | 0 | -1.1369156510 | (0.8, 0.2, -0.5) | 0.8878074082 |
| 33 × 49, eight dates | 1 | -0.2470774770 | (0.8, 0.2, 0.8) | 0.8941989907 |

The portfolio moves across its full feasible interval on both meshes. The zero-shift calculations reproduce the corresponding published reference values. This does not establish a continuous-time reversal, identify a unique mechanism, or show that the original calibration is inadmissible. It demonstrates that a simple, currently unmotivated reward-level choice can overturn the portfolio sign in the very finite model used for the evidence.

**Required resolution:** Ground the liquidation/outside-option level and utility normalization in a coherent economic question, and separate preference hedging from incentives to shorten or prolong the operating regime. Report robustness over economically defended alternatives and show a substantive finding beyond the generic cost-effort ordering. The solution is not to hide the exit mechanism, reintroduce projection, or simply rename a short position as hedging.

### R4-F7. The abstract confuses unweighted adjustment effort with coefficient-weighted adjustment cost — moderate, but directly concerns the headline economic claim

**Sources:** Abstract in [MAIN]; the definition of `C^pi` and Theorem `thm:k` in [M4]; [T-K].

The theorem proves monotonicity of

\[
C(k)=E^{\pi_k}\int_0^{\tau}e^{-\rho t}\theta_t^2/2\,dt,
\]

not monotonicity of the actual coefficient-weighted adjustment term `k C(k)`. The abstract describes optimal discounted adjustment expenditure as decreasing in the coefficient. If expenditure denotes the cost appearing in the objective, that statement is not proved and is contradicted by the reported finite-model panel.

Multiplying the rounded table entries gives approximately 0.007307, 0.019776, and 0.011456 at k equal to 0.5, 2, and 8. The coefficient-weighted cost initially increases. This arithmetic does not challenge the effort theorem, which is correct. It does challenge an economically natural reading of the abstract.

**Required resolution:** Use the unambiguous term “discounted cumulative adjustment effort” for `C`, distinguish it from `kC`, and report the latter if expenditure or total adjustment cost is discussed. A result about the quantity of a costly activity is not automatically a result about total spending on that activity. Do not claim a new theorem for the latter without the additional restrictions it requires.

### R4-F8. The capacity example removes much of the intertemporal strategic difficulty it is supposed to illustrate — major as application evidence

**Sources:** [M6, S5, DIAGNOSTICS], function `game_test`; reviewer diagnostic D4.

Next-period capacity is drawn with probability equal to current investment and does not inherit current installed capacity. Current revenue is determined before that investment affects capacity. Consequently the current capacity pair affects the current payoff but not the investment maximand. Equilibrium investment is independent of both current capacities.

The simplification goes further. For the nonterminal decision dates, the value can be written as current operating profit plus a term depending only on demand. The latter term drops out of the marginal value of next-period capacity. With symmetric interior investment, the equilibrium therefore satisfies

\[
a_n(D)=\frac{\delta\{E[D'\mid D]/3-1/9\}}{\kappa+\delta/9},
\quad n=0,1,2,
\qquad a_3=\frac{0.05\delta}{\kappa}.
\]

At the stated parameters, the first three dates all have investment approximately 0.4551648352 and 0.5679120879 in the two demand states; the last date has 0.11875 in both. An independent backward solution using the two-by-two affine best-response system agrees with this formula to 1.11 × 10⁻¹⁶. Capacity dependence is exactly zero in the calculation.

This remains a legitimate finite stochastic game: investment affects next-period profits and the firms interact strategically. It is not the static Cournot arithmetic criticized in R3. But the renewal specification eliminates persistence of installed capacity and the associated longer-horizon strategic feedback. An eight-state enumeration therefore overstates the effective complexity of the investment policy. A complete state table and near-zero deviation gains do not demonstrate performance on a difficult dynamic capital game, much less on a trained neural equilibrium method.

**Required resolution:** Retain this as a transparent regression test or introduce an economically motivated persistent state mechanism when claiming substantive dynamic-game capability. The task is not to make a toy problem artificially complicated; it is to align the evidentiary weight assigned to the example with the actual intertemporal interaction it contains.

### R4-F9. The reported exploitability statistic does not cover the dates claimed in the supplement — moderate reporting defect

**Sources:** [S5] and [DIAGNOSTICS], final best-response loop in `game_test`; reviewer diagnostic D4.

The supplement describes a maximum over all dates, states, and players. The implementation computes a deviating value recursively at every date, but updates `maxgain` only **after** completing the date loop, by comparing the final backward value with `V[0, player]`. It therefore aggregates only date-zero gains. The program has the intermediate information required for an all-date check but does not include it in the returned statistic.

I independently solved the unilateral best-response problem at every date. The largest positive signed difference was 5.55 × 10⁻¹⁷, ordinary floating-point noise. There is no evidence from this check that the displayed equilibrium fails sequential optimality. The point is narrower: the stored metric and the stated metric are different, and the discrepancy should not be preserved merely because this particular game happens to pass the stronger check.

**Required resolution:** Accumulate per-date comparisons inside the backward loop, retain their locations, and distinguish signed rounding-level discrepancies from material profitable deviations. Update the ledger and description together. This is not an independent reason to reject an otherwise publishable paper, but it is a concrete source-to-claim inconsistency.

## 4. Conditions for a substantively reconsiderable submission

The next version should not treat this report as a request for nine more labels in a ledger. The central choice is what the paper contributes. A methodological contribution needs a demonstrated advantage or an operational guarantee beyond standard backward approximation with feasible improvement. An economic contribution needs a significant mechanism or conclusion that survives the relevant approximation and modeling uncertainty. Both routes are open; neither is supplied by a broad catalogue of applications.

For the current resource route, the decisive missing comparison is not another seed alone. It is the actor-free solver, the incremental value of the chosen continuation representation, and the total cost at a workload where a reusable feedback approximation is actually valuable. For the endogenous-preference route, the decisive missing evidence concerns approximation error at economically relevant states and the normalization of the stopped outside option. The current generic effort theorem cannot stand in for those results.

The recursive-utility, temporal-self, trace, and game materials can be retained with their correctly limited roles. Their validity as checks is not a reason to multiply headline contributions. The conditional Epstein–Zin comparison class is not a general existence theorem for arbitrary recursive policies; a trace estimand identity is not a trained-policy accuracy theorem; a detached-rival graph test is not a neural equilibrium computation. R4 mostly acknowledges these distinctions already. The next step is a focused contribution, not further disclaimer accumulation.

Preservation of previous manuscripts is compatible with a sharper current paper. I do not request arbitrary deletion of mathematical content or the historical archive. I request that the main argument earn the evidentiary weight it assigns to each component. Mechanical closure of the concrete defects in F7 and F9 would improve accuracy but would not resolve the publication recommendation.

## 5. Independent execution, reproducibility, and limits

The accompanying `reviewer_diagnostics.py` verifies the Git blob identities of the two imported author modules before executing them:

| Module | Bytes | Git blob |
|---|---:|---|
| `replication/r4/solver.py` | 10,384 | `e283614b137cd898d49a06f82d5938dc3c6a9cca` |
| `replication/r4/coupled_resource.py` | 10,423 | `7a8a82af0b343685b3edc8c5e24a6e86b0f5d9ad` |

Full SHA-256 identities, package versions, selected rerun identities, and diagnostic results are deposited alongside this report. The author's R4 manifest names source commit `d9f995c1e69696c3acecefed30fdaa99f00952ab`; a GitHub Git-commit lookup resolved that commit during this review. The old unresolvable-source objection is therefore not repeated. This is not a byte-level verification of every author checkpoint, source, table, or PDF.

The selected checks are:

**D1 — Author resource execution.** Two complete cases, dimension four with seeds 101 and 202, were independently trained and evaluated from the exact source. Both attained the reported target. For seed 101 the reviewer upper loss, 0.0006446319679763795, agrees with the deposited author value, 0.0006446319679762442, to approximately 1.4 × 10⁻¹⁶. Proposal-only costs differ slightly across executions; no claim of bitwise neural-training replication is made. An initial attempt at the default nine-case command hit the execution time limit after the two completed records. The remaining cases are not reported as independently rerun or as numerical failures.

**D2 — Missing actor-free ablation.** Saved weights from those reviewer reruns were reloaded. The same convex continuation functions were used with actor initialization and zero initialization, followed by complete-tree policy-cost evaluation. The zero-start test removes the actor only, not the critic or the improvement optimizer. It reproduces the accuracy and iteration observations in F3.

**D3 — Stopped-economy reward-level sensitivity.** The positive transition model was re-solved on two specified state-time grids and the same 175-point action mesh, with reward shifts zero and one. This is a finite-model robustness experiment and is not a continuum certificate or an assertion of utility-representation equivalence. The original baseline values are reproduced before interpreting the changed economies.

**D4 — Independent game solution and all-date deviations.** A separate two-by-two best-response solve and unilateral backward recursion verify the closed-form simplification and check deviations at all four dates. This does not modify or silently repair the author's implementation. The metric-scope finding is established by source inspection; the stronger check finds no material deviation.

From a checkout of the new review branch, run:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
python reviews/2026-09-16-econometrica-r4/reviewer_diagnostics.py
```

The default command retrains only the two declared resource cases and writes under the review's `rerun/` directory, not under author outputs. NumPy, SciPy, and CPU PyTorch are required. The deposited aggregate result was generated with `--reuse-existing` after those independent author-source reruns, to avoid repeating their training during packaging; the flag is recorded explicitly. Scientific conclusions should be compared at the stated tolerances, not by wall time or complete file hashes that include timings. The reproducible program is not intended to rerun every source-inspection finding.

**Limits:** I reviewed the main and supplemental TeX argument, the current response, the relevant previous report, and selected code and numerical records. I did not independently retrain the three safeguarded NDU networks, rerun all nine resource cases, rebuild every table, conduct interval arithmetic, prove uniform PDE errors, or compile/render the PDFs. Assertions in this report about author-reported NDU tables are identified as such. The targeted primary-literature check establishes relevant prior mechanisms and version identities, not exhaustive novelty priority. The recommendation is an editorial assessment supported by the specified findings, not a claim of complete formal verification of the repository.

## 6. References and immutable source map

### Primary literature

[1] Jacka, S. D., and A. Mijatović (2015). *On the policy improvement algorithm in continuous time*. [Primary preprint](https://arxiv.org/abs/1509.09041).

[2] Kim, Y., M. Kim, Y. Kim, and N. Cho (2026). *Physics-Informed Policy Iteration for High-Dimensional Hamilton–Jacobi–Bellman Equations: Interior Error Bounds without Boundary Data*. Version 2, August 9, 2026. [Version-pinned primary preprint](https://arxiv.org/abs/2508.01718v2). The 2025 first version has a different title and author ordering; this report does not conflate them.

[3] Lee, J. Y., and Y. Kim (2024). *Hamilton-Jacobi Based Policy-Iteration via Deep Operator Learning*. [Primary preprint](https://arxiv.org/abs/2406.10920).

[4] Amos, B., L. Xu, and J. Z. Kolter (2017). *Input Convex Neural Networks*. Proceedings of Machine Learning Research 70, 146–155. [Primary proceedings record](https://proceedings.mlr.press/v70/amos17b.html).

### Repository sources

All R4 links below are pinned to the reviewed commit, not a moving branch. Source labels in the report identify TeX sections, equation labels, tables, and executable function names; they are not PDF page references.

- [INDEX: authoritative revision index](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/REVISION_INDEX.md)
- [MAIN: main wrapper and abstract](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/ECTA_R4.tex)
- [INTRO: introduction and related work](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/revisions/2026-09-16-r4/paper/01_introduction.tex)
- [M2: operators and exact improvement](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/revisions/2026-09-16-r4/paper/02_operators.tex)
- [M3: approximation analysis](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/revisions/2026-09-16-r4/paper/03_approximation.tex)
- [M4: endogenous preferences](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/revisions/2026-09-16-r4/paper/04_preferences.tex)
- [M5: computation](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/revisions/2026-09-16-r4/paper/05_computation.tex)
- [M6: recursive utility, selves, and games](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/revisions/2026-09-16-r4/paper/06_extensions.tex)
- [S1: operator proofs](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/revisions/2026-09-16-r4/paper/S1_proofs.tex)
- [S2: counterexamples and trace estimands](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/revisions/2026-09-16-r4/paper/S2_negative_controls.tex)
- [S3: stopped preferences and effort proof](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/revisions/2026-09-16-r4/paper/S3_stopped_preferences.tex)
- [S4: recursive-utility verification](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/revisions/2026-09-16-r4/paper/S4_recursive.tex)
- [S5: temporal and game supplement](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/revisions/2026-09-16-r4/paper/S5_equilibria.tex)
- [S6: replication supplement](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/revisions/2026-09-16-r4/paper/S6_replication.tex)
- [T-NDU: neural policy table](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/revisions/2026-09-16-r4/paper/table_ndu_neural.tex)
- [T-POLICY: all-control discrepancy table](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/revisions/2026-09-16-r4/paper/table_ndu_policy.tex)
- [T-REFINE: state-time refinements](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/revisions/2026-09-16-r4/paper/table_ndu_refinement.tex)
- [T-K: adjustment-cost panel](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/revisions/2026-09-16-r4/paper/table_ndu_k.tex)
- [T-RESOURCE: resource comparison](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/revisions/2026-09-16-r4/paper/table_resource.tex)
- [RESOURCE: resource solver](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/replication/r4/coupled_resource.py)
- [SOLVER: transition and neural primitives](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/replication/r4/solver.py)
- [SAFE: safeguarded preference solver](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/replication/r4/safeguard.py)
- [DIAGNOSTICS: author game and diagnostic functions](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/replication/r4/diagnostics.py)
- [RESOURCE-101: deposited author case used for comparison](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/replication/r4/output/resource_results_4_101.json)
- [MANIFEST: author provenance and evidence identities](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/replication/r4/output/manifest.json)
- [RESPONSE: R4 response to the R3 report](https://github.com/TrillionniumFoundation/NBO/blob/f20dcb1483f509ff34c17c8c6fcb94bd51f0ab32/revisions/2026-09-16-r4/response_to_referee.md)
- [R3: previous report, pinned to its review commit](https://github.com/TrillionniumFoundation/NBO/blob/79a7d84be2cbbf9bd5d181599ee110540128e3b5/reviews/2026-09-16-econometrica-r3/referee_report.md)

### This review's evidence

- [Executable reviewer diagnostics](reviewer_diagnostics.py)
- [Full-precision diagnostic results](diagnostic_results.json)
- [Review provenance and scope manifest](review_manifest.json)
