# R26 referee entry — Neural Bellman Operators

## Read in this order

`ECTA_R26.pdf` is the current 15-page article; `RESPONSE_R26.pdf` is the finding-by-finding response; `SUPP_R26.pdf` contains the new technical record and all 151 pages of the reviewed R24 article and supplement. The corresponding TeX roots compile with the retained Econometrica `econsocart` class. No historical scientific source/results have been overwritten.

## Frozen lineage

Latest report inspected: `reviews/2026-09-23-econometrica-r24/referee_report.md`, review head `0eb0400ae311333fb77826ef9e2f067718926ae8`, reviewed manuscript `14ce582e188f437cc8d99f310edd4f06515936a4`.

Pre-existing R25 evidence is retained at `c78d934c0b3b8d346a40c7ddcaf415e167462265`. R26 is an additive revision on that exact base, not a replacement of concurrent R25 work. Source and evidence are under `revisions/2026-09-23-r26/`.

## Material changes

A synchronous certification-coupled operator is executed with full optimizer rollback. Six new trajectories yield 18 decisions: 13 accepted, 5 rejected. Four isolated shadow continuations differ from the actual restored trajectory. All states and checks are retained; these are diagnostic stress runs, not held-out efficiency claims.

Centered second-order interval jets certify the two fixed stochastic-reference neural policies below 0.001 on 32,768 cells, versus the inherited 262,144-cell stopping rule. Every coarse failure is retained. An exact rational Bernstein certificate verifies the unchanged direct policy at 1.2978908373252045e-7, eliminating the old derivative-coefficient rounding shortcut. This is a verification improvement, not a neural-efficiency result.

The article adds complete proofs of precision-adaptive payoff separation, conditional finite-work quotient polling with explicit oracle cost, the stochastic completion, interval jets, and exact polynomial verification. It integrates the pre-existing expanded calibration and moving historical-transport evidence with explicit chronology and cost definitions.

## Scientific status, not a closure claim

The original economy, current-state/full-domain objective, and 0.01 target remain unchanged. The inherited continuation bound is 7.181834580823298, and no separate policy-payoff improvement is proved. The original continuous stopped-gradient certificate and neural accuracy/work dominance over direct L-BFGS-B remain unestablished. Auxiliary-model certificates are not substituted for those objectives. The response covers F1–F12, T1–T6, and N1–N8 individually.

## Reproduction and delivery

See `revisions/2026-09-23-r26/REPRODUCE.md`, `PROTOCOL.md`, `results/PUBLICATION_SUMMARY.json`, `results/test_summary.json`, and `results/historical_pdf_audit.json`. The old root index is preserved in `source_audit/REVISION_INDEX_before_R26.md`.

The delivered Git bundle requires the exact frozen R25 base above and carries two new local revision references. At preparation time no remote write was available or completed. `publish_revision.sh` in the delivery package performs guarded, non-force publication and verifies the remote heads; an artifact or local branch alone is not proof of a remote push.

## Repository-side publication

The original preparation metadata above is retained as historical provenance. This remote package is reproduced from the 35 hash-verified delivered source files and the exact pinned R24/R25 inputs. All eleven checks and the 151-page preservation audit must pass before the workflow atomically creates both R26 references. The successful workflow artifact contains `R26_REMOTE_PUBLICATION_RECEIPT.json`, recording the exact commit and the read-back of both remote heads. No existing branch is overwritten.
