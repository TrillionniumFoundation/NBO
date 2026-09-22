# Referee Report — Neural Bellman Operators, Revision R12

**Venue standard:** Econometrica-level numerical/computational methods  
**Recommendation:** **Reject in the present form; a new submission would require a substantial reconception rather than another incremental revision.**  
**Review date:** 2026-09-22  
**Reviewed branch:** `revision/econometrica-r12-uniform-cost-certification-2026-09-22`  
**Reviewed commit:** `4ff0404833a6d6773bcf7afab361013d732df686`  
**Main paper:** `ECTA_R12.pdf` / `ECTA_R12.tex`  
**Preservation supplement:** `SUPP_R12.pdf` / `SUPP_R12.tex`

## 1. Executive assessment

R12 is a material scientific improvement over the R9 version that I reviewed previously. Several earlier objections have been addressed rather than merely renamed. In particular:

1. the original continuous first-exit economy now has an explicit primal/dual certificate below the declared (0.01) regret threshold at (k=.5,2,8);
2. the cost parameter is extended from three nodes to a certified continuum (kin[.5,8]) through an exact affine-envelope calculation;
3. the manuscript now reports the weak and unfavorable parts of the external holdout rather than hiding them;
4. method-specific tuning has been expanded and the earlier tuning-boundary concern is directly examined;
5. a separate reference-solvable accuracy suite has been added;
6. the non-enumerative action certifier is implemented on a structured nonconvex family up to 128 action dimensions;
7. failure preservation, immutable source/result/build identities, and clean-checkout replay are substantially improved; and
8. the paper now states more explicitly that several theorems are a posteriori verification results rather than convergence theorems for Adam/RMSprop.

Those are real advances.

However, the revision now exposes a more fundamental problem that was less visible in R9: **the strongest certified scientific result is no longer a result about the neural Bellman algorithm advertised by the title.** The economically important certificate is obtained for sixteen-slab deterministic time controls with (p=0), followed by output polishing, exact stopped policy evaluation, and a model-specific market-deflator dual. The neural training trajectory is not part of the validity proof. The whole-state neural residual certificate in Theorem `r9:bridge` is not executed in the flagship economy. The high-dimensional action oracle is executed only at isolated frozen jets in a separate synthetic family. The reference-solvable accuracy study uses a different linear gain actor and a different optimization problem.

Thus the manuscript currently contains a strong **validated numerical certificate for one stochastic-control application**, a collection of useful verification components, and several separate neural experiments. It does **not yet establish Neural Bellman Operators as an Econometrica-level numerical method** with an end-to-end, state-space, accuracy-versus-computation theory and implementation.

I therefore recommend rejection in the present form. A credible resubmission is possible, but it should be rebuilt around one clear methodological claim and one complete end-to-end chain.

---

## 2. What I regard as genuinely resolved since R9

Before listing the remaining blockers, I want to be explicit about what should **not** be recycled as criticism from the prior report.

### 2.1 The flagship continuous-economy gap is no longer 8–14

R10/R12 provide lower and upper bounds for the unchanged stopped economy, with reported regret uppers approximately

- (0.00987440) at (k=.5),
- (0.00971727) at (k=2), and
- (0.00996896) at (k=8).

This is a qualitatively different object from the loose R8/R9 witness. The old objection that the main economic model is uncertified at useful precision is therefore no longer accurate as stated.

### 2.2 The continuum-(k) calculation is not a sampled-grid claim

Theorem `r12:envelope` is mathematically correct in its basic architecture: fixed-policy payoffs are affine in (k), the optimum is a supremum of affine functions and hence convex, policy lower lines can be transferred using expenditure bounds, and the convex value chord provides an upper bound between certified nodes. The final envelope is checked at exact rational breakpoints, not only at the training prices.

The final reported uniform bound,
[
0.009994024846927508<0.01,
]
is therefore not merely a dense-grid interpolation statement.

### 2.3 The R9 external holdout is now reported honestly

The paper now states that the dimension-16 panels do not establish a robust seed-level ordering and that the simple clipped quadratic-feedback baseline has lower mean cost than both learned methods. This is the correct direction of revision.

### 2.4 The tuning-boundary issue was substantively investigated

The R11 method-specific tuning experiment expands the scalar learning-rate range and varies consequential method-specific parameters under an equal nominal tuning budget. The selected learning-rate multipliers are no longer at the old boundary. This is a meaningful response to the prior report, even though it does not establish global tuning optimality.

