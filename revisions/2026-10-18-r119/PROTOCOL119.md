# R119 original-investment active-tail experiment: prospective execution protocol

This file is committed with the actual executable source before any R119 primary
acquisition, catalogue, reference, or timing execution. Its source commit is
recorded by `NBO_SOURCE119` and checked against Git content, not accepted merely
because a string resembles a SHA. R110 is the complete author-source baseline;
the controlling persisted R97 advisory reviewed R97. Their scientific identities
are fixed in `REVISION_BOUNDARY119.md`. R117/R118 reproductions have already run
under the separate custody commit 54512c9c7fcdc75d97ad37d20b8b61f22356a953. Their
outcomes informed this new design and are not new, independent R119 observations.

## 1. Question and model identity

The question is whether localizing a feasible upper-tail density, certifying its
suboptimality, and allocating integration to that density reduces the complete
cost of an original Bellman decision at unchanged economic accuracy. This is a
representation-neutral algorithm inside Neural Bellman Operators. It is not a
claim that ReLU alone can represent the relevant geometry, nor a prospective
experiment on action-aware fitting: the inherited acquisition objective is
unchanged. The new deterministic information theorem and the practical
strong-convexity certificate have different oracle accounts.

The primary economy is exactly the retained two-date nonlinear investment model:
state [0,1]^2; original capacity 1/8+mean(x)/8; original transition, stage and
terminal costs in frozen108/code/investment94.py; beta=15/16; innovations uniform
on [-1/32,1/32]; separate nested AVaR levels alpha=1/2 and 3/4. Terminal decisions
use the same complete observed-state controller, observation precision, and
2^-20 error allowance. The compiled optimal-continuation oracle is a certificate
construction primitive, not a replacement deployed terminal policy. Initial
actions remain in the original interval. Every returned service must qualify
original-policy loss <=1/256 and policy enclosure width <=1/8192. A failure is
recorded, never counted as a successful decision.

## 2. Information, acquisition, arms and resource account

Run a fresh acquisition on the exact deterministic 16x16 grid for each risk
level: 256 original-model terminal labels per risk. The same label bytes go to
quadratic, ReLU, its conventional hinge encoding, spline, degree-two and
degree-three polynomials, and grid interpolation. The eighth arm is the online
semi-analytic Bellman/continuous-action control. All inherited candidate fits,
rejected candidates, independent matrix/active-face QR audits, serialization,
deserialization, and label acquisition execute and are recorded. No model payload
from R117 or another episode is used. The conventional hinge is an exactly
equivalent encoding and receives the full standalone ReLU acquisition charge.
The grid arm has 256 nodes; its different storage budget is reported rather than
described as a rank-matched learned model. The archived original DP and analytic
comparisons remain part of the paper, with their own original identities.

The primary intervention holds each arm's fitted actor, feasible actions and
information fixed. Three services receive each same candidate:

1. `compiled`: frozen R117 `precision117.service(ladder=False)`, the retained
   original 128-bin compiled service including repair/refinement/fallback.
2. `geometric`: the unchanged frozen R117 8,16,32,64,128-bin initial schedule,
   then that same complete fallback.
3. `active-tail`: propose a cut using both endpoints and exactly six floating
   bisection updates, take the final bracket midpoint and round it to 32 binary
   places. Floating signs provide no certificate authority. Two outward endpoint
   value intervals and the original innovation curvature 181/64 pay for the
   cut's true AVaR deficit by constrained quadratic minimization. Integrate both
   selected tails with 2,4,8,16,32,64 cells per tail until qualification; otherwise
   execute the full-support 128-bin certificate and unchanged complete repair,
   refinement and rational fallback. Cache only the cut bound for the identical
   state/action/risk, with lookups recorded. Evaluate and charge zero-length tail
   arrays too. The sharper skipped-tail exact-information theorem is not the
   measured vector implementation's cost.

All services pay their own proposal, certification, rejected attempts, repairs,
refinements, inference and complete decision time. No trial is removed for being
slow or unsuccessful. Full acquisition cost, standalone per-arm cost and the
shared one-time campaign cost are separately available. Counters include the
terminal compiler, floating proposals, outward point values, density search,
sorting, all-action witnesses and cached lookups. Benchmark references, audits,
source verification and process startup are separate paid experiment costs, not
silently attributed to deployment or made free.

## 3. Fixed primary catalogue and timing

Use every state of represent108.grid(12), in its existing order: 144 states.
Both risk levels, all eight arms and all three services produce 6,912 primary
decisions. No primary grid, sample, parameter, tolerance, method or evaluation
criterion will be changed after outcomes are inspected. This deterministic
catalogue carries no population confidence interval or random-sample claim.

