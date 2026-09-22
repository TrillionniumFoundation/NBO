# R15 protocol addendum

The primary neural protocol is unchanged: all 40 checkpoints are retained. The order-1/2/4 and fine-cover runs are separate ablations. No successful seed is substituted for the predeclared seed 1500 comparisons.

## Independent arithmetic

The independent MPFR closed-normal calculation exposed interval derivative wrapping near zero time at high adjustment prices. The first fresh-library attempt is retained, including its large valid upper enclosures and interruption receipt. The corrected integration mesh is geometric in sqrt(time), with successive exact rational ratio 11/10 between 2^-14 and 1/64, followed by uniform subdivisions within each policy slab. The complete fresh-price experiment restarts from the model; it does not reuse the interrupted attempt's policies or pilots. Initial nodes are .5 and 8. Subsequent nodes are the exact worst envelope breakpoint rounded to spacing 1/1024; repeated nodes cause a largest-interval midpoint refinement. Stop at a proved gap below .01 or 40 newly generated nodes. Preserve every fitting attempt and all target failures.

## Matched state-space comparison

Both full-horizon classical solvers are evaluated as actual continuous-time interpolated policies, not by treating their discrete values as truth. Use the common initial region [.9,1] x [1.7,2.5] x [1.1,1.5] and verification tube [.9,1] x [1.5,2.7] x [.75,1.9]. A common conservative continuation allowance applies to every method. Any tighter nested-rectangle residual bound is selected only from proved all-control exit inequalities. Preserve all six classical refinement points and the neural and zero-preference-head controls.

## Coupled-state extension

Run a separate quadratic inventory/adjustment economy dX=(AX+a)dt+.1dW, A=-.2 I+.3 M, M=11'/d, running cost X'(I+.5M)X+|a|^2 and terminal cost .5|X|^2, horizon one. Dimensions: 4,8,16,32,64,128. The off-diagonal mean-field coupling is part of the dynamics. Neural gain functions are trained from Riccati residuals, not exact-solution labels: two tanh hidden layers, width 16, seeds 1600--1609, Adam .003, batch 128, checkpoints 1000 and 4000. Enforce the terminal gain exactly. Certify every retained checkpoint on 512 time cells and refine seed 1600 on 2048 cells. Report both total and per-coordinate loss for |x0|^2/d<=1. Compare with the analytic two-mode Riccati solution. This structured application tests genuine high-dimensional dynamics but does not establish an advantage over structure-aware classical solvers or resolve the original model's full-horizon accuracy gate.
