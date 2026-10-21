# R121 source-only review of the original-risk marginal link

Review completed: 2026-10-20 19:06 UTC. Reviewer role: author mathematical
cross-check by the manuscript agent. This is not an external referee report.
The review used source reading and manual mathematical reasoning. It ran no
economic primitive, numerical experiment, symbolic or numerical proof test,
fitting procedure, independent evaluator, build, or timing process. File
hashing below identifies the sources read and is not scientific execution.

## Scope and source identity

The target is Theorem `thm:rootmarginal121`, Lemma
`lem:cutmarginal121`, and Proposition `prop:marginalprobe121`, including the
immediate original-value regularity dependency. This is a bounded review of
the novel analytic link, not a fresh proof audit of every retained theorem or
an audit of any partial experimental outcome.

| Source | SHA-256 |
| --- | --- |
| `new121/marginal_main.tex` | `d99e219bf99bd65d0e1b2060043a07b38d1c37bd74ad54783be8c2132b1a2a76` |
| `new121/marginal_proofs.tex` | `6bb462f6126385876387f94b08480d703eb30f30a29945579533f89a30cbd200` |
| `new120/policy_improvement_main.tex` | `2951c714110693948964908a4c807a977d0cbfc0f5ef693df11050fbd3670a91` |
| `new120/policy_improvement_proofs.tex` | `34fcc2c5f5acd1f57b22b6f0bbfe371ef15d59de47666db048faab2f270d24b0` |
| `new119/foundations_supplement.tex` | `21a2e130ae402d6883a3a41389aec281f1ae7c218322f1a2f07e47d622ddb74e` |
| `new110/continuous-main.tex` | `fd5f5d2478966f70e1170591d82261b4095988d7b74a5f8ae5fb90abec801f70` |

The two new theorem-file hashes equal the entries in the local
`SOURCE_FREEZE121.json`. The parent reports the immutable F identity as
`16bf21334efcbc719b83e2ccf10e8527f8b956f2`; this review does not claim an
additional remote Git readback of its own. The retained original primitive
formulas in `frozen108/code/investment94.py` were inspected as text only.

## Finding

No concrete invalid inference or formula mismatch was found in the bounded
scope. The original-risk regularity claim includes binding action capacities
and shock-boundary tail cuts without differentiating the optimizer or assuming
an interior tail. No frozen scientific source was edited.

### 1. Nested last-date minimization and the state-gradient modulus

The immediate R119/R120 dependency is sufficient for the new theorem. The
joint original last-date objective has lower curvature
`((4-5*beta/4)/d) * ||dx||^2 + 2 * da^2`. The potentially negative transition
Hessian term is state-only; the complete Jacobian--terminal-Hessian--Jacobian
term is nonnegative in the full state/action direction. Interpolation of two
optimal pairs is feasible because capacity is affine. Minimizing over action
therefore preserves the stated state strong-convexity modulus. With d=2 and
beta=15/16 this is 181/128, as used in R121.

For the upper modulus, normalization `a=A(y)v` puts the last-date minimization
on the fixed interval [0,1]. Each fixed-v objective has state semiconcavity
constant M_alpha. The infimum of the corresponding concave functions remains
concave. This step is valid; no state-dependent feasible index is left inside
that infimum. Uniqueness and continuity of the normalized minimizer, together
with uniform first-order expansions, give the continuous state value gradient.
The capacity term is present in that envelope. Convexity and M_alpha
semiconcavity then imply the M_alpha Lipschitz gradient, including the continuous
boundary extension, by the stated interior mollification and limiting argument.

The primitive upper constants agree with the retained formula: 11 for S,
13 for the terminal Hessian, 5 for each terminal gradient coordinate,
3/4 for the normalized transition state Jacobian, and 5/8 for its second-order
chain-rule allowance. These give 127/16 for the composed terminal upper
curvature and 1413/128 for the current stage upper contribution. The affine
tail coefficient has squared gradient at most 19625/2048. Multiplication by
the tail derivative modulus alpha/(10t) gives the stated
19625*alpha/(20480t) term. Clipping junctions have matching first derivatives.

### 2. Original AVaR tail, uniqueness and shock-boundary cases

The innovation direction has squared norm two, so the original state modulus
181/128 yields innovation strong convexity m_z=181/64. For the central window
of length L=2R*alpha, the derivative of its integral is `f(c+L)-f(c)` and is
strongly monotone with modulus m_z*L. Its compact-interval minimizer is unique.

