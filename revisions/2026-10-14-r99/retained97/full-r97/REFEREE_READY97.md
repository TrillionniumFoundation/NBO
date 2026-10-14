# Neural Bellman Operators — R97 referee package

The paper remains **Neural Bellman Operators**, by Qian QI. This revision extends the original NBO paper; it does not replace the topic, remove its construction, or reinterpret unfavorable comparisons as neural wins. The article and mathematical supplements use the repository's Econometrica class and conventions.

## Read these four documents

| Document | Current PDF | Pages | Editable entry point |
| --- | --- | ---: | --- |
| Article | [ECTA.pdf](build/ECTA.pdf) | 47 | ECTA.tex |
| Technical supplement | [supp.pdf](build/supp.pdf) | 37 | supp.tex |
| Complete development appendix | [appendix.pdf](build/appendix.pdf) | 230 | appendix.tex |
| Point-by-point response | [response.pdf](build/response.pdf) | 5 | response.md |

Start with the response and article. The response maps all ten major objections, ten revision requests and twelve minor comments to changes or explicit remaining obligations. New scientific source is in `new/`; source-bound tables are in `tables/`. `REPRODUCE97.md` gives the full reproduction commands, including the logs required by the release gate. The downloadable workflow artifact contains the current build and new evidence, not all historical repository dependencies.

## Provenance and review target

The reviewed scientific parent is `9a80ab7d4de97c9a61747899766fab43ec3c2598`. The addressed report is `reviews/2026-10-14-econometrica-numerical-methods-r96/referee_report.md` on `review/econometrica-numerical-methods-r96-2026-10-14-9a80ab7`, pinned at `e91a0702a4f1df4baa7b43fdfdd1305d0d62940c`.

The prospective protocol was committed at `673d29e48922ae59908cdde245f312e077442539`. The primary experiment ran from `19a708620bad5063076904aeced5d8c49e50cc16`, retained on `revision/econometrica-nbo-r97-source-frozen-2026-10-14`. Its `new/study97.py` SHA-256 is `db947fbbe20a92f38d8b5b95e4f5d733f8a3162df30d2f670e13a472b493baba`.

GitHub Actions run `38514480061` completed successfully. The ordinary source, actual primary results and four PDFs were published at `b636b01c4a615c1051dd9a4868922eb638123b22`. Subsequent finalization adds inspection, development disclosure and reading/reproduction guides; it does not alter the scientific source, primary results, or these PDFs. The referee snapshot is `revision/econometrica-nbo-r97-referee-ready-2026-10-14`; the working revision is `revision/econometrica-nbo-r97-referee-revision-2026-10-14`.

## Substantive changes

**Information complexity and neural contribution.** Article Section 9 adds Theorem 17: a deterministic adaptive value-information lower bound for convex Lipschitz AVaR integration, matching the retained upper bound's second-order information exponent at fixed risk level. Proposition 18 gives an exact oblique-continuation representation comparison; it is not a policy-regret lower bound or a universal neural-versus-conventional separation. Proposition 19 makes certificate-oriented readout acquisition executable and guarantees nonincreasing validated residual span. Complete proofs are in Supplement Section 10.

**Matched construction and complete service.** Section 11 reports all 84 fixed configurations: two risk levels, three ranks, two label budgets and seven services. Each fitted LS–CA pair uses the same selected geometry and available labels; the three fitted families have equal deployed payload at a given rank. All feature-search work, candidate construction, whole-domain validation and durable serialization remain charged. All 5,376 diagnostic services pass the unchanged admission criteria. There are 1,401 first-proposal rejections, zero quadrature-refinement rows and zero rational fallbacks. All 36 matched pairs improve validated span, but rejection counts are not uniformly improved. Tables IV and BG.I retain every reversal.

**Acquisition, reuse and economic interpretation.** Theorem 20 uses `B d` for a B-decision workload, correcting the former per-decision/whole-process mismatch. The measured workload has B=32, with 42 sequential fresh timing processes. The predeclared 1,800-cell price grid contains 156 conditional adoption regions, 199 conditional rejection regions and 1,445 unresolved regions. These are sensitivities conditional on applicable clock ranges, not calibrated welfare findings. New actors use the deterministic cost-difference bound [-1/256,1/256], not the old actors' statistical intervals. The engineering margin 1/1280 is one percent of the maximal first-date charge 5/64, not an externally calibrated welfare margin.

**Independent verification and history.** `audit97/INDEPENDENT97.json` records reimplementation of all 32,768 R96 proposals, including the conventional online proposals. The maximum action difference is 2^-30, within the declared 2^-29 tolerance. All twelve exact rational statistical contrasts and 24 difficult rational endpoint checks pass. The fitting optimizer is not independently reimplemented. ReLU and spline reconstruction identities and quadratic reconstruction differences remain visible; small function differences are not asserted to imply identical policies. Pinned R96 ARM64 evidence is incorporated with its original model/state identities and adds zero independent observations or new R97 fits.

## Preservation, testing and inspection

All inherited scientific section files are preserved. Two whole article sections and seven whole supplement proof sections are moved intact to the complete development appendix, with preservation checks and document mappings; they are not deleted. The R96 quadratic winner and all twelve R96 simultaneous comparisons remain. No original scientific or review branch is rewritten.

The successful run passed **445 inherited tests and 8 new tests**. `RELEASE97.json` records all execution gates as true; all four builds have no unresolved references or overfull horizontal boxes. `audit97/VISUAL97.json` records post-build overview inspection of all 319 pages and detailed inspection of selected new mathematics, tables and response pages, with an additional Poppler rendering check. Its exact PDF hashes match the execution receipt. The earlier `visual_inspection_recorded=false` field is preserved because the execution receipt predates visual inspection; `FINALIZATION97.json` binds the later record without rewriting that history.

`audit97/DEVELOPMENT97.json` discloses the preprotocol pilot, original reconstruction diagnostics and local missing-fixture failures. The pilot's deterministic rows recur in one primary cell and are counted only once. Local development clocks are not pooled with the remote primary clocks. The first CI publication attempt failed when creating an archival branch; its actual logs remain in `audit97/ci-attempts/38513327637/`. No remote campaign ran in that failed attempt. The subsequent run passed after separating archival-ref creation from CI execution.

## Claims that this release does not make

The new empirical campaign is not a completed longer-horizon, multicontrol, multi-innovation continuous-risk tournament, an external economic calibration, an exhaustive conventional approximation frontier, or an independent implementation of fitting. Those are explicit remaining obligations in the response, not outcomes supplied by passing tests or renaming the original application. Referee-ready denotes a compiled, source-bound package for another review, not editorial acceptance or scientific closure of every objection.
