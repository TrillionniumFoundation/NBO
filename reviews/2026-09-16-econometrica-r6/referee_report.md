# Referee report: Neural Bellman Operators — revision R6

**Review date:** 16 September 2026  
**Manuscript:** *Neural Bellman Operators*, Qian QI  
**Reviewed branch:** `revision/econometrica-r6-2026-09-16`  
**Reviewed complete revision:** `24011fef6da09bc05dc79946a3c1779e1fe7d8a8`  
**Reviewed Git tree:** `36709be3522fb7e29e7bfc45abfc6305a84b203d`  
**Reachable execution-source commit:** `0727e4fec022c3aa8cff0363db918ad831431c6c`  
**Previous report:** R5 review at `0d0e79a52e540bd0647801ce316f051d667c6797`  
**Review branch:** `review/econometrica-r6-2026-09-16-24011fe`  
**Recommendation:** **Reject in its present form for Econometrica.**

This is an owner-commissioned, external-style advisory assessment against the standards of an Econometrica referee. It is not an appointment by the journal or an editorial decision. The recommendation concerns R6, not the possibility of developing the research further.

## Overall assessment

R6 makes genuine progress. The corrected transition-law chord is a valid finite-horizon supersolution construction under the stated assumptions. The fixed-policy Bernstein representation and switching argument provide an operational continuum certificate. The author has also responded seriously to the previous adverse computational comparisons: the reusable structural QP is now included, the negligible value contribution of neural proposals to the reward-bank tolerance is acknowledged, and the no-deliberate-adjustment economy is actually solved rather than discussed only verbally. These are substantive repairs, not merely a longer response letter. [M1], [M2], [M3], [M4], [M5], [H1], [H2]

Nevertheless, the revised paper still does not establish a sufficiently important incremental computational or economic contribution. Its main new comparison is particularly problematic. Table XIII places an adaptively localized corrected-chord construction with 17–19 anchor policies beside a single global count-information bound with three policies. I show below that, on the **same anchor interval**, the count-information recursion already described in the paper produces upper coefficients that are **no larger than the corrected-chord coefficients**. With the same lower policies and Bernstein cells, its certificate is therefore no worse. This is a general comparison theorem, not an extrapolation from a few favorable parameter samples.

I also execute that matched comparison in the deposited economy. For all three reported contracts, keeping every original anchor, lower-policy array, state, date, and subdivision cell, localizing the count relaxation reduces the reported uniform bound by approximately **18.87%, 23.86%, and 53.71%**, respectively. This does not refute Theorem 10. It does invalidate using the unmatched global comparator to establish a distinctive sharpness advantage for the corrected construction. The latter may be a useful cheaper compression of the count recursion, but that is a different contribution and requires a work–accuracy comparison the paper has not supplied. [M2], [M4], [D1], [D2]

The economic additions are similarly more credible than before but less powerful than their positioning suggests. The duration–effort ratio is an envelope/implicit-function identity conditional on the relevant active-policy moments. The preference-option decomposition is an accounting identity for nested feasible sets. The matched experiment establishes an adjustment-availability effect on a particular finite-model risk ranking. It does not yet explain, in economically interpretable primitives, when that effect must occur or why it is quantitatively consequential. Moreover, the new transition-law welfare certificate is not used to certify the new risk-frontier conclusions. The computational and economic contributions remain adjacent rather than demonstrably integrated.

My recommendation is not based on an alleged failure of the build, an invented error in the cross-term identity, or repetition of objections that R6 has addressed. It is based on the remaining contribution problem and the new matched countercomparison.

## Review basis and reproducibility

I examined the current 38-page main manuscript, the relevant inherited proofs and numerical specifications, the new supplement material in the 23-page supplement, the R5 report, the R6 response, and the executable sources and generated records for the new results. The theorem and numerical-table pages were also inspected as rendered PDF pages, including main pp. 16–18 and 31–32. I do not claim to have independently rederived every inherited continuous-time or game-theoretic result.

The complete R6 source/evidence bundle was retrieved from GitHub Actions run `35056958533`, artifact `10431013745`. Its downloaded ZIP has SHA-256 `e555694953fbfca02a871d1990b26ad561aa238f8bec021ca5765899cd960b01`. Extracting its source archive and reconstructing the Git tree produced **exactly** the reviewed tree above. All 60 entries in the R6 source inventory match their declared SHA-256 hashes. Subsequent diagnostics left the tracked author files unchanged. These identity checks establish which submission was tested; they are not scientific validation by themselves. [E1], [E2]

