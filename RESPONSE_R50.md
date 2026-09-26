# Response to the R48 referee report — R50

We thank the referee for distinguishing valid certificates from successful numerical optimization, and for identifying the missing publication inputs. R50 responds by adding mathematical and executable content rather than changing the common-policy target. The principal additions are complete price-portfolio loss bounds with exact occupation upper witnesses, a shared-regret-budget cover and its explicit repair modulus, paired Borel-policy approximation for density kernels, and an executed diffuse-law moment formulation. All original substantive theory is retained in the current argument; the complete R48 text is additionally preserved in the historical supplement.

The new study was source-frozen before primary evaluation. It has 39 diffuse models, two proposal backends, all intermediate grid certificates, and a cross-language exact reader. A separate retrospective study retains every result from two finite constructors at two declared caps. We do not equate within-project source freezing or cross-language replay with externally authored scientific replication. Several requests for a calibrated application, a difficult learned operating oracle, an external verified global comparator, and broad controlled-model scaling remain unfulfilled as experiments; the responses below state this explicitly rather than fabricate outcomes. The paper keeps its original research object and proves additional scope where the hypotheses permit it.

Reviewed report: 73a4f708581834692b817649ba5538b640b9e58d. Reviewed manuscript: 77b90a92250694271265e91f9624b7d6aacb0dea. The inherited R49 branch is preserved; R50 is a new branch. Freeze: 62585130b01f1b3479b5fc9f8ee0ee927509633a. The final exact evidence and complete build status are indexed in R50_REVIEW.md.

## R48-F01 — Complete immutable review object

The revision adds ordinary root entry points for the article, numerical supplement, referee response, and reconstructed historical article, together with a root review index and a one-command verification/build script. Missing historical numerical tables are regenerated from the original exact records. The publication manifest hashes sources, models, results, proofs, PDFs, and logs. The original review and prior revisions are not overwritten.

**Location:** R50_REVIEW.md; R50_BUILD.sh; MANIFEST.json; paper/archive_r48

Implemented; the build and replay outcomes are reported in the final manifest, not assumed from the presence of a script.

## R48-F02 — Method-relative target success

The revised article no longer counts tighter failed intervals as new target hits. It reports all twelve original rows, both new finite constructors at both caps, and a distinct new diffuse cohort. The latter gives positive-cost paired continuum certificates rather than a price-only attachment to inherited policies. The price and budget constructors are not declared uniform winners.

**Location:** paper/evidence.tex; results/finite-*.json; generated/finite_compare.tex

The original price method still has no extra R48 primary closures; the new evidence is explicitly separated.

## R48-F03 — Medium and large positive-cost closures

A new source-frozen study includes horizons 4, 8, 16, and 32, up to five actions and thousands of continuum policy rows; both endpoints are verified for the original diffuse-law target. Its largest LP has 24,608 variables. The paper states that uniform-reset structure, not arbitrary controlled-dynamics scalability, makes this construction effective.