### 2.5 Evidence retention and immutable identities are much better

The publication receipt pins source, result, build, review, and final PDF identities. The repository now distinguishes exploratory/local records from the clean-checkout replay. This is substantially more auditable than the earlier mutable branch-level evidence.

The remaining report therefore focuses on **new first-order issues**, not on pretending that R12 is still R9.

---

## 3. Blocking finding R12-F1: the flagship certified result is not a certified Neural Bellman policy

This is the central objection.

The policies used in the R12 continuum certificate are sixteen-slab deterministic time controls. For example,
`revisions/2026-09-22-r12/results/cases/k4.25/actor_k4.25.json`
records:

- `slabs: 16`;
- deterministic arrays for (c_t) and (	heta_t);
- (p_t=0) on every slab;
- `algorithm: L-BFGS-B output polishing with exact differentiable budget projection`; and
- `training_scope: finite time-control class; output polishing is not a claim of Adam convergence`.

The lower bound is then obtained by `original_policy_certificate.py`, which explicitly states that **no learned critic is used**. The upper bound is supplied by `flexible_dual.py`, a model-specific affine-preference market-deflator witness.

This is a legitimate and interesting validated-control calculation. But it does not demonstrate that the Neural Bellman Operator algorithm produced and certified a state-feedback neural solution to the dynamic program.

The present title and framing create a category error:

> neural training proposes an initialization or policy candidate, while the scientifically decisive object is a small deterministic time-control vector that is independently polished and certified.

That is much closer to **validated stochastic control with neural initialization** than to an end-to-end neural Bellman method.

### Required

Choose one of two intellectually clean directions.

**Option A — make the neural method the object of the theorem.**  
Certify the actual state-feedback neural actor/critic over a nontrivial state domain, including residual, neural derivative, action-oracle, boundary, and deployment allowances.

**Option B — reframe the paper.**  
Present the contribution as a validated primal/dual certification framework for stochastic control, in which a neural solver is one optional policy generator among several. In that case the title, abstract, theorem hierarchy, and numerical comparison should be rewritten accordingly.

The current hybrid framing is not acceptable for a top numerical-methods paper.

---

## 4. Blocking finding R12-F2: the original economic guarantee is pointwise in the initial state, not a solved policy function

Every economically important certificate is explicitly attached to
[
(t,u,x)=(0,2,1.25).
]

The continuum-(k) theorem is uniform over the **cost coefficient**, but not over states. The final `envelope.json` even correctly records the scope as:

> “Every real adjustment price in [0.5,8], central initial state ... no claim of uniformity over initial states.”

For an economic dynamic program, a numerical method should normally produce and validate a policy/value object over a relevant state region, not only one scalar value at one initial condition.

This matters because:

1. a pointwise certificate cannot be used to evaluate the policy from nearby states without a new proof;
2. it does not establish the quality of a learned feedback map;
3. it does not show how error behaves near the economically important liquidation boundaries;
4. it does not test whether the method is robust to the state distribution induced by alternative initial conditions; and
5. it prevents a meaningful comparison with standard HJB or dynamic-programming solvers, which naturally return a value/policy surface.

### Required

Provide at least one of the following:

- a certified state-domain value/policy enclosure on a nontrivial rectangle;
- a verified finite cover of economically relevant initial states with a uniform error bound;
- or a theorem plus executed calculation showing how pointwise certificates can be propagated or cheaply recomputed over the state domain.

A single central-state scalar, even when rigorously enclosed, is not sufficient evidence for a general numerical Bellman method.

---

## 5. Blocking finding R12-F3: Theorem `r9:bridge` remains an interface theorem, not an executed end-to-end neural certificate

The manuscript's most relevant theorem for connecting neural outputs to rigorous regret is the cover-and-oracle theorem `r9:bridge`. It requires, over a state-time cover:

- policy-evaluation residual bounds;
- cell-modulus bounds;
- a global action oracle;
- neural jet/derivative allowances;
- stopping-trace error; and
- assembly of these quantities into a whole-policy regret bound.

But the flagship economic result does not execute this theorem for the neural critic. Instead it uses an independently fitted analytic/polynomial witness and a separate dual.

The high-dimensional action oracle is executed on isolated frozen gradients in the synthetic rank-one-coupled family. The manuscript explicitly acknowledges that this is **not** a whole-state neural PDE residual.

This leaves the core method claim incomplete:

> the paper proves an interface for certifying a neural Bellman object, but never certifies the neural Bellman object that matters most.

### Required

Run the complete bridge on an actual stored neural policy/value pair over a nontrivial state domain. The result need not be as tight as the specialized economic dual, but it must demonstrate that the advertised neural verification architecture is computationally operational as a full pipeline.

---

## 6. Blocking finding R12-F4: “independent replay” is a reproducibility check, not an independent numerical verification

The R12 evidence package repeatedly uses the word “independent” for the clean-checkout replay. But
`revisions/2026-09-22-r12/replication/recheck.py`
imports exactly the same core certifiers:

- `original_policy_certificate`
- `flexible_dual`

and recomputes the same quantities, then checks agreement with the stored node data to (10^{-13}).

That is useful for:

- clean-checkout reproducibility,
- dependency drift detection,
- file-integrity checking, and
- workflow completeness.

It is **not** independent algorithmic verification. Any shared bug in the policy evaluator, dual integrator, localization allowance, primitive inequalities, or interval conversion is reproduced by the “independent” replay.

This issue is unusually important because the final tolerance margin is extremely small; see R12-F5.

### Required

Provide a genuinely independent cross-check for the decisive certificates, for example:

- a second implementation of the primal and dual bounds using a different interval package and code path;
- a high-precision implementation that does not import the production certifier;
- a proof-assistant or formally checked core inequality for the delicate parts;
- or an independently coded PDE/Monte Carlo/dual verification that encloses the same scalar values.

The present package is reproducible, but it is still single-implementation science.

---

## 7. Blocking finding R12-F5: the final continuum certificate passes by only about (5.98	imes10^{-6})

The final uniform regret is

[
0.009994024846927508,
]

so the distance to the declared threshold (0.01) is only

[
0.01-0.009994024846927508
=5.975153072492	imes10^{-6}.
]

This is approximately **0.06% of the target**.

The exact rational envelope computation is not the concern. Once the node inputs are valid, the hull computation is straightforward. The concern is the upstream chain that produces those inputs:

- polynomial utility approximation;
- stopped-exit correction;
- interval arithmetic;
- Gaussian moment integration;
- supporting-plane verification;
- covariance correction;
- variance allowance;
- localization potentials;
- source quadrature;
- binary64 endpoint export;
- and fitting of the model-specific witness.

A one-code-path replay cannot provide a persuasive safety argument when the final acceptance margin is only six parts in a million in objective units.

### Required

Do not stop at the first pass below (0.01). Produce a materially separated certificate, for example below (0.009), or demonstrate a rigorous robustness study under:

- substantially finer quadrature;
- higher working precision;
- independently enlarged primitive bounds;
- alternate interval arithmetic;
- and perturbed witness coefficients.

A top-journal numerical certificate should not sit on the acceptance boundary when the entire proof depends on custom numerical code.

---

## 8. Major finding R12-F6: the generation path is not reproduced end-to-end from the pinned source

The publication receipt is admirably explicit that the adaptive case records retain `local-development` provenance labels and that the clean replay validates the **frozen policy and dual**, not retraining/refitting.

For mathematical validity, this is enough: a feasible policy plus a valid dual certificate does not need a reproducible optimizer history.

For a **numerical-method paper**, it is not enough. The scientific question includes whether the stated method reliably generates those objects, at what computational cost, and with what tuning.

The R12 clean replay does not re-run:

- neural training;
- L-BFGS-B policy polishing;
- dual pilot fitting;
- adaptive refinement from scratch;
- interrupted attempts; or
- the complete stopping rule under a fresh immutable source execution.

### Required

Add an end-to-end clean execution that starts from the pinned source and produces the final certified library, including all fitting, polishing, refinement decisions, failures, retries, and final proof objects.

If exact bitwise reproduction is not possible, define and verify a deterministic scientific acceptance criterion for the generated certificate.

---

## 9. Blocking finding R12-F7: there is no accuracy-versus-computation frontier for the flagship original economy

R12's “frontier” is a **parameter-node refinement frontier**. It shows that adding certified cost nodes reduces the worst continuum-(k) envelope gap from about (0.0240) to (0.009994).

That is not the same thing as a numerical-method convergence frontier.

At each node, the primal/dual gap remains near the (0.01) level. The finite-refinement theorem is explicitly conditional on future nodes having local slack. The paper does not demonstrate that the original-economy certificate can be driven to

