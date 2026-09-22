# Referee Report — Neural Bellman Operators, Revision R16

**Venue standard:** Econometrica-level numerical / computational methodology  
**Recommendation:** **Reject in the present form. R16 is a serious scientific revision, but it still does not establish that Neural Bellman Operators are an accurate or competitive numerical method for the flagship nonlinear economy.**  
**Review date:** 2026-09-23  
**Remote revision target:** revision/econometrica-r16-certified-policy-iteration-2026-09-23  
**Revision head reviewed:** 2932b74dad6d8d9efce5a114d5098a99ea17ab1f  
**Canonical manuscript:** ECTA_R16.tex / ECTA_R16.pdf  
**Canonical supplement:** SUPP_R16.tex / SUPP_R16.pdf  
**Previous review input:** bb09ac177fc766aea8aba26cb6a40b8aff68528c  
**Review branch:** review/econometrica-r16-numerical-methods-2026-09-23

## 1. Executive assessment

R16 is materially better than R14. It addresses several of the previous report's concrete requests rather than merely adding another certification wrapper. In particular, the revision:

1. proves a genuine stopping-trace inconsistency in the unchanged flagship economy;
2. introduces a signed accessibility-weighted verification theorem and an executable boundary-aware neural architecture;
3. runs ten predeclared seeds at two widths and two checkpoints, certifying all twenty original-economy neural objects;
4. implements controlled Markov-chain and semi-Lagrangian state-space candidate generators;
5. adds a coupled inventory control problem with up to 128 state coordinates and a state-global quadratic certificate;
6. regenerates the full sharp price continuum from model-only numerical starts;
7. recomputes all eighteen historical price-library nodes with MPFR-directed arithmetic;
8. gives a finite discounted approximate policy-iteration recurrence;
9. introduces an explicit consumption-top-up interpretation of the sharp non-neural welfare gap; and
10. preserves adverse results rather than hiding them.

These are genuine improvements.

Unfortunately, the new evidence makes the central venue problem even clearer.

The flagship nonlinear Neural Bellman Operators solver still does not come remotely close to its declared accuracy target. Across all twenty original-economy neural checkpoints, the certified time-zero regret bounds range from

[
28.547310950704542
]

to

[
102.35556930408907,
]

against a target of (0.01). Even the best reported neural certificate is therefore about 2,855 times the target.

More damagingly, increasing the training budget from 800 to 2,400 actor updates makes the certificate worse for **all ten seeds**. The mean certificate rises from about 36.95 to 77.39. The deterioration ratio ranges from approximately 1.74 to 2.34, with median about 2.13. This is not merely a failure to demonstrate monotone convergence. It is direct evidence that the current sampled actor/critic objective is systematically misaligned with the worst-case quantity the paper ultimately claims to certify.

The paper understates this point. It says that a larger optimization budget “does not uniformly tighten” the certificates. In fact, under the predeclared R16 experiment, it uniformly loosens them across all ten seeds.

The new boundary-aware construction is mathematically interesting, but R16 does not demonstrate that it improves numerical accuracy. The matched first-seed 800-update all-face hard-trace ablation has a signed finite-resolution certificate of approximately 28.1955, while the accessibility-aware 800-update network has approximately 30.1947. This does not contradict the trace-discontinuity theorem, because the theorem concerns the impossibility of vanishing global positive residual in the all-face class. But it does show that the principal new architectural idea has not yet been shown to improve the numerical method at the finite budgets actually used.

The accurate result in the original nonlinear economy is still delivered by another method class. The fresh model-to-price-library calculation achieves a uniform bound of approximately

[
0.009981645275,
]

and the complete historical MPFR recalculation gives approximately

[
0.009969007707.
]

These are important validated computations, but they belong to a deterministic time-control / specialized dual pipeline, not to the neural actor/critic.

The new 128-state inventory example does not close the high-dimensional neural-method gap either. Numerically, the network sees **time only** and outputs **two scalar gain functions**. The entire (d)-dimensional control problem is analytically reduced to two invariant Riccati modes, and one learned gain pair is reused for (d=4,8,16,32,64,128). A structure-aware classical method therefore solves two scalar Riccati equations. The retained classical RK45 diagnostic takes about 0.037 seconds. This is a useful correctness example, but it is not evidence that a neural Bellman method has solved a genuinely high-dimensional nonlinear dynamic program.

The new classical baselines also do not satisfy the R14 request for strong matched-accuracy same-problem comparison. Both candidate generators are forced to use the same wealth-distance portfolio factor as the neural architecture, narrowing the policy class relative to the original admissible controls. More importantly, all six policies are certified with the same inaccurate neural critic. Their reported regret bounds, roughly 48.93–49.70, are therefore dominated by a poor common witness and cannot be interpreted as a meaningful accuracy frontier for the classical methods.

