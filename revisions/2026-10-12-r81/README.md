# Neural Bellman Operators — R81

Ordinary sources: `ECTA.tex`, `supp.tex`, `appendix.tex`, `response.md`.
The corresponding current PDFs are under `build/` only after successful build.

R81 integrates the separately frozen R80 factorial experiment into the original
NBO paper. It adds affine-calibrated qualification, exact action-switch duals,
optimizer-class policy-cost transfer and a complete conditional charge account.
Both calibrated own-controller gains and the reversed matched basis ranking are
reported. Every inherited active section and scientific record is preserved.

The controlling advisory report is R67 (11 October 2026), review commit
`4b27b56f4514f6c1d77b69fe707f7202f8b06b19`. The executed R80 baseline is
`ec8d40a058bfc03a88a62a223559698c5e849b22`.

Full offline build, from a checkout containing the pinned dependency revisions:

    python3 revisions/2026-10-12-r81/code/build81.py

`audit/RELEASE81.json` records current-source tests, complete bin replay, exact
switch verification and typography checks. `audit/CLEAN_REBUILD81.json` records
a separate clean-archive build. `audit/FINAL_DELIVERY81.json` binds the delivered
sources and PDFs only after both pass. Visual inspection, if performed, is a
separate hash-bound record; it is not implied by compilation or text extraction.

`CONTENT_MAP81.md` gives every inherited section's reading location. Old files
in `preserved/` and old-numbered audit files retain their historical provenance.
No new R81 independent policy-cost observations or scientific retiming is claimed.
