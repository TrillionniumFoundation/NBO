# Referee Report: Neural Bellman Operators — Revision R4

**Review date:** September 21, 2026  
**Repository:** `TrillionniumFoundation/NBO`  
**Reviewed branch:** `revision/econometrica-r4-stochastic-operator-2026-09-21`  
**Reviewed commit:** `6083a59f60d067169144e23a2921bf4af0ddeb6e`  
**Authoritative manuscript:** `ECTA_R4.tex`, with main text and appendices under `revisions/2026-09-21-r4/paper/`  
**Recommendation:** **Reject in its present form.**

This is an owner-commissioned, AI-assisted external referee report written to the substantive standard I would apply to an Econometrica submission whose claimed contribution lies in numerical methods for dynamic economic models. It is not commissioned by Econometrica and is not an editorial decision. The report is pinned to the commit above and is written on a separate review branch; no manuscript or author replication file is modified.

## 1. Assessment for the editor

R4 is the first version of this project that I regard as technically coherent enough to review as an actual numerical-method paper rather than as a collection of incompatible claims. The revision genuinely fixes many of the severe R3 failures. The NDU transition now contains the stated preference diffusion, portfolio-dependent wealth diffusion, and cross covariance. The impossible state-constraint interpretation has been replaced by an explicit liquidation contract. Preference adjustment is no longer grid-locked by nearest-neighbor rounding. The sophisticated-self recursion and trace estimand are corrected. The false actor-stationarity implication is removed. The exact policy-iteration argument is materially better. Most importantly, there are now actual neural training runs and independent finite-model policy evaluation.

Those repairs are substantial. They also expose the remaining central problem more clearly: **the paper has not yet established a publishable numerical-method contribution at the Econometrica level.** The successful nonlinear NDU experiment is a two-state, six-date, lattice-trained finite problem in which the actor is trained on *all* interior grid points and receives labels obtained by exhaustive enumeration of all 125 discrete actions against the frozen critic. The independently coded exhaustive dynamic program solves the same finite economy in roughly 0.6–0.7 seconds, while the neural training takes roughly 19–21 seconds. The neural method therefore does not currently solve a computational problem that the benchmark cannot solve more directly, cheaply, and with an exact finite-model answer.

The more serious issue is that the finite economy itself is not yet shown to approximate the intended stopped diffusion with controlled error. The reported refinement table is strongly non-monotone and quantitatively material. The central value moves by about 0.141 when only the time grid changes from 6 to 12 dates on the coarse state grid, by about 0.191 when the state grid is changed at 12 dates, by about 0.079 when the baseline time grid is doubled from 12 to 24 dates, and by about 0.107 when the state grid is refined at 24 dates. The action-grid change from five to seven points per control moves the central value by another 0.013. The manuscript correctly refuses to call these differences a continuum error certificate. But once that concession is made, the main economic numbers are still values of a particular killed-Euler/Rademacher/interpolation economy whose relation to the continuous model remains unresolved.

The analytical contributions do not fill this gap. The finite-horizon certificate is mathematically useful, but in the actual neural runs its computable gain bounds are 0.259, 0.264, and 0.521, far above the paper's declared 0.05 policy-loss target. The statement that all three runs meet the 0.05 target instead uses the exact finite optimal reference itself. That is an audit available in this small experiment, not an operational certificate for an application where the optimum is unknown. The adjustment-cost theorem is correct and useful, but it is essentially a supremum-of-affine-functions/revealed-preference argument; it does not by itself supply the kind of new economic or computational result that would justify the broader method claims.

I therefore recommend rejection rather than another incremental revision. A reconsiderable paper would need a new numerical evidence package: a converged or otherwise certified continuous/stopped-control benchmark, a nontrivial nonlinear problem for which NBO has a credible accuracy/cost rationale, and a comparison against the closest modern policy-iteration/neural-control methods. R4 has moved from "incorrect implementation" to "correctly delimited but insufficient contribution." That is real progress, but it is not yet an Econometrica numerical-method paper.

## 2. What R4 genuinely fixes

The review should not recycle R3 objections that are now closed.

