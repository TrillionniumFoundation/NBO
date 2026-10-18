#!/usr/bin/env python3
"""Close the fixed historical read scope with failed/missing-only retries."""
from pathlib import Path
import collections
import datetime as dt
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = Path(__file__).parent
INITIAL = HERE.parent/'historical_remote119'
REVISION = HERE.parent.parent/'NBO/revisions/2026-10-18-r119'
SOURCE = REVISION/'provenance/historical/HISTORICAL_stream_audit.py'
MANIFEST = INITIAL/'HISTORICAL_stream_all_missing.jsonl'
OUT = HERE/'HISTORICAL_remote_closure119'
EXPECTED_SOURCE = '7d0e4635a756ff065b212c7c8088241f8aeb2e354a8f6b82b0a8d0a31e510f99'
EXPECTED_MANIFEST = '77006c56b959486e6408f994b3cad4a97a2ccfc197f5badde6206d7560d05e24'
PYTHON = '/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python'


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(65536),b''):h.update(b)
    return h.hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def is_complete(r):
    return (r.get('git_blob_verified') is True
            and r.get('declared_size_matches') is not False
            and r.get('parse',{}).get('semantic_complete') is True)


def scan(files):
    best, failures, attempts = {}, [], collections.Counter()
    for path in files:
        with path.open() as f:
            for line_no, line in enumerate(f,1):
                r=json.loads(line)
                attempts['attempt_records']+=1
                attempts['recorded_bytes_read']+=r.get('bytes_read',0)
                attempts['git_verified_attempts']+=bool(r.get('git_blob_verified'))
                compact={k:r.get(k) for k in ('sha','witness_commit','witness_path','bytes_read','sha256',
                         'git_blob_sha1','git_blob_verified','parse_suffix','transport','started_utc','ended_utc')}
                compact.update(record_path=str(path),record_line=line_no,
                               record_line_sha256=hashlib.sha256(line.encode()).hexdigest(),
                               semantic_complete=r.get('parse',{}).get('semantic_complete'),
                               complete=is_complete(r),parse_format=r.get('parse',{}).get('format'),
                               field_inventory_complete=r.get('parse',{}).get('field_inventory_complete'),
                               all_matched_events_retained=r.get('parse',{}).get('all_matched_events_retained'),
                               error=r.get('error',r.get('parse',{}).get('error')),
                               error_type=r.get('error_type',r.get('parse',{}).get('error_type')))
                previous=best.get(r['sha'])
                if previous is None or (compact['complete'] and not previous['complete']):best[r['sha']]=compact
                if not compact['complete']:failures.append({'reference':compact,'full_record':r})
    return best, failures, attempts


