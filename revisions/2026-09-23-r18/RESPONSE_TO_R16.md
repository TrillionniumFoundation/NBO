# Response to the referee: Neural Bellman Operators, R18

**Review input:** `review/econometrica-r16-numerical-methods-2026-09-23`, commit `82af00bc296da59e8a3a28ef1bf86c1d6fca2367`.

**New review object:** `ECTA_R18.tex/PDF`, `SUPP_R18.tex/PDF`, `RESPONSE_R18.tex/PDF`, and `R18_REVIEW.md`.

We thank the referee for distinguishing verification validity from successful numerical solution. This revision responds through an executed certificate-aligned objective, a theorem linking that objective to policy loss, paired complete-domain experiments, unrestricted classical candidates with method-specific witnesses, a nonlinear full-state control application with an explicit accuracy/work bound, and budget-feasible wealth compensation. The original neural-solver objective, title, economic model, control opportunities, and 0.01 accuracy target are retained. Historical mathematical and numerical content is preserved rather than deleted.

The most consequential remaining fact is stated directly: the final original-economy neural certificates improve substantially but do not reach 0.01. We do not substitute a separate model, a non-neural library, or an arithmetic regression test for that requirement. The detailed changes below identify which findings have been addressed, which numerical comparisons have improved, and which accuracy conclusions the evidence still does not establish.

## Scientific findings
### R16-F0 — Review-target integrity

**Preserved and extended.**

The new canonical review object is ECTA_R18.tex/PDF, SUPP_R18.tex/PDF, and RESPONSE_R18.tex/PDF, with R18_REVIEW.md as the entry point. The latest report is pinned at 82af00bc296da59e8a3a28ef1bf86c1d6fca2367 and its reviewed manuscript at 2932b74dad6d8d9efce5a114d5098a99ea17ab1f. R18 builds on the already executed R17 science at 982326994c8550db4e039d915c225a9ace8e3044. The new checks verify all 589 entries of the immutable scientific manifest. Historical sources, results, and PDFs are not overwritten. Source, execution, and publication identities are distinguished in the publication manifest.

### R16-F1 — Original nonlinear neural accuracy

**Substantive certificate progress; the unchanged target is not attained.**

We retain the original economic model, continuous action comparison, full-domain requirement, and 0.01 target. The complete-cover objective now gives strictly decreasing raw certificates at 0, 100, and 400 updates for all ten accessibility-aware seeds. The final range is 7.27831906346675–7.343665026665505, compared with initial values 26.30051415819305–26.666727866770486. Every prescribed object is retained, not replaced by a selected incumbent. The paper reports these values directly and does not infer successful 0.01 accuracy from software test success. A fixed-witness theorem establishes a resolution-independent positive-residual floor above 6.27 for the final accessible critics. This identifies a concrete remaining witness approximation problem rather than attributing the gap to arithmetic or changing the scientific target. Neither the sharp non-neural library nor the new nonlinear inventory result is substituted for the original neural solve.

### R16-F2 — Anti-alignment of the sampled objective

**Addressed by an executed certificate-aligned objective and quantitative audit.**

The historical 800-to-2,400 update experiment is now described exactly: all ten certificates worsen, while sampled residual MSE decreases for nine seeds. The primary algorithm uses a differentiable interval envelope of both signed residuals on the entire 1,024-cell cover at every update. Every selected proposal is independently checked by MPFR and accepted only if its complete certificate decreases. All raw proposals and acceptance records are retained. The new trainable-envelope theorem controls policy loss by a directed soft maximum plus an explicitly checked endpoint correction; the new audit verifies that implication for all 60 paired-architecture checkpoints and 61,440 cells. The largest correction is below 1.20e-13. Raw certificates decrease in every declared trajectory, so the observed trend is not manufactured by incumbent selection. This is evidence for the executed objective, not an unconditional convergence theorem for Adam.

### R16-F3 — Boundary architecture and finite-budget ablation

**Requested matched experiment supplied; no uniform finite-budget advantage claimed.**

There are ten paired seeds, two widths, identical initialization logic, optimizer settings, complete covers, and budgets 0/100/400. Every checkpoint has a signed decomposition. At width 16 the accessible final bound wins all five pairs; at width 32 the all-face final bound wins all five pairs. The mean accessible-minus-all-face final difference is about 0.005049. The paper retains this reversal and distinguishes it from the proof that the all-face class is asymptotically inconsistent. A theorem about trace consistency is not presented as a theorem about finite-budget optimization rankings.

