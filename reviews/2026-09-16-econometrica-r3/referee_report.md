# Referee Report: Neural Bellman Operators — Revision R3

**Review date:** September 16, 2026  
**Repository:** TrillionniumFoundation/NBO  
**Reviewed branch:** `revision/econometrica-r3-2026-09-15`  
**Reviewed commit:** `eb3b908ed0d95f44c762ae9bec562ff1cfeda81d`  
**Authoritative manuscript:** `ECTA_R2.tex`, as identified by the R3 revision index; `SUPP_R2.tex` is the standalone supplement.  
**Recommendation:** **Reject in its present form.**

This is an owner-commissioned, AI-assisted advisory referee report written to the substantive standard of an Econometrica review. It is not commissioned by Econometrica, does not claim an appointment by the journal, and is not an editorial decision. Findings concern the pinned revision above, not the author's intentions. This review adds files only on a new review branch and does not modify the manuscript or author replication artifacts.

## 1. Assessment for the editor

R3 is a meaningful improvement in transparency but not a successful validation of the proposed method. Unlike R2, it contains an executable reference harness and actual numerical records. I independently ran the exact author script: all thirteen records were generated, and all ten raw-output digests that exclude elapsed wall time matched the committed ledger exactly. The mathematical and computational objections below therefore cannot be dismissed as an inability to reproduce the package. The calculations are reproducible; several calculate the wrong object.

The central NDU reference solver omits every diffusion and covariance term in the stated stochastic model. Its nearest-neighbor transition also makes every admissible preference adjustment leave the preference grid index unchanged, eliminating the economic margin the application is supposed to study. The reported zero policy error excludes the portfolio policy, whose coarse/fine discrepancy reaches the entire admissible range, 1.3. The time-inconsistency code evaluates continuation with beta at every date, contrary to the newly corrected sophisticated-self equations. The trace experiment averages squared one-probe residuals rather than squaring the K-probe mean, and thus does not test the claimed probe-budget bias. There is also a distinct false inference from isolated actor stationary points to a policy-improvement fixed point.

These are not requests for additional robustness tables. They are failures of correspondence among the economic problem, its operator, the executable algorithm, and the reported estimand. Moreover, no executed neural Bellman solver is supplied. The alleged coupled scalability evidence is a small, well-conditioned static quadratic program with inactive box constraints, not a coupled stochastic dynamic program or a neural-versus-sparse-grid comparison. Correcting the diagnostic bugs alone would still leave the paper's methodological novelty and quantitative economic contribution unestablished.

I recommend rejection rather than a cosmetic revise-and-resubmit. A reconsiderable submission would have to supply a working method, a mathematically admissible application, and evidence that the method solves that application with a meaningful advantage or yields a substantive economic result. A longer audit protocol is not a substitute for those contributions.

## 2. What R3 genuinely fixes

The review should not repeat objections that the author has addressed. The NDU objective now discounts the entire running integrand and terminal payoff consistently with the displayed HJB. The main text, inline supplement, and standalone supplement now agree on the temporal-self equations. The exact-operator proposition now specifies substantial topology, continuity, compactness, selector, and verification hypotheses. The Merton arithmetic and the distinction between the no-short test and a wealth-dependent kink remain corrected. Historical arrays are much more clearly identified as archival rather than current evidence. The former composite-loss and residual-only viscosity claims are appropriately withdrawn; the retained counterexamples are useful.

| R2 objection | R3 assessment |
|---|---|
| F1: no author solver/run | Real reference code and thirteen records now exist; the absence of an executed NBO neural method remains. |
| F2: NDU objective/HJB discount mismatch | Closed at the displayed continuous-time equation level; new implementation and viability failures arise below. |
| F3: contradictory temporal-self equations | Closed between the written sources; the executable recursion still solves a different preference model. |
| F4: exact-operator theorem and neural bridge | Exact assumptions materially strengthened; the neural bridge remains absent, and the separate stochastic-approximation implication is false. |
| F5: application domains/boundaries | Numerical domains, controls, and terminal payoff supplied; the stated diffusion is not viable on those domains. |
| F6: coupled scalability | A coupled static quadratic calculation exists; the advertised dynamic comparison does not. |
| F7: historical evidence | Most captions and surrounding prose now disclaim evidentiary use; some titles and present-tense claims remain misleading. |
| F8: Epstein–Zin evidence | Correct algebraic/domain point check, not a recursive-utility solution or an implemented sign-enforcing network. |
| F9: dynamic games | Static Cournot arithmetic implemented; no dynamic game, detached-gradient test, or dynamic exploitability audit. |
| F10: Hutchinson comparison | Executed, but with the wrong K-probe squared-loss estimand. |
| F11: NDU comparative statics | Not established: preference adjustment is grid-locked, and no re-solved k-panel is supplied. |
| F12: provenance/build | Exact script identity and numerical reproducibility verified; recorded source commit is unresolvable, and several metrics are not what their names claim. |

