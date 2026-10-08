# R50: cost-directed improvement and separated allocation

Date: 8 October 2026. This protocol is frozen locally before the measured catalogue. It is not a remote preregistration: the current connection exposes repository reads but no write action. The known R49 outcomes motivated the design. No R50 measured outcome has been used to choose its cells or sample size.

## Policies and safety

Retain the original R49 economy, continuous uniform innovation, horizons, prices, and original lexicographic owner rules. Both native witness/ReLU and conventional FVI receive exactly the same terminal improvement. Observe eight bits per state coordinate, deploy actions on the 1/4096 lattice, and enforce capacity at the entire observation cell. Earlier date actors remain unchanged. Compute the final-date expected cost and its derivative analytically, including the integrated positive-part penalty. Find the lattice minimizer at the observed cell center by convex derivative bisection. Accept it only when an outward interval for its actual conditional cost minus incumbent cost is nonpositive on the whole cell. Otherwise return the exact incumbent. The theorem's general multistage version is distinct from this executed final-stage specialization.

## Construction catalogue

Use dimensions 2,3,4 with T=2, price=1 and common target 5. In dimension 2 also use T=2,3 and price=1,4 at common target 2. For each of these seven cells run compiled witness and tensor FVI. Choose N,K,M prospectively by exact enumeration of the sufficient primitive bound over powers of two: N from 4 through 64, K and M from 1 through 16, reserving 1e-8 for arithmetic. Minimize T(N+1)^d(K+1)M, breaking ties lexicographically. This is a query proxy, not total work; evaluate the actual policy certificate separately and retain failures.

Add residual-driven FVI at d=2,T=2,price=1,target=5 using the same planned quotas. The adaptive rule inserts knots using own-future Bellman midpoint interpolation surpluses and then equidistributes square-root surplus masses on each coordinate, quantized to 24 fractional bits. Include all pilot queries. Record whether the grid truly changed, rather than treating the method name as evidence. This is not a general sparse-grid comparison.

Add witness and FVI isotropic allocations at d=2,T=2,price=1,target=5, selecting the smallest power-of-two N=K=M meeting the same primitive budget. Execute all 17 services three times in separate processes, with one CPU, one numerical-library thread, identical warm-up, and rotated service order: 51 services. Repetitions measure clocks, not optimizer success probabilities. Freeze all payload hashes and retain all failures.

## Direct actual costs

There are 25 predeclared groups. Sixteen use the original R49 witness and FVI policies at first crossing of target 2 for the four horizon/price cells, each under uniform initial states or the constant vectors 1/8,1/2,7/8. Seven groups use the new planned services under uniform states. One compares residual-driven and uniform FVI. One uses the isotropic services. Each group evaluates both original and terminal-repaired policies, giving four absolute costs and all six pair differences, hence 250 estimands.

Use 131072 common paths per group, forty-bit innovation/initial-state bins with outward interval propagation, and exact integration of the last innovation. Acquisition ambiguity is enclosed, never dropped. Use simultaneous empirical-Bernstein bounds with family maximum 512, error 1/100 and logarithm upper bound 13. Conditional on independent ideal draws, the union bound covers the full declared family. PCG64 and fixed seeds supply reproducibility, not a proof of probabilistic independence. The own-policy reduction is centered algebraically and has deterministic nonnegative support from the cell gate. Other differences are computed directly, not by subtracting separate regret bounds.

## Work and disclosure

Construction clocks start before planning and include targets, fitting/compilation, actors, certificate, and durable checkpoint output. Record a separate through-record clock, operation categories, checkpoint bytes and peak resident memory. Direct evaluation clocks include both loads/compilations, interval paths, terminal gates and statistical reconstruction. Do not splice historical and new clocks; do not label uncounted bit operations or FLOPs as zero. Price calculations may use finite-catalogue interval envelopes, with normalized prices explicitly distinguished from calibrated information technology.

Before freezing, exact-arithmetic tests exposed that midpoint bisection alone can remain uniform at a power-of-two quota. The square-root-surplus equidistribution was added before measured execution, and the failed development test and prior source are retained in the audit. Local pre-execution development and inspection are not included in performance clocks. Refuse overwriting completed records. Source and input hashes are fixed in SOURCE_FREEZE.json; offline publication archives are retained permanently with their original digests.
