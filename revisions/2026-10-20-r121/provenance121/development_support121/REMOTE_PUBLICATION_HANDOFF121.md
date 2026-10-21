# R121 remote package delivery handoff

The implementation is ready for inclusion in author source S. No actual S/P/Q/V package or GitHub publication workflow has been executed by this agent. The original scientific programs and frozen F files are unchanged. All tests cited below are bounded infrastructure fixtures, with no original scientific inputs.

## Files to include before S

- `revisions/2026-10-20-r121/verification121/remote_publish121.py`
- `revisions/2026-10-20-r121/verification121/remote_verify121.py`
- `.github/workflows/nbo-r121-publication.yml`
- Updated `revisions/2026-10-20-r121/verification121/ci121.py`
- Updated `.github/workflows/nbo-r121-author-package.yml`

The workflows are outside the native R121 transport prefix and need the direct GitHub text-write route. Any existing tracked helper changed relative to the actual transport parent also needs a direct text write in T; the assembly helper may add only absent native files or accept byte-identical existing files.

The source CI now explicitly binds both native TeX result copies to the original report's stable outputs and to the fresh deterministic replay. Both copies must appear in the complete S manifest. It writes `NATIVE_MANUSCRIPT_TABLE_LINKAGE121.json`. This is a manuscript-table byte link, without any new economics or change to a result.

## Commit boundaries and request

1. S contains the final manuscript, all complete original evidence, all required helpers and both workflows. Run the real author-source CI at S and preserve its actual artifacts and API readback.
2. Run the unchanged `publication121.py bind` locally against the original strict source build receipt at S. P retains every S byte/mode and adds the exact binding and actual source-CI records.
3. Q is a single direct child of P, adding **only** `revisions/2026-10-20-r121/delivery121/PACKAGE_REQUEST121.json`. Create Q through the GitHub plugin, so this request push triggers the publication workflow.
4. The Q workflow checks the actual S CI through the GitHub API, packs complete P outside the checkout, verifies every ZIP member, describes virtual 8 MiB ranges, and uploads the complete ZIP and preparation evidence as an artifact.
5. Only after the actual artifact is uploaded and checked does the helper write exact part Git objects, stage additive delivery files through the index and push V. It checks remote Q immediately before the ordinary non-force push. An intervening divergent remote update makes that push fail; all resulting logs remain available.

Request schema, with actual immutable identities and actual native-relative P record paths:

```json
{
  "kind": "nbo-r121-remote-publication-request-v1",
  "revision_prefix": "revisions/2026-10-20-r121",
  "author_source_commit": "S_FULL_40_HEX",
  "publication_commit": "P_FULL_40_HEX",
  "source_ci_run_id": 123456789,
  "required_records": {
    "author_source_ci_result": "ACTUAL_NATIVE_CI_RESULT_PATH.json",
    "author_source_ci_remote_readback": "ACTUAL_NATIVE_REMOTE_READBACK_PATH.json"
  },
  "required_publication_paths": []
}
```

`required_publication_paths` can list additional exact native-relative P files that the packer must retain. The two required records are always passed to `publication121.py pack --required-path`.

The saved actual CI result must identify S and have `status=passed_final_author_source_package`, `exit_code=0`, `final_author_source_ci=true`, `complete_author_package_gate=true`, `strict_build_and_all_four_pdf_hashes_verified=true`, and `original_economic_execution_performed=false`.

The saved remote readback must have these top-level fields:

```json
{
  "source_commit": "S_FULL_40_HEX",
  "run_id": 123456789,
  "head_sha": "S_FULL_40_HEX",
  "status": "completed",
  "conclusion": "success",
  "workflow_path": ".github/workflows/nbo-r121-author-package.yml"
}
```

Include the actual artifact IDs/digests, timestamps and other observed run metadata in that record as appropriate. Preparation independently queries that same source run and checks S, workflow path, branch and completed/success state.

## Actual workflow commands

The workflow supplies actual Actions environment values, including `GITHUB_RUN_ID`, `GITHUB_RUN_ATTEMPT`, `GITHUB_REPOSITORY`, `GITHUB_REF`, `GITHUB_SHA`, and a contents-write/actions-read `GITHUB_TOKEN`.

```bash
python revisions/2026-10-20-r121/verification121/remote_publish121.py prepare \
  --repository "$GITHUB_WORKSPACE" \
  --request-commit "$GITHUB_SHA" \
  --work-dir "$RUNNER_TEMP/nbo-r121-publication"
```

After the complete artifact upload, finalize receives the upload action's actual output fields:

```bash
python revisions/2026-10-20-r121/verification121/remote_publish121.py finalize \
  --repository "$GITHUB_WORKSPACE" \
  --request-commit "$GITHUB_SHA" \
  --work-dir "$RUNNER_TEMP/nbo-r121-publication" \
  --artifact-id "$ACTUAL_PACKAGE_ARTIFACT_ID" \
  --artifact-digest "$ACTUAL_PACKAGE_ARTIFACT_DIGEST" \
  --artifact-url "$ACTUAL_PACKAGE_ARTIFACT_URL"
```

