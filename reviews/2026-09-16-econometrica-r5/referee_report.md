# Referee report: Neural Bellman Operators — revision R5

**Review date:** 16 September 2026  
**Manuscript:** *Neural Bellman Operators*, Qian QI  
**Reviewed branch:** `revision/econometrica-r5-2026-09-16`  
**Reviewed commit:** `c9f71077cf6a339573ac07be55d7660797bcf6ea`  
**Reviewed Git tree:** `e57eb654bd1c4959be7d96f04327778f7cbbde05`  
**Previous report:** R4 report at `11082cc5054e91d3b2ac27826705f374ca74bfae`  
**Recommendation:** **Reject in its present form.**

This is an owner-commissioned, external-style advisory assessment using the standards of an Econometrica referee. It is not a referee appointment, submission record, or editorial decision by the journal. The recommendation concerns the submitted R5, not the possibility of developing the research further.

## Summary assessment

R5 is materially better than R4. The author has implemented a genuine finite-model welfare certificate, repaired the previously profitable deviations, correctly distinguished adjustment effort from its coefficient-weighted charge, measured rather than merely extrapolated query workloads, and corrected the dynamic-game verification to cover every date. The current text is unusually explicit about which computations are finite-state references, which are trained approximations, and which claims have not been transferred to a diffusion. These improvements deserve credit. I do not recommend rejection by simply repeating objections that the revision has resolved.

The remaining problem is more fundamental: the revision has not established a sufficiently important incremental economic or computational contribution. Its strongest new certificate is obtained by exact finite-state policy construction and established reward-transfer geometry. Its principal resource-workload advantage disappears when the conventional comparator is allowed to reuse the invariant structure of the same quadratic program. Moreover, a new reviewer ablation constructs policies using only the common action mesh and still attains the manuscript's uniform welfare target against the original, neural-inclusive finite problem. These are executable findings, not conjectures about what a better baseline might accomplish.

The distinction is important. R5 largely repairs **validity within its declared numerical targets**, but this does not establish **necessity of the learned representation, a new transfer principle, or a substantial economic discovery**. I would not recommend another revision whose main content is more bookkeeping, more regression tests, or narrower wording. A successful further paper would need new substantive evidence or theory addressing the four issues below.

## Scope and evidence

I read the 27-page main manuscript, the 21-page supplement, the R4 report, the R5 response, the source and generated tables for the new sections, and the relevant current and inherited replication programs. The PDF theorem and computation pages were also inspected visually. The authoritative reading order is the R5 revision index, not `main`, `ECTA.tex`, or an older supplement. [M0], [H1], [H2]

The source and execution bundle was obtained from GitHub Actions run `35050137046`, artifact `10428761839`. Its source anchor is `84a4f2ba53d301dbd08af96bc3f7018b43acb0ec`; the final evidence commit is the reviewed commit above. Reconstructing the Git tree from the extracted original files, including executable modes and excluding only reviewer additions and generated Python caches, produced **exactly the live reviewed tree hash**. Thus the local tests below use the deposited R5, not an approximate reconstruction of it.

The accompanying scripts execute two kinds of checks. Independently constructed diagnostics include the reusable scenario-tree QP, its algebra/gradient checks, and piecewise-affine interval maximizations. Re-executions of author routines include fixed-policy feature evaluation, the sign-certificate implementation, the all-nine resource validator, and the all-date game validator. Those latter checks corroborate execution; they are not mislabeled as independently implemented algorithms. Complete neural retraining of the stopped preference model and a fresh full historical hyperparameter sweep were not performed.

## 1. What is now established

**Finite-model policy reuse.** The target really does contain 1,565 common actions—the union of both old meshes—plus three frozen neural proposals at each node. There are 1,617 states, eight decision dates, and 47 contract anchors. Re-evaluating all anchor policies gives a maximum feature discrepancy of `8.881784197001252e-16`. Checking the original full menu gives a maximum anchor Bellman gain of `4.440892098500626e-16`. Independently evaluating the endpoints and line intersections reproduces the uniform bound `0.0009306975603620149`, below `0.001`. [M2], [C1], [E1], [D1]

