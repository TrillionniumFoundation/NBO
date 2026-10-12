# R77: original NBO controller-cost qualification

Controlling advisory report: R67, 11 October 2026, review commit
`4b27b56f4514f6c1d77b69fe707f7202f8b06b19`, manuscript
`eacd3e217ae1e2e9ea6e154b48da7d103159d051`.
Base: `2d7d9c4e62abc2230087f3a092a5c493b8ca6cb0`.
The title, author, original expected-cost investment primitives, and original
Bellman optimum are unchanged. R70/R72/R73 developments and all prior adverse
observations remain in the reading package. An unexecuted source commitment
on R74--R76 is not a scientific observation and is not silently materialized
as a supposedly historical experiment.

## Predetermined policies and new observations

Five complete two-date policies: the admissible zero-investment incumbent and
the four R73 constructed actors (`relu-n8`, `bernstein-n8`, `relu-n16`,
`bernstein-n16`). Read each actor from its original stage `data.actions`;
never refit, replace its actual fitted future, optimize it on the new samples,
or relabel it as a callable recursive R69 controller. The whole-cell actor
is constant on its n by n acquired-state grid and has downward action quantum
1/4096. The four R73 construction file hashes are frozen before any new paths.
Two bases at the same n have matching acquisition and construction design;
comparisons across n retain their different acquisition precision. The zero
incumbent is an economic reference, not a strong conventional optimizer.
Strong conventional query controls, training, reuse and vector comparisons
remain the separately frozen R67/R69/R70 studies.

Exactly 524,288 independent rows in the declared simulation model, generated
from NumPy PCG64 seed 20261011077, with four independent uniform 40-bit bin
indices per row: two initial coordinates and two innovations. Each bin is a
continuous interval with its original probability. All five policies share
these rows. Neither policies nor contrasts count as additional independent
rows. The seed gives reproducibility, not a theorem of stochastic independence.
The unchanged innovation is common and opposite-signed across coordinates,
uniform on [-1/32,1/32]; beta=15/16 and horizon=2.

For every policy retain (i) the complete cash-cost enclosure and (ii) an
enclosure after analytically integrating the last innovation. Both estimate
the same original-law expected cost. Conditional integration does not change
the policy or the economic law and does not evaluate an optimal Bellman tree.
No timing or policy advantage is assumed for either estimator.

All five marginal costs and all ten paired differences are reported for both
estimators: 30 estimands, 60 one-sided endpoint events. Apply Maurer--Pontil's
bounded empirical-Bernstein inequality with log upper bound 10. The family
failure probability is at most 120 exp(-10) < 1/100. A primitive global cash
support is [0,21097/4096]; differences have signed support [-H,H]. Endpoint
samples are intersected with these proved supports. Exact integer sums and
sums of squares, and an upward rational square root, determine all statistical
endpoints. No Gaussian approximation, clipped path gain, optional resampling,
or sample-size extension after seeing signs is permitted.

For each paired interval the predeclared full-width target and two-sided
policy-cost equivalence margin are separately 1/256. Passing width alone is
not equivalence; equivalence requires the entire interval within (-1/256,1/256).
Strict ordering, noninferiority, unresolved cases and failed precision targets
are all retained. These are normalized loss units, not calibrated currency.
A replacement-fee frontier is derived for every pair and for every monetary
scale, declared deployment count and compute charge, without estimating those
prices from processor seconds.

## Independent arithmetic and resources

The production evaluator uses binary64 outward interval operations. A separate
implementation uses Python-integer interval endpoints on a 48-bit dyadic grid,
with explicit floor/ceiling after every nonexact multiplication and division.
It shares no floating interval or economic evaluation routines with the first.
Both implementations re-evaluate every path and acquisition rectangle. Their
intervals must overlap; the reported enclosure is their hull intersected with
the primitive support. The full fixed-point arrays and bin indices are stored.
An additional exact-Fraction midpoint check covers 512 predetermined rows
per controller, selected independently of cost outcomes. These are arithmetic
regressions, not new independent economic observations. This is independent
full-bin coverage of the NEW two-date calculation, not a claim to have rerun
the inherited eight-million-query vector tree.

The new experiment is one complete five-controller evaluation service.
Parent time includes process launch, imports, reading and hashing the original
controllers, rectangle preparation, both complete interval evaluators, exact
checks, inference, compressed output and shutdown. Phase clocks, CPU affinity,
frequency/governor availability, peak RSS and operation counts are separately
recorded. This is an inference-work account, not a cold-start generator
competition. Prior construction clocks are reported separately, not retimed.

## Release conditions

Commit these ordinary sources and a SHA-256 freeze before execution. Preserve
all failure records and stop on arithmetic disagreement. Run all inherited
formal/numerical suites, the R73 exact construction replay, the complete new
cost replay and new theorem/interval regressions. Compile four ordinary-source
reading documents, preserve all inherited active section bytes and labels,
and rebuild from a clean archive including transitive source and result inputs.
The new scientific service is not rerun or retimed in the publication build.
Visual and automated PDF checks are separately identified; a missing visual
inspection may not be labeled passed. Old review/revision branches are not
changed. Only the new R77 branches receive non-forced commits.
