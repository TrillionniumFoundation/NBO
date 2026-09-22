# Referee Report — Neural Bellman Operators, Revision R18

**Venue standard:** Econometrica-level numerical / computational methodology  
**Recommendation:** **Reject in the present form. R18 is a serious and unusually transparent revision, but it still does not establish Neural Bellman Operators as an accurate or competitive neural numerical method on the flagship nonlinear economy. The new evidence instead shows that most of the certified improvement is witness/critic improvement, while policy improvement remains unestablished.**  
**Review date:** 2026-09-23  
**Revision reviewed:** `revision/econometrica-r18-referee-copy-2026-09-23`  
**Revision head:** `49d286a174a7d3f71293adc920284584673f390b`  
**Canonical manuscript:** `ECTA_R18.tex / ECTA_R18.pdf`  
**Canonical supplement:** `SUPP_R18.tex / SUPP_R18.pdf`  
**Point-by-point response:** `RESPONSE_R18.tex / RESPONSE_R18.pdf`  
**Previous referee input:** `82af00bc296da59e8a3a28ef1bf86c1d6fca2367`  
**Review branch:** `review/econometrica-r18-numerical-methods-2026-09-23`

## 1. Executive assessment

R18 is materially stronger than R16. The authors did not evade the previous report. They changed the executed training objective, linked that objective to the complete certificate by a quantitative theorem, ran a matched multi-seed boundary ablation, removed the most obvious restrictions from the classical state-space baselines, gave those baselines method-specific witnesses, added a genuinely full-state nonlinear control example, and supplied a budget-feasible welfare compensation for the sharp non-neural library.

These are real improvements.

The central Econometrica-level problem nevertheless remains unresolved.

The flagship original-economy neural method still does not establish useful policy accuracy. The best final complete certificate is

[
7.27831906346675,
]

against the unchanged target

[
0.01.
]

Thus the best certified result is still about **728 times the declared target**. The fixed-network refinement experiment reaches approximately (7.25156), not a small-policy-error regime. More importantly, the new fixed-witness theorem shows that the final accessible critics themselves impose residual floors above approximately (6.27). This is not now primarily an interval-resolution problem.

The more serious scientific issue is what the successful certificate descent means. At the final checkpoint, the negative/policy-side certificate component is exactly zero for every reported accessibility-aware seed. The entire reported bound is the positive optimal-comparison component. For seed 17100, pairing the **initial actor with the final critic gives exactly the same bound** as pairing the final actor with the final critic:

[
7.339624178645005.
]

Pairing the final actor with the initial critic gives (23.718685694842687).

This is decisive evidence about the current experiment. R18 has demonstrated that the new objective learns a much better *witness*. It has **not demonstrated that the neural policy itself becomes materially better**. The authors are commendably explicit about this, but that candor does not remove the numerical-method requirement.

The new high-dimensional nonlinear inventory problem is also informative but does not rescue the neural-method claim. Its strongest theorem follows from global strong convexity and holds for **any bounded initialization, including an untrained one**. At 128 coordinates, zero-start gradient descent with the same 32 corrections attains a query certificate of approximately (2.06	imes10^{-14}), while neural initialization plus gradient correction gives approximately (1.63	imes10^{-14}). Accelerated gradient is better still, approximately (2.6	imes10^{-16}), with no training cost. The state-uniform theorem itself does not use learned quality. Scientifically, this is a clean strongly-convex control-plan optimization result with a neural warm start, not evidence that a neural Bellman operator is required.

I did not find an obvious local contradiction in the new accessibility theorem, objective-bridge theorem, finite-horizon defect allocation, nonlinear Hessian argument, or wealth-compensation proof during this audit. The negative recommendation is therefore not based on an identified mathematical error. It is based on the mismatch between the paper's methodological identity and what the validated numerical evidence now establishes.

My recommendation remains **Reject**.

---

## 2. Review-object integrity

The R18 review object is well organized and materially auditable.

The publication-pinned revision head is

`49d286a174a7d3f71293adc920284584673f390b`

with publication message

> publication(r18): validated manuscript PDFs, complete objective audit and preservation manifest

