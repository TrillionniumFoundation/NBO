# R46 protocol: witness-preserving neural Bellman construction

Date: 7 October 2026. This is a prospective specification relative to the new execution, not independent preregistration or a new random economic sample. No full R46 catalogue has been executed at this commit. Development algebra and small exact examples are permitted and must be disclosed.

## Immutable inputs and review chronology

The latest report by commit time is the R43 supplemental review at 9a1ce0502a2cb8f57c697d1df9ba796da0403474 (12:27:38 UTC), reviewing 3c9ad7a969bddf3c79ec5dc07e4b74704fed8615. Its principal concern is an incomplete staging snapshot. It is not a review of R45. The R44 substantive review at 5d4eca82b5477c4f0305f0f90bf9adc1635ec5de (10:42:23 UTC) remains relevant. The manuscript baseline is the completed R45 at 336ea58decb4fae486efa41bb86e69a28879d9d6. Do not regress to or overwrite R43/R44/R45.

## Scientific addition

For node labels y_i and their attaining feasible actions a_i, a min-plus ReLU continuation f(x)=min_i[y_i+L||x-x_i||_1] retains the attaining cone index i(x) and deploys a_i(x). When each numerical action query has error at most e, Q(f_future;x,a_i(x))-f(x)<=e. Combine this one-sided selected-policy inequality directly with the optimal Bellman residual upper bound. Do not add the separate residual-width and nearest-node actor accounts a second time. Prove the general one-sided policy sandwich, the witness construction, approximate-selector allowance and exact scalar witness compilation. Credit classical Lipschitz extension and distinguish this implementation/theorem from generic optimizer convergence and neural superiority.

## Matched execution

Use exactly the R45 primitives, continuous uniform innovation law, discount 15/16, horizons 2 and 4, prices 1 and 4, and resolutions N=16,32,64,128,256,512. Each rung starts fresh from primitives. Numerical integration, label rounding and rational PWL compilation are the existing hash-pinned R45 implementation, unchanged. All generators use their own future continuation.

Execute three methods: (1) min-plus-ReLU with cone-witness actor; (2) the same min-plus-ReLU with original nearest-node actor, as an actor ablation; (3) the piecewise-linear spline with nearest-node actor. Give BOTH nearest-node comparators the direct one-sided policy bound obtained by maximizing y_i+L|x-x_i|-f(x) on their complete nearest-node cells. This avoids comparing the new theorem only against an unnecessarily loose old certificate. Preserve the old R45 bound as a separate diagnostic.

Fix targets 1/4, 1/8, 1/16. Execute every rung even after attainment. Two horizons times two prices times three methods times three isolated timing repetitions gives 36 services, 216 rungs and 72 distinct method/economy/resolution rows. Use all rows, not only prior failures. Report every first crossing and capped failure. No tolerance rounding into attainment. Fix single numerical-library threads and one available CPU per process; report uncontrolled CPU frequency and host metadata. Include fresh target construction, witness compilation, certificate calculation, failed rungs, checkpoint serialization and fsync in the internal prefix clock; record process time separately. Do not add historical clocks. Do not call primitive-object counts FLOPs or complete bit costs. Charge witness indices, rational knots, comparison upper counts and storage separately.

## Actor and evaluation contracts

The witness actor is a NEW policy, not recertification of the R45 nearest-node policy. Store original labels/actions, rational cone switchpoints and witnesses. At exact ties either minimizing witness is valid; fix a deterministic convention and retain adjacent alternatives for uncertain acquisition. A selector whose cone value exceeds the exact minimum by at most nu adds sum B_t nu_t to the policy loss. Do not treat a floating index lookup at a rounded rational switchpoint as exact deployment. Verify the compiled witness against direct rational minimization on small exhaustive and random rational test sets. Verify full checkpoint formulas and complete catalogue counts independently.

## Comparison and scope

The targets are all-state regret tolerances, not superiority or equivalence margins. No new direct policy-cost simulation is in this protocol. Retain the 24 R44 direct intervals and their unresolved signs, all historical adverse conventional comparisons and precision findings. New execution is scalar and deterministic; it is not a genuinely high-dimensional study, an optimizer success probability, or a calibrated economic discovery. Report improvements that the records establish, without selecting a favorable conclusion.

## Atomic release

Use this branch only for staging. Publish a fresh review-ready branch only after materialized UTF-8 sources, complete response, all raw records, generated tables, inherited/new tests, source hashes, clean compilation, preservation checks and authoritative root entry points exist together. The final source tree must rebuild without decoding a source capsule, downloading an expiring artifact, or retraining. Preserve all historical files. Include the latest R43 report and a point-by-point crosswalk distinguishing snapshot-completeness repairs from substantive mathematical/comparative questions.