Package artifact name: `nbo-r121-referee-ready-Q-attemptN`.

Final diagnostics artifact name: `nbo-r121-publication-diagnostics-Q-attemptN`.

Source-CI artifact name: `nbo-r121-author-package-S-attemptN`.

Here Q/S are the complete actual hashes and N is the actual Actions run attempt. This preserves distinct failure attempts without overwriting their artifacts. Both publication uploads use compression level zero. The final diagnostics artifact uses `if: always()` and contains only small records/logs, avoiding a second whole-ZIP upload.

No lazy-fetch prohibition is inherited by partial checkout. The helpers prohibit lazy fetching for their later verification subprocesses, after checkout has materialized the selected native files.

## V contents and scope

V preserves all P and Q files and adds only the exact delivery set:

- Root-native `REFEREE_READY_PACKAGE121.json` and `VIRTUAL_ZIP_CHUNKS121.json`.
- Root-native `referee-ready121.zip.part0000`, etc., each at most 8 MiB. The Git objects are written directly from archive ranges; no physical duplicate part files are created on the runner.
- `delivery121/receipts/` containing preparation, exact part-object and artifact metadata, pack/verify/describe receipts, completed preparation logs and a finite completed-finalization log snapshot.

The full ZIP is retained in the Actions artifact, not committed as one large Git file. The package manifest remains the original no-split manifest, with `split_performed=false` and `parts=[]`. The separate virtual descriptor describes the parts actually added in V. The archive is the complete P native tree; Q request and V delivery outputs are outside the P archive to avoid self-recursion.

`DELIVERY_PRECOMMIT121.json` expressly does not claim that commit/push has already succeeded and cannot contain its future V hash. Actual post-push `PUSH_RESULT121.json`, all later index/commit/push logs and remote head readback are in the final diagnostics artifact. The parent/root must verify actual V, its Q parent, additive tree diff and the actual workflow conclusion independently.

## Root verification without a whole local ZIP

After independently observing V and the two small root-native metadata files and their SHA256 values:

```bash
python verification121/remote_verify121.py \
  --repository TrillionniumFoundation/NBO \
  --delivery-commit V_FULL_40_HEX \
  --source-commit S_FULL_40_HEX \
  --publication-commit P_FULL_40_HEX \
  --expected-manifest-sha256 OBSERVED_PACKAGE_SHA256 \
  --expected-descriptor-sha256 OBSERVED_DESCRIPTOR_SHA256 \
  --cache-mib 32 \
  --output-dir /fresh/small/remote-verification-staging
```

The caller-selected hashes are required. This helper fetches immutable raw GitHub paths at V, verifies every part on every cache miss, hashes the complete archive in order, and streams every member through CRC, content, mode, name and embedded S/P checks. Its part cache is at most 32 MiB; it never writes a full archive or extracted member. It retains request, part, member, complete archive and failure receipts.

Its success status `immutable_remote_delivery_bytes_verified` is a byte-verification result. It does not infer source CI success, scientific correctness, remote Git ancestry or equality with remote Git trees. These have separate evidence.

`publication121.py verify --parts-dir` is for the earlier physically split manifest schema. It must not be used directly with this no-split manifest and virtual descriptor. Use the remote verifier above, or explicitly reassemble the ZIP and pass `--archive` to the unchanged complete ZIP verifier.

## Completed bounded evidence

- `remote_publication_synthetic_attempt01/RESULT121.json`: nine checks, 2.043 seconds, 174-byte synthetic ZIP, local bare Git origin. The pack/verify/describe subprocess was an explicit interface stub; actual strict scientific/source/build validation is not claimed. The unchanged publisher executed its actual ancestry, request, API-binding comparison, exact part-object, additive-index, commit, ordinary local-bare push and remote-ref checks. All fixture commands and failure prefixes remain retained.
- `remote_verifier_synthetic_attempt01/RESULT121.json`: eight checks, 0.055 seconds, 4,205-byte in-memory ZIP and fake HTTP opener. Complete byte-reader pipeline, range coverage, corruption rejection, caller S/hash rejection, chunk offsets and bounded LRU behavior were checked.
- `native_table_linkage_synthetic_attempt01/RESULT121.json`: five positive/negative linkage checks, 0.00193 seconds, tiny invented table bytes.
- `source_edits121/CI_NATIVE_TABLE_LINKAGE121.json`, with the prior CI helper snapshot.
- `source_edits121/AUTHOR_CI_ARTIFACT_ATTEMPT121.json`, with the prior author-CI workflow snapshot.
- `REMOTE_PUBLICATION_SOURCE_READY121.json`: initial AST/source/workflow interface check receipt before the separately recorded author-CI artifact-name adjustment.
- `REMOTE_PUBLICATION_HANDOFF121.json`: final file identities and the evidence inventory for this handoff.

All paths in this section are relative to `audit121/experiments/`. The complete fixture driver sources are `remote_publication_synthetic121.py` and `remote_verifier_synthetic121.py`; the Git and output receipts remain in their named attempt directories. No actual scientific data, partial outcomes, remote package, source build, source CI or GitHub push was executed in these bounded tests.
