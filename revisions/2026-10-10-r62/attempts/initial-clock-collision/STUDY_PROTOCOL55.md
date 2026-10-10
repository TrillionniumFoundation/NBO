# R55 prospective execution protocol — frozen before production

## Scope and provenance

This is a new execution responding to the R54 report at
`adf1256cff9cde365246a3db2dac90c72fda3b13`. The manuscript baseline is
`00e837adb431f4d4b5248fc6d5ff1fc927dd3b65`. R53 and R54 observations remain
unchanged and are not counted as new data. The title remains Neural Bellman
Operators. Correctness development uses disjoint tiny tasks, seeds and sample
sizes. Production services must verify `audit/SOURCE_FREEZE55.json` before
running. No production outcome may change these declared budgets or targets.

## Original economic law

Use the existing scaled cyclic nonlinear investment primitives, stage price
p=1, discount 15/16, state [0,1]^d, state-dependent action capacity, and common
uniform innovation on [-1/32,1/32] with alternating signs. Extend the existing
coordinate formula, without altering its coefficients, to even dimension 8.
The domain remains invariant: drift without action is in [1/16,11/16],
feasible action is at most 1/4, exposure is at most 1/2, and noise magnitude is
at most 1/32. Cost support is the same dimension-normalized bound used in R54.
Tasks are (d,T)=(2,2),(4,4),(8,6). These are theoretical, uncalibrated economies.

## Separate from-primitives first-attainment services

The expected-cost targets are 9/10 and 49/50 of the expected cost of the
installed zero-investment policy under the original uniform initial law.
They ask for 10% and 2% cost reductions, not chosen post hoc cost endpoints.
Every target has a separate process and inference account. The signed stopping
estimand is J(policy)-q J(zero), not a plug-in ratio of estimated means.

Generators are trained single-hidden-layer ReLU Bellman regression,
quadratic fitted value iteration, and ExtraTrees fitted value iteration.
The d=2 task additionally includes the original compiled-witness and tensor-FVI
frontends. The original constructors use their own future labels; fitted
frontends also use their own subsequent-date critic. No pretrained checkpoints
are loaded free of charge. None of the trained objects is an exact encoding of
an inherited min-plus policy. ReLU hidden and output weights are fitted.

There are two construction stages: (training rows, acquired leaves, innovation
bins)=(256,32,4),(1024,128,8). ReLU width is 32 with 120 full-batch Adam steps
and a final ridge output fit; coefficients are quantized to 24 binary fractional
bits. ExtraTrees uses 16 trees, depth at most 8, minimum leaf size 3, one worker.
Both use the 17-action training menu. The two original d=2 frontends use N=8,16,
K=4,M=4 at the two stages. All training rows, pilots, parameters and raw models
are charged and retained. Trees are integrated by enclosing noise bins during
verification; the one-hidden-layer ReLU and quadratic expectations are analytic.
Training may use approximate labels. No convergence of training is assumed.

A generator-independent dyadic binary partition supplies acquired observations.
Its local splits depend on the declared geometric score and seed 551, and are
nested between stages. It is not a tensor product. Each action is constant on
a leaf and downward-quantized at spacing 1/4096 using the whole-leaf lower
capacity. The first incumbent is zero investment. On the second partition the
previous accepted policy is transferred exactly to its child leaves.

Each stage executes one complete simultaneous safe sweep against that stage's
old incumbent. Candidates are the nine common robust actions and the generator's
one proposed action. Eight contiguous action intervals cover all continuous
feasible actions. A backward residual/value cache encloses the old policy;
the proposed action is adopted only at a strict negative whole-leaf advantage
upper endpoint. This is a full all-date sweep, not an asserted exact T-pass
solution. No change is forced when its safety is unresolved.

