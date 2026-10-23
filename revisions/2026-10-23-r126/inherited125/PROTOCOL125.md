# R125 prospective deterministic original-economy study

## Identity and independence

This study belongs only to revision R125. Its protocol, complete scientific
code, public frozen dependencies, all 56 acquired actor files, and deterministic
state design must be committed and read back from the new isolated remote
revision branch before any original economic evaluation. `SOURCE_FREEZE125.json`
enumerates those bytes. `BOUNDARIES125.json` records the actual F125 commit and
remote readback; all economic entry points enforce the gate. No outcome is
available when this protocol is frozen.

The original continuous-risk investment economy, the actual implemented future
controller, the fixed M121 actors, and their original acquisition bills remain
unchanged. The actor commit is
`796c5f2badf68b051ac6c144884c0e61b87faf5e`. Public dependency bytes are verified
against the R124B source manifest, source commit
`47135d84683661857e8469fc092251a870b7d3dc`; this is only a verified source import.
No R124B state, output, or unpublished result is imported. R123 and live R124B
are separate research identities and are neither rerun nor completed here.

## Economic object and complete census

The state is exactly two dimensional. The four preselected dyadic states, in
order, are `(1/4,1/4)`, `(1/4,3/4)`, `(3/4,1/4)`, `(3/4,3/4)`. This is a complete
deterministic census of these four named states, not a random sample or a
population estimate. It is not selected after evaluating economic outcomes.
Both original risk levels, 1/2 and 3/4, are included.

The original stage cost, transition, capacity, uniform continuous shock, nested
upper-cost AVaR, beta=15/16, and constrained terminal optimization are unchanged.
The target is the original optimized-future action cost q, with the actually
implemented future-controller cost J satisfying q<=J<=q+delta,
delta=15/2^24. No derivatives of that controller error are assumed. Every deployed
action must satisfy original regret <=1/256 and absolute J-interval width
<=1/8192. A separately reported, stronger original-regret target is 1/65536;
ordinary service qualification never counts as success at this stronger target.

All 56 actor files are included: two risks, budgets 5 and 9, seven representations
(quadratic, ReLU, matched ordinary hinge, spline, degree-two polynomial,
degree-three polynomial, grid), and both value and marginal fitting losses.
ReLU and hinge have matched features, information, and realized actor decisions.
Two original-model online controls are also included. Each of these 58 actor or
online cohorts is evaluated by all four services below. Two additional original
uniform-action DP cohorts give 234 service cohorts and 936 primary decisions.

## Services and prospective stopping rules

All four services begin with a separately executed, fully charged, strong R123
`fused` service, including its original actor/online fallback, every qualification
attempt, all already paid supports and rejected finite-menu proposals. The
returned full `initial_support_certificates` ledger is retained. No service
receives another service's paid evaluations without charging them.

1. `fused_control` returns that completed strong original service.
2. `warm_adaptive` initializes an original-q optimizer bracket from all inherited
   derivative envelopes and uses fresh midpoint queries with adaptive precision.
3. `cold_adaptive` starts at the full feasible original action interval and uses
   the same adaptive rule, while still paying the identical completed prefix.
4. `warm_fixed512` uses the warm bracket and one 512-bin query per midpoint.

For adaptive services the risk-bin sequence is exactly 32,64,128,256,512,1024,2048
at each new action center. At most eight new action centers are attempted.
Midpoints are rounded to the inherited feasible 30-bit action lattice; the
actual rounding error is included in contraction checks. An original-gradient
interval [glo,ghi] is recovered from each original quadratic support and the
proved action smoothness constant. Positive lower derivative shrinks the right
endpoint; negative upper derivative shrinks the left; a straddling interval is
intersected with [a-ghi/2,a-glo/2]. Refinement stops when this certifies halving
(including the recorded action-rounding allowance), or a selected action meets
the stronger target. Failure to contract at maximum precision, empty-bracket
errors, lattice resolution, and budget exhaustion are explicit outcomes.

Every new query contributes `2*bins+1` requested terminal midpoint/endpoint
contexts. The enhancement cap is 32,768 requested contexts per decision; it is
checked before starting a query. This is a hard acquisition accounting unit,
not a substitute for actual terminal iterations, risk sorts, all original
operation counters, or complete wall time, which are also recorded. All coarse
queries discarded by later refinement remain charged. The original prefix is
additional and is never hidden by this enhancement cap.

The service recomputes exact rational original-action support and derivative
envelopes using every paid query. A new action replaces the completed prefix
only if its original regret and width qualify and an exact original contrast
plus delta is strictly negative; the contrast is intersected with valid
original endpoint-level bounds. It is chosen by largest certified strict gain,
then smaller action. A later failure retains the last accepted safe action.
An already strong-target-qualified prefix terminates immediately. A strict safe
improvement that misses the stronger target remains an improvement with target
failure, without changing the target after observation.

