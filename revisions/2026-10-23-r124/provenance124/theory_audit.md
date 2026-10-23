# R124 mathematical author-revision audit and contribution

## Identity and scope

This is an author-revision mathematical work record, not a new referee report or
an Econometric Society decision. The read-only base is
`fcf814f3579a13b08e1cca655c864b8b4d2f47fa`. The complete manuscript component is
R122 at `a4c22b50087430cdd42d07b161d696ebce54a858`. R123 at the base commit is a
separately frozen, actively executing experiment; its two deposited mathematical
files were read as frozen source, and no unpublished R123 output was read or
used. No R122 or R123 source, protocol, state, or output was edited by this task.

The exact files inspected, their Git blob identities, byte counts and SHA-256
hashes are recorded in `theory_sources124.json`. The review here covers those
active mathematical foundations and the new interpolation calculation. It is
not a claim that every historical numerical experiment has been reproduced or
every theorem in the complete historical development appendix was independently
reproved during this subtask.

## What is retained and what was checked

1. **Own-future Bellman construction.** `new121/core_main121.tex` uses its own
   acquired continuation, an explicitly paid original Bellman calculation,
   effective feasible nets, a Borel repair, and feasible action witnesses. The
   Lipschitz extension and affine–ReLU realization do not receive a neural-only
   capability claim; the native min-plus encoding is explicitly equivalent.
   Termination remains conditional on effective covers, repairs and certified
   queries at the prescribed accuracy. A fixed finite ladder does not establish
   arbitrary-tolerance convergence.
2. **Finite-horizon existence and policy comparison.**
   `new119/foundations_supplement.tex` states compact continuous primitives,
   continuous feasible correspondences, a fixed original conditional innovation
   law, and bounded monetary-risk evaluation. It separately imposes and proves
   parameter-kernel measurability for expectation and AVaR. The nested closed-ball
   argument constructs a Borel argmin selector; the subsequent induction compares
   the Markov optimizer with the declared Borel history-policy class. No inference
   of Borel selection from arbitrary discontinuous Bellman objectives was found.
3. **Boundaries, uniqueness, and stability.** The investment invariance and affine
   capacity arguments were checked, as were the state/action curvature argument,
   normalized-action envelope at capacity, and the terminal observation allowance.
   The code-level controller must still enforce its stated gap and fallback.
   The model gives unique continuous constrained optimal actors; it does not
   assert global differentiability of those actors across active-set changes.
4. **Continuous risk and action marginal.** `new121/marginal_main.tex` and the
   active foundations explicitly control the original AVaR tail under the
   original law, including an active central interval at either boundary. The
   new calculation uses the proved original curvature constants. It does not
   infer them from a learned critic. The original derivative cap used in R124
   has a simple independent proof: the continuation modulus is at most
   `(15/d)*(3d/8)*beta=45*beta/8`, while `h'<=3/4`; at `beta=15/16`,
   `|Q'|<=771/128<7`.
5. **Gradient and computational graph.** The retained graph distinguishes the
   actor path, partial parameter derivative of the future target, and present
   critic derivative. Its AVaR envelope formula assumes an atomless unique
   quantile and appropriate domination. It does not differentiate a sorting
   permutation, identify a detached target with the full gradient, or assert
   optimizer convergence. Projection and rounding failures of differentiability
   are explicitly excluded from that smooth gradient formula.
6. **NDU/FBSDE and nonlinear utility.** `new110/recursive_bridge.tex` is a
   decoupled forward Brownian Markov subcase with control-uniform state and driver
   Lipschitz constants, bounded data, and a separately admissible well-posed
   feedback. The stopped extension carries the boundary discrepancy. The
   Girsanov step includes an H1 martingale integrability argument. It explicitly
   does not prove a fully coupled FBSDE theorem or treat a piecewise-affine ReLU
   function as C2. Noncash-invariant recursive utility keeps its own stability
   factor and cannot inherit the investment AVaR shift identity.
7. **Recursive policy improvement.** `new122/dynamic_gain122.tex` uses an infimum
   with a positive centered penalty to propagate lower gains. Its domain includes
   kernels whose penalties are relaxed. The occupation calculation correctly
   distinguishes a lower dual/subsolution certificate from a feasible flow's
   upper bound. The stationary extension uses a complete bounded-Borel domain.

No substantive contradiction was identified in the active statements checked
above. These checks do not turn their explicit hypotheses into numerical facts.
In particular the global learned feature cover, general fully coupled NDU
extension, neural-specific complexity advantage, and profitable neural adoption
remain separate research obligations unless independently supplied elsewhere.

