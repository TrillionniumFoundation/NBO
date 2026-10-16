# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r54-review-ready-2026-10-08`  
**Pinned revision commit:** `00e837adb431f4d4b5248fc6d5ff1fc927dd3b65`  
**Pinned revision tree:** `70fe6bd2584c9026f0f31e9dfd5f3b3a23c1ed86`  
**Pinned main manuscript:** `revisions/2026-10-08-r54/ECTA.tex`, Git blob `a8bbb8831aba4539158469a0f31016ec36f26f4e`  
**Pinned technical supplement:** `revisions/2026-10-08-r54/supp.tex`, Git blob `cd4a37bb03e488bb180ce032a9c89526d737ce5d`  
**Pinned response:** `revisions/2026-10-08-r54/response.md`, Git blob `cdbd053a4856c55addb67ed0655e1fea87a3d8b1`  
**Publication workflow / artifact:** `37811366061` / `11565815940`  
**Artifact SHA-256:** `3b74173305dd489f900f4fd3c7dcf2a71a115856fc8ef5368e5867a1d510f9e5`  
**Report date:** 9 October 2026  
**Recommendation:** **Reject in the present form and do not invite another ordinary revision of the cumulative manuscript. A new, sharply focused paper on directed safe policy improvement with coupled-residual verification in acquired-state dynamic programs could merit evaluation, but R54 does not establish a method-specific Econometrica-level numerical or economic advantage for Neural Bellman Operators.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R54 is the strongest and most complete version of this project that I have reviewed. It is a canonical, source-bound revision rather than a detached science branch or incomplete workflow artifact. The release contains a 67-page active article, a 45-page active supplement, a 9-page response, complete development editions, frozen evidence, 80 passing tests, and a successful clean-archive rebuild. The branch and publication artifact identities are internally consistent.

The revision also responds substantively to the R52 report. The new directed finite-sweep theorem is no longer confined to a zero or terminal-only setting. It gives an incumbent-preserving policy-improvement recursion in which the coefficient on the previous policy error is one, and exact greedy certificates recover the finite-horizon Bellman optimum after finitely many simultaneous sweeps. The paper then executes that theorem in the original two-state continuous-law investment economy for horizons two and three. It evaluates actual policy costs, records all-date action changes, exposes pair-recursion work and storage, adds a nonuniform conventional comparator, and studies controlled departures from exact action-null structure.

I found no immediate algebraic contradiction in the directed policy-safety argument, the finite-sweep recursion, the signed coupled-residual transport identity, or the exact-horizon conclusion under the stated premises. The manuscript is also appropriately candid that the certificate is representation neutral, that the adaptive comparator remains tensor based, that controlled perturbations are not learned-null discovery, and that one timed service is not a hardware-general speed ranking.

The scientific conclusion, however, remains unfavorable to the broad method claim.

The compiled-witness policies do improve their own incumbents. At horizon two, the final own-incumbent expected-cost gain is certified in `[0.00665, 0.01683]`; at horizon three it is `[0.00344, 0.01579]`. This is a real positive result. But the contemporaneous tensor-FVI policies begin with lower expected cost, their final all-state directed gap bounds are tighter, and their final expected-cost upper endpoints remain lower. The final witness-minus-FVI cost intervals contain zero at both horizons, so the executed evidence identifies neither witness superiority nor equivalence.

The numerical rankings are especially important. After the final sweep, the witness all-state gap is approximately `0.08149` at `T=2`, versus `0.06317` for tensor FVI, and approximately `0.22556` at `T=3`, versus `0.09350` for tensor FVI. Thus the witness bound is about 1.29 and 2.41 times the FVI bound. Complete service time is essentially tied at `T=2` and is slightly worse for the witness at `T=3`. The postprocessed complete-catalogue frontier gives the witness a roughly 0.03-second advantage only at the looser horizon-two cost-upper target, while tensor FVI alone reaches the stricter target. At horizon three, tensor FVI has both the lower cost upper endpoint and the lower recorded catalogue work.

The adaptive extension does not reverse this conclusion. Surplus-driven FVI has the smallest cost upper endpoint, tensor FVI has the least recorded work at the common looser targets, and the compiled witness has neither the sharpest cost endpoint nor the least work. The surplus method is more expensive, but it demonstrates that a stronger conventional method can move the cost frontier without invoking the witness backend.