`grid33` is a fresh conventional original-model action-grid DP baseline. It
evaluates all 33 rounded actions A*i/32 at 128 bins, retains every support and
all-action lower bound, and selects the qualifying action with smallest original
J upper endpoint. If the stronger target fails, it refines the initially best
upper-value action at 256,512,1024,2048 bins subject to the same 32,768-context cap.
If no grid action qualifies under the original service requirements, it pays a
complete original online fused fallback. Its runtime and operation ledger
include the whole grid, all discarded candidates, and any fallback.

## Timing, costs, and economically priced adoption

After the primary census, exactly three serial complete timing processes run
every one of the 234 services on the first fixed state `(1/4,1/4)`. Cohort order
is rotated by 13*r for r=0,1,2. This produces 702 timed decisions. One-thread
BLAS/OpenMP settings are fixed. No timing is dropped or replaced. Exact action,
certificate, stopping reason and operation-count identity with the primary
first-state decision is required. The host is shared and frequency/load are
uncontrolled; minima and maxima of these three observations are descriptive
timing brackets, not statistical confidence intervals or machine-independent
performance guarantees.

Both whole child and parent process clocks are saved. The reporting service
allocates each parent residual over all 234 cohorts, in addition to measured
per-cohort load, full service, output and bookkeeping costs. Historical actor
acquisition, label generation, training, fitted-model audit, and required parent
ReLU cost for hinge are imported from their unchanged published measured
allocation ledger. Those are historical component allocations, not newly
observed standalone process times. Every refused candidate and extra precision
level is included. New verification and independent economics are charged in the
research ledger separately. Missing historical interrupted process clocks remain
unknown; no complete all-history research bill is fabricated.

Four-state economic summaries are separate from first-state timing. On the
first-state workload only, report sufficient and optimistic price regions for
each ReLU service against every traditional service at the same risk, using
cost J + lambda*(complete per-decision seconds + acquisition/N). N is fixed at
1,32,1000,1,000,000; lambda ranges over all nonnegative values and is solved by
exact linear-inequality intersections. Sufficient comparisons use own upper
cost/time versus competitor lower cost/time; optimistic outer comparisons use
the converse. Empty regions and traditional wins are retained. Equality endpoints
of sufficient regions are excluded. There is no neural-specific advantage claim
from shared hinge geometry or from a different economic objective.

## Independent evidence and failure preservation

`verify125.py` checks the full census, feasible actions, original regret and width,
declared budgets, exact recovered gradients, certified bracket contractions,
strict acceptance algebra, all matched ReLU/hinge output identities, and all
three timing replications. This is exact saved-algebra replay, not independent
economic evaluation.

`independent125.py` imports only the published rational `independent94.py`
economic primitives through the frozen standard-library-only `exact121.py`
adapter. All distinct final actions and completed-prefix actions are independently
evaluated. Every action receives an 8-bin original continuous-law evaluation;
keys are processed in sorted hash order. Terminal bisection budget is 32.
At levels 32 and 128, refine each key involved in an unresolved interval
containment or accepted-gain check. The total audit cap is 65,536 terminal
contexts, checked before each refinement; all first-level keys must fit, else
the audit fails rather than silently samples a subset. Every terminal witness,
continuous-risk primal/dual identity, original value, exact all-action lower
bound, actual bisection count, and evaluation time is saved. Independent interval
containment and claimed strict gains must be distinguished from unresolved
checks at the maximum precision or global cap. Disjoint intervals or an exact
opposite gain bound are contradictions and cause failure.

`fixtures125.py` verifies exact rational support-complete interpolation examples:
a strict original-action contrast improvement when a previously omitted paid
support is retained; an inconsistent payload whose stored node values all lie
above an obstacle but whose between-node values violate it; finite-box dual
residual correction; and constrained optimizer brackets including boundaries.
The strict witness has reduced contrast upper bound -1/4 and full-support bound
-5/8, with matching explicit rational quadratic witnesses. Cheap direct support
evaluation already attains that endpoint improvement; no additional computational
or neural-specific superiority is claimed. These mathematical fixtures do not
replace the original-economy experiment, and the production services in this
census do not implement the new support-complete conic solver.

All results use exclusive attempt directories. Failed imports, compilation,
execution, serialization, resource failures and interrupted processes remain
recorded with partial outputs and elapsed time. Scientific source changes after
F125 require an explicit new public correction boundary; they are never called
the original frozen experiment. Reporting-only adapters must disclose their
scope and preserve the original raw data. No empirical pilot is allowed before
the first source freeze. Static compilation, import checks, and non-economic
serialization checks may be performed and recorded before that boundary.