After each sweep the service samples its own interval paths at cumulative
looks 4096,16384,65536. A nonpositive upper endpoint for J(policy)-q J(zero)
returns the policy immediately. A strictly positive lower endpoint ends that
stage's inference and moves to the next construction stage. Otherwise another
look is drawn. The last unsuccessful stage returns `budget_exhausted` with its
safe incumbent, not an impossibility claim. No later pass or inference is run
after success. Every attempted stage, inference look and failed target is kept.

## Statistical account and economic reporting

Forty-bit initial-state and innovation cells enclose the original continuous
law. The last innovation is integrated analytically. The inherited bounded
empirical-Bernstein formula, with its rounded-moment account, is used with
logarithm upper bound 14, family limit 2048 and total error 1/100. At most
(5+3+3)*2 targets*3 repetitions*2 stages*3 looks*3 estimands=1188 intervals
are produced. Exact rational arithmetic verifies exp(14)>4*2048/(1/100).
Cost, target contrast and own-incumbent gain are the three estimands. Negative
pathwise gains are retained. Common streams across methods and repeated seeds
do not imply independent policy observations; the union account does not
require them. New stages use fresh streams independent of the current policy.

Report every target attainment or budget exhaustion, pass, actual cost and gain
interval, verification gap, residual widths, candidate-enclosure/continuous-cover
components, membership comparisons, actor ambiguity, serialized bytes, memory,
construction, verification and own inference clocks. The two decomposition
components add cellwise to U-L; their maxima need not add to the maximum gap.
They are certificate bookkeeping, not separately identified causal errors.

The economic interpretation is explicit: a gain interval [l,u] supports a
replacement charge tau<l, and rejects a charge tau>u, in the normalized units.
No empirical fee calibration or universal neural dominance is presumed.

## Timing and repetition

Three isolated sequential processes reproduce each method/task/target with
identical training and inference seeds. CPU affinity is fixed to one available
core and OMP, OpenBLAS and MKL threads to one. Record governor availability and
state that clock frequency is not controlled. The driver records whole-process
wall time including imports and output; the service records internal components
through durable outputs. Report min/median/max and deterministic identity checks.
These are timing repetitions, not independent neural training draws or a
population of economic tasks. Different task cohorts may run on separate runners;
no clock comparison across machines is interpreted as a controlled ranking.

## Learned-null inference study

For dimensions 2,4,8 and seeds 0,1,2, fit a normalized direction from 256 paired
transition observations by projecting the first coordinate off the fitted
action-exposure vector. Quantize that direction to 24 binary fractional bits.
Use separate validation samples N=512,4096,32768 to form simultaneous coordinate
confidence intervals for unknown action exposure B in [0,1]^d. Noise is bounded,
additive and action invariant; its law and nonlinear drift remain known. This
is a structured unknown-parameter problem, not arbitrary unknown-kernel inference.

The confidence half-width is (1/2)*sqrt(14/(2N)), plus verified arithmetic and
forty-bit bin allowances. With 27 boxes, at most 8 coordinates, and two tails,
27*8*2*exp(-14)<1/200. Confidence in all coordinates controls every data-dependent
linear projection. The robust bound is |M| sup_{B in box}|v'B| |a-b|. The full
critic advantage also encloses the same uncertain B; neither the nuisance nor
the remaining continuation is evaluated at an unjustified true-parameter oracle.

Use 64 acquired leaves and amplitudes 1,16,4096 in all 81 cases. Keep all corrected
and plug-in/false-null decisions, all validation boxes including any noncoverage,
and independent true-model postchecks. The corrected gate never sees the simulator's
true exposure. A false-null action is classified harmful only when its true
advantage lower endpoint is positive. These repeated cell cases are not independent
expected-policy-cost observations. The two new inference families jointly have
error at most 1/100+1/200 by a union bound.

## Publication and changes

Record every execution failure rather than silently replacing it. A correctness
fix after production starts requires a new frozen version and preservation of the
failed execution. Manuscript edits do not modify frozen scientific files. Build
and replay are offline and do not create new observations. Historical figures,
negative results and proofs are preserved in the complete editions and companion.
