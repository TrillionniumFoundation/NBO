# External Referee Report — R44

**Venue perspective:** Econometrica-level numerical and computational methods  
**Intended/inherited article:** *Certified Bellman Operators for Costly Policy Revision*  
**Repository:** `TrillionniumFoundation/NBO`  
**Reviewed branch:** `revision/econometrica-r44-global-bellman-envelopes-2026-09-25`  
**Reviewed HEAD:** `71a002bb5a47b825093593d2ea8fafca50d776e7`  
**Prior external report addressed by the protocol:** `reviews/2026-09-25-econometrica-r43/referee_report.md` at `554cae0c865498cf3fd6def18a80b75a1ee1abb3`  
**Review branch:** `review/econometrica-r44-numerical-methods-2026-09-25-71a002b`  
**Date:** 2026-09-25

## 1. Recommendation

**Reject. The current remote object is also not a complete reviewable manuscript revision.**

The first problem is procedural but decisive. The reviewed HEAD is explicitly a staging commit entitled `revision(r44): stage full Econometrica manuscript and response source package (1/3)`. It adds only `revisions/2026-09-25-r44/transport/publication.00.b64`. The branch does not contain `R44_REVIEW.md`, `ECTA_R44.tex` or `ECTA_R44.pdf`, `SUPP_R44`, `RESPONSE_R44`, `COMPUTATION_R44`, a materialized `paper/` directory, a current manuscript source tree, or a publication manifest tying a compiled article to the numerical objects. The source exists only as opaque base64 transport chunks, while the publication transport contains only the first advertised chunk. A referee should not be required to reconstruct a private staging format in order to discover what theorem statements, tables, qualifications, and claims are actually being submitted.

The visible numerical package is sufficiently extensive to permit a substantive assessment, and I have reviewed it rather than stopping at the staging defect. R44 adds two internally verified global-search formulations—an enhanced Bellman-envelope/simplex-RLT tree and an aggregate-product tree—plus a PySCIPOpt comparison on twelve predeclared finite-state environments and four tie-stress environments. It also retains exact rational tree certificates, independent reconstruction, source/model hashes, property tests, and failed/time-capped runs. This is serious computational work.

The results nevertheless do not support an Econometrica-level numerical-methods claim. Under the registered absolute gap target of \(10^{-3}\), the Bellman-envelope tree succeeds in only 4 of 12 primary environments and the aggregate-product tree succeeds in only 5 of 12. Most medium and large cases terminate at the 120-second cap. The largest instances explore only 7–13 nodes because each relaxation is already expensive. In several of those rows, branching produces essentially no improvement over the root bound. The enhanced Bellman formulation is not uniformly stronger: it dominates on some maintenance, inventory, and queue cases, while the aggregate formulation is dramatically stronger on other large cases. The package therefore demonstrates that different formulations can be useful in a portfolio; it does not establish a consistently effective Bellman-envelope algorithm.

The SCIP comparison is also not a fully verified same-object comparison. SCIP often reports substantially stronger native floating-point lower bounds, including native intervals that meet the target where the two internal certified trees do not. However, the repository labels those lower bounds “solver-reported floating-point; not independently certified.” Only the candidate upper policy is checked. The displayed “shared certified interval” then reuses the best internal rational lower bound rather than certifying SCIP's own lower bound. Thus the strongest evidence favoring the external solver is intentionally excluded from the certified comparison, while the paper cannot legitimately count SCIP's native target hits as verified results. This is an important verification gap, not a cosmetic labeling issue.

The exact tree verifier appears careful, and I did not find an obvious contradiction in the inspected Bellman recursions, McCormick/RLT construction, residual lower-bound calculation, tree-cover verification, or policy feasibility checks. The rejection is therefore not an allegation of hidden arithmetic error. It follows from an incomplete submission object, weak and unstable practical performance, a comparison whose strongest external lower bounds are uncertified, continued reliance on synthetic exact-known finite models, and the absence of a demonstrated solution to the original action-dependent continuous-state problem that has motivated the paper throughout its revision history.

