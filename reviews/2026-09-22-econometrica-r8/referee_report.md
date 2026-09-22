# External Referee Report on Neural Bellman Operators — Revision R8

**Repository:** TrillionniumFoundation/NBO  
**Reviewed branch:** revision/econometrica-r8-verified-manuscript-2026-09-22  
**Reviewed commit:** 939b612ff57794a2127f0b0adeb74ab7eef9e72e  
**Review date:** 2026-09-22  
**Standard:** Econometrica-level numerical methods / quantitative economics  
**Recommendation:** **REJECT IN ITS PRESENT FORM**  
**Scope:** External-style technical review, not an editorial decision.

## 1. Executive assessment

R8 is a serious improvement over R5. The authors now provide a genuine continuous-time verification pair for the stopped economic problem, explicitly handle the contractual first-exit boundary, separate raw and corrected policies, restore a complete manuscript/reproducibility chain, and replace the prior in-house benchmark by a pinned author implementation of SOC-MartNet on a coupled nonconvex control problem. Several earlier objections are therefore genuinely closed.

The decisive scientific gap remains open: the flagship original-payoff NDU calculation is not resolved at economically useful precision. The new continuous regret bounds are 14.0914048908 and 8.3395605260, against a stated 0.01 target. The better bound is over 800 times the target and about 167 times even the older 0.05 diagnostic. The revision correctly records original_continuum_precision_target_met = false. A valid certificate proving that the present computation is too inaccurate is valuable, but it is not a successful numerical solution of the motivating economic problem.

The successful all-state certificate in the learned-geometry experiment is obtained only after modifying the running payoff so that a known witness is exactly the value function; the actor has four parameters and the critic is known. This is a useful unit test of the verifier, not evidence that NBO can learn and certify the difficult original model.

The new SOC-MartNet comparison is encouraging, but it measures relative realized cost under one synthetic problem, two dimensions, six seeds, and one ten-second training budget. The optimum is unknown. The result therefore does not establish absolute error, matched-accuracy efficiency, long-budget behavior, or general computational dominance.

For these reasons I recommend rejection in the present form.

## 2. What R8 successfully fixes

I regard the following R5 objections as substantially resolved:

1. The manuscript is complete and reviewable: ECTA_R8.tex, SUPP_R8.tex, plaintext sources, proofs, response, tables, PDFs, manifests, and validation records are present.
2. The continuous action domain is no longer silently replaced by a finite candidate grid.
3. Boundary irregularity is confronted directly; reflection/clipping is not substituted for the stated economy.
4. The finite safeguard is explicitly a different algorithmic object from the raw actor.
5. The twelve-date 0.05 correction share falls to 0.8746 percent.
6. The external comparator is a pinned author implementation, and the new control benchmark has genuinely nonconvex coupled actions without analytical greedy labels.
7. Failed precision and convergence tests are reported rather than relabeled as successes.
8. Provenance and raw-evidence validation are strong.

The rejection below is based on remaining scientific blockers, not on repeating the R5 review.

## 3. Blocking finding R8-F1: the original economic problem still fails its own precision requirement

The executed continuous regret bounds for the original Brownian first-exit NDU model are:

- N=6 retained policy: 14.09140489080375;
- N=12 retained policy: 8.33956052603494;
- target: 0.01.

These are orders of magnitude too wide for the welfare and adjustment-cost questions motivating the paper. The paper's own validation report explicitly marks the precision target as unmet.

A top numerical-methods application must ultimately produce an error bound smaller than the economic effect being interpreted. R8 has supplied the missing theorem and a valid failure certificate, but not a successful flagship computation.

**Required:** obtain a continuous original-payoff certificate below the economically calibrated tolerance on the relevant initial set.

## 4. Blocking finding R8-F2: the current witness family is valid but not yet a usable certifying algorithm

The original-economy construction uses

U = G - alpha C_rho(1-t),  
L = g - beta C_rho(1-t),

so the date-zero gap is 8 + (beta-alpha) C_rho(1). The liquidation covenant therefore contributes an eight-unit baseline to this witness family. For N=12, alpha is about 0.86483 and beta about 1.21123, yielding 8.33956.

The theorem is not the problem; the constructive numerical step is. R8 mentions occupation-sensitive potentials and other tightening routes but does not execute them. It does not show how to learn/refine upper and lower witnesses until a useful bound is reached.

**Required:** implement a constructive witness-improvement procedure on the original model, with globally validated residuals, and report certificate width versus refinement and computation.

## 5. Blocking finding R8-F3: the semigroup error decomposition remains schematic

The paper correctly names time, within-step feedback, action, interpolation, quadrature, exit, inner-solve, and arithmetic errors. But the corresponding certified terms are not computed for the final NDU calculation.

The mesh diagnostics themselves show unresolved approximation:

- time refinement at fixed 25x31 state grid and 5 action nodes/component: value -1.45149, -1.54979, -1.60853 for N=24,48,96; exit probability 0.1043, 0.1934, 0.2275;
- state refinement at N=48: value -1.54979 to -1.39165 and exit 0.1934 to 0.1024 from 25x31 to 49x61;
- action refinement at N=48, 25x31: value -1.60654 to -1.53671 and exit 0.2453 to 0.1828 from 3 to 9 nodes/component.

The manuscript correctly refuses to infer convergence. Therefore the decomposition has not yet been turned into an end-to-end numerical error analysis.

**Required:** give certified numerical values for every material term and a joint refinement regime with a shrinking total bound.

## 6. Blocking finding R8-F4: the safeguard is less intrusive but still exhaustive and low-dimensional

At the 0.05 finite target the N=12 correction fraction is only 0.8746 percent, which is a real improvement. But two audits still execute about 2,362,200 value-action evaluations and 2,343,600 envelope-action evaluations, with four shock branches and 125 grid actions per state/date plus the proposal.

A small override fraction is not a small certification cost. The guarantee still relies on exhaustive finite action enumeration. A tensor grid of this form is not scalable in action dimension.

The raw N=12 finite localized bound is also 0.09224 before correction, while the continuum certificate remains 8.33956 after all of this.

**Required:** report certification complexity versus action dimension and tolerance; demonstrate a non-enumerative global action certifier; keep raw NBO and safeguarded NBO results separate.

## 7. Blocking finding R8-F5: the learned-geometry success is a manufactured verifier test

The geometry experiment preserves the NDU state/control/exit geometry but changes the running payoff by subtracting the optimal residual of a known witness. The modified value is therefore known exactly. The actor has four trainable parameters; the critic witness is not learned.

The resulting 0.00081-0.00112 regret certificates show that the interval verifier can certify a simple learned actor near a constructed optimum. They do not show that the difficult critic/value learning and verification problem is solved.

**Required:** certify a learned actor and learned or independently computed witness on an unknown-value problem, preferably the original NDU economy.

## 8. Blocking finding R8-F6: the external comparison lacks an absolute accuracy axis

The SOC-MartNet result is favorable to NBO under the declared short-budget protocol. Paired NBO-minus-SOC realized-cost differences are about -1.718 at d=8 and -2.247 at d=16, with six-seed Student intervals below zero.

The primary training clocks are genuinely close to ten seconds: NBO averages about 10.003-10.004 seconds and SOC-MartNet about 10.012 seconds. I do not regard the training-only comparison as invalidated by timing mismatch.

The problem is that the optimum is unknown. NBO cost near 0.48 may be excellent or poor; SOC cost near 2.7 may simply mean the comparator has not converged under this adapter and budget. The experiment establishes relative short-budget performance, not numerical accuracy.

**Required:** add a trustworthy lower bound, verified reference, or low-dimensional continuation of the same benchmark family where absolute regret can be measured.

## 9. Major finding R8-F7: the external benchmark is not yet decisive

Pinned author code is an improvement, but the adapter uses materially different optimization systems: NBO uses Adam, fixed 0.003 learning rate, 3 critic steps per actor step, 256 states and four successors; SOC-MartNet uses RMSprop, 0.003/sqrt(d), a 600-output test network, J=2, K=1, and multiplier dynamics.

These choices may be reasonable, but no symmetric tuning budget is documented for the new objective. One ten-second point and two dimensions are insufficient to establish scaling or a robust computational advantage. There are no learning curves, matched-accuracy frontiers, or longer-budget checks.

Setup-plus-training time is also not directly comparable because NBO runs first and absorbs one-time initialization: roughly 10.69 versus 10.02 seconds. The paper correctly discloses this; future end-to-end claims should neutralize run order.

**Required:** predeclare symmetric tuning, report multiple budgets, extend dimensions, randomize/warm setup, and add another credible comparator or independent reference.

## 10. Blocking finding R8-F8: the theory remains disconnected from the implemented neural optimizer

The exact-operator convergence result assumes compactness, strong C1,2 precompactness/continuity, selector continuity, closure, and comparison. These assumptions are not established for the implemented neural networks, Adam trajectories, stopped NDU model, or high-dimensional experiment.

Thus the strongest theorems verify a supplied policy/witness or ideal exact operators. They do not show that the neural training algorithm produces a certifiable policy at a stated rate or cost. The same verification theorem could be applied to a policy produced by another solver.

**Required:** either connect neural approximation/optimization error to the verified quantities, or reposition the contribution explicitly as an a posteriori verification framework and benchmark that framework accordingly.

## 11. Major finding R8-F9: the economic theorem states the accuracy requirement but the computation does not satisfy it

The adjustment-cost theorem is useful and the algebra appears sound. The finer finite panel reports budgets about 0.01681, 0.01158, and 0.00189 for k=0.5,2,8, consistent with monotonicity.

