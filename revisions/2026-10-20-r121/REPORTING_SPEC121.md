# R121 prospective statistical and economic reporting specification

This file is part of source/protocol freeze F, before acquisition, actor freeze
M, state freeze D and all R121 outcomes. The single new 64-row sample is the
population unit. Its law is the product uniform distribution on the two
40-bit initial-state coordinates, conditional on the stated entropy assumption.
The economic innovation law remains the original continuous uniform law.

## Complete treatment census and outcomes

The two risks each have 28 stored policies (budgets 5 and 9, seven families,
VALUE and MARGINAL) and one online original-model policy. Every one of the 58
cells uses all 64 new states. Report all 3,712 primary rows and five fresh
serial 32-row timing processes (9,280 timing rows), including rejections,
refinement, exact fallback, roots, proposal candidates and adverse outcomes.
The first proposal and the final deployed action are both independently
evaluated. Final actions qualify at regret target tau=1/256 and original value
interval-width target 1/8192. The deterministic total fallback and its proved
primitive constants supply an all-state service, not just sample qualification.
Recoverable numerical proposal/certificate failures on valid frozen inputs
retain their attempted work and enter the same exact fallback. If no feasible
raw proposal was returned, its field is null and that fact is counted; no raw
action or diagnostic is invented. Such a cell's raw-proposal sample aggregate
is marked unavailable, while all its actual final policies remain evaluated.
Source, domain, corruption and infrastructure failures abort the attempt.

For each cell report original objective intervals; original optimal-value and
policy-regret intervals; original action-error upper bounds from curvature
two; raw-proposal regret and changed-action counts; first-rejection counts;
all qualification attempts; bound compatibility; actual acquisition, fitting,
optimization-audit, model-loading, inference and complete-service costs;
operation counters, memory, model bytes and all five distinct clocks. A bound
on action error is labelled a bound, not an observed exact action error.

The 28 paired treatment contrasts compare MARGINAL with VALUE within the same
risk, family and acquisition budget. Gain means original cost under VALUE
minus original cost under MARGINAL. It can be adverse. Each completed policy
has regret in [0,tau], hence the gain support is [-tau,tau]. Identical original
policy keys have exactly zero paired gain. No nonnegative safety clipping from
the older R120 experiment is used.

## A fixed joint 95 percent population family

All actors and row-local services are fixed before the independent sample.
The following family uses a union bound, without assuming independence across
risks, methods, losses, events or timing processes:

| Quantity | Number | Failure allocated to each |
|---|---:|---:|
| Two-sided mean original optimal value | 2 | 1/200 |
| Two-sided mean completed-policy regret | 58 | 1/5800 |
| Two-sided mean signed MARGINAL gain | 28 | 1/2800 |
| One-sided probability of gain at least 2^-20 or 2^-16, or loss at least either threshold | 112 | 1/11200 |
| One-sided first-rejection probability endpoints | 116 | 1/11600 |

The total is exactly 1/20. Interval-valued observations use the sample average
of their lower and upper endpoints. The regret Hoeffding radius is
35*tau/128; the signed-gain radius is 35*tau/64. Their exponent is 1225/128.
An exact degree-20 positive Taylor lower bound for its exponential exceeds
11600, proving both stated two-sided error budgets without rounded logarithms.

On the invariant original state/action domain, S <= 49/32, g <= 37/16 and
h <= 5/64. Therefore V1 <= 967/256 and the root original optimal value lies
in [0,K], K=21097/4096. Its Hoeffding radius is 7*K/32; exponent 49/8 has an
exact degree-20 exponential lower bound exceeding 400. Add the simultaneous
optimal-value and regret intervals to obtain population original-policy value
intervals, intersected with [0,K+tau]. These conservative bounds do not assert
a practically precise population objective level from 64 observations.

Threshold probability lower bounds count only independently certified events:
gain lower endpoint at least the positive threshold, or gain upper endpoint
at most its negative. Exact Clopper--Pearson lower inversions use 48 rational
bisections. First-rejection rates use lower inversion at k and one minus lower
inversion at 64-k. Raw counts and every endpoint remain available. No threshold,
tail allocation, favorable subgroup or sample size is selected after outcomes.
No timing repeat, risk node or identical hinge encoding creates new sample units.

## Cost accounting and adoption conditions

Each budget has its own actually executed original-model label acquisition.
Within it, each standalone representation is charged the complete shared
information bundle and its own fitting, serialization and required training
certificate costs. The hinge readout is the equal-feature control: its identity
with the ReLU readout is explicit and it receives the complete corresponding
readout/label charge. It is not falsely counted as independent neural training.
All failed or rejected fits and actions, loading, original-law certification,
fallback, refinement and full per-state service costs are retained. Shared
process overhead has an explicit allocation; unallocated experimental/research
overhead remains in the total research ledger and is not silently discarded.

Report acquisition and service cost frontiers at deployed volumes
N in {64,256,1024,16384}. A primary scenario uses the complete 64-row measured
service with its matching 64-row economic intervals. Each of five timing
scenarios uses its own 32-row clock and the matching first-32 economic intervals.
There is no favorable-clock selection, new timing, or mismatched clock/economic
cohort. Repeated clocks are descriptive hardware scenarios, not population
runtime confidence intervals. Frequency and external load are recorded as
observed and are not asserted controlled.

For a cost-minimizing policy m, the scenario criterion is N*J_m + p*C_m(N),
where p>=0 is a stated price in original objective units per measured second.
Report sufficient and unresolved price intervals against the complete
conventional menu (quadratic, equal-feature hinge, cubic spline, polynomial
degrees two and three, multilinear dynamic-programming grid and online
semi-analytic original-model control, across both budgets and losses). Each
pair uses original-objective difference bounds and its complete cost difference.
An empty sufficient region is reported as empty. A nonempty unresolved region
is not labelled adoption. No calibrated money price, empirical welfare gain or
neural-specific representational superiority follows from these conditional
comparisons. The same-information within-budget comparison is also retained.

## Retention and limits

Report finite-node LP and value-fit primal/dual gaps separately from continuum
action-control hypotheses and observed original policy performance. Any
unresolved global feature-cover bound remains unresolved; it does not invalidate
or replace the separate original-model service certificate. Budget 5 versus 9
measures actual information/feature and cost scaling in this two-state model;
it is not evidence of state-dimension, horizon, or innovation-dimension scaling.
R120 outcomes and all earlier negative results retain their old identities and
are never substituted for these new rows. Scientific failures remain immutable.
