# Neural Bellman Operators — R39

Current integrated revision responding to the R37 advisory report. Original topic and complete economic applications retained.

- [Main paper](revisions/2026-10-07-r39/build/ECTA.pdf), [self-contained TeX](revisions/2026-10-07-r39/ECTA.tex).
- [Technical supplement](revisions/2026-10-07-r39/build/supp.pdf).
- [Response](revisions/2026-10-07-r39/response.md), [PDF](revisions/2026-10-07-r39/build/response.pdf).
- [Complete applications](revisions/2026-10-07-r39/build/applications.pdf).
- [Retained historical article](revisions/2026-10-07-r39/build/historical_article.pdf) and [historical supplement](revisions/2026-10-07-r39/build/historical_supplement.pdf).
- [Release audit](revisions/2026-10-07-r39/audit/RELEASE_AUDIT.json) and [new endpoint/source audit](revisions/2026-10-07-r39/audit/R39_AUDIT.json).

R39 adds nonlinear full-policy construction, all-state trained-ReLU verification, native complete-step residual bounds, complete-work accounting and nonlinear investment-price policy comparisons. The 315 R38 economic services are re-audited, not rerun or retimed. The structural and spline baselines remain faster in the stated comparisons. No universal neural work advantage or journal acceptance is claimed.

Build from the repository root with `python revisions/2026-10-07-r39/publication/publish.py build`. Materialized active sources require no historical input expansion. The publication workflow restores pinned artifact dependencies when needed; hashes and source identities are recorded.
