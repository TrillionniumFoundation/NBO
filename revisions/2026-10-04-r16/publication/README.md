# Neural Bellman Operators — R16 referee reading edition

This edition revises the original NBO paper in response to the complete R15 advisory referee report. It does not replace the research topic or delete the inherited mathematical applications.

## Reading order

1. `build/ECTA.pdf`: current article (pagination is recorded in `results/COMPILATION.json`).
2. `build/supp.pdf`: complete current supplement (complete current pagination in the same compilation receipt).
3. `build/response.pdf`: point-by-point R15 response (compiled with the same source revision).

The repository roots `ECTA.tex` and `supp.tex` build the current reading edition. Its editable new text is in `editorial/`; `manuscript/` contains the complete assembled reading sources. `archive/` preserves the exact preceding roots. All historical `revisions/` and `reviews/` files remain at their original paths.

## Substantive changes

The edition integrates all four completed source-frozen families: signed occupation Bellman assessment, prospective paired replication, strengthened-HJB economic robustness, and the five-method continuation menu. It adds a proved economic decision-value identity for fixed scalar-gradient compression, with explicit approximation bias and interior-feasibility conditions, and independent finite-support tests. The common-continuation, antithetic range, and whole-segment scalar optimality arguments are made accessible in the article and supplement. General theory, the original recursive-utility/preference/temporal-self/game applications, and adverse numerical findings remain in the current supplement.

## Evidence status

Completed numerical evidence is pinned to signed commit `d74c20877b27b5c4a94d41bac3ec16e9fa5da497` and paired replication commit `2f17d8163a1d1d6b72a32b6ea6d6b683dc62031e`. The strengthened-HJB and continuation-menu scientific design is pinned to `503a724817899105a78f8c2fd516f417efb6b483`, which includes the strengthened-HJB source `21d4cc505202686382b5b45d5f710ffdc12f889c`.

The article uses the complete registered outcomes, not partial workflow output. In the continuation menu, six of eight final-stage comparisons certify practical equivalence with cached SAA at lower construction/query work; both long cases favor cached SAA materially. All 216 menu primary events, 128 scalar events and 648 robustness events are retained. `COMMENT_STATUS.json` records completed changes and remaining empirical scope for every M1–M10/B1–B8 concern. In particular, the signed positive policy account does not establish NBO superiority over Raw, and fresh fixed-policy confirmation is not new training or a new economic calibration.

## Validation

`FINAL_AUDIT.json` checks unchanged historical Git blobs, exact archive destinations for the three reading-root replacements, every original compiled label, immutable scientific result subtrees, independent manufactured tests, and all three document builds. `PUBLICATION_MANIFEST.json` binds the publication files to the immutable assembly source. Publication-integrity success is deliberately distinct from closure of every empirical referee question.

Local checks preserve their receipts, including a Python-version gate failure in the robustness infrastructure suite under the local non-3.12 interpreter. The final workflow reruns that suite in its declared Python 3.12/Linux environment rather than weakening the gate. Test-only HJB fits are manufactured API fixtures and evaluate no registered economic bank.

## Reproduction

On a checkout of the final reading branch, with Python 3.12 and the pinned numerical dependencies installed:

```sh
python revisions/2026-10-04-r16/publication/code/completed_evidence_audit.py
python revisions/2026-10-04-r16/publication/code/assemble_publication.py
python revisions/2026-10-04-r16/publication/code/build.py
```

The source assembly is idempotent and copies only from immutable preceding article sources; it does not rerun fitting or confirmation. The workflow documents exact numerical-package and TeX dependencies, merge parents, checks, and creation-only publication branches. No main, review, source, or existing evidence branch is overwritten.

## Completed comparison sources

Continuation-menu evidence: `103b6717dac939cb9cd18876f56d889c9e2a751d`; strengthened-HJB evidence: `0b0b113b8c249d916daf0da22808180ce15caa2f`. Their result subtrees are included without alteration. `results/COMPLETED_EVIDENCE_READING_AUDIT.json` checks every menu primary endpoint and independently recounts the reported decisions and scalar attainments from the immutable report. It is not represented as rerunning the raw 12.2 GB numerical study.

The final reading edition also includes the stable-active-face decision-value proposition and its full proof. Its ten exact constrained-optimizer tests and completion receipt are in `completion/`. All original numerical evidence and all 78 inherited unit-test requirements are retained.