- The NDU finite operator now includes the stated two diffusions and their covariance, with a direct generator test on (1,u,X,u^2,X^2,uX).
- The lower-bound viability contradiction is no longer hidden by clipping. The economic problem now stops at first exit under an explicit liquidation settlement.
- Bilinear continuation permits preference adjustment to affect continuation values; the prior exact grid-locking failure is gone.
- All three policy coordinates are reported, and the manuscript openly records the large portfolio discrepancy even when value loss is small.
- The temporal-self code now separates ordinary continuation evaluation from the acting self's (eta)-weighted improvement.
- The trace experiment now squares the batched probe mean and reports the (1/K) population effect correctly.
- The actor-stationarity counterexample is incorporated, and the manuscript no longer identifies parameter stationarity with global policy improvement.
- The exact policy-iteration limit proof now uses equality of limiting values rather than an invalid equality of limiting policies.
- A continuous stopped-diffusion value-loss inequality and a finite-horizon counterpart are supplied with explicit hypotheses.
- Actual Merton and NDU neural runs exist, and the hard enacted policy is independently re-evaluated by a separate NumPy path.
- Failed and timed-out runs are retained rather than silently omitted.
- The recursive, game, and LQ calculations are more accurately labeled as reference or structurally favorable tests rather than as evidence they do not provide.

These are substantive corrections. The objections below concern the R4 object that now actually exists.

## 3. Detailed findings

### R4-F1. The central NDU "neural method" is an exhaustive finite-action dynamic program followed by neural compression — blocking contribution problem

The key implementation is `revisions/2026-09-21-r4/replication/solver.py`.

For each date, the code evaluates every one of the 125 discrete actions at every interior lattice point against the frozen next-date critic:

`q=q_torch(st,aa,nxt,t,cfg); labels=q.argmax(-1)`.

The actor is then a 125-logit classifier trained by cross entropy plus a softmax-weighted regret term. Training uses **all interior nodes** of the (25	imes31) lattice, not sampled states. Thus the global action maximization in the successful experiment is not learned; it is explicitly enumerated to produce the actor's training target. This avoids the old stationary-actor fallacy, but it also means that the method's most difficult control subproblem is solved by brute force before the actor learns anything.

The same issue appears in scaling. With three controls and (n_a) points per coordinate, the actor has (n_a^3) outputs and the target construction evaluates all (n_a^3) actions at every collocation state. In higher action dimension this becomes exponentially expensive. The paper currently presents the finite implementation as a realization of NBO, but computationally it is closer to **compressing an exhaustive Bellman maximizer into a classifier**.

This distinction matters because the independent exhaustive reference is faster than the neural method on the only nonlinear stochastic application actually trained. The reported reference times are about 0.60–0.67 seconds; neural training is about 19–21 seconds, before any argument about development or tuning cost. The manuscript is commendably explicit about this fact. But once stated, it leaves no demonstrated numerical advantage.

**Required resolution:** either (i) redesign the actor step so that the neural method actually solves a nontrivial continuous/high-cardinality action improvement problem without exhaustive labels, or (ii) explicitly redefine the contribution as a finite-action compression/certification method and demonstrate a regime where that compression has a measurable economic or computational benefit. The current experiment does neither.

### R4-F2. There is still no verified approximation to the intended continuous stopped diffusion — blocking

The paper now clearly distinguishes its finite model from the continuous diffusion. That is the correct conceptual repair. The numerical evidence, however, shows that this distinction is quantitatively important.

The refinement table reports central values

- (N=6,13	imes16,5): (-1.423383)
- (N=12,13	imes16,5): (-1.564151)
- (N=12,25	imes31,5): (-1.372708)
- (N=24,25	imes31,5): (-1.451486)
- (N=24,49	imes61,5): (-1.344458)
- (N=12,25	imes31,7): (-1.359628).

These movements are not small relative to the economic effects being discussed. They are also non-monotone across separately refined axes. The appendix itself correctly notes that positive interpolation can contribute an (h^2/Delta) term and that a coupled limit is required. But the paper does not execute such a coupled sequence. Nor does it give a monotonicity/stability/consistency argument for the full killed operator with boundary crossing and action discretization.

As a result, the successful neural policy-loss numbers (.0113–.0235) establish accuracy **only relative to one particular finite economy**. They do not show that the resulting policy is close to the policy of the continuous economic model, nor even that the reported central values are numerically resolved.

**Required resolution:** construct and execute a genuine convergence design in which (Delta), state spacing, action spacing, quadrature, and boundary treatment are refined jointly under a stated consistency condition. Report value and policy quantities along that sequence. Preferably provide either a theorem for the stopped scheme or a validated external reference on the same continuous problem. Separate one-axis sensitivity tables are diagnostic, not convergence evidence.

### R4-F3. The killed-boundary approximation remains numerically consequential and theoretically uncertified — major/blocking for the continuous application

The replacement of hidden clipping by an explicit liquidation contract is a major improvement. The remaining scheme is nevertheless not an exact stopped-diffusion solver. It uses four Rademacher branches and a straight-line first intersection of the Euler increment. A Brownian path can cross and return within a step; the linear-segment rule does not represent that event. The manuscript acknowledges that it is not a Brownian-bridge correction.

