"""Reporting-only reconciliation of saved audits; makes no economic calls."""
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
import argparse, csv, gzip, hashlib, json, time, traceback

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def rows(path):
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt') as f:
        return [json.loads(line) for line in f]


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def run(output):
    out = Path(output)
    out.mkdir(parents=True, exist_ok=False)
    tick = time.perf_counter()
    write(out / 'START125.json', dict(
        started_utc=datetime.now(timezone.utc).isoformat(),
        reporting_only=True, economic_evaluations=0,
        script_sha256=digest(__file__)))
    try:
        p = ROOT / 'results125'
        for name in ('SOURCE_FREEZE125.json', 'POSTFREEZE_AUDIT_FREEZE125.json'):
            m = read(ROOT / name)
            for rel, expected in m['files'].items():
                assert digest(ROOT / rel) == expected, rel
        original = read(p / 'independent/SUMMARY125.json')
        new = read(p / 'independent-followup512/SUMMARY125.json')
        child = read(p / 'independent-followup512/EXECUTION125.json')
        parent = read(p / 'launch-independent-followup512/PROCESS125.json')
        assert child['exit_code'] == parent['returncode'] == 0
        old_checks = rows(p / 'independent/checks125.jsonl')
        new_checks = rows(p / 'independent-followup512/checks125.jsonl')
        primary = rows(p / 'primary/records125.jsonl.gz')
        assert len(old_checks) == len(new_checks) == len(primary) == 936
        identity = ('index', 'budget', 'arm', 'training_loss', 'mode', 'row')
        table = {tuple(r[k] for k in identity): r for r in primary}
        old_table = {tuple(r[k] for k in identity): r for r in old_checks}
        evaluations = {r['key_id']: r for r in rows(p / 'independent/evaluations125.jsonl.gz')}
        refined = rows(p / 'independent-followup512/evaluations125.jsonl.gz')
        assert len(refined) == len({r['key_id'] for r in refined}) == 110
        for r in refined:
            assert r['bins'] == 512 and r['terminal_steps'] == 32
            old = evaluations[r['key_id']]
            merged = dict(r)
            for field in ('q_lower', 'j_lower', 'optimum_lower'):
                merged[field] = str(max(F(old[field]), F(r[field])))
            for field in ('q_upper', 'j_upper'):
                merged[field] = str(min(F(old[field]), F(r[field])))
            evaluations[r['key_id']] = merged
        counts = Counter()
        by_mode = {}
        for c in new_checks:
            key = tuple(c[k] for k in identity)
            old, r = old_table[key], table[key]
            v, b = evaluations[c['final_key']], evaluations[c['baseline_key']]
            lo, hi = F(r['complete_policy_lower']), F(r['complete_policy_upper'])
            contained = lo <= F(v['j_lower']) <= F(v['j_upper']) <= hi
            gain = F(0) if c['final_key'] == c['baseline_key'] else F(b['j_lower']) - F(v['j_upper'])
            gain_ok = not c['accepted'] or gain >= F(c['claimed_gain'])
            assert contained == c['contained'] and gain_ok == c['gain_confirmed']
            assert gain == F(c['independent_gain_lower'])
            assert old['contained'] == c['initial_contained']
            assert old['gain_confirmed'] == c['initial_gain_confirmed']
            assert not old['contained'] or contained
            assert not (old['accepted'] and old['gain_confirmed']) or gain_ok
            assert not c['contradiction']
            a = by_mode.setdefault(c['mode'], Counter())
            for target in (counts, a):
                target['decisions'] += 1
                target['initial_contained'] += old['contained']
                target['contained'] += contained
                target['accepted'] += c['accepted']
                target['initial_gain_confirmed'] += c['accepted'] and old['gain_confirmed']
                target['gain_confirmed'] += c['accepted'] and gain_ok
        assert counts['initial_contained'] == original['contained'] == 850
        assert counts['initial_gain_confirmed'] == original['accepted_gain_confirmed'] == 193
        assert counts['contained'] == new['contained']
        assert counts['gain_confirmed'] == new['accepted_gain_confirmed']
        work = Counter()
        trace = p / 'independent-followup512/terminal_witnesses125.jsonl.gz'
        old_trace_hash = digest(p / 'independent/terminal_witnesses125.jsonl.gz')
        with gzip.open(trace, 'rt') as f:
            for sequence, line in enumerate(f):
                r = json.loads(line)
                assert r['sequence'] == sequence
                work['requested_contexts'] += 1
                if 'reused_original_trace_sha256' in r:
                    assert r['reused_original_trace_sha256'] == old_trace_hash
                    work['reused_contexts'] += 1
                else:
                    work['new_contexts'] += 1
                    work['new_terminal_bisections'] += r['terminal_bisections_executed']
        assert work['requested_contexts'] == new['requested_terminal_contexts'] == 112750
        assert work['new_contexts'] == new['counts']['terminal_contexts']
        assert work['reused_contexts'] == new['counts']['reused_independent_terminal_contexts']
        assert work['new_terminal_bisections'] == new['counts']['actual_terminal_bisection_iterations']
        cost_rows = []
        for tag in ('fixtures', 'primary', 'timing0', 'timing1', 'timing2',
                    'verification', 'independent', 'report', 'independent-followup512'):
            a = read(p / tag / 'EXECUTION125.json')
            b = read(p / ('launch-' + tag) / 'PROCESS125.json')
            cost_rows.append(dict(phase=tag, child_seconds=a['seconds'],
                                  complete_parent_seconds=b['seconds'],
                                  peak_child_rss_kib=b['peak_child_rss_kib'],
                                  returncode=b['returncode'],
                                  parent_receipt_sha256=digest(p / ('launch-' + tag) / 'PROCESS125.json')))
        extra_rows = []
        for rel in ('postfreeze-terminal-diagnostic/EXECUTION125.json',
                    'BALANCED_WEIGHTING125.json',
                    'SAVED_CLOCK_PROFILE125.json',
                    'ADOPTION_SUPPORT_DIAGNOSTIC125.json',
                    'presentation-clockprofile/INTEGRATION125.json',
                    'presentation-attempt01/PRESENTATION125.json',
                    'presentation-directed/PRESENTATION125.json',
                    'independent_transport/TRANSPORT_SPLIT125.json',
                    'independent_transport/STATIC_TRANSPORT_CHECK125.json',
                    'independent_transport/STATIC_CACHE_TIMER_CHECK125.json',
                    'independent-followup512_transport/TRANSPORT_SPLIT125.json',
                    'independent-followup512_transport/RECONSTRUCTION125.json'):
            d = read(p / rel)
            extra_rows.append(dict(path='results125/' + rel, seconds=d['seconds'],
                                   sha256=digest(p / rel), economic_evaluations=0))
        result = dict(original_capped_audit=dict(contained=850, decisions=936,
                      gain_confirmed=193, accepted=251, unchanged=True),
                      combined_followup_counts=dict(counts), by_mode=by_mode,
                      newly_confirmed_containment=counts['contained'] - 850,
                      newly_confirmed_gains=counts['gain_confirmed'] - 193,
                      unresolved_containment=936 - counts['contained'],
                      unresolved_gain_bounds=251 - counts['gain_confirmed'],
                      exact_trace_work=dict(work), cache_loading_seconds=new['cache_loading_seconds'],
                      scientific_phase_costs=cost_rows, additional_measured_reporting_costs=extra_rows,
                      sum_complete_scientific_process_seconds=sum(r['complete_parent_seconds'] for r in cost_rows),
                      phase_sum_is_not_overall_research_wall_time=True,
                      historical_total_research_cost_known=False,
                      reporting_failure_receipts=[
                          'reporting125/PRESENTATION_ATTEMPT02_FAILURE.json',
                          'results125/reporting_failures/BALANCED_WEIGHTING_ATTEMPT01_FAILURE.json'],
                      unmeasured_costs=['Historical interrupted parent clocks were not recorded.',
                                       'The initial 4,080-support theory diagnostic has no separately recorded elapsed time.',
                                       'Two oversized connector upload rejections have no separate execution clock.',
                                       'A reporting-only FileExistsError attempt has no separate clock.',
                                       'Interactive analysis, publication, and document builds are outside these scientific process clocks.'],
                      original_production_targets_unchanged=True, production_decisions_changed=0,
                      population_inference=False, source_commit=new['source_boundary']['source_commit'],
                      source_manifest_sha256=new['source_boundary']['manifest_sha256'],
                      inputs={str(q.relative_to(ROOT)): digest(q) for q in (
                          p / 'primary/records125.jsonl.gz', p / 'independent/SUMMARY125.json',
                          p / 'independent-followup512/SUMMARY125.json', trace)},
                      reporting_economic_evaluations=0)
        write(out / 'RECONCILIATION125.json', result)
        with (out / 'scientific_phase_costs125.csv').open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(cost_rows[0]))
            w.writeheader(); w.writerows(cost_rows)
        write(out / 'EXECUTION125.json', dict(status='executed', exit_code=0,
              seconds=time.perf_counter() - tick, economic_evaluations=0,
              source_sha256=digest(__file__), checks_reconciled=936,
              terminal_trace_records_reconciled=112750,
              reconciliation_sha256=digest(out / 'RECONCILIATION125.json')))
        print(json.dumps(dict(counts=counts, work=work, seconds=time.perf_counter()-tick)))
    except BaseException:
        write(out / 'FAILURE125.json', dict(seconds=time.perf_counter()-tick,
              economic_evaluations=0, traceback=traceback.format_exc()))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    run(parser.parse_args().output)