### R16-F4 — Policy-iteration theorem versus implemented algorithm

**The methodological center now analyzes the executed algorithm.**

The stationary finite-MDP recurrence is retained, with full proof, under the explicitly auxiliary heading “An auxiliary finite-Bellman policy-iteration bound.” It is not used to claim that the historical actor/critic implemented certified policy iteration. The primary method is now defined by its actual proposal graph, complete certificate, and strict acceptance rule, and the central objective theorem applies to that graph. We additionally prove a finite-horizon defect allocation, with total error 2q^N b + sum q^n(2 epsilon_n + eta_n), and exact-rational regression tests. Time-local defects scaled by C_rho(h) accumulate as C_rho(T), without importing a stationary squared resolvent. This is not represented as an executed continuous-time policy-iteration transfer theorem: the primary neural and classical policies are checked directly in continuous time.

### R16-F5 — Two-mode inventory example and dimensional significance

**A nonlinear full-state control problem and explicit uniform accuracy theorem are added.**

The quadratic two-mode model is preserved as a validation example, with its analytic reduction stated prominently. The new application is a heterogeneous nonlinear 12-date inventory problem with 8, 32, or 128 coordinates. Its neural input is the complete state vector and its output is the full 12d-dimensional control plan. Nonquadratic individual and cyclic cross-product costs depend on every coordinate; no Riccati labels or known value are supplied. Three predeclared neural seeds are trained on the original cost. Strong convexity gives a quantitative certificate for a declared gradient-correction stage. At d=128, the state-uniform total-cost bound decreases from 0.1248195711352104 at 16 corrections to 0.0003596086619013272 at 24 and 1.0360425735991298e-6 at 32. This is a deterministic strongly convex nonlinear planning problem, not a generic high-dimensional stochastic HJB result or proof that neural initialization is necessary.

### R16-F6 — Restricted baselines and a poor common critic

**Both design confounds are removed; sharp matched accuracy remains unestablished.**

The new Markov-chain and semi-Lagrangian generators use the original action grids without the neural portfolio-distance multiplier on interior controls. They treat the upper grid column as an interior continuation trace and compare zero-portfolio continuation with immediate settlement for nonzero portfolio there. The resulting interpolated policies have a separately checked inaccessibility property. Each candidate has its own independently trained witness and a complete continuous-time check over the original continuous action set. Generation, witness training, and verification time are separately reported for all six configurations. Bounds range approximately from 7.31451 to 7.77413; none reaches 0.01. We therefore do not call these a matched-0.01 efficiency frontier or rank actual policy values from loose certificates. The historical restricted/common-witness table remains, with the restriction prominent in its caption and note.

### R16-F7 — Accuracy versus work and approximation floors

**Actual certificate/work sequences and separate obstruction/accuracy results supplied.**

The paper distinguishes raw training trajectories, fixed-network cover refinement, and a genuine correction-budget accuracy theorem. The original neural raw bounds improve at all declared training budgets, with the full cost of all certificate checks retained, but do not reach the requested sequence of small original-economy tolerances. Refining the final seed-17100 accessible network from 1,024 to 8,192 to 65,536 cells gives 7.33962418, 7.28022178, and 7.25155951. The new fixed-witness floor shows why this cannot solve the original gap by cover refinement alone. The nonlinear inventory application has a state-uniform total-error/work curve with a proved O(Hd) cost per correction and logarithmic correction count in Hd/epsilon. That is a positive accuracy theorem for its own model, not a replacement for an original-economy sharp frontier. The retained 0.005 dual-floor result is not concealed or relabeled as convergence.

### R16-F8 — Neural identity versus the specialized sharp solver

**The neural-solver objective and title are preserved; numerical objects remain separate.**

The paper remains Neural Bellman Operators and seeks accurate, competitive neural solutions of the original dynamic economic problem. Its core algorithm is stated as an executable neural proposal/witness/certificate procedure rather than a collection of loosely interchangeable methods. The central theorem now concerns the actual complete-cover objective. We do not rename the deterministic time-control/dual library as a neural solver. The new nonlinear neural-initialized solver includes its gradient correction explicitly, and its strong classical comparators are retained. The original flagship accuracy requirement is not claimed resolved by these distinct results.

### R16-F9 — MPFR and shared mathematical premises

**The independent-arithmetic scope is preserved.**

