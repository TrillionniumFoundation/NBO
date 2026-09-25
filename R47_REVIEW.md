# R47 — Certified Bellman Operators for Costly Policy Revision

## Review entry points

- **Article:** [ECTA_R47.pdf](ECTA_R47.pdf), [ordinary TeX entry](ECTA_R47.tex).
- **Full numerical supplement:** [SUPP_R47.pdf](SUPP_R47.pdf).
- **Response to R44:** [RESPONSE_R47.pdf](RESPONSE_R47.pdf), [16 findings and 30 comments in JSON](revisions/2026-09-26-r47/REFEREE_RESPONSE.json).
- **Computation and verification report:** [COMPUTATION_R47.pdf](COMPUTATION_R47.pdf).
- **Preserved complete R45 and earlier history:** [HISTORY_R47.pdf](HISTORY_R47.pdf).
- **Current source directory:** [paper](revisions/2026-09-26-r47/paper).
- **Content identity:** [publication manifest](revisions/2026-09-26-r47/PUBLICATION_MANIFEST.json), [build logs](revisions/2026-09-26-r47/build).

The final Git commit containing these materialized files is the review object. No base64 staging fragment needs to be decoded to read it. The source/build commit is recorded separately in the manifest; a manifest intentionally does not embed its own future Git commit hash.

## Scientific changes

The paper retains the common randomized Markov target and every-state/date operating protection. Its central result is the restart-price Bellman certificate with an exact nonnegative-slack gap decomposition, valid for bounded Borel controlled kernels and operating ties. The new paired operating-witness budget and continuation-best repair quantify approximation on both endpoints. Complete finite search, strict-gap refinements, controlled-atomic upper density, structural paired results, adverse comparisons, and original continuous experiments remain present or fully preserved in the historical volume.

The original R44 frozen primary success rates remain **4/12 Bellman and 5/12 aggregate** at absolute width `1/1000`. The **retrospective** price-strengthened search reaches **6/12 primary and 3/4 tie cases**; its scalar certified portfolio reaches **9/16**. It reuses earlier certified incumbents, whose cost is not disguised as new incremental time. The exact-tie restart interval has width approximately `3.0701e-11`. All non-target rows remain visible.

The current revision independently replays **64 inherited R46 price/tree objects**, constructs and independently checks **64 new operating-witness precision objects**, and rejects **51 malformed witness objects** with three valid controls. Precision variants and paired methods are not counted as independent environments.

## Evidence boundaries

SCIP native nonlinear global lower bounds are still solver-reported rather than independently certified; only its feasible policies can contribute an exact upper. The 64 precision objects test the approximate-witness interface on finite models, not a difficult high-dimensional learned oracle. No empirical calibration is claimed. The original **30 positive-cost continuous randomized intervals remain open**, and generic paired continuum convergence is not inferred from one-sided upper density and valid price lower bounds.

## Provenance and preservation

- Referee report: `reviews/2026-09-25-econometrica-r44/referee_report.md` on review commit `bdfd4e94b74a41ef904158d0061d10a6fcf39c8c`.
- Numerical baseline: `fb88b1122ce5709d36104993937083b57470d1de`, R46.
- New branch: `revision/econometrica-r47-complete-referee-2026-09-26`.
- Original R44/R46 code, models, proofs, failures, and protocols are inherited unchanged. The build rejects modifications or removals of baseline tracked files.
- The R45 authoring sources are preserved and hash-checked. Their original standalone local transport ZIP is not the new publication format; their scientific inputs are inherited from the repository, and their complete manuscripts are reproduced here.

Run `bash R47_BUILD.sh` from the repository root. This replays certificates, constructs and checks the witness audit, regenerates tables/figures, and compiles current and preserved documents. It does not rerun the original optimization benchmarks. Run `python revisions/2026-09-26-r47/replication/finalize.py` after the build to record final hashes. The manifest and JSON records separate the original execution platform from current replay times.
