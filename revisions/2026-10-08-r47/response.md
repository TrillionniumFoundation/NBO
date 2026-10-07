# Response to the Referee: Neural Bellman Operators

**Revision:** R47, executed-comparison revision, 8 October 2026.  
**Author:** Qian QI.  
**Report addressed:** the complete R46 report at `0bf1ff6060bb9211762f191b6ead306ae4725beb`, reviewing `c3930399e3b8267451096d0e70ea67f49510065e`.

We thank the referee for distinguishing a sharper policy certificate from the cost and value of the method that produces it. We have revised the existing *Neural Bellman Operators* paper. Its title, economic subject, earlier theorem chain and applications remain; the new work is integrated into its construction, implementation and economic-comparison argument. We have not replaced the paper with a differently titled certification article or removed adverse evidence.

The revision adds an exact witness-preserving tensor compiler, a theorem for acquired-state feasible policies, an explicit primitive precision-and-resource allocation, a complete two- and three-state constrained execution, and direct expected-cost comparisons of both the original witness policies and the new deployed policies. The compiler is supplied equally to the native minimum-plus and ReLU representations. Its classical distance-transform ingredients are credited; shared acceleration is not presented as exclusively neural.

The prospective protocols precede the new executions. The study contains 48 constrained construction services, 144 rungs, thirty direct original-policy contrasts and eight direct constrained-policy contrasts. All raw path endpoints, policy identities, failed targets and timing repetitions are retained. Every confidence interval lies within the prespecified numerical cost margin 0.005 and contains zero. This supports the declared tolerance comparison, not exact equality or a superiority ranking. The two comparison families have separate 95 percent coverage accounts.

The following responses identify completed changes and the precise scope of the evidence. They do not ask that conventional results be discounted because they are unfavorable to neural representation.

## Blocking concerns

### B1. The construction is not specifically neural

The new section *Compiled witnesses and implementable policies* separates the envelope algorithm, its exact circuit realization, and the implementation's work. The same frozen labels, actions and original witness table are queried in flat native minimum-plus form, compiled native form and a ReLU minimum-gate backend with shared outward distance preprocessing. Thus the relevant identical-algorithm comparator is now executed, not merely discussed.

The off-grid compilation proposition proves that the witnesses stored at the enclosing cell's at most 2^d corners contain an original globally attaining cone. Two exact sweeps per coordinate construct the table for arbitrary noisy labels. The result preserves the original action, rather than interpolating actions or assuming Lipschitz-consistent labels. The exact neural circuit and conventional envelope therefore represent the same constructed NBO. The executed compiler improves query work for both representations. Native compiled queries are faster than the ReLU minimum-gate backend in all 24 date-level observations; this is reported prominently. The paper makes no unsupported neural-exclusive speed claim.

### B2. The earlier sharper bound did not improve the target frontier

Every original R46 rung is reconstructed into a complete work-to-bound staircase, retaining historical prefix clocks and query counts. We do not select new favorable thresholds from that staircase. The original identical target crossings remain unchanged.

The new constrained catalogue fixes all targets j/32, j=1,...,32, before execution and executes every rung for both own-future generators. There are 363 common successful target-by-repetition comparisons: fitted-value iteration uses an earlier rung in 54 and the rungs coincide in 309. Witness never uses an earlier rung. Witness is faster in 147 local comparisons. These are correlated descriptive counts, not independent economic trials. The supplement gives every distinct rung, and raw records give all repetitions and failed targets. The work frontier is now observable rather than inferred from an isolated final certificate.

### B3. The new witness policy's actual economic cost was not compared

We now compare all three policy pairs at every common successful first crossing of the original R46 witness experiment. Ten economic-cell/target objects produce thirty contrasts, using the original checkpoint policies, uniform initial capital on the full state interval, and 262,144 common continuous-law bin paths per object. The estimand is the actual discounted-cost difference. No regret-bound subtraction is used.

All thirty simultaneous intervals lie inside the prespecified numerical margin ±0.005; the largest absolute endpoint is approximately 0.0006491. All also contain zero. The paper reports this as a tolerance comparison under the stated initial-state distribution, not a lower-cost policy or exact equality. The fixed margin is explicitly a numerical decision tolerance in an uncalibrated cost normalization, not an estimated welfare threshold. Every original capped failure remains a failure, and repetition-zero policies are not counted as three independent trained policies.

### B4. The new construction was only executed in a scalar economy

The revision executes the witness backend in coupled two- and three-capital economies with continuous common uncertainty, nonlinear cyclic capital transitions, and a capacity interval depending on current aggregate capital. Both horizons two and four and investment-price coefficients one quarter and one are included. A conventional multilinear fitted-value-iteration generator constructs its own continuation and receives a strengthened own-critic, one-sided repaired-actor certificate.

