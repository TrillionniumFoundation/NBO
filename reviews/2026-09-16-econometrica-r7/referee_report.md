# Referee report: *Neural Bellman Operators*, revision R7

**Author:** Qian QI  
**Review date:** 16 September 2026  
**Reviewed branch:** `revision/econometrica-r7-2026-09-16`  
**Reviewed commit:** `fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17`  
**Reviewed Git tree:** `cdc8e227881d5e95a8740c4f77298f73a0b9399d`  
**Previous report:** R6 advisory report at `10a7cbee28de5126d844dea9eae8c36c5cda9e9b`  
**Recommendation:** **Reject in its present form for Econometrica.**

This is an owner-commissioned, external-referee-style advisory assessment. It is not an appointment by Econometrica, a confidential journal report, or an editorial decision. The recommendation is a judgment about this manuscript, not about the possibility of developing the research further.

## 1. Assessment for the editor and author

R7 is a substantive revision. It should not be rejected by mechanically repeating the previous report. The author has accepted the localized-count comparison, supplied a mathematically meaningful compression interpretation, reported a genuinely autonomous refinement experiment, added a primitive sufficient condition, and constructed a decision-specific certificate over a joint contract–transition region. These changes close important deficiencies of R6. I did not find an algebraic counterexample to the new ordering, total coefficient-error bound, primitive option inequality, or tensor sign construction under their stated finite-model assumptions.

Nevertheless, I do not recommend publication. The strongest new economic conclusion is extremely accurately certified for a particular finite target, but its qualitative content is not stable under a nearby temporal discretization. In a reviewer extension retaining the same state grid and the complete common action menu, the non-adjusting agent's risk ranking changes sign at a corner of the advertised region when the number of dates increases from eight to sixteen. This does not invalidate the eight-date certificate. It does materially weaken its use as the substantive economic payoff of the framework.

A separate matched reviewer calculation removes all three neural proposals from the feasible policy bank while retaining the author's original full-target upper tensors. The entire joint-region reversal remains certified, with almost unchanged bounds. Thus the new decision does not require neural policies, and its executed upper bound uses localized count rather than the compressed chord. The manuscript still needs to establish why the collection of neural operators, transfer certificates, and economic examples constitutes one important contribution rather than several correct but only loosely connected components.

There is a positive computational result: in the reported autonomous experiment the compressed method is faster than count at the common tolerance, despite requiring more anchors. I credit that result. What remains missing is evidence that this tradeoff has sufficient generality and economic consequence to carry the paper at this journal. The primitive economic addition is also valid but does not yet explain the mechanism generating the stopped-economy result. These are substantive contribution and robustness objections, not demands for more build badges or a longer response letter.

## 2. Materials, provenance, and scope of verification

I examined the complete 45-page R7 main PDF and 29-page supplement, their source entry points and inherited inputs, the response to R6, the previous advisory report, and the relevant numerical source and deposited arrays. New proofs and experiments received the most detailed examination. Selected equation and table pages were also visually inspected. This is not a claim to have independently re-proved every inherited theorem or rerun every historical neural-training experiment.

The source was obtained through the repository's successful Actions run `35063710310`, artifact `10433863234`. The downloaded archive's SHA-256 is `b0bcb8542760adffae90e3ffff7ad61d0fe5b49e0b93e0f66a05eeea170d51c2`. Extracting the complete source and reconstructing its Git tree produced exactly the reviewed tree above. All 27 entries in the R7 authored-source inventory matched their recorded hashes. The artifact's final-commit record also matched the reviewed commit. This prevents confusing the workflow's earlier triggering commit with the completed manuscript and evidence commit.

The accompanying programs distinguish three evidence classes. First, I reran the author's small-model validation, primitive calculation, and coefficient-only decision replay. Second, I wrote a masked Bellman optimization that constructs neural-free lower policies against the unchanged full-target upper certificate. Third, I constructed nearby finite targets with different numbers of dates and reran both risk classes. The latter two are reviewer extensions, but they reuse the author's transition-kernel implementation. They are not an independent implementation of the economic transition law or an independently validated diffusion solver.