For timing, use its first 32 states in seven sequential fresh Python processes.
Each process runs both risks and all arms; service order rotates deterministically
by (repeat+risk_index+arm_index) modulo three. There are 10,752 timing decisions.
No warm-up or discarded repeat is permitted. No other controlled scientific
campaign runs concurrently. All seven clocks and process wall times are kept;
report median and observed minimum/maximum, not an iid timing confidence interval.
Record CPU, versions, thread environment and maximum process RSS; external host
load and CPU frequency are not controlled. Timing comparisons are descriptive
on this host. If a source defect aborts a run, retain it and label any amended
source/run as a new attempt; do not re-time merely to improve an outcome.

Set OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1 and MKL_NUM_THREADS=1 for all
current primary, reference and timing processes. The recorded numerical runtime
is Python 3.12 with NumPy 2.3.5 and SciPy 1.17.0; exact minor Python and platform
identities are recorded by the execution receipts.

## 4. Original economic values and decision errors

After all primary decisions, independently of their method-specific certificates,
enumerate every distinct returned action at each original state/risk. Exact
binary equality permits reuse only for that same original policy. Compute a
fresh full-support 1,024-bin original-law certificate, in batches of at most 32.
These references do not use the active-tail routine. All benchmark work is paid.
The enclosure includes the same actual terminal-controller allowance.

For each state/risk, the largest valid all-action lower bound and the smallest
valid policy upper bound bracket the original optimum. Report every method's
original cost interval, policy-regret interval, and certified distance-to-optimal-
action upper bound implied by curvature two. A bound is not a measured exact
regret or action error. Report original-policy contrasts against both other
services. Identical complete policies have exactly zero cost difference; changed
actions receive interval differences and are called improvements only when the
upper cost difference is strictly negative. A narrower certificate does not by
itself constitute policy improvement. Reference inconsistencies fail the audit.

Record separately: first certificate attempt rejected; initial schedule
exhausted; proposed action repaired; final action changed; rational fallback.
The inherited raw `first_rejected` means the 128-bin repair gate, not the first
8-bin or active-tail attempt. Derived tables use explicit names and preserve the
raw field. Every per-attempt record remains available.

Adoption is reported as a conditional resource/economic inequality: acquisition
plus decision-serving cost, and a separately chosen value per economic-loss unit.
Do not invent an economic shadow price, request population, or break-even horizon.
Ranked speed alone and statistical precision alone do not certify neural adoption.

## 5. Independent checks and supporting exact catalogue

`code119/independent_tail119.py` and its separately frozen validation protocol
specify independent Fraction checks of constrained minima, dyadic probability
mass, endpoint cases and original primitive terminal values. They compare
production enclosures with independently reconstructed rational polynomial
primitives and bracketed terminal minimization. Finite checks support code
reliability, while continuum validity rests on the supplement's full proof.
Standard-library record auditing reconstructs all primary and timing bounds and
qualification gates using exact binary rationals, verifies every output hash,
and checks ReLU/hinge policy and certificate identity where they are equal.

A separately labeled exact point-information diagnostic evaluates the active-
tail theorem on a fixed convex piecewise-linear/quadratic catalogue on [-1,1].
Risk levels are 0,1/2,3/4,7/8,15/16,31/32,63/64,255/256; n=8,16,32,64.
All function coefficients, queries, oracle restrictions and independent analytic
integrals are fixed in the validation protocol and executable before execution.
Its exact arithmetic reports actual query counts, original AVaR enclosures and
the tail-uniform bound. It is not a new nonlinear-investment, learned-
representation, randomized, multidimensional-risk or population experiment.

A secondary primitive scaling diagnostic uses d=2,4,8, each with 32 states
x[i,j]=((17*i+11*j+3) mod 64)/64 and both inherited risk levels. For the same
online candidate compare a 128-bin full-support certificate and an eight-cell-
per-tail certificate. Charge the common proposal separately and each certificate
fully. Preserve unqualified cells. This is a one-step certificate/kernel scaling
diagnostic, not a complete learned high-dimensional or longer-horizon tournament.

## 6. Custody, reporting and completion

SOURCE_FREEZE119.json hashes this protocol and every scientific executable and
dependency. Source verification compares actual committed blobs. Outputs go to
a new attempt directory with START, stage logs, machine metadata, intermediate
progress, failure receipts if any, and completion/audit receipts. Existing output
identities cannot be overwritten. Any post-execution presentation code is marked
as derived reporting; it cannot change raw records or primary evaluation rules.

Keep historical R97 adverse results, all R110 complete-policy improvements and
gain-budget costs, R117 negative timing and unresolved precision cells, R118
exact supporting diagnostic, and all independent frozen R98/R100--R118 episodes
under their own identities. New observations supply none of their missing data.
Publication and CI success are claimed only after actual successful execution
with the same source identity. The ambition remains original recursive economic
decisions with learned Bellman operators; unresolved neural-specific superiority,
action-aware acquisition and large economic applications are recorded as research
obligations, not redefined as completed objectives.
