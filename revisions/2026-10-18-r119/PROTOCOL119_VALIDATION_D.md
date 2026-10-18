# R119 validation D: independent original-policy enclosures on every phase-C key

## 1. Prospective boundary and purpose

This protocol is fixed **after** the completed A, B and C studies and their known
results. It is a separate author-side numerical validation, not a new economic
campaign, a retiming, an independent sample, or confirmation on an unseen
workload. It changes no state, action, risk law, model, data, parameter, error
target, fitted representation, original observation, or economic objective.
It does not replace or add observations to A, B, C, R110 or any other episode.

The original C execution source is
`095936f1a7556d90d74809e63d75d9959d118360`. Its 96 primary files contain 13,824
decision records. Their exhaustive union has 983 distinct realized
state/action/risk keys: 492 at alpha 1/2 and 491 at alpha 3/4. Every one of these
keys is included, irrespective of representation, service, economic sign,
certificate quality or observed timing. The state catalogue remains the same
144 realized states per risk. No timing observations are rerun or amended.

The old 983-key, 1,024-cell policy reference uses a separate full-support
partition but shares the verified production terminal compiler. Its metadata
explicitly records this fact. The already executed, separately implemented
Fraction audit supplies 24 fixed original-model references, 72 certificates (24 contexts at three resolutions) and
3,736 retained terminal contexts. D expands the independent **value enclosure**
coverage to all actual C keys. The old 24-context suite remains a distinct
executed validation; its results are not relabeled D observations.

The fixed resolution of 64 whole-support cells and 32 rational terminal root
steps is selected for this validation using the known cost and width of the
older 24-context suite. No claim is made that this selection preceded the A/B/C
results. Every D source, the complete exact key list and the input hash manifest
must be committed and pushed before the first D economic evaluation. The actual
prospective commit is a required execution argument and is recorded in output.

## 2. Exact input and source custody

`VALIDATION_D119_KEYS.json` stores all 983 keys in fixed index/state-row/action
order, with exact binary64 hex identities and `Fraction(float_value)` ratios for
every observed state coordinate and action. The original alpha values are exact
1/2 and 3/4. No decimal rationalization, rounding to an intended grid,
`limit_denominator`, numerical tolerance for key matching, or replacement action
is permitted.

Before any economic evaluation, `independent_catalogue119.py`:

1. Checks its new code, this protocol, the frozen key file, its manifest, and
   all 45 current scientific-source files (the C freeze itself plus its 44
   entries) against the actual prospective Git commit and SHA256 values.
2. Checks byte lengths and SHA256 hashes of all 96 primary raw files and the
   existing `REFERENCE119.json`. Raw inputs are bound through the committed
   manifest; they need not be duplicated as individual Git blobs when their
   complete original archive has separate custody.
3. Reconstructs the union from **every** primary row, checking both risk blocks,
   all eight arms, all six services, every row 0–143 and the unchanged future
   terminal-controller identity. It requires exact equality with the frozen
   492+491 key list and complete exhaustion of the 983 old reference keys.

Only the unchanged `frozen108/code/independent94.py` is imported for science. Its
SHA256 is `a1a0e4ce5563d1105c3cea9eaad6678c609229446ba6794f7b8a7c03df01ebad`.
Its direct imports are restricted to Python standard-library modules. The D
program checks that import scope from its syntax tree. It never imports NumPy,
SciPy, `kernel108`, `investment94`, `interval94`, the production risk or terminal
compiler, any actor/feature implementation, or the primary campaign module.
Production files are read only for hash custody. Production output endpoints
are read only for the compatibility comparisons below.

There are no new model labels, fitted parameters, random numbers, stochastic
draws, action proposals, policy improvements, or candidate selection in D.

## 3. Independent terminal primitive and value bounds

For each realized original state/action/risk key, use all 129 distinct nodes of
the fixed 64-cell whole-support midpoint/endpoint mesh on `[-1/32,1/32]`.
Their exact coordinates are `z_k = -1/32 + k/(32*64)`, `k=0,...,128`.
Even indices are endpoints and odd indices are midpoints. Each terminal state is
reconstructed from the unchanged original economic transition using Fraction
arithmetic. No cross-policy cache or inherited compiler values are used.

At every terminal state, call the unchanged independent primitive's
`terminal_bounds(..., steps=32)`. It reconstructs the terminal cost polynomial
from the original primitive values at zero and the two original shock
endpoints, calculates the exact original continuous-AVaR tail integral,
brackets the feasible terminal optimum with up to 32 rational bisections, and
forms a global lower bound by exactly minimizing the original strong-convexity
quadratic on the full feasible displacement interval. An endpoint solution
requires no interior bisections. Any finite bracket length remains sound; the
number of steps controls enclosure width rather than the validity of the
strong-convexity lower bound.

Check and retain at every node:

- the original reachable state domain `[1/32,27/32]^2` and terminal feasibility;
- the reconstructed shock-quadratic coefficient exactly equal to 5;
- equality of the feasible upper value with the independently reconstructed
  original stage cost plus beta times the exact polynomial risk;
- ordered lower/upper terminal value bounds and a gap no greater than `2^-20`.

The even-dimensional original shock has zero aggregate loading. Thus the
aggregate-state hinge term is constant in the terminal shock; the terminal
cost is truly quadratic in that shock. The coefficient check is a recorded
primitive identity, not an assumption that interpolation would identify a
general nonlinear function.

The requested workload is exactly `983*129 = 126,807` terminal contexts.
Individual checks and all failures remain in the output. This is an independent
finite implementation audit, not a numerical substitute for the full convexity,
feasibility, strong-convexity and terminal-controller proofs.

## 4. Original continuous-risk Q and complete-policy J enclosures