## 3. Detailed findings

Source notation below is pinned to the reviewed commit: **M** denotes `ECTA_R2.tex`; **S** denotes `SUPP_R2.tex`; **C** denotes `replication/run_r3_diagnostics.py`; **L** denotes `replication/r3_results.jsonl`; **R** denotes `revisions/2026-09-15-r3/response_to_referee.md`. Links to these immutable sources appear at the end. Line ranges identify source text, not compiled PDF pagination.

### R3-F1. The reference harness does not implement the advertised neural method — blocking

**Evidence:** M, Introduction, Numerical Validation, and Numerical and Implementation Details; C:1–435; L:1–13; R:F1.

The reference/neural distinction made in the response is honest and should be retained. It also concedes the central evidentiary problem. The executable contains grid enumeration, scalar analytical targets, a two-dimensional random quadratic-form experiment, and projected gradient descent on static quadratic programs. It does not contain neural policy or value parameterizations, automatic differentiation, the separated critic and actor losses, a stop-gradient test, trained weights, or an executed baseline for the proposed algorithm.

The manuscript nevertheless describes all experiments as using three hidden layers of 256 GELU neurons, discusses Adam runs as finite-sample evidence, and describes matched sparse-grid comparisons and ablations as performed. Those descriptions cannot refer to the thirteen records supplied. An architectural specification and a future evidence protocol are not an implementation or an experiment. The valid counterexamples to the old loss and to residual-only viscosity selection establish what not to infer; they do not establish that the new solver works.

**Required resolution:** Supply an executable separated NBO solver and identify which current results it actually produces. At minimum, demonstrate evaluated policies and values on an independently solvable control problem and on a coherent nontrivial application, with a credible cost–accuracy comparison. Remove present-tense claims that refer to runs not supplied. This is a contribution requirement, not a demand that every possible application be implemented before publication.

### R3-F2. The NDU reference transition omits all stochastic diffusion — blocking

**Evidence:** M:870–917; C:137–181, especially the transition and continuation calculation at C:160–170. Diagnostic **D1**.

The stated model has

\[
du=\theta\,dt+0.05\,dZ^u,\qquad
dX=[(0.02+0.06\pi)X-c]dt+0.2\pi X\,dZ^X,
\quad d\langle Z^u,Z^X\rangle=-0.25\,dt.
\]

The code evaluates only the drift step, clips it to the rectangle, rounds to the nearest grid node, and reads a single continuation value. There are no diffusion branches, integration weights, shock draws, or covariance contributions. `sigma` is merely retained in returned metadata, and `su` does not affect the transition. A deterministic solver can of course integrate a stochastic model by quadrature; this script does not do so.

A local consistency test is decisive. At an interior node with theta zero, take the smooth test function phi(u,X)=u². The continuous generator is sigma_u²=0.0025, whereas the author's transition leaves u unchanged and produces generator zero. For phi(u,X)=uX, the omitted cross-covariance contribution at pi=0.8 and X=1 is −0.002. These discrepancies do not involve neural optimization, terminal approximation, or boundary behavior.

Thus the reference is not a low-accuracy solution of the stated stochastic HJB. It has a different transition operator and cannot validate risk-aversion shocks or intertemporal hedging against correlated financial shocks.

**Required resolution:** Construct a locally consistent stochastic transition/quadrature or Markov-chain approximation, including the cross term. Test its generator on constant, linear, square, and cross-product functions. Then refine time, state, control, and integration approximations under an explicitly specified boundary mechanism. Relabeling a drift-only calculation a deterministic audit does not resolve the model mismatch.

### R3-F3. The declared NDU state constraint is incompatible with the original SDE — blocking

**Evidence:** M:870–917; C:137–181 and 203–225. Diagnostic **D2**.

