# Referee report: Neural Bellman Operators
## Latest-deposit audit, economic interpretation, and incremental contribution

**Manuscript author:** Qian QI  
**Date:** 17 September 2026  
**Recommendation on the latest complete manuscript:** **Reject in its present form for Econometrica.**  
**Latest inspected revision head:** `0f0b1d86a61cd741d2cf346f88acbf6ec3026416`  
**Actual complete manuscript:** R7, `fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17`  
**Review branch:** `review/econometrica-latest-substantive-2026-09-17-0f0b1d8`

This is an owner-commissioned, independent advisory review written to a demanding general-interest economics-journal standard. It is not an appointment by Econometrica, a journal decision, or a review by the manuscript author. The recommendation concerns the deposited manuscript, not the feasibility of developing the research programme.

## 1. What is actually available for review

The two newest substantive-looking branch names, `revision/econometrica-r8-economic-frontier-2026-09-17` and `revision/econometrica-r8-economic-target-response-2026-09-17`, point to the same commit, `0f0b1d8...`. Its parent is the previous economic-target review, `112a3809...`. The complete diff against that parent contains exactly one addition: the five-line `revisions/2026-09-17-r8/README.md`. That file explicitly calls itself an initialization and says the revised manuscript, response, and executed evidence will follow. It does not claim that an author response has been completed. [P1–P3]

Comparing this head against the R7 manuscript commit gives 25 added files: 24 review files and the R8 initializer. There are no changed manuscript, author replication, or author numerical-evidence files. `REVISION_INDEX.md` and `ECTA_R7.tex` still identify the complete R7 manuscript. Consequently, there is **no deposited R8 manuscript to referee separately**. The present report assesses the latest complete manuscript carried by the latest revision head and records the delivery boundary accurately. It does not invent an R8 argument or charge the author with failing to respond in a response that does not exist. [P1–P4]

This distinction is more than administration. A sequence of review and initialization commits cannot supply missing economic evidence. Conversely, an honestly labelled initializer is not evidence of scientific misconduct. The substantive findings below concern the unchanged manuscript and distinguish new reviewer calculations from concerns already established in the preceding report.

## 2. Overall assessment

The strongest part of R7 is now a coherent finite-model construction. An endpoint correction supplies an upper value for an affine transition mixture; a count-information relaxation is sharper on matched coefficients; and feasible-policy Bernstein representations support regional welfare and class-choice certificates. The corrected total-error theorem includes policy-bank error rather than confusing a second-order correction with a second-order approximation of optimal policy. These are genuine improvements. The two-stage preference-adjustment proposition also gives an actual sufficient condition, not merely set inclusion. [M2–M5, M11]

My negative recommendation does not depend on finding those statements false. It follows from the remaining gap between them and the paper's integrated economic-methodological claim. The highlighted portfolio ranking is secure only for a particular stored finite target whose decision margin is already known to move under wealth refinement. The portable preference result does not explain that dynamic target, and its direction depends materially on a cardinal preference primitive beyond ordinary risk attitudes. The numerical showcase for the economic certificate uses the sharper count oracle rather than demonstrating that compression or learning is responsible for an economically consequential gain. The work therefore still reads as several individually defensible components whose conjunction has not yet established the proposed contribution. [M1–M7, H1]

I would not recommend an exposition-only revision. Another round should deliver discriminating theory and evidence: a defensible economic target, a decision-relevant error account, a dynamic mechanism linked to that target, and an attributable computational benefit at a common accuracy requirement. Repeatedly renaming the contribution or adding successful checks of the same finite arrays would not meet those requirements. Nor is deletion of the adverse comparisons an acceptable response.

### Scope of this assessment

I inspected the pinned main entry point, introduction, inherited approximation and stopped-economy sections, transition-transfer and risk-frontier arguments, the new comparative and economic sections, S.10–S.11 proofs, execution summary, R7 response, and the latest economic-target report. The principal mathematical scrutiny concerns these sections, not an independent re-proof of every inherited model. The manuscript was reviewed in its TeX source; I did not rebuild or visually inspect its complete main and supplementary PDFs in this run. I did not retrain the networks, rerun the large stopped-economy spatial experiment, or reproduce the author's elapsed-time contest. Those limits must not be obscured by a general statement that the repository was “verified.”