Finally, the new “certified neural policy iteration” theorem is a finite discounted MDP perturbation bound. The contraction ingredients are classical, the theorem is not specific to neural representations, it is not executed by the R16 neural training algorithm, and its constants deteriorate severely as (q=e^{-ho h}	o1). It therefore does not provide a convergence result for the continuous-time neural solver studied in the paper.

I did not find an obvious local mathematical contradiction in the new stopping-accessibility proof or the quadratic inventory certificate during this audit. The reason for rejection is not that the new theorems are visibly false. The reason is that the manuscript still does not establish the central scientific proposition expected from an Econometrica-level numerical-method paper: an accurate, reproducibly generated, competitively benchmarked neural solution method for a problem where the neural component is actually needed.

I therefore recommend rejection.

---

## 2. Review-target integrity

The R16 review object is materially better organized than several earlier revisions.

The exact branch head reviewed is:

2932b74dad6d8d9efce5a114d5098a99ea17ab1f

with commit message:

publication(r16): validated manuscript PDFs, complete result tables and preservation manifests

The revision provides:

- ECTA_R16.tex and ECTA_R16.pdf;
- SUPP_R16.tex and SUPP_R16.pdf;
- R16_REVIEW.md;
- a point-by-point response to R14;
- result manifests;
- preserved scientific source and result commits;
- machine-readable summaries;
- complete retained neural, baseline, inventory, fresh-library, and MPFR artifacts.

The publication manifest explicitly distinguishes the review-base commit, scientific-source commit, scientific-result commit, and publication commit. The R16 branch also preserves previous scientific files.

### R16-F0 — Resolved: the current review object is materialized and provenance-pinned

The version-integrity objection is not a reason for the present negative recommendation.

The scientific objections below apply to the fully materialized R16 object.

---

## 3. What R16 genuinely fixes from R14

The revision deserves explicit credit for several items.

### 3.1 The upper-wealth trace problem is now mathematically diagnosed

Proposition 1 establishes a strict continuation-value jump exceeding 6.37 utility units at the inward upper wealth boundary under the unchanged economy. This is a useful observation. It explains why an all-face hard-Dirichlet critic class is inconsistent with vanishing uniform positive Bellman residual.

The proof is transparent: it uses an explicit feasible policy and an elementary probability bound, not an estimated optimal value.

### 3.2 The boundary correction is constructive

The portfolio architecture makes the upper wealth face inaccessible for the candidate policy, while the critic matches settlement on reachable faces and dominates settlement at the inaccessible upper face. The signed facewise verification theorem correctly separates which sign of a trace discrepancy matters under the optimal upper comparison and under the candidate policy.

This is substantially more informative than merely increasing a boundary penalty.

### 3.3 The original neural experiment is now genuinely multi-seed

R16 uses ten fixed seeds, alternating widths 16 and 32, and retains both the 800- and 2,400-update checkpoints. Every checkpoint is independently certified. No favorable seed is substituted after seeing the outcome.

This satisfies the procedural part of the earlier request.

### 3.4 Fresh generation of the sharp price continuum is now end to end

The new fresh-price pipeline begins from model constants, deterministic numerical initializations, and the two endpoint prices. It does not read inherited actors, dual pilots, or the historical intermediate node list. Adaptive node selection is predeclared and all attempts are retained.

This resolves an important reproducibility objection.

### 3.5 The complete historical node set is recomputed with MPFR-directed arithmetic

The entire eighteen-node historical library is re-evaluated with 128-bit MPFR directed rounding, including directed binary64 endpoint conversion. This is materially stronger than the earlier high-precision spot checks.

The revision is also appropriately explicit that the MPFR calculation shares the economic derivation, quadrature mathematics, stopping inequalities, and exact envelope logic. It is an arithmetic cross-check, not an independent proof of every upstream premise.

### 3.6 The paper no longer hides the classical structure of the inventory extension

The inventory example explicitly says that a structure-aware classical solver needs only two scalar Riccati equations. This is scientifically honest.

### 3.7 The economic tolerance is no longer presented as intrinsically meaningful

The consumption-top-up construction at least defines an interpretation before quoting a percentage. The paper also correctly says that this is externally financed in-kind compensation, not a budget-feasible wealth equivalent.

These corrections make R16 much easier to assess. They do not, however, rescue the central numerical-method claim.

---

## 4. Decisive numerical facts