All eighteen historical nodes remain recomputed with MPFR-directed arithmetic. The paper continues to identify shared economic derivations, quadrature mathematics, stopping inequalities, envelope logic, indexing, and the C/MPFR interface. The new objective replay tests the quantitative implementation bridge but does not formally verify all of those shared premises. Exact-rational regression tests and numerical agreement are not called an independent end-to-end mathematical proof.

### R16-F10 — Economic welfare normalization

**An explicit budget-feasible sufficient wealth compensation is supplied.**

For each selected policy in the fresh original-economy library, an initial wealth increase of 39/5000 = 0.0078 finances a constant consumption increment 0.0078/C_0.02(1), while preference control, zero portfolio, consumption cap, and stopping settlement remain unchanged. A proof and MPFR checks establish admissibility for all 20 price-library policies, no wealth exit, and a utility gain of at least 0.010094048517141695, above the original uniform regret upper bound 0.009981645275150275. The wealth increase is 0.624% of initial wealth 1.25. This is sufficient budget-feasible compensation with an explicit policy adjustment, not the exact minimum wealth equivalent of an unchanged policy or an empirical calibration. The old externally financed top-up is preserved but secondary. No sharp welfare normalization is assigned to the much larger neural certificate.

### R16-F11 — Theory disconnected from numerical execution

**A central implemented-objective result and a nonlinear accuracy/work theorem are supplied.**

The trainable-envelope theorem bounds policy regret by the implemented complete-cover smooth maximum plus a checkable numerical discrepancy. It is instantiated for every retained paired-architecture checkpoint, with exact logits and directed evaluation records. The paper proves separately why monotone certificate acceptance does not imply monotone true policy values, including a constructive counterexample. The nonlinear control theorem derives global Hessian bounds 4I <= Hessian F <= (177/8)I, contracts gradients by 145/209 per exact-real correction, and establishes a state-uniform total-cost/error/work bound. Classical convexity and verification ingredients are acknowledged rather than claimed as new in isolation. These theorems do not prove global convergence of the nonconvex original neural optimizer or a neural speed advantage.

### R16-F12 — Exact-real policies and deployed floating-point inference

**The contract is explicit and is not expanded by inference.**

Original neural certificates concern exact stored dyadic weights, mathematical activations, and the specified bounded head perturbation before the portfolio factor. The nonlinear cube-uniform theorem concerns exact-real initialization and exact rational-step correction. Separately, stored floating-point plans are certified at their exact stored query vectors by MPFR KKT residuals. Neither result certifies an undocumented activation library, arbitrary floating-point inference graph, SDE simulator, or execution engine. The new objective audit is a rigorous post-hoc check on frozen logits, not a deployment certificate.

### R16-F13 — Economic model scope

**A new nonlinear multi-product application is added with its structure stated.**

The original two-state stochastic economy is retained unchanged as a demanding boundary/certification test. The new inventory planner has heterogeneous products, nonlinear own-inventory penalties, nonlinear cross-product coupling, and a policy plan that depends on the full high-dimensional state. Its unknown value is not analytically collapsed to two gain modes. The application is uncalibrated and deterministic, and it deliberately exposes its strong-convexity structure to classical competitors. It adds genuine nonlinear vector-state evidence without claiming that the original stochastic neural accuracy problem has disappeared.

## Additional technical comments

### R16-T1 and T2 — Exact deterioration statement and loss mismatch

The historical text now says all ten certificates worsen, and the new table/diagnostic records that sampled MSE falls for nine seeds. Exact ratios and all endpoint losses remain in diagnostics/r16_loss_mismatch.json.

### R16-T3 and T4 — Refinement floor and multi-seed ablation

Both architecture variants are refined through 65,536 cells for the fixed first-seed final object. The analytical floor is independent of cover resolution. The controlled ablation has ten paired seeds and three budgets with full signed decompositions.

### R16-T5 and T6 — Baseline restrictions and comparison validity

The historical table is labeled restricted/common-witness. New interior action grids have no neural distance multiplier, each policy has its own witness, and no loose upper-bound ranking is interpreted as actual solver-quality ranking.

### R16-T7 and T8 — Validated Riccati baseline and total loss

A closed-form/MPFR monotone-cell Riccati benchmark replaces reliance on an uncertified RK45 reference. For 32, 128, 512, and 2,048 time cells, both per-coordinate and d=128 total losses are displayed. The 128-cell total bound is below 0.002457; the 2,048-cell total bound is below 9.624e-6. Historical neural total losses above 0.01 remain visible.

