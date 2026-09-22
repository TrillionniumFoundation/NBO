# R16 — Neural Bellman Operators: review entry point

The current revision responds to the complete R14 referee report at commit `bb09ac177fc766aea8aba26cb6a40b8aff68528c`. It preserves the paper title, author Qian QI, Peking University affiliation, original nonlinear economic model, and all historical scientific sources.

## Readable review artifacts

- [Main manuscript, PDF](ECTA_R16.pdf) and [LaTeX entry](ECTA_R16.tex).
- [Technical supplement, PDF](SUPP_R16.pdf) and [LaTeX entry](SUPP_R16.tex).
- [Point-by-point referee response](revisions/2026-09-23-r16/RESPONSE_TO_R14.md).
- [Replication instructions](revisions/2026-09-23-r16/README.md).
- [Publication and validation manifest](revisions/2026-09-23-r16/PUBLICATION_MANIFEST.json).
- [Historical preservation manifest](revisions/2026-09-23-r16/PRESERVATION_MANIFEST.json).
- [Machine-readable paper summary](revisions/2026-09-23-r16/results/paper_summary.json).

The manuscript adds a stopping-trace discontinuity proof, signed accessibility-weighted verification, an exactly trace-controlled neural architecture, a quantitative conditional policy-iteration theorem, and a state-global neural certificate for a coupled inventory economy. It reports twenty original-economy neural checkpoints, six continuously verified classical candidates, twenty coupled-state neural checkpoints, a complete eighteen-node MPFR audit, and a fresh model-generated price continuum.

**Scope of numerical success:** the inventory neural final checkpoints meet the 0.001 per-coordinate target, and the two separately identified price-continuum calculations meet 0.01. The original nonlinear full-horizon neural checkpoints and six common-witness classical candidates do not meet 0.01. The inventory and time-control results are not reassigned to the original nonlinear neural policy. The response identifies the remaining scientific gates explicitly.

The working branch is `revision/econometrica-r16-certified-policy-iteration-2026-09-23`. A referee-copy branch, `revision/econometrica-r16-referee-copy-2026-09-23`, points to the completed materialized publication. Neither the historical review branch nor the incomplete R15 branch is modified. Consult the manifests for immutable source/result identities, counts, exact endpoint summaries, PDF hashes, and compiler validation.