The revision provides the main paper, supplement, response, review entry point, source-preservation records, objective-bridge audit, numerical validation files, and reproduction scripts. The publication manifest distinguishes the previous review, R16 reviewed manuscript, R17 scientific source/result objects, R18 source object, and publication object.

The R18 audit also correctly states that R18 audits already executed R17 scientific runs rather than relabeling them as newly randomized R18 experiments.

### R18-F0 — Resolved: review-target integrity is not a reason for rejection

The scientific objections below apply to the materialized R18 object.

---

## 3. What R18 genuinely fixes

Several previous objections are now substantially addressed.

### 3.1 The sampled-loss anti-alignment is replaced by a certificate-aligned objective

R16 showed a striking failure: more sampled actor/critic training worsened all ten complete certificates.

R18 replaces that proposal objective with a complete-cover differentiable residual envelope. All 1,024 boxes enter every proposal update. At each checkpoint the frozen actor/critic is independently re-evaluated by directed arithmetic, and the complete bound, not the smooth training objective, determines incumbent acceptance.

Across all ten accessibility-aware seeds the raw bounds decrease at both declared transitions:

- initialization: approximately (26.30)–(26.67);
- 100 updates: approximately (7.53)–(10.59);
- 400 updates: approximately (7.278)–(7.344).

The improvement is not manufactured by discarding unfavorable proposals. This is a genuine improvement over R16.

### 3.2 The objective theorem actually concerns the implemented proposal graph

Theorem 4 (the trainable envelope / certified policy-loss bridge) is much better connected to execution than the old finite-MDP policy-iteration discussion. The endpoint correction (D) explicitly covers disagreement between proposal logits and independently certified residual endpoints. The R18 audit evaluates all 60 objects and reports the largest integrated correction below (1.20	imes10^{-13}).

This is a meaningful implementation bridge.

### 3.3 The boundary issue is now scientifically separated from finite-budget performance

The paper no longer implies that the accessibility-aware architecture must dominate the all-face architecture at finite work. The paired experiment shows exactly the opposite kind of nuance one should report: width 16 favors the accessibility-aware architecture in all five pairs, width 32 favors the all-face architecture in all five pairs, and the average difference is tiny.

The structural asymptotic result and the finite-budget optimization result are now correctly distinguished.

### 3.4 The classical baselines are less confounded than in R16

The Markov-chain and semi-Lagrangian generators no longer impose the neural interior wealth-distance multiplier. Each transferred policy gets its own witness and a complete continuous-time check against the original action set.

This removes two important design defects of R16.

### 3.5 The new nonlinear application really uses the full state

The new 8/32/128-dimensional nonlinear inventory problem is not the previous two-mode Riccati system. The neural map takes the complete state vector and outputs the complete (12d)-dimensional control plan. The potential is nonlinear and cross-coordinate coupled.

This is a genuine dimensional improvement.

### 3.6 The welfare normalization is materially better

The new (0.0078) initial-wealth compensation for the sharp deterministic time-control library is budget financed and accompanied by an explicit feasible policy adjustment. It is correctly described as sufficient rather than exact.

This is a better economic interpretation than the earlier externally financed top-up.

These improvements make R18 easier to evaluate. They also make the remaining issue sharper.

---

## 4. Decisive numerical facts

| Object | R18 result | Referee interpretation |
|---|---:|---|
| Best original-economy neural certificate | 7.2783190635 | About 728 times the 0.01 target |
| Worst final original-economy neural certificate | 7.3436650267 | Same order; all ten fail |
| Fixed seed-17100 cover refinement | 7.339624 → 7.280222 → 7.251560 | Verifier refinement helps modestly; does not approach target |
| Final accessible fixed-witness floor | roughly 6.275–6.320 | Current learned witnesses cannot certify the target by cover/precision refinement |
| Final negative/policy certificate component | 0 for all ten seeds | Final bound is entirely upper-comparison/witness side |
| Seed 17100 initial actor + final critic | 7.339624178645005 | Exactly equal to final actor + final critic |
| Seed 17100 final actor + initial critic | 23.718685694842687 | Main observed gain comes from critic/witness |
| Final accessible vs all-face ablation | width-dependent reversal | No demonstrated finite-budget benefit of accessibility architecture |
| MC/SL original-economy certificates | about 7.3145–7.7741 | Better comparison design, but no matched sharp accuracy |
| Nonlinear 128-d uniform bound, 32 corrections | (1.036	imes10^{-6}) | Strong certified optimization result |
| 128-d query: neural + gradient | (1.63	imes10^{-14}) | Excellent query certificate |
| 128-d query: zero + gradient | (2.06	imes10^{-14}) | Almost the same without training |
| 128-d query: accelerated gradient | (2.6	imes10^{-16}) | Better certificate without neural training |
| Neural training cost in nonlinear example | about 12.7 s | No demonstrated end-to-end advantage |
| Sharp original-economy library | below 0.01 | Accurate result remains non-neural |

