# R51 response to the latest R48 referee report

The review report is addressed on top of the complete R50 revision. The manuscript retains its objective, title, earlier theorems, proofs, comparisons, and all failed intervals. The new contribution is an exact common-moment solver for state/action-dependent continuous densities under the original diffuse initial law.

## Major findings

### R48-F01: Complete immutable review object

R51 adds ordinary article, supplement and response entry points, full generated tables, a complete binary-cover archive, a standalone reader, a verified source archive, and a content-hash manifest. The prior publication artifact contained a truncated source tarball although its PDFs were committed; the new workflow explicitly validates every archive member and cannot report publication success before that check.

**Retained R50 response:** The revision adds ordinary root entry points for the article, numerical supplement, referee response, and reconstructed historical article, together with a root review index and a one-command verification/build script. Missing historical numerical tables are regenerated from the original exact records. The publication manifest hashes sources, models, results, proofs, PDFs, and logs. The original review and prior revisions are not overwritten.

**Evidence boundary:** Implemented; the build and replay outcomes are reported in the final manifest, not assumed from the presence of a script.

### R48-F02: Method-relative target success

The new controlled-density study has 27/27 unrestricted target hits and 27/27 uniform-regret counterfactual hits. Seventeen rows prove a strict implementation saving. This is a distinct Borel-policy result, not a claim that the old price method has acquired additional R48 hits.

**Retained R50 response:** The revised article no longer counts tighter failed intervals as new target hits. It reports all twelve original rows, both new finite constructors at both caps, and a distinct new diffuse cohort. The latter gives positive-cost paired continuum certificates rather than a price-only attachment to inherited policies. The price and budget constructors are not declared uniform winners.

**Evidence boundary:** The original price method still has no extra R48 primary closures; the new evidence is explicitly separated.

### R48-F03: Medium and large positive-cost closures

R50 large reset results remain intact. The new controlled problem is an infinite-state two-date problem reduced exactly to two moments; it is not counted as a medium/large finite closure or long-horizon controlled-density result.

**Retained R50 response:** A new source-frozen study includes horizons 4, 8, 16, and 32, up to five actions and thousands of continuum policy rows; both endpoints are verified for the original diffuse-law target. Its largest LP has 24,608 variables. The paper states that uniform-reset structure, not arbitrary controlled-dynamics scalability, makes this construction effective.

**Evidence boundary:** Substantive structured continuum closures are supplied. Broad medium/large controlled finite scalability is not established.

### R48-F04: Large unfinished intervals

No unfinished historical interval is discarded. The new theorem resolves the controlled-density common continuation on a separately declared model class; the original eight finite failures and thirty moving-atom intervals remain separately identified.

**Retained R50 response:** All unfinished intervals remain in the main finite table and supplement. A new uncapped occupation audit distinguishes incomplete price optimization from the gap between the price relaxation and the common-policy problem. Six historical failed rows have price-family optima bracketed below 1e-8, while two retain visibly loose price upper witnesses.

**Evidence boundary:** The diagnostic resolves an identifiable source of uncertainty without relabeling the original policy problems as closed.

### R48-F05: Price cost versus benefit

Every new run reports isolated-worker construction, independent replay, all-in cost, cover size, proof size and memory. Power-of-two-node checkpoints give within-run width/work data. The uniform-regret comparison is economic, not a claim about the computational superiority of prices.

**Retained R50 response:** The article retains the original aggregate work comparison and supplies new measured all-in times at two declared construction caps, individual proof size, verifier time, peak process memory, and complete trajectories. The two constructors use different local-proposal allocations, so their difference is not presented as a clean causal ablation of one feature.

**Evidence boundary:** No universal efficiency advantage is claimed. Time caps are soft, and completed exact operations are charged.

### R48-F06: Unbounded price generation and missing loss bounds

The uncapped price upper witnesses and cap/mask audit from R50 are preserved. The new controlled solver needs no price cap or mask scheduling; its stopping inequality directly brackets the common-policy optimum.

**Retained R50 response:** A portfolio-completion proposition bounds the ideal clipped price supremum by feasible occupation upper witnesses over all positive-support masks. The strict-reference mixing lemma repairs approximate occupation points into exact feasible upper witnesses. The audit searches caps 256, 1024, 4096, and 16384 on all eight unfinished rows and reports uncapped-upper minus capped replay. A rational-basis bound gives a finite, though impractical, universal cap.

**Evidence boundary:** Implemented theory and executed exact loss upper bounds. Loose occupation upper witnesses are not called resolved price optima.