I did execute a new, independently written diagnostic program that imports no author modules. It checks 60 dense finite models, with horizons 1, 2, 3, 4, 6, and 8, and 1,020 parameter-point optimizations. It compares count and chord coefficients, rectangular bounds, optimal values, fixed-policy coefficient replay, and the total-error estimate. The largest positive numerical inequality discrepancy and largest policy-replay discrepancy were both `8.881784197001252e-16`. These checks support the inspected recursions; numerical experiments do not prove their general validity. [D1]

The same program solves 27 two-stage primitive specifications, evaluating both risk classes in each, by strict-concavity derivative bisection and separately by bounded scalar optimization. The largest discrepancy between the two objective calculations was `8.40473524110763e-16`. It also recomputes the manuscript's conservatively rounded family bound and the decision-error and storage arithmetic used below. The code and diagnostic summary are deposited with this report; the code regenerates every individual model and primitive result. [D1–D2]

## 3. F1 — The finite-array certificate does not resolve the economic-target objection

**Status:** Substantive objection carried forward, with an explicit decision-error requirement.  
**Importance:** Publication-blocking for the flagship economic interpretation.  
**Locations:** `05c_r7_evidence.tex`, S.11.3–S.11.4, the inherited approximation theorem, and the preceding economic-target report.

R7 certifies opposite first-risk rankings on the rectangle

\[
(\lambda,d)\in[0,0.25]\times[0.4,0.45],\qquad (u,X)=(2,1.25),\quad k=2.
\]

Its reported minimum margins are `6.888728805714623e-5` in favor of the positive class with adjustment and `5.299365560501097e-5` in favor of the nonpositive class without adjustment. The per-class floating-point allowance is `3.797650002493679e-9`. The manuscript explicitly limits this arithmetic account to the stored finite arrays; it does not falsely claim that it controls diffusion or grid-construction error. The objection is that the uncontrolled component matters at exactly the margin used for the economic conclusion. [M5–M7]

The preceding report recomputed both adjustment regimes under wealth-only refinement with the decision calendar fixed. At `(lambda,d)=(0.25,0.45)`, its common-menu results for the no-adjustment class difference were `-0.0000530012509050`, `+0.0000612627395757`, and `+0.0000979426715393` at 49, 97, and 145 wealth nodes. The adjusted differences remained positive. Its relative adjustment option therefore survived while the opposite-risk-choice conclusion at that corner did not. These are **attributed prior computations**, not newly executed results of this report. They neither disprove the original finite-array theorem nor establish a limiting diffusion sign. [H1, Section 4]

For a precise statement of what is missing, let the target-to-array class-value error in regime `r` satisfy

\[
|W_{\sigma}^{r,\mathrm{target}}-W_{\sigma}^{r,\mathrm{array}}|
\leq\eta_{\sigma}^{r}.
\]

A certified array interval `[ell_r,u_r]` then implies only

\[
\Delta^{r,\mathrm{target}}\in
[\ell_r-\eta_+^r-\eta_-^r,\ u_r+\eta_+^r+\eta_-^r].
\]

Thus sufficient additional conditions for both reported signs are

\[
\eta_+^{\mathrm{adj}}+\eta_-^{\mathrm{adj}}<6.888728805714623\times10^{-5},
\qquad
\eta_+^{0}+\eta_-^{0}<5.299365560501097\times10^{-5}.
\]

A common additional per-class error strictly below `2.6496827802505486e-5` would suffice. This number is a required budget, not an estimate of the actual error. It does not charge the already included arithmetic allowance twice. Adding decimal places to the stored-array calculation cannot supply it. [M7; D2]

**Required response.** Retain the original rectangle and explain its movement relative to an explicitly stated target. Either provide economically relevant approximation control, or defend the finite transition mechanism as an economic primitive and examine meaningful perturbations of that primitive. Both adjustment regimes and traceable common action menus are necessary. A new favorable rectangle without a map of the old one's failure would not answer this objection. A formal substitution of an unevaluated approximation constant into the inherited theorem would not answer it either.

## 4. F2 — The primitive risk-specific option is sensitive to the cardinal preference benchmark

