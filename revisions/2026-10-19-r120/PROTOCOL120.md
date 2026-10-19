# R120: original-policy refinement with action-dependent continuation comparisons

**Status before the source commit:** this is a prospective protocol. No R120
label acquisition, fitted actor, new random state, economic decision, timing
campaign, or independent original-policy evaluation has been generated. The
actual source commit, actor commit, state commit and execution receipts will be
reported separately. A local filename or draft date is not evidence of a freeze.

## 1. Scientific identity and retained evidence

The study retains the original two-date constrained investment problem, its
continuous innovation law, nested AVaR Bellman objective, and implemented future
controller. It is an author revision of Neural Bellman Operators. The new
intervention changes first-date decisions only when a certificate establishes
a strict improvement in the original policy objective. It does not change the
risk law, fit the evaluation states, or replace the paper with a timing study.

The completed R119 scientific/publication baseline is preserved at its immutable
source and final publication commits, including the original-model source,
R110 paper and numerical work, R111--R118 distinct research episodes, R119
A/B/C campaigns, the independent 983-policy D validation, all unsuccessful
attempts, and all adverse results. In particular, R119 A/B/C services returned
the same actions within each representation; their timing differences were not
economic gains. The quadratic representation beat the ReLU representation in
both original mean objective comparisons independently resolved by R119 D.
The conventional hinge encoding shared the ReLU parameters. No R120 observation
is substituted for those results or for any earlier independent population
protocol, sample commitment, incomplete transfer, or failed run.

R108 already implemented three certified support-gradient policy changes;
R110 added stopping based on a certified ceiling on remaining gain. Those
results are not claimed as new. R120 calls the retained R108 `compiled-safe`
function unchanged as a contemporaneous comparator. The additional mechanism
is a proved action-dependent quadrature enclosure for a difference of original
continuation values. R119 explicitly did not establish convexity of such a
difference. R120 supplies a valid Lipschitz modulus and intersects its bound
with valid separate convex integration bounds. Ordinary continuation-value
training is retained; there is **no action-aware fitting completion claim**.

## 2. Fixed original economy and policy target

The primary dimension is `d=2`, with state in `[0,1]^2`, action
`0 <= a <= A(x)=1/8+mean(x)/8`, discount `beta=15/16`, action cost
`h(a)=a^2+4a^4`, and the original state and terminal costs in
`frozen108/code/investment94.py`. The transition is

```
F_j(x,a,z) = 1/16 + x_j/2 + x_{j+1}/8
             + x_j*(1-x_{j+1})/16 + b_j*a + s_j*z,
b=(1/2,1/4), s=(1,-1), z ~ continuous Uniform[-1/32,1/32].
```

Both nested AVaR levels `alpha=1/2` and `3/4` are retained. They index separate
economic objectives; neither objective is used as evidence of improvement in
the other. The continuation being learned and certified is the original
optimal one-date value `V1*`. The returned two-date policy uses the exact
retained implementation `terminal_controller94.terminal_policy` with downward
**40-bit state observations**. Forty bits is not an optimizer iteration count.
The original uniform future-policy allowance is `epsilon1=2^-20`.

Let `Q*(x,a)=S(x)+h(a)+beta*AVaR(V1*(F(x,a,Z)))` and let `J(x,a)` denote the
same root decision followed by that fixed implemented future controller.
Then `Q*(x,a) <= J(x,a) <= Q*(x,a)+beta*epsilon1`. A pair difference is bounded
with `+/-beta*epsilon1` once. `J` is not asserted to inherit the smoothness or
convexity of `Q*`. Every completed decision retains the original service
requirements `policy loss <= 1/256` and `policy enclosure width <= 1/8192`.
The future decision is the retained controller's singleton evaluation at its
own downward-quantized observation, so this policy target is a fixed function
of the economic state and does not depend on another investor's input batch.