This would be less important if exits were rare. They are not: the central exit probability in the reported cost panel is about 0.249. With roughly one quarter of paths terminating under the numerical contract, boundary treatment is first-order for the application rather than a negligible edge effect.

The fee (F=8) is also a deliberately imposed primitive rather than an empirically disciplined object. That is legitimate for a computational example, but it means the paper should not use this application as evidence of a quantitatively resolved economic mechanism unless the stopped-diffusion approximation itself has been validated.

**Required resolution:** provide a convergence result or a validated boundary-correction experiment for the stopped process, including first-exit treatment. At minimum, compare endpoint killing, Brownian-bridge-type corrections where available, and finer time grids on a coupled spatial sequence. If the authors instead wish to study the finite killed chain as the economic model in its own right, then the continuous-diffusion interpretation should no longer carry the evidentiary burden.

### R4-F4. The finite value certificate is valid but too loose to certify the paper's own accuracy target — major

Theorem 2 is a useful finite-horizon residual/gain inequality. The implementation also uses the strongest favorable case: the enacted policy is independently re-evaluated exactly on the finite model, so critic defects can be removed from the certificate.

Yet the resulting finite gain bounds are

- seed 0: 0.259331
- seed 1: 0.264491
- seed 2: 0.520503,

while the measured date-zero losses are 0.011291, 0.023526, and 0.012797. The manuscript's 0.05 success criterion is therefore **not certified by the proposed bound**. It is verified only because the exact finite optimum is separately computed.

That distinction is central for a numerical-method paper. On a problem large enough to make the neural method useful, the exact optimum is precisely what will not be available. A posteriori theory that certifies only a loss ten to forty times larger than the actual error is not yet an operational stopping rule at the target accuracy used by the paper.

The critic errors against independently evaluated policy values are also substantial, roughly 0.07–0.14 in sup norm. The separation architecture is therefore doing something sensible—policy regret can be much smaller than critic error—but the current theorem does not turn the trained objects into a useful fine-accuracy certificate.

**Required resolution:** develop a sharper computable bound, localized/per-state certificate, occupancy-weighted guarantee with justified change of measure, or another a posteriori diagnostic that can actually certify the target regime without solving the optimal reference problem. Otherwise the certificate should be presented as a qualitative decomposition rather than as a practical validation mechanism.

### R4-F5. The benchmark suite does not establish scalability, competitiveness, or the necessity of NBO — blocking contribution problem

The Merton benchmark has one critic parameter and two actor logits in an analytically correct homothetic family. It is an excellent graph/derivative unit test, but not a serious neural PDE benchmark.

The coupled dynamic LQ exercise is also structurally exact: the critic family is quadratic and the actor is linear, so the known solution lies in the represented family. Dimensions 4, 8, and 16 are modest, the Riccati solver is faster, and the reported near-machine-precision errors reflect exact representability more than nonlinear approximation power.

The recursive-utility calculation is a scalar implicit reference solver, not NBO training. The dynamic game is an exact three-date finite enumeration, not a neural MPE calculation. The stochastic-trace example verifies an algebraic estimand, not the effect of stochastic Hessian contraction on a trained nonlinear control problem.

The only genuinely nonlinear trained stochastic application is the two-state NDU lattice, where the grid benchmark is dramatically faster. There is no matched experiment against a modern PINN policy-iteration method, DeepONet policy iteration, SOC-MartNet, sparse grids, or another competitive solver at a common error target.

**Required resolution:** add at least one nonlinear stochastic control problem in a dimension where an exhaustive tensor grid is no longer the obvious solution, with a credible independent reference or cross-method agreement. Report end-to-end time, memory, failure rate, and error at matched tolerances. The high-dimensional claim should be earned on a problem where the network is not simply representing an exact linear/quadratic family.

### R4-F6. The paper's strongest economic theorem is correct but too generic to carry the Econometrica contribution — major

Theorem 3 writes the objective as

[
V(k)=sup_pi {A(pi)-kB(pi)}.
]

Convexity and monotonicity in (k), and the ordering of optimal (B), follow from the supremum of affine functions plus the two optimizer inequalities. This is clean and correct. It is also a very general revealed-preference/envelope argument that does not depend on the neural method, the diffusion, or most of the economic structure.

The numerical panel confirms the theorem in the finite model, but the central policy is heavily constrained by the coarse action set: consumption is at its upper bound (c=.8) for all three reported (k)'s; (	heta=.2) is at its upper bound for (k=.5) and (k=2); and the reported central portfolio is .15 for every (k). The theorem concerns the discounted adjustment budget rather than pointwise (	heta), so this does not invalidate it. It does make the central quantitative example weak evidence for a rich endogenous-preference mechanism.

