# R119 prospective independent validation and exact supporting protocol

**Status at writing:** source and catalogue preparation only. No R119 supporting-study or original-economy audit observation has been acquired by this validator. An immutable R119 commit containing this protocol, the implementation, and all dependencies must precede execution. The author will copy this file unchanged to `revisions/2026-10-18-r119/VALIDATION_PROTOCOL119.md` before that commit.

This protocol supplements the separately frozen original-economy primary and timing campaign. It does not replace that campaign, any R98–R118 independent episode, the R115 committed actor/sample population experiment, or any older observation. The exact supporting class below concerns a theorem about continuous uniform risk and point information; it is not the original investment economy and supplies no observed economic-policy improvement.

## 1. Implementation and execution identity

The assigned validator is `code119/independent_tail119.py`. At this protocol's initial writing its SHA-256 is `95eba66a6cfcd4e01afce85b8b087fcc0727b468278428929a6938137d0fd524`. Its only pre-execution mechanical check was Python AST parsing, which neither imports nor executes scientific routines. The contemporaneous `code119/active_tail119.py` SHA-256 is `46891fdc2153bc449a4000ec28798f44c40d1bb70ce7bb433bfda43de8951b1e`; the actual prospective Git commit remains authoritative if the author makes documented pre-execution source edits.

Each mode requires `--custody-commit` with the full prospective 40-character Git SHA. Before scientific imports or observations, the validator compares all bound files to the exact committed bytes with `git show`, verifies the inherited freeze manifest hashes, and writes `PROVENANCE119.json`. A new, nonexistent output directory is mandatory. It refuses to overwrite a prior execution or failure.

Run after the author's source-freeze commit, using its actual SHA in place of `COMMIT`:

```bash
python code119/independent_tail119.py supporting --custody-commit COMMIT --output results119/supporting_tail119
python code119/independent_tail119.py audit --custody-commit COMMIT --output results119/independent_tail119
```

The author must capture stdout, stderr, return code, and actual command externally as well. Run these diagnostics separately from the primary timing campaign. Diagnostic elapsed time is execution evidence, not a competitive service-time observation. A binding/acquisition failure is retained and is not a scientific observation. Any rerun has a new output directory and an explicit reason; failed scientific cases are never removed or silently repeated under a changed protocol.

## 2. Exact supporting catalogue: 320 fixed cells

The support is always `[-1,1]`. Every function has the fixed form

`f(z) = q*z^2 + b*z + c + sum_j w_j * max(0, z-k_j)`.

All coefficients, knots, values, integrals, and query positions use `fractions.Fraction`. The following ten formulas remain identical across risk levels and budgets. The declared `K` is known equally to both algorithms. A positive valid upper bound is used for the constant function.

| Function | q | b | c | (knot, weight) pairs | K |
|---|---:|---:|---:|---|---:|
| constant | 0 | 0 | 3/7 | none | 1 |
| increasing_linear | 0 | 1 | 1 | none | 1 |
| decreasing_linear | 0 | -1 | 1 | none | 1 |
| centered_quadratic | 1 | 0 | 0 | none | 2 |
| shifted_quadratic | 1 | -1/2 | 1/16 | none | 5/2 |
| one_hinge | 0 | 0 | 0 | (1/3, 1) | 1 |
| shifted_absolute | 0 | -1 | -1/5 | (-1/5, 2) | 1 |
| flat_bottom | 0 | -1 | -1/4 | (-1/4, 1), (1/3, 1) | 1 |
| curved_two_hinges | 1/4 | -1/3 | 1/7 | (-1/2, 3/5), (1/4, 7/6) | 29/15 |
| curved_three_hinges | 1/8 | -3/4 | 2/5 | (-3/4, 1/4), (-1/8, 1), (5/8, 1/2) | 5/4 |

Risk levels are exactly `0, 1/2, 3/4, 7/8, 15/16, 31/32, 63/64, 255/256`; nominal quadrature parameters are exactly `n = 8,16,32,64`. Their Cartesian product has 320 cells. There is no fitted parameter, random sample, training stage, selection set, or test-driven function choice.

### Exact-point active-tail algorithm

