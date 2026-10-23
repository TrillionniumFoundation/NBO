# Independent author-side mathematical check of the R125 additions

This is an internal author revision check, performed separately from the theorem writer and the production numerical code. It is not a journal referee report, a proof-assistant verification or an economic experiment. The companion JSON binds the exact source bytes checked and the actual independent rational diagnostic. Later edits require a fresh source binding.

## 1. Exact interpolation above complete original supports

The checked theorem concerns one scalar action domain `[0,A]`, `A>0`, a continuously differentiable function with `mu`-strong convexity and `L`-Lipschitz derivative, finite paid value/derivative intervals, a valid finite derivative cap, and globally valid quadratic supports with the same curvature lower bound. Every observation location, support anchor, action under comparison and both endpoints must be among the nodes. This is a `C^{1,1}` class; the constructive interpolant need not be twice continuously differentiable.

Subtracting `mu*x^2/2` gives a convex function with derivative Lipschitz constant `K=L-mu`. A quadratic support with one unknown but globally valid slope becomes an affine obstacle whose coefficients are affine functions of that shared slope. The slope is a bounded nuisance variable, not necessarily the original objective's derivative at the anchor.

For an adjacent interval, write its length, derivative increment and excess integral as `d`, `s` and `w`. The necessary and sufficient smooth-convex interpolation restrictions are `0<=s<=K*d` and `s^2/(2K)<=w<=s*d-s^2/(2K)`. The proof correctly derives these restrictions by integrating the lower and upper derivative ramps.

At each node the additional support inequality is

`f_i - ell_j(x_i) >= max_{t in [-x_i,A-x_i]} ((r_j-g_i)*t - K*t^2/2)`.

Necessity follows from the smooth upper bound on the unknown function and the globally valid lower support. The maximum must be over the entire feasible displacement domain. Merely checking node levels against the obstacle is insufficient.

For sufficiency, when `D=d-s/K>0`, the proposed derivative increment

`min(K*t,c) + max(0,s-c-K*(d-t))`, with `c=(w-s^2/(2K))/D`,

is continuous, nondecreasing and `K`-Lipschitz. Its ramp endpoints do not overlap, its endpoint increments are exactly zero and `s`, and its integral is `c*D+s^2/(2K)=w`. Thus every adjacent jet pair is realized. When `D=0`, the interpolation bounds force the unique full `K` ramp. The `s=0` case is included without division by `s`. When `K=0`, the whole transformed function is affine and the node support constraint reduces to the two domain endpoints.

The global obstacle argument is valid. For an obstacle slope between the endpoint gradients, the minimum gap occurs on the first ramp or the last ramp, or is constant across the plateau. The two possible minima are the left gap minus `v^2/(2K)` and the right gap minus `(s-v)^2/(2K)`. The corresponding maximizing displacement is feasible from that endpoint and is therefore constrained by its bounded-domain conjugate. Slopes outside the endpoint-gradient range attain their minimum gap at an endpoint. This verifies every obstacle everywhere for the same constructed interpolant and the same chosen slopes.

Gluing the intervals produces a global `C^{1,1}` interpolant. After adding back the quadratic, its derivative is monotone and remains between the derivative values at adjacent nodes, so the original derivative cap holds everywhere. All finite boxes must be derived from valid original bounds; they are not arbitrary fitting restrictions. Nonemptiness is a compatibility premise. Closedness, bounded node/slope variables and convexity then give compactness and attained fixed-action contrast extrema. The finite convexity claim is for a fixed action pair or separately enumerated finite menu; freely optimizing node locations is not covered by the same convex program.

### Corrected shared-slope interpretation

The initial suggestion that a shared existential slope gives strictly more information than the full pointwise robust slope envelope was rejected during this check. For a convex transformed function the two global restrictions are equivalent. With `h(a)>=W`, left secant slopes relative to `(a,W)` lie below right secant slopes. The robust envelope bounds the former above by the interval's upper slope and the latter below by its lower slope. Those intervals intersect, providing one valid global supporting slope. The final source now includes this proof, including one-sided endpoint conventions.

The valid improvement is over the R124 class that omitted raw supports, or over incomplete node-only obstacle checks. It is not a stronger information set than correctly enforcing the entire robust obstacle.

