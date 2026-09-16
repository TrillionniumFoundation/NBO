# Referee report: *Neural Bellman Operators*, R7
## Economic-target audit, both adjustment regimes, and contribution assessment

**Author:** Qian Qi  
**Report date:** 17 September 2026  
**Recommendation:** **Reject in its present form for Econometrica.**  
**Reviewed manuscript:** `revision/econometrica-r7-2026-09-16` at `fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17`  
**Verified manuscript tree:** `cdc8e227881d5e95a8740c4f77298f73a0b9399d`  
**New review branch:** `review/econometrica-r7-economic-target-audit-2026-09-17-fbfbf90`  
**Historical-review parent:** `bfba0168a58b35507e37183147ecd2249de65a7c`

This is an owner-commissioned, external-referee-style advisory assessment. It does not represent an appointment by Econometrica, a journal submission, or an editorial decision. The recommendation concerns this manuscript, not the possibility of developing a successful research contribution.

## 1. Assessment for the editor

R7 has repaired several mathematical and computational defects identified in the preceding rounds. It now contains a coherent comparison between a count-informed upper recursion and a compressed corrected chord, a total coefficient-error bound that includes policy-bank error, and a decision-specific regional certificate. These improvements deserve credit. A review that continued to describe the corrected construction as invalid, or asserted that compression has no positive computational case, would not accurately assess this revision.

Nevertheless, I do not recommend publication. The paper still lacks a sufficiently secure connection between its computational certificates and its principal economic conclusion. The new audit below sharpens this diagnosis. I independently recomputed **both adjustment regimes**, rather than only the no-adjustment arm examined in the preceding directional report. On wealth-refined representations, the inspected corner changes from opposite first-risk rankings to positive rankings in both regimes. At the same time, the relative adjustment option remains positive. Thus the calculation distinguishes two propositions that the economic narrative must not conflate: adjustment can be relatively more valuable in the positive-risk class without being what changes the risk choice at the advertised contract.

This is not a counterexample to the tensor theorem on the original arrays. It is evidence that the location of the reported choice reversal depends on a numerical representation whose economic approximation error is not controlled at the decision margin. The remaining contribution problem is likewise substantive: the headline certificate uses the count method, while the necessity of the learned proposals and the economic importance of compression have not been established by that certificate. A valid regional inequality, a helpful local computational tradeoff, and a possible economic mechanism do not, by their conjunction alone, establish the paper's claimed integrated contribution.

The needed response involves research and discriminating evidence, not another layer of qualifications or a cosmetic reorganization.

### Which revision is being reviewed?

I checked the live branch inventory before the audit and again before creating this review branch. The three R8-named branches point to existing R7 review commits. Comparing the most inclusive of them, `bfba0168...`, with the manuscript commit shows eighteen added review files and no manuscript or numerical-source revision. `REVISION_INDEX.md` still identifies R7. Accordingly, this is a further assessment of **unchanged R7**, not a review of a nonexistent R8 manuscript. No failure to answer the newer R7 reports is attributed to an author response that has not been deposited. [M0, H1]

## 2. Materials, execution, and evidentiary limits

The assessment draws on the assembled R7 manuscript and supplement, their entry points and response to R6, the new comparative and economic proofs, the inherited operator, approximation, stopped-economy and risk-frontier sections, and the corresponding numerical source. The preceding directional report supplies the historical spatial finding against which the new calculation is compared. The closest mathematical scrutiny concerns the new R7 propositions and their implementation, not an independent re-proof of every inherited result. The main manuscript's comparative and economic tables and the supplement's arithmetic discussion were also inspected in rendered PDF pages. [M0–M7, H1]

I obtained the source and executed evidence from Actions run `35063710310`, artifact `10433863234`. Its ZIP SHA-256 is `b0bcb8542760adffae90e3ffff7ad61d0fe5b49e0b93e0f66a05eeea170d51c2`. Extracting the source archive and applying the deposited evidence overlays reconstructs the exact Git tree `cdc8e227...` of the reviewed commit. All 27 authored-source inventory entries match their hashes. The 45-page main PDF and 29-page supplement match the deposited PDF hashes. No manuscript, author numerical source, or author evidence file was changed.