**Status:** New quantitative reviewer finding; not a counterexample to the stated proposition.  
**Importance:** Major limitation on the economic interpretation and portability of the mechanism.  
**Locations:** `04_preferences.tex`, `04f_economic_certification.tex`, and S.11.1–S.11.2.

The manuscript correctly states that preference-dependent utility normalizations change incentives when preferences are controlled. I do not ask it to impose an invariance that its model expressly rejects. The remaining question is substantive: what economically grounds the particular cross-preference cardinal comparison, and how much of the advertised option ordering comes from that comparison rather than from risk exposure?

A controlled perturbation makes this issue concrete. In the two-stage specialization, replace the felicity function by

\[
\widetilde U_a(c,u)=\frac{c^{1-u}}{1-u}+a(u-u_0),\qquad u_0=2.
\]

The same `a` is used for both risk classes. This is a **different cardinal preference primitive**, not a harmless re-expression of the same endogenous-preference economy. However, it preserves all consumption derivatives at every fixed `u`, hence the relative risk-aversion index `u`. It also preserves the complete unadjusted class values at `u=u0`, their difference, the consumption lotteries, the adjustment box, the cost coefficient, and the curvature with respect to `u`. It changes only the common slope of the payoff assigned to moving across preference indices:

\[
\widetilde g_\sigma=g_\sigma+a,\qquad \widetilde M_\sigma=M_\sigma.
\]

This is useful precisely because the manuscript's sufficient condition compares squared preference slopes. A common linear tilt can affect the two squared slopes very differently. No mathematical inconsistency is involved.

Take a point inside the declared primitive family: `p=0.08`, `k=40`, `C_-=0.5`, `C_+=0.05` or `0.8`, adjustment bound `0.2`, and `D_A=0.5`. Independent optimization gives:

| Common cardinal tilt `a` | Positive-class option | Nonpositive-class option | Relative option | Adjusted indifference contract |
|---:|---:|---:|---:|---:|
| 0 | 0.0532950841903 | 0.00446671772342 | +0.0488283664669 | 1.40234326707 |
| 1 | 0.0169955555072 | 0.0309153211408 | -0.0139197656336 | 1.52783953127 |
| 2 | 0.000902516463628 | 0.0811850258312 | -0.0802825093676 | 1.66056501874 |

The no-adjustment indifference contract remains exactly `d0=1.5` in all three cases. Thus the original downward shift becomes an upward shift under the common tilt. No risk-specific additive adjustment has been introduced. These are illustrative sensitivity calculations, not preregistered estimates or a calibration. [D1–D2]

The reversal for `a=1` is supported by a sufficient inequality, not merely an optimizer output. Applying the paper's own quadratic argument to the other class gives

\[
\widetilde\Omega_- - \widetilde\Omega_+
\geq \frac{(g_-+a)^2}{2(k+M_-)}
      -\frac{(g_++a)^2}{2k}.
\]

Here `g_++1=-1.2997867216977266`, `g_-+1=1.6137056388801094`, and `M_-=4.075449952488117`. The lower-bound trial is feasible, and the displayed lower bound is approximately `0.00842270584932`, strictly positive. The curvature maximum uses the manuscript's endpoint-curvature argument. The strict margin and continuity also imply a neighborhood of primitive specifications with the reversed ordering; the report does not claim a numerically certified size for that neighborhood.

For the original, untilted specification, I independently recover the rounded family lower estimate `0.0018627207858683808 > 0.00186`. The original sufficient-condition theorem therefore survives this audit. What does not follow from it is that downside risk or endogenous risk aversion alone determines the direction of the premium. The cardinal value of changing the preference index is doing economically substantial work.

**Required response.** Ground that primitive in an explicit interpretation of preferences over preference changes, or characterize a meaningful class of cardinal perturbations for which the mechanism survives. In the dynamic economy, separate the contribution of the felicity normalization from settlement, operating duration, and preference hedging. This requires analysis, not another disclaimer that units are fixed. I have not rerun the full stopped economy under this tilt: its no-adjustment preference state remains stochastic, so the two-stage baseline-invariance argument cannot simply be transferred to it.

## 5. F3 — A first-action value partition needs a nondegenerate economic decision horizon