The full design has eight economic cells, two generators, three fresh isolated repetitions and three state/action resolutions: 48 services and 144 rungs. At the finest resolution, the fitted-value certificate is tighter in every economic cell. Direct costs of the new 12-bit deployed policies are compared in all eight cells on 65,536 common bin paths. All eight intervals lie inside the fixed margin and contain zero. These are genuine new multidimensional constrained executions, but not a high-dimensional scaling frontier or an adaptive sparse-grid implementation. Tensor state coverage remains explicit.

### B5. The computational primitives may contain the hard part

For the new benchmark, feasible nets, integration, repair and numerical queries are all constructed from the displayed economic primitives. Feasible node actions use exact integer downward rounding of fractions of local capacity. The continuous-law quadrature remainder follows from an explicit innovation Lipschitz modulus. The terminal quadratic is evaluated directly. Capacity repair is an integer floor of a known affine lower capacity over the acquisition cell. No external value oracle or optimizer success flag supplies these ingredients.

The supplement derives every primitive modulus and a sufficient bound

$$
G\le S_T\{1735/(512N)+(845/256)2^{-b}+(77/32)2^{-a}+2\epsilon_{\rm ar}+\nu\}.
$$

It then allocates resolution and precision from a requested tolerance and displays the remaining state/action/integration factors. This closes the primitive obligations in the executed economic class. The general feasible-witness theorem still requires effective nets and certified repair for other correspondences; we do not claim those tasks are costless in arbitrary economic models.

### B6. Acquisition and numerical selection were theorem-only allowances

The implemented policies now acquire states at 12 and 20 fractional bits. Actions are repaired against the minimum capacity throughout the acquisition cell and rounded down to a 20-bit action lattice. The integer formula proves feasibility at every compatible true state. The selected original witness uses outward score intervals; a uniform score allowance and the observed numerical excess are both checked. The theorem adds state, selection and repair errors to the one-sided all-state bound.

The direct constrained simulations execute 1,042,306 nontrivial action reductions. No unresolved acquisition ambiguity occurs in those sampled paths; adversarial tests separately force boundary ambiguity, ties and endpoint states. Ambiguous paths are conservatively enclosed, never dropped. The ideal exact-state bound is a mathematical reference, not advertised as a physical exact-real computation. The paper does not equate objective accuracy with feasibility.

### B7. Timing and total work were too narrow

All new construction observations use fresh isolated processes with fixed thread counts and CPU affinity. The three repetitions have identical policy/certificate checkpoint hashes and separate clocks. Complete prefix clocks include every previous rung, target generation, continuous-law integration, exact compilation, actor construction, certificate calculation and durable checkpoint output. Process start is separately recorded. CPU frequency is not controlled, and resident-memory measurements include process overhead.

The complete-work statement now separates cover size, feasible action nets, integration, rational closure, circuit or native queries, acquisition, repair, precision, storage and independent policy comparison. Exact integer endpoint moments also have a stated bit-work account. Primitive query counts are not called FLOPs. Same-object compiled native queries are 35.3–68.8 times faster than flat native queries in the local observations; that is a query-engine result, not a complete-service or neural-exclusive speedup. No cross-host clocks are added together.

### B8. The economic application did not provide a substantive method result

The new direct comparisons now identify an economic decision-tolerance statement: under the declared initial-state distributions, the policies' expected-cost differences lie inside a margin fixed before comparison. That is stronger than an unresolved sign without a margin and different from a certificate-width comparison. It can inform an implementation choice when resource use and feasibility matter at the declared numerical tolerance.

The new capacity economy also executes an endogenous feasibility constraint with nonlinear coupled dynamics rather than checking an algebraic example alone. It remains a stylized economic laboratory. This revision does not claim a calibrated policy counterfactual, a neural-only welfare discovery, or empirical indispensability. The positive construction and executed comparison results are developed within the original NBO economic program, while these different substantive criteria remain distinct.

### B9. The broader platform exceeds the new evidence

We retain the original controlled-diffusion, recursive-preference, endogenous-preference, temporal-self and game theory with its own hypotheses. The new sections explicitly distinguish the monotone recursive policy inequalities from the expectation-specific direct-cost inference. No new claim treats a linear paired-score identity as a result for nonlinear certainty equivalents or games.

The title and original subject remain *Neural Bellman Operators*. The introduction now connects the retained theory to a specified constructive backend, exact compilation, robust implementation and direct economic value. Historical companions remain preserved, but the new proofs and all new experimental claims are in the active article and supplement. A benchmark is not presented as evidence that every retained economic application has been executed.

## Major comments

### M1. Isolate the identical non-neural envelope

