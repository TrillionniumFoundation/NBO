# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Science revision reviewed:** `revision/econometrica-nbo-r42-source-2026-10-07`  
**Pinned science commit:** `70bf2db76bf7c873be0d8748a5cc120001f347aa`  
**Pinned science tree:** `661afa45b698a6f928f39d2d1ff7977764044b37`  
**Inherited authoritative manuscript:** `revision/econometrica-nbo-r41-review-ready-2026-10-07`, commit `06a104a8db06b76464165899d817b303cb2aaa01`  
**Inherited main manuscript:** `revisions/2026-10-07-r41/ECTA.tex`, Git blob `07e8100e1a97d1b2b1aae7e47d0be3b1906e8f6d`  
**Inherited technical supplement:** `revisions/2026-10-07-r41/supp.tex`, Git blob `ac5fc091749f32c31a6aec891943f29b591d687f`  
**R42 successful workflow run:** `37581511628`  
**R42 evidence artifact:** `11465997076`, SHA-256 `540f80f65c27b9998b2a54375f79413f1a1f3d82bd04e50b810dba6dfed607cc`  
**Report date:** 7 October 2026  
**Recommendation:** **Reject in the present form and do not continue the cumulative manuscript through another ordinary revision round. A new, sharply focused paper on from-primitives neural Bellman training and direct certification in compact nonlinear control could merit evaluation, but the R42 evidence does not establish an Econometrica-level method-specific contribution for the broad NBO program.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R42 makes a real scientific advance over R41. The preceding report's most important objection was that the direct nonlinear theorem certified four frozen networks but did not supply a from-primitives method for producing them. R42 now executes fresh backward training on each candidate's own already-fitted future network. The scalar neural services use no conventional labels, inherited weights, or spline fallback. The coupled nonlinear services train hidden weights in a two-state, two-control model with a continuous innovation law and continuous simplex actions. The catalogue also includes a flexible 96-feature nonnegative ridge comparator and three independent repetitions of the precision-pressure design. The successful run executes all 150 fixed services and reports no software failure.

The provenance standard is again unusually strong. The first full run is retained and records four software exceptions caused by an unstable inverse-softplus transformation. The source was then changed to an algebraically equivalent stable transformation, finite-coefficient regression tests were added, and the unchanged catalogue was rerun under the same economic primitives, seeds, targets, training budgets, and comparator definitions. I downloaded both artifacts, verified their digests, and independently replayed the aggregate arithmetic from every successful service record.

These improvements resolve an important procedural and conceptual threshold. R42 is no longer only post-training verification of inherited networks. It is an executed finite training-to-certificate algorithm with explicit failure outcomes and a common service boundary.

The revision nevertheless remains unsuitable for publication in its present form for two distinct reasons.

First, **R42 has not been materialized as a paper revision**. The branch contains a study protocol, an addendum, a source capsule, a correction script, a workflow, and the successful science artifact. Its root README still identifies R41 as the current paper. There is no R42 main article, technical supplement, point-by-point response, generated table set, release audit, or compiled R42 PDF. The authoritative article is therefore still R41, whose abstract, text, and tables do not contain the new R42 catalogue or its adverse findings. A referee can review the R42 science as an evidence addendum to R41, but not as one internally coherent submitted manuscript.

Second, the new evidence still does not establish a method-specific advantage for NBO. In the scalar catalogue, direct neural training reaches the 0.06 all-state target in all twelve services but reaches 0.04 in only six; the spline reaches both targets in all twelve. Every matched spline global gap is tighter, with neural-to-spline ratios between approximately 1.296 and 1.317. At the common 0.06 crossing, 29 of 48 displayed-state neural-minus-spline cost intervals have strictly positive lower endpoints, none has a strictly negative upper endpoint, and 19 overlap zero. All are inside the prespecified descriptive ±0.005 margin, but interval containment inside a margin is not equivalence and the signed evidence favors the spline.

