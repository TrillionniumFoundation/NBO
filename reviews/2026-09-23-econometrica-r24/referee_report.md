# External Referee Report — Neural Bellman Operators (R24)

**Venue standard:** Econometrica-level numerical / computational methodology  
**Recommendation:** **Reject in the present form.**  
**Review date:** 2026-09-23  
**Reviewed referee-copy branch:** `revision/econometrica-r24-referee-copy-2026-09-23`  
**Equivalent development branch:** `revision/econometrica-r24-state-geometry-2026-09-23`  
**Reviewed sealed commit:** `14ce582e188f437cc8d99f310edd4f06515936a4`  
**Review branch:** `review/econometrica-r24-numerical-methods-2026-09-23-14ce582`

---

## 1. Executive assessment

R24 is a serious revision. It directly addresses a number of objections raised against R23: the financed expert controller is now given an explicit augmented-state realization; the manuscript distinguishes unrestricted economic value from a restricted expert implementation; the Adam/output-geometry discussion is corrected for momentum; tuning and evaluation seeds are separated; five first-order parameterizations are calibrated on a declared grid; two proposal quadrature rules are crossed in held-out evaluation; all scheduled certification checkpoints are retained; the acceptance gate now actually rejects some proposals; a genuine four-cell initial-state cover is executed; and an analytic benchmark with a known optimum is supplied.

Those are meaningful improvements. They make the paper much easier to audit.

They do **not** close the publication-level numerical-method problem.

The core evidence now says, with unusual clarity, that:

1. the original full-state current-state objective remains unsolved by an enormous margin;
2. the strongest tested solver is still the direct classical method, not the neural method;
3. the purportedly tuned first-order comparison is not actually bracketed because **every Adam arm selects the largest tested learning rate**;
4. the new geometry experiment does not reproduce the actual moving, momentum-dependent neural metric that the paper itself proves governs Adam;
5. the proposal objective still lacks a certified gradient-error bridge to the stopped continuous objective;
6. the acceptance operator is a replayed deployment filter that does not alter the optimizer trajectory;
7. the successful regional theorem concerns a small (t=0), two-dimensional initial-state patch under an augmented controller with stored initialization memory and a favorable exact-pricing structure;
8. the deterministic reference problem is too simple to validate the stochastic stopped Bellman mechanism that matters for the paper's central claim.

The revision therefore succeeds mainly in **making the limitations mathematically explicit**. That is valuable scientific work, but it does not establish a competitive Neural Bellman Operator at Econometrica-level numerical-method standards.

My recommendation remains **reject in the present form**.

---

## 2. What R24 genuinely fixes

Before listing the remaining blockers, I want to be explicit about what should no longer be criticized in the same way as R23.

### 2.1 The state-definition ambiguity is substantially repaired

R24 no longer pretends that the successful financed expert controller is a feedback map on ((t,u,x)) alone. The current paper states that the deployed implementation is Markov in

[
(t,u,x,Y,lambda),
]

with frozen expert coefficients, common factor (Y), and initialization weights (lambda). The proof of the aggregate dynamics is transparent, and the unrestricted augmented value identity is correctly framed as an admissible-class statement under the original Brownian filtration.

This resolves an important semantic defect in R23.

It does **not** solve the original-state current-state numerical problem. The paper now says so itself.

### 2.2 The neural-geometry discussion is more correct

The manuscript no longer identifies Adam with a current (J D^{-1}J^	op) metric while ignoring momentum. The output-transport formula correctly contains historical Jacobians and historical output gradients, plus a nonlinear remainder.

This is a real improvement in analytical accuracy.

### 2.3 The tuning/evaluation chronology is much better

The R24 protocol precedes the new scientific execution; tuning uses seeds 24001–24002 and evaluation uses 24101–24102. The rate-selection rule is explicit. All tuning trials are retained.

The problem is no longer data leakage. The problem is that the tuning grid does not bracket the optimum.

### 2.4 The paper now retains adverse outcomes rather than hiding them

The paper prominently reports:

- direct L-BFGS-B superiority;
- neural L-BFGS-B failure;
- poor whitening performance;
- a transferred-rate analytic-reference neural failure;
- lack of a rigorous stopped-gradient error bound;
- lack of a new full-state certificate;
- lack of a successful nonreplicable stochastic execution.

That transparency is a strength.

---

## 3. Decisive numerical facts

The current R24 publication summary is enough to judge the method.

### 3.1 Original full-state target

