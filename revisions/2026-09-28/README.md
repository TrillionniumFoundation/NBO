# NBO revision — September 28, 2026

The revised article is the root `ECTA.tex`; the coherent supplementary article is root `supp.tex`. Both use the repository's existing Econometrica class. `RESPONSE_TO_REFEREE.md` answers R1–R12. `SECTION_MAP.md` maps the original content to the revision. `archive/` preserves the complete original manuscript, supplement, historical comments, and template README; these are not current experimental evidence.

## Reproduce

From the repository root, with Python and the pinned requirements installed:

```sh
python revisions/2026-09-28/code/experiments.py
python revisions/2026-09-28/code/test_revision.py
python reviews/2026-09-15-econometrica/verify_counterexamples.py --output /tmp/reviewer-checks.json
pdflatex -interaction=nonstopmode -halt-on-error ECTA.tex
bibtex8 ECTA
pdflatex -interaction=nonstopmode -halt-on-error ECTA.tex
pdflatex -interaction=nonstopmode -halt-on-error ECTA.tex
pdflatex -interaction=nonstopmode -halt-on-error supp.tex
pdflatex -interaction=nonstopmode -halt-on-error supp.tex
```

`bibtex` can replace `bibtex8` where available. The original reviewer `--source-root` option expects the ORIGINAL root blobs. To check those identities after revision, provide a temporary directory whose `ECTA.tex` and `supp.tex` are copied from `archive/`; do not point that mode at the revised root manuscript.

The complete execution writes `results/experiments.json`, iteration CSVs, coefficient and grid NPZ arrays, environment information, and `SHA256SUMS.json`. It records 29 attempts and retains every declared seed. The read-only remote workflow regenerates these files and PDFs as an artifact tied to its source commit. The locally executed complete package, including binary arrays and PDFs, is also supplied as a conversation attachment. No queued or unobserved workflow result is treated as a pass.

The exact recorded local summary is committed as `results/experiments.json.gz`; `gzip -dc` reads it without altering the recorded output. `results/LOCAL_VALIDATION.json` records local checks and hashes. Numerical replay may differ in last bits and wall times across BLAS/CPU/TeX environments. The tests use explicit tolerances; they do not demand identical nondeterministic runtime values. `--quick` runs only a smoke subset and is NOT compatible with the full-run count/array regression tests or a substitute for the full recorded suite.

## Evidence distinctions

Portfolio runs exploit homogeneity; the coupled LQ runs exploit a quadratic-neural class and exact Lyapunov evaluation. The NDU grids are independent reference computations, not unrestricted neural fits. The temporal-self laboratory solves a derived homothetic equilibrium and finite-duration deviations. The static Cournot diagnostic and graph tests are not a dynamic MPNE computation. The general multilayer differential core is implemented and gradient-tested, but unrestricted neural solver comparisons remain separate, unexecuted work.

`results/diagnostic_history/` documents the superseded development run and gives a lossless source-reconstruction patch. The complete historical script and summary are also retained in the attached execution package. Its quadratic residual-reporting sign was corrected, the drift/payoff model was made genuinely noncommuting, the wealth boundary reset was made explicit, and the full suite was rerun. Those diagnostic artifacts are not the final evidence. Main and review branches are not modified by this revision.
