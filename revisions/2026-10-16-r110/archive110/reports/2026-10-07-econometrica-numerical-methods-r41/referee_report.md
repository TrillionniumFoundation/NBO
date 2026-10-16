# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r41-review-ready-2026-10-07`  
**Pinned revision commit:** `06a104a8db06b76464165899d817b303cb2aaa01`  
**Pinned revision tree:** `783b70a4ea1ead950d7ea04aeebccc27a7510bf4`  
**Pinned main manuscript:** `revisions/2026-10-07-r41/ECTA.tex`, Git blob `07e8100e1a97d1b2b1aae7e47d0be3b1906e8f6d`  
**Pinned technical supplement:** `revisions/2026-10-07-r41/supp.tex`, Git blob `ac5fc091749f32c31a6aec891943f29b591d687f`  
**Pinned response:** `revisions/2026-10-07-r41/response.md`, Git blob `25b4f5c41023a17dbcafe22448ce7cfabcdbb903`  
**Pinned applications companion:** `revisions/2026-10-07-r41/applications.tex`, Git blob `311fde2ab16eb51fc70f8c90bdd412704060f71b`  
**Report date:** 7 October 2026  
**Recommendation:** **Reject in the present form and do not continue this cumulative manuscript through another ordinary revision round. A new, sharply focused paper on direct post-training neural Bellman certification for compact nonlinear control could merit evaluation, but the current evidence does not establish a method-specific Econometrica-level contribution for the broad NBO program.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R41 is a substantial and technically serious response to the R39 report. It addresses the two clearest defects in the preceding revision rather than merely rewriting the claims. First, the stored current network is now checked against a Bellman operator containing the stored future network itself. The direct certificate is executable with the conventional spline evaluator disabled. Second, the new precision catalogue actually exercises the adaptive branch: binary32 proposals are rejected, binary64 proposals are accepted, and ten of the twelve adaptive services mix the two precisions. The revision also supplies a nonzero numerical-execution allowance, sharpens the displayed-state policy bounds below 0.02, adds contemporaneous neural-versus-spline value comparisons, preserves the failed R40 execution, and materializes one source-bound publication with clean active documents.

I independently checked the R41 publication ledger, all 278 publication-file hashes, the pinned source blobs, all twelve neural-refinement records, all four direct-comparison records, and all forty-eight precision records. I also recomputed the principal direct-policy and precision comparisons from the deposited records. I found no immediate algebraic contradiction in the direct neural residual argument or in its use of monotonicity, cash invariance, state and action covers, terminal error, and own-future continuation. R41 therefore clears an important threshold: the nonlinear neural continuation is no longer merely a proposal judged by a spline Bellman residual.

The central difficulty is now empirical and identificational rather than formal. The new direct certificate establishes that four already-trained networks, together with newly selected tabulated policies, satisfy conservative policy-loss bounds in four scalar finite-horizon economies. It does not establish a constructive or reliable nonlinear neural training method. There are no new training runs. The four certified networks were historically trained on deterministic spline labels, and the current theorem begins after those trained objects exist. This is a valuable post-training verification result, but it is not yet a numerical method for obtaining a certified neural continuation with controlled work or success probability.

The contemporaneous conventional comparator remains stronger on the recorded economic objects. Fourteen of the sixteen neural-minus-reoptimized-spline cost intervals have strictly positive lower endpoints, none has a strictly negative upper endpoint, and two overlap zero. Thus the neural policy has higher cost in fourteen displayed state--economy cells and is never certified to have lower cost. The spline also has the tighter global policy certificate in all four economies. An independent calculation from the deposited spline lower Bellman function and policy-value intervals shows that its displayed-state gap bound is tighter in all four economies as well. Neural global gap bounds are about 1.44--1.47 times the spline bounds, and neural displayed-state bounds are about 1.74--1.84 times the spline bounds.

The precision mechanism is now activated, but the complete-work evidence is again unfavorable. Adaptive and fixed64 execute exactly the same total number of accepted updates, 158. Adaptive additionally incurs forty-two rejected binary32 proposals. In every one of the twelve matched objects, the single recorded adaptive clock exceeds the fixed64 clock. The adaptive/fixed64 time ratio ranges from about 1.002 to 1.096, with a median near 1.019; aggregate recorded adaptive time is about 2.64 percent higher. These are single-run descriptive clocks, not stable performance estimates, but they provide no evidence of an adaptive work advantage.