The new mixed-modulus proof used in this execution is restricted to `d=2`.
No `d=4` or `d=8` learned-policy result, state-distribution guarantee or new
modulus is inferred from the present experiment. Higher-dimensional original
models and the retained R119 online scaling evidence remain in the paper;
further policy experiments require their own valid constants and protocol.

## 3. Eight representation/actor arms and common training information

The fixed arms are `online`, `quadratic`, `relu`, `hinge`, `spline`, `poly2`,
`poly3`, and `grid`. They use the unchanged `represent108.fit_all` and
`represent108.proposal` implementations. The online arm evaluates the original
one-date Bellman problem using the conventional analytic terminal compiler and
buys no fitted critic or training label. Every arm can call that same compiler,
original support oracle, original-law certificate and complete fallback.

The seven stored non-online representations receive the identical 256
terminal-value interval labels at the fixed 16-by-16 tensor midpoint grid.
Labels are newly evaluated after the source freeze using
`kernel108.compiled_certificate`; this compiler is common economic information,
not a neural feature. The training target is each interval's midpoint. Both
risk objectives acquire their own original labels and fits. The acquisition
retains all greedy feature-search trials, nonnegative readout fits, rejected
rank-deficient candidates, independent pivoted-QR/active-set numerical fit
audits, rounding, serialization and exact model payloads. There is no new
hyperparameter search or outcome-dependent model selection.

The rank-six quadratic, ReLU and spline fits retain their fixed feature rules.
The full quadratic and cubic polynomial fits and tensor interpolant retain
their stronger, unmatched-size controls; no equal-rank or equal-memory claim
is imposed on them. The conventional hinge encoding uses exactly the fitted
ReLU directions, offsets and coefficients. It is an implementation and
information-equivalence control, not an independently fitted discovery.
Differences caused by actual floating evaluation order, if any, are reported;
parameter identity does not authorize claiming unobserved action identity.

## 4. Four complete services for every arm

Every one of the eight arms runs every service on every retained test state and
both risk levels. The services begin by independently completing the same
retained original-model proposal/certificate/repair procedure. They pay their
own incumbent acquisition and certification costs; a successful incumbent from
another service is not supplied free.

1. **`completed`:** unchanged compiled original service with no optional policy
   improvement. This is each arm's incumbent and original-policy comparison.
2. **`legacy-safe`:** unchanged R108 `complete_service(..., compiled=True,
   safe=True)`. Its three original support proposals use fractions 1, 1/2 and
   1/4, fresh 128-cell whole-support candidate certificates, strict interval
   separation and original qualification. All attempted and rejected work is
   recorded.
3. **`paired`:** the same three support-gradient proposal rules and fractions,
   evaluated sequentially from the current accepted incumbent. The support
   slope is the slope of a feasible global lower witness, not an asserted exact
   derivative of the original Bellman value. Each proposed action is rounded
   down to the inherited 30-bit action mesh and respects the original capacity.
   Candidate acceptance uses the new paired comparison below, at the fixed
   increasing tail-cell ladder `(2,4,8,16,32,64)`. This design holds candidate
   generation fixed relative to the historical control while changing its
   economically aligned information acquisition and acceptance rule.
4. **`direct-refine`:** after completing the arm's incumbent, purchase the
   conventional original root actor at 512 midpoint innovation nodes and 24
   derivative bisections, with no fitted continuation. This is a stronger
   direct numerical proposal, not an exact continuous-risk optimizer. It gets
   the same new paid paired certificate and full resolution ladder. Its online
   arm has no training charge and is the stand-alone strong conventional
   comparator. The other seven arms retain their actual incumbent and training
   costs; their duplicated direct work is not amortized away.

No equality of realized query counts is claimed. The declared controls have
common access to the original economic information and feasible action space.
All actual oracle counts, precision levels and complete costs are reported so
any difference in resources is visible. No neural-specific advantage can be
inferred from a method equally available to conventional representations.

## 5. Original paired comparison and fixed acquisition/stopping rule