Three evidence classes are kept separate:

* **Rerun author checks:** the 96-model, 480-parameter validation, the two-stage primitive calculation, and the coefficient-only regional replay. The wrapper redirects output away from the author's evidence files. These are reruns of deposited author routines, not newly invented independent proofs.
* **New reviewer calculations:** a separate blockwise Bellman driver solves both risk classes and both adjustment regimes on three wealth grids, at the four advertised corners and the center, under two action-menu treatments. This yields 120 class values and 120 direct selected-policy replays. The driver uses the author's transition constructor, so it is not an independently implemented stopped diffusion.
* **Attributed evidence:** the author's full timing contest, historical neural training and structural comparisons, and the earlier reports' temporal and preference-grid experiments. Those large experiments were not rerun here.

The maximum sparse-backend versus weighted-gather discrepancy is `4.440892098500626e-16`. The maximum discrepancy across the new direct policy replays is `1.3322676295501878e-15`. The sixteen original-grid corner class values in the full-menu arm reproduce the deposited author values within `2.220446049250313e-16`. These are useful implementation checks, not bounds on spatial approximation or proofs of a limiting economic sign. All 120 class values, including unchanged signs, are retained in `diagnostic_results.json`; the scripts and reproduction instructions accompany this report. [D1–D3]

## 3. What this revision has genuinely accomplished

**The upper-oracle ordering is coherent.** The count recursion chooses a common action before mixing the two endpoint-law branches. The enlarged information about the remaining count explains its status as an upper value. The coefficientwise ordering against the corrected chord, and its preservation under positive Bernstein subdivision, are appropriately formulated. I found no algebraic counterexample to the stated finite-model ordering. In the rerun, the largest count replay discrepancy is `1.7763568394002505e-15`, and the smallest chord-minus-count coefficient is `-2.220446049250313e-16`, consistent with floating-point roundoff. [M1, M3, D1]

**The total error theorem addresses the right object.** The bound `2 L_n w + (1/2) Q_n w^2` includes the endpoint-policy bank rather than only the quadratic correction. It allows maximizing actions to change. Its scalar worst-case interval count is explicitly `O(epsilon^-1)` for fixed finite-model constants; the manuscript no longer infers a second-order policy-bank rate from the correction. The proof's coefficient induction is important. Random numerical checks support implementation consistency but are not its justification. [M1, M3]

**The primitive option inequality is a genuine sufficient condition.** Global concavity of the specified CRRA expression in its preference index gives a lower quadratic option bound and an upper bound. The endpoint-curvature argument supports the declared continuum family. The rerun obtains a uniform relative-option lower bound of `0.0018668287652439802`. The proposition is not merely the observation that enlarging the feasible set helps. [M2, M4, D1]

**The regional certificate is decision-specific.** It separately bounds each risk class under each adjustment regime. The deposited coefficient replay agrees exactly with the stored bounds. Conditional on its finite-array and arithmetic assumptions, Table XVIII establishes the advertised signs on that target; it does not infer a sign of order `10^-5` from the generic `10^-3` welfare tolerance. [M2, M4, M5, D1]

**Compression has a measured benefit.** Table XVII reports 18 anchors and 73.41 seconds for chord-only refinement, versus 11 anchors and 115.38 seconds for count-only refinement and 127.73 seconds for the cascade. These are deposited single-pass results, not reviewer timing measurements. Count needs fewer anchors but more upper-oracle work. This is a real tradeoff and must not be erased by the subsequent criticism of its broader significance. [M5]

## 4. R7-ET-F1 — Recomputing both regimes separates an adjustment premium from a choice reversal

**Severity: publication-blocking robustness issue for the flagship economic interpretation.**  
**Locations:** Main Section 8.13 and Table XVIII, pp. 39–40; `05c_r7_evidence.tex`; Supplement S.11.3–S.11.4; `replication/r7/decision.py`. [M4–M5, C1]

