# External Referee Report on NBO Revision R5

**Repository:** TrillionniumFoundation/NBO  
**Reviewed branch:** revision/econometrica-r5-certified-control-2026-09-21  
**Reviewed commit:** 448b1153cb2a9e89fff295b9ab0ad90ef5496bef  
**Review date:** 2026-09-21  
**Standard applied:** Econometrica-level numerical-methods / quantitative-economics standard  
**Recommendation:** **REJECT IN ITS PRESENT FORM**  
**Scope:** External-style technical review, not an editorial decision.

## 1. Executive assessment

R5 is a serious improvement over R4. The authors have added a predeclared confirmatory panel, ten baseline seeds, a longer-horizon panel, one-factor sensitivity experiments, trained continuous actors, an a posteriori gain-envelope audit that does not use the candidate optimum in its stopping rule, a bridge-corrected stopped-diffusion test, high-dimensional nonlinear control experiments, genuinely trained recursive-utility and dynamic-game extensions, raw arrays/checkpoints, timing/memory records, and independent algebra checks. These changes resolve several concrete objections from the previous review.

They do **not**, however, close the central numerical-methods gap required for a top econometrics/economic-theory journal. The current certification statement remains a certificate for a **finite candidate economy** consisting of the R4 action grid augmented by one frozen neural proposal per state and date. The protocol itself explicitly states that the finite certificate excludes time discretization, action coverage, quadrature, interpolation, and continuous first-exit error. The target NDU economic calculation continues to have no end-to-end continuum error bound. When the raw actor becomes harder to train, the reported “safeguarded” success is obtained by a grid-based policy-improvement operation that can overwrite roughly one half to two thirds of state-date decisions. In the recursive extension, a 31 x 31 action search similarly repairs both raw neural policies to near machine-level candidate-set optimality after two sweeps. This is not a minor diagnostic correction; it changes the algorithm being evaluated.

The new 8/16/32-dimensional experiment also does not establish a computational advantage. On the paper’s own table, NBO has a larger mean policy loss than the in-house PINN-policy-iteration comparator at every dimension, and longer training time at every dimension. Moreover, the high-dimensional model has an analytic greedy action and a Cole-Hopf representation, and the NBO actor is trained by squared-error regression to the analytic greedy target -2 grad v. That is a useful implementation check, but it does not test the central difficult regime in which action optimization is implicit, nonconvex, or controls the diffusion.

Finally, the exact R5 HEAD is not presently a reviewable manuscript artifact. The HEAD commit message is “paper(r5): transport verified manuscript and response capsule, part 2 of 10”; only paper-0.b64 and paper-1.b64 are present, while paper-2.b64 through paper-9.b64 are absent. ECTA_R5.tex and SUPP_R5.tex are also absent. The R5 review-build workflow directly requires those two TeX files and contains no manuscript-capsule reconstruction step. Thus the numerical evidence can be reviewed, but the authoritative R5 manuscript and response are not reproducibly reconstructible from the reviewed checkout.

For these reasons, I do not think R5 is publishable at an Econometrica-level numerical-methods standard. The revision is materially better engineered, but the main scientific burden has shifted rather than disappeared: the paper now needs an end-to-end continuous-problem guarantee or a sharply narrower claim, a defensible account of the safeguard as part of the algorithm rather than as a post hoc repair, and a genuinely competitive numerical demonstration on problems for which the proposed operator architecture is needed.

## 2. What R5 successfully fixes

Before listing the blocking issues, I want to acknowledge the substantial progress.