For an incumbent `a` and candidate `b`, write
`f_a(z)=V1*(F(x,a,z))`, `D_ab=f_b-f_a`, `R=1/32`, and `t=1-alpha`.
The proved rational constant is

```
M_alpha = 1413/128 + (15/16)*(127/16 + 19625*alpha/(20480*(1-alpha))),
Lip_z(D_ab) <= E_ab = (4/5)*M_alpha*abs(b-a).
```

All constants, separations and bounds are evaluated using termwise-outward
interval arithmetic. This is an original-economy bound, not a fitted or
empirically estimated modulus. A floating candidate tail cut is only a
proposal. The retained six-step cut proposal and 32-bit cut rounding define a
feasible two-tail density. Both actions buy their own original endpoint
residuals at that same cut, yielding nonnegative slacks `kappa_a` and
`kappa_b`. Zero-mass tails are skipped; every positive-mass midpoint and
endpoint for **both actions** is purchased and recorded. Repeated nodes are
paid whenever requested. No cross-state or cross-service scientific cache is
used.

The directly paid incumbent slack is intersected with the additionally proved
action-dependent transfer bound
`(sqrt(kappa_b)+E_ab*sqrt(alpha/(2*(181/64)*(1-alpha))))^2`.
Each square root is bounded above using integer square roots of the exact
binary-rational input, upward rounding to a 40-bit dyadic, and an exact final
Fraction inequality check; no floating square-root enclosure is presumed.
The transfer computation, its two input bounds and actual activity are logged
and charged. At this candidate-selected density it can tighten the lower
difference and rejection test. It does not replace the candidate's directly
paid slack in the upper acceptance test or create an unobserved query saving.

With cell lengths `h_i`, density normalization `2*R*t`, and exact dyadic cell
masses, paired midpoint integration has absolute discretization error at most
`E_ab*sum(h_i^2)/(4*2*R*t)`. Its interval includes the actual terminal point
enclosure widths. Independently, convexity of each `f_a` and `f_b` bounds the
same selected-tail difference by
`[midpoint_lower_b-secant_upper_a, secant_upper_b-midpoint_lower_a]`.
The intersection is valid even though `D_ab` need not be convex.

If this integral intersection is `[L_D,U_D]`, the actual original-policy
difference satisfies

```
J(x,b)-J(x,a) in h(b)-h(a)
  + beta*[L_D-kappa_a-epsilon1, U_D+kappa_b+epsilon1].
```

The common state cost cancels exactly. The action-cost difference is computed
by its polynomial factorization. The same point payload supplies a fresh
candidate policy enclosure, a global original-optimum lower witness and
original qualification. A previously valid all-action optimum lower bound
may be reused; an old action's policy interval may not be reused as the new
action's interval.

At each ladder level, accept a changed candidate only if the original-policy
difference upper bound is strictly negative **and** the fresh candidate meets
both original service tolerances. If the difference lower bound is nonnegative,
reject the candidate without further refinement. Otherwise continue to the
next fixed level. At level 64, any unresolved candidate is rejected and the
qualified incumbent is returned. Exact identical actions have exact zero
difference and purchase no pair density or point payload. Every attempted
level, non-improvement, unqualified candidate, precision exhaustion and
accepted action is retained. The direct proposal follows the same rule.

The new comparison is not promised to terminate favorably for every positive
gain: terminal point width, tail mismatch and the unchanged future allowance
can leave a real improvement unresolved. The experiment reports how often the
action-scaled bound actually tightens the convex bound; it does not credit the
new modulus for acceptances supplied only by the older convex information.

Accepted lower gains are added with outward arithmetic to obtain a certified
nonnegative gain from the completed incumbent. A rejection returns that
incumbent and contributes zero. The original complete service retains its
finite fallback schedule: whole-support refinements through 4096 cells and,
if needed, the original finite rational cover with 1025 actions, 256 shock
cells and at most 80 terminal bisections per context. Its cost can be large.
No small wall-time bound is asserted for entering this fallback. Any exception
fails the attempted campaign closed and is retained, not silently substituted.

