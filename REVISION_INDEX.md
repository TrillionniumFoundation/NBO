# Neural Bellman Operators — revision R2

**Revision date:** 15 September 2026
**Revision branch:** `revision/econometrica-r2-2026-09-15`
**Base revision:** `revision/econometrica-r1-2026-09-15` at `2c9e758c6974957b0a30f3cdf780a015c32300eb`
**Latest reviewed report:** `review/econometrica-r1-2026-09-15-2c9e758` at `37731a8d8c11de5d7ce012f9e1f631b91837d746`

## Authoritative reading order

1. `ECTA_R2.tex` — revised main manuscript, with separated NBO updates, corrected analytical anchors, conditional theorem, and scoped evidence.
2. `SUPP_R2.tex` — revised standalone supplementary appendix for temporal selves, dynamic games, trace estimation, and evidence rules.
3. `revisions/2026-09-15-r2/response_to_referee.md` — point-by-point response to R0–R12.
4. `revisions/2026-09-15-r2/preservation_map.md` — preservation and modification map.
5. `replication/README.md` and `replication/results_schema.json` — build and evidence protocol.
6. `replication/reviewer_diagnostics.json` — reproduced reviewer arithmetic/counterexample checks.
7. `revisions/2026-09-15-r2/revision_manifest.json` — source identity, build, and evidence policy.

## Scientific scope

R2 retains the paper's recursive-utility, endogenous-preference, time-inconsistency, dynamic-game, and high-dimensional objectives. It replaces the invalid joint composite-loss proposition with a separated policy-evaluation/policy-improvement iteration; states the Markov, boundary, recursive-utility, and comparison conditions needed for the conditional consistency result; corrects the Merton and Epstein–Zin anchors; and adds unilateral/equilibrium, boundary, probe-bias, and held-out error diagnostics.

Historical sources are immutable audit material. Their embedded arrays and illustrative figures are not R2 experimental observations unless a run-level provenance record is present. The R2 manuscript uses the Econometric Society class and builds in the verified environment with the commands in `replication/README.md`.
