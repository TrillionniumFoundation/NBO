# Response to the R13 referee report, with the inherited R12 findings

**Manuscript:** Neural Bellman Operators. **Revision:** R14, 22 September 2026.

**Review input:** `reviews/2026-09-22-econometrica-r13/referee_report.md` at `857bfeab28ca1b7a7f732edf180126f3ded6b451`, read together with the full R12 report at the same tree. The R13 report's reviewed target was `442ef9be75e620b53f923cdc476be50edaa64ca7`; the last actual manuscript was R12 at `4ff0404833a6d6773bcf7afab361013d732df686`.

We agree that a revision branch name cannot establish a scientific revision. R14 supplies a new manuscript, a current technical supplement, new proofs, actual neural weights, complete state-time neural audit records, a separately implemented economic primal and dual audit, new state–price and economic-resolution calculations, robustness experiments, fresh generation experiments, and explicit source/result identities. The original economic opportunity set, utility and stopping contract are unchanged. Earlier files and adverse results remain available, with a preservation crosswalk rather than a requirement to reproduce every previous line in the new paper.

The distinction between a completed calculation and an achieved accuracy is essential in the responses below. The full-domain neural certificate has now been executed, but its current bound is not 0.01. The sharp time-control/dual certificates are not assigned to that neural feedback. Likewise, the new classical experiment is not described as two matched-accuracy state-space baselines. These remaining empirical conditions are identified, rather than marked resolved by a change in terminology.

All paths below are relative to revisions/2026-09-22-r14/ unless stated otherwise. The canonical evidence entry point is root R14_REVIEW.md. R14 is published on revision/econometrica-r14-independent-state-audit-2026-09-22 and mirrored on revision/econometrica-r14-referee-copy-2026-09-22. Both remote branches descend from the exact latest review commit 857bfeab28ca1b7a7f732edf180126f3ded6b451; no existing review, revision, or main branch was force-updated.

## R13-F0 — No actual scientific delta in purported R13

**Change.** Root `ECTA_R14.tex/.pdf` and `SUPP_R14.tex/.pdf` are new. The main paper has 18 pages and the current technical supplement 11 pages. The source includes a complete neural residual/transport theorem and proof, a four-corner state–price theorem and proof, and explicit independent enclosure lemmas. New code and new numerical results accompany each executed claim. The original R13 aliases and review branches are not reused or overwritten.

**Evidence.** `paper/main.tex`, `paper/proofs.tex`, `paper/supplement.tex`, `replication/`, `results/`, this response, the canonical manifest, and the publication receipt. The local scientific commit and the local receipt commit are distinct from the actual remote R12/R13 commits. PDF and source identities are content-pinned.

**Status.** Resolved procedurally: an actual scientific revision exists and has been published on two new remote revision branches. Neither the prior review branches nor main were overwritten.

## R13-F1 — The sharp certificate is not a neural Bellman policy certificate

**Change.** We chose to retain and execute the neural-method chain rather than rename the paper as if the issue disappeared. A fresh two-hidden-layer, 48-unit tanh state-feedback actor and critic are trained on the original continuous stopped economy. The stored actor is evaluated directly by an independent interval program; it is not first replaced by polished deterministic outputs. Every network derivative, action maximization, residual and boundary term is enclosed on a complete state-time cover.

The sharp library and the new neural object are now separately named and tabulated. The former remains a feasible time-control library with an upper comparison over all adapted controls. No theorem or abstract assigns its 0.009969007711 bound to the neural network.

**Evidence.** Main Sections 3, 4 and 6; `replication/neural_economy.py`, `replication/neural_certificate.py`; `results/neural_run/`; all `results/neural_audit_*.json` and compressed cell records.

**Status.** The neural object and its full verification are real and complete. High-accuracy neural control remains unachieved: the finest neural bound is 23.493172462829243. The scientific identity issue is addressed by making the actual neural certificate falsifiable, not by claiming that this numerical accuracy satisfies the referee's full requirement.

## R13-F2 — Only one initial state was certified

**Change.** Two new domains are treated. The neural theorem is executed over the complete original state-time domain. Independently, a new affine-dual initial-state extension and a jointly concave budget-preserving lower construction produce a useful economic guarantee throughout `u in [1.98,2.02]`, `x in [1.24,1.26]`, and every `k in [0.5,8]` at initial time zero.

