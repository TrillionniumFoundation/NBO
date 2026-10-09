# Response to the Referee: Neural Bellman Operators

**Author:** Qian QI. **Revision:** R51, 8 October 2026.

We thank the referee for distinguishing a reproducible input export from a submitted paper, and for making actual policy cost the decisive numerical endpoint. This revision addresses the threshold report on R50 and the controlling substantive report on R49. It revises the original *Neural Bellman Operators* paper: neither its title nor its economic primitives are replaced, and earlier theoretical developments and adverse findings remain available in full.

The R50 threshold report is pinned at `2822f50100c7a53ec5fe07d39e9b37d487ab0547`. The controlling R49 report is pinned at `4708450610c38e6b8963670cecadc887508c85c0`, and the R49 manuscript at `4ede6077aa3d78aa36ec9b9471e5338a636a49f4`.

## 1. Principal changes

The revision makes a constructive change to the policy-improvement argument. Signed evaluation bands now control a centered comparison with the implemented incumbent. A proposed action is adopted only if a feasible, whole-acquisition-cell upper advantage is nonpositive; otherwise the original action is retained exactly. The expected gain is expressed under the implemented new policy's occupancy law. Thus the conclusion concerns actual policy cost, not a comparison of unrelated certificate widths.

R51 adds a finite-sweep accuracy theorem. With certified action error alpha, centered enclosure width zeta, and own-policy evaluation width w, the new policy satisfies

$$
 E_t^{k+1}\leq\beta_t E_{t+1}^k+
 \alpha_t^k+\zeta_t^k+2\beta_tw_{t+1}^k.
$$

The full unrolling yields a near-optimality budget for the original Bellman problem after T passes. With exact comparisons, greedy proposals and policy evaluation up to a datewise constant, the policy is optimal after at most T passes, and every intermediate policy is nonworsening. A common feasible-menu proposition quantifies acquisition and action errors. A two-action construction proves that the coefficient two on w is sharp for the stated gate. All three arguments are proved, and five additional exact-rational tests check their formulas and boundary cases.

The numerical specialization integrates the original investment economy's final innovation analytically and uses an outward, cellwise improvement test. Both witness and conventional FVI receive the same rule. The source-bound study executes resource planning, a genuinely residual-driven conventional comparator, common-target dimensional services, and direct expected-cost comparisons. These are final-date improvement experiments; they do not claim to execute the full T-pass theorem.

## 2. Response to the R50 threshold requirements

### 4.1. One canonical paper object

The designated review branch is `revision/econometrica-nbo-r51-review-ready-2026-10-08`. It is published only after the ordinary sources, raw evidence, generated tables, all five compiled documents, tests and clean-archive build have passed their recorded gates. The integrated-source branch has the same final delivery head. The science-freeze branch remains a distinct immutable input identity.

The root navigation is changed only on the new branches and points to R51. The main article, supplement and response are ordinary UTF-8 sources rather than an encoded transport or an expiring artifact. The complete development article and supplement retain the broader historical exposition. The exact delivered identity is in the final-delivery record and the remote Git head; a workflow-success flag is not used in its place.

### 4.2. Substantive response and change map

This response treats B1–B10 and M1–M10 below. The new sections are `improvement50.tex`, `proofs50.tex`, `frontier50.tex`, the current `study51.tex`, `finite_sweeps51.tex`, and `finite_sweeps_proofs51.tex`. The R50 sections and source modules are recovered from the previously unpushed local package and identified as such; the finite-sweep results and integrated publication are new to R51. The generated R49-to-R51 manuscript differences and label-preservation audit identify changes without deleting earlier claims or assumptions.

### 4.3. Numerical-method evidence

The package includes separate construction, policy and verification records. The primary catalogue contains 17 specifications with three isolated repetitions each; the common-accuracy block contains two methods in three dimensions with three repetitions each. Failed primary allocations remain failures, and every common-target refinement is charged. The direct family has 28 groups and 280 estimands. Old and improved policies are both evaluated. The supplied cost-resource ledger, rather than a certificate-only attainment table, is the joint performance account.