The coupled nonlinear experiment is more ambitious and genuinely exercises learned hidden features. Yet the flexible ridge comparator remains at least as compelling. Both methods reach 0.25 in all six services; the ridge reaches 0.10 in all six, while the neural method reaches it in five. The neural final all-state gap is tighter in two of six services and looser in four. At the 0.25 target the ridge reaches the target faster in all six matched services. At 0.10, the ridge is faster in four of the five services in which both pass, the neural method is faster in one, and one neural service fails while the ridge passes. Moreover, the coupled records do not contain direct neural-minus-ridge policy-value intervals, so separate regret bounds cannot identify the sign of the actual policy-cost difference.

The precision result remains adverse. Fixed64 and adaptive both certify all 36 objects and execute the same 474 accepted updates. Adaptive also performs 126 rejected binary32 proposals before escalating. It is slower in 26 of 36 paired runs and faster in ten; its aggregate recorded time is approximately 0.98 percent higher than fixed64. This is not evidence that adaptive precision is universally slower, but it is no evidence of the claimed complete-work benefit.

The successful contribution is therefore narrower than the manuscript's platform framing: R42 supplies a careful finite catalogue showing that fresh own-future neural training can sometimes be taken through a direct all-state certificate. It also shows, honestly, that strong conventional approximations remain more reliable or sharper on the declared tasks and that the adaptive precision controller does not reduce complete recorded work. That is scientifically useful. It is not yet an Econometrica-level demonstration that Neural Bellman Operators unlock a substantive economic result or improve the work-to-certified-accuracy frontier.

I recommend rejection in the present form. A new paper centered on the training-to-certificate algorithm, with a fully materialized manuscript, direct method comparisons, multidimensional scaling evidence, and a substantive economic application could merit serious consideration.

## 2. What R42 successfully repairs

### 2.1 Fresh own-future neural training is now executed

The scalar direct-neural services start from economic primitives, construct terminal targets from the primitive terminal cost, and proceed backward using only their own fitted future networks. The successful records report:

- zero conventional training labels;
- zero inherited neural weights;
- zero spline fallbacks;
- finite optimizer schedules;
- complete target-generation work;
- all attempted verification resolutions; and
- durable checkpoint records before target crossings are timestamped.

This directly answers the most important R41 objection. The result is no longer merely a verifier applied to historically selected networks.

### 2.2 The primary estimand is correctly defined as a capped service

The protocol defines a method as an algorithm that either returns a stored continuation and a certified policy at a declared all-state target or records a failure. It does not relabel successful final objects as proof that a nonconvex optimizer always converges. Success fractions are reported on the complete fixed task-and-seed catalogue rather than extrapolated to an unspecified population.

The accounting boundary includes own-future target construction, fitting, failed refinements, policy extraction, verification, independent state queries where available, serialization, and fsync. Initialization and outer-process time are retained separately. This is a substantial improvement over comparisons that charge one method only after its candidate has already been constructed.

### 2.3 The conventional comparison set is materially stronger

The scalar spline is reconstructed from the same economic primitives and receives its own resolution ladder and the same stopping targets. In the coupled experiment, the author retains the deliberately weak quadratic comparator but adds a 96-feature squared-hinge ridge dictionary fitted by nonnegative least squares on its own future targets.

The addendum explicitly states why this comparator was added: failure of a degree-two projection must not be interpreted as neural superiority over flexible conventional approximation. This is the correct scientific response to an unfavorable design concern.

### 2.4 The coupled experiment is genuinely nonlinear and uses continuous actions and innovations

The coupled model has two states, two controls, a shared simplex constraint, coupled nonlinear transitions, and independent continuous uniform innovations. Verification uses analytic positive-part moments, a continuous-action primal-dual certificate, state coverage, terminal allowances, and an independently checked own-policy recursion. It does not certify only a finite action menu or sampled state set.

