# R125 theory, frozen code, and execution correspondence

## Identities and chronological scope

This note records the mathematical and implementation audit at
**2026-10-23T07:26:19.480751+00:00**. It is a post-freeze manuscript and
provenance addition, not part of the prospective scientific executable.
The final manuscript statements, proofs, attribution, and the sharper terminal
regret bound were developed separately from the frozen production service.
Their presence in the final author package does not imply that these final
formulations were present at the experiment's source boundary or implemented
in its measured decisions.

The scientific manifest was frozen at `2026-10-23T07:16:14.523627+00:00`.
The remotely published source commit is
`a94e1f43bf64d8cb90af21e4b53d07335c615576`; its source tree is
`16bd6c5fc3e5aed9fb9fd7ff74d5c3411a29ebda`. The manifest SHA256 is
`62b092b04a79c174497012d2e53f953caadb8af260fcb6085236890db7872913`.
All 338 published entries, comprising 336 manifest-listed files plus the
manifest and file list, were read back at
`2026-10-23T07:18:25.628290+00:00` before the first original-economic call.
The primary census began at `2026-10-23T07:19:07.367910+00:00`.
The 336 scientific file hashes were checked again at this note's timestamp:
**no mismatch**. The complete source, rather than a version name, defines the
experiment. See `SOURCE_FREEZE125.json`, `BOUNDARIES125.json`, and
`provenance/F125_REMOTE_READBACK125.json`.

The manuscript-theory SHA256 values at this checkpoint are:

| File | SHA256 |
| --- | --- |
| `new125/acquisition_main125.tex` | `8123a0f1e6984183414670031a78a677250a59388d32bdba23bd1da18d38df83` |
| `new125/acquisition_proofs125.tex` | `336a53de5cd220eed850d23e34332297ac77f02cc6796dce9609577e66bfa07c` |
| `references125.bib` | `e89d627557fb92c5a6ae783013adcef7ede8a79cab020a5ce732286f086d33c6` |

These checkpoint hashes supplement, and do not replace, the final source/PDF
manifest. No theory amendment changes frozen scientific bytes, retrospective
selection, experimental targets, or the classification of a recorded outcome.
Protected R123 and R124B independent experiments remain separate; their
unpublished outcomes are not evidence for R125.

## Theorem-to-code map