### 4.4. Publication integrity

The historical R48 publication, R49 main and R49 graded archives are permanent repository files with verified digests. Source modules, original protocol statements, corrected and uncorrected direct evaluations, reference data, generated tables, PDF audits and the independent clean-archive rebuild are retained. The final-delivery record binds these objects to the candidate Git commit. It does not assert an official editorial decision or turn a successful build into scientific acceptance.

## 3. Response to the substantive comments

### B1 and M1. Canonical and self-contained submission

We agree that R49's split source and evidence objects and R50's input-only export were not complete submissions. R51 integrates them in one additive manuscript directory. The current paper can be rebuilt offline. The original review branches, failed delivery records and adverse observations are not rewritten. The new publication procedure checks a Git-archive copy rather than relying only on the active working directory.

### B2 and M2. What is and is not neural-specific

The native original-owner distance transform is stated as the algorithm. The affine–ReLU representation computes the same continuation, owner and feasible action; it is not entered as an independent empirical competitor. This identification is kept explicit in the construction and improvement sections. The paper remains about Neural Bellman Operators, including the relation between policy evaluation, representation, acquisition and feasible improvement. We do not attribute the common min-plus compilation saving uniquely to a neural architecture.

The positive additional result is the accuracy-to-improvement account: a neural continuation accompanied by the stated signed evaluation and action-search bounds participates in a safe policy update and the finite-sweep error recursion. Merely fitting a neural critic does not certify those bounds. The theorem's hypotheses apply equally to another representation that supplies them.

### B3–B4 and M3–M4. Actual cost, certificate attainment and removable loss

The R49 sign pattern is preserved exactly: 93 higher witness costs, no lower witness costs and three unresolved comparisons. We do not replace these economic comparisons with the tighter witness certificates. The new endpoint is the expected cost of the implemented acquired policy.

The same terminal improvement is applied to both generators. Direct records separately report each incumbent's gain and the remaining difference after both improvements. The identity

$$
 J_W-J_F=(J_W-J_{W^+})+(J_{W^+}-J_{F^+})-(J_F-J_{F^+})
$$

separates removable terminal-action loss from the residual cross-method difference. Date-level action and terminal-state summaries, capacity and quantum repair counts, accepted and blocked proposals, and evaluation work accompany the contrast. This decomposition does not pretend to identify every earlier-date approximation mechanism.

The finite-sweep theorem supplies a further positive mathematical response: it gives sufficient error budgets for approaching the original optimum without an intervening increase in cost. It is not invoked as evidence that the current one-date numerical specialization has already achieved that optimum. The sharpness example explains why an economically beneficial action can still be rejected by a conservative, correctly implemented gate.

### B5–B6 and M5. Conventional adaptive comparison

The original curvature-FVI block remains explicitly nonadaptive in its realized geometry: its 72 substantive checkpoints matched uniform FVI. The genuinely graded amendment remains a distinct adverse result. Neither block is used as evidence against adaptive methods in general.

The recovered R50 design adds a residual/surplus-driven coordinate method that queries its own future objective, chooses knots through an economically relevant interpolation criterion, and records the actual nonuniform partition. Pilot work, surplus queries, allocation, compilation and output are priced in its service record. Uniform FVI remains the strong baseline. This executes a genuine adaptive mechanism; it is not a substitute for a comprehensive comparison with every sparse-grid or local-residual method.

### B7 and M6. A common accuracy target in every reported dimension

The first block retains the planned-allocation failures. The separate common-accuracy rule begins from the planner and doubles the state resolution only after the method's own certificate fails, preserving every attempted checkpoint. Both methods face the same target five in dimensions two, three and four. Returned policies receive direct cost comparisons, and peak memory and full prefix work are recorded.

The common-target block repairs the mismatch in the earlier dimensional comparison. It does not remove the tensor factor `(N+1)^d` or the corner factor `2^d`. Those factors remain visible in both the theory and accounting. The finite-sweep theorem controls policy accuracy conditional on its error budgets; it is not a claim of dimension-free construction complexity.

