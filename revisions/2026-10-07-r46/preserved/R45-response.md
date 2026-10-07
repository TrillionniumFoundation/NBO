# Response to the Referee: Neural Bellman Operators

**Revision:** R45, 7 October 2026.  
**Report addressed:** the R44 advisory report at review commit `5d4eca82b5477c4f0305f0f90bf9adc1635ec5de`.  
**Reviewed article:** `e00d3d46484029738884119f18ce1e15fbdcc929`.  
**Paper and author:** *Neural Bellman Operators*, Qian QI.

We thank the referee for distinguishing the validity of a certificate from the value of the procedure that constructs the policy. We have revised the same paper rather than replacing its economic subject or removing adverse comparisons. The controlled-economy formulation, title, author, prior results, economic applications, and all earlier evidence remain available without alteration. The current main article retains every R44 LaTeX label and adds a constructive theorem and a complete matched execution.

The central addition is a deterministic own-future ReLU backend. A minimum of Lipschitz cones represents each continuation exactly, with a primitive Lipschitz bound that is independent of numerical label error. The theorem produces the continuation, a feasible actor, signed Bellman residuals, and an all-adapted-policy loss budget. Its corollary chooses state, action, and numerical tolerances from the requested economic accuracy. This is a construction theorem, not an assumption that an optimizer eventually returns a sufficiently accurate network. It extends the earlier scalar constructive argument without claiming that classical Lipschitz extension, ReLU minimum gates, or spline representation are new.

The second addition is a predeclared full-catalogue execution. Two horizons, two investment prices, two generators and three isolated repetitions produce 24 services and 144 recorded rungs. Every method executes the same fixed ladder, forms its own future labels, and uses analytic integration under the original continuous uniform innovation law. Exact rational compilation and outward arithmetic are shared by the neural and spline implementations. The original capped R42 services and the later R44 selected recertifications remain separate evidence objects.

The new execution is informative but does not establish neural superiority. At targets 0.5 and 0.25 both methods certify all twelve services. At 0.125 the neural backend certifies nine and the spline twelve. The three neural failures repeat the same horizon-four, price-four economy; its final upper bound, approximately 0.12503, is not rounded into attainment. All 33 common successful method/target/repetition clock comparisons favor the spline in these local observations. The paper reports these results directly. The theorem supplies deterministic termination with its sufficient resource allocation; a finite predeclared ladder can fail to contain that allocation. Neither assertion is substituted for the other.

The table below is a reading map, not a declaration that every substantive concern has been eliminated. Mathematical progress, completed executions, and comparative requirements not established by them are distinguished in each response.

## Blocking concerns

### B1. A method-neutral certificate does not isolate the value of NBO

We agree that the policy theorem alone does not construct a neural continuation. The new main section, *A constructive neural service with a primitive error budget*, proves a separate construction result. For prescribed primitive moduli, state and action covers, and numerical query accuracy, it constructs an exact affine–ReLU circuit and a nearest-node feasible actor. The residual, actor and terminal allowances imply an explicit all-state policy-loss bound. The Lipschitz constant does not grow with label error divided by mesh spacing.

The associated supplement proves all components, including the exact scalar acceleration used in the execution. Classical Lipschitz extension is credited to McShane; the earlier scalar spline–ReLU construction is discussed explicitly. The increment is the arbitrary finite-dimensional, noise-stable own-future construction and its full policy/resource account, not a claim that the elementary architecture is newly invented or uniquely available to neural computation. A conventional implementation can use related Lipschitz regularization. Comparative neural advantage therefore remains an empirical or additional theoretical question; it is not asserted as a consequence of this theorem.

### B2. Postselected recertification does not improve original reliability

The seven R44 recertifications remain postselected diagnostics of frozen objects. None is reclassified as an original capped-service success. The new study is a different, completely specified generator and service. Its protocol was committed before catalogue execution, and every declared neural and spline service runs the full common ladder. All failed rungs and all final failures are retained. The study source is checked against its frozen digest before execution.

The new 24-service catalogue is not a fresh random sample of the R42 optimizers. Its method-level mathematical estimand is deterministic termination of the stated constructive backend under the stated primitive and effective-computability conditions. The finite implementation result is reported separately from that theorem.

### B3. Verification-only improvement is large and lacks a common frontier

Tables in the main article and supplement now give the entire common constructive frontier: 48 distinct method/economy/resolution rows, each repeated three times. Each rung starts from primitives rather than borrowing a previously trained candidate. Prefix counts and clocks include every earlier failed rung, target generation, exact compilation, actor formation, certificate calculation and durable checkpoint output. All defining labels, compiled rational knots, actions, numerical errors and exact gap formulas are deposited.

The neural and spline generators receive the same continuous-law integration acceleration. There is no dense-loop baseline imposed merely to favor the neural method. Additional records report deployed actor scalars, compiled rational storage, numerator/denominator bit lengths, checkpoint bytes and process peak resident memory. Primitive-object counts are explicitly not described as complete floating-point or bit-operation counts. The earlier verification-only work counts remain unchanged; they are not added to clocks from another host to manufacture an end-to-end observation.