**Status:** Additional conceptual/technical clarification beyond the preceding wealth-grid objection.  
**Importance:** Major for any continuous-time interpretation; not a defect in the explicitly finite eight-date certificate.  
**Location:** Opening paragraph of `04d_risk_frontier.tex`, together with the continuous-time stopped economy.

The risk classes are defined by the sign of the first risky position, with later positions unrestricted. This is well-defined on the finite decision calendar: a first action governs a positive-length decision period. But the manuscript also mentions the continuous model, subject to attainment or compact-closure qualifications. Those qualifications alone do not make a class partition by the control at one isolated initial instant economically meaningful. [M8–M9]

Under the usual measurable-control formulation of the displayed diffusion, changing a bounded risky-share control only at the deterministic initial instant changes neither its drift integral nor its stochastic integral. The latter difference has zero quadratic variation because the singleton has zero time measure. The state trajectory, stopped payoff, and expected objective are unchanged. One can therefore alter that isolated control value to either sign without changing the policy value. A literal partition by `pi(t0)>0` versus `pi(t0)<=0` then has equal class suprema. It cannot support a strictly nonzero lifetime class-value difference.

This observation does not contradict a finite first-period ranking, nor does it prevent a nonzero optimal Hamiltonian selector. Those are different objects. It shows why the definition of the decision whose sign is certified must accompany any passage between the finite economy and the continuous formulation. Even temporal refinement can change the duration of the restriction, rather than merely improve the approximation of a fixed economic experiment.

**Required response.** Define the economic commitment or rebalancing interval, or formulate a local Hamiltonian/action-gap result with its appropriate units and assumptions. A fixed-calendar model is a legitimate choice and does not need a continuous-time limit to be interesting. The paper should nevertheless explain why that calendar and the first-period classification are the economically relevant objects. Do not advertise calendar refinement as a common-estimand convergence exercise without preserving the duration of the restricted choice. This requirement is separate from F1: the cited wealth-only experiment already kept the calendar fixed.

## 6. F4 — The explanatory specialization does not yet explain the executed dynamic economy

**Status:** The preceding dynamic-mechanism objection remains open; F2 sharpens one reason.  
**Importance:** Major economic-contribution issue.  
**Locations:** The introduction, primitive proposition, stopped-economy model, and regional experiment.

The two-stage sufficient condition fixes a consumption lottery and assigns an exogenous duration difference. The stopped portfolio economy instead chooses consumption, investment, and adjustment jointly; these choices change exit, future consumption exposure, and the covariance-related continuation term. Its numerical certificate fixes `k=2`, whereas the illustrative primitive family uses `k` in `[20,80]`. The manuscript expressly says the specialization is neither a calibration nor an approximation of the full economy. That is an honest boundary, but it leaves the purported explanatory connection to be demonstrated. [M1, M4–M6, M9]

The option identity

\[
\Delta^{\mathrm{adj}}-\Delta^0=\Omega_+-\Omega_-
\]

identifies the arithmetic difference of two counterfactual rankings. It is not, by itself, a mechanism analysis. The tensor certificate verifies a sign in the implemented target; it does not establish that the consumption-exposure channel of the specialization, rather than another primitive interaction, is responsible for it. Nor does the existence of a positive option prove that adjustment is necessary for positive risk at every contract. The preceding two-regime refinement results show why this distinction matters. [M8, H1]

**Required response.** Supply a dynamic sufficient condition that connects primitive restrictions to the executed economy, or a disciplined mechanism analysis with both regimes recomputed. Such an analysis should retain the original model and report how altered settlement incentives, operating duration, covariance, and cardinal preference incentives affect the relevant value differences. A decomposition of optimized feature moments can be informative, but it must not be presented as a causal identification theorem. There is no demand here to estimate the model from data; the demand is for economic explanation commensurate with a theory/computation paper's claim.

## 7. F5 — The method needs an attributable end-to-end gain at the economic accuracy target

**Status:** Contribution objection carried forward; new storage arithmetic illustrates the bottleneck.  
**Importance:** Publication-blocking for the integrated methodological claim.  
**Locations:** The introduction, comparative-oracle section, S.10.2, and execution summary.