1. The baseline confirmatory panel is no longer a three-seed illustration. Seeds 10--19 are fixed in the protocol, failed or interrupted runs are retained, and the development pilot is explicitly excluded from the confirmatory denominator.
2. Training no longer enumerates the R4 125-action grid in the NDU actor stage. The actor is genuinely continuous and receives no optimal-policy labels.
3. The stopping certificate is computed from one-step gain envelopes under the evaluated policy and does not feed the independently computed candidate optimum into training or the stopping rule.
4. The revision separates raw and safeguarded outcomes and records override fractions.
5. The stopped-diffusion section introduces Brownian-bridge killing and an occupation-barrier argument instead of pretending endpoint killing is sufficient.
6. The high-dimensional extension supplies an independent Cole-Hopf/QMC reference and reports simulation uncertainty.
7. Recursive utility and the game are no longer merely interface demonstrations; they now include learned actors/critics and independent NumPy audits.
8. The repository contains checkpoints, raw arrays, histories, environment records, and validation scripts for the numerical evidence.

Those are meaningful improvements. The rejection recommendation below is therefore not based on the old R4 defects being ignored; it is based on what the new evidence actually establishes.

## 3. Blocking finding R5-F1: the main “certificate” is still a finite candidate-set certificate, not a certificate for the continuous control problem

The central NDU protocol defines the candidate action set as the R4 125-action grid union the frozen continuous neural proposal at each state and date. The protocol also states, verbatim in substance, that the finite certificates do not include time, action-coverage, quadrature, interpolation, or continuous first-exit error. continuous_actor.py likewise says that the finite audit is not a continuum audit, and the delivered NDU result records have continuum_certificate = null.

This distinction is not cosmetic. Let A be the true continuous action domain and A_h union {a_theta(s,t)} the audited candidate set. A small Bellman gain over the latter does not rule out a materially better action in A outside that set. The same issue occurs in the state/time discretization: a certificate for the finite operator does not by itself certify the continuous stopped control problem.

The R5 coupled-scheme results do not close this gap. The sparse NDU scheme records continuum_error_bound = null and continuous_boundary_regular_for_all_actions = false. There is therefore no theorem or computed error budget of the form

continuous-control loss <= candidate-set Bellman envelope + action discretization + time discretization + state interpolation + quadrature + first-exit error.

That is the quantity the paper needs if it wants to use “certified control” language at the level suggested by the revision name and numerical narrative.

**Required for a publishable revision:** either (i) prove and numerically instantiate a complete decomposition with computable bounds for every omitted term, or (ii) narrow all claims explicitly to the discrete candidate economy and stop presenting the result as a certificate for the continuous economic control problem. A Lipschitz/convexity-based action-cover term, verified inner continuous optimizer, interval/validated numerics, or another rigorous global action maximization device would be acceptable routes; simply adding more action grid points without a bound would not be enough.

## 4. Blocking finding R5-F2: the safeguard is doing substantive policy iteration and, in the hard cases, replaces most of the learned policy

The raw-versus-safeguarded table is the single most important empirical result in R5. It should be interpreted much more critically than the manuscript appears to intend.

For the baseline n=6 panel, all 10 raw runs pass the 0.05 localized candidate-set bound. But the harder and sensitivity panels show:

| Panel | Raw passes | Safeguarded passes | Override fraction on failed raw runs |
|---|---:|---:|---:|
| baseline | 10/10 | 10/10 | 0 |
| longer horizon n=12 | 0/3 | 3/3 | 0.502--0.547 |
| width 32 | 1/2 | 2/2 | 0.631 |
| learning rate 0.002 | 0/2 | 2/2 | 0.654--0.658 |
| actor steps 300 | 0/2 | 2/2 | 0.670--0.685 |
| critic steps 400 | 1/2 | 2/2 | 0.605 |

The n=12 raw policy losses are about 0.0503--0.0513 and the raw localized bounds about 0.0837--0.0922. After one safeguard sweep the reported losses fall to about 0.0023--0.0031 and the bounds to about 0.0052--0.0064, but this occurs after overwriting approximately 50--55% of interior state-date decisions.