The main methodological claim is therefore still not supported by the strongest validated evidence.

---

## 5. Blocking scientific findings

### R18-F1 — Blocking: the flagship neural method still fails the declared policy-accuracy requirement by more than two orders of magnitude

This is the most basic unresolved point.

The paper keeps the title **Neural Bellman Operators**, keeps the original nonlinear economy as the flagship problem, keeps the full-domain certification requirement, and keeps the 0.01 target.

The best final result is (7.278319).

The gap is not a minor constant-factor miss. It is roughly (728	imes) the declared tolerance.

The authors correctly refuse to rename the accurate deterministic time-control/dual library as a neural result. That honesty is important, but it leaves the central empirical proposition unproved.

#### Required for another top-venue round

A future revision should not be triggered by another certification wrapper around the present actors and critics. It should be triggered by a materially new solver object that reaches a genuinely useful full-domain accuracy regime on the unchanged economy.

At minimum:

1. multiple predeclared work levels;
2. multiple seeds;
3. complete certificates at every retained work level;
4. a policy-sensitive accuracy measure, not only witness-sensitive certificate descent;
5. final accuracy near the economically defended target;
6. end-to-end timing at that accuracy;
7. comparison against conventional solvers at the same certified accuracy.

---

### R18-F2 — Blocking: the new certificate descent is principally witness descent, not demonstrated policy improvement

This is the most important new finding created by R18 itself.

The supplement reports, for every final accessibility-aware seed, a zero negative/policy component. For example, seed 17100 moves from

[
16.983515 + 9.316999 = 26.300514
]

at initialization to

[
7.339624 + 0 = 7.339624
]

at 400 updates.

The same qualitative endpoint holds for all ten seeds: the final bound is entirely the positive optimal-comparison component.

Even more revealingly, the seed-17100 actor/critic interchange gives:

- initial actor + final critic: (7.339624178645005);
- final actor + final critic: (7.339624178645005);
- final actor + initial critic: (23.718685694842687).

Thus, for the one interchange experiment actually shown, the final actor is unnecessary for the reported final certificate.

This does **not** prove that the final actor is worse than the initial actor. It proves something different and directly relevant: the experiment does not establish that the actor got better.

A numerical method for policy computation cannot be validated merely by showing that a jointly trained upper/lower witness pair yields a smaller upper bound while the policy contribution becomes nonbinding.

#### Required

The next revision needs a policy-sensitive evaluation design. Suitable possibilities include:

- independently solving the fixed-policy linear evaluation problem with verified upper/lower bounds;
- holding an evaluation witness fixed while comparing actors;
- constructing certified policy-payoff lower bounds that can be ordered across actors;
- using actor-only interventions with identical critics;
- reporting all-seed initial-actor/final-critic and final-actor/initial-critic interchanges;
- measuring certified policy-improvement steps rather than joint actor/critic certificate decreases.

The paper itself proves in Proposition 5 that certificate acceptance need not imply policy improvement. The flagship experiment currently sits on exactly that identification problem.

---

### R18-F3 — Blocking: the central objective theorem is a valid a posteriori bridge, but it is not yet a policy-learning theorem

The trainable-envelope theorem is useful. It shows how a differentiable complete-cover surrogate plus an independently checked correction can upper-bound the complete policy-loss certificate.

