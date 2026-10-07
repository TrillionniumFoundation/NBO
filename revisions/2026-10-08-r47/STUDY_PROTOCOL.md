# NBO R47: protocol fixed before new study execution

Date: 8 October 2026. This is a revision of Neural Bellman Operators, not a replacement paper. Reviewed report: reviews/2026-10-08-econometrica-numerical-methods-r46/referee_report.md at 0bf1ff6060bb9211762f191b6ead306ae4725beb. Reviewed article: c3930399e3b8267451096d0e70ea67f49510065e. No prior manuscript, review, result, failure, or application is to be overwritten.

## 1. Direct cost of the actual R46 policies

Use the R46 repetition-zero checkpoints for every economy and every common first crossing of the ORIGINAL targets 1/4, 1/8, 1/16. All three methods must cross; failures stay in the original attainment array. Repeated clocks are not independent policies. Duplicate checkpoints selected by different targets remain explicitly identified.

Compare cone-witness minus cone-nearest, cone-witness minus spline-nearest, and cone-nearest minus spline-nearest. The primary initial-state law is uniform on [0,1]; additional fixed states are 1/8, 1/2 and 7/8. Each comparison group uses 131072 common independent innovation-bin paths, including common initial-state bins for the uniform-state estimand. Each uniform draw is represented by a 40-bit bin and every path calculation encloses all points of that bin. The conditional sampling model is independent uniform bins and independent continuous uniforms inside bins. Fixed pseudorandom seeds provide reproducibility, not proof of independence.

The estimand is expected discounted cost under the original continuous innovation law. Use the existing own-continuation Bellman telescoping score, not a subtraction of regret bounds. Build deterministic score-difference support from the actual signed residual and terminal accounts and the exact extrema of the two initial PWL continuations. Outward arithmetic, rational boundary uncertainty and ambiguous actors must be enclosed, not discarded. An ambiguous selector is enclosed by the hull of all feasible candidate actions, and its cost is recorded. Use simultaneous empirical-Bernstein endpoint bounds with total family error 0.01 across all 120 two-sided policy contrasts (three contrasts, four state laws, ten common crossings). Any actual discrepancy in the catalogue size must stop execution rather than silently change the family error.

The signed superiority threshold is zero. The separate decision tolerance is 1/1024 in the declared normalized cost units: a decision maker willing to forgo this much expected cost can accept a policy whose direct upper cost difference is at most this number. This is an ex ante numerical decision tolerance, not a calibrated welfare margin. Equivalence requires the ENTIRE direct confidence interval to lie in [-1/1024,1/1024]; overlap with zero is not equivalence. No sample-size increase, discarded state or new margin may be chosen after inspecting outcomes.

## 2. Identical-envelope and continuous-frontier controls

Expose the same cone data and action witnesses as a conventional min-plus Bellman implementation. Prove equality of its mathematical continuation, tie rule, actor and certificate with the ReLU encoding. Exercise both ordinary min-plus evaluation and the affine-ReLU min circuit on a fixed grid, retaining any arithmetic discrepancies. Shared compilation cannot be counted twice as independent training, nor interpreted as evidence of neural acceleration.

For the existing full R46 frontier compute the exact lower-envelope function W(epsilon): the cost of the first original rung with bound at most epsilon, including all previous rungs. Report its breakpoints and every nonempty interval of epsilon on which the witness uses fewer Bellman queries than spline, as well as intervals where it does not. This is a descriptive reconstruction of already observed curves, not a new prospective target experiment. Do not select a new favorable tolerance and relabel it an original target.

## 3. Executed constrained two-state construction

State x in [0,1]^2; scalar action 0 <= a <= c(x)=1/8+(x1+x2)/16. Continuous common shock z is uniform on [-1/32,1/32]. Discount is 15/16. Transitions are
F1=1/16+x1/2+x2/8+x1(1-x2)/16+a/2+z,
F2=1/16+x2/2+x1/8+x2(1-x1)/16+a/4-z.
Stage cost is (x1-5/8)^2+(x2-5/8)^2+(x1-x2)^2/4+2(1/2-x1-x2)_+^2+p a^2+4a^4. Terminal cost doubles the first two squared-target terms and retains the imbalance and shortage terms. Horizons are 2 and 3; prices are 1 and 4.

Methods are the feasible cone-witness backend and conventional bilinear fitted-value iteration with a nearest-node feasible repaired actor. Each constructs its OWN future labels on the full tensor grids N=4,8,16. At a node use N+1 equally spaced feasible actions. Integrate the continuous shock using N midpoint bins with a PROVED Lipschitz remainder and outward numerical enclosures; never replace continuous uncertainty by a discrete model. Three fresh isolated process repetitions per method/economy yield 24 services and 72 rungs. Run the full ladder; report prefix work and clocks for targets 4,2,1,1/2 and all failures. These targets are mathematical all-state loss tolerances, not a claim of economically adequate accuracy. Stronger conclusions require their actual bounds and direct comparisons.

Derive primitive state and action moduli, finite nets, invariant-domain bounds, integration error and explicit repair min(a,c(x)). Include cell-corner one-sided selected-policy bounds for the bilinear comparator, so it is not charged only a deliberately weak separated certificate. Report nodes, actions, continuous-law quadrature work, representation evaluations, repair, storage and all failed prefix work. Tensor-grid dependence remains explicit. The conventional comparator is fitted-value iteration, not an unexecuted sparse-grid method.

## 4. Acquired state and finite-precision deployment

For the saved two-state witness policies, test dyadic acquisition with coordinate errors bounded by 2^-12 and 2^-8, plus an exact-input reference. On a fixed 33-by-33 measurement grid, execute ordinary binary64 cone comparisons. Certify the chosen index's excess and the feasible repair over the ENTIRE acquisition box. Compare exact robust repair and downward action quantization at 2^-12. Retain active repair and quantization counts, numerical selection allowances and the resulting additional full-policy bound. Test deliberately ambiguous scalar switchpoints separately. The acquisition-aware guarantee must not silently assume that a policy discontinuity is Lipschitz.

## 5. Execution and preservation

Freeze all scientific source digests before catalogue execution. Development tests may repair implementation errors; disclose amendments, failed executions and whether any outcome was observed. Do not retune the declared models, targets, margins or sample size after results. New clocks are new observations; do not add them to historical construction clocks to manufacture a combined runtime. The paper, full proofs, point-by-point response, complete evidence and reproducible build are to be materialized on a fresh R47 review-ready branch. Passing tests is not peer approval, and the response must distinguish a mathematical repair, an executed comparison and a review claim still not established.