| Object | R16 numerical result | Scope | Referee interpretation |
|---|---:|---|---|
| Best original-economy neural checkpoint | 28.5473109507 | Full state-time cylinder, (k=2) | Complete certificate, but about 2,855 times the 0.01 target |
| Worst original-economy neural checkpoint | 102.3555693041 | Same | Catastrophic relative to stated accuracy target |
| Mean 800-update neural certificate | about 36.95 | Ten seeds | Already unusable at target scale |
| Mean 2,400-update neural certificate | about 77.39 | Ten seeds | More training systematically worsens certification |
| Seed 16100, 2,400 updates, coarse cover | 54.0040458428 | 1,024 cells | Poor candidate plus substantial enclosure error |
| Same fixed network, refined cover | 32.1573203269 | 8,192 cells | Refinement helps, but remains thousands of times above target |
| All-face hard-trace ablation, 800 updates | 28.1954718646 | 1,024 cells | Finite-budget certificate is slightly better than matched accessible 800 network |
| Markov-chain candidate bounds | 48.96–49.45 | Three refinements | Dominated by common bad critic; not matched-accuracy evidence |
| Semi-Lagrangian candidate bounds | 48.93–49.70 | Three refinements | Same limitation |
| Inventory final neural loss | (2.53	imes10^{-5}) to (9.56	imes10^{-5}) per coordinate | Structured LQ model | Accurate, but problem reduces to two scalar gain ODEs |
| Inventory total loss at (d=128) | about 0.00324–0.01224 | Ten final checkpoints | Not uniformly below 0.01 in total welfare units |
| Fresh original-economy price library | 0.009981645275 | Central state, all (kin[0.5,8]) | Accurate, reproducible, non-neural |
| Historical MPFR price library | 0.009969007707 | Same | Accurate, arithmetic-audited, non-neural |
| Fresh-library compensation bound | about 1.033% | Externally financed consumption top-up | Defined, but not conventional budget-feasible CEV |

The central numerical facts are therefore still unfavorable to the paper's advertised neural methodology.

---

## 5. Blocking scientific findings

### R16-F1 — Blocking: the flagship Neural Bellman Operators solver still fails the central accuracy test by orders of magnitude

The core problem from R14 remains unresolved.

The original nonlinear economy is the only problem in the paper where:

- the dynamic programming problem is genuinely nonlinear;
- the stopping geometry is nontrivial;
- the neural actor/critic architecture is intended to matter;
- the verifier operates over a nontrivial state-time rectangle; and
- the proposed “Neural Bellman Operators” identity is scientifically tested.

On this problem, every neural checkpoint fails.

The best bound is about 28.55. The target is 0.01.

The magnitude matters. This is not a paper sitting slightly outside a tolerance because of a conservative interval enclosure. The gap is several orders of magnitude.

A numerical-method contribution cannot be rescued merely by saying that the verifier honestly detects failure. Honest failure detection is useful evidence for the verification component. It is not evidence that the proposed solver works.

#### Required

A future neural-method revision needs an actual successful flagship solve.

At minimum:

1. a predeclared sequence of materially different approximation/training budgets;
2. multiple independent seeds at each relevant configuration;
3. certification of all selected checkpoints over the full original state-time domain;
4. a demonstrated decrease in certified regret with increasing work;
5. final neural accuracy in an economically meaningful regime;
6. a clear explanation of which algorithmic ingredient causes the improvement;
7. no substitution of the time-control/dual method or the inventory LQ example for the original nonlinear neural result.

Without this, the paper should be reframed primarily as a verification / validated-numerics paper rather than a successful neural Bellman solver paper.

---

### R16-F2 — Blocking: the R16 training procedure is systematically anti-aligned with certified accuracy

R16 provides unusually strong negative evidence here.

For every seed 16100–16109,

[
	ext{certificate}_{2400} > 	ext{certificate}_{800}.
]

The deterioration is not small. The ratio ranges roughly from 1.74 to 2.34.

This matters because the training histories do not show an analogous systematic explosion in the sampled critic residual. For many seeds, the sampled residual MSE at 2,400 updates is lower than at 800 updates, while the complete certificate is dramatically worse.

This is precisely the type of failure mode the paper argues average residual training can miss. But the manuscript does not yet convert that diagnosis into a numerical algorithm.

At present, R16 demonstrates:

> the sampled actor/critic training objective is not a reliable surrogate for the worst-case quantity used to certify the final policy.

That is a central methodological failure, not a side observation.

#### Required

The next method must use the certificate information operationally.

Possible routes include:

- certificate-aware early stopping;
- adaptive worst-cell sampling;
- adversarial state/time sampling driven by verified residual boxes;
- direct minimization of a certified upper surrogate;
- alternating policy improvement with globally verified acceptance tests;
- trust-region updates rejected when the complete certificate worsens;
- a genuine certified policy-iteration loop.

The resulting procedure should show a reproducible accuracy-versus-work trend. A theorem about what would happen **if** (epsilon_n) and (eta_n) decreased is not enough when the actual training procedure makes the certificate systematically worse.

---

### R16-F3 — Blocking: the new boundary architecture is mathematically justified but not numerically validated as an improvement

The trace-discontinuity theorem is one of the strongest new mathematical results in R16.

However, the numerical ablation does not show that the proposed accessibility-preserving approximation space improves the actual finite-budget solver.

For seed 16100 at 800 updates:

- accessibility-aware certificate: about 30.1947;
- all-face hard-trace ablation: about 28.1955.

Thus the hard-trace ablation is slightly better at the finite resolution actually used.

Again, this does not contradict the theorem. The theorem excludes a **vanishing-residual sequence** in the all-face class. It does not say every finite all-face network must have a worse certificate than every accessibility-aware network.

But that distinction is exactly why a numerical-method paper needs a proper ablation.

R16 currently proves that the new class removes a structural asymptotic obstruction. It does not show that the proposed training procedure can exploit that larger class to produce a better policy.

#### Required

Run a controlled multi-seed ablation with:

- matched initialization logic;
- matched width/depth;
- matched optimizer budget;
- matched sampling;
- identical verification grids and refinement;
- several training budgets;
- certificate decomposition by signed residual and action gap.

Demonstrate that the accessibility-aware class improves the **certified policy result**, not merely that its trace term is analytically zero.

If it does not, the paper should present the construction as a correctness repair, not as demonstrated numerical progress.

---

### R16-F4 — Blocking: “certified neural policy iteration” is not the algorithm used in the paper

Theorem 3 is a finite discounted MDP perturbation inequality. Its ingredients are standard:

- Bellman contraction;
- approximate policy evaluation;
- approximate greedy improvement;
- resolvent bounds.

The paper itself acknowledges that the contraction ingredients are classical.

More importantly, the theorem is not an analysis of the R16 neural training procedure.

The actual flagship training code performs:

- three sampled critic-residual Adam updates;
- one sampled actor Hamiltonian Adam update;
- no global acceptance test;
- no complete evaluation-defect check between policy iterations;
- no certified improvement-defect check used to accept or reject a new policy;
- no discretization-transfer error budget inside the optimizer.

The theorem therefore proves a conditional statement about an algorithm that is not actually executed.

There is an additional numerical problem. In a continuous-time discretization with (q=e^{-ho h}), the constants

[
(1-q)^{-1}, qquad (1-q)^{-2}
]

explode as (h	o0). The theorem explicitly contains

[
rac{2qepsilon_n}{(1-q)^2}.
]

For fine time steps, tiny one-step defects would be needed before this bound becomes informative. R16 does not instantiate this scaling with the discretizations used in the paper.

#### Required

Either:

1. implement the theorem as an actual certified policy-iteration algorithm and report its defects, acceptance decisions, convergence, and continuous-time transfer error; or
2. remove “neural policy iteration” from the methodological center and present the theorem as a general auxiliary lemma.

A conditional finite-MDP recurrence does not establish convergence of the current continuous-time neural algorithm.

---

### R16-F5 — Blocking for the high-dimensional motivation: the 128-state inventory example is numerically a two-scalar-ODE problem

The inventory section is carefully written, and the quadratic certificate appears internally coherent. The problem is its significance.

The model has exactly two invariant modes:

- an orthogonal mode;
- a mean mode.

The optimal policy is characterized by two scalar Riccati gains.

The neural network:

- takes one scalar input: time;
- outputs two scalar gains;
- is trained only against two scalar Riccati differential residuals;
- is reused unchanged at every reported state dimension.

No (d)-dimensional state vector is fed to the network.

No high-dimensional HJB is approximated.

No high-dimensional state cover is constructed.

No high-dimensional policy-learning problem is solved.

The (d=128) result is obtained by algebraically lifting the same two scalar learned functions to a 128-dimensional linear feedback.

A structure-aware classical calculation solves the same two scalar Riccati equations. The retained RK45 diagnostic reports about 0.037 seconds, while the neural runs take several seconds plus certification.

This is a valid demonstration of a state-global analytic certificate. It is not a convincing high-dimensional neural Bellman benchmark.

