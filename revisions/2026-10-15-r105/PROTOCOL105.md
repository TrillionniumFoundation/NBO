# R105 prospective postqualification cost-descent experiment

This is an additional experiment, not an amendment or replacement of R104. Its design is made after observing R104's completed fixed-catalogue results. In particular, R104 repair reduced conventional fallbacks but could have higher final policy cost than the online fallback. That observation motivates this experiment and is not hidden behind a preregistration claim. The hypotheses, catalogue, services and thresholds below are fixed before R105 execution. R98 and R100-R103 remain separate.

## Identity and target

Retain the original two-date investment economy, d=2, S/g/h, beta=15/16, feasible investment interval, continuous uniform innovations [-1/32,1/32], nested AVaR levels 1/2 and 3/4, complete inherited terminal controller, original-optimum tolerance 1/256 and cost-width target 1/8192. Use exactly the eight actors acquired by the unchanged R104 code under protocol fbddd01b3b91d220b6b9a913f71f3f4486aa8248. Serialize and hash every actor before this experiment. Do not refit or select them using the new catalogue. Their entire shared-label, fitting, rejected-candidate and fitting-audit expense is charged to standalone service comparisons; reuse for this experiment is declared, not free information.

The new catalogue is the full 8 by 8 Cartesian product of ((3*i+1)/24 for i=0,...,7), ordered lexicographically. Executed binary64 coordinates are retained as exact input observations. It is disjoint from both R104's 16 by 16 training midpoint grid and its 8 by 8 evaluation midpoint grid. Numerical mean intervals describe this entire deterministic equal-weight catalogue, not random-sample population confidence intervals.

## Three complete services

For each of the eight fixed actors and two risks compare:
1. the unchanged R104 fast_legacy complete service;
2. that same qualified service followed by fixed-128-bin cost-only descent;
3. that same qualified service followed by adaptive-bin cost-only descent.

Postqualification is essential: the incumbent is already a complete qualified policy. Preserve its original-optimum lower bound B. Only exact-fallback rows or rows with incumbent regret upper bound <=2^-16 skip descent. The skip rule is a fixed computation budget choice, not a claim of exact optimality.

For the remaining rows, form a clipped support step a-s/2, with s the midpoint of the incumbent's original-law slope interval. Try displacement factors 1,1/2,1/4 from this same incumbent, rounded downward to the existing 30-bit action grid and feasible capacity. Stop after the first accepted candidate. Identical actions are skipped. A candidate is accepted only if its valid original complete-policy cost interval [L,U] has U < incumbent L0 and width <=1/8192. Then reuse B and require U-B <=1/256; a contradiction fails the run. Retain the incumbent on all refusals and exhaustion. These comparisons concern the same terminal policy and original law.

A cost-only query reuses the inherited midpoint/end-point continuous-risk enclosure and terminal certificates but does not form a new root all-action quadratic minimum. All terminal, risk-sorting and interval work is charged. The fixed service queries at 128 bins. The adaptive service queries at 8,16,32,64,128 bins, intersecting successive valid intervals. It may stop and reject a candidate when its lower endpoint is at least the incumbent upper endpoint; otherwise it refines until acceptance or the 128-bin budget. Contradictory interval intersections fail closed. Every failed candidate, bin level and refused comparison remains recorded. Different accepted actions across the two services are reported, not masked as execution-only identity.

## Outcomes and timing

Execute all 64 states, eight actors, two risks and three services: 3072 final decisions if successful. Record baseline and final actions, actual policy-cost intervals, retained optimum lower bounds, loss/width, accepted gains, every proposed displacement, precision, refusal, skip, root-minimum count, primitive/risk/continuation operations, wall time and process memory. No row is dropped. Strict improvement counts require disjoint cost intervals, not a reduced regret upper bound. Catalogue mean cost gains use outward rational accumulation of interval endpoints. The comparison against the fixed-128 service includes all refused/refined work, not merely accepted queries. Conventional actors receive exactly the same rule as neural actors.

Run seven sequential fresh-process timing repetitions, each evaluating the complete three-service menu on the first 32 new catalogue states, using one computational thread. Record all repetitions, operations, process clocks, CPU metadata and memory. Report descriptive medians/ranges, not inferential confidence intervals for hardware. Do not pool these new clocks with R104 clocks. Report acquisition as a separate full standalone charge in addition to per-service work. No empirical adoption prices or calibrated welfare margins are invented.

## Verification and scope

Before primary execution, deposit actual executable source and its hash. Reproduction must verify the previously frozen R104 code and actor hashes. Independently check all recorded strict-descent gates, unchanged-action identities, global-bound reuse, targets and exact-rational mean intervals without importing the descent selector. Verify the new tail-switching and shared-allocation examples using separate rational calculations. Preserve any failure and record a nonretroactive amendment before changing frozen scientific code.

This experiment tests value-improving postqualification and its work cost in the original economy. It neither proves a neural-specific representation advantage nor supplies R98's independent population sample, a longer-horizon tournament or external economic calibration. The main paper remains Neural Bellman Operators with its original theoretical and Econometrica objectives.