### Rational residual certificate

For convex constraints `c_j<=0`, nonnegative multipliers and valid subgradients at an arbitrary rational point, the Lagrangian affine minorant is a lower bound on the linear minimization objective. Minimizing that affine minorant over an enclosing box gives the stated residual correction. The direction of both inequalities is correct. Feasibility and stationarity of the proposed point and strong duality are not needed. The conjugate derivative is the clipped displacement for `K>0`; for `K=0` any active endpoint, or a convex combination at a tie, is a valid rational subgradient.

Intersecting a numerical proposal with all earlier valid same-objective bounds preserves the returned certificate even when the proposal is poor. Exact-program dominance alone does not guarantee that an approximate numerical solver returns a better bound.

## 2. Exact witnesses and actual independent diagnostic

The strict witness is correct. In the reduced class strong convexity at the midpoint forces `q(1)>=1/4`, attained by `q(x)=x^2/2-x/4`. Retaining the original support forces `q(1)>=5/8`, attained by `q(x)=x^2/2+x/8`. Both satisfy all stated value, derivative and curvature restrictions. Thus the maximum contrast for `1 -> 0` changes from `-1/4` to `-5/8`. The derivative interval is obtainable from the disclosed original support gap and feasible-radius conversion. Arbitrary bounded implemented-future error contributes exactly `+delta` to the worst contrast for distinct actions.

Cheap direct evaluation of the retained support at the incumbent already attains the improved bound in this witness. It demonstrates a real loss from discarding paid information, but does not demonstrate a computational advantage of the conic formulation or a neural-specific advantage. The separate inconsistent-payload example correctly passes nodewise obstacle checks while violating the obstacle between nodes, and the new conjugate inequality correctly detects the inconsistency.

The separately written `check_obstacle_interpolation125.py` uses only Python `Fraction`. It imports no production numerical implementation and evaluates no economic state or fitted actor. Its executed receipt records 240 deterministic rational jet configurations, three adjacent intervals per configuration, 17 slope choices per configuration and 4,080 support cases. It independently enumerates derivative-piece boundaries and stationary points to compute the exact global minimum gap, then compares that value with the node-conjugate condition. Valid and invalid shifted obstacle intercepts are both checked. Zero increments, saturated increments, both interpolation-area endpoints and the `K=0` affine case are included. The recorded execution passed. This finite diagnostic corroborates the construction; the written argument, not the finite case count, establishes the theorem.

## 3. Paid action localization and its work bound

The original-regret initialization is valid at both interior and constrained boundary optima. The constrained variational inequality and strong convexity give squared action distance at most `2*K0/mu` from an incumbent with original regret certificate `K0`; `q<=J` transfers that certificate. Outward rounding and intersection with other valid optimizer intervals preserve inclusion. This is a valid optional theorem rule, not an undocumented modification of the frozen service.

The support-precision calculation uses a feasible finite radius and is correct. When the current interval width exceeds the requested next width `t`, a rounded midpoint with relative error at most `xi<1/2` has feasible left and right radius at least `(1/2-xi)*t`. The declared `h=chi*t` lies within that radius. The converted derivative enclosure has width at most `v+2*e/h+K*h`; the prescribed gap and slope widths bound those three terms by `mu*t/4`, `mu*t/2` and `mu*t/4`. The retained R123 midpoint result therefore delivers width at most `t`. Actual and planned widths are properly distinguished.

The geometric work sum is algebraically correct. With `gamma=1/2+xi` and the minimal guaranteed number of probes, the backward schedule chooses the largest admissible requested width at each step, subject to the final target and the contraction floor. Since the declared upper cost decreases with requested width, it minimizes the sum of these declared bounds. A longer schedule cannot reduce its final required cost terms and adds nonnegative terms. This optimum is only for that stated planned-width problem. It is not a lower bound on actual runtime, a guarantee for adaptive observed stopping, or an optimum over all economic algorithms.

The oracle premise must independently cover level accuracy, slope enclosure, unsuccessful precision levels and original continuation accuracy. A fixed terminal solver, finite risk ladder, action lattice or resource cap may invalidate that premise. No unconditional numerical complexity claim follows from the theorem. The production service uses its frozen ladder rather than the ideal minimizing schedule; those implementation identities remain explicit.