The manuscript restricts u to [1.2,2.8] and X to [0.5,2], but gives u an uncontrollable, strictly positive normal diffusion at both endpoints. A bounded drift cannot prevent Brownian exits from that interval. Coordinatewise projection after an Euler step is not a proof that the original controlled diffusion is viable.

There is a second, independent obstruction. At the lower wealth boundary, even the largest possible drift over the stated action set is

\[
(0.02+0.8\times0.06)\times0.5-0.05=-0.016<0.
\]

If pi is set to zero to eliminate wealth diffusion, the maximal drift is −0.04. Thus the lower wealth boundary cannot satisfy the original state-constraint interpretation even after ignoring the problem with u. The admissible controls needed for a viable process starting on this boundary do not exist.

Clipping also changes the resource economics. With X=0.5, c=0.8, pi=0, and Delta=0.25, the unprojected next wealth is 0.3025. Resetting it to 0.5 creates a transfer of 0.1975. Repeated consumption supported by such resets is not a solution of the written self-financing model.

Reflection, absorption, an exogenous transfer rule, and a genuinely viable state-constrained diffusion are distinct models. Reflection requires a regulator/local-time specification and an appropriate boundary operator; it cannot simply inherit the value-only Dirichlet penalty displayed for the generic critic. The code's literal zero `boundary_error` and `max_state_projection_violation` certify neither stochastic viability nor the relevant PDE boundary condition.

**Required resolution:** Choose and economically justify one boundary model, derive its stochastic dynamics and boundary condition, and implement that model. Record projection/regulator magnitudes and pre-correction exits separately from post-correction feasibility. A hard clipping operation should never be reported as a zero-error certificate for a different SDE.

### R3-F4. The grid destroys the preference margin, while the policy metrics omit the portfolio — blocking

**Evidence:** C:137–225; L:2; M, NDU analytical policies and comparative statics. Diagnostic **D3**.

The coarse u-grid spacing is 0.4 and the fine spacing is 0.2. The largest preference drift displacement is only |theta|Delta=0.2×0.25=0.05. Because 0.05 is smaller than half even the fine spacing, every admissible theta maps every u-node back to that same node under nearest-neighbor rounding. Preference adjustment therefore has no effect on continuation value. Only its quadratic cost survives. The optimal theta is mechanically zero everywhere on both grids, regardless of the economic incentives the paper intends to study.

This is an exact reachability failure, not a conjecture about a coarse mesh. The reviewer checks every state/action pair and finds zero pairs that move the preference index. The executed policies also have c=0.8 everywhere. Consequently, agreement of consumption and preference adjustment across these grids is particularly uninformative.

More seriously, `policy_error` compares consumption alone. At time zero on common nodes, the portfolio policies differ by as much as **1.3**, the full interval from −0.5 to 0.8, while the ledger reports policy error zero. The purported Hamiltonian improvement gap is the sum of absolute differences in consumption and theta across two grids. It is an action-distance statistic, with mixed units, not a difference in maximized Hamiltonian values; it also omits pi. The reported value discrepancy is approximately 0.088036, not an independently certified value-function error.

The response correctly says a full k-panel remains an extension. The main text still says such comparative statics are generated by re-solving each k and recorded in the ledger. There is one hardcoded k=2 run, and its preference margin has been removed by discretization. No comparative-static conclusion follows.

**Required resolution:** Use a transition/interpolation scheme that allows controls to affect continuation value, verify reachability and consistency, and refine all relevant action grids. Report errors for the full policy vector and distinguish coarse/fine differences from errors against a validated reference. Compute an independent feasible Bellman/Hamiltonian gain in value units. Re-solve the economically meaningful model before interpreting preference adjustment or k-comparative statics.

### R3-F5. The temporal-self code reintroduces beta into policy evaluation — blocking

**Evidence:** M:1037–1047; S:23–34; C:233–285. Diagnostics **D4–D5**.

The written revision now correctly distinguishes the acting self's criterion from ordinary continuation evaluation. Writing delta=exp(−rho Delta), the equations are

\[
c_n^*\in\arg\max_c\{u(c)\Delta+\beta\delta\,E[V_{n+1}]\},
\qquad
V_n=u(c_n^*)\Delta+\delta\,E[V_{n+1}].
\]

The code instead sets `values[it,iw] = vals[j]`, where `vals[j]` is `log(c) + beta * values[it+1,iwn]`. Beta therefore enters both improvement and evaluation. Repetition gives geometric beta discounting, not the sophisticated quasi-hyperbolic equilibrium written in the paper. Neither a change of notation nor the corrected supplement cures this executable mismatch.

