# Response to the R3 referee report

**Revision:** R4, 16 September 2026  
**Report answered:** `reviews/2026-09-16-econometrica-r3/referee_report.md` at `79a7d84be2cbbf9bd5d181599ee110540128e3b5`  
**New manuscript:** `ECTA_R4.tex`; standalone supplement: `SUPP_R4.tex`  
**New branch:** `revision/econometrica-r4-2026-09-16`

We thank the referee for identifying failures of correspondence between the written economic problems and their executable counterparts. Reproducibility of the earlier script did not establish that it solved the displayed model. R4 responds by changing the mathematical and computational substance, not by adding an audit protocol around the same calculations.

The revision supplies actual neural actors and critics, independent policy evaluation, a fully specified stochastic stopped economy, and a constrained coupled dynamic resource-allocation experiment. It also proves a quantitative approximate-operator value-loss bound and an economic cumulative-adjustment comparative static. The current paper is rewritten as an economic and numerical argument, with complete proofs and implementation details in a new supplement. All earlier sources and reports remain unchanged. No claim of journal appointment, actual submission, or editorial approval is made.

## R3-F1. Supply an executable neural method and evaluated economic policies

**Response.** `replication/r4/solver.py` now contains trained neural policy and value functions. `safeguard.py` trains the stopped preference model with separate parameter blocks, explicit frozen continuations, feasible output transformations, and a candidate improvement calculation. It saves all actor and critic weights, date-specific losses, optimizer statistics, complete policy arrays, and independently evaluated policy values. The default safeguarded experiment has eight dates, two-hidden-layer tanh actors of width 32, critics of width 64, and 2,048 training states; all three seeds 101, 202, and 303 are retained. The smaller-budget unsafeguarded pilot remains visible rather than being silently discarded.

A second actual neural implementation, `coupled_resource.py`, uses a convex feature critic and a bounded neural proposal actor in a stochastic shared-budget economy. It supplies nine dimension–seed runs, independent nonanticipative scenario-tree optimization, exact enumeration of the finite shock distribution during policy evaluation, and a same-weight deployment ablation. This is not a static arithmetic calculation. Neural training does not receive reference values or optimal reference policies. `replay.py` independently reloads the deposited weights and reproduces actions or complete policy costs without retraining.

The executed primary neural algorithms use the finite-step Bellman operator. The differential Hamiltonian is retained in the theory and in automatic-derivative and homothetic tests; we do not describe an unexecuted large-network differential-residual run as an experiment. Main §§2–3 and 5, Supplement S.1/S.6, and the replication README specify the actual algorithms and their evidence classes. The previous universal “three layers of 256 GELU neurons” description is replaced by the architectures that were actually run.

## R3-F2. Restore diffusion and covariance in the preference transition

**Response.** Both the NumPy reference and PyTorch training transition retain preference volatility, financial volatility, and their cross covariance. Four equiprobable sign branches reproduce the conditional covariance of the written Brownian model; the second financial sign combines correlation with an independent component. Continuation is integrated over all branches, not read at a single drift endpoint. The implementations are separately written and are checked against one another on terminal backups.

`diagnostics.py` tests the generator on constants, both coordinates, both squares, and the cross product. The interior test covariance is `[[0.0025,-0.002],[-0.002,0.0256]]`; time-step refinement separates the intended generator from order-step drift products. Three joint state–time refinements, additional spatial/time runs, and a richer action mesh are executed. The principal joint refinement reduces squared mesh width divided by time step from 0.04 to 0.02 to 0.01, rather than refining time alone on a fixed interpolating grid.

Main §5 and Supplement S.3 give the transition and discounted stopped backup explicitly. The four-point rule and line-exit mechanism are identified as approximations to the diffusion, not exact Brownian first-passage integration. The new error theorem has a separate operator-discrepancy term for precisely this reason. We do not rename a drift-only method a stochastic audit.

## R3-F3. Specify an economically coherent boundary mechanism