### R48-F07: Bilinear completion is not yet an algorithm

The exact common-moment theorem supplies a feasible-moment characterization, an explicit Borel realization, integrated lower rectangles and a quantitative two-coordinate refinement bound. This directly turns an omitted shared-continuation coupling into an executed global solver for genuinely controlled densities.

**Retained R50 response:** The new shared-regret-budget cover branches in n(T-1) coordinates. Conditional on a box, backward node programs enumerate feasible pure actions and crossing action pairs, avoiding a bilinear node solve. Both ordinary and price-enhanced node minimizers are repaired, and complete cover objects are independently replayed. A theorem gives an explicit error modulus in budget diameter, witness error, and deployment precision.

**Evidence boundary:** Implemented and executed on all twelve historical primary models. The constructor is not uniformly faster.

### R48-F08: Search complexity

For this structured model the sufficient cover count is of inverse-squared accuracy order, apart from precision work, with constants depending on operating slack. No general polynomial complexity claim is made. The effective dimension is exactly one in the no-control negative controls.

**Retained R50 response:** The manuscript states the exact smaller coordinate count, an explicit mesh sufficient for a requested width, the exponential covering count, and per-node operation counts. It does not infer polynomial complexity from fewer coordinates. The reset subclass instead has an explicitly linear finite proposal representation.

**Evidence boundary:** The structural complexity statement is proved; strong general practical scaling remains unestablished.

### R48-F09: External verified comparator

SciPy supplies an independent row-LP cross-check in the contract suite; it does not supply a verified global lower bound. No external global-solver victory or independently proof-logged comparator is asserted. The new primary solver uses no optimizer output for either endpoint.

**Retained R50 response:** The revision separates arithmetic certificates from native solver statuses and retains the historical uncertified SCIP comparison only as such. The new budget constructor is a different verified search formulation; two HiGHS backends and a JavaScript reader provide additional implementation checks. They are not described as an independently authored external verified global solver.

**Evidence boundary:** No new external verified-global-optimizer performance comparison is claimed. This referee request is not fully met.

### R48-F10: Small synthetic sample

Three frozen seeds appear in every one of nine cells. All 54 resulting runs are retained. The 27 models remain internally designed, and the source-freeze record explicitly discloses pilot-guided design rather than asserting external validation.

**Retained R50 response:** The new protocol freezes three seeds for each of thirteen configurations, giving 39 distinct diffuse models and 78 method runs. The seeds and source hashes were committed before evaluation. Every intermediate grid and failure rule is retained. The twelve historical finite cases are a separate retrospective study, not newly counted environments.

**Evidence boundary:** Implemented. This remains a designed numerical sample, not an empirical population.

### R48-F11: Confounded scaling

The family-A cells share seed perturbations and vary one factor at a time: discount, allowance, or density control. No-control and reversed-control cells separately diagnose dependence on the transition mechanism.

**Retained R50 response:** Horizon, number of actions, discount factor, operating allowance, and spatial slope vary one factor at a time around a fixed baseline. Each configuration has three seeds. Absolute width, relative width, normalized decision loss, all-in work, LP dimensions, and memory accompany the results. The older jointly varying cohort is not used to identify separate scaling effects.

**Evidence boundary:** Implemented within the uniform-reset model class; no high-dimensional-state scaling claim is made.

### R48-F12: A difficult operating oracle

The new raw operating rewards yield exactly known operating values, which are printed in the model specification. This allows direct examination of common-continuation optimization but does not constitute a difficult learned-oracle experiment. The inherited witness-interface and precision results remain unchanged.

**Retained R50 response:** The original witness-only finite constructors and their precision budgets are preserved; the new budget theorem retains explicit dependence on witness error. Every finite row now exposes its guard ratio and oracle time. The reset model has analytically tractable operating values and is explicitly not a test of an expensive fitted, neural, or sparse-grid oracle.

**Evidence boundary:** The interface is strengthened and audited, but the requested hard end-to-end operating-oracle experiment is not supplied.

### R48-F13: Diffuse initial laws and continuous kernels

The new transition density depends jointly on state, successor state and selected action. Its moment-set proof ranges over all Borel continuations, its upper realization is globally feasible, and no spatial discretization enters either endpoint. The theorem does not apply across singular moving-atom kernels.

