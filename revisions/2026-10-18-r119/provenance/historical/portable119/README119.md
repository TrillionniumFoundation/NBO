# Portable historical custody and index material

This directory completes the compact historical evidence package. It preserves
the exact bytes of the original audit programs, input-selection manifests,
launch and parsing records, and the name-bound foundations diagnostic. It does
not execute historical scientific programs, revise past results, or repeat an
economic experiment. The original 359-branch read closure and its limitations
remain in the parent directory.

`PORTABLE_LOCATION_MANIFEST119.json` records the original absolute source path,
original byte count and SHA-256, the published location and encoding, and the
published byte count and SHA-256 for all 62 retained records. Nine entries refer
to an already published identical record one directory above this directory;
those references deliberately avoid duplicate copies. Consequently verification
uses this directory together with its containing `provenance/historical`
directory. Original execution paths inside copied receipts are unchanged. A
new published location does not alter the recorded execution identity.

## Verify without historical execution

From the revision directory:

```bash
python provenance/historical/portable119/verify_extract119.py
```

The helper uses only the Python standard library. It checks every location
record, decompresses encoded records to verify their original byte identity,
checks all archive parts and their concatenated hash, then checks each exact
tar member. It does not import any preserved audit/scientific module and does
not load a model, pickle or object array. `VERIFY_PORTABLE119.json` records the
actual completed verification, including the command, return code and output.
The recorded verification passed all 62 location records and all eight index
members; optional filesystem extraction was not run to create a duplicate
member set.

## Historical index archive

`INDEX_ARCHIVE119.json` binds these eight exact compressed exports that were
advertised by the original `HISTORICAL_coverage.json`:

- Object identities and original commit records.
- Tree edges and source-blob records.
- LaTeX label occurrences.
- Python function entries and economic primitive assignments.
- Historical source, execution, result and failure signatures.

The eight member files contain **51,389,489 bytes** before the additional outer
archive compression. The outer archive is **50,754,663 bytes**, distributed as
seven ordered parts of at most 8 MiB each. Its SHA-256 is
`7361aaf98d32752d07d15c0a6d829501975d69bf51e93ed950915a0698d53db7`.
There is no duplicate full `index119.tar.gz` in the package.

The tar members are ordered by name, use USTAR format, fixed zero timestamps and
owner identifiers, empty owner names and mode `0644`. The outer gzip uses an
empty filename, timestamp zero and compression level nine. The packaging
program and runtime record identify the actual compressor implementation;
member identity is independently checked regardless of filesystem timestamps.

For optional extraction, choose a destination that does not already exist:

```bash
python provenance/historical/portable119/verify_extract119.py --extract-index /tmp/nbo-r119-index
```

The helper permits only the eight declared regular-file basenames. It rejects
duplicates, links, undeclared members, directory traversal, incorrect sizes and
incorrect hashes. It never extracts arbitrary archive paths or overwrites an
existing destination. The original 513-MB SQLite and page rasterizations were
not copied.

## What the records establish

The local raw records retain format-level observations that are absent from a
minimal final hash union. The initial priority-identity read retains its own
version and capped first summaries, even though later complete reads filled
their fields. The initial remote-mirror launch and per-shard summaries retain
their actual command and clock scope. Retry-only records retain the failed
first attempts and their subsequent immutable-object recovery. The R110 JSON
records describe all 5,097 actual member reads and strict parsing; their inputs
remain reconstructible from the separately published generated-evidence parts
and the original Git source export.

The foundations bundle is the original non-preregistered proof diagnostic,
including its source, algebra output, standalone PDF/log and timing receipt.
Its observations are not new economic or competitive-timing results.

The exhaustive source index remains a machine extraction and custody record.
It does not independently prove every historical theorem or rerun every
historical experiment. The preserved historical syntax errors, truncated R118
archive, opaque binaries and incomplete research episodes retain their declared
status. The portable packaging and verification do not assert remote CI success.