### B4. The twenty-four direct policy-cost intervals are unresolved

All twenty-four R44 neural-minus-ridge intervals remain reported as containing zero. We introduce no retrospectively chosen equivalence or noninferiority margin. The new constructive targets are all-state policy-loss tolerances; they are not direct comparative-cost margins. No new direct policy-cost simulation has been executed in the constructive catalogue, and its missing cost is not reported as zero or included in the internal service clock.

Thus this revision does not claim to identify the sign of the coupled policy-cost contrast or to establish all-state equivalence. A prospectively economically justified comparison margin and state-design study would be additional evidence, not a reinterpretation of existing intervals.

### B5. Conventional methods remain compelling

We retain the scalar spline's tighter certificates and identified favorable cost signs, the coupled ridge's strong original attainment and timing results, and the unresolved direct coupled intervals. The new matched execution also favors the spline on the recorded common-target clocks and gives it complete attainment at the tightest target. These observations are visible in the main text rather than confined to an audit file.

The positive result established here is a defined neural construction with a primitive-to-policy guarantee. We do not equate that result with uniform numerical superiority, economic necessity, or dominance of conventional approximation. No adverse comparator is removed to make the contribution appear stronger.

### B6. There is no complete matched work-to-accuracy comparison

The new catalogue supplies fresh isolated processes and complete prefix clocks on one runner, with three repetitions of each method/economic cell. The input starts from the declared economic primitives; all failed resolutions, fitting by exact compilation, feasible policy construction, verification and durable checkpoints are charged. The full frontier is executed even after a target has been crossed so that the complete schedule remains observable.

The measurement boundary is now explicit. Process startup and the identical non-economic warm-up are excluded from the internal clock but included in separate process clocks. CPU affinity and numerical-library thread counts are fixed; CPU frequency is not controlled. Peak resident memory includes the interpreter and warm-up. Independent policy-cost comparison is not executed. These observations therefore establish a local matched construction-to-certificate comparison, not universal hardware-normalized work superiority or a complete cost including an unperformed economic comparison. The original nonlinear services have not been retimed or replaced.

### B7. Nonlinear evidence is low-dimensional and tensor-cover dependent

The new theorem is valid in arbitrary finite state dimension under its stated common-action and primitive-modulus conditions. Its operation and storage accounts display the state, action, innovation and precision factors. Tensor coverage remains exponential in dimension. The exact scalar compiler is clearly identified as a one-dimensional acceleration.

The fresh execution varies horizon and price in a scalar nonlinear continuous-innovation investment economy. It is not a genuinely high-dimensional benchmark. No adaptive sparse-grid, adaptive partition, fitted-value or approximate-policy-iteration dimension frontier is claimed to have been executed. The mathematical extension is substantive, but it is not presented as empirical evidence that neural approximation removes the coverage burden.

### B8. Nonlinear optimizer reliability is undefined

A deterministic termination corollary now replaces the need to assume successful optimization for the new backend. Its conditions are explicit: effective state/action covers, invariant dynamics, primitive Lipschitz moduli, a common monotone cash-invariant evaluation domain, and certified numerical queries at the requested accuracy. The prescribed resource allocation yields a policy-loss bound at most the requested tolerance.

The theorem does not apply retroactively to Adam, L-BFGS or unrestricted nonconvex training. The original fixed-seed catalogue remains a finite-array result, not an estimated initialization success probability. The new three repetitions have identical policy and certificate hashes; they measure timing dispersion rather than optimizer randomness. Arbitrarily fine tolerance can require arbitrary precision; fixed binary64 and a finite ladder are not promised to achieve every tolerance.

### B9. Adaptive precision remains an adverse empirical result

The retained precision record is unchanged: fixed64 and adaptive each certify all 36 services, adaptive rejects 126 binary32 proposals, and its aggregate recorded time is about 0.98 percent greater. The main article continues to describe the mechanism's activation without claiming a work saving. The conditional numerical-acceptance theory and its economic role are preserved, but this revision adds no evidence of a mixed-precision efficiency advantage.

The new constructive experiment uses outward binary64 evaluation with exact rational coefficients and explicitly checked query-error allowances. It is not a mixed-precision performance experiment and is not used to repair the adverse precision comparison by substitution.

### B10. Economic scope exceeds completed comparative evidence

We preserve the controlled diffusion, recursive utility, endogenous preference, temporal-self and game developments and their conditions. The new construction closes an additional primitive-to-policy route for a well-defined compact nonlinear class. The investment laboratory has continuous uncertainty, nonlinear capital dynamics, convex nonlinear adjustment cost and a downside capital penalty, but it is not a calibrated empirical application.

No new claim is made that reoptimization after a price change is uniquely accessible to neural computation or unavailable to a strong spline/ridge method. A substantive calibrated application or a broadly competitive multidimensional benchmark is not supplied by these experiments. The paper's economic program is retained, while the level of completed comparative evidence is stated accurately.

## Major comments

### M1. Choose one central paper

