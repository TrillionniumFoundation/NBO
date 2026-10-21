"""Verify retained R121 report, route and dated source-census evidence.

This program reads bytes and JSON only. It does not import scientific modules,
rerun experiments, or turn a syntactic registry into proof revalidation.
"""
from __future__ import annotations

import argparse
from collections import Counter
import datetime
import gzip
import hashlib
import json
from pathlib import Path
import time


def identity(raw):
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                git_blob_sha1=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest())


def require(test, message):
    if not test:
        raise AssertionError(message)


def read_json(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def bind(revision, item, path_key='path', identity_key=None):
    path=revision/item[path_key]
    raw=path.read_bytes(); expected=item[identity_key] if identity_key else item
    got=identity(raw)
    for key in ('bytes','sha256','git_blob_sha1'):
        if key in expected:
            require(got[key]==expected[key], 'Retained identity differs: '+str(path)+' '+key)
    return dict(path=item[path_key],**got)


def verify(revision):
    lineage=revision/'provenance121/lineage121'
    reports=read_json(revision/'provenance121/reports121/REPORT_SOURCE_INDEX121.json')
    require(len(reports['files'])==35 and reports['review_ref_count']==36,'Original report census')
    report_ids={r['report_id']:r for r in reports['files']}
    require(len(report_ids)==35,'Duplicate report identifier')
    verified_reports=[bind(revision,r) for r in reports['files']]
    coverage=read_json(lineage/'REPORT_READING_COVERAGE121.json')
    require(coverage['counts']['full_bodies_read']==35,'Prior full-reading receipt')
    require({r['report_id'] for r in coverage['reports']}==set(report_ids),'Reading/report identity coverage')
    for row in coverage['reports']:
        require(row['actually_read_entire_body'] is True,'Incomplete original reading receipt')
        require(row['original_report_identity']==report_ids[row['report_id']], 'Original report identity in reading receipt')
        require((revision/row['semantic_note_file']).is_file(),'Missing report reading note')

    snapshot=read_json(lineage/'initial_author_response121/INDEX121.json')
    snapshots={r['original_path']:r for r in snapshot['files']}
    for item in snapshot['files']:
        compressed=(revision/item['path']).read_bytes()
        require(identity(compressed)==item['compressed_identity'],'Initial response transport changed')
        require(identity(gzip.decompress(compressed))==item['original_identity'],'Initial response bytes changed')
    for item in coverage['note_bindings']:
        if item['path'] in snapshots:
            expected=snapshots[item['path']]['original_identity']
            require(all(expected[k]==item[k] for k in expected),'Initial note snapshot mismatch')
        else:
            bind(revision,item)

    compact=read_json(lineage/'COMPACT_CENSUS_INDEX121.json')
    compact_verified=[bind(revision,item) for item in compact['files']]
    ledger=read_json(lineage/'ALL_BRANCH_FILE_LEDGER121.json')
    require(len(ledger['branches'])==361 and len(ledger['ledgers'])==303,'All-branch census cardinality')
    require(compact['raw_tree_entries']==24121986 and compact['unique_blob_ids']==67440,'Full stream census counts')
    require(compact['large_raw_tree_streams_copied'] is False,'Unexpected raw-stream-copy claim')

    inherited=revision/'provenance121/reports121/inherited_maps'
    prior=read_json(inherited/'R97_REQUIREMENTS120.json.gz')
    current=read_json(revision/'provenance121/R97_REQUIREMENTS121.json')
    old={r['key']:r for r in prior['items']}
    require(len(old)==30 and len(current['items'])==30,'R97 exact response census')
    response=(revision/'new121/response121_body.tex').read_text()
    exact_quotes=[]
    for item in current['items']:
        require(item['inherited_r120_record_unchanged']==old[item['key']],'Prior R120 record altered')
        require(item['exact_text']==old[item['key']]['exact_text'],'Controlling comment altered')
        require(hashlib.sha256(item['exact_text'].encode()).hexdigest()==item['comment_sha256'],'Controlling comment hash')
        require(item['exact_inherited_quote_latex'] in response,'Exact quote absent from current response')
        exact_quotes.append(item['comment_id'])
    require(len(set(exact_quotes))==30,'Duplicated R97 comment')
    routes=read_json(inherited/'HISTORICAL_ROUTE_BINDINGS120.json.gz')
    categories=Counter(r['category'] for r in routes['rows'])
    require(categories==dict(major=620,additional=394,overlapping_parent=35),'Historical route categories')
    require(len(routes['rows'])==1049 and len({r['key'] for r in routes['rows']})==1049,'Historical route keys')
    require(routes['counts']['routed_requests_excluding_overlapping_parents']==1014,'Historical request count')

    independent=[]
    for folder in ('independent_constraints121','episode_boundaries121'):
        index=read_json(revision/'provenance121'/folder/'COPY_INDEX121.json')
        independent.extend(bind(revision,item) for item in index['files'])
    archival=read_json(lineage/'archival_route_code121/INDEX121.json')
    archival_files=[bind(revision,item,'preserved_path','actual_identity') for item in archival['files']]
    require(len(archival_files)==10 and sum(x['bytes']for x in archival_files)==160666,'Historical route code copy census')

    registry_dir=lineage/'theorem_code_registry_attempt02'
    execution=read_json(registry_dir/'EXECUTION121.json')
    require(execution['status']=='passed' and execution['source_science_runs']==0,'Registry execution scope')
    require(execution['fresh_mathematical_proof_validation_claimed'] is False,'Registry overclaims proof validation')
    for name,item in execution['outputs'].items():
        require(identity((registry_dir/name).read_bytes())==item,'Registry output identity: '+name)
    raw=gzip.decompress((registry_dir/'THEOREM_PROOF_CODE_REGISTRY121.json.gz').read_bytes())
    require(identity(raw)==execution['registry_exact_uncompressed'],'Registry decompressed identity')
    json.loads(raw)
    require((lineage/'theorem_code_registry_attempt01/FAILED121.json').is_file(),'Initial registry failure disappeared')
    later_changes=[]
    for item in execution['input_files']:
        p=revision/item['path']
        require(p.is_file(),'Retained source snapshot file disappeared: '+item['path'])
        if identity(p.read_bytes())!={k:item[k] for k in ('bytes','sha256','git_blob_sha1')}:
            later_changes.append(item['path'])
    return dict(status='passed', original_report_bodies=len(verified_reports),
        original_report_bytes=sum(x['bytes']for x in verified_reports),
        original_report_reading_receipt_utc=coverage['recorded_utc'],
        full_reading_claim_is_prior_dated_receipt_not_new_reading=True,
        exact_current_R97_quotes=exact_quotes, unchanged_complete_R120_records=30,
        historical_route_categories=dict(categories),historical_request_records=1014,
        overlapping_parent_treatments_are_not_additional_issues=True,
        routes_are_not_scientific_closure_counts=True,
        initial_branch_count=361,initial_unique_head_commits=303,
        compact_census_files_verified=len(compact_verified),
        independent_constraint_and_boundary_files_verified=len(independent),
        additional_exact_archival_program_files=len(archival_files),
        registry_original_execution=execution['finished_utc'],registry_counts=execution['counts'],
        registry_later_source_changes=later_changes,
        registry_source_change_scope='The original dated structural snapshot is retained unchanged; later editorial or reporting-source changes require a new final snapshot.',
        no_new_original_economic_execution=True,no_new_historical_proof_revalidation=True,
        no_new_semantic_reading_of_all_original_sources_claimed=True,
        current_response_identity=identity((revision/'new121/response121_body.tex').read_bytes()),
        current_requirement_map_identity=identity((revision/'provenance121/R97_REQUIREMENTS121.json').read_bytes()))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--revision',type=Path,default=Path(__file__).resolve().parents[2]);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();start=time.perf_counter();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    require(not args.output.exists(),'Exclusive output path already exists')
    result=verify(args.revision.resolve())
    result.update(schema='NBO_R121_RETENTION_READBACK_V1',started_utc=started,
        finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),elapsed_seconds=time.perf_counter()-start,
        verifier_identity=identity(Path(__file__).read_bytes()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x')as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({k:result[k] for k in ('status','original_report_bodies','original_report_bytes','unchanged_complete_R120_records','historical_request_records','initial_unique_head_commits','registry_later_source_changes','elapsed_seconds')},sort_keys=True))


if __name__=='__main__':
    main()
