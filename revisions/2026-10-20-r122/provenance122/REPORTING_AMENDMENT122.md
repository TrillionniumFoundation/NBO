# Disclosed deterministic reporting corrections after F

## Original source and discovery

The scientific source remains F `2f483615c8bc0037e43ec01a16cce05c724f8c60`, including all 243 declared files. No original economic source, actor, drawn sample, policy outcome, population inference family, comparison-menu membership, computational-cost formula or manuscript theorem is changed by this amendment. The original reporter `code122/report122.py` remains SHA256 `b504bab12124c1a7dab04e5307b30297ab957aa918178c89f9c211556e8b11e2`. Two reporting defects are disclosed below. The second changes deterministic timed-scenario aggregation relative to the frozen implementation to satisfy the already-frozen written protocol; it is not described as a cosmetic change.

The post-freeze saved-evidence verifier development exposed a Python schema collision. Frozen `stats122.py` already emits `raw_independent_sample_gain_lower` and `raw_independent_sample_gain_upper`. Frozen `report122.py:economics` passes the whole statistics row through `dict(**s, ...)` while also supplying those two same keyword names. Python raises `TypeError` before a final reporter output is produced. This is a concrete serializer defect. The earlier artificial schema fixture did not contain these two redundant statistics fields and therefore did not detect it; its successful limited checks and that limitation are preserved.

The original frozen report attempt must actually be executed once on the completed primary, independent and statistics bytes, with its actual failure and outer process cost retained. It must not be silently relabeled as successful. The repaired report uses exactly the same input bytes in a new output directory and has its own immutable reporting-adapter commit before execution.

## Minimal correction and equality obligation

`verification122/report_schema_adapter122.py` imports the unchanged frozen reporter and temporarily wraps only its `economics` function. For each of the 116 safe cells, it independently sums the 32 saved rational raw independent gain endpoints and divides by 32. Both saved redundant statistics fields must equal those exact values. Only then does the wrapper remove the two fields from a shallow in-memory copy and invoke the unchanged frozen `economics` function. The frozen function recomputes and emits those same two fields. The wrapper checks those resulting fields again against the unchanged original statistics rows.

This supplies 232 exact pre-call equality checks, 116 complete safe-cell checks, and one unchanged frozen economics call. Any mismatch fails; it is not repaired, rounded away or silently overwritten. The original files are never edited. This schema component alone changes no economic mean, population formula, cost allocation or menu calculation. Its complete-schema artificial fixture passed, while preserving the original duplicate-keyword failure. Production source identities are not replaced by fixture source authenticators.

## Timed-scenario protocol conformance

The frozen `REPORTING_SPEC122.md`, under the economic reporting requirements, states: "Primary independent economics uses all 32 states. Each timed cost scenario uses the matching first 16-state economics". The frozen implementation instead calls `contrast()` over `range(N)` with `N=32` and caches those means solely by candidate/comparator. It then reuses the 32-state means for all four clock scenarios. Its timing-volume rows also incorrectly state `economic_state_units=32`. This contradicts the fixed state-matching rule, despite leaving primary economics and all fixed population inference unchanged. The read-only package-verifier audit discovered the mismatch before actual report execution; the earlier all-zero synthetic fixture could not distinguish the two aggregation rules.

The separately published `verification122/report_protocol_adapter122.py` installs the exact-equality schema component and wraps `price_tables()`. It first invokes the original frozen `price_tables()` without modification and retains **all** its outputs under `FROZEN_CODE_DIAGNOSTIC_`: 2,784 cost-volume rows, 28,800 pairwise price constraints, 384 full menus, and 96 all-three-clock intersections. These all-32-for-all-clocks tables are explicitly nonconforming diagnostics, not the adopted analysis.

It then computes every timing-scenario candidate/comparator gain interval from the saved independent original-policy enclosures at fixed row indices 0 through 15, dividing exact sums by 16. Same-policy exact zero, original qualification clipping, strict price inequalities, all conventional comparators, all four volumes and all three clocks remain unchanged. The timing menus and their three-clock intersections are recomputed from these matching means. Every original cost is retained exactly; no elapsed time is selected or remeasured. The 696 primary cost-volume rows, 7,200 primary pairwise constraints and 96 primary menus must be exactly equal to the original frozen output. The correction changes neither the 32-state primary analysis nor the 116/232/348 population family.

The protocol adapter verifies its own bytes, the unchanged schema-adapter bytes and this amendment against its separately published immutable commit before use. It also checks the unchanged frozen reporter hash. The primary failed report remains failed. This document and the saved diagnostic tables explicitly preserve the discrepancy between the F implementation and the F written protocol.

## Execution and accounting boundary

The corrected report is run in `results122/report-attempt02` after the original `report-attempt01` failure. Its `REPORTING_ADAPTER122.json` records the schema component's source/hash and 232 exact equalities; `REPORTING_PROTOCOL_ADAPTER122.json` separately records the protocol correction's source/hash, all retained diagnostic row counts, exact primary-table preservation, and the 16-state timing scope. Both component receipts share one outer report process and must not be added as separate runtime charges. The ordinary frozen `VERIFIED_SOURCE122.json` still authenticates F and all its original bytes. Both original and corrected outer report-process costs belong in the whole-study research ledger; neither is a representation-specific service penalty. Scientific cohort costs and original historical acquisition allocations are unchanged. The interrupted first primary attempt remains separately visible with bounded observed cost, as specified in the independently published administrative restart protocol.

This amendment corrects deterministic saved-result reporting. It does not change a prospective experiment after observing outcomes, supply new population observations or rehabilitate an unsuccessful original workflow. Success is asserted only for the adapter execution and its actual completed receipts. The untouched original frozen report remains an actually failed attempt.

## Reproduction

After the adapter commit has been published and the original failed attempt preserved:

```sh
python code122/launch122.py --receipt results122/launch-report-attempt02 -- \
  python verification122/report_protocol_adapter122.py --repair-commit ADAPTER_COMMIT \
  --source-commit 2f483615c8bc0037e43ec01a16cce05c724f8c60 \
  --primary results122/primary-attempt02 --independent results122/independent-attempt01 \
  --stats results122/statistics-attempt01 --output results122/report-attempt02
```

`ADAPTER_COMMIT` is replaced by the actual separately recorded immutable commit. The complete-schema artificial check under `provenance122/review/` executes the final frozen statistics serializer on artificial zero-economics records and verifies the untouched reporter's duplicate-key failure, followed by the repaired full report. Its scientific source authenticators are replaced only within that artificial test; production requires the real Git identities. It creates no original economic state, actor fit or economic evaluation.

The separate `reporter_protocol_fixture122.py` constructs unequal first and second halves, so its 32-state means are exactly zero while its 16-state means are generally nonzero. Its actual `REPORTER_PROTOCOL_FIXTURE_RESULT122.json` records 123,555 exact assertions, 19,884 changed synthetic timing-constraint endpoints, complete preservation of all cost fields and primary tables, and all original diagnostic rows. It calls pure table functions only, does not replace a source authenticator, and provides no scientific outcome or population observation. The retained complete-schema, original-failure and adapted-execution receipts describe the earlier artificial fixture separately.
