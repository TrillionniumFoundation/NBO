# Advisory Referee Report: Neural Bellman Operators — R11

**Recommendation: Reject in its present form.**  
**Review date:** 18 September 2026.  
**Standard:** Substantive Econometrica-style assessment.  
**Reviewed branch:** `revision/econometrica-r11-dynamic-contract-response-2026-09-18`.  
**Reviewed commit:** `3ab1ee131ee246fe1353ad3115451d0b72b60272`.  
**Status:** Owner-commissioned advisory report, not an appointment, report, or editorial decision issued by Econometrica.

## 1. Assessment for the editor

R11 is a genuine revision, not another branch pointing to an old report. It supplies a complete 72-page main paper, a 43-page supplement, new proofs, new code, deposited coefficient arrays, and executed results. The reachable-state transport proposition and the joint surrender/permission certificate constitute substantive progress. The earlier objection that a two-stage example was being substituted for a dynamic directional argument must be revised accordingly. Likewise, the author now prices both enforcement technologies and explicitly recovers the dominance of a free full compulsory term. Those repairs deserve credit. [M1–M4]

Nevertheless, I do not recommend publication. The central economic results still concern different decisions: an agent's financial-class ranking, the value of a counterfactual surrender option, and the minimum cost of implementing a *previously selected* noncancellable allocation. They use common primitives, but a common model does not by itself turn them into one institutional-choice result. My new R11 calculations show that the omitted procurement margin is material even after the new enforcement costs are included. A principal allowed to choose between two initial sign mandates prefers the positive mandate in both adjustment regimes at the central implementing contracts, whereas the unadjusted agent prefers the nonpositive class. This is not a contradiction of the carefully conditional implementation proposition. It is a reason not to interpret that proposition as closing the economic decision problem. [E1]

The computational claims also require a more discriminating verification chain. I completed the entire R11 scientific runner and its supplied validator. The economic signs reproduced, and the largest difference across the 107 regenerated certificate arrays was only `4.440892098500626e-16`. Yet 53 of 155 primitive-array manifest entries did not reproduce bit for bit. Moreover, in a temporary copy, replacing a central upper-coefficient array by the constant `-1,000,000` still produced an all-passed result from the advertised independent validator. My separate coefficient reduction immediately detected the resulting inconsistent interval. These observations do not falsify the original economic inequalities. They do show that numerical agreement, target identity, and independent certification are not yet connected by the supplied reproduction procedure. [E2–E4]

The strongest prospective contribution remains a specific computational one: signed compression of changing-law upper information, combined with feasible-policy polynomials and a verifiable economic decision. My objection is not that every component is wrong. It is that the paper has not yet made a sufficiently compelling, integrated economic and methodological contribution for Econometrica. Another additive section and another successful self-check would not, by themselves, answer this objection.

## 2. What was actually reviewed and executed

The authoritative revision index identifies R11 at the reviewed commit. The similarly named `revision/econometrica-r11-integrated-mechanism-2026-09-18` branch is not the latest completed science. This report does **not** repeat the earlier version-status criticism. I inspected the new main and supplement sources, the inherited operator/error/transition-law and contracting arguments on which they depend, the response, numerical constructors, certification routines, and historical review concerns. I visually checked main pages 8–9 and supplement pages 40 and 42 against their sources. Historical extensions were examined selectively; I do not claim to have independently reproved every extension or retrained the neural proposals. [M1–M5]

The R11 package came from GitHub Actions run `35308875819`, artifact `10532990335`; its ZIP hash matches the recorded artifact digest. The inherited executable sources came from artifact `10497729014` at `755b507870b54a100616b0658eba9a031eef2833`. GitHub's comparison to the reviewed commit shows no modifications to those inherited scientific files: the differences consist of new R11 and review files and the appended revision index. Overlaying the R11 package therefore reconstructed the executable scientific inputs, not every administrative file in the later repository tree. The artifact records scientific source commit `853a7856827b46efe94bf994ffca79669bdb1128` and final deposit commit `3ab1ee1...`. A successful run at an earlier workflow head is not silently attributed to the final deposit head. [E4]

