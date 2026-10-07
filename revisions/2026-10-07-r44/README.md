# Neural Bellman Operators — R44

Authoritative revision of the existing paper, responding to the R42 advisory referee report. The title, author, controlled-economy framework, original theory and applications are preserved.

Read [the main article](build/ECTA.pdf), [technical supplement](build/supp.pdf), and [point-by-point response](response.md). Sources are [ECTA.tex](ECTA.tex), [supp.tex](supp.tex), and [response.tex](response.tex). All 24 direct comparison intervals are in the supplement. [Publication summary](audit/PUBLICATION_SUMMARY.json) and [test audit](audit/TEST_AUDIT.json) give machine-readable results.

Seven unchanged neural policies now meet their previously unresolved tighter targets after residual-only recertification. Original weights AND deployed actors are retained. The original R42 capped failures are not rewritten. All 24 direct neural-minus-ridge cost intervals contain zero; no sign or equivalence claim is made. Original conventional-comparator and precision findings remain visible. New diagnostic clocks are not reconstructed end-to-end or isolated comparative timings.

## Complete retained paper

The [unchanged R41 article](../2026-10-07-r41/build/ECTA.pdf), [unchanged original supplement](../2026-10-07-r41/build/supp.pdf), and [complete economic applications](../2026-10-07-r41/build/applications.pdf) remain in the repository, along with every earlier revision and review. [Preservation audit](audit/PRESERVATION.json) records their hashes and labels. R44 controls the current empirical account; older descriptions remain historical, not alternative current claims.

## Reproduce and build

From repository root, run `python revisions/2026-10-07-r44/code/build.py`. Requirements: Python, numpy, scipy, a LaTeX installation with the packages used by the bundled R41 econsocart template, and BibTeX. The build does not train or retime anything; it audits frozen evidence and compiles the documents.

The published branch contains `evidence/2026-10-07-r42` materialized from artifact 11465997076 of workflow 37581511628, exact archive SHA-256 `540f80f65c27b9998b2a54375f79413f1a1f3d82bd04e50b810dba6dfed607cc`. The original R41 publication artifact 11460768113, workflow 37572319968, has SHA-256 `b5dc1a9fdcedc3279dbd7e9c190425f7e856f1fbcd67083e7452c2febc06aac6`. These identities are immutable input anchors, not substitutes for the materialized files.

For a new scientific run, copy the revision into a fresh working tree, keep the pinned evidence, and move the completed `results` and diagnostic-run logs to a separate immutable directory. Run `python code/study.py audit`, `python code/run_diagnostics.py <absolute-revision-directory>`, and `python code/run_pairs.py <absolute-revision-directory>` from the revision directory. The study refuses to overwrite completed result records. Preserve new clocks separately; a new execution is a new observation, not a rewrite of this release.

`STUDY_PROTOCOL.md` was committed before these diagnostics. `code/study.py` is the source-bound executed program; `audit/FILES_SHA256.json` binds the release. An independent referee should read the response's M5–M7 entries: this release does not claim a new adaptive-grid comparator, nonlinear dimension frontier, or repeated isolated nonlinear timing study.