Write `Delta^0` for the positive-first-position class value minus the nonpositive-first-position class value when deliberate adjustment is prohibited, and `Delta^adj` for the analogous difference with adjustment. The reported region is

\[
(\lambda,d)\in[0,0.25]\times[0.4,0.45],\qquad (u,X)=(2,1.25),\quad k=2.
\]

The whole-region conclusion requires `Delta^0 < 0 < Delta^adj`. The previous directional report already found that the first inequality changes under wealth-only refinement. It did not recompute the adjusted arm on those grids. The present experiment supplies that missing comparison, while preserving the distinction between the two action-menu treatments. [H1]

### Design and action-set control

Every run retains eight dates over horizon one, 33 preference nodes, the published financial and preference-shock parameters, the same stopping and settlement construction, and the common-parameter mixture. Only wealth-node counts change from 49 to 97 and 145. The initial state is a node on all grids.

The **common-menu arm** holds fixed the exact union of both historical meshes: 1,565 distinct actions, of which 185 satisfy zero deliberate adjustment. It does not use the author's `include_neural=False` shortcut, which would also remove one of those meshes. This arm isolates spatial representation with an unchanged finite menu. The previous exact-menu audit establishes that the admissible original frozen proposals in the no-adjustment arm are duplicates of these common actions. [C2, H1]

The **prolonged-full arm** additionally retains the three stored state/date-dependent proposals. Their controls at original nodes are copied exactly; at new nodes they are bilinearly interpolated, within the same control box. This is an explicitly reviewer-defined extension, not a claim that the author provided a refined-grid neural target or that a neural network was retrained. In particular, new interpolated zero-adjustment proposals can enlarge the fixed arm's menu slightly. The original-grid full arm is the original target and reproduces the author's class values. Agreement between this extension and the fixed common-menu experiment is useful robustness evidence; their feasible sets are not silently equated. [D2]

### Results at the vulnerable corner

At `(lambda,d)=(0.25,0.45)`, the common-menu results are:

| Preference × wealth nodes | `Delta^0` | `Delta^adj` | `Delta^adj - Delta^0` |
|---|---:|---:|---:|
| 33 × 49 | `-0.0000530012509050` | `+0.0003245296361472` | `+0.0003775308870522` |
| 33 × 97 | `+0.0000612627395757` | `+0.0004264103236278` | `+0.0003651475840520` |
| 33 × 145 | `+0.0000979426715393` | `+0.0004600881635678` | `+0.0003621454920285` |

The prolonged-full arm gives the same qualitative result:

| Preference × wealth nodes | `Delta^0` | `Delta^adj` | Relative option |
|---|---:|---:|---:|
| 33 × 49 | `-0.0000530012509050` | `+0.0003245296453478` | `+0.0003775308962528` |
| 33 × 97 | `+0.0000612627395757` | `+0.0004264101412843` | `+0.0003651474017086` |
| 33 × 145 | `+0.0000979430882651` | `+0.0004595449459314` | `+0.0003616018576663` |

These point solves establish a narrower and more informative result than saying that the economic mechanism disappears. At this corner, both refined-grid regimes select the positive class, but adjustment remains relatively more valuable in that class. The relative option is positive at all thirty grid/parameter/menu combinations examined, ranging from approximately `0.000361602` to `0.000438372`. This is pointwise evidence, not a new regional lower bound. [D1–D2]

Nor is the original opposite-ranking phenomenon eliminated at every inspected point. At the center `(0.125,0.425)`, the common-menu `Delta^0` remains negative on all three grids, while `Delta^adj` remains positive. The respective fixed-arm differences are `-0.0002093269611781`, `-0.0000947805379946`, and `-0.0000576017554235`. The evidence therefore concerns the placement and stability of the advertised whole-region choice reversal, not a claim that adjustment can never reverse risk rankings. [D1]

**Required response.** Explain the location and movement of the choice region relative to a clearly identified economic target. More decimal places for the original finite-array certificate will not address this finding. Moving to a newly favorable rectangle without explaining the movement would also be inadequate. The original arrays and rectangle should remain available as an explicitly delimited result. A substantive response must address both regimes, keep the policy menus traceable, and distinguish relative option value from a change in the chosen risk class.