### Sharpened terminal decision account

During this check the terminal actual-regret bound was sharpened from `e_b+delta+M*r_b` to `delta+M*r_b`. The value-interval width is unnecessary for that direct regret bound once the original optimizer bracket and derivative cap are certified. For a certified stationary optimum, the sharper smoothness bound is `delta+L*r_b^2/2`. At a capacity boundary the derivative may be nonzero, so the stationary formula cannot be used without an independent stationarity condition.

The absolute implemented-policy interval still has width `e_b+delta`; the final absolute-value query therefore remains a separate required and charged gate. A narrow optimizer interval is not an absolute value certificate, and the derivative of the arbitrary bounded future-controller discrepancy is never assumed.

## 4. Reduced-interface terminal minimax result

The stationary-bracket proposition is valid under its explicitly reduced information class. For any action law, smoothness bounds expected original regret by one half of `L` times the variance plus squared distance of the mean to the unknown optimum. Maximizing over an interval selects an endpoint. The endpoint quadratic functions attain this bound and satisfy the stated derivative-cap qualification, if any. Zero variance and the interval midpoint minimize the maximum endpoint distance, yielding `L*(r-l)^2/8`; constant future discrepancy `delta` attains the additional allowance. Randomizing the returned action cannot improve this minimax value.

This is not a lower bound when raw supports, additional paid levels or model-specific formulas are also supplied. Likewise, the exact absolute interval `[W,U+delta]` uses a class in which arbitrary additive shifts are still allowed. Those interface limitations are essential and are explicit in the source.

## 5. Novelty and execution boundaries

The prior R123 sources already contain intersect-before-integrate derivative envelopes, rounded-midpoint contraction, a conditional geometric localization rate, optimizer bracketing, remaining-gain ceilings and compulsory-cost stopping. R124 already contains exact scalar value/derivative interpolation without raw supports, a boxed rational residual certificate, bounded future-error transport, local minimax statements and refinement credits. These cannot be presented as new R125 inventions.

The checked R125 additions are the exact finite raw-support obstacle interpolation theorem and constructive proof; the complete finite-radius support-precision account and its explicitly scoped planning bound; the sharpened separation of terminal regret and absolute value precision; and the reduced-interface stationary-bracket calculation. The strict witness supplies an original-action consequence while acknowledging an equally informed cheap conventional calculation.

The frozen original-economy census does not implement the new support-complete conic solver. Its empirical runtime and action outcomes evaluate the separately defined adaptive acquisition service. They cannot be attributed to conic-program execution or be called a computational validation of that solver. No neural-specific superiority, generic multidimensional scaling, calibrated field adoption or independent refitting is established by this mathematical check.

## 6. Post-freeze singleton-target diagnostic

The separate diagnostic `reporting125/diagnose_terminal_gate125.py` was inspected after the primary experiment. It reads the already saved record and calls no economic primitive. Its selection is explicitly post-outcome. For the two warm-service records at the same cubic-marginal incumbent, the recorded action and certified optimizer bracket both equal the capacity `3/16`. A feasible left-displacement bound from the saved original support, transported to capacity by the proved original smoothness constant, gives the exact derivative upper bound `-6125769643636980517/65212122604324782080 < 0`. Convexity then implies that the capacity action minimizes the original `q`. The unchanged future controller therefore has original regret at most `delta=15/16777216`, below the stronger target, while its already paid absolute interval remains qualified.

The mathematical inference is valid conditional on the original support's validity. The smoothness formula was checked against the retained original marginal-regularity theorem, and a separate exact Fraction calculation checked the saved radius, curvature adjustment, negative capacity derivative, tolerance inequalities and unchanged action/classification flags. Its receipt is `TERMINAL_DIAGNOSTIC_REVIEW125.json`. This does not substitute for independent reconstruction of the original economic support.

The production implementation did not apply this direct bracket gate. Its frozen recorded target counts remain **231/232** for each warm service. The diagnostic makes no new action change, policy gain, population observation or economic evaluation, and it does not convert those recorded failures to successes. It identifies a future implementation amendment supported by the new terminal decision account; implementing and evaluating that amendment requires its own prospective boundary.
