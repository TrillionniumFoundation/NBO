# R120 reporting specification, prepared before outcomes

This is a reporting specification prepared after scientific source freeze
`369d02724cf12ae0e54390b4e7b5f894f703892e` (F) and before this reporting author
has read any new R120 labels, fitted models, sampled states, economic outcomes,
timings, independent values or population results. It does not amend the frozen
experiment. The companion `code120/report120.py` imports no economic solver,
production terminal compiler, neural model or numerical training routine.
Its execution will begin only after the root author confirms the actual output
receipts. Its own source, inputs, runtime, errors and outputs will be bound
separately from F and the primary scientific cost.

## Input scope and completeness

Default input directories are `results120/acquisition-attempt01`,
`states-attempt01`, `primary-attempt01`, `independent-attempt01` and
`stats-attempt01`; actual paths may be supplied explicitly without changing
their scientific contents. The reporter checks the recorded F/M/D identities,
all source hashes, all 4096 primary decision identities, all 4096 independent
comparison identities, all 64 states including possible duplicate draws, the
48 population groups and 192 threshold records, all three timing processes,
and their 6144 decision identities. Every file actually read is SHA-256 bound
before and after reading. Failure and launcher receipts are listed alongside
successful observations; no missing decision, unsuccessful precision level,
timing clock or adverse contrast is silently excluded.

Incomplete scientific inputs do not produce a success table. The reporter
retains an incomplete/failure receipt identifying the absent or contradictory
inputs. A failed report may be repaired as a new reporting attempt with its
earlier prefix preserved; it cannot alter or substitute scientific data.

## Fixed descriptive census

The order is risks 1/2 and 3/4; arms online, quadratic, relu, hinge, spline,
poly2, poly3 and grid; services completed, legacy-safe, paired and direct-refine.
There are 64 primary group rows, each containing all 64 observations.

For every group report independently enclosed original mean policy objective,
mean original regret interval, maximum original regret upper bound, mean and
maximum squared optimal-action-error upper bounds, and upward square-root
bounds for action distance. These are bounds on loss/error, not exact regret
or exact distance to an observed optimal action. Also report the complete
incumbent-to-returned action-change count, accepted steps, original first-actor
rejections, fallback entries, identical-action shortcuts, candidate attempts,
precision attempts, unqualified levels, certified non-improvements and budget
exhaustions. Do not infer a neural advantage from a method also available to a
conventional representation.

Report all 48 service-versus-own-completed gain groups and all 192 threshold
records from the frozen statistics code. Independently reaggregate event
counts, sample-mean bounds and the fixed staircase from the stored independent
comparison rows. Check recorded binomial lower and upper bracket inequalities
with exact integer arithmetic. This is verification of reported statistics,
not a new outcome-selected confidence method or extra economic evaluation.
The simultaneous 19/20 population statement applies to its declared within-arm
gain family. No cross-representation population confidence statement is added.

## Complete comparisons and certificate diagnostics

Within each risk compare every unordered pair of the 32 arm/service groups:
496 comparisons per risk and 992 in total. Form mean original-J differences
row by row, using exact zero when the two actual policy keys coincide and
independent interval subtraction otherwise. Original-regret differences have
the same interval because the same original optimum cancels. Report every
strict positive, strict negative, exact-zero and unresolved sign. All 96
within-arm service comparisons and all 224 same-service arm comparisons remain
identifiable subsets, not selected replacements for the full table.

Check actual ReLU/hinge parameter identity for each risk and all 512 matching
primary action pairs. Report any action disagreement rather than inferring
floating action identity from parameter identity. Compare every one of the
6144 timing actions against its matching primary action and state. Retain all
mismatches with exact identities; a mismatch restricts interpretation of the
clock instead of being replaced by a more favorable repeat.

Reaggregate original-policy interval overlap and both containment directions,
original-optimum feasibility compatibility, and certified gain versus independent
gain upper bounds. These are finite execution checks and are not called an
empirical proof of global certificate reliability or independent authorship.

Read the already recorded paired event payloads to report all mixed-midpoint
upper/lower activity, direct/transfer tail-defect activity, point-row counts,
integer-square-root calls, actual resolutions and rejected candidates. From
the recorded bounds and exact action-cost polynomial identity, additionally
replay whether an accepted action at that resolution would fail the separately
valid convex-only upper comparison, and whether an early rejection would fail
without the transferred incumbent slack. Such counts identify use of the new
bound at the recorded resolution; they do not assert that a later traditional
refinement would fail, or that a counterfactual timing was measured. No original
continuation, risk optimization or terminal primitive is reevaluated.

