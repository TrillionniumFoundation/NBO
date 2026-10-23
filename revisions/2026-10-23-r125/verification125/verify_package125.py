"""Verify the delivered R125 bytes and scientific custody before any rebuild.

This is a package/evidence check, not a fresh original-economy experiment.
The immutable scientific gate and recorded algebra replay remain separate.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', required=True)
    args = p.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)
    tick = time.perf_counter()
    receipt = {'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
               'scope': 'delivered bytes, custody, exact retained objects and recorded completion; not a new economic experiment',
               'checks': {}, 'status': 'running'}
    try:
        m = json.loads((ROOT / 'DELIVERY_MANIFEST125.json').read_text())
        assert m['schema'] == 1
        from materialize_delivery125 import materialize
        receipt['transport_reconstruction'] = materialize(ROOT, m)
        for relative, record in m['files'].items():
            path = (ROOT / relative).resolve()
            assert path.is_relative_to(ROOT), relative
            assert path.is_file(), relative
            assert path.stat().st_size == record['bytes'], relative
            assert sha(path) == record['sha256'], relative
        receipt['checks']['delivered_files'] = len(m['files'])
        receipt['manifest_sha256'] = sha(ROOT / 'DELIVERY_MANIFEST125.json')
        sys.path.insert(0, str(ROOT / 'code125'))
        from common125 import verify_inputs
        verified = verify_inputs()
        assert verified['boundaries']['source_commit'] == 'a94e1f43bf64d8cb90af21e4b53d07335c615576'
        receipt['checks']['frozen_scientific_files'] = verified['files']
        retained = json.loads((ROOT / 'provenance/R122_AUTHOR_TEXT_RETENTION125.json').read_text())
        for row in retained:
            assert sha(ROOT / row['retained_path']) == row['sha256'], row['retained_path']
        receipt['checks']['unchanged_R122_objects'] = len(retained)
        complete_retention = json.loads((ROOT / 'CONTENT_RETENTION125.json').read_text())['records']
        assert len(complete_retention) == 307
        for row in complete_retention:
            assert sha(ROOT / row['retained_path']) == row['sha256'], row['retained_path']
        receipt['checks']['all_retained_original_objects'] = len(complete_retention)
        primary = json.loads((ROOT / 'results125/primary/EXECUTION125.json').read_text())
        assert primary['status'] == 'executed' and primary['decisions'] == 936
        for i in range(3):
            e = json.loads((ROOT / f'results125/timing{i}/EXECUTION125.json').read_text())
            assert e['status'] == 'executed' and e['decisions'] == 234
        audit = json.loads((ROOT / 'results125/verification/EXECUTION125.json').read_text())
        assert audit['status'] == 'executed' and audit['checks'] >= 16000
        independent = json.loads((ROOT / 'results125/independent/SUMMARY125.json').read_text())
        assert independent['decisions'] == 936 and independent['contradictions'] == 0
        completed = json.loads((ROOT / 'results125/independent/EXECUTION125.json').read_text())
        assert completed['status'] == 'executed'
        receipt['checks']['recorded_primary_decisions'] = 936
        receipt['checks']['recorded_timed_decisions'] = 702
        receipt['checks']['independent_evidence'] = {
            k: independent[k] for k in ('decisions', 'unique_actions', 'contained',
                'unresolved_containment', 'accepted', 'accepted_gain_confirmed', 'contradictions')}
        if m.get('separate_followup_completed', False):
            followup = json.loads((ROOT / 'results125/independent-followup512/SUMMARY125.json').read_text())
            execution = json.loads((ROOT / 'results125/independent-followup512/EXECUTION125.json').read_text())
            boundary = json.loads((ROOT / 'POSTFREEZE_AUDIT_BOUNDARY125.json').read_text())
            frozen_path = ROOT / 'POSTFREEZE_AUDIT_FREEZE125.json'
            assert sha(frozen_path) == 'd6c2009754e36e288662974f4f53eeea31d22dba8a4440e324e55c348e6faad9'
            frozen_followup = json.loads(frozen_path.read_text())
            for relative, expected in frozen_followup['files'].items():
                assert sha(ROOT / relative) == expected, relative
            receipt['checks']['frozen_followup_files'] = len(frozen_followup['files'])
            assert execution['status'] == 'executed'
            assert boundary['source_commit'] == 'a5f2047222751217b9660b241b9e63f36d87c53a'
            assert boundary['remote_readback_before_new_economics'] is True
            assert followup['new_unique_actions'] == 110
            assert followup['requested_terminal_contexts'] == 112750
            assert followup['decisions'] == 936 and followup['accepted'] == 251
            assert followup['contradictions'] == 0
            assert followup['changed_production_policies'] == 0
            assert followup['initial_contained'] == independent['contained'] == 850
            assert followup['initial_accepted_gain_confirmed'] == independent['accepted_gain_confirmed'] == 193
            receipt['checks']['separate_followup'] = {
                k: followup[k] for k in ('new_unique_actions', 'decisions', 'contained',
                    'unresolved_containment', 'accepted', 'accepted_gain_confirmed', 'contradictions')}
        receipt['status'] = 'passed'
    except BaseException as exc:
        receipt.update(status='failed', error_type=type(exc).__name__, error=str(exc))
        raise
    finally:
        receipt['seconds'] = time.perf_counter() - tick
        receipt['finished_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
        (out / 'PACKAGE_VERIFICATION125.json').write_text(json.dumps(receipt, indent=2) + '\n')
        print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
