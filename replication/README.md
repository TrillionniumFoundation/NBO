# NBO R2 replication and audit record

The authoritative manuscript is `ECTA_R2.tex`; the standalone supplement is `SUPP_R2.tex`. Historical `ECTA.tex` and `supp.tex` are preserved and are not the R2 manuscript.

## Build

The source uses the Econometric Society class and the packages listed in `revisions/2026-09-15-r2/revision_manifest.json`. The current checkout was built with:

```sh
pdflatex -interaction=nonstopmode -halt-on-error ECTA_R2.tex
bibtex ECTA_R2
pdflatex -interaction=nonstopmode -halt-on-error ECTA_R2.tex
pdflatex -interaction=nonstopmode -halt-on-error ECTA_R2.tex
pdflatex -interaction=nonstopmode -halt-on-error SUPP_R2.tex
pdflatex -interaction=nonstopmode -halt-on-error SUPP_R2.tex
```

The R2 source removes the unavailable `algorithm`, `algorithmicx`, `algpseudocode`, and `newpxtext` dependencies; pseudocode is written as mathematical update definitions. Build warnings about undefined references disappear after the final LaTeX pass except for historical appendix bookmark duplication and ordinary underfull boxes.

## Verification available in this checkout

The reviewer diagnostics are rerun from the historical script and written to `replication/reviewer_diagnostics.json`:

```sh
python3 reviews/2026-09-15-econometrica/verify_counterexamples.py \
  --output replication/reviewer_diagnostics.json
```

The output reproduces all twelve arithmetic/counterexample checks in the R1 report. It is explicitly **not** an author training replication. No historical hand-entered curve is promoted to an R2 experiment without a run identifier, seed, configuration hash, source digest, and raw output.

## Authoritative result schema

Every future solver result must be one JSON object per line in `results.jsonl`, conforming to `results_schema.json`. Required fields include the model, run ID, seed, configuration hash, code commit, state/action domains, horizon and boundary specification, optimizer and step sizes, Hessian mode and probe count, stopping rule, failure status, held-out distribution, and separate value/policy/boundary/improvement errors. Failed runs are retained. Figures and tables must be generated from this file, never from embedded TeX arrays.

Historical arrays embedded in `ECTA.tex` are negative controls. They document the reviewed source and are deliberately not copied into `results.jsonl`.
