# Referee Report — Neural Bellman Operators, Revision R14

**Venue standard:** Econometrica-level numerical / computational methodology  
**Recommendation:** **Reject in the present form. A future paper would require a substantive new scientific revision, not another certification wrapper around the current numerical objects.**  
**Review date:** 2026-09-22  
**Remote review target:** revision/econometrica-r14-independent-state-audit-2026-09-22  
**Latest remote branch head reviewed:** 502b56e2ec8c91a17ddbe5ccfbd798bba3d799a8  
**Validated scientific commit reviewed:** 18c18702988c2bffe886f9b3d779183df22e3971  
**Review branch:** review/econometrica-r14-final-numerical-methods-2026-09-22  
**Target status:** published, materialized, and provenance-pinned R14

## 1. Executive assessment

Revision R14 is a substantial improvement over the purported R13 revision. In particular, it finally separates three objects that earlier versions repeatedly risked conflating:

1. the freshly trained neural actor/critic;
2. the sharp finite time-control policy library;
3. the application-specific affine-preference dual used to upper-bound the original adapted-control problem.

That separation is scientifically important. The revision also executes the previously abstract neural cover/oracle interface on an actual stored neural network, supplies an independent second numerical implementation for the sharp policy/dual calculation, records adverse results rather than suppressing them, introduces a nontrivial initial-state/price continuation argument, and reports a freshly generated policy-richness experiment.

Those changes make the present paper much easier to evaluate. Unfortunately, they also make the central venue problem impossible to avoid:

> **The Neural Bellman Operators solver does not solve the flagship problem to useful certified accuracy.**

The finest complete certificate for the actual R14 neural actor/critic is

\[
23.493172462829243,
\]

while the declared numerical target is \(0.01\). The boundary-trace contribution alone is approximately

\[
14.046215886665081,
\]

and the integrated residual/action contribution is approximately

\[
9.446956576164158.
\]

By contrast, the results below \(0.01\) are delivered by a different numerical object: a library of deterministic time controls with \(p=0\), combined with a specialized affine-preference dual. The independently audited central-state continuum certificate is

\[
0.009969007710640541,
\]

and the newly generated 16/32/64-slab time-control experiment gives approximately

\[
0.0096880571,\quad 0.0096695479,\quad 0.0096650730.
\]

R14 now states this distinction correctly. But correct labeling does not resolve the scientific mismatch. It establishes that the verifier can falsify an inaccurate neural candidate, while the accurate certified solution is presently supplied by another method class.

For an Econometrica-level numerical-method contribution, that is not enough. The paper needs a numerical method that (i) produces economically useful solutions, (ii) has a convincing accuracy-versus-work story, (iii) compares against serious same-problem alternatives, and (iv) demonstrates that the part of the method advertised as the contribution is responsible for the numerical success. R14 does not yet meet those requirements.

I therefore recommend rejection in the present form.

---

## 2. Review-target integrity and provenance

The R14 branch changed state while this referee audit was in progress. I therefore followed the publication sequence to completion rather than attaching the final report to an intermediate moving branch snapshot.

The sequence relevant to the review is:

- materialization commit: b30733758355b27174e01956e804422897a96f1e;
- validated scientific commit: 18c18702988c2bffe886f9b3d779183df22e3971;
- final metadata-only branch head: 502b56e2ec8c91a17ddbe5ccfbd798bba3d799a8.

The latest branch-head commit changes only publication metadata and restored runtime cache bytes relative to the validated scientific commit. The final publication receipt explicitly pins the scientific source, results, build evidence, and referee response to 18c18702988c2bffe886f9b3d779183df22e3971. The canonical manifest records remote_publication.state = “published_and_pinned.”

Direct retrieval succeeds for ECTA_R14.tex/.pdf, SUPP_R14.tex/.pdf, R14_REVIEW.md, the current paper sources, response, replication code, numerical records, manifest, and receipt.

### R14-F0 — **Resolved during review: R14 is now a materialized and provenance-pinned scientific revision**

At the beginning of the audit, R14 existed only as a bootstrap patch delivery. During the audit it was materialized and then followed by publication-status commits. The final state now distinguishes:

- the materialization commit;
- the validated scientific commit;
- the metadata-only branch head;
- historical reconstructed local commit IDs.

That resolves the version-integrity objection for this review round.

The scientific assessment below is therefore not based on a branch name, an unexecuted patch, or a synthetic local commit. It is based on the materialized scientific objects pinned to 18c18702988c2bffe886f9b3d779183df22e3971, with the latest remote metadata at 502b56e2ec8c91a17ddbe5ccfbd798bba3d799a8.

No adverse scientific finding below depends on the earlier bootstrap state.

---

## 3. What R14 genuinely fixes

Several prior objections have been addressed and should be credited explicitly.

### 3.1 The neural certificate is now actually executed

The previous cover/oracle theorem is no longer merely an interface theorem. R14 stores a fresh two-hidden-layer, width-48 tanh actor/critic, evaluates network derivatives with an independent interval implementation, covers the full state-time rectangle, solves the continuous action maximization conservatively, checks all four first-exit faces, and records zero skipped/failed cells.

The finest retained cover has:

- 16,384 interior cells;
- 512 cells on each of four first-exit faces;
- exact terminal trace by construction.

This is a real numerical experiment.

### 3.2 The sharp time-control certificate is no longer called a neural certificate

R14 correctly states that the \(0.009969...\) result belongs to a feasible time-control policy library and an independent upper comparison over all original adapted controls. The paper no longer assigns that number to the neural feedback.

This correction is essential.

### 3.3 The second numerical stack is materially more independent

The new policy and dual evaluators do not import the inherited R8–R12 certifiers. They use a new outward interval core, rational-series transcendental enclosures, rational isolation of Gauss nodes, interval differentiation of the dual source, and a different policy-integration decomposition. A clean replay recomputes all decisive fields.

This is a significant improvement over calling same-code replay “independent verification.”

### 3.4 The paper now reports negative results

The following adverse facts are stated rather than hidden:

- the neural certificate misses \(0.01\) by orders of magnitude;
- the 800-update network is not uniformly better than the 300-update network at the same coarse cover;
- 16/32/64-slab refinement does not reach \(0.005\);
- two matched strong classical state-space baselines remain absent;
- the retained 128-dimensional result is an action oracle at frozen jets, not a 128-state dynamic-control solution;
- the old sharp policy library was inherited and its generation cost is unknown.

This is the right scientific practice.

These improvements, however, mainly clarify the scope of what has and has not been achieved. They do not yet establish the main numerical-method claim.

---

## 4. The decisive numerical facts

| Object | Certified quantity | Scope | Referee interpretation |
|---|---:|---|---|
| Fresh R14 neural actor/critic | 23.493172462829243 | \(t=0\), full original state rectangle, \(k=2\) | Complete certificate, but numerically unusable relative to the claimed \(0.01\) target |
| Neural stopping-trace contribution | 14.046215886665081 | Same | Boundary error alone is catastrophic |
| Neural residual/action contribution | 9.446956576164158 | Same | Sampled training residual is not a proxy for certified error |
| Neural coefficient-box certificate | 23.53040781305452 | Small coefficient box around \(k=2\) | Transport machinery works, but transports a poor base solution |
| Independently audited historical time-control library | 0.009969007710640541 | Central initial state, all \(k\in[0.5,8]\) | Sharp but non-neural |
| Perturbed-witness library | 0.009970977449945498 | Same | Useful robustness test, still non-neural |
| Initial-state/price time-control family | 0.012095431553888848 | \(t=0\), \(u\in[1.98,2.02]\), \(x\in[1.24,1.26]\), all \(k\) | Continuous-domain extension, but tiny and open-loop/time-control in nature |
| Fresh 16-slab time-control experiment | 0.009688057135165852 | \(k=2\) | Passes \(0.01\) |
| Fresh 32-slab time-control experiment | 0.009669547904274768 | \(k=2\) | Small improvement |
| Fresh 64-slab time-control experiment | 0.0096650730255341 | \(k=2\) | Small improvement; still fails \(0.005\) |

