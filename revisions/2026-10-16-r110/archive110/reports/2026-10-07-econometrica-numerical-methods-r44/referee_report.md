# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r44-review-ready-2026-10-07`  
**Pinned revision commit:** `e00d3d46484029738884119f18ce1e15fbdcc929`  
**Pinned revision tree:** `28d2c344da8875eefbf2e6e6f5d27c77c33ef999`  
**Pinned main manuscript:** `revisions/2026-10-07-r44/ECTA.tex`, Git blob `724c6e74f8a5b7500875f46b9982dc90b52166ad`  
**Pinned technical supplement:** `revisions/2026-10-07-r44/supp.tex`, Git blob `e3d5a6834897929e4646600261d8d5ef4c213db8`  
**Pinned response:** `revisions/2026-10-07-r44/response.md`, Git blob `5c31016c623e6d070b6db8546301c1eafe2918c7`  
**Publication workflow:** run `37605826115`, artifact `11475101500`  
**Publication artifact SHA-256:** `5e80020a7a737fcb970e5e2c05ef8c7ad8fd103b524b4cf2ebe6110df9dacff9`  
**Report date:** 7 October 2026  
**Recommendation:** **Reject in the present form and do not continue this cumulative manuscript through another ordinary revision round. A new, sharply focused paper on from-primitives neural policy construction and direct all-state certification in compact nonlinear control could merit evaluation, but R44 does not establish an Econometrica-level method-specific contribution for the broad Neural Bellman Operators program.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R44 is a substantial and careful response to the R42 report. The threshold publication problem is resolved. The current branch contains one authoritative article, a new proof supplement, a point-by-point response, generated tables, materialized evidence, release and preservation audits, and compiled documents. The article is concise relative to earlier versions and presents the new argument in a coherent order. The repository retains unfavorable historical comparisons rather than replacing them with a selectively favorable record.

The revision also adds two useful mathematical and computational ideas.

First, the retained-policy corollary distinguishes a failure to certify from a failure of the policy itself. If the continuation and deployed actor remain fixed, a finer valid residual enclosure can sharpen the same policy's loss bound while retaining the original actor allowance and terminal account. The implementation applies this logic to seven policies that missed the tighter target in the original capped R42 services. All seven cross the target without changing a network weight or a deployed action.

Second, the paper now compares neural and ridge policies through a direct policy-cost estimand rather than by subtracting separate regret bounds. A Bellman telescoping score has expectation equal to the fixed policy's cost under conditional expectation. Signed residual enclosures yield a deterministic support interval, and common-innovation interval simulation plus simultaneous empirical-Bernstein bounds produce twenty-four neural-minus-ridge policy-cost intervals for the declared states. This closes a genuine estimand gap in R42.

I checked the centered policy theorem, its date-shift invariance, the retained-policy logic, and the paired telescoping identity in finite exact examples. I also audited the deposited records and source identities, ran the revision's fourteen tests, reconstructed the reported comparison arithmetic, and independently reproduced one scalar recertification record byte for byte. I found no immediate algebraic contradiction in the new theorem chain under its stated assumptions.

The remaining difficulty is substantive. R44 demonstrates that a fixed learned policy can sometimes be certified more sharply and that a direct comparison can remain unresolved even when separate certificates differ. It still does not show that NBO is a better way to construct a policy, a more reliable way to reach a requested accuracy, or a more efficient way to obtain a certified economic answer than the strong conventional methods in the same study.

The original capped-service estimand remains unfavorable at the tighter targets: scalar neural succeeds in six of twelve services at `0.04` while spline succeeds in all twelve; coupled neural succeeds in five of six at `0.10` while ridge succeeds in all six. The seven post-review recertifications are selected precisely from those observed failures and extend verification only. They do not alter the original algorithm's success array, training work, policy cost, or optimizer reliability. The extension is also computationally substantial: the six scalar diagnostics add 302,358,600 Bellman-transition evaluations in total, and the coupled diagnostic records 2,054,388,096 neural-neuron expectations on 66,049 states.

