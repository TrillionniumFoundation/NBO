# Neural Bellman Operators — R41

Revision of the existing NBO paper responding to the R39 advisory referee report. The title, original economic framework, and complete applications remain unchanged.

## Read the revision

- [Main article](build/ECTA.pdf) and [self-contained source](ECTA.tex).
- [Technical supplement](build/supp.pdf), including arithmetic and dimension/continuous-innovation work proofs.
- [Point-by-point response](response.md) and [response PDF](build/response.pdf).
- [Complete applications](build/applications.pdf), [historical article](build/historical_article.pdf), and [historical supplement](build/historical_supplement.pdf).
- [Executed study](results/R41_STUDY.json), [deterministic audit](audit/RESULT_AUDIT.json), [release audit](audit/RELEASE_AUDIT.json), and [file hashes](audit/FILES_SHA256.json).

The learned current and future networks are now directly Bellman-certified. The new four-economy study passes a 0.02 query-state policy target; all-state bounds are reported separately. Binary32 rejection and binary64 escalation are executed and charged. Numerical execution has a nonzero error account. A contemporaneously reoptimized spline remains a strong competitor; no unobserved neural speed or cost superiority is claimed. The multidimensional continuous-innovation theorem is not misreported as an executed nonlinear scaling benchmark.

The R40 failed-run outputs and R39 publication are preserved; new clocks are not replacements for inherited clocks. See the response for exactly which comparative-performance requests still require additional evidence.

Build from repository root: `python revisions/2026-10-07-r41/publication/build.py`. Reproduce science in a fresh directory, never over completed records: `python revisions/2026-10-07-r41/code/study.py`.