## 2. What is actually present on the reviewed branch

The R44 directory contains:

- a frozen `PROTOCOL.json`;
- sixteen finite model files covering maintenance, inventory, queue, and tie families;
- implementation sources for the two internal trees, a local proposal, SCIP adapter, diagnostics, and independent verifier;
- per-case result files for Bellman, aggregate, and SCIP runs;
- compressed proof objects;
- source-transport verification records;
- mutation and finite property tests.

The protocol fixes an absolute target of \(10^{-3}\), 120 seconds and 2,047 nodes per method, 15 seconds per node LP, five seconds for the local proposal, and one thread. The twelve primary cases use the following size sequence in each of three designed families:

| Index | States | Horizon | Actions | Discount | Operating allowance |
|---:|---:|---:|---:|---:|---:|
| 0 | 4 | 4 | 3 | 0.90 | 0.01 |
| 1 | 8 | 8 | 3 | 0.95 | 0.01 |
| 2 | 8 | 16 | 4 | 0.95 | 0.005 |
| 3 | 16 | 32 | 4 | 0.95 | 0.001 |

The package records all sixteen cases as completed and reports no collection errors. That establishes that the experiment ran. It does not establish that the optimization target was reached, nor does it replace a manuscript explaining theorems and claims.

The reviewed branch does **not** contain a materialized R44 article or response. Consequently, I cannot verify whether the intended manuscript accurately states the target-hit counts, distinguishes native SCIP and certified bounds, reports zero-cost rows separately, or places the finite experiments within the correct scope. This missing scientific interface is itself a blocking defect.

## 3. Genuine strengths of the visible computational package

The negative recommendation should not obscure several strengths.

### 3.1 The target policy class is coherent

The implementation continues to solve a common randomized Markov problem rather than independent restart-specific problems. One probability vector is attached to each date and state. The all-restart operating constraints and the initial-distribution implementation objective remain distinct.

### 3.2 The lower bounds are proof-producing

Floating LP output is used only as a proposal. Equality and inequality multipliers are rounded to a dyadic grid, and a rational residual calculation produces a valid lower bound over every probability box. No LP infeasibility flag is used to discard a box. The final proof object includes the binary cover, every leaf bound, and a feasible common policy.

### 3.3 The independent verifier is meaningful

`verify_tree.py` imports neither the constructor nor the optimizer. It reconstructs the primitive model, operating-optimal values, regret and savings coordinates, tie-safe support transforms, rectangular bounds, the node LP contract, every rational residual, every split, the complete binary cover, and the deployed policy's all-restart constraints. It checks that no node is omitted or unreachable and recomputes the global minimum leaf bound.

### 3.4 Failures and caps are retained

The package does not delete time-capped cases, node-capped tie cases, missing primal/dual proposals, or rows that fail the target. This is good scientific practice.

### 3.5 The protocol covers more than one synthetic family

Maintenance, inventory, and queue dynamics are all represented, and the action count rises to four in the larger rows. This is broader than a single maintenance generator, although all three remain designed known-model families generated within the same codebase.

These strengths make the visible package credible as a computational experiment. They do not cure the blocking findings below.

## 4. Blocking scientific findings

### R44-F1 — The submitted R44 object is incomplete and not reviewable as a manuscript

The HEAD is explicitly `(1/3)` of a staging process. There is no materialized R44 article, supplement, response, computation report, review index, or compiled PDF. The only publication transport object is `publication.00.b64`. The three source chunks may reconstruct code or prose under an unpublished transport convention, but the repository tree does not expose a normal scientific source package. The current branch therefore fails the most basic requirement for peer review: a stable, human-readable manuscript whose claims can be compared with its evidence.

This is not a complaint about filenames. The referee cannot determine from the branch:

- the exact theorem statements claimed in R44;
- the relation of the Bellman-envelope tree to the inherited R43 theory;
- which numerical rows are in the abstract or conclusion;
- how the authors characterize SCIP's uncertified lower bounds;
- whether the original thirty open randomized intervals are still acknowledged;
- whether the incomplete publication transport was ever compiled successfully.

**Required correction:** materialize the complete article, supplement, response, computation report, generated tables, build logs, publication manifest, and a human-readable review index on one final commit. The review object must not depend on decoding base64 staging chunks.

### R44-F2 — The protocol's registered target is missed in most primary cases

For the twelve primary environments, the certified internal results are:

- **Bellman-envelope tree:** target met in 4 of 12 cases;
- **Aggregate-product tree:** target met in 5 of 12 cases.

The Bellman successes are `maintenance0`, `inventory0`, `queue0`, and `queue1`. The aggregate successes are `maintenance0`, `inventory0`, `queue0`, `queue1`, and `queue3`. Every other primary row stops at the time cap.

This is not a high closure rate for a predeclared numerical-method evaluation. One of the exact rows, `inventory0`, is a zero-cost case and therefore does not demonstrate difficult constrained optimization. The short `maintenance0` and `queue0` rows close at the root. The evidence for nontrivial global search is largely `queue1`, where 49 Bellman nodes or 153 aggregate nodes are needed to move just below the \(10^{-3}\) threshold.

The paper should not summarize this experiment as general “completion” of the predeclared suite. The scientifically relevant statement is that most medium and large positive-cost rows remain open under the registered budget.

**Required correction:** report target attainment by method and family in the abstract and main results, separate zero-cost/root-exact rows, and provide a prospective suite on which a substantial majority of nontrivial cases actually reaches the declared target.

### R44-F3 — The Bellman-envelope formulation does not dominate the aggregate formulation

The new branch name emphasizes “global Bellman envelopes,” but the evidence does not establish a stable advantage.

Examples where Bellman is stronger include:

- `maintenance1`: gap 0.00716 versus aggregate 0.02217;
- `maintenance2`: gap 0.00872 versus aggregate 0.02551;
- `inventory2`: gap 0.01419 versus aggregate 0.03488;
- `queue2`: gap 0.00115 versus aggregate 0.00499.

Examples where aggregate is much stronger include:

- `maintenance3`: gap 0.11501 versus Bellman 0.72857;
- `inventory3`: gap 0.00477 versus Bellman 0.06400;
- `queue3`: aggregate closes at the root with gap 0.000694, while Bellman times out with gap 0.03216.

The strongest formulation changes by model and size. This is not a defect in using a portfolio, but it undermines a method claim centered on Bellman envelopes. The package does not provide a structural classifier predicting which formulation will be strong, an adaptive strategy that selects or intersects them efficiently, or an ablation isolating the value of support envelopes, explicit reference products, savings cones, and rectangular propagation.

**Required correction:** frame the algorithm as a certified formulation portfolio unless a genuine dominance or selection theorem is established. Report best-of-portfolio intervals separately from per-formulation intervals and quantify the incremental cost and benefit of every strengthening.

### R44-F4 — Branching is often computationally irrelevant on the hard cases

The complete tree is theoretically important, but its executed contribution is frequently negligible.

For `maintenance3`:

- Bellman root gap: 0.7285670470;
- Bellman final gap after 7 nodes: 0.7285670470;
- aggregate root gap: 0.1150131202;
- aggregate final gap after 13 nodes: 0.1150112628.

For `inventory3`:

- Bellman root and final gap: approximately 0.0640000000 after 7 nodes;
- aggregate root gap: 0.005122994;
- aggregate final gap: 0.004768268 after 13 nodes.

For `queue3`, the useful aggregate certificate is already obtained at the root. The Bellman tree explores only 7 nodes before timing out and does not improve its 0.032158 root gap.

Thus the hard-case evidence is primarily evidence about root relaxation quality, not the practical effectiveness of the global tree. Formal eventual completeness does not compensate for a search that cannot process enough nodes for branching to matter.

