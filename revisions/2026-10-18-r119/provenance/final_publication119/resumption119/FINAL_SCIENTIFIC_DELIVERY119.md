# Final scientific delivery assessment — R119

**Assessment date:** 19 October 2026 (UTC).  
**Author source reviewed:** 6250abfd317f3b2a56cb1303eb5ce78249bf4042 (S).  
**Scope:** focused, read-only scientific delivery assessment of the published main text, supplement additions, retained economic/operator definitions, controlling-report response and completed D outcome receipts. Source objects were read directly at S through GitHub after the resumed local environment was found to retain directories without regular files. No scientific program, test, compiler, timer or package builder was run; no native source, PDF, ZIP or Git object was modified. After root restored the published files, a further read-only check matched all 28 inspected local scientific/report files (294,748 bytes) to the GitHub-retrieved S blob identities, with no mismatch. This receipt is an additional assessment, not a new experiment, literature-priority search or independent replay of every historical theorem.

## Delivery judgment

R119 supplies a coherent author revision of **Neural Bellman Operators** within the original recursive-decision research programme. Its strongest new result is a deterministic tail-information upper construction with the same risk-level dependence as the retained lower bound. It connects that information to an outward, all-action certificate for the unchanged nested-AVaR investment criterion, and implements bounded and packed preliminary evaluation before the original complete fallback. The completed numerical development and independent D validation make the cost and economic interpretation materially more credible.

The scientific increment is **shared information acquisition and original-policy qualification**. It does not establish a neural-exclusive representation advantage or a new policy improvement in the A–C catalogue. The strongest conventional quadratic control remains both economically better than ReLU on the catalogue mean and cheaper in the reported full-catalogue component comparison. The paper and response state those limits expressly; they are unresolved research requirements, not editorial acceptance or blanket closure of the referee's concerns. See [main introduction][intro], [original NBO construction][core], [numerical account][study] and [author response B1–B10/M1–M10][response].

## Exact theorem scope and ownership

1. **Tail-uniform deterministic point information** — labels thm:tailinformation119 and supp:activetail119. For a convex K-Lipschitz function on the scalar uniform support [-R,R], let t=1-alpha, L=2R alpha and H(u)=integral from u to u+L of f. Its derivative D(u)=f(u+L)-f(u) is monotone and 2K-Lipschitz. The complement of a minimizing central interval is an optimal feasible AVaR tail, including endpoint and flat-threshold cases. After m exact sign bisections, returning the **midpoint of the final retained bracket** gives tail-location loss at most KRt·4^(-m)/2. At most n+1 nonempty selected-tail cells yield a certified interval of width at most

   \[
   KRt\{n^{-2}+\tfrac12 4^{-m}\}.
   \]

   With m=ceil(log2 n), the width is at most 3KRt/(2n²), using at most 2n+2ceil(log2 n)+8 distinct exact values, including localization. Every sound deterministic adaptive N-query interval procedure has worst-case width at least KRt/[6(N+1)²]. The proof supplies the conservative upper constant (75/2)KRt/N² for N>=32. Thus the matching order is KR(1-alpha)N^(-2), uniformly for alpha in [0,1); alpha=0 uses ordinary integration and alpha=1 is excluded. Formula/derivative/integral access, randomized minimax optimality, bit complexity and multivariate tractability are outside this theorem. The **lower bound is retained**; the new upper algorithm closes the previous tail-factor mismatch. Classical AVaR duality and midpoint/secant ingredients are credited. [Statement][tail]; [complete proof][tailproof].

2. **Original-policy certificate from an inexact feasible tail** — thm:investmenttail119. The actual investment primitives give V1 state strong-convexity modulus (4-5 beta/4)/d, innovation modulus **181/64** at beta=15/16, innovation Lipschitz bound **15**, and action modulus **2**. An outward bracket [d-,d+] for the two original endpoint values bounds the tail defect by

   \[
   \kappa(u)=\frac1{2Rt}\max_{d\in\{d_-,d_+\}}
      \left[-\min_{v\in[-R,R-L]}
        \{d(v-u)+(181/64)L(v-u)^2/2\}\right].
   \]

   The inner minimizer is the constrained projection; uncertain signs enlarge the defect. A fixed feasible density and global V1 supports give the all-action quadratic W+s(v-a)+(v-a)². Minimizing it over the **entire original feasible action interval**, with slope uncertainty retained, bounds V0 below. The policy interval is S+h+beta times [r-, r+ + kappa + epsilon1], where **epsilon1=2^(-20)** belongs to the unchanged deployed terminal controller. No convexity of that deployed policy value or differentiation through its rounding is assumed. The actual first-date acceptance limits remain regret **1/256** and policy-width **1/8192**. [Statement][tail]; [proof and boundary cases][tailproof]; [unchanged economic criterion][economy].

