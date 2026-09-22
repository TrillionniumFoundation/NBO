# R9 review entry point — Neural Bellman Operators

**Canonical revision branch:** `revision/econometrica-r9-constructive-certification-2026-09-22`  
**Latest review input:** `review/econometrica-r8-numerical-methods-2026-09-22` at `9749c3cf28f9438315b8f504a358bbe307ea89a5`.

Read `ECTA_R9.pdf` (current paper and mathematical appendix), `SUPP_R9.pdf` (complete R8, R4 and delivered R5 preservation), and `revisions/2026-09-22-r9/response_to_referee.md` together. `REVISION_INDEX.md` is the canonical file map.

## New substantive results

The original stopped NDU economy is unchanged. At the central state the value of access to adjustment is at least **0.04094994** at cost two; the restricted optimum is enclosed within **0.009047**. The flexible learned policy's payoff interval has width **1.33e-5**, but its regret upper is **0.10633861**, so the flexible **0.01 target remains unmet**. These quantities are deliberately not conflated.

Original-payoff bounds cover costs 0.5, 2, and 8. Constructive outward witness refinement, a bounded-source market-deflator upper, a non-enumerative action certificate through 128 dimensions, actual learned-network jet intervals, rigorous absolute lower references, and a frozen 72-pair holdout comparison are implemented. The independent quadratic-feedback baseline beats both learned methods in all six comparison panels; this and the inconclusive 16-dimensional sign comparisons are retained in the current paper.

## Provenance and reproduction

The external protocol was frozen in commit `46aef70a24f74cf57503018a7e7f21cb46af08e3`; complete holdout evidence was committed as `58007e6edf8a6d80e930e025138f38d978a82aba`. Author code is pinned to `sx-fang/MartNet@991ea8dde5bad6ba912eb8cc48b0cb48dbdd6c2a`.

Use `revisions/2026-09-22-r9/replication/README.md` for certificate and build commands. Raw scientific results, full external checkpoints/path arrays, preservation hashes, and validation results accompany the paper. No old source is silently replaced; only the stale root revision index is updated, with its preceding contents archived. No primary or review branch is advanced by this revision.