The learned continuation uses trainable hidden locations and nonnegative squared-ReLU coefficients. The hidden weights move materially in the successful fits. This is not a fixed feature dictionary mislabeled as neural training.

### 2.5 The precision experiment now has repetitions and actual escalation

The twelve dimension/conditioning/target objects are repeated three times for fixed32, fixed64, and adaptive. Fixed32 fails most objects. Adaptive accepts both 32- and 64-bit proposals and retains every rejection. The records expose update counts, precision-specific attempts, accepted and rejected work, multiply-add proxies, and full service clocks.

This is a much more informative mechanism experiment than a single trace in which the adaptive branch never changes precision.

### 2.6 Development failures and the correction chronology are preserved

The first publication run attempted all 150 services and recorded four `Nonfinite network` software exceptions in coupled neural services. The successful rerun followed a specific numerical-stability correction, not a change to the economic design, target, seed list, or comparator menu. Both artifact digests and the correction description are retained.

This is good practice. A software correction before the final source-bound run is not itself a scientific defect when the failed run is preserved and the design remains fixed.

### 2.7 The evidence is unusually auditable

Every service runs in an isolated subprocess and has a separate record, clock, stdout log, process record, and optional checkpoint directory. The successful index binds 150 record hashes and five source hashes. The protocol, addendum, source capsule, inherited R41 artifact, first failed R42 artifact, and final successful R42 artifact all have explicit identities.

## 3. Blocking concerns

### B1. There is no materialized R42 paper to review

This is the threshold publication problem.

The latest branch is named `r42-source`, not `r42-review-ready`. Its root README still declares R41 as the current paper. The R42 directory contains only:

- `STUDY_PROTOCOL.md`;
- `PROTOCOL_ADDENDUM.md`;
- a base64 source capsule;
- a stability correction script; and
- the workflow source.

The successful 28 MB evidence package exists only as a workflow artifact. There is no integrated R42 `ECTA.tex`, supplement, response, result table, release manifest, or compiled PDF. The inherited R41 manuscript therefore remains the only paper, while the R42 evidence materially changes the answers to the R41 referee report.

This separation is not merely editorial. A reader of the current article will not learn that:

- fresh scalar training reaches 0.04 in only six of twelve services;
- the spline reaches both targets in all twelve;
- the flexible ridge reaches both coupled targets in all six services;
- one coupled neural service misses 0.10;
- the scalar signed comparisons favor the spline;
- the coupled records lack direct neural-versus-ridge policy intervals; or
- adaptive precision is slower in 26 of 36 matched runs.

A submission must first bind its claims, theorems, tables, limitations, response, and evidence into one immutable review-ready snapshot. R42 has not done so.

### B2. The scalar training-to-certificate result is reliable only at the looser target

The direct neural procedure reaches the all-state target 0.06 in all twelve scalar services. It reaches 0.04 in only six, exactly the price-one services. All six price-four services fail to reach 0.04 within the frozen cap.

The conventional spline reaches both 0.06 and 0.04 in all twelve services. Its final global bound lies between approximately 0.02947 and 0.03168, compared with approximately 0.03843 to 0.04137 for the neural method. In every one of the twelve matched services the neural bound is larger, by factors between approximately 1.296 and 1.317.

This is not a minor difference in presentation. The protocol deliberately declared two targets to reveal whether the algorithm has an accuracy frontier. The tighter target separates the methods, and the direct neural method fails on half the catalogue.

A numerical-method paper should analyze these failures. Which component is binding: representation, optimization, terminal fit, off-grid state cover, action cover, or numerical allowance? Can additional work reliably reduce it? What is the work-to-gap curve beyond the current cap? R42 reports the outcomes but does not yet turn them into a method analysis.

### B3. The scalar direct economic comparisons favor the spline

At the first common 0.06 crossing, the 48 displayed-state neural-minus-spline cost intervals have the following signs:

- neural cost strictly higher: 29;
- neural cost strictly lower: 0;
- interval overlaps zero: 19.

At the first common 0.04 crossing, which exists only in the six price-one pairs, the 24 intervals have:

- neural cost strictly higher: 17;
- neural cost strictly lower: 0;
- overlap: 7.

Every interval lies inside the prespecified ±0.005 descriptive margin. This supports the statement that the methods are numerically close at these selected states. It does not support equivalence because no equivalence testing design or two-one-sided decision rule is supplied, and it does not support neural superiority. The signed evidence is one-sided in favor of the conventional method.

The economic conclusion is consequently method-neutral: both procedures can produce policies close enough for the declared state queries, but the spline is sharper globally and has lower certified cost in many queries. The paper must not present the scalar catalogue as evidence that learned hidden features are economically useful relative to the conventional construction.

### B4. The flexible coupled comparator is at least as strong as the learned-hidden-feature method

The coupled neural method reaches 0.25 in all six services and 0.10 in five. The ridge comparator reaches both targets in all six.

At the final cap:

- neural gap tighter than ridge: 2 of 6;
- ridge gap tighter than neural: 4 of 6.

At the 0.25 target, ridge reaches the target faster in all six matched services. The neural/ridge time ratio ranges from approximately 1.04 to 2.78, with a median near 1.35. At 0.10, both methods pass in five services; ridge is faster in four and neural in one. In the sixth service, ridge passes while neural fails.

The neural fit does update hidden weights, so the comparison is meaningful. But the result does not establish that learned hidden locations improve reliability, certificate sharpness, or complete work relative to a fixed flexible dictionary of comparable storage. The neural final continuation stores 975 scalars in each service; the ridge stores approximately 1,023 to 1,055. This is not a comparison of a tiny conventional model with a vastly larger neural model.

A top-journal claim would require either a domain where learned features systematically improve certified work or a theorem explaining why the finite neural construction achieves something the fixed dictionary cannot. R42 provides neither.

### B5. The coupled study lacks a direct neural-versus-ridge economic comparison

The coupled records report an upper bound for each candidate policy value and a lower bound for the optimum. These provide separate regret bounds. They do not provide lower and upper bounds for

\[
J(\pi^{\mathrm{neural}})-J(\pi^{\mathrm{ridge}}).
\]

Subtracting two regret upper bounds cannot identify which policy has lower cost. The scalar study correctly supplies direct interval comparisons at common states; the coupled study does not.

This omission matters because the final regret bounds alternate: the neural method is tighter for two seeds and the ridge for four. Direct common-state or common-innovation policy-value differences are necessary to determine whether these certificate differences correspond to actual policy-cost differences.

The next study should predeclare an initial-state distribution or state set, evaluate both policies on identical uncertainty draws or through a shared deterministic quadrature, and form the difference directly with a complete numerical allowance. Method ranking should not be inferred from separate distance-to-optimum bounds.

### B6. The nonlinear evidence remains a small tensor-cover experiment rather than a scaling result

The scalar study is one-dimensional. The coupled study has two states, two controls, four decision dates, and the same three seeds. Its finest accepted state cover has at most 16,641 nodes and its action certification uses a problem-specific strongly convex simplex solver. Continuous uncertainty is integrated analytically through positive-part moments.

This is a legitimate nonlinear construction, but it does not establish practical scaling. The verifier still pays tensor state coverage, and the actor table at the finest neural attempt stores 133,128 scalar entries. The neural verification performs hundreds of millions of neuron-expectation operations in some services.

The broad NBO program claims relevance to high-dimensional controlled economies, recursive preferences, and games. R42 does not execute the new from-primitives nonlinear method in those settings. The old quadratic dimensions and the precision matrix catalogue are different algorithms and cannot serve as nonlinear scaling evidence.