The utility normalization is cardinally fixed by assumption, the liquidation fee is imposed, and no primitives are estimated or disciplined by data. The paper is therefore not yet delivering a new quantitative economic result that could compensate for the absence of a numerical performance advantage.

**Required resolution:** either derive a substantially stronger economic implication tied to the stochastic preference mechanism and test it on a numerically resolved model, or present the adjustment theorem as a supporting lemma rather than one of three headline contributions. Robustness should include finer action sets and specifications in which the key controls are not mechanically at box constraints.

### R4-F7. The advertised recursive-utility and strategic-interaction scope remains mostly interface-level, not demonstrated NBO scope — major

The manuscript is much more honest than R3 about what is and is not implemented. That honesty should be preserved. But the title/abstract still invite a reader to view recursive utility and strategic interaction as demonstrated domains of the proposed method.

The recursive experiment solves a deterministic saving reference problem by scalar root finding; its central consumption fraction is at the lower grid bound .01. There is no trained recursive neural portfolio problem. The dynamic game is exact backward enumeration on 18 states per date; there is no neural best-response/MPE training. The trace calculation is an algebraic Monte Carlo check. These are useful regression tests for formulas and interfaces, but they do not establish that NBO solves the broader economic classes.

**Required resolution:** either execute at least one genuinely neural recursive-utility problem and one genuinely neural strategic-interaction problem, or narrow the evidentiary claims so that these sections are clearly mathematical extensions awaiting numerical validation. Breadth of notation is not the same as breadth of demonstrated method.

### R4-F8. The novelty comparison is already out of date for a September 2026 revision — major contribution concern

The manuscript now cites closer work than earlier versions, including neural policy iteration, HJB/DeepONet policy iteration, and SOC-MartNet. That is an important improvement. But the comparison is no longer current enough for a September 21, 2026 numerical-method claim.

In particular:

1. Kim, Cho, Kim, and Kim, **"Physics-Informed Approach for Exploratory Hamilton–Jacobi–Bellman Equations via Policy Iterations," AAAI 2026**, develops a mesh-free neural policy-iteration method with an explicit decomposition of iteration, policy-network, and PDE-residual errors and nonlinear/high-dimensional benchmarks.
2. Kim, Kim, Kim, and Cho, **"Physics-Informed Policy Iteration for High-Dimensional Hamilton–Jacobi–Bellman Equations: Interior Error Bounds without Boundary Data," posted August 18, 2026**, directly targets bounded-domain policy iteration and interior error control.
3. Cai, Fang, and Zhou's SOC-MartNet is now a published **SIAM Journal on Scientific Computing** article (2025), not merely an arXiv comparator, and reports stochastic-control tests at substantially higher dimensions.

These papers do not automatically dominate NBO; they do raise the bar. A new paper must state precisely what theorem, computational regime, economic structure, or certifiable quantity is unavailable in those methods and then demonstrate it.

**Required resolution:** update the literature through the revision date and provide a side-by-side contribution table covering evaluation equation, policy improvement mechanism, boundary treatment, error notion, action optimization, stochastic diffusion control, and demonstrated dimensions. The current "particular combination" argument is too weak without a numerical or theoretical advantage.

Relevant sources include:
- https://doi.org/10.1609/aaai.v40i27.39421
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7306930
- https://doi.org/10.1137/24M1681033
- https://doi.org/10.1016/j.neucom.2025.130515

### R4-F9. Reproducibility is improved, but the reviewable artifact is still incomplete — major for a numerical paper

The branch contains the executed source and a summary ledger, which is good. The README states that successful checkpoints, full raw arrays, training histories, timeout logs, and complete game profiles live in an accompanying review bundle rather than in the repository. That means the Git commit alone does not contain all artifacts underlying the reported training results.

The canonical Econometric Society-class build is also explicitly not verified in the available execution environment. A separate standard-class reading copy is not equivalent to a successful build of the authoritative entry.

Neither issue is a mathematical objection, but for a computational paper they matter. A referee should be able to pin the exact source, weights, raw outputs, and manuscript build to an immutable public artifact.

**Required resolution:** attach the complete successful-run artifacts to a versioned release or repository/LFS artifact with cryptographic hashes in the manifest, and make the canonical manuscript build pass in CI. The exact successful seeds should be rerunnable from that pinned artifact without relying on an external overlay whose persistence is unspecified.

### R4-F10. Three successful seeds are not yet a robustness study, particularly after a failed pilot and incomplete longer runs — major

