# R30 protocol — frozen before the new numerical runs

Baseline: review/econometrica-r29-second-pass-numerical-methods-2026-09-24, commit 3175974aed89dac1595af174a201dcae7bcfae31; manuscript reviewed at 788246778893695471015ce4db76e6a61a2c9ca0. The first and second R29 referee reports and all earlier manuscripts remain unchanged.

This is a new exploratory, report-informed study, not a preregistered independent confirmation of earlier outcomes. Changes to this protocol must be appended and dated; no unsuccessful configuration may be silently replaced.

## Questions
1. Can a whole-region certificate avoid state enumeration when the known model and a compiled proposal admit exact regional bounds?
2. Can policy preservation be valued using discounted occupancy and explicit implementation costs, rather than unweighted edit counts?
3. Can the original stopped diffusion be evaluated with validated derivatives when boundary exit has material probability?

## Structured economic study
Eight-period binary operating-mode choice. State x in [0,1], action-independent reset distribution with density 2x, survival 9/10, discount 19/20, zero settlement. Action zero pays x/5; action one adds one of three fixed rational gains: x-3/8; 16(x-1/5)(x-1/2)(x-4/5); 2(x-33/100)^2-1/25. This is a separate economic family, not a discretization of the original diffusion. Use exact Bernstein bounds, rational compiled-policy intervals, and tolerance 1/100 uniformly over all states and restart dates. Report the continuous-state cover and finite-grid counts for m=8,12,20,40 (2^m midpoint states); never treat state count as state dimension.

Neural proposals: one-hidden-layer ReLU networks, widths 8 and 16, seeds 30001 through 30005, both Adam (200 steps, rate .02) and L-BFGS (maximum 200 iterations, strong-Wolfe search). Train only against 512 fixed midpoint reward-difference observations, not against an optimal-policy/value file. Serialize and hash every candidate before certification and benchmark construction. Include polynomial least-squares, constant-action, and exact structural/classical comparators; report unsuccessful raw proposals, compilation costs, full training and certification times, bound evaluations, policy bytes and rational bit lengths. No best-seed selection. Structure-aware and vectorized dynamic programming receive the same model information. Do not infer neural specificity from generic certification.

Economic metrics: discounted changes under density 2x; state-priority cost 1+x; exact raw-to-completed reward gains; lower/upper bounds on the minimum revision cost in the explicitly stated locally admissible class; comparisons with near-exact structural optimization; break-even shadow costs, rather than an assumed money value for CPU seconds. The implementation uses conservative interval refinement near indifference surfaces and records any extra edits due to unresolved tolerance boundaries.

## Original-economy stopping study
Retain every primitive in Section 2 of R29. Use initial preference 1.22 (rather than 2), wealth 5/4, c=3/4, p=0, k=2, and constant theta in {-1/5,-1/10,0,1/10,1/5}. Evaluate stopped payoffs, exit probabilities and first two theta derivatives by a killed-Brownian kernel/Dynkin representation with directed ball arithmetic and explicit time-truncation and opposite-boundary remainders. Include the inherited central restart as a comparator where useful. Log failed enclosures; do not replace a failed enclosure by a decimal quadrature value. This does not by itself certify the 47-dimensional actor or the original all-domain .01 target.

## Integrity and validation
All original R29 source and historical evidence are retained. The paper must distinguish proof, executed numerical evidence, inherited evidence, and unresolved requirements. New theorem checks include zero-tolerance backward completion, negative/malformed certificate tests, all-state coverage, exact network compilation, weighted-cost bounds, and endpoint/tie handling. Preserve the original target and its numerical ledger; do not describe the outstanding full-domain certificate as completed without an actual validated computation.
