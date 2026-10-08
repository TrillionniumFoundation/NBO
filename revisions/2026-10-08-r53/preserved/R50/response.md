# Response to the Referee: Neural Bellman Operators

**Revision:** R50 completed manuscript, 8 October 2026.  
**Author:** Qian QI.  
**Latest screening report:** `review/econometrica-numerical-methods-r50-threshold-2026-10-08-25295d6`, review commit `2822f50100c7a53ec5fe07d39e9b37d487ab0547`.  
**Controlling substantive report:** R49, review commit `4708450610c38e6b8963670cecadc887508c85c0`.  
**Manuscript baseline:** R49 source commit `4ede6077aa3d78aa36ec9b9471e5338a636a49f4`.

We thank the referee for making the distinction between a policy's certificate, its construction cost and its actual economic performance decisive. We revise the existing *Neural Bellman Operators* paper. Its title, author, controlled-economy subject, policy-specific continuation program, original theory and economic applications are retained. The active article and supplement preserve every R49 label. Complete development editions preserve the R48 exposition and add the current argument; the historical sources and all adverse experimental blocks remain available without alteration.

The central addition is a cost-directed, incumbent-preserving improvement theorem. Signed reference-policy evaluation bands control the error in a centered action advantage. A proposal is accepted only when its true advantage is certified nonpositive after observation and numerical allowances; otherwise the actual incumbent action is retained. The theorem gives all-state nonincrease under the stipulated monotone conditional recursion and an explicit discounted gain under expectation. The executed specialization uses exact final-period integration in the original nonlinear investment economies. Both witness and FVI receive the same improvement. The conventional policy generally remains less costly, but the new rule now produces strictly positive identified actual-cost reductions for the witness incumbents instead of substituting a tighter certificate for an improvement.

The computational addition is a locally pre-frozen resource planner, a residual-driven conventional comparator, full actual-cost evaluation and a separate common-accuracy completion. The primary catalogue contains 51 services. A later, separately frozen amendment contains 18 services, explicitly charging unsuccessful attempts before a state refinement. The cost study contains 28 comparison groups, four policies and ten estimands per group. Every group has 131,072 interval paths with analytic final-innovation integration. There are 280 reported actual-cost estimands, not 280 independent economic experiments.

A publication review found that cross-policy subtraction required one further directed rounding step. The same frozen policies and random streams were replayed with the correction. Original sources, raw results and clocks are retained; active tables use the corrected records, and the numerical replay adds no sample size. The correction is documented separately rather than changing the frozen primary source or concealing a failed check.

## Latest R50 threshold report

### Submitted object and authoritative entry point

The threshold report correctly observed that the pinned R50 branch only exported inputs and did not contain a new manuscript. That export workflow is not a scientific revision. The present package supplies ordinary `ECTA.tex`, `supp.tex`, `response.md`, bibliography, section sources, all generated tables, scientific sources, complete frozen evidence, build instructions, and compiled main/supplement/response PDFs. The complete development editions and historical theory/application sources are also present.

The latest review and original R49 manuscript identities are recorded in the release audit. The R49 main study and its separate graded study are both included as permanent offline archives with the original artifact digests. Their clocks are never pooled. The publication rebuild extracts them locally, reconstructs the old results and tables, verifies the new records, and compiles the active sources without network access or new training.

### Offline reproducibility versus remote publication

The local revision is an actual manuscript and executable replication package, not a plan or a request that a future workflow assemble a paper. A clean local Git-archive build tests the submitted ordinary sources after generated products are removed. The attached apply script restricts changes to the new revision directory and the root entry points, preserves the review base, creates a new branch without force-pushing, builds before committing, and pushes only that branch.

There is a distinct administrative limitation: this turn's connected GitHub interface exposed reads but no write operations, and container access could not resolve the GitHub host. No remote write, branch creation or commit is claimed. The proposed branch name is an apply-script target, not evidence of an existing remote branch. Consequently the local materialization and reproducibility objections are addressed by delivered files; remote publication remains unperformed. This limitation is not used to replace the substantive revision with infrastructure work.

