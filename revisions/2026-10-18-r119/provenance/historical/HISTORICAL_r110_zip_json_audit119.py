#!/usr/bin/env python3
"""Read every R110 custody JSON member, parse each exact content identity once.

No historical source is imported or executed. At most one JSON body is staged;
ZIP CRC, complete byte hashes, source-export identity and execution-manifest
identity are checked separately. The source audit parser is our own frozen
read-only tool, not a file from the recovered research archive.
"""
from pathlib import Path
import collections
import hashlib
import json
import resource
import sys
import tempfile
import time
import zipfile

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE/'_parser_dep'))
import HISTORICAL_stream_audit as audit

ARCHIVE = HERE.parent/'r110_custody119'/'selected-r110.zip'
EXPECTED_ARCHIVE_SHA256 = '9f40a73a3ce4ca154228b1ffceb304be8a5a77d2909fc69b278fe0c56a94a8c2'
EXPECTED_PARSER_SHA256 = '7d0e4635a756ff065b212c7c8088241f8aeb2e354a8f6b82b0a8d0a31e510f99'
OUT = HERE/'HISTORICAL_r110_json_run'


def main():
    resource.setrlimit(resource.RLIMIT_AS, (512*1024**2, 512*1024**2))
    resource.setrlimit(resource.RLIMIT_CPU, (600, 600))
    started, tic = audit.utc(), time.monotonic()
    OUT.mkdir(exist_ok=True)
    (OUT/'events').mkdir(exist_ok=True)
    (OUT/'parse').mkdir(exist_ok=True)
    parser_sha = audit.sha_file(Path(audit.__file__))
    assert parser_sha == EXPECTED_PARSER_SHA256
    archive_sha = audit.sha_file(ARCHIVE)
    assert archive_sha == EXPECTED_ARCHIVE_SHA256
    counts = collections.Counter()
    cache, errors = {}, []
    with zipfile.ZipFile(ARCHIVE) as z:
        infos = sorted((x for x in z.infolist() if x.filename.endswith('.json')),
                       key=lambda x: (0 if x.filename.endswith('REMOTE_ATTEMPT110.json') else
                                      1 if x.filename.endswith('REMOTE_SOURCE_EXPORT110.json') else 2,
                                      x.filename))
        assert len(infos) == 5097
        source = json.loads(z.read('NBO_R110/REMOTE_SOURCE_EXPORT110.json'))
        attempt = json.loads(z.read('REMOTE_ATTEMPT110.json'))
        source_map = {'NBO_R110/'+r['path']:r for r in source['files']}
        attempt_map = {r['path']:r for r in attempt['files']}
        with tempfile.TemporaryDirectory(prefix='r110-json-', dir=OUT) as tmp, \
             (OUT/'records.jsonl').open('w') as records:
            staged = Path(tmp)/'one.json'
            for no, info in enumerate(infos):
                row = {'member_index': no, 'path':info.filename,
                       'declared_bytes': info.file_size,
                       'zip_crc32': format(info.CRC,'08x')}
                if info.file_size > 128*1024**2:
                    row.update(raw_complete=False, error='explicit 128 MiB member cap')
                    records.write(json.dumps(row)+'\n'); errors.append(row); continue
                sha = hashlib.sha256()
                git = hashlib.sha1(f'blob {info.file_size}\0'.encode())
                n = 0
                try:
                    with z.open(info) as f, staged.open('wb') as output:
                        for b in iter(lambda:f.read(audit.CHUNK),b''):
                            n += len(b); sha.update(b); git.update(b); output.write(b)
                    row.update(bytes_read=n, sha256=sha.hexdigest(), git_blob_sha1=git.hexdigest(),
                               raw_complete=n==info.file_size, zip_crc_checked=True)
                    counts['raw_json_members'] += 1
                    counts['raw_json_bytes'] += n
                    original = source_map.get(info.filename)
                    receipt = attempt_map.get(info.filename)
                    if original:
                        row['source_export_match'] = (original['sha256']==row['sha256'] and
                                                      original['git_blob']==row['git_blob_sha1'])
                        counts['source_export_members'] += 1
                        counts['source_export_matches'] += row['source_export_match']
                    else:
                        row['source_export_match'] = None
                        counts['not_in_source_export_members'] += 1
                    if receipt:
                        row['execution_receipt_match'] = (receipt['sha256']==row['sha256'] and
                                                         receipt['bytes']==n)
                        counts['execution_receipt_members'] += 1
                        counts['execution_receipt_matches'] += row['execution_receipt_match']
                    else:
                        row['execution_receipt_match'] = None
                    identity = row['sha256']
                    if identity not in cache:
                        ep = OUT/'events'/f'{identity}.jsonl.gz'
                        events = audit.Events(ep, cap=500000)
                        try:
                            result = audit.json_audit(staged, events)
                        except Exception as e:
                            result = {'semantic_complete':False, 'error_type':type(e).__name__,
                                      'error':str(e)}
                        result.update(events.close())
                        result['body_sha256'] = identity
                        result['event_file_sha256'] = audit.sha_file(ep)
                        audit.dump(OUT/'parse'/f'{identity}.json', result)
                        cache[identity] = {k:result.get(k) for k in
                                           ('semantic_complete','all_matched_events_retained',
                                            'field_inventory_complete','error','error_type')}
                        counts['unique_json_contents_parsed'] += 1
                        counts['unique_json_complete'] += bool(result['semantic_complete'])
                        counts['unique_event_retention_complete'] += result['all_matched_events_retained']
                        counts['unique_field_summary_complete'] += bool(result.get('field_inventory_complete'))
                    else:
                        counts['exact_content_parse_reuses'] += 1
                    row['parse_identity_sha256'] = identity
                    row['parse'] = cache[identity]
                    row['semantic_complete'] = bool(cache[identity]['semantic_complete'])
                    counts['member_semantic_complete'] += row['semantic_complete']
                    if (not row['semantic_complete'] or row.get('source_export_match') is False
                            or row.get('execution_receipt_match') is False):
                        errors.append(row)
                except Exception as e:
                    row.update(raw_complete=False,error_type=type(e).__name__,error=str(e))
                    errors.append(row)
                records.write(json.dumps(row,allow_nan=False)+'\n')
                records.flush()
                staged.unlink(missing_ok=True)
                if (no+1)%250==0:
                    print(json.dumps({'processed':no+1, 'unique':len(cache),
                                      'errors':len(errors), 'elapsed_seconds':time.monotonic()-tic}),flush=True)
    summary = {'scope':'Custody, complete raw JSON read and strict SAX parse only; no historical code execution or economic experiment rerun.',
               'started_utc':started,'ended_utc':audit.utc(),'elapsed_seconds':time.monotonic()-tic,
               'script_sha256':audit.sha_file(Path(__file__)),'parser_sha256':parser_sha,
               'archive_sha256':archive_sha,'archive_bytes':ARCHIVE.stat().st_size,
               'source_workflow_commit':source['workflow_commit'],
               'source_revision_tree':source['revision_tree'],
               'historical_attempt_workflow_commit':attempt['workflow_commit'],
               'historical_attempt_run_id':attempt['run_id'],
               'historical_attempt_declared_status':attempt['job_status_before_receipt'],
               'historical_attempt_declared_scope':attempt['scope'],
               'counts':dict(counts),'unresolved_records':errors,
               'maximum_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               'all_declared_members_raw_read':counts['raw_json_members']==5097,
               'all_declared_members_semantically_parsed':counts['member_semantic_complete']==5097,
               'selected_scope_complete':counts['member_semantic_complete']==5097 and not errors,
               'records_sha256':audit.sha_file(OUT/'records.jsonl'),
               'deduplication':'Every member body was fully decompressed/hash-read; identical SHA256 contents share one strict parser result.'}
    audit.dump(OUT/'summary.json',summary)
    print(json.dumps(summary,allow_nan=False),flush=True)
    return 0 if summary['selected_scope_complete'] else 2


if __name__=='__main__':
    raise SystemExit(main())
