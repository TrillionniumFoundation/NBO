# R119 final numerical and visual QA of the native author manuscript

## Scope and result

The actual 42-page native PDF snapshot passed numerical-table binding and numerical-page visual inspection. Two wording precision items were reported to the parent author; neither changes a recorded scientific result. This is AI author-assistant QA, not human review or an external referee report. No experiments, solver calls or timings were rerun, and no manuscript or scientific raw files were changed.

PDF SHA256: `a7a66d2d6693a759cbbbfc34ff384264d40e953bdc7b21286194f6f6d90dbda1`. The complete source/figure snapshot identities are in `SNAPSHOT119.json`. Rendered pages 31–40 and their contact sheet were inspected; pages 36, 38 and 39 and the standalone figure received individual full-size inspection. The 42-page count applies to this exact snapshot, not a later rebuild.

## Numerical binding to actual raw records

The read-only checker hashed and read **1,232 B/C timing raw files**, recomputed **176 published medians** from all seven actual clocks per cell, checked all **16** acquisition/full-144-service economic-bound rows, and reconstructed all **112** figure points. All checks passed. Printed regret and action bounds in the cost table round outward; timing and component displays match their stated rounding.

The figure spans the actual raw range **0.6391778335840805–1.406012650769053**. Its diamonds are ratios of the separate medians; its grey dots are paired process ratios. Those statistics can differ, as the retained polynomial-2 high-risk cell demonstrates. No population confidence-interval interpretation is used.

| Comparator to fused service | Median wins | Cells with all seven paired wins | Primary 144-service wins |
|---|---:|---:|---:|
| compiled | 16/16 | 9/16 | 16/16 |
| geometric | 10/16 | 2/16 | 11/16 |
| active-tail | 14/16 | 7/16 | 12/16 |
| masked-tail | 16/16 | 12/16 | 16/16 |
| budgeted-tail | 16/16 | 11/16 | 14/16 |

All six fused/geometric median losses remain visible:

| Risk level | Representation | Fused/geometric median ratio | Paired process wins |
|---|---|---:|---:|
| 0.5 | online | 1.0357205 | 1/7 |
| 0.5 | quadratic | 1.0576226 | 1/7 |
| 0.5 | spline | 1.1225594 | 1/7 |
| 0.5 | poly2 | 1.1033988 | 1/7 |
| 0.5 | grid | 1.0338291 | 2/7 |
| 0.75 | poly2 | 1.0184475 | 5/7 |

The complete within-arm service comparisons have exactly zero policy changes. Faster certification does not change the original economic objective in these records. Conventional comparisons also remain explicit: at risk 1/2, quadratic with geometric service has acquisition plus actual load plus actual 144-decision component cost **0.1485192340 s**, against **0.3407350870 s** for ReLU with fused service; at risk 3/4, quadratic with fused service is **0.1417108130 s**, against **0.3131015450 s** for ReLU. The quadratic upper bound on mean original cost lies strictly below the ReLU lower bound in each block: **0.6116062380 < 0.6116236716** and **0.6212681825 < 0.6212857167**. These are actual recorded component totals and deterministic objective intervals, not new enclosing-process timings or population estimates.

## Visual findings

Tables I–III and Figure 1 fit inside the native margins and are legible. No clipping, text overlap, missing glyphs or obscured figure labels were observed on the inspected numerical pages. Figure 1 preserves every adverse raw point, all six red median losses, and all ten blue median wins. The unity line and numeric labels convey the same distinction without requiring color. Its caption explicitly separates actual loading and broader process costs from service clocks and disclaims confidence-interval interpretation.

Table II reports acquisition and actual load plus the actual 144-service component totals. The main text retains A's complete-time negative, B's full-cost weakness, C's remaining six geometric losses, exact ReLU/hinge equality, the conventional quadratic economic and cost advantage, the fixed-catalogue scope, and the conditional adoption inequality. No neural-specific adoption success is inferred.

## Wording precision items reported

1. **Reference independence.** The abstract says “independent original policy references,” and Section 11.3 says the reference “independently partitions” the support. The 1,024-bin reference uses an independent full-support partition with the shared verified terminal compiler. Its actual record explicitly marks both properties. Wording should distinguish this from the separately implemented Fraction primitive/reference suite. Suggested wording: “a separate full-support policy reference using the shared verified terminal compiler.”
2. **Timing table scope.** The Table I and Table III notes say only “Acquisition is reported separately.” Actual model loading and enclosing process costs are also outside these 32-decision service medians and are recorded separately. Suggested note: “Acquisition, actual loading, and enclosing process costs are reported separately.” Figure 1 already provides this scope correctly.

Both items are recorded as reported and pending parent-author disposition in this snapshot. There is no observed numerical or layout defect requiring scientific reexecution.

## Evidence

`NUMERICAL_BINDING119.json` records every checked displayed entry, all 112 ratios, all six adverse cells, conventional comparisons, and the 1,232 raw-file identities. `verify_published_numbers119.py` is its read-only checker. `VISUAL_NUMERICAL_QA119.json` binds this report to source/PDF/figure snapshots and all inspected render hashes. The QA does not itself certify the analytical proofs, unseen population performance, complete high-dimensional service, historical reexecution or remote CI.