The new nonlinear result also remains a scalar, four-date, three-shock, grid-first construction. The multidimensional continuous-innovation extension is mathematically explicit and commendably states its cover counts and policy-query costs, but it is not an executed nonlinear scaling result. The direct neural verification clock excludes historical label construction and network training, while the conventional clock is reported for construction and query at the final resolution. There is therefore no matched from-scratch work-to-certified-accuracy frontier.

The revision has consequently produced a credible direct verifier for frozen neural continuations and an honest precision-pressure catalogue. It has not shown that NBO is a competitive way to construct the continuation, that adaptive precision reduces complete work, or that the neural method unlocks an economic result unavailable more sharply and cheaply from the conventional dynamic-programming construction. The broad 68-page article, 45-page supplement, and 48-page applications companion remain disproportionate to this narrower successful result.

I recommend rejection in the present form. I would take seriously a new paper centered on direct post-training neural Bellman certification, provided it clearly separates verification from training, supplies a genuinely nonlinear multidimensional benchmark and a matched complete-work design, and either demonstrates a neural capability not delivered by conventional methods or deliberately presents a method-neutral verification contribution.

## 2. What R41 successfully repairs

The negative recommendation should not obscure genuine progress.

### 2.1 The trained continuation is now the certified Bellman object

R39 certified actions proposed by a neural continuation against spline-based Bellman brackets. R41 instead evaluates each stored current network against the Bellman operator using its own stored future network. The residual endpoints include current- and future-network arithmetic, state coverage, continuous-action coverage, and terminal-network discrepancy. The policy is newly selected from the resulting neural Q intervals and evaluated independently on its own future shock tree.

The deposited test suite disables the conventional spline evaluator and still executes the direct certificate. This closes the most important conceptual gap in R39. The result is no longer merely “a neural proposal with a spline verifier.”

### 2.2 The policy theorem has the correct comparison class in the declared economy

Within the compact scalar nonlinear model, the certificate compares the returned policy with all adapted feasible policies, not only neural policies or actions on the stored mesh. State and action covers are paid explicitly. Terminal discrepancy and selected-action allowance remain separate. The proof does not presume that the optimizer used to train the network converged.

### 2.3 The precision branch is genuinely exercised

The pressure catalogue contains dimensions two and eight, two conditioning regimes, and three economic targets. Fixed32 passes only two of twelve objects. Adaptive accepts 116 binary32 and 42 binary64 proposals, rejects 42 binary32 proposals, and mixes precisions in ten services. Failed proposals are retained and charged. This is a material improvement over R39, where the “adaptive” method never left binary32.

### 2.4 Numerical execution receives a nonzero account

For the nonlinear program, R41 provides rational range-and-error propagation through the specified separate-operation binary32 graph. It includes state acquisition, transition, stage cost, terminal cost, clipping, and nearest-node policy selection. The additional global allowance is about `1e-5`, not zero. The manuscript correctly distinguishes the exact economic model from the numerically perturbed transition-and-accounting model.

### 2.5 The economic gain now exceeds the displayed-state neural regret bound

At the eight changed-price state--risk pairs, the verified gain from reoptimization over retaining the old price-one rule has a positive lower endpoint above the displayed-state neural regret allowance. This repairs the previous mismatch in which the policy-loss bound could exceed the economic gain being interpreted.

### 2.6 A contemporaneously reoptimized conventional policy is reported

The old-rule comparison is no longer the only contrast. The revision constructs and evaluates a new spline policy at the changed price. It explicitly states that the resulting neural policy is close at the displayed states, not superior, and that the `0.001` margin is descriptive and post hoc rather than a preregistered equivalence threshold.

### 2.7 Provenance and failure preservation remain unusually strong

R41 preserves the failed R40 artifact, identifies the JSON restoration bug, reruns the complete catalogue in a fresh directory, retains inherited clocks, and records source and result hashes. The active article, supplement, applications companion, and response compile without undefined references, duplicate labels, missing characters, or overfull boxes.

