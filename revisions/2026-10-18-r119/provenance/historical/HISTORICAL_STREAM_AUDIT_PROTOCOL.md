# Historical streaming custody audit for R119

## Authority, identity, and actual execution status

This is a read-audit of immutable historical artifacts, separate from every scientific experiment and every timing campaign. It does not execute historical Python, import historical packages, load Torch models, unpickle arrays, change a parameter, or regenerate a historical result. A JSON field saying `success` is reported as a retained assertion; it is not proof that the associated experiment succeeded. Git blob SHA1 and independently computed SHA256 identify the exact bytes that were read.

The input universe comes from all 359 originally inventoried GitHub branch refs, their 301 distinct heads, and every commit ancestor in the captured Git object graph. The script's manifest generator retains objects that appeared in any historical ancestor, including files deleted from later branch tips. Five new R119-only missing Git-object references are excluded from the historical missing count; their worktree bytes were separately matched to their Git hashes. No native historical TeX, Python, or Markdown blob was missing from the offline science index.

The initial missing history contains 1,239 JSON blobs. Its 19 strict source/evidence identity records total 50,622,588 bytes by immutable GitHub tree metadata. All 19 were actually downloaded, Git/SHA256 verified, and fully walked by the streaming JSON parser between 2026-10-18 06:00:36 UTC and 06:01:23 UTC, using the first audited script identity recorded in their raw logs. Peak measured parser RSS was 26,980 KiB. Their outputs are under `HISTORICAL_stream_identity_run`; the first deliberately limited one-object invocation returned exit 2 because 18 selected objects remained, then a resumed invocation completed those 18. The retained summary and individual records distinguish these invocations. Three very wide identity maps exceeded the compact in-record field-count dictionary cap; their full bytes and complete syntax walks were verified and all matched source/hash evidence was retained. The subsequent script revision additionally emits every map-key occurrence into the compressed event stream; it must carry its own source hash and must not be retroactively attributed to the first run.

The 15 small parser diagnostics in `HISTORICAL_stream_parser_validation.json` are artificial custody tests, not economic experiments. They check exact large integers and Decimal values, distinct dotted keys and array-index paths, duplicate-key event order, empty containers, JSON sequences, invalid NaN/UTF8/truncated/extra-root inputs, multiline CSV, NPY byte lengths and finite/nonfinite counts, complete NPZ member reads and CRC checks, object-array opacity, expansion limits, and Git LFS pointers. These diagnostics do not certify every possible archive/parser input.

## Inputs and staged coverage

`HISTORICAL_stream_identity_priority.jsonl` selects the 19 identity records first. `HISTORICAL_stream_missing_json.jsonl` selects all 1,239 initially missing historical JSON blobs. `HISTORICAL_stream_all_missing.jsonl` selects all 10,358 initially missing historical Git blobs, including the separately reported binary/opaque formats. `HISTORICAL_stream_manifest.jsonl` selects the full historical native-science and raw-data scope, including objects already available locally. Every row carries the blob SHA, a real containing commit, representative path, suffix aliases, initial local availability, and a known byte size when available. The full offline index retains all alias/commit membership, so the representative path is not a claim that the file appeared only once.

Use immutable `raw.githubusercontent.com/{repository}/{commit}/{path}` downloads for remote CI. There is no per-object Git API metadata query. An optional `github_blob` transport is available for the small source-identity phase. Both transports verify the returned content against the known Git blob hash; incorrect raw paths, HTML errors, LFS pointers, and representation mismatches cannot silently become valid scientific data. Authentication is sent only to the requested GitHub content/API host, and cross-host redirects strip it. Tokens are never printed or retained.

Already available local history should be audited with `--transport auto --local-repo PATH` or `--transport local`; `GIT_NO_LAZY_FETCH=1` applies to all subprocess Git reads. This avoids re-downloading data that are already present. The CI template selects only initially missing objects, uses 16 deterministic hash shards, permits four concurrent jobs, grants `contents: read`, and uploads both successful and failed records. CI makes no author commit or remote push. A workflow dispatch or green job must never be substituted for actual content/parse results.