The direct paired comparison is scientifically welcome, but all twenty-four intervals contain zero. The intervals have widths of approximately `1.95e-4` to `2.70e-4`; no superiority, noninferiority, or equivalence margin was specified for this coupled comparison. The data therefore do not identify the sign of the neural-minus-ridge policy-cost difference. The conventional evidence remains strong: the matched spline certificate is tighter in all twelve scalar services and the signed scalar policy-cost evidence frequently favors spline; ridge reaches the coupled targets more reliably, reaches `0.25` faster in all six original services, and has the tighter final all-state gap in four of six.

The strongest successful contribution of R44 is therefore a **method-neutral policy-certification and direct-comparison framework applied to a finite catalogue of learned and conventional candidates**. That contribution may be publishable in a focused computational-methods paper. It is not yet evidence for the broad numerical superiority, necessity, or economic indispensability of Neural Bellman Operators.

I consequently recommend rejection of the present cumulative submission. A new paper could be seriously considered if it centers the direct certification contribution, defines a method-level training estimand, supplies matched end-to-end work-to-accuracy comparisons, and demonstrates the construction in a nonlinear problem where learned continuation structure materially changes the feasible economic analysis.

## 2. What R44 successfully repairs

### 2.1 The submitted object is complete and immutable

R42 consisted of source, protocol, and workflow evidence without an integrated manuscript. R44 contains a 22-page main article, a 10-page active supplement, and an 8-page response, all tied to one review-ready commit. The release audit records no undefined references, duplicate labels, or overfull boxes in the active documents. The current root entry point identifies R44 rather than an older paper.

This is now a reviewable submission rather than a detached science addendum.

### 2.2 The paper states the original capped-service outcome honestly

The article retains the original R42 attainment array:

- scalar neural: `12/12` at `0.06`, `6/12` at `0.04`;
- scalar spline: `12/12` at both targets;
- coupled neural: `6/6` at `0.25`, `5/6` at `0.10`;
- coupled ridge: `6/6` at both targets.

The seven later recertifications are explicitly labeled post-review diagnostics. None of the original failures is reclassified. This distinction is exactly right.

### 2.3 Retained-policy recertification is a useful conceptual clarification

The corollary fixes the continuation, deployed policy, actor allowance, and terminal enclosure, and changes only the valid residual enclosure. This prevents a finer actor proposed internally by the verifier from being substituted silently for the deployed policy. The implementation hash-checks the old network and actor and discards fine-grid action proposals while charging their work and transient storage.

The result is useful beyond neural methods: a coarse verifier can fail even when a fixed policy admits a sharper certificate. R44 makes that distinction operational.

### 2.4 The direct policy-cost estimand is now the correct one

R42 compared separate all-state gaps but did not directly identify neural-minus-ridge policy cost. R44 supplies an own-policy telescoping score whose expectation is the actual fixed-policy cost. The score is not a subtraction of two upper bounds. Coupling is permitted as long as each marginal innovation law is preserved.

The paper also correctly reports every interval crossing zero as unresolved. It does not rename lack of significance as equivalence.

### 2.5 Numerical and statistical allowances are separated

The within-bin innovation uncertainty, state propagation, nearest-node ambiguity, deterministic support, finite-sample uncertainty, and outward arithmetic are separately represented. The recorded paired simulations contain zero unresolved actor-selection ambiguities. The paper states that a fixed pseudorandom stream provides reproducibility, not a proof of independence.

### 2.6 Adverse method comparisons remain visible

The active article preserves all of the following:

- scalar spline certificates are tighter in every matched service;
- identified scalar policy-cost signs favor spline and never favor neural;
- ridge reaches the coupled targets more reliably and is often faster;
- all twenty-four new neural-minus-ridge intervals are unresolved;
- adaptive precision is slower in twenty-six of thirty-six matched records and about `0.98%` slower in aggregate than fixed binary64;
- no nonlinear scaling frontier or stable neural timing advantage has been established.

This is exemplary disclosure.

### 2.7 Provenance and auditability are unusually strong