But these are finite-scheme results without a continuum error enclosure. The available continuous original-payoff regret bounds are far too wide to certify the magnitude of the economic effect.

**Required:** produce continuous value/regret enclosures across the relevant k grid and certified intervals for adjustment budgets and welfare access values whose widths are smaller than the reported effects.

## 12. Major finding R8-F10: recursive utility and games still broaden scope without matching evidence

R8 retains correct-looking Epstein-Zin, sophisticated-self, and game formulations, but no new large-scale recursive or game computation is supplied. Earlier raw recursive failures and grid corrections remain; the game remains small; and the nonlinear Lipschitz extension requires intervals/constants not verified for the neural run.

**Required:** either move these claims to the supplement as framework directions or solve one extension at serious scale with an independent accuracy reference and full error budget.

## 13. Major finding R8-F11: six-seed inference should be treated as exploratory

The paired design is improved, but six training seeds remain thin. The t interval depends heavily on an approximate Gaussian model for seed-level differences. The new benchmark, adapter and settings were developed after prior unfavorable results and after R5 review; the protocol discloses a development seed. This is transparent, but it limits confirmatory interpretation.

**Required:** more independent seeds, robust interval summaries, and a predeclared multi-problem benchmark suite or holdout tasks.

## 14. Major finding R8-F12: novelty positioning needs a stronger rigorous-numerics comparison

The one-sided witness result is useful in the controlled-exit application, but its core proof is a stopped Ito supersolution/subsolution verification argument, while the semigroup result is a telescoping error budget. The manuscript should explain theorem-by-theorem what is new relative to classical stochastic-control verification, viscosity/subsolution methods, monotone schemes, rigorous dynamic programming, and validated numerical PDE work, not only relative to neighboring neural methods.

I am not making a priority ruling; I am saying the current novelty discussion is too neural-method-centric for the mathematical objects carrying the strongest guarantees.

## 15. Reproducibility and presentation

R8 is strong here, with one notable inconsistency: REVISION_INDEX.md is stale and still identifies R3 as the current revision. The identical R8 referee-copy and verified-manuscript branches could also be replaced by one canonical pointer. These are not scientific blockers.

Continue the useful distinction between float64 finite envelopes and outward-rounded interval certificates.

## 16. Minimum conditions for a credible resubmission

### P0 — close the flagship computation

- Tight continuous certificate for the original-payoff NDU economy.
- Certified error below the welfare/comparative-static effect.
- Fully executed witness or semigroup error route, not a schematic budget.

### P0 — demonstrate an operational certifier

- Constructive witness/certificate refinement with shrinking error.
- Runtime/scaling evidence.
- No general dependence on exhaustive tensor action grids.

### P0 — establish absolute benchmark accuracy

- Independent high-accuracy reference or rigorous bounds.
- Absolute regret/error in addition to pairwise cost.
- Multiple budgets and a meaningful dimension range.

### P1 — strengthen comparative evidence

- Symmetric tuning protocol.
- More seeds and predeclared benchmark suite.
- Matched-accuracy and matched-wall-clock frontiers.
- At least one additional credible comparator/reference.

### P1 — focus the paper

- Convert the adjustment-cost theorem into a certified numerical economic result.
- Scale one recursive/game extension or move broad scope claims to the supplement.
- Sharpen novelty against classical rigorous-control/numerical-analysis literature.
- Update REVISION_INDEX.md.

## 17. Recommendation

**Reject in its present form.**

R8 is technically mature enough to identify the real remaining problem: the original economic model still cannot be certified at useful precision. The successful continuous experiment manufactures a known witness, and the favorable external comparison has no absolute optimality reference. The implemented neural optimizer remains theoretically disconnected from the exact-operator assumptions, and the strongest finite guarantee remains tied to exhaustive low-dimensional action auditing.

The next revision should not add more breadth. It should close one chain:

**original economically meaningful model -> learned policy/value -> constructive global verification -> narrow certified error -> economic conclusion larger than that error.**

R8 articulates that chain but does not yet close it numerically.

---

## Evidence reviewed

I reviewed ECTA_R8.tex, SUPP_R8.tex, R8_REVIEW.md, the R8 response-to-referee, main.tex, numerics.tex, proofs.tex, protocol.json, validation_report.json, continuum_witnesses.json, safeguard_results.json, mesh_results.json, geometry_summary.json, external_summary.json, the twelve d={8,16}, seed={400,...,405} external records, verify_continuum.py, learned_geometry.py, external_comparison.py, diagnostics.py, validate_evidence.py, the build manifest, and the prior R5 referee report.

For the external comparison I also inspected sx-fang/MartNet at pinned commit 991ea8dde5bad6ba912eb8cc48b0cb48dbdd6c2a, including the SOCMartNet training routine called by the R8 adapter.