3. **Bounded preliminary work and packing** — prop:budgetedtail119 and rem:fusedtail119. For the implemented risk levels 1/2 and 3/4, the two-level prelude (2 then 4 cells per nonempty tail) purchases at most **30 outward terminal payloads** and **16 floating proposal values** per proposed action; a one-sided tail needs at most **16 outward** payloads. The precise outward count is 2+14p for p=1 or 2 nonempty tails. The defect endpoints are cached once; repeated requested payloads remain paid. Floating signs propose a feasible cut and never certify it. The complete original 128-bin fallback, repair and exact recovery remain available and charged. Packing preserves the indexed original point requests and sound aggregation, but batch-dependent fallback can change valid interval endpoints; policy identity is an empirical check. Neither proposition proves wall-clock dominance. The separate precision allocation minimizes a declared continuous work model with A,B>0, not a globally optimal economic discovery process. [Prelude][budget]; [proof][budgetproof]; [packing proof][packingproof].

4. **Coupled action certificates and signed recursive transport** — thm:coupled119 and prop:nearactive119. For a common feasible risk law q, the exact difference is E_q(Y-X)+k_Y(q)-k_X(q); both nonnegative witness slacks are retained. AVaR's atom-safe remainder is bounded by E(delta-|X-eta|)_+/t, and by C·delta^(kappa+1)/[t(kappa+1)] under the stated margin condition. A positive quantile atom generally precludes a positive margin exponent. An original complete-policy contrast needs only **plus/minus beta epsilon1**, because both continuation errors are one-sided; identical complete policies have exact zero contrast. Signed recursion retains the reference dual penalty and needs only laws with slack <=osc(D), or <=osc(D)+r under reference uncertainty r, without requiring an attained maximizer. A difference of convex continuations is not silently integrated as convex. These proofs integrate the attributed R111/R112 question; **A–C do not execute a new paired-policy-improvement algorithm**. [Statements][coupled]; [proofs][coupledproof].

5. **Foundations, gradients and continuous-time boundary scope.** The new foundations explicitly prove compact finite-horizon continuous Bellman values, Borel minimizers and comparison against the specified adapted history policies. Risk-kernel measurability and essential-uniform continuity are explicit; uniqueness of value does not imply uniqueness of an actor without extra curvature. Original invariance is **[1/32,27/32]^d**, capacity lies in **[1/8,1/4]**, and the constrained envelope includes **-lambda grad A**. The deployed observation transfer is 2^(-21)+30·2^(-40)<2^(-20). The full half-squared-residual gradient includes future and actor paths; it is not a training convergence theorem. Infinite-horizon contraction is restricted to beta<1 and its declared function classes. The stopped Brownian BSDE certificate is

   \[
   e^{L_yT}(\eta_-+\eta_+)+
   \int_0^T e^{L_ys}\{e_-(s)+e_+(s)\}\,ds,
   \]

   with bounded smooth test functions, Lipschitz measurable drivers, admissible well-posed controls and the actual stopping payoff. General recursive utility is not automatically cash invariant, a ReLU critic is not automatically a classical Ito test function, and a fully coupled NDU/FBSDE is not identified with the investment AVaR experiment. These are explicit classical foundations and corrections, not novel fixed-point claims. [Full foundations][foundations]; [retained BSDE theorem][bridge]; [original-formulation corrigendum][correction].

## Economic and execution interpretation

The comparison holds the declared two-date nonlinear investment technology, continuous uniform innovation, state-dependent capacity, nested upper-cost AVaR, deployed terminal controller and qualification targets fixed. The earlier expected-cost model and the separate Brownian recursive-utility problem remain distinct criteria. Eight arms receive the common acquired terminal labels, and the equivalent conventional hinge receives the ReLU features/coefficients and full standalone acquisition charge. [Economic primitives][economy]; [protocol and complete comparison][study].