The manuscript is unusually candid about these numbers. The difficulty is that the numbers do not support an Econometrica-level claim that the proposed neural solver is currently a competitive numerical solution method.

---

## 5. Central scientific objection

### R14-F1 — **Blocking: the actual Neural Bellman Operators solver fails its own flagship accuracy test by orders of magnitude**

The intended R14 manuscript says that the full-domain neural certificate gives a time-zero regret bound of approximately \(23.493\), with a two-sided stopping-trace allowance of approximately \(14.05\). The neural result explicitly fails the declared \(0.01\) target.

This is not a minor issue of conservatism at the fourth decimal place. The certified bound is more than three orders of magnitude larger than the target.

The paper correctly emphasizes that a large certificate can expose a poor candidate rather than invalidate the certificate. I agree. But that observation establishes the usefulness of the **verification framework**, not the numerical success of the **Neural Bellman Operators solver**.

At an Econometrica numerical-method standard, the natural question is not merely:

> Can the method tell us that one trained network is inaccurate?

It is:

> Can the proposed method actually generate accurate, economically useful policy/value objects on problems where the method is supposed to matter?

R14 does not yet answer that question positively.

The training protocol makes the gap even more striking. The fresh neural run uses:

- one fixed seed;
- two hidden layers of width 48;
- 800 actor updates;
- three critic updates per actor update;
- batch size 128;
- one CPU Torch thread;
- about 13 seconds after program entry;
- a boundary-loss coefficient of \(0.025\).

The resulting sampled residual mean square may look modest, but the complete certificate exposes massive boundary and worst-case errors. That is exactly why the certification is valuable. It is also evidence that the current training algorithm is not yet a reliable solver for the model.

### Required

A new revision needs an actual successful neural solve, not merely a more refined diagnosis of the current failure.

At minimum:

1. train multiple independent seeds;
2. vary architecture, optimizer budget, boundary parameterization, boundary penalties, and sampling distributions;
3. choose checkpoints according to predeclared criteria that do not peek at the final desired conclusion;
4. certify every selected stored network with the same complete full-domain verifier;
5. demonstrate a meaningful accuracy-versus-computation frontier;
6. obtain a neural policy certificate in the same numerical regime as the successful comparator, not \(23.49\) versus \(0.01\);
7. show whether the improvement comes from better training, a boundary-satisfying architecture, policy iteration, adaptive sampling, or another reproducible algorithmic change.

Until then, the paper has a validated **neural failure case**, not a validated successful neural numerical method.

---

## 6. The sharp result belongs to a different method

### R14-F2 — **Blocking: the strongest certified numerical result is still not produced by the advertised neural method**

The central \(0.009969...\) result is produced by:

1. a finite library of deterministic 16-slab time controls;
2. \(p=0\) throughout those policies;
3. direct rigorous stopped-policy evaluation;
4. an application-specific affine-preference market-deflator dual;
5. exact price-envelope postprocessing.

This is a legitimate and interesting validated stochastic-control pipeline. It is also materially different from the trained state-feedback actor/critic that motivates the title.

R14 no longer hides this fact. Indeed, the new paper repeatedly separates the two objects. That improves correctness but sharpens the methodological conclusion:

> the accurate certified solver in the flagship economy is currently the specialized time-control/dual construction, not Neural Bellman Operators.

The manuscript sometimes presents the sharp library as an “independent comparison object.” But the sharp library is doing much more than benchmarking. It supplies the only economically useful certified solution presently reported.

A numerical-method paper cannot claim success by placing its inaccurate proposed method next to a successful auxiliary method and then treating the existence of the verifier as the principal numerical achievement.

### Required

The authors need to choose and substantiate one of two coherent scientific identities.

**Route A — Neural numerical-method paper.**  
The neural algorithm must itself generate accurate policies/value approximations and survive full-domain certification at useful tolerances.

**Route B — Validated stochastic-control / verification paper.**  
The core contribution should be the a posteriori certification architecture and application-specific primal/dual machinery, with neural training treated as one candidate generator that presently fails this test.

For Econometrica as a numerical-method contribution under the current title and framing, Route A is the relevant standard.