- (0.005),
- (0.0025),
- (0.001),

or any other tightening by increasing witness richness, policy richness, quadrature resolution, neural capacity, or computation.

The current result therefore establishes:

> “we found a certificate just below one chosen tolerance,”

not:

> “we understand how computational work controls error in the flagship problem.”

### Required

For the unchanged original economy, report a true accuracy frontier. Vary the relevant approximation/certificate controls and show:

- certified regret width;
- total generation cost;
- total verification cost;
- memory;
- witness/policy complexity;
- and failure rate.

The main paper needs a convergence story for the object it claims to solve.

---

## 10. Major finding R12-F8: the reported R12 computation time is not end-to-end and is not suitable for method comparison

The R12 frontier reports roughly 325 seconds of “cumulative successful task-seconds,” but the file itself states that this number excludes:

- the three inherited certificates;
- interrupted attempts;
- overlapping parallelism;
- inherited network training;
- witness fitting outside the counted stage;
- imports;
- setup; and
- some other one-time computation.

This is useful engineering metadata, but it is not the computational complexity of the method.

For a numerical-method contribution, especially one that emphasizes constructive certification, the reader needs:

- total wall-clock time from a clean start;
- total CPU/GPU seconds;
- number of cores;
- memory;
- all failed/refinement attempts;
- policy-generation time;
- dual-fitting time;
- verification time;
- final PDF/evidence generation time only as secondary metadata.

### Required

Provide a full resource ledger and separate:

1. policy generation;
2. witness/dual construction;
3. rigorous verification;
4. parameter continuation;
5. failed/refined attempts.

Without this, the paper cannot support computational-efficiency claims.

---

## 11. Major finding R12-F9: the continuum-(k) theorem is a useful specialized envelope argument, not a general Neural Bellman continuation method

Theorem `r12:envelope` works because the cost coefficient appears affinely as
[
J_k(pi)=A(pi)-kB(pi),
]
and the admissible policy set and dynamics do not change with (k).

That is an elegant and useful exploitation of this model. But it is not a general parameter-continuation theory for Neural Bellman Operators.

The theorem does not address parameters that alter:

- drift or volatility;
- state constraints;
- discounting;
- action constraints;
- boundary conditions;
- preferences non-affinely;
- transition kernels;
- or equilibrium mappings.

The manuscript should therefore avoid presenting the continuum result as evidence of general parameterized dynamic-programming capability.

### Required

Either narrow the claim to **affine objective parameters with a common policy set**, or generalize the theorem to a broader class with explicit modulus/transport bounds.

---

## 12. Major finding R12-F10: a uniform (0.01) policy-regret guarantee does not imply uniformly resolved comparative statics in (k)

The paper correctly resolves some large effects, such as the reported (2	o8) welfare loss. But for nearby prices (p<q), the true economic difference (V(p)-V(q)) can be far smaller than (0.01).

Thus the statement that the policy library supports a “continuum of cost counterfactuals” should be interpreted carefully. It supports a policy with a uniform absolute regret bound. It does **not** imply that every local welfare comparison along the continuum is economically resolved.

The envelope can easily be accurate enough for control deployment while too wide for derivative-like or local comparative-static conclusions.

### Required

Report a continuum diagnostic for economic resolution, for example:

- certified width of (V(p)-V(q)) as a function of (|p-q|);
- secant/slope intervals;
- regions in which sign and magnitude are resolved;
- and regions in which only policy near-optimality is certified.

Do not conflate uniform policy regret with uniform comparative-static precision.

---

## 13. Blocking finding R12-F11: the external comparison still does not support a claim of numerical superiority

The manuscript now reports the evidence more honestly, but the underlying fact remains important.

In the R11 method-specific tuning experiment:

- only the (d=8) panel establishes the declared robust seed-level ordering;
- the (d=16) and (d=32) panels do not;
- a simple independently specified clipped-feedback baseline has lower mean cost than both neural pipelines in every new panel.

The older frozen experiment also contains a non-robust dimension-16 result.

This is not fatal if the paper is about certification rather than superiority. But it means the comparative experiment cannot carry the methodological contribution.

### Required

Remove any residual implication that NBO is empirically superior as a general solver. If comparative superiority is an intended contribution, broaden the evidence dramatically and include stronger baselines.

---

## 14. Blocking finding R12-F12: the paper does not compare against the strongest relevant classical numerical methods on the same flagship problem