## 6. Three distinct immutable boundaries and independent held-out states

The commands are separate so training cannot see the new evaluation states:

1. **F: source/protocol commit.** Publish the actual code, this protocol, the
   independent evaluation/statistics protocol, theory constants and complete
   scientific dependency hashes. Each subsequent command verifies its local
   source bytes against F before importing scientific packages.
2. **M: actor/label commit.** Run `acquire` after F and retain the fixed-grid
   labels, all eight model payloads at each risk, fitting/audit records,
   unsuccessful attempts and `ACQUISITION_MANIFEST120.json`. Publish these
   completed artifacts at M before drawing any new test state.
3. **D: state commit.** The `sample` command first verifies all sixteen actual
   model payloads and the acquisition manifest against M. It then calls
   `os.urandom(640)` once, saving the exact 640 bytes before any economic
   evaluation. For each of 64 rows, two disjoint five-byte big-endian integers
   define exact binary rational coordinates `integer/2^40`. Save and publish
   the entropy, exact coordinates/hex identities and `STATE_MANIFEST120.json`
   at D. The primary command verifies F, M and D before evaluation.

The artifact gates verify their declared kind and embedded generating source F,
not only committed file bytes, and require exactly sixteen risk/arm model
payloads. They also verify the distinct Git ancestor chain F -> M -> D.
Actual remote publication receipts establish when those boundaries were
published; Git ancestry alone is not represented as a wall-clock receipt.

The population is the product discrete uniform law on
`{0,...,2^40-1}/2^40` in two coordinates. It is not silently described as exact
continuous uniform. Each coordinate receives independent operating-system
entropy bytes; a pseudorandom sequence from a finite seed is not being claimed
as independent draws. The same 64 states are used for both risks and every
arm/service. Thus rows are independent, while risk, arm and service comparisons
are paired within rows. This is an evaluation-state population; the original
continuous economic innovation law remains unchanged.

Every complete service is called with exactly **one initial state**. Internal
shock nodes remain vectorized. This is essential because the retained compiler
may fall back for an entire supplied batch: batching distinct held-out states
could make a row's returned action depend on other sampled rows. Immutable
models and row-local service calls make each policy/gain a function of its own
state and the fixed protocol. Global operation counters do not enter decisions.

There is one draw, no replacement sample, no selected subset and no reroll after
seeing outcomes. A source/runtime failure preserves the entire attempt. Any
necessary revised executable is committed and described as such; no prior
failed attempt or inspected data is represented as unseen.

## 7. Primary catalogue, cost accounting and descriptive timing

The primary catalogue contains `64*2*8*4=4096` complete singleton decisions.
All of them are retained. The raw file `records120.jsonl` stores risk, arm,
service, row, exact state/action identity, original policy lower/upper bounds,
original optimum lower bound, qualification, completed incumbent, certified
gain lower bound, action changes, actual singleton service time and actual
per-row oracle counts. Separate `trials120.jsonl` and deterministic-gzip
event streams retain all paid candidates, densities, original point payloads,
precision levels, accepts, rejects, failures and original fallback events.

Acquisition stores total experiment cost and explicit standalone charges. Every
learned arm pays the full common label acquisition and label-recording costs,
its fit, fit audit, serialization and model storage, and the entire measured
unassigned common fitting bookkeeping residual. The hinge arm pays the ReLU
fit/audit in full. Shared acquisition is never divided by the number of arms.
Any bookkeeping conservatism in this allocation is disclosed alongside actual
whole-process time. The online arm pays its actual artifact handling but no
training-label or fitting cost.

For decision service, actual singleton times include scientific audit-event
recording. Each model is loaded afresh for each service cohort; the separately
measured model load, all row/trial serialization and other cohort overhead are
included in the recorded cohort end-to-end clock. Clock components are not
silently omitted or subtracted to manufacture an advantage. Actual process
launch, source/input verification, numerical imports, acquisition, independent
evaluation, statistical analysis and package-validation costs are reported at
their own scope. Expensive validation is not misclassified as free training or
online inference, and is not attributed to only an unfavored representation.