### R16-T9 — Stationary amplification constants

The supplement instantiates both multipliers at 64, 128, and 256 time steps. The evaluation multipliers are approximately 5.12e6, 2.048e7, and 8.192e7. It identifies the implied defect levels as one-use additive-term requirements, not infinite-iteration accuracy guarantees. The finite-horizon alternative is proved separately.

### R16-T10 — The price-library floor

The fresh 0.01 threshold attainment, historical 0.005 failure, and specialized upper-relaxation floor are all retained. R18 does not claim that adding nodes or MPFR precision removes the original dual relaxation gap.

### R16-T11 and T12 — Shared arithmetic premises and machine contract

The manuscript preserves the independent-arithmetic/shared-mathematics distinction and the requirement that an admissible portfolio perturbation precede multiplication by the boundary-distance factor. The new complete-cover objective bridge does not certify the deployed floating-point graph.

### R16-T13 — Control differences

Full-domain final ranges and uniform changes from initialization are retained for consumption, preference adjustment, and portfolio for every accessible seed. In addition, the new range audit covers all six unrestricted classical policies and all twenty fresh-library actors. The supplement provides a complete comparison table. Classical controls are defined as original-action-clipped exact-real bilinear state interpolants; no neural wealth-distance multiplier is imposed. The fresh-library ranges hold for every selected price in [0.5,8] and every pre-stopping time. These are rigorous ranges, not sampled confidence intervals or control-optimality statements.

### R16-T14 — One executable core algorithm

The primary original-economy algorithm is joint neural complete-cover envelope minimization, frozen-object MPFR checking, and strict certificate-based incumbent replacement, with every raw proposal retained. The finite-MDP lemmas, specialized dual, Riccati validation, and nonlinear strongly-convex specialization have explicit separate roles.

## Review gates and claim-to-evidence map

| Gate | R18 evidence | Exact conclusion |
|---|---|---|
| R17-A: accurate original neural solve | Ten complete-cover trajectories; immutable full-domain certificates; fixed-witness floor | Certificates improve, but the original 0.01 accuracy target is not attained. |
| R17-B: certificate-aware algorithm | Executed envelope objective, independent strict acceptance, all 60 objects, new bridge theorem/audit | Operational use of complete-domain certificate information is established; global Adam convergence and monotone true policy improvement are not asserted. |
| R17-C: matched classical baselines | Two original-action generators, six separate witnesses, full continuous-time checks and separated costs | Design confounds are removed; sharp original-economy matched accuracy is not established. |
| R17-D: implemented policy-iteration claim | Actual core algorithm now explicitly defined and analyzed; stationary lemma auxiliary; finite-horizon lemma separately proved | No unexecuted continuous-time policy-iteration or unproved transfer is claimed. |
| R17-E: nonlinear high-dimensional control | Full-state neural plans at 8/32/128 coordinates, nonlinear coupled unknown-value model, uniform correction theorem and classical comparisons | A state-uniform nonlinear control-plan accuracy/work bound is established under strong convexity; generic stochastic scalability or neural superiority is not asserted. |
| R17-F: standard welfare interpretation | Feasible 0.0078 initial-wealth adjustment, explicit controls, all 20 library policies checked | Sufficient budget-feasible compensation is established, not minimum WEV, calibration, or neural welfare accuracy. |
| R17-G: coherent identity | Executable primary neural objective and certificate interface; comparator modules distinguished | Neural-solver ambition is preserved without assigning the specialized comparator's accuracy to the neural actor. |

## New execution and preservation

The R18 entry point verifies all 589 immutable R17 scientific files. It re-evaluates the trainable-envelope implication at 60 checkpoints (61,440 cells), re-executes two full-cylinder MPFR certificates, rechecks all 18 final nonlinear neural query plans, and runs 450 exact-rational arithmetic checks and 80 exact-rational finite-MDP cases. Gradient/Hessian point checks are labeled regression diagnostics, not global proofs. The new mathematical proofs are in the main appendix. Complete signed tables, control ranges, nonlinear budget curves, implementation semantics, and reproduction instructions are in the supplement.

The latest review report, preceding manuscripts, source code, raw networks, and complete results remain unchanged. The new revision is written only to new R18 files and new revision branches. The publication manifest distinguishes the review base, scientific input, new source commit, execution records, and published artifacts. The final review branch and its referee copy point to the same publication commit.