**Retained R50 response:** The new restriction--averaging lemma is exact for cellwise density kernels over the whole Borel-policy class. Uniform primitive and total-variation errors yield a lower finite problem at a relaxed allowance and an upper one at a tightened allowance, with explicit transfer errors and a stopping modulus. The initial law is held fixed. A uniform-reset experiment executes both endpoints under a diffuse initial law and a continuous transition density.

**Evidence boundary:** Implemented paired theorem and executable diffuse example. Singular moving-atom approximations do not satisfy the density argument and are kept separate.

### R48-F14: Small fleet graphs and changed objective law

The uniform initial population is retained. No replacement by a two-point fleet is used. The new proof solves a genuinely controlled-density target, while the finite-fleet results and their exponential reachability qualifications remain in the inherited article.

**Retained R50 response:** The finite-observation fleet theorem, exact graph sizes, and original two-point-law intervals are retained without substitution for the uniform law. The new primary experiment genuinely uses the uniform initial law and a diffuse transition density. The article does not claim that this structured density result closes the original thirty moving-atom uniform-law intervals.

**Evidence boundary:** Paired diffuse-law evidence is supplied in a different explicitly stated kernel class; larger original controlled-atom fleet closures are not supplied.

### R48-F15: Economic substance and arbitrary dollars

Seventeen exact interval separations prove conditional savings from state-dependent continuation relative to the uniform-regret counterfactual. The fee test and scale-free ratio make the decision implication explicit. The primitives are not estimated, and no arbitrary dollar conversion or welfare estimate is introduced.

**Retained R50 response:** The current main article states fleet costs and budget distinctions in normalized implementation units. It replaces monetary headlines by certified implementation savings relative to an operating-best policy, a deployment-fee separation rule, and cost-normalization-invariant decision loss. The historical dollar example is preserved only inside the explicitly labeled historical article.

**Evidence boundary:** No estimated/calibrated application, institutional validation, or empirical welfare conclusion is fabricated. A substantive empirical application remains outstanding.

### R48-F16: Scale-comparable accuracy

The absolute target remains 1/1000. Every new run also reports relative width; the supplement explains scale-invariant fee and policy-class savings. A nonpositive saving certificate is never interpreted as evidence that unrestricted policies are worse.

**Retained R50 response:** The registered absolute target is unchanged. Relative width, normalized decision loss, and certified savings are reported for every diffuse model, with exact underlying fractions. The article proves that common positive rescaling of implementation costs, fees, budgets, and accuracy preserves the stated decisions.

**Evidence boundary:** Implemented; the common absolute target is no longer the sole economic accuracy interpretation.

### R48-F17: Computational ties

The three no-control rows are negative controls, not optimal-action tie experiments. They correctly produce no strict savings. The original tie evidence and open tie cases remain unchanged; this study is not relabeled as broad tie robustness.

**Retained R50 response:** The original T0, T1, and T2 outcomes remain visible, including the exact zero-cost closure and two original failures. The uncapped audits include T0 and T2. Separate constant-affine analytic tests use a nontrivial optimal face at four horizons and known positive-cost optima without the hidden-potential generator. They test formula validity, not broad tie-family performance.

**Evidence boundary:** Additional algebraic/analytic checks supplied; no large prospectively sampled tie-family performance study is claimed.

### R48-F18: Theorem-level positioning

The original theorem-level literature map and all sixteen R50 references are retained. The elementary moment extremum is proved directly and is not advertised as a new general moment theorem; the contribution is its exact coupling of operating and implementation continuation for the stated policy object.

**Retained R50 response:** The introduction now compares occupation constraints, information relaxation, approximate-DP LPs, finite constrained-control approximation, robust DP, batch safe improvement, semi-infinite programming, polynomial moment optimization, and verified computation at the level of policy classes, constraints, and target endpoints. All old references are retained and seven primary references are added.

**Evidence boundary:** Implemented. Novelty is attached to the common-budget consistency and paired all-restart transfer, not to generic LP or branch-and-bound machinery.

### R48-F19: Independent scientific replication

A standalone standard-library reader uses independently written corner enumeration, mixture integration, and a longer logarithm series. Mutation tests challenge cover completeness and feasibility. This is stronger implementation separation but not an external research-team replication; the external-facing benchmark specification makes that remaining task well-defined.

**Retained R50 response:** A standalone external-facing target specification is included. A separate JavaScript BigInt implementation reconstructs thirteen representative diffuse certificates from raw model files, with no Python or constructor imports. The source freeze, same-project arithmetic readers, clean-runner reproduction, and external scientific replication are explicitly distinguished.