At an interior cut, the two endpoint values agree. At the left cut boundary,
the inward optimality inequality gives `f(-R+L) >= f(-R)`. Convexity then places
every central-window value below the right-tail values; the right cut boundary
is symmetric. Thus the adverse AVaR density is correctly placed on the
**complement** of the minimizing central interval. A zero-length tail is
allowed. Strong convexity makes each value level set contain at most two
points, so there is no positive uniform-law mass at the threshold.

The quantitative cut comparison uses the two constrained variational
inequalities, with the signs in the source correct. Combining them with
strong monotonicity bounds `m_z*L*|dc|^2` by `L*E*|dc|`. The cancellation of L
gives `|dc| <= E/m_z`. No zero derivative equation is imposed at either cut
boundary. All denominators are positive at alpha=1/2 or 3/4; no alpha=1 claim
is being made.

### 3. Envelope differentiation, normalization and both explicit moduli

The fixed-cut objective is continuously differentiable uniformly over its
compact cut interval. Unique continuous maximizing cuts permit the stated
old-cut/new-cut envelope argument. This yields beta times the normalized tail
integral of `b^T grad V1`, while holding the cut fixed. The factor A(x) from
the v derivative cancels exactly in `H=A(x)^(-1) partial_v R`. Consequently
the global variation of H has no omitted derivative of 1/A: its integrand is
the original-action marginal with constant b, and all state/capacity dependence
is carried by `m(x,v)` and its cut.

At fixed state, the integrand change has bound `(5M/16)|da|`, and its shock
Lipschitz constant is at most `C=4M/5`. The cut comparison supplies
`|dc| <= C|da|/m_z`. Replacing the cut in a fixed marginal integrand changes
the normalized tail integral by at most `(C*alpha/t)|dc|`. Together these
give the displayed D_alpha and `L_alpha=5+beta*D_alpha`, since `2 <= h'' <= 5`.
The continuation is convex by the original convex V1, affine action transition
and monotone convex AVaR. Adding h supplies the original-action strong-convexity
modulus two. The normalized version multiplies both action curvature bounds
by A(x)^2.

For joint state/normalized-action variation, the source bounds
`||D_x m|| <= 3/4` and `||D_v m|| <= sqrt(5)/16`, hence
`||D_u m|| <= sqrt(149)/16 <= 49/64`. Combining this with
`||b|| <= 9/16` gives the first coefficient 441M/1024. Combining it with
`||s|| <= 3/2` gives 147M/128 for the innovation derivative of the difference.
The cut bound and `C=4M/5` then give 147*M^2*alpha/(160*m_z*t). These agree
with Lambda_alpha in both the main statement and proof; beta is charged once.

### 4. Derivative labels and policy scope

The forward and backward secant enclosures have the correct strong-convexity
signs. The central second-difference derivative bound has radius
`(L_alpha-2)*d/4`, obtained by integrating the two opposite derivative
increments. The endpoint rules use only feasible inward probes. A fixed x
uses `d=A(x)*2^-12`, and derivative design rows are in original-action units
through division by A(x). Subtraction of h' is explicitly required to be
outward or exact. The value-uncertainty half-width `e/d` and its balancing
formula are consistent with input value-interval widths at most 2e.

All this regularity concerns the optimized original Q and V1, rather than a
fitted critic or the rounded future policy. The implemented future allowance
is separately bounded by delta=beta*2^-20; no derivative or convexity of that
allowance is assumed. Finite-node derivative fitting does not inherit a
continuum guarantee without the separately proved and actually constructed
feature-cell inequalities. These distinctions remain explicit in the source.

## Nonblocking wording point

The main theorem's phrase “normalized action curvature” is supported as the
strong-convexity/smoothness pair of inequalities, or as an almost-everywhere
second-derivative bound. It should not be paraphrased in the abstract or
interpretation as an everywhere classical second derivative at all active-set
switches. The current theorem already states continuous differentiability and
a Lipschitz first derivative, which is enough for all secant and policy uses.

The earlier unfrozen introduction phrase “adverse central interval” was
corrected to “central interval excluded from the adverse tail.” That editorial
correction aligns prose with the already correct frozen formula and proof; it
does not revise any mathematical assumption, algorithm or experimental rule.