The latter uses exact four-vertex bounds, not sampled-state interpolation. Its uniform regret upper is **0.012095431553888848**. The consumption shift preserves terminal wealth and is verified inside the original action set for every policy. The dual upper is convex in initial state, while the exact covered lower functional is concave. Exact price intersections complete the state–price certificate.

**Evidence.** Main Section 5 and Appendix B; `replication/state_cost_certificate.py`; `results/state_cost/` (72 corner certificates, corner summary and exact envelope). The source explicitly distinguishes full-horizon expenditure of the lower functional from stopped expenditure of the central-state policies.

**Status.** A nondegenerate continuous initial-state certificate and a complete neural state-time audit are executed. The useful rectangle certificate is for an initial-state-indexed time-control family, not an accurate neural feedback at all initial times.

## R13-F3 — The neural cover/oracle bridge was an unexecuted interface

**Change.** The bridge is now executed on stored network weights. The finest cover has **16,384 interior cells**, **512 cells on each of four stopping faces**, an exact terminal trace, and no skipped or failed cells. The action oracle retains the entire original continuous action set, including uncertain-curvature branches. A componentwise `2^-24` output neighborhood is included in the action enclosure.

The final error budget is not hidden: two-sided trace **14.046215886665081**; integrated residual and improvement **9.446956576164158**; total time-zero bound **23.493172462829243**. All initial times are covered by a separately assembled conservative bound. Every cell's components are stored. The output-neighborhood statement is a mathematical error contract, not an unproved guarantee for a library transcendental function or an SDE discretization.

**Evidence.** Main Theorem 1, Table I and Table II; `results/neural_audit_0800_16_32_32.json` and `.cells.json.gz`; all earlier checkpoint/resolution rows are retained, including the unfavorable comparison between checkpoints.

**Status.** Executed. The requested methodological interface is operational on the original problem; its useful-accuracy and complete machine-deployment requirements remain distinct.

## R13-F4 — Same-code replay was called independent

**Change.** The new primal and dual implementations do not import any inherited certifier. They use a new outward arithmetic core with rational exponential/logarithm remainders, rationally isolated Gauss nodes and weights, and a different policy integration decomposition. The dual uses new cap/interior formulas and interval automatic source Hessians rather than the inherited manually differentiated expressions and weighted polynomial integrator. Supporting-plane and continuation primitives are rerun with complete interval covers. Expenditure inputs are independently recalculated as well.

A source-frozen clean replay recomputes all 18 nodes and confirms exact equality of **54 decisive fields** (lower endpoint, upper endpoint and expenditure interval at each node) and the exact rational price envelope. This replay is correctly called reproducibility of the new implementation. Its numerical independence is established by the distinct code and decomposition, not by the equality test itself.

**Evidence.** `replication/interval64.py`, `validated_gauss.py`, `independent_primal.py`, `independent_dual.py`, `exact_price_audit.py`; `results/independent_library/`, `results/clean_recheck/`, `results/clean_recheck_receipt.json`.

**Additional check.** A third closed-lognormal-moment implementation at 40 and 70 digits verifies source, affine coefficient and covariance against the independent intervals at three prices. These point-valued quadratures are explicitly diagnostic, not formal interval proofs: `results/high_precision/`.

**Status.** Independent numerical implementation executed for all decisive nodes. The underlying analytic dual theorem remains a shared, fully stated mathematical premise; no claim of independent formal verification is made.

## R13-F5 — The 0.01 threshold had only six micro-units of slack

**Change.** The independent calculation uses a finer dual cover and a substantially sharper direct original-utility policy enclosure. Its central-state continuum bound is **0.009969007710640541**, with about `3.10e-5` slack. More importantly, a full-library stress experiment perturbs every witness and simultaneously weakens primitive constants: source floor `-7.11`, coefficient bound `1.11`, doubled normal-tail allowances, and variance allowance multiplied by `1.1`. Initial deflator values are perturbed by `1e-6`, and reference drifts by alternating `+/-1e-6`, projected inward. All 18 certificates are recomputed.

The stressed continuum bound is **0.009970977449945498**, still below 0.01. The higher-precision, different-decomposition checks also pass. The original 0.009994024846927508 result remains recorded with its original scope.

**Evidence.** Main Section 7 and Table V; `results/robust_library/`, `results/high_precision/`, `results/independent_price_audit.json`, the inherited-envelope audit and the independent source/primitives files.

**Status.** The requested alternative robustness route is executed. We do not claim a bound below 0.009, immunity to all possible software defects, or proof from endpoint sensitivity alone.

## R13-F6 — Parameter-node refinement was not an accuracy frontier

