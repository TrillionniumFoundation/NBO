# Neural Bellman Operators — revision R3

**Revision date:** 15 September 2026
**Revision branch:** `revision/econometrica-r3-2026-09-15`
**Base revision:** `revision/econometrica-r2-2026-09-15` at `4267424c529e9c07966b1fe7660bcaaa35209881`
**Latest reviewed report:** `review/econometrica-r2-2026-09-15-4267424` at `4de25e5b54c79909959f6c1ca89c24506f7588c7`

## Authoritative reading order

1. `ECTA_R2.tex` — R3 main manuscript with the unified NDU objective, discrete temporal-self system, stronger exact-operator assumptions, bounded KKT/viability specification, and corrected evidence claims.
2. `SUPP_R2.tex` — standalone supplement using the same temporal-self equations and player-specific game convention.
3. `revisions/2026-09-15-r3/response_to_referee.md` — point-by-point response to F1–F12 of the R2 report.
4. `revisions/2026-09-15-r3/preservation_map.md` — preservation and provenance map.
5. `replication/run_r3_diagnostics.py` — executable deterministic reference/grid audit; it is not a neural training log.
6. `replication/r3_results.jsonl` and `replication/r3_raw_outputs.json` — run ledger and canonical raw payloads generated from the final source commit.
7. `replication/README.md` and `replication/results_schema.json` — build and evidence protocol.
8. `revisions/2026-09-15-r3/revision_manifest.json` — source hashes, review inputs, environment, build transcript, and evidence policy.

## Scientific scope

R3 retains the recursive-utility, endogenous-preference, temporal-self, dynamic-game, historical, and high-dimensional objectives. It distinguishes four evidence classes: exact operator statements, deterministic reference audits, neural training runs, and archival negative controls. The R3 harness executes the reference audits with explicit domains, terminal values, projected viability, best-response gaps, trace probe counts, coupled-resource dimensions, seeds, and raw-output digests. No historical embedded curve is used as current economic evidence.

The manuscript uses the Econometric Society class and is built with the commands in `replication/README.md`. Historical sources and earlier reports remain in the repository for review continuity.