I find the basic proof of Theorem 7 sound under its stated finite-model hypotheses: fixed-policy values are affine in the reward coefficients; anchor upper values provide convex-combination upper bounds; positivity gives the policy-switching lower bound by backward induction. A separate horizon multiplier is not required for this complete-policy-value envelope. The action-separation proposition correctly requires the **same first action and continuation policy** at both endpoints. Re-executing its implementation reproduces the negative interval ending at `0.36101794261747294`, the unresolved band, and the positive interval starting at `0.3736538321392164`. This is not a proof of a unique switch inside that band, and the author does not claim one. [M2], [D1]

**Actor and game corrections.** The resource actor is now correctly presented as a possible initialization device rather than the source of final policy accuracy. The all-nine matched results are retained, including the small actor–zero differences and the failures of the fitted quadratic comparators. The persistent-capacity game changes the transition economically rather than merely increasing the size of the old reset calculation. The all-date unilateral best-response test and late-date negative control now test the advertised scope. The additional reviewer execution confirms the resource and game validators without overwriting author results. [M3], [M4], [E1], [D1]

**Interpretation.** The annuity identity, the distinction between `C` and `kC`, and the finite-model/diffusion separation are explicit. I do not allege that a sampled residual has been passed off as a Brownian guarantee, that the resource actor remains unablated, or that a date-zero test is still being represented as an all-date test. Those would be inaccurate descriptions of R5.

## 2. Major findings

### R5-F1 — The contribution has not been distinguished from optimistic linear support and policy-cache transfer

**Severity: decisive contribution objection.** Relevant locations are the Introduction's contribution paragraph, Proposition 6, Theorem 7, the scalar anchor construction, and Supplement S.7. [M1], [M2]

R5 appropriately credits Nemecek and Parr (2021) for the policy-cache upper bound. That is a genuine improvement over claiming the upper envelope as new. But the closest comparison cannot stop there. Alegre, Bazzan, and da Silva (2022) develop successor-feature optimistic linear support (SFOLS), combining policy-set construction with generalized policy improvement; their Algorithm 1 chooses new reward weights, Algorithm 2 bounds possible improvement, and Theorem 4.1 concerns corner weights of a piecewise-linear value envelope. Their paper also identifies the connection to the Nemecek–Parr bound. R5 does not cite or compare with this work. [L1], [L2]

The relevant correspondence is mathematical, not terminological. At fixed `k`, R5 stores vectors that determine the lines

$$
J_i(s,n;d)=[B_i(s,n)-kC_i(s,n)]+dA_i(s,n).
$$

It takes their pointwise maximum, combines solved anchor values into an optimistic upper bound, and obtains another policy by solving at a parameter where the bound is most unsatisfactory. That is precisely the family of design questions for which optimistic linear support is a necessary comparator. Calling the reward weight a contract contrast does not by itself change that algorithmic question.

There are real distinctions that should be assessed rather than erased: R5 demands simultaneous coverage over all finite states and dates; its implemented switching rule selects among policy actions using policy values; its scalar implementation uses adjacent chords; and it adds an opposite-action separation test. These are not literally identical statements to a convex-coverage result formulated for an initial-state distribution or to full action-value generalized policy improvement. But R5 needs to show what those distinctions buy. Dates can be included in a finite state description, and statewise maxima are available in this enumerated example. The manuscript presently does not demonstrate a new obstruction, a sharper order of error, reduced oracle complexity, or a substantial economic consequence that existing transfer machinery could not obtain.

The contract reduction is correct but its depth should also be assessed accurately. The pathwise equality

$$
\rho\int_0^\tau e^{-\rho t}\,dt+e^{-\rho\tau}=1
$$

immediately yields `d=m-rho*ell`. It does not depend on preference adjustment, financial hedging, a neural approximation, or this particular stopping diffusion. Convexity and the two-contract moment inequality then follow from maximizing affine functions and adding two optimality inequalities. These are useful organizing observations, but a correct accounting identity plus standard revealed preference is not, without a further result, a major new economic theorem.