**Change.** A new experiment changes actual policy richness on the unchanged economy at `k=2`. Policies with 16, 32 and 64 time intervals are freshly generated from fixed initial guesses; dual pilots are separately fitted; both sides are independently verified. Bounds are **0.009688057135165852**, **0.009669547904274768**, and **0.0096650730255341**. The paper also reports an actual neural-cover refinement for one frozen 800-step neural snapshot, plus checkpoint comparisons at fixed cover size.

**Evidence.** Main Section 8 and Table VI; `replication/fresh_time_frontier.py`, `results/fresh_frontier/`; neural Table I and its full data.

**Status.** Actual approximation/verification frontiers are now executed, not relabeled cost-node counts. The stronger requested progression to 0.005, 0.0025 and 0.001 is **not achieved**. The exact predicates are stored as false. The unchanged affine upper relaxation explains why quadrature/policy refinement alone need not eliminate the observed gap; it is not asserted to be an impossibility result for better methods.

## R13-F7 — End-to-end generation cost was absent

**Change.** The new neural run records all fresh training, updates, checkpoints and resource use; it uses no inherited weights. The new classical frontier records fresh policy generation, dual fitting and both verification stages. For the three classical cases, measured total case times are approximately 8.67, 8.54 and 8.77 seconds. Interpreter/import time is separately shell-timed. Each fit's attempts and optimizer diagnostics are retained. Hardware, package versions and memory measurements are supplied.

The historical library's approximately 103-second independent audit is explicitly verification-only, not the cost of its unobserved original training. Missing or interrupted historical generation costs are unknown, not zero. Overlapping local experiment clocks are not used to claim a matched-hardware speed ranking.

**Evidence.** `results/neural_run/resource_ledger.json`, `results/fresh_frontier/resource_ledger.json`, all stage records and `build_logs/`; `environment.json`; `replication/reproduce.py` joins the separately executed stages into a fresh-directory command.

**Status.** New-generation resource ledgers exist. A full historical cost reconstruction for every inherited proposal does not, and is not claimed.

## R13-F8 — Two strong classical same-problem baselines at matched accuracy

**Change.** We added a fresh direct time-control optimization and dual-fitting baseline on the original economy, rather than another external or reference-solvable model. It is independently certified and its actual approximation dimension and computation are reported.

**Status.** **Not fully addressed.** This is one classical feasible-policy/dual pipeline, not two independently implemented monotone HJB, semi-Lagrangian or controlled Markov-chain solvers at matched certified accuracy. The neural bound also does not reach the classical comparator's tolerance. The paper makes no neural-efficiency advantage claim and does not label this missing comparison as completed.

## R13-F9 — Frozen high-dimensional actions were confused with dynamic control

**Change.** Main Section 8 and the preservation map identify the retained result as a rank-one-coupled, frozen-jet continuous-action oracle. Its scalar aggregate reduction is retained. Neither a full 128-dimensional value surface nor a 128-state stochastic control certificate is attributed to it. The new full-domain dynamic certificate concerns the original two-state economy.

**Status.** Scope corrected without deleting the high-dimensional action result or its data.

## R13-F10 — External evidence did not establish superiority

**Change.** The unfavorable clipped-feedback comparisons and unstable seed-level rankings are explicitly retained in the introduction, comparison section and preservation map. Candidate quality, validity of a certificate and numerical efficiency versus alternatives are treated as separate claims. The old data remain unchanged.

**Status.** The invalid superiority inference is not used. General solver superiority remains unestablished rather than being inferred from certification success.

## R13-F11 — Affine cost continuation was model-specialized

**Change.** The cost theorem precisely requires a common policy set and affine objective dependence. In addition, a new coefficient-transport proposition applies to changes in drift, covariance, discount and running payoff on a common domain and action set. It uses verified residual differences and incurs the explicit `2d` transport allowance. This is proved without assuming common stopping times.

The transport is executed over intervals for the interest rate, risky drift, both volatility coefficients, discount and adjustment price using the actual stored neural witness. The bound is **23.53040781305452** at initial time zero. Its size is inherited from the coarse base neural certificate; it is not represented as a sharp changed-economy result.

**Evidence.** Main Proposition 1, Appendix A and Section 6; per-slab `d` fields in the full-domain audit; supplement's covariance/derivative details.

**Status.** Scope is precise, and a broader constructive transport mechanism has an actual execution. No unsupported general parameter-continuation claim remains.