## 5. R7-ET-F2 — The precision budget does not yet control the economically relevant error

**Severity: major error-account and interpretation issue.**  
**Locations:** Inherited approximation theorem, main model definition, and Supplement S.11.4. [M4, M6–M7]

The arithmetic allowance of `3.797650002493679e-9` per class concerns the stored finite model. The certificate also controls the specified upper-relaxation and feasible-policy gaps. It does not bound the errors in constructing that model from the economic transition problem. The manuscript discloses this limitation; the objection is that the disclosed limitation is quantitatively consequential, not that the disclosure is absent.

For clarity, suppose the intended target class values satisfy

\[
|V_{\sigma}^{r,\mathrm{target}}-V_{\sigma}^{r,\mathrm{array}}|
\leq \eta_{\sigma}^{r},\qquad r\in\{0,\mathrm{adj}\}.
\]

Then a certified array interval `[ell_r,u_r]` for the class difference only implies the target interval

\[
[\ell_r-\eta_+^r-\eta_-^r,\ u_r+\eta_+^r+\eta_-^r].
\]

Using the reported Table XVIII margins, sufficient additional conditions for its two strict signs are approximately

\[
\eta_+^{\mathrm{adj}}+\eta_-^{\mathrm{adj}}<6.8887\times10^{-5},
\quad
\eta_+^0+\eta_-^0<5.2993\times10^{-5},
\]

uniformly over the advertised region. These are additional target-error requirements; the table's arithmetic allowances should not be charged a second time. A uniform per-class bound below half the corresponding margin would suffice. The new wealth-only movement in the fixed difference, about `1.14264e-4` from 49 to 97 nodes at the corner, exceeds the original decision margin. It is evidence that the unbudgeted component matters. It is not itself a rigorous bound on either discretization's distance from a limiting solution.

There is also a structural reason not to dismiss interpolation as a harmless representation detail. For an interior quadrature outcome `Y`, positive tensor interpolation can be viewed as randomizing to neighboring nodes `Z`. Conditional means are preserved, but total covariance acquires the diagonal term

\[
\operatorname{Cov}(Z)-\operatorname{Cov}(Y)
=\operatorname{diag}\!\left(E[(Y_i-l_i(Y))(r_i(Y)-Y_i)]\right).
\]

This follows directly from conditional two-point variances and the law of total covariance. The earlier directional report checks the identity against actual kernel weights and shows that wealth refinement changes this artificial marginal variance while retaining the decision calendar. Those prior moment calculations are attributed, not rerun here. The current two-regime calculations show why the issue bears on the economic decision, not only on a local moment diagnostic. [C2–C3, H1]

**Required response.** Either control the relevant decision error relative to the intended continuous-state target, or give an economic justification for the finite-state transition as a primitive and demonstrate robustness to meaningful perturbations of that primitive. Holding eight dates fixed is not an answer to a sensitivity exercise performed with those same eight dates. Merely inserting an unevaluated approximation constant from the inherited theorem into the discussion would not close the gap. No particular discretization rate is presumed here; the requirement is an error account or economic defense commensurate with the claimed sign.

## 6. R7-ET-F3 — The explanatory specialization is not yet a mechanism for the dynamic result

**Severity: major economic contribution issue.**  
**Locations:** Primitive proposition, inherited risk-frontier discussion, and Table XVIII. [M2, M4, M7]

The two-stage proposition is useful, but its lotteries and operating durations are exogenous, whereas the dynamic application jointly chooses consumption, preference adjustment, subsequent portfolio positions, and stopping. Its cost rectangle is `[20,80]`, whereas the stopped example uses `k=2`. R7 explicitly says that the specialization is not a calibration or approximation of that economy. This is honest, but it leaves a substantive bridge to be built.

