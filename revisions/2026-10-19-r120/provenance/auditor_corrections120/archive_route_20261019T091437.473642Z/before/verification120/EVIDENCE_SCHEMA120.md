# R120 saved-evidence manifest and bounded CI

`EVIDENCE_MANIFEST120.json` is created only after the selected acquisition,
sample, primary/timing, independent validation, inference and reporting attempts
have actually completed. Its creation is a byte inventory operation; it is not
an experimental result or a successful verification/CI claim.

## Immutable scientific barriers

| Boundary | Actual commit |
|---|---|
| Scientific source F | `369d02724cf12ae0e54390b4e7b5f894f703892e` |
| Actual actors M | `1c5e4dc7e04c108fe698d4c247a144b625db301c` |
| Original sampled states D | `aebc7a0175c0729b9ff5e833a7facc1ed5c4c2fd` |
| Reporting specification | `594d9336d89bedfd360e942146ae490e0fabd3a0` |

The frozen source census is 157 files and 1,206,453 bytes. The auditor checks
every file's SHA256 and Git blob, the distinct direct parent sequence F→M→D→R,
actual actor/sample artifact manifests, retained remote publication receipts,
and external launch identities. The reporting-publication receipt was written
after primary launch. Its reported operation order and the actual launch HEAD
are checked separately; neither its later recording time nor a Git committer
date is represented as an independently observed prelaunch push timestamp.

## Manifest V1

The schema identifier is `NBO_R120_EVIDENCE_MANIFEST_V1`.

Every file identity is the exact four-field record
`{path, bytes, sha256, git_blob}`. Paths are canonical relative POSIX paths.
`git_blob` is SHA1 of the Git blob header followed by the actual bytes. Files
may not be symlinks. A reference to a file's SHA is not a substitute for
retaining the original file or a lossless archive containing it.

- `commits` contains F, M, D and the reporting-specification commit.
- `layout` names the six actual result directories: acquisition, states,
  primary, independent, statistics and reporting. The selected attempts must
  have actual successful exit receipts; previous failed attempts remain in the
  full inventory.
- `retained_roots` is exactly `['results120']`. `files` inventories every regular
  file below this root, including all successful and failed raw/launcher/log
  records, rather than only the selected final tables. `file_count` and
  `total_payload_bytes` must match this census. No exclusion list is supported.
- `publication_receipts` and `external_launch_receipts` bind the actual source,
  acquisition, sample, reporting and execution chronology. Optional reporter
  launcher metadata remains separate from its successful internal execution.
- `tool_sources`, `repository_tool_sources`, and `support_files` bind the
  auditor, reporter/statistics source, manifest builder, workflow, build driver,
  requirements and exact original advisory reports/maps. They are packaging
  derivatives and are not falsely represented as part of frozen scientific F.
- `expected_census` fixes 16 actors; 64 two-coordinate states from 640 bytes;
  4,096 primary decisions; three descriptive timing processes and 6,144 timing
  decisions; all 4,096 independent comparisons; 48 population groups and 192
  fixed threshold records; and all 992 group-pair contrasts. The unique returned
  policy count is measured from the complete records, not prespecified after
  observing it.
- `report_replay_contract` uses the actual reporter's `stable_replay_files`.
  The present specification has 34 scientific table files and two TeX snippets.
  Actual replay clocks/environment/paths and research-ledger derivatives remain
  retained with separate identities; excluding them from byte equality does not
  exclude them from custody.
- `report_ledger_paths` records any additional native ledger inputs supplied to
  the actual reporter. They must be retained and are passed unchanged to replay.
- `archives` is a list of disjoint transport bundles described below. `archive`
  is null for this multiple-archive representation. A legacy single archive
  remains accepted only when `archives` is empty.

## Lossless archive checkpoints

Each bundle is `{files, archive, descriptor}`. `files` is an exact subset of the
full manifest's four-field identities; subsets cannot overlap. The optional
`descriptor` is the four-field identity of an earlier separately published
checkpoint descriptor. Reusing a primary checkpoint does not recompress or
replace its bytes.

The archive object is:

```json
{
  "kind": "concatenated-tar-gzip-parts",
  "sha256": "SHA256 of the ordered compressed parts concatenated",
  "compressed_bytes": 0,
  "uncompressed_payload_bytes": 0,
  "member_count": 0,
  "parts": [{"path": "evidence120/example.tar.gz.part0000", "bytes": 0,
             "sha256": "part SHA256", "git_blob": "part Git blob SHA1"}]
}
```

The zeros and digest labels above illustrate field types, not actual evidence.
The builder writes normalized regular-file tar members into a gzip stream with
timestamp zero and exclusive sequential parts. The verifier stream-checks each
part, concatenated bytes, member census, member bytes and both digests. It does
not need a second concatenated archive file. If complete loose evidence is
already present, it verifies archives without extraction. A fresh audit copy is
materialized only when raw files are missing, as in sparse CI. Existing raw or
archive files are never overwritten or removed.

The same `make_archive` helper can checkpoint completed primary evidence before
independent validation finishes. A primary-only descriptor is **not** a complete
R120 evidence manifest and carries no completion claim for later stages.

## Creating the final manifest

After actual completion, run from the revision directory:

```bash
python verification120/build_evidence_manifest120.py \
  --output EVIDENCE_MANIFEST120.json \
  --existing-archive evidence120/PRIMARY_CHECKPOINT120.json \
  --archive-prefix evidence120/remaining120 \
  --part-bytes 8388608
```

Use the actual descriptor path, if a primary checkpoint exists; otherwise omit
`--existing-archive`. `--archive-prefix` archives all remaining result files.
Actual stage paths can be supplied with `--acquisition`, `--states`, `--primary`,
`--independent`, `--statistics`, and `--reporting`; matching external launch paths
have `--launch-<stage>` options. `--launch-reporting` is optional. Additional
ledger inputs use repeatable `--report-ledger` arguments.

The builder fails if its output already exists. Retain a failed or superseded
manifest/attempt and use a new name for a new inventory. Changing a bound
packaging source requires a new manifest; it does not authorize changing F, M,
D or any scientific result. Root-owned publication records subsequently bind
the final committed source, actual build, PDFs, archive and remote CI receipt.

## Bounded verification

```bash
python verification120/audit_evidence120.py \
  --manifest EVIDENCE_MANIFEST120.json \
  --output ci120/evidence-audit \
  --replay-statistics --replay-reporting \
  --require-current-commit --require-final-author
python build120.py --receipt-dir ci120/build-receipts
```

The audit output is exclusive. Its first receipt and all partial/replay/failure
evidence remain if a gate fails. A successful `AUDIT_EVIDENCE120.json` means:

1. All original raw and archive bytes, scientific barrier identities and full
   observation/candidate/event counts passed their stored-record checks.
2. Every one of the 6,144 timing actions was compared with its own primary
   action. Mismatches are retained and constrain price/value matching; they are
   never replaced by a preferred repeat.
3. All saved independent terminal witnesses, full-support aggregation,
   Lagrange-support arithmetic, 4,096 policy comparisons, original all-action
   lower bounds and gain/regret/action-error fields were reaggregated exactly.
   This check is conditional on the saved independent primitive values and
   gradients. It does **not** import or rerun the independent economic solver or
   independently certify every narrower production endpoint.
4. The 48 population groups and 192 fixed exact binomial brackets, bounded-mean
   intervals and staircase lower bounds passed exact arithmetic checks. If
   requested, the same frozen statistical source was replayed from the saved
   observations and compared byte-for-byte.
5. If requested, the post-freeze reporter regenerated all declared scientific
   tables/snippets from saved evidence with exact byte equality. Its clocks and
   derivative metadata remain separately reported.
6. All 35 exact original report bodies, 1,049 inherited author routes and 30
   current controlling R97 point responses retain their source/text/proof
   bindings. Overlapping parent routes are not counted as independent issues;
   neither routing nor audit success asserts blanket scientific closure.

The workflow calls neither `campaign120.py` nor `independent120.py`, draws no
entropy, trains no model, changes no experimental action, repeats no scientific
timing, and performs no new model selection. The four-document PDF build is a
separate actual execution. Queued or running CI has no successful conclusion;
publication must use actual dated run/job/artifact receipts.
