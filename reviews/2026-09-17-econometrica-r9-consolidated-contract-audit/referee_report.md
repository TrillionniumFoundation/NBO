# Referee report: Neural Bellman Operators — complete R9
## A priced implementation is not yet a unified economic mechanism

**Date:** 17 September 2026  
**Author:** Qian QI  
**Standard:** Econometrica; owner-commissioned advisory review, not an official journal appointment or editorial decision.  
**Recommendation:** **Reject in its present form. A substantive economic result, rather than a further exposition-only revision, is required.**  
**Reviewed branch:** `revision/econometrica-r9-participation-permissions-2026-09-17`  
**Reviewed scientific commit:** `8c1e0472279fb66a2419b63b3e35df028ecfdd78`  
**Review branch:** `review/econometrica-r9-consolidated-contract-audit-2026-09-17-8c1e047`

## 1. Assessment, manuscript identity, and the two preceding reports

R9 is a complete scientific revision, not an initialization branch bearing a new number. Its entry points import new participation, surrender, enforcement, and permission sections; its deposit includes a response, numerical evidence, and manuscript files. I reviewed these additions, their proofs and implementation, and the inherited economic arguments on which their interpretation depends. The reviewed object is the pinned R9 above, not the older `revision/econometrica-r9-contract-response-2026-09-17` initialization. [M1–M5, C1]

The revision makes real progress. It gives a coherent separate-account participation model, an explicit principal participation condition, a necessary-and-sufficient **statewise** enforcement threshold, an operational sufficient regional charge, and a finite breakpoint reduction for the continuous first-date risky share. It retains unfavorable surrender and permission experiments. I have not identified a counterexample to these stated finite-model propositions. My independent rational checks support the enforcement and envelope arguments; they do not manufacture an adverse verdict from a failed numerical test. [M2–M4, E1]

Nevertheless, I do not recommend publication in the present form. The strongest economic result remains a narrowly specified portfolio comparison whose primitive mechanism and executed dynamic mechanism have not been connected. The new participation layer prices a particular way of reproducing compulsory operation, but leaves an alternative form of compulsory commitment without a separately specified enforcement cost. Moreover, the advertised successful fee interval makes surrender strictly inactive. These observations do not invalidate the original certificate. They limit what the new contracting results establish economically.

Two R8 reports must be distinguished. The economic-stress report, at `8c20474...`, requested participation/surrender and investment-permission analysis. R9 substantially supplies that analysis. A separate independent-mechanism report, at `cd8596c...`, identified a different problem: the primitive sufficient theorem and the executed dynamic example move the positive class's preference index in opposite directions. R9's response expressly addresses the former report; the active manuscript has not resolved the latter problem. This is a consolidation of parallel review records, not an allegation that the author deliberately ignored a report. [H1, H2, M1, M5]

The recommendation is a judgment about the remaining contribution, not a finding that neural approximation, finite economic models, or numerical methods are unsuitable for economics. An empirical calibration is not mandatory for a theoretical paper. Nor must a theoretical mechanism survive arbitrary changes in its primitives. What is missing is a sufficiently informative economic result connecting the paper's particular primitives, actual optimizing behavior, and headline comparison.

### Disposition of the principal inherited objections

| Issue | R9 disposition in this review |
|---|---|
| R8-E1: no participation or surrender analysis | The formal omission is substantially repaired. A remaining issue is the economic comparability and pricing of the commitment instruments, discussed in Section 3. |
| R8-E2: unexplained binding financial permissions | Substantially addressed for the declared initial-permission target. Both optimizers, both switching boundaries, and appropriate one-sided sensitivities are reported. |
| R8-I1: primitive versus dynamic adjustment mechanism | **Open and central.** The new contracting results do not establish the missing connection. |
| Finite versus diffusion target; instantaneous first action | The finite contract and positive-duration estimand are explicit. I do not renew demands for a diffusion sign or criticize a singleton restriction the current experiment does not use. |
| Cardinal primitive and dynamic reoptimization accounting | Their specification and accounting roles are acknowledged. Their presence does not by itself establish the economic sign mechanism. |
| Same-target certificate accounting and regional-method correspondence | The inspected material recognizes the appropriate distinctions and adverse comparisons. This report does not claim that R9 lacks all baselines or establishes neural necessity. |