**What would resolve the objection:** a precise result-by-result comparison with policy caches and optimistic linear support, including the distinction between initial-distribution and simultaneous statewise guarantees; an executed same-oracle comparison of anchor counts, preparation costs, memory, and final guarantees; and a clearly identified additional theorem or economic implication. Merely adding the missing citation or describing the same construction more emphatically would not resolve it. This is a judgment about incremental contribution, not an allegation of plagiarism.

### R5-F2 — The measured resource crossover does not survive a conventional reusable-QP comparator

**Severity: decisive computational finding; new executable countercomparison.** Relevant locations are Section 6.6, Table IX on printed page 22, `resource_ablation.py`, and the inherited `coupled_resource.py`. [M3], [C2], [C3]

The original R5 timing is a real measurement, and its accounting is substantially cleaner than an extrapolated break-even claim. On the author's machine the 2,048-query row reports `3.411242` seconds for critic training plus deployment versus `5.707676` seconds for the reference, a ratio of `1.6732`. I do not claim that these recorded times are fabricated. The problem is the inference that this comparison identifies the nonlinear learned continuation as the useful reusable object. [E1]

Every query in that workload has the same dynamics, shocks, horizon, quadratic costs, and nodewise feasible set. Only the initial state changes. Stacking the 21 nonanticipative control vectors therefore gives the **same parametric convex QP** for every query:

$$
C_x(u)=\tfrac12 u^\top H u+f(x)^\top u+c(x),
\qquad u_h\ge0,\quad \mathbf1^\top u_h\le0.25d.
$$

The Hessian and the linear map defining `f(x)` can be assembled once. This is ordinary structural reuse, not policy learning. The submitted reference instead applies its original tree-gradient routine with a conservative global step bound. Its node probabilities vary across dates, so probability-based diagonal preconditioning is particularly natural.

The reviewer implementation analytically assembles the quadratic form, scales by node probabilities, computes the resulting Hessian's largest eigenvalue once, and solves from **zero controls for every query**. It includes setup, all 64 terminal paths, and an independent evaluation of the author's complete-tree gradient and convex optimality gap. The information structure, feasible controls, initial-state draws, and `10^-3` tolerance are unchanged. It is not a clairvoyant pathwise optimization, an unconstrained Riccati calculation, a fitted quadratic continuation, or a table of precomputed query answers.

All following times are **reviewer-machine** seconds, measured serially with one-thread numerical libraries and median-of-three query runs. The learned arm uses the deposited critic; its critic-only training cost is independently rerun and included. The original reference is rerun on the same machine. [D1]

| Fresh queries | Learned continuation: training + query | Author reference, rerun | Reusable exact QP: setup + query | QP full-tree gap, maximum | Learned / reusable-QP time |
|---:|---:|---:|---:|---:|---:|
| 32 | 1.153111 | 0.129609 | 0.005942 | 0.000633261 | 194.06 |
| 128 | 1.282531 | 0.362474 | 0.011368 | 0.000664162 | 112.82 |
| 512 | 1.937393 | 1.263352 | 0.041384 | 0.000664162 | 46.82 |
| 2,048 | 4.442411 | 4.809725 | 0.165284 | 0.000677426 | 26.88 |

The independent quadratic-form cost/gradient checks agree with the tree implementation to floating-point precision. Across these workloads the gradient discrepancy is below `6.1e-15` and the largest feasibility discrepancy below `4.5e-16`. The 2,048-query QP's own full-tree gap is below the same `0.001` target. Its maximum cost-loss upper bound relative to the deposited tighter reference is `1.4957168343753015e-6`; that tighter-reference comparison is corroboration, not needed for its own gap certificate. The replayed learned costs match the deposited costs within `6.7e-16`.

Even after excluding all setup and learning costs, the largest workload takes about `3.3274` seconds for learned deployment against `0.1623` seconds for the reusable QP. Thus the finding is not merely that training has been amortized over too few queries. A more direct exploitation of the same problem structure is substantially faster online as well.

