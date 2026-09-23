# R19 scientific protocol

Parent review: 074849b9aad1812b59e25e1d3833383ed11aa401. Reviewed manuscript: 49d286a174a7d3f71293adc920284584673f390b. This protocol is committed before execution of the R19 studies below. It is not a retrospective preregistration of R17/R18.

The title Neural Bellman Operators, the original stopped nonlinear economy, its action set, and its full-domain 0.01 accuracy objective are unchanged. A result on a selected initial-state set is never reported as a full-domain certificate. Historical R18 scientific content and evidence are preserved. No successful run or closed scientific gate is asserted by this protocol.

## A. Policy-value-separated neural updates

At k=2 train a new two-hidden-layer width-16 tanh neural time-control generator on the original CRRA expectation; no stored optimal policy, value, dual witness, or supervised control labels enter training. The network maps the 16 slab midpoints to consumption and preference controls. Consumption is budget normalized with a 1e-7 present-value reserve; its raw shape amplitude is 0.006. Preference adjustment is 0.1+0.1*tanh(output). The portfolio is zero. This is a neural-generated, finite-time-control subclass of the unchanged economy, not the full-state R17 architecture.

Seeds 19100--19104; Adam learning rate 0.003; checkpoints 0, 50, 200, 800; full-batch 16-point time / 40-point Gaussian proposal quadrature; CPU float64, one thread. Save every proposed network and its compiled dyadic policy, including failures. Re-evaluate each proposal by the existing independent rational-Gauss/Cauchy/stopping evaluator under MPFR-directed arithmetic. An actor replaces the incumbent only if its payoff LOWER endpoint exceeds the incumbent payoff UPPER endpoint. A lower endpoint increase alone is not accepted as proof of policy improvement. Report both true-improvement margins and optimality bounds separately.

The existing certified dual envelope is used only after actor generation to evaluate regret at (t,u,x)=(0,2,1.25). Report final values at the four corners of [1.98,2.02] x [1.24,1.26] with the historical budget-preserving wealth transfer. These are state-specific checks, not a new claim of a continuum theorem without its required concavity/stopping allowances. Generate fresh SLSQP time-control comparators at 16, 32 and 64 slabs, with the same independent payoff evaluation and the same certified upper comparator. Separate generation, compilation, verification, shared-upper generation/verification cost, and process peak memory. Conventional MC/SL historical evidence remains intact; a time-control comparator is not mislabeled as a PDE solver.

## B. Continuation-trace intervention and attribution

Expand the R17 actor/critic 2x2 interchange to all ten accessible seeds, and report upper-face trace excess, fixed-witness lower floor and signed residual components at all 30 accessible checkpoints. This is explicitly an audit of historical frozen runs, not new training.

For a separate intervention, take final accessible networks for seeds 17100--17104. Freeze their actors and all critic parameters except the last additive bias. Lift that bias by a directed monotone search until the certified trace excess at (0,2,2) is at least the explicit feasible-policy continuation lower bound Delta. Recompute the entire 1024-box certificate, with every box retained. Record any increase as well as decrease of the complete bound. The point-trace condition removes the particular necessary fixed-witness obstruction only; it does not imply a good global witness or an improved actor. Derive a general two-witness policy-improvement criterion and a constructive trace-aware acceptance rule, keeping this distinction explicit.

## C. Learned warm-start contribution at matched tolerance

Use the already stored R17 d=8,32,128 neural initializers, all three seeds, without retraining. Declare a new finite query distribution before evaluation: 32 independent uniform-cube queries per dimension, RNG seed 19200+d. Evaluate target losses 1e-2, 1e-3, 1e-4 and 1e-6. Compare neural-start gradient descent, zero-start gradient descent and zero-start accelerated gradient. Stop at a directed gradient certificate below the target, not at a common arbitrary iteration count; cap at 64 corrections, retaining failures. Count gradient evaluations including final checking and report online inference/correction time separately from certificate time. Report break-even query counts only when the measured mean online saving is strictly positive, and include the historical neural training cost. A finite-query result is not a cube-uniform guarantee; provide a separate learned-gradient-dependent theorem with explicit covering and Lipschitz hypotheses.

## D. Publication and validation

Retain every input and old manuscript; add new ECTA_R19, SUPP_R19, RESPONSE_R19 sources and PDFs using the existing unmodified econsocart class. Include all referee F1--F11 and T1--T10 in the response, with precise evidence scopes and remaining gates. Run interval arithmetic tests, acceptance-rule tests, source-preservation checks, three-pass LaTeX builds, unresolved-reference/overfull checks, and visual inspection. Pin input, protocol, source and publication commits separately. Arithmetic independence is not claimed as independent mathematics or a formal proof.