---

## 7. The state-domain extension remains much narrower than advertised numerical dynamic programming

### R14-F3 — **Blocking: the useful state certificate is a tiny \(t=0\) initial-state family of time controls, not a verified feedback policy/value surface**

R14 now extends the sharp certificate from one initial state to

\[
u\in[1.98,2.02],\qquad x\in[1.24,1.26],
\]

at \(t=0\), uniformly in \(k\in[0.5,8]\).

The mathematical construction is clever: the upper comparison is convex, the lower covered policy functional is concave, and four corner calculations plus exact price breakpoints give a continuum certificate.

However, the economically useful object is still not a feedback solution of the dynamic program.

The policy family is generated by shifting deterministic consumption according to the **initial wealth**:

\[
c_j(x)=c_j+\frac{x-1.25}{Q_r},
\]

while retaining the same time path of preference adjustment and \(p=0\). The paper correctly calls it an initial-state-indexed time-control family.

Three limitations follow.

1. **The domain is extremely small.**  
   The original state domain is \(u\in(1.2,2.8)\), \(x\in(0.5,2)\). The useful certified rectangle has width only \(0.04\) in preference and \(0.02\) in wealth.

2. **The certificate is only at initial time zero.**  
   It does not produce a high-accuracy continuation policy from arbitrary later states.

3. **It is not a closed-loop policy surface.**  
   It does not show that the numerical method approximates the Bellman policy/value functions over the state space.

A dynamic-programming numerical method should normally deliver a reusable state-contingent object, not merely a collection of initial-state-indexed open-loop controls.

### Required

Provide a genuinely nontrivial verified state-time region for an accurate feedback policy, including:

- later initial times;
- states near economically relevant boundaries;
- quantitative policy/value errors across the domain;
- a state-space accuracy surface rather than only a scalar regret number;
- evidence that refinement increases the verified state region or decreases the error.

The current tiny \(t=0\) rectangle is useful evidence but not a replacement for this.

---

## 8. Missing same-problem classical baselines

### R14-F4 — **Blocking: the paper still lacks strong matched-accuracy state-space baselines**

The R14 response itself acknowledges that this objection is not fully addressed.

The new direct time-control optimization is a useful comparator, but it is not a strong state-space HJB solver. The paper still lacks serious same-problem implementations such as:

- a monotone finite-difference or finite-volume HJB method;
- a semi-Lagrangian method;
- a controlled Markov-chain approximation;
- adaptive sparse grids / collocation;
- policy iteration with a conventional basis;
- another credible state-space primal/dual method.

This omission is especially damaging because the neural method does not reach the comparator's accuracy.

The paper's motivating numerical premise is presumably that neural methods offer value when classical state-space methods become difficult. Yet the actually certified neural state problem here has only two state variables, precisely the regime in which strong classical methods should be most competitive and easiest to validate.

Without these baselines one cannot determine whether:

- the neural training is competitive;
- the full-domain interval verifier is unusually expensive;
- the specialized time-control construction is exploiting model structure that a generic HJB method would capture easily;
- the claimed numerical contribution improves any established accuracy/work frontier.

### Required

Add at least two independent, strong classical state-space solvers on the **same unchanged economy**.

Compare them using:

1. the same initial states and state domain;
2. the same payoff and stopping contract;
3. matched verified accuracy rather than fixed iteration counts;
4. end-to-end wall time and memory;
5. solution-generation cost plus verification cost;
6. refinement curves, not one operating point.

Do not use reference-solvable external examples as a substitute.

---

## 9. No convincing convergence or accuracy-versus-work law

### R14-F5 — **Blocking: R14 has a frontier experiment, but not a numerical convergence result**

The new 16/32/64-slab experiment is a meaningful improvement over the previous parameter-node “frontier.” It genuinely changes policy richness.

But the resulting bounds are:

- 16 slabs: \(0.0096880571\);
- 32 slabs: \(0.0096695479\);
- 64 slabs: \(0.0096650730\).

The upper bound is exactly the same in all three cases:

\[
U=-1.2853299527626258.
\]