At minimum, a new paper should vary dimension, horizon, state-cover strategy, action dimension, innovation representation, and conditioning. It should include sparse-grid or adaptive-partition comparators and report failure as cover costs become prohibitive.

### B7. There is no stable matched work-to-certified-accuracy advantage

R42 improves the service boundary, but the resulting work frontier does not favor one neural method consistently.

In the scalar catalogue, relative time depends sharply on the economic cell and target. At 0.06 the neural method is slower on average in three of four price-risk cells and faster in one. At 0.04 it passes only the two price-one cells; it is slower in one and faster in the other. The spline is always sharper at the final cap.

In the coupled catalogue, ridge is faster in all six services at 0.25 and generally faster at 0.10. The neural method's median training time is approximately 3.83 seconds, compared with 1.41 seconds for ridge, before the remaining verification work is added.

All timings are single GitHub Actions observations with uncontrolled CPU frequency and no repeated scalar or coupled run. The protocol correctly labels them descriptive. That also means they cannot support a stable performance conclusion.

A publishable method comparison needs repeated isolated timings, machine-independent operation counts, complete memory accounts, actual early stopping, and accuracy-versus-work curves. The comparator should receive its own adaptive refinement and optimization tuning under the same predeclared rules.

### B8. Adaptive precision again fails to reduce complete recorded work

The precision catalogue is now large enough to state the result clearly.

- fixed64 certified: 36 of 36;
- adaptive certified: 36 of 36;
- fixed32 certified: 6 of 36.

Fixed64 and adaptive each perform 474 accepted updates. Adaptive first attempts binary32 on all of them, accepts 348, rejects 126, and then performs 126 accepted binary64 updates. Across the 36 paired services:

- adaptive faster: 10;
- adaptive slower: 26;
- median adaptive/fixed64 time ratio: approximately 1.018;
- aggregate adaptive time change: approximately +0.98 percent.

At the object level, using the median of the three repetitions, adaptive is faster for three objects and slower for nine.

This is a useful negative result: the controller activates, but low-precision savings do not offset rejection and control overhead on the recorded CPU implementation. It should be presented as such. The current evidence does not support adaptive precision as a numerical advantage.

### B9. Fixed catalogues do not establish nonlinear training reliability

The three seeds are prespecified and every failure is retained. That is good. It is still a finite catalogue, not a theorem or population estimate for nonlinear optimizer reliability.

The successful coupled neural rerun follows a numerical-stability correction after four software failures. The corrected code then completes all six coupled neural services, but one misses the tighter economic target. The hidden-weight optimizer has no deterministic convergence cap to the required residual and no probabilistic success model over initialization or economic tasks.

A method-level claim requires a clear estimand. Possibilities include:

- probability of reaching a certified target under a prespecified initialization law;
- median complete work to target, with failures assigned their actual capped cost;
- deterministic performance over a declared compact input class; or
- a worst-case fallback guarantee that remains genuinely neural rather than reverting to the conventional spline.

R42 reports fixed-object outcomes but does not yet establish one of these broader objects.

### B10. The broad manuscript scope remains disproportionate to the new result

The inherited active manuscript is 68 pages, with a 45-page technical supplement and a 48-page applications companion. It retains controlled diffusions, recursive utility, endogenous preferences, temporal selves, games, several historical numerical laboratories, the quadratic construction, direct nonlinear certification, floating-point execution, and the new training catalogue.

R42's strongest new contribution is much narrower:

1. a scalar own-future neural training service with direct global certification;
2. a two-dimensional convex squared-ReLU training service;
3. matched spline and ridge comparators; and
4. an adverse mixed-precision replication.

The original applications do not receive the R42 training-to-certificate algorithm or a new matched work study. The economic counterfactuals remain stylized and are at least as accessible to conventional methods. The cumulative architecture therefore continues to obscure the paper that might actually be publishable.

## 4. Major comments and required changes

### M1. Materialize one immutable R42 submission