Three evidence classes are kept separate. First, a complete fresh execution reproduced the author's calculations on locally regenerated primitives. Second, my own de Casteljau implementation recomputed the regional difference bounds from the *original deposited* coefficients. Third, additional economic reoptimizations used the author's solver and moment primitives, while a temporary-fixture mutation tested the scope of the author's validator. None of these is described as an independent interval implementation of the entire Bellman system. The audit script, results, logs, identities, and replay comparison accompany this report.

## 3. Repairs that should be accepted, not litigated again

The transport proposition has a coherent backward-induction argument. It compares every negative-drift action with a feasible zero-drift counterpart having the same financial controls, bounds the signed continuation difference, and checks a support tube closed under all feasible transitions. It does not infer direction from the chosen initial control. The support has `1, 30, 100, 203, 342, 495, 637, 735, 833` nodes over the nine dates. The reported strict comparison survives its stated numerical allowance; the least slack exceeds `0.000070902`. Frozen proposals are separately checked. I found no counterexample to this proposition under its stated enclosure and target assumptions. [M2, M3; E2]

The joint-region proof also avoids a previously important pitfall. A feasible lower policy is fixed across benefit/fee corners and Bernstein coefficients before taking the minimum. Policy maximization is outside that minimum. Permission monotonicity is used conservatively, with smaller permissions for lower policies and larger permissions for upper values. This is a continuum argument, not interpolation between six interior solutions. My independent reduction of the deposited coefficients reproduced all six interval endpoints for both upper methods with zero binary64 discrepancy. The three comparisons, approximately, are:

| Regional comparison | Independently reduced interval |
|---|---:|
| Adjusted positive minus nonpositive value | `[0.0001876285083493, 0.0002023955467600]` |
| Unadjusted positive minus nonpositive value | `[-0.0001792986622546, -0.0001221851436102]` |
| Unadjusted positive class: surrender minus noncancellable value | `[0.0000347089579420, 0.0000864510989614]` |

These are checks of the deposited coefficient reduction, conditional on the validity of those coefficients as value bounds. They are not an independent proof of their primitive-to-coefficient construction. [M3; E3]

The surrender interpretation is now appropriately qualified. The positive unadjusted class has a strictly valuable surrender option, but the unconstrained unadjusted agent selects the nonpositive class. R11 does not claim that this selected agent surrenders. The argument that a sufficiently near-optimal positive-class policy must have positive elective-surrender incidence is valid under the stated common-payoff comparison. Discounted incidence is not called an undiscounted or diffusion hitting probability. [M2, M3]

The enforcement comparison has also improved. Capacity cost and compulsory-term cost are both included; the positive-part participation formula is retained; weak implementation at a stopping tie is distinguished from strict implementation and its infimum. The active-surrender box is not conflated with the earlier inactive implementation interval. Adverse permission and surrender experiments, the alternative initial state, and unfavorable computational controls remain visible. These are substantive corrections, not defects to be rediscovered under different wording. [M2–M5]

## 4. E1 — The priced implementation result still does not select the economic allocation

### 4.1 The missing comparison

Main Proposition 3 fixes an operating policy from the noncancellable agent optimum, writes its value as `W^r = max_sigma W^r_sigma`, and minimizes the cost of implementing that selected allocation. The resulting formula

\[
P_r=\min_m\{[G(x_0)-W^r+C(F_r^*(m))]_+ +D(m)\}
\]

is meaningful for its specified implementation technology. It prices *how to implement*, after fixing *what to implement*. It does not compare the principal's returns across different financial allocations. The explicit disclaimer of unrestricted mechanism design is correct, but does not resolve this narrower distinction. [M2, lines 95–121; M3, Section S.14.4]

Consider only two sign mandates, not an unrestricted contract space. Within each mandate retain the author's agent optimization, outside option, fee recipient, capacity cost, term cost, and policy selection. Let the principal offer the corresponding minimum signing grant. Then

\[
q^r_\sigma=[G(x_0)-W^r_\sigma+C(E)]_+,
\qquad
\Pi^r_\sigma(b)=bA^r_\sigma-q^r_\sigma-D(m).
\]