### B8 and M7–M8. Executed allocation and complete resource boundaries

The primitive allocation searches the declared finite dyadic menu before construction and minimizes the exact integer Bellman-query proxy subject to its sufficient error budget. Isotropic controls and the actual-modulus FVI results are retained. A witness-sufficient plan is not mislabeled as a certificate for conventional FVI.

The query proxy is separated from complete execution work. Records include planning, all own-future construction, compiled transforms, actor queries, corner/interpolation work, terminal derivative evaluations, whole-cell gate tests, interval widths, serialized bytes and process peak memory. The common-target service also includes failed attempts. Joint policy-evaluation time is an explicitly charged shared operation; it is not silently set to zero or attributed only to one generator. Primitive counters are not called a complete hardware-independent bit-operation count.

### B9 and M9. Information technology and conservative choice

The information fee now has an explicit theoretical technology: b bits for each of d coordinates require tau times db resource units per observation. At resource price w and setup cost K_b, the present fee is

$$
 C_b=K_b+w\tau db\sum_{t<T}B_t.
$$

This gives the normalized bit-price sensitivity an economic unit and interpretation. It is not an empirical calibration: the original economy contains no measurements that identify a particular sensor's w or tau.

The simultaneous net-cost theorem bounds the chosen policy's loss relative to the unknown true best policy in the declared finite catalogue. Its upper-minus-lower envelope explicitly prices conservatism. A replacement decision uses a paired cost upper bound plus implementation and replacement charges. It does not substitute the lowest sample mean for the true expected-net-cost optimum. All earlier sensor comparisons remain available.

### B10 and M10. Editorial focus without changing the paper

The active article now follows the model, original-owner construction, signed policy evaluation, safe improvement, finite-sweep accuracy, resource allocation and actual economic decisions. Detailed proofs, all direct intervals and accounting are in the supplement. The complete development volumes preserve the broader original theory and applications under their original assumptions. Moving a reading priority is not deletion, and historical applications are not silently claimed to have received the new low-dimensional numerical validation.

## 4. Provenance of the recovered study and the new execution

The complete local R50 ZIP was recovered from the author's file library, not inferred from the input workflow. Its digest is `fa1fe9690a389a6289bba728d6814b8cc7ee68942a6fc67539c1e9d3de53f4b6`; all 964 delivered-file hashes passed verification. Its source modules, design and earlier local-freeze declarations are retained. The archived declarations describe that earlier local execution, not a prospective R51 experiment.

R51's numerical execution is explicitly a known-design reproduction after those outcomes were available. The new Git source identity and runner environment are recorded before this execution. The common-accuracy rule and the outward-subtraction replay retain their separate identities. Reproducing the same streams or correcting arithmetic on them supplies no additional independent observations. New runner times are not pooled with historical times.

The direct inference has a finite simultaneous family and the conditional independent-bin model stated in the supplement. Fixed pseudorandom streams establish computational reproducibility, not mathematical independence by themselves. The all-state policy-improvement theorem is a separate deterministic statement on its verified hypotheses.

## 5. Verification and remaining empirical questions

The release executes the inherited R49 and graded tests, the recovered R50 constructive and publication tests, and five new exact-rational finite-sweep tests. It independently reconstructs the historical referee findings, audits current checkpoint identities and intervals, regenerates the tables, and compiles five documents with unresolved-reference, duplicate-label, overflow and missing-glyph gates. The actual counts and outcomes, rather than planned success assertions, are in the release and clean-archive records.

The substantive response is a positive extension of the original method: certified incumbent improvement, a sharp finite-sweep accuracy account, an executed original-economy specialization and joint cost-resource evidence. Unique neural efficiency, calibrated device prices, broad high-dimensional competitiveness and a full multi-pass economic implementation are not inferred from these results. They remain empirical questions to be evaluated on their own evidence, not reasons to relabel adverse observations or change the subject of the paper.