The author-suite replay covered 96 generated small models and 480 parameter checks. The count replay discrepancy was at most `1.7763568394002505e-15`; the coefficient ordering held up to floating-point noise; the largest tested ratio to the total-error bound was `0.5534812664972152`. The deposited decision bounds replayed without discrepancy. These facts support implementation consistency; randomized tests are not substituted for proofs.

Machine-readable results and runnable programs are deposited alongside this report. No author manuscript, source, historical report, or author output is changed by this review. Author-run timings below are quoted from deposited records, not compared with reviewer-machine timings.

## 3. Disposition of the previous round

| Previous concern | R7 disposition | Remaining issue |
|---|---|---|
| R6-F1: localization confounded the upper-oracle comparison | **Closed as a comparison defect.** R7 states and proves localized-count dominance, reproduces the matched bounds, and separates precision from work. | General importance of the compression tradeoff, not the old unmatched comparison. |
| R6-F2: no positive computational case | **Partly closed.** R7 supplies a real autonomous cost comparison and finite-refinement bound. | Breadth, total resource scaling, and consequences beyond one short finite economy. |
| R6-F3: economic identities do not predict an option ordering from primitives | **Formally addressed in a new specialization.** Proposition 16 is more than set inclusion or an envelope identity. | A demonstrated explanatory bridge to the main stopped economy. |
| R6-F4: generic welfare tolerance cannot certify the risk conclusion | **Closed for the stated eight-date finite target.** Proposition 17 and Table XVIII give class-specific joint-region signs. | The new temporal-sensitivity finding and the economic relevance of that particular finite target. |

The recommendation below does not revoke credit for these repairs. In particular, it would be incorrect to say that R7 has no regional economic certificate, no primitive prediction, no executed autonomous comparison, or that a `10^-3` tolerance is still being used to certify the new signs.

## 4. Major finding R7-F1: the economic ranking is sensitive to the time discretization

**Severity: publication-blocking economic robustness issue; not a refutation of the finite-model theorem.**

**Locations:** Main pp. 24–25 and 39–40, Proposition 17 and Table XVIII; `04f_economic_certification.tex`, lines 46–72; `05c_r7_evidence.tex`, lines 15–26; Supplement S.11.3–S.11.4, pp. 27–28; `replication/r7/decision.py`.

The manuscript certifies opposite first-risk rankings throughout `(lambda,d) in [0,0.25] x [0.4,0.45]`, at initial state `(u,X)=(2,1.25)` and adjustment cost `k=2`. This is a real certificate, not a grid of optimistic point comparisons. The reported adjusted-class advantage is bounded below by `6.888728805714623e-5`; the non-adjusting class difference is bounded above by `-5.2993655605010966e-5`. The per-class arithmetic allowance is `3.797650002493679e-9`.

The numerical precision of a certificate conditional on stored arrays does not control the economic effect of changing those arrays. I therefore held fixed the physical horizon of one, the 33-by-49 state grid, all financial and preference primitives, the boundary and settlement construction, the two endpoint shock-law generators, and the complete 1,565-action union mesh. Neural proposals were excluded from both arms at every horizon. This common-menu restriction matters: the factory's ordinary `include_neural=False` option would also remove an older mesh from the union and confound the comparison. The reviewer program explicitly preserves both original meshes.

Only the number of decision dates, and consequently the step size supplied to the same transition constructor, changes. At `(lambda,d)=(0.25,0.45)`, the first-risk class differences are:

| Dates | Adjustment available: positive minus nonpositive value | No deliberate adjustment: positive minus nonpositive value |
|---:|---:|---:|
| 4 | `+5.292244754435682e-4` | `-1.3986966545576074e-4` |
| 8 | `+3.2452963614693076e-4` | `-5.300125090501595e-5` |
| 16 | `+2.4784234209518363e-4` | `+5.312359482567697e-5` |

