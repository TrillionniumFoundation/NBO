"""Replay frozen inference and disclosed reporting from saved R122 evidence.

This is publication verification, not a new state draw, fit, economic-oracle
execution, or service timing experiment. Original saved clocks are inputs to
the report and are never replaced by the runtime of these replay processes.
The ordinary frozen source gates and the published adapter gate still run.
"""
from __future__ import annotations
import argparse
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
F = '2f483615c8bc0037e43ec01a16cce05c724f8c60'
ADAPTER = 'af73f9bca8f2249da1601208a1921f50ea8fd074'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    receipt = dict(status='started', source_commit=F, reporting_adapter_commit=ADAPTER,
        verifier_sha256=sha(Path(__file__)), started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        commands=[], comparisons=[], new_states=0, new_training=0,
        new_economic_evaluations=0, new_service_timing_processes=0,
        scope='Frozen statistics and separately published protocol-conformant report replay only; original service clocks remain unchanged inputs.')
    started = time.perf_counter()

    def save():
        (output / 'SAVED_REPLAY122.json').write_text(json.dumps(receipt, indent=2) + '\n')

    def run(argv, label):
        begin = time.perf_counter()
        log = output / (label + '.log')
        with log.open('xb') as stream:
            result = subprocess.run(argv, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
        receipt['commands'].append(dict(argv=argv, exit_code=result.returncode,
            elapsed_seconds=time.perf_counter()-begin,
            log=str(log.relative_to(ROOT)), log_sha256=sha(log)))
        save()
        if result.returncode:
            raise RuntimeError('Saved-evidence replay failed: ' + label)

    def compare(original, replay, *, compressed=False):
        a, b = original.read_bytes(), replay.read_bytes()
        if compressed:
            # Python/zlib versions can change compression bytes without
            # changing a single deterministic record. Both hashes are saved.
            same = gzip.decompress(a) == gzip.decompress(b)
        else:
            same = a == b
        receipt['comparisons'].append(dict(original=str(original.relative_to(ROOT)),
            replay=str(replay.relative_to(ROOT)), original_sha256=sha(original),
            replay_sha256=sha(replay), bytes_equal=a == b,
            uncompressed_exact_equal=same if compressed else None,
            comparison='exact decompressed bytes' if compressed else 'exact bytes'))
        if not same:
            raise ArithmeticError('Deterministic saved output differs: ' + original.name)

    save()
    try:
        primary = 'results122/primary-attempt02'
        independent = 'results122/independent-attempt02'
        original_stats = ROOT / 'results122/statistics-attempt01'
        original_report = ROOT / 'results122/report-attempt02'
        stats = output / 'statistics-replay01'
        report = output / 'report-replay01'
        run([sys.executable, 'code122/launch122.py', '--receipt', str(output / 'launch-statistics-replay01'), '--',
            sys.executable, 'code122/stats122.py', '--source-commit', F,
            '--primary', primary, '--independent', independent, '--output', str(stats)], 'statistics')
        for name in ('INPUTS122.json', 'RADIUS_WITNESS122.json', 'STATS122.jsonl', 'SIGNED_COMPARISONS122.jsonl'):
            compare(original_stats / name, stats / name)
        # Use original scientific stage receipts, including the original stats
        # clock, so every historical cost and deterministic report stays fixed.
        run([sys.executable, 'code122/launch122.py', '--receipt', str(output / 'launch-report-replay01'), '--',
            sys.executable, 'verification122/report_protocol_adapter122.py', '--repair-commit', ADAPTER,
            '--source-commit', F, '--primary', primary, '--independent', independent,
            '--stats', str(original_stats), '--output', str(report)], 'report')
        names = sorted(p.name for p in original_report.iterdir()
            if p.is_file() and (p.name.endswith(('.jsonl', '.jsonl.gz', '.csv', '.csv.gz', '.tex'))
                               or p.name in ('SUMMARY_REPORT122.json', 'INPUTS_REPORT122.json')))
        if len(names) < 35:
            raise ArithmeticError('Incomplete original reporting catalogue')
        for name in names:
            compare(original_report / name, report / name, compressed=name.endswith('.gz'))
        receipt.update(status='verified', comparisons_count=len(receipt['comparisons']),
            all_saved_economic_inference_cost_and_menu_outputs_equal=True,
            replay_process_receipts_separate_from_original_scientific_clocks=True)
    except BaseException as error:
        receipt.update(status='failed', error_type=type(error).__name__, error=str(error))
        raise
    finally:
        receipt.update(elapsed_seconds=time.perf_counter()-started,
                       finished_utc=dt.datetime.now(dt.timezone.utc).isoformat())
        save()


if __name__ == '__main__':
    main()