When both participation constraints bind and the same enforcement instrument is used within a regime,

\[
\Pi^r_+(b)-\Pi^r_-(b)
=\Delta^r+b(A^r_+-A^r_-).
\tag{E1}
\]

The additional term is the difference in the service the principal buys. The service price `b` is not the operating-benefit parameter `d`. Outside binding participation, the positive parts must remain. Equation (E1) is elementary accounting, not a proposed new theorem; its purpose is to identify the payoff that a procurement-choice certificate must actually control.

### 4.2 Fresh R11 experiment, including the newly priced institutions

I reoptimized the central contract `(lambda,d)=(0.125,0.425)` with `C(E)=0.02 E^2` and `D(m)=kappa(m-1)/8`. For `kappa = 0, 0.01, 0.02`, the R11 weak-cost minimizers are respectively terms `8, 7, 1`. For terms below eight I used the computed threshold plus `1e-5`, reoptimized, and checked that both implemented class values reproduce the noncancellable values. Thus the comparison does not depend on an unspecified stopping tie. It uses the selected R11 institution and a strict implementation perturbation, not a claim of attainment of the strict-incentive cost infimum. [E1]

For all three institution choices, the within-regime differences are:

| Regime | Agent value difference | Service difference | Principal surplus difference at `b=1` |
|---|---:|---:|---:|
| Adjustment | `+0.000196740684027` | `+0.002303043895612` | `+0.002499784579639` |
| No adjustment | `-0.000209326961178` | `+0.002335340407378` | `+0.002126013446200` |

All twelve class-specific implementing offers in this experiment are feasible at `b=1`. The smallest principal surplus is approximately `0.05806881`. At `kappa=0.02`, for example, the unadjusted positive and nonpositive offers yield principal surpluses `0.06019482` and `0.05806881`. The principal prefers the positive mandate even though the unadjusted agent prefers the nonpositive class under a common grant. Pricing the compulsory term and guarantee therefore does not eliminate the allocation-selection issue documented in the preceding procurement review. [E1; H1]

I also tested the *actual midpoint of the new box*, `(lambda,d,F,L,S)=(0.125,0.42425,0.8,0.8,0.5)`, taking `E=F`, `m=1`, and the same capacity technology. In the unadjusted regime, the agent difference is `-0.000150630486`, but the service difference is `-0.054969148101`; the principal difference at `b=1` is `-0.055119778587`. The positive-class discounted surrender incidence is `0.068995145990`. Both offers remain feasible. The adjusted principal instead prefers the positive class. Active surrender changes the procurement comparison through service, not merely through the small certified agent-value difference. These are pointwise reoptimizations, not a continuum procurement theorem or proof that this fee is optimal. [E1]

### 4.3 Required response

Declare who chooses the sign, permissions, fee, term, and grant, and what is contractible. An imposed agent mandate is legitimate, but then its institutional implementation is conditional. A principal choosing among even two mandates requires the service and participation comparison, not only `Delta`. The manuscript need not solve unrestricted mechanism design. It needs a central economic decision whose timing, feasible instruments, payoff comparison, and numerical certificate agree. Either justify the instrument restriction economically or establish the appropriate finite-menu procurement result. The present conditional Proposition 3 is not false; the claimed integration is insufficiently persuasive.

## 5. R1 — Exact target identity is not closed by the reproduction instructions

The paper deliberately identifies a finite stored-array target and distinguishes its arithmetic from constructor and diffusion errors. That is an acceptable mathematical object; I do not demand a diffusion theorem. Precisely because this is the object, its input identity matters. [M2, line 128; M3, Section S.14.5]

The prescribed complete rerun rebuilt the primitive arrays. It used the listed Python/NumPy/SciPy versions `3.13.5/2.3.5/1.17.0`, but a different Python build and native environment. Comparing its manifest with the untouched deposit produced **53 unequal entries out of 155**. The differences concern reward/settlement/exit-discount arrays; the transition CSR identities and first-date manifest entries match. Across the 107 regenerated certificate arrays, the largest absolute difference was `4.440892098500626e-16`; policy and first-action arrays matched. All substantive signs and all supplied checks passed. This is excellent numerical agreement, but it is not a bit-identical rerun of the stated primitive target. The full mismatching-key list is deposited. [E2, E4]

