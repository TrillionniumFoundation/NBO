# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r2-2026-09-28`  
**Pinned revision commit:** `d9054ab6284369ccd6134286e9d2694e3621d562`  
**Pinned manuscript blob:** `d3261aaa857ce9bdc1c479cc3785711846a3f845` (`ECTA.tex`)  
**Pinned supplement blob:** `4e8f07484059e1a3d065717bf4d72120fad0c238` (`supp.tex`)  
**Report date:** 28 September 2026  
**Recommendation:** **Reject in the present form; do not invite another ordinary revision in the current round.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written in an Econometrica numerical-methods style. It is not a report commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

The revision is a serious and, in several respects, exemplary response to the September 15 report. The author has removed the most consequential false claims in the reviewed draft, separated policy evaluation from policy improvement, repaired the recursive-utility sign convention, stated boundary and utility-domain requirements, replaced the invalid viscosity-selection argument by a monotone Bellman route, corrected the portfolio arithmetic, and sharply improved the provenance of the numerical evidence. I independently reconstructed and executed the exact revision code. The 29 declared computations reproduce, and all eight regression tests pass.

Those achievements materially change my assessment of the manuscript's correctness. They do **not**, however, make the paper publishable as an Econometrica numerical-methods contribution. The central problem is now unusually clear: the revision describes a general neural numerical method, but it never actually applies that method to a nontrivial economic boundary-value problem.

Every reported calculation avoids the advertised generic neural approximation problem:

| Reported laboratory | What is actually computed |
|---|---|
| Merton and recursive-utility portfolios | Three scalar output parameters in an analytically invariant homothetic class |
| Nonsmooth exit problem | Direct finite-grid dynamic programming |
| Coupled LQ “scalability” | Exact Lyapunov policy evaluation and exact Riccati comparison in a quadratic class |
| Endogenous preferences | A finite-action, two-dimensional semi-Lagrangian grid reference |
| Temporal selves | A scalar analytical root and finite-duration deviation calculation |
| Dynamic Cournot | A static arithmetic diagnostic and gradient-routing test; no dynamic equilibrium computation |
| General multilayer NBO core | Derivative-routing unit tests only; no trained economic application |

This is not a semantic objection about labels. It prevents the paper from answering the numerical questions on which its contribution depends: whether the proposed block updates train reliably; whether generic networks attain useful value, derivative, boundary, and action-gap accuracy; whether the claimed certificates can be computed rather than merely assumed; whether the method improves on a direct neural HJB solve, deep Galerkin, deep BSDE, classical policy iteration, or structure-exploiting numerical methods; and whether the method scales in a genuinely coupled, nonlinear problem for which no exact matrix solve or low-dimensional grid is available.

The revision has therefore become a careful mathematical framework, implementation skeleton, and validation suite. That is valuable research engineering. It is not yet an Econometrica-level numerical-method paper. The missing evidence is not a modest extension that can be repaired by another textual revision. It requires a new computational study and, in my view, a substantially refocused paper.

## 2. What the revision successfully repairs

The report should not obscure the amount of real progress.

1. **The population objective is no longer internally inconsistent.** Equations `eq:criticloss` and `eq:actorloss` are block-specific, and the code enforces the intended stop-gradient graph. The old composite-loss counterexample is retained rather than hidden.

2. **Boundary conditions and utility domains are treated as part of the economic problem.** The manuscript distinguishes terminal, lateral stopping, and reflected boundaries; it no longer claims that a terminal architecture automatically handles all of them. The Epstein–Zin power domain is explicitly addressed.

3. **The viscosity claim is materially corrected.** The paper no longer identifies a small integrated differential residual or neural spectral bias with viscosity selection. The positive-weight Bellman construction and the wrong-limit exit example are useful.

4. **The finite-horizon and finite-state bounds are stated in economically interpretable terms.** Evaluation error, feasible-action gap, and boundary error are separated. This is much better than inferring optimality from optimizer stationarity.

5. **The numerical record is candid about approximation classes.** The manuscript repeatedly says that the portfolio and LQ calculations exploit exact structure, that the endogenous-preference calculation is a grid reference, and that the dynamic-game computation remains undone.

6. **The executable evidence is reproducible.** The current code, version pins, seed accounting, archived source, and regression tests are a large improvement over the original figures.