The new verification account is computationally explicit, which is a virtue, but it also reveals the limitation. In the final horizon-three pass, each method performs roughly 9.7 million actor queries and visits roughly 4.9 million pair nodes. More than 95 percent of the actor boxes are ambiguous under the retained interval calculation. The theorem retains tensor-state dependence and an exponential-in-horizon pair recursion. The executed study remains two-dimensional and has horizons only two and three.

The strongest contribution in R54 is therefore a representation-neutral theorem and verification architecture for safe simultaneous policy improvement in a low-dimensional acquired-state dynamic program. That contribution may be publishable in a focused paper. It is not evidence that a neural representation improves the work-to-accuracy frontier, that NBO dominates strong conventional dynamic programming, or that the broad controlled-diffusion, recursive-preference, temporal-self, and game program has received a common constructive numerical foundation.

I recommend rejection in the present form and against another ordinary revision of the cumulative manuscript.

## 2. What R54 successfully repairs

### 2.1 The submission is canonical, complete, and reproducible

The review-ready branch contains ordinary sources, compiled PDFs, raw evidence, generated tables, source identities, release audits, and clean-rebuild records. The active article and supplement have no undefined references, duplicate labels, missing characters, or overfull boxes. Five publication documents reproduce with matching page counts and extracted text under the clean-archive build.

This resolves the publication-threshold failures that affected several earlier rounds.

### 2.2 The directed theorem is a genuine nonzero dynamic result

The new theorem separates two enclosures on each acquired-state cell:

1. an upper bound on the selected candidate’s advantage relative to the incumbent; and
2. a lower bound on the best feasible continuous-action advantage.

Their difference is a directed greedy-gap allowance. If the selected upper bound is nonpositive, the adopted policy is statewise no worse than the incumbent. The policy-error recursion

\[
E_t^{k+1}\leq \beta_t E_{t+1}^{k}+\varepsilon_t^k
\]

uses coefficient one rather than an avoidable factor two. Under exact full-action greedy certificates, backward propagation across passes reaches the finite-horizon optimum after at most the horizon number of passes.

This is a useful theorem independently of the neural representation.

### 2.3 The theorem is executed at every decision date

R54 does not certify only a terminal action. Each frozen incumbent is improved simultaneously at all dates, then independently verified before the next pass. The horizon-two study executes two passes and the horizon-three study executes three. The raw records retain accepted, blocked, and equal candidate comparisons, continuous-action lower covers, action arrays, gap recursions, and complete work.

This directly addresses the principal execution request in the R52 report.

### 2.4 Actual policy cost is now the primary endpoint

The revision evaluates every retained pass policy under the original continuous initial and innovation laws. It reports absolute expected costs, gains relative to each method’s own initial policy, stepwise gains, and contemporaneous witness-minus-FVI contrasts. The intervals are based on common paths and a simultaneous family account rather than on subtracting separate regret upper bounds.

The positive own-incumbent witness gains are therefore economic policy-value statements, not merely certificate improvements.

### 2.5 Work and storage are charged explicitly

The paper records actor-table preprocessing, pair nodes, actor queries, ambiguity counts, peak resident memory, serialized arrays, complete service clocks, and shared inference clocks. It distinguishes logical actor-table storage from total process memory and states the tensor and horizon dependence explicitly.

The complete-catalogue table also states that it is not a minimum-work sequential stopping frontier. This is honest and important.

### 2.6 A stronger conventional comparison is included

The extension adds surplus-driven FVI with nonuniform tensor coordinates. The paper does not call this a sparse-grid or non-tensor method. It also retains tensor FVI, which remains a strong comparator in the primary experiment.

The negative conventional results are not hidden.

### 2.7 Approximate nullity is no longer treated as exact by assumption

The paper derives a quantitative action-contrast allowance for known perturbations of ReLU directions, action exposures, and action-dependent innovation means. The 384-case catalogue preserves corrected safe choices and deliberately false-null choices. It records 116,185 cell-cases in which the false-null policy is certified harmful.

This is a valuable robustness warning and a meaningful response to the previous report.

### 2.8 Provenance and adverse evidence remain exemplary

The protocol predates the production services. Source freezes, policy hashes, path streams, endpoint moments, publication inputs, and clean rebuilds are recorded. Unresolved cross-method comparisons, conventional advantages, nonattained claims, and the limitations of the adaptive and misspecification exercises are retained.