Thus the eight-date opposite-ranking conclusion does not survive at this corner in the sixteen-date common-menu economy: both adjustment regimes prefer the positive class. At `(0.25,0.4)`, the non-adjusting difference moves from `-1.6815344568577029e-4` at eight dates to `-2.3106771110947832e-6` at sixteen. The accompanying record contains all five inspected parameter points at four, eight, and sixteen dates, with both adjustment regimes. Selected-policy reevaluation errors were below `2e-11`.

Three qualifications are essential. These are exact backward optimizations of nearby finite menus up to ordinary arithmetic, not new uniform tensor certificates. The original full target has three additional frozen neural actions, whereas this temporal comparison excludes them consistently; the separate matched experiment in R7-F2 establishes that their removal does not eliminate the original regional result. Finally, holding the spatial grid fixed while refining time is not a valid stand-alone convergence demonstration for the diffusion. Interpolation and boundary effects may contribute to the change. I do not infer the sign of a continuous-time limiting problem from these runs.

Those qualifications protect the interpretation of the experiment; they do not make it uninformative. The author has established one finite target's sign with nanoscopic arithmetic allowances while a nearby temporal target changes the economic classification. The paper explicitly disclaims a diffusion error certificate, so this is not an accusation that a theorem promises one. It is a challenge to the scientific significance of the chosen target. The distinction between a highly accurate numerical answer and a robust economic conclusion is central here.

A satisfactory response must do more than move the rectangle to another favorable location. It should explain the sign movement and supply a decision-specific joint state/time/action and transition-approximation sensitivity account. Alternatively, the author could justify eight decision dates as an economically intended primitive, rather than as a numerical approximation, and demonstrate robustness to economically relevant changes in decision frequency and other primitives. Either route requires substantive evidence. A new statement that the theorem is conditional on the finite arrays would be true but would not answer this objection.

## 5. Major finding R7-F2: the new joint-region result does not require neural policies

**Severity: publication-blocking attribution and contribution issue.**

**Locations:** Abstract and Introduction; Main pp. 34 and 39–40, Tables XI and XVIII; `05c_r7_evidence.tex`; `replication/r7/core.py`, `decision.py`, and `output/decision_coefficients.npz`; the review's `reviewer_r7_checks.py`.

R7 commendably retains earlier neural-free and structural-optimization comparisons. The unresolved question is sharper than whether a generic welfare bound can be achieved without neural proposals: does the new decision-specific economic result need them?

I solved the corner problems again, masking out all three neural proposals at every state and date. The complete common union mesh remained available. I independently reevaluated each resulting policy through the author's selected-policy arithmetic path and constructed its fixed-policy transition coefficients. Crucially, I did **not** replace the original upper problem by an easier mesh-only upper problem. I retained the deposited class-specific upper tensors for the original 1,568-action target and paired them with the newly generated neural-free feasible lower polynomials.

Applying the same tensor extrema and arithmetic allowance gives:

| Regime | Reviewer neural-free lower bank against original full-target uppers: certified interval for the class difference |
|---|---|
| Adjustment available | `[6.88872246050138e-5, 3.245372998448897e-4]` |
| No deliberate adjustment | `[-3.6948485968774585e-4, -5.2993655605010966e-5]` |

Both strict signs therefore hold throughout the **same entire rectangle**, still against the original full target. The adjusted lower endpoint differs from the author's by approximately `6.35e-11`. This is not evidence that a merely sampled neural-free policy performs reasonably well. It is a matched, decision-specific certificate showing that neural proposals are unnecessary for the new headline regional result.

There is a second attribution distinction. The new economic certificate is executed with localized count uppers. It does not establish that the new compressed chord is necessary to obtain the economic finding, or that the economic conclusion is an implication uniquely enabled by that compression. Neither observation makes the general certificate invalid. Together they substantially narrow what this application demonstrates about the manuscript's nominally integrated contribution.

The conclusion already says that containing a neural network is not the substantive criterion. I agree. The problem is not a terminological demand to rename the paper. It is that the paper needs to establish a consequential role for at least one distinctive proposed ingredient. Conventional exact finite-action backward optimization, feasible-policy polynomial evaluation, and count-information upper bounds currently recover the new economic decision without the neural proposals and without using the compressed oracle for that decision.

