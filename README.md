# Neural Bellman Operators

**R16 Econometrica revision — 4 October 2026**

This repository develops *Neural Bellman Operators* by Qian QI: learned continuation evaluation, feasible economic improvement, and explicit error accounts for control and equilibrium problems. R16 answers the complete advisory report at review commit `cb4595bbcc7147e47e44ba40cb2f5034510ae19f`, which reviewed publication `1cb3cc9efe135966ec228dfaf51c6841a6dfc97c`.

The revision retains the original title, nonlinear capital economy, recursive utility, endogenous preferences, temporal selves and dynamic games. Its main numerical contribution concerns the economic value of reusing a learned continuation across decision tasks. Four completed scientific families support that contribution, and all previous mathematical content and substantive applications remain current.

## Read the revision

1. [Main article PDF](revisions/2026-10-04-r16/build/ECTA.pdf) and [article source](ECTA.tex).
2. [Technical supplement PDF](revisions/2026-10-04-r16/build/supp.pdf) and [supplement source](supp.tex).
3. [Economic Applications PDF](revisions/2026-10-04-r16/build/applications.pdf) and [application source](revisions/2026-10-04-r16/applications.tex).
4. [Point-by-point referee response PDF](revisions/2026-10-04-r16/build/response.pdf) and [response source](revisions/2026-10-04-r16/response.tex).
5. [Latest advisory referee report](reviews/2026-10-04-econometrica-numerical-methods-r15/referee_report.md) and [eighteen-point response map](revisions/2026-10-04-r16/RESPONSE_MAP.json).
6. [Editorial and preservation record](revisions/2026-10-04-r16/EDITORIAL_PLAN.md) and [reproduction/publication contract](revisions/2026-10-04-r16/PUBLICATION_PIPELINE.md).

The main article uses the original publisher class, authorship and title. The technical and application documents have distinct numbering and cross-document references. The abstract contains 148 words under the publication audit.

## Incremental economic value of reusable continuation

A finite decision menu shares one continuation within each economic calibration while current preferences, externality weights and action caps change. The experiment retains all four calibrations, dimensions 10 and 50, sixteen fixed streams, 384 task-state queries, five methods, and three prescribed budgets: **128 trials, 640 fits and 1,920 stage candidates**, with no fit failure or reference fallback. All 216 payoff events and 128 scalar accuracy events are retained.

At the final prescribed stage, the two previously unpiloted fifty-dimensional cells establish material NBO payoff gains over both the materialized Raw actor and direct policy. The following lower endpoints are rounded downward:

| Finite economic design, dimension 50 | NBO minus Raw actor lower bound | NBO minus direct policy lower bound | NBO construction/query seconds | Direct-policy construction/query seconds |
|---|---:|---:|---:|---:|
| Long | 0.001802 | 0.000327 | 14.59 | 38.03 |
| Intermediate | 0.000147 | 0.000130 | 12.70 | 45.58 |

All four lower endpoints exceed the predetermined economic margin **0.0001**. The costs are actual mean complete three-stage construction and query clocks for the declared runs. The vector predictor and materialized Raw actor are cheaper than NBO in every final cell, so the economic increment over those alternatives has a computational cost.

In six of eight cells, the final NBO–cached-SAA interval lies entirely within **±0.0001**, with NBO using **19.73–84.02%** less construction and query work than the prescribed final 64-path SAA. SAA has materially higher payoffs in both Long cells. All cheaper four- and sixteen-path SAA budgets remain reported; the final-budget result does not establish a minimum-work frontier. The complete shared five-method, three-stage confirmation bill is displayed separately. Charging that entire bill to each procedure is an explicit conservative allocation, not a standalone verifier clock.

The theory proves the common continuation identity and states the bias–variance account of a fixed gradient dictionary under explicit conditional assumptions. The nonlinear fitted procedure is assessed by its economic outcomes; these comparisons do not separately measure critic-risk reduction or identify a unique variance mechanism.

## Independent confirmation, stronger HJB, and signed gains

**Original-policy confirmation.** A new bank assesses all 128 original policies using a paired proof, constants, code and family allocation fixed before the observations. NBO-minus-original-HJB lower endpoints are **0.0001760737** and **0.0013423158** in dimensions 10 and 50, exceeding 0.0001. All four NBO–Raw/direct-policy comparisons remain unresolved. These are fresh conditional payoff results for the original finite policy population; the old R15 refinement remains labelled post-freeze and its original zero-covering interval remains current.