The paper cites classical verification, monotone approximation, Markov-chain approximation, sparse grids, and primal/dual control methods. But the numerical experiments do not compare NBO/certification against such methods on the **same original low-dimensional economy**.

The flagship state dimension is only two. That is precisely the regime in which one should be able to run serious classical baselines:

- finite differences / monotone HJB schemes;
- semi-Lagrangian schemes;
- controlled Markov chains;
- adaptive sparse grids;
- direct policy iteration;
- PDE residual methods;
- and primal/dual bounds.

Without this comparison, it is difficult to know what the neural machinery contributes in the one problem where rigorous accuracy is claimed.

### Required

Run at least two strong non-neural numerical baselines on the unchanged original economy and report:

- accuracy;
- policy quality;
- wall-clock;
- memory;
- behavior near first exit;
- and ability to reproduce the certified welfare comparisons.

A top numerical-methods paper cannot compare mainly to one neural competitor when the principal example is two-dimensional.

---

## 15. Major finding R12-F13: the LQ absolute-accuracy suite validates a different algorithmic object

The R11 reference-solvable suite is a useful test of exact held-action error decomposition. But it does not validate the same NBO solver used in the external comparison.

The experiment uses:

- linear gain outputs;
- time gates;
- independently known Riccati structure;
- a quadratic Bellman constructor;
- and Adam optimization over gain outputs.

The manuscript itself correctly says that this is not the width-48 tanh actor used in the external benchmark.

Therefore the result

> “below (0.003) at 128 decisions”

is an accuracy result for a structured actor class in a reference-solvable LQ family. It is not evidence that the general tanh NBO actor/critic converges to similar accuracy.

### Required

Add a reference-solvable suite using the **same neural architecture and training pipeline** as the main NBO experiments. Measure true regret against the exact solution while varying training budget, network width/depth, deployment mesh, and verification effort.

---

## 16. Major finding R12-F14: the 128-dimensional action certificate is not a 128-dimensional dynamic-control solution

The scalar global partition theorem is useful. It exploits a special structure:

- all nonconvex coupling is through the scalar sum (z=sum_i a_i);
- the remaining subproblems are strongly convex;
- the global search is therefore one-dimensional.

The 128-dimensional calculation certifies one frozen Hamiltonian instance / gradient, not a 128-dimensional state-space stochastic control problem.

This distinction is stated in places, but the paper still risks giving an exaggerated impression of high-dimensional control scalability.

### Required

Describe the result as a **high-dimensional action-oracle experiment for a rank-one-coupled Hamiltonian**. Do not use it as evidence that the full Bellman method scales to 128 state dimensions unless a complete high-dimensional control problem is solved and certified.

---

## 17. Major finding R12-F15: the novelty boundary is clearer, but the remaining general theory is still too thin for Econometrica

The revised related-work section is much better. It explicitly acknowledges that:

- stopped verification is classical;
- policy iteration is classical;
- primal/dual bounding is classical;
- Riccati completion is classical;
- the continuation result uses standard convexity of a supremum of affine functions.

That honesty improves the paper.

But it also sharpens the novelty question.

At present, the main mathematical pieces are:

1. a classical stopped one-sided comparison theorem;
2. a generic cover-and-oracle bookkeeping theorem;
3. a highly model-specific affine-preference dual;
4. a structured scalar branch-and-bound action oracle;
5. a simple affine-parameter envelope theorem; and
6. several separate empirical studies.

The most original part appears to be the **specific dual/witness construction for this economic model**, not a broadly applicable Neural Bellman convergence or certification theorem.

### Required

State one theorem-level methodological contribution that applies to a recognizable class of stochastic economic models beyond this one parameterization. Give assumptions that can be checked outside the present example and at least one additional nontrivial application.

If no such theorem is intended, reposition the paper as a computational economics application with validated numerics rather than a general numerical-method paper.

---

## 18. Major finding R12-F16: historical preservation has become an editorial anti-pattern

The repository's preservation discipline is excellent for research provenance. It is not an appropriate constraint on the scientific manuscript.

`validate_revision.py` explicitly checks that **every inherited R11 main-text line survives as an ordered subsequence** of the R12 main text. The preservation supplement is 148 pages and reproduces complete earlier manuscripts and supplements.

This makes version control a manuscript-design rule.

A serious journal revision must be allowed to:

- delete obsolete exposition;
- rewrite claims;
- merge repeated arguments;
- remove dead branches;
- shorten historical detours;
- and reorganize the paper around the final scientific contribution.

