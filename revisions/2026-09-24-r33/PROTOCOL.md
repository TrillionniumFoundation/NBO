# R33: global-cost bounds and unrestricted revision certificates

Date: 2026-09-24. Repository: TrillionniumFoundation/NBO.
Frozen parent: de8a54b7367101e079b7001a98098c2800e4d4b0.
Source referee: reviews/2026-09-24-econometrica-r30/referee_report.md at e9bc144fbb6843d6a3436825a28584efb64fb8f1.
Existing R32 executed package: Actions run 35969341278, source 6bd65d5d5db242def26d61746aaef7d4da26f2da, artifact 10795880408. Its results are inherited evidence, not newly generated R33 observations.
Destination: revision/econometrica-r33-global-cost-bounds-2026-09-24 only. Existing revisions and review branches are not modified.

## Scientific increment

Construct class-free lower bounds on the true minimum intervention cost under the unchanged all-state/all-restart operating-regret constraint. For each nonnegative rational multiplier, solve the unrestricted Bellman problem maximizing multiplier times operating return minus implementation cost. Combine its support values with a constructively computed operating lower witness to bound every feasible policy, including randomized and history-dependent alternatives. Independently test candidate policy values against the operating upper witness and report a certified primal-dual cost gap. No strong-duality or global-optimality claim is made merely from multiplier search.

The lower witness must be built from primitives and a checked upper-witness compression defect, not read from an optimal-value file. Charge witness construction, all multiplier solves including unsuccessful candidates, exact own-policy evaluation, finite encoding and independent checking. An exact structured operating DP is an additional information-matched control and diagnostic; its values do not construct the primary witnesses or support policies.

## Fixed computational design, before R33 outcomes

Use unchanged R32 maintenance primitives; horizons 4, 8, 12; operating tolerances 1/100 and 1/20; all seven installed proposals (three retained neural seeds, two splines, all-defer, separately labelled occupancy stress). Use multipliers 0, 1, 4, 16, 64, 256, 1024, 4096. Build a shared operating upper witness at witness-accuracy parameter 1/10000 with the inherited compression rule (per-stage compression allowance one quarter of its stage budget). This gives 168 unrestricted support computations and 42 final horizon/proposal/tolerance summaries. Preserve every multiplier outcome and every rejected or capped computation. Piece cap: 200000, unchanged. If that cap binds, report the unresolved configuration rather than replacing the model or deleting it.

Policies are compiled exact piecewise-constant functions with isolated endpoint decisions. All-state checks cover open-cell limits and every knot. A feasible new deployment may be compared with the inherited class-minimum and zero-intervention candidates, but its value and cost must be recomputed from the unchanged primitives. Selection minimizes uniformly integrated intervention cost among the complete finite set of verified candidates; this finite selection is not claimed to optimize all feasible policies. The cost lower bound concerns the unrestricted feasible set and is kept distinct from finite candidate selection.

## Preservation and reporting

Retain the full R32 main text, proofs, supplementary derivations, original stopped-economy target, historical annex, adverse neural/classical results, protocols and failed attempts. Add substantive theorem/proof and computation sections, update the introduction and response map, and preserve an exact old-to-new content map. The original stopped-economy global upper bound is not improved by changing the maintenance objective. No unexecuted full-domain result will be asserted. The revision will keep the numerical-method program and neural proposals in scope while distinguishing proved guarantees from measured advantage.

This is an exploratory referee-informed revision, not an independently preregistered replication. Record software, exact rational outputs, hashes, all stage costs, checker mutation tests, and any amendment. Publish Econometrica-class main paper, supplement, response, computation manifest, and a lossless historical annex on the new branch.