The exact ratios are hardware- and implementation-dependent; no universal nonneural superiority follows. What does follow is that the manuscript's economic-computation inference is not identified by its chosen comparator. Matching welfare tolerances is necessary but not sufficient when only one side is allowed to exploit reusable structure effectively. The comparison with a **fitted full quadratic continuation** does not fix this: that approximation class is different from solving the original parametric quadratic program exactly to a certified tolerance.

**What would resolve the objection:** include a reusable structural solver in the matched workload comparison and explain where learned continuation adds value beyond it. A broader advantage would need evidence across genuinely more difficult horizons, uncertainty, or model families, with comparable reuse and conditioning in the nonneural arms. Simply retiming the existing reference or relabeling the observed ratio as conditional would not supply the missing computational contribution.

### R5-F3 — The flagship uniform target can be met without any neural proposal in the deployed policy bank

**Severity: major attribution and contribution finding; new all-parameter ablation.** Relevant locations are Section 6.4, Tables V–VI, the contract implementation, and the response to R4-F5. [M3], [C1], [H2]

The repaired policies are not the original neural policies with a newly demonstrated learning guarantee. At each anchor the program exhaustively optimizes the finite menu backward using the already optimized continuation. The separate recursion then evaluates the resulting policy features. This is a valid and useful exact dynamic-programming repair, but the operation doing the scientific work must not disappear behind the NBO label.

To quantify the contribution of the frozen proposals, I removed only those three actions and kept the complete 1,565-action common mesh. The comparison continues to use the **original full target** as its welfare benchmark. At all 47 deposited contract anchors, the largest loss over every date and state is only `3.8712475224245146e-5`; the largest focal-state loss is about `7.13e-11`. The initial endpoint portfolios remain `-0.5` and `0.8`. Neural actions were selected 37,000 times in the original 607,992 anchor-policy decisions, so the correct observation is **small value contribution**, not “the neural actions are never selected.” [D1]

The additional check goes beyond those anchor comparisons. It constructs a common-mesh policy bank at the same anchors, independently evaluates its features, and retains the deposited **full-target** anchor optima as upper information. For each adjacent interval it maximizes

$$
U^{\mathrm{full}}(d)-
\max\{J^{\mathrm{mesh}}_a(d),J^{\mathrm{mesh}}_b(d)\}
$$

at both endpoints and the two feasible-policy lines' intersection, for every date and state. This is the same mathematical welfare test as the manuscript, but no learned action is permitted in the lower-bound policies. Its maximum is **`0.0009306975845364551`**, still below `0.001`. Positivity and the policy-switching argument therefore certify an entirely common-mesh deployed policy over **all `d` in `[0,1]`**, all original finite states, and all dates against the original full problem. Random switching replays are additional checks, not the source of that interval conclusion. [D1]

Two qualifications are essential. This ablation reuses the author's 47 anchor locations and full-target upper oracle; it is not an independently timed, autonomous anchor-discovery method. It also does not establish a diffusion error bound or reproduce the original sign-separation intervals for the restricted action set. Nevertheless, it directly shows that learned proposals are unnecessary for attaining the specified flagship welfare tolerance with this bank construction. Removing them has not weakened the welfare benchmark to a different target.

The author already disclaims a neural compression advantage in this low-dimensional example. That disclaimer is accurate, but it leaves the paper with a familiar exact-grid policy cache as its strongest certified application. Together with R5-F2, this makes the gap between valid computation and an important new neural methodology substantive rather than cosmetic.

**What would resolve the objection:** distinguish the economic value and computational value of neural proposals, approximate continuation, the upper-bound oracle, and the policy cache in a matched ablation. A meaningful result would demonstrate an advantage or a new guarantee that survives the common-mesh bank and reusable-QP controls. More exact repairs of the same small target do not establish such an advantage.

### R5-F4 — The economic experiment certifies a selected exit incentive, but not yet a substantial new economic result

**Severity: major economic-significance objection.** Relevant locations are the preference model, Proposition 6, Table VI, and the correlation/refinement panels. [M2], [M3], [M5], [E1]