**Required correction:** provide gap-versus-node and gap-versus-time curves on cases where branching materially improves the bound; analyze branching scores and strong-branch alternatives; and demonstrate closure that is impossible at the root but achieved by the actual tree within a meaningful budget.

### R44-F5 — The SCIP comparison does not certify SCIP's strongest lower bounds

The SCIP adapter reports a native lower bound and a verified candidate upper policy. The lower bound is explicitly labeled “solver-reported floating-point; not independently certified.” The package then reports a “shared certified interval” using an internal rational lower bound.

This distinction changes the conclusions. For example:

- `maintenance1`: SCIP native gap 0.000832, which meets the target; shared certified gap 0.007157, which does not;
- `maintenance2`: SCIP native gap 0.000835, which meets the target; shared certified gap 0.008723, which does not;
- `maintenance3`: SCIP native gap about 0.0520; shared certified gap about 0.1139.

The external solver may be substantially better than the internal methods, but R44 has not converted that advantage into a certificate. Conversely, it would be invalid to count SCIP's native target hits as verified successes. A “same Bellman support and cone cuts” model does not make a floating global dual bound exact.

This is the central comparator problem. The paper cannot simultaneously market a verified comparison and leave the strongest comparator lower bound outside the verification boundary.

**Required correction:** post-certify SCIP's global lower bound. Possible routes include exact reconstruction of the root and node relaxations, rational validation of dual bounds, proof logging, interval-certified branch-and-bound, or a solver that exports checkable certificates. Until then, present SCIP only as a numerical proposal/diagnostic, not as an equal verified method.

### R44-F6 — The complete-search theorem remains practically exponential

The probability-box tree has no polynomial complexity guarantee. At \(n=16\), \(T=32\), and \(m=4\), there are \(nT(m-1)=1{,}536\) nonreference probability coordinates. The registered node cap of 2,047 is negligible relative to the combinatorial tree needed to refine such a space.

The computational symptoms are already severe:

- `maintenance3` Bellman LP: 17,952 variables, no usable primal/dual at the root time allocation, seven nodes in about 128 seconds;
- `maintenance3` aggregate LP: 8,512 variables, thirteen nodes in about 124 seconds;
- process high-water memory reaches roughly 400–450 MiB on large rows;
- proof objects reach several megabytes for only a handful of nodes.

Formal completeness under unlimited refinement is therefore still closer to decidability than to a practically useful numerical method. The paper needs a complexity story beyond “the full binary tree eventually covers the probability box.”

**Required correction:** derive problem-dependent convergence rates for the actual tree, quantify node growth in \(n,T,m,arepsilon\), and demonstrate nontrivial closure on instances where thousands—not seven—of informative nodes can be processed. Report proof-size and verification-time scaling as part of the algorithmic complexity.

### R44-F7 — Small relative gaps obscure failure of the registered absolute target

Several rows have visually small relative gaps but miss the predeclared absolute target by large factors. Examples include:

- `inventory3` aggregate: relative gap about 0.0306%, absolute gap 0.00477;
- `maintenance3` aggregate: relative gap about 0.703%, absolute gap 0.1150;
- `queue2` Bellman: relative gap about 0.0152%, absolute gap 0.001151.

Relative width can be economically useful, but it was not the registered stopping target. Switching emphasis from absolute to relative gap after the run would be outcome-dependent reporting. Both statistics should be shown, with the protocol target governing success.

**Required correction:** preserve the absolute target as the primary success criterion and report relative widths only as secondary diagnostics. Justify the economic scale of \(10^{-3}\) before evaluation rather than interpreting whichever metric looks favorable ex post.

### R44-F8 — Exact and near operating ties remain a serious failure mode

The R43 small-allowance contraction relies on a positive minimum action disadvantage. R44 correctly includes tie environments where this assumption fails or becomes weak. The generic trees remain sound, but the numerical results are poor.

Representative rows are:

- exact tie `tie0`: Bellman gap 0.004995 after 879 nodes and 120 seconds; aggregate gap 0.160574 at the 2,047-node cap;
- `tie3`: Bellman gap 0.134494 after 1,053 nodes; aggregate gap 1.360331 at the node cap.

The tie-safe support transform avoids an invalid certificate, which is valuable. It does not provide a practically satisfactory replacement for the inverse-gap geometry. The method's strongest rate therefore applies where the difficult degeneracy is absent, while the generic fallback is weak precisely at the degeneracy.

**Required correction:** develop tie-aware structural reductions or active-set aggregation that exploit multiple operating-optimal actions, and demonstrate useful certified performance as the action gap tends to zero. Merely falling back to a sound but very loose tree is not enough.

### R44-F9 — The scaling diagnostic is too narrow to establish algorithmic scaling

The additional scaling study fixes \(n=3\), \(T=8\), \(m=3\), and \(eta=0.95\), varies only the operating allowance, and solves scaled/unscaled root relaxations for three synthetic families. This can illustrate a fixed-model small-\(arepsilon\) phenomenon. It does not measure scaling in state count, horizon, action count, dimension, or tree depth.

Moreover, a small root width as \(arepsilon\) becomes tiny can be economically uninformative if the feasible policy is forced arbitrarily close to the operating-optimal reference. The paper must distinguish a numerically easy small-allowance limit from a generally effective constrained revision method.

**Required correction:** add controlled scaling in \(n,T,m,eta\), minimum action gap, transition sensitivity, and revision-cost heterogeneity. Report both root-relaxation scaling and full-search scaling, including cases with nontrivial intervention mass.

### R44-F10 — The experiments still use exact known finite operating models

All new primary models are finite, rational, fully known, and generated by the repository. The operating value and reference action are computed exactly. The package therefore does not test the inherited witness-driven theory where operating approximation is itself difficult.

This matters because the motivating numerical setting is not merely nonconvex policy search. It is simultaneous certification of operating performance and implementation cost in dynamic models where the operating Bellman solution may be approximate. R44 removes that difficulty from the experiment.

**Required correction:** execute the method with a genuinely approximate operating oracle, propagate independently verified witness errors through the global search, and show that the final interval remains informative. Exact finite dynamic programming should be presented as a controlled reference experiment, not broad evidence for approximate dynamic models.

### R44-F11 — The three economic families are synthetic variants within one generator ecosystem

The maintenance family is inherited from the R43 random finite generator. Inventory and queue models add recognizable labels, but their parameters remain random designed primitives with uniform initial laws and normalized costs. They are not calibrated inventory or queueing applications, do not include estimation uncertainty, and do not generate an economic conclusion beyond solver performance.

The experiment is broader than one family, but not external validation. All models, algorithms, proof formats, and verifiers are authored in the same repository and evaluated on the same execution platform. The prospective hash freeze reduces tuning risk; it does not make the suite representative of economic dynamic programs.

**Required correction:** include at least one independently specified economic application with disciplined primitives, meaningful units, and a decision conclusion that changes because of the certificate. Otherwise narrow the journal claim to verified global optimization for a synthetic finite benchmark class.

### R44-F12 — R44 does not advance the original continuous-state maintenance problem

The prior report emphasized that all thirty positive-cost randomized intervals in the original continuous-state maintenance cohort remained open. The visible R44 package contains no new result for that cohort. It replaces the motivating problem with twelve new finite-state environments.

Finite-state progress is legitimate. It should not be presented as resolving the main continuous atomic problem. The exact affine-shock condition process still lacks a convergent certified scheme for the common randomized optimum, and the nonlinear two-state intervals remain inherited rather than improved.

**Required correction:** either solve or materially tighten the original positive-cost randomized intervals, or remove that model from the central motivation and title. A paper cannot repeatedly motivate a method with one class while validating each revision on a different tractable subclass.

### R44-F13 — The verifier proves finite arithmetic, not the absent analytic manuscript

