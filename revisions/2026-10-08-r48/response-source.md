# Response to the Referee: Neural Bellman Operators

**Revision:** R48, 8 October 2026.  
**Author:** Qian QI.  
**Report addressed:** R47 advisory report, review commit `3e142dda054f6fd3b9559c0cf2faa658933a2169`.  
**Reviewed source:** `27f3c36984f00ff060d0586712a01b87355914ba`.  
**Scientific protocol:** `ce166e6feb49796bbc60670bcc36201eec07837b`.  
**Ordinary scientific source, frozen before execution:** `53e4eff391bd4b6e035981c7fbb96df1aeff0e54`.

We thank the referee for identifying the distinction between a sharper bound, a less expensive representation, and a better implemented economic policy. We have revised the existing *Neural Bellman Operators* paper. The title, author, controlled-economy subject, previous theoretical results, economic applications, and unfavorable evidence are retained. We address the computational and economic objections by extending the operator's constructive implementation and its decision analysis, rather than changing the subject or interpreting the advisory recommendation as a reason to stop the research.

The principal theoretical addition is an exact continuous-state compiler for the cone-based neural continuation. It preserves the original feasible action witness and the original tie rule. On a tensor cover with S nodes in d dimensions, classical coordinate distance transforms compute nodal values and owners in O(dS) arithmetic operations. A continuous off-grid query then needs at most 2^d corner owners rather than a scan over all S labels. The new obligation is not the classical nodal transform: it is the off-grid identity with the original witness, including inconsistent labels and ties, and its integration into the feasible Bellman-policy and numerical-error account. The two-state representation workload consequently changes from O(TN^6) to O(TN^4). A new corollary allocates construction, numerical, sensing and action precision from a requested implemented-policy loss, and gives a sufficient O(T epsilon^-4) algebraic construction account at fixed primitives and horizon, with precision and physical costs kept explicit. The native implementation can use the same compiler; no neural-exclusive property is attributed to a change of encoding.

A second addition prices the observation technology. The sensor reports a finite-bit state cell, and robust repair guarantees feasibility throughout it. The resulting economic upper account combines construction error, acquisition error, action quantization and a linear information fee. Exact neighboring-bit comparisons identify its minimizing precision. A separate direct comparison evaluates the actual costs of the constrained policies and asks whether either controller replacement recoups a predeclared resource charge. It does not obtain a ranking by subtracting regret bounds.

The full source-frozen execution comprises 36 two-state construction services, eight higher-dimensional stress services, 204 rungs, and 48 direct constrained-policy contrasts. Uniform and error-driven conventional FVI receive their own future labels, the same continuous law, state-dependent capacity, and one-sided all-state criterion. Three isolated repetitions of each main cell record complete prefix work, not independent training draws. Every failed rung and every final failure remain in the evidence. The direct study freezes the original R47 N=16 policies and its sample size, initial laws, information contracts and replacement fee before execution.

@@RESULTS48@@

The responses below distinguish mathematical results, completed executions and conclusions that would require a different experiment. A publication check is not a claim of journal acceptance, and a successful regression is not a substitute for review of a proof.

## Blocking concerns

### B1. The submitted R47 object was not canonical and complete

The R47 publication failure is retained as a historical fact. We do not relabel its failed or cancelled workflows as successful. R48 is assembled from the exact R47 source-bound publication input, with the main and supplement hashes fixed in the build. The main article, technical supplement, response, table generator, ordinary scientific sources, raw records, release audit and PDFs are materialized together in the new revision directory. The root entry points on the new review-ready branch designate R48.

The publication gate installs `poppler-utils`, so the missing `pdfinfo` dependency that stopped R47 is explicitly supplied. It also rebuilds from a clean Git archive after removing generated R48 sources, tables and PDFs. The clean rebuild requires no capsule decoding, expiring artifact download, new simulation, or retiming. Its exact scope, source comparison, regression count and PDF checks are recorded in `audit/CLEAN_REBUILD.json`. The final delivery binds that evidence to the ordinary submitted files. Historical revision and review paths are checked against the pinned review base and are neither overwritten nor deleted.