Thus the experiment mostly demonstrates that the current specialized upper relaxation is the bottleneck.

That is useful diagnosis. It is not a convergence theorem or a convincing empirical convergence frontier.

Likewise, refining the interval cover around a fixed inaccurate neural network can reduce enclosure overestimation, but cannot show convergence of the underlying neural approximation to the dynamic-programming solution.

The paper has no result of the form:

\[
\varepsilon \downarrow 0
\quad\text{as}\quad
\text{model approximation / network / policy / verification work}\uparrow.
\]

Nor does it establish a complexity relationship between target accuracy and computational work.

### Required

For the unchanged flagship problem, produce an actual error-versus-work sequence, for example:

\[
10^{-2},\;5\times10^{-3},\;2.5\times10^{-3},\;10^{-3},
\]

or explain rigorously why a different sequence is scientifically appropriate.

The sequence must vary the approximation object that is claimed to converge and must include the cost of obtaining the comparison bound. Merely refining quadrature around a fixed dual or a fixed network is insufficient.

Ideally, the paper should also provide a consistency or convergence theorem for the proposed approximation/certification scheme under stated assumptions.

---

## 10. The verifier itself has not escaped the curse of dimensionality

### R14-F6 — **Blocking for the high-dimensional motivation: the complete certificate is demonstrated only in two state dimensions**

The paper carefully corrects the scope of the historical 128-dimensional result. It is a structured action-optimization oracle at frozen jets, not a 128-dimensional dynamic-control solution.

That correction is welcome, but it exposes the remaining scaling problem.

The rigorous neural certificate uses a complete rectangular cover of

\[
[0,1]\times[1.2,2.8]\times[0.5,2].
\]

Even for one time dimension plus two state dimensions, the finest reported run uses 16,384 interior cells plus boundary cells.

A straightforward complete box cover scales exponentially in state dimension. The paper does not provide:

- adaptive subdivision complexity results;
- dimension-independent residual bounds;
- compositional or sparse certificate structure;
- low-rank derivative enclosures;
- probabilistic certificates with controlled failure probabilities;
- certified neural relaxations that avoid full tensor covering;
- a demonstrated full dynamic certificate beyond the two-state model.

This is fundamental because high dimensionality is one of the principal reasons to use neural PDE/control methods in the first place.

### Required

Either:

1. demonstrate complete policy certification on a materially higher-dimensional dynamic model, with scaling data and unchanged rigorous semantics; or
2. sharply narrow the methodological claim and explain that the current verifier is a low-dimensional a posteriori certificate.

A frozen high-dimensional action oracle cannot substitute for state-space certification.

---

## 11. The strongest sharp result is not reproducible end-to-end from fresh generation

### R14-F7 — **Major: the independently audited 18-node library starts from inherited historical proposals**

R14 correctly states that the inherited policy proposals and dual pilots are frozen inputs and that their historical generation cost is unknown.

This is honest, but it means the strongest central result is not an end-to-end reproducible numerical method.

The clean replay demonstrates that, **given the selected policies and witnesses**, the second implementation reproduces the decisive lower and upper bounds. It does not demonstrate how a new user, starting from only the economic model, would rediscover the 18-node policy/dual library.

The fresh 16/32/64-slab experiment partially addresses this problem at \(k=2\), but it does not regenerate the full \(k\in[0.5,8]\) library or the exact final sharp continuum object.

### Required

Provide a one-command, clean-environment end-to-end experiment that starts from:

- the model specification;
- fixed seeds or deterministic initializations;
- no inherited policy files;
- no inherited dual pilots;
- no hand-selected historical nodes.

It should regenerate the full reported price library, fit all witnesses, adaptively select nodes if needed, verify them, and rebuild the final exact price envelope.

Record all failures, refinements, optimizer restarts, and total resource use.

---

## 12. The neural experiment is too weak to establish either capability or robust failure

### R14-F8 — **Major: one small fresh run cannot support broad conclusions about NBO**

The current neural experiment is useful because it is fully auditable. But it is only one training configuration with one seed and a very small computational budget.

The paper should not infer from this that the NBO concept is generally poor; equally, it cannot infer that the NBO method is generally effective.

