# Independent referee report: *Neural Bellman Operators*, R7

**Author:** Qian Qi  
**Date:** 16 September 2026  
**Recommendation:** **Reject in its present form for Econometrica.**  
**Manuscript reviewed:** `revision/econometrica-r7-2026-09-16`, commit `fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17`  
**Manuscript tree:** `cdc8e227881d5e95a8740c4f77298f73a0b9399d`  
**New review branch:** `review/econometrica-r7-independent-2026-09-16-fbfbf90`  
**Historical-review base:** `3b40e6813a2b56d88b454f5a164a648fb035d0f3`

This is an owner-commissioned, external-referee-style advisory report, not an appointment by Econometrica or an editorial decision. It assesses the manuscript rather than the author's ability to develop the research. A negative recommendation is not a claim that the research program cannot succeed.

## 1. Version identification and editorial assessment

The distinction between a new branch and a new manuscript matters in this case. At both repository inspections for this review, `revision/econometrica-r8-2026-09-16` pointed to `3b40e6813a2b56d88b454f5a164a648fb035d0f3`, the existing R7 review head. Its revision index still identified R7; it contained no new R8 manuscript. The latest deposited manuscript was therefore R7 at the immutable commit above. This report is a new independent assessment of that manuscript, extending rather than overwriting the existing R7 report. It does not invent an eighth revision or attribute new author responses to an unchanged tree.

R7 makes real progress. The localized-count ordering, the distinction between upper-oracle compression and certificate sharpness, the total coefficient-error bound, the autonomous refinement experiment, the primitive option inequality, and the joint-region class-value certificate are substantive improvements. I found no algebraic counterexample to the new finite-model ordering, primitive inequality, or tensor-sign construction under their stated hypotheses. The report should not be read as reviving the already repaired assertion that a generic welfare tolerance certifies an arbitrarily small risk difference.

Nevertheless, the paper still fails at the point where computational accuracy is supposed to support an economic conclusion. My principal new result is a fixed-calendar spatial test: with eight decision dates and the same common action menu, the no-adjustment risk ranking changes sign at a corner of the advertised region when the state grid is refined. Unlike the earlier report's time-refinement experiment, this comparison does not change the number of opportunities to act. A separate local calculation identifies a substantial, control-dependent interpolation contribution to preference-state variance. These findings do not falsify the certificate for the original stored arrays. They do undermine the scientific interpretation of that particular certified array problem as the paper's main economic payoff.

The computational contribution also remains insufficiently integrated with that payoff. The compressed oracle has a genuine local timing advantage, which I credit. But the principal economic certificate uses the sharper count construction, and the previous review's matched full-target certificate survives removal of neural proposals. The paper needs to establish a consequential role for its distinctive construction in obtaining a robust economic answer, not merely place a correct compression result beside a numerically fragile economic example.

## 2. What was examined and actually executed

I consulted the 45-page R7 main manuscript and 29-page supplement, their source entry points and relevant inherited sections, the R7 response to R6, historical reports, and the numerical programs and deposited evidence. The new comparison and economic proofs, the finite-target transition construction, and the regional decision calculation received the closest examination. Selected equation and table pages were visually inspected. This is not a claim to have independently re-proved every inherited result.

The complete source and executed output were obtained from Actions run `35063710310`, artifact `10433863234`. The downloaded ZIP's SHA-256 was `b0bcb8542760adffae90e3ffff7ad61d0fe5b49e0b93e0f66a05eeea170d51c2`. Reconstructing the final source and evidence snapshot produced exactly the manuscript tree stated above. All 27 authored-source inventory entries matched. The final-commit record matched the manuscript commit, rather than merely the earlier workflow-triggering commit. No tracked author file was changed during the checks.

Three classes of execution are distinguished in the accompanying programs and `diagnostic_results.json`.

First, I reran the author's 96-small-model, 480-parameter-check comparison suite, the primitive-family calculation, and the deposited tensor-coefficient replay. The count replay discrepancy was at most `1.7763568394002505e-15`; the minimum chord-minus-count coefficient was `-2.220446049250313e-16`, consistent with roundoff; the largest tested ratio to the total coefficient-error bound was `0.5534812664972152`. The deposited regional bounds replayed with zero discrepancy. These are implementation checks, not replacements for proofs.