The operating-benefit/settlement contrast has a coherent interpretation. It is also correctly distinguished from a harmless utility normalization and from unconditional preference hedging. The sign certificates add real numerical information: they rule out all opposite-sign actions in the declared menu over specified contract intervals. I do not dismiss those statements merely because the sign margins are small, and I do not substitute an action-distance objection for a value calculation.

However, what economically surprising or generally informative result has been learned beyond the effect of rewarding time before exit? The baseline stopping payoff is chosen so that it is a strict supersolution with a substantial negative flow-generator margin. The operating rectangle, bounded consumption, capped portfolio, and settlement rule all shape the incentive to terminate. Raising `d` changes the compensation for remaining in that environment. The algebra predicts greater discounted duration under optimal choice, but not a portfolio-sign theorem. The sign reversal is obtained from the selected finite economy.

In the five focal-state contract rows, consumption remains at `0.8` and preference adjustment at `0.2`, while the portfolio moves between the allowed endpoints `-0.5` and `0.8`. The endpoint reversal also survives the correlation changes. These are useful disclosures. They do not establish that endogenous preference adjustment is the economic source of the reversal, nor do they establish that the interior hedging decomposition explains the focal decisions. The manuscript itself correctly cautions against that interpretation.

A sharply informative economic analysis would separate generic stopping incentives from preference formation. For example, it could characterize when contract changes must alter risk exposure, and when the same reversal is possible without adjustable preferences; then test the implication using otherwise matched restrictions on preference adjustment, the operating boundary, and settlement curvature. The precise design should follow an economic question, not a requirement to accumulate another arbitrary parameter panel. Some choices of outside option define genuinely different contracts, not numerical robustness checks, and should be interpreted as such.

There is also an unresolved scale of relevance. The parameter interval is chosen in fixed cardinal utility units, not linked to an observed contract or an identified economic magnitude. This is not a demand that a theory paper contain data. A theoretical contribution can stand without estimation. But then the economic force must come from a substantial, portable proposition or a mechanism with a convincing domain of applicability. The annuity identity is portable but elementary; the portfolio reversal is computationally certified but highly specific. The current combination does not bridge that gap.

Finally, the strongest transfer theorem changes only reward coefficients with kernels and feasible actions held fixed. Changes in shock correlation, survival, boundary geometry, or transition dynamics require separate solves and generally invalidate direct reuse of the stored features. R5 acknowledges this. The issue is therefore not hidden mathematical invalidity, but the economic range of the result offered as the central counterfactual method. The separate recursive, sophisticated-self, and capacity-game checks do not enlarge that demonstrated range: they remain distinct structured benchmarks, not applications of a common trained and certified counterfactual operator. [M4]

**What would resolve the objection:** develop a consequential economic implication that cannot be reduced to a generic stopped-reward accounting exercise, and connect its numerical investigation to a comparator-robust method. A larger stack of valid benchmark regressions is not a substitute for that contribution.

## 3. Disposition of the previous R4 findings

The following classifications concern the actual objection at its stated scope. “Closed” does not mean that the overall paper has met the publication standard.

| Previous item | R5 disposition | Reason |
|---|---|---|
| R4-F1: identifiable original contribution | **Open** | Contract reuse is better organized, but the missing optimistic-linear-support comparison and reviewer countercomparators leave significance unresolved. |
| R4-F2: operational nonlinear welfare budget | **Closed for the declared finite target** | The full-menu anchor checks and the all-state/date/interval envelope are executable and reproduce. No diffusion transfer is implied. |
| R4-F3: actor-free and continuation comparisons | **Closed for the requested ablations** | All nine actor-free cases and full PSD-quadratic fits are present. Their narrow factual results stand; they do not settle R5-F2. |
| R4-F4: actually measured reusable workloads | **Measurement issue closed; substantive advantage open** | Fresh query workloads are executed. The resource advantage is comparator-sensitive and reversed by structural QP reuse. |
| R4-F5: substantial profitable neural-policy deviations | **Closed for exact finite-model repair; neural attribution open** | Full-menu backward optimization removes the deviations. It is not evidence of a successful new neural repair algorithm. |
| R4-F6: liquidation and cardinal utility levels | **Normalization issue closed; economic significance open** | The annuity direction and finite sign intervals are explicit. General economic content remains to be established. |
| R4-F7: effort versus weighted expenditure | **Closed** | `C` and `kC` are distinguished, and nonmonotonic weighted charge is retained. |
| R4-F8: reset capacity versus genuine persistence | **Closed for the new finite game** | Survival changes the transition, policies depend on installed capacity, and the continuation game is checked. It is not a trained neural game. |
| R4-F9: all-date exploitability | **Closed** | Full backward deviations and an explicitly late-date negative control are implemented and re-executed. |