Before another external review, create one authoritative R42 main article, supplement, response, tables, source manifest, and compiled document set. The article must state every new success and adverse outcome. A workflow artifact is evidence, not a substitute for the submitted paper.

### M2. Choose a method-level estimand

Define whether the paper studies target-attainment probability, complete work to target, deterministic finite-catalogue performance, or a worst-case construction. Design training repetitions and failure handling around that object. Do not move from three fixed seeds to general method reliability without an explicit bridge.

### M3. Diagnose target failures by allowance component

For every scalar and coupled neural failure, report the representation, optimization, terminal, state-cover, action-cover, numerical, and policy-evaluation contributions separately as work increases. This would show whether the method can improve with additional training or is limited by the verifier and cover design.

### M4. Supply direct coupled policy comparisons

Evaluate neural and ridge policies on the same declared initial states or initial-state distribution and form direct cost differences. Preserve common innovations or common quadrature so the comparison targets the quantity of interest. Separate regret certificates are not method contrasts.

### M5. Strengthen conventional nonlinear baselines

The ridge comparator is a good start. A focused paper should also include at least one adaptive sparse-grid, projection, fitted-value, or approximate-policy-iteration method with comparable access to analytic innovation integration and the same final verifier. Comparator exclusions should be justified by a precise incompatibility.

### M6. Establish a nonlinear scaling frontier

Execute the fresh training-to-certificate algorithm over a dimension and horizon grid. Vary state/action dimension, coupling, innovation complexity, cover strategy, and target accuracy. Report when the certificate becomes computationally infeasible. A two-dimensional success should not carry a high-dimensional title claim.

### M7. Use repeated end-to-end performance measurements

Repeat each method-service pair in isolated processes under a fixed timing protocol. Report medians and dispersion, initialization, training, failed refinements, verification, policy queries, serialization, memory, and machine-independent operation counts. Stop at the first common target crossing.

### M8. Recast adaptive precision as a negative result unless a new design changes it

The present controller does not save complete work. Either explain why this is the expected outcome on CPU and move it to a diagnostic section, or design a setting in which low-precision kernels have a real measured advantage. Do not treat mixed-precision activation as efficiency.

### M9. Separate verification, construction, and economic discovery

The verifier is credible and useful even when conventional policies are better. The training algorithm is a separate contribution. The economic counterfactual is a third object. State clearly which one is novel and which results identify it.

### M10. Reduce the active paper substantially

A focused submission should contain one notation system, one nonlinear algorithm, one policy theorem, one evidence design, and one economic application. Historical quadratic and application materials can remain in an archive or separate companion, but should not make the active paper appear to establish a general platform that the new evidence does not support.

## 5. A focused publishable route

The strongest potential paper emerging from R42 is:

> **From-Primitives Neural Bellman Training with Direct All-State Policy Certification in Compact Nonlinear Control.**

A credible new submission would include the following components.

### 5.1 One constructive algorithm

Specify the own-future target recursion, network class, initialization law, optimizer cap, actor construction, state/action cover, numerical arithmetic, failure rule, and optional conventional fallback. State exactly what is deterministic and what is random.

### 5.2 One theorem-evidence chain

Connect approximation and optimization error to the direct Bellman residual, then to policy loss and implementation error. Report every allowance component from the executed services. Avoid carrying unrelated historical theorem chains in the main article.

### 5.3 A contribution-isolating benchmark

Use direct policy differences, flexible conventional baselines, repeated work measurements, target sweeps, and dimensions large enough to expose scaling. The neural method need not win every cell, but the paper must identify a capability or work region in which learning hidden features changes the certified frontier.

### 5.4 A substantive economic application

Apply the method where the continuation is genuinely nonlinear and conventional tensor grids become limiting. The final economic conclusion should depend on the certified policy and should not be obtainable more sharply and cheaply from the strongest comparator in the study.

### 5.5 Honest negative findings