Let `f(z)=V1*(F(x,a,z))` for the same original model and risk level. The proved
convexity of the original continuation value implies convexity of `f` along
the original affine shock direction. Let `l_k,u_k` denote the independent
terminal optimum lower/upper bounds at the mesh nodes.

Compute the exact equal-mass AVaR of the 64 midpoint lower values. Compute a
separate exact AVaR of the 128 endpoint upper values, where **each cell supplies
both endpoints**. Interior endpoints therefore occur twice. Their probability
is `1/128` per supplied atom; no endpoint deduplication is allowed in this
distribution. The AVaR routine sorts exact Fractions and handles a possible
fractional cutoff atom exactly. At the fixed two risk levels the tail counts
are integral, but the implementation does not rely on an approximate cutoff.

For every threshold eta, the function `(f-eta)+` is convex. Conditional Jensen
gives its midpoint lower expectation. Convex secant domination gives the
endpoint-mixture upper expectation. Taking the infimum in the original AVaR
threshold representation preserves both inequalities. This proves an outer
risk enclosure; a bound on the ordinary integral alone would not suffice.

Add the exact original root stage cost and multiply the risk endpoints by the
unchanged beta `15/16`. The resulting `Q_lower,Q_upper` enclose the original
root objective with optimal continuation. For the **unchanged implemented
future policy**, report

`J_lower = Q_lower`,

`J_upper = Q_upper + (15/16)*2^-20`.

The final allowance is added exactly once. It uses the already proved uniform
performance bound for the unchanged terminal controller. It is **not** direct
exact evaluation of that controller's 40-step floating implementation. D does
not independently calculate the global date-zero optimum or create a new
global policy-regret or action-distance certificate. Those claims retain their
own proof and executable-audit scope.

## 5. Comparisons and required reporting

For each independent policy interval, compare it with every corresponding
original service interval and with the existing 1,024-cell reference interval.
Convert the observed endpoints to exact Fractions of their realized binary64
values. Record interval overlap and both containment directions separately.
**Overlap is a compatibility check only.** It does not validate every fine
production endpoint or prove a production interval correct merely because two
intervals intersect. Any absence of overlap is a required failed check and is
retained for investigation. Containment is observed, not a required pass gate.

Report all 96 arm/service/risk mean original-policy intervals (the same 16
arm/risk means are repeated when exact service-policy identities apply). The
mean always gives the 144 fixed original states equal weight. These are
deterministic numerical bounds, not estimates over a sampled population.

Report every one of the 56 unordered arm mean contrasts, with the orientation
`left original mean policy cost minus right` and the fixed arm order online,
quadratic, ReLU, hinge, spline, degree-two polynomial, degree-three polynomial,
grid. The prospectively fixed canonical label is the compiled service; all
240 arm/risk/service-pair identity cells are checked and reported to establish
when the same comparisons apply to every service. At a state where the complete
policies have the same exact action and unchanged future controller, their
difference is exactly zero. Otherwise use independent interval subtraction
before averaging. Retain every positive, negative, zero and unresolved sign.

There is **no required favorable economic sign**, no neural-adoption pass
condition, and no requirement that every policy interval achieve a new width
target. A successful validation requires all source/input identities, the full
983-key/126,807-node exhaustion, original primitive checks, the recorded service
identity checks and interval compatibility checks to pass. Economic ordering
is a reported result, not a criterion for selecting or repeating the study.

## 6. Actual cost, failure preservation and files

The validation writes into a new nonexistent output directory. It never
overwrites a failed attempt. `EVENTS119D.jsonl` and
`POLICY_ENCLOSURES119D.jsonl` are opened exclusively, appended sequentially and
flushed/fsynced after every record. Each policy's primitive trace is a separately
and exclusively created gzip JSONL file with its compressed SHA256 and the
uncompressed stream SHA256 bound into the policy record. The trace retains exact
node, state, independent action, value bounds, polynomial, risk and tail
threshold data. Gzip avoids replicating a large uncompressed artifact.

Record actual per-policy elapsed and CPU seconds, including its solve, primitive
trace closing/hashing and compatibility comparisons. The small result-log
serialization overhead remains in total process cost. Record source/input
binding time, actual aggregation time, full internal elapsed/CPU time, maximum
RSS, every output hash and the external launcher command/stdout/stderr/return
code. This cost is additional author-side validation overhead. It is not
inserted into or used to replace any original A/B/C timing.

The optional maximum retained Fraction bit-length field concerns only the
terminal values actually saved in each trace. It is neither the maximum size
of every intermediate arithmetic expression nor a measured bit-operation count.

Individual exceptions retain the complete policy key, exception and partial
trace identity, then the program proceeds to the next fixed key. Failed
inequalities accumulate. A partial process interruption retains all completed
records and the started-policy event. A failure receipt is written when Python
can handle the interruption; abrupt external termination is not mislabeled a
completed run. There is no automatic retry, resolution increase, changed
selection or silent rerun. Any later attempt requires a new output directory,
preserved reason and separately documented source/protocol identity.

The program writes `PROVENANCE119D.json`, `SUMMARY119D.json`,
`EXECUTION119D.json`, the two append-only logs and all primitive traces. Failures
also write `FAILED119D.json`. Success of this finite local validation is not
remote CI success, external referee acceptance, a theorem proof, population
validation or a neural-specific economic advantage.

After the source and inputs have actually been committed and pushed:

```bash
python code119/independent_catalogue119.py --custody-commit COMMIT --output results119/validation119d_attempt01
```

The launcher must replace `COMMIT` with the actual immutable prospective SHA,
capture command/output/return status externally, and preserve all files before
making any successful-execution claim.
