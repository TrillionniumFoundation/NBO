# Neural Bellman Operators — R11 referee entry point

**Revision branch:** `revision/econometrica-r11-accuracy-and-robustness-2026-09-22`  
**Base:** completed R10, `d633bd60818998e53051cee6e7ad351c52a61795`.  
**Latest report:** review commit `251ad29668788b2a911c4ca6f9c0a226886518d6`, report blob `42cee0954515e5578dc579a4ca0428bb4e399b2e`.

## Read this revision

- Main paper: [ECTA_R11.pdf](ECTA_R11.pdf), source [ECTA_R11.tex](ECTA_R11.tex).
- Full preservation supplement: [SUPP_R11.pdf](SUPP_R11.pdf), source [SUPP_R11.tex](SUPP_R11.tex).
- Point-by-point response: [response_to_referee.md](revisions/2026-09-22-r11/response_to_referee.md).
- Exact report input: [referee_report.md](revisions/2026-09-22-r11/review_input/referee_report.md).
- Immutable source, result, build and PDF identities: [publication_receipt.json](revisions/2026-09-22-r11/publication_receipt.json).
- Preservation and numerical validation: [validation_report.json](revisions/2026-09-22-r11/validation_report.json), [validation_tests.json](revisions/2026-09-22-r11/validation_tests.json), [independent execution](revisions/2026-09-22-r11/ci_results/status.json).

## What is new here

R11 keeps the original stopped-economy guarantees below 0.01, independently rechecks all three costs, and retains all R10 welfare results. It adds 168 prospectively specified method-specific tuning trials and 36 entirely new holdout pairs on the unchanged external benchmark. The new corrected sign tests support the d=8 ordering, but not d=16 or d=32; all outcomes and the stronger clipped-feedback comparator remain visible. The frozen source is `17b0e1e786a79c26dc853eaaba83371b8f181928`, and the complete result commit is `a03d24ee21b52356305f7662f884264e22584b4b`.

The new reference-solvable tracking, mean-reverting, and ill-conditioned problems supply exact continuous optima, independently enclosed costs of stored held-action actors, a two-error identity, 30 policy certificates, and matched-accuracy computation paths. They complement rather than replace the original economy and external comparison. Every historical theorem, proof, failure record, and manuscript remains in the source tree and preservation supplement.

## Reproduce

From the repository root, use Python 3.11 with `numpy==2.3.5`, `scipy==1.17.0`, `mpmath==1.3.0`, and CPU `torch==2.10.0`.

```sh
python revisions/2026-09-22-r11/replication/test_revision.py
python revisions/2026-09-22-r11/replication/validate_revision.py --skip-pdf
python revisions/2026-09-22-r11/replication/accuracy.py --out /tmp/r11-accuracy-recheck
bash revisions/2026-09-22-r11/replication/build.sh
python revisions/2026-09-22-r11/replication/validate_revision.py
```

The external experiment is defined by `protocol.json`, `replication/robustness.py`, and `.github/workflows/r11-study.yml`. Its author implementation is pinned to `sx-fang/MartNet@991ea8dde5bad6ba912eb8cc48b0cb48dbdd6c2a`. Training clocks vary by machine; the stored raw outputs are the review evidence. Numerical acceptance is based on certificates and the declared tests, never on a favorable clock or missing-run exclusion.