These changes eliminate most of the specific mathematical objections in the first report. My negative recommendation is based on what remains after those repairs, not on the superseded draft.

## 3. Blocking concerns

### B1. The paper does not execute the numerical method it proposes

The decisive issue is the absence of a single end-to-end experiment in which a nontrivial multilayer critic and actor are trained on an economic PDE, followed by independent evaluation of the quantities appearing in the paper's own theorems.

The general implementation in `revisions/2026-09-28/code/nbo_core.py` provides:

- exact automatic-differentiation jets for batch-separable networks;
- block-specific critic and actor losses;
- a hard-terminal wrapper;
- player-specific gradient routing;
- an independent-probe trace objective; and
- a finite-state Bellman certificate.

That is a useful core. But `experiments.py` does not import or exercise this general core. The portfolio code optimizes a log coefficient and two scalar action outputs. The LQ code calls `solve_continuous_lyapunov` and then sets `K = P`; it does not train a neural critic. The endogenous-preference computation uses `RegularGridInterpolator`, action enumeration, and backward induction. The remaining laboratories are analytical or diagnostic.

Consequently, the revision supplies no evidence about the numerical behavior of the advertised architecture. In particular, it does not report:

- convergence or failure rates for generic actor–critic training;
- sensitivity to network width, depth, activation, initialization, update ratio, or learning rate;
- held-out value, derivative, PDE, and boundary errors;
- independently maximized action gaps for a trained actor;
- extrapolation or coverage failures;
- conditioning of second derivatives;
- the effect of stochastic trace estimation on training;
- memory and runtime at a fixed economic error tolerance; or
- robustness across seeds, including failed runs.

A numerical-method paper cannot substitute graph-level unit tests and exactly representable special cases for a demonstration of the method. At minimum, the title, abstract, and contribution claims currently outrun the executed evidence.

### B2. The manuscript does not isolate a novel numerical contribution against appropriate baselines

The revised theory combines familiar ingredients: approximate policy evaluation and greedification, comparison-based residual bounds, contraction residual bounds for finite-state Bellman maps, and monotone-scheme convergence with a vanishing perturbation. The synthesis is careful and economically literate, but the paper does not establish that this combination yields a method that is materially different from, or better than:

- classical policy iteration or Howard improvement;
- a direct neural HJB method that eliminates the actor by the same feasible maximization routine;
- deep Galerkin or related neural PDE residual methods with explicit boundary losses;
- deep BSDE methods where applicable;
- semi-Lagrangian or monotone finite-difference methods;
- fitted value iteration or approximate policy iteration; or
- structure-exploiting projection methods used in computational economics.

The paper itself acknowledges several of these connections, but no controlled comparison is executed. Without such a comparison, the reader cannot tell whether the separate actor is useful, harmful, or simply an alternative parameterization of a maximization already performed to calculate the action gap.

A publishable numerical paper needs a contribution-isolating design. The same problem, domain, action constraints, function class, random seeds, compute budget, and stopping criterion should be used across methods. The comparison must report value and policy error, boundary error, feasible-action gap, failures, wall time, and memory at matched accuracy. At present there is no empirical basis for a numerical-method claim.

### B3. The proposed certificates are non-operational in the regime that motivates the paper

The principal continuous-time bound assumes uniform control of the policy-evaluation residual and the feasible-action gap over the verification domain. The coverage subsection correctly notes that a sampled mean residual is insufficient and offers conditional fill-distance and Lipschitz arguments. But the manuscript does not provide a practical, scalable way to obtain the constants or upper bounds needed for a generic high-dimensional network.

This is not a technical footnote. The acceptance criterion in Algorithm 1 depends on these quantities.

For a trained network, the paper must explain and demonstrate how to compute credible upper bounds on:

1. the residual over a continuous state-time domain;
2. the boundary error on every relevant boundary face;
3. the global feasible-action gap, including binding constraints; and
4. the interpolation, action-discretization, and time-discretization errors connecting the certificate to the continuous control problem.

Trying many validation states or local deviations gives lower bounds on missed violations, not upper bounds on the global errors. A fill-distance certificate becomes exponentially expensive with dimension unless additional structure is exploited. A Lipschitz constant estimated from samples is not a certificate. A global action solver may itself be as hard as the original Hamiltonian problem.