A serious next step would identify a problem class in which the proposed representation or compression enables an otherwise difficult, economically meaningful comparison, and measure the relevant total cost at decision-level accuracy against strong non-neural alternatives. Merely inserting neural endpoints into an inequality that permits them would not demonstrate their usefulness. Nor would removing adverse baselines or dropping economic models improve the scientific argument. The present adverse results should remain visible.

## 6. Major finding R7-F3: a real local computational gain is not yet a general computational contribution

**Severity: major contribution and external-validity issue.**

**Locations:** Main pp. 19–21 and 38–39, Proposition 12, Theorem 13, Tables XVI–XVII; Supplement S.10; `replication/r7/matched.py`, `adaptive.py`, and their deposited JSON records.

I accept the comparison's basic mathematics. With common endpoints, feasible policies, and cells, localized count is coefficientwise no larger than the corrected chord. The correction trades precision for fewer upper-kernel applications: `4H-6` rather than `H(H+1)-2` for the specified implementations. The total coefficient-error bound includes the endpoint-policy bank's first-order loss and yields a finite scalar dyadic refinement rule. It does not improperly infer a second-order bank rate from a second-order correction. These are improvements over R6.

The autonomous experiment also delivers a positive result:

| Rule | Anchors | Final bound | Author-run total seconds |
|---|---:|---:|---:|
| Chord | 18 | `0.0008998289604379428` | `73.4053110100001` |
| Count | 11 | `0.0009244712735729799` | `115.37686621400007` |
| Cascade | 11 | `0.0009244712735729799` | `127.73181597900009` |

The chord is faster in this run at the shared `10^-3` acceptance target. Count needs fewer anchors. The cascade pays additional oracle work without improving this realized anchor count or bound. These are honest results; describing R7 as having no positive computational case would be wrong. The matched-bank results likewise provide meaningful precision–work points, with shared stages properly charged.

The remaining problem is the distance between these results and a general-purpose computational contribution. The autonomous comparison is one horizon, one state/action target, one contract coefficient, and one tolerance. Instrumented small models verify the kernel-call accounting at other horizons; they do not establish end-to-end scaling in the stopped economy. The policy bank still stores order `m S H^2` coefficients, and exhaustive finite-action backups remain. A reduced upper-propagation complexity is not automatically a reduced total complexity once policy evaluation, subdivision, storage, and anchor demand are jointly optimized.

The scale of the storage claim should also remain in perspective. In the deposited `d=0.5`, 18-anchor bank, common lower coefficients occupy 10,478,160 bytes and policy indices 931,392 bytes. The chord-versus-count persistent upper comparison is 90,552 versus 362,208 bytes. The upper saving is real, but it is roughly 2.3 percent of these combined bank/upper components, before including transition storage and temporary action arrays. The author already discloses excluded components; my objection is to economic importance and scaling, not an allegation of an undisclosed fourfold total-memory claim.

The most useful extension would trace a total-cost frontier across horizons, state/action sizes, tolerances, and parameter regions, including cases where count's reduced anchor demand dominates. At least one experiment should have an economic decision accuracy requirement, not only a generic welfare target. This would connect the computational argument to the actual economic certificate rather than leaving the two as adjacent demonstrations.

The literature comparison also needs to address closer attempts to preserve parameter dependence while tightening relaxations. R7 correctly adds Quatmann et al. (2016). Heck et al. (2025), *Generalized Parameter Lifting: Finer Abstractions for Parametric Markov Chains*, develops generalized lifting and a big-step transformation for tighter parametric-chain abstractions. That is not the same controlled finite-horizon reward problem, and I make no claim that its theorem subsumes the corrected chord or that its software would dominate these timings. It is nevertheless relevant to the proposed precision–dependence–work interpretation. The paper should explain what changes when moving from those chain constructions to controlled rewards, rather than treating a deliberately coarse rectangular reset recursion as exhausting the strongest nearby comparison.