| Frozen phase | Primary decisions | Fresh-process timing decisions | Median service-time wins against its contemporaneous geometric control |
|---|---:|---:|---:|
| A: active tail | 6,912 | 10,752 | 1 of 16 |
| B: bounded prelude | 11,520 | 17,920 | 2 of 16 |
| C: packed evaluation | 13,824 | 21,504 | 10 of 16 |

These are 16 risk/representation cells and seven fresh timing processes per phase. B and C are explicitly development after observing their predecessors on the known catalogue; later clocks do not replace earlier adverse observations. C improves all 16 median cells relative to its budgeted and compiled controls, but preserves all six losses to geometric evaluation. C's ReLU packed/geometric ratios are **0.8614** and **0.8494**. These are observed service clocks, not population confidence intervals or hardware-general speed guarantees. [A/B evidence][study]; [C evidence][studyc].

All services return the same complete policy within each arm/risk/state comparison in the observed catalogue. Their economic contrasts are therefore exactly zero; narrower certificates and packing do not lower those policy costs. C's acquisition-plus-load-plus-144-decision component account remains adverse for ReLU: **0.1485 seconds** for quadratic/geometric versus **0.3407** for ReLU/packed at risk 1/2; **0.1417** for quadratic/packed versus **0.3131** for ReLU/packed at risk 3/4. Additional author-side validation and broader process work retain separate costs. Reported regret and action-distance figures are numerical **upper bounds**, not exact action errors or an independent determination of the global optimum. [C interpretation][studyc]; [A/B regret and adoption account][study].

### Independently implemented D outcome

The read-only assessment retrieved the **actual completed** D numerical review, reporter receipt and external launcher record at S. They confirm source cafd38aedc5bcbddf5aafee2481fbf5e9a267bab, exit zero, **983 exact policy keys**, **126,807 terminal contexts**, **652,774 original validation checks**, no failed key, all **96 means**, **56 arm contrasts** and **240 service-pair identities**. The separate reporter records **590,818** further checks; that count must not be confused with the original validation count.

D independently reconstructs the original primitives and rational last-date bounds on a fixed **64-cell** whole-support mesh. Its threshold-wise Jensen/repeated-endpoint secant proof encloses original optimal-continuation Q; **beta·2^(-20)** is then added once for the unchanged future-controller J allowance. It does not directly rerun that floating controller or independently solve date-zero global regret. All 13,824 service intervals and 983 shared-compiler references overlap D. Exactly 10,300 service intervals contain D, while 3,524 lie within D; all 983 fine reference intervals lie within the broader D interval. Overlap or that reverse containment does not validate the fine endpoints. [D proof][dproof]; [main D account][studyd]; [completed numerical review][dreview].

The 56 contrast signs are **32 negative, 20 positive, 2 exact zero and 2 unresolved** in their fixed left-minus-right orientation. Reading the exact stored Fractions and rendering outward to the displayed precision reproduces:

| Risk | Independent ReLU-minus-quadratic mean original cost |
|---|---|
| 1/2 | [17.4360, 19.2238] × 10^(-6) |
| 3/4 | [17.5331, 19.3595] × 10^(-6) |

Both establish strictly lower mean original cost for quadratic; ReLU/hinge contrasts remain exactly zero. A favorable neural sign was not a pass condition. The actual external validation time is **1697.331508 seconds**, with **1693.603548 CPU seconds**, additional to the unchanged A–C service clocks. D is validation of the known C catalogue, not an unseen population sample. [Outcome record][dreview]; [external execution][dlaunch]; [full D interpretation][developmentd].

## Remaining substantive research requirements

- **Neural-specific value under matched resources:** the exact conventional hinge shares the network's function and policies, and quadratic retains the reported complete-cost/economic advantage. Unknown-geometry acquisition and an expanded tournament including adaptive conventional representations remain unestablished.
- **Prospective action-aware learning:** the new certificate controls a decision-relevant gap, but A–C leave least-squares fitting unchanged. They do not reverse the retained R97 result of 36 improved residual spans with first-proposal rejections rising from 644 to 757, or prove training/optimizer convergence. A new frozen acquisition-to-service experiment is still needed.
- **Full scaling:** the exact information theorem is scalar and uniform-law; d=2,4,8 primitive checks are not a learned multi-horizon, multi-action, multivariate-risk service. Descendant solves, memory, finite-precision work and failed paths still need complete accounting.
- **Economic adoption and applications:** the conditional adoption inequality needs an actual workload, horizon, compute prices and value per economic-loss unit. No calibrated institutional adoption or welfare result is established. Portfolio, controlled-preference, temporal-self and game programmes retain their own corrected domains, objectives, deviations and missing validation; archival figures are not current evidence.
- **Statistical and continuous-time scope:** no independent population inference is attached to the deterministic catalogue or known-catalogue D check. General fully coupled NDU/FBSDE verification, singular recursive utilities, weak/smoothed nonsmooth critics and relevant model-specific existence/selection conditions remain separate work.

