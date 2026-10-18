# R119 well-posedness, actor graph, and boundary audit

## Scope and source authority

This author audit supplements the complete R110 manuscript retained in
`NBO/revisions/2026-10-17-r118`. The controlling complete-author source is
R110 commit `4ba2bbaa11b5fa59f83705b28b35bf82a63ca169`, subtree
`5885983fdef89cdc11fe471753cccfa46160956f`. It is not identified by the
R118 directory name. No frozen experiment, policy, objective, or historical
source was edited in this audit.

The targeted obligations were checked in the active core, full current
supplement, active-region compiler and tail theorem, recursive-improvement
theorem, and the retained expectation regularity, transport, occupation,
and nonlinear-recursion interfaces. In particular the relevant source
files are `new110/core-main.tex`, `new110/recursive_bridge.tex`,
`new109/{compiler,tail,proofs}.tex`, `new110/budget_proofs.tex`,
`sections/{proofs67,proofs92,proofs95,proofs96,accuracy62-print,
recursive86,proofs86,transport90,proofs90}.tex`, and `new/proofs99.tex`.
This is a cross-cutting foundations and graph audit, not an assertion
that every archived empirical or statistical result has been re-executed.

## Deliverables and insertion order

- `foundations_main.tex`: short English main-text insertion. Include after
  the economic operator definition and before using value/policy existence.
- `foundations_supplement.tex`: full author module with three precise
  propositions and proofs, original-primitive closure and curvature,
  residual recursion, computational graph, and stopped BSDE verification.
  Its discrete section can precede the inherited proof collection. Its
  stopped section refers to the retained Brownian Picard proof, which
  should remain in the complete supplement.
- `verify_foundations119.py`: independently readable `Fraction` arithmetic
  checks of the displayed primitive algebra; no package dependencies.
- `foundations_algebra119.json`: actual successful output of that check.
- `foundations_check119.tex` and `.pdf`: a standalone proof draft used to
  compile the module with the existing bibliography. The integrated ECTA
  document still requires its own build, cross-reference, and layout audit.

The main/supplement module explicitly assigns the fixed-point and
selection foundations to classical dynamic programming. Existing
references `ruszczynski2010risk`, `ruszczynski2014erratum`,
`PardouxPeng1990`, and `ElKarouiPengQuenez1997` are reused. No claim of
novelty is made for Banach contraction, compact minimization, measurable
selection, or the standard Lipschitz Brownian BSDE existence theorem.

## Findings and exact remedies

### 1. Continuity is an actual primitive obligation

The current core assumes continuous action objectives and measurable
minimizers. Those are acceptable premises for its comparison results,
but they do not derive existence from the economic primitives. The new
finite-horizon proposition supplies a complete sufficient route:
compact metric state/action/innovation spaces; nonempty compact,
upper- and lower-hemicontinuous feasible correspondence; continuous
original cost, transition, and terminal value; invariant transition;
fixed innovation law; finite monotone cash-invariant risk.

Monotonicity plus cash invariance gives the needed supremum-norm
nonexpansiveness. Compact joint continuity then gives uniform
continuation continuity. A subsequence proof establishes continuity of
the Bellman minimum. An explicit finite closed-ball, nested-fiber
construction proves existence of a Borel minimizer. Backward induction
proves uniqueness of the value sequence and optimality against the
declared full history-policy class, not merely Markov comparisons.

With noncompact innovations, pointwise continuity of the transition
does not suffice for every monetary risk. The supplied counterexample
uses exponential `Z`, `F(x,z)=1-exp(-xz)`, `g(y)=y`, and `ess sup`:
the value is zero at `x=0` and one at every `x>0`. The valid general
replacement is essential-uniform continuation continuity. This is an
assumption completion; it does not invalidate the original compact
uniform-law investment model.

### 2. Borel risk kernels do not follow from order properties alone

The finite monetary map on `L infinity` must additionally preserve
Borel parameter kernels if implemented policies are only Borel. The
new section states that property explicitly. For the original AVaR it
is proved by its threshold integral, a countable infimum over rational
thresholds, and the measurable-kernel integration argument. Expectation
is the simpler same argument. No general result about nonseparable
`L infinity` parameter maps is silently assumed.