The total loss also grows linearly with dimension. At (d=128), the retained final total bounds range up to approximately 0.01224. The strongest headline is obtained by dividing by dimension and reporting per-coordinate loss.

Per-coordinate normalization can be reasonable for an extensive quadratic objective, but it should not be confused with dimension-free total accuracy.

#### Required

If high-dimensional motivation remains central, add a genuinely high-dimensional dynamic model in which:

- the neural policy depends on the high-dimensional state;
- the value/policy cannot be reduced analytically to two scalar modes;
- the nonlinear dynamic programming problem is not exactly LQ;
- serious classical alternatives are implemented;
- the neural method achieves a competitive verified accuracy/work frontier;
- certification semantics remain rigorous.

Otherwise, narrow the high-dimensional claim to “analytic lifting of a certified low-dimensional gain approximation.”

---

### R16-F6 — Blocking: the new classical baselines are not strong matched-accuracy baselines

R16 technically implements two conventional state-space schemes:

- controlled Markov-chain approximation;
- semi-Lagrangian weak Euler approximation.

This is progress over R14.

But the experiment still does not answer the relevant comparison question.

#### 6.1 The policy class is artificially narrowed

The baseline code multiplies the portfolio head by

[
(2-x)/1.5,
]

exactly as in the neural candidate architecture.

The paper acknowledges that the resulting candidate class is narrower than the original admissible control class.

That choice is convenient because it inherits the upper-boundary inaccessibility property. It is not a neutral implementation of a classical HJB solver for the original unrestricted policy problem.

A strong classical method should be allowed to exploit the full original control set and handle the discontinuous stopping trace correctly rather than being forced into the neural policy parameterization.

#### 6.2 The common critic destroys the comparison

All six baseline policies are evaluated using the same seed-16100 final neural critic.

That critic is itself inaccurate.

The resulting continuous-time bounds cluster around 49 regardless of whether the grid is 9, 17, or 25 nodes per axis. They do not produce a meaningful matched-accuracy frontier.

The paper says that a common witness makes the comparison interpretable. I disagree with that formulation. It makes the **verification contract common**, but when the witness is very poor it prevents the experiment from revealing the actual relative quality of the policies.

The discrete central values improve materially with state/time refinement, but those values are explicitly uncertified.

Thus the paper has neither:

- a trustworthy classical convergence curve; nor
- a matched certified comparison with the neural policy.

#### Required

Implement at least two serious classical solvers without the neural policy restriction.

For each method:

1. solve the original action problem;
2. use a numerically appropriate treatment of the inward stopping boundary;
3. generate a method-specific value approximation or independent upper/lower comparison object;
4. validate the transferred continuous-time policy;
5. report accuracy versus end-to-end work;
6. compare at matched certified accuracy.

A poor common critic should not be allowed to collapse every baseline into the same uninformative 49-unit certificate.

---

### R16-F7 — Blocking: there is still no convergence or accuracy-versus-work frontier on the flagship nonlinear problem

An Econometrica-level numerical-method paper needs more than a finite collection of validated objects. It needs evidence that increasing computational effort improves the object that is claimed to solve the economic model.

R16 does not provide that.

For the flagship neural solver:

- 800 to 2,400 updates worsens all ten certificates.

For fixed-network cover refinement:

- 54.00 falls to 32.16.

This shows that interval dependency matters, but it is verifier refinement around a fixed poor object, not solver convergence.

For the fresh time-control library:

- adaptive price-node refinement stops just below 0.01 by construction;
- the retained 16/32/64-slab experiment still fails to attain 0.005;
- the upper dual relaxation remains an accuracy floor.

For the state-space baselines:

- the common-witness bounds do not improve with grid refinement.

There is therefore no demonstrated sequence such as

[
10^{-2}, 5	imes 10^{-3}, 2.5	imes10^{-3}, 10^{-3}
]

on the unchanged nonlinear problem.

#### Required

Provide a true end-to-end accuracy/work curve in which the approximation object, not only the enclosure, improves.

The curve should report:

- candidate-generation time;
- verification time;
- memory;
- target accuracy;
- actual certified accuracy;
- state/time/control discretization or network complexity;
- all upper-comparison costs.

If the method hits an irreducible floor, explain the floor and provide a refinement that removes it.

---

### R16-F8 — Blocking for the current title/framing: the accurate original-economy solver remains non-neural

R16 deserves credit for no longer conflating numerical objects.

That makes the scientific identity problem unavoidable.

The two accurate original-economy continuum calculations are:

1. historical policies plus full MPFR verification: about 0.0099690;
2. fresh model-to-library generation: about 0.0099816.

