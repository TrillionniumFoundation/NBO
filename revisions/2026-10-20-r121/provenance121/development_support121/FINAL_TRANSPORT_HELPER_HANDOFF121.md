# Final R121 native classification and transport

`verification121/prepare_transport121.py` is new unfrozen infrastructure. It
does not replace the previously published packer or assembler, and imports no
scientific module. Its original source was checked using tiny synthetic Git
fixtures only. No actual R121 file census, scientific-evidence hash, or final
transport has been executed by this handoff.

## Exact commands after the independent run and root authorization

Set `NBO121_PARENT` to the complete immutable new parent R that root has
actually verified remotely and checked out locally. It is not hard-coded to D.
The helper requires this parent to be an ancestor of actual local HEAD.

```bash
python revisions/2026-10-20-r121/verification121/prepare_transport121.py classify \
  --repository /workspace/scratch/913249553838/NBO \
  --base-commit "$NBO121_PARENT" \
  --output-dir /workspace/scratch/913249553838/audit121/transport121/classify-final-attempt01
```

Outputs are:

- `NATIVE_CLASSIFICATION121.json`: every local native file or missing parent
  path, identities for authored/evidence files, dispositions and blockers.
- `TRANSPORT_INCLUDE121.json`: explicit full identities for all newly added
  regular non-executable native files eligible for byte assembly.
- `DIRECT_WRITES121.json`: changed tracked text/binary, new executables and
  new transport control paths which require direct Git writes.
- `PREPARATION121.json`: the actual parent/head, helper, metadata commands,
  status, elapsed time and counts. Missing tracked data returns exit 2.

Before final packing, review any direct writes and blockers. Only absent or
already byte-identical native paths can be assembled by the current workflow.
Publish direct writes before or in T. Preserve the modes specified in the
classification, including executable files. The root workflow itself is
outside native R121 and requires a separate direct Git write if it changed.

```bash
python revisions/2026-10-20-r121/verification121/prepare_transport121.py pack \
  --repository /workspace/scratch/913249553838/NBO \
  --base-commit "$NBO121_PARENT" \
  --bundle-id author-source01 \
  --compression-policy mixed \
  --include-list /workspace/scratch/913249553838/audit121/transport121/classify-final-attempt01/TRANSPORT_INCLUDE121.json \
  --output-dir /workspace/scratch/913249553838/audit121/transport121/pack-author-source01
```

All outputs remain outside native R121. `UPLOAD_PLAN121.json` gives the exact
repository destination for `bundle/REQUEST121.json` and each
`bundle/payload.zip.partNNNN`. The archive is `payload.zip`. The request contains
full repository-relative native member names, SHA256, Git blobs and byte
counts. Member order, modes and time metadata are fixed. Default `mixed`
compression matches the original helper: `.gz`, `.png`, `.pdf` and `.zip`
members are stored, while other files use deflate level 6. The alternative
`--compression-policy store` stores every member. The preparation receipt
records Python and compiled/runtime zlib versions; mixed compressed bytes are
deterministic under that actual implementation. Actual archive member
bytes/CRCs and physical parts are read back before the request is written.

`--include-list` is repeatable and accepts a JSON array, a JSON object with
`files` or `paths`, or one POSIX file path per text line. JSON records may
include exact byte/hash/mode requirements. `--include` adds individual files.
Paths can be native-relative or full repository-relative; directories are not
silently expanded. The explicit list cannot contain transport controls,
deferred S/P controls, the final container itself, or generated caches.

## Conservative exclusions

Tracked files are never silently omitted. Historical traces, failed attempts,
build logs, `.fls`, generated bibliography/auxiliary inputs, existing transport
parts, and archived earlier failed containers remain in the native census.
No broad extension or results-directory exclusion is applied.

Only untracked interpreter/tool cache directories are automatically excluded.
Other temporary files require `--transient-exclusions FILE` with this schema:

```json
{
  "kind": "nbo-r121-transient-exclusions-v1",
  "files": [
    {
      "path": "local-generated.tmp",
      "reason": "A generated non-evidence temporary file, retained locally.",
      "not_authored_or_scientific_evidence": true
    }
  ]
}
```

The helper rejects tracked paths, arbitrary authored filenames and sensitive
results/provenance/trace/failure paths in this exclusion list. It retains the
actual excluded files and records their paths and reasons.

The exact root final ZIP, its ordered root parts and its root package manifest
are separated to avoid their own container recursion. Earlier containers under
provenance or development directories remain evidence. Source/evidence and
ready controls are deferred to S; source/PDF and source-inventory controls are
deferred to P. They are recorded as deferred, not silently discarded.

If a previous unpublished transport REQUEST is present in the direct-write
list, preserve it without adding it alongside the current T's new REQUEST:
the assembler intentionally requires exactly one newly added REQUEST in T.
Prior request files already committed at the selected parent cause no issue.

## Publication helper requirements

The source-only review of `publication121.py` found no mandatory change for
the agreed sequence:

1. Preserve the original local strict source build and its recorders. `bind`
   parses recorder PWD/INPUT paths and cannot substitute a remote CI runner's
   absolute paths for the local build snapshot referenced by SOURCE_READY.
2. S precedes `SOURCE_PDF_MANIFEST121.json` and
   `AUTHOR_SOURCE_INVENTORY121.json`; `bind` writes them for later P.
3. P preserves every S blob and mode, including S's evidence manifest and
   ready marker. Do not expand those controls to include P's additions.
4. Pass repeated `pack --required-path` arguments for the actual final-source
   CI result and actual remote workflow/readback records. Byte packaging alone
   does not infer CI evidence or success.
5. `bind --expected-source-tree` means the repository root tree SHA.
6. Ordinary physical split mode supports `verify --parts-dir`. A
   `--no-split` manifest followed by virtual `describe-parts` still has no
   physical parts declared; reconstruct and verify that ZIP with `--archive`.
7. Supply `verify --source-commit`, `--publication-commit` and
   `--expected-manifest-sha256` to bind the caller-selected actual S/P and
   published manifest, since these optional arguments are not inferred from
   the intended remote publication.