For a nonnormalized monetary risk, the original operator is preserved
exactly by `rho_bar=rho-rho(0)` and `c_bar=c+beta*rho(0)`. Its constant
is not discarded from the objective.

### 3. Continuous Bellman values and Borel policy values are distinct spaces

The new discounted theorem applies Bellman contraction on `C(X)`, which
the compact theorem proves invariant. Fixed Borel policy operators act
on bounded Borel functions by the kernel property. It does not assert
that taking an infimum of arbitrary bounded Borel action objectives
always produces a Borel function. The inherited R109 policy-iteration
theorem separately assumes the needed preservation and selection on
its larger function class; those assumptions remain in force.

Independent review caught this same distinction in the first draft's
stability sentence. It now states Bellman stability for continuous
terminal continuations. Bounded Borel terminals remain allowed for
fixed-policy comparison under the explicit kernel assumption.

No discount contraction is used to assert finite-horizon existence:
finite nonnegative discounts can exceed one. Infinite horizon explicitly
requires `0 <= beta < 1`, bounded costs, and the same original nested
criterion. Its infinite history comparison follows from a uniform
discounted tail bound, not a static AVaR reinterpretation.

### 4. Original investment invariance, strong curvature, and actor regularity

The exact state term `p/2+q/8+p(1-q)/16` is increasing in both inputs
on the unit square and has range `[0,5/8]`. Adding the unchanged
constant, action exposure, and shock gives
`F in [1/32,27/32]^d`. This bound even holds on the entire outer action
rectangle `[0,1/4]`, which contains every capacity-feasible pair.
The original capacity lies in `[1/8,1/4]`. Safe cost bounds are
`S <= 49/32`, `g <= 37/16`, and `S+h <= 103/64`.

The module gives the full joint Hessian argument. The positive
Jacobian/Hessian/Jacobian term is kept as a whole, including mixed
state-action entries. The only adverse transition curvature is at
least `-5||v||^2/(4d)`. Adding stage curvature yields joint modulus
`((4-5 beta/4)/d)||v||^2 + 2 w^2`. Integration under each feasible
risk density and the common-quadratic supremum preserve it. Partial
minimization over the affine capacity graph gives the same state
modulus for `V1`. For `beta=15/16`, the innovation direction has
curvature `181/64`. This is the actual optimal continuation, not an
unqualified convexity assertion about a fitted network or deployed
terminal value.

Both dates' original action objectives are strongly convex with
modulus two and have unique continuous constrained actors. The
last-date formula is C1. Normalizing the feasible action as `a=A(x)v`
over a fixed unit interval gives
`grad V=grad_x Q-lambda grad A`, with the correct nonnegative
capacity multiplier. This includes lower-bound, interior, binding
capacity, and switching cases. The actor itself need not be globally
differentiable across regime boundaries.

The root continuation along the original scalar innovation is strongly
convex. Its level sets contain at most two points, so its continuous-law
distribution has no atoms. The unique central-tail minimizer and the
fixed-domain envelope theorem give the original root C1 formula.
No derivative of a changing approximate tail or rounded actor is used.
The inherited expectation-model semiconcavity theorem is still an
expectation-model theorem; arbitrary AVaR supremization was not used
to promote that whole result to another preference.

### 5. Observation and the actual future policy remain in the certificate

The terminal controller observes a downward 40-bit state `y <= x` and
returns an action feasible at `y`. The affine capacity preserves its
feasibility at `x`. Its certified gap at `y` is at most `2^-21`.
Both the original fixed-action objective and true value have an
`ell-one` state modulus at most `15/d`. Consequently the original-state
gap is at most `2^-21+30*2^-40 < 2^-20`.

The exact arithmetic audit confirms the resulting fraction
`262159/549755813888 < 1/1048576`. The controller must still enforce
the first premise via its actual outward arithmetic and fallback.
These constant checks do not by themselves test every runtime branch.
Changing the integration locations does not change or remove this
future-policy allowance.

