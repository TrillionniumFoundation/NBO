# Referee Report on “Neural Bellman Operators” — R6

**Venue perspective:** *Econometrica*, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r6-2026-09-29`  
**Pinned revision commit:** `01f4e00a33d9ae29142c8e49bd3c7ec107806796`  
**Pinned tree:** `4097228167e8b84e18f6b988c6d3cc03a17f6de3`  
**Main manuscript:** `ECTA.tex`, git blob `83a195c4b0dbde3b8aa356a5c83d143db3efa298`  
**Supplement:** `supp.tex`, git blob `b8b950657f4f4082353993e2b85e11168c55904f`  
**Report date:** 29 September 2026  
**Recommendation:** **Reject in the present form; encourage a substantially narrower and newly executed resubmission.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from the perspective of an Econometrica numerical-methods referee. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R6 is a genuine and substantial revision. The decisive criticism in my previous report—that the paper proposed a generic neural method without ever executing that method on a nontrivial economic boundary-value problem—no longer applies in that form. The author now trains actual multilayer critics and actors, preserves unfavorable runs, adds a direct-HJB comparator, supplies a one-dimensional continuous-domain interval verification, trains the endogenous-preference model on the stated finite economy, replaces the quadratic “scaling” claim by a nonlinear coupled-capital experiment, and computes dynamic fixed-rival best responses in a finite Cournot game. The exact-source workflow, raw weights, histories, certificates, and PDFs are materially better than the evidence available in R2.

The stopped-consumption experiment is the strongest new result. It provides a coherent theorem–algorithm–experiment chain: a nonhomothetic control problem, generic multilayer networks, independent closed-action maximization, exact boundary lifting, and an outward-rounded subdivision calculation that encloses the residual and action gap over the full one-dimensional state interval. I independently reran the training and interval verifier. All three NBO and all three direct-HJB runs met the declared full-domain thresholds; all three joint-loss ablations failed by a large margin. This is a useful and credible proof of concept.

The revision nevertheless does not yet establish an Econometrica-level numerical-method contribution. The positive certified chain is confined to one state variable, an analytically solvable Hamiltonian maximization, and a custom interval routine whose complexity is exponential under direct extension. In the first substantive two-state economic application, every final NBO seed misses the declared policy-regret target, while the direct Bellman comparator passes comfortably. In the coupled nonlinear capital experiment, NBO is not more accurate or robust than the direct comparator; two of three twenty-dimensional NBO runs fail the stated diagnostic target, and small residuals on the fitted box coexist with economically large critic-versus-simulated-payoff discrepancies. The dynamic Cournot calculation is a finite-grid dynamic-programming result, not a neural NBO result and not a continuous-game error bound.

The paper is therefore now a careful framework, a strong scalar verification example, and a candid collection of positive and negative diagnostics. What remains missing is a deep numerical result showing when the explicit actor–critic construction delivers something that a direct Bellman/HJB method or a strong classical method does not, together with an operational error account on the economically relevant multidimensional problem. That missing contribution requires more than another textual revision.

## 2. What R6 successfully resolves

The following changes are substantive and should be retained in any future version.

1. **A real multilayer NBO is finally executed.** The stopped-consumption experiment trains two-hidden-layer critics and actors without fitting reference values or policies. The NDU and coupled-capital studies also use generic networks rather than exact homothetic or quadratic parameterizations.

2. **The computational object is now specified honestly.** The implemented map records the model, policy class, network class, sampling stream, boundary realization, and verification output. The manuscript correctly identifies the procedure as an approximate-policy-iteration construction rather than a new principle of optimality.

3. **The scalar continuous-domain certificate is operational.** The interval program propagates value, first derivative, second derivative, and actor enclosures through stored binary64 weights; it covers every dyadic leaf of the state interval and maximizes over the closed consumption set. The resulting welfare bound does not use the reference-grid error.

4. **The finite-state error accounts are computed rather than inferred from training loss.** In the NDU experiment, evaluation errors, action gaps, boundary terms, policy values, and exact finite-model regrets are evaluated over all grid states, times, and 175 actions.

5. **Failures are preserved.** Joint differentiation fails in the scalar experiment; the pilot NDU classifier fails; all final NDU actor runs miss the policy-regret target; and two twenty-dimensional NBO runs miss the coupled-capital diagnostic target. This is much stronger scientific practice than the original draft.

6. **The dynamic-game distinction is repaired.** The revision computes a finite dynamic Cournot profile and then solves each fixed-rival best-response problem separately. It no longer substitutes the static `1/64` diagnostic for a dynamic computation.

7. **The evidence chain is unusually transparent.** R6 commits materialized source, package versions, raw weights, arrays, optimization histories, failed outcomes, generated tables, compiled PDFs, and exact-source workflow metadata. I reproduced the twelve R6 regression tests and the principal calculations described below.

These changes eliminate most of the correctness and provenance objections in the earlier report. My negative recommendation rests on the remaining contribution and external-validity issues.

## 3. Blocking concerns

### B1. The paper still does not isolate a numerical advantage or distinct capability of NBO

The revision now includes the right direct comparator, but the comparison does not establish a reason to prefer the explicit actor–critic construction.

- In stopped consumption, NBO and direct HJB both attain value errors on the order of `10^{-4}` to `10^{-3}` and essentially the same conservative welfare bound. Depending on seed and closure count, either method can be faster or more accurate.
- In NDU, direct Bellman fitting is materially better. The final repository table reports NBO finite-model policy regrets of `0.1656`, `0.1487`, and `0.1014`, versus approximately `0.026` for all direct runs.
- In the coupled-capital experiment, direct HJB has zero actor-approximation gap by construction, similar or lower residuals, no failures at dimension twenty, and generally smaller critic-versus-policy-payoff discrepancies.

The paper appropriately does not claim universal superiority. But once that claim is removed, the contribution needs another basis. The current theoretical ingredients—policy evaluation, greedification, residual comparison bounds, finite-state contraction accounts, and monotone-scheme perturbation—are established numerical-analysis and approximate-policy-iteration ingredients. The revision combines them carefully, but it does not show that the explicit neural actor enables a problem, accuracy level, constraint treatment, or computational regime unavailable to direct maximization.

For an Econometrica numerical-method paper, the reader needs a contribution-isolating result. A future paper should identify a setting in which direct Hamiltonian maximization is genuinely difficult or unavailable, show that the actor makes the computation feasible, and compare accuracy, failures, runtime, and memory against strong alternatives at a common economic error target. Otherwise the NBO actor is an additional approximation layer that the present experiments mostly show to be costly.

### B2. The only full economic certificate is one-dimensional and problem-specific

The scalar certificate is the strongest part of R6, but its scope is much narrower than the paper's general agenda.

The verifier benefits from all of the following special features:

- one continuous state variable;
- a compact interval with exact Dirichlet lifting;
- an action Hamiltonian with a closed-form global maximizer;
- a width-16 tanh network small enough for interval subdivision;
- a residual tolerance that can be reached after roughly six to eight thousand leaves; and
- no state-dependent action set, reflection, correlated multidimensional boundary, or high-dimensional coverage problem.

The reported regret bound is approximately `0.05`, whereas the reference value errors are around `3×10^{-4}` to `6×10^{-4}`. The bound is valid under the stated contract, but it is two orders of magnitude looser than the observed error and its economic meaning is not calibrated. More importantly, the same method is not demonstrated in the two-state preference model, the coupled-capital model, or the game.

The manuscript is candid that direct interval subdivision does not avoid dimensional complexity. That candor does not solve the contribution problem. If the main claim is a general economic error account, the paper needs at least one nontrivial multidimensional example in which the account is operational beyond sampled diagnostics. Alternatives could include verified domain decomposition, monotonicity/convexity structure, certified neural relaxations, probabilistic bounds with explicit coverage assumptions, or a posteriori finite-element/finite-difference comparison. Without such an extension, the title and breadth should be narrowed around the scalar certified experiment and finite-state accounting.

### B3. The endogenous-preference NBO fails its own policy criterion and is platform-sensitive

The NDU experiment is the most relevant test of the advertised actor–critic architecture because it has two states, three controls, reflection, stopping, and 175 actions. Its result is negative.

The final repository table reports:

| Method | Seed | Finite-model value error | Finite-model policy regret | Declared regret target |
|---|---:|---:|---:|---:|
| NBO | 11 | 0.1679 | 0.1656 | 0.1 |
| NBO | 29 | 0.1495 | 0.1487 | 0.1 |
| NBO | 47 | 0.1572 | 0.1014 | 0.1 |
| Direct Bellman | 11–47 | 0.106–0.134 | 0.026–0.027 | 0.1 |

Thus all three NBO seeds miss the policy-regret target, while every direct run passes. The NBO time-zero certificate is also very loose (`2.85` to `3.40`) relative to the realized finite-model regret.

I reran the exact committed source with the same Python, NumPy, SciPy, and PyTorch versions on another Linux CPU environment. The qualitative conclusion was unchanged, but the NBO regrets changed materially to approximately `0.2002`, `0.1075`, and `0.1224`; the direct regrets remained about `0.026`. This matters for two reasons. First, the failure is robust. Second, the manuscript's statement that the implementation is deterministic with a fixed sampling stream needs a platform qualification: deterministic source, seeds, and package versions do not yield numerically identical L-BFGS paths across the recorded CPU/BLAS environments.

The correct conclusion is not that the NDU experiment should be removed. It is an informative negative result. But it cannot support the method as a successful economic application. A future study needs a better actor representation or optimization scheme, a predeclared cross-platform tolerance protocol, and an explanation of when a categorical actor is preferable to enumerating the same finite action set.

### B4. The high-dimensional experiment measures local residual fitting, not value accuracy or scalability

The dense nonlinear capital experiment is a substantial improvement over the former exact LQ calculation. It actually trains generic networks and exposes failures. Its results, however, do not validate high-dimensional economic accuracy.

The principal table uses 512 held-out points in `[0,1]×[-.5,.5]^d` and declares success from residual RMS at most `.025` and queried action gap at most `.01`. At dimension twenty, two of three NBO seeds fail, while all direct-HJB seeds pass. More importantly, even runs that pass this diagnostic can have large disagreement between the initial critic and the independently simulated policy payoff.

In my exact-source rerun:

- at `d=10`, NBO residual RMS values were approximately `.014`–`.019`, yet the 80-step simulated payoff differed from the initial critic by about `.089`–`.122`, or roughly 22–31 reported Monte Carlo standard errors;
- at `d=20`, the NBO discrepancies were approximately `.097`, `.165`, and `.471`; the last is more than 130 reported standard errors;
- direct HJB also showed substantial discrepancies, though generally smaller.

These discrepancies are not automatically critic errors: the paths leave the fitted box, Euler time discretization is biased, and no exact high-dimensional value is available. That is precisely the point. The sampled residual target is not an economic accuracy criterion, and the experiment cannot be called a scaling success. It demonstrates the coverage problem identified by the paper's own theory.

A convincing high-dimensional result must close this loop. It should train on a domain connected to the actual path distribution and relevant counterfactuals, measure exit/coverage rates, control simulation bias, and report a value or welfare comparison whose uncertainty includes time discretization and approximation error. Alternatively, it should provide a certified local statement and avoid global scalability language.

### B5. The dynamic Cournot calculation is not evidence for the neural method

The revised game computation is correct in conception: it solves a finite positive-weight dynamic game, records missing pure equilibria, and independently recomputes each player's dynamic best response after fixing rivals. I reproduced the six principal finite-game cases and the reported zero finite-grid exploitability.

This result is nevertheless orthogonal to the main numerical-method claim. It uses direct grid interpolation, pure-action enumeration, and backward induction; no neural critic or actor is trained. Zero exploitability applies only to the specified finite state/action/time game. The continuous-state/action equilibrium error is explicitly `null`, and the coarse/fine tables do not provide a convergence rate or error bound.

The game section can remain as an illustration of the paper's error-accounting discipline, but it should not be counted as evidence that NBO solves strategic economic models. If strategic interaction is a principal contribution, the paper needs either a trained neural game with independent exploitability bounds or a rigorous continuous-to-discrete convergence study for the finite solver.

### B6. The baseline study is still too narrow for the venue

R6 adds the most important comparator—direct neural HJB with the same critic and maximization routine—and an upwind reference for the scalar problem. This is progress. It is not yet a broad numerical-method evaluation.

The study should include, where applicable:

- classical Howard or modified policy iteration on the same discretization;
- a strong monotone/semi-Lagrangian method using the same economic domain and actions;
- a genuine DGM-style architecture rather than only a plain-MLP residual fit;
- a deep-BSDE or probabilistic solver on a problem where that formulation is natural;
- structure-aware projection or sparse approximation baselines used in computational economics; and
- matched-accuracy runtime and memory, not only fixed-update diagnostics.

The relevant comparison is not whether each method can reduce a training residual. It is the cost and failure rate required to reach a common value, policy, welfare, or exploitability tolerance. At present, the direct comparator is at least as good in every substantive application, and the paper does not establish a separate empirical advantage.

### B7. The paper remains too broad relative to its completed result

The manuscript still combines:

- actor–critic differentiation;
- approximate-policy-iteration error accounting;
- viscosity selection;
- interval verification;
- recursive utility;
- endogenous preferences;
- sophisticated temporal selves;
- dynamic games;
- stochastic Hessian traces; and
- high-dimensional scaling.

The common language of evaluation and improvement is useful, but breadth is not a substitute for one deep result. The strongest publishable core is now much clearer: a block-specific neural policy-iteration method, a scalar full-domain verification, and finite-state error accounts with honest negative examples. The remaining applications could be shortened or moved to a separate computational appendix unless they are developed to the same theorem–algorithm–evidence depth.

For Econometrica, I would prefer a narrower paper that fully establishes one economically important multidimensional application, rather than a long manuscript in which many sections primarily document what has not been certified.

## 4. Major comments

### M1. Recast the interval result as a conditional verified enclosure, not an independently certified theorem of execution

The custom interval code is carefully written and passed the supplied derivative, transcendental, and cover tests. I did not find a simple counterexample in the reviewed arithmetic path. The manuscript also correctly states that it is not a formal machine proof.

That limitation should be made more prominent wherever the phrase “full-domain certificate” appears. The conclusion is conditional on the implementation of outward rounding, dot-product error bounds, transcendental remainders, absence of flush-to-zero, and the stored binary64 interpretation. A future version should cross-check the result with an independent interval package or proof assistant, or supply a small formally verified kernel. The current self-verification is strong evidence, but not independent certification.

### M2. Define reproducibility at the level actually obtained

The exact-source workflow is excellent, but R6 should distinguish:

1. source reproducibility;
2. package-version reproducibility;
3. bitwise numerical reproducibility; and
4. qualitative/threshold reproducibility.

My NDU rerun used the same named package versions yet produced materially different seed-level regrets, while preserving the same pass/fail pattern. Record the BLAS backend, compiler, CPU instructions, thread settings, deterministic-algorithm flags, and tolerance expectations. “Deterministic with a fixed sampling stream” is too strong without those qualifications.

### M3. Report target selection and robustness more explicitly

The bootstrap source fixed the principal thresholds before the remote evidence commit, which is good. The paper should say this directly and explain the economic scale of `.1` NDU regret, `.025` residual RMS, `.01` action gap, and `.05` scalar regret bound. Targets that are only numerical conveniences should not be described as economically meaningful accuracy levels.

### M4. Keep every continuous/discrete bridge visibly conditional

The revised bridge proposition and finite-horizon accounts are correctly conditional. Preserve the distinctions among:

- differential residual;
- scheme residual;
- action-net coverage;
- state/time discretization;
- neural representation/optimization;
- boundary realization; and
- embedding a discrete policy in continuous time.

In particular, the NDU and Cournot certificates are finite-economy statements. Their continuous-control and continuous-state errors must remain unavailable rather than being inferred from refinement tables.

### M5. The coupled-capital payoff diagnostic needs a designed error decomposition

The current Monte Carlo check mixes at least four quantities: critic error, policy-evaluation error, Euler bias, and state-domain extrapolation. Report the fraction of paths outside each training box, use paired paths and multiple time steps to estimate weak-discretization bias, and evaluate the fixed learned policy with a separate critic or numerical method where possible. The wide-domain follow-up is useful, but it should be organized as a predeclared coverage experiment rather than a collection of post hoc diagnostics.

### M6. Compare computational work at matched accuracy

Equal L-BFGS iteration caps do not imply equal work, as the manuscript notes. The next study should report function/gradient/Hessian-vector evaluations, closure counts, memory, and wall time to a common accepted economic tolerance. The interval-verification cost should be included in the total cost of a certified answer.

### M7. Separate mathematical synthesis from genuinely new results

The manuscript now acknowledges approximate policy iteration and inherited monotone-scheme arguments. Continue this separation. State precisely which theorem, bound, verifier, or algorithmic design is new, and which is an application or recombination of standard comparison/contraction arguments. This will make the contribution easier to assess and reduce the impression that the name “Neural Bellman Operator” is doing conceptual work that belongs to familiar Bellman and policy-iteration maps.

### M8. Tighten the main text

The 43-page main paper plus 18-page supplement remains long for the depth of the central result. The archival history, superseded counterexamples, exact LQ checks, temporal-self algebra, trace variants, and some game sensitivities can be moved to a replication appendix. The main paper should lead with one economic problem, one method, one operational error account, and one matched comparison.

### M9. Freeze the candidate before the review run

The final reviewed commit is immutable and its evidence is well identified. The path to that commit, however, used a workflow that first materialized source and then committed generated evidence back to the candidate branch. Future revisions should present a complete source commit before review, run a read-only workflow, and publish artifacts or a separate evidence commit without moving the candidate ref during inspection. This would simplify scope authentication and avoid a reviewer having to switch baselines while the review is underway.

## 5. A credible path to a future paper

A future submission could be strong if it is rebuilt around the following program.

1. **Choose one central multidimensional economic problem.** It should have continuous controls, binding constraints, nonlinear dynamics, and no cheap exact maximization/value solution that trivializes the actor.

2. **Use one immutable protocol.** Fix architecture, seeds, budgets, domains, thresholds, and baselines before executing the final study. Repeat on at least two hardware/math-library environments.

3. **Close the economic error account.** Bound or estimate, with explicit confidence and approximation assumptions, policy evaluation, feasible improvement, boundary error, state/action/time discretization, and domain coverage.

4. **Compare against strong alternatives at matched accuracy.** Direct HJB, classical policy iteration, monotone/semi-Lagrangian methods, and a modern neural PDE/probabilistic baseline should all receive the same model, resources, and stopping rule.

5. **Show when the actor is useful.** The paper should identify a regime in which the actor either reduces the cost of repeated constrained maximization, represents a difficult policy class, or enables equilibrium computation—and quantify the price of its approximation.

6. **Narrow the claims.** Retain scalar interval verification as a validation laboratory, not as evidence that general high-dimensional certification has been solved. Keep finite-game results explicitly finite unless a continuous convergence result is supplied.

That program would constitute a new numerical contribution rather than another repair of the present manuscript.

## 6. Independent reproduction and scope

I reviewed the final R6 head rather than the initial bootstrap head. The exact-source workflow materialized the candidate, executed all suites, compiled the papers, and committed the evidence at `01f4e00a33d9ae29142c8e49bd3c7ec107806796`. I also performed the following independent checks from the committed source:

- reconstructed the six bootstrap parts into a 46,648-byte archive with SHA-256 `9f24d5cd5c2342efaecc717c318837c30537fc767da24d78f05e59b2b799905c`;
- verified the extracted R6 source blobs against the materialized final tree;
- ran all twelve R6 regression tests successfully;
- reran the nine stopped-consumption training jobs: six NBO/direct runs passed and three joint-loss runs failed;
- reran all six scalar interval enclosures: every full interval was covered and every NBO/direct run passed the declared residual/gap thresholds;
- reran all six NDU primary jobs: all NBO runs failed the `.1` finite-model policy-regret target, all direct runs passed;
- reran all twenty-four coupled-capital primary jobs: the same dimension-twenty NBO failure pattern and the critic/payoff discrepancies were reproduced; and
- reran the six principal dynamic Cournot finite games and their independent best-response checks.

The local reruns used Python `3.13.5`, NumPy `2.3.5`, SciPy `1.17.0`, and PyTorch `2.10.0+cpu`. They were independent of the repository's remote workflow but not an independent reimplementation of every algorithm. The custom interval arithmetic was inspected and tested, not formally verified. I did not treat a successful regression suite as proof of the paper's mathematical assumptions or as evidence of journal acceptance.

## 7. Recommendation

R6 deserves credit for a large improvement in correctness, transparency, and executable content. The stopped-consumption theorem–algorithm–verification chain is real, and the preservation of negative outcomes is exemplary. The revision has answered the strongest factual criticism in the previous report.

The remaining issue is contribution rather than repair. The full certificate is restricted to a tailored scalar problem; the principal two-state NBO application fails its own policy target and is dominated by direct Bellman fitting; the high-dimensional study does not convert sampled residuals into economic value accuracy; the game result is finite-grid rather than neural; and the actor's numerical advantage is not demonstrated against strong alternatives.

I therefore recommend **rejection in the present form, with encouragement to develop a substantially narrower and newly executed resubmission**. Such a paper should center on one multidimensional economic application, make the full error account operational there, and establish a clear reason to use the actor–critic construction instead of direct or classical alternatives.