At the start of this review, the branch contained source commit `0727e4f` while its workflow was still producing evidence. The complete evidence commit `24011fe` arrived during the review. The intervening change adds the executed outputs, generated tables, logs, and PDFs without changing the theory or executable source. This report reviews that completed revision. The initial temporary absence of evidence is **not** counted as a defect of the reviewed submission.

There are three distinct kinds of execution evidence here. First, `reviewer_diagnostics.py` independently implements small finite MDPs, the two upper constructions, fixed-policy evaluation, and coefficient certificates. Second, `matched_local_count.py` independently implements local count optimization and replays the certificate on the full author economy, while deliberately reusing the author's kernel executor and deposited policy bank. Third, the author's small-model `unit_tests.run` was rerun with its output writer intercepted; this is a rerun of author code, not an independent implementation. The distinctions are preserved in the JSON records. [D1], [D2], [D3]

The review does **not** perform a fresh full neural-training sweep, a new autonomous anchor-discovery experiment, a diffusion convergence proof, or a new timing contest between fully optimized solvers. The resource-QP and mechanism numbers discussed below are inspected deposited R6 results, not newly measured reviewer-machine replications of those entire workloads.

## 1. What R6 has resolved

The exact-scalar support comparison is now explicit. The initial-distribution objective uses three anchors, whereas simultaneous state/date coverage uses 47; their guarantee scopes are correctly separated. The adjacent-policy/full-line equivalence is a useful exact-oracle clarification, not a claim that general action-value GPI and policy-action switching are identical. The missing optimistic-linear-support connection has been addressed. [M1], [M4], [L1], [L2]

The stronger resource baseline is now part of the main text. At 2,048 queries, the deposited R6 totals are approximately `3.66747814` seconds for the learned arm and `0.143247756` seconds for the reusable QP, with the QP's complete-tree gap approximately `0.000677426363`. The author no longer treats failure of a fitted quadratic continuation as evidence against the exact parametric QP. That correction closes the previous attribution error; it does not create a positive learned-computation advantage. [M4], [E1]

The mesh-only bank is evaluated against the unchanged full target and still attains the reward-interval tolerance: `0.0009306975845364551`. R6 correctly distinguishes a small value contribution from an absence of neural action selections. I do not repeat the false charge that the neural proposals are never selected. [M4], [E1]

The new adjustment restriction is meaningful. It fixes deliberate adjustment to zero at all dates and states while retaining preference shocks and the other declared primitives. In the deposited finite economy, the positive/nonpositive risk ranking differs between the two arms at several contracts. Thus the R5 concern that the paper had not separated adjustment availability from a generic duration incentive has received an actual within-model counterfactual answer. The remaining questions are the depth, robustness, and certified economic use of that answer, not whether the restriction was executed at all. [M3], [M4], [C3]

Finally, I find the central proofs in Section 6 sound within their declared finite-model scope. The signed cross term has the correct orientation; the same-action restriction inside the correction is preserved; the conditional-count representation does not give future information to the feasible policy; and the minimum/maximum ordering in the coefficient certificate is conservative in the correct direction. The additional correction's second-order bound is explicitly not a second-order bound on total policy-bank loss. These distinctions should be retained.

## 2. Major findings

### R6-F1 — The principal transition-law countercomparison confounds localization and policy-bank coverage

**Severity: decisive comparative-evidence objection; new general result and full-model execution.** Relevant locations: Section 6, especially Theorem 10, Corollary 11, and the final count-information paragraph; Section 8.10; Table XIII on p. 31; Supplement S.9.1. Source anchors are `04c_kernel_transfer.tex:73–116`, `05b_incremental_evidence.tex:25–35`, and the two transition programs. [M2], [M4], [S1], [C1], [C2]

The reported count bound is real and valid for the particular construction used. The problem is what it can establish. `transport.py` forms one count-information upper polynomial over `[0,1]`, paired with policies solved at `0`, `0.5`, and `1`. `kernel_certificate.py` instead repeatedly splits intervals, solves new endpoints, and pairs each interval with its endpoint policies. Table XIII compares both the upper construction **and** its localization **and** its feasible-policy coverage at once.