The new calculations provide a concrete reason to demand that bridge. In the author's primitive family, the positive-class preference shadow ranges from approximately `-3.11750` to `-1.48207`; all nine displayed positive-class optimal adjustments are negative. In the dynamic corner calculations on all three common-menu grids, the initial adjusted controls are `(c,theta,pi)=(0.8,0.2,0.8)` in the positive class and `(0.8,0.2,-0.5)` in the nonpositive class. Thus both classes choose the same upper-bound initial preference adjustment, not opposite initial adjustment directions. This is not a contradiction between theorems about different models. It shows why the two-stage shadow story cannot simply be treated as an explanation of the executed dynamic choice. [D1–D3]

The first-period portfolio choices are also at opposite boundaries. At the inspected corner, the class difference therefore compares the two constrained opportunities and their subsequent continuations; it is not an infinitesimal perturbation of a common interior portfolio optimum. The original-grid no-adjustment difference is the small residual of much larger feature contributions. Independent policy replay gives

\[
\Delta^0 = \Delta B+d\Delta A-2\Delta C+\Delta G,
\]

with, on the common 33 × 49 grid,

\[
\Delta B=-0.00309204772123,\qquad
0.45\Delta A=+0.00103636975303,\qquad
\Delta C=0,\qquad
\Delta G=+0.00200267671730.
\]

Their sum is approximately `-5.30012509e-5`. Settlement and operating duration are consequently quantitatively material to this observed ranking. This accounting does not causally attribute the ranking to any one feature: the policies determining all the features were optimized together. It identifies why a post-optimization option identity is not yet a portable explanation. [D1–D2]

**Required response.** Supply a dynamic sufficient condition, a justified limiting connection, or controlled counterfactuals that separately identify consumption exposure, operating duration, settlement, and subsequent policy adaptation. Any counterfactual changing an economic primitive must reoptimize consistently or explicitly state that it evaluates a fixed policy. The resulting account should predict something beyond the already computed ordering. Neither calibration to outside data nor utility-normalization invariance is imposed as a prerequisite for a theoretical paper. The manuscript already acknowledges the importance of cardinal normalization; that acknowledgement is not an explanation of the particular dynamic comparative static.

## 7. R7-ET-F4 — The integrated methodological contribution remains underidentified

**Severity: major originality and significance issue.**  
**Locations:** Abstract and introduction, comparative-oracle discussion, and computational sections. [M0–M5]

There are now three distinguishable ingredients: learned proposal construction, reusable feasible-policy evaluation, and upper certification. The most convincing new result uses exact finite-action endpoint optimization and count-based upper coefficients. It therefore does not, by itself, show that learning or corrected-chord compression is what makes the economic conclusion obtainable.

This is not a requirement that a neural method beat every structural solver, nor a claim that the learned proposals are mathematically irrelevant everywhere. The new common-menu experiment omits genuinely distinct adjusted proposals, and the prolonged-full experiment can produce different values. Nevertheless, the inspected signs and their spatial sensitivity are unchanged between those treatments. The full-grid regional theorem and the pointwise common-menu calculations have different scopes; I do not promote the latter into a neural-free regional certificate. The relevant unresolved question is what scientific or computational advantage the distinctive learned/compressed ingredient delivers at a common economic accuracy target.

R7's horizon counts are meaningful: with shared exact endpoint solutions, the specified chord construction uses `4H-6` action-wide kernel applications rather than `H(H+1)-2` for count, with lower additional upper-oracle storage. But the common policy bank still has order `m S H^2` coefficients, and the demonstrated anchors require exact finite optimization. The small-model horizon tests verify accounting; they do not establish a high-dimensional advantage or an end-to-end scaling result. [M1, M3, D1]

**Required response.** Identify a consequential workload and compare the complete procedures at the same decision or welfare error target, charging proposal construction, endpoint work, policy evaluation, storage, and certification. Retain the structural QP and mesh-only comparisons, including unfavorable outcomes. The criterion is not an arbitrary universal speedup. It is an attributable gain that survives an honest comparison and matters for the economic conclusion. A single-pass timing result is evidence for its reported task, not a general computational frontier. The paper's title and lead contribution should reflect what is actually established, rather than relying on the presence of neural components elsewhere in the repository.