The declared target is

[
0.01.
]

The current all-start-time full-state bound remains

[
7.241462443133396.
]

This is approximately **724 times the target**.

R24 explicitly records:

- `new_full_state_accuracy_established = false`;
- `new_actor_payoff_improvement_established = false`.

The flagship original-state numerical objective therefore remains unresolved.

### 3.2 Central held-out comparison

At proposal orders ((8,16)):

| Method | Worst regret upper | Mean calls | Mean generation sec. |
|---|---:|---:|---:|
| neural Adam | 0.0019257129 | 400 | 1.3026 |
| direct Adam | 0.0020392271 | 400 | 1.1805 |
| diagonal Adam | 0.0020087346 | 400 | 1.1787 |
| tangent Adam | 0.0021572316 | 400 | 1.1748 |
| whitening Adam | 0.0187420285 | 400 | 1.1751 |
| neural L-BFGS-B | 0.0096083261 | 251 | 0.7917 |
| **direct L-BFGS-B** | **0.0019234429** | **111.5** | **0.3208** |

The direct L-BFGS-B result is not merely a dual-bound artifact. The pairwise certified interval for neural Adam relative to direct L-BFGS-B is strictly negative:

[
[-2.7981	imes 10^{-6},,-1.5150	imes 10^{-6}],
]

so direct L-BFGS-B has strictly higher certified payoff in the matched held-out comparison.

The same qualitative conclusion survives the finer ((12,24)) proposal rule.

### 3.3 Multicell regional comparison

On the four-cell region

[
uin[1.98,2.02],qquad xin[1.24,1.27],qquad t=0,
]

the reported region bounds are:

- neural Adam: (0.0042805258);
- direct Adam: (0.0043987899);
- tangent Adam: (0.0045082560);
- **direct L-BFGS-B: (0.0042748622)**.

Generation work is also favorable to direct L-BFGS-B:

- neural Adam: 3600 gradient calls, 11.755 sec.;
- direct L-BFGS-B: 1250 gradient calls, 3.592 sec.

Thus the direct method again lies on the stronger accuracy/work frontier.

### 3.4 Known-solution reference

Worst optimization gaps in the deterministic reference include:

- neural Adam: (2.771	imes10^{-3});
- direct Adam: (5.492	imes10^{-5});
- tangent Adam: (1.956	imes10^{-5});
- whitening Adam: (5.646	imes10^{-1});
- **direct L-BFGS-B: (3.393	imes10^{-13})**.

This benchmark confirms that the verifier can resolve very small gaps in the simplified reference problem. It does not provide evidence of neural superiority. It provides the opposite.

### 3.5 Tuning is censored at the grid boundary

Every first-order arm selects learning rate (0.08), the largest value in the declared grid

[
{0.005,0.02,0.08}.
]

Every one of those (0.08) trials is feasible.

More importantly, the tuning scores are still improving toward the boundary. For example, the direct Adam tuning score moves from approximately

[
-1.2900451 quad	ext{at }0.02
]

to

[
-1.2875232 quad	ext{at }0.08,
]

an improvement of about (2.52	imes10^{-3}). That movement is much larger than the held-out neural-vs-direct-Adam payoff difference, which is on the order of (10^{-4}).

This is not a minor editorial point. It means the comparison is still not calibrated to a demonstrated first-order frontier.

---

## 4. Blocking findings

### R24-F1 — The paper still does not solve the numerical problem stated as its strongest objective

The most important fact is also the simplest.

The original economy, full state-time domain, current-state actor, and uniform (0.01) target are retained. The best complete-domain bound remains (7.241462443133396), and R24 establishes no separate payoff improvement for the changed actor.

That is not a near miss. It is a failure by roughly three orders of magnitude.

The new regional augmented-state result is mathematically cleaner than the R23 presentation, but it is not the same numerical object. It cannot be used to imply progress of comparable magnitude on the original full-state current-state target.

For a paper whose title and framing continue to center Neural Bellman Operators for the stopped economy, this remains a decisive publication barrier.

### R24-F2 — The “tuned” Adam comparison is not actually tuned to a bracketed frontier

R24 correctly introduces disjoint tuning, but the chosen tuning family is too narrow to support the interpretation placed on it.

All five first-order arms select (0.08), the largest tested learning rate. All are feasible there. Several arms improve substantially from (0.02) to (0.08).

A proper calibration exercise must either:

1. bracket the useful range by including rates large enough to show deterioration/instability after the optimum; or
2. demonstrate a plateau sufficiently broad that the selected endpoint is insensitive to further enlargement; or
3. tune a schedule family under a prospectively fixed resource budget.

R24 does none of these.

The paper acknowledges that the finite grid does not identify an optimum outside its range. That acknowledgement is correct, but it also means the central neural-vs-direct Adam comparison is not yet a fair tuned comparison.

This is especially consequential because the direct Adam tuning score is still moving materially at the boundary.

### R24-F3 — The strongest tested solver is direct L-BFGS-B, repeatedly and on certified payoff

The direct L-BFGS-B result is the main numerical finding of R24.

It is:

- more accurate than neural Adam at the central held-out problem;
- strictly better in certified pairwise payoff;
- much cheaper in gradient calls and generation time;
- slightly better in the multicell regional certificate;
- essentially exact in the known-solution reference.

Neural L-BFGS-B remains fragile, and the post-hoc layer rescaling experiment shows that a large part of that fragility is coordinate dependent.

This evidence supports a conclusion about **neural parameterization sensitivity**, not a conclusion that a Neural Bellman Operator improves the efficient frontier.

A top numerical-method paper centered on a neural mechanism should show a regime in which the neural construction changes what can be achieved at a given accuracy/work level. R24 does not.

### R24-F4 — The direct geometry controls still do not reproduce the actual neural Adam mechanism

R24's own transport theorem makes this point unavoidable.

The actual first-order neural output update contains terms of the form

[
J_n D_n^{-1}J_r^	op g_r
]

over historical (r), plus nonlinear output curvature.

The direct geometry experiments instead freeze charts constructed from the **initial** matrix (J_0J_0^	op), or from diagonal/whitened variants.

Those controls are useful. They do not identify the mechanism that the theorem says governs neural Adam.

In particular:

- the tangent chart is static;
- the whitening chart is merely an inverse static scaling;
- neither transports historical gradients through historical Jacobians;
- neither adapts to the current Adam second moment;
- neither recreates network-induced nonlinear output curvature.

Therefore the failure of a frozen tangent chart to match neural Adam does not show that neural structure contributes an irreducible advantage. It only shows that one static approximation to one part of the mechanism is insufficient.

A convincing mechanism experiment would implement, in the 47-dimensional quotient, at least one prospectively defined direct method using a current or lagged approximation to the measured neural output metric/transport, with regularization fixed before evaluation.

### R24-F5 — The reduced-gradient theorem is conditional and is not instantiated for the original stopped problem

Theorem r24gradient is a correct type of perturbation statement: price-root error, derivative error, and root conditioning must all enter.

But the theorem is not turned into a numerical certificate for the executed optimizer.

The paper does not provide verified numerical values for the full collection of quantities required to bound

[
|
abla F_N-
abla F|
]

for the original stopped objective along the relevant optimization trajectories.

Instead it reports two-rule differences.

The publication summary records:

- largest absolute raw-gradient rule difference: about (4.409	imes10^{-7});
- largest relative raw-gradient rule difference: about (22.99);
- largest financing-offset rule difference: about (9.345	imes10^{-6}).

The manuscript correctly says these are diagnostics and do **not** imply a rigorous continuous-gradient error bound.

That means the core R23 objection about surrogate-optimization robustness is not closed. It is reformulated more honestly.

For a paper making claims about optimizer geometry, the gradient field being optimized is central. A conditional theorem whose hypotheses are not certified on the actual calculation does not establish robustness of the optimizer ordering to the continuous stopped objective.

### R24-F6 — The acceptance operator is now exercised, but it is still not the proposal algorithm

R24 improves on R23 in one respect: 19 of 140 held-out checkpoint decisions are rejected, including 12 changed candidates.

However, the optimizer does not roll back. It continues along the same proposal trajectory independently of the deployment gate.

Thus the executed mechanism is:

1. run an optimizer trajectory;
2. archive checkpoints;
3. independently certify them;
4. replay a monotone deployment rule afterward.

This gives a legitimate **deployment-safety filter**.

It does not establish:

- a Bellman iteration driven by acceptance;
- convergence of the proposal mechanism;
- improved proposal efficiency due to the gate;
- measured online latency of certification-coupled optimization.

The paper states this honestly. But then the word “operator” should not derive algorithmic force from the gate. The gate is a verifier/deployer, not the engine that produces the successful policy.

### R24-F7 — The augmented-state theorem repairs semantics, not the restart/global Bellman problem