## Controlling R49 blocking concerns

### B1. Incomplete canonical manuscript and disconnected evidence

The active article, proof supplement, point-by-point response and both historical R49 evidence blocks are assembled in one directory. Ordinary sources and a deterministic build replace reliance on an input-export workflow or encoded manuscript transport. The main text includes generated results, the graded block's adverse outcome and the direct-cost evidence. The current root entry-point files in the delivery package select R50; the originals are saved before an apply operation. The publication audit separates local build completion from the unperformed remote push.

### B2. Native min-plus and ReLU encode the same method

The revised abstract, introduction and construction section explicitly describe one native witness method with an equivalent affine–ReLU realization. Original labels, owner identities and tie rules are common. The classical nodal transform and Lipschitz-extension antecedents remain credited. Native and neural encodings are not counted as two competing empirical methods, and no compiler result is presented as an exclusive neural capability.

The additional improvement theorem changes the implemented decision rather than relabeling its encoding. It joins the original NBO policy-evaluation program to a certified action-advantage test under acquired states. The principle of monotone policy improvement has precedents, including safe approximate policy iteration; these are cited. The contribution claimed here is the explicit signed evaluation, centered numerical and cell-feasibility account, not priority for Bellman's improvement principle or universal neural superiority.

### B3. Actual witness cost is often higher

All 96 original R49 first-crossing intervals remain in the active supplement: 93 certify higher witness cost and three are unresolved. The old favorable work pair's unresolved direct comparisons also remain. No old controller is replaced in those records.

The new experiment keeps earlier actions fixed and changes a final action only after a whole-cell actual-cost check. Its own-policy contrast is computed directly from the centered final conditional cost. Every declared witness comparison group has a strictly positive identified reduction under its specified initial law. All-state weak improvement comes from the theorem; strict improvement under a particular law comes from its direct interval. These are not interchangeable assertions. The conventional comparator generally remains less costly after both methods are improved, and that residual ordering is reported.

### B4. Certificate/work improvement does not imply economic policy improvement

The primary ordinate in the new comparison is actual expected discounted implemented-policy cost. The paper reports four absolute costs and six direct contrasts per group, alongside construction, verification and evaluation charges. The incumbent's original loss certificate is not subtracted from another certificate to manufacture a gain.

A new finite-catalogue proposition places a joint cost/resource upper-minus-lower envelope around the selected policy's true net-cost regret. A separate direct paired gate assesses replacement against an incumbent, including any specified installation or runtime charge. This permits a cheaper certificate, a cheaper construction and a cheaper policy to disagree without giving contradictory economic conclusions.

### B5. The original curvature comparator was uniform

The active text states the realized zero-nonuniformity result, including all recorded date models. It no longer claims that a method name establishes adaptation. A new residual-driven FVI comparator uses actual own-future midpoint interpolation surpluses, deterministic insertion and square-root-surplus equidistribution, with dyadic monotonicity checks. Its realized nonuniform grids, pilot work and direct costs are deposited.

The initial bisection-only development test also remained uniform at its power-of-two quota. That failed development check is preserved; equidistribution was specified before the measured primary catalogue. The new comparator is a genuine additional coordinate-adaptive implementation, not proof that every competitive adaptive or sparse-grid algorithm has been represented.

### B6. The genuinely graded comparator was adverse

The separate graded block is materialized with its own source and result manifest. It is not silently merged with the main block's clocks or advertised as a successful adaptive design. Its twelve matched final certificates and clocks remain adverse relative to uniform FVI; its tight-target failures remain failures. The new surplus rule uses a different, explicitly recorded objective and receives no favorable relabeling of that old evidence.

Uniform FVI remains the strong baseline throughout. The new residual comparator is evaluated on actual policy cost as well as certificate, geometry and all pilot charges. Its outcome is not extrapolated into a conclusion about the entire adaptive approximation literature.

### B7. Tensor dependence and low-dimensional evidence