These dispositions follow the active imports and source, not just the response letter. [M1–M6, H1, H2]

## 2. R9-M1 — The central dynamic mechanism remains unproved

**Severity: major; publication-blocking contribution issue.**  
**Status: an unresolved objection from the independent R8 review, rechecked against active R9. It is not a counterexample to the primitive proposition.**

The primitive theorem establishes a positive relative adjustment premium for a two-stage family. It considers

\[
\Phi_\sigma(\theta)=F_\sigma(\theta)-F_\sigma(0)+a\theta-\tfrac12k\theta^2,
\qquad -0.2\leq\theta\leq0.2,
\]

with the consumption lotteries, cost interval, and cardinal tilt stated in `prop:r8_cardinal`. The inherited proof supplies strict concavity and the bounds

\[
-3.118\leq g_+\leq-1.482,
\qquad g_-=2(1-\log2),
\qquad a\in[-0.25,0.25].
\]

Consequently, throughout that family,

\[
\Phi_+'(0)\leq-1.232<0,
\qquad
\Phi_-'(0)\geq0.36370563888\ldots>0.
\]

Strict concavity and the availability of adjustments of either sign imply

\[
\theta_+^*<0<\theta_-^*.
\]

This is a uniform analytical implication of the manuscript's own bounds, not an inference from a finite table. My independent 65-digit Decimal calculation at `(p,k,a)=(0.08,40,0)` gives `theta_plus=-0.0464338126712310...`, `theta_minus=0.0145613501634963...`, and relative option `0.0488283664668915...`. The advertised conservative lower bound recalculates to `0.000417380273806973...`. These are supportive checks of the primitive result. [M5, E1]

Now compare the actual R9 initial-optimizer table. With deliberate adjustment allowed, both initial classes choose **positive adjustment at its upper limit**:

\[
(c,\theta,\pi)_+=(0.8,0.2,0.8),\qquad
(c,\theta,\pi)_-=(0.8,0.2,-0.5).
\]

The dynamic cost is `k=2`, outside the primitive theorem's `[20,80]` family. In the primitive model adjustment changes a preference level; in the dynamic model it changes a drift. Their numerical magnitudes should not be equated. Their directions of movement of the preference index can, however, be meaningfully distinguished. In the positive class they differ. [M4, M5]

There is no logical contradiction: the manuscript correctly says that the two-stage economy does not mechanically determine the dynamic direction. The problem is that this caveat leaves the main economic inference unsupported. A positive four-value contrast in two models is not evidence that the same preference-adjustment mechanism generates it. In the dynamic economy, continuation utility, the reference-state payoff, endogenous duration, boundary exposure, consumption choice, and financial constraints interact. The primitive consumption-lottery inequality does not order those dynamic incentives.

The R9 participation and enforcement results do not fill this gap. Policy inclusion establishes that a larger adjustment menu weakly raises each class value and can reduce each class's compensation and implementing fee. Those orders hold for generic nested action sets. They do not predict which class gains more, why both initial adjustments increase the index, or when the relative option changes the investment ranking. Similarly, the fee and permission envelope identities identify relevant marginal exposures but do not establish their ordering. [M2, M3, M5]

**Required scientific response.** Provide an economically interpretable sufficient condition in the stopped dynamic class actually used for the headline result, or construct an explicit connecting family that explains the change of adjustment direction. The condition should account for the cardinal state payoff and endogenous exit, not assume the desired ordering of optimized class values. At the realized boundary controls, finite-menu one-sided action-value comparisons are the appropriate diagnostic; an interior first-order condition is not a characterization of these optimizers. Show the relevant current-payoff and continuation incentives for each initial class, and explain why their difference produces the relative premium. Preserve the existing primitive theorem. More optimized rows or another envelope identity would not answer this objection.

## 3. R9-M2 — The model prices a surrender charge but not all commitment

**Severity: major for the interpretation of the new contracting contribution.**  
**Status: new conditional dominance comparison within the declared contract family, not a refutation of `prop:r9_participation`.**

The separate-account model is now explicit. The grant and fee do not enter managed wealth; the principal purchases discounted operating duration; charges go to a separate enforcement institution; and capacity has an ex ante carrying cost. Given those assumptions and a specified agent-policy selection, the participation calculation is correct:

\[
q_r^*(E)=\bigl[G(x_0)-\max_\sigma W_\sigma^r+C(E)\bigr]_+,
\qquad \Pi_r=b\mathcal A_{p_r^*}-q_r^*(E).
\]

R9 also correctly qualifies the selection problem when optimal agent policies deliver different amounts of service. I do not criticize the formula for omitting a wealth effect it explicitly excludes. [M2, M3]

The unresolved issue is the treatment of the **minimum compulsory term**. The same family allows `m=8`, which is noncancellable regardless of `F`. The charged capacity applies to the elective termination fee. No independent cost or capacity requirement is specified for imposing the compulsory term itself. Thus one enforcement instrument is priced while another can impose the original obligation without that price.

This distinction is quantitatively transparent in the author's positive-cost example. At the center, `F=E=0.85`, `m=1`, `C(E)=0.01`, and `b=0.90`, the source reports:

| Regime | Discounted service | Grant including capacity cost | Principal surplus |
|---|---:|---:|---:|
| Adjustment | 0.890233276155981 | 0.791344080901693 | 0.009865867638690 |
| No adjustment | 0.887897935748603 | 0.826592076882386 | -0.027483934708643 |

These are author-deposited full-model values, not new portfolio solves in this review. [D1]

Consider the alternative `m=8`, `F=E=0`, **assuming `C(0)=0`, availability of that term, no separate mandatory-commitment cost, and the same optimizing operating-policy selection**. It has the same operating values and delivered service as the implemented noncancellable allocation, but avoids the `0.01` capacity cost. The principal's surplus becomes

\[
\Pi_{\rm adj}=0.019865867638690,\qquad
\Pi_0=-0.017483934708643.
\]

The improvement is exactly `0.01` in each regime. The arithmetic is independently reproduced from the transcribed source values in E1. This is not an assertion of a globally optimal contract or a reversal of the paper's adjusted-only participation example: adjustment still distinguishes the signs of principal surplus here. It shows that, when the term is selectable on the stated terms, the priced fee implementation is dominated by an already admitted hard-commitment implementation with the same service. [M2, D1, E1]

There are two coherent resolutions. The minimum term may be institutionally fixed or constrained for reasons the model specifies; then the fee frontier is conditional on that independently supplied commitment technology. Alternatively, compulsory operation can have its own enforceability constraint or cost `K(m)`. For identical implemented operating policies, the relevant comparison then involves `K(8)-K(1)` against `C(0.85)-C(0)`, not the latter cost alone. Either resolution would make the economic comparison interpretable. Merely appending a positive carrying cost to the surrender fee does not price the source of all commitment.

The point is not that a theoretical contract must solve an unrestricted mechanism-design problem. It is that an economically meaningful price comparison requires either comparable instruments or an explicit restriction excluding their substitution. R9 varies the compulsory term and calls the result a commitment frontier; it should therefore not leave the availability of the cheaper instrument implicit.

There is a related distinction between reducing compensation and improving procurement. Under binding participation and a common outside option,

\[
\Pi_{\rm adj}-\Pi_0
=b(\mathcal A_{\rm adj}-\mathcal A_0)
+(W_{\rm adj}-W_0)-(C_{\rm adj}-C_0).
\]

Policy inclusion controls the middle term, not delivered duration. A simple two-policy example in E1 has outside value `1` and service price `0.8`. An old policy has agent value `0.4` and duration `1`; an added policy has value `0.5` and duration `0.1`. The required grant falls from `0.6` to `0.5`, but principal surplus falls from `0.2` to `-0.42`. This is an illustrative example, **not the NBO calibration and not a counterexample to the paper's correctly conditional proposition**. It identifies why the new policy-inclusion order alone is too weak to deliver a general procurement mechanism.

**Required response.** State which commitment instruments are actually substitutable and on what resource/enforcement terms. Establish the resulting comparison in the specified economy, including the service response and agent-policy selection. A full optimal-contract solution is unnecessary; leaving an unpriced hard-commitment alternative beside the headline priced implementation is not.

## 4. R9-M3 — The successful fee box is a no-surrender implementation region

**Severity: an important limitation on the interpretation of the new evidence; connected to M1–M2, not an independent claim that the certificate is false.**

The statewise threshold result is a useful and correctly qualified implementation theorem. In particular, R9 distinguishes statewise equality from merely preserving two initial values. The reachable-state restriction is also appropriate: an enforcement requirement should not automatically include unrelated initial conditions. [M2, M3]