The successful regional policy depends on stored (lambda) and the common factor (Y). R24 is correct to make that state explicit.

But the numerical certificate is still only for initialized reachable states in a small (t=0) region.

It does not establish a certified policy for arbitrary:

- start times;
- original states ((u,x));
- augmented memory states ((Y,lambda));
- off-manifold restarts.

This matters for a Bellman-method claim because dynamic programming is fundamentally a restart statement.

The unrestricted value theorem says memory does not change the *optimal value*. It does not certify the restricted financed library after arbitrary restart, nor does it compress that library back to a current-state policy.

The paper explicitly allows arbitrary admissible off-manifold extensions. That is enough for formal admissibility, but not enough for a global numerical Bellman solution.

### R24-F8 — The multicell experiment is still a tiny favorable two-dimensional cover, not state-global scaling evidence

The new (3	imes3) grid is a real improvement over four vertices. It should be credited as such.

But its scope remains narrow:

- (t=0) only;
- (u)-width (0.04);
- (x)-width (0.03);
- four cells;
- nine experts;
- exact conditional-price reconstruction;
- a common factor shared across financed experts.

The paper itself says this is not high-dimensional scaling evidence.

That concession is correct and important.

The next methodological step must test a materially harder dimension: a larger state-time cover, a nonreplicable stochastic problem, a second economic model, or a regime in which the exact financed decoder is unavailable.

Without such evidence, the regional result remains a specialized construction rather than a general numerical Bellman method.

### R24-F9 — The analytic reference is too easy to validate the difficult part of the method

The known-solution reference is deterministic, one-dimensional in the economically active control, has no risky asset, no preference adjustment, no stopping complexity, no financing root, and no dual slack. Thirty-two of the raw outputs are inactive in payoff.

It is useful for one narrow purpose: demonstrating that the directed arithmetic and optimization-gap reporting can recover a known optimum.

It is not a meaningful stress test of:

- stochastic state propagation;
- stopped payoff derivatives;
- financing-root sensitivity;
- portfolio hedging;
- augmented policy memory;
- common-shock mixture certification;
- Bellman residual verification.

Therefore it does not separate the important error components of the original economy as strongly as the response claims.

A useful verifier-limited benchmark should retain substantially more of the original stochastic and stopping structure while possessing an independently known or ultra-high-accuracy solution.

### R24-F10 — The reference experiment weakens, rather than strengthens, a neural-efficiency claim

In the analytic reference, direct L-BFGS-B is essentially exact, while neural Adam has a worst gap around (2.77	imes10^{-3}). Direct Adam and tangent Adam also outperform neural Adam in the worst case.

This is not merely “an adverse transferred-rate outcome.” It is evidence that the selected neural first-order configuration is not robust even on a drastically simpler problem where approximation and quadrature error have been removed.

Because the learning rate is transferred rather than retuned, the experiment does not prove neural inferiority in general. But it also cannot be cited as positive support for the neural method.

At most it demonstrates that the paper's chosen neural configuration is problem sensitive.

### R24-F11 — The post-hoc rescaling experiment identifies fragility but not a stable neural mechanism

The adverse R23 neural L-BFGS-B run is informative. R24 shows:

- regenerated regret: about (0.010503067);
- equivalent powers-of-two parameter rescaling: about (0.002554827);
- tighter tolerance restart: still about (0.010503067);
- direct restart from the saturated raw outputs: still about (0.010503067).

This is valuable diagnostic work.

It also confirms that nominally equivalent parameter coordinates can radically alter the neural optimization trajectory.

That makes the missing invariance/robustness story more serious, not less serious.

A numerical method whose quality moves by a factor of roughly four under an equivalent layer scaling requires a principled chart-selection rule or a parameterization-robust optimizer. A post-hoc demonstration that one equivalent chart is much better is not such a rule.

### R24-F12 — The new theory is mostly explanatory identity, not yet a top-level numerical theorem

The three main new analytical devices are:

1. admissible-class equality under causal state augmentation;
2. an Adam first-moment expansion followed by a Taylor remainder;
3. an implicit-function gradient perturbation inequality.

These are useful and mostly correctly scoped.

They do not, by themselves, constitute the missing numerical-method theorem.

The output-transport theorem explains why the optimizer is parameterization dependent; it does not yield convergence or a complexity improvement. The gradient theorem lists sufficient error terms; it does not certify them. The augmented-state theorem preserves unrestricted value; it does not establish accuracy of the restricted neural/financed policy.

