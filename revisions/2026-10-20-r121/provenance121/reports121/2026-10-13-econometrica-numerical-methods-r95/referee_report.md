# Referee Report on "Neural Bellman Operators" — Revision R95

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r95-integrated-2026-10-13`  
**Pinned revision commit:** `85263fd95ccbb60f0cf1875c0f29f1b7c2558a34`  
**Pinned revision tree:** `c302a05050f1100b86398db3f5e6a2e99fc8500a`  
**Pinned main manuscript:** `revisions/2026-10-13-r95/ECTA.tex`, Git blob `8cf26137129209e533d3e457357a14cb3f980a85`  
**Pinned technical supplement:** `revisions/2026-10-13-r95/supp.tex`, Git blob `4cbab50c9757fbaff5bd2ae10255f22247d20520`  
**Pinned numerical appendix:** `revisions/2026-10-13-r95/appendix.tex`, Git blob `448f3ac0b44a5107d9c4cdf2c3c26f996969711d`  
**Pinned response:** `revisions/2026-10-13-r95/response.md`, Git blob `c0c098bb6663d92ed6d8c75f12ccc0214f319726`  
**Release workflow:** `38398977506`  
**Release artifact:** `11818488156`, SHA-256 `494923d18f313d81103002cf95610243324e43a65c798dfdb89683e5b94c14cc`  
**Report date:** 13 October 2026  
**Recommendation:** **Reject in the present form and do not continue the cumulative manuscript through another ordinary revision round. R95 contains a substantial, potentially publishable theorem--algorithm--evidence core, but the current submission does not yet establish an Econometrica-level neural-specific contribution, economically consequential gain, or practical scalability result. A new, sharply focused submission centered on certified stored continuations under recursive risk could merit evaluation after the release defect and the comparative-design issues below are resolved.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R95 is a major scientific advance over the earlier versions of this project. It is the first revision in which I see a coherent continuous-law theorem--algorithm--evidence chain under a nonlinear recursive risk criterion. The paper derives primitive curvature and global supports in the original investment technology, constructs an all-action lower certificate and a complete-policy upper enclosure under nested AVaR, and evaluates frozen stored continuations against a paid online risk-DP comparator. The numerical design separates training, calibration and evaluation streams, retains every arm, applies one common policy-accuracy requirement, and reports both positive and adverse findings. The source-preservation and failure-disclosure practice is unusually strong.

I found no immediate algebraic contradiction in the primitive-curvature proposition, the all-action qualification theorem, the strict tail-exclusion argument, the empirical-Bernstein account, or the horizon-uniform constructive bound under their stated assumptions. The new independent rational checker is also meaningful: it reconstructs the terminal shock polynomial, evaluates AVaR through a separate primal representation, uses its own one-date optimizer, and requires containment rather than mere overlap on the prescribed policy fixtures.

The main numerical result is now positive in an important but narrower sense. Storing a fitted continuation reduces the completed local evaluation workload from approximately 31--33 seconds for online risk-DP to approximately 11--12 seconds for each fitted representation. The corresponding terminal-proposal count falls from 112,721,920 to 13,631,488. This is a genuine computational finding, not merely a change in an error bound.

The same evidence, however, also determines the limits of the contribution.

First, the measured gain is a **stored-continuation effect**, not a neural effect. Quadratic, spline and ReLU continuations all achieve roughly the same reduction. The spline is fastest at one risk level, ReLU at the other, and the timing differences among fitted arms are not identified by one execution. ReLU has much narrower whole-square residual brackets, but its maximum joint-support policy-loss bounds are materially looser than those of the quadratic and spline fits. Calibration selects online risk-DP at both risk levels.

Second, the economic comparison identifies equivalence only at a generous normalized margin. All twelve simultaneous paired intervals include zero and have widths about 0.0595. The largest absolute midpoint difference is below 0.001. The equivalence margin is 1/16 = 0.0625, which the manuscript notes is four fifths of the maximum first-date investment charge. This is a valid numerical tolerance, but without an external economic calibration it is not an Econometrica-level welfare or policy conclusion.

Third, the executed experiment is two-dimensional, two-date and scalar-control. The new horizon proposition is a constructive existence and accounting result. Its operation count remains exponential in state dimension through the tensor cover, polynomially expensive in the requested accuracy, and subject to rational bit growth. It does not demonstrate practical long-horizon or vector-control scalability.

Fourth, the review-ready release is not green. The publication workflow concluded with failure, `RELEASE95.json` records `gates.tests=false`, and the complete test ledger contains one failed preservation-hash test. The scientific replay, independent kernel check and four document builds succeeded; the failure is a stale source-preservation identity for `sections/core49.tex`, not a demonstrated counterexample to the new theorem. Nevertheless, a submission whose own release contract fails cannot be treated as a final, source-frozen revision.

R95 therefore crosses the threshold from an exploratory research program to a credible computational-method paper. It does not yet cross the considerably higher Econometrica threshold. I recommend rejection of the current cumulative manuscript, while encouraging a focused new submission that preserves the strong R95 core and answers the comparative and economic questions directly.

## 2. What R95 successfully establishes

### 2.1 A continuous-law original-optimum certificate under nested risk

The new construction does not replace the continuous innovation law by a finite-state economic model. Innovation bins are numerical covers with outward upper and lower inequalities. A feasible risk density supplies a lower witness; binwise domination supplies an upper risk value; and the lower action model is minimized over the full original feasible interval. This is the right direction for a numerical method whose target is the original Bellman optimum rather than a discretized surrogate.

The state-dependent capacity constraint is handled within the support calculation, including an explicit penalty for imperfect action stationarity. The terminal controller includes acquired-state rounding, outward acceptance, and rational fallback. The policy upper bound therefore applies to the implemented controller, not to a hypothetical exact terminal optimizer.

### 2.2 A useful distinction between global residual size and local economic qualification

The fitted ReLU has the smallest training RMSE and by far the narrowest whole-square residual enclosure:

| Risk level | Quadratic residual width | ReLU residual width | Spline residual width |
|---|---:|---:|---:|
| 0.50 | 0.65826 | 0.13038 | 0.61988 |
| 0.75 | 0.65332 | 0.13642 | 0.55620 |

Yet the local joint-support policy certificate gives the following maximum original-optimum loss bounds:

| Risk level | Quadratic | ReLU | Spline |
|---|---:|---:|---:|
| 0.50 | 0.005501 | 0.021836 | 0.012112 |
| 0.75 | 0.006422 | 0.022145 | 0.008098 |

This is scientifically informative. A globally tighter approximation does not automatically give the sharpest policy certificate. The manuscript correctly avoids converting residual quality into an asserted economic ranking.

### 2.3 A positive, representation-neutral storage result

For 2,048 evaluation states per risk level, the completed execution reports:

| Risk level | Online risk-DP | Quadratic | ReLU | Spline |
|---|---:|---:|---:|---:|
| 0.50 | 32.509 s | 12.254 s | 11.797 s | 11.442 s |
| 0.75 | 30.770 s | 11.746 s | 11.237 s | 11.523 s |

Relative to online risk-DP, fitted-arm time reductions range from approximately 61.8% to 64.8%, or speedups of approximately 2.62--2.84 times. All fitted arms pay for an additional original-value witness. The operation ledger also records the large reduction in terminal proposals. This is a real result in favor of storing continuations for repeated evaluation.

### 2.4 A correctly qualified equivalence finding

All twelve prespecified simultaneous intervals lie inside `[-1/16,1/16]`, and all include zero. The manuscript therefore claims equivalence at the declared tolerance and does not claim strict superiority. This is the appropriate interpretation of the reported evidence. The calibration selector chooses online risk-DP at both risk levels, and every unselected arm remains in the comparison family.

### 2.5 Honest negative evidence on screening

The strict continuum-bin screen is mathematically valid and excludes many candidates. Once the proof and exclusion test are charged, however, every displayed screened calculation is slightly slower than the corresponding full calculation. The paper retains this adverse result. That separation between a valid certificate and a useful algorithm is exemplary.

### 2.6 A meaningful but limited independent implementation

The separate Fraction implementation does not import the production interval kernel or terminal fallback. It checks the six serialized fits, exact feature evaluations, all row identities, and selected policy fixtures under a finer continuous-law enclosure. This is considerably stronger than a checksum-only replay.

The manuscript also states the boundary correctly: the paired-inference replay shares the production statistical formula, and the independent implementation does not reproduce the complete learning stack or the largest vector recursion.

### 2.7 Transparent provenance and limitations

The paper distinguishes the local freeze from remote preregistration, preserves two interrupted starts, does not count a replay of the same stream as new observations, and labels the certificate re-accounting as post-evaluation. It also retains the old vector-scaling evidence and explicitly states that the new horizon theorem is not an execution of the largest vector benchmark.

## 3. Quantitative audit of the principal claims

My deterministic review audit of the pinned tables and release ledgers reproduces the following statements.

1. There are four arms, two risk levels and 2,048 evaluation states per arm-risk pair, hence 16,384 arm-state records and 4,096 independent initial-state observations.
2. All eight arm-risk workloads report zero qualification failures.
3. The largest displayed original-optimum loss bound is 0.022145, below the 0.0625 target.
4. All twelve paired intervals include zero and are strictly contained in the equivalence band.
5. Interval widths range from 0.059463 to 0.059666; their average width is approximately 0.059557.
6. The largest absolute paired-interval midpoint is approximately 0.000937.
7. The fitted-arm execution-time reductions relative to online risk-DP range from 61.83% to 64.80%.
8. ReLU has the narrowest whole-square residual enclosure at both risk levels.
9. Quadratic has the smallest maximum joint-support policy-loss bound at both risk levels.
10. The pruned tail calculation is slower than the full calculation in every displayed screening row.
11. Sixteen of seventeen test suites pass. Counting individual tests, 400 of 401 pass.
12. The sole failing test is a preservation-ledger hash comparison: the active `sections/core49.tex` no longer has the hash recorded in `audit/PREPARATION72.json`.
13. The release workflow, current PDFs, byte-identical replay and independent kernel check are retained; the aggregate release gate nevertheless records `tests=false`.

These checks validate the paper's own restrained interpretation. They do not provide an independent rerun of fitting, policy evaluation, timings, or the 302 MB workflow artifact.

## 4. Blocking concerns

### B1. The computational gain is not identified as neural

The strongest positive observation is that a stored continuation avoids repeated terminal risk-DP work. Quadratic, spline and ReLU fits all obtain the gain. Nothing in the completed comparison shows that the ReLU representation is necessary for the speedup, that it lies on a superior accuracy-work frontier, or that its tighter residual cover produces a better implemented policy.

This is not a semantic objection to the title. It is an identification problem. The certificate is representation-neutral, and the work gain is shared by non-neural approximators. The paper may still make a neural construction contribution, but it cannot use the present numerical evidence to establish a neural numerical advantage.

### B2. The approximation comparison is not budget matched

All fitted arms have 35 stored coefficients, but the projected-quadratic design has effective rank six. Nominal feature count is not approximation-space dimension, statistical degrees of freedom, conditioning, or training cost. Conversely, the spline basis is fixed and does not represent a strong adaptive non-neural approximation frontier.

A top-journal comparison should match several economically relevant budgets: independent rank, number of labels, serialized bytes, fitting time, evaluation operations, and certificate-construction work. It should include adaptive convex splines or sparse convex regression, richer polynomial bases, and a conventional cached continuation chosen with the same calibration protocol.

### B3. The equivalence margin is not economically disciplined

The 1/16 margin is fixed before evaluation, which is good. It is nevertheless very large relative to the observed differences and equals 80% of the maximum first-date investment charge. The paper explicitly concedes that application-specific economic importance requires external calibration.

As a result, “all policies are equivalent” is currently a statement about a permissive normalized numerical tolerance, not a substantive economic conclusion. An Econometrica contribution needs either a structural calibration that gives this margin economic meaning or a substantially tighter margin derived from the decision problem.

### B4. The statistical design establishes margin containment, not close economic equivalence

The paired intervals are about 0.0595 wide, while their midpoints are below 0.001 in absolute value. The intervals fit inside a 0.125-wide equivalence band, but they remain much too wide to resolve the actual observed differences. The result does not show that the policies are nearly identical at the scale suggested by their point estimates; it shows only that the present design rules out differences larger than the broad declared margin.

The next experiment should be designed backward from a target half-width, with a decomposition of sampling, numerical integration, terminal-control, acquisition and arithmetic components. The economic margin and the intended resolving power should be fixed together.

### B5. Complete work and amortization are not yet identified

The fitted-arm timing result is promising, but it comes from one x86-64 execution. The table excludes preparation, the approximately 90-second independent audit, diagnostic screening and two interrupted starts. Those exclusions are disclosed, but the paper has not yet produced a complete acquisition-and-reuse frontier.

The relevant object is a break-even curve over the number of future workloads, with per-model label cost, fitting cost, serialization, load, validation, drift checks, fallback, evaluation and shutdown. Timings need repetition, processor-frequency control or recording, and machine-independent operation counts. The audit campaign can be separated from per-deployment cost, but that separation should be an explicit economic choice rather than an omitted term.

### B6. The executed scope remains a two-date, two-state, scalar-control example

The horizon-uniform proposition is constructive and useful. It does not remove the curse of dimensionality: the state cover has size `(n_x+1)^d`, vector action coverage and innovation quadrature remain explicit, and exact-number bit lengths grow with the horizon. The sufficient resolutions are intentionally conservative and very large.

The paper therefore has a theorem showing finite fixed-accuracy construction at every finite horizon, not evidence of practical horizon or dimension scalability. The earlier adverse vector frontier remains the relevant executed evidence. A numerical-method paper at this venue needs at least one matched risk-sensitive vector or longer-horizon execution that tests the new construction rather than relying on operation notation alone.

### B7. The confirmatory status is weaker than the prose “frozen” may suggest

The source and actor hashes were written before the local evaluation, and the evaluator rejected changed sources. That is useful internal discipline. The freeze was not remotely timestamped or externally published before the primary local run. The post-evaluation joint-certificate re-accounting was then added on the same observations.

The manuscript discloses these facts, so I do not regard this as misconduct or a hidden protocol change. I do regard the current experiment as internally frozen but not independently preregistered. A new independent evaluation stream, committed before execution, should be used for any confirmatory claims about comparative performance.

### B8. Independent verification does not cover the full critical stack

The Fraction checker independently validates important kernels. It does not independently reproduce training, calibration selection, all 16,384 policy evaluations, the statistical inference formula, or the largest vector computation. Row hashes establish identity, not independent numerical agreement. The paired-inference replay shares the production interval formula.

Given the history of a substantive interval-accounting error in earlier revisions, the full endpoint chain deserves a second implementation: state acquisition, action selection, continuous-law integration, original-optimum witness, complete-policy upper evaluation, and simultaneous inference.

### B9. The formal release gate fails

The workflow run concludes with failure. The test ledger shows that all scientific and current suites pass except `tests_publication72`, where `test_every_prior_active_section_has_one_assignment` detects that `sections/core49.tex` has changed relative to a ledger that declares it unchanged. The actual and expected hashes differ.

The text change appears to be the intentional clarification separating the earlier expectation experiments from the new nested-AVaR experiment. The likely remedy is to update the preservation classification and source map, not to reverse the scientific clarification. But until the ledger, manuscript and release contract agree and a fresh workflow is green, the repository does not contain a final review-ready release.

### B10. The strongest certificate comparison is retrospective

The joint-support certificate qualifies every fitted-arm row, whereas the two global scalar accounts qualify none. This is an important deterministic observation. It was computed after primary evaluation and is not a prospective comparison of optimized certificate algorithms. The result therefore establishes that local information can tighten accounting on these fixed policies; it does not establish a prospective runtime or data-efficiency advantage of the joint method.

A new ablation should freeze the certificate builders, tuning rules and cost accounting before a new evaluation stream, then compare width, failures and complete work.

### B11. The cumulative manuscript remains too broad for its new evidence

The release contains a 56-page article, a 56-page technical supplement and a 178-page numerical/development appendix, in addition to the response. Preservation of the research history is valuable, but it is not the same as an Econometrica submission architecture.

The active numerical evidence now concerns one continuous investment model under nested AVaR. The main paper still carries a broad platform of historical constructions and applications. The resulting contribution is difficult to evaluate, and the reader must distinguish current evidence from preserved programmatic claims across nearly 300 pages.

### B12. Economic consequence remains absent

The new experiment proves that several qualified policies are equivalent at a broad normalized tolerance and that stored continuations reduce work on one synthetic workload. It does not change a substantive economic conclusion, recover a new comparative static, alter an estimated policy, or establish a calibrated welfare-computation frontier.

For a general numerical-method journal this may be sufficient when paired with the theory. For Econometrica, the paper needs a clearer economic reason why the certificate or storage architecture changes what economists can credibly compute or conclude.

## 5. Major required changes

### M1. Repair and rerun the complete release

Reclassify the intentional `core49.tex` amendment in the preservation map, regenerate the source identities, run every suite without skips, and publish a new immutable revision whose workflow conclusion and `RELEASE` gates are all successful. Do not overwrite the failed R95 evidence.

### M2. State one central contribution

Organize the paper around one theorem--algorithm--evidence chain: certified stored continuations for original-law dynamic decisions under recursive risk. Explain precisely which part is specifically neural, which part applies to any convex stored continuation, and which empirical result concerns storage rather than representation.

### M3. Run a budget-matched representation frontier

Match rank, labels, serialized size, fitting work and evaluation work. Include stronger adaptive non-neural approximators and a conventional cached-continuation baseline. Report Pareto frontiers for residual width, original-optimum certificate, policy cost and complete work.

### M4. Freeze a genuinely independent confirmation

Commit the protocol, source identities, models, selectors, margin, sample size and analysis code before opening a new evaluation stream. Retain all arms and all failures. Use that stream for the principal comparative claims.

### M5. Motivate and power the economic margin

Derive the margin from an economic loss, welfare, policy or adoption requirement. Choose the number of independent initial states and numerical precision to achieve a target simultaneous half-width materially smaller than that margin.

### M6. Report the complete acquisition-and-reuse frontier

For each representation, include label construction, fitting, validation, serialization, loading, identity checks, evaluation, fallback and shutdown. Show the break-even workload count and its uncertainty. Separate one-time independent audit cost from deployment cost explicitly.

### M7. Strengthen timing evidence

Use repeated fresh processes, record or control processor frequency, report uncertainty, and repeat on at least one materially different architecture. Prefer machine-independent primitive and interval-operation counts where timing differences are small.

### M8. Execute the risk-sensitive vector or longer-horizon method

Run at least one two-control/two-innovation comparison using the new nested-risk certificate, with matched stored and online continuations, direct policy costs, memory, operation counts and independent endpoint checks. Preserve adverse scaling.

### M9. Independently implement the full endpoint chain

A second implementation should reconstruct policy actions and cost enclosures from primitives, not merely verify model identities or reuse the production inference formula. Prespecified fixture containment is a good start; extend it to a statistically meaningful random audit and the critical large computation.

### M10. Make certificate construction a prospective algorithmic ablation

Compare global norm, signed scalar and joint local-support certificates on new fixed actors, with prespecified implementation choices. Charge support construction, state covering, risk witnesses, action minimization and all fallback work.

### M11. Supply an economically consequential application

Either calibrate the investment model and loss units or apply the method to a decision problem where certification changes an economic conclusion. Otherwise narrow the claim to a constructive numerical-certification result and target the venue accordingly.

### M12. Compress the submission

Keep the historical archive in the repository, but make the active journal submission self-contained and focused. A reasonable article would contain the core NBO construction, the recursive-risk qualification theorem, the continuous investment algorithm, one matched comparison and the essential proofs. The remainder can remain as archival companion material.

## 6. Technical and presentation comments

1. State in one place whether each theorem requires convexity of the true continuation, the fitted continuation, or both.
2. Give a machine-readable mapping from every constant in the continuous theorem to the production variable and test that uses it.
3. Report the frequency of rational terminal fallback, ambiguous acquisition branching and maximum bin refinement for every arm.
4. Add the raw paired means and numerical-width components to the main comparison table rather than requiring reconstruction from interval endpoints.
5. Explain why 32 nonlinear features and the 32-by-32 residual cover are appropriate numerical budgets, and show sensitivity to these choices.
6. Separate the discrete 20-bit initial-state target distribution from statements about the continuous state domain in the abstract and conclusion.
7. Report model-specific preparation and serialization cost; the aggregate 8.79-second preparation time cannot identify representation-level break-even.
8. Preserve the screening result as negative evidence. Do not use the number of excluded bins as a proxy for speed.
9. Distinguish a uniform whole-state residual certificate from the pointwise first-date original-optimum certificates on the evaluation states.
10. Report the exact source commit used by every generated table. The current branch includes bot-generated descendants of the workflow trigger, while the artifact is tied to the trigger commit.
11. Retain the explicit statement that the horizon theorem is not an executed scalability result.
12. Keep the qualification that the independent checker is kernel-level and that the inference replay is not an independently derived statistical implementation.

## 7. A focused publishable route

The strongest material could support a new paper with a title such as:

> **Certified Stored Continuations for Risk-Sensitive Bellman Decisions**

or, retaining the existing program identity,

> **Neural Bellman Operators: Original-Law Certification under Nested Risk**

The essential contribution would be:

1. the own-future feasible continuation construction;
2. the primitive continuous-law lower and upper certificate;
3. the centered recursive-risk comparison;
4. a representation-neutral certificate interface;
5. a budget-matched stored-continuation frontier;
6. a prospectively frozen work-loss and policy-cost experiment;
7. a calibrated economic margin;
8. a vector or longer-horizon execution; and
9. a fully green, independently checked release.

This route would preserve the substance of R95 without requiring the current experiment to establish a uniquely neural superiority result that it does not show.

## 8. Recommendation

R95 is rigorous, transparent and materially more convincing than its predecessors. Its continuous-law nested-risk construction, explicit all-action certificate, complete-policy accounting, stored-continuation work reduction and preservation of adverse evidence are genuine contributions. I encourage the author to develop this core.

For Econometrica, however, the present submission still lacks the required combination of method-specific identification, economically disciplined precision, practical scalability and release completeness. The main measured gain belongs to storage across all fitted representations; the policy experiment establishes only broad-margin equivalence; the execution remains two-date and two-dimensional; the independent implementation is partial; and the formal release gate fails.

I therefore recommend **rejection in the present form**, with encouragement to submit a substantially focused new paper after completing the comparative, economic and reproducibility program described above.
