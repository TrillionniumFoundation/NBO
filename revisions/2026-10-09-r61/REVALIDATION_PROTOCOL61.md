# R61 fixed-policy Bellman revalidation — 9 October 2026

The original Neural Bellman Operators paper and its economic primitives are unchanged. The controlling advisory review is 8f56a3ae24ef3ce4383d0e9d1d757bd3ed7378c6, reviewing R59 manuscript 00412e6a4f43100996b324ea1ace097232c3fbbf. R60 scientific records are pinned to c55d18af14ee1573a8e356021d2326fae703cd23; the separately frozen common-reference calculation is pinned to e94a8b867d6136ce14ba9697fc2288e0c7a7bc48. Both successful and unsuccessful predecessors are preserved.

## Selection before execution

This protocol is written after the R60 centered frontier has been observed, and before R61 fixed-policy bounds are calculated. It implements the revalidation already described in CENTERED_BELLMAN_AMENDMENT60.md. The collection comprises every returned R60 service with d=2 and T=2, on both workers, both declared training seeds, both initial-law targets, and all four generators. Exact equality of the entire policy-plus-partition identity permits one deterministic calculation for repeated actors. No policy is omitted because of its reported cost, unsuccessful target, generator, or anticipated bound. Duplicate actors are listed as aliases, not new observations.

The verification grid is fixed at N=128 cells per state coordinate and q=32 original-law innovation bins. The lower Bellman excess table is the deposited N=128, A=64, q=32 centered construction. Its exact raw-file identity is verified, and its complete construction is independently recomputed before use. No new lower grid is selected from the revalidation outcomes. The tolerance catalogue is 1/2, 1/4, 1/8, 1/16, 1/32, matching the centered amendment. All results, including failures, are reported.

## Upper recursion for the actual returned actor

Each stored partition is reconstructed and compared with its complete payload. On every verification cell, the actor range includes all intersecting acquired leaves and both closed endpoints. Neither midpoint interpolation nor differentiation of a discontinuous actor is used. The original quantum action indices and partition are never changed.

The signed zero-policy advantage is evaluated by the original centered primitive identities. Backward upper recursion transports excess values under the original continuous innovation law. Subtracting the common lower Bellman excess table gives an all-state bound for that particular returned policy against the original continuous-action optimum, not a gain relative to zero under an initial distribution.

Two upper recursions are retained. The first uses only outward primitive and rectangle bounds. The second additionally intersects each upper excess endpoint with zero. That intersection is permitted only after the full independent service reconstruction has established the original reference-advantage gate at every acquired cell and date; backward policy improvement then proves the returned policy nonworsening relative to zero everywhere. The unconstrained upper endpoints are retained, so this mathematical tightening is visible and cannot conceal an invalid enclosure or an unfavorable action. Every final gap is computed outward.

## Cost, identity and inference

All endpoint arrays, input identities, aliases, maximum datewise bounds, and target classifications are saved. Per-actor timings cover partition reconstruction, complete upper recursion and endpoint serialization. Whole-process import/log/durable-receipt overhead is recorded separately by the execution wrapper. The common lower-table reconstruction is a shared verification expense, also measured separately. None of these new clocks replaces, reduces or retrospectively changes an R60 prospective-service clock. Comparing different predecessor hosts as one fictional end-to-end execution is prohibited.

There is no retraining, new policy search, or new policy-cost sample in this calculation. Original stopping targets and stopping decisions remain fixed. Deterministic post-selection verification is not an additional statistical observation. It does not establish high-dimensional Bellman accuracy outside the executed d=2,T=2 case or a representation-specific advantage.

SOURCE_FREEZE61.json binds this protocol, the revalidation implementation and its disjoint regression tests to the unchanged R60 source freezes before any R61 revalidation output is written. Scientific corrections require an explicit amendment and preservation of affected attempts. Compilation and reproducibility are not external mathematical or editorial acceptance.
