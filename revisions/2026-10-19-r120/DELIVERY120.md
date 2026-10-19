# R120 referee-ready delivery

The exact author source is **39a20bf1fe011175857811bf67bacd788ae80c52** (S).
The exact PDF/publication snapshot is **cc58ec9613044f97aa1ae5c8d60ec1c3c0021dcd** (P).
The additive commit introducing this file is delivery V. V retains every S/P
file and adds the package and these transport records.

The complete ZIP contains **1,099 files**, with **247,958,898 uncompressed
payload bytes**. Its exact container identity is:

| Field | Value |
|---|---|
| Filename | `referee-ready120.zip` |
| ZIP bytes | 248,168,182 |
| SHA256 | `26cf56c4839853b452def1c64740cb78c04be08bde1e91e2efe7038239bb14c3` |
| Git transport parts | 30, at most 8 MiB each |
| Author-source native files retained | 1,040 |
| Publication files added | 59 |

Every ZIP member was read to EOF and checked for its name, mode, byte length,
ZIP CRC, SHA256 and Git blob identity. All 30 actual GitHub blob-upload results
match the precomputed ordered byte ranges. The complete source/PDF binding,
package inventory and transport receipts are in `SOURCE_PDF_MANIFEST120.json`,
`REFEREE_READY_PACKAGE120.json`, `VIRTUAL_ZIP_CHUNKS120.json`, `DELIVERY120.json`
and `provenance/delivery120/`.

The range descriptor's original flags say that it was created before remote
upload. Those dated facts remain unchanged. The later actual upload receipt
`provenance/delivery120/PACKAGE_BLOB_UPLOAD120.json` records all 30 successful
remote operations; this distinction preserves the real operation sequence.

## Actual CI and readable documents

[GitHub Actions run 39240515942](https://github.com/TrillionniumFoundation/NBO/actions/runs/39240515942)
completed successfully on S. The downloaded artifact contains 87 verified
members; all four CI PDFs are byte-identical to the final native PDFs. Read:

- `build/ECTA.pdf`: current English main article, 42 pages.
- `build/supp.pdf`: full technical supplement, 99 pages.
- `build/RESPONSE_TO_REFEREE.pdf`: current point response, 27 pages.
- `build/appendix.pdf`: complete development companion, 794 pages.

The exact actual CI artifact, logs, original audit/build receipts and download
verification remain under `provenance/ci120/source-run-39240515942/`. S contains
the successful scientific-source gate. P and V only add publication material
and skip duplicate CI; success is not attributed to a different HEAD.

## Reassemble the Git transport

In a checkout of delivery V, change into `revisions/2026-10-19-r120`. The
following reader command creates an exclusive new ZIP and checks every ordered
part and the concatenated bytes. It does not run or alter any experiment.

```bash
python - <<'PY'
from pathlib import Path
import hashlib
import json

manifest = json.loads(Path('REFEREE_READY_PACKAGE120.json').read_text())
descriptor = json.loads(Path('VIRTUAL_ZIP_CHUNKS120.json').read_text())
output = Path('referee-ready120.reassembled.zip')
total = 0
whole = hashlib.sha256()
with output.open('xb') as target:
    for item in descriptor['chunks']:
        assert item['offset'] == total
        data = Path(item['path']).read_bytes()
        assert len(data) == item['bytes']
        assert hashlib.sha256(data).hexdigest() == item['sha256']
        header = b'blob ' + str(len(data)).encode() + b'\0'
        assert hashlib.sha1(header + data).hexdigest() == item['git_blob']
        target.write(data)
        whole.update(data)
        total += len(data)
assert total == manifest['bytes']
assert whole.hexdigest() == manifest['sha256']
print(output, total, whole.hexdigest())
PY
```

Then verify the ZIP's complete inventory and source/publication identities with
the retained package verifier and a fresh output directory:

```bash
python verification120/publication120.py verify \
  --manifest REFEREE_READY_PACKAGE120.json \
  --archive referee-ready120.reassembled.zip \
  --source-commit 39a20bf1fe011175857811bf67bacd788ae80c52 \
  --publication-commit cc58ec9613044f97aa1ae5c8d60ec1c3c0021dcd \
  --output-dir /tmp/nbo-r120-package-reader-verification
```

The package manifest intentionally has `parts: []`, because its original ZIP
was created with `--no-split`; use `--archive` for verification. The separate
range descriptor binds the uploaded transport. The ZIP root is the native
revision directory. Commit-ancestry verification requires a Git checkout with
the referenced metadata. `REPRODUCE120.md` separately specifies saved-record
replay and a genuinely new economic run, preserving independent-protocol
boundaries.

## Scope of the completed revision

The package preserves the original NBO research identity, exact current raw
records, all report routes, failed attempts, conventional winners and unresolved
neural adoption regions. It documents new mathematical policy-improvement
results and actual original-objective gains. It also retains the paired
service's unresolved incremental cell mean advantage and adverse timing, the
equal-feature ReLU/hinge policy identities, and the outstanding questions of
paid computational competitiveness, action-aware learning and an independent
neural contribution. Publication, CI and archive integrity establish none of
those unproved claims, and do not constitute an Econometric Society decision.