**Economic robustness and strengthened HJB.** Four continuous-diffusion calibrations, two dimensions and eight newly trained streams per cell retain **64 trials, 256 construction processes, 320 policy outputs and 648 events**. The HJB comparator uses exact diffusion traces in both dimensions, all four frozen learning-rate/collocation configurations, independent residual selection, optimized greedy actions and a distilled actor. All forty pooled method gain lower endpoints exceed 0.0005. Only the low-volatility, fifty-dimensional NBO comparisons against both HJB deployments clear 0.0001; the other thirty direct comparisons are unresolved. All configurations, diagnostics, deployments and complete costs are current. Finite collocation residuals and iterate changes do not certify global value accuracy or rank the whole HJB class.

**Signed Bellman assessment.** The 32 original NBO policies receive 32,768 fresh continuation bridges. Direct common-future-path cancellation gives continuous-economy gain lower bounds **0.0007677118** and **0.0007765569**, exceeding the primary 0.0005 target. Neither attains the secondary 0.001 target. The signed continuation-correction intervals still contain zero. Original nonpositive Cauchy–Schwarz bounds and critic-versus-Raw risk uncertainty remain visible.

## Accuracy and substantive preservation

The new scalar menu account certifies a gap below 0.0001 for **80 of 128** fixed candidates over the whole continuous common-action segment. The remaining upper bounds do not certify that tolerance and do not prove that true regret exceeds it. These are scalar finite-economy certificates, distinct from the vector optimum and the adapted continuous-diffusion optimum. Full-adapted-class regret bounds remain beside schedule-relative gains.

The current reading set preserves all **285 original labels, 33 explicit mathematical/proof environments, eighteen complete heading proofs, and one NBO algorithm**. The original applications remain fully readable in the current application companion. All previous unresolved or contrary results, scalar classical comparisons, full-class gaps, stopping records and historical scientific files are retained.

The complete R15 tree contains **12,055 blobs**. Exact Git identities preserve every historical leaf; the three original publication roots have checked archival copies before replacement. The [source inventory](revisions/2026-10-04-r16/SOURCE_INVENTORY.json), [editorial map](revisions/2026-10-04-r16/EDITORIAL_MAP.json), and [proof preservation map](revisions/2026-10-04-r16/MATHEMATICAL_PRESERVATION.json) provide the current locations.

## Immutable scientific sources and evidence

| Family | Generating source S | Complete evidence E |
|---|---|---|
| Original-policy confirmation | `7e14a66813f6e5ecb04611ce72914771e02b1dc4` | `2f17d8163a1d1d6b72a32b6ea6d6b683dc62031e` |
| Economic robustness / HJB | `21d4cc505202686382b5b45d5f710ffdc12f889c` | `0b0b113b8c249d916daf0da22808180ce15caa2f` |
| Signed Bellman assessment | `5c4f94740207e950e809c4efd47ba8d9a181984d` | `d74c20877b27b5c4a94d41bac3ec16e9fa5da497` |
| Continuation menu | `503a724817899105a78f8c2fd516f417efb6b483` | `103b6717dac939cb9cd18876f56d889c9e2a751d` |

The family allocations are .01, .01, .01 and .02, totaling .05. All frozen code, protocols, scientific proofs, canonical reports, and raw evidence retain their exact bytes. The complete menu raw payload is preserved in Git; its bounded analysis subset suffices for independent report replay. Publication checks use a partial sparse checkout and exact complete-tree identities, avoiding a mandatory full raw-data checkout.

## Reproduce and verify

After obtaining the inputs documented in [PUBLICATION_PIPELINE.md](revisions/2026-10-04-r16/PUBLICATION_PIPELINE.md), the four publication documents rebuild with:

```sh
python revisions/2026-10-04-r16/code/integrate.py --write-roots
python revisions/2026-10-04-r16/code/build.py --publication
```

The publication workflow first verifies all four scientific report families and their source/evidence identities. It also regenerates the author presentation tables from complete reports, checks every current label and proof, compiles and renders all four documents, and binds the complete-page author review to the final source closure. A single verified publication commit is created on three new review branches atomically. Existing branch history is not replaced.

[The publication source configuration](revisions/2026-10-04-r16/PUBLICATION_SOURCES.json) gives all branch roles and exact identities. Final source-closure tables and ledgers are generated after the gates; the [publication contract](revisions/2026-10-04-r16/PUBLICATION_PIPELINE.md) explains their noncircular provenance.