## 3. Blocking concerns

### B1. R41 verifies four frozen neural continuations; it does not establish a constructive nonlinear neural method

The direct theorem starts from stored networks. It provides a post-training implication:

1. compile or enclose the stored current and future networks;
2. bound their Bellman residual globally;
3. select a feasible action from neural Q intervals;
4. evaluate the returned policy; and
5. convert the resulting residual and actor allowances into a policy bound.

This is valuable. But no theorem or experiment in R41 explains how the nonlinear networks are obtained at the required accuracy from economic primitives. The study reports `new_neural_training_runs: 0`. The four canonical networks were inherited from R39 and were trained on the conventional spline's deterministic nodal values. R41 therefore certifies four fixed objects; it does not establish a success probability, deterministic training cap, or work guarantee for producing such objects.

The historical exact-ReLU spline fallback further clarifies the distinction. Termination of the finite construction is guaranteed by a conventional spline that can be represented as a ReLU network, not by convergence of the trained width-31 network. A relabeled spline is not evidence for neural training.

For an NBO numerical-method contribution, the missing object is a complete training-to-certificate procedure for the nonlinear network. At minimum, the paper needs a prespecified training distribution or deterministic construction, failure accounting, multiple independent training objects, and a statement of what is guaranteed when training does not reach the residual floor required by the verifier.

### B2. The contemporaneous spline policy is better on the deposited economic evidence

The direct comparison is unambiguous if costs are the objective:

- 14 of 16 neural-minus-spline intervals have a strictly positive lower endpoint;
- 0 have a strictly negative upper endpoint; and
- 2 overlap zero.

Thus the neural policy is certified to have higher cost in fourteen displayed cells and is never certified to have lower cost. The fact that all intervals lie inside a post-hoc `±0.001` margin does not establish equivalence.

The certificate sharpness points in the same direction. The spline global gap bounds are approximately `0.02947`, `0.02957`, `0.03157`, and `0.03168`, whereas the neural bounds are approximately `0.04309`, `0.04333`, `0.04547`, and `0.04581`. Neural bounds are 1.44--1.47 times larger.

At the four declared states, the spline's own lower Bellman function and outward policy-value upper intervals imply maximum gap bounds of approximately `0.00888`, `0.00891`, `0.00987`, and `0.01021`. The corresponding neural bounds are approximately `0.01628`, `0.01640`, `0.01783`, and `0.01778`, or 1.74--1.84 times larger.

A numerical method need not dominate every conventional comparator. But when the conventional construction is better on policy cost and certificate sharpness in the complete executed nonlinear study, the paper must identify another capability uniquely delivered by the neural method. R41 does not yet do so.

### B3. There is no matched end-to-end work-to-certified-accuracy comparison

The new neural clock is explicitly scoped to post-training verification, policy construction, and independent queries. Historical label construction and network training remain outside it. The conventional clock covers construction and query at the final accepted resolution. The two clocks therefore do not measure the same service from raw economic primitives to a certified policy.

Even within this partial comparison, the sum of the three retained neural verification refinements is not lower than the reported final-resolution spline construction-and-query clock:

| Economy | Neural verification, all refinements | Spline final construction and query |
|---|---:|---:|
| Price 1, risk 0 | 8.978 s | 8.544 s |
| Price 1, risk 1 | 32.091 s | 26.392 s |
| Price 4, risk 0 | 8.464 s | 8.162 s |
| Price 4, risk 1 | 31.319 s | 26.058 s |

These are single recorded executions and should not be overinterpreted. They nevertheless provide no neural work advantage before adding the omitted label-construction and training costs.

A publishable method comparison should start from the same primitives, include all training labels, fitting, failed refinements, policy construction, verification, and durable output, and stop at the first common certified target. The conventional method must be allowed its own adaptive refinement. Repeated isolated timings and machine-independent operation counts should accompany the clocks.

### B4. Precision adaptation is active but does not reduce recorded complete work

Adaptive precision and fixed64 each execute 158 accepted factor updates across the twelve matched objects. Adaptive additionally pays for forty-two rejected binary32 proposals. In every matched object, the single recorded adaptive service time exceeds fixed64:

- adaptive/fixed64 ratio range: approximately `1.0019`--`1.0963`;
- median ratio: approximately `1.0193`;
- aggregate adaptive time: approximately `5.9452` seconds;
- aggregate fixed64 time: approximately `5.7922` seconds.

This is not statistical evidence that adaptive precision is universally slower. It is direct evidence that the deposited mechanism catalogue does not demonstrate a work advantage. The adaptive branch is correctly exercised, but activation is not the same as efficiency.

The next design should include repeated timings, precision-dependent operation counts, a target sweep, and cases where mixed precision saves enough low-precision work to offset rejected attempts and control overhead. The comparison should be against an implementable fixed-precision policy, not an oracle selected after observing the result.

### B5. The executed nonlinear problem remains scalar and grid-first

The four nonlinear economies have:

- one state variable;
- one constrained action;
- three shock outcomes;
- four decision dates; and
- tensor state/action covers with up to 2,048 state cells and 1,024 action cells.

The newly trained object is not exercised in a multidimensional nonlinear economy. The supplement extends the theorem to compact multidimensional states and actions and quantized continuous innovations, but its explicit counts retain tensor-cover dependence, and its separate policy-query tree can grow exponentially with horizon and innovation support. This is an honest theorem, not a scaling result.

The dimensions two through eight in the precision catalogue concern quadratic matrix-factor services, not the direct nonlinear neural certificate. They cannot be used as evidence that the nonlinear NBO construction scales.

A serious next benchmark needs coupled multidimensional nonlinear dynamics, continuous or high-support uncertainty, a nontrivial action set, and strong sparse-grid, projection, fitted-value, or approximate-policy-iteration baselines. It must report complete verified work rather than only a theorem with dimension-explicit cover counts.

### B6. The economic result remains method-neutral

R41 validly shows that reoptimization after a fourfold increase in investment cost improves on retaining the old price-one rule. It also shows that the displayed-state neural regret allowance is smaller than that verified gain. This is a genuine economic accounting statement.

But the contemporaneously reoptimized spline policy delivers the same substantive conclusion, has lower recorded cost in fourteen of sixteen direct comparisons, and has tighter policy certificates. The economic result is therefore “reoptimization matters under a large price change,” not “NBO reveals an economic conclusion unavailable to conventional methods.”

For Econometrica, the numerical method should enable a substantive economic result that could not be obtained as sharply or cheaply with the strongest conventional comparator. The current counterfactual does not meet that test.

### B7. The implementation theorem is strong but narrow and does not close the whole NBO platform

The nonlinear deployment account is tied to a particular arithmetic graph and a nearest-node tabulated actor. Dyadic actions and selection cutpoints are exactly representable; recursive risk is interval-evaluated; fused arithmetic, flush-to-zero behavior, and physical actuation are outside the contract. This is a legitimate and useful specification.

It is not an end-to-end account for the broad actor--critic framework in the retained applications. It does not cover nonlinear network training arithmetic, every historical quadratic pipeline, or deployment of a continuously evaluated neural actor. The current scalar policy is ultimately a stored table selected from neural Q intervals.

The manuscript should present this as a complete implementation result for the declared scalar construction, not as evidence that the broader controlled-diffusion, preference, temporal-self, and game implementations have received the same treatment.

### B8. The cumulative scope remains disproportionate to the completed contribution

The active publication consists of a 68-page main article, a 45-page technical supplement, a 48-page applications companion, and a four-page response. It retains controlled diffusions, recursive utility, endogenous preferences, temporal selves, dynamic games, quadratic risk-sensitive control, continuation reuse, precision adaptation, and the scalar nonlinear verifier.

The strongest completed R41 result is much narrower: direct post-training certification of four scalar neural continuations, plus a native-precision pressure catalogue for quadratic factor updates. The manuscript is transparent that the two instances do not computationally discharge the obligations of every application, but the title and cumulative structure still invite a platform-level interpretation.

This is not merely a request for shorter exposition. The broad structure makes it difficult to identify the paper's estimand, method, comparator, and decisive evidence. A focused submission should contain one authoritative nonlinear construction, one training-to-certificate chain, one matched work design, and one substantive economic application.