The independent tree checker is a major strength. The property test additionally reports 145 transformed policies and 19,720 support inequalities, including an exact operating tie. The record correctly labels these as finite property tests rather than a machine-checked general theorem.

Because the R44 manuscript is absent, there is no way to compare the implementation contract with the exact analytic claims the authors intend to publish. A common specification error can be shared by constructor and verifier, and finite tests do not prove a general support-envelope theorem.

**Required correction:** materialize the theorem statements and provide a theorem-to-code contract table. Identify which assumptions and inequalities are machine checked, which are verified only for finite models, and which remain conventional mathematical proofs.

### R44-F14 — The publication and provenance workflow is unfinished and unnecessarily brittle

The branch stores scientific source through manually corrected base64 transport chunks. `SOURCE_TRANSPORT_VERIFICATION.json` records several byte-level corrections before experiments. The final HEAD then adds only the first publication chunk. There is no ordinary source snapshot, no complete publication transport, no build record, and no final manifest.

Even when hashes match, this workflow is unnecessarily opaque. A journal referee should inspect normal TeX and source files, not trust a custom restoration path whose output is absent from the reviewed tree.

**Required correction:** commit the restored source files directly, compile the final documents, record the exact source and result hashes in a publication manifest, and make the final Git commit—not an external transport convention—the authoritative review object.

### R44-F15 — The numerical contribution is a portfolio of classical relaxations, and novelty remains unclear

The visible code combines:

- Bellman regret/savings coordinates;
- finite support-price envelopes;
- McCormick products and RLT equalities;
- box branch-and-bound;
- LP-based local proposals;
- SCIP with related cuts;
- exact residual postprocessing.

The proof-producing integration is valuable. Most optimization ingredients are classical. The experiment does not establish that the Bellman-envelope construction is uniformly stronger than aggregate products or SCIP, nor that it solves cases beyond the reach of standard global formulations. On some hard rows SCIP's native floating lower bound is strongest; on others aggregate products dominate Bellman envelopes.

**Required correction:** state the precise theorem-level novelty and demonstrate a problem class where it creates a decisive, reproducible advantage over strong classical formulations after equal verification requirements are imposed.

### R44-F16 — The current object is too fragmented for Econometrica

Across recent revisions, the project now contains deterministic outer bounds, randomized repair, finite complete search, exogenous exact aggregation, density reset transfer, observable fibers, regret-scaled roots, Bellman envelopes, aggregate products, local programs, nonlinear boxes, and multiple verification systems. R44 adds yet another layer but does not supply the manuscript that would unify or prune them.

The repository demonstrates sustained technical effort. It does not yet present one coherent Econometrica article with a central theorem, a practically decisive algorithm, and a substantive economic application.

**Required correction:** substantially narrow the paper. A viable version should center either:

1. a finite verified global-optimization method with convincing comparative performance;
2. a continuous-state convergence theorem demonstrated on a nontrivial application; or
3. an economic policy-revision application whose conclusion depends on certified randomization.

The current omnibus trajectory is not an acceptable substitute for depth in one of these directions.

## 5. Minimum requirements for a future reviewable submission

A future submission should, at minimum:

1. materialize a complete, compiled manuscript and response on one final commit;
2. certify the strongest comparator lower bounds rather than borrowing internal bounds for a “shared” interval;
3. report the predeclared success rate prominently: 4/12 Bellman and 5/12 aggregate on the current suite;
4. separate zero-cost/root-exact rows from nontrivial search successes;
5. demonstrate an actual branching benefit on difficult three- and four-action cases;
6. provide a structural rule or adaptive portfolio for choosing Bellman versus aggregate formulations;
7. show scaling in states, horizon, actions, discounting, action gaps, and proof size;
8. test a difficult approximate operating oracle;
9. address operating ties with more than a loose generic fallback;
10. either advance the original continuous-state randomized problem or stop using it as the central motivation;
11. include an external economic application or sharply narrow the journal claim;
12. provide a theorem-to-code verification map and a complete publication manifest.