## 4. Presentation and reporting points

The supplement's S.6 still calls the R4 sources “authoritative” within its historical provenance subsection. Its opening and S.8 explain the inheritance, so this is not evidence that the wrong manuscript was built. It should nevertheless say **authoritative R4 source record** to avoid contradicting the root R5 index. Preserve the history; clarify its status rather than silently replace it.

Use **maximum of feasible policy values**, or **lower bound**, when explaining `L=max_i J_i`. Calling this the “lower envelope” is understandable as a bound on the optimum, but is easy to confuse with the mathematical lower envelope of the policy lines. The formulas and proofs are clear; this is a terminology issue, not a counterexample.

Retain the distinctions that R5 now gets right: unknown switch band versus a certified threshold; full finite-model guarantee versus diffusion approximation; held-out resource guarantees versus uniform state-space guarantees; exact game references versus neural experiments; and a completed build versus a scientific conclusion. These disclosures improve the manuscript and should not be removed in response to this report.

## 5. Recommendation and requirements for a materially different assessment

I recommend **rejection in the present form**, rather than acceptance or a routine revise-and-resubmit. The finite-model correctness repairs are substantial, and the repository is unusually auditable. But correct implementation of familiar bounds is not sufficient evidence of a major new method. Nor is a speed crossover against a conventional solver that is not permitted comparable structural reuse a persuasive demonstration of the value of neural continuation.

A materially different assessment would require four substantive advances corresponding to the findings: a defensible incremental result relative to optimistic linear support and policy caches; a matched computational comparison that includes reusable structural solvers; an explanation of what learned components contribute after removing them from the certified policy bank; and an economic implication whose importance survives the chosen stopping-contract example. These are not requests to delete the historical material, abandon the economic model, or replace ambitious claims with vague qualifications. They are requests to supply the missing contribution.

The present report establishes a narrower and more useful conclusion than “nothing works.” **The finite certificates work. The all-date repairs work. What remains unestablished is why this combination constitutes a sufficiently original and important contribution for Econometrica.**

## Reproduction and source notes

Run from the repository root in an environment with NumPy, SciPy, and PyTorch:

```bash
python reviews/2026-09-16-econometrica-r5/reviewer_diagnostics.py \
  --mode all --remove-neural --output /tmp/nbo-r5-referee-primary.json
python reviews/2026-09-16-econometrica-r5/additional_checks.py \
  --output /tmp/nbo-r5-referee-additional.json
```

The deposited `diagnostic_results.json` retains scalar checks, all interval bounds, all 47 anchor-restriction comparisons, and timing samples. Per-query QP cost/gap arrays are regenerated by the first command; their original output hashes are recorded in the manifest rather than repeating those arrays in the review commit. Numerical certificates here, like those in R5, use double precision and the stated tolerances, not directed-rounding interval arithmetic. No reviewer script writes an author source or output file.

### Pinned manuscript and repository sources