These boundaries are stated directly in response B1–B8/B10 and M3–M9, the original-formulation corrigendum and the conclusion. They should remain explicit in delivery; the presence of a detailed response does not certify every scientific request as completed. [Response][response]; [corrigendum][correction]; [conclusion][conclusion].

## Corrections or discrepancies before publication

**No new material scientific correction was identified in this focused read.** The tail constants, boundary arguments, one-sided future allowances, finite D proof and retrieved D sign/count claims agree across the inspected source and receipts. This assessment does not claim a fresh visual PDF inspection, exhaustive historical proof audit, current CI success or final package-byte completeness.

The final publication description must continue to distinguish: method-neutral gains from neural exclusivity; identical-policy implementation savings from economic improvement; known-catalogue development from unseen validation; D's independent implementation from the old shared-compiler fine references; and historical/earlier-source success from a new run. The inspected scientific text already makes these distinctions. The resumed loss of local-only regular files/ZIP is a separate packaging-custody matter being handled by root, not evidence that the science was rerun or that its outcomes changed.

### Immutable source identities for this assessment

The links below all resolve at author commit S. Git blob identities of the principal checked objects are:

| Source object | Git blob SHA |
|---|---|
| ECTA.tex | b8684051e2f5d1f8835351748bebdd342ef18d85 |
| supp.tex | afb586e2d205a83613bbdc77626cf4fc3a7e1894 |
| new119/active_tail_main.tex | 731908ef78fb5c8ea5baffc9b824ddd933029100 |
| new119/active_tail_proofs.tex | 3545c5021c1f2eae352ca4f1b1464db2ba6ead7a |
| new119/foundations_supplement.tex | e989ab43fbb81f6ed8656cfe04bf5d4ed9779e6c |
| new119/independent_validation119_proof.tex | 46ce6bcda2c9a397855aa5d3d206f29b9fe5c8f8 |
| new119/response119_body.tex | db65330e30083d98aee66c7ba3a51cf9f7209fa8 |
| provenance/validationd119/R119D_NUMERICAL_REVIEW.json | eb1f796a532784698e2bb08abd5f9643085430a5 |
| provenance/validationd119/R119D_REPORTER_EXECUTION.json | 0d92f04d5a1a6f0ab6a61c10048c6b1003344899 |
| provenance/validationd119/validation119d_attempt01.json | 947b1585b2490f371e571ba17c310ee5af1b7fb1 |


[intro]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/new119/introduction.tex
[core]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/new110/core-main.tex
[economy]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/new110/continuous-main.tex
[study]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/new119/R119_STUDY_MAIN.tex
[response]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/new119/response119_body.tex
[tail]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/new119/active_tail_main.tex
[tailproof]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/new119/active_tail_proofs.tex
[budget]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/new119/budgeted_tail_main119.tex
[budgetproof]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/new119/budgeted_tail_proofs119.tex
[packingproof]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/new119/packing_proofs119.tex
[coupled]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/new119/coupled_main.tex
[coupledproof]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/new119/coupled_proofs.tex
[foundations]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/new119/foundations_supplement.tex
[bridge]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/new110/recursive_bridge.tex
[correction]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/new119/original_correctness119.tex
[studyc]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/new119/study_c119.tex
[studyd]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/new119/study_d119.tex
[dproof]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/new119/independent_validation119_proof.tex
[dreview]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/provenance/validationd119/R119D_NUMERICAL_REVIEW.json
[dlaunch]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/provenance/validationd119/validation119d_attempt01.json
[developmentd]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/new119/development_d119.tex
[conclusion]: https://github.com/TrillionniumFoundation/NBO/blob/6250abfd317f3b2a56cb1303eb5ce78249bf4042/revisions/2026-10-18-r119/new119/conclusion119.tex