The missing matched comparison is especially consequential because it admits a clean ordering. On an arbitrary original anchor interval `[a,b]`, write

$$
\lambda=a+(b-a)t,\qquad
(R_\lambda^u,K_\lambda^u)=(1-t)(R_a^u,K_a^u)+t(R_b^u,K_b^u).
$$

Now apply the paper's count-informed recursion to the two endpoint operators `a` and `b`, rather than once to `0` and `1`. Denote the resulting coefficients by `W^I_{n,j}`. If `h=N-n`, the corrected chord has coefficients

$$
U^I_{n,j}=\left(1-\frac jh\right)v_n^a+\frac jh v_n^b
 +\frac{j(h-j)}{h(h-1)}M_n
$$

for `h>=2`, with the natural terminal and one-period definitions. Under the same endpoint-supersolution assumptions as Theorem 10,

$$
\boxed{W^I_{n,j}(s)\le U^I_{n,j}(s)\quad\text{for every }n,j,s.}
$$

Appendix A supplies the proof, including the endpoint and short-horizon cases. Both resulting polynomials are upper bounds on the **same original**, fixed-parameter optimal value. Bernstein subdivision preserves the coefficient ordering. Consequently, with the **same** lower-policy polynomials and closed cells,

$$
\epsilon_I^{\mathrm{local\ count}}\le\epsilon_I^{\mathrm{corrected\ chord}}.
$$

This is not a claim that the original controller observes a future regime count. The enlarged information structure is used solely to construct an upper bound, exactly as it is in the author's global comparator.

**Executed matched result.** I recomputed the local count upper recursion on all 51 deposited anchor intervals across the three contracts. The comparison retains the full 1,568-action target, all 1,617 states, eight decision dates, each interval's two original lower policies, and its eight Bernstein cells. The original corrected bounds are reproduced from their deposited coefficient arrays. No new anchor or easier target is introduced. [D2]

| Fixed contract `d` | Original anchors | Corrected bound, replayed | Local count bound, same bank/cells | Bound reduction |
|---:|---:|---:|---:|---:|
| 0 | 19 | 0.0009045733003105738 | 0.0007338463674633200 | 18.87% |
| 0.5 | 18 | 0.0008998289604379428 | 0.0006851026198662069 | 23.86% |
| 1 | 17 | 0.0009414120278261606 | 0.0004357448654037643 | 53.71% |

These are continuum coefficient certificates, not maximum losses over sampled parameters. The minimum corrected-minus-local-count coefficient across the matched calculations is `-1.1102230246251565e-15`, consistent with floating-point evaluation of the proved ordering. The mathematical ordering, rather than that tolerance test, is the general result. These remain ordinary double-precision numerical certificates in the same sense as the author's results.

A separate two-period example shows strictness transparently. At date zero, choose between states whose final success probabilities are `t` and `1-t`. The true date-zero value is `max(t,1-t)`. The corrected upper coefficients are `[1,1,1]`, whereas the count upper coefficients are `[1,0.5,1]`. At `t=0.5`, the true value is `0.5`, the corrected upper is `1`, and the count upper is `0.75`. With the same endpoint-policy bank and eight cells, the all-state/date certificates are `0.5` and `0.25`. This example changes transition probabilities, not merely a reward coefficient; it is not represented as a calibration of the portfolio economy. [D1]

**What this does and does not show.** Theorem 10 is not false. The global count column is not numerically misreported. Nor does the example show that local count recursion is faster. A corrected-chord construction uses a number of backward action-optimization layers linear in the horizon, whereas a count recursion has a triangular number of such layers. The latter can buy precision at additional work. Conversely, both methods also incur lower-policy evaluation and subdivision costs. The review has not compared their optimized end-to-end costs or autonomous anchor counts, and cross-machine times cannot establish that comparison.

The finding is that the paper has not identified the corrected construction's incremental benefit. Its own alternative, fairly localized and given the same policy bank, is sharper. A defensible contribution could be a **provably controlled, computationally cheaper compression** of that alternative. Establishing it requires a matched frontier of certificate size, action/kernel work, memory, and elapsed time, including anchor solves, coefficient evaluation, and subdivision. The negative control `t(1-t)` establishes that an uncorrected chord can fail; it does not establish the necessity of this particular correction among valid upper oracles.