**Response.** R4 replaces the impossible state-constraint interpretation with a first-exit liquidation contract. The interior SDE, complete original control vector, diffusion coefficients, correlation, utility normalization, horizon, and terminal payoff are retained. The operating contract ends on first exit from the rectangle or at the terminal date, and the same declared payoff is paid at that stopping time. A start on the boundary settles immediately. An exiting wealth path does not obtain renewed interior continuation, and no resources are injected by clipping.

This is an explicit change in the boundary economy, not a proof that the old process was viable. Main §4 and Supplement S.3 explain the original nonviability and derive the stopped objective and Dirichlet payoff. A new analytical calculation verifies that the specified terminal payoff is a strict supersolution: its maximized flow-plus-generator-minus-discount is below −0.8162 for every admissible control and every nonnegative adjustment-cost coefficient. Stopped verification bounds the value above by that payoff; a fixed uniformly nondegenerate policy supplies the matching boundary limit. We do not assume classical differentiability at rectangle corners.

The program records branch exits, pre-exit overshoots, and induced-policy occupation and stopping statistics separately. A reflection regulator is inapplicable and is null with a reason. `graph_tests.py` evaluates the immediate-boundary settlement identity directly. A hard boundary identity is not labeled a global PDE accuracy certificate.

## R3-F4. Restore the adjustment margin and report all controls and genuine gains

**Response.** Positive bilinear interpolation and stochastic branches replace nearest-node rounding. The generator test explicitly checks that opposite adjustment controls produce different mean next preference states even when their drift displacement is less than a spatial cell. Preference adjustment now changes the continuation value.

The independent comparison in `analysis.py` reports both mean and maximum discrepancies for consumption, preference adjustment, and portfolio share over all common interior states and dates. A Bellman improvement is computed in value units using a richer feasible candidate search against the independently evaluated continuation of the policy being tested. It is not an action-distance statistic. The paper displays large policy switches and boundary-region errors rather than reporting a misleading zero for the entire policy vector.

The full problem is re-solved at adjustment costs 0.5, 2, and 8 on the same state, time, and action grids. Discounted cumulative adjustment effort is evaluated backward and by forward occupation accounting. The panel shows a decreasing cumulative effort measure. The paper adds a theorem establishing this economically meaningful ordering, including endogenous consumption, portfolio choice, and exit time, and an approximate-policy version showing how value errors limit a numerical monotonicity test. It does not infer a sign theorem for each policy coordinate from the formal condition `theta=V_u/k`. Main §§4–5, Supplement S.3, and the four NDU tables contain these changes.

## R3-F5. Separate the current self's criterion from continuation evaluation

**Response.** The temporal computation now stores ordinary continuation values, without reintroducing beta at every evaluation date. Only the acting self's one-shot criterion includes beta. The same equations appear in the main paper, supplement, and implementation. The discount factor and time step are explicit.

For log consumption with terminal log wealth, the coefficient recursion supplies an independent closed-form solution, including beta below one. The program checks the written evaluation equation and solves separate bounded one-shot optimizations against the actual frozen continuation coefficients at several wealth levels. The two-consumption-date, beta=0.7 regression reproduces the sophisticated first-date fraction 1/(1+2 beta), and retains the earlier geometric-beta fraction as a negative comparison. The beta-one test remains but is no longer treated as sufficient. Main §6 and Supplement S.5 contain the derivation.

## R3-F6. Correct the K-probe squared-loss estimand

**Response.** The trace experiment now averages the K quadratic forms before squaring the residual, repeats this over 20,000 independent batches for each K, and reports the batch-mean Monte Carlo standard error. It separately records individual-probe variance and batch-mean variance. The original mean-of-individual-squares statistic remains as an explicitly incorrect-objective negative control.

For the referee's matrix, the known excess expectation is 7.5/K. The new table compares the empirical repeated-batch means with that population quantity rather than interpreting one realized excess as its expectation. We also give and execute an off-diagonal U-statistic whose expectation is the exact squared residual. The proof states the independent-probe and differentiation assumptions, the possibility of negative sample values, and the selection issue when optimizing with reused probes. Main §3 and Supplement S.2 do not infer trained-policy accuracy from this algebraic regression. The resource experiment uses a finite-step operator and is not attributed to unexecuted Hutchinson acceleration.