The publication materializes the original 150 R42 records, verifies all five original science-source hashes, binds the new diagnostic sources and results, and preserves the first failed R42 run. The release includes machine-readable summaries, tests, record hashes, build instructions, and preservation maps. This evidentiary standard is a major strength of the project.

## 3. Blocking concerns

### B1. The positive theorem chain is method-neutral and does not isolate the value of NBO

The centered Bellman certificate accepts any fitted continuation and feasible policy satisfying the stated residual and actor enclosures. The retained-policy corollary applies to any fixed candidate. The paired telescoping score likewise applies to any two fixed policies under expectation.

These are useful results, but their validity does not establish that neural continuation learning is necessary, more accurate, more reliable, or cheaper. Indeed, the strongest numerical consequences in R44 are about verification of frozen objects and direct comparison of fixed policies. The same machinery can certify spline, ridge, projection, or hand-designed policies.

For an Econometrica numerical-method paper organized around Neural Bellman Operators, the distinctive learned component must produce a capability or work-to-accuracy advantage that the method-neutral verifier alone does not supply. R44 does not establish that increment.

### B2. Postselected recertification does not improve the original training-to-certificate method's reliability

The R44 diagnostics select exactly the seven neural objects that had already failed the tighter R42 targets. The networks and actors are frozen. Only the verification mesh is extended. This is a legitimate diagnostic of those seven policies, but it is not a prospective performance result for the original capped service.

The relevant method-level facts remain:

- scalar neural succeeds at `0.04` in `6/12` original services;
- coupled neural succeeds at `0.10` in `5/6` original services;
- spline and ridge succeed in all corresponding services.

The recertification shows that the original failure indicator confounded policy quality with verifier resolution. It does not show that the original algorithm would return a certificate at the tighter target within its declared cap, nor that a new prospective rule would do so reliably. A publishable construction claim needs a prospectively specified verification ladder and a new full-catalogue execution under that ladder.

### B3. The verification-only improvement is computationally large and is not compared on a common frontier

The finer certificate is not costless:

- each of six scalar recertifications evaluates 50,393,100 additional Bellman transitions, for 302,358,600 total;
- the coupled recertification uses 66,049 state nodes, 528,392 transient action scalars, and 2,054,388,096 neural-neuron expectations;
- the coupled actor retained in deployment already stores 133,128 scalar actions.

These counts are valuable, but the design refines only the selected neural failures. It does not apply the same additional verification budget to spline and ridge, does not construct a complete prospective certificate frontier for every method, and does not supply comparable isolated clocks on one environment. The result therefore cannot support an efficiency claim or a statement that neural policies obtain tighter certification per unit of work.

A fair design would run the full verification ladder for every candidate generator and stop each method at the first common target, charging all failed refinements and storage.

### B4. The twenty-four direct intervals do not identify comparative policy value

All twenty-four neural-minus-ridge confidence intervals include zero. Their widths range from approximately `0.00019469` to `0.00026982`; the smallest symmetric margin containing every reported interval is approximately `0.00013959`.

These intervals are substantially more informative than separate regret bounds, but they establish neither superiority nor equivalence. No economically justified noninferiority or equivalence margin was fixed for the coupled comparison. Four initial states and six frozen policy pairs also do not provide an all-state ranking or a method-level distribution over trained policies.

If practical equivalence is the intended conclusion, the paper must define the economic margin before examining the comparison and design sample size and state coverage around it. If superiority is the intended conclusion, the current evidence is simply unresolved.

### B5. Strong conventional methods remain at least as compelling on every completed experiment

The scalar evidence favors the conventional construction:

- the spline all-state certificate is tighter in all twelve matched services;
- at the first common `0.06` crossing, 29 of 48 neural-minus-spline intervals certify higher neural cost, none certify lower neural cost, and 19 overlap zero;
- at `0.04`, 17 of 24 certify higher neural cost, none certify lower neural cost, and seven overlap zero.

The coupled evidence is also unfavorable or unresolved:

- ridge reaches `0.10` in all six original services; neural reaches it in five;
- ridge reaches `0.25` faster in all six original observations;
- ridge has the tighter final all-state gap in four of six pairs;
- the new direct policy-cost intervals do not identify a neural advantage.