**Evidence boundary:** Cross-language and clean-environment checks supplied. These are not external authorship or independent institutional replication.

### R48-F20: Scope and organization

The title and original minimum-cost common-policy objective are retained. The article integrates the new controlled-density theorem, executable cover and conditional policy-class comparison, while preserving the complete R50 and R48 argument and all failed results. New structure is established rather than replacing the target by a narrower economic objective.

**Retained R50 response:** The revision keeps the original common-policy research object and title, while organizing the scientific argument as one chain: exact price relaxation, shared-budget completion, operating-witness certification, paired continuum transfer, and an executed diffuse contract. Complete historical text is preserved in the supplement rather than deleted. The main conclusion explicitly distinguishes general theorems from the structured experiment and remaining empirical validation.

**Evidence boundary:** Scope is strengthened rather than abandoned; numerical claims remain tied to the actually executed model class.

## Forty detailed comments

All forty detailed replies remain in RESPONSE_MAP.json and the attached full R50 response. R51 additions are indexed per item in the machine-readable map; inherited evidence is not described as new execution.

### R48-T01: Closure taxonomy

The main historical discussion separates zero-cost T1, root Q0, branching W0/I0, absent medium/large positive-cost closures, and zero additional price-relative R48 hits. The new diffuse cohort is reported separately.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T02: Upper costs and relative widths

Original upper costs and relative widths appear beside absolute historical widths. Every new diffuse model has relative and normalized decision loss, and all exact endpoints remain in JSON.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T03: Root and incumbent movement

All 48 finite constructions report initial upper, root lower, final endpoints, and separate upper/lower movements. The lower-movement share is stored when its denominator is nonzero.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T04: Complete work curves

Every retained diffuse grid and every recorded finite improvement is written to a common CSV with cumulative time and both endpoints. Final-only tables do not replace these trajectories.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T05: Separate process memory

Every model--method call is a new worker process. Peak memory is the worker high-water value, separately reported from proof bytes. Historical R48 sequential-family memory is not relabeled method-isolated.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T06: Resource dimensions

All diffuse LP variables/constraints are retained per grid. Finite numerical-variable counts, leaves, proof bytes, rational bit lengths, and verifier time are tabulated. Budget rows use action/pair enumeration rather than a floating node LP. An explicit count of every old bilinear product is not reconstructed as a new measured statistic.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T07: Mask attempts and statuses

The audit retains every attempted mask and numerical status for every cap. The main finite diagnostics retain the original proposal mask logs. Masks used in the uncapped upper cover are also retained with their rational witnesses.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T08: Four price caps

All eight original unfinished rows receive cap 256, 1024, 4096, and 16384 audits, with verified replay fields and ideal-upper-minus-replay loss bounds.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T09: Mask enrichment

The audit considers every subset of the positive initial support, including pairs and larger sets. A small support in the largest models reduces this count even though all-state policy constraints remain.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T10: Five distinct lower objects

The article separates ideal uncapped price intervals, capped proposal fields, rational replay, root relaxation, and full-tree endpoints. Their records are not interchanged; price-audit exact operating values are diagnostic only.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T11: Occupation primal witnesses

Every certified audit occupation point contains rational action flows and edge allocation masses. A separately implemented reader checks flow conservation, capacities, costs, and every mask upper bound.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T12: Shared-budget residuals

The supplement reports the maximum incoming-edge implied-budget spread for the retained occupation witnesses. This is a descriptive incompatibility measure, not a regression or a proven bound on the policy gap.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T13: Zero-flow budgets

For a zero-flow edge both allocation masses vanish; the edge imposes no ratio restriction. The proof and diagnostics do not divide by zero or impose a spurious common ratio on such edges.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T14: Rational conditioning

The proof scan reports maximum numerator and denominator bit lengths, and the price audit reports maximum field magnitude. Arithmetic feasibility is exact even when rational sizes are large; no floating residual is presented as a conditioning-independent proof.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T15: Meaning of cap 4096

The main text calls it a numerical convention, not an economic constant. The uncapped occupation bound quantifies possible loss of the actually computed capped portfolio.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T16: Individual witness budgets

All finite rows retain selected witness bits, xi divided by (1-beta)epsilon, oracle time, and price-amplification budget. The aggregate table is supplemented by exact per-run diagnostics.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T17: Severe repair condition

The budget theorem and finite section explicitly require xi<(1-beta)epsilon and show its appearance in the denominator of the repair modulus. No uniform cheapness as beta approaches one is inferred.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T18: Initial support in largest cases