The algorithm receives only an exact point-value oracle, `K`, the uniform law, `alpha`, and `n`. It does not inspect formula coefficients, derivatives, integrals, or the independent quantile solution. Set `m=ceil(log2(n))` and `t=1-alpha`.

For positive alpha it evaluates the two endpoint signs of `D(u)=f(u+2*alpha)-f(u)`. It uses the appropriate endpoint when that sign certifies an endpoint optimum; otherwise it makes at most `m` sign bisections. An exact zero exits early. If no exact exit occurs, the selected cut is the final bracket midpoint and the localization allowance is `K*t/(2*4^m)`. Endpoint and exact-zero exits have zero localization allowance. Alpha zero uses the full support and no cut search.

Each nonempty selected tail of length `b` receives `ceil(n*b/(2*t))` equal cells. Midpoint values give its lower integral and endpoint secants give its upper integral. Duplicate exact point locations are cached within that method and cell. Both total requests and unique acquired values remain in the output; no cache is shared between methods or catalogue cells. Zero-length tails are skipped in this theorem algorithm, unlike the separately paid vectorized original-economy implementation.

The prespecified width upper bound is `K*t*(n^-2 + (1/2)*4^-m)`. The point-query cap is `N=2*n+2*m+8`, including localization and quadrature. Every paid location and exact answer is retained. Constants, ties, exact exits, narrow-tail behavior and cases with a weaker observed interval remain in the catalogue.

### Conventional comparator and information fairness

The conventional algorithm has the same uniform law, same convex/Lipschitz class, same exact point oracle, and same upper cap `N`. It uses `B=floor((N-1)/2)` equal cells over the full support, queries their midpoints and distinct endpoints, and forms the ordinary convex-order AVaR lower bound from the midpoint distribution and upper bound from the equal-mass left/right endpoint mixture. A fractional atom at the tail cutoff is integrated exactly. It uses at most `2*B+1` distinct values.

This comparison matches the allowed query budget, not an invented equality of realized work: actual active-tail and whole-support counts can differ, especially at an early exit. The whole-support algorithm knows `K` but is not claimed to use all possible class information optimally. Neither arm receives formula access. No neural-specific representation advantage or floating-bit complexity result is inferred.

### Independent exact truth and required comparisons

Truth is computed independently from the formula. The central-integral derivative is piecewise affine because the global quadratic coefficient is common to every piece. The truth routine enumerates both admissible endpoints, all hinge knots and their shifts by the central length, and every affine zero between consecutive breakpoints. It minimizes the exact polynomial central integral over that complete candidate set. It then integrates the exact two tails. This procedure uses neither the algorithm's query transcript nor its bisection cut.

For every cell report exact AVaR, exact quantile cut, selected-tail integral, localization error, both interval endpoints, lower and upper errors, width, theorem width bound, requested and unique query counts, localization exits, cells and full transcripts. Check that both reported intervals contain the exact original-law AVaR; the active-tail width, localization defect, cell count and cell lengths satisfy the theorem; and both methods respect their common query cap. Report all width wins, losses and ties.

The column `K*t/[6*(N+1)^2]` is the theorem's minimax lower bound over consistent functions. It is not asserted as a lower bound on the width for each fixed displayed function; for example a constant function may be identified more accurately on this input. These 320 exact cases support executable correctness and illustrate constants. They do not prove worst-case complexity or create an empirical population distribution.

## 3. Independent audit of constrained scalar minimization: 880 cases

Compare actual `active_tail119.constrained_gain` output with an independent exact Fraction minimizer of `g*d + curvature*d^2/2` on the original feasible displacement interval. The exact minimizer is independently clipped to that interval. For a slope interval, the maximum gain is evaluated at both endpoints; nine fixed evenly spaced slopes additionally check coverage within the interval.

The Cartesian catalogue consists of:

- Intervals `[-1,1]`, `[0,1]`, `[-1/32,0]`, and `[-1/32,-1/64]`.
- Anchor relative positions `0,1/4,1/2,3/4,1`, including both constrained endpoints.
- Curvatures `1/16,1,181/64,8`.
- Eleven dimensionless slope intervals: `[-2,-2]`, `[-1,-1]`, `[-1-e,-1+e]`, `[-1/4,1/4]`, `[0,0]`, `[-e,e]`, `[1-e,1+e]`, `[1,1]`, `[2,2]`, `[-2,2]`, `[-3/4,-1/2]`, where `e=2^-40`. Multiply both endpoints by curvature times interval length.

There are exactly 880 rows. Realized binary floats are converted with `Fraction(float_value)`. Require a finite nonnegative production upper bound no smaller than the exact endpoint-slope worst case. Retain the exact gain, production bound and excess. These include slope uncertainty around projection boundaries and zero, not solely unconstrained stationary points.

## 4. Actual production dyadic-density audit: 228 cases

Audit the arrays returned by the actual production `tail_mesh` used by `certificate`, comparing every midpoint, edge and weight to an independently constructed exact rational mesh.

The original shock support is `[-1/32,1/32]`. Alpha is `1/2` or `3/4`; `m` is `2,4,8,16,32,64`. For each risk use the 17 cuts evenly spaced across the full admissible cut interval, including both endpoints, plus the two cuts one `2^-32` step inside those endpoints. All 19 cuts satisfy the declared dyadic32 grid. This gives `2*6*19=228` rows.

Check exact binary equality of all edges, midpoints and weights; exact unit mass; nonnegative weights; strictly positive weights in every nonempty tail; and zero weights only for the empty tail at an admissible endpoint. The production implementation intentionally evaluates those empty-tail nodes and must continue to charge their cost. The feasible density is exactly `1/(1-alpha)` relative to the original law on the two tails, zero in the central interval.

## 5. Original-investment independent finite audit: 24 contexts, 72 resolutions

The original economic primitives, continuous uniform risk, beta `15/16`, feasible capacity and implemented terminal-controller allowance `2^-20` remain unchanged. The fixed states are:

| State | Dimension | Coordinates |
|---|---:|---|
| zero2 | 2 | (0,0) |
| one2 | 2 | (1,1) |
| asymmetric2 | 2 | (1/8,7/8) |
| mixed4 | 4 | (0,1/2,1,1/4) |

For each state, use both original risk levels `1/2` and `3/4` and three fixed realized actions: zero, half the exact capacity, and exact capacity minus `2^-36`. The last is explicitly a near-capacity action, not mislabeled an exact boundary action; it remains below the inherited outward capacity lower endpoint. Exact boundary minimization is separately covered by Section 3. These 24 contexts use all `m=2,8,32` production tail resolutions, giving 72 certificate rows. Qualification is observed and retained; no requirement that every deliberately poor action qualifies is imposed.

The production floating cut is an examined proposal, not independent truth. At its two endpoints and every selected cell midpoint/endpoint, the independent checker uses the retained `independent94.py` implementation, which imports no production interval, risk, feature or optimization module. It reconstructs terminal polynomial coefficients from original primitive values, checks the original quadratic shock coefficient is exactly 5, integrates the original terminal risk through its exact polynomial threshold identity, and brackets the terminal optimum by exactly 32 rational bisection steps with the original strong-convexity bound. Every queried rational terminal context and result is retained, including independently reconstructed polynomial, feasible action, derivative and threshold tails.

For each original state/action/risk context an independent whole-support reference uses exactly 64 cells, rational midpoint lower values, and the repeated endpoint upper-value mixture. It computes separate bounds for the optimal-continuation objective Q and for the complete implemented policy J; only the latter adds the unchanged discounted terminal-controller allowance. These are reference intervals, not exact observations of J or V0.

The checks are:

1. Production residual endpoints contain the independent endpoint-difference enclosure; production kappa covers independently minimized constrained gain divided by the original tail mass.
2. Independent rational selected-tail midpoint/secant bounds lie within the outward production selected-tail bounds; original stage, beta and terminal-controller allowance aggregate in the correct direction.
3. The independent whole-support original-policy interval overlaps the production interval.
4. The production optimum lower endpoint is no larger than an exact Fraction minimum of its supplied witness and uncertain slope over the full exact original feasible capacity. The loss and width arithmetic are outward.
5. Every supplied minorant is checked at all three fixed actions against the corresponding independent feasible Q upper interval.