### B2. The witness backend is not distinctively neural merely because it has a ReLU encoding

We agree with the attribution point and preserve the representation-control proposition. The new section *Witness-preserving compilation of the neural operator* begins with the underlying minimum of Lipschitz cones, defines its original action-index rule, and proves the continuous compiler theorem. It explicitly credits the classical separable distance-transform algorithm of Felzenszwalb and Huttenlocher and explains what that algorithm alone does not establish for a policy: the transformed node's location is not necessarily the location of its original feasible action witness.

The theorem resolves this issue. For an arbitrary continuous query in a tensor cell, a corner owner attains the original envelope minimum, and lexicographic comparison of the original owners recovers the original tie rule. Identical repair therefore gives an identical mathematical policy. Exact rational and interval tests cover arbitrary labels, zero slopes, nonuniform coordinates, dominated sites, off-grid queries and dimensions one through four.

The numerical consequence is a constructive implementation improvement for the cone-based NBO backend, available equally to its identical native implementation. It is not evidence that this representation is unavailable to conventional computation or that all learned neural candidate generators dominate it. The original operator framework and learned-candidate studies remain part of the same paper, with this deterministic backend's contribution stated precisely. At the prospective target two in the horizon-three, price-four cell, its sharper certificate permits stopping at N=32, whereas uniform FVI needs N=64; the complete-prefix medians are approximately 5.498 and 54.146 seconds. This local work-to-target result is separated from the 27 of 30 common successful comparisons in which uniform FVI is earlier.

### B3. The scalar tolerance result was not a signed ranking or calibrated welfare equivalence

All 120 R47 scalar intervals and their interpretations remain unchanged. We add a different decision with an explicit economic primitive, rather than selecting a new scalar equivalence band after inspecting the old intervals. The direct R48 comparison concerns the actual R47 constrained policies, four declared initial laws and three observation contracts. Its replacement fee is fixed at 1/64 of the model's resource unit before execution, equal to one quarter of maximal quadratic investment expenditure at price one.

The new direct-cost theorem separates two conclusions. An interval excluding zero gives a signed expected-cost ranking. An interval strictly inside the fee band implies that replacing either installed controller would not recoup that one-time charge. Neither statement establishes equality, an all-state ranking, a population training effect, or calibrated welfare equivalence. The fee is a primitive of a transparent theoretical economic decision; no empirical calibration is asserted. Every one of the 48 intervals and decisions is reported.

### B4. The constrained comparison was unfavorable on work and lacked actual policy costs

We address both parts with separate measurements. The dense implementation's repeated all-label scan is removed by the exact compiler. This preserves the represented policy when its input labels and witnesses are fixed, so the frozen-object diagnostic directly tests representation cost without changing the candidate. The fresh construction catalogue then measures full own-future services, not just a cheap continuation call. It includes uniform and error-driven FVI, all unsuccessful rungs, policy formation, robust deployment checks and durable output.

The direct experiment is separate again: it freezes both original constrained N=16 policies, preserves their exact mathematical selector definitions, and computes actual discounted path-cost differences on common continuous innovations. The interval simulator encloses every unresolved actor, sensor-cell, repair and quantization branch. Raw path costs, not differences between all-state upper bounds, are the estimand. The joint comparison clock includes loading both policies, compilation, simulation, finite-sample bounds and durable output. The response and tables report the actual timing and sign outcomes without assuming that a smaller certificate implies either one.

The original R47 targets and roughly twenty-one-fold dense-versus-FVI timing comparison remain visible as historical observations. They are not reclassified using the new compiler or finer ladder. Fresh construction arithmetic can also produce different rounded labels from the historical dense program; the exact same-policy assertion applies to fixed input labels, not to byte identity of two independently executed constructions.

### B5. A Bellman-query frontier was not a complete-work frontier