## 6. Additional technical and presentation comments

1. The main table should include absolute gap, relative gap, target status, stop reason, nodes, LP time, total construction time, verification time, memory, and proof bytes for every method.
2. “Target met” must always refer to the registered **absolute** target, not a favorable relative gap.
3. SCIP's `native_lower`, the internal certified lower, and the verified candidate upper must be shown in separate columns.
4. Do not label a SCIP row “verified” merely because its candidate policy is verified.
5. Report the best certified portfolio interval obtained by intersecting all independently valid internal lower bounds and feasible upper policies, but retain the individual methods as predeclared.
6. Explain why support prices are fixed at the chosen powers of two and test sensitivity to that grid without using the evaluation suite for retuning.
7. Quantify how much each of the following contributes at the root: rectangular propagation, savings cones, support envelopes, reference-product RLT equalities, and local proposal.
8. The branch coordinate heuristic should be compared with widest-coordinate, strong branching, pseudo-cost branching, and reliability branching.
9. Report how often LP proposals are unavailable and how much the midpoint/lower-corner fallback degrades the upper policy.
10. Distinguish solver time from rational residual construction, tree serialization, and independent verification.
11. Include proof-size versus node-count plots. Multi-megabyte proofs at fewer than twenty nodes raise obvious scaling concerns.
12. Report whether verification memory is lower or higher than construction memory.
13. For every time-capped case, show the last ten bound improvements, not only sparse traces.
14. For `maintenance3`, explain why the Bellman root has no usable primal or dual while aggregate does.
15. For `queue3`, explain structurally why aggregate closes at the root and Bellman remains two orders of magnitude wider.
16. For exact ties, report the dimension of the operating-optimal action face and exploit it rather than selecting the lowest-index maximizer as the sole reference.
17. The finite property tests should include random malformed covers, duplicated leaves, omitted subtrees, and inconsistent inherited lower bounds.
18. Mutation tests should separately attack objective coefficients, support-envelope directions, RLT equalities, branch cuts, and policy feasibility.
19. The exact verifier should check protocol/model hashes directly in every invocation rather than relying only on surrounding collection scripts.
20. A zero lower bound should be identified as a fallback certificate, not interpreted as evidence about the true optimum.
21. The inventory and queue primitives need an economic interpretation beyond labels assigned to generated transition matrices.
22. Uniform initial laws should be justified or varied prospectively.
23. Add nonuniform and atomic initial distributions to test the distinction between all-restart feasibility and initial objective weighting.
24. The algorithm currently assumes one operating constraint. Discuss multiple constraints and whether the repair remains practical.
25. Report sensitivity to implementation-cost scale; an absolute gap target is meaningless without a scale justification.
26. Explain whether the local five-second proposal budget is included in each method's 120-second budget in every path and verify that accounting in the result schema.
27. The source transport corrections should be removed from the final review object; corrected source should simply be committed and hashed.
28. A final R44 response must address every R43 blocking finding rather than relying on protocol metadata.
29. The abstract should state that the original thirty positive-cost randomized intervals remain open unless R44 actually changes that fact.
30. The conclusion should distinguish finite arithmetic correctness, asymptotic completeness, and practical closure under the registered budget.

## 7. Final editorial assessment

R44 contains a credible proof-producing finite optimization experiment and a strong independent checker. It also provides useful evidence that Bellman-envelope and aggregate-product relaxations have sharply different strengths across model families. Those are worthwhile research observations.

The submission before the referee, however, is an unfinished staging branch rather than a manuscript. Even treating the numerical package as the intended paper, most primary cases miss the predeclared target, the hardest searches barely branch, formulation superiority reverses across cases, the strongest SCIP lower bounds are not certified, exact and near ties remain difficult, and the original continuous-state randomized problem is untouched. The new suite remains synthetic and uses exact known finite operating models.

**Recommendation: Reject.**