### 6. The actor/critic gradient is a full graph derivative

The new section writes the derivative of the original residual with
all shared-parameter paths: stage/transition via the actor, direct
continuation-parameter derivative at a fixed successor, and current
critic derivative. Risk-envelope differentiation holds the maximizing
density fixed only under the stated domination and atomless unique-
quantile conditions. It is not justified by differentiating a sort
permutation. The loss is explicitly half the expected squared residual,
so its derivative is `E[r grad r]` with the correct factor.

Detaching a future target is a different frozen-target gradient or
semigradient algorithm. It is not presented as the gradient of the full
coupled objective or as a convergence theorem. Projection/rounding
discontinuities are treated through implemented feasible actions and
their certificate; smooth derivatives are claimed only on their
valid branches.

### 7. The retained Brownian BSDE proof is sound under its intended hypotheses

Checked explicitly: decoupled forward Picard argument; Brownian natural
filtration and martingale representation; weighted BSDE Picard
contraction factors `max(8 Ly^2/k^2,4 Lz^2/k)`; residual signs;
divided-difference bounds; Girsanov density sign; positive integrating
factor; and the transfer to an H1 martingale under the tilted measure.
No mathematical sign or constant error was found in these parts.

Its phrase "usual measurability" is made concrete: deterministic
coefficients and driver are jointly Borel, so composition with an
admissible progressive control is progressive; all stated Lipschitz
constants are uniform in action. The specified feedback must itself
have a well-posed closed loop. The argument remains for a decoupled
forward system, not a general fully coupled NDU/FBSDE.

### 8. The stopped-boundary bridge is now a complete proposition

The retained paragraph required a stopped-boundary allowance but did
not supply the full stopped verification theorem. The new proposition
uses the specified stopping time, bounded Borel original boundary
payoff, bounded smooth critic, uniform residual envelopes, and the
complete stopping/terminal discrepancy. It embeds the stopped problem
using a driver set to zero after stopping, proves the integration-factor
identity, and obtains the same exponential residual-loss bound with
`tau <= T`. No optimizer existence is assumed: the infimum over
admissible controls suffices.

A deterministic two-exit example proves why the boundary term cannot
be deleted: the zero critic and zero interior residual coexist with
unit policy regret if the two exits have different original costs.
The finite-horizon ReLU construction is not inserted into the C1,2
Itô formula by setting a ReLU Hessian to zero off its kinks. A weak,
viscosity, or smoothing theorem would need its own conditions and error
account before authorizing that step.

### 9. Recursive utility is not automatically monetary

For the standard globally Lipschitz BSDE driver `f=lambda*y`,
`Y0=exp(lambda*T) E[xi]`. Translating the terminal criterion by a
constant changes the answer by its exponential multiple, not generally
by that same constant. The BSDE bridge therefore retains its actual
`exp(Ly*T)` stability factor. It is a rigorous continuation of the
NBO research program in a separately declared original criterion, not
an empirical identity with nested investment AVaR.

## Independent review and actual checks

The independent review-lineage agent checked the new explicit selector
proof, the constrained V1 C1 envelope, and the root C1 argument. It
confirmed them and supplied the continuous-versus-Borel stability
correction above. The earlier four new active-tail/coupled theorem
files remain unchanged by this foundations task.

Executed successfully:

```text
python audit/theory_research/verify_foundations119.py
pdflatex -halt-on-error -interaction=nonstopmode \
  -output-directory=audit/theory_research \
  audit/theory_research/foundations_check119.tex
bibtex audit/theory_research/foundations_check119
# Two further pdflatex passes resolved references and citations.
```

The algebra result is saved as JSON. The final standalone compile had
no undefined citations/references, overfull boxes, warnings, or errors
in its log. It produced a nine-page proof draft. A first draft build
needed TeX font generation; it completed through the allowed temporary
font cache. This was a document build, not a scientific experiment or
CI execution. Root remains responsible for the integrated ECTA/PDF
layout, source hashes, scientific experiment, and release manifests.