Likewise, Theorem `thm:viscosity` assumes `delta_h + epsilon_h = o(h)`. No training result establishes this rate, and none of the generic neural experiments needed to study it is present. The theorem is a conditional perturbation result, not an analysis of the proposed optimizer. That distinction should be central rather than left for the reader to infer.

### B4. The endogenous-preference “reference” is dominated by arbitrary action truncation

The endogenous-preference calculation is presented honestly as a finite-action reference, but even in that role it is currently too weak to support the surrounding application.

The baseline action set is

- `c/X ∈ {0.02, 0.05, 0.10}`,
- `p ∈ {0, 0.375, 0.75}`, and
- `theta ∈ {-0.15, 0, 0.15}`.

At the reported center state, the selected action is `(0.10, 0.75, -0.15)`: every component is on the boundary of the declared action grid. This is an immediate warning that action truncation, rather than the economic optimum, may be determining the result.

I reran the exact same positive-weight grid algorithm while changing only the finite action set. On the coarser `17 × 25` state grid with 20 time steps and `k = 1`, I obtain:

| Action set | Number of actions | Center value | Center action |
|---|---:|---:|---|
| Revision baseline | 27 | `-11.9152112208` | `(0.10, 0.75, -0.15)` |
| Expanded adjustment grid | 63 | `-10.6081194696` | `(0.10, 0.75, -0.45)` |
| Expanded consumption, portfolio, and adjustment grids | 175 | `-4.8410081366` | `(0.30, 1.50, -0.45)` |

The same qualitative result appears on the finer `25 × 37` grid with 40 time steps:

| Action set | Center value (`k = 1`) | Center action |
|---|---:|---|
| 27 actions | `-11.8667684766` | `(0.10, 0.75, -0.15)` |
| 63 actions | `-10.5395482986` | `(0.10, 0.75, -0.45)` |
| 175 actions | `-4.8394619790` | `(0.30, 1.50, -0.45)` |

These wider grids do not by themselves define the economically correct continuous-action problem; they deliberately change the finite approximation. They do prove, however, that the reported reference is strongly action-bound and that no continuous-action conclusion, reliable policy reference, or meaningful NBO error comparison can be based on it without an action-domain justification and action-coverage error analysis.

This matters beyond one table. The paper's theoretical emphasis is precisely on an **upper bound** for the feasible-action gap. The main economic reference does not calculate such a bound and visibly chooses truncation endpoints. A revised computational study must specify economically defensible compact action domains, establish that they are not artificially binding, refine the action grid, and report an action-discretization or global-maximization error.

### B5. The LQ experiment is a classical exact policy-iteration identity, not evidence of neural scalability

The coupled LQ problem is a better test than the separable benchmark in the original draft, and the noncommuting dense matrices eliminate a trivial coordinate decomposition. But the computation still does not test the claimed method.

For each policy matrix `K`, the critic is obtained by an exact dense Lyapunov solve. Policy improvement then sets `K = P` exactly. The reference is an exact algebraic Riccati solve. The fact that the iteration reaches machine precision in six steps through dimension 50 is a useful algebraic regression test. It says essentially nothing about:

- neural approximation error;
- stochastic optimization;
- Hessian estimation;
- state-space sampling;
- verification coverage;
- boundary handling;
- nonquadratic policies;
- memory scaling of automatic differentiation; or
- performance relative to a strong numerical baseline at fixed accuracy.

Calling this a quadratic-neural class does not change the computation actually performed. Any positive semidefinite quadratic can be represented by a suitable network, but the code does not train that representation. The numerical procedure is an exact matrix method.

The LQ section should therefore be treated as a correctness check, not a scalability result. A genuine scaling experiment needs a coupled, nonquadratic problem for which the solution is not recovered by a Riccati or Lyapunov routine and for which a generic neural approximation is actually optimized.

### B6. The principal economic extensions are specified but not numerically delivered

The manuscript ranges across endogenous preferences, temporal selves, recursive utility, dynamic games, constrained portfolios, viscosity solutions, and high-dimensional diffusion traces. The breadth makes the paper appear more complete than its numerical evidence.