Both use deterministic time controls and a specialized analytic dual.

The neural full-horizon feedbacks remain inaccurate.

Thus the strongest result in the flagship economy still belongs to the auxiliary comparator.

The fresh experiment closes the R14 reproducibility objection. Scientifically, however, it strengthens the evidence that the successful method is the specialized time-control/dual construction.

#### Required

The paper must choose one of two identities.

**Neural-method identity:**  
The neural solver itself must become accurate and competitive.

**Validated-control identity:**  
The paper should center the general certification architecture and the specialized primal/dual numerical method, treating neural training as one candidate generator that currently fails on the flagship model.

The current title and methodological emphasis demand the first standard.

---

### R16-F9 — Major: the MPFR cross-check reduces arithmetic risk but leaves a substantial shared trusted mathematical base

R16 substantially improves the arithmetic audit.

The MPFR backend performs directed operations and elementary functions at 128 bits, and all eighteen nodes are recomputed.

However, the following remain shared:

- economic derivation;
- primal/dual analytic formulas;
- rational Gaussian quadrature construction and remainder arguments;
- stopping corrections;
- exact price-envelope mathematics;
- Python indexing and data plumbing;
- the MPFR/C ABI interface.

The manuscript correctly discloses this.

This is no longer the main reason for rejection. But the result should continue to be described as independent arithmetic, not independent end-to-end mathematical verification.

If the authors want a computer-assisted theorem to carry a large part of the paper's novelty, a formalized or independently derived validation path would still be valuable.

---

### R16-F10 — Major: the new compensation metric is explicit but not a conventional economic welfare equivalent

The new normalization is an improvement over treating 0.01 as self-interpreting.

But the quantity is unusual.

The experiment:

- holds wealth fixed;
- holds the stopping path fixed;
- holds preference and adjustment-cost paths fixed;
- injects proportional consumption from outside the budget.

The resulting approximately 1.033% top-up is therefore not:

- a consumption-equivalent variation under the original budget constraint;
- a wealth-equivalent welfare loss;
- a policy-feasible compensating variation;
- an empirical calibration.

The paper says this explicitly, which is good.

However, the metric cannot support a strong economic claim beyond a scale-normalized bound.

The fact that the sharp non-neural result corresponds to a sufficient externally financed top-up of about one percent also shows that “below 0.01” is not obviously a negligible economic error.

#### Required

For an Econometrica-level empirical/economic interpretation, provide a conventional welfare metric where possible:

- budget-feasible CEV;
- wealth equivalent;
- normalized value loss tied to economically meaningful benchmark variation;
- calibrated policy effects.

If the special top-up metric is retained, keep it secondary.

---

### R16-F11 — Blocking at the claimed methodological level: the new general theory remains too disconnected from numerical success

R16 adds more genuine mathematics than R14, especially the stopping-trace inconsistency and accessibility-weighted theorem.

Still, the general contribution remains fragmented.

- The stopped verification identity is classical in substance.
- The accessibility theorem is useful but tailored to policy-specific stopping geometry.
- The policy-iteration recurrence is classical finite-MDP perturbation theory and is not implemented.
- The inventory certificate exploits exact quadratic structure.
- The sharp original-economy result uses an application-specific affine-preference dual.

This is a strong collection of validated-numerics constructions.

It is not yet a convincing new general numerical algorithm with demonstrated superiority or convergence.

#### Required

A future version should contain at least one central result of the form:

- a convergent certified neural policy-iteration algorithm that is actually executed;
- an adaptive global certification procedure with proved work/accuracy behavior;
- a theorem connecting a trainable objective to the certified Bellman/policy error under checkable conditions;
- a scalable verification mechanism on a genuinely high-dimensional nonlinear dynamic model;
- a matched-accuracy benchmark showing a real neural advantage.

Without such a result, the contribution is better characterized as a careful computational verification study than a new general numerical methodology.

---

### R16-F12 — Major: exact-real neural certification remains separate from deployed floating-point inference

The paper is appropriately explicit that its neural certificate concerns:

- exact dyadic stored weights;
- mathematical tanh/softplus;
- a specified bounded output perturbation;
- portfolio perturbation applied before the wealth-distance factor.

It does not certify:

- a platform libm tanh;
- a floating-point inference graph;
- an SDE simulator;
- an execution engine.

This is acceptable if the claim is purely about mathematical policy functions.

It is not a deployment certificate.

This distinction is not a reason for rejection by itself, but it must remain explicit.

---

### R16-F13 — Major: the flagship economic model remains too small and stylized to carry the broader numerical ambition