The safeguard is not a lightweight certification wrapper. In continuous_actor.py it computes old.actions(cfg), evaluates the finite action grid at every state and date, constructs a greedy action, and then replaces every state with positive audited gain. In the baseline NDU configuration the enumerated grid contains 125 actions. Thus, precisely where the neural actor is weak, the final successful object becomes a hybrid “neural proposal + exhaustive finite-grid policy improvement” algorithm.

The recursive-utility extension makes the point even more starkly. global_q constructs a 31 x 31 = 961-action grid at every wealth node. Seed 51 has raw log-value loss 0.04246 against a prespecified 0.01 target; seed 52 has raw loss 0.05018. Both raw actors therefore fail by factors of about four to five. Two grid-based safeguard sweeps reduce the reported candidate-set bound to approximately 4.7e-6 and 1.35e-5, respectively.

This does not invalidate the repaired policy. It changes the scientific claim. If the safeguard is part of the method, then its action-enumeration cost, memory, dimensional scaling, and dependence on a low-dimensional action grid must be counted as part of the algorithm. If the safeguard is only a diagnostic, then the raw neural results are the relevant method results and several central stress tests fail.

**Required for a publishable revision:** define two algorithms cleanly—raw NBO and safeguarded NBO—and benchmark both. Report total end-to-end cost, including action enumeration and all safeguard sweeps. Show how the safeguard scales as action dimension grows. Most importantly, show that the override fraction and gain corrections shrink with training/refinement rather than becoming the mechanism that makes the method pass.

## 5. Blocking finding R5-F3: the economically relevant NDU discretization is not shown to have converged

The coupled refinement table is useful, but it does not support a claim that the continuous economic quantities are resolved at the 0.05 level.

For k=2, the reported center value is

- N=12: -1.624355
- N=24: -1.510132
- N=48: -1.391646
- N=96: -1.353683.

The total movement is about 0.271, and even the last N=48 to N=96 increment is about 0.038. That last change alone is roughly three quarters of the paper’s 0.05 diagnostic target. The exit probability moves from about 0.1543 and 0.1558 at the first two levels to 0.1024 and 0.0987 at the last two. The action mesh is also changed discontinuously: n_a is 3 at the first two levels and 5 at the last two, corresponding in the code to action_mesh_max 0.65 and 0.325. Consequently these runs do not identify a clean convergence order in time, state, action, or boundary treatment.

The absence of a continuum_error_bound field is therefore substantive, not merely conservative metadata. The numerical sequence has not been converted into an error estimate. No Richardson-style extrapolation, verified monotone envelope, independent high-accuracy reference, or separated discretization error budget is supplied.

**Required for a publishable revision:** perform controlled one-factor convergence studies for time step, state mesh, action approximation, quadrature, and first-exit handling; then perform a final joint refinement under a stated asymptotic regime. Report convergence rates or validated upper bounds for the economic objects actually used in the paper, including value, policy, exit probability, and the comparative-static quantity. The paper should not use a 0.05 policy diagnostic as a substitute for numerical convergence of the underlying model.

## 6. Blocking finding R5-F4: the manufactured continuum certificate is informative but does not certify the neural NDU calculation

The one-dimensional manufactured stopped-diffusion experiment is a welcome addition. The bridge treatment materially improves the value error: the reported bridge t=0 value error decreases from 0.0581 at N=16 to 0.0040 at N=256. The occupation-barrier construction is also a sensible way to avoid requiring uniform near-boundary policy accuracy.

But this experiment is not the target NBO computation. It is a one-dimensional analytically manufactured problem with a known verification pair and a finite dynamic-programming action search. There is no neural actor in the manufactured solver. It therefore validates a boundary-handling and a posteriori bounding technique in a highly structured case; it does not validate the full learned NDU pipeline.

The distinction becomes especially important because the reported nodewise action sup error actually **increases** across refinement, from 0.3783 to 0.5502. The reported policy-loss bound nevertheless falls from 0.1691 to 0.0106 because the occupation argument discounts the poorly resolved boundary layer. That may be legitimate for value regret, but it is evidence against uniform policy convergence and should be described as such.