Taking the favorable specialization rho=0 and Delta=1 isolates the problem without introducing another discount discrepancy. On the author's fine grid, the beta=0.7 policy and stored values violate the manuscript's evaluation equation by up to **1.1897063857**. Correctly evaluating the same frozen policy changes stored values by up to **1.8804819136**. A held-out one-shot search against the correctly evaluated continuation produces a gain of **0.1755578479**. This is a finite-grid lower bound on a profitable deviation, not an upper bound or a global exploitability certificate. The author's reported 0.0200624 uses a different coarse-policy/fine-continuation comparison and is not a like-for-like equilibrium certificate.

For beta=1, the corresponding evaluation residual is approximately 4.44×10^−16. The beta-one test is therefore incapable of detecting precisely the error at issue.

A grid-free example makes the distinction transparent. Consider two consumption dates followed by terminal log wealth, no interest, delta=1, and interior choices. At the second date both models choose c1=w1/(1+beta). The correct ordinary continuation value is 2 log w1 plus a constant. Hence the sophisticated first self consumes

\[
\frac{c_0^{\rm soph}}{w}=\frac{1}{1+2\beta},
\]

whereas the implemented geometric-beta recursion gives

\[
\frac{c_0^{\rm code}}{w}=\frac{1}{1+\beta+\beta^2}.
\]

At beta=0.7 these are 0.4166667 and 0.4566210. No boundary convention or approximation issue explains the difference.

**Required resolution:** Store the continuation evaluation separately from the acting self's maximand, use the stated delta and time step, and test beta below one. Evaluate deviations against the actual frozen continuation policy being certified, rather than substituting another grid's policy/value. Retain the beta-one check, but do not treat it as sufficient.

### R3-F6. The Hutchinson experiment measures the wrong K-probe objective — major

**Evidence:** M:674–750; S, Trace Estimation; C:337–358; L:7–10. Diagnostic **D6**.

Let q_k=z_k'Az_k and qbar_K be their mean. The paper's training objective uses the squared residual of the mean trace, (a−qbar_K/2)². The script computes the mean of the individual squared residuals, mean_k (a−q_k/2)². These estimands have different population biases.

For the actual matrix A=[[2,1],[1,3]], tr(A)=5 and ||A||_F²=15. Gaussian probes give Var(q_k)=30. The desired K-probe objective therefore has an excess expectation of **7.5/K**, whereas the author's mean-of-squares statistic has excess expectation **7.5**, independent of K.

With the actual K=64 probes, the script reports a squared-residual statistic of **10.1077269174**, while squaring the residual formed from the same probes' mean gives **1.5682351984**. The exact-trace loss is 1.5625. The correct *population* excess at K=64 is 0.1171875; the realized excess of 0.0057352 is a random observation, not that population quantity. Conversely, a negative realized excess for a small probe sample does not disprove the population identity.

The stored sample variance is also the variance across individual probes, not directly the variance of their mean. The distinction matters for the claimed probe-budget correction. A constant 2×2 matrix test, even corrected, does not measure policy error, value error, or the effect of trace noise on neural training.

**Required resolution:** Average the probes before squaring; use repeated independent batches to compare the empirical mean with the known 1/K bias; identify the variance estimand explicitly. Any claim about trained policies or high-dimensional performance requires an actual controlled PDE experiment in addition to this algebraic regression test.

### R3-F7. The stochastic-approximation conclusion does not follow from isolated stationary points — major mathematical error

**Evidence:** M, appendix subsection Conditional stochastic-approximation statement. Diagnostic **D7**.

The passage separates constant-step Adam from the two-timescale statement, which is appropriate. But it then reasons that isolated stationary points of the actor ODE, together with the condition that an improvement gap is zero only at optimal policies, imply a policy-iteration fixed point. The missing implication is that an actor stationary point has zero improvement gap. Isolation does not supply that implication.

Consider the compact action set [−2,2] and smooth Hamiltonian

\[
H(a)=-(a^2-1)^2+0.2a.
\]

It can be embedded in a finite-horizon control problem with this running payoff, zero terminal payoff, and exact evaluation V^a(t)=(T−t)H(a). Let the actor follow gradient ascent and let the fast critic be globally attracted to exact evaluation. Noise can be identically zero, and bounded projected iterates with the stated diminishing step-size conditions are available.