| Mathematical item and scope | Frozen implementation and execution evidence | Scientific status |
| --- | --- | --- |
| Exact finite interpolation for scalar strongly convex, smooth objectives above every paid quadratic support (`thm:fullinterpolation125`). Includes boundary nodes, all observed jets, shared support slopes, and bounded-domain conjugates. | `support125.py` evaluates the exact rational conjugate, adjacency inequalities, and raw-support inequalities for supplied candidate jets. `fixtures125.py` supplies explicit rational witnesses. It does not solve the finite convex optimization problem. | General equivalence and constructive sufficiency are analytic results with complete proofs. Exact finite fixtures executed. No original-economy conic-solver performance is claimed. |
| Boxed rational Lagrangian residual certificate (`eq:fullresidual125`). | `support125.py::residual_lower_bound` evaluates the correction for supplied convex-constraint values, valid subgradients, multipliers, and finite boxes. The frozen fixture checks a nonstationary linear example. | The generic mathematical guarantee is proved. The helper does not certify that arbitrary user-supplied gradients are valid, generate a dual solution, or establish solver optimality. There is no production dual solve to credit. |
| Strict support-retention action witness: contrast upper bound changes from `-1/4` to `-5/8`, with explicit extremizers and additional guaranteed gain `3/8`. | Both rational jet tuples and the excluded reduced-class tuple are checked in `fixtures125.py`; `results125/fixtures/FIXTURES125.json` preserves all slack values. | Executed mathematical fixture under its stated scalar information interface. Direct evaluation of the retained support also attains the stronger endpoint bound. This is neither an economic census observation nor an advantage over that direct comparator. |
| Interior-obstacle counterexample despite passing stored-node lower bounds. | The deliberately inconsistent rational payload is rejected by the conjugate constraints; exact interior violation is `1/64`. | Executed negative mathematical fixture, not admissible economic data. It illustrates why endpoint-only obstacle tests do not complete the theorem. |
| R123 midpoint contraction with action rounding and interval derivatives (`prop:midpoint123`). | `service125.py::update_bracket` retains constrained boundary optima. The service uses rounded 30-bit midpoints, derivative intervals recovered from paid original supports, and checks the achieved contraction. `verify125.py` replays saved arithmetic. | Inherited theorem; newly executed acquisition service. The localization lemma is not presented as a new R125 discovery. |
| Incumbent-regret warm bracket (`eq:warmbracket125`). | Frozen warm services initialize from the retained R123 derivative-envelope roots; cold services initialize from `[0,A]`. They do not initialize from the displayed regret-radius rule. | Additional analytic initialization rule. No unexecuted warm-start benefit is attributed to it. |
| Coupled finite-radius value/gradient precision conditions and conditional complete-work bound (`thm:paidwork125`, `eq:jointprecision125`, `eq:geometricwork125`). | Frozen adaptive services buy the fixed ladder `32,64,128,256,512,1024,2048` until actual contraction, stronger qualification, or the declared cap/floor. The fixed comparator buys 512 bins. Every attempt is retained and charged. Neither implements the optimal planned-width schedule. | The work theorem is conditional on an explicitly stated bound for obtaining the joint oracle tolerances, including unsuccessful refinement levels. No such power-cost bound is inferred from these four states, and no measured speedup is credited to the unimplemented schedule. |
| Separate actual-action error, original-policy regret, and absolute value-width requirements. | The production service reports an action-distance upper bound derived from its certified regret using original curvature `mu=2`. It accepts a changed action only after a strict original-policy contrast plus the unchanged future-controller allowance, ordinary regret `1/256`, and width `1/8192`. The stronger target is separately `1/65536`. | Implemented and replayed, with original continuation controller unchanged. A narrower interval alone is not a recorded policy improvement. |
| Sharp terminal bracket regret `J(b)-min q <= delta + M*r_b`, or `delta + L*r_b^2/2` when stationarity is certified (`eq:terminalpolicy125`). | Frozen services retain the inherited support-envelope optimum lower bound. They do not use this new direct terminal bracket gate; the displayed production regret can therefore exceed this analytic bound. A fresh value query is still separately needed if absolute width is not qualified. | Post-freeze analytic result only for the recorded service. A singleton bracket implies theoretical regret at most `delta`, but cannot retrospectively convert a recorded stronger-target failure into success. |
| Matching terminal minimax bound for the specifically stated stationary-bracket information interface. | No production implementation or oracle-query complexity experiment. | Analytic lower/upper result for its precise restricted interface. It is not a lower bound for methods with extra original-model formulas, value observations, support records, or different information, and is not a neural complexity separation. |

The rational interpolation helper checks the inequalities supplied to it. Its
generic call interface is not a stand-alone verifier of every theorem premise:
the caller must include both domain endpoints and the required observed nodes,
enforce original value/derivative boxes and derivative caps, and supply genuine
globally valid support records. The explicit frozen fixtures satisfy their
stated premises. The complete proof, rather than finite test enumeration,
establishes the general theorem.

The shared existential slope in a support interval is an exact convex lifting
of the fully enforced robust pointwise minimum-slope obstacle under convexity.
It is not a strictly stronger information source than that complete continuous
obstacle. The mathematical increment completes the raw supports deliberately
omitted from R124's reduced interpolation class. It does not claim generic
interpolation, inexact-oracle scheduling, or collected-oracle lower bounds as
new: the article cites Taylor--Hendrickx--Glineur, Devolder--Glineur--Nesterov,
Van Dessel--Glineur, and Florea--Nesterov with the corresponding scope.

## Actual executed work at this checkpoint

The following statements are supported by completed local receipts, not by
the existence of code:

| Receipt | Observed completed scope |
| --- | --- |
| `results125/primary/EXECUTION125.json` | 234 predeclared service cohorts and 936 primary decisions; exit code 0. |
| `results125/timing0/EXECUTION125.json`, `timing1`, `timing2` | Three serial passes, each with all 234 first-state decisions; 702 timed decisions in total; all exit codes 0. Shared, unregulated host timings are descriptive. |
| `results125/verification/EXECUTION125.json` | 16,162 saved-algebra and timing checks; exit code 0. This is not an independent economic calculation. |
| `results125/fixtures/EXECUTION125.json` | 266 exact rational fixture checks; exit code 0; explicitly no economic outcomes. |
| `provenance/OBSTACLE_INTERPOLATION_DIAGNOSTIC125.json` | Independently implemented exact diagnostic: 240 jet configurations, 4,080 affine-support cases, and 12 affine `K=0` pairs. It ran at 07:10:46 UTC, before the scientific freeze, and is a disclosed non-economic mathematical diagnostic. |