## Bounded resources and retained evidence

The default raw download cap is 128 MiB per object. A 64 KiB buffer streams the response into one temporary file while computing SHA256; a second bounded pass computes the Git blob hash including its exact size header. The temporary directory is discarded after parsing. No collection of historical payloads accumulates in scratch.

Each semantic parser runs in a separate process with a 512 MiB address-space limit, 300 CPU-second limit, 360 wall-second limit, and 128 MiB output-file limit. The orchestration process retains one manifest row and compact per-object metadata at a time. Compressed outputs persist; raw downloads do not. The NPY header is limited to 64 KiB, dimension count to 64, dtype nesting to 32, ZIP central directory to 16 MiB, JSON nesting to 256, CSV row bytes to 16 MiB, and archive expansion to 1 GiB. Any limit is a recorded unresolved semantic scope item, not a reason to drop the object from the denominator. Zip64 directories currently remain an explicit semantic limitation even after full raw-byte verification.

JSON uses pinned `ijson==3.4.0.post0`, `basic_parse`, `use_float=False`, and no comment/NaN extension. Arrays are visited without constructing a whole JSON document. Exact integers and Decimal strings are retained. The current script emits every map-key occurrence plus selected status/source/economic/hash scalar records, with exact array indices and distinct literal dotted keys. The compact field-frequency dictionary is capped at 10,000 names; this cap does not stop the syntax walk. Scalar display prefixes are capped and carry length/hash information when truncated. Matched-event retention is capped at 500,000 per object and has explicit total/retained counters. Neither a prefix nor a limited dictionary is described as the complete original object. Duplicate JSON keys remain separate SAX events; the auditor does not silently resolve them by keeping the last value.

NPZ is processed as a ZIP container without extracting paths. Every supported member is decompressed in blocks, SHA256 hashed, and CRC checked. NPY shape, dtype, byte order, layout, header hash, data length and data hash are recorded. Simple numeric dtypes are scanned for count, finite/nonfinite values, and minimum/maximum. Structured/complex/string dtypes can have complete data hashes and size checks while lacking those simple scalar statistics. Object arrays remain opaque and are never unpickled. Torch/model/PDF/image blobs are raw-byte identity checks only. Gzip payloads are streamed and hashed but are not recursively interpreted as arbitrary archives. These scope distinctions remain in each record.

## Commands and reporting

Install the pinned dependency, then run the current small parser diagnostics. For the first remote phase, run:

```sh
python HISTORICAL_stream_audit.py run \
  --manifest HISTORICAL_stream_missing_json.jsonl \
  --output read-audit-json \
  --transport raw_commit
```

For CI, supply `--shard-count 16 --shard-index 0` through `15`. The selected denominator is the manifest subset assigned to that shard; `--max-objects` preserves unattempted rows in the denominator and yields a nonzero exit code. `--resume` appends records and skips previously fully read/parsed rows. Records preserve errors from preceding attempts. Merging shards requires checking the exact union of selected Git SHAs against the input manifest, checking script/manifest identities, and retaining every unresolved object; summing green job counts alone is insufficient.

The authoritative reporting categories are: bytes fully read, Git identity verified, supported semantics completely walked, opaque payloads hashed, fields/signatures retained or truncated, and unresolved transport/identity/parse/limit errors. These describe data custody and reading. Independent theorem verification, independent economic result recomputation, provenance of historical runtime logs, and neural adoption remain separate scientific claims.

## Primary format references

GitHub, REST Git blobs, documents `application/vnd.github.raw+json`, `contents: read`, and the 100 MB blob-endpoint limit: <https://docs.github.com/en/rest/git/blobs#get-a-blob> (read 2026-10-18). NumPy's NPY/NPZ format documentation specifies ZIP-contained NPY files, headers, dtype/shape and object-pickle payloads: <https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html> (read 2026-10-18). The pinned parser's own release documentation specifies event interfaces, exact integer/Decimal defaults and multiple-value parsing: <https://pypi.org/project/ijson/3.4.0.post0/> (read 2026-10-18). These are format references, not evidence for an NBO scientific result.