**Location:** paper/reset.tex; paper/evidence.tex; models/; results/*-highs-*.json

Substantive structured continuum closures are supplied. Broad medium/large controlled finite scalability is not established.

## R48-F04 — Large unfinished intervals

All unfinished intervals remain in the main finite table and supplement. A new uncapped occupation audit distinguishes incomplete price optimization from the gap between the price relaxation and the common-policy problem. Six historical failed rows have price-family optima bracketed below 1e-8, while two retain visibly loose price upper witnesses.

**Location:** paper/pricecompletion.tex; proofs/price-audit-*.json.gz; results/diagnostics.json

The diagnostic resolves an identifiable source of uncertainty without relabeling the original policy problems as closed.

## R48-F05 — Price cost versus benefit

The article retains the original aggregate work comparison and supplies new measured all-in times at two declared construction caps, individual proof size, verifier time, peak process memory, and complete trajectories. The two constructors use different local-proposal allocations, so their difference is not presented as a clean causal ablation of one feature.

**Location:** paper/evidence.tex; paper/supplement.tex; results/work_curves.csv

No universal efficiency advantage is claimed. Time caps are soft, and completed exact operations are charged.

## R48-F06 — Unbounded price generation and missing loss bounds

A portfolio-completion proposition bounds the ideal clipped price supremum by feasible occupation upper witnesses over all positive-support masks. The strict-reference mixing lemma repairs approximate occupation points into exact feasible upper witnesses. The audit searches caps 256, 1024, 4096, and 16384 on all eight unfinished rows and reports uncapped-upper minus capped replay. A rational-basis bound gives a finite, though impractical, universal cap.

**Location:** paper/pricecompletion.tex; replication/price_audit.py; replication/check_price.py; generated/price_caps.tex

Implemented theory and executed exact loss upper bounds. Loose occupation upper witnesses are not called resolved price optima.

## R48-F07 — Bilinear completion is not yet an algorithm

The new shared-regret-budget cover branches in n(T-1) coordinates. Conditional on a box, backward node programs enumerate feasible pure actions and crossing action pairs, avoiding a bilinear node solve. Both ordinary and price-enhanced node minimizers are repaired, and complete cover objects are independently replayed. A theorem gives an explicit error modulus in budget diameter, witness error, and deployment precision.

**Location:** paper/budget.tex; replication/budget.py; replication/check_budget.py

Implemented and executed on all twelve historical primary models. The constructor is not uniformly faster.

## R48-F08 — Search complexity

The manuscript states the exact smaller coordinate count, an explicit mesh sufficient for a requested width, the exponential covering count, and per-node operation counts. It does not infer polynomial complexity from fewer coordinates. The reset subclass instead has an explicitly linear finite proposal representation.

**Location:** paper/budget.tex; paper/reset.tex; generated/finite_resources.tex

The structural complexity statement is proved; strong general practical scaling remains unestablished.

## R48-F09 — External verified comparator

The revision separates arithmetic certificates from native solver statuses and retains the historical uncertified SCIP comparison only as such. The new budget constructor is a different verified search formulation; two HiGHS backends and a JavaScript reader provide additional implementation checks. They are not described as an independently authored external verified global solver.

**Location:** paper/evidence.tex; paper/supplement.tex; replication/check_diffuse.mjs

No new external verified-global-optimizer performance comparison is claimed. This referee request is not fully met.

## R48-F10 — Small synthetic sample

The new protocol freezes three seeds for each of thirteen configurations, giving 39 distinct diffuse models and 78 method runs. The seeds and source hashes were committed before evaluation. Every intermediate grid and failure rule is retained. The twelve historical finite cases are a separate retrospective study, not newly counted environments.

**Location:** PROTOCOL.json; EVALUATION_COMPLETE.json; replication/evaluate.py

Implemented. This remains a designed numerical sample, not an empirical population.

## R48-F11 — Confounded scaling

Horizon, number of actions, discount factor, operating allowance, and spatial slope vary one factor at a time around a fixed baseline. Each configuration has three seeds. Absolute width, relative width, normalized decision loss, all-in work, LP dimensions, and memory accompany the results. The older jointly varying cohort is not used to identify separate scaling effects.

**Location:** generated/diffuse_factors.tex; generated/diffuse_all.tex; generated/diffuse_economic.tex

Implemented within the uniform-reset model class; no high-dimensional-state scaling claim is made.

## R48-F12 — A difficult operating oracle

The original witness-only finite constructors and their precision budgets are preserved; the new budget theorem retains explicit dependence on witness error. Every finite row now exposes its guard ratio and oracle time. The reset model has analytically tractable operating values and is explicitly not a test of an expensive fitted, neural, or sparse-grid oracle.

**Location:** paper/finite.tex; paper/budget.tex; generated/finite_diagnostics.tex; results/diagnostics.json

The interface is strengthened and audited, but the requested hard end-to-end operating-oracle experiment is not supplied.

## R48-F13 — Diffuse initial laws and continuous kernels

The new restriction--averaging lemma is exact for cellwise density kernels over the whole Borel-policy class. Uniform primitive and total-variation errors yield a lower finite problem at a relaxed allowance and an upper one at a tightened allowance, with explicit transfer errors and a stopping modulus. The initial law is held fixed. A uniform-reset experiment executes both endpoints under a diffuse initial law and a continuous transition density.

**Location:** paper/density.tex; paper/reset.tex; replication/diffuse.py; replication/check_diffuse.py

Implemented paired theorem and executable diffuse example. Singular moving-atom approximations do not satisfy the density argument and are kept separate.

## R48-F14 — Small fleet graphs and changed objective law

The finite-observation fleet theorem, exact graph sizes, and original two-point-law intervals are retained without substitution for the uniform law. The new primary experiment genuinely uses the uniform initial law and a diffuse transition density. The article does not claim that this structured density result closes the original thirty moving-atom uniform-law intervals.

**Location:** paper/continuum.tex; paper/density.tex; generated/historical_fleet.tex

Paired diffuse-law evidence is supplied in a different explicitly stated kernel class; larger original controlled-atom fleet closures are not supplied.

## R48-F15 — Economic substance and arbitrary dollars

The current main article states fleet costs and budget distinctions in normalized implementation units. It replaces monetary headlines by certified implementation savings relative to an operating-best policy, a deployment-fee separation rule, and cost-normalization-invariant decision loss. The historical dollar example is preserved only inside the explicitly labeled historical article.

**Location:** paper/continuum.tex; paper/evidence.tex; generated/diffuse_economic.tex

No estimated/calibrated application, institutional validation, or empirical welfare conclusion is fabricated. A substantive empirical application remains outstanding.

## R48-F16 — Scale-comparable accuracy

The registered absolute target is unchanged. Relative width, normalized decision loss, and certified savings are reported for every diffuse model, with exact underlying fractions. The article proves that common positive rescaling of implementation costs, fees, budgets, and accuracy preserves the stated decisions.

**Location:** paper/reset.tex; paper/evidence.tex; generated/diffuse_economic.tex

Implemented; the common absolute target is no longer the sole economic accuracy interpretation.

## R48-F17 — Computational ties

The original T0, T1, and T2 outcomes remain visible, including the exact zero-cost closure and two original failures. The uncapped audits include T0 and T2. Separate constant-affine analytic tests use a nontrivial optimal face at four horizons and known positive-cost optima without the hidden-potential generator. They test formula validity, not broad tie-family performance.

**Location:** replication/test_contracts.py; results/price-audit-ties*.json; paper/evidence.tex

Additional algebraic/analytic checks supplied; no large prospectively sampled tie-family performance study is claimed.

## R48-F18 — Theorem-level positioning

The introduction now compares occupation constraints, information relaxation, approximate-DP LPs, finite constrained-control approximation, robust DP, batch safe improvement, semi-infinite programming, polynomial moment optimization, and verified computation at the level of policy classes, constraints, and target endpoints. All old references are retained and seven primary references are added.

**Location:** paper/front.tex; paper/references.tex

Implemented. Novelty is attached to the common-budget consistency and paired all-restart transfer, not to generic LP or branch-and-bound machinery.

## R48-F19 — Independent scientific replication

A standalone external-facing target specification is included. A separate JavaScript BigInt implementation reconstructs thirteen representative diffuse certificates from raw model files, with no Python or constructor imports. The source freeze, same-project arithmetic readers, clean-runner reproduction, and external scientific replication are explicitly distinguished.

**Location:** paper/supplement.tex; replication/check_diffuse.mjs; results/cross-language.json; VERIFICATION.json

Cross-language and clean-environment checks supplied. These are not external authorship or independent institutional replication.

## R48-F20 — Scope and organization

The revision keeps the original common-policy research object and title, while organizing the scientific argument as one chain: exact price relaxation, shared-budget completion, operating-witness certification, paired continuum transfer, and an executed diffuse contract. Complete historical text is preserved in the supplement rather than deleted. The main conclusion explicitly distinguishes general theorems from the structured experiment and remaining empirical validation.

**Location:** paper/main.tex; paper/front.tex; paper/evidence.tex; paper/archive_r48

Scope is strengthened rather than abandoned; numerical claims remain tied to the actually executed model class.

## R48-T01 — Closure taxonomy

The main historical discussion separates zero-cost T1, root Q0, branching W0/I0, absent medium/large positive-cost closures, and zero additional price-relative R48 hits. The new diffuse cohort is reported separately.

**Location:** paper/evidence.tex

## R48-T02 — Upper costs and relative widths

Original upper costs and relative widths appear beside absolute historical widths. Every new diffuse model has relative and normalized decision loss, and all exact endpoints remain in JSON.

**Location:** generated/historical_primary.tex; generated/diffuse_economic.tex

## R48-T03 — Root and incumbent movement

All 48 finite constructions report initial upper, root lower, final endpoints, and separate upper/lower movements. The lower-movement share is stored when its denominator is nonzero.

**Location:** generated/finite_diagnostics.tex; results/diagnostics.json

## R48-T04 — Complete work curves

Every retained diffuse grid and every recorded finite improvement is written to a common CSV with cumulative time and both endpoints. Final-only tables do not replace these trajectories.

**Location:** results/work_curves.csv

## R48-T05 — Separate process memory

Every model--method call is a new worker process. Peak memory is the worker high-water value, separately reported from proof bytes. Historical R48 sequential-family memory is not relabeled method-isolated.

**Location:** replication/evaluate.py; generated/finite_all.tex

## R48-T06 — Resource dimensions

All diffuse LP variables/constraints are retained per grid. Finite numerical-variable counts, leaves, proof bytes, rational bit lengths, and verifier time are tabulated. Budget rows use action/pair enumeration rather than a floating node LP. An explicit count of every old bilinear product is not reconstructed as a new measured statistic.

**Location:** generated/finite_resources.tex; results/*-highs-*.json

## R48-T07 — Mask attempts and statuses

The audit retains every attempted mask and numerical status for every cap. The main finite diagnostics retain the original proposal mask logs. Masks used in the uncapped upper cover are also retained with their rational witnesses.

**Location:** results/price-audit-*.json; results/diagnostics.json

## R48-T08 — Four price caps

All eight original unfinished rows receive cap 256, 1024, 4096, and 16384 audits, with verified replay fields and ideal-upper-minus-replay loss bounds.

**Location:** generated/price_caps.tex

## R48-T09 — Mask enrichment

The audit considers every subset of the positive initial support, including pairs and larger sets. A small support in the largest models reduces this count even though all-state policy constraints remain.

**Location:** replication/price_audit.py

## R48-T10 — Five distinct lower objects

The article separates ideal uncapped price intervals, capped proposal fields, rational replay, root relaxation, and full-tree endpoints. Their records are not interchanged; price-audit exact operating values are diagnostic only.

**Location:** paper/pricecompletion.tex; results/diagnostics.json

## R48-T11 — Occupation primal witnesses

Every certified audit occupation point contains rational action flows and edge allocation masses. A separately implemented reader checks flow conservation, capacities, costs, and every mask upper bound.

**Location:** proofs/price-audit-*.json.gz; replication/check_price.py

## R48-T12 — Shared-budget residuals

The supplement reports the maximum incoming-edge implied-budget spread for the retained occupation witnesses. This is a descriptive incompatibility measure, not a regression or a proven bound on the policy gap.

**Location:** generated/coupling.tex

## R48-T13 — Zero-flow budgets

For a zero-flow edge both allocation masses vanish; the edge imposes no ratio restriction. The proof and diagnostics do not divide by zero or impose a spurious common ratio on such edges.

**Location:** paper/pricecompletion.tex; paper/supplement.tex

## R48-T14 — Rational conditioning

The proof scan reports maximum numerator and denominator bit lengths, and the price audit reports maximum field magnitude. Arithmetic feasibility is exact even when rational sizes are large; no floating residual is presented as a conditioning-independent proof.

**Location:** generated/finite_resources.tex; generated/coupling.tex

## R48-T15 — Meaning of cap 4096

The main text calls it a numerical convention, not an economic constant. The uncapped occupation bound quantifies possible loss of the actually computed capped portfolio.

**Location:** paper/pricecompletion.tex; paper/evidence.tex

## R48-T16 — Individual witness budgets

All finite rows retain selected witness bits, xi divided by (1-beta)epsilon, oracle time, and price-amplification budget. The aggregate table is supplemented by exact per-run diagnostics.

**Location:** generated/finite_diagnostics.tex; results/diagnostics.json

## R48-T17 — Severe repair condition

The budget theorem and finite section explicitly require xi<(1-beta)epsilon and show its appearance in the denominator of the repair modulus. No uniform cheapness as beta approaches one is inferred.

**Location:** paper/budget.tex; paper/finite.tex

## R48-T18 — Initial support in largest cases

The article distinguishes objective support from all-state constraints and explains that support size determines the number of clipping masks, not the number of constrained restart rows.

**Location:** paper/evidence.tex; paper/supplement.tex

## R48-T19 — Upper versus lower weakness

Initial/final upper and root/final lower values are retained separately. The uncapped price audit further identifies rows where additional search in the same price family cannot account for the remaining common-policy interval.

**Location:** generated/finite_diagnostics.tex; generated/price_audit.tex

## R48-T20 — Local incumbent diagnostics

Optimizer status, iterations, initial incumbent, final incumbent and policy provenance are retained where emitted by the original constructor. The revision does not invent a causal count of local-only gains where that intermediate upper was not recorded.

**Location:** results/diagnostics.json; finite proof objects

## R48-T21 — Branch-rule ablations

The new budget rule and its diameter-reduction guarantee are specified and executed. Pure-widest, strong-branching, and reliability-branching studies were not separately frozen or executed; no claim of such an ablation is made.

**Location:** paper/budget.tex; PROTOCOL.json

## R48-T22 — Soft-limit overruns

Started exact operations, final encoding and replay are allowed to finish; their measured costs remain in the all-in record. Equal soft caps are not represented as equal wall-clock observations.

**Location:** paper/evidence.tex; replication/evaluate.py

## R48-T23 — Largest rational sizes

Numerator and denominator maxima are computed recursively over each finite proof and price-audit proof. They are paired with proof bytes and replay costs; a large denominator is not suppressed by printing only six decimal places.

**Location:** generated/finite_resources.tex; generated/coupling.tex

## R48-T24 — Fleet graph expansion

Active decision-node and terminal-forward-set sizes are retained with the exponential all-action bound. Additional duplicate-merge instrumentation was not executed, so no new empirical merge-count column is claimed.

**Location:** paper/continuum.tex

## R48-T25 — Off-forward extension

The analytic Borel extension remains in the main theorem and appendix. It is distinguished from the finite arithmetic reader; representative off-graph execution timings are not supplied as new measured results.

**Location:** paper/continuum.tex; paper/appendix.tex

## R48-T26 — Zero spatial error and graph growth

Every current interpretation of exact finite-atomic closure pairs zero spatial approximation error with the potentially exponential forward graph. The density theorem is a different approximation argument.

**Location:** paper/continuum.tex; paper/density.tex

## R48-T27 — Designed versus observed fleets

The current evidence table explicitly calls the states and weights designed, not data. The historical manuscript keeps its original wording only behind a preservation notice.

**Location:** paper/evidence.tex; paper/supplement.tex

## R48-T28 — Monetary framing

The current fleet discussion uses normalized costs and invariant budget comparisons. The old 500-dollar conversion is retained only as historical text and is not a headline current economic result.

**Location:** paper/continuum.tex

## R48-T29 — Fleet sensitivity

A general invariant budget/fee separation rule and diffuse allowance variations are supplied. A new sensitivity grid over the original fleet weights, epsilon and lottery fees was not executed and is not implied by those different exercises.

**Location:** paper/evidence.tex; generated/diffuse_economic.tex

## R48-T30 — Diffuse-law execution

The 39 new models have a uniform initial law and a continuous uniform reset density. Their lower certificates are valid for all Borel policies and their deployed upper policies satisfy every state constraint.

**Location:** paper/reset.tex; results/*-highs-*.json

## R48-T31 — Historical uniform-law rows

All thirty old positive-cost moving-atom intervals remain identified as historical and unfinished. The reset density results neither replace their initial law nor count as closures of those rows.

**Location:** paper/density.tex; paper/evidence.tex

## R48-T32 — Independent tie geometry

Four constant-affine positive-cost analytic tests use an optimal face without the hidden-potential generator. They test correctness and known values, not general-purpose performance over newly frozen tie families.

**Location:** replication/test_contracts.py

## R48-T33 — Proof-size budget

Proof size and verifier cost are reported for all finite runs and all diffuse grids. A new fixed-proof-size-budget optimization experiment was not frozen or executed. The revision does not call the resource table such an experiment.

**Location:** generated/finite_resources.tex; results/*-highs-*.json

## R48-T34 — Closest formulations and bibliography

The introduction compares the constraint sets and policy classes of occupation, approximate-DP LP, semi-infinite, moment, robust-control and safe-improvement formulations. Seven primary references are added without deleting any original reference.

**Location:** paper/front.tex; paper/references.tex

## R48-T35 — Assumption-to-evidence map

The main article includes a matrix separating finite models, price audits, exact atomic closure, general density transfer, and the executed uniform-reset subclass.

**Location:** paper/evidence.tex

## R48-T36 — Borel theorem versus finite checker

The article and supplement explicitly separate the analytic averaging/extension proofs from the finite certificate reader. The reader is not called a machine-checked proof of Borel measurability.

**Location:** paper/density.tex; paper/evidence.tex

## R48-T37 — What replay does not validate

Source identity, model definition, mathematical theorem, arithmetic replay and scientific generalization are treated as distinct claims. Neither internal source freeze nor a clean runner is called external replication.

**Location:** paper/evidence.tex; R50_REVIEW.md

## R48-T38 — Stable root index

The root review index links current PDFs, source entry points, response, protocol, results, proofs, manifest, reproduction and historical context. Prior entry points are not overwritten.

**Location:** R50_REVIEW.md

## R48-T39 — Clean-room build

R50_BUILD.sh regenerates every current numerical table from retained records, replays every proof, and builds all four PDFs. R50_REPRODUCE.sh reruns the frozen numerical study before that build. No uncommitted generated input is required.

**Location:** R50_BUILD.sh; R50_REPRODUCE.sh

## R48-T40 — Title and numerical boundaries

The original title and common-policy target are retained. The introduction and conclusion prominently distinguish the successful structured diffuse cohort from remaining general controlled-model scalability, hard-oracle, moving-atom and empirical-application questions.

**Location:** paper/front.tex; paper/evidence.tex