The article distinguishes objective support from all-state constraints and explains that support size determines the number of clipping masks, not the number of constrained restart rows.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T19: Upper versus lower weakness

Initial/final upper and root/final lower values are retained separately. The uncapped price audit further identifies rows where additional search in the same price family cannot account for the remaining common-policy interval.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T20: Local incumbent diagnostics

Optimizer status, iterations, initial incumbent, final incumbent and policy provenance are retained where emitted by the original constructor. The revision does not invent a causal count of local-only gains where that intermediate upper was not recorded.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T21: Branch-rule ablations

The new budget rule and its diameter-reduction guarantee are specified and executed. Pure-widest, strong-branching, and reliability-branching studies were not separately frozen or executed; no claim of such an ablation is made.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T22: Soft-limit overruns

Started exact operations, final encoding and replay are allowed to finish; their measured costs remain in the all-in record. Equal soft caps are not represented as equal wall-clock observations.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T23: Largest rational sizes

Numerator and denominator maxima are computed recursively over each finite proof and price-audit proof. They are paired with proof bytes and replay costs; a large denominator is not suppressed by printing only six decimal places.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T24: Fleet graph expansion

Active decision-node and terminal-forward-set sizes are retained with the exponential all-action bound. Additional duplicate-merge instrumentation was not executed, so no new empirical merge-count column is claimed.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T25: Off-forward extension

The analytic Borel extension remains in the main theorem and appendix. It is distinguished from the finite arithmetic reader; representative off-graph execution timings are not supplied as new measured results.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T26: Zero spatial error and graph growth

Every current interpretation of exact finite-atomic closure pairs zero spatial approximation error with the potentially exponential forward graph. The density theorem is a different approximation argument.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T27: Designed versus observed fleets

The current evidence table explicitly calls the states and weights designed, not data. The historical manuscript keeps its original wording only behind a preservation notice.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T28: Monetary framing

The current fleet discussion uses normalized costs and invariant budget comparisons. The old 500-dollar conversion is retained only as historical text and is not a headline current economic result.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T29: Fleet sensitivity

A general invariant budget/fee separation rule and diffuse allowance variations are supplied. A new sensitivity grid over the original fleet weights, epsilon and lottery fees was not executed and is not implied by those different exercises.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T30: Diffuse-law execution

The 39 new models have a uniform initial law and a continuous uniform reset density. Their lower certificates are valid for all Borel policies and their deployed upper policies satisfy every state constraint.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T31: Historical uniform-law rows

All thirty old positive-cost moving-atom intervals remain identified as historical and unfinished. The reset density results neither replace their initial law nor count as closures of those rows.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T32: Independent tie geometry

Four constant-affine positive-cost analytic tests use an optimal face without the hidden-potential generator. They test correctness and known values, not general-purpose performance over newly frozen tie families.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T33: Proof-size budget

Proof size and verifier cost are reported for all finite runs and all diffuse grids. A new fixed-proof-size-budget optimization experiment was not frozen or executed. The revision does not call the resource table such an experiment.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T34: Closest formulations and bibliography

The introduction compares the constraint sets and policy classes of occupation, approximate-DP LP, semi-infinite, moment, robust-control and safe-improvement formulations. Seven primary references are added without deleting any original reference.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T35: Assumption-to-evidence map

The main article includes a matrix separating finite models, price audits, exact atomic closure, general density transfer, and the executed uniform-reset subclass.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T36: Borel theorem versus finite checker

The article and supplement explicitly separate the analytic averaging/extension proofs from the finite certificate reader. The reader is not called a machine-checked proof of Borel measurability.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T37: What replay does not validate

Source identity, model definition, mathematical theorem, arithmetic replay and scientific generalization are treated as distinct claims. Neither internal source freeze nor a clean runner is called external replication.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T38: Stable root index

The root review index links current PDFs, source entry points, response, protocol, results, proofs, manifest, reproduction and historical context. Prior entry points are not overwritten.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T39: Clean-room build

R50_BUILD.sh regenerates every current numerical table from retained records, replays every proof, and builds all four PDFs. R50_REPRODUCE.sh reruns the frozen numerical study before that build. No uncommitted generated input is required.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.

### R48-T40: Title and numerical boundaries

The original title and common-policy target are retained. The introduction and conclusion prominently distinguish the successful structured diffuse cohort from remaining general controlled-model scalability, hard-oracle, moving-atom and empirical-application questions.

Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.

**Boundary:** See the precise response; reporting and execution are distinguished.