We retain *Neural Bellman Operators* as the original subject. The abstract and introduction now connect policy-specific continuation, centered economic error, an explicit neural construction, all-state certification, and direct expected-cost comparisons. The new construction is an additional theorem about that operator, not a replacement topic. The paper does not claim that method-neutral verification makes neural generation universally preferable.

### M2. Prespecify the entire training-and-verification service

The original protocol, pre-execution primitive-domain amendment, frozen source hashes, fixed schedule and all 24 executed services are included. The state/action ladder, horizons, prices, methods, targets and number of repetitions were fixed before execution. A corrected transition intercept is disclosed: the preliminary 1/16 violated invariance at the upper corner; the final 1/32 gives exact extrema 0 and 1. No catalogue result was used to tune this correction. Earlier development checks are excluded from empirical clocks.

### M3. Define a method-level reliability estimand

The new estimand is deterministic termination under explicit primitive and computability conditions. The finite-cap attainment array is an implementation result. It does not estimate a population optimizer success probability. The response to B8 and the termination corollary state this distinction formally.

### M4. Compare complete verification frontiers

The supplement lists every distinct frontier row; the underlying 144 checkpoints retain all repetitions. The main article reports first crossings and prefix work. Exact rational gap reconstruction, source hashes, checkpoint hashes, actor feasibility, query counts and cross-repetition object identity are audited. Storage and memory are in the machine-readable records and summarized with the paper's work account.

### M5. Use an economic margin for the direct comparison

We have not invented a margin after viewing the R44 intervals. Existing direct contrasts remain unresolved, and the new study does not make an equivalence claim. The new all-state targets concern loss to the optimum and have a different estimand. This request is not closed by relabeling certificate tolerances as comparative margins.

### M6. Execute a genuinely multidimensional nonlinear benchmark

The new theorem is dimension-explicit and the new execution is explicitly scalar. The requested high-dimensional comparative execution is not included. We preserve the existing coupled economy and the broader program rather than substituting a disguised low-rank example or an unexecuted protocol for the requested result.

### M7. Use repeated isolated complete-work measurements

Three sequential fresh-process repetitions, a fixed CPU affinity, single numerical-library threads, a common warm-up, prefix clocks through durable checkpoint output, process clocks and memory records are supplied. The full original training experiments are not rerun. Frequency is not fixed, and primitive-object counts are not full FLOP counts. The results are therefore local reproducible measurements with explicit limitations, not a stable universal speed claim.

### M8. Separate expectation-specific and recursive conclusions

The paired telescoping score remains restricted to conditional expectation. The new constructive policy theorem uses the stipulated monotone cash-invariant recursion and requires a numerical evaluator for that same functional. Neither theorem gives a direct policy-cost comparison for nonlinear recursive utility or games without the additional application-specific argument. These scope boundaries appear in the abstract, theorem conditions, algorithm description and supplement.

### M9. Make the active submission self-contained

The new main article and technical supplement contain the definitions and complete proofs needed for the active centered, full-policy, retained-policy, direct-expectation and constructive results. They use one notation system. The complete R41 source tree and compiled economic companions are materialized byte-for-byte within the current revision, not merely left on another branch. The full R44 article and supplement are also preserved as source copies. A preservation audit verifies all copied identities and retention of all R44 labels.

The historical companions are identified as preserved theory and applications under their original conditions, not alternative descriptions of the new experiment. Further editorial consolidation of every historical development is distinct from deleting that material. The current article controls all current empirical claims.

### M10. Develop a substantive economic application

The investment laboratory now has an explicit primitive error budget and a fully executed resource-to-policy account across horizons and prices. It demonstrates construction in a nonlinear controlled economy rather than fitting pre-solved optimal labels. It is nevertheless a numerical laboratory, not a new calibrated economic finding unavailable to conventional methods. The retained economic applications have not been declared empirically validated by this new scalar study.

## Reproducibility and remaining scientific assessment

The release contains the revised article, proof supplement, this response, materialized preserved theory and applications, source-frozen study code, full results, generated tables and machine-readable audits. The inherited fourteen R44 tests were rerun; the thirteen new exact-arithmetic regressions test the envelope, noisy labels, dimensions one through three, actor bounds, terminal/numerical budgets, rational knot boundaries and continuous-law integration. Every new checkpoint's gap and hash is independently reconstructed. These checks are evidence of internal consistency, not formal proof checking or editorial endorsement.

The first remote study attempt rejected corrupted transport bytes before running any experiment. The transport was repaired to the already fixed SHA-256; no scientific source was altered. A pre-execution cell-index regression failure and its correction are likewise retained. Completed observations are never overwritten to hide development failures.

The revision advances the original paper by replacing an assumed successful neural fit, for one explicit backend, with a primitive-budget construction theorem and by executing a full matched catalogue. It does not establish neural superiority, resolve the existing direct coupled ranking, deliver a high-dimensional nonlinear frontier, or add a calibrated empirical application. We submit the new theorem, proofs, complete execution and preserved economic program for renewed substantive review rather than treating successful compilation as acceptance.