Supplement page 42 expressly anticipates this possibility and says to check the identities or treat rebuilt arrays as a separately identified target. I credit that disclosure. The operational problem is that the advertised runner overwrites the local manifest, while the validator does not compare it with an immutable expected manifest. The later primitive operators are reconstructed by `SparseKernel`/`Economy`; the supplied first-date operator and certificate archives do not provide a canonical-loading path for those later primitives. A reader following the README can obtain a new manifest and an all-passed record without establishing the identity of the original theorem's target. [C1–C3]

The requested repair is not to deposit a particular file format or to claim that last-bit changes alter a decision. Supply either retrievable canonical primitive inputs with a hash-enforcing read path, a deterministic environment that actually reproduces their identities, or a checked operator-transfer enclosure that connects the regenerated target to the original one. Preserve the expected manifest instead of replacing the reference during the check. A failed identity check must be reported as such, separately from a successful computation on new arrays. The disclosed initial-value transfer budget `1.7354e-5` is a useful requirement, not an estimated transfer error or a substitute for a statewise transport account.

## 6. R2 — The independent validator can accept a destroyed certificate

This is a concrete test of the supplied verifier, not speculation about possible implementation bugs. I copied the untouched R11 outputs into a temporary directory and changed only

`certificate_arrays.npz['chord.upper.0.0.positive']`

to the constant `-1,000,000`. All other files, including the favorable JSON summaries, were left unchanged. Running `replication/r11/validate.py` against that copy returned `all_passed: true`, including `both_joint_certificates` and `deposited_coefficients_support_and_feasibility`. The independent reduction of the modified coefficients instead produced an adjusted interval with lower endpoint about `0.0001876285` and upper endpoint about `-999999.2398807`: an immediate contradiction. The temporary directory was removed. No original scientific file or remote result was altered. [E3]

The reason is visible in the code. Lines 10–19 test favorable numbers already recorded in JSON. Lines 20–28 check finiteness, interval ordering for continuation enclosures, support counts, positive lower first actions, and nonnegative first-date transition entries. They do not reconstruct the reported regional bounds from the deposited coefficient arrays. Nor does this post-processing validator independently reconstruct all Bellman upper inequalities or the signed transport comparisons. Its name and success record therefore support a narrower claim than an independent certificate checker. [C3]

This does **not** show that the original coefficients are invalid. On the contrary, my reduction of the original coefficients exactly recovers their advertised bounds, and the full scientific runner independently executes more calculations than this post-processor. The objection is the missing link between the deposited mathematical witnesses and the assertion that those witnesses have been checked.

A revised verifier should consume immutable primitive and certificate identities, recompute the extrema with the proper fixed-policy ordering, test lower-policy feasibility and upper/transport inequalities at the claimed scope, and reject a corrupted coefficient, policy, transition row, or stale summary. Selected-control reconstruction and six interior points remain valuable cross-checks, but they are not substitutes for checking a uniform regional witness. A negative test of a disposable fixture is a particularly inexpensive way to prevent recurrence.

## 7. M1 — Directional elimination is not yet an economically predictive class mechanism

The new dynamic transport result is a valid sufficient condition under its premises, and its certified domain is materially stronger than nine initial-state equalities. I withdraw the old objection at that level. The remaining issue concerns what explains the *difference between financial classes*, rather than what eliminates downward drift in either class. [M2, lines 18–64; M3, Sections S.14.1–S.14.2]

The decomposition of each adjustment option into a current-drift gain and exposure to future adjustment value is exact when the selected first financial controls coincide. R11 checks that premise and retains the omitted financial-replacement term when required. At the reported noncancellable center, the relative local component is approximately `0.0000503943`, and the relative future component is `0.0003556734`. This is useful accounting. It does not, by itself, give a primitive ordering of the two classes' future adjustment exposure. Nonnegative adjustment value at each state does not determine the sign of its expectation under a signed difference of class kernels.