Completed in the same-object representation experiment and off-grid compilation proposition. All three backends use the same frozen labels/actions. The native and ReLU compiled versions share the same witness table. The paper reports native's faster query clocks and does not attribute the shared compiler to neural representation alone.

### M2. Predeclare direct values and an economic margin

Completed for every original common crossing and every new finest-rung economic cell. The protocol fixes sample counts, uniform initial-state distributions, original continuous innovation laws, all pairs, margin 0.005 and multiplicity before execution. Raw dyadic endpoints are deposited. Exact integer moments and an independent rational-series/squaring audit verify all published empirical-Bernstein endpoints. IID is a stipulated simulation model, not a property proved by the fixed PRNG seed. The two families have separately stated error accounts.

### M3. Report continuous work-to-bound curves or dense targets

Completed: all historical R46 rungs are retained as an exact staircase; all 48 distinct new constrained rungs are tabulated, with every repetition and complete prefix work in the deposited records. The new target grid j/32 is predeclared. We do not present a tighter final bound as an earlier target crossing.

### M4. Execute feasible witness transport

Completed in the state-dependent capacity economies and finite-acquisition deployments. Feasible nets and repairs are generated from the capacity function. Ideal-state, 12-bit and 20-bit error accounts are separately reported; the actual direct costs concern the 12-bit implementation. Nontrivial repairs occur in the executed paths. The conventional constrained fitted-value method receives the same feasible-net and robust-repair machinery. An independently timed exact-real hardware policy is not claimed.

### M5. Include a multidimensional conventional comparator

Completed with two- and three-state coupled nonlinear continuous-uncertainty economies and an own-future multilinear fitted-value-iteration comparator. The conventional certificate is strengthened on the complete half-grid. This is not labeled an adaptive-partition, sparse-grid or approximate-policy-iteration implementation. Those stronger scaling comparisons remain separate from the completed benchmark.

### M6. Report realistic execution errors

Completed through dyadic acquisition, ordinary outward binary64 score calculations, original witness indices, integer robust capacity repair and explicit acquisition/selection/repair additions to the policy certificate. Adversarial tests force ambiguous acquisition and exact ties. Path simulation conservatively encloses all compatible actions instead of using an unverified midpoint actor.

### M7. Give total complexity and representation dependence

Completed in the primitive work statement and technical supplement. Exact closure is linear in the number of grid nodes up to dimension and rational arithmetic cost; off-grid evaluation uses at most 2^d original witnesses. Training queries, integration, selector, repair, precision, stored coefficients/indices, verification and direct-comparison work are accounted for. The compiled native envelope enjoys exactly the same asymptotic improvement. The remaining factor (N+1)^d is visible.

### M8. Separate sufficient termination from finite-cap performance

Completed quantitatively. The primitive cap bound allocates each of five error terms at most one fifth of the requested tolerance divided by S_T. Resolution and acquisition/action/query precision must grow accordingly. The published finite target attainment is reported without substituting this unbounded construction theorem for a capped success. It is not a reliability claim for Adam, L-BFGS or arbitrary initializations.

### M9. Connect the economic claim to the evidence

The active conclusion now distinguishes all-state loss, direct distributional expected-cost tolerance, computational work and calibrated welfare. Only the first three are established in the new construction study. The explicit margin prevents retrospective relabeling of a zero-crossing interval as equality. Neither the observed equivalence-at-tolerance nor the shared compiler establishes neural indispensability.

### M10. Focus the active argument without discarding the original paper

The revised main article follows the existing economic problem and operator through certification, deterministic construction, witness preservation, robust implementation and direct economic comparison. The technical supplement contains the new complete proofs, arithmetic contract, all original-policy intervals and complete constrained frontier. Every R46 main and supplement label is retained, and the preservation audit binds the baseline files. Earlier papers, applications, reviews and adverse records are unchanged. This is a revision of the same paper, not a topic replacement.

## Reproduction and delivery

The new study source is fixed at `0cbc5138373923eb282114532fc5624daeb863ba`; its completed run is `37701989313`, artifact `11517677897`, SHA-256 `9ef9bb39be0cb7291cf467e47e5af5f2e8adf27e4f09ac2b74879d5e6a6759e2`. The scientific tests and entire execution passed. Its final generic evidence-branch write was correctly refused because that branch already contained another execution. We preserved the other branch and deposited these observations on a distinct comparison-evidence branch. Neither run is silently substituted for the other.

Rebuilding the published source audits frozen records and recompiles the paper; it does not resimulate, retrain or rewrite clocks. A separate reproduction must use a new result directory. The publication includes source and evidence identities, preservation checks, raw endpoints, generated tables, all test outputs and compiled documents. Successful tests and compilation are not a mathematical peer-review verdict or an Econometrica editorial decision.