But the deposit itself implies a sharper description of the advertised successful fee box. Its sufficient uniform fee is `0.8348592805606`. The smallest fee in the certified interval is `0.85`, leaving

\[
0.85-0.8348592805606=0.0151407194394>0.
\]

Conditional on that deposited stored-array bound, at every eligible reachable node throughout the original law/benefit rectangle, surrender is strictly inferior to the mandatory continuation. Backward induction recovers the mandatory values. Accordingly, throughout this fee box,

\[
\mathcal S^r_\sigma=0,\qquad W^r_{\sigma,F}=0.
\]

The optimized values are locally constant in the fee, and the operating policies never use the new elective exit margin. The `F` dimension therefore supplies an **implementation interval**, not a region with an active surrender mechanism. This conclusion is analytical given the sufficient bound; I have not independently rerun its 1,617-state construction. [M2–M4, E1]

The two certified class differences remain meaningful:

\[
\Delta^{\rm adj}\in[0.0000686948833572,\;0.0003247296453481],
\]
\[
\Delta^0\in[-0.0003696772643877,\;-0.0000528012509051].
\]

They recover the original opposite-position comparison with finite fee-backed enforcement. That is a valid answer to whether formally prohibiting surrender is essential to implementing those values. It is not evidence that the comparison is generated by, or survives interaction with, a used surrender option. The manuscript already recognizes recovery; the economic contribution must be judged accordingly. [M4]

R9 deserves credit for preserving the genuinely active-margin evidence. At free surrender after one compulsory interval, the two regimes have identical class values and zero relative option at the reported center. At `F=0.70`, the relative option is approximately `-0.00341186`, although each class benefits from adjustment. At `F=0.80`, the center again has opposite rankings, but the original rectangle fails: the no-adjustment class difference at `(lambda,d)=(0,0.4)` is positive, approximately `0.00139238`. These observations show why the active margin matters; they are not hidden failures. [M4]

I do **not** require free surrender to preserve the original conclusion. Nor is an active-exit theorem a universal condition for publishing a contracting model. For this manuscript, however, the strongest successful new box is economically the old compulsory allocation with an implementation instrument. To make the active margin carry additional scientific weight, a revision could establish a nondegenerate region with positive elective-surrender exposure, a characterized adjustment mechanism, and the relevant participation conditions. Alternatively, a substantive dynamic theorem under implemented commitment could answer M1 directly. The essential requirement is a result beyond the existence of a sufficiently deterrent charge; it is not an obligation to expand the number of robustness tables indefinitely.

## 5. What is substantially resolved, and remaining technical boundaries

### 5.1 Investment permissions

The breakpoint argument is persuasive for its declared target. Conditional on a finite consumption/adjustment pair, the first proposed wealth coordinate is affine in risky share; the preference interpolation weights are independent of it; and the verified initial nonexit range keeps the within-period reward independent of risky share. The first-date continuation payoff is therefore continuous and piecewise affine. Endpoints and wealth-node crossings suffice. This is a useful exact reduction, not merely a denser scan. It does not optimize consumption, deliberate adjustment, or later controls continuously, and the paper does not claim otherwise. [M2, M3, C1]

The original optimizers are now displayed beside the decision certificate. Both financial permissions bind, both positions carry risk, and the no-deliberate-adjustment regime retains stochastic preferences. At the center, the long switches are approximately `0.7890095` and `0.8107837`; the short switches are approximately `0.5094806` and `0.4907037`. The permission derivatives and reoptimized benefit roots explain how the original benefit can move outside the opposite-choice interval. I regard this as a substantive response to R8-E2, not a reason to repeat the old complaint. [M4]

The remaining economic issue is not a missed risky-share grid point. It is that permission sensitivities do not connect the primitive adjustment theorem to the realized dynamic incentive. Likewise, the permission roots are explicitly local floating-point calculations, not certified global root-uniqueness results. They should retain that status.

### 5.2 Numerical target and evidence boundaries

R9 distinguishes the mathematical settlement constructor, stored arrays, and a diffusion or alternative protocol. Its Bellman perturbation account correctly identifies the reward, kernel-row, continuation-magnitude, and terminal errors needed for target transfer. The stated arithmetic allowance covers evaluation of the stored arrays; selected-control reconstruction is not a directed-rounding enclosure of the entire constructor. Those distinctions are disclosed, not newly discovered omissions that invalidate the finite-array theorem. [M2, M3, C1]