- **M0:** R5 revision index and authoritative reading order.
- **M1:** Introduction, particularly lines 16–23 on related literature and contribution.
- **M2:** Contract reduction, reuse theorem, interval construction, and action separation.
- **M3:** Computation, particularly lines 45–62 and 100–114; main Tables V, VI, and IX.
- **M4:** Recursive utility, temporal selves, and persistent dynamic competition.
- **M5:** Stopped-economy admissibility, boundary contract, and supersolution calculation.
- **C1:** Contract kernel, exact anchor solution, feature evaluation, and policy-cache construction.
- **C2:** Original resource primitives, exact tree cost/gradient, and reference optimizer.
- **C3:** R5 matched resource ablations and fresh-state workload implementation.
- **E1:** R5 generated execution summary; not a substitute for source or independent checks.
- **H1/H2:** R4 referee report and R5 point-by-point response.
- **D1:** The reviewer scripts and generated diagnostics in this directory.

[M0]: https://github.com/TrillionniumFoundation/NBO/blob/c9f71077cf6a339573ac07be55d7660797bcf6ea/REVISION_INDEX.md
[M1]: https://github.com/TrillionniumFoundation/NBO/blob/c9f71077cf6a339573ac07be55d7660797bcf6ea/revisions/2026-09-16-r5/paper/01_introduction.tex#L16-L23
[M2]: https://github.com/TrillionniumFoundation/NBO/blob/c9f71077cf6a339573ac07be55d7660797bcf6ea/revisions/2026-09-16-r5/paper/04b_contract_transfer.tex
[M3]: https://github.com/TrillionniumFoundation/NBO/blob/c9f71077cf6a339573ac07be55d7660797bcf6ea/revisions/2026-09-16-r5/paper/05_computation.tex
[M4]: https://github.com/TrillionniumFoundation/NBO/blob/c9f71077cf6a339573ac07be55d7660797bcf6ea/revisions/2026-09-16-r5/paper/06_extensions.tex
[M5]: https://github.com/TrillionniumFoundation/NBO/blob/c9f71077cf6a339573ac07be55d7660797bcf6ea/revisions/2026-09-16-r5/paper/S3_stopped_preferences.tex
[C1]: https://github.com/TrillionniumFoundation/NBO/blob/c9f71077cf6a339573ac07be55d7660797bcf6ea/replication/r5/contracts.py
[C2]: https://github.com/TrillionniumFoundation/NBO/blob/c9f71077cf6a339573ac07be55d7660797bcf6ea/replication/r4/coupled_resource.py#L83-L110
[C3]: https://github.com/TrillionniumFoundation/NBO/blob/c9f71077cf6a339573ac07be55d7660797bcf6ea/replication/r5/resource_ablation.py
[E1]: https://github.com/TrillionniumFoundation/NBO/blob/c9f71077cf6a339573ac07be55d7660797bcf6ea/revisions/2026-09-16-r5/execution_summary.md
[H1]: https://github.com/TrillionniumFoundation/NBO/blob/11082cc5054e91d3b2ac27826705f374ca74bfae/reviews/2026-09-16-econometrica-r4/referee_report.md
[H2]: https://github.com/TrillionniumFoundation/NBO/blob/c9f71077cf6a339573ac07be55d7660797bcf6ea/revisions/2026-09-16-r5/response_to_referee.md
[D1]: diagnostic_results.json

### Primary literature checked for this report

**L1.** Nemecek, Mark, and Ronald Parr (2021), “Policy Caches with Successor Features,” *Proceedings of the 38th International Conference on Machine Learning*, PMLR 139, 8025–8033. The policy-cache bounds are the relevant comparison, already acknowledged in R5.

**L2.** Alegre, Lucas Nunes, Ana L. C. Bazzan, and Bruno C. da Silva (2022), “Optimistic Linear Support and Successor Features as a Basis for Optimal Policy Transfer,” *Proceedings of the 39th International Conference on Machine Learning*, PMLR 162, 394–413. Relevant locations: Theorems 3.2, 3.5, and 4.1; Algorithms 1–2; Appendix A.4. The report's comparison with R5 is the referee's analysis, not a statement that the papers' hypotheses or switching rules are identical.

[L1]: https://proceedings.mlr.press/v139/nemecek21a.html
[L2]: https://proceedings.mlr.press/v162/alegre22a.html
