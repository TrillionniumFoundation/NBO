# R48 study protocol

Date: 8 October 2026. Paper: Neural Bellman Operators, Qian QI.
Review anchor: 3e142dda054f6fd3b9559c0cf2faa658933a2169.
Reviewed source: 27f3c36984f00ff060d0586712a01b87355914ba.
Reviewed assembled-source artifact: 11503019522, SHA-256 65a3c49014b58f1708802496106175631b0bb0cba9b1bfc6f00128e6afbc1bbf.

The revision extends the existing paper. No earlier result, failed workflow, comparison, application, or review is overwritten. The report's recommendation is advisory; it does not dictate a change of subject. This protocol fixes the new empirical objects before their complete execution. Unit tests and implementation development are separate from reportable timing or simulation records. Any necessary pre-execution amendment must be committed and disclosed; completed observations are never overwritten.

## 1. Scientific questions

Can the same witness-preserving NBO continuation and actor be compiled without a scan over all state nodes at every query? Does this remove the extra state-cover factor in the R47 implementation while preserving exact mathematical policy identity, including ties? What are the directly evaluated costs of the R47 constrained policies? How do complete construction-to-certificate costs compare with uniform and error-driven conventional fitted-value iteration? How does an explicitly priced observation technology enter the policy and decision budget?

The compiler uses a classical separable L1 distance transform, credited to the existing literature. The new obligations are the continuous off-grid identity, preservation of the original feasible witness and tie rule, outward numerical evaluation, and the resulting complete Bellman-policy resource account. Compilation is not new training and is not a capability unavailable to the mathematically identical native envelope.

## 2. Construction catalogue

The principal experiment retains exactly the R47 two-state nonlinear continuous-uniform-innovation economy, prices 1 and 4, horizons 2 and 3, and its primitive constants. The common ladder is N=M=4,8,16,32,64. Every rung is reconstructed from primitives. Methods are: compiled cone witness; multilinear tensor fitted-value iteration; and error-driven nonuniform tensor fitted-value iteration. The last is a conventional adaptive-coordinate baseline, not a sparse-grid or locally refined quadtree claim.

There are three isolated process repetitions per method/economic cell: 36 services, 180 rungs. All rungs are executed even after crossing a target. Targets are 4,2,1,1/2,1/4; failed rungs and final failures remain in the ledger. Each method uses its own future continuation, the same feasible action fractions j/N, the original continuous innovation law with its deterministic midpoint remainder, outward arithmetic, and the same one-sided all-state policy criterion. No comparator's values become another generator's labels.

The adaptive-coordinate rule is fixed: for each date, evaluate a fresh four-subdivision pilot grid against that method's own future; use the pilot's coordinatewise second differences as a curvature indicator; repeatedly bisect the interval with largest width-squared times a positive curvature weight until each axis has N intervals. Ties use axis/left-endpoint order. Pilot work, repeated evaluations, knot selection and all certificate costs are charged. The exact indicator and weight formula will be fixed in the source before any complete execution; they will not be selected by observed performance. The largest actual coordinate gap, not an assumed uniform mesh, determines the covering allowance.

The compiler's exact rational preprocessing carries the smallest original witness index on ties. Its checked continuous evaluator examines at most 2^d adjacent-corner certificates per query. A separate frozen-object benchmark compares this evaluator with the original dense evaluator on every distinct R47 constrained checkpoint, including compilation cost and verified point outputs. It is a representation benchmark, not a comparison of independently trained policies.

## 3. Dimension stress catalogue

A cycle-coupled extension retains the R47 economy at d=2. For d=3,4, use x in [0,1]^d, scalar investment a in [0,1/8+sum(x)/(8d)], cyclic neighbor x_(i+1), and
F_i=1/16+x_i/2+x_(i+1)/8+x_i(1-x_(i+1))/16+b_i a+s_i z,
where b_i alternates 1/2 and 1/4, s_i alternates +1 and -1, and z is continuously uniform on [-1/32,1/32]. Stage state cost is (2/d) sum_i (x_i-5/8)^2+(1/(4d))sum_i(x_i-x_(i+1))^2+2(1/2-2 sum_i x_i/d)_+^2; terminal doubles the target-square term. Action cost is p a^2+4a^4.

Fix p=1, T=2,3, methods compiled witness and uniform multilinear FVI, and one execution per cell. The d=3 ladder is 4,8,16; d=4 is 2,4,8. This adds eight services and 24 rungs. Different maximum covers are explicitly memory-limited stress cases, not common-accuracy dimension scaling. All actual dimensions, states, actions, midpoint queries, certificates, clocks and failures are reported. The general theorem continues to expose the exponential cover and 2^d corner factor.

