# R96 source-first confirmation protocol

Date: 13 October 2026. Controlling review: `2fcf0bbd5926ee927c14a5f6d122fb50bb420988`, reviewing the R95 source `85263fd95ccbb60f0cf1875c0f29f1b7c2558a34`. The title, author, economic primitives, complete-policy optimum, original NBO construction and all inherited scientific sections remain. This is not a replacement topic.

## Estimand and economic precision

The original two-date investment model has continuous states and uniform innovations, beta 15/16 and nested AVaR at 1/2 and 3/4. The primary initial distribution is the uniform 20-bit dyadic grid on the two-dimensional square, not a continuous-uniform initial distribution. The estimand is the initial-distribution mean of the original recursive-risk cost of a complete **qualified service**, including its proposal admission and paid fallback. It is not the cost of the unmodified proposal alone, cash expenditure, or field-calibrated welfare.

The statewise service loss allowance is tau=1/256. Each policy-cost interval must have width at most 1/8192. The economic comparison margin is exactly 1/1280: one percent of the maximal first-date investment charge h(1/4)=5/64, rather than the previous 80 percent. This is a transparent model-relative purchaser tolerance, not an estimated household preference. There are 4096 independent initial states per risk level and twelve fixed pairwise contrasts. A fixed rational sampling radius 1/4096 gives family coverage at least 95 percent, because 24 exp(-8)<0.05. The total simultaneous half-width is at most 3/8192, strictly less than half the margin. These settings are fixed together before confirmation.

## Four arms and matched budget slice

The arms are online-risk-dp, quadratic, relu and spline. Each fitted arm has three nonlinear features and three unrestricted affine coefficients. All use the same 1024 paid training labels per risk level and the same 30-bit readout precision. All have realized design rank six, checked before admission, and a common 128-byte executable model encoding. Their active coefficient counts and condition numbers are reported rather than equated with design rank.

Each fitted representation selects three features by training-only forward selection from 32 candidates, with identical candidate solver and stopping rules. Quadratic and ReLU candidate directions are primitive-only. Coordinate spline knots are training-covariate quantiles; selection also uses training labels. Every candidate solve and rank-rejected candidate is recorded. Equal candidate-search schedules are not equal elapsed fitting work; actual work is measured. This is one controlled rank-six slice, not a claim that all ranks, adaptive convex-regression methods, label budgets and compute budgets have been exhausted.

Calibration uses 128 separate states per risk level and chooses the smallest mean cost-interval midpoint, with lexical ties. All four arms remain in the twelve-contrast family. The six binary models, selected arms, source hashes and calibration record must be committed remotely before evaluation can start.

## Qualified action, quadrature and fallback

The candidate first action uses the inherited 128-bin, 16-step bisection and 30-bit downward action rule. Convex-order risk quadrature evaluates original terminal value bounds at innovation midpoints and endpoints. The all-original-action lower witness uses globally valid affine continuation supports. Acceptance requires both the original-optimum target and numerical width. A rejected proposal is recorded and replaced by a paid online-risk-DP proposal. Integration may increase to 256, 512, 1024, 2048 and 4096 bins without changing that conventional proposal. Remaining states use the explicit exact rational action/innovation cover. The latter is part of the service definition; its execution frequency must be reported. Infrastructure exceptions abort the entire workload and retain progress, not remove observations.

The common terminal controller is the original acquired-state controller with its original uniform 2^-20 allowance. The new quadrature uses convexity of the true V1, not convexity of the discontinuous realized controller. No observed sample maximum is substituted for the global paired support [-tau,tau].

## Prospective fixed-builder ablation

On each fitted proposal, compute the inherited global-norm, signed-scalar and joint-local certificates with the fixed 32-by-32 residual cover and 128-bin own-continuation witness. Preserve whether the proposal was rejected by the service gate. A scalar certificate of a proposed actor is not assigned to a different fallback actor. Charge cover construction and all builder work. This is a prospective comparison of these fixed builders, not an optimally tuned solver frontier. Preserve the R95 paid-screening negative result without turning removed-bin counts into speed savings.

## Streams, timing and independence

All new streams use PCG64(SeedSequence([2026101396, stream, risk_index])): stream 1 training, 2 calibration, 3 confirmation, 5 fixed repeated timing. Development tests use other seeds and are not confirmation. Stream 3 is opened only by the evaluator after checking the committed freeze and source hashes. No sample enlargement, actor reselection, discarded arm, or changed margin is allowed after evaluation.

Each arm/risk timing has five fresh child processes on the same fixed 32-state stream-5 workload. Parent time includes startup, source/model identity checks, loading, qualification, output and shutdown. Record CPU model/frequency, threads, memory, logical counts and all repetitions. Frequency is recorded, not controlled. Min/max timing envelopes are descriptive, not confidence intervals for future machines. Primary construction is on x86-64; a second architecture replays the frozen models without refitting. Repeated streams add no independent economic observations.

Independent inference reads all endpoint rows as exact rational representations of their binary64 values and independently recomputes all paired means, support intersections, signs and coverage constants. A separate rational primitive implementation audits eight randomly selected rows per arm/risk stratum (64 endpoints total) using a 256-bin finer enclosure and its own original-action lower support. Stored candidate actions are independently reconstructed. Conventional candidate selection and the full fitting stack are not independently replayed; the audit states this boundary. The two-control/two-innovation largest execution is not claimed by the scalar confirmation.

## Preservation and release

The stale core49 preservation declaration is reclassified as an intentional amendment with its old hash, current hash, full old source and reason. The old failed R95 ledgers remain unchanged. The preservation test must cover both unchanged and amended sections, so moving one section out of the unchanged category cannot remove its identity check.

All inherited/current tests run without skips. The final record separates scientific execution, source preservation, independent endpoints, document compilation, fresh-process timings, architecture replication and PDF inspection. The four PDFs are freshly compiled; no old PDF is relabeled. Every table records the source and freeze identity that generated it. A queued job or failed aggregate gate is never described as a passed release.

### Pre-construction independent-audit scheduling

The fixed rational endpoint checks may use up to four worker processes (bounded by the reported processor count). Fixture identities, order, arithmetic, containment tests and sample sizes are unchanged. The independent-audit receipt records the worker count and complete parent elapsed time. This scheduling does not create fits or independent observations and is fixed before construction and confirmation.