The paper correctly reports the failed pilot and the two incomplete twelve-date attempts. That is commendable. But the successful evidence still consists of three seeds under one width, learning rate, actor-step count, critic-step count, grid, and six-date horizon.

There is no sensitivity table for width, optimization budget, learning rate, initialization, or actor/critic update imbalance. There is no success-rate study over a larger seed set. The successful six-date setup is also easier than the default twelve-date configuration, whose attempted runs did not complete their final audit under the available execution budget.

This is especially relevant because the finite benchmark is so cheap. When an exact reference is available in under one second, a numerical-method paper has the unusual luxury of being able to map the neural solver's robustness carefully. That opportunity should be used.

**Required resolution:** run a predeclared robustness panel over seeds and key optimizer hyperparameters, including the twelve-date configuration, and report failures as part of the method's cost. Do not select a success tolerance after observing the reference errors; justify the target economically or numerically.

## 4. Interpretation of the current R4 numerical claims

The following claims are supported by the current repository:

1. The R4 finite operator is internally consistent with its stated four-branch drift/covariance moments on the reported polynomial tests.
2. The exact finite NDU solver, independent policy evaluator, and PyTorch target operator agree on the tested finite operator.
3. The three delivered six-date neural policies have small value loss relative to the exact optimum of that same finite operator.
4. Policy-coordinate agreement can be poor even when finite-model value regret is small.
5. The adjustment-budget monotonicity theorem is valid under its stated fixed-feasible-set/fixed-settlement assumptions and is satisfied by the finite re-solves.
6. The corrected temporal-self and trace regressions evaluate the intended formulas.
7. The dynamic finite game and recursive reference calculations are legitimate reference computations of the limited models they declare.

The following stronger claims are **not** established:

1. that the NDU policy is accurate for the underlying continuous stopped diffusion;
2. that NBO provides a computational advantage over standard dynamic programming on the demonstrated nonlinear problem;
3. that the finite certificate can certify the paper's .05 target without access to the exact optimum;
4. that the method scales competitively to high-dimensional nonlinear economic control;
5. that recursive-utility or dynamic-game NBO training has been demonstrated;
6. that the adjustment-cost panel is a numerically resolved quantitative economic result for the continuous model;
7. that NBO offers a clear theoretical or empirical advantage over the closest 2025–2026 neural policy-iteration methods.

## 5. Conditions for a reconsiderable numerical-method submission

A future version should be organized around a small number of hard deliverables rather than a larger number of interface demonstrations.

**First, close the continuous-model error loop.** Choose one nontrivial stopped stochastic control problem and establish a converged/validated numerical reference. Refine time, state, action, quadrature, and boundary treatment jointly. Show that the economic quantities used in the paper stabilize.

**Second, make the actor step computationally meaningful.** Do not rely on exhaustive (n_a^m) action labels as the main mechanism in the experiment that is supposed to demonstrate scalability. If enumeration is retained, characterize honestly the class of problems for which it is affordable and measure the value of the neural compression.

**Third, demonstrate a regime in which NBO is competitive.** Use a nonlinear problem beyond two state variables, compare against at least one close neural policy-iteration/control method and an appropriate conventional benchmark, and match methods at the same value/policy tolerance. Report memory and failures as well as wall time.

**Fourth, make the certificate operational.** A computable bound that is an order of magnitude larger than the target error is not enough. Develop a sharper certificate or state clearly that exact-reference evaluation is the present validation mechanism.

**Fifth, strengthen the economic result.** Show that the principal comparative static survives numerical refinement and less corner-dominated action sets, and connect it to a nontrivial implication of endogenous stochastic preferences rather than only the generic monotonicity of an optimal adjustment budget with its linear price.

**Sixth, complete the artifact.** Pin weights/raw outputs, pass the canonical build in CI, and make the complete review package recoverable from immutable repository/release identifiers.

## 6. Recommendation

**Reject in its present form.**

This recommendation is materially different from the R3 rejection. R3 failed because several executed objects were mathematically different from the paper's stated objects. R4 fixes most of those correspondence failures. The current obstacle is that the corrected method has not yet earned its claimed numerical-method importance. Its only nonlinear trained application is a small finite lattice problem solved much faster by exhaustive dynamic programming; the continuum error is unresolved; the practical certificate is too loose; the high-dimensional evidence is structurally trivial; and the broader recursive/game scope remains untrained.

R4 should be treated as a technically serious foundation for a new numerical paper, not as a final validation package. A successful next version would need fewer demonstrations, but each would need to close the full chain from economic model to discretization to neural algorithm to independent accuracy/cost evidence.
