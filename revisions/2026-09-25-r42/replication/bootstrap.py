#!/usr/bin/env python3
"""Materialize the R42 source bundle, verifying its identity before any writes.

Transport files are retained for reproducibility; expanded source files are
committed by the publication job. Only the new R42 subtree may be written.
"""
import base64
import hashlib
import json
import lzma
from pathlib import Path, PurePosixPath

BASE = Path(__file__).resolve().parents[1]
EXPECTED = '844078828340b88b08ee65e23a8742870300b9372978006557a67e14760cd599'
encoded = ''.join((BASE / 'transport' / f'source.part{i}.b64').read_text().strip() for i in range(3))
packed = base64.b64decode(encoded, validate=True)
actual = hashlib.sha256(packed).hexdigest()
if actual != EXPECTED:
    raise RuntimeError(f'Source transport checksum mismatch: {actual}')
files = json.loads(lzma.decompress(packed).decode('utf-8'))
if not isinstance(files, dict) or len(files) != 15:
    raise RuntimeError('Unexpected source manifest')
for name, text in files.items():
    rel = PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts or not isinstance(text, str):
        raise RuntimeError(f'Unsafe source entry: {name}')
    if not (name.startswith('paper/') or name.startswith('replication/') or name in ('README.md', 'results/inherited_r41_finest.json')):
        raise RuntimeError(f'Unexpected source destination: {name}')
for name, text in files.items():
    path = BASE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
print(json.dumps({'passed': True, 'sha256': actual, 'expanded_source_files': len(files)}))