Second, I wrote a separate common-menu Bellman maximization and selected-policy reevaluation driver for three spatial grids at the same eight dates. Across the four corners and center of the region, both adjustment regimes and both first-risk classes were evaluated. This gives 30 regime/parameter/grid comparisons and 60 class values. The largest selected-policy replay discrepancy was `2.220446049250313e-15`. The sparse continuation backend was checked against the author's original weighted-gather implementation. The transition law itself is reused from the author; this is not an independently implemented diffusion solver.

Third, I calculated pre-interpolation and post-interpolation moments from the actual kernel weights at an interior state, and checked an independent analytical identity for the interpolation variance. This is a local consistency diagnostic, not a numerical bound on the entire economic value function.

I did not rerun historical neural training, the full author timing contest, or the previous review's neural-free regional construction. Their results are identified below as deposited author or prior-review evidence. The larger spatial run initially exceeded this session's 4-GiB memory limit. It was completed using the identical double-precision sparse entries in read-only disk-backed arrays. This implementation change is disclosed in the replication instructions; no cross-machine speed comparison is inferred from reviewer runtimes.

## 3. Disposition of the inherited objections

| Issue | Assessment of R7 |
|---|---|
| Unmatched localization in the earlier count comparison | Repaired. R7 compares common intervals, policies, and cells and proves the relevant ordering. |
| No positive computational case | No longer an accurate description. The autonomous chord arm is faster at the reported common tolerance. The unresolved issue is the breadth and economic relevance of the gain. |
| A primitive prediction rather than only an option identity | Supplied in a separate two-stage family. Its connection to the stopped portfolio mechanism remains unestablished. |
| Generic welfare accuracy used to claim a strict regional risk ranking | Repaired for the declared finite target. The class-specific tensor certificate is genuine. |
| Robustness of that economic ranking | Not resolved. The new fixed-date spatial result strengthens the earlier concern without relying on a change in decision frequency. |

The recommendation below respects these repairs. It is not based on an allegation that R7 has no theorem, no executed comparison, or no valid finite-model certificate.

## 4. R7-I-F1: the headline ranking fails a fixed-calendar spatial check

**Severity: publication-blocking economic robustness issue, not a counterexample to the finite-array certificate.**

**Locations:** Main Section 8.13 and Table XVIII, pp. 39–40; `revisions/2026-09-16-r7/paper/05c_r7_evidence.tex`, lines 15–26; `S11_economic_proofs.tex`, lines 44–68; `replication/r7/decision.py`; this review's `reviewer_spatial_checks.py` and `diagnostic_results.json`.

The manuscript certifies opposite first-risk rankings with and without deliberate adjustment throughout

\[
(\lambda,d)\in[0,0.25]\times[0.4,0.45]
\]

at initial state `(u,X)=(2,1.25)` and adjustment cost `k=2`. Its adjusted-class difference has a positive lower bound of `6.888728805714623e-5`; its no-adjustment difference has a negative upper bound of `-5.2993655605010966e-5`. The per-class arithmetic allowance is `3.797650002493679e-9`. I accept what this establishes for the stored eight-date, 1,617-state target.

The existing R7 report found a sign change when the number of dates increased while the spatial grid remained fixed. That experiment is informative, but it jointly changes decision frequency, step length, interpolation behavior, and the stopped-transition approximation. A natural author response would be that eight dates are an economically intended calendar rather than merely a numerical parameter. I therefore hold that calendar fixed.

The new experiment retains the physical horizon of one, all eight decision dates, financial and preference primitives, operating boundaries, settlement function, endpoint shock generators, and the entire union of the two published common action meshes. The common menu has 1,565 actions on every grid. Frozen neural proposals are excluded consistently; simply calling the author's `include_neural=False` factory would also remove one historical mesh, so the reviewer program constructs the union explicitly. Only the spatial representation changes: `33 x 49`, `49 x 73`, and `65 x 97` states. The initial state is exactly a node on each grid; no interpolation of the reported initial values is needed. The finest grid is a nested refinement of the original grid.

At the same corner `(lambda,d)=(0.25,0.45)`, the results are:

| State grid | Adjustment available: positive minus nonpositive first-risk value | No deliberate adjustment: positive minus nonpositive first-risk value |
|---|---:|---:|
| 33 x 49 | `+3.245296361471528e-4` | `-5.300125090501595e-5` |
| 49 x 73 | `+3.532611320811174e-4` | `-1.3633353268538428e-5` |
| 65 x 97 | `+4.297268480522032e-4` | `+7.203016004175833e-5` |