### R6-F2 — A valid finite-MDP construction has not yet become a substantial computational contribution

**Severity: decisive contribution objection, not an allegation that nonneural guarantees are intrinsically uninteresting.** Relevant locations: Introduction and Conclusion; Section 6; the approximate-endpoint paragraph on p. 17; Sections 8.8–8.10 and Table XIII. [M1], [M2], [M4], [M5]

The central theorem is independent of a neural architecture. That is a strength if the intended contribution is a general theorem about certified parametric control. It is not evidence that the learned representation has solved a problem that conventional dynamic programming could not solve economically. Every demonstrated new anchor is obtained by exhaustive finite-action backward optimization. The feasible policy polynomials are then evaluated over the complete finite state grid. The neural endpoint extension requires a uniform one-sided residual upper bound over the same state/action target; no new executed case shows how obtaining that bound avoids the expensive global computation.

R6 is candid about these facts. The issue is therefore not another missing disclaimer. After conceding the QP and mesh countercomparisons, the paper needs a positive result supporting its new center of gravity: a nontrivial precision–work improvement, a useful reduction in certified oracle demand, a demonstrably harder economic computation enabled by the method, or a theorem with economic implications beyond the availability of a valid upper bound. Appendix A and the matched experiment identify exactly where that case now needs to be made.

The current scaling evidence does not make it. A library of `m` fixed policies stores order `m*S*H^2` value coefficients across all dates before compression, in addition to policy indices and transition information. This follows directly from summing `h+1` coefficients over the remaining horizons. The proposed scalar interval scheme also needs exhaustive action work for the endpoint solves and its upper correction. The conditional `O((b-a)^2)` statement controls the added cross-term correction; it neither controls the entire policy-bank error nor resolves the number of anchors needed when optimal actions change. The manuscript correctly says so, but offers no replacement complexity or scaling result that would establish the practical scope of the new certificate.

The literature comparison must also move beyond reward transfer and generic transition sensitivity. Quatmann et al. (2016) study regional verification for parametric Markov models using refinable bounds and parameter lifting. Their introductory two-toss example uses the same heads-then-tails obstruction behind `t(1-t)`. This does **not** establish that their theorems are identical to Theorem 10: specification, reward, topology, and policy assumptions require a careful comparison. It does establish that parameter-region certification and dependence across repeated transition parameters are an existing comparison class, not an obstruction addressed only by moving beyond successor features. [L3], [L4], [L5]

The needed analysis is substantive: distinguish which dependence the corrected construction retains, quantify what is lost by its compression relative to the localized count bound, and show what this buys relative to an appropriate regional method on a common target. A generic acknowledgment of robust control, or the statement that no exhaustive priority claim is made, cannot substitute for that comparison. I make no allegation of plagiarism and no unsupported claim that the precise corrected-chord formula has previously appeared.

### R6-F3 — The economic propositions organize the calculation but do not yet explain the mechanism in primitives

**Severity: major economic-contribution objection.** Relevant locations: Section 7, Propositions 12–13, equations (56)–(60), and Section 8.11 with Tables XIV–XV. Source: `04d_risk_frontier.tex:5–58`, `05b_incremental_evidence.tex:37–45`. [M3], [M4]

The new class-value construction is sensible. For positive and nonpositive first-risk classes,

$$
W_\sigma(d,k)=\max_{p\in\mathcal P_\sigma}\{B_p+dA_p-kC_p\}.
$$

On a regular active-policy cell, differentiating the difference of these envelopes and applying the implicit-function theorem gives

$$
\frac{d d^*(k)}{dk}=\frac{C_+-C_-}{A_+-A_-}.
$$

The result is correctly conditional and correctly credits envelope reasoning. But the formula does not itself establish either moment ordering. The hypothesis that every active positive-risk policy has at least `kappa` more duration than every active nonpositive-risk policy is already a strong restriction on the solved policy correspondence. The paper does not derive it from the consumption technology, adjustment law, return process, or liquidation contract, and explicitly does not verify it over an interval in the implementation. [M3], [L6]

Similarly,

$$
\Delta^{\rm adj}-\Delta^0=\Omega_+-\Omega_-
$$

