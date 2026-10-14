# Neural Bellman Operators -- R95

This revision answers the controlling R92 advisory report without changing the paper's title, author, economic technology or research topic. The sources are based on R94 commit `84148cd179fe58c280a91ad281c7a81656d49788`; the review is pinned at `bd2945b4b4e76b6a997dbcf7548f5fe24d3e92e6`.

## Current documents

- `ECTA.tex` and `build/ECTA.pdf`: the revised main article.
- `supp.tex` and `build/supp.pdf`: complete technical proofs.
- `appendix.tex` and `build/appendix.pdf`: numerical evidence and preserved historical sections.
- `response.md`, `response.tex`, and `build/response.pdf`: point-by-point referee response.

Fifteen complete former main-text sections are relocated, not deleted. `audit/local95/CONTENT_MAP95.json` records their identical source hashes. Original entry points remain under `preserved/R92-wrappers`; inherited compiled documents are retained separately and are never relabelled as the current PDFs.

## Mathematical and numerical additions

`sections/continuous95.tex` constructs original-law all-action lower witnesses, complete-controller upper enclosures, whole-state residual covers and strict continuum tail exclusions. `sections/proofs95.tex` proves primitive curvature and state moduli, includes imperfect KKT multipliers, and supplies a horizon-uniform fixed-accuracy construction for the scalar and vector investment economies. State, action, shock and exact-number costs are separate.

The frozen R94 protocol and eight numerical source files are unchanged. Six fitted continuations, four arms and two risk levels give 16,384 arm-state records from 4,096 independent initial states. All records meet the own-continuation tolerance 1/64 and original-optimum loss tolerance 1/16. All twelve simultaneous contrasts establish equivalence at the fixed normalized margin; none establishes strict superiority. ReLU has narrower residual brackets, while all fitted representations reduce local evaluation work. Calibration selects online risk-DP at both risk levels, and paid screening is slower. All these results are retained.

## Verification and provenance

`audit/local95` preserves the original local attempt, including missing historical-fixture errors, interrupted starts, local-only calibration timestamp, source-bound original tables and environment. Those historical limitations are not silently overwritten. `audit/remote95` and `RELEASE95.json` record the publication continuation's actual repository tests, raw-file identity checks, independent kernel replay and current builds. An absent or failed receipt is not a passed gate.

The source and evidence branches are:

```
revision/econometrica-nbo-r95-integrated-2026-10-13
revision/econometrica-nbo-r95-evidence-2026-10-13
```

Original measurement reports and frozen models are retained byte-for-byte. When published raw CSVs are reconstructed by deterministic replay, every byte hash must match the original retained report before the file is admitted as an original record. A replay never increases the independent sample size. Model selection, sample size, risk preference and tolerances are not changed after evaluation.

## Reproduction

Use a full or dependency-complete checkout, Python 3.13.5 and `requirements95.txt`, with BLAS/OpenMP threads fixed at one. From this directory run:

```sh
python code/run_tests95.py --output-dir audit/fresh-replay95/tests
python code/audit94.py --tag local95
python code/build95.py --audit-dir audit/fresh-replay95/build
```

Use a fresh explicit tag for numerical replication. Do not overwrite original fits, reports or machine-cost records. Current broader research obligations include rank/approximation-budget-matched fitting, a prospectively frozen optimized certificate-cost ablation, a second full independent largest-vector implementation, and complete energy/campaign-cost measurements. The new horizon theorem is not a claim that the largest-vector benchmark was executed.