Thus the finer eight-date common-menu economy has the same sign in both adjustment regimes at this corner. The opposite-ranking statement is not stable under this spatial change. The movement in the no-adjustment difference from the first to the last grid is about `1.2503e-4`, measured in the same utility units as the decision margin. Small replay errors do not explain that movement.

The remaining inspected points are not hidden. The four corners and center are all recorded. For example, at `(0.25,0.4)`, the no-adjustment difference moves from `-1.6815344568577029e-4` to `-3.860557281842869e-5`; at the center it moves from `-2.0932696117825778e-4` to `-8.304979788120725e-5`. Those signs remain negative. The finding is not that every preference-adjustment reversal disappears, nor that the limiting diffusion necessarily has the finest-grid sign. It is that the advertised whole-region qualitative conclusion is sensitive to spatial representation even at an unchanged decision calendar.

These are optimized finite-menu point comparisons, not newly constructed regional upper/lower tensors. They are not a diffusion-convergence proof. Also, the author's original target contains three additional neural proposals, whereas this comparison uses the identical common menu across all grids. That distinction must remain explicit. It does not make the experiment an unrelated model: the common-grid baseline reproduces the previous mesh-only values, and the previous report separately established that neural-free lower policies still certify the original region against the original full-target upper tensors. The latter is inherited evidence, not a new calculation claimed here.

A satisfactory response must explain and control this spatial sensitivity. It is not enough to repeat that the original theorem conditions on stored arrays, or to defend eight decision dates as a primitive. Neither answer addresses a change in spatial representation at those same dates. The author should either provide decision-level spatial/action/transition approximation control for the intended economy, or substantively justify the discretized state transition itself as an economic primitive and examine economically meaningful perturbations of that primitive. Moving the favorable rectangle without explaining its movement would not resolve the issue.

## 5. R7-I-F2: interpolation adds substantial, control-dependent preference variance

**Severity: major numerical-mechanism issue requiring a substantive diagnosis.**

**Locations:** `replication/r4/solver.py`, lines 35–66; `replication/r5/contracts.py`, class `Kernel`; inherited `revisions/2026-09-16-r6/paper/03_approximation.tex`, lines 13–46; R7 Supplement S.11.4; this review's `reviewer_kernel_moments.py`.

The preceding sign movement should not be treated as an unexplained demand for ever-finer grids. There is a concrete local discrepancy in the implemented stochastic mechanism. Consider the interior state `u=2`, step `h=1/8`, and zero deliberate adjustment. The preference shock in the pre-interpolation quadrature is

\[
Y=u\pm a,\qquad a=\sigma_u\sqrt h,
\qquad \sigma_u=0.05.
\]

Its variance is `sigma_u^2 h = 0.0003125`. On the original preference grid, spacing is `Delta_u=0.05`, so `a<Delta_u`. Positive linear interpolation places probability `a/(2 Delta_u)` at each neighboring grid node and the remaining probability at the center. Consequently,

