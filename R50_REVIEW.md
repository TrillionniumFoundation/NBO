# NBO — R50 review entry point

**Article:** *Certified Bellman Operators for Costly Policy Revision*, Qian QI.

This revision retains the common randomized Markov-policy target and responds to the latest R48 review by adding price-portfolio completion, shared-regret-budget refinement, paired density-kernel approximation, and an executed uniform-reset continuum contract. Prior revision and review branches are unchanged.

## Read in this order

| Object | PDF | Ordinary source |
|---|---|---|
| Current article | [ECTA_R50.pdf](ECTA_R50.pdf) | [ECTA_R50.tex](ECTA_R50.tex) |
| All numerical rows and preserved R48 article | [SUPP_R50.pdf](SUPP_R50.pdf) | [SUPP_R50.tex](SUPP_R50.tex) |
| Response to 20 major findings and 40 technical comments | [RESPONSE_R50.pdf](RESPONSE_R50.pdf) | [RESPONSE_R50.md](RESPONSE_R50.md), [TeX](RESPONSE_R50.tex) |
| Standalone historical reconstruction | [R48_RECONSTRUCTED_R50.pdf](R48_RECONSTRUCTED_R50.pdf) | [TeX](R48_RECONSTRUCTED_R50.tex) |

## Provenance and evidence

The reviewed report is `reviews/2026-09-26-econometrica-r48/referee_report.md` at `73a4f708581834692b817649ba5538b640b9e58d`; its manuscript is `77b90a92250694271265e91f9624b7d6aacb0dea`. The inherited R49 branch at `bce0f688dfd0041bc69b858346ef264994d65740` is preserved. Its partial transfer materials are not counted as completed scientific results.

R50 is on `revision/econometrica-r50-complete-diffuse-2026-09-26`. The immutable primary source-hash/seed commitment is `62585130b01f1b3479b5fc9f8ee0ee927509633a`, made before generating any primary R50 seed. It is a within-project freeze, not external preregistration.

The complete numerical records, rather than this index, determine the publication counts and machine-specific timings:

- [Protocol](revisions/2026-09-26-r50/PROTOCOL.json), [evaluation environment](revisions/2026-09-26-r50/EVALUATION_COMPLETE.json), [numerical summary](revisions/2026-09-26-r50/SUMMARY.json).
- [Models](revisions/2026-09-26-r50/models), [all results](revisions/2026-09-26-r50/results), [all exact proof objects](revisions/2026-09-26-r50/proofs), [work curves](revisions/2026-09-26-r50/results/work_curves.csv).
- [Full replay outcome](revisions/2026-09-26-r50/VERIFICATION.json), [cross-language checks](revisions/2026-09-26-r50/results/cross-language.json), [60-item response map](revisions/2026-09-26-r50/RESPONSE_MAP.json).
- [Content manifest and PDF hashes](revisions/2026-09-26-r50/MANIFEST.json), [historical preservation map](revisions/2026-09-26-r50/PRESERVATION.json), [build and test logs](revisions/2026-09-26-r50/logs).

The new primary study consists of 39 distinct diffuse models, two HiGHS proposal backends, and all intermediate grid proofs. The 48 finite constructions are retrospective complete-constructor comparisons, not fresh models or a pure branch-rule ablation. Eight occupation audits concern the uncapped **price relaxation**, not the common-policy optimum. Their capped-portfolio loss bounds cover all positive-support masks.

The paper explicitly separates structured reset-kernel success from general controlled finite scalability, action-dependent diffuse-kernel performance, expensive learned operating witnesses, calibrated applications, and externally authored verified-global-solver comparisons. The original thirty unfinished moving-atom uniform-law intervals are not claimed closed. Exact arithmetic, an analytic theorem, source identity, numerical efficiency, and external scientific replication are different evidence claims.

## Rebuild from committed records

Use Python 3.13, Node.js 22, the pinned Python dependencies, and a TeX Live installation containing the packages used by `econsocart`. On Ubuntu the required TeX packages are provided by `texlive-latex-extra`, `texlive-fonts-recommended`, and `texlive-science`; `poppler-utils` provides `pdfinfo`.

```bash
python -m pip install -r requirements-r50.txt
bash R50_BUILD.sh
```

This replays every R50 exact proof, checks all frozen source hashes, runs the analytic/adversarial contract tests and thirteen JavaScript checks, regenerates every table from the retained records, reconstructs the historical article, and builds all four PDFs. It does **not** rerun the numerical search. Source or theorem correctness is not inferred merely from passing arithmetic replay.

## Rerun the entire numerical study

```bash
bash R50_REPRODUCE.sh
```

This runs every registered diffuse model/backend, every finite model/method/cap, and all eight retrospective price audits before the same publication build. Soft-time-budget finite endpoints and machine timings may change across environments; regenerated tables and macros follow the new actual records. The raw protocol and six frozen constructor/reader hashes must not change. All failures are retained.

All substantive scientific files are ordinary `.tex`, `.py`, `.mjs`, `.json`, and `.json.gz` files. The `transport` directory is a checked transfer record, not a substitute for those files. No consumer needs to decode it after publication. The original review paths and earlier papers were not rewritten; the historical copy changes only input paths and restores two missing tables from unchanged original fractions.
