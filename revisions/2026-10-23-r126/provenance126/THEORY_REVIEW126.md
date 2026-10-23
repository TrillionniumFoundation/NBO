# R126 author-side mathematical and validation review

**Review completed:** 2026-10-23T13:46:49.023468+00:00. **Finding:** no blocking issue found in the new mathematical results under their stated assumptions. This is an author-side review by a separate collaborating agent, with a second agent checking the direct-stopping and full cache proofs. It is not external peer review, an Econometrica editorial decision, or proof-assistant verification.

## Source and review boundary

The scientific baseline is R125 `eda26b02fbfb1e02807bc0cee1c0015d62d59e56`. The independently commissioned controlling advisory report remains R97 `9723c6cd2cc8b3e071422f3e522d4a843946db63`. The two scientific execution boundaries remain distinct:

| Boundary | Commit | Read-only closure check in this review |
|---|---|---|
| F126 | `769e3eb3ac08beaa7bb6778c1676f15e1f8d6d2b` | All 538 manifest entries match |
| F126C | `9c6246ecad31acd6a937a2d8ad4710bcabc8c801` | All 546 manifest entries match |

There were zero missing files or hash mismatches. The adjacent [machine-readable review](THEORY_REVIEW126.json) contains every frozen input hash and a snapshot of all 21 current `new126` TeX files, all four `code126c` files, the R126 code, protocols, integration documents, and selected validation receipts. Hashes establish byte identity, not mathematical correctness. The additional proofs are author exposition after the scientific freezes; they do not retrospectively preregister a result. No economic evaluations, model fits, or timing runs were performed for this final review, and no frozen code or protocol was changed.

## Mathematical findings and necessary scope

| Component | Verified argument | Limits retained in the manuscript |
|---|---|---|
| Original-action stopping | Feasible projected-gradient gap, transported optimizer bracket, stationary-root quadratic route, separate absolute-value interval, actual rounded-midpoint bound, strict original-policy replacement with one future allowance | Smooth scalar strongly convex original objective; arbitrary future error is not differentiated; finite budgets need not attain the stronger target; actual failed work and fallback remain paid |
| Finite complete-support certificate | Shared support slope, rational subgradients including constant-curvature case, nonnegative cut aggregation with exact box residual, finite-grid regret sandwich and sharp `1/8` constant, exact cell maximum | Solver success is unnecessary for validity; a verified primal witness is necessary for a checked numerical gap; no finite accuracy or convergence rate follows from the capped numerical run |
| Class and economic information | Raw dual bound describes the encoded support class; an additional original-optimum floor may tighten the actual original-objective bound | Intersecting with a floor absent from the class does not certify a tighter solution of the larger-class extremum; conventional comparator receives the same cap, supports and floor |
| Paid stopping and robust actions | Strong convexity and Lipschitz continuity of compatible worst regret; conditional robust-action grid error; a compulsory-cost stopping dominance result | Near-minimax accuracy requires checked pairwise gaps; the resource price and unavoidable cost must be supplied; no reuse across decisions is allowed by that dominance statement |
| Independent finite-design audit | Box-tangent least-squares lower bound, normalized weak-dual marginal bound, feasible lattice rounding and design-specific perturbation inequalities | Fixed acquired labels and features; 48 solves plus eight matched hinge copies; shared SciPy/HiGHS libraries; no independent economic reacquisition or whole-domain critic certificate |
| Exact geometry reuse | Full and clipped all-crossing partition identity, exact primitive differences, gradient/root/raw-minimum equivalence, complete keys, induction over service decisions | Finite nonempty rational records, feasible arguments, immutable normalized cases and strong references; same original oracle outputs; no timing-dependent scientific decision; no guarantee against machine-resource failure |
| Geometry work and custody | At most `1+s+binom(s,2)` derivative pieces; `O(s^3)` inherited construction; explicit per-key, per-query, output, key-formation and storage account | Rational bit cost and hash-table internals are additional work; no uncached lower bound or uniform runtime advantage; cache begins empty and is cleared in every individual paid service |

The raw-support envelope can have downward derivative-interval kinks. Its proof enumerates affine pieces after subtracting the common quadratic; it does not incorrectly assume that envelope is convex. Coincident lines create no isolated crossings, and the inherited tie rule is retained. These details are essential to both the identity statement and the operation count.

The ideal nested-relaxation convergence proposition assumes exact subproblem minimization, a cut for every constraint at each iterate, retained cuts, compactness, continuity and bounded selected subgradients. Its conclusion is value convergence, with **no convergence rate**. The implemented capped solver is justified by the finite rational certificate alone.

## Validation evidence and its provenance

The reviewed receipts distinguish synthetic algebra, reconstruction of executed records, and the economic experiment. Existing synthetic work includes 1,465 exact support-fixture checks on 24 piecewise quadratic witnesses with six deliberately corrupted certificates rejected; 1,375 separate-comparator cross-checks on 25 abstract cases; two abstract solver witnesses; 65 fitting algebra/feature assertions; and 57 direct-service checks on 24 quadratic cases including a narrow-regret/wide-value counterexample. None acquired new economic outcomes.

For the frozen cache source, `STATIC_CACHE126C_attempt03.json` records 660 exact geometry fixtures, and `STATIC_CACHE_SCHEMA126C_attempt02.json` records 528 comparisons with already executed F126 timing records. The unnumbered and earlier cache fixtures refer to earlier pre-freeze source snapshots. The initial schema failure is retained, and the final full-record exclusions were fixed before C economics. The direct fixture receipt `STATIC_VALIDATION126_attempt02.json` matches the frozen direct-service implementation; it does not purport to validate every file later amended before the freeze.

The existing postexecution support audit independently reconstructed 33,331 cuts for 888 contrasts, with 1,924 exact record checks, and did not claim finite solver optimality. The distance audit checked all 2,112 original records using exact squared binary-rational inequalities; a valid distance upper bound is not a measured action error. The separately executed C verifier checked all 4,224 complete scientific records against F126 and their distance bounds, excluding only declared clocks and run metadata. This final review read and hashed those receipts; it did not rerun their experiments or convert their assertions into independent label acquisition.

## Integrated economic claims and remaining limits

The revised main text retains the initial direct-service timing loss and the distinct prospective C boundary. The later algorithm receives the same implementation optimization in conventional and neural services. Its paired complete cost is distinguished from the initial service-component clock. Cached direct still has greater nine-state complete cost than cached warm; its policy outputs and acquired economic information are unchanged. Exact ReLU/hinge equivalence continues to block neural-specific attribution.

Production qualification, an independent original-objective audit, and interval containment remain different claims. Cache identity supplies no new independent value-width confirmation: the original 307 unresolved regret checks, 1,113 unresolved containment checks and 250 unresolved policy orderings remain unresolved. The support solver's 48 tighter contrasts and six tighter regrets are retained alongside zero newly qualified strict gains. Fixed-state shared-host ranges are descriptive, and the deterministic state census is not a population sample.

The inherited Bellman foundations, nonlinear recursive-utility and stochastic-control connections retain their stated original assumptions and economic identities. This review does not claim to have independently re-proved every historical theorem. No general neural representation advantage, unrestricted information lower bound, universal speedup, population effect, or guaranteed optimal acquisition schedule follows from the new results. Full-document build, PDF hashes, layout and CI claims belong to their separate execution receipts. Later editorial assembly must be bound by final package hashes; this report is an explicitly dated source snapshot.