R7 does have a positive compression result. The author's autonomous experiment reports approximately 73.405 seconds and 18 anchors for chord-only refinement, compared with 115.377 seconds and 11 anchors for count-only refinement; the cascade takes approximately 127.732 seconds. These are attributed single-pass measurements, not timings repeated by this referee. They show that fewer anchors need not mean less work. It would be inaccurate to dismiss compression as entirely useless. [M7]

But that experiment targets a generic `10^-3` welfare tolerance. The flagship economic comparison uses class-specific count upper bounds and much smaller sign margins. It does not demonstrate how much learning or chord compression contributes to obtaining that particular economic conclusion. Exact finite-action optimization supplies the demonstrated anchors. The paper itself retains structural and mesh-based comparisons that limit the neural claim. This is good reporting; it is not yet a positive case for the distinctive integrated method. [M1–M3, M5–M7]

The storage distinction also deserves quantitative emphasis. At `H=8`, the upper correction saves 21 state vectors relative to the 28 interior count vectors. If a full coefficient bank of `m` policies is retained, the lower bank has `45m` state vectors, including its terminal coefficients, under the paper's accounting. Ignoring all other common storage, the largest fraction saved in bank-plus-upper coefficient storage is then

\[
\frac{21}{45m+28}.
\]

It is about 17.80 percent for `m=2`, but only 2.506 percent for `m=18`; common endpoint, kernel, control-index, and temporary storage would reduce the overall fraction further. This is an illustrative accounting identity, not measured process memory and not a claim that every implementation retains an 18-policy bank. A streamed or local-bank implementation changes the accounting and should be measured on its own terms. [M3; D2]

**Required response.** Demonstrate an economically meaningful workload on which the proposed component changes cost, scale, or attainable accuracy, with the economic target and tolerance held fixed. Charge proposal construction, anchor optimization, lower-policy evaluation, certificate construction, and storage. A matched decision-certification comparison of chord, count, and a non-neural feasible-policy construction would be more probative than another generic speed table, provided all arms are judged against the same full target and decision error. There is no requirement to beat every solver, to discard neural components, or to erase the existing favorable compression result. The requirement is a defensible attribution of the gain claimed by this paper.

## 8. F6 — The nearest-literature distinction remains insufficiently precise

**Status:** Existing positioning issue independently checked against a primary source.  
**Importance:** Major for the novelty assessment, not a finding of duplication.

The comparison cannot lean on rewards or controlled Markov models being absent from parameter lifting. Quatmann et al. (2016) explicitly define parametric MDPs, add reward functions, and discuss expected-reward properties in Sections 2.1–2.2; I checked the relevant primary PDF pages. Heck et al. (2025) explicitly study tighter dependency-sensitive abstractions for parametric Markov chains. The latter's model class should not be silently identified with NBO's controlled finite-horizon reward target. [L1–L2]

The author should set out the actual correspondence: state augmented by date, action information, common versus reset parameters, substochastic mass, terminal rewards, feasible lower policies, and the signed compression. Date augmentation and a cemetery state are natural comparison devices, not proofs that the two algorithms are identical. The plausible contribution lies in the particular compression, its ordering and error analysis, and a consequential use of it—not in a broad claim that regional reward control was previously unavailable. I have not established that the specific NBO theorem appears in prior work, and this is not an exhaustive priority search. Adding citations without the mathematical comparison will not resolve the positioning problem. [M1–M3]

## 9. What a substantive next revision must deliver

The current contribution cannot be repaired by adjectives, a larger preservation map, or a new branch label. The following requirements are targeted to the findings above; they do not demand deletion of valid results or abandonment of the project.

| Finding | Evidence that would address it | Evidence that would not address it |
|---|---|---|
| Version boundary | A deposited complete new manuscript, response, and evidence on a pinned revision commit | An initializer or an inherited review tree |
| F1: target and decision error | Both-regime robustness or target-error control at the actual sign margin, with traceable menus | More precision on the unchanged arrays or an unexplained new rectangle |
| F2: cardinal mechanism | A grounded cross-preference primitive and informative sensitivity/robustness analysis | Repeating that the existing normalization is fixed |
| F3: first-choice estimand | A positive-duration decision definition or a properly formulated local action result | Attainment/closure language without a decision horizon |
| F4: dynamic explanation | A primitive-to-dynamic argument or controlled full-model mechanism analysis | The option identity placed next to an unrelated specialization |
| F5: computational contribution | An attributable full-cost gain at a common meaningful economic accuracy target | Upper-array ratios, kernel counts, or neural terminology alone |
| F6: novelty | Explicit correspondence and differentiation from the nearest regional methods | A probability-versus-reward slogan or bibliography expansion alone |