The repository can and should preserve every earlier version. The submitted paper should not.

### Required

Remove the “all previous lines must survive” validation rule from manuscript acceptance. Keep historical versions in Git. Write a clean final paper from scratch around the current contribution.

The supplement should contain only material needed to verify the final paper, not a museum of all prior versions.

---

## 19. Major finding R12-F17: the manuscript still tries to carry too many partially independent papers at once

The current submission combines:

- the stopped preference-adjustment economy;
- the specialized market-deflator dual;
- continuum-(k) certification;
- a synthetic nonconvex action family;
- a high-dimensional action oracle;
- a neural-vs-SOC holdout;
- a second tuning study;
- a separate LQ reference suite;
- preserved recursive-utility material;
- preserved sophisticated-self material;
- games;
- trace identities;
- historical counterexamples; and
- large preservation supplements.

The result is impressive as a repository, but diffuse as a paper.

For Econometrica-level publication, the reader should be able to answer:

> What is the one new method?  
> What theorem establishes it?  
> What experiment validates it?  
> What economic conclusion requires it?

That hierarchy is still unclear.

### Required

Choose one center of gravity and cut aggressively.

My preferred structure would be:

1. one general validated-control theorem;
2. one end-to-end neural implementation of that theorem;
3. one flagship economic application;
4. one classical numerical baseline comparison;
5. one reference-solvable accuracy suite using the same implementation;
6. a concise supplement with proofs and reproducibility details.

Everything else belongs in separate papers or the repository history.

---

## 20. Major finding R12-F18: exact rational post-processing cannot substitute for an independently audited upstream enclosure stack

The exact hull in `price_envelope.py` is a good design choice. But it can only be as valid as the node intervals supplied to it.

Those node intervals are produced by a mixed stack involving:

- `mpmath.iv`;
- custom binary64 outward arithmetic using `np.nextafter`;
- numerical partitioning;
- custom Gaussian-moment routines;
- Taylor remainder bounds;
- clipping logic;
- and several model-specific inequalities.

The code appears careful. I did not find an obvious algebraic error in the R12 envelope theorem or sign-sensitive transfer. But the standard required for a result that passes the target by only (5.98	imes10^{-6}) should be higher than “the same code re-ran successfully.”

### Required

For the decisive R12 node set:

- verify the primal bounds with a second interval implementation;
- verify the dual bounds with a second implementation or substantially different decomposition;
- document the floating-point model and every trusted-library assumption;
- and report a certificate with enough slack that one-implementation edge effects cannot determine acceptance.

---

## 21. Secondary comments

### 21.1 The economic model remains stylized

This is not by itself a rejection reason for a numerical-method paper, but it means the methods contribution must carry the submission. The paper should not rely on the economic calibration as an independent reason for Econometrica-level significance.

### 21.2 The (0.01) target needs stronger motivation

The target is now met, but it remains largely a declared tolerance. The paper should link the tolerance to economically meaningful loss scales, policy loss, or decision thresholds rather than treating (0.01) as a purely engineering target.

### 21.3 The policy library is useful but should be characterized economically

For each selected policy region in (k), report the width of the price interval over which the same policy is chosen and how the controls change across active policies. This would make the continuum construction more interpretable.

### 21.4 The failure archives are useful but should not dominate the paper

Keep them in the repository and reproducibility appendix. They should not determine the narrative structure of the journal submission.

### 21.5 The negative external results are scientifically valuable

The fact that the simple baseline beats both neural methods and that tuning changes the apparent ranking is useful evidence. Preserve it. The correct conclusion is that certification and solver ranking are different questions.

---

## 22. Minimum conditions for a credible new submission

### P0 — decide what the paper is

Either:

- certify an actual neural Bellman policy/value object end-to-end; or
- reframe the paper as a validated stochastic-control certification method with neural policy generation as optional.

Do not continue with the current ambiguous identity.

### P0 — execute a whole-state neural certificate

Run the cover/residual/jet/action/boundary machinery on a stored neural policy and critic over a nontrivial state domain.

### P0 — obtain genuinely independent numerical verification

Recompute the decisive original-economy primal and dual bounds with a second implementation and create a materially larger margin below the target.

### P0 — produce an original-economy accuracy/computation frontier

Show how verified regret decreases as policy/witness/certificate complexity and computation increase. Report full end-to-end resource use.

### P0 — compare with strong classical methods on the same original economy

