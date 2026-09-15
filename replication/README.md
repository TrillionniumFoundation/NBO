# NBO R3 replication and audit record

The authoritative sources are `ECTA_R2.tex` and `SUPP_R2.tex`, revised on branch `revision/econometrica-r3-2026-09-15`. Historical `ECTA.tex`, `supp.tex`, embedded arrays, and prior review folders are preserved for provenance. The R3 executable harness is a deterministic reference/grid audit. It is not a reconstructed neural training log; a neural result requires weights, a run log, and the same ledger fields.

## Build

```sh
pdflatex -interaction=nonstopmode -halt-on-error ECTA_R2.tex
bibtex ECTA_R2
pdflatex -interaction=nonstopmode -halt-on-error ECTA_R2.tex
pdflatex -interaction=nonstopmode -halt-on-error ECTA_R2.tex
pdflatex -interaction=nonstopmode -halt-on-error SUPP_R2.tex
pdflatex -interaction=nonstopmode -halt-on-error SUPP_R2.tex
```

## Executed R3 reference audit

```sh
python3 replication/run_r3_diagnostics.py \
  --code-commit "$(git rev-parse HEAD)" \
  --output replication/r3_results.jsonl \
  --raw-output replication/r3_raw_outputs.json
```

The script emits thirteen deterministic success records: corrected Merton/no-short anchors, a bounded NDU projected dynamic program, beta=.7 and beta=1 temporal-self recursions, player-specific Cournot best responses, Epstein--Zin domain checks, Hutchinson probes `K=1,2,8,64`, and coupled quadratic-resource audits at dimensions 4, 8, and 16. The coupled timings are local CPU measurements; no H100 timing is asserted. Applicable metrics are non-null; fields marked `null` in the schema are explicitly not applicable to that model's estimand.

Every result carries a run ID, seed, configuration digest, source commit, state/action domain, terminal and boundary specification, stopping rule, applicable error metrics, and raw-output digest. Failed pilots are retained when they occur. Each `raw_output_sha256` is the SHA-256 digest of the canonical raw payload for that run; the aggregate raw JSON file preserves those payloads for inspection.

Historical arrays embedded in `ECTA.tex` are archival negative controls. They are not read by the R3 harness and cannot supply a current policy or economic claim. Figures and tables for current results must be generated from `r3_results.jsonl` or a future neural ledger with the same provenance fields.