One minor correction is also warranted. The final paragraph of `04e_comparative_oracles.tex` says the frontier does not represent an executed autonomous cascade timing contest, while the manuscript subsequently reports precisely a separately executed autonomous experiment. Distinguishing the common-bank frontier from that separate experiment would remove the ambiguity. This presentation issue is not grounds for dismissing the deposited timing evidence. [M2, M5]

**Final recommendation.** Reject the current complete manuscript in its present form. The corrected finite-model mathematics merits preservation, and the new independent checks support rather than overturn its central ordering and error arguments. The negative recommendation rests on the unclosed economic-target, mechanism, decision-definition, and contribution issues. No recommendation is made on an unavailable R8 manuscript. A genuinely new revision must supply the missing research, not merely another statement that the previous objections have been closed.

## Sources and audit trail

All manuscript paths below are pinned to `0f0b1d86a61cd741d2cf346f88acbf6ec3026416`; the comparison establishes that their contents are inherited unchanged from R7. The manifest records the inspected blob identities. Section labels are used because this run did not rebuild the manuscript PDFs.

**Provenance.** P1: live GitHub branch inventory; P2: commit metadata and comparison `112a3809...` to `0f0b1d8...`; P3: `revisions/2026-09-17-r8/README.md`; P4: comparison `fbfbf902...` to `0f0b1d8...`, `REVISION_INDEX.md`, and `ECTA_R7.tex`.

**Manuscript.** M1: `revisions/2026-09-16-r7/paper/01_introduction.tex`. M2: `revisions/2026-09-16-r7/paper/04e_comparative_oracles.tex`. M3: `revisions/2026-09-16-r7/paper/S10_comparison_proofs.tex`. M4: `revisions/2026-09-16-r7/paper/04f_economic_certification.tex`. M5: `revisions/2026-09-16-r7/paper/05c_r7_evidence.tex`. M6: `revisions/2026-09-16-r7/paper/S11_economic_proofs.tex`. M7: `revisions/2026-09-16-r7/execution_summary.md`. M8: `revisions/2026-09-16-r6/paper/04d_risk_frontier.tex`. M9: `revisions/2026-09-16-r6/paper/04_preferences.tex`. M10: `revisions/2026-09-16-r6/paper/03_approximation.tex`. M11: `revisions/2026-09-16-r6/paper/04c_kernel_transfer.tex`. M12: `revisions/2026-09-16-r7/response_to_referee.md`.

**History.** H1: `reviews/2026-09-17-econometrica-r7-economic-target/referee_report.md`, originally at `112a38099317d90b42bfc0028839e4320fdd1aae`, especially Sections 4–8. Its wealth-grid calculations are attributed, not rerun here. The report is read as historical evidence, not an author response.

**New diagnostics.** D1: `reviewer_checks.py`, an independent program implementing the displayed formulas without importing the author's solver. D2: `diagnostic_summary.json`, with environment, aggregate checks, cardinal-sensitivity rows, and error/storage arithmetic. The complete executed per-model and per-primitive output is included as `diagnostic_results.json.gz`. Running D1 regenerates `diagnostic_results.json`; its hash is recorded in the manifest. `README.md` states reproduction and evidentiary limits.

**External primary sources.** L1: Quatmann, Tim, Christian Dehnert, Nils Jansen, Sebastian Junges, and Joost-Pieter Katoen (2016), *Parameter Synthesis for Markov Models: Faster Than Ever*, arXiv:1602.05113v2, Sections 2.1–2.2, particularly printed pp. 4–6. Primary PDF text and rendered pp. 4–5 checked. L2: Heck, Linus, Tim Quatmann, Jip Spel, Joost-Pieter Katoen, and Sebastian Junges (2025), *Generalized Parameter Lifting: Finer Abstractions for Parametric Markov Chains*, arXiv:2504.05965v2; abstract and bibliographic scope checked. No claim is made to have independently audited every result of L2.