- The endogenous-preference model receives a small finite-action grid reference, but no NBO fit and no error comparison.
- The temporal-self example is a one-dimensional homothetic analytical calculation, not a trained multi-critic NBO.
- The dynamic Cournot model receives no dynamic Markov-perfect equilibrium computation at all.
- The recursive-utility calculation is exactly representable by a scalar homothetic coefficient.
- The trace estimator is not used in any trained economic experiment.

The paper must either narrow its claims to the framework and the few calculations actually completed, or carry at least one of these applications through to a convincing numerical solution. For Econometrica, an economic application cannot remain mainly a list of equations and future comparison requirements.

If the dynamic-game section is retained as a contribution, the paper needs an actual dynamic equilibrium computation with independent best-response solutions or certified unilateral exploitability over the verification domain. The static Cournot counterexample and gradient test are necessary safeguards, not a result on the stated dynamic game.

### B7. The revision is too broad for the depth of result it currently provides

The revised manuscript is intellectually more disciplined than the original, but it still tries to be simultaneously:

- an actor–critic method paper;
- a verification-error paper;
- a viscosity-scheme paper;
- a recursive-utility paper;
- an endogenous-preference application;
- a time-inconsistency paper;
- a dynamic-game paper;
- a scalability paper; and
- a stochastic-trace paper.

Each component is plausible in isolation. The combination has not yet produced one deep theorem–algorithm–experiment chain. The current paper often states the right condition, explains why an earlier shortcut was wrong, and then stops before demonstrating that the condition can be met in the target computation.

For a top journal, the paper should select a narrower contribution and complete it. One viable route would be a rigorous approximate-policy-iteration paper with computable certificates and two demanding economic applications. Another would be a focused numerical paper on recursive utility and endogenous preference formation, with a complete solver comparison and error study. The present omnibus format dilutes both novelty and evidence.

## 4. Major technical and implementation concerns

### M1. The continuous-time verification theorem is useful but highly conditional

Theorem `thm:verification` assumes a bounded smooth candidate in an invariant utility interval, an admissible Markov policy, uniform residual and action-gap bounds, bounded boundary error, exact reflected conditions, and comparison for the relevant HJB and fixed-policy problems. Under these assumptions the barrier argument is credible. But many applications motivating the paper involve unbounded wealth, degenerate diffusion, nonsmooth constraints, or recursive utility where comparison and invariant-domain arguments are substantive.

The paper should identify, application by application, which hypotheses are actually verified and which are imposed only for a bounded validation problem. A general theorem whose assumptions contain the difficult well-posedness and uniform-error work cannot be presented as a ready-made certification method without a computational route to verify them.

### M2. The viscosity theorem does not analyze the learned algorithm

Theorem `thm:viscosity` is best understood as stability of an exact monotone scheme under a vanishing neural perturbation. It does not show that the block optimizer produces such perturbations, that its iterates remain in the invariant domain, or that the policy implementation converges as a controlled process. The proof appropriately acknowledges some of this, but the contribution should be positioned with greater precision.

The paper should separate:

1. convergence of the exact monotone state/action discretization;
2. approximation of its fixed point by a neural representation;
3. optimization error from the training algorithm;
4. maximization and action-discretization error; and
5. conversion from discrete policy arrays to continuous-time controlled payoffs.

At present these layers are compressed into `delta_h + epsilon_h = o(h)`.

### M3. The repository does not implement the full acceptance procedure described in the paper

The general `critic_loss` contains no generic boundary loss `L_B`. The repository supplies a hard-terminal wrapper, but no reusable lateral Dirichlet lifting, reflected-boundary penalty or exact construction, domain-invariance check, global action-gap solver, fill-distance computation, or certified residual upper bound. These omissions are acceptable for a minimal core, but not if the code is presented as an implementation of Algorithm 1's acceptance criterion.

The implementation should return a structured certificate with clearly separated:

- representation/training residual;
- boundary error by face;
- maximization or action-net error;
- state-space coverage term;
- time and state discretization error;
- policy-value and optimal-value bounds; and
- assumptions that remain unchecked.

### M4. The stochastic-trace result is disconnected from the experiments and tests

The independent-probe product correctly removes the single-bank variance term in the population squared residual under the stated conditional-independence assumptions. But the estimator can be negative and high variance, and the paper provides no training experiment that uses it.