Strict enclosure checks are conservative sufficient implementation checks. A failed strict enclosure is retained and investigated; it does not by itself distinguish a false certificate from two valid but nonnested numerical enclosures. The independent whole-support overlap and finite cross-action checks detect inconsistencies; they do not establish a global theorem or certify an empirical exact optimum. Global supporting-minorant validity and continuum coverage remain mathematical obligations of the supplement.

## 6. Output, retention and interpretation

The supporting mode writes all 320 cases to `SUPPORTING_TAIL119.json`. Audit mode writes `INDEPENDENT_TAIL119.json`, including all scalar-minimization rows, density rows, original reference intervals, certificate rows and rational primitive records. It also checkpoints stage completion in `AUDIT_PROGRESS119.json`. Both modes write source provenance and execution receipts; exceptions create `FAILED119.json`. Failed inequalities accumulate rather than being omitted. A final success status requires every declared check and catalogue count to pass. External logs and return codes are retained by the author.

No stochastic confidence interval is attached to these deterministic finite catalogues. No timing CI is synthesized from diagnostic runtimes. Actual comparisons of economic objectives, returned actions, service costs, strong representation baselines and adoption remain in the separate original-economy primary/timing protocol. No old R117/R118 observation is credited to this R119 protocol.

## 7. Complete source dependence closure

The validator binds these six R119 files to the actual prospective commit:

- `code119/independent_tail119.py`
- `code119/active_tail119.py`
- `VALIDATION_PROTOCOL119.md`
- `PROTOCOL119.md`
- `REVISION_BOUNDARY119.md`
- `frozen108/SOURCE_FREEZE108.json`

It also binds and verifies all 14 inherited files named in that unchanged freeze manifest. The list is intentionally slightly wider than the audit's dynamic imports so that the inherited science identity remains intact:

| Path below frozen108 | SHA-256 |
|---|---|
| code/continuum94.py | 0c2d20acda04903d45e3d641dc8da0162c7198712efc1e464e53a4e61f57bd3f |
| code/independent94.py | a1a0e4ce5563d1105c3cea9eaad6678c609229446ba6794f7b8a7c03df01ebad |
| code/interval94.py | 55cf99152dad7ebf25c0155810d93467f9c4bc9ffb566e4f0966d60d1bde6588 |
| code/investment94.py | 4e926df04795b086a47023edfa2c7e1aed4cdfe2acaa3bdcd35225f55d632b82 |
| code/matched96.py | 16376b4bd97b0206c30df67286263360b9cf429cce0b35a604ed5e1554292374 |
| code/quadrature96.py | 9b8dd5588cce4f99f868ca275d929cc37308255c4277cb80a6f7bd260f48062b |
| code/rational96.py | b13345f267a047a1dbb0d33fefa870333bacdfcb9bf51fda5fe968d9b800020d |
| code/representations94.py | 9eb65d513ea9e5f5cb6435ede626ca13bf8ccb819fd74176f1d167e7d7a6898f |
| code108/audit108.py | f6c83ef60e5a0155bf91af81c31993edc8cbc5a1c547552028640a34cff5e1da |
| code108/campaign108.py | b24016072d9ced0efb49650561f0922957def2f2c0dc1dead997c956af52a2ff |
| code108/kernel108.py | c26c6bd89326dee308b700d5ba6a2097d382b332aee59f8f54b9e4ed77917965 |
| code108/represent108.py | a8268985fe9bba3abfadd6125cf6a773a7bdec306454626df3518b0ab318d9dd |
| code108/test108.py | 92ba484921dbe61520fe369b06dc1ac6f52e2207459d65ad87cd8e179c8966a9 |
| new/study97.py | db947fbbe20a92f38d8b5b95e4f5d733f8a3162df30d2f670e13a472b493baba |

The supporting algorithm and formula truth use the Python standard library only. Audit mode additionally imports NumPy and the bound production dependency closure, which includes SciPy through inherited modules. Runtime Python, NumPy and platform identities are recorded. The theorem source and source-freeze manifest for the entire new primary package are separately maintained by the author; this validator does not modify them.