The present result establishes only:

> this particular network/training run has a bad complete certificate.

The enormous boundary error suggests an obvious algorithmic target: the critic architecture enforces the terminal trace exactly but not the first-exit trace. A numerical-method paper should investigate that failure systematically.

### Required

At minimum report:

- 10+ independent seeds;
- several network widths/depths;
- substantially larger training budgets;
- architectures that enforce all stopping faces exactly or with hard constraints;
- adaptive boundary sampling;
- residual weighting studies;
- actor/critic update-ratio studies;
- certified, not sampled, error at each retained checkpoint;
- wall time and memory for every setting.

The key comparison should be based on **certified policy regret**, not only training loss.

---

## 13. Bespoke interval arithmetic remains a large trusted computing base

### R14-F9 — **Major: the second implementation is independent of the old certifier, but not independently rigorous in the strongest sense**

The R14 interval code is thoughtful. It uses:

- explicit nextafter outward widening;
- rational Taylor series for exp/log;
- exact rational interpretation of model decimals;
- dyadic interpretation of stored binary64 weights;
- rational Gauss-root isolation;
- analytic remainder bounds;
- fail-closed behavior on invalid cells.

I did not find an obvious local contradiction in the pieces audited.

However, the entire proof stack still depends on a substantial bespoke numerical kernel implemented in Python/NumPy plus assumptions about the floating-point environment. The 100-digit mpmath comparisons are useful diagnostics, but they are not a second formal interval proof.

For a computer-assisted numerical claim whose headline distinction is crossing a hard \(0.01\) threshold, an Econometrica-level paper should reduce the trusted computing base further.

### Required

Independently reproduce the decisive bounds using an established rigorous package or a materially different arithmetic foundation, for example:

- MPFR/MPFI;
- Arb;
- Julia IntervalArithmetic / validated numerics;
- a formally verified kernel;
- another outward-rounded library with documented elementary-function correctness.

The second implementation should cover the decisive full-node calculation, not merely three diagnostic high-precision points.

Agreement should be reported at the level of certified intervals and final rational/interval envelopes.

---

## 14. The \(0.01\) target lacks an economic normalization

### R14-F10 — **Major: “passes 0.01” is a numerical convention, not yet an economically interpretable accuracy criterion**

R14 improves this discussion considerably. It explicitly states that \(0.01\) is an absolute utility-unit tolerance and not scale free. It also reports strict-loss and relative-resolution diagnostics.

That concession is correct and important.

But it weakens the significance of the main “below 0.01” milestone. A method that returns \(0.009969\) has not thereby established an economically important level of accuracy unless the utility scale is calibrated or normalized.

The welfare-resolution calculations show the problem directly: some large price changes are separated, while nearby comparative statics remain unresolved.

### Required

Provide an economically interpretable error metric, such as:

- consumption-equivalent welfare loss;
- percentage wealth equivalent;
- normalized value error;
- a scale-free policy-loss measure.

Then report the verification frontier in those units.

The numerical tolerance should be justified by the economic question, not merely by the fact that a certificate can be made to fall just below a round threshold.

---

## 15. Methodological novelty is still below the claimed venue bar

### R14-F11 — **Blocking at Econometrica standard: the general theorem is classical in substance, while the strongest new machinery is application-specific**

The manuscript itself now says that the core stopped verification identity is classical. That is accurate.

The main general ingredients are:

- an a posteriori residual bound;
- a global continuous-action improvement gap;
- a stopping-boundary mismatch;
- a coefficient perturbation term.

These are useful to package and execute, but conceptually they are close to standard verification/supersolution arguments.

The sharper pieces are more specialized:

- the affine-preference market-deflator dual;
- the supporting-plane construction;
- the localization potentials;
- the four-corner initial-state/price continuation;
- the exact price-envelope calculation.

Those are interesting for this particular economy, but they do not yet amount to a broadly compelling new general numerical method.

R14 therefore occupies an awkward middle ground:

- the general neural theorem is executable but the neural solver is inaccurate;
- the accurate result is application-specific and non-neural;
- the broad high-dimensional promise is not certified;
- the classical numerical baselines are missing.