**Required for a publishable revision:** transfer the continuum argument to the actual learned NDU model or prove a theorem showing which structural assumptions allow the manufactured certificate to carry over. At minimum, demonstrate the certificate on a learned actor in a problem with the same first-exit, interpolation, and control geometry as the economic model, and separately report value/regret accuracy versus policy sup-norm accuracy.

## 7. Blocking finding R5-F5: the new high-dimensional benchmark does not demonstrate an NBO advantage and is structurally too favorable

The new nonlinear benchmark is the strongest addition in R5, but its own results do not establish the numerical-method contribution claimed for NBO.

The delivered table reports:

| d | NBO mean loss | PINN-PI mean loss | NBO train s | PINN-PI train s |
|---:|---:|---:|---:|---:|
| 8 | 0.0010 | -0.0001 | 14.93 | 12.59 |
| 16 | 0.0037 | 0.0013 | 14.29 | 11.67 |
| 32 | 0.0102 | 0.0075 | 16.29 | 13.34 |

NBO has the larger mean loss and longer training time at every tested dimension. Including the separately reported audit time gives approximate train+audit totals of 18.38 versus 19.20 seconds at d=8, 18.13 versus 17.36 at d=16, and 20.01 versus 18.98 at d=32. Thus there is no consistent end-to-end speed advantage either.

More importantly, the benchmark does not exercise the difficult action-optimization problem that motivates NBO. For the model dX = a dt + sqrt(2)dW with quadratic control cost, the greedy action is analytically a = -2 grad v. The in-house PINN-PI comparator uses this formula directly. NBO does not learn the action by solving a hard implicit Hamiltonian problem; in nonlinear_control.py its actor is trained by squared-error regression to the detached analytic target -2 grad v. The value reference is also available through a Cole-Hopf/QMC representation.

This is therefore closer to a policy-network approximation test than a decisive benchmark of an operator method that allegedly avoids difficult inner optimization. The 8-dimensional PINN-PI mean “loss” being slightly negative is an additional warning that sampling/time-discretization error is of the same order as the smallest measured method differences.

**Required for a publishable revision:** add at least one high-dimensional benchmark with no closed-form greedy action, nonconvex or constrained controls, and preferably control-dependent diffusion. Use a target for which NBO’s architectural choice is genuinely needed. Compare at matched accuracy, matched wall-clock/resource budget, and matched implementation quality. If NBO does not outperform alternatives, the paper must identify a different, demonstrated benefit and narrow the claim accordingly.

## 8. Blocking finding R5-F6: the external comparator and current-literature positioning are still insufficient

R5 compares against an explicitly in-house “PINN-PI” implementation rather than authors’ code from a published method. That makes the experiment useful as an internal ablation but weak as a state-of-the-art comparison.

The surrounding literature has moved quickly. Relevant examples include:

- Kim, Cho, Kim, and Kim (AAAI 2026), “Physics-Informed Approach for Exploratory Hamilton-Jacobi-Bellman Equations via Policy Iterations,” DOI 10.1609/aaai.v40i27.39421. This paper supplies a mesh-free policy-iteration method and decomposes approximation error into iteration, policy-network, and PDE-residual components.
- Kim, Kim, Kim, and Cho (posted 18 Aug 2026), “Physics-Informed Policy Iteration for High-Dimensional Hamilton-Jacobi-Bellman Equations: Interior Error Bounds without Boundary Data,” DOI 10.2139/ssrn.7306930. This is directly relevant to interior error control and model-only safeguards.
- Cai, Fang, and Zhou, “SOC-MartNet,” SIAM Journal on Scientific Computing 47(4), 2025, DOI 10.1137/24M1681033. The method trains value/control networks without requiring an explicit infimum of the Hamiltonian and reports very high-dimensional stochastic-control tests, including drift/volatility control.
- Lee and Kim, “Hamilton-Jacobi based policy-iteration via deep operator learning,” Neurocomputing 646 (2025) 130515, DOI 10.1016/j.neucom.2025.130515.