The compiler still incurs tensor storage and a dimension-dependent corner factor. Both factors remain explicit. The new common-accuracy block uses the same target five in dimensions two, three and four, with both methods, three fresh repetitions, first-success stopping and every failed refinement charged. Each returned pair receives direct actual-cost evaluation before and after the common safety gate.

This closes the missing connection between a dimension-specific construction observation and an actual common-target policy comparison in the executed cells. It is not an asymptotic scaling result, and dimensions beyond four are not claimed. The theoretical finite-dimensional construction and the executed small-dimensional study remain separate statements.

### B8. The allocation theorem had not been executed

The primary service now minimizes the exact integer Bellman-query proxy over a fixed dyadic menu using the primitive coefficients, before construction. An isotropic service is executed on the declared comparison cell rather than assigned an unexecuted runtime. All actual certificates, failures, complete service clocks, operation categories and storage are recorded.

The primitive formula is witness-sufficient, not automatically FVI-sufficient. The primary experiment preserves FVI failures rather than claiming otherwise. The separately frozen common-accuracy rule uses each method's actual certificate to decide a further state refinement and charges all attempts. Neither finite rule is described as globally optimal for true runtime, memory, arbitrary-precision arithmetic or the unknown actual policy loss. The distinctions between a proxy optimum, a verified policy account and measured full work are now operational.

### B9. Information prices and conservative net choice

An explicit theoretical technology maps transmitted coordinate-bits into resource units through a conversion factor and prices those units, with an optional setup charge. The old normalized bit prices are a special case, not a calibration. The old sensor intervals, their 101 unresolved and three higher-cost nonidentity comparisons, and the exact identity rows remain visible.

The upper-net-cost selector's upper-minus-lower regret compares it with the unknown true best policy in the observed finite catalogue. A sample-mean or midpoint winner is not called the true ex post optimum. The sensor experiment does not contain device data that could identify a real information-production technology. The revision provides an explicit economic interpretation and sensitivity frontier while retaining that empirical distinction.

### B10. Broad economic program versus demonstrated numerical content

The paper remains *Neural Bellman Operators*: policy-specific continuation, feasible improvement, transport, acquired-state implementation and economic resource transfer remain its subject. The original controlled-diffusion, recursive-utility, endogenous-preference, temporal-self and game results and their hypotheses remain in the complete development edition and preserved application sources.

The active article is self-contained for the current finite-horizon construction, reference-policy improvement and expected-cost inference. The monotone-recursion comparison is stated separately from the expectation-only occupancy and sampling results. No new equilibrium, transversality or recursive-domain assumption is supplied merely by a numerical experiment. The added investment study is theoretical and controlled, not a calibrated macroeconomic exercise. This organization preserves the original subject while making the additional positive results and their empirical reach precise.

## R49 major comments

### M1. Deliver one canonical review package

The package has one active article, supplement and response, ordinary scientific sources, both R49 evidence blocks, corrected new records, complete editions and a single offline build command. The clean-archive test removes generated products and rebuilds from these files. The delivery manifest does not confuse a successful local archive rebuild with the unavailable remote push.

### M2. Put the native algorithm first and clarify neural realization

The construction is the original-owner min-plus envelope. The exact affine–ReLU identities are a representation theorem for it. The compiler, direct policy and tie rules are shared, and the related-work discussion credits the corresponding classical ideas. A newly proved cost-directed acceptance rule changes the policy only through its verified advantage; it does not create an artificial native-versus-neural performance comparison.

### M3. Make actual cost a primary reported outcome

Every new group reports original and repaired actual expected costs, all direct pair contrasts and the economic gain available for a replacement fee. The joint resource table places these intervals next to fresh service and evaluation clocks. Neither lower certificate widths nor a successful stopping indicator substitute for those costs. Every original unfavorable comparison remains.

### M4. Diagnose why a tighter certificate can give a worse policy

The new mechanism experiment leaves the original continuation, owner rule and all earlier actions fixed, then repairs only the final decision using exact integration. The decomposition of witness-minus-FVI cost into each incumbent's removable final loss and the remaining repaired-policy gap is an exact identity. Date-level action means, final state means, proposal acceptance and blocking, capacity/quantum repairs and gate bounds accompany it.