### Required

A future version needs at least one major new methodological result beyond packaging verification identities. Examples include:

- a convergent certified neural policy-iteration scheme;
- adaptive domain certification with proved complexity;
- a theorem linking training error to certifiable error under checkable conditions;
- a scalable global action/state certification method;
- a certified high-dimensional benchmark where the neural approach materially improves the attainable accuracy/work frontier.

Without such an advance, the paper is better characterized as a careful validated-numerics case study than as a new general numerical methodology.

---

## 16. Mathematical-real network versus deployed numerical implementation

### R14-F12 — **Major: the neural certificate is for an exact-real tanh network plus an abstract action-output error contract**

R14 is explicit about this limitation.

The certificate treats:

- stored binary64 weights as exact dyadic reals;
- tanh as an exact mathematical function;
- action outputs within a specified \(2^{-24}\) neighborhood.

It does **not** certify:

- the actual platform tanh implementation;
- a floating-point inference graph;
- an SDE simulator;
- budget reconstruction;
- an execution stack.

This is acceptable for a theorem about a mathematical policy, but it is weaker than a deployment-level guarantee.

### Required

Clarify the target claim.

If the paper claims certified mathematical policy functions, the present scope is acceptable but should remain explicit.

If it claims auditable deployed numerical control, then the floating-point inference and action implementation must be included in the proof object.

---

## 17. Economic scope remains too small for the claimed numerical ambition

### R14-F13 — **Major: the flagship certified dynamic problem is a two-state, short-horizon stylized economy**

The economic example is useful as a controlled test bed. It has:

- two continuous state variables;
- three controls;
- one-year normalized horizon;
- an artificial first-exit liquidation fee;
- no empirical calibration presented as part of the main numerical claim.

A top computational-economics contribution need not always use a massive empirical model. But when the methodological claim concerns neural methods and high-dimensional dynamic control, a two-state example is not sufficient—especially when the neural method is less accurate than the structured comparator.

### Required

Add at least one economically recognizable model where:

- state dimension is materially larger;
- classical tensor methods are genuinely stressed;
- policy/value accuracy remains verifiable;
- the neural algorithm solves rather than merely proposes a candidate;
- the comparison is against serious state-of-the-art alternatives.

---

## 18. Technical comments on the new constructions

These are not my primary reason for rejection, but they should be addressed.

### R14-T1 — The bridge theorem should be explicitly positioned as verification, not convergence

Theorem 1 is an a posteriori implication conditional on global residual/action/boundary inequalities. It does not show that the proposed training algorithm can attain those inequalities.

Keep the distinction explicit everywhere, including title/abstract language.

### R14-T2 — Report the conservatism decomposition under cover refinement

For the neural certificate, separate:

- true candidate residual error;
- interval dependency overestimation;
- action-oracle overestimation;
- boundary approximation error;
- output-neighborhood allowance.

The current tables show totals but do not fully quantify which component is structural and which is interval wrapping.

### R14-T3 — Boundary-satisfying architectures should be the first ablation

The terminal boundary is built into the critic, while the first-exit faces are not. Since the trace dominates the certificate, a hard boundary construction is the most obvious numerical repair and should be evaluated before claiming the training method has been meaningfully tested.

### R14-T4 — The price-library node-selection process needs a predeclared rule

The final exact envelope is reproducible given the nodes. The process by which the 18 historical nodes were chosen is not fully regenerated.

A future end-to-end run should define adaptive refinement based on a transparent criterion and stop only when that criterion is met.

### R14-T5 — The state rectangle should not be described as evidence of broad state-space accuracy

It is mathematically nondegenerate, but numerically tiny relative to the full state domain. Report its size relative to the original domain and avoid rhetorical inflation.

### R14-T6 — Distinguish model-specific dual efficiency from general solver efficiency

The dual verifier dominates fresh time-control runtime and is highly specialized. Its success does not establish that the same framework scales to unrelated HJBs.

### R14-T7 — Report certified policy differences, not only value regret