The theoretical additions therefore clarify the evidence but do not overturn the numerical conclusion.

---

## 5. Additional technical findings

### R24-T1 — The learning-rate boundary issue should be elevated from a qualification to a primary limitation

The current text says the finite calibration family “does not identify an optimum outside its range.”

That is too mild.

Because **all** five first-order methods choose the largest rate, the grid has failed as a tuning design. The next revision should enlarge it prospectively and repeat the held-out study with the new fixed rule.

The current held-out direct-vs-neural Adam comparison should not be described as a tuned frontier.

### R24-T2 — The gradient-perturbation theorem should state the numerical-version derivative bounds unambiguously

The proof uses bounds on both numerical and exact derivative factors. The theorem text says “both versions satisfy” bounds written only in exact notation.

For auditability, state explicitly something like

[
max{|F_a|,|F_{N,a}|}le M_B,qquad
max{|P_y|,|P_{N,y}|}le M_C.
]

The current wording is interpretable, but unnecessarily ambiguous.

### R24-T3 — A static (J_0J_0^	op) chart is not a faithful test of Adam's adaptive neural geometry

This should be stated even more forcefully in the results section.

The theorem and the experiment currently sit next to each other in a way that can invite the reader to overinterpret the tangent-chart failure.

A proper causal identification experiment would use time-varying metric information or explicitly say that no executed direct arm approximates the full historical transport.

### R24-T4 — The “110 trajectories” count should remain purely bookkeeping

The manuscript mostly handles this correctly.

These trajectories belong to different purposes:

- tuning;
- held-out evaluation;
- multicell construction;
- analytic reference;
- post-hoc failure diagnosis.

They are not 110 independent replications of one scientific effect.

No future text should use the aggregate count rhetorically as robustness evidence.

### R24-T5 — The current revision index is stale

At the reviewed R24 commit, `REVISION_INDEX.md` still says:

> Current review object: R23

and points to `R23_REVIEW.md`.

That is a packaging defect in the current review object.

It does not alter the mathematics, but a sealed referee copy should have a self-consistent entry index.

### R24-T6 — The end-to-end cost story remains dominated by verification infrastructure

For held-out runs, checkpoint checking is around ten seconds per method, while generation is typically below two seconds.

This is not a flaw: certified computation can legitimately spend most of its time verifying.

But it means the paper must distinguish:

- proposal-generation efficiency;
- deployment-certificate efficiency;
- amortized dual cost;
- full end-to-end cost.

The neural-vs-direct generation comparison alone is not the whole numerical method.

---

## 6. What would constitute a materially new R25

Another bookkeeping-heavy revision of the same R24 design would not address the central issues. A materially new revision should deliver new numerical evidence.

### N1 — Actually bracket first-order hyperparameter performance

Use a prospectively fixed expanded grid or schedule family for each first-order representation.

The selected configuration should be interior, on a demonstrated plateau, or explicitly limited by instability.

Then rerun held-out evaluation.

### N2 — Implement a direct method that follows the measured neural output geometry

At minimum, compare neural Adam against a direct quotient method using a prospectively declared regularized approximation to one of:

- current (J_nD_n^{-1}J_n^	op);
- a lagged moving average of that metric;
- a low-rank/historical transport approximation.

This is the experiment needed to decide whether the neural map contributes more than an implicit preconditioner.

### N3 — Certify or tightly control proposal-gradient error

Instantiate the perturbation theorem with numerical constants on the relevant region/trajectory, or replace it by a rigorous refinement argument.

Two nearby quadrature rules are not enough.

### N4 — Produce a successful current-state full-domain result

The current (7.241462443) bound versus (0.01) remains the largest substantive gap in the paper.

A credible next revision needs an orders-of-magnitude improvement and a separately certified policy-payoff improvement for the original actor.

### N5 — Execute a nonreplicable stochastic problem

The paper explicitly retains this as unresolved.

A new stochastic model in which the favorable exact conditional-price decoder is unavailable would materially test the claimed methodology.

### N6 — Add a restart/state-time coverage experiment

Demonstrate a certified method on multiple start times and a materially larger state region, not only a (t=0) initialization patch.

### N7 — Use a stronger known-solution benchmark

The benchmark should preserve stopping and at least one nontrivial stochastic/financing feature while retaining an independently known high-accuracy solution.

### N8 — Decide what the paper is actually about

There are two coherent paths.

