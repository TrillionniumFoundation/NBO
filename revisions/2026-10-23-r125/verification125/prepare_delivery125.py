"""Describe a closed author-package snapshot without executing economics.

The manifest is excluded from its own hash map. Large logical evidence is
delivered through exact binary transport parts and reconstructed by the reader.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_COMPONENTS = {'__pycache__', 'ci125', 'verification_runs', 'reproduction125',
                       'release125', 'publication125'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=('primary-checkpoint', 'complete'), required=True)
    args = parser.parse_args()
    files = {}
    excluded = []
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if path.name == 'DELIVERY_MANIFEST125.json' or path.suffix == '.pyc':
            continue
        if any(part in EXCLUDED_COMPONENTS for part in path.relative_to(ROOT).parts):
            continue
        if args.phase == 'primary-checkpoint' and any(
                part in {'independent-followup512', 'launch-independent-followup512',
                         'followup-reconciliation', 'independent-followup512_transport'}
                for part in path.relative_to(ROOT).parts):
            excluded.append(rel)
            continue
        data = path.read_bytes()
        files[rel] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    transports = {}
    audit = json.loads((ROOT / 'POSTFREEZE_AUDIT_FREEZE125.json').read_text())
    logical = audit['logical_independent_terminal_trace']
    transports[logical['path']] = {'parts': logical['parts'],
                                 'identity_source': 'POSTFREEZE_AUDIT_FREEZE125.json'}
    for path in ROOT.glob('results125/*transport*/TRANSPORT_SPLIT125.json'):
        split = json.loads(path.read_text())
        # New transport records use this explicit generic interface. The
        # original audit's different frozen record is handled above unchanged.
        if 'logical_path' in split and 'parts' in split:
            target = split['logical_path']
            if target in files:
                transports[target] = {'parts': [p['path'] if isinstance(p, dict) else p
                                                for p in split['parts']],
                                      'identity_source': path.relative_to(ROOT).as_posix()}
    for relative, transport in transports.items():
        assert relative in files, relative
        digest = hashlib.sha256()
        size = 0
        for part in transport['parts']:
            assert part in files, part
            data = (ROOT / part).read_bytes()
            digest.update(data)
            size += len(data)
        assert (size, digest.hexdigest()) == (files[relative]['bytes'], files[relative]['sha256'])
    m = {'schema': 1, 'created_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
         'phase': args.phase, 'separate_followup_completed': args.phase == 'complete',
         'scientific_source_commit': 'a94e1f43bf64d8cb90af21e4b53d07335c615576',
         'separate_followup_source_commit': 'a5f2047222751217b9660b241b9e63f36d87c53a',
         'scope': 'Exact author source, retained history, actual saved evidence and compiled documents; no claim of a new economic experiment by this package operation.',
         'files': files, 'transports': transports,
         'excluded_in_progress_paths': excluded,
         'self_hash_policy': 'This manifest, later verification receipts, CI outputs and release archives are excluded to avoid self-reference. Their hashes are recorded by the release receipt.'}
    if args.phase == 'complete':
        execution = json.loads((ROOT / 'results125/independent-followup512/EXECUTION125.json').read_text())
        assert execution['status'] == 'executed'
    (ROOT / 'DELIVERY_MANIFEST125.json').write_text(json.dumps(m, indent=2) + '\n')
    print(json.dumps({'phase': args.phase, 'files': len(files), 'bytes': sum(x['bytes'] for x in files.values()),
                      'transported_logical_files': list(transports),
                      'manifest_sha256': hashlib.sha256((ROOT / 'DELIVERY_MANIFEST125.json').read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
