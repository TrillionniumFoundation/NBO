# R82 deterministic optimizer-sublevel transfer protocol

The controlling advisory report is the R67 report dated 11 October 2026,
commit `4b27b56f4514f6c1d77b69fe707f7202f8b06b19`. The manuscript baseline is
R81, commit `c411bfb2badac2981f001f4c84d99c8c3c306c5e`. No original model,
controller, random stream, confidence interval, or historical service clock is
changed. This study is deterministic verification, not a new statistical or
training experiment.

## Fixed objects and complete scope

Use all four calibrated R80 constructions: ReLU and Bernstein, at n=8 and n=16.
The terminal actor, robust 33-action menus, initial uniform law, opposite-signed
uniform innovations, investment costs and discount factors are those of R80.
For each construction fix the attained terminal-label qualification objective U.
Study every coefficient vector with F(theta) <= U + epsilon, separately for
epsilon = 0, 1/65536 and 1/4096. The same coefficient vector is used across
initial cells. Exact and epsilon-optimal fits are included because min F <= U.
No guarantee for arbitrary inaccurate fits or trained hidden features is inferred.

Retain the reference action and every alternative whose exact R80 switch dual
lower bound D is <= U+epsilon. Equality is retained. All 20,480 dual constraints
are independently checked by the existing R81 verifier during the full build.
The maximum tolerance admits 976 alternatives across the four constructions;
all of them are evaluated, including coarse ReLU cells with uninformative duals.
The exact enumeration and source hashes must agree before numerical evaluation.

## Deterministic integration and error account

Use the four complete dyadic rungs (r,q) = (2,8), (4,16), (8,32), (16,64).
Here r subdivides each side of an initial acquisition cell and q partitions the
first uniform innovation. The last innovation is analytically integrated from
the original polynomial and invariant-shortage identities, not omitted or
replaced by its mean without the expectation correction.

Each possible alternative b is compared with the reference action a on each
whole subbox, followed by the same frozen terminal actor. Binary64 centered
differences and a separately implemented integer-directed expanded polynomial
both enclose the complete paired cost. The actor lookup includes every crossed
terminal acquisition cell. All endpoint arrays have r*r*q entries per action.
The published bin interval is the hull of both implementations, intersected
with the proved signed support [-21097/4096,21097/4096]. Disjoint arithmetic
intervals stop the calculation and create an explicit disagreement record.

Integrate lower and upper endpoints with exact equal probabilities and Python
integer sums. Retain these sums, denominators, full endpoint-stream hashes,
work counts and four independently evaluated rational midpoint checks per
pair/rung. Midpoint tests are regression evidence, not the enclosure proof.
Intersect independently valid integral bands across rungs; do not intersect
point values as though they were whole-bin information. No residual numerical
width is called a sampling standard error.

## Uniform policy-cost transfer

For each initial cell take the smallest lower and largest upper integrated cost
difference among its possible actions, including the exact reference difference
zero. Weight by the original cell probability 1/n^2. This gives a directed band
[L,U] for every policy induced by the fixed optimization sublevel. Record the
old H times uncertified initial mass bound beside it, and verify containment.
The independent per-cell action sets are a relaxation: their extrema need not
be attainable by one common coefficient vector. No sharpness claim for the
joint optimizer class is made.

For every pair of calibrated classes and every tolerance/rung, transform the
existing simultaneous attained-controller interval [l,u] into
[l+L_first-U_second, u+U_first-L_second]. Report every result, whether positive,
negative, equivalent at the old 1/256 margin, or unresolved. Also report the
final-rung gains against each method's own old controller and the zero action
controller. These deterministic transfers all hold on the existing R80 event;
they create no new IID rows or multiple-testing budget.

## Development and execution boundary

Before freezing, small deterministic pilot calculations checked both arithmetic
implementations and the usefulness of directed cancellation. Pilots included
four of the 976 possible actions and three low-resolution rungs for the n=16
classes at epsilon=1/65536. They informed the final dyadic refinement level.
Consequently this is not described as a prospectively selected economic
experiment or an untouched holdout test. The original R80 cost observations
remain frozen and no new policies are fitted or retrospectively chosen for
sampling. The designated full execution begins only after SOURCE_FREEZE82.json
binds these code files, this protocol and every construction/barrier/cost input.

Execution does not overwrite a results directory. Full replay recomputes every
paired subbox and every endpoint digest with both implementations, retaining the
original scientific clocks. Wall time and memory are recorded as verification
costs, not as evidence that one generator is faster. Frequency is recorded when
available and is not claimed to be locked. An independent large vector-tree
reimplementation, broader trained vector benchmark and empirical monetary
calibration are not provided by this deterministic two-date calculation.