## 8. R7-ET-F5 — The literature boundary needs a theorem-level correction

**Severity: major positioning issue, not an allegation that the new theorem is already known.**  
**Location:** Literature paragraph in `04e_comparative_oracles.tex` and the introduction. [M1]

The comparison with Quatmann et al. (2016) cannot rest on a contrast between probabilistic specifications and reward optimization. Their paper explicitly introduces expected rewards and nondeterministic Markov decision processes in Sections 2.1–2.2, and treats parameter lifting beyond an uncontrolled probability example. The broader 2024 treatment also includes regional synthesis for Markov decision processes and an expected-reward extension. Thus the presence of actions, rewards, or a repeated parameter is not, by itself, the new boundary. [L1–L2]

A useful correspondence would specify the time-augmented state, admissible scheduler information, repeated-parameter restriction, treatment of substochastic mass and terminal reward, and the exact upper relaxation. For finite horizons, augmenting the state by the date converts date-dependent recursions into a layered finite model. This elementary reduction does not prove equivalence of the two algorithms, but it prevents finite-horizon terminology alone from bearing an originality claim.

Heck et al. (2025) further develops tighter parameter-lifting abstractions and transformations aimed at retaining more dependency information. Its parametric-Markov-chain setting is not automatically equivalent to R7's controlled reward problem. It is nevertheless relevant to the claimed precision-versus-relaxation tradeoff and should be compared on its actual assumptions. [L3]

The potential distinctive object here is the particular signed compression, its ordering, total coefficient-error account, and resulting work/precision tradeoff. The author should establish that distinction directly. I have not shown that these particular results are contained in the cited papers, and I do not claim an exhaustive priority search. Adding bibliography entries without the mathematical correspondence would not answer the objection; benchmarking a software package outside its supported problem class is not required either.

## 9. Presentation and requirements for a substantive next revision

There is a small but concrete inconsistency: the final sentence of `04e_comparative_oracles.tex` says that the frontier does not represent the cascade as an executed autonomous timing contest, whereas Table XVII reports a separate autonomous experiment. The common-bank and autonomous exercises should be named explicitly to remove the ambiguity. This is not grounds for discarding the executed timing evidence. [M1, M5]

The larger organizational problem is inferential, not stylistic. The manuscript should make it possible to follow, without reconstructing the response history, the chain from an economically defined target to an approximation error, a policy-value certificate, a stable decision, and the incremental contribution of the proposed method. Preserving old evidence is good repository practice; its volume is not evidence of scientific closure. Historical manuscripts and adverse results should remain intact, while the current argument should be self-contained.

For another assessment, the following are the substantive acceptance gates for the objections in this report:

| Finding | What would address it | What would not address it |
|---|---|---|
| ET-F1 | Both-regime evidence explaining the movement of the choice region, with explicit target and menus | Replaying only the original array certificate or silently replacing the rectangle |
| ET-F2 | Decision-level target-error control, or a substantive finite-state primitive and robustness defense | Arithmetic precision alone or an unevaluated generic approximation constant |
| ET-F3 | A dynamic prediction or controlled mechanism analysis consistent with the executed economy | Repeating the option identity or treating the separate two-stage family as a calibration |
| ET-F4 | An attributable end-to-end gain at a common meaningful accuracy target | Kernel-call counts or neural terminology alone |
| ET-F5 | Explicit mathematical correspondence and differentiation from regional verification | A reward-versus-probability slogan or citations without a comparison |

These gates do not prescribe deleting the models, weakening a valid theorem, or abandoning the project. They identify what is missing from the present argument. Several results already warrant preservation: the finite-model ordering, the corrected total-error theorem, the primitive sufficient condition, and the original array-specific sign certificate. The negative recommendation follows because those results do not yet establish a robust and sufficiently distinctive economic-methodological contribution at the level sought.

**Bottom line:** the new audit confirms that a positive adjustment premium can survive while the advertised opposite-risk-choice conclusion moves with the wealth representation. The paper must explain and control that distinction. In its present form I recommend rejection, rather than an exposition-only revision.

## Sources and reproducible evidence