The actor has three isolated stationary points. The point a≈−0.9739943532 is locally asymptotically stable because H''(a)≈−7.38398. The global maximizer is a≈1.0241203002. The local attractor has strictly positive Hamiltonian improvement gap **0.3998745872**. The gap is zero only at the global optimum, exactly as stipulated in the manuscript, but the actor can converge to the strictly suboptimal isolated attractor.

This counterexample targets the separate stochastic-approximation implication, not the exact pointwise-maximization proposition. It does not rely on Adam, sampling error, or a defective critic.

**Required resolution:** Conclude only convergence toward the appropriate stationary/invariant set unless additional assumptions exclude suboptimal attractors. Conditions such as a justified global concavity or gradient-domination property, or an explicit hypothesis that all relevant attractors have zero improvement gap, must be stated and established where used. One-way optimality of a zero gap is insufficient.

### R3-F8. The exact-operator result is more credible, but remains disconnected from the neural algorithm — major

**Evidence:** M:626–634 and 1107–1118; M:607–617 for the boundary loss; R:F4.

I do not repeat the R2 criticism as though the new assumptions did not exist. Compactness in a declared policy topology, continuity/precompactness of evaluation, closure under an attained selector, and comparison/verification are substantial additions. Under the intended hypotheses, the exact policy-improvement conclusion is plausible. The source proof is still too compressed, but its central limit step can be made precise.

In particular, monotonicity and precompactness give a common limiting value Vbar. For a convergent policy subsequence pi_nj→p, continuity gives E(p)=Vbar. Continuity of improvement/evaluation and convergence of the shifted value sequence give E(I(p))=Vbar as well. Evaluation of the improved policy at this same limiting value then supplies the maximized HJB equation. It is equality of limiting *values*, not an unjustified assertion that successive limiting policies coincide, that closes the argument. The final paper should write this step and specify the boundary/generator topology explicitly.

The proposition nevertheless assumes exact evaluation and an exact pointwise maximizer inside a closed policy class. A finite neural class is not generally closed under that selector, and a small sampled residual is not the stipulated strong evaluation approximation. No result bounds the loss of value from critic, boundary, actor, sampling, and discretization errors for the proposed implementation. Smooth approximation of a C² function is not such a result.

Nor are the proposition's assumptions verified for the central application: the NDU viability problem above prevents using it as a worked instance. The value-only boundary residual in the generic algorithm cannot stand in for every possible reflected or state-constrained boundary operator.

**Required resolution:** Provide the complete conditional proof without advertising it as a neural convergence theorem. Then either establish a quantitative approximate-policy-iteration link under useful application assumptions, or demonstrate the finite algorithm convincingly and state its empirical scope. The exact theorem should support the contribution rather than replace the absent numerical method. Continuous-time policy-improvement theory already distinguishes the assumptions needed for improvement and convergence; see reference [1].

### R3-F9. The coupled scalability record is a static, uniformly well-conditioned quadratic exercise — blocking for the scalability claim

**Evidence:** M, Benchmarking against Grid-Based Methods and computational-cost sections; C:366–396; L:11–13; R:F6. Diagnostic **D8**.

The new quadratic problem genuinely has cross-coordinate coupling; calling it separable would be incorrect. But it is not the coupled stochastic dynamic model promised in the manuscript. The calculation minimizes 0.5 x'Qx−b'x over a box, with Q having diagonal 2 and adjacent off-diagonal entries 0.25. It compares a direct linear solve with 1,000 projected-gradient steps at dimensions 4, 8, and 16.

There is no evolving state, shared aggregate resource constraint, stochastic shock process, HJB equation, neural approximation, or sparse-grid comparator. Calling Q a covariance in metadata does not make its use in a quadratic objective an implemented stochastic covariance. The function also performs no stochastic trace experiment and records no peak memory, despite broader descriptions in the response.

The matrix family is deliberately easy: its eigenvalues lie in [1.5,2.5], so the condition number is at most 5/3 independently of dimension. The observed exact actions have maximum absolute values around 0.09; every box constraint is inactive. Consequently, the test neither confronts difficult constraints nor approximates a function on a high-dimensional state space. Its near-machine-precision output is not evidence of escaping a dynamic-programming curse of dimensionality.

The timer starts after the direct solve and eigenvalue calculation and covers only the gradient loop. There is no matched end-to-end fixed-accuracy timing comparison. One seed label attached to a deterministic calculation is not a multi-seed failure-rate study.