## R3-F7. Repair the actor-stationarity implication constructively

**Response.** R4 reproduces the referee's quartic counterexample and proves that its bad stationary point is locally attracting despite a strictly positive improvement gap. The invalid implication from isolated stationary points to an optimal policy is not retained. The exact policy-improvement theorem is kept separate from parameter optimization and from stochastic-approximation limiting-set statements.

More importantly, the executable method now has a distinct improvement mechanism. A neural proposal is compared with feasible alternatives, and the convex resource case uses a linear minimization gap that bounds suboptimality of the surrogate action problem. Nonnegative squared-ReLU coefficients guarantee convexity of its continuation critic; the immediate quadratic action cost makes the one-period objective strongly convex. This supplies the assumption required for the convex action certificate rather than asserting that an arbitrary neural landscape has no bad attractors. The independent lifetime-cost calculation separately measures the remaining critic error. Main §3 and Supplement S.1–S.2 contain the proof and counterexample.

## R3-F8. Complete the exact proof and connect approximate evaluation to value

**Response.** The exact theorem now specifies the strong evaluation topology, including time derivatives and boundary traces. Its proof uses the common limiting value: monotonicity and precompactness give a unique value limit, and continuity yields `E(p)=E(I(p))`. Evaluation of the improved policy at that common value supplies the maximized HJB. The proof does not assert that consecutive limiting policies must coincide.

The new finite-horizon theorem links a computed policy to its target value under monotone Lipschitz operators. It distinguishes evaluation defects, feasible improvement gaps, terminal discrepancies, and differences between implemented and target operators. The policy-evaluation bound has coefficients epsilon+kappa; the optimized recursion has epsilon+delta+kappa; adding yields the policy-loss account with 2 epsilon+delta+2 kappa. A differential stopped-control corollary gives an analogous verification bound from uniform residual and boundary errors. The supplement also derives a conditional action-error bound under strong concavity.

These results are useful without claiming that a sampled training loss is a sup-norm bound. The paper states the coverage/regularity information needed to promote samples to such a bound. The constrained resource application obtains an independent finite-tree cost interval from convexity. The NDU application reports held-out errors and refinement rather than inventing the missing continuum bound. Main §§2–3 and Supplement S.1 provide complete arguments.

## R3-F9. Replace the static scalability calculation with a coupled dynamic experiment

**Response.** The new main experiment has interacting resource stocks, three decision dates, four correlated shock realizations per period, a common investment budget, and a nonseparable state cost. Budget constraints are active on many held-out states. We execute dimensions 4, 8, and 16, each at all three declared seeds. The primary comparison is with an independently optimized nonanticipative scenario tree that exploits the actual convex structure of this economy.

For each stored initial state, the learned policy is evaluated over the complete finite shock tree. Convex reference gaps bound its cost loss without using its critic as a performance score. All nine local development combinations met the stated 10^-3 held-out loss criterion; the authoritative committed rerun and its ledger determine the final reported results. The same trained actors are also evaluated without deployment improvement, isolating that mechanism. Main §5 and Supplement S.6 report the dimension and seed results, binding frequencies, gap tolerances, and timing definitions.

The timing comparison uses the same 10^-3 accuracy target on the same initial-state batch. A separate tighter reference run is used for auditing, not made the baseline timer to manufacture a neural speed advantage. The structure-exploiting reference is faster end to end in this experiment, and the manuscript says so. The result is verified constrained dynamic accuracy and a measured safeguard effect, not an unsupported universal speed or complexity claim. Structured stochastic LQR remains an additional regression test. The original static quadratic and historical sparse-grid arrays are preserved in the archive, not repurposed as current dynamic evidence.

## R3-F10. Distinguish arithmetic anchors from actual solutions