## 4. Major comments and required changes

### M1. Separate verification from training in the statement of contribution

The direct theorem is a post-training verifier. State that clearly. Do not treat certification of four frozen networks as a constructive training result. If training is part of NBO's contribution, supply its own assumptions, resource account, failures, and reliability estimand.

### M2. Define a method-level estimand

Possible targets include:

- probability that a prespecified training procedure returns a certifiable policy;
- expected or median complete work to a certified economic threshold;
- a deterministic guarantee over a declared initialization basin; or
- an equivalence/superiority probability over a specified task distribution.

Four selected frozen networks establish none of these method-level objects.

### M3. Run a matched from-scratch frontier

For both neural and spline procedures, include label or target construction, fitting, all failed refinements, policy extraction, final verification, and output. Stop each method at the first common global or displayed-state target. Report both total clocks and machine-independent work.

### M4. Use a prospective economic equivalence or superiority margin

The `0.001` margin was selected after inherited results existed and is explicitly descriptive. A future experiment should choose the economically meaningful margin before final evaluation and allocate training and verification effort accordingly. Intervals contained in a post-hoc band should not be called equivalence evidence.

### M5. Demonstrate a nonlinear neural construction rather than only a nonlinear neural verifier

One route is to train directly on Bellman or own-policy targets with held-out residual certification and record all failures. Another is to give a deterministic approximation-and-optimization construction with explicit width, sample, and iteration requirements. The current spline-supervised historical fit is not enough.

### M6. Execute the multidimensional theorem

Use at least one coupled multidimensional nonlinear economy with continuous or high-support shocks. Include a strong non-neural approximate-dynamic-programming baseline and report state/action/innovation cover growth, memory, and policy-query cost.

### M7. Redesign the precision experiment around work savings

Activation has now been shown. The remaining question is whether adaptation helps. Prespecify cases spanning conditioning and target accuracy, repeat isolated clocks, report attempted and accepted operations by precision, and compare adaptive with the best implementable fixed policy at the same economic target.

### M8. Tighten the certificate comparison

Report, in the main table, both neural and spline global and query-state policy-gap bounds. The current direct value intervals alone obscure that the conventional policy also has substantially tighter certificates.

### M9. Distinguish the tabulated deployed actor from a neural actor

The policy returned by the nonlinear verifier is a nearest-node table selected using neural Q intervals. This is acceptable, but it should be reflected in the algorithm name, complexity statement, and implementation discussion. It is not the same object as a continuously evaluated neural actor.

### M10. Reorganize the publication around one completed contribution

A focused paper could retain the historical applications as motivation or an online archive. The main submitted object should not require a referee to assess several generations of method, theorem, and experiment at once.

## 5. A focused publishable route

The strongest publishable object now visible in R41 is:

> A direct, source-bound method for certifying frozen neural Bellman continuations and their induced feasible policies on compact nonlinear control problems, with explicit state/action cover, terminal, risk, and numerical-execution allowances.

A credible new submission could be organized as follows.

### 5.1 Verification theorem

State the direct neural residual theorem, the actor-selection allowance, terminal discrepancy, and the nonzero arithmetic contract in one chain. Make clear which objects are exact, interval-enclosed, tabulated, or neural.

### 5.2 Training-to-certificate study

Prespecify a nonlinear neural training procedure and task distribution. Retain failed fits. Report the probability or deterministic conditions under which the resulting network passes the direct verifier.

### 5.3 Matched conventional comparison

Compare with spline, sparse-grid, projection, fitted-value, and policy-iteration baselines from common primitives to a common certificate. Include construction, training, verification, and query work.

### 5.4 Multidimensional economic application

Use an economy in which the nonlinear continuation is genuinely multidimensional and the certified policy changes an economically substantive counterfactual. The neural method need not dominate every baseline, but it should deliver either a capability, accuracy, or work regime not already obtained more sharply by the conventional method.

### 5.5 Precision as a supporting result

Keep the activated mixed-precision catalogue, but present it as mechanism evidence unless repeated matched-work results show a real efficiency gain.

## 6. Independent verification performed for this report