But the theorem does not say that minimizing the surrogate improves the actor, nor that Adam converges, nor that joint actor/critic optimization approaches the optimal policy.

R18 openly states this.

That limitation becomes central because the observed improvement can be explained almost entirely by the critic.

The new objective has therefore solved the specific R16 pathology

> sampled loss can improve while complete certificate worsens,

but has not yet solved the harder methodological problem

> certificate-aware training produces increasingly accurate policies.

Those are not equivalent statements.

#### Required

A future method needs an optimization mechanism whose acceptance criterion is policy-sensitive. For example, one could alternate:

1. construct or update a verified upper witness;
2. improve the actor against a frozen witness or certified advantage;
3. accept the actor only if an independently verified policy lower bound improves;
4. refresh the witness separately.

A joint objective in which the critic can absorb essentially all of the numerical progress does not yet identify successful policy learning.

---

### R18-F4 — Blocking: the final learned witness family is still numerically in the wrong continuation regime

The fixed-witness theorem is one of the most useful additions in R18 because it prevents a misleading interpretation of further cover refinement.

The final accessible critics have upper-face trace excesses only about (0.052)–(0.097). The paper's own theorem then gives a positive-optimal-residual floor above approximately (6.27).

This is much larger than the 0.01 target.

The scientific implication is stronger than “the current certificate is loose.” The final witness is qualitatively too close to settlement at the inward upper-wealth face. The true continuation value has a jump exceeding 6.37 there, while the learned witness only lifts slightly above settlement.

Thus:

- more MPFR precision cannot fix the gap;
- much finer boxes cannot fix the gap;
- the present final witness itself must change substantially.

R18 correctly says this, but does not yet supply the algorithmic mechanism that produces such a witness.

#### Required

The next solver needs an explicit strategy for learning the continuation trace / upper witness rather than merely avoiding an inconsistent equality boundary condition.

Possible evidence would include:

- continuation-trace parameterization or adaptive boundary continuation targets;
- a separate upper-witness solve;
- verified trace-excess trajectories during training;
- a direct connection between the learned upper-face continuation lift and the reduction of positive Bellman residual.

Until then, the strongest theorem diagnoses the remaining failure rather than solving it.

---

### R18-F5 — Major: accessibility repair remains a correctness result, not a demonstrated finite-budget numerical advantage

The matched ablation is now adequate enough to answer the previous question.

It does not show a uniform practical advantage.

At width 16, accessibility-aware wins all five pairs. At width 32, all-face wins all five pairs.

This is perfectly compatible with the trace-consistency theorem. But it means the architecture should be sold as:

> a mathematically correct approximation-space repair that removes an asymptotic inconsistency,

not as an empirically superior finite-work architecture.

The manuscript is mostly careful about this. The abstract and introduction should remain equally careful in future revisions.

---

### R18-F6 — Blocking: the original-economy classical comparison is cleaner but still not a matched certified accuracy frontier

R18 fixes two serious R16 baseline confounds:

- unrestricted original interior action grids;
- method-specific witnesses.

However, the resulting bounds remain approximately (7.31)–(7.77), and the finest grids are not best. The paper itself says these bounds cannot rank true policy values.

Therefore the table still cannot answer the practical numerical-method question:

> At a target certified error (arepsilon), what work is required by NBO versus a standard controlled Markov-chain or semi-Lagrangian solver?

The current answer is: none of these methods reaches the target under the reported verification pipeline.

That is scientifically useful negative evidence, but it is not the matched-accuracy benchmark requested by the venue standard.

#### Required

The next comparison should produce at least one conventional solver with a sharp certified value/policy evaluation, so that the frontier is not dominated by weak witnesses.

A strong comparison could use:

- validated fixed-policy linear solves for each classical candidate;
- a common independently certified upper bound plus candidate-specific lower bounds;
- monotone PDE/SL error estimates with explicit continuous-time transfer;
- a verified adaptive refinement sequence.

Without a sharp comparator, one cannot tell whether the 7-unit floor reflects policy quality, witness quality, or both.

---

