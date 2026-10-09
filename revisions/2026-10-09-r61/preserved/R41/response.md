# Response to the R39 advisory referee report — R41

Paper: **Neural Bellman Operators**. The title, economic topic, authorship, controlled-economy framework, and full applications companion are retained. This is a revision of the existing paper, not a replacement paper on another topic. The report is an owner-commissioned advisory report, not an Econometrica editorial decision.

## Reviewed sources and revision identity

The report is pinned to `c95c0771c468db7d98ee9746a6bf5972de242569`; its reviewed manuscript is `f472a7c21f2f9db5285f1bf7746edf2d9463638e`. The development parent is `a4ec3525a7184e2d2fe04953d131fbfd725ac941`. The complete R39 publication and R40 failed-run artifacts are retained with their hashes. New material is confined to `revisions/2026-10-07-r41`, apart from root entry points, the repository reading guide, and its dedicated workflow. No historical paper, report, source, or clock is deleted or overwritten.

We thank the referee for distinguishing the validity of the comparison theorem from identification of a specifically neural numerical contribution. We retain NBO as the object of study and address the mathematical and implementation objections directly. We do not treat a negative benchmark as a reason to change the topic, and we do not represent an unestablished performance advantage as a proved result.

## B1 / M1 — The learned continuation itself

**Implemented and proved.** The new main section, “The Trained Continuation as the Certified Bellman Object,” evaluates every stored current network against the Bellman operator containing its own stored future network. The residual endpoints include both current-network and future-network arithmetic, state cover, continuous-action cover, and terminal-network discrepancy. The selected policy is newly constructed from these neural Q intervals and evaluated on its own future shock tree. The global guarantee is against all adapted feasible policies, not just neural policies.

The proof explicitly includes the current network's Lipschitz term, which cannot be omitted merely because the former spline interpolated its nodes. Rational affine-region compilation is an exact evaluation of the network's trained weights, not substitution of a reference spline. Tests execute the direct verifier with the conventional spline evaluator disabled. The networks' original spline-label training history and cost remain disclosed. This closes the distinction between a spline-certified neural proposal and certification of the learned Bellman continuation itself without claiming reference-free training.

## B2 / M2 — Precision actually changes

**Mechanism exercised; efficiency not presumed.** The pressure design has twelve objects and four methods, hence 48 services. Fixed32 passes two objects. Fixed64, adaptive, and tuned precision each pass all twelve. Adaptive execution accepts 116 binary32 and 42 binary64 proposals, with 42 rejected binary32 proposals. Ten adaptive services mix precisions. Every attempted input, output, precision, target, and acceptance is retained; the acceptance gate is inherited unchanged.

The design predates the new complete replay, but some failed R40 outputs had been observed. It is not described as a fresh prospective experiment. One execution per object is sufficient to demonstrate an activated branch and its certificate, not stable adaptive superiority over the best fixed precision. That comparative-work part of the comment remains open to measurement.

## B3 / M3 — The strongest conventional comparator

**Direct comparison added; unfavorable results retained.** At the accepted resolution a new conventional spline policy is independently constructed and evaluated. All sixteen neural-minus-spline cost intervals are contained within a descriptive cardinal margin of plus or minus 0.001. Fourteen nevertheless have strictly positive lower endpoints, none has a strictly negative upper endpoint, and two overlap zero. Thus the reported neural policy is close at these states, not superior. Overlap is never equated with equivalence.

The comparison uses the same final verification resolution; it does not tune both procedures to a separately chosen common global accuracy. Its clocks are not presented as a matched end-to-end work victory. All R39 structural and spline dominance observations remain visible. A competitive method-specific complete-work frontier has not been established by these new services.

## B4 / M4 — Dimension and uncertainty

**General extension and explicit work theorem added; nonlinear scaling experiment still required.** The supplement extends the direct neural certificate to compact multidimensional state and action spaces and continuous innovations with a certified quantizer. A coupling argument charges innovation discretization inside the same residual and actor account. The theorem gives state/action/innovation cover counts, network-forward and risk-evaluation work, streaming storage, output size, attempted-refinement sums, and the separate exponential policy-query tree cost.

This is a genuine mathematical extension, not an empirical claim that a scalar execution scales freely. The current nonlinear execution is still scalar; quadratic dimensions 2 through 32 are not relabeled nonlinear evidence. A coupled multidimensional nonlinear benchmark with a strong sparse, projection, or fitted dynamic-programming baseline remains a substantive experimental requirement. No high-dimensional neural advantage is asserted without that experiment.