Similarly, the reward-transfer component must continue to be separated from established optimistic linear support and successor-feature coverage methods, including Alegre, Bazzan, and da Silva (2022). Their fixed-transition reward setting is not an answer to changing transition laws. Precise distinctions strengthen a contribution; broad umbrella terminology does not establish one.

## 7. Major finding R7-F4: the primitive result and the main economy remain explanatorily disconnected

**Severity: major economic-content issue.**

**Locations:** Main pp. 23–25, Propositions 16–17; `04f_economic_certification.tex`, lines 1–44; Supplement S.11.1–S.11.2; `replication/r7/primitive.py`; inherited preference and risk-frontier sections.

The new primitive proposition is valid and nonvacuous. Concavity of CRRA utility in the preference index supplies a lower quadratic trial value and an upper quadratic bound. Under the feasible-trial condition, the adjustment option is between `g_sigma^2/[2(k+M_sigma)]` and `g_sigma^2/(2k)`. Comparing the positive-class lower bound with the nonpositive-class upper bound gives a genuinely primitive sufficient condition, not an identity involving optimized-policy moments. The declared probability–cost family is supported by analytical extrema, not just by its nine displayed optimizations.

But this is an explanatory specialization, not yet an explanation of the stopped-economy result. The specialization takes consumption lotteries and the duration difference as exogenous. Its example uses consumption 0.5 in one class, a lottery over 0.05 and 0.8 in the other, an imposed duration gap of 0.5, and adjustment costs between 20 and 80. The stopped-economy result instead uses cost 2 and endogenous consumption, duration, stopping, and portfolio exposure. The manuscript explicitly disclaims a calibration or approximation link. That disclaimer is accurate; it also leaves the economic bridge unbuilt.

The direction of the primitive adjustment illustrates the gap. In the declared lottery family, the positive-class preference shadow is negative and its optimal adjustment is negative in the executed examples. At the focal state, the reviewer common-menu policies producing the main eight-date positive-class advantage choose consumption 0.8 and adjustment `+0.2`, at the adjustment cap, with risky position `+0.8`, also at its upper limit. This does not contradict the primitive theorem: the problems differ. It does show why citing the theorem next to the table does not by itself identify the mechanism behind the table.

A persuasive economic contribution needs a result or decomposition that transports the primitive logic into the stopped setting: how exposure affects the preference shadow along relevant states, how deliberate adjustment changes survival and settlement, and when the resulting duration/effort changes favor one risk class. The endogenous duration difference is particularly important; assuming its sign in the explanatory family cannot establish its role in the main economy. Sensitivity to the adjustment and portfolio caps is also warranted given the binding focal controls.

Utility normalization is already acknowledged as economically substantive when preferences are adjustable. I do not demand invariance to transformations that change the model. I do ask for an economic rationale for the chosen cardinal specification and for robustness to plausible alternatives. Raw utility differences should also be translated into interpretable contract-equivalent or consumption-equivalent quantities under clearly stated conditions. Their small numerical magnitude alone is not an argument that they are economically unimportant; absence of a persuasive scale and mechanism is the problem.

The framework's many retained examples do not substitute for that missing link. Recursive utility, temporal selves, persistent competition, and the stopped preference economy each introduce distinct economics. Their coexistence is useful documentation of scope, but it does not establish that the central mechanism travels across them. The author should organize the argument around a clear general economic or computational insight and show which results actually support it, while preserving the historical and adverse evidence.

## 8. Additional comments and precise revision priorities

The numerical error account is considerably better than in earlier rounds. I found no specific contradiction between the stored coefficient replay and the reported arithmetic allowance. However, arithmetic, certificate slack, state/action approximation, shock-law construction, and economic specification remain different error categories. They should be displayed together when presenting an economic decision, rather than allowing the smallest category to dominate the reader's impression of precision.

The region was selected during exploration; Supplement S.11.3 discloses this. There is no statistical sampling claim here, so it would be inappropriate to label this ordinary multiple-testing bias. The issue is representativeness. A map of where signs can be certified, where they cannot, and how those sets move with primitives and numerical targets would be more informative than repeatedly showcasing one favorable rectangle.

