# Neural Bellman Operators

**R15 Econometrica revision — 4 October 2026**

This repository develops *Neural Bellman Operators* by Qian QI: continuation
evaluation, feasible policy improvement, and quantitative economic error
accounts for continuous-time control and equilibrium models. R15 responds to
the advisory referee report on R14 commit
`f5021cefa71492babfcbfa580e0c984f59a9de26`, retained at review commit
`7aff61a41a3d28e5eaff73c9fe21e9856110f422`.

The paper keeps its NBO subject, original capital model, endogenous preference
formation, recursive utility, temporal selves, and dynamic games. One current
article and a subject-based supplement integrate the theory, applications,
new numerical evidence, and preceding evidence.

## Read the revision

1. [Main article PDF](revisions/2026-10-04-r15/build/ECTA.pdf) and authoritative [TeX source](ECTA.tex).
2. [Complete supplement PDF](revisions/2026-10-04-r15/build/supp.pdf) and [TeX source](supp.tex).
3. [Point-by-point referee response PDF](revisions/2026-10-04-r15/build/response.pdf) and [response source](revisions/2026-10-04-r15/manuscript/response_body.tex).
4. [Latest referee report](revisions/2026-10-04-r15/review_source/referee_report.md), with all four original review files and source identities.
5. [Detailed R15 evidence and interpretation](revisions/2026-10-04-r15/README.md) and [complete reproduction instructions](revisions/2026-10-04-r15/REPRODUCTION.md).

The original publisher class, configuration, and bibliography style remain in
use. The manuscript has one authoritative NBO algorithm, numbered results,
author–year references, and cross-document references.

## What R15 adds

The finite Bellman bridge connects learned continuation to a feasible action
change under the candidate's actual occupation law. Its theorem carries
costate error, the actual actor's maximization gap, holding error, arithmetic,
and payoff transfer to a continuous-economy gain account. The independent
numerical assessment instantiates every term for all 32 returned NBO policies.

The main experiment executes four methods in dimensions 10 and 50 over the
complete support of a prospectively specified sixteen-stream randomized
implementation: **128 executions, no fallback, and 238 simultaneous final
events**. It compares NBO with reusable antithetic Raw-costate targets, direct
policy optimization, and a neural HJB method including its derivative and
action-search deployment work. The new capital parameters use
idiosyncratic/common volatilities 0.6/0.3. The original 0.15/0.10 evidence
remains separate and fully retained.

A proved deterministic refinement tightens direct policy-pair transfer on
the original statistical events. Both original and refined intervals remain
in the paper. Developed after the numerical source freeze, the refinement
has a disclosed chronology and changes no fitted policy, sample, economic
margin, confidence allocation, or stopping decision.

## Main economic findings

The intervals below are rounded outward; unrounded values determine decisions.

| Dimension | NBO mean gain over the analytical schedule | Simultaneous NBO gain interval | Refined NBO-minus-HJB interval |
|---:|---:|---|---|
| 10 | 0.001268 | [0.000943, 0.001592] | [0.000179, 0.000411] |
| 50 | 0.001342 | [0.000957, 0.001727] | [0.001347, 0.001650] |

Both direct NBO–HJB intervals exceed the predeclared economic margin of
`0.0001`, establishing a material payoff advantage over the specified HJB
implementation in the declared finite stream population. The NBO–Raw and
NBO–direct-policy comparisons remain unresolved in both dimensions and
establish neither practical equivalence nor noninferiority.

Every NBO, Raw-costate, and direct-policy stream attains a final certified
gain of `0.0005` in both dimensions. Online stopping is separate: all
dimension-10 procedures exhaust the registered checkpoints without an online
stop, whereas all sixteen dimension-50 streams of each of those three methods
actually stop. Neural HJB has no successful online stop in either dimension.

At the dimension-50 online target, mean complete work is **357.80 seconds for
NBO, 346.22 for Raw-costate, and 596.94 for direct policy**. Neural HJB consumes
1,690.10 seconds on average without an online stop. These are measured process
clocks through final confirmation and durable output; dependency installation
and artifact extraction precede them. Operation counts are separate, without
a claim of equal FLOPs or hardware-independent timing ratios.

## Mechanism, absolute accuracy, and additional evidence

The candidate-occupation account is fully executed and independently replayed.
Strong concavity is verified in both dimensions. Its conservative
continuous-gain lower bounds, approximately -0.006778 and -0.004800, do not
independently certify positive mechanism welfare. The critic-minus-Raw risk
intervals contain zero in both dimensions. Lower descriptive critic risk in
dimension 10 and higher risk in dimension 50 both remain visible.

The full adapted-control economic gap follows from the existing anchor upper
bound and the same method lower event, without new probability. The NBO gap
bounds are **0.025970104** and **0.036842066**, rounded upward. They give
explicit absolute guarantees but do not establish near-optimality at the
`0.0001` margin.

The scalar Howard study retains eight complete solves and eleven deployed
policies, including fitting and deployment work. Four matched full-box/tube
grids have identical value and action arrays. Monotone comparison and outward
algebraic enclosures bound finite-grid restriction loss by **1.788e-11**.
Grid refinement and domain extension are separately reported. The classical
policy's higher observed population payoff and the frozen neural policies'
state-specific ranking reversal remain in the tables.

The finite-observation study assesses four protected parents and all twelve
measurement specifications using the original weights and volatility regime.
All four parent lower gains are positive; **six of twelve** measurement
specifications retain a positive lower gain after their sensing allowance.

## Immutable sources and preservation

| Numerical family | Generating source | Complete evidence |
|---|---|---|
| Protected observations | `9f968785ac3cccab2bc37b1ec4096a1f5b8301b2` | `a268929ffa982fa8a6cc644813190fa7f4b4146e` |
| Main methods and scalar Howard | `9142f404bb9c5163aa94d3a4ded4d0fa48a49c50` | `b08347444e3001725d7fea33ff0bfce9c7e95e37` |
| Candidate-occupation mechanism | `b6b63511f5f76308d9073c373a889effe0e9a0c3` | `8d8ab9875b89680edc6766eb892c71ac2519af22` |

The mechanism evidence has both the mechanism source and main evidence as
parents and reuses the exact main-experiment subtree.
[PUBLICATION_SOURCES.json](revisions/2026-10-04-r15/PUBLICATION_SOURCES.json),
the [source ledger](revisions/2026-10-04-r15/SOURCE_LEDGER.json),
[payload manifest](revisions/2026-10-04-r15/EVIDENCE_MANIFEST.json), and
[final audit](revisions/2026-10-04-r15/FINAL_AUDIT.json) bind the generating
sources, raw records, editorial integration, and compiled documents.

All **8,652 historical blobs** in the reviewed R14 tree are preserved byte for
byte. The three replaced root reading files have exact archive copies.
All 230 old labels have a current or exact-archive destination; every original
labelled mathematical statement remains in the current article or supplement.
The original applications and adverse numerical findings remain accessible
and discussed.

## New revision branches

The complete delivery uses three newly created refs:

- `revision/econometrica-nbo-r15-2026-10-04`
- `revision/econometrica-nbo-r15-evidence-2026-10-04`
- `revision/econometrica-nbo-r15-referee-2026-10-04`

The publication-source branch is
`revision/econometrica-nbo-r15-source-2026-10-04`.
Its delivery workflow rebuilds the three documents, independently replays
numerical reports, verifies historical preservation and source identities,
and atomically creates the three complete revision refs. The advisory review
and response are repository research artifacts, without implying an
Econometrica editorial decision.