## B5 / M5 — Economic gain versus numerical regret

**Sharper direct regret and contemporaneous baseline added.** Every economy now passes a 0.02 target at the four declared initial states. The largest displayed-state bound is below 0.0179. Full-domain bounds are separately reported, approximately 0.0431 to 0.0459. These are not interchangeable. At the eight changed-price state-risk pairs the verified gain over the old rule has lower endpoints above 0.0232. Thus, at the displayed states, the certified neural regret is smaller than the verified gain from reoptimization.

The paper also supplies the neural-versus-new-spline cost intervals requested in B3, so the stale-rule comparison is no longer the only policy contrast. Reoptimization remains available to both methods; no economic result is attributed exclusively to NBO merely because the old rule is deliberately not reoptimized. The 0.001 margin is descriptive, not a preregistered welfare threshold.

## B6 / M6 — Nonzero numerical execution

**Instantiated for the nonlinear program.** The implementation supplies rational range-and-error propagation through the actual separate-operation binary32 graph. It charges state acquisition, transition, stage cost, terminal cost, and clipping; dyadic action values and selection cutpoints are exactly representable. A discontinuous actor is handled by the distance to the selected node, not an assumed actor Lipschitz constant. The resulting additional global allowance is about 0.00001 and is never set to zero.

The main proposition distinguishes the feasible rounded actor in the original economic model from the numerical economy with rounded transitions and accounting. Only the former has a nonnegative gap against the original optimum. The latter has a valid upper excess-cost bound, but need not have a nonnegative difference because its primitives are perturbed. Recursive risk is interval-evaluated with its stated mathematical meaning. Fused arithmetic, flush-to-zero hardware, and physical actuators are outside this tested contract. This instantiation does not retroactively certify every retained quadratic deployment pipeline.

## B7 / M7–M8 — Complete work and stable timing

**Work accounting sharpened; clocks kept descriptive.** All failed meshes and precision attempts are retained. The neural table sums all three attempted meshes through result-file synchronization, rather than reporting only a favorable final mesh. The historical label-construction and training work is explicitly outside these new post-training clocks and remains chargeable in a from-scratch comparison. CPU affinity, one-thread execution, native versions, code hashes, and frequency-control status are recorded. The data do not warrant a timing-distribution or asymptotic-speed claim.

The work theorem displays state/action dimension, innovation support or quantization size, horizon, network evaluation size, risk-evaluation precision costs, and output/working storage. It distinguishes precision-dependent primitive cost and conditioning data from an unjustified universal unit-cost constant. Refinement only reduces verification slack; a fixed inaccurate network retains its intrinsic Bellman residual floor. An additional repeated matched-work scaling experiment is still needed for the full frontier requested by the referee.

## B8 / M9–M10 — One paper and one authoritative chain

**Integrated rather than replaced.** The abstract, introduction, conclusion, and reading guide now lead from the stored learned continuation to its own Bellman residual, actor allowance, terminal discrepancy, own-policy comparison, and execution account. The main article and supplement are materialized self-contained sources. Earlier theoretical statements, complete original applications, historical manuscripts, and adverse empirical results are retained. A label-preservation audit confirms that no inherited active theorem label disappears.

The complete constructive economic instances are the recursive quadratic capital economy and scalar nonlinear investment economy. The continuous-innovation multidimensional extension is identified as a theorem with explicit cost, not as an executed economy. The controlled-diffusion, recursive-utility, endogenous-preference, temporal-self, and game applications retain their own hypotheses and are not certified simply by citing the two numerical instances. The retained breadth is a framework with explicit obligations, not a claim that every application's assumptions have been computationally discharged.

## Source repair and verification

The R40 science attempt failed after reading a JSON policy whose knot and actor arrays remained Python lists. R41 restores both numerical arrays before repricing, adds a regression check for that restoration, and reruns the entire catalogue in a fresh directory. The failed artifact and all earlier clocks are preserved. No partial result is silently promoted to a complete execution.

The publication includes direct neural and risk arithmetic fixtures, exact rational native-execution fixtures, source/record hashes, a deterministic result audit, four compiled active PDFs, complete historical companions, and a release manifest. Compilation and numerical audit are evidence of the deposited revision's internal consistency, not independent referee approval or a proof of a comparative advantage that was not observed.