A numerical method need not dominate every baseline. But a top-journal paper must identify what the proposed method delivers that the strongest comparator does not. R44 does not yet identify such a capability.

### B6. There is still no matched end-to-end work-to-certified-accuracy comparison

R42 substantially improved the service boundary by including own-future target generation, fitting, failed refinements, policy extraction, verification, and durable output. R44's new diagnostic clocks, however, are explicitly local, concurrently scheduled, and not comparable across hosts or methods. They cannot be added to historical clocks to reconstruct a new end-to-end service.

The original nonlinear timings are singleton observations. The conventional methods frequently reach the targets faster, and the paper has not supplied repeated isolated executions, a common hardware protocol, or machine-independent total-operation counts covering training, verification, policy storage, and independent economic comparison.

The absence of a stable work advantage is not merely a missing robustness check. It is central to a numerical-method contribution.

### B7. The nonlinear evidence remains one- and two-dimensional and tensor-cover dependent

The fresh nonlinear construction is executed only in:

- a scalar state/action economy; and
- a two-state, two-control, four-date economy.

The finer coupled diagnostic uses 66,049 states and a large tabulated actor. The dimension-explicit theorem honestly exposes state, action, innovation, and query factors, but it is not an executed scaling result. The quadratic matrix-factor and precision experiments concern different structured algorithms and cannot substitute for nonlinear NBO scaling evidence.

No adaptive sparse-grid, adaptive partition, fitted-value iteration, or approximate policy-iteration comparator has been executed on the same nonlinear problem. Without such evidence, the paper does not establish that the proposed verification architecture remains useful beyond small tensor-cover laboratories.

### B8. Nonlinear optimizer reliability remains undefined

The complete catalogue contains three fixed neural seed labels per economic cell. The paper correctly treats the catalogue fraction as a finite-array estimand rather than a success probability. But then it cannot support claims about the reliability of neural training under new initializations, architectures, or economic tasks.

There is neither:

- a deterministic nonlinear training theorem;
- a prespecified probability law over training randomness with repeated independent draws;
- a lower confidence bound on target-attainment probability; nor
- a worst-case guarantee over a declared initialization class.

The recertification diagnostic reduces uncertainty about seven frozen policies. It does not supply any of these method-level reliability objects.

### B9. Adaptive precision remains an adverse result, not a numerical contribution

Fixed binary64 and adaptive precision each certify all thirty-six services and execute 474 accepted updates. Adaptive additionally rejects 126 binary32 proposals. It is slower in 26 of 36 matched records and approximately `0.976%` slower in aggregate.

The paper now interprets this correctly. Nevertheless, the precision program remains prominent in the retained NBO narrative without an empirical work benefit. A future paper should either demonstrate a setting in which mixed precision reduces complete certified work or move this result to a negative diagnostic rather than present it as a principal numerical advance.

### B10. The economic result and retained platform scope remain disproportionate to the completed method evidence

The nonlinear investment economies are transparent theoretical laboratories, not calibrated quantitative exercises. The main economic conclusion—that reoptimization can improve on retaining an old policy after a large investment-price change—is available from the spline and ridge constructions at least as sharply as from the neural policies.

The active article also retains controlled diffusions, recursive utility, endogenous preferences, temporal selves, and games as part of the paper's program. Those applications do not receive the new from-primitives nonlinear training study, retained-policy diagnostic, or direct method comparison. Linked historical companions preserve important material, but preservation is not evidence that one numerical contribution has been established across the entire platform.

For Econometrica, the paper should either unlock a substantive economic result unavailable to strong conventional computation, or establish a general and competitive numerical method across a carefully controlled benchmark class. R44 does neither.

## 4. Major comments and required changes

### M1. Choose one central paper

The strongest coherent paper in R44 is about direct all-state certification and comparison of frozen learned policies. Center the title, abstract, and contribution list on that object. Neural candidate generation can be one important application of a method-neutral verifier rather than the unsupported universal protagonist.