At least two serious non-neural baselines should be included.

### P1 — make the reference suite use the same NBO architecture

The exact-solution tests should evaluate the actual tanh actor/critic pipeline, not only linear gain outputs.

### P1 — narrow the high-dimensional claim

Present the 128-dimensional result as a structured action-oracle result unless a complete high-dimensional stochastic-control problem is solved.

### P1 — rewrite the manuscript cleanly

Remove the requirement that all prior text survive. Keep historical preservation in Git, not in the submitted prose.

### P1 — separate policy regret from comparative-static resolution

Map where the continuum-(k) certificate actually resolves welfare differences and where it does not.

---

## 23. Recommendation

**Reject in the present form.**

This recommendation is not based on the old R9 objection that the original economic problem has no useful certificate. R12 has made substantial progress and the central-state primal/dual bounds are now the strongest part of the project.

The rejection is instead based on a mismatch between the paper's claimed numerical method and the object actually certified.

The current end-to-end scientific chain is:

> neural or inherited candidate  
> (ightarrow) deterministic time-control polishing  
> (ightarrow) exact stopped policy evaluation  
> (ightarrow) model-specific dual upper bound  
> (ightarrow) pointwise central-state certificate  
> (ightarrow) affine cost-parameter envelope.

That is a defensible and potentially publishable validated-control computation.

It is **not yet** the chain implied by the title:

> neural Bellman training  
> (ightarrow) state-feedback neural policy/value  
> (ightarrow) whole-domain certified Bellman residual and global improvement  
> (ightarrow) controlled error-versus-computation frontier  
> (ightarrow) demonstrated advantage over serious alternatives.

A new submission should close one of these chains completely rather than adding more partially independent components.

---

## 24. Evidence reviewed

I reviewed the following repository state and records.

### Immutable review target

- branch `revision/econometrica-r12-uniform-cost-certification-2026-09-22`;
- commit `4ff0404833a6d6773bcf7afab361013d732df686`;
- publication receipt `revisions/2026-09-22-r12/publication_receipt.json`.

### Main manuscript and supplement

- `ECTA_R12.tex`;
- `ECTA_R12.pdf`;
- `SUPP_R12.tex`;
- `SUPP_R12.pdf`;
- `R12_REVIEW.md`;
- `revisions/2026-09-22-r12/response_to_referee.md`.

### R12 continuation theory and evidence

- `revisions/2026-09-22-r12/paper/main.tex`;
- `revisions/2026-09-22-r12/paper/continuation.tex`;
- `revisions/2026-09-22-r12/paper/continuation_proof.tex`;
- `revisions/2026-09-22-r12/results/envelope.json`;
- `revisions/2026-09-22-r12/results/frontier.json`;
- `revisions/2026-09-22-r12/results/refinement_history.json`;
- `revisions/2026-09-22-r12/validation_report.json`;
- `revisions/2026-09-22-r12/ci_results/status.json`;
- `revisions/2026-09-22-r12/replication/price_envelope.py`;
- `revisions/2026-09-22-r12/replication/cost_case.py`;
- `revisions/2026-09-22-r12/replication/recheck.py`;
- `revisions/2026-09-22-r12/replication/validate_revision.py`.

### Representative R12 case

- `revisions/2026-09-22-r12/results/cases/k4.25/actor_k4.25.json`;
- `revisions/2026-09-22-r12/results/cases/k4.25/status.json`;
- `revisions/2026-09-22-r12/results/cases/k4.25/dual_pilot_k4.25.json`;
- `revisions/2026-09-22-r12/results/cases/k4.25/flexible_dual_k4.25.json`.

### Inherited R10/R11 material used by R12

- `revisions/2026-09-22-r10/paper/flexible_dual.tex`;
- `revisions/2026-09-22-r10/paper/dual_proof.tex`;
- `revisions/2026-09-22-r10/replication/flexible_dual.py`;
- `revisions/2026-09-22-r9/replication/original_policy_certificate.py`;
- `revisions/2026-09-22-r11/paper/robustness_section.tex`;
- `revisions/2026-09-22-r11/paper/accuracy_section.tex`.

### Prior referee baseline

- prior numerical-methods referee input at commit `251ad29668788b2a911c4ca6f9c0a226886518d6`, blob `42cee0954515e5578dc579a4ca0428bb4e399b2e`.

The report is intentionally based on the pinned R12 state above and does not treat branch names alone as immutable evidence.