At this checkpoint the separate original-economic reconstruction has a start
record and retained partial outputs, but no completion receipt. Its final
status must be taken from `results125/independent/EXECUTION125.json` and its
published summary when those exist; this note grants it no advance completion
credit. The subsequent final report must preserve confirmed, unresolved, and
contradicted checks separately. Neither mathematical fixtures nor saved-algebra
replay may substitute for that reconstruction.

The 56 inherited actors cover two state mesh resolutions, `5 x 5` and `9 x 9`,
seven representations, two risks, and value/marginal fitting. The mesh
parameters 5 and 9 are not numbers of acquired labels: each risk pays 13
original-Q contexts per state, giving 325 and 1,053 contexts respectively.
The four-state R125 census is deterministic and supplies no population sample
or sampling confidence interval. Acquisition, complete deployed services,
failed/refused proposals, and research-only independent verification remain
separate charged quantities. Unknown historical interrupted clocks remain
unknown. All neural/hinge identities, conventional winners, and empty adoption
regions retain their recorded status.

## Subsequent post-freeze singleton diagnosis

At `2026-10-23T07:30:40.593136+00:00`, the separately written reporting-only
script `reporting125/diagnose_terminal_gate125.py` completed in
0.7462448680016678 seconds. Its exclusive receipts are in
`results125/postfreeze-terminal-diagnostic/`. It read and hashed the saved
936 primary records, checked the completed algebra-audit receipt, verified
all 336 frozen scientific hashes again, and made zero economic calls.
The diagnostic was selected after observing the primary results and is
explicitly not a preregistered experiment or a frozen-service amendment.

It selects every recorded failed stronger-target decision with a singleton
optimizer bracket equal to the deployed capacity action. There are two:
the warm-adaptive and warm-fixed512 services for risk `1/2`, mesh parameter
5, cubic-polynomial marginal fitting, state `(1/4,3/4)`. Both deploy
`A = 3/16` and record optimizer bracket `[3/16,3/16]`. Independent rational
reconstruction of the finite-radius derivative bound from the already paid
raw support, followed by smoothness transport to capacity, gives

\[
q'(A)\le -6125769643636980517/65212122604324782080<0.
\]

Convexity therefore identifies `A` as the original constrained minimizer;
the actual unchanged future gives regret at most `delta = 15/16777216`.
The stored regret and absolute width are both
`5255799856267265/295147905179352825856`, approximately
`1.780734256973116e-5`: above the stronger regret target, below the separate
width requirement. This exactly illustrates a loose level-based regret
certificate after the action has already been resolved.

The script does not replace that stored certificate. It preserves the
warm and fixed service counts of **231 successes among 232 decisions**, all
recorded intervals, the unchanged policy, and zero additional policy gain.
The sharper terminal gate is a concrete prospective production change.
The saved support's original-economic validity remains an inherited premise;
this diagnostic is exact consequence checking, not independent economic
reconstruction. Its input, script, and output hashes and measured cost are
recorded in `DIAGNOSTIC125.json` and `EXECUTION125.json`.

## Wrapper and attribution audit

The transitive source closure of the current `ECTA.tex`, `supp.tex`, and
`appendix.tex` was checked at the same audit checkpoint: 278 available input
sources, no missing referenced label definitions, no missing cited keys, and
no duplicate labels. Only the intentionally pending generated
`new125/numerical_results125.tex` and `new125/development_results125.tex` were
absent at that checkpoint; the final PDF build must validate their addition.
R123 memory statements/proofs and R124 joint statements/proofs/inference are
in the technical supplement. R124B bridge/inference and the published R124A
saturation diagnosis are preserved in the development companion, with their
cross-document references resolved through the supplement. The new citation
keys are supplied by `references122.bib`, `references124.bib`, and
`references125.bib`.

This audit found no mathematical or algorithmic scope mismatch in the new
introduction, experimental account, and discussion. Two descriptive corrections
were sent to the wrapper owner: call 5 and 9 mesh resolutions rather than
acquired label counts, and call the 296 verified baseline source/graphic
objects files rather than bytes. The wrapper owner retains editorial custody.