Alternatively, retain NBO as the center only after demonstrating a problem in which its learned continuation materially improves attainable accuracy, economic scope, or complete certified work.

### M2. Prespecify a complete training-and-verification service

Before a new execution, fix the full ladder of training budgets and verification resolutions. Apply it to every method, not only observed neural failures. The service should stop at the first certificate below each target and retain every failed attempt. Post hoc verifier refinement should remain a separate diagnostic.

### M3. Define a method-level reliability estimand

Choose one of the following and design the study around it:

- probability of attaining a certificate under a specified training-randomness law;
- expected or median complete work to target;
- worst-case performance over a declared finite initialization class; or
- deterministic termination under stated nonlinear conditions.

A finite catalogue fraction is useful, but it must not stand in for these different objects.

### M4. Compare verification frontiers, not isolated final certificates

For neural, spline, ridge, and any additional baseline, report certificate width against:

- state and action cells;
- Bellman-transition or neuron-expectation counts;
- transient and deployed policy storage;
- verification memory;
- wall time under one controlled environment; and
- total work from primitives.

This would reveal whether learned smoothness or representation produces a verification advantage rather than merely a valid certificate.

### M5. Design the direct comparison around an economic decision margin

Specify the initial-state distribution or state family and an economically meaningful superiority, noninferiority, or equivalence margin before simulation. Determine the number of paths from that margin. Report direct intervals for all candidate pairs under the same familywise error account.

Four hand-selected states are a useful diagnostic but not a broad comparative conclusion.

### M6. Execute a genuinely multidimensional nonlinear benchmark

A credible benchmark should include coupled nonlinear dynamics, continuous uncertainty, and nontrivial actions in dimensions where tensor grids are no longer the default solution. Include strong sparse-grid, projection, fitted-value, approximate-policy-iteration, and simulation-based baselines where applicable.

The benchmark should expose what learned continuation structure buys in certification or repeated economic queries.

### M7. Report stable complete-work measurements

Use repeated isolated process executions, fixed warm-up and CPU rules, and medians with dispersion. Report machine-independent counts alongside clocks. Include label or target generation, fitting, all failed refinements, policy extraction, verification, independent comparison, serialization, and peak storage.

### M8. Keep expectation-specific and recursive results visibly separate

The paired telescoping score uses conditional expectation. It is not automatically a direct comparison theorem for nonlinear certainty equivalents, recursive utility, or games. The paper says this, but the organization should make the scope difference impossible to miss. Each broader application requires its own direct estimand and comparison theorem.

### M9. Make the active submission self-contained

The 22-page article is more readable, but it repeatedly relies on an unchanged R41 article, a historical supplement, and an applications companion. A final submission should contain one authoritative source tree, one notation system, and one clear boundary between active results and archive material. Preservation can remain in the repository without making historical companions part of the current argumentative burden.

### M10. Develop one substantive economic application

Use the certified method to answer an economic question whose conclusion, feasible model, or uncertainty account changes materially because of the method. The current price-change laboratory is useful for testing the numerical pipeline but does not yet provide Econometrica-scale economic content.

## 5. A focused publishable route

A credible new submission could be organized around the following narrower contribution.

### 5.1 Core theorem

A method-neutral theorem converts uniform own-future Bellman and actor enclosures into an all-adapted-policy loss bound. A retained-policy result distinguishes candidate quality from verification resolution. A direct telescoping score supplies fixed-policy cost differences with deterministic numerical support and simultaneous finite-sample coverage.

### 5.2 Prospective algorithm

Specify a complete from-primitives training-and-verification service, including its prospective resolution ladder, stopping rule, failure output, and complete work boundary. Apply the identical design to neural and strong conventional generators.

### 5.3 Comparative study

Use a multidimensional nonlinear economy for which no exact structural solution is available. Define an economically meaningful target and state distribution. Report target-attainment probability or deterministic coverage, complete work-to-target, storage, and direct policy-cost differences.

### 5.4 Economic result

Show that the certified policy supports a substantive comparative static, welfare statement, or robust decision that cannot be obtained equally sharply and cheaply from the strongest conventional alternative.

