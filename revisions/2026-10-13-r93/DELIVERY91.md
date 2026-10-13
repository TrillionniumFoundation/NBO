# Neural Bellman Operators — R91 referee package

## Current documents

| Document | PDF | Editable source | Pages |
|---|---|---|---:|
| Main article | [ECTA.pdf](build/ECTA.pdf) | [ECTA.tex](ECTA.tex) | 84 |
| Technical supplement | [supp.pdf](build/supp.pdf) | [supp.tex](supp.tex) | 43 |
| Numerical and development appendix | [appendix.pdf](build/appendix.pdf) | [appendix.tex](appendix.tex) | 123 |
| Point-by-point referee response | [response.pdf](build/response.pdf) | [response.md](response.md) | 5 |

This package revises the original **Neural Bellman Operators** paper. The original title, author, economic primitives, original-optimum objective, substantive applications, inherited active sections and unfavorable evidence remain. The current Econometrica class files are unchanged. No earlier revision directory or review branch is overwritten.

## Which review and manuscript were used?

The controlling advisory report is at commit `b030d87d7e96440eb25a3178c94ee6a87940cdb0`, in `reviews/2026-10-12-econometrica-numerical-methods-r84/referee_report.md`. It reviewed delivery `c1314494aca25e68f1426b554938e6fe89dd8409`. R91 starts from the intervening complete R90 manuscript at `9e06160b5464c41a5b84eaab9c3c4d171fc22832`; it does not repeat the earlier R67/R54 response.

The current verified source commit is **`437e311238d5a0ba8123dd1fba1abf9a7a6053af`**. Actual current PDFs, table reconstruction and verification records are committed at **`1f343cb2d3521d87445e1c0281424056d36bfc2d`**. The final delivery adds this navigation and the layout/release records only; the checked source and PDF bytes remain unchanged.

## Substantive amendments

**Main Theorem 22**, in Section 15 (pages 46–49), supplies a signed original-law complete-policy loss bound for the original monotone cash-invariant recursive evaluation. The all-action lower discrepancy and selected-action upper discrepancy replace an unnecessarily symmetric transfer charge. The proof permits changes at every date, preserves original feasible actions, retains endogenous occupations and does not apply linear expectation telescoping to nonlinear risk. A sharp deterministic example attains the signed allowance, at half the earlier symmetric allowance.

**Proposition 23** gives explicit original-law transport coefficients for upper-tail average value at risk and entropic evaluation. The tail coefficient is sharp; entropic sensitivity depends on continuation oscillation. A monotone coupling supplies a one-sided improvement. Their dated resource account does not multiply all future tail-risk factors, while actual continuation moduli and construction work remain charged.

The full proofs, stationary extension and objective-preservation counterexamples are in **Technical Supplement 15, pages 39–43**. The new tests retain quantile atoms, exact ties, terminal errors and the distinction between global constant bias, statewise action-independent bias, and static versus nested risk. The original complete-policy, population, shared-proposal, prospective selection, price-fee, strategic and horizon sections remain active. [CONTENT_MAP91.md](CONTENT_MAP91.md) and the response map all twelve major objections to the active material.

## Verification actually completed

Workflow run **38347272108**, job **115131469766**, completed successfully. The current recipe ran **325 tests in 15 suites, with no skipped tests**, including 36 new signed-risk tests and 14 new regressions for inherited R86 claims. The latter are new R91 tests, not a recovered historical R86 execution.

The independent original-law replay recomputed **139,264 frozen rows**, **1,253,376 complete paths per implementation**, and all **144 stream estimands**. It reproduces the stored economic records after the NumPy scalar-integer portability repair; it adds no independent observations. The inherited common-readout certificates were independently checked as well.

The new exact finite-state diagnostics enumerate **27 configurations**, all **1,728 complete three-date policies**, and **3,456 initial-state inequalities**. Another 216 finite-law cases compare threshold minimization with an independently written capped-density risk evaluator. General continuous-domain and entropic statements rely on the displayed proofs, not those finite fixtures.

All required tables were reconstructed. All four current PDFs passed checks for undefined references, duplicate labels, missing glyphs, fatal errors and overfull boxes. A fresh typesetting reconstruction reproduced every current PDF and extracted text **byte-for-byte**. This clean comparison is a document-source reconstruction, separate from the scientific replay; it is not a fresh sampling experiment.

The actual downloaded cloud PDFs received AI-assisted rendered-page layout inspection: all **255 pages** in 23 overview contact sheets, plus seven pages at readable enlargement. No visible clipping, overlap, broken glyphs or unexpected blank pages was observed. The record states its exact inspection coverage and PDF hashes; it is not represented as human referee approval or full-magnification reading of every page.

Read [the full verification record](audit/reproduction91/VERIFICATION91.json), [clean typesetting comparison](audit/reproduction91/CLEAN91.json), [actual-PDF layout record](audit/VISUAL91.json), and [release manifest](audit/RELEASE91.json). The original failed delivery attempt and arithmetic amendment are explained in [PORTABILITY91.md](audit/PORTABILITY91.md).

## Scientific status retained for the next referee

This is a complete, checked **referee package**, not a declaration of editorial acceptance or of every scientific objection being closed. The largest-vector independent reimplementation and matched vector comparator tournament are not supplied by the new finite-state diagnostics. Measured energy and application-specific monetary calibration are also not supplied. These remain evidence requirements inside the original scope, rather than reasons to delete those sections or replace the topic. The shared-proposal study's unfavorable incremental ReLU query-work outcome and unresolved economic comparisons remain visible.

The next referee can examine the complete original paper, the two new general results and their proofs, all twelve point-by-point responses, and the exact source-bound numerical and publication records in this directory.