Similarly, the fee certificate uses the original finite action menu plus surrender, while the permission study enlarges only first-date risky shares. The text expressly declines to combine them into an unproved joint target. A subsequent joint claim would require a new reachable-support and optimization/error account; the present manuscript should not be accused of making that claim.

### 5.3 Methodological contribution and organization

The signed compression of transition-law upper information, its count comparison, and feasible-policy lower evaluation remain the most distinctive methodological objects. The related-literature section now recognizes parametric reward MDPs and distinguishes controlled models from dependency-sensitive parametric Markov-chain abstractions. Standard envelope logic, nested-policy-set monotonicity, and the backward stopping recovery argument should not be counted as separate new general principles. The manuscript itself attributes much of this background appropriately. [M5, M6, W1–W3]

The current comparison also retains mesh-only feasible lower policies and an adverse exact reusable structural-solver comparison. Consequently, this report does not infer neural necessity from a certificate result or demand a baseline already present. The residual editorial problem is focus: the title foregrounds neural operators, while the incremental mathematical contribution is a particular upper-bound compression and the latest economic additions are a specified commitment implementation. A clearer hierarchy would help, but retitling or shortening alone would not resolve M1–M2.

## 6. Independent execution and its limits

The accompanying `independent_audit.py` uses only Python's standard library and imports no author solver. It executed **4,029 exact-rational assertions** on finite toy models. Eighteen two-state models span horizons two through five, affine endpoint laws, signed rewards, substochastic kernels, and nested operating menus. The checks cover statewise fee sufficiency and necessity, initial-class implementation, monotonicity in the minimum term and benefit, adjustment-capacity ordering, and fee convexity/Lipschitz behavior. Eight additional two-date models are checked by exhaustive Markov-policy evaluation: **5,232 policy evaluations and 96 class–parameter comparisons**. All passed. These models test generic finite-model claims; they do not reproduce the portfolio calibration. [E1]

The program also runs **27** 65-digit Decimal primitive optimizations, recalculates the conservative primitive lower bound, and reproduces the commitment comparison and strict-fee slack from clearly marked transcribed inputs. Including those direction and diagnostic assertions gives **4,059 assertions in total**. The high-precision optimizer is not an interval proof; the uniform direction conclusion instead follows from the analytical inequalities in Section 2. Tests corroborate inspected arguments but do not prove general theorems.

I did **not** rebuild the full 1,617-state, 1,568-action portfolio kernels, rerun all R9 economic experiments, train networks, rebuild the NBO PDFs, or construct an interval enclosure of the transition constructor. All full-model portfolio values, timing observations inherited from prior comparisons, and regional fee bounds cited here are attributed to the pinned author deposit or the identified earlier reports. This distinction is essential to the evidentiary weight of the review.

## 7. What would change the recommendation

A persuasive next revision must answer the unresolved **dynamic mechanism** objection with a result that applies to the actual economic class or an explicitly justified connecting family. It must also settle the institutional comparability of the commitment instruments rather than interpret one instrument's carrying cost as the price of all commitment. The resulting economic proposition should make clear whether it concerns implemented compulsory operation or an active surrender margin, and connect that proposition to a genuinely matching certificate.

These requirements do not call for deleting the original theorem, concealing adverse results, claiming a diffusion limit, or abandoning the research program. Preserve the valid compression results, the primitive theorem, the original rectangle, the adverse free/intermediate-fee examples, the permission interventions, and the unfavorable computational comparisons. They are valuable evidence. What they do not yet supply is the missing economic connection. Another response that adds standard identities and reproduces the same compulsory allocation would improve the record without crossing the substantive threshold identified here.

**Recommendation: reject in its present form.** The mathematics inspected here has improved substantially; the remaining obstacle is the economic contribution and its integration, not the absence of another successful execution log.

## Source register

All manuscript and numerical paths below are pinned to the reviewed R9 commit unless a different historical commit is expressly given. Labels and function names identify substantive locations; branch names alone are not used as evidence of scientific revision.