Moreover, the regression acceptance flag in `experiments.py` does not test the Monte Carlo trace estimates against a declared tolerance, and `test_revision.py` does not exercise `independent_probe_loss`. This makes the trace section a mathematical aside rather than validated method functionality. Either integrate it into a real experiment with variance, gradient, and convergence diagnostics, or remove it from the central contribution.

### M5. Reproducibility is improved, but the durable evidence package is incomplete

The exact code and compressed summary are committed, and the computations can be regenerated. That is good. However, the repository does not contain the raw NPZ arrays and seed traces referenced by the tests and manuscript; the revision README refers to a “complete conversation package.” A private or conversational attachment is not an adequate long-term research artifact.

The final package should provide a durable archive or release, ideally with content hashes and a persistent identifier, containing:

- every raw array and iteration trace used in tables;
- stdout/stderr logs;
- environment lock data;
- compiled manuscript artifacts if relevant;
- all failed and excluded runs;
- machine and timing metadata; and
- an exact source commit.

At the time of this review, the revision commit also had no remote workflow run or status check visible. My independent local reproduction mitigates concern about the current code, but a permanent CI record would strengthen the package.

### M6. The method's name and operator interpretation need sharper definition

“Neural Bellman Operators” suggests that the paper introduces a specific learned operator or operator approximation. In the revision, the central objects are instead a block-specific actor–critic procedure and, separately, a classical positive-weight Bellman operator used for certification and viscosity selection. The relationship between these two components is not fully operationalized.

The paper should state exactly:

- which map is the NBO;
- its domain and codomain;
- whether it is learned, analytically defined, or discretized;
- how one iteration differs from approximate policy iteration;
- which properties are new;
- which properties come from the underlying monotone scheme; and
- how the differential actor–critic implementation is connected to the finite-state operator in actual code.

Without this, “operator” risks functioning as a broad label rather than a mathematically distinctive algorithmic object.

## 5. Numerical program required for a potentially publishable new paper

I would not recommend another conventional revision that merely adds discussion or one more special-case table. A credible new submission should contain a substantially new numerical program. At minimum:

### 5.1 One complete low- or moderate-dimensional nonlinear benchmark

Use a genuinely nonlinear economic control problem with an accurate external reference. Train the generic multilayer actor and critic end to end. Report:

- value and policy error on dense held-out grids;
- derivative error where available;
- boundary error by boundary face;
- independently computed feasible-action gaps;
- seed-by-seed histories and failures;
- sensitivity to architecture and update ratios; and
- ablations for joint loss versus block-specific updates.

The reference and the NBO must solve the same problem, with the same horizon, boundary data, utility normalization, and action domain.

### 5.2 One genuinely high-dimensional, coupled, nonquadratic problem

The problem should not reduce to Riccati, Lyapunov, separable one-dimensional components, or an exact invariant parametric family. It should exercise the claimed advantages of automatic differentiation and neural representation. Report fixed-accuracy scaling, not only dimension-dependent wall time:

- accuracy target;
- achieved residual, boundary, and action-gap errors;
- samples and optimization steps;
- memory and runtime;
- Brownian rank and covariance handling;
- failures and confidence intervals; and
- comparison with the strongest feasible alternative.

### 5.3 Matched baselines

At least the following should be considered:

- direct neural HJB with the same network and action solver;
- classical policy iteration or semi-Lagrangian dynamic programming;
- DGM or another neural PDE baseline;
- deep BSDE where structurally applicable; and
- an economics projection method exploiting the same known structure.

All methods should receive comparable tuning effort and computational budgets. Do not compare an exact-structure NBO to an intentionally unstructured baseline.

### 5.4 Operational certificates

Demonstrate how the paper's errors are upper-bounded in practice. Depending on the problem, this might use:

- interval or branch-and-bound maximization over actions;
- concavity and duality gaps;
- certified action nets;
- Lipschitz bounds obtained from network weights;
- domain decomposition and interval arithmetic;
- residual adversarial search followed by local certification; or
- a posteriori numerical-analysis estimates.

An empirical maximum over random points should be labeled as such, not inserted into a theorem requiring a uniform bound.

### 5.5 Action and domain sensitivity

For every constrained application:

- justify compact action bounds economically;
- report how often the solution lies on each bound;
- expand the bounds and refine the action grid;
- quantify the action-coverage error;
- vary the state domain and boundary placement; and
- show that the substantive conclusions are stable.

The endogenous-preference reference fails this test in its current form.

### 5.6 A complete dynamic-game calculation if that application is retained

Compute a dynamic Markov-perfect equilibrium for the stated capital game. For each player, solve or bound the fixed-rival best response and report a unilateral exploitability map. Include asymmetric initializations, boundary actions, and both market-size normalizations only if their economic comparison is explicit.

### 5.7 Durable reproduction archive

Commit or release the raw results, not only a compressed summary and references to a conversation attachment. The archive should be sufficient for a third party to regenerate every reported table and figure from the pinned source.

## 6. Additional comments

1. The manuscript should distinguish “the theorem provides a bound if uniform errors are known” from “the algorithm computes a certificate.” These are presently too easy to conflate.

2. The exact-representation portfolio and LQ calculations should be called unit or integration tests throughout, not empirical validation of generic approximation.

3. The NDU tables should report the frequency of each boundary action and the value change under action-set expansion before any policy interpretation is offered.

4. The temporal-self example is a useful derivation but does not validate a multi-critic neural computation. It belongs either as an analytical example or must be complemented by an actual trained problem.

5. The dynamic-game section should not count the static `1/3`, `1/4`, and `1/64` arithmetic as a numerical application.

6. The paper should report confidence or repeated-run variation for every stochastic numerical result. Machine-level agreement in deterministic exact-structure tests is not a substitute.

7. The exact computational domain used for every residual, boundary, and action-gap statement should appear in the corresponding table.

8. A numerical-method paper should explain failure modes. The present primary suite records 29 accepted computations and no failed final runs, but most are deterministic or exactly representable. Generic training will have failures that need to be measured rather than engineered away from the test set.

9. The literature discussion should more directly compare the proposed procedure to approximate policy iteration and actor–critic methods with separate evaluation and improvement. The claimed novelty cannot rest mainly on correcting an invalid joint objective.

10. The paper's unusually candid limitations are a strength. They should now be used to narrow the contribution rather than surrounded by a title and abstract that imply the missing general solver evidence already exists.

## 7. Independent reproduction record

I reviewed the exact R2 source pinned above and independently reconstructed the following files from the repository:

- `ECTA.tex`;
- `supp.tex`;
- `revisions/2026-09-28/code/experiments.py`;
- `revisions/2026-09-28/code/nbo_core.py`; and
- `revisions/2026-09-28/code/test_revision.py`.

The reconstructed Python-source SHA-256 values matched those recorded in `LOCAL_VALIDATION.json`. Using the pinned NumPy, SciPy, and PyTorch versions, I independently reproduced:

- all nine portfolio and recursive-utility scalar calibrations;
- all fifteen coupled LQ runs for dimensions 2, 5, 10, 20, and 50;
- both endogenous-preference grids for both cost values;
- the nonsmooth exit diagnostic;
- the temporal-self calculation;
- the scalar regression diagnostics; and
- all eight repository regression tests.

The primary declared count of 29 completed computations is therefore reproducible from the present source. This supports the reliability of the revised record. It does not address the substantive concern that the record contains no generic neural economic solve.

I also executed the action-set sensitivity check described in B4. The diagnostic script and machine-readable output are committed beside this report. Those checks preserve the revision's state grid, time discretization, transition interpolation, boundary treatment, utility, and model parameters; only the finite action set is changed.

## 8. Recommendation

The author has transformed an unreliable draft into a much more honest and mathematically coherent manuscript. The response to the previous report is unusually thorough, and the executable revision is reproducible. I commend that work.

Nevertheless, the paper does not yet meet the standard of an Econometrica numerical-methods contribution. It proposes a generic neural method but supplies no nontrivial execution of that method; its principal certificates are not operationally demonstrated; its strongest “scaling” result is an exact matrix calculation; its principal economic grid reference is strongly action-bound; and the dynamic-game application is not computed.

I therefore recommend **rejection in the present form and no further ordinary revision in this submission round**. A future paper could be worth serious consideration after a fundamentally new numerical study establishes what the method can solve, how its certificates are computed, and how it compares at matched accuracy with strong alternatives. That would be a new research contribution rather than another repair of the current manuscript.
