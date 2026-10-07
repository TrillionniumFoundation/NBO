# Neural Bellman Operators — R46

**Author:** Qian QI. **Date:** 7 October 2026.

The authoritative referee object is the complete `revision/econometrica-nbo-r46-review-ready-2026-10-07` branch at its final publication commit. The witness-source branch is staging, not a submitted manuscript. The publication workflow refuses to replace an existing review-ready branch.

## Manuscript and response

[Main article (PDF)](build/ECTA.pdf) · [Main source](ECTA.tex) · [Technical supplement (PDF)](build/supp.pdf) · [Supplement source](supp.tex) · [Point-by-point response (PDF)](build/response.pdf) · [Response text](response.md).

This revision extends the complete R45 manuscript at `336ea58decb4fae486efa41bb86e69a28879d9d6`. The title, author, economic subject, active R45 labels, original theory and applications are retained. The extensive R41 theory and application companions remain physically preserved under [preserved/R41](preserved/R41). Historical R44/R45 files and earlier revision/review branches are not overwritten.

## Review chronology

The latest report by commit time is the supplemental R43 review at `9a1ce0502a2cb8f57c697d1df9ba796da0403474` (12:27:38 UTC), reviewing the incomplete snapshot `3c9ad7a969bddf3c79ec5dc07e4b74704fed8615`. It is not a review of R45. The substantive R44 report at `5d4eca82b5477c4f0305f0f90bf9adc1635ec5de` was committed earlier at 10:42:23 UTC. The response addresses every R43 B1–B10/M1–M10 item and maps continuing R44 concerns to the new work. The [R43 report and audit files](../../reviews/2026-10-07-econometrica-numerical-methods-r43) are materialized from their exact pinned blobs in the final branch. The historical incomplete R43 object is not relabeled as complete.

## Mathematical addition

A one-sided policy sandwich combines the optimal Bellman-residual upper bound with the selected policy's residual, under the original monotonicity, cash-invariance and admissible-policy conditions. The min-plus ReLU continuation retains the original feasible action attaining each numerical label. Selecting the minimizing cone's action makes its selected-policy residual at most the numerical query error. The sufficient nonterminal allowance is half the previous separated construction's allowance, with the terminal account unchanged.

The result includes deterministic resource allocation, exact scalar witness compilation, rational switching boundaries and explicit allowances for approximate index selection, state acquisition and feasible action execution. The critic is a ReLU circuit; the possibly discontinuous action-index selector is not described as a continuous ReLU output. Classical Lipschitz envelopes and minimum gates are credited. The theorem does not imply that conventional implementation is impossible, that arbitrary neural optimizers converge, or that actual policy costs are ordered by their certificates.

## Completed matched study

The [protocol](STUDY_PROTOCOL.md) was committed at `62506d4c67b80fe0709d7493775cf555c111315b` before the complete execution. The study contains 36 services, 216 rungs and 72 distinct method/economy/resolution rows: two horizons, two prices, three generators/selectors, six resolutions and three isolated repetitions. Every rung starts from primitives. The two cone variants have identical critics and original node actions, isolating the returned selector. Both nearest-node comparators, including the spline, receive the strengthened one-sided certificate.

All three methods attain 1/4 and 1/8 in 12/12 services, and 1/16 in 6/12. The witness certificate is tighter than the same-critic nearest-node certificate in 24/24 unique comparisons and tighter than the strengthened spline in 23/24. The exception at horizon 4, price 1, N=16 is retained. The declared first-crossing resolutions coincide for all methods. Spline is faster than witness in all 30 common successful target/repetition observations; witness is faster than the nearest-node neural ablation in all 30. Repetitions have byte-identical checkpoints and are timing observations, not independent economic draws.

The improvement is a certificate and constructive-policy result, not a direct policy-cost ranking or general neural timing advantage. Original capped R42 outcomes, selected R44 recertifications, all 24 unresolved coupled direct-cost intervals, the R45 construction catalogue and adverse precision findings remain distinct and unchanged. A genuinely high-dimensional nonlinear comparison and calibrated economic discovery are not manufactured from this scalar study.

## Evidence and validation

Study source: `f91835f150fdf981f5bab43416121583444a36c7`. Study evidence: `257a7b207adf72f07d62d025c93d71a6e1ecb2d2`. Successful study workflow: `37623758585`. Artifact: `11483102637`, SHA-256 `8cb0fa519bb5e9c15760541d29ca3af5312e73ca728a39ea81a5fc521ba7235a`. These anchors supplement the [materialized raw records](results/services), not replace them.

[Release audit](audit/RELEASE_AUDIT.json) · [Complete numerical summary](audit/PUBLICATION_SUMMARY.json) · [Checkpoint reconstruction](audit/RESULT_AUDIT.json) · [Preservation audit](audit/PRESERVATION.json) · [File hashes](audit/FILES_SHA256.json) · [Development disclosure](audit/DEVELOPMENT_DISCLOSURE.md).

The build reruns 14 new exact regressions, 13 inherited R45 regressions and 14 inherited R44 regressions, reconstructs every new checkpoint/formula/first crossing, and compiles all three documents. The release gate checks the latest review blob, authoritative root entry points and unchanged historical R44/R45 paths. Compilation rejects undefined references, duplicate labels, missing characters and overfull boxes. Reproducibility tests are not mathematical peer approval or a journal decision.

## Reproduction

From the repository root:

```sh
python revisions/2026-10-07-r46/code/build.py
```

Dependencies: Python, NumPy 2.1.3, SciPy 1.14.1, Pandoc, PDFLaTeX, BibTeX and pdfinfo, with the committed Econometric Society LaTeX inputs. On a minimal Ubuntu installation, the publication workflow installs texlive-latex-extra, texlive-fonts-recommended, texlive-science, pandoc and poppler-utils.

The build reads ordinary committed sources and frozen results. It requires no capsule decoding, expiring artifact download or retraining. A new study execution is a new observation and must use a clean result directory; `code/execute.py` refuses to overwrite a completed catalogue. Internal clocks include failed rungs through checkpoint fsync, while process clocks additionally include startup and warm-up. CPU frequency is uncontrolled. Rational storage, comparison counts and primitive evaluations are not complete FLOP or bit-operation counts.