I am not asserting that any one of these methods dominates NBO. The point is that the current revision does not yet establish a clean incremental contribution against this literature. A bespoke comparator that is worse in some metrics and better in others cannot carry the novelty burden.

**Required for a publishable revision:** add a contribution matrix separating assumptions, inner-control treatment, error guarantees, boundary handling, state/action dimension, equilibrium/recursive scope, and observed compute. Reproduce at least one credible external implementation or benchmark protocol from the closest methods. Claims of superiority should be made only where the side-by-side evidence supports them.

## 9. Major finding R5-F7: the statistical design is still too thin for the precision of the numerical claims

The confirmatory NDU baseline is much better designed than R4, but the extension panels remain small:

- high-dimensional NBO/PINN-PI: only two seeds per method and dimension;
- recursive utility: two confirmatory seeds;
- game: two confirmatory seeds;
- QMC reference: four scrambles at each power;
- policy audits reuse a fixed rollout seed 9921 across configurations.

Common random numbers can be beneficial, but then the natural object is a paired difference with a paired uncertainty estimate. The paper reports means and one-method sampling upper bounds instead. There is no uncertainty interval for “NBO versus PINN-PI,” no power analysis, and no uncertainty on failure probabilities.

The target construction is also not compelling. The NDU protocol explicitly says that 0.05 is retained from R4 and is not calibrated to economic data. The extension protocol carries the same 0.05 diagnostic into a different high-dimensional model with different value scale and units. The baseline NDU localized bounds cluster close to the threshold—roughly 0.0390 to 0.0496, with one run at 0.049627—after a development pilot had already produced a 0.0421 bound. That is not misconduct; the protocol is transparent about its post-pilot status. But it means the threshold should be treated as a development diagnostic, not as an economically or statistically meaningful success criterion.

**Required for a publishable revision:** use model-specific tolerances tied to welfare/value accuracy or an explicit numerical target; add more independent seeds; report paired confidence intervals for method differences; separate Monte Carlo, QMC, and time-discretization uncertainty; and report the full empirical distribution of raw failures and safeguard corrections.

## 10. Major finding R5-F8: the recursive and game extensions are useful demonstrations, but they do not yet establish the advertised generality

The recursive model is now a real learned operator, which is an improvement. But both confirmatory raw actors miss the declared 0.01 log-loss target by a wide margin: 0.04246 and 0.05018. The final near-zero losses arise only after the 961-action global_q safeguard is repeatedly applied. The recursive extension therefore reinforces, rather than resolves, the concern that the neural actor requires conventional action search to achieve the reported certificate.

The game experiment is cleaner. The all-subgame best-response gains of about 0.0067 and 0.0037 are encouraging, and the audit checks an exact continuous best response for the finite Markov-state operator. But the problem has only three dates and 18 states, and the best response is analytically reducible to a small piecewise-quadratic search. The delivered record explicitly disclaims any continuum-state equilibrium assertion.

These experiments are valuable unit tests of interfaces. They are not yet evidence that one numerical framework scales to the broad class of recursive utilities and dynamic games suggested by the paper’s scope.

**Required for a publishable revision:** either narrow these sections to proof-of-concept extensions or scale at least one of them beyond exact finite-state/action-search validation. For recursive utility, report raw actor accuracy separately and eliminate or bound the safeguard dependence. For games, show nontrivial state dimension, longer horizon, and a best-response problem that is not analytically solved by a tiny enumeration of segments.

## 11. Major finding R5-F9: the economic comparative statics remain coarse-grid and partly corner-driven

The k-sensitivity results at N=48 are directionally plausible but numerically too coarse to support a strong economic theorem or calibration claim. The center action at k=0.5 and k=2 is [0.8, 0.2, 0.15]; at k=8 it is [0.8, 0.1, 0.15]. Thus the reported reconfiguration choice changes by one action-grid step while consumption remains at its upper bound and the portfolio component is unchanged. The action mesh maximum is 0.325.

