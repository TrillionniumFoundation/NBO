# Prospective R124-B design audit

## Scope and stage identity

This is an author-side review of the prospective R124-B design after the completed R124-A findings and before a B source boundary or independent B draw exists. It records no B outcome and changes no A source, sample, clock or audit. The current code snapshots below are provisional source identities, not a scientific freeze.

The B comparator is the complete published `service123.service(..., 'fused')` service. All three B arms recompute and pay that entire service. This is stronger than A's two-candidate fused comparator, so an internally valid B improvement is not a direct relabeling of the A experiment. Published R123 source can be used without importing its separately constrained sample or outcomes.

| B arm | Actual own-stage baseline | Required paid work | Valid gain scope |
|---|---|---|---|
| `fused_full` | Original qualified actor incumbent before the full fused menu | Entire original actor, all original queries and full fused menu | Original incumbent minus completed fused policy |
| `bridge` | Completed `fused_full` policy | All fused work plus common new-menu construction and the entire bridge stage | Completed fused policy minus completed bridge policy |
| `joint` | Completed bridge policy | All fused work, the complete bridge stage, and every started joint solve | Completed bridge policy minus completed joint policy |
| Additional cumulative comparison | Completed `fused_full` policy | Full joint service; no subtraction of inherited service costs | Completed fused policy minus completed joint policy |

`stage_incumbent_action`, its exact hexadecimal encoding and its original-value bounds must refer to the actual preceding implemented policy. The separate `original_incumbent_action`, `fused_action`, `bridge_action`, nested stage answers and complete `full_fused_record` make that distinction inspectable. Paired records must verify that each recomputed nested incumbent equals the corresponding independently executed preceding arm.

## What the new rule can and cannot establish

The cheap bridge uses original Bellman values at paid anchors and strong convexity. Its upper bound is the strong-convex chord bound; its quadratic minimizer is clipped to the anchor segment. The implemented formula `1/2 - (U_t-U_s)/(mu*(t-s)^2)` is the correct normalized minimizer. The midpoint and six feasible neighboring actions are deterministic menu members. The entire new menu is fixed at the completed fused action and reused by bridge and joint; a joint solver does not get to change its competitors after seeing its own proposal.

A strictly positive lower bound for the original implemented-policy difference, together with the same qualification requirements, supports a real action improvement. Returning the actual preceding policy on an unqualified candidate or numerical failure gives the nested weak order conditional on valid original numerical premises. This is not an unconditional optimizer-convergence statement. A positive common-information result would be an improvement in the Bellman decision service; the value geometry is available to quadratic, spline, hinge, grid and neural representations alike and establishes no architecture-specific advantage.

The two-distinct-anchor gate is a declared experimental restriction. It is not a theorem that every single-anchor problem is saturated. Every ineligible state remains in the complete population denominator with its actual retained policy and cost. A conditional table of eligible states must not replace the prespecified all-state confidence family.

Matched ReLU and ordinary-hinge models have identical feature and readout data. Their implementation clocks may differ, and the inherited hinge charge includes its ReLU-parent construction and audit. Such engineering/allocation differences cannot establish an intrinsic neural representation or information advantage. A newly optimized independent hinge-fitting implementation remains a separate scientific comparison; this B design does not claim to have executed it.

## Inference check

The 32 newly drawn initial states, conditional on the frozen B design and inherited models, are the independent units. The methods, risks, representations, service stages and timing repetitions do not increase that sample size. A design informed by A is compatible with prospective inference on a separately frozen, independent B draw, provided the dependency is disclosed.

There are 174 own-stage safe-gain cells and 58 additional cumulative joint-versus-fused cells, giving 232 safe means and 232 certified-event probabilities. Each gain lies in `[0,tau]`: even the cumulative gain is at most `tau` because its completed fused baseline is already within `tau` of the same original optimum. Summing the bridge and joint certified lower gains is a valid telescoping lower bound; it does not enlarge the true support to `[0,2*tau]`.

The safe radius `7*tau/16` at `n=32` gives Hoeffding exponent `49/4`. The 348 signed comparisons (174 versus same-risk online/full-fused and 174 versus same-budget quadratic/VALUE/full-fused) have support `[-tau,tau]`; radius `7*tau/8` gives the same exponent. With exact rational arithmetic,

`sum((49/4)^j/j!, j=0,...,30) = 26617843732923156515942847184319813955674666954261401 / 127370148369821061520493558366195920404480000000 > 208980 > 46400`.

Thus the 232 two-sided safe means have total failure below 0.002221, the 348 signed comparisons below 0.003331, and 232 one-sided Clopper–Pearson lower bounds at `alpha=1/23200` have total failure at most 0.01. The sum is below 0.015551, so a declared joint coverage of at least 95% is conservative. Dependence across methods is allowed by the union bound. The event threshold remains `2^-24`, and the 48-step exact rational lower bisection must be retained. No unregistered post-outcome interval should replace this family.

Unlike A's radius larger than `tau`, the proposed signed radius `7*tau/8` can in principle exclude zero. Whether it actually does is an execution result. Same observed actions imply an exact sample difference of zero; only mathematical identity of the compared method permits a population identity of zero.

## Complete cost and sample matching

The expected complete census is 5,568 primary decisions (`58*3*32`), 4,176 timed decisions (`3*58*3*8`), 174 policy cells and 696 clock cells. Each timing process uses the same first eight states for its economic means and cost denominator. At four declared reuse volumes there are 2,784 exact standalone cost scenarios.

Each neural purchase menu must include every same-risk non-ReLU policy and every service stage: 75 conventional competitor cells per clock. With 24 ReLU policy cells, four volumes and five clock groupings, the full catalogue has 480 domains and 50,400 inequalities per endpoint family. Both sufficient and optimistic domains, including empty ones, remain in the output.

The standalone formula must retain inherited acquisition, full process residual, cold load and the complete cohort time. The joint arm's bridge work is included in its own measured cohort; it is not reused for free from a previously executed arm. Common new-menu construction is outside the stage-only timer but inside the complete service timer. A stage-only clock therefore cannot substitute for the whole decision-service cost. Actual research accounting counts whole processes once and does not sum alternative standalone allocations. Large reuse volumes remain extrapolations, and historical unknown costs remain unknown.

## Prefreeze issue and required checks

The initial `stage()` implementation catches local failures into `bridge_stage.failure` or `joint_stage.failure`, while the outer `enhancement_failure` can remain null. A reporter copied from A that counts only the outer flag would hide retained local failures. This was sent to the numerical owner before freeze. The prospective report must count fused, bridge, joint and outer failures separately or expose a correctly aggregated failure flag, while preserving all partial candidates and elapsed cost. The existing policy fallback is appropriate: a completed bridge remains the actual joint incumbent.

Before B source freeze, the full protocol/report code and failure handling require a second read. After the independent B draw and terminal report, the separate publication audit will bind source, sample and model Git identities; reconstruct actual nested baselines and cumulative gains; independently recheck every reported rational mean, confidence endpoint, cost scenario and complete purchase domain; and preserve all failed attempts. The fixed A auditor and its receipt will not be edited.

## Provisional source snapshots

- `code124b/common124b.py`: `d23ecdcf436860a71bf7c76f93e7ccf6c6e576e133f990dcce06b035aed00d5f`
- `code124b/service124b.py`: `ee5d18d01b7219093f628857403995f6a64896297d1c3e8ee96bfdeab7fba619`

Observed at 2026-10-23T05:50:13.741495+00:00. These hashes do not assert a source freeze or completed experiment.
