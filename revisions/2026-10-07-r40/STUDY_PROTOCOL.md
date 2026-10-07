# R40 study protocol

The revision is based on the R39 review-ready commit `f472a7c21f2f9db5285f1bf7746edf2d9463638e` and its advisory referee report in `review/econometrica-numerical-methods-r39-2026-10-07-f472a7c`. All R38 records and clocks remain immutable.

## Direct trained-continuation verification

Use the deposited trained networks for all four scalar nonlinear economies: investment price in {1,4}, risk parameter in {0,1}, horizon four. At every date verify `f_t - T_t f_(t+1)` by outward interval evaluation of the networks themselves. Do not use spline values, spline Bellman brackets, or network-to-spline error to establish these new residuals. Use exact rational piecewise-quadratic terminal extrema. Compare all continuous actions, adding the explicit action-cover allowance, and cover every state by a certified neural-plus-Bellman Lipschitz allowance.

Retain the historical policy and separately identify each new neural-selected policy. Verification meshes are (state cells, action cells) = (256,128), (1024,512), (2048,1024), (4096,2048). Refinement stops once the four displayed statewise near-optimality upper bounds are all at most 0.02, or the last mesh is reached. Record the global bound as well; a displayed-state target is not a uniform target. A development run of the price-one, risk-zero economy at (256,128) preceded this protocol; it is retained and is not presented as a fresh prospective observation.

Evaluate the newly selected policies independently on the finite shock tree. Report direct neural-minus-reoptimized-spline cost intervals, in addition to the old-rule repricing exercise. For the inherited four-state comparisons use a disclosed descriptive equivalence margin of 0.001 model cost units; this margin was selected after the inherited results existed and is not a preregistered inferiority test. Do not replace inherited clocks with new verification-only timings.

## Precision activation at economic targets

Execute every combination of (dimension, cost condition) in {(2,1),(2,16),(8,1),(8,16)} and economic target in {1e-10,1e-12,1e-14}. Horizon four, valuation one, innovation covariance 0.001 times the identity and risk parameter 0.1 are fixed. Methods are fixed32-cached, fixed64-cached, adaptive-cached and tuned-cached; tuned tries fixed32 first and then fixed64. Use the inherited R38 native residual verifier and complete-policy stopping test without changing its tolerance or silently accepting a failed target. Preserve every rejected precision proposal, binary64 fallback, failed service and reported reason.

First execute the entire catalogue once as mechanism evidence, not a timing-superiority test. Any later repeated timing experiment must have its own recorded protocol and must include failed trials and construction/verification work. No fixed-precision oracle may be selected retrospectively and presented as an implementable method.

## Deployment and scope

Derive nonzero uniform binary32 storage/evaluation/transition bounds from the arithmetic graph, including clipping and nearest-node selection. Arithmetic fixtures check the implementation; the all-state guarantee is the analytic enclosure, not a sample maximum. State the computational and economic objective being certified. Do not claim physical actuator validation.

Retain the controlled-diffusion framework, all historical theory, all adverse comparisons, and the applications companion. Dimension-dependent continuous-innovation theory is distinct from executed multidimensional numerical evidence. A new theorem or a passing certificate alone is not a method-specific efficiency result.