The center budget changes from about 0.01697 to 0.01197 to 0.00241 as k increases, while the exit probability remains about 0.102. Those are interesting diagnostics, but because the continuum action error is unbounded and the center policy is coarse, the numerical experiment cannot yet distinguish a smooth continuous comparative static from a grid-threshold effect.

**Required for a publishable revision:** evaluate the comparative static with a continuous optimizer or a certified action-approximation bound, demonstrate stability under action refinement, and report economically interpretable welfare differences with an error bar smaller than the comparative-static effect.

## 12. Blocking finding R5-F10: the reviewed R5 HEAD does not contain a complete, canonical manuscript artifact

This is a publication-process blocker independent of the mathematical issues.

At the reviewed commit 448b1153cb2a9e89fff295b9ab0ad90ef5496bef:

1. The HEAD commit message is “paper(r5): transport verified manuscript and response capsule, part 2 of 10.”
2. Only revisions/2026-09-21-r5/manuscript_transport/paper-0.b64 and paper-1.b64 are present.
3. paper-2.b64 through paper-9.b64 are absent.
4. ECTA_R5.tex and SUPP_R5.tex are absent.
5. The existing R5 review-build workflow begins by requiring ECTA_R5.tex and SUPP_R5.tex and does not reconstruct the manuscript transport capsule.
6. The R5 manifest does not bind ECTA_R5.tex, SUPP_R5.tex, or the manuscript_transport pieces.
7. The recorded numerical CI execution points to source commit 373404fa134de91fb2d1be660493004605c6649b, not to the reviewed manuscript HEAD. The later manuscript transport commits may be content-only, but the repository currently lacks a single manifest tying the exact manuscript, exact numerical evidence, and exact build result together.
8. The reviewed HEAD has no combined commit statuses.

The numerical evidence under revisions/2026-09-21-r5 is sufficiently visible to permit the technical review above. The manuscript itself is not. A peer-review branch should never require a reviewer to reverse-engineer a partial base64/gzip transport stream, and an incomplete 2-of-10 stream is not an authoritative paper artifact.

**Required before any further review round:** commit the full human-readable manuscript and supplement as canonical plaintext sources; make a clean checkout build them without hidden/manual reconstruction; add the exact files to the SHA-256 manifest; pin a successful build to the exact reviewed commit; and commit the response-to-referee letter in human-readable form. Do not use a transport capsule as the only reviewable manuscript representation.

## 13. Questions that the authors must answer explicitly

1. What exact mathematical statement connects the finite candidate-set gain envelope to the continuous action domain?
2. What are the separately bounded contributions of time discretization, state interpolation, action coverage, quadrature, and first-exit treatment in the target NDU model?
3. Is the safeguard part of NBO or merely a diagnostic? If it is part of the method, why should its exhaustive action enumeration not be viewed as discrete policy iteration?
4. How does safeguard cost scale with action dimension, and what happens when a 125- or 961-action grid is no longer feasible?
5. Why do all n=12 raw NDU runs fail while the safeguarded runs pass only after replacing roughly half the policy?
6. Why do both recursive raw policies miss the prespecified target, and what remains of the neural contribution after two global-grid improvement sweeps?
7. In the high-dimensional benchmark, what problem is NBO solving that is not already solved analytically by a = -2 grad v?
8. Why is NBO’s mean loss larger than PINN-PI’s at d=8,16,32, and what demonstrated advantage should the reader take from that benchmark?
9. How is the 0.05 target economically or numerically calibrated across models with different value scales?
10. Can a third party reproduce the exact reviewed manuscript and all tables from the exact reviewed commit with one documented command?

## 14. Minimum conditions for a credible resubmission

I would regard the following as minimum, not optional polish:

### P0 — scientific validity