Retain the R42 facts: spline and ridge are strong, the tighter neural target can fail, and adaptive precision does not save work in the current implementation. These findings improve the paper when they are used to define the method's actual scope.

## 6. Independent verification performed for this report

I performed the following checks against the pinned R42 source and artifacts.

1. **Branch and workflow identity.** I fixed the science revision at commit `70bf2db76bf7c873be0d8748a5cc120001f347aa`, tree `661afa45b698a6f928f39d2d1ff7977764044b37`, and successful workflow run `37581511628`.
2. **Successful artifact digest.** The downloaded `nbo-r42-from-primitives-science` archive has SHA-256 `540f80f65c27b9998b2a54375f79413f1a1f3d82bd04e50b810dba6dfed607cc`, matching GitHub's artifact digest.
3. **First-run artifact digest.** The retained first-run archive has SHA-256 `ab6b0147aebf8191a68022ce64d4787145859ae8413cc2bcc4c7ff8b3fa53587`. Its index records four software failures. I independently recovered the same four failed coupled neural services and the common terminal error `ValueError: Nonfinite network`.
4. **Catalogue completeness.** The successful artifact reports 150 fixed services, 150 executed services, and zero software failures. I verified all 150 service record hashes and all five frozen source hashes.
5. **Method counts.** The catalogue contains 12 scalar direct-neural, 12 scalar spline, six coupled convex-neural, six ridge, six quadratic, and 36 services for each precision method.
6. **Scalar attainment.** Direct neural reaches 0.06 in 12/12 and 0.04 in 6/12; spline reaches both targets in 12/12. The neural/spline final global-gap ratio lies between approximately 1.2960 and 1.3174.
7. **Scalar direct comparisons.** At 0.06, I recomputed 29 strictly positive neural-minus-spline cost intervals, zero strictly negative intervals, and 19 overlaps. At 0.04, the counts are 17, zero, and seven. All intervals lie inside the fixed ±0.005 descriptive margin.
8. **Coupled attainment.** Neural reaches 0.25 in 6/6 and 0.10 in 5/6; ridge reaches both in 6/6; quadratic reaches neither. Ridge has the tighter final gap in four of six matched services and reaches 0.25 faster in all six.
9. **Precision replication.** Fixed64 and adaptive certify 36/36; fixed32 certifies 6/36. Adaptive is faster in 10 paired runs and slower in 26. Aggregate adaptive time is approximately 0.976 percent higher. Adaptive executes 126 rejected binary32 proposals in addition to the same 474 accepted updates completed by fixed64.
10. **Scope limitation.** I did not rerun or retime the 150 services. A new run would produce new optimizer and timing observations rather than verify the frozen records. The review directory contains a standard-library script that replays the committed record hashes, source hashes, target counts, direct scalar comparisons, coupled comparisons, precision arithmetic, and first-run failure count.

## 7. Recommendation

R42 deserves substantial credit. It directly addresses the central R41 criticism by executing fresh own-future neural training under a complete service boundary, and it strengthens the comparator set instead of avoiding adverse evidence. The source and evidence discipline is exceptional.

The scientific conclusion, however, remains unfavorable to the current broad submission. R42 is not yet a materialized paper revision. The scalar neural method is less reliable at the tighter target and has looser global certificates than the spline. The displayed-state signed comparisons never favor neural and often favor spline. In the coupled problem, the flexible ridge comparator is more reliable, usually faster, and usually sharper; no direct policy-cost comparison is reported. Adaptive precision again supplies no work advantage. The nonlinear experiments remain one- and two-dimensional, and the broad economic applications do not receive the new construction or evidence.

I therefore recommend **rejection in the present form and no further ordinary revision of this cumulative manuscript**. A new, much shorter paper on from-primitives neural Bellman training with direct nonlinear certification could merit serious review after it is materialized as one coherent submission and demonstrates either a distinct certified capability or a favorable work-to-accuracy region relative to strong conventional methods.