## Mathematical increment for this revision

R123's frozen derivative-cone construction correctly disclaims sharpness after
absolute value levels are imposed. R124 addresses that information loss. With
the same paid levels and derivative intervals, it imposes the exact scalar
smooth strongly convex interpolation conditions on adjacent sorted nodes. The
resulting finite convex quadratic/conic problem gives the exact worst original
action contrast over the declared joint information class.

For spacing `d`, curvature gap `K=L-mu`, derivative increment
`s=g_next-g-mu*d`, and value increment
`w=f_next-f-g*d-mu*d*d/2`, the conditions are

`0 <= s <= K*d`, `s*s <= 2*K*w`, and
`s*s <= 2*K*(s*d-w)`.

Necessity follows by integrating the tight lower and upper derivative ramps.
Sufficiency is constructive: on each interval interpolate those two ramps to
match the required integral; the resulting continuous piecewise-affine
derivatives join at every measured node. This gives a full proof, not a solver
assumption. The `mu=L` case uses linear equalities, repeated anchors share one
node, endpoints are included, `A=0` is trivial, and global range boxes are proved
to enclose the original quantities.

The scalar interpolation principle itself is classical and is credited to the
smooth convex interpolation literature already cited by R122
(`THG2017Interpolation122`). The contribution is its use in the paid Bellman
information interface, its economic gain/width/regret account, and a certified
implementation which can remain correct when a numerical solve is inaccurate.
Every competing representation can use the same calculation.

The exact interface intentionally includes levels, derivative intervals,
curvature and any declared gradient cap. It does not silently encode every raw
quadratic support or the complete algebraic investment model. A matching
minimax bound applies only to that stated class. Additional raw-support
certificates can be intersected with the new bounds without transferring the
sharpness claim to the stronger information class.

## Implementable numerical safeguard

SLSQP or another optimizer may propose a primal point and multipliers. Actual
certificate acceptance uses exact rational weak duality plus a convex tangent
bound minimized over a finite enclosing box. Nonnegative multipliers and the
residual correction suffice; primal feasibility, exact stationarity, strong
duality, or a solver success flag are not assumed. The complete rational witness
must be retained for independent verification. An inaccurate proposal can simply
produce an unusably wide bound.

The resulting upper original contrast receives the implemented-future allowance
once for a distinct action. Equal-action contrasts are zero. Absolute objective
width remains a separate predicate. A strictly improved already qualified
incumbent retains its regret qualification by direct regret transport; this does
not establish objective-width qualification on its own.

The same dual tangent supplies exact endpoint refinement credits in original
objective units. A verified action cover and original derivative cap yield a
remaining-gain ceiling for the existing compulsory-cost stopping rule. Neither
calculation predicts an unobserved query's outcome or treats shared-host timings
as universal economic prices.

## Exact independent witness

`verify_joint_witness124.py` imports only Python standard-library exact arithmetic
and does not import any production economic or certificate module. Its executed
record is `joint_witness124.json`, with status
`passed-exact-rational-algebra`.

The data are `mu=1`, `L=2`, `A=1`, `q(0)=0`, `q(1)=3/16`,
`q'(0)=-1/2`, and `q'(1)=1`, with incumbent zero. The derivative-envelope
calculation followed by the separate absolute-value intersection has best
guaranteed original gain `1/16`. Joint interpolation has exact robust action
`3/8` and gain `5/64`, a strict difference `1/64`. A continuous piecewise-affine
derivative realizes all supplied data and attains the bound. An independent
rational dual with multipliers `1/2,1/2` has exactly zero residual and proves
the matching upper contrast. All adjacent interpolation constraints are checked.

This is a mathematical witness in the declared information class. It is not a
new investment state, an independent economic experiment, a neural-specific
advantage, or a substitute for the still pending R123 experiment.

## Files for integration

- `joint_main124.tex`: new main-text definitions, statements, interpretation,
  cost account and stopping/refinement implications.
- `proofs124.tex`: full proofs and strict rational witness.
- `theory124.tex`: combined identical source, convenient for independent review.
- `verify_joint_witness124.py` and `joint_witness124.json`: exact independent
  arithmetic validation and its actual execution output.
- `theory_sources124.json`: identities of the inherited mathematical sources
  inspected for this audit.

No empirical or remote CI success is claimed by this mathematical work record.