follows by subtracting the definitions of the two option values. The reversal condition then rearranges that equality. This logic would apply to any nested expansion of a dynamic feasible set with the same two action classes. Labeling the additional choice preference formation does not give the identity a preference-specific prediction. The substantive question is why the relative option value has the relevant sign and magnitude in this economy.

The matched experiment provides one answer at one declared specification, and should receive credit for that answer. At `d=0.5`, the deposited finite-model class differences are about `+0.0002991993` with adjustment and `-0.0001356840` without it. The adjustment option therefore changes the preferred risk class under the same contract. At `d=1`, both arms favor positive risk. These observations establish an incremental availability effect; they also confirm that adjustment is not necessary for every duration-induced reversal. I do not describe these observations as uncomputed or internally contradictory. [E1], [C3]

The remaining gap is between that observation and an economically portable result. The current propositions say how to read moments **after** optimizing the model, not which primitive changes robustly produce the relevant moment ordering or a substantial risk-ranking effect. The selected operating region, cardinal utility levels, and settlement contract are economically consequential. Recognizing that they are primitives rather than numerical normalizations is correct, but does not remove the need to explain the result's dependence on them.

A substantial resolution would derive an interpretable primitive condition for the relative option or duration ordering and use it to predict a nontrivial pattern in a declared family of economies. Alternatively, a carefully motivated quantitative application could establish the magnitude and stability of the mechanism in economically interpretable units. This is not a demand for an empirical estimate in every theory paper or for a universal sign theorem under every possible contract. It is a demand for economic content beyond an envelope identity, a nested-set identity, and a selected ranking reversal.

### R6-F4 — The new computational certificate is not yet a certificate for the new economic conclusion

**Severity: major missing connection between the computational and economic contributions; not a claim that the reported finite-model signs are false.** Relevant locations: Corollary 11; Proposition 12's error-to-location assertion; Sections 8.10–8.11; Tables XIII–XV. [M2], [M3], [M4]

The transition experiment certifies a welfare loss below `0.001` for each of three fixed `d` values over the entire `lambda` interval. The mechanism experiment instead freshly optimizes two first-action classes with and without adjustment and reports a difference, a cost comparative static, and a narrow opposite-sign bracket. The new transition certificate is not used to bound those two constrained class values or their difference. The inherited reward sign exclusions are separately useful, but do not supply that missing transition-law/adjustment comparison.

The distinction matters quantitatively. At `d=0.375`, the adjustment-enabled class difference is only approximately `1.1318786e-5`. A generic `0.001` welfare statement cannot determine its sign. The paper correctly warns elsewhere that a welfare bound need not identify an action sign, yet its new economic application does not complete that additional certification step.

For scale only, suppose the displayed pointwise duration gap `0.00230304` were a valid uniform lower bound, and suppose each class value had error at most `0.001`. The error-to-location formula would permit a threshold error of approximately `0.8684`, not `2e-5`. Achieving the latter location precision through that formula would require a **combined** class-value error no larger than about `4.60608e-8`, as well as the uniform duration-separation hypothesis. Neither hypothetical premise follows from Table XIII. This calculation illustrates the missing error budget; it is not an estimate of the actual error of the exact finite Bellman solves.

The reported `2e-5` brackets come from direct finite-model optimization and opposite signs. They do not depend on treating the reusable policy's generic welfare tolerance as a class-value tolerance. Thus those brackets are not refuted by the calculation above. Nor does R6 claim they prove a globally unique diffusion-model threshold. The problem is that the paper has not demonstrated its opening promise that the new reusable representation and its error account support the economically important decision being studied, rather than simply coexist with another direct solution of that decision problem.

The needed next result is decision-specific: certify the relevant constrained class values, relative option, or sign exclusion on a stated economically relevant counterfactual region; allocate policy, endpoint, and numerical errors to that decision; and establish any duration separation actually used. A finite-model demonstration can already be informative. A continuous-time interpretation would additionally require the corresponding approximation control. More generic welfare tables, without this connection, do not resolve the issue.

## 3. Priorities and presentation

The paper should not respond by deleting unfavorable baselines, relabeling the mesh computation as neural success, or replacing a result with a qualification. Those behaviors would undo R6's real progress. Nor would another package of passing regression checks settle the contribution issue.