Repository source links below are pinned to the reviewed manuscript, not to mutable revision labels. The new diagnostics refer to files in this review directory.

- **M0:** [Revision index](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/REVISION_INDEX.md), [R7 main entry point](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/ECTA_R7.tex), and [response to R6](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/revisions/2026-09-16-r7/response_to_referee.md).
- **M1:** [Comparative oracles and total error](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/revisions/2026-09-16-r7/paper/04e_comparative_oracles.tex), especially the ordering, work/storage, literature, total-error and final cascade paragraphs.
- **M2:** [Primitive option and tensor certificate](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/revisions/2026-09-16-r7/paper/04f_economic_certification.tex).
- **M3:** [S.10 comparison proofs](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/revisions/2026-09-16-r7/paper/S10_comparison_proofs.tex).
- **M4:** [S.11 economic proofs and arithmetic account](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/revisions/2026-09-16-r7/paper/S11_economic_proofs.tex), especially S.11.3–S.11.4, supplement pp. 26–28.
- **M5:** [R7 evidence discussion](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/revisions/2026-09-16-r7/paper/05c_r7_evidence.tex), included Tables XVI–XVIII, main pp. 38–40, and [executed summary](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/revisions/2026-09-16-r7/execution_summary.md).
- **M6:** [Inherited approximation theorem](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/revisions/2026-09-16-r6/paper/03_approximation.tex).
- **M7:** [Stopped preference economy](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/revisions/2026-09-16-r6/paper/04_preferences.tex) and [risk-frontier analysis](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/revisions/2026-09-16-r6/paper/04d_risk_frontier.tex).
- **C1:** [Regional decision implementation](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/replication/r7/decision.py) and [author decision results](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/replication/r7/output/decision.json).
- **C2–C3:** [Kernel/menu construction](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/replication/r5/contracts.py) and [transition/interpolation construction](https://github.com/TrillionniumFoundation/NBO/blob/fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17/replication/r4/solver.py).
- **H1:** [Preceding directional R7 report](https://github.com/TrillionniumFoundation/NBO/blob/bfba0168a58b35507e37183147ecd2249de65a7c/reviews/2026-09-16-econometrica-r7-directional/referee_report.md), including its action-menu audit, wealth-only finding, moment identity, and links to the earlier R7 reports. These historical files are preserved by this review's parent.
- **D1:** [New diagnostic results](diagnostic_results.json): all 120 class values, both-regime comparisons, corner feature accounting, author-check rerun results, and source identities.
- **D2:** [Reviewer spatial driver](reviewer_spatial_both_regimes.py): unchanged common menus, explicit frozen-proposal prolongation, separate Bellman optimization and direct selected-policy replay.
- **D3:** [Core-check wrapper](reviewer_core_checks.py), [reproduction instructions](README.md), and [review manifest](review_manifest.json).
- **L1:** Quatmann, Tim, Christian Dehnert, Nils Jansen, Sebastian Junges, and Joost-Pieter Katoen (2016), *Parameter Synthesis for Markov Models: Faster Than Ever*, [arXiv:1602.05113v2](https://arxiv.org/abs/1602.05113v2), Sections 2.1–2.2 and the parameter-lifting development. Primary text checked, including the reward/MDP definitions.
- **L2:** Junges, Sebastian, Erika Ábrahám, Christian Hensel, Nils Jansen, Joost-Pieter Katoen, Tim Quatmann, and Matthias Volk (2024), *Parameter Synthesis for Markov Models: Covering the Parameter Space*, **Formal Methods in System Design**, 62, 181–259, [publisher article](https://doi.org/10.1007/s10703-023-00442-x), including the expected-reward extension in Section 7.4.
- **L3:** Heck, Leon, Tim Quatmann, Joël Spel, Joost-Pieter Katoen, and Sebastian Junges (2025), *Generalized Parameter Lifting: Finer Abstractions for Parametric Markov Chains*, [arXiv:2504.05965v2](https://arxiv.org/abs/2504.05965v2). Its model class is not assumed equivalent to the controlled finite-horizon reward problem.