The last paragraph of `04e_comparative_oracles.tex` says that the ensuing comparison does not represent the cascade as an executed autonomous timing contest. The later text and Table XVII do report such an execution. This is stale prose and should be corrected. It is minor and has no bearing on the recommendation.

The next revision should prioritize the sign-instability diagnosis, the matched neural-free regional result, the economic mechanism, and the total-cost frontier, in that order. It should not spend another round producing more administrative indices or declaring issues closed because additional tests pass. Tests can establish properties of implementations; they cannot establish economic importance or novelty.

## 9. Final recommendation

R7 has repaired important mathematics and numerical semantics. Its regional sign certificate is a genuine achievement for the declared finite target, and the compressed oracle has a demonstrated local cost advantage. I would not characterize this revision as empty formalism.

The bar for Econometrica is nevertheless not met by assembling valid ingredients and certifying an economically fragile finite-grid example to many decimal places. The new reviewer calculations leave two concrete problems: the headline opposite-ranking region is not stable in a nearby time-discretized economy, and it remains certified without neural proposals against the original full target. The economic specialization and computational comparison do not yet turn those facts into a compelling general contribution.

I therefore recommend **rejection in the present form**, rather than a claim that another cosmetic round would suffice. A materially stronger paper would explain and resolve the economic sensitivity, establish a consequential role for its distinctive computational construction, and connect its primitive mechanism to the economy in which the principal decision is certified.

## 10. Source guide and selected primary references

All manuscript and numerical locations below refer to the immutable reviewed commit stated at the top. Paths are relative to the repository root.

**R7 primary materials:** `ECTA_R7.tex`; `SUPP_R7.tex`; `revisions/2026-09-16-r7/ECTA_R7.pdf`; `revisions/2026-09-16-r7/SUPP_R7.pdf`; `revisions/2026-09-16-r7/response_to_referee.md`; `revisions/2026-09-16-r7/paper/04e_comparative_oracles.tex`; `04f_economic_certification.tex`; `05c_r7_evidence.tex`; `S10_comparison_proofs.tex`; `S11_economic_proofs.tex` in the same paper directory. Relevant generated tables are XVI–XVIII, pp. 38–40.

**Executed author evidence:** `replication/r7/output/matched.json`, `adaptive.json`, `decision.json`, `decision_coefficients.npz`, and `primitive.json`; implementations in `replication/r7/`; inherited finite-target construction in `replication/r5/contracts.py`, `replication/r4/solver.py`, and `replication/r6/transport.py`. The retained neural-free and structural-QP comparisons are identified in the main manuscript and R6 output records.

**Reviewer evidence:** [diagnostic_results.json](diagnostic_results.json), [reviewer_r7_checks.py](reviewer_r7_checks.py), [reviewer_time_refinement.py](reviewer_time_refinement.py), and [README.md](README.md). The reported temporal comparison is a finite-target sensitivity check, not a limiting-diffusion result; the matched ablation is a regional certificate against the unchanged original full target.

**Selected primary literature checked for this report:**

Quatmann, T., C. Dehnert, N. Jansen, S. Junges, and J.-P. Katoen (2016): “Parameter Synthesis for Markov Models: Faster Than Ever.” [Author paper, arXiv:1602.05113](https://arxiv.org/abs/1602.05113).

Alegre, L. N., A. L. C. Bazzan, and B. C. da Silva (2022): “Optimistic Linear Support and Successor Features as a Basis for Optimal Policy Transfer.” *Proceedings of the 39th International Conference on Machine Learning*, PMLR 162, 394–413. [Proceedings article](https://proceedings.mlr.press/v162/alegre22a.html).

Heck, L., T. Quatmann, J. Spel, J.-P. Katoen, and S. Junges (2025): “Generalized Parameter Lifting: Finer Abstractions for Parametric Markov Chains.” ATVA 2025. [Author paper, arXiv:2504.05965v2](https://arxiv.org/abs/2504.05965v2); DOI `10.1007/978-3-032-08707-2_10`. This report cites it as a relevant abstraction comparison, not as a proved equivalent or dominating algorithm for NBO's controlled reward problem.