I performed the following checks against the pinned R41 snapshot and the source-bound workflow artifact `nbo-r41-complete-review-publication` (artifact ID `11460768113`, SHA-256 `b5dc1a9fdcedc3279dbd7e9c190425f7e856f1fbcd67083e7452c2febc06aac6`).

1. **Snapshot and source identity.** I fixed the reviewed branch at commit `06a104a8db06b76464165899d817b303cb2aaa01` and tree `783b70a4ea1ead950d7ea04aeebccc27a7510bf4`. I verified the Git blob identities of the main article, supplement, response, and applications companion.
2. **Publication ledger.** All 278 files in `FILES_SHA256.json` exist in the publication artifact and match their declared SHA-256 values.
3. **Study identities.** All six study-code hashes, twelve neural-refinement record hashes, four direct-comparison hashes, and forty-eight precision record hashes match.
4. **Direct neural execution.** The committed test result records successful execution of the direct neural certificate with the spline evaluator disabled. The active test suite also reports 2,590 rational neural checks, 100 high-precision risk checks, and 1,032 exact rational deployment fixtures.
5. **Direct policy comparison.** Recomputing every neural-minus-spline interval gives 14 strictly positive lower endpoints, 0 strictly negative upper endpoints, and 2 intervals overlapping zero. All sixteen lie inside the disclosed post-hoc `±0.001` descriptive band.
6. **Certificate comparison.** The spline has the tighter global policy bound in all four economies. Using its own certified lower Bellman function at the four query knots and its outward policy-value upper intervals, I also obtain tighter displayed-state bounds in all four. Neural/spline global-gap ratios range from approximately `1.440` to `1.466`; query-gap ratios range from approximately `1.742` to `1.841`.
7. **Post-training clocks.** Summing all retained neural refinements gives approximately `8.978`, `32.091`, `8.464`, and `31.319` seconds across the four economies. The contemporaneous spline final-resolution construction-and-query clocks are approximately `8.544`, `26.392`, `8.162`, and `26.058` seconds. I do not interpret these single, differently scoped clocks as a matched end-to-end test.
8. **Precision catalogue.** Adaptive and fixed64 each perform 158 accepted updates. Adaptive additionally incurs 42 rejected binary32 proposals and mixes precision in ten services. Its recorded clock exceeds fixed64 in all twelve matched objects. The adaptive/fixed64 time ratio ranges from approximately `1.002` to `1.096`, with median approximately `1.019` and aggregate ratio approximately `1.026`.
9. **Compilation.** The active article, supplement, applications companion, and response contain no recorded undefined references, duplicate labels, missing characters, or overfull boxes. Their page counts are 68, 45, 48, and 4.
10. **Scope.** I did not rerun neural training, the nonlinear verification catalogue, or the precision services. New executions would be new observations rather than validation of the frozen clocks. The review directory contains the deterministic audit script and its machine-readable output.

## 7. Recommendation

R41 is a real advance over R39. The author has directly certified the trained continuation against its own future network, activated the precision branch, supplied a nonzero execution account, and sharpened the economic interpretation. The source and evidence discipline is exemplary, and I found no immediate internal contradiction in the new direct neural certificate under its stated assumptions.

Nevertheless, the current manuscript does not meet the standard for an Econometrica numerical-methods contribution. It verifies four inherited, spline-supervised neural objects but does not provide a constructive or reliable nonlinear neural training method. The contemporaneously reoptimized spline is certified to have lower cost in fourteen of sixteen displayed comparisons, is never certified worse, and has tighter policy-loss bounds. The new neural verification work is not lower in the recorded partial comparison, while the full from-scratch costs are not matched. Mixed precision is activated but is slower than fixed64 in every recorded object. The nonlinear execution remains scalar, short-horizon, and grid-first; the broad multidimensional and multi-application framing is not supported by executed method-specific evidence.

I therefore recommend **rejection in the present form and no further ordinary revision of this cumulative submission**. A new, sharply focused paper on direct post-training neural Bellman certification—or a genuinely new NBO study with a complete nonlinear training-to-certificate chain, multidimensional execution, and matched conventional comparison—could merit serious consideration.
