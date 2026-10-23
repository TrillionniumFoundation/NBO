"""Descriptive decomposition of existing clocks, without re-timing a service."""
from fractions import Fraction as F
from pathlib import Path
import gzip, hashlib, json, time

ROOT = Path(__file__).resolve().parents[1]


def main():
    tick = time.perf_counter()
    p = ROOT / 'results125'
    source = p / 'primary/records125.jsonl.gz'
    with gzip.open(source, 'rt') as f:
        rows = [json.loads(line) for line in f]
    cohorts = [json.loads(line) for line in (p/'primary/cohorts125.jsonl').read_text().splitlines()]
    parent = json.loads((p/'launch-primary/PROCESS125.json').read_text())
    residual = F(parent['seconds']) - sum((F(c['seconds']) for c in cohorts), F(0))
    table = []
    for mode in ('warm_adaptive', 'cold_adaptive', 'warm_fixed512'):
        r = [x for x in rows if x['mode'] == mode]
        c = [x for x in cohorts if x['mode'] == mode]
        assert len(r) == 232 and len(c) == 58
        prefix = sum((F(x['complete_fused_prefix125']['complete_seconds']) for x in r), F(0))
        queries = sum((F(q['seconds']) for x in r for q in x['new_queries125']), F(0))
        service = sum((F(x['seconds125']) for x in r), F(0))
        total = sum((F(x['seconds']) for x in c), F(0)) + residual * len(c) / len(cohorts)
        other_service = service - prefix - queries
        cohort_overhead = total - service
        assert prefix >= 0 and queries >= 0 and other_service >= 0 and cohort_overhead >= 0
        assert prefix + queries + other_service + cohort_overhead == total
        table.append(dict(mode=mode, decisions=len(r),
            query_attempts=sum(len(x['new_queries125']) for x in r),
            new_terminal_contexts=sum(x['new_terminal_nodes125'] for x in r),
            prefix_seconds=str(prefix), query_and_gradient_recovery_seconds=str(queries),
            remaining_service_seconds=str(other_service),
            cohort_and_parent_residual_seconds=str(cohort_overhead),
            complete_primary_parent_allocated_seconds=str(total)))
    result = dict(status='executed', source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        economic_evaluations=0, services_retimed=0, scientific_source_changed=False,
        scope='Post-primary description of every saved clock in each complete 232-case enhancement census; one observed execution, no timing inference.',
        remaining_service_scope='All work outside the recorded inherited prefix and new query-plus-gradient timer, including setup, full-support ledger reconstruction, lower-bound/candidate algebra, policy selection and local bookkeeping; no isolated causal attribution.',
        source_timer_definition='code125/service125.py: qt encloses q_query, recover and bracket update; checked_candidate and make_case occur after that timer.',
        rows=table, seconds=time.perf_counter()-tick)
    with (p/'SAVED_CLOCK_PROFILE125.json').open('x') as f:
        json.dump(result, f, indent=2, sort_keys=True); f.write('\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