The highest priority is the comparison in R6-F1: characterize the corrected chord relative to a fairly localized count oracle, and measure the resulting precision–work tradeoff. The second is a positive contribution case, as opposed to progressively narrowing previously unsupported advantages. The third is an economic result whose primitive interpretation and decision-specific certification are demonstrated together. These are research deliverables, not editorial word substitutions.

Presentation should distinguish a **sharpness claim**, a **cost claim**, and a **validity claim** wherever upper oracles are compared. Table XIII should not allow its adaptive/global asymmetry to carry the scientific conclusion. The conditional nature of the second-order correction and the narrow scope of the three fixed contracts should remain explicit. Likewise, the regular-branch slopes in Table XV should not be converted into global comparative statics without establishing the required policy-cell and duration conditions.

The accumulated framework, historical demonstrations, and adverse results are worth preserving, but preservation need not make every past experiment an equal part of the current central argument. A clearer hierarchy between the principal theorem, the economic implication it enables, and supporting regression exercises would improve the paper without erasing its history.

## 4. Recommendation

R6 is more rigorous and more honest about its computations than its predecessors. I would not reject it on the grounds that the new finite-model upper bound is invalid: my examination and the executed checks support that construction under its hypotheses. Nevertheless, a valid construction and a well-preserved replication record are not sufficient for the contribution claimed here.

The matched localized-count result materially changes the assessment of the strongest new computational comparison. The economic identities and the newly executed adjustment counterfactual do not yet supply the missing general or quantitatively important economic insight, and the new welfare certificate does not certify the new risk-frontier conclusion. I therefore recommend **rejection in the present form**, rather than another revision whose acceptance is implicitly tied to closing a checklist of citations, tests, and wording changes. A substantially developed paper could be reconsidered on the strength of new comparative theory, matched computational evidence, and an integrated economic result.

---

## Appendix A. Why the local count coefficients dominate the corrected chord

Fix an interval `I=[a,b]` and suppress the interval superscript. Let `h=N-n`, and let `v^a,v^b` be the endpoint supersolutions of Theorem 10. Put

$$
C_{n,j}=\left(1-\frac jh\right)v_n^a+\frac jh v_n^b,
\qquad f_{h,j}=\frac{j(h-j)}{h(h-1)}\quad(h\ge2).
$$

The degree-elevated corrected coefficients are `U_{n,j}=C_{n,j}+f_{h,j}M_n`. At the terminal date both upper constructions equal `g`. At `h=1`, `M_n=0` because the endpoint terminal functions coincide. The count coefficients at that date are the respective endpoint Bellman maxima and are bounded by the endpoint supersolutions. This proves the base cases.

For `h>=2`, assume `W_{n+1,j}<=U_{n+1,j}`. Positivity permits substitution of `U` for `W` in the count recursion. For an interior count `1<=j<=h-1`, the part containing the linear endpoint coefficients equals

$$
\left(1-\frac jh\right)T^u_{n,a}v^a_{n+1}
+\frac jh T^u_{n,b}v^b_{n+1}
+ f_{h,j}(K^u_{n,a}-K^u_{n,b})(v^b_{n+1}-v^a_{n+1}).
$$

By endpoint supersolution inequalities this is at most `C_{n,j}+f_{h,j}D_n^u`, with exactly the paper's signed cross term.

For `h>2`, the propagated correction is

$$
f_{h,j}\left\{
\frac{h-j-1}{h-2}K^u_{n,a}M_{n+1}
+\frac{j-1}{h-2}K^u_{n,b}M_{n+1}
\right\}.
$$

The two displayed weights are nonnegative and sum to one. Thus, for the **same** current action `u`, the entire backup is at most

$$
C_{n,j}+f_{h,j}\left[D_n^u+
\max\{K^u_{n,a}M_{n+1},K^u_{n,b}M_{n+1}\}\right]
\le C_{n,j}+f_{h,j}M_n=U_{n,j}.
$$

At `h=2`, the next-date correction is zero, so the same conclusion follows directly from the `D` term and the definition of `M_n`. At `j=0` or `j=h`, the recursion is a pure endpoint backup and the endpoint supersolution inequality applies. Maximization over the common action preserves every inequality, completing the induction.