**Required resolution:** Retain this as a small linear-algebra regression test. To claim high-dimensional control performance, specify a genuinely coupled dynamic model, execute NBO and relevant baselines on identical economic primitives and accuracy targets, and report end-to-end costs and failures. The dimension cutoffs and claims of relative advantage cannot be inferred from the current quadratic records.

### R3-F10. Algebraic anchors are being assigned solution-error metrics they do not measure — major

**Evidence:** C:107–131, 292–330; L:1,5–6; M, Recursive Utility and Dynamic Cournot sections; R:F5,F8,F9.

The Merton targets (0.75,0.04125), Epstein–Zin candidates (0.3,0.0455), and static Cournot quantity 1/3 are useful arithmetic checks. They are not trained policies or independently solved value functions. Several `value_error`, `policy_error`, `boundary_error`, `residual_mean`, and `improvement_gap` fields are assigned literal zeros despite no corresponding computation. Zero is a substantive numerical assertion; an inapplicable or unmeasured quantity should not be made to look like a passed solution certificate.

For Epstein–Zin, the script evaluates the aggregator at c=1 and V=−1. The string `V=-exp(raw)` appears in the configuration, but no such neural transformation is executed, and no terminal-sign test is performed. The pointwise domain check is real; the claimed architecture/domain-wide/terminal audit is not. Formal stationary ratios remain formal candidates until the utility problem and verification conditions have been supplied.

For Cournot, the script computes the static analytical best response. It does not differentiate any actor graph, so this calculation cannot test whether rivals were actually detached in an implementation. It also does not define a dynamic state transition, horizon, capital dynamics, independent dynamic best response, or competitive limit. The main text's statements about multiple initial profiles and a separately solved competitive benchmark are not supported by this record.

**Required resolution:** Separate arithmetic tests, domain checks, execution success, and solution certificates in the ledger. Use null with an explanation for unmeasured errors. Supply recursive-utility and dynamic-game runs before describing those applications as numerical validations of NBO; otherwise retain them explicitly as proposed extensions.

### R3-F11. The novelty comparison omits the closest operator-iteration literature — major contribution concern

**Evidence:** M, Related Literature, Relation to Existing Methods, and Domain of Validity; primary references [1]–[5].

The comparison to generic PINNs, reinforcement learning, and the original Deep BSDE paper does not isolate the proposed contribution. Closely related primary work already combines neural PDE evaluation with policy improvement. Kim, Kim, Kim, and Cho's August 2025 version describes a physics-informed neural policy-iteration approach with fixed-policy PDE evaluation and policy-error analysis [2]. Lee and Kim combine HJB policy iteration with deep operator learning [3]. SOC-MartNet represents both value and control without requiring an explicit analytical Hamiltonian optimizer [4]. Direct neural control approximation also predates this paper [5].

These references do not establish that all of NBO's claimed economic applications or recursive aggregators have been solved before. They do establish that neural approximation, operator factorization, mesh-free residual evaluation, and avoidance of an analytical argmax are not, by themselves, an adequate novelty claim. The paper must identify a specific new algorithmic mechanism, theorem, verified accuracy/cost advantage, or economic result relative to these closer comparators.

The BSDE discussion also conflates different distinctions. Semilinearity concerns dependence on the highest-order derivative, not simply whether an analyst can eliminate the control analytically. An analytical maximizer need not remove nonlinear Hessian dependence, and a BSDE representation of an HJB equation is not automatically the Pontryagin adjoint system. Accordingly, an inability to derive a closed-form control does not establish the claimed categorical separation.

The O(d²) versus O(Kd) discussion is at best a conditional differentiation-cost model. Network size, diffusion-loading multiplication, parameter-gradient computations, probe count required for accuracy, sample count, and optimization iterations remain material. Exact low-rank diffusion contractions need not materialize a dense d×d Hessian. Universal optimal-use regimes at dimensions 50 or 100 cannot be deduced from derivative counts or the current static quadratic test.

**Required resolution:** Rewrite the contribution comparison around the closest methods and a declared cost model. Support a concrete advantage with either a nontrivial theorem or actual matched experiments. Preserve the economic ambition, but do not substitute broad application labels for a demonstrated economic contribution.

### R3-F12. Provenance is improved, but the source label and certification semantics remain defective — major

**Evidence:** revision manifest; L:1–13; C:65–100; replication schema, README, environment, and build transcript; S, Evidence and Reproducibility.