### R18-F7 — Blocking for the current methodological framing: the high-dimensional nonlinear result is primarily a strongly-convex optimization theorem, not evidence that a neural Bellman method is needed

The nonlinear 128-dimensional example is mathematically clean and is a real improvement over the two-mode Riccati example.

But its strongest guarantee is deliberately initialization-agnostic.

Theorem 7 proves that **every bounded initialization** converges under exact-real gradient correction with the same contraction factor. The cube-uniform bound at 32 corrections therefore holds even for an untrained bounded initializer.

The query data reinforce this:

- neural + gradient: about (1.63	imes10^{-14});
- zero + gradient: about (2.06	imes10^{-14});
- accelerated gradient: about (2.6	imes10^{-16}).

Online time is essentially the same for neural and zero-start gradient descent, while the neural version has an additional training cost of about 12.7 seconds.

At eight corrections the learned warm start is useful on the two fixed queries, but the paper does not establish an amortized break-even point or a matched-tolerance query distribution on which the offline training pays for itself.

More conceptually, the executed method optimizes the deterministic full-horizon control plan directly. Although the problem has a Bellman equation, the successful numerical theorem is not a neural Bellman-operator theorem.

#### Required

If this application is kept as central evidence for the neural methodology, the paper should show at least one of:

1. a state-uniform bound that actually uses learned approximation quality;
2. a provable reduction in required online corrections due to the neural initializer;
3. an amortized complexity advantage over classical initialization for a stated query distribution;
4. a regime where classical zero/accelerated starts cannot match the neural online work;
5. an application where the high-dimensional learned representation is doing more than supplying a warm start to a globally well-conditioned convex problem.

Otherwise, this section should be framed as a validated neural warm-start experiment rather than evidence for the main NBO algorithm.

---

### R18-F8 — Blocking at the current title/identity level: the strongest original-economy solver remains non-neural

The manuscript now separates its numerical objects more carefully than previous versions.

That makes the identity problem clearer.

On the original nonlinear economy:

- the neural full-state certificates are around 7.3;
- the sharp sub-0.01 result is delivered by the deterministic time-control / specialized dual library.

The latter is now reproducible, audited, and economically normalized. It is a strong validated-numerics result.

But it is not the method named in the title.

The paper cannot use the strong non-neural result to establish the success of Neural Bellman Operators, and to its credit it does not explicitly do so. The consequence is simply that the headline neural claim remains unsupported.

A future version must either make the neural solver itself accurate or reorganize the paper around the validated-control/certification contribution.

---

### R18-F9 — Major: the nonlinear high-dimensional application is still too favorable to classical optimization to establish broad numerical significance

The new nonlinear model is genuinely full-state, but it is:

- deterministic;
- finite horizon with only 12 dates;
- globally strongly convex in the entire control plan;
- sparse and explicitly differentiable;
- unconstrained in controls;
- solvable by cheap first-order or quasi-Newton methods with rigorous gradient-based suboptimality bounds.

This is an excellent environment for validating the certificate machinery.

It is not a convincing stress test for a neural method motivated by the curse of dimensionality in dynamic economics.

The fact that accelerated gradient outperforms the neural-initialized method in the matched query table is not a defect of the experiment; it is useful evidence. But it weakens the claim that the new application establishes neural numerical necessity or advantage.

A future top-venue version needs either a harder nonlinear stochastic dynamic model or a sharply stated narrower methodological claim.

---

### R18-F10 — Major: the boundary-aware certificate still does not identify the actual quality of the neural controls

The supplement now reports full-domain ranges and changes in consumption, preference adjustment, and portfolio controls. That is useful.

But those ranges are descriptive. They do not establish proximity to an optimal policy.

The central actor changes can be substantial while the final certificate is unchanged under an initial-actor substitution. This is precisely why control ranges and certificate values should not be conflated with policy accuracy.

#### Required

Report a certified control or payoff comparison against a trusted benchmark on a nontrivial subset of the state-time domain.

For example:

- certified fixed-policy values for neural and classical policies at selected state-time boxes;
- verified action gaps relative to a sharp upper witness;
- policy-improvement residuals under a common value approximation;
- economically interpretable control discrepancies where the specialized library applies.