The headline new frontier uses observed complete-prefix wall and CPU times. Each prefix starts from primitives and includes pilot work where applicable, own-future target formation, continuous-law integration, compiled or multilinear evaluation, action selection, certificate construction, every previous failed rung, a finite acquired-state deployment checksum and checkpoint fsync. Process clocks separately include startup and warm-up. The full positive-tolerance partition includes all exact rational bound breakpoints, the unattained region and the final unbounded interval. No favorable target is inserted after inspection and described as prospective.

Component counts remain available but are not converted into a fictitious universal FLOP measure. Exact rational preprocessing has a bit cost: coefficient sizes and peak resident memory are reported. The adaptive pilot and compiled preprocessing are charged rather than hidden. Independent economic comparison remains a joint service with its own clock; it is not implicitly free and is not assigned arbitrarily to one method.

We also reconstruct the R46 scalar partition using its original complete-prefix clocks alongside the previously reported query counts. These historical times are not retimed or added to R48 times from another environment. The supplement and machine-readable records preserve all selected checkpoints, the three repeated times, favorable and unfavorable regions, and one-sided nonattainment.

### B6. The nonlinear implementation remained low-dimensional and tensor-cover dependent

The compiler removes the unnecessary additional state-cover scan, not the underlying state cover. The resource theorem displays S, 2^d, feasible action counts, continuous-integration queries and cell-location work. In the two-state design the leading representation workload falls from O(TN^6) to O(TN^4). This is a constructive operation-account result, not an extrapolation from timings.

The new stress catalogue executes a cycle-coupled nonlinear extension in dimensions three and four, with continuous common uncertainty, endogenous capacity, a continuous scalar action, and two horizons. The primitive extension recovers the original two-state economy at d=2. The supplement proves domain invariance, state and action moduli, capacity transport, terminal regularity and the continuous-law remainder for every executed dimension.

The caps are different across dimensions and explicitly recorded. Each higher-dimensional cell has one observation, so it is a finite implementation stress test, not a repeated matched-accuracy scaling law. We do not claim a sparse or low-rank approximation architecture, unrestricted action-dimensional scalability, or removal of the curse of dimensionality. Those are separate generalizations; the present revision closes the particular repeated-scan bottleneck and supplies actual nonlinear executions beyond two states.

### B7. Acquisition radii were not linked to an economic observation technology

The new section *Priced observation and direct constrained-policy decisions* specifies the technology rather than treating a radius as free. A b-bit-per-coordinate sensor reports a dyadic state cell with its midpoint; the true state belongs to the reported cell. The implemented action is repaired against the lowest feasible capacity throughout that cell and rounded downward to the prescribed action spacing. Thus both the information set and its feasibility consequence are explicit.

The deterministic acquisition theorem yields a precision-dependent upper account of the form G plus a quantization term plus A times 2 to the power minus b plus C times b. Here A is determined by the continuation, action and capacity moduli, and C is the discounted coordinate-bit price. Its discrete increments are monotone. The smallest minimizing integer therefore follows from neighboring inequalities evaluated with exact rational arithmetic. Higher information prices weakly reduce the selected precision, holding the other inputs fixed.

The execution reports all thirteen candidate bit counts at all three prespecified prices for every original witness checkpoint, not just the selected optimum. The direct constrained-policy study separately evaluates exact, six-bit and ten-bit implementations. The selected bit count minimizes the certified augmented account relative to the full-information comparator; it is not claimed to minimize the unobserved actual loss. Coarse construction error remains in G and cannot be repaired by paying for more observation bits.

### B8. Reliability statements were finite-object and deterministic

The revised text separates four objects: the exact compiler and policy theorems; finite-cap target attainment; timing variation of identical deterministic checkpoints; and finite-sample inference on fixed policy costs. The first is conditional on its stated primitives and numerical contracts. The second is the entire declared attainment array. The third uses three isolated repetitions, with CPU affinity and numerical-library threads fixed but CPU frequency uncontrolled. The fourth is conditional on independent uniform bin indices and the exact fixed policies.

