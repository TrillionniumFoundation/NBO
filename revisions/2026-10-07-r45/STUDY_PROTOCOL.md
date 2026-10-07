# R45: constructive own-future NBO service

Date: 7 October 2026. Paper: Neural Bellman Operators, Qian QI.
Review baseline: 5d4eca82b5477c4f0305f0f90bf9adc1635ec5de.
Reviewed manuscript: e00d3d46484029738884119f18ce1e15fbdcc929.
Reviewed report: reviews/2026-10-07-econometrica-numerical-methods-r44/referee_report.md.

## Scientific object and preservation

Revise the existing NBO paper; preserve its title, author, controlled-economy subject, every prior revision, theorem, application, empirical record and adverse finding. The new backend is a deterministic min-plus ReLU continuation constructor trained against its own future, not a claim that the original Adam/L-BFGS services have acquired a convergence theorem. Original R42 failures and all R44 diagnostics remain unchanged. The new theorem must choose construction, action coverage and numerical accuracy from primitives and an economic tolerance, rather than assume a successful trained network. Its dimension and bit-cost factors must remain visible.

## New service catalogue, fixed before execution

The laboratory uses x in [0,1], a in [0,1/4], beta=15/16, independent continuous uniform innovations z in [-1/32,1/32], and
F(x,a,z)=1/16+(11/16)x+(1/16)x(1-x)+a+z.
Every admissible transition stays in [0,1]. Stage cost is
c_p(x,a)=(x-11/16)^2+p a^2+4 a^4+2(3/8-x)_+^2,
and terminal cost is g(x)=2(x-11/16)^2+2(3/8-x)_+^2.
This is an additional compact nonlinear investment laboratory with a continuous innovation primitive, not a replacement for either R42 economy and not a high-dimensional experiment.

Use horizons {2,4}, prices {1,4}, two generators {min-plus-ReLU, piecewise-linear-spline}, and three fresh isolated repetitions of every cell: 24 full services in total. All services run the full state/action ladder N=A in {16,32,64,128,256,512}. Economic all-state policy-loss targets are {0.5,0.25,0.125}. Record every rung, its certificate, its first target crossings, all failed work, model and actor storage, operation counters, and time through durable output. Keep failures; no target or ladder is tuned to the results.

For every rung, construct a fresh terminal continuation from g. At each preceding date, form targets using only that generator's own future continuation, the same action grid, and analytic integration of its piecewise-linear continuation under the original continuous uniform law. Certified interval arithmetic encloses every target; labels are rounded to dyadic multiples of 2^-40. The ReLU constructor is the Lipschitz lower envelope min_i{y_i+L||x-x_i||_1}, realized exactly by affine/ReLU/min gates. Its one-dimensional piecewise-linear compilation is an exact acceleration of that network, not externally solved labels. The spline comparator uses its own targets, and its actual exact slope bound is propagated. Both use the same nearest-node feasible actor and the same economic target. Any numerical tolerance that cannot be certified causes a recorded failure, not an omitted row.

Choose primitive state/action Lipschitz constants with outward or exact arithmetic. Validate the constructed network's residual, actor gap, and terminal residual from the constructive theorem. Analytic integration must enclose rational breakpoints and all rounding. An optimizer stopping flag and sampled residual are not certificates. Account separately for mathematical arithmetic contracts, implementation tests, and empirical timing observations.

## Estimand and timing

The primary reliability statement is deterministic termination of the new constructive backend under the theorem's stated compact-domain, primitive-Lipschitz, innovation-approximation and arithmetic hypotheses. The finite experiment tests that backend on the entire declared catalogue; it does not estimate success probability of unrestricted neural training. Three repetitions supply timing dispersion, not additional independent economic tasks.

Run one process at a time, pin a single available CPU where supported, and set BLAS/OpenMP threads to one. Apply one fixed common non-economic warm-up before the timed service. Report hardware, affinity, versions and frequency-control limitations. Each rung begins from primitives rather than continuing a hidden precomputed solution. Costs to target are actual prefix costs through the first durably stored qualifying checkpoint; complete service totals include the whole frontier. Charge target construction, neural/spline compilation, actor construction, certificate calculation and serialization. Independent policy-cost comparison is NOT performed in this study and must not be assigned a zero cost or claimed as included. No universal speed advantage is a predeclared outcome.

## Verification and release

Add exact-arithmetic adversarial tests for the multidimensional envelope theorem, terminal and actor accounts, ties, additive shifts, numerical label perturbations, and the action/state-cover factors; test accelerated one-dimensional evaluation/integration against the defining network. Rerun inherited R44 tests when the materialized source permits it. Freeze source hashes before new service execution and preserve execution errors, corrections and reruns in a development disclosure.

Materialize a revised main article, proof supplement, point-by-point response to B1-B10 and M1-M10, complete results, generated tables, executable code and release/preservation audits. Compile using the retained Econometric Society class. The new active theorem chain must have its own complete definitions and proofs; archived applications remain preserved and their additional hypotheses visible. Do not equate a compiled manuscript or passing tests with mathematical peer approval. Requests not settled by the actual theorem or new execution must remain explicitly identified rather than described as closed.