**Path A:** keep the title-level Neural Bellman Operator claim and produce a competitive original-state numerical method.

**Path B:** reframe the paper around the result actually demonstrated: certified augmented-state expert control, exact financing, policy verification, and parameterization-dependent optimization geometry.

Path B could be scientifically interesting, but it is a narrower paper.

---

## 7. Editorial and presentation points

1. The abstract should lead with the fact that direct L-BFGS-B remains more accurate and cheaper in the tested policy class, not place that fact after the neural result.
2. “Tuned neural Adam” should be replaced by wording such as “selected from the declared three-rate grid” until the grid brackets performance.
3. The multicell result should always include (t=0) and the augmented-state scope in the same sentence as the (0.004281) number.
4. The reference benchmark should not be described as broad validation of the stochastic method.
5. The acceptance gate should be called a replayed certified deployment rule unless an online coupled implementation is actually executed.
6. The tangent-chart result should not be used to imply that direct preconditioning has been exhausted.
7. The full-state (7.241462443) number should remain prominent whenever the original (0.01) objective is discussed.
8. `REVISION_INDEX.md` should be updated before another sealed referee copy is produced.

---

## 8. Recommendation

**Reject in the present form.**

R24 is the strongest and most honest version of the manuscript I have seen. It substantially improves state semantics, auditability, calibration chronology, checkpoint reporting, and failure analysis.

The problem is no longer that the paper hides its limitations. The problem is that the limitations are now demonstrated by the paper's own strongest evidence.

The original current-state full-domain target remains missed by roughly a factor of 724. The direct classical solver is still the best tested accuracy/work method. The first-order tuning grid is censored at its upper endpoint. The executed direct geometry controls do not reproduce the actual historical adaptive transport that the paper proves governs neural Adam. The proposal-gradient bridge remains conditional rather than certified. The successful continuum result remains a small (t=0) augmented-state region built on favorable exact financing. The analytic reference is too simple and in fact contains a significant neural failure.

These are not cosmetic defects. They are the central numerical-method questions.

A future revision should be reconsidered only if it contains a materially new algorithmic result: a genuinely calibrated first-order frontier, a direct neural-metric control, a rigorous proposal-gradient bridge, and—most importantly—substantial progress on the original full-state current-state objective or a clear reframing away from that claim.

---

## 9. Source map inspected

### Current R24 referee object

- `ECTA_R24.tex`
- `SUPP_R24.tex`
- `RESPONSE_R24.tex`
- `R24_REVIEW.md`
- `REVISION_INDEX.md`

### Current R24 paper

- `revisions/2026-09-23-r24/paper/introduction.tex`
- `revisions/2026-09-23-r24/paper/state.tex`
- `revisions/2026-09-23-r24/paper/geometry.tex`
- `revisions/2026-09-23-r24/paper/design.tex`
- `revisions/2026-09-23-r24/paper/results.tex`
- `revisions/2026-09-23-r24/paper/conclusion.tex`
- `revisions/2026-09-23-r24/paper/proofs.tex`
- `revisions/2026-09-23-r24/paper/supplement.tex`
- `revisions/2026-09-23-r24/paper/response.tex`

### Current R24 numerical evidence

- `revisions/2026-09-23-r24/results/PUBLICATION_SUMMARY.json`
- `revisions/2026-09-23-r24/results/tuning_selection.json`
- `revisions/2026-09-23-r24/results/multicell_summary.json`
- `revisions/2026-09-23-r24/results/failure_summary.json`
- `revisions/2026-09-23-r24/results/full_state_canonical.json`
- `revisions/2026-09-23-r24/results/EXECUTION_COMPLETENESS.json`
- `revisions/2026-09-23-r24/results/tests.json`
- complete ledger and checkpoint-ledger metadata

### Retained proof chain checked

- `revisions/2026-09-23-r21/paper/proofs.tex`
- `revisions/2026-09-23-r22/paper/proofs.tex`
- `revisions/2026-09-23-r18/paper/retained_foundations.tex`
- `revisions/2026-09-23-r18/paper/aligned_proofs.tex`

### Previous second-pass referee baseline

- `reviews/2026-09-23-econometrica-r23-second-pass/referee_report.md`

The two R24 branches `revision/econometrica-r24-state-geometry-2026-09-23` and `revision/econometrica-r24-referee-copy-2026-09-23` were confirmed identical at sealed commit `14ce582e188f437cc8d99f310edd4f06515936a4`.
