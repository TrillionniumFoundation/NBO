# Neural Bellman Operators — R126 Econometrica author revision

This is an author revision of the original Neural Bellman Operators paper. It preserves the recursive economic problem, continuation critics, feasible actors, complete original-policy value, prior theorems/proofs and all negative evidence. It is not an external referee review or a different research topic.

The repository-layout referee package is `release126/NBO_R126_REFEREE_READY.tar.gz`; its checksum and complete archive-member verification are in `release126/ARCHIVE_IDENTITY126.json` and `release126/ARCHIVE_VERIFICATION126.json`.

## Restore the published transport before verification

From this revision directory, reconstruct or verify the original canonical data before running saved-evidence checks:

```bash
python transport126/restore126.py --output replication126/transport-check
python verification126/verify_package126.py --output replication126/package-check
```

The repository transports the large C primary record as ordered fragments of at most 8 MiB. `DATA_TRANSPORT126.json` binds every fragment and the complete original file by byte count, SHA256 and Git blob identity. Restoration verifies those identities; it does not rerun or change the experiment. An extracted referee archive already contains the canonical record, so the default command verifies it without requiring fragment files.

To reconstruct and check the compressed referee archive in a repository checkout, use a fresh receipt directory and request the additional archive transport:

```bash
python transport126/restore126.py --archive --output replication126/archive-transport-check
python verification126/verify_package126.py --require-archive --output replication126/package-with-archive-check
```

The default package verifier checks delivered members without requiring their compressed container. CI explicitly restores both transports and requires the separate container hash. `release126/ARCHIVE_TRANSPORT126.json` and `release126/parts/` describe that container transport. The canonical archive retains the original scientific data and transport utilities, while omitting the redundant repository fragments. The observed HTTP 400 request-body limit and superseded second-archive identity are preserved in `provenance126/package-attempt02/`; that publication transport failure is separate from scientific execution.

## Current article and evidence

- `build/ECTA.pdf` / `ECTA.tex`: current ECTA main article.
- `build/supp.pdf` / `supp.tex`: complete active mathematical proofs.
- `build/appendix.pdf` / `appendix.tex`: development companion, complete cohort results, historical experiments, failures and correction history.
- `build/RESPONSE_TO_REFEREE.pdf` / `RESPONSE_TO_REFEREE.tex`: all 30 controlling requests answered individually; `response_inputs/RESPONSE_MAP126.json` binds original text and current routes.
- `CONTENT_RETENTION126.json` and `.md`: preserved source identities and current routes, extending the unchanged 307-object inherited map.
- `REPRODUCE126.md`: runnable protocols, separate execution identities and limits.
- `SOURCE_PDF_HASHES126.json` and `REFEREE_MANIFEST126.json`: source/PDF and complete delivered-file hashes.
- `provenance126/RESEARCH_WORK_LEDGER126.json`: measured current parent-process cost subtotal, with unknown historical and other unmeasured costs left unknown.

## Executed contributions and their limits

The first source boundary is `769e3eb3ac08beaa7bb6778c1676f15e1f8d6d2b`. All 1,584 primary and 528 timed decisions were executed and checked. Action-aligned direct stopping meets the stronger target in 522/522 cases versus 296/522 for the fused control. Independent original-cost comparisons certify a lower mean cost against that control, with 13 individual direct losses; the mean comparison with warm adaptation remains unresolved. The first implementation's service cost was unfavorable and remains in the evidence.

The second, separately prospective source boundary is `9c6246ecad31acd6a937a2d8ad4710bcabc8c801`. Exact geometry reuse received 3,168 fresh paired primary and 1,056 timed decisions. All 4,224 complete scientific records match the first study. Complete direct-service cost falls 51.3% in the paired study, from 68.849 to 33.512 seconds, but remains 22.2% above equally cached warm adaptation. The optimization is available to every representation.

The complete-support solver executes 888 contrasts on 74 fixed pools, with 48 tighter upper contrasts and 6 tighter regret bounds but no new qualified policy gain. A separate independent checker reconstructs all 33,331 rational cuts. The finite-design fitting audit completes 48 solves and 8 explicitly charged hinge copies, with 227,203 exact assertions. It does not change the deployed actors or acquire fresh economic labels.

All current sufficient neural adoption regions are empty and have conventional identical-policy cost blockers under their respective complete measured costs. Neural-specific superiority, broad control/horizon/innovation scaling, an independent LP implementation and calibrated adoption remain explicit scientific requirements. The research programme and Econometrica objective are retained.

## Provenance

The content-verified complete baseline is R125 at `eda26b02fbfb1e02807bc0cee1c0015d62d59e56`. The actual controlling report is the owner-commissioned R97 advisory at `9723c6cd2cc8b3e071422f3e522d4a843946db63`, report SHA256 `479b28c8800084846336cac078877a01dbbd2bae546d179633a2734401da19b9`. It reviewed its named R97 manuscript, not later revisions, and is not an Econometric Society editorial decision.

The branch census, actual report bodies and immutable trees determine those identities. 35 distinct report bodies and 684 overlapping historical extraction records retain exact source routes; no blanket closure of 684 independent issues is claimed. Protected R123/R124B and other independent studies retain their own protocols, source and execution status. The archive includes a minimal immutable Git object witness for the independent fit source gate; full history remains in the repository.