All thirteen author records and the build summary identify source commit `a694ede0d5408ae3c9e6d7e3dd9131441cb9b146`. A repository Git-commit lookup returned **404 Not Found** during this review. The reviewed R3 commit instead has R2 as its immediate parent. The recorded source may have been a local or subsequently squashed commit; the evidence does not justify a claim about why it is missing. Nevertheless, it is not currently a resolvable repository provenance anchor.

This is not an allegation that the runs are fictitious. The exact author script's SHA-256 and Git blob identity match the repository, and ten non-timing payload digests reproduced exactly. The correct repair is to record a reachable source identity or an explicit, independently checkable mapping from the local source to the committed tree.

The status field is hardcoded to `success` when a record is constructed. It does not distinguish program completion from meeting an accuracy tolerance. Several boundary and solution errors are constants or misnamed distances, as discussed above. The schema also mixes evidence categories and execution status in one enumeration, and does not enforce metric definitions, units, evidence classes, or reasons for unavailable metrics. NDU's configuration object omits several hardcoded model/discretization parameters, while other quantities reside only in raw metadata or source.

The three coupled raw digests include elapsed wall time and are therefore not expected to be byte-for-byte deterministic across reruns. That is not a numerical replication failure; it is a reason to separate scientific payload digests from timing metadata. The standalone supplement also points to `replication/results.jsonl`, rather than the R3 ledger.

The supplied build transcript is a summary claiming a 25-page main PDF and two-page supplement with clean final passes. I have not independently recompiled R3 or audited its rendered PDF. I therefore neither endorse those build claims as reviewer-verified nor repeat the older R2 layout objections as established current defects.

**Required resolution:** Repair source provenance, distinguish evidence class/execution/tolerance status, document actual metric estimands, correct ledger references, and reserve numerical zeros for quantities truly evaluated. These changes improve auditability but cannot repair the mathematical and economic problems by themselves.

## 4. Reproducible review evidence

This review includes `reviewer_diagnostics.py`, `diagnostic_results.json`, and `review_manifest.json` in the same directory. From a checkout of the new review branch, run:

```sh
python reviews/2026-09-16-econometrica-r3/reviewer_diagnostics.py
```

NumPy is required. The test verifies the exact reviewed author script before importing it and never modifies author source files or ledgers. It regenerates thirteen author records, checks the ten non-timing raw digests against the committed ledger, and then performs independent diagnostics. Its successful completion means that the documented discrepancies were reproduced, not that the manuscript passed validation.

| Independent diagnostic | Result |
|---|---|
| Author source identity | 21,274 bytes; SHA-256 and Git blob both match. |
| Author rerun | 13 records; 10/10 non-timing raw digests match exactly. |
| Missing u-diffusion | Generator of u²: manuscript 0.0025; author transition 0. |
| Lower wealth viability | Maximum drift at X=0.5 is −0.016. |
| Preference-grid reachability | Zero state/action pairs move u, on both grids. |
| Omitted portfolio discrepancy | Maximum common-node time-zero difference 1.3; reported policy error 0. |
| Beta=0.7 evaluation mismatch | Maximum equation residual 1.1897063857. |
| Beta=0.7 unilateral grid deviation | Gain 0.1755578479 against correctly evaluated author continuation. |
| K=64 trace loss | Mean of squares 10.1077269174; square of mean residual 1.5682351984. |
| Isolated actor attractor | Strictly suboptimal stable point with gap 0.3998745872. |

The reviewer environment used Python 3.13.5 and NumPy 2.3.5; the author's environment file reports Python 3.12.14 and the same NumPy version. Timing is not compared byte-for-byte. The temporal diagnostic retains the author's clipped transition and nearest-neighbor grid to isolate the evaluation error; it does not endorse either as an economic model. The grid-free example and polynomial-generator checks provide separate analytical diagnostics.

Review limitations are explicit. No neural training or global PDE error certificate was produced. No independent R3 LaTeX/PDF build audit was conducted. The author script's full-content hashes were independently verified; the report does not claim to have recomputed every manuscript/source hash in the author manifest. Primary literature was checked for relevant methods and scope, not exhaustively searched for priority. None of these limitations weakens the explicit operator, recursion, estimand, and logical counterexamples above.

## 5. Conditions for reconsideration