## 3. Blocking concerns

### B1. The main theorem is not a method-specific neural contribution

The directed policy-safety argument applies to any incumbent, candidate menu, and valid advantage enclosure. Its proof uses Bellman monotonicity, feasible adoption, and signed policy-value transport. None of these depends on a neural representation.

The compiled witness used in the study is itself policy-identical to a native min-plus/Lipschitz-envelope implementation established in the preceding revisions. The ReLU form is an exact representation of the same continuation and witness selector. R54 appropriately admits this, but the consequence is substantive: the theorem and the strongest positive evidence belong to a general certified policy-improvement method, not to an identified neural numerical advantage.

For an Econometrica numerical-method paper under the title *Neural Bellman Operators*, the manuscript must isolate something that the neural representation or training contributes beyond exact encoding. R54 does not do so.

### B2. The actual policy-cost evidence does not favor the witness method

At horizon two, the witness is certified to improve its own policy, but tensor FVI has a lower final cost upper endpoint:

- witness: `[0.59093, 0.61168]`;
- tensor FVI: `[0.58984, 0.61062]`.

At horizon three the same ordering holds:

- witness: `[0.70899, 0.73147]`;
- tensor FVI: `[0.70577, 0.72833]`.

The final paired witness-minus-FVI intervals are `[-0.00375, 0.00589]` and `[-0.00287, 0.00923]`. They are unresolved. Earlier passes significantly favor FVI: the pass-zero and pass-one intervals have strictly positive lower endpoints at both horizons.

The correct conclusion is that the witness closes part of its initial disadvantage. It is not that the witness policy is better, equivalent, or economically preferred.

### B3. The conventional method has the tighter final all-state certificate

The final directed gap bounds are:

- `T=2`: witness `0.08149`, tensor FVI `0.06317`;
- `T=3`: witness `0.22556`, tensor FVI `0.09350`.

The witness-to-FVI ratios are approximately 1.29 and 2.41. The central certification mechanism therefore does not yield the sharpest final guarantee for the method highlighted by the paper.

The empirical witness gains are much smaller than these all-state bounds. This is not a contradiction—the objects are different—but it shows that the operational certificate remains too conservative to identify the method ranking that motivates the numerical study.

### B4. The reported catalogue frontier is retrospective, not an executable stopping service

For each method the catalogue selects the pass with the smallest simultaneous actual-cost upper endpoint after every planned pass and the full shared inference service have already been executed. All own construction and sweep work is charged, which is conservative, but the procedure is not a prospective rule that knows when to stop.

At `T=2`, the witness uses approximately `8.463` seconds and FVI `8.493` seconds at the looser common target, a difference of roughly 0.36 percent. Yet FVI alone reaches the stricter recorded cost-upper target. At `T=3`, FVI is both less costly and faster. In the adaptive cohort tensor FVI is less costly and faster than the witness at common targets, while surplus FVI reaches the strictest endpoint at much higher work.

This finite post hoc partition is useful descriptive evidence. It does not establish a deployable work-to-certified-cost algorithm. A journal numerical-method claim should be based on a prespecified stopping rule with method-specific inference costs and failure accounting.

### B5. Verification remains computationally heavy and poorly scaled

The h=0 specialization evaluates incumbent policy-value differences from primitive stage and terminal costs. This makes the certificate genuine, but it also means that verification contains a substantial policy-evaluation problem.

In the final horizon-three pass, the witness uses approximately 9.76 million actor queries and 4.93 million pair nodes; tensor FVI uses approximately 9.67 million and 4.89 million. Ambiguous actor boxes account for approximately 96.2 and 95.5 percent of actor queries. The paper’s own complexity statement retains tensor state-cover dependence and a geometric horizon term.

Only `d=2`, `T=2`, and `T=3` are executed. R54 therefore supplies a careful low-dimensional verifier, not evidence that the approach resolves the state or horizon scaling problem central to modern numerical dynamic programming.

### B6. The adaptive comparator does not establish a neural or witness frontier

The surplus-driven FVI comparator uses nonuniform coordinate sets but remains a tensor method. It has the smallest actual-cost upper endpoint in the adaptive cohort, reaches that endpoint with much larger recorded work, and does not alter the conclusion that tensor FVI is the least-work method at the common looser targets.