\[
\operatorname{Var}_{\rm grid}(u')=a\Delta_u,
\qquad
\frac{\operatorname{Var}_{\rm grid}(u')}
     {\operatorname{Var}_{\rm raw}(Y)}
=\frac{\Delta_u}{\sigma_u\sqrt h}
=2.828427124746\ldots.
\]

The actual normalized kernel weights reproduce this identity. Discounting is divided out, and the selected interior step has no killing; the result is not a row-mass or boundary artifact. Bilinear interpolation in the two-state problem has the same preference marginal. Both endpoint correlation laws give this preference-variance ratio.

At fixed eight dates and zero adjustment, the ratios on the three tested grids are:

| Preference/wealth grid | Post-interpolation preference variance divided by raw quadrature variance |
|---|---:|
| 33 x 49 | `2.8284271247462076` |
| 49 x 73 | `1.8856180831641363` |
| 65 x 97 | `1.4142135623731038` |

There is also an endogenous numerical channel. At the original grid and `theta=0.2`, the preference drift over a step is `0.025`. The two raw preference endpoints lie between the same adjacent nodes. Interpolation preserves the mean but yields variance `0.000625`, twice the raw variance, rather than 2.828 times it. The artificial variance therefore depends on the control. On the `65 x 97` grid, the zero-adjustment and `theta=0.2` cases both give a ratio of approximately 1.414, because the latter drift shifts the mean by exactly one preference-grid spacing. The control dependence of numerical noise itself changes with grid alignment.

This is not a complaint that interpolation is inherently illegitimate. It is an exact description of the finite kernel that is being certified. More generally, for positive interpolation between neighboring nodes `l(Y)` and `r(Y)`, the mean is preserved and

\[
\operatorname{Var}_{\rm grid}(u')-
\operatorname{Var}_{\rm raw}(Y)
=\mathbb E[(Y-l(Y))(r(Y)-Y)]\geq0.
\]

The program checks this identity against the author's kernel, including nonzero adjustment. It isolates a numerical variance contribution relative to the raw quadrature; it does not require a claim that the quadrature itself exactly represents a stopped diffusion.

This calculation also sharpens the interpretation of the earlier temporal test. At a fixed preference spacing of `0.05` and zero adjustment, the variance-inflation ratios at 4, 8, 16, and 32 dates are 2, approximately 2.828, 4, and approximately 5.657. Time refinement alone on that grid is not a local-consistency path. In the one-cell regime the induced variance rate is `sigma_u Delta_u / sqrt(h)`, which does not approach `sigma_u^2` at fixed spacing. A generic sufficient condition for vanishing interpolation contribution to local variance rate is `Delta_u^2/h -> 0`, since the variance increment is bounded by `Delta_u^2/4`; a full convergence argument must also treat wealth, controls, killing, and rewards.

The manuscript's own error theorem has a place for this discrepancy: its operator-error term includes transition and interpolation errors. The problem is not that this term is absent from the theorem. The problem is that the regional economic calculation bounds arithmetic relative to stored arrays without operationally controlling that term for the economic target. Monotonicity and a small arithmetic allowance are not substitutes for consistency or decision-level model error.

I do not claim that the local variance discrepancy alone causes the sign reversal in Section 4. Wealth interpolation, boundary behavior, and continuation-policy changes can contribute. In particular, both first-risk classes may share the same first preference action while differing later. Establishing the causal contribution requires further decomposition. The present evidence establishes a sizable, behavior-dependent numerical mechanism that the economic interpretation must confront. A useful repair would separately examine preference-grid, wealth-grid, and stopped-transition effects, and then verify the decision on a justified joint approximation path. Simply giving the original array calculation more digits would be irrelevant.

## 6. R7-I-F3: valid compression is not yet a compelling integrated contribution

**Severity: major contribution and attribution issue.**

**Locations:** Abstract and Introduction; Main Section 6.3, Proposition 12 and Theorem 13; Tables XVI–XVIII; `04e_comparative_oracles.tex`, lines 24–69; `replication/r7/output/adaptive.json`; previous R7 report, Sections 5–6.

The positive computational result deserves explicit recognition. In the deposited autonomous experiment, at the common `10^-3` tolerance, the chord arm uses 18 anchors and 73.405 seconds, count uses 11 anchors and 115.377 seconds, and the cascade uses 11 anchors and 127.732 seconds. These are author-run times, not reviewer-machine comparisons. Count has a sharper certificate and fewer anchors; chord is faster in this run. R7 therefore does demonstrate a useful local tradeoff.

The theoretical accounting is also materially improved. The stated upper propagation uses `4H-6` action-wide kernel applications for the correction versus `H(H+1)-2` for the specified cached count recursion. The total coefficient bound includes first-order policy-bank error rather than incorrectly inferring a second-order bank rate from the correction. These results should be retained.

Their importance is not yet established at the level claimed by the overall paper. The autonomous experiment is one short horizon, one state/action target, one contract, and one tolerance. Small-model operation counts at other horizons do not establish total-cost scaling in the economic application. The common lower-policy coefficient bank still has order `m S H^2` storage, and endpoint optimization, transition storage, subdivision, and policy evaluation remain. A saving in one upper component need not be a saving in the total computation at the accuracy required for a strict economic decision.

More importantly, the economic and computational arguments still do not depend on each other in a persuasive way. The joint-region economic certificate is executed using localized count uppers, not the compressed chord. The previous R7 review constructed neural-free lower policies against the unchanged original full-target uppers and obtained adjusted bounds `[6.88872246050138e-5, 3.245372998448897e-4]` and no-adjustment bounds `[-3.6948485968774585e-4, -5.2993655605010966e-5]`. That is a matched regional result, not merely a favorable mesh sample. Its source is the preserved previous report and diagnostic files; I have not represented it as a newly rerun experiment.

I do not require a neural architecture to win by definition, or demand a cosmetic change of title. Nor does a valid general certificate become uninteresting because non-neural policies can enter it. The substantive question is whether an identifiable new ingredient enables a robust and important economic comparison at an advantageous total cost. At present, the main economic finding neither requires the neural proposals nor uses the compressed upper construction for its executed certificate, while the compression demonstration does not address the model-sensitivity problem just identified.

A convincing computational extension would compare total cost at a decision-level error requirement on the economically justified targets, with common constraints and strong structural alternatives. It should expose settings where count's reduced anchor demand wins as well as settings where compressed propagation wins, and include at least a modest horizon/state/action/tolerance frontier. The relevant outcome is a robust economic decision per unit of total resource, not an isolated kernel-call ratio.

The closest literature comparison should also be sharpened without making unsupported equivalence claims. R7 properly discusses scalar optimistic linear support and parameter lifting. Alegre, Bazzan, and da Silva (2022) already combine optimistic linear support, successor features, and generalized policy improvement. Heck et al. (2025) study generalized parameter lifting and a big-step transformation that tightens abstractions by handling repeated-parameter dependence differently. The latter concerns parametric Markov-chain verification, not automatically the same controlled reward problem. The author should articulate what its endpoint/count compression preserves that those constructions do not, and what extension to the present reward/control setting is genuinely new. Merely listing another citation is not a novelty argument. Conversely, I have not proved that their method dominates or subsumes NBO.

## 7. R7-I-F4: the primitive economic result does not yet explain the principal economy

**Severity: major economic-content issue.**

**Locations:** Main Proposition 16 and Sections 7.2–7.3; `04f_economic_certification.tex`, lines 1–44; Supplement S.11.1–S.11.3; inherited `04_preferences.tex` and `04d_risk_frontier.tex`.

The primitive option bound is correct and more informative than an envelope identity. Global concavity of CRRA utility in the preference index gives a lower quadratic bound and an upper tangent bound. Subject to feasibility of the lower trial, these produce `g_sigma^2/[2(k+M_sigma)] <= Omega_sigma <= g_sigma^2/(2k)`. A positive difference between the positive-class lower bound and negative-class upper bound yields the stated contract-threshold shift. My replay reproduced the primitive-family checks.

The unresolved issue is explanatory reach. In the two-stage specialization, the consumption lotteries and duration difference are primitives. In the stopped portfolio economy, consumption, stopping, exposure, and effort are jointly endogenous. The numerical primitive family also uses adjustment costs between 20 and 80, while the principal finite economy uses `k=2`. The manuscript candidly says that this is neither a calibration nor an approximation of the full economy. That admission is appropriate, but it leaves a gap between the valid sufficient condition and the mechanism supposedly demonstrated by the headline application.

The option identity `Delta_adj - Delta_fixed = Omega_positive - Omega_nonpositive` identifies the accounting quantity that changes a ranking. It does not identify why the relative option is positive, how much comes from duration versus consumption exposure, or how robust the result is to the implemented transition mechanism. The new variance calculation makes that last question concrete: the numerical representation changes an aspect of the preference process in a control-dependent way. The paper must distinguish economic preference formation from numerical effects associated with representing that formation.

The required bridge is not another toy example selected to satisfy a sufficient inequality. It is an informative decomposition or a theorem with usable bounds in the main economy. For example, the author could bound the relevant exposure and curvature terms for economically justified class policies, quantify duration and settlement contributions, and show which inequalities survive approximation changes. An adverse result should remain visible rather than be removed. The point is to learn when the mechanism operates, not simply to produce a region where the signs differ.

The manuscript already recognizes that state-dependent cardinal normalization and settlement affect behavior. I therefore do not treat arbitrary preference-index-dependent utility renormalizations as innocuous invariances that the model must satisfy. Such transformations change this model. The legitimate request is economic justification and sensitivity of the chosen primitives, not invariance to every different preference-formation objective.

Finally, positive versus nonpositive *first portfolio exposure* is not a general ordering by risk. In the inspected common-menu problems, the positive and nonpositive first positions are `0.8` and `-0.5`; later positions are unrestricted. The paper should consistently keep the choice-class interpretation, rather than allowing a signed-exposure comparison to be read as a universal proposition that more risk is desirable when preferences are adjustable.

## 8. Presentation and revision priorities

The presentation is considerably more disciplined than in earlier rounds, but its logical hierarchy should be clearer. Arithmetic error, upper-information slack, feasible-policy error, spatial/action approximation, transition-law construction, and economic-specification sensitivity are different objects. The principal decision table should identify all of them, including those not bounded. Nanoscopic arithmetic allowances should not be allowed to dominate the reader's impression of economic precision.

The disclosed exploratory selection of the rectangle is not, by itself, a statistical multiple-testing violation: no sampling-based significance claim is made. It is a representativeness issue. A map of certified, uncertified, and unstable decision regions under declared numerical and economic perturbations would be more useful than another isolated favorable rectangle. The map should distinguish absence of a certificate from a proved opposite sign.

A small textual inconsistency remains: the final paragraph of `04e_comparative_oracles.tex` says the ensuing comparison does not represent an executed autonomous cascade timing contest, while the later text and Table XVII report one. Correct it, but do not confuse that edit with a substantive response.

The next scientific priorities are, in order: resolve the fixed-calendar spatial sensitivity; account for the artificial, control-dependent variance and other transition approximations; establish a robust decision-level computation with a meaningful total-cost comparison; and connect the primitive mechanism to that validated economic result. This does not require deleting the recursive-utility, temporal-self, or competition material. It does require explaining which parts support the main contribution and which are separate scope demonstrations.

## 9. Recommendation

I recommend rejection in the present form. The strongest criticism is not that the paper lacks correct mathematics. It is that a well-verified finite-array answer is still being asked to bear more economic weight than the validation of the underlying numerical economy supports.

The new spatial experiment strengthens the previous review in a specific way: keeping the eight-date calendar fixed does not stabilize the advertised opposite-ranking conclusion. The local moment audit identifies a substantial and control-dependent numerical mechanism that must be disentangled from the economic one. At the same time, the paper's positive compression result and primitive inequality remain valid within their respective scopes. A stronger paper could build on them, but another round of narrower disclaimers, extra administrative evidence, or additional digits on the original target would not suffice.

## 10. Sources and replication guide

All author-source locations above are pinned to manuscript commit `fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17`; all prior-review attributions refer to commit `3b40e6813a2b56d88b454f5a164a648fb035d0f3`.

Primary manuscript and numerical sources: `ECTA_R7.tex`; `SUPP_R7.tex`; the PDFs and source files in `revisions/2026-09-16-r7/`; `replication/r7/core.py`, `decision.py`, `adaptive.py`, `validate.py`, `primitive.py`, and their deposited outputs; `replication/r5/contracts.py`; `replication/r4/solver.py`. The inherited finite-horizon operator-error account is in `revisions/2026-09-16-r6/paper/03_approximation.tex`. The previous R7 report and its diagnostics are preserved at `reviews/2026-09-16-econometrica-r7/`.

New evidence: [diagnostic_results.json](diagnostic_results.json), [reviewer_spatial_checks.py](reviewer_spatial_checks.py), [reviewer_kernel_moments.py](reviewer_kernel_moments.py), [reviewer_author_replay.py](reviewer_author_replay.py), and [README.md](README.md). The programs make their reuse of author kernels explicit and write only to requested output paths. The README records commands, computational scope, and the memory-backed/disk-backed distinction.

Selected primary literature checked for this report:

Alegre, L. N., A. L. C. Bazzan, and B. C. da Silva (2022): “Optimistic Linear Support and Successor Features as a Basis for Optimal Policy Transfer.” *Proceedings of the 39th International Conference on Machine Learning*, PMLR 162, 394–413. [Proceedings article](https://proceedings.mlr.press/v162/alegre22a.html).

Heck, L., T. Quatmann, J. Spel, J.-P. Katoen, and S. Junges (2025): “Generalized Parameter Lifting: Finer Abstractions for Parametric Markov Chains.” [Author manuscript, arXiv:2504.05965v2](https://arxiv.org/html/2504.05965v2). Cited as a relevant dependence-abstraction comparison, not as an established equivalent of the present controlled reward construction.