A new submission should first make the mathematical problem and executable object agree. For NDU this requires a defensible boundary economy and a stochastic transition retaining the intended covariance and preference-adjustment margin. For temporal selves it requires distinct acting and continuation-evaluation objects. For stochastic traces it requires the correct batched estimand. The actor convergence claim must either be strengthened with assumptions that exclude suboptimal attractors or restricted to the conclusion actually established.

The second requirement is an actual NBO implementation, not additional reference arithmetic. It should expose the critic, actor, boundary, and rival-gradient conventions in executable tests and demonstrate at least one nontrivial solved economic application. Independent value/policy/gain evaluation and a meaningful matched comparison should establish what the method contributes. Breadth can remain an ambition; it cannot count as completed evidence.

Finally, the presentation should be regenerated from those executed results. Historical arrays may remain in the repository without remaining in the manuscript's evidentiary narrative. A trustworthy ledger should make a failed or unmeasured test visible rather than representing it as a zero error. Provenance should identify the actual reachable source tree. These are necessary conditions for assessing a future submission, not a prediction that mechanical compliance would establish novelty or meet the journal's standard.

## 6. Primary references and pinned repository sources

[1] Jacka, S. D., and A. Mijatović. *On the policy improvement algorithm in continuous time*. Primary preprint, 2015. https://arxiv.org/abs/1509.09041

[2] Kim, Yeongjong, Yeoneung Kim, Minseok Kim, and Namkyeong Cho. *Neural Policy Iteration for Stochastic Optimal Control: A Physics-Informed Approach*. Version 1, August 3, 2025. The version is pinned because the later version has a different title. https://arxiv.org/abs/2508.01718v1

[3] Lee, Jae Yong, and Yeoneung Kim. *Hamilton-Jacobi Based Policy-Iteration via Deep Operator Learning*. Primary preprint, 2024. https://arxiv.org/abs/2406.10920

[4] Cai, Wei, Shuixin Fang, and Tao Zhou. *SOC-MartNet: A Martingale Neural Network for the Hamilton–Jacobi–Bellman Equation without Explicit inf H in Stochastic Optimal Controls*. Version 4, March 15, 2025. https://arxiv.org/abs/2405.03169v4

[5] Han, J., and W. E. *Deep Learning Approximation for Stochastic Control Problems*. Primary preprint, 2016. https://arxiv.org/abs/1611.07422

Repository source links, all pinned to the reviewed R3 commit:

- [Revision index](https://github.com/TrillionniumFoundation/NBO/blob/eb3b908ed0d95f44c762ae9bec562ff1cfeda81d/REVISION_INDEX.md)
- [M: authoritative manuscript](https://github.com/TrillionniumFoundation/NBO/blob/eb3b908ed0d95f44c762ae9bec562ff1cfeda81d/ECTA_R2.tex)
- [S: standalone supplement](https://github.com/TrillionniumFoundation/NBO/blob/eb3b908ed0d95f44c762ae9bec562ff1cfeda81d/SUPP_R2.tex)
- [C: executable author harness](https://github.com/TrillionniumFoundation/NBO/blob/eb3b908ed0d95f44c762ae9bec562ff1cfeda81d/replication/run_r3_diagnostics.py)
- [L: author R3 ledger](https://github.com/TrillionniumFoundation/NBO/blob/eb3b908ed0d95f44c762ae9bec562ff1cfeda81d/replication/r3_results.jsonl)
- [R: response to R2 referee](https://github.com/TrillionniumFoundation/NBO/blob/eb3b908ed0d95f44c762ae9bec562ff1cfeda81d/revisions/2026-09-15-r3/response_to_referee.md)
- [R3 manifest](https://github.com/TrillionniumFoundation/NBO/blob/eb3b908ed0d95f44c762ae9bec562ff1cfeda81d/revisions/2026-09-15-r3/revision_manifest.json)
- [Previous R2 report](https://github.com/TrillionniumFoundation/NBO/blob/eb3b908ed0d95f44c762ae9bec562ff1cfeda81d/reviews/2026-09-15-econometrica-r2/referee_report.md)

## 7. Recommendation

**Reject in its present form.** R3 has made the record more transparent and genuinely reproducible. It has not demonstrated that NBO solves the stated economic problems. The stochastic NDU operator, sophisticated-self recursion, probe-budget estimand, and actor-convergence implication contain independently identifiable failures. Beyond those failures, the promised neural implementation and the paper's comparative methodological/economic contribution remain unestablished. A future review should assess newly executed, corrected work rather than another relabeling of the current diagnostics.