---

### R18-F11 — Major: the wealth-compensation result is useful but does not validate the neural solver

The new (0.624%) initial-wealth compensation is a good response to the welfare-normalization objection.

It applies to the sharp deterministic time-control library.

It does not assign a meaningful welfare scale to the 7-unit neural certificate, and it should not be used rhetorically to soften that gap.

The manuscript currently keeps this distinction reasonably clear. It should remain explicit.

---

## 6. Technical comments

### R18-T1 — Put the signed decomposition in the main text, not only the supplement

The most important numerical fact in R18 is not merely that the total certificate falls from about 26 to about 7.3.

It is that the final negative/policy component is zero for all ten seeds and the full remaining bound is the positive optimal-comparison component.

That fact belongs in the main table or immediately next to it.

### R18-T2 — Expand the actor–critic interchange to all ten seeds

One seed is enough to reveal the identification problem, but not enough to characterize it.

For every seed report:

- initial actor + initial critic;
- final actor + initial critic;
- initial actor + final critic;
- final actor + final critic.

If feasible, add cross-seed critic swaps. This would quantify how much of the apparent improvement is actor versus witness.

### R18-T3 — Report upper-face trace excess during training

The fixed-witness theorem gives a direct diagnostic.

For every seed and checkpoint, report:

- verified upper-face trace excess (h_v);
- implied fixed-witness floor;
- positive certificate component;
- relation between the two.

This is more scientifically informative than another table of optimizer loss.

### R18-T4 — A strict certificate-incumbent rule is not a policy-improvement rule

The manuscript proves this correctly.

The algorithm description should therefore avoid any terminology that suggests policy iteration unless the policy-specific lower bound is also shown to improve.

### R18-T5 — The complete-cover training cost should be reported as a scaling object

The current original-economy cover has 1,024 boxes. If the proposed algorithm is meant as a general method, report how one training step scales with:

- state dimension;
- number of boxes;
- network width/depth;
- action maximization cost;
- interval dependency / subdivision.

At present the method avoids sampled-state failure by putting the full low-dimensional cover into every update. That is scientifically legitimate in two states, but its dimensional scaling is central.

### R18-T6 — The nonlinear state-uniform theorem should state even more prominently that training is irrelevant to the guarantee

The paper already says the theorem holds for an untrained initialization.

This should be visible in the main discussion because it determines what scientific claim the theorem can support.

### R18-T7 — Give an amortization/break-even analysis for the nonlinear warm start

The learned initializer improves the zero-correction and early-correction query errors. But its one-time training cost is nontrivial relative to the online solve.

For target tolerances such as (10^{-2},10^{-3},10^{-4},10^{-6}), report:

- corrections needed by neural start;
- corrections needed by zero start;
- accelerated-gradient work;
- per-query online time;
- number of queries required to amortize training.

### R18-T8 — The classical original-economy finest-grid deterioration needs diagnosis

The MC/SL bounds improve from coarse to medium grids and then worsen at the finest grid because the policy residual contribution is no longer zero.

This deserves a decomposition analogous to the neural table. Otherwise the reader cannot tell whether candidate quality, interpolation, witness fitting, or certification dependency is responsible.

### R18-T9 — Keep “independent arithmetic” distinct from independent mathematics

R18 is careful here. Preserve that wording.

The MPFR path shares model derivations, stopping arguments, objective formulas, and software plumbing. It is an arithmetic validation layer, not an independent formal proof of the full theorem stack.

### R18-T10 — The R18 audit is post-hoc to R17 training

This is disclosed correctly. It is not a problem by itself.

But the next genuinely new neural algorithm should be predeclared and executed under the theorem/acceptance logic from the outset, rather than primarily justified by a later audit of frozen R17 trajectories.

---

## 7. Status of the previous review gates

### Gate R17-A — Accurate neural solution of the unchanged nonlinear economy

**Open.**

Best certified bound is approximately 7.2783 versus 0.01.

### Gate R17-B — Certificate-aware solver convergence

**Partially addressed at the certificate level, still open at the policy level.**

Raw certificates now decrease with work, but the demonstrated decrease is principally witness-driven and does not establish improving policy values.