For economics, researchers often care about controls. A value-regret certificate can coexist with materially different policies in flat objective regions. Report verified policy ranges or economic action errors where possible.

### R14-T8 — The coefficient-transport result inherits the quality of the base certificate

The executed transport around the neural object gives approximately \(23.53\), so it demonstrates mechanics rather than useful robustness. The paper should not present this as an economic robustness success.

### R14-T9 — The direct time-control frontier needs an upper-bound frontier too

The unchanged upper endpoint across 16/32/64 slabs makes the bottleneck obvious. A complete accuracy study should separately refine the dual/upper relaxation and show how the combined gap changes.

### R14-T10 — The high-precision cross-check is diagnostic, not a proof

The paper already says this. Preserve that wording and do not allow tables/abstract summaries to imply otherwise.

### R14-T11 — Preserve negative historical comparisons

The current revision does this correctly. Future revisions should continue to retain the clipped-feedback result and unstable seed orderings.

### R14-T12 — Keep exact and rounded endpoints clearly separated

The exact rational breakpoint calculations are a strength. Any displayed decimal used for a theorem statement should remain outward rounded and traceable to the exact stored object.

---

## 19. What would be required for another Econometrica-level review

I would not recommend another referee round based only on tighter prose, another verification implementation, or a larger collection of historical files.

A scientifically meaningful next revision should satisfy the following gates.

### Gate A — Immutable review object

- Materialized remote commit.
- Canonical manuscript and supplement directly in the tree.
- Exact source/result/build hashes.
- No self-mutating bootstrap branch as the reviewed object.

### Gate B — Successful neural numerical solution

- Multiple seeds and materially larger training budgets.
- Boundary-aware architecture or equivalent algorithmic repair.
- Complete full-domain certificate for the actual neural policy.
- Certified regret in an economically meaningful range, not \(23.49\).

### Gate C — Accuracy/work frontier

- Several target accuracies.
- Candidate generation plus verification cost.
- Memory and hardware.
- Clear convergence/refinement mechanism.

### Gate D — Strong same-problem classical comparators

- At least two credible state-space solvers.
- Matched accuracy.
- Same stopping contract and economic model.
- End-to-end cost.

### Gate E — State-space significance

- Accurate feedback on a substantial state-time region.
- Not only \(t=0\).
- Not only a tiny initial-state rectangle.

### Gate F — Independent rigorous arithmetic cross-check

- Established validated-numerics package or formally checked kernel.
- Full decisive node set.
- Final envelope independently reproduced.

### Gate G — End-to-end reproduction of the strongest sharp result

- No inherited policy library as an unexplained starting object.
- Regenerate proposal, selection, verification, and continuum envelope from the model specification.

### Gate H — Economic interpretation

- Scale-normalized welfare error.
- Policy implications with certified resolution.
- At least one nontrivial higher-dimensional economic application if high-dimensional motivation is retained.

Absent these items, another revision would likely repeat the current pattern: stronger evidence that the verification machinery is careful, but no evidence that the advertised neural numerical solver is competitive.

---

## 20. Recommendation

**Reject.**

This recommendation is not based on a hidden implementation failure. In fact, the strongest aspect of R14 is that the new audit makes the limitations visible.

The paper has moved from an earlier state in which different certificates were easy to conflate to a much cleaner state in which the central facts are explicit:

1. the neural actor/critic can now be verified end to end;
2. that neural policy is currently very inaccurate under the complete certificate;
3. the sharp \(<0.01\) result is produced by a specialized non-neural time-control/dual pipeline;
4. the useful state extension is small and initial-state-indexed;
5. the paper still lacks matched strong state-space baselines;
6. there is no convincing high-dimensional full-state certification result;
7. the strongest historical library is not regenerated end to end;
8. the general verification theorem is useful but classical in substance.

Those are scientific, not editorial, deficiencies.

The most promising part of R14 is the discipline of separating proposal, evaluation, upper comparison, and certification. That architecture could support an excellent future paper. But at the Econometrica numerical-method bar, the current manuscript still needs the central missing result: **an accurate, competitive, reproducibly generated neural solution whose own complete certificate supports the methodological claim.**