There is also a domain distinction worth making visible: the illustrative decomposition uses `d=0.425`, whereas the new joint theorem uses `d in [0.424,0.4245]`. It is not a decomposition certified uniformly on that theorem's box. This is not a logical contradiction; the text should not let proximity of the examples stand in for the missing uniform mechanism.

The five-dimensional region is genuine, but three coordinates have very small widths: the fee and long permission each vary by `0.0002`, as does the short permission; the benefit varies by `0.0005`. Nearby adverse permission experiments are honestly retained. Those facts establish a local effect and its fragility, not its general economic importance. A useful next result would connect interpretable continuation or exposure restrictions to the class differential, or map economically justified parameter regions and changes of the dominant component. It need not assert global monotonicity, a maximal region, or immunity to adverse cases. The bar is a transferable economic insight beyond the fact that a carefully specified local comparison has a certified sign.

## 8. C1 — The methodological increment needs a stronger central demonstration

The revised literature positioning is substantially more accurate. Alegre, Bazzan, and da Silva (2022) relate successor features, optimistic linear support, and policy transfer for linearly expressible rewards. Quatmann et al. (2016) develop parameter lifting with extremal nondeterministic choices for regional probabilistic verification; Junges et al. (2019, revised 2023) give a broader account of regional analysis for parametric Markov chains and decision processes. These comparisons concern related structures, not an assertion that their theorems are identical to R11's signed compression. The manuscript already acknowledges the reward-MDP correspondence and relevant regional methods. An allegation of missing this entire literature would be inaccurate. [L1–L3; M5]

The paper does execute matched chord/count work accounts and retains earlier precision/work and neural-free comparisons. The unresolved editorial issue is how consequential the specific increment is in the new headline experiment. From the original deposited arrays, I measured the chord coefficients above the line joining their endpoint coefficients. Across all three targets, both classes, and all reward corners, the largest correction is about `2.81919e-9`; the largest chord/count coefficient difference is about `1.20260e-8`. These are below the charged `1e-7` per-value allowance. [E3]

An uncorrected chord is **not** thereby proved valid. The signed term cannot simply be deleted from a theorem because it is numerically small. Rather, the observation shows that this new economic box is not a demanding demonstration of the incremental correction's economic importance. The equal final regional intervals are not evidence that the methods are generally equivalent. The earlier broader frontiers remain relevant and should be synthesized into the central contribution, including policy-switching behavior, economically meaningful accuracy, and total work. I do not require neural indispensability or claim that the earlier controls are absent. I require a clear account of what a researcher learns or computes materially better because of the particular new result.

## 9. Organization and the standard for a further revision

The main paper and supplement now total 115 pages, with the main source importing large blocks from R6 through R9 around the new opening section. Preserving historical science in the repository is valuable. Making the reader reconstruct the contribution through a succession of accumulated results is not. The abstract, opening results, computational comparison, and conclusion should identify the same economic question and the same methodological increment. Historical material need not be deleted: it can remain fully available with explicit dependencies and an authoritative reading order. [M1, M4]

For another substantive assessment, the following are the minimum responses, not a declaration-of-completion checklist:

| Concern | What would answer it |
|---|---|
| E1: economic decision | A justified contractible-instrument menu and a certificate for the relevant agent or principal payoff, including service and participation when procurement is claimed. |
| R1: target identity | A hash-enforcing canonical-input or deterministic-reproduction path, or an explicit checked transfer enclosure; expected and regenerated identities must remain distinguishable. |
| R2: verifier scope | A witness-driven checker that rejects the deposited mutation test and checks the claimed regional inequalities rather than trusting their JSON summaries. |
| M1/C1: significance | An interpretable class-specific economic mechanism and a central demonstration of the changing-law increment, using the existing adverse cases and computational controls rather than hiding them. |