The witness is neither the least-cost policy nor the least-work method in this cohort. The experiment is useful precisely because it shows that stronger conventional approximation can move the cost endpoint. It does not provide evidence for a witness or neural advantage.

### B7. Approximate-null robustness is controlled, not learned or model-robust

The misspecification study changes known coefficients in a declared ReLU direction, action exposure, and innovation mean. The correct contrast allowance is then computed from those known changes. This proves that the bound reacts correctly when the analyst knows how the null structure is violated.

It does not address the harder numerical problem:

- discovering an approximately null direction from fitted data;
- estimating its uncertainty;
- maintaining validity under an unknown transition kernel;
- or deciding when the null simplification should be rejected.

The maximum recorded contrast allowance is approximately `315`, and false-null selection is certified harmful in 116,185 cell-cases. These numbers show that the issue can be severe. They do not establish a practical learned-null procedure.

### B8. Reliability evidence concerns a finite catalogue, not a method population

The deterministic policy and certificate theorems are uniform under their premises. The numerical evidence concerns four primary construction services, one adaptive cohort, and a controlled deterministic perturbation catalogue. The actual-cost intervals are conditional on frozen policies and an independent-bin sampling model.

There is no population of independently trained neural objects, no distribution over economic tasks, and no repeated hardware-controlled service experiment. Single-host times are descriptive. The successful clean rebuild establishes reproducibility of the frozen release, not method-level reliability or performance generalization.

### B9. The economic conclusion remains narrow and uncalibrated

The executed economy is a normalized theoretical two-capital investment model with horizons two and three. The positive finding is that the compiled witness can safely improve its own incumbent under the stated construction. No calibrated counterfactual, estimated welfare threshold, substantive policy mechanism, or economically motivated stopping cost is supplied.

An abstract numerical-method paper need not be empirical. It must then deliver a sufficiently general or efficient computational result. R54’s low-dimensional tensor experiment and adverse conventional ranking do not satisfy that alternative route.

### B10. The cumulative scope remains disproportionate to the completed contribution

The active article is 67 pages and the active supplement 45 pages; the complete development editions are 130 and 107 pages. The manuscript retains controlled diffusions, recursive utility, endogenous preferences, temporal selves, games, finite sensing, and many earlier experiments.

The new directed theorem and execution apply to a finite-horizon expected-cost model with a specific acquisition and continuous-law verification structure. The other applications retain their own hypotheses and do not receive the same finite-sweep construction or evidence.

Preserving history is commendable. Carrying it as coequal support for the current Econometrica contribution makes the paper harder to assess and overstates the reach of the new result.

## 4. Major comments and required changes

### M1. Reframe the contribution around directed safe policy improvement

The theorem should be presented as a representation-neutral result. A focused title such as *Directed Safe Policy Improvement with Coupled-Residual Verification* would accurately locate the contribution. Neural realization can remain one implementation class, but it should not carry a method-specific claim without separate evidence.

### M2. Define and execute a prospective stopping algorithm

Prespecify how a method chooses whether to run another sweep, how it allocates inference error, and when it returns a policy. Charge all failed passes, verification, inference, and durable output. Compare methods at the first attained common actual-cost or loss target under that rule.

The current after-the-fact catalogue partition is not enough.

### M3. Compare complete work at matched economic accuracy

Use a denser set of prespecified policy-cost targets or a valid anytime procedure. Report construction, verification, path evaluation, inference, storage, and memory. The target should bind rather than leave methods compared at different effective accuracies.

### M4. Improve or decompose certificate tightness

The final witness certificate is materially wider than the FVI certificate. Report the contribution of candidate-menu coverage, continuous-action lower coverage, actor ambiguity, innovation coupling, state acquisition, and interval arithmetic to the final gap. Then target the dominant terms algorithmically.

### M5. Execute a non-tensor multidimensional benchmark

A serious scaling study should include sparse grids, adaptive partitions, low-rank approximation, or another genuinely non-tensor method in a coupled nonlinear economy. State and horizon dependence should be observed rather than only written as an upper bound.

### M6. Use strong policy-iteration and value-approximation baselines

Tensor FVI and surplus FVI are useful, but the comparison should include a modern approximate-policy-iteration or adaptive value-method baseline under the same policy-safety verifier. This would separate the verifier’s contribution from the candidate generator.

