# R120 prospective independent original-objective validation

This protocol is frozen with scientific source F before acquisition, sampling or
new economic evaluation. It applies only to this R120 study and does not complete,
replace or redefine any R98, R115 or other independently frozen experiment.

## Scope and immutable inputs

The primary study contains 64 new, row-local initial-state observations for each
of two risks, eight representations and four complete services (4,096 decisions).
The validator reads the entire primary `records120.jsonl`, records its exact
SHA-256 before reading, and verifies that it remains byte-identical. It checks
the full Cartesian census, original feasible state/action identity, exact binary
serialization, and the equality of each service's completed incumbent with the
separately executed completed service. Timing repetitions are not observations.

Every unique exact `(state, action, alpha)` key is evaluated. Exact duplicates
share validation work only after all decisions have already been executed; all
keys, deduplication counts and actual validation cost are recorded. This sharing
does not subsidize a decision service. No key is selected by its fit, economic
outcome, sign, representation, runtime or ease of certification.

## Exact arithmetic and independently implemented economics

The validator imports Python's standard library and the unchanged independent
economic primitives `frozen108/code/independent94.py`, SHA-256
`a1a0e4ce5563d1105c3cea9eaad6678c609229446ba6794f7b8a7c03df01ebad`.
It imports no production interval, risk, compiler, representation or quadrature
module. An AST import whitelist and the actual source-commit byte gate run before
scientific imports. Binary64 state/action bytes are converted exactly to rational
numbers; they are not rounded to more convenient test inputs.

For every key the fixed independent mesh has **64 equal cells on the entire
original innovation interval** and its **129 distinct midpoint/endpoint nodes**.
Every node uses exactly the declared **32 rational terminal derivative-bisection
steps** in the interior case; an exact endpoint derivative condition ends at the
boundary. No adaptive resolution is added after seeing results. The complete
original terminal objective, feasible action, invariant domain, quadratic shock
coefficient 5, exact continuous-risk primal/dual equality and terminal gap no
larger than `2^-20` are checked and retained in compressed exact-rational traces.

The lower fixed-action original-optimal-future value uses midpoint Jensen bounds.
The upper uses endpoint secants and the equal-mass distribution of **128 endpoint
atoms with their multiplicities preserved**. The actual future controller remains
`terminal_controller94.terminal_policy` with downward 40-bit observations. Its
proved `2^-20` terminal suboptimality is paid once as `beta * 2^-20` in the policy
upper bound. This is a rigorous enclosure of the deployed policy, not an assertion
that its value equals the independently optimized continuation.

## Independent original global optimum and regret

At each midpoint, differentiate the exact original terminal objective against a
fixed feasible maximizing risk density. The exact Lagrange-support intercept is
`c = W + lambda*(v-A(y)) - nu*v - (p_v+lambda-nu)^2/4`, with state slope
`r = p_y - lambda/(8d) * 1`. Boundary multipliers are nonnegative and zero away
from their respective active boundary. The retained joint-curvature proof
licenses the affine support globally on the original state cube. The clipped
scalar `terminal_bounds` lower value is **not substituted for this intercept**.

Choose the top `64*(1-alpha)` intercepts with original node index breaking exact
ties. They define a feasible piecewise constant original-risk density. Integrate
each affine state support over its symmetric bin exactly. Add the original
action-cost quadratic minorant and minimize it on the actual feasible interval.
The resulting bound is below the original date-zero optimum for every feasible
action. At the same state and risk, maximize all already paid such lower bounds
and minimize all feasible original-optimal-future upper bounds. This separately
paid validation gives original policy regret intervals and squared distance
bounds to the unique original optimal action. They are bounds, not exact regrets
or exact action errors. Full proofs are in the R120 supplement and the retained
continuous-investment curvature appendix.

For each policy, check that independently obtained fixed-policy intervals overlap
the production certificate, that production optimum lower bounds do not exceed
an independently feasible upper bound, and that production certified gains do
not exceed independent gain upper bounds. Compatibility does not establish exact
equality of two numerical implementations. The complete rational witnesses
provide a route to implement the economic calculation independently again.

## Population inference fixed before observing states

The exact population is the product uniform distribution on
`{0,...,2^40-1}/2^40` in two coordinates, conditional on the stated ideal independent
uniform OS-byte law. Frozen actors precede the single 640-byte acquisition.
All services are row-local: one sampled state cannot trigger another state's
numerical fallback. The two risk levels and all methods share the same 64 rows;
independence across those groups is not assumed.

For each risk, each of eight representations and each of three non-completed
services, the uniform safety theorem puts original gain over that representation's
own completed incumbent in `[0, tau]`, `tau=1/256`. The **48 groups** each receive
two-sided mean error probability `1/1920`. The four fixed event thresholds are
`2^-20, 2^-18, 2^-16, 2^-14`, giving **192 events**, each with one-sided error
probability `1/7680`. The total union allocation is `1/20`.

The event is an independently certified lower gain at least the fixed threshold.
For its count k among all 64 states, use the lower bracket endpoint after exactly
48 rational bisections of the binomial upper-tail equation; k=0 returns zero.
All polynomial comparisons use exact integers. A fixed staircase, with increments
equal to successive threshold differences, turns these probability lower bounds
into a population expected-gain lower bound without selecting a threshold after
observing results.

For means, the fixed rational Hoeffding radius is `33*tau/128`. The exact exponent
is `1089/128`; the degree-20 positive Taylor lower bound for its exponential
exceeds 3840, proving each two-sided error below `1/1920` without floating-point
logarithms, square roots or unverified special-function calls. Apply the radius
to the averages of independent rational gain bounds and intersect with `[0,tau]`.
Intersect this mean lower bound with the simultaneous staircase lower bound.
Clopper--Pearson inversion and Hoeffding concentration are classical methods,
fully attributed, not claimed new contributions.

An unavailable independent comparison is retained as `[0,tau]`; its event count
contribution is zero. It is never dropped or replaced. An incomplete independent
validation remains explicitly incomplete even when conservative inference can
still be reported. No timing repetition increases the state sample size. Runtime
is reported descriptively with all actual clocks and counts; no population runtime
interval or neural adoption conclusion follows from an incumbent-gain interval.

## Execution and failures

Run `code120/independent120.py --source-commit F --primary PRIMARY/records120.jsonl
--output NEW_DIRECTORY`, then `code120/stats120.py --source-commit F --primary
PRIMARY/records120.jsonl --independent INDEPENDENT/comparisons120.jsonl --output
NEW_DIRECTORY`. Paths are illustrative; exact commands and commits are recorded.
Every output directory is created exclusively. Every failed prefix, exception,
elapsed clock, record and input hash is retained. No scientific code or parameter
amendment is described as part of the earlier freeze; a necessary amendment must
be separately committed and disclosed before a new explicitly identified attempt.