The original economy has two continuous states and three controls on a one-year normalized horizon.

It is a useful test bed because it exposes a real stopping-boundary pathology.

But a top numerical-method paper motivated by neural methods and high-dimensional dynamic programming needs more.

The new inventory model does not fill the gap because of its two-mode Riccati reduction.

There is still no economically recognizable nonlinear higher-dimensional model on which:

- the neural method is necessary;
- a classical tensor method is genuinely stressed;
- the neural policy is state dependent in high dimension;
- the result is accurately certified.

#### Required

Add a genuinely higher-dimensional nonlinear economic application or narrow the paper's ambition substantially.

---

## 6. Additional technical comments

### R16-T1 — Correct the description of the 800-to-2,400 update experiment

The text says the larger budget “does not uniformly tighten” certificates.

The data show something stronger:

**all ten seeds deteriorate.**

This should be stated directly.

### R16-T2 — The sampled training loss is not a meaningful stopping criterion

The histories show that sampled residual behavior and certified worst-case behavior can move in opposite directions.

The paper should quantify this mismatch rather than only discussing it qualitatively.

### R16-T3 — The refined seed-16100 certificate shows that verifier overestimation is still large

The fixed 2,400-update network improves from about 54.00 to 32.16 when the cover grows from 1,024 to 8,192 cells.

This is a large change.

A paper making claims from a 1,024-cell certificate should quantify whether further refinement converges to 30, 10, 1, or another value. The current single refinement does not establish the asymptotic verification floor.

### R16-T4 — The all-face ablation should use more than one seed

One seed does not establish the practical value of the new approximation space.

The theorem establishes asymptotic inconsistency of the all-face class, but the numerical claim needs a multi-seed finite-budget ablation.

### R16-T5 — The baseline restriction should be highlighted in the main comparison table

The classical policy generators use the neural wealth-distance portfolio factor.

This is not a minor implementation detail. It narrows the candidate class and should appear prominently in the main table/caption, not only in prose.

### R16-T6 — A common inaccurate witness does not create a useful solver comparison

A shared upper witness can help standardize verification, but when it dominates every bound it prevents the table from measuring solver quality.

Use stronger policy-specific evaluation witnesses and a common independently certified optimal upper bound, or another matched scheme.

### R16-T7 — The inventory classical comparator should itself be rigorously validated

The current RK45 reference is labeled diagnostic, which is correct.

Because the problem reduces to two scalar Riccati equations, producing a validated interval ODE benchmark should be straightforward. That would make the comparison scientifically cleaner and likely emphasize how easy the problem is classically.

### R16-T8 — Per-coordinate inventory loss and total welfare loss should be equally visible

At (d=128), the largest retained final total bound is above 0.01 even though every per-coordinate final bound is below 0.001.

The abstract is technically accurate, but the main narrative should avoid allowing per-coordinate normalization to be read as dimension-free total welfare accuracy.

### R16-T9 — Instantiate the policy-iteration constants at the actual time-step scales

Because (q=e^{-ho h}), the factors in Theorem 3 become very large for small (h).

Report numerical values of the amplification constants for representative (h) used by the state-space methods. This would make clear how demanding the theorem's defect requirements are in continuous-time approximations.

### R16-T10 — The fresh price library stops immediately after crossing the declared 0.01 threshold

That is consistent with the predeclared rule and not improper.

But it means the experiment demonstrates threshold attainment, not convergence.

A second target such as 0.005 should be pursued by changing the actual upper relaxation, not only adding nodes.

### R16-T11 — The MPFR agreement should not be used to validate shared analytic premises

The manuscript currently avoids this error. Preserve that language.

### R16-T12 — Keep the exact-real versus machine-policy contract explicit

In particular, an additive deployed portfolio error after multiplication by the wealth-distance factor is outside the proof.

This is an important implementation qualification.

### R16-T13 — Report policy differences on the original nonlinear model

Value regret is important, but economic users also care about controls.

Where the sharp time-control library or state-space policies are available, report certified ranges or discrepancies for consumption, preference adjustment, and portfolio decisions.

### R16-T14 — The paper still needs a clearer answer to “what is the NBO algorithm?”

At present, “NBO” can refer to:

- sampled actor/critic training;
- global verification;
- signed boundary treatment;
- a finite-MDP policy-iteration theorem;
- a specialized price dual;
- an LQ gain-residual trainer.

These are different objects.

Define one executable core algorithm and separate optional verification/comparison modules around it.

---

## 7. Status of the R14 gates

The R14 report proposed several gates before another Econometrica-level review. R16's status is:

### Gate A — Immutable review object

**Closed.**