The study's pseudorandom stream supports replication, not a proof that deterministic numbers are independent. No initializer distribution is postulated for the new deterministic compiler, and no population optimizer success probability is estimated by counting its timing repetitions. The original nonconvex training results remain their original finite catalogue. This distinction is made in the main theory, experiment and conclusion, not confined to provenance metadata.

### B9. Broader applications have separate analytic obligations

The controlled-economy formulation and the original diffusion, recursive preference, temporal-self and game applications are retained. The active main article states the common monotonicity, cash-invariance, domain and feasible-comparison conditions for the finite-horizon policy account. The compiler is a pointwise representation identity for a specified continuation and actor; it does not discharge utility-domain, equilibrium, transversality or diffusion-approximation conditions by itself.

The direct sampling theorem is expressly conditional-expectation based. It is not substituted for direct comparison under a nonlinear certainty equivalent or an equilibrium operator. A deterministic observation fee can be transported through a cash-invariant recursion when the earlier comparison hypotheses apply, while sampling the resulting recursive utility would need its own estimand. The reading map makes these scope boundaries explicit. Preserving the historical applications is not represented as new empirical validation of all of them by the constrained experiment.

### B10. The economic contribution needed a decision-relevant interpretation

We add two economic choices within the original controlled-investment subject. First, the information technology prices the tradeoff between observation precision and a certified feasible-policy loss account. Second, a predeclared controller replacement charge permits a direct adoption decision from actual expected costs. The two choices use different theorem chains and are not inferred by treating a certificate as observed welfare.

The contribution is a theoretical resource decision with executed constrained policies and complete computational accounts. It is not a newly calibrated quantitative application, and its compiler is not a capability inaccessible to the mathematically identical conventional envelope. Whether these additions meet the journal's substantive contribution standard remains a matter for further review; the revision supplies the missing construction, experiment and decision objects rather than declaring that standard satisfied by tests or by changing the paper's title.

## Major comments

### M1. Produce one canonical, rebuildable submission

The new review-ready branch contains the ordinary assembled main article and supplement, the current response, generated tables, records, code, audits and all three PDFs. The root entry points select this object. The clean-rebuild and final-delivery records describe what was actually verified. The failed and cancelled R47 publication runs remain failed and cancelled. The reader no longer needs to infer the submitted article from a partial workflow artifact.

### M2. Describe the underlying algorithm and attribute neural claims correctly

The new compiler section defines the min-plus envelope and original witness first. It credits the classical nodal distance transform, proves continuous off-grid witness preservation, and gives the numerical and complete resource accounts. Native and ReLU implementations with identical defining data remain the same method. The improvement is an implementation of the constructive NBO backend, not a neural-exclusive theorem or a new classical distance transform.

### M3. Compare the constrained policies directly

All four original N=16 constrained policy pairs are evaluated under four initial laws and three information contracts. Each contrast uses 262,144 common paths under a source-frozen 40-bit-bin design. The simulator encloses the original continuous law, possible actors, sensor cells, capacity repairs and action quantization. The simultaneous confidence account uses bounded raw policy costs and certified endpoint means and variances. Every interval, zero-threshold sign and replacement-fee decision is retained, with no post-result sample extension.

### M4. Supply total-work curves at every breakpoint

The deposited complete frontier uses exact rational certificate thresholds and first-crossing complete-prefix times, with the full component ledger and storage account. The supplement gives every interval, including favorable, unfavorable, tied and unattained cases. The historical scalar frontier is also reconstructed with its actual prefix times. Independent policy-cost comparison is separately timed as a joint service; no clock is manufactured by adding incompatible historical and new observations.

### M5. Add an adaptive conventional comparator

The new error-driven coordinate-FVI method uses own-future pilot second differences to construct nonuniform dyadic coordinate grids. Its fixed rule pays for the pilot and every allocation step. The same continuous innovation law and feasible action fractions are used. The verifier uses the largest actual coordinate gaps and an exact nearest-cell excess calculation for the multilinear continuation; it does not pretend that a nonuniform mesh has the uniform covering radius.