**Response.** Merton and Epstein–Zin are now actual separated homothetic-feature solves: the unknown value coefficient and bounded control parameters are learned, and independent analytical solutions are used afterward to calculate errors. The Epstein–Zin value transform is executed and checked over positive wealth. Supplement S.4 derives the fixed-policy branch, interior maximizer, admissible localized comparison class, and the selected policy's positive transversality decay. A separate finite-horizon terminal/sign architecture test is labeled exactly that, not a completed additional utility solve.

The game calculation is now a stochastic four-date capacity duopoly on its complete eight-state space, with actual investment decisions and maintenance costs. It computes state-dependent equilibrium policies from multiple initial profiles and independently solves each player's dynamic best response against the frozen rival policy at every subsequent date. The static Cournot distinction remains a derivative-graph negative control. Main §6 and Supplement S.5 also retain a carefully normalized many-firm theoretical extension with a conditional small-player deviation bound, without claiming an unexecuted competitive-limit experiment.

The ledger separates feature solves, finite-state equilibrium solutions, graph/domain tests, numerical references, and full neural runs. An unmeasured error is not reported as zero. Actual numerical zeros, such as a hard terminal identity or a checked absent gradient, follow an executed calculation or assertion.

## R3-F11. Locate the contribution relative to the closest methods

**Response.** The literature section now explicitly discusses continuous-time policy improvement, Kim and coauthors' 2025 version and their August 2026 revision, Lee and Kim's operator-learning policy iteration, SOC-MartNet, direct neural control approximation, and input-convex neural networks. The version-specific bibliographic entries preserve the different titles and author orders of the two Kim manuscripts. We do not claim priority for neural evaluation, actor factorization, mesh-free residuals, an implicit argmax, or convex neural inference.

The contribution is stated through the approximate-operator value account, economically explicit boundary specification, cumulative-adjustment result, checked improvement mechanisms, and independently evaluated constrained dynamic policies. Semilinearity is correctly tied to dependence on the highest derivatives, not simply to whether a control has a closed-form formula. A value-based BSDE is not equated categorically with a Pontryagin adjoint system. The cost discussion accounts for network size, loading rank, optimization, samples, probes, and target accuracy. Dimension cutoffs unsupported by evidence are not repeated as theorems. Main §§1, 3, 5, and 6 make these comparisons substantive rather than rhetorical.

## R3-F12. Repair source provenance and certification semantics

**Response.** The R4 branch preserves the pinned review and every historical manuscript. New source files are committed before authoritative execution. `validate.py` resolves the source commit and compares every executed Python file byte-for-byte with that commit. The final numerical ledger also records source-file SHA-256s, package versions, scientific payload digests, checkpoint/array hashes, and links to complete records. Timing and memory are separated from scientific digests, while complete file digests still identify all bytes.

Execution completion, evidence class, and tolerance status are distinct. Resource tolerances are computed from actual cost/gap records; NDU results are classified as diagnostics without a uniform continuum certificate. Every current table is generated from the executed JSON records. The standalone supplement points to the current R4 ledger. All declared neural seeds and the retained pilot are deposited. Checkpoint replay, full console logs, build logs, and the development disclosure are included.

The new manuscripts use the inherited Econometric Society class with author–year references, numbered mathematical statements, separate proofs, and tables linked to actual experiments. They are new files, not replacements for earlier manuscripts. The first-page heading identifies the revision rather than falsely claiming submission or editorial action. Build reports record actual page counts and unresolved-reference/overflow checks; rendered PDFs are inspected before delivery.

## Reading and reproduction

The main paper presents the argument and economic results. The supplement supplies the full proofs, admissibility and verification details, negative controls, algorithms, additional tables, and many-firm extension. The preservation map documents the disposition of every major earlier topic, including the archival figures. `replication/r4/README.md` and `run_all.sh` provide a complete rerun; `replay.py` checks saved policies without retraining. The final source and result commits are independently reachable from the revision branch.

This response does not presume the referee's next recommendation. It supplies a different and materially stronger object for that review: a mathematically specified economy, an executed method, independent policy performance, and explicit arguments connecting approximation errors to economic conclusions.