def main():
    started=dt.datetime.now(dt.timezone.utc).isoformat()
    assert sha(SOURCE)==EXPECTED_SOURCE
    assert sha(MANIFEST)==EXPECTED_MANIFEST
    assert (INITIAL/'COMMANDS119.json').exists(), 'Wait for all initial shards before retrying.'
    commands=json.loads((INITIAL/'COMMANDS119.json').read_text())
    assert len(commands)==16 and all('exit_code' in q for q in commands)
    expected_rows=[json.loads(s) for s in MANIFEST.open()]
    expected={r['sha']:r for r in expected_rows}
    assert len(expected)==len(expected_rows)==10358
    OUT.mkdir(exist_ok=True)
    files=sorted(INITIAL.glob('shard-*/records.jsonl'))
    assert len(files)==16
    first, failed, attempts=scan(files)
    write(OUT/'INITIAL_PASS119.json',{'expected_objects':len(expected),'observed_objects':len(first),
            'complete_objects':sum(r['complete'] for r in first.values()),
            'attempts':dict(attempts),'failure_count':len(failed),
            'initial_command_exit_codes':[q['exit_code'] for q in commands],
            'initial_start_receipt_sha256':sha(INITIAL/'START119.json'),
            'initial_commands_receipt_sha256':sha(INITIAL/'COMMANDS119.json')})
    write(OUT/'INITIAL_FAILED_ATTEMPTS119.json',failed)
    env=dict(os.environ,PYTHONPATH=str(HERE/'_parser_dep'))
    retry_receipts=[]
    for round_no in range(1,4):
        best, _, _=scan(files)
        pending=[expected[s] for s in sorted(expected) if s not in best or not best[s]['complete']]
        if not pending:break
        rd=OUT/f'retry-{round_no:02d}'
        rd.mkdir(exist_ok=False)
        manifest=rd/'RETRY_ONLY_MANIFEST119.jsonl'
        manifest.write_text(''.join(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n' for r in pending))
        cmd=[PYTHON,str(SOURCE),'run','--manifest',str(manifest),'--output',str(rd/'results'),
             '--repository','TrillionniumFoundation/NBO','--transport','raw_commit',
             '--shard-count','1','--shard-index','0','--object-mib','128','--memory-mib','512',
             '--cpu-seconds','300','--wall-seconds','360','--output-mib','128']
        receipt={'round':round_no,'argv':cmd,'started_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
                 'source_sha256':EXPECTED_SOURCE,'manifest_sha256':sha(manifest),
                 'retry_objects':len(pending),'only_previously_missing_or_failed':True}
        write(rd/'COMMAND119.json',receipt)
        tic=time.monotonic()
        with (rd/'run.log').open('wb') as log:
            result=subprocess.run(cmd,env=env,cwd=REVISION,stdout=log,stderr=subprocess.STDOUT)
        receipt.update(exit_code=result.returncode,elapsed_seconds=time.monotonic()-tic,
                       ended_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                       log_sha256=sha(rd/'run.log'))
        write(rd/'COMMAND119.json',receipt)
        retry_receipts.append(receipt)
        if (rd/'results/records.jsonl').exists():files.append(rd/'results/records.jsonl')
        print(json.dumps({'retry_round':round_no,'objects':len(pending),'exit_code':result.returncode}),flush=True)
    best, failed, attempts=scan(files)
    missing=sorted(set(expected)-set(best))
    unexpected=sorted(set(best)-set(expected))
    unresolved=[best[s] for s in sorted(set(best)&set(expected)) if not best[s]['complete']]
    formats=collections.Counter(r['parse_format'] for s,r in best.items() if s in expected)
    suffixes=collections.Counter(r['parse_suffix'] for s,r in best.items() if s in expected)
    warnings=[r for s,r in best.items() if s in expected and
              (r['field_inventory_complete'] is False or r['all_matched_events_retained'] is False)]
    union=OUT/'FINAL_OBJECT_UNION119.jsonl.gz'
    with gzip.open(union,'wt',encoding='utf-8') as f:
        for s in sorted(best):f.write(json.dumps(best[s],sort_keys=True)+'\n')
    ledger=OUT/'ALL_ATTEMPT_RECORDS119.jsonl.gz'
    ledger_sha=hashlib.sha256()
    with gzip.open(ledger,'wt',encoding='utf-8') as f:
        for p in files:
            with p.open() as source:
                for no,line in enumerate(source,1):
                    envelope={'record_file':str(p),'record_line':no,'record':json.loads(line)}
                    text=json.dumps(envelope,sort_keys=True,allow_nan=False)+'\n'
                    f.write(text);ledger_sha.update(text.encode())
    write(OUT/'FAILED_ATTEMPTS_AND_RETRY_HISTORY119.json',failed)
    write(OUT/'PARSE_WARNING_OBJECTS119.json',warnings)
    source_receipts=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
    summary={'scope':'All fixed historical missing-object identities read and format-audited; no historical code execution, no pickle loading, no theorem-proof claim, no new economic experiment.',
             'started_utc':started,'ended_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
             'source_sha256':EXPECTED_SOURCE,'manifest_sha256':EXPECTED_MANIFEST,
             'closure_script_sha256':sha(Path(__file__)),
             'expected_objects':10358,'unique_observed_objects':len(best),
             'complete_expected_objects':sum(best[s]['complete'] for s in set(best)&set(expected)),
             'complete_unique_bytes':sum(best[s]['bytes_read'] or 0 for s in set(best)&set(expected) if best[s]['complete']),
             'attempts':dict(attempts),'initial_transport_failures':len(json.loads((OUT/'INITIAL_FAILED_ATTEMPTS119.json').read_text())),
             'retained_failed_attempts':len(failed),'retry_rounds':retry_receipts,
             'missing_objects':missing,'unexpected_objects':unexpected,'unresolved_objects':unresolved,
             'parse_formats':dict(formats),'selected_format_suffixes':dict(suffixes),
             'parse_warning_objects':len(warnings),
             'format_scope_warning':'Opaque binaries have complete byte/hash audits only. NPZ object arrays are never unpickled. Gzip opaque payloads are not recursively interpreted. Field-summary caps and matched-event retention are separate from complete syntax parsing.',
             'all_selected_scope_complete':not missing and not unexpected and not unresolved,
             'related_github_ci_run':39103777344,'ci_workflow_success_asserted':False,
             'transport':'local-host immutable raw.githubusercontent.com commit/path reads using the same frozen CI auditor',
             'source_record_files':source_receipts,
             'portable_ledger':{'path':ledger.name,'bytes':ledger.stat().st_size,'sha256':sha(ledger),'uncompressed_sha256':ledger_sha.hexdigest()},
             'portable_union':{'path':union.name,'bytes':union.stat().st_size,'sha256':sha(union)}}
    write(OUT/'SUMMARY119.json',summary)
    print(json.dumps(summary,sort_keys=True),flush=True)
    return 0 if summary['all_selected_scope_complete'] else 2


if __name__=='__main__':raise SystemExit(main())