### Gate R17-C — Matched classical baselines

**Improved, still open.**

Policy-class and common-witness confounds are reduced, but no solver reaches matched sharp certified accuracy.

### Gate R17-D — Implemented certified policy iteration or remove the central claim

**Largely resolved as a framing issue.**

The finite-MDP recurrence is now clearly auxiliary. The primary method is the executed complete-cover objective.

### Gate R17-E — Genuine high-dimensional nonlinear control

**Partially closed structurally, open as evidence for neural necessity/advantage.**

The model is genuinely full-state and nonlinear, but the rigorous convergence mechanism is a classical strongly-convex correction that works from untrained initialization.

### Gate R17-F — Standard economic welfare interpretation

**Substantially closed for the sharp non-neural library.**

The budget-feasible wealth compensation is a meaningful improvement.

### Gate R17-G — A single coherent methodological identity

**Still open scientifically.**

The manuscript defines the components more clearly, but the validated successes remain split:

- neural method: decreasing but loose certificates;
- sharp original-economy accuracy: specialized non-neural library;
- high-dimensional accuracy theorem: strongly-convex correction with neural warm start.

A top-method paper needs these pieces to support one coherent claim.

---

## 8. What would justify another Econometrica-level referee round

I would not recommend another round based mainly on:

- more seeds under the current witness regime;
- finer interval covers of the current final critics;
- more arithmetic regression tests;
- additional MPFR precision;
- another specialized validation example;
- more prose separating scopes.

The current paper has already diagnosed why those steps will not solve the main problem.

A scientifically meaningful next revision should clear the following new gates.

### Gate R19-A — Policy-sensitive progress on the flagship economy

Show that the actor itself improves under an independently verified policy-value criterion.

### Gate R19-B — A witness that removes the 6.27-unit floor

Demonstrate a materially different continuation witness whose verified upper-face behavior and positive residual are compatible with the target regime.

### Gate R19-C — Full-domain neural accuracy in a useful range

Reach a complete original-economy bound that is no longer hundreds of times the declared tolerance.

### Gate R19-D — Matched-accuracy classical frontier

At least one conventional solver must be carried to a similarly sharp continuous-time certified accuracy, with generation, evaluation, verification, memory, and wall time all reported.

### Gate R19-E — Neural contribution in the high-dimensional example

Show a certified amortized or complexity benefit from the learned representation, rather than a guarantee that is equally available from an untrained start.

### Gate R19-F — Coherent paper identity

Either:

1. make Neural Bellman Operators themselves the successful accurate method; or
2. reframe the paper around validated dynamic-control certification, with neural networks as one candidate generator whose limitations are part of the contribution.

Both could be valuable papers. The current version still claims the first identity while the strongest evidence supports the second.

---

## 9. Recommendation

**Reject.**

R18 is the strongest revision of this paper I have reviewed. It fixes the earlier training-loss anti-alignment, gives a real theorem for the executed complete-cover objective, supplies a useful fixed-witness obstruction, improves the classical baseline design, adds a genuinely full-state nonlinear example, and gives a better welfare normalization.

Those are substantial accomplishments.

But the central numerical-method requirement remains unmet.

On the unchanged nonlinear economy, the best neural certificate is still about 7.28 against a 0.01 target. The final certificates are entirely dominated by the positive upper-comparison/witness term. For the one explicit actor–critic interchange, the initial actor paired with the final critic produces exactly the same certificate as the final actor. The new high-dimensional success is driven by a globally strongly-convex correction that works nearly as well from zero and better under accelerated gradient, with no neural training cost.

The paper has therefore progressed from

> a neural solver whose sampled loss is anti-aligned with its certificate

to

> a certificate-aware joint actor/critic system that learns much better witnesses but still does not establish accurate policy learning on the flagship problem.

That is real progress, but it is not yet an Econometrica-level demonstration of a successful new neural numerical method.

The next revision should concentrate almost entirely on the two missing scientific objects: **a policy-sensitive neural improvement mechanism and a continuation witness capable of escaping the current 6.27-unit floor.** Everything else is now secondary.