Such a paper could make a valuable contribution to reliable computational economics without requiring a claim that neural methods dominate universally.

## 6. Independent verification performed for this report

I performed the following checks against the pinned R44 snapshot and its source-bound publication artifact.

1. **Snapshot and artifact identity.** I fixed the review at commit `e00d3d46484029738884119f18ce1e15fbdcc929` and tree `28d2c344da8875eefbf2e6e6f5d27c77c33ef999`. The downloaded publication artifact has SHA-256 `5e80020a7a737fcb970e5e2c05ef8c7ad8fd103b524b4cf2ebe6110df9dacff9`, matching the GitHub artifact digest.
2. **Source identities.** The Git blob identities of the main article, supplement, and response match the pinned revision. The materialized R42 audit verifies all 150 original records and all five frozen science-source hashes.
3. **Repository tests.** The fourteen R44 tests pass. They cover record hashes and counts, retained-policy invariance, paired confidence reconstruction, exact finite-state policy bounds, date-shift invariance, exact paired telescoping, actor-boundary handling, innovation-bin identities, and supporting arithmetic.
4. **Mathematical spot checks.** I constructed a finite three-date control problem and checked the centered certificate and its shift-width invariance exactly. I separately enumerated a paired finite policy problem and verified that the telescoping score's mean equals the actual policy-cost difference.
5. **Recertification audit.** All seven records retain the original network and actor identities and attain their stated tighter target. Bound reductions range from approximately `24.85%` to `35.79%`. The deposited work accounts sum to 302,358,600 additional scalar Bellman-transition evaluations and 2,054,388,096 coupled neural-neuron expectations. I independently reran scalar service 041's recertification and obtained a byte-identical result record.
6. **Direct comparison audit.** I checked all twenty-four paired records, reconstructed their confidence intervals from the stored endpoint statistics and deterministic support, and confirmed that every interval contains zero. Interval widths range from `0.00019468885525231503` to `0.0002698183813589405`; no actor-selection ambiguity is recorded.
7. **Precision audit.** The deposited counts reproduce fixed32 `6/36`, fixed64 `36/36`, adaptive `36/36`, 126 rejected binary32 proposals, adaptive slower in 26 pairs and faster in 10, and aggregate adaptive time approximately `0.976%` above fixed64.
8. **Compilation.** The published release audit records clean 22-, 10-, and 8-page main, supplement, and response documents. I also rebuilt the active documents locally after restoring the source-bound class and bibliography inputs. The local build completed without undefined references, duplicate labels, or overfull boxes; PDF byte hashes are environment-dependent and were not treated as an exact binary replay.
9. **Limitations.** I did not rerun the full nonlinear training catalogue or all twenty-four paired simulations. New executions would create new optimization and timing observations. The independent audit verifies the frozen records, formulas, identities, and aggregate claims rather than reproducing every historical clock.

The review directory contains the audit script, its actual machine-readable output, and a manifest fixing the reviewed scope.

## 7. Recommendation

R44 is the most coherent and scientifically candid version of the project. It resolves the manuscript-materialization problem, adds a valid retained-policy distinction, constructs the right direct policy-cost estimand, and preserves all adverse evidence. The new theorem chain appears internally coherent under its stated assumptions, and the repository's audit standard is exceptional.

Nevertheless, the revision does not meet the standard for an Econometrica numerical-methods contribution. The successful mathematics is method-neutral; the neural-specific training service remains less reliable at the tighter original targets; postselected recertification requires substantial verification work and does not alter that reliability; all direct neural-minus-ridge intervals are unresolved; strong conventional methods remain sharper or faster on the completed experiments; nonlinear scaling and stable complete-work comparisons are absent; and the broad economic platform is not supported by a correspondingly broad executed method result.

I therefore recommend **rejection in the present form and no further ordinary revision of this cumulative submission**. A new, focused paper on from-primitives learned-policy construction, all-state certification, and direct economic comparison could merit serious evaluation if it supplies a prospective method-level design, contribution-isolating baselines, multidimensional nonlinear evidence, and a substantive economic application.