The first issue determines the economic interpretation; the next two determine what the numerical verification establishes; the last determines the contribution's importance. They should not be answered by more version labels, a longer response letter, or treating every passed script as a mathematical proof. Conversely, genuine R11 advances should not be erased merely because the recommendation remains negative. My recommendation concerns the present manuscript's contribution and evidentiary chain, not an assertion that its central conditional propositions have been refuted.

## 10. Source and evidence map

All repository paths below refer to the reviewed commit unless another commit is stated. Main and supplement page numbers are the printed/PDF page numbers of the deposited R11 documents.

**M1.** `REVISION_INDEX.md`, `ECTA_R11.tex`, `SUPP_R11.tex`; the complete PDFs in `revisions/2026-09-18-r11-dynamic-contract/`.

**M2.** `revisions/2026-09-18-r11-dynamic-contract/paper/02_integrated_economics.tex`, particularly lines 18–64, 66–93, 95–121, and 123–128; main pp. 6–10.

**M3.** `revisions/2026-09-18-r11-dynamic-contract/paper/S14_integrated_proofs.tex`, Sections S.14.1–S.14.5; supplement pp. 38–42.

**M4.** The same revision directory's `response_to_referee.md`, `execution_summary.md`, `preservation_map.md`, `paper/01_introduction.tex`, and `paper/07_conclusion.tex`.

**M5.** `revisions/2026-09-16-r6/paper/02_operators.tex`, `03_approximation.tex`, `04b_contract_transfer.tex`, `04c_kernel_transfer.tex`; `revisions/2026-09-17-r8-full-response/paper/04e_comparative_oracles.tex` and `04h_literature_correspondence.tex`; `revisions/2026-09-17-r9-participation-permissions/paper/04i_contracting.tex`.

**C1.** `replication/r11/README.md`; `core.py`, especially lines 147–255; `run.py`, especially lines 117–143 and 161–215.

**C2.** `replication/r8/model.py`, `SparseKernel` and `Economy`; `replication/r9/contracts.py`, `FirstDateMenu`, `first_moments`, and `arithmetic_audit`.

**C3.** `replication/r11/validate.py`, especially lines 8–28; original Git blob `5e97ca1c709f91092b6c5f9c420c623494b12786`.

**E1.** This review's `reviewer_audit.py` and `reviewer_results.json`, `economic_experiments`. These are new model reoptimizations, not copied historical review outputs.

**E2.** This review's `execution_logs.txt` and `replay_comparison.json`; full fresh R11 execution and comparison against the untouched original artifact.

**E3.** This review's `reviewer_results.json`, independent coefficient reduction, chord corrections, and temporary-fixture validator mutation test.

**E4.** This review's `review_manifest.json`: artifact hashes, scientific-source identities, execution environment, scope, and provenance.

**H1.** `reviews/2026-09-18-econometrica-r9-r11-procurement-mechanism/referee_report.md` at `fa3fc96373b6170b20700fde35889308650e3b1f`. Its economic concern was considered independently of the obsolete R11-version observation. R11's own response identifies the earlier report at `30548ad06852cc0a447dedf1e63cc9e7f79f6c06` as its response target.

**L1.** Alegre, Lucas N., Ana L. C. Bazzan, and Bruno C. da Silva (2022), “Optimistic Linear Support and Successor Features as a Basis for Optimal Policy Transfer,” *Proceedings of Machine Learning Research*, 162, 394–413. Author preprint: https://arxiv.org/abs/2206.11326.

**L2.** Quatmann, Tim, Christian Dehnert, Nils Jansen, Sebastian Junges, and Joost-Pieter Katoen (2016), “Parameter Synthesis for Markov Models: Faster Than Ever.” Author preprint, version 2: https://arxiv.org/abs/1602.05113v2; the parameter-lifting construction and Figure 1 were inspected.

**L3.** Junges, Sebastian, Erika Ábrahám, Christian Hensel, Nils Jansen, Joost-Pieter Katoen, Tim Quatmann, and Matthias Volk (2019; revised 2023), “Parameter Synthesis for Markov Models: Covering the Parameter Space.” Author preprint, version 2: https://arxiv.org/abs/1903.07993v2.