This identifies a concrete removable decision loss in the original controllers. It does not assert that the residual is uniquely caused by a neural representation or that the effect of every earlier owner and state transition has been separately identified. Such a stronger attribution would need additional interventions.

### M5. Execute a meaningful adaptive conventional baseline

The residual-driven comparator has genuinely nonuniform recorded geometry and forms all pilots against its own future. It shares the primitive economy, action menus, innovation integration and one-sided certificate with uniform FVI. The pilot and partition costs are counted. The old uniform curvature heuristic and the adverse graded heuristic are preserved as separate experiments, not renamed to claim that this request had already been met. The new experiment covers one declared adaptive cell and is not represented as a broad sparse-grid benchmark.

### M6. Common-accuracy dimensions and actual policy values

The separate common-accuracy service executes dimensions two through four at the same target, retaining its repeated first-success checkpoint identities and complete prefix work. Both returned methods are compared under the same uniform initial law and acquired-state contract. The paper reports their actual costs, repaired costs and remaining difference. It does not substitute a looser target as dimension grows or extrapolate a dimension-free claim.

### M7. Execute the resource rule and compare isotropic allocation

The primary fixed-menu optimizer is executed before each service. The isotropic alternatives are real service records, with their own attained or failed certificates, rather than arithmetic work estimates treated as timings. The common-accuracy amendment additionally distinguishes a proxy-proposed allocation from each method's certificate-based completion. All additional attempts and failures are charged within their own run. The amendment's chronology after the primary outcomes is explicit.

### M8. Extend work accounting beyond Bellman calls

The ledger includes planning, primitive target generation, transform relaxations, corner/interpolation operations, retained coefficients and original owners, actor quantities, terminal derivative and comparison calls, cell-gate counts, exact fallbacks, ambiguity events, serialized bytes and peak memory. Clocks cover the declared service boundary through durable output; direct paired inference is a separate joint charge. Uncounted bit operations are not zero, and the counters are not described as full FLOPs.

The raw common-service map adds the descriptor named maximum_coefficient_bits as part of a generic prefix map. Publication does not interpret that sum as a maximum: it reconstructs the actual maximum over attempts and distinguishes additive counts from peak/live descriptors. The reporting correction is disclosed without rewriting the executed record.

### M9. Explain the information-production technology and conservative choice

The bit technology specifies coordinate-bit transmission, a resource conversion factor, a unit price and an optional setup charge. The finite-catalogue envelope then bounds actual net-cost regret for all nonnegative prices on one simultaneous event. The observational data do not identify a calibrated device technology or an exact true ex post optimum; midpoint choices remain descriptive. The same logic gives an economically interpretable break-even installation charge for the terminal safety gate.

### M10. Maintain a coherent paper without discarding its program

The active argument runs from economic primitives through own-future construction, feasible acquired policy, reference-policy improvement and actual net-cost choice. The original title and topic remain. Complete editions retain the prior theory, proofs, applications and all unfavorable numerical results; no result is removed to make the current comparison look stronger. The response distinguishes an executed final-stage improvement from the general conditional theorem and from claims that remain unsupported, including universal neural superiority and high-dimensional competitiveness.

## Validation and interpretation

Exact-arithmetic tests cover terminal integration, convex discrete action minimization, feasibility, whole-cell safety, reference-advantage widths, finite-state policy telescoping, resource enumeration, realized adaptation, simultaneous inference arithmetic, directed endpoint subtraction and price-envelope regret. Frozen-record audits reconstruct every new policy-bound formula, original-owner transform, repeated checkpoint identity and corrected confidence interval. The original R49 referee audit is rerun against both materialized evidence blocks. Build tests and finite examples support reproducibility and catch implementation errors; they are not mathematical peer approval or an editorial decision.

The positive additional conclusion is an explicitly verified actual-cost improvement route for the same NBO policies and economy, accompanied by complete charged numerical evidence. The remaining comparative cost ordering is reported rather than erased. The local delivery provides the material needed for another substantive referee reading; a remote publication is not asserted where it has not occurred.