This is a conventional adaptive-coordinate tensor algorithm. Its actual output is also audited: all 210 recorded date models are uniform, and all 60 adaptive checkpoints have the same continuations and actors as uniform FVI. The reported difference therefore measures its pilot/allocation overhead, not successful spatial adaptation. It is neither a sparse grid nor a general locally refined tree. A genuinely nonuniform adaptive performance advantage remains unestablished; the original algorithm and every observation are retained rather than tuned after seeing this outcome. The main text and supplement describe the algorithm precisely enough to distinguish it from more general adaptive baselines that have not been executed.

### M6. Execute dimensions beyond the two-state laboratory

The cycle-coupled three- and four-state economies add eight complete services and 24 rungs, varying horizon at price one. The mathematical constants and invariant box are proved in the supplement. The resource counts display the remaining dimension dependence. Unequal maximum resolutions and singleton stress clocks are visible; the experiment does not claim common-accuracy scaling or a full sweep of action dimension and capacity geometry.

### M7. Price the acquisition technology

The bit-price experiment uses a fixed dyadic observation mechanism with an exact error set, robust action repair, action quantization and a discounted fee per coordinate-bit per date. It computes the entire finite precision frontier and the exact integer choice minimizing the uniform augmented account. The raw policy-cost comparison separately executes two finite-bit technologies, allowing the decision fee and numerical acquisition account to be interpreted without postselecting an attractive radius.

### M8. Interpret the targets as economic decisions

The construction thresholds remain explicit normalized all-state loss tolerances. They are not described as empirical welfare tolerances. The direct comparison adds an independently interpretable adoption threshold: a one-time resource fee of 1/64 that must be recouped by a lower expected operating cost. The theorem derives both replacement directions. The observation study adds an information-price primitive. These provide theoretical economic decisions rather than retrospectively renaming a numerical interval a calibrated welfare result.

### M9. Keep theorem reliability, catalogue attainment and inference separate

The revision uses separate statements and tables for deterministic correctness, finite-cap attainment, repeated clocks and fixed-policy inference. All 69 inherited and 27 new tests are rerun by the publication build. Their role is to check code identities, exact algebra and reconstruction, not estimate optimizer success or certify every historical theorem. New scientific observations remain separate from build verification; rebuilding never reruns or overwrites a timing or policy-sampling catalogue.

### M10. Preserve one coherent paper without changing its subject

We retain *Neural Bellman Operators* and organize the additions around its original policy-specific continuation and implemented-policy objective. Exact compilation, priced acquisition and direct constrained-policy decisions are connected steps of that same operator. The main article identifies the active new evidence and the frozen historical evidence explicitly. The technical supplement contains the full proof and experiment details, while historical theory and application companions remain available without deletion. The response does not replace the manuscript by the differently titled paper suggested in the report.

## Verification and reading instructions

The main article introduces the compiler theorem, the priced precision proposition, the direct decision theorem and the complete study in that order. The supplement provides the line-transform invariant, off-grid tie proof, numerical enclosures, nonuniform FVI certificate, higher-dimensional primitive bounds, observation-account proof, confidence construction, all 48 direct intervals and full time partitions. The published `audit/PRESERVATION.json` maps retained labels and historical companions.

`audit/RESULT_AUDIT.json` reconstructs all 44 services, 204 checkpoints and 48 direct contrasts from their frozen records. `audit/EDITORIAL_NUMBERS.json` reconstructs the reported timing comparisons. `audit/RELEASE_AUDIT.json` binds those results to the 96-test build and compiled PDFs. `audit/CLEAN_REBUILD.json` and `audit/FINAL_DELIVERY.json` establish the submitted object's ordinary-source rebuild and delivery scope. Every unfavorable comparison remains an observation rather than an implementation error to be silently discarded.