R16 is materialized and provenance-pinned.

### Gate B — Successful neural numerical solution

**Open.**

The original neural solver remains orders of magnitude above the declared target.

### Gate C — Accuracy/work frontier

**Open.**

The flagship neural certificates systematically worsen with more training. No convergent end-to-end frontier is shown.

### Gate D — Strong same-problem classical comparators

**Partially implemented, scientifically still open.**

Two state-space candidate generators now exist, but they use a restricted neural-style portfolio class and an inaccurate common neural witness. No matched certified comparison is obtained.

### Gate E — State-space significance

**Open for the flagship nonlinear solver.**

The original full-domain neural certificate is broad but inaccurate. The accurate price-library result remains initial-state/time-control based.

### Gate F — Independent rigorous arithmetic cross-check

**Substantially closed at the arithmetic layer.**

All historical nodes are recomputed with MPFR-directed arithmetic. Shared analytic premises remain.

### Gate G — End-to-end reproduction of the strongest sharp result

**Closed for the fresh 0.01 price-library result.**

The fresh model-to-library experiment begins without inherited policy/pilot/node data.

### Gate H — Economic interpretation and nontrivial higher-dimensional application

**Partially open.**

An explicit compensation metric is supplied, but it is externally financed and uncalibrated. The 128-state inventory problem is analytically a two-mode Riccati system and does not constitute a genuinely high-dimensional nonlinear economic application.

The most important gates—B, C, D, and the substantive part of H—remain open.

---

## 8. What would justify another top-venue referee round

I would not recommend another round based on:

- more manifests;
- more arithmetic regression tests;
- another historical-library replay;
- additional prose distinguishing scopes;
- more seeds under the same failing objective;
- another structured problem reducible to a handful of scalar ODEs.

A scientifically meaningful next revision should instead clear the following gates.

### Gate R17-A — Accurate neural solution of the unchanged nonlinear economy

The actual neural policy must achieve a rigorous full-domain regret in a useful range.

The tolerance should be economically justified, not merely selected because a comparator can barely cross it.

### Gate R17-B — Certificate-aware solver convergence

Show that increasing computational work improves certified policy quality.

The solver should use global/certified information operationally rather than only after training.

### Gate R17-C — Matched classical baselines

Implement unrestricted conventional solvers on the same economy and compare at matched certified accuracy with full end-to-end cost.

### Gate R17-D — Implemented certified policy iteration or remove the central claim

If the finite-MDP recurrence is meant to be a core contribution, execute an algorithm satisfying its defects and carry the analysis to the continuous-time problem.

### Gate R17-E — Genuine high-dimensional nonlinear control

Use a model whose neural policy depends on a genuinely high-dimensional state and that cannot be analytically collapsed to two scalar modes.

### Gate R17-F — Standard economic welfare interpretation

Add a budget-feasible or otherwise conventional welfare normalization when possible.

### Gate R17-G — A single coherent methodological identity

State precisely whether the paper's main contribution is:

- a neural solver;
- a verification framework;
- a specialized primal/dual validated solver;
- or a combination with a clearly defined interface.

The numerical evidence must support the chosen identity.

---

## 9. Recommendation

**Reject.**

R16 is a much stronger and more scientifically disciplined revision than R14.

It resolves important issues of provenance, arithmetic auditing, end-to-end price-library generation, multi-seed reporting, and stopping-boundary logic.

But the central problem remains.

The manuscript is titled **Neural Bellman Operators** and is framed as a numerical methodology for dynamic economics. On the only genuinely nonlinear flagship problem, the neural solver's best certified bound is about 28.55 against a target of 0.01, and all ten seeds become worse when training is extended from 800 to 2,400 updates.

The new accurate neural example is a quadratic inventory model that analytically reduces to two scalar Riccati equations. The new classical baselines do not yield matched accuracy and are handicapped by the same boundary-oriented portfolio class and a poor common neural witness. The new policy-iteration theorem is not the algorithm actually executed. The sharp original-economy solution continues to come from the non-neural time-control/dual pipeline.

Those facts do not support an Econometrica-level claim of a successful new neural numerical method.

The most valuable direction is now clear. The authors should stop spending the next revision primarily on certification wrappers around already-known numerical objects and instead solve the missing scientific problem: construct a neural algorithm whose own **complete certificate improves with work and reaches economically useful accuracy on the unchanged nonlinear economy**, then compare it fairly against unrestricted classical solvers.

Until that result exists, the paper remains an impressive validated-numerics and failure-diagnosis study around a neural solver that has not yet demonstrated the numerical capability claimed by its title.