- Close the end-to-end continuum error loop for the actual NDU learned policy, including action-domain coverage and first-exit treatment, or sharply narrow the paper to a discrete candidate economy.
- Treat the safeguard as an explicit algorithmic component and count its full complexity; demonstrate that it does not replace most of the learned policy in the regimes used to claim robustness.
- Produce a converged/certified NDU economic calculation whose total error is materially smaller than the economic effects discussed.
- Add a genuinely difficult high-dimensional benchmark with no analytic greedy action and no Cole-Hopf reduction, and compare with at least one credible external method at matched budgets.

### P0 — reviewability and reproducibility

- Restore complete canonical plaintext R5 manuscript/supplement/response files.
- Make the canonical build pass from a fresh checkout of the exact reviewed commit.
- Bind source, manuscript, tables, results, checkpoints, and build outputs in one manifest.

### P1 — evidence quality

- Increase extension seed counts and report paired uncertainty for method comparisons.
- Replace cross-model reuse of the arbitrary 0.05 threshold with model-specific numerical/economic accuracy targets.
- Demonstrate action-refinement stability of the economic comparative statics.
- Either scale the recursive/game extensions or explicitly label them as finite-model proof-of-concept demonstrations.

## 15. Recommendation

**Reject in its present form.**

R5 demonstrates that the authors can engineer a substantially more careful computational package and can respond constructively to specific numerical objections. That is encouraging. But the most important remaining issues are conceptual, not cosmetic: what is actually certified, what algorithm is actually being benchmarked after safeguards, whether the target continuous economic problem is numerically resolved, and whether the method has a demonstrated advantage on a problem that requires it.

A future submission could become much stronger if it centers the paper on one rigorously closed end-to-end numerical theorem plus one genuinely hard, competitive benchmark, rather than accumulating additional interface demonstrations. At present, however, the evidence does not meet the standard I would require for an Econometrica-level numerical-methods contribution.

---

## Evidence reviewed

Primary repository evidence includes:

- revisions/2026-09-21-r5/protocol.json
- revisions/2026-09-21-r5/extensions_protocol.json
- revisions/2026-09-21-r5/manifest.json
- revisions/2026-09-21-r5/replication/continuous_actor.py
- revisions/2026-09-21-r5/replication/nonlinear_control.py
- revisions/2026-09-21-r5/replication/recursive_neural.py
- revisions/2026-09-21-r5/replication/neural_game.py
- revisions/2026-09-21-r5/replication/scheme_validation.py
- revisions/2026-09-21-r5/replication/boundary_certificate.py
- revisions/2026-09-21-r5/replication/validate_r5.py
- revisions/2026-09-21-r5/results/summary.json
- revisions/2026-09-21-r5/results/manufactured_boundary_bounds.json
- revisions/2026-09-21-r5/results/recursive_s51.json and recursive_s52.json
- revisions/2026-09-21-r5/results/game_s61.json and game_s62.json
- revisions/2026-09-21-r5/results/nonlinear_d{8,16,32}_s{40,41}_{nbo,pinnpi}_o4_e800_a400_w192.json
- revisions/2026-09-21-r5/results/coupled_*.json
- revisions/2026-09-21-r5/paper/table_ndu.tex
- revisions/2026-09-21-r5/paper/table_nonlinear.tex
- revisions/2026-09-21-r5/paper/table_boundary.tex
- revisions/2026-09-21-r5/paper/table_coupled.tex
- revisions/2026-09-21-r5/paper/table_recursive.tex
- revisions/2026-09-21-r5/paper/table_game.tex
- .github/workflows/r5-execute-and-pin.yml
- .github/workflows/r5-review-build.yml
- prior R4 referee report for issue-by-issue comparison.

Current literature was checked against the publisher/venue records for the AAAI 2026 PINN policy-iteration paper, the August 2026 interior-error-bound preprint, SOC-MartNet (SIAM J. Sci. Comput. 2025), and the 2025 PI-DeepONet paper cited above.