- **M1 — Identity and response:** [REVISION_INDEX.md](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/REVISION_INDEX.md), [ECTA_R9.tex](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/ECTA_R9.tex), [SUPP_R9.tex](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/SUPP_R9.tex), and [response_to_referee.md](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r9-participation-permissions/response_to_referee.md).
- **M2 — Contracting propositions:** [04i_contracting.tex](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r9-participation-permissions/paper/04i_contracting.tex), especially `prop:r9_participation`, `prop:r9_enforcement`, `prop:r9_knots`, and `subsec:r9_certificate`.
- **M3 — Proofs and scope:** [S13_contract_proofs.tex](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r9-participation-permissions/paper/S13_contract_proofs.tex), including policy selection, reachable enforcement, breakpoint, and arithmetic/target-transfer discussions.
- **M4 — Executed economic evidence and optimizer table:** [05e_contract_evidence.tex](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r9-participation-permissions/paper/05e_contract_evidence.tex), [table_r9_initial.tex](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r9-participation-permissions/paper/table_r9_initial.tex), and [table_r9_benefit_frontiers.tex](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r9-participation-permissions/paper/table_r9_benefit_frontiers.tex).
- **M5 — Inherited primitive and dynamic arguments actually imported by R9:** [S11_economic_proofs.tex](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-16-r7/paper/S11_economic_proofs.tex) and [04g_decision_economics.tex](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r8-full-response/paper/04g_decision_economics.tex), especially `prop:r8_cardinal` and `prop:r8_mechanisms`.
- **M6 — Contribution and correspondence:** [01_introduction.tex](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r9-participation-permissions/paper/01_introduction.tex) and [04h_literature_correspondence.tex](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/revisions/2026-09-17-r8-full-response/paper/04h_literature_correspondence.tex).
- **C1 — Implementation inspected:** [contracts.py](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/replication/r9/contracts.py), [run.py](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/replication/r9/run.py), [validate.py](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/replication/r9/validate.py), and [README.md](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/replication/r9/README.md). Relevant functions are `Contract.pair`, `Contract.moments`, `upper_pair`, `FirstDateMenu.optimize`, `region_certificate`, `reachable_fee`, `permission_analysis`, and `procurement`.
- **D1 — Source of transcribed procurement quantities:** [replication/r9/output/procurement.json](https://github.com/TrillionniumFoundation/NBO/blob/8c1e0472279fb66a2419b63b3e35df028ecfdd78/replication/r9/output/procurement.json).
- **H1 — R8 economic-stress review:** [referee_report.md at 8c20474bca5b7388f5ba4640ec165f1ad8f5e91a](https://github.com/TrillionniumFoundation/NBO/blob/8c20474bca5b7388f5ba4640ec165f1ad8f5e91a/reviews/2026-09-17-econometrica-r8-economic-stress/referee_report.md).
- **H2 — Parallel R8 independent-mechanism review:** [referee_report.md at cd8596c4dce9d477bea86525d8e1ae7eb0aed9ec](https://github.com/TrillionniumFoundation/NBO/blob/cd8596c4dce9d477bea86525d8e1ae7eb0aed9ec/reviews/2026-09-17-econometrica-r8-independent-mechanism-audit/referee_report.md). Its recommendation and mechanism objection are not silently identified with H1.
- **E1 — New independent execution:** [independent_audit.py](independent_audit.py) and [independent_audit_results.json](independent_audit_results.json), deposited with this report. Full-model transcriptions and additional assumptions are explicitly marked.
- **W1 — Envelope background:** Milgrom, P., and I. Segal (2002), “Envelope Theorems for Arbitrary Choice Sets,” *Econometrica*, 70(2), 583–601; [author manuscript](https://web.stanford.edu/~isegal/envelope.pdf).
- **W2 — Regional parameter background:** Quatmann, T., C. Dehnert, N. Jansen, S. Junges, and J.-P. Katoen (2016), “Parameter Synthesis for Markov Models: Faster Than Ever,” [arXiv:1602.05113v2](https://arxiv.org/abs/1602.05113v2).
- **W3 — Dependency-sensitive pMC background:** Heck, L., T. Quatmann, J. Spel, J.-P. Katoen, and S. Junges (2025), “Generalized Parameter Lifting: Finer Abstractions for Parametric Markov Chains,” [arXiv:2504.05965v2](https://arxiv.org/abs/2504.05965v2). These references discipline the comparison; this review does not claim an exhaustive priority audit or an external-software benchmark.