## R13-F12 — Policy regret did not resolve all comparative statics

**Change.** A separate exact calculation now identifies strict-loss regions and conservative relative-resolution regions. It combines value intervals with the analytical expenditure Lipschitz bound and preserves known weak monotonicity. Main Tables VII and VIII contrast a resolved large price change with unresolved strict loss for nearby prices. All active policy regions, exact endpoint fractions, widths and control summaries are also recorded.

**Evidence.** Main Section 9, Appendix C and supplement's policy-region table; `results/independent_price_audit.json` fields `economic_resolution_regions`, `welfare_queries` and `active_policy_regions`.

**Status.** Executed. A 0.01 policy guarantee is no longer used as an assertion that every local welfare effect is relatively resolved.

## R13-F13 — The paper was an accumulation of separate components

**Change.** The new main paper is organized around the constructive stopped verification theorem, the original economy, the actual neural execution, and its independently sharp economic comparison objects. The state–price theorem links the latter to a continuous state region. Fresh accuracy/resource experiments and economic identification follow that chain. Complete current proofs are in the main appendices and technical supplement.

Historical extensions and studies are preserved at their original paths, not concatenated into the current supplement. The old “every inherited line must survive” acceptance rule is not applied to the new manuscript. A content-preservation map explains where recursive utility, sophisticated selves, games, trace identities, prior counterexamples and unfavorable experiments remain available.

**Status.** Manuscript architecture substantially rewritten without changing the model or erasing substantive history. The remaining neural-accuracy and matched-baseline conditions are still scientific limitations of this chain, not editorial matters declared solved by organization alone.

## R13-F14 — Canonical metadata was contradictory

**Change.** The previous root index is archived byte-for-byte. A single new root index points to R14's main PDF, source, supplement, response, exact manifest and evidence. Remote review-input identities, local reconstructed-base identity, scientific source/result/build identity and the receipt identity are not conflated. Source/result/PDF hashes are included. No field labels the uncreated remote branch as published.

**Evidence.** Root `REVISION_INDEX.md`, `R14_REVIEW.md`; `canonical_manifest.json`, `publication_receipt.json`, `preservation_manifest.json`; the downloadable delivery manifest and patch.

**Status.** Local canonical identity is unambiguous. Remote publication remains explicitly separate.

## Additional inherited R12 findings

**R12-F13 — Same-architecture exact-reference accuracy suite.** The new economic actor and critic are genuinely width-48 tanh networks, but the present work has not rerun an exact-solvable LQ suite using precisely this actor/critic training adapter. The older gain-output experiment remains labeled as such and preserved. This condition is not marked closed by architectural similarity alone.

**R12-F15 — Generality and novelty.** The main verification and coefficient-transport assumptions describe a recognizable class of bounded stopped controlled diffusions, rather than this calibration alone. The new transport box is executed. Classical Itô comparison, policy iteration, convexity of a supremum of affine functions, and dual bounding are credited as existing principles; the constructive neural and state–price implementations are identified as the contribution. A separate, nontrivial economic application beyond this model has not been added.

**R12-F16 and F17 — Editorial preservation and focus.** All 1,830 archived baseline files were checked against the source archive before editing. Except for the deliberately replaced navigation index (itself preserved in `archive/`), historical files remain unchanged. The new supplement contains current proof details and a preservation map, not copies of all old manuscripts. Thus substantive content is neither arbitrarily deleted nor forced into the main narrative as obsolete prose.

**R12-F18 — Upstream enclosure validity.** The second primal/dual implementation, independent expenditure calculation, root-certified quadrature, full primitive covers, source-frozen replay and closed-normal high-precision cross-check all address the upstream stack. The arithmetic and analytic trust assumptions are explicit. Exact envelope arithmetic is not used as a substitute for validating its inputs.

## Reviewable result and remaining conditions

R14 is a real, data-bearing revision. It completes the missing whole-domain neural *execution*, independently audits the sharp original-economy library, tests all nodes under perturbed witnesses and larger allowances, and supplies a nontrivial continuous state–price guarantee and exact economic-resolution map. It also supplies a fresh actual-policy-richness frontier and explicit resource accounting.

It does **not** establish useful-accuracy whole-domain neural control, the requested finer flagship tolerance sequence, two matched-accuracy classical state-space baselines, or the identical-pipeline exact-reference suite. These conditions remain visible to the next referee. A successful build or a valid but large neural bound is not represented as their closure. Remote publication is complete; it does not alter those substantive unresolved conditions.