After the primary catalogue, three fresh serial timing processes repeat all
arms and services on the prospectively fixed first 32 stored rows. Every
initial-state service remains a singleton. Each process reloads model payloads
and rotates the service order by `(repeat+risk_index+arm_index) mod 4`. There
are `3*32*2*8*4=6144` timing decisions. Training is not rerun to obtain a more
favorable clock. The primary and all three individual clocks, medians, ranges,
operation counts and process/cold-load scope are retained. These are
descriptive timing observations; external load and processor frequency are
not controlled, and no timing significance or favorable sign is required.

## 8. Independent original-policy validation and population inference

The separately frozen independent evaluator reconstructs the original
economy from the standard-library Fraction primitive implementation, without
importing the production terminal compiler. It covers every unique returned
primary state/action/risk key, including the completed incumbents. Deduplication
and exact identical-action cancellation apply to validation work only; they
do not delete primary policies or waive any service's actual decision cost.
The exact binary values are converted to Fractions without rational fitting or
`limit_denominator` substitution.

The fixed independent rule uses 64 whole-support shock cells and 32 terminal
bisections, convex-order AVaR midpoint/endpoint-mixture integration, and the
single unchanged `beta*epsilon1` future allowance. It records its actual
per-policy and total costs. Independently reconstructed feasible Lagrange
state supports provide valid all-action original-optimum lower witnesses as
specified in the independent protocol. These are finite numerical enclosures,
not exact optimal actions. All mean original objectives, policy regrets,
action-distance bounds, arm and service contrasts, unresolved signs and
certificate compatibility/containment results are retained. Agreement or
interval overlap alone is not a proof that a production interval is correct.

The fixed inference family is specified in the separately frozen statistics
protocol. In particular it includes the certified gain thresholds
`2^-20,2^-18,2^-16,2^-14`, exact binomial event intervals for the 48
non-completed risk/arm/service groups, and bounded mean comparisons of each
service with its own arm's completed incumbent, with numerical enclosure
uncertainty retained. Cross-representation economic contrasts are additionally
reported as independent finite-sample numerical enclosures; these are not
extra population confidence statements. Pointwise nonnegative gain
comes from the safe-return theorem; statistical intervals are not used to
authorize an unsafe individual action. Broad or unresolved population
intervals, conventional wins, neural losses, zero changes and zero events
are valid outcomes and must be reported.

No R119 D observation, earlier fixed catalogue, R115 sample commitment, or
post hoc selected state is used as a fresh R120 independent observation.

## 9. Failure custody, success criteria and interpretation

Output directories and immutable JSON records are created exclusively.
Scientific events and failures are appended and flushed; unsuccessful
attempts are never overwritten. A malformed source identity, missing frozen
actor/state artifact, contradictory enclosure, unqualified returned policy,
exception or failed declared timing process stops the attempted campaign and
preserves its prefix. Remaining rows are missing observations, not successes.
The complete declared sample may not be silently shortened for cost or sign.

Execution success means the actual specified computations completed with
valid, traceable records. A CI/audit pass means only the tests actually run and
passed. Scientific superiority requires the reported original economic,
information, accuracy and complete-cost comparisons to support it. A policy
improvement available equally to quadratic, spline, hinge, polynomial, tensor
or direct conventional methods is not a neural-specific advantage. If the
mixed bound never binds, if the legacy or direct control wins, or if remaining
economic gains are below the future-controller/certificate floor, those are
explicit results and continuing research requirements, not completion of a
larger unproved claim.

This protocol preserves the Econometrica objective: a correct original
Bellman-operator method that changes economically consequential actions,
matched against strong conventional numerical alternatives and supported by
complete proofs, independent value/regret validation, all costs and honest
population uncertainty.
