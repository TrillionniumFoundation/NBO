# Neural Bellman Operators — R32

This revision responds to the R21 advisory referee report without changing the paper's title, topic, original controlled-economy model, or economic applications. It integrates the subsequently committed R23–R31 theory and evidence rather than resubmitting an independent R16 candidate.

## Pinned inputs

- Referee: `review/econometrica-numerical-methods-r21-2026-10-05-2789166`, `reviews/2026-10-05-econometrica-numerical-methods-r21/referee_report.md`, blob `947147612cc22f5e10ff15faf347fcb3de222656`.
- Reviewed article: commit `278916666b32e03081ffe8d4aa05d9766c259b85`.
- Revision base: commit `2bbd8900080a009e806f8d9d0f27fb9f0eefe9e1`, tree `cd591ef54ba92774294c2a717c1051c876d61c55`.
- Frozen recursive experiment: scientific source `01d627862b2c6fbc00c49c0c61968fc8a76e3363`; all 72 registered services are replayed unchanged and separately identified. The original R31 execution and its measured clocks are not overwritten.

## Reading order

The current native Econometrica article is `ECTA.tex`; `supp.tex` contains current full-policy and constructive proofs. `response.md` answers every B1–B9 and M1–M10. The Economic Applications companion retains the original models. The historical article and supplement preserve the original R21 argument and adverse results verbatim apart from cross-reference routing in their new wrappers. Original source files are never edited or deleted.

The new section gives an explicit gradient–curvature implication for trained square critics, including inexact own-policy evaluation. It rejects the zero-gradient singular saddle, proves the sufficient rank bound, propagates coefficient error to the full-action residual, and makes the recursive terminal transformation explicit. These are mathematical implications, not a claim that neural fitting is faster than the structural solution of a quadratic economy.

## Reproduction and provenance

`publication/assemble.py` retrieves immutable scientific inputs, executes tests and the unchanged frozen catalogue, constructs the publication, checks references, and creates file hashes. The GitHub Actions workflow records the exact source commit. `publication/publish.py` writes only the new R32 publication and evidence paths to a new referee-ready revision branch, with an immutable parent and no force push. Its release record distinguishes newly executed results from inherited results.

The small-matrix curvature checker uses exact rational PSD checks. Its target-radius premise must be supplied by an independent evaluator. It is not the fifty-dimensional stopping verifier and is not included in the primary work comparison.