## 4. Direct constrained-policy comparison

Freeze the R47 N=16 witness and bilinear-FVI policies from repetition zero, for all four (T,p) cells. Do not substitute new R48 policies after observing costs. Initial laws are independent uniform coordinates on [0,1]^2 and fixed vectors (1/8,1/8), (1/2,1/2), (7/8,7/8). Observation contracts are exact state, 6 bits per coordinate, and 10 bits per coordinate. The finite-bit sensor reports the containing dyadic cell; a midpoint is the acquired state, and repair uses the lowest capacity on that cell. Finite-bit executed investment is rounded downward to spacing 1/4096. The exact-state policy is unquantized. The action selector and all ambiguous path/observation cells are enclosed, never replaced by unchecked midpoints.

There are 4 economic cells x 4 initial laws x 3 observation contracts = 48 contrasts. Each uses 262144 common paths and 40-bit uniform-bin enclosures for the original continuous innovations (and initial uniform law). Use a fixed source-defined SHA-256/PCG64 stream per group. The statistical assertion is conditional on independent uniform bins; a pseudorandom stream supplies reproducibility, not a proof of independence. The estimand is the actual discounted path-cost difference, not a subtraction of regret bounds. Deterministic primitive-cost support, lower/upper endpoint moments with roundoff allowances, and simultaneous empirical-Bernstein bounds supply a family error at most 0.01. Use a rationally certified upper logarithm of 10 for log(4*48/0.01).

The signed superiority threshold is zero. The separate decision threshold is a once-only controller replacement fee k=1/64 in the model's resource units, equal to one quarter of maximal quadratic investment expenditure at p=1. This is an explicitly chosen theoretical economic charge, not an empirical welfare calibration. A cost interval lying strictly inside [-k,k] can rule out recouping that replacement charge in either direction for the stated task and observation contract; it cannot establish equality or a signed ranking. Report every interval and every decision, including unresolved cases. No sample-size extension follows inspection of results.

## 5. Observation technology and total work

For the witness policies, evaluate b=4,...,16 bits per coordinate and observation prices lambda in {1/16384,1/4096,1/1024} per coordinate-bit per date. The discounted observation charge is lambda*d*b*sum_t beta^t. The deterministic acquisition allowance is calculated from the proved uniform moduli and robust capacity repair, with action spacing 1/4096. Choose b only by minimizing the stated certified augmented cost upper bound. Report the entire fee-versus-guarantee curve, the integer optimum and neighboring-bit inequalities. This is a theoretical observation-technology choice, not an assertion that any numerical radius was measured in data.

Primary work is actual isolated process and CPU time, with an internal prefix clock from primitives through each durable checkpoint and an additional finite acquired-policy deployment checksum per rung. Charge compilation, pilots, query formation, integration, representation evaluation, selector, feasibility/quantization, all failed rungs, certification and serialization. Also record rational coefficient bit lengths, transient/retained storage, peak resident memory and primitive/evaluator counts. Counts are components rather than universal FLOP equivalents. Startup and warm-up are separately recorded; CPU affinity and numerical-library thread counts are fixed, CPU frequency is not.

A direct pair-comparison clock includes loading, both actors, common simulation, statistical construction and durable result output. It is a joint decision-service cost, not silently allocated to one method. Never add clocks from different historical environments to manufacture a new service observation. Reconstruct the entire positive-tolerance first-crossing partition from every recorded bound, with all favorable, unfavorable, tied and unattained intervals. Historical R46 scalar prefix-time curves may be reconstructed separately and remain historical, not retimed.

## 6. Validation and publication

Freeze scientific source hashes before the complete run. Check exact off-grid values and original witness indices against dense rational enumeration, including ties, dominated labels, zero slopes, unequal coordinate grids and dimensions 1--4. Check interval enclosures, continuous-law remainders, adaptive covering/nearest-cell bounds, feasibility, sensor thresholds, confidence reconstruction and ledger hashes. Retain and rerun the 69 inherited regressions without rewriting historical observations.

Publication must materialize ordinary assembled manuscript sources, technical supplement, response, generated tables, raw records, code, audits and PDFs on a NEW review-ready branch. Use the retained Econometric Society template without modifying its class. A clean rebuild must work without expiring artifact downloads; historical input restoration is a publication-stage action only. Verify no historical paths were deleted or modified, no undefined references/labels or overfull text remain, and final source/PDF/record hashes agree. Do not call an incomplete workflow or a planned branch a completed submission.