### M7. Turn approximate-null analysis into an inferential procedure

Specify how an approximate null direction is estimated, how estimation error enters the action-contrast bound, and how the method rejects an unsafe simplification. Test it on fitted rather than hand-perturbed directions and on transition-law uncertainty.

### M8. Add controlled performance repetitions

Use isolated repeated executions, fixed affinity, controlled numerical-library threads, and reported frequency conditions where possible. Separate deterministic policy identity from timing variation. Include machine-independent operation and byte counts alongside clocks.

### M9. Supply an economically consequential application

Either calibrate the information, computation, or policy-loss tolerance in economic units, or apply the method to a theoretical problem where the safe-improvement result changes a substantive conclusion that conventional methods cannot obtain as sharply at comparable work.

### M10. Produce one focused paper

A publishable manuscript should contain one model class, one directed theorem, one candidate-generation comparison, one prospective service design, one scaling study, and one substantive economic use. The extensive historical program can remain in a repository companion.

## 5. A focused publishable route

A credible new submission could center on:

> **Directed Safe Policy Improvement under Acquired States**

The mathematical core would contain:

1. the incumbent-preserving adoption theorem;
2. the finite-sweep error recursion and its sharp coefficient;
3. signed coupled-residual verification;
4. acquisition and continuous-action coverage;
5. explicit work, storage, and arithmetic contracts; and
6. controlled approximate-structure inference.

The numerical paper would then need:

1. a prospective stopping rule;
2. strong representation-neutral baselines;
3. direct policy-cost intervals at matched targets;
4. a non-tensor multidimensional benchmark;
5. repeated complete-work measurements; and
6. an economic exercise whose conclusion depends on the method.

That would be a coherent and potentially valuable contribution. It would not require claiming that an exact ReLU encoding creates a neural advantage.

## 6. Independent verification performed for this report

I independently downloaded and inspected the R54 workflow artifact `nbo-r54-paper-audits-and-logs` and verified its SHA-256:

`3b74173305dd489f900f4fd3c7dcf2a71a115856fc8ef5368e5867a1d510f9e5`.

The review audit then:

1. verified the five committed PDF digests and their reported page counts;
2. confirmed the canonical branch, workflow run, clean rebuild, 1,600-file delivery, and 80-test release;
3. parsed the frozen R54 result audit and recomputed the primary cost intervals and cross-method signs;
4. recomputed the final witness-to-FVI gap ratios, service-time ratios, actor-query counts, pair-node counts, and ambiguity rates;
5. reconstructed the three complete-catalogue cost/work frontiers;
6. checked the 384-case misspecification totals and harmful false-null count; and
7. confirmed that no new policy-cost samples or scientific services were generated during the R54 publication build.

Key independently recomputed values include:

- witness/FVI final gap ratio: approximately `1.28997` at `T=2` and `2.41226` at `T=3`;
- final witness-minus-FVI intervals: `[-0.0037504, 0.0058923]` and `[-0.0028735, 0.0092341]`;
- witness final cost-upper excess over FVI: approximately `0.0010562` and `0.0031404`;
- final horizon-three actor queries: approximately `9.76` million for witness and `9.67` million for FVI;
- final horizon-three pair nodes: approximately `4.93` million and `4.89` million;
- harmful false-null cell-cases: `116,185`.

The review directory contains the deterministic standard-library script and its machine-readable output. I did not rerun policy construction, simulation, inference, or timing services. A new run would create new statistical and performance observations rather than verify the frozen ones.

## 7. Recommendation

R54 deserves substantial credit. It closes the main formal and execution gaps identified in R52, supplies a coherent canonical publication, proves a useful directed safe-improvement theorem, executes full policy sweeps in the continuous-law economy, evaluates actual policy costs, and exposes the computational bill honestly.

The new evidence nevertheless does not support the broad NBO claim. The central theorem is representation neutral; strong conventional policies have tighter final certificates and lower cost upper endpoints; signed cross-method differences remain unresolved; the catalogue frontier is not a prospective stopping service; verification retains severe tensor and horizon dependence; and the economic application remains normalized and narrow.

I therefore recommend **rejection in the present form and no further ordinary revision of the cumulative manuscript**. A new, focused paper on directed safe policy improvement and coupled-residual verification could merit serious consideration after the method contribution, stopping design, scaling evidence, and economic use are isolated.