## Full cost and resource accounting

For all 64 groups display the measured original 64-state cohort time, sum of
singleton service times, cold model load, row/trial recording, remaining cohort
overhead, one-time standalone acquisition charge, complete observed 64-state
cost `(acquisition + cohort time)/64`, and every recorded operation counter.
Keep fitting, fitting audits, all feature-search trials, full common labels,
serialization and conservative unassigned acquisition overhead visible. The
hinge charge includes the ReLU fit and audit in full. Do not sum counters that
measure overlapping work into a fictitious universal query unit.

For each group retain all three raw 32-state timing clocks, their exact
descriptive median/range, model loading, operation counts, memory receipt scope
and process overhead. Clock ratios are formed within the same repetition;
medians are not divided to invent paired observations. No clock is discarded.
Global process high-water RSS is not attributed as a representation's own
peak memory. Actual model payload bytes are reported separately.

The research ledger lists all supplied execution/launcher/failure receipts with
their time scope and nesting, including acquisition, state custody, primary,
timing children, independent validation, statistical analysis, reporting and
available verification receipts. A union of recorded wall-clock intervals is
shown separately from nested component sums, preventing double counting of
timing children inside the primary process. Untimed authoring, remote waits or
future package work are marked as unavailable, not assigned zero cost. Final
package receipts can extend this ledger as a publication derivative.

Construct interval-nondominated sample frontiers for complete observed cost and
original J, and separately for the recorded original-query/resource dimensions.
Dominance requires a nonpositive paired J upper difference, no greater recorded
resource use, and at least one strict comparison. Unresolved nodes remain in the
set; membership is not a proof of true Pareto optimality or population adoption.

## Prespecified adopter-price calculations

In addition to the actual 64-state cost, use the fixed workloads
`B in {1,64,1024,65536}` as explicitly labeled amortization scenarios. With actual
standalone acquisition charge A, repetition-r cohort time T_r and measured cold
load L_r, define

```
C_r(B) = (A + L_r)/B + (T_r - L_r)/32.
```

This preserves all observed operating/cohort overhead and moves only the measured
one-time cold load with the amortization volume. It is an extrapolation from the
recorded 32-state service, not a measured scaling experiment or a latency bound.
All three individual scenarios and their intersection are reported.

For each candidate against its own completed incumbent, and against every
conventional arm/service alternative at the same risk, let `[gL,gU]` enclose the
comparator's sample mean J minus the candidate's. At computing price lambda in
original objective units per second, and recorded extra cost dC, net benefit is
enclosed by `[gL-lambda*dC, gU-lambda*dC]`. Report the exact nonnegative-price
domain on which the lower endpoint is strictly positive, and the domain on
which the upper endpoint is strictly positive. Handle zero/negative dC and
open endpoints exactly; do not divide by a near-zero number and report infinity
as a measured benefit.

The conventional menu contains all seven non-ReLU arms and all four services,
28 alternatives per risk, with only a candidate's identical own label omitted
when relevant. To compare with the best conventional sample outcome at a price,
intersect the candidate's sufficient positive-benefit domains against every
alternative. The corresponding intersection based on upper endpoints means
only that pairwise interval checks do not rule it out; it is not a joint
existence proof. No favorable conventional comparator is selected after results.
Report all-three-clock intersections as robustness within the recorded timing
scenarios, not population timing confidence. These price calculations are
conditional on sample economic intervals, the measured cost scopes and the
declared amortization model; they do not establish out-of-sample adoption.

## Deliverables and manuscript treatment

The reporter produces machine-readable exact-fraction JSON and CSV/TSV tables
for the full census, comparisons, event probabilities, cost components,
operation counters, timing matches, certificate diagnostics, price domains and
input/output identities. It produces `new120/results120.tex` with fixed all-arm
economic, cost and population panels, and `new120/development120_results.tex`
with the complete extended tables and diagnostic interpretation. Full large
comparison tables remain in the development material and machine files; they
do not displace the main economic argument.

Text is generated from observed counts and directions only after completed
receipts are available. Zero changes, broad intervals, an inactive new bound,
conventional wins, neural losses, failed attempts and empty adoption domains
are reported explicitly. Neither a successful report nor a passed execution
check constitutes a favorable scientific comparison.