The local count polynomial is itself an upper value because any original policy can ignore the extra count information in the enlarged experiment. The Bernstein weights are nonnegative, so coefficient dominance yields polynomial dominance. De Casteljau subdivision is also positive and linear. Subtracting the same restricted lower coefficients, then applying the same maximum over coefficients, minimum over policies, positive part, and maximum over states/dates preserves the ordering of certificates. This proves the claim for every original anchor interval and every closed subdivision cell, not only at tested parameter values. **Q.E.D.**

This proof also identifies the compression: the corrected recursion replaces count-dependent propagation weights by their worst endpoint contribution and bounds endpoint action backups by their supersolutions. It is therefore potentially cheaper but weakly less sharp. Establishing when that compression is worthwhile is the missing comparative question.

## Appendix B. Diagnostic record and reproduction

`reviewer_diagnostics.py` uses only NumPy and no author imports. Its 160 randomized tests cover horizons 1–8, three states, three actions, affine positive substochastic kernels, signed rewards, random parameter intervals, and 11 parameter checks per model. The smallest corrected-minus-count coefficient is about `-4.44e-16`; the largest independent fixed-policy polynomial replay error is about `2.66e-15`; no coefficient certificate reverses the proved ordering. The deterministic strict example is recorded separately. Random tests support implementation checks; Appendix A, not random coverage, establishes the general proposition. [D1]

`matched_local_count.py` uses the exact deposited economy and all three fixed contracts, reuses each original endpoint pair and its feasible-policy coefficients, and independently computes local count upper coefficients and the same eight-cell coefficient gap. Its final JSON contains all 51 intervals and completed rows for all three contracts. The recorded times include local upper construction and replay of both coefficient certificates, but not a fresh optimized reconstruction of the competing chord and anchor library. They must **not** be interpreted as a matched speed comparison. [D2]

The author-unit replay completes 660 random parameter checks and 110 exhaustive small-policy checks, with discrepancies on the order of `1e-15`. The reviewer intercepted its `save` function to avoid overwriting the deposited author output. This corroborates execution of the submitted unit suite; it is not an independent 660-case implementation. [D3]

From a checkout containing this review directory and the reviewed R6 source, run:

```bash
python reviews/2026-09-16-econometrica-r6/reviewer_diagnostics.py \
  --output /tmp/nbo-r6-independent.json
python reviews/2026-09-16-econometrica-r6/matched_local_count.py \
  --repo "$PWD" --contracts 0 0.5 1 \
  --output /tmp/nbo-r6-matched.json
```

The matched script needs the R6 dependency environment and its inherited checkpoints/arrays. It is not a stand-alone two-file recreation of the economic model. Complete neural retraining and the full historical hyperparameter sweep are outside this review's execution scope. `review_manifest.json` pins the reviewed source, artifact identity, relevant input hashes, and the deposited review files.

## Sources and precise reading locations

**M1:** R6 Introduction, especially lines 17–23.  
**M2:** R6 transition-law theory, `04c_kernel_transfer.tex`, lines 5–116; main pp. 16–18.  
**M3:** R6 risk-frontier theory, `04d_risk_frontier.tex`, lines 5–58; main pp. 18–20.  
**M4:** R6 incremental evidence, `05b_incremental_evidence.tex`; Tables X–XV, main pp. 29–32.  
**M5:** R6 Conclusion.  
**S1:** Supplement S.9, especially its coefficient-construction and risk-class-scope discussions.  
**C1:** `transport.py`, fixed-policy/count recursions and global three-policy experiment.  
**C2:** `kernel_certificate.py`, corrected chord and adaptive interval construction.  
**C3:** `mechanism.py`, class optimization, independent policy evaluation, and brackets.  
**E1:** Completed R6 execution summary.  
**E2:** R6 source inventory and artifact provenance described above.  
**H1/H2:** R5 referee report and R6 point-by-point response.  
**D1/D2/D3:** Reviewer independent diagnostics, matched diagnostics, and author-unit replay in this directory.

