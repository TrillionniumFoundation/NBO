# R88 prospective shared-proposal protocol

## Source and scope

This revision answers the R84 report at b030d87d7e96440eb25a3178c94ee6a87940cdb0, retaining the title Neural Bellman Operators and the full economic program. The manuscript baseline is R86 as retained by ba0c71dda605a66ed8c07f4f20342202d13a553f. Earlier revisions and reviews remain unchanged. Reconstructing the fixed R85 streams is replication of inherited evidence, not a new R88 independent sample.

## New experiment, fixed before execution

Use the original scalar investment economy and corrected protected Bellman oracle in the retained R67 kernel66.py. All contexts have two remaining dates, continuous innovations under the original law, states uniform on [0,1]^d, and the original feasible investment cap. Acquisition states are actual continuous states, not fitted-state projections. Numerical action rounding and protected fallback are identical across arms.

Fit once on 128 states in dimension 2 and 128 states in dimension 8, using PCG64 seed 202610128801. Targets are the protected adaptive oracle's feasible actions at tolerance 1/256, divided by the current cap. No optimal-value labels are supplied. The common 14-dimensional input contains eight zero-padded state coordinates, the mean, even-coordinate mean, odd-coordinate mean, mean square, mean adjacent-coordinate product, and d/8. No dimension-4 training state is included.

There are two fitted proposals: one shared single-hidden-layer ReLU network of width 32 (MLPRegressor, lbfgs, alpha 1e-5, max_iter 1000, tol 1e-8, random_state 88), and a complete degree-two polynomial with ridge coefficient 1e-6 on the same features. No architecture, seed, or hyperparameter is selected after evaluation. All warnings and failed fitting attempts are retained. A nonfinite fit is an invalid predictor, not an omitted arm. Freeze complete coefficients, training inputs, labels, and hashes before creating either calibration or evaluation states.

Compare five services: protected adaptive subdivision, protected bisection, an analytic one-date proposal, the shared ReLU proposal, and the shared polynomial proposal. All return the same tolerance 1/64 certificate or an explicit failure. Learned and analytic proposals are untrusted probes, never sources of validity. This is a scalar-query transfer experiment, not a replacement for the separately retained full-policy cost or two-control evidence.

Calibration uses 64 fresh states in each of dimensions 2 and 8, PCG64 seed 202610128802. Select the service minimizing mean (Bellman action queries + terminal queries), with ties in the listed arm order. This declared two-component operation price is not a monetary calibration. Save the selected arm and all calibration records before generating evaluation data.

Evaluation uses 128 fresh states in each of dimensions 2, 4, and 8, PCG64 seed 202610128803. Execute every arm on the identical workload. Report selector regret against the ex post mean-work winner separately from any expected-cost guarantee. Preserve every query, including warnings, invalid proposals, feasibility repairs, first-screen closures, subsequent protected refinements, exact fallbacks, and zero-progress probes. Report model multiplication/addition/ReLU counts separately from oracle work, and source-bound payload bytes and process peak memory separately from additive operations.

All service timing includes interpreter startup, model/input loading, numerical execution, serialization, and shutdown, with three fresh-process repetitions per arm and dimension. Execution order cycles across repetitions. Retain component work next to complete process time and all repetitions. A second machine may replay the identical frozen models and inputs without refitting; it adds timing evidence, not independent statistical observations. Energy and monetary prices are not measured and must not be invented.

## Inference and evidence boundaries

The comparison is paired on the complete fixed workload. Report distributions and paired mean differences in deterministic work, not an unsupported universal neural superiority claim. Original-law policy costs are addressed by the separate nine-controller R85 protocol (139264 inherited independent rows, 144 simultaneously allocated comparisons), which is replayed with both interval kernels. Query certificate success, predictor reliability, complete-controller cost, and wall-clock performance are different estimands.

The new mathematical work extends the full-policy transfer through common-parameter policy patterns and explicitly accounts for cross-date accuracy dependence in stored-continuation computation. Finite exact examples validate implementations, not theorems by sampling. Final publication requires current ordinary LaTeX sources, nonempty bibliographies, clean compilation, actual rendered-page inspection, exact input/output hashes, and an explicitly scoped clean reconstruction. A failed or unperformed gate remains visible.
