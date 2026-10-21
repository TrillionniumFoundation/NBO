"""Pure post-campaign schema fixtures plus complete saved-primary algebra replay.

No actor is loaded and no original economic primitive is imported or called.
Synthetic quadratics use the already-preserved pre-F fixture, with the actual
campaign metadata merge now applied after the service's numerical fields.
"""
from __future__ import annotations
import argparse, copy, importlib.util, json, math, sys, time
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code122'))
sys.path.insert(0, str(ROOT / 'verification122'))
import algebra_audit122 as frozen
import independent_schema_adapter122 as adapter
from common122 import digest, dump, fail, finish, key, identities, start, verify_source


def post_campaign(row, label='value'):
    """Apply the actual metadata overwrite after completing fixture aliases."""
    row = copy.deepcopy(row)
    if not row['accepted_improvement']:
        row.update(lower=row['complete_policy_lower'], upper=row['complete_policy_upper'],
                   optimum_lower=row['original_optimum_lower'])
        row['loss'] = math.nextafter(row['upper'] - row['optimum_lower'], math.inf)
        row['width'] = math.nextafter(row['upper'] - row['lower'], math.inf)
        row['certified_regret_upper'] = row['loss']
    row.update(index=0 if row['alpha'] == .5 else 1, row=0, budget=5,
               arm='quadratic', loss=label, population_observation=True, repeat=None)
    return json.loads(json.dumps(row, allow_nan=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-commit', required=True)
    parser.add_argument('--primary', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out, initial, tick = start(args.output, 'pure-independent-schema-repair-check',
                               {'source_commit': args.source_commit})
    try:
        dump(out / 'VERIFIED_SOURCE122.json', verify_source(args.source_commit))
        if digest(Path(frozen.__file__)) != adapter.FROZEN_AUDITOR_SHA256:
            raise ValueError('Frozen algebra source hash differs')
        fixture_path = ROOT / 'provenance122/review/verify_serialized_algebra122.py'
        spec = importlib.util.spec_from_file_location('original_synthetic_fixture122', fixture_path)
        fixture = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixture)
        original_audit = frozen.audit
        synthetic_checks = {}
        wrapped = adapter.make_audit(original_audit, synthetic_checks)
        serialized = []

        def postmerge_audit(row):
            native = post_campaign(row, 'value' if len(serialized) % 2 == 0 else 'marginal')
            before = json.dumps(native, sort_keys=True, allow_nan=False)
            result = wrapped(native)
            if json.dumps(native, sort_keys=True, allow_nan=False) != before:
                raise AssertionError('Adapter changed a nested native synthetic record')
            serialized.append(native)
            return result

        frozen.audit = postmerge_audit
        try:
            synthetic = fixture.run()
        finally:
            frozen.audit = original_audit
        if len(serialized) != 126:
            raise AssertionError('Complete inherited synthetic scenario census differs')
        accepted = next(r for r in serialized if r['accepted_improvement'])
        try:
            original_audit(accepted)
        except ArithmeticError as error:
            if 'returned qualified candidate loss' not in str(error):
                raise
            original_error = repr(error)
        else:
            raise AssertionError('Original accepted merged-schema defect was not reproduced')
        tamper_results = []
        for field in ('numeric-training-label', 'unknown-training-label', 'numeric-regret',
                      'selected-candidate-regret', 'selected-fraction', 'gradient', 'gain', 'action'):
            bad = copy.deepcopy(accepted)
            if field == 'numeric-training-label':
                bad['loss'] = bad['certified_regret_upper']
            elif field == 'unknown-training-label':
                bad['loss'] = 'unregistered'
            elif field == 'numeric-regret':
                bad['certified_regret_upper'] = math.nextafter(bad['certified_regret_upper'], math.inf)
            elif field == 'selected-candidate-regret':
                record = bad['support_attempts'][-1]
                entry = next(z for z in record['candidate_menu']
                             if z['fraction_index'] == record['selected_fraction_index'])
                entry['candidate_certificate']['loss'] = 0.
            elif field == 'selected-fraction':
                bad['support_attempts'][-1]['selected_fraction_index'] = 6
            elif field == 'gradient':
                bad['support_attempts'][0]['gradient']['lower'] = '7'
            elif field == 'gain':
                bad['support_attempts'][0]['candidate_menu'][0]['proposal']['original_policy_gain_lower'] = '1'
            else:
                bad['action_hex'] = '0x0.0p+0'
            try:
                wrapped(bad)
            except ArithmeticError as error:
                tamper_results.append({'kind': field, 'rejected': True, 'error': repr(error)})
            else:
                raise AssertionError('Tampered merged-schema record passed: ' + field)
        # A real online identity has no training label or fitted acquisition.
        online = next(copy.deepcopy(r) for r in serialized if not r['accepted_improvement'])
        online.update(arm='online', budget=0, loss='online')
        wrapped(online)
        checks, counts, census = {}, {}, set()
        audit = adapter.make_audit(original_audit, checks)
        path = args.primary / 'records122.jsonl'
        primary_hash = digest(path)
        labels = {}
        with path.open() as stream:
            for number, line in enumerate(stream, 1):
                row = json.loads(line)
                identity = key(row)
                if identity in census or row['source_commit'] != args.source_commit:
                    raise ValueError('Duplicate or wrong-source saved primary row')
                census.add(identity)
                before = json.dumps(row, sort_keys=True, allow_nan=False)
                result = audit(row)
                if json.dumps(row, sort_keys=True, allow_nan=False) != before:
                    raise AssertionError('Adapter changed a nested saved primary record')
                for name, value in result.items():
                    counts[name] = counts.get(name, 0) + value
                labels[row['loss']] = labels.get(row['loss'], 0) + 1
                if number % 512 == 0:
                    print('SAVED_ALGEBRA_ROWS', number, round(time.perf_counter() - tick, 3), flush=True)
        if census != identities() or counts['rows'] != 5568 or digest(path) != primary_hash:
            raise ValueError('Saved primary census or unchanged bytes failed')
        forbidden = []
        for name, module in tuple(sys.modules.items()):
            file = getattr(module, '__file__', None)
            if file and '/2026-10-20-r121/' in str(file):
                forbidden.append(name)
        if forbidden:
            raise AssertionError('Original economy module unexpectedly imported: ' + repr(forbidden))
        result = dict(status='passed', source_commit_F=args.source_commit,
            primary_sha256=primary_hash, primary_rows=counts['rows'], native_training_label_counts=labels,
            unchanged_saved_record_bytes=True, native_record_deep_equal_after_every_audit=True,
            synthetic_post_campaign_rows=126, synthetic_result=synthetic,
            synthetic_adapter_checks=synthetic_checks, synthetic_original_failure=original_error,
            rejected_tamper_cases=tamper_results, saved_primary_algebra_counts=counts,
            saved_primary_adapter_checks=checks, original_economic_calls=0,
            original_economic_modules_imported=forbidden, new_population_observations=0,
            production_service_configured=False,
            scope='Pure exact saved-support algebra, conditional on premises; no independent primitive economics yet.',
            source_sha256={str(p.relative_to(ROOT)): digest(p) for p in
                (Path(__file__), Path(adapter.__file__), Path(frozen.__file__), fixture_path,
                 ROOT / 'code122/service122.py', ROOT / 'code122/independent122.py')})
        dump(out / 'RESULT122.json', result)
        finish(out, initial, tick, {'pure_arithmetic_only': True, 'saved_primary_rows': counts['rows'],
                                   'synthetic_rows': 126, 'original_economic_calls': 0})
        print(json.dumps({k: result[k] for k in ('status', 'primary_rows', 'saved_primary_algebra_counts',
                                               'saved_primary_adapter_checks', 'original_economic_calls')}, indent=2), flush=True)
    except BaseException:
        fail(out, tick)
        raise


if __name__ == '__main__':
    main()