[M1]: https://github.com/TrillionniumFoundation/NBO/blob/24011fef6da09bc05dc79946a3c1779e1fe7d8a8/revisions/2026-09-16-r6/paper/01_introduction.tex
[M2]: https://github.com/TrillionniumFoundation/NBO/blob/24011fef6da09bc05dc79946a3c1779e1fe7d8a8/revisions/2026-09-16-r6/paper/04c_kernel_transfer.tex
[M3]: https://github.com/TrillionniumFoundation/NBO/blob/24011fef6da09bc05dc79946a3c1779e1fe7d8a8/revisions/2026-09-16-r6/paper/04d_risk_frontier.tex
[M4]: https://github.com/TrillionniumFoundation/NBO/blob/24011fef6da09bc05dc79946a3c1779e1fe7d8a8/revisions/2026-09-16-r6/paper/05b_incremental_evidence.tex
[M5]: https://github.com/TrillionniumFoundation/NBO/blob/24011fef6da09bc05dc79946a3c1779e1fe7d8a8/revisions/2026-09-16-r6/paper/07_conclusion.tex
[S1]: https://github.com/TrillionniumFoundation/NBO/blob/24011fef6da09bc05dc79946a3c1779e1fe7d8a8/revisions/2026-09-16-r6/paper/S9_transition_replication.tex
[C1]: https://github.com/TrillionniumFoundation/NBO/blob/24011fef6da09bc05dc79946a3c1779e1fe7d8a8/replication/r6/transport.py
[C2]: https://github.com/TrillionniumFoundation/NBO/blob/24011fef6da09bc05dc79946a3c1779e1fe7d8a8/replication/r6/kernel_certificate.py
[C3]: https://github.com/TrillionniumFoundation/NBO/blob/24011fef6da09bc05dc79946a3c1779e1fe7d8a8/replication/r6/mechanism.py
[E1]: https://github.com/TrillionniumFoundation/NBO/blob/24011fef6da09bc05dc79946a3c1779e1fe7d8a8/revisions/2026-09-16-r6/execution_summary.md
[E2]: https://github.com/TrillionniumFoundation/NBO/blob/24011fef6da09bc05dc79946a3c1779e1fe7d8a8/revisions/2026-09-16-r6/source_inventory.json
[H1]: https://github.com/TrillionniumFoundation/NBO/blob/0d0e79a52e540bd0647801ce316f051d667c6797/reviews/2026-09-16-econometrica-r5/referee_report.md
[H2]: https://github.com/TrillionniumFoundation/NBO/blob/24011fef6da09bc05dc79946a3c1779e1fe7d8a8/revisions/2026-09-16-r6/response_to_referee.md
[D1]: diagnostic_results.json
[D2]: matched_local_count_results.json
[D3]: author_unit_replay.json

### Primary literature

**L1.** Nemecek, M., and R. Parr (2021), “Policy Caches with Successor Features,” *ICML*, PMLR 139, 8025–8033.  
**L2.** Alegre, L. N., A. L. C. Bazzan, and B. C. da Silva (2022), “Optimistic Linear Support and Successor Features as a Basis for Optimal Policy Transfer,” *ICML*, PMLR 162, 394–413.  
**L3.** Csáji, B. C., and L. Monostori (2008), “Value Function Based Reinforcement Learning in Changing Markovian Environments,” *JMLR*, 9, 1679–1709.  
**L4.** Brown, D. B., J. E. Smith, and P. Sun (2010), “Information Relaxations and Duality in Stochastic Dynamic Programs,” *Operations Research*, 58, 785–801. DOI: `10.1287/opre.1090.0796`.  
**L5.** Quatmann, T., C. Dehnert, N. Jansen, S. Junges, and J.-P. Katoen (2016), “Parameter Synthesis for Markov Models: Faster Than Ever,” *ATVA*, LNCS 9938, 50–67; arXiv:1602.05113. The comparison here concerns regional certification and parameter dependence, not an assertion that its assumptions or bounds coincide with Theorem 10.  
**L6.** Milgrom, P., and I. Segal (2002), “Envelope Theorems for Arbitrary Choice Sets,” *Econometrica*, 70, 583–601. DOI: `10.1111/1468-0262.00296`.

[L1]: https://proceedings.mlr.press/v139/nemecek21a.html
[L2]: https://proceedings.mlr.press/v162/alegre22a.html
[L3]: https://www.jmlr.org/papers/v9/csaji08a.html
[L4]: https://scholars.duke.edu/publication/1243382
[L5]: https://arxiv.org/abs/1602.05113
[L6]: https://onlinelibrary.wiley.com/doi/abs/10.1111/1468-0262.00296
